from pathlib import Path

import pytest

from style_sample_system import Point
from terrain_cut_grammar_v2 import CliffEdge, cliff_edge_layer, cliff_edges, validate_terrain_scene


SURFACE_CELLS = frozenset(Point(x, y) for y in range(5) for x in range(7))
LOWER_CELLS = frozenset(
    {Point(x, y) for y in range(1, 4) for x in range(1, 4)}
    | {Point(x, 2) for x in range(4, 7)}
)
ELEVATIONS = {point: (0 if point in LOWER_CELLS else 1) for point in SURFACE_CELLS}
REFERENCE = Path("style_samples/review/sunken-terrain-reference-v2.txt")

EXPECTED_REFERENCE = (
    "                   ,— —,— —,— —,— —,— —,— —,— —,",
    "                   |__/___/___/___/___/___/__ /|",
    "                   |   ,— — — — — —.         | |",
    "                   |  /|           | `   `   |/|",
    "                   | ‘ |           |         | |",
    "                   | |/|           | `   `   |/|",
    "                   | | |           '— — — —. | |",
    "                   | |/|                   | |/|",
    "   ,— —,— —,— —,— —' | |                   | | ,— —,— —,— —,",
    "   |__/___/___/___/  |/|                   | ‘/___/___/__ /|",
    "   |   ,— — — — — —. | ,— —,— —,— —,— —,— —,   ,— — — —. | |",
    "   |  /|           | ‘/___/___/___/___/___/   /|       | |/|",
    "   | ‘ |           |                         ‘ |       | | |",
    "   | |/|           | `   `   `   `   `   `   |/|       | |/|",
    "   | | |           '— — — — — — — — — — — — —'—'       | | |",
    "   | |/|                                               | |/|",
    "   | | |                                               | | |",
)


def _reference_rows() -> tuple[str, ...]:
    lines = REFERENCE.read_text(encoding="utf-8").splitlines()
    start = lines.index("REFERENCE PROJECTION") + 2
    end = lines.index("AUTHORITATIVE INTERPRETATION") - 1
    return tuple(lines[start:end])


def test_terrain_data_is_explicit_and_walkability_is_separate() -> None:
    validate_terrain_scene(SURFACE_CELLS, ELEVATIONS, LOWER_CELLS)
    assert LOWER_CELLS < SURFACE_CELLS
    assert {ELEVATIONS[point] for point in LOWER_CELLS} == {0}
    assert {ELEVATIONS[point] for point in SURFACE_CELLS - LOWER_CELLS} == {1}


def test_cliffs_exist_only_between_defined_surfaces_of_different_height() -> None:
    edges = cliff_edges(SURFACE_CELLS, ELEVATIONS, LOWER_CELLS)
    assert len(edges) == 17
    assert all(ELEVATIONS[edge.upper] > ELEVATIONS[edge.lower] for edge in edges)
    assert all(edge.height_delta == 1 for edge in edges)
    assert CliffEdge(Point(0, 2), Point(1, 2), "east", 1) in edges
    assert CliffEdge(Point(1, 0), Point(1, 1), "south", 1) in edges
    assert CliffEdge(Point(3, 4), Point(3, 3), "north", 1) in edges


def test_crop_boundary_does_not_create_an_implicit_closing_cliff() -> None:
    edges = cliff_edges(SURFACE_CELLS, ELEVATIONS, LOWER_CELLS)
    assert not any(edge.upper == Point(6, 0) and edge.direction == "east" for edge in edges)
    assert not any(edge.upper == Point(6, 4) and edge.direction == "south" for edge in edges)


def test_direction_controls_background_and_foreground_composition() -> None:
    assert cliff_edge_layer(CliffEdge(Point(0, 2), Point(1, 2), "east", 1)) == "background_elevation_face"
    assert cliff_edge_layer(CliffEdge(Point(1, 0), Point(1, 1), "south", 1)) == "foreground_elevation_face"
    assert cliff_edge_layer(CliffEdge(Point(3, 4), Point(3, 3), "north", 1)) == "background_elevation_face"
    assert cliff_edge_layer(CliffEdge(Point(4, 1), Point(3, 1), "west", 1)) == "foreground_elevation_face"


def test_surface_elevations_must_cover_the_scene_exactly() -> None:
    missing = dict(ELEVATIONS)
    missing.pop(Point(0, 0))
    with pytest.raises(ValueError, match="missing elevations"):
        validate_terrain_scene(SURFACE_CELLS, missing, LOWER_CELLS)

    extra = dict(ELEVATIONS)
    extra[Point(9, 9)] = 1
    with pytest.raises(ValueError, match="outside surface"):
        validate_terrain_scene(SURFACE_CELLS, extra, LOWER_CELLS)


def test_user_authored_sunken_terrain_reference_is_exactly_locked() -> None:
    assert _reference_rows() == EXPECTED_REFERENCE
