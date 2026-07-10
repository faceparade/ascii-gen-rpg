from pathlib import Path
import json

import pytest

from style_sample_system import (
    BoundaryEdge,
    Point,
    actor_anchor,
    build_renders,
    cells_from_mask,
    lattice_points,
    lattice_vertices,
    load_catalog,
    projection_model,
    render_bulk_outline,
    render_irregular_room,
    render_mask,
    render_projected_room_shell,
    review_manifest,
    section_occluders,
)


def test_mask_normalizes_and_renders() -> None:
    cells = cells_from_mask(("..##", "..##"))
    assert cells == frozenset({Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)})
    assert render_mask(cells) == ("##", "##")


def test_one_by_one_has_actor_anchor_but_no_lattice_marker() -> None:
    cells = cells_from_mask(("#",))
    model = projection_model(cells)
    assert model.actor_anchors == ((Point(0, 0), Point(2, 2)),)
    assert model.lattice_markers == frozenset()
    assert section_occluders(cells, Point(0, 0)) == frozenset({"west", "south"})


def test_two_by_two_has_one_shared_lattice_intersection() -> None:
    cells = cells_from_mask(("##", "##"))
    assert lattice_vertices(cells) == frozenset({Point(1, 1)})
    assert lattice_points(cells) == frozenset({Point(4, 3)})
    assert actor_anchor(Point(0, 0)) == Point(2, 2)
    assert actor_anchor(Point(1, 1)) == Point(6, 4)


def test_four_by_four_projected_room_matches_approved_wall_fixture() -> None:
    assert render_projected_room_shell(4, 4) == (
        "  ,— —,— —,— —,— —,",
        " /|__/___/___/__ /|",
        "‘ |             | |",
        "|/| `   `   `   |/|",
        "| |             | |",
        "|/| `   `   `   |/|",
        "| |             | |",
        "|/| `   `   `   |/|",
        "| ,— —,— —,— —,—‘—,",
        "‘/___/___/___/___/",
    )


def test_four_by_four_foreground_removed_matches_floor_reference() -> None:
    assert render_projected_room_shell(4, 4, foreground=False) == (
        "  ,— —,— —,— —,— —,",
        " /___/___/___/__ /|",
        "‘               | |",
        "|   `   `   `   |/|",
        "|               | |",
        "|   `   `   `   |/|",
        "|               | |",
        "|   `   `   `   |/|",
        "|               | ,",
        "‘ ___ ___ ___ ___/",
    )


def test_l_shape_has_directional_edges_and_only_complete_lattice_vertices() -> None:
    cells = cells_from_mask(("###", "##.", "##."))
    model = projection_model(cells)
    assert model.lattice_markers == frozenset({Point(4, 3), Point(4, 5)})
    assert BoundaryEdge(Point(1, 1), "east") in model.east_edges
    assert BoundaryEdge(Point(2, 0), "south") in model.south_edges
    assert model.west_occluded_sections == frozenset({Point(0, 0), Point(0, 1), Point(0, 2)})
    assert model.south_occluded_sections == frozenset({Point(2, 0), Point(0, 2), Point(1, 2)})
    assert Point(2, 0) in model.foreground_occluded_sections


def test_l_shape_renderer_preserves_void_and_concave_turn() -> None:
    cells = cells_from_mask(("###", "##.", "##."))
    rows = render_irregular_room(cells)
    text = "\n".join(rows)
    assert text.count("`") == 2
    assert "/" in text
    assert "," in text
    assert len(rows) >= 7


def test_coarse_fallback_uses_lattice_intersections_not_one_marker_per_cell() -> None:
    cells = cells_from_mask(("###", "###"))
    rows = render_bulk_outline(cells)
    assert rows[1][2] == "`"
    assert rows[1][6] == "`"
    assert sum(row.count("`") for row in rows[1:2]) == 2


def test_catalog_is_unique_and_complete(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        json.dumps({"schema_version": 1, "samples": [{"id": "one", "title": "One", "category": "room", "mask": ["#"]}]}),
        encoding="utf-8",
    )
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
    catalog.write_text(
        json.dumps({"schema_version": 1, "samples": [{"id": "one", "title": "One", "category": "room", "mask": ["##"]}]}),
        encoding="utf-8",
    )
    (targets / "one.txt").write_text("HAND\nEDIT\n", encoding="utf-8")
    render = build_renders(catalog, targets)[0]
    assert render.target_rows == ("HAND", "EDIT")
    assert render.draft_rows != render.target_rows
    assert review_manifest((render,))["samples"][0]["has_target"] is True
