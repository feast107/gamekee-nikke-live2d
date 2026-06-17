"""
Download live2d assets and Spine runtime files.
"""

import re
import ssl
import struct
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Set

from .parser import normalize_url


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.gamekee.com/",
}

SPINE_RUNTIME_VERSIONS = {
    "4.0": {
        "js": "https://unpkg.com/@esotericsoftware/spine-player@4.0/dist/iife/spine-player.js",
        "css": "https://unpkg.com/@esotericsoftware/spine-player@4.0/dist/spine-player.css",
        "var": "spine.SpinePlayer",
    },
    "4.1": {
        "js": "https://cdnstatic.gamekee.com/wiki/spa/apps/web/client/dist/static/spine-player-4.1.54.js?t=10002",
        "css": "https://cdnstatic.gamekee.com/wiki/spa/apps/web/client/dist/static/spine-player-4.1.54.css?t=10002",
        "var": "spine_4_1_54.SpinePlayer",
    },
}


def download_file(url: str, dest: Path, overwrite: bool = False) -> bool:
    """
    Download a single file.

    Args:
        url: Remote URL.
        dest: Local destination path.
        overwrite: Whether to overwrite existing file.

    Returns:
        True if downloaded successfully, False otherwise.
    """
    if dest.exists() and not overwrite:
        return True

    url = normalize_url(url)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            dest.write_bytes(resp.read())
        return True
    except Exception:
        return False


def detect_skel_version(skel_path: Path) -> str:
    """
    Detect Spine runtime version from binary skel file.

    Returns major.minor version string, e.g. "4.0" or "4.1".
    Defaults to "4.1" if detection fails.
    """
    try:
        with open(skel_path, "rb") as f:
            f.read(8)  # skip signature/hash
            length = struct.unpack("B", f.read(1))[0]
            raw = f.read(length)
        version = raw.decode("utf-8", errors="ignore")[:10]
        match = re.match(r"(\d+\.\d+)", version)
        if match:
            return match.group(1)
    except Exception:
        pass
    return "4.1"


def download_runtime(output_dir: Path, versions: Set[str], overwrite: bool = False) -> Dict[str, Dict[str, str]]:
    """
    Download Spine runtime files for the requested versions.

    Returns:
        Mapping from version to runtime metadata.
    """
    downloaded: Dict[str, Dict[str, str]] = {}
    for version in versions:
        if version not in SPINE_RUNTIME_VERSIONS:
            version = "4.1"
        meta = SPINE_RUNTIME_VERSIONS[version]
        js_name = f"spine-player-{version}.js"
        css_name = f"spine-player-{version}.css"
        download_file(meta["js"], output_dir / js_name, overwrite)
        download_file(meta["css"], output_dir / css_name, overwrite)
        downloaded[version] = {
            "js": js_name,
            "css": css_name,
            "var": meta["var"],
        }
    return downloaded


def download_assets(
    pose_entries: Dict[str, Dict[str, Any]],
    output_dir: Path,
    overwrite: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """
    Download live2d assets for each pose.

    Args:
        pose_entries: Mapping from pose to live2d entry.
        output_dir: Directory to save files.
        overwrite: Whether to overwrite existing files.

    Returns:
        Mapping from pose to local asset metadata.
    """
    from .parser import base_name_from_url, normalize_url

    assets: Dict[str, Dict[str, Any]] = {}
    for pose, entry in pose_entries.items():
        skel_url = normalize_url(entry.get("skel", ""))
        atlas_url = normalize_url(entry.get("atlas", ""))
        image_urls = [normalize_url(u.strip()) for u in entry.get("image", "").split(",") if u.strip()]

        if not skel_url:
            continue

        base = base_name_from_url(skel_url)
        files = {
            "skel": f"{base}.skel",
            "atlas": f"{base}.atlas",
            "pngs": [],
        }

        download_file(skel_url, output_dir / files["skel"], overwrite)
        download_file(atlas_url, output_dir / files["atlas"], overwrite)

        for image_url in image_urls:
            image_name = base_name_from_url(image_url)
            if not image_name.endswith(".png"):
                image_name += ".png"
            download_file(image_url, output_dir / image_name, overwrite)
            files["pngs"].append(image_name)

        files["spine_version"] = detect_skel_version(output_dir / files["skel"])
        assets[pose] = files

    return assets
