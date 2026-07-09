#!/usr/bin/env python3
"""Six-room scene generator assembled from locked named fragments."""
from __future__ import annotations

from argparse import ArgumentParser
import json
from html import escape
from dataclasses import dataclass
from pathlib import Path

from connector_specs import SceneFragmentSpec
from curved_dungeon_grammar import Rect, annotate, html_review, write_text


@dataclass(frozen=True)
class SixRoomLayoutSpec:
    """Locked horizontal layout for the current three-room scene bands."""

    room_width: int = 34
    connector_width: int = 23
    room_count: int = 3

    @property
    def segment_widths(self) -> tuple[int, int, int, int, int]:
        return (
            self.room_width,
            self.connector_width,
            self.room_width,
            self.connector_width,
            self.room_width,
        )

    @property
    def row_width(self) -> int:
        return sum(self.segment_widths)


@dataclass(frozen=True)
class SceneRegionSpec:
    """Named contiguous region in the locked six-room scene."""

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
class SceneCellInfo:
    """Debug metadata for one zero-based scene coordinate."""

    x: int
    y: int
    char: str | None
    regions: tuple[str, ...]
    rooms: tuple[str, ...]


@dataclass(frozen=True)
class SceneConnection:
    """Named adjacency edge in the locked six-room scene."""

    from_room: str
    to_room: str
    kind: str
    region_name: str


@dataclass(frozen=True)
class SixRoomSceneGraph:
    """Data model for the locked six-room scene assembly."""

    rooms: tuple[SceneRoomPlacement, ...]
    connections: tuple[SceneConnection, ...]
    regions: tuple[SceneRegionSpec, ...]


ROOM_BOTTOM_RAIL = tuple(SceneFragmentSpec.room_bottom_rail_34().render())
ROOM_TOP_BAND = tuple(SceneFragmentSpec.room_top_band_34().render())
ROOM_FLOOR_BAND = tuple(SceneFragmentSpec.room_floor_band_34().render())
MIDDLE_SEAM_CONNECTOR_GAP = tuple(SceneFragmentSpec.middle_seam_connector_gap_80().render())
LOWER_BAND_LEFT_ROOM_STRIP = tuple(SceneFragmentSpec.lower_band_left_room_strip_34().render())
LOWER_BAND_GAP_STRIP = tuple(SceneFragmentSpec.lower_band_gap_strip_23().render())
LOWER_BAND_MIDDLE_ROOM_STRIP = tuple(SceneFragmentSpec.lower_band_middle_room_strip_34().render())
LOWER_BAND_RIGHT_ROOM_STRIP = tuple(SceneFragmentSpec.lower_band_right_room_strip_34().render())
UPPER_BAND_LEFT_ROOM_STRIP = tuple(SceneFragmentSpec.upper_band_left_room_strip_34().render())
UPPER_BAND_GAP_STRIP = tuple(SceneFragmentSpec.upper_band_gap_strip_23().render())
UPPER_BAND_MIDDLE_ROOM_STRIP = tuple(SceneFragmentSpec.upper_band_middle_room_strip_34().render())
UPPER_BAND_RIGHT_ROOM_STRIP = tuple(SceneFragmentSpec.upper_band_right_room_strip_34().render())
SCENE_TOP_ROWS = tuple(SceneFragmentSpec.scene_top_rows_1_4().render())
SCENE_MID_CONNECTOR_ROWS = tuple(SceneFragmentSpec.scene_mid_connector_rows_14_17().render())
SCENE_LOWER_CONNECTOR_ROWS = tuple(SceneFragmentSpec.scene_lower_connector_rows_20_22().render())


def validate_region_widths(
    strips: tuple[tuple[str, ...], ...],
    expected_widths: tuple[int, ...],
) -> None:
    """Validate that every row in each strip matches its expected width."""
    if len(strips) != len(expected_widths):
        raise ValueError(
            f"strip count must match expected widths: {len(strips)} != {len(expected_widths)}"
        )
    for index, (strip, width) in enumerate(zip(strips, expected_widths, strict=True), start=1):
        actual_widths = {len(row) for row in strip}
        if actual_widths != {width}:
            raise ValueError(f"strip {index} expected width {width}, got {sorted(actual_widths)}")


def assemble_striped_region(strips: tuple[tuple[str, ...], ...]) -> list[str]:
    """Join same-height horizontal strips row-by-row."""
    if not strips:
        return []
    heights = {len(strip) for strip in strips}
    if len(heights) != 1:
        raise ValueError(f"strip heights must match: {sorted(heights)}")
    return ["".join(parts) for parts in zip(*strips, strict=True)]


def assemble_middle_seam_rows() -> list[str]:
    """Rebuild source lines 18–19 from named scene fragments.

    The row-18 trailing space is intentional: line 18 is 149 columns while line
    19 is 148. Keep that ragged edge explicit instead of padding every row.
    """
    top_gap, floor_gap = MIDDLE_SEAM_CONNECTOR_GAP
    top = ROOM_TOP_BAND[0]
    floor = ROOM_FLOOR_BAND[0]
    return [
        top + top_gap + top + " ",
        floor + floor_gap + floor,
    ]


