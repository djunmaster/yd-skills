import argparse
import hashlib
import json
from pathlib import Path


def read_json(file_path):
    return json.loads(file_path.read_text(encoding="utf-8-sig"))


def validate_content(content, max_nodes):
    required_fields = ("headline", "summary", "takeaway", "sections", "footer")
    for field_name in required_fields:
        if not content.get(field_name):
            raise ValueError(f"Missing content field: {field_name}")
    if "connections" not in content:
        raise ValueError("Missing content field: connections")
    nodes = [node for section in content["sections"] for node in section["nodes"]]
    node_ids = [node["id"] for node in nodes]
    if not nodes or len(nodes) > max_nodes:
        raise ValueError(f"Use 1-{max_nodes} nodes; split denser material into multiple images")
    if len(set(node_ids)) != len(node_ids):
        raise ValueError("Node IDs must be unique")
    for node in nodes:
        if not node.get("title") or "caption" not in node:
            raise ValueError(f"Node requires a title and caption: {node['id']}")
    for connection in content["connections"]:
        for endpoint in ("from", "to"):
            if connection[endpoint] not in node_ids:
                raise ValueError(f"Unknown connection endpoint: {connection[endpoint]}")


def build_request(skill_root, content, layout_name, image_path):
    style = read_json(skill_root / "references/style-lock.json")
    validate_content(content, style["max_nodes"])
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
        "FIXED TYPE HIERARCHY: " + json.dumps(style["typography"], ensure_ascii=False),
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
    print(json.dumps({"request": arguments.out.resolve().as_posix(), "prompt_sha256": prompt_hash, "reference_count": len(request["reference_images"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
