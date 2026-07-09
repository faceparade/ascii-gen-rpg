#!/usr/bin/env python3
"""Structural alignment checks for ``six_rooms_two_platforms.txt``.

These checks are intentionally independent of the source-vs-generated-artifact
byte comparison.  They lock named visual anchors, especially the backtick grid,
so a glyph on the correct column but the wrong row is reported as structural
alignment drift instead of being hidden by source-as-truth comparisons.

Coordinate convention in this file is human-readable 1-based ``(line, column)``.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from connector_specs import RaisedFragmentSpec, SceneFragmentSpec
from curved_dungeon_grammar import raised_floor_section_tall_narrow, raised_platform

ROOT = Path(__file__).resolve().parent
SOURCE_PATH = ROOT / "six_rooms_two_platforms.txt"

# Preserve the source's intentionally ragged scene shape.  This catches accidental
# row padding/truncation separately from glyph-level slice checks.
EXPECTED_LINE_WIDTHS: tuple[int, ...] = (
    0,
    148,
    148,
    148,
    148,
    148,
    148,
    148,
    148,
    148,
    148,
    148,
    148,
    92,
    96,
    122,
    149,
    149,
    148,
    148,
    148,
    148,
    148,
    148,
    148,
    148,
    148,
    148,
    148,
)

# Full locked snapshot of the invisible/reference backtick grid.  This is the
# check that catches a backtick moved from line 15 to line 16 even if all row
# lengths and generated artifacts still match.
EXPECTED_BACKTICKS_BY_LINE: dict[int, tuple[int, ...]] = {
    5: (4, 8, 12, 16, 20, 24, 28, 61, 65, 69, 73, 77, 81, 85, 118, 142),
    7: (4, 8, 12, 16, 20, 24, 28, 61, 65, 69, 73, 77, 81, 85, 142),
    9: (4, 8, 12, 16, 20, 24, 28, 32, 61, 65, 69, 73, 77, 81, 85, 89, 142),
    11: (4, 8, 12, 16, 20, 24, 28, 61, 65, 69, 73, 77, 81, 85, 142),
    13: (1, 61, 65, 69, 73, 77, 81, 85, 115),
    15: (58, 81),
    21: (4, 8, 12, 16, 20, 24, 28, 61, 65, 69, 73, 77, 81, 85, 118, 126, 130, 134, 138, 142),
    23: (4, 8, 12, 16, 20, 24, 28, 61, 85, 126, 130, 134, 138, 142),
    25: (4, 8, 12, 16, 20, 24, 28, 32, 85, 89, 126, 130, 134, 138, 142),
    27: (4, 8, 12, 16, 20, 24, 28, 85, 126, 130, 134, 138, 142),
    29: (1, 58, 115),
}

# Top-rim starts for raised/raised-like structures.  The line-15 entry is the
# fragment that previously had its backtick one row too low.
EXPECTED_RAISED_TOP_STARTS: tuple[tuple[int, int], ...] = (
    (5, 118),
    (9, 32),
    (9, 89),
    (15, 81),
    (21, 118),
    (23, 61),
    (25, 32),
    (25, 89),
)


@dataclass(frozen=True)
class SliceSpec:
    name: str
    line: int
    column: int
    rows: tuple[str, ...]


FULL_RAISED_SECTION = tuple(raised_platform(4))
TALL_NARROW_SECTION = tuple(raised_floor_section_tall_narrow())
LINE15_RAISED_FRAGMENT = tuple(RaisedFragmentSpec.connector_line15_short().render())
WIDENED_RAISED_FRAGMENT = tuple(RaisedFragmentSpec.widened_27_partial().render())
CENTER_DECORATED_FRAGMENT = tuple(RaisedFragmentSpec.center_decorated_29().render())
ROOM_BOTTOM_RAIL = tuple(SceneFragmentSpec.room_bottom_rail_34().render())
ROOM_TOP_BAND = tuple(SceneFragmentSpec.room_top_band_34().render())
ROOM_FLOOR_BAND = tuple(SceneFragmentSpec.room_floor_band_34().render())
MIDDLE_SEAM_CONNECTOR_GAP = tuple(SceneFragmentSpec.middle_seam_connector_gap_80().render())


def assemble_middle_seam_rows() -> list[str]:
    """Rebuild source lines 18–19 from named scene fragments.

    The row-18 trailing space is intentional: line 18 is 149 columns while line
    19 is 148. Keep that ragged edge explicit instead of padding every row.
    """
    top_gap, floor_gap = MIDDLE_SEAM_CONNECTOR_GAP
    top = ROOM_TOP_BAND[0]
    floor = ROOM_FLOOR_BAND[0]
    return [
        top + top_gap + top + " ",
        floor + floor_gap + floor,
    ]

SLICE_SPECS: tuple[SliceSpec, ...] = (
    SliceSpec(
        name="upper-right full raised floor section",
        line=5,
        column=118,
        rows=FULL_RAISED_SECTION,
    ),
    SliceSpec(
        name="line-15 connector raised fragment with corrected backtick",
        line=15,
        column=81,
        rows=LINE15_RAISED_FRAGMENT,
    ),
    SliceSpec(
        name="lower-right tall/narrow raised floor section",
        line=21,
        column=118,
        rows=TALL_NARROW_SECTION,
    ),
    SliceSpec(
        name="center decorated raised connector fragment",
        line=23,
        column=61,
        rows=CENTER_DECORATED_FRAGMENT,
    ),
    SliceSpec(
        name="upper-left widened raised fragment",
        line=9,
        column=32,
        rows=WIDENED_RAISED_FRAGMENT,
    ),
    SliceSpec(
        name="upper-middle widened raised fragment",
        line=9,
        column=89,
        rows=WIDENED_RAISED_FRAGMENT,
    ),
    SliceSpec(
        name="lower-left widened raised fragment",
        line=25,
        column=32,
        rows=WIDENED_RAISED_FRAGMENT,
    ),
    SliceSpec(
        name="lower-middle widened raised fragment",
        line=25,
        column=89,
        rows=WIDENED_RAISED_FRAGMENT,
    ),
    SliceSpec(
        name="upper-left room bottom rail",
        line=13,
        column=1,
        rows=ROOM_BOTTOM_RAIL,
    ),
    SliceSpec(
        name="lower-left room bottom rail",
        line=29,
        column=1,
        rows=ROOM_BOTTOM_RAIL,
    ),
    SliceSpec(
        name="lower-middle room bottom rail",
        line=29,
        column=58,
        rows=ROOM_BOTTOM_RAIL,
    ),
    SliceSpec(
        name="lower-right room bottom rail",
        line=29,
        column=115,
        rows=ROOM_BOTTOM_RAIL,
    ),
    SliceSpec(
        name="middle-left room top band",
        line=18,
        column=1,
        rows=ROOM_TOP_BAND,
    ),
    SliceSpec(
        name="middle-right room top band",
        line=18,
        column=115,
        rows=ROOM_TOP_BAND,
    ),
    SliceSpec(
        name="middle-left room floor band",
        line=19,
        column=1,
        rows=ROOM_FLOOR_BAND,
    ),
    SliceSpec(
        name="middle-right room floor band",
        line=19,
        column=115,
        rows=ROOM_FLOOR_BAND,
    ),
    SliceSpec(
        name="middle seam connector gap",
        line=18,
        column=35,
        rows=MIDDLE_SEAM_CONNECTOR_GAP,
    ),
)


def load_scene_lines(path: Path = SOURCE_PATH) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def backticks_by_line(lines: list[str]) -> dict[int, tuple[int, ...]]:
    return {
        line_no: tuple(index + 1 for index, ch in enumerate(row) if ch == "`")
        for line_no, row in enumerate(lines, start=1)
        if "`" in row
    }


def raised_top_starts(lines: list[str]) -> tuple[tuple[int, int], ...]:
    starts: list[tuple[int, int]] = []
    for line_no, row in enumerate(lines, start=1):
        start = 0
        while True:
            index = row.find("` ,—", start)
            if index == -1:
                break
            starts.append((line_no, index + 1))
            start = index + 1
    return tuple(starts)


def _extract_slice(lines: list[str], line: int, column: int, width: int, height: int) -> list[str]:
    y0 = line - 1
    x0 = column - 1
    extracted: list[str] = []
    for dy in range(height):
        y = y0 + dy
        if y >= len(lines):
            extracted.append("<missing line>")
            continue
        extracted.append(lines[y][x0:x0 + width])
    return extracted


def collect_alignment_issues(lines: list[str]) -> list[str]:
    issues: list[str] = []

    actual_widths = tuple(len(row) for row in lines)
    if actual_widths != EXPECTED_LINE_WIDTHS:
        max_len = max(len(actual_widths), len(EXPECTED_LINE_WIDTHS))
        mismatches = []
        for index in range(max_len):
            line_no = index + 1
            expected = EXPECTED_LINE_WIDTHS[index] if index < len(EXPECTED_LINE_WIDTHS) else "<missing>"
            actual = actual_widths[index] if index < len(actual_widths) else "<missing>"
            if expected != actual:
                mismatches.append(f"  line {line_no}: expected width {expected}, got {actual}")
        issues.append("source line width drift:\n" + "\n".join(mismatches))

    actual_backticks = backticks_by_line(lines)
    if actual_backticks != EXPECTED_BACKTICKS_BY_LINE:
        all_lines = sorted(set(actual_backticks) | set(EXPECTED_BACKTICKS_BY_LINE))
        mismatches = [
            f"  line {line_no}: expected {EXPECTED_BACKTICKS_BY_LINE.get(line_no, ())}, got {actual_backticks.get(line_no, ())}"
            for line_no in all_lines
            if actual_backticks.get(line_no, ()) != EXPECTED_BACKTICKS_BY_LINE.get(line_no, ())
        ]
        issues.append("backtick grid drift:\n" + "\n".join(mismatches))

    actual_top_starts = raised_top_starts(lines)
    if actual_top_starts != EXPECTED_RAISED_TOP_STARTS:
        issues.append(
            "raised top-rim start drift:\n"
            f"  expected {EXPECTED_RAISED_TOP_STARTS}\n"
            f"  got      {actual_top_starts}"
        )

    for spec in SLICE_SPECS:
        width = max(len(row) for row in spec.rows)
        expected = [row.ljust(width) for row in spec.rows]
        actual = _extract_slice(lines, spec.line, spec.column, width, len(spec.rows))
        if actual != expected:
            detail = [f"slice drift in {spec.name} at line {spec.line}, column {spec.column}:"]
            for offset, (got, want) in enumerate(zip(actual, expected), start=0):
                if got != want:
                    detail.append(
                        f"  line {spec.line + offset}: expected {want!r}, got {got!r}"
                    )
            issues.append("\n".join(detail))

    return issues


def assert_scene_alignment(lines: list[str] | None = None) -> None:
    scene_lines = load_scene_lines() if lines is None else lines
    issues = collect_alignment_issues(scene_lines)
    if issues:
        raise AssertionError("six-room scene structural alignment failed:\n" + "\n\n".join(issues))


def main() -> None:
    assert_scene_alignment()
    print("PASS six-room scene structural alignment")


if __name__ == "__main__":
    main()
