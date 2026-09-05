"""S0-01 through the CANONICAL proof-runner: today the positive leg must DEFER (the golden bundle is not
captured yet), the runner must preserve (create no result.json), and the negative leg's exact reason line
must be the one the spec binds. Runs the real runner on a copy of proofs/ (never the shared tree)."""
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


def test_positive_leg_defers_and_preserves_no_artifact(tmp_path):
    root = _copy(tmp_path)
    r = subprocess.run([sys.executable, str(RUNNER), "--proof", "S0-01", "--venue", "sandbox", "--root", str(root), "run"],
                       capture_output=True, text=True, timeout=180)
    assert r.returncode != 0
    assert "deferred" in (r.stdout + r.stderr).lower() and "S0-01" in (r.stdout + r.stderr)
    assert not (root / "proofs" / "S0-01" / "result.json").exists()


def test_negative_leg_reason_line_matches_the_spec_binding(tmp_path):
    root = _copy(tmp_path)
    spec = json.loads((root / "proofs" / "S0-01" / "spec.json").read_text())
    neg = next(l for l in spec["legs"] if l["leg"] == "negative")
    r = subprocess.run([sys.executable, *neg["cmd"][1:]], cwd=root, capture_output=True, text=True, timeout=60)
    assert r.returncode == neg["expect"]["exit_code"]
    assert any(neg["expect"]["failure_reason"] in line for line in (r.stdout + "\n" + r.stderr).splitlines())
    assert spec["legs"][0]["cmd"][1].endswith("check_acp_conformance.py")
