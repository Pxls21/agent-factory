"""Proof-runner contract tests; all artifacts and doubles stay under tmp_path."""
import hashlib
import http.server
import json
import os
import pathlib
import secrets
import shutil
import subprocess
import sys
import threading
import time

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "proof-runner"
VALIDATOR = ROOT / "scripts" / "validate-ledger"
SCHEMAS = ("spec.schema.json", "probe.schema.json", "result.schema.json", "blocked.schema.json", "spike.schema.json")


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def _copy_contract(tmp_path):
    root = tmp_path / "repo"
    (root / "proofs" / "schemas").mkdir(parents=True)
    shutil.copy(ROOT / "proofs" / "registry.yaml", root / "proofs" / "registry.yaml")
    for name in SCHEMAS:
        shutil.copy(ROOT / "proofs" / "schemas" / name, root / "proofs" / "schemas" / name)
    return root


def _copy_probe(root, proof_id):
    target = root / "proofs" / proof_id
    target.mkdir(parents=True, exist_ok=True)
    for source in (ROOT / "proofs" / proof_id).iterdir():
        if source.is_file() and source.name != "blocked.json":
            shutil.copy(source, target / source.name)
    return target


def _runner(root, verb, proof_id, *, env=None, runner=RUNNER):
    return subprocess.run(
        [sys.executable, str(runner), verb, "--proof", proof_id, "--venue", "sandbox", "--root", str(root)],
        capture_output=True,
        text=True,
        timeout=8,
        env=env,
    )


def _validator(root):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "integrity", "--root", str(root)],
        capture_output=True,
        text=True,
        timeout=5,
    )


def _spec(proof_id="S0-01"):
    return {
        "proof_id": proof_id,
        "legs": [
            {
                "leg": "negative",
                "cmd": [sys.executable, "-c", "import sys; print('expected-denial', file=sys.stderr); raise SystemExit(7)"],
                "cwd": ".",
                "timeout_s": 2,
                "expect": {"exit_code": 7, "failure_reason": "expected-denial"},
            },
            {
                "leg": "positive",
                "cmd": [sys.executable, "-c", "print('accepted')"],
                "cwd": ".",
                "timeout_s": 2,
                "expect": {"exit_code": 0},
            },
        ],
    }


# Negative controls precede positive controls.
def test_negative_control_without_reason_writes_no_result(tmp_path):
    root = _copy_contract(tmp_path)
    spec = _spec()
    spec["legs"][0]["cmd"] = [sys.executable, "-c", "raise SystemExit(7)"]
    _write_json(root / "proofs" / "S0-01" / "spec.json", spec)

    completed = _runner(root, "run", "S0-01")

    assert completed.returncode == 1
    assert "negative-control-unmet: S0-01" in completed.stderr
    assert not (root / "proofs" / "S0-01" / "result.json").exists()


def test_unexpected_leg_exit_writes_no_result(tmp_path):
    root = _copy_contract(tmp_path)
    spec = _spec()
    spec["legs"][1]["cmd"] = [sys.executable, "-c", "raise SystemExit(9)"]
    _write_json(root / "proofs" / "S0-01" / "spec.json", spec)

    completed = _runner(root, "run", "S0-01")

    assert completed.returncode == 1
    assert "leg-exit-mismatch: S0-01 positive expected 0 got 9" in completed.stderr
    assert not (root / "proofs" / "S0-01" / "result.json").exists()


def test_every_negative_leg_must_emit_its_expected_reason(tmp_path):
    root = _copy_contract(tmp_path)
    spec = _spec()
    spec["legs"].insert(
        1,
        {
            "leg": "negative",
            "cmd": [sys.executable, "-c", "raise SystemExit(8)"],
            "cwd": ".",
            "timeout_s": 2,
            "expect": {"exit_code": 8, "failure_reason": "second-denial"},
        },
    )
    _write_json(root / "proofs" / "S0-01" / "spec.json", spec)

    completed = _runner(root, "run", "S0-01")

    assert completed.returncode == 1
    assert "negative-control-unmet: S0-01" in completed.stderr
    assert not (root / "proofs" / "S0-01" / "result.json").exists()


