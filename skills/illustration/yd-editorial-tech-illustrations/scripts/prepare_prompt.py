import argparse
import hashlib
import json
from pathlib import Path


def read_json(file_path):
    return json.loads(file_path.read_text(encoding="utf-8-sig"))


def collect_render_strings(content):
    """提取所有将渲染到画面中的文本，供总字数预算校验与出图后逐字验收使用。"""
    items = []
    for key in ("eyebrow", "headline", "summary", "takeaway", "footer"):
        if content.get(key):
            items.append({"field": key, "text": content[key]})
    for sec in content["sections"]:
        items.append({"field": f"section:{sec['id']}.title", "text": sec["title"]})
        if sec.get("qualifier"):
            items.append({"field": f"section:{sec['id']}.qualifier", "text": sec["qualifier"]})
        if sec.get("explanation"):
            items.append({"field": f"section:{sec['id']}.explanation", "text": sec["explanation"]})
        for node in sec["nodes"]:
            items.append({"field": f"node:{node['id']}.title", "text": node["title"]})
            if node.get("caption"):
                items.append({"field": f"node:{node['id']}.caption", "text": node["caption"]})
    for idx, conn in enumerate(content.get("connections", [])):
        if conn.get("label"):
            items.append({"field": f"connection:{idx}.label", "text": conn["label"]})
    return items


def validate_content(content, style):
    max_nodes = style["max_nodes"]
    max_total_chars = style.get("max_total_chars", 180)
    required_fields = ("headline", "summary", "takeaway", "sections", "footer")
    for field_name in required_fields:
        if not content.get(field_name):
            raise ValueError(f"Missing content field: {field_name}")
    if "connections" not in content:
        raise ValueError("Missing content field: connections")

    def char_count(value):
        return len(value) if isinstance(value, str) else 0

    headline = content.get("headline", "")
    if char_count(headline) > 18:
        raise ValueError(f"Headline too long ({char_count(headline)} chars, max 18): keep one short sentence")
    summary = content.get("summary", "")
    if char_count(summary) > 32 or summary.strip().rstrip("。 .!！") == headline.strip().rstrip("。 .!！"):
        raise ValueError("Summary must be one clause (<=32 chars, <=24 recommended) that adds information, not a repeat of the headline")
    takeaway = content.get("takeaway", "")
    if char_count(takeaway) > 36 or any(mark in takeaway for mark in ("!", "！", "不要", "记住")):
        raise ValueError("Takeaway must be one factual sentence (<=36 chars), no imperative slogans or exclamation marks")

    for section in content["sections"]:
        qualifier = section.get("qualifier", "")
        if qualifier and isinstance(qualifier, str) and not qualifier.endswith(("时", "后", "前", "时,", "后,", "前,")):
            raise ValueError(f"Qualifier should state a real trigger condition (usually ending with 时/后/前): {qualifier!r}")
        explanation = section.get("explanation", "")
        if char_count(explanation) > 48:
            raise ValueError(f"Section explanation too long ({char_count(explanation)} chars, max 48): {section.get('id', '?')}")

    nodes = [node for section in content["sections"] for node in section["nodes"]]
    node_ids = [node["id"] for node in nodes]
    if not nodes or len(nodes) > max_nodes:
        raise ValueError(f"Use 1-{max_nodes} nodes (ideal 5-7); split denser material into multiple images")
    if len(set(node_ids)) != len(node_ids):
        raise ValueError("Node IDs must be unique")

    for node in nodes:
        if not node.get("title") or "caption" not in node:
            raise ValueError(f"Node requires a title and caption: {node['id']}")
        title = node["title"]
        caption = node.get("caption", "")
        if not (2 <= char_count(title) <= 8):
            raise ValueError(f"Node title should be 2-8 Chinese characters: {node['id']} {title!r}")
        if not (4 <= char_count(caption) <= 20):
            raise ValueError(f"Node caption should be 4-20 Chinese characters (ideal 6-16): {node['id']} {caption!r}")

    accent_count = sum(1 for connection in content["connections"] if connection.get("kind") == "accent")
    if accent_count > 1:
        raise ValueError("At most one connection may use kind=accent (single clay-orange highlight relation per image)")
    for connection in content["connections"]:
        for endpoint in ("from", "to"):
            if connection[endpoint] not in node_ids:
                raise ValueError(f"Unknown connection endpoint: {connection[endpoint]}")

    render_items = collect_render_strings(content)
    total_chars = sum(len(item["text"]) for item in render_items)
    if total_chars > max_total_chars:
        raise ValueError(
            f"Total rendered text too dense ({total_chars} chars, max {max_total_chars}); "
            "shorten captions or split into two diagrams"
        )

    warnings = []
    if char_count(summary) > 24:
        warnings.append(f"Summary is {char_count(summary)} chars (>24); consider tightening to reduce narrow-column wrap typo risk.")
    declared_logos = {logo["name"].lower() for logo in content.get("logo_references", [])}
    for node in nodes:
        tool_name = node.get("tool")
        if tool_name and tool_name.lower() not in declared_logos:
            warnings.append(f"Node {node['id']} declares tool {tool_name!r} without matching logo_references entry; render as clean text label only.")
    return render_items, total_chars, warnings


