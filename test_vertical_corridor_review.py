from irregular_room_grammar import directional_runs
from junction_grammar_v2 import VerticalJunction, vertical_junctions
from style_sample_system import (
    Point,
    cells_from_mask,
    render_irregular_room,
    section_occluders,
)


VERTICAL_CORRIDOR_MASK = (
    "#####",
    "#####",
    "..#..",
    "..#..",
    "..#..",
    "#####",
    "#####",
)
APPROVED_TARGET = (
    "  ,— —,— —,— —,— —,— —,",
    " /|__/___/___/___/___/|",
    "‘ |                 | |",
    "|/| `   `   `   `   |/|",
    "| ,— —,— —,   ,— —,—‘—,",
    "‘/___/___/   /|__/___/",
    "        ‘ | ‘ |",
    "        |/| |/|",
    "        | | | |",
    "        |/| |/|",
    "  ,— —,—‘—, | ,— —,— —,",
    " /|__/___/  ‘/___/___/|",
    "‘ |                 | |",
    "|/| `   `   `   `   |/|",
    "| ,— —,— —,— —,— —,—‘—,",
    "‘/___/___/___/___/___/",
)


def test_vertical_room_passage_is_classified_from_topology() -> None:
    assert vertical_junctions(cells_from_mask(VERTICAL_CORRIDOR_MASK)) == (
        VerticalJunction(
            "vertical_corridor",
            2,
            2,
            4,
            "upper_room",
            "lower_room",
        ),
    )


def test_vertical_corridor_has_paired_directional_wall_runs() -> None:
    cells = cells_from_mask(VERTICAL_CORRIDOR_MASK)
    assert directional_runs(cells, "west") == (
        (0, 0, 1),
        (0, 5, 6),
        (2, 2, 4),
    )
    assert directional_runs(cells, "east") == (
        (3, 2, 4),
        (5, 0, 1),
        (5, 5, 6),
    )


def test_vertical_corridor_west_wall_is_the_only_actor_occluder() -> None:
    cells = cells_from_mask(VERTICAL_CORRIDOR_MASK)
    for y in range(2, 5):
        assert section_occluders(cells, Point(2, y)) == frozenset({"west"})


def test_vertical_corridor_matches_approved_target_exactly() -> None:
    assert render_irregular_room(cells_from_mask(VERTICAL_CORRIDOR_MASK)) == APPROVED_TARGET
