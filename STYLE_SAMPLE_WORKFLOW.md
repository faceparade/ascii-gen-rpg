# Structure Sample and Style Review Workflow — Grammar v2

The floorplan is authoritative. ASCII wall art is a directional projection layered over that floorplan.

## Pipeline

1. **Floor topology** — each `#` is one walkable logical section.
2. **Corridor-band topology** — passage length, thickness, and room-wall margins are measured independently.
3. **Elevation topology** — optional non-negative height is stored separately for each floor section.
4. **Actor anchors** — projected at `(2 + 4x, 2 + 2y)` and remain tied to logical sections.
5. **Lattice intersections** — a backtick appears only where four neighboring floor sections meet.
6. **Directional walls** — north/east are background layers; south/west are foreground layers.
7. **Elevation projection** — positive-height components are projected over the floor using directional background and foreground faces.
8. **Junction classification** — bridge, corridor, T, cross, and enclosed-loop structures are identified from topology.
9. **Junction resolution** — approved motifs replace literal wall-layer collisions where needed.
10. **Entities** — placed from logical section coordinates, never inferred from visible wall glyphs.
11. **Composition** — foreground walls and elevation faces may hide an entity or display it in x-ray styling.

Approved fixtures live under `style_samples/targets/`. Unapproved visual cases remain under `style_samples/review/`.

## East-cap terminal spacing

An underside or hanging face that terminates directly into an east wall reserves one recessed blank column before the face slash:

```text
/__ /|
```

It must not collapse to:

```text
/___/|
```

This rule is shared by rooms, bridges, corridors, junctions, enclosed courtyards, and platform shells. Ordinary south-wall faces remain unchanged.

## Corridor-band semantics

A corridor is represented as a rectangular logical band rather than assuming a one-section opening.

For an east-west passage, the model records:

- `start_x..end_x`: passage length
- `start_y..end_y`: doorway thickness
- top and bottom room-wall margins at both ends

For a north-south passage, the model records:

- `start_y..end_y`: passage length
- `start_x..end_x`: doorway thickness
- left and right room-wall margins at both ends

Equal opposing margins indicate a centered opening. Unequal margins indicate an offset opening. Centering is descriptive metadata, not a validity requirement.

## Regression sequence

1. 1×1 section
2. 2×2 block
3. approved 4×4 room
4. approved L-shaped room
5. approved U-shaped courtyard
6. approved east-extending bridge
7. approved west-extending bridge
8. approved one-section horizontal corridor
9. approved centered vertical corridor
10. reviewing two-section-wide horizontal corridor
11. reviewing offset vertical corridor
12. approved south-branch T-junction
13. approved four-way cross-junction
14. approved enclosed rectangular corridor loop
15. approved irregular enclosed courtyard
16. paused centered raised-platform projection

## Reviewing two-section-wide horizontal corridor

`room-wide-horizontal-corridor-v2` uses this mask:

```text
###...###
###...###
#########
#########
###...###
###...###
```

Its corridor band spans logical `x=3..5`, `y=2..3`. It is three sections long and two sections thick. Both ends have equal two-section top and bottom margins, so the opening is centered. The literal projection is regression-locked for review, but the upper doorway, open interior row, and lower doorway are not yet approved art.

## Reviewing offset vertical corridor

`room-offset-vertical-corridor-v2` uses this mask:

```text
#######
#######
.#.....
.#.....
.#.....
#######
#######
```

The one-section passage occupies logical `x=1`, `y=2..4`. Each doorway has a one-section west margin and a five-section east margin. The existing vertical corridor logic accepts the opening without requiring it to be centered. The short-west/long-east doorway transitions remain under visual review.

## Approved irregular enclosed courtyard

`room-irregular-enclosed-void-v2` contains one connected 16-cell enclosed void with bounds `x=1..5`, `y=1..4`, but the component does not fill those rectangular bounds. Its exact 16-row stepped inner-boundary rendering is approved.

## Paused centered raised platform

The centered 3×3 platform topology and executable nested-shell draft remain regression-tested. Visual approval and actor/elevation interaction work are paused until wide and offset corridor openings are resolved.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
python generate_corridor_variation_review.py
```

GitHub Actions compiles all modules and runs the complete test suite once per pull-request update. Superseded runs are cancelled.

The branch remains draft and should be squashed before merge.
