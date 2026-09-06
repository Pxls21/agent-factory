"""tests/test_s0_01_check_initialize.py — check_initialize.py directory mode + file mode.

Tests exact exit codes and output for all directory-mode paths (request + response),
file mode (unchanged from v1), pin validation failures via A22 shared validator,
malformed evidence wrapper (6-verify F13), usage error exit 64 (8-verify F10 / A10),
required-files check (A11), NaN rejection (A11), seq==1 check (A11), fixture-absent guard (A11),
interpreter pin tests (4-F6), response-mode id matching (4-F5/6-F10), and --fixtures-dir.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "proofs" / "S0-01"
CHECK_INIT = P / "check_initialize.py"
FIXTURE = P / "fixtures" / "neg-malformed-initialize.json"

sys.path.insert(0, str(P))
import pins  # noqa: E402


def _run(kind, target, fixtures_dir=None):
    cmd = [sys.executable, str(CHECK_INIT), kind, str(target)]
    if fixtures_dir is not None:
        cmd += ["--fixtures-dir", str(fixtures_dir)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return r


def _probe_sha():
    """SHA256 of the actual acp_probe.py file."""
    return hashlib.sha256((P / "tools" / "acp_probe.py").read_bytes()).hexdigest()


# The PINNED error response the validator requires (A22)
_PINNED_ERROR_RESPONSE = {
    "jsonrpc": "2.0", "id": 0,
    "error": {"code": pins.PINNED_NEGATIVE_ERROR_CODE,
              "message": pins.PINNED_NEGATIVE_ERROR_MESSAGE,
              "data": {"errors": [{"type": "missing", "loc": ["protocolVersion"],
                                   "msg": "Field required"}]}},
}


def _make_capture_dir(tmp_path, *, params=None, a2c_frame="DEFAULT", rid_overrides=None,
                      has_timeline=True, has_rid=True, has_env=True,
                      has_stderr=True, extra_files=None, extra_a2c_before=None):
    """Build a negative probe capture directory valid for the A22 shared validator.

    a2c_frame="DEFAULT" uses the pinned error response; pass None for no a2c, or a
    specific frame dict to override. rid_overrides merges into the valid default RID.
    extra_a2c_before: list of (frame, t_utc, t_mono) to prepend before the main a2c.
    """
    d = tmp_path / "capture"
    d.mkdir(exist_ok=True)

    if has_timeline:
        fixture = json.loads(FIXTURE.read_text())
        p = params if params is not None else fixture
        c2a_frame = {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": p}
        entries = [
            {"seq": 1, "dir": "c2a", "t_utc": "2026-09-05T17:57:20.411449Z",
             "t_mono_ns": 4649101715037563, "frame": c2a_frame},
        ]
        seq = 2
        if extra_a2c_before:
            for frame, t_utc, t_mono in extra_a2c_before:
                entries.append({"seq": seq, "dir": "a2c", "t_utc": t_utc,
                                "t_mono_ns": t_mono, "frame": frame})
                seq += 1
        actual_a2c = _PINNED_ERROR_RESPONSE if a2c_frame == "DEFAULT" else a2c_frame
        if actual_a2c is not None:
            entries.append({
                "seq": seq, "dir": "a2c", "t_utc": "2026-09-05T17:57:21.031783Z",
                "t_mono_ns": 4649102335384757, "frame": actual_a2c,
            })
        (d / "timeline.jsonl").write_text(
            "\n".join(json.dumps(e, separators=(",", ":")) for e in entries) + "\n"
        )

    if has_rid:
        default_rid = {
            "probe_path": "/home/rocco/agent-factory/proofs/S0-01/tools/acp_probe.py",
            "probe_sha256": _probe_sha(),
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
        if rid_overrides:
            default_rid.update(rid_overrides)
        (d / "runtime-identity.json").write_text(json.dumps(default_rid, indent=2))

    if has_env:
        (d / "env.json").write_text(json.dumps({
            "PATH": pins.PINNED_PATH,
            "HOME": pins.PINNED_HOME,
            "HERMES_HOME": pins.PINNED_HERMES_HOME,
            "PYTHONDONTWRITEBYTECODE": "1",
            "S0_01_AGENT": pins.PINNED_AGENT_REALPATH,
            "S0_01_FRAMEDIR": "/home/rocco/s0-01-pinned/.markers/v2-negative",
            "OMNIROUTE_API_KEY": {"redacted": True, "len": 35, "sha256_12": "fe5d1f1b287b"},
        }, indent=1, sort_keys=True) + "\n")

    if has_stderr:
        (d / "agent-stderr.txt").write_text("")

    if extra_files:
        for name, content in extra_files.items():
            (d / name).write_text(content)

    return d


# ---- File mode (unchanged) ----

def test_file_mode_request_fixture_exits_1_with_seed_reason():
    """request <fixture> produces the exact seed reason."""
    r = _run("request", FIXTURE)
    assert r.returncode == 1
    assert r.stdout.strip() == "protocol-violation: missing required initialize field"


def test_file_mode_response_fixture():
    """response <fixture> classifies the fixture (no protocolVersion) as a protocol violation."""
    r = _run("response", FIXTURE)
    assert r.returncode == 1
    assert r.stdout.strip() == "protocol-violation: missing required initialize field"


# ---- Directory mode: deferral ----

def test_request_dir_defers_when_absent(tmp_path):
    """request on a nonexistent directory exits 2 with exact deferral text."""
    r = _run("request", tmp_path / "nonexistent")
    assert r.returncode == 2
    assert r.stdout.strip() == "deferred: negative probe not captured"


def test_request_dir_defers_when_no_timeline(tmp_path):
    """request on a directory without timeline.jsonl exits 2 with exact deferral text."""
    d = tmp_path / "empty_dir"
    d.mkdir()
    r = _run("request", d)
    assert r.returncode == 2
    assert r.stdout.strip() == "deferred: negative probe not captured"


def test_response_dir_defers_when_absent(tmp_path):
    """response on a nonexistent directory exits 2 with exact deferral text."""
    r = _run("response", tmp_path / "nonexistent")
    assert r.returncode == 2
    assert r.stdout.strip() == "deferred: negative probe not captured"


def test_response_dir_defers_when_no_timeline(tmp_path):
    """response on a directory without timeline.jsonl exits 2 with exact deferral text."""
    d = tmp_path / "empty_dir"
    d.mkdir()
    r = _run("response", d)
    assert r.returncode == 2
    assert r.stdout.strip() == "deferred: negative probe not captured"


# ---- Directory mode request: validation failures (each names negative:) ----

def test_request_dir_fails_no_c2a_frames(tmp_path):
    """Empty timeline (only a2c) fails via validator."""
    d = tmp_path / "capture"
    d.mkdir()
    entry = {"seq": 1, "dir": "a2c", "t_utc": "2026-09-05T00:00:00.000000Z",
             "t_mono_ns": 1000000, "frame": {"jsonrpc": "2.0", "id": 0, "result": {}}}
    (d / "timeline.jsonl").write_text(json.dumps(entry, separators=(",", ":")) + "\n")
    (d / "runtime-identity.json").write_text("{}")
    (d / "env.json").write_text(json.dumps({"HERMES_HOME": pins.PINNED_HERMES_HOME,
                                            "PYTHONDONTWRITEBYTECODE": "1"}) + "\n")
    (d / "agent-stderr.txt").write_text("")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: seq 1 is not a c2a frame"


def test_request_dir_fails_first_not_initialize(tmp_path):
    """First c2a frame not an initialize request."""
    d = tmp_path / "capture"
    d.mkdir()
    entry = {"seq": 1, "dir": "c2a", "t_utc": "2026-09-05T00:00:00.000000Z",
             "t_mono_ns": 1000000, "frame": {"jsonrpc": "2.0", "id": 0, "method": "session/new", "params": {}}}
    (d / "timeline.jsonl").write_text(json.dumps(entry, separators=(",", ":")) + "\n")
    (d / "runtime-identity.json").write_text("{}")
    (d / "env.json").write_text(json.dumps({"HERMES_HOME": pins.PINNED_HERMES_HOME,
                                            "PYTHONDONTWRITEBYTECODE": "1"}) + "\n")
    (d / "agent-stderr.txt").write_text("")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: seq 1 is not an initialize request"


def test_request_dir_fails_params_mismatch(tmp_path):
    """Params not matching the fixture is a failure."""
    wrong_params = {"protocolVersion": 2, "clientInfo": {"name": "test"}}
    d = _make_capture_dir(tmp_path, params=wrong_params)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: initialize params != fixture"


def test_request_dir_fails_no_rid(tmp_path):
    """Missing runtime-identity.json is a failure."""
    d = _make_capture_dir(tmp_path, has_rid=False)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: runtime-identity.json absent"


def test_request_dir_fails_agent_realpath_mismatch(tmp_path):
    """agent_realpath mismatch fails naming the field (A22 validator)."""
    d = _make_capture_dir(tmp_path, rid_overrides={"agent_realpath": "/tmp/evil/fake-agent"})
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: agent_realpath mismatch"


def test_request_dir_fails_entrypoint_sha_mismatch(tmp_path):
    """agent_entrypoint_sha256 mismatch fails naming the field."""
    d = _make_capture_dir(tmp_path, rid_overrides={"agent_entrypoint_sha256": "0" * 64})
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: agent_entrypoint_sha256 mismatch"


def test_request_dir_fails_bytecode_not_true(tmp_path):
    """python_dont_write_bytecode not True fails."""
    d = _make_capture_dir(tmp_path, rid_overrides={"python_dont_write_bytecode": False})
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: python_dont_write_bytecode is not True"


def test_request_dir_fails_no_a2c_response(tmp_path):
    """No a2c response matching the request id is a failure."""
    d = _make_capture_dir(tmp_path, a2c_frame=None)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: no agent response captured"


def test_request_dir_fails_no_matching_id(tmp_path):
    """a2c response with wrong id does not match."""
    a2c = {"jsonrpc": "2.0", "id": 999, "error": {"code": -32602, "message": "Invalid params"}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: agent response id 999 does not match the request id at seq 2"


# ---- Directory mode request: success path ----

def test_request_dir_valid_capture_exits_1_with_classification_and_observed(tmp_path):
    """A22: valid capture with the pinned error response: line 1 = seed reason, line 2 = observed."""
    d = _make_capture_dir(tmp_path)
    r = _run("request", d)
    assert r.returncode == 1
    lines = r.stdout.strip().splitlines()
    assert len(lines) == 2
    assert lines[0] == "protocol-violation: missing required initialize field"
    assert lines[1] == "observed: error code=-32602 message=Invalid params"


def test_request_dir_result_response_rejected_by_validator(tmp_path):
    """A22/4-F3: agent accepting the malformed initialize is now a validator FAILURE."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {
        "protocolVersion": 1, "agentCapabilities": {},
    }}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: pinned agent accepted a malformed initialize (result protocolVersion=1)"


