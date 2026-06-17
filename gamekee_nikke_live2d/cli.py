"""
Command-line interface for gamekee_nikke_live2d.
"""

import argparse
import sys
from pathlib import Path

from .api import get_character_assets
from .downloader import download_assets, download_runtime
from .html_generator import generate_html


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

    pose_entries = get_character_assets(char_id)
    if not pose_entries:
        raise RuntimeError(f"No live2d assets found for character {char_id}")

    download_runtime(output_dir)
    local_assets = download_assets(pose_entries, output_dir)

    character_data = {}
    for pose, files in local_assets.items():
        character_data[pose] = {
            "base": Path(files["skel"]).stem,
            "position": pose_entries[pose].get("position", {}),
        }

    generate_html(
        output_path=output_dir / "index.html",
        title=f"GameKee NIKKE Live2D - {char_id}",
        character_data=character_data,
        default_pose="full" if "full" in character_data else next(iter(character_data)),
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
        help="Output directory (default: demo_<char_id>)",
    )
    args = parser.parse_args(argv)

    output_dir = args.output if args.output else f"demo_{args.char_id}"
    demo_dir = build_demo(args.char_id, output_dir)
    print(f"Demo generated: {demo_dir}")
    print(f"Run: cd {demo_dir} && python -m http.server 8766")
    print("Then open http://localhost:8766")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
