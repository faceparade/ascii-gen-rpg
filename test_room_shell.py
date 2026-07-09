#!/usr/bin/env python3
"""Exact-match and behavior tests for the parametric RoomShell generator."""
from __future__ import annotations

from pathlib import Path

from room_shell import RoomShell, single_room_four_openings_shell
from modular_ascii_parts import NorthWall, Opening
from caps import VerticalOpening
from curved_dungeon_grammar import room_shell_middle_8, room_shell_left_8, room_shell_middle_8_west_east
from three_room_macro_test import empty_terminal_room_shell_8

ROOT = Path(__file__).resolve().parent


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}\nactual:   {actual!r}\nexpected: {expected!r}")


def test_byte_for_byte_match() -> None:
    generated = RoomShell().render()
    locked = room_shell_middle_8()
    assert_equal(generated, locked, "RoomShell() must reproduce room_shell_middle_8() byte-for-byte")
    print("PASS byte-for-byte match vs locked room_shell_middle_8()")


def test_middle_shell_has_no_embedded_raised_floor_section() -> None:
    generated = RoomShell().render()
    joined = "\n".join(generated)
    assert "._ _" not in joined, "RoomShell() should not include the modular raised floor section"
    assert ";.;" not in joined, "RoomShell() should not include raised floor section detail"
    print("PASS middle shell is empty of raised floor sections by default")


def test_left_variant_match() -> None:
    generated = RoomShell(variant="left").render()
    locked = room_shell_left_8()
    assert_equal(generated, locked, "RoomShell(variant='left') must reproduce room_shell_left_8() byte-for-byte")
    print("PASS byte-for-byte match vs locked room_shell_left_8()")


def test_terminal_variant_match() -> None:
    generated = RoomShell(variant="terminal").render()
    locked = empty_terminal_room_shell_8()
    assert_equal(generated, locked, "RoomShell(variant='terminal') must reproduce empty_terminal_room_shell_8() byte-for-byte")
    print("PASS byte-for-byte match vs locked empty_terminal_room_shell_8()")


def test_four_openings_variant_matches_locked_file() -> None:
    locked = (ROOT / "single_room_four_openings.txt").read_text(encoding="utf-8").splitlines()
    generated = RoomShell(variant="four_openings").render()
    assert_equal(generated, locked, "RoomShell(variant='four_openings') must match single_room_four_openings.txt byte-for-byte")
    assert_equal(single_room_four_openings_shell(), locked, "single_room_four_openings_shell() must match locked file")
    assert_equal(len(generated), 15, "four-opening locked shell row count")
    assert_equal(sorted({len(row) for row in generated}), [33, 42, 44, 45], "four-opening locked shell preserves intentional ragged widths")
    assert_equal(generated[0].startswith("       ,"), True, "four-opening first row keeps seven-space left pad")
    assert_equal(generated[4].startswith("— —,— —,"), True, "west opening left connector is preserved")
    assert_equal(generated[13].rstrip().endswith(",— — — —'"), True, "south/north lower connector is preserved")
    print("PASS four-opening RoomShell variant matches locked single_room_four_openings.txt")


def test_height_default_equivalence() -> None:
    generated = RoomShell(height_chunks=5, variant="middle").render()
    locked = room_shell_middle_8()
    assert_equal(generated, locked, "RoomShell(height_chunks=5, variant='middle') must equal room_shell_middle_8()")
    print("PASS height_chunks=5 equivalence for middle variant")


def test_middle_close_transform_matches_locked_north_rows() -> None:
    from room_shell import close_north_wall_for_middle

    bare = NorthWall(8).render()
    closed = close_north_wall_for_middle(bare)
    locked = room_shell_middle_8()
    assert_equal(closed, locked[:2], "closed bare NorthWall must equal locked middle north rows")
    print("PASS middle close transform matches locked north rows")


def test_internal_width_consistency() -> None:
    # terminal: every row is uniformly full width (no trailing spaces),
    # except the north top row which is one shorter by design.
    shell = RoomShell(variant="terminal")
    rows = shell.render()
    for r in range(1, len(rows)):
        assert_equal(len(rows[r]), shell.full_width, f"terminal row {r} should be full width")
    assert_equal(len(rows[0]), shell.north_top_width, "terminal north top row width")

    # middle v3: the box is rectangular — every row (including the north top
    # row) is full width (34) because v3 closes the box with a '|' right wall.
    shell = RoomShell(variant="middle")
    rows = shell.render()
    for r in range(len(rows)):
        assert_equal(len(rows[r]), shell.full_width, f"middle v3 row {r} should be full width (34)")
    assert_equal(len(rows[0]), shell.full_width, "middle v3 north top row is full width (box closed)")
    # left variant is intentionally 35 wide (trailing-space padded lock).
    shell = RoomShell(variant="left")
    rows = shell.render()
    for r in range(len(rows)):
        assert_equal(len(rows[r]), 35, f"left variant row {r} should be 35 wide")
    print("PASS internal width consistency")