# ---- 4-F6: interpreter pin tests ----

def test_request_dir_fails_interpreter_realpath_mismatch(tmp_path):
    """4-F6: forged agent_interpreter_realpath fails with exact reason."""
    d = _make_capture_dir(tmp_path, rid_overrides={
        "agent_interpreter_realpath": "/usr/bin/attacker-python"})
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: agent_interpreter_realpath mismatch"


def test_request_dir_fails_interpreter_sha_mismatch(tmp_path):
    """4-F6: forged agent_interpreter_sha256 fails with exact reason."""
    d = _make_capture_dir(tmp_path, rid_overrides={
        "agent_interpreter_sha256": "0" * 64})
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: agent_interpreter_sha256 mismatch"


# ---- 4-F5/6-F10: response-mode id matching with many a2c frames ----

def test_response_dir_skips_notification_finds_matching_id(tmp_path):
    """4-F5/6-F10: response <dir> with a junk notification before the real response
    finds the response by id matching, not a2c[0]."""
    notification = {"jsonrpc": "2.0", "method": "log", "params": {"message": "starting"}}
    result_frame = {"jsonrpc": "2.0", "id": 0, "result": {
        "protocolVersion": 1, "agentCapabilities": {},
    }}
    d = _make_capture_dir(tmp_path,
                          extra_a2c_before=[(notification, "2026-09-05T17:57:20.800000Z", 4649102100000000)],
                          a2c_frame=result_frame)
    r = _run("response", d)
    assert r.returncode == 0
    assert r.stdout.strip() == "ok"


