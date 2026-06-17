"""
GameKee NIKKE Spine Live2D demo generator.

This package fetches live2d asset metadata from GameKee's content API,
downloads the Spine runtime and character assets, and generates a standalone
HTML demo page that supports manual interaction and pose switching.

Example::

    from gamekee_nikke_live2d import build_demo
    build_demo(char_id=164728, output_dir="demo_anker")

Command line::

    python -m gamekee_nikke_live2d 164728
    cd demo && python -m http.server 8766
"""

from .api import fetch_content, get_character_assets, get_character_skins
from .cli import build_demo, main
from .downloader import download_assets, download_file, download_runtime
from .html_generator import generate_html
from .parser import (
    base_name_from_url,
    extract_live2d_entries,
    guess_pose_type,
    normalize_url,
    unique_entries_by_pose,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "base_name_from_url",
    "build_demo",
    "download_assets",
    "download_file",
    "download_runtime",
    "extract_live2d_entries",
    "fetch_content",
    "generate_html",
    "get_character_assets",
    "get_character_skins",
    "guess_pose_type",
    "main",
    "normalize_url",
    "unique_entries_by_pose",
]
