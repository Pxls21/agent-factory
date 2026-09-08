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
import fcntl
import hashlib
import json
import os
import re
import select as _select
import stat
import subprocess
import sys
import threading
import time


# Redaction regex matching pins.REDACTED_ENV_KEY_RE (hardcoded to avoid import issues on the PC)
_REDACTED_ENV_KEY_RE = re.compile(r"(?i)(KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV)")

# N5f-F4: pinned early-sample loop parameters (consumed by the retry loop)
_EARLY_SAMPLE_DEADLINE_S = 0.2
_EARLY_SAMPLE_STEP_S = 0.002

# N5h-#39: the ONLY accepted ACP_PROBE_TIMEOUT syntax — plain decimal digits with an
# optional fractional part.  float() also accepts "3_0", " 30 ", "nan", "inf", "-5";
# the domain is closed HERE, before the conversion runs.
_TIMEOUT_DOMAIN_RE = re.compile(r"[0-9]+(\.[0-9]+)?")


def _sha256_file(path):
    # N5h-#7 (class): every file the probe reads must be a REGULAR file — open() on a
    # FIFO blocks forever and a character device (/dev/zero) never reaches EOF.  os.stat
    # does not open the file, so it cannot block.  One guard covers all three receivers
    # of this function: the probe's own file, the agent entrypoint, the child interpreter.
    if not stat.S_ISREG(os.stat(path).st_mode):
        raise OSError("not a regular file: %s" % (path,))
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _open_regular(path, mode):
    """Open `path` for WRITING in a way that can never block, and name the refusal.

    N5i-F5 (the WRITE class): the read side was closed in round 11, the write side
    was not — a FIFO planted at runtime-identity.json, env.json or timeline.jsonl
    made open() block forever (measured on the PIN: rc 124 under `timeout 12`, all
    three).  O_NONBLOCK turns a reader-less FIFO into ENXIO instead of a wait,
    O_NOFOLLOW turns a symlink into ELOOP, a directory already fails with EISDIR,
    and S_ISREG on the OPEN descriptor rejects every other type (character devices,
    sockets) with no TOCTOU window.  O_NONBLOCK is cleared before the handle is
    returned so the caller writes to an ordinary file object."""
    fd = os.open(path,
                 os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW | os.O_NONBLOCK,
                 0o644)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError("not a regular file: %s" % (path,))
        fcntl.fcntl(fd, fcntl.F_SETFL,
                    fcntl.fcntl(fd, fcntl.F_GETFL) & ~os.O_NONBLOCK)
    except Exception:
        os.close(fd)
        raise
    return os.fdopen(fd, mode)


# N5i-F4: the probe's own file is hashed ONCE, here, inside a try.  On the PIN
# _write_evidence and the M3 handler each called _sha256_file(realpath(__file__))
# unguarded: an agent that replaced the probe's script with a FIFO made the first
# call raise, the handler re-raise the same read inside its own `except`, and
# CPython's traceback printer block in linecache.getline() on the FIFO —
# rc 124 with ZERO evidence files (measured on the PIN this round).  Reading the
# file once, before the agent exists, also records the digest of the bytes that
# actually ran rather than whatever is at that path when the run ends.
_PROBE_PATH = os.path.realpath(__file__)
try:
    _PROBE_SHA256 = _sha256_file(_PROBE_PATH)
    _PROBE_SHA256_ERROR = None
except Exception as _exc:   # OSError today; an import must never fail here
    _PROBE_SHA256 = None
    _PROBE_SHA256_ERROR = f"{type(_exc).__name__}: {_exc}"


