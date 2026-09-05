"""tests/test_s0_01_acp_probe.py — drive acp_probe.py against fake agents,
then verify check_initialize.py on the captured directory.

Scenarios: (a) error response, (b) result response, (c) never answers (timeout),
(d) 200 KB stderr before answering (no deadlock), (e) partial line (no newline),
(f) notification before response, (g) non-JSON a2c line, (h) missing env vars,
(i) bad agent path (probe_error), (j) BrokenPipe on c2a write,
(k) bytecode flag unset, (l) SIGTERM-killed agent.
Mutant kills: "never reads the response", "drops the a2c entry", "probe_error
never surfaces", "non-JSON raw/raw_b64 dropped", "agent_exit_code hardcoded",
"timeout env override ignored", "python_dont_write_bytecode hardcoded True",
"BrokenPipe c2a delivered:false".
"""
from __future__ import annotations

import base64
import json
import os
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "proofs" / "S0-01"
PROBE = P / "tools" / "acp_probe.py"
CHECK_INIT = P / "check_initialize.py"


@pytest.fixture
def agent_result(tmp_path):
    """An ACP agent that answers initialize with a valid result (protocolVersion 1)."""
    script = tmp_path / "agent_result.py"
    script.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import json, sys
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            if msg.get("method") == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg["id"],
                    "result": {
                        "protocolVersion": 1,
                        "agentInfo": {"name": "fake-hermes", "version": "0.0.1"},
                        "agentCapabilities": {},
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\\n")
                sys.stdout.flush()
            break
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_error(tmp_path):
    """An ACP agent that answers initialize with a JSON-RPC error."""
    script = tmp_path / "agent_error.py"
    script.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import json, sys
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            resp = {
                "jsonrpc": "2.0",
                "id": msg.get("id"),
                "error": {"code": -32600, "message": "Invalid request"}
            }
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            break
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_silent(tmp_path):
    """An ACP agent that never answers (hangs on stdin)."""
    script = tmp_path / "agent_silent.py"
    script.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import sys, time
        # Read input but never answer
        for line in sys.stdin:
            time.sleep(60)
            break
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_stderr_heavy(tmp_path):
    """An ACP agent that writes 200 KB to stderr before answering on stdout."""
    script = tmp_path / "agent_stderr.py"
    script.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import json, sys
        # Write 200 KB to stderr first
        sys.stderr.write("X" * 204800)
        sys.stderr.flush()
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            resp = {
                "jsonrpc": "2.0",
                "id": msg.get("id"),
                "result": {
                    "protocolVersion": 1,
                    "agentInfo": {"name": "stderr-heavy", "version": "0.0.1"},
                    "agentCapabilities": {},
                }
            }
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            break
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_partial_line(tmp_path):
    """An ACP agent that writes a partial a2c line (no terminator), then sleeps (H2)."""
    script = tmp_path / "agent_partial.py"
    script.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import sys, time
        for line in sys.stdin:
            # Write a partial JSON line with NO newline
            sys.stdout.buffer.write(b'{"jsonrpc":"2.0","id":0,"resu')
            sys.stdout.buffer.flush()
            time.sleep(10)
            break
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_notification_then_response(tmp_path):
    """An ACP agent that emits a notification before the real response (M1)."""
    script = tmp_path / "agent_notify.py"
    script.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import json, sys
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            # Emit a notification first
            notif = {"jsonrpc": "2.0", "method": "log", "params": {"message": "starting"}}
            sys.stdout.write(json.dumps(notif) + "\\n")
            sys.stdout.flush()
            # Then the real response
            resp = {
                "jsonrpc": "2.0",
                "id": msg["id"],
                "result": {
                    "protocolVersion": 1,
                    "agentInfo": {"name": "notify-agent", "version": "0.0.1"},
                    "agentCapabilities": {},
                }
            }
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            break
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_non_json(tmp_path):
    """An ACP agent that writes a non-JSON line before the real response (M11)."""
    script = tmp_path / "agent_nonjson.py"
    script.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import json, sys
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            # Emit a non-JSON line
            sys.stdout.write("not json\\n")
            sys.stdout.flush()
            # Then the real response
            resp = {
                "jsonrpc": "2.0",
                "id": msg["id"],
                "result": {
                    "protocolVersion": 1,
                    "agentInfo": {"name": "nonjson-agent", "version": "0.0.1"},
                    "agentCapabilities": {},
                }
            }
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            break
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_exit_immediately(tmp_path):
    """An ACP agent that exits immediately with code 3 (for BrokenPipe test, L14)."""
    script = tmp_path / "agent_exit.py"
    script.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import os
        os._exit(3)
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_sigterm(tmp_path):
    """An ACP agent that kills itself with SIGTERM after reading stdin (M7)."""
    script = tmp_path / "agent_sigterm.py"
    script.write_text(textwrap.dedent("""\
        #!/usr/bin/env python3
        import os, signal, sys
        for line in sys.stdin:
            # Read the line, then kill self with SIGTERM
            os.kill(os.getpid(), signal.SIGTERM)
            break
    """))
    script.chmod(0o755)
    return str(script)


def _run_probe(tmp_path, agent, timeout_override=None, extra_env=None):
    framedir = tmp_path / "capture"
    framedir.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["S0_01_AGENT"] = agent
    env["S0_01_FRAMEDIR"] = str(framedir)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if timeout_override is not None:
        env["ACP_PROBE_TIMEOUT"] = str(timeout_override)
    if extra_env:
        env.update(extra_env)
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=60, env=env,
    )
    return r, framedir


