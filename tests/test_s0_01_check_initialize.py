"""tests/test_s0_01_check_initialize.py — check_initialize.py directory mode + file mode.

Tests exact exit codes and output for all directory-mode paths (request + response),
file mode (unchanged from v1), pin validation failures, malformed evidence wrapper (6-verify F13),
usage error exit 64 (8-verify F10 / A10), required-files check (A11), NaN rejection (A11),
seq==1 check (A11), and fixture-absent guard (A11).
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
                      has_timeline=True, has_rid=True, has_env=True,
                      has_stderr=True, extra_files=None):
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

    if has_env:
        (d / "env.json").write_text(json.dumps({
            "HERMES_HOME": pins.PINNED_HERMES_HOME,
            "PYTHONDONTWRITEBYTECODE": "1",
        }) + "\n")

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

def _valid_env_json():
    """Return valid env.json content for tests that need to get past the env check."""
    return json.dumps({
        "HERMES_HOME": pins.PINNED_HERMES_HOME,
        "PYTHONDONTWRITEBYTECODE": "1",
    })


def test_request_dir_fails_no_c2a_frames(tmp_path):
    """Empty timeline (only a2c) fails with the right failure_reason."""
    d = tmp_path / "capture"
    d.mkdir()
    entry = {"seq": 1, "dir": "a2c", "t_utc": "2026-09-05T00:00:00.000000Z",
             "t_mono_ns": 1000000, "frame": {"jsonrpc": "2.0", "id": 0, "result": {}}}
    (d / "timeline.jsonl").write_text(json.dumps(entry, separators=(",", ":")) + "\n")
    (d / "runtime-identity.json").write_text("{}")
    (d / "env.json").write_text(_valid_env_json())
    (d / "agent-stderr.txt").write_text("")
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
    (d / "env.json").write_text(_valid_env_json())
    (d / "agent-stderr.txt").write_text("")
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


# ---- 8-verify F10 / A10: usage error exits 64, not 2 ----

def test_usage_error_exits_64():
    """Bad CLI usage exits 64 (EX_USAGE), not 2."""
    r = subprocess.run(
        [sys.executable, str(CHECK_INIT), "bogus", str(FIXTURE)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 64


def test_usage_error_no_args_exits_64():
    """No args at all exits 64."""
    r = subprocess.run(
        [sys.executable, str(CHECK_INIT)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 64


# ---- 6-verify F13: malformed evidence ----

def test_malformed_timeline_non_json(tmp_path):
    """F13: non-JSON timeline line → exit 1 with failure_reason: malformed evidence."""
    d = tmp_path / "capture"
    d.mkdir()
    (d / "timeline.jsonl").write_text("not json\n")
    (d / "runtime-identity.json").write_text("{}")
    (d / "env.json").write_text(_valid_env_json())
    (d / "agent-stderr.txt").write_text("")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: malformed evidence: JSONDecodeError: Expecting value: line 1 column 1 (char 0)"


def test_malformed_timeline_missing_dir_key(tmp_path):
    """F13: entry without 'dir' key → exit 1 with failure_reason: malformed evidence."""
    d = tmp_path / "capture"
    d.mkdir()
    entry = {"seq": 1, "frame": {"method": "initialize"}}
    (d / "timeline.jsonl").write_text(json.dumps(entry) + "\n")
    (d / "runtime-identity.json").write_text("{}")
    (d / "env.json").write_text(_valid_env_json())
    (d / "agent-stderr.txt").write_text("")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: malformed evidence: KeyError: 'dir'"


# ---- A11: required files ----

def test_request_dir_fails_missing_env_json(tmp_path):
    """A11: env.json absent → failure naming the file."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c, has_env=False)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: env.json absent"


def test_request_dir_fails_missing_agent_stderr(tmp_path):
    """A11: agent-stderr.txt absent → failure naming the file."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c, has_stderr=False)
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: agent-stderr.txt absent"


def test_request_dir_fails_extra_file(tmp_path):
    """A11: extra file in directory → failure."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c, extra_files={"bogus.txt": "evil"})
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: unexpected file bogus.txt"


# ---- A11: NaN rejection ----

