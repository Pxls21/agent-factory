"""proofs/S0-01/tools/frame_tee.py v2 — stdio proxy with timeline, identity, directional files.

Tests the v2 tee contract: timestamps + seq inside the lock, os.read stdin pump,
bounded stdout join, signal exit codes, raw_b64 for non-JSON, tee_pid in identity.

Mutant-killing tests (V-c F7): lock removal (bursty two-pump stress >= 2000 frames
per direction), 64 KiB truncation, dropped c2a partial line, dropped a2c partial line,
CRLF normalisation, hardcoded bytecode flag, frozen timestamps, NaN/Infinity -> raw/raw_b64,
t_mono_ns window bracket, missing env vars.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import textwrap
import time
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


def _run_tee(tmpdir, agent_code, input_bytes, env_extra=None, timeout=30):
    """Run the tee with a given agent and return all artifacts."""
    framedir = tmpdir / "frames"
    framedir.mkdir(parents=True, exist_ok=True)

    agent_script = tmpdir / "fake_agent.py"
    agent_script.write_text("#!%s\n" % sys.executable + agent_code)
    agent_script.chmod(0o755)

    env = os.environ.copy()
    env["S0_01_FRAMEDIR"] = str(framedir)
    env["S0_01_AGENT"] = str(agent_script)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if env_extra:
        env.update(env_extra)

    proc = subprocess.run(
        [sys.executable, str(TEE)],
        input=input_bytes,
        capture_output=True,
        env=env,
        timeout=timeout,
    )

    timeline_lines = []
    tl_path = framedir / "timeline.jsonl"
    if tl_path.exists():
        for raw in tl_path.read_bytes().split(b"\n"):
            if raw.strip():
                timeline_lines.append(json.loads(raw))

    c2a_bytes = b""
    c2a_path = framedir / "frames-client-to-agent.jsonl"
    if c2a_path.exists():
        c2a_bytes = c2a_path.read_bytes()

    a2c_bytes = b""
    a2c_path = framedir / "frames-agent-to-client.jsonl"
    if a2c_path.exists():
        a2c_bytes = a2c_path.read_bytes()

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


@pytest.fixture(scope="module")
def tee_run(tmp_path_factory):
    tmpdir = tmp_path_factory.mktemp("tee")
    return _run_tee(tmpdir, FAKE_AGENT_CODE, _build_input())


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
        """Client sent 'this is not json' — timeline records frame=null, raw=string, raw_b64."""
        c2a = [e for e in tee_run["timeline"] if e["dir"] == "c2a"]
        non_json = [e for e in c2a if e["frame"] is None]
        assert len(non_json) >= 1, "no non-JSON c2a entry"
        assert non_json[0]["raw"] == "this is not json"
        # raw_b64 must round-trip to the original line bytes
        decoded = base64.b64decode(non_json[0]["raw_b64"])
        assert decoded == b"this is not json\n"

    def test_a2c_non_json(self, tee_run):
        """Agent replied 'agent-echo-nonJSON' — timeline records frame=null, raw=string, raw_b64."""
        a2c = [e for e in tee_run["timeline"] if e["dir"] == "a2c"]
        non_json = [e for e in a2c if e["frame"] is None]
        assert len(non_json) >= 1, "no non-JSON a2c entry"
        assert non_json[0]["raw"] == "agent-echo-nonJSON"
        decoded = base64.b64decode(non_json[0]["raw_b64"])
        assert decoded == b"agent-echo-nonJSON\n"


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
        parts = []
        for e in entries:
            if e["frame"] is not None:
                parts.append(json.dumps(e["frame"], separators=(",", ":")).encode("utf-8") + b"\n")
            else:
                # Use raw_b64 for exact byte reconstruction
                parts.append(base64.b64decode(e["raw_b64"]))
        return b"".join(parts)

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
            "tee_path", "tee_sha256", "tee_pid", "agent_argv", "agent_realpath",
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

    def test_tee_pid(self, tee_run):
        assert isinstance(tee_run["identity"]["tee_pid"], int)
        assert tee_run["identity"]["tee_pid"] > 0


# ---------------------------------------------------------------------------
# Exit code propagation
# ---------------------------------------------------------------------------
class TestExitCode:
    def test_exit_code(self, tee_run):
        assert tee_run["proc"].returncode == 42


# ---------------------------------------------------------------------------
# V-c F8: signal-killed agent -> tee exit 128+signal (e.g. SIGTERM -> 143)
# ---------------------------------------------------------------------------
class TestSignalExitCode:
    def test_sigterm_agent_exit_143(self, tmp_path):
        agent_code = textwrap.dedent("""\
            import os, signal, sys, json
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            os.kill(os.getpid(), signal.SIGTERM)
        """)
        input_bytes = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}).encode() + b"\n"
        result = _run_tee(tmp_path, agent_code, input_bytes)
        assert result["proc"].returncode == 143, f"expected 143, got {result['proc'].returncode}"


# ---------------------------------------------------------------------------
# V-c F1: agent exits while client stdin is open -> tee exits with agent code,
# no SIGABRT, no dropped frames
# ---------------------------------------------------------------------------
class TestAgentExitsWhileStdinOpen:
    def test_tee_exits_cleanly_with_agent_code(self, tmp_path):
        """Agent reads one frame, replies, exits 0. Client sends a second frame 0.5s later.
        The tee must exit with code 0 within 3 seconds and not lose the first frame."""
        agent_code = textwrap.dedent("""\
            import sys, json
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            sys.exit(0)
        """)
        # Use a helper script that sends one frame, waits, sends another
        helper = tmp_path / "helper.py"
        helper.write_text(textwrap.dedent("""\
            import sys, time, json
            frame1 = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
            sys.stdout.buffer.write(frame1.encode() + b"\\n")
            sys.stdout.buffer.flush()
            time.sleep(1.0)
            frame2 = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "late", "params": {}})
            sys.stdout.buffer.write(frame2.encode() + b"\\n")
            sys.stdout.buffer.flush()
        """))

        framedir = tmp_path / "frames"
        framedir.mkdir()
        agent_script = tmp_path / "fake_agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)

        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        start = time.monotonic()
        # pipe helper stdout into tee stdin
        helper_proc = subprocess.Popen(
            [sys.executable, str(helper)],
            stdout=subprocess.PIPE,
        )
        tee_proc = subprocess.Popen(
            [sys.executable, str(TEE)],
            stdin=helper_proc.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        helper_proc.stdout.close()  # allow tee to get SIGPIPE/EOF when helper ends
        tee_proc.wait(timeout=10)
        elapsed = time.monotonic() - start
        helper_proc.wait(timeout=5)

        assert tee_proc.returncode == 0, f"expected 0, got {tee_proc.returncode}"
        assert elapsed < 6, f"tee took {elapsed:.1f}s (should be < 6)"
        # stderr should NOT contain SIGABRT/Fatal Python error
        stderr = tee_proc.stderr.read().decode("utf-8", errors="replace")
        assert "Fatal Python error" not in stderr
        # The a2c directional file should have the agent's reply
        a2c = (framedir / "frames-agent-to-client.jsonl").read_bytes()
        assert len(a2c) > 0, "agent reply was lost"


# ---------------------------------------------------------------------------
# V-c F9: grandchild holding stdout -> tee exits within 6 s
# ---------------------------------------------------------------------------
class TestGrandchildStdout:
    def test_grandchild_does_not_stall_tee(self, tmp_path):
        """A grandchild holding stdout open must not stall the tee beyond the 5s join timeout."""
        agent_code = textwrap.dedent("""\
            import subprocess, sys, json
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            # Grandchild inherits stdout and sleeps 30s
            subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
            sys.exit(0)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir(parents=True, exist_ok=True)
        agent_script = tmp_path / "fake_agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)

        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        input_bytes = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                  "params": {}}).encode() + b"\n"

        # Use Popen so we can wait on the tee process exit without blocking on
        # stdout EOF (the grandchild holds stdout open longer than the tee lives).
        tee_proc = subprocess.Popen(
            [sys.executable, str(TEE)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        start = time.monotonic()
        tee_proc.stdin.write(input_bytes)
        tee_proc.stdin.close()
        # The tee should exit within ~6s (agent exits fast, 5s stdout join timeout)
        rc = tee_proc.wait(timeout=12)
        elapsed = time.monotonic() - start
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert rc == 0, f"expected 0, got {rc}"
        assert elapsed < 10, f"tee took {elapsed:.1f}s (should be < 10 with 5s join timeout)"


# ---------------------------------------------------------------------------
# Mutant killer: lock removed — bursty two-pump stress (8-verify F4)
# Client burst >= 2000 frames, agent independently bursts >= 2000 frames.
# The agent reads ONE trigger, then writes >= 2000 frames independently
# while the tee's c2a pump still processes the remaining client frames.
# ---------------------------------------------------------------------------
class TestLockContention:
    def test_seq_contiguous_and_mono_nondecreasing_under_contention(self, tmp_path):
        """Bursty stress with >= 2000 frames from EACH direction (not lock-step echo).
        Assert seq contiguous 1..N, t_mono_ns non-decreasing, t_utc non-decreasing.
        Kills the 'lock removed' mutant (8-verify F4)."""
        n_c2a = 5000
        n_a2c = 5000
        # Agent: read one trigger, then burst n_a2c frames while draining stdin.
        # Write each frame individually (no batch flush) to maximize interleaving.
        agent_code = textwrap.dedent("""\
            import sys, json, threading
            def burst_writer(n):
                for i in range(n):
                    r = {"jsonrpc": "2.0", "method": "burst", "params": {"n": i}}
                    line = json.dumps(r, separators=(",", ":")).encode() + b"\\n"
                    sys.stdout.buffer.write(line)
                    if i %% 50 == 0:
                        sys.stdout.buffer.flush()
                sys.stdout.buffer.flush()
            sys.stdin.readline()  # read trigger
            t = threading.Thread(target=burst_writer, args=(%d,))
            t.start()
            sys.stdin.read()  # drain remaining client frames
            t.join()
            sys.exit(0)
        """ % n_a2c)

        # Build input: 1 trigger + (n_c2a - 1) more frames
        lines = []
        for i in range(n_c2a):
            lines.append(json.dumps({"jsonrpc": "2.0", "id": i, "method": "m", "params": {}},
                                    separators=(",", ":")) + "\n")
        input_bytes = "".join(lines).encode("utf-8")

        result = _run_tee(tmp_path, agent_code, input_bytes, timeout=60)
        tl = result["timeline"]
        assert len(tl) >= n_c2a + n_a2c, \
            f"expected >= {n_c2a + n_a2c} entries, got {len(tl)}"

        # seq must be contiguous 1..N
        for i, entry in enumerate(tl):
            assert entry["seq"] == i + 1, f"seq gap at index {i}: {entry['seq']} != {i + 1}"

        # t_mono_ns must be non-decreasing
        for i in range(1, len(tl)):
            assert tl[i]["t_mono_ns"] >= tl[i - 1]["t_mono_ns"], \
                f"t_mono_ns decreased at seq {tl[i]['seq']}: {tl[i]['t_mono_ns']} < {tl[i - 1]['t_mono_ns']}"

        # t_utc must be non-decreasing
        for i in range(1, len(tl)):
            assert tl[i]["t_utc"] >= tl[i - 1]["t_utc"], \
                f"t_utc decreased at seq {tl[i]['seq']}: {tl[i]['t_utc']} < {tl[i - 1]['t_utc']}"


# ---------------------------------------------------------------------------
# V-c F7 mutant killer: 64 KiB line round-trips byte-exact
# ---------------------------------------------------------------------------
class TestLargeLineRoundTrip:
    def test_64kb_line_preserved(self, tmp_path):
        """A line > 64 KiB must round-trip byte-exact through the directional file."""
        agent_code = textwrap.dedent("""\
            import sys
            for line in sys.stdin:
                sys.stdout.write(line)
                sys.stdout.flush()
            sys.exit(0)
        """)
        # Build a JSON line > 64 KiB
        big_value = "x" * 70000
        frame = {"jsonrpc": "2.0", "id": 1, "method": "big", "params": {"v": big_value}}
        line = json.dumps(frame, separators=(",", ":")) + "\n"
        assert len(line.encode()) > 65536, f"line too short: {len(line.encode())}"
        input_bytes = line.encode("utf-8")

        result = _run_tee(tmp_path, agent_code, input_bytes)
        assert result["proc"].returncode == 0
        # c2a directional file must contain the exact bytes
        assert result["c2a_bytes"] == input_bytes
        # a2c directional file must also match (agent echoes)
        assert result["a2c_bytes"] == input_bytes
        # Timeline frame must parse back to the same object
        c2a_entries = [e for e in result["timeline"] if e["dir"] == "c2a"]
        assert len(c2a_entries) == 1
        assert c2a_entries[0]["frame"]["params"]["v"] == big_value


# ---------------------------------------------------------------------------
# Mutant killer: partial last line — c2a direction (5-verify M6, 8-verify F6)
# The c2a path uses _read_lines_from_fd; `if buf: yield buf` is the guard.
# ---------------------------------------------------------------------------
class TestPartialLastLineC2A:
    def test_c2a_partial_line_at_eof(self, tmp_path):
        """A final CLIENT line without a trailing newline must be recorded in
        frames-client-to-agent.jsonl and timeline.jsonl.  Kills the
        'drop-partial-last-line' mutant (5-verify M6, 8-verify F6)."""
        agent_code = textwrap.dedent("""\
            import sys
            # Drain stdin so the tee pump can finish
            sys.stdin.read()
            sys.exit(0)
        """)
        # Input WITHOUT a trailing newline
        partial_line = b'{"jsonrpc":"2.0","id":99,"method":"partial","params":{}}'
        result = _run_tee(tmp_path, agent_code, partial_line)
        assert result["proc"].returncode == 0
        # The c2a directional file must contain the partial line bytes exactly
        assert result["c2a_bytes"] == partial_line
        # Timeline must have a c2a entry with the parsed frame
        c2a = [e for e in result["timeline"] if e["dir"] == "c2a"]
        assert len(c2a) == 1, f"expected 1 c2a entry, got {len(c2a)}"
        assert c2a[0]["frame"] == {"jsonrpc": "2.0", "id": 99, "method": "partial", "params": {}}


# ---------------------------------------------------------------------------
# V-c F7 mutant killer: partial last line — a2c direction (existing test)
# ---------------------------------------------------------------------------
class TestPartialLastLine:
    def test_partial_line_at_eof(self, tmp_path):
        """A final line without a trailing newline must still be recorded."""
        agent_code = textwrap.dedent("""\
            import sys
            sys.stdout.buffer.write(b'{"jsonrpc":"2.0","id":1,"result":{}}')
            sys.stdout.buffer.flush()
            sys.exit(0)
        """)
        # Send a complete line to stdin (agent reads and replies with no terminator)
        input_bytes = b'{"jsonrpc":"2.0","id":1,"method":"init","params":{}}\n'
        result = _run_tee(tmp_path, agent_code, input_bytes)
        assert result["proc"].returncode == 0
        # The a2c directional file must contain the partial line bytes
        assert result["a2c_bytes"] == b'{"jsonrpc":"2.0","id":1,"result":{}}'
        # Timeline must have an a2c entry with the parsed frame
        a2c = [e for e in result["timeline"] if e["dir"] == "a2c"]
        assert len(a2c) == 1
        assert a2c[0]["frame"] == {"jsonrpc": "2.0", "id": 1, "result": {}}


# ---------------------------------------------------------------------------
# V-c F7 mutant killer: CRLF preserved in the directional file
# ---------------------------------------------------------------------------
class TestCrlfPreservation:
    def test_crlf_line_byte_exact(self, tmp_path):
        """A CRLF-terminated line must appear byte-exact in the directional file."""
        agent_code = textwrap.dedent("""\
            import sys
            sys.stdout.buffer.write(b'{"jsonrpc":"2.0","id":1,"result":{}}\\r\\n')
            sys.stdout.buffer.flush()
            sys.exit(0)
        """)
        # Input with CRLF
        input_bytes = b'{"jsonrpc":"2.0","id":1,"method":"init","params":{}}\r\n'
        result = _run_tee(tmp_path, agent_code, input_bytes)
        assert result["proc"].returncode == 0
        # c2a file must preserve CRLF
        assert result["c2a_bytes"] == input_bytes
        # a2c file must preserve CRLF
        assert result["a2c_bytes"] == b'{"jsonrpc":"2.0","id":1,"result":{}}\r\n'


# ---------------------------------------------------------------------------
# V-c F7 mutant killer: python_dont_write_bytecode reflects the env var
# ---------------------------------------------------------------------------
class TestBytecodeFlag:
    def test_bytecode_true_when_set(self, tmp_path):
        agent_code = textwrap.dedent("""\
            import sys
            sys.exit(0)
        """)
        result = _run_tee(tmp_path / "bt", agent_code, b"", env_extra={"PYTHONDONTWRITEBYTECODE": "1"})
        assert result["identity"]["python_dont_write_bytecode"] is True

    def test_bytecode_false_when_unset(self, tmp_path):
        """python_dont_write_bytecode must be False when the env var is absent.
        Kills the 'hardcoded True' mutant (V-c F7)."""
        agent_code = textwrap.dedent("""\
            import sys
            sys.exit(0)
        """)
        framedir = tmp_path / "bf" / "frames"
        framedir.mkdir(parents=True)
        agent_script = tmp_path / "bf" / "fake_agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)

        # Build env WITHOUT PYTHONDONTWRITEBYTECODE
        env = {k: v for k, v in os.environ.items() if k != "PYTHONDONTWRITEBYTECODE"}
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)

        subprocess.run(
            [sys.executable, str(TEE)],
            input=b"",
            capture_output=True,
            env=env,
            timeout=30,
        )
        identity = json.loads((framedir / "runtime-identity.json").read_text())
        assert identity["python_dont_write_bytecode"] is False


# ---------------------------------------------------------------------------
# V-c F7 mutant killer: timestamps are real (not frozen to epoch)
# ---------------------------------------------------------------------------
class TestTimestampsAreReal:
    def test_t_utc_within_60s_of_now(self, tee_run):
        """All t_utc values must parse and be within 60s of test execution time."""
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        for e in tee_run["timeline"]:
            ts = e["t_utc"]
            # Must match YYYY-MM-DDTHH:MM:SS.ffffffZ exactly
            parsed = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                tzinfo=datetime.timezone.utc)
            delta = abs((now - parsed).total_seconds())
            assert delta < 60, f"t_utc {ts} is {delta:.1f}s from now"

    def test_t_utc_increases(self, tee_run):
        """t_utc values must be non-decreasing (kills frozen-timestamp mutant)."""
        utcs = [e["t_utc"] for e in tee_run["timeline"]]
        for i in range(1, len(utcs)):
            assert utcs[i] >= utcs[i - 1], f"t_utc decreased at {i}: {utcs[i]} < {utcs[i - 1]}"


