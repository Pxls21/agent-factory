#!/usr/bin/env python3
"""Run ONE shell command on the PC through the token-gated bridge and behave like a local process.

The bridge answers with a JSON envelope {"rc": int, "stdout": str, "stderr": str}. This helper
unwraps it: the remote stdout goes to our stdout, the remote stderr to our stderr, and the
remote rc becomes our exit code — so a caller can write `pc_bridge_exec.py "cmd" > out` and get
the command's output, not the envelope. (Bit 2026-09-03: the first real lane produced a report
that scripts/pc_lane.sh could not fetch because it base64-decoded the ENVELOPE.)

Rules honoured (PC-BRIDGE.md): the token reaches curl through `--config -` on stdin (never argv,
never a file); `Connection: close`; a non-JSON reply is retried up to three times; the client
timeout stays under the bridge's ~120 s cap. Exit 3 = no JSON after retries, 4 = curl/bridge error.
"""
import json
import os
import subprocess
import sys
import tempfile
import time


def run(cmd: str, url: str, token: str, attempts: int = 3, max_time: int = 110):
    body = json.dumps({"cmd": cmd}).encode()
    with tempfile.NamedTemporaryFile("wb", suffix=".json", delete=False) as fh:
        fh.write(body)  # the command is not secret; the token is
        data_path = fh.name
    try:
        cfg = (
            f'url = "{url.rstrip("/")}/exec"\n'
            'request = "POST"\n'
            'header = "Content-Type: application/json"\n'
            f'header = "X-Agent-Token: {token}"\n'
            'header = "Connection: close"\n'
            f'data-binary = "@{data_path}"\n'
            f'silent\nshow-error\nmax-time = {max_time}\n'
        )
        last = None
        for attempt in range(attempts):
            r = subprocess.run(["curl", "--config", "-"], input=cfg, capture_output=True, text=True)
            last = r
            text = r.stdout.lstrip()
            if text.startswith("{"):
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    pass
            if attempt < attempts - 1:
                time.sleep(1)
        if last is not None and last.returncode != 0:
            sys.stderr.write(f"pc_bridge_exec: curl exited {last.returncode}: {last.stderr.strip()}\n")
            return {"rc": 4, "stdout": "", "stderr": "bridge error"}
        sys.stderr.write("pc_bridge_exec: no JSON envelope after retries\n")
        return {"rc": 3, "stdout": "", "stderr": "non-JSON reply"}
    finally:
        os.unlink(data_path)


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write("usage: pc_bridge_exec.py '<command>'\n")
        return 2
    url, token = os.environ.get("PC_BRIDGE_URL"), os.environ.get("PC_BRIDGE_TOKEN")
    if not url or not token:
        sys.stderr.write("pc_bridge_exec: PC_BRIDGE_URL / PC_BRIDGE_TOKEN not set (export them; .pc-bridge.env)\n")
        return 2
    env = run(sys.argv[1], url, token)
    sys.stdout.write(env.get("stdout") or "")
    err = env.get("stderr") or ""
    if err:
        sys.stderr.write(err if err.endswith("\n") else err + "\n")
    try:
        return int(env.get("rc", 4))
    except (TypeError, ValueError):
        return 4


if __name__ == "__main__":
    sys.exit(main())
