from style_sample_system import cells_from_mask, render_irregular_room


def test_approved_l_shape_matches_concave_wall_target() -> None:
    cells = cells_from_mask(("###", "##.", "##."))
    assert render_irregular_room(cells) == (
        "  ,— —,— —,— —,",
        " /|__/___/___/|",
        "‘ |       ,—‘—,",
        "|/| `    /|__/",
        "| |     ‘ |",
        "|/| `   |/|",
        "| ,— —,—‘—,",
        "‘/___/___/",
    )
