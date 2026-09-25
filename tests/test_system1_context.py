"""`.claude/hooks/system1-context.py` through its REAL registered command lines (S1-L1, D-090; design L1 and L3).

Each behaviour test feeds a fixture hook payload to the command string exactly as `.claude/settings.json` holds it
(`sh -c <command>` with CLAUDE_PROJECT_DIR set), or as `scripts/install_session_hooks.py` writes it, and asserts what
reaches the model: the `additionalContext` of hook_context.py's one JSON line. The oracle for "the governing lines,
verbatim" is the skill file itself, read here independently of the hook: every line between a block's label and its
pointer must be a whole line of that skill file (or the `…` gap mark), and the pointer's heading must be a heading of it.

State never touches the real .jev/: AF_SYSTEM1_STATE points each test at its own tmp dir.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / ".claude" / "hooks"
HOOK = HOOKS / "system1-context.py"
TABLE = json.loads((HOOKS / "system1-situations.json").read_text(encoding="utf-8"))
SETTINGS = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
ROWS = {row["id"]: row for row in TABLE["rows"]}
SID = "s1test-session-0001"


def registered(event, matcher=None):
    """The settings file's one command that runs system1-context.py for this event."""
    cmds = [h["command"] for g in SETTINGS["hooks"][event] for h in g["hooks"]
            if "system1-context.py" in h["command"] and (matcher is None or g.get("matcher") == matcher)]
    assert len(cmds) == 1, (event, cmds)
    return cmds[0]


PRE = registered("PreToolUse", "Write|Edit|Bash")
PROMPT = registered("UserPromptSubmit")
START = SETTINGS["hooks"]["SessionStart"][0]["hooks"][0]["command"]


def run(cmd, payload, state, timeout=60):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT), AF_SYSTEM1_STATE=str(state), CLAUDE_CODE_REMOTE="false")
    data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    return subprocess.run(["sh", "-c", cmd], input=data, capture_output=True, timeout=timeout, env=env, cwd="/")


def context(r):
    """What reaches the model: the additionalContext of the one JSON line, or '' when the hook printed nothing."""
    assert r.returncode == 0, (r.returncode, r.stderr)
    out = r.stdout.decode("utf-8")
    if not out.strip():
        return ""
    obj = json.loads(out)
    assert set(obj) == {"hookSpecificOutput"} and set(obj["hookSpecificOutput"]) == {"hookEventName", "additionalContext"}
    return obj["hookSpecificOutput"]["additionalContext"]


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


def skill_lines(skill):
    return (ROOT / ".claude" / "skills" / skill / "SKILL.md").read_text(encoding="utf-8").split("\n")


def blocks(ctx):
    """Split an injection into (label, body, pointer) blocks and check each against its skill file (the oracle)."""
    out, cur = [], None
    for line in ctx.split("\n"):
        if line.startswith("[system1 · "):
            assert cur is None, "a label inside an open block"
            cur = [line, []]
        elif line.startswith("full details: .claude/skills/"):
            assert cur is not None, "a pointer with no label"
            skill, heading = line[len("full details: .claude/skills/"):].split("/SKILL.md § ", 1)
            lines = skill_lines(skill)
            assert any(x.lstrip("#").strip() == heading for x in lines if x.startswith("#")), heading
            assert cur[1] and cur[1][0] != "…", "a block with no skill line"
            for body in cur[1]:
                assert body == "…" or body in lines, f"not a verbatim line of {skill}: {body[:80]!r}"
            out.append((cur[0], cur[1], line, skill))
            cur = None
        else:
            assert cur is not None, f"text outside a block: {line[:80]!r}"
            cur[1].append(line)
    assert cur is None, "a block with no pointer"
    return out


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
def test_a_row_injects_its_lines_on_a_match(rid, tmp_path):
    """A matching input puts the row's first line, verbatim, and its pointer in front of the model within three calls
    of one window (a row that loses the byte budget to an earlier row is delivered on the next matching call)."""
    row = ROWS[rid]
    name, ti = FIXTURES[rid][0]
    delivered = None
    for n in range(3):
        ctx = context(run(PRE, tool(name, ti), tmp_path))
        blocks(ctx)
        rec = telemetry(tmp_path)[-1]
        assert rid in rec["matched"], (n, rec)
        if any(i["row"] == rid for i in rec["injected"]):
            delivered = ctx
            break
    assert delivered is not None, telemetry(tmp_path)
    labels = [b for b in blocks(delivered) if b[0].startswith(f"[system1 · {rid}]")]
    assert len(labels) == 1 and labels[0][2] == pointer(row)
    if n == 0:                                      # a fresh window starts at the row's first line
        assert labels[0][1][0] == first_line(row)


