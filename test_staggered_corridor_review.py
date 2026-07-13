from pathlib import Path

from corridor_variations_v2 import vertical_corridor_bands
from staggered_corridor_v2 import StaggeredVerticalCorridor, staggered_vertical_corridors
from style_sample_system import Point, cells_from_mask, render_irregular_room


TARGET = Path("style_samples/targets/room-staggered-dogleg-corridor-v2.txt")

STAGGERED_MASK = (
    "#######",
    "#######",
    ".#.....",
    ".#.....",
    ".#####.",
    ".....#.",
    ".....#.",
    "#######",
    "#######",
)


def test_staggered_openings_form_one_eastward_dogleg() -> None:
    corridors = staggered_vertical_corridors(cells_from_mask(STAGGERED_MASK))
    assert corridors == (
        StaggeredVerticalCorridor(1, 5, 2, 4, 6, 1, 5, 5, 1),
    )
    corridor = corridors[0]
    assert corridor.direction == "eastward"
    assert corridor.horizontal_shift == 4
    assert corridor.path_length == 9


def test_dogleg_path_is_one_section_thick() -> None:
    corridor = staggered_vertical_corridors(cells_from_mask(STAGGERED_MASK))[0]
    assert corridor.path_cells == frozenset(
        {
            Point(1, 2),
            Point(1, 3),
            Point(1, 4),
            Point(2, 4),
            Point(3, 4),
            Point(4, 4),
            Point(5, 4),
            Point(5, 5),
            Point(5, 6),
        }
    )


def test_dogleg_is_not_a_rectangular_vertical_band() -> None:
    assert vertical_corridor_bands(cells_from_mask(STAGGERED_MASK)) == ()


def test_solid_room_has_no_staggered_corridor() -> None:
    solid = frozenset(Point(x, y) for y in range(7) for x in range(7))
    assert staggered_vertical_corridors(solid) == ()


def test_staggered_rendering_matches_approved_target() -> None:
    expected = tuple(TARGET.read_text(encoding="utf-8").splitlines())
    assert render_irregular_room(cells_from_mask(STAGGERED_MASK)) == expected
