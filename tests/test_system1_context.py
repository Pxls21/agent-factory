"""`.claude/hooks/system1-context.py` through its REAL registered command lines (S1-L1, D-090; design L1 and L3).

Each behaviour test feeds a fixture hook payload to the command string exactly as `.claude/settings.json` holds it
(`sh -c <command>` with CLAUDE_PROJECT_DIR set), or as `scripts/install_session_hooks.py` writes it, and asserts what
reaches the model: the `additionalContext` of hook_context.py's one JSON line. The oracle for "the governing lines,
verbatim" is the skill file itself, read here independently of the hook: every line between a block's label and its
pointer must be a whole line of that skill file (or the `…` gap mark), and the pointer's heading must be a heading of it.
The oracle for "whole entries" is this file's own reading of the table and the skills (`resolved`, `units`), never the
hook's.

State never touches the real .jev/: AF_SYSTEM1_STATE points each test at its own tmp dir. The tests that need a broken
skill, table or row run the registered command against a copy of the hook, the table and the skills (`copy_repo`).
S1-L1-R1 added the tests for the VERIFY-S1-L1 follow-ups (F1, F2, F4-F10, F12, F16, F17) and for its mutants.

S1-ALL (task #296, D-093) made the prompt path read every skill under .claude/skills. A library skill (outside the
table's project_skills) is reached by its name and its excerpt opens with its one-line description; the oracle for that
line is PyYAML's reading of the skill's frontmatter (`description_of`), never the hook's parser. The tests from
`test_a_library_skill_is_reached_by_name_with_its_description` on each name the reason they are red on the PIN, a67489f.

S1-RATE (task #295, D-092 item 3): the wrapper stamps what it hands the model. `context` checks the stamp (the first line
`[S1 <id> system1-context]`, the last line the score request for that id) against literals and cuts it off, so every
test below reads the hook's own text; AF_S1_RATE_STATE keeps the wrapper's telemetry in each test's tmp dir. The tool
path's record carries the payload's tool_use_id and each block's sha (`test_the_tool_record_carries_its_join_keys`).
"""
import collections
import fcntl
import hashlib
import importlib.util
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / ".claude" / "hooks"
HOOK = HOOKS / "system1-context.py"
TABLE = json.loads((HOOKS / "system1-situations.json").read_text(encoding="utf-8"))
SETTINGS = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
ROWS = {row["id"]: row for row in TABLE["rows"]}
PROJECT = set(TABLE["project_skills"])        # the project's own skills; any other skill is a library one
SID = "s1test-session-0001"
# An entry starts at a heading, a bold lead, a list item, a numbered or lettered item, a table, a quote or a fence, or
# after a blank line; other lines continue it. The hook's ENTRY_START_RX must say the same (a test holds it).
ENTRY_RX = re.compile(r"^\s*(?:\*\*|#{1,6}\s|[-*+]\s|\d+[a-z]?\.\s|\([a-z0-9]{1,3}\)\s|\||>|```)")
HEAD_RX = re.compile(r"#{1,6}\s")
STAMP = re.compile(r"\[S1 (s1-[0-9a-f]{8}) system1-context\]")                  # the wrapper's stamp (S1-RATE)
REQUEST = ('Begin your next text with "S1-RATE {id} rel=R use=U" (+ a note <=120 chars: why, if a 0), one line per '
           'unscored injection. rel 0 unrelated,1 same area not this step,2 relevant to this step,3 governs it; '
           'use 0 noise/known,1 confirms,2 used it,3 changed what I did')


@pytest.fixture(autouse=True)
def _s1_rate_state(tmp_path, monkeypatch):
    monkeypatch.setenv("AF_S1_RATE_STATE", str(tmp_path / "s1-rate-state"))   # never the real .jev/


def registered(event, matcher=None):
    """The settings file's one command that runs system1-context.py for this event."""
    cmds = [h["command"] for g in SETTINGS["hooks"][event] for h in g["hooks"]
            if "system1-context.py" in h["command"] and (matcher is None or g.get("matcher") == matcher)]
    assert len(cmds) == 1, (event, cmds)
    return cmds[0]


PRE = registered("PreToolUse", "Write|Edit|Bash")
PROMPT = registered("UserPromptSubmit")
START = SETTINGS["hooks"]["SessionStart"][0]["hooks"][0]["command"]


def run(cmd, payload, state, timeout=60, root=ROOT, prefix=""):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root), AF_SYSTEM1_STATE=str(state), AF_S1_RATE_STATE=str(state),
               CLAUDE_CODE_REMOTE="false")
    data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    return subprocess.run(["sh", "-c", prefix + cmd], input=data, capture_output=True, timeout=timeout, env=env, cwd="/")


def unstamp(ctx):
    """The hook's own text inside the wrapper's stamp: the first line `[S1 <id> system1-context]` and the last line the
    score request for that id, both checked against the literals, then cut off."""
    first, _, rest = ctx.partition("\n")
    m = STAMP.fullmatch(first)
    assert m, first[:80]
    body, _, last = rest.rpartition("\n")
    assert last == REQUEST.format(id=m.group(1)), last[:80]
    return body


def context(r):
    """What reaches the model, the stamp checked and cut off: the hook's text in the additionalContext of the one JSON
    line, or '' when the hook printed nothing."""
    assert r.returncode == 0, (r.returncode, r.stderr)
    out = r.stdout.decode("utf-8")
    if not out.strip():
        return ""
    obj = json.loads(out)
    assert set(obj) == {"hookSpecificOutput"} and set(obj["hookSpecificOutput"]) == {"hookEventName", "additionalContext"}
    return unstamp(obj["hookSpecificOutput"]["additionalContext"])


def telemetry(state):
    p = Path(state) / "system1.jsonl"
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def tool(name, ti, sid=SID, agent=None):
    p = {"session_id": sid, "transcript_path": "/dev/null", "cwd": str(ROOT), "hook_event_name": "PreToolUse",
         "tool_name": name, "tool_input": ti, "tool_use_id": "toolu_s1test"}
    if agent:
        p["agent_id"] = agent
    return p


def bash(cmd):
    return ("Bash", {"command": cmd, "description": "a fixture"})


def write(rel, content="x\n"):
    return ("Write", {"file_path": f"{ROOT}/{rel}", "content": content})


def edit(rel, new="y", old="x"):
    return ("Edit", {"file_path": f"{ROOT}/{rel}", "old_string": old, "new_string": new})


def prompt(text, sid=SID):
    return {"session_id": sid, "transcript_path": "/dev/null", "cwd": str(ROOT), "hook_event_name": "UserPromptSubmit",
            "prompt": text}


def start(source, sid=SID, agent=None):
    p = {"session_id": sid, "transcript_path": "/dev/null", "cwd": str(ROOT), "hook_event_name": "SessionStart",
         "source": source}
    if agent:
        p["agent_id"] = agent
    return p


def skill_lines(skill, root=ROOT):
    return (root / ".claude" / "skills" / skill / "SKILL.md").read_text(encoding="utf-8").split("\n")


