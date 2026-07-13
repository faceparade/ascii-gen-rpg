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

Equal opposing margins indicate a centered opening. Unequal margins are valid. The margin pairs at opposite ends are independent, so a straight corridor may connect horizontally shifted room shells without bending. `room_shift_x` is positive when the lower room starts farther east.

A staggered corridor is a one-section-thick orthogonal path. It records the two opening positions, bend row, direction, path length, and all four room-wall margins.

## Approved corridor coverage

The exact approved target set now includes:

1. One-section horizontal corridor
2. One-section centered vertical corridor
3. Two-section-wide horizontal corridor
4. West-offset vertical corridor in aligned rooms
5. Straight vertical corridor between horizontally shifted rooms
6. Eastward staggered dogleg corridor
7. South-branch T-junction
8. Four-way cross-junction
9. Enclosed rectangular loop
10. Irregular enclosed courtyard

### Approved wide horizontal corridor

```text
###...###
###...###
#########
#########
###...###
###...###
```

The passage spans `x=3..5`, `y=2..3`, with length 3, thickness 2, and equal `2/2` margins at both room walls.

### Approved west-offset vertical corridor

```text
#######
#######
.#.....
.#.....
.#.....
#######
#######
```

The passage occupies `x=1`, `y=2..4`. Both openings have west/east margins `1/5`.

### Approved shifted rooms with straight corridor

```text
#######....
#######....
.....#.....
.....#.....
.....#.....
....#######
....#######
```

The corridor stays at `x=5`. The upper opening has margins `5/1`; the lower room shifts four sections east and the lower opening has margins `1/5`. There is no corridor bend.

### Approved eastward dogleg

```text
#######
#######
.#.....
.#.....
.#####.
.....#.
.....#.
#######
#######
```

The path connects an upper `1/5` opening to a lower `5/1` opening through one eastward bend on `y=4`.

## Reviewing two-section-wide vertical corridor

```text
########
########
...##...
...##...
...##...
########
########
```

The corridor spans `x=3..4`, `y=2..4`, with length 3, thickness 2, and equal `3/3` margins at both openings. The exact draft is stored at `style_samples/review/room-wide-vertical-corridor-v2.txt`.

Review focus:

- two-section upper doorway
- paired vertical wall faces
- interior backtick column
- two-section lower doorway

## Next corridor case

After the wide-vertical draft is approved or revised, add a corridor that is both multiple sections wide and offset within its adjoining room walls. Then add mirrored shifted-room and westward-dogleg regressions before resuming elevation.

## Paused centered raised platform

The centered 3×3 platform topology and executable nested-shell draft remain regression-tested. Visual approval and actor/elevation interaction work are paused until the remaining corridor-width cases are resolved.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
python generate_corridor_variation_review.py
```

GitHub Actions compiles all modules and runs the complete test suite once per pull-request update. Superseded runs are cancelled.

The branch remains draft and should be squashed before merge.
