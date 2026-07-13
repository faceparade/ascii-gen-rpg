"""One connected pre-elevation dungeon integration map for Grammar v2.

Every approved structural variation is embedded as an exact translated submask.
Short orthogonal passages connect those structures into an irregular dungeon
network with branches, loops, crosslinks, and no full-width gallery spine.
Elevation is intentionally absent from this fixture.
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
    FeaturePlacement("enclosed_loop", ("#######", "#.....#", "#.....#", "#.....#", "#.....#", "#.....#", "#######"), Point(3, 1)),
    FeaturePlacement("irregular_courtyard", ("#######", "#...###", "#...###", "#.....#", "#.....#", "#######", "#######"), Point(21, 0)),
    FeaturePlacement("u_courtyard", ("##..##", "##..##", "##..##", "######"), Point(40, 1)),
    FeaturePlacement("east_bridge", ("##....", "##....", "######"), Point(56, 1)),
    FeaturePlacement("west_bridge", ("....##", "....##", "######"), Point(70, 4)),
    FeaturePlacement("unit", ("#",), Point(89, 0)),
    FeaturePlacement("two_by_two", ("##", "##"), Point(97, 1)),
    FeaturePlacement("four_by_four", ("####", "####", "####", "####"), Point(106, 0)),
    FeaturePlacement("l_shape", ("###", "##.", "##."), Point(88, 10)),
    FeaturePlacement("horizontal_corridor", ("###...###", "###...###", "#########", "###...###", "###...###"), Point(3, 20)),
    FeaturePlacement("vertical_corridor", ("#####", "#####", "..#..", "..#..", "..#..", "#####", "#####"), Point(18, 18)),
    FeaturePlacement("wide_horizontal_corridor", ("###...###", "###...###", "#########", "#########", "###...###", "###...###"), Point(29, 19)),
    FeaturePlacement("four_way_cross", ("..#####..", "..#####..", "....#....", "....#....", "#########", "....#....", "....#....", "..#####..", "..#####.."), Point(47, 19)),
    FeaturePlacement("south_branch_t", ("###...###", "###...###", "#########", "....#....", "....#....", "....#....", "..#####..", "..#####.."), Point(63, 19)),
    FeaturePlacement("west_offset_vertical_corridor", ("#######", "#######", ".#.....", ".#.....", ".#.....", "#######", "#######"), Point(80, 18)),
    FeaturePlacement("wide_vertical_centered", ("########", "########", "...##...", "...##...", "...##...", "########", "########"), Point(94, 18)),
    FeaturePlacement("wide_vertical_west_offset", ("########", "########", ".##.....", ".##.....", ".##.....", "########", "########"), Point(3, 40)),
    FeaturePlacement("wide_vertical_east_offset", ("########", "########", ".....##.", ".....##.", ".....##.", "########", "########"), Point(18, 40)),
    FeaturePlacement("wide_shifted_rooms", ("########....", "########....", ".....##.....", ".....##.....", ".....##.....", "....########", "....########"), Point(33, 39)),
    FeaturePlacement("shifted_room_east", ("#######....", "#######....", ".....#.....", ".....#.....", ".....#.....", "....#######", "....#######"), Point(53, 40)),
    FeaturePlacement("shifted_room_west", ("....#######", "....#######", ".....#.....", ".....#.....", ".....#.....", "#######....", "#######...."), Point(70, 40)),
    FeaturePlacement("eastward_dogleg", ("#######", "#######", ".#.....", ".#.....", ".#####.", ".....#.", ".....#.", "#######", "#######"), Point(88, 38)),
    FeaturePlacement("westward_dogleg", ("#######", "#######", ".....#.", ".....#.", ".#####.", ".#.....", ".#.....", "#######", "#######"), Point(102, 40)),
)


CONNECTIONS: tuple[Polyline, ...] = (
    # Northern chambers form a winding chain rather than a straight display row.
    (Point(9, 4), Point(16, 4), Point(16, 2), Point(21, 2)),
    (Point(27, 5), Point(33, 5), Point(33, 3), Point(40, 3)),
    (Point(45, 4), Point(50, 4), Point(50, 8), Point(58, 8), Point(58, 3)),
    (Point(61, 3), Point(64, 3), Point(64, 9), Point(72, 9), Point(72, 6)),
    (Point(75, 6), Point(81, 6), Point(81, 11), Point(88, 11)),
    (Point(90, 10), Point(92, 10), Point(92, 0), Point(89, 0)),
    (Point(89, 0), Point(93, 0), Point(93, 1), Point(97, 1)),
    (Point(98, 2), Point(102, 2), Point(102, 1), Point(106, 1)),

    # Branches descend from different northern structures into the middle dungeon.
    (Point(6, 7), Point(6, 14), Point(0, 14), Point(0, 22), Point(3, 22)),
    (Point(24, 6), Point(24, 12), Point(20, 12), Point(20, 18)),
    (Point(43, 4), Point(43, 11), Point(33, 11), Point(33, 19)),
    (Point(58, 3), Point(58, 12), Point(51, 12), Point(51, 19)),
    (Point(72, 6), Point(72, 14), Point(70, 14), Point(70, 19)),
    (Point(88, 12), Point(86, 12), Point(86, 18)),
    (Point(107, 3), Point(107, 12), Point(98, 12), Point(98, 18)),

    # The middle level is a linked junction network with staggered crosslinks.
    (Point(11, 22), Point(14, 22), Point(14, 19), Point(18, 19)),
    (Point(22, 19), Point(25, 19), Point(25, 21), Point(29, 21)),
    (Point(37, 21), Point(42, 21), Point(42, 23), Point(47, 23)),
    (Point(55, 23), Point(59, 23), Point(59, 21), Point(63, 21)),
    (Point(71, 21), Point(75, 21), Point(75, 19), Point(80, 19)),
    (Point(86, 19), Point(90, 19), Point(90, 16), Point(94, 16), Point(94, 19)),

    # Separate drops reach lower rooms and create multiple possible routes.
    (Point(7, 24), Point(7, 32), Point(6, 32), Point(6, 40)),
    (Point(20, 24), Point(20, 32), Point(22, 32), Point(22, 40)),
    (Point(33, 24), Point(33, 31), Point(38, 31), Point(38, 39)),
    (Point(51, 27), Point(51, 34), Point(58, 34), Point(58, 40)),
    (Point(67, 26), Point(67, 33), Point(75, 33), Point(75, 40)),
    (Point(83, 24), Point(83, 31), Point(91, 31), Point(91, 38)),
    (Point(98, 24), Point(98, 32), Point(105, 32), Point(105, 40)),

    # Lower crosslinks complete loops without introducing a global spine.
    (Point(10, 41), Point(13, 41), Point(13, 36), Point(18, 36), Point(18, 41)),
    (Point(25, 41), Point(29, 41), Point(29, 37), Point(33, 37), Point(33, 40)),
    (Point(40, 40), Point(46, 40), Point(46, 36), Point(53, 36), Point(53, 40)),
    (Point(59, 40), Point(64, 40), Point(64, 50), Point(74, 50), Point(74, 46)),
    (Point(80, 40), Point(84, 40), Point(84, 35), Point(88, 35), Point(88, 38)),
    (Point(94, 38), Point(98, 38), Point(98, 52), Point(102, 52), Point(102, 48)),
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
