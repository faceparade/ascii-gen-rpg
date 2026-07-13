"""Projection compositor for Grammar v2 raised platforms."""
from __future__ import annotations

from typing import Mapping

from corridor_grammar import render_irregular_room
from raised_platform_grammar_v2 import PlatformEdge, RaisedPlatform, raised_platforms
from style_sample_system_v2_base import (
    SECTION_STRIDE_X,
    SECTION_STRIDE_Y,
    Point,
    cell_bounds,
    is_solid_rectangle,
    normalize_cells,
)


def platform_edge_layer(edge: PlatformEdge) -> str:
    """Return the semantic elevation layer for one exposed platform edge."""
    if edge.direction in {"north", "east"}:
        return "background_elevation_face"
    if edge.direction in {"south", "west"}:
        return "foreground_elevation_face"
    raise ValueError(f"unsupported platform direction: {edge.direction!r}")


def _ensure_canvas(rows: tuple[str, ...], width: int, height: int) -> list[list[str]]:
    canvas = [list(row.ljust(width)) for row in rows]
    canvas.extend([list(" " * width) for _ in range(height - len(canvas))])
    return canvas


def _overlay_rectangular_platform(
    canvas: list[list[str]],
    platform: RaisedPlatform,
) -> None:
    """Overlay one rectangular platform as a nested Grammar v2 shell.

    The platform shell is shifted by the platform's logical origin. Its north
    underside and south hanging face explicitly clear lower-floor lattice marks
    before their own glyphs are applied. This models the elevation face as an
    opaque layer rather than accidental punctuation over the base floor.
    """
    if not is_solid_rectangle(normalize_cells(platform.cells)):
        raise NotImplementedError("projection currently supports rectangular platforms only")

    min_x = min(point.x for point in platform.cells)
    min_y = min(point.y for point in platform.cells)
    local_cells = normalize_cells(platform.cells)
    shell = render_irregular_room(local_cells)
    offset_x = min_x * SECTION_STRIDE_X
    offset_y = min_y * SECTION_STRIDE_Y

    clear_rows = {1, len(shell) - 1}
    for local_y, row in enumerate(shell):
        target_y = offset_y + local_y
        if local_y in clear_rows:
            for local_x in range(len(row)):
                target_x = offset_x + local_x
                if 0 <= target_x < len(canvas[target_y]):
                    canvas[target_y][target_x] = " "
        for local_x, glyph in enumerate(row):
            if glyph == " ":
                continue
            target_x = offset_x + local_x
            if 0 <= target_x < len(canvas[target_y]):
                canvas[target_y][target_x] = glyph


def render_room_with_platforms(
    floor_cells: frozenset[Point],
    elevations: Mapping[Point, int],
) -> tuple[str, ...]:
    """Render a room plus all supported positive-elevation platform components."""
    base = render_irregular_room(floor_cells)
    platforms = raised_platforms(floor_cells, elevations)
    floor_width, floor_height = cell_bounds(floor_cells)
    width = floor_width * SECTION_STRIDE_X + 3
    height = floor_height * SECTION_STRIDE_Y + 2
    canvas = _ensure_canvas(base, width, height)

    for platform in platforms:
        _overlay_rectangular_platform(canvas, platform)

    rows = tuple("".join(row).rstrip() for row in canvas)
    while rows and not rows[-1]:
        rows = rows[:-1]
    return rows
