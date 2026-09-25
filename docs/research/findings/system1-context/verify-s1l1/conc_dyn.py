import os, sys, json, subprocess, time, collections, fcntl
sys.path.insert(0, ".")
import h
CMDS = ["git commit -m x && git push origin HEAD:claude/x", "bash scripts/pc.sh 'sqlite3 a.db; podman ps'",
        "bash scripts/pc_suite.sh launch -- tests/test_vendored_manifest.py", "nohup python3 x.py > l 2>&1 &",
        "python3 scripts/anchor_edit.py f --replace a b", "pgrep -f '[x]' ; graft ask q", "bash scripts/lane_context.sh -q q",
        "npx gitnexus analyze && python3 scripts/vendored_manifest.py --write"]
def launch(sid, n):
    env = h.env_for()
    procs = []
    for k in range(n):
        data = json.dumps(h.bash(CMDS[k % len(CMDS)], sid=sid)).encode()
        p = subprocess.Popen(["sh", "-c", h.PRE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env, cwd=str(h.R))
        procs.append((p, data))
    for p, data in procs:
        p.stdin.write(data); p.stdin.close()
    outs = []
    for p, _ in procs:
        o = p.stdout.read(); p.wait(); outs.append(h.ctx(type("R", (), {"returncode": p.returncode, "stdout": o, "stderr": b""})()))
    return outs
def tally(outs, sid):
    count = collections.Counter()
    for c in outs:
        for rid, skill, hd, idx in (h.check(c) if c else []):
            for i in idx:
                count[(skill, i)] += 1
    dup = sum(1 for v in count.values() if v > 1)
    marker = h.state() / "system1-seen" / f"{sid}.main.json"
    import hashlib
    keys = set(json.loads(marker.read_text())["keys"]) if marker.exists() else set()
    def key(skill, i):
        line = h.skill_text(skill).split("\n")[i]
        return hashlib.sha1(f"{skill}\n{line}".encode()).hexdigest()[:16]
    lost = sum(1 for (skill, i) in count if key(skill, i) not in keys)
    return len(count), dup, lost
h.wipe_state()
for trial in range(4):
    sid = f"vs1-conc-{trial}"
    t0 = time.monotonic(); outs = launch(sid, 16); dt = time.monotonic() - t0
    print("free lock   trial", trial, "lines delivered / delivered twice / delivered but missing from the marker:", tally(outs, sid), f"wall {dt:.2f}s")
# hold the window lock from outside (a stuck or slow sibling), then the same burst
for trial in range(2):
    sid = f"vs1-held-{trial}"
    seen = h.state() / "system1-seen"; seen.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(seen / f"{sid}.main.json.lock"), os.O_WRONLY | os.O_CREAT, 0o600); fcntl.flock(fd, fcntl.LOCK_EX)
    t0 = time.monotonic(); outs = launch(sid, 16); dt = time.monotonic() - t0
    os.close(fd)
    print("HELD lock   trial", trial, "lines delivered / delivered twice / delivered but missing from the marker:", tally(outs, sid), f"wall {dt:.2f}s")
recs = [r for r in h.telemetry() if r.get("window", "").startswith("vs1-held")]
ms = sorted(r["ms"] for r in recs)
print("held-lock hook-internal ms: min", ms[0], "median", ms[len(ms)//2], "max", ms[-1], "| errors:", collections.Counter(r.get("error") for r in h.telemetry() if r.get("error")))
print("marker files valid JSON:", all(json.loads(p.read_text()) is not None for p in (h.state() / "system1-seen").glob("*.json")))
print("stray tmp files:", [p.name for p in (h.state() / "system1-seen").iterdir() if p.name.endswith(".tmp")])
