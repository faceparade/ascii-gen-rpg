from enclosed_loop_grammar_v2 import enclosed_voids, rectangular_corridor_loops
from style_sample_system import Point, cells_from_mask, render_irregular_room, section_occluders


LOOP_MASK = (
    "#######",
    "#.....#",
    "#.....#",
    "#.....#",
    "#.....#",
    "#.....#",
    "#######",
)

LITERAL_DRAFT = (
    "  ,— —,— —,— —,— —,— —,— —,— —,",
    " /|__/___/___/___/___/___/___/|",
    "‘ |   ,— —,— —,— —,— —,— —, | |",
    "|/|  /|__/___/___/___/___/  |/|",
    "| | ‘ |                 ‘ | | |",
    "|/| |/|                 |/| |/|",
    "| | | |                 | | | |",
    "|/| |/|                 |/| |/|",
    "| | | |                 | | | |",
    "|/| |/|                 |/| |/|",
    "| | | |                 | | | |",
    "|/| |/|                 |/| |/|",
    "| | | ,— —,— —,— —,— —,—‘—, | |",
    "|/| ‘/___/___/___/___/___/  |/|",
    "| ,— —,— —,— —,— —,— —,— —,—‘—,",
    "‘/___/___/___/___/___/___/___/",
)


def test_loop_has_one_enclosed_rectangular_void() -> None:
    cells = cells_from_mask(LOOP_MASK)
    voids = enclosed_voids(cells)
    assert len(voids) == 1
    assert (voids[0].min_x, voids[0].min_y, voids[0].max_x, voids[0].max_y) == (1, 1, 5, 5)
    assert len(voids[0].cells) == 25


def test_loop_is_classified_as_one_section_thick_rectangular_ring() -> None:
    loops = rectangular_corridor_loops(cells_from_mask(LOOP_MASK))
    assert len(loops) == 1
    assert (loops[0].outer_min_x, loops[0].outer_min_y) == (0, 0)
    assert (loops[0].outer_max_x, loops[0].outer_max_y) == (6, 6)


def test_loop_representative_foreground_occlusion_is_directional() -> None:
    cells = cells_from_mask(LOOP_MASK)
    assert section_occluders(cells, Point(3, 0)) == frozenset({"south"})
    assert section_occluders(cells, Point(0, 3)) == frozenset({"west"})
    assert section_occluders(cells, Point(6, 3)) == frozenset({"west"})
    assert section_occluders(cells, Point(3, 6)) == frozenset({"south"})
    assert section_occluders(cells, Point(0, 6)) == frozenset({"south", "west"})


def test_loop_literal_rendering_is_stable_for_review() -> None:
    assert render_irregular_room(cells_from_mask(LOOP_MASK)) == LITERAL_DRAFT
