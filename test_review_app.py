from __future__ import annotations

import json
import shutil
import subprocess
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from review_app import (
    PublishError,
    ReviewHTTPServer,
    ReviewState,
    StaleCandidateError,
    ValidationError,
    extract_artwork,
    safe_project_path,
    sha256_text,
)


CANDIDATE_ART = "  ,— —,\n  |__ /|\n"
REFERENCE_ART = "  ,— —,\n  |___/|\n"


def build_project(root: Path) -> None:
    (root / "style_samples/review").mkdir(parents=True)
    (root / "style_samples/targets").mkdir(parents=True)
    (root / "review_app.html").write_text("<!doctype html><title>test</title>", encoding="utf-8")
    (root / "review_grid_editor.js").write_text("export const editor = true;\n", encoding="utf-8")
    (root / "style_samples/review/sample-v2.txt").write_text(
        "SAMPLE — REVIEW\n\nAUTOMATIC DRAFT\n---------------\n"
        + CANDIDATE_ART
        + "\nSTATUS\n------\nManual review.\n",
        encoding="utf-8",
    )
    (root / "style_samples/review/reference-v2.txt").write_text(
        "REFERENCE\n\nREFERENCE PROJECTION\n--------------------\n"
        + REFERENCE_ART,
        encoding="utf-8",
    )
    (root / "style_samples/targets/structural-v2.txt").write_text(
        "completed structural target  \n",
        encoding="utf-8",
    )
    (root / "style_samples/targets/room-foreground-walls-on.txt").write_text(
        "completed room style reference\n",
        encoding="utf-8",
    )
    catalog = {
        "schema_version": 1,
        "samples": [
            {
                "id": "sample-v2",
                "title": "Sample",
                "category": "elevation",
                "status": "reviewing",
                "review": "review/sample-v2.txt",
                "reference_id": "reference-v2",
                "surface_mask": ["###"],
                "elevation_map": ["101"],
                "walkable_mask": [".#."],
            },
            {
                "id": "reference-v2",
                "title": "Reference",
                "category": "elevation",
                "status": "authoritative",
                "review": "review/reference-v2.txt",
            },
            {
                "id": "structural-v2",
                "title": "Approved structural sample",
                "category": "corridor",
                "status": "approved",
                "mask": ["##"],
            },
            {
                "id": "room-draft-v2",
                "title": "Room draft",
                "category": "room",
                "status": "reviewing",
                "mask": ["#"],
            },
        ],
    }
    (root / "style_samples/catalog_v2.json").write_text(
        json.dumps(catalog, ensure_ascii=False),
        encoding="utf-8",
    )


@pytest.fixture()
def project(tmp_path: Path) -> Path:
    build_project(tmp_path)
    return tmp_path


def test_extract_artwork_from_wrapped_review() -> None:
    wrapped = "HEADER\n\nAUTOMATIC DRAFT\n---------------\nabc  \ndef\n\nSTATUS\n------\nreview\n"
    assert extract_artwork(wrapped) == "abc  \ndef\n"


def test_current_output_panel_labels_geometry_as_reference() -> None:
    html = Path("review_app.html").read_text(encoding="utf-8")
    candidate_start = html.index('id="candidatePanel"')
    reference_start = html.index('id="referencePanel"')
    candidate_markup = html[candidate_start:reference_start]

    assert 'id="candidateShape"' in candidate_markup
    assert 'id="candidateShapeGrid"' in candidate_markup
    assert "Geometry reference — not an output preview" in candidate_markup
    assert "renderShapeKey(state.detail.shape_key)" in html


def test_review_html_exposes_cell_grid_editor_controls() -> None:
    html = Path("review_app.html").read_text(encoding="utf-8")

    assert 'type="module"' in html
    assert 'from "./review_grid_editor.js"' in html
    assert "Current output" in html
    assert "Style reference — shape may differ" in html
    assert "Text difference vs style reference" in html
    assert "state.detail.display_output" in html
    assert "state.detail.display_source" in html
    assert "state.detail.correction !== null" in html
    assert 'className = `shape-map-cell ${shapeCellClass(section.label, value)}`' in html
    assert 'class="shape-map-legend"' in html
    for element_id in (
        "gridEditorPanel",
        "gridEditorShape",
        "gridEditorShapeGrid",
        "gridCanvas",
        "glyphPalette",
        "gridPencil",
        "gridEraser",
        "gridUndo",
        "gridRedo",
        "gridInsertCell",
        "gridDeleteCell",
        "gridInsertRowAbove",
        "gridInsertRowBelow",
        "gridDeleteRow",
        "gridShortenRow",
        "gridLengthenRow",
        "saveGridCorrectionButton",
    ):
        assert f'id="{element_id}"' in html


