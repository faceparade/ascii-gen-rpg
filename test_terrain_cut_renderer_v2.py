from pathlib import Path

from style_sample_system import Point
from terrain_cut_renderer_v2 import mirror_cliff_art_horizontally, render_sunken_terrain


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
OUTSIDE_CORNER_TARGET = Path("style_samples/targets/sunken-outside-cliff-corner-v2.txt")
OUTSIDE_CORNER_CORRECTION = Path("style_samples/corrections/sunken-outside-cliff-corner-v2.txt")
MIRRORED_INSIDE_REVIEW = Path("style_samples/review/sunken-mirrored-inside-cliff-corner-v2.txt")
MIRRORED_INSIDE_TARGET = Path("style_samples/targets/sunken-mirrored-inside-cliff-corner-v2.txt")
MIRRORED_INSIDE_CORRECTION = Path("style_samples/corrections/sunken-mirrored-inside-cliff-corner-v2.txt")
MIRRORED_OUTSIDE_REVIEW = Path("style_samples/review/sunken-mirrored-outside-cliff-corner-v2.txt")
MIRRORED_OUTSIDE_TARGET = Path("style_samples/targets/sunken-mirrored-outside-cliff-corner-v2.txt")
MIRRORED_OUTSIDE_CORRECTION = Path("style_samples/corrections/sunken-mirrored-outside-cliff-corner-v2.txt")
OPEN_CORRIDOR_SHOULDER_REVIEW = Path("style_samples/review/sunken-open-corridor-shoulder-v2.txt")
OPEN_CORRIDOR_SHOULDER_TARGET = Path("style_samples/targets/sunken-open-corridor-shoulder-v2.txt")
OPEN_CORRIDOR_SHOULDER_CORRECTION = Path("style_samples/corrections/sunken-open-corridor-shoulder-v2.txt")
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
EXPECTED_OUTSIDE_CORNER = (
    "         ,— —,- -,— —,",
    "         |__/___/___/_",
    "         |",
    "         |",
    "—,— —,- -,",
    "/___/___/",
)
EXPECTED_MIRRORED_INSIDE_REVIEW = (
    ",— —,— —,— —,— —,      ",
    "|/ __/___/___/__|      ",
    "'—'— — — — —,   |      ",
    "            |/  |      ",
    "            | ‘ |      ",
    "            |/| |      ",
    "            | | |      ",
    "            |/| |      ",
    "            | | |      ",
    "            |/| |      ",
    "            '—'—'      ",
    "                       ",
)
EXPECTED_MIRRORED_OUTSIDE_REVIEW = (
    ",— —,- -,— —,         ",
    "_/___/___/__|         ",
    "            |         ",
    "            |         ",
    "            ,- -,— —,—",
    "             /___/___/",
)


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


def test_user_approved_outside_corner_matches_renderer_and_golden_target() -> None:
    surface = frozenset(Point(x, y) for y in range(5) for x in range(5))
    upper = frozenset(Point(x, y) for y in range(3) for x in range(2)) | frozenset(
        Point(x, 0) for x in range(2, 5)
    )
    lower = surface - upper
    elevations = {point: (1 if point in upper else 0) for point in surface}

    assert render_sunken_terrain(surface, elevations, lower) == EXPECTED_OUTSIDE_CORNER
    assert tuple(OUTSIDE_CORNER_TARGET.read_text(encoding="utf-8").splitlines()) == EXPECTED_OUTSIDE_CORNER
    assert OUTSIDE_CORNER_TARGET.read_bytes() == OUTSIDE_CORNER_CORRECTION.read_bytes()


def test_mirrored_inside_corner_review_preserves_the_approved_canvas() -> None:
    assert mirror_cliff_art_horizontally(EXPECTED_INSIDE_CORNER) == EXPECTED_MIRRORED_INSIDE_REVIEW
    assert tuple(MIRRORED_INSIDE_REVIEW.read_text(encoding="utf-8").splitlines()) == EXPECTED_MIRRORED_INSIDE_REVIEW
    assert len(EXPECTED_MIRRORED_INSIDE_REVIEW) == len(EXPECTED_INSIDE_CORNER)
    assert max(map(len, EXPECTED_MIRRORED_INSIDE_REVIEW)) == max(map(len, EXPECTED_INSIDE_CORNER))


