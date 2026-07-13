# Structure Sample and Style Review Workflow — Grammar v2

The floorplan is authoritative. ASCII wall art is a directional projection layered over that floorplan.

## Pipeline

1. **Floor topology** — each `#` is one walkable logical section.
2. **Actor anchors** — projected at `(2 + 4x, 2 + 2y)`.
3. **Lattice intersections** — a backtick appears only where four neighboring floor sections meet.
4. **Directional walls** — north/east are background layers; south/west are foreground layers.
5. **Junction classification** — bridge, corridor, T, and crossing structures are identified from topology.
6. **Junction resolution** — approved motifs replace literal wall-layer collisions when needed.
7. **Entities** — placed from logical section coordinates, never inferred from visible wall glyphs.
8. **Composition** — foreground walls may hide an entity or display it in x-ray styling.

The authoritative machine-readable rules are in `style_samples/style_rules_v2.json`.

## Regression sequence

1. 1×1 section — actor anchor, no lattice marker.
2. 2×2 block — one lattice intersection.
3. Approved 4×4 room — directional walls and occlusion.
4. Approved L-shaped room — concave edge transitions.
5. Approved U-shaped room — mirrored courtyard bridge.
6. Approved east-extending one-sided bridge.
7. Approved west-extending one-sided bridge.
8. Approved horizontal corridor.
9. Approved vertical corridor.
10. Approved south-branch T-junction.
11. Reviewing four-way corridor crossing.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
```

Approved fixtures live under `style_samples/targets/`. Unapproved visual cases remain under `style_samples/review/`.

## Approved corridor and junction fixtures

The horizontal corridor intentionally reuses the hanging `‘/___.../` upper junction face while retaining its foreground south wall.

The vertical corridor retains its literal upper and lower doorway transitions. Its west wall is foreground and its east wall is background.

The south-branch T-junction retains its literal center and lower-room doorway transitions. The junction center is unobscured; descending branch sections are occluded only by their west wall. Its exact output is locked at `style_samples/targets/room-t-junction-v2.txt`.

## Reviewing four-way crossing

The fixture `room-cross-junction-v2` uses this mask:

```text
..#####..
..#####..
....#....
....#....
#########
....#....
....#....
..#####..
..#####..
```

`cross_junction_grammar_v2.py` identifies the logical center when all four cardinal neighbors are occupied and all four diagonals are empty. This excludes ordinary room interiors.

Confirmed semantics:

- center section `(4,4)` has no foreground occluder;
- vertical arm sections are occluded by their west wall only;
- horizontal arm sections are occluded by their south wall;
- the far-west horizontal section is occluded by both west and south walls.

The literal 20-row rendering remains under review at `style_samples/review/room-cross-junction-v2.txt`.

## Remaining work

- approve or edit the four-way center and arm transitions;
- add entity movement and x-ray fixtures across approved junctions;
- define raised-platform projection;
- run the complete suite and squash the feature branch before merge.
