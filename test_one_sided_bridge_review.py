from irregular_room_grammar import (
    courtyard_bridge_runs,
    directional_runs,
    one_sided_bridge_runs,
)
from style_sample_system import Point, cells_from_mask, lattice_points, render_irregular_room


ONE_SIDED_MASK = ("##....", "##....", "######")
APPROVED_TARGET = (
    "  ,— —,— —,",
    " /|__/___/|",
    "‘ |     | |",
    "|/| `   |/|",
    "| |     | ,— —,— —,— —,— —,",
    "|/| `   ‘/___/___/___/___/|",
    "| ,— —,— —,— —,— —,— —,—‘—,",
    "‘/___/___/___/___/___/___/",
)


def test_one_sided_bridge_topology_and_boundary_runs_are_stable() -> None:
    cells = cells_from_mask(ONE_SIDED_MASK)
    assert directional_runs(cells, "north") == ((0, 0, 1), (2, 2, 5))
    assert directional_runs(cells, "east") == ((2, 0, 1), (6, 2, 2))
    assert directional_runs(cells, "south") == ((3, 0, 5),)
    assert directional_runs(cells, "west") == ((0, 0, 2),)


def test_one_sided_bridge_has_left_leg_lattice_only() -> None:
    cells = cells_from_mask(ONE_SIDED_MASK)
    assert lattice_points(cells) == frozenset({Point(4, 3), Point(4, 5)})


def test_one_sided_bridge_uses_approved_specific_resolver() -> None:
    cells = cells_from_mask(ONE_SIDED_MASK)
    assert courtyard_bridge_runs(cells) == ()
    assert one_sided_bridge_runs(cells) == ((2, 2, 5),)


def test_one_sided_bridge_matches_approved_target_exactly() -> None:
    assert render_irregular_room(cells_from_mask(ONE_SIDED_MASK)) == APPROVED_TARGET
