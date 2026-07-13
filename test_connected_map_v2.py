from collections import deque
from pathlib import Path

from connected_map_v2 import FEATURES, connected_map_cells, connected_map_mask
from style_sample_system import Point, render_irregular_room


REVIEW = Path("style_samples/review/connected-map-v2.txt")


def _component(cells: frozenset[Point], start: Point) -> frozenset[Point]:
    seen = {start}
    queue = deque([start])
    while queue:
        point = queue.popleft()
        for neighbor in (
            Point(point.x + 1, point.y),
            Point(point.x - 1, point.y),
            Point(point.x, point.y + 1),
            Point(point.x, point.y - 1),
        ):
            if neighbor in cells and neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return frozenset(seen)


def _longest_horizontal_run(mask: tuple[str, ...]) -> int:
    longest = 0
    for row in mask:
        current = 0
        for glyph in row:
            if glyph == "#":
                current += 1
                longest = max(longest, current)
            else:
                current = 0
    return longest


def test_connected_map_is_one_walkable_component() -> None:
    cells = connected_map_cells()
    assert len(cells) == 966
    assert _component(cells, min(cells)) == cells


def test_connected_map_has_compact_dungeon_bounds() -> None:
    mask = connected_map_mask()
    assert len(mask) == 68
    assert {len(row) for row in mask} == {85}


def test_connected_map_avoids_a_full_width_gallery_spine() -> None:
    assert _longest_horizontal_run(connected_map_mask()) <= 24


def test_every_approved_variation_is_embedded_as_an_exact_translated_submask() -> None:
    cells = connected_map_cells()
    assert len(FEATURES) == 23
    for feature in FEATURES:
        assert feature.cells.issubset(cells), feature.name


def test_feature_placements_do_not_overlap_each_other() -> None:
    occupied: set[Point] = set()
    for feature in FEATURES:
        assert occupied.isdisjoint(feature.cells), feature.name
        occupied.update(feature.cells)


def test_connected_map_has_no_elevation_layer() -> None:
    assert "Elevation data is intentionally absent." in REVIEW.read_text(encoding="utf-8")


def test_connected_map_renderer_handles_complete_dungeon() -> None:
    rows = render_irregular_room(connected_map_cells())
    assert len(rows) == 138
    assert max(map(len, rows)) == 343
