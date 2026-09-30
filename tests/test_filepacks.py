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
kill). A mutant must fail the same check with the named failure; CM_MUTANTS do the same with a copy of
scripts/codemap.py. The code-map pack of scripts/alpha.py is planted in codemap.py's format as its builder writes one
since the re-scope (`plant_code_pack`: the symbols from the file's own AST, the graph sections no reader shows);
test_the_planted_code_pack_has_the_real_builders_fields compares its fields and symbols with a pack the real codemap
builder writes. Deterministic and LLM-free.

Round 2 (VERIFY-K2): F1, a file untracked since the last build whose code pack was rebuilt from the working copy with a
canary, runs three ways: with no build after the untracking commit (check untracked-since-build), with the post-commit
patch applied to the real hook by `git apply` (its build alone keeps the file out), and with the REAL L2a refresh after
a graft re-index (skipped loudly where graft is absent). The verifier's seventeen F14 checks are here under their names,
and the parser's F3, F4 and F5 shapes (the wrong files, the nested scripts, the remote commands, a 6,000-pair command's
time). `run` kills a stalled hook and fails as a stall.

Rounds 3 and 4 (VERIFY-K2 rounds 2 and 3; D-115): B1 (a caller or test in an untracked file named in a tracked file's
code part), R3-1 and the provenance by blob tested the callers-and-tests surface, which the re-scope removed; their
checks, mutants and class test went with it. B2 (a pack whose symbols came from a graph that had not indexed its bytes)
became condition (a) below. B3: `hook_dir` applies the post-commit patch only to a hook that does not carry it, and the
negative control's hook comes from UNPATCHED_AT (refused unless it is the patch's pre-image), so this file passes before
the patch lands and after. The verifier's seven checks that killed mutants the round-2 checks missed are here.

K2 RE-SCOPE (task #353, contract revision 5, D-117; VERIFY-K2-R4's R4-1): every byte shown, its readers' words aside,
is committed text of HEAD's tree or the build's commit history, which after a same-tree ref move can hold commits
HEAD's history lacks (round 6, F9).
(b) Nothing is shown unless the build's tree is HEAD's: tree-after-reset (`git reset --mixed` and `--soft` after
a build: nothing, the record says tree), same-tree-move (push_clean's ref move to a commit with HEAD's tree: the packs
stay), head-unresolved (an unborn branch, no repository, a git that does not answer), and the class test through the
REAL patched post-commit hook (`reset_scenario`: both resets and the ledger line they uncommit, and the same-tree ref
move), whose leak control turns the tree check off so each canary shows. (a) A pack's symbols are the committed blob's
own ast: committed-symbols (the real code-map builder over a working copy with an uncommitted def), legacy-symbols (a
pack whose symbols came from a graph is withheld), late-code-pack (a code pack of an older commit's blob), and the real
refresh after graft indexed a canary. The surface that went: no-graph-text plants a canary in every graph field and none
shows; registry-screens shows a row only from the build's committed screen. A build replaces its record with one that
names no tree before it changes any pack, and the reader reads the record again after the parts: build-in-flight (a
Read while a build of the undone commit runs, after a reset) and record-rechecked (a build that begins between the two
reads) show nothing. Every build's record carries its own random id: record-rebuilt (two builds between the reads, the
second of the commit the record names, both 0 ms long) shows nothing.

Round 6 (VERIFY-K2-RS's follow-ups, task #420, D-120): registry-committed (F1: a registry row comes from the committed
blob, never the working copy), head-unresolved's record with no tree beside a git that fails (F2), cli-label (F3: the
code map's lookup and demo CLIs label a text the hook would not show), foreign-git-dir (F4: a GIT_DIR its caller left
set never picks the reader's HEAD), deep-chain (F5: one bad file never ends a code-map build), no-symbols-lines (F6: a
file with no symbols says why) and recover (F15: the SessionStart reset starts one build after a build that crashed
after its marker, never beside a live one). The verifier's two surviving mutants are here by name.
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
import sys
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


def committed_blob(repo, commit_id, rel):
    """`rel`'s blob id in `commit_id`'s tree, or None when that tree holds no blob there or there is no such commit
    (git's own answer)."""
    r = subprocess.run(["git", "ls-tree", "-z", commit_id, "--", rel], cwd=repo, capture_output=True, text=True,
                       timeout=60)
    head, _, path = r.stdout.rstrip("\0").partition("\t")
    return head.split()[2] if r.returncode == 0 and path == rel and head.split()[1:2] == ["blob"] else None


SCREENS = ("scripts/ap_screen.py", ".claude/hooks/edit-snapshot.py")     # codemap.SCREENS: the registry screen's files


def plant_code_pack(repo, rel, commit_id):
    """A code-map pack of `rel` in codemap.py's format (schema 1) as its builder writes one at `commit_id` since the
    re-scope (K2, D-117): the symbols from the AST of the file's bytes (`symbols_from: "ast"`), their blob, one
    registry row with the blob ids of the screen files as they are here (`0` * 40 for one that is absent), and graph
    sections that no reader shows (a GitNexus caller and risk per symbol, a code-review-graph test). The builder
    reads the committed blob: a pack planted from a working copy that differs from `commit_id` stands for a pack of
    other bytes."""
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
    screens = {p: git(repo, "hash-object", "--", p).strip() if (repo / p).is_file() else "0" * 40 for p in SCREENS}
    pack = {"schema": 1, "path": rel, "language": "python", "blob": git(repo, "hash-object", "--", rel).strip(),
            "sha256": sha, "lines": data.count(b"\n"), "bytes": len(data), "commit": commit_id,
            "symbols_from": "ast", "parsed": True, "caller_files": [],
            "instruments": {"graft": dict(fresh), "gitnexus": dict(fresh, indexed_commit=commit_id, symbols=len(syms),
                                                                   unmatched=[]),
                            "code-review-graph": dict(fresh, tests_found=1),
                            "ap_screen": {"status": "ok", "rows_screened": 1, "screens": screens}},
            "symbols": syms, "tests": [{"file": "tests/test_alpha.py", "line": 3, "name": "test_helper",
                                        "indirect": False}],
            "registry": [{"row": "AF-AP-9", "line": 2, "text": "import os", "message": "a fixture row"}],
            "built_at": "2026-01-01T00:00:00Z", "timing": {}}
    p = repo / ".jev" / "codemap" / (rel + ".json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(pack, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return pack


def fixture(tmp, fp_text=None, cm_text=None):
    """(repo, commit ids): the tree committed at c1, briefs A to D one commit each (c2 to c5), then three commits to
    scripts/alpha.py (c6 to c8); the tooling copied in (with `fp_text` / `cm_text` as filepacks.py / codemap.py when
    given: a mutant), never committed; alpha's code pack planted."""
    repo = tmp / "repo"
    repo.mkdir()
    repo = repo.resolve()
    git(repo, "init", "-q")
    for rel, src in TOOLING.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, repo / rel)
    if fp_text is not None:
        (repo / "scripts" / "filepacks.py").write_text(fp_text, encoding="utf-8")
    if cm_text is not None:
        (repo / "scripts" / "codemap.py").write_text(cm_text, encoding="utf-8")
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
    """AF-AP-175: every read names the commit the build was given, never HEAD; so does the tree it records (the
    reader's check, D-117)."""
    ledger = (repo / LEDGER).read_text(encoding="utf-8")
    later = commit(repo, {LEDGER: ledger + "a later line naming scripts/beta.py\n"}, "a later ledger", 9)
    fp = load(repo)
    rec = fp.build(repo, st, sha=ids["fourth"])
    assert rec["commit"] == ids["fourth"]
    assert rec["tree"] == git(repo, "rev-parse", ids["fourth"] + "^{tree}").strip(), \
        "the build recorded another commit's tree"
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
    assert b.get("tree") == git(repo, "rev-parse", "HEAD^{tree}").strip(), "the build recorded no tree: %s" % b
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


def check_stale_code(repo, st, ids, tmp):
    """An uncommitted edit (HEAD's tree unchanged since the build): the code part is the committed blob's and goes out
    with the code map's STALE mark, or not at all when the mark does not fit; the pack's lines are the build's. (A
    commit after the build shows nothing at all: tree-after-reset and the class test.)"""
    build(repo, st)
    alpha = (repo / "scripts" / "alpha.py").read_text()
    (repo / "scripts" / "alpha.py").write_text(alpha + "# rev 5\n", encoding="utf-8")
    lines = context(run(repo, st, read(repo, "scripts/alpha.py"))).split("\n")
    assert any(x.startswith("filepack scripts/alpha.py @%s: ledger 5 · " % ids["fourth"][:7]) for x in lines), \
        "the pack's lines were not read: %s" % lines
    assert lines[0].startswith("codemap scripts/alpha.py — 5 symbols") and lines[1].startswith(
        "STALE: the file changed since this pack was built"), "a stale code pack passed as fresh: %s" % lines[:2]
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
    """F1's stale boundary: the untracking commit changed HEAD's tree after the build, so nothing is shown (the record
    says tree); the canary's code pack, of bytes no commit holds, would be left out by the blob check as well."""
    canary = untrack_with_a_canary(repo, st)
    assert "\nscripts/gamma.py\n" in (st / "filepacks" / "TRACKED.txt").read_text(), "not F1's stale boundary"
    assert canary in (repo / ".jev" / "codemap" / "scripts" / "gamma.py.json").read_text(), "no canary in the pack"
    for p in gamma_probes(repo, "p6"):
        ctx = context(run(repo, st, p))
        assert canary not in ctx and canary[4:] not in ctx, "the untracked file's text reached the model"
        assert ctx == "", "the packs of a tree that is not HEAD's reached the model: %r" % ctx[:80]
        assert records(st)[-1]["skipped"] == [{"key": "file:scripts/gamma.py", "why": "tree"}], records(st)[-1]


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


