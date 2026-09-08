"""proofs/S0-01/tools/frame_tee.py v2 -- stdio proxy with timeline, identity, directional files.

Tests the v2 tee contract: timestamps + seq inside the lock, os.read stdin pump,
bounded stdout join, signal exit codes, raw_b64 for non-JSON, tee_pid in identity,
A21d running-status rewrites (final/non-final, updated_seq, atomic writes).
"""
from __future__ import annotations

import ast
import base64
import datetime
import hashlib
import io
import json
import os
import re
import signal as sig
import subprocess
import sys
import textwrap
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEE = ROOT / "proofs" / "S0-01" / "tools" / "frame_tee.py"

# F16: import the pinned key tuple from pins.py
sys.path.insert(0, str(ROOT / "proofs" / "S0-01"))
from pins import PINNED_TEE_STATUS_KEYS  # noqa: E402

# Import the canonical shutdown clause from the tee (item 1: one place that can be wrong)
sys.path.insert(0, str(ROOT / "proofs" / "S0-01" / "tools"))
from frame_tee import PINNED_SHUTDOWN_CLAUSE, _reread_interpreter  # noqa: E402

# AF-AP-59: import the anti-pattern screen from the edit-snapshot hook (never edit it)
import importlib.util as _ilu
_es_spec = _ilu.spec_from_file_location("edit_snapshot", str(ROOT / ".claude" / "hooks" / "edit-snapshot.py"))
_es_mod = _ilu.module_from_spec(_es_spec)
_es_spec.loader.exec_module(_es_mod)
AP_SCREEN = _es_mod.AP_SCREEN + _es_mod.TEST_SCREEN

# The vendored oracle (READ-ONLY; sha256 checked by the oracle test)
VENDORED_ACP_RS = ROOT / "proofs" / "S0-01" / "vendor" / "buzz-acp" / "acp.rs"
VENDORED_ACP_RS_SHA256 = "44e82861763694d2b82d02b15ee100ffd6c78874a2b2282865e6656c539c38f1"

# VERIFY-B5h F1/F12/F13: buzz-acp's shutdown bound is stated ONCE, in
# frame_tee.py (PINNED_SHUTDOWN_CLAUSE plus the module docstring that carries it
# verbatim; the oracle test joins them to the vendored source by equality).
# Every other site carries this reference and no shutdown prose of its own.
CLAUSE_REF = "buzz-acp's shutdown bound: see PINNED_SHUTDOWN_CLAUSE in frame_tee.py"

# Venue declaration (SWEEP-tests 10.5), mirroring test_real_leg_corpus_declared
# in tests/test_s0_01_check_acp_conformance.py.
_VENUE = os.environ.get("S0_01_VENUE", "sandbox")
# The eight write-failure proofs and the declaration test read the SAME name,
# so repointing it fails the declaration instead of silently skipping eight.
_DEV_FULL = "/dev/full"

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


def _kill_own_grandchild(framedir):
    """Kill THIS test's grandchild from its pid file, with identity verification.

    RETURNS THE BRANCH IT TOOK, so each caller states which one its own shape
    can produce (VERIFY-B5h F4 -- a silent skip is what hid F-B5g-8):
    - ``"live"``: /proc/<pid>/cmdline names our grandchild ("time.sleep") ->
      SIGKILL it and wait for it to go.
    - ``"gone"``: already fully reaped (FileNotFoundError / ProcessLookupError),
      or a zombie (stat state Z) with an empty cmdline, or it raced us between
      the identity read and the kill (ProcessLookupError from os.kill -- the
      benign race, which IS the success condition).
    A LIVE process with a foreign cmdline is a hard failure -- refuse to kill.
    A PermissionError on the identity read is also a hard failure: an
    unidentifiable pid is never signalled (fail-closed).
    Pid reuse is unreachable here (pid_max 32768, ~5 pids/s measured vs the
    ~728/s needed for a full lap), and the zombie window (~0.97 s) is the
    reachable direction.
    """
    gc_pid_path = framedir / "grandchild.pid"
    assert gc_pid_path.exists(), "agent never wrote grandchild.pid"
    gc_pid = int(gc_pid_path.read_text().strip())
    gone_or_foreign = False
    try:
        cmdline = open("/proc/%d/cmdline" % gc_pid).read().replace("\0", " ")
    except (FileNotFoundError, ProcessLookupError):
        gone_or_foreign = True  # fully reaped
    except PermissionError:
        raise AssertionError("cannot identify pid %d -- not killing" % gc_pid)
    else:
        if "time.sleep" not in cmdline:
            # Empty cmdline on a zombie = our grandchild, already dead
            try:
                st = open("/proc/%d/stat" % gc_pid).read().split()[2]
            except (OSError, IOError, IndexError):
                st = "gone"
            assert st in ("Z", "gone"), (
                "refusing to kill a foreign pid %d (cmdline: %s, state: %s)"
                % (gc_pid, cmdline, st))
            gone_or_foreign = True
    if gone_or_foreign:
        return "gone"
    try:
        os.kill(gc_pid, sig.SIGKILL)
    except ProcessLookupError:
        return "gone"  # raced us to exit between the identity read and the kill
    deadline_gc = time.monotonic() + 2
    while time.monotonic() < deadline_gc:
        try:
            st = open("/proc/%d/stat" % gc_pid).read().split()
            if len(st) >= 3 and st[2] == "Z":
                break
        except (OSError, IOError):
            break
        time.sleep(0.1)
    gone = True
    try:
        st = open("/proc/%d/stat" % gc_pid).read().split()
        if len(st) >= 3 and st[2] != "Z":
            gone = False
    except (OSError, IOError):
        pass
    assert gone, "grandchild pid %d still alive after kill" % gc_pid
    return "live"


def _read_with_deadline(pipe, deadline_s):
    """Read ONE line from a tee pipe, bounded by a deadline (VERIFY-B5h F9).

    An agent that dies without writing leaves the tee with nothing to send, and
    the tee cannot exit while the test still holds its stdin: a bare
    ``readline()`` there blocks the test forever (reproduced with the wchan/fd
    table -- tee main thread in hrtimer_nanosleep, c2a reader in anon_pipe_read,
    test fd == tee fd 0).  The reader runs in a daemon thread joined with a
    deadline, so the wedge becomes a returned ``None`` instead of a hang.
    """
    box = {}

    def _rd():
        try:
            box["line"] = pipe.readline()
        except (OSError, ValueError):
            box["line"] = b""

    th = threading.Thread(target=_rd, daemon=True)
    th.start()
    th.join(deadline_s)
    if th.is_alive():
        return None
    return box.get("line")


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

    # SWEEP-tests 1.1/1.2: absence is a FAILURE, never a default.  The four
    # defaults ([] / b"" / b"" / {}) let seven tests pass while the tee had
    # produced no evidence at all (measured: R19 wiped the artifacts and they
    # still passed, vacuously).
    tl_path = framedir / "timeline.jsonl"
    assert tl_path.is_file(), "tee wrote no timeline.jsonl"
    timeline_lines = []
    for raw in tl_path.read_bytes().split(b"\n"):
        if raw.strip():
            timeline_lines.append(json.loads(raw))

    c2a_path = framedir / "frames-client-to-agent.jsonl"
    assert c2a_path.is_file(), "tee wrote no frames-client-to-agent.jsonl"
    c2a_bytes = c2a_path.read_bytes()

    a2c_path = framedir / "frames-agent-to-client.jsonl"
    assert a2c_path.is_file(), "tee wrote no frames-agent-to-client.jsonl"
    a2c_bytes = a2c_path.read_bytes()

    id_path = framedir / "runtime-identity.json"
    assert id_path.is_file(), "tee wrote no runtime-identity.json"
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
        """F1: a client frame the agent can no longer receive must still be RECORDED, and the tee
        must exit 70 -- never 0 with the frame missing.

        Deterministic by construction (CI on ec270f3 caught the racy version: on a fast runner the
        tee had forwarded all 50 frames into the pipe before the agent exited, so nothing broke and
        it exited 0). The agent CLOSES ITS STDIN BEFORE it answers frame 1, so the moment the client
        sees the answer the agent's read end is already gone: every later forward hits EPIPE
        whatever the scheduling, while the recorder must keep going."""
        agent_code = textwrap.dedent("""\
            import os, sys, json, time
            line = sys.stdin.readline()
            os.close(0)                       # the precondition, established BEFORE the handshake
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            time.sleep(1.0)                   # lifetime is irrelevant to the outcome; keeps the run short
            os._exit(0)
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
        frame1 = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                             "params": {}}, separators=(",", ":")) + "\n"
        late_frames = [json.dumps({"jsonrpc": "2.0", "id": i, "method": "late", "params": {}},
                                  separators=(",", ":")) + "\n" for i in range(2, 51)]
        tee_proc = subprocess.Popen([sys.executable, str(TEE)], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        try:
            tee_proc.stdin.write(frame1.encode()); tee_proc.stdin.flush()
            answer = _read_with_deadline(tee_proc.stdout, 30)
            assert answer, "no handshake line from the tee within 30 s"
            assert json.loads(answer)["id"] == 1
            tee_proc.stdin.write("".join(late_frames).encode())
            _, stderr = tee_proc.communicate(timeout=30)   # flushes + closes stdin (EOF), reaps the tee
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
        c2a = (framedir / "frames-client-to-agent.jsonl").read_bytes()
        assert c2a.count(b'"method":"late"') == 49        # every late frame RECORDED
        assert tee_proc.returncode == 70                 # and the loss is LOUD, never a silent 0
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["recorded_c2a"] == 50
        assert status["forwarded_c2a"] < status["recorded_c2a"]
        assert status["drained"] is False
        assert status["write_errors"] == ["forward c2a: BrokenPipeError"]
        assert b"Fatal Python error" not in stderr

    def test_late_frame_agent_stdin_closed_before_handshake(self, tmp_path):
        """F7/R1: agent closes stdin BEFORE the handshake, client sends
        the late frame AFTER reading the handshake response, then closes
        stdin (client EOF).  The drain-to-EOF records the frame.
        Deterministic: the forward hits EPIPE whatever the scheduling.
        (Renamed from test_late_frame_after_reap_with_client_holding_stdin:
        the agent is alive during the late frame -- no actual reap.)"""
        agent_code = textwrap.dedent("""\
            import os, sys, json, time
            line = sys.stdin.readline()
            os.close(0)                       # precondition: stdin closed BEFORE handshake
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            time.sleep(1.0)
            os._exit(0)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir(parents=True, exist_ok=True)
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        frame1 = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                             "params": {}}, separators=(",", ":")) + "\n"
        late_frame = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "late",
                                 "params": {}}, separators=(",", ":")) + "\n"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        try:
            tee_proc.stdin.write(frame1.encode())
            tee_proc.stdin.flush()
            answer = _read_with_deadline(tee_proc.stdout, 30)
            assert answer, "no handshake line from the tee within 30 s"
            assert json.loads(answer)["id"] == 1
            tee_proc.stdin.write(late_frame.encode())
            tee_proc.stdin.flush()
            # R1: close stdin (client EOF) so the drain-to-EOF completes
            tee_proc.stdin.close()
            tee_proc.wait(timeout=30)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        c2a = (framedir / "frames-client-to-agent.jsonl").read_bytes()
        assert c2a.count(b'"method":"late"') == 1
        assert tee_proc.returncode == 70
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["recorded_c2a"] == 2
        assert status["forwarded_c2a"] < status["recorded_c2a"]
        assert status["drained"] is False
        assert status["stdin_reader_done"] is True
        assert status["write_errors"] == ["forward c2a: BrokenPipeError"]

    def test_agent_stdin_closed_before_handshake_exit_code(self, tmp_path):
        """F7/F2: agent closes stdin BEFORE answering; client sends frame 2
        AFTER the handshake, then closes stdin (client EOF).  Deterministic:
        rc 70, frame 2 recorded.  (Renamed from test_tee_exits_cleanly_with_agent_code:
        the agent is alive during the late frame -- no actual reap.)"""
        agent_code = textwrap.dedent("""\
            import os, sys, json, time
            line = sys.stdin.readline()
            os.close(0)                       # precondition: stdin closed BEFORE handshake
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            time.sleep(1.0)
            os._exit(42)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir(parents=True, exist_ok=True)
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        frame1 = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                             "params": {}}, separators=(",", ":")) + "\n"
        frame2 = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "late",
                             "params": {}}, separators=(",", ":")) + "\n"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        try:
            tee_proc.stdin.write(frame1.encode())
            tee_proc.stdin.flush()
            answer = _read_with_deadline(tee_proc.stdout, 30)
            assert answer, "no handshake line from the tee within 30 s"
            assert json.loads(answer)["id"] == 1
            tee_proc.stdin.write(frame2.encode())
            tee_proc.stdin.flush()
            # R1: close stdin (client EOF) so the drain-to-EOF completes
            tee_proc.stdin.close()
            tee_proc.wait(timeout=30)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 70
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["recorded_c2a"] == 2
        assert status["write_errors"] == ["forward c2a: BrokenPipeError"]


# ---------------------------------------------------------------------------
class TestGrandchildStdout:
    def test_grandchild_keeps_tee_alive(self, tmp_path):
        """B5e: grandchild holds the agent's stdout (sleeps 30 s).
        Symmetric drain-to-EOF: the tee stays alive past the agent's exit.
        After confirming the handshake, verify the tee is still running at 3 s,
        then SIGTERM it.  Exit 70, non-final."""
        agent_code = textwrap.dedent("""\
            import subprocess, sys, json, os
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            gc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
            fd = os.environ.get("S0_01_FRAMEDIR", "")
            if fd:
                open(os.path.join(fd, "grandchild.pid"), "w").write(str(gc.pid))
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
        try:
            tee_proc.stdin.write(input_bytes)
            tee_proc.stdin.close()
            def _drain():
                while True:
                    chunk = tee_proc.stdout.read(65536)
                    if not chunk:
                        break
            drainer = threading.Thread(target=_drain, daemon=True)
            drainer.start()
            status_path = framedir / "tee-status.json"
            loaded = False
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if status_path.exists():
                    try:
                        s = json.loads(status_path.read_text())
                        if s.get("recorded_a2c", 0) >= 1:
                            loaded = True
                            break
                    except (json.JSONDecodeError, ValueError):
                        pass
                time.sleep(0.1)
            assert loaded, "no a2c frame recorded before the liveness window"
            time.sleep(3)
            assert tee_proc.poll() is None, "tee exited early"
            tee_proc.send_signal(sig.SIGTERM)
            tee_proc.wait(timeout=10)
            drainer.join(timeout=5)
        finally:
            try:
                if tee_proc.poll() is None:
                    tee_proc.kill()
                    tee_proc.wait(timeout=5)
                # F-B5e-12 / F-B5g-4: kill THIS test's grandchild with identity.
                # VERIFY-B5h F4: the grandchild is still sleeping here, so this
                # site takes the LIVE branch and says so.
                assert _kill_own_grandchild(framedir) == "live"
            finally:
                tee_proc.stdout.close()
                tee_proc.stderr.close()
        assert tee_proc.returncode == 70


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

    def _run_with_agent(self, tmp_path, agent_value, framedir_name="frames"):
        framedir = tmp_path / framedir_name
        framedir.mkdir()
        env = {k: v for k, v in os.environ.items()
               if k not in ("S0_01_FRAMEDIR", "S0_01_AGENT")}
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_value)
        proc = subprocess.run([sys.executable, str(TEE)], input=b"",
                              capture_output=True, env=env, timeout=10)
        return proc, framedir

    def test_empty_agent(self, tmp_path):
        """SWEEP-prod #13: S0_01_AGENT was checked for None but not for empty,
        so "" reached Popen and crashed with an uncaught PermissionError,
        rc 1, and tee-status.json was NEVER written.  Now it is the same
        fail-closed rc 64 the framedir domain already had."""
        proc, framedir = self._run_with_agent(tmp_path, "")
        assert proc.returncode == 64
        assert proc.stderr.decode().strip() == "frame_tee: S0_01_AGENT is empty"
        assert b"Traceback" not in proc.stderr
        assert list(framedir.iterdir()) == []

    def test_non_executable_agent(self, tmp_path):
        """A regular file without an execute bit is not an agent: rc 64,
        named, no traceback (the PIN raised PermissionError, rc 1).

        The FIFO shape is here too (VERIFY-B5i VB-F11: the rc-64 domain was
        reported for it with no committed test).  A FIFO can carry an execute
        bit, so it is os.access(X_OK)-true and only the isfile() half of the
        guard rejects it -- the shape that would survive if the guard were
        weakened to a permission check."""
        plain = tmp_path / "plain.txt"
        plain.write_text("not executable\n")
        proc, framedir = self._run_with_agent(tmp_path, plain)
        assert proc.returncode == 64
        assert proc.stderr.decode().strip() == (
            "frame_tee: S0_01_AGENT is not an executable file: %s" % plain)
        assert b"Traceback" not in proc.stderr
        assert list(framedir.iterdir()) == []

        fifo = tmp_path / "agent.fifo"
        os.mkfifo(str(fifo), 0o755)
        assert os.access(str(fifo), os.X_OK), (
            "the FIFO has no execute bit, so this case would not exercise the "
            "isfile() half of the guard")
        proc, framedir = self._run_with_agent(tmp_path, fifo,
                                              framedir_name="frames_fifo")
        assert proc.returncode == 64
        assert proc.stderr.decode().strip() == (
            "frame_tee: S0_01_AGENT is not an executable file: %s" % fifo)
        assert b"Traceback" not in proc.stderr
        assert list(framedir.iterdir()) == []

    def test_directory_agent(self, tmp_path):
        """A directory at the agent path: rc 64, named, no traceback."""
        d = tmp_path / "adir"
        d.mkdir()
        proc, framedir = self._run_with_agent(tmp_path, d)
        assert proc.returncode == 64
        assert proc.stderr.decode().strip() == (
            "frame_tee: S0_01_AGENT is not an executable file: %s" % d)
        assert b"Traceback" not in proc.stderr

    def test_agent_that_cannot_be_spawned(self, tmp_path):
        """The Popen arm of the same domain: an executable script whose
        interpreter does not exist passes every static check and fails in
        execve.  rc 64 with a named line, not an uncaught OSError."""
        script = tmp_path / "badshebang.sh"
        script.write_text("#!/nonexistent/interpreter\necho hi\n")
        script.chmod(0o755)
        proc, framedir = self._run_with_agent(tmp_path, script)
        assert proc.returncode == 64
        err = proc.stderr.decode().strip()
        assert err.startswith("frame_tee: cannot spawn S0_01_AGENT %s: " % script), err
        assert b"Traceback" not in proc.stderr
        assert list(framedir.iterdir()) == []


