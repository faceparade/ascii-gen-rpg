#!/usr/bin/env python3
"""Reusable graph model and ordered-region renderer for ASCII dungeon scenes."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SceneRegionSpec:
    """Named contiguous region placed at a one-based scene line."""

    name: str
    start_line: int
    rows: tuple[str, ...]

    @property
    def end_line(self) -> int:
        return self.start_line + len(self.rows) - 1

    @property
    def widths(self) -> tuple[int, ...]:
        return tuple(len(row) for row in self.rows)


@dataclass(frozen=True)
class SceneRoomPlacement:
    """Room bounds in zero-based scene coordinates."""

    room_id: str
    x: int
    y: int
    width: int = 34
    height: int = 9


@dataclass(frozen=True)
class SceneConnection:
    """Named adjacency edge between two rooms."""

    from_room: str
    to_room: str
    kind: str
    region_name: str


@dataclass(frozen=True)
class SceneGraph:
    """Layout-independent rooms, connections, and rendered source regions."""

    rooms: tuple[SceneRoomPlacement, ...]
    connections: tuple[SceneConnection, ...]
    regions: tuple[SceneRegionSpec, ...]


def render_scene_graph(graph: SceneGraph) -> list[str]:
    """Render regions at their one-based start lines, preserving intentional gaps."""
    rows: list[str] = []
    for region in sorted(graph.regions, key=lambda item: item.start_line):
        target_index = region.start_line - 1
        if target_index < 0:
            raise ValueError(f"region {region.name} start_line must be positive")
        if target_index < len(rows):
            raise ValueError(f"region {region.name} overlaps an earlier region")
        rows.extend("" for _ in range(target_index - len(rows)))
        rows.extend(region.rows)
    return rows


def validate_scene_graph(graph: SceneGraph) -> tuple[str, ...]:
    """Return duplicate-name and broken-reference errors without rendering."""
    errors: list[str] = []
    room_ids: set[str] = set()
    for room in graph.rooms:
        if room.room_id in room_ids:
            errors.append(f"room {room.room_id} is duplicated")
        room_ids.add(room.room_id)

    region_names: set[str] = set()
    for region in graph.regions:
        if region.name in region_names:
            errors.append(f"region {region.name} is duplicated")
        region_names.add(region.name)

    for connection in graph.connections:
        label = f"connection {connection.from_room}->{connection.to_room}"
        if connection.from_room not in room_ids:
            errors.append(f"{label} references unknown from_room {connection.from_room}")
        if connection.to_room not in room_ids:
            errors.append(f"{label} references unknown to_room {connection.to_room}")
        if connection.region_name not in region_names:
            errors.append(f"{label} references unknown region {connection.region_name}")
    return tuple(errors)