# ---------- round 3: the verifier's seven checks (B1 went with the callers and tests; B2 is now (a)) ----------

def alter_pack(repo, change):
    """Apply `change` (a function of the pack) to alpha's planted code pack."""
    p = repo / ".jev" / "codemap" / "scripts" / "alpha.py.json"
    pk = json.loads(p.read_text(encoding="utf-8"))
    change(pk)
    p.write_text(json.dumps(pk, indent=1, sort_keys=True) + "\n", encoding="utf-8")


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


# ---------- K2 RE-SCOPE (D-117): (b) nothing unless the build's tree is HEAD's; (a) the blob's own symbols ----

def check_tree_after_reset(repo, st, ids, tmp):
    """VERIFY-K2-R4's R4-1 on built packs: a commit adds a ledger line naming scripts/beta.py and a def to
    scripts/alpha.py, a canary each, and a build follows; `git reset --mixed HEAD~1` moves HEAD back and runs no hook,
    so the packs describe the undone commit: nothing is shown, and the record says tree. The same after the commit is
    made again, built, and undone by `git reset --soft HEAD~1`. Before each reset the canaries show (the control)."""
    cn = "rs" + secrets.token_hex(5)
    led, alpha = (repo / LEDGER).read_text(), (repo / "scripts" / "alpha.py").read_text()
    changed = {LEDGER: led + "**T9 HOME.** %s: a line naming scripts/beta.py\n" % cn,
               "scripts/alpha.py": alpha + "\n\ndef leak_%s(x):\n    return x\n" % cn}
    for k, mode in enumerate(("--mixed", "--soft")):
        head = commit(repo, changed, "canaries", 9 + k)
        plant_code_pack(repo, "scripts/alpha.py", head)
        build(repo, st)
        probes = [read(repo, "scripts/beta.py", sid="tr%d-b" % k), read(repo, "scripts/alpha.py", sid="tr%d-a" % k)]
        assert all(cn in context(run(repo, st, p)) for p in probes), "the control: a committed canary was not shown"
        git(repo, "reset", "-q", mode, "HEAD~1")
        for p in probes:
            p = dict(p, session_id=p["session_id"] + "-after")
            ctx = context(run(repo, st, p))
            assert cn not in ctx and ctx == "", "a byte HEAD's tree does not hold reached the model: %r" % ctx[:120]
            rel = p["tool_input"]["file_path"][len(str(repo)) + 1:]
            assert records(st)[-1]["skipped"] == [{"key": "file:" + rel, "why": "tree"}], records(st)[-1]


def check_same_tree_move(repo, st, ids, tmp):
    """scripts/push_clean.sh:69-72 moves the branch to a commit with the same tree (its rewrite) and runs no hook: the
    packs describe that tree, so they still show (trees, not commits)."""
    build(repo, st)
    head = git(repo, "rev-parse", "HEAD").strip()
    new = git(repo, "commit-tree", "HEAD^{tree}", "-p", "HEAD~1", "-m", "rewritten", k=9).strip()
    git(repo, "update-ref", git(repo, "symbolic-ref", "HEAD").strip(), new)
    assert git(repo, "rev-parse", "HEAD").strip() == new != head and git(repo, "rev-parse", "HEAD^{tree}") == git(
        repo, "rev-parse", head + "^{tree}"), "not the case: a same-tree ref move"
    assert json.loads((st / "filepacks" / "BUILD.json").read_text())["commit"] == head, "not the case: a build before"
    for k, p in enumerate((read(repo, "scripts/alpha.py", sid="st0"), read(repo, "docs/NOTE.md", sid="st1"))):
        ctx = context(run(repo, st, p))
        assert ctx.startswith(("codemap scripts/alpha.py — ", "filepack docs/NOTE.md @")[k]), \
            "the packs of HEAD's tree were not shown after a same-tree ref move: %r" % ctx[:80]


def check_head_unresolved(repo, st, ids, tmp):
    """A HEAD that cannot be resolved shows nothing: an unborn branch, no repository (.git moved away; the search stops
    at the repo's parent), a git that does not answer within HEAD_TIMEOUT (a `git` first on PATH that sleeps: the real
    one cannot be made to hang on demand), and a git that fails beside a record that names no tree (a build's from before
    the check, and a marker; VERIFY-K2-RS F2: None equals None); a HEAD that resolves shows (the control, before and
    after)."""
    build(repo, st)
    env = dict(env_for(repo, st), GIT_CEILING_DIRECTORIES=str(repo.parent))
    assert context(run(repo, st, read(repo, "docs/NOTE.md", sid="hu0"), env=env)), "the control: a HEAD that resolves"
    ref = git(repo, "symbolic-ref", "HEAD").strip()
    git(repo, "symbolic-ref", "HEAD", "refs/heads/k2-unborn")
    try:
        ctx = context(run(repo, st, read(repo, "docs/NOTE.md", sid="hu1"), env=env))
    finally:
        git(repo, "symbolic-ref", "HEAD", ref)
    assert ctx == "", "an unresolved HEAD showed a pack (an unborn branch): %r" % ctx[:80]
    os.rename(repo / ".git", tmp / "dotgit-away")
    try:
        ctx = context(run(repo, st, read(repo, "docs/NOTE.md", sid="hu2"), env=env))
    finally:
        os.rename(tmp / "dotgit-away", repo / ".git")
    assert ctx == "", "an unresolved HEAD showed a pack (no repository): %r" % ctx[:80]
    shim = tmp / "slow-git"
    shim.mkdir()
    (shim / "git").write_text("#!/bin/sh\nexec sleep 30\n")
    (shim / "git").chmod(0o755)
    t0 = time.monotonic()
    ctx = context(run(repo, st, read(repo, "docs/NOTE.md", sid="hu3"), env=dict(env, PATH="%s:%s" % (
        shim, env["PATH"])), timeout=25))
    assert ctx == "" and time.monotonic() - t0 < 15, "an unresolved HEAD showed a pack (a git that does not answer)"
    path = st / "filepacks" / "BUILD.json"            # VERIFY-K2-RS F2: a record with no tree and a git that fails
    raw = path.read_bytes()
    old = {k: v for k, v in json.loads(raw).items() if k not in ("tree", "id")}      # a record from before the check
    shim = tmp / "failing-git"
    shim.mkdir()
    (shim / "git").write_text("#!/bin/sh\nexit 128\n")
    (shim / "git").chmod(0o755)
    try:
        for k, rec in enumerate((old, {"schema": 1, "commit": old["commit"], "building": True})):     # and a marker
            path.write_text(json.dumps(rec, sort_keys=True) + "\n")
            ctx = context(run(repo, st, read(repo, "docs/NOTE.md", sid="hu5%d" % k), env=dict(env, PATH="%s:%s" % (
                shim, env["PATH"]))))
            assert ctx == "", "a record with no tree and a git that fails showed a pack: %r" % ctx[:80]
    finally:
        path.write_bytes(raw)
    assert context(run(repo, st, read(repo, "docs/NOTE.md", sid="hu4"), env=env)), "the control: after"


def check_late_code_pack(repo, st, ids, tmp):
    """The code map's refresh waits on the graph re-indexes, so it can lag the file-pack build: a code pack of
    alpha.py's blob at an older commit, whose def a later commit removed, is left out (`blob`) and the pack's lines show
    alone; once the code pack is of the build's blob it shows (the control)."""
    cn = "lc" + secrets.token_hex(5)
    alpha = (repo / "scripts" / "alpha.py").read_text()
    old = commit(repo, {"scripts/alpha.py": alpha + "\n\ndef old_%s(x):\n    return x\n" % cn}, "an old def", 9)
    plant_code_pack(repo, "scripts/alpha.py", old)
    commit(repo, {"scripts/alpha.py": alpha}, "the old def removed", 10)
    build(repo, st)
    ctx = context(run(repo, st, read(repo, "scripts/alpha.py", sid="lc0")))
    assert cn not in ctx, "a code pack of another blob reached the model"
    assert ctx.startswith("filepack scripts/alpha.py @"), ctx[:80]
    assert records(st)[-1]["injected"][0].get("code_skip") == "blob", records(st)[-1]["injected"]
    plant_code_pack(repo, "scripts/alpha.py", git(repo, "rev-parse", "HEAD").strip())
    ctx = context(run(repo, st, read(repo, "scripts/alpha.py", sid="lc1")))
    assert ctx.startswith("codemap scripts/alpha.py — 5 symbols"), "the control: the build's blob: %r" % ctx[:80]


def codemap_build(repo, tmp, *rels):
    """The REAL code-map builder of the fixture (`codemap.py build`), no graph on PATH (their sections say absent)."""
    r = subprocess.run([sys.executable, "scripts/codemap.py", "build", *rels], cwd=repo, capture_output=True,
                       text=True, timeout=120, env={"PATH": "/usr/bin:/bin", "HOME": str(tmp), "LANG": "C.UTF-8",
                                                    "PYTHONDONTWRITEBYTECODE": "1"})
    assert r.returncode == 0, (r.stdout[-400:], r.stderr[-400:])
    return r.stdout


