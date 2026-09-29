"""K2 (task #353, D-106): scripts/filepacks.py, the context pack of every tracked file (P2) and the hook that shows it
when a file is touched (P1).

Every check runs on a throwaway git repository (`fixture`) that holds copies of the tooling (the builder and hook, the
code map, the wrapper and the System-1 hook it imports) beside a small tracked tree whose ledger-plane sources name its
files in known places. The builder runs as the post-commit hook runs it (`python3 scripts/filepacks.py build`) and the
hook as the harness will: through the REAL wrapper, with the exact command strings the registration adds (REG_PRE,
REG_RESET). State never touches the real .jev/: AF_FILEPACKS_STATE and AF_S1_RATE_STATE point each run at the test's
own directory. The oracles are independent of the code under test: the fixture's own construction (which line names
which file, which commit touched which file), Python's ast for symbol spans, git for commit ids and blob ids.

Each property is a check run on the real filepacks.py and on mutated copies of it (MUTANTS: one mutation per property,
its anchor found exactly once, the mutant compiled before use, so a mutant that does not compile is never counted as a
kill). A mutant must fail the same check with the named failure. The code-map pack of scripts/alpha.py is planted in
codemap.py's format, its symbols from the file's own AST as the real builder's are (tests/test_codemap.py
check_pack_fields holds them equal); test_the_planted_code_pack_has_the_real_builders_fields compares its fields with a
pack the real codemap builder writes. Deterministic and LLM-free.
"""
import ast
import fcntl
import hashlib
import importlib.util
import json
import os
import re
import secrets
import shutil
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FILEPACKS = ROOT / "scripts" / "filepacks.py"
TOOLING = {"scripts/filepacks.py": FILEPACKS, "scripts/codemap.py": ROOT / "scripts" / "codemap.py",
           "scripts/hook_context.py": ROOT / "scripts" / "hook_context.py",
           ".claude/hooks/system1-context.py": ROOT / ".claude" / "hooks" / "system1-context.py"}
# The registration the coordinator adds at landing (the repo's .claude/settings.json spelling).
REG_PRE = ("[ -f $CLAUDE_PROJECT_DIR/scripts/filepacks.py ] && [ -f $CLAUDE_PROJECT_DIR/scripts/hook_context.py ] || "
           "exit 0; python3 $CLAUDE_PROJECT_DIR/scripts/hook_context.py PreToolUse -- python3 "
           "$CLAUDE_PROJECT_DIR/scripts/filepacks.py hook")
REG_RESET = ("[ -f $CLAUDE_PROJECT_DIR/scripts/filepacks.py ] || exit 0; python3 "
             "$CLAUDE_PROJECT_DIR/scripts/filepacks.py hook --reset")
SID = "k2test-session-0001"
STAMP = re.compile(r"\[S1 (s1-[0-9a-f]{8}) filepacks\]")                       # the wrapper's stamp (S1-RATE)
REQUEST = ('Begin your next text with "S1-RATE {id} rel=R use=U" (+ a note <=120 chars: why, if a 0), one line per '
           'unscored injection. rel 0 unrelated,1 same area not this step,2 relevant to this step,3 governs it; '
           'use 0 noise/known,1 confirms,2 used it,3 changed what I did')
EPOCH = 1767225600                 # 2026-01-01T00:00:00Z: the fixture's commit clock, so its ids repeat run to run
SKILLS = ("env-tool-quirks", "pc-bridge-lanes", "orchestration", "build-loop", "deep-work", "anti-hollow-green",
          "session-continuity", "code-intel-trio", "ouroboros-stdio")

ALPHA = '''"""alpha: the file-pack fixture (K2)."""
import os


def helper(x):
    return x + 1


class Box:
    def __init__(self, v):
        self.v = helper(v)

    def get(self):
        return self.v


def main():
    return Box(os.getpid()).get()
'''
LONG_HEAD = "T3 " + "H" * 200
LEDGER, DECISIONS, INCIDENTS = "todo/BUILD-TASKLIST.md", "docs/08_DECISION_LOG.md", "docs/INCIDENT-LOG.md"
SKILL = ".claude/skills/env-tool-quirks/SKILL.md"
BRIEF = "tasks/briefs/k/%s-brief.md"
NOTE_LEDGER = "**T1 LANDED — alpha.** the first line naming scripts/alpha.py and docs/NOTE.md."


def base_files(repo):
    """The first commit's tree. The ledger names scripts/alpha.py on lines 2, 4, 5, 6 (by its absolute path) and 7;
    lines 8 and 9 name only other paths that hold it (the whole-path boundary)."""
    ledger = "\n".join([
        "# ledger",
        NOTE_LEDGER,
        "a plain line naming nothing",
        "**T2 DISPATCHED.** second: `scripts/alpha.py`.",
        "**%s** third: %s scripts/alpha.py %s" % (LONG_HEAD, "f" * 260, "g" * 260),
        "**T4 HOME.** fourth, absolute: %s/scripts/alpha.py" % repo,
        "the fifth ends on the name: see scripts/alpha.py.",
        "a line naming scripts/alpha.py.json only",
        "a line naming x/scripts/alpha.py only"]) + "\n"
    return {LEDGER: ledger,
            DECISIONS: "# decisions\n| Id | Decision |\n|---|---|\n| D-001 | a ruling on scripts/alpha.py |\n"
                       "| D-002 | a ruling on docs/NOTE.md |\n",
            INCIDENTS: "# incidents\n| AF-AP-001 | a class seen in docs/NOTE.md |\n"
                       "**2026-01-01 — an entry naming docs/NOTE.md.**\n",
            SKILL: "---\nname: env-tool-quirks\ndescription: the fixture skill\n---\n# quirks\n- a quirk of scripts/alpha.py\n",
            "docs/NOTE.md": "# note\n", "scripts/alpha.py": ALPHA, "scripts/beta.py": "def STALE_beta():\n    return 2\n",
            "scripts/gamma.py": "def gamma():\n    return 3\n"}


def git(repo, *args, k=None):
    env = dict(os.environ)
    if k is not None:
        env.update(GIT_AUTHOR_DATE="@%d +0000" % (EPOCH + k), GIT_COMMITTER_DATE="@%d +0000" % (EPOCH + k))
    r = subprocess.run(["git", "-c", "user.email=k2@test", "-c", "user.name=k2", "-c", "core.hooksPath=/dev/null",
                        "-c", "commit.gpgsign=false", *args], cwd=repo, env=env, capture_output=True, text=True,
                       timeout=60)
    assert r.returncode == 0, (args, r.stdout[-400:], r.stderr[-400:])
    return r.stdout


def commit(repo, files, msg, k):
    for rel, text in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text, encoding="utf-8")
    git(repo, "add", "--", *files, k=k)
    git(repo, "commit", "-q", "-m", msg, k=k)
    return git(repo, "rev-parse", "HEAD").strip()


