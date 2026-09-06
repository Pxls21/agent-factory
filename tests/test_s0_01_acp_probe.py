"""tests/test_s0_01_acp_probe.py — drive acp_probe.py against fake agents,
then verify check_initialize.py on the captured directory.

Scenarios: (a) error response, (b) result response, (c) never answers (timeout),
(d) 200 KB stderr before answering (no deadlock), (e) partial line (no newline),
(f) notification before response, (g) non-JSON a2c line, (h) missing env vars,
(i) bad agent path (probe_error), (j) BrokenPipe on c2a write,
(k) bytecode flag unset, (l) SIGTERM-killed agent, (m) ACP_PROBE_TIMEOUT validation,
(n) c2a params == fixture deep comparison.
Mutant kills: "never reads the response", "drops the a2c entry", "probe_error
never surfaces", "non-JSON raw/raw_b64 dropped", "agent_exit_code hardcoded",
"timeout env override ignored", "python_dont_write_bytecode hardcoded True",
"BrokenPipe c2a delivered:false", "fixture params replaced by {}",
"interpreter fields null after wait".
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
    """(b) Agent returns a result: probe captures it, check_initialize classifies correctly.
    V2: interpreter fields must NOT be null (sampled before proc.wait)."""
    r, framedir = _run_probe(tmp_path, agent_result)
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"

    # Verify capture files
    assert (framedir / "timeline.jsonl").exists()
    assert (framedir / "runtime-identity.json").exists()
    assert (framedir / "agent-stderr.txt").exists()
    assert (framedir / "env.json").exists()

    # Parse timeline -- MUST have exactly 2 entries (c2a + a2c)
    entries = [json.loads(line) for line in
               (framedir / "timeline.jsonl").read_text().splitlines() if line.strip()]
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

    # V2: Runtime identity has interpreter fields NOT null (sampled before wait)
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_argv"] == [agent_result]
    assert "probe_path" in rid
    assert "probe_sha256" in rid
    assert rid["agent_exit_code"] == 0  # M7: exact value
    assert "spawned_at_utc" in rid
    # V2: interpreter fields are populated, not null
    assert rid["agent_interpreter_realpath"] is not None, \
        "agent_interpreter_realpath is null (V2: readlink must happen before proc.wait)"
    assert rid["agent_interpreter_sha256"] is not None, \
        "agent_interpreter_sha256 is null (V2: sha must be sampled before proc.wait)"

    # env.json exists with redaction
    env_data = json.loads((framedir / "env.json").read_text())
    assert isinstance(env_data, dict)
    assert env_data.get("PYTHONDONTWRITEBYTECODE") == "1"

    # check_initialize.py request <dir> -- in the sandbox, env.json lacks HERMES_HOME,
    # so the checker hits the HERMES_HOME mismatch before reaching identity pins.
    r2 = subprocess.run(
        [sys.executable, str(CHECK_INIT), "request", str(framedir)],
        capture_output=True, text=True, timeout=30,
    )
    assert r2.returncode == 1
    assert r2.stdout.strip() == "failure_reason: negative: HERMES_HOME mismatch"


def test_probe_error_response(tmp_path, agent_error):
    """(a) Agent returns a JSON-RPC error: probe captures the a2c entry with the error."""
    r, framedir = _run_probe(tmp_path, agent_error)
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"

    entries = [json.loads(line) for line in
               (framedir / "timeline.jsonl").read_text().splitlines() if line.strip()]
    assert len(entries) == 2, f"expected 2 timeline entries, got {len(entries)}"
    assert entries[1]["dir"] == "a2c"
    assert entries[1]["seq"] == 2
    assert entries[1]["frame"]["error"]["code"] == -32600
    assert entries[1]["frame"]["error"]["message"] == "Invalid request"
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_exit_code"] == 0


def test_probe_never_answers(tmp_path, agent_silent):
    """(c) Agent never answers: probe completes within timeout, timeline has 1 entry only.
    L1: timeout env override is honoured (elapsed < 5 s with ACP_PROBE_TIMEOUT=1).
    L7: assert exact exit code, not vacuous is-not-None."""
    t0 = time.monotonic()
    r, framedir = _run_probe(tmp_path, agent_silent, timeout_override=1)
    elapsed = time.monotonic() - t0
    assert r.returncode == 0
    assert elapsed < 10, f"probe took {elapsed:.1f}s with ACP_PROBE_TIMEOUT=1"

    entries = [json.loads(line) for line in
               (framedir / "timeline.jsonl").read_text().splitlines() if line.strip()]
    assert len(entries) == 1
    assert entries[0]["dir"] == "c2a"


def test_probe_stderr_heavy_no_deadlock(tmp_path, agent_stderr_heavy):
    """(d) Agent writes 200 KB to stderr before answering: probe must not deadlock."""
    r, framedir = _run_probe(tmp_path, agent_stderr_heavy)
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"

    stderr_file = framedir / "agent-stderr.txt"
    assert stderr_file.exists()
    assert stderr_file.stat().st_size >= 200000

    entries = [json.loads(line) for line in
               (framedir / "timeline.jsonl").read_text().splitlines() if line.strip()]
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
    assert isinstance(env_data["MY_SECRET_KEY"], dict)
    assert env_data["MY_SECRET_KEY"]["redacted"] is True
    assert env_data["MY_SECRET_KEY"]["len"] == len("supersecret123")
    assert len(env_data["MY_SECRET_KEY"]["sha256_12"]) == 12
    assert env_data["PYTHONDONTWRITEBYTECODE"] == "1"


# ---- H2: partial a2c line ----

def test_probe_partial_line_completes(tmp_path, agent_partial_line):
    """H2: agent writes a partial a2c line (no terminator) -- probe must complete
    within the timeout and record the partial as frame:null with raw/raw_b64."""
    t0 = time.monotonic()
    r, framedir = _run_probe(tmp_path, agent_partial_line, timeout_override=2)
    elapsed = time.monotonic() - t0
    assert elapsed < 15, f"probe took {elapsed:.1f}s -- likely hung on readline"

    entries = [json.loads(line) for line in
               (framedir / "timeline.jsonl").read_text().splitlines() if line.strip()]
    assert len(entries) == 2
    assert entries[1]["dir"] == "a2c"
    assert entries[1]["frame"] is None
    assert "raw" in entries[1]
    assert "raw_b64" in entries[1]
    assert entries[1]["raw"] == '{"jsonrpc":"2.0","id":0,"resu'


# ---- M1: notification before response ----

def test_probe_notification_then_response(tmp_path, agent_notification_then_response):
    """M1: agent emits a notification before the real response -- both must be captured."""
    r, framedir = _run_probe(tmp_path, agent_notification_then_response, timeout_override=5)
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"

    entries = [json.loads(line) for line in
               (framedir / "timeline.jsonl").read_text().splitlines() if line.strip()]
    assert len(entries) == 3, f"expected 3 timeline entries, got {len(entries)}"
    assert entries[1]["dir"] == "a2c"
    assert entries[1]["seq"] == 2
    assert entries[1]["frame"]["method"] == "log"
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
    entries = [json.loads(line) for line in
               (framedir / "timeline.jsonl").read_text().splitlines() if line.strip()]
    spawned = rid["spawned_at_utc"]
    first_t = entries[0]["t_utc"]
    assert spawned <= first_t, f"spawned_at {spawned} > first frame {first_t}"


# ---- M3: probe_error on exception ----

def test_probe_bad_agent_path_writes_probe_error(tmp_path):
    """M3: nonexistent agent path -> exit 1 + probe_error in runtime-identity.json,
    not a bare traceback."""
    r, framedir = _run_probe(tmp_path, "/nonexistent/agent/binary")
    assert r.returncode == 1
    assert "Traceback" not in r.stderr
    assert "acp_probe:" in r.stderr

    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["probe_error"] == (
        "FileNotFoundError: [Errno 2] No such file or directory: '/nonexistent/agent/binary'"
    )


# ---- M7: agent_exit_code exact value ----

def test_probe_sigterm_killed_agent_exit_code(tmp_path, agent_sigterm):
    """M7: SIGTERM-killed agent -> agent_exit_code == -15 (negative signal number)."""
    r, framedir = _run_probe(tmp_path, agent_sigterm, timeout_override=5)
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
    """M10: force an exception in the main body -> exit 1 + probe_error in identity."""
    r, framedir = _run_probe(tmp_path, "/nonexistent/agent/binary")
    assert r.returncode == 1
    rid_path = framedir / "runtime-identity.json"
    assert rid_path.exists()
    rid = json.loads(rid_path.read_text())
    assert rid["probe_error"] == (
        "FileNotFoundError: [Errno 2] No such file or directory: '/nonexistent/agent/binary'"
    )


# ---- M11: non-JSON a2c line ----

def test_probe_non_json_a2c_line(tmp_path, agent_non_json):
    """M11: agent emits 'not json\\n' -> frame is None, raw == 'not json',
    base64.b64decode(raw_b64) == b'not json\\n'."""
    r, framedir = _run_probe(tmp_path, agent_non_json, timeout_override=5)
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"

    entries = [json.loads(line) for line in
               (framedir / "timeline.jsonl").read_text().splitlines() if line.strip()]
    assert len(entries) == 3
    nonjson = entries[1]
    assert nonjson["dir"] == "a2c"
    assert nonjson["frame"] is None
    assert nonjson["raw"] == "not json"
    assert base64.b64decode(nonjson["raw_b64"]) == b"not json\n"


# ---- V7: BrokenPipe deterministic via monkeypatch ----

def test_probe_broken_pipe_deterministic(tmp_path, agent_result):
    """V7: deterministically trigger BrokenPipe by monkeypatching proc.stdin.write.
    The c2a entry must have delivered:False, probe_error must name BrokenPipe,
    and the probe must exit 1."""
    framedir = tmp_path / "capture"
    framedir.mkdir(exist_ok=True)
    env = {
        "S0_01_AGENT": agent_result,
        "S0_01_FRAMEDIR": str(framedir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "5",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }

    # Write a wrapper script that patches stdin.write to raise BrokenPipeError
    wrapper = tmp_path / "run_probe_patched.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe
        import subprocess as _sub

        _OrigPopen = _sub.Popen

        class _PatchedPopen(_OrigPopen):
            def __new__(cls, *a, **kw):
                inst = _OrigPopen.__new__(cls)
                return inst

            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                _orig_write = self.stdin.write
                def _raise_broken(*args, **kwargs):
                    raise BrokenPipeError("simulated broken pipe")
                self.stdin.write = _raise_broken

        with unittest.mock.patch.object(_sub, 'Popen', _PatchedPopen):
            try:
                acp_probe.main()
            except SystemExit as e:
                sys.exit(e.code)
    """))

    r = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 1, f"expected exit 1, got {r.returncode}: stderr={r.stderr}"

    # The timeline must have the c2a entry with delivered:False
    tl_path = framedir / "timeline.jsonl"
    assert tl_path.exists()
    entries = [json.loads(line) for line in tl_path.read_text().splitlines() if line.strip()]
    assert len(entries) >= 1
    c2a = entries[0]
    assert c2a["dir"] == "c2a"
    assert c2a["delivered"] is False

    # probe_error must be set in runtime-identity.json
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["probe_error"] == "BrokenPipeError: agent process exited before c2a write landed"


