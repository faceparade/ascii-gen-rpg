#!/usr/bin/env python3
"""First failing tests for the corrected section-based room/corridor/enclosure system."""
from __future__ import annotations


def test_section_layout_module_exists() -> None:
    try:
        import section_layout as _imported  # noqa: F401
    except ImportError:
        raise AssertionError("section_layout is not yet implemented")


def _section_layout_imported():
    try:
        import section_layout  # noqa: F401
    except ImportError:
        raise AssertionError("section_layout is not yet implemented")
    return section_layout


def _room_renderer_imported():
    try:
        import section_room_renderer  # noqa: F401
    except ImportError:
        raise AssertionError("section_room_renderer is not yet implemented")
    return section_room_renderer


def test_nine_by_seven_room_owns_complete_north_wall() -> None:
    section_layout = _section_layout_imported()
    section_room_renderer = _room_renderer_imported()

    spec = section_layout.RoomModuleSpec(
        room_id="room_a",
        width_sections=9,
        height_sections=7,
        openings=(section_layout.DoorwaySpec("east", 2, 1),),
    )

    room = section_room_renderer.render_room(spec)
    rows = room.rows
    assert rows, "rendered room must not be empty"
    north = rows[0]
    assert any("north_wall" in src for key, src in room.provenance.items() if key.startswith("north_")), "first provenance region must belong to the north wall"
    assert len(north) > 0, "north wall must not be blank"
    assert "," in north or "|" in north, "north wall row must carry the room's own north-wall glyphs"
    assert room.width_sections == 9
    assert room.height_sections == 7


def test_ten_by_six_room_owns_complete_north_wall() -> None:
    section_layout = _section_layout_imported()
    section_room_renderer = _room_renderer_imported()

    spec = section_layout.RoomModuleSpec(
        room_id="room_b",
        width_sections=10,
        height_sections=6,
    )

    room = section_room_renderer.render_room(spec)
    rows = room.rows
    north = rows[0]
    assert any("north_wall" in src for key, src in room.provenance.items() if key.startswith("north_")), \
        "room must record north-wall provenance"
    assert "," in north or "|" in north, "north wall row must not be blank"
    assert room.width_sections == 10
    assert room.height_sections == 6


def test_east_doorway_is_section_addressed_at_offset_two() -> None:
    section_layout = _section_layout_imported()
    section_room_renderer = _room_renderer_imported()

    spec = section_layout.RoomModuleSpec(
        room_id="room_a",
        width_sections=9,
        height_sections=7,
        openings=(section_layout.DoorwaySpec("east", 2, 1),),
    )

    room = section_room_renderer.render_room(spec)
    east_port = room.ports["east"]
    assert east_port is not None
    assert east_port.offset_sections == 2
    assert east_port.span_sections == 1


def test_room_b_with_closed_three_by_four_enclosure() -> None:
    section_layout = _section_layout_imported()
    section_room_renderer = _room_renderer_imported()

    spec = section_layout.RoomModuleSpec(
        room_id="room_b",
        width_sections=10,
        height_sections=6,
        interiors=(
            section_layout.InteriorEnclosureSpec(
                x_sections=2,
                y_sections=1,
                width_sections=3,
                height_sections=4,
                openings=(),
                style="raised_floor",
            ),
        ),
    )

    room = section_room_renderer.render_room(spec)
    assert room.interiors
    enclosure = room.interiors[0]
    assert enclosure.x_sections == 2
    assert enclosure.y_sections == 1
    assert enclosure.width_sections == 3
    assert enclosure.height_sections == 4
    assert enclosure.openings == ()
    assert enclosure.style == "raised_floor"
    assert any(
        "enclosure" in part
        for src in room.provenance.values()
        for part in src
    )


if __name__ == "__main__":
    tests = [
        test_section_layout_module_exists,
        test_nine_by_seven_room_owns_complete_north_wall,
        test_ten_by_six_room_owns_complete_north_wall,
        test_east_doorway_is_section_addressed_at_offset_two,
        test_room_b_with_closed_three_by_four_enclosure,
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