def assemble_lower_band_rows() -> list[str]:
    """Rebuild source lines 23–29 from named lower-band strips."""
    strips = (
        LOWER_BAND_LEFT_ROOM_STRIP,
        LOWER_BAND_GAP_STRIP,
        LOWER_BAND_MIDDLE_ROOM_STRIP,
        LOWER_BAND_GAP_STRIP,
        LOWER_BAND_RIGHT_ROOM_STRIP,
    )
    validate_region_widths(strips, SixRoomLayoutSpec().segment_widths)
    return assemble_striped_region(strips)


def assemble_upper_band_rows() -> list[str]:
    """Rebuild source lines 5–13 from named upper-band strips."""
    strips = (
        UPPER_BAND_LEFT_ROOM_STRIP,
        UPPER_BAND_GAP_STRIP,
        UPPER_BAND_MIDDLE_ROOM_STRIP,
        UPPER_BAND_GAP_STRIP,
        UPPER_BAND_RIGHT_ROOM_STRIP,
    )
    validate_region_widths(strips, SixRoomLayoutSpec().segment_widths)
    return assemble_striped_region(strips)


def six_room_placements() -> tuple[SceneRoomPlacement, ...]:
    """Return room bounds for the locked six-room scene.

    Coordinates are zero-based. Upper rooms cover lines 5–13. Lower rooms start
    at the middle seam top on line 18 and extend through line 29.
    """
    layout = SixRoomLayoutSpec()
    x_positions = (0, layout.room_width + layout.connector_width, (layout.room_width + layout.connector_width) * 2)
    return (
        SceneRoomPlacement("upper_left", x_positions[0], 4, layout.room_width, 9),
        SceneRoomPlacement("upper_middle", x_positions[1], 4, layout.room_width, 9),
        SceneRoomPlacement("upper_right", x_positions[2], 4, layout.room_width, 9),
        SceneRoomPlacement("lower_left", x_positions[0], 17, layout.room_width, 12),
        SceneRoomPlacement("lower_middle", x_positions[1], 17, layout.room_width, 12),
        SceneRoomPlacement("lower_right", x_positions[2], 17, layout.room_width, 12),
    )


def top_region() -> SceneRegionSpec:
    return SceneRegionSpec("top", 1, SCENE_TOP_ROWS)


def upper_band_region() -> SceneRegionSpec:
    return SceneRegionSpec("upper_band", 5, tuple(assemble_upper_band_rows()))


def mid_connector_region() -> SceneRegionSpec:
    return SceneRegionSpec("mid_connector", 14, SCENE_MID_CONNECTOR_ROWS)


def middle_seam_region() -> SceneRegionSpec:
    return SceneRegionSpec("middle_seam", 18, tuple(assemble_middle_seam_rows()))


def lower_connector_region() -> SceneRegionSpec:
    return SceneRegionSpec("lower_connector", 20, SCENE_LOWER_CONNECTOR_ROWS)


def lower_band_region() -> SceneRegionSpec:
    return SceneRegionSpec("lower_band", 23, tuple(assemble_lower_band_rows()))


def scene_regions() -> list[SceneRegionSpec]:
    """Return the locked six-room scene as named contiguous regions."""
    return [
        top_region(),
        upper_band_region(),
        mid_connector_region(),
        middle_seam_region(),
        lower_connector_region(),
        lower_band_region(),
    ]


def build_six_room_scene_graph() -> SixRoomSceneGraph:
    """Return the locked six-room scene as rooms, visible adjacencies, and source regions."""
    return SixRoomSceneGraph(
        rooms=six_room_placements(),
        connections=(
            SceneConnection("upper_left", "upper_middle", "horizontal", "upper_band"),
            SceneConnection("upper_middle", "upper_right", "horizontal", "upper_band"),
            SceneConnection("upper_left", "lower_left", "vertical", "mid_connector"),
            SceneConnection("upper_middle", "lower_middle", "vertical", "mid_connector"),
            SceneConnection("upper_right", "lower_right", "vertical", "mid_connector"),
            SceneConnection("lower_left", "lower_middle", "horizontal", "lower_band"),
            SceneConnection("lower_middle", "lower_right", "horizontal", "lower_band"),
        ),
        regions=tuple(scene_regions()),
    )


def render_six_room_scene_graph(graph: SixRoomSceneGraph) -> list[str]:
    """Render a six-room scene graph from its ordered named source regions."""
    return [row for region in graph.regions for row in region.rows]


def scene_connections_for_room(graph: SixRoomSceneGraph, room_id: str) -> tuple[SceneConnection, ...]:
    """Return connections touching ``room_id``, oriented from that room to its neighbor."""
    oriented: list[SceneConnection] = []
    for connection in graph.connections:
        if connection.from_room == room_id:
            oriented.append(connection)
        elif connection.to_room == room_id:
            oriented.append(
                SceneConnection(
                    room_id,
                    connection.from_room,
                    connection.kind,
                    connection.region_name,
                )
            )
    return tuple(oriented)


