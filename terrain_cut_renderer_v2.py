"""Manual-review renderer for sunken rooms cut into higher terrain.

The initial treatment reuses the approved irregular-boundary grammar on the
upper terrain footprint. Boundaries adjacent to lower surfaces become cliff
rims/faces. South and east edges that leave the explicit review crop are
removed so continuing terrain is not boxed in.
"""
from __future__ import annotations

from typing import Mapping

from corridor_grammar import render_irregular_room
from style_sample_system_v2_base import (
    ACTOR_ORIGIN_Y,
    SECTION_STRIDE_X,
    SECTION_STRIDE_Y,
    Point,
    cell_bounds,
    lattice_points,
)
from terrain_cut_grammar_v2 import validate_terrain_scene


def _ensure_canvas(rows: tuple[str, ...], width: int, height: int) -> list[list[str]]:
    canvas = [list(row.ljust(width)) for row in rows]
    canvas.extend([list(" " * width) for _ in range(height - len(canvas))])
    return canvas


def _clear(canvas: list[list[str]], point: Point) -> None:
    if 0 <= point.y < len(canvas) and 0 <= point.x < len(canvas[point.y]):
        canvas[point.y][point.x] = " "


def _remove_open_crop_closures(
    canvas: list[list[str]],
    surface_cells: frozenset[Point],
    upper_cells: frozenset[Point],
) -> None:
    """Remove south/east outlines where terrain continues beyond the crop.

    North and west crop edges remain as orientation framing, matching the
    user-authored reference. Missing neighbors are never treated as cliffs.
    """

    for cell in upper_cells:
        east = Point(cell.x + 1, cell.y)
        if east not in surface_cells:
            x = (cell.x + 1) * SECTION_STRIDE_X
            y = ACTOR_ORIGIN_Y + cell.y * SECTION_STRIDE_Y
            for dy in (0, 1):
                for dx in (0, 1, 2):
                    _clear(canvas, Point(x + dx, y + dy))

        south = Point(cell.x, cell.y + 1)
        if south not in surface_cells:
            x = 2 + cell.x * SECTION_STRIDE_X
            y = ACTOR_ORIGIN_Y + cell.y * SECTION_STRIDE_Y
            for dx in range(5):
                _clear(canvas, Point(x + dx, y))
            for dx in range(4):
                _clear(canvas, Point(x + dx, y + 1))


def render_sunken_terrain(
    surface_cells: frozenset[Point],
    elevations: Mapping[Point, int],
    walkable_cells: frozenset[Point],
) -> tuple[str, ...]:
    """Render the first level-1 terrain / level-0 cut treatment.

    This checkpoint deliberately supports only a single upper height and a
    single lower height. More levels remain a later manual review.
    """

    validate_terrain_scene(surface_cells, elevations, walkable_cells)
    heights = frozenset(elevations.values())
    if heights != {0, 1}:
        raise NotImplementedError("initial terrain-cut projection requires heights {0, 1}")
    if any(elevations[cell] != 0 for cell in walkable_cells):
        raise ValueError("initial terrain-cut projection requires walkable cells at level 0")

    upper_cells = frozenset(cell for cell in surface_cells if elevations[cell] == 1)
    if not upper_cells or not walkable_cells:
        raise ValueError("terrain-cut projection requires both upper and lower surfaces")

    width_cells, height_cells = cell_bounds(surface_cells)
    width = width_cells * SECTION_STRIDE_X + 3
    height = height_cells * SECTION_STRIDE_Y + 2
    canvas = _ensure_canvas(render_irregular_room(upper_cells), width, height)

    _remove_open_crop_closures(canvas, surface_cells, upper_cells)

    # Lower-floor lattice remains tied to the logical walkable topology. It is
    # added only where the cliff compositor has left the lower plane visible.
    for marker in lattice_points(walkable_cells):
        if 0 <= marker.y < height and 0 <= marker.x < width and canvas[marker.y][marker.x] == " ":
            canvas[marker.y][marker.x] = "`"

    rows = tuple("".join(row).rstrip() for row in canvas)
    while rows and not rows[-1]:
        rows = rows[:-1]
    return rows
