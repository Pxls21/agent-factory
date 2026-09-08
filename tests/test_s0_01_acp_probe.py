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
    script.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
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
        sys.stdin.read()
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_error(tmp_path):
    """An ACP agent that answers initialize with a JSON-RPC error."""
    script = tmp_path / "agent_error.py"
    script.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
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
        sys.stdin.read()
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_silent(tmp_path):
    """An ACP agent that never answers (hangs on stdin)."""
    script = tmp_path / "agent_silent.py"
    script.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
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
    script.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
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
        sys.stdin.read()
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_partial_line(tmp_path):
    """An ACP agent that writes a partial a2c line (no terminator), then sleeps (H2)."""
    script = tmp_path / "agent_partial.py"
    script.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
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
    script.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
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
        sys.stdin.read()
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_non_json(tmp_path):
    """An ACP agent that writes a non-JSON line before the real response (M11)."""
    script = tmp_path / "agent_nonjson.py"
    script.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
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
        sys.stdin.read()
    """))
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def agent_sigterm(tmp_path):
    """An ACP agent that kills itself with SIGTERM after reading stdin (M7)."""
    script = tmp_path / "agent_sigterm.py"
    script.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
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

    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_argv"] == [agent_result]
    assert "probe_path" in rid

    # env.json exists with redaction
    env_data = json.loads((framedir / "env.json").read_text())
    assert isinstance(env_data, dict)
    assert env_data.get("PYTHONDONTWRITEBYTECODE") == "1"

    # check_initialize.py request <dir> -- the A22 validator rejects the
    # result response (pinned agent accepted a malformed initialize).
    r2 = subprocess.run(
        [sys.executable, str(CHECK_INIT), "request", str(framedir)],
        capture_output=True, text=True, timeout=30,
    )
    assert r2.returncode == 1
    assert r2.stdout.splitlines()[0] == "failure_reason: negative: pinned agent accepted a malformed initialize (result protocolVersion=1)"


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
    assert stderr_file.stat().st_size == 204800

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
    not a bare traceback. R6-N5b-F18: the M3 handler also writes whatever timeline
    entries have accumulated (partial timeline). Kills AP-35."""
    r, framedir = _run_probe(tmp_path, "/nonexistent/agent/binary")
    assert r.returncode == 1
    assert "Traceback" not in r.stderr
    assert r.stderr.strip() == "acp_probe: FileNotFoundError: [Errno 2] No such file or directory: '/nonexistent/agent/binary'"

    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["probe_error"] == (
        "FileNotFoundError: [Errno 2] No such file or directory: '/nonexistent/agent/binary'"
    )
    # M3 handler must write timeline.jsonl (even if empty — kills AP-35)
    assert (framedir / "timeline.jsonl").exists(), (
        "timeline.jsonl absent after M3 exception — the partial-timeline write is missing"
    )


# ---- M7: agent_exit_code exact value ----

def test_probe_sigterm_killed_agent_exit_code(tmp_path, agent_sigterm):
    """M7: SIGTERM-killed agent -> agent_exit_code == -15 (negative signal number).
    The early retry loop samples right after Popen, before the agent reaches
    stdin, so the interpreter is always sampled (rc 0)."""
    r, framedir = _run_probe(tmp_path, agent_sigterm, timeout_override=5)
    assert r.returncode == 0, f"expected exit 0, got {r.returncode}: stderr={r.stderr}"
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_exit_code"] == -signal.SIGTERM  # -15
    assert rid["agent_interpreter_realpath"] == os.path.realpath(sys.executable)
    assert rid["agent_interpreter_sha256"] is not None


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
    assert len(entries) == 1
    c2a = entries[0]
    assert c2a["dir"] == "c2a"
    assert c2a["delivered"] is False

    # probe_error must be set in runtime-identity.json
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["probe_error"] == "BrokenPipeError: agent process exited before c2a write landed"
    # N5e-F2: the early retry loop samples the interpreter while the child is
    # still alive, so on a BrokenPipe capture the fields are NON-null.
    assert rid["agent_interpreter_realpath"] is not None
    assert rid["agent_interpreter_sha256"] is not None


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


def test_probe_timeout_space_exits_64(tmp_path, agent_result):
    """R5-N5-F15: ACP_PROBE_TIMEOUT=' ' -> exit 64."""
    r, framedir = _run_probe(tmp_path, agent_result, timeout_override=" ")
    assert r.returncode == 64
    assert r.stderr.strip() == "acp_probe: ACP_PROBE_TIMEOUT is not a valid number: ' '"


def test_probe_timeout_empty_string_exits_64(tmp_path, agent_result):
    """R5-N5-F15: ACP_PROBE_TIMEOUT='' -> exit 64."""
    r, framedir = _run_probe(tmp_path, agent_result, timeout_override="")
    assert r.returncode == 64
    assert r.stderr.strip() == "acp_probe: ACP_PROBE_TIMEOUT is not a valid number: ''"


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

def test_probe_interpreter_fields_pinned(tmp_path, agent_result):
    """R5-N5-F1: the recorded interpreter must equal os.path.realpath(sys.executable)
    and its sha. The agent_result fixture uses #!{sys.executable}, so the
    child's /proc/<pid>/exe resolves to the runner's interpreter."""
    r, framedir = _run_probe(tmp_path, agent_result)
    assert r.returncode == 0

    rid = json.loads((framedir / "runtime-identity.json").read_text())
    expected_interp = os.path.realpath(sys.executable)
    assert rid["agent_interpreter_realpath"] == expected_interp, (
        f"interpreter realpath {rid['agent_interpreter_realpath']!r} != {expected_interp!r}"
    )
    import hashlib
    expected_sha = hashlib.sha256(Path(expected_interp).read_bytes()).hexdigest()
    assert rid["agent_interpreter_sha256"] == expected_sha, (
        f"interpreter sha {rid['agent_interpreter_sha256']!r} != {expected_sha!r}"
    )


# ---- L15: missing env vars ----

def test_probe_missing_framedir_exits_64():
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


# ---- 4-F10/6-F8: ACP_PROBE_TIMEOUT writes probe_error + exit 64 ----

def test_probe_timeout_nan_writes_probe_error(tmp_path, agent_result):
    """4-F10/6-F8: ACP_PROBE_TIMEOUT=NaN -> exit 64 + probe_error in runtime-identity.json."""
    r, framedir = _run_probe(tmp_path, agent_result, timeout_override="NaN")
    assert r.returncode == 64
    rid_path = framedir / "runtime-identity.json"
    assert rid_path.exists(), "runtime-identity.json not written on timeout validation failure"
    rid = json.loads(rid_path.read_text())
    assert rid["probe_error"] == "ACP_PROBE_TIMEOUT must be a finite float > 0, got 'NaN'"


def test_probe_timeout_negative_writes_probe_error(tmp_path, agent_result):
    """4-F10/6-F8: ACP_PROBE_TIMEOUT=-1 -> exit 64 + probe_error in runtime-identity.json."""
    r, framedir = _run_probe(tmp_path, agent_result, timeout_override="-1")
    assert r.returncode == 64
    rid_path = framedir / "runtime-identity.json"
    assert rid_path.exists()
    rid = json.loads(rid_path.read_text())
    assert rid["probe_error"] == "ACP_PROBE_TIMEOUT must be a finite float > 0, got '-1'"


def test_probe_timeout_abc_writes_probe_error(tmp_path, agent_result):
    """4-F10/6-F8: ACP_PROBE_TIMEOUT=abc -> exit 64 + probe_error in runtime-identity.json."""
    r, framedir = _run_probe(tmp_path, agent_result, timeout_override="abc")
    assert r.returncode == 64
    rid_path = framedir / "runtime-identity.json"
    assert rid_path.exists()
    rid = json.loads(rid_path.read_text())
    assert rid["probe_error"] == "ACP_PROBE_TIMEOUT is not a valid number: 'abc'"


# ---- 4-F11: empty/invalid S0_01_FRAMEDIR ----

def test_probe_empty_framedir_exits_64_no_probe_error(tmp_path):
    """4-F11/R5-N5-F4: S0_01_FRAMEDIR='' -> exit 64 with 'is empty' message.
    No probe_error is written (documented exception: failure before the wrapped body).
    R6-N5b-F12: runtime-identity.json must be ABSENT."""
    env = os.environ.copy()
    env["S0_01_AGENT"] = "/some/agent"
    env["S0_01_FRAMEDIR"] = ""
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env, cwd=str(tmp_path),
    )
    assert r.returncode == 64
    assert r.stderr.strip() == "acp_probe: required environment variable S0_01_FRAMEDIR is empty"
    assert "Traceback" not in r.stderr
    # No runtime-identity.json created (failure before the wrapped body)
    assert not (tmp_path / "runtime-identity.json").exists()


