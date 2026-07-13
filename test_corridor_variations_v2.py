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
REVIEWS = Path("style_samples/review")


def _target(name: str) -> tuple[str, ...]:
    return tuple((TARGETS / name).read_text(encoding="utf-8").splitlines())


def _review_rows(name: str) -> tuple[str, ...]:
    lines = (REVIEWS / name).read_text(encoding="utf-8").splitlines()
    start = lines.index("AUTOMATIC DRAFT") + 2
    end = next((index for index in range(start, len(lines)) if not lines[index]), len(lines))
    return tuple(lines[start:end])


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
    assert (band.top_left_margin, band.top_right_margin) == (5, 1)
    assert (band.bottom_left_margin, band.bottom_right_margin) == (1, 5)
    assert band.room_shift_x == 4
    assert not band.rooms_are_horizontally_aligned
    assert not band.opening_margins_match
    assert band.is_offset


def test_existing_vertical_classifier_accepts_shifted_rooms() -> None:
    junctions = vertical_corridor_junctions(cells_from_mask(SHIFTED_ROOM_STRAIGHT_MASK))
    assert len(junctions) == 1
    assert junctions[0].boundary_x == 5
    assert (junctions[0].start_y, junctions[0].end_y) == (2, 4)


def test_shifted_room_straight_rendering_matches_approved_target() -> None:
    assert render_irregular_room(cells_from_mask(SHIFTED_ROOM_STRAIGHT_MASK)) == _target(
        "room-shifted-straight-corridor-v2.txt"
    )


def test_centered_vertical_corridor_remains_centered() -> None:
    assert vertical_corridor_bands(cells_from_mask(CENTERED_VERTICAL_MASK)) == (
        VerticalCorridorBand(2, 2, 2, 4, 2, 2, 2, 2),
    )


def test_two_section_wide_vertical_corridor_band() -> None:
    cells = cells_from_mask(WIDE_VERTICAL_MASK)
    assert vertical_corridor_bands(cells) == (
        VerticalCorridorBand(3, 4, 2, 4, 3, 3, 3, 3),
    )
    band = vertical_corridor_bands(cells)[0]
    assert band.length == 3
    assert band.thickness == 2
    assert band.is_centered
    assert band.room_shift_x == 0
    assert vertical_corridor_junctions(cells) == ()


def test_wide_vertical_literal_rendering_is_stable_for_review() -> None:
    assert render_irregular_room(cells_from_mask(WIDE_VERTICAL_MASK)) == _review_rows(
        "room-wide-vertical-corridor-v2.txt"
    )


def test_solid_room_has_no_corridor_bands() -> None:
    solid = frozenset(Point(x, y) for y in range(5) for x in range(5))
    assert horizontal_corridor_bands(solid) == ()
    assert vertical_corridor_bands(solid) == ()
