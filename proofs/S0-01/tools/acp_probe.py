"""S0-01 negative-control probe: launch a pinned ACP agent and send a malformed initialize.

Reads:
  S0_01_AGENT   -- absolute path to the agent binary
  S0_01_FRAMEDIR -- output directory for timeline.jsonl + runtime-identity.json + env.json

Sends the malformed initialize request from fixtures/neg-malformed-initialize.json as JSON-RPC
id 0 method initialize, reads the response (timeout 30 s), then closes stdin.

Writes timeline.jsonl (same shape as frame_tee.py), runtime-identity.json (probe identity keys),
env.json (caller's environment with sensitive keys redacted), and agent-stderr.txt (drained).

The agent is run with the caller's environment (the PC launcher sets HERMES_HOME etc.).
"""
import base64
import datetime
import hashlib
import json
import os
import re
import select
import subprocess
import threading
import time


# Redaction regex matching pins.REDACTED_ENV_KEY_RE (hardcoded to avoid import issues on the PC)
_REDACTED_ENV_KEY_RE = re.compile(r"(?i)(KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV)")


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


def main():
    framedir = os.environ["S0_01_FRAMEDIR"]
    agent = os.environ["S0_01_AGENT"]
    timeout = float(os.environ.get("ACP_PROBE_TIMEOUT", "30"))
    os.makedirs(framedir, exist_ok=True)

    # Load the malformed initialize fixture
    here = os.path.dirname(os.path.abspath(__file__))
    fixture_path = os.path.join(os.path.dirname(here), "fixtures", "neg-malformed-initialize.json")
    params = json.loads(open(fixture_path).read())
    request = {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": params}

    proc = subprocess.Popen(
        [agent], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Start draining stderr in a background thread
    stderr_path = os.path.join(framedir, "agent-stderr.txt")
    stderr_thread = threading.Thread(
        target=_drain_stderr, args=(proc, stderr_path), daemon=True
    )
    stderr_thread.start()

    # Timeline entries
    timeline = []
    seq = 0
    probe_error = None

    # Send the malformed initialize request
    req_bytes = json.dumps(request, separators=(",", ":")).encode("utf-8") + b"\n"
    t_utc = _utc_now()
    t_mono = time.monotonic_ns()
    try:
        proc.stdin.write(req_bytes)
        proc.stdin.flush()
    except BrokenPipeError:
        pass
    seq += 1
    timeline.append({
        "seq": seq, "dir": "c2a", "t_utc": t_utc, "t_mono_ns": t_mono,
        "frame": request,
    })

    # Read the response (timeout configurable via ACP_PROBE_TIMEOUT, default 30s)
    try:
        ready, _, _ = select.select([proc.stdout], [], [], timeout)
        if ready:
            line = proc.stdout.readline()
            if line:
                t_utc = _utc_now()
                t_mono = time.monotonic_ns()
                text = line.decode("utf-8", errors="replace")
                stripped = text.rstrip("\r\n")
                try:
                    response_frame = json.loads(stripped)
                except (json.JSONDecodeError, ValueError):
                    response_frame = None
                seq += 1
                if response_frame is not None:
                    entry = {
                        "seq": seq, "dir": "a2c", "t_utc": t_utc, "t_mono_ns": t_mono,
                        "frame": response_frame,
                    }
                else:
                    entry = {
                        "seq": seq, "dir": "a2c", "t_utc": t_utc, "t_mono_ns": t_mono,
                        "frame": None,
                        "raw": stripped,
                        "raw_b64": base64.b64encode(line).decode("ascii"),
                    }
                timeline.append(entry)
    except Exception as exc:
        probe_error = f"{type(exc).__name__}: {exc}"

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

    # Resolve agent identity
    agent_realpath = os.path.realpath(agent)
    interp_realpath = None
    interp_sha256 = None
    try:
        interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
        interp_sha256 = _sha256_file(interp_realpath)
    except (OSError, IOError):
        pass

    # Write runtime-identity.json (probe-specific keys, not tee keys)
    identity = {
        "probe_path": os.path.realpath(__file__),
        "probe_sha256": _sha256_file(os.path.realpath(__file__)),
        "agent_argv": [agent],
        "agent_realpath": agent_realpath,
        "agent_entrypoint_sha256": _sha256_file(agent_realpath),
        "agent_child_pid": proc.pid,
        "agent_interpreter_realpath": interp_realpath,
        "agent_interpreter_sha256": interp_sha256,
        "python_dont_write_bytecode": os.environ.get("PYTHONDONTWRITEBYTECODE") == "1",
        "spawned_at_utc": _utc_now(),
        "agent_exit_code": agent_exit_code,
    }
    if probe_error is not None:
        identity["probe_error"] = probe_error
    with open(os.path.join(framedir, "runtime-identity.json"), "w") as f:
        json.dump(identity, f, indent=2)
        f.write("\n")

    # Write env.json (caller's environment with redaction)
    env_data = _redact_env(dict(os.environ))
    with open(os.path.join(framedir, "env.json"), "w") as f:
        json.dump(env_data, indent=1, sort_keys=True, fp=f)
        f.write("\n")

    # Write timeline.jsonl
    tl_path = os.path.join(framedir, "timeline.jsonl")
    with open(tl_path, "w") as f:
        for entry in timeline:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")

    # Exit non-zero if there was a probe error
    if probe_error is not None:
        print(f"probe error: {probe_error}", file=__import__("sys").stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
