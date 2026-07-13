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

The exact approved target matrix now covers:

1. One-section horizontal and centered vertical corridors.
2. Two-section-wide horizontal corridor.
3. One-section west-offset vertical corridor.
4. One-section straight corridor between rooms shifted east.
5. Mirrored one-section straight corridor between rooms shifted west.
6. Eastward and westward dogleg corridors.
7. Centered two-section-wide vertical corridor.
8. West-offset and east-offset two-section-wide vertical corridors.
9. Two-section-wide straight corridor between shifted room shells.
10. T-junction, four-way crossing, enclosed loop, and irregular enclosed courtyard.

The wide-vertical family uses one approved treatment across centered, offset, and shifted-room placements: paired side faces with an interior backtick column. The rectangular-band classifier remains generic for thicknesses greater than two, but exact golden art currently covers thicknesses one and two.

## Batch approval rule

Symmetric or parameter-only variants no longer require separate manual review when all of the following hold:

- the topology classifier returns the expected semantic object;
- the variant changes only margins, mirror direction, or room origin;
- no new glyph collision or layer type appears;
- the literal rendering is stored as an exact golden target;
- the complete CI suite passes.

A case returns to visual review only when it introduces a new wall transition, layer interaction, or unresolved glyph collision. This keeps the workflow from repeating one-case-at-a-time approval for mechanically equivalent geometry.

## Active phase: centered raised platform

The centered 3×3 platform topology and executable nested-shell draft are regression-tested. Corridor work is no longer blocking elevation.

Next elevation steps:

1. Approve or revise the centered platform shell.
2. Test an actor standing on the platform.
3. Test lower-floor actors behind south and west platform faces.
4. Verify opaque, x-ray, and walls-removed visibility modes.
5. Generalize projection to irregular platform footprints.
6. Add multiple elevation levels.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
python generate_corridor_variation_review.py
```

GitHub Actions compiles all modules and runs the complete test suite once per pull-request update. Superseded runs are cancelled.

The branch remains draft and should be squashed before merge.
