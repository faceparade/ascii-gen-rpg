# Style samples

`catalog.json` defines usable floor-section masks. Each `#` is one possible centered character position. The generator writes disposable comparisons to `output/`; handcrafted references belong in `targets/`.

`foreground_occlusion.py` treats floor topology, projected walls, entities, and occlusion as separate layers. Its HTML output shows entities behind walls in gray.
