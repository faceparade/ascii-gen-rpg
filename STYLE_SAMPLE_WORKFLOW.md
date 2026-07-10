# Structure Sample and Style Review Workflow — Grammar v2

The floorplan is authoritative. ASCII wall art is a directional projection layered over that floorplan.

## Pipeline

1. **Floor topology** — each `#` is one walkable logical section.
2. **Actor anchors** — projected at `(2 + 4x, 2 + 2y)`.
3. **Lattice intersections** — a backtick appears only where four neighboring floor sections meet.
4. **Directional walls** — north/east are background layers; south/west are foreground layers.
5. **Entities** — placed from logical section coordinates, never inferred from visible wall glyphs.
6. **Composition** — foreground walls may hide an entity or display it in x-ray styling.

The authoritative machine-readable rules are in `style_samples/style_rules_v2.json`. The former `style_rules.json` is retained only as a compatibility pointer.

## Confirmed reference

`style_samples/targets/foreground_occlusion_v2.txt` is the approved 4×4 wall and occlusion fixture. It establishes:

- actor anchors use a 4×2 stride beginning at screen coordinate `(2, 2)`;
- backticks are shared interior lattice intersections, not actor anchors;
- west walls occlude sections with exposed west edges;
- south walls occlude sections with exposed south edges;
- east walls sit beyond centered one-character actors;
- deleting south/west walls reveals the unchanged underlying floorplan.

## Review sequence

The current Grammar v2 regression set is:

1. 1×1 section — actor anchor, no lattice marker;
2. 2×2 block — one lattice intersection;
3. approved 4×4 room — exact rectangular wall grammar;
4. approved L-shaped room — one-sided concave edge transitions;
5. approved U-shaped room — mirrored courtyard walls meeting an interior bridge;
6. approved one-sided bridge — one terminating inner wall meeting an exterior-ended bridge.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
```

Generated output may be overwritten. Files under `style_samples/targets` must not be overwritten by generators.

## Approved irregular-room fixture

The minimal L-shaped fixture `room-l-shape-v2` is approved. Its north run, west foreground run, concave east start, exterior south-face start, and concave south-face start are generated from directional boundary runs.

## Approved courtyard-bridge fixture

The U-shaped fixture `room-u-shape-v2` is approved. Its interior north run is recognized as a courtyard bridge when it is flanked by an exposed east wall on the left and an exposed west wall on the right, with empty courtyard cells above. The bridge rim is repainted above both vertical walls, and its underside uses a hanging `‘/___.../` face that clears the terminated wall caps.

## Approved one-sided bridge fixture

The asymmetric fixture `room-one-sided-bridge-v2` is approved. Its interior north run is recognized when an exposed east wall terminates immediately to the left, the notch cells above are empty, and the bridge’s rightmost floor section has an exposed exterior east edge. The renderer applies the approved left half of the courtyard-bridge face and preserves the normal exterior east cap.

More complex mirrored, multi-level, doorway, corridor, and platform junctions remain reviewable until their handcrafted targets promote reusable motifs.
