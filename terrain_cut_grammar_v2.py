"""Explicit terrain-surface and cliff topology for Grammar v2 elevation.

The primary dungeon elevation model is a lower room/path cut into a surrounding
higher terrain plane. Surface occupancy, elevation, and walkability are separate:

* every rendered terrain surface is listed in ``surface_cells``;
* every surface cell has an explicit non-negative height;
* ``walkable_cells`` is an independent subset of the surfaces;
* a cliff exists only between two defined adjacent surfaces of different heights;
* the edge of a crop never creates an implicit closing wall.

Freestanding raised platforms remain a later, separate elevation treatment.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

from style_sample_system_v2_base import Point

Direction = Literal["north", "east", "south", "west"]
ElevationLayer = Literal["background_elevation_face", "foreground_elevation_face"]

_OFFSETS: dict[Direction, tuple[int, int]] = {
    "north": (0, -1),
    "east": (1, 0),
    "south": (0, 1),
    "west": (-1, 0),
}


@dataclass(frozen=True, order=True)
class CliffEdge:
    """One directed height transition from an upper surface toward a lower one."""

    upper: Point
    lower: Point
    direction: Direction
    height_delta: int


def validate_terrain_scene(
    surface_cells: frozenset[Point],
    elevations: Mapping[Point, int],
    walkable_cells: frozenset[Point] = frozenset(),
) -> None:
    """Validate explicit surface, elevation, and walkability data.

    Elevations must cover the surface exactly. This prevents blank map space from
    being interpreted accidentally as either elevated ground or empty void.
    """

    elevation_cells = frozenset(elevations)
    missing = surface_cells - elevation_cells
    extra = elevation_cells - surface_cells
    negative = frozenset(point for point, height in elevations.items() if height < 0)
    unsupported_walkable = walkable_cells - surface_cells

    problems: list[str] = []
    if missing:
        problems.append(f"missing elevations for {sorted(missing)!r}")
    if extra:
        problems.append(f"elevations outside surface for {sorted(extra)!r}")
    if negative:
        problems.append(f"negative elevations at {sorted(negative)!r}")
    if unsupported_walkable:
        problems.append(f"walkable cells outside surface for {sorted(unsupported_walkable)!r}")
    if problems:
        raise ValueError("invalid terrain scene: " + "; ".join(problems))


def cliff_edges(
    surface_cells: frozenset[Point],
    elevations: Mapping[Point, int],
    walkable_cells: frozenset[Point] = frozenset(),
) -> tuple[CliffEdge, ...]:
    """Return directed cliff edges from higher surfaces toward lower surfaces.

    Missing neighbors are ignored deliberately. A review crop can therefore end
    inside a continuing upper plane without acquiring an artificial south/east
    enclosure or any other implicit boundary face.
    """

    validate_terrain_scene(surface_cells, elevations, walkable_cells)
    result: set[CliffEdge] = set()

    for upper in surface_cells:
        upper_height = elevations[upper]
        for direction, (dx, dy) in _OFFSETS.items():
            lower = Point(upper.x + dx, upper.y + dy)
            if lower not in surface_cells:
                continue
            height_delta = upper_height - elevations[lower]
            if height_delta > 0:
                result.add(CliffEdge(upper, lower, direction, height_delta))

    return tuple(sorted(result))


def cliff_edge_layer(edge: CliffEdge) -> ElevationLayer:
    """Assign a directional cliff face to its composition layer."""

    if edge.direction in {"north", "east"}:
        return "background_elevation_face"
    return "foreground_elevation_face"
