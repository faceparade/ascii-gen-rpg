"""Doorway/corridor resolution layered over the approved irregular renderer."""
from __future__ import annotations

from irregular_room_grammar import render_irregular_room as _render_irregular_room
from junction_grammar_v2 import corridor_junctions
from style_sample_system_v2_base import (
    ACTOR_ORIGIN_X,
    SECTION_STRIDE_X,
    SECTION_STRIDE_Y,
    Point,
)


def _paint(canvas: list[list[str]], point: Point, glyph: str) -> None:
    canvas[point.y][point.x] = glyph


def _resolve_horizontal_corridor_north_wall(
    canvas: list[list[str]],
    boundary_y: int,
    start_x: int,
    end_x: int,
) -> None:
    """Keep the corridor's north wall behind the walkable passage.

    The generic U-bridge resolver correctly joins the upper side walls at the
    rim, but its hanging foreground underside is wrong when matching lower room
    walls prove that the span is a doorway corridor. Replace only that underside
    with the ordinary background north-wall face.
    """
    y = boundary_y * SECTION_STRIDE_Y
    screen_start = ACTOR_ORIGIN_X + start_x * SECTION_STRIDE_X
    screen_end = ACTOR_ORIGIN_X + (end_x + 1) * SECTION_STRIDE_X

    # Reassert the joined top rim. The right inner west wall uses the approved
    # curved termination established by the courtyard fixture.
    for screen_x in range(screen_start, screen_end + 1):
        _paint(canvas, Point(screen_x, y), " ")
    for logical_x in range(start_x, end_x + 1):
        x = ACTOR_ORIGIN_X + logical_x * SECTION_STRIDE_X
        _paint(canvas, Point(x, y), ",")
        _paint(canvas, Point(x + 1, y), "—")
        _paint(canvas, Point(x + 3, y), "—")
    _paint(canvas, Point(screen_end - 2, y), "‘")
    _paint(canvas, Point(screen_end, y), ",")

    # Ordinary north-wall underside: /|__ + /___ repeats + /| end.
    for screen_x in range(screen_start - 2, screen_end + 1):
        _paint(canvas, Point(screen_x, y + 1), " ")
    _paint(canvas, Point(screen_start - 1, y + 1), "/")
    _paint(canvas, Point(screen_start, y + 1), "|")
    for logical_x in range(start_x, end_x + 1):
        x = ACTOR_ORIGIN_X + logical_x * SECTION_STRIDE_X
        underscore_start = x + 1 if logical_x == start_x else x
        for screen_x in range(underscore_start, x + 3):
            _paint(canvas, Point(screen_x, y + 1), "_")
        _paint(canvas, Point(x + 3, y + 1), "/")
    _paint(canvas, Point(screen_end, y + 1), "|")


def render_irregular_room(cells: frozenset[Point]) -> tuple[str, ...]:
    rows = _render_irregular_room(cells)
    if not rows:
        return rows

    width = max(len(row) for row in rows)
    canvas = [list(row.ljust(width)) for row in rows]

    for junction in corridor_junctions(cells):
        _resolve_horizontal_corridor_north_wall(
            canvas,
            junction.boundary_y,
            junction.start_x,
            junction.end_x,
        )

    return tuple("".join(row).rstrip() for row in canvas)
