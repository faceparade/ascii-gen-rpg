#!/usr/bin/env python3
"""Tests for the raised floor section abstraction."""
from __future__ import annotations

from pathlib import Path

from curved_dungeon_grammar import raised_floor_section_tall_narrow, raised_platform
from platform_shell import PlatformShell, RaisedFloorSection, RaisedShell

ROOT = Path(__file__).resolve().parent


def assert_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}\nactual:   {actual!r}\nexpected: {expected!r}")


def assert_source_slice(lines: list[str], origin: tuple[int, int], expected: list[str], label: str) -> None:
    x, y = origin
    extracted = [lines[y + dy][x:x + len(row)] for dy, row in enumerate(expected)]
    assert_equal(extracted, expected, label)


def test_raised_floor_section_matches_locked_stamp() -> None:
    section = RaisedFloorSection(4)
    rows = section.render()
    assert_equal(rows, raised_platform(4), "RaisedFloorSection must reproduce the locked raised floor section stamp")
    assert_equal(PlatformShell(4).render(), rows, "PlatformShell compatibility name should render the same raised floor section")
    assert_equal(len(rows), 7, "RaisedFloorSection height")
    assert_equal({len(row) for row in rows}, {23}, "RaisedFloorSection rows should be rectangular")
    assert_equal(section.width, 23, "RaisedFloorSection width property")
    assert_equal(section.height, 7, "RaisedFloorSection height property")
    assert_equal(RaisedShell(4).render(), rows, "RaisedShell alias should render the same locked section")
    print("PASS RaisedFloorSection reproduces locked raised floor section")


def test_raised_floor_section_documents_inverted_room_wall_faces() -> None:
    section = RaisedFloorSection(4)
    assert_equal(section.face_for_room_wall("east"), "left_face", "normal east wall maps to raised section left face")
    assert_equal(section.face_for_room_wall("north"), "bottom_face", "normal north wall maps to raised section bottom face")
    assert_equal(section.face_for_room_wall("west"), "right_face", "normal west wall maps to raised section right face")
    assert_equal(section.face_for_room_wall("south"), "top_rim", "normal south wall maps to raised section top rim")
    try:
        section.face_for_room_wall("ceiling")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown wall side should raise ValueError")
    print("PASS RaisedFloorSection exposes inverted room-wall mapping")


def test_raised_floor_sections_match_six_room_source() -> None:
    lines = (ROOT / "six_rooms_two_platforms.txt").read_text(encoding="utf-8").splitlines()
    full_section = RaisedFloorSection(4).render()

    assert_source_slice(
        lines,
        (117, 4),
        full_section,
        "full upper-right raised floor section should match six-room source",
    )

    # The lower-center section is partially interrupted by surrounding room/connector
    # art in the source. Lock the visible rows instead of inventing hidden side-wall rows.
    lower_center_visible = [
        full_section[0],
        full_section[1],
        full_section[2],
        "|/‘— —,— —,— —,— —,— -'",
        full_section[6],
    ]
    assert_source_slice(
        lines,
        (60, 22),
        lower_center_visible,
        "lower-center raised floor section visible rows should match six-room source",
    )

    narrow_lower_right = raised_floor_section_tall_narrow()
    assert_equal(len(narrow_lower_right), 7, "tall/narrow raised floor section height")
    assert_equal({len(row) for row in narrow_lower_right}, {7}, "tall/narrow raised floor section width")
    assert_source_slice(
        lines,
        (117, 20),
        narrow_lower_right,
        "minimal tall/narrow lower-right raised floor section should match six-room source",
    )
    assert_equal(lines[20][117], "`", "tall/narrow raised floor section should start on a backtick grid column")

    widened_floor_section = [
        "` ,— — — — — — — — — — — —.".ljust(29),
        " /|                       |".ljust(29),
        ", |                       |".ljust(29),
        "|/|                       |".ljust(29),
    ]
    for origin in ((31, 8), (88, 8), (31, 24), (88, 24)):
        assert_source_slice(
            lines,
            origin,
            widened_floor_section,
            f"widened raised floor section at {origin} should match six-room source",
        )
        x, y = origin
        assert_equal(lines[y][x], "`", f"raised floor section at {origin} should start on a backtick grid column")

    print("PASS RaisedFloorSection source variants match the six-room grid-aligned art")


def test_raised_floor_section_rejects_unlocked_widths() -> None:
    try:
        RaisedFloorSection(5).render()
    except NotImplementedError:
        pass
    else:
        raise AssertionError("RaisedFloorSection should reject widths without a locked reference")
    print("PASS RaisedFloorSection rejects unlocked widths")


def main() -> None:
    test_raised_floor_section_matches_locked_stamp()
    test_raised_floor_section_documents_inverted_room_wall_faces()
    test_raised_floor_sections_match_six_room_source()
    test_raised_floor_section_rejects_unlocked_widths()
    print("ALL RaisedFloorSection tests passed")


if __name__ == "__main__":
    main()