def validate_six_room_scene_graph(graph: SixRoomSceneGraph) -> tuple[str, ...]:
    """Return graph reference errors without mutating or rendering the scene."""
    room_ids = {room.room_id for room in graph.rooms}
    region_names = {region.name for region in graph.regions}
    errors: list[str] = []
    for connection in graph.connections:
        label = f"connection {connection.from_room}->{connection.to_room}"
        if connection.from_room not in room_ids:
            errors.append(f"{label} references unknown from_room {connection.from_room}")
        if connection.to_room not in room_ids:
            errors.append(f"{label} references unknown to_room {connection.to_room}")
        if connection.region_name not in region_names:
            errors.append(f"{label} references unknown region {connection.region_name}")
    return tuple(errors)


def validate_six_room_scene_graph_data(data: dict[str, object]) -> tuple[str, ...]:
    """Return validation errors for exported graph JSON data."""
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append(f"unsupported schema_version {data.get('schema_version')}")

    room_entries = data.get("rooms")
    region_entries = data.get("regions")
    connection_entries = data.get("connections")
    if not isinstance(room_entries, list):
        errors.append("rooms must be a list")
        room_entries = []
    if not isinstance(region_entries, list):
        errors.append("regions must be a list")
        region_entries = []
    if not isinstance(connection_entries, list):
        errors.append("connections must be a list")
        connection_entries = []

    room_ids = {
        room.get("room_id")
        for room in room_entries
        if isinstance(room, dict) and isinstance(room.get("room_id"), str)
    }
    region_names = {
        region.get("name")
        for region in region_entries
        if isinstance(region, dict) and isinstance(region.get("name"), str)
    }
    for connection in connection_entries:
        if not isinstance(connection, dict):
            errors.append("connection entry must be an object")
            continue
        from_room = connection.get("from_room")
        to_room = connection.get("to_room")
        region_name = connection.get("region_name")
        label = f"connection {from_room}->{to_room}"
        if from_room not in room_ids:
            errors.append(f"{label} references unknown from_room {from_room}")
        if to_room not in room_ids:
            errors.append(f"{label} references unknown to_room {to_room}")
        if region_name not in region_names:
            errors.append(f"{label} references unknown region {region_name}")
    return tuple(errors)


def assemble_six_room_scene_rows() -> list[str]:
    """Rebuild the locked six-room source through the six-room scene graph."""
    return render_six_room_scene_graph(build_six_room_scene_graph())


def _default_graph(graph: SixRoomSceneGraph | None) -> SixRoomSceneGraph:
    return graph if graph is not None else build_six_room_scene_graph()


def scene_region_rects(graph: SixRoomSceneGraph | None = None) -> list[Rect]:
    """Return named source-region rectangles for coordinate review artifacts."""
    scene_graph = _default_graph(graph)
    return [
        Rect(
            region.name,
            0,
            region.start_line - 1,
            max(region.widths) if region.widths else 0,
            len(region.rows),
        )
        for region in scene_graph.regions
    ]


def scene_room_rects(graph: SixRoomSceneGraph | None = None) -> list[Rect]:
    """Return room-placement rectangles for coordinate review artifacts."""
    scene_graph = _default_graph(graph)
    return [
        Rect(placement.room_id, placement.x, placement.y, placement.width, placement.height)
        for placement in scene_graph.rooms
    ]


def scene_review_rects(graph: SixRoomSceneGraph | None = None) -> list[Rect]:
    """Return both fragment-region and room-placement rectangles."""
    return scene_region_rects(graph) + scene_room_rects(graph)


def scene_bounds(graph: SixRoomSceneGraph | None = None) -> tuple[int, int]:
    """Return ``(width, height)`` for the ragged six-room scene canvas."""
    rows = render_six_room_scene_graph(_default_graph(graph))
    return (max(map(len, rows)), len(rows))


def scene_regions_at(x: int, y: int, graph: SixRoomSceneGraph | None = None) -> tuple[str, ...]:
    """Return named source regions covering a zero-based scene coordinate."""
    return tuple(
        rect.name
        for rect in scene_region_rects(graph)
        if rect.x <= x < rect.x + rect.w and rect.y <= y < rect.y + rect.h
    )


def scene_rooms_at(x: int, y: int, graph: SixRoomSceneGraph | None = None) -> tuple[str, ...]:
    """Return room ids covering a zero-based scene coordinate."""
    return tuple(
        rect.name
        for rect in scene_room_rects(graph)
        if rect.x <= x < rect.x + rect.w and rect.y <= y < rect.y + rect.h
    )


def _rects_overlap(left: Rect, right: Rect) -> bool:
    return (
        left.x < right.x + right.w
        and right.x < left.x + left.w
        and left.y < right.y + right.h
        and right.y < left.y + left.h
    )


def scene_regions_for_room(graph: SixRoomSceneGraph, room_id: str) -> tuple[str, ...]:
    """Return scene regions whose rectangles overlap a room placement."""
    room_rect = next((rect for rect in scene_room_rects(graph) if rect.name == room_id), None)
    if room_rect is None:
        return ()
    return tuple(
        region_rect.name
        for region_rect in scene_region_rects(graph)
        if _rects_overlap(room_rect, region_rect)
    )