def ast_symbols(text):
    """[(qualname, def line, end line, first decorator line, kind, signature)] in line order: the oracle for spans."""
    out = []

    def walk(node, prefix, in_class):
        for n in ast.iter_child_nodes(node):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                q = prefix + n.name
                kind = "class" if isinstance(n, ast.ClassDef) else ("method" if in_class else "function")
                sig = text.split("\n")[n.lineno - 1].strip().rstrip(":")
                out.append((q, n.lineno, n.end_lineno, min([d.lineno for d in n.decorator_list] or [n.lineno]), kind,
                            sig))
                walk(n, q + ".", isinstance(n, ast.ClassDef))
            else:
                walk(n, prefix, in_class)
    walk(ast.parse(text), "", False)
    return sorted(out, key=lambda s: (s[1], -s[2], s[0]))


def plant_code_pack(repo, rel, commit_id):
    """A code-map pack of `rel` in codemap.py's format (schema 1), its symbols from the file's AST, fresh."""
    data = (repo / rel).read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    syms = []
    for q, start, end, frm, kind, sig in ast_symbols(data.decode("utf-8")):
        s = {"name": q.rsplit(".", 1)[-1], "qualname": q, "kind": kind, "start": start, "end": end, "signature": sig,
             "gitnexus": {"id": "Function:%s:%s" % (rel, q), "risk": "LOW", "impacted": 2, "direct": 1,
                          "callers": {"count": 1, "tests": 0, "sample": [{"name": "main", "file": rel, "line": 18}]}}}
        if frm != start:
            s["from"] = frm
        syms.append(s)
    fresh = {"status": "ok", "graph": "fresh", "indexed_sha256": sha}
    pack = {"schema": 1, "path": rel, "language": "python", "blob": git(repo, "hash-object", "--", rel).strip(),
            "sha256": sha, "lines": data.count(b"\n"), "bytes": len(data), "commit": commit_id,
            "symbols_from": "graft", "caller_files": [],
            "instruments": {"graft": dict(fresh), "gitnexus": dict(fresh, indexed_commit=commit_id, symbols=len(syms),
                                                                   unmatched=[]),
                            "code-review-graph": dict(fresh, tests_found=1),
                            "ap_screen": {"status": "ok", "rows_screened": 1}},
            "symbols": syms, "tests": [{"file": "tests/test_alpha.py", "line": 3, "name": "test_helper",
                                        "indirect": False}],
            "registry": [{"row": "AF-AP-9", "line": 2, "text": "import os", "message": "a fixture row"}],
            "built_at": "2026-01-01T00:00:00Z", "timing": {}}
    p = repo / ".jev" / "codemap" / (rel + ".json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(pack, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return pack


def fixture(tmp, fp_text=None):
    """(repo, commit ids): the tree committed at c1, briefs A to D one commit each (c2 to c5), then three commits to
    scripts/alpha.py (c6 to c8); the tooling copied in, never committed; alpha's code pack planted."""
    repo = tmp / "repo"
    repo.mkdir()
    repo = repo.resolve()
    git(repo, "init", "-q")
    for rel, src in TOOLING.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, repo / rel)
    if fp_text is not None:
        (repo / "scripts" / "filepacks.py").write_text(fp_text, encoding="utf-8")
    ids = {"c1": commit(repo, base_files(repo), "fixture: the tree", 1)}
    for k, name in enumerate("ABCD"):
        text = "# %s\nnames scripts/alpha.py%s\n" % (name, " and itself: " + BRIEF % name if name == "A" else "")
        ids[name] = commit(repo, {BRIEF % name: text}, "brief " + name, 2 + k)
    alpha = ALPHA
    for k, word in enumerate(("second", "third", "fourth")):
        alpha += "# rev %d\n" % (k + 2)
        ids[word] = commit(repo, {"scripts/alpha.py": alpha}, "alpha: " + word, 6 + k)
    plant_code_pack(repo, "scripts/alpha.py", ids["fourth"])
    return repo, ids


# ---------- running the builder and the hook as they run for real ----------

def env_for(repo, st):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo), AF_FILEPACKS_STATE=str(st), AF_S1_RATE_STATE=str(st))
    for k in ("PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX"):          # the registration sets neither
        env.pop(k, None)
    return env


def build(repo, st):
    r = subprocess.run(["python3", str(repo / "scripts" / "filepacks.py"), "build"], env=env_for(repo, st),
                       capture_output=True, text=True, timeout=120, cwd="/")
    assert r.returncode == 0, (r.stdout, r.stderr)
    return r.stdout


def run(repo, st, data, cmd=REG_PRE, timeout=60):
    data = data if isinstance(data, bytes) else json.dumps(data).encode()
    return subprocess.run(["sh", "-c", cmd], input=data, capture_output=True, timeout=timeout, env=env_for(repo, st),
                          cwd="/")


def context(r):
    """What reaches the model, the stamp checked against its literals and cut off: '' when nothing was printed."""
    assert r.returncode == 0, (r.returncode, r.stderr)
    out = r.stdout.decode("utf-8")
    if not out.strip():
        return ""
    obj = json.loads(out)
    assert set(obj) == {"hookSpecificOutput"} and set(obj["hookSpecificOutput"]) == {"hookEventName", "additionalContext"}
    first, _, rest = obj["hookSpecificOutput"]["additionalContext"].partition("\n")
    m = STAMP.fullmatch(first)
    assert m, first[:80]
    body, _, last = rest.rpartition("\n")
    assert last == REQUEST.format(id=m.group(1)), last[:80]
    return body


def records(st):
    p = Path(st) / "filepacks.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def pack(st, rel):
    return json.loads((Path(st) / "filepacks" / (rel + ".json")).read_text(encoding="utf-8"))


def payload(repo, tool, ti, sid=SID, agent=None, cwd=None):
    p = {"session_id": sid, "transcript_path": "/dev/null", "cwd": str(repo) if cwd is None else cwd,
         "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": ti, "tool_use_id": "toolu_k2test"}
    if agent:
        p["agent_id"] = agent
    return p


def read(repo, rel, sid=SID, agent=None, **kw):
    return payload(repo, "Read", dict({"file_path": "%s/%s" % (repo, rel)}, **kw), sid, agent)


def edit(repo, rel, old, new="x", sid=SID):
    return payload(repo, "Edit", {"file_path": "%s/%s" % (repo, rel), "old_string": old, "new_string": new}, sid)


def write(repo, rel, content="x\n", sid=SID):
    return payload(repo, "Write", {"file_path": "%s/%s" % (repo, rel), "content": content}, sid)


def bash(repo, cmd, sid=SID, cwd=None):
    return payload(repo, "Bash", {"command": cmd, "description": "a fixture"}, sid, cwd=cwd)


def start(source, sid=SID, agent=None):
    p = {"session_id": sid, "transcript_path": "/dev/null", "hook_event_name": "SessionStart", "source": source}
    if agent:
        p["agent_id"] = agent
    return p


