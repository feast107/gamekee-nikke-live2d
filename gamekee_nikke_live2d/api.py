"""
Fetch and process GameKee content API.
"""

import json
import ssl
import urllib.request
from typing import Any, Dict, List

from .parser import extract_live2d_entries_by_style, unique_entries_by_pose


API_BASE = "https://api-cdn.gamekee.com/wiki2.0/pro/1253/content/{char_id}.json"


def fetch_content(char_id: int | str) -> Dict[str, Any]:
    """
    Fetch character content from GameKee API.

    Args:
        char_id: GameKee character ID.

    Returns:
        Parsed JSON response.
    """
    url = API_BASE.format(char_id=char_id)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.gamekee.com/",
        },
    )
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        raw = resp.read()
    return json.loads(raw)


def get_character_assets(char_id: int | str) -> Dict[str, Dict[str, Any]]:
    """
    Get unique live2d asset entries grouped by pose for a character.

    Uses the first style only. For multi-skin characters, see
    `get_character_skins`.

    Args:
        char_id: GameKee character ID.

    Returns:
        Mapping from pose name to entry metadata.
    """
    skins = get_character_skins(char_id)
    return skins[0] if skins else {}


def get_character_skins(char_id: int | str) -> List[Dict[str, Dict[str, Any]]]:
    """
    Get live2d asset entries grouped by pose for each style/skin.

    Args:
        char_id: GameKee character ID.

    Returns:
        List of mappings from pose name to entry metadata, one per skin.
    """
    data = fetch_content(char_id)
    return extract_live2d_entries_by_style(data)