def check_committed_symbols(repo, st, ids, tmp):
    """D-117 (a): the real code-map builder over a working copy of alpha.py that holds an uncommitted def with a canary.
    The pack describes the committed blob, so the canary never reaches the model on Edit, Read or cat; the committed
    symbols do (the control: helper's entry on the Edit, the symbols on the Read), with the STALE mark."""
    cn = "cs" + secrets.token_hex(5)
    with open(repo / "scripts" / "alpha.py", "a", encoding="utf-8") as f:
        f.write("\n\ndef leak_%s(token='%s-arg'):\n    return token\n" % (cn, cn))
    out = codemap_build(repo, tmp, "scripts/alpha.py")
    assert out.startswith("built scripts/alpha.py "), "not the real builder: %r" % out[-300:]
    build(repo, st)
    probes = [edit(repo, "scripts/alpha.py", "    return x + 1", sid="cs0"), read(repo, "scripts/alpha.py", sid="cs1"),
              bash(repo, "cat scripts/alpha.py", sid="cs2")]
    for k, p in enumerate(probes):
        ctx = context(run(repo, st, p))
        assert cn not in ctx, "an uncommitted symbol reached the model"
        assert ctx.startswith(("codemap scripts/alpha.py:6 — function helper L5-6 · def helper(x)",
                               "codemap scripts/alpha.py — 5 symbols", "codemap scripts/alpha.py — 5 symbols")[k]) \
            and "\nSTALE: the file changed" in ctx, "the control: the committed symbols: %r" % ctx[:120]


def check_legacy_symbols(repo, st, ids, tmp):
    """D-117 (a): a code pack whose symbols came from a graph (a code map from before the re-scope: symbols_from graft,
    code-review-graph or none) is left out (`symbols`) and the pack's lines show alone, even with the build's blob; the
    builder's own marker shows (the control, with the same planted symbol)."""
    build(repo, st)
    cn = "lg" + secrets.token_hex(5)
    alter_pack(repo, lambda pk: pk["symbols"].append(dict(pk["symbols"][0], name=cn, qualname=cn, start=16, end=16)))
    for k, src in enumerate(("graft", "code-review-graph", None, "ast")):
        alter_pack(repo, lambda pk: pk.update(symbols_from=src))
        ctx = context(run(repo, st, read(repo, "scripts/alpha.py", sid="lg%d" % k)))
        if src == "ast":
            assert cn in ctx, "the control: the builder's marker was left out: %r" % ctx[:120]
            break
        assert cn not in ctx and ctx.startswith("filepack scripts/alpha.py @"), \
            "a code part whose symbols came from a graph reached the model: %r" % ctx[:80]
        assert records(st)[-1]["injected"][0].get("code_skip") == "symbols", records(st)[-1]["injected"]


def check_no_graph_text(repo, st, ids, tmp):
    """The callers-and-tests surface went (K2 RE-SCOPE): a canary in every graph field of alpha's code pack (per symbol
    a caller's name and file, its counts and risk; the file's tests and caller files; each graph section's state and
    note) shows on none of an Edit in a symbol, an Edit at module level, a Read range, a whole Read and cat, and no line
    names a risk, a caller, a test or an instrument; the symbols show (the control)."""
    build(repo, st)
    cn = "ng" + secrets.token_hex(5)

    def change(pk):
        for s in pk["symbols"]:
            s["gitnexus"] = {"id": "x", "risk": "HIGH" + cn, "impacted": 912345, "direct": 912346, "callers": {
                "count": 912347, "tests": 912348,
                "sample": [{"name": "c" + cn, "file": "scripts/%s.py" % cn, "line": 3}]}}
        pk["tests"] = [{"file": "tests/test_%s.py" % cn, "line": 1, "name": "test_" + cn, "indirect": False}]
        pk["caller_files"] = ["scripts/%s.py" % cn]
        for g in ("graft", "gitnexus", "code-review-graph"):
            pk["instruments"][g].update(graph="stale", note=cn)
    alter_pack(repo, change)
    probes = [edit(repo, "scripts/alpha.py", "    return x + 1", sid="ng0"), edit(repo, "scripts/alpha.py", "import os",
                                                                              sid="ng1"),
              read(repo, "scripts/alpha.py", sid="ng2", offset=9, limit=6), read(repo, "scripts/alpha.py", sid="ng3"),
              bash(repo, "cat scripts/alpha.py", sid="ng4")]
    for p in probes:
        ctx = context(run(repo, st, p))
        assert ctx.startswith("codemap scripts/alpha.py"), "the control: no code part: %r" % ctx[:80]
        lines = ctx.split("\n")
        assert cn not in ctx and "91234" not in ctx and not any(ln.startswith((
            "risk", "callers", "tests of the file", "instruments:")) for ln in lines), \
            "a graph's caller, test, count or state reached the model: %r" % ctx[:300]


def check_registry_screens(repo, st, ids, tmp):
    """A registry row carries its id and message from the screen's table: it shows only when the screen the code map ran
    (its recorded blobs of scripts/ap_screen.py and .claude/hooks/edit-snapshot.py) is the build's committed one. Both
    committed and recorded: the row shows (the control); a pack recorded over an uncommitted edit of either file (a
    canary in the row's message): the row is left out, and the code part stays."""
    commit(repo, {SCREENS[0]: "# the screen's code, a fixture\n", SCREENS[1]: "AP_SCREEN = []\n"}, "the screen", 9)
    plant_code_pack(repo, "scripts/alpha.py", git(repo, "rev-parse", "HEAD").strip())
    build(repo, st)
    lines = context(run(repo, st, edit(repo, "scripts/alpha.py", "import os", sid="rg0"))).split("\n")
    assert "registry rows here 1: AF-AP-9 :2 import os — a fixture row" in lines, "the control: the row: %s" % lines
    for k, rel in enumerate(SCREENS):
        cn = "rg" + secrets.token_hex(5)
        before = (repo / rel).read_text()
        (repo / rel).write_text(before + "# %s\n" % cn)
        blob = git(repo, "hash-object", "--", rel).strip()
        (repo / rel).write_text(before)

        def change(pk):
            pk["instruments"]["ap_screen"]["screens"][rel] = blob
            pk["registry"][0]["message"] = cn
        alter_pack(repo, change)
        ctx = context(run(repo, st, edit(repo, "scripts/alpha.py", "import os", sid="rg%d" % (k + 1))))
        assert ctx.startswith("codemap scripts/alpha.py:2 — module level"), "the control: no code part: %r" % ctx[:80]
        assert cn not in ctx and "AF-AP-9" not in ctx, \
            "a registry row from a screen the build does not hold reached the model: %r" % ctx[:200]
        plant_code_pack(repo, "scripts/alpha.py", git(repo, "rev-parse", "HEAD").strip())


def check_build_in_flight(repo, st, ids, tmp):
    """A build rewrites the packs before it writes its record, so while it runs the record is the last build's: the
    build replaces the record with one that names no tree before it changes any pack. The case: a build at the fixture's
    head; a commit adds a ledger line naming scripts/beta.py with a canary; `git reset --soft HEAD~1` puts HEAD back on
    the built tree; a build at the undone commit (as its post-commit hook launched it) runs, and a Read of
    scripts/beta.py is made the moment its packs are written (at its BLOBS.txt write). Nothing is shown and the record
    says tree, while the pack on disk holds the canary (else: not the case)."""
    build(repo, st)
    cn = "bf" + secrets.token_hex(5)
    head = commit(repo, {LEDGER: (repo / LEDGER).read_text() + "**T9 HOME.** %s: a line naming scripts/beta.py\n" % cn},
                  "a canary line", 9)
    git(repo, "reset", "-q", "--soft", "HEAD~1")
    fp, seen = load(repo), {}
    real, n = fp._write, len(records(st))

    def probe(path, raw):
        if path.endswith("BLOBS.txt") and not seen:
            seen["pack"] = cn in (st / "filepacks" / "scripts" / "beta.py.json").read_text()
            seen["ctx"] = context(run(repo, st, read(repo, "scripts/beta.py", sid="bf0")))
            seen["recs"] = records(st)[n:]
        return real(path, raw)
    fp._write = probe
    fp.build(repo, st, sha=head)
    assert seen.get("pack"), "not the case: the build had not written the canary's pack: %s" % seen
    assert cn not in seen["ctx"] and seen["ctx"] == "", \
        "a byte HEAD's tree does not hold reached the model (a build in flight): %r" % seen["ctx"][:120]
    assert [r["skipped"] for r in seen["recs"]] == [[{"key": "file:scripts/beta.py", "why": "tree"}]], seen["recs"]


def check_record_rechecked(repo, st, ids, tmp):
    """The record is read before the parts and again after them: a build that began in between (it replaces the record
    first) may have rewritten a part, so the parts go (tree). In process: the entry of scripts/alpha.py, with a
    build's first write (a record with no tree) landing right after the reader's P2 read; the same entry with no build
    between shows the code part (the control)."""
    build(repo, st)
    fp = load(repo)
    e = fp.entry("scripts/alpha.py", {}, packs=fp.Packs(repo, st))
    assert e["text"].startswith("codemap scripts/alpha.py — "), "the control: %r" % e["text"][:80]
    path = st / "filepacks" / "BUILD.json"
    raw, real = path.read_bytes(), fp._p2_lines

    def p2(rel, packs):
        out = real(rel, packs)
        path.write_text(json.dumps({"schema": 1, "commit": "0" * 40, "building": True}) + "\n")
        return out
    fp._p2_lines = p2
    try:
        e = fp.entry("scripts/alpha.py", {}, packs=fp.Packs(repo, st))
    finally:
        path.write_bytes(raw)
    assert e["text"] == "" and e["skip"] == "tree", \
        "a part read while a build began reached the model: %r" % e["text"][:120]


