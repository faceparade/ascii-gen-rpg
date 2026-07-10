# Handcrafted targets

Each `<sample-id>.txt` file is an authoritative visual target. Generation must never overwrite these files.

`room-foreground-walls-on.txt` and `room-foreground-south-west-off.txt` are a paired reference: the floor projection remains stable while the south and west foreground faces are toggled. `foreground_occlusion.py` uses the pair for entity visibility tests.
