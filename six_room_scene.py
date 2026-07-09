#!/usr/bin/env python3
"""Six-room scene generator assembled from locked named fragments."""
from __future__ import annotations

from argparse import ArgumentParser
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


def assemble_six_room_scene_rows() -> list[str]:
    """Rebuild the locked six-room source through the six-room scene graph."""
    return render_six_room_scene_graph(build_six_room_scene_graph())


def scene_region_rects() -> list[Rect]:
    """Return named source-region rectangles for coordinate review artifacts."""
    return [
        Rect(
            region.name,
            0,
            region.start_line - 1,
            max(region.widths) if region.widths else 0,
            len(region.rows),
        )
        for region in scene_regions()
    ]


def scene_room_rects() -> list[Rect]:
    """Return room-placement rectangles for coordinate review artifacts."""
    return [
        Rect(placement.room_id, placement.x, placement.y, placement.width, placement.height)
        for placement in six_room_placements()
    ]


def scene_review_rects() -> list[Rect]:
    """Return both fragment-region and room-placement rectangles."""
    return scene_region_rects() + scene_room_rects()


def scene_bounds() -> tuple[int, int]:
    """Return ``(width, height)`` for the ragged six-room scene canvas."""
    rows = assemble_six_room_scene_rows()
    return (max(map(len, rows)), len(rows))


def scene_regions_at(x: int, y: int) -> tuple[str, ...]:
    """Return named source regions covering a zero-based scene coordinate."""
    return tuple(
        rect.name
        for rect in scene_region_rects()
        if rect.x <= x < rect.x + rect.w and rect.y <= y < rect.y + rect.h
    )


def scene_rooms_at(x: int, y: int) -> tuple[str, ...]:
    """Return room ids covering a zero-based scene coordinate."""
    return tuple(
        rect.name
        for rect in scene_room_rects()
        if rect.x <= x < rect.x + rect.w and rect.y <= y < rect.y + rect.h
    )


def scene_cell_info(x: int, y: int) -> SceneCellInfo:
    """Return glyph + region/room metadata for a zero-based scene coordinate."""
    rows = assemble_six_room_scene_rows()
    char = rows[y][x] if 0 <= y < len(rows) and 0 <= x < len(rows[y]) else None
    return SceneCellInfo(
        x=x,
        y=y,
        char=char,
        regions=scene_regions_at(x, y),
        rooms=scene_rooms_at(x, y),
    )


def write_six_room_scene_artifacts(output_dir: Path, graph: SixRoomSceneGraph | None = None) -> list[Path]:
    """Write generated scene text, coordinate annotations, and HTML review."""
    output_dir.mkdir(parents=True, exist_ok=True)
    graph = graph or build_six_room_scene_graph()
    rows = render_six_room_scene_graph(graph)
    rects = scene_review_rects()

    scene_path = output_dir / "six_room_scene_generated.txt"
    annotated_path = output_dir / "six_room_scene_generated_annotated.txt"
    html_path = output_dir / "six_room_scene_generated.html"

    write_text(scene_path, rows)
    annotated_path.write_text(annotate(rows, rects), encoding="utf-8")
    html_path.write_text(html_review(rows, rects), encoding="utf-8")

    return [scene_path, annotated_path, html_path]


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
    args = parser.parse_args(argv)

    written = write_six_room_scene_artifacts(args.output_dir)
    width, height = scene_bounds()
    print(f"six-room scene bounds: width={width} height={height}")
    for path in written:
        print(path.resolve())

    if args.cell:
        x, y = _parse_cell_arg(args.cell)
        print(format_scene_cell_info(scene_cell_info(x, y)))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