def check_record_rebuilt(repo, st, ids, tmp):
    """Two builds while the parts are read, another commit's and then HEAD's again, each taking 0 ms (the module's
    clock is held): the record ends with the fields it began with, and the part read between was the other commit's.
    Its id tells the two HEAD builds apart, so nothing shows. The case: a build at the fixture's head; a commit adds a
    ledger line naming scripts/beta.py with a canary; `git reset --soft HEAD~1`; builds of that commit and of HEAD; the
    entry of scripts/beta.py, with both builds run around the reader's P2 read (it holds the canary, else not the case).
    The entry with no build between shows the pack (the control)."""
    build(repo, st)
    cn = "rb" + secrets.token_hex(5)
    line = "**T9 HOME.** %s: a line naming scripts/beta.py\n" % cn
    other = commit(repo, {LEDGER: (repo / LEDGER).read_text() + line}, "a canary line", 9)
    git(repo, "reset", "-q", "--soft", "HEAD~1")
    fp = load(repo)

    class Clock:                                         # the module's clock: every build is 0 ms long
        monotonic = staticmethod(lambda: 0.0)

        def __getattr__(self, name):
            return getattr(time, name)
    fp.time = Clock()
    fp.build(repo, st, sha=other)
    fp.build(repo, st)                                   # HEAD's after the other commit's: the record the reader reads
    e = fp.entry("scripts/beta.py", {}, packs=fp.Packs(repo, st))
    assert e["text"].startswith("filepack scripts/beta.py @") and cn not in e["text"], "the control: %r" % e["text"]
    path, real, seen = st / "filepacks" / "BUILD.json", fp._p2_lines, {}

    def p2(rel, packs):
        fp.build(repo, st, sha=other)
        out = real(rel, packs)
        seen["read"] = "\n".join(out)
        fp.build(repo, st)
        return out
    fp._p2_lines = p2
    before = json.loads(path.read_text())
    e = fp.entry("scripts/beta.py", {}, packs=fp.Packs(repo, st))
    after = json.loads(path.read_text())
    assert cn in seen.get("read", ""), "not the case: the part read was not the other commit's: %s" % seen
    assert dict(before, id=None) == dict(after, id=None), "not the case: the record changed more than its id"
    assert cn not in e["text"] and e["text"] == "" and e["skip"] == "tree", \
        "a part another build wrote reached the model (two builds while the parts were read): %r" % e["text"][:120]


# ---------- round 6: VERIFY-K2-RS's follow-ups (task #420, D-120) ----------

def check_registry_committed(repo, st, ids, tmp):
    """VERIFY-K2-RS F1: a registry row comes from the committed blob, never from the working copy. The repo's own screen
    committed, alpha.py commits a line the AF-AP-175 screen hits; after that commit a working-copy line the screen hits
    too, with a canary. The real code-map build, then the file-pack build and the hook: an Edit on the canary line shows
    the code part and no byte of that line; an Edit on the committed line shows its row, at its committed line (the
    control)."""
    commit(repo, {rel: (ROOT / rel).read_text(encoding="utf-8") for rel in SCREENS}, "the screen", 9)
    alpha = (repo / "scripts" / "alpha.py").read_text().replace(
        "    return Box(os.getpid()).get()", '    ref = "HEAD"  # the committed hit\n    return Box(os.getpid()).get()')
    commit(repo, {"scripts/alpha.py": alpha}, "a committed hit", 10)
    cn = "rw" + secrets.token_hex(5)
    line = '    leak = "%s" + "HEAD"' % cn
    (repo / "scripts" / "alpha.py").write_text(alpha.replace("    return x + 1", line + "\n    return x + 1"))
    out = codemap_build(repo, tmp, "scripts/alpha.py")
    assert out.startswith("built scripts/alpha.py "), "not the real builder: %r" % out[-300:]
    build(repo, st)
    ctx = context(run(repo, st, edit(repo, "scripts/alpha.py", line, sid="rw0")))
    assert cn not in ctx and "leak = " not in ctx, \
        "an uncommitted line reached the model through a registry row: %r" % ctx[:300]
    assert ctx.startswith("codemap scripts/alpha.py:6 — function helper L5-6 · def helper(x)"), \
        "the control: no code part on the canary line: %r" % ctx[:120]
    ctx = context(run(repo, st, edit(repo, "scripts/alpha.py", '    ref = "HEAD"  # the committed hit', sid="rw1")))
    assert 'registry rows here 1: AF-AP-175 :18 ref = "HEAD"  # the committed hit — ' in ctx, \
        "the control: the committed line's row: %r" % ctx[:300]


def codemap_cli(repo, st, *args):
    """The fixture's code-map dev CLI (`codemap.py lookup` or `demo`) with the file-pack state `st`: its output lines."""
    r = subprocess.run([sys.executable, "scripts/codemap.py", *args], cwd=repo, capture_output=True, text=True,
                       timeout=60, env={"PATH": "/usr/bin:/bin", "HOME": str(repo.parent), "LANG": "C.UTF-8",
                                        "PYTHONDONTWRITEBYTECODE": "1", "AF_FILEPACKS_STATE": str(st)})
    assert r.returncode == 0, (r.stdout[-400:], r.stderr[-400:])
    return r.stdout.split("\n")


LABEL = "codemap: NOT HEAD's committed code (%s): "


def check_cli_label(repo, st, ids, tmp):
    """VERIFY-K2-RS F3: `codemap.py lookup` and `demo` run the checks the hook runs before it shows a code part, and
    when one fails their first line says the text is not HEAD's committed code and names it; the rest prints as without
    it. A commit adds a def with a canary to alpha.py, its code pack and a build follow: at HEAD's tree neither CLI
    prints a label (the control); after `git reset --mixed HEAD~1` and, the commit made again, after `git reset --hard
    HEAD~1`, both print the tree label, then the undone commit's symbol. Then a build of HEAD's tree beside that code
    pack (blob), the pack of HEAD's blob (no label), and its symbols from a graph (symbols)."""
    cn = "cl" + secrets.token_hex(5)
    new = (repo / "scripts" / "alpha.py").read_text() + "\n\ndef leak_%s(x):\n    return x\n" % cn
    at = str(new.count("\n") - 1)                                # the canary def's line
    payload = tmp / "edit.json"
    payload.write_text(json.dumps(edit(repo, "scripts/alpha.py", "    return x + 1")))
    sym = "codemap scripts/alpha.py:%s — function leak_%s" % (at, cn)

    def outs():
        return (codemap_cli(repo, st, "lookup", "scripts/alpha.py", "--line", at),
                codemap_cli(repo, st, "demo", str(payload)))
    for k, mode in enumerate(("--mixed", "--hard")):
        head = commit(repo, {"scripts/alpha.py": new}, "a canary def", 9 + k)
        plant_code_pack(repo, "scripts/alpha.py", head)
        build(repo, st)
        lk, dm = outs()
        assert lk[0].startswith(sym) and dm[0] == "old_string at: L6-6", \
            "the control: at HEAD's tree a CLI printed a label: %r %r" % (lk[:2], dm[:2])
        git(repo, "reset", "-q", mode, "HEAD~1")
        lk, dm = outs()
        assert lk[0].startswith(LABEL % "tree") and dm[0].startswith(LABEL % "tree"), \
            "a CLI printed a pack of another tree without the label: %r %r" % (lk[:2], dm[:2])
        assert lk[1].startswith(sym) and dm[1:3] == ["old_string at: L6-6", "enclosing: helper"], \
            "the text after the label is not the text without it: %r %r" % (lk[:3], dm[:3])
    build(repo, st)                                  # HEAD's tree; alpha's code pack is still the undone commit's
    lk = codemap_cli(repo, st, "lookup", "scripts/alpha.py", "--line", "6")
    assert lk[0].startswith(LABEL % "blob"), "a CLI printed a pack of another blob without the label: %r" % lk[:2]
    plant_code_pack(repo, "scripts/alpha.py", ids["fourth"])
    lk = codemap_cli(repo, st, "lookup", "scripts/alpha.py", "--line", "6")
    assert lk[0].startswith("codemap scripts/alpha.py:6 — function helper L5-6"), "the control: %r" % lk[:2]
    alter_pack(repo, lambda pk: pk.update(symbols_from="graft"))
    lk = codemap_cli(repo, st, "lookup", "scripts/alpha.py", "--line", "6")
    assert lk[0].startswith(LABEL % "symbols"), "a CLI printed a graph's symbols without the label: %r" % lk[:2]


def check_foreign_git_dir(repo, st, ids, tmp):
    """VERIFY-K2-RS F4: the reader resolves HEAD in this repository, whatever GIT_* variable its caller left set. A
    commit adds a ledger line naming scripts/beta.py with a canary; a clone takes that commit; a build follows, and
    `git reset --mixed HEAD~1` undoes the commit here: the clone's HEAD has the build's tree, this repository's has not.
    With GIT_DIR naming the clone, nothing shows and the record says tree. The leak control: a git that reads the clone
    whatever its environment (a shim first on PATH) shows the canary. (GIT_COMMON_DIR, GIT_WORK_TREE or GIT_INDEX_FILE
    alone did not move the PIN's HEAD: measured, so none is a case here.)"""
    cn = "fg" + secrets.token_hex(5)
    commit(repo, {LEDGER: (repo / LEDGER).read_text() + "**T9 HOME.** %s: a line naming scripts/beta.py\n" % cn},
           "a canary line", 9)
    clone = tmp / "clone"
    git(tmp, "clone", "-q", str(repo), str(clone))
    build(repo, st)
    git(repo, "reset", "-q", "--mixed", "HEAD~1")
    tree = json.loads((st / "filepacks" / "BUILD.json").read_text())["tree"]
    assert git(clone, "rev-parse", "HEAD^{tree}").strip() == tree != git(repo, "rev-parse", "HEAD^{tree}").strip(), \
        "not the case: the clone's HEAD has the build's tree and this HEAD has another"
    env = env_for(repo, st)
    ctx = context(run(repo, st, read(repo, "scripts/beta.py", sid="fg0"), env=dict(env, GIT_DIR=str(clone / ".git"))))
    assert cn not in ctx and ctx == "", "a foreign GIT_DIR's HEAD decided what shows: %r" % ctx[:120]
    assert records(st)[-1]["skipped"] == [{"key": "file:scripts/beta.py", "why": "tree"}], records(st)[-1]
    shim = tmp / "foreign-git"
    shim.mkdir()
    (shim / "git").write_text('#!/bin/sh\nGIT_DIR=%s exec %s "$@"\n' % (clone / ".git", shutil.which("git")))
    (shim / "git").chmod(0o755)
    ctx = context(run(repo, st, read(repo, "scripts/beta.py", sid="fg9"), env=dict(env, PATH="%s:%s" % (
        shim, env["PATH"]))))
    assert cn in ctx, "the control: a git that reads the clone did not show the canary: %r" % ctx[:120]


