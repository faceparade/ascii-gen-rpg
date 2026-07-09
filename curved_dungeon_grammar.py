#!/usr/bin/env python3
"""Curved Dungeon Grammar — locked macro extraction baseline.

This script renders the approved two-room reference from named macros:
room shell stamps, the same-level horizontal corridor, and the wide platform.
It still validates byte-for-byte against the locked hand-edited reference.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
LOCKED_REFERENCE = OUT_DIR / "locked_two_room_connection_reference.txt"


@dataclass(frozen=True)
class Rect:
    name: str
    x: int
    y: int
    w: int
    h: int


# ─────────────────────────────────────────────────────────────────────────────
# Regions (from earlier measurements)
# ─────────────────────────────────────────────────────────────────────────────
# Tristan's floor grammar uses shared grid intersections:
# - Each logical box is 5 characters wide by 3 rows tall if you count both
#   boundary grid-lines.
# - Adjacent boxes share their boundary line, so the next crossing point is
#   4 columns / 2 rows away.
# - Backticks mark grid crossings, not the center of a one-character tile.
GRID_BOX_W = 5
GRID_BOX_H = 3
GRID_STEP_X = GRID_BOX_W - 1
GRID_STEP_Y = GRID_BOX_H - 1

# Verified: the wide platform's macro origin is the left grid-line support
# column. The visible top dot is one column to the right of this origin.
WIDE_PLATFORM_ROOM_OFFSET_X = 7
WIDE_PLATFORM_ROOM_OFFSET_Y = 5

REGIONS = [
    Rect("ROOM_1_SHELL_AREA", 0, 0, 35, 12),
    Rect("ROOM_2_SHELL_AREA", 57, 0, 35, 12),
    Rect("HORIZONTAL_CORRIDOR_OVERLAP", 32, 4, 28, 7),
    Rect("ROOM_2_WIDE_PLATFORM", 64, 5, 20, 5),
]


# ─────────────────────────────────────────────────────────────────────────────
# Macro vocabulary (so far)
# ─────────────────────────────────────────────────────────────────────────────

def horizontal_corridor(width_units: int = 6) -> list[str]:
    """Return the locked same-level room-to-room corridor macro.

    The room's visible east wall at C031 is outside this macro; this stamp starts
    on the next grid-line at C032 with `/t...`. Trailing spaces are structural.
    """
    if width_units != 6:
        raise NotImplementedError("horizontal_corridor currently supports only the locked 6-unit width")
    return [
        "/t— -‘— -‘— -‘— -‘— -‘— -‘".ljust(28),
        "/___/___/___/___/___/___/".ljust(28),
        "".ljust(28),
        " ’— -’— -’— -’— -’— -’— -’".ljust(28),
        "/|                       ,".ljust(28),
        " |                       ,".ljust(28),
        "/|                       ,".ljust(28),
    ]


def regular_vertical_pathway(width_units: int = 6) -> list[str]:
    """Compatibility wrapper for the locked R24 vertical/offshoot pathway preset."""
    if width_units != 6:
        raise NotImplementedError("regular_vertical_pathway currently supports only the locked R24 width")
    from presets import build_vertical_pathway

    return list(build_vertical_pathway("regular_r24_6"))


def raised_platform(width_units: int = 4) -> list[str]:
    """Compatibility wrapper for the full raised floor section source stamp."""
    if width_units != 4:
        raise NotImplementedError("raised_platform currently supports only the locked 4-unit raised floor section")
    rows = [
        "` ,— — — — — — — — — —.",
        " /|                   |",
        ", |                   |",
        "|/|                   |",
        "| |                   |",
        "|/‘— —,— —,— —,— —,— -,",
        "‘/___/___/;.;/___/___/",
    ]
    width = max(len(row) for row in rows)
    return [row.ljust(width) for row in rows]


def raised_floor_section_tall_narrow() -> list[str]:
    """Return the locked small tall/narrow raised floor section source stamp."""
    rows = [
        "` ,— —.",
        " /|   |",
        ", |   |",
        "|/|   |",
        "| |   |",
        "|/‘— —,",
        "‘/___/ ",
    ]
    width = max(len(row) for row in rows)
    return [row.ljust(width) for row in rows]


def south_opening_template(name: str = "compact_r24") -> list[tuple[int, str]]:
    """Compatibility wrapper for locked south-opening preset rows."""
    from presets import build_south_opening_template

    try:
        return list(build_south_opening_template(name))
    except KeyError as exc:
        raise NotImplementedError("only the compact_r24 south-opening template is locked so far") from exc


def wide_platform(width_units: int = 4) -> list[str]:
    """Return the locked wide-platform block for the current reference width."""
    if width_units != 4:
        raise NotImplementedError("wide_platform currently supports only the locked 4-unit width")
    # Origin is the left grid-line support column, one cell-column before
    # the visible top cap dot. The first row intentionally begins with SPACE.
    return [
        " ._ _ _ _ _ _ _ _ _.",
        "/| . ` . ` . ` . ` |",
        ",| . ` . ` . ` . ` |",
        ",t —,— —,— —,— —,— j",
        "t__/___/;;;/___/__/",
    ]





def room_shell_left_8() -> list[str]:
    """Locked left/entry room shell stamp, 8 shared-grid crossings wide."""
    return [
        ',— -,— -,— -,— -,— -,— -,— -,— -.  ',
        ',__/___/___/___/___/___/___/___/ | ',
        ',                              |/| ',
        ',  `   `   `   `   `   `   `   | | ',
        ',                              |/t—',
        ',  `   `   `   `   `   `   `   t/__',
        ',                                  ',
        ',  `   `   `   `   `   `   `     ’—',
        ',                               /| ',
        ',  `   `   `   `   `   `   `   , | ',
        ',                              |/| ',
        '’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’ ',
    ]


def room_shell_middle_8() -> list[str]:
    """Locked v3 middle room shell stamp: rectangular box with '|' room walls
    (easiest for a generative system — each row is '|' + interior + '|').
    Interior is the 6-line structure with the backtick-alignment rule (every
    other row: 1,3,5) applied as POSITION only; the shipped skin uses '.' for
    the interior grid (backticks are a reference overlay, never drawn).
    """
    return [
        ',— -,— -,— -,— -,— -,— -,— -,— -,.',
        '|__/___/___/___/___/___/___/___/ |',
        '|                              | |',
        '|  `   `   `   `   `   `   `   |/|',
        '|                              | |',
        '|  `   `   `   `   `   `   `   |/|',
        '|                              | |',
        '|  `   `   `   `   `   `   `   |/|',
        '|                              | |',
        '|  `   `   `   `   `   `   `   |/|',
        '`— — — — — — — — — — — — — — — — \'',
    ]


def room_shell_middle_8_west_east() -> list[str]:
    """Locked v3 middle room shell stamp WITH both west + east doorways carved,
    hand-drawn (user art, grid-aligned lower corners).

    This shell is 36 wide (vs the 34-wide room_shell_middle_8 base) because the
    user's drawn structure interior is 2 columns wider. Boundaries stay at col 0
    and col 35. The door caps sit INSIDE the walls (west cap at col 1, east cap at
    col 34) — never on the border columns — and the lower corners (west 'j' at
    row 8, east '/' at row 9) land on the structure's grid column (col 25).
    """
    return [
        '|,— -,— -,— -,— -,— -,— -,— -,— -,.|',
        '||__/___/___/___/___/___/___/___/ ||',
        '||                              | ||',
        '||  `   `   `   `   `   `   `   |/||',
        '|j   ._ _ _ _ _ _ _ _ _ _.      | t|',
        '|   /| . . . . . . . . . |  `   t/_|',
        '|   ,| .   .   .   .   . |         |',
        '|   ,| . . . . . . . . . |  `   `  |',
        '|.  ,t— —,— —,— —,— —,— -j        .|',
        '||  t___/___/;.;/___/___/   `   `/||',
        '|`— — — — — — — — — — — — — — — — \'|',
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _paste(dest: list[list[str]], src: list[str], x: int, y: int) -> None:
    """Paste src into dest at (x, y). dest is list of mutable char lists."""
    for dy, row in enumerate(src):
        ty = y + dy
        if ty < 0 or ty >= len(dest):
            continue
        drow = dest[ty]
        if len(drow) < len(src[0]):
            drow.extend([' '] * (len(src[0]) - len(drow)))
        for dx, ch in enumerate(row):
            if x + dx < len(drow):
                drow[x + dx] = ch


def build_two_room_generated() -> list[str]:
    # Load reference
    ref_lines = LOCKED_REFERENCE.read_text(encoding="utf-8").rstrip("\n").splitlines()
    height = len(ref_lines)
    width = max(len(line) for line in ref_lines)

    # Blank canvas
    canvas: list[list[str]] = [[' '] * width for _ in range(height)]

    # Place locked room shell macros. These are still non-parametric on purpose:
    # locked macro first, then parameterize after exact-match verification.
    _paste(canvas, room_shell_left_8(), REGIONS[0].x, REGIONS[0].y)
    _paste(canvas, room_shell_middle_8(), REGIONS[1].x, REGIONS[1].y)

    # Place locked horizontal corridor macro (overwrites room-mouth geometry).
    corr_rect = REGIONS[2]   # HORIZONTAL_CORRIDOR_OVERLAP
    _paste(canvas, horizontal_corridor(6), corr_rect.x, corr_rect.y)

    # Place wide platform macro
    plat = wide_platform(4)
    plat_x = REGIONS[1].x + WIDE_PLATFORM_ROOM_OFFSET_X
    plat_y = REGIONS[1].y + WIDE_PLATFORM_ROOM_OFFSET_Y
    _paste(canvas, plat, plat_x, plat_y)

    # Convert to strings
    result = [''.join(row).rstrip() for row in canvas]
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Review/export helpers
# ─────────────────────────────────────────────────────────────────────────────

def write_text(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")


def annotate(lines: list[str], regions: list[Rect]) -> str:
    width = max(map(len, lines))
    tens = "     " + "".join(str((i // 10) % 10) if i % 10 == 0 else " " for i in range(width))
    ones = "     " + "".join(str(i % 10) for i in range(width))
    out = [tens, ones]
    for y, line in enumerate(lines):
        out.append(f"L{y:02d} |{line.ljust(width)}|")
    out.append("\nREGIONS")
    for r in regions:
        out.append(f"- {r.name}: L{r.y:02d}-L{r.y+r.h-1:02d}, C{r.x:03d}-C{r.x+r.w-1:03d}")
    return "\n".join(out) + "\n"


def html_review(lines: list[str], regions: list[Rect]) -> str:
    width = max(map(len, lines))
    body = []
    for y, line in enumerate(lines):
        cells = []
        for x, ch in enumerate(line.ljust(width)):
            content = "&nbsp;" if ch == " " else escape(ch)
            ink = " ink" if ch != " " else ""
            cells.append(f'<span class="ch{ink}" data-x="{x}" data-y="{y}" data-ch="{escape(ch)}">{content}</span>')
        body.append(f'<div class="line"><span class="lineno">L{y:02d}</span>{"".join(cells)}</div>')
    region_html = "\n".join(
        f"<li><code>{escape(r.name)}</code>: L{r.y:02d}-L{r.y+r.h-1:02d}, C{r.x:03d}-C{r.x+r.w-1:03d}</li>"
        for r in regions
    )
    return f"""<!doctype html>
