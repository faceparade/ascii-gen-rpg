"""Shared topology descriptions for Grammar v2 horizontal and vertical wall junctions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from irregular_room_grammar import directional_runs
from style_sample_system_v2_base import BoundaryEdge, Point, boundary_edges

JunctionKind = Literal[
    "courtyard_bridge",
    "east_extending_bridge",
    "west_extending_bridge",
    "horizontal_corridor",
]
Termination = Literal[
    "inner_east_wall",
    "inner_west_wall",
    "exterior_west",
    "exterior_east",
]
VerticalJunctionKind = Literal["vertical_corridor"]
VerticalTermination = Literal["upper_room", "lower_room"]


@dataclass(frozen=True, order=True)
class HorizontalJunction:
    """One exposed north-edge span and the structures that terminate its ends."""

    kind: JunctionKind
    boundary_y: int
    start_x: int
    end_x: int
    left_termination: Termination
    right_termination: Termination

    @property
    def width(self) -> int:
        return self.end_x - self.start_x + 1


@dataclass(frozen=True, order=True)
class VerticalJunction:
    """One single-section-wide passage and the rooms at its ends."""

    kind: VerticalJunctionKind
    boundary_x: int
    start_y: int
    end_y: int
    top_termination: VerticalTermination
    bottom_termination: VerticalTermination

    @property
    def height(self) -> int:
        return self.end_y - self.start_y + 1


def _edge(edges: frozenset[BoundaryEdge], section: Point, direction: str) -> bool:
    return BoundaryEdge(section, direction) in edges


def horizontal_junctions(cells: frozenset[Point]) -> tuple[HorizontalJunction, ...]:
    """Classify promoted bridge motifs and one-cell-high room corridors.

    The classifier is topology-only. It does not inspect rendered characters.
    """
    edges = boundary_edges(cells)
    south_runs = set(directional_runs(cells, "south"))
    result: list[HorizontalJunction] = []

    for boundary_y, start_x, end_x in directional_runs(cells, "north"):
        if boundary_y == 0:
            continue

        above_empty = all(
            Point(x, boundary_y - 1) not in cells
            for x in range(start_x, end_x + 1)
        )
        if not above_empty:
            continue

        left_upper = start_x > 0 and _edge(
            edges, Point(start_x - 1, boundary_y - 1), "east"
        )
        right_upper = _edge(
            edges, Point(end_x + 1, boundary_y - 1), "west"
        )
        left_exterior = start_x == 0 and _edge(
            edges, Point(start_x, boundary_y), "west"
        )
        right_exterior = _edge(
            edges, Point(end_x, boundary_y), "east"
        )

        left_lower = (
            _edge(edges, Point(start_x - 1, boundary_y + 1), "east")
            if start_x > 0
            else False
        )
        right_lower = _edge(
            edges, Point(end_x + 1, boundary_y + 1), "west"
        )
        below_empty = all(
            Point(x, boundary_y + 1) not in cells
            for x in range(start_x, end_x + 1)
        )
        matching_south = (boundary_y + 1, start_x, end_x) in south_runs

        if (
            left_upper
            and right_upper
            and left_lower
            and right_lower
            and below_empty
            and matching_south
        ):
            result.append(
                HorizontalJunction(
                    "horizontal_corridor",
                    boundary_y,
                    start_x,
                    end_x,
                    "inner_east_wall",
                    "inner_west_wall",
                )
            )
        elif left_upper and right_upper:
            result.append(
                HorizontalJunction(
                    "courtyard_bridge",
                    boundary_y,
                    start_x,
                    end_x,
                    "inner_east_wall",
                    "inner_west_wall",
                )
            )
        elif left_upper and right_exterior:
            result.append(
                HorizontalJunction(
                    "east_extending_bridge",
                    boundary_y,
                    start_x,
                    end_x,
                    "inner_east_wall",
                    "exterior_east",
                )
            )
        elif left_exterior and right_upper:
            result.append(
                HorizontalJunction(
                    "west_extending_bridge",
                    boundary_y,
                    start_x,
                    end_x,
                    "exterior_west",
                    "inner_west_wall",
                )
            )

    return tuple(result)


def corridor_junctions(cells: frozenset[Point]) -> tuple[HorizontalJunction, ...]:
    return tuple(
        junction
        for junction in horizontal_junctions(cells)
        if junction.kind == "horizontal_corridor"
    )


def vertical_junctions(cells: frozenset[Point]) -> tuple[VerticalJunction, ...]:
    """Classify single-section-wide passages connecting upper and lower rooms.

    A vertical corridor has paired exposed west/east wall runs, continuous floor
    between occupied sections above and below, and matching room-wall segments
    on both sides of each doorway opening.
    """
    edges = boundary_edges(cells)
    east_runs = set(directional_runs(cells, "east"))
    result: list[VerticalJunction] = []

    for boundary_x, start_y, end_y in directional_runs(cells, "west"):
        if start_y == 0 or boundary_x == 0:
            continue
        if (boundary_x + 1, start_y, end_y) not in east_runs:
            continue
        if not all(
            Point(boundary_x, y) in cells
            for y in range(start_y, end_y + 1)
        ):
            continue

        top = Point(boundary_x, start_y - 1)
        bottom = Point(boundary_x, end_y + 1)
        if top not in cells or bottom not in cells:
            continue

        top_left = _edge(
            edges, Point(boundary_x - 1, start_y - 1), "south"
        )
        top_right = _edge(
            edges, Point(boundary_x + 1, start_y - 1), "south"
        )
        bottom_left = _edge(
            edges, Point(boundary_x - 1, end_y + 1), "north"
        )
        bottom_right = _edge(
            edges, Point(boundary_x + 1, end_y + 1), "north"
        )

        if top_left and top_right and bottom_left and bottom_right:
            result.append(
                VerticalJunction(
                    "vertical_corridor",
                    boundary_x,
                    start_y,
                    end_y,
                    "upper_room",
                    "lower_room",
                )
            )

    return tuple(result)


def vertical_corridor_junctions(
    cells: frozenset[Point],
) -> tuple[VerticalJunction, ...]:
    return tuple(
        junction
        for junction in vertical_junctions(cells)
        if junction.kind == "vertical_corridor"
    )
