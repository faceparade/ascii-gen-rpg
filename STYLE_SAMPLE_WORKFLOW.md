# Structure Sample and Style Review Workflow — Grammar v2

The floorplan is authoritative. ASCII wall art is a directional projection layered over that floorplan.

## Pipeline

1. **Floor topology** — each `#` is one walkable logical section.
2. **Corridor topology** — rectangular bands and one-section orthogonal paths record length, thickness, bends, and room-wall margins.
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

It must not collapse to:

```text
/___/|
```

This rule is shared by rooms, bridges, corridors, junctions, enclosed courtyards, and platform shells. Ordinary south-wall faces remain unchanged.

## Corridor semantics

A straight corridor is represented as a rectangular logical band.

For an east-west passage, the model records passage length, doorway thickness, and top/bottom room-wall margins at both ends. For a north-south passage, it records passage length, doorway thickness, and left/right margins at both ends. Equal opposing margins indicate a centered opening. Unequal margins indicate a valid offset opening.

A staggered corridor is represented as a one-section-thick orthogonal path. It records the upper and lower opening positions independently, the bend row, direction of the horizontal shift, path length, and all four room-wall margins.

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
11. reviewing west-offset vertical corridor
12. reviewing staggered eastward dogleg corridor
13. approved south-branch T-junction
14. approved four-way cross-junction
15. approved enclosed rectangular corridor loop
16. approved irregular enclosed courtyard
17. paused centered raised-platform projection

## Reviewing two-section-wide horizontal corridor

`room-wide-horizontal-corridor-v2` uses:

```text
###...###
###...###
#########
#########
###...###
###...###
```

Its corridor band spans logical `x=3..5`, `y=2..3`. It is three sections long and two sections thick. Both ends have equal two-section top and bottom margins. The upper doorway, open interior row, and lower doorway remain review art.

## Reviewing offset vertical corridor

`room-offset-vertical-corridor-v2` uses:

```text
#######
#######
.#.....
.#.....
.#.....
#######
#######
```

The passage occupies logical `x=1`, `y=2..4`. Each doorway has west/east margins of `1/5`. Centering is not required.

## Reviewing staggered dogleg corridor

`room-staggered-dogleg-corridor-v2` uses:

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

The upper opening is at `x=1` with margins `1/5`; the lower opening is at `x=5` with margins `5/1`. The one-section path bends eastward on logical row `y=4`, shifts four columns, and contains nine logical sections. It is not a rectangular band. The two inside-corner transitions and the long middle passage remain under visual review.

## Approved irregular enclosed courtyard

`room-irregular-enclosed-void-v2` contains one connected 16-cell enclosed void with bounds `x=1..5`, `y=1..4`, but the component does not fill those rectangular bounds. Its exact 16-row stepped inner-boundary rendering is approved.

## Paused centered raised platform

The centered 3×3 platform topology and executable nested-shell draft remain regression-tested. Visual approval and actor/elevation interaction work are paused until corridor width, offset, and staggered-opening cases are resolved.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
python generate_corridor_variation_review.py
```

GitHub Actions compiles all modules and runs the complete test suite once per pull-request update. Superseded runs are cancelled.

The branch remains draft and should be squashed before merge.
