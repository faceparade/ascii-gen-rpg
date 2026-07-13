"""Topology model for Grammar v2 raised platforms."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Mapping

from style_sample_system_v2_base import Point


@dataclass(frozen=True, order=True)
class PlatformEdge:
    section: Point
    direction: str


@dataclass(frozen=True)
class RaisedPlatform:
    elevation: int
    cells: frozenset[Point]
    perimeter: frozenset[PlatformEdge]


def _perimeter(cells: frozenset[Point]) -> frozenset[PlatformEdge]:
    offsets = {
        "north": (0, -1),
        "east": (1, 0),
        "south": (0, 1),
        "west": (-1, 0),
    }
    return frozenset(
        PlatformEdge(section, direction)
        for section in cells
        for direction, (dx, dy) in offsets.items()
        if Point(section.x + dx, section.y + dy) not in cells
    )


def raised_platforms(
    floor_cells: frozenset[Point],
    elevations: Mapping[Point, int],
) -> tuple[RaisedPlatform, ...]:
    """Return connected positive-elevation components supported by floor.

    Elevation is independent from occupancy: every elevated section must already
    be walkable floor. Components are split when either connectivity or height
    differs, allowing adjacent platforms at different levels later.
    """
    invalid = {point for point, height in elevations.items() if height < 0 or point not in floor_cells}
    if invalid:
        raise ValueError(f"invalid platform sections: {sorted(invalid)}")

    remaining = {point for point, height in elevations.items() if height > 0}
    result: list[RaisedPlatform] = []
    offsets = ((1, 0), (-1, 0), (0, 1), (0, -1))

    while remaining:
        start = min(remaining)
        height = elevations[start]
        queue = deque([start])
        component = {start}
        remaining.remove(start)
        while queue:
            point = queue.popleft()
            for dx, dy in offsets:
                neighbor = Point(point.x + dx, point.y + dy)
                if neighbor in remaining and elevations[neighbor] == height:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        frozen = frozenset(component)
        result.append(RaisedPlatform(height, frozen, _perimeter(frozen)))

    return tuple(sorted(result, key=lambda platform: (platform.elevation, min(platform.cells))))