def load(repo):
    """The repo's filepacks.py as a module (its reader and builder run in process); proven to be that copy."""
    path = repo / "scripts" / "filepacks.py"
    spec = importlib.util.spec_from_file_location("filepacks_%d" % time.monotonic_ns(), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.__file__ == str(path) and mod.ROOT == repo, (mod.__file__, mod.ROOT)
    return mod


# ---------- the checks (each also runs on a mutant, which must fail it) ----------

def check_edit_once_per_symbol(repo, st, ids, tmp):
    build(repo, st)
    a = context(run(repo, st, edit(repo, "scripts/alpha.py", "    return x + 1")))
    assert a.split("\n")[0] == ("codemap scripts/alpha.py:6 — function helper L5-6 · def helper(x)  "
                                "[pack .jev/codemap/scripts/alpha.py.json]"), "the Edit did not inject its symbol: %r" % a[:160]
    assert "\nfilepack scripts/alpha.py @" in a, "the first touch did not bring the pack's lines"
    b = context(run(repo, st, edit(repo, "scripts/alpha.py", "def helper(x):")))
    assert b == "", "a second Edit of the same symbol injected again"
    c = context(run(repo, st, edit(repo, "scripts/alpha.py", "        return self.v")))
    assert c.split("\n")[0].startswith("codemap scripts/alpha.py:14 — method Box.get L13-14"), \
        "an Edit of another symbol injected nothing: %r" % c[:120]
    assert "filepack scripts/alpha.py" not in c, "the pack's lines came twice in one window"
    keys = json.loads((st / "filepacks-seen" / ("%s.main.json" % SID)).read_text())["keys"]
    assert keys == ["file:scripts/alpha.py", "sym:scripts/alpha.py:Box.get", "sym:scripts/alpha.py:helper"], keys


def check_read_range(repo, st, ids, tmp):
    build(repo, st)
    syms = ast_symbols((repo / "scripts" / "alpha.py").read_text())
    want = "symbols in range: " + " · ".join("%s L%d-%d" % (q, f, e) for q, _, e, f, _, _ in syms if f <= 11 and e >= 4)
    lines = context(run(repo, st, read(repo, "scripts/alpha.py", offset=4, limit=8))).split("\n")
    assert want in lines, "a Read range did not show the symbols in range: %s" % lines[:2]
    assert lines[0].startswith("codemap scripts/alpha.py:4-11 — 3 of the file's 5 symbols in range")
    one = context(run(repo, st, read(repo, "scripts/alpha.py", sid="w-one", offset=13, limit=2))).split("\n")
    assert one[0].startswith("codemap scripts/alpha.py:13-14 — method Box.get L13-14"), \
        "a Read range inside one symbol did not show that symbol: %s" % one[0]


def check_bash_readers(repo, st, ids, tmp):
    build(repo, st)
    ctx = context(run(repo, st, bash(repo, "sed -n 1,40p scripts/alpha.py")))
    assert ctx.startswith("codemap scripts/alpha.py — 5 symbols, 3 at top level"), \
        "sed -n 1,40p did not inject the file: %r" % ctx[:80]
    for k, cmd in enumerate(["cat docs/NOTE.md", "head -n 3 docs/NOTE.md", "tail -2 docs/NOTE.md",
                             "grep -n note docs/NOTE.md", "awk '{print}' docs/NOTE.md", "wc -l docs/NOTE.md",
                             "nl docs/NOTE.md", "less docs/NOTE.md", "more docs/NOTE.md", "egrep x docs/NOTE.md",
                             "rg -n x docs/NOTE.md", "diff docs/NOTE.md scripts/beta.py",
                             "cmp docs/NOTE.md scripts/beta.py", "git log -1 && cat 'docs/NOTE.md' | head -1"]):
        assert "filepack docs/NOTE.md @" in context(run(repo, st, bash(repo, cmd, sid="r%d" % k))), \
            "the reader in %r injected nothing" % cmd
    assert "filepack docs/NOTE.md @" in context(run(repo, st, bash(repo, "cd %s && cat docs/NOTE.md" % repo,
                                                                   sid="cd1", cwd="/"))), "a cd was not followed"
    assert context(run(repo, st, bash(repo, "cat docs/NOTE.md", sid="cd2", cwd="/"))) == "", \
        "a relative path from / resolved into the repo"


def check_reset(repo, st, ids, tmp):
    build(repo, st)
    main, sub = read(repo, "docs/NOTE.md"), read(repo, "docs/NOTE.md", agent="agent-a1")
    assert context(run(repo, st, main)) and context(run(repo, st, main)) == ""
    assert context(run(repo, st, sub)), "a subagent is its own window"

    def reset(source, agent=None):
        r = run(repo, st, start(source, agent=agent), cmd=REG_RESET)
        assert (r.returncode, r.stdout) == (0, b"")
    reset("startup")
    assert context(run(repo, st, main)) == "", "a startup forgot the window"
    reset("compact")
    assert context(run(repo, st, main)), "a compact reset did not re-arm the window"
    assert context(run(repo, st, sub)) == "", "the subagent's window was forgotten by the main window's compaction"
    for source in ("resume", "clear"):
        reset(source)
        assert context(run(repo, st, main)) and context(run(repo, st, sub)), "a %s did not re-arm the session" % source
    resets = [r for r in records(st) if r["event"] == "SessionStart"]
    assert [(r["source"], r["removed"]) for r in resets] == [("startup", 0), ("compact", 1), ("resume", 2),
                                                               ("clear", 2)], resets


def check_doc_pack_lines(repo, st, ids, tmp):
    build(repo, st)
    head7 = git(repo, "rev-parse", "HEAD")[:7]
    want = ["filepack docs/NOTE.md @%s: ledger 1 · incidents 2 · decisions 1 · commits 1 (pack %s/filepacks/docs/"
            "NOTE.md.json)" % (head7, st),
            "ledger L2: " + NOTE_LEDGER,
            "incidents L3: **2026-01-01 — an entry naming docs/NOTE.md.**",
            "decisions L5 D-002: | D-002 | a ruling on docs/NOTE.md |",
            "commit %s 2026-01-01: fixture: the tree" % ids["c1"][:7],
            "incidents L2 AF-AP-001: | AF-AP-001 | a class seen in docs/NOTE.md |"]
    got = context(run(repo, st, read(repo, "docs/NOTE.md")))
    assert got.split("\n") == want, "a tracked document got no pack lines, or others: %r" % got[:300]
    rec = records(st)[-1]
    assert set(rec) == {"event", "tool", "tool_use_id", "injected", "skipped", "bytes", "window", "t", "ms"}, rec
    assert rec["injected"][0]["code"] is None and rec["injected"][0]["key"] == "file:docs/NOTE.md"
    assert context(run(repo, st, write(repo, "docs/NOTE.md", sid="w2"))).split("\n") == want, "a Write differs"


def check_build_lines(repo, st, ids, tmp):
    build(repo, st)
    alpha = pack(st, "scripts/alpha.py")
    led = [m for m in alpha["mentions"] if m["source"] == "ledger"]
    assert [m["line"] for m in led] == [7, 6, 5] and alpha["counts"]["ledger"] == 5, \
        "the ledger mentions are not the newest 3 on a whole-path boundary: %s" % [m["line"] for m in led]
    (dec,) = [m for m in alpha["mentions"] if m["source"] == "decisions"]
    assert (dec["line"], dec.get("id")) == (4, "D-001"), "a registry row lost its id: %s" % dec
    note = pack(st, "docs/NOTE.md")
    assert [(m["line"], m.get("id")) for m in note["mentions"] if m["source"] == "incidents"] == [
        (3, None), (2, "AF-AP-001")], "a registry row lost its id: %s" % note["mentions"]
    third = led[2]
    assert third["headline"] == LONG_HEAD[:159] + "…", "a ledger headline is over 160 characters: %d" % len(
        third["headline"])
    assert "scripts/alpha.py" in third["snippet"] and len(third["snippet"]) <= 240 \
        and third["snippet"][0] == third["snippet"][-1] == "…", "the snippet is not around the first mention"
    assert led[0] == {"source": "ledger", "line": 7, "snippet": "the fifth ends on the name: see scripts/alpha.py.",
                      "at": 0}, led[0]
    assert [(m["source"], m["line"]) for m in alpha["mentions"] if m["source"].startswith("skill:")] == [
        ("skill:env-tool-quirks", 6)]


def check_build_briefs_commits(repo, st, ids, tmp):
    build(repo, st)
    alpha = pack(st, "scripts/alpha.py")
    briefs = [(m["path"], m["line"], m["commit"]) for m in alpha["mentions"] if m["source"] == "brief"]
    assert briefs == [(BRIEF % n, 2, ids[n][:7]) for n in "DCB"] and alpha["counts"]["briefs"] == 4, \
        "the briefs are not the newest 3 by their last commit: %s" % briefs
    commits = [(m["commit"], m["subject"]) for m in alpha["mentions"] if m["source"] == "commit"]
    assert commits == [(ids[w][:7], "alpha: " + w) for w in ("fourth", "third", "second")] \
        and alpha["counts"]["commits"] == 4, "the commits are not the newest 3: %s" % commits
    assert [m for m in pack(st, BRIEF % "A")["mentions"] if m["source"] == "brief"] == [], "a brief named itself"


def check_build_sha_threaded(repo, st, ids, tmp):
    """AF-AP-175: every read names the commit the build was given, never HEAD."""
    ledger = (repo / LEDGER).read_text(encoding="utf-8")
    later = commit(repo, {LEDGER: ledger + "a later line naming scripts/beta.py\n"}, "a later ledger", 9)
    fp = load(repo)
    rec = fp.build(repo, st, sha=ids["fourth"])
    assert rec["commit"] == ids["fourth"]
    assert "ledger" not in pack(st, "scripts/beta.py")["counts"], \
        "the build read a source at HEAD, not at the commit it was given"
    rec = fp.build(repo, st)
    assert rec["commit"] == later and pack(st, "scripts/beta.py")["counts"]["ledger"] == 1, "the control: HEAD"


def check_build_removes(repo, st, ids, tmp):
    build(repo, st)
    pdir = st / "filepacks"
    assert (pdir / "scripts" / "gamma.py.json").is_file()
    (pdir / "stray.json").write_text("{}")
    (pdir / "scripts" / "beta.py.json.4242.tmp").write_text("{}")
    git(repo, "rm", "-q", "scripts/gamma.py", k=9)
    git(repo, "commit", "-q", "-m", "gamma removed", k=9)
    out = build(repo, st)
    assert not (pdir / "scripts" / "gamma.py.json").exists(), "a pack whose file has nothing any more was kept"
    assert not (pdir / "stray.json").exists() and not list(pdir.rglob("*.tmp"))
    assert "(0 written, 2 removed, 0 failed)" in out, out


def check_build_meta(repo, st, ids, tmp):
    build(repo, st)
    pdir = st / "filepacks"
    assert not list(pdir.rglob("*.tmp")), "a temp file was left"
    b = json.loads((pdir / "BUILD.json").read_text())
    tracked = git(repo, "ls-tree", "-r", "--name-only", "HEAD").split("\n")[:-1]
    assert (b["schema"], b["commit"], b["tracked"], b["files"]) == (1, ids["fourth"], len(tracked), 12), b
    assert b["missing"] == [".claude/skills/%s/SKILL.md" % s for s in SKILLS if s != "env-tool-quirks"], b
    assert isinstance(b["ms"], int) and b["ms"] >= 0
    assert (pdir / "TRACKED.txt").read_text() == "\n" + "\n".join(tracked) + "\n"
    packs = sorted(p.relative_to(pdir).as_posix()[:-5] for p in pdir.rglob("*.json") if p != pdir / "BUILD.json")
    assert packs == sorted(tracked), packs
    snap = {p: p.read_bytes() for p in pdir.rglob("*.json") if p != pdir / "BUILD.json"}
    assert "(0 written, 0 removed, 0 failed)" in build(repo, st), "a second build rewrote a pack"
    assert {p: p.read_bytes() for p in pdir.rglob("*.json") if p != pdir / "BUILD.json"} == snap


def check_budget_cut(repo, st, ids, tmp):
    build(repo, st)
    fp = load(repo)
    packs = fp.Packs(repo, st)
    full = fp.entry("docs/NOTE.md", {}, 10 ** 6, packs=packs)["text"].split("\n")
    sizes = [len(x.encode("utf-8")) for x in full]
    assert len(full) == 6 and any(s > len(x) for s, x in zip(sizes, full)), "the fixture lines are not multi-byte"
    for budget in range(sum(sizes) + len(sizes) + 1):
        e = fp.entry("docs/NOTE.md", {}, budget, packs=packs)
        got = e["text"].split("\n") if e["text"] else []
        assert got == full[:len(got)], "the cut is not on a line boundary (budget %d)" % budget
        assert len(e["text"].encode("utf-8")) <= budget, "over budget (budget %d)" % budget
        fits = max(k for k in range(len(full) + 1) if sum(sizes[:k]) + max(0, k - 1) <= budget)
        assert len(got) == fits, "the cut kept %d lines where %d fit (budget %d)" % (len(got), fits, budget)


def check_older_p2_stale_code(repo, st, ids, tmp):
    build(repo, st)
    alpha = (repo / "scripts" / "alpha.py").read_text()
    commit(repo, {LEDGER: (repo / LEDGER).read_text() + "a newer line naming scripts/alpha.py\n",
                  "scripts/alpha.py": alpha + "# rev 5\n"}, "a commit after the build", 9)
    lines = context(run(repo, st, read(repo, "scripts/alpha.py"))).split("\n")
    assert any(x.startswith("filepack scripts/alpha.py @%s: ledger 5 · " % ids["fourth"][:7]) for x in lines), \
        "the P2 pack built at an older commit was not read: %s" % lines
    assert lines[1].startswith("STALE: the file changed since this pack was built"), "a stale code pack passed as fresh"
    fp = load(repo)
    packs = fp.Packs(repo, st)
    whole = fp.entry("scripts/alpha.py", {}, 10 ** 6, packs=packs)
    assert whole["stale"] is True and whole["code"] == "file"
    e = fp.entry("scripts/alpha.py", {}, len(whole["text"].split("\n")[0].encode("utf-8")), packs=packs)
    assert e["text"] == "", "a stale code part went out without its STALE mark"
    plant_code_pack(repo, "scripts/beta.py", ids["fourth"])        # its one symbol's name holds the word STALE
    (repo / "scripts" / "beta.py").write_text("def STALE_beta():\n    return 3\n", encoding="utf-8")
    b = fp.entry("scripts/beta.py", {"old_string": "    return 3"}, 10 ** 6, packs=packs)
    head = b["text"].split("\n")[0]
    assert b["stale"] is True and head.startswith("codemap scripts/beta.py:2 — function STALE_beta L1-2"), head
    e = fp.entry("scripts/beta.py", {"old_string": "    return 3"}, len(head.encode("utf-8")), packs=packs)
    assert e["text"] == "", "a stale code part went out without its STALE mark (the word in a symbol's name)"


def check_corrupt(repo, st, ids, tmp):
    build(repo, st)
    (st / "filepacks" / "docs" / "NOTE.md.json").write_text("{not json", encoding="utf-8")
    ctx = context(run(repo, st, bash(repo, "cat docs/NOTE.md scripts/alpha.py")))
    assert ctx.startswith("codemap scripts/alpha.py — ") and "filepack docs/NOTE.md" not in ctx, ctx[:120]
    assert {"key": "file:docs/NOTE.md", "why": "corrupt"} in records(st)[-1]["skipped"], \
        "a corrupt pack was not logged as corrupt: %s" % records(st)[-1]["skipped"]
    (repo / ".jev" / "codemap" / "scripts" / "alpha.py.json").write_text("[1, 2", encoding="utf-8")
    ctx = context(run(repo, st, read(repo, "scripts/alpha.py", sid="w2")))
    assert ctx == "", "a corrupt code pack still gave the file's entry: %r" % ctx[:120]
    assert records(st)[-1]["skipped"] == [{"key": "file:scripts/alpha.py", "why": "corrupt"}], records(st)[-1]


def check_missing_state(repo, st, ids, tmp):
    assert not st.exists()
    r = run(repo, st, read(repo, "docs/NOTE.md"))
    assert (r.returncode, r.stdout, r.stderr) == (0, b"", b""), r
    assert not st.exists(), "the hook created the state directory before any build"
    build(repo, st)
    assert context(run(repo, st, read(repo, "docs/NOTE.md"))), "the control: built, the same call injects"


def check_lock_held(repo, st, ids, tmp):
    build(repo, st)
    seen = st / "filepacks-seen"
    seen.mkdir()
    fd = os.open(seen / ("%s.main.json.lock" % SID), os.O_WRONLY | os.O_CREAT, 0o600)
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        r = run(repo, st, read(repo, "docs/NOTE.md"))
        assert (r.returncode, r.stdout) == (0, b""), "a held lock still injected"
        rec = records(st)[-1]
        assert (rec["error"], rec["window"], rec["tool"]) == ("WindowLockTimeout", "%s.main" % SID, "Read"), rec
        assert not (seen / ("%s.main.json" % SID)).exists()
    finally:
        os.close(fd)
    assert context(run(repo, st, read(repo, "docs/NOTE.md"))), "the control: the lock free, the same call injects"


def check_empty_fields(repo, st, ids, tmp):
    build(repo, st)
    before = len(records(st))
    for data in (b"", b"null", b"[1, 2]", json.dumps({"hook_event_name": "Stop"}).encode(),
                 payload(repo, "Read", {}), payload(repo, "Read", {"file_path": ""}),
                 payload(repo, "Read", {"file_path": 7}), payload(repo, "Edit", {"old_string": "x"}),
                 payload(repo, "Bash", {"command": ""}), payload(repo, "Bash", {"command": "   "}),
                 payload(repo, "Bash", {}), payload(repo, "Read", "not an object"),
                 payload(repo, "Bash", ["cat", "docs/NOTE.md"]), payload(repo, "Write", None),
                 payload(repo, "Read", {"file_path": str(repo / "docs")})):
        r = run(repo, st, data)
        assert (r.returncode, r.stdout) == (0, b""), (data, r.stdout, r.stderr)
    assert records(st)[before:] == [], "an empty or missing field was logged as an error: %s" % records(st)[before:]
    r = run(repo, st, b"not json")
    assert (r.returncode, r.stdout) == (0, b"") and records(st)[-1]["error"] == "JSONDecodeError"
    assert context(run(repo, st, read(repo, "docs/NOTE.md"))), "the control: a whole payload injects"


def check_untracked(repo, st, ids, tmp):
    build(repo, st)
    (repo / "scripts" / "untracked.py").write_text("def u():\n    return 1\n", encoding="utf-8")
    p2 = dict(pack(st, "scripts/beta.py"), path="scripts/untracked.py")
    (st / "filepacks" / "scripts" / "untracked.py.json").write_text(json.dumps(p2), encoding="utf-8")
    plant_code_pack(repo, "scripts/untracked.py", "0" * 40)
    for k, p in enumerate([read(repo, "scripts/untracked.py"), bash(repo, "cat scripts/untracked.py"),
                           edit(repo, "scripts/untracked.py", "    return 1")]):
        p["session_id"] = "u%d" % k
        assert context(run(repo, st, p)) == "", "an untracked file was injected"
    assert context(run(repo, st, read(repo, "scripts/beta.py", sid="uc"))), "the control: a tracked file injects"


def check_outside_root(repo, st, ids, tmp):
    build(repo, st)
    assert context(run(repo, st, read(repo, "docs/NOTE.md", sid="ctl"))), "the control"
    cases = [(payload(repo, "Read", {"file_path": "/etc/passwd"}), "a path outside the root was injected"),
             (bash(repo, "cat /etc/passwd"), "a path outside the root was injected"),
             (payload(repo, "Read", {"file_path": "%s/../x" % repo}), "a path with a .. component was injected"),
             (bash(repo, "cat ../x"), "a path with a .. component was injected"),
             (payload(repo, "Read", {"file_path": "%s/scripts/../scripts/alpha.py" % repo}),
              "a path with a .. component was injected"),
             (bash(repo, "cat scripts/../docs/NOTE.md"), "a path with a .. component was injected"),
             (payload(repo, "Read", {"file_path": "%sXscripts/alpha.py" % repo}),
              "a path beside the root resolved inside it")]
    for k, (p, why) in enumerate(cases):
        p["session_id"] = "o%d" % k
        assert context(run(repo, st, p)) == "", why


def check_links(repo, st, ids, tmp):
    build(repo, st)
    pdir, away = st / "filepacks", tmp / "away"
    away.mkdir()
    note = pdir / "docs" / "NOTE.md.json"
    shutil.copy2(note, away / "NOTE.md.json")
    note.unlink()
    note.symlink_to(away / "NOTE.md.json")
    assert context(run(repo, st, read(repo, "docs/NOTE.md", sid="l1"))) == "", "a linked pack was read"
    assert records(st)[-1]["skipped"] == [{"key": "file:docs/NOTE.md", "why": "link"}], records(st)[-1]
    code = repo / ".jev" / "codemap" / "scripts" / "alpha.py.json"
    shutil.copy2(code, away / "alpha.py.json")
    code.unlink()
    code.symlink_to(away / "alpha.py.json")
    assert context(run(repo, st, read(repo, "scripts/alpha.py", sid="l2"))) == "", "a linked code pack was read"
    assert records(st)[-1]["skipped"] == [{"key": "file:scripts/alpha.py", "why": "link"}], records(st)[-1]
    os.rename(pdir / "scripts", away / "scripts")
    (pdir / "scripts").symlink_to(away / "scripts")
    assert context(run(repo, st, read(repo, "scripts/beta.py", sid="l3"))) == "", \
        "a pack under a linked directory was read"
    assert records(st)[-1]["skipped"] == [{"key": "file:scripts/beta.py", "why": "link"}], records(st)[-1]
    assert context(run(repo, st, read(repo, LEDGER, sid="l4"))), "the control: a regular pack is read"


def check_data_words(repo, st, ids, tmp):
    build(repo, st)
    for k, cmd in enumerate(['echo "cat scripts/alpha.py"',
                             "cat > /tmp/k2-never-written <<'EOF'\nsed -n 1p scripts/alpha.py\nEOF",
                             "git add scripts/alpha.py", "ls  # ; cat scripts/alpha.py",
                             "python3 scripts/alpha.py", "git commit -m 'cat scripts/alpha.py'",
                             "grep -n x <<< 'scripts/alpha.py'", "wc -l < /dev/null > scripts/alpha.py"]):
        assert context(run(repo, st, bash(repo, cmd, sid="d%d" % k))) == "", "a data word injected: %r" % cmd
    assert context(run(repo, st, bash(repo, "cat scripts/alpha.py", sid="dc"))), "the control: a real reader"


def check_call_and_window_max(repo, st, ids, tmp):
    build(repo, st)
    ctx = context(run(repo, st, bash(repo, "cat docs/NOTE.md scripts/beta.py scripts/gamma.py")))
    assert [x.split(" @")[0] for x in ctx.split("\n") if x.startswith("filepack ")] == [
        "filepack docs/NOTE.md", "filepack scripts/beta.py"], "more than two files in one call, or others: %r" % ctx
    assert records(st)[-1]["skipped"] == [{"key": "file:scripts/gamma.py", "why": "call-max"}]
    seen = st / "filepacks-seen"
    for sid, n in (("w64", 64), ("w63", 63)):
        (seen / ("%s.main.json" % sid)).write_text(json.dumps({"keys": ["file:x%d" % i for i in range(n)]}))
    assert context(run(repo, st, read(repo, "docs/NOTE.md", sid="w64"))) == "", "a 65th file in a window was injected"
    assert records(st)[-1]["skipped"] == [{"key": "file:docs/NOTE.md", "why": "window-max"}]
    assert context(run(repo, st, read(repo, "docs/NOTE.md", sid="w63"))), "the control: the 64th file injects"


def check_kill_switch(repo, st, ids, tmp):
    build(repo, st)
    off = st / "filepacks-off"
    off.write_text("")
    n = len(records(st))
    r = run(repo, st, read(repo, "docs/NOTE.md"))
    assert (r.returncode, r.stdout, r.stderr, len(records(st))) == (0, b"", b"", n), "the off switch did not hold"
    r = run(repo, st, start("compact"), cmd=REG_RESET)
    assert r.returncode == 0 and records(st)[-1]["event"] == "SessionStart", "the reset did not run with it off"
    off.unlink()
    off.symlink_to(st / "nowhere")
    r = run(repo, st, read(repo, "docs/NOTE.md"))
    assert (r.returncode, r.stdout) == (0, b""), "a dangling link named filepacks-off did not switch it off"
    off.unlink()
    assert context(run(repo, st, read(repo, "docs/NOTE.md"))), "the control: on again"


def check_no_input_in_state(repo, st, ids, tmp):
    build(repo, st)
    canary = "cnry" + secrets.token_hex(8)
    calls = [edit(repo, "scripts/alpha.py", "    return x + 1", new=canary),
             write(repo, "docs/NOTE.md", content=canary + "\n", sid="c2"),
             bash(repo, "cat scripts/beta.py  # %s" % canary, sid="c3"),
             bash(repo, "grep -n %s scripts/gamma.py" % canary, sid="c4"),
             payload(repo, "Read", {"file_path": "%s/scripts/%s.py" % (repo, canary)}, sid="c5")]
    outs = [run(repo, st, p) for p in calls]
    assert [bool(context(r)) for r in outs] == [True, True, True, True, False], "the canaries rode no real work"
    for p in st.rglob("*"):
        if p.is_file():
            data = p.read_bytes()
            assert canary.encode() not in data and canary[4:].encode() not in data, \
                "the tool input reached a state file: %s" % p.name


def check_no_pyc_in_claude(repo, st, ids, tmp):
    build(repo, st)
    assert context(run(repo, st, bash(repo, "cat scripts/alpha.py")))
    files = sorted(p.relative_to(repo).as_posix() for p in (repo / ".claude").rglob("*") if p.is_file())
    assert files == [".claude/hooks/system1-context.py", SKILL], "a bytecode cache was written under .claude: %s" % files
    assert list((st / "pycache").rglob("system1-context.*.pyc")), "the bytecode cache went nowhere"


def check_replay(repo, st, ids, tmp):
    build(repo, st)

    def call(name, ti, **extra):
        return dict({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": ti}]}},
                    **extra)
    recs = [call("Read", {"file_path": "%s/docs/NOTE.md" % repo}),
            call("Read", {"file_path": "%s/scripts/beta.py" % repo}, isSidechain=True),
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "cat scripts/alpha.py"},
                                                          {"type": "tool_use", "name": "Bash", "input": {
                                                              "command": "cat docs/NOTE.md scripts/gamma.py"}}]}},
            {"type": "system", "subtype": "compact_boundary"},
            call("Read", {"file_path": "%s/docs/NOTE.md" % repo}),
            call("Read", {"file_path": "%s/scripts/beta.py" % repo})]
    raw = "".join(json.dumps(r) + "\n" for r in recs)
    tr = tmp / "transcript.jsonl"
    tr.write_text(raw, encoding="utf-8")
    r = subprocess.run(["python3", str(repo / "scripts" / "filepacks.py"), "replay", "--transcript", str(tr),
                        "--bytes", str(len(raw) - 10)], env=env_for(repo, st), capture_output=True, text=True,
                       timeout=120, cwd="/")
    assert r.returncode == 0, r.stderr
    out = r.stdout.splitlines()
    assert [x.rsplit(" bytes ", 1)[0] for x in out[:2]] == ["window 0: calls 2 injections 2",
                                                           "window 1: calls 1 injections 1"], \
        "the replay counted a subagent's call or a cut line: %s" % out[:2]
    rx = re.compile(r"window \d+: calls \d+ injections \d+ bytes \d+|(injections|bytes) per window: median \S+ p90 "
                    r"\d+ max \d+ \(windows \d+\)|entry ms: p50 [\d.]+ p95 [\d.]+ max [\d.]+ over \d+ entries")
    assert all(rx.fullmatch(x) for x in out) and len(out) == 5, "the replay printed more than counts: %s" % out


