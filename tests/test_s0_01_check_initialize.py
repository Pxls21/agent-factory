"""tests/test_s0_01_check_initialize.py — check_initialize.py directory mode + file mode.

Tests exact exit codes and output for all directory-mode paths (request + response),
file mode (unchanged from v1), and pin validation failures.
"""
from __future__ import annotations

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


def _run(kind, target):
    r = subprocess.run(
        [sys.executable, str(CHECK_INIT), kind, str(target)],
        capture_output=True, text=True, timeout=30,
    )
    return r


def _make_capture_dir(tmp_path, *, params=None, a2c_frame=None, rid=None,
                      has_timeline=True, has_rid=True):
    """Build a minimal negative probe capture directory."""
    d = tmp_path / "capture"
    d.mkdir(exist_ok=True)

    if has_timeline:
        fixture = json.loads(FIXTURE.read_text())
        p = params if params is not None else fixture
        c2a_frame = {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": p}
        entries = [
            {"seq": 1, "dir": "c2a", "t_utc": "2026-09-05T00:00:00.000000Z",
             "t_mono_ns": 1000000, "frame": c2a_frame},
        ]
        if a2c_frame is not None:
            entries.append({
                "seq": 2, "dir": "a2c", "t_utc": "2026-09-05T00:00:01.000000Z",
                "t_mono_ns": 2000000, "frame": a2c_frame,
            })
        (d / "timeline.jsonl").write_text(
            "\n".join(json.dumps(e, separators=(",", ":")) for e in entries) + "\n"
        )

    if has_rid:
        default_rid = {
            "probe_path": "/tmp/probe.py",
            "probe_sha256": "0" * 64,
            "agent_argv": [pins.PINNED_AGENT_REALPATH],
            "agent_realpath": pins.PINNED_AGENT_REALPATH,
            "agent_entrypoint_sha256": pins.PINNED_AGENT_ENTRYPOINT_SHA256,
            "agent_child_pid": 12345,
            "agent_interpreter_realpath": pins.PINNED_AGENT_INTERPRETER_REALPATH,
            "agent_interpreter_sha256": pins.PINNED_AGENT_INTERPRETER_SHA256,
            "python_dont_write_bytecode": True,
            "spawned_at_utc": "2026-09-05T00:00:00.000000Z",
            "agent_exit_code": 0,
        }
        actual_rid = rid if rid is not None else default_rid
        (d / "runtime-identity.json").write_text(json.dumps(actual_rid, indent=2))

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
    assert r.stdout.strip().startswith("protocol-violation:")


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
    """Empty timeline (only a2c) fails with the right failure_reason."""
    d = tmp_path / "capture"
    d.mkdir()
    entry = {"seq": 1, "dir": "a2c", "t_utc": "2026-09-05T00:00:00.000000Z",
             "t_mono_ns": 1000000, "frame": {"jsonrpc": "2.0", "id": 0, "result": {}}}
    (d / "timeline.jsonl").write_text(json.dumps(entry, separators=(",", ":")) + "\n")
    (d / "runtime-identity.json").write_text("{}")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: no c2a frames in timeline"


def test_request_dir_fails_first_not_initialize(tmp_path):
    """First c2a frame not an initialize request."""
    d = tmp_path / "capture"
    d.mkdir()
    entry = {"seq": 1, "dir": "c2a", "t_utc": "2026-09-05T00:00:00.000000Z",
             "t_mono_ns": 1000000, "frame": {"jsonrpc": "2.0", "id": 0, "method": "session/new", "params": {}}}
    (d / "timeline.jsonl").write_text(json.dumps(entry, separators=(",", ":")) + "\n")
    (d / "runtime-identity.json").write_text("{}")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: first c2a frame is 'session/new', not initialize"


def test_request_dir_fails_params_mismatch(tmp_path):
    """Params not matching the fixture is a failure."""
    wrong_params = {"protocolVersion": 2, "clientInfo": {"name": "test"}}
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, params=wrong_params, a2c_frame=a2c)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: params != fixture"


def test_request_dir_fails_no_rid(tmp_path):
    """Missing runtime-identity.json is a failure."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c, has_rid=False)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: runtime-identity.json absent"


def test_request_dir_fails_agent_realpath_mismatch(tmp_path):
    """agent_realpath mismatch fails naming the field."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    rid = {
        "agent_realpath": "/tmp/evil/fake-agent",
        "agent_entrypoint_sha256": pins.PINNED_AGENT_ENTRYPOINT_SHA256,
        "agent_interpreter_realpath": pins.PINNED_AGENT_INTERPRETER_REALPATH,
        "agent_interpreter_sha256": pins.PINNED_AGENT_INTERPRETER_SHA256,
        "python_dont_write_bytecode": True,
    }
    d = _make_capture_dir(tmp_path, a2c_frame=a2c, rid=rid)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: agent_realpath mismatch"


