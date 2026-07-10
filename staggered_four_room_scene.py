#!/usr/bin/env python3
"""A staggered four-room path assembled exclusively from locked scene fragments."""
from __future__ import annotations

from pathlib import Path

from scene_graph import SceneConnection, SceneGraph, SceneRegionSpec, SceneRoomPlacement
from six_room_scene import (
    LOWER_BAND_GAP_STRIP,
    LOWER_BAND_MIDDLE_ROOM_STRIP,
    LOWER_BAND_RIGHT_ROOM_STRIP,
    SCENE_MID_CONNECTOR_ROWS,
    UPPER_BAND_GAP_STRIP,
    UPPER_BAND_LEFT_ROOM_STRIP,
    UPPER_BAND_RIGHT_ROOM_STRIP,
    assemble_striped_region,
    write_scene_artifacts,
)

ROOM_WIDTH = 34
CONNECTOR_WIDTH = 23
ROOM_STEP = ROOM_WIDTH + CONNECTOR_WIDTH


def _upper_band_rows() -> tuple[str, ...]:
    return tuple(
        assemble_striped_region(
            (
                UPPER_BAND_LEFT_ROOM_STRIP,
                UPPER_BAND_GAP_STRIP,
                UPPER_BAND_RIGHT_ROOM_STRIP,
            )
        )
    )


def _vertical_bridge_rows() -> tuple[str, ...]:
    return tuple(
        " " * ROOM_STEP
        + row[ROOM_STEP : ROOM_STEP + ROOM_WIDTH]
        + " " * ROOM_STEP
        for row in SCENE_MID_CONNECTOR_ROWS
    )


def _lower_band_rows() -> tuple[str, ...]:
    body = assemble_striped_region(
        (
            LOWER_BAND_MIDDLE_ROOM_STRIP,
            LOWER_BAND_GAP_STRIP,
            LOWER_BAND_RIGHT_ROOM_STRIP,
        )
    )
    return tuple(" " * ROOM_STEP + row for row in body)


def build_staggered_four_room_scene_graph() -> SceneGraph:
    """Return a four-room S-shaped path using the established locked glyph strips."""
    return SceneGraph(
        rooms=(
            SceneRoomPlacement("north_west", 0, 0, ROOM_WIDTH, 9),
            SceneRoomPlacement("north_east", ROOM_STEP, 0, ROOM_WIDTH, 9),
            SceneRoomPlacement("south_center", ROOM_STEP, 13, ROOM_WIDTH, 7),
            SceneRoomPlacement("south_east", ROOM_STEP * 2, 13, ROOM_WIDTH, 7),
        ),
        connections=(
            SceneConnection("north_west", "north_east", "horizontal", "upper_band"),
            SceneConnection("north_east", "south_center", "vertical", "vertical_bridge"),
            SceneConnection("south_center", "south_east", "horizontal", "lower_band"),
        ),
        regions=(
            SceneRegionSpec("upper_band", 1, _upper_band_rows()),
            SceneRegionSpec("vertical_bridge", 10, _vertical_bridge_rows()),
            SceneRegionSpec("lower_band", 14, _lower_band_rows()),
        ),
    )


def write_staggered_four_room_scene_artifacts(output_dir: Path) -> list[Path]:
    """Write review artifacts for the staggered four-room graph."""
    return write_scene_artifacts(
        output_dir,
        build_staggered_four_room_scene_graph(),
        "staggered_four_room_scene",
    )
