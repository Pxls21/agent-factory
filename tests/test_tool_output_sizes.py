"""scripts/tool_output_sizes.py: the size census behind the pruner's floor (D-123 item 1).

The estimator is checked against the plugin's own (vendor/jev-pruner/dist/jev.js, run by node), the scan on a
synthetic transcript, and the usage error by its exact message.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "tool_output_sizes.py"
PLUGIN_JEV = ROOT / "vendor" / "jev-pruner" / "dist" / "jev.js"

_spec = importlib.util.spec_from_file_location("tool_output_sizes", SCRIPT)
tos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tos)

SAMPLES = [
    "",
    "abc 12 ! Hello_world 1234567 xyzxyzxyzxyz",
    "step 0001 worker alpha processed batch with value 0.123",
    "caf" + chr(0xE9) + " na" + chr(0xEF) + "ve " + chr(0x0663) + chr(0x0664) + " digits",
    "emoji " + chr(0x1F600) + chr(0x1F680) + " end",
    "nbsp" + chr(0xA0) + "here" + chr(0x2028) + "line" + chr(0xFEFF) + "bom" + chr(0x85) + "nel" + chr(0x1C) + "fs",
    '{"a": [1, 2, 3], "b": "ccccccccccccccccc"}\n' * 40,
]


def test_estimator_matches_the_plugin():
    node = shutil.which("node")
    if node is None or not PLUGIN_JEV.is_file():
        pytest.skip("LOUD SKIP: node or vendor/jev-pruner/dist/jev.js missing; the estimator's oracle cannot run")
    program = (
        "import('" + PLUGIN_JEV.as_uri() + "').then(m => {"
        "const texts = JSON.parse(require('fs').readFileSync(0, 'utf8'));"
        "console.log(JSON.stringify(texts.map(t => m.estimateTokens(t))));});"
    )
    run = subprocess.run([node, "-e", program], input=json.dumps(SAMPLES), capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stderr
    expected = json.loads(run.stdout)
    assert [tos.estimate_tokens(text) for text in SAMPLES] == expected
    # The samples reach every branch whose JavaScript and Python readings differ.
    assert expected[3] != 0 and expected[4] != 0 and expected[5] != 0


def _record(stamp: str, role: str, parts: list) -> str:
    return json.dumps({"timestamp": stamp, "type": role, "message": {"role": role, "content": parts}})


def _transcript(path: Path) -> Path:
    lines = [
        _record("2026-09-20T10:00:00Z", "assistant", [{"type": "tool_use", "id": "old", "name": "Bash", "input": {}}]),
        _record("2026-09-20T10:00:01Z", "user", [{"type": "tool_result", "tool_use_id": "old", "content": "x" * 900}]),
        _record("2026-10-01T10:00:00Z", "assistant", [{"type": "tool_use", "id": "a1", "name": "Bash", "input": {}}]),
        _record("2026-10-01T10:00:01Z", "user", [{"type": "tool_result", "tool_use_id": "a1", "content": "hello world 42"}]),
        _record("2026-10-01T10:01:00Z", "assistant", [{"type": "tool_use", "id": "b1", "name": "Bash", "input": {}}]),
        _record("2026-10-01T10:01:01Z", "user", [{"type": "tool_result", "tool_use_id": "b1",
                                                  "content": [{"type": "text", "text": "one two"},
                                                              {"type": "image", "source": {}}]}]),
        _record("2026-10-01T10:02:00Z", "assistant", [{"type": "tool_use", "id": "c1", "name": "Bash", "input": {}}]),
        _record("2026-10-01T10:02:01Z", "user", [{"type": "tool_result", "tool_use_id": "c1",
                                                  "content": "<persisted-output>\nOutput too large (2.5KB). Full output "
                                                             "saved to: /tmp/x.txt\n\nPreview (first 2KB):\nabc\n"
                                                             "</persisted-output>"}]),
        _record("2026-10-01T10:03:00Z", "assistant", [{"type": "tool_use", "id": "r1", "name": "Read", "input": {}}]),
        _record("2026-10-01T10:03:01Z", "user", [{"type": "tool_result", "tool_use_id": "r1", "content": "def f():\n"}]),
        _record("2026-10-01T10:04:01Z", "user", [{"type": "tool_result", "tool_use_id": "nobody", "content": "zz"}]),
        "{not json",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_scan_pairs_results_with_their_tools(tmp_path):
    summary = tos.summarize(tos.scan([_transcript(tmp_path / "t.jsonl")], "2026-10-01"))
    bash = summary["Bash"]
    assert (bash["results"], bash["inline"], bash["persisted"]) == (3, 2, 1)
    assert bash["persisted_chars_p50"] == 2560
    assert bash["tokens_max"] == tos.estimate_tokens("hello world 42")
    assert bash["chars_max_inline"] == len("hello world 42")
    assert summary["Read"]["results"] == 1
    assert summary["?"]["results"] == 1


def test_since_keeps_the_older_result_out(tmp_path):
    transcript = _transcript(tmp_path / "t.jsonl")
    assert tos.summarize(tos.scan([transcript], None))["Bash"]["results"] == 4
    assert tos.summarize(tos.scan([transcript], "2026-10-01"))["Bash"]["results"] == 3


def test_cli_prints_counts_and_never_the_text(tmp_path):
    transcript = _transcript(tmp_path / "t.jsonl")
    out_json = tmp_path / "s.json"
    run = subprocess.run([sys.executable, str(SCRIPT), "--since", "2026-10-01", "--json", str(out_json),
                          str(transcript)], capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stderr
    assert run.stdout.startswith("Bash: results 3 inline 2 persisted 1 ")
    assert "hello" not in run.stdout and "hello" not in out_json.read_text(encoding="utf-8")
    assert json.loads(out_json.read_text(encoding="utf-8"))["Bash"]["inline"] == 2


def test_missing_transcript_is_a_usage_error(tmp_path):
    missing = tmp_path / "absent.jsonl"
    run = subprocess.run([sys.executable, str(SCRIPT), str(missing)], capture_output=True, text=True, timeout=60)
    assert run.returncode == 64
    assert run.stderr == f"tool_output_sizes: no such file: {missing}\n"
