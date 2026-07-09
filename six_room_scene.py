#!/usr/bin/env python3
"""Six-room scene generator assembled from locked named fragments."""
from __future__ import annotations

from dataclasses import dataclass

from connector_specs import SceneFragmentSpec


@dataclass(frozen=True)
class SixRoomLayoutSpec:
    """Locked horizontal layout for the current three-room scene bands."""

    room_width: int = 34
    connector_width: int = 23
    room_count: int = 3

    @property
    def segment_widths(self) -> tuple[int, int, int, int, int]:
        return (
            self.room_width,
            self.connector_width,
            self.room_width,
            self.connector_width,
            self.room_width,
        )

    @property
    def row_width(self) -> int:
        return sum(self.segment_widths)


ROOM_BOTTOM_RAIL = tuple(SceneFragmentSpec.room_bottom_rail_34().render())
ROOM_TOP_BAND = tuple(SceneFragmentSpec.room_top_band_34().render())
ROOM_FLOOR_BAND = tuple(SceneFragmentSpec.room_floor_band_34().render())
MIDDLE_SEAM_CONNECTOR_GAP = tuple(SceneFragmentSpec.middle_seam_connector_gap_80().render())
LOWER_BAND_LEFT_ROOM_STRIP = tuple(SceneFragmentSpec.lower_band_left_room_strip_34().render())
LOWER_BAND_GAP_STRIP = tuple(SceneFragmentSpec.lower_band_gap_strip_23().render())
LOWER_BAND_MIDDLE_ROOM_STRIP = tuple(SceneFragmentSpec.lower_band_middle_room_strip_34().render())
LOWER_BAND_RIGHT_ROOM_STRIP = tuple(SceneFragmentSpec.lower_band_right_room_strip_34().render())
UPPER_BAND_LEFT_ROOM_STRIP = tuple(SceneFragmentSpec.upper_band_left_room_strip_34().render())
UPPER_BAND_GAP_STRIP = tuple(SceneFragmentSpec.upper_band_gap_strip_23().render())
UPPER_BAND_MIDDLE_ROOM_STRIP = tuple(SceneFragmentSpec.upper_band_middle_room_strip_34().render())
UPPER_BAND_RIGHT_ROOM_STRIP = tuple(SceneFragmentSpec.upper_band_right_room_strip_34().render())
SCENE_TOP_ROWS = tuple(SceneFragmentSpec.scene_top_rows_1_4().render())
SCENE_MID_CONNECTOR_ROWS = tuple(SceneFragmentSpec.scene_mid_connector_rows_14_17().render())
SCENE_LOWER_CONNECTOR_ROWS = tuple(SceneFragmentSpec.scene_lower_connector_rows_20_22().render())


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


def assemble_lower_band_rows() -> list[str]:
    """Rebuild source lines 23–29 from named lower-band strips."""
    return [
        left + gap + middle + gap + right
        for left, gap, middle, right in zip(
            LOWER_BAND_LEFT_ROOM_STRIP,
            LOWER_BAND_GAP_STRIP,
            LOWER_BAND_MIDDLE_ROOM_STRIP,
            LOWER_BAND_RIGHT_ROOM_STRIP,
            strict=True,
        )
    ]


def assemble_upper_band_rows() -> list[str]:
    """Rebuild source lines 5–13 from named upper-band strips."""
    return [
        left + gap + middle + gap + right
        for left, gap, middle, right in zip(
            UPPER_BAND_LEFT_ROOM_STRIP,
            UPPER_BAND_GAP_STRIP,
            UPPER_BAND_MIDDLE_ROOM_STRIP,
            UPPER_BAND_RIGHT_ROOM_STRIP,
            strict=True,
        )
    ]


def assemble_six_room_scene_rows() -> list[str]:
    """Rebuild the locked six-room source from named scene regions."""
    return [
        *SCENE_TOP_ROWS,
        *assemble_upper_band_rows(),
        *SCENE_MID_CONNECTOR_ROWS,
        *assemble_middle_seam_rows(),
        *SCENE_LOWER_CONNECTOR_ROWS,
        *assemble_lower_band_rows(),
    ]