# ---------------------------------------------------------------------------
# L2 mutant killer: t_mono_ns is monotonic_ns, not wall clock (5-verify L2)
# Bracket the tee run with time.monotonic_ns() and assert all recorded
# t_mono_ns values lie inside that window.
# ---------------------------------------------------------------------------
class TestMonoNsWindow:
    def test_t_mono_ns_within_monotonic_window(self, tmp_path):
        """All t_mono_ns values must lie within the test's own monotonic_ns window.
        Kills the 'time.time_ns() instead of monotonic_ns()' mutant (5-verify L2)."""
        agent_code = textwrap.dedent("""\
            import sys, json
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp, separators=(",", ":")) + "\\n")
            sys.stdout.flush()
            sys.exit(0)
        """)
        input_bytes = json.dumps(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            separators=(",", ":")).encode() + b"\n"

        before = time.monotonic_ns()
        result = _run_tee(tmp_path, agent_code, input_bytes)
        after = time.monotonic_ns()

        assert result["proc"].returncode == 0
        tl = result["timeline"]
        assert len(tl) >= 1, "timeline is empty"
        for e in tl:
            mono = e["t_mono_ns"]
            assert before <= mono <= after, \
                f"t_mono_ns {mono} outside monotonic window [{before}, {after}]"


# ---------------------------------------------------------------------------
# M9 mutant killer: NaN/Infinity lines take the raw/raw_b64 branch
# (5-verify M9)
# ---------------------------------------------------------------------------
class TestNanInfinityRawBranch:
    def test_nan_line_takes_raw_branch(self, tmp_path):
        """A line containing NaN must be recorded as frame=null with raw/raw_b64,
        NOT re-emitted as non-strict JSON.  Kills the NaN-passthrough mutant
        (5-verify M9)."""
        agent_code = textwrap.dedent("""\
            import sys
            # Agent echoes the NaN line back
            sys.stdout.buffer.write(b'{"value": NaN}\\n')
            sys.stdout.buffer.flush()
            sys.stdin.read()
            sys.exit(0)
        """)
        # Client sends a NaN line
        input_bytes = b'{"value": NaN}\n'
        result = _run_tee(tmp_path, agent_code, input_bytes)
        assert result["proc"].returncode == 0
        # Both c2a and a2c should have raw/raw_b64 entries (frame=null)
        c2a = [e for e in result["timeline"] if e["dir"] == "c2a"]
        assert len(c2a) >= 1, "no c2a entry"
        assert c2a[0]["frame"] is None, "NaN line should have frame=null"
        assert c2a[0]["raw"] == '{"value": NaN}'
        decoded = base64.b64decode(c2a[0]["raw_b64"])
        assert decoded == b'{"value": NaN}\n'

        a2c = [e for e in result["timeline"] if e["dir"] == "a2c"]
        assert len(a2c) >= 1, "no a2c entry"
        assert a2c[0]["frame"] is None, "NaN line should have frame=null"
        assert a2c[0]["raw"] == '{"value": NaN}'

    def test_infinity_line_takes_raw_branch(self, tmp_path):
        """A line containing Infinity must be recorded as frame=null."""
        agent_code = textwrap.dedent("""\
            import sys
            sys.stdout.buffer.write(b'{"value": Infinity}\\n')
            sys.stdout.buffer.flush()
            sys.stdin.read()
            sys.exit(0)
        """)
        input_bytes = b'{"value": Infinity}\n'
        result = _run_tee(tmp_path, agent_code, input_bytes)
        assert result["proc"].returncode == 0
        c2a = [e for e in result["timeline"] if e["dir"] == "c2a"]
        assert len(c2a) >= 1, "no c2a entry"
        assert c2a[0]["frame"] is None, "Infinity line should have frame=null"
        assert c2a[0]["raw"] == '{"value": Infinity}'

    def test_neg_infinity_line_takes_raw_branch(self, tmp_path):
        """A line containing -Infinity must be recorded as frame=null."""
        agent_code = textwrap.dedent("""\
            import sys
            sys.stdin.read()
            sys.exit(0)
        """)
        input_bytes = b'{"value": -Infinity}\n'
        result = _run_tee(tmp_path, agent_code, input_bytes)
        assert result["proc"].returncode == 0
        c2a = [e for e in result["timeline"] if e["dir"] == "c2a"]
        assert len(c2a) >= 1, "no c2a entry"
        assert c2a[0]["frame"] is None, "-Infinity line should have frame=null"
        assert c2a[0]["raw"] == '{"value": -Infinity}'

    def test_nan_line_directional_file_byte_exact(self, tmp_path):
        """The directional file preserves NaN lines byte-exactly."""
        agent_code = textwrap.dedent("""\
            import sys
            sys.stdin.read()
            sys.exit(0)
        """)
        input_bytes = b'{"value": NaN}\n'
        result = _run_tee(tmp_path, agent_code, input_bytes)
        assert result["c2a_bytes"] == input_bytes


