# Structure Sample and Style Review Workflow

This workflow separates bulk geometry generation from handcrafted ASCII styling.
The generator may be replaced or improved at any time. Approved target art must
remain stable until it is deliberately edited.

## Objectives

1. Generate the bulk silhouette of rooms, corridors, platforms, and voids.
2. Compare the logical mask, automatic draft, and handcrafted target together.
3. Record which examples have been reviewed and approved.
4. Promote recurring corrections into reusable style rules or motifs.
5. Retain `six_rooms_two_platforms.txt` as a high-level reference and regression fixture.

## Files

- `style_sample_system.py` validates masks and generates review artifacts.
- `style_samples/catalog.json` is the source catalog of geometry cases.
- `style_samples/targets/<sample-id>.txt` contains optional handcrafted targets.
- `style_samples/style_rules.json` is the destination for approved reusable rules.
- `style_samples/output/sample_sheet.txt` is the terminal-friendly comparison sheet.
- `style_samples/output/sample_sheet.html` is the visual comparison sheet.
- `style_samples/output/review_manifest.json` summarizes review state.

Generated output can be overwritten. Files under `style_samples/targets` must not
be overwritten by the generator.

## Review states

- `generated`: the geometry case exists and has an automatic draft.
- `reviewing`: a target is being edited or the sample needs decisions.
- `approved`: the target is an accepted reference for the current style.
- `promoted`: the useful correction has been encoded as a reusable rule or motif.

Status belongs in `catalog.json`. A target file alone does not imply approval.

## Run the generator

```bash
python style_sample_system.py
```

The default command reads `style_samples/catalog.json` and writes the three
files under `style_samples/output`.

Run tests with:

```bash
pytest -q
```

## Add a geometry case

Add one object to `style_samples/catalog.json`:

```json
{
  "id": "room-new-shape",
  "title": "New room shape",
  "category": "irregular-room",
  "mask": [
    "#####...",
    "########",
    "...#####"
  ],
  "tags": ["concave-corner"],
  "notes": "What this sample is intended to test.",
  "status": "generated"
}
```

`#` is occupied structure, while `.` or a space is empty. Masks are normalized
to their occupied upper-left boundary.

## Handcraft a target

Create `style_samples/targets/<sample-id>.txt`. The file contains only the
intended ASCII rows. It may differ in dimensions from the automatic draft.
Regenerate the sheet and compare all three columns.

### Confirmed floor-grid invariant

Backticks on open floor are grid markers, not free decoration. With the current
projection, logical sections are four columns wide and two rows high. A marker
is placed one glyph left and one glyph below a fully interior logical grid
vertex. In a solid 4-by-3 room this yields three markers across on each of two
interior grid rows. Boundary-corner backticks are separate structural glyphs.

Keep edits local to one structural problem when possible. A small, clear target
is easier to convert into a reusable rule than an entire completed level.

## Promote approved work

Before promoting a target, identify the smallest recurring concept represented
by the correction:

- glyph preference
- straight-edge rhythm
- convex corner
- concave corner
- opening cap
- wall-to-corridor junction
- raised-platform edge or face
- multi-cell motif

Record the rule in `style_samples/style_rules.json`, add a test, then mark the
sample `promoted`. Large one-off structures may remain approved targets without
becoming rules.

## Development sequence

1. Bulk orthogonal masks and boundary extraction.
2. Separate semantic wall, floor, void, and platform layers.
3. Openings, corridors, and routed connections.
4. Elevated surfaces and visible faces.
5. Shape-aware glyph profiles based on the chosen monospace font.
6. Neighbor-aware glyph selection and reusable junction motifs.
7. Full procedural level generation using approved style rules.

The first generator is intentionally coarse. It proves the review process and
provides editable bulk shapes before more sophisticated projection and glyph
selection are added.
