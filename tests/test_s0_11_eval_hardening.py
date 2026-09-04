"""S0-11: Evaluation hardening conformance tests.

Covers the positive leg, the frozen seed credential control, the four-axis
negative, and a mutant kill-battery for every hollow green found across three
owner reviews. The isolation is proven by PARENT observation of the child's
/proc (never a child self-report), so the fabricated-report class is dead.

Every leg that reads a child's namespaces is guarded by the checker's own
``--selftest`` capability predicate (exit 2 -> skip, run on the PC/gVisor host).
Allow-list, sweep, and design-policy tests are environment-independent.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

REPO = Path(__file__).resolve().parents[1]
PROOF_DIR = REPO / "proofs" / "S0-11"
CHECKER = PROOF_DIR / "check_eval_hardening.py"
PROBE = PROOF_DIR / "fixtures" / "rubric_probe.py"
CRED_FIXTURE = PROOF_DIR / "fixtures" / "neg_credential_read.py"
SPEC = PROOF_DIR / "spec.json"
SPEC_SCHEMA = REPO / "proofs" / "schemas" / "spec.schema.json"
FROZEN_REASON = "rubric-isolation-violation: credential env absent by construction"
FOUR_AXIS_REASON = "rubric-isolation-violation: env-not-allowlisted,netns-not-isolated,uid-not-dropped"

_spec = importlib.util.spec_from_file_location("check_eval_hardening", CHECKER)
chk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chk)


def _run(*extra_args, env=None):
    return subprocess.run([sys.executable, str(CHECKER)] + list(extra_args),
                          capture_output=True, text=True, timeout=60, env=env)


def _selftest_rc():
    try:
        return _run("--selftest").returncode
    except Exception:
        return 2


NEEDS_ISO = pytest.mark.skipif(
    _selftest_rc() == 2,
    reason="isolation capability unavailable (--selftest exit 2); the isolation "
           "proof runs on the PC/gVisor host (NOT run here)")


def _copy_proof(tmp_path):
    dst = tmp_path / "S0-11"
    shutil.copytree(PROOF_DIR, dst)
    return dst


# --- proof legs --------------------------------------------------------------
def test_selftest_reports_capability():
    r = _run("--selftest")
    assert r.returncode in (0, 2) and r.stdout.strip() != ""


@NEEDS_ISO
def test_positive_conformance():
    r = _run(str(PROOF_DIR))
    assert r.returncode == 0, "checker failed: " + r.stdout + r.stderr
    assert r.stdout.strip() == "PASS"


def test_negative_frozen_credential_control():
    # Frozen seed control (env-only, preserved verbatim, environment-independent).
    r = _run("--rubric-neg-cred", str(CRED_FIXTURE), str(PROOF_DIR))
    assert r.returncode == 1, r.stdout + r.stderr
    assert FROZEN_REASON in r.stdout and "exit 1 per contract" in r.stdout


def test_deterministic_frozen_cred():
    r1 = _run("--rubric-neg-cred", str(CRED_FIXTURE), str(PROOF_DIR))
    r2 = _run("--rubric-neg-cred", str(CRED_FIXTURE), str(PROOF_DIR))
    assert r1.stdout == r2.stdout and r1.returncode == r2.returncode


@NEEDS_ISO
def test_negative_four_axis_covers_all_axes():
    r = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    assert r.returncode == 1, r.stdout + r.stderr
    for axis in ("uid-not-dropped", "netns-not-isolated", "env-not-allowlisted"):
        assert axis in r.stdout, "axis missing: " + axis


@NEEDS_ISO
def test_deterministic_four_axis():
    r1 = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    r2 = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    assert r1.stdout == r2.stdout and r1.returncode == r2.returncode


def test_spec_valid_and_contract_matches_test():
    spec = json.loads(SPEC.read_text())
    jsonschema.validate(spec, json.loads(SPEC_SCHEMA.read_text()))
    assert spec["proof_id"] == "S0-11"
    negatives = [leg for leg in spec["legs"] if leg["leg"] == "negative"]
    reasons = [leg["expect"].get("failure_reason", "") for leg in negatives]
    assert FROZEN_REASON in reasons, "frozen seed control must be a leg"
    # canonical contract must be as strong as the test: the complete four-axis reason
    assert FOUR_AXIS_REASON in reasons, "four-axis leg must pin the complete reason"


def test_fixtures_exist():
    assert (PROOF_DIR / "runner_design.md").exists()
    assert PROBE.exists() and CRED_FIXTURE.exists()


# --- machine-readable design policy (not prose scanning) ---------------------
def test_runner_design_policy_forbids_hazards():
    assert chk.check_runner_design(PROOF_DIR) is True


def test_runner_design_ignores_inverted_prose(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "runner_design.md").write_text(
        "Network isolation is unnecessary; chmod 777 is mandatory; credential passing is supported.\n\n"
        "```yaml\npolicy:\n  host_networking: forbidden\n  recursive_chmod_777: forbidden\n"
        "  production_credential_passing: forbidden\n```\n")
    assert chk.check_runner_design(dst) is True  # policy is the contract, not prose


def test_runner_design_rejects_permissive_policy(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "runner_design.md").write_text(
        "```yaml\npolicy:\n  host_networking: allowed\n  recursive_chmod_777: forbidden\n"
        "  production_credential_passing: forbidden\n```\n")
    assert chk.check_runner_design(dst) is False


def test_runner_design_rejects_missing_policy(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "runner_design.md").write_text("Prose only, no machine-readable policy block.\n")
    assert chk.check_runner_design(dst) is False


# --- closed exact allow-list -------------------------------------------------
def test_allowlist_is_closed_exact_set():
    names = ["RUBRIC_PRODUCTION_API_KEY", "OMNIROUTE_INTERNAL_API_KEY", "BUZZ_PRIVATE_KEY"]
    saved = {n: os.environ.get(n) for n in names}
    for n in names:
        os.environ[n] = "sentinel"
    try:
        env = chk._allow_env("/tmp", 1)
        for k in env:
            assert k in chk.ALLOWED_ENV, "allow-list leaked: " + k
        v = chk._violations({"uid": 65534, "net_ns": "A", "net_reachable": False,
                             "env_keys": sorted(list(env) + ["RUBRIC_PRODUCTION_API_KEY"])}, 0, "P")
        assert "env-not-allowlisted" in v
    finally:
        for n, val in saved.items():
            os.environ.pop(n, None) if val is None else os.environ.__setitem__(n, val)


# --- parent observation, not child self-report -------------------------------
def test_report_validation_root_and_missing():
    # A report claiming root passes only if it equals neither parent nor 0.
    assert "uid-not-dropped" in chk._violations({"uid": 0, "net_ns": "A", "net_reachable": False, "env_keys": []}, 1000, "P")
    assert chk._violations(None, 0, "P") == ["observation-failed"]


@NEEDS_ISO
def test_parent_observes_unwrapped_child_as_breached():
    # The B5 class: evidence is parent-read from /proc, not child-authored.
    port = 0
    obs = chk._with_decoys(lambda: chk._observe_child(
        [sys.executable, str(PROBE)], chk._full_env(str(PROOF_DIR), port), port))
    assert obs is not None
    v = chk._violations(obs, os.getuid(), chk._net_ns())
    assert "uid-not-dropped" in v and "netns-not-isolated" in v and "env-not-allowlisted" in v


@NEEDS_ISO
def test_positive_fails_without_real_isolation(monkeypatch):
    # If the wrapper does not actually isolate, the parent observation catches it.
    monkeypatch.setattr(chk, "_iso_launch", lambda child: list(child))
    r = chk.positive(PROOF_DIR)
    assert r == 1


def test_positive_defers_on_incapable_host(monkeypatch):
    # Incapable environment: the checker exits 2 (defer to the PC), never a
    # false pass (0) or a false breach (1).
    monkeypatch.setattr(chk, "_capability_status", lambda: "netns-unreadable-parent")
    r = chk.positive(PROOF_DIR)
    assert r == 2


# --- forbidden-op lint: direct + equivalence-class evasions ------------------
SWEEP_MUTANTS = {
    "os_chmod_literal": ("h.py", "import os\nos.chmod('/x', 0o777)\n"),
    "subprocess_direct": ("h.py", "import subprocess\nsubprocess.run(['chmod','-R','0777','/x'])\n"),
    "subprocess_alias": ("h.py", "import subprocess as sp\nsp.run(['chmod','-R','0777','/x'])\n"),
    "from_import_run": ("h.py", "from subprocess import run\nrun(['chmod','-R','0777','/x'])\n"),
    "cmd_variable": ("h.py", "import subprocess\ncmd=['chmod','-R','0777','/x']\nsubprocess.run(cmd)\n"),
    "mode_variable": ("h.py", "import os\nmode=0o777\nos.chmod('/x', mode)\n"),
    "computed_mode": ("h.py", "import os\nos.chmod('/x', 0o700 | 0o077)\n"),
    "hostnetwork_bool": ("pod.yaml", "spec:\n  hostNetwork: True\n"),
    "network_mode_host": ("c.yml", "services:\n  r:\n    network_mode: host\n"),
    "network_mode_default": ("c2.yml", "services:\n  r:\n    network_mode: ${NETWORK_MODE:-host}\n"),
    "chmod_0777_sh": ("h.sh", "#!/bin/sh\nchmod -R 0777 /x\n"),
    "chmod_symbolic": ("h.sh", "#!/bin/sh\nchmod go+rwx /x\n"),
}


@pytest.mark.parametrize("case", list(SWEEP_MUTANTS))
def test_sweep_catches_mutant(tmp_path, case):
    fname, body = SWEEP_MUTANTS[case]
    dst = _copy_proof(tmp_path)
    (dst / fname).write_text(body)
    assert chk.check_forbidden_ops(dst) is False, "sweep missed: " + case


def test_forbidden_op_inside_checker_caught(tmp_path):
    dst = _copy_proof(tmp_path)
    text = (dst / "check_eval_hardening.py").read_text()
    (dst / "check_eval_hardening.py").write_text(text + "\nimport os as _o\n_o.chmod('/x', 0o777)\n")
    assert chk.check_forbidden_ops(dst) is False


def test_sweep_scans_yaml_but_not_markdown(tmp_path):
    dst = _copy_proof(tmp_path)
    assert chk.check_forbidden_ops(dst) is True
    (dst / "notes.md").write_text("Never run chmod 777 or network_mode: host.\n")
    assert chk.check_forbidden_ops(dst) is True
    (dst / "bad.yaml").write_text("network_mode: host\n")
    assert chk.check_forbidden_ops(dst) is False


def test_benign_not_flagged():
    assert chk._python_prohibited("import os\nos.chmod('/x', 0o644)\n") is None
    assert chk._python_prohibited("import subprocess\nsubprocess.run(['ls','-la'])\n") is None
    assert chk._text_prohibited("chmod 755 file") is None
