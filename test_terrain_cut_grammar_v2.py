from pathlib import Path

import pytest

from style_sample_system import Point
from review_app import ReviewState
from terrain_cut_grammar_v2 import CliffEdge, cliff_edge_layer, cliff_edges, validate_terrain_scene


SURFACE_CELLS = frozenset(Point(x, y) for y in range(5) for x in range(7))
LOWER_CELLS = frozenset(
    {Point(x, y) for y in range(1, 4) for x in range(1, 4)}
    | {Point(x, 2) for x in range(4, 7)}
)
ELEVATIONS = {point: (0 if point in LOWER_CELLS else 1) for point in SURFACE_CELLS}
REFERENCE = Path("style_samples/review/sunken-terrain-reference-v2.txt")
CATALOG = Path("style_samples/catalog_v2.json")

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


def test_inside_cliff_corner_review_fixture_has_one_explicit_l_turn() -> None:
    import json

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    sample = next(item for item in catalog["samples"] if item["id"] == "sunken-inside-cliff-corner-v2")

    assert sample["status"] == "approved"
    assert sample["surface_mask"] == ["#####"] * 5
    assert sample["elevation_map"] == ["11111", "10000", "10111", "10111", "10111"]
    assert sample["walkable_mask"] == [".....", ".####", ".#...", ".#...", ".#..."]

    surface = frozenset(Point(x, y) for y, row in enumerate(sample["surface_mask"]) for x, cell in enumerate(row) if cell == "#")
    lower = frozenset(Point(x, y) for y, row in enumerate(sample["walkable_mask"]) for x, cell in enumerate(row) if cell == "#")
    elevations = {
        Point(x, y): int(height)
        for y, row in enumerate(sample["elevation_map"])
        for x, height in enumerate(row)
    }
    edges = cliff_edges(surface, elevations, lower)

    assert len(lower) == 7
    assert len(edges) == 14
    assert CliffEdge(Point(2, 2), Point(1, 2), "west", 1) in edges
    assert CliffEdge(Point(2, 2), Point(2, 1), "north", 1) in edges
    assert not any(edge.lower == Point(4, 1) and edge.direction == "west" for edge in edges)
    assert not any(edge.lower == Point(1, 4) and edge.direction == "north" for edge in edges)


def test_inside_cliff_corner_exposes_approved_artwork() -> None:
    state = ReviewState(Path.cwd())
    detail = state.sample_detail("sunken-inside-cliff-corner-v2")

    assert detail["sample"]["review"] == "review/sunken-inside-cliff-corner-v2.txt"
    assert detail["sample"]["target"] == "targets/sunken-inside-cliff-corner-v2.txt"
    assert detail["candidate_source"] == "targets/sunken-inside-cliff-corner-v2.txt"
    assert detail["candidate"].strip()
    assert "SURFACE" not in detail["candidate"]
    assert detail["reference_source"] == "corrections/sunken-inside-cliff-corner-v2.txt"
    assert detail["reference"] == detail["display_output"]
    assert detail["decision"]["decision"] == "approved"


def test_outside_cliff_corner_review_fixture_has_one_projecting_upper_tip() -> None:
    import json

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    sample = next(item for item in catalog["samples"] if item["id"] == "sunken-outside-cliff-corner-v2")

    assert sample["status"] == "approved"
    assert sample["target"] == "targets/sunken-outside-cliff-corner-v2.txt"
    assert sample["surface_mask"] == ["#####"] * 5
    assert sample["elevation_map"] == ["11111", "11000", "11000", "00000", "00000"]
    assert sample["walkable_mask"] == [".....", "..###", "..###", "#####", "#####"]

    surface = frozenset(
        Point(x, y)
        for y, row in enumerate(sample["surface_mask"])
        for x, cell in enumerate(row)
        if cell == "#"
    )
    lower = frozenset(
        Point(x, y)
        for y, row in enumerate(sample["walkable_mask"])
        for x, cell in enumerate(row)
        if cell == "#"
    )
    elevations = {
        Point(x, y): int(height)
        for y, row in enumerate(sample["elevation_map"])
        for x, height in enumerate(row)
    }
    edges = cliff_edges(surface, elevations, lower)

    assert len(surface - lower) == 9
    assert len(lower) == 16
    assert len(edges) == 7
    assert CliffEdge(Point(1, 2), Point(2, 2), "east", 1) in edges
    assert CliffEdge(Point(1, 2), Point(1, 3), "south", 1) in edges
    assert not any(edge.lower == Point(4, 4) for edge in edges)


def test_outside_cliff_corner_exposes_approved_artwork() -> None:
    state = ReviewState(Path.cwd())
    detail = state.sample_detail("sunken-outside-cliff-corner-v2")

    assert detail["sample"]["status"] == "approved"
    assert detail["sample"]["review"] == "review/sunken-outside-cliff-corner-v2.txt"
    assert detail["sample"]["target"] == "targets/sunken-outside-cliff-corner-v2.txt"
    assert detail["candidate_source"] == "targets/sunken-outside-cliff-corner-v2.txt"
    assert detail["candidate"].strip()
    assert "ELEVATION" not in detail["candidate"]
    assert detail["reference_source"] == "targets/sunken-corridor-chamber-cliff-art-v2.txt"
    assert detail["display_source"] == "corrections/sunken-outside-cliff-corner-v2.txt"
    assert detail["candidate"] == detail["display_output"]
    assert detail["decision"]["decision"] == "approved"
    assert "open stepped outside-cliff layout" in detail["decision"]["notes"]
    assert detail["decision"]["correction_sha256"] == detail["candidate_sha256"]
    assert detail["decision"]["correction"] == "corrections/sunken-outside-cliff-corner-v2.txt"
    correction_path = Path("style_samples/corrections/sunken-outside-cliff-corner-v2.txt")
    assert detail["correction"] == correction_path.read_text(encoding="utf-8")


