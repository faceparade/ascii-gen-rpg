"""Directional boundary-run renderer for Grammar v2 irregular rooms."""
from __future__ import annotations

from typing import Iterable

from style_sample_system_v2_base import (
    ACTOR_ORIGIN_X,
    ACTOR_ORIGIN_Y,
    SECTION_STRIDE_X,
    SECTION_STRIDE_Y,
    BoundaryEdge,
    Direction,
    LayeredCanvas,
    Point,
    boundary_edges,
    cell_bounds,
    lattice_points,
)


def _contiguous_runs(values: Iterable[int]) -> tuple[tuple[int, int], ...]:
    ordered = sorted(set(values))
    if not ordered:
        return ()
    runs: list[tuple[int, int]] = []
    run_start = previous = ordered[0]
    for value in ordered[1:]:
        if value != previous + 1:
            runs.append((run_start, previous))
            run_start = value
        previous = value
    runs.append((run_start, previous))
    return tuple(runs)


def directional_runs(cells: frozenset[Point], direction: Direction) -> tuple[tuple[int, int, int], ...]:
    """Group exposed edges into straight logical boundary runs."""
    edges = tuple(edge for edge in boundary_edges(cells) if edge.direction == direction)
    groups: dict[int, list[int]] = {}
    if direction in {"north", "south"}:
        for edge in edges:
            boundary = edge.section.y if direction == "north" else edge.section.y + 1
            groups.setdefault(boundary, []).append(edge.section.x)
    else:
        for edge in edges:
            boundary = edge.section.x if direction == "west" else edge.section.x + 1
            groups.setdefault(boundary, []).append(edge.section.y)
    return tuple(
        (boundary, start, end)
        for boundary in sorted(groups)
        for start, end in _contiguous_runs(groups[boundary])
    )


def _put(canvas: LayeredCanvas, layer: str, x: int, y: int, glyph: str) -> None:
    if glyph != " ":
        canvas.put(layer, Point(x, y), glyph)


def _render_north_run(canvas: LayeredCanvas, boundary_y: int, start_x: int, end_x: int) -> None:
    layer = "background_wall"
    y = boundary_y * SECTION_STRIDE_Y
    screen_start = ACTOR_ORIGIN_X + start_x * SECTION_STRIDE_X
    screen_end = ACTOR_ORIGIN_X + (end_x + 1) * SECTION_STRIDE_X

    for logical_x in range(start_x, end_x + 1):
        x = ACTOR_ORIGIN_X + logical_x * SECTION_STRIDE_X
        _put(canvas, layer, x, y, ",")
        _put(canvas, layer, x + 1, y, "—")
        _put(canvas, layer, x + 3, y, "—")
    _put(canvas, layer, screen_end, y, ",")

    _put(canvas, layer, screen_start - 1, y + 1, "/")
    _put(canvas, layer, screen_start, y + 1, "|")
    for logical_x in range(start_x, end_x + 1):
        x = ACTOR_ORIGIN_X + logical_x * SECTION_STRIDE_X
        underscore_start = x + 1 if logical_x == start_x else x
        for screen_x in range(underscore_start, x + 3):
            _put(canvas, layer, screen_x, y + 1, "_")
        _put(canvas, layer, x + 3, y + 1, "/")
    _put(canvas, layer, screen_end, y + 1, "|")


def _render_west_run(canvas: LayeredCanvas, boundary_x: int, start_y: int, end_y: int) -> None:
    layer = "foreground_wall"
    inner_x = ACTOR_ORIGIN_X + boundary_x * SECTION_STRIDE_X
    face_x = inner_x - 1
    outer_x = inner_x - 2
    for logical_y in range(start_y, end_y + 1):
        actor_y = ACTOR_ORIGIN_Y + logical_y * SECTION_STRIDE_Y
        _put(canvas, layer, outer_x, actor_y, "‘" if logical_y == start_y else "|")
        _put(canvas, layer, inner_x, actor_y, "|")
        if logical_y < end_y:
            _put(canvas, layer, outer_x, actor_y + 1, "|")
            _put(canvas, layer, face_x, actor_y + 1, "/")
            _put(canvas, layer, inner_x, actor_y + 1, "|")


