#!/usr/bin/env python3
"""Execute the generated editor's pure JavaScript helpers with Node."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from six_room_scene import write_six_room_scene_artifacts


def generated_script() -> str:
    with TemporaryDirectory() as temp:
        html_path = write_six_room_scene_artifacts(Path(temp))[2]
        html = html_path.read_text(encoding="utf-8")
    scripts = [part.split("</script>", 1)[0] for part in html.split("<script>")[1:]]
    return next(script for script in scripts if "function validateGraphData(data)" in script)


def run_node(source: str) -> str:
    result = subprocess.run(
        ["node", "-e", source],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def test_generated_editor_javascript_has_valid_syntax() -> None:
    with TemporaryDirectory() as temp:
        script_path = Path(temp) / "editor.js"
        script_path.write_text(generated_script(), encoding="utf-8")
        result = subprocess.run(
            ["node", "--check", str(script_path)],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    assert result.returncode == 0, result.stderr


def test_generated_editor_center_and_validation_helpers_execute() -> None:
    script = generated_script()
    validate_helper = script.split("function validateGraphData(data)", 1)[1].split(
        "function updateLayerToggles()", 1
    )[0]
    center_helper = script.split("function roomCenter(room)", 1)[1].split(
        "function rebuildRoomConnectionSummaries()", 1
    )[0]
    graph = {
        "schema_version": 1,
        "rooms": [
            {"room_id": "upper_left", "x": 0, "y": 4, "width": 34, "height": 9, "regions": ["upper_band"]},
            {"room_id": "upper_right", "x": 57, "y": 4, "width": 34, "height": 9, "regions": ["upper_band"]},
        ],
        "regions": [{"name": "upper_band"}],
        "connections": [
            {
                "from_room": "upper_left",
                "to_room": "upper_right",
                "kind": "horizontal",
                "region_name": "upper_band",
            }
        ],
    }
    source = (
        "function validateGraphData(data)" + validate_helper
        + "function roomCenter(room)" + center_helper
        + f"const graph = {json.dumps(graph)};\n"
        + "const badRegion = structuredClone(graph); badRegion.rooms[0].regions = ['missing'];\n"
        + "console.log(JSON.stringify({center: roomCenter(graph.rooms[0]), valid: validateGraphData(graph), invalid: validateGraphData([]), badRegion: validateGraphData(badRegion)}));"
    )
    result = json.loads(run_node(source))
    assert result["center"] == {"x": 16, "y": 8}
    assert result["valid"] == []
    assert result["invalid"] == ["graph JSON root must be an object"]
    assert result["badRegion"] == ["room upper_left references unknown region missing"]


def test_generated_editor_numeric_input_does_not_truncate_fractions() -> None:
    script = generated_script()
    helper = script.split("function intFromInput(id)", 1)[1].split("function roomCenter(room)", 1)[0]
    source = (
        "const values = {blank: '', fraction: '1.5', whole: '-2'};"
        "const document = {getElementById: id => ({value: values[id]})};"
        "function intFromInput(id)" + helper
        + "console.log(JSON.stringify([intFromInput('blank'), intFromInput('fraction'), intFromInput('whole')]));"
    )
    values = json.loads(run_node(source))
    assert values == [None, 1.5, -2]


def test_generated_editor_html_escape_helper_executes() -> None:
    script = generated_script()
    escape_helper = script.split("function escapeHtml(value)", 1)[1].split("function roomById", 1)[0]
    source = (
        "function escapeHtml(value)" + escape_helper
        + "console.log(escapeHtml('<img src=x onerror=alert(1)>\\\"\\\''));"
    )
    assert run_node(source) == "&lt;img src=x onerror=alert(1)&gt;&quot;&#39;"


if __name__ == "__main__":
    test_generated_editor_javascript_has_valid_syntax()
    test_generated_editor_center_and_validation_helpers_execute()
    test_generated_editor_numeric_input_does_not_truncate_fractions()
    test_generated_editor_html_escape_helper_executes()
    print("PASS six-room editor JavaScript execution")
