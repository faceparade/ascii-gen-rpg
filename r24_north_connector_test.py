#!/usr/bin/env python3
"""Verification/artifact generator for port-aware R24 north connector experiments.

This is intentionally separate from the locked/editor baselines. It proves the
R24 downward tail can be treated as a port, mapped onto a chunk-based NorthWall
opening, then rendered as review artifacts for room-2-only and three-room cases.
"""
from __future__ import annotations

from pathlib import Path

from curved_dungeon_grammar import OUT_DIR, regular_vertical_pathway
from latest_r24_style import SOURCE_OF_TRUTH_PATH, r24_new_style_with_room3_platform
from modular_ascii_parts import Opening, NorthWall, north_wall_top_width, north_wall_underside_width
from r24_north_connector import (
    R24NorthConnector,
    build_r24_room2_only_case,
    build_r24_three_room_case,
    r24_tail_port,
    write_r24_connector_artifacts,
)

ROOM2_X = 57
ROOM_Y = 4
ROOM3_X = 114
SIX_ROOM_TOP_Y = 1


def assert_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}\nactual:   {actual!r}\nexpected: {expected!r}")


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)


def test_south_opening_template_spec_preserves_compact_r24_fragment() -> None:
    from connector_specs import SouthOpeningTemplateSpec
    from curved_dungeon_grammar import south_opening_template

    spec = SouthOpeningTemplateSpec.compact_r24()
    assert_equal(spec.name, "compact_r24", "south-opening spec should name the locked template")
    assert_equal(spec.rows, tuple(south_opening_template("compact_r24")), "south-opening spec should preserve locked rows byte-for-byte")
    assert_equal((spec.height, spec.min_room_local_x, spec.max_room_local_x, spec.width), (4, 8, 34, 26), "south-opening bbox should cover the ragged locked fragment")
    assert_equal(spec.origin_from_room(ROOM2_X, ROOM_Y), (ROOM2_X + 8, ROOM_Y - 4), "south-opening origin should be room-local to the target room")
    assert_equal(spec.region_from_room(ROOM2_X, ROOM_Y), (ROOM2_X + 8, ROOM_Y - 4, 26, 4), "south-opening region should map to global bbox")
    assert_equal(
        spec.rows_for_room(ROOM2_X, ROOM_Y),
        (
            (ROOM2_X + 8, ROOM_Y - 4, "|  `   `   `   `   `   |/|"),
            (ROOM2_X + 8, ROOM_Y - 3, "'— — — — — —.    ,— — — —'"),
            (ROOM2_X + 20, ROOM_Y - 2, "|  `/|"),
            (ROOM2_X + 20, ROOM_Y - 1, "|  , |"),
        ),
        "south-opening row triples should resolve to global paste coordinates",
    )


def test_vertical_pathway_spec_preserves_regular_r24_stamp() -> None:
    from connector_specs import VerticalPathwaySpec

    spec = VerticalPathwaySpec.regular_r24()
    assert_equal(spec.name, "regular_r24", "vertical pathway spec should name the locked R24 stamp")
    assert_equal(spec.width_units, 6, "regular R24 spec should preserve the locked width_units")
    assert_equal(spec.render(), regular_vertical_pathway(6), "vertical pathway spec should render the locked R24 stamp byte-for-byte")


def test_north_connector_spec_maps_room_local_opening_to_global_regions() -> None:
    from connector_specs import NorthConnectorSpec
    from presets import NORTH_OPENING_PRESETS

    spec = NorthConnectorSpec(
        name="r24_reference_compact",
        room_x=ROOM2_X,
        room_y=ROOM_Y,
        room_chunks=8,
        opening=NORTH_OPENING_PRESETS["compact_north_r24"],
        upper_rows=tuple(R24NorthConnector().reference_upper_rows),
    )
    spec.validate()
    assert_equal(spec.opening_start_x, ROOM2_X + 20, "compact R24 opening should start at chunk 6")
    assert_equal(spec.opening_window, (ROOM2_X + 20, ROOM_Y, 5, 2), "opening window should cover the rendered north-wall carve")
    assert_equal(spec.north_wall_region, (ROOM2_X, ROOM_Y, 34, 2), "north wall region should match the closed middle shell rows")
    assert_equal(spec.upper_fragment_origin, (ROOM2_X + 8, ROOM_Y - 4), "upper fragment should start from the first room-local row offset")


