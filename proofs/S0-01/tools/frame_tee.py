#!/usr/bin/env python3
"""stdio proxy: preserve raw ACP JSON-RPC frames between buzz-acp (client) and hermes-acp (agent).

Writes into S0_01_FRAMEDIR:
  timeline.jsonl               - interleaved, seq-numbered, under ONE lock
  frames-client-to-agent.jsonl - byte-identical relay c2a
  frames-agent-to-client.jsonl - byte-identical relay a2c
  runtime-identity.json        - written once at spawn (includes tee_pid)
  tee-status.json              - RUNNING status, rewritten after every recorded
                                 frame under the timeline lock (A21d)

After the agent exits, the tee drains BOTH pumps to EOF -- there is no
stall timeout on either side.  A client that never closes (c2a) or a
grandchild that holds the agent's stdout (a2c) keeps the tee alive.
buzz-acp SIGKILLs the group (killpg) first and then waits up to 5 s
for the child to exit.
The cited source ranges are ``acp.rs:422-444`` and ``:2323-2329``,
pinned ``1c8321cd``.  SIGKILL cannot be handled, so the leg's evidence
is its last RUNNING status (A21d).

The SIGTERM path below covers an operator/systemd TERM, not the
shutdown pinned in PINNED_SHUTDOWN_CLAUSE above.
The only uncovered SIGTERM window is Python interpreter startup before
the handler install (default disposition: rc -15, no status file).  The
``final`` field is true only on the clean-exit write; the SIGTERM write
is non-final (final=false, exit fields null, write_errors includes
"terminated: SIGTERM", exit 70).

A frame the client wrote before the tee exits MUST be recorded in
frames-client-to-agent.jsonl, or the tee exits 70 (EX_SOFTWARE).  An agent
that exits without consuming the full client stream causes exit 70 when any
recorded c2a frame was not forwarded into the agent's stdin pipe (note:
"forwarded" means written into the pipe, not received or processed by
the agent).
"""
# imported by tests/test_s0_01_frame_tee.py -- keep this module import-side-effect free
import base64
import datetime
import hashlib
import json
import math
import os
import signal
import subprocess
import sys
import threading
import time

# The canonical one-sentence summary of buzz-acp's shutdown behaviour, derived
# from the vendored source (acp.rs at pinned commit 1c8321cd).  The module
# docstring carries this clause verbatim; other comments and docstrings refer to
# this constant without restating it, so there is one prose sentence to audit.
PINNED_SHUTDOWN_CLAUSE = (
    "buzz-acp SIGKILLs the group (killpg) first and then waits up to 5 s"
    " for the child to exit"
)


