"""S0-12: License/SBOM pin-diff conformance tests."""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / "proofs" / "S0-12" / "check_pin_diff.py"
NEG_FIXTURE = REPO / "proofs" / "S0-12" / "fixtures" / "mutated-root"
SPEC = REPO / "proofs" / "S0-12" / "spec.json"


def _run(root_path):
    return subprocess.run(
        [sys.executable, str(CHECKER), str(root_path)],
        capture_output=True, text=True, timeout=30,
    )


def test_positive_conformance():
    r = _run(REPO)
    assert r.returncode == 0, f"checker failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_negative_mutated_pin():
    r = _run(NEG_FIXTURE)
    assert r.returncode == 1, f"expected failure, got rc={r.returncode}: {r.stdout}"
    assert "sbom-pin-drift: pin differs from upstream.lock.yaml" in r.stdout


def test_spec_valid():
    spec = json.loads(SPEC.read_text())
    assert spec["proof_id"] == "S0-12"
    legs = spec["legs"]
    pos = [l for l in legs if l["leg"] == "positive"]
    neg = [l for l in legs if l["leg"] == "negative"]
    assert len(pos) >= 1
    assert len(neg) >= 1
    assert neg[0]["expect"]["failure_reason"] == "sbom-pin-drift: pin differs from upstream.lock.yaml"


def test_deterministic():
    r1 = _run(REPO)
    r2 = _run(REPO)
    assert r1.stdout == r2.stdout
    assert r1.returncode == r2.returncode


def test_files_exist():
    assert (REPO / "LICENSE-DECISION.md").exists()
    assert (REPO / "THIRD-PARTY-NOTICES.md").exists()
    assert (REPO / "SBOM.yaml").exists()
