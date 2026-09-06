#!/usr/bin/env python3
"""stdio proxy: preserve raw ACP JSON-RPC frames between buzz-acp (client) and hermes-acp (agent).

Writes into S0_01_FRAMEDIR:
  timeline.jsonl               - interleaved, seq-numbered, under ONE lock
  frames-client-to-agent.jsonl - byte-identical relay c2a
  frames-agent-to-client.jsonl - byte-identical relay a2c
  runtime-identity.json        - written once at spawn (includes tee_pid)
  tee-status.json              - written at exit (drain status, counters, exit code)
"""
import base64
import datetime
import hashlib
import json
import math
import os
import subprocess
import sys
import threading
import time


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _utc_now():
    dt = datetime.datetime.now(datetime.timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


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
    if os.path.exists(framedir) and not os.path.isdir(framedir):
        print("frame_tee: S0_01_FRAMEDIR is not a directory: %s" % framedir, file=sys.stderr)
        raise SystemExit(64)
    agent = os.environ.get("S0_01_AGENT")
    if agent is None:
        print("frame_tee: S0_01_AGENT is not set", file=sys.stderr)
        raise SystemExit(64)
    os.makedirs(framedir, exist_ok=True)

    proc = subprocess.Popen([agent], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

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
    with open(os.path.join(framedir, "runtime-identity.json"), "w") as f:
        json.dump(identity, f, indent=2)
        f.write("\n")

    # --- shared timeline state ---
    lock = threading.Lock()
    seq = [0]
    tl = open(os.path.join(framedir, "timeline.jsonl"), "ab")

    # --- shared counters for tee-status (P2 drain tracking) ---
    state = {
        "recorded_c2a": 0, "recorded_a2c": 0,
        "forwarded_c2a": 0, "forwarded_a2c": 0,
        "write_errors": [],
        "stdin_reader_done": False,
    }

    def pump_fd(fd, dst, direction, dir_path, close_dst):
        """Pump from a raw file descriptor (stdin fd 0)."""
        df = open(dir_path, "ab")
        try:
            for line in _read_lines_from_fd(fd):
                try:
                    df.write(line)
                    df.flush()
                except OSError as e:
                    state["write_errors"].append("directional %s: %s" % (direction, e))
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
                    with lock:
                        t_utc = _utc_now()
                        t_mono = time.monotonic_ns()
                        seq[0] += 1
                        entry = {"seq": seq[0], "dir": direction, "t_utc": t_utc,
                                 "t_mono_ns": t_mono, "frame": frame}
                        try:
                            tl.write(json.dumps(entry, separators=(",", ":")).encode("utf-8") + b"\n")
                            tl.flush()
                        except OSError as e:
                            state["write_errors"].append("timeline %s seq %d: %s" % (direction, seq[0], e))
                        state["recorded_%s" % direction] += 1
                except (json.JSONDecodeError, ValueError):
                    raw_b64 = base64.b64encode(line).decode("ascii")
                    with lock:
                        t_utc = _utc_now()
                        t_mono = time.monotonic_ns()
                        seq[0] += 1
                        entry = {"seq": seq[0], "dir": direction, "t_utc": t_utc,
                                 "t_mono_ns": t_mono, "frame": None,
                                 "raw": stripped, "raw_b64": raw_b64}
                        try:
                            tl.write(json.dumps(entry, separators=(",", ":")).encode("utf-8") + b"\n")
                            tl.flush()
                        except OSError as e:
                            state["write_errors"].append("timeline %s seq %d: %s" % (direction, seq[0], e))
                        state["recorded_%s" % direction] += 1
                try:
                    dst.write(line)
                    dst.flush()
                    state["forwarded_%s" % direction] += 1
                except BrokenPipeError:
                    state["write_errors"].append("forward %s: BrokenPipeError" % direction)
                    break
        finally:
            df.close()
            if direction == "c2a":
                state["stdin_reader_done"] = True
            if close_dst:
                try:
                    dst.close()
                except Exception:
                    pass

    def pump_pipe(src, dst, direction, dir_path, close_dst):
        """Pump from a subprocess pipe (proc.stdout)."""
        df = open(dir_path, "ab")
        try:
            while True:
                line = src.readline()
                if not line:
                    break
                try:
                    df.write(line)
                    df.flush()
                except OSError as e:
                    state["write_errors"].append("directional %s: %s" % (direction, e))
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
                    with lock:
                        t_utc = _utc_now()
                        t_mono = time.monotonic_ns()
                        seq[0] += 1
                        entry = {"seq": seq[0], "dir": direction, "t_utc": t_utc,
                                 "t_mono_ns": t_mono, "frame": frame}
                        try:
                            tl.write(json.dumps(entry, separators=(",", ":")).encode("utf-8") + b"\n")
                            tl.flush()
                        except OSError as e:
                            state["write_errors"].append("timeline %s seq %d: %s" % (direction, seq[0], e))
                        state["recorded_%s" % direction] += 1
                except (json.JSONDecodeError, ValueError):
                    raw_b64 = base64.b64encode(line).decode("ascii")
                    with lock:
                        t_utc = _utc_now()
                        t_mono = time.monotonic_ns()
                        seq[0] += 1
                        entry = {"seq": seq[0], "dir": direction, "t_utc": t_utc,
                                 "t_mono_ns": t_mono, "frame": None,
                                 "raw": stripped, "raw_b64": raw_b64}
                        try:
                            tl.write(json.dumps(entry, separators=(",", ":")).encode("utf-8") + b"\n")
                            tl.flush()
                        except OSError as e:
                            state["write_errors"].append("timeline %s seq %d: %s" % (direction, seq[0], e))
                        state["recorded_%s" % direction] += 1
                try:
                    dst.write(line)
                    dst.flush()
                    state["forwarded_%s" % direction] += 1
                except BrokenPipeError:
                    state["write_errors"].append("forward %s: BrokenPipeError" % direction)
                    break
        finally:
            df.close()
            if close_dst:
                try:
                    dst.close()
                except Exception:
                    pass

    c2a = os.path.join(framedir, "frames-client-to-agent.jsonl")
    a2c = os.path.join(framedir, "frames-agent-to-client.jsonl")
    # stdin pump: use raw fd to avoid BufferedReader lock SIGABRT at shutdown (V-c F1)
    stdin_fd = sys.stdin.buffer.fileno()
    ti = threading.Thread(target=pump_fd,
                          args=(stdin_fd, proc.stdin, "c2a", c2a, True),
                          daemon=True)
    to = threading.Thread(target=pump_pipe,
                          args=(proc.stdout, sys.stdout.buffer, "a2c", a2c, False),
                          daemon=True)
    ti.start()
    to.start()
    # Wait for the agent process to exit
    proc.wait()
    # Progress-based drain of stdout pump (P2: keep forwarding while making progress;
    # give up only after a 5 s stall with no bytes forwarded)
    stall_timeout = 5
    last_fwd = state["forwarded_a2c"]
    stall_start = time.monotonic()
    while to.is_alive():
        time.sleep(0.1)
        current_fwd = state["forwarded_a2c"]
        if current_fwd > last_fwd:
            last_fwd = current_fwd
            stall_start = time.monotonic()
        elif time.monotonic() - stall_start >= stall_timeout:
            break
    # The stdin pump is a daemon thread reading a raw fd; it will exit when we do.
    try:
        tl.close()
    except OSError:
        pass
    # Determine drain status: forwarded everything recorded in BOTH directions?
    drained = (state["forwarded_a2c"] == state["recorded_a2c"]
               and state["forwarded_c2a"] == state["recorded_c2a"])
    # Compute exit code (V-c F8: signal-killed agent -> 128+signal)
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
    # Write tee-status.json (best-effort)
    status = {
        "agent_returncode": proc.returncode,
        "drained": drained,
        "stdin_reader_done": state["stdin_reader_done"],
        "recorded_c2a": state["recorded_c2a"],
        "recorded_a2c": state["recorded_a2c"],
        "forwarded_c2a": state["forwarded_c2a"],
        "forwarded_a2c": state["forwarded_a2c"],
        "write_errors": list(state["write_errors"]),
        "exit_code": exit_code,
    }
    try:
        with open(os.path.join(framedir, "tee-status.json"), "w") as f:
            json.dump(status, f, indent=2)
            f.write("\n")
    except OSError:
        pass
    os._exit(exit_code)


if __name__ == "__main__":
    main()
