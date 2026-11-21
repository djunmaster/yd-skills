#!/usr/bin/env python3
"""Audit SVG figures for spacing, collisions, and routing errors."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


LAYOUT_JS = r"""
() => {
  const round = (n) => Math.round(n * 100) / 100;
  const numberAttr = (el, name, fallback) => {
    const raw = el?.dataset?.[name] ?? el?.getAttribute?.(`data-${name}`) ?? el?.getAttribute?.(name);
    const value = Number.parseFloat(raw);
    return Number.isFinite(value) ? value : fallback;
  };
  const svgRoot = (el) => el.ownerSVGElement || (el.tagName?.toLowerCase() === "svg" ? el : null);
  const localToRoot = (el) => {
    const svg = svgRoot(el);
    const rootCtm = svg?.getScreenCTM?.();
    const ctm = el.getScreenCTM?.();
    return rootCtm && ctm ? rootCtm.inverse().multiply(ctm) : null;
  };
  const rectFromPoints = (points) => {
    if (!points.length) return null;
    const xs = points.map((p) => p.x);
    const ys = points.map((p) => p.y);
    const x = Math.min(...xs);
    const y = Math.min(...ys);
    const width = Math.max(...xs) - x;
    const height = Math.max(...ys) - y;
    return { x, y, width, height, right: x + width, bottom: y + height };
  };
  const rectOf = (el) => {
    if (!el || el.closest?.("defs")) return null;
    try {
      const b = el.getBBox();
      const m = localToRoot(el);
      if (!m || !Number.isFinite(b.width) || !Number.isFinite(b.height)) return null;
      const points = [
        [b.x, b.y],
        [b.x + b.width, b.y],
        [b.x, b.y + b.height],
        [b.x + b.width, b.y + b.height],
      ].map(([x, y]) => new DOMPoint(x, y).matrixTransform(m));
      return rectFromPoints(points);
    } catch (_) {
      return null;
    }
  };
  const expand = (r, amount) => ({
    x: r.x - amount,
    y: r.y - amount,
    width: r.width + amount * 2,
    height: r.height + amount * 2,
    right: r.right + amount,
    bottom: r.bottom + amount,
  });
  const overlapSize = (a, b) => ({
    width: Math.max(0, Math.min(a.right, b.right) - Math.max(a.x, b.x)),
    height: Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y)),
  });
  const rectGap = (a, b) => {
    const dx = Math.max(a.x - b.right, b.x - a.right, 0);
    const dy = Math.max(a.y - b.bottom, b.y - a.bottom, 0);
    return Math.hypot(dx, dy);
  };
  const pointInRect = (p, r) => p.x >= r.x && p.x <= r.right && p.y >= r.y && p.y <= r.bottom;
  const segmentIntersectsRect = (a, b, r) => {
    if (pointInRect(a, r) || pointInRect(b, r)) return true;
    const corners = [
      { x: r.x, y: r.y },
      { x: r.right, y: r.y },
      { x: r.right, y: r.bottom },
      { x: r.x, y: r.bottom },
    ];
    for (let i = 0; i < corners.length; i += 1) {
      const edgeStart = corners[i];
      const edgeEnd = corners[(i + 1) % corners.length];
      if (segmentIntersection(a, b, edgeStart, edgeEnd)) return true;
    }
    return false;
  };
  const distancePointToRect = (p, r) => {
    if (pointInRect(p, r)) return 0;
    const dx = Math.max(r.x - p.x, 0, p.x - r.right);
    const dy = Math.max(r.y - p.y, 0, p.y - r.bottom);
    return Math.hypot(dx, dy);
  };
  const penetrationInRect = (p, r) => {
    if (!pointInRect(p, r)) return 0;
    return Math.min(p.x - r.x, r.right - p.x, p.y - r.y, r.bottom - p.y);
  };
  const distancePointToSegment = (p, a, b) => {
    const vx = b.x - a.x;
    const vy = b.y - a.y;
    const len2 = vx * vx + vy * vy;
    if (!len2) return Math.hypot(p.x - a.x, p.y - a.y);
    const t = Math.max(0, Math.min(1, ((p.x - a.x) * vx + (p.y - a.y) * vy) / len2));
    return Math.hypot(p.x - (a.x + t * vx), p.y - (a.y + t * vy));
  };
  const distancePointToPolyline = (p, points) => {
    let best = Infinity;
    for (let i = 0; i < points.length - 1; i += 1) {
      best = Math.min(best, distancePointToSegment(p, points[i], points[i + 1]));
    }
    return best;
  };
  const orientation = (a, b, c) => (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
  const onSegment = (a, b, c) =>
    b.x >= Math.min(a.x, c.x) - 0.5 &&
    b.x <= Math.max(a.x, c.x) + 0.5 &&
    b.y >= Math.min(a.y, c.y) - 0.5 &&
    b.y <= Math.max(a.y, c.y) + 0.5;
  const segmentIntersection = (a, b, c, d) => {
    const o1 = orientation(a, b, c);
    const o2 = orientation(a, b, d);
    const o3 = orientation(c, d, a);
    const o4 = orientation(c, d, b);
    const proper =
      ((o1 > 0.5 && o2 < -0.5) || (o1 < -0.5 && o2 > 0.5)) &&
      ((o3 > 0.5 && o4 < -0.5) || (o3 < -0.5 && o4 > 0.5));
    if (proper) {
      const t = o1 / (o1 - o2);
      return { x: a.x + t * (b.x - a.x), y: a.y + t * (b.y - a.y) };
    }
    if (Math.abs(o1) <= 0.5 && onSegment(a, c, b)) return { ...c };
    if (Math.abs(o2) <= 0.5 && onSegment(a, d, b)) return { ...d };
    if (Math.abs(o3) <= 0.5 && onSegment(c, a, d)) return { ...a };
    if (Math.abs(o4) <= 0.5 && onSegment(c, b, d)) return { ...b };
    return null;
  };
  const sampleElement = (el, step) => {
    const tag = el.tagName.toLowerCase();
    const local = [];
    const sampleSegment = (x1, y1, x2, y2) => {
      const length = Math.hypot(x2 - x1, y2 - y1);
      if (!Number.isFinite(length) || length <= 0) return;
      const count = Math.min(900, Math.max(2, Math.ceil(length / step) + 1));
      for (let i = 0; i < count; i += 1) {
        const t = i / (count - 1);
        local.push(new DOMPoint(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t));
      }
    };
    if (tag === "path") {
      const length = el.getTotalLength();
      const count = Math.min(900, Math.max(2, Math.ceil(length / step) + 1));
      for (let i = 0; i < count; i += 1) {
        local.push(el.getPointAtLength((length * i) / (count - 1)));
      }
    } else if (tag === "line") {
      const x1 = Number(el.getAttribute("x1"));
      const y1 = Number(el.getAttribute("y1"));
      const x2 = Number(el.getAttribute("x2"));
      const y2 = Number(el.getAttribute("y2"));
      sampleSegment(x1, y1, x2, y2);
    } else if (tag === "polyline") {
      const raw = el.getAttribute("points") || "";
      const values = raw.trim().split(/[\s,]+/).map(Number).filter(Number.isFinite);
      for (let i = 0; i + 1 < values.length; i += 2) {
        local.push(new DOMPoint(values[i], values[i + 1]));
      }
    } else if (tag === "polygon") {
      const raw = el.getAttribute("points") || "";
      const values = raw.trim().split(/[\s,]+/).map(Number).filter(Number.isFinite);
      const vertices = [];
      for (let i = 0; i + 1 < values.length; i += 2) {
        vertices.push({ x: values[i], y: values[i + 1] });
      }
      if (vertices.length > 1) {
        for (let i = 0; i < vertices.length; i += 1) {
          const start = vertices[i];
          const end = vertices[(i + 1) % vertices.length];
          sampleSegment(start.x, start.y, end.x, end.y);
        }
      }
    } else if (tag === "rect") {
      const x = Number(el.getAttribute("x") || 0);
      const y = Number(el.getAttribute("y") || 0);
      const width = Number(el.getAttribute("width") || 0);
      const height = Number(el.getAttribute("height") || 0);
      if (Number.isFinite(width) && Number.isFinite(height) && width > 0 && height > 0) {
        sampleSegment(x, y, x + width, y);
        sampleSegment(x + width, y, x + width, y + height);
        sampleSegment(x + width, y + height, x, y + height);
        sampleSegment(x, y + height, x, y);
      }
    } else if (tag === "circle" || tag === "ellipse") {
      const cx = Number(el.getAttribute("cx") || 0);
      const cy = Number(el.getAttribute("cy") || 0);
      const rx = Number(el.getAttribute(tag === "circle" ? "r" : "rx") || 0);
      const ry = Number(el.getAttribute(tag === "circle" ? "r" : "ry") || 0);
      const count = 128;
      if (Number.isFinite(rx) && Number.isFinite(ry) && rx > 0 && ry > 0) {
        for (let i = 0; i < count; i += 1) {
          const angle = (Math.PI * 2 * i) / count;
          local.push(new DOMPoint(cx + Math.cos(angle) * rx, cy + Math.sin(angle) * ry));
        }
        local.push(local[0]);
      }
    }
    const m = localToRoot(el);
    return m ? local.map((p) => p.matrixTransform(m)) : [];
  };
  const distanceFromPolylineEndpoints = (p, points) => {
    if (!points.length) return Infinity;
    return Math.min(Math.hypot(p.x - points[0].x, p.y - points[0].y), Math.hypot(p.x - points[points.length - 1].x, p.y - points[points.length - 1].y));
  };
  const visibleStroke = (el) => {
    const style = getComputedStyle(el);
    const stroke = el.getAttribute("stroke") || style.stroke;
    const strokeWidth = Number.parseFloat(el.getAttribute("stroke-width") || style.strokeWidth || "0");
    const opacity = Number.parseFloat(style.opacity || "1");
    const strokeOpacity = Number.parseFloat(style.strokeOpacity || "1");
    if (!stroke || stroke === "none" || !Number.isFinite(strokeWidth) || strokeWidth <= 0) return null;
    if (style.display === "none" || style.visibility === "hidden" || opacity <= 0 || strokeOpacity <= 0) return null;
    if (el.closest('[data-backdrop="true"]') && opacity * strokeOpacity <= 0.28) return null;
    const svg = svgRoot(el);
    const rootCtm = svg?.getScreenCTM?.();
    const ctm = el.getScreenCTM?.();
    const rootScale = rootCtm && ctm ? Math.hypot(ctm.a, ctm.b) / Math.max(0.001, Math.hypot(rootCtm.a, rootCtm.b)) : 1;
    return { width: strokeWidth * rootScale };
  };
  const renderedFontSize = (el) => {
    const size = Number.parseFloat(getComputedStyle(el).fontSize);
    const ctm = el.getScreenCTM?.();
    if (!Number.isFinite(size)) return null;
    const scale = ctm ? Math.hypot(ctm.a, ctm.b) : 1;
    return size * scale;
  };
  const figures = [];
  document.querySelectorAll("figure.viz").forEach((figure, figureIndex) => {
    const svg = figure.querySelector("svg");
    if (!svg) return;
    const contract = figure.dataset.layoutContract || svg.dataset.layoutContract || "";
    const figureId = figure.dataset.visualId || figure.id || `figure-${figureIndex + 1}`;
    const visualMode = (figure.dataset.visualMode || svg.dataset.visualMode || "").trim().toLowerCase();
    const countVisualPrimitives = () => {
      let count = 0;
      const defsPatterns = svg.querySelectorAll("defs pattern, defs linearGradient, defs radialGradient, defs filter");
      if (defsPatterns.length) count += Math.min(2, defsPatterns.length);
      const nonLinkShapes = [...svg.querySelectorAll("path,circle,ellipse,polygon,polyline,line")].filter((el) => {
        if (el.closest("defs") || el.closest("[data-callout-badge]") || el.closest('[data-backdrop="true"]')) return false;
        if (el.hasAttribute("data-link") || el.hasAttribute("data-callout-leader")) return false;
        return true;
      });
      count += nonLinkShapes.length;
      const objectGroups = svg.querySelectorAll("[data-object]");
      count += objectGroups.length;
      svg.querySelectorAll("[data-node]").forEach((nodeEl) => {
        const directRects = [...nodeEl.querySelectorAll("rect")].filter(
          (r) => !r.closest("defs") && !r.closest("[data-callout-badge]") && r.closest("[data-node]") === nodeEl
        );
        if (directRects.length > 1) count += directRects.length - 1;
      });
      return count;
    };
    const visualPrimitives = countVisualPrimitives();
    const strokeAudit = (() => {
      const violations = [];
      const addLegacyViolation = (severity, code, message, details = {}, fix = "") => {
        violations.push({ severity, code, message, ...details, fix });
      };
      const texts = [...figure.querySelectorAll("text")]
        .filter((text) => !text.closest("defs"))
        .map((el, index) => ({
          el,
          rect: rectOf(el),
          fontPx: renderedFontSize(el),
          text: el.textContent.trim().slice(0, 36) || `text-${index + 1}`,
        }))
        .filter((item) => item.rect);
      const minTextPx = numberAttr(svg, "min-text-px", 12);
      texts.forEach((text) => {
        if (text.fontPx !== null && text.fontPx + 0.05 < minTextPx) {
          addLegacyViolation(
            "error",
            "TEXT_TOO_SMALL",
            `文字“${text.text}”实际渲染约 ${round(text.fontPx)}px，小于 ${minTextPx}px。`,
            { figure: figureId, text: text.text, fontPx: round(text.fontPx), minimum: minTextPx },
            "提高字号或扩大 SVG 显示宽度；核心标签不低于 14px，次要说明不低于 12px。"
          );
        }
      });
      const strokeEls = [...figure.querySelectorAll("path,line,polyline,rect,circle,ellipse,polygon")]
        .filter((el) => !el.closest("defs"))
        .map((el, index) => {
          const style = visibleStroke(el);
          if (!style) return null;
          const sampleStep = numberAttr(svg, "sample-step", 2);
          const points = sampleElement(el, sampleStep);
          const maxContinuousJump = Math.max(12, sampleStep * 6);
          const segments = [];
          for (let pointIndex = 0; pointIndex < points.length - 1; pointIndex += 1) {
            const start = points[pointIndex];
            const end = points[pointIndex + 1];
            if (Math.hypot(end.x - start.x, end.y - start.y) <= maxContinuousJump) segments.push([start, end]);
          }
          if (!segments.length) return null;
          return {
            el,
            segments,
            width: style.width,
            id: el.dataset.link || el.id || `${el.tagName.toLowerCase()}-${index + 1}`,
          };
        })
        .filter((item) => item);
      texts.forEach((text) => {
        strokeEls.forEach((stroke) => {
          const badgeGroup = stroke.el.dataset.badgeShape === "true" ? stroke.el.closest("[data-callout-badge]") : null;
          if (badgeGroup && text.el.closest("[data-callout-badge]") === badgeGroup) return;
          let overlapsText = false;
          let touchesText = false;
          const strokePadding = Math.max(1.5, stroke.width / 2 + 0.5);
          const strokeTouchRect = expand(text.rect, strokePadding);
          for (const [start, end] of stroke.segments) {
            if (segmentIntersectsRect(start, end, text.rect)) {
              overlapsText = true;
              break;
            }
            if (!touchesText && segmentIntersectsRect(start, end, strokeTouchRect)) touchesText = true;
          }
          if (overlapsText) {
            const graphicTag = stroke.el.tagName.toLowerCase();
            const code = graphicTag === "line" ? "TEXT_LINE_OVERLAP" : graphicTag === "path" ? "TEXT_PATH_OVERLAP" : "TEXT_SHAPE_OVERLAP";
            addLegacyViolation(
              "error",
              code,
              `图形 ${stroke.id} 穿过文字“${text.text}”。`,
              { figure: figureId, text: text.text, graphic: stroke.id },
              "把文字移出路径通道，或缩短/改道该路径；文字与线条不得相交。"
            );
          } else if (touchesText) {
            addLegacyViolation(
              "warning",
              "TEXT_LABEL_TOUCHES_STROKE",
              `图形 ${stroke.id} 贴近文字“${text.text}”。`,
              { figure: figureId, text: text.text, graphic: stroke.id },
              "为文字和线条留出独立间距，避免渲染时因描边宽度发生视觉粘连。"
            );
          }
        });
      });
      const targetBoxes = [...figure.querySelectorAll("[data-target-for]")];
      targetBoxes.forEach((box) => {
        const objectId = box.dataset.targetFor;
        const object = document.getElementById(objectId);
        if (!object || !svg.contains(object)) {
          addLegacyViolation(
            "error",
            "TARGET_OBJECT_MISSING",
            `目标框引用的对象 ${objectId} 不在当前 SVG 中。`,
            { figure: figureId, object: objectId },
            "用 data-target-for 指向本图中实际对象的唯一 id。"
          );
          return;
        }
        const boxRect = rectOf(box);
        const objectRect = rectOf(object);
        if (!boxRect || !objectRect || objectRect.x < boxRect.x - 0.5 || objectRect.y < boxRect.y - 0.5 || objectRect.right > boxRect.right + 0.5 || objectRect.bottom > boxRect.bottom + 0.5) {
          addLegacyViolation(
            "error",
            "TARGET_BOX_MISS",
            `目标框没有完整覆盖对象 ${objectId}。`,
            { figure: figureId, object: objectId },
            "按对象的实际几何边界调整目标框，并人工核对是否指向了正确的对象。"
          );
        }
      });
      const calloutBadges = [...figure.querySelectorAll("[data-callout-badge]")]
        .filter((el) => !el.closest("defs"))
        .map((el, index) => ({
          el,
          id: (el.dataset.calloutBadge || `badge-${index + 1}`).trim(),
          rect: rectOf(el),
        }))
        .filter((item) => item.rect);
      calloutBadges.forEach((badge) => {
        const shapeEl = badge.el.querySelector('[data-badge-shape="true"]');
        const shapeRect = shapeEl ? rectOf(shapeEl) : null;
        if (shapeRect) {
          badge.el.querySelectorAll("text").forEach((textEl) => {
            const tRect = rectOf(textEl);
            if (!tRect) return;
            if (
              tRect.x < shapeRect.x + 1 ||
              tRect.y < shapeRect.y + 1 ||
              tRect.right > shapeRect.right - 1 ||
              tRect.bottom > shapeRect.bottom - 1
            ) {
              addLegacyViolation(
                "error",
                "BADGE_TEXT_OVERFLOW",
                `编号锚点“${badge.id}”内的文字超出锚点外框。`,
                { figure: figureId, badge: badge.id, text: textEl.textContent.trim() },
                "适当增大锚点图形半径（建议 r>=14）或缩短锚点序号。"
              );
            }
          });
        }
      });
      for (let i = 0; i < calloutBadges.length; i += 1) {
        for (let j = i + 1; j < calloutBadges.length; j += 1) {
          const ov = overlapSize(calloutBadges[i].rect, calloutBadges[j].rect);
          if (ov.width > 0.5 && ov.height > 0.5) {
            addLegacyViolation(
              "error",
              "CALLOUT_BADGE_OVERLAP",
              `编号锚点 ${calloutBadges[i].id} 与 ${calloutBadges[j].id} 重叠。`,
              { figure: figureId, badges: [calloutBadges[i].id, calloutBadges[j].id] },
              "拉开编号锚点位置，按阅读顺序分布在画面清晰空位。"
            );
          }
        }
      }
      if (["interface", "scene", "metaphor", "mechanism", "before-after", "cutaway"].includes(visualMode) && visualPrimitives < 4) {
        addLegacyViolation(
          "warning",
          "VISUAL_TOO_SCHEMATIC",
          `图“${figureId}”声明为 ${visualMode} 可视化画面，但视觉原语仅 ${visualPrimitives} 项，疑似退化为纯方框连线图。`,
          { figure: figureId, visualMode, visualPrimitives },
          "参考 references/visual-svg-cookbook.md，补充界面框架、物体轮廓、状态隐喻或对比细节，确保通过去字可辨检验。"
        );
      }
      const errors = violations.filter((item) => item.severity === "error");
      const warnings = violations.filter((item) => item.severity === "warning");
      return {
        id: figureId,
        contract: contract || "(missing)",
        visualMode: visualMode || "",
        skipped: false,
        legacy: true,
        status: errors.length ? "error" : warnings.length ? "warning" : "pass",
        counts: { nodes: 0, links: 0, labels: 0, texts: texts.length, strokes: strokeEls.length, targets: targetBoxes.length, badges: calloutBadges.length, visualPrimitives },
        violations,
      };
    })();
    if (contract !== "v1") {
      figures.push(strokeAudit);
      return;
    }

    const minNodeGap = numberAttr(svg, "min-node-gap", 16);
    const textPadding = numberAttr(svg, "text-padding", 8);
    const linkNodeClearance = numberAttr(svg, "link-node-clearance", 6);
    const linkTextClearance = numberAttr(svg, "link-text-clearance", 4);
    const linkGap = numberAttr(svg, "link-gap", 8);
    const attachTolerance = numberAttr(svg, "attach-tolerance", 18);
    const attachPenetration = numberAttr(svg, "attach-penetration", 5);
    const safeMargin = numberAttr(svg, "safe-margin", 24);
    const sampleStep = numberAttr(svg, "sample-step", 4);
    const viewBox = svg.viewBox.baseVal;
    const violations = [...strokeAudit.violations];

    const addViolation = (severity, code, message, details = {}, fix = "") => {
      violations.push({
        severity,
        code,
        message,
        ...details,
        fix,
      });
    };

    if (!viewBox || !viewBox.width || !viewBox.height) {
      addViolation("error", "VIEWBOX_MISSING", "SVG 缺少有效 viewBox。", {}, "设置明确的 viewBox，并让所有坐标落在其范围内。");
      figures.push({ id: figureId, contract, skipped: false, status: "error", violations });
      return;
    }

    // 整图被缩小会让所有文字按同一比例缩水：标称 14px 的标签在 0.98 倍下只有 13.7px。
    // 这是 TEXT_TOO_SMALL 的根因，因此单独报告，提示改容器而不是逐个调字号。
    const renderedWidth = svg.getBoundingClientRect().width;
    const figureScale = renderedWidth / viewBox.width;
    if (figureScale < 0.995) {
      addViolation(
        "error",
        "FIGURE_SHRUNK",
        `图“${figureId}”整图渲染为 viewBox 的 ${round(figureScale * 100)}%（${round(renderedWidth)}px / ${round(viewBox.width)}px），文字与线宽同比缩水。`,
        { figure: figureId, viewBoxWidth: round(viewBox.width), renderedWidth: round(renderedWidth), scale: round(figureScale * 1000) / 1000 },
        "给 figure.viz 设置 --viz-min-w: <viewBox 宽度>px，让窄屏改为横向滚动而不是缩小整图。"
      );
    }

    const nodeEls = [...figure.querySelectorAll("[data-node]")];
    const nodes = [];
    const nodeIds = new Set();
    nodeEls.forEach((el, index) => {
      const id = el.dataset.node || `node-${index + 1}`;
      if (nodeIds.has(id)) {
        addViolation("error", "NODE_ID_DUPLICATE", `节点 id 重复：${id}`, { node: id }, "为每个 data-node 使用唯一 id。");
      }
      nodeIds.add(id);
      if (el.tagName.toLowerCase() !== "g") {
        addViolation("warning", "NODE_NOT_GROUP", `节点 ${id} 没有使用 <g> 包裹。`, { node: id }, "用 <g data-node=\"...\"> 包裹节点图形和文字，便于检查文字内边距。");
      }
      const rect = rectOf(el);
      if (!rect) {
        addViolation("error", "NODE_BBOX_MISSING", `节点 ${id} 无法计算边界。`, { node: id }, "确认节点已渲染且有非零尺寸。");
        return;
      }
      nodes.push({
        id,
        el,
        rect,
        expanded: expand(rect, linkNodeClearance),
      });
    });

    const nodeMap = new Map(nodes.map((node) => [node.id, node]));
    const nodePairs = [];
    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i];
        const b = nodes[j];
        const nested = a.el.contains(b.el) || b.el.contains(a.el) || a.el.dataset.nested === "true" || b.el.dataset.nested === "true";
        nodePairs.push({ a, b, nested });
        if (nested) continue;
        const overlap = overlapSize(a.rect, b.rect);
        const intersects = overlap.width > 0.5 && overlap.height > 0.5;
        if (intersects) {
          addViolation(
            "error",
            "NODE_OVERLAP",
            `节点 ${a.id} 与 ${b.id} 重叠 ${round(overlap.width)} × ${round(overlap.height)}。`,
            { nodes: [a.id, b.id], overlap: { width: round(overlap.width), height: round(overlap.height) } },
            "重新分配网格单元；至少保留 16px 节点间距。"
          );
        } else {
          const gap = rectGap(a.rect, b.rect);
          if (gap < minNodeGap) {
            addViolation(
              "error",
              "NODE_GAP_TOO_SMALL",
              `节点 ${a.id} 与 ${b.id} 的间距 ${round(gap)}px，小于 ${minNodeGap}px。`,
              { nodes: [a.id, b.id], gap: round(gap), minimum: minNodeGap },
              "扩大列间距或行间距，不要靠减小留白塞内容。"
            );
          }
        }
      }
    }

    nodes.forEach((node) => {
      const texts = [...node.el.querySelectorAll("text")].filter((text) => text.closest("[data-node]") === node.el);
      texts.forEach((text, index) => {
        const rect = rectOf(text);
        if (!rect) return;
        const label = text.textContent.trim().slice(0, 36) || `text-${index + 1}`;
        if (
          rect.x < node.rect.x + textPadding - 0.5 ||
          rect.y < node.rect.y + textPadding - 0.5 ||
          rect.right > node.rect.right - textPadding + 0.5 ||
          rect.bottom > node.rect.bottom - textPadding + 0.5
        ) {
          addViolation(
            "error",
            "TEXT_PADDING_TOO_SMALL",
            `节点 ${node.id} 的文字“${label}”未保留 ${textPadding}px 内边距。`,
            { node: node.id, text: label, rect: { x: round(rect.x), y: round(rect.y), width: round(rect.width), height: round(rect.height) } },
            "扩大节点尺寸、缩短文案，或把长说明移到图注。"
          );
        }
      });
    });

    const allTexts = [...figure.querySelectorAll("text")]
      .filter((text) => !text.closest("defs"))
      .map((el) => ({ el, rect: rectOf(el), fontPx: renderedFontSize(el), text: el.textContent.trim().slice(0, 36) }))
      .filter((item) => item.rect);
    const minTextPx = numberAttr(svg, "min-text-px", 12);
    allTexts.forEach((text) => {
      if (text.fontPx !== null && text.fontPx + 0.05 < minTextPx) {
        addViolation(
          "error",
          "TEXT_TOO_SMALL",
          `文字“${text.text}”实际渲染约 ${round(text.fontPx)}px，小于 ${minTextPx}px。`,
          { text: text.text, fontPx: round(text.fontPx), minimum: minTextPx },
          "提高字号或扩大 SVG 显示宽度；核心标签不低于 14px，次要说明不低于 12px。"
        );
      }
    });
    for (let i = 0; i < allTexts.length; i += 1) {
      for (let j = i + 1; j < allTexts.length; j += 1) {
        const a = allTexts[i];
        const b = allTexts[j];
        const overlap = overlapSize(a.rect, b.rect);
        if (overlap.width > 1 && overlap.height > 1) {
          addViolation(
            "error",
            "TEXT_OVERLAP",
            `文字“${a.text}”与“${b.text}”重叠。`,
            { texts: [a.text, b.text], overlap: { width: round(overlap.width), height: round(overlap.height) } },
            "将标签移到独立标注带，或缩短文字。"
          );
        }
      }
    }

    const linkEls = [...figure.querySelectorAll("[data-link]")];
    const links = [];
    linkEls.forEach((el, index) => {
      const id = el.dataset.link || `link-${index + 1}`;
      const from = el.dataset.from || "";
      const to = el.dataset.to || "";
      const missingEndpoints = [];
      if (!from.trim()) missingEndpoints.push("data-from");
      if (!to.trim()) missingEndpoints.push("data-to");
      if (missingEndpoints.length) {
        addViolation(
          "error",
          "LINK_ENDPOINT_MISSING",
          `连线 ${id} 缺少非空端点引用：${missingEndpoints.join("、")}。`,
          { link: id, missingEndpoints },
          "为每条 data-link 填写可解析到 data-node 的非空 data-from 与 data-to。"
        );
      }
      const points = sampleElement(el, sampleStep);
      if (points.length < 2) {
        addViolation("error", "LINK_SAMPLE_FAILED", `连线 ${id} 无法采样。`, { link: id }, "使用 path、line 或 polyline，并保证坐标有效。");
        return;
      }
      links.push({
        id,
        el,
        points,
        rect: rectFromPoints(points),
        from,
        to,
        laneGroup: el.dataset.laneGroup || "",
        allowCrossing: el.dataset.allowCrossing === "true",
      });
    });

    links.forEach((link) => {
      if (link.from.trim() && !nodeMap.has(link.from)) {
        addViolation("error", "LINK_FROM_UNKNOWN", `连线 ${link.id} 的 data-from="${link.from}" 未找到节点。`, { link: link.id }, "修正 data-from 或添加对应节点。");
      }
      if (link.to.trim() && !nodeMap.has(link.to)) {
        addViolation("error", "LINK_TO_UNKNOWN", `连线 ${link.id} 的 data-to="${link.to}" 未找到节点。`, { link: link.id }, "修正 data-to 或添加对应节点。");
      }
      const endpoints = [
        { nodeId: link.from, point: link.points[0], label: "起点" },
        { nodeId: link.to, point: link.points[link.points.length - 1], label: "终点" },
      ];
      endpoints.forEach(({ nodeId, point, label }) => {
        if (!nodeId || !nodeMap.has(nodeId)) return;
        const node = nodeMap.get(nodeId);
        const outside = distancePointToRect(point, node.rect);
        const inside = penetrationInRect(point, node.rect);
        if (outside > attachTolerance || inside > attachPenetration) {
          addViolation(
            "error",
            "LINK_ATTACHMENT_MISS",
            `连线 ${link.id} ${label}未准确接到节点 ${nodeId}（外侧 ${round(outside)}px，内侧 ${round(inside)}px）。`,
            { link: link.id, node: nodeId, endpoint: label, outside: round(outside), inside: round(inside) },
            "把端点与目标节点边界对齐；不要悬空，也不要深入节点。"
          );
        }
      });

      nodes.forEach((node) => {
        for (let i = 0; i < link.points.length; i += 1) {
          const point = link.points[i];
          if (node.id === link.from || node.id === link.to) {
            const endpointDistance = Math.min(
              Math.hypot(point.x - link.points[0].x, point.y - link.points[0].y),
              Math.hypot(point.x - link.points[link.points.length - 1].x, point.y - link.points[link.points.length - 1].y)
            );
            if (endpointDistance < 20) continue;
          }
          if (pointInRect(point, node.expanded)) {
            addViolation(
              "error",
              "LINK_THROUGH_NODE",
              `连线 ${link.id} 穿过或贴近节点 ${node.id}。`,
              { link: link.id, node: node.id, point: { x: round(point.x), y: round(point.y) } },
              "换用独立布线通道，从节点外侧绕行；保持至少 6px 净距。"
            );
            break;
          }
        }
      });
      for (const text of allTexts) {
        const textRect = expand(text.rect, linkTextClearance);
        const hit = link.points.find((point) => pointInRect(point, textRect));
        if (hit) {
          addViolation(
            "error",
            "LINK_THROUGH_TEXT",
            `连线 ${link.id} 穿过文字“${text.text}”。`,
            { link: link.id, text: text.text, point: { x: round(hit.x), y: round(hit.y) } },
            "把文字移出连线通道，或从文字外侧绕线。"
          );
        }
      }
    });

    const labels = [...figure.querySelectorAll("[data-link-label]")];
    labels.forEach((el, index) => {
      const id = el.dataset.linkLabel || `label-${index + 1}`;
      const linkId = el.dataset.for || "";
      const link = links.find((item) => item.id === linkId);
      const rect = rectOf(el);
      if (!rect) return;
      if (!link) {
        addViolation("warning", "LINK_LABEL_ORPHAN", `连线标签 ${id} 的 data-for="${linkId}" 未找到连线。`, { label: id, link: linkId }, "修正 data-for 或移除孤儿标签。");
        return;
      }
      let best = Infinity;
      link.points.forEach((point) => {
        best = Math.min(best, distancePointToRect(point, rect));
      });
      if (best < linkTextClearance) {
        addViolation(
          "error",
          "LINK_LABEL_TOO_CLOSE",
          `连线标签 ${id} 距连线 ${linkId} 仅 ${round(best)}px。`,
          { label: id, link: linkId, gap: round(best), minimum: linkTextClearance },
          "把标签放到独立标注带，保持至少 8px 间距。"
        );
      }
      nodes.forEach((node) => {
        if (rectGap(rect, node.rect) < 6) {
          addViolation(
            "error",
            "LINK_LABEL_TOUCHES_NODE",
            `连线标签 ${id} 距节点 ${node.id} 过近。`,
            { label: id, node: node.id },
            "把标签移到节点与连线之间的空带，或缩短标签。"
          );
        }
      });
    });

    for (let i = 0; i < links.length; i += 1) {
      for (let j = i + 1; j < links.length; j += 1) {
        const a = links[i];
        const b = links[j];
        if (a.from === b.from && a.to === b.to) continue;
        if (a.allowCrossing || b.allowCrossing) continue;
        let crossing = null;
        for (let ai = 0; ai < a.points.length - 1 && !crossing; ai += 1) {
          for (let bi = 0; bi < b.points.length - 1 && !crossing; bi += 1) {
            const hit = segmentIntersection(a.points[ai], a.points[ai + 1], b.points[bi], b.points[bi + 1]);
            if (!hit) continue;
            const tooNearEndpoint =
              distanceFromPolylineEndpoints(hit, a.points) < 14 ||
              distanceFromPolylineEndpoints(hit, b.points) < 14;
            if (!tooNearEndpoint) crossing = hit;
          }
        }
        if (crossing) {
          addViolation(
            "error",
            "LINK_CROSSING",
            `连线 ${a.id} 与 ${b.id} 交叉。`,
            { links: [a.id, b.id], point: { x: round(crossing.x), y: round(crossing.y) } },
            "调整节点顺序，或给每条连线分配不同的水平/垂直通道。"
          );
        } else if (a.laneGroup !== b.laneGroup || !a.laneGroup) {
          let minDistance = Infinity;
          const aSafe = a.points.filter((point) => distanceFromPolylineEndpoints(point, a.points) > 24);
          const bSafe = b.points.filter((point) => distanceFromPolylineEndpoints(point, b.points) > 24);
          const aStride = Math.max(1, Math.floor(aSafe.length / 80));
          const bStride = Math.max(1, Math.floor(bSafe.length / 80));
          for (let ai = 0; ai < aSafe.length; ai += aStride) {
            for (let bi = 0; bi < bSafe.length; bi += bStride) {
              const d = Math.hypot(aSafe[ai].x - bSafe[bi].x, aSafe[ai].y - bSafe[bi].y);
              if (d < minDistance) minDistance = d;
            }
          }
          if (minDistance < linkGap) {
            addViolation(
              "warning",
              "LINK_TOO_CLOSE",
              `连线 ${a.id} 与 ${b.id} 最近距离 ${round(minDistance)}px，小于 ${linkGap}px。`,
              { links: [a.id, b.id], gap: round(minDistance), minimum: linkGap },
              "给平行连线分配不同通道，或用 data-lane-group 明确共享总线。"
            );
          }
        }
      }
    }

    const checkBounds = (kind, id, rect, margin) => {
      if (!rect) return;
      const epsilon = 1e-6;
      if (
        rect.x < -0.5 ||
        rect.y < -0.5 ||
        rect.right > viewBox.width + 0.5 ||
        rect.bottom > viewBox.height + 0.5 ||
        rect.x < margin - epsilon ||
        rect.y < margin - epsilon ||
        rect.right > viewBox.width - margin + epsilon ||
        rect.bottom > viewBox.height - margin + epsilon
      ) {
        addViolation(
          "error",
          "VIEWBOX_OVERFLOW",
          `${kind} ${id} 超出 viewBox 或安全边距。`,
          { kind, id, rect: { x: round(rect.x), y: round(rect.y), width: round(rect.width), height: round(rect.height) }, safeMargin: margin },
          "扩展 viewBox，或把元素移回安全绘制区。"
        );
      }
    };
    nodes.forEach((node) => checkBounds("节点", node.id, node.rect, safeMargin));
    links.forEach((link) => {
      if (link.rect && (link.rect.x < 0 || link.rect.y < 0 || link.rect.right > viewBox.width || link.rect.bottom > viewBox.height)) {
        addViolation(
          "error",
          "VIEWBOX_OVERFLOW",
          `连线 ${link.id} 超出 viewBox。`,
          { kind: "连线", id: link.id, rect: { x: round(link.rect.x), y: round(link.rect.y), width: round(link.rect.width), height: round(link.rect.height) } },
          "扩展 viewBox，或调整布线通道。"
        );
      }
    });
    allTexts.forEach((item, index) => checkBounds("文字", `text-${index + 1}`, item.rect, 0));
    [...figure.querySelectorAll("[data-callout-badge]")].forEach((badgeEl, index) => {
      if (badgeEl.closest("defs")) return;
      const bRect = rectOf(badgeEl);
      checkBounds("编号锚点", badgeEl.dataset.calloutBadge || `badge-${index + 1}`, bRect, 4);
    });

    const errors = violations.filter((item) => item.severity === "error");
    const warnings = violations.filter((item) => item.severity === "warning");
    figures.push({
      id: figureId,
      contract,
      visualMode: visualMode || "",
      skipped: false,
      status: errors.length ? "error" : warnings.length ? "warning" : "pass",
      counts: {
        nodes: nodes.length,
        links: links.length,
        labels: labels.length,
        texts: allTexts.length,
        strokes: strokeAudit.counts.strokes,
        targets: strokeAudit.counts.targets,
        badges: strokeAudit.counts.badges,
        visualPrimitives,
      },
      violations,
    });
  });

  const pageViolations = [];
  const coverage = [];
  const logicSync = [];
  document.querySelectorAll("[data-for-visual]").forEach((listEl) => {
    const visualId = (listEl.dataset.forVisual || "").trim();
    if (!visualId) return;
    const figure = [...document.querySelectorAll("figure.viz")].find((item) => item.dataset.visualId === visualId);
    if (!figure) {
      logicSync.push({ visual: visualId, badges: [], points: [], missingInList: [], missingInSvg: [], status: "error" });
      pageViolations.push({
        severity: "error",
        code: "LOGIC_VISUAL_MISSING",
        message: `分点说明关联的图示 ${visualId} 不存在于页面中。`,
        fix: "核对 data-for-visual 与对应 figure.viz 的 data-visual-id 是否一致。",
      });
      return;
    }
    const badgeSet = new Set(
      [...figure.querySelectorAll("[data-callout-badge]")]
        .filter((el) => !el.closest("defs"))
        .map((el) => (el.dataset.calloutBadge || "").trim())
        .filter(Boolean)
    );
    const pointSet = new Set(
      [...listEl.querySelectorAll("[data-point]")]
        .filter((el) => el.dataset.noBadge !== "true")
        .map((el) => (el.dataset.point || "").trim())
        .filter(Boolean)
    );
    const missingInList = [...badgeSet].filter((id) => !pointSet.has(id));
    const missingInSvg = [...pointSet].filter((id) => !badgeSet.has(id));
    const status = missingInList.length || missingInSvg.length ? "error" : "pass";
    logicSync.push({ visual: visualId, badges: [...badgeSet], points: [...pointSet], missingInList, missingInSvg, status });
    if (missingInList.length || missingInSvg.length) {
      pageViolations.push({
        severity: "error",
        code: "CALLOUT_POINT_MISMATCH",
        message: `图示 ${visualId} 的编号锚点与分点说明未对齐（图有文无：${missingInList.join(",") || "无"}；文有图无：${missingInSvg.join(",") || "无"}）。`,
        fix: "让 SVG 中的 data-callout-badge（1–6）与 .logic-points 中的 data-point（1–6）完全对应；纯总括分点可加 data-no-badge=\"true\"。",
      });
    }
  });
  document.querySelectorAll('[data-required-visuals]').forEach((group, index) => {
    const required = group.dataset.requiredVisuals.trim().split(/\s+/).filter(Boolean);
    const available = [...group.querySelectorAll('figure.viz')];
    const missing = [];
    const duplicates = [];
    for (const visualId of new Set(required)) {
      const matches = available.filter((figure) => figure.dataset.visualId === visualId);
      if (matches.length > 1) duplicates.push(visualId);
      if (matches.length !== 1 || !matches[0].querySelector('svg')) missing.push(visualId);
    }
    const groupId = group.id || `coverage-${index + 1}`;
    coverage.push({ group: groupId, required, missing, duplicates, status: missing.length ? 'error' : 'pass' });
    for (const visualId of missing) {
      pageViolations.push({
        severity: 'error',
        code: duplicates.includes(visualId) ? 'CONTENT_VISUAL_DUPLICATE' : 'CONTENT_VISUAL_MISSING',
        message: `${groupId} 的 ${visualId} 缺少唯一且包含 SVG 的解释图。`,
        fix: '为该内容条目补齐解释图，核对分组归属与 visual-id 唯一性。',
      });
    }
  });
  if (document.documentElement.scrollWidth > window.innerWidth + 1) {
    pageViolations.push({
      severity: "error",
      code: "PAGE_HORIZONTAL_OVERFLOW",
      message: `页面横向溢出：${document.documentElement.scrollWidth}px > ${window.innerWidth}px。`,
      fix: "把宽图放入 .viz-scroll；不要扩大页面根容器。",
    });
  }
  // 窄屏不缩小整图，改为横向滚动；因此凡是能横向滚动的图，必须给出可见的滑动提示。
  // 提示可以挂在 .viz-scroll 上，也可以挂在外层 .viz-card / .grammar-card 上。
  const pseudoHint = (el) => {
    const content = getComputedStyle(el, "::before").content || "";
    const hint = content.replace(/^["']|["']$/g, "").trim();
    return hint && hint !== "none" && hint !== "normal" ? hint : "";
  };
  document.querySelectorAll("figure.viz .viz-scroll").forEach((scrollEl) => {
    // 只有一两像素的溢出不会真正影响阅读，也不要求提示；明显需要滚动时才检查。
    const overflow = scrollEl.scrollWidth - scrollEl.clientWidth;
    if (overflow <= Math.max(24, scrollEl.clientWidth * 0.08)) return;
    const carriers = [scrollEl, scrollEl.closest(".viz-card"), scrollEl.closest(".grammar-card")];
    if (carriers.some((el) => el && pseudoHint(el))) return;
    const figure = scrollEl.closest("figure.viz");
    pageViolations.push({
      severity: "error",
      code: "SWIPE_HINT_MISSING",
      message: `${figure?.dataset?.visualId || "figure"} 需要横向滚动 ${round(overflow)}px（${scrollEl.scrollWidth}px > ${scrollEl.clientWidth}px），但没有可见的滑动提示。`,
      fix: "为 .viz-scroll 或外层 .viz-card 添加 ::before 文案，例如“左右滑动查看完整图示”。",
    });
  });
  document.querySelectorAll("figure.viz").forEach((figure) => {
    const figureRect = figure.getBoundingClientRect();
    const scrollRect = figure.querySelector(".viz-scroll")?.getBoundingClientRect();
    const captionRect = figure.querySelector("figcaption")?.getBoundingClientRect();
    if (scrollRect && captionRect) {
      const gap = captionRect.top - scrollRect.bottom;
      if (gap < 12) {
        pageViolations.push({
          severity: "error",
          code: "CAPTION_TOO_CLOSE",
          message: `${figure.dataset.visualId || "figure"} 的图示与图注仅相隔 ${round(gap)}px。`,
          fix: "在图注上方保留至少 12px 间距。",
        });
      }
    }
    const parentDisplay = figure.parentElement ? getComputedStyle(figure.parentElement).display : "";
    const inGroupedLayout = parentDisplay.includes("grid") || parentDisplay.includes("flex");
    if (!inGroupedLayout) {
      const siblings = [
        { el: figure.previousElementSibling, side: "before" },
        { el: figure.nextElementSibling, side: "after" },
      ];
      siblings.forEach(({ el, side }) => {
        if (!el) return;
        const siblingRect = el.getBoundingClientRect();
        const gap = side === "before" ? figureRect.top - siblingRect.bottom : siblingRect.top - figureRect.bottom;
        if (gap < 16) {
          pageViolations.push({
            severity: "error",
            code: "FIGURE_NEIGHBOR_TOO_CLOSE",
            message: `${figure.dataset.visualId || "figure"} 与${side === "before" ? "上方" : "下方"}内容仅相隔 ${round(gap)}px。`,
            fix: "图表与正文/图组之间保留至少 16px 间距。",
          });
        }
      });
    }
  });

  const passed = figures.filter((f) => !f.skipped && f.status === "pass").length;
  const warnings = figures.filter((f) => !f.skipped && f.status === "warning").length;
  const errors = figures.filter((f) => !f.skipped && f.status === "error").length;
  const skipped = figures.filter((f) => f.skipped).length;
  return {
    figures,
    coverage,
    logic_sync: logicSync,
    page_violations: pageViolations,
    summary: {
      total: figures.length,
      passed,
      warnings,
      errors,
      skipped,
      page_errors: pageViolations.filter((item) => item.severity === "error").length,
      page_warnings: pageViolations.filter((item) => item.severity === "warning").length,
    },
  };
}
"""


def file_url(value: str) -> str:
    if value.startswith(("http://", "https://", "file://")):
        return value
    return Path(value).expanduser().resolve().as_uri()


def launch_browser(playwright: Any, requested_channel: str | None) -> Any:
    channels = [requested_channel] if requested_channel else ["msedge", "chrome", None]
    last_error: Exception | None = None
    for channel in channels:
        try:
            return playwright.chromium.launch(channel=channel) if channel else playwright.chromium.launch()
        except PlaywrightError as exc:
            last_error = exc
    raise RuntimeError(f"无法启动 Chromium/Edge/Chrome：{last_error}")


def print_report(report: dict[str, Any]) -> None:
    summary = report["layout"]["summary"]
    print(
        "SVG LAYOUT: "
        f"total={summary['total']} pass={summary['passed']} "
        f"warn={summary['warnings']} error={summary['errors']} skipped={summary['skipped']} "
        f"page_error={summary['page_errors']} page_warn={summary['page_warnings']}"
    )
    if report["page_errors"]:
        print(f"PAGE ERRORS: {len(report['page_errors'])}")
        for error in report["page_errors"]:
            print(f"  - {error}")
    for group in report["layout"].get("coverage", []):
        print(f"CONTENT COVERAGE: {group['group']} {group['status'].upper()} required={len(group['required'])} missing={len(group['missing'])}")
    for item in report["layout"].get("logic_sync", []):
        print(f"LOGIC SYNC: {item['visual']} {item['status'].upper()} badges={len(item['badges'])} points={len(item['points'])}")
    for figure in report["layout"]["figures"]:
        if figure.get("skipped"):
            print(f"- {figure['id']}: SKIP contract={figure['contract']}")
            continue
        if figure.get("legacy"):
            counts = figure["counts"]
            print(
                f"- {figure['id']}: {figure['status'].upper()} "
                f"legacy texts={counts['texts']} strokes={counts['strokes']}"
            )
            for violation in figure["violations"]:
                print(f"  [{violation['severity'].upper()}] {violation['code']}: {violation['message']}")
                if violation.get("fix"):
                    print(f"    FIX: {violation['fix']}")
            continue
        mode_tag = f" mode={figure['visualMode']}" if figure.get("visualMode") else ""
        badges_tag = f" badges={figure['counts'].get('badges', 0)}" if figure["counts"].get("badges") else ""
        print(
            f"- {figure['id']}: {figure['status'].upper()} "
            f"nodes={figure['counts']['nodes']} links={figure['counts']['links']}"
            f"{mode_tag}{badges_tag} primitives={figure['counts'].get('visualPrimitives', 0)}"
        )
        for violation in figure["violations"]:
            print(f"  [{violation['severity'].upper()}] {violation['code']}: {violation['message']}")
            if violation.get("fix"):
                print(f"    FIX: {violation['fix']}")
    for violation in report["layout"].get("page_violations", []):
        print(f"  [{violation['severity'].upper()}] {violation['code']}: {violation['message']}")
        if violation.get("fix"):
            print(f"    FIX: {violation['fix']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SVG layout contracts and legacy text/path overlap.")
    parser.add_argument("target", help="HTML file path or http(s)/file URL.")
    parser.add_argument("--channel", choices=["msedge", "chrome", "chromium"], help="Browser channel. Auto-detect by default.")
    parser.add_argument("--json", dest="json_path", help="Write the full report to this JSON file.")
    parser.add_argument("--screenshot", help="Write a full-page screenshot for visual inspection.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    parser.add_argument("--timeout", type=int, default=30000, help="Page load timeout in milliseconds.")
    parser.add_argument("--viewport", default="1440x1000", help="Browser viewport as WIDTHxHEIGHT, e.g. 390x844.")
    args = parser.parse_args()

    try:
        viewport_width, viewport_height = (int(part) for part in args.viewport.lower().split("x", 1))
    except (TypeError, ValueError):
        parser.error("--viewport 必须使用 WIDTHxHEIGHT 格式，例如 390x844。")

    console_errors: list[str] = []
    page_errors: list[str] = []
    report: dict[str, Any]
    with sync_playwright() as playwright:
        try:
            browser = launch_browser(playwright, args.channel)
        except Exception as exc:  # noqa: BLE001 - CLI should show one clear startup error.
            print(str(exc), file=sys.stderr)
            return 2
        try:
            page = browser.new_page(
                viewport={"width": viewport_width, "height": viewport_height},
                device_scale_factor=1,
                is_mobile=viewport_width <= 480,
            )
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            page.goto(file_url(args.target), wait_until="networkidle", timeout=args.timeout)
            page.evaluate("() => document.fonts.ready")
            layout = page.evaluate(LAYOUT_JS)
            if args.screenshot:
                page.screenshot(path=args.screenshot, full_page=True)
            report = {
                "target": file_url(args.target),
                "viewport": {"width": viewport_width, "height": viewport_height},
                "console_errors": console_errors,
                "page_errors": page_errors,
                "layout": layout,
            }
        finally:
            browser.close()

    if args.json_path:
        Path(args.json_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print_report(report)
    summary = report["layout"]["summary"]
    failed = bool(report["page_errors"] or console_errors or summary["errors"] or summary["page_errors"])
    if args.strict and (summary["warnings"] or summary["page_warnings"]):
        failed = True
    if summary["total"] and summary["passed"] + summary["warnings"] + summary["errors"] == 0:
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
