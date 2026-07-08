#!/usr/bin/env python3
"""Wall-direction cap vocabulary for Tristan's curved dungeon grammar.

Phase B: a CapSkin describes, per wall side, the cap glyphs used where a
vertical opening meets that wall, plus the vertical inner fill. This gives one
vocabulary for all four wall directions (north/east/south/west) instead of
ad-hoc glyph math in each renderer.

The glyph choices follow the visual language already established by the north
opening (opening_skin.plain_opening_skin): the north opening uses a ``j``
top-left corner, a ``,t`` top-right join, and a ``t`` underside join. A west or
east opening is that same corner rotated 90 degrees, so its top and bottom caps
reuse those glyphs.

Note on the east top cap: a south/north opening spans several columns, so its
top-right join ``,t`` sits at the right *end* of a multi-column gap. A west/east
opening, by contrast, carves a single side-wall column, so its top cap must be a
single glyph. We use ``/`` for the east top cap because ``/`` already caps the
locked east wall (e.g. the ``     /|`` connector in room_shell_middle_8); this
keeps the corner vocabulary consistent with the existing reference art.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class CapSkin:
    """Cap vocabulary for a vertical (side-wall) opening on one wall side.

    Attributes:
        top_cap: glyph placed at the top of the opening on the side-wall column.
        bottom_cap: glyph placed at the bottom of the opening on the side-wall column.
        inner_fill: fill glyph for the vertical run between the caps.
    """

    top_cap: str
    bottom_cap: str
    inner_fill: str = " "


@dataclass(frozen=True)
class VerticalOpening:
    """A chunk-based vertical opening in a side wall.

    Rows are absolute shell-row indices (0 = north wall top). The opening
    carves the side-wall column across [start_row, start_row + height_chunks - 1].
    """

    start_row: int
    height_chunks: int
    skin: Optional[CapSkin] = None

    def __post_init__(self) -> None:
        if self.height_chunks < 1:
            raise ValueError("VerticalOpening.height_chunks must be >= 1")


def west_cap_skin() -> CapSkin:
    """West (left-column) opening: top corner ``j``, underside ``t``, blank inner."""
    return CapSkin(top_cap="j", bottom_cap="t", inner_fill=" ")


def east_cap_skin() -> CapSkin:
    """East (right-column) opening: top corner ``/`` (locked east-wall cap), ``t`` underside."""
    return CapSkin(top_cap="/", bottom_cap="t", inner_fill=" ")


def render_side_opening_column(side: str, start_row: int, height_chunks: int,
                               skin: CapSkin) -> List[str]:
    """Return the carved side-wall column glyphs for one opening.

    The result is a list of single-glyph strings, one per opened row, from
    ``start_row`` down to ``start_row + height_chunks - 1``:
      first row -> top_cap
      middle rows -> inner_fill
      last row  -> bottom_cap
    """
    if side not in ("west", "east"):
        raise ValueError(f"side {side!r} not supported; expected 'west' or 'east'")
    if height_chunks < 1:
        raise ValueError("height_chunks must be >= 1")
    glyphs: List[str] = []
    for k in range(height_chunks):
        if k == 0:
            glyphs.append(skin.top_cap)
        elif k == height_chunks - 1:
            glyphs.append(skin.bottom_cap)
        else:
            glyphs.append(skin.inner_fill)
    return glyphs
