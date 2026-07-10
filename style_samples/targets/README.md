# Handcrafted targets

Create one UTF-8 text file per reviewed sample using the catalog sample ID:

```text
room-l-shape.txt
platform-island.txt
```

The entire file is treated as the intended target render. Do not add metadata
inside the target. Metadata and review status belong in `../catalog.json`.

The generator reads these files but never modifies them.
