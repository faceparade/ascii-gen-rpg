from corridor_variations_v2 import (
    HorizontalCorridorBand,
    VerticalCorridorBand,
    horizontal_corridor_bands,
    vertical_corridor_bands,
)
from junction_grammar_v2 import corridor_junctions, vertical_corridor_junctions
from style_sample_system import Point, cells_from_mask, render_irregular_room


WIDE_HORIZONTAL_MASK = (
    "###...###",
    "###...###",
    "#########",
    "#########",
    "###...###",
    "###...###",
)

WIDE_HORIZONTAL_DRAFT = (
    "  ,— —,— —,— —,           ,— —,— —,— —,",
    " /|__/___/__ /|          /|__/___/__ /|",
    "‘ |         | |         ‘ |         | |",
    "|/| `   `   |/|         |/| `   `   |/|",
    "| |         | ,— —,— —,—‘—,         | |",
    "|/| `   `   ‘/___/___/___/  `   `   |/|",
    "| |                                 | |",
    "|/| `   `   `   `   `   `   `   `   |/|",
    "| |           ,— —,— —,— —,         | |",
    "|/| `   `    /|__/___/___/  `   `   |/|",
    "| |         ‘ |         ‘ |         | |",
    "|/| `   `   |/|         |/| `   `   |/|",
    "| ,— —,— —,—‘—,         | ,— —,— —,—‘—,",
    "‘/___/___/___/          ‘/___/___/___/",
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

OFFSET_VERTICAL_DRAFT = (
    "  ,— —,— —,— —,— —,— —,— —,— —,",
    " /|__/___/___/___/___/___/__ /|",
    "‘ |                         | |",
    "|/| `   `   `   `   `   `   |/|",
    "| ,— —,   ,— —,— —,— —,— —,—‘—,",
    "‘/___/   /|__/___/___/___/___/",
    "    ‘ | ‘ |",
    "    |/| |/|",
    "    | | | |",
    "    |/| |/|",
    "  ,—‘—, | ,— —,— —,— —,— —,— —,",
    " /|__/  ‘/___/___/___/___/__ /|",
    "‘ |                         | |",
    "|/| `   `   `   `   `   `   |/|",
    "| ,— —,— —,— —,— —,— —,— —,—‘—,",
    "‘/___/___/___/___/___/___/___/",
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


def test_two_section_wide_horizontal_corridor_band() -> None:
    assert horizontal_corridor_bands(cells_from_mask(WIDE_HORIZONTAL_MASK)) == (
        HorizontalCorridorBand(3, 5, 2, 3, 2, 2, 2, 2),
    )
    band = horizontal_corridor_bands(cells_from_mask(WIDE_HORIZONTAL_MASK))[0]
    assert band.length == 3
    assert band.thickness == 2
    assert band.is_centered
    assert not band.is_offset


def test_wide_corridor_is_not_repainted_as_one_row_corridor() -> None:
    assert corridor_junctions(cells_from_mask(WIDE_HORIZONTAL_MASK)) == ()


def test_wide_corridor_literal_rendering_is_stable_for_review() -> None:
    assert render_irregular_room(cells_from_mask(WIDE_HORIZONTAL_MASK)) == WIDE_HORIZONTAL_DRAFT


def test_offset_vertical_opening_records_unequal_wall_margins() -> None:
    assert vertical_corridor_bands(cells_from_mask(OFFSET_VERTICAL_MASK)) == (
        VerticalCorridorBand(1, 1, 2, 4, 1, 5, 1, 5),
    )
    band = vertical_corridor_bands(cells_from_mask(OFFSET_VERTICAL_MASK))[0]
    assert band.thickness == 1
    assert band.length == 3
    assert band.is_offset
    assert not band.is_centered


def test_existing_vertical_classifier_accepts_offset_opening() -> None:
    junctions = vertical_corridor_junctions(cells_from_mask(OFFSET_VERTICAL_MASK))
    assert len(junctions) == 1
    assert junctions[0].boundary_x == 1
    assert (junctions[0].start_y, junctions[0].end_y) == (2, 4)


def test_offset_vertical_literal_rendering_is_stable_for_review() -> None:
    assert render_irregular_room(cells_from_mask(OFFSET_VERTICAL_MASK)) == OFFSET_VERTICAL_DRAFT


def test_centered_vertical_corridor_remains_centered() -> None:
    assert vertical_corridor_bands(cells_from_mask(CENTERED_VERTICAL_MASK)) == (
        VerticalCorridorBand(2, 2, 2, 4, 2, 2, 2, 2),
    )


def test_solid_room_has_no_corridor_bands() -> None:
    solid = frozenset(Point(x, y) for y in range(5) for x in range(5))
    assert horizontal_corridor_bands(solid) == ()
    assert vertical_corridor_bands(solid) == ()
