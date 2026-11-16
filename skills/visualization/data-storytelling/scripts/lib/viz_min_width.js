// Ensure each figure keeps its SVG at the declared viewBox width.
// Without this, `.viz-scroll > svg { min-width }` can render the whole figure
// smaller than its viewBox, which shrinks every label below its declared
// data-min-text-px and makes text unreadable on narrow viewports.

const FIGURE_OPEN = /<figure\b[^>]*class="[^"]*\bviz\b[^"]*"[^>]*>/g;
const VIEW_BOX = /viewBox\s*=\s*["']\s*0\s+0\s+(\d+(?:\.\d+)?)/;

function setMinWidth(figureTag, width) {
  const variable = `--viz-min-w: ${width}px;`;
  const styleMatch = figureTag.match(/\sstyle\s*=\s*["']([^"']*)["']/i);
  if (styleMatch) {
    if (/--viz-min-w\s*:/.test(styleMatch[1])) return figureTag;
    const existing = styleMatch[1].trim().replace(/;\s*$/, "");
    const merged = existing ? `${existing}; ${variable}` : variable;
    const updated = ` style="${merged}"`;
    return figureTag.replace(styleMatch[0], updated);
  }
  return figureTag.replace(/>$/, ` style="${variable}">`);
}

function applyVizMinWidth(html) {
  let out = "";
  let cursor = 0;
  FIGURE_OPEN.lastIndex = 0;
  let match;
  while ((match = FIGURE_OPEN.exec(html)) !== null) {
    const tag = match[0];
    if (/--viz-min-w\s*:/.test(tag)) continue;
    const rest = html.slice(match.index + tag.length);
    const figureEnd = rest.search(/<figure\b|<\/figure>/i);
    const scope = figureEnd === -1 ? rest : rest.slice(0, figureEnd);
    const viewBox = scope.match(VIEW_BOX);
    if (!viewBox) continue;
    out += html.slice(cursor, match.index) + setMinWidth(tag, viewBox[1]);
    cursor = match.index + tag.length;
    FIGURE_OPEN.lastIndex = cursor;
  }
  out += html.slice(cursor);
  return out;
}

module.exports = { applyVizMinWidth };