def test_user_approved_mirrored_inside_corner_matches_renderer_and_golden_target() -> None:
    surface = frozenset(Point(x, y) for y in range(5) for x in range(5))
    lower = frozenset(
        {Point(x, 1) for x in range(4)}
        | {Point(3, y) for y in range(2, 5)}
    )
    elevations = {point: (0 if point in lower else 1) for point in surface}
    approved_text = MIRRORED_INSIDE_CORRECTION.read_text(encoding="utf-8")
    approved_rows = tuple(approved_text.split("\n"))

    assert render_sunken_terrain(surface, elevations, lower) == approved_rows
    assert MIRRORED_INSIDE_TARGET.read_bytes() == MIRRORED_INSIDE_CORRECTION.read_bytes()


def test_mirrored_outside_corner_review_preserves_latest_approved_canvas() -> None:
    assert mirror_cliff_art_horizontally(EXPECTED_OUTSIDE_CORNER) == EXPECTED_MIRRORED_OUTSIDE_REVIEW
    assert tuple(MIRRORED_OUTSIDE_REVIEW.read_text(encoding="utf-8").splitlines()) == EXPECTED_MIRRORED_OUTSIDE_REVIEW
    assert len(EXPECTED_MIRRORED_OUTSIDE_REVIEW) == len(EXPECTED_OUTSIDE_CORNER)
    assert max(map(len, EXPECTED_MIRRORED_OUTSIDE_REVIEW)) == max(map(len, EXPECTED_OUTSIDE_CORNER))


def test_user_approved_mirrored_outside_corner_matches_renderer_and_golden_target() -> None:
    surface = frozenset(Point(x, y) for y in range(5) for x in range(5))
    upper = frozenset(Point(x, y) for y in range(3) for x in range(3, 5)) | frozenset(
        Point(x, 0) for x in range(3)
    )
    lower = surface - upper
    elevations = {point: (1 if point in upper else 0) for point in surface}
    approved_rows = tuple(MIRRORED_OUTSIDE_CORRECTION.read_text(encoding="utf-8").splitlines())

    assert len(approved_rows) == 12
    assert {len(row) for row in approved_rows} == {22}
    assert render_sunken_terrain(surface, elevations, lower) == approved_rows
    assert MIRRORED_OUTSIDE_TARGET.read_bytes() == MIRRORED_OUTSIDE_CORRECTION.read_bytes()


def test_open_corridor_shoulder_review_starts_from_approved_cliff_vocabulary() -> None:
    draft = OPEN_CORRIDOR_SHOULDER_REVIEW.read_bytes()

    assert draft == TARGET.read_bytes()
    assert draft.endswith(b"\n")


def test_user_approved_open_corridor_shoulder_matches_renderer_and_golden_target() -> None:
    surface = frozenset(Point(x, y) for y in range(5) for x in range(7))
    lower = frozenset(
        {Point(x, y) for y in (1, 2) for x in range(1, 7)}
        | {Point(x, y) for y in (3, 4) for x in (1, 2)}
    )
    elevations = {point: (0 if point in lower else 1) for point in surface}
    approved_rows = tuple(OPEN_CORRIDOR_SHOULDER_CORRECTION.read_text(encoding="utf-8").splitlines())

    assert len(approved_rows) == 14
    assert {len(row) for row in approved_rows} == {18, 27, 30}
    assert render_sunken_terrain(surface, elevations, lower) == approved_rows
    assert OPEN_CORRIDOR_SHOULDER_TARGET.read_bytes() == OPEN_CORRIDOR_SHOULDER_CORRECTION.read_bytes()
