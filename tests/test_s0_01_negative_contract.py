"""Gate for proofs/S0-01/negative_contract.py — the ONE negative-control validator both consumers share.

Every mutation below is one of the audit's (2026-09-05, 08a4a7d, P1 "negative execution") or a
sibling of it, and each asserts the EXACT reason string. The valid capture is synthesized from the
shape the pinned hermes-acp produced live on the PC (JSON-RPC error -32602 "Invalid params" with
pydantic's `missing protocolVersion` detail). Nothing here writes outside tmp_path.
"""
import base64
import hashlib
import json
import sys
from pathlib import Path

import pytest

P = Path(__file__).resolve().parents[1] / "proofs" / "S0-01"
sys.path.insert(0, str(P))
import pins  # noqa: E402
import negative_contract as nc  # noqa: E402

FIXTURE = json.loads((P / "fixtures" / "neg-malformed-initialize.json").read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _entry(seq, direction, t_utc, mono, frame):
    return {"seq": seq, "dir": direction, "t_utc": t_utc, "t_mono_ns": mono, "frame": frame}


def _error_response():
    return {"jsonrpc": "2.0", "id": 0, "error": {"code": -32602, "message": "Invalid params",
            "data": {"errors": [{"type": "missing", "loc": ["protocolVersion"], "msg": "Field required"}]}}}


def build_valid(neg: Path):
    neg.mkdir(parents=True, exist_ok=True)
    req = {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": json.loads(json.dumps(FIXTURE))}
    entries = [_entry(1, "c2a", "2026-09-05T17:57:20.411449Z", 4649101715037563, req),
               _entry(2, "a2c", "2026-09-05T17:57:21.031783Z", 4649102335384757, _error_response())]
    _write_timeline(neg, entries)
    rid = {
        "probe_path": "/home/rocco/agent-factory/proofs/S0-01/tools/acp_probe.py",
        "probe_sha256": _sha(P / "tools" / "acp_probe.py"),
        "agent_argv": [pins.PINNED_AGENT_REALPATH],
        "agent_realpath": pins.PINNED_AGENT_REALPATH,
        "agent_entrypoint_sha256": pins.PINNED_AGENT_ENTRYPOINT_SHA256,
        "agent_child_pid": 1975441,
        "agent_interpreter_realpath": pins.PINNED_AGENT_INTERPRETER_REALPATH,
        "agent_interpreter_sha256": pins.PINNED_AGENT_INTERPRETER_SHA256,
        "python_dont_write_bytecode": True,
        "spawned_at_utc": "2026-09-05T17:57:20.395720Z",
        "agent_exit_code": 0,
    }
    (neg / "runtime-identity.json").write_text(json.dumps(rid, indent=1) + "\n")
    env = {"PATH": pins.PINNED_PATH, "HOME": pins.PINNED_HOME, "HERMES_HOME": pins.PINNED_HERMES_HOME,
           "PYTHONDONTWRITEBYTECODE": "1", "S0_01_AGENT": pins.PINNED_AGENT_REALPATH,
           "S0_01_FRAMEDIR": "/home/rocco/s0-01-pinned/.markers/v2-negative",
           "OMNIROUTE_API_KEY": {"redacted": True, "len": 35, "sha256_12": "fe5d1f1b287b"}}
    (neg / "env.json").write_text(json.dumps(env, indent=1, sort_keys=True) + "\n")
    (neg / "agent-stderr.txt").write_text("2026-09-05 18:57:21 [INFO] acp_adapter.server: ACP client connected\n")
    return entries


def _write_timeline(neg: Path, entries):
    (neg / "timeline.jsonl").write_text("".join(json.dumps(e, separators=(",", ":")) + "\n" for e in entries))


def _rid(neg: Path):
    return json.loads((neg / "runtime-identity.json").read_text())


def _set_rid(neg: Path, **kw):
    rid = _rid(neg)
    rid.update(kw)
    (neg / "runtime-identity.json").write_text(json.dumps(rid, indent=1) + "\n")


def _expect(neg: Path, reason: str):
    with pytest.raises(nc.NegativeFailure) as ei:
        nc.validate_negative_dir(neg, P / "fixtures")
    assert str(ei.value) == reason


@pytest.fixture
def neg(tmp_path):
    d = tmp_path / "negative"
    build_valid(d)
    return d


def test_valid_capture_returns_observed_line(neg):
    assert nc.validate_negative_dir(neg, P / "fixtures") == "observed: error code=-32602 message=Invalid params"


def test_absent_dir_defers(tmp_path):
    with pytest.raises(nc.NegativeDeferred) as ei:
        nc.validate_negative_dir(tmp_path / "nope", P / "fixtures")
    assert str(ei.value) == "negative probe not captured"


# --- the audit's P1 mutations -------------------------------------------------------------------
def test_audit_agent_request_masquerading_as_response(neg):
    entries = build_valid(neg)
    entries[1]["frame"] = {"jsonrpc": "2.0", "id": 0, "method": "session/request_permission", "params": {}}
    _write_timeline(neg, entries)
    _expect(neg, "agent sent a request (method 'session/request_permission') instead of a response at seq 2")


def test_audit_undelivered_request_with_failed_probe(neg):
    entries = build_valid(neg)
    entries[0]["delivered"] = False
    _write_timeline(neg, entries)
    _expect(neg, "initialize request was not delivered to the agent")


def test_audit_probe_error_is_fatal(neg):
    _set_rid(neg, probe_error="BrokenPipeError: request not delivered")
    _expect(neg, "probe reported an error: BrokenPipeError: request not delivered")


def test_audit_agent_exit_code_minus_9(neg):
    _set_rid(neg, agent_exit_code=-9)
    _expect(neg, "agent_exit_code is -9, expected 0")


def test_audit_agent_argv_true_binary(neg):
    _set_rid(neg, agent_argv=["/usr/bin/true"])
    _expect(neg, "agent_argv mismatch")


def test_audit_agent_child_pid_minus_1(neg):
    _set_rid(neg, agent_child_pid=-1)
    _expect(neg, "agent_child_pid is not a positive int")


# --- response envelope discipline -------------------------------------------------------------
def test_no_response_only_notification(neg):
    entries = build_valid(neg)
    entries[1]["frame"] = {"jsonrpc": "2.0", "method": "session/update", "params": {}}
    _write_timeline(neg, entries)
    _expect(neg, "no agent response captured")


def test_duplicate_responses_same_id(neg):
    entries = build_valid(neg)
    entries.append(_entry(3, "a2c", "2026-09-05T17:57:21.100000Z", 4649102400000000, {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1}}))
    _write_timeline(neg, entries)
    _expect(neg, "2 agent responses carry the request id (expected exactly one)")


def test_result_and_error_in_one_envelope(neg):
    entries = build_valid(neg)
    entries[1]["frame"] = {"jsonrpc": "2.0", "id": 0, "result": {}, "error": {"code": -32602, "message": "Invalid params"}}
    _write_timeline(neg, entries)
    _expect(neg, "agent response is not a valid JSON-RPC envelope (exactly one of result/error)")


def test_agent_accepted_malformed_initialize(neg):
    entries = build_valid(neg)
    entries[1]["frame"] = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    _write_timeline(neg, entries)
    _expect(neg, "pinned agent accepted a malformed initialize (result protocolVersion=1)")


def test_wrong_error_code(neg):
    entries = build_valid(neg)
    entries[1]["frame"]["error"]["code"] = -32600
    _write_timeline(neg, entries)
    _expect(neg, "agent error is code=-32600 message='Invalid params', expected code=-32602 message='Invalid params'")


def test_wrong_error_message(neg):
    entries = build_valid(neg)
    entries[1]["frame"]["error"]["message"] = "Invalid Request"
    _write_timeline(neg, entries)
    _expect(neg, "agent error is code=-32602 message='Invalid Request', expected code=-32602 message='Invalid params'")


def test_response_with_other_id(neg):
    entries = build_valid(neg)
    entries[1]["frame"]["id"] = 7
    _write_timeline(neg, entries)
    _expect(neg, "agent response id 7 does not match the request id at seq 2")


def test_error_code_float_rejected(neg):
    entries = build_valid(neg)
    entries[1]["frame"]["error"]["code"] = -32602.0
    _write_timeline(neg, entries)
    _expect(neg, "agent error envelope has no integer code")


# --- request side --------------------------------------------------------------------------
def test_params_differ_from_fixture(neg):
    entries = build_valid(neg)
    entries[0]["frame"]["params"]["protocolVersion"] = 1
    _write_timeline(neg, entries)
    _expect(neg, "initialize params != fixture")


def test_first_frame_not_c2a(neg):
    entries = build_valid(neg)
    # swap frames and directions only — timestamps stay monotone so the ordering check is not what fires
    entries[0]["dir"], entries[1]["dir"] = entries[1]["dir"], entries[0]["dir"]
    entries[0]["frame"], entries[1]["frame"] = entries[1]["frame"], entries[0]["frame"]
    _write_timeline(neg, entries)
    _expect(neg, "seq 1 is not a c2a frame")


def test_second_c2a_frame(neg):
    entries = build_valid(neg)
    entries.append(_entry(3, "c2a", "2026-09-05T17:57:21.200000Z", 4649102500000000, {"jsonrpc": "2.0", "id": 1, "method": "session/new", "params": {}}))
    _write_timeline(neg, entries)
    _expect(neg, "unexpected second c2a frame at seq 3")


def test_fixture_file_absent(neg, tmp_path):
    fx = tmp_path / "fixtures"
    fx.mkdir()
    with pytest.raises(nc.NegativeFailure) as ei:
        nc.validate_negative_dir(neg, fx)
    assert str(ei.value) == "fixtures/neg-malformed-initialize.json absent"


# --- timeline hygiene ------------------------------------------------------------------------
def test_nan_rejected(neg):
    raw = (neg / "timeline.jsonl").read_text().replace('"t_mono_ns":4649102335384757', '"t_mono_ns":NaN')
    (neg / "timeline.jsonl").write_text(raw)
    _expect(neg, "timeline.jsonl line 2 is not strict JSON: non-finite JSON constant NaN")


def test_seq_gap(neg):
    entries = build_valid(neg)
    entries[1]["seq"] = 3
    _write_timeline(neg, entries)
    _expect(neg, "timeline seq not 1..N at index 1")


def test_blank_line(neg):
    (neg / "timeline.jsonl").write_text((neg / "timeline.jsonl").read_text() + "\n")
    _expect(neg, "timeline.jsonl line 3 is blank")


def test_non_json_agent_frame(neg):
    entries = build_valid(neg)
    entries[1] = {"seq": 2, "dir": "a2c", "t_utc": entries[1]["t_utc"], "t_mono_ns": entries[1]["t_mono_ns"],
                  "frame": None, "raw": "hello", "raw_b64": base64.b64encode(b"hello\n").decode()}
    _write_timeline(neg, entries)
    _expect(neg, "non-JSON agent frame at seq 2")


# --- directory / identity / env ---------------------------------------------------------------
def test_extra_entry(neg):
    (neg / "evil.txt").write_text("x")
    _expect(neg, "unexpected entry evil.txt")


@pytest.mark.parametrize("name", sorted(pins.NEGATIVE_REQUIRED_FILES - {"timeline.jsonl"}))
def test_required_file_absent(neg, name):
    (neg / name).unlink()
    _expect(neg, f"{name} absent")


def test_probe_sha_mismatch(neg):
    _set_rid(neg, probe_sha256="0" * 64)
    _expect(neg, "probe_sha256 mismatch")


@pytest.mark.parametrize("key", ["agent_realpath", "agent_entrypoint_sha256", "agent_interpreter_realpath", "agent_interpreter_sha256"])
def test_identity_pin_mismatch(neg, key):
    _set_rid(neg, **{key: "/tmp/evil" if "path" in key else "f" * 64})
    _expect(neg, f"{key} mismatch")


def test_interpreter_null_is_a_mismatch(neg):
    _set_rid(neg, agent_interpreter_realpath=None)
    _expect(neg, "agent_interpreter_realpath mismatch")


def test_identity_key_absent(neg):
    rid = _rid(neg)
    rid.pop("spawned_at_utc")
    (neg / "runtime-identity.json").write_text(json.dumps(rid))
    _expect(neg, "runtime identity key spawned_at_utc absent")


def test_bytecode_flag_false(neg):
    _set_rid(neg, python_dont_write_bytecode=False)
    _expect(neg, "python_dont_write_bytecode is not True")


def test_spawned_after_first_frame(neg):
    _set_rid(neg, spawned_at_utc="2026-09-05T17:57:25.000000Z")
    _expect(neg, "spawned_at_utc is later than the first frame")


def test_exit_code_bool_rejected(neg):
    _set_rid(neg, agent_exit_code=False)
    _expect(neg, "agent_exit_code is False, expected 0")


@pytest.mark.parametrize("key", ["HERMES_HOME", "PYTHONDONTWRITEBYTECODE", "S0_01_AGENT"])
def test_env_pin_mismatch(neg, key):
    env = json.loads((neg / "env.json").read_text())
    env[key] = "/tmp/evil"
    (neg / "env.json").write_text(json.dumps(env))
    _expect(neg, f"env {key} mismatch")


def test_env_key_not_redacted(neg):
    env = json.loads((neg / "env.json").read_text())
    env["OMNIROUTE_API_KEY"] = "sk-plaintext"
    (neg / "env.json").write_text(json.dumps(env))
    _expect(neg, "env OMNIROUTE_API_KEY not redacted or empty")


# ---- R5-N5-F11 (2026-09-06): guards that had no killing test (mutants NC-08 / NC-12 / NC-22 / NC-27 survived) ----

def _timeline(neg: Path):
    return [json.loads(l) for l in (neg / "timeline.jsonl").read_text().splitlines() if l.strip()]


def test_empty_probe_error_is_still_an_error(neg):
    """R8-N5d-F9: `probe_error == ""` validated — an empty reason is a reported error, not an absence."""
    _set_rid(neg, probe_error="")
    _expect(neg, "probe reported an error: (empty reason)")


@pytest.mark.parametrize("value, shown", [(0, "0"), (False, "False"), ([], "[]"), ({}, "{}")])
def test_falsy_non_string_probe_error_is_shown_by_repr(neg, value, shown):
    """R9-N5e-F7: a falsy non-string probe_error must surface its value, never '(empty reason)'."""
    _set_rid(neg, probe_error=value)
    _expect(neg, f"probe reported an error: {shown}")



@pytest.mark.parametrize("bad", ["/x", None, 12345], ids=["wrong-path", "null", "int"])
def test_probe_path_value_is_pinned_to_the_probe_tail(neg, bad):
    """R7-N5c-F3: probe_path was required to exist but never read — /x, null and 12345 all validated."""
    _set_rid(neg, probe_path=bad)
    _expect(neg, "probe_path is not the probe's path")


def test_agent_child_pid_bool_is_not_an_int(neg):
    """NC-08: `_is_int` must exclude bool — `true` is an int subclass and would pass a naive isinstance check."""
    _set_rid(neg, agent_child_pid=True)
    _expect(neg, "agent_child_pid is not a positive int")


def test_t_mono_ns_must_not_decrease(neg):
    """NC-12: the monotonic clock decreasing between consecutive entries is a Failure naming the seq."""
    entries = _timeline(neg)
    entries[1]["t_mono_ns"] = entries[0]["t_mono_ns"] - 1
    _write_timeline(neg, entries)
    _expect(neg, "t_mono_ns decreases at seq 2")


def test_timeline_entry_with_an_unexpected_key_is_rejected(neg):
    """NC-22: the entry key set is closed — an extra key is a Failure naming the entry."""
    entries = _timeline(neg)
    entries[0]["note"] = "smuggled"
    _write_timeline(neg, entries)
    _expect(neg, "timeline entry 1 has unexpected keys")


def test_t_utc_without_microseconds_is_rejected(neg):
    """NC-27: t_utc must match YYYY-MM-DDTHH:MM:SS.ffffffZ exactly — a second-resolution stamp is a Failure."""
    entries = _timeline(neg)
    entries[1]["t_utc"] = "2026-09-05T17:57:21Z"
    _write_timeline(neg, entries)
    _expect(neg, "timestamp '2026-09-05T17:57:21Z' does not match YYYY-MM-DDTHH:MM:SS.ffffffZ")


# ---- R6-N5b-F15 / AF-AP-42 (2026-09-06): the builder is pinned to ONE live run of the real producer ----

_FAKE_AGENT = """#!%s
import json, sys
line = sys.stdin.readline()
req = json.loads(line)
resp = {"jsonrpc": "2.0", "id": req["id"], "error": {"code": %d, "message": %r,
        "data": {"errors": [{"type": "missing", "loc": ["protocolVersion"], "msg": "Field required"}]}}}
sys.stdout.write(json.dumps(resp) + "\\n")
sys.stdout.flush()
sys.stdin.read()  # R8-N5d-F4: stay alive until the probe closes stdin (the interpreter sample must find a live child)
"""


def _run_real_probe(tmp_path: Path) -> Path:
    """One live run of proofs/S0-01/tools/acp_probe.py — the producer every fixture in this file imitates."""
    import os
    import subprocess
    agent = tmp_path / "fake_agent.py"
    # R7-N5c-F6: the fixture's envelope is built FROM the pins, never a literal copy of them
    agent.write_text(_FAKE_AGENT % (sys.executable, pins.PINNED_NEGATIVE_ERROR_CODE, pins.PINNED_NEGATIVE_ERROR_MESSAGE))
    agent.chmod(0o755)
    neg = tmp_path / "live-negative"
    neg.mkdir()
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(tmp_path), "S0_01_FRAMEDIR": str(neg),
           "S0_01_AGENT": str(agent), "ACP_PROBE_TIMEOUT": "20", "PYTHONDONTWRITEBYTECODE": "1",
           "OMNIROUTE_API_KEY": "dummy-value-for-the-redaction-shape-0123456789"}
    r = subprocess.run([sys.executable, str(P / "tools" / "acp_probe.py")], env=env, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return neg


def test_build_valid_matches_the_live_producer_shape(tmp_path):
    live = _run_real_probe(tmp_path)
    built = tmp_path / "built-negative"
    build_valid(built)
    # the file set
    assert sorted(p.name for p in live.iterdir()) == sorted(p.name for p in built.iterdir())
    # runtime-identity.json: key SET (JSON object order is not semantics; the producer sorts keys, the builder need not)
    live_rid = json.loads((live / "runtime-identity.json").read_text())
    built_rid = json.loads((built / "runtime-identity.json").read_text())
    assert sorted(built_rid) == sorted(live_rid)
    # timeline entries: key sets per direction and the a2c envelope keys
    def entries(d):
        return [json.loads(l) for l in (d / "timeline.jsonl").read_text().splitlines() if l.strip()]
    le, be = entries(live), entries(built)
    assert [e["dir"] for e in le] == [e["dir"] for e in be] == ["c2a", "a2c"]
    for l, b in zip(le, be):
        assert sorted(b) == sorted(l)
        assert sorted(b["frame"]) == sorted(l["frame"])
    assert sorted(be[1]["frame"]["error"]) == sorted(le[1]["frame"]["error"])
    # env.json: the redacted-dict SHAPE the producer writes, and the required keys the validator reads
    live_env = json.loads((live / "env.json").read_text())
    built_env = json.loads((built / "env.json").read_text())
    live_red = live_env["OMNIROUTE_API_KEY"]
    built_red = built_env["OMNIROUTE_API_KEY"]
    assert sorted(built_red) == sorted(live_red) == ["len", "redacted", "sha256_12"]
    assert built_red["redacted"] is True and live_red["redacted"] is True
    assert isinstance(live_red["len"], int) and len(live_red["sha256_12"]) == 12
    for key in ("PATH", "HOME", "S0_01_FRAMEDIR", "S0_01_AGENT", "PYTHONDONTWRITEBYTECODE", "OMNIROUTE_API_KEY"):
        assert key in live_env and key in built_env
    # the live run itself satisfies everything the validator asks except the venue pins — prove the reason is a PIN, not shape
    with pytest.raises(nc.NegativeFailure) as ei:
        nc.validate_negative_dir(live, P / "fixtures")
    # R7-N5c-F5: the live run fails on exactly ONE venue pin, deterministically — assert it, never a set of candidates.
    assert str(ei.value) == "agent_argv mismatch"
