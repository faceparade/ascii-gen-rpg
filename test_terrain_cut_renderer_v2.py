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
LATEST_APPROVED_CORRECTION = Path("style_samples/corrections/sunken-corridor-chamber-cliff-art-v2.txt")
INSIDE_CORNER_TARGET = Path("style_samples/targets/sunken-inside-cliff-corner-v2.txt")
EXPECTED_DRAFT = (
    "      ,— —,— —,— —,— —,",
    "      |__/___/___/__ /|",
    "      |   ,— — — — —'—'",
    "      |  /|           ",
    "      | ‘ |",
    "      | |/|",
    "      | | |",
    "      | |/|",
    "      | | |",
    "      | |/|",
    "      '—'—'",
    "    ",
)
EXPECTED_INSIDE_CORNER = EXPECTED_DRAFT


def _draft() -> tuple[str, ...]:
    return render_sunken_terrain(SURFACE_CELLS, ELEVATIONS, LOWER_CELLS)


def test_approved_projection_has_expected_bounds() -> None:
    rows = _draft()
    assert len(rows) == 12
    assert max(map(len, rows)) == 23


def test_projection_contains_submitted_inside_corner_join() -> None:
    rows = _draft()
    assert rows[2].endswith("'—'")
    assert rows[10].endswith("'—'—'")


def test_rejected_cliff_artwork_remains_archived() -> None:
    review_text = REJECTED.read_text(encoding="utf-8")
    assert "REJECTED" in review_text
    assert "Do not promote" in review_text


def test_approved_cliff_artwork_matches_golden_target() -> None:
    assert _draft() == EXPECTED_DRAFT
    assert tuple(TARGET.read_text(encoding="utf-8").splitlines()) == EXPECTED_DRAFT


def test_canonical_cliff_target_reflects_latest_approved_update() -> None:
    assert TARGET.read_bytes() == LATEST_APPROVED_CORRECTION.read_bytes()


def test_user_approved_inside_corner_matches_golden_target() -> None:
    surface = frozenset(Point(x, y) for y in range(5) for x in range(5))
    lower = frozenset(
        {Point(x, 1) for x in range(1, 5)}
        | {Point(1, y) for y in range(2, 5)}
    )
    elevations = {point: (0 if point in lower else 1) for point in surface}

    assert render_sunken_terrain(surface, elevations, lower) == EXPECTED_INSIDE_CORNER
    assert tuple(INSIDE_CORNER_TARGET.read_text(encoding="utf-8").splitlines()) == EXPECTED_INSIDE_CORNER
