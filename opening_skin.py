#!/usr/bin/env python3
"""Opening skins for modular ASCII walls.

An OpeningSkin defines how to render the opening gap in a wall:
- top row: left cap + inner fill + right cap
- underside row: left prefix + inner fill + right cap

The wall itself provides the surrounding wall chunks (e.g., ,— - and ___/ runs).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OpeningSkin:
    """Skin for a wall opening.

    Attributes:
        top_left_cap: glyph(s) placed at the left edge of the opening on the top row.
        top_right_cap: glyph(s) placed at the right edge of the opening on the top row.
        top_inner_fill: fill string repeated to cover the horizontal gap between the caps.
        underside_left_prefix: glyph(s) placed immediately before the inner fill on the underside row.
        underside_right_cap: glyph(s) placed at the right edge of the opening on the underside row.
        underside_inner_fill: fill string repeated to cover the horizontal gap on the underside.
    """
    top_left_cap: str
    top_right_cap: str
    top_inner_fill: str = " "
    underside_left_prefix: str = ""
    underside_right_cap: str = "t"
    underside_inner_fill: str = " "

    def render_top_gap(self, total_width: int) -> str:
        """Render the top-row gap given the total glyph width of the opening."""
        left_len = len(self.top_left_cap)
        right_len = len(self.top_right_cap)
        if total_width < left_len + right_len:
            # Not enough space for both caps, fallback to left cap (truncated if needed)
            return self.top_left_cap[:total_width]
        inner_width = total_width - left_len - right_len
        if inner_width < 0:
            inner_width = 0
        return self.top_left_cap + self.top_inner_fill * inner_width + self.top_right_cap

    def _top_left_char(self) -> str:
        return self.top_left_cap

    def _top_right_char(self) -> str:
        return self.top_right_cap

    def render_underside_gap(self, total_width: int) -> str:
        """Render the underside-row gap given the total glyph width of the opening."""
        left_len = len(self.underside_left_prefix)
        right_len = len(self.underside_right_cap)
        if total_width < left_len + right_len:
            return self.underside_left_prefix[:total_width]
        inner_width = total_width - left_len - right_len
        if inner_width < 0:
            inner_width = 0
        return self.underside_left_prefix + self.underside_inner_fill * inner_width + self.underside_right_cap

    def _underside_left_char(self) -> str:
        return self.underside_left_prefix

    def _underside_right_char(self) -> str:
        return self.underside_right_cap


def plain_opening_skin() -> OpeningSkin:
    """The plain/structural opening skin used in the current experiments."""
    return OpeningSkin(
        top_left_cap="j",
        top_right_cap=",t",
        top_inner_fill=" ",
        underside_left_prefix="",
        underside_right_cap="t",
        underside_inner_fill=" ",
    )