CHECKS = {"edit-once-per-symbol": check_edit_once_per_symbol, "read-range": check_read_range,
          "bash-readers": check_bash_readers, "reset": check_reset, "doc-pack-lines": check_doc_pack_lines,
          "build-lines": check_build_lines, "build-briefs-commits": check_build_briefs_commits,
          "build-sha-threaded": check_build_sha_threaded, "build-removes": check_build_removes,
          "build-meta": check_build_meta, "budget-cut": check_budget_cut,
          "older-p2-stale-code": check_older_p2_stale_code, "corrupt": check_corrupt,
          "missing-state": check_missing_state, "lock-held": check_lock_held, "empty-fields": check_empty_fields,
          "untracked": check_untracked, "outside-root": check_outside_root, "links": check_links,
          "data-words": check_data_words, "call-and-window-max": check_call_and_window_max,
          "kill-switch": check_kill_switch, "no-input-in-state": check_no_input_in_state,
          "no-pyc-in-claude": check_no_pyc_in_claude, "replay": check_replay}
# one mutation per property: (the check it must fail, old text, new text, the failure it must fail with)
MUTANTS = {
    "edit-key-per-file": ("edit-once-per-symbol",
                          'key = "sym:%s:%s" % (rel, e["symbol"]) if tool == "Edit" and e["symbol"] else fkey',
                          "key = fkey", "an Edit of another symbol injected nothing"),
    "no-seen": ("edit-once-per-symbol", "    taken = set(seen)\n", "    taken = set()\n",
                "a second Edit of the same symbol injected again"),
    "range-ignored": ("read-range", "if type(off) is int and type(lim) is int and off >= 0 and lim >= 1:", "if False:",
                      "a Read range did not show the symbols in range"),
    "no-sed": ("bash-readers", '"cat", "head", "tail", "sed", ', '"cat", "head", "tail", ',
               "sed -n 1,40p did not inject the file"),
    "no-cd": ("bash-readers", "            cwd = _cd(words, cwd)\n", "            pass\n", "a cd was not followed"),
    "reset-noop": ("reset", "            if hit or now - os.lstat(path).st_mtime > sys1.MARKER_MAX_AGE_S:",
                   "            if False:", "a compact reset did not re-arm the window"),
    "doc-without-pack-lines": ("doc-pack-lines", "e = entry(rel, ti, budget, packs=packs, p2=fkey not in taken)",
                               "e = entry(rel, ti, budget, packs=packs, p2=False)",
                               "a tracked document got no pack lines"),
    "suffix-match": ("build-lines", 'for t in (tok, tok.rstrip(".")):',
                     'for t in (tok, tok.rstrip("."), tok.split("/", 1)[-1]):',
                     "the ledger mentions are not the newest 3 on a whole-path boundary"),
    "extension-strip": ("build-lines", 'for t in (tok, tok.rstrip(".")):',
                        'for t in (tok, tok.rstrip("."), tok.rsplit(".", 1)[0]):',
                        "the ledger mentions are not the newest 3 on a whole-path boundary"),
    "oldest-lines-first": ("build-lines", "for i in range(len(lines) - 1, -1, -1):", "for i in range(len(lines)):",
                           "the ledger mentions are not the newest 3 on a whole-path boundary"),
    "keep-all": ("build-lines", "KEEP = 3 ", "KEEP = 10 ",
                 "the ledger mentions are not the newest 3 on a whole-path boundary"),
    "no-registry-id": ("build-lines", r'REGISTRY_RX = re.compile(r"\|\s*(D-\d+|AF-AP-\d+)\s*\|")',
                       r'REGISTRY_RX = re.compile(r"(?!)(x)")', "a registry row lost its id"),
    "headline-uncapped": ("build-lines", 'rec["headline"] = _cut(h.group(1), HEADLINE)',
                          'rec["headline"] = _cut(h.group(1), 10 ** 6)', "a ledger headline is over 160 characters"),
    "snippet-at-line-start": ("build-lines", "a = max(0, min(pos - (SNIPPET - n) // 2, len(line) - SNIPPET))",
                              "a = 0", "the snippet is not around the first mention"),
    "briefs-oldest-first": ("build-briefs-commits", "for h, d, _, names in _log(root, sha, path=BRIEFS):",
                            "for h, d, _, names in reversed(_log(root, sha, path=BRIEFS)):",
                            "the briefs are not the newest 3 by their last commit"),
    "commits-oldest-first": ("build-briefs-commits", "for h, d, subj, names in _log(root, sha, limit=COMMITS):",
                             "for h, d, subj, names in reversed(_log(root, sha, limit=COMMITS)):",
                             "the commits are not the newest 3"),
    "reads-at-head": ("build-sha-threaded", "texts = _blobs(root, sha, ", 'texts = _blobs(root, "HEAD", ',
                      "the build read a source at HEAD"),
    "keeps-stale-packs": ("build-removes", "removed = _clean(pdir, set(packs))", "removed = 0",
                          "a pack whose file has nothing any more was kept"),
    "temp-left": ("build-meta", "        os.replace(tmp, path)\n    except BaseException:",
                  "        open(path, 'wb').write(open(tmp, 'rb').read())\n    except BaseException:",
                  "a temp file was left"),
    "rewrites-every-pack": ("build-meta", "            if sys1.read_regular(path) == raw:\n                continue\n",
                            "            pass\n", "a second build rewrote a pack"),
    "cut-mid-line": ("budget-cut", "        if used + cost > budget:\n            break",
                     "        if used + cost > budget:\n            kept.append(ln[:max(0, budget - used - 1)])\n"
                     "            break", "the cut is not on a line boundary"),
    "chars-not-bytes": ("budget-cut", 'cost = len(ln.encode("utf-8")) + (1 if kept else 0)',
                        "cost = len(ln) + (1 if kept else 0)", "over budget"),
    "stale-passes": ("older-p2-stale-code", "if stale and not any(STALE_MARK in ln for ln in kept):", "if False:",
                     "a stale code part went out without its STALE mark"),
    "stale-word-only": ("older-p2-stale-code", "if stale and not any(STALE_MARK in ln for ln in kept):",
                        'if stale and not any("STALE" in ln for ln in kept):',
                        "a stale code part went out without its STALE mark (the word in a symbol's name)"),
    "corrupt-code-pack-ignored": ("corrupt", 'raise PackError("corrupt" if os.path.lexists(pack) else "gone")',
                                  'return None, "", None, None', "a corrupt code pack still gave the file's entry"),
    "corrupt-as-no-pack": ("corrupt", "        return dict(res, error=e.why)", "        return dict(res, error=None)",
                           "a corrupt pack was not logged as corrupt"),
    "state-created": ("missing-state", 'sys1 = s1(state / "pycache" if state.is_dir() else None)',
                      'sys1 = s1(state / "pycache")', "the hook created the state directory"),
    "no-lock": ("lock-held", "            with sys1.WindowLock(marker):", "            with open(os.devnull):",
                "a held lock still injected"),
    "no-dict-check": ("empty-fields", "    if not isinstance(ti, dict):\n        return []\n    if tool in",
                      "    if tool in", "an empty or missing field was logged as an error"),
    "untracked-allowed": ("untracked", "if packs.tracked(r)]", "if True]", "an untracked file was injected"),
    "dotdot-allowed": ("outside-root", ' or ".." in path.split("/"):', ":", "a path with a .. component was injected"),
    "root-prefix-without-slash": ("outside-root",
                                  'return norm[len(base) + 1:] if norm.startswith(base + "/") else None',
                                  "return norm[len(base) + 1:] if norm.startswith(base) else None",
                                  "a path beside the root resolved inside it"),
    "linked-parent-followed": ("links", "    return d == b or d.startswith(b + os.sep)", "    return True",
                               "a pack under a linked directory was read"),
    "data-words-read": ("data-words", "    code = sys1.shell_code(cmd)", "    code = cmd", "a data word injected"),
    "call-max-3": ("call-and-window-max", "CALL_MAX = 2 ", "CALL_MAX = 3 ", "more than two files in one call"),
    "window-max-off": ("call-and-window-max", "PACK_WINDOW_MAX = 64 ", "PACK_WINDOW_MAX = 10 ** 6 ",
                       "a 65th file in a window was injected"),
    "off-switch-file-only": ("kill-switch", 'os.path.lexists(state / "filepacks-off")',
                             'os.path.isfile(state / "filepacks-off")',
                             "a dangling link named filepacks-off did not switch it off"),
    "input-logged": ("no-input-in-state", '"injected": [], "skipped": [], "bytes": 0}',
                     '"injected": [], "skipped": [], "bytes": 0, "input": ti}', "the tool input reached a state file"),
    "pyc-beside-hook": ("no-pyc-in-claude", "            sys.pycache_prefix = str(cache)", "            pass",
                        "a bytecode cache was written under .claude"),
    "sidechain-counted": ("replay", 'if rec.get("type") != "assistant" or rec.get("isSidechain") or',
                          'if rec.get("type") != "assistant" or', "the replay counted a subagent's call"),
}


