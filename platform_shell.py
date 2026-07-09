#!/usr/bin/env python3
"""Raised floor section shell for Tristan's curved dungeon grammar.

A raised floor section is treated as room-local shell geometry, not a decorative
prop.  Its visible wall vocabulary is the inverted counterpart of a normal
RoomShell:

* normal east wall  -> raised-section left face
* normal north wall -> raised-section bottom face
* normal west wall  -> raised-section right face
* normal south wall -> raised-section top rim

The current renderer is intentionally locked to the approved 4-unit art from
``six_rooms_two_platforms.txt`` and must reproduce
``curved_dungeon_grammar.raised_platform(4)`` byte-for-byte.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from curved_dungeon_grammar import raised_platform


@dataclass(frozen=True)
class PlatformShell:
    """Compatibility name for a room-local raised floor section shell.

    ``width_units=4`` is the only approved/locked width today.  The class exists
    so callers can depend on a shell abstraction now, while the glyph body stays
    byte-for-byte tied to the locked reference until more width variants are
    promoted into reusable stamps.
    """

    width_units: int = 4

    INVERTED_WALL_MAP: ClassVar[dict[str, str]] = {
        "east": "left_face",
        "north": "bottom_face",
        "west": "right_face",
        "south": "top_rim",
    }

    def render(self) -> list[str]:
        """Return the locked raised floor section rows as a rectangular stamp."""
        return raised_platform(self.width_units)

    @property
    def width(self) -> int:
        rows = self.render()
        return max(len(row) for row in rows)

    @property
    def height(self) -> int:
        return len(self.render())

    def face_for_room_wall(self, side: str) -> str:
        """Map a normal room wall side to the section's inverted visible face."""
        try:
            return self.INVERTED_WALL_MAP[side]
        except KeyError as exc:
            raise ValueError(f"unknown side {side!r}; expected east/north/west/south") from exc


RaisedFloorSection = PlatformShell
RaisedShell = PlatformShell
