#!/usr/bin/env python3
"""Chunk-aware modular ASCII parts for Tristan's curved dungeon grammar.

This module is the first step away from raw hand-spliced text and toward
logical parts with explicit geometry. It intentionally starts small: the
8-chunk north wall used by the current room shells.

Refactored to drive opening cap glyphs through an OpeningSkin, separating
geometry from skin. The width math is preserved exactly from the earlier
passing version:

  solid top row width      = 4*chunks + 1
  solid underside width    = 4*chunks + 2
  opening top gap width    = 4*width_chunks + 1
  opening underside gap    = 4*width_chunks
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List

from opening_skin import OpeningSkin, plain_opening_skin
from modular_canvas import ModularCanvas, PasteMode, OPAQUE

CHUNK_GLYPH_W = 4


def north_wall_top_width(chunks: int) -> int:
    """Glyph width of the north-wall top row for N logical chunks."""
    return chunks * CHUNK_GLYPH_W + 1


def north_wall_underside_width(chunks: int) -> int:
    """Glyph width of the north-wall underside row for N logical chunks."""
    return chunks * CHUNK_GLYPH_W + 2


@dataclass(frozen=True)
class Opening:
    """A chunk-based opening in a wall.

    Chunks are 1-indexed because that matches visual/design discussion:
    an 8-chunk wall has chunks 1..8.
    """

    start_chunk: int
    width_chunks: int
    skin: 'OpeningSkin' = None  # defaults to plain later

    def __post_init__(self):
        if self.skin is None:
            object.__setattr__(self, "skin", plain_opening_skin())

    @property
    def end_chunk(self) -> int:
        return self.start_chunk + self.width_chunks - 1


@dataclass(frozen=True)
class NorthWall:
    """Parametric north wall rendered in the current curved room-shell style.

    The no-opening case must exactly match the bare locked 8-chunk north-wall rows:

        ,— -,— -,— -,— -,— -,— -,— -,— -.
        ,__/___/___/___/___/___/___/___/ |

    Openings are chunk-based rather than arbitrary character edits. The current
    opening skin is deliberately plain/structural: a `j` left cap on the top row,
    a `,t` right join, blank span between, and a `t` underside join.

    Important width rule: this style's top and underside rows are intentionally
    not rectangular. For N chunks, top width is `4N+1`; underside width is
    `4N+2`. Callers must preserve per-row widths instead of forcing one shared
    width too early.

    First-pass constraint: openings must have at least one intact wall chunk on
    both the west and east sides. Edge/full-wall openings are a different port
    grammar and are rejected until their cap rules are designed.
    """

    chunks: int = 8
    openings: Tuple[Opening, ...] = ()

    def __post_init__(self) -> None:
        if self.chunks < 1:
            raise ValueError("NorthWall.chunks must be >= 1")
        if len(self.openings) > 1:
            raise NotImplementedError(
                "NorthWall currently supports one opening; add splitting logic before multiple openings"
            )
        for opening in self.openings:
            if opening.start_chunk < 1:
                raise ValueError("Opening.start_chunk must be >= 1")
            if opening.width_chunks < 1:
                raise ValueError("Opening.width_chunks must be >= 1")
            if opening.end_chunk > self.chunks:
                raise ValueError("Opening extends past wall chunks")
            if opening.start_chunk == 1 or opening.end_chunk == self.chunks:
                raise NotImplementedError(
                    "NorthWall edge/full openings need their own cap grammar; "
                    "first-pass openings must leave at least one wall chunk on each side"
                )

    def _solid_top(self, chunks: int) -> str:
        # Bare NorthWall top is 4*chunks+1 wide. RoomShell closes the v3
        # middle box separately by replacing the final '.' with ',.'.
        return ",— -" * chunks + "."

    def _solid_underside(self, chunks: int) -> str:
        # Bare NorthWall underside starts open with ','; RoomShell closes the
        # left wall separately by replacing that first glyph with '|'.
        if chunks == 1:
            return ",__/ |"
        return ",__/" + "___/" * (chunks - 1) + " |"

    def _top_with_opening(self, opening: Opening) -> str:
        left_chunks = opening.start_chunk - 1
        right_chunks = self.chunks - opening.end_chunk

        left = ",— -" * left_chunks
        # Opening top gap is exactly 4*width_chunks + 1 glyphs wide for this style.
        gap_width = opening.width_chunks * CHUNK_GLYPH_W + 1
        gap = opening.skin.render_top_gap(gap_width)
        if right_chunks:
            right = "— -" + ",— -" * (right_chunks - 1) + "."
        else:
            right = "."
        return left + gap + right

    def _underside_with_opening(self, opening: Opening) -> str:
        left_chunks = opening.start_chunk - 1
        right_chunks = self.chunks - opening.end_chunk

        if left_chunks:
            left = ",__/" + "___/" * (left_chunks - 1)
        else:
            left = ""
        # Opening underside gap is exactly 4*width_chunks glyphs wide for this style.
        gap_width = opening.width_chunks * CHUNK_GLYPH_W
        gap = opening.skin.render_underside_gap(gap_width)
        if right_chunks:
            right = "___/" * right_chunks + " |"
        else:
            right = " |"
        return left + gap + right

    def render(self) -> List[str]:
        """Return [top_row, underside_row]."""
        if not self.openings:
            return [self._solid_top(self.chunks), self._solid_underside(self.chunks)]
        opening = self.openings[0]
        return [self._top_with_opening(opening), self._underside_with_opening(opening)]

    def draw_on(self, canvas: 'ModularCanvas', x: int, y: int, mode: 'PasteMode' = OPAQUE) -> None:
        """Draw the north wall onto the given canvas at the given top-left coordinate.

        Args:
            canvas: the ModularCanvas to draw on.
            x: left column (0-indexed) where the top row starts.
            y: top row (0-indexed) where the wall is drawn.
            mode: how to interact with existing content (default OPAQUE).
        """
        rows = self.render()
        canvas.paste_stamp([rows[0]], x, y, mode, source="north_wall", layer="wall")
        canvas.paste_stamp([rows[1]], x, y + 1, mode, source="north_wall", layer="wall")


def render_north_wall(chunks: int = 8, openings: Tuple[Opening, ...] = ()) -> List[str]:
    """Convenience wrapper for callers that do not need a NorthWall object."""
    return NorthWall(chunks=chunks, openings=openings).render()


def chunk_ruler(chunks: int) -> str:
    """Return a compact visual chunk ruler aligned to the north-wall top row."""
    labels = []
    for n in range(1, chunks + 1):
        text = str(n)
        labels.append(text.center(CHUNK_GLYPH_W))
    return "".join(labels) + " "