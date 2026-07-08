#!/usr/bin/env python3
"""Verification and sample output for the chunk-aware north wall renderer."""
from __future__ import annotations

from pathlib import Path

from modular_ascii_parts import (
    Opening,
    NorthWall,
    chunk_ruler,
    north_wall_top_width,
    north_wall_underside_width,
)

OUT_DIR = Path(__file__).resolve().parent

BASELINE_TOP = ",— -,— -,— -,— -,— -,— -,— -,— -."
BASELINE_UNDERSIDE = ",__/___/___/___/___/___/___/___/ |"


def assert_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}\nactual:   {actual!r}\nexpected: {expected!r}")


def assert_same_width(rows: list[str], expected_widths: tuple[int, int], label: str) -> None:
    widths = tuple(len(row) for row in rows)
    if widths != expected_widths:
        raise AssertionError(f"{label}: widths {widths!r} != {expected_widths!r}")


def assert_raises(exc_type: type[BaseException], fn, label: str) -> None:
    try:
        fn()
    except exc_type:
        return
    except Exception as exc:  # pragma: no cover - explicit diagnostic for script use
        raise AssertionError(f"{label}: raised {type(exc).__name__}, expected {exc_type.__name__}") from exc
    raise AssertionError(f"{label}: did not raise {exc_type.__name__}")


def render_case(title: str, wall: NorthWall) -> str:
    rows = wall.render()
    out = [title, chunk_ruler(wall.chunks), rows[0], rows[1]]
    return "\n".join(out)


def main() -> None:
    baseline = NorthWall(8).render()
    assert_equal(baseline, [BASELINE_TOP, BASELINE_UNDERSIDE], "solid 8-chunk north wall should match locked shell rows")
    expected_widths = (north_wall_top_width(8), north_wall_underside_width(8))
    assert_equal(expected_widths, (len(BASELINE_TOP), len(BASELINE_UNDERSIDE)), "formal width helpers should match locked baseline")

    # Edge/full-width openings are explicitly unsupported until their cap and
    # connector grammar are designed. This prevents the renderer from producing
    # plausible-looking but geometrically wrong rows.
    assert_raises(NotImplementedError, lambda: NorthWall(8, (Opening(1, 1),)), "west-edge opening rejected")
    assert_raises(NotImplementedError, lambda: NorthWall(8, (Opening(8, 1),)), "east-edge opening rejected")
    assert_raises(NotImplementedError, lambda: NorthWall(8, (Opening(1, 8),)), "full-wall opening rejected")
    assert_raises(NotImplementedError, lambda: NorthWall(8, (Opening(3, 2), Opening(6, 1))), "multiple openings rejected")
    assert_raises(ValueError, lambda: NorthWall(8, (Opening(0, 1),)), "zero start rejected")
    assert_raises(ValueError, lambda: NorthWall(8, (Opening(7, 3),)), "opening past end rejected")

    cases = [
        ("baseline: no opening", NorthWall(8)),
        ("2-chunk opening: chunks 4-5", NorthWall(8, (Opening(4, 2),))),
        ("3-chunk uneven opening: chunks 3-5", NorthWall(8, (Opening(3, 3),))),
        ("4-chunk centered opening: chunks 3-6", NorthWall(8, (Opening(3, 4),))),
        ("6-chunk wide interior opening: chunks 2-7", NorthWall(8, (Opening(2, 6),))),
    ]

    for title, wall in cases:
        assert_same_width(wall.render(), expected_widths, title)

    sample = "\n\n".join(render_case(title, wall) for title, wall in cases) + "\n"
    sample_path = OUT_DIR / "north_wall_opening_samples.txt"
    sample_path.write_text(sample, encoding="utf-8")

    print("PASS north wall chunk renderer")
    print(f"wrote {sample_path}")


if __name__ == "__main__":
    main()
