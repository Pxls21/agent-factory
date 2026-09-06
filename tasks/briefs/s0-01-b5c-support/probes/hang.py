#!/usr/bin/env python3
"""Decisive probe: c2a directional file unwritable (ENOSPC) + an agent that reads
to EOF (the production shape, and the shape frame_tee.py's own docstring now requires).
Compare with the suite's own agent (exits after one readline)."""
import json
import os
import pathlib
import subprocess
import sys
import textwrap
import time

# PROBE_WORK: the work dir holding base/ (a copy or symlink of the tree under test) — sandbox default below.
_VB6 = os.environ.get("PROBE_WORK", "/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vb6")

TEE = os.environ.get(
    "PROBE_TEE",
    _VB6 + "/base/proofs/S0-01/tools/frame_tee.py")
WORK = pathlib.Path(_VB6 + "/hangwork")


def case(name, agent_code, nlines, target, timeout=25):
    d = WORK / name.split()[0]
    subprocess.run(["rm", "-rf", str(d)])
    d.mkdir(parents=True)
    fd = d / "frames"
    fd.mkdir()
    os.symlink("/dev/full", str(fd / target))
    a = d / "agent.py"
    a.write_text("#!%s\n" % sys.executable + textwrap.dedent(agent_code))
    a.chmod(0o755)
    e = os.environ.copy()
    e["S0_01_FRAMEDIR"] = str(fd)
    e["S0_01_AGENT"] = str(a)
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "m", "params": {}},
                      separators=(",", ":")) + "\n"
    t0 = time.monotonic()
    try:
        r = subprocess.run([sys.executable, TEE], input=(line * nlines).encode(),
                           capture_output=True, env=e, timeout=timeout)
        rc = str(r.returncode)
        err = r.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired as ex:
        rc = "HANG(killed at %ds)" % timeout
        err = (ex.stderr or b"").decode("utf-8", "replace")
    el = time.monotonic() - t0
    stp = fd / "tee-status.json"
    st = json.loads(stp.read_text()) if stp.exists() else None
    print("%-36s target=%-30s n=%-4d rc=%-18s wall=%5.1fs status=%s"
          % (name, target, nlines, rc, el,
             "MISSING" if st is None
             else "final=%s exit=%s errs=%d" % (st["final"], st["exit_code"], len(st["write_errors"]))))
    if err.strip():
        print("    tee stderr: %s" % err.strip().replace("\n", " | ")[:700])


AGENT_READS_TO_EOF = """
    import sys
    sys.stdin.read()
    sys.exit(0)
"""
AGENT_SUITE_STYLE = """
    import sys, json
    line = sys.stdin.readline()
    sys.stdout.write('{"jsonrpc":"2.0","id":1,"result":{}}\\n')
    sys.stdout.flush()
    sys.exit(0)
"""

if __name__ == "__main__":
    case("A-suite-style-agent-1-line", AGENT_SUITE_STYLE, 1, "frames-client-to-agent.jsonl")
    case("B-EOF-agent-1-line", AGENT_READS_TO_EOF, 1, "frames-client-to-agent.jsonl")
    case("C-EOF-agent-100-lines", AGENT_READS_TO_EOF, 100, "frames-client-to-agent.jsonl")
    case("D-EOF-agent-a2c-unwritable", AGENT_READS_TO_EOF, 5, "frames-agent-to-client.jsonl")
    case("E-EOF-agent-timeline-unwritable", AGENT_READS_TO_EOF, 5, "timeline.jsonl")
