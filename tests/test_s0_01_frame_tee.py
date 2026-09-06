"""proofs/S0-01/tools/frame_tee.py v2 — stdio proxy with timeline, identity, directional files.

Tests the v2 tee contract: timestamps + seq inside the lock, os.read stdin pump,
bounded stdout join, signal exit codes, raw_b64 for non-JSON, tee_pid in identity,
A21d running-status rewrites (final/non-final, updated_seq, atomic writes).
"""
from __future__ import annotations

import base64
import datetime
import hashlib
import json
import os
import signal as sig
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

# A21d: the exact key set for tee-status.json
STATUS_KEYS = {
    "final", "agent_returncode", "drained", "stdin_reader_done",
    "recorded_c2a", "recorded_a2c", "forwarded_c2a", "forwarded_a2c",
    "write_errors", "exit_code", "updated_seq", "updated_utc",
}


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
    t_before = datetime.datetime.now(datetime.timezone.utc)
    result = _run_tee(tmpdir, FAKE_AGENT_CODE, _build_input())
    t_after = datetime.datetime.now(datetime.timezone.utc)
    result["t_utc_before"] = t_before
    result["t_utc_after"] = t_after
    return result


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
        assert len(a2c) == 5, f"expected 5 a2c entries, got {len(a2c)}"


# ---------------------------------------------------------------------------
class TestNonJsonLine:
    def test_c2a_non_json(self, tee_run):
        c2a = [e for e in tee_run["timeline"] if e["dir"] == "c2a"]
        non_json = [e for e in c2a if e["frame"] is None]
        assert len(non_json) >= 1
        assert non_json[0]["raw"] == "this is not json"
        assert base64.b64decode(non_json[0]["raw_b64"]) == b"this is not json\n"

    def test_a2c_non_json(self, tee_run):
        a2c = [e for e in tee_run["timeline"] if e["dir"] == "a2c"]
        non_json = [e for e in a2c if e["frame"] is None]
        assert len(non_json) >= 1
        assert non_json[0]["raw"] == "agent-echo-nonJSON"
        assert base64.b64decode(non_json[0]["raw_b64"]) == b"agent-echo-nonJSON\n"


# ---------------------------------------------------------------------------
class TestByteRelay:
    def test_c2a_relay(self, tee_run):
        assert tee_run["c2a_bytes"] == tee_run["input_bytes"]

    def test_a2c_relay(self, tee_run):
        assert tee_run["a2c_bytes"] == tee_run["stdout"]


# ---------------------------------------------------------------------------
class TestDirectionalEqualsTimeline:
    def _timeline_split(self, tee_run, direction):
        entries = [e for e in tee_run["timeline"] if e["dir"] == direction]
        parts = []
        for e in entries:
            if e["frame"] is not None:
                parts.append(json.dumps(e["frame"], separators=(",", ":")).encode("utf-8") + b"\n")
            else:
                parts.append(base64.b64decode(e["raw_b64"]))
        return b"".join(parts)

    def test_c2a_split(self, tee_run):
        assert self._timeline_split(tee_run, "c2a") == tee_run["c2a_bytes"]

    def test_a2c_split(self, tee_run):
        assert self._timeline_split(tee_run, "a2c") == tee_run["a2c_bytes"]


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
        assert tee_run["identity"]["agent_entrypoint_sha256"] == _sha256_file(str(tee_run["agent_script"]))

    def test_tee_sha256(self, tee_run):
        assert tee_run["identity"]["tee_sha256"] == _sha256_file(str(TEE))

    def test_agent_argv(self, tee_run):
        assert tee_run["identity"]["agent_argv"] == [str(tee_run["agent_script"])]

    def test_python_dont_write_bytecode(self, tee_run):
        assert tee_run["identity"]["python_dont_write_bytecode"] is True

    def test_spawned_at_utc_format(self, tee_run):
        ts = tee_run["identity"]["spawned_at_utc"]
        assert ts.endswith("Z") and "T" in ts

    def test_agent_child_pid(self, tee_run):
        assert isinstance(tee_run["identity"]["agent_child_pid"], int)
        assert tee_run["identity"]["agent_child_pid"] > 0

    def test_tee_pid(self, tee_run):
        assert isinstance(tee_run["identity"]["tee_pid"], int)
        assert tee_run["identity"]["tee_pid"] > 0


# ---------------------------------------------------------------------------
class TestExitCode:
    def test_exit_code(self, tee_run):
        assert tee_run["proc"].returncode == 42


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
        assert result["proc"].returncode == 143


