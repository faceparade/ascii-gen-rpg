#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Iterable, Literal

from style_sample_system import Point, SECTION_STRIDE_X, SECTION_STRIDE_Y

WALLS_ON = (
    "  ,— —,— —,— —,— —, ",
    " /|__/___/___/__ /|",
    "‘ |             | |",
    "|/| `   `   `   |/|",
    "| |             | |",
    "|/| `   `   `   |/|",
    "| |             | |",
    "|/| `   `   `   |/|",
    "| ,— —,— —,— —,—‘—,",
    "‘/___/___/___/___/ ",
)

SOUTH_WEST_OFF = (
    "  ,— —,— —,— —,— —, ",
    " /___/___/___/__ /|",
    "‘               | |",
    "|   `   `   `   |/|",
    "|               | |",
    "|   `   `   `   |/|",
    "|               | |",
    "|   `   `   `   |/|",
    "|               | ,",
    "‘ ___ ___ ___ ___/ ",
)

GRID_COLUMNS = 4
GRID_ROWS = 4
CENTER_ORIGIN = Point(2, 2)


@dataclass(frozen=True)
class Entity:
    section: Point
    glyph: str

    def __post_init__(self) -> None:
        if len(self.glyph) != 1 or self.glyph.isspace():
            raise ValueError("entity glyph must be one visible character")


@dataclass(frozen=True)
class Projection:
    rows: tuple[str, ...]
    occluded_screen_points: frozenset[Point]
    hidden_sections: frozenset[Point]
    revealed_sections: frozenset[Point] = frozenset()


def section_center(section: Point) -> Point:
    if not (0 <= section.x < GRID_COLUMNS and 0 <= section.y < GRID_ROWS):
        raise ValueError(f"section outside 4x4 diagnostic grid: {section}")
    return Point(
        CENTER_ORIGIN.x + section.x * SECTION_STRIDE_X,
        CENTER_ORIGIN.y + section.y * SECTION_STRIDE_Y,
    )


def section_occluders(
    section: Point,
    *,
    south_west_walls: bool = True,
    east_wall: bool = True,
) -> frozenset[str]:
    section_center(section)
    result: set[str] = set()
    if south_west_walls and section.x == 0:
        result.add("west")
    if south_west_walls and section.y == GRID_ROWS - 1:
        result.add("south")
    _ = east_wall
    return frozenset(result)


def floor_only_rows() -> tuple[str, ...]:
    width = max(map(len, WALLS_ON))
    canvas = [[" " for _ in range(width)] for _ in WALLS_ON]
    return tuple("".join(row) for row in canvas)


def compose(
    entities: Iterable[Entity],
    *,
    wall_view: Literal["on", "south-west-off", "floor-only"] = "on",
    occlusion_mode: Literal["opaque", "xray"] = "opaque",
    mark_revealed: bool = False,
    show_lattice: bool = True,
) -> Projection:
    if wall_view == "on":
        rows, south_west, east = WALLS_ON, True, True
    elif wall_view == "south-west-off":
        rows, south_west, east = SOUTH_WEST_OFF, False, True
    elif wall_view == "floor-only":
        rows, south_west, east = floor_only_rows(), False, False
    else:
        raise ValueError(f"unsupported wall view: {wall_view!r}")

    width = max(map(len, rows))
    canvas = [list(row.ljust(width)) for row in rows]
    if not show_lattice:
        for row in canvas:
            for x, glyph in enumerate(row):
                if glyph == "`":
                    row[x] = " "
    used: set[Point] = set()
    gray: set[Point] = set()
    hidden: set[Point] = set()
    revealed: set[Point] = set()

    for entity in entities:
        if entity.section in used:
            raise ValueError(f"multiple entities occupy {entity.section}")
        used.add(entity.section)
        screen = section_center(entity.section)
        occluders = section_occluders(
            entity.section,
            south_west_walls=south_west,
            east_wall=east,
        )
        reference_occluders = section_occluders(
            entity.section,
            south_west_walls=True,
            east_wall=True,
        )

        if occluders and occlusion_mode == "opaque":
            hidden.add(entity.section)
            continue

        reveal_marker = mark_revealed and not occluders and bool(reference_occluders)
        dimmed = bool(occluders) or reveal_marker
        glyph = entity.glyph.lower() if dimmed and entity.glyph.isalpha() else entity.glyph
        canvas[screen.y][screen.x] = glyph

        if occluders:
            gray.add(screen)
        if reveal_marker:
            revealed.add(entity.section)

    return Projection(
        rows=tuple("".join(row).rstrip() for row in canvas),
        occluded_screen_points=frozenset(gray),
        hidden_sections=frozenset(hidden),
        revealed_sections=frozenset(revealed),
    )


