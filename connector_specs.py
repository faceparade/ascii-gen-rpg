#!/usr/bin/env python3
"""Reusable connector placement specs for the ASCII dungeon grammar.

These are small data/geometry helpers: they map room-local connector choices
(chunk openings, room origin, optional visible upper fragments) into global
canvas regions, and expose locked stamps/templates through named specs when a
fragment has not been fully parameterized yet.
"""
from __future__ import annotations

from dataclasses import dataclass

from modular_ascii_parts import CHUNK_GLYPH_W, Opening, NorthWall, north_wall_underside_width


@dataclass(frozen=True)
class SouthOpeningTemplateSpec:
    """Locked visible south-opening starter for a room north of a target room.

    The rows are stored as ``(room_local_x, row_text)`` pairs because this
    fragment is aligned to the target room's north wall but visually belongs to
    the room/connector immediately above it. It is intentionally a locked
    template first: parameterization can happen after more hand-drawn variants
    are proven byte-for-byte.
    """

    name: str
    rows: tuple[tuple[int, str], ...]

    @classmethod
    def compact_r24(cls) -> "SouthOpeningTemplateSpec":
        """Return the current locked compact R24 upper/south-opening fragment."""
        from presets import build_south_opening_template

        return cls("compact_r24", build_south_opening_template("compact_r24"))

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def min_room_local_x(self) -> int:
        if not self.rows:
            return 0
        return min(dx for dx, _ in self.rows)

    @property
    def max_room_local_x(self) -> int:
        if not self.rows:
            return 0
        return max(dx + len(row) for dx, row in self.rows)

    @property
    def width(self) -> int:
        return self.max_room_local_x - self.min_room_local_x

    def origin_from_room(self, room_x: int, room_y: int) -> tuple[int, int]:
        """Resolve the bounding-box origin for the upper fragment."""
        return (room_x + self.min_room_local_x, room_y - self.height)

    def region_from_room(self, room_x: int, room_y: int) -> tuple[int, int, int, int]:
        """Return global ``(x, y, width, height)`` for the fragment bbox."""
        x, y = self.origin_from_room(room_x, room_y)
        return (x, y, self.width, self.height)

    def rows_for_room(self, room_x: int, room_y: int) -> tuple[tuple[int, int, str], ...]:
        """Return rows as global ``(x, y, row_text)`` triples."""
        top_y = room_y - self.height
        return tuple((room_x + dx, top_y + dy, row) for dy, (dx, row) in enumerate(self.rows))


@dataclass(frozen=True)
class RaisedFragmentSpec:
    """Named locked raised-floor / raised-edge fragment.

    These fragments are smaller than a full room module but structurally
    important: their leading backticks and left-face rows define the invisible
    grid alignment of the six-room source. They are kept as data-backed specs
    until a broader raised-fragment grammar is proven byte-for-byte.
    """

    name: str
    rows: tuple[str, ...]

    @classmethod
    def from_preset(cls, name: str) -> "RaisedFragmentSpec":
        """Return a named locked raised fragment from ``presets``."""
        from presets import build_raised_fragment

        return cls(name, build_raised_fragment(name))

    @classmethod
    def connector_line15_short(cls) -> "RaisedFragmentSpec":
        """Return the corrected line-15 connector raised fragment."""
        return cls.from_preset("connector_line15_short")

    @classmethod
    def widened_27_partial(cls) -> "RaisedFragmentSpec":
        """Return the four-row widened 27-column raised-edge fragment."""
        return cls.from_preset("widened_27_partial")

    @classmethod
    def center_decorated_29(cls) -> "RaisedFragmentSpec":
        """Return the decorated 29-column center raised connector fragment."""
        return cls.from_preset("center_decorated_29")

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def width(self) -> int:
        return max((len(row) for row in self.rows), default=0)

    def render(self) -> list[str]:
        """Return the locked fragment rows."""
        return list(self.rows)


@dataclass(frozen=True)
class SceneFragmentSpec:
    """Named locked generic source-scene fragment.

    Use this for structural source anchors that are not connector placements or
    raised-floor subparts but still need byte-exact row/column verification.
    """

    name: str
    rows: tuple[str, ...]

    @classmethod
    def from_preset(cls, name: str) -> "SceneFragmentSpec":
        """Return a named locked generic scene fragment from ``presets``."""
        from presets import build_scene_fragment

        return cls(name, build_scene_fragment(name))

    @classmethod
    def room_bottom_rail_34(cls) -> "SceneFragmentSpec":
        """Return the repeated 34-column room bottom rail fragment."""
        return cls.from_preset("room_bottom_rail_34")

    @classmethod
    def room_top_band_34(cls) -> "SceneFragmentSpec":
        """Return the repeated 34-column room top/opening band fragment."""
        return cls.from_preset("room_top_band_34")

    @classmethod
    def room_floor_band_34(cls) -> "SceneFragmentSpec":
        """Return the repeated 34-column room floor/underside band fragment."""
        return cls.from_preset("room_floor_band_34")

    @classmethod
    def middle_seam_connector_gap_80(cls) -> "SceneFragmentSpec":
        """Return the 80-column connector interruption in the middle seam."""
        return cls.from_preset("middle_seam_connector_gap_80")

    @classmethod
    def lower_band_left_room_strip_34(cls) -> "SceneFragmentSpec":
        """Return the 34-column lower-band left room strip."""
        return cls.from_preset("lower_band_left_room_strip_34")

    @classmethod
    def lower_band_gap_strip_23(cls) -> "SceneFragmentSpec":
        """Return the repeated 23-column lower-band inter-room gap strip."""
        return cls.from_preset("lower_band_gap_strip_23")

    @classmethod
    def lower_band_middle_room_strip_34(cls) -> "SceneFragmentSpec":
        """Return the 34-column lower-band middle room strip."""
        return cls.from_preset("lower_band_middle_room_strip_34")

    @classmethod
    def lower_band_right_room_strip_34(cls) -> "SceneFragmentSpec":
        """Return the 34-column lower-band right room strip."""
        return cls.from_preset("lower_band_right_room_strip_34")

    @classmethod
    def upper_band_left_room_strip_34(cls) -> "SceneFragmentSpec":
        """Return the 34-column upper-band left room strip."""
        return cls.from_preset("upper_band_left_room_strip_34")

    @classmethod
    def upper_band_gap_strip_23(cls) -> "SceneFragmentSpec":
        """Return the repeated 23-column upper-band inter-room gap strip."""
        return cls.from_preset("upper_band_gap_strip_23")

    @classmethod
    def upper_band_middle_room_strip_34(cls) -> "SceneFragmentSpec":
        """Return the 34-column upper-band middle room strip."""
        return cls.from_preset("upper_band_middle_room_strip_34")

    @classmethod
    def upper_band_right_room_strip_34(cls) -> "SceneFragmentSpec":
        """Return the 34-column upper-band right room strip."""
        return cls.from_preset("upper_band_right_room_strip_34")

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def width(self) -> int:
        return max((len(row) for row in self.rows), default=0)

    def render(self) -> list[str]:
        """Return the locked fragment rows."""
        return list(self.rows)


