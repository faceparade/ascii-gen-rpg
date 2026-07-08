#!/usr/bin/env python3
"""Quick test of geometry.py primitives."""
from geometry import RoomSpec, WallSpan, PortSpec, ChunkGrid

def test_room_spec():
    r = RoomSpec(width_chunks=8, height_chunks=5)
    assert r.width_chunks == 8
    assert r.height_chunks == 5
    print("RoomSpec OK")

def test_wall_span():
    ws = WallSpan(side="north", start_chunk=3, length_chunks=4)
    assert ws.side == "north"
    assert ws.start_chunk == 3
    assert ws.length_chunks == 4
    assert ws.end_chunk == 6
    assert ws.contains(3) == True
    assert ws.contains(6) == True
    assert ws.contains(2) == False
    assert ws.contains(7) == False
    print("WallSpan OK")

def test_port_spec():
    p = PortSpec(side="north", start_chunk=3, end_chunk=6)
    assert p.side == "north"
    assert p.start_chunk == 3
    assert p.end_chunk == 6
    assert p.length_chunks == 4
    p2 = PortSpec(side="north", start_chunk=5, end_chunk=8)
    assert p.overlaps(p2) == True
    p3 = PortSpec(side="north", start_chunk=1, end_chunk=2)
    assert p.overlaps(p3) == False
    p4 = PortSpec(side="south", start_chunk=3, end_chunk=6)
    assert p.overlaps(p4) == False  # different side
    print("PortSpec OK")

def test_chunk_grid():
    cg = ChunkGrid(chunks_wide=8, chunks_high=5)
    assert cg.chunks_wide == 8
    assert cg.chunks_high == 5
    assert cg.north_wall_top_width(8) == 8*4 + 1  # 33
    assert cg.north_wall_underside_width(8) == 8*4 + 2  # 34
    x0, x1 = cg.chunk_to_glyph_span(1, 8)
    assert x0 == 0
    assert x1 == 32  # 0..32 inclusive = 33 glyphs
    print("ChunkGrid OK")

if __name__ == "__main__":
    test_room_spec()
    test_wall_span()
    test_port_spec()
    test_chunk_grid()
    print("All geometry tests passed")