import sys, json, os, shutil, secrets, subprocess
sys.path.insert(0, ".")
import h
from pathlib import Path
RK = Path("repo_k").resolve()
def fresh():
    shutil.rmtree(RK, ignore_errors=True); shutil.copytree(h.R, RK, symlinks=True); shutil.rmtree(RK / ".jev", ignore_errors=True)
# ---- item 5: the kill switch
for kind in ("file", "directory", "dangling symlink", "symlink to a file"):
    fresh(); st = RK / ".jev"; st.mkdir()
    off = st / "system1-off"
    if kind == "file": off.write_text("")
    elif kind == "directory": off.mkdir()
    elif kind == "dangling symlink": off.symlink_to(st / "nowhere")
    else: (st / "target").write_text(""); off.symlink_to(st / "target")
    a = h.run(h.PRE, json.dumps(h.bash("git commit -m x", repo=RK)).encode(), repo=RK)
    b = h.run(h.PROMPT, json.dumps(h.prompt("negotiate the contract gate before building the increment", repo=RK)).encode(), repo=RK)
    s = h.run(h.START, json.dumps(h.start("compact", repo=RK)).encode(), repo=RK)
    tel = h.telemetry(RK)
    print(f"kill switch as a {kind:17s}: PreToolUse out {len(a.stdout)}B rc {a.returncode} | prompt out {len(b.stdout)}B rc {b.returncode} | "
          f"SessionStart rc {s.returncode} out {len(s.stdout)}B | telemetry lines {[r['event'] for r in tel]}")
# ---- the exception path: exactly one telemetry line naming the type, nothing out
fresh()
d = RK / ".jev/system1-seen"; d.mkdir(parents=True); (d / "vs1-session.main.json").mkdir()
r = h.run(h.PRE, json.dumps(h.bash("git commit -m x", repo=RK)).encode(), repo=RK)
tel = h.telemetry(RK)
print("exception path: rc", r.returncode, "stdout", len(r.stdout), "stderr", len(r.stderr), "| telemetry lines", len(tel), "| its keys", sorted(tel[0]), "| error", tel[0].get("error"))
# ---- item 6: canaries in every tool-input field, a prompt, and the SessionStart payload
fresh()
C = {k: "CNRY" + secrets.token_hex(12) for k in ("cmd", "desc", "content", "path", "old", "new", "prompt", "cwd", "tpath", "tuid", "sspath")}
calls = [
 ("PRE", dict(h.bash(f"git commit -m 'token={C['cmd']}' && git push origin HEAD:x", repo=RK), transcript_path=f"/tmp/{C['tpath']}.jsonl", tool_use_id=C["tuid"])),
 ("PRE", h.tool("Bash", {"command": f"echo {C['cmd']} 13:0xZ 5 passed", "description": C["desc"]}, repo=RK)),
 ("PRE", h.write(f"tasks/briefs/{C['path']}/X-brief.md", f"# brief {C['content']}\nDORMANT 12:3xZ 3 failed\n", repo=RK)),
 ("PRE", h.edit(f"tests/test_{C['path']}.py", new=f"assert '{C['new']}' DORMANT", old=C["old"], repo=RK)),
 ("PRE", dict(h.edit(f"/tmp/{C['path']}/scripts/push_gate.py", new=C["new"], old=C["old"], repo=RK), cwd=f"/tmp/{C['cwd']}")),
 ("PROMPT", h.prompt(f"negotiate the contract gate {C['prompt']} before the build, write the brief", repo=RK)),
 ("PROMPT", h.prompt(f"<task-notification> {C['prompt']}", repo=RK)),
 ("START", dict(h.start("compact", repo=RK), transcript_path=f"/tmp/{C['sspath']}.jsonl", cwd=f"/tmp/{C['cwd']}")),
]
outs = []
for kind, p in calls:
    cmd = {"PRE": h.PRE, "PROMPT": h.PROMPT, "START": h.START}[kind]
    r = h.run(cmd, json.dumps(p).encode(), repo=RK)
    outs.append(r.stdout + r.stderr)
hits = {}
for f in RK.rglob("*"):
    if f.is_file() and not f.is_symlink():
        b = f.read_bytes()
        for k, v in C.items():
            if v.encode() in b or v[4:].encode() in b:
                hits.setdefault(k, []).append(str(f.relative_to(RK)))
for k, v in C.items():
    for o in outs:
        if v.encode() in o: hits.setdefault(k, []).append("<hook stdout/stderr>")
print("canary fields:", len(C), "| files written under .jev:", sorted(str(p.relative_to(RK / '.jev')) for p in (RK / ".jev").rglob("*") if p.is_file()))
print("canary hits (field -> where):", hits or "NONE")
tel = h.telemetry(RK)
print("telemetry records:", len(tel), "| key sets:", sorted({tuple(sorted(r)) for r in tel}))
print("injections that happened (so the canaries rode through real work):", [len(r.get("injected", [])) for r in tel])
shutil.rmtree(RK, ignore_errors=True)
