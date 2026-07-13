# Structure Sample and Style Review Workflow — Grammar v2

The floorplan is authoritative. ASCII wall art is a directional projection layered over that floorplan.

## Pipeline

1. **Floor topology** — each `#` is one walkable logical section.
2. **Corridor topology** — rectangular bands and one-section orthogonal paths record length, thickness, bends, room shifts, and room-wall margins.
3. **Elevation topology** — optional non-negative height is stored separately for each floor section.
4. **Actor anchors** — projected at `(2 + 4x, 2 + 2y)` and remain tied to logical sections.
5. **Lattice intersections** — a backtick appears only where four neighboring floor sections meet.
6. **Directional walls** — north/east are background layers; south/west are foreground layers.
7. **Elevation projection** — positive-height components are projected over the floor using directional background and foreground faces.
8. **Junction classification** — bridge, corridor, T, cross, enclosed-loop, and dogleg structures are identified from topology.
9. **Junction resolution** — approved motifs replace literal wall-layer collisions where needed.
10. **Entities** — placed from logical section coordinates, never inferred from visible wall glyphs.
11. **Composition** — foreground walls and elevation faces may hide an entity or display it in x-ray styling.

Approved fixtures live under `style_samples/targets/`. Unapproved visual cases remain under `style_samples/review/`.

## Approved east-cap spacing

An underside or hanging face that terminates directly into an east wall reserves one recessed blank column before the face slash:

```text
/__ /|
```

It must not collapse to `/___/|`. Ordinary south-wall faces remain unchanged.

## Corridor phase complete

Approved exact targets cover:

- one-section horizontal and vertical corridors;
- centered and offset openings;
- rooms shifted east and west around a straight corridor;
- eastward and westward doglegs;
- two-section-wide horizontal and vertical corridors;
- centered, west-offset, east-offset, and shifted-room wide vertical corridors;
- T-junction, four-way crossing, enclosed loop, and irregular enclosed courtyard.

The rectangular-band topology accepts arbitrary positive thickness, while exact artwork is currently locked for thicknesses one and two.

## Batch approval rule for non-elevation geometry

Symmetric or parameter-only variants may be promoted without an additional visual stop when:

- the topology classifier returns the expected semantic object;
- only margins, mirror direction, or room origin changes;
- no new glyph collision or layer type appears;
- the literal rendering is stored as an exact golden target;
- the complete CI suite passes.

A case returns to manual review when it introduces a new wall transition, layer interaction, or unresolved glyph collision.

## Approved organic integration dungeon

`connected_map_v2.py` embeds all 23 approved structural variations in one organic cardinally connected dungeon.

Confirmed properties:

- logical bounds: 85 × 68 sections;
- walkable floor: 966 sections;
- connectivity: one cardinal component;
- longest horizontal floor run: 24 sections;
- rendered output: 138 rows, maximum width 343;
- rendering SHA-256: `51ca9dbef997129b449b6c32dfbe11e3d6932bdcb10fe2774e7fc03e45178ea6`;
- elevation data: deliberately absent.

The approved metadata and digest are stored at `style_samples/targets/connected-map-v2.txt`. Generate the full projection with:

```bash
python generate_connected_map_review.py
```

## Elevation review policy

Elevation is not eligible for automatic batch approval. Every new elevation treatment must be shown and explicitly approved before promotion.

Review sequence:

1. Centered rectangular platform shell.
2. Actor standing on elevated floor.
3. Lower-floor actors behind south and west elevation faces.
4. Opaque, x-ray, and walls-removed visibility modes.
5. Irregular platform footprints.
6. Multiple elevation levels.

Only one new visual concept should be introduced at each checkpoint.

## Active checkpoint: centered 3×3 platform shell

Floor mask:

```text
#####
#####
#####
#####
#####
```

Elevation map:

```text
00000
01110
01110
01110
00000
```

The topology is confirmed. Manual review is limited to the nested top rim, north/east background faces, south/west foreground faces, and platform-top lattice spacing. Actor rendering and multiple levels are not part of this checkpoint.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
python generate_corridor_variation_review.py
python generate_connected_map_review.py
```

GitHub Actions compiles all modules and runs the complete test suite once per pull-request update. Superseded runs are cancelled.

The branch remains draft and should be squashed before merge.