def test_dev_full_declared():
    """SWEEP-tests 10.5: eight write-failure proofs in this file skip
    themselves when /dev/full is absent, so a venue with a restricted /dev
    retires every ENOSPC proof silently and green.  The venue declares
    instead, mirroring test_real_leg_corpus_declared in
    tests/test_s0_01_check_acp_conformance.py: in sandbox and pc /dev/full
    MUST exist; ci skips by declaration."""
    assert _VENUE in ("ci", "sandbox", "pc"), (
        "S0_01_VENUE=%r is not a known venue" % _VENUE)
    if _VENUE in ("sandbox", "pc"):
        assert os.path.exists(_DEV_FULL), (
            "S0_01_VENUE=%s but /dev/full is absent -- the tee's write-failure "
            "proofs cannot run in this venue and would skip green" % _VENUE)


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
# P2 / A21d: tee-status.json -- drain tracking, exit code discipline, running status
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
        """F16: key SET matches the pinned tuple."""
        status = json.loads((tee_run["framedir"] / "tee-status.json").read_text())
        assert set(status.keys()) == set(PINNED_TEE_STATUS_KEYS)

    def test_status_keys_order_matches_pin(self, tee_run):
        """F16: key ORDER matches the pinned tuple."""
        status = json.loads((tee_run["framedir"] / "tee-status.json").read_text())
        assert tuple(status.keys()) == PINNED_TEE_STATUS_KEYS

    def test_agent_burst_drained(self, tmp_path):
        """F12/F-PC-2: agent emits 1000 small frames; assert all drained.
        Reads tee stdout concurrently (no pipe-size assumption)."""
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
        try:
            tee_proc.stdin.close()

            def _drain():
                while True:
                    chunk = tee_proc.stdout.read(65536)
                    if not chunk:
                        break
            drainer = threading.Thread(target=_drain, daemon=True)
            drainer.start()
            tee_proc.wait(timeout=30)
            drainer.join(timeout=5)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
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
        """Client NEVER reads a2c -> the a2c pump blocks on the full pipe;
        after the agent dies the tee stays alive (symmetric drain-to-EOF on
        a2c).  buzz-acp's shutdown bound: see PINNED_SHUTDOWN_CLAUSE in
        frame_tee.py; that leg's evidence is its last RUNNING status (A21d).
        The path exercised here is the tee's own operator/systemd TERM: exit
        70, non-final, write_errors carries the single terminated entry."""
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
        try:
            tee_proc.stdin.close()
            # Wait for some a2c frames to be recorded
            status_path = framedir / "tee-status.json"
            loaded = False
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if status_path.exists():
                    try:
                        s = json.loads(status_path.read_text())
                        if s.get("recorded_a2c", 0) >= 1:
                            loaded = True
                            break
                    except (json.JSONDecodeError, ValueError):
                        pass
                time.sleep(0.1)
            assert loaded, "no a2c frame recorded before SIGTERM"
            # Symmetric drain: tee stays alive (pump blocked on full pipe).
            tee_proc.send_signal(sig.SIGTERM)
            tee_proc.wait(timeout=10)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 70
        status = json.loads(status_path.read_text())
        assert status["final"] is False
        assert status["write_errors"] == ["terminated: SIGTERM"]

    def test_write_failure_exit_70(self, tmp_path):
        if not os.path.exists(_DEV_FULL):
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
        os.symlink(_DEV_FULL, str(framedir / "timeline.jsonl"))
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
            "timeline c2a: [Errno 28] No space left on device",
            "timeline a2c: [Errno 28] No space left on device",
        ]

    def test_grandchild_straggler_recorded(self, tmp_path):
        """F3/B5e: grandchild inherits the agent's stdout, writes one frame
        6 s after the agent exits, then closes.  Symmetric drain-to-EOF:
        the frame IS recorded in the timeline and a2c file, forwarded to the
        client, rc 0, drained true, write_errors [].
        Kills a2c stall timeouts shorter than the 6 s straggler gap (0 and
        5 s); the 30 s case is killed by test_drain_loops_have_no_break_or_timeout."""
        agent_code = textwrap.dedent("""\
            import subprocess, sys, json, os
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            subprocess.Popen([sys.executable, "-c",
                "import sys, time, json; time.sleep(6); "
                "sys.stdout.write(json.dumps({'jsonrpc':'2.0','method':'late_gc','params':{}}) + chr(10)); "
                "sys.stdout.flush()"])
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
        try:
            tee_proc.stdin.write(input_bytes)
            tee_proc.stdin.close()
            # Drain stdout concurrently
            def _drain():
                while True:
                    chunk = tee_proc.stdout.read(65536)
                    if not chunk:
                        break
            drainer = threading.Thread(target=_drain, daemon=True)
            drainer.start()
            tee_proc.wait(timeout=30)
            drainer.join(timeout=5)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 0
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["final"] is True
        assert status["drained"] is True
        assert status["write_errors"] == []
        assert status["exit_code"] == 0
        assert status["recorded_a2c"] == 2  # handshake + late_gc
        assert status["forwarded_a2c"] == 2
        # The late frame must be in the timeline and the a2c file
        tl = (framedir / "timeline.jsonl").read_bytes()
        a2c = (framedir / "frames-agent-to-client.jsonl").read_bytes()
        assert b"late_gc" in tl, "late grandchild frame NOT in timeline"
        assert b"late_gc" in a2c, "late grandchild frame NOT in a2c file"

    def test_grandchild_never_closes_sigterm_required(self, tmp_path):
        """F3/B5e: grandchild holds the agent's stdout forever (never closes).
        Symmetric drain-to-EOF: the tee stays alive.  buzz-acp's shutdown
        bound: see PINNED_SHUTDOWN_CLAUSE in frame_tee.py; that leg's evidence
        is its last RUNNING status (A21d).  The path exercised here is the
        tee's own operator/systemd TERM.
        Assert the tee is still alive after the 15-second hold, then signal it
        -> rc 70, non-final, write_errors carries the single terminated entry."""
        agent_code = textwrap.dedent("""\
            import subprocess, sys, json, os
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            gc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
            fd = os.environ.get("S0_01_FRAMEDIR", "")
            if fd:
                open(os.path.join(fd, "grandchild.pid"), "w").write(str(gc.pid))
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
        try:
            tee_proc.stdin.write(input_bytes)
            tee_proc.stdin.close()
            # Drain stdout concurrently
            def _drain():
                while True:
                    chunk = tee_proc.stdout.read(65536)
                    if not chunk:
                        break
            drainer = threading.Thread(target=_drain, daemon=True)
            drainer.start()
            # Wait for the tee to process the handshake
            status_path = framedir / "tee-status.json"
            loaded = False
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if status_path.exists():
                    try:
                        s = json.loads(status_path.read_text())
                        if s.get("recorded_a2c", 0) >= 1:
                            loaded = True
                            break
                    except (json.JSONDecodeError, ValueError):
                        pass
                time.sleep(0.1)
            assert loaded, "no a2c frame recorded before the liveness window"
            # The tee must be alive at 15 s (grandchild holds the pipe)
            time.sleep(15)
            assert tee_proc.poll() is None, "tee exited before 15 s"
            # SIGTERM it
            tee_proc.send_signal(sig.SIGTERM)
            tee_proc.wait(timeout=10)
            drainer.join(timeout=5)
        finally:
            try:
                if tee_proc.poll() is None:
                    tee_proc.kill()
                    tee_proc.wait(timeout=5)
                # F-B5e-12 / F-B5g-4: kill THIS test's grandchild with identity.
                # VERIFY-B5h F4: the grandchild is still sleeping here, so this
                # site takes the LIVE branch and says so.
                assert _kill_own_grandchild(framedir) == "live"
            finally:
                tee_proc.stdout.close()
                tee_proc.stderr.close()
        assert tee_proc.returncode == 70
        status = json.loads(status_path.read_text())
        assert status["final"] is False
        assert status["write_errors"] == ["terminated: SIGTERM"]

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

    def test_bounded_write_errors_dedup(self, tmp_path):
        """F7: repeated directional errors produce one entry with a count."""
        if not os.path.exists(_DEV_FULL):
            pytest.skip("/dev/full not available")
        agent_code = textwrap.dedent("""\
            import sys, json
            for line in sys.stdin:
                stripped = line.strip()
                if not stripped:
                    continue
                sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":1,"result":{}}) + "\\n")
                sys.stdout.flush()
            sys.exit(0)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        os.symlink(_DEV_FULL, str(framedir / "frames-client-to-agent.jsonl"))
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        lines = []
        for i in range(5):
            lines.append(json.dumps({"jsonrpc": "2.0", "id": i, "method": "m", "params": {}},
                                    separators=(",", ":")) + "\n")
        input_bytes = "".join(lines).encode()
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        try:
            tee_proc.stdin.write(input_bytes)
            tee_proc.stdin.close()
            # Drain stdout concurrently
            def _drain():
                while True:
                    chunk = tee_proc.stdout.read(65536)
                    if not chunk:
                        break
            drainer = threading.Thread(target=_drain, daemon=True)
            drainer.start()
            tee_proc.wait(timeout=15)
            drainer.join(timeout=5)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 70
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["write_errors"] == [
            "directional c2a: [Errno 28] No space left on device (5 occurrences)",
            "directional c2a close: [Errno 28] No space left on device",
        ]

    def test_initial_status_before_first_frame(self, tmp_path):
        """F10: tee-status.json exists immediately after runtime-identity.json,
        before any frame is processed."""
        agent_code = textwrap.dedent("""\
            import sys, json, time, os
            # Wait until tee-status.json exists (it should be written before
            # the agent gets any frames)
            framedir = os.environ.get("S0_01_FRAMEDIR_CHECK", "")
            if framedir:
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    if os.path.exists(os.path.join(framedir, "tee-status.json")):
                        break
                    time.sleep(0.01)
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
        env["S0_01_FRAMEDIR_CHECK"] = str(framedir)
        input_bytes = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                  "params": {}}, separators=(",", ":")).encode() + b"\n"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        try:
            # Poll for initial status BEFORE sending any frame
            status_path = framedir / "tee-status.json"
            deadline = time.monotonic() + 10
            initial_status = None
            while time.monotonic() < deadline:
                if status_path.exists():
                    try:
                        initial_status = json.loads(status_path.read_text())
                        break
                    except (json.JSONDecodeError, ValueError):
                        pass
                time.sleep(0.01)
            # NOW send the frame
            tee_proc.stdin.write(input_bytes)
            tee_proc.stdin.close()
            tee_proc.wait(timeout=15)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert initial_status is not None, "tee-status.json never appeared before first frame"
        assert initial_status["updated_seq"] == 0
        assert initial_status["recorded_c2a"] == 0
        assert initial_status["recorded_a2c"] == 0
        assert initial_status["forwarded_c2a"] == 0
        assert initial_status["forwarded_a2c"] == 0
        assert initial_status["final"] is False
        assert set(initial_status.keys()) == set(PINNED_TEE_STATUS_KEYS)


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
        try:
            tee_proc.stdout.close()
            tee_proc.stdin.close()
            tee_proc.wait(timeout=180)
            reader_proc.wait(timeout=60)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
            if reader_proc.poll() is None:
                reader_proc.kill()
                reader_proc.wait(timeout=5)
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
        if not os.path.exists(_DEV_FULL):
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
        os.symlink(_DEV_FULL, str(framedir / target_file))
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
        assert status["write_errors"] == [
            "directional %s: [Errno 28] No space left on device" % direction,
            "directional %s close: [Errno 28] No space left on device" % direction,
        ]

    def test_c2a_directional_enospc_eof_agent_exits_70(self, tmp_path):
        """F3: unwritable c2a directional with EOF-consuming agent must not hang;
        exits 70 within a bounded wait."""
        if not os.path.exists(_DEV_FULL):
            pytest.skip("/dev/full not available")
        agent_code = textwrap.dedent("""\
            import sys
            sys.stdin.read()
            sys.exit(0)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        os.symlink(_DEV_FULL, str(framedir / "frames-client-to-agent.jsonl"))
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
                              capture_output=True, env=env, timeout=15)
        assert proc.returncode == 70
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["write_errors"] == [
            "directional c2a: [Errno 28] No space left on device",
            "directional c2a close: [Errno 28] No space left on device",
        ]
        assert status["stdin_reader_done"] is True

    def test_a2c_directional_close_error_recorded(self, tmp_path):
        """F19: a2c pump finally records the directional close error."""
        if not os.path.exists(_DEV_FULL):
            pytest.skip("/dev/full not available")
        agent_code = textwrap.dedent("""\
            import sys, json
            line = sys.stdin.readline()
            for i in range(3):
                sys.stdout.write('{"jsonrpc":"2.0","id":%d,"result":{}}\\n' % i)
                sys.stdout.flush()
            sys.exit(0)
        """)
        framedir = tmp_path / "frames"
        framedir.mkdir()
        os.symlink(_DEV_FULL, str(framedir / "frames-agent-to-client.jsonl"))
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
                              capture_output=True, env=env, timeout=15)
        assert proc.returncode == 70
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["write_errors"] == [
            "directional a2c: [Errno 28] No space left on device (3 occurrences)",
            "directional a2c close: [Errno 28] No space left on device",
        ]


# ---------------------------------------------------------------------------
class TestStdinReaderDoneValue:
    def test_stdin_reader_done_true_on_clean_exit(self, tee_run):
        status = json.loads((tee_run["framedir"] / "tee-status.json").read_text())
        assert status["stdin_reader_done"] is True

    def test_stdin_reader_done_false_when_client_never_closes(self, tmp_path):
        """R1/F8: stdin never closed -> tee stays alive (drain-to-EOF).
        Proves LIVENESS: gate on recorded_a2c >= 1 and stdin_reader_done is
        False, then sleep out the 15-second liveness window and assert the tee
        is still alive (poll is None) BEFORE it is signalled.  buzz-acp's shutdown bound: see
        PINNED_SHUTDOWN_CLAUSE in frame_tee.py; that leg's evidence is its last
        RUNNING status (A21d).  The path exercised here is the tee's own
        operator/systemd TERM.  Exit 70, stdin_reader_done False."""
        agent_code = textwrap.dedent("""\
            import sys, json
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp, separators=(",", ":")) + "\\n")
            sys.stdout.flush()
            sys.exit(0)
        """)
        helper = tmp_path / "holder.py"
        helper.write_text("import time\ntime.sleep(120)\n")
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
        try:
            # F8: gate on stdin_reader_done is False AND recorded_a2c >= 1
            status_path = framedir / "tee-status.json"
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if status_path.exists():
                    try:
                        s = json.loads(status_path.read_text())
                        if (s.get("stdin_reader_done") is False
                                and s.get("recorded_a2c", 0) >= 1):
                            break
                    except (json.JSONDecodeError, ValueError):
                        pass
                time.sleep(0.1)
            # F8: the tee MUST be alive at 15 s (client never closed stdin)
            time.sleep(15)
            assert tee_proc.poll() is None, "tee exited before 15 s liveness check"
            # R1: SIGTERM it (an operator/systemd TERM; buzz-acp
            # SIGKILLs the group instead).
            tee_proc.send_signal(sig.SIGTERM)
            tee_proc.wait(timeout=10)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
            holder_proc.kill()
            holder_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        status = json.loads(status_path.read_text())
        assert status["stdin_reader_done"] is False
        assert tee_proc.returncode == 70
        assert status["write_errors"] == ["terminated: SIGTERM"]


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
# F6: SIGTERM handler -- NON-final status
# ---------------------------------------------------------------------------
class TestSigtermHandler:
    def test_sigterm_writes_status_and_exits_70(self, tmp_path):
        """F6: SIGTERM writes a NON-final status (final=false, exit fields null),
        then exits 70.  F11: handler takes no lock."""
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
        try:
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
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdin.close()
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 70
        status = json.loads(status_path.read_text())
        assert status["final"] is False
        assert status["agent_returncode"] is None
        assert status["exit_code"] is None
        assert status["write_errors"] == ["terminated: SIGTERM"]

    def test_sigterm_no_deadlock_under_contention(self, tmp_path):
        """F11: SIGTERM during a status write must not deadlock; the tee must
        exit within a bounded time."""
        agent_code = textwrap.dedent("""\
            import sys, json
            for i in range(3000):
                f = {"jsonrpc": "2.0", "method": "d", "params": {"i": i}}
                sys.stdout.write(json.dumps(f, separators=(",", ":")) + "\\n")
                sys.stdout.flush()
            sys.stdin.read()
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
        try:
            # Drain stdout concurrently
            def _drain():
                while True:
                    chunk = tee_proc.stdout.read(65536)
                    if not chunk:
                        break
            drainer = threading.Thread(target=_drain, daemon=True)
            drainer.start()
            # Wait for some frames to be processed
            status_path = framedir / "tee-status.json"
            loaded = False
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if status_path.exists():
                    try:
                        s = json.loads(status_path.read_text())
                        if s.get("updated_seq", 0) >= 100:
                            loaded = True
                            break
                    except (json.JSONDecodeError, ValueError):
                        pass
                time.sleep(0.01)
            assert loaded, "no contention: the wait for updated_seq >= 100 timed out"
            tee_proc.send_signal(sig.SIGTERM)
            tee_proc.wait(timeout=5)  # must answer within 5s, not hang
            drainer.join(timeout=5)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdin.close()
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 70


