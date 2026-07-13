"""Generate the organic connected pre-elevation Grammar v2 review dungeon."""
from pathlib import Path

from connected_map_v2 import connected_map_cells, connected_map_mask, feature_legend
from style_sample_system import render_irregular_room


def main() -> None:
    mask = connected_map_mask()
    cells = connected_map_cells()
    rendering = render_irregular_room(cells)
    lines = [
        "GRAMMAR V2 ORGANIC CONNECTED PRE-ELEVATION DUNGEON — MANUAL REVIEW",
        "",
        "SUMMARY",
        "-------",
        "23 approved structural variations embedded in one cardinally connected dungeon.",
        "Central junction complex, northern chambers, looping side wings, and a staggered southern route.",
        "No full-width gallery spine or detachable showcase rows.",
        "Elevation data is intentionally absent.",
        f"Logical dimensions: {len(mask[0])} columns × {len(mask)} rows.",
        f"Walkable logical cells: {len(cells)}.",
        f"Rendered dimensions: {max(map(len, rendering))} columns × {len(rendering)} rows.",
        "",
        "FEATURE LEGEND",
        "--------------",
        *feature_legend(),
        "",
        "LOGICAL MASK",
        "------------",
        *mask,
        "",
        "AUTOMATIC RENDERING",
        "-------------------",
        *rendering,
    ]
    Path("connected-map-review.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
