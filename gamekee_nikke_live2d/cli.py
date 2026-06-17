"""
Command-line interface for gamekee_nikke_live2d.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from .api import fetch_content, get_character_skins
from .downloader import download_assets, download_runtime
from .html_generator import generate_html


def extract_character_name(data: dict) -> str:
    """Extract character display name from content API response."""
    try:
        content = json.loads(data.get("content", "{}"))
        base_data = content.get("baseData", [])
        if base_data and len(base_data[0]) > 1:
            value = base_data[0][1].get("value", "")
            if value:
                return value
    except Exception:
        pass
    return ""


def sanitize_name(name: str) -> str:
    """Remove characters that are not safe for directory names."""
    return re.sub(r"[^\w\u4e00-\u9fff-]+", "_", name).strip("_") or "unknown"


def build_demo(char_id: int | str, output_dir: str | Path) -> Path:
    """
    Build a standalone demo for a GameKee character.

    Args:
        char_id: GameKee character ID.
        output_dir: Directory to create the demo in.

    Returns:
        Path to the generated demo directory.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_data = fetch_content(char_id)
    char_name = extract_character_name(raw_data)

    skins = get_character_skins(raw_data)
    if not skins:
        raise RuntimeError(f"No live2d assets found for character {char_id}")

    character_data = {"skins": []}
    required_versions = set()

    for skin_index, pose_entries in enumerate(skins):
        local_assets = download_assets(pose_entries, output_dir)
        skin_data = {}
        for pose, files in local_assets.items():
            skin_data[pose] = {
                "base": Path(files["skel"]).stem,
                "position": pose_entries[pose].get("position", {}),
                "spine_version": files.get("spine_version", "4.1"),
            }
            required_versions.add(files.get("spine_version", "4.1"))
        character_data["skins"].append(skin_data)

    runtime_map = download_runtime(output_dir, required_versions)

    default_skin = 0
    default_pose = "full" if "full" in character_data["skins"][default_skin] else next(iter(character_data["skins"][default_skin]))

    generate_html(
        output_path=output_dir / "index.html",
        title=f"GameKee NIKKE Live2D - {char_id} {char_name}".strip(),
        character_data=character_data,
        runtime_map=runtime_map,
        default_skin=default_skin,
        default_pose=default_pose,
    )

    return output_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gamekee-nikke-live2d",
        description="Generate standalone GameKee NIKKE Spine live2d demo pages.",
    )
    parser.add_argument("char_id", help="GameKee character ID")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output directory (default: demo_<char_id>_<char_name>)",
    )
    args = parser.parse_args(argv)

    if args.output:
        output_dir = args.output
        demo_dir = build_demo(args.char_id, output_dir)
    else:
        # Need name before building to form directory name.
        raw_data = fetch_content(args.char_id)
        char_name = sanitize_name(extract_character_name(raw_data))
        output_dir = f"demo_{args.char_id}_{char_name}"
        demo_dir = build_demo(args.char_id, output_dir)

    print(f"Demo generated: {demo_dir}")
    print(f"Run: cd {demo_dir} && python -m http.server 8766")
    print("Then open http://localhost:8766")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
