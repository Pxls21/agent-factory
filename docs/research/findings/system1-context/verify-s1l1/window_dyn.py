import os, sys, time, json
sys.path.insert(0, ".")
import h
h.wipe_state()
C = "git commit -m 'x'"
def pre(sid, agent=None):
    return h.ctx(h.run(h.PRE, h.bash(C, sid=sid, agent=agent)))
def ss(source, sid, agent=None):
    r = h.run(h.START, h.start(source, sid=sid, agent=agent))
    assert (r.returncode, r.stdout) == (0, b""), (r.returncode, r.stdout[:200])
    return h.telemetry()[-1]
res = []
A, B = "vs1-A", "vs1-B"
res.append(("A.main first", bool(pre(A))))
res.append(("A.main again", bool(pre(A))))
res.append(("A.agentX first", bool(pre(A, "agentX"))))
res.append(("B.main first", bool(pre(B))))
for src in ("startup", "fork", "", "weird"):
    t = ss(src, A)
    res.append((f"after SessionStart {src!r}: A.main / A.X injects", bool(pre(A)), bool(pre(A, "agentX")), "removed", t.get("removed")))
t = ss("compact", A)
res.append(("after compact(main): A.main / A.X / B.main", bool(pre(A)), bool(pre(A, "agentX")), bool(pre(B)), "removed", t["removed"]))
t = ss("compact", A, "agentX")
res.append(("after compact(agentX): A.main / A.X", bool(pre(A)), bool(pre(A, "agentX")), "removed", t["removed"]))
for src in ("resume", "clear"):
    t = ss(src, A)
    res.append((f"after {src}: A.main / A.X / B.main", bool(pre(A)), bool(pre(A, "agentX")), bool(pre(B)), "removed", t["removed"]))
# no payload at all on SessionStart (empty stdin): nothing reset, still exits 0
r = h.run(h.START, b"")
res.append(("SessionStart with empty stdin rc/stdout", r.returncode, r.stdout))
for x in res: print(x)
# the 7-day prune
seen = h.state() / "system1-seen"
old = time.time() - 8 * 86400
for name in ("vs1-C.main.json", "vs1-C.main.json.lock", "vs1-C.main.json.123.tmp", "vs1-C.agentY.json"):
    p = seen / name; p.write_text('{"keys": []}'); os.utime(p, (old, old))
before = sorted(os.listdir(seen))
t = ss("startup", A)
after = sorted(os.listdir(seen))
print("prune: before", len(before), "after", len(after), "removed(count of .json)", t["removed"], "left C files:", [n for n in after if n.startswith("vs1-C")])
# an old marker of the LIVE window A.main is pruned too (a window idle for 7 days loses its memory)
p = seen / "vs1-A.main.json"
pre(A)
os.utime(p, (old, old))
ss("startup", B)
print("A.main marker idle 8 days, after another session's startup: exists =", p.exists(), "| A.main injects again:", bool(pre(A)))
