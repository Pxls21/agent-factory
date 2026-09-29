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

Round 2 (VERIFY-K2): F1, a file untracked since the last build whose code pack was rebuilt from the working copy with a
canary, runs three ways: with no build after the untracking commit (check untracked-since-build), with the post-commit
patch applied to the real hook by `git apply` (its build alone keeps the file out), and with the REAL L2a refresh
building the pack after a graft re-index (the verifier's probe_p6.py; skipped loudly where graft is absent). The
verifier's seventeen F14 checks are here under their names, and the parser's F3, F4 and F5 shapes (the wrong files, the
nested scripts, the remote commands, a 3,000-pair command's time). `run` kills a stalled hook and fails as a stall.

Round 3 (VERIFY-K2 round 2): B1, a caller or test in an untracked file named in a tracked file's code part, runs on
planted packs (untracked-callers, same-file-stale, caller-path-newline) and through the REAL patched post-commit hook
with graft, GitNexus and code-review-graph (the verifier's probe_callers2.py; skipped loudly without them). B2, a pack
whose symbols come from a graph that had not indexed its bytes, runs on planted packs (stale-symbol-graph,
sourceless-symbols) and through the REAL refresh in both of the verifier's shapes (an untracked file, a reverted edit).
B3: `hook_dir` applies the post-commit patch only to a hook that does not carry it, and the negative control's hook
comes from UNPATCHED_AT, so this file passes before the patch lands and after. The verifier's seven checks that killed
mutants the round-2 checks missed are here under their names.
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
import signal
import subprocess
import tempfile
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


def run(repo, st, data, cmd=REG_PRE, timeout=60, env=None):
    """The hook through a shell, as the harness runs it. A run past `timeout` is killed with its process group and
    fails as a stall (the verifier's bound, VERIFY-K2 F2), never as a hung test."""
    data = data if isinstance(data, bytes) else json.dumps(data).encode()
    p = subprocess.Popen(["sh", "-c", cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=env or env_for(repo, st), cwd="/", start_new_session=True)
    try:
        out, err = p.communicate(data, timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.communicate()
        raise AssertionError("the hook stalled past %d s" % timeout) from None
    return subprocess.CompletedProcess(p.args, p.returncode, out, err)


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


# ---------- round 2: VERIFY-K2 F1 (a stale boundary), F2 (a FIFO), F3 (a linear parse), F4 and F5 (the right file) ----

def heads(ctx):
    """The files whose pack lines an injected text holds, in order."""
    return [x.split(" @")[0][len("filepack "):] for x in ctx.split("\n") if x.startswith("filepack ")]


def untrack_with_a_canary(repo, st, build_first=True):
    """The verifier's P6 (VERIFY-K2 F1): a build lists scripts/gamma.py; a later commit untracks it, the file stays on
    disk and no build follows; a canary goes into the file, and its code pack is rebuilt from the working copy (in
    codemap.py's format, the symbols from the file's AST, as the L2a refresh builds a pack). Returns the canary."""
    if build_first:
        build(repo, st)
    git(repo, "rm", "-q", "--cached", "scripts/gamma.py", k=9)
    git(repo, "commit", "-q", "-m", "gamma untracked", k=9)
    canary = "cnry" + secrets.token_hex(6)
    (repo / "scripts" / "gamma.py").write_text('def leak_%s(token="%s-arg"):\n    return token\n' % (canary, canary),
                                                encoding="utf-8")
    plant_code_pack(repo, "scripts/gamma.py", git(repo, "rev-parse", "HEAD").strip())
    return canary


def gamma_probes(repo, sid):
    return [edit(repo, "scripts/gamma.py", "    return token", sid=sid + "e"), read(repo, "scripts/gamma.py", sid=sid + "r"),
            bash(repo, "cat scripts/gamma.py", sid=sid + "b")]


def check_untracked_since_build(repo, st, ids, tmp):
    canary = untrack_with_a_canary(repo, st)
    assert "\nscripts/gamma.py\n" in (st / "filepacks" / "TRACKED.txt").read_text(), "not F1's stale boundary"
    assert canary in (repo / ".jev" / "codemap" / "scripts" / "gamma.py.json").read_text(), "no canary in the pack"
    for p in gamma_probes(repo, "p6"):
        ctx = context(run(repo, st, p))
        assert canary not in ctx and canary[4:] not in ctx, "the untracked file's text reached the model"
        assert heads(ctx) == ["scripts/gamma.py"] and ctx.startswith("filepack scripts/gamma.py @"), \
            "the pack's lines were not shown alone: %r" % ctx[:80]
        assert records(st)[-1]["injected"][0].get("code_skip") == "blob", records(st)[-1]["injected"]


def check_blobs_exact_path(repo, st, ids, tmp):
    """A code part is checked against its own file's blob: another tracked file whose path ends with this one's (and
    sorts before it in BLOBS.txt) is never read in its place."""
    commit(repo, {"harness-ports/scripts/alpha.py": "def other():\n    return 0\n"}, "a path ending like alpha's", 9)
    build(repo, st)
    blobs = (st / "filepacks" / "BLOBS.txt").read_text()
    tree = [(x.split("\t", 1)[1], x.split()[2]) for x in git(repo, "ls-tree", "-r", "HEAD").splitlines()]
    assert blobs == "\n" + "".join("%s\t%s\n" % t for t in tree), "BLOBS.txt is not git's blob ids at the build"
    lines = blobs.split("\n")
    assert lines.index("harness-ports/scripts/alpha.py\t" + git(repo, "rev-parse", "HEAD:harness-ports/scripts/alpha.py"
                                                                ).strip()) < lines.index(
        "scripts/alpha.py\t" + git(repo, "rev-parse", "HEAD:scripts/alpha.py").strip()), "BLOBS.txt is not as built"
    ctx = context(run(repo, st, read(repo, "scripts/alpha.py")))
    assert ctx.startswith("codemap scripts/alpha.py — "), "a code pack was checked against another file's blob: %r" % (
        ctx[:80])


def check_fifo_working_file(repo, st, ids, tmp):
    plant_code_pack(repo, "scripts/beta.py", ids["fourth"])
    build(repo, st)
    os.unlink(repo / "scripts" / "beta.py")
    os.mkfifo(repo / "scripts" / "beta.py")
    t0 = time.monotonic()
    ctx = context(run(repo, st, read(repo, "scripts/beta.py"), timeout=15))
    assert time.monotonic() - t0 < 10 and ctx.startswith("filepack scripts/beta.py @"), "a FIFO working file: %r" % (
        ctx[:80])


def check_code_pack_parent_link(repo, st, ids, tmp):
    build(repo, st)
    cmd, away = repo / ".jev" / "codemap" / "scripts", tmp / "away-cm"
    shutil.copytree(cmd, away)
    shutil.rmtree(cmd)
    cmd.symlink_to(away)
    assert context(run(repo, st, read(repo, "scripts/alpha.py"))) == "", "a code pack under a linked directory was read"


def check_pack_path_field(repo, st, ids, tmp):
    build(repo, st)
    note = st / "filepacks" / "docs" / "NOTE.md.json"
    note.write_text(json.dumps(dict(json.loads(note.read_text()), path="scripts/beta.py")))
    assert context(run(repo, st, read(repo, "docs/NOTE.md", sid="pf"))) == "", "a pack naming another file was read"


def check_pack_schema(repo, st, ids, tmp):
    build(repo, st)
    note = st / "filepacks" / "docs" / "NOTE.md.json"
    note.write_text(json.dumps(dict(json.loads(note.read_text()), schema=2)))
    assert context(run(repo, st, read(repo, "docs/NOTE.md", sid="ps"))) == "", "a pack of another schema was read"


def check_root_untracked_suffix(repo, st, ids, tmp):
    build(repo, st)
    (repo / "alpha.py").write_text("def u():\n    return 1\n")
    (st / "filepacks" / "alpha.py.json").write_text(json.dumps(dict(pack(st, "scripts/beta.py"), path="alpha.py")))
    assert context(run(repo, st, read(repo, "alpha.py", sid="rs"))) == "", \
        "an untracked root file matched a tracked path's tail"


def check_window_max_two(repo, st, ids, tmp):
    build(repo, st)
    seen = st / "filepacks-seen"
    seen.mkdir(parents=True, exist_ok=True)
    (seen / "w63b.main.json").write_text(json.dumps({"keys": ["file:x%d" % i for i in range(63)]}))
    ctx = context(run(repo, st, bash(repo, "cat docs/NOTE.md scripts/beta.py", sid="w63b")))
    assert len(heads(ctx)) == 1, "a window at 63 files took two more in one call"


def check_cd_variable_dotdot(repo, st, ids, tmp):
    build(repo, st)
    assert context(run(repo, st, bash(repo, "cd $NOWHERE/.. && cat scripts/alpha.py", sid="cv"))) == "", \
        "a cd through an unset variable was followed"


def check_tilde(repo, st, ids, tmp):
    build(repo, st)
    env = dict(env_for(repo, st), HOME=str(repo.parent))
    assert "filepack docs/NOTE.md @" in context(run(repo, st, bash(repo, "cat ~/%s/docs/NOTE.md" % repo.name, sid="tl"),
                                                    env=env)), "a ~/ path was not expanded"


def check_replace_all(repo, st, ids, tmp):
    commit(repo, {"scripts/delta.py": "def twice():\n    x = 1\n    x = 1\n    return x\n"}, "delta", 9)
    plant_code_pack(repo, "scripts/delta.py", git(repo, "rev-parse", "HEAD").strip())
    build(repo, st)
    p = payload(repo, "Edit", {"file_path": "%s/scripts/delta.py" % repo, "old_string": "    x = 1\n", "new_string": "y",
                               "replace_all": True}, sid="ra")
    assert "function twice" in context(run(repo, st, p)), "a replace_all Edit was not placed in its symbol"


def check_offset_zero(repo, st, ids, tmp):
    build(repo, st)
    ctx = context(run(repo, st, read(repo, "scripts/alpha.py", sid="oz", offset=0, limit=5)))
    assert ctx.startswith("codemap scripts/alpha.py:1-5"), "a Read at offset 0 lost its entry: %r" % ctx[:60]


def check_log_rotation(repo, st, ids, tmp):
    build(repo, st)
    (st / "filepacks.jsonl").write_bytes(b"x" * 4_000_001)
    context(run(repo, st, read(repo, "docs/NOTE.md", sid="lr")))
    assert (st / "filepacks.jsonl.1").exists() and (st / "filepacks.jsonl").stat().st_size < 4_000_000, \
        "the log did not rotate"


def check_long_subject(repo, st, ids, tmp):
    commit(repo, {"scripts/gamma.py": "def gamma():\n    return 4\n"}, "S" * 300, 9)
    build(repo, st)
    subj = [m["subject"] for m in pack(st, "scripts/gamma.py")["mentions"] if m["source"] == "commit"][0]
    assert len(subj) == 240 and subj.endswith("…"), "a commit subject was not cut at 240 characters"


def check_age_prune(repo, st, ids, tmp):
    build(repo, st)
    context(run(repo, st, read(repo, "docs/NOTE.md", sid="old-session")))
    m = st / "filepacks-seen" / "old-session.main.json"
    old = time.time() - 8 * 86400
    os.utime(m, (old, old))
    run(repo, st, start("startup"), cmd=REG_RESET)
    assert not m.exists(), "a marker idle 8 days was not pruned"


def check_reset_no_state(repo, st, ids, tmp):
    r = run(repo, st, start("compact"), cmd=REG_RESET)
    assert r.returncode == 0 and not st.exists(), "a reset with no state created one"


def check_event_check(repo, st, ids, tmp):
    build(repo, st)
    p = dict(read(repo, "docs/NOTE.md", sid="ev"), hook_event_name="PostToolUse")
    assert context(run(repo, st, p)) == "", "a PostToolUse payload injected"


def check_dot_slash(repo, st, ids, tmp):
    led = (repo / LEDGER).read_text()
    commit(repo, {LEDGER: led + "a line naming ./scripts/gamma.py only\n"}, "dot slash", 9)
    build(repo, st)
    assert pack(st, "scripts/gamma.py")["counts"].get("ledger") == 1, "a ./ mention was not counted"


def check_nul_newline(repo, st, ids, tmp):
    build(repo, st)
    n = len(records(st))
    p = payload(repo, "Read", {"file_path": "%s/docs/NOTE.md\nscripts/alpha.py" % repo}, sid="nl")
    assert context(run(repo, st, p)) == "" and len(records(st)) == n, "a path holding a newline was taken as tracked"


def same_name_pair(repo, st):
    """README.md and deploy/README.md, both tracked, both with a pack (the verifier's wrong-file oracle, F4)."""
    commit(repo, {"README.md": "# root readme\n", "deploy/README.md": "# deploy readme\n"}, "a same-name pair", 9)
    build(repo, st)


def bash_heads(repo, st, cmd, sid):
    return heads(context(run(repo, st, bash(repo, cmd, sid=sid))))


def check_cd_scope(repo, st, ids, tmp):
    same_name_pair(repo, st)
    for k, cmd in enumerate(["(cd deploy && true); cat README.md", "(cd deploy) && cat README.md",
                             "echo $(cd deploy && pwd); cat README.md", "x=$(cd deploy); cat README.md",
                             "echo `cd deploy`; cat README.md"]):
        got = bash_heads(repo, st, cmd, "cs%d" % k)
        assert got == ["README.md"], "a cd inside ( ) or $( ) leaked out: %r gave %s" % (cmd, got)
    got = bash_heads(repo, st, "true && (cd scripts && cat alpha.py) && cat README.md", "cs-a")
    assert got == ["scripts/alpha.py", "README.md"], "a cd inside ( ) or $( ) leaked out: %s" % got
    assert bash_heads(repo, st, "(cd deploy && cat README.md)", "cs-in") == ["deploy/README.md"], \
        "the control: a cd holds inside its ( )"


def check_pushd_popd(repo, st, ids, tmp):
    same_name_pair(repo, st)
    got = bash_heads(repo, st, "pushd deploy >/dev/null && cat README.md", "pu")
    assert got == ["deploy/README.md"], "pushd was not followed: %s" % got
    got = bash_heads(repo, st, "pushd deploy >/dev/null && popd >/dev/null && cat README.md", "po")
    assert got == ["README.md"], "popd was not followed: %s" % got


def check_grep_pattern(repo, st, ids, tmp):
    build(repo, st)
    for k, cmd in enumerate(["grep scripts/beta.py docs/NOTE.md", "grep -e scripts/beta.py docs/NOTE.md",
                             "egrep -n scripts/beta.py docs/NOTE.md", "rg -g '*.md' scripts/beta.py docs/NOTE.md",
                             "grep --regexp=scripts/beta.py docs/NOTE.md", "grep -m 1 scripts/beta.py docs/NOTE.md"]):
        got = bash_heads(repo, st, cmd, "gp%d" % k)
        assert got == ["docs/NOTE.md"], "a grep pattern was taken as a file: %r gave %s" % (cmd, got)
    got = bash_heads(repo, st, "grep -f scripts/beta.py docs/NOTE.md", "gf")
    assert got == ["scripts/beta.py", "docs/NOTE.md"], "a grep -f pattern file was missed: %s" % got


def check_nested_script(repo, st, ids, tmp):
    same_name_pair(repo, st)
    for k, (cmd, want) in enumerate([("bash -c 'cat scripts/beta.py'", ["scripts/beta.py"]),
                                     ('sh -c "cat scripts/beta.py"', ["scripts/beta.py"]),
                                     ("bash -c 'cat scripts/beta.py scripts/gamma.py'",
                                      ["scripts/beta.py", "scripts/gamma.py"]),
                                     ("eval 'cat scripts/gamma.py'", ["scripts/gamma.py"])]):
        got = bash_heads(repo, st, cmd, "ns%d" % k)
        assert got == want, "a nested shell's script was not read: %r gave %s" % (cmd, got)
    got = bash_heads(repo, st, "bash -c 'cd deploy && cat README.md'; cat README.md", "nc")
    assert got == ["deploy/README.md", "README.md"], "a child shell's cd leaked out: %s" % got
    got = bash_heads(repo, st, "eval 'cd deploy'; cat README.md", "ne")
    assert got == ["deploy/README.md"], "an eval script's cd was not kept: %s" % got


def check_remote(repo, st, ids, tmp):
    build(repo, st)
    for k, cmd in enumerate(["ssh pc 'cat scripts/beta.py'", 'ssh -p 22 pc "cat scripts/beta.py docs/NOTE.md"',
                             "scripts/pc.sh 'cat scripts/beta.py'", 'bash scripts/pc.sh "cat scripts/beta.py"',
                             "ssh pc <<'EOF'\ncat scripts/beta.py\nEOF"]):
        assert bash_heads(repo, st, cmd, "rm%d" % k) == [], "a command run on another host injected: %r" % cmd
    for k, cmd in enumerate(["ssh pc time cat scripts/beta.py", "ssh pc bash -c 'cat scripts/beta.py'"]):
        assert bash_heads(repo, st, cmd, "rx%d" % k) == [], "a command under ssh injected: %r" % cmd
    got = bash_heads(repo, st, "ssh pc 'cat scripts/beta.py' && cat docs/NOTE.md", "rc")
    assert got == ["docs/NOTE.md"], "the control: a local read after a remote command: %s" % got


def check_linear_parse(repo, st, ids, tmp):
    """F3: 6,000 `time cat` pairs through the wrapper (the verifier's: the 55 s cap). The bound, 3 s, sits far from
    both sides on every venue measured: the capped scan is linear, and the uncapped one (the no-word-cap mutant) is
    quadratic. At 3,000 pairs the uncapped scan took about 5 s here but under 3 s on CI's faster runner (run 1145,
    2026-09-29: the negative control did not raise), so the pair count doubled: the uncapped time grows about fourfold,
    the capped one about twofold."""
    build(repo, st)
    cmd = "echo " + "time cat " * 6000 + "docs/NOTE.md"
    t0 = time.monotonic()
    ctx = context(run(repo, st, bash(repo, cmd, sid="lin"), timeout=120))
    took = time.monotonic() - t0
    assert took < 3, "the parse is not linear: 6,000 time-cat pairs took %.1f s" % took
    assert heads(ctx) == ["docs/NOTE.md"], "the control: the reader's file was read: %s" % heads(ctx)


# ---------- round 3: VERIFY-K2 R2 B1 (untracked callers and tests), B2 (the symbols' graph), the seven checks ------

def alter_pack(repo, change):
    """Apply `change` (a function of the pack) to alpha's planted code pack."""
    p = repo / ".jev" / "codemap" / "scripts" / "alpha.py.json"
    pk = json.loads(p.read_text(encoding="utf-8"))
    change(pk)
    p.write_text(json.dumps(pk, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def plant_callers(repo, callers, tests, caller_files, count=5, graphs=None):
    """alpha's code pack with helper's callers sample, the file's tests and its caller files as given, and the graph
    marks in `graphs` ({graph: fresh|stale}); everything else as plant_code_pack wrote it."""
    def change(pk):
        helper = next(s for s in pk["symbols"] if s["qualname"] == "helper")
        helper["gitnexus"]["callers"] = {"count": count, "tests": 1, "sample": callers}
        pk["tests"], pk["caller_files"] = tests, caller_files
        for g, v in (graphs or {}).items():
            pk["instruments"][g]["graph"] = v
    alter_pack(repo, change)


def helper_edit(repo, sid):
    return edit(repo, "scripts/alpha.py", "    return x + 1", sid=sid)


def check_untracked_callers(repo, st, ids, tmp):
    """VERIFY-K2 R2 B1: GitNexus (and code-review-graph) index untracked files too. The code part names only the
    callers and tests in files TRACKED.txt lists, and a callers total that counted any other caller (a sampled one, or
    one past the sample that caller_files names) is left out; a clean pack's total stands (the control)."""
    commit(repo, {"tests/test_trk.py": "def test_trk():\n    pass\n"}, "a tracked test", 9)
    build(repo, st)
    uc, ut, trk = ("%s%s" % (k, secrets.token_hex(5)) for k in ("uc", "ut", "trk"))
    tracked = [{"name": trk, "file": "scripts/beta.py", "line": 2},
               {"name": "main", "file": "scripts/alpha.py", "line": 18}]
    tests = [{"file": "tests/test_trk.py", "line": 1, "name": "test_" + trk, "indirect": False}]
    test_line = "tests of the file (code-review-graph) 1: tests/test_trk.py:1 test_" + trk
    left_out = ("callers in tracked files (the total is left out): %s scripts/beta.py:2 · main scripts/alpha.py:18"
                % trk)
    plant_callers(repo, tracked, tests, ["scripts/beta.py", "tests/test_trk.py"])
    lines = context(run(repo, st, helper_edit(repo, "uc0"))).split("\n")
    assert "callers 5 (1 in tests): %s scripts/beta.py:2 · main scripts/alpha.py:18 · +3 more" % trk in lines, \
        "the control: a clean pack's callers total was left out: %s" % lines[:4]
    plant_callers(repo, [{"name": uc, "file": "scripts/caller_%s.py" % uc, "line": 4}] + tracked,
                  [{"file": "tests/test_%s.py" % ut, "line": 1, "name": "test_" + ut, "indirect": False}] + tests,
                  ["scripts/beta.py", "scripts/caller_%s.py" % uc, "tests/test_%s.py" % ut, "tests/test_trk.py"])
    for k, p in enumerate((helper_edit(repo, "uc1"), read(repo, "scripts/alpha.py", sid="uc2"))):
        ctx = context(run(repo, st, p))
        assert uc not in ctx, "an untracked caller reached the model"
        assert ut not in ctx, "an untracked test reached the model"
        assert test_line in ctx.split("\n") and (k or "%s scripts/beta.py:2" % trk in ctx), \
            "the control: a tracked caller or test was left out: %r" % ctx[:400]
        assert k or left_out in ctx.split("\n"), \
            "a callers total counted a caller the model is not shown: %r" % ctx[:400]
    plant_callers(repo, tracked, tests, ["scripts/beta.py", "scripts/caller_%s.py" % uc, "tests/test_trk.py"])
    lines = context(run(repo, st, helper_edit(repo, "uc3"))).split("\n")
    assert left_out in lines, "a callers total counted an unseen untracked caller: %s" % lines[:4]


def check_same_file_stale(repo, st, ids, tmp):
    """A caller or a test in the file itself is named from a graph's index of the file: from a stale graph the name can
    come from bytes no commit holds (B2's class, through B1's lists), so it is left out, and so is the callers total
    (it can count such callers past the sample); a fresh graph's names stay (the control)."""
    build(repo, st)
    cc, ct, trk = ("%s%s" % (k, secrets.token_hex(5)) for k in ("cc", "ct", "trk"))
    callers = [{"name": trk, "file": "scripts/beta.py", "line": 2},
               {"name": cc, "file": "scripts/alpha.py", "line": 30}]
    tests = [{"file": "scripts/alpha.py", "line": 31, "name": ct, "indirect": False}]
    plant_callers(repo, callers, tests, ["scripts/beta.py"], count=2)
    ctx = context(run(repo, st, helper_edit(repo, "sf0")))
    assert cc in ctx and ct in ctx, "the control: a fresh graph's names of this file were left out: %r" % ctx[:400]
    plant_callers(repo, callers, tests, ["scripts/beta.py"], count=2,
                  graphs={"gitnexus": "stale", "code-review-graph": "stale"})
    ctx = context(run(repo, st, helper_edit(repo, "sf1")))
    assert cc not in ctx, "a caller named by a stale GitNexus graph of this file reached the model"
    assert ct not in ctx, "a test named by a stale code-review-graph of this file reached the model"
    assert "%s scripts/beta.py:2" % trk in ctx, "the control: a tracked caller in another file was left out"
    plant_callers(repo, callers[:1], [], ["scripts/beta.py"], count=2, graphs={"gitnexus": "stale"})
    lines = context(run(repo, st, helper_edit(repo, "sf2"))).split("\n")
    assert "callers in tracked files (the total is left out): %s scripts/beta.py:2" % trk in lines, \
        "a callers total from a stale GitNexus graph stood: %s" % lines[:4]


def check_caller_path_newline(repo, st, ids, tmp):
    """TRACKED.txt's match is a whole line: a caller path holding a newline, whose two halves are tracked lines one
    after the other, is not a tracked file."""
    build(repo, st)
    assert "\nscripts/beta.py\nscripts/gamma.py\n" in (st / "filepacks" / "TRACKED.txt").read_text(), "not the case"
    cn = "cn" + secrets.token_hex(5)
    plant_callers(repo, [{"name": cn, "file": "scripts/beta.py\nscripts/gamma.py", "line": 1}], [], ["scripts/beta.py"])
    ctx = context(run(repo, st, helper_edit(repo, "pn")))
    assert ctx.startswith("codemap scripts/alpha.py:6 — function helper"), "the control: no code part: %r" % ctx[:80]
    assert cn not in ctx, "a caller path holding a newline was taken as tracked"


def check_stale_symbol_graph(repo, st, ids, tmp):
    """VERIFY-K2 R2 B2: a pack's symbols come from one graph's index (symbols_from). When that graph had not indexed the
    pack's bytes, the symbols can be another content's (an untracked or a reverted edit), so the code part is left out
    and the record says stale-graph; the source graph is the one read (the control: a stale graft beside a fresh
    code-review-graph source leaves the code part shown)."""
    build(repo, st)

    def marks(src, graft, crg):
        def change(pk):
            pk["symbols_from"] = src
            pk["instruments"]["graft"]["graph"], pk["instruments"]["code-review-graph"]["graph"] = graft, crg
        alter_pack(repo, change)
    for k, (src, graft, crg) in enumerate([("graft", "stale", "fresh"), ("code-review-graph", "fresh", "stale")]):
        marks(src, graft, crg)
        ctx = context(run(repo, st, read(repo, "scripts/alpha.py", sid="sg%d" % k)))
        assert ctx.startswith("filepack scripts/alpha.py @") and "codemap " not in ctx, \
            "a code part from a stale symbol graph reached the model: %r" % ctx[:80]
        assert records(st)[-1]["injected"][0].get("code_skip") == "stale-graph", records(st)[-1]["injected"]
    marks("code-review-graph", "stale", "fresh")
    ctx = context(run(repo, st, read(repo, "scripts/alpha.py", sid="sg-c")))
    assert ctx.startswith("codemap scripts/alpha.py — 5 symbols"), \
        "the control: a fresh symbol graph's code part was left out: %r" % ctx[:80]


def check_sourceless_symbols(repo, st, ids, tmp):
    """A pack that holds symbols but names no graph they came from is left out: no graph can vouch for them. One with
    neither gives the file's entry (the control: nothing to tie)."""
    build(repo, st)
    alter_pack(repo, lambda pk: pk.update(symbols_from=None))
    ctx = context(run(repo, st, read(repo, "scripts/alpha.py", sid="ns0")))
    assert ctx.startswith("filepack scripts/alpha.py @"), \
        "a code part whose symbols name no source graph reached the model: %r" % ctx[:80]
    alter_pack(repo, lambda pk: pk.update(symbols=[]))
    ctx = context(run(repo, st, read(repo, "scripts/alpha.py", sid="ns1")))
    assert ctx.startswith("codemap scripts/alpha.py — 0 symbols"), "the control: no file entry: %r" % ctx[:80]


# The verifier's seven (VERIFY-K2 R2 finding 4: each mutant survived the round-2 checks), from its mutdrv3.py killers.

def check_blobs_missing(repo, st, ids, tmp):
    """The registration state: the live .jev/filepacks is a build from before BLOBS.txt existed. No code part goes out
    until a build writes it; the pack's lines do."""
    build(repo, st)
    os.unlink(st / "filepacks" / "BLOBS.txt")
    ctx = context(run(repo, st, read(repo, "scripts/alpha.py", sid="bm")))
    assert ctx.startswith("filepack scripts/alpha.py @") and "codemap " not in ctx, \
        "a code part went out with no BLOBS.txt: %r" % ctx[:60]


def check_grep_long_value(repo, st, ids, tmp):
    build(repo, st)
    got = bash_heads(repo, st, "grep --max-count 1 scripts/beta.py docs/NOTE.md", "gl")
    assert got == ["docs/NOTE.md"], "a long option's value was taken as the pattern: %s" % got


def check_grep_attached(repo, st, ids, tmp):
    build(repo, st)
    got = bash_heads(repo, st, "grep -m1 scripts/beta.py docs/NOTE.md", "ga")
    assert got == ["docs/NOTE.md"], "an attached short value swallowed the pattern: %s" % got


def check_script_paren(repo, st, ids, tmp):
    build(repo, st)
    got = bash_heads(repo, st, "bash -c 'case x in x) true;; esac'; cat docs/NOTE.md", "sp")
    assert got == ["docs/NOTE.md"], "a ) inside a nested script broke the frame scan: %s" % got


def check_dq_substitution(repo, st, ids, tmp):
    same_name_pair(repo, st)
    got = bash_heads(repo, st, 'echo "$(cd deploy && pwd)"; cat README.md', "dq")
    assert got == ["README.md"], "a cd inside a double-quoted $( ) leaked out: %s" % got


def check_grep_double_dash(repo, st, ids, tmp):
    build(repo, st)
    got = bash_heads(repo, st, "grep -- scripts/beta.py docs/NOTE.md", "dd")
    assert got == ["docs/NOTE.md"], "grep -- lost its files or read its pattern: %s" % got


def check_files_max(repo, st, ids, tmp):
    fp = load(repo)
    cmd = "cat " + " ".join("d%d/f.py" % i for i in range(60)) + "; cat " + " ".join("e%d/f.py" % i for i in range(60))
    n = len(fp.bash_paths(cmd, str(repo), repo))
    assert n == 64, "a command line gave %d paths, not FILES_MAX (64)" % n


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
          "no-pyc-in-claude": check_no_pyc_in_claude, "replay": check_replay,
          # round 2 (VERIFY-K2): F1, the verifier's seventeen (F14), F3, F4 and F5
          "untracked-since-build": check_untracked_since_build, "blobs-exact-path": check_blobs_exact_path,
          "fifo-working-file": check_fifo_working_file, "code-pack-parent-link": check_code_pack_parent_link,
          "pack-path-field": check_pack_path_field, "pack-schema": check_pack_schema,
          "root-untracked-suffix": check_root_untracked_suffix, "window-max-two": check_window_max_two,
          "cd-variable-dotdot": check_cd_variable_dotdot, "tilde": check_tilde, "replace-all": check_replace_all,
          "offset-zero": check_offset_zero, "log-rotation": check_log_rotation, "long-subject": check_long_subject,
          "age-prune": check_age_prune, "reset-no-state": check_reset_no_state, "event-check": check_event_check,
          "dot-slash": check_dot_slash, "nul-newline": check_nul_newline, "cd-scope": check_cd_scope,
          "pushd-popd": check_pushd_popd, "grep-pattern": check_grep_pattern, "nested-script": check_nested_script,
          "remote": check_remote, "linear-parse": check_linear_parse,
          # round 3 (VERIFY-K2 R2): B1, B2, and the verifier's seven (finding 4)
          "untracked-callers": check_untracked_callers, "same-file-stale": check_same_file_stale,
          "caller-path-newline": check_caller_path_newline, "stale-symbol-graph": check_stale_symbol_graph,
          "sourceless-symbols": check_sourceless_symbols, "blobs-missing": check_blobs_missing,
          "grep-long-value": check_grep_long_value, "grep-attached": check_grep_attached,
          "script-paren": check_script_paren, "dq-substitution": check_dq_substitution,
          "grep-double-dash": check_grep_double_dash, "files-max": check_files_max}
# one mutation per property: (the check it must fail, old text, new text, the failure it must fail with)
ALL_KEPT = '    all_kept = fresh["gitnexus"] and isinstance(files, list) and all(listed(f) for f in files)\n'
TESTS_KEPT = '    pack["tests"] = [x for x in pack.get("tests") or [] if keep(x, "code-review-graph")]\n'
STALE_GRAPH = '    if (src is not None or pack.get("symbols")) and (graphs.get(src) or {}).get("graph") != "fresh":\n'
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
    "no-cd": ("bash-readers", "            cwd = _cd(args, cwd)\n", "            pass\n", "a cd was not followed"),
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
    "corrupt-code-pack-ignored": ("corrupt", '        raise PackError("corrupt") from None\n    if not isinstance(pack, dict)',
                                  '        return None, "", None, None, None\n    if not isinstance(pack, dict)',
                                  "a corrupt code pack still gave the file's entry"),
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
    # round 2: F1
    "no-blob-check": ("untracked-since-build", 'if pack["blob"] != packs.blob(rel):', "if False:",
                      "the untracked file's text reached the model"),
    "blobs-suffix-match": ("blobs-exact-path", 'key = ("\\n%s\\t" % rel).encode("utf-8")',
                           'key = ("%s\\t" % rel).encode("utf-8")', "a code pack was checked against another file's blob"),
    # round 2: the verifier's seventeen (VERIFY-K2 F14), each anchored on this file's text
    "fifo-working-file-read": ("fifo-working-file", "        if not stat.S_ISREG(wst.st_mode):\n            return None",
                               "        if False:\n            return None", "a FIFO working file"),
    "code-pack-parent-link-followed": ("code-pack-parent-link",
                                       "if not stat.S_ISREG(st.st_mode) or not _inside(path, Path(root) / cm.PACK_DIR):",
                                       "if not stat.S_ISREG(st.st_mode):", "a code pack under a linked directory was read"),
    "path-field-unchecked": ("pack-path-field", ' or pack.get("path") != rel:', ":", "a pack naming another file was read"),
    "schema-unchecked": ("pack-schema", 'pack.get("schema") != SCHEMA or ', "", "a pack of another schema was read"),
    "tracked-suffix-match": ("root-untracked-suffix", '("\\n%s\\n" % rel)', '("%s\\n" % rel)',
                             "an untracked root file matched a tracked path's tail"),
    "window-count-not-incremented": ("window-max-two", "        files += fkey not in taken\n", "",
                                     "a window at 63 files took two more in one call"),
    "cd-variable-followed": ("cd-variable-dotdot", '    if "$" in d or "`" in d:\n        return None\n', "",
                             "a cd through an unset variable was followed"),
    "tilde-not-expanded": ("tilde", '    if path.startswith("~/"):\n        path = os.path.expanduser(path)\n', "",
                           "a ~/ path was not expanded"),
    "replace-all-ignored": ("replace-all", 'replace_all=ti.get("replace_all") is True', "replace_all=False",
                            "a replace_all Edit was not placed in its symbol"),
    "offset-zero-not-clamped": ("offset-zero", "        lo = max(off, 1)\n", "        lo = off\n",
                                "a Read at offset 0 lost its entry"),
    "log-no-rotation": ("log-rotation", "            if os.path.getsize(path) > sys1.LOG_MAX_BYTES:", "            if False:",
                        "the log did not rotate"),
    "commit-subject-uncut": ("long-subject", '"subject": _cut(subj, SNIPPET)', '"subject": subj',
                             "a commit subject was not cut at 240 characters"),
    "no-age-prune": ("age-prune", "if hit or now - os.lstat(path).st_mtime > sys1.MARKER_MAX_AGE_S:", "if hit:",
                     "a marker idle 8 days was not pruned"),
    "reset-without-state-check": ("reset-no-state", "            if not state.is_dir():\n                return 0",
                                  "            if False:\n                return 0", "a reset with no state created one"),
    "no-event-check": ("event-check", 'elif payload.get("hook_event_name") == "PreToolUse":', "elif True:",
                       "a PostToolUse payload injected"),
    "dot-slash-ignored": ("dot-slash", '        elif t.startswith("./"):', "        elif False:",
                          "a ./ mention was not counted"),
    "no-nul-newline-guard": ("nul-newline", ' or "\\0" in path or "\\n" in path or ', " or ",
                             "a path holding a newline was taken as tracked"),
    # round 2: F4 and F5 (the right file) and F3 (a linear parse)
    "cd-scope-leaks": ("cd-scope", "                if f[0]:\n                    cwd, dirs = f[1], f[2]\n",
                       "                pass\n", "a cd inside ( ) or $( ) leaked out"),
    "no-pushd": ("pushd-popd", '            cwd = _cd(args, cwd) if len(args) == 1 and args[0] and args[0][0] not in "+-" '
                 'else None\n', "            pass\n", "pushd was not followed"),
    "no-popd": ("pushd-popd", "            elif dirs:\n                cwd, dirs = dirs\n",
                "            elif dirs:\n                pass\n", "popd was not followed"),
    "grep-pattern-as-file": ("grep-pattern", "return files + operands[0 if given else 1:]", "return files + operands",
                             "a grep pattern was taken as a file"),
    "grep-f-file-missed": ("grep-pattern", '                    if ch == "f":\n                        files.append(val)\n',
                           '                    if ch == "f":\n                        pass\n',
                           "a grep -f pattern file was missed"),
    "no-quote-strip": ("nested-script", " + [(k, k + 1) for k in closers])", ")",
                       "a nested shell's script was not read"),
    "bash-c-cd-leaks": ("nested-script", 'stack.append([ev[2] != "script" or stack[-1][3] != "eval", cwd, dirs, None])',
                        'stack.append([ev[2] != "script", cwd, dirs, None])', "a child shell's cd leaked out"),
    "eval-scoped": ("nested-script", 'stack.append([ev[2] != "script" or stack[-1][3] != "eval", cwd, dirs, None])',
                    "stack.append([True, cwd, dirs, None])", "an eval script's cd was not kept"),
    "remote-read-locally": ("remote", '    if "ssh" not in cmd and "pc.sh" not in cmd:\n        return code, frozenset()',
                            "    if True:\n        return code, frozenset()", "a command run on another host injected"),
    "remote-extent-ignored": ("remote", "            remote = len(stack)", "            remote = 0",
                              "a command under ssh injected"),
    "no-word-cap": ("linear-parse", "        for s, e in self.toks[i:i + WORDS_MAX]:", "        for s, e in self.toks[i:]:",
                    "the parse is not linear"),
    # round 3: B1 (a filter per list, the total both ways), the same-file names of a stale graph, the exact line
    "untracked-callers-kept": ("untracked-callers", '        kept = [x for x in sample if keep(x, "gitnexus")]\n',
                               "        kept = list(sample)\n", "an untracked caller reached the model"),
    "untracked-tests-kept": ("untracked-callers", TESTS_KEPT, '    pack["tests"] = pack.get("tests") or []\n',
                             "an untracked test reached the model"),
    "callers-total-kept": ("untracked-callers", "        if not all_kept or len(kept) < len(sample):\n",
                           "        if False:\n", "a callers total counted a caller the model is not shown"),
    "callers-total-always-dropped": ("untracked-callers", ALL_KEPT, "    all_kept = False\n",
                                     "the control: a clean pack's callers total was left out"),
    "caller-files-ignored": ("untracked-callers", ALL_KEPT, '    all_kept = fresh["gitnexus"]\n',
                             "a callers total counted an unseen untracked caller"),
    "same-file-names-from-stale-graphs": ("same-file-stale",
                                          "        return listed(f) and (f != rel or fresh[graph])\n",
                                          "        return listed(f)\n",
                                          "a caller named by a stale GitNexus graph of this file reached the model"),
    "stale-gitnexus-total-stands": ("same-file-stale", ALL_KEPT,
                                    "    all_kept = isinstance(files, list) and all(listed(f) for f in files)\n",
                                    "a callers total from a stale GitNexus graph stood"),
    "tracked-newline-unguarded": ("caller-path-newline",
                                  '        return isinstance(f, str) and "\\n" not in f and "\\0" not in f and packs.tracked(f)\n',
                                  "        return packs.tracked(f)\n",
                                  "a caller path holding a newline was taken as tracked"),
    # B2: the clause, its source graph, a pack with symbols and no source
    "stale-symbol-graph-shown": ("stale-symbol-graph", STALE_GRAPH, "    if False:\n",
                                 "a code part from a stale symbol graph reached the model"),
    "symbol-graph-always-graft": ("stale-symbol-graph", '(graphs.get(src) or {}).get("graph") != "fresh"',
                                  '(graphs.get("graft") or {}).get("graph") != "fresh"',
                                  "a code part from a stale symbol graph reached the model"),
    "sourceless-symbols-shown": ("sourceless-symbols", '    if (src is not None or pack.get("symbols")) and',
                                 "    if src is not None and",
                                 "a code part whose symbols name no source graph reached the model"),
    # the verifier's seven, with the anchors and replacements of its mutdrv2.py and mutdrv3.py
    "blob-fail-open": ("blobs-missing", '    if pack["blob"] != packs.blob(rel):',
                       '    if packs.blob(rel) is not None and pack["blob"] != packs.blob(rel):',
                       "a code part went out with no BLOBS.txt"),
    "grep-long-value-dropped": ("grep-long-value", "            if name in long_ and not eq:\n",
                                "            if False:\n", "a long option's value was taken as the pattern"),
    "grep-attached-ignored": ("grep-attached", "                    val = w[k:]\n", '                    val = ""\n',
                              "an attached short value swallowed the pattern"),
    "frame-close-any": ("script-paren", '            if top == "sub":\n                stack.pop()',
                        "            if stack:\n                stack.pop()",
                        "a ) inside a nested script broke the frame scan"),
    "dq-sub-not-opened": ("dq-substitution", '            elif c in "(`":\n', "            elif False:\n",
                          "a cd inside a double-quoted $( ) leaked out"),
    "grep-double-dash-dropped": ("grep-double-dash", "            operands += words[i:]\n            break\n",
                                 "            break\n", "grep -- lost its files or read its pattern"),
    "files-max-off": ("files-max", "FILES_MAX = 64 ", "FILES_MAX = 10 ** 9 ", "not FILES_MAX (64)"),
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


def test_negative_control_the_code_map_without_its_left_out_total(tmp_path):
    """The code map's half of B1: without its line for a total the reader left out (codemap._callers_line), such a
    symbol's kept callers are lost, and check untracked-callers fails on its control."""
    repo, ids = fixture(tmp_path)
    cm = repo / "scripts" / "codemap.py"
    text = cm.read_text(encoding="utf-8")
    old = ('    if g and c.get("count") is None and isinstance(c.get("sample"), list):     # the file-pack reader\'s view'
           ' (K2 R3)\n        return "callers in tracked files (the total is left out): %s" % (\n'
           '            " · ".join("%s %s" % (x["name"], _where(x)) for x in c["sample"]) or "none shown")\n')
    assert text.count(old) == 1, "INVALID: the anchor occurs %d times" % text.count(old)
    compile(text.replace(old, ""), "codemap-mutant.py", "exec")
    cm.write_text(text.replace(old, ""), encoding="utf-8")
    with pytest.raises(AssertionError, match=re.escape("the control: a tracked caller or test was left out")):
        check_untracked_callers(repo, tmp_path / "state", ids, tmp_path)


# ---------- F1 with the post-commit patch applied, and with the real code-map refresh ----------

PATCH = ROOT / "tasks" / "briefs" / "jev-trim" / "K2-post-commit.patch"
# origin 99583a2 (K2 round 3's PIN): its scripts/hooks/post-commit is the patch's pre-image, the hook without the patch
UNPATCHED_AT = "99583a26915d2cbd3a228b9a561864fc81b97487"
GRAFT = shutil.which("graft")


def hook_dir(tmp, patch, src=None):
    """A hooks directory holding the post-commit hook. With `patch`: the repo's own hook (`src`, the working copy by
    default) carrying the K2 patch, applied by `git apply` as the coordinator applies it unless the hook carries it
    already (once the patch lands, VERIFY-K2 R2 B3). Without: the hook before the patch, from UNPATCHED_AT, never the
    working copy (which carries the patch once it lands); its blob is the one the patch names as its pre-image."""
    d = Path(tempfile.mkdtemp(prefix="hookcopy-", dir=tmp))
    (d / "scripts" / "hooks").mkdir(parents=True)
    hook = d / "scripts" / "hooks" / "post-commit"
    env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(tmp))

    def apply(*args):
        return subprocess.run(["git", "apply", *args, str(PATCH)], cwd=d, capture_output=True, text=True, timeout=60,
                              env=env)
    if patch:
        shutil.copy2(src or ROOT / "scripts" / "hooks" / "post-commit", hook)
        if apply("-R", "--check").returncode != 0:      # not carrying the patch yet
            r = apply()
            assert r.returncode == 0, r.stderr
    else:
        r = subprocess.run(["git", "show", UNPATCHED_AT + ":scripts/hooks/post-commit"], cwd=ROOT, capture_output=True,
                           timeout=60)
        assert r.returncode == 0, r.stderr
        hook.write_bytes(r.stdout)
        hook.chmod(0o755)
        pre = re.search(r"^index ([0-9a-f]+)\.\.", PATCH.read_text(encoding="utf-8"), re.M).group(1)
        blob = subprocess.run(["git", "hash-object", "--no-filters", str(hook)], capture_output=True, text=True,
                              timeout=60).stdout
        assert blob.startswith(pre), "the hook at UNPATCHED_AT is not the patch's pre-image %s: %s" % (pre, blob)
    return d / "scripts" / "hooks"


def patched_scenario(tmp, patch, fp_text=None):
    """F1 with the post-commit hook in place: a build lists scripts/gamma.py; a commit untracks it (hooks off); a
    docs-only commit goes through the real hook, which with the patch launches the file-pack build at HEAD (a docs-only
    commit launches nothing else, so no graph or code-map job leaves the test); once that build is done, the canary
    goes in and the code pack is rebuilt from the working copy. 0 canary bytes, and nothing, on Edit, Read and cat."""
    repo, ids = fixture(tmp, fp_text=fp_text)
    st, pct = tmp / "state", tmp / "pctmp"
    pct.mkdir()
    build(repo, st)
    git(repo, "rm", "-q", "--cached", "scripts/gamma.py", k=9)
    git(repo, "commit", "-q", "-m", "gamma untracked", k=9)
    (repo / "docs" / "NOTE.md").write_text("# note\na docs-only line\n", encoding="utf-8")
    env = dict(env_for(repo, st), AF_POST_COMMIT_TMP=str(pct), GIT_AUTHOR_DATE="@%d +0000" % (EPOCH + 10),
               GIT_COMMITTER_DATE="@%d +0000" % (EPOCH + 10))
    r = subprocess.run(["git", "-c", "user.email=k2@test", "-c", "user.name=k2", "-c", "commit.gpgsign=false", "-c",
                        "core.hooksPath=%s" % hook_dir(tmp, patch), "commit", "-q", "-am", "docs only"], cwd=repo,
                       env=env, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    head = git(repo, "rev-parse", "HEAD").strip()
    log = pct / "filepacks-build.log"
    assert log.exists() and "%s filepacks build launched" % head[:7] in log.read_text(), \
        "the post-commit hook ran no file-pack build"
    fd = os.open(pct / "filepacks-build.lock", os.O_RDONLY)        # held until the build and its subshell are gone
    try:
        deadline = time.monotonic() + 60
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                assert time.monotonic() < deadline, "the post-commit build did not finish in 60 s"
                time.sleep(0.1)
    finally:
        os.close(fd)
    assert json.loads((st / "filepacks" / "BUILD.json").read_text())["commit"] == head, log.read_text()[-300:]
    assert "filepacks build: %s " % head[:7] in log.read_text(), log.read_text()[-300:]
    canary = "cnry" + secrets.token_hex(6)
    (repo / "scripts" / "gamma.py").write_text('def leak_%s(token="%s-arg"):\n    return token\n' % (canary, canary),
                                                encoding="utf-8")
    plant_code_pack(repo, "scripts/gamma.py", head)
    for p in gamma_probes(repo, "pp"):
        ctx = context(run(repo, st, p))
        assert canary not in ctx and ctx == "", "the untracked file's text reached the model: %r" % ctx[:80]


@pytest.mark.parametrize("fp", ["real", "no-blob-check"])
def test_untracked_since_build_with_the_post_commit_patch(tmp_path, fp):
    """F1 with the patch applied: its build alone keeps the file out (so the mutant without the blob check passes
    too; the blob check is the second guard, for a failed or stalled build)."""
    patched_scenario(tmp_path, True, None if fp == "real" else mutant(fp))


def test_negative_control_the_hook_without_the_patch_runs_no_build(tmp_path):
    with pytest.raises(AssertionError, match=re.escape("the post-commit hook ran no file-pack build")):
        patched_scenario(tmp_path, False)


@pytest.mark.skipif(not GRAFT, reason="LOUD SKIP: graft is not installed here (scripts/setup.sh installs it); this "
                                      "test runs the real L2a refresh, which builds from graft's graph")
@pytest.mark.parametrize("fp", ["real", "no-blob-check"])
def test_untracked_since_build_with_the_real_code_map_refresh(tmp_path, fp):
    """The verifier's probe_p6.py exactly: the untracked file's code pack is rebuilt by the REAL refresh
    (`codemap.py refresh --commit … --graphs graft`, as the post-commit hook runs it) after a graft re-index. The
    real hook shows 0 canary bytes on Edit, Read and cat; the mutant without the blob check shows the canary on all
    three (the control: the refresh's pack carries the canary into the entry)."""
    repo, ids = fixture(tmp_path, fp_text=None if fp == "real" else mutant(fp))
    st, home, locks = tmp_path / "state", tmp_path / "home", tmp_path / "locks"
    (home / ".graft").mkdir(parents=True)
    locks.mkdir()
    # a fresh update-check answer in graft's private HOME: with none, `graft build` spawns a detached registry check
    # that outlives the test and writes into this HOME after pytest removed it (and a later test reused the name)
    (home / ".graft" / "update-check.json").write_text(json.dumps({"latest": None,
                                                                   "checkedAt": int(time.time() * 1000)}))
    env = {"PATH": "%s:/usr/bin:/bin" % os.path.dirname(GRAFT), "HOME": str(home), "DO_NOT_TRACK": "1",
           "LANG": "C.UTF-8"}

    def sh(*argv):
        r = subprocess.run(list(argv), cwd=repo, env=env, capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, (argv, r.stdout[-400:], r.stderr[-400:])
        return r.stdout
    sh(GRAFT, "build")
    build(repo, st)
    git(repo, "rm", "-q", "--cached", "scripts/gamma.py", k=9)
    git(repo, "commit", "-q", "-m", "gamma untracked", k=9)
    c9 = git(repo, "rev-parse", "HEAD").strip()
    canary = "cnry" + secrets.token_hex(6)
    (repo / "scripts" / "gamma.py").write_text('def leak_%s(token="%s-arg"):\n    return token\n' % (canary, canary),
                                                encoding="utf-8")
    sh(GRAFT, "build")
    out = sh("python3", "scripts/codemap.py", "refresh", "--commit", c9, "--lock-dir", str(locks), "--graphs", "graft",
             "--wait", "60", "--grace", "5", "--", "scripts/gamma.py")
    assert canary in (repo / ".jev" / "codemap" / "scripts" / "gamma.py.json").read_text(), out[-300:]
    leaked = [canary in context(run(repo, st, p)) for p in gamma_probes(repo, "rf")]
    if fp == "real":
        assert leaked == [False, False, False], "the untracked file's text reached the model: %s" % leaked
    else:
        assert leaked == [True, True, True], "the control: without the blob check the canary reaches the model"


# ---------- round 3: B3 (the patch's own tests once it lands), B2 and B1 through the real instruments ----------

GITNEXUS = shutil.which("gitnexus")
CRG_FALLBACK = "/root/venv-crg/bin/code-review-graph"                 # the post-commit hook's fixed fallback path
CRG = shutil.which("code-review-graph") or (CRG_FALLBACK if os.access(CRG_FALLBACK, os.X_OK) else None)


def test_hook_dir_knows_whether_the_hook_carries_the_patch(tmp_path):
    """VERIFY-K2 R2 B3: before the patch lands and after it, `hook_dir` gives the hook carrying the patch once (never
    `git apply` on a hook that has it), and the hook without it from UNPATCHED_AT whatever the working copy holds."""
    before = subprocess.run(["git", "show", UNPATCHED_AT + ":scripts/hooks/post-commit"], cwd=ROOT,
                            capture_output=True, timeout=60).stdout
    src = tmp_path / "working" / "post-commit"
    src.parent.mkdir()
    src.write_bytes(before)
    after = (hook_dir(tmp_path, True, src) / "post-commit").read_bytes()
    assert after != before and b"scripts/filepacks.py build" in after, "the patch was not applied to the hook"
    src.write_bytes(after)                                   # the working copy once the patch has landed
    assert (hook_dir(tmp_path, True, src) / "post-commit").read_bytes() == after, "the landed hook was changed"
    assert (hook_dir(tmp_path, False, src) / "post-commit").read_bytes() == before, \
        "the hook without the patch came from the working copy"


def graft_env(tmp):
    """graft's own environment: a private HOME holding a fresh update-check answer (with none, `graft build` spawns a
    detached registry check that outlives the test), graft's directory and the system's on PATH."""
    home = tmp / "home"
    (home / ".graft").mkdir(parents=True, exist_ok=True)
    (home / ".graft" / "update-check.json").write_text(json.dumps({"latest": None,
                                                                   "checkedAt": int(time.time() * 1000)}))
    return {"PATH": "%s:/usr/bin:/bin" % os.path.dirname(GRAFT), "HOME": str(home), "DO_NOT_TRACK": "1",
            "LANG": "C.UTF-8"}


@pytest.mark.skipif(not GRAFT, reason="LOUD SKIP: graft is not installed here (scripts/setup.sh installs it); this "
                                      "test runs the real L2a refresh, which builds from graft's graph")
@pytest.mark.parametrize("fp", ["real", "stale-symbol-graph-shown"])
@pytest.mark.parametrize("shape", ["untracked", "tracked"])
def test_stale_symbol_graph_with_the_real_code_map_refresh(tmp_path, shape, fp):
    """VERIFY-K2 R2 B2, the verifier's probe_f1b.py sg-untracked and probe_f1.py sg-tracked: graft indexes a canary,
    the file's bytes go back to the blob BLOBS.txt holds, and the REAL refresh builds a pack whose blob matches while
    its symbols are the canary's (graft stale). untracked: scripts/gamma.py, untracked since the build; tracked: an
    edit of scripts/alpha.py reverted by `git checkout`. The real hook shows 0 canary bytes and says stale-graph; the
    mutant without the clause shows the canary (the control)."""
    repo, ids = fixture(tmp_path, fp_text=None if fp == "real" else mutant(fp))
    st, locks, env = tmp_path / "state", tmp_path / "locks", graft_env(tmp_path)
    locks.mkdir()

    def sh(*argv):
        r = subprocess.run(list(argv), cwd=repo, env=env, capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, (argv, r.stdout[-400:], r.stderr[-400:])
        return r.stdout
    sh(GRAFT, "build")
    build(repo, st)
    rel = "scripts/gamma.py" if shape == "untracked" else "scripts/alpha.py"
    if shape == "untracked":
        git(repo, "rm", "-q", "--cached", rel, k=9)
        git(repo, "commit", "-q", "-m", "gamma untracked", k=9)
    at = git(repo, "rev-parse", "HEAD").strip()
    before = (repo / rel).read_bytes()
    canary = "cnry" + secrets.token_hex(6)
    fn = 'def leak_%s(token="%s-arg"):\n    return token\n' % (canary, canary)
    (repo / rel).write_text(fn if shape == "untracked" else before.decode("utf-8") + "\n\n" + fn, encoding="utf-8")
    sh(GRAFT, "build")
    if shape == "untracked":
        (repo / rel).write_bytes(before)
    else:
        git(repo, "checkout", "--", rel)
    assert (repo / rel).read_bytes() == before, "the bytes did not go back"
    out = sh("python3", "scripts/codemap.py", "refresh", "--commit", at, "--lock-dir", str(locks), "--graphs", "graft",
             "--wait", "8", "--grace", "2", "--", rel)
    pk = json.loads((repo / ".jev" / "codemap" / (rel + ".json")).read_text(encoding="utf-8"))
    assert canary in json.dumps(pk) and pk["instruments"]["graft"]["graph"] == "stale", out[-300:]
    assert "\n%s\t%s\n" % (rel, pk["blob"]) in (st / "filepacks" / "BLOBS.txt").read_text(), "the blob check stops it"
    probes = gamma_probes(repo, "sg") if shape == "untracked" else [read(repo, rel, sid="sgr"),
                                                                    bash(repo, "cat " + rel, sid="sgb")]
    leaked = [canary in context(run(repo, st, p)) for p in probes]
    if fp == "real":
        assert leaked == [False] * len(probes), "a stale symbol graph's text reached the model: %s" % leaked
        skips = [i.get("code_skip") for r in records(st)[-len(probes):] for i in r["injected"]]
        assert skips == ["stale-graph"] * len(probes), "the records did not say stale-graph: %s" % skips
    else:
        assert leaked == [True] * len(probes), "the control: without the clause the canary reaches the model"


def fixture_processes(tmp):
    """The pids of the processes whose working directory is under `tmp`: a job the test's commit started."""
    out = []
    for pid in os.listdir("/proc"):
        try:
            if pid.isdigit() and os.readlink("/proc/%s/cwd" % pid).startswith(str(tmp) + os.sep):
                out.append(int(pid))
        except OSError:
            pass
    return out


def wait_post_commit(pct, head, bound=300):
    """Until the post-commit hook's jobs for `head` are done: the code-map refresh and the file-pack build logged their
    results, and no job holds its lock any more. Returns a reader of the hook's logs."""
    deadline = time.monotonic() + bound

    def text(name):
        p = pct / name
        return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
    while not ("%s codemap refresh done" % head[:7] in text("codemap-refresh.log")
               and "filepacks build: %s " % head[:7] in text("filepacks-build.log")):
        assert time.monotonic() < deadline, "the post-commit jobs did not finish in %d s: %s" % (
            bound, text("codemap-refresh.log")[-300:])
        time.sleep(0.5)
    for name in ("graft-build.lock", "gitnexus-analyze.lock", "cbm-index.lock", "crg-build.lock",
                 "codemap-refresh.lock", "filepacks-build.lock"):
        if not (pct / name).exists():
            continue
        fd = os.open(pct / name, os.O_RDONLY)
        try:
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    assert time.monotonic() < deadline, "a post-commit job held %s past %d s" % (name, bound)
                    time.sleep(0.2)
        finally:
            os.close(fd)
    return text


@pytest.mark.skipif(not (GRAFT and GITNEXUS and CRG), reason="LOUD SKIP: graft, gitnexus or code-review-graph is not "
                    "installed here (scripts/setup.sh installs them); this test runs the real post-commit re-index")
@pytest.mark.parametrize("fp", ["real", "untracked-callers-kept"])
def test_untracked_callers_with_the_post_commit_patch(tmp_path, fp):
    """VERIFY-K2 R2 B1, the verifier's probe_callers2.py: an untracked scripts/caller_new.py and tests/test_new_u.py call
    alpha's helper beside tracked ones; a commit of an alpha change goes through the REAL patched post-commit hook
    (each graph re-indexed, the code map refreshed, the file packs built) and every graph reads fresh. An Edit in
    helper and a Read show the tracked caller and test (the controls) and neither the untracked name nor its paths;
    the mutant without the callers filter shows the untracked caller."""
    repo, ids = fixture(tmp_path, fp_text=None if fp == "real" else mutant(fp))
    st, pct = tmp_path / "state", tmp_path / "pctmp"
    pct.mkdir()
    env = dict(env_for(repo, st), HOME=graft_env(tmp_path)["HOME"], DO_NOT_TRACK="1", AF_POST_COMMIT_TMP=str(pct))
    try:
        for argv in ([GRAFT, "build"], [GITNEXUS, "analyze", "--skip-agents-md"], [CRG, "build"]):
            r = subprocess.run(argv, cwd=repo, env=env, capture_output=True, text=True, timeout=300)
            assert r.returncode == 0, (argv, r.stdout[-300:], r.stderr[-300:])
        build(repo, st)
        unt, trk = "unt" + secrets.token_hex(5), "trk" + secrets.token_hex(5)
        body = "from alpha import helper\n\n\ndef %s():\n    return helper(2)\n"
        tbody = ("import sys\nsys.path.insert(0, 'scripts')\nfrom alpha import helper\n\n\ndef test_%s():\n"
                 "    assert helper(1) == 2\n")
        (repo / "tests").mkdir()
        for rel, text in (("scripts/caller_new.py", body % unt), ("scripts/caller_trk.py", body % trk),
                          ("tests/test_new_u.py", tbody % unt), ("tests/test_trk_t.py", tbody % trk)):
            (repo / rel).write_text(text, encoding="utf-8")
        (repo / "scripts" / "alpha.py").write_text((repo / "scripts" / "alpha.py").read_text(encoding="utf-8")
                                                   + "# a committed change\n", encoding="utf-8")
        git(repo, "add", "scripts/alpha.py", "scripts/caller_trk.py", "tests/test_trk_t.py")
        r = subprocess.run(["git", "-c", "user.email=k2@test", "-c", "user.name=k2", "-c", "commit.gpgsign=false", "-c",
                            "core.hooksPath=%s" % hook_dir(tmp_path, True), "commit", "-q", "-m", "alpha changed"],
                           cwd=repo, env=env, capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr
        head = git(repo, "rev-parse", "HEAD").strip()
        wait_post_commit(pct, head)
        assert json.loads((st / "filepacks" / "BUILD.json").read_text())["commit"] == head, "no build at HEAD"
        pk = json.loads((repo / ".jev" / "codemap" / "scripts" / "alpha.py.json").read_text(encoding="utf-8"))
        marks = {g: pk["instruments"][g].get("graph") for g in ("graft", "gitnexus", "code-review-graph")}
        assert pk["blob"] == git(repo, "rev-parse", "HEAD:scripts/alpha.py").strip() and set(marks.values()) == {
            "fresh"}, "not B1's healthy pipeline: %s" % marks
        assert unt in json.dumps(pk) and trk in json.dumps(pk), "the graph named no untracked caller: a vacuous test"
        ctx = context(run(repo, st, helper_edit(repo, "pe")))
        rctx = context(run(repo, st, read(repo, "scripts/alpha.py", sid="pr")))
        if fp == "real":
            for c in (ctx, rctx):
                assert unt not in c and "caller_new.py" not in c and "test_new_u.py" not in c, \
                    "an untracked caller's name or path reached the model"
            assert "%s scripts/caller_trk.py:4" % trk in ctx, "the control: the tracked caller was left out: %r" % ctx
            assert "tests/test_trk_t.py" in ctx and "tests/test_trk_t.py" in rctx, \
                "the control: the tracked test was left out"
        else:
            assert unt in ctx, "the control: without the filter the untracked caller reaches the model"
        assert fixture_processes(tmp_path) == [], "a post-commit job outlived its lock"
    finally:
        for pid in fixture_processes(tmp_path):
            os.kill(pid, signal.SIGKILL)


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