def test_request_dir_fails_nan_in_timeline(tmp_path):
    """A11: NaN in timeline → failure_reason: malformed evidence."""
    d = tmp_path / "capture"
    d.mkdir()
    # Write a timeline line with NaN manually
    (d / "timeline.jsonl").write_text(
        '{"seq":1,"dir":"c2a","t_utc":"2026-09-05T00:00:00.000000Z","t_mono_ns":NaN,"frame":null}\n'
    )
    (d / "runtime-identity.json").write_text("{}")
    (d / "env.json").write_text(_valid_env_json())
    (d / "agent-stderr.txt").write_text("")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: malformed evidence: ValueError: NaN/Infinity not allowed in timeline: 'NaN'"


# ---- A11: seq == 1 check ----

def test_request_dir_fails_seq_not_1(tmp_path):
    """A11: c2a initialize seq is not 1 → failure."""
    d = tmp_path / "capture"
    d.mkdir()
    fixture = json.loads(FIXTURE.read_text())
    c2a_frame = {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": fixture}
    entry = {"seq": 5, "dir": "c2a", "t_utc": "2026-09-05T00:00:00.000000Z",
             "t_mono_ns": 1000000, "frame": c2a_frame}
    (d / "timeline.jsonl").write_text(json.dumps(entry, separators=(",", ":")) + "\n")
    (d / "runtime-identity.json").write_text("{}")
    (d / "env.json").write_text(_valid_env_json())
    (d / "agent-stderr.txt").write_text("")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: c2a initialize seq is 5, expected 1"


# ---- A11: fixture absent ----

def test_request_dir_fails_fixture_absent(tmp_path):
    """A11: neg-malformed-initialize.json absent → failure."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    # Use subprocess with inline Python to patch FIXTURE at import time
    r2 = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, %r); "
         "from pathlib import Path; "
         "import check_initialize; "
         "check_initialize.FIXTURE = Path('/nonexistent/fixture.json'); "
         "rc = check_initialize._check_request_directory(Path(%r)); "
         "raise SystemExit(rc)" % (str(P), str(d))],
        capture_output=True, text=True, timeout=30,
    )
    assert r2.returncode == 1
    assert r2.stdout.strip() == "failure_reason: negative: fixtures/neg-malformed-initialize.json absent"


# ---- V12: input-error exit 64, not 2 (mutant C02 killer) ----

def test_input_error_non_initialize_frame_exits_64(tmp_path):
    """V12: file mode with a non-initialize frame exits 64 (input error, not deferred).
    This kills the mutant that reverts the exit code from 64 back to 2."""
    f = tmp_path / "session_new.jsonl"
    f.write_text(json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "session/new", "params": {}
    }) + "\n")
    r = _run("request", f)
    assert r.returncode == 64
    assert r.stderr.strip() == "input error: frame method is 'session/new', not 'initialize'"


# ---- V13: extra subdirectory rejected (not just files) ----

def test_request_dir_fails_extra_subdirectory(tmp_path):
    """V13: extra subdirectory under the capture dir is a Failure, same as extra files.
    This kills the mutant that filters with is_file() instead of iterdir()."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    (d / "sneaky_subdir").mkdir()
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: unexpected file sneaky_subdir"


# ---- V14: env.json HERMES_HOME and PYTHONDONTWRITEBYTECODE validated ----

def test_request_dir_fails_hermes_home_mismatch(tmp_path):
    """V14/A17: env.json with wrong HERMES_HOME → failure."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    # Overwrite env.json with wrong HERMES_HOME
    (d / "env.json").write_text(json.dumps({
        "HERMES_HOME": "/wrong/path",
        "PYTHONDONTWRITEBYTECODE": "1",
    }))
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: HERMES_HOME mismatch"


def test_request_dir_fails_pythondontwritebytecode_mismatch(tmp_path):
    """V14/A17: env.json with wrong PYTHONDONTWRITEBYTECODE → failure."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    # Overwrite env.json with correct HERMES_HOME but wrong bytecode
    (d / "env.json").write_text(json.dumps({
        "HERMES_HOME": pins.PINNED_HERMES_HOME,
        "PYTHONDONTWRITEBYTECODE": "0",
    }))
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: PYTHONDONTWRITEBYTECODE mismatch"


def test_request_dir_fails_empty_env_json(tmp_path):
    """V14/A17: env.json with {} (no keys) → HERMES_HOME mismatch."""
    a2c = {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": 1, "agentCapabilities": {}}}
    d = _make_capture_dir(tmp_path, a2c_frame=a2c)
    (d / "env.json").write_text("{}")
    r = _run("request", d)
    assert r.returncode == 1
    assert r.stdout.strip() == "failure_reason: negative: HERMES_HOME mismatch"
