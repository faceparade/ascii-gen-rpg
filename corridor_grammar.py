"""Final Grammar v2 room compositor and approved east-cap spacing."""
from __future__ import annotations

from irregular_room_grammar import render_irregular_room as _render_irregular_room
from style_sample_system_v2_base import Point


EAST_CAP_UNDERSIDE_SOURCE = "___/|"
EAST_CAP_UNDERSIDE_TARGET = "__ /|"


def _apply_east_cap_spacing(rows: tuple[str, ...]) -> tuple[str, ...]:
    """Reserve the recessed column before every east-face slash.

    Ordinary north-wall undersides and hanging faces that terminate directly
    into an east wall use ``/__ /|`` rather than ``/___/|``. South-wall faces
    are unaffected because they do not terminate in an east-wall pipe.
    """
    return tuple(
        row.replace(EAST_CAP_UNDERSIDE_SOURCE, EAST_CAP_UNDERSIDE_TARGET)
        for row in rows
    )


def render_irregular_room(cells: frozenset[Point]) -> tuple[str, ...]:
    """Render an irregular room and apply the approved recessed east cap."""
    return _apply_east_cap_spacing(_render_irregular_room(cells))
