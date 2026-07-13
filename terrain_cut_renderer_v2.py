"""Manual-review renderer for sunken rooms cut into higher terrain.

The terrain rim is derived from the connected lower floor. A rendered boundary
exists only where a lower surface touches an explicitly higher surface. Missing
neighbors remain open by topology, so corridor exits at the edge of a crop are
never erased after rendering.
"""
from __future__ import annotations

from typing import Mapping

from style_sample_system_v2_base import (
    ACTOR_ORIGIN_X,
    ACTOR_ORIGIN_Y,
    SECTION_STRIDE_X,
    SECTION_STRIDE_Y,
    LayeredCanvas,
    Point,
    cell_bounds,
    lattice_points,
)
from terrain_cut_grammar_v2 import Direction, validate_terrain_scene

_OFFSETS: dict[Direction, tuple[int, int]] = {
    "north": (0, -1),
    "east": (1, 0),
    "south": (0, 1),
    "west": (-1, 0),
}


def _lower_cliff_boundaries(
    surface_cells: frozenset[Point],
    elevations: Mapping[Point, int],
    lower_cells: frozenset[Point],
) -> dict[Direction, frozenset[Point]]:
    """Return lower cells whose named side touches explicit higher terrain."""

    result: dict[Direction, set[Point]] = {direction: set() for direction in _OFFSETS}
    for lower in lower_cells:
        lower_height = elevations[lower]
        for direction, (dx, dy) in _OFFSETS.items():
            neighbor = Point(lower.x + dx, lower.y + dy)
            if neighbor in surface_cells and elevations[neighbor] > lower_height:
                result[direction].add(lower)
    return {direction: frozenset(points) for direction, points in result.items()}


def _draw_upper_crop_frame(canvas: LayeredCanvas, width_cells: int, height_cells: int) -> None:
    """Frame only the north and west edges of the continuing upper plane."""

    for column in range(width_cells):
        x = 2 + column * SECTION_STRIDE_X
        for offset, glyph in enumerate(",— —"):
            if glyph != " ":
                canvas.put("background_wall", Point(x + offset, 0), glyph)
    canvas.put("background_wall", Point(2 + width_cells * SECTION_STRIDE_X, 0), ",")

    canvas.put("background_wall", Point(1, 1), "/")
    canvas.put("background_wall", Point(2, 1), "|")
    for x in range(3, 2 + width_cells * SECTION_STRIDE_X):
        canvas.put("background_wall", Point(x, 1), "/" if (x - 1) % SECTION_STRIDE_X == 0 else "_")

    for row in range(height_cells):
        actor_y = ACTOR_ORIGIN_Y + row * SECTION_STRIDE_Y
        canvas.put("background_wall", Point(0, actor_y), "‘" if row == 0 else "|")
        canvas.put("background_wall", Point(2, actor_y), "|")
        if row < height_cells - 1:
            canvas.put("background_wall", Point(0, actor_y + 1), "|")
            canvas.put("background_wall", Point(1, actor_y + 1), "/")
            canvas.put("background_wall", Point(2, actor_y + 1), "|")


def _draw_cliff_boundaries(
    canvas: LayeredCanvas,
    boundaries: dict[Direction, frozenset[Point]],
) -> None:
    """Project one continuous lower-floor rim using directional cliff faces."""

    for cell in boundaries["north"]:
        x = 2 + cell.x * SECTION_STRIDE_X
        y = cell.y * SECTION_STRIDE_Y
        for offset, glyph in enumerate(",— —,"):
            if glyph != " ":
                canvas.put("background_wall", Point(x + offset, y), glyph)
        for offset, glyph in enumerate("/|__/"):
            if glyph != " ":
                canvas.put("background_wall", Point(x - 1 + offset, y + 1), glyph)

    for cell in boundaries["east"]:
        x = (cell.x + 1) * SECTION_STRIDE_X
        y = ACTOR_ORIGIN_Y + cell.y * SECTION_STRIDE_Y
        canvas.put("background_wall", Point(x, y), "|")
        canvas.put("background_wall", Point(x + 2, y), "|")
        canvas.put("background_wall", Point(x, y + 1), "|")
        canvas.put("background_wall", Point(x + 1, y + 1), "/")
        canvas.put("background_wall", Point(x + 2, y + 1), "|")

    for cell in boundaries["south"]:
        x = 2 + cell.x * SECTION_STRIDE_X
        y = ACTOR_ORIGIN_Y + cell.y * SECTION_STRIDE_Y
        for offset, glyph in enumerate(",— —,"):
            if glyph != " ":
                canvas.put("foreground_wall", Point(x + offset, y), glyph)
        for offset, glyph in enumerate("___/"):
            canvas.put("foreground_wall", Point(x + offset, y + 1), glyph)

    for cell in boundaries["west"]:
        x = ACTOR_ORIGIN_X + cell.x * SECTION_STRIDE_X
        y = ACTOR_ORIGIN_Y + cell.y * SECTION_STRIDE_Y
        canvas.put("foreground_wall", Point(x - 2, y), "‘" if cell.y == min(p.y for p in boundaries["west"]) else "|")
        canvas.put("foreground_wall", Point(x, y), "|")
        canvas.put("foreground_wall", Point(x - 2, y + 1), "|")
        canvas.put("foreground_wall", Point(x - 1, y + 1), "/")
        canvas.put("foreground_wall", Point(x, y + 1), "|")


def render_sunken_terrain(
    surface_cells: frozenset[Point],
    elevations: Mapping[Point, int],
    walkable_cells: frozenset[Point],
) -> tuple[str, ...]:
    """Render the initial level-1 terrain / level-0 recessed-floor treatment."""

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
    canvas = LayeredCanvas(width, height)

    _draw_upper_crop_frame(canvas, width_cells, height_cells)

    # Both planes retain their own lattice. Cliff layers overwrite a marker only
    # where a height transition physically occupies the same projected position.
    for marker in lattice_points(upper_cells) | lattice_points(walkable_cells):
        canvas.put("lattice", marker, "`")

    boundaries = _lower_cliff_boundaries(surface_cells, elevations, walkable_cells)
    _draw_cliff_boundaries(canvas, boundaries)
    return canvas.compose()
