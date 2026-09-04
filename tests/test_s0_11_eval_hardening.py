"""S0-11: Evaluation hardening conformance tests.

Isolation is proven by PARENT observation of the child's /proc (uid, netns,
cwd, environ) plus an ACTIVE nsenter listener discriminator — never a child
self-report. Every namespace-reading leg (positive, --rubric-neg) runs the
checker's own `--selftest` preflight and DEFERS (exit 2) on a venue that cannot
run the discriminator; a capable venue must run nsenter (root). The env-only
frozen credential leg runs everywhere.

Isolation-dependent tests skip via `--selftest` (exit 2); allow-list, sweep,
design-policy, and report-validation tests are environment-independent.
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
STABLE_NEG_REASON = ("rubric-isolation-violation: "
                     "cwd-not-isolated,env-not-allowlisted,netns-not-isolated")

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
           "proof runs on a capable (root, nsenter) venue (NOT run here)")


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


@NEEDS_ISO
def test_all_spec_legs_via_canonical_invocation():
    # Every spec leg, run exactly as the canonical runner invokes it.
    spec = json.loads(SPEC.read_text())
    for leg in spec["legs"]:
        args = leg["cmd"][1:]  # drop "python3"
        r = subprocess.run([sys.executable] + args, capture_output=True, text=True,
                           timeout=60, cwd=str(REPO))
        assert r.returncode == leg["expect"]["exit_code"], \
            leg["leg"] + " exit " + str(r.returncode) + ": " + r.stdout + r.stderr
        if "failure_reason" in leg["expect"]:
            assert leg["expect"]["failure_reason"] in (r.stdout + r.stderr)


def test_negative_frozen_credential_control():
    # Env-only, preserved verbatim, environment-independent (no preflight gate).
    r = _run("--rubric-neg-cred", str(CRED_FIXTURE), str(PROOF_DIR))
    assert r.returncode == 1, r.stdout + r.stderr
    assert FROZEN_REASON in r.stdout and "exit 1 per contract" in r.stdout


def test_deterministic_frozen_cred():
    r1 = _run("--rubric-neg-cred", str(CRED_FIXTURE), str(PROOF_DIR))
    r2 = _run("--rubric-neg-cred", str(CRED_FIXTURE), str(PROOF_DIR))
    assert r1.stdout == r2.stdout and r1.returncode == r2.returncode


@NEEDS_ISO
def test_negative_covers_stable_axes():
    r = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    assert r.returncode == 1, r.stdout + r.stderr
    assert STABLE_NEG_REASON in r.stdout
    for axis in ("netns-not-isolated", "cwd-not-isolated", "env-not-allowlisted"):
        assert axis in r.stdout


@NEEDS_ISO
def test_deterministic_four_axis():
    r1 = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    r2 = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    assert r1.stdout == r2.stdout and r1.returncode == r2.returncode


def test_spec_valid_and_contract_matches_test():
    spec = json.loads(SPEC.read_text())
    jsonschema.validate(spec, json.loads(SPEC_SCHEMA.read_text()))
    assert spec["proof_id"] == "S0-11"
    reasons = [leg["expect"].get("failure_reason", "")
               for leg in spec["legs"] if leg["leg"] == "negative"]
    assert FROZEN_REASON in reasons, "frozen seed control must be a leg"
    assert STABLE_NEG_REASON in reasons, "negative leg must pin the complete stable reason"


def test_fixtures_exist():
    assert (PROOF_DIR / "runner_design.md").exists()
    assert PROBE.exists() and CRED_FIXTURE.exists()


# --- machine-readable design policy ------------------------------------------
def test_runner_design_policy_forbids_hazards():
    assert chk.check_runner_design(PROOF_DIR) is True


def test_runner_design_ignores_inverted_prose(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "runner_design.md").write_text(
        "Network isolation is unnecessary; chmod 777 is mandatory; credential passing is supported.\n\n"
        "```yaml\npolicy:\n  host_networking: forbidden\n  recursive_chmod_777: forbidden\n"
        "  production_credential_passing: forbidden\n```\n")
    assert chk.check_runner_design(dst) is True


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


# --- closed exact allow-list + report validation (env-independent) -----------
def test_allowlist_is_closed_exact_set():
    names = ["RUBRIC_PRODUCTION_API_KEY", "OMNIROUTE_INTERNAL_API_KEY", "RUBRIC_LLM_ENDPOINT"]
    saved = {n: os.environ.get(n) for n in names}
    for n in names:
        os.environ[n] = "sentinel"
    try:
        env = chk._allow_env()
        for k in env:
            assert k in chk.ENV_ALLOWLIST, "allow-list leaked: " + k
        obs = {"uid": 65534, "net_ns": "A", "cwd": "/fresh", "net_reachable": False,
               "env_keys": sorted(list(chk.ALLOWED_ENV) + ["RUBRIC_PRODUCTION_API_KEY"])}
        assert "env-not-allowlisted" in chk._violations(obs, "P", "/parent")
    finally:
        for n, val in saved.items():
            os.environ.pop(n, None) if val is None else os.environ.__setitem__(n, val)


def test_report_validation_axes():
    parent_ns, parent_cwd = "P", "/parent"
    isolated = {"uid": 65534, "net_ns": "A", "cwd": "/fresh", "net_reachable": False, "env_keys": []}
    assert chk._violations(isolated, parent_ns, parent_cwd) == []
    assert "uid-is-root" in chk._violations({**isolated, "uid": 0}, parent_ns, parent_cwd)
    assert "netns-not-isolated" in chk._violations({**isolated, "net_ns": parent_ns}, parent_ns, parent_cwd)
    assert "cwd-not-isolated" in chk._violations({**isolated, "cwd": parent_cwd}, parent_ns, parent_cwd)
    assert chk._violations(None, parent_ns, parent_cwd) == ["observation-failed"]


# --- venue behaviour: capable runs; incapable defers on every namespace leg --
@NEEDS_ISO
@pytest.mark.skipif(os.getuid() != 0 or not os.path.exists("/usr/bin/setpriv"),
                    reason="non-root venue simulation needs a root runner + setpriv")
def test_non_root_venue_defers():
    # A non-root venue cannot run the nsenter discriminator, so the checker
    # DEFERS (exit 2) — never a false pass or breach.
    r = subprocess.run(
        ["/usr/bin/setpriv", "--reuid", "65534", "--regid", "65534", "--clear-groups",
         "--", sys.executable, str(CHECKER), str(PROOF_DIR)],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 2, "expected defer, got " + str(r.returncode) + ": " + r.stdout


def test_every_namespace_leg_defers_on_incapable(monkeypatch):
    # Incapable environment: positive AND the namespace-reading negative both
    # defer (exit 2); the env-only frozen credential leg still runs.
    monkeypatch.setattr(chk, "_capability_status", lambda: "nsenter-unavailable")
    assert chk.positive(PROOF_DIR) == 2
    assert chk.rubric_neg(PROBE, PROOF_DIR) == 2
    assert chk.rubric_neg_cred(CRED_FIXTURE, PROOF_DIR) == 1  # env-only, ungated


@NEEDS_ISO
def test_parent_observes_unwrapped_child_as_breached():
    listener = chk._LoopbackListener()
    try:
        obs = chk._with_decoys(lambda: chk._observe_child(
            [sys.executable, str(PROBE)], chk._full_env(), listener.port, False))
    finally:
        listener.close()
    assert obs is not None
    for axis in ("netns-not-isolated", "cwd-not-isolated", "env-not-allowlisted"):
        assert axis in chk._violations(obs, chk._net_ns(), os.getcwd())
    assert obs["net_reachable"] is True  # un-wrapped child reaches the parent's listener
    if os.getuid() == 0:
        assert "uid-is-root" in chk._violations(obs, chk._net_ns(), os.getcwd())


@NEEDS_ISO
def test_wrapped_child_has_fresh_cwd_and_refuses_listener():
    listener = chk._LoopbackListener()
    try:
        obs = chk._with_decoys(lambda: chk._observe_child(
            chk._iso_launch([sys.executable, str(PROBE)]), chk._allow_env(), listener.port, True))
    finally:
        listener.close()
    assert obs is not None
    assert obs["cwd"] != os.getcwd() and "rubric-cwd-" in obs["cwd"]  # fresh dir
    assert obs["net_reachable"] is False  # isolated netns refuses the listener
    assert chk._violations(obs, chk._net_ns(), os.getcwd()) == []


@NEEDS_ISO
def test_positive_fails_without_real_isolation(monkeypatch):
    monkeypatch.setattr(chk, "_iso_launch", lambda child: list(child))
    assert chk.positive(PROOF_DIR) == 1


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