# ---- V8/A16: ACP_PROBE_TIMEOUT validation ----

def test_probe_timeout_nan_exits_64(tmp_path, agent_result):
    """A16: ACP_PROBE_TIMEOUT=NaN -> exit 64 with named message."""
    r, framedir = _run_probe(tmp_path, agent_result, timeout_override="NaN")
    assert r.returncode == 64
    assert r.stderr.strip() == "acp_probe: ACP_PROBE_TIMEOUT must be a finite float > 0, got 'NaN'"


def test_probe_timeout_negative_exits_64(tmp_path, agent_result):
    """A16: ACP_PROBE_TIMEOUT=-1 -> exit 64 with named message."""
    r, framedir = _run_probe(tmp_path, agent_result, timeout_override="-1")
    assert r.returncode == 64
    assert r.stderr.strip() == "acp_probe: ACP_PROBE_TIMEOUT must be a finite float > 0, got '-1'"


def test_probe_timeout_infinity_exits_64(tmp_path, agent_result):
    """A16: ACP_PROBE_TIMEOUT=inf -> exit 64."""
    r, framedir = _run_probe(tmp_path, agent_result, timeout_override="inf")
    assert r.returncode == 64
    assert r.stderr.strip() == "acp_probe: ACP_PROBE_TIMEOUT must be a finite float > 0, got 'inf'"


