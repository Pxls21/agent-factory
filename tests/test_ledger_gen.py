"""Contract tests for the Stage 0 ledger generator.

Negative controls first: each asserts the exact failure before the positive.
All mutations happen in temporary copies; the repository never gains fake artifacts.
"""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "ledger-gen"
VALIDATOR = ROOT / "scripts" / "validate-ledger"
PROOF_IDS = [f"S0-{i:02d}" for i in range(1, 13)]


def _copy_contract(tmp_path):
    root = tmp_path / "repo"
    (root / "proofs" / "schemas").mkdir(parents=True)
    shutil.copy(ROOT / "proofs" / "registry.yaml", root / "proofs" / "registry.yaml")
    shutil.copy(ROOT / "proofs" / "normalization.yaml", root / "proofs" / "normalization.yaml")
    for schema in ("result.schema.json", "blocked.schema.json", "spike.schema.json"):
        shutil.copy(ROOT / "proofs" / "schemas" / schema, root / "proofs" / "schemas" / schema)
    return root


def _run_gen(root, output=None):
    cmd = [sys.executable, str(CLI), "--root", str(root)]
    if output:
        cmd += ["--output", str(output)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=10)


def _run_validate(root, ledger_path):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "integrity", "--root", str(root),
         "--ledger", str(ledger_path)],
        capture_output=True, text=True, timeout=10,
    )


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def _run_leg(leg, stdout=""):
    return {
        "leg": leg,
        "cmd": ["python3", "-c", f"print({stdout!r})"],
        "started_at": "2026-09-03T00:00:00Z",
        "finished_at": "2026-09-03T00:00:01Z",
        "exit_code": 0 if leg == "positive" else 1,
        "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256(b"").hexdigest(),
    }


def _result(proof_id="S0-01", classification="execution_proof",
            recorded_at="2026-09-03T00:00:02Z"):
    runs = [_run_leg("positive", "ok"), _run_leg("negative")]
    digest = hashlib.sha256(
        json.dumps(runs, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "proof_id": proof_id,
        "classification": classification,
        "recorded_at": recorded_at,
        "env_fingerprint": "sandbox:test",
        "runs": runs,
        "negative_control": {
            "fixture": "fixtures/test/negative.json",
            "expected_failure_reason": "expected-test-failure",
            "observed_failure_reason": "expected-test-failure",
        },
        "digest": digest,
    }


def _attested(root, proof_id, result):
    """Seed a proof input file and stamp the result with a matching attestation
    (now a required, tree-bound field re-derived from the proof directory)."""
    proof_dir = root / "proofs" / proof_id
    proof_dir.mkdir(parents=True, exist_ok=True)
    source = proof_dir / "spec.json"
    source.write_text(json.dumps({"proof_id": proof_id}) + "\n")
    result["attestation"] = {
        str(source.relative_to(root)): hashlib.sha256(source.read_bytes()).hexdigest()
    }
    return result


def _blocked(proof_id="S0-03", classification="blocked_credential",
             blocker_status="absent", env_fingerprint="pc-bridge:fedora"):
    return {
        "proof_id": proof_id,
        "classification": classification,
        "env_fingerprint": env_fingerprint,
        "marker": {
            "probe_cmd": ["sh", "-c", "exit 10"],
            "probe_run": {
                "leg": "negative",
                "cmd": ["sh", "-c", "exit 10"],
                "started_at": "2026-09-03T18:33:34Z",
                "finished_at": "2026-09-03T18:33:35Z",
                "exit_code": 10,
                "stdout_sha256": hashlib.sha256(b"").hexdigest(),
                "stderr_sha256": hashlib.sha256(b"").hexdigest(),
            },
            "blocker_status": blocker_status,
            "unblock_condition": "test condition",
            "owner": "test-owner",
            "reason": "credential_absent",
        },
    }


def _load_ledger(path):
    return json.loads(path.read_text())


# --- Negative controls ---

def test_missing_normalization_fails(tmp_path):
    root = _copy_contract(tmp_path)
    (root / "proofs" / "normalization.yaml").unlink()
    output = tmp_path / "ledger.json"

    completed = _run_gen(root, output)

    assert completed.returncode != 0
    assert not output.exists()


def test_forged_digest_produces_invalid(tmp_path):
    root = _copy_contract(tmp_path)
    artifact = _result()
    artifact["digest"] = "0" * 64
    _write_json(root / "proofs" / "S0-01" / "result.json", artifact)
    output = tmp_path / "ledger.json"

    completed = _run_gen(root, output)

    assert completed.returncode == 0
    ledger = _load_ledger(output)
    entry = next(p for p in ledger["proofs"] if p["proof_id"] == "S0-01")
    assert entry["state"] == "INVALID"


def test_substantive_change_alters_digest(tmp_path):
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / "S0-03" / "blocked.json",
                _blocked(blocker_status="absent"))
    output_a = tmp_path / "ledger_a.json"
    _run_gen(root, output_a)
    digest_a = next(
        p["normalized_digest"] for p in _load_ledger(output_a)["proofs"]
        if p["proof_id"] == "S0-03"
    )

    artifact = _blocked(blocker_status="absent")
    artifact["marker"]["unblock_condition"] = "changed condition"
    _write_json(root / "proofs" / "S0-03" / "blocked.json", artifact)
    output_b = tmp_path / "ledger_b.json"
    _run_gen(root, output_b)
    digest_b = next(
        p["normalized_digest"] for p in _load_ledger(output_b)["proofs"]
        if p["proof_id"] == "S0-03"
    )

    assert digest_a != digest_b


