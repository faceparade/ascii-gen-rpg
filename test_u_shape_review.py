from irregular_room_grammar import directional_runs
from style_sample_system import Point, cells_from_mask, lattice_points, render_irregular_room


U_MASK = ("##..##", "##..##", "##..##", "######")


def test_u_shape_topology_and_boundary_runs_are_stable() -> None:
    cells = cells_from_mask(U_MASK)
    assert directional_runs(cells, "north") == (
        (0, 0, 1),
        (0, 4, 5),
        (3, 2, 3),
    )
    assert directional_runs(cells, "east") == (
        (2, 0, 2),
        (6, 0, 3),
    )
    assert directional_runs(cells, "west") == (
        (0, 0, 3),
        (4, 0, 2),
    )
    assert directional_runs(cells, "south") == ((4, 0, 5),)


def test_u_shape_has_two_independent_lattice_columns() -> None:
    cells = cells_from_mask(U_MASK)
    assert lattice_points(cells) == frozenset(
        {
            Point(4, 3), Point(4, 5), Point(4, 7),
            Point(20, 3), Point(20, 5), Point(20, 7),
        }
    )


def test_u_shape_draft_keeps_courtyard_void_open() -> None:
    rows = render_irregular_room(cells_from_mask(U_MASK))
    assert rows[2][11:16] == "     "
    assert rows[4][11:16] == "     "
    assert "— —,—" in rows[6]
