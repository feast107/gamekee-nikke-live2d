"""
Fetch and process GameKee content API.
"""

import json
import ssl
import urllib.request
from typing import Any, Dict

from .parser import extract_live2d_entries, unique_entries_by_pose


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

    Args:
        char_id: GameKee character ID.

    Returns:
        Mapping from pose name to entry metadata.
    """
    data = fetch_content(char_id)
    entries = extract_live2d_entries(data)
    return unique_entries_by_pose(entries)
