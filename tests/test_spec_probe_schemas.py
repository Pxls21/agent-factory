"""Coordinator contract tests for the two increment-#2 input schemas (spec, probe).

Negatives first: every object is closed, a spec may not carry `classification`, a negative leg
must declare its failure reason, both legs must be present. Authored by the coordinator on
2026-09-03 after a build lane halted because the brief's prose promised closures the JSON lacked.
"""
import json
import pathlib

import jsonschema
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "proofs" / "schemas" / "spec.schema.json").read_text())
PROBE = json.loads((ROOT / "proofs" / "schemas" / "probe.schema.json").read_text())


def _leg(kind, **extra):
    leg = {"leg": kind, "cmd": ["python3", "-c", "print('x')"], "cwd": "proofs/S0-01", "timeout_s": 5,
           "expect": {"exit_code": 0 if kind == "positive" else 1}}
    if kind == "negative":
        leg["expect"]["failure_reason"] = "expected-test-failure"
    leg.update(extra)
    return leg


def _spec():
    return {"proof_id": "S0-01", "legs": [_leg("positive"), _leg("negative")]}


def _probe():
    return {"proof_id": "S0-08", "probe_cmd": ["proofs/S0-08/probe.sh"], "timeout_s": 30,
            "reason_map": {"10": "capability_absent", "11": "capability_present_but_failing"}}


def _errors(schema, instance):
    return sorted(e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(instance))


def test_both_schemas_are_valid_draft_2020_12():
    jsonschema.Draft202012Validator.check_schema(SPEC)
    jsonschema.Draft202012Validator.check_schema(PROBE)


@pytest.mark.parametrize("mutate, fragment", [
    (lambda s: s.__setitem__("classification", "execution_proof"), "'classification' was unexpected"),
    (lambda s: s["legs"][0].__setitem__("shell", True), "'shell' was unexpected"),
    (lambda s: s["legs"][0]["expect"].__setitem__("stdout", "x"), "'stdout' was unexpected"),
    (lambda s: s["legs"][1]["expect"].pop("failure_reason"), "'failure_reason' is a required property"),
    (lambda s: s.__setitem__("legs", [_leg("positive"), _leg("positive")]), "does not contain items matching the given schema"),
    (lambda s: s["legs"][0].__setitem__("cwd", "/abs/path"), "does not match"),
    (lambda s: s["legs"][0].__setitem__("cwd", "../escape"), "does not match"),
    (lambda s: s["legs"][0].__setitem__("timeout_s", 0), "less than the minimum"),
    (lambda s: s["legs"][0].__setitem__("env", {"K": 1}), "1 is not of type 'string'"),
], ids=["classification", "leg-extra-key", "expect-extra-key", "negative-without-reason",
        "no-negative-leg", "absolute-cwd", "dotdot-cwd", "zero-timeout", "non-string-env"])
def test_spec_schema_rejects_each_hostile_shape(mutate, fragment):
    spec = _spec()
    mutate(spec)
    errors = _errors(SPEC, spec)
    assert errors, "hostile spec validated"
    assert any(fragment in e for e in errors), errors


def test_spec_schema_accepts_the_canonical_spec():
    assert _errors(SPEC, _spec()) == []


@pytest.mark.parametrize("mutate, fragment", [
    (lambda p: p.__setitem__("classification", "blocked_host"), "'classification' was unexpected"),
    (lambda p: p.__setitem__("reason_map", {"0": "capability_absent"}), "does not match"),
    (lambda p: p.__setitem__("reason_map", {"10": "made_up_reason"}), "is not one of"),
    (lambda p: p.__setitem__("reason_map", {}), "should be non-empty"),
    (lambda p: p.__setitem__("key_env", "lowercase"), "does not match"),
    (lambda p: p.pop("timeout_s"), "'timeout_s' is a required property"),
], ids=["classification", "exit-0-in-reason-map", "unknown-reason", "empty-reason-map",
        "lowercase-key-env", "missing-timeout"])
def test_probe_schema_rejects_each_hostile_shape(mutate, fragment):
    probe = _probe()
    mutate(probe)
    errors = _errors(PROBE, probe)
    assert errors, "hostile probe validated"
    assert any(fragment in e for e in errors), errors


def test_probe_schema_accepts_the_canonical_probe_with_key_env():
    probe = _probe()
    probe["key_env"] = "OMNIROUTE_API_KEY"
    assert _errors(PROBE, probe) == []
