from pathlib import Path

from style_sample_system import Point
from terrain_cut_renderer_v2 import render_sunken_terrain


SURFACE_CELLS = frozenset(Point(x, y) for y in range(5) for x in range(7))
LOWER_CELLS = frozenset(
    {Point(x, y) for y in range(1, 4) for x in range(1, 4)}
    | {Point(x, 2) for x in range(4, 7)}
)
ELEVATIONS = {point: (0 if point in LOWER_CELLS else 1) for point in SURFACE_CELLS}
REVIEW = Path("style_samples/review/sunken-corridor-chamber-cliff-art-v2.txt")


def _draft() -> tuple[str, ...]:
    return render_sunken_terrain(SURFACE_CELLS, ELEVATIONS, LOWER_CELLS)


def test_initial_terrain_cut_projection_stays_inside_surface_canvas() -> None:
    rows = _draft()
    assert rows
    assert len(rows) <= 12
    assert max(map(len, rows)) <= 31


def test_both_planes_retain_logical_lattice_markers() -> None:
    rows = _draft()
    assert sum(row.count("`") for row in rows) >= 4


def test_open_east_corridor_has_no_closing_face() -> None:
    rows = tuple(row.ljust(31) for row in _draft())
    east_exit_x = 28
    corridor_actor_y = 6
    corridor_lattice_y = 7
    for y in (corridor_actor_y, corridor_lattice_y):
        assert "|" not in rows[y][east_exit_x:31]
        assert "/" not in rows[y][east_exit_x:31]


def test_rejected_cliff_artwork_is_not_an_approved_golden_target() -> None:
    review_text = REVIEW.read_text(encoding="utf-8")
    assert "REJECTED" in review_text
    assert "Do not promote" in review_text
    assert "approved regression target" in review_text


def test_projection_is_deterministic_while_renderer_is_redesigned() -> None:
    assert _draft() == _draft()
