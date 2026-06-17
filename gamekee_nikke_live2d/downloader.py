"""
Download live2d assets and Spine runtime files.
"""

import ssl
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

from .parser import normalize_url


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.gamekee.com/",
}

SPINE_RUNTIME_FILES = {
    "spine-player-4.1.54.js": "https://cdnstatic.gamekee.com/wiki/spa/apps/web/client/dist/static/spine-player-4.1.54.js?t=10002",
    "spine-player-4.1.54.css": "https://cdnstatic.gamekee.com/wiki/spa/apps/web/client/dist/static/spine-player-4.1.54.css?t=10002",
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


def download_runtime(output_dir: Path, overwrite: bool = False) -> List[str]:
    """
    Download Spine runtime files.

    Returns:
        List of downloaded filenames.
    """
    downloaded = []
    for name, url in SPINE_RUNTIME_FILES.items():
        if download_file(url, output_dir / name, overwrite):
            downloaded.append(name)
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

        assets[pose] = files

    return assets
