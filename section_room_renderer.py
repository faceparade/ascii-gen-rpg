#!/usr/bin/env python3
"""Section-based standalone room renderer using locked six-room references."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from section_layout import DoorwaySpec, InteriorEnclosureSpec, RoomModuleSpec
from modular_ascii_parts import NorthWall, Opening
from modular_canvas import ModularCanvas, OPAQUE
from room_shell import RoomShell
from platform_shell import RaisedFloorSection


@dataclass(frozen=True)
class RenderedRoom:
    room_id: str
    width_sections: int
    height_sections: int
    rows: List[str]
    provenance: Dict[str, str]
    ports: Dict[str, DoorwaySpec | None]
    interiors: List[InteriorEnclosureSpec]


def _locked_middle_body_rows() -> List[str]:
    locked = RoomShell(width_chunks=8, height_chunks=5, variant='middle').render()
    if len(locked) < 3:
        raise AssertionError("locked RoomShell middle must have at least 3 rows")
    return locked[2:-1]


_LOCKED_MIDDLE_BODY_ROWS = _locked_middle_body_rows()


def _locked_floor_section_rows() -> List[str]:
    rows = RaisedFloorSection(4).render()
    if not rows:
        raise AssertionError("locked RaisedFloorSection must contain rows")
    return rows


_LOCKED_FLOOR_SECTION_ROWS = _locked_floor_section_rows()


def _room_body_rows(width_sections: int, height: int) -> List[str]:
    """Build room body rows from exact locked middle-shell body rows."""
    if height < 1:
        raise ValueError("room body height must be >= 1")
    locked_rows = _LOCKED_MIDDLE_BODY_ROWS
    width_glyphs = width_sections * 4 + 2
    body_rows: List[str] = []
    for body_y in range(height):
        ref = locked_rows[body_y % len(locked_rows)]
        repeated = (ref[1:] * ((width_sections + 3) // 4 + 1))[:max(0, width_glyphs)]
        row_text = "|" + repeated
        body_rows.append(row_text[:width_glyphs].ljust(width_glyphs))
    return body_rows


def _enclosure_rows(width_sections: int, height: int) -> List[str]:
    """Build enclosure rows from exact locked raised-floor section rows."""
    if height < 3:
        raise ValueError("enclosure height must be >= 3 for the locked raised-floor section")
    locked_rows = _LOCKED_FLOOR_SECTION_ROWS
    width_glyphs = width_sections * 4 + 1
    results: List[str] = []
    for row_y in range(height):
        ref = locked_rows[row_y % len(locked_rows)]
        repeated = (ref * ((width_sections + 2) // 4 + 1))[:max(0, width_glyphs)]
        results.append(repeated.ljust(width_glyphs))
    return results


def render_room(spec: RoomModuleSpec) -> RenderedRoom:
    width = spec.width_sections
    height = spec.height_sections
    width_glyphs = width * 4 + 2

    openings_by_side: Dict[str, List[DoorwaySpec]] = {}
    for opening in spec.openings:
        openings_by_side.setdefault(opening.side, []).append(opening)

    north_opening = None
    if "north" in openings_by_side:
        opening = openings_by_side["north"][0]
        if opening.span_sections != 1 or opening.start_section < 1 or opening.start_section > width:
            raise ValueError("north opening must occupy exactly one section within the room width")
        north_opening = Opening(opening.start_section, opening.span_sections)

    north_rows = NorthWall(width, (north_opening,) if north_opening else ()).render()
    body_rows = _room_body_rows(width, height)
    row_count = len(north_rows) + len(body_rows) + 1
    provenance: Dict[str, str] = {}
    ports = {
        "north": next(iter(openings_by_side.get("north", [])), None),
        "south": next(iter(openings_by_side.get("south", [])), None),
        "east": next(iter(openings_by_side.get("east", [])), None),
        "west": next(iter(openings_by_side.get("west", [])), None),
    }

    canvas = ModularCanvas(width_glyphs, row_count)
    for y, row in enumerate(north_rows):
        source = "north_wall_opening" if north_opening else "north_wall"
        canvas.paste_stamp([row], 0, y, OPAQUE, source=source, layer="wall")
        provenance[f"north_{y + 1}"] = source

    east_doorway = ports["east"]
    west_doorway = ports["west"]

    for body_y, raw in enumerate(body_rows):
        y = len(north_rows) + body_y
        body_y_one_based = body_y + 1
        pasted = list(" " * width_glyphs)
        west_glyph = " "
        east_glyph = " "
        if not (west_doorway and west_doorway.start_section == body_y_one_based):
            west_glyph = "|"
            pasted[0] = "|"
        if not (east_doorway and east_doorway.start_section == body_y_one_based):
            east_glyph = "|"
            pasted[width_glyphs - 1] = "|"
        clamped = raw[:width_glyphs].ljust(width_glyphs)
        for idx, ch in enumerate(clamped):
            if ch != " ":
                pasted[idx] = ch
        text = "".join(pasted)
        canvas.paste_stamp([text], 0, y, OPAQUE, source="room_body", layer="wall")
        provenance[f"body_{body_y_one_based}"] = west_glyph + text[1:-1] + east_glyph

    south_y = len(north_rows) + len(body_rows)
    south_glyph = "'" * width_glyphs
    canvas.paste_stamp([south_glyph], 0, south_y, OPAQUE, source="south_wall", layer="wall")
    provenance[f"body_{len(body_rows) + 1}"] = "south_wall"

    for enclosure in spec.interiors:
        _paste_locked_enclosure(canvas, enclosure, len(north_rows), provenance, width_glyphs)

    return RenderedRoom(
        room_id=spec.room_id,
        width_sections=width,
        height_sections=height,
        rows=[row.ljust(width_glyphs) for row in canvas.render_lines()],
        provenance=provenance,
        ports=ports,
        interiors=list(spec.interiors),
    )


def _paste_locked_enclosure(canvas: ModularCanvas, enclosure: InteriorEnclosureSpec, room_top: int, provenance: Dict[str, str], width_glyphs: int) -> None:
    if enclosure.openings:
        raise ValueError("interior enclosure openings are not implemented in the locked proof scene")
    if enclosure.style != "raised_floor":
        raise NotImplementedError(
            f"interior enclosure style {enclosure.style!r} is not implemented yet"
        )

    x_start = 1 + enclosure.x_sections * 4
    y = room_top + enclosure.y_sections
    width = enclosure.width_sections * 4 + 1
    locked_rows = _enclosure_rows(enclosure.width_sections, enclosure.height_sections)
    west_source = f"enclosure_{enclosure.x_sections}_{enclosure.y_sections}_west"
    east_source = f"enclosure_{enclosure.x_sections}_{enclosure.y_sections}_east"
    for relative_y, row in enumerate(locked_rows):
        source = west_source if relative_y < enclosure.height_sections - 1 else east_source
        canvas.paste_stamp([row], x_start, y + relative_y, OPAQUE, source=source, layer="wall")
        provenance[f"enclosure_{enclosure.x_sections}_{enclosure.y_sections + relative_y}"] = source
