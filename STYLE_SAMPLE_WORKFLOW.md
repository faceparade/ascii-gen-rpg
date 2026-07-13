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

## East-cap terminal spacing

An underside or hanging face that terminates directly into an east wall reserves one recessed blank column before the face slash:

```text
/__ /|
```

It must not collapse to `/___/|`. Ordinary south-wall faces remain unchanged.

## Corridor semantics

A straight corridor is a rectangular logical band. East-west passages record length, doorway thickness, and top/bottom room-wall margins. North-south passages record length, doorway thickness, and left/right margins.

Equal opposing margins indicate a centered opening. Unequal margins are valid. Margin pairs at opposite ends are independent, so a straight corridor may connect shifted room shells without bending. `room_shift_x` is positive when the lower room starts farther east.

A staggered corridor is a one-section-thick orthogonal path. It records both opening positions, bend row, direction, path length, and all four room-wall margins.

## Corridor phase complete

The exact approved target matrix covers:

1. One-section horizontal and centered vertical corridors.
2. Two-section-wide horizontal corridor.
3. One-section west-offset vertical corridor.
4. One-section straight corridors between rooms shifted east and west.
5. Eastward and westward dogleg corridors.
6. Centered two-section-wide vertical corridor.
7. West-offset and east-offset two-section-wide vertical corridors.
8. Two-section-wide straight corridor between shifted room shells.
9. T-junction, four-way crossing, enclosed loop, and irregular enclosed courtyard.

The wide-vertical family uses one approved treatment across centered, offset, and shifted-room placements: paired side faces with an interior backtick column. The rectangular-band classifier remains generic for thicknesses greater than two, but exact golden art currently covers thicknesses one and two.

## Batch approval rule

Symmetric or parameter-only variants no longer require separate manual review when all of the following hold:

- the topology classifier returns the expected semantic object;
- the variant changes only margins, mirror direction, or room origin;
- no new glyph collision or layer type appears;
- the literal rendering is stored as an exact golden target;
- the complete CI suite passes.

A case returns to visual review only when it introduces a new wall transition, layer interaction, or unresolved glyph collision.

## Single connected pre-elevation integration map

`connected_map_v2.py` embeds 23 approved structural variations in one cardinally connected logical map. Three horizontal gallery spines and one vertical backbone join the translated feature masks without overlapping them.

Confirmed properties:

- logical bounds: 140 × 54 sections;
- walkable floor: 1,258 sections;
- connectivity: one cardinal component;
- rendered output: 110 rows, maximum width 563;
- rendering SHA-256: `12da9aed6fd7264a297baa6a3d18cda0996b8d1b72e0eb894d889b91c27603b3`;
- elevation data: deliberately absent.

The map metadata and logical mask are stored at `style_samples/review/connected-map-v2.txt`. Generate the full projection with:

```bash
python generate_connected_map_review.py
```

This connected map requires manual visual approval before elevation work resumes.

## Elevation review policy

Elevation is not eligible for automatic batch approval. Every new elevation treatment must be shown for manual review before it becomes an approved target, including:

- centered platform shell artwork;
- actors standing on elevated floor;
- lower-floor actors behind south and west elevation faces;
- opaque, x-ray, and walls-removed visibility modes;
- irregular platform footprints;
- multiple elevation levels.

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
