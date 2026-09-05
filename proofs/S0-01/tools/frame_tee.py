#!/usr/bin/python3
"""stdio proxy: preserve raw ACP JSON-RPC frames between buzz-acp (client) and hermes-acp (agent).

Writes into S0_01_FRAMEDIR:
  timeline.jsonl               - interleaved, seq-numbered, under ONE lock
  frames-client-to-agent.jsonl - byte-identical relay c2a
  frames-agent-to-client.jsonl - byte-identical relay a2c
  runtime-identity.json        - written once at spawn
"""
import datetime
import hashlib
import json
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


def main():
    framedir = os.environ["S0_01_FRAMEDIR"]
    agent = os.environ["S0_01_AGENT"]
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

    def pump(src, dst, direction, dir_path, close_dst):
        df = open(dir_path, "ab")
        try:
            while True:
                line = src.readline()
                if not line:
                    break
                df.write(line)
                df.flush()
                t_utc = _utc_now()
                t_mono = time.monotonic_ns()
                text = line.decode("utf-8", errors="replace")
                if text.endswith("\r\n"):
                    stripped = text[:-2]
                elif text.endswith("\n"):
                    stripped = text[:-1]
                else:
                    stripped = text
                try:
                    frame = json.loads(stripped)
                    entry = {"seq": 0, "dir": direction, "t_utc": t_utc,
                             "t_mono_ns": t_mono, "frame": frame}
                except (json.JSONDecodeError, ValueError):
                    entry = {"seq": 0, "dir": direction, "t_utc": t_utc,
                             "t_mono_ns": t_mono, "frame": None, "raw": stripped}
                with lock:
                    seq[0] += 1
                    entry["seq"] = seq[0]
                    tl.write(json.dumps(entry, separators=(",", ":")).encode("utf-8") + b"\n")
                    tl.flush()
                try:
                    dst.write(line)
                    dst.flush()
                except BrokenPipeError:
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
    ti = threading.Thread(target=pump,
                          args=(sys.stdin.buffer, proc.stdin, "c2a", c2a, True),
                          daemon=True)
    to = threading.Thread(target=pump,
                          args=(proc.stdout, sys.stdout.buffer, "a2c", a2c, False),
                          daemon=True)
    ti.start()
    to.start()
    to.join()
    proc.wait()
    ti.join(timeout=2)
    tl.close()
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