# ---------------------------------------------------------------------------
# F1: late client frame must be recorded or tee exits 70
# ---------------------------------------------------------------------------
class TestLateClientFrameRecorded:
    def test_late_client_frame_recorded_or_exit_70(self, tmp_path):
        """F1: agent reads one frame, replies, exits immediately. The remaining
        49 frames must be recorded in c2a.jsonl and tee must exit 70."""
        agent_code = textwrap.dedent("""\
            import os, sys, json
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            os._exit(0)
        """)
        frame1 = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                             "params": {}}, separators=(",", ":")) + "\n"
        late_frames = []
        for i in range(2, 51):
            late_frames.append(json.dumps({"jsonrpc": "2.0", "id": i, "method": "late",
                                           "params": {}}, separators=(",", ":")) + "\n")
        input_bytes = (frame1 + "".join(late_frames)).encode("utf-8")
        result = _run_tee(tmp_path, agent_code, input_bytes)
        # Late frames must be in c2a.jsonl (pump continues recording after forward error)
        assert b'"method":"late"' in result["c2a_bytes"]
        assert result["proc"].returncode == 70
        assert b"Fatal Python error" not in result["proc"].stderr


# ---------------------------------------------------------------------------
class TestGrandchildStdout:
    def test_grandchild_does_not_stall_tee(self, tmp_path):
        agent_code = textwrap.dedent("""\
            import subprocess, sys, json
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
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
        tee_proc = subprocess.Popen(
            [sys.executable, str(TEE)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
        )
        tee_proc.stdin.write(input_bytes)
        tee_proc.stdin.close()
        tee_proc.wait(timeout=30)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 0


# ---------------------------------------------------------------------------
class TestLockContention:
    def test_seq_contiguous_and_mono_nondecreasing_under_contention(self, tmp_path):
        n_c2a = 10000
        n_a2c = 10000
        agent_code = textwrap.dedent("""\
            import sys, json, threading
            def burst_writer(n):
                for i in range(n):
                    r = {"jsonrpc": "2.0", "method": "b", "params": {"n": i}}
                    sys.stdout.buffer.write(json.dumps(r, separators=(",", ":")).encode() + b"\\n")
                    sys.stdout.buffer.flush()
            sys.stdin.readline()
            t = threading.Thread(target=burst_writer, args=(%d,))
            t.start()
            sys.stdin.read()
            t.join()
            sys.exit(0)
        """ % n_a2c)
        lines = []
        for i in range(n_c2a):
            lines.append(json.dumps({"jsonrpc": "2.0", "id": i, "method": "m", "params": {}},
                                    separators=(",", ":")) + "\n")
        input_bytes = "".join(lines).encode("utf-8")
        result = _run_tee(tmp_path, agent_code, input_bytes, timeout=600)
        tl = result["timeline"]
        assert len(tl) >= n_c2a + n_a2c
        for i, entry in enumerate(tl):
            assert entry["seq"] == i + 1, f"seq gap at {i}: {entry['seq']} != {i + 1}"
        for i in range(1, len(tl)):
            assert tl[i]["t_mono_ns"] >= tl[i - 1]["t_mono_ns"]
            assert tl[i]["t_utc"] >= tl[i - 1]["t_utc"]


# ---------------------------------------------------------------------------
class TestLargeLineRoundTrip:
    def test_64kb_line_preserved(self, tmp_path):
        agent_code = textwrap.dedent("""\
            import sys
            for line in sys.stdin:
                sys.stdout.write(line)
                sys.stdout.flush()
            sys.exit(0)
        """)
        big_value = "x" * 70000
        frame = {"jsonrpc": "2.0", "id": 1, "method": "big", "params": {"v": big_value}}
        line = json.dumps(frame, separators=(",", ":")) + "\n"
        assert len(line.encode()) > 65536
        result = _run_tee(tmp_path, agent_code, line.encode("utf-8"))
        assert result["proc"].returncode == 0
        assert result["c2a_bytes"] == line.encode("utf-8")
        assert result["a2c_bytes"] == line.encode("utf-8")


# ---------------------------------------------------------------------------
class TestPartialLastLineC2A:
    def test_c2a_partial_line_at_eof(self, tmp_path):
        agent_code = "import sys\nsys.stdin.read()\nsys.exit(0)\n"
        partial_line = b'{"jsonrpc":"2.0","id":99,"method":"partial","params":{}}'
        result = _run_tee(tmp_path, agent_code, partial_line)
        assert result["proc"].returncode == 0
        assert result["c2a_bytes"] == partial_line


class TestPartialLastLine:
    def test_partial_line_at_eof(self, tmp_path):
        agent_code = textwrap.dedent("""\
            import sys
            sys.stdin.read()
            sys.stdout.buffer.write(b'{"jsonrpc":"2.0","id":1,"result":{}}')
            sys.stdout.buffer.flush()
            sys.exit(0)
        """)
        result = _run_tee(tmp_path, agent_code, b'{"jsonrpc":"2.0","id":1,"method":"init","params":{}}\n')
        assert result["proc"].returncode == 0
        assert result["a2c_bytes"] == b'{"jsonrpc":"2.0","id":1,"result":{}}'


class TestCrlfPreservation:
    def test_crlf_line_byte_exact(self, tmp_path):
        agent_code = textwrap.dedent("""\
            import sys
            sys.stdin.read()
            sys.stdout.buffer.write(b'{"jsonrpc":"2.0","id":1,"result":{}}\\r\\n')
            sys.stdout.buffer.flush()
            sys.exit(0)
        """)
        result = _run_tee(tmp_path, agent_code, b'{"jsonrpc":"2.0","id":1,"method":"init","params":{}}\r\n')
        assert result["proc"].returncode == 0
        assert result["c2a_bytes"] == b'{"jsonrpc":"2.0","id":1,"method":"init","params":{}}\r\n'
        assert result["a2c_bytes"] == b'{"jsonrpc":"2.0","id":1,"result":{}}\r\n'


# ---------------------------------------------------------------------------
class TestBytecodeFlag:
    def test_bytecode_true_when_set(self, tmp_path):
        result = _run_tee(tmp_path / "bt", "import sys\nsys.exit(0)\n", b"",
                          env_extra={"PYTHONDONTWRITEBYTECODE": "1"})
        assert result["identity"]["python_dont_write_bytecode"] is True

    def test_bytecode_false_when_unset(self, tmp_path):
        framedir = tmp_path / "bf" / "frames"
        framedir.mkdir(parents=True)
        agent_script = tmp_path / "bf" / "fake_agent.py"
        agent_script.write_text("#!%s\nimport sys\nsys.exit(0)\n" % sys.executable)
        agent_script.chmod(0o755)
        env = {k: v for k, v in os.environ.items() if k != "PYTHONDONTWRITEBYTECODE"}
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        subprocess.run([sys.executable, str(TEE)], input=b"", capture_output=True, env=env, timeout=30)
        assert json.loads((framedir / "runtime-identity.json").read_text())["python_dont_write_bytecode"] is False


# ---------------------------------------------------------------------------
# F8: time bracket captured in the fixture
# ---------------------------------------------------------------------------
class TestTimestampsAreReal:
    def test_t_utc_within_fixture_window(self, tee_run):
        t_before = tee_run["t_utc_before"]
        t_after = tee_run["t_utc_after"]
        margin = datetime.timedelta(seconds=2)
        for e in tee_run["timeline"]:
            parsed = datetime.datetime.strptime(e["t_utc"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                tzinfo=datetime.timezone.utc)
            assert t_before - margin <= parsed <= t_after + margin

    def test_t_utc_increases(self, tee_run):
        utcs = [e["t_utc"] for e in tee_run["timeline"]]
        for i in range(1, len(utcs)):
            assert utcs[i] >= utcs[i - 1]


# ---------------------------------------------------------------------------
class TestMonoNsWindow:
    def test_t_mono_ns_within_monotonic_window(self, tmp_path):
        agent_code = textwrap.dedent("""\
            import sys, json
            line = sys.stdin.readline()
            sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":1,"result":{}},separators=(",",":"))+"\\n")
            sys.stdout.flush()
            sys.exit(0)
        """)
        input_bytes = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                                 separators=(",", ":")).encode() + b"\n"
        before = time.monotonic_ns()
        result = _run_tee(tmp_path, agent_code, input_bytes)
        after = time.monotonic_ns()
        assert result["proc"].returncode == 0
        for e in result["timeline"]:
            assert before <= e["t_mono_ns"] <= after


# ---------------------------------------------------------------------------
class TestNanInfinityRawBranch:
    def test_nan_line_takes_raw_branch(self, tmp_path):
        agent_code = "import sys\nsys.stdout.buffer.write(b'{\"value\": NaN}\\n')\nsys.stdout.buffer.flush()\nsys.stdin.read()\nsys.exit(0)\n"
        result = _run_tee(tmp_path, agent_code, b'{"value": NaN}\n')
        assert result["proc"].returncode == 0
        c2a = [e for e in result["timeline"] if e["dir"] == "c2a"]
        assert c2a[0]["frame"] is None and c2a[0]["raw"] == '{"value": NaN}'

    def test_infinity_line_takes_raw_branch(self, tmp_path):
        agent_code = "import sys\nsys.stdout.buffer.write(b'{\"value\": Infinity}\\n')\nsys.stdout.buffer.flush()\nsys.stdin.read()\nsys.exit(0)\n"
        result = _run_tee(tmp_path, agent_code, b'{"value": Infinity}\n')
        assert result["proc"].returncode == 0
        c2a = [e for e in result["timeline"] if e["dir"] == "c2a"]
        assert c2a[0]["frame"] is None and c2a[0]["raw"] == '{"value": Infinity}'

    def test_neg_infinity_line_takes_raw_branch(self, tmp_path):
        result = _run_tee(tmp_path, "import sys\nsys.stdin.read()\nsys.exit(0)\n", b'{"value": -Infinity}\n')
        c2a = [e for e in result["timeline"] if e["dir"] == "c2a"]
        assert c2a[0]["frame"] is None and c2a[0]["raw"] == '{"value": -Infinity}'

    def test_nan_line_directional_file_byte_exact(self, tmp_path):
        result = _run_tee(tmp_path, "import sys\nsys.stdin.read()\nsys.exit(0)\n", b'{"value": NaN}\n')
        assert result["c2a_bytes"] == b'{"value": NaN}\n'


class TestMissingEnvVars:
    def test_missing_framedir(self, tmp_path):
        env = {k: v for k, v in os.environ.items() if k not in ("S0_01_FRAMEDIR", "S0_01_AGENT")}
        proc = subprocess.run([sys.executable, str(TEE)], input=b"", capture_output=True, env=env, timeout=10)
        assert proc.returncode == 64
        assert proc.stderr.decode().strip() == "frame_tee: S0_01_FRAMEDIR is not set"

    def test_missing_agent(self, tmp_path):
        env = {k: v for k, v in os.environ.items() if k not in ("S0_01_FRAMEDIR", "S0_01_AGENT")}
        env["S0_01_FRAMEDIR"] = str(tmp_path)
        proc = subprocess.run([sys.executable, str(TEE)], input=b"", capture_output=True, env=env, timeout=10)
        assert proc.returncode == 64
        assert proc.stderr.decode().strip() == "frame_tee: S0_01_AGENT is not set"


# ---------------------------------------------------------------------------
class TestNonFiniteRawBranchWithOracle:
    @pytest.mark.parametrize("input_text", ['{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '{"a":1e999}'])
    def test_both_directions_raw_and_oracle(self, tmp_path, input_text):
        agent_code = "import sys\nfor line in sys.stdin:\n    sys.stdout.write(line)\n    sys.stdout.flush()\nsys.exit(0)\n"
        input_bytes = (input_text + "\n").encode("utf-8")
        result = _run_tee(tmp_path, agent_code, input_bytes)
        assert result["proc"].returncode == 0
        for d in ("c2a", "a2c"):
            entries = [e for e in result["timeline"] if e["dir"] == d]
            assert len(entries) == 1 and entries[0]["frame"] is None and entries[0]["raw"] == input_text
        def _raise(c):
            raise ValueError(c)
        for raw_line in (result["framedir"] / "timeline.jsonl").read_bytes().split(b"\n"):
            if raw_line.strip():
                json.loads(raw_line, parse_constant=_raise)

    def test_normal_float_still_parsed(self, tmp_path):
        result = _run_tee(tmp_path, "import sys\nsys.stdin.read()\nsys.exit(0)\n", b'{"a":1.5}\n')
        assert result["proc"].returncode == 0
        c2a = [e for e in result["timeline"] if e["dir"] == "c2a"]
        assert c2a[0]["frame"] == {"a": 1.5}


# ---------------------------------------------------------------------------
# P2 / A21d: tee-status.json — drain tracking, exit code discipline, running status
# ---------------------------------------------------------------------------
class TestTeeStatus:
    def test_normal_run_writes_status(self, tee_run):
        status = json.loads((tee_run["framedir"] / "tee-status.json").read_text())
        assert status["final"] is True
        assert status["drained"] is True
        assert status["recorded_c2a"] == 3
        assert status["recorded_a2c"] == 5
        assert status["forwarded_c2a"] == status["recorded_c2a"]
        assert status["forwarded_a2c"] == status["recorded_a2c"]
        assert status["write_errors"] == []
        assert status["exit_code"] == 42
        assert status["agent_returncode"] == 42
        assert status["updated_seq"] == 8  # 3 c2a + 5 a2c
        assert status["updated_utc"].endswith("Z")

    def test_status_keys_exact(self, tee_run):
        status = json.loads((tee_run["framedir"] / "tee-status.json").read_text())
        assert set(status.keys()) == STATUS_KEYS

    def test_agent_burst_within_pipe_buffer_drained(self, tmp_path):
        """F12: agent emits 1000 small frames that fit in the pipe buffer."""
        agent_code = textwrap.dedent("""\
            import sys, json
            for i in range(1000):
                f = {"jsonrpc": "2.0", "method": "c", "params": {"i": i}}
                sys.stdout.write(json.dumps(f, separators=(",", ":")) + "\\n")
                sys.stdout.flush()
            sys.exit(7)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        tee_proc.stdin.close()
        time.sleep(6)
        tee_proc.wait(timeout=15)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 7
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["final"] is True
        assert status["forwarded_a2c"] == 1000
        assert status["drained"] is True
        assert status["write_errors"] == []
        assert status["exit_code"] == 7

    def test_never_reading_client(self, tmp_path):
        """Client NEVER reads -> exit 70, drained false."""
        agent_code = textwrap.dedent("""\
            import os, sys, threading
            def kill_self():
                os._exit(3)
            timer = threading.Timer(2, kill_self)
            timer.daemon = True
            timer.start()
            payload = "x" * 10000
            for i in range(200):
                line = '{"i":' + str(i) + ',"p":"' + payload + '"}\\n'
                try:
                    sys.stdout.buffer.write(line.encode())
                    sys.stdout.buffer.flush()
                except (BrokenPipeError, OSError):
                    break
            os._exit(3)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        tee_proc.stdin.close()
        tee_proc.wait(timeout=20)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 70
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["final"] is True
        assert status["drained"] is False
        assert status["forwarded_a2c"] < status["recorded_a2c"]
        assert status["exit_code"] == 70
        assert len(status["write_errors"]) == 1
        assert status["write_errors"][0].startswith("drain a2c: stopped with ")

    def test_write_failure_exit_70(self, tmp_path):
        if not os.path.exists("/dev/full"):
            pytest.skip("/dev/full not available")
        agent_code = textwrap.dedent("""\
            import sys, json
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            sys.exit(0)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        os.symlink("/dev/full", str(framedir / "timeline.jsonl"))
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        input_bytes = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                                 separators=(",", ":")).encode() + b"\n"
        proc = subprocess.run([sys.executable, str(TEE)], input=input_bytes,
                              capture_output=True, env=env, timeout=30)
        assert proc.returncode == 70
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["exit_code"] == 70
        assert status["write_errors"] == [
            "timeline c2a seq 1: [Errno 28] No space left on device",
            "timeline a2c seq 2: [Errno 28] No space left on device",
        ]

    def test_grandchild_holds_stdout_drained(self, tmp_path):
        """F8: assert drain outcome, not wall-clock ceiling."""
        agent_code = textwrap.dedent("""\
            import subprocess, sys, json
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
            sys.exit(0)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        input_bytes = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                                 separators=(",", ":")).encode() + b"\n"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        tee_proc.stdin.write(input_bytes)
        tee_proc.stdin.close()
        tee_proc.wait(timeout=30)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 0
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["final"] is True
        assert status["drained"] is True
        assert status["write_errors"] == []
        assert status["exit_code"] == 0

    def test_signal_exit_status(self, tmp_path):
        agent_code = textwrap.dedent("""\
            import os, signal, sys, json
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            os.kill(os.getpid(), signal.SIGTERM)
        """)
        input_bytes = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                                 separators=(",", ":")).encode() + b"\n"
        result = _run_tee(tmp_path, agent_code, input_bytes)
        assert result["proc"].returncode == 143
        status = json.loads((result["framedir"] / "tee-status.json").read_text())
        assert status["agent_returncode"] == -15
        assert status["exit_code"] == 143
        assert status["drained"] is True
        assert status["final"] is True


# ---------------------------------------------------------------------------
class TestProgressGatedDrain:
    def test_large_payload_late_reader_drained(self, tmp_path):
        n_lines = 2000
        agent_code = textwrap.dedent("""\
            import sys, json
            for i in range(%d):
                f = {"jsonrpc": "2.0", "method": "d", "params": {"i": i}}
                sys.stdout.write(json.dumps(f, separators=(",", ":")) + "\\n")
                sys.stdout.flush()
            sys.exit(7)
        """ % n_lines)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        reader = tmp_path / "reader.py"
        reader.write_text("import sys, time\nwhile True:\n    chunk = sys.stdin.buffer.read(2048)\n    if not chunk: break\n    time.sleep(0.5)\n")
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        reader_proc = subprocess.Popen([sys.executable, str(reader)],
                                       stdin=tee_proc.stdout, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        tee_proc.stdout.close()
        tee_proc.stdin.close()
        tee_proc.wait(timeout=180)
        reader_proc.wait(timeout=60)
        tee_proc.stderr.close()
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["drained"] is True
        assert status["forwarded_a2c"] == n_lines
        assert status["write_errors"] == []
        assert status["exit_code"] == 7
        assert tee_proc.returncode == 7


# ---------------------------------------------------------------------------
class TestDrainedBothDirections:
    def test_c2a_broken_pipe_is_write_error(self, tmp_path):
        agent_code = textwrap.dedent("""\
            import sys, json, os
            sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp, separators=(",", ":")) + "\\n")
            sys.stdout.flush()
            os._exit(5)
        """)
        pad = "x" * 400
        lines = []
        for i in range(5000):
            lines.append(json.dumps({"jsonrpc": "2.0", "id": i, "method": "m",
                                     "params": {"p": pad}}, separators=(",", ":")) + "\n")
        result = _run_tee(tmp_path, agent_code, "".join(lines).encode("utf-8"), timeout=300)
        assert result["proc"].returncode == 70
        status = json.loads((result["framedir"] / "tee-status.json").read_text())
        assert status["drained"] is False
        assert status["write_errors"] == ["forward c2a: BrokenPipeError"]
        assert status["exit_code"] == 70
        assert status["forwarded_c2a"] < status["recorded_c2a"]


# ---------------------------------------------------------------------------
class TestDirectionalWriteErrorBothDirections:
    @pytest.mark.parametrize("target_file", ["frames-client-to-agent.jsonl", "frames-agent-to-client.jsonl"])
    def test_directional_enospc(self, tmp_path, target_file):
        if not os.path.exists("/dev/full"):
            pytest.skip("/dev/full not available")
        agent_code = textwrap.dedent("""\
            import sys, json
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            sys.exit(0)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        os.symlink("/dev/full", str(framedir / target_file))
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        input_bytes = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                                 separators=(",", ":")).encode() + b"\n"
        proc = subprocess.run([sys.executable, str(TEE)], input=input_bytes,
                              capture_output=True, env=env, timeout=30)
        assert proc.returncode == 70
        status = json.loads((framedir / "tee-status.json").read_text())
        direction = "c2a" if "client-to-agent" in target_file else "a2c"
        assert status["write_errors"] == ["directional %s: [Errno 28] No space left on device" % direction]


