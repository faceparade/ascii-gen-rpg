from pathlib import Path
import json

import pytest

from style_sample_system import (
    Point,
    build_renders,
    cells_from_mask,
    load_catalog,
    render_bulk_outline,
    render_mask,
    render_projected_room_shell,
    review_manifest,
)


def test_mask_normalizes_and_renders() -> None:
    cells = cells_from_mask(("..##", "..##"))
    assert cells == frozenset({Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)})
    assert render_mask(cells) == ("##", "##")


def test_outline_contains_source_style_corner_vocabulary() -> None:
    text = "\n".join(render_bulk_outline(cells_from_mask(("##", "##"))))
    for glyph in ",.`'|—":
        assert glyph in text


def test_one_section_is_five_by_three_with_center_marker() -> None:
    rows = render_bulk_outline(cells_from_mask(("#",)))
    assert len(rows) == 3
    assert max(map(len, rows)) == 5
    assert rows[1][2] == "`"


def test_adjacent_sections_share_outside_edges() -> None:
    rows = render_bulk_outline(cells_from_mask(("##",)))
    assert max(map(len, rows)) == 9
    assert rows[1][2] == "`"
    assert rows[1][6] == "`"


def test_three_by_two_floor_has_six_center_indicators() -> None:
    rows = render_bulk_outline(cells_from_mask(("###", "###")))
    expected = {(2, 1), (6, 1), (10, 1), (2, 3), (6, 3), (10, 3)}
    assert all(rows[y][x] == "`" for x, y in expected)


def test_four_by_two_projected_room_has_correct_north_and_east_walls() -> None:
    assert render_projected_room_shell(4, 2) == (
        ",— —,— —,— —,— —,— —,.",
        "|__/___/___/___/___/ |",
        "|                  |/|",
        "|  `   `   `   `   | |",
        "|                  |/|",
        "|  `   `   `   `   | |",
        "|                  |/|",
        "`— — — — — — — — — — '",
    )


def test_source_proportion_room_matches_closed_reference_shell() -> None:
    rows = render_projected_room_shell(7, 4)
    assert rows[0] == ",— —,— —,— —,— —,— —,— —,— —,— —,."
    assert rows[1] == "|__/___/___/___/___/___/___/___/ |"
    assert rows[2] == "|                              |/|"
    assert rows[3] == "|  `   `   `   `   `   `   `   | |"
    assert rows[-2] == "|                              |/|"
    assert rows[-1] == "`— — — — — — — — — — — — — — — — '"


def test_section_markers_follow_occupied_irregular_cells() -> None:
    rows = render_bulk_outline(cells_from_mask(("##.", "###")))
    expected = {(2, 1), (6, 1), (2, 3), (6, 3), (10, 3)}
    assert all(rows[y][x] == "`" for x, y in expected)


def test_irregular_shape_preserves_an_interior_turn() -> None:
    rows = render_bulk_outline(cells_from_mask(("##.", "###")))
    assert "`—" in "\n".join(rows)
    assert len(rows[2]) > len(rows[0])


def test_catalog_is_unique_and_complete(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema_version": 1, "samples": [{"id": "one", "title": "One", "category": "room", "mask": ["#"]}]}), encoding="utf-8")
    assert load_catalog(catalog)[0].sample_id == "one"


def test_duplicate_catalog_ids_are_rejected(tmp_path: Path) -> None:
    item = {"id": "same", "title": "Same", "category": "room", "mask": ["#"]}
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema_version": 1, "samples": [item, item]}), encoding="utf-8")
    with pytest.raises(ValueError, match="unique"):
        load_catalog(catalog)


def test_targets_are_loaded_without_modifying_drafts(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.json"
    targets = tmp_path / "targets"
    targets.mkdir()
    catalog.write_text(json.dumps({"schema_version": 1, "samples": [{"id": "one", "title": "One", "category": "room", "mask": ["##"]}]}), encoding="utf-8")
    (targets / "one.txt").write_text("HAND\nEDIT\n", encoding="utf-8")
    render = build_renders(catalog, targets)[0]
    assert render.target_rows == ("HAND", "EDIT")
    assert render.draft_rows != render.target_rows
    assert review_manifest((render,))["samples"][0]["has_target"] is True