LONG_NAME = "scripts/" + "n" * 245 + ".py"      # its pack's temporary file name is past NAME_MAX (255): the write raises


def check_deep_chain(repo, st, ids, tmp):
    """VERIFY-K2-RS F5: one bad file never ends a code-map build. One real `codemap.py build` of four committed files,
    alpha.py last: a 20,000-deep unary chain (its parse raises MemoryError on Python 3.11, 3.12 and 3.13, measured), a
    1,500-deep one with a def after it (it parses; a walk into its expressions raises RecursionError) and a file whose
    pack cannot be written (LONG_NAME). The build exits 0, alpha.py gets its pack and symbols, each chain its pack
    (the deep one with no symbols and `parsed` false), and the long name is `failed`, with its reason on stderr."""
    deep, mid = "scripts/chain_deep.py", "scripts/chain_mid.py"
    commit(repo, {deep: "x = " + "-" * 20000 + "1\n", mid: "x = " + "-" * 1500 + "1\n\n\ndef after():\n    return 1\n",
                  LONG_NAME: "def f():\n    return 1\n"}, "deep files", 9)
    r = subprocess.run([sys.executable, "scripts/codemap.py", "build", deep, mid, LONG_NAME, "scripts/alpha.py"],
                       cwd=repo, capture_output=True, text=True, timeout=120,
                       env={"PATH": "/usr/bin:/bin", "HOME": str(tmp), "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"})
    assert r.returncode == 0, "one bad file ended the code-map build: rc %d %r" % (r.returncode, r.stderr[-300:])
    out = r.stdout.split("\n")
    assert out[3].startswith("built scripts/alpha.py 5 symbols") and out[2] == "failed " + LONG_NAME, out[:4]
    assert "codemap: %s failed: OSError: " % LONG_NAME in r.stderr, r.stderr[-300:]
    got = {}
    for rel in (deep, mid):
        p = repo / ".jev" / "codemap" / (rel + ".json")
        assert p.exists(), "a file whose parse fails lost its pack, not only its symbols: %s %r" % (rel, out[:2])
        pk = json.loads(p.read_text(encoding="utf-8"))
        got[rel] = (pk["parsed"], [s["qualname"] for s in pk["symbols"]])
    assert got == {deep: (False, []), mid: (True, ["after"])}, got


NO_SYMBOLS = {"scripts/broken.py": ("def broken(:\n    return 1\n", "def broken(:",
                                    "no symbols: the committed blob does not parse"),
              "scripts/run.sh": ("#!/bin/sh\necho one\necho two\n", "echo one", "no symbols for shell"),
              "scripts/consts.py": ("ONE = 1\nTWO = 2\n", "ONE = 1",
                                    "no symbols: the committed blob defines no function or class")}


def check_no_symbols_lines(repo, st, ids, tmp):
    """VERIFY-K2-RS F6: a code file with no symbols says why, never "0 symbols, 0 at top level". Three committed files
    through the real code-map build: a Python file that does not parse, a shell file, a Python file with no def. Through
    the hook, for each: a whole Read, a Read range and an Edit."""
    commit(repo, {rel: v[0] for rel, v in NO_SYMBOLS.items()}, "files with no symbols", 9)
    codemap_build(repo, tmp, *NO_SYMBOLS)
    build(repo, st)
    ctxs = []
    for k, (rel, (_, old, why)) in enumerate(NO_SYMBOLS.items()):
        ctxs.append(context(run(repo, st, read(repo, rel, sid="ns%da" % k))))
        assert ctxs[-1].startswith("codemap %s — %s  [pack " % (rel, why)), \
            "a file with no symbols did not say why (a whole Read): %r" % ctxs[-1][:120]
        ctxs.append(context(run(repo, st, read(repo, rel, sid="ns%db" % k, offset=1, limit=2))))
        assert ctxs[-1].startswith("codemap %s:1-2 — %s  [pack " % (rel, why)), \
            "a file with no symbols did not say why (a Read range): %r" % ctxs[-1][:120]
        line = NO_SYMBOLS[rel][0].split("\n").index(old) + 1
        ctxs.append(context(run(repo, st, edit(repo, rel, old, sid="ns%dc" % k))))
        assert ctxs[-1].startswith("codemap %s:%d — module level (%s)  [pack " % (rel, line, why)), \
            "a file with no symbols did not say why (an Edit): %r" % ctxs[-1][:120]
    assert not any("0 symbols" in c or "0 at top level" in c for c in ctxs), ctxs


def crash_after_marker(repo, st):
    """A build that crashes after its marker (in process: its first step after the marker raises). BUILD.json is left
    the marker, and the build's lock is free."""
    fp = load(repo)

    def crash(pdir, keep):
        raise RuntimeError("a crash after the marker")
    fp._clean = crash
    with pytest.raises(RuntimeError, match="a crash after the marker"):
        fp.build(repo, st)
    rec = json.loads((st / "filepacks" / "BUILD.json").read_text())
    assert rec.get("building") is True and "tree" not in rec, "not the case: no marker left: %s" % rec


def gone(pid):
    """True once `pid` has ended (no process, or a zombie its new parent has not reaped yet)."""
    try:
        with open("/proc/%d/stat" % pid) as f:
            return f.read().rsplit(")", 1)[1].split()[0] == "Z"
    except OSError:
        return True


def wait_builds(pids, bound=60):
    deadline = time.monotonic() + bound
    for pid in pids:
        while not gone(pid):
            assert time.monotonic() < deadline, "a build the reset started ran past %d s: %s" % (bound, cmdline(pid))
            time.sleep(0.1)


def check_recover(repo, st, ids, tmp):
    """VERIFY-K2-RS F15: a build that crashed after its marker leaves the hook dark until a build writes its record. The
    SessionStart reset (the registration's command) starts one build when no build holds the lock, and none while one
    does. A build, then one that crashes after its marker (the hook shows nothing: else not the case). With the lock
    free, the reset's record says `rebuild: started`, a build writes a record with a tree, and the hook shows the pack
    again. After a second crash, with the lock held (a build in flight): `busy`, and no build process."""
    build(repo, st)
    crash_after_marker(repo, st)
    assert context(run(repo, st, read(repo, "docs/NOTE.md", sid="rv0"))) == "", "not the case: a marker still shows"
    r = run(repo, st, start("startup", sid="rv-s1"), cmd=REG_RESET)
    assert (r.returncode, r.stdout) == (0, b""), r
    rec = records(st)[-1]
    wait_builds([rec["pid"]] if "pid" in rec else [])
    assert rec.get("rebuild") == "started", "a crashed build's marker was not rebuilt at SessionStart: %s" % rec
    built = json.loads((st / "filepacks" / "BUILD.json").read_text())
    assert "tree" in built and "building" not in built, "the build it started wrote no record: %s %r" % (
        built, (st / "filepacks-recover.log").read_text()[-300:])
    assert context(run(repo, st, read(repo, "docs/NOTE.md", sid="rv1"))).startswith("filepack docs/NOTE.md @"), \
        "the hook did not show the pack again after the rebuild"
    crash_after_marker(repo, st)
    fd = os.open(st / "filepacks.lock", os.O_WRONLY | os.O_CREAT, 0o600)
    fcntl.flock(fd, fcntl.LOCK_EX)                   # a build in flight holds it
    try:
        r = run(repo, st, start("startup", sid="rv-s2"), cmd=REG_RESET)
        rec = records(st)[-1]
        procs = [p for p in fixture_processes(tmp) if "filepacks.py" in cmdline(p)]
    finally:
        os.close(fd)
    wait_builds(procs + ([rec["pid"]] if "pid" in rec else []))
    assert (r.returncode, rec.get("rebuild"), procs) == (0, "busy", []), \
        "a second build started beside a live build: %s %s" % (rec, [cmdline(p) for p in procs])