def test_probe_timeout_non_numeric_exits_64(tmp_path, agent_result):
    """A16: ACP_PROBE_TIMEOUT=abc -> exit 64 with named message."""
    r, framedir = _run_probe(tmp_path, agent_result, timeout_override="abc")
    assert r.returncode == 64
    assert r.stderr.strip() == "acp_probe: ACP_PROBE_TIMEOUT is not a valid number: 'abc'"


def test_probe_timeout_zero_exits_64(tmp_path, agent_result):
    """A16: ACP_PROBE_TIMEOUT=0 -> exit 64 (must be > 0)."""
    r, framedir = _run_probe(tmp_path, agent_result, timeout_override="0")
    assert r.returncode == 64
    assert r.stderr.strip() == "acp_probe: ACP_PROBE_TIMEOUT must be a finite float > 0, got '0'"


# ---- V9/A16: c2a params == fixture deep comparison ----

def test_probe_c2a_params_match_fixture(tmp_path, agent_result):
    """V9/A16: the probe's c2a entry carries the FIXTURE params exactly.
    Deep-compare the c2a frame params against the fixture file."""
    r, framedir = _run_probe(tmp_path, agent_result)
    assert r.returncode == 0

    fixture = json.loads((P / "fixtures" / "neg-malformed-initialize.json").read_text())
    entries = [json.loads(line) for line in
               (framedir / "timeline.jsonl").read_text().splitlines() if line.strip()]
    c2a_frame = entries[0]["frame"]
    assert c2a_frame["params"] == fixture, \
        f"c2a params differ from fixture: {c2a_frame['params']!r} != {fixture!r}"