# ---------------------------------------------------------------------------
class TestStdinReaderDoneValue:
    def test_stdin_reader_done_true_on_clean_exit(self, tee_run):
        status = json.loads((tee_run["framedir"] / "tee-status.json").read_text())
        assert status["stdin_reader_done"] is True

    def test_stdin_reader_done_false_when_client_never_closes(self, tmp_path):
        """F11: stdin never closed -> stdin_reader_done False, returncode 0, drained True."""
        agent_code = textwrap.dedent("""\
            import sys, json
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp, separators=(",", ":")) + "\\n")
            sys.stdout.flush()
            sys.exit(0)
        """)
        helper = tmp_path / "holder.py"
        helper.write_text("import time\ntime.sleep(30)\n")
        framedir = tmp_path / "frames"
        framedir.mkdir()
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        holder_proc = subprocess.Popen([sys.executable, str(helper)], stdout=subprocess.PIPE)
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=holder_proc.stdout, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        holder_proc.stdout.close()
        tee_proc.wait(timeout=20)
        holder_proc.kill()
        holder_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["stdin_reader_done"] is False
        assert tee_proc.returncode == 0
        assert status["drained"] is True


# ---------------------------------------------------------------------------
class TestFramedirValidation:
    def test_empty_framedir(self, tmp_path):
        env = {k: v for k, v in os.environ.items() if k not in ("S0_01_FRAMEDIR", "S0_01_AGENT")}
        env["S0_01_FRAMEDIR"] = ""
        env["S0_01_AGENT"] = "/bin/true"
        proc = subprocess.run([sys.executable, str(TEE)], input=b"", capture_output=True, env=env, timeout=10)
        assert proc.returncode == 64
        assert proc.stderr.decode().strip() == "frame_tee: S0_01_FRAMEDIR is empty"

    def test_framedir_is_plain_file(self, tmp_path):
        notadir = tmp_path / "notadir"
        notadir.write_text("x")
        env = {k: v for k, v in os.environ.items() if k not in ("S0_01_FRAMEDIR", "S0_01_AGENT")}
        env["S0_01_FRAMEDIR"] = str(notadir)
        env["S0_01_AGENT"] = "/bin/true"
        proc = subprocess.run([sys.executable, str(TEE)], input=b"", capture_output=True, env=env, timeout=10)
        assert proc.returncode == 64
        assert proc.stderr.decode().strip() == "frame_tee: S0_01_FRAMEDIR is not a directory: %s" % notadir

    def test_framedir_dangling_symlink(self, tmp_path):
        """F7: dangling symlink -> exit 64."""
        dangling = tmp_path / "dangling"
        os.symlink(str(tmp_path / "nonexistent"), str(dangling))
        env = {k: v for k, v in os.environ.items() if k not in ("S0_01_FRAMEDIR", "S0_01_AGENT")}
        env["S0_01_FRAMEDIR"] = str(dangling)
        env["S0_01_AGENT"] = "/bin/true"
        proc = subprocess.run([sys.executable, str(TEE)], input=b"", capture_output=True, env=env, timeout=10)
        assert proc.returncode == 64
        assert proc.stderr.decode().strip() == "frame_tee: S0_01_FRAMEDIR is not a directory: %s" % dangling


