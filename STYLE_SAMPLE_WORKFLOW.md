# Structure Sample and Style Review Workflow — Grammar v2

The floorplan is authoritative. ASCII wall art is a directional projection layered over that floorplan.

## Pipeline

1. **Floor topology** — each `#` is one walkable logical section.
2. **Elevation topology** — optional non-negative height is stored separately for each floor section.
3. **Actor anchors** — projected at `(2 + 4x, 2 + 2y)` and remain tied to logical sections.
4. **Lattice intersections** — a backtick appears only where four neighboring floor sections meet.
5. **Directional walls** — north/east are background layers; south/west are foreground layers.
6. **Junction classification** — bridge, corridor, T, cross, and enclosed-loop structures are identified from topology.
7. **Junction resolution** — approved motifs replace literal wall-layer collisions where needed.
8. **Entities** — placed from logical section coordinates, never inferred from visible wall glyphs.
9. **Composition** — foreground walls and elevation faces may hide an entity or display it in x-ray styling.

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

This is a renderer-level rule shared by rooms, bridges, corridors, junctions, and enclosed courtyards. Ordinary south-wall faces remain unchanged.

## Regression sequence

1. 1×1 section
2. 2×2 block
3. approved 4×4 room
4. approved L-shaped room
5. approved U-shaped courtyard
6. approved east-extending bridge
7. approved west-extending bridge
8. approved horizontal corridor
9. approved vertical corridor
10. approved south-branch T-junction
11. approved four-way cross-junction
12. approved enclosed rectangular corridor loop
13. approved irregular enclosed courtyard
14. reviewing centered raised platform

## Approved irregular enclosed courtyard

`room-irregular-enclosed-void-v2` contains one connected 16-cell enclosed void with bounds `x=1..5`, `y=1..4`, but the component does not fill those rectangular bounds. Its exact 16-row stepped inner-boundary rendering is approved.

## Reviewing centered raised platform

`room-raised-platform-v2` uses a 5×5 walkable floor and a separate elevation map:

```text
00000
01110
01110
01110
00000
```

The centered 3×3 platform is one connected elevation-1 component with 12 exposed directional perimeter edges. Actor anchors remain unchanged. North/east platform faces are background; south/west faces are foreground. Projection glyphs remain under review.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
```

The branch remains draft and should be squashed before merge.
