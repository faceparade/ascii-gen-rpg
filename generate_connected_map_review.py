"""Generate the single connected pre-elevation Grammar v2 review map."""
from pathlib import Path

from connected_map_v2 import connected_map_cells, connected_map_mask, feature_legend
from style_sample_system import render_irregular_room


def main() -> None:
    lines = [
        "GRAMMAR V2 SINGLE CONNECTED PRE-ELEVATION MAP — MANUAL REVIEW",
        "",
        "SUMMARY",
        "-------",
        "23 approved structural variations embedded in one cardinally connected map.",
        "Elevation data is intentionally absent.",
        "",
        "FEATURE LEGEND",
        "--------------",
        *feature_legend(),
        "",
        "LOGICAL MASK",
        "------------",
        *connected_map_mask(),
        "",
        "AUTOMATIC RENDERING",
        "-------------------",
        *render_irregular_room(connected_map_cells()),
    ]
    Path("connected-map-review.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