def test_request_dir_fails_entrypoint_sha_mismatch(tmp_path):
    """agent_entrypoint_sha256 mismatch fails naming the field."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    rid = {
        "agent_realpath": pins.PINNED_AGENT_REALPATH,
        "agent_entrypoint_sha256": "0" * 64,
        "agent_interpreter_realpath": pins.PINNED_AGENT_INTERPRETER_REALPATH,
        "agent_interpreter_sha256": pins.PINNED_AGENT_INTERPRETER_SHA256,
        "python_dont_write_bytecode": True,
    }
    d = _make_capture_dir(tmp_path, a2c_frame=a2c, rid=rid)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: agent_entrypoint_sha256 mismatch"


def test_request_dir_fails_bytecode_not_true(tmp_path):
    """python_dont_write_bytecode not True fails."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    rid = {
        "agent_realpath": pins.PINNED_AGENT_REALPATH,
        "agent_entrypoint_sha256": pins.PINNED_AGENT_ENTRYPOINT_SHA256,
        "agent_interpreter_realpath": pins.PINNED_AGENT_INTERPRETER_REALPATH,
        "agent_interpreter_sha256": pins.PINNED_AGENT_INTERPRETER_SHA256,
        "python_dont_write_bytecode": False,
    }
    d = _make_capture_dir(tmp_path, a2c_frame=a2c, rid=rid)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: python_dont_write_bytecode is not True"


def test_request_dir_fails_no_a2c_response(tmp_path):
    """No a2c response matching the request id is a failure."""
    # Build a capture with c2a but no a2c
    d = _make_capture_dir(tmp_path, a2c_frame=None)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: no agent response captured"


def test_request_dir_fails_no_matching_id(tmp_path):
    """a2c response with wrong id does not match."""
    a2c = {"jsonrpc": "2.0", "id": 999, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: no agent response captured"


# ---- Directory mode request: success path ----

def test_request_dir_valid_capture_exits_1_with_classification_and_observed(tmp_path):
    """Valid capture: line 1 is the classification, line 2 is the observed response."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {
        "protocolVersion": 1,
        "agentInfo": {"name": "hermes", "version": "0.0.1"},
        "agentCapabilities": {},
    }}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    r = _run("request", d)
    assert r.returncode == 1
    lines = r.stdout.strip().splitlines()
    assert len(lines) == 2
    assert lines[0] == "protocol-violation: missing required initialize field"
    assert lines[1] == "observed: result protocolVersion=1 agentCapabilities={}"


def test_request_dir_valid_capture_error_response(tmp_path):
    """Valid capture where agent returns a JSON-RPC error."""
    a2c = {"jsonrpc": "2.0", "id": 0, "error": {"code": -32600, "message": "Invalid request"}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    r = _run("request", d)
    assert r.returncode == 1
    lines = r.stdout.strip().splitlines()
    assert len(lines) == 2
    assert lines[0] == "protocol-violation: missing required initialize field"
    assert lines[1] == "observed: error code=-32600 message=Invalid request"


# ---- Directory mode response: distinct from request ----

def test_response_dir_classifies_result(tmp_path):
    """response <dir> classifies the a2c response's result, NOT the c2a request's params."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {
        "protocolVersion": 1,
        "agentInfo": {"name": "hermes", "version": "0.0.1"},
        "agentCapabilities": {},
    }}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    r = _run("response", d)
    assert r.returncode == 0
    assert r.stdout.strip() == "ok"


def test_response_dir_no_a2c_fails(tmp_path):
    """response <dir> with no a2c frames fails."""
    d = _make_capture_dir(tmp_path, a2c_frame=None)
    r = _run("response", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: no a2c response to classify"


def test_response_dir_error_response(tmp_path):
    """response <dir> with a JSON-RPC error prints the error."""
    a2c = {"jsonrpc": "2.0", "id": 0, "error": {"code": -32600, "message": "Invalid request"}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    r = _run("response", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "error code=-32600 message=Invalid request"


def test_response_dir_distinct_from_request(tmp_path):
    """response <dir> produces different output from request <dir> on the same capture (V-d F20)."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {
        "protocolVersion": 1,
        "agentInfo": {"name": "hermes", "version": "0.0.1"},
        "agentCapabilities": {},
    }}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    r_req = _run("request", d)
    r_resp = _run("response", d)
    # request exits 1 (classification = protocol violation), response exits 0 (result is ok)
    assert r_req.returncode == 1
    assert r_resp.returncode == 0
    # outputs are distinct
    assert r_req.stdout != r_resp.stdout


# ---- Negative control: bad usage ----

def test_usage_error_exits_2():
    """Bad CLI usage exits 2."""
    r = subprocess.run(
        [sys.executable, str(CHECK_INIT), "bogus", str(FIXTURE)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 2