def description_of(skill, root=ROOT):
    """A skill's frontmatter description as PyYAML reads it, whitespace folded: the oracle for the hook's own parser."""
    text = (root / ".claude" / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    front = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    return " ".join(str(yaml.safe_load(front.group(1)).get("description") or "").split()) if front else ""


def description_line_ok(skill, line, root=ROOT):
    """A library excerpt's description line: `description: ` and the skill's description, whole, or cut at a word
    boundary to at most 300 UTF-8 bytes and marked with `…`."""
    if not line.startswith("description: "):
        return False
    text, want = line[len("description: "):], description_of(skill, root)
    head = text[:-1]
    return text == want or (text.endswith("…") and len(text.encode("utf-8")) <= 300 and want.startswith(head)
                            and want[len(head):len(head) + 1] in (" ", ",", ";", ":"))


def blocks(ctx, pointer_only_ok=False, root=ROOT):
    """Split an injection into (label, body, pointer, skill) blocks and check each against its skill file (the oracle).
    A block with no line (label and pointer only) is allowed only where the caller says so (F4, the prompt path). A
    library skill's prompt block may open with its description line (S1-ALL): checked against PyYAML's reading of the
    skill, and left out of the body returned."""
    out, cur = [], None
    for line in ctx.split("\n") if ctx else []:
        if line.startswith("[system1 · "):
            assert cur is None, "a label inside an open block"
            cur = [line, []]
        elif line.startswith("full details: .claude/skills/"):
            assert cur is not None, "a pointer with no label"
            skill, heading = line[len("full details: .claude/skills/"):].split("/SKILL.md § ", 1)
            lines = skill_lines(skill, root)
            assert any(x.lstrip("#").strip() == heading for x in lines if x.startswith("#")), heading
            body = cur[1]
            if skill not in PROJECT and body[:1] and description_line_ok(skill, body[0], root):
                body = body[1:]
            assert (body or pointer_only_ok) and body[:1] != ["…"], "a block with no skill line"
            for x in body:
                assert x == "…" or x in lines, f"not a verbatim line of {skill}: {x[:80]!r}"
            out.append((cur[0], body, line, skill))
            cur = None
        else:
            assert cur is not None, f"text outside a block: {line[:80]!r}"
            cur[1].append(line)
    assert cur is None, "a block with no pointer"
    return out


def row_of(label):
    return label[len("[system1 · "):].split("]", 1)[0]


def section(row):
    """(lines, start, end) of the row's section: from its heading to the next heading, found here without the hook."""
    lines, heads, fence = skill_lines(row["skill"]), [], False
    for i, x in enumerate(lines):
        if x.lstrip().startswith("```"):
            fence = not fence
        elif not fence and re.match(r"#{1,6}\s", x):
            heads.append(i)
    start = [i for i in heads if lines[i].lstrip("#").strip() == row["heading"]]
    assert len(start) == 1, (row["id"], row["heading"])
    return lines, start[0], next((i for i in heads if i > start[0]), len(lines))


def resolved(row):
    """(lines, start, end, the row's line indexes), read here from the table's own words: a string names one line and
    takes its entry to the entry's end; a [from, to] pair takes the lines from one to the first that holds the other."""
    lines, s, e = section(row)
    out = []
    for sel in row["lines"]:
        a_text, b_text = (sel, None) if isinstance(sel, str) else sel
        hits = [i for i in range(s + 1, e) if a_text in lines[i]]
        assert len(hits) == 1, (row["id"], a_text, len(hits))
        b = a = hits[0]
        if b_text is None:
            while b + 1 < e and lines[b + 1].strip() and not ENTRY_RX.match(lines[b + 1]):
                b += 1
        else:
            b = next(k for k in range(a, e) if b_text in lines[k])
        out += [k for k in range(a, b + 1) if k not in out]
    return lines, s, e, out


def units(row):
    """The row's lines cut into whole entries (a gap, a blank line or an entry start begins a new one): the unit a call
    takes whole or leaves for a later call."""
    lines, _, _, idx = resolved(row)
    out, prev = [], None
    for i in idx:
        if not lines[i].strip():
            prev = None
            continue
        if prev is None or i != prev + 1 or ENTRY_RX.match(lines[i]):
            out.append([])
        out[-1].append(lines[i])
        prev = i
    return out


def first_line(row):
    """The section line the row's first selector names (a selector is unique in its section, not in its file)."""
    sel = row["lines"][0]
    start_text = sel if isinstance(sel, str) else sel[0]
    lines, s, e = section(row)
    hits = [x for x in lines[s + 1:e] if start_text in x]
    assert len(hits) == 1, (row["id"], start_text, len(hits))
    return hits[0]


def pointer(row):
    return f"full details: .claude/skills/{row['skill']}/SKILL.md § {row['heading']}"


def line_key(skill, line):
    """The marker's key of one line, as the marker format defines it (sha1 of skill and line, 16 hex)."""
    return hashlib.sha1(f"{skill}\n{line}".encode("utf-8")).hexdigest()[:16]


def copy_repo(dst):
    """A copy of the hook, its table, the wrapper and every skill the table names, to break one of them safely."""
    (dst / ".claude" / "hooks").mkdir(parents=True)
    (dst / "scripts").mkdir()
    for f in ("system1-context.py", "system1-situations.json"):
        shutil.copy2(HOOKS / f, dst / ".claude" / "hooks" / f)
    shutil.copy2(ROOT / "scripts" / "hook_context.py", dst / "scripts" / "hook_context.py")
    for skill in sorted({r["skill"] for r in TABLE["rows"]} | PROJECT):
        (dst / ".claude" / "skills" / skill).mkdir(parents=True)
        shutil.copy2(ROOT / ".claude" / "skills" / skill / "SKILL.md", dst / ".claude" / "skills" / skill / "SKILL.md")
    return dst


def _module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---- the registrations

def test_both_events_are_registered_through_the_wrapper():
    for event, cmd in (("PreToolUse", PRE), ("UserPromptSubmit", PROMPT)):
        assert f"scripts/hook_context.py {event} -- python3 $CLAUDE_PROJECT_DIR/.claude/hooks/system1-context.py" in cmd
        assert cmd.startswith("[ -f $CLAUDE_PROJECT_DIR/.claude/hooks/system1-context.py ] && [ -f ") and "|| exit 0;" in cmd
    assert "session-start.sh" in START
    sys.path.insert(0, str(ROOT / "scripts"))
    import install_session_hooks as ish
    hooks = ish.our_hooks(ROOT)
    pre = [g for g in hooks["PreToolUse"] if "system1-context.py" in g["hooks"][0]["command"]]
    ups = [g for g in hooks["UserPromptSubmit"] if "system1-context.py" in g["hooks"][0]["command"]]
    assert len(pre) == 1 and pre[0]["matcher"] == "Write|Edit|Bash" and len(ups) == 1 and "matcher" not in ups[0]
    assert "hook_context.py PreToolUse -- python3" in pre[0]["hooks"][0]["command"]
    assert "hook_context.py UserPromptSubmit -- python3" in ups[0]["hooks"][0]["command"]


# ---- every situation row: a matching and a non-matching tool input

FIXTURES = {
    "pc-sqlite": (bash('bash scripts/pc.sh "echo $B64 | base64 -d > /tmp/q.sh && sqlite3 s.db < /tmp/q.sh"'),
                  bash("bash scripts/pc.sh 'uptime'")),
    "pc-podman": (bash("bash scripts/pc.sh 'podman ps -a'"), bash("podman ps -a")),
    "pc-call": (bash("bash scripts/pc.sh 'uptime'"), bash("ls -la scripts/pc.sh")),
    "pc-lane": (bash("bash scripts/pc_lane.sh tasks/briefs/pc/X-brief.md hermes code-implementer"),
                bash("sed -n 140,150p scripts/pc_lane.sh")),
    "pc-suite": (bash("bash scripts/pc_suite.sh wait 1234"), bash("grep -n 'pc_suite.sh' CLAUDE.md")),
    "ouroboros": (bash('IS_SANDBOX=1 python scripts/ooo_mcp.py ouroboros_interview "$JSONARG"'),
                  bash("cat sandbox-kit/OUROBOROS-SETUP.md")),
    "push": (bash("git push origin HEAD:claude/x"), bash("git log --oneline origin/claude/x..HEAD")),
    "push-delegate-work": (bash("PUSH_BRANCH=claude/x bash scripts/push_clean.sh --no-delegates-live"),
                           bash("git push-something")),
    "hook-installer": (bash("python3 scripts/install_session_hooks.py --check"),
                       bash("grep -n install_session_hooks.py scripts/setup.sh")),
    "stamp": (write("docs/notes/s1test.md", "ledger 15:2xZ\n"), write("docs/notes/s1test.md", "at 1520Z and 15:2x\n")),
    "commit": (bash("git commit -m 'fix: the thing'"), bash("git commit-tree HEAD^{tree}")),
    "commit-increment": (bash("bash scripts/safe_commit.sh -m 'x' scripts/a.py"), bash("cat scripts/safe_commit.sh")),
    "proof-regen": (bash("python3 scripts/proof-runner run --proof S0-01 --venue sandbox --root ."),
                    bash("cat scripts/proof-runner")),
    "vendored-manifest-write": (bash("python3 scripts/vendored_manifest.py --write"),
                                bash("python3 scripts/vendored_manifest.py --check")),
    "test-vendored-manifest": (bash("python3 -m pytest tests/test_vendored_manifest.py -k class"),
                               bash("python3 -m pytest tests/test_session_hooks.py")),
    "test-proof-status": (bash("python3 -m pytest tests/test_proof_status.py --basetemp /tmp/ps/bt"),
                          bash("python3 -m pytest tests/test_session_hooks.py")),
    "test-gate": (bash("bash scripts/test_summary.sh tests/test_session_hooks.py"), bash("cat scripts/test_summary.sh")),
    "pasted-count": (edit("todo/BUILD-TASKLIST.md", "gate: 28 passed in 1.9s"), edit("todo/BUILD-TASKLIST.md", "all passed")),
    "anchor-edit": (bash("python3 scripts/anchor_edit.py todo/BUILD-TASKLIST.md --replace A B"),
                    bash("grep -n anchor_edit.py CLAUDE.md")),
    "ops-script": (bash("bash scripts/resume-heal.sh"), bash("bash scripts/setup.sh")),
    "background": (bash("nohup python3 x.py > /tmp/x.log 2>&1 &"), bash("python3 x.py > /tmp/x.log 2>&1 && echo ok")),
    "pgrep": (bash("pgrep -f '[p]ytest' || true"), bash("ps -eo pid,args | head")),
    "gitnexus": (bash("node .gitnexus/run.cjs impact our_hooks --direction upstream --repo ."), bash("ls .gitnexus")),
    "codebase-memory": (bash("codebase-memory-mcp cli search_graph --project home-user-agent-factory --query x"),
                        bash("ls /root/.local/bin")),
    "code-review-graph": (bash("/root/venv-crg/bin/code-review-graph query callers_of merged"),
                          bash("ls /root/venv-crg/bin")),
    "graft": (bash("graft ask 'who calls merged'"), bash("ls graft")),
    "lane-context": (bash("bash scripts/lane_context.sh -q 'x' -o /tmp/p.md scripts/a.py"),
                     bash("sed -n 1,5p scripts/lane_context.sh")),
    "brief-registers-hook": (write("tasks/briefs/system1/S1-L9-brief.md", "MODIFY: `.claude/settings.json`\n"),
                             write("tasks/briefs/system1/S1-L9-brief.md", "# a brief that registers no hook\n")),
    "brief": (write("tasks/briefs/system1/S1-L9-brief.md", "# brief\n"),
              write("tasks/briefs/system1/S1-L9-report.md", "# report\n")),
    "brief-contract": (edit("tasks/briefs/system1/S1-L9-brief.md", "the contract"), edit("tasks/briefs/pc/VENUE-MAP.md")),
    "research-prompt": (write("docs/research/prompts/RESEARCH-PROMPT-99.md"), write("docs/research/findings/X.md")),
    "live-state": (edit("wiki/topics/live-state.md", "- **LIVE:** x"), edit("wiki/topics/other.md", "- **LIVE:** x")),
    "claude-md-gitnexus-block": (edit("CLAUDE.md", "# GitNexus — Code Intelligence"), edit("CLAUDE.md", "a graft line")),
    "dormant-claim": (edit("docs/s1test.md", "the seam is DORMANT"), edit("docs/s1test.md", "the seam is dormant-ish")),
    "test-edit": (edit("tests/test_s1x.py", "assert x"), edit("docs/test_notes.md", "assert x")),
    "test-edit-increment": (edit("tests/test_s1x.py", "assert x"), edit("docs/tests.md")),
    "gate-edit": (edit("scripts/hooks/pre-commit"), edit("scripts/hookless.py")),
    "gate-edit-tactics": (edit("scripts/ci_gate.py"), edit("scripts/hookless.py")),
    "code-edit": (edit("scripts/s1x.py", "x = 1"), edit("docs/s1x.md", "x = 1")),
    "code-edit-guidelines": (edit("src/agent_factory/s1x.py", "x = 1"), edit("sandbox-kit/s1x.py", "x = 1")),
}


def test_every_row_has_a_fixture_and_every_fixture_a_row():
    assert set(FIXTURES) == set(ROWS)


@pytest.mark.parametrize("rid", sorted(ROWS))
def test_a_row_delivers_its_whole_entries_in_one_window(rid, tmp_path):
    """F2: repeat the matching input in one window until the hook has nothing new. Every block's body is whole entries
    (the next ones of its row not yet in the window), every line of the row arrives once and in order (a line another
    row of the same skill delivered first counts), and each call stays within 2,048 bytes."""
    name, ti = FIXTURES[rid][0]
    seen, got = set(), []                                     # (skill, line) delivered in this window; this row's lines
    for n in range(10):
        ctx = context(run(PRE, tool(name, ti), tmp_path))
        rec = telemetry(tmp_path)[-1]
        assert rid in rec["matched"], (n, rec)
        assert len(ctx.encode("utf-8")) <= 2048 and rec["bytes"] == len(ctx.encode("utf-8"))
        for label, body, ptr, skill in blocks(ctx):
            row = ROWS[row_of(label)]
            assert ptr == pointer(row)
            text = [x for x in body if x != "…"]
            fresh = [u for u in ([x for x in u if (skill, x) not in seen] for u in units(row)) if u]
            assert any(text == sum(fresh[:k], []) for k in range(1, len(fresh) + 1)), (row["id"], "not whole entries")
            if row["id"] == rid:
                got += text
            seen |= {(skill, x) for x in text}
        if not ctx:
            break
    else:
        pytest.fail("the row never finished in ten calls")
    want = [x for u in units(ROWS[rid]) for x in u]
    assert [x for x in want if (ROWS[rid]["skill"], x) not in seen] == []           # every line arrived
    assert got == [x for x in want if x in got] and len(got) == len(set(got))       # in order, each once


@pytest.mark.parametrize("rid", sorted(ROWS))
def test_a_row_stays_silent_on_a_near_miss(rid, tmp_path):
    name, ti = FIXTURES[rid][1]
    ctx = context(run(PRE, tool(name, ti), tmp_path))
    assert f"[system1 · {rid}]" not in ctx
    assert rid not in telemetry(tmp_path)[-1]["matched"]


# ---- F2: whole entries, statically, and the text the verifier named

# The runs that stay inside an entry only until the coordinator applies the skill line breaks proposed in
# tasks/briefs/system1/S1-L1-R1-report.md (the skills are outside the S1-L1-R1 boundary). Each maps to the test that
# says whether its break is in: once it is, that run must be whole like every other.
PENDING_BREAKS = {
    ("ops-script", "end"): ("env-tool-quirks", lambda L: any(x.startswith("**`scripts/anchor_edit.py`") for x in L)),
    ("anchor-edit", "start"): ("env-tool-quirks", lambda L: any(x.startswith("**`scripts/anchor_edit.py`") for x in L)),
    ("ouroboros", "end"): ("ouroboros-stdio", lambda L: any(x.startswith("**Resume uses the EXACT") for x in L)),
    ("stamp", "start"): ("build-loop", lambda L: any(not L[i - 1].strip() and L[i].startswith(
        "   Test counts in reports and commit messages are PASTED") for i in range(1, len(L)))),
}


def test_every_row_is_whole_entries():
    """F2: each run of a row's lines starts where a skill entry starts and ends where one ends (the verifier's
    rows_static.py, with this file's own parser). The hook's entry rule is this file's."""
    assert _module(HOOK, "s1_entries").ENTRY_START_RX.pattern == ENTRY_RX.pattern
    bad = set()
    for row in TABLE["rows"]:
        lines, s, e, idx = resolved(row)
        runs = [[idx[0]]]
        for i in idx[1:]:
            runs[-1].append(i) if i == runs[-1][-1] + 1 else runs.append([i])
        for run_ in runs:
            a, b = run_[0], run_[-1]
            if not (ENTRY_RX.match(lines[a]) or not lines[a - 1].strip() or HEAD_RX.match(lines[a - 1])):
                bad.add((row["id"], "start"))
            if not (b + 1 >= e or not lines[b + 1].strip() or ENTRY_RX.match(lines[b + 1])):
                bad.add((row["id"], "end"))
    pending = {k for k, (skill, applied) in PENDING_BREAKS.items() if not applied(skill_lines(skill))}
    assert bad == pending


def test_the_rows_carry_the_text_the_verifier_named():
    """F2: the push qualifier, push-delegate-work from its first word to its last sentence, the NaN numeric-guard rule,
    and the two rows carried from the S1-L1 harvest."""
    def text(rid):
        lines, _, _, idx = resolved(ROWS[rid])
        return [lines[i] for i in idx]
    push = text("push")
    assert any(x.startswith("*(Since CTX1, D-089, no automatic `gitnexus analyze`") for x in push)
    assert any(x.startswith("**`push_clean.sh --lanes-live` counts TRACKED dirty files only**") for x in push)
    pdw = text("push-delegate-work")
    assert pdw[0].startswith("(f) **A push publishes EVERY local boundary, reviewed or not: run `git log")
    assert pdw[-1].endswith("race and triggers a needless continuity alarm (bit 2026-08-24).**")
    for rid in ("test-edit", "gate-edit-tactics"):
        assert any("NaN is a fail-open WORMHOLE" in x for x in text(rid))
    order = [r["id"] for r in TABLE["rows"]]
    assert order.index("push-delegate-work") < order.index("push")
    for rid in ("brief-registers-hook", "hook-installer"):
        assert ROWS[rid]["heading"].startswith("A lane that registers a hook changes the coordinator's own session")


def test_the_first_push_of_a_window_brings_the_whole_orchestration_entry(tmp_path):
    """F2's budget half: "Push the REVIEWED SHA explicitly … never HEAD" never arrived in 19 of 131 windows. Now the
    orchestration entry goes first and whole, and push's entries follow, each whole, on the next push calls."""
    payload = tool(*bash("git -C /home/user/agent-factory push origin 1a2b3c4:claude/x"))
    first = blocks(context(run(PRE, payload, tmp_path)))
    assert row_of(first[0][0]) == "push-delegate-work"
    assert [x for x in first[0][1] if x != "…"] == units(ROWS["push-delegate-work"])[0]
    assert "never HEAD.**" in "\n".join(first[0][1])
    later = [b for _ in range(3) for b in blocks(context(run(PRE, payload, tmp_path)))]
    assert [x for b in later if row_of(b[0]) == "push" for x in b[1] if x != "…"] == sum(units(ROWS["push"]), [])


# ---- once per context window, and the reset

def test_once_per_window_and_the_reset(tmp_path):
    commit = tool(*bash("git commit -m 'fix: the thing'"))
    first = context(run(PRE, commit, tmp_path))
    assert "[system1 · commit]" in first and "[system1 · commit-increment]" in first
    assert context(run(PRE, commit, tmp_path)) == ""                          # the same window: nothing again
    assert {s["why"] for s in telemetry(tmp_path)[-1]["skipped"]} == {"duplicate"}
    sub = tool(*bash("git commit -m 'fix: the thing'"), agent="agent-a1")      # a subagent is another window
    assert "[system1 · commit]" in context(run(PRE, sub, tmp_path))
    other = tool(*bash("git commit -m 'fix'"), sid="s1test-session-0002")
    assert "[system1 · commit]" in context(run(PRE, other, tmp_path))

    def session_start(source, agent=None):
        r = run(START, start(source, agent=agent), tmp_path)
        assert (r.returncode, r.stdout) == (0, b"")                           # the reset prints nothing

    session_start("startup")
    assert context(run(PRE, commit, tmp_path)) == ""                          # a startup keeps the window
    session_start("compact")
    assert "[system1 · commit]" in context(run(PRE, commit, tmp_path))       # the compacted main window forgets
    assert context(run(PRE, sub, tmp_path)) == ""                             # the subagent's window did not compact
    for source in ("resume", "clear"):
        session_start(source)
        assert "[system1 · commit]" in context(run(PRE, commit, tmp_path))   # every window of the session forgets
        assert "[system1 · commit]" in context(run(PRE, sub, tmp_path))
    assert context(run(PRE, tool(*bash("git commit -m 'fix'"), sid="s1test-session-0002"), tmp_path)) == ""
    resets = [r for r in telemetry(tmp_path) if r["event"] == "SessionStart"]
    assert [r["source"] for r in resets] == ["startup", "compact", "resume", "clear"]
    assert [r["removed"] for r in resets] == [0, 1, 2, 2]


def test_the_reset_prunes_markers_idle_for_seven_days(tmp_path):
    """Markers, locks and temp files of a session gone for eight days go at any SessionStart; a live one stays."""
    seen = tmp_path / "system1-seen"
    seen.mkdir()
    old = time.time() - 8 * 86400
    for name in ("gone.main.json", "gone.main.json.lock", "gone.main.json.4242.tmp", "gone.agentY.json"):
        (seen / name).write_text('{"keys": []}')
        os.utime(seen / name, (old, old))
    (seen / "live.main.json").write_text('{"keys": []}')
    r = run(START, start("startup", sid="another-session"), tmp_path)
    assert (r.returncode, r.stdout) == (0, b"")
    assert sorted(p.name for p in seen.iterdir()) == ["live.main.json"]
    assert telemetry(tmp_path)[-1]["removed"] == 2                            # the two markers (.json)


# ---- the two budgets

def test_the_tool_budget_takes_whole_entries_and_keeps_the_pointer(tmp_path):
    """Four rows match one pc_suite call. Each call stays within 2,048 bytes, every block keeps its pointer, an entry
    that does not fit waits for the next call, whole, and over the calls every row's lines arrive once and in order."""
    payload = tool(*bash("bash scripts/pc_suite.sh launch -n 8 -- tests/test_vendored_manifest.py"))
    got = collections.defaultdict(list)
    for n in range(8):
        ctx = context(run(PRE, payload, tmp_path))
        rec = telemetry(tmp_path)[-1]
        assert len(ctx.encode("utf-8")) <= 2048 and rec["bytes"] == len(ctx.encode("utf-8"))
        if not ctx:
            break
        for label, body, ptr, skill in blocks(ctx):
            assert ptr == pointer(ROWS[row_of(label)])
            got[row_of(label)] += [x for x in body if x != "…"]
    first = telemetry(tmp_path)[0]
    assert {s["row"] for s in first["skipped"] if s["why"] == "budget"}        # the cap acted on the first call
    assert n >= 2                                                             # and a later call carried the rest
    for rid in first["matched"]:
        want = [x for u in units(ROWS[rid]) for x in u]
        delivered = [x for r2, xs in got.items() if ROWS[r2]["skill"] == ROWS[rid]["skill"] for x in xs]
        assert [x for x in want if x not in delivered] == [], rid
        assert got[rid] == [x for x in want if x in got[rid]] and len(got[rid]) == len(set(got[rid])), rid


def test_the_budget_counts_bytes_not_characters():
    """A unit whose characters fit the room but whose UTF-8 bytes do not waits for a later call; one byte less and it
    goes. The boundary sits inside a two-byte character."""
    s1 = _module(HOOK, "s1_bytes")
    label, ptr = "L", s1.skill_pointer("s", "h")
    room = 300 - len(label.encode()) - len(ptr.encode()) - 2
    ok = "é" * ((room - 1) // 2)                                              # 2 bytes each, plus its newline: fits
    over = ok + "é"                                                           # one character more: over by bytes only
    assert len(ok.encode()) + 1 <= room < len(over.encode()) + 1 and len(over) + 1 <= room
    text, injected, skipped, new = s1.compose([("r", "s", "h", [[(0, over)]], label)], set(), 300)
    assert (text, skipped) == ("", [{"row": "r", "key": "s § h", "why": "budget"}])
    text, injected, skipped, new = s1.compose([("r", "s", "h", [[(0, ok)]], label)], set(), 300)
    assert text.split("\n") == [label, ok, ptr] and len(text.encode()) <= 300 and injected[0]["lines"] == 1


def _score(matched):
    return float(matched.rsplit("(", 1)[1].rstrip(")"))


def test_the_prompt_budget(tmp_path):
    # one long section: its excerpt is cut at the share (half the prompt budget), the pointer kept. The next section
    # passed its gate (matched lists only those) but scores under SECOND_EXCERPT_RATIO of the best: one excerpt only.
    ask = "anti hollow green: the negative control on every gate and the mutation check"
    ctx = context(run(PROMPT, prompt(ask), tmp_path / "a"))
    rec = telemetry(tmp_path / "a")[-1]
    assert rec["event"] == "UserPromptSubmit" and 0 < rec["bytes"] == len(ctx.encode("utf-8")) <= 2048
    assert len(blocks(ctx)) == 1 and rec["injected"][0]["cut"] > 0
    s1 = _module(HOOK, "s1_ratio")
    best, second = _score(rec["matched"][0]), _score(rec["matched"][1])
    assert second < s1.SECOND_EXCERPT_RATIO * best                               # de-vacuous: the case is the boundary
    # two sections that score alike: two excerpts, each within its share, both within 4,096
    for k, ask in enumerate(("claude 5 prompting and delegation: how to write the brief",
                             "bug echo after the fix, find similar bugs")):
        ctx = context(run(PROMPT, prompt(ask), tmp_path / f"b{k}"))
        rec = telemetry(tmp_path / f"b{k}")[-1]
        assert len(blocks(ctx)) == 2 and 0 < rec["bytes"] == len(ctx.encode("utf-8")) <= 4096
        assert all(i["bytes"] <= 2048 for i in rec["injected"])
    # a short prompt that names a project skill still reaches its section (the project skills keep their reach)
    assert "§ Trace the chain" in context(run(PROMPT, prompt("trace the chain from the hook to the model"), tmp_path / "c"))


def test_the_prompt_path_filters_and_never_repeats(tmp_path):
    ask = prompt("claude 5 prompting and delegation: how to write the brief")
    first = blocks(context(run(PROMPT, ask, tmp_path)))
    again = context(run(PROMPT, ask, tmp_path))                                # the cut remainder, never a repeat
    assert again and not set(again.split("\n")) & {x for _, body, _, _ in first for x in body if x != "…"}
    for chat in ("thanks", "ok continue", "yes do it",                       # no heading shares a word
                 "commit the fix", "please fix the typo in the README"):     # a heading does, under MIN_PROMPT_SCORE
        assert context(run(PROMPT, prompt(chat), tmp_path)) == ""
    assert telemetry(tmp_path)[-1]["matched"] == []
    event = "<task-notification> the resume after compaction protocol, fetch origin and compare the three clocks"
    assert context(run(PROMPT, prompt(event), tmp_path)) == ""
    assert telemetry(tmp_path)[-1]["why"] == "harness-event"
    assert "SESSION-RESUME" in context(run(PROMPT, prompt(event.split(">", 1)[1]), tmp_path))   # the control


def test_a_prompt_whose_first_line_is_too_long_still_gets_its_pointer(tmp_path):
    """F4: the best section's excerpt starts at a line longer than the share, so no line of it can go; its label and
    pointer still reach the model, once per window."""
    # The prompt picks pc-bridge-lanes § Launching, re-attaching and sizing PC lanes, whose best entry for these words is
    # its 4,800-byte first line. A skill edit that adds a shorter entry matching the prompt better moves the excerpt's
    # start (the D-099 lesson did, on "sizing" and "lane"; CI run #1105): re-point the prompt, never the assertions.
    ask = prompt("launching and re-attaching pc lanes")
    ctx = context(run(PROMPT, ask, tmp_path))
    rec = telemetry(tmp_path)[-1]
    best = rec["matched"][0].rsplit(" (", 1)[0]
    skill, heading = best.split(" § ", 1)
    ptr = f"full details: .claude/skills/{skill}/SKILL.md § {heading}"
    assert ptr in ctx.split("\n")
    only = [b for b in blocks(ctx, pointer_only_ok=True) if b[2] == ptr]
    assert len(only) == 1 and only[0][1] == []                                # label and pointer, no line
    inj = [i for i in rec["injected"] if i["key"] == best]
    assert inj and inj[0]["lines"] == 0 and inj[0]["cut"] > 0                  # de-vacuous: its lines did not fit
    assert ptr not in context(run(PROMPT, ask, tmp_path))                     # once per window


def test_a_one_word_lead_needs_a_higher_score(tmp_path, monkeypatch):
    """F5: a section with ONE lead word (a description, heading or name word that few skills hold) needs
    ONE_LEAD_MIN_SCORE. The case: `metadata`, the one lead of bug-echo § Metadata keys in this prompt. Opening the
    two-lead gates changes nothing; opening the one-lead gate lets it through: the one-lead gate is the reason."""
    ask = "why keep the metadata keys at all"
    assert context(run(PROMPT, prompt(ask), tmp_path)) == ""
    s1 = _module(HOOK, "s1_lead")
    table, cache = s1.load_table(), str(tmp_path / "cache.json")
    for name in ("MIN_PROMPT_SCORE", "SHORT_MIN_SCORE"):
        monkeypatch.setattr(s1, name, 0.0)
    assert s1.plan_prompt({"prompt": ask}, table, set(), cache)[1]["matched"] == []
    monkeypatch.setattr(s1, "ONE_LEAD_MIN_SCORE", 0.0)
    rec = s1.plan_prompt({"prompt": ask}, table, set(), cache)[1]
    assert rec["matched"][0].startswith("bug-echo § Metadata keys (")
    assert _score(rec["matched"][0]) < _module(HOOK, "s1_lead2").ONE_LEAD_MIN_SCORE
    # the verifier's F5 case drew "Repair briefs …" on the word "unit"; now only pc-bridge-lanes, whose description
    # names a PC-side systemctl command, may answer it
    sysd = context(run(PROMPT, prompt("the systemctl user unit restart on the PC failed with XDG_RUNTIME_DIR"), tmp_path))
    assert "Repair briefs" not in sysd and {b[3] for b in blocks(sysd, pointer_only_ok=True)} <= {"pc-bridge-lanes"}
    # a prompt with several lead words still goes: the resume protocol
    assert "SESSION-RESUME" in context(run(PROMPT, prompt(
        "the resume after compaction protocol, fetch origin and compare the three clocks"), tmp_path))


# ---- the kill switch, the telemetry line, an exception

def test_the_kill_switch(tmp_path):
    payload = tool(*bash("git commit -m 'x'"))
    (tmp_path / "system1-off").write_text("")
    for cmd, p in ((PRE, payload), (PROMPT, prompt("contract gate: negotiate the contract"))):
        r = run(cmd, p, tmp_path)
        assert (r.returncode, r.stdout, r.stderr) == (0, b"", b"")
    assert telemetry(tmp_path) == []
    (tmp_path / "system1-off").unlink()
    assert "[system1 · commit]" in context(run(PRE, payload, tmp_path))      # the control: on again


def test_a_dangling_link_named_system1_off_switches_it_off_too(tmp_path):
    """F12: the switch is the NAME, so a symlink whose target is gone still counts."""
    (tmp_path / "system1-off").symlink_to(tmp_path / "nowhere")
    for cmd, p in ((PRE, tool(*bash("git commit -m 'x'"))), (PROMPT, prompt("contract gate: negotiate the contract"))):
        r = run(cmd, p, tmp_path)
        assert (r.returncode, r.stdout, r.stderr) == (0, b"", b"")
    assert telemetry(tmp_path) == []


def test_the_telemetry_line(tmp_path):
    canary = "S1CANARY7F3A"
    context(run(PRE, tool(*bash(f"git commit -m '{canary}'")), tmp_path))
    context(run(PROMPT, prompt(f"contract gate {canary}"), tmp_path))
    raw = (tmp_path / "system1.jsonl").read_text(encoding="utf-8")
    assert canary not in raw                                                  # ids and counts, never the input
    pre, ups = telemetry(tmp_path)
    assert pre["event"] == "PreToolUse" and pre["tool"] == "Bash" and pre["window"] == f"{SID}.main"
    assert pre["matched"] == ["commit", "commit-increment"] and pre["skipped"] == []
    assert [(i["row"], i["key"]) for i in pre["injected"]] == [
        ("commit", "env-tool-quirks § Shell, git, commit-helper and tool quirks"),
        ("commit-increment", "build-loop § The operative core (CLAUDE.md's index of this skill)")]
    assert pre["bytes"] > 0 and all(i["lines"] > 0 and i["bytes"] > 0 for i in pre["injected"])
    assert isinstance(pre["ms"], float) and pre["t"].endswith("Z")
    assert ups["event"] == "UserPromptSubmit" and ups["matched"] and ups["injected"]
    marker = tmp_path / "system1-seen" / f"{SID}.main.json"
    assert (marker.stat().st_mode & 0o777) == 0o600 and ((tmp_path / "system1.jsonl").stat().st_mode & 0o777) == 0o600


def test_no_input_text_reaches_any_state_file(tmp_path):
    """F10: a lower-case canary (the prompt path lower-cases words) in a Write path and its text, an Edit path and both
    strings, a command and a prompt; then every file under the state dir (telemetry, marker, lock, prompt cache) is
    searched for it and for its hex part."""
    canary = "cnry" + secrets.token_hex(8)
    calls = [(PRE, tool(*write(f"tasks/briefs/{canary}/X-brief.md", f"# {canary}\nMODIFY `.claude/settings.json`\n"))),
             (PRE, tool(*edit(f"tests/test_{canary}.py", f"assert '{canary}'", old=canary))),
             (PRE, tool(*bash(f"git commit -m '{canary}' && git push origin HEAD:{canary}"))),
             (PROMPT, prompt(f"negotiate the contract gate {canary} before the build and write the brief")),
             (PROMPT, prompt(f"<task-notification> {canary}"))]
    outs = [run(cmd, p, tmp_path) for cmd, p in calls]
    tel = telemetry(tmp_path)
    assert [bool(r.get("injected")) for r in tel] == [True, True, True, True, False]   # the canaries rode real work
    files = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert {"system1.jsonl", "system1-cache.json", f"{SID}.main.json", f"{SID}.main.json.lock"} <= {p.name for p in files}
    for p in files:
        data = p.read_bytes()
        assert canary.encode() not in data and canary[4:].encode() not in data, p.name
    for r in outs:
        assert canary[4:].encode() not in r.stdout + r.stderr


def test_an_exception_injects_nothing_and_logs_its_type(tmp_path):
    payload = tool(*bash("git commit -m 'x'"))
    marker = tmp_path / "system1-seen" / f"{SID}.main.json"
    marker.mkdir(parents=True)                                                # the marker cannot be read
    r = run(PRE, payload, tmp_path)
    assert (r.returncode, r.stdout) == (0, b"")
    rec = telemetry(tmp_path)[-1]
    assert (rec["event"], rec["tool"], rec["error"]) == ("PreToolUse", "Bash", "OSError") and "injected" not in rec
    assert rec["window"] == f"{SID}.main"                                     # which window failed: ids only
    marker.rmdir()
    os.mkfifo(marker)                                                         # a FIFO must not hang the hook
    t0 = time.monotonic()
    r = run(PRE, payload, tmp_path, timeout=30)
    assert (r.returncode, r.stdout) == (0, b"") and time.monotonic() - t0 < 20
    assert telemetry(tmp_path)[-1]["error"] == "OSError"
    marker.unlink()
    assert "[system1 · commit]" in context(run(PRE, payload, tmp_path))      # the control: the same call injects


def test_bad_input_never_blocks(tmp_path):
    for data in (b"", b"not json", b"[1, 2]", b"null", json.dumps({"hook_event_name": "Stop"}).encode(),
                 json.dumps(tool("Bash", "not a dict")).encode(), json.dumps(tool("Read", {"file_path": "x"})).encode()):
        for cmd in (PRE, PROMPT):
            r = run(cmd, data, tmp_path)
            assert (r.returncode, r.stdout) == (0, b""), (data, r.stdout, r.stderr)


def test_a_stdin_that_never_closes_does_not_hang_the_reset(tmp_path):
    env = dict(os.environ, AF_SYSTEM1_STATE=str(tmp_path))
    proc = subprocess.Popen([sys.executable, str(HOOK), "--reset"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env)
    try:
        t0 = time.monotonic()
        assert proc.wait(timeout=15) == 0 and time.monotonic() - t0 < 10     # the bounded read gives up
        assert proc.stdout.read() == b""
    finally:
        proc.kill()
        proc.stdin.close()


def test_a_failed_marker_write_leaves_no_temp_file(tmp_path):
    """F9: with every write refused (ulimit -f 0), the call injects nothing and its <marker>.<pid>.tmp is gone."""
    r = run(PRE, tool(*bash("git commit -m 'x'")), tmp_path, prefix="ulimit -f 0; ")
    assert (r.returncode, r.stdout) == (0, b"")
    seen = tmp_path / "system1-seen"
    assert (seen / f"{SID}.main.json.lock").exists()                          # de-vacuous: it reached the marker write
    assert [p.name for p in seen.iterdir() if p.name.endswith(".tmp")] == []


# ---- F8: the window lock

def test_a_held_lock_injects_nothing_and_logs_why(tmp_path):
    """F8: another holder keeps the window's lock past LOCK_WAIT_S: the call injects nothing (so no line goes twice),
    writes no marker (so no key is lost) and logs the timeout. Released, the same call injects."""
    payload = tool(*bash("git commit -m 'x'"))
    seen = tmp_path / "system1-seen"
    seen.mkdir()
    fd = os.open(seen / f"{SID}.main.json.lock", os.O_WRONLY | os.O_CREAT, 0o600)
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        r = run(PRE, payload, tmp_path)
        assert (r.returncode, r.stdout) == (0, b"")
        rec = telemetry(tmp_path)[-1]
        assert (rec["event"], rec["tool"], rec["error"], rec["window"]) == ("PreToolUse", "Bash", "WindowLockTimeout",
                                                                         f"{SID}.main")
        assert not (seen / f"{SID}.main.json").exists()
    finally:
        os.close(fd)
    assert "[system1 · commit]" in context(run(PRE, payload, tmp_path))      # the control: the lock free


def test_a_parallel_burst_on_one_window_never_repeats_or_loses_a_line(tmp_path):
    """F8 and F10: twelve calls of one window at once. No line reaches the model twice, every line that reached it is
    in the marker, and the only error a call may log is a lock timeout (it then injects nothing)."""
    cmds = ["git commit -m x && git push origin HEAD:claude/x", "bash scripts/pc.sh 'sqlite3 a.db; podman ps'",
            "bash scripts/pc_suite.sh launch -- tests/test_vendored_manifest.py", "nohup python3 x.py > l 2>&1 &",
            "python3 scripts/anchor_edit.py f --replace a b", "pgrep -f '[x]' ; graft ask q"]
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT), AF_SYSTEM1_STATE=str(tmp_path), CLAUDE_CODE_REMOTE="false")
    procs = [subprocess.Popen(["sh", "-c", PRE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              env=env, cwd="/") for _ in range(12)]
    for k, p in enumerate(procs):
        p.stdin.write(json.dumps(tool(*bash(cmds[k % len(cmds)]))).encode())
        p.stdin.close()
    delivered = collections.Counter()
    for p in procs:
        out = p.stdout.read()
        assert p.wait(timeout=60) == 0
        ctx = unstamp(json.loads(out)["hookSpecificOutput"]["additionalContext"]) if out.strip() else ""
        for label, body, ptr, skill in blocks(ctx):
            delivered.update((skill, x) for x in body if x != "…")
    assert delivered and max(delivered.values()) == 1
    keys = set(json.loads((tmp_path / "system1-seen" / f"{SID}.main.json").read_text())["keys"])
    assert [k for k in delivered if line_key(*k) not in keys] == []
    assert {r.get("error") for r in telemetry(tmp_path)} <= {None, "WindowLockTimeout"}


# ---- F16, F17 and the unresolved row: one bad row or file, through the registered command on a copy

def test_an_unresolved_row_is_skipped_through_the_registered_command(tmp_path):
    root = copy_repo(tmp_path / "repo")
    skill = root / ".claude" / "skills" / "env-tool-quirks" / "SKILL.md"
    anchor = ROWS["commit"]["lines"][0]
    text = skill.read_text(encoding="utf-8")
    assert text.count(anchor) == 1
    skill.write_text(text.replace(anchor, anchor.replace("safe_commit", "safe-commit")), encoding="utf-8")
    ctx = context(run(PRE, tool(*bash("git commit -m 'x'")), tmp_path / "st", root=root))
    assert "[system1 · commit-increment]" in ctx and "[system1 · commit]" not in ctx
    rec = telemetry(tmp_path / "st")[-1]
    assert [(s["row"], s["why"]) for s in rec["skipped"]] == [("commit", "unresolved")] and "error" not in rec


def test_one_bad_row_skips_itself_only(tmp_path):
    """F16: a row pattern that does not compile, or a skill file that is gone, skips that row; the others inject, and
    the skip logs the type (`re.error`, not a bare `error`)."""
    root = copy_repo(tmp_path / "repo")
    table_path = root / ".claude" / "hooks" / "system1-situations.json"
    t = json.loads(table_path.read_text(encoding="utf-8"))
    t["rows"][0]["command"] = "pc\\.sh(("
    table_path.write_text(json.dumps(t), encoding="utf-8")
    ctx = context(run(PRE, tool(*bash("git commit -m 'x'")), tmp_path / "a", root=root))
    assert "[system1 · commit]" in ctx and "[system1 · commit-increment]" in ctx
    assert [(s["row"], s["why"], s["error"]) for s in telemetry(tmp_path / "a")[-1]["skipped"]] == [
        (t["rows"][0]["id"], "error", "re.error")]
    shutil.rmtree(root / ".claude" / "skills" / "env-tool-quirks")
    ctx = context(run(PRE, tool(*bash("git commit -m 'y'")), tmp_path / "b", root=root))
    assert "[system1 · commit-increment]" in ctx and "[system1 · commit]" not in ctx
    assert ("commit", "error", "FileNotFoundError") in [
        (s["row"], s["why"], s.get("error")) for s in telemetry(tmp_path / "b")[-1]["skipped"]]


def _unblock(fifo):
    """Open a FIFO for writing so a reader stuck on it (a hook without the fix) returns."""
    try:
        os.close(os.open(fifo, os.O_WRONLY | os.O_NONBLOCK))
    except OSError:
        pass


def test_skill_and_table_reads_never_block_on_a_fifo(tmp_path):
    """F17: a FIFO in place of a skill file skips that skill's rows at once; a FIFO in place of the table fails the call
    quietly at once. Neither waits for a writer."""
    root = copy_repo(tmp_path / "repo")
    fifo = root / ".claude" / "skills" / "env-tool-quirks" / "SKILL.md"
    fifo.unlink()
    os.mkfifo(fifo)
    try:
        t0 = time.monotonic()
        r = run(PRE, tool(*bash("git commit -m 'x'")), tmp_path / "a", root=root, timeout=20)
        assert time.monotonic() - t0 < 10
        assert "[system1 · commit-increment]" in context(r)
        assert ("commit", "error", "OSError") in [
            (s["row"], s["why"], s.get("error")) for s in telemetry(tmp_path / "a")[-1]["skipped"]]
    finally:
        _unblock(fifo)
    table = root / ".claude" / "hooks" / "system1-situations.json"
    table.unlink()
    os.mkfifo(table)
    try:
        t0 = time.monotonic()
        r = run(PRE, tool(*bash("git commit -m 'x'")), tmp_path / "b", root=root, timeout=20)
        assert time.monotonic() - t0 < 10 and (r.returncode, r.stdout) == (0, b"")
        assert telemetry(tmp_path / "b")[-1]["error"] == "OSError"
    finally:
        _unblock(table)


# ---- F1, F6, F7: what counts as a command

@pytest.mark.parametrize("cmd", ["while pgrep -f '[l]ane_gate' >/dev/null; do sleep 5; done",
                                 "until ! pgrep -f hermes; do sleep 1; done",
                                 "if pgrep -x hermes >/dev/null; then echo up; fi",
                                 "{ pgrep -f y; } || true",
                                 "x=1 && ! pkill -f z"])
def test_loop_and_group_keywords_start_a_command(cmd, tmp_path):
    """F1: `while`, `until`, `if`, `elif`, `!` and `{` start a command position."""
    assert "[system1 · pgrep]" in context(run(PRE, tool(*bash(cmd)), tmp_path))


F6_CASES = [
    # data: a commit message, a pattern, a heredoc for cat or python, a message built from a heredoc, a comment
    ('git commit -m "fix: then git push later"', {"commit"}, {"push", "push-delegate-work"}),
    ("grep -n 'x; git push' CLAUDE.md", set(), {"push"}),
    ("cat > /tmp/r.md <<'EOF'\nbash scripts/pc.sh 'uptime'\ngit push origin HEAD\nEOF\necho done", set(),
     {"pc-call", "push"}),
    ("python3 - <<'PY'\nimport os\nos.system('x; git push')\nPY", set(), {"push"}),
    ("git commit -m \"$(cat <<'EOF'\nfix: then git push; pgrep x\nEOF\n)\"", {"commit"}, {"push", "pgrep"}),
    ("ls  # then git push", set(), {"push"}),
    # code a shell reads: a pc.sh or ssh command line, bash -c, a heredoc fed to bash, a substitution in quotes
    ("bash scripts/pc.sh 'pgrep -f hermes'", {"pc-call", "pgrep"}, set()),
    ("bash -c 'git push origin HEAD:x'", {"push"}, set()),
    ('ssh pc "pgrep -f y && sudo systemctl restart z"', {"pgrep"}, set()),
    ("bash <<'EOF'\ngit push origin HEAD:x\nEOF", {"push"}, set()),
    ('echo "$(git push origin HEAD:x)"', {"push"}, set()),
    # a `\` + newline joins two lines into one command: the script after an interpreter is still its command word,
    # and a word after `echo` is still an argument
    ("python3 \\\n  scripts/proof-runner run --proof S0-01 --venue sandbox", {"proof-regen"}, set()),
    ("echo a \\\n  git push origin HEAD:x", set(), {"push"}),
]


@pytest.mark.parametrize("cmd,fires,silent", F6_CASES)
def test_quoted_and_heredoc_text_is_data_unless_a_shell_reads_it(cmd, fires, silent, tmp_path):
    """F6: a command row matches shell code only."""
    context(run(PRE, tool(*bash(cmd)), tmp_path))
    matched = set(telemetry(tmp_path)[-1]["matched"])
    assert fires <= matched and not silent & matched, matched


def test_the_command_scan_is_linear():
    """F7: the old scan rescanned the rest of a run from every separator (40,000 ';' took 2.6 s). Now each of these
    takes under 100 ms in process, the best of three: the verifier's 198 KB heredoc among them."""
    s1 = _module(HOOK, "s1_linear")
    table = s1.load_table()

    def best_ms(f):
        ts = []
        for _ in range(3):
            t0 = time.perf_counter()
            f()
            ts.append(time.perf_counter() - t0)
        return min(ts) * 1000

    assert best_ms(lambda: s1.command_positions("echo " + ";" * 40000)) < 100
    body = "a&&b||c(d);" * 18000                                             # 198 KB of minified-JS-like text
    for cmd in ("cat > /tmp/x.js <<'EOF'\n" + body + "\nEOF\n",             # data
                "bash <<'EOF'\n" + body + "\nEOF\n",                         # code a shell reads
                "echo " + ";" * 198000):
        payload = {"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": str(ROOT)}
        assert best_ms(lambda: s1.plan_tool(payload, table, set())) < 100, cmd[:14]


# ---- the table against the skills, and a drift guard

def test_every_row_resolves_and_each_entry_fits_a_call_alone():
    s1 = _module(HOOK, "system1_context_under_test")
    table = s1.load_table()
    assert len(table["rows"]) == len(ROWS) and all(set(r["tools"]) <= set(s1.TOOLS) for r in table["rows"])
    for row in table["rows"]:
        rx = s1.detectors(row)                                                # every regex compiles
        assert any(rx[k] for k in ("path", "command", "command_any", "text")), row["id"]
        assert "/" not in row.get("command", ""), row["id"]                  # matched at the command word
        lines, sections = s1.parse_skill((ROOT / ".claude" / "skills" / row["skill"] / "SKILL.md").read_text())
        idx = s1.resolve(row, lines, sections)
        label = f"[system1 · {row['id']}] skill {row['skill']}, the governing lines verbatim:"
        for unit in units(row):                                               # an entry that never fits never arrives
            need = len(label.encode()) + sum(len(x.encode()) + 1 for x in unit) + len(pointer(row).encode()) + 1
            assert need <= s1.TOOL_BUDGET, (row["id"], unit[0][:40], need)
        assert lines[idx[0]] == first_line(row) and row["source"]
    for skill in PROJECT:
        assert (ROOT / ".claude" / "skills" / skill / "SKILL.md").is_file(), skill


def test_a_changed_skill_line_is_reported_unresolved_not_injected(tmp_path):
    s1 = _module(HOOK, "system1_context_drift")
    row = dict(ROWS["commit"], lines=["**a line no skill holds"])
    lines, sections = s1.parse_skill((ROOT / ".claude" / "skills" / "env-tool-quirks" / "SKILL.md").read_text())
    with pytest.raises(LookupError):
        s1.resolve(row, lines, sections)


def test_the_harness_event_prefixes_are_wiki_contexts():
    assert (_module(HOOK, "s1_prefixes").HARNESS_EVENT_PREFIXES
            == _module(HOOKS / "wiki-context.py", "wiki_context_prefixes").HARNESS_EVENT_PREFIXES)


# ---- the commands install_session_hooks.py writes (the /home/user-rooted session)

def test_the_installed_commands_reach_the_model_form(tmp_path):
    target = tmp_path / "settings.json"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "install_session_hooks.py"), "--target", str(target)],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    hooks = json.loads(target.read_text())["hooks"]
    pre = [h["command"] for g in hooks["PreToolUse"] for h in g["hooks"] if "system1-context.py" in h["command"]]
    ups = [h["command"] for g in hooks["UserPromptSubmit"] for h in g["hooks"] if "system1-context.py" in h["command"]]
    assert len(pre) == len(ups) == 1
    env = dict(os.environ, AF_SYSTEM1_STATE=str(tmp_path / "st"))
    env.pop("CLAUDE_PROJECT_DIR", None)
    for cmd, payload, want in ((pre[0], tool(*bash("git commit -m 'x'")), "[system1 · commit]"),
                               (ups[0], prompt("contract gate: negotiate the contract"), "[system1 · prompt]")):
        r = subprocess.run(["sh", "-c", cmd], input=json.dumps(payload).encode(), capture_output=True, timeout=60,
                           env=env, cwd="/")
        assert want in context(r)


