"""proofs/S0-01/tools/frame_tee.py v2 — stdio proxy with timeline, identity, directional files.

A fake agent (Python script written by the test) reads JSON-RPC lines and answers
initialize + one notification burst.  Driven through the real tee under sys.executable.

Asserts: timeline seq/ordering/dir, byte-identical relay, runtime-identity fields
(sha256 of the fake agent file), exit-code propagation, the non-JSON-line path,
and that the directional files equal the timeline split.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEE = ROOT / "proofs" / "S0-01" / "tools" / "frame_tee.py"

FAKE_AGENT_CODE = textwrap.dedent("""\
    import json, sys
    for line in sys.stdin:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
        except (json.JSONDecodeError, ValueError):
            sys.stdout.write("agent-echo-nonJSON\\n")
            sys.stdout.flush()
            continue
        method = obj.get("method", "")
        if method == "initialize":
            resp = {"jsonrpc": "2.0", "id": obj["id"],
                    "result": {"protocolVersion": "1"}}
            sys.stdout.write(json.dumps(resp, separators=(",", ":")) + "\\n")
            sys.stdout.flush()
        elif method == "notifications/burst":
            for i in range(3):
                n = {"jsonrpc": "2.0", "method": "agent_message_chunk",
                     "params": {"i": i}}
                sys.stdout.write(json.dumps(n, separators=(",", ":")) + "\\n")
                sys.stdout.flush()
    sys.exit(42)
