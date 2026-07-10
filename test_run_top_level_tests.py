#!/usr/bin/env python3
"""Tests for top-level test discovery."""
from __future__ import annotations

from run_top_level_tests import TESTS


def test_discovery_only_includes_test_filename_conventions() -> None:
    names = [path.name for path in TESTS]
    assert "latest_r24_style.py" not in names
    assert all(
        name.startswith("test_") or name.endswith("_test.py") or name.endswith("_tests.py")
        for name in names
    )


def test_discovery_deduplicates_files_matching_multiple_patterns() -> None:
    assert len(TESTS) == len(set(TESTS))


if __name__ == "__main__":
    test_discovery_only_includes_test_filename_conventions()
    test_discovery_deduplicates_files_matching_multiple_patterns()
    print("PASS top-level test discovery")