# ---- S1-ALL (D-093): the prompt path reads every skill under .claude/skills. Each test below names its red on the PIN.

LIBRARY_ASK = "convene the council on the memory design"
RWKV_ASK = "fine-tune rwkv on one gpu: how do we train an rwkv model and compare rwkv with transformers"
ENV_LOG = ("Loaded env from /srv/app/.env\nwarning: REQUIRE_API_KEY in /srv/app/.env is ignored, set it first\n"
           "listening on 0.0.0.0:20128\nhealth check ok (200)\ndashboard ready at http://localhost:20128/dashboard\n"
           "session store: sqlite at /srv/app/data/app.db\nprovider registry loaded: 14 providers, 3 combos\n") * 8


def fixture_skill(root, name, description, sections):
    """Write a library skill into a copied tree: its frontmatter, a title, and `sections` [(heading, [lines])]."""
    d = root / ".claude" / "skills" / name
    d.mkdir(parents=True, exist_ok=True)
    body = [f"# {name}", "", "A fixture skill for tests/test_system1_context.py.", ""]
    for heading, lines in sections:
        body += [f"## {heading}", ""] + lines + [""]
    p = d / "SKILL.md"
    p.write_text(f"---\nname: {name}\ndescription: {description}\n---\n\n" + "\n".join(body), encoding="utf-8")
    return p


