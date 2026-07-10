#!/usr/bin/env python3
"""Generate reviewable ASCII structures from logical floor-section masks.

Grammar v2 keeps logical floor topology, actor anchors, lattice intersections,
directional wall projection, and final character compositing separate.
Generated drafts remain disposable; handcrafted targets remain independent.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Iterable, Literal

SECTION_WIDTH = 5
SECTION_HEIGHT = 3
SECTION_STRIDE_X = 4
SECTION_STRIDE_Y = 2
ACTOR_ORIGIN_X = 2
ACTOR_ORIGIN_Y = 2
LATTICE_ORIGIN_X = 4
LATTICE_ORIGIN_Y = 3

# Compatibility aliases for older callers. In Grammar v2 these identify actor
# anchors, not backtick locations.
SECTION_CENTER_X = ACTOR_ORIGIN_X
SECTION_CENTER_Y = ACTOR_ORIGIN_Y
CELL_WIDTH = SECTION_STRIDE_X
CELL_HEIGHT = SECTION_STRIDE_Y
VALID_STATUS = {"generated", "reviewing", "approved", "promoted"}
DIRECTIONS = ("north", "east", "south", "west")
Direction = Literal["north", "east", "south", "west"]


@dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True, order=True)
class BoundaryEdge:
    section: Point
    direction: Direction


@dataclass(frozen=True)
class ProjectionModel:
    cells: frozenset[Point]
    actor_anchors: tuple[tuple[Point, Point], ...]
    lattice_markers: frozenset[Point]
    north_edges: frozenset[BoundaryEdge]
    east_edges: frozenset[BoundaryEdge]
    south_edges: frozenset[BoundaryEdge]
    west_edges: frozenset[BoundaryEdge]
    west_occluded_sections: frozenset[Point]
    south_occluded_sections: frozenset[Point]

    @property
    def foreground_occluded_sections(self) -> frozenset[Point]:
        return self.west_occluded_sections | self.south_occluded_sections


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
    """Sparse orthogonal stroke graph used for coarse non-room silhouettes."""

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


class LayeredCanvas:
    """Retain semantic layers until the final character is selected."""

    ORDER = ("floor", "lattice", "background_wall", "entity", "foreground_wall")

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.layers: dict[str, dict[Point, str]] = {name: {} for name in self.ORDER}

    def put(self, layer: str, point: Point, glyph: str) -> None:
        if layer not in self.layers:
            raise ValueError(f"unsupported layer: {layer}")
        if len(glyph) != 1:
            raise ValueError("glyph must be one character")
        if 0 <= point.x < self.width and 0 <= point.y < self.height:
            self.layers[layer][point] = glyph

    def compose(self, *, foreground: bool = True) -> tuple[str, ...]:
        canvas = [[" " for _ in range(self.width)] for _ in range(self.height)]
        for layer in self.ORDER:
            if layer == "foreground_wall" and not foreground:
                continue
            for point, glyph in self.layers[layer].items():
                canvas[point.y][point.x] = glyph
        rows = tuple("".join(row).rstrip() for row in canvas)
        while rows and not rows[-1]:
            rows = rows[:-1]
        return rows


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
    materialized = frozenset(cells)
    if not materialized:
        return materialized
    min_x = min(point.x for point in materialized)
    min_y = min(point.y for point in materialized)
    return frozenset(Point(point.x - min_x, point.y - min_y) for point in materialized)


def cell_bounds(cells: frozenset[Point]) -> tuple[int, int]:
    return max(point.x for point in cells) + 1, max(point.y for point in cells) + 1


def render_mask(cells: frozenset[Point]) -> tuple[str, ...]:
    width, height = cell_bounds(cells)
    return tuple(
        "".join("#" if Point(x, y) in cells else "." for x in range(width))
        for y in range(height)
    )


def is_solid_rectangle(cells: frozenset[Point]) -> bool:
    width, height = cell_bounds(cells)
    return cells == frozenset(Point(x, y) for y in range(height) for x in range(width))


def actor_anchor(section: Point) -> Point:
    """Project one logical floor section to its actor/object anchor."""
    return Point(
        ACTOR_ORIGIN_X + section.x * SECTION_STRIDE_X,
        ACTOR_ORIGIN_Y + section.y * SECTION_STRIDE_Y,
    )


def lattice_vertices(cells: frozenset[Point]) -> frozenset[Point]:
    """Return logical interior vertices surrounded by four floor sections."""
    width, height = cell_bounds(cells)
    vertices: set[Point] = set()
    for vertex_y in range(1, height):
        for vertex_x in range(1, width):
            surrounding = {
                Point(vertex_x - 1, vertex_y - 1),
                Point(vertex_x, vertex_y - 1),
                Point(vertex_x - 1, vertex_y),
                Point(vertex_x, vertex_y),
            }
            if surrounding.issubset(cells):
                vertices.add(Point(vertex_x, vertex_y))
    return frozenset(vertices)


def lattice_point(vertex: Point) -> Point:
    if vertex.x < 1 or vertex.y < 1:
        raise ValueError("lattice vertices must be interior logical coordinates")
    return Point(
        SECTION_STRIDE_X * vertex.x,
        1 + SECTION_STRIDE_Y * vertex.y,
    )


def lattice_points(cells: frozenset[Point]) -> frozenset[Point]:
    return frozenset(lattice_point(vertex) for vertex in lattice_vertices(cells))


def boundary_edges(cells: frozenset[Point]) -> frozenset[BoundaryEdge]:
    offsets: dict[Direction, Point] = {
        "north": Point(0, -1),
        "east": Point(1, 0),
        "south": Point(0, 1),
        "west": Point(-1, 0),
    }
    edges: set[BoundaryEdge] = set()
    for cell in cells:
        for direction, offset in offsets.items():
            neighbor = Point(cell.x + offset.x, cell.y + offset.y)
            if neighbor not in cells:
                edges.add(BoundaryEdge(cell, direction))
    return frozenset(edges)


def projection_model(cells: frozenset[Point]) -> ProjectionModel:
    edges = boundary_edges(cells)
    by_direction = {
        direction: frozenset(edge for edge in edges if edge.direction == direction)
        for direction in DIRECTIONS
    }
    west_sections = frozenset(edge.section for edge in by_direction["west"])
    south_sections = frozenset(edge.section for edge in by_direction["south"])
    return ProjectionModel(
        cells=cells,
        actor_anchors=tuple(sorted((cell, actor_anchor(cell)) for cell in cells)),
        lattice_markers=lattice_points(cells),
        north_edges=by_direction["north"],
        east_edges=by_direction["east"],
        south_edges=by_direction["south"],
        west_edges=by_direction["west"],
        west_occluded_sections=west_sections,
        south_occluded_sections=south_sections,
    )


def section_occluders(cells: frozenset[Point], section: Point) -> frozenset[str]:
    if section not in cells:
        raise ValueError(f"section is not occupied: {section}")
    model = projection_model(cells)
    result: set[str] = set()
    if section in model.west_occluded_sections:
        result.add("west")
    if section in model.south_occluded_sections:
        result.add("south")
    return frozenset(result)


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
    """Coarse fallback for routes/platforms using Grammar v2 lattice semantics."""
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
    for point in lattice_points(cells):
        coarse = Point(point.x - 2, point.y - 2)
        if 0 <= coarse.y < canvas_height and 0 <= coarse.x < canvas_width and canvas[coarse.y][coarse.x] == " ":
            canvas[coarse.y][coarse.x] = "`"
    rows = tuple("".join(row).rstrip() for row in canvas)
    while rows and not rows[-1]:
        rows = rows[:-1]
    return rows


def _render_rectangular_room(floor_columns: int, floor_rows: int, *, foreground: bool, show_lattice: bool) -> tuple[str, ...]:
    if floor_columns < 1 or floor_rows < 1:
        raise ValueError("projected room needs at least one floor section")

    width = floor_columns * SECTION_STRIDE_X + 3
    height = floor_rows * SECTION_STRIDE_Y + 2
    rows = [[" " for _ in range(width)] for _ in range(height)]
    east_inner_x = floor_columns * SECTION_STRIDE_X
    east_face_x = east_inner_x + 1
    east_outer_x = east_inner_x + 2

    for column in range(floor_columns):
        start = 2 + column * SECTION_STRIDE_X
        rows[0][start] = ","
        rows[0][start + 1] = "—"
        rows[0][start + 3] = "—"
    rows[0][2 + floor_columns * SECTION_STRIDE_X] = ","

    rows[1][1] = "/"
    if foreground:
        rows[1][2] = "|"
        underside_start = 3
    else:
        underside_start = 2
    for x in range(underside_start, east_inner_x):
        rows[1][x] = "_"
    for boundary in range(1, floor_columns):
        rows[1][1 + boundary * SECTION_STRIDE_X] = "/"
    rows[1][east_inner_x] = " "
    rows[1][east_face_x] = "/"
    rows[1][east_outer_x] = "|"

    for row_index in range(floor_rows):
        actor_y = ACTOR_ORIGIN_Y + row_index * SECTION_STRIDE_Y
        rows[actor_y][0] = "‘" if row_index == 0 else "|"
        if foreground:
            rows[actor_y][2] = "|"
        rows[actor_y][east_inner_x] = "|"
        rows[actor_y][east_outer_x] = "|"

        if row_index < floor_rows - 1:
            lattice_y = actor_y + 1
            rows[lattice_y][0] = "|"
            if foreground:
                rows[lattice_y][1] = "/"
                rows[lattice_y][2] = "|"
            if show_lattice:
                for vertex_x in range(1, floor_columns):
                    rows[lattice_y][SECTION_STRIDE_X * vertex_x] = "`"
            rows[lattice_y][east_inner_x] = "|"
            rows[lattice_y][east_face_x] = "/"
            rows[lattice_y][east_outer_x] = "|"

    south_y = floor_rows * SECTION_STRIDE_Y
    face_y = south_y + 1
    if foreground:
        rows[south_y][0] = "|"
        for column in range(floor_columns):
            start = 2 + column * SECTION_STRIDE_X
            rows[south_y][start] = ","
            rows[south_y][start + 1] = "—"
            rows[south_y][start + 2] = "‘" if column == floor_columns - 1 else " "
            rows[south_y][start + 3] = "—"
        rows[south_y][east_outer_x] = ","
        rows[face_y][0] = "‘"
        rows[face_y][1] = "/"
        for column in range(floor_columns):
            start = 2 + column * SECTION_STRIDE_X
            rows[face_y][start] = "_"
            rows[face_y][start + 1] = "_"
            rows[face_y][start + 2] = "_"
            rows[face_y][start + 3] = "/"
    else:
        rows[south_y][0] = "|"
        rows[south_y][east_inner_x] = "|"
        rows[south_y][east_outer_x] = ","
        rows[face_y][0] = "‘"
        for column in range(floor_columns):
            start = 2 + column * SECTION_STRIDE_X
            rows[face_y][start] = "_"
            rows[face_y][start + 1] = "_"
            rows[face_y][start + 2] = "_"
            rows[face_y][start + 3] = "/" if column == floor_columns - 1 else " "

    return tuple("".join(row).rstrip() for row in rows)


def render_projected_room_shell(
    floor_columns: int,
    floor_rows: int,
    *,
    foreground: bool = True,
    show_lattice: bool = True,
) -> tuple[str, ...]:
    """Render the approved rectangular Grammar v2 wall projection."""
    return _render_rectangular_room(
        floor_columns,
        floor_rows,
        foreground=foreground,
        show_lattice=show_lattice,
    )


def render_irregular_room(cells: frozenset[Point]) -> tuple[str, ...]:
    """Resolve directional Grammar v2 layers for an irregular room.

    This renderer is intentionally conservative. Its semantic edge extraction is
    authoritative; concave-corner glyph selection remains reviewable artwork.
    """
    width_cells, height_cells = cell_bounds(cells)
    canvas = LayeredCanvas(width_cells * SECTION_STRIDE_X + 3, height_cells * SECTION_STRIDE_Y + 2)
    model = projection_model(cells)

    for point in model.lattice_markers:
        canvas.put("lattice", point, "`")

    for edge in model.north_edges:
        x = 2 + edge.section.x * SECTION_STRIDE_X
        y = edge.section.y * SECTION_STRIDE_Y
        motif = ",— —,"
        for offset, glyph in enumerate(motif):
            if glyph != " ":
                canvas.put("background_wall", Point(x + offset, y), glyph)
        under = "|__/"
        for offset, glyph in enumerate(under):
            canvas.put("background_wall", Point(x + offset, y + 1), glyph)

    for edge in model.east_edges:
        x = (edge.section.x + 1) * SECTION_STRIDE_X
        y = ACTOR_ORIGIN_Y + edge.section.y * SECTION_STRIDE_Y
        canvas.put("background_wall", Point(x, y), "|")
        canvas.put("background_wall", Point(x + 2, y), "|")
        canvas.put("background_wall", Point(x, y + 1), "|")
        canvas.put("background_wall", Point(x + 1, y + 1), "/")
        canvas.put("background_wall", Point(x + 2, y + 1), "|")

    for edge in model.south_edges:
        x = 2 + edge.section.x * SECTION_STRIDE_X
        y = ACTOR_ORIGIN_Y + edge.section.y * SECTION_STRIDE_Y
        motif = ",— —,"
        for offset, glyph in enumerate(motif):
            if glyph != " ":
                canvas.put("foreground_wall", Point(x + offset, y), glyph)
        for offset, glyph in enumerate("___/"):
            canvas.put("foreground_wall", Point(x + offset, y + 1), glyph)

    for edge in model.west_edges:
        x = ACTOR_ORIGIN_X + edge.section.x * SECTION_STRIDE_X
        y = ACTOR_ORIGIN_Y + edge.section.y * SECTION_STRIDE_Y
        canvas.put("foreground_wall", Point(x - 2, y), "|")
        canvas.put("foreground_wall", Point(x, y), "|")
        canvas.put("foreground_wall", Point(x - 2, y + 1), "|")
        canvas.put("foreground_wall", Point(x - 1, y + 1), "/")
        canvas.put("foreground_wall", Point(x, y + 1), "|")

    return canvas.compose()


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
    if sample.category in {"room", "irregular-room"}:
        if is_solid_rectangle(cells):
            width, height = cell_bounds(cells)
            return render_projected_room_shell(width, height)
        return render_irregular_room(cells)
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
    height = max((len(rows) for rows in columns), default=0)
    for y in range(height):
        output.append(gap.join((rows[y] if y < len(rows) else "").ljust(width) for rows, width in zip(columns, widths, strict=True)).rstrip())
    return output


def render_text_sheet(renders: tuple[SampleRender, ...]) -> str:
    lines = [
        "ASCII STRUCTURE STYLE REVIEW SHEET — GRAMMAR V2",
        "Floor topology, actor anchors, lattice, directional walls, and composition are separate.",
        "",
    ]
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
<meta name=viewport content="width=device-width,initial-scale=1"><title>ASCII Grammar v2 review</title>
<style>body{margin:0;background:#11100d;color:#e8dfc4;font:15px/1.45 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:28px}article{border:1px solid #514a38;background:#181610;padding:18px;margin:0 0 22px}h1,h2,h3{color:#f3d37a}.columns{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}section{min-width:0}pre{overflow:auto;min-height:100px;padding:14px;background:#0c0c0b;border:1px solid #383327;color:#f2ead1;font:16px/1.15 "Cascadia Mono",Consolas,monospace}code{color:#8fd3ef}@media(max-width:900px){.columns{grid-template-columns:1fr}}</style></head><body><main><h1>ASCII structure Grammar v2 review</h1><p>The floorplan is authoritative. Wall art is a directional projection layered over it.</p>"""
    return head + "".join(cards) + "</main></body></html>\n"


def review_manifest(renders: tuple[SampleRender, ...]) -> dict[str, object]:
    return {
        "schema_version": 2,
        "grammar": "floor topology -> actor anchors -> lattice -> directional walls -> composition",
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