# ---------------------------------------------------------------------------
# F4: SIGTERM handler
# ---------------------------------------------------------------------------
class TestSigtermHandler:
    def test_sigterm_writes_status_and_exits_70(self, tmp_path):
        """F4: send one frame so the tee writes tee-status.json (confirming
        the handler is installed), then SIGTERM it."""
        agent_code = textwrap.dedent("""\
            import sys, json
            for line in sys.stdin:
                resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
                sys.stdout.write(json.dumps(resp, separators=(",", ":")) + "\\n")
                sys.stdout.flush()
            sys.exit(0)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        # Send one frame and wait for the status file to confirm the tee is running
        frame = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "init", "params": {}},
                           separators=(",", ":")).encode() + b"\n"
        tee_proc.stdin.write(frame)
        tee_proc.stdin.flush()
        status_path = framedir / "tee-status.json"
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if status_path.exists():
                try:
                    s = json.loads(status_path.read_text())
                    if s.get("updated_seq", 0) >= 1:
                        break
                except (json.JSONDecodeError, ValueError):
                    pass
            time.sleep(0.1)
        tee_proc.send_signal(sig.SIGTERM)
        tee_proc.wait(timeout=10)
        tee_proc.stdin.close()
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 70
        status = json.loads(status_path.read_text())
        assert status["exit_code"] == 70
        assert status["write_errors"] == ["terminated: SIGTERM"]
        assert status["final"] is True


# ---------------------------------------------------------------------------
# F5: forward OSError on stdout
# ---------------------------------------------------------------------------
class TestForwardOSErrorStdout:
    def test_forward_enospc_stdout_devfull(self, tmp_path):
        if not os.path.exists("/dev/full"):
            pytest.skip("/dev/full not available")
        agent_code = textwrap.dedent("""\
            import sys, json
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            sys.exit(0)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        devfull = open("/dev/full", "wb")
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=devfull,
                                    stderr=subprocess.PIPE, env=env)
        devfull.close()
        input_bytes = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                                 separators=(",", ":")).encode() + b"\n"
        tee_proc.stdin.write(input_bytes)
        tee_proc.stdin.close()
        tee_proc.wait(timeout=15)
        tee_proc.stderr.close()
        assert tee_proc.returncode == 70
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["write_errors"] == ["forward a2c: [Errno 28] No space left on device"]