# --- Positive controls ---

def test_byte_identical(tmp_path):
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / "S0-03" / "blocked.json",
                _blocked(blocker_status="absent"))
    out_a = tmp_path / "a.json"
    out_b = tmp_path / "b.json"

    _run_gen(root, out_a)
    _run_gen(root, out_b)

    assert out_a.read_bytes() == out_b.read_bytes()


def test_empty_set_all_absent(tmp_path):
    root = _copy_contract(tmp_path)
    output = tmp_path / "ledger.json"

    completed = _run_gen(root, output)

    assert completed.returncode == 0
    ledger = _load_ledger(output)
    assert len(ledger["proofs"]) == 12
    for entry in ledger["proofs"]:
        assert entry["state"] == "ABSENT"
        assert "normalized_digest" not in entry


def test_result_present(tmp_path):
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / "S0-01" / "result.json", _attested(root, "S0-01", _result()))
    output = tmp_path / "ledger.json"

    completed = _run_gen(root, output)

    assert completed.returncode == 0
    entry = next(p for p in _load_ledger(output)["proofs"] if p["proof_id"] == "S0-01")
    assert entry["state"] == "PRESENT"
    assert entry["classification"] == "execution_proof"
    assert len(entry["normalized_digest"]) == 64


def test_blocked_state(tmp_path):
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / "S0-03" / "blocked.json",
                _blocked(blocker_status="absent"))
    output = tmp_path / "ledger.json"

    _run_gen(root, output)

    entry = next(p for p in _load_ledger(output)["proofs"] if p["proof_id"] == "S0-03")
    assert entry["state"] == "BLOCKED"
    assert len(entry["normalized_digest"]) == 64


def test_expired_state(tmp_path):
    root = _copy_contract(tmp_path)
    artifact = _blocked(proof_id="S0-08", classification="blocked_host",
                         blocker_status="expired")
    del artifact["marker"]["reason"]
    _write_json(root / "proofs" / "S0-08" / "blocked.json", artifact)
    output = tmp_path / "ledger.json"

    _run_gen(root, output)

    entry = next(p for p in _load_ledger(output)["proofs"] if p["proof_id"] == "S0-08")
    assert entry["state"] == "EXPIRED"
    assert len(entry["normalized_digest"]) == 64


def test_volatile_fields_irrelevant(tmp_path):
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / "S0-01" / "result.json",
                _result(recorded_at="2026-09-03T00:00:02Z"))
    out_a = tmp_path / "a.json"
    _run_gen(root, out_a)
    digest_a = next(
        p["normalized_digest"] for p in _load_ledger(out_a)["proofs"]
        if p["proof_id"] == "S0-01"
    )

    _write_json(root / "proofs" / "S0-01" / "result.json",
                _result(recorded_at="2026-12-25T23:59:59Z"))
    out_b = tmp_path / "b.json"
    _run_gen(root, out_b)
    digest_b = next(
        p["normalized_digest"] for p in _load_ledger(out_b)["proofs"]
        if p["proof_id"] == "S0-01"
    )

    assert digest_a == digest_b


def test_validates_with_integrity(tmp_path):
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / "S0-03" / "blocked.json",
                _blocked(blocker_status="absent"))
    output = tmp_path / "ledger.json"
    _run_gen(root, output)

    completed = _run_validate(root, output)

    assert completed.returncode == 0, completed.stdout


def test_sorted_by_proof_id(tmp_path):
    root = _copy_contract(tmp_path)
    output = tmp_path / "ledger.json"
    _run_gen(root, output)

    ledger = _load_ledger(output)
    ids = [p["proof_id"] for p in ledger["proofs"]]
    assert ids == sorted(ids) == PROOF_IDS