def test_probe_framedir_is_file_exits_64(tmp_path, agent_result):
    """4-F11: S0_01_FRAMEDIR pointing to a regular file -> exit 64 (makedirs OSError)."""
    notadir = tmp_path / "notadir"
    notadir.write_text("x")
    env = os.environ.copy()
    env["S0_01_AGENT"] = agent_result
    env["S0_01_FRAMEDIR"] = str(notadir)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 64
    assert r.stderr.splitlines()[0] == "acp_probe: S0_01_FRAMEDIR error: [Errno 17] File exists: '%s'" % str(notadir)
    assert "Traceback" not in r.stderr


# ---- 6-F7: interpreter identity sampled from CHILD's /proc/<pid>/exe ----

def test_probe_interpreter_is_child_not_self(tmp_path):
    """6-F7: the recorded interpreter must be the CHILD's exe, not the probe's.
    A bash agent's /proc/<pid>/exe is bash, not python. If the probe read
    /proc/self/exe instead, it would record python. This test kills that mutant."""
    agent = tmp_path / "agent.sh"
    agent.write_text(
        '#!/bin/bash\n'
        'read line\n'
        'echo \'{"jsonrpc":"2.0","id":0,"result":{"protocolVersion":1,"agentCapabilities":{}}}\'\n'
        'sleep 5\n'
    )
    agent.chmod(0o755)
    r, framedir = _run_probe(tmp_path, str(agent), timeout_override=5)
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    # The child's interpreter must NOT be the probe's own python
    probe_exe = os.readlink(f"/proc/{os.getpid()}/exe")
    assert rid["agent_interpreter_realpath"] != probe_exe, (
        f"recorded interpreter {rid['agent_interpreter_realpath']!r} matches the probe's "
        f"own exe {probe_exe!r} — the probe is reading /proc/self/exe, not /proc/<child>/exe"
    )
    # It should be bash or sh
    assert rid["agent_interpreter_realpath"] is not None


# ---- 4-F15: spawned_at two-sided ----

def test_probe_spawned_at_two_sided(tmp_path, agent_result):
    """4-F15: spawned_at_utc is bracketed: after a pre-Popen timestamp and before
    the first frame. A hardcoded 1970 epoch constant would fail the lower bound."""
    import datetime
    t0 = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    r, framedir = _run_probe(tmp_path, agent_result)
    assert r.returncode == 0
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    entries = [json.loads(line) for line in
               (framedir / "timeline.jsonl").read_text().splitlines() if line.strip()]
    spawned = rid["spawned_at_utc"]
    first_t = entries[0]["t_utc"]
    assert t0 <= spawned, f"spawned_at {spawned} is before the test's pre-Popen time {t0}"
    assert spawned <= first_t, f"spawned_at {spawned} > first frame {first_t}"


# ---- R5-N5-F7: producer identity fields pinned against a live run ----

