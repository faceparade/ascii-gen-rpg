# Structure Sample and Style Review Workflow — Grammar v2

The logical terrain is authoritative. ASCII wall and cliff art is a directional projection layered over explicit topology.

## Pipeline

1. **Surface topology** — every rendered terrain surface is explicit.
2. **Walkable floor topology** — rooms and pathways are a subset of terrain surfaces.
3. **Corridor topology** — bands and orthogonal paths record length, width, bends, room shifts, and wall margins.
4. **Elevation topology** — every surface cell has an explicit non-negative height.
5. **Actor anchors** — projected at `(2 + 4x, 2 + 2y)` for walkable logical sections.
6. **Lattice intersections** — a backtick appears only where four neighboring floor sections meet.
7. **Cliff detection** — height transitions run from the higher surface toward the lower adjacent surface.
8. **Directional projection** — north/east faces use background layers; south/west faces use foreground layers.
9. **Junction resolution** — approved motifs replace literal layer collisions where required.
10. **Entities and composition** — foreground walls and cliff faces may hide actors or display x-ray styling.

Approved fixtures live under `style_samples/targets/`. Unapproved elevation concepts remain under `style_samples/review/`.

## Approved east-cap spacing

An underside or hanging face that terminates directly into an east wall reserves one recessed blank column:

```text
/__ /|
```

It must not collapse to `/___/|`. Ordinary south-wall faces remain unchanged.

## Structural phase complete

Exact targets cover rooms, courtyards, bridges, corridor widths and offsets, shifted room shells, mirrored doglegs, T-junctions, crossings, loops, and the organic connected dungeon.

The rectangular corridor topology accepts arbitrary positive thickness. Golden artwork currently covers thicknesses one and two.

Symmetric or parameter-only **non-elevation** variants may be promoted together when their topology, layers, exact targets, and full CI suite agree. Elevation never uses this shortcut.

## Reviewed correction promotion complete

- 22 approved correction files are reproduced exactly by shared renderers and promoted golden targets.
- Legacy catalog outcomes have review decision sidecars; no decisions are stale.
- `room-two-by-two-v2` is approved. Its former mislabeled 4 × 4 draft was replaced with topology-correct 2 × 2 output and promoted as a golden target.
- The exact-output regression suite and GitHub Actions are green.

## Approved organic dungeon

`connected_map_v2.py` embeds all 23 approved structural variations in one cardinally connected dungeon.

- Logical bounds: 85 × 68 sections
- Walkable floor: 966 sections
- Connected components: one
- Longest horizontal floor run: 24 sections
- Projection: 138 rows, maximum width 343
- Rendering SHA-256: `a1384a9e0167bda6e834eff6f8332ad61e600d9daa1fbfec5df92f8fb9eff819`
- Elevation: intentionally absent from this target

Metadata is stored at `style_samples/targets/connected-map-v2.txt`.

## Primary elevation model

Rooms and pathways occupy a lower plane cut into an explicit higher terrain plane.

Authoritative rules:

- surface occupancy, elevation, and walkability are separate data;
- every rendered surface has an explicit elevation;
- blank ASCII space alone means neither terrain nor void;
- a cliff exists only between defined adjacent surfaces of different heights;
- the cliff descends from the higher surface toward the lower surface;
- absent neighbors do not create implicit walls;
- crop continuation is topology, not post-render character deletion;
- freestanding raised platforms use their own open-floor elevation renderer and approved target.

The user-authored conceptual reference remains at:

`style_samples/review/sunken-terrain-reference-v2.txt`

## Approved first terrain-cut fixture

Surface:

```text
#######
#######
#######
#######
#######
```

Elevation:

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
- 23 level-1 surfaces;
- 17 directed cliff edges.

The topology target is:

`style_samples/targets/sunken-corridor-chamber-v2.txt`

The approved user-authored cliff projection is:

```text
      ,— —,— —,— —,— —,
      |__/___/___/__ /|
      |   ,— — — — —'—'
      |  /|
      | ‘ |
      | |/|
      | | |
      | |/|
      | | |
      | |/|
      '—'—'
```

Its golden target is:

`style_samples/targets/sunken-corridor-chamber-cliff-art-v2.txt`

The rejected room-shell-based attempt remains archived under `style_samples/review/` and must not be reused.

## Active elevation checkpoint: mirrored cliff corners

Completed and locked byte-for-byte:

1. **Inside corner:** `sunken-inside-cliff-corner-v2` defines a 5 × 5 level-0 east-to-south L-turn around level-1 terrain.
2. **Outside corner:** `sunken-outside-cliff-corner-v2` defines a 5 × 5 level-1 shelf projecting south into the lower plane.
3. **Freestanding platform:** `room-raised-platform-v2` defines a centered 3 × 3 level-1 platform on an open 5 × 5 lower-floor canvas, without perimeter room walls or a decorative doorway.

The active manual-review sequence is now:

1. Mirrored cliff-corner variants derived from the approved inside/outside treatments.
2. Corner joins adjoining an open corridor shoulder.
3. A sunken T- or cross-junction.
4. Elevation applied to a region of the organic dungeon.
5. Actors on lower and upper planes and behind foreground cliffs.
6. Opaque, x-ray, and walls-removed modes.
7. Irregular footprints and multiple elevation levels.

Only one new elevation concept is introduced at each checkpoint.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
python generate_connected_map_review.py
```

GitHub Actions compiles all modules and runs the complete test suite once per pull-request update. Superseded runs are cancelled.

The branch remains draft and should be squashed before merge.
