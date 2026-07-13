from pathlib import Path

from style_sample_system import Point
from terrain_cut_renderer_v2 import render_sunken_terrain


SURFACE_CELLS = frozenset(Point(x, y) for y in range(5) for x in range(7))
LOWER_CELLS = frozenset(
    {Point(x, y) for y in range(1, 4) for x in range(1, 4)}
    | {Point(x, 2) for x in range(4, 7)}
)
ELEVATIONS = {point: (0 if point in LOWER_CELLS else 1) for point in SURFACE_CELLS}
REJECTED = Path("style_samples/review/sunken-corridor-chamber-cliff-art-v2.txt")
ATTEMPT_2 = Path("style_samples/review/sunken-corridor-chamber-cliff-art-v2-attempt-2.txt")
EXPECTED_DRAFT = (
    "                    `   `",
    "      ,— — — — — —.",
    "     /|           |",
    "    ‘ |           | '— — — — —",
    "    |/| `   `   |/|",
    "    | |           | ,— — — — —",
    "    |/| `   `   |/|",
    "    | '— — — — — —'",
    "     ‘/___/___/___/",
    "                    `   `",
)


def _draft() -> tuple[str, ...]:
    return render_sunken_terrain(SURFACE_CELLS, ELEVATIONS, LOWER_CELLS)


def test_initial_terrain_cut_projection_stays_inside_surface_canvas() -> None:
    rows = _draft()
    assert len(rows) == 10
    assert max(map(len, rows)) <= 31


def test_both_planes_retain_logical_lattice_markers() -> None:
    rows = _draft()
    assert sum(row.count("`") for row in rows) == 6


def test_open_east_corridor_has_no_closing_face() -> None:
    rows = tuple(row.ljust(31) for row in _draft())
    for y in (3, 5):
        assert "|" not in rows[y][30:31]
        assert "/" not in rows[y][30:31]


def test_rejected_cliff_artwork_remains_archived() -> None:
    review_text = REJECTED.read_text(encoding="utf-8")
    assert "REJECTED" in review_text
    assert "Do not promote" in review_text


def test_attempt_2_is_exactly_locked_while_under_review() -> None:
    assert _draft() == EXPECTED_DRAFT
    review_text = ATTEMPT_2.read_text(encoding="utf-8")
    assert "\n".join(EXPECTED_DRAFT) in review_text
    assert "Manual artwork review required" in review_text
    assert "Do not promote without explicit approval" in review_text
