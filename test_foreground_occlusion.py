from foreground_occlusion import (
    Entity,
    SOUTH_WEST_OFF,
    WALLS_ON,
    compose,
    section_center,
    section_occluders,
)
from style_sample_system import Point


def test_reference_art_is_preserved() -> None:
    assert WALLS_ON[3] == "|/| `   `   `   |/|"
    assert SOUTH_WEST_OFF[3] == "|   `   `   `   |/|"
    assert WALLS_ON[8] == "| ,— —,— —,— —,—‘—,"
    assert SOUTH_WEST_OFF[8] == "|               | ,"


def test_four_by_four_section_centers() -> None:
    assert section_center(Point(0, 0)) == Point(4, 3)
    assert section_center(Point(3, 0)) == Point(16, 3)
    assert section_center(Point(0, 3)) == Point(4, 9)
    assert section_center(Point(3, 3)) == Point(16, 9)


def test_provisional_occlusion_map() -> None:
    assert section_occluders(Point(0, 0)) == frozenset()
    assert section_occluders(Point(3, 1)) == frozenset({"east"})
    assert section_occluders(Point(1, 3)) == frozenset({"south"})
    assert section_occluders(Point(3, 3)) == frozenset({"east", "south"})
    assert all("west" not in section_occluders(Point(0, y)) for y in range(4))


def test_opaque_and_xray_composition() -> None:
    entities = (
        Entity(Point(0, 0), "A"),
        Entity(Point(3, 0), "D"),
        Entity(Point(0, 3), "M"),
        Entity(Point(3, 3), "P"),
    )
    opaque = compose(entities)
    assert opaque.rows[3][4] == "A"
    assert opaque.rows[3][16] == "|"
    assert opaque.rows[9][4] == "_"
    assert opaque.hidden_sections == frozenset({Point(3, 0), Point(0, 3), Point(3, 3)})

    xray = compose(entities, occlusion_mode="xray")
    assert xray.rows[3][16] == "d"
    assert xray.rows[9][4] == "m"
    assert xray.rows[9][16] == "p"
    assert xray.occluded_screen_points == frozenset({Point(16, 3), Point(4, 9), Point(16, 9)})


def test_removing_south_west_reveals_south_but_not_east() -> None:
    result = compose(
        (Entity(Point(0, 3), "M"), Entity(Point(3, 1), "H")),
        wall_view="south-west-off",
    )
    assert result.rows[9][4] == "M"
    assert result.rows[5][16] == "|"
    assert result.hidden_sections == frozenset({Point(3, 1)})
