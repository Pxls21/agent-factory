"""Contract tests for the Stage 0 proof ledger validator.

The integrity negatives are intentionally authored before their positive controls.
All mutations happen in temporary copies; the repository never gains fake proof artifacts.
"""
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys

import jsonschema
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "validate-ledger"
# The CLI is spawned under sys.executable (the interpreter running pytest = the project
# venv that declares jsonschema). Spawning it through its shebang would inherit whatever
# `python3` is first on PATH: the PC's system python carried jsonschema and minted a
# 33/33 green the sandbox could not reproduce (AF-AP-11, 2026-09-03).
CLASSES = (
    "execution_proof",
    "conformance_checked_decision",
    "blocked_credential",
    "blocked_host",
)
PROOF_IDS = [f"S0-{index:02d}" for index in range(1, 13)]


def _copy_contract(tmp_path):
    root = tmp_path / "repo"
    (root / "proofs" / "schemas").mkdir(parents=True)
    shutil.copy(ROOT / "proofs" / "registry.yaml", root / "proofs" / "registry.yaml")
    for schema in ("result.schema.json", "blocked.schema.json", "spike.schema.json"):
        shutil.copy(ROOT / "proofs" / "schemas" / schema, root / "proofs" / "schemas" / schema)
    return root


def _load_registry(path):
    text = "\n".join(
        line for line in path.read_text().splitlines() if not line.lstrip().startswith("#")
    )
    return json.loads(text)


