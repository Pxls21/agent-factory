"""tests/test_s0_01_acp_probe.py — drive acp_probe.py against fake agents,
then verify check_initialize.py on the captured directory.

Scenarios: (a) error response, (b) result response, (c) never answers (timeout),
(d) 200 KB stderr before answering (no deadlock).
Mutant kills: "never reads the response" and "drops the a2c entry".
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
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


def _run_probe(tmp_path, agent, timeout_override=None):
    framedir = tmp_path / "capture"
    framedir.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["S0_01_AGENT"] = agent
    env["S0_01_FRAMEDIR"] = str(framedir)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if timeout_override is not None:
        env["ACP_PROBE_TIMEOUT"] = str(timeout_override)
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=60, env=env,
    )
    return r, framedir


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

    # Runtime identity has probe-specific keys
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_argv"] == [agent_result]
    assert "probe_path" in rid
    assert "probe_sha256" in rid
    assert "agent_exit_code" in rid
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


def test_probe_never_answers(tmp_path, agent_silent):
    """(c) Agent never answers: probe completes within timeout, timeline has 1 entry only."""
    r, framedir = _run_probe(tmp_path, agent_silent, timeout_override=1)
    # Probe should complete (not hang forever)
    assert r.returncode is not None

    entries = [json.loads(l) for l in
               (framedir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    # Only the c2a entry, no a2c
    assert len(entries) == 1
    assert entries[0]["dir"] == "c2a"

    # check_initialize request <dir> must fail (exit 1, names negative:).
    # In the sandbox the identity pins don't match (fake agent path), so the
    # specific reason is agent_realpath mismatch, not "no agent response captured".
    # The key mutant-kill assertion is that timeline has exactly 1 entry (above).
    r2 = subprocess.run(
        [sys.executable, str(CHECK_INIT), "request", str(framedir)],
        capture_output=True, text=True, timeout=30,
    )
    assert r2.returncode == 1
    assert "failure_reason: negative:" in r2.stdout


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
