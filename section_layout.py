#!/usr/bin/env python3
"""Logical section-domain specs for the corrected room/corridor/enclosure system."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple


def _positive(name: str, value: int) -> None:
    if value < 1:
        raise ValueError(f"{name} must be >= 1, got {value}")


def _nonoverlapping_openings(
    openings: Tuple["DoorwaySpec", ...], length: int
) -> None:
    seen: list[tuple[str, int, int]] = []
    for opening in openings:
        for side, start, end in seen:
            if side == opening.side and not (
                opening.end_section < start or opening.start_section > end
            ):
                raise ValueError(
                    f"overlapping doorway sections on {opening.side}: "
                    f"({opening.start_section}, {opening.end_section}) and ({start}, {end})"
                )
        seen.append(
            (opening.side, opening.start_section, opening.end_section)
        )


@dataclass(frozen=True)
class DoorwaySpec:
    """A wall section that is replaced by an opening."""

    side: Literal["north", "south", "east", "west"]
    offset_sections: int
    span_sections: int = 1

    def __post_init__(self) -> None:
        _positive("DoorwaySpec.offset_sections", self.offset_sections)
        _positive("DoorwaySpec.span_sections", self.span_sections)

    @property
    def start_section(self) -> int:
        return self.offset_sections

    @property
    def end_section(self) -> int:
        return self.offset_sections + self.span_sections - 1


@dataclass(frozen=True)
class InteriorEnclosureSpec:
    """A closed interior enclosure inside a room."""

    x_sections: int
    y_sections: int
    width_sections: int
    height_sections: int
    openings: Tuple[DoorwaySpec, ...] = ()
    style: Literal["raised_floor", "interior_wall"] = "raised_floor"

    def __post_init__(self) -> None:
        _positive("InteriorEnclosureSpec.x_sections", self.x_sections)
        _positive("InteriorEnclosureSpec.y_sections", self.y_sections)
        _positive("InteriorEnclosureSpec.width_sections", self.width_sections)
        _positive("InteriorEnclosureSpec.height_sections", self.height_sections)
        if self.openings:
            raise ValueError("interior enclosure openings must be empty for the locked proof scene")
        _nonoverlapping_openings(self.openings, max(self.width_sections, self.height_sections))


@dataclass(frozen=True)
class RoomModuleSpec:
    """A standalone room described in logical wall sections."""

    room_id: str
    width_sections: int
    height_sections: int
    openings: Tuple[DoorwaySpec, ...] = ()
    interiors: Tuple[InteriorEnclosureSpec, ...] = ()

    def __post_init__(self) -> None:
        _positive("RoomModuleSpec.width_sections", self.width_sections)
        _positive("RoomModuleSpec.height_sections", self.height_sections)
        _nonoverlapping_openings(self.openings, self.width_sections if any(
            opening.side in {"north", "south"} for opening in self.openings
        ) else self.height_sections)
        if not self.room_id:
            raise ValueError("RoomModuleSpec.room_id must not be empty")


@dataclass(frozen=True)
class CorridorModuleSpec:
    """A length-parameterized east/west corridor connecting two rooms."""

    from_room: str
    from_side: Literal["east", "west"]
    from_offset_sections: int
    to_room: str
    to_side: Literal["east", "west"]
    to_offset_sections: int
    length_sections: int

    def __post_init__(self) -> None:
        if self.from_side == self.to_side:
            raise ValueError(
                f"corridor endpoints must face opposite sides, got {self.from_side} and {self.to_side}"
            )
        _positive("CorridorModuleSpec.length_sections", self.length_sections)
        _positive("CorridorModuleSpec.from_offset_sections", self.from_offset_sections)
        _positive("CorridorModuleSpec.to_offset_sections", self.to_offset_sections)