def test_probe_identity_fields_all_pinned(tmp_path):
    """R5-N5-F7/R6-N5b-F2: every runtime-identity field the validator pins is asserted
    against the live producer run: probe_sha256, agent_child_pid (== the pid the agent
    itself reports), agent_realpath, agent_entrypoint_sha256, interpreter sha, and
    redacted dict sha256_12. Kills AP-17/AP-12/AP-12b/AP-12c/AP-19/AP-21/AP-22."""
    import hashlib
    # Agent that writes its own PID to a file so we can verify agent_child_pid
    pid_file = tmp_path / "agent_pid.txt"
    agent_script = tmp_path / "agent_with_pid.py"
    agent_script.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
        import json, sys, os
        pid_path = os.environ.get("_TEST_PID_FILE", "")
        if pid_path:
            with open(pid_path, "w") as f:
                f.write(str(os.getpid()))
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
                        "agentInfo": {"name": "pid-agent", "version": "0.0.1"},
                        "agentCapabilities": {},
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\\n")
                sys.stdout.flush()
            break
        sys.stdin.read()
    """))
    agent_script.chmod(0o755)
    sentinel_val = "sentinel_for_sha_check_42"
    # N5e-F11: sanitized env so the redacted tally is pinned at exactly the
    # sentinel — a live CI env full of real *KEY*/*TOKEN*/*SECRET* variables
    # would otherwise inflate the count.
    framedir = tmp_path / "capture"
    framedir.mkdir(exist_ok=True)
    env = {
        "S0_01_AGENT": str(agent_script),
        "S0_01_FRAMEDIR": str(framedir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "5",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "_TEST_PID_FILE": str(pid_file),
        "MY_SENTINEL_SECRET": sentinel_val,
    }
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 0, f"probe failed: {r.stderr}"

    rid = json.loads((framedir / "runtime-identity.json").read_text())
    probe_file = P / "tools" / "acp_probe.py"
    expected_probe_sha = hashlib.sha256(probe_file.read_bytes()).hexdigest()
    assert rid["probe_sha256"] == expected_probe_sha, (
        f"probe_sha256 {rid['probe_sha256']!r} != committed {expected_probe_sha!r}"
    )
    # agent_child_pid == the pid the agent itself reports (kills AP-12b/AP-12c)
    reported_pid = int(pid_file.read_text())
    assert rid["agent_child_pid"] == reported_pid, (
        f"agent_child_pid {rid['agent_child_pid']!r} != agent-reported {reported_pid}"
    )
    # agent_realpath == os.path.realpath(agent) (kills AP-21)
    assert rid["agent_realpath"] == os.path.realpath(str(agent_script)), (
        f"agent_realpath {rid['agent_realpath']!r} != {os.path.realpath(str(agent_script))!r}"
    )
    # agent_entrypoint_sha256 == sha256 of agent file bytes (kills AP-22)
    expected_entry_sha = hashlib.sha256(
        Path(os.path.realpath(str(agent_script))).read_bytes()
    ).hexdigest()
    assert rid["agent_entrypoint_sha256"] == expected_entry_sha, (
        f"agent_entrypoint_sha256 {rid['agent_entrypoint_sha256']!r} != {expected_entry_sha!r}"
    )
    # interpreter sha matches the sha of the file at the realpath
    expected_interp = os.path.realpath(sys.executable)
    expected_interp_sha = hashlib.sha256(Path(expected_interp).read_bytes()).hexdigest()
    assert rid["agent_interpreter_sha256"] == expected_interp_sha
    # env.json: explicit sentinel must be redacted with correct sha256_12
    env_data = json.loads((framedir / "env.json").read_text())
    sentinel_entry = env_data.get("MY_SENTINEL_SECRET")
    assert isinstance(sentinel_entry, dict) and sentinel_entry.get("redacted") is True, (
        "MY_SENTINEL_SECRET was not redacted"
    )
    expected_12 = hashlib.sha256(sentinel_val.encode("utf-8")).hexdigest()[:12]
    assert sentinel_entry["sha256_12"] == expected_12, (
        f"sentinel sha256_12 {sentinel_entry['sha256_12']!r} != {expected_12!r}"
    )
    # Exactly one redacted key under the sanitized test env (the sentinel)
    redacted_seen = sum(1 for v in env_data.values()
                        if isinstance(v, dict) and v.get("redacted") is True)
    assert redacted_seen == 1, (
        f"expected exactly 1 redacted key (the sentinel), got {redacted_seen}"
    )


# ---- R5-N5-F16: makedirs branch (absent-but-creatable framedir) ----

def test_probe_creates_absent_framedir(tmp_path, agent_result):
    """R5-N5-F16: S0_01_FRAMEDIR pointing to a nonexistent-but-creatable dir
    is created by makedirs and the probe succeeds."""
    framedir = tmp_path / "deep" / "nested" / "capture"
    assert not framedir.exists()
    env = os.environ.copy()
    env["S0_01_AGENT"] = agent_result
    env["S0_01_FRAMEDIR"] = str(framedir)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"
    assert framedir.is_dir()
    assert (framedir / "timeline.jsonl").exists()
    assert (framedir / "runtime-identity.json").exists()


# ---- R6-N5b-F10: S0_01_AGENT="" ----

def test_probe_empty_agent_exits_64(tmp_path):
    """R6-N5b-F10: S0_01_AGENT='' -> exit 64 with exact 'is empty' message.
    Kills AP-29 (empty check applies only to FRAMEDIR mutant)."""
    env = os.environ.copy()
    env["S0_01_AGENT"] = ""
    env["S0_01_FRAMEDIR"] = str(tmp_path)
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 64
    assert r.stderr.strip() == "acp_probe: required environment variable S0_01_AGENT is empty"


# ---- R6-N5b-F8: redaction regex covers all alternatives ----

def test_probe_env_redaction_all_alternatives(tmp_path, agent_result):
    """R6-N5b-F8: one sentinel per regex alternative (SECRET, PASSWORD, NSEC, PRIV),
    each asserted redacted. Kills AP-25 (regex narrowed to KEY|TOKEN)."""
    import hashlib
    sentinels = {
        "MY_SECRET_VALUE": "secret_test_val_1",
        "DB_PASSWORD_1": "password_test_val_2",
        "NOSTR_NSEC_HEX": "nsec_test_val_3",
        "APP_PRIV_CONFIG": "priv_test_val_4",
    }
    r, framedir = _run_probe(tmp_path, agent_result, extra_env=sentinels)
    assert r.returncode == 0
    env_data = json.loads((framedir / "env.json").read_text())
    for key_name, raw_val in sentinels.items():
        entry = env_data.get(key_name)
        assert isinstance(entry, dict) and entry.get("redacted") is True, (
            f"{key_name} was not redacted (regex alternative missing)"
        )
        expected_12 = hashlib.sha256(raw_val.encode("utf-8")).hexdigest()[:12]
        assert entry["sha256_12"] == expected_12, (
            f"{key_name} sha256_12 {entry['sha256_12']!r} != {expected_12!r}"
        )


# ---- R6-N5b-F5: interpreter sample failure is FAIL-LOUD ----

def test_probe_interpreter_sample_failure(tmp_path, agent_result):
    """R6-N5b-F5: OSError while sampling /proc/<pid>/exe sets probe_error
    'interpreter sample failed: <exc>' and exits 1. Uses monkeypatch via
    a wrapper to force os.readlink to raise on /proc/*/exe."""
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
    wrapper = tmp_path / "run_probe_readlink_fail.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        _orig_readlink = os.readlink
        def _failing_readlink(path):
            if "/proc/" in str(path) and "/exe" in str(path):
                raise OSError("No such process")
            return _orig_readlink(path)

        with unittest.mock.patch.object(os, 'readlink', _failing_readlink):
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
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["probe_error"] == "interpreter sample failed: No such process"
    assert r.stderr.strip() == "acp_probe: interpreter sample failed: No such process"


# ---- N5d-F1: probe never exits 0 with unsampled interpreter identity ----

def test_probe_agent_exits_without_output_keeps_interpreter_identity(tmp_path):
    """N5d-F1 shape A: agent does import sys; sys.exit(0) without writing to stdout.
    rc is race-decided (the c2a write lands before or after the exit); the
    interpreter triple is constant."""
    agent = tmp_path / "agent_silent_exit.py"
    agent.write_text(f"#!{sys.executable}\nimport sys\nsys.exit(0)\n")
    agent.chmod(0o755)
    r, framedir = _run_probe(tmp_path, str(agent))
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_exit_code"] == 0
    assert r.returncode in (0, 1)
    if r.returncode == 1:
        assert rid["probe_error"] == "BrokenPipeError: agent process exited before c2a write landed"
        assert r.stderr.strip() == "acp_probe: BrokenPipeError: agent process exited before c2a write landed"
    else:
        assert "probe_error" not in rid
    # Interpreter identity is always sampled (early retry loop)
    assert rid["agent_interpreter_realpath"] is not None
    assert rid["agent_interpreter_sha256"] is not None


def test_probe_interpreter_sample_failure_after_child_exit(tmp_path):
    """N5d-F1: readlink patched to sleep 1 s then raise (child reaped by then).
    Without the poll() guard the failure must still be loud: exit 1 + exact reason.
    Uses a quick-exit agent (os._exit after response, no sys.stdin.read) so the
    child is dead before the in-loop readlink returns."""
    # Dedicated quick-exit agent: writes response then exits immediately via os._exit
    agent = tmp_path / "agent_quick_exit.py"
    agent.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
        import json, sys, os
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
                        "agentInfo": {"name": "quick-exit", "version": "0.0.1"},
                        "agentCapabilities": {},
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\\n")
                sys.stdout.flush()
            os._exit(0)
    """))
    agent.chmod(0o755)
    framedir = tmp_path / "capture"
    framedir.mkdir(exist_ok=True)
    env = {
        "S0_01_AGENT": str(agent),
        "S0_01_FRAMEDIR": str(framedir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "5",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }
    wrapper = tmp_path / "run_probe_readlink_delay_fail.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, time, unittest.mock
        import select as _select_mod
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        _orig_readlink = os.readlink
        def _delayed_failing_readlink(path):
            if "/proc/" in str(path) and "/exe" in str(path):
                time.sleep(1)
                raise OSError("No such process")
            return _orig_readlink(path)

        # N5e: add a brief delay before select to ensure the os._exit agent is
        # dead by the time the in-loop poll() check runs — kills mutant G2.
        _orig_select = _select_mod.select
        _select_called = [False]
        def _settling_select(*a, **kw):
            if not _select_called[0]:
                _select_called[0] = True
                time.sleep(0.1)
            return _orig_select(*a, **kw)

        with unittest.mock.patch.object(os, 'readlink', _delayed_failing_readlink), \\
             unittest.mock.patch.object(_select_mod, 'select', _settling_select):
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
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["probe_error"] == "interpreter sample failed: No such process"
    assert r.stderr.strip() == "acp_probe: interpreter sample failed: No such process"


# ---- N5e: F1/F2/F3/F8 agent-independence scenarios ----


def test_probe_fast_exit_agent_is_deterministic(tmp_path):
    """N5e-F1: an agent that writes one byte and os._exit(0)s immediately must
    yield a CONSTANT interpreter-sample result across 20 runs.  The post-Popen
    retry loop makes the interpreter identity deterministic (always sampled);
    rc may vary (BrokenPipe if stdin.write races with the child's exit)."""
    agent = tmp_path / "agent_fast_exit.py"
    agent.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
        import sys, os
        sys.stdout.write('x')
        sys.stdout.flush()
        os._exit(0)
    """))
    agent.chmod(0o755)
    interp_outcomes = set()
    for i in range(20):
        framedir = tmp_path / f"capture_{i}"
        framedir.mkdir()
        env = os.environ.copy()
        env["S0_01_AGENT"] = str(agent)
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["ACP_PROBE_TIMEOUT"] = "5"
        subprocess.run(
            [sys.executable, str(PROBE)],
            capture_output=True, text=True, timeout=30, env=env,
        )
        rid = json.loads((framedir / "runtime-identity.json").read_text())
        interp_outcomes.add((
            rid["agent_interpreter_realpath"] is None,
            rid["agent_interpreter_sha256"] is None,
            rid["agent_exit_code"],
        ))
    assert len(interp_outcomes) == 1, (
        f"fast-exit agent gave {len(interp_outcomes)} distinct interpreter "
        f"outcomes across 20 runs: {interp_outcomes}"
    )
    # The interpreter must always be sampled (never null)
    sole_outcome = interp_outcomes.pop()
    assert sole_outcome == (False, False, 0), (
        f"expected (interp_null=False, sha_null=False, exit=0), got {sole_outcome}"
    )


def test_probe_post_loop_sha256_failure_truthful_error(tmp_path):
    """N5e-F3: the post-loop sample block must report the REAL exception when
    readlink succeeded but sha256 failed, not the fixed 'agent exited before
    its first a2c byte' wording.  This test exercises the post-loop block by
    defeating the early retry loop DETERMINISTICALLY (its deadline patched to 0,
    so it makes exactly one attempt, which fails) and using a silent agent (no
    a2c data, so the in-loop sample never fires).  After the a2c timeout the
    post-loop readlink — the SECOND readlink of the run — succeeds with the fake
    path but sha256 fails.  VERIFY-N5g F1: the gated readlink is path-aware — a
    read of /proc/self/exe returns a sentinel, so the post-loop site must read
    the CHILD's exe (kills mutant LG2-POST); no wall clock anywhere.
    VERIFY-N5g-b F1: the gate is PHASE-aware (early loop = main thread alone;
    post-loop = drain thread alive) and the wrapper prints its own mechanism
    (RL_CALLS / DEADLINE_SEEN), which the test asserts — an inlined deadline
    (mutant DL-INLINE) now dies on RL_CALLS; a call-count gate let it live."""
    agent = tmp_path / "agent_silent_stdin.py"
    agent.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
        import sys
        sys.stdin.readline()
        import time
        time.sleep(30)
    """))
    agent.chmod(0o755)

    framedir = tmp_path / "capture"
    framedir.mkdir()
    env = {
        "S0_01_AGENT": str(agent),
        "S0_01_FRAMEDIR": str(framedir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "1",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }

    wrapper = tmp_path / "f3_wrapper.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, threading, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        _orig_readlink = os.readlink
        _fake_path = "/tmp/fake_interp (deleted)"
        _rl_calls = [0]

        def _gated_readlink(path):
            if "/proc/self/exe" in str(path):
                return "/SELF/should-never-be-sampled"   # the site must read the CHILD's exe (LG2-POST)
            if "/proc/" in str(path) and "/exe" in str(path):
                _rl_calls[0] += 1
                # PHASE gate (VERIFY-N5g-b F1, mutant DL-INLINE): the early loop runs BEFORE the
                # stderr drain thread starts, so while the main thread is alone EVERY attempt
                # fails; only the post-loop site (drain thread alive, agent still running) gets
                # the fake path.  A call-count gate ("call 1 fails, call 2 succeeds") let an
                # inlined 0.2 s deadline survive: the loop's 2nd attempt succeeded 2 ms later
                # with the identical error text.  Under this gate an inlined deadline retries
                # ~100 times -> RL_CALLS != 2 -> red.
                if threading.active_count() == 1:
                    raise OSError("No such process")      # early-loop attempt(s)
                return _fake_path                        # the post-loop site
            return _orig_readlink(path)

        _orig_sha256 = acp_probe._sha256_file
        def _gated_sha256(path):
            if path == _fake_path:
                raise FileNotFoundError(2, "No such file or directory", path)
            return _orig_sha256(path)

        with unittest.mock.patch.object(os, 'readlink', _gated_readlink), \\
             unittest.mock.patch.object(acp_probe, '_sha256_file', _gated_sha256), \\
             unittest.mock.patch.object(acp_probe, '_EARLY_SAMPLE_DEADLINE_S', 0.0):
            try:
                acp_probe.main()
            except SystemExit as e:
                _rc = e.code
            else:
                _rc = 0
            # VERIFY-N5g-b F1: the killer asserts its OWN mechanism — exactly two child readlinks
            # (one failing early attempt, then the post-loop site) under the patched deadline. An
            # inlined deadline constant or an extra readlink would otherwise make this test vacuous.
            print(f"RL_CALLS={{_rl_calls[0]}} DEADLINE_SEEN={{acp_probe._EARLY_SAMPLE_DEADLINE_S}}", flush=True)
            sys.exit(_rc)
    """))

    r = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 1, f"expected exit 1, got {r.returncode}: stderr={r.stderr}"
    assert "RL_CALLS=2 DEADLINE_SEEN=0.0" in r.stdout.splitlines(), r.stdout
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    # N5f-F3: exact equality — the probe_error must carry the full prefix + path
    expected_f3_error = (
        "interpreter sample failed: [Errno 2] No such file or directory: "
        "'/tmp/fake_interp (deleted)'"
    )
    assert rid["probe_error"] == expected_f3_error, (
        f"expected exact probe_error, got {rid['probe_error']!r}"
    )
    assert rid["agent_interpreter_realpath"] == "/tmp/fake_interp (deleted)"
    assert rid["agent_interpreter_sha256"] is None


def test_probe_self_deleting_script_is_probe_error_not_traceback(tmp_path):
    """N5f-F6: an agent that unlinks its OWN SCRIPT file at start.  The
    entrypoint sha256 of the now-deleted agent produces a graceful degradation:
    rc 1, no Traceback, all four files present, 11 identity keys +
    probe_error with agent_entrypoint_sha256=None.  The REAL checker
    must print the producer error, never 'env.json absent'."""
    agent = tmp_path / "agent_self_delete.py"
    agent_path = str(agent)
    agent.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
        import os, sys, json
        os.unlink(os.path.abspath(__file__))
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            resp = {
                "jsonrpc": "2.0",
                "id": msg.get("id"),
                "error": {"code": -32602, "message": "Invalid params"},
            }
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            break
        sys.stdin.read()
    """))
    agent.chmod(0o755)
    r, framedir = _run_probe(tmp_path, agent_path, timeout_override=5)
    assert r.returncode == 1, f"expected exit 1, got {r.returncode}: stderr={r.stderr}"
    assert "Traceback" not in r.stderr, (
        f"uncaught traceback leaked to stderr: {r.stderr}"
    )
    # All four files must exist
    for name in ("runtime-identity.json", "env.json", "timeline.jsonl", "agent-stderr.txt"):
        assert (framedir / name).exists(), f"{name} absent in capture"
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    # N5g-F9: identity key set derived from pins
    sys.path.insert(0, str(P))
    import pins  # noqa: E402
    assert set(rid) - {"probe_error"} == set(pins.NEGATIVE_IDENTITY_KEYS), (
        f"identity keys mismatch: got={set(rid) - {'probe_error'}}, "
        f"pins={set(pins.NEGATIVE_IDENTITY_KEYS)}"
    )
    agent_realpath = os.path.realpath(agent_path)
    expected_error = (
        f"FileNotFoundError: [Errno 2] No such file or directory: '{agent_realpath}'"
    )
    assert rid["probe_error"] == expected_error, (
        f"probe_error {rid['probe_error']!r} != {expected_error!r}"
    )
    assert rid["agent_entrypoint_sha256"] is None
    # The REAL checker must report the producer error, never 'env.json absent'
    r2 = subprocess.run(
        [sys.executable, str(CHECK_INIT), "request", str(framedir)],
        capture_output=True, text=True, timeout=30,
    )
    assert r2.returncode == 1
    first_line = r2.stdout.splitlines()[0]
    assert first_line == (
        f"failure_reason: negative: probe reported an error: "
        f"FileNotFoundError: [Errno 2] No such file or directory: '{agent_realpath}'"
    ), f"checker line: {first_line!r}"


def test_probe_broken_pipe_post_loop_placement(tmp_path, agent_result):
    """N5e-F2/N8: the post-loop sample block MUST sit inside 'if c2a_delivered:'.
    Dedenting it (mutant N8) overwrites the BrokenPipe probe_error with the
    interpreter-sample error when both the early retry loop and the in-loop
    sample are defeated.  This test patches readlink to fail everywhere AND
    forces BrokenPipe on stdin.write — the only remaining sample path is the
    post-loop block, which runs only if c2a_delivered is True (i.e. it stays
    skipped on the not-delivered path)."""
    framedir = tmp_path / "capture"
    framedir.mkdir()
    env = {
        "S0_01_AGENT": agent_result,
        "S0_01_FRAMEDIR": str(framedir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "5",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }

    wrapper = tmp_path / "n8_wrapper.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, unittest.mock, subprocess as _sub
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        _orig_readlink = os.readlink
        def _always_fail_readlink(path):
            if "/proc/" in str(path) and "/exe" in str(path):
                raise OSError("No such process")
            return _orig_readlink(path)

        _OrigPopen = _sub.Popen
        class _PatchedPopen(_OrigPopen):
            def __new__(cls, *a, **kw):
                return _OrigPopen.__new__(cls)
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                def _raise_broken(*args, **kwargs):
                    raise BrokenPipeError("simulated broken pipe")
                self.stdin.write = _raise_broken

        with unittest.mock.patch.object(os, 'readlink', _always_fail_readlink), \\
             unittest.mock.patch.object(_sub, 'Popen', _PatchedPopen):
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
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    # The BrokenPipe error must NOT be overwritten by an interpreter-sample error
    assert rid["probe_error"] == "BrokenPipeError: agent process exited before c2a write landed", (
        f"expected BrokenPipe probe_error (post-loop block skipped), got {rid['probe_error']!r}"
    )
    assert rid["agent_interpreter_realpath"] is None
    assert rid["agent_interpreter_sha256"] is None


def test_probe_early_retry_recovers_from_transient_readlink_failure(tmp_path, agent_result):
    """N5e-F1/AP-F1a: readlink patched to fail the first 3 calls, then succeed.
    The retry loop recovers; a single-shot AP-F1a sample does not.  Assert the
    interpreter IS sampled and no probe_error from the interpreter path.
    N5h (AF-AP-57 class): "transient" IS defined by a count, so the count stays —
    but the fake now gates on the ARGUMENT (a read of /proc/self/exe returns a
    sentinel instead of consuming a failure) and PRINTS its mechanism, which the
    test asserts: without RL_CALLS a shape change that adds an earlier
    /proc/<pid>/exe read would eat the three failures and leave the retry loop
    completely untested while the test stayed green."""
    framedir = tmp_path / "capture"
    framedir.mkdir()
    env = {
        "S0_01_AGENT": agent_result,
        "S0_01_FRAMEDIR": str(framedir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "5",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }

    wrapper = tmp_path / "apf1a_wrapper.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        _orig_readlink = os.readlink
        _rl_calls = [0]
        def _transient_fail_readlink(path):
            if "/proc/self/exe" in str(path):
                return "/SELF/should-never-be-sampled"
            if "/proc/" in str(path) and "/exe" in str(path):
                _rl_calls[0] += 1
                if _rl_calls[0] <= 3:
                    raise OSError("transient failure")
            return _orig_readlink(path)

        with unittest.mock.patch.object(os, 'readlink', _transient_fail_readlink):
            try:
                acp_probe.main()
            except SystemExit as e:
                _rc = e.code
            else:
                _rc = 0
            # the mechanism, asserted by the test: 3 failing attempts + the 4th
            # (successful) early attempt + the one a2c-triggered late sample.
            print(f"RL_CALLS={{_rl_calls[0]}}", flush=True)
            sys.exit(_rc)
    """))

    r = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 0, f"expected exit 0 (retry recovered), got {r.returncode}: {r.stderr}"
    assert "RL_CALLS=5" in r.stdout.splitlines(), (
        f"expected 5 child /proc/<pid>/exe reads (3 transient failures, the recovering "
        f"attempt, the late sample); got {r.stdout!r}"
    )
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_interpreter_realpath"] is not None, (
        "retry loop failed to recover from transient readlink failures"
    )
    assert rid["agent_interpreter_sha256"] is not None
    assert "probe_error" not in rid


# ---- N5f-F1: the later reading wins ----


def test_probe_interpreter_is_the_final_exec_not_a_wrapper(tmp_path):
    """N5f-F1: a #!/bin/sh wrapper doing sleep 0.05 then exec python real_agent.py.
    The probe must record the PYTHON interpreter (the final exec stage), not the
    shell wrapper.  rc 0, no probe_error."""
    real_agent = tmp_path / "real_agent.py"
    real_agent.write_text(textwrap.dedent("""\
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
                        "agentInfo": {"name": "wrapper-test", "version": "0.0.1"},
                        "agentCapabilities": {},
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\\n")
                sys.stdout.flush()
            break
        sys.stdin.read()
    """))
    wrapper = tmp_path / "wrapper_agent.sh"
    wrapper.write_text(
        "#!/bin/sh\nsleep 0.05\n"
        f'exec "{sys.executable}" "{real_agent}"\n'
    )
    wrapper.chmod(0o755)
    r, framedir = _run_probe(tmp_path, str(wrapper), timeout_override=5)
    assert r.returncode == 0, f"probe failed: stderr={r.stderr}"
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    expected_interp = os.path.realpath(sys.executable)
    assert rid["agent_interpreter_realpath"] == expected_interp, (
        f"wrapper agent: interpreter {rid['agent_interpreter_realpath']!r} != "
        f"expected python {expected_interp!r}"
    )
    import hashlib
    expected_sha = hashlib.sha256(Path(expected_interp).read_bytes()).hexdigest()
    assert rid["agent_interpreter_sha256"] == expected_sha
    assert "probe_error" not in rid


def test_probe_env_shebang_interpreter_is_constant(tmp_path):
    """N5f-F1: #!/usr/bin/env python3 agent, 12 runs → exactly one distinct
    (realpath, sha256) pair equal to python's, and never /usr/bin/env."""
    import shutil
    agent = tmp_path / "env_agent.py"
    agent.write_text("#!/usr/bin/env python3\n" + textwrap.dedent("""\
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
                        "agentInfo": {"name": "env-agent", "version": "0.0.1"},
                        "agentCapabilities": {},
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\\n")
                sys.stdout.flush()
            break
        sys.stdin.read()
    """))
    agent.chmod(0o755)
    python_realpath = os.path.realpath(shutil.which("python3"))
    import hashlib
    python_sha = hashlib.sha256(Path(python_realpath).read_bytes()).hexdigest()
    pairs = set()
    for i in range(12):
        framedir = tmp_path / f"env_cap_{i}"
        framedir.mkdir()
        env = {
            "S0_01_AGENT": str(agent),
            "S0_01_FRAMEDIR": str(framedir),
            "PYTHONDONTWRITEBYTECODE": "1",
            "ACP_PROBE_TIMEOUT": "5",
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
        }
        r = subprocess.run(
            [sys.executable, str(PROBE)],
            capture_output=True, text=True, timeout=30, env=env,
        )
        assert r.returncode == 0, r.stderr
        rid = json.loads((framedir / "runtime-identity.json").read_text())
        assert "probe_error" not in rid
        pairs.add((rid["agent_interpreter_realpath"], rid["agent_interpreter_sha256"]))
    assert len(pairs) == 1, (
        f"env-shebang agent gave {len(pairs)} distinct interpreter pairs "
        f"across 12 runs: {pairs}"
    )
    sole = pairs.pop()
    assert sole == (python_realpath, python_sha), (
        f"expected ({python_realpath!r}, {python_sha!r}), got {sole}"
    )
    env_realpath = os.path.realpath("/usr/bin/env")
    assert sole[0] != env_realpath, (
        f"interpreter should never be /usr/bin/env, got {sole[0]!r}"
    )


# ---- N5f-F4: early sample loop bound is pinned ----


def test_probe_early_sample_loop_bound_is_pinned(tmp_path, agent_result):
    """N5f-F4: the early sample loop attempts exactly ceil(0.2/0.002)+1 = 101
    readlinks when every readlink fails.  Uses a fake clock that advances
    only in sleep (no wall-clock timing)."""
    framedir = tmp_path / "capture"
    framedir.mkdir()
    env = {
        "S0_01_AGENT": agent_result,
        "S0_01_FRAMEDIR": str(framedir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "5",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }

    wrapper = tmp_path / "f4_wrapper.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        # Fake clock: monotonic_ns driven by an integer-microsecond counter
        # that advances ONLY in sleep.
        _clock_us = [0]
        _post_deadline = [False]
        _dl = acp_probe._EARLY_SAMPLE_DEADLINE_S
        class _FakeClock:
            def monotonic(self):
                v = _clock_us[0] / 1_000_000.0
                if v >= _dl:
                    _post_deadline[0] = True
                return v
            def monotonic_ns(self):
                return _clock_us[0] * 1000
            def sleep(self, seconds):
                _clock_us[0] += int(seconds * 1_000_000)
        _fake = _FakeClock()

        _orig_readlink = os.readlink
        _early_readlink_count = [0]
        def _always_fail_readlink(path):
            if "/proc/" in str(path) and "/exe" in str(path):
                if not _post_deadline[0]:
                    _early_readlink_count[0] += 1
                raise OSError("No such process")
            return _orig_readlink(path)

        with unittest.mock.patch.object(acp_probe, 'time', _fake), \\
             unittest.mock.patch.object(os, 'readlink', _always_fail_readlink):
            try:
                acp_probe.main()
            except SystemExit as e:
                pass
        # Print the EARLY readlink attempt count for the test to read
        print(f"READLINK_COUNT={{_early_readlink_count[0]}}")
    """))

    r = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    # Extract readlink count from stdout
    count_line = [l for l in r.stdout.splitlines() if l.startswith("READLINK_COUNT=")]
    assert count_line, f"no READLINK_COUNT in stdout: {r.stdout!r}"
    count = int(count_line[0].split("=")[1])
    assert count == 101, (
        f"early sample loop attempted {count} readlinks, expected 101 "
        f"(ceil(0.2/0.002) + 1)"
    )
    # N5g-F3: pin the absolute values, not just the ratio
    import importlib
    sys.path.insert(0, str(P / "tools"))
    import acp_probe as _ap
    importlib.reload(_ap)
    assert _ap._EARLY_SAMPLE_DEADLINE_S == 0.2
    assert _ap._EARLY_SAMPLE_STEP_S == 0.002


# ---- N5f-LATE-NOCLEAR: early interpreter-sample-failed error cleared on late success ----


def test_probe_late_sample_clears_early_interpreter_error(tmp_path, agent_result):
    """LATE-NOCLEAR mutant killer: sha256 patched to fail during the early
    loop (readlink succeeds, sha256 raises → probe_error set to
    'interpreter sample failed: ...'), but sha256 succeeds at the late
    a2c-triggered sample.  The late success must CLEAR the early error:
    'probe_error' not in rid, rc 0.
    N5h-#4.1/9.3 (AF-AP-57): the fake no longer gates on the call ORDINAL
    (`_sha_call[0] == 1`) — under that gate the sweep's R10a mutant (the gate moved
    to `== 99`, so the early sha NEVER fails) left the test green: `assert
    "probe_error" not in rid` is trivially true when nothing failed.  The fake now
    gates on the ARGUMENT (the child interpreter's path) plus a fired-flag, writes a
    SENTINEL naming the path it failed on, and the test asserts that sentinel BEFORE
    the negation — a fake that never fires is now a red test, not a green one."""
    framedir = tmp_path / "capture"
    framedir.mkdir()
    sentinel = tmp_path / "early_sha_failed_on.txt"
    env = {
        "S0_01_AGENT": agent_result,
        "S0_01_FRAMEDIR": str(framedir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "5",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }

    wrapper = tmp_path / "late_noclear_wrapper.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        # The agent's shebang is this same interpreter, so /proc/<child>/exe resolves
        # here: the ARGUMENT that identifies an interpreter sample (never the probe's
        # own file, never the agent entrypoint — the other two _sha256_file receivers).
        _interp_path = os.path.realpath(sys.executable)
        _orig_sha256 = acp_probe._sha256_file
        _fired = [False]
        def _early_fail_sha256(path):
            if path == _interp_path and not _fired[0]:
                _fired[0] = True
                with open({str(sentinel)!r}, "w") as _s:
                    _s.write(path)
                raise OSError("early sha failure")
            return _orig_sha256(path)

        with unittest.mock.patch.object(acp_probe, '_sha256_file', _early_fail_sha256):
            try:
                acp_probe.main()
            except SystemExit as e:
                sys.exit(e.code)
    """))

    r = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    # POSITIVE CONTROL FIRST: the early error was really set, on the interpreter path.
    assert sentinel.exists(), (
        "the early sha256 failure never fired — the test would assert the absence of "
        "a probe_error that was never set (AF-AP-57 vacuity)"
    )
    assert sentinel.read_text() == os.path.realpath(sys.executable), (
        f"the fake failed on {sentinel.read_text()!r}, not the child interpreter"
    )
    assert r.returncode == 0, f"expected exit 0, got {r.returncode}: {r.stderr}"
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert "probe_error" not in rid, (
        f"early 'interpreter sample failed' error not cleared on late success: "
        f"{rid.get('probe_error')!r}"
    )
    assert rid["agent_interpreter_realpath"] is not None
    assert rid["agent_interpreter_sha256"] is not None


# ---- N5f-F6: M3 handler writes complete evidence ----


def test_probe_m3_handler_writes_complete_evidence(tmp_path, agent_result):
    """N5f-F6: the M3 crash path (exception inside the wrapped body) writes
    all four files with all 11 identity keys + probe_error.  Simulated by
    patching _write_evidence to raise RuntimeError('boom')."""
    framedir = tmp_path / "capture"
    framedir.mkdir()
    env = {
        "S0_01_AGENT": agent_result,
        "S0_01_FRAMEDIR": str(framedir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "5",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }

    wrapper = tmp_path / "m3_wrapper.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        _orig_write = acp_probe._write_evidence
        def _raise_boom(*a, **kw):
            raise RuntimeError("boom")

        with unittest.mock.patch.object(acp_probe, '_write_evidence', _raise_boom):
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
    assert r.stderr.strip() == "acp_probe: RuntimeError: boom"
    # All four files must exist
    for name in ("runtime-identity.json", "env.json", "timeline.jsonl", "agent-stderr.txt"):
        assert (framedir / name).exists(), f"{name} absent after M3 crash"
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["probe_error"] == "RuntimeError: boom"
    # N5g-F9: identity key set derived from pins
    sys.path.insert(0, str(P))
    import pins  # noqa: E402
    assert set(rid) - {"probe_error"} == set(pins.NEGATIVE_IDENTITY_KEYS), (
        f"M3 identity keys mismatch: got={set(rid) - {'probe_error'}}, "
        f"pins={set(pins.NEGATIVE_IDENTITY_KEYS)}"
    )


# ---- N5g-F1: late readlink failure keeps the early reading ----


def test_probe_late_readlink_failure_keeps_the_early_reading(tmp_path, agent_result):
    """N5g-F1 LATE-NULL killer: /proc/<child>/exe succeeds in the early loop and
    raises OSError at every later sample.  Agent = the answering fixture.
    The early reading must survive: interp non-null, sha non-null, no
    probe_error, rc 0.  Red on LATE-NULL (rc 1, interp None, probe_error
    'interpreter sample failed: No such process').
    N5h (AF-AP-57 class): the selector is the PHASE, not the ordinal it used to be
    (`_call_count[0] >= 2`) — the early loop runs with the main thread alone, every
    later sample runs with the stderr drain thread alive (the same gate the
    DL-INLINE killer uses).  An extra readlink anywhere no longer shifts which
    call fails, and RL_CALLS pins the mechanism."""
    framedir = tmp_path / "capture"
    framedir.mkdir()
    env = {
        "S0_01_AGENT": agent_result,
        "S0_01_FRAMEDIR": str(framedir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "5",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }

    wrapper = tmp_path / "f1_late_null_wrapper.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, threading, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        _orig_readlink = os.readlink
        _rl_calls = [0]
        def _phase_gated_readlink(path):
            if "/proc/self/exe" in str(path):
                return "/SELF/should-never-be-sampled"
            if "/proc/" in str(path) and "/exe" in str(path):
                _rl_calls[0] += 1
                # PHASE gate: the early loop runs before the stderr drain thread
                # starts; every later sample runs with that thread alive.
                if threading.active_count() > 1:
                    raise OSError("No such process")
            return _orig_readlink(path)

        with unittest.mock.patch.object(os, 'readlink', _phase_gated_readlink):
            try:
                acp_probe.main()
            except SystemExit as e:
                _rc = e.code
            else:
                _rc = 0
            print(f"RL_CALLS={{_rl_calls[0]}}", flush=True)
            sys.exit(_rc)
    """))

    r = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert "RL_CALLS=2" in r.stdout.splitlines(), (
        f"expected 2 child /proc/<pid>/exe reads (early success, late failure); "
        f"got {r.stdout!r}"
    )
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    # keeps the early reading — a wrong early reading fails the pinned
    # interpreter checks downstream; pinned by test_probe_late_readlink_failure_keeps_the_early_reading
    assert rid["agent_interpreter_realpath"] == os.path.realpath(sys.executable)
    assert rid["agent_interpreter_sha256"] is not None
    assert "probe_error" not in rid
    assert r.returncode == 0, f"expected rc 0, got {r.returncode}: stderr={r.stderr}"


# ---- N5g-F2: early site self-sampling — silent bash agent ----


def test_probe_interpreter_is_child_not_self_for_a_silent_agent(tmp_path):
    """N5g-F2 LG2-EARLY killer: a #!/bin/bash agent that reads one line and
    never writes stdout (ACP_PROBE_TIMEOUT=2).  The early loop determines
    identity.  Must record bash, not the probe's own python.
    Red on LG2-EARLY (records python)."""
    agent = tmp_path / "silent_bash_agent.sh"
    agent.write_text(
        '#!/bin/bash\n'
        'read line\n'
        'sleep 3\n'
    )
    agent.chmod(0o755)
    r, framedir = _run_probe(tmp_path, str(agent), timeout_override=2)
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    # Must NOT be the probe's own interpreter
    assert rid["agent_interpreter_realpath"] != os.readlink(
        f"/proc/{os.getpid()}/exe"
    ), (
        f"silent bash agent recorded the probe's own python "
        f"{rid['agent_interpreter_realpath']!r}"
    )
    assert os.path.basename(rid["agent_interpreter_realpath"]) == "bash"


# ---- N5g-F6: interpreter sampled once at the first a2c byte ----


def test_probe_interpreter_is_sampled_once_at_the_first_a2c_byte(tmp_path):
    """N5g-F6 LATE-EVERY killer: agent writes a notification FIRST (triggers
    the late sample but not found_response), then after 0.2 s writes the
    response with id:0.  os.readlink patched to return a distinct sentinel
    from call 3 on.  With the once-gate (HEAD), only the notification's
    chunk fires the late sample (call 2, real path recorded).  With
    LATE-EVERY, the response's chunk fires a SECOND late sample (call 3,
    sentinel recorded — the test fails).
    Red on LATE-EVERY (re-sample on every chunk picks the sentinel)."""
    # Agent that writes a notification, delays, then the response
    agent = tmp_path / "two_chunk_agent.py"
    agent.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
        import json, sys, time
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            if msg.get("method") == "initialize":
                # Notification first (no id, no found_response)
                notif = {"jsonrpc": "2.0", "method": "log", "params": {"message": "extra"}}
                sys.stdout.write(json.dumps(notif) + "\\n")
                sys.stdout.flush()
                # Delay so the probe consumes the first chunk before the second
                time.sleep(0.2)
                # Response second (with LATE-EVERY this triggers re-sample)
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg["id"],
                    "result": {
                        "protocolVersion": 1,
                        "agentCapabilities": {},
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\\n")
                sys.stdout.flush()
            break
        sys.stdin.read()
    """))
    agent.chmod(0o755)

    framedir = tmp_path / "capture"
    framedir.mkdir()
    env = {
        "S0_01_AGENT": str(agent),
        "S0_01_FRAMEDIR": str(framedir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "5",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }

    wrapper = tmp_path / "f6_once_wrapper.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, threading, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        # N5h (AF-AP-57 class): PHASE + a fired-flag, not the call ordinals this fake
        # used (`== 1` early / `== 2` first-late / else sentinel).  An extra early
        # retry used to shift every ordinal and hand the sentinel to the FIRST late
        # sample; the state gate is immune to that.
        _orig_readlink = os.readlink
        _rl_calls = [0]
        _late1_value = [None]
        _sentinel = "/SENTINEL/should-never-be-recorded"
        def _phase_gated_readlink(path):
            if "/proc/self/exe" in str(path):
                return "/SELF/should-never-be-sampled"
            if "/proc/" in str(path) and "/exe" in str(path):
                _rl_calls[0] += 1
                if threading.active_count() == 1:
                    # Early loop (drain thread not started) — succeed normally
                    return _orig_readlink(path)
                if _late1_value[0] is None:
                    # FIRST late sample — record what we return
                    _late1_value[0] = _orig_readlink(path)
                    return _late1_value[0]
                # any FURTHER late sample (LATE-EVERY) — a distinguishable sentinel
                return _sentinel
            return _orig_readlink(path)

        with unittest.mock.patch.object(os, 'readlink', _phase_gated_readlink):
            try:
                acp_probe.main()
            except SystemExit as e:
                pass
        # Print the first-late-sample value and the mechanism for the outer test
        print(f"CALL2={{_late1_value[0]}}")
        print(f"RL_CALLS={{_rl_calls[0]}}")
    """))

    r = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    # sampled once, at the first a2c byte: the stage that wrote the first
    # protocol byte is the interpreter of record; an agent that execs later
    # is recorded as the stage that spoke first
    call2_line = [l for l in r.stdout.splitlines() if l.startswith("CALL2=")]
    assert call2_line, f"no CALL2 in stdout: {r.stdout!r}"
    call2_val = call2_line[0].split("=", 1)[1]
    assert "RL_CALLS=2" in r.stdout.splitlines(), (
        f"expected exactly 2 child /proc/<pid>/exe reads (early loop + ONE late "
        f"sample); a third read is the LATE-EVERY shape: {r.stdout!r}"
    )
    assert rid["agent_interpreter_realpath"] == call2_val, (
        f"recorded {rid['agent_interpreter_realpath']!r} != call-2 value {call2_val!r}"
    )
    assert rid["agent_interpreter_realpath"] != "/SENTINEL/should-never-be-recorded"


# ---- N5g-F8: interpreter deleted after start is a loud probe error ----


def test_probe_interpreter_deleted_after_start_is_a_loud_probe_error(tmp_path):
    """N5g-F8 shape N: agent whose shebang interpreter (a private COPY of the
    system shell — `/bin/sh` resolved, dash on Debian, bash on Fedora; never a
    distro-specific path, AF-AP-4) is unlinked after Popen, then the agent
    closes stdout and sleeps.  rc 1, realpath ends with ' (deleted)', sha256 None,
    probe_error carries the exact FileNotFoundError.
    Uses an in-process wrapper to delete the copied interpreter before the
    first readlink — deterministic, no race."""
    import shutil
    # A private copy of the system shell in tmp_path (a copy, not a hardlink: /tmp is
    # tmpfs on the PC, and /bin/dash does not exist there — the first PC gate of 8k was red)
    myshell = tmp_path / "myshell"
    shutil.copy2(os.path.realpath("/bin/sh"), str(myshell))
    myshell.chmod(0o755)
    myshell_path = str(myshell)

    agent = tmp_path / "agent_close_stdout.sh"
    # Agent closes stdout and sleeps (the interpreter is deleted externally)
    agent.write_text(
        f'#!{myshell_path}\n'
        'exec 1>&-\n'
        'sleep 5\n'
    )
    agent.chmod(0o755)

    framedir = tmp_path / "capture"
    framedir.mkdir()
    env = {
        "S0_01_AGENT": str(agent),
        "S0_01_FRAMEDIR": str(framedir),
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "2",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }

    wrapper = tmp_path / "f8_wrapper.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        _orig_readlink = os.readlink
        _deleted = [False]
        def _deleting_readlink(path):
            if "/proc/" in str(path) and "/exe" in str(path) and not _deleted[0]:
                # Delete the copied interpreter before the first readlink fires,
                # so /proc/<pid>/exe returns 'myshell (deleted)'
                _deleted[0] = True
                try:
                    os.unlink({myshell_path!r})
                except FileNotFoundError:
                    pass
            return _orig_readlink(path)

        with unittest.mock.patch.object(os, 'readlink', _deleting_readlink):
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
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_interpreter_realpath"].endswith(" (deleted)"), (
        f"expected realpath ending ' (deleted)', got {rid['agent_interpreter_realpath']!r}"
    )
    assert rid["agent_interpreter_sha256"] is None
    expected_error = (
        f"interpreter sample failed: [Errno 2] No such file or directory: "
        f"'{myshell_path} (deleted)'"
    )
    assert rid["probe_error"] == expected_error, (
        f"probe_error {rid['probe_error']!r} != {expected_error!r}"
    )


# ================= N5h: the sweep's six production rows, closed as classes =================
#
# Every test below carries the run that proved the defect on the PIN (2823f05) in its
# docstring, and a positive control so the assertion cannot pass vacuously.


def _probe_tree_copy(tmp_path):
    """A private copy of proofs/S0-01/{tools/acp_probe.py, fixtures/} under tmp_path.

    The probe derives its fixture path from its OWN location, so a test that needs a
    non-regular file at that path must run a copy — the repo tree is never touched."""
    import shutil
    root = tmp_path / "S0-01"
    (root / "tools").mkdir(parents=True)
    (root / "fixtures").mkdir()
    shutil.copy2(str(PROBE), str(root / "tools" / "acp_probe.py"))
    shutil.copy2(str(P / "fixtures" / "neg-malformed-initialize.json"),
                 str(root / "fixtures" / "neg-malformed-initialize.json"))
    return root


# ---- N5h-#7: the fixture read cannot hang (AF-AP-30 class, probe side) ----

def test_probe_refuses_a_non_regular_fixture(tmp_path, agent_result):
    """N5h-#7 (SWEEP-prod row 7).  os.path.exists() is True for a FIFO and open()
    then blocks forever: on the PIN this run was rc 124 under `timeout 20` (20.01 s,
    the sweep's measurement, reproduced this round).  os.stat + S_ISREG exits 64
    immediately.  Positive control: the SAME copied tree with the real fixture exits
    0, so the 64 is the guard firing and not a broken rig.  The subprocess timeout of
    5 s is the bound — a regression hangs and fails here, it cannot pass."""
    tree = _probe_tree_copy(tmp_path)
    probe = tree / "tools" / "acp_probe.py"
    fixture = tree / "fixtures" / "neg-malformed-initialize.json"

    base_env = {
        "S0_01_AGENT": agent_result,
        "PYTHONDONTWRITEBYTECODE": "1",
        "ACP_PROBE_TIMEOUT": "5",
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
    }

    # POSITIVE CONTROL: the copied tree with a REGULAR fixture runs to completion
    ok_dir = tmp_path / "ok"
    ok_dir.mkdir()
    r_ok = subprocess.run(
        [sys.executable, str(probe)], capture_output=True, text=True, timeout=30,
        env=dict(base_env, S0_01_FRAMEDIR=str(ok_dir)),
    )
    assert r_ok.returncode == 0, f"rig broken: {r_ok.returncode}: {r_ok.stderr}"

    fixture.unlink()
    os.mkfifo(str(fixture))
    fifo_dir = tmp_path / "fifo"
    fifo_dir.mkdir()
    r = subprocess.run(
        [sys.executable, str(probe)], capture_output=True, text=True, timeout=5,
        env=dict(base_env, S0_01_FRAMEDIR=str(fifo_dir)),
    )
    assert r.returncode == 64, f"expected exit 64, got {r.returncode}: {r.stderr}"
    assert r.stderr.strip() == f"acp_probe: fixture is not a regular file: {fixture}"


def test_sha256_file_refuses_a_non_regular_file(tmp_path):
    """N5h-#7 (the CLASS): _sha256_file is the shared read receiver for all three
    remaining reads — the probe's own file, the agent entrypoint, the child's
    interpreter.  open() on a FIFO blocks forever and /dev/zero never reaches EOF,
    so the guard lives in the receiver.  Driven in a CHILD under a hard timeout: a
    regression hangs the child and fails the test instead of wedging the suite.
    Positive control: the same call over a REGULAR file returns the real digest."""
    import hashlib
    fifo = tmp_path / "a_fifo"
    os.mkfifo(str(fifo))
    regular = tmp_path / "a_regular"
    regular.write_bytes(b"n5h")

    driver = tmp_path / "sha_driver.py"
    driver.write_text(textwrap.dedent(f"""\
        import sys
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe
        print("REGULAR=" + acp_probe._sha256_file({str(regular)!r}))
        try:
            acp_probe._sha256_file({str(fifo)!r})
        except OSError as exc:
            print("FIFO=" + str(exc))
        else:
            print("FIFO=<NO ERROR: the FIFO was read>")
    """))
    r = subprocess.run(
        [sys.executable, str(driver)], capture_output=True, text=True, timeout=5,
    )
    assert r.returncode == 0, f"driver failed: {r.stderr}"
    assert f"REGULAR={hashlib.sha256(b'n5h').hexdigest()}" in r.stdout.splitlines()
    assert f"FIFO=not a regular file: {fifo}" in r.stdout.splitlines(), r.stdout


# ---- N5h-#10: the stderr drain failure is recorded, not swallowed ----

def test_probe_reports_a_stderr_drain_failure(tmp_path, agent_result):
    """N5h-#10 (SWEEP-prod row 10).  A directory at agent-stderr.txt makes the drain
    thread's open() raise; `except Exception: pass` killed the thread silently and
    the probe still exited 0 with NO probe_error (the PIN run, reproduced this
    round).  Now: rc 1 and probe_error naming the exception class and the path.
    NEGATIVE CONTROL: the same agent with a writable stderr path exits 0 with no
    probe_error — the drain error is not being invented on every run."""
    framedir = tmp_path / "capture"
    framedir.mkdir()
    (framedir / "agent-stderr.txt").mkdir()
    r, _ = _run_probe(tmp_path, agent_result, timeout_override=5)
    assert r.returncode == 1, f"expected exit 1, got {r.returncode}: {r.stderr}"
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    expected = (
        f"stderr drain failed: IsADirectoryError: [Errno 21] Is a directory: "
        f"'{framedir / 'agent-stderr.txt'}'"
    )
    assert rid["probe_error"] == expected, f"got {rid.get('probe_error')!r}"

    control = tmp_path / "control"
    control.mkdir()
    r_ok, _ = _run_probe(tmp_path, agent_result, timeout_override=5,
                         extra_env={"S0_01_FRAMEDIR": str(control)})
    assert r_ok.returncode == 0, f"control run failed: {r_ok.stderr}"
    assert "probe_error" not in json.loads((control / "runtime-identity.json").read_text())


# ---- N5h-#23: a lossy decode keeps the lossless copy ----

_LOSSY_A2C_LINE = (
    b'{"jsonrpc":"2.0","id":0,"error":{"code":-32602,'
    b'"message":"Invalid par\xffams"}}\n'
)


def test_probe_keeps_raw_b64_when_a_byte_was_replaced(tmp_path):
    """N5h-#23 (SWEEP-prod row 23).  decode(errors="replace") rewrites the agent's
    bytes: on the PIN the negative leg's only record of the pinned agent's rejection
    was "Invalid par�ams" with raw_b64 ABSENT — the exact bytes were gone.  The
    entry now also carries raw_b64, which must decode to the bytes the agent wrote.
    The parsed frame is kept so response detection still fires (id 0 → no timeout)."""
    agent = tmp_path / "agent_lossy_byte.py"
    agent.write_text(f"#!{sys.executable}\n" + textwrap.dedent("""\
        import sys
        sys.stdin.readline()
        sys.stdout.buffer.write(%r)
        sys.stdout.buffer.flush()
        sys.stdin.read()
    """) % _LOSSY_A2C_LINE)
    agent.chmod(0o755)

    r, framedir = _run_probe(tmp_path, str(agent), timeout_override=5)
    assert r.returncode == 0, f"probe failed: {r.stderr}"
    entries = [json.loads(line) for line in
               (framedir / "timeline.jsonl").read_text().splitlines() if line.strip()]
    a2c = [e for e in entries if e["dir"] == "a2c"]
    assert len(a2c) == 1, f"expected one a2c entry, got {len(a2c)}"
    entry = a2c[0]
    assert "raw_b64" in entry, (
        f"the lossless copy of a replaced-byte line is missing: {sorted(entry)}"
    )
    assert base64.b64decode(entry["raw_b64"]) == _LOSSY_A2C_LINE
    assert entry["frame"]["id"] == 0
    assert "�" in entry["frame"]["error"]["message"], (
        "the frame should still carry the replaced text — raw_b64 is the copy, not a swap"
    )


def test_probe_clean_utf8_line_carries_no_raw_b64(tmp_path, agent_result):
    """N5h-#23 NEGATIVE CONTROL: a line that decodes losslessly carries no raw_b64,
    so the key is evidence of a replaced byte and not decoration on every entry."""
    r, framedir = _run_probe(tmp_path, agent_result, timeout_override=5)
    assert r.returncode == 0, f"probe failed: {r.stderr}"
    entries = [json.loads(line) for line in
               (framedir / "timeline.jsonl").read_text().splitlines() if line.strip()]
    assert entries, "no timeline entries"
    for e in entries:
        assert "raw_b64" not in e, f"raw_b64 on a clean line: {e}"


# ---- N5h-#34: the mirror constant is pinned to pins.py ----

def test_probe_redaction_pattern_equals_the_pin():
    """N5h-#34 (SWEEP-prod row 34).  acp_probe._REDACTED_ENV_KEY_RE is a hand copy of
    pins.REDACTED_ENV_KEY_RE (the probe must stay import-free of pins on the PC), and
    on the PIN NO test pinned them equal — `grep -rn _REDACTED_ENV_KEY_RE tests/`
    returned nothing.  The TEST does the equality.  The second assertion is the
    negative control on the WRONG fix: making the probe import pins would satisfy the
    equality while breaking the PC constraint the comment claims."""
    import re as _re
    sys.path.insert(0, str(P))
    from pins import REDACTED_ENV_KEY_RE  # noqa: E402
    sys.path.insert(0, str(P / "tools"))
    import acp_probe  # noqa: E402

    assert acp_probe._REDACTED_ENV_KEY_RE.pattern == REDACTED_ENV_KEY_RE, (
        f"probe copy {acp_probe._REDACTED_ENV_KEY_RE.pattern!r} has drifted from "
        f"pins.REDACTED_ENV_KEY_RE {REDACTED_ENV_KEY_RE!r}"
    )
    assert not _re.search(r"^\s*(import|from)\s+pins\b", PROBE.read_text(), _re.M), (
        "the probe must not import pins — it runs from a bare tools/ directory on the PC"
    )


# ---- N5h-#39: the ACP_PROBE_TIMEOUT domain is closed ----

@pytest.mark.parametrize("raw,expected", [
    ("3_0", "is not a valid number: '3_0'"),
    (" 30 ", "is not a valid number: ' 30 '"),
    ("30s", "is not a valid number: '30s'"),
    ("0x10", "is not a valid number: '0x10'"),
    ("+30", "is not a valid number: '+30'"),
    ("1e3", "is not a valid number: '1e3'"),
    ("nan", "must be a finite float > 0, got 'nan'"),
    ("inf", "must be a finite float > 0, got 'inf'"),
    ("-5", "must be a finite float > 0, got '-5'"),
    ("0", "must be a finite float > 0, got '0'"),
    pytest.param("9" * 400, "must be a finite float > 0, got '%s'" % ("9" * 400),
                 id="digits400_overflows_to_inf"),
])
def test_probe_timeout_rejects_forms_outside_the_domain(tmp_path, agent_result, raw, expected):
    """N5h-#39 (SWEEP-prod row 39).  float() accepts far more than a timeout may be:
    on the PIN "3_0" and " 30 " were ACCEPTED as 30.0 (measured, rc 0).  The domain
    is now re.fullmatch(r"[0-9]+(\\.[0-9]+)?") BEFORE the conversion, so float()'s
    leniency is unreachable; isfinite still guards the FINAL value because a 400-digit
    string passes the regex and float()s to inf (found this round, not in the sweep).
    Both message classes are preserved exactly."""
    r, _ = _run_probe(tmp_path, agent_result, timeout_override=raw)
    assert r.returncode == 64, f"expected exit 64 for {raw!r}, got {r.returncode}"
    assert r.stderr.strip() == f"acp_probe: ACP_PROBE_TIMEOUT {expected}"


@pytest.mark.parametrize("raw", ["30", "5", "0.5", "5.25"])
def test_probe_timeout_accepts_the_domain(tmp_path, agent_result, raw):
    """N5h-#39 POSITIVE CONTROL: the gate rejects the class, not everything — a
    plain decimal is still accepted and the probe runs to a clean exit."""
    r, framedir = _run_probe(tmp_path, agent_result, timeout_override=raw)
    assert r.returncode == 0, f"{raw!r} rejected: {r.stderr}"
    assert "probe_error" not in json.loads((framedir / "runtime-identity.json").read_text())


# ---- N5h-#40: the bytecode flag is the runtime state, not a string mirror ----

@pytest.mark.parametrize("value", ["1", "2", "true", "0", "", None])
def test_identity_records_the_runtime_bytecode_state_not_the_string(tmp_path, agent_result, value):
    """N5h-#40 (SWEEP-prod row 40).  `os.environ.get(...) == "1"` was a mirror of the
    string, not the state: CPython also disables bytecode writing for "2" and "true",
    so the PIN recorded python_dont_write_bytecode=false while writing WAS disabled
    (measured both ways this round).  The oracle here is CPython itself — a child
    interpreter started with the SAME environment reports its own
    sys.dont_write_bytecode — never a hardcoded expectation."""
    env = os.environ.copy()
    env["S0_01_AGENT"] = agent_result
    env["S0_01_FRAMEDIR"] = str(tmp_path / "capture")
    env["ACP_PROBE_TIMEOUT"] = "5"
    if value is None:
        env.pop("PYTHONDONTWRITEBYTECODE", None)
    else:
        env["PYTHONDONTWRITEBYTECODE"] = value
    (tmp_path / "capture").mkdir()

    oracle = subprocess.run(
        [sys.executable, "-c", "import sys; print(sys.dont_write_bytecode)"],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert oracle.returncode == 0, oracle.stderr
    expected = {"True": True, "False": False}[oracle.stdout.strip()]

    r = subprocess.run(
        [sys.executable, str(PROBE)], capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 0, f"probe failed: {r.stderr}"
    rid = json.loads((tmp_path / "capture" / "runtime-identity.json").read_text())
    assert rid["python_dont_write_bytecode"] is expected, (
        f"PYTHONDONTWRITEBYTECODE={value!r}: recorded "
        f"{rid['python_dont_write_bytecode']!r}, CPython reports {expected!r}"
    )
