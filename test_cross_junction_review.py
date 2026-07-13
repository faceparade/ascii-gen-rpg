from pathlib import Path

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


def approved_target() -> tuple[str, ...]:
    path = Path(__file__).parent / "style_samples" / "targets" / "room-cross-junction-v2.txt"
    return tuple(path.read_text(encoding="utf-8").splitlines())


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


def test_cross_matches_approved_target_exactly() -> None:
    assert render_irregular_room(cells_from_mask(CROSS_MASK)) == approved_target()
