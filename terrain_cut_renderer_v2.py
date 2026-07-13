"""Manual-review renderer for the first sunken chamber/corridor treatment.

This checkpoint deliberately supports one visual concept: a rectangular lower
chamber whose center row continues east as an open corridor. The compositor
traces that connected lower cut as one rim. It does not render the surrounding
upper cells as separate room shells, and it never closes the corridor at the
crop edge.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from style_sample_system_v2_base import (
    ACTOR_ORIGIN_Y,
    SECTION_STRIDE_X,
    SECTION_STRIDE_Y,
    LayeredCanvas,
    Point,
    cell_bounds,
    lattice_points,
    lattice_vertices,
)
from terrain_cut_grammar_v2 import validate_terrain_scene


@dataclass(frozen=True)
class ChamberCorridorCut:
    min_x: int
    max_x: int
    min_y: int
    max_y: int
    corridor_y: int
    corridor_end_x: int

    @property
    def width(self) -> int:
        return self.max_x - self.min_x + 1

    @property
    def height(self) -> int:
        return self.max_y - self.min_y + 1


def _classify_chamber_corridor(
    surface_cells: frozenset[Point],
    lower_cells: frozenset[Point],
) -> ChamberCorridorCut:
    """Recognize the first approved 3-row chamber with an eastbound corridor."""

    min_x = min(point.x for point in lower_cells)
    min_y = min(point.y for point in lower_cells)
    max_y = max(point.y for point in lower_cells)
    if max_y - min_y + 1 != 3:
        raise NotImplementedError("initial cliff artwork requires a three-row chamber")

    row_bounds: dict[int, tuple[int, int]] = {}
    for y in range(min_y, max_y + 1):
        xs = sorted(point.x for point in lower_cells if point.y == y)
        if not xs or xs != list(range(xs[0], xs[-1] + 1)):
            raise NotImplementedError("initial cliff artwork requires contiguous lower rows")
        row_bounds[y] = (xs[0], xs[-1])

    corridor_y = min_y + 1
    top_bounds = row_bounds[min_y]
    middle_bounds = row_bounds[corridor_y]
    bottom_bounds = row_bounds[max_y]
    if top_bounds != bottom_bounds:
        raise NotImplementedError("initial cliff artwork requires matching chamber top and bottom rows")
    if top_bounds[0] != min_x or middle_bounds[0] != min_x:
        raise NotImplementedError("initial cliff artwork requires a shared west chamber wall")

    max_x = top_bounds[1]
    corridor_end_x = middle_bounds[1]
    if corridor_end_x <= max_x:
        raise NotImplementedError("initial cliff artwork requires an eastbound corridor")

    chamber = frozenset(
        Point(x, y)
        for y in range(min_y, max_y + 1)
        for x in range(min_x, max_x + 1)
    )
    corridor = frozenset(Point(x, corridor_y) for x in range(max_x + 1, corridor_end_x + 1))
    if lower_cells != chamber | corridor:
        raise NotImplementedError("lower topology is not the initial chamber/corridor fixture")

    surface_width, _ = cell_bounds(surface_cells)
    if corridor_end_x != surface_width - 1:
        raise NotImplementedError("initial corridor must remain open at the east crop boundary")

    return ChamberCorridorCut(min_x, max_x, min_y, max_y, corridor_y, corridor_end_x)


def _put_text(canvas: LayeredCanvas, layer: str, x: int, y: int, text: str) -> None:
    for offset, glyph in enumerate(text):
        if glyph != " ":
            canvas.put(layer, Point(x + offset, y), glyph)


def _continuous_rim(width: int, start: str, end: str | None) -> str:
    chars = [" " for _ in range(width + 1)]
    chars[0] = start
    for index in range(1, width):
        if index % 2 == 1:
            chars[index] = "—"
    if end is not None:
        chars[width] = end
    return "".join(chars)


def _bottom_face(section_count: int) -> str:
    return "‘/" + "___/" * section_count


def render_sunken_terrain(
    surface_cells: frozenset[Point],
    elevations: Mapping[Point, int],
    walkable_cells: frozenset[Point],
) -> tuple[str, ...]:
    """Render the manually reviewed level-1 exterior / level-0 cut fixture."""

    validate_terrain_scene(surface_cells, elevations, walkable_cells)
    heights = frozenset(elevations.values())
    if heights != {0, 1}:
        raise NotImplementedError("initial terrain-cut projection requires heights {0, 1}")
    if any(elevations[cell] != 0 for cell in walkable_cells):
        raise ValueError("initial terrain-cut projection requires walkable cells at level 0")

    upper_cells = frozenset(cell for cell in surface_cells if elevations[cell] == 1)
    if not upper_cells or not walkable_cells:
        raise ValueError("terrain-cut projection requires both upper and lower surfaces")

    cut = _classify_chamber_corridor(surface_cells, walkable_cells)
    surface_width, _ = cell_bounds(surface_cells)
    canvas = LayeredCanvas(surface_width * SECTION_STRIDE_X + 7, 13)

    chamber_left = 2 + cut.min_x * SECTION_STRIDE_X
    chamber_right = 2 + (cut.max_x + 1) * SECTION_STRIDE_X
    corridor_end = 2 + (cut.corridor_end_x + 1) * SECTION_STRIDE_X
    chamber_screen_width = chamber_right - chamber_left
    corridor_screen_width = corridor_end - chamber_right

    top_rim_y = cut.min_y * SECTION_STRIDE_Y
    corridor_top_y = ACTOR_ORIGIN_Y + cut.min_y * SECTION_STRIDE_Y
    corridor_bottom_y = ACTOR_ORIGIN_Y + cut.corridor_y * SECTION_STRIDE_Y
    bottom_rim_y = ACTOR_ORIGIN_Y + cut.max_y * SECTION_STRIDE_Y

    # Upper-plane lattice appears above and below the corridor strips. Its
    # placement is intentionally separated from the lower-floor lattice.
    for vertex in lattice_vertices(upper_cells):
        x = vertex.x * SECTION_STRIDE_X
        y = top_rim_y - 1 if vertex.y <= cut.corridor_y else bottom_rim_y + 2
        canvas.put("lattice", Point(x, y), "`")

    for marker in lattice_points(walkable_cells):
        canvas.put("lattice", marker, "`")

    # Chamber north rim and its recessed face.
    _put_text(
        canvas,
        "background_wall",
        chamber_left,
        top_rim_y,
        _continuous_rim(chamber_screen_width, ",", "."),
    )
    _put_text(canvas, "background_wall", chamber_left - 1, top_rim_y + 1, "/|")
    canvas.put("background_wall", Point(chamber_right, top_rim_y + 1), "|")

    # West foreground cliff, one continuous run through all chamber rows.
    for row_index, logical_y in enumerate(range(cut.min_y, cut.max_y + 1)):
        actor_y = ACTOR_ORIGIN_Y + logical_y * SECTION_STRIDE_Y
        _put_text(canvas, "foreground_wall", chamber_left - 2, actor_y, "‘ |" if row_index == 0 else "| |")
        if logical_y < cut.max_y:
            _put_text(canvas, "foreground_wall", chamber_left - 2, actor_y + 1, "|/|")

    # The chamber's east step creates the two corridor shoulders. Both runs are
    # intentionally open at the right edge; there is no terminal cap glyph.
    _put_text(canvas, "background_wall", chamber_right - 2, corridor_top_y + 1, "|/|")
    canvas.put("foreground_wall", Point(chamber_right, corridor_top_y), "|")
    _put_text(
        canvas,
        "foreground_wall",
        chamber_right + 2,
        corridor_top_y,
        _continuous_rim(corridor_screen_width - 2, "'", None),
    )

    _put_text(canvas, "foreground_wall", chamber_right - 2, corridor_bottom_y + 1, "|/|")
    canvas.put("foreground_wall", Point(chamber_right, corridor_bottom_y), "|")
    _put_text(
        canvas,
        "foreground_wall",
        chamber_right + 2,
        corridor_bottom_y,
        _continuous_rim(corridor_screen_width - 2, ",", None),
    )

    # Chamber south rim and one continuous hanging face.
    _put_text(
        canvas,
        "foreground_wall",
        chamber_left,
        bottom_rim_y,
        _continuous_rim(chamber_screen_width, "'", "'"),
    )
    _put_text(
        canvas,
        "foreground_wall",
        chamber_left - 1,
        bottom_rim_y + 1,
        _bottom_face(cut.width),
    )

    return canvas.compose()