@dataclass(frozen=True)
class VerticalPathwaySpec:
    """Locked vertical/offshoot pathway stamp selected by name and width.

    This keeps R24 pathway selection in connector-spec vocabulary while the
    actual glyph rows remain the locked reference macro.
    """

    name: str
    width_units: int = 6

    @classmethod
    def regular_r24(cls, width_units: int = 6) -> "VerticalPathwaySpec":
        """Return the current locked regular vertical/offshoot R24 pathway."""
        return cls("regular_r24", width_units)

    def render(self) -> list[str]:
        """Return the locked vertical/offshoot pathway stamp."""
        if self.name != "regular_r24":
            raise NotImplementedError(f"unknown vertical pathway spec: {self.name}")
        if self.width_units != 6:
            raise NotImplementedError("regular_r24 currently supports only the locked 6-unit width")
        from presets import build_vertical_pathway

        return list(build_vertical_pathway("regular_r24_6"))


@dataclass(frozen=True)
class HorizontalConnectorSpec:
    """Room-local horizontal same-level connector placement.

    ``offset_x`` / ``y`` mirror the locked three-room macro convention: the
    connector origin is resolved relative to the source room's x coordinate,
    while y is already in scene/canvas coordinates. Rendering stays locked to
    ``horizontal_corridor(width_units)`` until a broader corridor family is
    drawn and verified.
    """

    from_room: str
    to_room: str
    offset_x: int
    y: int
    width_units: int

    def origin_from_room_x(self, room_x: int) -> tuple[int, int]:
        """Resolve this room-local connector origin to global canvas coords."""
        return (room_x + self.offset_x, self.y)

    def render(self) -> list[str]:
        """Return the locked same-level horizontal corridor stamp."""
        from curved_dungeon_grammar import horizontal_corridor

        return horizontal_corridor(self.width_units)


@dataclass(frozen=True)
class NorthConnectorSpec:
    """Room-local north connector placement resolved into global glyph regions.

    ``opening`` is chunk-based and room-local. ``upper_rows`` stores optional
    visible rows north of the room as ``(room_local_x, row_text)`` pairs; the
    first row's x offset defines the upper-fragment origin used by annotations.
    """

    name: str
    room_x: int
    room_y: int
    room_chunks: int
    opening: Opening
    upper_rows: tuple[tuple[int, str], ...] = ()

    @classmethod
    def from_opening_preset(
        cls,
        name: str,
        *,
        room_x: int,
        room_y: int,
        room_chunks: int = 8,
        upper_rows: tuple[tuple[int, str], ...] = (),
    ) -> "NorthConnectorSpec":
        """Build a north connector spec from ``presets.NORTH_OPENING_PRESETS``."""
        from presets import build_north_opening

        return cls(
            name=name,
            room_x=room_x,
            room_y=room_y,
            room_chunks=room_chunks,
            opening=build_north_opening(name),
            upper_rows=upper_rows,
        )

    def validate(self) -> None:
        """Validate the opening against the supported NorthWall grammar."""
        NorthWall(self.room_chunks, (self.opening,))

    @property
    def opening_start_x(self) -> int:
        return self.room_x + (self.opening.start_chunk - 1) * CHUNK_GLYPH_W

    @property
    def opening_window(self) -> tuple[int, int, int, int]:
        """Global ``(x, y, width, height)`` covering the north-wall opening carve."""
        width = self.opening.width_chunks * CHUNK_GLYPH_W + 1
        return (self.opening_start_x, self.room_y, width, 2)

    @property
    def north_wall_region(self) -> tuple[int, int, int, int]:
        """Global ``(x, y, width, height)`` for the closed middle-shell north rows."""
        return (self.room_x, self.room_y, north_wall_underside_width(self.room_chunks), 2)

    @property
    def upper_fragment_y(self) -> int:
        return self.room_y - len(self.upper_rows)

    @property
    def upper_fragment_origin(self) -> tuple[int, int]:
        if not self.upper_rows:
            return (self.room_x, self.upper_fragment_y)
        first_x, _ = self.upper_rows[0]
        return (self.room_x + first_x, self.upper_fragment_y)
