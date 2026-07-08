#!/usr/bin/env python3
"""Test opening_skin.py."""
from opening_skin import OpeningSkin, plain_opening_skin

# Gap widths per the north-wall style:
#   top gap width      = 4 * width_chunks + 1
#   underside gap width = 4 * width_chunks
# Plain skin: top = j ... ,t ; underside = (spaces) ... t
#   (top_left="j" [1], top_right=",t" [2] -> inner = width-3)
#   (underside_left="" [0], underside_right="t" [1] -> inner = width-1)

def test_plain_skin() -> None:
    skin = plain_opening_skin()

    # 1-chunk opening: top width 5, underside width 4
    assert skin.render_top_gap(5) == "j  ,t", repr(skin.render_top_gap(5))
    assert skin.render_underside_gap(4) == "   t", repr(skin.render_underside_gap(4))

    # 2-chunk opening: top width 9, underside width 8
    assert skin.render_top_gap(9) == "j      ,t", repr(skin.render_top_gap(9))
    assert skin.render_underside_gap(8) == "       t", repr(skin.render_underside_gap(8))

    # 3-chunk opening: top width 13, underside width 12
    assert skin.render_top_gap(13) == "j          ,t", repr(skin.render_top_gap(13))
    assert skin.render_underside_gap(12) == "           t", repr(skin.render_underside_gap(12))
    print("OpeningSkin tests passed")


if __name__ == "__main__":
    test_plain_skin()
