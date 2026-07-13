from pathlib import Path

from corridor_variations_v2 import (
    HorizontalCorridorBand,
    VerticalCorridorBand,
    horizontal_corridor_bands,
    vertical_corridor_bands,
)
from junction_grammar_v2 import (
    corridor_junctions,
    horizontal_junctions,
    vertical_corridor_junctions,
)
from style_sample_system import Point, cells_from_mask, render_irregular_room


TARGETS = Path("style_samples/targets")


def _target(name: str) -> tuple[str, ...]:
    return tuple((TARGETS / name).read_text(encoding="utf-8").splitlines())


WIDE_HORIZONTAL_MASK = (
    "###...###",
    "###...###",
    "#########",
    "#########",
    "###...###",
    "###...###",
)

OFFSET_VERTICAL_MASK = (
    "#######",
    "#######",
    ".#.....",
    ".#.....",
    ".#.....",
    "#######",
    "#######",
)

SHIFTED_ROOM_STRAIGHT_MASK = (
    "#######....",
    "#######....",
    ".....#.....",
    ".....#.....",
    ".....#.....",
    "....#######",
    "....#######",
)

MIRRORED_SHIFTED_ROOM_STRAIGHT_MASK = (
    "....#######",
    "....#######",
    ".....#.....",
    ".....#.....",
    ".....#.....",
    "#######....",
    "#######....",
)

CENTERED_VERTICAL_MASK = (
    "#####",
    "#####",
    "..#..",
    "..#..",
    "..#..",
    "#####",
    "#####",
)

WIDE_VERTICAL_MASK = (
    "########",
    "########",
    "...##...",
    "...##...",
    "...##...",
    "########",
    "########",
)

WIDE_OFFSET_VERTICAL_MASK = (
    "########",
    "########",
    ".##.....",
    ".##.....",
    ".##.....",
    "########",
    "########",
)

WIDE_EAST_OFFSET_VERTICAL_MASK = (
    "########",
    "########",
    ".....##.",
    ".....##.",
    ".....##.",
    "########",
    "########",
)

WIDE_SHIFTED_ROOM_STRAIGHT_MASK = (
    "########....",
    "########....",
    ".....##.....",
    ".....##.....",
    ".....##.....",
    "....########",
    "....########",
)


def test_two_section_wide_horizontal_corridor_band() -> None:
    assert horizontal_corridor_bands(cells_from_mask(WIDE_HORIZONTAL_MASK)) == (
        HorizontalCorridorBand(3, 5, 2, 3, 2, 2, 2, 2),
    )
    band = horizontal_corridor_bands(cells_from_mask(WIDE_HORIZONTAL_MASK))[0]
    assert band.length == 3
    assert band.thickness == 2
    assert band.is_centered
    assert not band.is_offset


def test_wide_horizontal_corridor_bypasses_one_row_resolvers() -> None:
    cells = cells_from_mask(WIDE_HORIZONTAL_MASK)
    assert corridor_junctions(cells) == ()
    assert horizontal_junctions(cells) == ()


def test_wide_horizontal_rendering_matches_approved_target() -> None:
    assert render_irregular_room(cells_from_mask(WIDE_HORIZONTAL_MASK)) == _target(
        "room-wide-horizontal-corridor-v2.txt"
    )


def test_offset_vertical_opening_records_unequal_wall_margins() -> None:
    assert vertical_corridor_bands(cells_from_mask(OFFSET_VERTICAL_MASK)) == (
        VerticalCorridorBand(1, 1, 2, 4, 1, 5, 1, 5),
    )
    band = vertical_corridor_bands(cells_from_mask(OFFSET_VERTICAL_MASK))[0]
    assert band.thickness == 1
    assert band.length == 3
    assert band.is_offset
    assert not band.is_centered
    assert band.rooms_are_horizontally_aligned
    assert band.opening_margins_match


def test_existing_vertical_classifier_accepts_offset_opening() -> None:
    junctions = vertical_corridor_junctions(cells_from_mask(OFFSET_VERTICAL_MASK))
    assert len(junctions) == 1
    assert junctions[0].boundary_x == 1
    assert (junctions[0].start_y, junctions[0].end_y) == (2, 4)


def test_offset_vertical_rendering_matches_approved_target() -> None:
    assert render_irregular_room(cells_from_mask(OFFSET_VERTICAL_MASK)) == _target(
        "room-offset-vertical-corridor-v2.txt"
    )


def test_shifted_rooms_keep_one_straight_corridor_column() -> None:
    bands = vertical_corridor_bands(cells_from_mask(SHIFTED_ROOM_STRAIGHT_MASK))
    assert bands == (
        VerticalCorridorBand(5, 5, 2, 4, 5, 1, 1, 5),
    )
    band = bands[0]
    assert band.thickness == 1
    assert band.length == 3
    assert band.start_x == band.end_x == 5
    assert band.room_shift_x == 4
    assert not band.rooms_are_horizontally_aligned
    assert not band.opening_margins_match


