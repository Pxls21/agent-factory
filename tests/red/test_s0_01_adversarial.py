"""RED verifier regressions for S0-01 (adversarial verify lane s0-01c, 2026-09-03; harvested from its
worktree after the lane died mid-run). Five findings accepted by the coordinator; the lane's sixth
(a code-shape assertion on a finding's message text) was graded INFO and dropped. Repair brief:
tasks/briefs/s0-01d-repair-verifier-reds.md — make these green, do not edit them."""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "validate-ledger"


def _copy_contract(tmp_path):
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "proofs", root / "proofs")
    return root


def _run(root, *extra):
    return subprocess.run(
        [sys.executable, str(CLI), "integrity", "--root", str(root), *map(str, extra)],
        capture_output=True,
        text=True,
        timeout=5,
    )


def _registry(root):
    path = root / "proofs" / "registry.yaml"
    text = "\n".join(line for line in path.read_text().splitlines() if not line.lstrip().startswith("#"))
    return path, json.loads(text)


def test_unknown_ledger_proof_id_is_rejected_not_silently_treated_as_absent(tmp_path):
    root = _copy_contract(tmp_path)
    ledger = root / "ledger.json"
    ledger.write_text(json.dumps({"proofs": [{"proof_id": "S0-99", "state": "ABSENT"}]}))

    completed = _run(root, "--ledger", ledger)

    assert completed.returncode == 1
    assert "registry-schema: ledger unknown proof_id S0-99" in completed.stdout


def test_non_mapping_class_aliases_has_a_registry_finding_not_a_traceback(tmp_path):
    root = _copy_contract(tmp_path)
    path, registry = _registry(root)
    registry["class_aliases"] = []
    path.write_text(json.dumps(registry))

    completed = _run(root)

    assert completed.returncode == 1
    assert "registry-schema: class_aliases must be an object" in completed.stdout
    assert completed.stderr == ""


def test_non_mapping_spike_mapping_has_a_registry_finding_not_a_traceback(tmp_path):
    root = _copy_contract(tmp_path)
    path, registry = _registry(root)
    registry["spike_to_class_mapping"] = {}
    path.write_text(json.dumps(registry))

    completed = _run(root)

    assert completed.returncode == 1
    assert "registry-schema: spike_to_class_mapping must be a list" in completed.stdout
    assert completed.stderr == ""


def test_mapping_entry_with_a_non_mapping_effect_has_a_registry_finding(tmp_path):
    root = _copy_contract(tmp_path)
    path, registry = _registry(root)
    registry["spike_to_class_mapping"][0]["negative_effect"] = []
    path.write_text(json.dumps(registry))

    completed = _run(root)

    assert completed.returncode == 1
    assert "registry-schema: map-rust-s006 negative_effect must be an object" in completed.stdout
    assert completed.stderr == ""


def test_result_requires_a_negative_leg_after_schema_mutation(tmp_path):
    root = _copy_contract(tmp_path)
    schema_path = root / "proofs" / "schemas" / "result.schema.json"
    schema = json.loads(schema_path.read_text())
    schema["properties"]["runs"]["allOf"][0]["minContains"] = 0
    schema_path.write_text(json.dumps(schema))

    empty_digest = hashlib.sha256(b"").hexdigest()
    runs = [
        {
            "leg": "positive",
            "cmd": ["true"],
            "started_at": "2026-09-03T00:00:00Z",
            "finished_at": "2026-09-03T00:00:01Z",
            "exit_code": 0,
            "stdout_sha256": empty_digest,
            "stderr_sha256": empty_digest,
        },
        {
            "leg": "positive",
            "cmd": ["true"],
            "started_at": "2026-09-03T00:00:00Z",
            "finished_at": "2026-09-03T00:00:01Z",
            "exit_code": 0,
            "stdout_sha256": empty_digest,
            "stderr_sha256": empty_digest,
        },
    ]
    artifact = {
        "proof_id": "S0-01",
        "classification": "execution_proof",
        "recorded_at": "2026-09-03T00:00:00Z",
        "env_fingerprint": "sandbox:test",
        "runs": runs,
        "negative_control": {
            "fixture": "x",
            "expected_failure_reason": "x",
            "observed_failure_reason": "x",
        },
        "digest": hashlib.sha256(
            json.dumps(runs, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    result = root / "proofs" / "S0-01" / "result.json"
    result.parent.mkdir(exist_ok=True)  # proofs/S0-01/ exists since GROUNDING.md landed (2026-09-04)
    result.write_text(json.dumps(artifact))

    completed = _run(root)

    assert completed.returncode == 1
    assert "runs:" in completed.stdout
    assert completed.stderr == ""