def test_north_connector_spec_builds_from_approved_opening_presets() -> None:
    from connector_specs import NorthConnectorSpec
    from presets import NORTH_OPENING_PRESETS

    for name, opening in NORTH_OPENING_PRESETS.items():
        spec = NorthConnectorSpec.from_opening_preset(name, room_x=ROOM2_X, room_y=ROOM_Y)
        spec.validate()
        expected_start_x = ROOM2_X + (opening.start_chunk - 1) * 4
        expected_width = opening.width_chunks * 4 + 1
        assert_equal(spec.opening, opening, f"{name} should use the named preset opening data")
        assert_equal(spec.opening_window, (expected_start_x, ROOM_Y, expected_width, 2), f"{name} should map to the expected global opening window")


def test_r24_tail_port_is_derived_from_locked_stamp() -> None:
    stamp = regular_vertical_pathway(6)
    port = r24_tail_port(stamp)
    assert_equal((port.left, port.right), (10, 16), "R24 tail side-wall bounds should come from the locked tail row")
    assert_equal(port.width, 7, "R24 tail port width should include both side-wall columns")
    assert_equal(port.suggested_opening_width_chunks, 2, "R24 tail should map to the smallest coherent NorthWall opening preset")


def test_r24_connector_exposes_reusable_vertical_pathway_spec() -> None:
    connector = R24NorthConnector(room_x=ROOM2_X, room_y=ROOM_Y, opening=Opening(6, 1))
    spec = connector.pathway_spec
    assert_equal((spec.name, spec.width_units), ("regular_r24", 6), "R24 connector should expose the reusable vertical pathway spec")
    assert_equal(connector.stamp, regular_vertical_pathway(6), "R24 connector stamp should be rendered through the pathway spec")


def test_connector_maps_opening_chunk_to_reference_corner() -> None:
    connector = R24NorthConnector(room_x=ROOM2_X, room_y=ROOM_Y, opening=Opening(6, 1))
    assert_equal(connector.opening_start_x, ROOM2_X + 20, "reference compact opening should start at chunk 6")
    assert_equal(connector.upper_fragment_x, ROOM2_X + 8, "upper fragment should begin 8 glyphs into the room")
    assert_equal(connector.stamp_y, ROOM_Y - 4, "upper fragment should occupy the four rows immediately north of the room edge")


def test_r24_connector_exposes_reusable_north_connector_spec() -> None:
    connector = R24NorthConnector(room_x=ROOM2_X, room_y=ROOM_Y, opening=Opening(6, 1))
    spec = connector.spec
    assert_equal(spec.name, "r24_reference_north", "R24 connector should name its reusable north-connector spec")
    assert_equal(spec.opening, connector.opening, "R24 connector spec should carry the selected opening")
    assert_equal(spec.upper_rows, tuple(connector.reference_upper_rows), "R24 connector spec should carry room-local upper fragment rows")
    assert_equal(spec.opening_window, (connector.opening_start_x, ROOM_Y, 5, 2), "R24 spec opening window should match connector math")
    assert_equal(spec.upper_fragment_origin, (connector.upper_fragment_x, connector.stamp_y), "R24 spec upper origin should match connector math")