# ---------------------------------------------------------------------------
# F5: forward OSError on stdout
# ---------------------------------------------------------------------------
class TestForwardOSErrorStdout:
    def test_forward_enospc_stdout_devfull(self, tmp_path):
        if not os.path.exists(_DEV_FULL):
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
        devfull = open(_DEV_FULL, "wb")
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=devfull,
                                    stderr=subprocess.PIPE, env=env)
        devfull.close()
        try:
            input_bytes = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                                     separators=(",", ":")).encode() + b"\n"
            tee_proc.stdin.write(input_bytes)
            tee_proc.stdin.close()
            tee_proc.wait(timeout=15)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stderr.close()
        assert tee_proc.returncode == 70
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["write_errors"] == ["forward a2c: [Errno 28] No space left on device"]


# ---------------------------------------------------------------------------
# F9: agent exits without consuming stdin -> exit 70 (deterministic)
# ---------------------------------------------------------------------------
class TestConsumeToEofRequired:
    def test_agent_exits_without_consuming_stdin_exit_70(self, tmp_path):
        """F4/F9: deterministic via the 712fe01 pattern -- agent closes its stdin
        BEFORE answering, so every later forward hits EPIPE whatever the scheduling."""
        agent_code = textwrap.dedent("""\
            import os, sys, json
            line = sys.stdin.readline()
            os.close(0)                       # precondition: stdin closed BEFORE handshake
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp, separators=(",", ":")) + "\\n")
            sys.stdout.flush()
            import time; time.sleep(1.0)
            os._exit(0)
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
        frame1 = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                             "params": {}}, separators=(",", ":")) + "\n"
        late_frames = [json.dumps({"jsonrpc": "2.0", "id": i, "method": "m", "params": {}},
                                  separators=(",", ":")) + "\n" for i in range(2, 101)]
        tee_proc = subprocess.Popen([sys.executable, str(TEE)], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        try:
            tee_proc.stdin.write(frame1.encode())
            tee_proc.stdin.flush()
            answer = _read_with_deadline(tee_proc.stdout, 30)
            assert answer, "no handshake line from the tee within 30 s"
            assert json.loads(answer)["id"] == 1
            tee_proc.stdin.write("".join(late_frames).encode())
            _, stderr = tee_proc.communicate(timeout=30)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
        assert tee_proc.returncode == 70
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["drained"] is False
        assert status["write_errors"] == ["forward c2a: BrokenPipeError"]
        assert status["recorded_c2a"] == 100
        assert status["forwarded_c2a"] < status["recorded_c2a"]


# ---------------------------------------------------------------------------
# F9: stderr on failed tee-status.json write; unwritable status -> exit 70
# ---------------------------------------------------------------------------
class TestStatusWriteFailureStderr:
    def test_status_write_failure_prints_stderr(self, tmp_path):
        if not os.path.exists(_DEV_FULL):
            pytest.skip("/dev/full not available")
        framedir = tmp_path / "frames"
        framedir.mkdir()
        os.symlink(_DEV_FULL, str(framedir / "tee-status.json"))
        os.symlink(_DEV_FULL, str(framedir / ".tee-status.tmp"))
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
        assert "tee-status.json write failure" in stderr

    def test_unwritable_status_exits_70(self, tmp_path):
        """F9: when the final tee-status.json write fails, the tee exits 70
        even on an otherwise clean run."""
        if not os.path.exists(_DEV_FULL):
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
        os.symlink(_DEV_FULL, str(framedir / "tee-status.json"))
        os.symlink(_DEV_FULL, str(framedir / ".tee-status.tmp"))
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
                              capture_output=True, env=env, timeout=15)
        assert proc.returncode == 70


# ---------------------------------------------------------------------------
# A21d: SIGKILL leaves non-final status; clean exit has final=True;
#       no torn JSON under concurrent reads; F5 seq consistency
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
        try:
            tee_proc.stdin.close()
            # Drain stdout concurrently
            def _drain():
                while True:
                    chunk = tee_proc.stdout.read(65536)
                    if not chunk:
                        break
            drainer = threading.Thread(target=_drain, daemon=True)
            drainer.start()
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
            drainer.join(timeout=5)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        status = json.loads(status_path.read_text())
        assert status["final"] is False
        assert status["agent_returncode"] is None
        assert status["exit_code"] is None
        assert status["updated_seq"] > 0
        # R2: on non-final snapshot, recorded - forwarded in {0, 1}
        assert 0 <= status["recorded_a2c"] - status["forwarded_a2c"] <= 1
        assert set(status.keys()) == set(PINNED_TEE_STATUS_KEYS)
        # R2: seq consistency on the surviving snapshot
        assert status["updated_seq"] == status["recorded_c2a"] + status["recorded_a2c"]
        # F11/S1: status is never AHEAD of the timeline (lag >= 0)
        tl_path = framedir / "timeline.jsonl"
        # SWEEP-tests 1.3: an absent timeline would default the lag to 0 and pass
        assert tl_path.is_file(), "tee wrote no timeline.jsonl"
        tl_last_seq = 0
        for raw in tl_path.read_bytes().split(b"\n"):
            if raw.strip():
                try:
                    e = json.loads(raw)
                    tl_last_seq = max(tl_last_seq, e.get("seq", 0))
                except (json.JSONDecodeError, ValueError):
                    pass
        assert 0 <= tl_last_seq - status["updated_seq"] <= 1, (
            "lag %d not in {0,1}: tl_last_seq=%d updated_seq=%d"
            % (tl_last_seq - status["updated_seq"], tl_last_seq, status["updated_seq"]))

    def test_clean_exit_has_final_true(self, tee_run):
        """A21d: clean exit -> final=True, agent_returncode and exit_code set."""
        status = json.loads((tee_run["framedir"] / "tee-status.json").read_text())
        assert status["final"] is True
        assert status["agent_returncode"] == 42
        assert status["exit_code"] == 42
        assert status["updated_seq"] > 0
        assert status["updated_utc"].endswith("Z")

    def test_rewrite_is_atomic(self, tmp_path):
        """R2: no torn JSON under a concurrent reader.  BIDIRECTIONAL load
        (client streams while the agent echoes) so both pumps write status
        concurrently -- kills N4 (snapshot outside lock) and D3 (no status_lock).
        F-PC-1: drains stdout concurrently to prevent pipe deadlock.
        F5: every snapshot satisfies updated_seq == recorded_c2a + recorded_a2c.
        R2: recorded_<dir> - forwarded_<dir> in {0, 1} on running snapshots."""
        n_frames = 5000
        agent_code = textwrap.dedent("""\
            import sys, json
            for line in sys.stdin:
                stripped = line.strip()
                if not stripped:
                    continue
                sys.stdout.write(line)
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
        lines = []
        for i in range(n_frames):
            lines.append(json.dumps({"jsonrpc": "2.0", "id": i, "method": "m",
                                     "params": {}}, separators=(",", ":")) + "\n")
        input_bytes = "".join(lines).encode()
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        try:
            # F-PC-1: drain stdout on a reader thread to prevent pipe deadlock
            def _drain():
                while True:
                    chunk = tee_proc.stdout.read(65536)
                    if not chunk:
                        break
            drainer = threading.Thread(target=_drain, daemon=True)
            drainer.start()
            # Feed input on a writer thread so we can spin-read the status
            def _feed():
                try:
                    tee_proc.stdin.write(input_bytes)
                    tee_proc.stdin.close()
                except (BrokenPipeError, OSError):
                    pass
            feeder = threading.Thread(target=_feed, daemon=True)
            feeder.start()
            status_path = framedir / "tee-status.json"
            torn = 0
            reads = 0
            seq_violations = 0
            fwd_violations = 0
            deadline = time.monotonic() + 60
            while tee_proc.poll() is None and time.monotonic() < deadline:
                if status_path.exists():
                    try:
                        s = json.loads(status_path.read_text())
                        reads += 1
                        # R2: seq consistency
                        if s["updated_seq"] != s["recorded_c2a"] + s["recorded_a2c"]:
                            seq_violations += 1
                        # R2: forwarded never more than 1 behind recorded (running)
                        if not s["final"]:
                            for d in ("c2a", "a2c"):
                                diff = s["recorded_%s" % d] - s["forwarded_%s" % d]
                                if diff < 0 or diff > 1:
                                    fwd_violations += 1
                    except (json.JSONDecodeError, ValueError):
                        torn += 1
                # spin with no sleep for maximum read density
            tee_proc.wait(timeout=60)
            drainer.join(timeout=5)
            feeder.join(timeout=5)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert reads > 10000, "only %d reads -- need >= 10000" % reads
        assert torn == 0, "%d torn reads out of %d" % (torn, reads + torn)
        assert seq_violations == 0, (
            "%d snapshots where updated_seq != recorded_c2a + recorded_a2c" % seq_violations)
        assert fwd_violations == 0, (
            "%d snapshots where recorded - forwarded not in {0, 1}" % fwd_violations)
        # final status: forwarded == recorded
        final = json.loads(status_path.read_text())
        assert final["final"] is True
        assert final["forwarded_c2a"] == final["recorded_c2a"]
        assert final["forwarded_a2c"] == final["recorded_a2c"]

    def test_directional_trails_timeline_after_sigkill(self, tmp_path):
        """R2/F17/N3: after SIGKILL the directional file may be one frame SHORT
        of the timeline (timeline written first), never AHEAD.  12 trials,
        BOTH directions loaded, len(results) == 12."""
        n_frames = 20000
        agent_code = textwrap.dedent("""\
            import sys, json
            for line in sys.stdin:
                stripped = line.strip()
                if not stripped:
                    continue
                sys.stdout.write(line)
                sys.stdout.flush()
            sys.exit(0)
        """)
        results = []
        for trial in range(12):
            framedir = tmp_path / ("frames_%d" % trial)
            framedir.mkdir()
            agent_script = tmp_path / ("agent_%d.py" % trial)
            agent_script.write_text("#!%s\n" % sys.executable + agent_code)
            agent_script.chmod(0o755)
            env = os.environ.copy()
            env["S0_01_FRAMEDIR"] = str(framedir)
            env["S0_01_AGENT"] = str(agent_script)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            lines = []
            for i in range(n_frames):
                lines.append(json.dumps({"jsonrpc": "2.0", "id": i, "method": "m",
                                         "params": {}}, separators=(",", ":")) + "\n")
            input_bytes = "".join(lines).encode()
            tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, env=env)
            try:
                # Drain stdout concurrently
                def _drain(p=tee_proc):
                    while True:
                        chunk = p.stdout.read(65536)
                        if not chunk:
                            break
                drainer = threading.Thread(target=_drain, daemon=True)
                drainer.start()
                # Feed input concurrently
                def _feed(p=tee_proc):
                    try:
                        p.stdin.write(input_bytes)
                        p.stdin.close()
                    except (BrokenPipeError, OSError):
                        pass
                feeder = threading.Thread(target=_feed, daemon=True)
                feeder.start()
                # Wait for some frames then SIGKILL
                status_path = framedir / "tee-status.json"
                kill_delay = 0.15 + trial * 0.05  # spread kill instants
                deadline = time.monotonic() + 15
                while time.monotonic() < deadline:
                    if status_path.exists():
                        try:
                            s = json.loads(status_path.read_text())
                            if s.get("updated_seq", 0) >= 100:
                                time.sleep(kill_delay)
                                break
                        except (json.JSONDecodeError, ValueError):
                            pass
                    time.sleep(0.01)
                tee_proc.send_signal(sig.SIGKILL)
                tee_proc.wait(timeout=5)
                drainer.join(timeout=5)
                feeder.join(timeout=5)
            finally:
                if tee_proc.poll() is None:
                    tee_proc.kill()
                    tee_proc.wait(timeout=5)
            tee_proc.stdout.close()
            tee_proc.stderr.close()
            # Count timeline entries vs directional entries, BOTH directions
            # SWEEP-tests 1.3: the tee opens all three files at startup and this
            # trial waited for updated_seq >= 100, so absence is a FAILURE here,
            # not a trial that quietly contributes nothing.
            tl_path = framedir / "timeline.jsonl"
            assert tl_path.is_file(), "trial %d: tee wrote no timeline.jsonl" % trial
            tl_c2a = tl_a2c = 0
            for raw in tl_path.read_bytes().split(b"\n"):
                if raw.strip():
                    try:
                        e = json.loads(raw)
                        if e.get("dir") == "c2a":
                            tl_c2a += 1
                        elif e.get("dir") == "a2c":
                            tl_a2c += 1
                    except (json.JSONDecodeError, ValueError):
                        pass
            c2a_path = framedir / "frames-client-to-agent.jsonl"
            a2c_path = framedir / "frames-agent-to-client.jsonl"
            assert c2a_path.is_file(), (
                "trial %d: tee wrote no frames-client-to-agent.jsonl" % trial)
            assert a2c_path.is_file(), (
                "trial %d: tee wrote no frames-agent-to-client.jsonl" % trial)
            dir_c2a = dir_a2c = 0
            for raw in c2a_path.read_bytes().split(b"\n"):
                if raw.strip():
                    dir_c2a += 1
            for raw in a2c_path.read_bytes().split(b"\n"):
                if raw.strip():
                    dir_a2c += 1
            results.append({"tl_c2a": tl_c2a, "tl_a2c": tl_a2c,
                            "dir_c2a": dir_c2a, "dir_a2c": dir_a2c})
            # directional must never LEAD the timeline in either direction
            assert dir_c2a <= tl_c2a, (
                "trial %d: dir c2a (%d) > timeline c2a (%d)" % (trial, dir_c2a, tl_c2a))
            assert dir_a2c <= tl_a2c, (
                "trial %d: dir a2c (%d) > timeline a2c (%d)" % (trial, dir_a2c, tl_a2c))
            # F-B5e-2/S1: status updated_seq is never AHEAD of the timeline
            tl_last_seq = tl_c2a + tl_a2c  # timeline entries == total seq
            sp = framedir / "tee-status.json"
            assert sp.is_file(), "trial %d: tee wrote no tee-status.json" % trial
            try:
                st = json.loads(sp.read_text())
            except (json.JSONDecodeError, ValueError):
                st = None  # torn status after SIGKILL -- not actionable
            if st is not None:
                assert 0 <= tl_last_seq - st["updated_seq"] <= 1, (
                    "trial %d: lag %d not in {0,1}: tl_last_seq=%d updated_seq=%d"
                    % (trial, tl_last_seq - st["updated_seq"], tl_last_seq, st["updated_seq"]))
        assert len(results) == 12, "expected 12 completed trials, got %d" % len(results)
        # F15: every trial must have recorded enough frames to be meaningful
        assert all(r["tl_c2a"] >= 100 for r in results), (
            "some trials had too few frames: %s" % [r["tl_c2a"] for r in results])


