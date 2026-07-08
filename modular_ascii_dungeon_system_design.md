# Modular ASCII Dungeon System Design

Goal: turn the curved ASCII dungeon vocabulary into a modular procedural-generation system where parts are understood structurally, geometrically, and stylistically — eventually supporting a Townscaper-like editor where an end user can drag walls, openings, bridges, gates, platforms, rooms, holes, drops, and skins into place.

## Core idea

Do not treat the map as raw text first. Treat it as layered modular structure:

```text
logical structure -> geometric grid -> connected parts -> skinned glyph layers -> rendered ASCII
```

Raw ASCII is the final render, not the source of truth.

## 1. Coordinate systems

The system needs at least two coordinate systems:

### A. Logical grid

This is the procedural/editor grid. It knows about rooms, wall chunks, floor chunks, openings, corridors, bridges, drops, columns, etc.

Example:

```text
Room north wall = 8 wall chunks
Opening = chunks 3-6
Left remainder = chunks 1-2
Right remainder = chunks 7-8
```

### B. Glyph grid

This is the final monospace character canvas.

Example mapping from current style:

```text
1 wall chunk = 4 glyph columns
8 wall chunks = 32 glyph columns plus caps/sidewall details
shared-grid floor crossings advance by 4 columns / 2 rows
```

The generator should compose in logical units, then render to glyph rows.

## 2. Parts registry

Every reusable piece should become a registered part with metadata, not just a text snippet.

A part record should include:

```yaml
id: room_shell_8x
family: room_shell
role: enclosure
logical_size:
  chunks_w: 8
  chunks_h: 5
render_size:
  glyph_w: 34
  glyph_h: 12
anchors:
  origin: north_west_gridline
ports:
  north:
    chunks: [1,2,3,4,5,6,7,8]
    can_open: true
  east:
    can_connect: true
  west:
    can_connect: true
  south:
    foundation: true
layers:
  structure: required
  floor_texture: swappable
  wall_skin: swappable
  decor: optional
  damage: optional
  openings: generated
```

The important thing: a part knows what it depicts and where other things can connect.

## 3. Ports and joins

Connections should be explicit.

Examples:

```text
north_wall_opening(width_chunks=4, offset_chunks=2)
east_room_connector(width_chunks=6)
vertical_r24_offshoot(opening_width_chunks=2/4/6)
bridge_between_platforms(length_chunks=N)
drop_off(edge=north/south/east/west)
boss_gate_skin(on_port=east, width_chunks=6)
```

Each port should know:

- which logical chunks it occupies;
- which glyph columns/rows it maps to;
- what needs to be removed from the base part;
- what connector/gate/wall cap glyphs need to be inserted;
- whether it is same-level, vertical/offshoot, bridge, hole, stairs, drop, etc.

## 4. Structure vs skin

The system should separate structure from visual skin.

### Structure examples

- room shell
- north wall
- east wall
- west wall
- floor grid
- horizontal corridor
- vertical/offshoot corridor R24
- bridge
- hole
- cliff/drop
- platform
- column/post
- boss gate

### Skin examples

- plain wall
- boss gate wall
- cracked wall
- wet wall
- columned wall
- broken wall
- hole cutout
- bridge plank texture
- stone floor texture
- dirt floor texture
- dripping ceiling
- special underside material: `;;;`, `^^`, `@@`, `xx`, etc.

A boss gate should not be a totally unrelated object if it shares the same structural opening. It should often be:

```text
structure: opening/connector
skin: boss_gate
```

## 5. Layered render model

Render in layers so pieces do not destructively overwrite each other accidentally.

Suggested layers:

1. empty/background
2. room/enclosure structure
3. floor texture
4. wall/edge/foundation lines
5. openings/cuts
6. connectors/corridors/bridges
7. posts/caps/corners
8. decor/skin overlays
9. labels/debug annotations, optional

Each glyph can carry provenance:

```text
char: j
source_part: room2_north_opening
layer: connector_caps
logical_coord: room2.north.chunk6.right_corner
```

This makes debugging much easier than asking “why is this random `j` here?”

## 6. Openings must be chunk-based

The current north-wall issue shows why openings cannot be arbitrary character edits.

Room 2 north wall currently has 8 chunks:

```text
,— -,— -,— -,— -,— -,— -,— -,— -.
 1   2   3   4   5   6   7   8
```

So an opening should be defined like:

```yaml
wall: north
start_chunk: 3
width_chunks: 4
left_cap: j
right_cap: t
```

Not like:

```text
blank columns 77-80
```

Character edits are okay for hand correction, but the generator needs logical chunk edits.

## 7. Parametric wall builder

Eventually a wall should be generated for any length:

```python
wall_north(length_chunks=8, openings=[Opening(start=3, width=4, skin='plain_connector')])
```

Possible render:

```text
,— -,— -j        ,t— -,— -.
,__/___/          t___/___/ |
```

The exact glyph vocabulary can change later, but the structure should remain:

```text
left wall run + left opening cap + opening span + right opening cap + right wall run + terminal cap
```

This same logic should apply to east/west/south walls, bridges, railings, fences, and platform edges.

## 8. Parts as generators, not static strings

The workflow should move from fixed snippets to parametric generators.

Stages:

1. Lock exact hand-drawn examples as references.
2. Extract fixed-width parts with metadata.
3. Identify logical chunks and ports.
4. Build parametric generators for one structure at a time.
5. Verify generated output exactly matches locked examples for known sizes.
6. Add skins as alternative render layers.
7. Add editor interaction once the grammar is reliable.

## 9. Editor direction: Townscaper-like builder

Ideal editor behavior:

- User chooses a tool: wall, room, corridor, opening, bridge, gate, hole, column, platform, decor.
- User drags across a logical grid.
- The system snaps to chunk/grid boundaries.
- The renderer picks correct caps, joins, corners, underside rows, and interior textures.
- User can swap skins after placement without rebuilding structure.

Example tools:

```text
Wall tool: drag from chunk A to chunk B; generate any length wall.
Opening tool: click wall chunks; convert selected span to opening.
Connector tool: drag from one port to another; choose horizontal/vertical/offshoot/bridge.
Skin tool: paint selected structure with boss_gate, cracked_wall, wet_wall, etc.
Decor tool: add columns, holes, drip-offs, banners, rubble.
```

## 10. Immediate next implementation target

The next practical step should be the north wall as a parametric part:

```python
render_north_wall(chunks=8, openings=[Opening(start=3, width=4, skin='r24_plain')])
```

This would let us test:

- 2-chunk opening;
- 3-chunk uneven opening;
- 4-chunk centered opening;
- 6-chunk wide opening with one wall chunk left on each side.

Once that works, connect it to the current three-room test and replace the hand-edited north-wall rows with generated rows.

## 11. Design rule

A glyph string is not a module unless the system knows:

1. what structure it represents;
2. where its logical boundaries are;
3. where its ports are;
4. how it joins other structures;
5. what can be swapped as skin/decor;
6. how it scales in chunks;
7. how to verify it against a locked visual reference.

That is the standard the modular system should move toward.
