"""One organic connected pre-elevation dungeon for Grammar v2.

Every approved structural variation is embedded as an exact translated submask.
Short orthogonal passages integrate those structures into a central junction complex,
northern chambers, looping side wings, and a staggered southern route. The layout
intentionally avoids full-width gallery spines and detachable showcase rows.
Elevation is deliberately absent from this fixture.
"""
from __future__ import annotations

from dataclasses import dataclass

from style_sample_system_v2_base import Point


Mask = tuple[str, ...]
Polyline = tuple[Point, ...]


@dataclass(frozen=True)
class FeaturePlacement:
    name: str
    mask: Mask
    origin: Point

    @property
    def cells(self) -> frozenset[Point]:
        return frozenset(
            Point(self.origin.x + x, self.origin.y + y)
            for y, row in enumerate(self.mask)
            for x, glyph in enumerate(row)
            if glyph == "#"
        )

    @property
    def bounds(self) -> tuple[int, int, int, int]:
        cells = self.cells
        return (
            min(point.x for point in cells),
            min(point.y for point in cells),
            max(point.x for point in cells),
            max(point.y for point in cells),
        )


FEATURES = (
    # Northern chambers and irregular boundaries.
    FeaturePlacement("enclosed_loop", ("#######", "#.....#", "#.....#", "#.....#", "#.....#", "#.....#", "#######"), Point(27, 5)),
    FeaturePlacement("irregular_courtyard", ("#######", "#...###", "#...###", "#.....#", "#.....#", "#######", "#######"), Point(58, 5)),
    FeaturePlacement("u_courtyard", ("##..##", "##..##", "##..##", "######"), Point(10, 12)),
    FeaturePlacement("east_bridge", ("##....", "##....", "######"), Point(19, 17)),
    FeaturePlacement("west_bridge", ("....##", "....##", "######"), Point(68, 15)),
    FeaturePlacement("unit", ("#",), Point(84, 20)),
    FeaturePlacement("two_by_two", ("##", "##"), Point(79, 22)),
    FeaturePlacement("four_by_four", ("####", "####", "####", "####"), Point(79, 10)),
    FeaturePlacement("l_shape", ("###", "##.", "##."), Point(11, 24)),

    # Central junction complex.
    FeaturePlacement("horizontal_corridor", ("###...###", "###...###", "#########", "###...###", "###...###"), Point(27, 27)),
    FeaturePlacement("four_way_cross", ("..#####..", "..#####..", "....#....", "....#....", "#########", "....#....", "....#....", "..#####..", "..#####.."), Point(42, 28)),
    FeaturePlacement("wide_horizontal_corridor", ("###...###", "###...###", "#########", "#########", "###...###", "###...###"), Point(56, 34)),
    FeaturePlacement("south_branch_t", ("###...###", "###...###", "#########", "....#....", "....#....", "....#....", "..#####..", "..#####.."), Point(42, 13)),
    FeaturePlacement("vertical_corridor", ("#####", "#####", "..#..", "..#..", "..#..", "#####", "#####"), Point(44, 39)),

    # Western lower wing.
    FeaturePlacement("west_offset_vertical_corridor", ("#######", "#######", ".#.....", ".#.....", ".#.....", "#######", "#######"), Point(24, 39)),
    FeaturePlacement("eastward_dogleg", ("#######", "#######", ".#.....", ".#.....", ".#####.", ".....#.", ".....#.", "#######", "#######"), Point(8, 37)),
    FeaturePlacement("shifted_room_east", ("#######....", "#######....", ".....#.....", ".....#.....", ".....#.....", "....#######", "....#######"), Point(4, 47)),
    FeaturePlacement("wide_vertical_west_offset", ("########", "########", ".##.....", ".##.....", ".##.....", "########", "########"), Point(21, 50)),

    # Eastern lower wing.
    FeaturePlacement("westward_dogleg", ("#######", "#######", ".....#.", ".....#.", ".#####.", ".#.....", ".#.....", "#######", "#######"), Point(76, 37)),
    FeaturePlacement("shifted_room_west", ("....#######", "....#######", ".....#.....", ".....#.....", ".....#.....", "#######....", "#######...."), Point(70, 47)),
    FeaturePlacement("wide_vertical_east_offset", ("########", "########", ".....##.", ".....##.", ".....##.", "########", "########"), Point(61, 50)),

    # Southern staggered descent.
    FeaturePlacement("wide_vertical_centered", ("########", "########", "...##...", "...##...", "...##...", "########", "########"), Point(39, 50)),
    FeaturePlacement("wide_shifted_rooms", ("########....", "########....", ".....##.....", ".....##.....", ".....##.....", "....########", "....########"), Point(45, 61)),
)