# ---------------------------------------------------------------------------
# F9: agent exits without consuming stdin -> exit 70
# ---------------------------------------------------------------------------
class TestConsumeToEofRequired:
    def test_agent_exits_without_consuming_stdin_exit_70(self, tmp_path):
        agent_code = textwrap.dedent("""\
            import os, sys, json
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp, separators=(",", ":")) + "\\n")
            sys.stdout.flush()
            os._exit(0)
        """)
        lines = []
        for i in range(100):
            lines.append(json.dumps({"jsonrpc": "2.0", "id": i, "method": "m", "params": {}},
                                    separators=(",", ":")) + "\n")
        result = _run_tee(tmp_path, agent_code, "".join(lines).encode("utf-8"), timeout=30)
        assert result["proc"].returncode == 70
        status = json.loads((result["framedir"] / "tee-status.json").read_text())
        assert status["drained"] is False
        assert status["write_errors"] == ["forward c2a: BrokenPipeError"]
        assert status["recorded_c2a"] == 100
        assert status["forwarded_c2a"] < status["recorded_c2a"]


# ---------------------------------------------------------------------------
# F10: stderr on failed tee-status.json write
# ---------------------------------------------------------------------------
class TestStatusWriteFailureStderr:
    def test_status_write_failure_prints_stderr(self, tmp_path):
        if not os.path.exists("/dev/full"):
            pytest.skip("/dev/full not available")
        framedir = tmp_path / "frames"
        framedir.mkdir()
        # Pre-create tee-status.json as symlink to /dev/full — the atomic
        # temp-file write still works (the .tmp file is a regular file) but
        # os.replace onto /dev/full fails.  Pre-create the .tmp symlink too.
        os.symlink("/dev/full", str(framedir / "tee-status.json"))
        os.symlink("/dev/full", str(framedir / ".tee-status.tmp"))
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\nimport sys\nsys.stdin.read()\nsys.exit(0)\n" % sys.executable)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run([sys.executable, str(TEE)], input=b"",
                              capture_output=True, env=env, timeout=15)
        stderr = proc.stderr.decode("utf-8", errors="replace")
        assert "frame_tee: failed to write tee-status.json:" in stderr