def test_response_dir_foreign_id_a2c_response_first(tmp_path):
    """4-F5/6-F10: response <dir> with a foreign-id a2c RESPONSE before the real one.
    The a2c[0] is a response with id=999 (not matching); the real one has id=0."""
    foreign = {"jsonrpc": "2.0", "id": 999, "error": {"code": -32600, "message": "Invalid"}}
    result_frame = {"jsonrpc": "2.0", "id": 0, "error": {"code": -32602, "message": "Invalid params"}}
    d = _make_capture_dir(tmp_path,
                          extra_a2c_before=[(foreign, "2026-09-05T17:57:20.800000Z", 4649102100000000)],
                          a2c_frame=result_frame)
    r = _run("response", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "error code=-32602 message=Invalid params"


# ---- Directory mode response ----

def test_response_dir_classifies_result(tmp_path):
    """response <dir> classifies the a2c response's result."""
    result_frame = {"jsonrpc": "2.0", "id": 0, "result": {
        "protocolVersion": 1, "agentCapabilities": {},
    }}
    d = _make_capture_dir(tmp_path, a2c_frame=result_frame)
    r = _run("response", d)
    assert r.returncode == 0
    assert r.stdout.strip() == "ok"


def test_response_dir_no_a2c_fails(tmp_path):
    """response <dir> with no a2c frames fails."""
    d = _make_capture_dir(tmp_path, a2c_frame=None)
    r = _run("response", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "no a2c response to classify"


def test_response_dir_error_response(tmp_path):
    """response <dir> with a JSON-RPC error prints the error."""
    a2c = {"jsonrpc": "2.0", "id": 0, "error": {"code": -32600, "message": "Invalid request"}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    r = _run("response", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "error code=-32600 message=Invalid request"


def test_response_dir_distinct_from_request(tmp_path):
    """response <dir> produces different output from request <dir> on the same capture.
    R5-N5-F17: assert exact output of each mode, not just inequality."""
    d = _make_capture_dir(tmp_path)
    r_req = _run("request", d)
    r_resp = _run("response", d)
    assert r_req.returncode == 1
    assert r_resp.returncode == 1
    req_lines = r_req.stdout.strip().splitlines()
    assert req_lines[0] == "protocol-violation: missing required initialize field"
    assert req_lines[1] == "observed: error code=-32602 message=Invalid params"
    assert r_resp.stdout.strip() == "error code=-32602 message=Invalid params"


# ---- 8-verify F10 / A10: usage error exits 64, not 2 ----

def test_usage_error_exits_64():
    """Bad CLI usage exits 64 (EX_USAGE), not 2."""
    r = subprocess.run(
        [sys.executable, str(CHECK_INIT), "bogus", str(FIXTURE)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 64
    assert r.stderr.strip() == "usage: check_initialize.py request|response <file|dir> [--fixtures-dir <dir>]"


def test_usage_error_no_args_exits_64():
    """No args at all exits 64."""
    r = subprocess.run(
        [sys.executable, str(CHECK_INIT)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 64
    assert r.stderr.strip() == "usage: check_initialize.py request|response <file|dir> [--fixtures-dir <dir>]"


# ---- 6-verify F13: malformed evidence ----

def test_malformed_timeline_non_json(tmp_path):
    """F13: non-JSON timeline line via validator."""
    d = tmp_path / "capture"
    d.mkdir()
    (d / "timeline.jsonl").write_text("not json\n")
    (d / "runtime-identity.json").write_text("{}")
    (d / "env.json").write_text(json.dumps({"HERMES_HOME": pins.PINNED_HERMES_HOME,
                                            "PYTHONDONTWRITEBYTECODE": "1"}) + "\n")
    (d / "agent-stderr.txt").write_text("")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: timeline.jsonl line 1 is not strict JSON: Expecting value: line 1 column 1 (char 0)"


def test_malformed_timeline_missing_dir_key(tmp_path):
    """F13: entry without 'dir' key via validator."""
    d = tmp_path / "capture"
    d.mkdir()
    entry = {"seq": 1, "frame": {"method": "initialize"}}
    (d / "timeline.jsonl").write_text(json.dumps(entry) + "\n")
    (d / "runtime-identity.json").write_text("{}")
    (d / "env.json").write_text(json.dumps({"HERMES_HOME": pins.PINNED_HERMES_HOME,
                                            "PYTHONDONTWRITEBYTECODE": "1"}) + "\n")
    (d / "agent-stderr.txt").write_text("")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: timeline seq 1 has an invalid dir"


# ---- A11: required files ----

def test_request_dir_fails_missing_env_json(tmp_path):
    """A11: env.json absent."""
    d = _make_capture_dir(tmp_path, has_env=False)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: env.json absent"


def test_request_dir_fails_missing_agent_stderr(tmp_path):
    """A11: agent-stderr.txt absent."""
    d = _make_capture_dir(tmp_path, has_stderr=False)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: agent-stderr.txt absent"


def test_request_dir_fails_extra_file(tmp_path):
    """A11: extra file in directory."""
    d = _make_capture_dir(tmp_path, extra_files={"bogus.txt": "evil"})
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: unexpected entry bogus.txt"


# ---- A11: NaN rejection ----

def test_request_dir_fails_nan_in_timeline(tmp_path):
    """A11: NaN in timeline via validator."""
    d = tmp_path / "capture"
    d.mkdir()
    (d / "timeline.jsonl").write_text(
        '{"seq":1,"dir":"c2a","t_utc":"2026-09-05T00:00:00.000000Z","t_mono_ns":NaN,"frame":null}\n'
    )
    (d / "runtime-identity.json").write_text("{}")
    (d / "env.json").write_text(json.dumps({"HERMES_HOME": pins.PINNED_HERMES_HOME,
                                            "PYTHONDONTWRITEBYTECODE": "1"}) + "\n")
    (d / "agent-stderr.txt").write_text("")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: timeline.jsonl line 1 is not strict JSON: non-finite JSON constant NaN"


# ---- A11: seq == 1 check ----

def test_request_dir_fails_seq_not_1(tmp_path):
    """A11: c2a initialize seq is not 1."""
    d = tmp_path / "capture"
    d.mkdir()
    fixture = json.loads(FIXTURE.read_text())
    c2a_frame = {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": fixture}
    entry = {"seq": 5, "dir": "c2a", "t_utc": "2026-09-05T00:00:00.000000Z",
             "t_mono_ns": 1000000, "frame": c2a_frame}
    (d / "timeline.jsonl").write_text(json.dumps(entry, separators=(",", ":")) + "\n")
    (d / "runtime-identity.json").write_text("{}")
    (d / "env.json").write_text(json.dumps({"HERMES_HOME": pins.PINNED_HERMES_HOME,
                                            "PYTHONDONTWRITEBYTECODE": "1"}) + "\n")
    (d / "agent-stderr.txt").write_text("")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: timeline seq not 1..N at index 0"


# ---- A11: fixture absent ----

def test_request_dir_fails_fixture_absent(tmp_path):
    """A11: neg-malformed-initialize.json absent → failure via validator."""
    d = _make_capture_dir(tmp_path)
    # Use a fixtures_dir that lacks the fixture file
    fx = tmp_path / "fixtures"
    fx.mkdir()
    r = _run("request", d, fixtures_dir=fx)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: fixtures/neg-malformed-initialize.json absent"


# ---- V12: input-error exit 64, not 2 (mutant C02 killer) ----

def test_input_error_non_initialize_frame_exits_64(tmp_path):
    """V12: file mode with a non-initialize frame exits 64."""
    f = tmp_path / "session_new.jsonl"
    f.write_text(json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "session/new", "params": {}
    }) + "\n")
    r = _run("request", f)
    assert r.returncode == 64
    assert r.stderr.strip() == "input error: frame method is 'session/new', not 'initialize'"


# ---- V13: extra subdirectory rejected ----

def test_request_dir_fails_extra_subdirectory(tmp_path):
    """V13: extra subdirectory under the capture dir is a Failure."""
    d = _make_capture_dir(tmp_path)
    (d / "sneaky_subdir").mkdir()
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: unexpected entry sneaky_subdir"


# ---- V14: env.json validated ----

def test_request_dir_fails_hermes_home_mismatch(tmp_path):
    """V14/A17: env.json with wrong HERMES_HOME via validator."""
    d = _make_capture_dir(tmp_path)
    (d / "env.json").write_text(json.dumps({
        "HERMES_HOME": "/wrong/path", "PYTHONDONTWRITEBYTECODE": "1",
    }))
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: env HERMES_HOME mismatch"


def test_request_dir_fails_pythondontwritebytecode_mismatch(tmp_path):
    """V14/A17: env.json with wrong PYTHONDONTWRITEBYTECODE via validator."""
    d = _make_capture_dir(tmp_path)
    (d / "env.json").write_text(json.dumps({
        "HERMES_HOME": pins.PINNED_HERMES_HOME, "PYTHONDONTWRITEBYTECODE": "0",
    }))
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: env PYTHONDONTWRITEBYTECODE mismatch"


def test_request_dir_fails_empty_env_json(tmp_path):
    """V14/A17: env.json with {} → env HERMES_HOME mismatch."""
    d = _make_capture_dir(tmp_path)
    (d / "env.json").write_text("{}")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: env HERMES_HOME mismatch"


# ---- R5-N5-F8: response <dir> cardinality gate ----

def test_response_dir_rejects_duplicate_id_responses(tmp_path):
    """R5-N5-F8: two a2c responses carrying the same request id is a Failure.
    Kills CI-10 (matching[-1] mutant)."""
    first_resp = {"jsonrpc": "2.0", "id": 0, "error": {"code": -32602, "message": "Invalid params"}}
    second_resp = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path,
                          extra_a2c_before=[(first_resp, "2026-09-05T17:57:20.800000Z", 4649102100000000)],
                          a2c_frame=second_resp)
    r = _run("response", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "Failure: 2 a2c responses carry request id 0"


# ---- R5-N5-F18: response <dir> with unparseable c2a frame ----

def test_response_dir_rejects_unparseable_c2a(tmp_path):
    """R5-N5-F18: c2a frame with no 'id' key does not silently match notifications."""
    d = tmp_path / "capture"
    d.mkdir()
    c2a = {"seq": 1, "dir": "c2a", "t_utc": "2026-09-05T17:57:20.411449Z",
           "t_mono_ns": 4649101715037563, "frame": {"jsonrpc": "2.0", "method": "initialize"}}
    a2c = {"seq": 2, "dir": "a2c", "t_utc": "2026-09-05T17:57:21.031783Z",
           "t_mono_ns": 4649102335384757,
           "frame": {"jsonrpc": "2.0", "method": "log", "params": {"msg": "hi"}}}
    (d / "timeline.jsonl").write_text(
        json.dumps(c2a, separators=(",", ":")) + "\n" +
        json.dumps(a2c, separators=(",", ":")) + "\n"
    )
    r = _run("response", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "c2a frame has no id"


def test_response_dir_rejects_null_c2a_frame(tmp_path):
    """R5-N5-F18: c2a with frame=null does not match notifications with missing id."""
    d = tmp_path / "capture"
    d.mkdir()
    c2a = {"seq": 1, "dir": "c2a", "t_utc": "2026-09-05T17:57:20.411449Z",
           "t_mono_ns": 4649101715037563, "frame": None}
    a2c_notif = {"seq": 2, "dir": "a2c", "t_utc": "2026-09-05T17:57:21.031783Z",
                 "t_mono_ns": 4649102335384757,
                 "frame": {"jsonrpc": "2.0", "method": "log", "params": {"msg": "hi"}}}
    (d / "timeline.jsonl").write_text(
        json.dumps(c2a, separators=(",", ":")) + "\n" +
        json.dumps(a2c_notif, separators=(",", ":")) + "\n"
    )
    r = _run("response", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "c2a frame has no id"


# ---- R5-N5-F5: schema resolution via --fixtures-dir ----

def test_request_file_mode_uses_fixtures_dir_schema(tmp_path):
    """R5-N5-F5: a mutated schema in --fixtures-dir changes file-mode classification.
    Kills CI-06c (file-mode schema load mutant). Directory-mode mutants CI-06/CI-06b
    are killed by the separate request-dir and response-dir schema tests below."""
    # Create a custom fixtures dir with a modified schema that DOES NOT
    # require protocolVersion, so the fixture classifies as "ok" instead.
    fx = tmp_path / "fixtures"
    fx.mkdir()
    import shutil
    schema_src = ROOT / "proofs" / "S0-01" / "fixtures" / "acp-schema-v1.json"
    schema = json.loads(schema_src.read_text())
    # Remove protocolVersion from required in InitializeRequest
    if "InitializeRequest" in schema.get("$defs", {}):
        ir = schema["$defs"]["InitializeRequest"]
        if "required" in ir and "protocolVersion" in ir["required"]:
            ir["required"].remove("protocolVersion")
    (fx / "acp-schema-v1.json").write_text(json.dumps(schema, indent=2))
    # Also copy the fixture file needed by the validator
    shutil.copy2(ROOT / "proofs" / "S0-01" / "fixtures" / "neg-malformed-initialize.json",
                 fx / "neg-malformed-initialize.json")

    r = _run("request", FIXTURE, fixtures_dir=fx)
    # With protocolVersion not required, the fixture should classify as "ok"
    assert r.returncode == 0, f"expected exit 0 with relaxed schema, got {r.returncode}: {r.stdout}"
    assert r.stdout.strip() == "ok"


# ---- R5-N5-F6: malformed evidence arm gated (CI-08 killer) ----

def test_malformed_evidence_exits_1_not_0(tmp_path):
    """R5-N5-F6: the malformed evidence handler returns 1. Kills CI-08
    (return 1 -> return 0 mutant)."""
    d = tmp_path / "capture"
    d.mkdir()
    (d / "timeline.jsonl").write_text("not json\n")
    # Intentionally corrupt runtime-identity.json too
    (d / "runtime-identity.json").write_text("{corrupt")
    (d / "env.json").write_text("{}")
    (d / "agent-stderr.txt").write_text("")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: timeline.jsonl line 1 is not strict JSON: Expecting value: line 1 column 1 (char 0)"


def test_malformed_rid_json_exits_1(tmp_path):
    """R5-N5-F6: invalid JSON in runtime-identity.json triggers malformed evidence arm."""
    d = _make_capture_dir(tmp_path)
    (d / "runtime-identity.json").write_text("{bad json")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: malformed evidence: JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)"


# ---- R5-N5-F10: capture dir builder pinned to a live producer run ----

def test_make_capture_dir_keys_match_live_producer(tmp_path):
    """R5-N5-F10: _make_capture_dir produces a RID with the same key set and
    key order as a live acp_probe run. Kills AP-02/AP-16 (extra/missing key)."""
    import textwrap
    PROBE = ROOT / "proofs" / "S0-01" / "tools" / "acp_probe.py"
    # Run the actual probe to get a live producer sample
    agent = tmp_path / "agent_live.py"
    agent.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import json, sys
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            resp = {
                "jsonrpc": "2.0", "id": msg["id"],
                "error": {"code": -32602, "message": "Invalid params",
                          "data": {"errors": [{"type": "missing",
                                               "loc": ["protocolVersion"],
                                               "msg": "Field required"}]}},
            }
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            break
    """))
    agent.chmod(0o755)
    import os
    framedir = tmp_path / "live_capture"
    framedir.mkdir()
    env = os.environ.copy()
    env["S0_01_AGENT"] = str(agent)
    env["S0_01_FRAMEDIR"] = str(framedir)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 0, f"probe failed: {r.stderr}"
    live_rid = json.loads((framedir / "runtime-identity.json").read_text())
    live_keys = list(live_rid.keys())
    # Compare with _make_capture_dir's default
    d = _make_capture_dir(tmp_path)
    builder_rid = json.loads((d / "runtime-identity.json").read_text())
    builder_keys = list(builder_rid.keys())
    assert set(builder_keys) == set(live_keys), (
        f"builder keys {set(builder_keys)} != live keys {set(live_keys)}"
    )
    assert builder_keys == live_keys, (
        f"builder key order {builder_keys} != live key order {live_keys}"
    )
    # Timeline key set also matches
    live_tl = [json.loads(l) for l in (framedir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    builder_tl = [json.loads(l) for l in (d / "timeline.jsonl").read_text().splitlines() if l.strip()]
    assert set(live_tl[0].keys()) == set(builder_tl[0].keys()), (
        f"timeline c2a keys differ: live={set(live_tl[0].keys())} builder={set(builder_tl[0].keys())}"
    )


# ---- R6-N5b-F1: directory-mode schema via --fixtures-dir ----

def _make_relaxed_fixtures_dir(tmp_path):
    """Create a fixtures dir with a RELAXED schema (protocolVersion not required)
    and a copy of the neg-malformed-initialize.json fixture."""
    import shutil
    fx = tmp_path / "relaxed_fixtures"
    fx.mkdir(exist_ok=True)
    schema_src = ROOT / "proofs" / "S0-01" / "fixtures" / "acp-schema-v1.json"
    schema = json.loads(schema_src.read_text())
    for defn_name in ("InitializeRequest", "InitializeResponse"):
        defn = schema.get("$defs", {}).get(defn_name, {})
        if "required" in defn and "protocolVersion" in defn["required"]:
            defn["required"].remove("protocolVersion")
    (fx / "acp-schema-v1.json").write_text(json.dumps(schema, indent=2))
    shutil.copy2(ROOT / "proofs" / "S0-01" / "fixtures" / "neg-malformed-initialize.json",
                 fx / "neg-malformed-initialize.json")
    return fx


def test_request_dir_uses_fixtures_dir_schema(tmp_path):
    """R6-N5b-F1: request <dir> with --fixtures-dir carrying a RELAXED schema
    changes the classification to 'ok'. Kills CI-06 (schema = load_schema() mutant)."""
    d = _make_capture_dir(tmp_path)
    fx = _make_relaxed_fixtures_dir(tmp_path)
    r = _run("request", d, fixtures_dir=fx)
    assert r.returncode == 1  # request dir always returns 1
    lines = r.stdout.strip().splitlines()
    # With the relaxed schema, protocolVersion is not required → classification is "ok"
    assert lines[0] == "ok", (
        f"expected 'ok' with relaxed schema, got {lines[0]!r} (CI-06 may survive)"
    )


def test_response_dir_uses_fixtures_dir_schema(tmp_path):
    """R6-N5b-F1: response <dir> with --fixtures-dir carrying a RELAXED schema
    classifies a result lacking protocolVersion as 'ok'. Kills CI-06b."""
    # Build a capture with a result that is MISSING protocolVersion
    a2c_frame = {"jsonrpc": "2.0", "id": 0, "result": {"agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c_frame)
    fx = _make_relaxed_fixtures_dir(tmp_path)
    r = _run("response", d, fixtures_dir=fx)
    # With relaxed schema: "ok" → exit 0
    assert r.returncode == 0, (
        f"expected exit 0 with relaxed schema, got {r.returncode}: {r.stdout}"
    )
    assert r.stdout.strip() == "ok"


# ---- R6-N5b-F9: response-dir with zero c2a entries ----

def test_response_dir_no_c2a_frames_exits_1(tmp_path):
    """R6-N5b-F9: response <dir> with a timeline of zero c2a entries outputs
    the exact line 'no c2a frames in timeline'. Kills CI-09."""
    d = tmp_path / "capture"
    d.mkdir()
    # Only a2c entries, no c2a
    a2c = {"seq": 1, "dir": "a2c", "t_utc": "2026-09-05T17:57:21.031783Z",
           "t_mono_ns": 4649102335384757,
           "frame": {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1}}}
    (d / "timeline.jsonl").write_text(json.dumps(a2c, separators=(",", ":")) + "\n")
    r = _run("response", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "no c2a frames in timeline"


# ---- R6-N5b-F11: response-dir with schema-invalid result ----

def test_response_dir_invalid_result_exits_1(tmp_path):
    """R6-N5b-F11: response <dir> with a result missing protocolVersion → exit 1
    with the exact classification line. Kills CI-16 (return 0 mutant)."""
    a2c_frame = {"jsonrpc": "2.0", "id": 0, "result": {"agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c_frame)
    r = _run("response", d)
    assert r.returncode == 1, (
        f"expected exit 1 for schema-invalid result, got {r.returncode}: {r.stdout}"
    )
    assert r.stdout.strip() == "protocol-violation: missing required initialize field"


# ---- R6-N5b-F13: response-dir NaN rejection ----

def test_response_dir_nan_in_a2c_frame(tmp_path):
    """R6-N5b-F13: NaN in a response-mode a2c frame triggers the NaN rejection.
    Kills CI-14 (parse_constant removed mutant)."""
    d = tmp_path / "capture"
    d.mkdir()
    c2a = {"seq": 1, "dir": "c2a", "t_utc": "2026-09-05T17:57:20.411449Z",
           "t_mono_ns": 4649101715037563,
           "frame": {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}}}
    (d / "timeline.jsonl").write_text(
        json.dumps(c2a, separators=(",", ":")) + "\n"
        + '{"seq":2,"dir":"a2c","t_utc":"2026-09-05T17:57:21.031783Z","t_mono_ns":NaN,'
          '"frame":{"jsonrpc":"2.0","id":0,"result":{"protocolVersion":1}}}\n'
    )
    r = _run("response", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: malformed evidence: ValueError: NaN/Infinity not allowed in timeline: 'NaN'"


# ---- R6-N5b-F14: --fixtures-dir with no value ----

def test_fixtures_dir_no_value_exits_64():
    """R6-N5b-F14: --fixtures-dir with no value after it → usage + exit 64.
    Kills CI-18 (return 0 mutant)."""
    r = subprocess.run(
        [sys.executable, str(CHECK_INIT), "request", str(FIXTURE), "--fixtures-dir"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 64
    assert r.stderr.strip() == "usage: check_initialize.py request|response <file|dir> [--fixtures-dir <dir>]"
