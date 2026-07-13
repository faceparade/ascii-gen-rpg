from pathlib import Path

from irregular_room_grammar import directional_runs
from junction_grammar_v2 import (
    HorizontalJunction,
    VerticalJunction,
    horizontal_junctions,
    vertical_junctions,
)
from style_sample_system import (
    Point,
    cells_from_mask,
    render_irregular_room,
    section_occluders,
)


T_MASK = (
    "###...###",
    "###...###",
    "#########",
    "....#....",
    "....#....",
    "....#....",
    "..#####..",
    "..#####..",
)


def approved_target() -> tuple[str, ...]:
    path = Path(__file__).parent / "style_samples" / "targets" / "room-t-junction-v2.txt"
    return tuple(path.read_text(encoding="utf-8").splitlines())


def test_three_room_layout_is_classified_as_south_branch_t_junction() -> None:
    junctions = horizontal_junctions(cells_from_mask(T_MASK))
    assert junctions[0] == HorizontalJunction(
        "south_branch_t_junction",
        2,
        3,
        5,
        "inner_east_wall",
        "inner_west_wall",
        4,
    )


def test_vertical_branch_terminates_at_t_junction_and_lower_room() -> None:
    assert vertical_junctions(cells_from_mask(T_MASK)) == (
        VerticalJunction(
            "vertical_corridor",
            4,
            3,
            5,
            "t_junction",
            "lower_room",
        ),
    )


def test_t_branch_directional_walls_and_occlusion_are_stable() -> None:
    cells = cells_from_mask(T_MASK)
    assert (4, 3, 5) in directional_runs(cells, "west")
    assert (5, 3, 5) in directional_runs(cells, "east")
    assert section_occluders(cells, Point(4, 2)) == frozenset()
    for y in range(3, 6):
        assert section_occluders(cells, Point(4, y)) == frozenset({"west"})


def test_t_junction_matches_approved_target_exactly() -> None:
    assert render_irregular_room(cells_from_mask(T_MASK)) == approved_target()
