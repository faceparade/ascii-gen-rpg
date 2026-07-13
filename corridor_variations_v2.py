"""Generalized corridor-band topology for Grammar v2.

The promoted one-section corridor junctions remain valid. This module adds the
geometry needed to describe passages that are wider than one logical section,
openings that are not centered in the adjoining room walls, and straight
passages whose adjoining rooms have different horizontal or vertical origins.
"""
from __future__ import annotations

from dataclasses import dataclass

from irregular_room_grammar import directional_runs
from style_sample_system_v2_base import Point


@dataclass(frozen=True, order=True)
class HorizontalCorridorBand:
    """A rectangular east-west passage between two room walls."""

    start_x: int
    end_x: int
    start_y: int
    end_y: int
    left_top_margin: int
    left_bottom_margin: int
    right_top_margin: int
    right_bottom_margin: int

    @property
    def length(self) -> int:
        return self.end_x - self.start_x + 1

    @property
    def thickness(self) -> int:
        return self.end_y - self.start_y + 1

    @property
    def is_centered(self) -> bool:
        return (
            self.left_top_margin == self.left_bottom_margin
            and self.right_top_margin == self.right_bottom_margin
        )

    @property
    def is_offset(self) -> bool:
        return not self.is_centered


@dataclass(frozen=True, order=True)
class VerticalCorridorBand:
    """A rectangular north-south passage between two room walls."""

    start_x: int
    end_x: int
    start_y: int
    end_y: int
    top_left_margin: int
    top_right_margin: int
    bottom_left_margin: int
    bottom_right_margin: int

    @property
    def thickness(self) -> int:
        return self.end_x - self.start_x + 1

    @property
    def length(self) -> int:
        return self.end_y - self.start_y + 1

    @property
    def is_centered(self) -> bool:
        return (
            self.top_left_margin == self.top_right_margin
            and self.bottom_left_margin == self.bottom_right_margin
        )

    @property
    def is_offset(self) -> bool:
        return not self.is_centered

    @property
    def room_shift_x(self) -> int:
        """Horizontal shift of the lower room relative to the upper room.

        Positive values mean the lower room begins farther east. A straight
        corridor may therefore occupy one fixed x column while having different
        relative opening positions in the two room walls.
        """
        return self.top_left_margin - self.bottom_left_margin

    @property
    def rooms_are_horizontally_aligned(self) -> bool:
        return self.room_shift_x == 0

    @property
    def opening_margins_match(self) -> bool:
        return (
            self.top_left_margin == self.bottom_left_margin
            and self.top_right_margin == self.bottom_right_margin
        )


def _vertical_extent(cells: frozenset[Point], x: int, start_y: int, end_y: int) -> tuple[int, int]:
    minimum = start_y
    maximum = end_y
    while Point(x, minimum - 1) in cells:
        minimum -= 1
    while Point(x, maximum + 1) in cells:
        maximum += 1
    return minimum, maximum


def _horizontal_extent(cells: frozenset[Point], y: int, start_x: int, end_x: int) -> tuple[int, int]:
    minimum = start_x
    maximum = end_x
    while Point(minimum - 1, y) in cells:
        minimum -= 1
    while Point(maximum + 1, y) in cells:
        maximum += 1
    return minimum, maximum


def horizontal_corridor_bands(cells: frozenset[Point]) -> tuple[HorizontalCorridorBand, ...]:
    """Return rectangular east-west passages, including multi-row passages."""
    south_runs = tuple(directional_runs(cells, "south"))
    result: list[HorizontalCorridorBand] = []

    for top_y, start_x, end_x in directional_runs(cells, "north"):
        if top_y == 0 or start_x == 0:
            continue
        for bottom_boundary, south_start, south_end in south_runs:
            if (south_start, south_end) != (start_x, end_x) or bottom_boundary <= top_y:
                continue
            end_y = bottom_boundary - 1
            corridor = {
                Point(x, y)
                for y in range(top_y, end_y + 1)
                for x in range(start_x, end_x + 1)
            }
            if not corridor.issubset(cells):
                continue
            if not all(
                Point(start_x - 1, y) in cells and Point(end_x + 1, y) in cells
                for y in range(top_y, end_y + 1)
            ):
                continue
            if not all(
                Point(x, top_y - 1) not in cells and Point(x, end_y + 1) not in cells
                for x in range(start_x, end_x + 1)
            ):
                continue
            if not all(
                point in cells
                for point in (
                    Point(start_x - 1, top_y - 1),
                    Point(end_x + 1, top_y - 1),
                    Point(start_x - 1, end_y + 1),
                    Point(end_x + 1, end_y + 1),
                )
            ):
                continue

            left_min, left_max = _vertical_extent(cells, start_x - 1, top_y, end_y)
            right_min, right_max = _vertical_extent(cells, end_x + 1, top_y, end_y)
            result.append(
                HorizontalCorridorBand(
                    start_x,
                    end_x,
                    top_y,
                    end_y,
                    top_y - left_min,
                    left_max - end_y,
                    top_y - right_min,
                    right_max - end_y,
                )
            )
            break

    return tuple(sorted(set(result)))


def vertical_corridor_bands(cells: frozenset[Point]) -> tuple[VerticalCorridorBand, ...]:
    """Return rectangular north-south passages, including shifted-room openings."""
    east_runs = tuple(directional_runs(cells, "east"))
    result: list[VerticalCorridorBand] = []

    for left_x, start_y, end_y in directional_runs(cells, "west"):
        if left_x == 0 or start_y == 0:
            continue
        for right_boundary, east_start, east_end in east_runs:
            if (east_start, east_end) != (start_y, end_y) or right_boundary <= left_x:
                continue
            end_x = right_boundary - 1
            corridor = {
                Point(x, y)
                for y in range(start_y, end_y + 1)
                for x in range(left_x, end_x + 1)
            }
            if not corridor.issubset(cells):
                continue
            if not all(
                Point(x, start_y - 1) in cells and Point(x, end_y + 1) in cells
                for x in range(left_x, end_x + 1)
            ):
                continue
            if not all(
                Point(left_x - 1, y) not in cells and Point(end_x + 1, y) not in cells
                for y in range(start_y, end_y + 1)
            ):
                continue
            if not all(
                point in cells
                for point in (
                    Point(left_x - 1, start_y - 1),
                    Point(end_x + 1, start_y - 1),
                    Point(left_x - 1, end_y + 1),
                    Point(end_x + 1, end_y + 1),
                )
            ):
                continue

            top_min, top_max = _horizontal_extent(cells, start_y - 1, left_x, end_x)
            bottom_min, bottom_max = _horizontal_extent(cells, end_y + 1, left_x, end_x)
            result.append(
                VerticalCorridorBand(
                    left_x,
                    end_x,
                    start_y,
                    end_y,
                    left_x - top_min,
                    top_max - end_x,
                    left_x - bottom_min,
                    bottom_max - end_x,
                )
            )
            break

    return tuple(sorted(set(result)))
