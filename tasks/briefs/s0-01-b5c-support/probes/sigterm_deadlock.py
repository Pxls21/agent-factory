#!/usr/bin/env python3
"""Probe: the SIGTERM handler calls _write_status(), which acquires the NON-reentrant
status_lock.  The main thread also calls _write_status() from the drain loops
(frame_tee.py:375/380/394/399) and the final write (:419).  A TERM delivered while the
main thread is inside that `with status_lock:` block re-enters the same lock on the same
thread -> self-deadlock -> the tee never exits and never writes a final status.

pc_post.sh TERMs surviving tee pids at teardown, and the c2a drain loop keeps the main
thread in that loop for up to stall_timeout (5 s) on the production shape (client holds
stdin open), calling _write_status ~10x/s.

The window is widened HONESTLY (no code change): the timeline file is a symlink to
/dev/full so every frame appends one write_errors entry, and each status write then has
to serialise that whole list.
"""
import json
import os
import pathlib
import random
import subprocess
import sys
import textwrap
import time

# PROBE_WORK: the work dir holding base/ (a copy or symlink of the tree under test) — sandbox default below.
_VB6 = os.environ.get("PROBE_WORK", "/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vb6")

TEE = os.environ.get(
    "PROBE_TEE",
    _VB6 + "/base/proofs/S0-01/tools/frame_tee.py")
WORK = pathlib.Path(_VB6 + "/sigwork")

AGENT = """
    import sys, json
    line = sys.stdin.readline()
    sys.stdout.write('{"jsonrpc":"2.0","id":1,"result":{}}' + chr(10))
    sys.stdout.flush()
    sys.exit(0)
"""


def trial(i, nprefill, term_after, hang_budget=12.0):
    d = WORK / ("t%d" % i)
    subprocess.run(["rm", "-rf", str(d)])
    d.mkdir(parents=True)
    fd = d / "frames"
    fd.mkdir()
    os.symlink("/dev/full", str(fd / "timeline.jsonl"))   # every frame -> one write_errors entry
    a = d / "agent.py"
    a.write_text("#!%s\n" % sys.executable + textwrap.dedent(AGENT))
    a.chmod(0o755)
    e = os.environ.copy()
    e["S0_01_FRAMEDIR"] = str(fd)
    e["S0_01_AGENT"] = str(a)
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    tp = subprocess.Popen([sys.executable, TEE], stdin=subprocess.PIPE,
                          stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=e)
    line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "m", "params": {}},
                      separators=(",", ":")) + "\n"
    tp.stdin.write((line * nprefill).encode())
    tp.stdin.flush()                     # stdin stays OPEN -> the c2a drain loop runs 5 s
    time.sleep(term_after)
    t0 = time.monotonic()
    tp.terminate()
    hung = False
    try:
        tp.wait(timeout=hang_budget)
    except subprocess.TimeoutExpired:
        hung = True
        tp.kill()
        tp.wait(timeout=5)
    el = time.monotonic() - t0
    tp.stdin.close()
    tp.stderr.close()
    stp = fd / "tee-status.json"
    st = json.loads(stp.read_text()) if stp.exists() else None
    return {"i": i, "term_after": round(term_after, 3), "rc": tp.returncode,
            "secs_after_term": round(el, 2), "HUNG": hung,
            "n_errs": (len(st["write_errors"]) if st else None),
            "final": (st["final"] if st else None)}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    prefill = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    random.seed(7)
    hangs = 0
    for i in range(n):
        # aim inside the 5 s c2a drain window that starts once the agent has exited
        r = trial(i, prefill, 1.0 + random.random() * 4.0)
        hangs += 1 if r["HUNG"] else 0
        print(json.dumps(r))
    print("SIGTERM-deadlock trials=%d HUNG=%d" % (n, hangs))
