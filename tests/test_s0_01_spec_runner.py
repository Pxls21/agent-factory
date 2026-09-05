"""S0-01 through the CANONICAL proof-runner: with the committed evidence still v1
(no timeline.jsonl), the runner's positive leg must DEFER (exit 2, no result.json).
The negative leg also defers today (the negative/ directory does not exist yet).
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


def test_negative_leg_defers_today(tmp_path):
    """The negative leg points at proofs/S0-01/evidence/golden/negative which does not
    exist yet, so check_initialize.py on that directory returns exit 2 (deferred)."""
    root = _copy(tmp_path)
    spec = json.loads((root / "proofs" / "S0-01" / "spec.json").read_text())
    neg = next(l for l in spec["legs"] if l["leg"] == "negative")
    r = subprocess.run(
        [sys.executable, *neg["cmd"][1:]],
        cwd=root, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 2, f"expected exit 2 (deferred), got {r.returncode}: {r.stdout}"
    assert "deferred:" in r.stdout


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
