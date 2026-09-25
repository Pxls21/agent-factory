import sys, json, os, shutil, uuid, statistics, time, subprocess
sys.path.insert(0, ".")
import h
from pathlib import Path
RL = Path("repo_l").resolve()
shutil.rmtree(RL, ignore_errors=True); shutil.copytree(h.R, RL, symlinks=True); shutil.rmtree(RL / ".jev", ignore_errors=True)
N = 20
def stats(walls, mss, outs, label):
    walls = sorted(walls); p90 = walls[int(0.9 * (len(walls) - 1))]
    ms = f"{statistics.median(mss):6.1f}" if mss else "     -"
    print(f"{label:58s} wall median {statistics.median(walls)*1000:6.1f} ms p90 {p90*1000:6.1f} ms | hook-internal median {ms} ms | out>0 {sum(outs)}/{len(outs)}")
def series(cmd, mk, label, n=N, prep=None):
    walls, mss, outs = [], [], []
    for k in range(n):
        if prep: prep(k)
        before = len(h.telemetry(RL))
        r = h.run(cmd, json.dumps(mk(k)).encode(), repo=RL)
        walls.append(r.wall); outs.append(len(r.stdout) > 0)
        tel = h.telemetry(RL)
        if len(tel) > before and "ms" in tel[-1]: mss.append(tel[-1]["ms"])
    stats(walls, mss, outs, label)
wrapper_true = f"python3 {RL}/scripts/hook_context.py PreToolUse -- true"
series(wrapper_true, lambda k: {}, "reference: hook_context.py wrapping `true`")
series(h.PRE, lambda k: h.bash("ls -la", repo=RL, sid=f"L-{k}"), "PreToolUse Bash, no row matches (ls -la)")
series(h.PRE, lambda k: h.bash("git commit -m x", repo=RL, sid=f"L2-{k}"), "PreToolUse Bash, 2 rows inject (git commit), fresh window")
series(h.PRE, lambda k: h.bash("git commit -m x", repo=RL, sid="L3"), "PreToolUse Bash, same window again (duplicate)")
series(h.PRE, lambda k: h.edit("scripts/x.py", "y = 2", repo=RL, sid=f"L4-{k}"), "PreToolUse Edit of a code file, fresh window")
(RL / ".jev/system1-cache.json").unlink(missing_ok=True)
series(h.PROMPT, lambda k: h.prompt("bug echo after the fix, find similar bugs", repo=RL, sid=f"L5-{k}"), "UserPromptSubmit, cold cache (first prompt builds it)", n=1)
series(h.PROMPT, lambda k: h.prompt("bug echo after the fix, find similar bugs", repo=RL, sid=f"L6-{k}"), "UserPromptSubmit, warm cache, 2 excerpts inject")
series(h.PROMPT, lambda k: h.prompt("please fix the typo in the README", repo=RL, sid=f"L7-{k}"), "UserPromptSubmit, warm cache, nothing scores")
series(h.START, lambda k: h.start("compact", repo=RL, sid=f"L8-{k}"), "SessionStart: session-start.sh with the reset (compact)")
(RL / ".jev/system1-off").write_text("")
series(h.PRE, lambda k: h.bash("git commit -m x", repo=RL, sid=f"L9-{k}"), "kill switch on: PreToolUse Bash (git commit)")
shutil.rmtree(RL, ignore_errors=True)