# ---------------------------------------------------------------------------
# R1: p9 gap sweep -- late frame recorded with gaps 1, 6, 8 s after agent death
# ---------------------------------------------------------------------------
class TestLateFrameAfterAgentDeath:
    @pytest.mark.parametrize("gap", [1, 4, 6, 8, 12])
    def test_late_frame_after_agent_death_recorded(self, tmp_path, gap):
        """R1/A2: agent writes a sentinel and exits; the test waits for the
        sentinel (genuine reap), sleeps ``gap`` seconds, sends the late frame,
        closes stdin.  The drain-to-EOF records the frame regardless of gap.
        Kills mutant A2 (the old stall-timeout drain that exits early)."""
        sentinel = tmp_path / "agent_done"
        agent_code = textwrap.dedent("""\
            import os, sys, json
            line = sys.stdin.readline()
            os.close(0)
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            open(%r, "w").write("done")
            os._exit(0)
        """ % str(sentinel))
        framedir = tmp_path / ("frames_%d" % gap)
        framedir.mkdir(parents=True, exist_ok=True)
        agent_script = tmp_path / "agent.py"
        agent_script.write_text("#!%s\n" % sys.executable + agent_code)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        frame1 = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                             "params": {}}, separators=(",", ":")) + "\n"
        late_frame = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "late",
                                 "params": {}}, separators=(",", ":")) + "\n"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        try:
            tee_proc.stdin.write(frame1.encode())
            tee_proc.stdin.flush()
            answer = _read_with_deadline(tee_proc.stdout, 30)
            assert answer, "no handshake line from the tee within 30 s"
            assert json.loads(answer)["id"] == 1
            # Wait for agent death via sentinel
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if sentinel.exists():
                    break
                time.sleep(0.05)
            assert sentinel.exists(), "agent did not write sentinel"
            time.sleep(0.5)  # margin for process exit
            # Now wait the gap -- the agent is dead
            time.sleep(gap)
            # Send the late frame AFTER the gap
            tee_proc.stdin.write(late_frame.encode())
            tee_proc.stdin.flush()
            # Close stdin (client EOF) so the drain completes
            tee_proc.stdin.close()
            tee_proc.wait(timeout=30)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        c2a = (framedir / "frames-client-to-agent.jsonl").read_bytes()
        assert c2a.count(b'"method":"late"') == 1, "late frame NOT recorded"
        assert tee_proc.returncode == 70
        status = json.loads((framedir / "tee-status.json").read_text())
        assert status["recorded_c2a"] == 2
        assert status["forwarded_c2a"] == 1
        assert status["drained"] is False
        assert status["stdin_reader_done"] is True
        assert status["write_errors"] == ["forward c2a: BrokenPipeError"]


