#!/usr/bin/env python3
"""Current scene source-of-truth helpers.

``six_rooms_two_platforms.txt`` remains the byte-for-byte review reference. The
runtime compatibility scene is now assembled from named locked regions so drift
is caught in presets/tests instead of silently reading the art file.
"""
from __future__ import annotations

from pathlib import Path

from six_room_scene import assemble_six_room_scene_rows

SOURCE_OF_TRUTH_PATH = Path(__file__).resolve().parent / "six_rooms_two_platforms.txt"
# Backwards-compatible name for tests/callers that still import TEMPLATE_PATH.
TEMPLATE_PATH = SOURCE_OF_TRUTH_PATH


def latest_reference_lines(path: Path = TEMPLATE_PATH) -> list[str]:
    """Return the active ASCII scene review reference from disk."""
    return path.read_text(encoding="utf-8").splitlines()


def six_room_source_lines(path: Path = SOURCE_OF_TRUTH_PATH) -> list[str]:
    """Return ``six_rooms_two_platforms.txt`` byte-for-byte as review rows."""
    return path.read_text(encoding="utf-8").splitlines()


def r24_new_style_with_room3_platform() -> list[str]:
    """Assemble the active six-room raised-floor scene from named regions."""
    return assemble_six_room_scene_rows()
