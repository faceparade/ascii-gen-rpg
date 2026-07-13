from pathlib import Path

from corridor_variations_v2 import vertical_corridor_bands
from staggered_corridor_v2 import StaggeredVerticalCorridor, staggered_vertical_corridors
from style_sample_system import Point, cells_from_mask, render_irregular_room


TARGETS = Path("style_samples/targets")


def _target(name: str) -> tuple[str, ...]:
    return tuple((TARGETS / name).read_text(encoding="utf-8").splitlines())


EASTWARD_MASK = (
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

WESTWARD_MASK = (
    "#######",
    "#######",
    ".....#.",
    ".....#.",
    ".#####.",
    ".#.....",
    ".#.....",
    "#######",
    "#######",
)


def test_both_dogleg_directions_are_classified() -> None:
    eastward = staggered_vertical_corridors(cells_from_mask(EASTWARD_MASK))
    westward = staggered_vertical_corridors(cells_from_mask(WESTWARD_MASK))

    assert eastward == (
        StaggeredVerticalCorridor(1, 5, 2, 4, 6, 1, 5, 5, 1),
    )
    assert westward == (
        StaggeredVerticalCorridor(5, 1, 2, 4, 6, 5, 1, 1, 5),
    )
    assert eastward[0].direction == "eastward"
    assert westward[0].direction == "westward"
    assert eastward[0].horizontal_shift == westward[0].horizontal_shift == 4
    assert eastward[0].path_length == westward[0].path_length == 9


def test_dogleg_paths_are_one_section_thick() -> None:
    eastward = staggered_vertical_corridors(cells_from_mask(EASTWARD_MASK))[0]
    westward = staggered_vertical_corridors(cells_from_mask(WESTWARD_MASK))[0]

    assert eastward.path_cells == frozenset(
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
    assert westward.path_cells == frozenset(
        {
            Point(5, 2),
            Point(5, 3),
            Point(5, 4),
            Point(4, 4),
            Point(3, 4),
            Point(2, 4),
            Point(1, 4),
            Point(1, 5),
            Point(1, 6),
        }
    )


def test_doglegs_are_not_rectangular_vertical_bands() -> None:
    assert vertical_corridor_bands(cells_from_mask(EASTWARD_MASK)) == ()
    assert vertical_corridor_bands(cells_from_mask(WESTWARD_MASK)) == ()


def test_solid_room_has_no_staggered_corridor() -> None:
    solid = frozenset(Point(x, y) for y in range(7) for x in range(7))
    assert staggered_vertical_corridors(solid) == ()


def test_dogleg_renderings_match_approved_targets() -> None:
    assert render_irregular_room(cells_from_mask(EASTWARD_MASK)) == _target(
        "room-staggered-dogleg-corridor-v2.txt"
    )
    assert render_irregular_room(cells_from_mask(WESTWARD_MASK)) == _target(
        "room-westward-dogleg-corridor-v2.txt"
    )