CHECKS = {"edit-once-per-symbol": check_edit_once_per_symbol, "read-range": check_read_range,
          "bash-readers": check_bash_readers, "reset": check_reset, "doc-pack-lines": check_doc_pack_lines,
          "build-lines": check_build_lines, "build-briefs-commits": check_build_briefs_commits,
          "build-sha-threaded": check_build_sha_threaded, "build-removes": check_build_removes,
          "build-meta": check_build_meta, "budget-cut": check_budget_cut,
          "stale-code": check_stale_code, "corrupt": check_corrupt,
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
          # round 3 (VERIFY-K2 R2): the verifier's seven (finding 4)
          "blobs-missing": check_blobs_missing, "grep-long-value": check_grep_long_value,
          "grep-attached": check_grep_attached, "script-paren": check_script_paren,
          "dq-substitution": check_dq_substitution, "grep-double-dash": check_grep_double_dash,
          "files-max": check_files_max,
          # K2 RE-SCOPE (D-117): (b) the tree check, (a) the committed blob's own symbols, the surface that went
          "tree-after-reset": check_tree_after_reset, "same-tree-move": check_same_tree_move,
          "head-unresolved": check_head_unresolved, "late-code-pack": check_late_code_pack,
          "committed-symbols": check_committed_symbols, "legacy-symbols": check_legacy_symbols,
          "no-graph-text": check_no_graph_text, "registry-screens": check_registry_screens,
          "build-in-flight": check_build_in_flight, "record-rechecked": check_record_rechecked,
          "record-rebuilt": check_record_rebuilt,
          # round 6: VERIFY-K2-RS's follow-ups (F2 is in head-unresolved)
          "registry-committed": check_registry_committed, "cli-label": check_cli_label,
          "foreign-git-dir": check_foreign_git_dir, "deep-chain": check_deep_chain,
          "no-symbols-lines": check_no_symbols_lines, "recover": check_recover}
# one mutation per property: (the check it must fail, old text, new text, the failure it must fail with)
TREE_GATE = ('    if not packs.current():\n        return dict(res, skip="tree")                    # D-117 (b): the '
             "packs describe a tree that is not HEAD's\n")
TRY_CODE = "    try:\n        status, text, sym, stale, skip = _code_part(rel, ti, packs)\n"
CURRENT = '            want, got = self.record().get("tree"), _rev(self.root, "HEAD^{tree}")\n'
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
    "stale-passes": ("stale-code", "if stale and not any(STALE_MARK in ln for ln in kept):", "if False:",
                     "a stale code part went out without its STALE mark"),
    "stale-word-only": ("stale-code", "if stale and not any(STALE_MARK in ln for ln in kept):",
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
    # round 2: F1 (since the re-scope the tree check guards F1's shape first; the blob check guards a late code pack)
    "no-blob-check": ("late-code-pack", 'if pack["blob"] != packs.blob(rel):', "if False:",
                      "a code pack of another blob reached the model"),
    "untracked-since-build-tree-off": ("untracked-since-build", TREE_GATE, "",
                                       "the packs of a tree that is not HEAD's reached the model"),
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
    # K2 RE-SCOPE (D-117): the brief's item 7 on the reader's side, and one per new clause
    "tree-check-off": ("tree-after-reset", TREE_GATE, "", "a byte HEAD's tree does not hold reached the model"),
    "p2-outside-the-check": ("tree-after-reset", TREE_GATE + TRY_CODE,
                             "    try:\n        status, text, sym, stale, skip = _code_part(rel, ti, packs) "
                             'if packs.current() else (None, "", None, None, "tree")\n',
                             "a byte HEAD's tree does not hold reached the model"),
    "commits-not-trees": ("same-tree-move", CURRENT, '            want, got = self.record().get("commit"), '
                          '_rev(self.root, "HEAD")\n',
                          "the packs of HEAD's tree were not shown after a same-tree ref move"),
    "unresolved-head-trusted": ("head-unresolved", " and got == want\n", " and got in (want, None)\n",
                                "an unresolved HEAD showed a pack (an unborn branch)"),
    "tree-at-head": ("build-sha-threaded", '_git(root, "rev-parse", "--verify", sha + "^{tree}")',
                     '_git(root, "rev-parse", "--verify", "HEAD^{tree}")', "the build recorded another commit's tree"),
    "no-tree-in-build": ("build-meta", '"commit": sha, "tree": tree, ', '"commit": sha, ',
                         "the build recorded no tree"),
    "legacy-symbols-shown": ("legacy-symbols", '    if pack.get("symbols_from") != "ast":\n', "    if False:\n",
                             "a code part whose symbols came from a graph reached the model"),
    "screens-unchecked": ("registry-screens", "    if not _screened(pack, packs):\n", "    if False:\n",
                          "a registry row from a screen the build does not hold reached the model"),
    "screens-one-file": ("registry-screens", "for p in codemap().SCREENS)", "for p in codemap().SCREENS[:1])",
                         "a registry row from a screen the build does not hold reached the model"),
    "no-building-marker": ("build-in-flight",
                           '    _write(str(pdir / "BUILD.json"), (json.dumps({"schema": SCHEMA, "commit": sha, '
                           '"building": True}, sort_keys=True)\n' + " " * 38 + '+ "\\n").encode("utf-8"))', "    pass",
                           "a byte HEAD's tree does not hold reached the model (a build in flight)"),
    "record-not-rechecked": ("record-rechecked", "    if not packs.still():\n", "    if False:\n",
                             "a part read while a build began reached the model"),
    "record-without-id": ("record-rebuilt", ', "id": os.urandom(8).hex()}', "}",
                          "a part another build wrote reached the model (two builds while the parts were read)"),
    # round 6: VERIFY-K2-RS's follow-ups (task #420, D-120); the first is the verifier's own (its p8disc.py)
    "current-none-equals-none": ("head-unresolved", "            self._current = isinstance(want, str) and "
                                 "OBJECT_RX.fullmatch(want) is not None and got == want\n",
                                 "            self._current = got == want\n",
                                 "a record with no tree and a git that fails showed a pack"),
    "env-strip-removed": ("foreign-git-dir", "cwd=root, env=_own_env(), capture_output=True,",
                          "cwd=root, capture_output=True,", "a foreign GIT_DIR's HEAD decided what shows"),
    "recovery-removed": ("recover", ",\n                **recover(state))", ")",
                         "a crashed build's marker was not rebuilt at SessionStart"),
    "recovery-ignores-the-lock": ("recover", "        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)\n", "        pass\n",
                                  "a second build started beside a live build"),
}


def mutate_text(path, old, new):
    """`path`'s text with `old` (found exactly once) replaced by `new`, compiled (INVALID, never a kill, otherwise)."""
    text = Path(path).read_text(encoding="utf-8")
    assert text.count(old) == 1, "INVALID: the anchor occurs %d times in %s" % (text.count(old), Path(path).name)
    out = text.replace(old, new)
    compile(out, str(path), "exec")
    return out


def mutant(name):
    """The text of filepacks.py with mutant `name` applied: its anchor must occur exactly once, and the result must
    compile (a mutant that does not compile would fail every check for the wrong reason: INVALID, never a kill)."""
    _, old, new, _ = MUTANTS[name]
    return mutate_text(FILEPACKS, old, new)


CODEMAP = ROOT / "scripts" / "codemap.py"
AST_SYMBOLS = '    syms = _ast_symbols(data) if lang == "python" else []'
# the code map's side of the re-scope, run through the reader: (the check it must fail, old text, new text, the failure)
CM_MUTANTS = {
    "symbols-from-working-copy": ("committed-symbols", AST_SYMBOLS,
                                  '    syms = _ast_symbols(path.read_bytes()) if lang == "python" else []',
                                  "an uncommitted symbol reached the model"),
    "caller-line-restored": ("no-graph-text", '    if where_rows:\n        lines.append("registry rows here %d: "',
                             '    if sym is not None and (sym.get("gitnexus") or {}).get("callers"):\n'
                             '        lines.append("callers: " + " · ".join("%s %s:%s" % '
                             '(x["name"], x["file"], x["line"]) for x in sym["gitnexus"]["callers"]["sample"]))\n'
                             '    if where_rows:\n        lines.append("registry rows here %d: "',
                             "a graph's caller, test, count or state reached the model"),
    # round 6: VERIFY-K2-RS's follow-ups; the first is the verifier's own (its p8disc.py)
    "registry-from-working-text-fullfp": ("registry-committed", "    reg_sec, registry = _registry(root, rel, text)\n",
                                          '    reg_sec, registry = _registry(root, rel, path.read_text(encoding="utf-8", '
                                          'errors="replace"))\n',
                                          "an uncommitted line reached the model through a registry row"),
    "cli-label-removed": ("cli-label", '            print("codemap: NOT HEAD\'s committed code (%s): %s" % (why, '
                          'HEAD_CHECKS[why]))\n', "            pass\n",
                          "a CLI printed a pack of another tree without the label"),
    "per-file-guard-removed": ("deep-chain", "            try:\n                results.append((rel,) + build_one(root, rel, "
                               "gn, env, commit))\n            except Exception as e:",
                               "            results.append((rel,) + build_one(root, rel, gn, env, commit))\n"
                               "            if False:", "one bad file ended the code-map build"),
    "ast-starts-parse-uncaught": ("deep-chain", "        tree = ast.parse(text)\n    except (SyntaxError, ValueError, "
                                  "RecursionError, MemoryError):\n", "        tree = ast.parse(text)\n    except "
                                  "(SyntaxError, ValueError):\n",
                                  "a file whose parse fails lost its pack, not only its symbols"),
    "ast-starts-walk-uncaught": ("deep-chain", '    try:\n        walk(tree, "")\n    except RecursionError:\n        '
                                 'return None\n', '    walk(tree, "")\n    if False:\n        return None\n',
                                 "a file whose parse fails lost its pack, not only its symbols"),
    "zero-symbols-restored": ("no-symbols-lines", '        head = "codemap %s — %s" % (rel, "%d symbols, %d at top level" '
                              '% (len(syms), len(shown)) if syms\n                                    else '
                              '_no_symbols(pack))\n', '        head = "codemap %s — %d symbols, %d at top level" % (rel, '
                              'len(syms), len(shown))\n', "a file with no symbols did not say why (a whole Read)"),
    "zero-symbols-in-range": ("no-symbols-lines", '        head = "codemap %s:%d-%d — %s" % (rel, line, end_line, "%d of '
                              'the file\'s %d symbols in range" % (\n            len(shown), len(syms)) if syms else '
                              '_no_symbols(pack))\n', '        head = "codemap %s:%d-%d — %d of the file\'s %d symbols '
                              'in range" % (rel, line, end_line, len(shown), len(syms))\n',
                              "a file with no symbols did not say why (a Read range)"),
    "module-level-count-restored": ("no-symbols-lines", '    if sym is None and not pack["symbols"]:\n        head += '
                                    '"module level (%s)" % _no_symbols(pack)\n    elif sym is None:\n',
                                    "    if sym is None:\n", "a file with no symbols did not say why (an Edit)"),
    "parsed-always-true": ("no-symbols-lines", '    parsed = syms is not None if lang == "python" else None',
                           '    parsed = True if lang == "python" else None',
                           "a file with no symbols did not say why (a whole Read)"),
}


