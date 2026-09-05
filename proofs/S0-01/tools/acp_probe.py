#!/usr/bin/env python3
"""S0-01 negative-control probe: launch a pinned ACP agent and send a malformed initialize.

Reads:
  S0_01_AGENT   — absolute path to the agent binary
  S0_01_FRAMEDIR — output directory for timeline.jsonl + runtime-identity.json

Sends the malformed initialize request from fixtures/neg-malformed-initialize.json as JSON-RPC
id 0 method initialize, reads the response (timeout 30 s), then closes stdin.

Writes timeline.jsonl (same shape as frame_tee.py) and runtime-identity.json (same keys).
"""
import datetime
import hashlib
import json
import os
import subprocess
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


def main():
    framedir = os.environ["S0_01_FRAMEDIR"]
    agent = os.environ["S0_01_AGENT"]
    os.makedirs(framedir, exist_ok=True)

    # Load the malformed initialize fixture
    here = os.path.dirname(os.path.abspath(__file__))
    fixture_path = os.path.join(os.path.dirname(here), "fixtures", "neg-malformed-initialize.json")
    params = json.loads(open(fixture_path).read())
    request = {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": params}

    proc = subprocess.Popen(
        [agent], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Write runtime-identity.json
    agent_realpath = os.path.realpath(agent)
    interp_realpath = None
    interp_sha256 = None
    try:
        interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
        interp_sha256 = _sha256_file(interp_realpath)
    except (OSError, IOError):
        pass

    identity = {
        "tee_path": os.path.realpath(__file__),
        "tee_sha256": _sha256_file(os.path.realpath(__file__)),
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

    # Timeline entries
    timeline = []
    seq = 0

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

    # Read the response (timeout 30s)
    import select
    response_frame = None
    try:
        ready, _, _ = select.select([proc.stdout], [], [], 30.0)
        if ready:
            line = proc.stdout.readline()
            if line:
                t_utc = _utc_now()
                t_mono = time.monotonic_ns()
                text = line.decode("utf-8", errors="replace").strip()
                try:
                    response_frame = json.loads(text)
                except (json.JSONDecodeError, ValueError):
                    response_frame = None
                seq += 1
                entry = {
                    "seq": seq, "dir": "a2c", "t_utc": t_utc, "t_mono_ns": t_mono,
                    "frame": response_frame if response_frame is not None else {"raw": text},
                }
                timeline.append(entry)
    except Exception:
        pass

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

    # Write timeline.jsonl
    tl_path = os.path.join(framedir, "timeline.jsonl")
    with open(tl_path, "w") as f:
        for entry in timeline:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")

    # Also write directional files for compatibility
    with open(os.path.join(framedir, "frames-client-to-agent.jsonl"), "w") as f:
        for entry in timeline:
            if entry["dir"] == "c2a":
                f.write(json.dumps(entry["frame"], separators=(",", ":")) + "\n")
    with open(os.path.join(framedir, "frames-agent-to-client.jsonl"), "w") as f:
        for entry in timeline:
            if entry["dir"] == "a2c":
                f.write(json.dumps(entry["frame"], separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