def test_timeout_kills_the_leg_process_group_and_is_recorded(tmp_path):
    root = _copy_contract(tmp_path)
    spec = _spec()
    pid_path = root / "child.pid"
    code = (
        "import os,pathlib,subprocess,sys,time; "
        "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); "
        f"pathlib.Path({str(pid_path)!r}).write_text(str(os.getpid())+' '+str(child.pid)); "
        "time.sleep(30)"
    )
    spec["legs"][1].update({"cmd": [sys.executable, "-c", code], "timeout_s": 1, "expect": {"exit_code": -9}})
    _write_json(root / "proofs" / "S0-01" / "spec.json", spec)

    started = time.monotonic()
    completed = _runner(root, "run", "S0-01")
    elapsed = time.monotonic() - started

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert elapsed <= 2
    pids = [int(value) for value in pid_path.read_text().split()]
    deadline = time.monotonic() + 1
    while time.monotonic() < deadline and any((pathlib.Path("/proc") / str(pid)).exists() for pid in pids):
        time.sleep(0.01)
    for pid in pids:
        status = pathlib.Path("/proc") / str(pid) / "stat"
        assert not status.exists() or status.read_text().split()[2] == "Z"
    result = json.loads((root / "proofs" / "S0-01" / "result.json").read_text())
    assert next(run for run in result["runs"] if run["leg"] == "positive")["exit_code"] == -9


def test_parent_environment_is_not_inherited_by_legs(tmp_path):
    root = _copy_contract(tmp_path)
    spec = _spec()
    env_path = root / "environment.json"
    spec["legs"][1]["cmd"] = [
        sys.executable,
        "-c",
        f"import json,os,pathlib; pathlib.Path({str(env_path)!r}).write_text(json.dumps(dict(os.environ)))",
    ]
    spec["legs"][1]["env"] = {"EXPLICIT_FOR_LEG": "present"}
    _write_json(root / "proofs" / "S0-01" / "spec.json", spec)
    environment = os.environ.copy()
    environment["CANARY_FROM_PARENT"] = "must-not-cross"

    completed = _runner(root, "run", "S0-01", env=environment)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    observed = json.loads(env_path.read_text())
    assert observed["EXPLICIT_FOR_LEG"] == "present"
    assert "CANARY_FROM_PARENT" not in observed
    assert set(observed) <= {"PATH", "HOME", "LANG", "EXPLICIT_FOR_LEG", "LC_CTYPE"}


def test_spec_classification_is_rejected_and_registry_classification_is_used(tmp_path):
    root = _copy_contract(tmp_path)
    spec = _spec("S0-09")
    spec["classification"] = "execution_proof"
    _write_json(root / "proofs" / "S0-09" / "spec.json", spec)

    rejected = _runner(root, "run", "S0-09")

    assert rejected.returncode == 1
    assert "Additional properties are not allowed ('classification' was unexpected)" in rejected.stderr
    assert not (root / "proofs" / "S0-09" / "result.json").exists()

    del spec["classification"]
    _write_json(root / "proofs" / "S0-09" / "spec.json", spec)
    accepted = _runner(root, "run", "S0-09")
    result = json.loads((root / "proofs" / "S0-09" / "result.json").read_text())

    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    assert result["classification"] == "conformance_checked_decision"


def test_unmapped_probe_exit_writes_no_marker(tmp_path):
    root = _copy_contract(tmp_path)
    probe_dir = _copy_probe(root, "S0-08")
    probe = json.loads((probe_dir / "probe.json").read_text())
    probe["probe_cmd"] = [sys.executable, "-c", "raise SystemExit(12)"]
    _write_json(probe_dir / "probe.json", probe)

    completed = _runner(root, "probe", "S0-08")

    assert completed.returncode == 1
    assert "probe-invalid: S0-08 exit 12" in completed.stderr
    assert not (probe_dir / "blocked.json").exists()


def test_runsc_absence_blocks_and_success_expires_the_deferral(tmp_path):
    root = _copy_contract(tmp_path)
    probe_dir = _copy_probe(root, "S0-08")
    empty_path = root / "bin"
    empty_path.mkdir()
    probe = json.loads((probe_dir / "probe.json").read_text())
    probe["env"] = {"PATH": str(empty_path)}
    probe["probe_cmd"] = [str(probe_dir / "probe_runsc.sh")]
    _write_json(probe_dir / "probe.json", probe)

    absent = _runner(root, "probe", "S0-08")
    marker = json.loads((probe_dir / "blocked.json").read_text())
    marker_schema = json.loads((root / "proofs" / "schemas" / "blocked.schema.json").read_text())
    integrity = _validator(root)

    assert absent.returncode == 0, absent.stdout + absent.stderr
    jsonschema.Draft202012Validator(
        marker_schema, format_checker=jsonschema.FormatChecker()
    ).validate(marker)
    assert marker["marker"]["blocker_status"] == "absent"
    assert marker["marker"]["reason"] == "capability_absent"
    assert integrity.returncode == 0, integrity.stdout + integrity.stderr
    assert "S0-08 BLOCKED" in integrity.stdout

    runsc = empty_path / "runsc"
    runsc.write_text("#!/bin/sh\nexit 0\n")
    runsc.chmod(0o755)
    expired = _runner(root, "probe", "S0-08")
    marker = json.loads((probe_dir / "blocked.json").read_text())
    integrity = _validator(root)

    assert expired.returncode == 0, expired.stdout + expired.stderr
    assert marker["marker"]["blocker_status"] == "expired"
    assert "reason" not in marker["marker"]
    # Coordinator decision (2026-09-03): expiry is a STATE for integrity (honest marker, exit 0)
    # and a RED for stage1-gate (the proof must run) — never an integrity finding.
    assert integrity.returncode == 0, integrity.stdout + integrity.stderr
    assert "S0-08 EXPIRED" in integrity.stdout
    assert "deferral-expired" not in integrity.stdout
    assert "blocked_host numerator=0 denominator=1" in integrity.stdout
    gate = subprocess.run(
        [sys.executable, str(VALIDATOR), "stage1-gate", "--root", str(root)],
        capture_output=True, text=True, timeout=10,
    )
    assert gate.returncode == 2, gate.stdout + gate.stderr
    assert "missing: S0-08 (blocked_host; deferral expired — the proof must run)" in gate.stdout


