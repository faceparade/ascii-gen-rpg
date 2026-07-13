from style_sample_system import Point
from terrain_cut_renderer_v2 import render_sunken_terrain


SURFACE_CELLS = frozenset(Point(x, y) for y in range(5) for x in range(7))
LOWER_CELLS = frozenset(
    {Point(x, y) for y in range(1, 4) for x in range(1, 4)}
    | {Point(x, 2) for x in range(4, 7)}
)
ELEVATIONS = {point: (0 if point in LOWER_CELLS else 1) for point in SURFACE_CELLS}


def _draft() -> tuple[str, ...]:
    return render_sunken_terrain(SURFACE_CELLS, ELEVATIONS, LOWER_CELLS)


def test_initial_terrain_cut_projection_stays_inside_surface_canvas() -> None:
    rows = _draft()
    assert rows
    assert len(rows) <= 12
    assert max(map(len, rows)) <= 31


def test_lower_plane_retains_its_logical_lattice() -> None:
    rows = _draft()
    assert sum(row.count("`") for row in rows) >= 4


def test_open_east_crop_does_not_gain_a_vertical_closing_pipe() -> None:
    rows = tuple(row.ljust(31) for row in _draft())
    # Level-1 terrain at the east crop edge has no explicit neighbor outside
    # the crop, so its actor/lattice rows must remain open rather than boxed.
    for y in (4, 5, 8, 9):
        assert rows[y][28:31] == "   "


def test_projection_is_deterministic() -> None:
    assert _draft() == _draft()
