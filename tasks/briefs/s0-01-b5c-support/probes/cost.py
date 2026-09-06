#!/usr/bin/env python3
"""Cost of the A21d per-frame atomic status rewrite.

Compares the SHIPPED tee against a variant with the two per-frame _write_status()
calls removed (pump_fd + pump_pipe; everything else identical), on:
  (a) the 11-frame real-leg shape (realleg/golden/run-1: 3 c2a + 8 a2c)
  (b) the suite's 10000+10000-frame contention shape
Also counts the status rewrites and the bytes they push.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import textwrap
import time

# PROBE_WORK: the work dir holding base/ (a copy or symlink of the tree under test) — sandbox default below.
_VB6 = os.environ.get("PROBE_WORK", "/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vb6")

BASE = pathlib.Path(_VB6 + "")
SHIPPED = BASE / "pristine" / "frame_tee.py"
VARIANT = BASE / "nostatus" / "frame_tee.py"
WORK = BASE / "costwork"

EDITS = [
    ("                _write_status()\n        finally:\n            df.close()\n            if direction == \"c2a\":",
     "                pass\n        finally:\n            df.close()\n            if direction == \"c2a\":"),
    ("                _write_status()\n        finally:\n            df.close()\n            if close_dst and not forward_broken:",
     "                pass\n        finally:\n            df.close()\n            if close_dst and not forward_broken:"),
]


def build_variant():
    VARIANT.parent.mkdir(parents=True, exist_ok=True)
    s = SHIPPED.read_text()
    for o, n in EDITS:
        assert o in s, "edit did not apply"
        s = s.replace(o, n)
    VARIANT.write_text(s)


def run(tee, name, agent_code, input_bytes, timeout=900):
    d = WORK / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    fd = d / "frames"
    fd.mkdir()
    a = d / "agent.py"
    a.write_text("#!%s\n" % sys.executable + textwrap.dedent(agent_code))
    a.chmod(0o755)
    e = os.environ.copy()
    e["S0_01_FRAMEDIR"] = str(fd)
    e["S0_01_AGENT"] = str(a)
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, str(tee)], input=input_bytes, capture_output=True,
                       env=e, timeout=timeout)
    el = time.monotonic() - t0
    stp = fd / "tee-status.json"
    st = json.loads(stp.read_text()) if stp.exists() else None
    frames = (st["recorded_c2a"] + st["recorded_a2c"]) if st else 0
    return el, p.returncode, frames, (stp.stat().st_size if stp.exists() else 0)


LEG_AGENT = """
    import sys, json
    n = 0
    for line in sys.stdin:
        n += 1
        for k in range(2 if n < 3 else 3):
            sys.stdout.write(json.dumps({"jsonrpc":"2.0","method":"session/update",
                                         "params":{"n":n,"k":k}}) + chr(10))
            sys.stdout.flush()
    sys.exit(0)
"""

CONT_AGENT = """
    import sys, json, threading
    def burst_writer(n):
        for i in range(n):
            r = {"jsonrpc": "2.0", "method": "b", "params": {"n": i}}
            sys.stdout.buffer.write(json.dumps(r, separators=(",", ":")).encode() + b"\\n")
            sys.stdout.buffer.flush()
    sys.stdin.readline()
    t = threading.Thread(target=burst_writer, args=(10000,))
    t.start()
    sys.stdin.read()
    t.join()
    sys.exit(0)
"""

if __name__ == "__main__":
    build_variant()
    which = sys.argv[1] if len(sys.argv) > 1 else "both"

    if which in ("leg", "both"):
        leg_in = b"".join(
            (json.dumps({"jsonrpc": "2.0", "id": i, "method": "session/prompt",
                         "params": {"p": "x" * 80}}, separators=(",", ":")) + "\n").encode()
            for i in range(3))
        for tag, tee in (("shipped", SHIPPED), ("no-status", VARIANT)):
            ts = []
            for i in range(7):
                el, rc, fr, sz = run(tee, "leg_%s_%d" % (tag, i), LEG_AGENT, leg_in)
                ts.append(el)
            ts.sort()
            print("LEG(11-frame shape) %-10s rc=%d frames=%d median=%.3fs min=%.3fs max=%.3fs status_bytes=%d"
                  % (tag, rc, fr, ts[len(ts) // 2], ts[0], ts[-1], sz))

    if which in ("cont", "both"):
        cont_in = b"".join(
            (json.dumps({"jsonrpc": "2.0", "id": i, "method": "m", "params": {}},
                        separators=(",", ":")) + "\n").encode() for i in range(10000))
        for tag, tee in (("shipped", SHIPPED), ("no-status", VARIANT)):
            el, rc, fr, sz = run(tee, "cont_%s" % tag, CONT_AGENT, cont_in)
            print("CONTENTION(10000+10000) %-10s rc=%d frames=%d wall=%.2fs status_bytes=%d"
                  % (tag, rc, fr, el, sz))