def cm_mutant(name):
    _, old, new, _ = CM_MUTANTS[name]
    return mutate_text(CODEMAP, old, new)


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


@pytest.mark.parametrize("name", sorted(CM_MUTANTS))
def test_negative_control_the_same_check_fails_on_a_code_map_mutant(tmp_path, name):
    check, _, _, why = CM_MUTANTS[name]
    repo, ids = fixture(tmp_path, cm_text=cm_mutant(name))
    assert (repo / "scripts" / "codemap.py").read_text(encoding="utf-8") == cm_mutant(name)   # the mutant is what runs
    with pytest.raises(AssertionError, match=re.escape(why)):
        CHECKS[check](repo, tmp_path / "state", ids, tmp_path)


def test_every_check_has_a_mutant_and_every_mutant_compiles():
    assert set(CHECKS) == {m[0] for m in list(MUTANTS.values()) + list(CM_MUTANTS.values())}, \
        "a property has no mutant, or a mutant no check"
    for name in MUTANTS:
        mutant(name)
    for name in CM_MUTANTS:
        cm_mutant(name)


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


COMMITTED_READ = "    got = _committed(root, commit, [rel]).get(rel)\n"
WORKING_READ = "    got = (None, hashlib.sha256(path.read_bytes()).hexdigest(), path.read_bytes())\n"


@pytest.mark.skipif(not GRAFT, reason="LOUD SKIP: graft is not installed here (scripts/setup.sh installs it); this "
                                      "test runs the real L2a refresh after a graft re-index")
@pytest.mark.parametrize("cm", ["real", "pack-of-the-working-copy"])
def test_untracked_since_build_with_the_real_code_map_refresh(tmp_path, cm):
    """The verifier's probe_p6.py, re-scoped (D-117): scripts/gamma.py, untracked by the last commit, gets a canary def,
    graft re-indexes it, and the REAL refresh runs (`codemap.py refresh --commit … --graphs graft`, as the post-commit
    hook runs it). The real code map writes no pack of a file with no blob in the commit (`1 untracked`), so no pack
    holds the canary; the code map that packs the working copy (the leak control) writes it into gamma's pack. Either
    way 0 canary bytes reach the model on Edit, Read and cat: the file packs describe the tree before the untracking
    commit, and the record says tree."""
    cm_text = None if cm == "real" else mutate_text(CODEMAP, COMMITTED_READ, WORKING_READ)
    repo, ids = fixture(tmp_path, cm_text=cm_text)
    st, locks, env = tmp_path / "state", tmp_path / "locks", graft_env(tmp_path)
    locks.mkdir()

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
    held = sorted(str(p.relative_to(repo)) for p in (repo / ".jev" / "codemap").rglob("*.json")
                  if canary in p.read_text(encoding="utf-8"))
    if cm == "real":
        assert held == [] and " codemap refresh done: 1 untracked;" in out, \
            "an untracked file's text reached a code pack: %s %s" % (held, out[-300:])
    else:
        assert held == [".jev/codemap/scripts/gamma.py.json"], "the control: the working copy's pack: %s" % held
    for p in gamma_probes(repo, "rf"):
        ctx = context(run(repo, st, p))
        assert canary not in ctx and ctx == "", "the untracked file's text reached the model: %r" % ctx[:80]
        assert records(st)[-1]["skipped"] == [{"key": "file:scripts/gamma.py", "why": "tree"}], records(st)[-1]


# ---------- round 3: B3 (the patch's own tests once it lands); B2 became D-117 (a), with the real graft ----------

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


def test_a_wrong_unpatched_at_is_refused(tmp_path):
    """VERIFY-K2 R3 finding 5 (its preimage_killer.py): the hook without the patch must be the blob the patch names as
    its pre-image, so an UNPATCHED_AT whose hook is another blob (283faf0's is 2efcc7c) is refused, never used as the
    negative control's hook; the real UNPATCHED_AT passes (the control)."""
    global UNPATCHED_AT
    real = UNPATCHED_AT
    assert (hook_dir(tmp_path, False) / "post-commit").is_file()
    UNPATCHED_AT = "283faf044fef56b68c09ac46de886f96782a280f"
    try:
        with pytest.raises(AssertionError, match=re.escape("the hook at UNPATCHED_AT is not the patch's pre-image")):
            hook_dir(tmp_path, False)
    finally:
        UNPATCHED_AT = real


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
                                      "test runs the real L2a refresh after a graft re-index")