GLIMMER = ("zqx-glimmer", "Tune a zqx glimmer lattice before a glimmer run.",
           [("Glimmer lattice tuning", ["1. Pin the zqx glimmer lattice seed before the run.",
                                        "2. Record the lattice drift after it."])])


def split_blocks(ctx):
    """The injection cut at its label lines: each block's text as the model receives it."""
    parts, cur = [], []
    for line in ctx.split("\n"):
        if line.startswith("[system1 · ") and cur:
            parts.append("\n".join(cur))
            cur = []
        cur.append(line)
    return parts + ["\n".join(cur)] if cur else parts


def test_a_library_skill_is_reached_by_name_with_its_description(tmp_path):
    """A skill outside the table's project_skills (council, a library skill) is injected when the prompt names it: its
    label, one line `description: …` (the skill's frontmatter description), its lines verbatim, its pointer. Its
    description's words without its name bring none of it: a library skill counts only when named. Red on the PIN:
    council is outside the PIN's prompt_corpus, so no council block comes."""
    assert "council" not in PROJECT and (ROOT / ".claude" / "skills" / "council" / "SKILL.md").is_file()
    ctx = context(run(PROMPT, prompt(LIBRARY_ASK), tmp_path / "a"))
    got = [b for b in blocks(ctx) if b[3] == "council"]
    assert got, "no council block"
    lines = ctx.split("\n")
    assert description_line_ok("council", lines[lines.index(got[0][0]) + 1])     # right after the label
    rec = telemetry(tmp_path / "a")[-1]
    assert [e["project"] for e in rec["injected"] if e["skill"] == "council"] == [False] * len(got)
    ctl = context(run(PROMPT, prompt("multi-persona deliberation with historical thinkers"), tmp_path / "b"))
    assert "skill council," not in ctl                                            # the control: not named, not sent


