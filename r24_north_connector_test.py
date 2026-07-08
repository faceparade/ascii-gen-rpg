#!/usr/bin/env python3
"""Verification/artifact generator for port-aware R24 north connector experiments.

This is intentionally separate from the locked/editor baselines. It proves the
R24 downward tail can be treated as a port, mapped onto a chunk-based NorthWall
opening, then rendered as review artifacts for room-2-only and three-room cases.
"""
from __future__ import annotations

from pathlib import Path

from curved_dungeon_grammar import OUT_DIR, regular_vertical_pathway
from modular_ascii_parts import Opening, NorthWall, north_wall_top_width, north_wall_underside_width
from r24_north_connector import (
    R24NorthConnector,
    build_r24_room2_only_case,
    build_r24_three_room_case,
    r24_tail_port,
    write_r24_connector_artifacts,
)

ROOM2_X = 57
ROOM_Y = 3


def assert_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}\nactual:   {actual!r}\nexpected: {expected!r}")


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)


def test_r24_tail_port_is_derived_from_locked_stamp() -> None:
    stamp = regular_vertical_pathway(6)
    port = r24_tail_port(stamp)
    assert_equal((port.left, port.right), (10, 16), "R24 tail side-wall bounds should come from the locked tail row")
    assert_equal(port.width, 7, "R24 tail port width should include both side-wall columns")
    assert_equal(port.suggested_opening_width_chunks, 2, "R24 tail should map to the smallest coherent NorthWall opening preset")


def test_connector_maps_opening_chunk_to_reference_corner() -> None:
    connector = R24NorthConnector(room_x=ROOM2_X, room_y=ROOM_Y, opening=Opening(6, 1))
    assert_equal(connector.opening_start_x, ROOM2_X + 20, "reference compact opening should start at chunk 6")
    assert_equal(connector.upper_fragment_x, ROOM2_X + 8, "upper fragment should begin 8 glyphs into the room")
    assert_equal(connector.stamp_y, ROOM_Y - 3, "upper fragment should occupy the three rows immediately north of the room edge")


def test_generated_cases_keep_widths_and_visible_port_anchors() -> None:
    connector = R24NorthConnector(room_x=ROOM2_X, room_y=ROOM_Y, opening=Opening(6, 1))
    room2 = build_r24_room2_only_case(connector)
    three_room = build_r24_three_room_case(connector)
    assert_true(len(room2) >= ROOM_Y + 12, "room2-only scene should include shifted room shell")
    assert_true(len(three_room) >= ROOM_Y + 12, "three-room scene should include shifted base")

    north_rows = NorthWall(8, (Opening(6, 1),)).render()
    assert_equal((len(north_rows[0]), len(north_rows[1])), (north_wall_top_width(8), north_wall_underside_width(8)), "parametric wall widths stay coherent")
    assert_equal(room2[connector.stamp_y][connector.upper_fragment_x:connector.upper_fragment_x + 25], "|  `   `   `   `   `  '/|", "upper row should match the hand reference")
    assert_equal(room2[connector.stamp_y + 1][connector.upper_fragment_x:connector.upper_fragment_x + 25], "'- - - - - -.   .- - - -'", "cap row should match the hand reference corner style")
    assert_equal(room2[connector.stamp_y + 2][connector.opening_start_x:connector.opening_start_x + 5], "|  /|", "tail-above-north-edge row should match the hand reference")
    assert_equal(room2[ROOM_Y][connector.opening_start_x:connector.opening_start_x + 5], "j  ,t", "north-edge opening should use compact j/t corner join")
    assert_equal(room2[ROOM_Y + 1][connector.opening_start_x - 1:connector.opening_start_x + 5], "/   t_", "underside opening should keep slash-to-t corner join")
    assert_equal(three_room[ROOM_Y][connector.opening_start_x:connector.opening_start_x + 5], "j  ,t", "three-room north-edge opening should use compact j/t corner join")


def main() -> None:
    test_r24_tail_port_is_derived_from_locked_stamp()
    test_connector_maps_opening_chunk_to_reference_corner()
    test_generated_cases_keep_widths_and_visible_port_anchors()

    written = write_r24_connector_artifacts(OUT_DIR)
    for path in written:
        assert_true(Path(path).exists(), f"artifact should exist: {path}")
        print(path)
    print("PASS r24 north connector port-aware experiment")


if __name__ == "__main__":
    main()