def scene_cell_info(x: int, y: int, graph: SixRoomSceneGraph | None = None) -> SceneCellInfo:
    """Return glyph + region/room metadata for a zero-based scene coordinate."""
    scene_graph = _default_graph(graph)
    rows = render_six_room_scene_graph(scene_graph)
    char = rows[y][x] if 0 <= y < len(rows) and 0 <= x < len(rows[y]) else None
    return SceneCellInfo(
        x=x,
        y=y,
        char=char,
        regions=scene_regions_at(x, y, scene_graph),
        rooms=scene_rooms_at(x, y, scene_graph),
    )


def format_scene_room_connections(graph: SixRoomSceneGraph, room_id: str) -> str:
    """Return oriented room adjacency metadata for compact reports and HTML cells."""
    return ",".join(
        f"{connection.to_room}({connection.kind}:{connection.region_name})"
        for connection in scene_connections_for_room(graph, room_id)
    ) or "none"


def scene_room_connection_cell_attrs(graph: SixRoomSceneGraph) -> dict[tuple[int, int], dict[str, str]]:
    """Return per-cell HTML attributes for room adjacency metadata."""
    attrs: dict[tuple[int, int], dict[str, str]] = {}
    for room in graph.rooms:
        connections = format_scene_room_connections(graph, room.room_id)
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                attrs[(x, y)] = {"connections": connections}
    return attrs


