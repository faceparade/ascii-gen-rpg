"""Generate literal review output for wide, offset, and staggered corridors."""
from pathlib import Path

from corridor_variations_v2 import horizontal_corridor_bands, vertical_corridor_bands
from staggered_corridor_v2 import staggered_vertical_corridors
from style_sample_system import cells_from_mask, render_irregular_room

CASES = (
    (
        "TWO-SECTION-WIDE HORIZONTAL CORRIDOR",
        (
            "###...###",
            "###...###",
            "#########",
            "#########",
            "###...###",
            "###...###",
        ),
        horizontal_corridor_bands,
    ),
    (
        "OFFSET VERTICAL CORRIDOR",
        (
            "#######",
            "#######",
            ".#.....",
            ".#.....",
            ".#.....",
            "#######",
            "#######",
        ),
        vertical_corridor_bands,
    ),
    (
        "STAGGERED DOGLEG CORRIDOR",
        (
            "#######",
            "#######",
            ".#.....",
            ".#.....",
            ".#####.",
            ".....#.",
            ".....#.",
            "#######",
            "#######",
        ),
        staggered_vertical_corridors,
    ),
)


def main() -> None:
    lines: list[str] = ["GRAMMAR V2 CORRIDOR VARIATIONS — AUTOMATIC REVIEW", ""]
    for title, mask, classifier in CASES:
        cells = cells_from_mask(mask)
        lines.extend((title, "=" * len(title), "", "MASK", "----", *mask, ""))
        lines.append("SEMANTICS")
        lines.append("---------")
        for band in classifier(cells):
            lines.append(repr(band))
        lines.extend(("", "AUTOMATIC DRAFT", "---------------", *render_irregular_room(cells), "", ""))
    Path("corridor-variations-review.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
