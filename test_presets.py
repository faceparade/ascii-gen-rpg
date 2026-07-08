#!/usr/bin/env python3
"""Tests for the thin presets module (openings + shells)."""
from __future__ import annotations

from presets import (
    NORTH_OPENING_PRESETS,
    SHELL_PRESETS,
    build_shell,
    build_north_opening,
)
from curved_dungeon_grammar import (
    room_shell_middle_8,
    room_shell_left_8,
)
from three_room_macro_test import empty_terminal_room_shell_8


def main() -> None:
    # ── North-opening preset data ──
    assert NORTH_OPENING_PRESETS["compact_north_r24"].start_chunk == 6
    assert NORTH_OPENING_PRESETS["compact_north_r24"].width_chunks == 1
    assert NORTH_OPENING_PRESETS["center_2"].start_chunk == 4
    assert NORTH_OPENING_PRESETS["center_2"].width_chunks == 2
    assert NORTH_OPENING_PRESETS["wide_4"].start_chunk == 3
    assert NORTH_OPENING_PRESETS["wide_4"].width_chunks == 4
    assert NORTH_OPENING_PRESETS["center_4"].start_chunk == 3
    assert NORTH_OPENING_PRESETS["center_4"].width_chunks == 4
    assert NORTH_OPENING_PRESETS["wide_6"].start_chunk == 2
    assert NORTH_OPENING_PRESETS["wide_6"].width_chunks == 6
    print("PASS: north-opening preset data")

    # ── build_north_opening helper ──
    assert build_north_opening("compact_north_r24") is NORTH_OPENING_PRESETS["compact_north_r24"]
    assert build_north_opening("wide_4").width_chunks == 4
    print("PASS: build_north_opening helper")

    # ── build_shell('middle_8') matches the locked middle reference ──
    assert build_shell("middle_8").render() == room_shell_middle_8()
    print("PASS: build_shell('middle_8') == room_shell_middle_8()")

    # ── build_shell('left_8') matches the locked left reference ──
    assert build_shell("left_8").render() == room_shell_left_8()
    print("PASS: build_shell('left_8') == room_shell_left_8()")

    # ── build_shell('terminal_8') matches the locked terminal reference ──
    assert build_shell("terminal_8").render() == empty_terminal_room_shell_8()
    print("PASS: build_shell('terminal_8') == empty_terminal_room_shell_8()")

    # ── shell preset data sanity ──
    assert SHELL_PRESETS["middle_8"]["variant"] == "middle"
    assert SHELL_PRESETS["middle_8"]["width_chunks"] == 8
    assert SHELL_PRESETS["middle_8"]["height_chunks"] == 5
    assert SHELL_PRESETS["left_8"]["variant"] == "left"
    assert SHELL_PRESETS["terminal_8"]["variant"] == "terminal"
    print("PASS: shell preset data")


if __name__ == "__main__":
    main()
    print("ALL PRESETS TESTS PASSED")
