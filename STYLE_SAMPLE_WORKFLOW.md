# Structure Sample and Style Review Workflow — Grammar v2

The floorplan is authoritative. ASCII wall art is a directional projection layered over that floorplan.

## Pipeline

1. **Floor topology** — each `#` is one walkable logical section.
2. **Actor anchors** — projected at `(2 + 4x, 2 + 2y)`.
3. **Lattice intersections** — a backtick appears only where four neighboring floor sections meet.
4. **Directional walls** — north/east are background layers; south/west are foreground layers.
5. **Junction classification** — bridge and corridor spans are identified from topology and their left/right terminations.
6. **Junction resolution** — approved corner and bridge motifs replace literal wall-layer collisions.
7. **Entities** — placed from logical section coordinates, never inferred from visible wall glyphs.
8. **Composition** — foreground walls may hide an entity or display it in x-ray styling.

The authoritative machine-readable rules are in `style_samples/style_rules_v2.json`. The former `style_rules.json` is retained only as a compatibility pointer.

## Confirmed reference

`style_samples/targets/foreground_occlusion_v2.txt` is the approved 4×4 wall and occlusion fixture. It establishes:

- actor anchors use a 4×2 stride beginning at screen coordinate `(2, 2)`;
- backticks are shared interior lattice intersections, not actor anchors;
- west walls occlude sections with exposed west edges;
- south walls occlude sections with exposed south edges;
- east walls sit beyond centered one-character actors;
- deleting south/west walls reveals the unchanged floorplan.

## Review sequence

The current Grammar v2 regression set is:

1. 1×1 section — actor anchor, no lattice marker;
2. 2×2 block — one lattice intersection;
3. approved 4×4 room — exact rectangular wall grammar;
4. approved L-shaped room — one-sided concave edge transitions;
5. approved U-shaped room — mirrored courtyard walls meeting an interior bridge;
6. approved east-extending one-sided bridge — one terminating inner east wall and an exterior east cap;
7. approved west-extending one-sided bridge — an exterior west start and one terminating inner west wall;
8. reviewing horizontal corridor — two room openings joined by a one-section-high passage.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
```

Generated output may be overwritten. Files under `style_samples/targets` must not be overwritten by generators. Reviewing fixtures live under `style_samples/review/` until their glyph treatment is approved.

## Approved irregular-room fixture

The minimal L-shaped fixture `room-l-shape-v2` is approved. Its north run, west foreground run, concave east start, exterior south-face start, and concave south-face start are generated from directional boundary runs.

## Approved courtyard-bridge fixture

The U-shaped fixture `room-u-shape-v2` is approved. Its interior north run is recognized as a courtyard bridge when it is flanked by an exposed east wall on the left and an exposed west wall on the right, with empty courtyard cells above. The bridge rim is repainted above both vertical walls, and its underside uses a hanging `‘/___.../` face that clears the terminated wall caps.

## Approved east-extending one-sided bridge

The fixture `room-one-sided-bridge-v2` is recognized when an exposed east wall terminates immediately to the left, the notch cells above are empty, and the bridge’s rightmost floor section has an exposed exterior east edge. The renderer applies the approved left half of the courtyard-bridge face and preserves the normal exterior east cap.

## Approved west-extending one-sided bridge

The fixture `room-mirrored-one-sided-bridge-v2` is recognized when the bridge begins at an exposed exterior west edge, the notch cells above are empty, and an exposed west wall terminates immediately to its right. The renderer preserves the ordinary `/|__` exterior-west underside, applies the approved curved `‘—,` rim termination, and clears the inner west-wall cap beneath the final slash.

## Reviewing horizontal corridor

The fixture `room-horizontal-corridor-v2` contains two 3×5 rooms connected by a three-section, one-row-high passage. It differs from the U-shaped courtyard because matching side-wall segments continue below both openings. The shared junction classifier records this as `horizontal_corridor` rather than `courtyard_bridge`.

The corridor resolver keeps the joined north rim but restores the normal `/|__.../|` background underside. The south edge remains a foreground wall. The exact doorway transitions and south-face treatment remain reviewable in `style_samples/review/room-horizontal-corridor-v2.txt`.

Multi-level, nested, vertical-corridor, T-junction, doorway, and platform motifs remain reviewable until their handcrafted targets promote reusable rules.
