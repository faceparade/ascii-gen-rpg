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


def test_layout_spec_documents_locked_segment_widths() -> None:
    from six_room_scene import SixRoomLayoutSpec

    layout = SixRoomLayoutSpec()
    assert layout.room_width == 34
    assert layout.connector_width == 23
    assert layout.room_count == 3
    assert layout.segment_widths == (34, 23, 34, 23, 34)
    assert layout.row_width == 148
    print("PASS six-room layout spec locked widths")


def test_striped_region_composer_rejects_mismatched_heights() -> None:
    from six_room_scene import assemble_striped_region

    try:
        assemble_striped_region((("aa", "bb"), ("cc",)))
    except ValueError as exc:
        assert "strip heights must match" in str(exc)
    else:
        raise AssertionError("mismatched strip heights should fail")
    print("PASS six-room striped region rejects height drift")


def test_validate_region_widths_rejects_width_drift() -> None:
    from six_room_scene import validate_region_widths

    strips = (("aa", "bb"), ("ccc", "ddd"))
    try:
        validate_region_widths(strips, (2, 2))
    except ValueError as exc:
        message = str(exc)
        assert "strip 2 expected width 2" in message
        assert "got [3]" in message
    else:
        raise AssertionError("strip width drift should fail")
    print("PASS six-room strip width validation rejects drift")


def test_scene_regions_cover_locked_line_spans() -> None:
    from six_room_scene import scene_regions

    regions = scene_regions()
    assert [(region.name, region.start_line, region.end_line) for region in regions] == [
        ("top", 1, 4),
        ("upper_band", 5, 13),
        ("mid_connector", 14, 17),
        ("middle_seam", 18, 19),
        ("lower_connector", 20, 22),
        ("lower_band", 23, 29),
    ]
    assert [row for region in regions for row in region.rows] == load_scene_lines()
    print("PASS six-room scene regions cover locked spans")


def test_six_room_placements_match_locked_strip_boundaries() -> None:
    from six_room_scene import six_room_placements

    placements = six_room_placements()
    assert [(room.room_id, room.x, room.y, room.width, room.height) for room in placements] == [
        ("upper_left", 0, 4, 34, 9),
        ("upper_middle", 57, 4, 34, 9),
        ("upper_right", 114, 4, 34, 9),
        ("lower_left", 0, 17, 34, 12),
        ("lower_middle", 57, 17, 34, 12),
        ("lower_right", 114, 17, 34, 12),
    ]
    print("PASS six-room placements match locked strip boundaries")


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
    test_layout_spec_documents_locked_segment_widths()
    test_striped_region_composer_rejects_mismatched_heights()
    test_validate_region_widths_rejects_width_drift()
    test_scene_regions_cover_locked_line_spans()
    test_six_room_placements_match_locked_strip_boundaries()
    test_middle_seam_assembles_from_named_fragments()
    test_lower_band_assembles_from_named_strips()
    test_upper_band_assembles_from_named_strips()
    test_full_scene_assembles_from_named_regions()
    print("ALL six-room scene generator tests passed")


if __name__ == "__main__":
    main()