def test_the_corpus_follows_the_tree_with_no_table_edit(tmp_path):
    """A skill added to a copied tree is ranked with no table edit, and a removed one is gone at the next prompt. Red on
    the PIN: the PIN ranks only the table's prompt_corpus."""
    root = copy_repo(tmp_path / "repo")
    fixture_skill(root, *GLIMMER)
    assert "zqx-glimmer" not in (root / ".claude" / "hooks" / "system1-situations.json").read_text(encoding="utf-8")
    ask = "tune the zqx glimmer lattice before the next glimmer run"
    ctx = context(run(PROMPT, prompt(ask), tmp_path / "st", root=root))
    got = [b for b in blocks(ctx, root=root) if b[3] == "zqx-glimmer"]
    assert got, "the added skill was not reached"
    lines = ctx.split("\n")
    assert description_line_ok("zqx-glimmer", lines[lines.index(got[0][0]) + 1], root)
    n_skills = len(list((root / ".claude" / "skills").glob("*/SKILL.md")))
    assert telemetry(tmp_path / "st")[-1]["corpus"] == n_skills
    shutil.rmtree(root / ".claude" / "skills" / "zqx-glimmer")
    ctx = context(run(PROMPT, prompt(ask, sid="s1test-session-0003"), tmp_path / "st", root=root))
    rec = telemetry(tmp_path / "st")[-1]
    assert "zqx-glimmer" not in ctx and "error" not in rec and rec["corpus"] == n_skills - 1


