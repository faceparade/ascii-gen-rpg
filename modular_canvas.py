#!/usr/bin/env python3
"""Modular canvas for ASCII dungeon composition with explicit paste modes and cell provenance.

This module provides a grid of Cell objects that can store a character and optional
metadata (source part, layer). It supports different paste strategies to control
how incoming glyphs interact with existing canvas content.

Paste modes:
- OPAQUE: overwrite everything, including spaces (used for solid stamps like rooms/platforms when silhouette matters)
- TRANSPARENT_SPACE: only overwrite non-space glyphs; spaces in the stamp leave existing content untouched (useful for connectors/overlays)
- CUT: replace the target area with spaces (used to create openings)
- OVERLAY: only overlay non-space glyphs, but also record provenance (similar to TRANSPARENT_SPACE but with metadata tracking)

Each cell can store:
- ch: the character displayed
- source: optional string identifying the part/macro that placed this character
- layer: optional string indicating the logical layer (e.g., "wall", "opening", "connector", "decor")

The canvas coordinates follow the same convention as elsewhere: x increases right, y increases down.
Origin (0,0) is top-left.

Example usage:
    canvas = ModularCanvas(width=20, height=10)
    stamp = ["  /|", " / |", "/  |"]
    canvas.paste_stamp(stamp, x=2, y=2, mode=PasteMode.TRANSPARENT_SPACE, source="r24_tail", layer="connector")
    lines = canvas.render_lines()
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional


class PasteMode(Enum):
    """How a stamp interacts with the existing canvas."""
    OPAQUE = auto()          # overwrite all cells, including spaces
    TRANSPARENT_SPACE = auto() # only overwrite non-space cells; spaces leave existing content
    CUT = auto()             # replace the stamped area with spaces (used for openings)
    OVERLAY = auto()         # like TRANSPARENT_SPACE but also records source/layer metadata


@dataclass
class Cell:
    """A single cell in the modular canvas."""
    ch: str = " "
    source: Optional[str] = None
    layer: Optional[str] = None

    def is_empty(self) -> bool:
        return self.ch == " " and self.source is None and self.layer is None

    def copy(self) -> "Cell":
        return Cell(ch=self.ch, source=self.source, layer=self.layer)


class ModularCanvas:
    """A grid of Cell objects with paste methods."""

    def __init__(self, width: int, height: int):
        if width < 1 or height < 1:
            raise ValueError("Canvas dimensions must be positive")
        self.width = width
        self.height = height
        self._grid: List[List[Cell]] = [[Cell() for _ in range(width)] for _ in range(height)]

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x: int, y: int) -> Cell:
        if not self._in_bounds(x, y):
            raise IndexError(f"Coordinates ({x}, {y}) out of bounds for canvas {self.width}x{self.height}")
        return self._grid[y][x]

    def set_cell(self, x: int, y: int, cell: Cell) -> None:
        if not self._in_bounds(x, y):
            raise IndexError(f"Coordinates ({x}, {y}) out of bounds for canvas {self.width}x{self.height}")
        self._grid[y][x] = cell

    def clear(self) -> None:
        """Reset all cells to empty."""
        for y in range(self.height):
            for x in range(self.width):
                self._grid[y][x] = Cell()

    def paste_stamp(
        self,
        stamp: List[str],
        x: int,
        y: int,
        mode: PasteMode,
        source: Optional[str] = None,
        layer: Optional[str] = None,
    ) -> None:
        """Paste a list of strings (stamp) onto the canvas starting at (x, y).

        Args:
            stamp: list of strings, each string is a row of the stamp.
            x: left column of the stamp (0-indexed).
            y: top row of the stamp (0-indexed).
            mode: how the stamp interacts with existing content.
            source: optional identifier for the source part/macro.
            layer: optional logical layer label.
        """
        if not stamp:
            return
        for dy, row in enumerate(stamp):
            ty = y + dy
            if ty < 0 or ty >= self.height:
                continue
            for dx, ch in enumerate(row):
                tx = x + dx
                if tx < 0 or tx >= self.width:
                    continue

                if mode == PasteMode.OPAQUE:
                    self.set_cell(tx, ty, Cell(ch=ch, source=source, layer=layer))
                elif mode == PasteMode.TRANSPARENT_SPACE:
                    if ch != " ":
                        self.set_cell(tx, ty, Cell(ch=ch, source=source, layer=layer))
                elif mode == PasteMode.CUT:
                    # Always replace with space, regardless of stamp content
                    self.set_cell(tx, ty, Cell())
                elif mode == PasteMode.OVERLAY:
                    if ch != " ":
                        self.set_cell(tx, ty, Cell(ch=ch, source=source, layer=layer))
                else:
                    raise ValueError(f"Unsupported paste mode: {mode}")

    def render_lines(self) -> List[str]:
        """Convert the canvas to a list of strings (rows), stripping trailing spaces."""
        lines = []
        for y in range(self.height):
            row_chars = [self._grid[y][x].ch for x in range(self.width)]
            line = "".join(row_chars).rstrip()
            lines.append(line)
        return lines

    def render_grid(self) -> List[List[Cell]]:
        """Return a deep copy of the internal grid (for inspection/testing)."""
        return [[cell.copy() for cell in row] for row in self._grid]

    def __str__(self) -> str:
        return "\n".join(self.render_lines())


# Convenience constants for common paste modes
OPAQUE = PasteMode.OPAQUE
TRANSPARENT_SPACE = PasteMode.TRANSPARENT_SPACE
CUT = PasteMode.CUT
OVERLAY = PasteMode.OVERLAY


if __name__ == "__main__":
    # Simple self-test
    canvas = ModularCanvas(10, 5)
    stamp = [
        "/--\\",
        "|  |",
        "\\--/"
    ]
    canvas.paste_stamp(stamp, x=2, y=1, mode=OPAQUE, source="box", layer="wall")
    print("OPAQUE paste:")
    print(canvas)
    print()

    canvas.clear()
    canvas.paste_stamp(stamp, x=2, y=1, mode=TRANSPARENT_SPACE, source="box", layer="wall")
    print("TRANSPARENT_SPACE paste:")
    print(canvas)
    print()

    # First put down a wall, then cut an opening
    canvas.clear()
    wall_stamp = [
        "---------",
        "|       |",
        "---------"
    ]
    canvas.paste_stamp(wall_stamp, x=0, y=0, mode=OPAQUE, source="wall", layer="wall")
    cut_stamp = [
        "   ",
        "   ",
        "   "
    ]
    canvas.paste_stamp(cut_stamp, x=3, y=1, mode=CUT, source="opening", layer="opening")
    print("Wall with cut opening:")
    print(canvas)