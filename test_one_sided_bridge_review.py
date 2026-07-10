from irregular_room_grammar import courtyard_bridge_runs, directional_runs
from style_sample_system import Point, cells_from_mask, lattice_points, render_irregular_room


ONE_SIDED_MASK = ("##....", "##....", "######")


def test_one_sided_bridge_topology_and_boundary_runs_are_stable() -> None:
    cells = cells_from_mask(ONE_SIDED_MASK)
    assert directional_runs(cells, "north") == ((0, 0, 1), (2, 2, 5))
    assert directional_runs(cells, "east") == ((2, 0, 1), (6, 2, 2))
    assert directional_runs(cells, "south") == ((3, 0, 5),)
    assert directional_runs(cells, "west") == ((0, 0, 2),)


def test_one_sided_bridge_has_left_leg_lattice_only() -> None:
    cells = cells_from_mask(ONE_SIDED_MASK)
    assert lattice_points(cells) == frozenset({Point(4, 3), Point(4, 5)})


def test_one_sided_bridge_is_not_misclassified_as_mirrored_courtyard() -> None:
    cells = cells_from_mask(ONE_SIDED_MASK)
    assert courtyard_bridge_runs(cells) == ()


def test_one_sided_bridge_review_draft_keeps_notch_open() -> None:
    rows = render_irregular_room(cells_from_mask(ONE_SIDED_MASK))
    assert rows[2][11:24].strip() == ""
    assert rows[4].startswith("| |     |")
    assert rows[-1] == "‘/___/___/___/___/___/___/"
