from pathlib import Path

from enclosed_loop_grammar_v2 import enclosed_voids, rectangular_corridor_loops
from style_sample_system import Point, cells_from_mask, render_irregular_room


IRREGULAR_VOID_MASK = (
    "#######",
    "#...###",
    "#...###",
    "#.....#",
    "#.....#",
    "#######",
    "#######",
)


def approved_target() -> tuple[str, ...]:
    path = Path(__file__).parent / "style_samples" / "targets" / "room-irregular-enclosed-void-v2.txt"
    return tuple(path.read_text(encoding="utf-8").splitlines())


def test_irregular_void_is_enclosed_and_non_rectangular() -> None:
    cells = cells_from_mask(IRREGULAR_VOID_MASK)
    voids = enclosed_voids(cells)
    assert len(voids) == 1
    void = voids[0]
    assert (void.min_x, void.min_y, void.max_x, void.max_y) == (1, 1, 5, 4)
    assert len(void.cells) == 16
    rectangle = {
        Point(x, y)
        for y in range(void.min_y, void.max_y + 1)
        for x in range(void.min_x, void.max_x + 1)
    }
    assert void.cells != frozenset(rectangle)


def test_irregular_void_is_not_rectangular_loop() -> None:
    assert rectangular_corridor_loops(cells_from_mask(IRREGULAR_VOID_MASK)) == ()


def test_irregular_void_matches_approved_target_exactly() -> None:
    assert render_irregular_room(cells_from_mask(IRREGULAR_VOID_MASK)) == approved_target()
