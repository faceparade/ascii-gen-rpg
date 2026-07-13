# Structure Sample and Style Review Workflow — Grammar v2

The floorplan is authoritative. ASCII wall art is a directional projection layered over that floorplan.

## Pipeline

1. **Floor topology** — each `#` is one walkable logical section.
2. **Actor anchors** — projected at `(2 + 4x, 2 + 2y)`.
3. **Lattice intersections** — a backtick appears only where four neighboring floor sections meet.
4. **Directional walls** — north/east are background layers; south/west are foreground layers.
5. **Junction classification** — bridge, corridor, T, cross, and enclosed-loop structures are identified from topology.
6. **Junction resolution** — approved motifs replace literal wall-layer collisions where needed.
7. **Entities** — placed from logical section coordinates, never inferred from visible wall glyphs.
8. **Composition** — foreground walls may hide an entity or display it in x-ray styling.

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

This is a renderer-level rule shared by rectangular rooms, irregular rooms, bridges, corridors, T-junctions, cross-junctions, and enclosed loops. Ordinary south-wall faces that do not terminate in an east-wall pipe remain unchanged.

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
13. reviewing irregular enclosed courtyard

## Approved enclosed corridor loop

`room-enclosed-loop-v2` is a one-section-thick occupied ring around one rectangular enclosed void. Flood fill confirms the void cannot reach the exterior. The exact 16-row projection is approved, including all repeated inner/outer right-angle transitions and the recessed east-cap terminal motif.

## Reviewing irregular enclosed courtyard

`room-irregular-enclosed-void-v2` contains one connected enclosed void whose cells do not fill their rectangular bounds. It verifies that flood-fill detection generalizes beyond rectangular loops while leaving the stepped inner-boundary glyph transitions reviewable.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
```

The branch remains draft and should be squashed before merge.