def test_a_weak_match_injects_nothing(tmp_path, monkeypatch):
    """Noise is worse than absence: a prompt whose one lead is an incidental word, and a pasted service log, inject
    nothing, and nothing passes (matched is empty). Opened in process, the same gates let sections through: the gates
    are what hold them. Red on the PIN: it injects bug-echo § Metadata keys for the first prompt (and env-tool-quirks
    § Test gates and pasted counts for the log)."""
    for ask in ("why keep the metadata keys at all", ENV_LOG):
        assert context(run(PROMPT, prompt(ask), tmp_path)) == ""
        assert telemetry(tmp_path)[-1]["matched"] == [], ask[:20]
    s1 = _module(HOOK, "s1_weak")
    for name in ("MIN_PROMPT_SCORE", "ONE_LEAD_MIN_SCORE", "SHORT_MIN_SCORE", "NAMED_MIN_SCORE"):
        monkeypatch.setattr(s1, name, 0.0)
    table, cache = s1.load_table(), str(tmp_path / "cache.json")
    for ask in ("why keep the metadata keys at all", ENV_LOG):
        assert s1.plan_prompt({"prompt": ask}, table, set(), cache)[1]["matched"], ask[:20]   # de-vacuous


def test_the_budget_and_the_marker_with_the_whole_corpus(tmp_path):
    """Two excerpts of a library skill: each within its share (2,048 bytes), both within 4,096, each with its pointer;
    the description line once, in the first block; the same prompt again in the window repeats no line, the description
    included, and the marker holds the key of every line sent. Red on the PIN: it sends no rwkv block."""
    first = context(run(PROMPT, prompt(RWKV_ASK), tmp_path))
    rec = telemetry(tmp_path)[-1]
    got = blocks(first)
    assert [b[3] for b in got] == ["rwkv", "rwkv"]
    assert 0 < rec["bytes"] == len(first.encode("utf-8")) <= 4096 and all(e["bytes"] <= 2048 for e in rec["injected"])
    lines = first.split("\n")
    desc = [x for x in lines if x.startswith("description: ")]
    assert len(desc) == 1 and lines.index(desc[0]) == 1 and description_line_ok("rwkv", desc[0])
    sent = {x for b in got for x in b[1] if x != "…"} | set(desc)
    again = context(run(PROMPT, prompt(RWKV_ASK), tmp_path))
    assert not set(again.split("\n")) & sent                                  # nothing again, the description neither
    keys = set(json.loads((tmp_path / "system1-seen" / f"{SID}.main.json").read_text())["keys"])
    assert {line_key("rwkv", x) for x in sent} <= keys