def test_north_opening_delegates_to_northwall() -> None:
    opening = Opening(6, 1)
    shell_rows = RoomShell(north_opening=opening).render()
    wall_rows = NorthWall(8, (opening,)).render()
    # The v3 top row closes the box differently from the bare NorthWall top,
    # but the opening carve (j / ,t corners) must still be present and in the
    # same position as NorthWall produces.
    assert "j" in shell_rows[0] and ",t" in shell_rows[0], \
        "v3 top row should carry the NorthWall opening carve (j / ,t)"
    assert wall_rows[0] in (shell_rows[0] + "|") or shell_rows[0].startswith(wall_rows[0][:-1]), \
        "v3 top row should embed the NorthWall opening carve"
    assert_equal(shell_rows[1], "|" + wall_rows[1][1:], "v3 underside row keeps NorthWall carve with closed left wall")
    print("PASS north opening carve embedded in v3 top row")


def test_west_east_openings_carve_side_walls() -> None:
    # West opening: a doorway through the left wall band, rows 4..6.
    # v3 west wall is solid '|' on every body row.
    west = RoomShell(variant="middle", west_opening=VerticalOpening(4, 3)).render()
    assert_equal(west[0], room_shell_middle_8()[0], "west opening must not touch north wall")
    assert_equal(west[0][0], ",", "west wall col0 above opening unchanged (row 0 is ',')")
    assert_equal(west[4][0], "j", "west opening top cap")
    assert_equal(west[5][0], " ", "west opening inner fill")
    assert_equal(west[6][0], "t", "west opening bottom cap")
    # Rows outside the opening keep the locked base glyph for that row.
    assert_equal(west[3][0], room_shell_middle_8()[3][0], "west wall col0 above opening start unchanged")
    assert_equal(west[7][0], room_shell_middle_8()[7][0], "west wall col0 below opening unchanged")
    print("PASS west opening carves left column with j/ /t caps")

    # East opening: a doorway through the right wall band, rows 4..7.
    base = room_shell_middle_8()
    east = RoomShell(variant="middle", east_opening=VerticalOpening(4, 4)).render()
    assert_equal(east[0], base[0], "east opening must not touch north wall")
    assert_equal(east[4][-1], "/", "east opening top cap")
    assert_equal(east[5][-1], " ", "east opening inner fill")
    assert_equal(east[6][-1], " ", "east opening inner fill")
    assert_equal(east[7][-1], "t", "east opening bottom cap")
    # Rows outside the opening keep the locked base glyph for that row.
    assert_equal(east[3][-1], base[3][-1], "east wall col right above opening start unchanged")
    assert_equal(east[8][-1], base[8][-1], "east wall col right below opening unchanged")
    print("PASS east opening carves right column with // /t caps")


def test_middle_both_side_openings_use_locked_literal() -> None:
    shell = RoomShell(
        variant="middle",
        west_opening=VerticalOpening(4, 3),
        east_opening=VerticalOpening(4, 4),
    ).render()
    locked = room_shell_middle_8_west_east()
    assert_equal(shell, locked, "both-side middle doorway must use locked hand-drawn literal")
    assert_equal({len(row) for row in shell}, {36}, "both-door locked shell must be uniformly 36 wide")
    assert_equal(shell[8][25], "j", "west lower doorway corner must land on the structure grid")
    assert_equal(shell[9][33], "/", "east lower doorway corner must sit inside the east wall")
    print("PASS both-side middle doorway uses locked literal with grid-aligned corners")


def test_embedded_raised_floor_fallback_removed() -> None:
    # v3 has no embedded raised floor section; the legacy 'has_platform' field was removed.
    shell = RoomShell(variant="middle")
    assert not hasattr(shell, "has_platform"), "has_platform field should be removed in v3"
    assert_equal(len(shell.render()), 11, "v3 middle shell is 11 rows")
    print("PASS v3 middle shell has no embedded raised floor field (11 rows)")


def test_side_openings_none_preserves_locked() -> None:
    # Default (None) side openings must remain byte-for-byte identical.
    assert_equal(RoomShell(variant="middle").render(), room_shell_middle_8(),
                 "middle with None side openings == locked")
    assert_equal(RoomShell(variant="left").render(), room_shell_left_8(),
                 "left with None side openings == locked")
    assert_equal(RoomShell(variant="terminal").render(), empty_terminal_room_shell_8(),
                 "terminal with None side openings == locked")
    print("PASS None side openings preserve locked shells (regression)")


def test_left_scaling_not_implemented() -> None:
    try:
        RoomShell(variant="left", width_chunks=9).render()
    except NotImplementedError:
        pass
    else:
        raise AssertionError("left variant width scaling should raise NotImplementedError")
    print("PASS left variant scaling raises NotImplementedError")


if __name__ == "__main__":
    test_byte_for_byte_match()
    test_middle_shell_has_no_embedded_raised_floor_section()
    test_left_variant_match()
    test_terminal_variant_match()
    test_four_openings_variant_matches_locked_file()
    test_height_default_equivalence()
    test_middle_close_transform_matches_locked_north_rows()
    test_internal_width_consistency()
    test_north_opening_delegates_to_northwall()
    test_embedded_raised_floor_fallback_removed()
    test_west_east_openings_carve_side_walls()
    test_middle_both_side_openings_use_locked_literal()
    test_side_openings_none_preserves_locked()
    test_left_scaling_not_implemented()
    print("ALL RoomShell tests passed")
