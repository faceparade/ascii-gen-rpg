#!/usr/bin/env python3
"""Section-based standalone room renderer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from section_layout import DoorwaySpec, InteriorEnclosureSpec, RoomModuleSpec
from modular_ascii_parts import NorthWall, Opening
from modular_canvas import ModularCanvas, OPAQUE


@dataclass(frozen=True)
class RenderedRoom:
    room_id: str
    width_sections: int
    height_sections: int
    rows: list[str]
    provenance: dict[str, tuple[str, ...]]
    ports: dict[str, DoorwaySpec | None]
    interiors: list[InteriorEnclosureSpec]


_NORTH_SOURCE = ("north_wall",)
_WEST_SOURCE = ("west_wall",)
_EAST_SOURCE = ("east_wall",)
_SOUTH_SOURCE = ("south_wall",)
_FLOOR_SOURCE = ("floor",)
_ENCLOSURE_SOURCES = {
    "enclosure_top": ("enclosure_top",),
    "enclosure_body": ("enclosure_body",),
    "enclosure_bottom": ("enclosure_bottom",),
}


def render_room(spec: RoomModuleSpec) -> RenderedRoom:
    width = spec.width_sections
    height = spec.height_sections

    openings_by_side: dict[str, list[DoorwaySpec]] = {}
    for opening in spec.openings:
        openings_by_side.setdefault(opening.side, []).append(opening)

    north_opening = None
    if "north" in openings_by_side:
        opening = openings_by_side["north"][0]
        if opening.span_sections != 1 or opening.start_section < 1 or opening.start_section > width:
            raise ValueError("north opening must occupy exactly one section within the room width")
        north_opening = Opening(opening.start_section, opening.span_sections)

    north_rows = NorthWall(width, (north_opening,) if north_opening else ()).render()
    body_rows = height
    south_rows = 1
    row_count = len(north_rows) + body_rows + south_rows
    col_count = width * 4 + 2

    provenance: dict[str, tuple[str, ...]] = {}
    for index, row in enumerate(north_rows):
        provenance[f"north_{index}"] = _NORTH_SOURCE
    for body_y in range(body_rows):
        y = len(north_rows) + body_y
        west_source = "west_wall_doorway" if openings_by_side.get("west") and openings_by_side["west"][0].start_section == body_y + 1 else "west_wall"
        east_source = "east_wall_doorway" if openings_by_side.get("east") and openings_by_side["east"][0].start_section == body_y + 1 else "east_wall"
        provenance[f"body_{body_y}_west"] = (west_source,)
        provenance[f"body_{body_y}_east"] = (east_source,)
        provenance[f"body_{body_y}_floor"] = _FLOOR_SOURCE
    provenance[f"south_{0}"] = _SOUTH_SOURCE

    canvas = ModularCanvas(col_count, row_count)
    for y, row in enumerate(north_rows):
        canvas.paste_stamp([row], 0, y, OPAQUE, source="north_wall", layer="wall")

    east_doorway = next(iter(openings_by_side.get("east", [])), None)
    west_doorway = next(iter(openings_by_side.get("west", [])), None)
    east_col = col_count - 1
    west_col = 0

    for body_y in range(body_rows):
        y = len(north_rows) + body_y
        west_source = "west_wall_doorway" if west_doorway and west_doorway.start_section == body_y + 1 else "west_wall"
        east_source = "east_wall_doorway" if east_doorway and east_doorway.start_section == body_y + 1 else "east_wall"
        west_glyph = " " if west_source == "west_wall_doorway" else ","
        east_glyph = " " if east_source == "east_wall_doorway" else "/|"

        canvas.paste_stamp([west_glyph], west_col, y, OPAQUE, source=west_source, layer="wall")
        canvas.paste_stamp([east_glyph], east_col, y, OPAQUE, source=east_source, layer="wall")
        fill = " " * (col_count - 2)
        canvas.paste_stamp([fill], west_col + 1, y, OPAQUE, source="floor", layer="floor")

    south_y = len(north_rows) + body_rows
    south_glyph = "'" * col_count
    canvas.paste_stamp([south_glyph], 0, south_y, OPAQUE, source="south_wall", layer="wall")

    for enclosure in spec.interiors:
        _paste_enclosure(canvas, enclosure, len(north_rows), provenance)

    return RenderedRoom(
        room_id=spec.room_id,
        width_sections=width,
        height_sections=height,
        rows=[row.ljust(col_count) for row in canvas.render_lines()],
        provenance=provenance,
        ports={
            "north": next(iter(openings_by_side.get("north", [])), None),
            "south": next(iter(openings_by_side.get("south", [])), None),
            "east": next(iter(openings_by_side.get("east", [])), None),
            "west": next(iter(openings_by_side.get("west", [])), None),
        },
        interiors=list(spec.interiors),
    )


def _paste_enclosure(canvas: ModularCanvas, enclosure: InteriorEnclosureSpec, room_top: int, provenance: dict[str, tuple[str, ...]]) -> None:
    if enclosure.openings:
        raise ValueError("interior enclosure openings are not implemented in the locked proof scene")
    if enclosure.style != "raised_floor":
        raise NotImplementedError(
            f"interior enclosure style {enclosure.style!r} is not implemented yet"
        )

    x_start = 1 + enclosure.x_sections * 4
    y = room_top + enclosure.y_sections
    width = enclosure.width_sections * 4 + 1
    height = enclosure.height_sections

    top = "`" + "— " * (enclosure.width_sections * 2)
    top = top[:width].ljust(width)
    bottom = "'" + "— " * (enclosure.width_sections * 2)
    bottom = bottom[:width].ljust(width)
    middle = "|" + " " * (width - 2) + "|"

    canvas.paste_stamp([top], x_start, y, OPAQUE, source="enclosure_top", layer="wall")
    provenance[f"enclosure_{enclosure.x_sections}_{enclosure.y_sections}_top"] = _ENCLOSURE_SOURCES["enclosure_top"]
    y += 1
    for relative_y in range(1, max(1, height - 1)):
        canvas.paste_stamp([middle], x_start, y, OPAQUE, source="enclosure_body", layer="wall")
        provenance[f"enclosure_{enclosure.x_sections}_{enclosure.y_sections + relative_y}"] = _ENCLOSURE_SOURCES["enclosure_body"]
        y += 1
    canvas.paste_stamp([bottom], x_start, y, OPAQUE, source="enclosure_bottom", layer="wall")
    provenance[f"enclosure_{enclosure.x_sections}_{enclosure.y_sections + height - 1}_bottom"] = _ENCLOSURE_SOURCES["enclosure_bottom"]
