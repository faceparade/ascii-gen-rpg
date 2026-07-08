# Modular ASCII Architecture Shift Audit

Purpose: high-level review of early RPG ASCII modularization choices that should shift before they become hard to unwind.

Viewpoint correction: this grammar is near top-down / Diablo-ish isometric. Avoid platformer/side-view framing and avoid calling the north edge a roof. Use north wall, north edge, wall boundary, mouth, port, threshold, floor grid, and underside/depth-row vocabulary instead.

## Big rule

If something is likely to vary by length, width, decoration, material, damage, gate style, or connector type, do not make separate fixed snippets for every case.

Prefer:

```text
geometry + caps/posts + interior span + skin/decor overlays
```

over:

```text
one hardcoded ASCII block per size/style
```

Raw ASCII examples should remain locked references and test fixtures, but procedural code should move toward parametric structure.

---

## 1. Openings: shift from sized snippets to cap/span/skin

Current lesson: do not create separate 1-block, 2-block, 3-block, 4-block opening parts.

Better model:

```python
Opening(start_chunk=6, width_chunks=1, skin="plain_compact")
Opening(start_chunk=4, width_chunks=2, skin="plain_wide")
Opening(start_chunk=3, width_chunks=4, skin="boss_gate")
```

Renderer logic:

```text
left wall run + left cap + generated interior span + right cap + right wall run
```

Skin controls:

- left cap glyphs;
- right cap glyphs;
- underside/depth-row join;
- optional threshold/decor overlays;
- boss gate posts/bars/ornaments.

Geometry controls:

- wall side;
- start chunk;
- width chunks;
- glyph span;
- port anchor;
- compatible connector families.

Action: refactor `NorthWall` opening rendering toward `OpeningSkin` instead of embedding `j ... ,t` directly inside `_top_with_opening()` and `_underside_with_opening()`.

---

## 2. R24 north connector: shift from “paste R24 stamp” to connector adapter

The corrected R24 north connector shows the locked R24 source is not always the rendered join.

Do not treat `regular_vertical_pathway(6)` as one stamp pasted wholesale onto the north edge.

Better model:

```text
R24 source family metadata
  -> port adapter for north-edge room mouth
  -> visible upper fragment skin
  -> compact north-edge opening skin
```

Keep these separate:

- `R24TailPort`: measured metadata from locked R24 source.
- `NorthEdgeConnectorAdapter`: maps a connector family to a wall opening/anchor.
- `ReferenceUpperFragmentSkin`: current visible 3-line upper fragment.
- `OpeningSkin`: compact `j  ,t` / `/   t___` mouth.

Action: `r24_north_connector.py` should eventually stop hardcoding one `reference_upper_rows` list inside `R24NorthConnector`; move that to a named skin/adapter object.

---

## 3. Walls: shift from NorthWall-only to EdgeWall(side, length, skins)

Current `NorthWall` is useful, but it is too specific if left as the only wall model.

Better model:

```python
EdgeWall(side="north", chunks=8, openings=[...], wall_skin="plain")
EdgeWall(side="east", chunks=5, openings=[...], wall_skin="plain")
```

Why:

- north, south, east, west boundaries will all need openings;
- bridges, gates, drops, holes, and stairs may attach to any side;
- the editor should let a user drag a wall in any direction;
- cap grammar differs at edge/corner/full-span cases.

Action: keep `NorthWall` as the first implementation, but introduce a generic naming layer soon: `WallSide`, `EdgeWall`, `WallSkin`, `OpeningSkin`. Do not duplicate `SouthWall`, `EastWall`, etc. as unrelated modules unless they share a common interface.

---

## 4. Room shells: shift from fixed 8-chunk shell functions to generated room parts

Current functions like `room_shell_middle_8()` and `empty_terminal_room_shell_8()` are locked references, which is good for verification. But they should not become the long-term room system.

Better model:

```python
RoomShell(width_chunks=8, height_chunks=5, north_wall=EdgeWall(...), east_wall=..., floor_skin=...)
```

Room shell generator should know:

- width in chunks;
- depth/height in grid rows;
- north/east/south/west ports;
- floor grid crossings;
- edge/corner caps;
- interior decorators;
- attached platforms/connectors.

Action: next room-shell work should be “generate an 8-chunk room shell that exact-matches the locked shell,” not “copy another fixed row list.”

---

## 5. Corridors/connectors: shift from stamp families to connector interfaces

Current corridor families are useful classifications:

- same-level horizontal room connector;
- R24 regular vertical/offshoot connector;
- R26 special/gated skin;
- R28 boss gate skin;
- R31 larger two-level connector.

