#!/usr/bin/env python3
"""Tests for independent six-room structural alignment checks."""
from __future__ import annotations

from scene_alignment import (
    assert_scene_alignment,
    load_scene_lines,
)


def _replace_char(row: str, column: int, char: str) -> str:
    """Return row with 1-based column replaced by char."""
    index = column - 1
    if index >= len(row):
        row = row.ljust(index + 1)
    return row[:index] + char + row[index + 1:]


def test_current_scene_alignment() -> None:
    assert_scene_alignment()
    print("PASS current six-room scene structural alignment")


def _assert_alignment_failure(lines: list[str], *expected_fragments: str) -> None:
    """Assert that edited scene lines fail alignment with expected message text."""
    try:
        assert_scene_alignment(lines)
    except AssertionError as exc:
        message = str(exc)
        missing = [fragment for fragment in expected_fragments if fragment not in message]
        if missing:
            raise AssertionError(
                "alignment failure missed expected report text "
                f"{missing!r}; got:\n{message}"
            )
    else:
        raise AssertionError("structural alignment unexpectedly passed edited scene lines")


def test_alignment_catches_line15_backtick_moved_to_line16() -> None:
    lines = load_scene_lines()
    bad = list(lines)

    # Recreate the exact class of error that slipped through: the fragment's
    # top-left grid backtick is removed from line 15 and appears one row lower.
    # Coordinates are 1-based.  The corrected top-rim backtick is line 15 col 81
    # in Python's text-coordinate convention, even though it may be counted as
    # col 82 by a visual editor depending on the chosen origin/gutter.
    bad[15 - 1] = _replace_char(bad[15 - 1], 81, " ")
    bad[16 - 1] = _replace_char(bad[16 - 1], 81, "`")

    _assert_alignment_failure(bad, "backtick grid drift", "line 15", "line 16")
    print("PASS structural alignment catches line-15/line-16 backtick drift")


def test_alignment_catches_source_width_drift() -> None:
    lines = load_scene_lines()
    bad = list(lines)

    # The six-room source is intentionally ragged. Accidental padding should be
    # reported directly instead of only surfacing through downstream slices.
    bad[14 - 1] = bad[14 - 1] + " "

    _assert_alignment_failure(
        bad,
        "source line width drift",
        "line 14",
        "expected width 92, got 93",
    )
    print("PASS structural alignment catches source line-width drift")


def test_alignment_catches_center_decorated_floor_detail_drift() -> None:
    lines = load_scene_lines()
    bad = list(lines)

    # The ;.; detail is part of the 29-column decorated center connector slice
    # at line 23/column 61. Mutating it should report that named slice, not pass
    # just because row widths and the backtick grid are still unchanged.
    bad[27 - 1] = _replace_char(bad[27 - 1], 71, ":")

    _assert_alignment_failure(
        bad,
        "slice drift in center decorated raised connector fragment",
        "line 27",
    )
    print("PASS structural alignment catches center decorated ;.; drift")


def test_alignment_catches_room_bottom_rail_drift() -> None:
    lines = load_scene_lines()
    bad = list(lines)

    # Change the lower-middle rail's closing apostrophe while preserving row
    # length and all backticks. The generic room-bottom-rail anchor should catch
    # this exact visual drift.
    bad[29 - 1] = _replace_char(bad[29 - 1], 91, "’")

    _assert_alignment_failure(
        bad,
        "slice drift in lower-middle room bottom rail",
        "line 29",
    )
    print("PASS structural alignment catches room bottom rail drift")


def test_alignment_catches_room_top_band_drift() -> None:
    lines = load_scene_lines()
    bad = list(lines)

    # Mutate one glyph in the repeated middle-left top/opening band while
    # preserving width and the backtick grid. The named seam anchor should report
    # this as a slice drift.
    bad[18 - 1] = _replace_char(bad[18 - 1], 6, "-")

    _assert_alignment_failure(
        bad,
        "slice drift in middle-left room top band",
        "line 18",
    )
    print("PASS structural alignment catches room top-band drift")


def test_alignment_catches_middle_seam_connector_gap_drift() -> None:
    lines = load_scene_lines()
    bad = list(lines)

    # Change the connector interruption between the left/right 34-wide seam
    # bands without changing row width. The named 80-column gap should catch it.
    bad[19 - 1] = _replace_char(bad[19 - 1], 83, "/")

    _assert_alignment_failure(
        bad,
        "slice drift in middle seam connector gap",
        "line 19",
    )
    print("PASS structural alignment catches middle seam connector-gap drift")


def test_alignment_catches_lower_band_gap_strip_drift() -> None:
    lines = load_scene_lines()
    bad = list(lines)

    # Mutate the repeated 23-column lower inter-room strip while preserving all
    # row widths. The lower-band strip anchor should identify the gap drift.
    bad[25 - 1] = _replace_char(bad[25 - 1], 44, "-")

    _assert_alignment_failure(
        bad,
        "slice drift in lower-band inter-room gap strip",
        "line 25",
    )
    print("PASS structural alignment catches lower-band gap-strip drift")


def test_alignment_catches_upper_band_gap_strip_drift() -> None:
    lines = load_scene_lines()
    bad = list(lines)

    # Mutate the repeated 23-column upper inter-room strip while preserving all
    # row widths. The upper-band strip anchor should identify the gap drift.
    bad[6 - 1] = _replace_char(bad[6 - 1], 44, "-")

    _assert_alignment_failure(
        bad,
        "slice drift in upper-band inter-room gap strip",
        "line 6",
    )
    print("PASS structural alignment catches upper-band gap-strip drift")


def main() -> None:
    test_current_scene_alignment()
    test_alignment_catches_line15_backtick_moved_to_line16()
    test_alignment_catches_source_width_drift()
    test_alignment_catches_center_decorated_floor_detail_drift()
    test_alignment_catches_room_bottom_rail_drift()
    test_alignment_catches_room_top_band_drift()
    test_alignment_catches_middle_seam_connector_gap_drift()
    test_alignment_catches_lower_band_gap_strip_drift()
    test_alignment_catches_upper_band_gap_strip_drift()
    print("ALL scene alignment tests passed")


if __name__ == "__main__":
    main()
