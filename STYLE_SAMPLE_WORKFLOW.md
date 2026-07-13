# Structure Sample and Style Review Workflow — Grammar v2

The logical terrain is authoritative. ASCII wall and cliff art is a directional projection layered over explicit topology.

## Pipeline

1. **Surface topology** — every rendered terrain surface is explicit.
2. **Walkable floor topology** — rooms and pathways are a subset of terrain surfaces.
3. **Corridor topology** — rectangular bands and one-section orthogonal paths record length, thickness, bends, room shifts, and wall margins.
4. **Elevation topology** — every surface cell has an explicit non-negative height.
5. **Actor anchors** — projected at `(2 + 4x, 2 + 2y)` for walkable logical sections.
6. **Lattice intersections** — a backtick appears only where four neighboring floor sections meet.
7. **Cliff detection** — height transitions are directed from the higher surface toward the lower adjacent surface.
8. **Directional walls and cliff faces** — north/east are background layers; south/west are foreground layers.
9. **Junction resolution** — approved motifs replace literal layer collisions where needed.
10. **Entities** — placed from logical section coordinates and elevation.
11. **Composition** — foreground walls and cliff faces may hide an entity or display it in x-ray styling.

Approved fixtures live under `style_samples/targets/`. Unapproved visual cases remain under `style_samples/review/`.

## Approved east-cap spacing

An underside or hanging face that terminates directly into an east wall reserves one recessed blank column before the face slash:

```text
/__ /|
```

It must not collapse to `/___/|`. Ordinary south-wall faces remain unchanged.

## Structural phase complete

Approved exact targets cover rooms, courtyards, bridges, corridor widths and offsets, shifted room shells, mirrored doglegs, T-junctions, four-way crossings, loops, and the organic connected dungeon.

The rectangular corridor topology accepts arbitrary positive thickness, while exact artwork is currently locked for thicknesses one and two.

## Batch approval rule for non-elevation geometry

Symmetric or parameter-only structural variants may be promoted without another visual stop when:

- the topology classifier returns the expected semantic object;
- only margins, mirror direction, or room origin changes;
- no new glyph collision or layer type appears;
- the literal rendering is stored as an exact golden target;
- the complete CI suite passes.

Elevation never uses this shortcut.

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

The approved metadata and digest are stored at `style_samples/targets/connected-map-v2.txt`.

## Primary elevation model: sunken paths in raised terrain

The dungeon’s primary elevation model is no longer a freestanding raised island. Rooms and pathways occupy the lower plane, while the surrounding terrain is an explicit higher plane.

Authoritative rules:

- surface occupancy, elevation, and walkability are separate data;
- every rendered surface has an explicit elevation;
- blank ASCII space alone means neither elevated ground nor void;
- a cliff exists only between two defined cardinally adjacent surfaces of different heights;
- the cliff is directed from the higher surface toward the lower surface;
- absent neighbors do not produce an implicit wall or cliff;
- the elevated plane may therefore continue beyond the south, east, or any other crop boundary without being boxed in;
- freestanding raised platforms remain a separate later treatment.

The user-authored visual reference is stored at:

`style_samples/review/sunken-terrain-reference-v2.txt`

## Active checkpoint: straight sunken corridor opening into a chamber

Surface mask:

```text
#######
#######
#######
#######
#######
```

Elevation map:

```text
1111111
1000111
1000000
1000111
1111111
```

Walkable lower plane:

```text
.......
.###...
.######
.###...
.......
```

Confirmed topology:

- 35 explicit terrain surfaces;
- 12 walkable level-0 cells;
- 23 level-1 surrounding surfaces;
- 17 directed cliff edges;
- no implicit wall at the crop edge;
- the eastbound corridor may continue beyond the review crop.

The topology record is stored at `style_samples/review/sunken-corridor-chamber-v2.txt`. The next manual checkpoint is the rendered cliff artwork for this exact fixture.

## Elevation review sequence

1. Render and approve the straight sunken corridor/chamber fixture.
2. Add inside and outside cliff corners.
3. Add a junction surrounded by elevated terrain.
4. Apply the approved cliff treatment to a region of the organic dungeon.
5. Review actors on the lower plane and behind foreground cliff faces.
6. Review opaque, x-ray, and walls-removed modes.
7. Review irregular cliff footprints and multiple elevation levels.
8. Return later to freestanding raised platforms.

Only one new visual concept is introduced at each checkpoint.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
python generate_connected_map_review.py
```

GitHub Actions compiles all modules and runs the complete test suite once per pull-request update. Superseded runs are cancelled.

The branch remains draft and should be squashed before merge.
