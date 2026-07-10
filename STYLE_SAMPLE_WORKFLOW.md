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

The initial Grammar v2 regression set is:

1. 1×1 section — actor anchor, no lattice marker;
2. 2×2 block — one lattice intersection;
3. approved 4×4 room — exact rectangular wall grammar;
4. L-shaped room — concave edge extraction and incomplete lattice intersections.

For irregular rooms, boundary extraction and occlusion are authoritative now. Concave-corner glyph choices remain reviewable until a handcrafted L-shaped target is approved.

## Commands

```bash
pytest -q
python style_sample_system.py
python foreground_occlusion.py
```

Generated output may be overwritten. Files under `style_samples/targets` must not be overwritten by generators.