def test_mirrored_shifted_rooms_record_negative_room_shift() -> None:
    bands = vertical_corridor_bands(cells_from_mask(MIRRORED_SHIFTED_ROOM_STRAIGHT_MASK))
    assert bands == (
        VerticalCorridorBand(5, 5, 2, 4, 1, 5, 5, 1),
    )
    band = bands[0]
    assert band.start_x == band.end_x == 5
    assert band.room_shift_x == -4
    assert not band.rooms_are_horizontally_aligned
    assert not band.opening_margins_match


def test_existing_vertical_classifier_accepts_both_shift_directions() -> None:
    east_shift = vertical_corridor_junctions(cells_from_mask(SHIFTED_ROOM_STRAIGHT_MASK))
    west_shift = vertical_corridor_junctions(cells_from_mask(MIRRORED_SHIFTED_ROOM_STRAIGHT_MASK))
    assert len(east_shift) == len(west_shift) == 1
    assert east_shift[0].boundary_x == west_shift[0].boundary_x == 5
    assert (east_shift[0].start_y, east_shift[0].end_y) == (2, 4)
    assert (west_shift[0].start_y, west_shift[0].end_y) == (2, 4)


def test_shifted_room_renderings_match_approved_targets() -> None:
    assert render_irregular_room(cells_from_mask(SHIFTED_ROOM_STRAIGHT_MASK)) == _target(
        "room-shifted-straight-corridor-v2.txt"
    )
    assert render_irregular_room(
        cells_from_mask(MIRRORED_SHIFTED_ROOM_STRAIGHT_MASK)
    ) == _target("room-mirrored-shifted-straight-corridor-v2.txt")


def test_centered_vertical_corridor_remains_centered() -> None:
    assert vertical_corridor_bands(cells_from_mask(CENTERED_VERTICAL_MASK)) == (
        VerticalCorridorBand(2, 2, 2, 4, 2, 2, 2, 2),
    )


def test_wide_vertical_corridor_matrix() -> None:
    cases = (
        (
            WIDE_VERTICAL_MASK,
            VerticalCorridorBand(3, 4, 2, 4, 3, 3, 3, 3),
            "room-wide-vertical-corridor-v2.txt",
        ),
        (
            WIDE_OFFSET_VERTICAL_MASK,
            VerticalCorridorBand(1, 2, 2, 4, 1, 5, 1, 5),
            "room-wide-offset-vertical-corridor-v2.txt",
        ),
        (
            WIDE_EAST_OFFSET_VERTICAL_MASK,
            VerticalCorridorBand(5, 6, 2, 4, 5, 1, 5, 1),
            "room-wide-east-offset-vertical-corridor-v2.txt",
        ),
        (
            WIDE_SHIFTED_ROOM_STRAIGHT_MASK,
            VerticalCorridorBand(5, 6, 2, 4, 5, 1, 1, 5),
            "room-wide-shifted-straight-corridor-v2.txt",
        ),
    )

    for mask, expected_band, target_name in cases:
        cells = cells_from_mask(mask)
        assert vertical_corridor_bands(cells) == (expected_band,)
        band = vertical_corridor_bands(cells)[0]
        assert band.length == 3
        assert band.thickness == 2
        assert vertical_corridor_junctions(cells) == ()
        assert render_irregular_room(cells) == _target(target_name)


def test_wide_vertical_matrix_records_centering_offset_and_room_shift() -> None:
    centered = vertical_corridor_bands(cells_from_mask(WIDE_VERTICAL_MASK))[0]
    west_offset = vertical_corridor_bands(cells_from_mask(WIDE_OFFSET_VERTICAL_MASK))[0]
    east_offset = vertical_corridor_bands(cells_from_mask(WIDE_EAST_OFFSET_VERTICAL_MASK))[0]
    shifted = vertical_corridor_bands(cells_from_mask(WIDE_SHIFTED_ROOM_STRAIGHT_MASK))[0]

    assert centered.is_centered
    assert centered.room_shift_x == 0
    assert west_offset.is_offset and west_offset.room_shift_x == 0
    assert east_offset.is_offset and east_offset.room_shift_x == 0
    assert shifted.is_offset and shifted.room_shift_x == 4
    assert west_offset.opening_margins_match
    assert east_offset.opening_margins_match
    assert not shifted.opening_margins_match


def test_solid_room_has_no_corridor_bands() -> None:
    solid = frozenset(Point(x, y) for y in range(5) for x in range(5))
    assert horizontal_corridor_bands(solid) == ()
    assert vertical_corridor_bands(solid) == ()
