from collections import deque
import hashlib
from pathlib import Path

from connected_map_v2 import FEATURES, connected_map_cells, connected_map_mask
from style_sample_system import Point, render_irregular_room


TARGET = Path("style_samples/targets/connected-map-v2.txt")
EXPECTED_RENDER_SHA256 = "51ca9dbef997129b449b6c32dfbe11e3d6932bdcb10fe2774e7fc03e45178ea6"


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


def _render_digest() -> str:
    rows = render_irregular_room(connected_map_cells())
    payload = ("\n".join(rows) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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


def test_connected_map_target_records_no_elevation_layer() -> None:
    target = TARGET.read_text(encoding="utf-8")
    assert "Elevation data is intentionally absent." in target
    assert "Approved as the pre-elevation integration target." in target


def test_connected_map_rendering_matches_approved_digest() -> None:
    rows = render_irregular_room(connected_map_cells())
    assert len(rows) == 138
    assert max(map(len, rows)) == 343
    assert _render_digest() == EXPECTED_RENDER_SHA256
