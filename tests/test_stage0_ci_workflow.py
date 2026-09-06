"""Structural checks for .github/workflows/stage0-ci.yml.

Uses YAML parsing for step-level assertions and line-anchored regexes for
whole-file structure. Each assertion pins a structural property from the
review-fixes brief's contract C1.
"""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "stage0-ci.yml"
SETUP_SH = ROOT / "scripts" / "setup.sh"


def _read():
    return WORKFLOW.read_text()


def test_workflow_exists():
    assert WORKFLOW.is_file(), "stage0-ci.yml must exist"


def test_five_job_names():
    text = _read()
    expected = {"tests", "harness-suites", "ledger-integrity", "stage1-gate", "planning"}
    found = set(re.findall(r"^  (\S+):$", text, re.MULTILINE))
    assert expected <= found, f"missing jobs: {expected - found}"


def test_stage1_gate_continue_on_error():
    text = _read()
    assert re.search(r"stage1-gate:.*?continue-on-error:\s*true", text, re.DOTALL), \
        "stage1-gate must have continue-on-error: true"


def test_pip_pins_match_setup_sh():
    wf = _read()
    setup = SETUP_SH.read_text()
    for pin in ["jsonschema==4.25.1", "rfc3339-validator==0.1.4"]:
        assert pin in wf, f"{pin} missing from workflow"
        assert pin in setup, f"{pin} missing from setup.sh (test premise)"


def test_triggers_push_and_pull_request():
    text = _read()
    assert re.search(r"^on:", text, re.MULTILINE)
    assert re.search(r"^\s+push:", text, re.MULTILINE), "push trigger missing"
    assert re.search(r"^\s+pull_request:", text, re.MULTILINE), "pull_request trigger missing"


def test_permissions_contents_read():
    text = _read()
    assert re.search(r"^permissions:", text, re.MULTILINE)
    assert re.search(r"^\s+contents:\s*read", text, re.MULTILINE), \
        "permissions.contents must be read"


def test_ledger_diff_step_positioned_correctly():
    """F5: the ledger-diff step's `run` value must == the exact command (not regex),
    and its position asserted by index between 'Generate ledger' and
    'Validate ledger integrity'."""
    wf = yaml.safe_load(_read())
    steps = wf["jobs"]["ledger-integrity"]["steps"]
    # Find step indices by name
    gen_idx = next((i for i, s in enumerate(steps) if s.get("name") == "Generate ledger"), None)
    diff_idx = next((i for i, s in enumerate(steps)
                     if s.get("name") == "Committed ledger equals the regenerated one"), None)
    val_idx = next((i for i, s in enumerate(steps)
                    if s.get("name") == "Validate ledger integrity"), None)
    assert gen_idx is not None, "step 'Generate ledger' missing"
    assert diff_idx is not None, "step 'Committed ledger equals the regenerated one' missing"
    assert val_idx is not None, "step 'Validate ledger integrity' missing"
    # Position by index
    assert gen_idx < diff_idx < val_idx, \
        f"wrong step ordering: Generate({gen_idx}) < Diff({diff_idx}) < Validate({val_idx})"
    # Exact run command equality (not regex)
    assert steps[diff_idx]["run"] == "git diff --exit-code -- proofs/ledger.json"


def test_lint_proofs_and_tests_step():
    """6-F23: CI lints proofs/S0-01 and tests/ with pyflakes."""
    wf = yaml.safe_load(_read())
    steps = wf["jobs"]["tests"]["steps"]
    lint_step = next((s for s in steps
                      if s.get("name") == "Lint proofs and tests"), None)
    assert lint_step is not None, \
        "step 'Lint proofs and tests' missing from tests job"
    assert lint_step["run"] == "python -m pyflakes proofs/S0-01 tests/"