But long-term they should share a connector interface:

```python
ConnectorFamily(
    id="r24_regular",
    ports=[...],
    adapters={"north_edge": ..., "south_edge": ..., "east_edge": ...},
    skins=["plain", "gated", "boss"]
)
```

Do not make each connector placement a one-off paste script.

Action: create connector metadata records before adding more connector variants.

---

## 6. Platforms: shift from fixed wide_platform(4) to edge/cell generator + skins

Current `wide_platform(4)` is a locked macro and should stay as a reference. But future platforms should be generated from:

```text
left cap/support + repeated interior units + right cap + underside skin
```

Important known grammar:

- platform origin is the left grid-line/support column;
- visible top dot is one column to the right;
- underside material (`;;;`, `^^`, `@@`, etc.) is a skin, not a new geometry;
- spaces may be opaque for platform silhouette, unlike transparent connector overlays.

Action: do not create `wide_platform_5`, `wide_platform_6`, etc. as separate fixed functions. Make `Platform(width_units, underside_skin, edge_skin)`.

---

## 7. Decor/materials: shift from baked glyph rows to overlays

Do not bake these into core geometry:

- bars `;;;`;
- beams `^^`;
- cracks;
- wet wall/drips;
- holes;
- columns;
- rubble;
- boss-gate ornament;
- bridge planks;
- floor texture variants.

Better model:

```text
base structure layer
opening/cut layer
connector layer
cap/post layer
decor/material overlay layer
```

Action: create an overlay model before adding more decorative variants.

---

## 8. Canvas/paste behavior: shift from raw overwrite to layer-aware compositing

Current issue already appeared: fixed-width connector spaces erased wall chunks.

Needed paste modes:

- opaque paste: spaces are meaningful silhouette, used by platforms/rooms when needed;
- transparent-space paste: spaces do not erase existing wall/floor;
- cut mask: intentionally blanks a span;
- overlay: paints decor only on compatible cells;
- provenance paste: records source part/layer.

Action: create `modular_canvas.py` with `Cell(ch, source, layer)` and paste modes. Stop calling raw `_paste()` directly in new modular code except for legacy reference scripts.

---

## 9. Presets: keep them as named configurations, not separate modules

Presets are still useful, but they should be thin configs:

```python
PRESETS = {
    "compact_north_r24": Opening(start_chunk=6, width_chunks=1, skin="plain_compact"),
    "center_2": Opening(start_chunk=4, width_chunks=2, skin="plain"),
    "wide_4": Opening(start_chunk=3, width_chunks=4, skin="plain"),
    "boss_gate_4": Opening(start_chunk=3, width_chunks=4, skin="boss_gate"),
}
```

Do not let presets become the implementation.

---

## 10. Early code to deprecate or quarantine

`dungeon_tile_system.py` appears to use older terminology and a flatter tile/room model. It includes ceiling/side-view language and may not match the current near top-down grammar. Treat it as historical prototype/reference unless deliberately rewritten.

`curved_dungeon_grammar.py` is still valuable as a locked-reference extraction scaffold, but long-term procedural logic should move into modular parts/canvas/registry rather than adding endless new fixed stamp functions there.

`r24_north_connector.py` is a good experiment but should be refactored after visual approval into:

- connector metadata;
- north-edge adapter;
- upper-fragment skin;
- opening skin;
- artifact/test harness.

---

## Recommended next tasks

1. Add `OpeningSkin` and move compact `j  ,t` rendering out of `NorthWall` internals.
2. Add `modular_canvas.py` with explicit paste modes: opaque, transparent, cut, overlay.
3. Add a tiny `part_registry.py` with metadata for current locked references: room shell, north wall, R24 connector, wide platform.
4. Refactor `r24_north_connector.py` so `reference_upper_rows` is a skin/adapter, not hardcoded connector logic.
5. Build one exact-match generated room shell from `RoomShell(width_chunks=8)` before adding more room sizes.
6. Only after those, expand to other wall sides / boss-gate skins / drag-editor JSON.

## Decision summary

The biggest early shifts are:

```text
opening sizes       -> cap/span geometry + opening skins
R24 raw paste       -> connector adapter + rendered join skin
NorthWall-only      -> generic EdgeWall interface later
fixed room shells   -> generated RoomShell with locked exact-match tests
fixed platforms     -> cap/repeat/cap platform generator + underside skins
raw paste           -> layer-aware modular canvas
baked decor         -> overlays/skins
```

This keeps the system on track for a Townscaper-like editor where the user picks a structure, drags across logical chunks, and the renderer chooses the correct caps, joins, openings, skins, and overlays.
