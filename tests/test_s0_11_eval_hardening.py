"""S0-11: Evaluation hardening conformance tests.

Covers the positive/negative proof legs, the four isolation axes, and a
mutant kill-battery for every hollow green the owner reproduced:
pass-through ``unshare``, real credential names, ``network_mode: host`` in
YAML, ``chmod -R 0777``, and symbolic world-writable ``chmod``.

Isolation-dependent tests skip with an explicit reason where
``unshare --user --net`` is unavailable (e.g. AppArmor-restricted runners) —
the isolation proof then runs on the PC/gVisor host, and the grep-sweep and
allow-list mutants (environment-independent) still run everywhere.
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
SPEC = PROOF_DIR / "spec.json"
SPEC_SCHEMA = REPO / "proofs" / "schemas" / "spec.schema.json"

_spec = importlib.util.spec_from_file_location("check_eval_hardening", CHECKER)
chk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chk)


def _isolation_available() -> bool:
    try:
        r = subprocess.run(
            ["unshare", "--user", "--net", "--", sys.executable, "-c",
             "import os;print(os.getuid())"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return r.returncode == 0 and r.stdout.strip() not in ("", str(os.getuid()))


NEEDS_ISO = pytest.mark.skipif(
    not _isolation_available(),
    reason="unshare --user --net unavailable; isolation proof runs on the "
           "PC/gVisor host (NOT run here)",
)


def _run(*extra_args, env=None):
    return subprocess.run(
        [sys.executable, str(CHECKER)] + list(extra_args),
        capture_output=True, text=True, timeout=60, env=env,
    )


# --- proof legs --------------------------------------------------------------
@NEEDS_ISO
def test_positive_conformance():
    r = _run(str(PROOF_DIR))
    assert r.returncode == 0, "checker failed: " + r.stdout + r.stderr
    assert r.stdout.strip() == "PASS"


def test_negative_control_reports_violation():
    r = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    assert r.returncode == 1, "expected rc=1, got " + str(r.returncode) + ": " + r.stdout
    assert "rubric-isolation-violation:" in r.stdout
    assert "exit 1 per contract" in r.stdout


def test_negative_control_covers_all_axes():
    # The un-wrapped probe must be breached on every axis (non-vacuity of each).
    r = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    for axis in ("uid-not-dropped", "netns-not-isolated",
                 "network-reachable", "env-not-allowlisted"):
        assert axis in r.stdout, "axis missing from negative control: " + axis


def test_deterministic():
    r1 = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    r2 = _run("--rubric-neg", str(PROBE), str(PROOF_DIR))
    assert r1.stdout == r2.stdout
    assert r1.returncode == r2.returncode


def test_spec_valid():
    spec = json.loads(SPEC.read_text())
    schema = json.loads(SPEC_SCHEMA.read_text())
    jsonschema.validate(spec, schema)
    assert spec["proof_id"] == "S0-11"
    neg = [leg for leg in spec["legs"] if leg["leg"] == "negative"]
    assert neg and neg[0]["expect"]["exit_code"] == 1
    assert "rubric-isolation-violation:" in neg[0]["expect"]["failure_reason"]


def test_fixtures_exist():
    assert (PROOF_DIR / "runner_design.md").exists()
    assert PROBE.exists()


def test_runner_design_covers_hazards():
    text = (PROOF_DIR / "runner_design.md").read_text().lower()
    assert "network isolation" in text or "no host network" in text
    assert "chmod 777" in text or "permission hardening" in text
    assert "credential" in text
    # honest gap must be stated, not overclaimed
    assert "not verified" in text or "filesystem containment" in text


# --- mutant kill-battery: isolation axes (need real isolation) ---------------
@NEEDS_ISO
def test_mutant_passthrough_unshare_caught(tmp_path):
    # A fake `unshare` that drops --user/--net and execs the rest must be
    # rejected: uid stays root, netns unchanged, listener reachable, env leaks.
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake = fake_bin / "unshare"
    fake.write_text('#!/bin/bash\nwhile [[ "$1" == --* || "$1" == "--" ]]; do shift; done\nexec "$@"\n')
    fake.chmod(0o755)
    env = dict(os.environ, PATH=str(fake_bin) + os.pathsep + os.environ["PATH"])
    r = _run(str(PROOF_DIR), env=env)
    assert r.returncode == 1
    assert "rubric-isolation-failure:" in r.stdout


@NEEDS_ISO
def test_mutant_real_credential_names_stripped_end_to_end(tmp_path):
    # Real production credential names in the ambient env must not defeat the
    # allow-list: the proof still passes because they are stripped.
    env = dict(os.environ)
    env.update({
        "BUZZ_PRIVATE_KEY": "x",
        "OMNIROUTE_INTERNAL_API_KEY": "y",
        "STORAGE_ENCRYPTION_KEY": "z",
    })
    r = _run(str(PROOF_DIR), env=env)
    assert r.returncode == 0, r.stdout + r.stderr


# --- mutant kill-battery: allow-list + grep sweep (env-independent) ----------
def test_allowlist_strips_real_credentials():
    saved = {}
    names = ["BUZZ_PRIVATE_KEY", "OMNIROUTE_INTERNAL_API_KEY", "STORAGE_ENCRYPTION_KEY"]
    for n in names:
        saved[n] = os.environ.get(n)
        os.environ[n] = "ambient-secret"
    try:
        env = chk._probe_env(allowlisted=True, cwd="/tmp", port=1)
    finally:
        for n in names:
            if saved[n] is None:
                os.environ.pop(n, None)
            else:
                os.environ[n] = saved[n]
    for n in names:
        assert n not in env, "allow-list leaked credential: " + n
    # only allow-listed + RUBRIC_* keys survive
    for k in env:
        assert k in chk.ENV_ALLOWLIST or k.startswith(chk.RUBRIC_PREFIX)


def _copy_proof(tmp_path):
    dst = tmp_path / "S0-11"
    shutil.copytree(PROOF_DIR, dst)
    return dst


def test_mutant_hostnet_yaml_caught(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "docker-compose.yml").write_text("services:\n  rubric:\n    network_mode: host\n")
    assert chk.check_grep_sweep(dst) is False


def test_mutant_chmod_0777_caught(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "harden.sh").write_text("#!/bin/bash\nchmod -R 0777 /workspace\n")
    assert chk.check_grep_sweep(dst) is False


def test_mutant_chmod_symbolic_caught(tmp_path):
    dst = _copy_proof(tmp_path)
    (dst / "harden.sh").write_text("#!/bin/bash\nchmod -R go+rwx /workspace\n")
    assert chk.check_grep_sweep(dst) is False


def test_grep_sweep_scans_yaml_but_not_markdown(tmp_path):
    # YAML/Dockerfile/etc are scanned; markdown docs (which name the hazards on
    # purpose) are not — the design doc must not self-flag.
    dst = _copy_proof(tmp_path)
    assert chk.check_grep_sweep(dst) is True  # baseline clean
    (dst / "notes.md").write_text("We must never run chmod 777 or network_mode: host.\n")
    assert chk.check_grep_sweep(dst) is True  # markdown not flagged
    (dst / "compose.yaml").write_text("network_mode: host\n")
    assert chk.check_grep_sweep(dst) is False  # yaml flagged


def test_benign_chmod_not_flagged():
    for s in ("chmod 644 x", "chmod 0644 x", "chmod 755 x", "chmod u+x s.sh", "chmod 600 key"):
        assert chk._prohibited(s) is None, "false positive: " + s
    for s in ("chmod 777 x", "chmod -R 0777 x", "chmod go+rwx x", "network_mode: host"):
        assert chk._prohibited(s) is not None, "missed: " + s
