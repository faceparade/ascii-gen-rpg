#!/usr/bin/env python3
"""Three-room macro test built from the extracted curved dungeon grammar.

This does not change the locked two-room exact-match reference. It creates a
separate review artifact to test placing a third empty room shell on the shared
grid and connecting it with the locked horizontal corridor macro.
"""
from __future__ import annotations

from pathlib import Path

from curved_dungeon_grammar import (
    OUT_DIR,
    Rect,
    _paste,
    annotate,
    html_review,
    horizontal_corridor,
    room_shell_left_8,
    room_shell_middle_8,
    wide_platform,
)

ROOM_PITCH_X = 57
CORRIDOR_OFFSET_X = 32
ROOM_Y = 0
CORRIDOR_Y = 4
WIDE_PLATFORM_ROOM_OFFSET_X = 7
WIDE_PLATFORM_ROOM_OFFSET_Y = 5


def empty_terminal_room_shell_8() -> list[str]:
    """A clean 8-crossing room shell with floor ticks and no platform.

    This is intentionally a locked/non-parametric first pass. It follows the
    two-room shell grammar and keeps the right/east side terminal rather than
    adding a second platform. The left edge can be overwritten by a corridor
    macro when used as room 3.
    """
    return [
        ",— -,— -,— -,— -,— -,— -,— -,— -.",
        ",__/___/___/___/___/___/___/___/ |",
        ",                              |/|",
        ",  `   `   `   `   `   `   `   | |",
        ",                              |/|",
        ",  `   `   `   `   `   `   `   | |",
        ",                              |/|",
        ",  `   `   `   `   `   `   `   | |",
        ",                              |/|",
        ",  `   `   `   `   `   `   `   | |",
        ",                              |/|",
        "’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’",
    ]


def build_three_room_macro_test() -> list[str]:
    room_x = [0, ROOM_PITCH_X, ROOM_PITCH_X * 2]
    width = room_x[-1] + 36  # +1 keeps the terminal room's far-right cap visible.
    height = 12
    canvas: list[list[str]] = [[" "] * width for _ in range(height)]

    # Room shells.
    _paste(canvas, room_shell_left_8(), room_x[0], ROOM_Y)
    _paste(canvas, room_shell_middle_8(), room_x[1], ROOM_Y)
    _paste(canvas, empty_terminal_room_shell_8(), room_x[2], ROOM_Y)

    # Corridors: room1->room2 and room2->room3.
    for x in (room_x[0] + CORRIDOR_OFFSET_X, room_x[1] + CORRIDOR_OFFSET_X):
        _paste(canvas, horizontal_corridor(6), x, CORRIDOR_Y)

    # Keep the verified wide platform in room 2.
    _paste(
        canvas,
        wide_platform(4),
        room_x[1] + WIDE_PLATFORM_ROOM_OFFSET_X,
        ROOM_Y + WIDE_PLATFORM_ROOM_OFFSET_Y,
    )

    return ["".join(row).rstrip() for row in canvas]


def main() -> None:
    lines = build_three_room_macro_test()
    regions = [
        Rect("ROOM_1_LEFT_SHELL", 0, 0, 35, 12),
        Rect("CORRIDOR_1_TO_2", 32, 4, 28, 7),
        Rect("ROOM_2_MIDDLE_WITH_PLATFORM", 57, 0, 35, 12),
        Rect("ROOM_2_WIDE_PLATFORM", 64, 5, 20, 5),
        Rect("CORRIDOR_2_TO_3", 89, 4, 28, 7),
        Rect("ROOM_3_EMPTY_TERMINAL", 114, 0, 35, 12),
    ]

    txt = OUT_DIR / "three_room_macro_test.txt"
    ann = OUT_DIR / "three_room_macro_test_annotated.txt"
    html = OUT_DIR / "three_room_macro_test.html"

    txt.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    ann.write_text(annotate(lines, regions), encoding="utf-8")
    html.write_text(html_review(lines, regions), encoding="utf-8")

    print(txt)
    print(ann)
    print(html)
    print("lines", len(lines), "width", max(len(line) for line in lines))


if __name__ == "__main__":
    main()
