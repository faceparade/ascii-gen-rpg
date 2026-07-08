#!/usr/bin/env python3
"""Reusable connector placement specs for the ASCII dungeon grammar.

These are data/geometry helpers only: they map room-local connector choices
(chunk openings, room origin, optional visible upper fragments) into global
canvas regions. Rendering remains in the caller-specific modules.
"""
from __future__ import annotations

from dataclasses import dataclass

from modular_ascii_parts import CHUNK_GLYPH_W, Opening, NorthWall, north_wall_underside_width


@dataclass(frozen=True)
class NorthConnectorSpec:
    """Room-local north connector placement resolved into global glyph regions.

    ``opening`` is chunk-based and room-local. ``upper_rows`` stores optional
    visible rows north of the room as ``(room_local_x, row_text)`` pairs; the
    first row's x offset defines the upper-fragment origin used by annotations.
    """

    name: str
    room_x: int
    room_y: int
    room_chunks: int
    opening: Opening
    upper_rows: tuple[tuple[int, str], ...] = ()

    @classmethod
    def from_opening_preset(
        cls,
        name: str,
        *,
        room_x: int,
        room_y: int,
        room_chunks: int = 8,
        upper_rows: tuple[tuple[int, str], ...] = (),
    ) -> "NorthConnectorSpec":
        """Build a north connector spec from ``presets.NORTH_OPENING_PRESETS``."""
        from presets import build_north_opening

        return cls(
            name=name,
            room_x=room_x,
            room_y=room_y,
            room_chunks=room_chunks,
            opening=build_north_opening(name),
            upper_rows=upper_rows,
        )

    def validate(self) -> None:
        """Validate the opening against the supported NorthWall grammar."""
        NorthWall(self.room_chunks, (self.opening,))

    @property
    def opening_start_x(self) -> int:
        return self.room_x + (self.opening.start_chunk - 1) * CHUNK_GLYPH_W

    @property
    def opening_window(self) -> tuple[int, int, int, int]:
        """Global ``(x, y, width, height)`` covering the north-wall opening carve."""
        width = self.opening.width_chunks * CHUNK_GLYPH_W + 1
        return (self.opening_start_x, self.room_y, width, 2)

    @property
    def north_wall_region(self) -> tuple[int, int, int, int]:
        """Global ``(x, y, width, height)`` for the closed middle-shell north rows."""
        return (self.room_x, self.room_y, north_wall_underside_width(self.room_chunks), 2)

    @property
    def upper_fragment_y(self) -> int:
        return self.room_y - len(self.upper_rows)

    @property
    def upper_fragment_origin(self) -> tuple[int, int]:
        if not self.upper_rows:
            return (self.room_x, self.upper_fragment_y)
        first_x, _ = self.upper_rows[0]
        return (self.room_x + first_x, self.upper_fragment_y)