def _run(root, subcommand="integrity", *extra):
    return subprocess.run(
        [sys.executable, str(CLI), subcommand, "--root", str(root), *map(str, extra)],
        capture_output=True,
        text=True,
        timeout=5,
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


def _result(proof_id="S0-01", classification="execution_proof"):
    runs = [_run_leg("positive", "ok"), _run_leg("negative")]
    digest = hashlib.sha256(
        json.dumps(runs, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "proof_id": proof_id,
        "classification": classification,
        "recorded_at": "2026-09-03T00:00:02Z",
        "env_fingerprint": "sandbox:test",
        "runs": runs,
        "negative_control": {
            "fixture": "fixtures/test/negative.json",
            "expected_failure_reason": "expected-test-failure",
            "observed_failure_reason": "expected-test-failure",
        },
        "digest": digest,
    }


def _load_validator():
    loader = importlib.machinery.SourceFileLoader("stage0_validate_ledger", str(CLI))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
    loader.exec_module(module)
    return module


def _attested(root, proof_id, result):
    """Seed a proof input file and stamp the result with a matching attestation,
    computed by the REAL validator so it covers the whole trust closure (runner,
    validator, registry, schemas, proof-local inputs) that the validator will
    re-derive from this root."""
    proof_dir = root / "proofs" / proof_id
    proof_dir.mkdir(parents=True, exist_ok=True)
    (proof_dir / "spec.json").write_text(json.dumps({"proof_id": proof_id}) + "\n")
    result["attestation"] = _load_validator().proof_attestation(root, proof_id)
    return result


def _empty_lines():
    return [*(f"{proof_id} ABSENT" for proof_id in PROOF_IDS),
            "blocked_credential numerator=0 denominator=1",
            "blocked_host numerator=0 denominator=1",
            "conformance_checked_decision numerator=0 denominator=3",
            "execution_proof numerator=0 denominator=7"]


# Negative controls first: each asserts the contract's exact reason and exit code.
def test_cli_does_not_require_undeclared_yaml_dependency(tmp_path):
    root = _copy_contract(tmp_path)
    blocker = tmp_path / "import-blocker"
    blocker.mkdir()
    (blocker / "sitecustomize.py").write_text(
        "import builtins\n"
        "real_import = builtins.__import__\n"
        "def guarded(name, *args, **kwargs):\n"
        "    if name == 'yaml':\n"
        "        raise ModuleNotFoundError('yaml blocked by contract test')\n"
        "    return real_import(name, *args, **kwargs)\n"
        "builtins.__import__ = guarded\n"
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(blocker)

    completed = subprocess.run(
        [sys.executable, str(CLI), "integrity", "--root", str(root)],
        capture_output=True,
        text=True,
        timeout=5,
        env=environment,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_forged_digest_fails_for_exact_reason(tmp_path):
    root = _copy_contract(tmp_path)
    artifact = _result()
    artifact["runs"][0]["cmd"][-1] = "print('forged')"
    _write_json(root / "proofs" / "S0-01" / "result.json", artifact)

    completed = _run(root)

    assert completed.returncode == 1
    assert completed.stdout.splitlines().count("digest-mismatch: S0-01") == 1


def test_ledger_claim_over_empty_set_fails_for_exact_reason(tmp_path):
    root = _copy_contract(tmp_path)
    ledger = root / "ledger.json"
    _write_json(ledger, {"proofs": [{"proof_id": "S0-01", "state": "PASSED"}]})

    completed = _run(root, "integrity", "--ledger", ledger)

    assert completed.returncode == 1
    assert "ledger-drift: S0-01 claimed PASSED but ABSENT" in completed.stdout


def test_registry_missing_classification_fails_as_registry_schema(tmp_path):
    root = _copy_contract(tmp_path)
    registry_path = root / "proofs" / "registry.yaml"
    registry = _load_registry(registry_path)
    del registry["proofs"][0]["classification"]
    registry_path.write_text(json.dumps(registry))

    completed = _run(root)

    assert completed.returncode == 1
    assert "registry-schema: S0-01 missing classification" in completed.stdout


def test_registry_unknown_class_fails_for_exact_reason(tmp_path):
    root = _copy_contract(tmp_path)
    registry_path = root / "proofs" / "registry.yaml"
    registry = _load_registry(registry_path)
    registry["proofs"][0]["classification"] = "fifth_class"
    registry_path.write_text(json.dumps(registry))

    completed = _run(root)

    assert completed.returncode == 1
    assert "unknown-class: S0-01 fifth_class" in completed.stdout


@pytest.mark.parametrize(
    "effect",
    [
        {"affected_proof": "S0-03", "from_class": "blocked_credential", "to_class": "execution_proof", "rule_id": "unknown-rule"},
        {"affected_proof": "S0-03", "from_class": "blocked_host", "to_class": "execution_proof", "rule_id": "map-pcbridge-s003"},
    ],
)
def test_undeclared_spike_transition_fails_for_exact_reason(tmp_path, effect):
    root = _copy_contract(tmp_path)
    spike = {
        "spike_id": "pc-bridge",
        "schema": "proofs/schemas/spike.schema.json",
        "outcome": "positive",
        "ran_at": "2026-09-03T00:00:00Z",
        "env_fingerprint": "pc-bridge:test",
        "runs": [{"command": "true", "exit_code": 0, "stdout_digest": hashlib.sha256(b"").hexdigest()}],
        "facts": {},
        "classification_effect": [effect],
        "not_verified": [],
    }
    _write_json(root / "spikes" / "pc-bridge" / "result.json", spike)

    completed = _run(root)

    assert completed.returncode == 1
    assert "undeclared-transition: pc-bridge " + effect["from_class"] + "->" + effect["to_class"] in completed.stdout


def test_spike_effect_cannot_borrow_another_rule_for_same_class_pair(tmp_path):
    root = _copy_contract(tmp_path)
    spike = json.loads((ROOT / "spikes" / "pc-bridge" / "result.json").read_text())
    spike["classification_effect"][0] = {
        "affected_proof": "S0-01",
        "from_class": "execution_proof",
        "to_class": "execution_proof",
        "rule_id": "map-rust-s006",
    }
    _write_json(root / "spikes" / "pc-bridge" / "result.json", spike)

    completed = _run(root)

    assert completed.returncode == 1
    assert "undeclared-transition: pc-bridge execution_proof->execution_proof" in completed.stdout


def test_spike_effect_cannot_change_registry_class_without_a_proof_artifact(tmp_path):
    root = _copy_contract(tmp_path)
    spike_path = root / "spikes" / "pc-bridge" / "result.json"
    spike_path.parent.mkdir(parents=True)
    shutil.copy(ROOT / "spikes" / "pc-bridge" / "result.json", spike_path)

    completed = _run(root)

    assert completed.returncode == 0
    assert "S0-03 ABSENT" in completed.stdout
    assert "blocked_credential numerator=0 denominator=1" in completed.stdout


@pytest.mark.parametrize(
    ("directory", "filename", "artifact", "expected"),
    [
        (
            "S0-01",
            "result.json",
            _result(proof_id="S0-02"),
            "registry-schema: S0-01 result proof_id mismatch S0-02",
        ),
        (
            "S0-08",
            "blocked.json",
            {
                "proof_id": "S0-01",
                "classification": "blocked_host",
                "env_fingerprint": "sandbox:test",
                "marker": {
                    "probe_cmd": ["command", "-v", "runsc"],
                    "probe_run": _run_leg("negative"),
                    "blocker_status": "absent",
                    "unblock_condition": "runsc works",
                    "owner": "TBD-owner-gvisor-host",
                },
            },
            "registry-schema: S0-08 blocked proof_id mismatch S0-01",
        ),
    ],
)
def test_artifact_proof_id_must_match_its_directory(
    tmp_path, directory, filename, artifact, expected
):
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / directory / filename, artifact)

    completed = _run(root)

    assert completed.returncode == 1
    assert expected in completed.stdout


def test_invalid_spike_uses_the_exact_reason_prefix(tmp_path):
    root = _copy_contract(tmp_path)
    spike = json.loads((ROOT / "spikes" / "pc-bridge" / "result.json").read_text())
    spike["unexpected"] = True
    _write_json(root / "spikes" / "pc-bridge" / "result.json", spike)

    completed = _run(root)

    assert completed.returncode == 1
    assert "spike-artifact-invalid: pc-bridge: Additional properties" in completed.stdout


def test_extra_top_level_properties_are_rejected_by_all_schemas(tmp_path):
    root = _copy_contract(tmp_path)
    samples = {
        "result.schema.json": _result(),
        "blocked.schema.json": {
            "proof_id": "S0-08",
            "classification": "blocked_host",
            "env_fingerprint": "sandbox:test",
            "marker": {
                "probe_cmd": ["command", "-v", "runsc"],
                "probe_run": _run_leg("negative"),
                "blocker_status": "absent",
                "unblock_condition": "runsc works",
                "owner": "TBD-owner-gvisor-host",
            },
        },
        "spike.schema.json": {
            "spike_id": "test",
            "schema": "proofs/schemas/spike.schema.json",
            "outcome": "positive",
            "ran_at": "2026-09-03T00:00:00Z",
            "env_fingerprint": "sandbox:test",
            "runs": [],
            "facts": {},
            "classification_effect": [],
            "not_verified": [],
        },
    }
    for name, sample in samples.items():
        schema = json.loads((root / "proofs" / "schemas" / name).read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        sample["unexpected"] = True
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(sample, schema)


def test_rejecting_credential_probe_is_not_a_valid_blocked_marker(tmp_path):
    root = _copy_contract(tmp_path)
    marker = {
        "proof_id": "S0-03",
        "classification": "blocked_credential",
        "env_fingerprint": "sandbox:test",
        "marker": {
            "probe_cmd": ["credential-probe"],
            "probe_run": _run_leg("negative"),
            "blocker_status": "rejecting",
            "unblock_condition": "credential accepted",
            "owner": "TBD-owner-credential",
        },
    }
    _write_json(root / "proofs" / "S0-03" / "blocked.json", marker)

    completed = _run(root)

    assert completed.returncode == 1
    assert "registry-schema: S0-03 credential rejection is not a valid blocked marker" in completed.stdout


@pytest.mark.parametrize("digest", ["0" * 63, "A" * 64])
def test_result_schema_rejects_noncanonical_digest(tmp_path, digest):
    root = _copy_contract(tmp_path)
    artifact = _result()
    artifact["digest"] = digest
    schema = json.loads((root / "proofs" / "schemas" / "result.schema.json").read_text())

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(artifact, schema)


# Positive controls.
def test_empty_set_integrity_is_honest_and_deterministic(tmp_path):
    root = _copy_contract(tmp_path)

    first = _run(root)
    second = _run(root)

    assert first.returncode == second.returncode == 0
    assert first.stdout.encode() == second.stdout.encode()
    assert first.stderr == second.stderr == ""
    assert first.stdout.splitlines() == _empty_lines()


def test_empty_set_stage1_gate_names_all_twelve_and_is_deterministic(tmp_path):
    root = _copy_contract(tmp_path)
    registry = _load_registry(root / "proofs" / "registry.yaml")
    expected = [f"missing: {entry['proof_id']} ({entry['classification']})" for entry in registry["proofs"]]

    first = _run(root, "stage1-gate")
    second = _run(root, "stage1-gate")

    assert first.returncode == second.returncode == 2
    assert first.stdout.encode() == second.stdout.encode()
    assert first.stderr == second.stderr == ""
    assert first.stdout.splitlines() == expected


def test_valid_result_is_present_and_increments_its_class(tmp_path):
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / "S0-01" / "result.json", _attested(root, "S0-01", _result()))

    completed = _run(root)

    assert completed.returncode == 0
    assert "S0-01 PRESENT" in completed.stdout
    assert "execution_proof numerator=1 denominator=7" in completed.stdout


def test_attestation_mismatch_flips_present_to_invalid(tmp_path):
    # The source binding: a PRESENT artifact whose attested inputs no longer match
    # the tree (a source file changed after the artifact was recorded — the
    # neuter-and-keep-stale-green attack) becomes INVALID for exactly that reason.
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / "S0-01" / "result.json", _attested(root, "S0-01", _result()))
    assert "S0-01 PRESENT" in _run(root).stdout
    (root / "proofs" / "S0-01" / "spec.json").write_text('{"proof_id": "S0-01", "tampered": true}\n')
    out = _run(root).stdout
    assert "S0-01 PRESENT" not in out
    assert "attestation-mismatch: S0-01 proofs/S0-01/spec.json" in out


def test_forged_command_fails_runs_spec_binding(tmp_path):
    # The recorded runs must BE the attested spec's legs. Forging the positive
    # command (to /usr/bin/true) and recomputing the self-digest no longer
    # passes: the runs no longer match the spec.
    root = _copy_contract(tmp_path)
    result = _attested(root, "S0-01", _result())
    spec = {"proof_id": "S0-01", "legs": [
        {"leg": "positive", "cmd": result["runs"][0]["cmd"], "cwd": ".", "timeout_s": 60,
         "expect": {"exit_code": 0}},
        {"leg": "negative", "cmd": result["runs"][1]["cmd"], "cwd": ".", "timeout_s": 60,
         "expect": {"exit_code": 1, "failure_reason": "boom"}}]}
    (root / "proofs" / "S0-01" / "spec.json").write_text(json.dumps(spec) + "\n")
    result["runs"][1]["failure_reason"] = "boom"
    result["digest"] = hashlib.sha256(
        json.dumps(result["runs"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result["attestation"] = _load_validator().proof_attestation(root, "S0-01")
    _write_json(root / "proofs" / "S0-01" / "result.json", result)
    assert "S0-01 PRESENT" in _run(root).stdout  # honest baseline

    forged = json.loads((root / "proofs" / "S0-01" / "result.json").read_text())
    forged["runs"][0]["cmd"] = ["/usr/bin/true"]
    forged["digest"] = hashlib.sha256(
        json.dumps(forged["runs"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    _write_json(root / "proofs" / "S0-01" / "result.json", forged)
    out = _run(root).stdout
    assert "S0-01 PRESENT" not in out
    assert "runs-spec-mismatch: S0-01 leg 0" in out


def test_negative_reason_bound_to_spec(tmp_path):
    # A recorded negative leg whose reason does not carry the spec's
    # failure_reason fails, even with a matching command and exit code.
    root = _copy_contract(tmp_path)
    result = _attested(root, "S0-01", _result())
    spec = {"proof_id": "S0-01", "legs": [
        {"leg": "positive", "cmd": result["runs"][0]["cmd"], "cwd": ".", "timeout_s": 60,
         "expect": {"exit_code": 0}},
        {"leg": "negative", "cmd": result["runs"][1]["cmd"], "cwd": ".", "timeout_s": 60,
         "expect": {"exit_code": 1, "failure_reason": "the-required-reason"}}]}
    (root / "proofs" / "S0-01" / "spec.json").write_text(json.dumps(spec) + "\n")
    result["runs"][1]["failure_reason"] = "a-different-reason"  # does not carry the spec reason
    result["digest"] = hashlib.sha256(
        json.dumps(result["runs"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result["attestation"] = _load_validator().proof_attestation(root, "S0-01")
    _write_json(root / "proofs" / "S0-01" / "result.json", result)
    out = _run(root).stdout
    assert "S0-01 PRESENT" not in out
    assert "runs-spec-reason-mismatch: S0-01 leg 1" in out


def test_registry_mutation_breaks_attestation(tmp_path):
    # The attestation extends to the shared trust closure: mutating the registry
    # (not the proof directory) still breaks the binding.
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / "S0-01" / "result.json", _attested(root, "S0-01", _result()))
    assert "S0-01 PRESENT" in _run(root).stdout
    registry = root / "proofs" / "registry.yaml"
    registry.write_text(registry.read_text() + "\n# tampered\n")
    out = _run(root).stdout
    assert "S0-01 PRESENT" not in out
    assert "attestation-mismatch: S0-01 proofs/registry.yaml" in out


def test_registry_matches_seed_classes_and_counts():
    registry = _load_registry(ROOT / "proofs" / "registry.yaml")
    by_class = {classification: set() for classification in CLASSES}
    for entry in registry["proofs"]:
        by_class[entry["classification"]].add(entry["proof_id"])
    assert by_class == {
        "execution_proof": {"S0-01", "S0-02", "S0-04", "S0-05", "S0-06", "S0-07", "S0-11"},
        "conformance_checked_decision": {"S0-09", "S0-10", "S0-12"},
        "blocked_credential": {"S0-03"},
        "blocked_host": {"S0-08"},
    }
    assert next(entry for entry in registry["proofs"] if entry["proof_id"] == "S0-02")["required_negative_controls"] == 4


def test_committed_pc_bridge_spike_validates_and_declares_all_effects():
    completed = _run(ROOT)

    assert completed.returncode == 0, completed.stdout + completed.stderr


# Coordinator spine read of the lane's validator (2026-09-03): three gaps, each as a red test
# with its exact reason. The repair brief is "make these green; do not edit them".
def _spike(spike_id, effects):
    return {
        "spike_id": spike_id,
        "schema": "proofs/schemas/spike.schema.json",
        "outcome": "negative",
        "ran_at": "2026-09-03T00:00:00Z",
        "env_fingerprint": "sandbox:test",
        "runs": [{"command": "true", "exit_code": 1, "stdout_digest": hashlib.sha256(b"").hexdigest()}],
        "facts": {},
        "classification_effect": effects,
        "not_verified": [],
    }


def _write_registry(root, registry):
    (root / "proofs" / "registry.yaml").write_text(json.dumps(registry, indent=1) + "\n")


def test_allowed_transitions_come_only_from_the_registry(tmp_path):
    """AF-AP-13: a rule id this registry copy does not declare is undeclared, map-rust-s006 included."""
    root = _copy_contract(tmp_path)
    registry = _load_registry(root / "proofs" / "registry.yaml")
    rust = next(rule for rule in registry["spike_to_class_mapping"] if rule["spike"] == "rust-ai-memory")
    assert rust["positive_effect"].pop("rule_id") == "map-rust-s006"  # the committed registry declares it
    _write_registry(root, registry)
    effect = {"affected_proof": "S0-06", "from_class": "execution_proof", "to_class": "execution_proof", "rule_id": "map-rust-s006"}
    _write_json(root / "spikes" / "rust-ai-memory" / "result.json", _spike("rust-ai-memory", [effect]))

    completed = _run(root)

    assert completed.returncode == 1, completed.stdout + completed.stderr
    assert "undeclared-transition: rust-ai-memory execution_proof->execution_proof" in completed.stdout


def _typo_alias_value(registry):
    registry["class_aliases"]["blocked_capability"] = "blocked_hots"


def _canonical_alias_key(registry):
    registry["class_aliases"]["blocked_host"] = "execution_proof"


def _typo_branch_class(registry):
    rust = next(rule for rule in registry["spike_to_class_mapping"] if rule["spike"] == "rust-ai-memory")
    rust["negative_effect"]["to_class"] = "blocked_capabilty"


@pytest.mark.parametrize(
    ("mutate", "to_class", "expected"),
    [
        (_typo_alias_value, "blocked_capability", "registry-schema: class_aliases blocked_capability->blocked_hots is not canonical"),
        (_canonical_alias_key, "blocked_capability", "registry-schema: class_aliases key blocked_host is canonical"),
        (_typo_branch_class, "blocked_capabilty", "registry-schema: map-rust-s006 negative_effect to_class blocked_capabilty is not canonical"),
    ],
    ids=["alias-value-typo", "alias-key-canonical", "branch-class-typo"],
)
def test_registry_alias_and_branch_classes_must_be_canonical(tmp_path, mutate, to_class, expected):
    """AF-AP-14: both sides of the transition check resolve through the same table, so a typo
    in the table (or in a branch) makes them agree on a class that does not exist."""
    root = _copy_contract(tmp_path)
    registry = _load_registry(root / "proofs" / "registry.yaml")
    mutate(registry)
    _write_registry(root, registry)
    effect = {"affected_proof": "S0-06", "from_class": "execution_proof", "to_class": to_class, "rule_id": "map-rust-s006"}
    _write_json(root / "spikes" / "rust-ai-memory" / "result.json", _spike("rust-ai-memory", [effect]))

    completed = _run(root)

    assert completed.returncode == 1, completed.stdout + completed.stderr
    assert expected in completed.stdout


def test_result_run_timestamps_must_be_rfc3339(tmp_path):
    """Positive control for the date-time checker: it must actually fire."""
    root = _copy_contract(tmp_path)
    artifact = _result()
    artifact["runs"][0]["started_at"] = "yesterday"
    artifact["digest"] = hashlib.sha256(
        json.dumps(artifact["runs"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    _write_json(root / "proofs" / "S0-01" / "result.json", artifact)

    completed = _run(root)

    assert completed.returncode == 1, completed.stdout + completed.stderr
    assert "registry-schema: S0-01 result: runs.0.started_at: 'yesterday' is not a 'date-time'" in completed.stdout


def test_cli_fails_loud_when_the_date_time_checker_is_unavailable(tmp_path):
    """AF-AP-12: jsonschema registers the date-time checker only when rfc3339-validator imports;
    without it every `format` keyword is silently unchecked. The CLI must refuse to run, exit 3."""
    root = _copy_contract(tmp_path)
    _write_json(root / "proofs" / "S0-01" / "result.json", _result())
    blocker = tmp_path / "import-blocker"
    blocker.mkdir()
    (blocker / "sitecustomize.py").write_text(
        "import builtins\n"
        "real_import = builtins.__import__\n"
        "def guarded(name, *args, **kwargs):\n"
        "    if name == 'rfc3339_validator':\n"
        "        raise ModuleNotFoundError('rfc3339_validator blocked by contract test')\n"
        "    return real_import(name, *args, **kwargs)\n"
        "builtins.__import__ = guarded\n"
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(blocker)

    completed = subprocess.run(
        [sys.executable, str(CLI), "integrity", "--root", str(root)],
        capture_output=True,
        text=True,
        timeout=5,
        env=environment,
    )

    assert completed.returncode == 3, completed.stdout + completed.stderr
    assert "date-time format checker unavailable" in completed.stderr
    assert "S0-01 PRESENT" not in completed.stdout
