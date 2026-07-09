#!/usr/bin/env python3
"""Tests for six-room scene generator assembly."""
from __future__ import annotations

from scene_alignment import load_scene_lines
from six_room_scene import (
    assemble_lower_band_rows,
    assemble_middle_seam_rows,
    assemble_six_room_scene_rows,
    assemble_upper_band_rows,
)


def test_middle_seam_assembles_from_named_fragments() -> None:
    lines = load_scene_lines()
    assert assemble_middle_seam_rows() == lines[18 - 1:19]
    print("PASS six-room generator middle seam")


def test_lower_band_assembles_from_named_strips() -> None:
    lines = load_scene_lines()
    assert assemble_lower_band_rows() == lines[23 - 1:29]
    print("PASS six-room generator lower band")


def test_upper_band_assembles_from_named_strips() -> None:
    lines = load_scene_lines()
    assert assemble_upper_band_rows() == lines[5 - 1:13]
    print("PASS six-room generator upper band")


def test_full_scene_assembles_from_named_regions() -> None:
    assert assemble_six_room_scene_rows() == load_scene_lines()
    print("PASS six-room generator full scene")


def main() -> None:
    test_middle_seam_assembles_from_named_fragments()
    test_lower_band_assembles_from_named_strips()
    test_upper_band_assembles_from_named_strips()
    test_full_scene_assembles_from_named_regions()
    print("ALL six-room scene generator tests passed")


if __name__ == "__main__":
    main()
