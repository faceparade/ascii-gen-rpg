#!/usr/bin/env python3
"""
Geometry primitives for the modular ASCII dungeon system.

This module defines lightweight dataclasses for describing logical structure:
- RoomSpec: overall room footprint in chunks/grid
- WallSpan: a run of wall chunks on a given side
- PortSpec: where a connector can attach (which chunks it spans)
- ChunkGrid: helper to convert chunk coordinates to glyph coordinates

These are intentionally pure data; they know nothing about rendering or skins.
Rendering happens elsewhere by combining geometry with skins and a canvas.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class RoomSpec:
    """Logical footprint of a room in chunks (not glyphs)."""
    width_chunks: int
    height_chunks: int  # interior floor rows (does not count walls/roof/foundation)


@dataclass(frozen=True)
class WallSpan:
    """A contiguous run of wall chunks on a given side of a room."""
    side: str  # one of: "north", "south", "east", "west"
    start_chunk: int  # 1-indexed, inclusive
    length_chunks: int  # number of chunks

    @property
    def end_chunk(self) -> int:
        return self.start_chunk + self.length_chunks - 1

    def contains(self, chunk: int) -> bool:
        return self.start_chunk <= chunk <= self.end_chunk


@dataclass(frozen=True)
class PortSpec:
    """Describes where a connector can attach to a wall."""
    side: str  # which wall side
    start_chunk: int  # inclusive, 1-indexed
    end_chunk: int   # inclusive, 1-indexed

    @property
    def length_chunks(self) -> int:
        return self.end_chunk - self.start_chunk + 1

    def overlaps(self, other: "PortSpec") -> bool:
        if self.side != other.side:
            return False
        return not (self.end_chunk < other.start_chunk or other.end_chunk < self.start_chunk)


@dataclass(frozen=True)
class ChunkGrid:
    """Knows how to convert chunk coordinates to glyph coordinates for a given style."""
    chunks_wide: int
    chunks_high: int
    chunk_glyph_w: int = 4
    chunk_glyph_h: int = 1  # rows per chunk layer (can vary by part)

    # Style-specific row offsets (how many glyph rows per logical chunk row for different parts)
    north_wall_top_glyph_rows_per_chunk: int = 1
    north_wall_top_extra_glyph_cols: int = 1   # +1 for terminal cap column
    north_wall_underside_glyph_rows_per_chunk: int = 1
    north_wall_underside_extra_glyph_cols: int = 2  # +2 (leading , plus space/west_west_side_glyph_cols_per_chunk: int = 2  # e.g. ,— and —-
    east_side_glyph_cols_per_chunk: int = 2  # similar
    floor_glyph_cols_per_chunk: int = 4
    floor_glyph_rows_per_chunk: int = 1

    def chunk_to_glyph_span(self, start_chunk: int, length_chunks: int) -> tuple[int, int]:
        """Convert a chunk range [start, start+length) to inclusive glyph column range [x0, x1]."""
        # Assumes origin at chunk (1,1) maps to glyph (0,0) before side offsets
        # This is a simplified placeholder; real conversion depends on which wall/side.
        # For now we just use the north wall conversion as an example.
        glyph_width = length_chunks * self.chunk_glyph_w + self.north_wall_top_extra_glyph_cols
        x0 = (start_chunk - 1) * self.chunk_glyph_w
        x1 = x0 + glyph_width - 1
        return x0, x1

    def north_wall_top_width(self, chunks: int) -> int:
        return chunks * self.chunk_glyph_w + self.north_wall_top_extra_glyph_cols

    def north_wall_underside_width(self, chunks: int) -> int:
        return chunks * self.chunk_glyph_w + self.north_wall_underside_extra_glyph_cols