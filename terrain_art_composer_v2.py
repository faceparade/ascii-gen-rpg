"""Compose review artwork from approved ASCII fragments without mutating sources."""
from __future__ import annotations

from pathlib import Path


T_JUNCTION_SOURCES = (
    "sunken-mirrored-inside-cliff-corner-v2.txt",
    "sunken-inside-cliff-corner-v2.txt",
)


def transparent_stamp(
    canvas: list[list[str]],
    rows: list[str],
    *,
    x: int,
    y: int,
) -> None:
    """Overlay non-space glyphs on a fixed canvas, clipping at its boundaries."""

    height = len(canvas)
    for source_y, row in enumerate(rows):
        target_y = y + source_y
        if not 0 <= target_y < height:
            continue
        width = len(canvas[target_y])
        for source_x, glyph in enumerate(row):
            target_x = x + source_x
            if glyph != " " and 0 <= target_x < width:
                canvas[target_y][target_x] = glyph


def render_sunken_t_junction(project_root: Path) -> str:
    """Arrange two approved inside-corner treatments beneath one repeated north rim."""

    target_dir = project_root / "style_samples" / "targets"
    mirrored = (target_dir / T_JUNCTION_SOURCES[0]).read_text(encoding="utf-8").splitlines()
    inside = (target_dir / T_JUNCTION_SOURCES[1]).read_text(encoding="utf-8").splitlines()

    canvas = [[" "] * 50 for _ in range(16)]
    canvas[1][5:46] = list("," + "— —," * 10)
    canvas[2][5:46] = list("|__" + "/___" * 9 + "/_")
    canvas[3][5] = "|"
    canvas[4][5] = "|"

    mirrored_branch_wall = [row[:21] for row in mirrored[3:13]]
    inside_branch_wall = [row[8:23] for row in inside[2:11]]
    transparent_stamp(canvas, mirrored_branch_wall, x=0, y=5)
    transparent_stamp(canvas, inside_branch_wall, x=28, y=5)

    rendered = ["".join(row).rstrip() for row in canvas]
    while rendered and not rendered[-1]:
        rendered.pop()
    return "\n".join(rendered) + "\n"


def render_sunken_t_stitch_stress(project_root: Path) -> str:
    """Render the approved balanced 23-column T-junction seam composition."""

    del project_root  # Kept in the API for consistency with the source-based composer.
    rows = [
        "",
        "," + "— —," * 24,
        "___" + "/___" * 23 + "/_",
        "",
        "",
        "— " * 22 + "—." + " " * 7 + "," + "— " * 21 + "—",
        " " * 45 + "|      /|",
        " " * 45 + "|     ‘ |",
    ]
    for y in range(8, 24):
        right_face = "|/|" if y % 2 == 0 else "| |"
        rows.append(" " * 45 + "|" + " " * 5 + right_face)
    return "\n".join(rows) + "\n"