def test_grid_editor_model_with_node() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is not installed")
    result = subprocess.run(
        [node, "--test", "test_review_grid_editor.mjs"],
        cwd=Path(__file__).parent,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_candidate_reference_and_row_lengths(project: Path) -> None:
    state = ReviewState(project)
    detail = state.sample_detail("sample-v2")
    assert detail["candidate"] == CANDIDATE_ART
    assert detail["reference"] == REFERENCE_ART
    assert detail["candidate_sha256"] == sha256_text(CANDIDATE_ART)
    assert detail["candidate_row_lengths"] == [7, 8]
    assert detail["candidate_leading_spaces"] == [2, 2]
    assert detail["correction"] is None
    assert detail["display_output"] == CANDIDATE_ART
    assert detail["display_source"] == "review/sample-v2.txt"
    assert detail["sample"]["elevation_map"] == ["101"]
    assert detail["shape_key"] == [
        {
            "label": "Surface",
            "rows": ["###"],
            "legend": "# = defined terrain · . = outside crop",
        },
        {
            "label": "Elevation",
            "rows": ["101"],
            "legend": "1 = upper plane · 0 = lower plane",
        },
        {
            "label": "Walkable",
            "rows": [".#."],
            "legend": "# = walkable lower plane · . = not walkable",
        },
    ]


def test_existing_empty_correction_remains_the_current_output(project: Path) -> None:
    correction = project / "style_samples/corrections/sample-v2.txt"
    correction.parent.mkdir(parents=True)
    correction.write_text("", encoding="utf-8")

    detail = ReviewState(project).sample_detail("sample-v2")

    assert detail["correction"] == ""
    assert detail["display_output"] == ""
    assert detail["display_source"] == "corrections/sample-v2.txt"
    assert detail["display_sha256"] == sha256_text("")
    assert detail["correction_sha256"] == sha256_text("")
    assert detail["display_row_lengths"] == []
    assert detail["display_leading_spaces"] == []


def test_completed_references_are_inferred_from_golden_targets(project: Path) -> None:
    state = ReviewState(project)

    structural = state.sample_detail("structural-v2")
    assert structural["candidate"] == "MASK\n##\n"
    assert structural["reference"] == "completed structural target  \n"
    assert structural["reference_source"] == "targets/structural-v2.txt"
    assert structural["editable_output"] == "completed structural target  \n"
    assert structural["editable_source"] == "targets/structural-v2.txt"

    room_draft = state.sample_detail("room-draft-v2")
    assert room_draft["reference"] == "completed room style reference\n"
    assert room_draft["reference_source"] == "targets/room-foreground-walls-on.txt"
    assert room_draft["editable_output"] == "completed room style reference\n"

    generated = state.sample_detail("sample-v2")
    assert generated["editable_output"] == CANDIDATE_ART
    assert generated["editable_source"] == "review/sample-v2.txt"


def test_correction_preserves_exact_spaces_and_newline(project: Path) -> None:
    state = ReviewState(project)
    candidate_hash = state.sample_detail("sample-v2")["candidate_sha256"]
    correction = "a  \n b\n"
    result = state.save_correction(
        "sample-v2",
        {"candidate_sha256": candidate_hash, "text": correction},
    )
    assert (project / result["correction"]).read_text(encoding="utf-8") == correction
    assert result["correction_sha256"] == sha256_text(correction)
    assert result["correction_source"] == "corrections/sample-v2.txt"
    assert result["correction_row_lengths"] == [3, 2]
    assert result["correction_leading_spaces"] == [0, 1]
    detail = state.sample_detail("sample-v2")
    assert detail["display_output"] == correction
    assert detail["display_source"] == "corrections/sample-v2.txt"


def test_decision_records_hash_and_correction(project: Path) -> None:
    state = ReviewState(project)
    candidate_hash = state.sample_detail("sample-v2")["candidate_sha256"]
    state.save_correction(
        "sample-v2",
        {"candidate_sha256": candidate_hash, "text": "fixed\n"},
    )
    record = state.save_decision(
        "sample-v2",
        {
            "candidate_sha256": candidate_hash,
            "decision": "needs_changes",
            "notes": "Keep the upper rim continuous.",
        },
    )
    assert record["decision"] == "needs_changes"
    assert record["candidate_sha256"] == candidate_hash
    assert record["correction"] == "corrections/sample-v2.txt"
    saved = json.loads(
        (project / "style_samples/decisions/sample-v2.json").read_text(encoding="utf-8")
    )
    assert saved == record


def test_stale_hash_blocks_decision(project: Path) -> None:
    state = ReviewState(project)
    with pytest.raises(StaleCandidateError):
        state.save_decision(
            "sample-v2",
            {"candidate_sha256": "0" * 64, "decision": "approved", "notes": ""},
        )


def test_path_traversal_is_rejected(project: Path) -> None:
    with pytest.raises(ValidationError):
        safe_project_path(project, "../outside.txt")


def test_publish_is_disabled_by_default(project: Path) -> None:
    state = ReviewState(project)
    assert state.git_status() == {"enabled": False}


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def initialize_git_project(root: Path, branch: str) -> None:
    git(root, "init", "-b", branch)
    git(root, "config", "user.name", "Review App Test")
    git(root, "config", "user.email", "review-app-test@example.invalid")
    git(root, "add", ".")
    git(root, "commit", "-m", "initial fixture")


def save_test_decision(state: ReviewState) -> None:
    candidate_hash = state.sample_detail("sample-v2")["candidate_sha256"]
    state.save_decision(
        "sample-v2",
        {"candidate_sha256": candidate_hash, "decision": "approved", "notes": ""},
    )


def test_publish_refuses_protected_branch(project: Path) -> None:
    initialize_git_project(project, "phase-2-layout-generation")
    state = ReviewState(project, enable_git_publish=True)
    save_test_decision(state)
    with pytest.raises(PublishError, match="protected branch"):
        state.publish_batch()


def test_publish_refuses_unrelated_staged_file(project: Path) -> None:
    initialize_git_project(project, "feature/review-app-test")
    (project / "unrelated.txt").write_text("do not commit\n", encoding="utf-8")
    git(project, "add", "unrelated.txt")
    state = ReviewState(project, enable_git_publish=True)
    save_test_decision(state)
    with pytest.raises(PublishError, match="Unrelated files"):
        state.publish_batch()
    assert git(project, "diff", "--cached", "--name-only") == "unrelated.txt"


def test_publish_commits_and_pushes_only_review_files(project: Path) -> None:
    initialize_git_project(project, "feature/review-app-test")
    remote = project.parent / "review-app-remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    git(project, "remote", "add", "origin", str(remote))
    git(project, "push", "-u", "origin", "feature/review-app-test")

    state = ReviewState(project, enable_git_publish=True)
    candidate_hash = state.sample_detail("sample-v2")["candidate_sha256"]
    state.save_correction(
        "sample-v2",
        {"candidate_sha256": candidate_hash, "text": "fixed exactly  \n"},
    )
    save_test_decision(state)

    result = state.publish_batch()
    assert result["published"] is True
    assert result["branch"] == "feature/review-app-test"
    assert set(git(project, "show", "--pretty=format:", "--name-only", "HEAD").splitlines()) == {
        "style_samples/corrections/sample-v2.txt",
        "style_samples/decisions/sample-v2.json",
    }
    assert git(project, "status", "--porcelain") == ""
    assert git(remote, "rev-parse", "refs/heads/feature/review-app-test") == result["commit_sha"]


def test_http_api_smoke(project: Path) -> None:
    state = ReviewState(project)
    server = ReviewHTTPServer(("127.0.0.1", 0), state)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with urllib.request.urlopen(f"{base}/api/config") as response:
            config = json.loads(response.read().decode("utf-8"))
        assert config["token"] == server.token

        with urllib.request.urlopen(f"{base}/review_grid_editor.js") as response:
            editor_module = response.read().decode("utf-8")
            assert response.headers.get_content_type() == "text/javascript"
        assert editor_module.splitlines() == ["export const editor = true;"]

        rebinding_request = urllib.request.Request(
            f"{base}/api/config",
            headers={"Host": "attacker.example"},
        )
        with pytest.raises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(rebinding_request)
        assert exc.value.code == 403

        with urllib.request.urlopen(f"{base}/api/sample/sample-v2") as response:
            detail = json.loads(response.read().decode("utf-8"))
        assert detail["candidate"] == CANDIDATE_ART

        request = urllib.request.Request(
            f"{base}/api/decision/sample-v2",
            method="POST",
            data=json.dumps(
                {
                    "candidate_sha256": detail["candidate_sha256"],
                    "decision": "approved",
                    "notes": "",
                }
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Review-Token": server.token,
            },
        )
        with urllib.request.urlopen(request) as response:
            decision = json.loads(response.read().decode("utf-8"))
        assert decision["decision"] == "approved"

        bad_request = urllib.request.Request(
            f"{base}/api/decision/sample-v2",
            method="POST",
            data=b"{}",
            headers={"Content-Type": "application/json"},
        )
        with pytest.raises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(bad_request)
        assert exc.value.code == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