def mutant(name):
    """The text of filepacks.py with mutant `name` applied: its anchor must occur exactly once, and the result must
    compile (a mutant that does not compile would fail every check for the wrong reason: INVALID, never a kill)."""
    _, old, new, _ = MUTANTS[name]
    text = FILEPACKS.read_text(encoding="utf-8")
    assert text.count(old) == 1, "INVALID %s: the anchor occurs %d times" % (name, text.count(old))
    out = text.replace(old, new)
    compile(out, "filepacks-%s.py" % name, "exec")
    return out


@pytest.mark.parametrize("name", sorted(CHECKS))
def test_check_passes_on_the_real_filepacks(tmp_path, name):
    repo, ids = fixture(tmp_path)
    CHECKS[name](repo, tmp_path / "state", ids, tmp_path)


@pytest.mark.parametrize("name", sorted(MUTANTS))
def test_negative_control_the_same_check_fails_on_a_mutant(tmp_path, name):
    check, _, _, why = MUTANTS[name]
    repo, ids = fixture(tmp_path, fp_text=mutant(name))
    assert (repo / "scripts" / "filepacks.py").read_text(encoding="utf-8") == mutant(name)   # the mutant is what runs
    with pytest.raises(AssertionError, match=re.escape(why)):
        CHECKS[check](repo, tmp_path / "state", ids, tmp_path)


