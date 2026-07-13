"""Generate a local audit report for the approved Grammar v2 corridor matrix."""
from pathlib import Path

from corridor_variations_v2 import horizontal_corridor_bands, vertical_corridor_bands
from staggered_corridor_v2 import staggered_vertical_corridors
from style_sample_system import cells_from_mask, render_irregular_room

CASES = (
    ("TWO-SECTION-WIDE HORIZONTAL", ("###...###", "###...###", "#########", "#########", "###...###", "###...###"), horizontal_corridor_bands),
    ("WEST-OFFSET VERTICAL", ("#######", "#######", ".#.....", ".#.....", ".#.....", "#######", "#######"), vertical_corridor_bands),
    ("SHIFTED ROOMS EAST", ("#######....", "#######....", ".....#.....", ".....#.....", ".....#.....", "....#######", "....#######"), vertical_corridor_bands),
    ("SHIFTED ROOMS WEST", ("....#######", "....#######", ".....#.....", ".....#.....", ".....#.....", "#######....", "#######...."), vertical_corridor_bands),
    ("DOGLEG EASTWARD", ("#######", "#######", ".#.....", ".#.....", ".#####.", ".....#.", ".....#.", "#######", "#######"), staggered_vertical_corridors),
    ("DOGLEG WESTWARD", ("#######", "#######", ".....#.", ".....#.", ".#####.", ".#.....", ".#.....", "#######", "#######"), staggered_vertical_corridors),
    ("WIDE VERTICAL CENTERED", ("########", "########", "...##...", "...##...", "...##...", "########", "########"), vertical_corridor_bands),
    ("WIDE VERTICAL WEST-OFFSET", ("########", "########", ".##.....", ".##.....", ".##.....", "########", "########"), vertical_corridor_bands),
    ("WIDE VERTICAL EAST-OFFSET", ("########", "########", ".....##.", ".....##.", ".....##.", "########", "########"), vertical_corridor_bands),
    ("WIDE SHIFTED ROOMS", ("########....", "########....", ".....##.....", ".....##.....", ".....##.....", "....########", "....########"), vertical_corridor_bands),
)


def main() -> None:
    lines: list[str] = ["GRAMMAR V2 APPROVED CORRIDOR MATRIX", ""]
    for title, mask, classifier in CASES:
        cells = cells_from_mask(mask)
        lines.extend((title, "=" * len(title), "", "MASK", "----", *mask, "", "SEMANTICS", "---------"))
        lines.extend(repr(item) for item in classifier(cells))
        lines.extend(("", "RENDERING", "---------", *render_irregular_room(cells), "", ""))
    Path("corridor-matrix-audit.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
