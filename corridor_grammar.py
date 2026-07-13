"""Corridor-aware entry point preserving the approved literal composition."""
from __future__ import annotations

from irregular_room_grammar import render_irregular_room as _render_irregular_room
from style_sample_system_v2_base import Point


def render_irregular_room(cells: frozenset[Point]) -> tuple[str, ...]:
    """Render rooms without repainting classified horizontal corridors.

    Horizontal corridors remain semantically distinct in ``junction_grammar_v2``,
    but their approved visual treatment intentionally reuses the hanging
    ``‘/___.../`` junction face produced by the irregular-room compositor.
    """
    return _render_irregular_room(cells)
