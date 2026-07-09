#!/usr/bin/env python3
"""Current scene source-of-truth loader.

``six_rooms_two_platforms.txt`` is now the reference art to sample/review
against.  Older chat-derived templates remain in the repo only as historical
artifacts; new comparison/generation paths should load this file.
"""
from __future__ import annotations

from pathlib import Path

SOURCE_OF_TRUTH_PATH = Path(__file__).resolve().parent / "six_rooms_two_platforms.txt"
# Backwards-compatible name for tests/callers that still import TEMPLATE_PATH.
TEMPLATE_PATH = SOURCE_OF_TRUTH_PATH


def latest_reference_lines(path: Path = TEMPLATE_PATH) -> list[str]:
    """Return the active ASCII scene source of truth."""
    return path.read_text(encoding="utf-8").splitlines()


def six_room_source_lines(path: Path = SOURCE_OF_TRUTH_PATH) -> list[str]:
    """Return ``six_rooms_two_platforms.txt`` byte-for-byte as scene rows."""
    return path.read_text(encoding="utf-8").splitlines()


def r24_new_style_with_room3_platform() -> list[str]:
    """Compatibility wrapper for the active six-room raised-floor reference."""
    return six_room_source_lines()