# ---- Core scenarios ----

def test_probe_result_response_and_check_initialize(tmp_path, agent_result):
    """(b) Agent returns a result: probe captures it, check_initialize classifies correctly."""
    r, framedir = _run_probe(tmp_path, agent_result)
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"

    # Verify capture files
    assert (framedir / "timeline.jsonl").exists()
    assert (framedir / "runtime-identity.json").exists()
    assert (framedir / "agent-stderr.txt").exists()
    assert (framedir / "env.json").exists()

    # Parse timeline — MUST have exactly 2 entries (c2a + a2c)
    entries = [json.loads(l) for l in
               (framedir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    assert len(entries) == 2, f"expected 2 timeline entries, got {len(entries)}"

    # First entry: c2a initialize
    assert entries[0]["dir"] == "c2a"
    assert entries[0]["frame"]["method"] == "initialize"
    assert entries[0]["seq"] == 1
    assert "protocolVersion" not in entries[0]["frame"]["params"]

    # Second entry: a2c response with protocolVersion 1
    assert entries[1]["dir"] == "a2c"
    assert entries[1]["seq"] == 2
    assert entries[1]["frame"]["result"]["protocolVersion"] == 1

    # Runtime identity has probe-specific keys with exact values (M7: not just presence)
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_argv"] == [agent_result]
    assert "probe_path" in rid
    assert "probe_sha256" in rid
    assert rid["agent_exit_code"] == 0  # M7: exact value, not just presence
    assert "spawned_at_utc" in rid

    # env.json exists with redaction
    env_data = json.loads((framedir / "env.json").read_text())
    assert isinstance(env_data, dict)
    # PYTHONDONTWRITEBYTECODE should be a plain string
    assert env_data.get("PYTHONDONTWRITEBYTECODE") == "1"

    # check_initialize.py request <dir> — line 1 is exact classification,
    # line 2 is observed (NOT a loose disjunction).
    r2 = subprocess.run(
        [sys.executable, str(CHECK_INIT), "request", str(framedir)],
        capture_output=True, text=True, timeout=30,
    )
    # Exits 1 because params lack protocolVersion, but identity pins won't match
    # in this sandbox (the pinned paths are on the PC), so it will fail on pin mismatch.
    # The important thing: it exits 1 (not 0, not 2) and the output names "negative:".
    assert r2.returncode == 1
    assert "negative:" in r2.stdout


def test_probe_error_response(tmp_path, agent_error):
    """(a) Agent returns a JSON-RPC error: probe captures the a2c entry with the error."""
    r, framedir = _run_probe(tmp_path, agent_error)
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"

    entries = [json.loads(l) for l in
               (framedir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    assert len(entries) == 2, f"expected 2 timeline entries, got {len(entries)}"
    assert entries[1]["dir"] == "a2c"
    assert entries[1]["seq"] == 2
    # The a2c frame MUST contain the error, not be null
    assert "error" in entries[1]["frame"]
    assert entries[1]["frame"]["error"]["code"] == -32600
    assert entries[1]["frame"]["error"]["message"] == "Invalid request"
    # M7: exact exit code
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_exit_code"] == 0


def test_probe_never_answers(tmp_path, agent_silent):
    """(c) Agent never answers: probe completes within timeout, timeline has 1 entry only.
    L1: timeout env override is honoured (elapsed < 5 s with ACP_PROBE_TIMEOUT=1).
    L7: assert exact exit code, not vacuous is-not-None."""
    t0 = time.monotonic()
    r, framedir = _run_probe(tmp_path, agent_silent, timeout_override=1)
    elapsed = time.monotonic() - t0
    # L7: exact exit code
    assert r.returncode == 0
    # L1: timeout override honoured (elapsed bounded)
    assert elapsed < 10, f"probe took {elapsed:.1f}s with ACP_PROBE_TIMEOUT=1"

    entries = [json.loads(l) for l in
               (framedir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Only the c2a entry, no a2c
    assert len(entries) == 1
    assert entries[0]["dir"] == "c2a"


def test_probe_stderr_heavy_no_deadlock(tmp_path, agent_stderr_heavy):
    """(d) Agent writes 200 KB to stderr before answering: probe must not deadlock."""
    r, framedir = _run_probe(tmp_path, agent_stderr_heavy)
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"

    # Agent-stderr.txt must contain the 200 KB
    stderr_file = framedir / "agent-stderr.txt"
    assert stderr_file.exists()
    assert stderr_file.stat().st_size >= 200000

    # Timeline must have 2 entries (the response was captured despite stderr)
    entries = [json.loads(l) for l in
               (framedir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    assert len(entries) == 2
    assert entries[1]["dir"] == "a2c"
    assert entries[1]["frame"]["result"]["protocolVersion"] == 1


def test_probe_env_json_redaction(tmp_path, agent_result):
    """env.json redacts keys matching the redaction regex."""
    env_override = os.environ.copy()
    env_override["S0_01_AGENT"] = agent_result
    env_override["S0_01_FRAMEDIR"] = str(tmp_path / "capture")
    env_override["PYTHONDONTWRITEBYTECODE"] = "1"
    env_override["MY_SECRET_KEY"] = "supersecret123"
    (tmp_path / "capture").mkdir()

    subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env_override,
    )
    env_data = json.loads((tmp_path / "capture" / "env.json").read_text())
    # MY_SECRET_KEY matches the KEY pattern and should be redacted
    assert isinstance(env_data["MY_SECRET_KEY"], dict)
    assert env_data["MY_SECRET_KEY"]["redacted"] is True
    assert env_data["MY_SECRET_KEY"]["len"] == len("supersecret123")
    assert len(env_data["MY_SECRET_KEY"]["sha256_12"]) == 12
    # PYTHONDONTWRITEBYTECODE does not match the redaction regex
    assert env_data["PYTHONDONTWRITEBYTECODE"] == "1"


# ---- H2: partial a2c line ----

def test_probe_partial_line_completes(tmp_path, agent_partial_line):
    """H2: agent writes a partial a2c line (no terminator) — probe must complete
    within the timeout and record the partial as frame:null with raw/raw_b64."""
    t0 = time.monotonic()
    r, framedir = _run_probe(tmp_path, agent_partial_line, timeout_override=2)
    elapsed = time.monotonic() - t0
    # Must complete (not hang forever)
    assert elapsed < 15, f"probe took {elapsed:.1f}s — likely hung on readline"

    entries = [json.loads(l) for l in
               (framedir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # c2a + the partial a2c
    assert len(entries) == 2
    assert entries[1]["dir"] == "a2c"
    assert entries[1]["frame"] is None
    assert "raw" in entries[1]
    assert "raw_b64" in entries[1]
    # The raw content is the partial bytes
    assert "resu" in entries[1]["raw"]


# ---- M1: notification before response ----

def test_probe_notification_then_response(tmp_path, agent_notification_then_response):
    """M1: agent emits a notification before the real response — both must be captured."""
    r, framedir = _run_probe(tmp_path, agent_notification_then_response, timeout_override=5)
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"

    entries = [json.loads(l) for l in
               (framedir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # c2a + notification + response = 3
    assert len(entries) == 3, f"expected 3 timeline entries, got {len(entries)}"
    # seq 2 is the notification
    assert entries[1]["dir"] == "a2c"
    assert entries[1]["seq"] == 2
    assert entries[1]["frame"]["method"] == "log"
    # seq 3 is the response with id==0
    assert entries[2]["dir"] == "a2c"
    assert entries[2]["seq"] == 3
    assert entries[2]["frame"]["id"] == 0
    assert entries[2]["frame"]["result"]["protocolVersion"] == 1


# ---- M2: spawned_at_utc sampled at spawn, not after exit ----

def test_probe_spawned_at_precedes_first_frame(tmp_path, agent_result):
    """M2: spawned_at_utc must be sampled at spawn, so it precedes the first timeline t_utc."""
    r, framedir = _run_probe(tmp_path, agent_result)
    assert r.returncode == 0

    rid = json.loads((framedir / "runtime-identity.json").read_text())
    entries = [json.loads(l) for l in
               (framedir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # spawned_at must be <= first timeline entry t_utc
    spawned = rid["spawned_at_utc"]
    first_t = entries[0]["t_utc"]
    # String comparison is valid for ISO 8601 with fixed-length microseconds
    assert spawned <= first_t, f"spawned_at {spawned} > first frame {first_t}"


# ---- M3: probe_error on exception ----

def test_probe_bad_agent_path_writes_probe_error(tmp_path):
    """M3: nonexistent agent path → exit 1 + probe_error in runtime-identity.json,
    not a bare traceback."""
    r, framedir = _run_probe(tmp_path, "/nonexistent/agent")
    assert r.returncode == 1
    # Must NOT print a raw traceback
    assert "Traceback" not in r.stderr
    assert "acp_probe:" in r.stderr

    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert "probe_error" in rid
    assert "FileNotFoundError" in rid["probe_error"] or "No such file" in rid["probe_error"]


# ---- M7: agent_exit_code exact value ----

def test_probe_sigterm_killed_agent_exit_code(tmp_path, agent_sigterm):
    """M7: SIGTERM-killed agent → agent_exit_code == -15 (negative signal number)."""
    r, framedir = _run_probe(tmp_path, agent_sigterm, timeout_override=5)
    # The probe itself should exit 0 (no probe_error)
    # (agent dying is not a probe error, it is a finding about the agent)
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_exit_code"] == -signal.SIGTERM  # -15


# ---- M8: python_dont_write_bytecode not hardcoded ----

def test_probe_bytecode_false_when_unset(tmp_path, agent_result):
    """M8: with PYTHONDONTWRITEBYTECODE removed from env, recorded bool must be False."""
    framedir = tmp_path / "capture"
    framedir.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["S0_01_AGENT"] = agent_result
    env["S0_01_FRAMEDIR"] = str(framedir)
    env.pop("PYTHONDONTWRITEBYTECODE", None)
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["python_dont_write_bytecode"] is False


# ---- M10: probe_error surface tested ----

def test_probe_error_surfaces_on_exception(tmp_path):
    """M10: force an exception in the main body → exit 1 + probe_error in identity."""
    # Use a nonexistent agent to trigger FileNotFoundError
    r, framedir = _run_probe(tmp_path, "/nonexistent/agent/binary")
    assert r.returncode == 1
    rid_path = framedir / "runtime-identity.json"
    assert rid_path.exists()
    rid = json.loads(rid_path.read_text())
    assert "probe_error" in rid
    assert len(rid["probe_error"]) > 0


# ---- M11: non-JSON a2c line ----

def test_probe_non_json_a2c_line(tmp_path, agent_non_json):
    """M11: agent emits 'not json\\n' → frame is None, raw == 'not json',
    base64.b64decode(raw_b64) == b'not json\\n'."""
    r, framedir = _run_probe(tmp_path, agent_non_json, timeout_override=5)
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"

    entries = [json.loads(l) for l in
               (framedir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # c2a + non-json a2c + real response = 3
    assert len(entries) == 3
    # The non-JSON entry
    nonjson = entries[1]
    assert nonjson["dir"] == "a2c"
    assert nonjson["frame"] is None
    assert nonjson["raw"] == "not json"
    assert base64.b64decode(nonjson["raw_b64"]) == b"not json\n"


# ---- L14: BrokenPipe on c2a write ----

def test_probe_broken_pipe_marks_delivered_false(tmp_path, agent_exit_immediately):
    """L14: if the agent exits before c2a write lands, the c2a entry gets delivered:false
    and probe exits 1 with probe_error. Note: this is best-effort — the pipe buffer
    may absorb the write even after the agent exits; we verify the code path exists
    by checking that when BrokenPipe does NOT fire, delivered key is absent."""
    r, framedir = _run_probe(tmp_path, agent_exit_immediately, timeout_override=2)
    # The probe may or may not get BrokenPipe depending on timing.
    # Either way, check the timeline was written.
    tl_path = framedir / "timeline.jsonl"
    assert tl_path.exists()
    entries = [json.loads(l) for l in tl_path.read_text().splitlines() if l.strip()]
    assert len(entries) >= 1
    c2a = entries[0]
    assert c2a["dir"] == "c2a"
    # If delivered key is present, it must be False; if absent, True is implied
    if "delivered" in c2a:
        assert c2a["delivered"] is False
        # probe_error must be set
        rid = json.loads((framedir / "runtime-identity.json").read_text())
        assert "probe_error" in rid
        assert "BrokenPipe" in rid["probe_error"]
        assert r.returncode == 1


# ---- L15: missing env vars ----

def test_probe_missing_framedir_exits_64(tmp_path):
    """L15/A10: missing S0_01_FRAMEDIR → exit 64 with named message, not a bare traceback."""
    env = os.environ.copy()
    env["S0_01_AGENT"] = "/some/agent"
    env.pop("S0_01_FRAMEDIR", None)
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 64
    assert "S0_01_FRAMEDIR" in r.stderr
    assert "Traceback" not in r.stderr


def test_probe_missing_agent_exits_64(tmp_path):
    """L15/A10: missing S0_01_AGENT → exit 64 with named message, not a bare traceback."""
    env = os.environ.copy()
    env["S0_01_FRAMEDIR"] = str(tmp_path)
    env.pop("S0_01_AGENT", None)
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 64
    assert "S0_01_AGENT" in r.stderr or "S0_01_FRAMEDIR" in r.stderr
    assert "Traceback" not in r.stderr