CONNECTIONS: tuple[Polyline, ...] = (
    # Central junction and its staggered southern descent.
    (Point(46, 20), Point(46, 28)),
    (Point(35, 29), Point(39, 29), Point(39, 32), Point(42, 32)),
    (Point(50, 32), Point(53, 32), Point(53, 36), Point(56, 36)),
    (Point(46, 36), Point(46, 39)),
    (Point(46, 45), Point(46, 48), Point(43, 48), Point(43, 50)),
    (Point(47, 45), Point(47, 49), Point(44, 49), Point(44, 50)),
    (Point(43, 56), Point(43, 59), Point(48, 59), Point(48, 61)),
    (Point(44, 56), Point(44, 60), Point(49, 60), Point(49, 61)),

    # Northern chamber network.
    (Point(33, 9), Point(37, 9), Point(37, 14), Point(42, 14)),
    (Point(27, 9), Point(22, 9), Point(22, 13), Point(15, 13)),
    (Point(15, 15), Point(17, 15), Point(17, 18), Point(19, 18)),
    (Point(24, 19), Point(25, 19), Point(25, 28), Point(27, 28)),
    (Point(12, 24), Point(12, 15)),
    (Point(13, 25), Point(20, 25), Point(20, 29), Point(27, 29)),
    (Point(58, 9), Point(54, 9), Point(54, 14), Point(50, 14)),
    (Point(64, 9), Point(67, 9), Point(67, 16), Point(68, 16)),
    (Point(73, 17), Point(73, 22), Point(79, 22)),
    (Point(77, 16), Point(81, 16), Point(81, 13)),
    (Point(81, 13), Point(81, 18), Point(84, 18), Point(84, 20)),
    (Point(84, 20), Point(84, 22), Point(80, 22)),
    (Point(71, 17), Point(71, 28), Point(64, 28), Point(64, 35)),

    # Western wing, including two independent routes into the lower network.
    (Point(27, 30), Point(22, 30), Point(22, 36), Point(11, 36), Point(11, 37)),
    (Point(9, 45), Point(9, 47)),
    (Point(14, 52), Point(18, 52), Point(18, 54), Point(21, 54)),
    (Point(14, 41), Point(18, 41), Point(18, 40), Point(24, 40)),
    (Point(27, 45), Point(27, 50)),
    (Point(28, 52), Point(35, 52), Point(35, 53), Point(39, 53)),
    (Point(25, 56), Point(25, 59), Point(45, 59), Point(45, 61)),
    (Point(20, 29), Point(20, 40), Point(24, 40)),

    # Eastern wing and its loop back into the central descent.
    (Point(64, 37), Point(70, 37), Point(70, 39), Point(81, 39)),
    (Point(78, 45), Point(78, 47)),
    (Point(70, 52), Point(68, 52), Point(68, 53)),
    (Point(61, 53), Point(50, 53), Point(50, 52), Point(43, 52)),
    (Point(65, 56), Point(65, 59), Point(56, 59), Point(56, 61)),
    (Point(70, 39), Point(70, 51), Point(68, 51)),
)


def _add_segment(cells: set[Point], start: Point, end: Point) -> None:
    if start.x == end.x:
        minimum, maximum = sorted((start.y, end.y))
        cells.update(Point(start.x, y) for y in range(minimum, maximum + 1))
        return
    if start.y == end.y:
        minimum, maximum = sorted((start.x, end.x))
        cells.update(Point(x, start.y) for x in range(minimum, maximum + 1))
        return
    raise ValueError(f"Non-orthogonal connector segment: {start!r} -> {end!r}")


def connected_map_cells() -> frozenset[Point]:
    cells: set[Point] = set()
    for feature in FEATURES:
        cells.update(feature.cells)
    for polyline in CONNECTIONS:
        for start, end in zip(polyline, polyline[1:]):
            _add_segment(cells, start, end)
    return frozenset(cells)


def connected_map_mask() -> tuple[str, ...]:
    cells = connected_map_cells()
    width = max(point.x for point in cells) + 1
    height = max(point.y for point in cells) + 1
    return tuple(
        "".join("#" if Point(x, y) in cells else "." for x in range(width))
        for y in range(height)
    )


def feature_legend() -> tuple[str, ...]:
    return tuple(
        f"{feature.name}: x={feature.bounds[0]}..{feature.bounds[2]}, y={feature.bounds[1]}..{feature.bounds[3]}"
        for feature in FEATURES
    )
