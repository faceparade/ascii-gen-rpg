#!/usr/bin/env python3
"""Three-room test scene with room 2's north wall generated parametrically.

This is a non-destructive integration artifact for the modular wall work. It
keeps `three_room_macro_test.py` and the current editor baseline untouched while
showing how chunk-based north-wall openings change the room/corridor structure.
"""
from __future__ import annotations

from pathlib import Path

from curved_dungeon_grammar import OUT_DIR, Rect, annotate, html_review
from modular_ascii_parts import Opening, NorthWall
from room_shell import close_north_wall_for_middle
from three_room_macro_test import build_three_room_macro_test

ROOM2_X = 57
ROOM2_NORTH_Y = 0

OPENING_PRESETS: dict[str, Opening | None] = {
    "baseline_no_opening": None,
    "r24_narrow_2_chunks_4_5": Opening(4, 2),
    "r24_uneven_3_chunks_3_5": Opening(3, 3),
    "r24_center_4_chunks_3_6": Opening(3, 4),
    "r24_wide_6_chunks_2_7": Opening(2, 6),
}


def replace_room2_north_wall(base: list[str], opening: Opening | None) -> list[str]:
    """Return `base` with room 2's north wall rows replaced by NorthWall output.

    ``NorthWall`` renders the bare/open north-wall part: its top row is 4W+1
    wide and its underside begins with ``,``.  Room 2 is the closed middle shell,
    so apply the same close-box transform used by ``RoomShell`` before pasting:
    top ``.`` -> ``,.`` and underside leading ``,`` -> ``|``.  This keeps the
    no-opening baseline byte-equal to ``build_three_room_macro_test()`` while
    still letting opening cases come from the parametric NorthWall carve.
    """
    wall_rows = close_north_wall_for_middle(
        NorthWall(8, () if opening is None else (opening,)).render()
    )
    width = max(max(len(row) for row in base), ROOM2_X + max(len(row) for row in wall_rows))
    canvas = [list(row.ljust(width)) for row in base]
    for dy, wall_row in enumerate(wall_rows):
        y = ROOM2_NORTH_Y + dy
        for dx, ch in enumerate(wall_row):
            canvas[y][ROOM2_X + dx] = ch
    return ["".join(row).rstrip() for row in canvas]


def build_case(name: str) -> list[str]:
    if name not in OPENING_PRESETS:
        raise KeyError(f"unknown opening preset: {name}")
    return replace_room2_north_wall(build_three_room_macro_test(), OPENING_PRESETS[name])


def case_regions(case_name: str) -> list[Rect]:
    opening = OPENING_PRESETS[case_name]
    regions = [
        Rect("ROOM_1_LEFT_SHELL", 0, 0, 35, 12),
        Rect("CORRIDOR_1_TO_2", 32, 4, 28, 7),
        Rect("ROOM_2_PARAMETRIC_NORTH_WALL", ROOM2_X, ROOM2_NORTH_Y, 34, 2),
        Rect("ROOM_2_SHELL_REMAINDER", ROOM2_X, 2, 35, 10),
        Rect("ROOM_2_WIDE_PLATFORM", ROOM2_X + 7, 5, 20, 5),
        Rect("CORRIDOR_2_TO_3", 89, 4, 28, 7),
        Rect("ROOM_3_EMPTY_TERMINAL", 114, 0, 35, 12),
    ]
    if opening is not None:
        start_x = ROOM2_X + (opening.start_chunk - 1) * 4
        regions.append(Rect(f"OPENING_{opening.start_chunk}_{opening.end_chunk}", start_x, 0, opening.width_chunks * 4 + 1, 2))
    return regions


def write_case_artifacts(name: str, lines: list[str]) -> None:
    stem = OUT_DIR / f"three_room_north_wall_parametric_{name}"
    regions = case_regions(name)
    stem.with_suffix(".txt").write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    Path(str(stem) + "_annotated.txt").write_text(annotate(lines, regions), encoding="utf-8")
    stem.with_suffix(".html").write_text(html_review(lines, regions), encoding="utf-8")


def build_index_html(case_names: list[str]) -> str:
    links = []
    previews = []
    for name in case_names:
        lines = build_case(name)
        links.append(f'<li><a href="three_room_north_wall_parametric_{name}.html">{name}</a></li>')
        crop = "\n".join(row[:100] for row in lines[:6])
        previews.append(f"<h2>{name}</h2><pre>{escape_html(crop)}</pre>")
    return f"""<!doctype html>
<meta charset="utf-8">
<title>Parametric North Wall Opening Candidates</title>
<style>
body {{ background:#10100f; color:#ddd0a8; font-family:system-ui,sans-serif; margin:22px; }}
a, code {{ color:#ffd36d; }}
pre {{ background:#181713; border:1px solid #5b5130; color:#f0d58a; padding:12px; overflow:auto; font-family:'Cascadia Mono','Consolas','Courier New',monospace; line-height:1.1; }}
</style>
<h1>Parametric North Wall Opening Candidates</h1>
<p>Room 2's north wall rows are generated from <code>NorthWall(8, Opening(...))</code>. Other room/corridor content comes from the existing three-room macro test.</p>
<ul>{''.join(links)}</ul>
{''.join(previews)}
"""


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    base = build_three_room_macro_test()
    baseline_case = build_case("baseline_no_opening")
    if baseline_case != base:
        raise SystemExit("baseline_no_opening should exactly match build_three_room_macro_test()")

    names = list(OPENING_PRESETS)
    for name in names:
        lines = build_case(name)
        write_case_artifacts(name, lines)

    index = OUT_DIR / "three_room_north_wall_parametric_index.html"
    index.write_text(build_index_html(names), encoding="utf-8")
    print(index)
    for name in names:
        print(OUT_DIR / f"three_room_north_wall_parametric_{name}.txt")


if __name__ == "__main__":
    main()
