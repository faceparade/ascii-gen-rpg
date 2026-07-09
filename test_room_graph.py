#!/usr/bin/env python3
"""Tests for room-graph assembly reproducing locked macro scenes."""
from __future__ import annotations

from connector_specs import HorizontalConnectorSpec
from curved_dungeon_grammar import horizontal_corridor
from room_graph import build_six_room_scene_graph, build_three_room_graph, render_room_graph, render_six_room_scene_graph
from six_room_scene import assemble_six_room_scene_rows
from three_room_macro_test import build_three_room_macro_test


def assert_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}\nactual:   {actual!r}\nexpected: {expected!r}")


def test_three_room_graph_declares_room_and_connector_specs() -> None:
    graph = build_three_room_graph()
    assert_equal(
        [(room.room_id, room.shell_preset, room.x, room.y, None if room.platform is None else (room.platform.width_units, room.platform.offset_x, room.platform.offset_y)) for room in graph.rooms],
        [("room1", "left_8", 0, 0, None), ("room2", "middle_8", 57, 0, None), ("room3", "terminal_8", 114, 0, (4, 3, 4))],
        "three-room graph should declare room shell presets, origins, and raised floor section ownership as data",
    )
    assert_equal(
        [(connector.from_room, connector.to_room, connector.offset_x, connector.y, connector.width_units) for connector in graph.horizontal_connectors],
        [("room1", "room2", 32, 4, 6), ("room2", "room3", 32, 4, 6)],
        "three-room graph should declare corridor connectors as data",
    )


def test_horizontal_connector_spec_resolves_origin_and_locked_stamp() -> None:
    spec = HorizontalConnectorSpec("room1", "room2", 32, 4, 6)
    assert_equal(spec.origin_from_room_x(57), (89, 4), "horizontal connector origin should be source-room-local")
    assert_equal(spec.render(), horizontal_corridor(6), "horizontal connector spec should render the locked corridor stamp")


def test_three_room_graph_render_matches_locked_macro() -> None:
    generated = render_room_graph(build_three_room_graph())
    locked = build_three_room_macro_test()
    assert_equal(generated, locked, "graph-generated three-room scene must match locked macro byte-for-byte")


def test_six_room_scene_graph_declares_rooms_connections_and_regions() -> None:
    graph = build_six_room_scene_graph()
    assert_equal(
        [(room.room_id, room.x, room.y, room.width, room.height) for room in graph.rooms],
        [
            ("upper_left", 0, 4, 34, 9),
            ("upper_middle", 57, 4, 34, 9),
            ("upper_right", 114, 4, 34, 9),
            ("lower_left", 0, 17, 34, 12),
            ("lower_middle", 57, 17, 34, 12),
            ("lower_right", 114, 17, 34, 12),
        ],
        "six-room scene graph should expose locked room placements as data",
    )
    assert_equal(
        [(c.from_room, c.to_room, c.kind, c.region_name) for c in graph.connections],
        [
            ("upper_left", "upper_middle", "horizontal", "upper_band"),
            ("upper_middle", "upper_right", "horizontal", "upper_band"),
            ("upper_left", "lower_left", "vertical", "mid_connector"),
            ("upper_middle", "lower_middle", "vertical", "mid_connector"),
            ("upper_right", "lower_right", "vertical", "mid_connector"),
            ("lower_left", "lower_middle", "horizontal", "lower_band"),
            ("lower_middle", "lower_right", "horizontal", "lower_band"),
        ],
        "six-room scene graph should expose visible room adjacency as data",
    )
    assert_equal(
        [(region.name, region.start_line, region.end_line) for region in graph.regions],
        [("top", 1, 4), ("upper_band", 5, 13), ("mid_connector", 14, 17), ("middle_seam", 18, 19), ("lower_connector", 20, 22), ("lower_band", 23, 29)],
        "six-room scene graph should preserve named source regions as data",
    )


def test_six_room_scene_graph_render_matches_locked_scene() -> None:
    generated = render_six_room_scene_graph(build_six_room_scene_graph())
    locked = assemble_six_room_scene_rows()
    assert_equal(generated, locked, "graph-generated six-room scene must match locked scene byte-for-byte")


def main() -> None:
    test_three_room_graph_declares_room_and_connector_specs()
    test_horizontal_connector_spec_resolves_origin_and_locked_stamp()
    test_three_room_graph_render_matches_locked_macro()
    test_six_room_scene_graph_declares_rooms_connections_and_regions()
    test_six_room_scene_graph_render_matches_locked_scene()
    print("Room graph tests passed")


if __name__ == "__main__":
    main()