def test_every_check_has_a_mutant_and_every_mutant_compiles():
    assert set(CHECKS) == {m[0] for m in MUTANTS.values()}, "a property has no mutant, or a mutant no check"
    for name in MUTANTS:
        mutant(name)


# ---------- the registration, the code pack's fields, the speed ----------

def test_the_installer_spelling_reaches_the_model_form(tmp_path):
    """The /home/user-rooted session's commands (scripts/install_session_hooks.py spells them with the root, a guard
    and a cd): with no CLAUDE_PROJECT_DIR they reach the model form, and the reset runs."""
    import shlex
    repo, _ = fixture(tmp_path)
    st = tmp_path / "state"
    build(repo, st)
    r = shlex.quote(str(repo))
    pre = ("[ -f %s/scripts/filepacks.py ] && [ -f %s/scripts/hook_context.py ] || exit 0; cd %s || exit 0; "
           "python3 %s/scripts/hook_context.py PreToolUse -- python3 %s/scripts/filepacks.py hook" % (r, r, r, r, r))
    reset = "[ -f %s/scripts/filepacks.py ] || exit 0; cd %s || exit 0; python3 %s/scripts/filepacks.py hook --reset" % (
        r, r, r)
    env = env_for(repo, st)
    env.pop("CLAUDE_PROJECT_DIR")
    out = subprocess.run(["sh", "-c", pre], input=json.dumps(read(repo, "docs/NOTE.md")).encode(),
                         capture_output=True, timeout=60, env=env, cwd="/")
    assert context(out).startswith("filepack docs/NOTE.md @")
    out = subprocess.run(["sh", "-c", reset], input=json.dumps(start("compact")).encode(), capture_output=True,
                         timeout=60, env=env, cwd="/")
    assert (out.returncode, out.stdout) == (0, b"") and records(st)[-1] == dict(records(st)[-1], event="SessionStart",
                                                                                source="compact", removed=1)