def build_request(skill_root, content, layout_name, image_path):
    style = read_json(skill_root / "references/style-lock.json")
    render_items, total_chars, warnings = validate_content(content, style)
    layout = style["layouts"][layout_name]
    reference_paths = [skill_root / "references/style-anchor.png"]
    reference_roles = ["Image 1: permanent style and default-layout master; its case-specific words are not current content."]
    if layout["extra_reference"]:
        reference_paths.append(skill_root / layout["extra_reference"])
        reference_roles.append(f"Image {len(reference_paths)}: selected {layout_name} layout reference; typography still follows the permanent master.")
    for logo in content.get("logo_references", []):
        logo_path = Path(logo["file"])
        if not logo_path.is_absolute():
            logo_path = skill_root / logo_path
        reference_paths.append(logo_path)
        reference_roles.append(f"Image {len(reference_paths)}: actual {logo['name']} logo; use only at matching content nodes.")
    for reference_path in reference_paths:
        if not reference_path.is_file():
            raise FileNotFoundError(reference_path)
    for relative_path, expected_hash in style["reference_sha256"].items():
        locked_path = skill_root / relative_path
        if not locked_path.is_file():
            raise FileNotFoundError(locked_path)
        actual_hash = hashlib.sha256(locked_path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(f"Locked reference changed: {relative_path}")

    prefix = (skill_root / "references/style-prefix.txt").read_text(encoding="utf-8")
    content_only = {key: value for key, value in content.items() if key != "logo_references"}
    prompt_sections = [
        prefix.strip(),
        f"STYLE VERSION: {style['version']}",
        "FIXED PALETTE: " + json.dumps(style["palette"], ensure_ascii=False),
        "SURFACE TIERS: " + json.dumps(style.get("surface_tiers", {}), ensure_ascii=False),
        "FIXED TYPE HIERARCHY: " + json.dumps(style["typography"], ensure_ascii=False),
        "FIXED SPACING: " + json.dumps(style.get("spacing", {}), ensure_ascii=False),
        "CONNECTOR LINE CRAFT: " + json.dumps(style.get("connection_line_craft", {}), ensure_ascii=False),
        "COLOR WEIGHT RULE: " + json.dumps(style.get("visual_quote_weights", {}), ensure_ascii=False),
        f"SELECTED LAYOUT: {layout_name}\n{layout['instructions']}",
        "REFERENCE ROLES:\n" + "\n".join(reference_roles),
        "CURRENT CONTENT PLAN (render strings accurately; graph IDs are only instructions):\n"
        + json.dumps(content_only, ensure_ascii=False, indent=2),
    ]
    return {
        "prompt": "\n\n".join(prompt_sections),
        "reference_images": [reference_path.resolve().as_posix() for reference_path in reference_paths],
        "model": style["model"],
        "size": style["size"],
        "quality": style["quality"],
        "n": 1,
        "path": image_path.resolve().as_posix(),
        "total_chars": total_chars,
        "warnings": warnings,
        "verification_checklist": render_items,
    }


def main():
    parser = argparse.ArgumentParser(description="Prepare a locked-style Magpie request without calling an API")
    parser.add_argument("--content", type=Path, required=True)
    parser.add_argument("--layout", choices=("editorial", "chapters", "lanes"), default="editorial")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--image-path", type=Path, required=True)
    arguments = parser.parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    request = build_request(skill_root, read_json(arguments.content), arguments.layout, arguments.image_path)
    arguments.out.parent.mkdir(parents=True, exist_ok=True)
    arguments.out.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    prompt_hash = hashlib.sha256(request["prompt"].encode("utf-8")).hexdigest()
    print(json.dumps({
        "request": arguments.out.resolve().as_posix(),
        "prompt_sha256": prompt_hash,
        "reference_count": len(request["reference_images"]),
        "total_chars": request["total_chars"],
        "warnings": request["warnings"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