""")


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _build_input():
    """Three client-to-agent lines: initialize, burst trigger, non-JSON."""
    lines = [
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                     "params": {}}, separators=(",", ":")) + "\n",
        json.dumps({"jsonrpc": "2.0", "method": "notifications/burst",
                     "params": {}}, separators=(",", ":")) + "\n",
        "this is not json\n",
    ]
    return "".join(lines).encode("utf-8")


@pytest.fixture(scope="module")
def tee_run(tmp_path_factory):
    """Run the tee once with a fake agent and return all artifacts."""
    tmpdir = tmp_path_factory.mktemp("tee")
    framedir = tmpdir / "frames"
    framedir.mkdir()

    agent_script = tmpdir / "fake_agent.py"
    agent_script.write_text("#!%s\n" % sys.executable + FAKE_AGENT_CODE)
    agent_script.chmod(0o755)

    env = os.environ.copy()
    env["S0_01_FRAMEDIR"] = str(framedir)
    env["S0_01_AGENT"] = str(agent_script)
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    input_bytes = _build_input()

    proc = subprocess.run(
        [sys.executable, str(TEE)],
        input=input_bytes,
        capture_output=True,
        env=env,
        timeout=30,
    )

    # Read artifacts
    timeline_lines = []
    tl_path = framedir / "timeline.jsonl"
    if tl_path.exists():
        for raw in tl_path.read_bytes().split(b"\n"):
            if raw.strip():
                timeline_lines.append(json.loads(raw))

    c2a_bytes = (framedir / "frames-client-to-agent.jsonl").read_bytes()
    a2c_bytes = (framedir / "frames-agent-to-client.jsonl").read_bytes()

    identity = {}
    id_path = framedir / "runtime-identity.json"
    if id_path.exists():
        identity = json.loads(id_path.read_text())

    return {
        "proc": proc,
        "timeline": timeline_lines,
        "c2a_bytes": c2a_bytes,
        "a2c_bytes": a2c_bytes,
        "identity": identity,
        "agent_script": agent_script,
        "framedir": framedir,
        "input_bytes": input_bytes,
        "stdout": proc.stdout,
    }


# ---------------------------------------------------------------------------
# Timeline: seq strictly increasing from 1, dir values valid
# ---------------------------------------------------------------------------
class TestTimeline:
    def test_seq_strictly_increasing(self, tee_run):
        tl = tee_run["timeline"]
        assert len(tl) > 0, "timeline is empty"
        for i, entry in enumerate(tl):
            assert entry["seq"] == i + 1, f"seq[{i}] = {entry['seq']}, expected {i+1}"

    def test_dir_values(self, tee_run):
        dirs = {e["dir"] for e in tee_run["timeline"]}
        assert dirs == {"c2a", "a2c"}, f"unexpected dir values: {dirs}"

    def test_has_t_utc_and_t_mono(self, tee_run):
        for e in tee_run["timeline"]:
            assert "t_utc" in e
            assert "t_mono_ns" in e
            assert isinstance(e["t_mono_ns"], int)
            assert e["t_utc"].endswith("Z")

    def test_t_mono_non_decreasing(self, tee_run):
        monos = [e["t_mono_ns"] for e in tee_run["timeline"]]
        for i in range(1, len(monos)):
            assert monos[i] >= monos[i - 1], f"t_mono decreased at {i}"

    def test_c2a_count(self, tee_run):
        c2a = [e for e in tee_run["timeline"] if e["dir"] == "c2a"]
        assert len(c2a) == 3, f"expected 3 c2a entries, got {len(c2a)}"

    def test_a2c_count(self, tee_run):
        a2c = [e for e in tee_run["timeline"] if e["dir"] == "a2c"]
        # 1 init response + 3 burst + 1 non-JSON echo = 5
        assert len(a2c) == 5, f"expected 5 a2c entries, got {len(a2c)}"


# ---------------------------------------------------------------------------
# Non-JSON line path
# ---------------------------------------------------------------------------
class TestNonJsonLine:
    def test_c2a_non_json(self, tee_run):
        """Client sent 'this is not json' — timeline should record frame=null, raw=string."""
        c2a = [e for e in tee_run["timeline"] if e["dir"] == "c2a"]
        non_json = [e for e in c2a if e["frame"] is None]
        assert len(non_json) >= 1, "no non-JSON c2a entry"
        assert non_json[0]["raw"] == "this is not json"

    def test_a2c_non_json(self, tee_run):
        """Agent replied 'agent-echo-nonJSON' — timeline should record frame=null, raw=string."""
        a2c = [e for e in tee_run["timeline"] if e["dir"] == "a2c"]
        non_json = [e for e in a2c if e["frame"] is None]
        assert len(non_json) >= 1, "no non-JSON a2c entry"
        assert non_json[0]["raw"] == "agent-echo-nonJSON"


# ---------------------------------------------------------------------------
# Byte-identical relay
# ---------------------------------------------------------------------------
class TestByteRelay:
    def test_c2a_relay(self, tee_run):
        """frames-client-to-agent.jsonl == input bytes."""
        assert tee_run["c2a_bytes"] == tee_run["input_bytes"]

    def test_a2c_relay(self, tee_run):
        """frames-agent-to-client.jsonl == tee stdout."""
        assert tee_run["a2c_bytes"] == tee_run["stdout"]


# ---------------------------------------------------------------------------
# Directional files equal the timeline split
# ---------------------------------------------------------------------------
class TestDirectionalEqualsTimeline:
    def _timeline_split(self, tee_run, direction):
        """Reconstruct directional file bytes from timeline entries."""
        entries = [e for e in tee_run["timeline"] if e["dir"] == direction]
        lines = []
        for e in entries:
            if e["frame"] is not None:
                lines.append(json.dumps(e["frame"], separators=(",", ":")) + "\n")
            else:
                lines.append(e["raw"] + "\n")
        return "".join(lines).encode("utf-8")

    def test_c2a_split(self, tee_run):
        reconstructed = self._timeline_split(tee_run, "c2a")
        assert reconstructed == tee_run["c2a_bytes"]

    def test_a2c_split(self, tee_run):
        reconstructed = self._timeline_split(tee_run, "a2c")
        assert reconstructed == tee_run["a2c_bytes"]


# ---------------------------------------------------------------------------
# Runtime identity
# ---------------------------------------------------------------------------
class TestRuntimeIdentity:
    def test_has_all_keys(self, tee_run):
        expected = {
            "tee_path", "tee_sha256", "agent_argv", "agent_realpath",
            "agent_entrypoint_sha256", "agent_child_pid",
            "agent_interpreter_realpath", "agent_interpreter_sha256",
            "python_dont_write_bytecode", "spawned_at_utc",
        }
        assert expected <= set(tee_run["identity"].keys())

    def test_agent_sha256(self, tee_run):
        expected = _sha256_file(str(tee_run["agent_script"]))
        assert tee_run["identity"]["agent_entrypoint_sha256"] == expected

    def test_tee_sha256(self, tee_run):
        expected = _sha256_file(str(TEE))
        assert tee_run["identity"]["tee_sha256"] == expected

    def test_agent_argv(self, tee_run):
        assert tee_run["identity"]["agent_argv"] == [str(tee_run["agent_script"])]

    def test_python_dont_write_bytecode(self, tee_run):
        assert tee_run["identity"]["python_dont_write_bytecode"] is True

    def test_spawned_at_utc_format(self, tee_run):
        ts = tee_run["identity"]["spawned_at_utc"]
        assert ts.endswith("Z")
        assert "T" in ts

    def test_agent_child_pid(self, tee_run):
        assert isinstance(tee_run["identity"]["agent_child_pid"], int)
        assert tee_run["identity"]["agent_child_pid"] > 0


# ---------------------------------------------------------------------------
# Exit code propagation
# ---------------------------------------------------------------------------
class TestExitCode:
    def test_exit_code(self, tee_run):
        assert tee_run["proc"].returncode == 42
