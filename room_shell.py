#!/usr/bin/env python3
"""Parametric RoomShell generator for Tristan's curved dungeon grammar.

This module reproduces the locked room-shell stamps byte-for-byte at
their default configuration, while also exposing a parametric surface:

* ``room_shell_middle_8()``  -> ``RoomShell(variant='middle')``
* ``room_shell_left_8()``    -> ``RoomShell(variant='left')``
* ``empty_terminal_room_shell_8()`` -> ``RoomShell(variant='terminal')``
* ``single_room_four_openings.txt`` -> ``RoomShell(variant='four_openings')``

The shell variants are exact at ``width_chunks == 8`` / ``height_chunks == 5``;
``four_openings`` is a locked ragged fragment and ignores scaling until the full
four-side grammar is proven.

Design
------
Each variant shares the north wall (delegated to ``NorthWall`` so north
openings already work via the existing ``Opening`` type) and is otherwise
composed of logical bands:

* ``variant='middle'`` (v3): a rectangular 8x11 box — north wall + solid ``|``
  side walls + interior pillars on the backtick grid (which can double as
  interior walls if the top is inaccessible in-game) + a backtick-corner bottom
  rail.  The box is locked to 8x5 (the v3 interior is hand-tuned, not
  per-chunk-repeatable).
* ``variant='terminal'`` : north wall + a repeating ``|/|`` / ``| |` plain
  floor band (``height_chunks`` controls how many) + bottom rail.  No platform.
* ``variant='left'`` : north wall (padded to 35 wide to match the locked
  stamp) + a plain floor band whose west edge is ``,`` on every row and whose
  east side uses the left-specific connector grammar, + bottom rail (also
  padded to 35).  No platform.
* ``variant='four_openings'`` : exact locked copy of
  ``single_room_four_openings.txt`` including ragged widths/trailing spaces.

Height scaling
--------------
For ``terminal`` the plain floor band count scales with ``height_chunks`` (the
locked default is 5, which yields exactly the 12-row terminal stamp). ``middle``
and ``left`` are locked to 8x5 and raise ``NotImplementedError`` for unsupported
sizes (the middle interior and left east-connector grammar are irregular;
extending them is documented as a follow-up).

East / west openings
--------------------
``west_opening`` / ``east_opening`` are ``VerticalOpening`` specs that carve a
vertical gap in the respective side wall (the left column for west, the right
column for east). The gap is rendered with the shared CapSkin vocabulary from
``caps.py``: a top cap (``j`` west, ``/`` east) and a bottom cap (``t``), with a
blank inner run — the same corner language as the north opening's ``j`` / ``,t``
/ ``t``. When ``None`` (the default), the render is byte-for-byte identical to
the locked shells.

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from modular_canvas import ModularCanvas, OPAQUE
from geometry import RoomSpec, WallSpan, PortSpec, ChunkGrid
from modular_ascii_parts import NorthWall, CHUNK_GLYPH_W, Opening
from caps import VerticalOpening, west_cap_skin, east_cap_skin, render_side_opening_column


# ─────────────────────────────────────────────────────────────────────────────
# Middle-shell grammar (locked v3: rectangular box with '|' room walls, easiest
# for a generative system — every row is '|' + interior + '|'.  The interior is
# the 6-line structure with two literal fixes: row 0 gets a leading space before
# ".", and the backtick-alignment rule (every other row: 1,3,5) drives POSITION
# only — the shipped skin uses '.' for the interior grid (backticks are a
# reference overlay, never drawn).  Exact for width_chunks == 8 only; other
# widths raise NotImplementedError.
# ─────────────────────────────────────────────────────────────────────────────
# Body rows 2-9 of the v3 middle shell (byte-equal to room_shell_middle_8()).
# Grid rows 1,3,5 of the structure carry the alignment guide; the shipped skin
# renders those interior ticks as '.' (uniform), per the "backticks are
# reference, not the final skin" decision.
MIDDLE_BODY_V3: list[str] = [
    "|                              | |",
    "|  `   `   `   `   `   `   `   |/|",
    "|                              | |",
    "|  `   `   `   `   `   `   `   |/|",
    "|                              | |",
    "|  `   `   `   `   `   `   `   |/|",
    "|                              | |",
    "|  `   `   `   `   `   `   `   |/|",
    "`— — — — — — — — — — — — — — — — '",
]

# Left-shell east connectors (locked, 4 glyphs each, placed at cols [L-4..L-1]
# where L = 35).  West edge is ',' on every row; no platform.
LEFT_EAST: dict[int, str] = {
    2: "|/| ",
    3: "| | ",
    4: "|/t—",
    5: "t/__",
    6: "    ",
    7: "  ’—",
    8: " /| ",
    9: ", | ",
    10: "|/| ",
}

# Plain floor rows of the left shell that carry the full interior tick set.
LEFT_TICK_ROWS = frozenset({3, 5, 7, 9})

# Target width of the left shell stamp (includes the trailing-space padding
# present in the locked room_shell_left_8() reference).
LEFT_WIDTH = 35

# Locked single-room shell with all four directional openings.  This is a
# user-supplied reference fragment, intentionally ragged/trailing-space-bearing;
# do not rectangularize it or derive it procedurally until the full four-side
# wall grammar has been proven byte-for-byte.
FOUR_OPENINGS_LOCKED: list[str] = [
    "       ,— —,— —,— —,— —,— —'  | ‘ —,— —,.    ",
    "       |__/___/___/___/___/   ‘/__/___/ |    ",
    "       |                              |/|   ",
    "       |  `   `   `   `   `   `   `   | |   ",
    "— —,— —,                              |/‘— —",
    "__/___/   `   `   `   `   `   `   `   ‘/___/",
    "                                            ",
    "— — — —.  `   `   `   `   `   `   `   ` ,— —",
    "       |                               /|   ",
    "       |  `   `   `   `   `   `   `   , |   ",
    "       |                              |/|   ",
    "       |                              | |   ",
    "       |          `   `   `   `   `   |/| ",
    "       `— — — — — — — — — —.    ,— — — —'   ",
    "                           |  `/|",
]


def single_room_four_openings_shell() -> list[str]:
    """Return the locked four-opening single-room shell reference."""
    return list(FOUR_OPENINGS_LOCKED)


def close_north_wall_for_middle(wall_rows: list[str]) -> list[str]:
    """Close a bare NorthWall for the v3 middle RoomShell box.

    ``NorthWall`` renders the bare/open part: top row width is ``4W+1`` and
    ends in ``.``; underside width is ``4W+2`` and starts with ``,``.  The
    locked middle shell closes that part into a rectangular room by replacing
    the top terminator with ``,.`` and the underside's leading ``,`` with ``|``.
    """
    if len(wall_rows) != 2:
        raise ValueError("expected exactly two NorthWall rows")
    top, underside = wall_rows
    if not top.endswith("."):
        raise ValueError(f"bare NorthWall top must end with '.', got {top!r}")
    if not underside.startswith(","):
        raise ValueError(f"bare NorthWall underside must start with ',', got {underside!r}")
    return [top[:-1] + ",.", "|" + underside[1:]]


@dataclass
class RoomShell:
    """Parametric room-shell generator covering the locked shell variants.

    Attributes
    ----------
    width_chunks:
        Number of north-wall chunks.  The shell full width is ``4*width_chunks+2``
        (34 at the default of 8).
    height_chunks:
        Controls how many plain floor bands the shell has.  The locked default
        of 5 yields exactly the 12-row locked stamps.
    floor_skin:
        Identifier for the interior floor skin.  Only ``'plain_ticks'`` is
        implemented (the locked `` ` ``-tick floor).
    variant:
        Which locked shell to reproduce: ``'middle'`` | ``'left'`` |
        ``'terminal'`` | ``'four_openings'``.
    north_opening:
        Optional ``Opening`` carved into the north wall (rows 0-1).
    west_opening:
        Optional ``VerticalOpening`` carved into the west (left) wall.
    east_opening:
        Optional ``VerticalOpening`` carved into the east (right) wall.
    """

    width_chunks: int = 8
    height_chunks: int = 5
    floor_skin: str = "plain_ticks"
    variant: str = "middle"
    north_opening: Optional[Opening] = None
    west_opening: Optional[VerticalOpening] = None
    east_opening: Optional[VerticalOpening] = None

    # ── geometry helpers (used by callers / future width scaling) ────────────
    @property
    def full_width(self) -> int:
        """Full shell glyph width (rows that reach the east wall)."""
        return 4 * self.width_chunks + 2

    @property
    def north_top_width(self) -> int:
        return 4 * self.width_chunks + 1

    def render(self) -> List[str]:
        """Return the shell rows as a list of strings (no trailing spaces).

        Raises
        ------
        NotImplementedError
            If ``variant='left'`` is requested with a non-default
            ``width_chunks`` / ``height_chunks`` (the left east-connector
            grammar is irregular and only the locked 8x5 stamp is reproduced
            exactly), or if a south opening is requested (not yet supported).
        ValueError
            If ``variant`` is not one of the supported values.
        """
        if self.floor_skin != "plain_ticks":
            raise NotImplementedError(
                f"floor_skin {self.floor_skin!r} not implemented; only 'plain_ticks'"
            )
        if self.variant == "middle":
            rows = self._render_middle()
        elif self.variant == "terminal":
            rows = self._render_terminal()
        elif self.variant == "left":
            rows = self._render_left()
        elif self.variant == "four_openings":
            rows = single_room_four_openings_shell()
        else:
            raise ValueError(
                f"unknown variant {self.variant!r}; expected 'middle', 'left', 'terminal', or 'four_openings'"
            )

        # Carve west/east side-wall openings (no-op when both are None, which
        # keeps the render byte-for-byte identical to the locked shells).
        # When BOTH doorways are set, _render_middle already returns the
        # hand-drawn both-doors stamp (with the doors baked in), so skip the
        # simple carve to avoid double-carving over the stamp art.
        both_doors = (
            self.variant == "middle"
            and self.west_opening is not None
            and self.east_opening is not None
        )
        if not both_doors:
            rows = self._apply_side_openings(rows)
        return rows

    def _apply_side_openings(self, rows: List[str]) -> List[str]:
        """Carve west/east vertical openings into the rendered shell rows."""
        S = self.full_width
        if self.west_opening is not None:
            self._carve_side(rows, "west", 0, self.west_opening, west_cap_skin())
        if self.east_opening is not None:
            self._carve_side(rows, "east", S - 1, self.east_opening, east_cap_skin())
        return rows

    @staticmethod
    def _carve_side(rows: List[str], side: str, fixed_col: int,
                    opening: VerticalOpening, skin) -> None:
        glyphs = render_side_opening_column(
            side, opening.start_row, opening.height_chunks, opening.skin or skin
        )
        for k, ch in enumerate(glyphs):
            r = opening.start_row + k
            if 0 <= r < len(rows):
                row = rows[r]
                # West wall is always column 0; east wall is the last glyph of
                # each row (the middle-shell platform rows are narrower than
                # the full width, so a fixed column is wrong for east).
                col = 0 if side == "west" else len(row) - 1
                if 0 <= col < len(row):
                    row_list = list(row)
                    row_list[col] = ch
                    rows[r] = "".join(row_list)

    # ── middle variant ──────────────────────────────────────────────────────
    def _render_middle(self) -> List[str]:
        # v3 interior is hand-tuned for the 8-chunk box and is not
        # per-chunk-repeatable; other widths are intentionally unsupported.
        if self.width_chunks != 8 or self.height_chunks != 5:
            raise NotImplementedError(
                "variant='middle' (v3) reproduces only the locked 8x5 stamp "
                "(room_shell_middle_8) exactly; the v3 interior is hand-tuned "
                "and not per-chunk repeatable, so width/height scaling is a "
                "documented follow-up."
            )
        W = self.width_chunks
        openings = (self.north_opening,) if self.north_opening is not None else ()

        # Rows 0-1: north wall.  v3 closes the box, so row 0 is the 34-wide
        # top ','— -'*8 + '.|' and row 1's left wall is '|' (not the open ','
        # that NorthWall emits for the unclosed style).  NorthWall still
        # supplies the opening carve on both rows.
        wall_rows = close_north_wall_for_middle(NorthWall(W, openings).render())
        top, und = wall_rows

        # Both west + east doorways: emit the hand-drawn locked stamp
        # (room_shell_middle_8_west_east), which is a standalone 36-wide art
        # piece (the user's drawn structure is 2 cols wider than the 34-wide
        # base). Return it as-is — its rows 0-1 are already 36-wide and
        # boundary-consistent, so we do NOT overwrite them with the 34-wide
        # top/und above. North-opening + both-doors is not a supported combo.
        from curved_dungeon_grammar import room_shell_middle_8_west_east
        if self.west_opening is not None and self.east_opening is not None:
            return room_shell_middle_8_west_east()

        return [top, und, *MIDDLE_BODY_V3]

    # ── terminal variant ────────────────────────────────────────────────────
    def _render_terminal(self) -> List[str]:
        W = self.width_chunks
        S = self.full_width
        openings = (self.north_opening,) if self.north_opening is not None else ()

        top, und = NorthWall(W, openings).render()
        rows: List[str] = [top, und]

        # Repeating plain floor band: height_chunks '|/|' rows alternating with
        # (height_chunks - 1) '| |' rows -> 2*height_chunks - 1 plain rows.
        # Ticks appear only on the '| |' rows (matching the locked stamp).
        for i in range(2 * self.height_chunks - 1):
            row = [" "] * S
            row[0] = ","
            if i % 2 == 1:
                for c in range(3, S - 4, 4):
                    row[c] = "`"
            mouth = " |/|" if i % 2 == 0 else " | |"
            for ci, ch in enumerate(mouth):
                row[S - 4 + ci] = ch
            rows.append("".join(row))

        rows.append("’" * S)
        return rows

    # ── left variant ────────────────────────────────────────────────────────
    def _render_left(self) -> List[str]:
        if self.width_chunks != 8 or self.height_chunks != 5:
            raise NotImplementedError(
                "variant='left' currently reproduces only the locked 8x5 stamp "
                "(room_shell_left_8) exactly; width/height scaling of the left "
                "east-connector grammar is a follow-up."
            )

        W = self.width_chunks
        L = LEFT_WIDTH
        openings = (self.north_opening,) if self.north_opening is not None else ()

        # North wall, padded with trailing spaces to match the 35-wide lock.
        top, und = NorthWall(W, openings).render()
        rows: List[str] = [top + "  ", und + " "]

        for r in range(2, 11):
            row = [" "] * L
            row[0] = ","
            if r in LEFT_TICK_ROWS:
                for c in range(3, L - 4, 4):
                    row[c] = "`"
            east = LEFT_EAST[r]
            for i, ch in enumerate(east):
                row[L - 4 + i] = ch
            rows.append("".join(row))

        # Bottom rail, padded to 35 wide.
        rows.append("’" * (L - 1) + " ")
        return rows