def _render_east_run(
    canvas: LayeredCanvas,
    cells: frozenset[Point],
    boundary_x: int,
    start_y: int,
    end_y: int,
) -> None:
    layer = "background_wall"
    inner_x = boundary_x * SECTION_STRIDE_X
    face_x = inner_x + 1
    outer_x = inner_x + 2
    starts_below_floor = (
        Point(boundary_x - 1, start_y - 1) in cells
        and Point(boundary_x, start_y - 1) in cells
    )
    for logical_y in range(start_y, end_y + 1):
        actor_y = ACTOR_ORIGIN_Y + logical_y * SECTION_STRIDE_Y
        first_glyph = "‘" if logical_y == start_y and starts_below_floor else "|"
        _put(canvas, layer, inner_x, actor_y, first_glyph)
        _put(canvas, layer, outer_x, actor_y, "|")
        if logical_y < end_y:
            _put(canvas, layer, inner_x, actor_y + 1, "|")
            _put(canvas, layer, face_x, actor_y + 1, "/")
            _put(canvas, layer, outer_x, actor_y + 1, "|")


def _render_south_run(
    canvas: LayeredCanvas,
    cells: frozenset[Point],
    boundary_y: int,
    start_x: int,
    end_x: int,
) -> None:
    layer = "foreground_wall"
    edges = boundary_edges(cells)
    y = boundary_y * SECTION_STRIDE_Y
    screen_start = ACTOR_ORIGIN_X + start_x * SECTION_STRIDE_X
    screen_end = ACTOR_ORIGIN_X + (end_x + 1) * SECTION_STRIDE_X

    for logical_x in range(start_x, end_x + 1):
        x = ACTOR_ORIGIN_X + logical_x * SECTION_STRIDE_X
        _put(canvas, layer, x, y, ",")
        _put(canvas, layer, x + 1, y, "—")
        _put(canvas, layer, x + 3, y, "—")
    _put(canvas, layer, screen_end, y, ",")

    if BoundaryEdge(Point(end_x, boundary_y - 1), "east") in edges:
        _put(canvas, layer, screen_end - 2, y, "‘")

    start_section = Point(start_x, boundary_y - 1)
    starts_at_west_exterior = BoundaryEdge(start_section, "west") in edges
    if starts_at_west_exterior:
        _put(canvas, layer, screen_start - 2, y + 1, "‘")
        _put(canvas, layer, screen_start - 1, y + 1, "/")
        for logical_x in range(start_x, end_x + 1):
            x = ACTOR_ORIGIN_X + logical_x * SECTION_STRIDE_X
            for screen_x in range(x, x + 3):
                _put(canvas, layer, screen_x, y + 1, "_")
            _put(canvas, layer, x + 3, y + 1, "/")
    else:
        _put(canvas, layer, screen_start - 1, y + 1, "/")
        _put(canvas, layer, screen_start, y + 1, "|")
        for logical_x in range(start_x, end_x + 1):
            x = ACTOR_ORIGIN_X + logical_x * SECTION_STRIDE_X
            underscore_start = x + 1 if logical_x == start_x else x
            for screen_x in range(underscore_start, x + 3):
                _put(canvas, layer, screen_x, y + 1, "_")
            _put(canvas, layer, x + 3, y + 1, "/")


def render_irregular_room(cells: frozenset[Point]) -> tuple[str, ...]:
    """Render an irregular room from Grammar v2 directional boundary runs."""
    width_cells, height_cells = cell_bounds(cells)
    canvas = LayeredCanvas(
        width_cells * SECTION_STRIDE_X + 3,
        height_cells * SECTION_STRIDE_Y + 2,
    )

    for point in lattice_points(cells):
        canvas.put("lattice", point, "`")
    for boundary_y, start_x, end_x in directional_runs(cells, "north"):
        _render_north_run(canvas, boundary_y, start_x, end_x)
    for boundary_x, start_y, end_y in directional_runs(cells, "east"):
        _render_east_run(canvas, cells, boundary_x, start_y, end_y)
    for boundary_x, start_y, end_y in directional_runs(cells, "west"):
        _render_west_run(canvas, boundary_x, start_y, end_y)
    for boundary_y, start_x, end_x in directional_runs(cells, "south"):
        _render_south_run(canvas, cells, boundary_y, start_x, end_x)

    return canvas.compose()
