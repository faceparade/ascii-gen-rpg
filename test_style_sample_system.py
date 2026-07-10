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
    review_manifest,
)


def test_mask_normalizes_and_renders() -> None:
    cells = cells_from_mask(("..##", "..##"))
    assert cells == frozenset({Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)})
    assert render_mask(cells) == ("##", "##")


def test_outline_contains_source_style_corner_vocabulary() -> None:
    rows = render_bulk_outline(cells_from_mask(("##", "##")))
    text = "\n".join(rows)
    assert "," in text
    assert "." in text
    assert "`" in text
    assert "'" in text
    assert "|" in text
    assert "—" in text


def test_floor_backticks_mark_interior_grid_vertices() -> None:
    rows = render_bulk_outline(cells_from_mask(("####", "####", "####")))
    expected = {
        (3, 3),
        (7, 3),
        (11, 3),
        (3, 5),
        (7, 5),
        (11, 5),
    }
    assert all(rows[y][x] == "`" for x, y in expected)
    assert sum(rows[y].count("`") for y in (3, 5)) == len(expected)


def test_floor_backticks_do_not_fill_voids_or_exposed_notches() -> None:
    rows = render_bulk_outline(cells_from_mask(("###", "##.", "###")))
    assert rows[3].count("`") == 1
    assert rows[5].count("`") == 1


def test_irregular_shape_preserves_an_interior_turn() -> None:
    rows = render_bulk_outline(cells_from_mask(("##.", "###")))
    text = "\n".join(rows)
    assert "`—" in text
    assert len(rows[2]) > len(rows[0])


def test_catalog_is_unique_and_complete(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "samples": [
                    {"id": "one", "title": "One", "category": "room", "mask": ["#"]}
                ],
            }
        ),
        encoding="utf-8",
    )
    samples = load_catalog(catalog)
    assert samples[0].sample_id == "one"


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
    catalog.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "samples": [
                    {"id": "one", "title": "One", "category": "room", "mask": ["##"]}
                ],
            }
        ),
        encoding="utf-8",
    )
    (targets / "one.txt").write_text("HAND\nEDIT\n", encoding="utf-8")
    render = build_renders(catalog, targets)[0]
    assert render.target_rows == ("HAND", "EDIT")
    assert render.draft_rows != render.target_rows
    assert review_manifest((render,))["samples"][0]["has_target"] is True
