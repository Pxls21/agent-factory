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
    defeating the early retry loop (readlink fails for 0.3 s) and using a
    silent agent (no a2c data, so the in-loop sample never fires).  After the
    a2c timeout the post-loop readlink succeeds but sha256 fails."""
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
        import sys, os, time, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        _orig_readlink = os.readlink
        _start = time.monotonic()
        _fake_path = "/tmp/fake_interp (deleted)"

        def _gated_readlink(path):
            if "/proc/" in str(path) and "/exe" in str(path):
                if time.monotonic() - _start < 0.3:
                    raise OSError("No such process")
                return _fake_path
            return _orig_readlink(path)

        _orig_sha256 = acp_probe._sha256_file
        def _gated_sha256(path):
            if path == _fake_path:
                raise FileNotFoundError(2, "No such file or directory", path)
            return _orig_sha256(path)

        with unittest.mock.patch.object(os, 'readlink', _gated_readlink), \\
             unittest.mock.patch.object(acp_probe, '_sha256_file', _gated_sha256):
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
    interpreter IS sampled and no probe_error from the interpreter path."""
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
        _call_count = [0]
        def _transient_fail_readlink(path):
            if "/proc/" in str(path) and "/exe" in str(path):
                _call_count[0] += 1
                if _call_count[0] <= 3:
                    raise OSError("transient failure")
            return _orig_readlink(path)

        with unittest.mock.patch.object(os, 'readlink', _transient_fail_readlink):
            try:
                acp_probe.main()
            except SystemExit as e:
                sys.exit(e.code)
    """))

    r = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode == 0, f"expected exit 0 (retry recovered), got {r.returncode}: {r.stderr}"
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
    The gate is _sha_call[0] == 1 alone — the early loop's sha is provably
    the first _sha256_file call (line 237 precedes 299, 372, 99, 106)."""
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

    wrapper = tmp_path / "late_noclear_wrapper.py"
    wrapper.write_text(textwrap.dedent(f"""\
        import sys, os, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        _orig_sha256 = acp_probe._sha256_file
        _sha_call = [0]
        def _early_fail_sha256(path):
            _sha_call[0] += 1
            # Fail on the first sha256 call (the early loop's sha)
            if _sha_call[0] == 1:
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
    """N5g-F1 LATE-NULL killer: os.readlink patched with a call counter —
    /proc/*/exe succeeds on call 1 (the early loop) and raises OSError from
    call 2 on (the late sample).  Agent = the answering fixture.
    The early reading must survive: interp non-null, sha non-null, no
    probe_error, rc 0.  Red on LATE-NULL (rc 1, interp None, probe_error
    'interpreter sample failed: No such process')."""
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
        import sys, os, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        _orig_readlink = os.readlink
        _call_count = [0]
        def _counted_readlink(path):
            if "/proc/" in str(path) and "/exe" in str(path):
                _call_count[0] += 1
                if _call_count[0] >= 2:
                    raise OSError("No such process")
            return _orig_readlink(path)

        with unittest.mock.patch.object(os, 'readlink', _counted_readlink):
            try:
                acp_probe.main()
            except SystemExit as e:
                sys.exit(e.code)
    """))

    r = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True, text=True, timeout=30, env=env,
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
        import sys, os, unittest.mock
        sys.path.insert(0, {str(P / "tools")!r})
        import acp_probe

        _orig_readlink = os.readlink
        _call_count = [0]
        _call2_value = [None]
        _sentinel = "/SENTINEL/should-never-be-recorded"
        def _counting_readlink(path):
            if "/proc/" in str(path) and "/exe" in str(path):
                _call_count[0] += 1
                if _call_count[0] == 1:
                    # Early loop — let it succeed normally
                    return _orig_readlink(path)
                elif _call_count[0] == 2:
                    # First late sample — record what we return
                    v = _orig_readlink(path)
                    _call2_value[0] = v
                    return v
                else:
                    # Later calls — return a distinguishable sentinel
                    return _sentinel
            return _orig_readlink(path)

        with unittest.mock.patch.object(os, 'readlink', _counting_readlink):
            try:
                acp_probe.main()
            except SystemExit as e:
                pass
        # Print the call-2 value for the outer test
        print(f"CALL2={{_call2_value[0]}}")
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
    assert rid["agent_interpreter_realpath"] == call2_val, (
        f"recorded {rid['agent_interpreter_realpath']!r} != call-2 value {call2_val!r}"
    )
    assert rid["agent_interpreter_realpath"] != "/SENTINEL/should-never-be-recorded"


# ---- N5g-F8: interpreter deleted after start is a loud probe error ----


def test_probe_interpreter_deleted_after_start_is_a_loud_probe_error(tmp_path):
    """N5g-F8 shape N: agent whose shebang interpreter (a hardlink of
    /bin/dash) is unlinked after Popen, then the agent closes stdout and
    sleeps.  rc 1, realpath ends with ' (deleted)', sha256 None,
    probe_error carries the exact FileNotFoundError.
    Uses an in-process wrapper to delete the hardlink before the first
    readlink — deterministic, no race."""
    import shutil
    # Create a hardlink to /bin/dash in tmp_path
    myshell = tmp_path / "myshell"
    shutil.copy2("/bin/dash", str(myshell))
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
                # Delete the hardlink before the first readlink fires,
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
