#!/usr/bin/env python3
"""Generate reviewable coarse ASCII structure samples from logical cell masks.

This module intentionally handles bulk shape construction rather than final art.
Hand-edited targets remain separate from generated drafts so regeneration never
silently destroys approved style work.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
import argparse
import json
from pathlib import Path
from typing import Iterable

SECTION_WIDTH = 5
SECTION_HEIGHT = 3
SECTION_STRIDE_X = SECTION_WIDTH - 1
SECTION_STRIDE_Y = SECTION_HEIGHT - 1
SECTION_CENTER_X = SECTION_WIDTH // 2
SECTION_CENTER_Y = SECTION_HEIGHT // 2

# Compatibility names for older callers. These are section strides, not the
# inclusive dimensions of one section.
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
        if not self.sample_id or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for ch in self.sample_id):
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
    """Sparse stroke graph used before resolving lines to display glyphs."""

    def __init__(self) -> None:
        self.connections: dict[Point, set[str]] = {}
        self.roles: dict[Point, set[str]] = {}

    def _point(self, point: Point) -> set[str]:
        return self.connections.setdefault(point, set())

    def add_horizontal(self, x0: int, x1: int, y: int, role: str) -> None:
        for x in range(x0, x1):
            left = Point(x, y)
            right = Point(x + 1, y)
            self._point(left).add("E")
            self._point(right).add("W")
            self.roles.setdefault(left, set()).add(role)
            self.roles.setdefault(right, set()).add(role)

    def add_vertical(self, x: int, y0: int, y1: int, role: str) -> None:
        for y in range(y0, y1):
            top = Point(x, y)
            bottom = Point(x, y + 1)
            self._point(top).add("S")
            self._point(bottom).add("N")
            self.roles.setdefault(top, set()).add(role)
            self.roles.setdefault(bottom, set()).add(role)


def cells_from_mask(mask: Iterable[str]) -> frozenset[Point]:
    rows = tuple(mask)
    if not rows:
        raise ValueError("mask must have at least one row")
    width = max((len(row) for row in rows), default=0)
    cells = {
        Point(x, y)
        for y, row in enumerate(rows)
        for x, ch in enumerate(row.ljust(width, "."))
        if ch == "#"
    }
    unexpected = {
        ch
        for row in rows
        for ch in row
        if ch not in {"#", ".", " "}
    }
    if unexpected:
        raise ValueError(f"mask has unsupported characters: {sorted(unexpected)!r}")
    if not cells:
        raise ValueError("mask must contain at least one # cell")
    return normalize_cells(cells)


def normalize_cells(cells: Iterable[Point]) -> frozenset[Point]:
    materialized = frozenset(cells)
    if not materialized:
        return materialized
    min_x = min(point.x for point in materialized)
    min_y = min(point.y for point in materialized)
    return frozenset(Point(point.x - min_x, point.y - min_y) for point in materialized)


def cell_bounds(cells: frozenset[Point]) -> tuple[int, int]:
    return (
        max(point.x for point in cells) + 1,
        max(point.y for point in cells) + 1,
    )


def render_mask(cells: frozenset[Point]) -> tuple[str, ...]:
    width, height = cell_bounds(cells)
    return tuple(
        "".join("#" if Point(x, y) in cells else "." for x in range(width))
        for y in range(height)
    )


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
            phase = point.x % CELL_WIDTH
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
    width, height = cell_bounds(cells)
    strokes = StrokeGrid()

    for cell in cells:
        # One logical floor section occupies a 5x3 glyph footprint. Adjacent
        # sections share their outside edge, so origins advance by 4x2.
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

    # Backticks are section-center indicators, not decoration and not grid
    # vertices. Each occupied logical section is an inclusive 5x3 footprint.
    # Neighboring sections overlap along their outside edge, giving a 4x2
    # origin stride. The indicator stays at local coordinate (2, 1).
    for cell in cells:
        gx = cell.x * SECTION_STRIDE_X + SECTION_CENTER_X
        gy = cell.y * SECTION_STRIDE_Y + SECTION_CENTER_Y
        if canvas[gy][gx] == " ":
            canvas[gy][gx] = "`"

    rows = tuple("".join(row).rstrip() for row in canvas)
    while rows and not rows[-1]:
        rows = rows[:-1]
    return rows


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
    if not path.exists():
        return None
    return tuple(path.read_text(encoding="utf-8").splitlines())


def build_renders(catalog_path: Path, target_dir: Path) -> tuple[SampleRender, ...]:
    results: list[SampleRender] = []
    for sample in load_catalog(catalog_path):
        cells = cells_from_mask(sample.mask)
        results.append(
            SampleRender(
                sample=sample,
                mask_rows=render_mask(cells),
                draft_rows=render_bulk_outline(cells),
                target_rows=load_target(target_dir, sample.sample_id),
            )
        )
    return tuple(results)


def _side_by_side(columns: tuple[tuple[str, ...], ...], labels: tuple[str, ...], gap: str = "    ") -> list[str]:
    widths = [
        max([len(label), *(len(row) for row in rows)], default=len(label))
        for label, rows in zip(labels, columns, strict=True)
    ]
    output = [gap.join(label.ljust(width) for label, width in zip(labels, widths, strict=True)).rstrip()]
    output.append(
        gap.join(
            ("-" * len(label)).ljust(width)
            for label, width in zip(labels, widths, strict=True)
        ).rstrip()
    )
    height = max((len(rows) for rows in columns), default=0)
    for y in range(height):
        parts = []
        for rows, width in zip(columns, widths, strict=True):
            parts.append((rows[y] if y < len(rows) else "").ljust(width))
        output.append(gap.join(parts).rstrip())
    return output


def render_text_sheet(renders: tuple[SampleRender, ...]) -> str:
    lines = [
        "ASCII STRUCTURE STYLE REVIEW SHEET",
        "Generated drafts are disposable. Hand-edited targets are preserved separately.",
        "",
    ]
    for render in renders:
        sample = render.sample
        lines.extend(
            [
                f"[{sample.sample_id}] {sample.title}",
                f"category={sample.category} status={sample.status} tags={','.join(sample.tags) or '-'}",
            ]
        )
        if sample.notes:
            lines.append(f"notes: {sample.notes}")
        target = render.target_rows or ("(not reviewed)",)
        lines.extend(
            _side_by_side(
                (render.mask_rows, render.draft_rows, target),
                ("MASK", "AUTOMATIC DRAFT", "HAND-EDITED TARGET"),
            )
        )
        lines.extend(("", ""))
    return "\n".join(lines).rstrip() + "\n"


def render_html_sheet(renders: tuple[SampleRender, ...]) -> str:
    cards = []
    for render in renders:
        sample = render.sample
        target = render.target_rows or ("(not reviewed)",)
        columns = []
        for label, rows in (
            ("Geometry mask", render.mask_rows),
            ("Automatic draft", render.draft_rows),
            ("Hand-edited target", target),
        ):
            columns.append(f"<section><h3>{escape(label)}</h3><pre>{escape(chr(10).join(rows))}</pre></section>")
        cards.append(
            "<article>"
            f"<h2>{escape(sample.title)} <code>{escape(sample.sample_id)}</code></h2>"
            f"<p><strong>{escape(sample.category)}</strong> · "
            f"{escape(sample.status)} · "
            f"{escape(', '.join(sample.tags) or 'no tags')}</p>"
            f"<p>{escape(sample.notes)}</p>"
            f"<div class=columns>{''.join(columns)}</div>"
            "</article>"
        )
    head = """<!doctype html>
<html lang=en>
<head>
<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>ASCII structure style review</title>
<style>
body { margin: 0; background: #11100d; color: #e8dfc4; font: 15px/1.45 system-ui, sans-serif; }
main { max-width: 1500px; margin: auto; padding: 28px; }
article { border: 1px solid #514a38; background: #181610; padding: 18px; margin: 0 0 22px; }
h1, h2, h3 { color: #f3d37a; }
h2 { margin-bottom: 4px; }
.columns { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
section { min-width: 0; }
pre {
  overflow: auto;
  min-height: 100px;
  padding: 14px;
  background: #0c0c0b;
  border: 1px solid #383327;
  color: #f2ead1;
  font: 16px/1.15 "Cascadia Mono", Consolas, monospace;
}
code { color: #8fd3ef; }
@media(max-width: 900px) { .columns { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<main>
<h1>ASCII structure style review</h1>
<p>Generated drafts provide bulk geometry. Targets are deliberately separate and may be handcrafted.</p>
"""
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
