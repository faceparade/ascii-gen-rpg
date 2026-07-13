"""Topology helpers for Grammar v2 enclosed corridor loops."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from style_sample_system_v2_base import Point, cell_bounds


@dataclass(frozen=True, order=True)
class EnclosedVoid:
    """One empty logical component fully enclosed by occupied floor."""

    cells: frozenset[Point]
    min_x: int
    min_y: int
    max_x: int
    max_y: int

    @property
    def width(self) -> int:
        return self.max_x - self.min_x + 1

    @property
    def height(self) -> int:
        return self.max_y - self.min_y + 1


@dataclass(frozen=True, order=True)
class RectangularCorridorLoop:
    """A one-section-thick occupied ring around one rectangular void."""

    void: EnclosedVoid
    outer_min_x: int
    outer_min_y: int
    outer_max_x: int
    outer_max_y: int


def enclosed_voids(cells: frozenset[Point]) -> tuple[EnclosedVoid, ...]:
    """Return empty components that cannot reach the floorplan exterior."""
    width, height = cell_bounds(cells)
    empty = {
        Point(x, y)
        for y in range(height)
        for x in range(width)
        if Point(x, y) not in cells
    }
    seen: set[Point] = set()
    result: list[EnclosedVoid] = []
    offsets = ((1, 0), (-1, 0), (0, 1), (0, -1))

    for start in sorted(empty):
        if start in seen:
            continue
        queue = deque([start])
        component: set[Point] = set()
        touches_exterior = False
        seen.add(start)
        while queue:
            point = queue.popleft()
            component.add(point)
            if point.x in {0, width - 1} or point.y in {0, height - 1}:
                touches_exterior = True
            for dx, dy in offsets:
                neighbor = Point(point.x + dx, point.y + dy)
                if neighbor in empty and neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        if not touches_exterior:
            result.append(
                EnclosedVoid(
                    frozenset(component),
                    min(point.x for point in component),
                    min(point.y for point in component),
                    max(point.x for point in component),
                    max(point.y for point in component),
                )
            )
    return tuple(result)


def rectangular_corridor_loops(
    cells: frozenset[Point],
) -> tuple[RectangularCorridorLoop, ...]:
    """Return one-cell-thick rectangular rings around enclosed rectangular voids."""
    loops: list[RectangularCorridorLoop] = []
    for void in enclosed_voids(cells):
        rectangle = frozenset(
            Point(x, y)
            for y in range(void.min_y, void.max_y + 1)
            for x in range(void.min_x, void.max_x + 1)
        )
        if void.cells != rectangle:
            continue

        outer_min_x = void.min_x - 1
        outer_min_y = void.min_y - 1
        outer_max_x = void.max_x + 1
        outer_max_y = void.max_y + 1
        ring = {
            Point(x, y)
            for y in range(outer_min_y, outer_max_y + 1)
            for x in range(outer_min_x, outer_max_x + 1)
            if x in {outer_min_x, outer_max_x}
            or y in {outer_min_y, outer_max_y}
        }
        if outer_min_x < 0 or outer_min_y < 0 or not ring.issubset(cells):
            continue
        loops.append(
            RectangularCorridorLoop(
                void,
                outer_min_x,
                outer_min_y,
                outer_max_x,
                outer_max_y,
            )
        )
    return tuple(loops)
