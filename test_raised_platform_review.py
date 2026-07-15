from pathlib import Path

import pytest

from raised_platform_grammar_v2 import PlatformEdge, raised_platforms
from raised_platform_renderer_v2 import platform_edge_layer, render_room_with_platforms
from review_app import ReviewState
from style_sample_system import Point, actor_anchor, cells_from_mask


ROOM_MASK = (
    "#####",
    "#####",
    "#####",
    "#####",
    "#####",
)
PLATFORM_CELLS = frozenset(
    Point(x, y)
    for y in range(1, 4)
    for x in range(1, 4)
)
ELEVATIONS = {point: 1 for point in PLATFORM_CELLS}
REBUILT_PLATFORM = (
    "                       ",
    "                       ",
    "      ,— — — — — —.    ",
    "     /|           |    ",
    "    , |           |    ",
    "    |/|           |    ",
    "    | |           |    ",
    "    |/|           |    ",
    "    | ‘— —,— —,— -,    ",
    "    ‘/___/___/___/     ",
    "                       ",
    "                       ",
)


def test_centered_three_by_three_platform_is_one_component() -> None:
    platforms = raised_platforms(cells_from_mask(ROOM_MASK), ELEVATIONS)
    assert len(platforms) == 1
    assert platforms[0].elevation == 1
    assert platforms[0].cells == PLATFORM_CELLS


def test_platform_perimeter_has_twelve_directional_edges() -> None:
    platform = raised_platforms(cells_from_mask(ROOM_MASK), ELEVATIONS)[0]
    assert len(platform.perimeter) == 12
    assert PlatformEdge(Point(1, 1), "north") in platform.perimeter
    assert PlatformEdge(Point(3, 1), "east") in platform.perimeter
    assert PlatformEdge(Point(3, 3), "south") in platform.perimeter
    assert PlatformEdge(Point(1, 3), "west") in platform.perimeter


def test_platform_edges_use_directional_elevation_layers() -> None:
    assert platform_edge_layer(PlatformEdge(Point(1, 1), "north")) == "background_elevation_face"
    assert platform_edge_layer(PlatformEdge(Point(3, 1), "east")) == "background_elevation_face"
    assert platform_edge_layer(PlatformEdge(Point(3, 3), "south")) == "foreground_elevation_face"
    assert platform_edge_layer(PlatformEdge(Point(1, 3), "west")) == "foreground_elevation_face"


def test_elevation_does_not_move_actor_anchor() -> None:
    assert actor_anchor(Point(2, 2)) == Point(10, 6)


def test_platform_projection_has_open_lower_floor_and_plain_foreground_face() -> None:
    rows = render_room_with_platforms(cells_from_mask(ROOM_MASK), ELEVATIONS)

    assert all(len(row) == 23 for row in rows)
    assert rows[0].isspace() and rows[-1].isspace()
    assert rows[2].startswith("      ,—")
    assert "‘/___/___/___/" in rows[9]
    assert ";.;" not in "\n".join(rows)


def test_centered_platform_uses_rebuilt_raised_floor_projection() -> None:
    assert render_room_with_platforms(cells_from_mask(ROOM_MASK), ELEVATIONS) == REBUILT_PLATFORM


def test_rebuilt_platform_is_the_current_review_candidate() -> None:
    detail = ReviewState(Path.cwd()).sample_detail("room-raised-platform-v2")

    assert detail["sample"]["status"] == "reviewing"
    assert tuple(detail["candidate"].splitlines()) == REBUILT_PLATFORM


def test_rectangular_platform_projection_remains_parametric() -> None:
    floor = cells_from_mask(("####",) * 4)
    elevations = {Point(x, y): 1 for y in range(1, 3) for x in range(1, 3)}

    rows = render_room_with_platforms(floor, elevations)

    assert len(rows) == 10
    assert any("‘/___/___/" in row for row in rows)


def test_platform_must_be_supported_by_walkable_floor() -> None:
    with pytest.raises(ValueError):
        raised_platforms(cells_from_mask(ROOM_MASK), {Point(7, 7): 1})
