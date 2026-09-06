"""S0-01 negative-control probe: launch a pinned ACP agent and send a malformed initialize.

Reads:
  S0_01_AGENT   -- absolute path to the agent binary
  S0_01_FRAMEDIR -- output directory for timeline.jsonl + runtime-identity.json + env.json

Sends the malformed initialize request from fixtures/neg-malformed-initialize.json as JSON-RPC
id 0 method initialize, reads every a2c line until a frame with id == 0 arrives or the deadline
passes (timeout configurable via ACP_PROBE_TIMEOUT, default 30 s), then closes stdin.

Writes timeline.jsonl (same shape as frame_tee.py), runtime-identity.json (probe identity keys),
env.json (caller's environment with sensitive keys redacted), and agent-stderr.txt (drained).

The agent is run with the caller's environment (the PC launcher sets HERMES_HOME etc.).

Documented exceptions to probe_error: when S0_01_FRAMEDIR or S0_01_AGENT is unset or empty,
the probe exits 64 with a named stderr message but does NOT write runtime-identity.json
(and therefore no probe_error field) because the failure occurs before the wrapped body opens.
"""
import base64
import datetime
import hashlib
import json
import os
import re
import select as _select
import subprocess
import sys
import threading
import time


# Redaction regex matching pins.REDACTED_ENV_KEY_RE (hardcoded to avoid import issues on the PC)
_REDACTED_ENV_KEY_RE = re.compile(r"(?i)(KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV)")

