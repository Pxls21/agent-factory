#!/usr/bin/env python3
"""Production-shaped A21d check.

A21d exists because the pinned buzz-acp SIGKILLs the agent process group at shutdown,
so the leg's tee-status.json is whatever running snapshot happened to be on disk.  The
checker then requires (A21d): recorded_<dir> == the timeline's per-direction counts AND
updated_seq == the timeline's last seq.

_write_status() snapshots state[] and seq[0] WITHOUT holding the `lock` that makes a
timeline write and its counter increment one atomic step (frame_tee.py:148-165 vs
:200-211 / :286-297), so a snapshot taken between the two is internally inconsistent.

This runs the tee with BOTH directions busy, SIGKILLs it at a random instant, and grades
the surviving status against the surviving timeline exactly as A21d says the checker does.
"""
import json
import os
import pathlib
import random
import shutil
import subprocess
import sys
import textwrap
import time

# PROBE_WORK: the work dir holding base/ (a copy or symlink of the tree under test) — sandbox default below.
_VB6 = os.environ.get("PROBE_WORK", "/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vb6")

TEE = os.environ.get(
    "PROBE_TEE",
    _VB6 + "/base/proofs/S0-01/tools/frame_tee.py")
WORK = pathlib.Path(_VB6 + "/killwork")

AGENT = """
    import sys, json
    n = 0
    for line in sys.stdin:
        n += 1
        sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":n,"result":{}}, separators=(",",":")) + chr(10))
        sys.stdout.flush()
    sys.exit(0)
"""


def trial(i, kill_after):
    d = WORK / str(i)
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    fd = d / "frames"
    fd.mkdir()
    a = d / "agent.py"
    a.write_text("#!%s\n" % sys.executable + textwrap.dedent(AGENT))
    a.chmod(0o755)
    e = os.environ.copy()
    e["S0_01_FRAMEDIR"] = str(fd)
    e["S0_01_AGENT"] = str(a)
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    tp = subprocess.Popen([sys.executable, TEE], stdin=subprocess.PIPE,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=e)
    line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "m", "params": {}},
                      separators=(",", ":")) + "\n"
    payload = (line * 20000).encode()
    try:
        tp.stdin.write(payload)
        tp.stdin.flush()
    except (BrokenPipeError, OSError):
        pass
    time.sleep(kill_after)
    os.kill(tp.pid, 9)          # what buzz-acp does to the process group at shutdown
    tp.wait(timeout=10)
    try:
        tp.stdin.close()
    except Exception:
        pass
    stp = fd / "tee-status.json"
    tl = fd / "timeline.jsonl"
    if not stp.exists() or not tl.exists():
        return {"i": i, "verdict": "NO-STATUS"}
    st = json.loads(stp.read_text())
    ents = []
    for raw in tl.read_bytes().split(b"\n"):
        if raw.strip():
            try:
                ents.append(json.loads(raw))
            except Exception:
                pass            # a torn last timeline line: not this probe's subject
    per = {}
    for x in ents:
        per[x["dir"]] = per.get(x["dir"], 0) + 1
    last = ents[-1]["seq"] if ents else 0
    checks = {
        "recorded_c2a==timeline_c2a": st["recorded_c2a"] == per.get("c2a", 0),
        "recorded_a2c==timeline_a2c": st["recorded_a2c"] == per.get("a2c", 0),
        "updated_seq==timeline_last_seq": st["updated_seq"] == last,
        "internally_consistent(updated_seq==rec_c2a+rec_a2c)":
            st["updated_seq"] == st["recorded_c2a"] + st["recorded_a2c"],
        "final_is_false": st["final"] is False,
        "exit_fields_null": st["agent_returncode"] is None and st["exit_code"] is None,
    }
    failed = [k for k, v in checks.items() if not v]
    return {"i": i, "verdict": "A21d-PASS" if not failed else "A21d-FAIL", "failed": failed,
            "updated_seq": st["updated_seq"], "rec_c2a": st["recorded_c2a"],
            "rec_a2c": st["recorded_a2c"], "tl_c2a": per.get("c2a", 0),
            "tl_a2c": per.get("a2c", 0), "tl_last": last}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    random.seed(11)
    res = [trial(i, 0.10 + random.random() * 0.9) for i in range(n)]
    for r in res:
        if r["verdict"] != "A21d-PASS":
            print(json.dumps(r))
    fails = sum(1 for r in res if r["verdict"] != "A21d-PASS")
    print("SIGKILL-at-random-instant trials=%d  A21d-FAIL/NO-STATUS=%d  A21d-PASS=%d"
          % (n, fails, n - fails))
