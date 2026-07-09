#!/usr/bin/env python3
"""Thin config presets for Tristan's curved dungeon grammar.

This module is DATA, not new rendering code. It maps named presets to
geometry/skin configs so that "2-block opening", "3-block opening", etc.
become preset configs instead of separate functions.

Two kinds of presets live here:

* ``NORTH_OPENING_PRESETS`` — named ``Opening`` configs (chunk-based north-wall
  openings). ``Opening`` defaults its ``skin`` to the plain skin via its own
  ``__post_init__``.
* ``SOUTH_OPENING_TEMPLATE_PRESETS`` — locked visible upper/south-opening rows
  as room-local ``(x, text)`` pairs for fragments not yet parameterized.
* ``VERTICAL_PATHWAY_PRESETS`` — locked vertical/offshoot pathway stamp rows.
* ``RAISED_FRAGMENT_PRESETS`` — locked raised-floor / raised-edge fragment rows
  used as independent structural anchors inside the six-room source.
* ``SCENE_FRAGMENT_PRESETS`` — locked generic scene fragment rows used as
  independent structural anchors inside the six-room source.
* ``SHELL_PRESETS`` — named shell configs as plain dicts. A preset carries a
  ``variant`` plus the geometry kwargs accepted by ``RoomShell`` (and, for the
  left/terminal variants that ``RoomShell``'s current geometry cannot yet
  reproduce, a ``render_ref`` naming the locked reference render function).

Helpers
-------
* ``build_shell(name)`` returns a ``RoomShell`` (or a ``RoomShell``-like object
  whose ``.render()`` matches the locked reference) for the named preset.
* ``build_north_opening(name)`` returns the named ``Opening``.
* ``build_south_opening_template(name)`` returns the named locked row template.
* ``build_vertical_pathway(name)`` returns the named locked pathway stamp rows.
* ``build_raised_fragment(name)`` returns the named locked raised fragment rows.
* ``build_scene_fragment(name)`` returns the named locked generic scene fragment rows.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

from modular_ascii_parts import Opening
from room_shell import RoomShell
from curved_dungeon_grammar import room_shell_left_8
from three_room_macro_test import empty_terminal_room_shell_8


# ─────────────────────────────────────────────────────────────────────────────
# North-opening presets (DATA: just Opening configs)
# ─────────────────────────────────────────────────────────────────────────────
NORTH_OPENING_PRESETS: Dict[str, Opening] = {
    # compact single-block opening centered on chunk 6 (e.g. r24 room)
    "compact_north_r24": Opening(6, 1),
    # 2-block centered-ish opening
    "center_2": Opening(4, 2),
    # 4-block wide opening
    "wide_4": Opening(3, 4),
    # 4-block centered variant (alias of wide_4 geometry, distinct name)
    "center_4": Opening(3, 4),
    # 6-block wide opening
    "wide_6": Opening(2, 6),
}


# ─────────────────────────────────────────────────────────────────────────────
# South-opening / upper-fragment templates (DATA: room-local rows)
# ─────────────────────────────────────────────────────────────────────────────
SOUTH_OPENING_TEMPLATE_PRESETS: Dict[str, tuple[tuple[int, str], ...]] = {
    "compact_r24": (
        (8, "|  `   `   `   `   `   |/|"),
        (8, "'— — — — — —.    ,— — — —'"),
        (20, "|  `/|"),
        (20, "|  , |"),
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Vertical/offshoot pathway presets (DATA: locked stamp rows)
# ─────────────────────────────────────────────────────────────────────────────
VERTICAL_PATHWAY_PRESETS: Dict[str, tuple[str, ...]] = {
    "regular_r24_6": (
        ', -,- -,—-j` . |t--,- -,.'.ljust(27),
        '|_/___/__j ` . t__/___/,| '.ljust(27),
        '|. ` . ` . ` . ` . ` .| |  '.ljust(27),
        "|. ` . ` . ` . ` . ` .'/|  ".ljust(27),
        "'- - - - -.` . `.- - -'-'".ljust(27),
        '          |` . /|'.ljust(27),
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Raised-floor / raised-edge fragments (DATA: locked row slices)
# ─────────────────────────────────────────────────────────────────────────────
RAISED_FRAGMENT_PRESETS: Dict[str, tuple[str, ...]] = {
    # Small connector fragment whose leading backtick was corrected to live on
    # line 15 in the six-room source. Keep this as a named spec so source
    # alignment tests do not hide row drift behind source-vs-source equality.
    "connector_line15_short": (
        "` ,— — — —'",
        " /|",
        ", |",
        "|/‘ —,— —,.",
        "‘/__/___/ |",
    ),
    # Widened 27-column raised-edge fragments embedded in four room interiors.
    "widened_27_partial": (
        "` ,— — — — — — — — — — — —.",
        " /|                       |",
        ", |                       |",
        "|/|                       |",
    ),
    # Decorated center connector fragment with ;.; floor detail and right-side
    # grid ticks. This one-off is fragile enough to lock independently.
    "center_decorated_29": (
        "` ,— — — — — — — — — —. `   ‘",
        " /|                   |      ",
        ", |                   | `   `",
        "|/‘— —,— —,— —,— —,— -'      ",
        "‘/___/___/;.;/___/___/  `   ,",
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Generic scene fragments (DATA: locked row slices)
# ─────────────────────────────────────────────────────────────────────────────
SCENE_FRAGMENT_PRESETS: Dict[str, tuple[str, ...]] = {
    "room_bottom_rail_34": (
        "`— — — — — — — — — — — — — — — — '",
    ),
    "room_top_band_34": (
        ",— —,— —,— —,— —,— —,— —,— —,— —,.",
    ),
    "room_floor_band_34": (
        "|__/___/___/___/___/___/___/___/ |",
    ),
    "middle_seam_connector_gap_80": (
        "                       ,— —,— —,— —,— —,— —'  |/‘ —,— —,.                       ",
        "                       |__/___/___/___/___/   ‘/__/___/ |                       ",
    ),
    "lower_band_left_room_strip_34": (
        "|  `   `   `   `   `   `   `   ‘/_",
        "|                                 ",
        "|  `   `   `   `   `   `   `   ` ,",
        "|                               /|",
        "|  `   `   `   `   `   `   `   , |",
        "|                              |/|",
        "`— — — — — — — — — — — — — — — — '",
    ),
    "lower_band_gap_strip_23": (
        "__/___/___/___/___/___/",
        "                       ",
        "— — — — — — — — — — — —",
        "                       ",
        "                       ",
        "                       ",
        "                       ",
    ),
    "lower_band_middle_room_strip_34": (
        "   ` ,— — — — — — — — — —. `   ‘/_",
        "    /|                   |        ",
        ".  , |                   | `   ` ,",
        "|  |/‘— —,— —,— —,— —,— -'      /|",
        "|  ‘/___/___/;.;/___/___/  `   , |",
        "|                              |/|",
        "`— — — — — — — — — — — — — — — — '",
    ),
    "lower_band_right_room_strip_34": (
        "   , |   | `   `   `   `   `   | |",
        "   |/|   |                     |/|",
        ".  | |   | `   `   `   `   `   | |",
        "|  |/‘— —,                     |/|",
        "|  ‘/___/  `   `   `   `   `   | |",
        "|                              |/|",
        "`— — — — — — — — — — — — — — — — '",
    ),
    "upper_band_left_room_strip_34": (
        "|  `   `   `   `   `   `   `   | |",
        "|                              |/‘",
        "|  `   `   `   `   `   `   `   ‘/_",
        "|                                 ",
        "|  `   `   `   `   `   `   `   ` ,",
        "|                               /|",
        "|  `   `   `   `   `   `   `   , |",
        "|                              |/|",
        "`— — — — — — — — — — — — — — — — '",
    ),
    "upper_band_gap_strip_23": (
        "                       ",
        "— —,— —,— —,— —,— —,— —",
        "__/___/___/___/___/___/",
        "                       ",
        "— — — — — — — — — — — —",
        "                       ",
        "                       ",
        "                       ",
        "                       ",
    ),
    "upper_band_middle_room_strip_34": (
        "|  `   `   `   `   `   `   `   | |",
        ",                              |/‘",
        "   `   `   `   `   `   `   `   ‘/_",
        "                                  ",
        ".  `   `   `   `   `   `   `   ` ,",
        "|                               /|",
        "|  `   `   `   `   `   `   `   , |",
        "|                              |/|",
        "|  `   `   `   `   `   `   `   | |",
    ),
    "upper_band_right_room_strip_34": (
        "|  ` ,— — — — — — — — — —. `   | |",
        ",   /|                   |     |/|",
        "   , |                   | `   | |",
        "   |/|                   |     |/|",
        ".  | |                   | `   | |",
        "|  |/‘— —,— —,— —,— —,— -,     |/|",
        "|  ‘/___/___/;.;/___/___/  `   | |",
        "|                              |/|",
        "`— — — — — — — — — — — — — — — — '",
    ),
    "scene_top_rows_1_4": (
        "",
        ",— —,— —,— —,— —,— —,— —,— —,— —,.                       ,— —,— —,— —,— —,— —,— —,- —,— —,.                       ,— —,— —,— —,— —,— —,— —,— —,— —,.",
        "|__/___/___/___/___/___/___/___/ |                       |__/___/___/___/___/___/___/___/ |                       |__/___/___/___/___/___/___/___/ |",
        "|                              |/|                       |                              |/|                       |                              |/|",
    ),
    "scene_mid_connector_rows_14_17": (
        "                                                         |                              |/| ",
        "                                                         `— — — — — — — — — —.  ` ,— — — —'     ",
        "                                                                             |   /|                                       ",
        "                                                                             |  , |                                                                  ",
    ),
    "scene_lower_connector_rows_20_22": (
        "|                              |/|                       |                              |/|                       |                              |/|",
        "|  `   `   `   `   `   `   `   | |                       |  `   `   `   `   `   `   `   | |                       |  ` ,— —. `   `   `   `   `   | |",
        "|                              |/‘— —,— —,— —,— —,— —,— —,                              |/‘— —,— —,— —,— —,— —,— —,   /|   |                     |/|",
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Shell presets (DATA: plain dicts)
# ─────────────────────────────────────────────────────────────────────────────
SHELL_PRESETS: Dict[str, Dict[str, object]] = {
    "middle_8": {
        "variant": "middle",
        "width_chunks": 8,
        "height_chunks": 5,
    },
    "left_8": {
        "variant": "left",
        "width_chunks": 8,
        "height_chunks": 5,
        # RoomShell's generic empty-room fallback uses a uniform east grammar and
        # does NOT reproduce the locked left-shell connector; delegate to the
        # compatibility macro until left-shell rendering is parameterized.
        "render_ref": "room_shell_left_8",
    },
    "terminal_8": {
        "variant": "terminal",
        "width_chunks": 8,
        "height_chunks": 5,
        # Same situation as left_8: delegate to the locked reference render.
        "render_ref": "empty_terminal_room_shell_8",
    },
    "four_openings_single": {
        "variant": "four_openings",
        "width_chunks": 8,
        "height_chunks": 5,
    },
}


# Locked reference renderers, keyed by the string stored in ``render_ref``.
_REF_RENDERERS: Dict[str, Callable[[], List[str]]] = {
    "room_shell_left_8": room_shell_left_8,
    "empty_terminal_room_shell_8": empty_terminal_room_shell_8,
}


@dataclass
class _LockedShell:
    """Thin adapter exposing a locked reference render as a RoomShell-like object.

    Used only for shell variants whose exact grammar ``RoomShell`` does not yet
    reproduce. It mirrors the minimal interface the tests rely on (``.render()``)
    and keeps ``SHELL_PRESETS`` as pure data.
    """

    render_ref: str

    def render(self) -> List[str]:
        return _REF_RENDERERS[self.render_ref]()


def build_shell(name: str) -> RoomShell:
    """Return a shell for the named preset.

    For the ``middle`` variant this constructs a real ``RoomShell(**cfg)``.
    For variants that ``RoomShell`` cannot yet reproduce exactly (``left`` /
    ``terminal``), it returns a ``RoomShell``-like adapter delegating to the
    locked reference render named by the preset's ``render_ref``.
    """
    cfg = dict(SHELL_PRESETS[name])
    ref = cfg.pop("render_ref", None)
    if ref is not None:
        cfg.pop("variant", None)  # consumed for locked-reference dispatch only
        return _LockedShell(ref)
    return RoomShell(**cfg)


def build_north_opening(name: str) -> Opening:
    """Return the named north-opening preset."""
    return NORTH_OPENING_PRESETS[name]


def build_south_opening_template(name: str) -> tuple[tuple[int, str], ...]:
    """Return the named locked south-opening/upper-fragment row template."""
    return SOUTH_OPENING_TEMPLATE_PRESETS[name]


def build_vertical_pathway(name: str) -> tuple[str, ...]:
    """Return the named locked vertical/offshoot pathway stamp rows."""
    return VERTICAL_PATHWAY_PRESETS[name]


def build_raised_fragment(name: str) -> tuple[str, ...]:
    """Return the named locked raised-floor / raised-edge fragment rows."""
    return RAISED_FRAGMENT_PRESETS[name]


def build_scene_fragment(name: str) -> tuple[str, ...]:
    """Return the named locked generic scene fragment rows."""
    return SCENE_FRAGMENT_PRESETS[name]
