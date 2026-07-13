"""Final Grammar v2 room compositor and approved east-cap spacing."""
from __future__ import annotations

from enclosed_loop_grammar_v2 import rectangular_corridor_loops
from irregular_room_grammar import render_irregular_room as _render_irregular_room
from style_sample_system_v2_base import ACTOR_ORIGIN_Y, SECTION_STRIDE_X, SECTION_STRIDE_Y, Point


EAST_CAP_UNDERSIDE_SOURCE = "___/|"
EAST_CAP_UNDERSIDE_TARGET = "__ /|"
EAST_CAP_RECESSED_FACE_SOURCE = "___/  |/|"
EAST_CAP_RECESSED_FACE_TARGET = "__ /  |/|"


def _apply_east_cap_spacing(rows: tuple[str, ...]) -> tuple[str, ...]:
    """Reserve the recessed column before every east-face slash.

    The pipe may be adjacent to the face slash or separated by the projected
    east-face depth. Ordinary south-wall faces remain unchanged.
    """
    return tuple(
        row.replace(EAST_CAP_RECESSED_FACE_SOURCE, EAST_CAP_RECESSED_FACE_TARGET)
        .replace(EAST_CAP_UNDERSIDE_SOURCE, EAST_CAP_UNDERSIDE_TARGET)
        for row in rows
    )


def _apply_rectangular_loop_inner_east_starts(
    rows: tuple[str, ...],
    cells: frozenset[Point],
) -> tuple[str, ...]:
    """Use a continuing pipe at the top of each enclosed loop's inner east wall."""
    loops = rectangular_corridor_loops(cells)
    if not loops:
        return rows
    canvas = [list(row) for row in rows]
    for loop in loops:
        x = (loop.void.max_x + 1) * SECTION_STRIDE_X
        y = ACTOR_ORIGIN_Y + loop.void.min_y * SECTION_STRIDE_Y
        if 0 <= y < len(canvas) and 0 <= x < len(canvas[y]):
            canvas[y][x] = "|"
    return tuple("".join(row).rstrip() for row in canvas)


def render_irregular_room(cells: frozenset[Point]) -> tuple[str, ...]:
    """Render a room and apply the approved terminal and loop-corner motifs."""
    rows = _apply_east_cap_spacing(_render_irregular_room(cells))
    return _apply_rectangular_loop_inner_east_starts(rows, cells)