def diagnostic_entities() -> tuple[Entity, ...]:
    letters = "ABCDEFGHIJKLMNOP"
    return tuple(
        Entity(Point(x, y), letters[y * GRID_COLUMNS + x])
        for y in range(GRID_ROWS)
        for x in range(GRID_COLUMNS)
    )


def render_text() -> str:
    entities = diagnostic_entities()
    views = (
        ("REFERENCE — SOUTH/WEST FOREGROUND WALLS ON", Projection(WALLS_ON, frozenset(), frozenset())),
        ("REFERENCE — SOUTH/WEST FOREGROUND WALLS REMOVED", Projection(SOUTH_WEST_OFF, frozenset(), frozenset())),
        ("LOGICAL 4x4 SECTION MAP — ALL WALLS REMOVED", compose(entities, wall_view="floor-only")),
        ("ENTITIES — WALLS ON, OPAQUE", compose(entities, wall_view="on", show_lattice=False)),
        ("ENTITIES — WALLS ON, X-RAY (lowercase = occluded)", compose(entities, wall_view="on", occlusion_mode="xray", show_lattice=False)),
        ("ENTITIES — SOUTH/WEST OFF, EAST WALL RETAINED", compose(entities, wall_view="south-west-off", mark_revealed=True, show_lattice=False)),
    )
    lines = [
        "FOREGROUND WALL AND ENTITY OCCLUSION DIAGNOSTIC",
        "Each letter occupies one logical floor section.",
        "",
    ]
    for title, view in views:
        lines.extend((title, "-" * len(title), *view.rows, ""))
    return "\n".join(lines).rstrip() + "\n"


def highlighted_pre(view: Projection) -> str:
    lines = []
    revealed_points = {section_center(section) for section in view.revealed_sections}
    for y, row in enumerate(view.rows):
        chars = []
        for x, glyph in enumerate(row):
            safe = escape(glyph)
            point = Point(x, y)
            if point in view.occluded_screen_points:
                chars.append(f'<span class="occluded">{safe}</span>')
            elif point in revealed_points:
                chars.append(f'<span class="revealed">{safe}</span>')
            else:
                chars.append(safe)
        lines.append("".join(chars))
    return "\n".join(lines)


def render_html() -> str:
    entities = diagnostic_entities()
    views = (
        ("Foreground walls on", Projection(WALLS_ON, frozenset(), frozenset())),
        ("South/west faces removed", Projection(SOUTH_WEST_OFF, frozenset(), frozenset())),
        ("Logical 4×4 section map", compose(entities, wall_view="floor-only")),
        ("Entities, opaque walls", compose(entities, wall_view="on", show_lattice=False)),
        ("Entities, x-ray walls", compose(entities, wall_view="on", occlusion_mode="xray", show_lattice=False)),
        ("Entities, south/west off", compose(entities, wall_view="south-west-off", mark_revealed=True, show_lattice=False)),
    )
    cards = "".join(
        f"<section><h2>{escape(title)}</h2><pre>{highlighted_pre(view)}</pre></section>"
        for title, view in views
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Foreground wall occlusion diagnostic</title><style>
body{{margin:0;background:#11100d;color:#e8dfc4;font:15px/1.45 system-ui,sans-serif}}
main{{max-width:1100px;margin:auto;padding:28px}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}
section{{border:1px solid #514a38;background:#181610;padding:16px;min-width:0}}h1,h2{{color:#f3d37a}}
pre{{overflow:auto;padding:14px;background:#0c0c0b;border:1px solid #383327;color:#f2ead1;font:18px/1.2 "Cascadia Mono",Consolas,monospace}}
.occluded{{color:#777;background:#242424}}.revealed{{color:#9ea9b5}}
@media(max-width:760px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><main><h1>Foreground wall and entity occlusion diagnostic</h1>
<p>Uppercase letters are unobstructed. Gray lowercase letters are seen through a wall. Muted lowercase letters mark sections revealed by removing the south/west walls.</p>
<div class="grid">{cards}</div><h2>Confirmed finding</h2>
<p>West covers A/E/I/M; south covers M/N/O/P; M is covered by both. The retained east wall covers no one-character centers.</p>
</main></body></html>\n'''


def write_outputs(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    text_path = output_dir / "foreground_occlusion_v2_generated.txt"
    html_path = output_dir / "foreground_occlusion_v2_generated.html"
    text_path.write_text(render_text(), encoding="utf-8")
    html_path.write_text(render_html(), encoding="utf-8")
    return text_path, html_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("style_samples/output"))
    args = parser.parse_args()
    for path in write_outputs(args.output):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
