# Structure Sample and Style Review Workflow

This workflow separates bulk geometry generation from handcrafted ASCII styling. Generated drafts may be replaced at any time. Approved targets remain stable until deliberately edited.

## Core loop

1. Define a logical floor-section mask in `style_samples/catalog.json`.
2. Generate a mask, automatic draft, and optional handcrafted target side by side.
3. Edit only the target under `style_samples/targets/`.
4. Mark the sample `approved` when it represents the intended style.
5. Promote recurring corrections into `style_samples/style_rules.json`.

## Review states

- `generated`: automatic draft exists.
- `reviewing`: target is being edited or decisions remain.
- `approved`: target is accepted as a reference.
- `promoted`: its reusable rule has been encoded and tested.

## Floor-section geometry

Each `#` represents one usable floor section and one possible character position. A section has an inclusive 5-column by 3-row footprint. Adjacent sections share their outside edge, so origins advance by 4 columns and 2 rows. The backtick sits at the local center `(2, 1)`.

## Rectangular projected room shell

The source room is not a flat outline. For `N` usable floor sections across and `M` down:

- centered indicators begin at glyph `(3, 3)` and repeat every `(4, 2)`;
- the north rim contains `N + 1` repeated `,— —` spans followed by `,.`;
- the underside starts with `|__`, repeats `/___`, and ends with `/ |`;
- the inner east wall is at `4N + 3`;
- the east face uses `/` on section-boundary rows and a space on center rows;
- the outer east edge is two glyphs to the right of the inner wall;
- a final east-wall boundary row appears before the south edge.

This relationship is visible in `six_rooms_two_platforms.txt`: seven floor indicators sit beneath eight north-wall spans.

A 4-by-2 room therefore contains eight possible centered character indicators and five north-wall spans. The fifth span moves the recessed east wall beyond the fourth indicator instead of occupying it.

## Files

- `style_sample_system.py`: mask validation and draft generation.
- `style_samples/catalog.json`: geometry cases.
- `style_samples/targets/<id>.txt`: handcrafted targets.
- `style_samples/style_rules.json`: confirmed reusable rules.
- `style_samples/output/`: generated review sheets and manifest.

Run:

```bash
python style_sample_system.py
pytest -q
```

Rectangular rooms now use the confirmed north/east projection. Irregular rooms, connections, and platforms still use the coarse shared-edge footprint renderer until their projection and junction rules are approved.
