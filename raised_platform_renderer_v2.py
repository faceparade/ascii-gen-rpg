"""Projection compositor for Grammar v2 raised platforms."""
from __future__ import annotations

from typing import Mapping

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


def _render_rectangular_platform_stamp(
    width_cells: int,
    height_cells: int,
) -> tuple[str, ...]:
    """Render a rectangular raised-floor stamp from locked rim/face macros."""
    if width_cells < 1 or height_cells < 1:
        raise ValueError("platform dimensions must be positive")

    visual_width = width_cells * SECTION_STRIDE_X + 3
    rows = ["  ," + "— " * (2 * width_cells - 1) + "—."]

    if height_cells == 1:
        side_prefixes = [" /|"]
    else:
        side_prefixes = [" /|", ", |"]
        for _ in range(height_cells - 2):
            side_prefixes.extend(("|/|", "| |"))
        side_prefixes.append("|/|")
    rows.extend(prefix + " " * (visual_width - 4) + "|" for prefix in side_prefixes)

    rows.append("| ‘" + "— —," * (width_cells - 1) + "— -,")
    underside = ["___"] * width_cells
    rows.append("‘" + "".join("/" + segment for segment in underside) + "/ ")

    if any(len(row) != visual_width for row in rows):
        raise AssertionError("raised-platform stamp rows must share one visual width")
    return tuple(rows)


def _overlay_rectangular_platform(
    canvas: list[list[str]],
    platform: RaisedPlatform,
) -> None:
    """Overlay a rebuilt rectangular raised-floor projection at its topology origin.

    The stamp uses the dedicated raised-floor rim and foreground-face vocabulary,
    rather than nesting a second room shell. Its bounding box is opaque so lower-
    floor lattice marks cannot show through the elevated footprint.
    """
    local_cells = normalize_cells(platform.cells)
    if not is_solid_rectangle(local_cells):
        raise NotImplementedError("projection currently supports rectangular platforms only")
    width_cells, height_cells = cell_bounds(local_cells)

    min_x = min(point.x for point in platform.cells)
    min_y = min(point.y for point in platform.cells)
    stamp = _render_rectangular_platform_stamp(width_cells, height_cells)
    offset_x = min_x * SECTION_STRIDE_X
    offset_y = min_y * SECTION_STRIDE_Y

    for local_y, row in enumerate(stamp):
        target_y = offset_y + local_y
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
    """Render positive-elevation platforms on an open lower-floor canvas."""
    platforms = raised_platforms(floor_cells, elevations)
    floor_width, floor_height = cell_bounds(floor_cells)
    width = floor_width * SECTION_STRIDE_X + 3
    height = floor_height * SECTION_STRIDE_Y + 2
    canvas = _ensure_canvas((), width, height)

    for platform in platforms:
        _overlay_rectangular_platform(canvas, platform)

    return tuple("".join(row) for row in canvas)
