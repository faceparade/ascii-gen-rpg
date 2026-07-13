from collections import deque
import hashlib
from pathlib import Path

from connected_map_v2 import FEATURES, connected_map_cells, connected_map_mask
from style_sample_system import Point, render_irregular_room


REVIEW = Path("style_samples/review/connected-map-v2.txt")
EXPECTED_RENDER_SHA256 = "12da9aed6fd7264a297baa6a3d18cda0996b8d1b72e0eb894d889b91c27603b3"


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


def _render_digest() -> str:
    rows = render_irregular_room(connected_map_cells())
    payload = ("\n".join(rows) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_connected_map_is_one_walkable_component() -> None:
    cells = connected_map_cells()
    assert len(cells) == 1258
    assert _component(cells, min(cells)) == cells


def test_connected_map_has_expected_bounds() -> None:
    mask = connected_map_mask()
    assert len(mask) == 54
    assert {len(row) for row in mask} == {140}


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


def test_connected_map_rendering_matches_manual_review_digest() -> None:
    rows = render_irregular_room(connected_map_cells())
    assert len(rows) == 110
    assert max(map(len, rows)) == 563
    assert _render_digest() == EXPECTED_RENDER_SHA256
