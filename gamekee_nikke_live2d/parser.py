"""
Parse live2d asset entries from GameKee content API response.
"""

import json
from pathlib import Path
from typing import Any, Dict, List


def extract_live2d_entries(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract all live2d asset entries from content API response.

    Args:
        data: Parsed JSON from GameKee content API.

    Returns:
        List of live2d entries, each containing atlas/skel/image/position etc.
    """
    entries: List[Dict[str, Any]] = []
    try:
        content = json.loads(data.get("content", "{}"))
        for style_data in content.get("styleData", []):
            for row in style_data.get("data", []):
                for cell in row:
                    value = cell.get("value")
                    if not isinstance(value, dict):
                        continue
                    if any(k in value for k in ("skel", "atlas", "live2dKey")):
                        entries.append(value)
    except Exception as exc:
        raise ValueError(f"Failed to parse content: {exc}") from exc
    return entries


def guess_pose_type(entry: Dict[str, Any]) -> str:
    """
    Guess pose type (full / aim / cover) from animation name or skel URL.

    Args:
        entry: A live2d asset entry.

    Returns:
        One of "full", "aim", "cover".
    """
    animation = entry.get("animation", "")
    anim_lower = animation.lower()

    if "aim" in anim_lower:
        return "aim"
    if "cover" in anim_lower:
        return "cover"

    skel = entry.get("skel", "")
    lower = skel.lower()

    if "_aim_" in lower or lower.endswith("_aim.skel"):
        return "aim"
    if "_cover_" in lower or lower.endswith("_cover.skel"):
        return "cover"
    if "_full_" in lower or lower.endswith("_full.skel"):
        return "full"

    # Fallback keywords
    if "aim" in lower:
        return "aim"
    if "cover" in lower:
        return "cover"
    return "full"


def unique_entries_by_pose(entries: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Deduplicate live2d entries by pose, keeping the first occurrence of each pose.

    For entries whose pose cannot be inferred from filename or animation name,
    assign poses in order: full -> aim -> cover. GameKee tables typically list
    poses in this order.

    Args:
        entries: List of live2d entries.

    Returns:
        Mapping from pose name to entry.
    """
    result: Dict[str, Dict[str, Any]] = {}
    fallback_poses = ["full", "aim", "cover"]
    fallback_index = 0

    for entry in entries:
        pose = guess_pose_type(entry)
        # If pose already taken (e.g. multiple entries guessed as full),
        # use the next available fallback pose in order.
        if pose in result:
            while fallback_index < len(fallback_poses) and fallback_poses[fallback_index] in result:
                fallback_index += 1
            if fallback_index < len(fallback_poses):
                pose = fallback_poses[fallback_index]
                fallback_index += 1
            else:
                continue
        result[pose] = entry
    return result


def normalize_url(url: str) -> str:
    """Convert protocol-relative URL to https://."""
    if url.startswith("//"):
        return f"https:{url}"
    return url


def base_name_from_url(url: str) -> str:
    """Return the file stem from a URL, e.g. c355_00."""
    return Path(normalize_url(url)).stem
