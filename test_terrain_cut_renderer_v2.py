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
TARGET = Path("style_samples/targets/sunken-corridor-chamber-cliff-art-v2.txt")
EXPECTED_DRAFT = (
    "  ,— —,— —,— —,— —,— —,— —,— —,",
    "  |__/___/___/___/___/___/__ /|",
    "  |   ,— — — — — —.         | |",
    "  |  /|           | `   `   |/|",
    "  | ‘ |           '— — — — —'—'",
    "  | |/|",
    "  | | |           ,— —,— —,— —,",
    "  | |/|           |__/___/__ /|",
    "  | | ,— —,— —,— —,         | |",
    "  | ‘/___/___/___/  `   `   |/|",
    "  '— — — — — — — — — — — — — —'",
)


def _draft() -> tuple[str, ...]:
    return render_sunken_terrain(SURFACE_CELLS, ELEVATIONS, LOWER_CELLS)


def test_approved_projection_has_expected_bounds() -> None:
    rows = _draft()
    assert len(rows) == 11
    assert max(map(len, rows)) == 31


def test_projection_contains_upper_and_lower_lattice_markers() -> None:
    rows = _draft()
    assert sum(row.count("`") for row in rows) == 4


def test_rejected_cliff_artwork_remains_archived() -> None:
    review_text = REJECTED.read_text(encoding="utf-8")
    assert "REJECTED" in review_text
    assert "Do not promote" in review_text


def test_approved_cliff_artwork_matches_golden_target() -> None:
    assert _draft() == EXPECTED_DRAFT
    assert tuple(TARGET.read_text(encoding="utf-8").splitlines()) == EXPECTED_DRAFT
