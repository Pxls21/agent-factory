"""tests/test_s0_01_acp_probe.py — drive acp_probe.py against a fake lenient agent,
then verify check_initialize.py on the captured directory.

The fake agent answers any initialize with protocolVersion 1 (lenient).
The probe sends the malformed fixture (no protocolVersion in the request).
check_initialize.py on the capture dir must exit 1 with the exact seed reason
and print an observed line.
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
def fake_agent(tmp_path):
    """A minimal ACP agent script that answers any initialize with protocolVersion 1."""
    script = tmp_path / "fake_agent.py"
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
            else:
                break
    """))
    script.chmod(0o755)
    return str(script)


def test_probe_captures_and_check_initialize_classifies(tmp_path, fake_agent):
    """Drive the probe against the fake agent, verify capture files,
    then run check_initialize.py on the capture dir."""
    framedir = tmp_path / "capture"
    framedir.mkdir()

    env = os.environ.copy()
    env["S0_01_AGENT"] = fake_agent
    env["S0_01_FRAMEDIR"] = str(framedir)

    # Run the probe
    r = subprocess.run(
        [sys.executable, str(PROBE)],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert r.returncode is not None, f"probe did not exit: stderr={r.stderr}"

    # Verify capture files exist
    assert (framedir / "timeline.jsonl").exists(), "timeline.jsonl not created"
    assert (framedir / "runtime-identity.json").exists(), "runtime-identity.json not created"

    # Parse timeline
    entries = [json.loads(l) for l in
               (framedir / "timeline.jsonl").read_text().splitlines() if l.strip()]
    assert len(entries) >= 1, "timeline has no entries"

    # First entry is c2a initialize
    assert entries[0]["dir"] == "c2a"
    assert entries[0]["frame"]["method"] == "initialize"
    assert entries[0]["seq"] == 1

    # The request params should match the malformed fixture (no protocolVersion)
    params = entries[0]["frame"]["params"]
    assert "protocolVersion" not in params

    # Second entry (if present) is a2c response
    if len(entries) >= 2:
        assert entries[1]["dir"] == "a2c"
        resp = entries[1]["frame"]
        assert resp.get("result", {}).get("protocolVersion") == 1

    # Runtime identity
    rid = json.loads((framedir / "runtime-identity.json").read_text())
    assert rid["agent_argv"] == [fake_agent]
    assert "spawned_at_utc" in rid

    # Now run check_initialize.py on the capture directory
    r2 = subprocess.run(
        [sys.executable, str(CHECK_INIT), "request", str(framedir)],
        capture_output=True, text=True, timeout=30,
    )
    assert r2.returncode == 1, f"expected exit 1, got {r2.returncode}: stdout={r2.stdout}"
    lines = r2.stdout.strip().splitlines()
    assert lines[0] == "protocol-violation: missing required initialize field"
    # observed line
    assert len(lines) >= 2
    assert lines[1].startswith("observed:")
    assert "accepted" in lines[1] or "error" in lines[1] or "none" in lines[1]


def test_check_initialize_directory_defers_when_absent(tmp_path):
    """check_initialize.py on a nonexistent directory exits 2 (deferred)."""
    r = subprocess.run(
        [sys.executable, str(CHECK_INIT), "request", str(tmp_path / "nonexistent")],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 2
    assert "deferred:" in r.stdout


def test_check_initialize_directory_defers_when_no_timeline(tmp_path):
    """check_initialize.py on a directory without timeline.jsonl exits 2."""
    d = tmp_path / "empty_dir"
    d.mkdir()
    r = subprocess.run(
        [sys.executable, str(CHECK_INIT), "request", str(d)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 2
    assert "deferred:" in r.stdout