@pytest.mark.parametrize("cm", ["real", "symbols-from-graft"])
def test_graft_symbols_never_reach_a_pack_with_the_real_code_map_refresh(tmp_path, cm):
    """D-117 (a) through the real instruments (VERIFY-K2 R2 B2, the verifier's probe_f1.py sg-tracked): graft indexes
    scripts/alpha.py with a canary def appended, the edit is undone by `git checkout`, and the REAL refresh builds
    alpha's pack of the build's blob. Its symbols are the committed blob's own ast, so the canary graft holds is in no
    pack and reaches the model on neither Read nor cat; the committed symbols show, and the graft section says stale.
    The code map that takes its symbols from graft (the leak control) shows the canary. (Round 3's untracked shape went:
    the code map writes no pack of an untracked file, test_untracked_since_build_with_the_real_code_map_refresh.)"""
    cm_text = None if cm == "real" else mutate_text(CODEMAP, AST_SYMBOLS, "    syms = _nest(graft_syms)")
    repo, ids = fixture(tmp_path, cm_text=cm_text)
    st, locks, env = tmp_path / "state", tmp_path / "locks", graft_env(tmp_path)
    locks.mkdir()

    def sh(*argv):
        r = subprocess.run(list(argv), cwd=repo, env=env, capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, (argv, r.stdout[-400:], r.stderr[-400:])
        return r.stdout
    sh(GRAFT, "build")
    build(repo, st)
    rel, at = "scripts/alpha.py", git(repo, "rev-parse", "HEAD").strip()
    before = (repo / rel).read_bytes()
    canary = "cnry" + secrets.token_hex(6)
    (repo / rel).write_text(before.decode("utf-8") + '\n\ndef leak_%s(token="%s-arg"):\n    return token\n' % (
        canary, canary), encoding="utf-8")
    sh(GRAFT, "build")
    git(repo, "checkout", "--", rel)
    assert (repo / rel).read_bytes() == before, "the bytes did not go back"
    assert canary in sh(GRAFT, "skeleton", "--json", "--no-refresh", rel), "not the case: graft holds no canary"
    out = sh("python3", "scripts/codemap.py", "refresh", "--commit", at, "--lock-dir", str(locks), "--graphs", "graft",
             "--wait", "8", "--grace", "2", "--", rel)
    pk = json.loads((repo / ".jev" / "codemap" / (rel + ".json")).read_text(encoding="utf-8"))
    assert "\n%s\t%s\n" % (rel, pk["blob"]) in (st / "filepacks" / "BLOBS.txt").read_text(), \
        "not the case: a pack of the build's blob (only (a) keeps the canary out)"
    ctxs = [context(run(repo, st, p)) for p in (read(repo, rel, sid="gs0"), bash(repo, "cat " + rel, sid="gs1"))]
    if cm == "real":
        assert canary not in json.dumps(pk) and not any(canary in c for c in ctxs), \
            "a graph's symbol reached a pack or the model: %s" % [c[:120] for c in ctxs]
        assert [(s["qualname"], s["start"], s["end"]) for s in pk["symbols"]] == [
            s[:3] for s in ast_symbols(before.decode("utf-8"))] and pk["instruments"]["graft"]["graph"] == "stale", \
            out[-300:]
        assert all(c.startswith("codemap scripts/alpha.py — 5 symbols") for c in ctxs), \
            "the control: the committed symbols: %s" % [c[:80] for c in ctxs]
    else:
        assert canary in json.dumps(pk) and all(canary in c for c in ctxs), \
            "the control: the symbols from graft reach the model: %s" % [c[:120] for c in ctxs]


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


def cmdline(pid):
    """A process's command line, for a message ('' once it is gone)."""
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as f:
            return f.read().replace(b"\0", b" ").decode("utf-8", "replace").strip()[:200]
    except OSError:
        return ""


def wait_post_commit(pct, head, bound=300):
    """Until the post-commit hook's jobs for `head` are done: the code-map refresh (or the hook's line that none runs)
    and the file-pack build logged their results, and no job holds its lock any more. Returns a reader of the hook's
    logs."""
    deadline = time.monotonic() + bound

    def text(name):
        p = pct / name
        return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
    while not (re.search(r"%s codemap refresh (done|none)" % head[:7], text("codemap-refresh.log"))
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


# ---------- K2 RE-SCOPE (D-117): the class test, a reset after a build, through the real patched hook ----------

RESET_WANT = {"read alpha": ("sym",), "read rst": ("new",), "read beta": ("led",), "cat alpha rst": ("sym", "new")}
RESET_TREE = {"read alpha": ["file:scripts/alpha.py"], "read rst": ["file:scripts/rst.py"],
              "read beta": ["file:scripts/beta.py"], "cat alpha rst": ["file:scripts/alpha.py", "file:scripts/rst.py"]}


def reset_scenario(tmp, fp_text=None):
    """VERIFY-K2-R4's R4-1 through the REAL post-commit hook carrying the K2 patch (each commit's graph re-index, where
    graft and GitNexus are off PATH the two graphs the hook finds by its fixed paths, the code-map refresh and the
    file-pack build) and the real wrapper. c_a changes scripts/alpha.py; c_b adds a def to it, a new file scripts/rst.py
    and a ledger line naming scripts/beta.py, a canary each (the ledger line is the P2 shape). After c_b's jobs: `git
    reset --mixed HEAD~1` (no hook runs); c_b made again and built, then `git reset --soft HEAD~1`; c_b made a third
    time and built, then push_clean's same-tree ref move (`git commit-tree` + `git update-ref`). Returns (seen, ctl):
    per observation point, the probes whose context holds each canary, the bytes shown and the tree skips recorded;
    the facts the controls read."""
    repo, ids = fixture(tmp, fp_text=fp_text)
    st, pct, home = tmp / "state", tmp / "pctmp", tmp / "home"
    pct.mkdir()
    home.mkdir()
    rdv = tempfile.mkdtemp(prefix="cbmr.", dir="/tmp")     # codebase-memory's rendezvous, private too (AF-AP-251)
    env = dict(env_for(repo, st), HOME=str(home), DO_NOT_TRACK="1", AF_POST_COMMIT_TMP=str(pct),
               PATH="/usr/local/bin:/usr/bin:/bin", CBM_RUNTIME_DIR=rdv)
    hooks = hook_dir(tmp, True)
    cn = {k: "%s%s" % (k, secrets.token_hex(5)) for k in ("sym", "new", "led")}
    alpha = (repo / "scripts" / "alpha.py").read_text(encoding="utf-8") + "# rev 5\n"
    c_b = {"scripts/alpha.py": alpha + "\n\ndef leak_%s(x):\n    return x\n" % cn["sym"],
           "scripts/rst.py": "def rst_%s():\n    return 1\n" % cn["new"],
           LEDGER: (repo / LEDGER).read_text(encoding="utf-8") + "**T9 HOME.** %s: a line naming scripts/beta.py\n" % (
               cn["led"])}
    seen, ctl = {}, {}

    def hooked(files, msg):
        for rel, text in files.items():
            (repo / rel).write_text(text, encoding="utf-8")
        git(repo, "add", "--", *files)                               # the named paths only, never -A
        r = subprocess.run(["git", "-c", "user.email=k2@test", "-c", "user.name=k2", "-c", "commit.gpgsign=false", "-c",
                            "core.hooksPath=%s" % hooks, "commit", "-q", "-m", msg], cwd=repo, env=env,
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr
        head = git(repo, "rev-parse", "HEAD").strip()
        wait_post_commit(pct, head)
        return head

    def observe(point):
        seen[point] = {"context": {k: [] for k in cn}, "bytes": 0, "tree": {}}
        for label, p in (("read alpha", read(repo, "scripts/alpha.py", sid=point + "-a")),
                         ("read rst", read(repo, "scripts/rst.py", sid=point + "-r")),
                         ("read beta", read(repo, "scripts/beta.py", sid=point + "-b")),
                         ("cat alpha rst", bash(repo, "cat scripts/alpha.py scripts/rst.py", sid=point + "-c"))):
            ctx = context(run(repo, st, p))
            for k, v in cn.items():
                if v in ctx:
                    seen[point]["context"][k].append(label)
            seen[point]["bytes"] += len(ctx.encode("utf-8"))
            seen[point]["tree"][label] = [s["key"] for s in records(st)[-1]["skipped"] if s["why"] == "tree"]
        seen[point]["context"] = {k: sorted(v) for k, v in seen[point]["context"].items()}

    def moved(want):
        tree = json.loads((st / "filepacks" / "BUILD.json").read_text(encoding="utf-8"))["tree"]
        return git(repo, "rev-parse", "HEAD").strip() == want and git(repo, "rev-parse", "HEAD^{tree}").strip() != tree
    try:
        c_a = hooked({"scripts/alpha.py": alpha}, "c_a: alpha")
        hooked(c_b, "c_b: the canaries")
        observe("built")
        git(repo, "reset", "-q", "--mixed", "HEAD~1")
        ctl["mixed"] = moved(c_a) and "scripts/rst.py" not in git(repo, "ls-files").split("\n")
        observe("mixed")
        hooked(c_b, "c_b again")
        observe("built again")
        git(repo, "reset", "-q", "--soft", "HEAD~1")
        ctl["soft"] = moved(c_a) and "scripts/rst.py" in git(repo, "diff", "--cached", "--name-only").split("\n")
        observe("soft")
        head = hooked(c_b, "c_b a third time")
        new = git(repo, "commit-tree", "HEAD^{tree}", "-p", "HEAD~1", "-m", "rewritten", k=9).strip()
        git(repo, "update-ref", git(repo, "symbolic-ref", "HEAD").strip(), new)
        ctl["same-tree"] = new != head and git(repo, "rev-parse", "HEAD^{tree}") == git(repo, "rev-parse",
                                                                                       head + "^{tree}")
        observe("same-tree")
        deadline = time.monotonic() + 30       # the codebase-memory index leaves a daemon that idles out in about 5 s
        while fixture_processes(tmp) and time.monotonic() < deadline:
            time.sleep(0.2)
        ctl["leftover"] = {pid: cmdline(pid) for pid in fixture_processes(tmp)}
        ctl["cbm"] = (pct / "cbm-index.log").read_text(errors="replace") if (pct / "cbm-index.log").exists() else ""
    finally:
        for pid in fixture_processes(tmp):
            os.kill(pid, signal.SIGKILL)
        shutil.rmtree(rdv, ignore_errors=True)
    return seen, ctl


@pytest.mark.parametrize("variant", ["real", "tree-check-off"])
def test_a_reset_shows_nothing_through_the_real_hook(tmp_path, variant):
    """K2 RE-SCOPE, contract item 5 (reset_scenario). real: after each reset nothing reaches the model (0 bytes) and
    each touched file's record says tree; the controls: each canary shows where RESET_WANT says after each build and
    after the same-tree ref move, with no tree skip. tree-check-off (the leak control): each canary, the P2 ledger line
    included, reaches the model after each reset."""
    seen, ctl = reset_scenario(tmp_path, None if variant == "real" else mutant(variant))
    assert ctl["leftover"] == {}, "a post-commit job, or a process it left, outlived it by 30 s: %s" % ctl["leftover"]
    assert "different cache directory" not in ctl["cbm"], \
        "the codebase-memory index met another daemon's rendezvous (AF-AP-251): %s" % ctl["cbm"]
    assert ctl["mixed"] and ctl["soft"] and ctl["same-tree"], "not the shapes: %s" % ctl
    want = {k: sorted(label for label, ks in RESET_WANT.items() if k in ks) for k in ("sym", "new", "led")}
    if variant != "real":
        missed = {p: seen[p]["context"] for p in ("mixed", "soft") if seen[p]["context"] != want}
        assert not missed, "the control: with the tree check off these canaries did not reach the model: %s" % missed
        return
    for p in ("built", "built again"):
        assert seen[p]["context"] == want and not any(seen[p]["tree"].values()), \
            "the control: a committed canary was not shown after the build: %s %s" % (p, seen[p])
    for p in ("mixed", "soft"):
        assert seen[p]["bytes"] == 0 and not any(seen[p]["context"].values()), \
            "a byte HEAD's tree does not hold reached the model through the real hook: %s %s" % (p, seen[p])
        assert seen[p]["tree"] == RESET_TREE, "the record did not say tree: %s %s" % (p, seen[p]["tree"])
    assert seen["same-tree"]["context"] == want, \
        "the packs of HEAD's tree were not shown after a same-tree ref move: %s" % seen["same-tree"]


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
    """Drift guard: the real codemap builder (build_one, its graphs absent, the repo's own registry screen copied in)
    writes a pack with the same fields, instrument sections, screen record and symbols (their graph data aside) as the
    planted one, so the checks read the format the builder writes."""
    repo, ids = fixture(tmp_path)
    for rel in SCREENS:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, repo / rel)
    planted = plant_code_pack(repo, "scripts/alpha.py", ids["fourth"])        # again, with the screen files here
    spec = importlib.util.spec_from_file_location("codemap_k2_drift", repo / "scripts" / "codemap.py")
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)
    outcome, real = cm.build_one(repo, "scripts/alpha.py", ("absent", "not in this test"), {"PATH": "/usr/bin:/bin"},
                                 ids["fourth"])
    assert outcome == "built" and set(real) == set(planted) and set(real["instruments"]) == set(planted["instruments"])
    assert (real["blob"], real["lines"], real["schema"], real["symbols_from"], real["parsed"]) == (
        planted["blob"], planted["lines"], planted["schema"], planted["symbols_from"], planted["parsed"])
    ap, pap = real["instruments"]["ap_screen"], planted["instruments"]["ap_screen"]
    assert ap["status"] == "ok" and set(ap) == set(pap) and ap["screens"] == pap["screens"], (ap, pap)
    bare = [[{k: v for k, v in s.items() if k != "gitnexus"} for s in pk["symbols"]] for pk in (real, planted)]
    assert bare[0] == bare[1], bare


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
