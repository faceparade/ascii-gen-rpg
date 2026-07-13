from cross_junction_grammar_v2 import CrossJunction, cross_junctions
from style_sample_system import (
    Point,
    cells_from_mask,
    render_irregular_room,
    section_occluders,
)


CROSS_MASK = (
    "..#####..",
    "..#####..",
    "....#....",
    "....#....",
    "#########",
    "....#....",
    "....#....",
    "..#####..",
    "..#####..",
)

LITERAL_DRAFT = (
    "          ,— —,— —,— —,— —,— —,",
    "         /|__/___/___/___/___/|",
    "        ‘ |                 | |",
    "        |/| `   `   `   `   |/|",
    "        | ,— —,— —,   ,— —,—‘—,",
    "        ‘/___/___/   /|__/___/",
    "                ‘ | ‘ |",
    "                |/| |/|",
    "  ,— —,— —,— —,—‘—, | ,— —,— —,— —,— —,",
    " /|__/___/___/___/  ‘/___/___/___/___/|",
    "‘ ,— —,— —,— —,— —,   ,— —,— —,— —,—‘—,",
    "‘/___/___/___/___/   /|__/___/___/___/",
    "                ‘ | ‘ |",
    "                |/| |/|",
    "          ,— —,—‘—, | ,— —,— —,",
    "         /|__/___/  ‘/___/___/|",
    "        ‘ |                 | |",
    "        |/| `   `   `   `   |/|",
    "        | ,— —,— —,— —,— —,—‘—,",
    "        ‘/___/___/___/___/___/",
)


def test_cross_is_classified_from_local_topology() -> None:
    assert cross_junctions(cells_from_mask(CROSS_MASK)) == (
        CrossJunction("four_way_cross", Point(4, 4)),
    )


def test_room_interior_is_not_a_cross_junction() -> None:
    assert cross_junctions(cells_from_mask(("###", "###", "###"))) == ()


def test_cross_center_and_arm_occlusion_are_stable() -> None:
    cells = cells_from_mask(CROSS_MASK)
    assert section_occluders(cells, Point(4, 4)) == frozenset()
    for point in (Point(4, 2), Point(4, 3), Point(4, 5), Point(4, 6)):
        assert section_occluders(cells, point) == frozenset({"west"})
    for x in (1, 2, 3, 5, 6, 7, 8):
        assert section_occluders(cells, Point(x, 4)) == frozenset({"south"})
    assert section_occluders(cells, Point(0, 4)) == frozenset({"south", "west"})


def test_cross_literal_draft_is_stable_for_review() -> None:
    assert render_irregular_room(cells_from_mask(CROSS_MASK)) == LITERAL_DRAFT