def test_generated_cases_keep_widths_and_visible_port_anchors() -> None:
    connector = R24NorthConnector(room_x=ROOM2_X, room_y=ROOM_Y, opening=Opening(6, 1))
    room2 = build_r24_room2_only_case(connector)
    three_room = build_r24_three_room_case(connector)
    assert_true(len(room2) >= ROOM_Y + 12, "room2-only scene should include shifted room shell")
    assert_true(len(three_room) >= ROOM_Y + 12, "three-room scene should include shifted base")

    north_rows = NorthWall(8, (Opening(6, 1),)).render()
    assert_equal((len(north_rows[0]), len(north_rows[1])), (north_wall_top_width(8), north_wall_underside_width(8)), "parametric wall widths stay coherent")
    assert_equal(room2[connector.stamp_y][connector.upper_fragment_x:connector.upper_fragment_x + 26], "|  `   `   `   `   `   |/|", "upper row should match the new hand reference")
    assert_equal(room2[connector.stamp_y + 1][connector.upper_fragment_x:connector.upper_fragment_x + 26], "'— — — — — —.    ,— — — —'", "cap row should match the new curved corner style")
    assert_equal(room2[connector.stamp_y + 2][connector.opening_start_x:connector.opening_start_x + 6], "|  `/|", "tail-above-north-edge row should include the new vertical pass-through")
    assert_equal(room2[connector.stamp_y + 3][connector.opening_start_x:connector.opening_start_x + 6], "|  , |", "new fourth upper row should preserve the center movement space")
    assert_equal(room2[ROOM_Y][connector.opening_start_x:connector.opening_start_x + 5], "j  ,t", "room2 north-edge opening should use compact j/t corner join")
    assert_equal(room2[ROOM_Y + 1][connector.opening_start_x - 1:connector.opening_start_x + 5], "/   t_", "underside opening should keep slash-to-t corner join")
    room2_window = [row[ROOM2_X:ROOM2_X + 34] for row in three_room[ROOM_Y:ROOM_Y + 11]]
    room3_window = [row[ROOM3_X:ROOM3_X + 34] for row in three_room[ROOM_Y:ROOM_Y + 11]]
    assert_true(all("._ _" not in row and ";.;" not in row for row in room2_window), "three-room room2 should remain empty of raised floor detail")
    assert_true(any(";.;" in row for row in room3_window), "three-room room3 should contain moved raised floor section detail")
    assert_true("‘/___/___/;.;/___/___/" in "\n".join(room3_window), "three-room room3 should use corrected far-left curved raised-section column")


def test_r24_three_room_uses_six_room_source_of_truth() -> None:
    generated = build_r24_three_room_case(R24NorthConnector(room_x=ROOM2_X, room_y=ROOM_Y, opening=Opening(6, 1)))
    expected = r24_new_style_with_room3_platform()
    assert_equal(generated, expected, "R24 scene should use six_rooms_two_platforms.txt as source of truth")
    assert_equal(SOURCE_OF_TRUTH_PATH.name, "six_rooms_two_platforms.txt", "active source-of-truth path should be the six-room reference")
    assert_true(generated[SIX_ROOM_TOP_Y].startswith(",— —,"), "six-room scene should use the latest em-dash top-wall vocabulary, not the older comma-hyphen room art")
    assert_true(",— -," not in generated[SIX_ROOM_TOP_Y], "six-room scene should not regress to the previous comma-hyphen wall style")
    assert_true("._ _" not in "\n".join(row[ROOM2_X:ROOM2_X + 34] for row in generated[ROOM_Y:ROOM_Y + 11]), "room2 should be empty in generated R24 scene")
    assert_true(";.;" in "\n".join(row[ROOM3_X:ROOM3_X + 34] for row in generated[ROOM_Y:ROOM_Y + 11]), "room3 should carry the raised floor section")


def main() -> None:
    test_south_opening_template_spec_preserves_compact_r24_fragment()
    test_vertical_pathway_spec_preserves_regular_r24_stamp()
    test_north_connector_spec_maps_room_local_opening_to_global_regions()
    test_north_connector_spec_builds_from_approved_opening_presets()
    test_r24_tail_port_is_derived_from_locked_stamp()
    test_r24_connector_exposes_reusable_vertical_pathway_spec()
    test_connector_maps_opening_chunk_to_reference_corner()
    test_r24_connector_exposes_reusable_north_connector_spec()
    test_generated_cases_keep_widths_and_visible_port_anchors()
    test_r24_three_room_uses_six_room_source_of_truth()

    written = write_r24_connector_artifacts(OUT_DIR)
    for path in written:
        assert_true(Path(path).exists(), f"artifact should exist: {path}")
        print(path)
    print("PASS r24 north connector port-aware experiment")


if __name__ == "__main__":
    main()
