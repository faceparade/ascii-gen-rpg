from __future__ import annotations

from pathlib import Path


EXPECTED_T_JUNCTION = """
     ,— —,— —,— —,— —,— —,— —,— —,— —,— —,— —,
     |__/___/___/___/___/___/___/___/___/___/_
     |
     |
— — — — — — — — —. |          ,— — — — —'—'
                 | |/        /|
                 | |        ‘ |
                 | |/       |/|
                 | |        | |
                 | |/       |/|
                 | |        | |
                 | |/       |/|
                 | |        '—'
                 | |/
"""


def test_transparent_stamp_arranges_fragments_without_spaces_erasing_existing_art() -> None:
    from terrain_art_composer_v2 import transparent_stamp

    canvas = [list("abc"), list("def")]

    transparent_stamp(canvas, [" X ", "Y "], x=0, y=0)

    assert ["".join(row) for row in canvas] == ["aXc", "Yef"]


def test_sunken_t_junction_composes_two_approved_inside_corners_under_one_rim() -> None:
    from terrain_art_composer_v2 import T_JUNCTION_SOURCES, render_sunken_t_junction

    root = Path(__file__).parent
    artwork = render_sunken_t_junction(root)

    assert artwork == EXPECTED_T_JUNCTION
    assert T_JUNCTION_SOURCES == (
        "sunken-mirrored-inside-cliff-corner-v2.txt",
        "sunken-inside-cliff-corner-v2.txt",
    )
    assert [len(row) for row in artwork.splitlines()] == [
        0, 46, 46, 6, 6, 43, 31, 31, 31, 31, 31, 31, 31, 31, 21
    ]
    for source_name in (*T_JUNCTION_SOURCES, "sunken-open-corridor-shoulder-v2.txt"):
        source = (root / "style_samples/targets" / source_name).read_text(encoding="utf-8")
        assert artwork != source