# ---- V2: interpreter fields not null ----

def test_probe_interpreter_fields_not_null(tmp_path, agent_result):
    """V2: readlink(/proc/<pid>/exe) is sampled BEFORE proc.wait, so interpreter
    fields must NOT be null for a normal Python agent."""
    r, framedir = _run_probe(tmp_path, agent_result)
    assert r.returncode == 0

    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_interpreter_realpath"] is not None
    assert rid["agent_interpreter_sha256"] is not None
    # The interpreter must be a real path
    assert rid["agent_interpreter_realpath"].startswith("/")
    # The sha256 must be 64 hex chars
    assert len(rid["agent_interpreter_sha256"]) == 64


# ---- L15: missing env vars ----

def test_probe_missing_framedir_exits_64(tmp_path):
    """L15/A10: missing S0_01_FRAMEDIR -> exit 64 with named message."""
    env = os.environ.copy()
    env["S0_01_AGENT"] = "/some/agent"
    env.pop("S0_01_FRAMEDIR", None)
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 64
    assert r.stderr.strip() == "acp_probe: required environment variable S0_01_FRAMEDIR is not set"


def test_probe_missing_agent_exits_64(tmp_path):
    """L15/A10: missing S0_01_AGENT -> exit 64 with named message."""
    env = os.environ.copy()
    env["S0_01_FRAMEDIR"] = str(tmp_path)
    env.pop("S0_01_AGENT", None)
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 64
    assert r.stderr.strip() == "acp_probe: required environment variable S0_01_AGENT is not set"