class _Terminated(BaseException):
    """Raised by the SIGTERM handler in the main thread.

    The handler takes NO lock -- it raises this exception, which unwinds any
    held lock context (``with lock:`` releases on unwind) and is caught at
    the top level of main().
    """


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _utc_now():
    dt = datetime.datetime.now(datetime.timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _reread_interpreter(pid, known=None):
    """AF-AP-55: re-read pid's interpreter, or say why it could not be read.

    Returns ``(realpath, sha256)`` for a new interpreter, ``(realpath, None)``
    when the realpath is already ``known`` (the spawn-time reading names it, and
    re-hashing it cost +100 ms on every leg), or ``None`` when the process
    exited before either read -- the caller then keeps the earlier reading and
    the reason goes to stderr, because the record's key set is fixed by
    check_acp_conformance.py.

    Module level, not a closure, so the exited-before-identity branch has a
    deterministic test: a pid above /proc/sys/kernel/pid_max, which no process
    can hold (VERIFY-B5i VB-F6 -- the closure's only coverage was a race that
    is silent on an idle box).
    """
    try:
        rp = os.readlink("/proc/%d/exe" % pid)
    except (OSError, IOError) as exc:
        print("frame_tee: agent interpreter re-sample: exited before"
              " identity (%s)" % exc, file=sys.stderr)
        return None
    if rp == known:
        return rp, None
    try:
        return rp, _sha256_file(rp)
    except (OSError, IOError) as exc:
        print("frame_tee: agent interpreter re-sample: exited before"
              " identity (%s)" % exc, file=sys.stderr)
        return None


def _read_lines_from_fd(fd):
    """Read from a raw fd, yield complete lines (including terminator bytes).

    Uses os.read to avoid BufferedReader lock issues at interpreter shutdown
    (V-c F1: daemon thread holding BufferedReader lock causes SIGABRT).
    Also handles partial last lines without a terminator.
    """
    buf = b""
    while True:
        try:
            chunk = os.read(fd, 65536)
        except OSError:
            break
        if not chunk:
            break
        buf += chunk
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            yield line + b"\n"
    if buf:
        yield buf  # partial last line without terminator


def _reject_nan_inf(constant):
    """parse_constant callback: reject NaN/Infinity so they take the raw/raw_b64 branch."""
    raise ValueError(constant)


def _reject_overflow_float(s):
    """parse_float callback: reject non-finite floats (e.g. 1e999 -> inf)."""
    val = float(s)
    if not math.isfinite(val):
        raise ValueError(s)
    return val


def main():
    framedir = os.environ.get("S0_01_FRAMEDIR")
    if framedir is None:
        print("frame_tee: S0_01_FRAMEDIR is not set", file=sys.stderr)
        raise SystemExit(64)
    if not framedir:
        print("frame_tee: S0_01_FRAMEDIR is empty", file=sys.stderr)
        raise SystemExit(64)
    if os.path.lexists(framedir) and not os.path.isdir(framedir):
        print("frame_tee: S0_01_FRAMEDIR is not a directory: %s" % framedir, file=sys.stderr)
        raise SystemExit(64)
    agent = os.environ.get("S0_01_AGENT")
    if agent is None:
        print("frame_tee: S0_01_AGENT is not set", file=sys.stderr)
        raise SystemExit(64)
    if not agent:
        print("frame_tee: S0_01_AGENT is empty", file=sys.stderr)
        raise SystemExit(64)
    if not (os.path.isfile(agent) and os.access(agent, os.X_OK)):
        print("frame_tee: S0_01_AGENT is not an executable file: %s" % agent,
              file=sys.stderr)
        raise SystemExit(64)
    os.makedirs(framedir, exist_ok=True)

    # --- All state that _write_status and the _Terminated handler need,
    #     initialised BEFORE the handler install so the except path never
    #     hits an uninitialised closure variable. ---
    proc = None  # pre-init: handler checks before terminate

    lock = threading.RLock()
    seq = [0]
    state = {
        "recorded_c2a": 0, "recorded_a2c": 0,
        "forwarded_c2a": 0, "forwarded_a2c": 0,
        "write_errors": [],
        "stdin_reader_done": False,
    }
    _error_counts = {}

    def _record_write_error(arm, direction, error_text):
        """Append or update a write-error entry, bounded to one per (arm, direction).

        First occurrence keeps the exact text; subsequent occurrences update to
        ``<arm> <dir>: <error> (N occurrences)``.  Must be called under ``lock``.
        """
        key = (arm, direction)
        base = "%s %s: %s" % (arm, direction, error_text)
        count = _error_counts.get(key, 0) + 1
        _error_counts[key] = count
        if count == 1:
            state["write_errors"].append(base)
        else:
            for i, e in enumerate(state["write_errors"]):
                if e.startswith("%s %s:" % (arm, direction)):
                    state["write_errors"][i] = "%s (%d occurrences)" % (base, count)
                    break

    status_lock = threading.Lock()
    _status_path = os.path.join(framedir, "tee-status.json")
    _status_tmp = os.path.join(framedir, ".tee-status.tmp")
    _status_write_failures = [0]

    def _write_status(final=False, exit_code_val=None, agent_rc=None):
        """Snapshot counters under ``lock``, write atomically under ``status_lock``.

        Returns True on success, False on write failure.
        """
        with lock:
            snap_seq = seq[0]
            snap_rec_c2a = state["recorded_c2a"]
            snap_rec_a2c = state["recorded_a2c"]
            snap_fwd_c2a = state["forwarded_c2a"]
            snap_fwd_a2c = state["forwarded_a2c"]
            snap_stdin_done = state["stdin_reader_done"]
            snap_errors = list(state["write_errors"])
        _drained = (snap_fwd_a2c == snap_rec_a2c
                    and snap_fwd_c2a == snap_rec_c2a)
        obj = {
            "final": final,
            "agent_returncode": agent_rc if final else None,
            "drained": _drained,
            "stdin_reader_done": snap_stdin_done,
            "recorded_c2a": snap_rec_c2a,
            "recorded_a2c": snap_rec_a2c,
            "forwarded_c2a": snap_fwd_c2a,
            "forwarded_a2c": snap_fwd_a2c,
            "write_errors": snap_errors,
            "exit_code": exit_code_val if final else None,
            "updated_seq": snap_seq,
            "updated_utc": _utc_now(),
        }
        with status_lock:
            try:
                with open(_status_tmp, "w") as f:
                    json.dump(obj, f, indent=2)
                    f.write("\n")
                os.replace(_status_tmp, _status_path)
                return True
            except OSError:
                _status_write_failures[0] += 1
                return False

    c2a = os.path.join(framedir, "frames-client-to-agent.jsonl")
    a2c = os.path.join(framedir, "frames-agent-to-client.jsonl")

    # --- SIGTERM handler (F11/F13): raise _Terminated, no lock.
    #     Installed AFTER all _write_status dependencies and BEFORE any
    #     statement that could take appreciable time (Popen, sha256 reads).
    #     The try: immediately follows -- ZERO statements between.
    #     The only uncovered window is Python interpreter startup BEFORE
    #     this install (the default SIGTERM disposition: rc -15, no status).
    def _sigterm_handler(signum, _frame):
        raise _Terminated()

    signal.signal(signal.SIGTERM, _sigterm_handler)
    try:
        try:
            proc = subprocess.Popen([agent], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        except OSError as exc:
            print("frame_tee: cannot spawn S0_01_AGENT %s: %s" % (agent, exc),
                  file=sys.stderr)
            raise SystemExit(64)

        # --- runtime-identity.json (written at spawn) ---
        tee_path = os.path.realpath(__file__)
        agent_realpath = os.path.realpath(agent)
        interp_realpath = None
        interp_sha256 = None
        try:
            interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
            interp_sha256 = _sha256_file(interp_realpath)
        except (OSError, IOError):
            pass

        identity = {
            "tee_path": tee_path,
            "tee_sha256": _sha256_file(tee_path),
            "tee_pid": os.getpid(),
            "agent_argv": [agent],
            "agent_realpath": agent_realpath,
            "agent_entrypoint_sha256": _sha256_file(agent_realpath),
            "agent_child_pid": proc.pid,
            "agent_interpreter_realpath": interp_realpath,
            "agent_interpreter_sha256": interp_sha256,
            "python_dont_write_bytecode": os.environ.get("PYTHONDONTWRITEBYTECODE") == "1",
            "spawned_at_utc": _utc_now(),
        }
        _identity_path = os.path.join(framedir, "runtime-identity.json")
        _identity_tmp = os.path.join(framedir, ".runtime-identity.tmp")
        with open(_identity_path, "w") as f:
            json.dump(identity, f, indent=2)
            f.write("\n")

        _late_sampled = [False]

        def _resample_interpreter():
            """AF-AP-55: re-read the agent's interpreter at the FIRST a2c byte.

            A two-stage agent (a wrapper that ``exec``s its real interpreter) is
            still the wrapper at Popen time, so the spawn-time reading names the
            wrapper.  The reading that matters is the one taken when the agent
            first speaks.  Ported from ``tools/acp_probe.py:296-320`` -- same
            field names, same "later reading wins" rule.

            The child can exit between its first byte and the readlink: that is
            an OSError, and it keeps the early reading (the record's key set is
            fixed by check_acp_conformance.py, so the reason goes to stderr).
            Both reads and that reason live in the module-level
            _reread_interpreter so the OSError branch is deterministically
            testable; a (realpath, None) return is the single-stage agent whose
            spawn-time reading already names the interpreter that spoke
            (re-hashing it cost +100 ms per leg: 0.053 s -> 0.156 s per run).
            """
            got = _reread_interpreter(proc.pid,
                                      identity["agent_interpreter_realpath"])
            if got is None or got[1] is None:
                return
            identity["agent_interpreter_realpath"] = got[0]
            identity["agent_interpreter_sha256"] = got[1]
            try:
                with open(_identity_tmp, "w") as f:
                    json.dump(identity, f, indent=2)
                    f.write("\n")
                os.replace(_identity_tmp, _identity_path)
            except OSError as exc:
                print("frame_tee: runtime-identity.json re-write failed: %s" % exc,
                      file=sys.stderr)

        # --- shared timeline file ---
        tl = open(os.path.join(framedir, "timeline.jsonl"), "ab")

        def pump_fd(fd, dst, direction, dir_path, close_dst):
            """Pump from a raw file descriptor (stdin fd 0)."""
            df = open(dir_path, "ab")
            forward_broken = False
            try:
                for line in _read_lines_from_fd(fd):
                    text = line.decode("utf-8", errors="replace")
                    if text.endswith("\r\n"):
                        stripped = text[:-2]
                    elif text.endswith("\n"):
                        stripped = text[:-1]
                    else:
                        stripped = text
                    try:
                        frame = json.loads(stripped, parse_constant=_reject_nan_inf,
                                           parse_float=_reject_overflow_float)
                        entry = {"dir": direction, "frame": frame}
                    except (json.JSONDecodeError, ValueError):
                        raw_b64 = base64.b64encode(line).decode("ascii")
                        entry = {"dir": direction, "frame": None,
                                 "raw": stripped, "raw_b64": raw_b64}
                    with lock:
                        t_utc = _utc_now()
                        t_mono = time.monotonic_ns()
                        seq[0] += 1
                        entry["seq"] = seq[0]
                        entry["t_utc"] = t_utc
                        entry["t_mono_ns"] = t_mono
                        # F17: timeline FIRST, then directional
                        try:
                            tl.write(json.dumps(entry, separators=(",", ":")).encode("utf-8") + b"\n")
                            tl.flush()
                        except OSError as e:
                            _record_write_error("timeline", direction, str(e))
                        try:
                            df.write(line)
                            df.flush()
                        except OSError as e:
                            _record_write_error("directional", direction, str(e))
                        state["recorded_%s" % direction] += 1
                        # R2: status snapshot inside the timeline lock
                        _write_status()
                    # forward outside the lock (can block on pipe full)
                    forward_error = None
                    if not forward_broken:
                        try:
                            dst.write(line)
                            dst.flush()
                        except BrokenPipeError:
                            forward_error = "forward %s: BrokenPipeError" % direction
                            forward_broken = True
                            if close_dst:
                                try:
                                    dst.close()
                                except Exception:
                                    pass
                        except OSError as e:
                            forward_error = "forward %s: %s" % (direction, e)
                            forward_broken = True
                            if close_dst:
                                try:
                                    dst.close()
                                except Exception:
                                    pass
                    # R2: update forwarded under the timeline lock
                    with lock:
                        if forward_error is not None:
                            state["write_errors"].append(forward_error)
                        elif not forward_broken:
                            state["forwarded_%s" % direction] += 1
            finally:
                try:
                    df.close()
                except OSError as e:
                    with lock:
                        state["write_errors"].append("directional %s close: %s" % (direction, e))
                if direction == "c2a":
                    state["stdin_reader_done"] = True
                if close_dst and not forward_broken:
                    try:
                        dst.close()
                    except Exception:
                        pass

        def pump_pipe(src, dst, direction, dir_path, close_dst):
            """Pump from a subprocess pipe (proc.stdout)."""
            df = open(dir_path, "ab")
            forward_broken = False
            try:
                while True:
                    line = src.readline()
                    if not line:
                        break
                    if not _late_sampled[0]:
                        # AF-AP-55: the first a2c byte is the identity sample point
                        _late_sampled[0] = True
                        _resample_interpreter()
                    text = line.decode("utf-8", errors="replace")
                    if text.endswith("\r\n"):
                        stripped = text[:-2]
                    elif text.endswith("\n"):
                        stripped = text[:-1]
                    else:
                        stripped = text
                    try:
                        frame = json.loads(stripped, parse_constant=_reject_nan_inf,
                                           parse_float=_reject_overflow_float)
                        entry = {"dir": direction, "frame": frame}
                    except (json.JSONDecodeError, ValueError):
                        raw_b64 = base64.b64encode(line).decode("ascii")
                        entry = {"dir": direction, "frame": None,
                                 "raw": stripped, "raw_b64": raw_b64}
                    with lock:
                        t_utc = _utc_now()
                        t_mono = time.monotonic_ns()
                        seq[0] += 1
                        entry["seq"] = seq[0]
                        entry["t_utc"] = t_utc
                        entry["t_mono_ns"] = t_mono
                        try:
                            tl.write(json.dumps(entry, separators=(",", ":")).encode("utf-8") + b"\n")
                            tl.flush()
                        except OSError as e:
                            _record_write_error("timeline", direction, str(e))
                        try:
                            df.write(line)
                            df.flush()
                        except OSError as e:
                            _record_write_error("directional", direction, str(e))
                        state["recorded_%s" % direction] += 1
                        # R2: status snapshot inside the timeline lock
                        _write_status()
                    # forward outside the lock (can block on pipe full)
                    forward_error = None
                    if not forward_broken:
                        try:
                            dst.write(line)
                            dst.flush()
                        except BrokenPipeError:
                            forward_error = "forward %s: BrokenPipeError" % direction
                            forward_broken = True
                        except OSError as e:
                            forward_error = "forward %s: %s" % (direction, e)
                            forward_broken = True
                    # R2: update forwarded under the timeline lock
                    with lock:
                        if forward_error is not None:
                            state["write_errors"].append(forward_error)
                        elif not forward_broken:
                            state["forwarded_%s" % direction] += 1
            finally:
                try:
                    df.close()
                except OSError as e:
                    with lock:
                        state["write_errors"].append("directional %s close: %s" % (direction, e))
                if close_dst and not forward_broken:
                    try:
                        dst.close()
                    except Exception:
                        pass

        # stdin pump: use raw fd to avoid BufferedReader lock SIGABRT at shutdown (V-c F1)
        stdin_fd = sys.stdin.buffer.fileno()
        ti = threading.Thread(target=pump_fd,
                              args=(stdin_fd, proc.stdin, "c2a", c2a, True),
                              daemon=True)
        to = threading.Thread(target=pump_pipe,
                              args=(proc.stdout, sys.stdout.buffer, "a2c", a2c, False),
                              daemon=True)

        # F10: initial status (12 keys, all zeros) before the first frame
        _write_status()

        ti.start()
        to.start()
        # Wait for the agent process to exit
        proc.wait()
        # R1: drain a2c until EOF -- no stall timeout.  A grandchild that
        # holds the agent's stdout keeps the tee alive;
        # buzz-acp's shutdown bound: see PINNED_SHUTDOWN_CLAUSE in frame_tee.py
        while to.is_alive():
            time.sleep(0.1)
            _write_status()
        # R1: drain c2a until client EOF -- no stall timeout on the c2a side.
        # A client that never closes keeps the tee alive;
        # buzz-acp's shutdown bound: see PINNED_SHUTDOWN_CLAUSE in frame_tee.py
        while ti.is_alive():
            time.sleep(0.1)
            _write_status()
        try:
            tl.close()
        except OSError:
            pass
        # Determine drain status: forwarded everything recorded in BOTH directions?
        drained = (state["forwarded_a2c"] == state["recorded_a2c"]
                   and state["forwarded_c2a"] == state["recorded_c2a"])
        # Compute exit code (V-c F8 / A21b: signal-killed agent -> 128+signal)
        rc = proc.returncode
        if rc < 0:
            agent_code = 128 + (-rc)
        else:
            agent_code = rc
        # Exit code: agent's code when drained and error-free, else 70 (EX_SOFTWARE)
        if drained and not state["write_errors"]:
            exit_code = agent_code
        else:
            exit_code = 70
        # Final status write (A21d)
        ok = _write_status(final=True, exit_code_val=exit_code, agent_rc=proc.returncode)
        if not ok:
            exit_code = 70
        if _status_write_failures[0] > 0:
            print("frame_tee: %d tee-status.json write failure(s)"
                  % _status_write_failures[0], file=sys.stderr)
        os._exit(exit_code)
    except _Terminated:
        state["write_errors"].append("terminated: SIGTERM")
        _write_status(final=False)
        # F14: terminate the agent child so it does not outlive the tee.
        # Popen.terminate() -> send_signal() polls first and absorbs
        # ProcessLookupError on an already-exited child (subprocess.py:1866).
        if proc is not None:
            proc.terminate()
        os._exit(70)


if __name__ == "__main__":
    main()
