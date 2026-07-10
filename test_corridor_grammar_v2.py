from junction_grammar_v2 import HorizontalJunction, horizontal_junctions
from style_sample_system import cells_from_mask, render_irregular_room

U_MASK = ("##..##", "##..##", "##..##", "######")
EAST_BRIDGE_MASK = ("##....", "##....", "######")
WEST_BRIDGE_MASK = ("....##", "....##", "######")
CORRIDOR_MASK = (
    "###...###",
    "###...###",
    "#########",
    "###...###",
    "###...###",
)


def test_shared_classifier_keeps_promoted_junction_kinds_distinct() -> None:
    assert horizontal_junctions(cells_from_mask(U_MASK)) == (
        HorizontalJunction(
            "courtyard_bridge", 3, 2, 3, "inner_east_wall", "inner_west_wall"
        ),
    )
    assert horizontal_junctions(cells_from_mask(EAST_BRIDGE_MASK)) == (
        HorizontalJunction(
            "east_extending_bridge", 2, 2, 5, "inner_east_wall", "exterior_east"
        ),
    )
    assert horizontal_junctions(cells_from_mask(WEST_BRIDGE_MASK)) == (
        HorizontalJunction(
            "west_extending_bridge", 2, 0, 3, "exterior_west", "inner_west_wall"
        ),
    )


def test_two_room_passage_is_classified_as_corridor_not_bridge() -> None:
    assert horizontal_junctions(cells_from_mask(CORRIDOR_MASK)) == (
        HorizontalJunction(
            "horizontal_corridor", 2, 3, 5, "inner_east_wall", "inner_west_wall"
        ),
    )


def test_corridor_north_wall_uses_background_underside() -> None:
    rows = render_irregular_room(cells_from_mask(CORRIDOR_MASK))
    assert rows[4] == "| |         | ,— —,— —,—‘—,         | |"
    assert rows[5] == "|/| `   `    /|__/___/___/| `   `   |/|"
    assert "‘/___/___/___/" not in rows[5]


def test_corridor_south_foreground_wall_and_room_floors_remain_unchanged() -> None:
    rows = render_irregular_room(cells_from_mask(CORRIDOR_MASK))
    assert rows[6] == "| |           ,— —,— —,— —,         | |"
    assert rows[7] == "|/| `   `    /|__/___/___/  `   `   |/|"
    assert rows[-1] == "‘/___/___/___/          ‘/___/___/___/"
