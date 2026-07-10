from foreground_occlusion import (
    Entity,
    SOUTH_WEST_OFF,
    WALLS_ON,
    compose,
    diagnostic_entities,
    render_text,
    section_center,
    section_occluders,
)
from style_sample_system import Point


def test_reference_art_is_generated_by_grammar_v2() -> None:
    assert WALLS_ON[3] == "|/| `   `   `   |/|"
    assert SOUTH_WEST_OFF[3] == "|   `   `   `   |/|"
    assert WALLS_ON[8] == "| ,— —,— —,— —,—‘—,"
    assert SOUTH_WEST_OFF[8] == "|               | ,"


def test_four_by_four_actor_centers_are_offset_from_backticks() -> None:
    assert section_center(Point(0, 0)) == Point(2, 2)
    assert section_center(Point(3, 0)) == Point(14, 2)
    assert section_center(Point(0, 3)) == Point(2, 8)
    assert section_center(Point(3, 3)) == Point(14, 8)


def test_confirmed_occlusion_map() -> None:
    assert section_occluders(Point(0, 0)) == frozenset({"west"})
    assert section_occluders(Point(3, 1)) == frozenset()
    assert section_occluders(Point(1, 3)) == frozenset({"south"})
    assert section_occluders(Point(0, 3)) == frozenset({"west", "south"})


def test_opaque_and_xray_composition() -> None:
    entities = (
        Entity(Point(0, 0), "A"),
        Entity(Point(3, 0), "D"),
        Entity(Point(0, 3), "M"),
        Entity(Point(3, 3), "P"),
    )
    opaque = compose(entities, show_lattice=False)
    assert opaque.rows[2][2] == "|"
    assert opaque.rows[2][14] == "D"
    assert opaque.rows[8][2] == ","
    assert opaque.rows[8][14] == ","
    assert opaque.hidden_sections == frozenset({Point(0, 0), Point(0, 3), Point(3, 3)})

    xray = compose(entities, occlusion_mode="xray", show_lattice=False)
    assert xray.rows[2][2] == "a"
    assert xray.rows[2][14] == "D"
    assert xray.rows[8][2] == "m"
    assert xray.rows[8][14] == "p"
    assert xray.occluded_screen_points == frozenset({Point(2, 2), Point(2, 8), Point(14, 8)})


def test_removing_south_west_reveals_all_centers_and_retains_east_wall() -> None:
    result = compose(diagnostic_entities(), wall_view="south-west-off", mark_revealed=True, show_lattice=False)
    assert result.rows[2][2] == "a"
    assert result.rows[2][14] == "D"
    assert result.rows[8][2] == "m"
    assert result.rows[8][14] == "p"
    assert result.hidden_sections == frozenset()
    assert result.revealed_sections == frozenset(
        {
            Point(0, 0), Point(0, 1), Point(0, 2), Point(0, 3),
            Point(1, 3), Point(2, 3), Point(3, 3),
        }
    )


def test_rendered_diagnostic_contains_user_corrected_rows() -> None:
    output = render_text()
    assert "‘ |   B   C   D | |" in output
    assert "‘ a   B   C   D | |" in output
    assert "| m— —n— —o— —p—‘—," in output
    assert "| m   n   o   p | ," in output
