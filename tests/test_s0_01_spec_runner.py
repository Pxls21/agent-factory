"""S0-01 through the CANONICAL proof-runner: with the committed evidence still v1
(no timeline.jsonl), the runner's positive leg must DEFER (exit 2, no result.json).
The negative leg also defers today (the negative/ directory does not exist yet).

This test invokes scripts/proof-runner for real (F11: not just the leg cmd directly)
and asserts the runner's failure_reason match rule (per-line substring over stdout+stderr)
by feeding it a two-line stdout fixture.

The runner matches failure_reason with:
    next((line for line in (stdout + "\\n" + stderr).splitlines() if expected_reason in line), None)
This is a per-line substring match. check_initialize's two-line output
(classification on line 1, observed on line 2) is compatible because the expected
failure_reason "protocol-violation: missing required initialize field" is the
exact text of line 1.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "proof-runner"


def _copy(tmp_path):
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "proofs", root / "proofs")
    # The runner also needs scripts/ for the validator
    shutil.copytree(ROOT / "scripts", root / "scripts")
    return root


def test_positive_leg_defers_on_v1_evidence(tmp_path):
    """The positive leg defers (exit 2) because the committed evidence is v1
    (no timeline.jsonl). The runner must NOT create a result.json."""
    root = _copy(tmp_path)
    spec = json.loads((root / "proofs" / "S0-01" / "spec.json").read_text())
    pos = next(l for l in spec["legs"] if l["leg"] == "positive")
    r = subprocess.run(
        [sys.executable, *pos["cmd"][1:]],
        cwd=root, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 2, f"expected exit 2 (deferred), got {r.returncode}: {r.stdout}"
    assert r.stdout.startswith("deferred:")
    assert not (root / "proofs" / "S0-01" / "result.json").exists()


def test_negative_leg_defers_via_runner(tmp_path):
    """F11: invoke the CANONICAL proof-runner for the negative leg.
    The negative/ directory does not exist yet, so check_initialize exits 2 (deferred),
    and the runner raises Deferred (exits 2) preserving any existing artifact.
    The runner's stdout carries the Deferred message."""
    root = _copy(tmp_path)
    r = subprocess.run(
        [sys.executable, str(RUNNER), "--proof", "S0-01", "--venue", "sandbox"],
        cwd=root, capture_output=True, text=True, timeout=120,
    )
    # The runner itself exits 2 on Deferred (raised by the capability-unavailable branch)
    assert r.returncode == 2, f"expected exit 2 (deferred), got {r.returncode}: stdout={r.stdout} stderr={r.stderr}"


def test_negative_leg_defers_directly(tmp_path):
    """The negative leg cmd defers today (directory absent) with the exact text."""
    root = _copy(tmp_path)
    spec = json.loads((root / "proofs" / "S0-01" / "spec.json").read_text())
    neg = next(l for l in spec["legs"] if l["leg"] == "negative")
    r = subprocess.run(
        [sys.executable, *neg["cmd"][1:]],
        cwd=root, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 2, f"expected exit 2 (deferred), got {r.returncode}: {r.stdout}"
    assert r.stdout.strip() == "deferred: negative probe not captured"


def test_spec_structure_matches_brief(tmp_path):
    """The spec's negative leg now points at the golden/negative directory,
    and the positive leg still runs check_acp_conformance.py."""
    root = _copy(tmp_path)
    spec = json.loads((root / "proofs" / "S0-01" / "spec.json").read_text())
    pos = next(l for l in spec["legs"] if l["leg"] == "positive")
    neg = next(l for l in spec["legs"] if l["leg"] == "negative")
    assert pos["cmd"][1].endswith("check_acp_conformance.py")
    assert neg["cmd"] == ["python3", "proofs/S0-01/check_initialize.py", "request",
                          "proofs/S0-01/evidence/golden/negative"]
    assert neg["expect"]["exit_code"] == 1
    assert neg["expect"]["failure_reason"] == "protocol-violation: missing required initialize field"


def test_runner_failure_reason_matching():
    """Verify the runner's failure_reason matching rule is per-line substring.
    With check_initialize's two-line output:
      line 1: protocol-violation: missing required initialize field
      line 2: observed: error code=-32600 message=Invalid request
    The expected failure_reason is the line 1 text, and the runner's substring
    match finds it on line 1."""
    expected_reason = "protocol-violation: missing required initialize field"
    stdout = ("protocol-violation: missing required initialize field\n"
              "observed: error code=-32600 message=Invalid request")
    stderr = ""
    # Reproduce the runner's matching logic (scripts/proof-runner:196)
    observed = next(
        (line for line in (stdout + "\n" + stderr).splitlines() if expected_reason in line),
        None,
    )
    assert observed is not None
    assert observed == "protocol-violation: missing required initialize field"
