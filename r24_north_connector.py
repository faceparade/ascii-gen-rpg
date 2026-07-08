#!/usr/bin/env python3
"""Port-aware R24 north connector experiment.

This module keeps the locked R24 stamp and existing room baselines unchanged. It
adds a small geometry layer that treats the downward R24 tail as a port, maps it
to a chunk-based NorthWall opening, and renders separate review artifacts.

Rendering now goes through modular_canvas.ModularCanvas so paste semantics are
explicit (opaque for solid stamps, transparent-space for overlay fragments).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from connector_specs import NorthConnectorSpec
from curved_dungeon_grammar import (
    OUT_DIR,
    Rect,
    annotate,
    html_review,
    regular_vertical_pathway,
    room_shell_middle_8,
    wide_platform,
)
from modular_ascii_parts import CHUNK_GLYPH_W, Opening, NorthWall
from modular_canvas import ModularCanvas, OPAQUE, TRANSPARENT_SPACE
from three_room_macro_test import (
    WIDE_PLATFORM_ROOM_OFFSET_X,
    WIDE_PLATFORM_ROOM_OFFSET_Y,
    build_three_room_macro_test,
)

PATHWAY_W = 27
ROOM_CHUNKS = 8
ROOM_W = 35
ROOM_H = 12
DEFAULT_ROOM2_X = 57
DEFAULT_ROOM_Y = 3


@dataclass(frozen=True)
class R24TailPort:
    """Side-wall bounds for the downward tail in the locked R24 stamp."""

    left: int
    right: int
    row: int

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def sidewall_delta(self) -> int:
        return self.right - self.left

    @property
    def suggested_opening_width_chunks(self) -> int:
        """Smallest NorthWall opening preset whose interior sidewalls fit R24.

        The current NorthWall plain opening has a useful sidewall-fit span of
        `4 * chunks - 2`: for a 2-chunk opening this is 6 columns, exactly the
        distance between R24's tail side-wall pipes (C10 and C16).
        """
        for chunks in range(1, ROOM_CHUNKS + 1):
            if CHUNK_GLYPH_W * chunks - 2 >= self.sidewall_delta:
                return chunks
        raise ValueError("R24 tail is wider than the supported 8-chunk north wall")


def r24_tail_port(stamp: list[str] | None = None) -> R24TailPort:
    """Derive the R24 tail side-wall bounds from the locked stamp's tail row."""
    rows = regular_vertical_pathway(6) if stamp is None else stamp
    if not rows:
        raise ValueError("R24 stamp is empty")
    tail_row_index = len(rows) - 1
    tail = rows[tail_row_index]
    left = tail.index("|")
    right = tail.rindex("|")
    if left == right:
        raise ValueError("R24 tail row must contain left and right side-wall pipes")
    return R24TailPort(left=left, right=right, row=tail_row_index)


@dataclass(frozen=True)
class R24NorthConnector:
    """Place a locked R24 stamp so its tail port lands in a NorthWall opening."""

    room_x: int = DEFAULT_ROOM2_X
    room_y: int = DEFAULT_ROOM_Y
    # Reference-style north join from Tristan's hand correction. This is a
    # near top-down / Diablo-ish isometric north-edge join. The visible upper
    # fragment sits north of the room, while the room's
    # north wall/edge uses a compact `j  ,t` corner.
    opening: Opening = Opening(6, 1)
    pathway_width_units: int = 6

    @property
    def stamp(self) -> list[str]:
        return regular_vertical_pathway(self.pathway_width_units)

    @property
    def reference_upper_rows(self) -> list[tuple[int, str]]:
        """Visible upper fragment from the current hand reference.

        Offsets are relative to room_x. Row 2 is intentionally narrower than
        the locked R24 tail: this style shows `|  /|` just north of the room
        edge, while the north wall/edge row below carries the `j  ,t` corner
        join.
        """
        return [
            (8, "|  `   `   `   `   `  '/|"),
            (8, "'- - - - - -.   .- - - -'"),
            (20, "|  /|"),
        ]

    @property
    def spec(self) -> NorthConnectorSpec:
        return NorthConnectorSpec(
            name="r24_reference_north",
            room_x=self.room_x,
            room_y=self.room_y,
            room_chunks=ROOM_CHUNKS,
            opening=self.opening,
            upper_rows=tuple(self.reference_upper_rows),
        )

    @property
    def upper_fragment_x(self) -> int:
        return self.spec.upper_fragment_origin[0]

    @property
    def port(self) -> R24TailPort:
        return r24_tail_port(self.stamp)

    @property
    def opening_start_x(self) -> int:
        return self.spec.opening_start_x

    @property
    def opening_fit_right_x(self) -> int:
        return self.opening_start_x + CHUNK_GLYPH_W * self.opening.width_chunks - 2

    @property
    def stamp_x(self) -> int:
        return self.opening_start_x - self.port.left

    @property
    def stamp_y(self) -> int:
        return self.spec.upper_fragment_y

    @property
    def tail_left_x(self) -> int:
        return self.stamp_x + self.port.left

    @property
    def tail_right_x(self) -> int:
        return self.stamp_x + self.port.right

    def validate(self) -> None:
        # Let NorthConnectorSpec/NorthWall validate edge/full-wall cap rules and unsupported skins.
        self.spec.validate()
        if self.opening.start_chunk != 6 or self.opening.width_chunks != 1:
            raise ValueError("reference-style R24 north join currently expects Opening(6, 1)")


def _replace_north_wall(canvas: ModularCanvas, connector: R24NorthConnector) -> None:
    NorthWall(ROOM_CHUNKS, (connector.opening,)).draw_on(
        canvas, connector.room_x, connector.room_y, OPAQUE
    )


