"""S0-11: Evaluation hardening conformance tests.

Covers the positive leg, the frozen seed credential control, the four-axis
negative, and a mutant kill-battery for every hollow green found in two owner
reviews: pass-through unshare, real credential names, RUBRIC_* wildcard leakage,
root/missing-field acceptance, os.chmod / subprocess chmod / hostNetwork bool /
network_mode host, symbolic chmod, forbidden ops hidden in the checker itself,
and a hazard-inverting design doc.

Isolation-dependent tests skip via the checker's own ``--selftest`` capability
predicate (exit 2) where the host cannot create/read the namespaces — the
isolation proof then runs on the PC/gVisor host. Allow-list, sweep, and design
tests are environment-independent and run everywhere.
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

_spec = importlib.util.spec_from_file_location("check_eval_hardening", CHECKER)
chk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chk)


def _run(*extra_args, env=None):
    return subprocess.run(
        [sys.executable, str(CHECKER)] + list(extra_args),
        capture_output=True, text=True, timeout=60, env=env,
    )


def _selftest_rc():
    try:
        return _run("--selftest").returncode
    except Exception:
        return 2


NEEDS_ISO = pytest.mark.skipif(
    _selftest_rc() == 2,
    reason="isolation capability unavailable (--selftest exit 2); the isolation "
           "proof runs on the PC/gVisor host (NOT run here)",
)


def _copy_proof(tmp_path):
    dst = tmp_path / "S0-11"
    shutil.copytree(PROOF_DIR, dst)
    return dst


# --- proof legs --------------------------------------------------------------
def test_selftest_reports_capability():
    r = _run("--selftest")
    assert r.returncode in (0, 2)
    assert r.stdout.strip() != ""


@NEEDS_ISO
def test_positive_conformance():
    r = _run(str(PROOF_DIR))
    assert r.returncode == 0, "checker failed: " + r.stdout + r.stderr
    assert r.stdout.strip() == "PASS"


def test_negative_frozen_credential_control():
    # Frozen seed control (must be preserved verbatim, env-independent).
    r = _run("--rubric-neg-cred", str(CRED_FIXTURE), str(PROOF_DIR))
    assert r.returncode == 1, r.stdout + r.stderr
    assert FROZEN_REASON in r.stdout
    assert "exit 1 per contract" in r.stdout


def test_negative_four_axis_covers_all_axes():
    r = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    assert r.returncode == 1, r.stdout + r.stderr
    assert "rubric-isolation-violation:" in r.stdout
    for axis in ("uid-not-dropped", "netns-not-isolated",
                 "network-reachable", "env-not-allowlisted"):
        assert axis in r.stdout, "axis missing: " + axis


def test_deterministic():
    r1 = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    r2 = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    assert r1.stdout == r2.stdout and r1.returncode == r2.returncode


def test_spec_valid_and_honors_frozen_seed_control():
    spec = json.loads(SPEC.read_text())
    jsonschema.validate(spec, json.loads(SPEC_SCHEMA.read_text()))
    assert spec["proof_id"] == "S0-11"
    negatives = [leg for leg in spec["legs"] if leg["leg"] == "negative"]
    assert len(negatives) >= 2, "need the frozen control AND the four-axis negative"
    reasons = [leg["expect"].get("failure_reason", "") for leg in negatives]
    assert any(r == FROZEN_REASON for r in reasons), "frozen seed reason must be a leg"


def test_fixtures_exist():
    assert (PROOF_DIR / "runner_design.md").exists()
    assert PROBE.exists()
    assert CRED_FIXTURE.exists()


def test_runner_design_covers_hazards():
    text = (PROOF_DIR / "runner_design.md").read_text().lower()
    assert "network isolation" in text or "no host network" in text
    assert "chmod 777" in text or "permission hardening" in text
    assert "credential" in text
    assert "not verified" in text or "filesystem containment" in text


# --- allow-list is a closed exact set, not a prefix wildcard -----------------
def test_allowlist_is_closed_exact_set():
    names = ["RUBRIC_PRODUCTION_API_KEY", "OMNIROUTE_INTERNAL_API_KEY", "BUZZ_PRIVATE_KEY"]
    saved = {n: os.environ.get(n) for n in names}
    for n in names:
        os.environ[n] = "sentinel"
    try:
        env = chk._probe_env(allowlisted=True, cwd="/tmp", port=1)
        for k in env:
            assert k in chk.ALLOWED_ENV, "allow-list leaked: " + k
        # a RUBRIC_*-named credential must be flagged, not passed by prefix
        v = chk._violations(
            {"uid": 65534, "net_ns": "A", "env_keys": sorted(list(env) + ["RUBRIC_PRODUCTION_API_KEY"]),
             "listener_reachable": False}, 0, "P")
        assert "env-not-allowlisted" in v
    finally:
        for n, val in saved.items():
            if val is None:
                os.environ.pop(n, None)
            else:
                os.environ[n] = val


# --- report validation: root uid and missing evidence ------------------------
def test_mutant_root_uid_caught():
    v = chk._violations({"uid": 0, "net_ns": "A", "env_keys": [], "listener_reachable": False}, 1000, "P")
    assert "uid-not-dropped" in v


def test_mutant_missing_report_fields_caught():
    v = chk._violations({"net_ns": "A", "listener_reachable": False}, 0, "P")
    assert any(d.startswith("report-") for d in v)
    v2 = chk._violations({"uid": 65534, "listener_reachable": False, "env_keys": []}, 0, "P")
    assert "report-netns-missing" in v2


# --- isolation mutants (need real capability) --------------------------------
@NEEDS_ISO
def test_mutant_passthrough_unshare_caught(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake = fake_bin / "unshare"
    fake.write_text('#!/bin/bash\nwhile [[ "$1" == --* || "$1" == "--" ]]; do shift; done\nexec "$@"\n')
    fake.chmod(0o755)
    env = dict(os.environ, PATH=str(fake_bin) + os.pathsep + os.environ["PATH"])
    r = _run(str(PROOF_DIR), env=env)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "rubric-isolation-failure:" in r.stdout


@NEEDS_ISO
def test_mutant_real_credential_names_stripped_end_to_end():
    env = dict(os.environ, BUZZ_PRIVATE_KEY="x", OMNIROUTE_INTERNAL_API_KEY="y",
               RUBRIC_PRODUCTION_API_KEY="z")
    r = _run(str(PROOF_DIR), env=env)
    assert r.returncode == 0, r.stdout + r.stderr


# --- structured forbidden-op sweep -------------------------------------------
def test_mutant_os_chmod_call_caught(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "harden.py").write_text("import os\nos.chmod('/workspace', 0o777)\n")
    assert chk.check_forbidden_ops(dst) is False


def test_mutant_subprocess_chmod_caught(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "harden.py").write_text("import subprocess\nsubprocess.run(['chmod','-R','0777','/x'])\n")
    assert chk.check_forbidden_ops(dst) is False


def test_mutant_hostnetwork_bool_yaml_caught(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "pod.yaml").write_text("apiVersion: v1\nspec:\n  hostNetwork: True\n")
    assert chk.check_forbidden_ops(dst) is False


def test_mutant_network_mode_host_yaml_caught(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "compose.yml").write_text("services:\n  rubric:\n    network_mode: host\n")
    assert chk.check_forbidden_ops(dst) is False


def test_mutant_chmod_0777_shell_caught(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "harden.sh").write_text("#!/bin/bash\nchmod -R 0777 /workspace\n")
    assert chk.check_forbidden_ops(dst) is False


def test_mutant_chmod_symbolic_caught(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "harden.sh").write_text("#!/bin/bash\nchmod -R go+rwx /workspace\n")
    assert chk.check_forbidden_ops(dst) is False


def test_mutant_forbidden_op_inside_checker_caught(tmp_path):
    # No self-exclusion hole: a forbidden call added to the checker copy is caught.
    dst = _copy_proof(tmp_path)
    text = (dst / "check_eval_hardening.py").read_text()
    (dst / "check_eval_hardening.py").write_text(text + "\nimport os as _o\n_o.chmod('/x', 0o777)\n")
    assert chk.check_forbidden_ops(dst) is False


def test_sweep_scans_yaml_but_not_markdown(tmp_path):
    dst = _copy_proof(tmp_path)
    assert chk.check_forbidden_ops(dst) is True
    (dst / "notes.md").write_text("Never run chmod 777 or set network_mode: host.\n")
    assert chk.check_forbidden_ops(dst) is True  # markdown documents hazards
    (dst / "bad.yaml").write_text("network_mode: host\n")
    assert chk.check_forbidden_ops(dst) is False


def test_benign_not_flagged():
    assert chk._python_prohibited("import os\nos.chmod('/x', 0o644)\n") is None
    assert chk._python_prohibited("import subprocess\nsubprocess.run(['ls','-la'])\n") is None
    assert chk._text_prohibited("chmod 755 file") is None


# --- design doc inversion guard ----------------------------------------------
def test_runner_design_rejects_inversion(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "runner_design.md").write_text(
        "netns unshare --net; credential isolation strip; permission hardening; chmod 777.\n"
        "But: network isolation is disabled; chmod 777 is required; credential passing is enabled.\n")
    assert chk.check_runner_design(dst) is False