def test_the_cache_rebuilds_on_a_changed_skill_file_only(tmp_path):
    """The prompt index is read as it is while no SKILL.md changes (the cache file is not rewritten), and rebuilt when
    one does: a section added to a library skill is found by the next prompt. Red on the PIN: its corpus never holds a
    library skill, so the new section never comes."""
    root = copy_repo(tmp_path / "repo")
    skill = fixture_skill(root, *GLIMMER)
    st = tmp_path / "st"
    cache = st / "system1-cache.json"
    context(run(PROMPT, prompt("tune the zqx glimmer lattice"), st, root=root))
    before = cache.stat()
    context(run(PROMPT, prompt("tune the zqx glimmer lattice", sid="s1test-session-0004"), st, root=root))
    after = cache.stat()
    assert (after.st_ino, after.st_mtime_ns) == (before.st_ino, before.st_mtime_ns)      # read, not rebuilt
    added = "\n## Quartz drift ledger\n\nLog every zqx glimmer quartz drift in the ledger.\n"
    skill.write_text(skill.read_text(encoding="utf-8") + added, encoding="utf-8")
    ctx = context(run(PROMPT, prompt("the zqx glimmer quartz drift ledger", sid="s1test-session-0005"), st, root=root))
    assert "§ Quartz drift ledger" in ctx
    assert cache.stat().st_ino != before.st_ino                                  # rewritten (a new file renamed in)
    s = skill.stat()
    assert json.loads(cache.read_text())["files"]["zqx-glimmer"] == [s.st_mtime_ns, s.st_size]