def test_the_planted_code_pack_has_the_real_builders_fields(tmp_path):
    """Drift guard: the real codemap builder (build_one, its graphs absent) writes a pack with the same fields and
    instrument sections as the planted one, so the checks read the format the builder writes."""
    repo, ids = fixture(tmp_path)
    planted = json.loads((repo / ".jev" / "codemap" / "scripts" / "alpha.py.json").read_text())
    spec = importlib.util.spec_from_file_location("codemap_k2_drift", repo / "scripts" / "codemap.py")
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)
    outcome, real = cm.build_one(repo, "scripts/alpha.py", ("absent", "not in this test"), {"PATH": "/usr/bin:/bin"},
                                 ids["fourth"])
    assert outcome == "built" and set(real) == set(planted) and set(real["instruments"]) == set(planted["instruments"])
    assert (real["blob"], real["lines"], real["schema"]) == (planted["blob"], planted["lines"], planted["schema"])


def test_the_entry_stays_fast(tmp_path):
    """A guard, not a control: warm, one entry reads two packs in a few milliseconds (the replay measures the real
    tree's p50 and p95); the bound here is 50 ms, the best of five."""
    repo, _ = fixture(tmp_path)
    st = tmp_path / "state"
    build(repo, st)
    fp = load(repo)
    packs = fp.Packs(repo, st)
    for ti in ({"old_string": "    return x + 1"}, {"offset": 4, "limit": 8}, {}):
        fp.entry("scripts/alpha.py", ti, packs=packs)
        ts = []
        for _ in range(5):
            t0 = time.perf_counter()
            fp.entry("scripts/alpha.py", ti, packs=packs)
            ts.append(time.perf_counter() - t0)
        assert min(ts) < 0.05, (ti, ts)
