"""Structural checks for .github/workflows/stage0-ci.yml.

Uses line-anchored regexes, not YAML parsing — PyYAML is not a declared
project dependency. Each assertion pins a structural property from the
review-fixes brief's contract C1.
"""
import re
from pathlib import Path

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
    """V-d F15: the 'Committed ledger equals the regenerated one' step must exist with the
    exact `git diff --exit-code -- proofs/ledger.json` run command, positioned after
    'Generate ledger' and before 'Validate ledger integrity'."""
    text = _read()
    # Find step names with their positions to assert ordering
    gen_pos = text.find("Generate ledger")
    diff_pos = text.find("Committed ledger equals the regenerated one")
    validate_pos = text.find("Validate ledger integrity")
    assert gen_pos >= 0, "step 'Generate ledger' missing"
    assert diff_pos >= 0, "step 'Committed ledger equals the regenerated one' missing"
    assert validate_pos >= 0, "step 'Validate ledger integrity' missing"
    assert gen_pos < diff_pos < validate_pos, \
        f"wrong ordering: Generate({gen_pos}) < Diff({diff_pos}) < Validate({validate_pos})"
    # Assert the exact run command
    assert re.search(
        r"Committed ledger equals the regenerated one.*?\n\s+run:\s*git diff --exit-code -- proofs/ledger\.json",
        text, re.DOTALL
    ), "ledger diff step run command must be 'git diff --exit-code -- proofs/ledger.json'"