@pytest.mark.parametrize("rid", sorted(ROWS))
def test_a_row_stays_silent_on_a_near_miss(rid, tmp_path):
    name, ti = FIXTURES[rid][1]
    ctx = context(run(PRE, tool(name, ti), tmp_path))
    assert f"[system1 · {rid}]" not in ctx
    assert rid not in telemetry(tmp_path)[-1]["matched"]


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


# ---- the two budgets

def test_the_tool_budget_cuts_at_a_line_boundary_and_keeps_the_pointer(tmp_path):
    payload = tool(*bash("bash scripts/pc_suite.sh launch -n 8 -- tests/test_vendored_manifest.py"))
    seen_lines, cut_rows = [], set()
    for _ in range(3):
        ctx = context(run(PRE, payload, tmp_path))
        assert 0 < len(ctx.encode("utf-8")) <= 2048
        rec = telemetry(tmp_path)[-1]
        assert rec["bytes"] == len(ctx.encode("utf-8"))
        cut_rows |= {i["row"] for i in rec["injected"] if i.get("cut")}
        for label, body, ptr, skill in blocks(ctx):                           # every block keeps its pointer
            seen_lines += [x for x in body if x != "…"]
    assert "ops-script" in cut_rows                                           # the cap acted on this input
    assert "test-gate" in {s["row"] for s in telemetry(tmp_path)[0]["skipped"] if s["why"] == "budget"}
    assert len(seen_lines) == len(set(seen_lines))                            # a cut row resumes, it never repeats
    row = ROWS["ops-script"]
    lines, s, e = section(row)
    first = s + 1 + lines[s + 1:e].index(first_line(row))
    last = next(i for i in range(first, e) if row["lines"][0][1] in lines[i])
    assert [x for x in seen_lines if x in lines[first:last + 1]] == lines[first:last + 1]   # all of it, in order


def _score(matched):
    return float(matched.rsplit("(", 1)[1].rstrip(")"))


def test_the_prompt_budget(tmp_path):
    # one long section: its excerpt is cut at the share (half the prompt budget), the pointer kept
    ctx = context(run(PROMPT, prompt("we just resumed after compaction, what is live now"), tmp_path / "a"))
    rec = telemetry(tmp_path / "a")[-1]
    assert rec["event"] == "UserPromptSubmit" and 0 < rec["bytes"] == len(ctx.encode("utf-8")) <= 2048
    assert len(blocks(ctx)) == 1 and rec["injected"][0]["cut"] > 0
    # two sections that score alike: two excerpts, each within its share, both within 4,096
    ctx = context(run(PROMPT, prompt("bug echo after the fix, find similar bugs"), tmp_path / "b"))
    rec = telemetry(tmp_path / "b")[-1]
    assert len(blocks(ctx)) == 2 and 0 < rec["bytes"] == len(ctx.encode("utf-8")) <= 4096
    assert all(i["bytes"] <= 2048 for i in rec["injected"])
    # a second section above MIN_PROMPT_SCORE but under SECOND_EXCERPT_RATIO of the best: one excerpt only
    ctx = context(run(PROMPT, prompt("why did the sqlite query over the bridge fail"), tmp_path / "c"))
    rec = telemetry(tmp_path / "c")[-1]
    s1 = _module(HOOK, "s1_ratio")
    best, second = _score(rec["matched"][0]), _score(rec["matched"][1])
    assert s1.MIN_PROMPT_SCORE <= second < s1.SECOND_EXCERPT_RATIO * best       # de-vacuous: the case is the boundary
    assert len(blocks(ctx)) == 1 and "§ Bridge calls" in ctx


def test_the_prompt_path_filters_and_never_repeats(tmp_path):
    ask = prompt("we just resumed after compaction, what is live now")
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


def test_an_exception_injects_nothing_and_logs_its_type(tmp_path):
    payload = tool(*bash("git commit -m 'x'"))
    marker = tmp_path / "system1-seen" / f"{SID}.main.json"
    marker.mkdir(parents=True)                                                # the marker cannot be read
    r = run(PRE, payload, tmp_path)
    assert (r.returncode, r.stdout) == (0, b"")
    rec = telemetry(tmp_path)[-1]
    assert (rec["event"], rec["tool"], rec["error"]) == ("PreToolUse", "Bash", "OSError") and "injected" not in rec
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


# ---- the table against the skills, and a drift guard

def _module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_row_resolves_and_its_first_line_fits_a_call_alone():
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
        need = len(label.encode()) + len(lines[idx[0]].encode()) + len(pointer(row).encode()) + 3
        assert need <= s1.TOOL_BUDGET, (row["id"], need)
        assert lines[idx[0]] == first_line(row) and row["source"]
    for skill in TABLE["prompt_corpus"]:
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
