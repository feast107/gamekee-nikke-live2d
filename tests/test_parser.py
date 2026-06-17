"""Tests for parser module."""

import pytest

from gamekee_nikke_live2d.parser import (
    base_name_from_url,
    extract_live2d_entries,
    guess_pose_type,
    normalize_url,
    unique_entries_by_pose,
)


def test_extract_live2d_entries():
    data = {
        "content": '{"styleData": [{"data": [[{"value": {"skel": "a.skel"}}]]}]}'
    }
    entries = extract_live2d_entries(data)
    assert len(entries) == 1
    assert entries[0]["skel"] == "a.skel"


def test_guess_pose_type():
    assert guess_pose_type({"skel": "c355_aim_00.skel"}) == "aim"
    assert guess_pose_type({"skel": "c355_cover_00.skel"}) == "cover"
    assert guess_pose_type({"skel": "c355_00.skel"}) == "full"


def test_unique_entries_by_pose():
    entries = [
        {"skel": "c355_00.skel"},
        {"skel": "c355_aim_00.skel"},
        {"skel": "c355_cover_00.skel"},
        {"skel": "c355_00.skel"},
    ]
    result = unique_entries_by_pose(entries)
    assert set(result.keys()) == {"full", "aim", "cover"}
    assert result["full"]["skel"] == "c355_00.skel"


def test_normalize_url():
    assert normalize_url("//cdn.example.com/a.png") == "https://cdn.example.com/a.png"
    assert normalize_url("https://cdn.example.com/a.png") == "https://cdn.example.com/a.png"


def test_base_name_from_url():
    assert base_name_from_url("https://cdn.example.com/c355_00.skel") == "c355_00"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
