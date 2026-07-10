#!/usr/bin/env python3
"""Generate reviewable ASCII structure samples from logical floor-section masks.

Generated drafts are disposable. Hand-edited targets are stored separately so
regeneration never destroys approved style work.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Iterable

SECTION_WIDTH = 5
SECTION_HEIGHT = 3
SECTION_STRIDE_X = 4
SECTION_STRIDE_Y = 2
SECTION_CENTER_X = 2
SECTION_CENTER_Y = 1
CELL_WIDTH = SECTION_STRIDE_X
CELL_HEIGHT = SECTION_STRIDE_Y
VALID_STATUS = {"generated", "reviewing", "approved", "promoted"}


@dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class ShapeSample:
    sample_id: str
    title: str
    category: str
    mask: tuple[str, ...]
    tags: tuple[str, ...] = ()
    notes: str = ""
    status: str = "generated"

    def __post_init__(self) -> None:
        allowed = "abcdefghijklmnopqrstuvwxyz0123456789-_"
        if not self.sample_id or any(ch not in allowed for ch in self.sample_id):
            raise ValueError(f"invalid sample id: {self.sample_id!r}")
        if self.status not in VALID_STATUS:
            raise ValueError(f"invalid status for {self.sample_id}: {self.status!r}")
        cells_from_mask(self.mask)


@dataclass(frozen=True)
class SampleRender:
    sample: ShapeSample
    mask_rows: tuple[str, ...]
    draft_rows: tuple[str, ...]
    target_rows: tuple[str, ...] | None


class StrokeGrid:
    """Sparse orthogonal stroke graph for coarse irregular outlines."""

    def __init__(self) -> None:
        self.connections: dict[Point, set[str]] = {}
        self.roles: dict[Point, set[str]] = {}

    def _point(self, point: Point) -> set[str]:
        return self.connections.setdefault(point, set())

    def add_horizontal(self, x0: int, x1: int, y: int, role: str) -> None:
        for x in range(x0, x1):
            left, right = Point(x, y), Point(x + 1, y)
            self._point(left).add("E")
            self._point(right).add("W")
            self.roles.setdefault(left, set()).add(role)
            self.roles.setdefault(right, set()).add(role)

    def add_vertical(self, x: int, y0: int, y1: int, role: str) -> None:
        for y in range(y0, y1):
            top, bottom = Point(x, y), Point(x, y + 1)
            self._point(top).add("S")
            self._point(bottom).add("N")
            self.roles.setdefault(top, set()).add(role)
            self.roles.setdefault(bottom, set()).add(role)


def cells_from_mask(mask: Iterable[str]) -> frozenset[Point]:
    rows = tuple(mask)
    if not rows:
        raise ValueError("mask must have at least one row")
    width = max(map(len, rows), default=0)
    unexpected = {ch for row in rows for ch in row if ch not in {"#", ".", " "}}
    if unexpected:
        raise ValueError(f"mask has unsupported characters: {sorted(unexpected)!r}")
    cells = {
        Point(x, y)
        for y, row in enumerate(rows)
        for x, ch in enumerate(row.ljust(width, "."))
        if ch == "#"
    }
    if not cells:
        raise ValueError("mask must contain at least one # cell")
    return normalize_cells(cells)


def normalize_cells(cells: Iterable[Point]) -> frozenset[Point]:
    cells = frozenset(cells)
    if not cells:
        return cells
    min_x = min(p.x for p in cells)
    min_y = min(p.y for p in cells)
    return frozenset(Point(p.x - min_x, p.y - min_y) for p in cells)


def cell_bounds(cells: frozenset[Point]) -> tuple[int, int]:
    return max(p.x for p in cells) + 1, max(p.y for p in cells) + 1


def render_mask(cells: frozenset[Point]) -> tuple[str, ...]:
    width, height = cell_bounds(cells)
    return tuple(
        "".join("#" if Point(x, y) in cells else "." for x in range(width))
        for y in range(height)
    )


def is_solid_rectangle(cells: frozenset[Point]) -> bool:
    width, height = cell_bounds(cells)
    return cells == frozenset(Point(x, y) for y in range(height) for x in range(width))


def _glyph_for(point: Point, directions: set[str], roles: set[str]) -> str:
    key = frozenset(directions)
    corners = {
        frozenset({"E", "S"}): ",",
        frozenset({"W", "S"}): ".",
        frozenset({"E", "N"}): "`",
        frozenset({"W", "N"}): "'",
    }
    if key in corners:
        return corners[key]
    if key == {"N", "S"}:
        return "|"
    if key == {"E", "W"}:
        if "north" in roles:
            phase = point.x % SECTION_STRIDE_X
            return "," if phase == 0 else (" " if phase == 2 else "—")
        return " " if point.x % 2 == 0 else "—"
    if len(key) >= 3:
        return "+"
    if key in ({"N"}, {"S"}):
        return "|"
    if key in ({"E"}, {"W"}):
        return "—"
    return " "


def render_bulk_outline(cells: frozenset[Point]) -> tuple[str, ...]:
    """Render coarse shared-edge 5x3 footprints for irregular structures."""
    width, height = cell_bounds(cells)
    strokes = StrokeGrid()
    for cell in cells:
        x0 = cell.x * SECTION_STRIDE_X
        x1 = x0 + SECTION_WIDTH - 1
        y0 = cell.y * SECTION_STRIDE_Y
        y1 = y0 + SECTION_HEIGHT - 1
        if Point(cell.x, cell.y - 1) not in cells:
            strokes.add_horizontal(x0, x1, y0, "north")
        if Point(cell.x, cell.y + 1) not in cells:
            strokes.add_horizontal(x0, x1, y1, "south")
        if Point(cell.x - 1, cell.y) not in cells:
            strokes.add_vertical(x0, y0, y1, "west")
        if Point(cell.x + 1, cell.y) not in cells:
            strokes.add_vertical(x1, y0, y1, "east")

    canvas_width = (width - 1) * SECTION_STRIDE_X + SECTION_WIDTH
    canvas_height = (height - 1) * SECTION_STRIDE_Y + SECTION_HEIGHT
    canvas = [[" " for _ in range(canvas_width)] for _ in range(canvas_height)]
    for point, directions in strokes.connections.items():
        canvas[point.y][point.x] = _glyph_for(point, directions, strokes.roles.get(point, set()))
    for cell in cells:
        x = cell.x * SECTION_STRIDE_X + SECTION_CENTER_X
        y = cell.y * SECTION_STRIDE_Y + SECTION_CENTER_Y
        if canvas[y][x] == " ":
            canvas[y][x] = "`"
    rows = tuple("".join(row).rstrip() for row in canvas)
    while rows and not rows[-1]:
        rows = rows[:-1]
    return rows


def _north_wall_top(floor_columns: int) -> str:
    return ",— —" * (floor_columns + 1) + ",."


def _north_wall_underside(floor_columns: int) -> str:
    span_count = floor_columns + 1
    return "|__" + "/___" * (span_count - 1) + "/ |"


def _south_wall(width: int) -> str:
    row = [" " for _ in range(width)]
    row[0], row[-1] = "`", "'"
    for x in range(1, width - 1, 2):
        row[x] = "—"
    return "".join(row)


def render_projected_room_shell(floor_columns: int, floor_rows: int) -> tuple[str, ...]:
    """Render the source-style north rim and recessed east wall.

    Dimensions count usable floor sections/possible character indicators. The
    shell adds one north span beyond those centers and a three-glyph east face.
    """
    if floor_columns < 1 or floor_rows < 1:
        raise ValueError("projected room needs at least one floor section")

    width = floor_columns * SECTION_STRIDE_X + 6
    east_inner_x = floor_columns * SECTION_STRIDE_X + 3
    east_face_x = east_inner_x + 1
    east_outer_x = east_inner_x + 2
    top = _north_wall_top(floor_columns)
    underside = _north_wall_underside(floor_columns)
    if len(top) != width or len(underside) != width:
        raise AssertionError("north wall grammar produced the wrong width")

    rows: list[str] = [top, underside]
    for section_y in range(floor_rows):
        boundary = [" " for _ in range(width)]
        boundary[0] = "|"
        boundary[east_inner_x] = "|"
        boundary[east_face_x] = "/"
        boundary[east_outer_x] = "|"
        rows.append("".join(boundary))

        center = [" " for _ in range(width)]
        center[0] = "|"
        for section_x in range(floor_columns):
            center[3 + section_x * SECTION_STRIDE_X] = "`"
        center[east_inner_x] = "|"
        center[east_outer_x] = "|"
        rows.append("".join(center))

    final_boundary = [" " for _ in range(width)]
    final_boundary[0] = "|"
    final_boundary[east_inner_x] = "|"
    final_boundary[east_face_x] = "/"
    final_boundary[east_outer_x] = "|"
    rows.append("".join(final_boundary))
    rows.append(_south_wall(width))
    return tuple(rows)


def load_catalog(path: Path) -> tuple[ShapeSample, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError(f"unsupported catalog schema_version: {data.get('schema_version')!r}")
    raw_samples = data.get("samples")
    if not isinstance(raw_samples, list):
        raise ValueError("catalog samples must be a list")
    samples = tuple(
        ShapeSample(
            sample_id=str(item["id"]),
            title=str(item["title"]),
            category=str(item["category"]),
            mask=tuple(str(row) for row in item["mask"]),
            tags=tuple(str(tag) for tag in item.get("tags", [])),
            notes=str(item.get("notes", "")),
            status=str(item.get("status", "generated")),
        )
        for item in raw_samples
    )
    ids = [sample.sample_id for sample in samples]
    if len(ids) != len(set(ids)):
        raise ValueError("catalog sample ids must be unique")
    return samples


def load_target(target_dir: Path, sample_id: str) -> tuple[str, ...] | None:
    path = target_dir / f"{sample_id}.txt"
    return tuple(path.read_text(encoding="utf-8").splitlines()) if path.exists() else None


def render_sample_draft(sample: ShapeSample, cells: frozenset[Point]) -> tuple[str, ...]:
    if sample.category == "room" and is_solid_rectangle(cells):
        width, height = cell_bounds(cells)
        return render_projected_room_shell(width, height)
    return render_bulk_outline(cells)


def build_renders(catalog_path: Path, target_dir: Path) -> tuple[SampleRender, ...]:
    results = []
    for sample in load_catalog(catalog_path):
        cells = cells_from_mask(sample.mask)
        results.append(
            SampleRender(
                sample=sample,
                mask_rows=render_mask(cells),
                draft_rows=render_sample_draft(sample, cells),
                target_rows=load_target(target_dir, sample.sample_id),
            )
        )
    return tuple(results)


def _side_by_side(columns: tuple[tuple[str, ...], ...], labels: tuple[str, ...], gap: str = "    ") -> list[str]:
    widths = [max([len(label), *(len(row) for row in rows)]) for label, rows in zip(labels, columns, strict=True)]
    output = [gap.join(label.ljust(width) for label, width in zip(labels, widths, strict=True)).rstrip()]
    output.append(gap.join(("-" * len(label)).ljust(width) for label, width in zip(labels, widths, strict=True)).rstrip())
    for y in range(max(map(len, columns), default=0)):
        output.append(gap.join((rows[y] if y < len(rows) else "").ljust(width) for rows, width in zip(columns, widths, strict=True)).rstrip())
    return output


def render_text_sheet(renders: tuple[SampleRender, ...]) -> str:
    lines = ["ASCII STRUCTURE STYLE REVIEW SHEET", "Generated drafts are disposable. Hand-edited targets are preserved separately.", ""]
    for render in renders:
        sample = render.sample
        lines.extend([
            f"[{sample.sample_id}] {sample.title}",
            f"category={sample.category} status={sample.status} tags={','.join(sample.tags) or '-'}",
        ])
        if sample.notes:
            lines.append(f"notes: {sample.notes}")
        lines.extend(_side_by_side(
            (render.mask_rows, render.draft_rows, render.target_rows or ("(not reviewed)",)),
            ("MASK", "AUTOMATIC DRAFT", "HAND-EDITED TARGET"),
        ))
        lines.extend(("", ""))
    return "\n".join(lines).rstrip() + "\n"


def render_html_sheet(renders: tuple[SampleRender, ...]) -> str:
    cards = []
    for render in renders:
        sample = render.sample
        columns = []
        for label, rows in (
            ("Geometry mask", render.mask_rows),
            ("Automatic draft", render.draft_rows),
            ("Hand-edited target", render.target_rows or ("(not reviewed)",)),
        ):
            columns.append(f"<section><h3>{escape(label)}</h3><pre>{escape(chr(10).join(rows))}</pre></section>")
        cards.append(
            "<article>"
            f"<h2>{escape(sample.title)} <code>{escape(sample.sample_id)}</code></h2>"
            f"<p><strong>{escape(sample.category)}</strong> · {escape(sample.status)} · {escape(', '.join(sample.tags) or 'no tags')}</p>"
            f"<p>{escape(sample.notes)}</p><div class=columns>{''.join(columns)}</div></article>"
        )
    head = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>ASCII structure style review</title>
<style>body{margin:0;background:#11100d;color:#e8dfc4;font:15px/1.45 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:28px}article{border:1px solid #514a38;background:#181610;padding:18px;margin:0 0 22px}h1,h2,h3{color:#f3d37a}.columns{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}section{min-width:0}pre{overflow:auto;min-height:100px;padding:14px;background:#0c0c0b;border:1px solid #383327;color:#f2ead1;font:16px/1.15 "Cascadia Mono",Consolas,monospace}code{color:#8fd3ef}@media(max-width:900px){.columns{grid-template-columns:1fr}}</style></head><body><main><h1>ASCII structure style review</h1><p>Generated drafts provide bulk geometry. Targets are deliberately separate and may be handcrafted.</p>"""
    return head + "".join(cards) + "</main></body></html>\n"


