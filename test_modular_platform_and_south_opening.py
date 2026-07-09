#!/usr/bin/env python3
"""Tests for raised floor section placement and south-opening template extraction."""
from __future__ import annotations

from connector_specs import SouthOpeningTemplateSpec
from curved_dungeon_grammar import raised_platform
from latest_r24_style import SOURCE_OF_TRUTH_PATH, latest_reference_lines
from platform_shell import PlatformShell
from r24_north_connector import R24NorthConnector, build_r24_three_room_case
from three_room_macro_test import ROOM_PITCH_X

ROOM2_X = ROOM_PITCH_X
ROOM3_X = ROOM_PITCH_X * 2
PLATFORM_OFFSET_X = 4
PLATFORM_OFFSET_Y = 4


def assert_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}\nactual:   {actual!r}\nexpected: {expected!r}")


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)


def test_raised_floor_section_is_a_standalone_modular_stamp() -> None:
    section = PlatformShell(4).render()
    assert_equal(section, raised_platform(4), "PlatformShell should delegate to the locked raised floor section stamp")
    assert_equal(len(section), 7, "raised floor section should include the full six-room source body")
    assert_equal(len({len(row) for row in section}), 1, "raised floor section rows should be rectangular")
    assert_equal(section[0].rstrip(), "` ,— — — — — — — — — —.", "raised floor section top should match the six-room source embedded rim")
    assert_true(";.;" in section[-1], "raised floor section floor should keep the centered movement/pass-through detail")


def test_r24_scene_leaves_room2_empty_and_moves_raised_floor_section_to_room3() -> None:
    scene = build_r24_three_room_case()
    room2_window = [row[ROOM2_X:ROOM2_X + 34] for row in scene[4:15]]
    room3_window = [row[ROOM3_X:ROOM3_X + 34] for row in scene[4:15]]

    assert_equal(scene, latest_reference_lines(), "R24 scene should reproduce six_rooms_two_platforms.txt byte-for-byte")
    assert_equal(SOURCE_OF_TRUTH_PATH.name, "six_rooms_two_platforms.txt", "active scene source of truth should be the six-room reference")
    assert_true(all(";.;" not in row for row in room2_window), "room 2 should not contain the raised floor section detail")
    assert_true(any(";.;" in row for row in room3_window), "room 3 should contain the moved raised floor section detail")
    assert_true("‘/___/___/;.;/___/___/" in "\n".join(room3_window), "room 3 should use the corrected raised floor section with the far-left curved column")


def test_north_connector_upper_fragment_is_south_opening_template() -> None:
    connector = R24NorthConnector()
    template = SouthOpeningTemplateSpec.compact_r24()
    assert_equal(
        template.rows,
        tuple(connector.reference_upper_rows),
        "north connector upper fragment should be reusable as a south-opening template for the room above",
    )
    assert_equal(connector.south_opening_spec, template, "R24 connector should expose the reusable south-opening spec")


def main() -> None:
    test_raised_floor_section_is_a_standalone_modular_stamp()
    test_r24_scene_leaves_room2_empty_and_moves_raised_floor_section_to_room3()
    test_north_connector_upper_fragment_is_south_opening_template()
    print("Raised floor section and south-opening tests passed")


if __name__ == "__main__":
    main()