<meta charset="utf-8">
<title>Two Room Generated Review</title>
<style>
body {{ background:#10100f; color:#ddd0a8; font-family:system-ui,sans-serif; margin:20px; }}
.map {{ font-family:'Cascadia Mono','Consolas','Courier New',monospace; font-size:16px; line-height:1.1; white-space:pre; }}
.line {{ height:1.1em; }}
.lineno {{ color:#777; display:inline-block; width:4ch; user-select:none; }}
.ch {{ display:inline-block; width:1ch; height:1.1em; cursor:crosshair; color:#5f5844; }}
.ch.ink {{ color:#f0d58a; }}
.ch:hover {{ background:#3a3520; outline:1px solid #e0b84d; }}
#readout {{ position:sticky; top:0; background:#1b1a16; padding:8px; border:1px solid #5b5130; margin-bottom:12px; }}
code {{ color:#ffd36d; }}
</style>
<div id="readout">Click a cell to copy coordinate.</div>
<div class="map">{''.join(body)}</div>
<h2>Regions</h2><ul>{region_html}</ul>
<script>
document.querySelectorAll('.ch').forEach(ch => ch.addEventListener('click', () => {{
  const y = ch.dataset.y.padStart(2,'0');
  const x = ch.dataset.x.padStart(3,'0');
  const raw = ch.dataset.ch;
  const shown = raw === ' ' ? 'SPACE' : raw;
  const text = `L${{y}} C${{x}} char=${{shown}} should be ...`;
  navigator.clipboard?.writeText(text);
  document.getElementById('readout').textContent = text;
}}));
</script>
"""


def main() -> None:
    reference_lines = LOCKED_REFERENCE.read_text(encoding="utf-8").rstrip("\n").splitlines() if LOCKED_REFERENCE.exists() else []
    generated_lines = build_two_room_generated()

    write_text(OUT_DIR / "two_room_generated.txt", generated_lines)
    (OUT_DIR / "two_room_generated_annotated.txt").write_text(annotate(generated_lines, REGIONS), encoding="utf-8")
    (OUT_DIR / "two_room_generated.html").write_text(html_review(generated_lines, REGIONS), encoding="utf-8")

    if reference_lines and reference_lines != generated_lines:
        raise SystemExit("Generated output does not match locked reference yet.")

    print("Generated output matches locked reference exactly.")
    print(OUT_DIR / "two_room_generated.txt")
    print(OUT_DIR / "two_room_generated_annotated.txt")
    print(OUT_DIR / "two_room_generated.html")


if __name__ == "__main__":
    main()