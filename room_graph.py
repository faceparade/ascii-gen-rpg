#!/usr/bin/env python3
"""Tiny room-graph assembly path for locked ASCII dungeon scenes.

This module is intentionally narrow: it turns the current three-room macro into
explicit data specs, then renders those specs through ModularCanvas. The locked
macro remains the ground truth; tests prove this graph path reproduces it
byte-for-byte before it becomes the path for future room/connector assembly.
"""
from __future__ import annotations

from dataclasses import dataclass

from connector_specs import HorizontalConnectorSpec
from modular_canvas import ModularCanvas, OPAQUE
from platform_shell import PlatformShell
from presets import build_shell
from three_room_macro_test import (
    CORRIDOR_OFFSET_X,
    CORRIDOR_Y,
    ROOM_PITCH_X,
    ROOM_Y,
    PLATFORM_ROOM3_OFFSET_X,
    PLATFORM_ROOM3_OFFSET_Y,
)


@dataclass(frozen=True)
class PlatformPlacement:
    width_units: int
    offset_x: int
    offset_y: int


@dataclass(frozen=True)
class RoomNode:
    room_id: str
    shell_preset: str
    x: int
    y: int
    platform: PlatformPlacement | None = None


@dataclass(frozen=True)
class RoomGraph:
    rooms: tuple[RoomNode, ...]
    horizontal_connectors: tuple[HorizontalConnectorSpec, ...] = ()


def build_three_room_graph() -> RoomGraph:
    """Return the current three-room macro as room and connector specs."""
    return RoomGraph(
        rooms=(
            RoomNode("room1", "left_8", 0, ROOM_Y),
            RoomNode("room2", "middle_8", ROOM_PITCH_X, ROOM_Y),
            RoomNode(
                "room3",
                "terminal_8",
                ROOM_PITCH_X * 2,
                ROOM_Y,
                PlatformPlacement(4, PLATFORM_ROOM3_OFFSET_X, PLATFORM_ROOM3_OFFSET_Y),
            ),
        ),
        horizontal_connectors=(
            HorizontalConnectorSpec("room1", "room2", CORRIDOR_OFFSET_X, CORRIDOR_Y, 6),
            HorizontalConnectorSpec("room2", "room3", CORRIDOR_OFFSET_X, CORRIDOR_Y, 6),
        ),
    )


def _room_by_id(graph: RoomGraph) -> dict[str, RoomNode]:
    return {room.room_id: room for room in graph.rooms}


def _stamp_extent(stamp: list[str], x: int, y: int) -> tuple[int, int]:
    if not stamp:
        return (x, y)
    return (x + max(len(row) for row in stamp), y + len(stamp))


def _canvas_size(graph: RoomGraph) -> tuple[int, int]:
    rooms = _room_by_id(graph)
    width = 1
    height = 1
    for room in graph.rooms:
        shell = build_shell(room.shell_preset).render()
        width = max(width, _stamp_extent(shell, room.x, room.y)[0])
        height = max(height, _stamp_extent(shell, room.x, room.y)[1])
        if room.platform is not None:
            platform = PlatformShell(room.platform.width_units).render()
            px = room.x + room.platform.offset_x
            py = room.y + room.platform.offset_y
            width = max(width, _stamp_extent(platform, px, py)[0])
            height = max(height, _stamp_extent(platform, px, py)[1])
    for connector in graph.horizontal_connectors:
        source = rooms[connector.from_room]
        corridor = connector.render()
        cx, cy = connector.origin_from_room_x(source.x)
        width = max(width, _stamp_extent(corridor, cx, cy)[0])
        height = max(height, _stamp_extent(corridor, cx, cy)[1])
    return (width, height)


def render_room_graph(graph: RoomGraph) -> list[str]:
    """Render a room graph using the current locked stamp vocabulary."""
    rooms = _room_by_id(graph)
    width, height = _canvas_size(graph)
    canvas = ModularCanvas(width, height)

    # Preserve the legacy macro paste order exactly: shells, corridors, then
    # platform overlays. This avoids visual drift while making placement data-driven.
    for room in graph.rooms:
        canvas.paste_stamp(
            build_shell(room.shell_preset).render(),
            room.x,
            room.y,
            OPAQUE,
            source=room.room_id,
            layer="room",
        )

    for connector in graph.horizontal_connectors:
        source = rooms[connector.from_room]
        cx, cy = connector.origin_from_room_x(source.x)
        canvas.paste_stamp(
            connector.render(),
            cx,
            cy,
            OPAQUE,
            source=f"{connector.from_room}->{connector.to_room}",
            layer="connector",
        )

    for room in graph.rooms:
        if room.platform is None:
            continue
        canvas.paste_stamp(
            PlatformShell(room.platform.width_units).render(),
            room.x + room.platform.offset_x,
            room.y + room.platform.offset_y,
            OPAQUE,
            source=f"{room.room_id}:platform",
            layer="platform",
        )

    return canvas.render_lines()