# ---------------------------------------------------------------------------
# A21d: SIGKILL leaves non-final status; clean exit has final=True;
#       no torn JSON under concurrent reads
# ---------------------------------------------------------------------------
class TestRunningStatus:
    def test_sigkill_leaves_nonfinal_status(self, tmp_path):
        """A21d: SIGKILL the tee after N frames -> status has final=False."""
        agent_code = textwrap.dedent("""\
            import sys, json, time
            for i in range(200):
                f = {"jsonrpc": "2.0", "method": "d", "params": {"i": i}}
                sys.stdout.write(json.dumps(f, separators=(",", ":")) + "\\n")
                sys.stdout.flush()
                time.sleep(0.02)
            sys.exit(0)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        tee_proc.stdin.close()
        status_path = framedir / "tee-status.json"
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if status_path.exists():
                try:
                    s = json.loads(status_path.read_text())
                    if s.get("forwarded_a2c", 0) >= 5:
                        break
                except (json.JSONDecodeError, ValueError):
                    pass
            time.sleep(0.05)
        tee_proc.send_signal(sig.SIGKILL)
        tee_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        status = json.loads(status_path.read_text())
        assert status["final"] is False
        assert status["agent_returncode"] is None
        assert status["exit_code"] is None
        assert status["updated_seq"] > 0
        assert status["forwarded_a2c"] == status["recorded_a2c"]
        assert set(status.keys()) == STATUS_KEYS

    def test_clean_exit_has_final_true(self, tee_run):
        """A21d: clean exit -> final=True, agent_returncode and exit_code set."""
        status = json.loads((tee_run["framedir"] / "tee-status.json").read_text())
        assert status["final"] is True
        assert status["agent_returncode"] == 42
        assert status["exit_code"] == 42
        assert status["updated_seq"] > 0
        assert status["updated_utc"].endswith("Z")

    def test_rewrite_is_atomic(self, tmp_path):
        """A21d: no torn JSON under a concurrent reader."""
        agent_code = textwrap.dedent("""\
            import sys, json
            for i in range(500):
                f = {"jsonrpc": "2.0", "method": "d", "params": {"i": i}}
                sys.stdout.write(json.dumps(f, separators=(",", ":")) + "\\n")
                sys.stdout.flush()
            sys.exit(0)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        tee_proc.stdin.close()
        status_path = framedir / "tee-status.json"
        torn = 0
        reads = 0
        while tee_proc.poll() is None:
            if status_path.exists():
                try:
                    json.loads(status_path.read_text())
                    reads += 1
                except (json.JSONDecodeError, ValueError):
                    torn += 1
            time.sleep(0.001)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert reads > 0, "never read a valid status"
        assert torn == 0, f"{torn} torn reads out of {reads + torn}"
