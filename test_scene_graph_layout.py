#!/usr/bin/env python3
"""Tests for reusable scene graphs and the staggered four-room layout."""
from __future__ import annotations

import json

from scene_graph import (
    SceneGraph,
    SceneRegionSpec,
    render_scene_graph,
    validate_scene_graph,
)
from six_room_scene import (
    LOWER_BAND_GAP_STRIP,
    LOWER_BAND_MIDDLE_ROOM_STRIP,
    LOWER_BAND_RIGHT_ROOM_STRIP,
    SCENE_MID_CONNECTOR_ROWS,
    UPPER_BAND_GAP_STRIP,
    UPPER_BAND_LEFT_ROOM_STRIP,
    UPPER_BAND_RIGHT_ROOM_STRIP,
    build_six_room_scene_graph,
    write_scene_artifacts,
)
from staggered_four_room_scene import (
    build_staggered_four_room_scene_graph,
    write_staggered_four_room_scene_artifacts,
)


def test_generic_renderer_honors_one_based_region_start_lines() -> None:
    graph = SceneGraph(
        rooms=(),
        connections=(),
        regions=(
            SceneRegionSpec("first", 1, ("aa",)),
            SceneRegionSpec("third", 3, ("bbb",)),
        ),
    )

    assert render_scene_graph(graph) == ["aa", "", "bbb"]


def test_generic_renderer_rejects_nonpositive_or_overlapping_regions() -> None:
    invalid_start = SceneGraph(
        rooms=(),
        connections=(),
        regions=(SceneRegionSpec("invalid", 0, ("x",)),),
    )
    overlapping = SceneGraph(
        rooms=(),
        connections=(),
        regions=(
            SceneRegionSpec("first", 1, ("a", "b")),
            SceneRegionSpec("second", 2, ("c",)),
        ),
    )

    for graph, message in (
        (invalid_start, "start_line must be positive"),
        (overlapping, "overlaps an earlier region"),
    ):
        try:
            render_scene_graph(graph)
        except ValueError as error:
            assert message in str(error)
        else:
            raise AssertionError(f"expected ValueError containing {message!r}")


def test_artifact_writer_rejects_unsafe_stems(tmp_path) -> None:
    graph = build_staggered_four_room_scene_graph()

    for stem in ("", ".", "..", "../escaped", "nested/escaped", r"nested\escaped"):
        try:
            write_scene_artifacts(tmp_path, graph, stem)
        except ValueError as error:
            assert "artifact_stem" in str(error)
        else:
            raise AssertionError(f"expected unsafe artifact stem to be rejected: {stem!r}")


def test_staggered_four_room_layout_is_a_distinct_path() -> None:
    graph = build_staggered_four_room_scene_graph()
    six_room_graph = build_six_room_scene_graph()

    assert isinstance(graph, SceneGraph)
    assert isinstance(six_room_graph, SceneGraph)
    assert validate_scene_graph(graph) == ()
    assert [(room.room_id, room.x, room.y, room.width, room.height) for room in graph.rooms] == [
        ("north_west", 0, 0, 34, 9),
        ("north_east", 57, 0, 34, 9),
        ("south_center", 57, 13, 34, 7),
        ("south_east", 114, 13, 34, 7),
    ]
    assert [(edge.from_room, edge.to_room, edge.kind) for edge in graph.connections] == [
        ("north_west", "north_east", "horizontal"),
        ("north_east", "south_center", "vertical"),
        ("south_center", "south_east", "horizontal"),
    ]
    assert len(graph.rooms) != len(build_six_room_scene_graph().rooms)


def test_staggered_four_room_layout_reuses_locked_strips_byte_for_byte() -> None:
    graph = build_staggered_four_room_scene_graph()
    rows = render_scene_graph(graph)

    expected_upper = [
        left + gap + right
        for left, gap, right in zip(
            UPPER_BAND_LEFT_ROOM_STRIP,
            UPPER_BAND_GAP_STRIP,
            UPPER_BAND_RIGHT_ROOM_STRIP,
            strict=True,
        )
    ]
    expected_bridge = [" " * 57 + row[57:91] + " " * 57 for row in SCENE_MID_CONNECTOR_ROWS]
    expected_lower = [
        " " * 57 + middle + gap + right
        for middle, gap, right in zip(
            LOWER_BAND_MIDDLE_ROOM_STRIP,
            LOWER_BAND_GAP_STRIP,
            LOWER_BAND_RIGHT_ROOM_STRIP,
            strict=True,
        )
    ]

    assert rows == expected_upper + expected_bridge + expected_lower
    assert max(map(len, rows)) == 148
    assert len(rows) == 20


def test_staggered_four_room_artifacts_use_distinct_names_and_graph_metadata(tmp_path) -> None:
    graph = build_staggered_four_room_scene_graph()

    paths = write_staggered_four_room_scene_artifacts(tmp_path)

    assert [path.name for path in paths] == [
        "staggered_four_room_scene_generated.txt",
        "staggered_four_room_scene_generated_annotated.txt",
        "staggered_four_room_scene_generated.html",
        "staggered_four_room_scene_graph.json",
    ]
    assert paths[0].read_text(encoding="utf-8").splitlines() == render_scene_graph(graph)
    graph_data = json.loads(paths[3].read_text(encoding="utf-8"))
    assert [room["room_id"] for room in graph_data["rooms"]] == [
        "north_west",
        "north_east",
        "south_center",
        "south_east",
    ]
    assert len(graph_data["connections"]) == 3
    html = paths[2].read_text(encoding="utf-8")
    assert "north_west" in html
    assert "staggered_four_room_scene_graph_edited.json" in html
    assert "six_room_scene_graph_edited.json" not in html
