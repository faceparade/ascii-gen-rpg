#!/usr/bin/env python3
"""Six-room scene generator assembled from locked named fragments."""
from __future__ import annotations

from argparse import ArgumentParser
import json
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


def six_room_scene_graph_data(graph: SixRoomSceneGraph) -> dict[str, object]:
    """Return machine-readable graph metadata for review/editor tooling."""
    width, height = scene_bounds(graph)
    return {
        "bounds": {"width": width, "height": height},
        "rooms": [
            {
                "room_id": room.room_id,
                "x": room.x,
                "y": room.y,
                "width": room.width,
                "height": room.height,
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
                "kind": connection.kind,
                "region_name": connection.region_name,
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
        html_review(rows, rects, scene_room_connection_cell_attrs(graph)),
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
    args = parser.parse_args(argv)

    graph = build_six_room_scene_graph()
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
