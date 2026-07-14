from __future__ import annotations

import json
from pathlib import Path

import pytest

from style_sample_system import (
    ShapeSample,
    cells_from_mask,
    render_sample_draft,
)


ROOT = Path(__file__).parent
CATALOG = ROOT / "style_samples" / "catalog_v2.json"
DECISIONS = ROOT / "style_samples" / "decisions"
CORRECTIONS = ROOT / "style_samples" / "corrections"


def approved_corrected_samples() -> list[tuple[ShapeSample, tuple[str, ...]]]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    samples_by_id = {item["id"]: item for item in catalog["samples"]}
    approved: list[tuple[ShapeSample, tuple[str, ...]]] = []
    for decision_path in sorted(DECISIONS.glob("*.json")):
        record = json.loads(decision_path.read_text(encoding="utf-8"))
        if record.get("decision") != "approved" or not record.get("correction"):
            continue
        item = samples_by_id[record["sample_id"]]
        # This parameterized check exercises the ordinary ShapeSample renderer.
        # Elevation corrections have dedicated terrain-cut golden tests.
        if "mask" not in item:
            continue
        sample = ShapeSample(
            sample_id=item["id"],
            title=item["title"],
            category=item["category"],
            mask=tuple(item["mask"]),
            tags=tuple(item.get("tags", [])),
            notes=item.get("notes", ""),
            status=item.get("status", "generated"),
        )
        correction = tuple(
            (ROOT / "style_samples" / record["correction"])
            .read_text(encoding="utf-8")
            .splitlines()
        )
        approved.append((sample, correction))
    return approved


APPROVED_CORRECTED_SAMPLES = approved_corrected_samples()


@pytest.mark.parametrize(
    ("sample", "approved_output"),
    APPROVED_CORRECTED_SAMPLES,
    ids=[sample.sample_id for sample, _ in APPROVED_CORRECTED_SAMPLES],
)
def test_renderer_reproduces_approved_corrected_output(
    sample: ShapeSample,
    approved_output: tuple[str, ...],
) -> None:
    assert render_sample_draft(sample, cells_from_mask(sample.mask)) == approved_output
