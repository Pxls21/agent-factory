"""S0-11: Evaluation hardening conformance tests."""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / "proofs" / "S0-11" / "check_eval_hardening.py"
PROOF_DIR = REPO / "proofs" / "S0-11"
NEG_FIXTURE = PROOF_DIR / "fixtures" / "neg_credential_read.py"
SPEC = PROOF_DIR / "spec.json"


def _run(*extra_args):
    return subprocess.run(
        [sys.executable, str(CHECKER)] + list(extra_args),
        capture_output=True, text=True, timeout=30,
    )


def test_positive_conformance():
    r = _run(str(PROOF_DIR))
    assert r.returncode == 0, "checker failed: " + r.stdout + r.stderr
    assert "PASS" in r.stdout


def test_negative_credential_violation():
    r = _run("--rubric-neg", str(NEG_FIXTURE), str(PROOF_DIR))
    assert r.returncode == 1, "expected failure, got rc=" + str(r.returncode) + ": " + r.stdout
    assert "rubric-isolation-violation:" in r.stdout
    assert "exit 1 per contract" in r.stdout


def test_spec_valid():
    spec = json.loads(SPEC.read_text())
    assert spec["proof_id"] == "S0-11"
    assert spec["classification"] == "execution_proof"
    legs = spec["legs"]
    pos = [l for l in legs if l["leg"] == "positive"]
    neg = [l for l in legs if l["leg"] == "negative"]
    assert len(pos) >= 1
    assert len(neg) >= 1
    assert neg[0]["expect"]["exit_code"] == 1
    assert "rubric-isolation-violation:" in neg[0]["expect"]["failure_reason"]


def test_deterministic():
    r1 = _run(str(PROOF_DIR))
    r2 = _run(str(PROOF_DIR))
    assert r1.stdout == r2.stdout
    assert r1.returncode == r2.returncode


def test_fixtures_exist():
    assert (PROOF_DIR / "runner_design.md").exists()
    assert (PROOF_DIR / "fixtures" / "rubric_probe.py").exists()
    assert (PROOF_DIR / "fixtures" / "neg_credential_read.py").exists()


def test_runner_design_covers_hazards():
    text = (PROOF_DIR / "runner_design.md").read_text()
    assert "network isolation" in text.lower() or "no host network" in text.lower()
    assert "chmod 777" in text.lower() or "permission hardening" in text.lower()
    assert "credential" in text.lower()