def _paste_reference_upper_fragment(canvas: ModularCanvas, connector: R24NorthConnector) -> None:
    for dy, (dx, row) in enumerate(connector.reference_upper_rows):
        canvas.paste_stamp(
            [row],
            connector.room_x + dx,
            connector.stamp_y + dy,
            TRANSPARENT_SPACE,
            source="ref_upper_fragment",
            layer="connector",
        )


def build_r24_room2_only_case(connector: R24NorthConnector | None = None) -> list[str]:
    """Render a shifted single room-2 scene with the R24 connector stamped in."""
    c = connector or R24NorthConnector()
    c.validate()
    width = max(c.room_x + ROOM_W + 1, c.stamp_x + PATHWAY_W)
    height = max(c.room_y + ROOM_H, c.stamp_y + len(c.stamp))
    canvas = ModularCanvas(width, height)
    canvas.paste_stamp(
        room_shell_middle_8(), c.room_x, c.room_y, OPAQUE, source="room_shell", layer="room"
    )
    canvas.paste_stamp(
        wide_platform(4),
        c.room_x + WIDE_PLATFORM_ROOM_OFFSET_X,
        c.room_y + WIDE_PLATFORM_ROOM_OFFSET_Y,
        OPAQUE,
        source="wide_platform",
        layer="room",
    )
    _replace_north_wall(canvas, c)
    _paste_reference_upper_fragment(canvas, c)
    return canvas.render_lines()


def build_r24_three_room_case(connector: R24NorthConnector | None = None) -> list[str]:
    """Render the existing three-room macro test shifted down, then add R24."""
    c = connector or R24NorthConnector()
    c.validate()
    base = build_three_room_macro_test()
    width = max(max(len(row) for row in base), c.stamp_x + PATHWAY_W)
    height = max(c.room_y + len(base), c.stamp_y + len(c.stamp))
    canvas = ModularCanvas(width, height)
    for y, row in enumerate(base):
        canvas.paste_stamp([row], 0, c.room_y + y, OPAQUE, source="three_room_base", layer="room")
    _replace_north_wall(canvas, c)
    _paste_reference_upper_fragment(canvas, c)
    return canvas.render_lines()


def connector_regions(connector: R24NorthConnector, scene_name: str) -> list[Rect]:
    spec = connector.spec
    north_x, north_y, north_w, north_h = spec.north_wall_region
    open_x, open_y, open_w, open_h = spec.opening_window
    base_regions = [
        Rect("REFERENCE_UPPER_NORTH_FRAGMENT", connector.upper_fragment_x, connector.stamp_y, 25, 3),
        Rect("REFERENCE_TAIL_ABOVE_NORTH_EDGE", open_x, connector.stamp_y + 2, 5, 1),
        Rect("ROOM2_NORTH_WALL_WITH_OPENING", north_x, north_y, north_w, north_h),
        Rect(
            f"NORTHWALL_OPENING_CHUNKS_{connector.opening.start_chunk}_{connector.opening.end_chunk}",
            open_x,
            open_y,
            open_w,
            open_h,
        ),
    ]
    if scene_name == "room2_only":
        base_regions.append(Rect("ROOM2_ONLY_SHIFTED_SHELL", connector.room_x, connector.room_y, ROOM_W, ROOM_H))
    else:
        base_regions.extend(
            [
                Rect("THREE_ROOM_BASE_SHIFTED", 0, connector.room_y, 150, ROOM_H),
                Rect("ROOM2_IN_THREE_ROOM_BASE", connector.room_x, connector.room_y, ROOM_W, ROOM_H),
            ]
        )
    return base_regions


def _write_text(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")


def _port_report(connector: R24NorthConnector) -> list[str]:
    port = connector.port
    return [
        "Reference-style R24 north connector report",
        f"locked R24 tail bounds retained for metadata: row={port.row}, left={port.left}, right={port.right}, width={port.width}, delta={port.sidewall_delta}",
        "rendered style: reference upper fragment + generated NorthWall compact corner opening",
        f"selected opening: start_chunk={connector.opening.start_chunk}, end_chunk={connector.opening.end_chunk}, width_chunks={connector.opening.width_chunks}",
        f"room origin: x={connector.room_x}, y={connector.room_y}",
        f"upper fragment origin: x={connector.upper_fragment_x}, y={connector.stamp_y}",
        f"tail-above-north-edge globals: left={connector.opening_start_x}, right={connector.opening_start_x + 4}",
        f"north-edge opening corner: j at x={connector.opening_start_x}, t at x={connector.opening_start_x + 4}",
    ]


def write_r24_connector_artifacts(out_dir: Path | str = OUT_DIR, connector: R24NorthConnector | None = None) -> list[Path]:
    """Write room2-only and three-room R24 connector review artifacts."""
    c = connector or R24NorthConnector()
    c.validate()
    out = Path(out_dir)
    written: list[Path] = []

    scenes = {
        "room2_only": build_r24_room2_only_case(c),
        "three_room": build_r24_three_room_case(c),
    }
    for name, lines in scenes.items():
        stem = out / f"r24_north_connector_{name}"
        txt = stem.with_suffix(".txt")
        ann = Path(str(stem) + "_annotated.txt")
        html = stem.with_suffix(".html")
        _write_text(txt, lines)
        ann.write_text(annotate(lines, connector_regions(c, name)), encoding="utf-8")
        html.write_text(html_review(lines, connector_regions(c, name)), encoding="utf-8")
        written.extend([txt, ann, html])

    report = out / "r24_north_connector_port_report.txt"
    _write_text(report, _port_report(c))
    written.append(report)
    return written


def main() -> None:
    for path in write_r24_connector_artifacts():
        print(path)
    print("R24 north connector artifacts written")


if __name__ == "__main__":
    main()
