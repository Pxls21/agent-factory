"""S0-09: Foundry host decision ADR conformance tests."""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / "proofs" / "S0-09" / "check_conformance.py"
ADR = REPO / "docs" / "adr" / "0005-foundry-host.md"
NEG_FIXTURE = REPO / "proofs" / "S0-09" / "fixtures" / "neg-missing-section.md"
SPEC = REPO / "proofs" / "S0-09" / "spec.json"


def _run(adr_path):
    return subprocess.run(
        [sys.executable, str(CHECKER), str(adr_path)],
        capture_output=True, text=True, timeout=30,
    )


def test_positive_conformance():
    r = _run(ADR)
    assert r.returncode == 0, f"checker failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_negative_missing_section():
    r = _run(NEG_FIXTURE)
    assert r.returncode == 1, f"expected failure, got rc={r.returncode}: {r.stdout}"
    assert "adr-incomplete: missing required section" in r.stdout


def test_negative_exact_reason():
    r = _run(NEG_FIXTURE)
    assert "Consequences" in r.stdout, f"should name the missing section: {r.stdout}"


def test_spec_valid():
    spec = json.loads(SPEC.read_text())
    assert spec["proof_id"] == "S0-09"
    legs = spec["legs"]
    pos = [l for l in legs if l["leg"] == "positive"]
    neg = [l for l in legs if l["leg"] == "negative"]
    assert len(pos) >= 1
    assert len(neg) >= 1
    assert "failure_reason" in neg[0]["expect"]
    assert neg[0]["expect"]["failure_reason"].startswith("adr-incomplete")


def test_deterministic():
    r1 = _run(ADR)
    r2 = _run(ADR)
    assert r1.stdout == r2.stdout
    assert r1.returncode == r2.returncode
