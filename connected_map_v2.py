"""One connected pre-elevation integration map for Grammar v2.

The map embeds every approved structural variation as an exact translated
submask, then joins the placements with three horizontal gallery spines and
one vertical backbone. Elevation is intentionally absent from this fixture.
"""
from __future__ import annotations

from dataclasses import dataclass

from style_sample_system_v2_base import Point


Mask = tuple[str, ...]


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


FEATURE_ROWS: tuple[tuple[tuple[str, Mask], ...], ...] = (
    (
        ("unit", ("#",)),
        ("two_by_two", ("##", "##")),
        ("four_by_four", ("####", "####", "####", "####")),
        ("l_shape", ("###", "##.", "##.")),
        ("u_courtyard", ("##..##", "##..##", "##..##", "######")),
        ("east_bridge", ("##....", "##....", "######")),
        ("west_bridge", ("....##", "....##", "######")),
        (
            "enclosed_loop",
            ("#######", "#.....#", "#.....#", "#.....#", "#.....#", "#.....#", "#######"),
        ),
    ),
    (
        (
            "irregular_courtyard",
            ("#######", "#...###", "#...###", "#.....#", "#.....#", "#######", "#######"),
        ),
        (
            "horizontal_corridor",
            ("###...###", "###...###", "#########", "###...###", "###...###"),
        ),
        ("vertical_corridor", ("#####", "#####", "..#..", "..#..", "..#..", "#####", "#####")),
        (
            "wide_horizontal_corridor",
            ("###...###", "###...###", "#########", "#########", "###...###", "###...###"),
        ),
        (
            "west_offset_vertical_corridor",
            ("#######", "#######", ".#.....", ".#.....", ".#.....", "#######", "#######"),
        ),
        (
            "shifted_room_east",
            (
                "#######....",
                "#######....",
                ".....#.....",
                ".....#.....",
                ".....#.....",
                "....#######",
                "....#######",
            ),
        ),
        (
            "shifted_room_west",
            (
                "....#######",
                "....#######",
                ".....#.....",
                ".....#.....",
                ".....#.....",
                "#######....",
                "#######....",
            ),
        ),
        (
            "eastward_dogleg",
            ("#######", "#######", ".#.....", ".#.....", ".#####.", ".....#.", ".....#.", "#######", "#######"),
        ),
    ),
    (
        (
            "westward_dogleg",
            ("#######", "#######", ".....#.", ".....#.", ".#####.", ".#.....", ".#.....", "#######", "#######"),
        ),
        (
            "wide_vertical_centered",
            ("########", "########", "...##...", "...##...", "...##...", "########", "########"),
        ),
        (
            "wide_vertical_west_offset",
            ("########", "########", ".##.....", ".##.....", ".##.....", "########", "########"),
        ),
        (
            "wide_vertical_east_offset",
            ("########", "########", ".....##.", ".....##.", ".....##.", "########", "########"),
        ),
        (
            "wide_shifted_rooms",
            (
                "########....",
                "########....",
                ".....##.....",
                ".....##.....",
                ".....##.....",
                "....########",
                "....########",
            ),
        ),
        (
            "south_branch_t",
            ("###...###", "###...###", "#########", "....#....", "....#....", "....#....", "..#####..", "..#####.."),
        ),
        (
            "four_way_cross",
            ("..#####..", "..#####..", "....#....", "....#....", "#########", "....#....", "....#....", "..#####..", "..#####.."),
        ),
    ),
)

SLOT_WIDTH = 18
ROW_ORIGINS = (0, 18, 38)
SPINE_ROWS = (13, 33, 53)


def _placements() -> tuple[FeaturePlacement, ...]:
    placements: list[FeaturePlacement] = []
    for row_index, row in enumerate(FEATURE_ROWS):
        for column_index, (name, mask) in enumerate(row):
            width = max(len(line) for line in mask)
            origin_x = column_index * SLOT_WIDTH + (SLOT_WIDTH - width) // 2
            placements.append(FeaturePlacement(name, mask, Point(origin_x, ROW_ORIGINS[row_index])))
    return tuple(placements)


FEATURES = _placements()


def _bottom_anchor(feature: FeaturePlacement) -> Point:
    cells = feature.cells
    bottom_y = max(point.y for point in cells)
    candidates = tuple(point for point in cells if point.y == bottom_y)
    minimum_x = min(point.x for point in cells)
    maximum_x = max(point.x for point in cells)
    center_x = (minimum_x + maximum_x) / 2
    return min(candidates, key=lambda point: (abs(point.x - center_x), point.x))


def connected_map_cells() -> frozenset[Point]:
    cells: set[Point] = set()

    for feature in FEATURES:
        cells.update(feature.cells)

    for row_index, row in enumerate(FEATURE_ROWS):
        spine_y = SPINE_ROWS[row_index]
        row_names = {name for name, _ in row}
        for feature in FEATURES:
            if feature.name not in row_names:
                continue
            anchor = _bottom_anchor(feature)
            cells.update(Point(anchor.x, y) for y in range(anchor.y, spine_y + 1))

    maximum_x = max(point.x for point in cells) + 2
    for spine_y in SPINE_ROWS:
        cells.update(Point(x, spine_y) for x in range(maximum_x + 1))

    cells.update(Point(0, y) for y in range(SPINE_ROWS[0], SPINE_ROWS[-1] + 1))
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
