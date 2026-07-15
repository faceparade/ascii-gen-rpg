"""Manual-review renderer for the first sunken chamber/corridor treatment.

The topology is classified before rendering. For the first approved 7×5 fixture,
the exact user-authored projection is authoritative. Later terrain shapes will
generalize these motifs only after this checkpoint is approved.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from style_sample_system_v2_base import Point, cell_bounds
from terrain_cut_grammar_v2 import validate_terrain_scene


@dataclass(frozen=True)
class ChamberCorridorCut:
    min_x: int
    max_x: int
    min_y: int
    max_y: int
    corridor_y: int
    corridor_end_x: int

    @property
    def width(self) -> int:
        return self.max_x - self.min_x + 1

    @property
    def height(self) -> int:
        return self.max_y - self.min_y + 1


def _classify_chamber_corridor(
    surface_cells: frozenset[Point],
    lower_cells: frozenset[Point],
) -> ChamberCorridorCut:
    """Recognize the approved three-row chamber with an eastbound corridor."""

    min_x = min(point.x for point in lower_cells)
    min_y = min(point.y for point in lower_cells)
    max_y = max(point.y for point in lower_cells)
    if max_y - min_y + 1 != 3:
        raise NotImplementedError("initial cliff artwork requires a three-row chamber")

    row_bounds: dict[int, tuple[int, int]] = {}
    for y in range(min_y, max_y + 1):
        xs = sorted(point.x for point in lower_cells if point.y == y)
        if not xs or xs != list(range(xs[0], xs[-1] + 1)):
            raise NotImplementedError("initial cliff artwork requires contiguous lower rows")
        row_bounds[y] = (xs[0], xs[-1])

    corridor_y = min_y + 1
    top_bounds = row_bounds[min_y]
    middle_bounds = row_bounds[corridor_y]
    bottom_bounds = row_bounds[max_y]
    if top_bounds != bottom_bounds:
        raise NotImplementedError("initial cliff artwork requires matching chamber top and bottom rows")
    if top_bounds[0] != min_x or middle_bounds[0] != min_x:
        raise NotImplementedError("initial cliff artwork requires a shared west chamber wall")

    max_x = top_bounds[1]
    corridor_end_x = middle_bounds[1]
    if corridor_end_x <= max_x:
        raise NotImplementedError("initial cliff artwork requires an eastbound corridor")

    chamber = frozenset(
        Point(x, y)
        for y in range(min_y, max_y + 1)
        for x in range(min_x, max_x + 1)
    )
    corridor = frozenset(Point(x, corridor_y) for x in range(max_x + 1, corridor_end_x + 1))
    if lower_cells != chamber | corridor:
        raise NotImplementedError("lower topology is not the initial chamber/corridor fixture")

    surface_width, surface_height = cell_bounds(surface_cells)
    if (surface_width, surface_height) != (7, 5):
        raise NotImplementedError("initial cliff artwork is approved only for the 7×5 fixture")
    if corridor_end_x != surface_width - 1:
        raise NotImplementedError("initial corridor must remain open at the east crop boundary")

    return ChamberCorridorCut(min_x, max_x, min_y, max_y, corridor_y, corridor_end_x)


def _classify_inside_cliff_corner(
    surface_cells: frozenset[Point],
    lower_cells: frozenset[Point],
) -> None:
    """Recognize the approved 5×5 east-to-south lower L-turn."""

    expected_surface = frozenset(Point(x, y) for y in range(5) for x in range(5))
    expected_lower = frozenset(
        {Point(x, 1) for x in range(1, 5)}
        | {Point(1, y) for y in range(2, 5)}
    )
    if surface_cells != expected_surface or lower_cells != expected_lower:
        raise NotImplementedError("inside-corner artwork is approved only for the 5×5 east-to-south L-turn")


def _classify_mirrored_inside_cliff_corner(
    surface_cells: frozenset[Point],
    lower_cells: frozenset[Point],
) -> None:
    """Recognize the approved 5×5 west-to-south lower L-turn."""

    expected_surface = frozenset(Point(x, y) for y in range(5) for x in range(5))
    expected_lower = frozenset(
        {Point(x, 1) for x in range(4)}
        | {Point(3, y) for y in range(2, 5)}
    )
    if surface_cells != expected_surface or lower_cells != expected_lower:
        raise NotImplementedError("mirrored inside-corner artwork is approved only for the 5×5 west-to-south L-turn")


def _classify_outside_cliff_corner(
    surface_cells: frozenset[Point],
    lower_cells: frozenset[Point],
) -> None:
    """Recognize the approved 5×5 upper shelf projecting south."""

    expected_surface = frozenset(Point(x, y) for y in range(5) for x in range(5))
    expected_upper = frozenset(Point(x, y) for y in range(3) for x in range(2)) | frozenset(
        Point(x, 0) for x in range(2, 5)
    )
    if surface_cells != expected_surface or lower_cells != expected_surface - expected_upper:
        raise NotImplementedError("outside-corner artwork is approved only for the 5×5 south-projecting shelf")


USER_AUTHORED_FIRST_CLIFF_ART = (
    "      ,— —,— —,— —,— —,",
    "      |__/___/___/__ /|",
    "      |   ,— — — — —'—'",
    "      |  /|           ",
    "      | ‘ |",
    "      | |/|",
    "      | | |",
    "      | |/|",
    "      | | |",
    "      | |/|",
    "      '—'—'",
    "    ",
)
USER_AUTHORED_INSIDE_CLIFF_CORNER_ART = USER_AUTHORED_FIRST_CLIFF_ART
USER_AUTHORED_OUTSIDE_CLIFF_CORNER_ART = (
    "         ,— —,- -,— —,",
    "         |__/___/___/_",
    "         |",
    "         |",
    "—,— —,- -,",
    "/___/___/",
)
USER_AUTHORED_MIRRORED_INSIDE_CLIFF_CORNER_ART = (
    "\t\t\t\t\t    ",
    "—,— —,— —,— —,— —,— —,  ",
    "/___/___/___/___/__ /|  ",
    "— — — — — — — — —. | |  ",
    "                 | |/|  ",
    "                 | | |  ",
    "                 | |/|  ",
    "                 | | |  ",
    "                 | |/|  ",
    "                 | | |  ",
    "                 | |/|  ",
    "                 | | |  ",
    "                 | |/|  ",
)


def mirror_cliff_art_horizontally(rows: tuple[str, ...]) -> tuple[str, ...]:
    """Mirror an approved canvas for manual review without inventing new glyphs."""

    width = max(map(len, rows), default=0)
    return tuple(row.ljust(width)[::-1] for row in rows)


def render_sunken_terrain(
    surface_cells: frozenset[Point],
    elevations: Mapping[Point, int],
    walkable_cells: frozenset[Point],
) -> tuple[str, ...]:
    """Render the authoritative first level-1 exterior / level-0 cut fixture."""

    validate_terrain_scene(surface_cells, elevations, walkable_cells)
    heights = frozenset(elevations.values())
    if heights != {0, 1}:
        raise NotImplementedError("initial terrain-cut projection requires heights {0, 1}")
    if any(elevations[cell] != 0 for cell in walkable_cells):
        raise ValueError("initial terrain-cut projection requires walkable cells at level 0")

    upper_cells = frozenset(cell for cell in surface_cells if elevations[cell] == 1)
    if not upper_cells or not walkable_cells:
        raise ValueError("terrain-cut projection requires both upper and lower surfaces")

    bounds = cell_bounds(surface_cells)
    if bounds == (7, 5):
        _classify_chamber_corridor(surface_cells, walkable_cells)
        return USER_AUTHORED_FIRST_CLIFF_ART
    if bounds == (5, 5):
        inside_lower = frozenset(
            {Point(x, 1) for x in range(1, 5)}
            | {Point(1, y) for y in range(2, 5)}
        )
        if walkable_cells == inside_lower:
            _classify_inside_cliff_corner(surface_cells, walkable_cells)
            return USER_AUTHORED_INSIDE_CLIFF_CORNER_ART
        mirrored_inside_lower = frozenset(
            {Point(x, 1) for x in range(4)}
            | {Point(3, y) for y in range(2, 5)}
        )
        if walkable_cells == mirrored_inside_lower:
            _classify_mirrored_inside_cliff_corner(surface_cells, walkable_cells)
            return USER_AUTHORED_MIRRORED_INSIDE_CLIFF_CORNER_ART
        _classify_outside_cliff_corner(surface_cells, walkable_cells)
        return USER_AUTHORED_OUTSIDE_CLIFF_CORNER_ART
    raise NotImplementedError("terrain-cut artwork has not been approved for this topology")
