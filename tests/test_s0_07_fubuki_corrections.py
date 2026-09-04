"""S0-07: Fubuki corrections conformance tests."""
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / "proofs" / "S0-07" / "check_fubuki_corrections.py"
NEG_FIXTURE = REPO / "proofs" / "S0-07" / "fixtures" / "neg-violating-persona"
SPEC = REPO / "proofs" / "S0-07" / "spec.json"
SPEC_SCHEMA = REPO / "proofs" / "schemas" / "spec.schema.json"

FUBUKI_ROOT = Path("/home/user/nerdherderdani/fubuki-os")

import pytest

needs_fubuki = pytest.mark.skipif(
    not (FUBUKI_ROOT / "src" / "fubuki_os").is_dir(),
    reason="fubuki-os not cloned at expected path",
)


def _run(*extra_args):
    return subprocess.run(
        [sys.executable, str(CHECKER)] + list(extra_args),
        capture_output=True, text=True, timeout=30,
    )


@needs_fubuki
def test_positive_conformance():
    r = _run(str(FUBUKI_ROOT))
    assert r.returncode == 0, f"checker failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


@needs_fubuki
def test_negative_violating_persona():
    r = _run("--lint-check", str(NEG_FIXTURE), str(FUBUKI_ROOT))
    assert r.returncode == 1, f"expected failure, got rc={r.returncode}: {r.stdout}"
    assert "lint-violation:" in r.stdout
    assert "exit 1 per contract" in r.stdout


def test_spec_valid():
    spec = json.loads(SPEC.read_text())
    schema = json.loads(SPEC_SCHEMA.read_text())
    jsonschema.validate(spec, schema)
    assert spec["proof_id"] == "S0-07"
    legs = spec["legs"]
    pos = [l for l in legs if l["leg"] == "positive"]
    neg = [l for l in legs if l["leg"] == "negative"]
    assert len(pos) >= 1
    assert len(neg) >= 1
    assert neg[0]["expect"]["exit_code"] == 1
    assert "lint-violation:" in neg[0]["expect"]["failure_reason"]


@needs_fubuki
def test_deterministic():
    r1 = _run(str(FUBUKI_ROOT))
    r2 = _run(str(FUBUKI_ROOT))
    assert r1.stdout == r2.stdout
    assert r1.returncode == r2.returncode


@needs_fubuki
def test_lint_ordering_bug_reproduced():
    """The upstream ordering bug is exercised and wrapped by the checker."""
    sys.path.insert(0, str(FUBUKI_ROOT / "src"))
    sys.path.insert(0, str(FUBUKI_ROOT))
    from lint.persona_lint import main as upstream_main

    fixture_dir = REPO / "proofs" / "S0-07" / "fixtures" / "ordered-lint"
    rc = upstream_main([
        str(fixture_dir / "01-review-only.txt"),
        str(fixture_dir / "02-has-violation.txt"),
    ])
    assert rc == 2, (
        f"upstream ordering bug not reproduced: expected exit 2 "
        f"(REVIEW before VIOLATION), got {rc}"
    )


def test_fixtures_exist():
    ordered = REPO / "proofs" / "S0-07" / "fixtures" / "ordered-lint"
    assert (ordered / "01-review-only.txt").exists()
    assert (ordered / "02-has-violation.txt").exists()
    assert (ordered / "clean.txt").exists()
    assert (NEG_FIXTURE / "violation.txt").exists()
