#!/usr/bin/env python3
"""Regular vertical/offshoot pathway test from Rooms.md R24.

This keeps the locked two-room baseline untouched. It renders the selected R24
pathway macro standalone and generates a small set of north-side placement
candidates above the current three-room macro test.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

from curved_dungeon_grammar import (
    OUT_DIR,
    Rect,
    _paste,
    annotate,
    html_review,
    regular_vertical_pathway,
)
from three_room_macro_test import build_three_room_macro_test

PATHWAY_W = 27
ROOM2_X = 57


def write_text(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")


def r24_source_fixed() -> list[str]:
    source = (OUT_DIR / "Rooms.md").read_text(encoding="utf-8").splitlines()[216:222]
    return [row.ljust(PATHWAY_W) for row in source]


def render_standalone() -> list[str]:
    return regular_vertical_pathway(6)


def pathway_tail_bounds(stamp: list[str]) -> tuple[int, int]:
    """Return left/right side-wall columns of the R24 downward tail row."""
    tail = stamp[-1]
    left = tail.index("|")
    right = tail.rindex("|")
    return left, right


def carve_north_wall_opening(canvas: list[list[str]], room_y: int, opening_left: int, opening_right: int) -> None:
    """Blank north-wall glyphs between corridor wall corners before stamping.

    The side-wall/corner columns themselves are preserved for the pathway stamp;
    only the roof/wall span between them is opened.
    """
    for yy in (room_y, room_y + 1):
        if yy < 0 or yy >= len(canvas):
            continue
        for xx in range(opening_left + 1, opening_right):
            if 0 <= xx < len(canvas[yy]):
                canvas[yy][xx] = " "


def paste_above_base(base: list[str], stamp: list[str], x: int, y: int, room_y: int) -> list[str]:
    """Render base rooms shifted down, carve north wall, then paste stamp."""
    height = max(room_y + len(base), y + len(stamp))
    width = max(max(len(row) for row in base), x + max(len(row) for row in stamp))
    canvas = [list(" " * width) for _ in range(height)]
    for by, row in enumerate(base):
        _paste(canvas, [row], 0, room_y + by)

    tail_left, tail_right = pathway_tail_bounds(stamp)
    carve_north_wall_opening(canvas, room_y, x + tail_left, x + tail_right)
    _paste(canvas, stamp, x, y)
    return ["".join(row).rstrip() for row in canvas]


def render_candidate_cards() -> str:
    base = build_three_room_macro_test()
    stamp = regular_vertical_pathway(6)
    # North-side candidates with intentional overlap into the room's north wall.
    # The room starts at room_y=6. Since R24 is 6 rows high, pathway_y=1 makes
    # the tail row hit the top roof row; pathway_y=2 pushes it one row deeper
    # into the north wall/underside. The carve step opens the roof between the
    # tail's side-wall corners before the pathway stamp is pasted.
    candidates = [
        (ROOM2_X + 4, 1, 6, "tail overlaps roof row; left-grid candidate"),
        (ROOM2_X + 8, 1, 6, "tail overlaps roof row; shifted right one grid step"),
        (ROOM2_X + 12, 1, 6, "tail overlaps roof row; shifted right two grid steps"),
        (ROOM2_X + 4, 2, 6, "tail one row deeper into north wall; left-grid candidate"),
        (ROOM2_X + 8, 2, 6, "tail one row deeper into north wall; shifted right one grid step"),
        (ROOM2_X + 12, 2, 6, "tail one row deeper into north wall; shifted right two grid steps"),
    ]

    cards = []
    for idx, (x, y, room_y, label) in enumerate(candidates, start=1):
        lines = paste_above_base(base, stamp, x, y, room_y)
        width = max(len(line) for line in lines)
        rows = []
        for yy, line in enumerate(lines):
            cells = []
            for ch in line.ljust(width):
                cells.append("<span class='ch'>&nbsp;</span>" if ch == " " else f"<span class='ch ink'>{escape(ch)}</span>")
            rows.append(f"<div><span class='ln'>L{yy:02d}</span>{''.join(cells)}</div>")
        cards.append(f"""
<section class="card" id="C{idx}">
  <h2>C{idx}: x={x}, pathway_y={y}, room_y={room_y}</h2>
  <p>{escape(label)} · pathway region L{y:02d}-L{y+len(stamp)-1:02d}, C{x:03d}-C{x+PATHWAY_W-1:03d}</p>
  <div class="map">{''.join(rows)}</div>
</section>
""")

    return f"""<!doctype html>
<meta charset="utf-8">
<title>R24 Regular Vertical Pathway North-Side Placement QA</title>
<style>
body {{ background:#10100f; color:#ddd0a8; font-family:system-ui,sans-serif; margin:24px; }}
h1,h2 {{ color:#f0d58a; }}
code {{ color:#ffd36d; }}
nav {{ position:sticky; top:0; background:#181713; border:1px solid #5b5130; padding:10px; margin-bottom:18px; }}
a {{ color:#ffd36d; margin-right:12px; }}
.card {{ border:1px solid #5b5130; background:#161511; padding:16px; margin:18px 0; }}
.map {{ font-family:'Cascadia Mono','Consolas','Courier New',monospace; font-size:16px; line-height:1.1; white-space:pre; overflow:auto; }}
.ln {{ color:#777; display:inline-block; width:4ch; user-select:none; margin-right:1ch; }}
.ch {{ display:inline-block; width:1ch; color:#4e4939; }}
.ch.ink {{ color:#f0d58a; }}
</style>
<h1>R24 Regular Vertical Pathway North-Side Placement QA</h1>
<p>Macro source: <code>Rooms.md:217-222</code>. These are north-side placement candidates with the room's north wall carved open between the pathway tail side-wall corners. The locked two-room baseline is not changed.</p>
<nav>{''.join(f'<a href="#C{i}">C{i}</a>' for i in range(1, len(candidates)+1))}</nav>
{''.join(cards)}
"""


def main() -> None:
    standalone = render_standalone()
    source = r24_source_fixed()
    if standalone != source:
        raise SystemExit("R24 macro does not match Rooms.md source after fixed-width normalization")

    regions = [Rect("R24_REGULAR_VERTICAL_PATHWAY", 0, 0, PATHWAY_W, len(standalone))]
    write_text(OUT_DIR / "regular_vertical_pathway_macro.txt", standalone)
    (OUT_DIR / "regular_vertical_pathway_macro_annotated.txt").write_text(annotate(standalone, regions), encoding="utf-8")
    (OUT_DIR / "regular_vertical_pathway_macro.html").write_text(html_review(standalone, regions), encoding="utf-8")
    north_qa = render_candidate_cards()
    (OUT_DIR / "regular_vertical_pathway_placement_qa.html").write_text(north_qa, encoding="utf-8")
    (OUT_DIR / "regular_vertical_pathway_north_placement_qa.html").write_text(north_qa, encoding="utf-8")

    print(OUT_DIR / "regular_vertical_pathway_macro.txt")
    print(OUT_DIR / "regular_vertical_pathway_macro_annotated.txt")
    print(OUT_DIR / "regular_vertical_pathway_macro.html")
    print(OUT_DIR / "regular_vertical_pathway_placement_qa.html")
    print(OUT_DIR / "regular_vertical_pathway_north_placement_qa.html")
    print("R24 macro fixed-width exact match True")


if __name__ == "__main__":
    main()
