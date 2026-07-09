#!/usr/bin/env python3
"""Tests for six-room scene generator assembly."""
from __future__ import annotations

from scene_alignment import load_scene_lines
from six_room_scene import (
    assemble_lower_band_rows,
    assemble_middle_seam_rows,
    assemble_six_room_scene_rows,
    assemble_upper_band_rows,
    build_six_room_scene_graph,
    format_scene_cell_info,
    main as six_room_scene_main,
    render_six_room_scene_graph,
    scene_bounds,
    scene_cell_info,
    scene_region_rects,
    scene_regions_at,
    scene_room_rects,
    scene_rooms_at,
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


def test_six_room_scene_graph_lives_in_scene_module() -> None:
    graph = build_six_room_scene_graph()
    assert [(room.room_id, room.x, room.y, room.width, room.height) for room in graph.rooms] == [
        ("upper_left", 0, 4, 34, 9),
        ("upper_middle", 57, 4, 34, 9),
        ("upper_right", 114, 4, 34, 9),
        ("lower_left", 0, 17, 34, 12),
        ("lower_middle", 57, 17, 34, 12),
        ("lower_right", 114, 17, 34, 12),
    ]
    assert [(c.from_room, c.to_room, c.kind, c.region_name) for c in graph.connections] == [
        ("upper_left", "upper_middle", "horizontal", "upper_band"),
        ("upper_middle", "upper_right", "horizontal", "upper_band"),
        ("upper_left", "lower_left", "vertical", "mid_connector"),
        ("upper_middle", "lower_middle", "vertical", "mid_connector"),
        ("upper_right", "lower_right", "vertical", "mid_connector"),
        ("lower_left", "lower_middle", "horizontal", "lower_band"),
        ("lower_middle", "lower_right", "horizontal", "lower_band"),
    ]
    assert render_six_room_scene_graph(graph) == load_scene_lines()
    print("PASS six-room scene graph lives in scene module")

def test_scene_rects_expose_review_coordinates() -> None:
    region_rects = scene_region_rects()
    room_rects = scene_room_rects()
    assert [(rect.name, rect.x, rect.y, rect.w, rect.h) for rect in region_rects] == [
        ("top", 0, 0, 148, 4),
        ("upper_band", 0, 4, 148, 9),
        ("mid_connector", 0, 13, 149, 4),
        ("middle_seam", 0, 17, 149, 2),
        ("lower_connector", 0, 19, 148, 3),
        ("lower_band", 0, 22, 148, 7),
    ]
    assert [(rect.name, rect.x, rect.y, rect.w, rect.h) for rect in room_rects] == [
        ("upper_left", 0, 4, 34, 9),
        ("upper_middle", 57, 4, 34, 9),
        ("upper_right", 114, 4, 34, 9),
        ("lower_left", 0, 17, 34, 12),
        ("lower_middle", 57, 17, 34, 12),
        ("lower_right", 114, 17, 34, 12),
    ]
    print("PASS six-room review rect coordinates")


def test_scene_coordinate_lookup_reports_region_room_and_glyph() -> None:
    assert scene_bounds() == (149, 29)
    assert scene_regions_at(0, 4) == ("upper_band",)
    assert scene_rooms_at(0, 4) == ("upper_left",)
    assert scene_rooms_at(40, 4) == ()
    assert scene_regions_at(40, 4) == ("upper_band",)
    assert scene_regions_at(57, 17) == ("middle_seam",)
    assert scene_rooms_at(57, 17) == ("lower_middle",)
    upper_left_cell = scene_cell_info(0, 4)
    assert upper_left_cell.char == "|"
    assert upper_left_cell.regions == ("upper_band",)
    assert upper_left_cell.rooms == ("upper_left",)
    assert format_scene_cell_info(upper_left_cell) == "L04 C000 char=| regions=upper_band rooms=upper_left"
    assert scene_cell_info(148, 0).char is None
    print("PASS six-room coordinate lookup metadata")


def test_six_room_scene_cli_generates_artifacts_and_cell_report() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from pathlib import Path
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temp:
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = six_room_scene_main(["--output-dir", temp, "--cell", "0,4"])
        output = stdout.getvalue()
        assert exit_code == 0
        assert "six-room scene bounds: width=149 height=29" in output
        assert "L04 C000 char=| regions=upper_band rooms=upper_left" in output
        for name in (
            "six_room_scene_generated.txt",
            "six_room_scene_generated_annotated.txt",
            "six_room_scene_generated.html",
        ):
            assert (Path(temp) / name).exists(), name
    print("PASS six-room scene CLI artifact generation")


def test_write_six_room_scene_artifacts(tmp_dir: str | None = None) -> None:
    from pathlib import Path
    from tempfile import TemporaryDirectory

    from six_room_scene import assemble_six_room_scene_rows, write_six_room_scene_artifacts

    with TemporaryDirectory() as temp:
        written = write_six_room_scene_artifacts(Path(temp))
        names = [path.name for path in written]
        assert names == [
            "six_room_scene_generated.txt",
            "six_room_scene_generated_annotated.txt",
            "six_room_scene_generated.html",
        ]
        for path in written:
            assert path.exists(), path
        assert written[0].read_text(encoding="utf-8").splitlines() == assemble_six_room_scene_rows()
        annotated = written[1].read_text(encoding="utf-8")
        html = written[2].read_text(encoding="utf-8")
        assert "upper_left" in annotated
        assert "upper_left" in html
        assert "L04-L12" in annotated
        assert "data-x=\"0\" data-y=\"0\"" in html
        assert 'data-regions="upper_band,upper_left"' in html
        assert "regions=${regions}" in html
    print("PASS six-room scene artifact writer")


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
    test_six_room_scene_graph_lives_in_scene_module()
    test_scene_rects_expose_review_coordinates()
    test_scene_coordinate_lookup_reports_region_room_and_glyph()
    test_six_room_scene_cli_generates_artifacts_and_cell_report()
    test_write_six_room_scene_artifacts()
    test_middle_seam_assembles_from_named_fragments()
    test_lower_band_assembles_from_named_strips()
    test_upper_band_assembles_from_named_strips()
    test_full_scene_assembles_from_named_regions()
    print("ALL six-room scene generator tests passed")


if __name__ == "__main__":
    main()