def test_mirrored_inside_cliff_corner_is_a_west_to_south_review_topology() -> None:
    import json

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    sample = next(item for item in catalog["samples"] if item["id"] == "sunken-mirrored-inside-cliff-corner-v2")

    assert sample["status"] == "approved"
    assert sample["surface_mask"] == ["#####"] * 5
    assert sample["elevation_map"] == ["11111", "00001", "11101", "11101", "11101"]
    assert sample["walkable_mask"] == [".....", "####.", "...#.", "...#.", "...#."]
    assert sample["review"] == "review/sunken-mirrored-inside-cliff-corner-v2.txt"
    assert sample["target"] == "targets/sunken-mirrored-inside-cliff-corner-v2.txt"

    surface = frozenset(Point(x, y) for y in range(5) for x in range(5))
    lower = frozenset({Point(x, 1) for x in range(4)} | {Point(3, y) for y in range(2, 5)})
    elevations = {point: (0 if point in lower else 1) for point in surface}
    edges = cliff_edges(surface, elevations, lower)

    assert len(lower) == 7
    assert len(edges) == 14
    assert CliffEdge(Point(2, 2), Point(3, 2), "east", 1) in edges
    assert CliffEdge(Point(4, 2), Point(3, 2), "west", 1) in edges

    detail = ReviewState(Path.cwd()).sample_detail(sample["id"])
    assert detail["candidate_source"] == sample["target"]
    assert detail["reference_source"] == "targets/sunken-inside-cliff-corner-v2.txt"
    assert detail["display_source"] == "corrections/sunken-mirrored-inside-cliff-corner-v2.txt"
    assert detail["candidate"] == detail["correction"]
    assert detail["decision"]["decision"] == "approved"
    assert detail["decision"]["correction_sha256"] == detail["candidate_sha256"]


def test_mirrored_outside_cliff_corner_is_a_west_projecting_review_topology() -> None:
    import json

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    sample = next(item for item in catalog["samples"] if item["id"] == "sunken-mirrored-outside-cliff-corner-v2")

    assert sample["status"] == "approved"
    assert sample["surface_mask"] == ["#####"] * 5
    assert sample["elevation_map"] == ["11111", "00011", "00011", "00000", "00000"]
    assert sample["walkable_mask"] == [".....", "###..", "###..", "#####", "#####"]
    assert sample["review"] == "review/sunken-mirrored-outside-cliff-corner-v2.txt"
    assert sample["target"] == "targets/sunken-mirrored-outside-cliff-corner-v2.txt"

    surface = frozenset(Point(x, y) for y in range(5) for x in range(5))
    upper = frozenset(Point(x, y) for y in range(3) for x in range(3, 5)) | frozenset(
        Point(x, 0) for x in range(3)
    )
    lower = surface - upper
    elevations = {point: (1 if point in upper else 0) for point in surface}
    edges = cliff_edges(surface, elevations, lower)

    assert len(upper) == 9
    assert len(lower) == 16
    assert len(edges) == 7
    assert CliffEdge(Point(3, 1), Point(2, 1), "west", 1) in edges
    assert CliffEdge(Point(4, 2), Point(4, 3), "south", 1) in edges

    detail = ReviewState(Path.cwd()).sample_detail(sample["id"])
    assert detail["candidate_source"] == sample["target"]
    assert detail["reference_source"] == "targets/sunken-outside-cliff-corner-v2.txt"
    assert detail["display_source"] == "corrections/sunken-mirrored-outside-cliff-corner-v2.txt"
    assert detail["candidate"] == detail["correction"]
    assert detail["decision"]["decision"] == "approved"
    assert detail["decision"]["correction_sha256"] == detail["candidate_sha256"]


def test_open_corridor_shoulder_is_a_two_wide_east_to_south_review_topology() -> None:
    import json

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    sample = next(item for item in catalog["samples"] if item["id"] == "sunken-open-corridor-shoulder-v2")

    assert sample["status"] == "reviewing"
    assert sample["surface_mask"] == ["#######"] * 5
    assert sample["elevation_map"] == ["1111111", "1000000", "1000000", "1001111", "1001111"]
    assert sample["walkable_mask"] == [".......", ".######", ".######", ".##....", ".##...."]
    assert sample["review"] == "review/sunken-open-corridor-shoulder-v2.txt"
    assert "target" not in sample

    surface = frozenset(Point(x, y) for y in range(5) for x in range(7))
    lower = frozenset(
        {Point(x, y) for y in (1, 2) for x in range(1, 7)}
        | {Point(x, y) for y in (3, 4) for x in (1, 2)}
    )
    elevations = {point: (0 if point in lower else 1) for point in surface}
    edges = cliff_edges(surface, elevations)

    assert len(surface - lower) == 19
    assert len(lower) == 16
    assert len(edges) == 16
    assert CliffEdge(Point(3, 3), Point(3, 2), "north", 1) in edges
    assert CliffEdge(Point(3, 3), Point(2, 3), "west", 1) in edges
    assert all(edge.lower.x != 6 or edge.direction != "east" for edge in edges)
    assert all(edge.lower.y != 4 or edge.direction != "south" for edge in edges)

    detail = ReviewState(Path.cwd()).sample_detail(sample["id"])
    assert detail["candidate_source"] == sample["review"]
    assert detail["reference_source"] == "targets/sunken-corridor-chamber-cliff-art-v2.txt"
    assert detail["display_source"] == sample["review"]
    assert detail["decision"] is None
