"""Generate the first sunken-terrain cliff artwork review."""
from pathlib import Path

from style_sample_system import Point
from terrain_cut_renderer_v2 import render_sunken_terrain

SURFACE_CELLS = frozenset(Point(x, y) for y in range(5) for x in range(7))
LOWER_CELLS = frozenset(
    {Point(x, y) for y in range(1, 4) for x in range(1, 4)}
    | {Point(x, 2) for x in range(4, 7)}
)
ELEVATIONS = {point: (0 if point in LOWER_CELLS else 1) for point in SURFACE_CELLS}


def main() -> None:
    rows = render_sunken_terrain(SURFACE_CELLS, ELEVATIONS, LOWER_CELLS)
    lines = [
        "GRAMMAR V2 SUNKEN CORRIDOR / CHAMBER CLIFF ART — MANUAL REVIEW",
        "",
        "ELEVATION",
        "---------",
        "1111111",
        "1000111",
        "1000000",
        "1000111",
        "1111111",
        "",
        "WALKABLE LOWER PLANE",
        "--------------------",
        ".......",
        ".###...",
        ".######",
        ".###...",
        ".......",
        "",
        "AUTOMATIC DRAFT",
        "---------------",
        *rows,
        "",
        "STATUS",
        "------",
        "Manual artwork review required. Topology is already approved.",
    ]
    Path("sunken-terrain-art-review.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
