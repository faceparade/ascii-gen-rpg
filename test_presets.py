#!/usr/bin/env python3
"""Tests for the thin presets module (openings + shells)."""
from __future__ import annotations

from pathlib import Path

from presets import (
    NORTH_OPENING_PRESETS,
    RAISED_FRAGMENT_PRESETS,
    SCENE_FRAGMENT_PRESETS,
    SOUTH_OPENING_TEMPLATE_PRESETS,
    SHELL_PRESETS,
    VERTICAL_PATHWAY_PRESETS,
    build_north_opening,
    build_raised_fragment,
    build_scene_fragment,
    build_shell,
    build_south_opening_template,
    build_vertical_pathway,
)
from connector_specs import RaisedFragmentSpec, SceneFragmentSpec
from curved_dungeon_grammar import (
    regular_vertical_pathway,
    room_shell_middle_8,
    room_shell_left_8,
    south_opening_template,
)
from three_room_macro_test import empty_terminal_room_shell_8

ROOT = Path(__file__).resolve().parent


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

    # ── South-opening template preset data ──
    compact_r24_south = (
        (8, "|  `   `   `   `   `   |/|"),
        (8, "'— — — — — —.    ,— — — —'"),
        (20, "|  `/|"),
        (20, "|  , |"),
    )
    assert SOUTH_OPENING_TEMPLATE_PRESETS["compact_r24"] == compact_r24_south
    assert build_south_opening_template("compact_r24") is SOUTH_OPENING_TEMPLATE_PRESETS["compact_r24"]
    assert tuple(south_opening_template("compact_r24")) == compact_r24_south
    print("PASS: south-opening template preset data")

    # ── Vertical pathway preset data ──
    assert len(VERTICAL_PATHWAY_PRESETS["regular_r24_6"]) == 6
    assert all(len(row) == 27 for row in VERTICAL_PATHWAY_PRESETS["regular_r24_6"])
    assert build_vertical_pathway("regular_r24_6") is VERTICAL_PATHWAY_PRESETS["regular_r24_6"]
    assert regular_vertical_pathway(6) == list(VERTICAL_PATHWAY_PRESETS["regular_r24_6"])
    print("PASS: vertical pathway preset data")

    # ── Raised-fragment preset data ──
    line15_fragment = (
        "` ,— — — —'",
        " /|",
        ", |",
        "|/‘ —,— —,.",
        "‘/__/___/ |",
    )
    widened_fragment = (
        "` ,— — — — — — — — — — — —.",
        " /|                       |",
        ", |                       |",
        "|/|                       |",
    )
    center_decorated_fragment = (
        "` ,— — — — — — — — — —. `   ‘",
        " /|                   |      ",
        ", |                   | `   `",
        "|/‘— —,— —,— —,— —,— -'      ",
        "‘/___/___/;.;/___/___/  `   ,",
    )
    assert RAISED_FRAGMENT_PRESETS["connector_line15_short"] == line15_fragment
    assert RAISED_FRAGMENT_PRESETS["widened_27_partial"] == widened_fragment
    assert RAISED_FRAGMENT_PRESETS["center_decorated_29"] == center_decorated_fragment
    assert build_raised_fragment("connector_line15_short") is RAISED_FRAGMENT_PRESETS["connector_line15_short"]
    assert RaisedFragmentSpec.connector_line15_short().render() == list(line15_fragment)
    assert RaisedFragmentSpec.widened_27_partial().width == 27
    assert RaisedFragmentSpec.center_decorated_29().width == 29
    assert RaisedFragmentSpec.center_decorated_29().render()[4][10:13] == ";.;"
    print("PASS: raised-fragment preset data")

    # ── Generic scene-fragment preset data ──
    room_bottom_rail = ("`— — — — — — — — — — — — — — — — '",)
    room_top_band = (",— —,— —,— —,— —,— —,— —,— —,— —,.",)
    room_floor_band = ("|__/___/___/___/___/___/___/___/ |",)
    middle_seam_gap = (
        "                       ,— —,— —,— —,— —,— —'  |/‘ —,— —,.                       ",
        "                       |__/___/___/___/___/   ‘/__/___/ |                       ",
    )
    assert SCENE_FRAGMENT_PRESETS["room_bottom_rail_34"] == room_bottom_rail
    assert SCENE_FRAGMENT_PRESETS["room_top_band_34"] == room_top_band
    assert SCENE_FRAGMENT_PRESETS["room_floor_band_34"] == room_floor_band
    assert SCENE_FRAGMENT_PRESETS["middle_seam_connector_gap_80"] == middle_seam_gap
    assert build_scene_fragment("room_bottom_rail_34") is SCENE_FRAGMENT_PRESETS["room_bottom_rail_34"]
    assert SceneFragmentSpec.room_bottom_rail_34().width == 34
    assert SceneFragmentSpec.room_bottom_rail_34().render() == list(room_bottom_rail)
    assert SceneFragmentSpec.room_top_band_34().width == 34
    assert SceneFragmentSpec.room_floor_band_34().width == 34
    assert SceneFragmentSpec.middle_seam_connector_gap_80().width == 80
    lower_band_specs = {
        "lower_band_left_room_strip_34": SceneFragmentSpec.lower_band_left_room_strip_34(),
        "lower_band_gap_strip_23": SceneFragmentSpec.lower_band_gap_strip_23(),
        "lower_band_middle_room_strip_34": SceneFragmentSpec.lower_band_middle_room_strip_34(),
        "lower_band_right_room_strip_34": SceneFragmentSpec.lower_band_right_room_strip_34(),
    }
    assert lower_band_specs["lower_band_left_room_strip_34"].width == 34
    assert lower_band_specs["lower_band_gap_strip_23"].width == 23
    assert lower_band_specs["lower_band_middle_room_strip_34"].width == 34
    assert lower_band_specs["lower_band_right_room_strip_34"].width == 34
    assert {spec.height for spec in lower_band_specs.values()} == {7}
    for name, spec in lower_band_specs.items():
        assert spec.render() == list(SCENE_FRAGMENT_PRESETS[name])
    assert SceneFragmentSpec.room_top_band_34().render() == list(room_top_band)
    assert SceneFragmentSpec.room_floor_band_34().render() == list(room_floor_band)
    assert SceneFragmentSpec.middle_seam_connector_gap_80().render() == list(middle_seam_gap)
    print("PASS: generic scene-fragment preset data")

    # ── build_shell('middle_8') matches the locked middle reference ──
    assert build_shell("middle_8").render() == room_shell_middle_8()
    print("PASS: build_shell('middle_8') == room_shell_middle_8()")

    # ── build_shell('left_8') matches the locked left reference ──
    assert build_shell("left_8").render() == room_shell_left_8()
    print("PASS: build_shell('left_8') == room_shell_left_8()")

    # ── build_shell('terminal_8') matches the locked terminal reference ──
    assert build_shell("terminal_8").render() == empty_terminal_room_shell_8()
    print("PASS: build_shell('terminal_8') == empty_terminal_room_shell_8()")

    # ── build_shell('four_openings_single') matches the locked four-opening file ──
    four_openings = (ROOT / "single_room_four_openings.txt").read_text(encoding="utf-8").splitlines()
    assert build_shell("four_openings_single").render() == four_openings
    print("PASS: build_shell('four_openings_single') == single_room_four_openings.txt")

    # ── shell preset data sanity ──
    assert SHELL_PRESETS["middle_8"]["variant"] == "middle"
    assert SHELL_PRESETS["middle_8"]["width_chunks"] == 8
    assert SHELL_PRESETS["middle_8"]["height_chunks"] == 5
    assert SHELL_PRESETS["left_8"]["variant"] == "left"
    assert SHELL_PRESETS["terminal_8"]["variant"] == "terminal"
    assert SHELL_PRESETS["four_openings_single"]["variant"] == "four_openings"
    print("PASS: shell preset data")


if __name__ == "__main__":
    main()
    print("ALL PRESETS TESTS PASSED")
