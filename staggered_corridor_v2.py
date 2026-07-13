"""Topology model for Grammar v2 staggered room openings.

A staggered corridor connects horizontal room walls at different x positions by
using two vertical stems and one horizontal jog. The path remains one logical
section thick even though its bounding box is wider than one section.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from style_sample_system_v2_base import Point, cell_bounds

DoglegDirection = Literal["eastward", "westward"]


@dataclass(frozen=True, order=True)
class StaggeredVerticalCorridor:
    """One-section corridor whose upper and lower openings are not aligned."""

    top_x: int
    bottom_x: int
    start_y: int
    bend_y: int
    end_y: int
    top_left_margin: int
    top_right_margin: int
    bottom_left_margin: int
    bottom_right_margin: int

    @property
    def direction(self) -> DoglegDirection:
        return "eastward" if self.bottom_x > self.top_x else "westward"

    @property
    def horizontal_shift(self) -> int:
        return abs(self.bottom_x - self.top_x)

    @property
    def path_length(self) -> int:
        return self.end_y - self.start_y + self.horizontal_shift + 1

    @property
    def path_cells(self) -> frozenset[Point]:
        left = min(self.top_x, self.bottom_x)
        right = max(self.top_x, self.bottom_x)
        return frozenset(
            {Point(self.top_x, y) for y in range(self.start_y, self.bend_y + 1)}
            | {Point(x, self.bend_y) for x in range(left, right + 1)}
            | {Point(self.bottom_x, y) for y in range(self.bend_y, self.end_y + 1)}
        )


def _horizontal_extent(cells: frozenset[Point], y: int, x: int) -> tuple[int, int]:
    minimum = maximum = x
    while Point(minimum - 1, y) in cells:
        minimum -= 1
    while Point(maximum + 1, y) in cells:
        maximum += 1
    return minimum, maximum


def staggered_vertical_corridors(
    cells: frozenset[Point],
) -> tuple[StaggeredVerticalCorridor, ...]:
    """Return one-section doglegs joining different positions on two room walls.

    The detector requires a one-cell upper stem, one horizontal bend row, and a
    one-cell lower stem. The occupied cells inside the corridor bounding box
    must match that path exactly, preventing solid rooms and wide rectangular
    passages from being classified as doglegs.
    """
    width, height = cell_bounds(cells)
    result: set[StaggeredVerticalCorridor] = set()

    for start_y in range(1, height - 2):
        for top_x in range(1, width - 1):
            if not {
                Point(top_x - 1, start_y - 1),
                Point(top_x, start_y - 1),
                Point(top_x + 1, start_y - 1),
                Point(top_x, start_y),
            }.issubset(cells):
                continue
            if Point(top_x - 1, start_y) in cells or Point(top_x + 1, start_y) in cells:
                continue

            for end_y in range(start_y + 2, height - 1):
                for bottom_x in range(1, width - 1):
                    if bottom_x == top_x:
                        continue
                    if not {
                        Point(bottom_x - 1, end_y + 1),
                        Point(bottom_x, end_y + 1),
                        Point(bottom_x + 1, end_y + 1),
                        Point(bottom_x, end_y),
                    }.issubset(cells):
                        continue
                    if Point(bottom_x - 1, end_y) in cells or Point(bottom_x + 1, end_y) in cells:
                        continue

                    left = min(top_x, bottom_x)
                    right = max(top_x, bottom_x)
                    box = {
                        Point(x, y)
                        for y in range(start_y, end_y + 1)
                        for x in range(left, right + 1)
                    }
                    actual = cells & box

                    for bend_y in range(start_y + 1, end_y):
                        candidate = StaggeredVerticalCorridor(
                            top_x,
                            bottom_x,
                            start_y,
                            bend_y,
                            end_y,
                            0,
                            0,
                            0,
                            0,
                        )
                        if actual != candidate.path_cells:
                            continue

                        top_min, top_max = _horizontal_extent(cells, start_y - 1, top_x)
                        bottom_min, bottom_max = _horizontal_extent(cells, end_y + 1, bottom_x)
                        result.add(
                            StaggeredVerticalCorridor(
                                top_x,
                                bottom_x,
                                start_y,
                                bend_y,
                                end_y,
                                top_x - top_min,
                                top_max - top_x,
                                bottom_x - bottom_min,
                                bottom_max - bottom_x,
                            )
                        )

    return tuple(sorted(result))