# ---------------------------------------------------------------------------
# R2/C1: running status tracks c2a BEFORE the agent exits
# ---------------------------------------------------------------------------
class TestRunningStatusTracksC2a:
    def test_running_status_tracks_c2a_before_agent_exits(self, tmp_path):
        """C1 killer: a long-lived agent that consumes stdin and stays silent.
        Client sends N frames; poll tee-status.json and assert recorded_c2a
        reaches N while the tee is still running.  C1 (no running status from
        pump_fd) freezes recorded_c2a at 0 in the status file."""
        n_frames = 20
        agent_code = textwrap.dedent("""\
            import sys, time
            for line in sys.stdin:
                pass
            time.sleep(0.5)
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
        lines = []
        for i in range(n_frames):
            lines.append(json.dumps({"jsonrpc": "2.0", "id": i, "method": "m",
                                     "params": {}}, separators=(",", ":")) + "\n")
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        try:
            # Send frames one at a time with a small delay to give status time to update
            for line in lines:
                tee_proc.stdin.write(line.encode())
                tee_proc.stdin.flush()
                time.sleep(0.05)
            # Poll status before closing stdin -- the tee is still running
            status_path = framedir / "tee-status.json"
            deadline = time.monotonic() + 10
            rec_c2a = 0
            while time.monotonic() < deadline:
                if status_path.exists():
                    try:
                        s = json.loads(status_path.read_text())
                        rec_c2a = s.get("recorded_c2a", 0)
                        if rec_c2a >= n_frames:
                            break
                    except (json.JSONDecodeError, ValueError):
                        pass
                time.sleep(0.05)
            assert rec_c2a >= n_frames, (
                "running status recorded_c2a=%d, expected >=%d" % (rec_c2a, n_frames))
            tee_proc.stdin.close()
            tee_proc.wait(timeout=15)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdout.close()
        tee_proc.stderr.close()


# ---------------------------------------------------------------------------
# R1/R3: SIGTERM status through the real checker — non-final arm
# ---------------------------------------------------------------------------
class TestSigtermStatusVsChecker:
    def test_sigterm_status_satisfies_check_tee_status(self, tmp_path):
        """R1: the SIGTERM status (non-final, exit 70, write_errors includes
        'terminated: SIGTERM') passes check_tee_status's RUNNING arm.
        Loads the checker the way the conformance test suite does."""
        P = Path(__file__).resolve().parents[1] / "proofs" / "S0-01"
        sys.path.insert(0, str(P))
        import check_acp_conformance as cc
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
        frame = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "init", "params": {}},
                           separators=(",", ":")).encode() + b"\n"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        try:
            tee_proc.stdin.write(frame)
            tee_proc.stdin.flush()
            status_path = framedir / "tee-status.json"
            loaded = False
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if status_path.exists():
                    try:
                        s = json.loads(status_path.read_text())
                        if s.get("updated_seq", 0) >= 1:
                            loaded = True
                            break
                    except (json.JSONDecodeError, ValueError):
                        pass
                time.sleep(0.1)
            assert loaded, "no recorded frame: the wait for updated_seq >= 1 timed out"
            tee_proc.send_signal(sig.SIGTERM)
            tee_proc.wait(timeout=10)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
            tee_proc.stdin.close()
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 70
        # Parse timeline entries the same way the checker does
        entries = cc._load_timeline_raw(framedir, "run-1")
        # The checker's RUNNING arm should accept this status
        cc.check_tee_status(framedir, "run-1", entries)


# ---------------------------------------------------------------------------
# F10/N6: the SIGTERM handler body is exactly `raise _Terminated()`
# ---------------------------------------------------------------------------
class TestSigtermHandlerStructure:
    def test_sigterm_handler_is_raise_terminated(self, tmp_path):
        """F10: ast-level assertion that the SIGTERM handler body is exactly
        ``raise _Terminated()``.  Kills N6 (handler that takes a lock and
        writes status itself)."""
        import ast
        source = Path(TEE).read_text()
        tree = ast.parse(source)
        # Find the _sigterm_handler function
        handler = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_sigterm_handler":
                handler = node
                break
        assert handler is not None, "_sigterm_handler not found"
        # The body must be exactly one statement: raise _Terminated()
        assert len(handler.body) == 1, (
            "handler body has %d statements, expected 1" % len(handler.body))
        stmt = handler.body[0]
        assert isinstance(stmt, ast.Raise), "handler body is not a raise"
        assert isinstance(stmt.exc, ast.Call), "raise is not a call"
        assert isinstance(stmt.exc.func, ast.Name), "raised is not a name"
        assert stmt.exc.func.id == "_Terminated", (
            "raised %s, expected _Terminated" % stmt.exc.func.id)
        assert len(stmt.exc.args) == 0, "raise has arguments"


# ---------------------------------------------------------------------------
# F2/F5/B5e: structural pins via ast -- drain loops and pump ordering
# ---------------------------------------------------------------------------
class TestStructuralPins:
    def test_drain_loops_have_no_break_or_timeout(self, tmp_path):
        """F5/B5e: both drain loops (c2a and a2c) contain only time.sleep(...)
        and _write_status() -- no break, no time.monotonic() comparison.
        Kills A2-t30 and the a2c stall-timeout mutants structurally."""
        source = Path(TEE).read_text()
        tree = ast.parse(source)
        # Find the main() function
        main_fn = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                main_fn = node
                break
        assert main_fn is not None
        # Find all `while <name>.is_alive():` loops in main
        drain_loops = []
        for node in ast.walk(main_fn):
            if isinstance(node, ast.While):
                test = node.test
                if (isinstance(test, ast.Call)
                        and isinstance(test.func, ast.Attribute)
                        and test.func.attr == "is_alive"):
                    drain_loops.append(node)
        assert len(drain_loops) == 2, (
            "expected 2 drain loops (a2c + c2a), found %d" % len(drain_loops))
        for i, loop in enumerate(drain_loops):
            # The loop body must contain ONLY time.sleep(...) and _write_status()
            for stmt in loop.body:
                if isinstance(stmt, ast.Expr):
                    call = stmt.value
                    if isinstance(call, ast.Call):
                        if isinstance(call.func, ast.Attribute):
                            assert call.func.attr == "sleep", (
                                "drain loop %d has call to .%s" % (i, call.func.attr))
                        elif isinstance(call.func, ast.Name):
                            assert call.func.id == "_write_status", (
                                "drain loop %d has call to %s" % (i, call.func.id))
                        else:
                            assert False, "drain loop %d has unexpected call" % i
                    else:
                        assert False, "drain loop %d has non-call expr" % i
                else:
                    assert False, (
                        "drain loop %d has %s statement" % (i, type(stmt).__name__))
            # No break inside the loop
            for child in ast.walk(loop):
                assert not isinstance(child, ast.Break), (
                    "drain loop %d contains a break" % i)

    def test_timeline_before_directional_in_pumps(self, tmp_path):
        """F2/N3/B5e: in both pump_fd and pump_pipe, inside the `with lock:`
        body, the timeline tl.write call precedes the directional df.write
        call.  Kills N3 (swap order) deterministically."""
        source = Path(TEE).read_text()
        tree = ast.parse(source)
        for pump_name in ("pump_fd", "pump_pipe"):
            pump_fn = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == pump_name:
                    pump_fn = node
                    break
            assert pump_fn is not None, "%s not found" % pump_name
            # Find the `with lock:` inside the for/while loop
            with_lock = None
            for node in ast.walk(pump_fn):
                if isinstance(node, ast.With):
                    for item in node.items:
                        ctx = item.context_expr
                        if isinstance(ctx, ast.Name) and ctx.id == "lock":
                            with_lock = node
                            break
                    if with_lock:
                        break
            assert with_lock is not None, "no `with lock:` in %s" % pump_name
            # Find the first tl.write and the first df.write inside that block
            tl_line = df_line = None
            for child in ast.walk(with_lock):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    if child.func.attr == "write":
                        if isinstance(child.func.value, ast.Name):
                            if child.func.value.id == "tl" and tl_line is None:
                                tl_line = child.lineno
                            elif child.func.value.id == "df" and df_line is None:
                                df_line = child.lineno
            assert tl_line is not None, "no tl.write in %s" % pump_name
            assert df_line is not None, "no df.write in %s" % pump_name
            assert tl_line < df_line, (
                "%s: tl.write at line %d is NOT before df.write at line %d"
                % (pump_name, tl_line, df_line))

    def test_status_write_follows_timeline_write_in_pumps(self, tmp_path):
        """F-B5e-2/S1: in both pump_fd and pump_pipe, inside the `with lock:`
        body, the tl.write call's lineno is LESS THAN the _write_status() call's
        lineno.  Kills S1 (status before timeline) deterministically."""
        tree = ast.parse(Path(TEE).read_text())
        for pump in ("pump_fd", "pump_pipe"):
            fn = next(n for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name == pump)
            wl = next(n for n in ast.walk(fn) if isinstance(n, ast.With)
                      and any(isinstance(i.context_expr, ast.Name) and i.context_expr.id == "lock"
                              for i in n.items))
            tl = next(c.lineno for c in ast.walk(wl)
                      if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                      and c.func.attr == "write" and getattr(c.func.value, "id", None) == "tl")
            ws = next(c.lineno for c in ast.walk(wl)
                      if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                      and c.func.id == "_write_status")
            assert tl < ws, "%s: _write_status at %d precedes tl.write at %d" % (pump, ws, tl)

    def test_write_status_snapshot_and_rewrite_are_locked(self, tmp_path):
        """F-B5e-3/N4/D3: _write_status takes `with lock:` containing the seq
        snapshot, and `with status_lock:` containing os.replace.
        Kills N4 (snapshot outside lock) and D3 (no status_lock)
        deterministically."""
        tree = ast.parse(Path(TEE).read_text())
        ws = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_write_status")
        withs = {}
        for n in ast.walk(ws):
            if isinstance(n, ast.With):
                for i in n.items:
                    if isinstance(i.context_expr, ast.Name):
                        withs.setdefault(i.context_expr.id, n)
        assert "lock" in withs, "_write_status takes no `with lock:`"
        assert "status_lock" in withs, "_write_status takes no `with status_lock:`"
        assert any(isinstance(c, ast.Name) and c.id == "seq" for c in ast.walk(withs["lock"])), \
            "the counter snapshot is not inside `with lock:`"
        # F-B5e-13: stdin_reader_done and write_errors must also be read inside the lock
        lock_src = ast.dump(withs["lock"])
        assert "stdin_reader_done" in lock_src, \
            "stdin_reader_done is not read inside `with lock:`"
        assert "write_errors" in lock_src, \
            "write_errors is not read inside `with lock:`"
        assert any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                   and c.func.attr == "replace" for c in ast.walk(withs["status_lock"])), \
            "os.replace is not inside `with status_lock:`"

    def test_write_status_reads_no_state_outside_the_lock(self, tmp_path):
        """F5: no state[...] or seq Subscript exists in _write_status outside
        `with lock:`.  MIRROR-SNAPSHOT (locked snapshot kept, fields re-read
        unlocked) must die."""
        tree = ast.parse(Path(TEE).read_text())
        ws = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_write_status")
        wl = next(n for n in ast.walk(ws) if isinstance(n, ast.With)
                  and any(getattr(i.context_expr, "id", "") == "lock"
                          for i in n.items))
        inside = {id(n) for n in ast.walk(wl)}
        stray = [n.lineno for n in ast.walk(ws)
                 if isinstance(n, ast.Subscript)
                 and getattr(n.value, "id", "") in ("state", "seq")
                 and id(n) not in inside]
        assert not stray, "state/seq read outside `with lock:` at %s" % stray

    def test_concurrent_main_thread_status_vs_pump(self, tmp_path):
        """F2/N4/D3/B5e: the agent exits while its grandchild keeps streaming
        a2c frames.  The client's stdin is closed as soon as the last late
        frame is written (VERIFY-B5h F9), so the tee's main thread sits in the
        a2c drain loop writing status concurrently with the a2c pump itself.
        Spin-read >= 10 000 snapshots -> torn == 0 AND
        updated_seq == recorded_c2a + recorded_a2c on every read.
        Kills N4 (snapshot outside lock) and D3 (no status_lock)."""
        agent_code = textwrap.dedent("""\
            import subprocess, sys, json, os
            line = sys.stdin.readline()
            os.close(0)
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            # grandchild streams a2c frames for 30 s
            gc = subprocess.Popen([sys.executable, "-c",
                "import sys, json, time\\n"
                "for i in range(3000):\\n"
                "    sys.stdout.write(json.dumps({'jsonrpc':'2.0','method':'gc','params':{'i':i}}) + chr(10))\\n"
                "    sys.stdout.flush()\\n"
                "    time.sleep(0.01)\\n"])
            fd = os.environ.get("S0_01_FRAMEDIR", "")
            if fd:
                open(os.path.join(fd, "grandchild.pid"), "w").write(str(gc.pid))
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
        frame1 = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                             "params": {}}, separators=(",", ":")) + "\n"
        late_frames = [json.dumps({"jsonrpc": "2.0", "id": i, "method": "late",
                                   "params": {}}, separators=(",", ":")) + "\n"
                       for i in range(2, 101)]
        tee_proc = subprocess.Popen([sys.executable, str(TEE)], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        try:
            tee_proc.stdin.write(frame1.encode())
            tee_proc.stdin.flush()
            answer = _read_with_deadline(tee_proc.stdout, 30)
            assert answer, "no handshake line from the tee within 30 s"
            assert json.loads(answer)["id"] == 1
            # Drain stdout concurrently
            def _drain():
                while True:
                    chunk = tee_proc.stdout.read(65536)
                    if not chunk:
                        break
            drainer = threading.Thread(target=_drain, daemon=True)
            drainer.start()
            # Send late c2a frames (agent's stdin is closed, so these hit EPIPE
            # and the c2a drain loop writes status from the main thread)
            tee_proc.stdin.write("".join(late_frames).encode())
            tee_proc.stdin.flush()
            # VERIFY-B5h F9: close the write end the moment the last frame is
            # written.  The test writes nothing after this, and holding a tee's
            # stdin open across a blocking read of its stdout is the deadlock
            # test_a_silent_agent_cannot_wedge_a_bounded_read pins.
            try:
                tee_proc.stdin.close()
            except OSError:
                pass
            # Spin-read status while both the main thread and the a2c pump write
            status_path = framedir / "tee-status.json"
            torn = 0
            reads = 0
            seq_violations = 0
            deadline = time.monotonic() + 45
            while tee_proc.poll() is None and time.monotonic() < deadline:
                if status_path.exists():
                    try:
                        s = json.loads(status_path.read_text())
                        reads += 1
                        if s["updated_seq"] != s["recorded_c2a"] + s["recorded_a2c"]:
                            seq_violations += 1
                    except (json.JSONDecodeError, ValueError):
                        torn += 1
            tee_proc.wait(timeout=30)
            drainer.join(timeout=5)
        finally:
            try:
                if tee_proc.poll() is None:
                    tee_proc.kill()
                    tee_proc.wait(timeout=5)
                # F-B5e-12 / F-B5g-4: kill THIS test's grandchild with identity.
                # VERIFY-B5h F4: this site can only ever see "gone", and says so.
                # The finally cannot run until tee_proc.wait() returns; the tee
                # cannot exit until its a2c pump sees EOF; and a2c EOF IS the
                # grandchild's death, because the grandchild holds the agent's
                # stdout.  The grandchild is therefore guaranteed dead before the
                # census here for ANY lifetime -- lengthening it cannot make the
                # kill reachable, which is why GRANDCHILD-UNKILLED-S3 survives BY
                # CONSTRUCTION.  Sites 1 and 2 carry the live branch.
                assert _kill_own_grandchild(framedir) == "gone"
            finally:
                tee_proc.stdout.close()
                tee_proc.stderr.close()
        assert reads >= 10000, "only %d reads -- need >= 10000" % reads
        assert torn == 0, "%d torn reads out of %d" % (torn, reads + torn)
        assert seq_violations == 0, (
            "%d snapshots where updated_seq != recorded_c2a + recorded_a2c" % seq_violations)


# ---------------------------------------------------------------------------
# F-B5g-4: zombie grandchild is "already gone", not a test failure
# ---------------------------------------------------------------------------
class TestZombieGrandchild:
    def test_zombie_grandchild_is_already_gone(self, tmp_path):
        """F-B5g-4: a grandchild that exits ~0.3 s before the census is a
        zombie (empty /proc/<pid>/cmdline, stat state Z).  The old F13 code
        treated this as 'not the grandchild' and failed the test.  After
        the fix, a zombie with a foreign cmdline = already gone, not a
        hard failure.  A LIVE foreign process = hard failure 'refusing to
        kill a foreign pid'.  Pid reuse is unreachable here (pid_max 32768,
        ~5 pids/s measured vs the ~728/s needed) and the zombie window
        (~0.97 s) is the reachable direction.
        RED on the PIN today: 'pid N is not the grandchild (cmdline: )'.
        GREEN after."""
        agent_code = textwrap.dedent("""\
            import subprocess, sys, json, os
            line = sys.stdin.readline()
            resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\\n")
            sys.stdout.flush()
            # Grandchild exits quickly (~0.3 s) so it is a zombie by census time
            gc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(0.3)"])
            fd = os.environ.get("S0_01_FRAMEDIR", "")
            if fd:
                open(os.path.join(fd, "grandchild.pid"), "w").write(str(gc.pid))
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
        # Send the initialize frame, then keep stdin alive so the tee
        # stays in the c2a drain loop while the grandchild becomes a zombie
        input_bytes = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                  "params": {}}).encode() + b"\n"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        try:
            tee_proc.stdin.write(input_bytes)
            tee_proc.stdin.flush()
            # Do NOT close stdin -- the tee stays alive in the c2a drain loop
            # Wait for grandchild to exit + become a zombie (~1.5 s)
            time.sleep(1.5)
            tee_proc.send_signal(sig.SIGTERM)
            tee_proc.wait(timeout=10)
        finally:
            try:
                if tee_proc.poll() is None:
                    tee_proc.kill()
                    tee_proc.wait(timeout=5)
                # The census must NOT fail on a zombie grandchild -- and it
                # must report the ZOMBIE branch.  Discarding the return let a
                # LIVE grandchild (which the helper kills) pass a test named
                # ..._is_already_gone (VERIFY-B5i VB-F5, ZOMBIE-BRANCH-LIVE).
                assert _kill_own_grandchild(framedir) == "gone"
            finally:
                tee_proc.stdin.close()
                tee_proc.stdout.close()
                tee_proc.stderr.close()
        assert tee_proc.returncode == 70


# ---------------------------------------------------------------------------
# F13: SIGTERM in the startup window produces rc 70 and a status file.
#      The handler is installed before Popen, and the try: immediately follows
#      signal.signal -- so _Terminated is caught even during sha256 reads.
# ---------------------------------------------------------------------------
class TestEarlySigterm:
    def test_sigterm_during_sha256_produces_status(self, tmp_path):
        """F13/B5e: the child cannot be visible to pgrep -P before the fork at
        Popen (after the handler install at signal.signal), so the TERM sent
        after pgrep succeeds can never precede the handler -- structural lower
        flake bound of 0.  The 234 MB entrypoint (sha256 >= 0.3 s) widens the
        in-try region as load insurance, not as the mechanism.
        Assert rc 70, status present, write_errors == ["terminated: SIGTERM"],
        final false, updated_seq 0, agent child gone within 2 s.

        RED STATE (before the full fix): rc=1 status_present=False
        stderr tail: ['    raise _Terminated()', '_Terminated']
        The half-fix installed the handler before Popen but left the try:
        290 lines later, so _Terminated propagated uncaught."""
        framedir = tmp_path / "frames"
        framedir.mkdir()
        agent_script = tmp_path / "big_agent.py"
        with open(agent_script, "w") as f:
            f.write("#!%s\nimport sys, time\ntime.sleep(30)\nsys.exit(0)\n" % sys.executable)
            line = "# " + "x" * 998 + "\n"  # ~1 KB per line
            for _ in range(234000):  # ~234 MB
                f.write(line)
        agent_script.chmod(0o755)
        env = os.environ.copy()
        env["S0_01_FRAMEDIR"] = str(framedir)
        env["S0_01_AGENT"] = str(agent_script)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        try:
            # Poll pgrep -P <tee_pid> every 2 ms until child appears
            deadline = time.monotonic() + 10
            child_pid = None
            while time.monotonic() < deadline:
                result = subprocess.run(
                    ["pgrep", "-P", str(tee_proc.pid)],
                    capture_output=True, timeout=1)
                if result.returncode == 0 and result.stdout.strip():
                    child_pid = int(result.stdout.strip().split()[0])
                    break
                time.sleep(0.002)
            assert child_pid is not None, "agent child never appeared"
            # SIGTERM immediately -- the tee is in sha256 reads
            tee_proc.send_signal(sig.SIGTERM)
            tee_proc.wait(timeout=10)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdin.close()
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 70
        status_path = framedir / "tee-status.json"
        assert status_path.exists(), "tee-status.json missing after early SIGTERM"
        status = json.loads(status_path.read_text())
        assert status["write_errors"] == ["terminated: SIGTERM"]
        assert status["final"] is False
        assert status["updated_seq"] == 0
        # F14/AF-AP-45: agent child dead or zombie within 2 s.
        # Read /proc/<pid>/stat field 3 for the state: Z = zombie (killed,
        # unreaped); absence = fully reaped.  Both count as "gone".
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            stat_path = "/proc/%d/stat" % child_pid
            if not os.path.exists(stat_path):
                break
            try:
                stat_fields = open(stat_path).read().split()
                if len(stat_fields) >= 3 and stat_fields[2] == "Z":
                    break  # zombie = killed, unreaped
            except (OSError, IOError):
                break  # vanished between exists() and open()
            time.sleep(0.1)
        # Final assertion: gone or zombie
        if os.path.exists("/proc/%d/stat" % child_pid):
            try:
                stat_fields = open("/proc/%d/stat" % child_pid).read().split()
                proc_state = stat_fields[2] if len(stat_fields) >= 3 else "?"
            except (OSError, IOError):
                proc_state = "gone"
            assert proc_state == "Z", (
                "agent child pid %d state %s, expected Z or gone" % (child_pid, proc_state))

    def test_no_statement_between_signal_and_try(self, tmp_path):
        """F13 structural pin: in main(), the signal.signal(SIGTERM, ...)
        call is immediately followed by a Try node with no intervening
        statements.  Kills the half-fix (handler installed but try: far away)."""
        source = Path(TEE).read_text()
        tree = ast.parse(source)
        main_fn = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                main_fn = node
                break
        assert main_fn is not None
        # Find the signal.signal call in main's body
        signal_idx = None
        for i, stmt in enumerate(main_fn.body):
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                func = stmt.value.func
                if (isinstance(func, ast.Attribute)
                        and isinstance(func.value, ast.Name)
                        and func.value.id == "signal"
                        and func.attr == "signal"):
                    signal_idx = i
                    break
        assert signal_idx is not None, "signal.signal call not found in main()"
        # VERIFY-B5i VB-F9 / SWEEP-tests 12.1: WHICH signal.  The pin matched
        # any signal.signal call and never read its first argument, so a
        # handler installed for another signal was invisible to it.
        sig_args = main_fn.body[signal_idx].value.args
        assert sig_args and getattr(sig_args[0], "attr", "") == "SIGTERM", (
            "the handler is installed for %r, not SIGTERM"
            % (getattr(sig_args[0], "attr", None) if sig_args else None))
        # The very next statement must be a Try
        next_stmt = main_fn.body[signal_idx + 1]
        assert isinstance(next_stmt, ast.Try), (
            "statement after signal.signal is %s at line %d, expected Try"
            % (type(next_stmt).__name__, next_stmt.lineno))
        # F-B5e-5: no Popen call precedes the handler install in main() body
        assert not any(
            isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
            and c.func.attr == "Popen"
            for s in main_fn.body[:signal_idx] for c in ast.walk(s)
        ), "Popen precedes the handler install"
        # F-B5e-6 / F11: ALL proc assignments before the install must be None
        pre_proc = [s for s in main_fn.body[:signal_idx]
                    if isinstance(s, ast.Assign)
                    and len(s.targets) == 1
                    and isinstance(s.targets[0], ast.Name)
                    and s.targets[0].id == "proc"]
        assert pre_proc and all(
            isinstance(s.value, ast.Constant) and s.value.value is None
            for s in pre_proc
        ), "proc is rebound to a non-None value before the handler install"

    def test_grandchild_cleanup_is_own_pid_scoped(self, tmp_path):
        """F12/AF-AP-59: no world-scoped process sweep exists in this test
        file, checked against the registry's own AP_SCREEN signatures.
        CENSUS-WORLD, CENSUS-PGREP-TIGHT, CENSUS-PGREP-A, CENSUS-PS-E
        must all die.  CENSUS-PGREP-X and CENSUS-PROC-WALK die on the AST
        pin below (an os.kill outside the allow-list).  Limit: a census
        that only ENUMERATES the world without killing is out of the AST
        pin's reach."""
        src = Path(__file__).read_text()
        # The AP_SCREEN import carries the AF-AP-59 row; no hand-typed literals
        for ap_id, rx, msg in AP_SCREEN:
            if ap_id == "AF-AP-59":
                hits = rx.findall(src)
                assert not hits, (
                    "AF-AP-59 match in test file: %s (%s)" % (hits, msg))

    def test_kill_calls_only_at_allowed_sites(self, tmp_path):
        """F-B5g-3 / VERIFY-B5h F3b AST pin, written as a SUBTRACTION: collect
        EVERY os.kill / os.killpg Call in this file first -- module scope, class
        body, lambda, comprehension, any nesting -- then subtract the ones whose
        enclosing function is allowed.  Only _kill_own_grandchild may signal a
        pid.  The inclusion form this replaced iterated FunctionDefs and looked
        inside them, so a kill written outside any def was never examined:
        KILL-MODULE-LEVEL and KILL-LAMBDA both passed it, measured.
        Kills CENSUS-PGREP-X and CENSUS-PROC-WALK (a world census plus a kill).
        DOCUMENTED LIMIT -- evasion by SPELLING, not a hole in the pin: it
        matches the attribute form on the name ``os`` only, so
        ``from os import kill as k``, ``signal.pthread_kill``,
        ``subprocess.run(["kill", ...])`` and ``Popen.send_signal`` are out of
        its reach, and so is a census that only ENUMERATES the world without
        killing (that class is held by the AF-AP-59 screen above)."""
        tree = ast.parse(Path(__file__).read_text())
        enclosing = {}

        def _map(node, fname):
            for child in ast.iter_child_nodes(node):
                nf = (child.name
                      if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                      else fname)
                enclosing[id(child)] = nf
                _map(child, nf)

        _map(tree, None)
        violations = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            # os.kill(pid, sig) or os.killpg(pid, sig), wherever it lives
            if (isinstance(func, ast.Attribute)
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "os"
                    and func.attr in ("kill", "killpg")):
                site = enclosing.get(id(node))
                if site != "_kill_own_grandchild":
                    violations.append("%s at line %d in %s"
                                      % (func.attr, node.lineno,
                                         site or "<module scope>"))
        assert not violations, (
            "os.kill/os.killpg outside _kill_own_grandchild: %s" % violations)

    def test_no_unbounded_tee_pipe_reads(self, tmp_path):
        """VERIFY-B5h F9 / VERIFY-B5i VB-F4 structural pin: every MENTION of a
        tee pipe is accounted for, not three call spellings.  Keying on
        ``.read``/``.readline``/``.communicate`` left four working evasions --
        ``next(iter(tee_proc.stdout), None)``, ``.readlines()``,
        ``os.read(tee_proc.stdout.fileno(), n)`` and a local alias -- and the
        first of those reproduces the identical deadlock on the tee (main
        thread in hrtimer_nanosleep, c2a reader in anon_pipe_read, this
        process's write end == the tee's fd 0).

        So: collect every ``tee_proc.stdout`` / ``tee_proc.stderr``, plus any
        local a pipe was assigned to in the same function, and allow exactly
        four things to be done with one -- hand it to a bounded helper, close
        it, hand it to another Popen as a keyword argument, or read it with a
        ``timeout=`` of its own.  Mentions INSIDE a bounded helper are the
        helper's own business and are skipped.  Anything else is a violation,
        whatever it is spelled.

        RED on the parent of checkpoint 8y: six unbounded readline sites, one
        of which (test_concurrent_main_thread_status_vs_pump) held the tee's
        stdin open across the read.
        LIMIT: the pin keys on the receiver NAME ``tee_proc`` for the pipe and
        tracks aliases of the PIPE (``x = tee_proc.stdout``).  An alias of the
        PROCESS (``p = tee_proc`` then ``p.stdout.readline()``, or a ``p=tee_proc``
        parameter default) is out of its reach -- as is a bounded helper that is
        trusted by NAME whether or not its thread is ever joined."""
        tree = ast.parse(Path(__file__).read_text())
        BOUNDED = {"_drain", "_read_with_deadline"}
        enclosing = {}
        parent = {}

        def _map(node, fname):
            for child in ast.iter_child_nodes(node):
                nf = (child.name
                      if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                      else fname)
                enclosing[id(child)] = nf
                parent[id(child)] = node
                _map(child, nf)

        _map(tree, None)

        def _is_pipe(node):
            return (isinstance(node, ast.Attribute)
                    and node.attr in ("stdout", "stderr")
                    and isinstance(node.value, ast.Name)
                    and node.value.id == "tee_proc")

        # locals a pipe was assigned to, scoped to the function that did it
        aliases = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and _is_pipe(node.value):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name):
                        aliases.add((enclosing.get(id(node)), tgt.id))

        mentions = []
        for node in ast.walk(tree):
            if _is_pipe(node):
                mentions.append(("tee_proc.%s" % node.attr, node))
            elif (isinstance(node, ast.Name)
                  and (enclosing.get(id(node)), node.id) in aliases
                  and not isinstance(node.ctx, ast.Store)):
                mentions.append(("alias %s" % node.id, node))

        bad = []
        for what, node in mentions:
            if enclosing.get(id(node)) in BOUNDED:
                continue
            up = parent.get(id(node))
            # 1. an argument to a bounded helper
            if (isinstance(up, ast.Call) and isinstance(up.func, ast.Name)
                    and up.func.id in BOUNDED and any(a is node for a in up.args)):
                continue
            # 2. closed
            if isinstance(up, ast.Attribute) and up.attr == "close":
                continue
            # 3. handed to another Popen as a keyword argument
            if isinstance(up, ast.keyword):
                call = parent.get(id(up))
                if (isinstance(call, ast.Call)
                        and getattr(call.func, "attr", None) == "Popen"):
                    continue
            # 4. read with a timeout= of its own
            if isinstance(up, ast.Attribute):
                call = parent.get(id(up))
                if (isinstance(call, ast.Call)
                        and any(kw.arg == "timeout" for kw in call.keywords)):
                    continue
            bad.append("%s at line %d in %s (%s)"
                       % (what, node.lineno,
                          enclosing.get(id(node)) or "<module scope>",
                          type(up).__name__))
        assert not bad, (
            "a tee pipe is used in a way that is not bounded, closed, handed "
            "to a Popen or given a timeout: %s" % bad)
        # de-vacuous: the walk must actually be finding the pipes it allows
        assert len(mentions) >= 50, (
            "the mention walk found only %d tee-pipe references -- it is not "
            "seeing the file" % len(mentions))

    def test_a_silent_agent_cannot_wedge_a_bounded_read(self, tmp_path):
        """VERIFY-B5h F9, the hang itself, as a test.  The agent consumes the
        handshake frame, closes its a2c side with NOTHING written and exits,
        while this test still holds the tee's stdin.  The tee then has nothing
        to send and cannot exit (its c2a pump is still reading our pipe), so a
        bare readline() here never returns -- reproduced against the PIN's tee
        with the tee's main thread in hrtimer_nanosleep, its c2a reader in
        anon_pipe_read, and this process's write end == the tee's fd 0.
        _read_with_deadline turns that wedge into a returned None, which is
        what this test asserts, together with the wedge being real (the tee is
        still alive) and the tee exiting once the client closes stdin."""
        agent_code = textwrap.dedent("""\
            import os, sys
            sys.stdin.readline()
            os.close(1)
            os._exit(0)
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
        frame = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                            "params": {}}, separators=(",", ":")).encode() + b"\n"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    env=env)
        try:
            tee_proc.stdin.write(frame)
            tee_proc.stdin.flush()
            t0 = time.monotonic()
            line = _read_with_deadline(tee_proc.stdout, 5)
            elapsed = time.monotonic() - t0
            assert line is None, (
                "expected no a2c line from a silent agent, got %r" % (line,))
            assert elapsed < 15, "the bounded read took %.1f s" % elapsed
            # the wedge is real: the tee is alive with the client holding stdin
            assert tee_proc.poll() is None, "tee exited before the client closed stdin"
            tee_proc.stdin.close()
            tee_proc.wait(timeout=30)
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
            tee_proc.stdout.close()
            tee_proc.stderr.close()
        assert tee_proc.returncode == 0, (
            "tee rc %d after a silent agent" % tee_proc.returncode)


# ---------------------------------------------------------------------------
# F14: SIGTERM terminates the agent child
# ---------------------------------------------------------------------------
class TestSigtermTerminatesAgent:
    def test_sigterm_kills_agent_child(self, tmp_path):
        """F14/B5e: after SIGTERM, the agent child pid is gone within 2 s."""
        agent_code = textwrap.dedent("""\
            import sys, json, time
            for line in sys.stdin:
                resp = {"jsonrpc": "2.0", "id": 1, "result": {}}
                sys.stdout.write(json.dumps(resp, separators=(",", ":")) + "\\n")
                sys.stdout.flush()
            time.sleep(120)
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
        frame = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "init", "params": {}},
                           separators=(",", ":")).encode() + b"\n"
        tee_proc = subprocess.Popen([sys.executable, str(TEE)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
        try:
            tee_proc.stdin.write(frame)
            tee_proc.stdin.flush()
            # Wait for identity to get agent pid
            id_path = framedir / "runtime-identity.json"
            identity = None
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if id_path.exists():
                    try:
                        identity = json.loads(id_path.read_text())
                        if "agent_child_pid" in identity:
                            break
                    except (json.JSONDecodeError, ValueError):
                        pass
                time.sleep(0.05)
            assert identity is not None, "runtime-identity.json never appeared"
            agent_pid = identity["agent_child_pid"]
            # Confirm agent is alive (AF-AP-45: check /proc/stat state, not just path)
            stat_path = "/proc/%d/stat" % agent_pid
            assert os.path.exists(stat_path), "agent not alive"
            stat_fields = open(stat_path).read().split()
            assert len(stat_fields) >= 3 and stat_fields[2] != "Z", (
                "agent is zombie before SIGTERM: %s" % stat_fields[2] if len(stat_fields) >= 3 else "?")
            tee_proc.send_signal(sig.SIGTERM)
            tee_proc.wait(timeout=10)
            # F14/AF-AP-45: agent dead or zombie within 2 s
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                if not os.path.exists("/proc/%d/stat" % agent_pid):
                    break
                try:
                    sf = open("/proc/%d/stat" % agent_pid).read().split()
                    if len(sf) >= 3 and sf[2] == "Z":
                        break  # zombie = killed, unreaped
                except (OSError, IOError):
                    break
                time.sleep(0.1)
            # Final: gone or zombie
            if os.path.exists("/proc/%d/stat" % agent_pid):
                try:
                    sf = open("/proc/%d/stat" % agent_pid).read().split()
                    proc_state = sf[2] if len(sf) >= 3 else "?"
                except (OSError, IOError):
                    proc_state = "gone"
                assert proc_state == "Z", (
                    "agent pid %d state %s after 2 s, expected Z or gone" % (agent_pid, proc_state))
        finally:
            if tee_proc.poll() is None:
                tee_proc.kill()
                tee_proc.wait(timeout=5)
        tee_proc.stdin.close()
        tee_proc.stdout.close()
        tee_proc.stderr.close()
        assert tee_proc.returncode == 70


# ---------------------------------------------------------------------------
# VERIFY-B5h F6: the census helper's four paths, driven directly
# ---------------------------------------------------------------------------
class TestKillOwnGrandchildBranches:
    """The identity read is monkeypatched (builtins.open); pathlib's read_text
    goes through io.open, which the patch does not touch, so the pid file stays
    real.  Every process here is one this test spawned and is killed by pid
    through Popen.kill(), never by name and never through os.kill."""

    @staticmethod
    def _framedir_with_pid(tmp_path, pid):
        framedir = tmp_path / "frames"
        framedir.mkdir(exist_ok=True)
        (framedir / "grandchild.pid").write_text(str(pid))
        return framedir

    @staticmethod
    def _fake_proc_read(pid, cmdline=None, state=None, exc=None):
        real_open = open

        def fake_open(path, *a, **kw):
            name = str(path)
            if name == "/proc/%d/cmdline" % pid:
                if exc is not None:
                    raise exc
                return io.StringIO(cmdline)
            if name == "/proc/%d/stat" % pid and state is not None:
                return io.StringIO("%d (python3) %s 1 1 1" % (pid, state))
            return real_open(path, *a, **kw)

        return fake_open

    def test_live_foreign_pid_is_refused_and_not_signalled(self, tmp_path, monkeypatch):
        victim = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            framedir = self._framedir_with_pid(tmp_path, victim.pid)
            monkeypatch.setattr("builtins.open",
                                self._fake_proc_read(victim.pid, cmdline="sleep 30 ",
                                                     state="S"))
            with pytest.raises(AssertionError) as excinfo:
                _kill_own_grandchild(framedir)
            monkeypatch.undo()
            assert "refusing to kill a foreign pid %d" % victim.pid in str(excinfo.value)
            assert victim.poll() is None, "a foreign pid was signalled"
        finally:
            victim.kill()
            victim.wait(timeout=10)

    def test_zombie_reports_gone_without_signalling(self, tmp_path, monkeypatch):
        victim = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            framedir = self._framedir_with_pid(tmp_path, victim.pid)
            monkeypatch.setattr("builtins.open",
                                self._fake_proc_read(victim.pid, cmdline="", state="Z"))
            branch = _kill_own_grandchild(framedir)
            monkeypatch.undo()
            assert branch == "gone"
            assert victim.poll() is None, "a zombie-looking pid was signalled"
        finally:
            victim.kill()
            victim.wait(timeout=10)

    def test_pid_that_raced_us_to_exit_reports_gone(self, tmp_path, monkeypatch):
        """The benign race F-B5g-4 was opened for: identified as ours at the
        cmdline read, reaped before the kill.  os.kill really runs -- on a pid
        ABOVE pid_max, which no process can ever hold, so ESRCH is guaranteed
        and no live process can be signalled by this test."""
        pid_max = int(Path("/proc/sys/kernel/pid_max").read_text().strip())
        dead = pid_max + 1
        framedir = self._framedir_with_pid(tmp_path, dead)
        monkeypatch.setattr(
            "builtins.open",
            self._fake_proc_read(dead, cmdline="python3 -c import time; time.sleep(30) "))
        branch = _kill_own_grandchild(framedir)
        monkeypatch.undo()
        assert branch == "gone"

    def test_unidentifiable_pid_is_never_signalled(self, tmp_path, monkeypatch):
        """Fail-closed: a /proc read that is denied means the pid cannot be
        identified, so it is not killed and the helper says why."""
        victim = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            framedir = self._framedir_with_pid(tmp_path, victim.pid)
            monkeypatch.setattr(
                "builtins.open",
                self._fake_proc_read(victim.pid,
                                     exc=PermissionError(13, "Permission denied")))
            with pytest.raises(AssertionError) as excinfo:
                _kill_own_grandchild(framedir)
            monkeypatch.undo()
            assert "cannot identify pid %d -- not killing" % victim.pid in str(excinfo.value)
            assert victim.poll() is None, "an unidentifiable pid was signalled"
        finally:
            victim.kill()
            victim.wait(timeout=10)


# ---------------------------------------------------------------------------
# SWEEP-prod #11 / AF-AP-55: the interpreter identity is sampled at the stage
# that speaks, not at the stage that was spawned
# ---------------------------------------------------------------------------
class TestInterpreterIdentityStage:
    """SWEEP-prod #11 / AF-AP-55.  A two-stage agent -- a shell wrapper that
    ``exec``s python -- is still the WRAPPER at Popen time, so the spawn-time
    readlink names the shell.  The tee re-reads /proc/<pid>/exe when the first
    a2c byte arrives (ported from tools/acp_probe.py:296-320, same field
    names), so runtime-identity.json names the interpreter that actually spoke.
    Red on the PIN, measured: 20/20 runs recorded /usr/bin/bash.
    """

    @staticmethod
    def _wrapper(tmp_path, tail):
        """A bash wrapper that execs python; ``tail`` is what python does after
        it has answered the handshake."""
        wrapper = tmp_path / "agent.sh"
        wrapper.write_text(
            "#!/bin/bash\n"
            "exec %s -c '\n"
            "import sys, json\n"
            "sys.stdin.readline()\n"
            "sys.stdout.write(json.dumps({\"jsonrpc\": \"2.0\", \"id\": 1,"
            " \"result\": {}}) + chr(10))\n"
            "sys.stdout.flush()\n"
            "%s\n"
            "'\n" % (sys.executable, tail))
        wrapper.chmod(0o755)
        return wrapper

    @staticmethod
    def _frame():
        return json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                           "params": {}}, separators=(",", ":")).encode() + b"\n"

    def test_interpreter_is_resampled_at_the_first_a2c_byte(self, tmp_path):
        """20 trials, deterministic by construction: the agent blocks on stdin
        after answering, and this test holds the tee's stdin open, so the agent
        CANNOT exit while the tee samples.  Every trial must name the
        interpreter that spoke.  20 trials and not one because the spawn-time
        reading is a race; the resampled one must not be."""
        assert os.path.exists("/bin/bash"), "/bin/bash absent: no two-stage agent"
        python_real = os.path.realpath(sys.executable)
        bash_real = os.path.realpath("/bin/bash")
        assert python_real != bash_real
        wrapper = self._wrapper(tmp_path, "for line in sys.stdin:\n    pass")
        recorded = []
        for trial in range(20):
            framedir = tmp_path / ("frames_%d" % trial)
            framedir.mkdir()
            env = os.environ.copy()
            env["S0_01_FRAMEDIR"] = str(framedir)
            env["S0_01_AGENT"] = str(wrapper)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            id_path = framedir / "runtime-identity.json"
            tee_proc = subprocess.Popen([sys.executable, str(TEE)], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        env=env)
            try:
                tee_proc.stdin.write(self._frame())
                tee_proc.stdin.flush()
                seen = None
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    if id_path.exists():
                        try:
                            seen = json.loads(id_path.read_text()).get(
                                "agent_interpreter_realpath")
                        except (json.JSONDecodeError, ValueError):
                            seen = None
                        if seen == python_real:
                            break
                    time.sleep(0.02)
                assert seen == python_real, (
                    "trial %d: runtime-identity.json names %r, expected the "
                    "interpreter that spoke (%s)" % (trial, seen, python_real))
                identity = json.loads(id_path.read_text())
                assert identity["agent_realpath"] == str(wrapper)
                assert identity["agent_interpreter_sha256"] == _sha256_file(seen), (
                    "trial %d: interpreter sha does not hash the recorded path" % trial)
                # the re-sample REWRITES this file; its key set is a contract
                # (check_acp_conformance.py rejects an extra or missing key)
                assert set(identity) == {
                    "tee_path", "tee_sha256", "tee_pid", "agent_argv",
                    "agent_realpath", "agent_entrypoint_sha256", "agent_child_pid",
                    "agent_interpreter_realpath", "agent_interpreter_sha256",
                    "python_dont_write_bytecode", "spawned_at_utc",
                }, "the re-sample changed runtime-identity.json's key set"
                recorded.append(seen)
                tee_proc.stdin.close()
                tee_proc.wait(timeout=30)
            finally:
                if tee_proc.poll() is None:
                    tee_proc.kill()
                    tee_proc.wait(timeout=5)
                tee_proc.stdout.close()
                tee_proc.stderr.close()
            assert tee_proc.returncode == 0, (
                "trial %d: tee rc %d" % (trial, tee_proc.returncode))
        assert recorded == [python_real] * 20, (
            "expected the interpreter that spoke in 20/20 trials, got %s"
            % sorted(set(recorded)))
        assert bash_real not in recorded

    def test_resample_that_loses_the_race_is_loud_not_silent(self, tmp_path):
        """AF-AP-55's own rule, pinned.  When the agent answers and exits at
        once, the readlink can lose the race with the child's exit (a zombie
        has no /proc/<pid>/exe): measured 1/20 on a loaded box, 0/20 idle.
        The record and the reason must then AGREE -- either the resample won
        and the recorded interpreter is the one that spoke with no marker on
        stderr, or it lost, the tee said so on stderr, and the EARLY reading is
        kept.  The early reading is usually the wrapper (bash), but not always:
        the spawn-time readlink races the child's exec too, and under load the
        child can already be python when the tee first looks (checkpoint-8y
        gate, 2026-09-08, load 7.8: trial 11 lost the late race with a record
        that already said python).  So "lost" pins the record to ONE OF the two
        stages and never to a third path; "won" pins it to the final stage.  A
        silently stale identity outside those two is what this pins out.
        The tee's identity key set is fixed by check_acp_conformance.py, so the
        reason cannot be a new field; write_errors would flip the exit code."""
        python_real = os.path.realpath(sys.executable)
        bash_real = os.path.realpath("/bin/bash")
        wrapper = self._wrapper(tmp_path, "sys.exit(0)")
        marker = b"agent interpreter re-sample: exited before identity"
        outcomes = []
        for trial in range(20):
            framedir = tmp_path / ("frames_%d" % trial)
            framedir.mkdir()
            env = os.environ.copy()
            env["S0_01_FRAMEDIR"] = str(framedir)
            env["S0_01_AGENT"] = str(wrapper)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            proc = subprocess.run([sys.executable, str(TEE)], input=self._frame(),
                                  capture_output=True, env=env, timeout=60)
            assert proc.returncode == 0, (
                "trial %d: tee rc %d, stderr %r" % (trial, proc.returncode, proc.stderr))
            identity = json.loads((framedir / "runtime-identity.json").read_text())
            seen = identity["agent_interpreter_realpath"]
            lost = marker in proc.stderr
            outcomes.append(lost)
            if lost:
                assert seen in (bash_real, python_real), (
                    "trial %d: the resample said it lost the race but the record "
                    "names a path that is neither stage: %r" % (trial, seen))
            else:
                assert seen == python_real, (
                    "trial %d: no marker on stderr, so the resample ran -- it must "
                    "record the interpreter that spoke, not %r" % (trial, seen))
            assert identity["agent_interpreter_sha256"] == _sha256_file(seen), (
                "trial %d: interpreter sha does not hash the recorded path" % trial)
        # VERIFY-B5i VB-F10: with a bash->python agent the lost branch admits
        # either stage, so it is near-vacuous on its own -- a tee whose
        # re-sample ALWAYS fails rode this test and died only on its sibling.
        # At least one of the 20 must have WON.  Measured on this box: 0/20
        # lost idle, 6/50 lost under load 2.7, so 20/20 lost is a broken
        # re-sample, not a slow box.  Aggregate, therefore after the loop.
        assert any(not lost for lost in outcomes), (
            "all 20 trials lost the re-sample race (stderr marker every time) "
            "-- the re-sample never completes")

    def test_reread_interpreter_reports_a_pid_that_cannot_exist(self, capsys):
        """VERIFY-B5i VB-F6: the AF-AP-55 OSError guard, deterministically.
        Its only coverage was the race above, which is SILENT on an idle box
        (mutant RESAMPLE-NO-OSERROR-GUARD: 2 passed idle, dies only under
        load).  A pid above /proc/sys/kernel/pid_max can never be held by a
        process, so the readlink always raises -- the helper must return None
        and say why on stderr, never propagate.  Deleting the try/except makes
        this raise FileNotFoundError on any box."""
        pid_max = int(Path("/proc/sys/kernel/pid_max").read_text().strip())
        assert _reread_interpreter(pid_max + 1) is None
        err = capsys.readouterr().err
        assert "agent interpreter re-sample: exited before identity" in err, (
            "the guard swallowed the reason instead of naming it: %r" % err)

    def test_reread_interpreter_skips_the_hash_for_a_known_interpreter(self):
        """The single-stage short circuit the closure depends on: when the
        realpath is the one already recorded, the helper returns it with NO
        sha (re-hashing cost +100 ms per leg) and the caller keeps the record
        as it stands.  Without this the lift would have re-introduced that
        cost on every leg."""
        me = os.readlink("/proc/%d/exe" % os.getpid())
        assert _reread_interpreter(os.getpid(), me) == (me, None)
        rp, sha = _reread_interpreter(os.getpid(), "/nonexistent/interpreter")
        assert rp == me and sha == _sha256_file(me)


