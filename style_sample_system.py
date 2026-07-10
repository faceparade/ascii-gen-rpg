"""Compatibility entry point with promoted irregular-room and corridor motifs."""
from __future__ import annotations

import style_sample_system_v2_base as _base
from corridor_grammar import render_irregular_room as _render_irregular_room

_base.render_irregular_room = _render_irregular_room
from style_sample_system_v2_base import *  # noqa: F401,F403,E402

render_irregular_room = _render_irregular_room

if __name__ == "__main__":
    raise SystemExit(_base.main())
