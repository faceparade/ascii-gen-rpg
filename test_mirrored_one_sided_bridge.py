from irregular_room_grammar import (
    courtyard_bridge_runs,
    mirrored_one_sided_bridge_runs,
    one_sided_bridge_runs,
)
from style_sample_system import Point, cells_from_mask, lattice_points, render_irregular_room


MIRRORED_MASK = ("....##", "....##", "######")
APPROVED_TARGET = (
    "                  ,— —,— —,",
    "                 /|__/___/|",
    "                ‘ |     | |",
    "                |/| `   |/|",
    "  ,— —,— —,— —,—‘—,     | |",
    " /|__/___/___/___/  `   |/|",
    "‘ ,— —,— —,— —,— —,— —,—‘—,",
    "‘/___/___/___/___/___/___/",
)


def test_mirrored_one_sided_bridge_topology_is_stable() -> None:
    cells = cells_from_mask(MIRRORED_MASK)
    assert lattice_points(cells) == frozenset({Point(20, 3), Point(20, 5)})


def test_mirrored_bridge_uses_only_its_specific_resolver() -> None:
    cells = cells_from_mask(MIRRORED_MASK)
    assert courtyard_bridge_runs(cells) == ()
    assert one_sided_bridge_runs(cells) == ()
    assert mirrored_one_sided_bridge_runs(cells) == ((2, 0, 3),)


def test_mirrored_bridge_retains_exterior_west_start() -> None:
    rows = render_irregular_room(cells_from_mask(MIRRORED_MASK))
    assert rows[4].startswith("  ,— —")
    assert rows[5].startswith(" /|__")
    assert rows[4][16:19] == "‘—,"


def test_mirrored_bridge_matches_approved_target_exactly() -> None:
    assert render_irregular_room(cells_from_mask(MIRRORED_MASK)) == APPROVED_TARGET