def _room_center(room: SceneRoomPlacement) -> dict[str, int]:
    """Return integer center coordinate for a room rectangle."""
    return {"x": room.x + room.width // 2 - 1, "y": room.y + room.height // 2}


def six_room_scene_graph_data(graph: SixRoomSceneGraph) -> dict[str, object]:
    """Return machine-readable graph metadata for review/editor tooling."""
    width, height = scene_bounds(graph)
    rooms_by_id = {room.room_id: room for room in graph.rooms}

    def connection_center(room_id: str) -> dict[str, int] | None:
        room = rooms_by_id.get(room_id)
        return _room_center(room) if room is not None else None

    def connection_midpoint(connection: SceneConnection) -> dict[str, int] | None:
        from_center = connection_center(connection.from_room)
        to_center = connection_center(connection.to_room)
        if from_center is None or to_center is None:
            return None
        return {
            "x": (from_center["x"] + to_center["x"]) // 2,
            "y": (from_center["y"] + to_center["y"]) // 2,
        }

    return {
        "schema_version": 1,
        "bounds": {"width": width, "height": height},
        "rooms": [
            {
                "room_id": room.room_id,
                "x": room.x,
                "y": room.y,
                "width": room.width,
                "height": room.height,
                "center": _room_center(room),
                "regions": list(scene_regions_for_room(graph, room.room_id)),
                "connections": [
                    {
                        "to_room": connection.to_room,
                        "kind": connection.kind,
                        "region_name": connection.region_name,
                    }
                    for connection in scene_connections_for_room(graph, room.room_id)
                ],
            }
            for room in graph.rooms
        ],
        "connections": [
            {
                "from_room": connection.from_room,
                "to_room": connection.to_room,
                "rooms": [connection.from_room, connection.to_room],
                "kind": connection.kind,
                "region_name": connection.region_name,
                "from_center": connection_center(connection.from_room),
                "to_center": connection_center(connection.to_room),
                "midpoint": connection_midpoint(connection),
            }
            for connection in graph.connections
        ],
        "regions": [
            {
                "name": region.name,
                "start_line": region.start_line,
                "end_line": region.end_line,
                "widths": list(region.widths),
            }
            for region in graph.regions
        ],
    }


def six_room_scene_html_review(rows: list[str], rects: list[Rect], graph: SixRoomSceneGraph) -> str:
    """Return HTML review with embedded graph data, overlays, and an inspector."""
    base_html = html_review(rows, rects, scene_room_connection_cell_attrs(graph))
    graph_json = json.dumps(six_room_scene_graph_data(graph), indent=2).replace("</", "<\\/")
    cell_w = 10
    cell_h = 18
    line_offset_x = 40
    line_offset_y = 10
    width, height = scene_bounds(graph)
    rooms_by_id = {room.room_id: room for room in graph.rooms}
    overlay_width = width * cell_w + line_offset_x * 2
    overlay_height = height * cell_h + 24
    room_boxes = "\n".join(
        (
            f'<rect class="room-box" data-room-id="{escape(room.room_id, quote=True)}" '
            f'x="{room.x * cell_w + line_offset_x}" '
            f'y="{room.y * cell_h + line_offset_y}" '
            f'width="{room.width * cell_w}" '
            f'height="{room.height * cell_h}" />'
            f'<text class="room-label" data-room-id="{escape(room.room_id, quote=True)}" '
            f'x="{room.x * cell_w + line_offset_x + 6}" '
            f'y="{room.y * cell_h + line_offset_y + 16}">{escape(room.room_id)}</text>'
        )
        for room in graph.rooms
    )
    overlay_lines = "\n".join(
        (
            f'<line class="connection-line" data-connection-index="{index}" '
            f'data-from-room="{escape(connection.from_room, quote=True)}" '
            f'data-to-room="{escape(connection.to_room, quote=True)}" '
            f'x1="{_room_center(rooms_by_id[connection.from_room])["x"] * cell_w + line_offset_x}" '
            f'y1="{_room_center(rooms_by_id[connection.from_room])["y"] * cell_h + line_offset_y}" '
            f'x2="{_room_center(rooms_by_id[connection.to_room])["x"] * cell_w + line_offset_x}" '
            f'y2="{_room_center(rooms_by_id[connection.to_room])["y"] * cell_h + line_offset_y}" />'
        )
        for index, connection in enumerate(graph.connections)
        if connection.from_room in rooms_by_id and connection.to_room in rooms_by_id
    )
    overlay_html = (
        '<div class="review-controls">'
        '<button id="copy-graph-json" type="button">Copy graph JSON</button> '
        '<button id="copy-selected-room-json" type="button">Copy selected room JSON</button> '
        '<button id="reset-graph-edits" type="button">Reset edits</button> '
        '<label><input id="toggle-room-boxes" type="checkbox" checked> rooms</label> '
        '<label><input id="toggle-connection-lines" type="checkbox" checked> connections</label> '
        '<span id="graph-copy-status"></span>'
        '</div>\n'
        '<div id="graph-inspector" aria-live="polite">Select a room or connection.</div>\n'
        f'<svg id="connection-overlay" viewBox="0 0 {overlay_width} {overlay_height}" '
        'aria-label="Room and connection overlay">'
        '<g id="connection-line-layer">'
        f'{overlay_lines}'
        '</g><g id="room-box-layer">'
        f'{room_boxes}'
        '</g></svg>\n'
    )
    connection_items = "\n".join(
        "<li>"
        f"<code>{escape(connection.from_room)}</code> → <code>{escape(connection.to_room)}</code> "
        f"<span>{escape(connection.kind)} via {escape(connection.region_name)}</span>"
        "</li>"
        for connection in graph.connections
    )
    graph_block = (
        f'<script type="application/json" id="scene-graph-data">\n{graph_json}\n</script>\n'
        f"{overlay_html}"
        f"<h2>Connections</h2><ul>{connection_items}</ul>\n"
    )
    overlay_script = """
<script>
const originalSceneGraphData = JSON.parse(document.getElementById('scene-graph-data').textContent);
let sceneGraphData = structuredClone(originalSceneGraphData);
let selectedRoomId = sceneGraphData.rooms?.[0]?.room_id || null;
let selectedConnectionIndex = null;
function graphStatus(text) { document.getElementById('graph-copy-status').textContent = text; }
function roomById(roomId) { return sceneGraphData.rooms.find(room => room.room_id === roomId); }
function connectionByIndex(index) { return sceneGraphData.connections[Number(index)]; }
function connectionSummary(connection) {
  return `${connection.from_room} -> ${connection.to_room} (${connection.kind}, ${connection.region_name})`;
}
function updateLayerToggles() {
  document.getElementById('room-box-layer').style.display = document.getElementById('toggle-room-boxes').checked ? '' : 'none';
  document.getElementById('connection-line-layer').style.display = document.getElementById('toggle-connection-lines').checked ? '' : 'none';
}
function clearGraphSelection() {
  document.querySelectorAll('.room-box,.room-label,.connection-line').forEach(node => node.classList.remove('selected', 'related'));
}
function renderInspector() {
  const inspector = document.getElementById('graph-inspector');
  if (selectedConnectionIndex !== null) {
    const connection = connectionByIndex(selectedConnectionIndex);
    inspector.innerHTML = `<strong>Connection</strong><br>${connectionSummary(connection)}<br>` +
      `<label>from <input id="edit-connection-from-room" value="${connection.from_room}"></label> ` +
      `<label>to <input id="edit-connection-to-room" value="${connection.to_room}"></label> ` +
      `<label>kind <input id="edit-connection-kind" value="${connection.kind}"></label> ` +
      `<label>region <input id="edit-connection-region" value="${connection.region_name}"></label> ` +
      `<button id="apply-connection-edits" type="button">Apply connection edits</button><br>` +
      `from_center=${JSON.stringify(connection.from_center)} to_center=${JSON.stringify(connection.to_center)} midpoint=${JSON.stringify(connection.midpoint)}`;
    document.getElementById('apply-connection-edits')?.addEventListener('click', applyConnectionInspectorEdits);
    return;
  }
  const room = roomById(selectedRoomId);
  if (!room) { inspector.textContent = 'Select a room or connection.'; return; }
  inspector.innerHTML = `<strong>Room</strong> ${room.room_id}<br>` +
    `<label>id <input id="edit-room-id" value="${room.room_id}"></label> ` +
    `<label>x <input id="edit-room-x" type="number" value="${room.x}"></label> ` +
    `<label>y <input id="edit-room-y" type="number" value="${room.y}"></label> ` +
    `<label>w <input id="edit-room-width" type="number" value="${room.width}"></label> ` +
    `<label>h <input id="edit-room-height" type="number" value="${room.height}"></label> ` +
    `<label>regions <input id="edit-room-regions" value="${room.regions.join(',')}"></label> ` +
    `<button id="apply-room-edits" type="button">Apply room edits</button><br>` +
    `bounds=x${room.x}..${room.x + room.width - 1} y${room.y}..${room.y + room.height - 1} size=${room.width}x${room.height}<br>` +
    `connections=${room.connections.map(c => `${c.to_room}(${c.kind}:${c.region_name})`).join(', ')}`;
  document.getElementById('apply-room-edits')?.addEventListener('click', applyRoomInspectorEdits);
}
function selectRoom(roomId) {
  selectedRoomId = roomId;
  selectedConnectionIndex = null;
  clearGraphSelection();
  document.querySelectorAll(`[data-room-id="${CSS.escape(roomId)}"]`).forEach(node => node.classList.add('selected'));
  document.querySelectorAll(`.connection-line[data-from-room="${CSS.escape(roomId)}"], .connection-line[data-to-room="${CSS.escape(roomId)}"]`).forEach(node => node.classList.add('related'));
  document.getElementById('readout').textContent = `room ${roomId}`;
  renderInspector();
}
function selectConnection(index) {
  const connection = connectionByIndex(index);
  selectedRoomId = connection.from_room;
  selectedConnectionIndex = Number(index);
  clearGraphSelection();
  document.querySelector(`.connection-line[data-connection-index="${index}"]`)?.classList.add('selected');
  [connection.from_room, connection.to_room].forEach(roomId => {
    document.querySelectorAll(`[data-room-id="${CSS.escape(roomId)}"]`).forEach(node => node.classList.add('related'));
  });
  document.getElementById('readout').textContent = connectionSummary(connection);
  renderInspector();
}
function intFromInput(id) { return Number.parseInt(document.getElementById(id).value, 10); }
function roomCenter(room) { return {x: room.x + Math.floor(room.width / 2) - 1, y: room.y + Math.floor(room.height / 2) - 1}; }
function rebuildRoomConnectionSummaries() {
  sceneGraphData.rooms.forEach(room => { room.connections = []; });
  sceneGraphData.connections.forEach(connection => {
    const from = roomById(connection.from_room);
    const to = roomById(connection.to_room);
    if (from) from.connections.push({to_room: connection.to_room, kind: connection.kind, region_name: connection.region_name});
    if (to) to.connections.push({to_room: connection.from_room, kind: connection.kind, region_name: connection.region_name});
  });
}
function recomputeGraphAnchors() {
  sceneGraphData.rooms.forEach(room => { room.center = roomCenter(room); });
  sceneGraphData.connections.forEach(connection => {
    const from = roomById(connection.from_room);
    const to = roomById(connection.to_room);
    connection.rooms = [connection.from_room, connection.to_room];
    connection.from_center = from ? roomCenter(from) : null;
    connection.to_center = to ? roomCenter(to) : null;
    connection.midpoint = (connection.from_center && connection.to_center)
      ? {x: Math.floor((connection.from_center.x + connection.to_center.x) / 2), y: Math.floor((connection.from_center.y + connection.to_center.y) / 2)}
      : null;
  });
  rebuildRoomConnectionSummaries();
}
function updateOverlayFromGraph() {
  recomputeGraphAnchors();
  document.querySelectorAll('.room-box').forEach(box => {
    const room = roomById(box.dataset.roomId);
    if (!room) return;
    box.setAttribute('x', room.x * 10 + 40);
    box.setAttribute('y', room.y * 18 + 10);
    box.setAttribute('width', room.width * 10);
    box.setAttribute('height', room.height * 18);
  });
  document.querySelectorAll('.room-label').forEach(label => {
    const room = roomById(label.dataset.roomId);
    if (!room) return;
    label.setAttribute('x', room.x * 10 + 46);
    label.setAttribute('y', room.y * 18 + 26);
    label.textContent = room.room_id;
  });
  document.querySelectorAll('.connection-line').forEach(line => {
    const connection = connectionByIndex(line.dataset.connectionIndex);
    if (!connection?.from_center || !connection?.to_center) return;
    line.dataset.fromRoom = connection.from_room;
    line.dataset.toRoom = connection.to_room;
    line.setAttribute('x1', connection.from_center.x * 10 + 40);
    line.setAttribute('y1', connection.from_center.y * 18 + 10);
    line.setAttribute('x2', connection.to_center.x * 10 + 40);
    line.setAttribute('y2', connection.to_center.y * 18 + 10);
  });
}
function applyRoomInspectorEdits() {
  const room = roomById(selectedRoomId);
  if (!room) return;
  const oldRoomId = room.room_id;
  const newRoomId = document.getElementById('edit-room-id').value.trim();
  room.room_id = newRoomId || oldRoomId;
  room.x = intFromInput('edit-room-x');
  room.y = intFromInput('edit-room-y');
  room.width = intFromInput('edit-room-width');
  room.height = intFromInput('edit-room-height');
  room.regions = document.getElementById('edit-room-regions').value.split(',').map(value => value.trim()).filter(Boolean);
  if (room.room_id !== oldRoomId) {
    sceneGraphData.connections.forEach(connection => {
      if (connection.from_room === oldRoomId) connection.from_room = room.room_id;
      if (connection.to_room === oldRoomId) connection.to_room = room.room_id;
    });
    document.querySelectorAll(`[data-room-id="${CSS.escape(oldRoomId)}"]`).forEach(node => { node.dataset.roomId = room.room_id; });
    selectedRoomId = room.room_id;
  }
  updateOverlayFromGraph();
  selectRoom(room.room_id);
  graphStatus(`applied room edits: ${room.room_id}`);
}
function applyConnectionInspectorEdits() {
  const connection = connectionByIndex(selectedConnectionIndex);
  if (!connection) return;
  connection.from_room = document.getElementById('edit-connection-from-room').value.trim();
  connection.to_room = document.getElementById('edit-connection-to-room').value.trim();
  connection.kind = document.getElementById('edit-connection-kind').value.trim();
  connection.region_name = document.getElementById('edit-connection-region').value.trim();
  updateOverlayFromGraph();
  selectConnection(selectedConnectionIndex);
  graphStatus(`applied connection edits: ${connectionSummary(connection)}`);
}
function resetGraphEdits() {
  sceneGraphData = structuredClone(originalSceneGraphData);
  selectedRoomId = sceneGraphData.rooms?.[0]?.room_id || null;
  selectedConnectionIndex = null;
  updateOverlayFromGraph();
  if (selectedRoomId) selectRoom(selectedRoomId);
  graphStatus('reset graph edits');
}
function copyGraphJson() {
  const text = JSON.stringify(sceneGraphData, null, 2);
  navigator.clipboard?.writeText(text);
  graphStatus('copied full graph JSON');
  return text;
}
function copySelectedRoomJson() {
  const room = roomById(selectedRoomId) || sceneGraphData.rooms[0];
  const text = JSON.stringify(room, null, 2);
  navigator.clipboard?.writeText(text);
  graphStatus(`copied room ${room?.room_id || 'none'}`);
  return text;
}
function drawConnectionOverlay() {
  document.querySelectorAll('.connection-line').forEach(line => line.addEventListener('click', () => selectConnection(line.dataset.connectionIndex)));
  document.querySelectorAll('.room-box,.room-label').forEach(node => node.addEventListener('click', () => selectRoom(node.dataset.roomId)));
  document.getElementById('toggle-room-boxes')?.addEventListener('change', updateLayerToggles);
  document.getElementById('toggle-connection-lines')?.addEventListener('change', updateLayerToggles);
  updateLayerToggles();
  if (selectedRoomId) selectRoom(selectedRoomId);
}
document.getElementById('copy-graph-json')?.addEventListener('click', copyGraphJson);
document.getElementById('copy-selected-room-json')?.addEventListener('click', copySelectedRoomJson);
document.getElementById('reset-graph-edits')?.addEventListener('click', resetGraphEdits);
drawConnectionOverlay();
</script>
"""
    overlay_css = "#connection-overlay { width:100%; height:330px; border:1px solid #5b5130; background:#171611; margin:10px 0; }\n.connection-line { stroke:#f6cf63; stroke-width:3; opacity:.65; cursor:pointer; }\n.connection-line:hover,.connection-line.selected { stroke:#72d6ff; opacity:1; stroke-width:5; }\n.connection-line.related { stroke:#9fd18b; opacity:.95; }\n.room-box { fill:rgba(114,214,255,.08); stroke:#72d6ff; stroke-width:2; stroke-dasharray:7 4; cursor:pointer; }\n.room-box:hover,.room-box.selected { fill:rgba(246,207,99,.16); stroke:#f6cf63; stroke-width:4; }\n.room-box.related { fill:rgba(159,209,139,.12); stroke:#9fd18b; }\n.room-label { fill:#d9d0b0; font:12px monospace; pointer-events:auto; cursor:pointer; }\n.room-label.selected,.room-label.related { fill:#ffd36d; font-weight:bold; }\n.review-controls { margin:10px 0; }\n.review-controls button { background:#2a261a; color:#ffd36d; border:1px solid #5b5130; padding:6px 8px; cursor:pointer; }\n.review-controls label { margin-left:10px; color:#d9d0b0; }\n#graph-inspector input { width:80px; background:#211d14; color:#f3e8c2; border:1px solid #5b5130; margin:2px; }\n#graph-inspector button { background:#2a261a; color:#ffd36d; border:1px solid #5b5130; padding:4px 6px; cursor:pointer; }\n#graph-copy-status { margin-left:10px; color:#9fd18b; }\n#graph-inspector { border:1px solid #5b5130; background:#15130d; padding:8px; margin:8px 0; color:#d9d0b0; min-height:54px; }\n#readout {{"
    return (
        base_html
        .replace("#readout {{", overlay_css, 1)
        .replace("<script>\n", graph_block + "<script>\n", 1)
        .replace("</script>\n", "</script>\n" + overlay_script, 1)
    )


def write_six_room_scene_artifacts(output_dir: Path, graph: SixRoomSceneGraph | None = None) -> list[Path]:
    """Write generated scene text, coordinate annotations, and HTML review."""
    output_dir.mkdir(parents=True, exist_ok=True)
    graph = graph or build_six_room_scene_graph()
    rows = render_six_room_scene_graph(graph)
    rects = scene_review_rects(graph)

    scene_path = output_dir / "six_room_scene_generated.txt"
    annotated_path = output_dir / "six_room_scene_generated_annotated.txt"
    html_path = output_dir / "six_room_scene_generated.html"
    graph_json_path = output_dir / "six_room_scene_graph.json"

    write_text(scene_path, rows)
    annotated_path.write_text(annotate(rows, rects), encoding="utf-8")
    html_path.write_text(
        six_room_scene_html_review(rows, rects, graph),
        encoding="utf-8",
    )
    graph_json_path.write_text(
        json.dumps(six_room_scene_graph_data(graph), indent=2) + "\n",
        encoding="utf-8",
    )

    return [scene_path, annotated_path, html_path, graph_json_path]


def _parse_cell_arg(value: str) -> tuple[int, int]:
    """Parse a zero-based ``X,Y`` coordinate argument."""
    try:
        x_text, y_text = value.split(",", 1)
        return (int(x_text), int(y_text))
    except ValueError as exc:
        raise ValueError("cell must be formatted as X,Y with zero-based integers") from exc


def format_scene_cell_info(info: SceneCellInfo) -> str:
    """Return a compact human-readable line for one scene cell."""
    if info.char is None:
        shown = "OUT_OF_BOUNDS"
    elif info.char == " ":
        shown = "SPACE"
    else:
        shown = info.char
    regions = ",".join(info.regions) if info.regions else "none"
    rooms = ",".join(info.rooms) if info.rooms else "none"
    return f"L{info.y:02d} C{info.x:03d} char={shown} regions={regions} rooms={rooms}"


def format_scene_room_summary(room: SceneRoomPlacement) -> str:
    """Return a compact room id + bounds summary line."""
    return (
        f"{room.room_id} x{room.x}..{room.x + room.width - 1} "
        f"y{room.y}..{room.y + room.height - 1} size={room.width}x{room.height}"
    )


def format_scene_connection_summary(connection: SceneConnection) -> str:
    """Return a compact directed graph-edge summary line."""
    return (
        f"{connection.from_room} -> {connection.to_room} "
        f"kind={connection.kind} region={connection.region_name}"
    )


def format_scene_room_info(graph: SixRoomSceneGraph, room_id: str) -> str:
    """Return room bounds and oriented adjacency metadata for one room."""
    rooms_by_id = {room.room_id: room for room in graph.rooms}
    room = rooms_by_id.get(room_id)
    if room is None:
        return f"room {room_id} not found"
    regions = scene_regions_for_room(graph, room_id)
    connection_text = format_scene_room_connections(graph, room_id)
    region_text = ",".join(regions) if regions else "none"
    return (
        f"room {room.room_id} bounds=x{room.x}..{room.x + room.width - 1} "
        f"y{room.y}..{room.y + room.height - 1} size={room.width}x{room.height} "
        f"regions={region_text} connections={connection_text}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="Generate six-room scene review artifacts.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory for generated .txt/.annotated.txt/.html artifacts (default: this file's folder).",
    )
    parser.add_argument(
        "--cell",
        metavar="X,Y",
        help="Also print metadata for a zero-based scene coordinate, e.g. --cell 0,4.",
    )
    parser.add_argument(
        "--room",
        metavar="ROOM_ID",
        help="Also print bounds and adjacency metadata for a room id, e.g. --room upper_middle.",
    )
    parser.add_argument(
        "--list-rooms",
        action="store_true",
        help="Also print compact bounds for every room in graph order.",
    )
    parser.add_argument(
        "--list-connections",
        action="store_true",
        help="Also print every graph connection in deterministic graph order.",
    )
    parser.add_argument(
        "--validate-graph",
        action="store_true",
        help="Also print graph validation status and any validation errors.",
    )
    parser.add_argument(
        "--print-graph-json",
        action="store_true",
        help="Print only the machine-readable graph JSON to stdout.",
    )
    parser.add_argument(
        "--graph-json",
        type=Path,
        help="Load an exported graph JSON file for validation or normalized printing.",
    )
    args = parser.parse_args(argv)

    if args.graph_json:
        graph_data = json.loads(args.graph_json.read_text(encoding="utf-8"))
        if args.print_graph_json:
            print(json.dumps(graph_data, indent=2))
            return 0
        if args.validate_graph:
            errors = validate_six_room_scene_graph_data(graph_data)
            if errors:
                print("graph json validation: failed")
                for error in errors:
                    print(f"graph json validation error: {error}")
                return 1
            print("graph json validation: ok")
            return 0
        print(f"loaded graph json: {args.graph_json.resolve()}")
        return 0

    graph = build_six_room_scene_graph()
    if args.print_graph_json:
        print(json.dumps(six_room_scene_graph_data(graph), indent=2))
        return 0

    written = write_six_room_scene_artifacts(args.output_dir, graph)
    width, height = scene_bounds(graph)
    print(f"six-room scene bounds: width={width} height={height}")
    for path in written:
        print(path.resolve())

    if args.cell:
        x, y = _parse_cell_arg(args.cell)
        print(format_scene_cell_info(scene_cell_info(x, y, graph)))

    if args.room:
        print(format_scene_room_info(graph, args.room))

    if args.list_rooms:
        for room in graph.rooms:
            print(format_scene_room_summary(room))

    if args.list_connections:
        for connection in graph.connections:
            print(format_scene_connection_summary(connection))

    if args.validate_graph:
        errors = validate_six_room_scene_graph(graph)
        if errors:
            print("graph validation: failed")
            for error in errors:
                print(f"graph validation error: {error}")
        else:
            print("graph validation: ok")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
