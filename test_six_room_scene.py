#!/usr/bin/env python3
"""Tests for six-room scene generator assembly."""
from __future__ import annotations

from scene_alignment import load_scene_lines
from six_room_scene import (
    SceneConnection,
    SceneRoomPlacement,
    assemble_lower_band_rows,
    assemble_middle_seam_rows,
    assemble_six_room_scene_rows,
    assemble_upper_band_rows,
    build_six_room_scene_graph,
    format_scene_cell_info,
    format_scene_connection_summary,
    format_scene_room_info,
    format_scene_room_summary,
    main as six_room_scene_main,
    render_six_room_scene_graph,
    scene_bounds,
    scene_cell_info,
    scene_connections_for_room,
    scene_region_rects,
    scene_regions_at,
    scene_regions_for_room,
    scene_room_rects,
    scene_rooms_at,
    six_room_scene_graph_data,
    six_room_scene_graph_from_data,
    validate_six_room_scene_graph,
    validate_six_room_scene_graph_data,
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


def test_six_room_graph_connection_lookup_lists_room_adjacencies() -> None:
    graph = build_six_room_scene_graph()
    assert [c.to_room for c in scene_connections_for_room(graph, "upper_middle")] == [
        "upper_left",
        "upper_right",
        "lower_middle",
    ]
    assert [c.kind for c in scene_connections_for_room(graph, "upper_middle")] == [
        "horizontal",
        "horizontal",
        "vertical",
    ]
    assert scene_connections_for_room(graph, "missing_room") == ()
    print("PASS six-room graph connection lookup")


def test_validate_six_room_scene_graph_reports_broken_references() -> None:
    from dataclasses import replace

    graph = build_six_room_scene_graph()
    assert validate_six_room_scene_graph(graph) == ()
    broken_graph = replace(
        graph,
        connections=(SceneConnection("upper_left", "missing_room", "horizontal", "missing_region"),),
    )
    assert validate_six_room_scene_graph(broken_graph) == (
        "connection upper_left->missing_room references unknown to_room missing_room",
        "connection upper_left->missing_room references unknown region missing_region",
    )
    print("PASS six-room graph validation reports broken references")


def test_six_room_scene_graph_data_exposes_editor_ready_connection_anchors() -> None:
    graph_data = six_room_scene_graph_data(build_six_room_scene_graph())
    assert graph_data["schema_version"] == 1
    upper_left_to_middle = graph_data["connections"][0]
    assert upper_left_to_middle["from_center"] == {"x": 16, "y": 8}
    assert upper_left_to_middle["to_center"] == {"x": 73, "y": 8}
    assert upper_left_to_middle["midpoint"] == {"x": 44, "y": 8}
    assert upper_left_to_middle["rooms"] == ["upper_left", "upper_middle"]
    assert graph_data["rooms"][0]["center"] == {"x": 16, "y": 8}
    print("PASS six-room graph JSON exposes connection anchors")


def test_validate_six_room_scene_graph_data_checks_round_trip_json() -> None:
    graph_data = six_room_scene_graph_data(build_six_room_scene_graph())
    assert validate_six_room_scene_graph_data(graph_data) == ()
    broken_data = dict(graph_data)
    broken_data["connections"] = [
        {"from_room": "upper_left", "to_room": "missing_room", "kind": "horizontal", "region_name": "missing_region"}
    ]
    assert validate_six_room_scene_graph_data(broken_data) == (
        "connection upper_left->missing_room references unknown to_room missing_room",
        "connection upper_left->missing_room references unknown region missing_region",
    )
    broken_room_data = dict(graph_data)
    broken_room_data["rooms"] = [dict(graph_data["rooms"][0], width=0)]
    broken_room_data["connections"] = []
    assert "room upper_left width must be positive" in validate_six_room_scene_graph_data(broken_room_data)
    print("PASS six-room graph JSON validation")


def test_six_room_scene_graph_from_data_imports_edited_room_and_connection_metadata() -> None:
    graph_data = six_room_scene_graph_data(build_six_room_scene_graph())
    graph_data["rooms"][1]["room_id"] = "upper_center"
    graph_data["rooms"][1]["x"] = 60
    graph_data["connections"][0]["to_room"] = "upper_center"
    graph_data["connections"][1]["from_room"] = "upper_center"
    graph_data["connections"][3]["from_room"] = "upper_center"
    graph = six_room_scene_graph_from_data(graph_data)
    assert graph.rooms[1] == SceneRoomPlacement("upper_center", 60, 4, 34, 9)
    assert graph.connections[0] == SceneConnection("upper_left", "upper_center", "horizontal", "upper_band")
    normalized = six_room_scene_graph_data(graph)
    assert normalized["rooms"][1]["center"] == {"x": 76, "y": 8}
    assert normalized["connections"][0]["to_center"] == {"x": 76, "y": 8}
    assert render_six_room_scene_graph(graph) == load_scene_lines()
    print("PASS six-room graph JSON importer")


def test_format_scene_room_info_reports_bounds_and_connections() -> None:
    graph = build_six_room_scene_graph()
    assert scene_regions_for_room(graph, "lower_middle") == (
        "middle_seam",
        "lower_connector",
        "lower_band",
    )
    assert format_scene_room_info(graph, "upper_middle") == (
        "room upper_middle bounds=x57..90 y4..12 size=34x9 regions=upper_band "
        "connections=upper_left(horizontal:upper_band),upper_right(horizontal:upper_band),"
        "lower_middle(vertical:mid_connector)"
    )
    assert format_scene_room_info(graph, "lower_middle") == (
        "room lower_middle bounds=x57..90 y17..28 size=34x12 "
        "regions=middle_seam,lower_connector,lower_band "
        "connections=upper_middle(vertical:mid_connector),lower_left(horizontal:lower_band),"
        "lower_right(horizontal:lower_band)"
    )
    assert format_scene_room_info(graph, "missing_room") == "room missing_room not found"
    print("PASS six-room room-info formatter")


def test_format_scene_room_summary_reports_compact_bounds() -> None:
    graph = build_six_room_scene_graph()
    assert [format_scene_room_summary(room) for room in graph.rooms] == [
        "upper_left x0..33 y4..12 size=34x9",
        "upper_middle x57..90 y4..12 size=34x9",
        "upper_right x114..147 y4..12 size=34x9",
        "lower_left x0..33 y17..28 size=34x12",
        "lower_middle x57..90 y17..28 size=34x12",
        "lower_right x114..147 y17..28 size=34x12",
    ]
    print("PASS six-room room summary formatter")


def test_format_scene_connection_summary_reports_edges() -> None:
    graph = build_six_room_scene_graph()
    assert [format_scene_connection_summary(connection) for connection in graph.connections] == [
        "upper_left -> upper_middle kind=horizontal region=upper_band",
        "upper_middle -> upper_right kind=horizontal region=upper_band",
        "upper_left -> lower_left kind=vertical region=mid_connector",
        "upper_middle -> lower_middle kind=vertical region=mid_connector",
        "upper_right -> lower_right kind=vertical region=mid_connector",
        "lower_left -> lower_middle kind=horizontal region=lower_band",
        "lower_middle -> lower_right kind=horizontal region=lower_band",
    ]
    print("PASS six-room connection summary formatter")

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


def test_graph_scoped_coordinate_lookup_uses_supplied_graph() -> None:
    from dataclasses import replace

    graph = build_six_room_scene_graph()
    shifted_graph = replace(
        graph,
        rooms=(SceneRoomPlacement("probe_room", 10, 4, 3, 2),),
    )
    assert scene_bounds(shifted_graph) == (149, 29)
    assert scene_rooms_at(0, 4, shifted_graph) == ()
    assert scene_rooms_at(10, 4, shifted_graph) == ("probe_room",)
    assert scene_cell_info(10, 4, shifted_graph).rooms == ("probe_room",)
    assert scene_cell_info(10, 4, shifted_graph).regions == ("upper_band",)
    print("PASS six-room graph-scoped coordinate lookup")


def test_six_room_scene_cli_generates_artifacts_and_cell_report() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from pathlib import Path
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temp:
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = six_room_scene_main(["--output-dir", temp, "--cell", "0,4", "--room", "upper_middle"])
        output = stdout.getvalue()
        assert exit_code == 0
        assert "six-room scene bounds: width=149 height=29" in output
        assert "L04 C000 char=| regions=upper_band rooms=upper_left" in output
        assert (
            "room upper_middle bounds=x57..90 y4..12 size=34x9 regions=upper_band "
            "connections=upper_left(horizontal:upper_band),upper_right(horizontal:upper_band),"
            "lower_middle(vertical:mid_connector)"
        ) in output
        for name in (
            "six_room_scene_generated.txt",
            "six_room_scene_generated_annotated.txt",
            "six_room_scene_generated.html",
        ):
            assert (Path(temp) / name).exists(), name
    print("PASS six-room scene CLI artifact generation")


def test_six_room_scene_cli_lists_rooms() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temp:
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = six_room_scene_main(["--output-dir", temp, "--list-rooms"])
        output = stdout.getvalue().splitlines()
        assert exit_code == 0
        assert "upper_left x0..33 y4..12 size=34x9" in output
        assert "upper_middle x57..90 y4..12 size=34x9" in output
        assert "upper_right x114..147 y4..12 size=34x9" in output
        assert "lower_left x0..33 y17..28 size=34x12" in output
        assert "lower_middle x57..90 y17..28 size=34x12" in output
        assert "lower_right x114..147 y17..28 size=34x12" in output
    print("PASS six-room scene CLI room listing")


def test_six_room_scene_cli_lists_connections() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temp:
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = six_room_scene_main(["--output-dir", temp, "--list-connections"])
        output = stdout.getvalue().splitlines()
        assert exit_code == 0
        assert "upper_left -> upper_middle kind=horizontal region=upper_band" in output
        assert "upper_middle -> upper_right kind=horizontal region=upper_band" in output
        assert "upper_left -> lower_left kind=vertical region=mid_connector" in output
        assert "upper_middle -> lower_middle kind=vertical region=mid_connector" in output
        assert "upper_right -> lower_right kind=vertical region=mid_connector" in output
        assert "lower_left -> lower_middle kind=horizontal region=lower_band" in output
        assert "lower_middle -> lower_right kind=horizontal region=lower_band" in output
    print("PASS six-room scene CLI connection listing")


def test_six_room_scene_cli_validates_graph() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temp:
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = six_room_scene_main(["--output-dir", temp, "--validate-graph"])
        output = stdout.getvalue().splitlines()
        assert exit_code == 0
        assert "graph validation: ok" in output
    print("PASS six-room scene CLI graph validation")


def test_six_room_scene_cli_prints_graph_json() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from tempfile import TemporaryDirectory
    import json

    with TemporaryDirectory() as temp:
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = six_room_scene_main(["--output-dir", temp, "--print-graph-json"])
        graph_data = json.loads(stdout.getvalue())
        assert exit_code == 0
        assert graph_data["schema_version"] == 1
        assert graph_data["bounds"] == {"width": 149, "height": 29}
        assert graph_data["rooms"][1]["room_id"] == "upper_middle"
        assert graph_data["connections"][0]["midpoint"] == {"x": 44, "y": 8}
    print("PASS six-room scene CLI graph JSON output")


def test_six_room_scene_cli_validates_loaded_graph_json() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from pathlib import Path
    from tempfile import TemporaryDirectory
    import json

    with TemporaryDirectory() as temp:
        graph_json = Path(temp) / "graph.json"
        graph_json.write_text(json.dumps(six_room_scene_graph_data(build_six_room_scene_graph())), encoding="utf-8")
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = six_room_scene_main(["--graph-json", str(graph_json), "--validate-graph"])
        output = stdout.getvalue().splitlines()
        assert exit_code == 0
        assert output == ["graph json validation: ok"]
    print("PASS six-room scene CLI loaded graph JSON validation")


def test_six_room_scene_cli_regenerates_artifacts_from_loaded_graph_json() -> None:
    from contextlib import redirect_stdout
    from io import StringIO
    from pathlib import Path
    from tempfile import TemporaryDirectory
    import json

    with TemporaryDirectory() as temp:
        temp_path = Path(temp)
        graph_data = six_room_scene_graph_data(build_six_room_scene_graph())
        graph_data["rooms"][1]["room_id"] = "upper_center"
        graph_data["connections"][0]["to_room"] = "upper_center"
        graph_data["connections"][1]["from_room"] = "upper_center"
        graph_data["connections"][3]["from_room"] = "upper_center"
        graph_json = temp_path / "edited_graph.json"
        graph_json.write_text(json.dumps(graph_data), encoding="utf-8")
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = six_room_scene_main(["--graph-json", str(graph_json), "--output-dir", temp, "--room", "upper_center"])
        output = stdout.getvalue()
        html = (temp_path / "six_room_scene_generated.html").read_text(encoding="utf-8")
        normalized_data = json.loads((temp_path / "six_room_scene_graph.json").read_text(encoding="utf-8"))
        assert exit_code == 0
        assert "loaded graph json:" in output
        assert "room upper_center bounds=x57..90 y4..12 size=34x9" in output
        assert "upper_center" in html
        assert normalized_data["rooms"][1]["room_id"] == "upper_center"
        assert normalized_data["connections"][0]["to_room"] == "upper_center"
    print("PASS six-room scene CLI graph JSON artifact regeneration")


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
            "six_room_scene_graph.json",
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
        assert (
            'data-connections="upper_left(horizontal:upper_band),'
            'upper_right(horizontal:upper_band),lower_middle(vertical:mid_connector)"'
        ) in html
        assert "connections=${connections}" in html
        assert "regions=${regions}" in html
        assert '<script type="application/json" id="scene-graph-data">' in html
        assert '<svg id="connection-overlay"' in html
        assert '<g id="connection-line-layer">' in html
        assert '<g id="room-box-layer">' in html
        assert '<line class="connection-line"' in html
        assert '<rect class="room-box" data-room-id="upper_left"' in html
        assert '<text class="room-label" data-room-id="upper_left"' in html
        assert 'data-connection-index="0"' in html
        assert '<button id="copy-graph-json"' in html
        assert '<button id="copy-selected-room-json"' in html
        assert '<button id="download-graph-json"' in html
        assert '<input id="load-graph-json-file" type="file"' in html
        assert '<button id="reset-graph-edits"' in html
        assert '<input id="toggle-room-boxes"' in html
        assert '<input id="toggle-connection-lines"' in html
        assert '<div id="graph-inspector"' in html
        assert "drawConnectionOverlay" in html
        assert "copyGraphJson" in html
        assert "downloadGraphJson" in html
        assert "loadGraphJsonFile" in html
        assert "loadGraphJsonData" in html
        assert "initGraphReview" in html
        assert "DOMContentLoaded" in html
        assert "six_room_scene_graph_edited.json" in html
        assert "text + '\\n'" in html
        assert "selectRoom(roomId)" in html
        assert "selectConnection(index)" in html
        assert "renderInspector" in html
        assert "applyRoomInspectorEdits" in html
        assert "applyConnectionInspectorEdits" in html
        assert "resetGraphEdits" in html
        assert "updateOverlayFromGraph" in html
        assert "sceneGraphData.rooms[index]" in html
        assert "box.dataset.roomId = room.room_id" in html
        assert "label.dataset.roomId = room.room_id" in html
        assert 'id=\"edit-room-id\"' in html
        assert 'id=\"edit-connection-from-room\"' in html
        assert 'id=\"apply-room-edits\"' in html
        assert 'id=\"apply-connection-edits\"' in html
        assert '<h2>Connections</h2>' in html
        assert ".connection-line { stroke:#f6cf63" in html
        assert ".room-box { fill:rgba(114,214,255,.08); stroke:#72d6ff" in html
        assert '<code>upper_left</code> → <code>upper_middle</code>' in html
        import json

        graph_data = json.loads(written[3].read_text(encoding="utf-8"))
        assert graph_data["bounds"] == {"width": 149, "height": 29}
        upper_middle_room = graph_data["rooms"][1]
        assert upper_middle_room["room_id"] == "upper_middle"
        assert upper_middle_room["x"] == 57
        assert upper_middle_room["y"] == 4
        assert upper_middle_room["width"] == 34
        assert upper_middle_room["height"] == 9
        assert upper_middle_room["center"] == {"x": 73, "y": 8}
        assert upper_middle_room["regions"] == ["upper_band"]
        assert upper_middle_room["connections"] == [
            {"to_room": "upper_left", "kind": "horizontal", "region_name": "upper_band"},
            {"to_room": "upper_right", "kind": "horizontal", "region_name": "upper_band"},
            {"to_room": "lower_middle", "kind": "vertical", "region_name": "mid_connector"},
        ]
        assert graph_data["connections"][0] | {
            "from_room": "upper_left",
            "to_room": "upper_middle",
            "kind": "horizontal",
            "region_name": "upper_band",
        } == graph_data["connections"][0]
    print("PASS six-room scene artifact writer")


def test_write_six_room_scene_artifacts_uses_supplied_graph_rects() -> None:
    from dataclasses import replace
    from pathlib import Path
    from tempfile import TemporaryDirectory

    from six_room_scene import write_six_room_scene_artifacts

    graph = replace(
        build_six_room_scene_graph(),
        rooms=(SceneRoomPlacement("probe_room", 10, 4, 3, 2),),
        connections=(),
    )
    with TemporaryDirectory() as temp:
        _, annotated_path, html_path, graph_json_path = write_six_room_scene_artifacts(Path(temp), graph)
        annotated = annotated_path.read_text(encoding="utf-8")
        html = html_path.read_text(encoding="utf-8")
        graph_json = graph_json_path.read_text(encoding="utf-8")
        assert "probe_room" in annotated
        assert "probe_room" in html
        assert "probe_room" in graph_json
        assert "upper_left" not in annotated
        assert "upper_left" not in html
    print("PASS six-room graph-scoped artifact writer")


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
    test_six_room_graph_connection_lookup_lists_room_adjacencies()
    test_validate_six_room_scene_graph_reports_broken_references()
    test_six_room_scene_graph_data_exposes_editor_ready_connection_anchors()
    test_validate_six_room_scene_graph_data_checks_round_trip_json()
    test_six_room_scene_graph_from_data_imports_edited_room_and_connection_metadata()
    test_format_scene_room_info_reports_bounds_and_connections()
    test_format_scene_room_summary_reports_compact_bounds()
    test_format_scene_connection_summary_reports_edges()
    test_scene_rects_expose_review_coordinates()
    test_scene_coordinate_lookup_reports_region_room_and_glyph()
    test_graph_scoped_coordinate_lookup_uses_supplied_graph()
    test_six_room_scene_cli_generates_artifacts_and_cell_report()
    test_six_room_scene_cli_lists_rooms()
    test_six_room_scene_cli_lists_connections()
    test_six_room_scene_cli_validates_graph()
    test_six_room_scene_cli_prints_graph_json()
    test_six_room_scene_cli_validates_loaded_graph_json()
    test_six_room_scene_cli_regenerates_artifacts_from_loaded_graph_json()
    test_write_six_room_scene_artifacts()
    test_write_six_room_scene_artifacts_uses_supplied_graph_rects()
    test_middle_seam_assembles_from_named_fragments()
    test_lower_band_assembles_from_named_strips()
    test_upper_band_assembles_from_named_strips()
    test_full_scene_assembles_from_named_regions()
    print("ALL six-room scene generator tests passed")


if __name__ == "__main__":
    main()