# N5f-F4: pinned early-sample loop parameters (consumed by the retry loop)
_EARLY_SAMPLE_DEADLINE_S = 0.2
_EARLY_SAMPLE_STEP_S = 0.002


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _utc_now():
    dt = datetime.datetime.now(datetime.timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _drain_stderr(proc, stderr_path):
    """Drain the agent's stderr to a file in a background thread."""
    try:
        with open(stderr_path, "wb") as f:
            while True:
                chunk = proc.stderr.read(65536)
                if not chunk:
                    break
                f.write(chunk)
    except Exception:
        pass


def _redact_env(env):
    """Redact sensitive environment values per the pins.REDACTED_ENV_KEY_RE pattern."""
    result = {}
    for k, v in env.items():
        if _REDACTED_ENV_KEY_RE.search(k):
            result[k] = {
                "redacted": True,
                "len": len(v),
                "sha256_12": hashlib.sha256(v.encode("utf-8")).hexdigest()[:12],
            }
        else:
            result[k] = v
    return result


def _write_env(framedir):
    """Write env.json (caller's environment with redaction)."""
    env_data = _redact_env(dict(os.environ))
    with open(os.path.join(framedir, "env.json"), "w") as f:
        json.dump(env_data, indent=1, sort_keys=True, fp=f)
        f.write("\n")


def _write_evidence(framedir, timeline, agent, agent_realpath, child_pid,
                    interp_realpath, interp_sha256, spawned_at_utc,
                    agent_exit_code, probe_error):
    """Write runtime-identity.json, env.json and timeline.jsonl.  N5e-F8: called
    INSIDE the wrapped body so a crash here degrades gracefully — a self-deleting
    agent produces probe_error + all four files with agent_entrypoint_sha256=None,
    and the M3 handler is the last resort."""
    # N5f-F6: guard the entrypoint hash — a self-deleting agent raises here
    try:
        agent_entrypoint_sha256 = _sha256_file(agent_realpath)
    except OSError as exc:
        agent_entrypoint_sha256 = None
        if probe_error is None:
            probe_error = f"{type(exc).__name__}: {exc}"
    identity = {
        "probe_path": os.path.realpath(__file__),
        "probe_sha256": _sha256_file(os.path.realpath(__file__)),
        "agent_argv": [agent],
        "agent_realpath": agent_realpath,
        "agent_entrypoint_sha256": agent_entrypoint_sha256,
        "agent_child_pid": child_pid,
        "agent_interpreter_realpath": interp_realpath,
        "agent_interpreter_sha256": interp_sha256,
        "python_dont_write_bytecode": os.environ.get("PYTHONDONTWRITEBYTECODE") == "1",
        "spawned_at_utc": spawned_at_utc,
        "agent_exit_code": agent_exit_code,
    }
    if probe_error is not None:
        identity["probe_error"] = probe_error
    with open(os.path.join(framedir, "runtime-identity.json"), "w") as f:
        json.dump(identity, f, indent=2)
        f.write("\n")

    _write_env(framedir)

    # timeline.jsonl
    tl_path = os.path.join(framedir, "timeline.jsonl")
    with open(tl_path, "w") as f:
        for entry in timeline:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")

    return probe_error


def main():
    # Validate required env vars early with a named message (L15/A10: exit 64).
    # Empty/unset cases exit 64 WITHOUT probe_error because the try block (which
    # writes runtime-identity.json) has not started yet — this is a documented
    # exception: probe_error requires the wrapped body to have opened.
    for k in ("S0_01_FRAMEDIR", "S0_01_AGENT"):
        v = os.environ.get(k)
        if v is None:
            print(f"acp_probe: required environment variable {k} is not set",
                  file=sys.stderr)
            raise SystemExit(64)
        if v == "":
            print(f"acp_probe: required environment variable {k} is empty",
                  file=sys.stderr)
            raise SystemExit(64)

    framedir = os.environ["S0_01_FRAMEDIR"]
    agent = os.environ["S0_01_AGENT"]

    # Load the malformed initialize fixture
    here = os.path.dirname(os.path.abspath(__file__))
    fixture_path = os.path.join(os.path.dirname(here), "fixtures", "neg-malformed-initialize.json")
    if not os.path.exists(fixture_path):
        print(f"acp_probe: fixture not found: {fixture_path}", file=sys.stderr)
        raise SystemExit(64)
    params = json.loads(open(fixture_path).read())
    request = {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": params}

    # Timeline entries
    timeline = []
    seq = 0
    probe_error = None

    # N5f-F6: pre-initialise identity fields before the try so they are
    # always in scope for the M3 handler's full identity write.
    agent_realpath = None
    interp_realpath = None
    interp_sha256 = None
    spawned_at_utc = None
    agent_exit_code = None
    child_pid = None

    # Wrap the main body so any exception lands in runtime-identity.json
    # under probe_error + exit 1 with a one-line stderr message (M3)
    try:
        # 4-F11: validate/create framedir inside the wrapped body
        if not os.path.isdir(framedir):
            try:
                os.makedirs(framedir, exist_ok=True)
            except OSError as exc:
                print(f"acp_probe: S0_01_FRAMEDIR error: {exc}", file=sys.stderr)
                raise SystemExit(64)

        # A16: validate ACP_PROBE_TIMEOUT inside the wrapped body — must be
        # a finite float > 0, else probe_error + exit 64
        timeout_raw = os.environ.get("ACP_PROBE_TIMEOUT", "30")
        try:
            timeout = float(timeout_raw)
        except (ValueError, OverflowError):
            msg = f"ACP_PROBE_TIMEOUT is not a valid number: {timeout_raw!r}"
            with open(os.path.join(framedir, "runtime-identity.json"), "w") as f:
                json.dump({"probe_error": msg}, f, indent=2)
                f.write("\n")
            print(f"acp_probe: {msg}", file=sys.stderr)
            raise SystemExit(64)
        import math
        if not math.isfinite(timeout) or timeout <= 0:
            msg = f"ACP_PROBE_TIMEOUT must be a finite float > 0, got {timeout_raw!r}"
            with open(os.path.join(framedir, "runtime-identity.json"), "w") as f:
                json.dump({"probe_error": msg}, f, indent=2)
                f.write("\n")
            print(f"acp_probe: {msg}", file=sys.stderr)
            raise SystemExit(64)

        agent_realpath = os.path.realpath(agent)

        proc = subprocess.Popen(
            [agent], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        child_pid = proc.pid

        # Sample spawned_at_utc right after Popen (M2: not after proc.wait)
        spawned_at_utc = _utc_now()

        # 6-F7: interpreter identity sampled from the CHILD's /proc/<pid>/exe,
        # never from /proc/self/exe (the probe's own interpreter).
        interp_realpath = None
        interp_sha256 = None
        _late_sampled = False

        # N5f-F1: early sample in a bounded retry loop.  This is the FALLBACK
        # for agents that exit before their first a2c byte; the reading at the
        # first a2c byte is authoritative (the later reading wins).  The early
        # loop covers agents that never write.
        _sample_deadline = time.monotonic() + _EARLY_SAMPLE_DEADLINE_S
        while True:
            try:
                candidate = os.readlink("/proc/%d/exe" % proc.pid)
            except (OSError, IOError):
                candidate = None
            if candidate is not None:
                interp_realpath = candidate
                try:
                    interp_sha256 = _sha256_file(candidate)
                except (OSError, IOError) as exc:
                    probe_error = f"interpreter sample failed: {exc}"
                break
            if time.monotonic() >= _sample_deadline:
                break
            time.sleep(_EARLY_SAMPLE_STEP_S)

        # Start draining stderr in a background thread
        stderr_path = os.path.join(framedir, "agent-stderr.txt")
        stderr_thread = threading.Thread(
            target=_drain_stderr, args=(proc, stderr_path), daemon=True
        )
        stderr_thread.start()

        # Send the malformed initialize request
        req_bytes = json.dumps(request, separators=(",", ":")).encode("utf-8") + b"\n"
        t_utc = _utc_now()
        t_mono = time.monotonic_ns()
        c2a_delivered = True
        try:
            proc.stdin.write(req_bytes)
            proc.stdin.flush()
        except BrokenPipeError:
            # L14: mark as not delivered, set probe_error, exit 1
            c2a_delivered = False
            probe_error = "BrokenPipeError: agent process exited before c2a write landed"
        seq += 1
        c2a_entry = {
            "seq": seq, "dir": "c2a", "t_utc": t_utc, "t_mono_ns": t_mono,
            "frame": request,
        }
        if not c2a_delivered:
            c2a_entry["delivered"] = False
        timeline.append(c2a_entry)

        # Read a2c lines: deadline loop over os.read until a frame with id==0
        # arrives or the deadline passes (H2/M1/8-verify F12)
        if c2a_delivered:
            deadline = time.monotonic() + timeout
            stdout_fd = proc.stdout.fileno()
            buf = b""
            found_response = False
            while time.monotonic() < deadline and not found_response:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                ready, _, _ = _select.select([stdout_fd], [], [], min(remaining, 0.5))
                if ready:
                    try:
                        chunk = os.read(stdout_fd, 65536)
                    except OSError:
                        break
                    if not chunk:
                        break  # EOF
                    # N5f-F1: at the first a2c chunk, ALWAYS re-read the
                    # interpreter — the later reading wins over the early loop.
                    # sampled ONCE, at the moment the probe consumes the first a2c
                    # chunk (pinned by test_probe_interpreter_is_sampled_once_at_the_first_a2c_byte).
                    # An agent that execs AFTER its first byte may be recorded as
                    # either stage — the read races its execve (VERIFY-N5g measured
                    # 41/48 first stage, 7/48 second): a multi-stage agent must not
                    # exec after speaking.
                    if not _late_sampled:
                        _late_sampled = True
                        try:
                            interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
                            try:
                                interp_sha256 = _sha256_file(interp_realpath)
                            except (OSError, IOError) as exc:
                                interp_sha256 = None
                                probe_error = f"interpreter sample failed: {exc}"
                            else:
                                # Clear an early "interpreter sample failed:" error.
                                # Defensive: no other probe_error class can be live
                                # here — :263 sets BrokenPipe but also c2a_delivered=False,
                                # which skips this whole block; no test, no kill count.
                                if (probe_error is not None and
                                        probe_error.startswith("interpreter sample failed: ")):
                                    probe_error = None
                        except (OSError, IOError) as exc:
                            # Child exited between its first byte and the readlink;
                            # keeps the early reading — a wrong early reading fails
                            # the pinned interpreter checks downstream; pinned by
                            # test_probe_late_readlink_failure_keeps_the_early_reading
                            if interp_realpath is None:
                                probe_error = f"interpreter sample failed: {exc}"
                    buf += chunk
                    # Process complete lines
                    while b"\n" in buf:
                        line_bytes, buf = buf.split(b"\n", 1)
                        line_bytes_with_nl = line_bytes + b"\n"
                        t_utc = _utc_now()
                        t_mono = time.monotonic_ns()
                        text = line_bytes.decode("utf-8", errors="replace")
                        stripped = text.rstrip("\r")
                        try:
                            response_frame = json.loads(stripped)
                        except (json.JSONDecodeError, ValueError):
                            response_frame = None
                        seq += 1
                        if response_frame is not None:
                            entry = {
                                "seq": seq, "dir": "a2c", "t_utc": t_utc,
                                "t_mono_ns": t_mono, "frame": response_frame,
                            }
                        else:
                            entry = {
                                "seq": seq, "dir": "a2c", "t_utc": t_utc,
                                "t_mono_ns": t_mono, "frame": None,
                                "raw": stripped,
                                "raw_b64": base64.b64encode(line_bytes_with_nl).decode("ascii"),
                            }
                        timeline.append(entry)
                        # Check if this frame has id == 0 (the response we want)
                        if response_frame is not None and response_frame.get("id") == 0:
                            found_response = True
                            break

            # Record any trailing partial line as frame: null with raw/raw_b64 (H2)
            if buf and not found_response:
                t_utc = _utc_now()
                t_mono = time.monotonic_ns()
                text = buf.decode("utf-8", errors="replace")
                seq += 1
                entry = {
                    "seq": seq, "dir": "a2c", "t_utc": t_utc,
                    "t_mono_ns": t_mono, "frame": None,
                    "raw": text,
                    "raw_b64": base64.b64encode(buf).decode("ascii"),
                }
                timeline.append(entry)

            # N5d-F1: sample interpreter at EOF/exit if not yet sampled.
            # This block is reached only under fault injection (readlink
            # patched to fail for longer than the early loop's deadline);
            # for real agents the early loop or the a2c-triggered sample
            # always fires first.
            if not _late_sampled:
                # N5e-F3: split readlink and sha256 — report the REAL exception
                # when readlink succeeded but sha256 failed; the fixed wording
                # is reserved for "nothing was ever sampled" (interp_realpath is None).
                if interp_realpath is None:
                    try:
                        interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
                    except (OSError, IOError):
                        probe_error = ("interpreter sample failed: agent exited "
                                       "before its first a2c byte")
                if interp_realpath is not None and interp_sha256 is None:
                    try:
                        interp_sha256 = _sha256_file(interp_realpath)
                    except (OSError, IOError) as exc:
                        probe_error = f"interpreter sample failed: {exc}"
                _late_sampled = True

        # Close stdin to signal EOF
        try:
            proc.stdin.close()
        except Exception:
            pass

        # Wait for process to exit (brief timeout)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

        # Wait for stderr drain to finish
        stderr_thread.join(timeout=3)

        agent_exit_code = proc.returncode

        # N5e-F8: evidence writes INSIDE the wrapped body.  A self-deleting
        # agent degrades gracefully (agent_entrypoint_sha256=None, probe_error
        # set, all four files written); the M3 handler is the last resort.
        probe_error = _write_evidence(
            framedir, timeline, agent, agent_realpath, child_pid,
            interp_realpath, interp_sha256, spawned_at_utc,
            agent_exit_code, probe_error,
        )

    except SystemExit:
        raise
    except Exception as exc:
        # M3: last resort — write all four files with all 11 identity keys
        # (pre-initialised to None, filled with whatever was reached).
        probe_error = f"{type(exc).__name__}: {exc}"
        identity = {
            "probe_path": os.path.realpath(__file__),
            "probe_sha256": _sha256_file(os.path.realpath(__file__)),
            "agent_argv": [agent],
            "agent_realpath": agent_realpath,
            "agent_entrypoint_sha256": None,
            "agent_child_pid": child_pid,
            "agent_interpreter_realpath": interp_realpath,
            "agent_interpreter_sha256": interp_sha256,
            "python_dont_write_bytecode": os.environ.get("PYTHONDONTWRITEBYTECODE") == "1",
            "spawned_at_utc": spawned_at_utc,
            "agent_exit_code": agent_exit_code,
            "probe_error": probe_error,
        }
        rid_path = os.path.join(framedir, "runtime-identity.json")
        with open(rid_path, "w") as f:
            json.dump(identity, f, indent=2)
            f.write("\n")
        _write_env(framedir)
        # Write whatever timeline we have
        tl_path = os.path.join(framedir, "timeline.jsonl")
        with open(tl_path, "w") as f:
            for entry in timeline:
                f.write(json.dumps(entry, separators=(",", ":")) + "\n")
        # agent-stderr.txt — create if missing (stderr drain may not have started)
        stderr_path = os.path.join(framedir, "agent-stderr.txt")
        if not os.path.exists(stderr_path):
            open(stderr_path, "wb").close()
        print(f"acp_probe: {probe_error}", file=sys.stderr)
        raise SystemExit(1)

    # Exit non-zero if there was a probe error
    if probe_error is not None:
        print(f"acp_probe: {probe_error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
