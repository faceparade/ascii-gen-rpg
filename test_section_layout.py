#!/usr/bin/env python3
"""Tests for section_layout validation rules."""
from __future__ import annotations

import section_layout


def test_room_module_spec_rejects_invalid_width_and_height() -> None:
    for width in (0, -1):
        try:
            section_layout.RoomModuleSpec("room", width_sections=width, height_sections=1)
        except ValueError as exc:
            assert "width_sections" in str(exc)
        else:
            raise AssertionError(f"expected width {width} to raise ValueError")

    for height in (0, -1):
        try:
            section_layout.RoomModuleSpec("room", width_sections=1, height_sections=height)
        except ValueError as exc:
            assert "height_sections" in str(exc)
        else:
            raise AssertionError(f"expected height {height} to raise ValueError")


def test_room_module_spec_rejects_blank_room_id() -> None:
    try:
        section_layout.RoomModuleSpec("", width_sections=1, height_sections=1)
    except ValueError as exc:
        assert "room_id" in str(exc)
    else:
        raise AssertionError("expected blank room_id to raise ValueError")


def test_doorway_spec_rejects_nonpositive_offset_and_span() -> None:
    try:
        section_layout.DoorwaySpec("east", 0, 1)
    except ValueError as exc:
        assert "offset_sections" in str(exc)
    else:
        raise AssertionError("expected offset 0 to raise ValueError")

    try:
        section_layout.DoorwaySpec("east", 1, 0)
    except ValueError as exc:
        assert "span_sections" in str(exc)
    else:
        raise AssertionError("expected span 0 to raise ValueError")


def test_corridor_module_spec_rejects_same_side_and_nonpositive_length() -> None:
    try:
        section_layout.CorridorModuleSpec(
            from_room="a",
            from_side="east",
            from_offset_sections=1,
            to_room="b",
            to_side="east",
            to_offset_sections=1,
            length_sections=1,
        )
    except ValueError as exc:
        assert "opposite sides" in str(exc)
    else:
        raise AssertionError("expected same-sided corridor to raise ValueError")

    try:
        section_layout.CorridorModuleSpec(
            from_room="a",
            from_side="east",
            from_offset_sections=1,
            to_room="b",
            to_side="west",
            to_offset_sections=1,
            length_sections=0,
        )
    except ValueError as exc:
        assert "length_sections" in str(exc)
    else:
        raise AssertionError("expected zero length corridor to raise ValueError")


def test_interior_enclosure_spec_rejects_openings_for_locked_proof_scene() -> None:
    try:
        section_layout.InteriorEnclosureSpec(
            x_sections=1,
            y_sections=1,
            width_sections=3,
            height_sections=4,
            openings=(section_layout.DoorwaySpec("east", 1, 1),),
            style="raised_floor",
        )
    except ValueError as exc:
        assert "openings must be empty" in str(exc)
    else:
        raise AssertionError("expected enclosure openings to raise ValueError")


if __name__ == "__main__":
    tests = [
        test_room_module_spec_rejects_invalid_width_and_height,
        test_room_module_spec_rejects_blank_room_id,
        test_doorway_spec_rejects_nonpositive_offset_and_span,
        test_corridor_module_spec_rejects_same_side_and_nonpositive_length,
        test_interior_enclosure_spec_rejects_openings_for_locked_proof_scene,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {test.__name__}: {exc}")
    print(f"{len(tests)-failed}/{len(tests)} passed; {failed} failed")
