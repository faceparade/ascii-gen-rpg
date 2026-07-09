#!/usr/bin/env python3
"""Tests for room-graph assembly reproducing locked macro scenes."""
from __future__ import annotations

from connector_specs import HorizontalConnectorSpec
from curved_dungeon_grammar import horizontal_corridor
from room_graph import build_three_room_graph, render_room_graph
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


def main() -> None:
    test_three_room_graph_declares_room_and_connector_specs()
    test_horizontal_connector_spec_resolves_origin_and_locked_stamp()
    test_three_room_graph_render_matches_locked_macro()
    print("Room graph tests passed")


if __name__ == "__main__":
    main()