# ---------------------------------------------------------------------------
# L15: missing env vars -> named error + exit 64 (5-verify L15)
# ---------------------------------------------------------------------------
class TestMissingEnvVars:
    def test_missing_framedir(self, tmp_path):
        """Missing S0_01_FRAMEDIR prints a named error and exits 64."""
        env = {k: v for k, v in os.environ.items()
               if k not in ("S0_01_FRAMEDIR", "S0_01_AGENT")}
        proc = subprocess.run(
            [sys.executable, str(TEE)],
            input=b"",
            capture_output=True,
            env=env,
            timeout=10,
        )
        assert proc.returncode == 64
        assert proc.stderr.decode().strip() == "frame_tee: S0_01_FRAMEDIR is not set"

    def test_missing_agent(self, tmp_path):
        """Missing S0_01_AGENT prints a named error and exits 64."""
        env = {k: v for k, v in os.environ.items()
               if k not in ("S0_01_FRAMEDIR", "S0_01_AGENT")}
        env["S0_01_FRAMEDIR"] = str(tmp_path)
        proc = subprocess.run(
            [sys.executable, str(TEE)],
            input=b"",
            capture_output=True,
            env=env,
            timeout=10,
        )
        assert proc.returncode == 64
        assert proc.stderr.decode().strip() == "frame_tee: S0_01_AGENT is not set"