def _utc_now():
    dt = datetime.datetime.now(datetime.timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _drain_stderr(proc, stderr_path, error_slot):
    """Drain the agent's stderr to a file in a background thread.

    N5h-#10: a failure here is RECORDED in error_slot (a one-element list the main
    path folds into probe_error), never swallowed — a directory at stderr_path used
    to kill this thread silently while the probe still exited 0."""
    try:
        with _open_regular(stderr_path, "wb") as f:
            while True:
                chunk = proc.stderr.read(65536)
                if not chunk:
                    break
                f.write(chunk)
    except Exception as exc:
        error_slot[0] = f"{type(exc).__name__}: {exc}"


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
    with _open_regular(os.path.join(framedir, "env.json"), "w") as f:
        json.dump(env_data, indent=1, sort_keys=True, fp=f)
        f.write("\n")


def _write_evidence(framedir, timeline, agent, agent_realpath, child_pid,
                    interp_realpath, interp_sha256, spawned_at_utc,
                    agent_exit_code, probe_error):
    """Write runtime-identity.json, env.json and timeline.jsonl.  N5e-F8: called
    INSIDE the wrapped body so a crash here degrades gracefully — a self-deleting
    agent produces probe_error + all four files with agent_entrypoint_sha256=None,
    and the M3 handler is the last resort."""
    # N5i-F4: an unreadable probe file is NAMED (never a traceback, never a
    # second read).  It is checked first because the import-time hash is the
    # chronologically earliest failure; "first error wins" is unchanged.
    if _PROBE_SHA256 is None and probe_error is None:
        probe_error = f"probe file unreadable: {_PROBE_SHA256_ERROR}"
    # N5f-F6: guard the entrypoint hash — a self-deleting agent raises here
    try:
        agent_entrypoint_sha256 = _sha256_file(agent_realpath)
    except OSError as exc:
        agent_entrypoint_sha256 = None
        if probe_error is None:
            probe_error = f"{type(exc).__name__}: {exc}"
    identity = {
        "probe_path": _PROBE_PATH,
        "probe_sha256": _PROBE_SHA256,
        "agent_argv": [agent],
        "agent_realpath": agent_realpath,
        "agent_entrypoint_sha256": agent_entrypoint_sha256,
        "agent_child_pid": child_pid,
        "agent_interpreter_realpath": interp_realpath,
        "agent_interpreter_sha256": interp_sha256,
        # N5h-#40: the RUNTIME state, not a string mirror.  CPython enables the flag
        # for "2"/"true" too, so `== "1"` recorded False while writing was disabled.
        "python_dont_write_bytecode": sys.dont_write_bytecode,
        "spawned_at_utc": spawned_at_utc,
        "agent_exit_code": agent_exit_code,
    }
    if probe_error is not None:
        identity["probe_error"] = probe_error
    with _open_regular(os.path.join(framedir, "runtime-identity.json"), "w") as f:
        json.dump(identity, f, indent=2)
        f.write("\n")

    _write_env(framedir)

    # timeline.jsonl
    tl_path = os.path.join(framedir, "timeline.jsonl")
    with _open_regular(tl_path, "w") as f:
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
    # N5h-#7: os.stat, not os.path.exists — a FIFO at the fixture path passes exists()
    # and then blocks open() forever (measured on the PIN: rc 124 under `timeout 20`).
    try:
        fixture_st = os.stat(fixture_path)
    except OSError:
        print(f"acp_probe: fixture not found: {fixture_path}", file=sys.stderr)
        raise SystemExit(64)
    if not stat.S_ISREG(fixture_st.st_mode):
        print(f"acp_probe: fixture is not a regular file: {fixture_path}", file=sys.stderr)
        raise SystemExit(64)
    with open(fixture_path) as f:
        params = json.load(f)
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
        # N5h-#39: the DOMAIN gate runs BEFORE the conversion, so float()'s own
        # leniency ("3_0", " 30 ", "nan", "inf", "-5", "0x10") is structurally
        # unreachable; isfinite still guards the FINAL value because "9"*400 passes
        # the regex and float()s to inf.  Both message classes are preserved: a
        # rejected value that float() parses to a non-finite/non-positive number
        # keeps the "finite float > 0" wording, everything else is "not a number".
        import math
        timeout_raw = os.environ.get("ACP_PROBE_TIMEOUT", "30")
        timeout = None
        msg = None
        if _TIMEOUT_DOMAIN_RE.fullmatch(timeout_raw) is None:
            try:
                rejected = float(timeout_raw)
            except (ValueError, OverflowError):
                rejected = None
            if rejected is None:
                msg = f"ACP_PROBE_TIMEOUT is not a valid number: {timeout_raw!r}"
            elif not math.isfinite(rejected) or rejected <= 0:
                msg = f"ACP_PROBE_TIMEOUT must be a finite float > 0, got {timeout_raw!r}"
            else:
                # N5i-F6: "1e3" IS a valid number (1000.0) — telling an operator it
                # is not was false for 9 measured forms (1e3 +30 .5 5. 1_000 3_0
                # ' 30 ' '30\n' ٣٠).  The real reason is the pinned syntax, and the
                # feature contradicted itself: 1e400, also scientific notation, got
                # the other wording only because float() overflows.
                msg = (f"ACP_PROBE_TIMEOUT must be plain decimal digits "
                       f"(e.g. '30' or '0.5'), got {timeout_raw!r}")
        else:
            timeout = float(timeout_raw)
            if not math.isfinite(timeout) or timeout <= 0:
                msg = f"ACP_PROBE_TIMEOUT must be a finite float > 0, got {timeout_raw!r}"
        if msg is not None:
            with _open_regular(os.path.join(framedir, "runtime-identity.json"), "w") as f:
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
        drain_error = [None]
        stderr_thread = threading.Thread(
            target=_drain_stderr, args=(proc, stderr_path, drain_error), daemon=True
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
                        # N5h-#23: strict first.  errors="replace" silently rewrites
                        # the agent's bytes, so a line that did not decode losslessly
                        # keeps its exact bytes in raw_b64 below.
                        try:
                            text = line_bytes.decode("utf-8")
                            lossy = False
                        except UnicodeDecodeError:
                            text = line_bytes.decode("utf-8", errors="replace")
                            lossy = True
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
                            if lossy:
                                # N5h-#23: the parsed frame carries the REPLACED text,
                                # not what the agent sent — keep the lossless copy.
                                entry["raw_b64"] = base64.b64encode(
                                    line_bytes_with_nl).decode("ascii")
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
        # N5i-F1: a drain that BLOCKS is a drain failure too.  `except Exception`
        # only sees failures that RAISE; on the PIN a drain still reading when the
        # join expired left agent-stderr.txt truncated and the probe exited 0 with
        # no probe_error (measured: a grandchild holding the agent's stderr open —
        # 0 bytes captured, rc 0).  The thread is a daemon, so the probe still exits.
        if stderr_thread.is_alive() and drain_error[0] is None:
            drain_error[0] = ("did not finish in 3s (the agent's stderr may still "
                              "be held open by a surviving child)")

        # N5h-#10: a drain failure IS a probe failure — fold it into probe_error.
        # N5i-F2/F8: when an earlier error is already live the drain error is
        # APPENDED, never dropped: on the PIN a BrokenPipe plus a directory at
        # agent-stderr.txt lost the IsADirectoryError with no residual at all.
        if drain_error[0] is not None:
            if probe_error is None:
                probe_error = f"stderr drain failed: {drain_error[0]}"
            else:
                probe_error = f"{probe_error}; stderr drain failed: {drain_error[0]}"

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
            # N5i-F4: the cached import-time hash — re-reading the probe's own
            # file HERE is what turned a named failure into a hang.
            "probe_path": _PROBE_PATH,
            "probe_sha256": _PROBE_SHA256,
            "agent_argv": [agent],
            "agent_realpath": agent_realpath,
            "agent_entrypoint_sha256": None,
            "agent_child_pid": child_pid,
            "agent_interpreter_realpath": interp_realpath,
            "agent_interpreter_sha256": interp_sha256,
            # N5h-#40: the runtime state (see _write_evidence)
            "python_dont_write_bytecode": sys.dont_write_bytecode,
            "spawned_at_utc": spawned_at_utc,
            "agent_exit_code": agent_exit_code,
            "probe_error": probe_error,
        }
        # N5i-F5: the last resort writes through _open_regular too, and a REFUSED
        # write is recorded per file instead of raising: an exception raised inside
        # this handler prints a traceback, and the traceback printer reads the
        # probe's own source — the read that hung the PIN.  Each file is attempted
        # independently so one planted path cannot cost the other three.
        m3_errors = []

        def _m3_write(path, text):
            try:
                with _open_regular(path, "w") as f:
                    f.write(text)
            except Exception as exc2:
                m3_errors.append(f"{os.path.basename(path)}: {type(exc2).__name__}: {exc2}")

        rid_path = os.path.join(framedir, "runtime-identity.json")
        _m3_write(rid_path, json.dumps(identity, indent=2) + "\n")
        try:
            _write_env(framedir)
        except Exception as exc2:
            m3_errors.append(f"env.json: {type(exc2).__name__}: {exc2}")
        # Write whatever timeline we have
        tl_path = os.path.join(framedir, "timeline.jsonl")
        _m3_write(tl_path, "".join(
            json.dumps(entry, separators=(",", ":")) + "\n" for entry in timeline))
        # agent-stderr.txt — create if missing (stderr drain may not have started)
        stderr_path = os.path.join(framedir, "agent-stderr.txt")
        if not os.path.exists(stderr_path):
            _m3_write(stderr_path, "")
        if m3_errors:
            print("acp_probe: last-resort evidence write failed: " + "; ".join(m3_errors),
                  file=sys.stderr)
        print(f"acp_probe: {probe_error}", file=sys.stderr)
        raise SystemExit(1)

    # Exit non-zero if there was a probe error
    if probe_error is not None:
        print(f"acp_probe: {probe_error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
