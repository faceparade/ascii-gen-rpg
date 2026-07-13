"""Generate literal review output for the complete Grammar v2 corridor matrix."""
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
        "WEST-OFFSET VERTICAL CORRIDOR",
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
        "SHIFTED ROOMS WITH STRAIGHT CORRIDOR",
        (
            "#######....",
            "#######....",
            ".....#.....",
            ".....#.....",
            ".....#.....",
            "....#######",
            "....#######",
        ),
        vertical_corridor_bands,
    ),
    (
        "MIRRORED SHIFTED ROOMS WITH STRAIGHT CORRIDOR",
        (
            "....#######",
            "....#######",
            ".....#.....",
            ".....#.....",
            ".....#.....",
            "#######....",
            "#######....",
        ),
        vertical_corridor_bands,
    ),
    (
        "EASTWARD DOGLEG CORRIDOR",
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
    (
        "WESTWARD DOGLEG CORRIDOR",
        (
            "#######",
            "#######",
            ".....#.",
            ".....#.",
            ".#####.",
            ".#.....",
            ".#.....",
            "#######",
            "#######",
        ),
        staggered_vertical_corridors,
    ),
    (
        "CENTERED TWO-SECTION-WIDE VERTICAL CORRIDOR",
        (
            "########",
            "########",
            "...##...",
            "...##...",
            "...##...",
            "########",
            "########",
        ),
        vertical_corridor_bands,
    ),
    (
        "WEST-OFFSET TWO-SECTION-WIDE VERTICAL CORRIDOR",
        (
            "########",
            "########",
            ".##.....",
            ".##.....",
            ".##.....",
            "########",
            "########",
        ),
        vertical_corridor_bands,
    ),
    (
        "EAST-OFFSET TWO-SECTION-WIDE VERTICAL CORRIDOR",
        (
            "########",
            "########",
            ".....##.",
            ".....##.",
            ".....##.",
            "########",
            "########",
        ),
        vertical_corridor_bands,
    ),
    (
        "TWO-SECTION-WIDE CORRIDOR BETWEEN SHIFTED ROOMS",
        (
            "########....",
            "########....",
            ".....##.....",
            ".....##.....",
            ".....##.....",
            "....########",
            "....########",
        ),
        vertical_corridor_bands,
    ),
)


def main() -> None:
    lines: list[str] = ["GRAMMAR V2 CORRIDOR MATRIX — AUTOMATIC REVIEW", ""]
    for title, mask, classifier in CASES:
        cells = cells_from_mask(mask)
        lines.extend((title, "=" * len(title), "", "MASK", "----", *mask, ""))
        lines.append("SEMANTICS")
        lines.append("---------")
        for band in classifier(cells):
            lines.append(repr(band))
        lines.extend(("", "AUTOMATIC DRAFT", "---------------", *render_irregular_room(cells), "", ""))
    Path("corridor-matrix-review.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