# ---------------------------------------------------------------------------
# F-B5e-1 / F-B5g-1: doc-anchor guard via the PINNED SOURCE as the oracle
# ---------------------------------------------------------------------------
class TestDocstringAnchor:
    def test_shutdown_prose_matches_the_pinned_source(self, tmp_path):
        """The prose is joined to the vendored source by EQUALITY, not by a
        word list (VERIFY-B5h F1/F5/F12/F13).  In order:
        (a) premise -- the vendored file is the pinned one (sha256), asserted
            FIRST so a tampered oracle can never be read as agreement;
        (b) facts DERIVED from it -- the source names no terminate signal, the
            group-kill helper uses the un-catchable one, the kill line precedes
            the bounded wait, the wait constant is unique before the test
            module, and both function line ranges;
        (c) EQUALITY -- the expected sentence is BUILT from those facts (the
            seconds parsed out of the source, the two halves ordered by the
            derived line order) and compared to PINNED_SHUTDOWN_CLAUSE with
            ``==``.  A false constant consistent across every site -- which is
            what survived the count-and-substring form -- fails here;
        (d) the tee's module docstring carries that sentence verbatim
            (per-site presence, not a file-wide count);
        (e) every acp.rs citation in BOTH scope files equals the derived
            ranges, so the numbers are asserted rather than typed;
        (f) the negatives -- the module docstring restates the bound nowhere
            outside the clause, and the five reference sites carry only the
            reference;
        (g) STRUCTURE, not a named list (VERIFY-B5i VB-F2/VB-F3): (g1) every
            sentence of the module docstring after the introduction that names
            the client must be the clause itself, so a PARAPHRASE beside it
            cannot survive by carrying neither banned token; (g2) over BOTH
            scope files whole, with the clause's own sites blanked out, no
            two-line window may carry both a kill token and the derived bound
            -- so a false sentence is inadmissible ANYWHERE in either file,
            not merely at the six places (f) can name.
        FALSECONST-ORDER, SITECOUNT-DUP, SEVENTH-SITE, SEVENTH-SITE-PARAPHRASE,
        SIXTH-SITE-TESTDOC, SIXTH-SITE-TEECOMMENT, MIRROR-3SITE,
        MIRROR-3SITE-ORDER, CITE-421, CITE-421-TEST, CITE-KPG-2324,
        DOCSTRING-ORDER, DOCSTRING-WRONGEVENT, DOCSTRING-HYBRID, CONST-ORDER,
        CONST-WRONGEVENT, COMMENT-TERM and TESTDOC-TERM must all die.
        LIMIT: (g1) keys on the name the clause itself uses.  A false sentence
        that speaks of the client without naming it, and without pairing a
        kill token with the bound, is outside both (g1) and (g2).
        LIMIT: while the sha256 holds, the derived facts in (b) cannot go red
        -- they are a pure function of bytes the premise pins.  Their value
        arrives on an upstream bump, when the constant is updated and they
        become the semantic guard on the new file; (c)-(f) are what guard the
        prose today."""
        # --- (a) premise: the vendored oracle is the pinned file ---
        oracle = VENDORED_ACP_RS.read_text()
        oracle_sha = hashlib.sha256(VENDORED_ACP_RS.read_bytes()).hexdigest()
        assert oracle_sha == VENDORED_ACP_RS_SHA256, (
            "vendored acp.rs sha256 mismatch: %s != %s"
            % (oracle_sha, VENDORED_ACP_RS_SHA256))

        # --- (b) mechanical facts, DERIVED from the source ---
        assert oracle.count("SIGTERM") == 0, (
            "acp.rs mentions SIGTERM %d times, expected 0" % oracle.count("SIGTERM"))
        lines = oracle.splitlines()

        def _fn_end(start):
            """Line of the closing brace at the fn's own indent."""
            indent = len(lines[start - 1]) - len(lines[start - 1].lstrip())
            for i in range(start, len(lines)):
                if (lines[i].strip() == "}"
                        and len(lines[i]) - len(lines[i].lstrip()) == indent):
                    return i + 1
            return None

        kpg_start = None
        for i, line in enumerate(lines, 1):
            if "fn kill_process_group" in line and "pub" not in line.split("fn")[0].split("//")[-1]:
                # The non-test fn (not inside a comment)
                if line.strip().startswith("//"):
                    continue
                kpg_start = i
                break
        assert kpg_start is not None, "fn kill_process_group not found"
        kpg_end = _fn_end(kpg_start)
        assert kpg_end is not None, "fn kill_process_group has no closing brace"
        kpg_body = "\n".join(lines[kpg_start - 1:kpg_end])
        assert "killpg(" in kpg_body, "kill_process_group does not contain killpg("
        assert "Signal::SIGKILL" in kpg_body, "kill_process_group does not use SIGKILL"

        # shutdown: kill PRECEDES the bounded wait
        sd_start = None
        for i, line in enumerate(lines, 1):
            if "pub async fn shutdown" in line:
                sd_start = i
                break
        assert sd_start is not None, "pub async fn shutdown not found"
        sd_end = _fn_end(sd_start)
        assert sd_end is not None, "pub async fn shutdown has no closing brace"
        kill_line = None
        wait_line = None
        wait_secs = None
        for i in range(sd_start - 1, min(sd_start + 30, len(lines))):
            text = lines[i]
            if kill_line is None and ("kill_process_group" in text or "start_kill" in text):
                kill_line = i + 1
            match = re.search(r"from_secs\((\d+)\)", text)
            if wait_line is None and match:
                wait_line = i + 1
                wait_secs = int(match.group(1))
        assert kill_line is not None, "no kill in shutdown()"
        assert wait_line is not None, "no bounded wait in shutdown()"
        assert kill_line < wait_line, (
            "kill at :%d does NOT precede the bounded wait at :%d"
            % (kill_line, wait_line))

        # the wait constant is unique before the test module boundary
        cfg_test_mod = None
        for i, line in enumerate(lines, 1):
            if line.strip() == "#[cfg(test)]" and i > 2000:
                for j in range(i, min(i + 3, len(lines))):
                    if "mod tests" in lines[j]:
                        cfg_test_mod = i
                        break
                if cfg_test_mod is not None:
                    break
        assert cfg_test_mod is not None, "#[cfg(test)] mod tests not found"
        prod_text = "\n".join(lines[:cfg_test_mod - 1])
        needle = "from_secs(%d)" % wait_secs
        assert prod_text.count(needle) == 1, (
            "%s appears %d times before #[cfg(test)] mod tests, expected 1"
            % (needle, prod_text.count(needle)))
        assert sd_start == 422, "shutdown starts at :%d, expected :422" % sd_start
        assert kpg_start == 2323, (
            "kill_process_group starts at :%d, expected :2323" % kpg_start)

        # --- (c) EQUALITY: the sentence is BUILT from the derived facts ---
        # The two halves are text, so bind each one to the facts its OWN
        # derived range carries: the signal and the helper the group kill
        # names, and the subject/method/seconds the bounded wait names.
        # Without this the halves are a third hand-typed copy and swapping
        # them (with the constant and the docstring) states the reverse order
        # and still passes the equality below -- VERIFY-B5i VB-F1, mutants
        # MIRROR-3SITE-ORDER and MIRROR-3SITE.
        kill_sig_m = re.search(r"Signal::(SIG[A-Z0-9]+)", kpg_body)
        kill_helper_m = re.search(r"(\w+)\(Pid::", kpg_body)
        assert kill_sig_m and kill_helper_m, (
            "the derived kill range names no Signal::SIG* and <helper>(Pid::: %r"
            % kpg_body)
        kill_sig, kill_helper = kill_sig_m.group(1), kill_helper_m.group(1)
        wait_call_m = re.search(r"self\.(\w+)\.(\w+)\(\)", lines[wait_line - 1])
        assert wait_call_m, (
            "the bounded wait line names no self.<subject>.<method>(): %r"
            % lines[wait_line - 1])
        wait_subject, wait_method = wait_call_m.group(1), wait_call_m.group(2)
        secs_token = "%d s" % wait_secs

        kill_half = "SIGKILLs the group (killpg)"
        wait_half = "waits up to %d s for the child to exit" % wait_secs
        assert kill_sig in kill_half and kill_helper in kill_half, (
            "the kill half %r does not name the signal (%s) and the helper (%s) "
            "the derived kill range uses" % (kill_half, kill_sig, kill_helper))
        assert secs_token in wait_half and "waits" in wait_half, (
            "the wait half %r does not name the derived bound (%s)"
            % (wait_half, secs_token))
        assert wait_method in wait_half and wait_subject in wait_half, (
            "the wait half %r does not name what the source waits on "
            "(self.%s.%s())" % (wait_half, wait_subject, wait_method))
        first_half, second_half = ((kill_half, wait_half) if kill_line < wait_line
                                   else (wait_half, kill_half))
        expected_clause = "buzz-acp %s first and then %s" % (first_half, second_half)
        assert PINNED_SHUTDOWN_CLAUSE == expected_clause, (
            "PINNED_SHUTDOWN_CLAUSE is not the sentence acp.rs derives:\n"
            "  constant: %r\n  derived : %r" % (PINNED_SHUTDOWN_CLAUSE, expected_clause))

        # --- (d) the tee's module docstring carries that sentence verbatim ---
        def _ws_norm(text):
            return re.sub(r"[\s#]+", " ", text)

        clause_norm = _ws_norm(PINNED_SHUTDOWN_CLAUSE).strip()
        tee_src = Path(TEE).read_text()
        test_src = Path(__file__).read_text()
        doc = ast.get_docstring(ast.parse(tee_src))
        assert doc is not None, "frame_tee.py has no module docstring"
        doc_norm = _ws_norm(doc)
        assert clause_norm in doc_norm, (
            "frame_tee.py's module docstring does not carry PINNED_SHUTDOWN_CLAUSE "
            "verbatim -- that docstring is the one place the sentence is spelled out")

        # --- (e) every citation equals the DERIVED ranges ---
        cites_shutdown = []
        cites_kpg = []
        for name, text in (("frame_tee.py", tee_src), ("test file", test_src)):
            norm = _ws_norm(text)
            for match in re.finditer(r"acp\.rs:(\d+)-(\d+)", norm):
                cites_shutdown.append((name, int(match.group(1)), int(match.group(2))))
            for match in re.finditer(r"``:(\d+)-(\d+)``", norm):
                cites_kpg.append((name, int(match.group(1)), int(match.group(2))))
        assert cites_shutdown, "no acp.rs:<start>-<end> citation in either scope file"
        assert cites_kpg, "no ``:<start>-<end>`` citation in either scope file"
        for name, start, end in cites_shutdown:
            assert (start, end) == (sd_start, sd_end), (
                "%s cites acp.rs:%d-%d; shutdown() spans %d-%d"
                % (name, start, end, sd_start, sd_end))
        for name, start, end in cites_kpg:
            assert (start, end) == (kpg_start, kpg_end), (
                "%s cites :%d-%d; kill_process_group spans %d-%d"
                % (name, start, end, kpg_start, kpg_end))

        # --- (f) the negative direction ---
        # Nothing in the module docstring may restate the bound outside the clause.
        residue = doc_norm.replace(clause_norm, " ")
        for token in (kill_helper, secs_token):
            assert token not in residue, (
                "frame_tee.py's module docstring states the shutdown bound outside "
                "PINNED_SHUTDOWN_CLAUSE (%r); the clause is the only place it may "
                "be stated" % token)
        head = doc.split("The SIGTERM path")[0]
        assert "SIGTERM" not in head, (
            "the module docstring names SIGTERM before 'The SIGTERM path' -- "
            "buzz-acp sends no terminate signal, and that is the claim this "
            "increment exists to keep out of the prose")
        # The five reference sites, enumerated BY NAME.
        ref_norm = _ws_norm(CLAUSE_REF).strip()
        sites = []
        tee_lines = tee_src.splitlines()
        for anchor in ("while to.is_alive():", "while ti.is_alive():"):
            hits = [i for i, line in enumerate(tee_lines) if line.strip() == anchor]
            assert len(hits) == 1, (
                "expected exactly one %r in frame_tee.py, found %d" % (anchor, len(hits)))
            i = hits[0] - 1
            block = []
            while i >= 0 and tee_lines[i].strip().startswith("#"):
                block.append(tee_lines[i])
                i -= 1
            sites.append(("frame_tee.py comment above '%s'" % anchor,
                          "\n".join(reversed(block))))
        test_tree = ast.parse(test_src)
        for fname in ("test_never_reading_client",
                      "test_grandchild_never_closes_sigterm_required",
                      "test_stdin_reader_done_false_when_client_never_closes"):
            defs = [n for n in ast.walk(test_tree)
                    if isinstance(n, ast.FunctionDef) and n.name == fname]
            assert len(defs) == 1, "expected exactly one def %s, found %d" % (fname, len(defs))
            site_doc = ast.get_docstring(defs[0])
            assert site_doc is not None, "%s has no docstring" % fname
            sites.append(("test docstring %s" % fname, site_doc))
        assert len(sites) == 5, "expected 5 reference sites, built %d" % len(sites)
        for name, text in sites:
            assert ref_norm in _ws_norm(text), (
                "%s does not carry the reference %r" % (name, CLAUSE_REF))
            for token in ("SIGTERM", kill_sig, kill_helper, secs_token):
                assert token not in text, (
                    "%s states the shutdown bound itself (%r); it may carry only "
                    "the reference to PINNED_SHUTDOWN_CLAUSE" % (name, token))

        # --- (g) ONE sentence in the repo, structurally (VB-F2 / VB-F3) ---
        # (g1) the module docstring speaks for buzz-acp exactly twice: the
        # introduction and the clause.  A PARAPHRASE beside the clause carries
        # neither banned token and evaded the residue blacklist above
        # (mutant SEVENTH-SITE-PARAPHRASE).
        doc_sentences = re.split(r"(?<=\.)\s+", doc_norm.strip())
        buzz_sentences = [sent for sent in doc_sentences if "buzz-acp" in sent]
        assert len(buzz_sentences) == 2, (
            "frame_tee.py's module docstring has %d buzz-acp sentences, "
            "expected only the client introduction and PINNED_SHUTDOWN_CLAUSE: %r"
            % (len(buzz_sentences), buzz_sentences))
        assert "(client)" in buzz_sentences[0], (
            "the module docstring's first buzz-acp sentence is not the client "
            "introduction: %r" % buzz_sentences[0])
        clause_sentence = clause_norm + "."
        assert buzz_sentences[1] == clause_sentence, (
            "the module docstring's shutdown sentence is not exactly "
            "PINNED_SHUTDOWN_CLAUSE: %r" % buzz_sentences[1])

        # (g2) over BOTH files WHOLE, not a named list: outside the clause's
        # own sites, no two-line window may carry both a kill token and the
        # derived bound.  Replaces two literal regexes that matched one exact
        # phrase, which a reworded false sentence walked straight past
        # (mutants SIXTH-SITE-TESTDOC, SIXTH-SITE-TEECOMMENT).  The bound is
        # word-bounded: the bare form also matches text like "F5 seq".
        def _q_norm(text):
            return re.sub(r"[\s#\"']+", " ", text)

        # Mask only the clause's exact words, preserving any text added beside
        # it on the same source line.  Blanking an entire line would let a
        # second false sentence ride inside that exemption.
        clause_rx = re.compile(
            re.escape(PINNED_SHUTDOWN_CLAUSE).replace(
                r"\ ", r"[\s#\"']+"))

        def _mask_clause(match):
            return re.sub(r"[^\n]", " ", match.group(0))

        secs_re = re.compile(r"(?<!\w)%d\s+s(?!\w)" % wait_secs)
        kill_tokens = (kill_sig, kill_helper)
        proximity = []
        blanked = {}
        for name, text in (("frame_tee.py", tee_src), ("test file", test_src)):
            masked, blanked[name] = clause_rx.subn(_mask_clause, text)
            src_lines = masked.splitlines()
            for i in range(len(src_lines)):
                window = _q_norm("\n".join(src_lines[i:i + 2]))
                if any(t in window for t in kill_tokens) and secs_re.search(window):
                    proximity.append("%s:%d" % (name, i + 1))
        # de-vacuous: the exemption must have found precisely the constant and
        # the module-docstring sentence.  The test file builds the clause from
        # derived halves and must not spell it as a third copy.
        assert blanked["frame_tee.py"] == 2, (
            "the ban masked %d clause copies in frame_tee.py, expected its "
            "constant and module-docstring sites only" % blanked["frame_tee.py"])
        assert blanked["test file"] == 0, (
            "the test file spells the clause out at %d site(s); it must build "
            "it from the derived halves instead" % blanked["test file"])
        assert not proximity, (
            "a kill token and the derived bound sit within two lines of each "
            "other outside PINNED_SHUTDOWN_CLAUSE's own sites: %s" % proximity)

        # --- no SIGTERM attribution to buzz-acp in EITHER file ---
        # Split the needle so this assertion message does not match itself
        _banned = r"buzz-acp'?s?\s+shut" + r"down\s+responsibility"
        assert not re.search(_banned, tee_src + test_src), (
            "a site still attributes SIGTERM to buzz-acp")

    def test_docstring_pins_the_meaning_not_the_tokens(self, tmp_path):
        """F-B5e-1/F4: the module docstring pins the MEANING of the shutdown
        bound -- the group kill, that the un-catchable signal cannot be
        handled, the last RUNNING status.  The source's real ORDER is pinned by
        equality in the oracle test above, and the two literal 'after' regexes
        that used to live here and there are replaced by that test's (g2)
        derived proximity ban over both files whole (VERIFY-B5i VB-F3): a
        literal regex only ever matched one phrasing.
        DOCSTRING-HYBRID and COMMENT-TERM must die."""
        src = Path(TEE).read_text()
        doc = ast.get_docstring(ast.parse(src))
        assert doc is not None, "module docstring missing"
        assert "killpg" in doc, "module docstring does not name killpg"
        assert "SIGKILL cannot be handled" in doc, (
            "module docstring does not state SIGKILL cannot be handled")
        assert "last RUNNING status" in doc, (
            "module docstring does not mention last RUNNING status")
        assert not re.search(r"SIGTERM path[^.]*(covers it|bounds)", doc), (
            "docstring still claims the SIGTERM path bounds a wedged leg")