class _RejectingHandler(http.server.BaseHTTPRequestHandler):
    authorization = None

    def do_GET(self):
        type(self).authorization = self.headers.get("Authorization")
        self.send_response(401)
        self.end_headers()

    def log_message(self, format, *args):
        pass


def test_credential_absence_blocks_and_rejection_is_proof_red_without_secret_leak(tmp_path):
    root = _copy_contract(tmp_path)
    probe_dir = _copy_probe(root, "S0-03")
    environment = os.environ.copy()
    environment.pop("OMNIROUTE_API_KEY", None)

    absent = _runner(root, "probe", "S0-03", env=environment)
    marker = json.loads((probe_dir / "blocked.json").read_text())

    assert absent.returncode == 0, absent.stdout + absent.stderr
    assert marker["marker"]["blocker_status"] == "absent"
    assert marker["marker"]["reason"] == "credential_absent"
    assert _validator(root).returncode == 0

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _RejectingHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        probe = json.loads((probe_dir / "probe.json").read_text())
        probe["probe_cmd"][-1] = f"http://127.0.0.1:{server.server_port}/v1/models"
        _write_json(probe_dir / "probe.json", probe)
        secret = secrets.token_hex(24)
        environment["OMNIROUTE_API_KEY"] = secret
        rejected = _runner(root, "probe", "S0-03", env=environment)
    finally:
        server.shutdown()
        thread.join()
        server.server_close()

    marker = json.loads((probe_dir / "blocked.json").read_text())
    integrity = _validator(root)
    assert rejected.returncode == 0, rejected.stdout + rejected.stderr
    assert _RejectingHandler.authorization == f"Bearer {secret}"
    assert marker["marker"]["blocker_status"] == "rejecting"
    assert marker["marker"]["reason"] == "credential_rejected"
    assert integrity.returncode == 1
    assert "S0-03 INVALID" in integrity.stdout
    assert "credential rejection is not a valid blocked marker" in integrity.stdout
    assert all(secret not in path.read_text(errors="ignore") for path in root.rglob("*") if path.is_file())


# Positive proof and digest controls.
def test_valid_result_matches_schema_validator_digest_and_integrity(tmp_path):
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / "S0-01" / "spec.json", _spec())

    completed = _runner(root, "run", "S0-01")
    result_path = root / "proofs" / "S0-01" / "result.json"
    result = json.loads(result_path.read_text())
    schema = json.loads((root / "proofs" / "schemas" / "result.schema.json").read_text())
    expected_digest = hashlib.sha256(
        json.dumps(result["runs"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    integrity = _validator(root)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(result)
    assert result["digest"] == expected_digest
    assert result["negative_control"]["observed_failure_reason"] == "expected-denial"
    assert integrity.returncode == 0, integrity.stdout + integrity.stderr
    assert "S0-01 PRESENT" in integrity.stdout


def test_indent_two_digest_mutant_is_rejected(tmp_path):
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / "S0-01" / "spec.json", _spec())
    assert _runner(root, "run", "S0-01").returncode == 0
    result_path = root / "proofs" / "S0-01" / "result.json"
    result = json.loads(result_path.read_text())
    result["digest"] = hashlib.sha256(json.dumps(result["runs"], sort_keys=True, indent=2).encode()).hexdigest()
    _write_json(result_path, result)

    completed = _validator(root)

    assert completed.returncode == 1
    assert completed.stdout.splitlines().count("digest-mismatch: S0-01") == 1