def review_manifest(renders: tuple[SampleRender, ...]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "workflow": ["generated", "reviewing", "approved", "promoted"],
        "samples": [
            {
                "id": render.sample.sample_id,
                "category": render.sample.category,
                "status": render.sample.status,
                "has_target": render.target_rows is not None,
                "target_path": f"targets/{render.sample.sample_id}.txt",
                "promotion_notes": "",
            }
            for render in renders
        ],
    }


def write_outputs(catalog_path: Path, target_dir: Path, output_dir: Path) -> tuple[Path, ...]:
    renders = build_renders(catalog_path, target_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    text_path = output_dir / "sample_sheet.txt"
    html_path = output_dir / "sample_sheet.html"
    manifest_path = output_dir / "review_manifest.json"
    text_path.write_text(render_text_sheet(renders), encoding="utf-8")
    html_path.write_text(render_html_sheet(renders), encoding="utf-8")
    manifest_path.write_text(json.dumps(review_manifest(renders), indent=2) + "\n", encoding="utf-8")
    return text_path, html_path, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path("style_samples/catalog.json"))
    parser.add_argument("--targets", type=Path, default=Path("style_samples/targets"))
    parser.add_argument("--output", type=Path, default=Path("style_samples/output"))
    args = parser.parse_args()
    for path in write_outputs(args.catalog, args.targets, args.output):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
