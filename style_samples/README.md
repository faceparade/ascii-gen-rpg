# Style samples

This directory converts logical floor masks into reviewable Grammar v2 projections.

- `catalog.json` contains bulk geometry cases.
- `style_rules_v2.json` is the authoritative topology, projection, wall, and composition grammar.
- `style_rules.json` is a superseded compatibility pointer.
- `targets/` contains handcrafted golden fixtures.
- `output/` contains disposable generated review sheets and diagnostics.

A logical mask is not ASCII art. Each `#` is a floor section. Actor anchors, lattice intersections, background walls, foreground walls, and entities are projected as separate layers.
