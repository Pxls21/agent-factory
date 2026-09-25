import sys, json, os, shutil, uuid, time
sys.path.insert(0, ".")
import h
from pathlib import Path
RB = Path("repo_h").resolve()
def fresh():
    shutil.rmtree(RB, ignore_errors=True); shutil.copytree(h.R, RB, symlinks=True)
    shutil.rmtree(RB / ".jev", ignore_errors=True)
def one(name, data, cmd=None, prep=None, want_inject=None, pre_cmd=""):
    fresh()
    if prep: prep()
    c = cmd or h.PRE
    full = f"{pre_cmd}{c}" if pre_cmd else c
    t0 = time.monotonic()
    r = h.run(full, data, repo=RB, timeout=120)
    dt = time.monotonic() - t0
    out = r.stdout.decode("utf-8", "replace")
    try:
        ctx = h.ctx(r)
    except Exception as e:
        ctx = f"<unparsed: {type(e).__name__}>"
    tel = h.telemetry(RB) if (RB / ".jev").is_dir() else []
    last = tel[-1] if tel else {}
    jev = sorted(str(p.relative_to(RB / ".jev")) for p in (RB / ".jev").rglob("*")) if (RB / ".jev").is_dir() else "no .jev dir"
    ok = r.returncode == 0 and (want_inject is None or bool(ctx) == want_inject)
    print(f"{'OK ' if ok else 'BAD'} {name:60s} rc {r.returncode} wall {dt:5.2f}s ctx {len(ctx):5d}B err {last.get('error')!s:18s} stderr {len(r.stderr)}B jev {jev if isinstance(jev, str) else len(jev)}")
    return r, ctx, last, jev
B = lambda cmd: json.dumps(h.bash(cmd, repo=RB)).encode()
one("empty stdin", b"", want_inject=False)
one("not JSON", b"{not json", want_inject=False)
one("invalid UTF-8 inside a JSON string", b'{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git commit \xff\xfe"},"session_id":"s"}', want_inject=False)
one("NUL escapes in the command", B("git commit -m '\u0000\u0000'"), want_inject=True)
one("deep nesting 100k arrays", b"[" * 100000 + b"]" * 100000, want_inject=False)
one("deep nesting inside tool_input", ('{"hook_event_name":"PreToolUse","tool_name":"Bash","session_id":"s","tool_input":' + "[" * 50000 + "]" * 50000 + "}").encode(), want_inject=False)
one("30 MB Write content", json.dumps(h.write("docs/big.md", ("line 12:3xZ 4 passed DORMANT\n" * 1_100_000), repo=RB)).encode(), want_inject=True)
for label, ti in (("command is a list", {"command": ["git", "commit"]}), ("command is null", {"command": None}),
                  ("tool_input is a string", "git commit"), ("file_path is a list", None)):
    p = h.bash("x", repo=RB); p["tool_input"] = ti if ti is not None else {"file_path": ["a"], "content": 3}
    if label == "file_path is a list": p["tool_name"] = "Write"
    one(label, json.dumps(p).encode(), want_inject=False)
p = h.bash("git commit -m x", repo=RB); p.update(cwd=12, session_id={"a": 1}, agent_id="../../../etc/passwd")
r, ctx, last, jev = one("cwd int, session_id dict, agent_id with ../", json.dumps(p).encode(), want_inject=True)
print("     marker names:", [x for x in jev if x.startswith("system1-seen/")])
one("unknown tool name", json.dumps(dict(h.bash("git commit", repo=RB), tool_name="Read")).encode(), want_inject=False)
one("missing skill dir (env-tool-quirks)", B("git commit -m x"), prep=lambda: shutil.rmtree(RB / ".claude/skills/env-tool-quirks"), want_inject=False)
one("SKILL.md is a directory", B("git commit -m x"), prep=lambda: (os.remove(RB / ".claude/skills/env-tool-quirks/SKILL.md"), os.mkdir(RB / ".claude/skills/env-tool-quirks/SKILL.md")), want_inject=False)
one("table missing", B("git commit -m x"), prep=lambda: os.remove(RB / ".claude/hooks/system1-situations.json"), want_inject=False)
one("table not JSON", B("git commit -m x"), prep=lambda: (RB / ".claude/hooks/system1-situations.json").write_text("{"), want_inject=False)
def bad_regex():
    p = RB / ".claude/hooks/system1-situations.json"; t = json.loads(p.read_text()); t["rows"][0]["command"] = "pc\\.sh(("; p.write_text(json.dumps(t))
one("a row regex that does not compile (row 1, Bash)", B("git commit -m x"), prep=bad_regex, want_inject=False)
def break_anchor():
    p = RB / ".claude/skills/env-tool-quirks/SKILL.md"; p.write_text(p.read_text().replace("**`scripts/safe_commit.sh -m", "**`scripts/safe-commit.sh -m"))
r, ctx, last, jev = one("commit row's anchor no longer resolves", B("git commit -m x"), prep=break_anchor, want_inject=True)
print("     rows injected:", [i["row"] for i in last.get("injected", [])], "skipped:", [(s["row"], s["why"]) for s in last.get("skipped", [])])
one(".jev missing (created)", B("git commit -m x"), want_inject=True)
one(".jev is a regular file", B("git commit -m x"), prep=lambda: (RB / ".jev").write_text("x"), want_inject=False)
r, ctx, last, jev = one("full disk (ulimit -f 0: every write fails EFBIG)", B("git commit -m x"), pre_cmd="ulimit -f 0; ", want_inject=False)
print("     .jev after:", jev)
def corrupt_marker():
    d = RB / ".jev/system1-seen"; d.mkdir(parents=True); (d / "vs1-session.main.json").write_text('{"keys": [')
r, ctx, last, jev = one("torn marker JSON", B("git commit -m x"), prep=corrupt_marker, want_inject=False)
r2 = h.run(h.PRE, B("git commit -m x"), repo=RB); print("     the next call in that window injects:", bool(h.ctx(r2)), "| error:", h.telemetry(RB)[-1].get("error"))
shutil.rmtree(RB, ignore_errors=True)