def test_the_description_parser_reads_every_skill_as_pyyaml_does():
    """The hook reads a frontmatter description with the stdlib; PyYAML's reading, whitespace folded, is the oracle, on
    every SKILL.md in the tree and on each YAML shape. Red on the PIN: it has no description()."""
    s1 = _module(HOOK, "s1_desc")
    files = sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md"))
    assert len(files) > 300
    differ = [p.parent.name for p in files
              if s1.description(p.read_text(encoding="utf-8")) != description_of(p.parent.name)]
    assert differ == []
    shapes = ["description: plain words on one line # a comment",
              'description: "double \\"quoted\\" text\\u2014escaped"',
              "description: 'single ''quoted'' text'",
              "description: >\n  a folded block\n  over two lines",
              "description: |\n  a literal block\n  kept",
              "name: no-description"]
    for front in shapes:
        want = " ".join(str(yaml.safe_load(front).get("description") or "").split())
        assert s1.description(f"---\n{front}\n---\nbody\n") == want, front
    assert s1.description("# no frontmatter\n") == ""


def test_the_prompt_entries_carry_their_join_keys(tmp_path):
    """Each prompt excerpt's telemetry entry names its skill, heading and score, whether the skill is a project skill,
    and the sha256 of the excerpt's text as the model receives it, so the agent's scores of an injection (task #295)
    join its entry exactly; the record counts the skills indexed. Red on the PIN: none of these fields."""
    n_skills = len(list((ROOT / ".claude" / "skills").glob("*/SKILL.md")))
    asks = ((RWKV_ASK, False), ("claude 5 prompting and delegation: how to write the brief", True))
    for k, (ask, own) in enumerate(asks):
        ctx = context(run(PROMPT, prompt(ask, sid=f"s1test-join-{k}"), tmp_path))
        rec = telemetry(tmp_path)[-1]
        parts = split_blocks(ctx)
        assert len(parts) == len(rec["injected"]) >= 1 and rec["corpus"] == n_skills
        for text, e in zip(parts, rec["injected"]):
            assert e["sha"] == hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            assert text.split("\n")[-1] == f"full details: .claude/skills/{e['skill']}/SKILL.md § {e['heading']}"
            assert e["key"] == f"{e['skill']} § {e['heading']}" and isinstance(e["score"], float) and e["score"] > 0
            assert e["project"] is own is (e["skill"] in PROJECT)


def test_the_tool_record_carries_its_join_keys(tmp_path):
    """S1-RATE (task #295): the REAL hook through the REAL wrapper on a fixture tool call. What the model receives is
    stamped; the tool path's system1.jsonl record carries the payload's tool_use_id (null when it has none), and each
    injected entry the sha256 (16 hex) of its block's text as the model receives it between the stamp lines, cut at the
    label lines; the wrapper's injections.jsonl line names the same tool_use_id and the sha256 of the whole stamped
    text. Nothing else in the record changes. Red on the PIN: no stamp, no tool_use_id, no sha."""
    r = run(PRE, tool(*bash("git commit -m 'x'")), tmp_path)
    raw = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    parts = split_blocks(context(r))
    rec = telemetry(tmp_path)[-1]
    assert set(rec) == {"event", "tool", "tool_use_id", "matched", "injected", "skipped", "bytes", "window", "t", "ms"}
    assert rec["tool_use_id"] == "toolu_s1test" and [e["row"] for e in rec["injected"]] == ["commit", "commit-increment"]
    assert len(parts) == len(rec["injected"])
    for text, e in zip(parts, rec["injected"]):
        assert e["sha"] == hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        assert {"row", "key", "lines", "bytes", "sha"} <= set(e) <= {"row", "key", "lines", "bytes", "sha", "cut"}
    (inj,) = [json.loads(x) for x in (tmp_path / "injections.jsonl").read_text(encoding="utf-8").splitlines()]
    assert (inj["id"], inj["source"], inj["event"], inj["tool"], inj["tool_use_id"], inj["session"]) == (
        STAMP.fullmatch(raw.split("\n", 1)[0]).group(1), "system1-context", "PreToolUse", "Bash", "toolu_s1test", SID)
    assert inj["sha256"] == hashlib.sha256(raw.encode("utf-8")).hexdigest()
    bare = tool(*bash("git push origin HEAD:claude/x"))
    del bare["tool_use_id"]
    context(run(PRE, bare, tmp_path))
    assert telemetry(tmp_path)[-1]["tool_use_id"] is None


def test_the_prompt_path_stays_fast_with_a_warm_cache(tmp_path):
    """CONTRACT 4's guard: with a warm index, a prompt cut at 4,000 characters plans well under a second in process
    (measured p95 36 ms over the owner's 219 prompts; the bound is 300 ms, best of three). Passes on the PIN too: a
    guard, not a control."""
    s1 = _module(HOOK, "s1_fast")
    table, cache, ask = s1.load_table(), str(tmp_path / "cache.json"), (ENV_LOG + RWKV_ASK + " ") * 3
    s1.plan_prompt({"prompt": ask}, table, set(), cache)                         # builds the index
    ts = []
    for _ in range(3):
        t0 = time.perf_counter()
        s1.plan_prompt({"prompt": ask}, table, set(), cache)
        ts.append(time.perf_counter() - t0)
    assert min(ts) < 0.3, ts


def test_a_fifo_in_the_tree_never_blocks_the_prompt_path(tmp_path):
    """F17 for the whole-tree scan: a FIFO in place of a skill's SKILL.md is left out at once, the prompt answered and
    nothing logged as an error. Passes on the PIN too, which never reads that directory."""
    root = copy_repo(tmp_path / "repo")
    fifo = fixture_skill(root, *GLIMMER)
    fifo.unlink()
    os.mkfifo(fifo)
    try:
        t0 = time.monotonic()
        r = run(PROMPT, prompt("tune the zqx glimmer lattice"), tmp_path / "st", root=root, timeout=20)
        assert time.monotonic() - t0 < 10 and "zqx-glimmer" not in context(r)
        assert "error" not in telemetry(tmp_path / "st")[-1]
    finally:
        _unblock(fifo)


def test_a_name_is_its_words_in_order(tmp_path):
    """A skill is named when its name's words stand in the prompt as a phrase, in order; the same words apart name
    nothing, so a library skill whose words are only scattered through a prompt stays out. Red on the PIN: the control
    (the name in order) reaches nothing, the skill being outside its prompt_corpus."""
    root = copy_repo(tmp_path / "repo")
    fixture_skill(root, *GLIMMER)
    assert "skill zqx-glimmer," in context(run(PROMPT, prompt("tune the zqx glimmer lattice"), tmp_path / "a", root=root))
    ctx = context(run(PROMPT, prompt("the glimmer of the zqx lattice, tuned"), tmp_path / "b", root=root))
    assert "zqx-glimmer" not in ctx and telemetry(tmp_path / "b")[-1]["matched"] == []


def test_a_title_with_nothing_under_it_is_never_ranked(tmp_path):
    """A heading with no line under it (a skill's bare title) has nothing to inject, so it is never ranked: it cannot
    win and leave the prompt with nothing, as vllm's title did in the replay before this rule. Red on the PIN: the
    skill is outside its prompt_corpus."""
    root = copy_repo(tmp_path / "repo")
    d = root / ".claude" / "skills" / "zqx-bare"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: zqx-bare\ndescription: The zqx bare procedure for bare runs.\n---\n\n"
                                "# zqx bare\n\n## Bare procedure steps\n\n1. Run the zqx bare procedure step by step.\n",
                                encoding="utf-8")
    ctx = context(run(PROMPT, prompt("the zqx bare procedure"), tmp_path / "st", root=root))
    assert "§ Bare procedure steps" in ctx
    assert not [m for m in telemetry(tmp_path / "st")[-1]["matched"] if m.startswith("zqx-bare § zqx bare (")]
