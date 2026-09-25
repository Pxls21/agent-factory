"""VERIFY-S1-L1 harness: the REAL registered command strings, run on a scratch copy of the repo (hook, table, skills,
wrapper, installer). State = the copy's own .jev/ (the production default path; AF_SYSTEM1_STATE is never set).
The oracle is independent of the hook: its own heading parser and section ranges."""
import json
import os
import re
import subprocess
import time
from pathlib import Path

S = Path(__file__).resolve().parent
R = S / "repo"
SETTINGS = json.loads((R / ".claude" / "settings.json").read_text(encoding="utf-8"))
TABLE = json.loads((R / ".claude" / "hooks" / "system1-situations.json").read_text(encoding="utf-8"))
ROWS = {r["id"]: r for r in TABLE["rows"]}


def registered(event, matcher=None):
    cmds = [h["command"] for g in SETTINGS["hooks"][event] for h in g["hooks"]
            if "system1-context.py" in h["command"] and (matcher is None or g.get("matcher") == matcher)]
    assert len(cmds) == 1, (event, cmds)
    return cmds[0]


PRE = registered("PreToolUse", "Write|Edit|Bash")
PROMPT = registered("UserPromptSubmit")
START = SETTINGS["hooks"]["SessionStart"][0]["hooks"][0]["command"]


def env_for(repo=R, **extra):
    env = {k: v for k, v in os.environ.items() if k not in ("AF_SYSTEM1_STATE",)}
    env.update(CLAUDE_PROJECT_DIR=str(repo), CLAUDE_CODE_REMOTE="false")
    env.update(extra)
    return env


def run(cmd, payload, repo=R, timeout=90, **extra):
    data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    t0 = time.monotonic()
    r = subprocess.run(["sh", "-c", cmd], input=data, capture_output=True, timeout=timeout, env=env_for(repo, **extra),
                       cwd=str(repo))
    r.wall = time.monotonic() - t0
    return r


def ctx(r):
    assert r.returncode == 0, (r.returncode, r.stderr[-300:])
    out = r.stdout.decode("utf-8")
    if not out.strip():
        return ""
    lines = [x for x in out.split("\n") if x.strip()]
    assert len(lines) == 1, len(lines)
    obj = json.loads(lines[0])
    assert set(obj) == {"hookSpecificOutput"}, obj.keys()
    return obj["hookSpecificOutput"]["additionalContext"]


def state(repo=R):
    return repo / ".jev"


def telemetry(repo=R):
    p = state(repo) / "system1.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def wipe_state(repo=R):
    import shutil
    shutil.rmtree(state(repo), ignore_errors=True)


def tool(name, ti, sid="vs1-session", agent=None, cwd=None, repo=R):
    p = {"session_id": sid, "transcript_path": "/dev/null", "cwd": str(cwd or repo), "hook_event_name": "PreToolUse",
         "tool_name": name, "tool_input": ti, "tool_use_id": "toolu_vs1"}
    if agent:
        p["agent_id"] = agent
    return p


def bash(cmd, **kw):
    return tool("Bash", {"command": cmd, "description": "d"}, **kw)


def write(path, content="x\n", repo=R, **kw):
    return tool("Write", {"file_path": path if path.startswith("/") else f"{repo}/{path}", "content": content}, **kw)


def edit(path, new="y", old="x", repo=R, **kw):
    return tool("Edit", {"file_path": path if path.startswith("/") else f"{repo}/{path}", "old_string": old,
                         "new_string": new}, **kw)


def prompt(text, sid="vs1-session", agent=None, repo=R):
    p = {"session_id": sid, "transcript_path": "/dev/null", "cwd": str(repo), "hook_event_name": "UserPromptSubmit",
         "prompt": text}
    if agent:
        p["agent_id"] = agent
    return p


def start(source, sid="vs1-session", agent=None, repo=R):
    p = {"session_id": sid, "transcript_path": "/dev/null", "cwd": str(repo), "hook_event_name": "SessionStart",
         "source": source}
    if agent:
        p["agent_id"] = agent
    return p


# ---------------------------------------------------------------- the independent oracle

def skill_text(skill, repo=R):
    return (repo / ".claude" / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")


def sections_of(skill, repo=R):
    """{heading: [(start, end)]} with my own parser: ATX headings outside ``` fences (a fence toggles on any line whose
    stripped form starts with ```)."""
    lines = skill_text(skill, repo).split("\n")
    heads, fence = [], False
    for i, x in enumerate(lines):
        if x.lstrip().startswith("```"):
            fence = not fence
            continue
        if not fence:
            m = re.match(r"^(#{1,6})\s+(.+?)\s*$", x)
            if m:
                heads.append((m.group(2), i))
    out = {}
    for k, (h, s) in enumerate(heads):
        e = heads[k + 1][1] if k + 1 < len(heads) else len(lines)
        out.setdefault(h, []).append((s, e))
    return lines, out


LABEL_RX = re.compile(r"^\[system1 · ([a-z0-9-]+)\] skill ([a-z0-9-]+), (the governing lines verbatim|the section that "
                      r"matches this prompt, verbatim):$")
PTR_RX = re.compile(r"^full details: \.claude/skills/([a-z0-9-]+)/SKILL\.md § (.+)$")


def check(c, repo=R):
    """Split an injection into blocks and check each against its skill file. Returns [(row id, skill, heading,
    [line indexes])]; raises AssertionError with a reason on any violation."""
    blocks, cur = [], None
    for ln in c.split("\n"):
        m = LABEL_RX.match(ln)
        if m and cur is None:
            cur = [m.group(1), m.group(2), []]
            continue
        p = PTR_RX.match(ln)
        if p and cur is not None:
            skill, heading = p.group(1), p.group(2)
            assert skill == cur[1], ("pointer names another skill", cur[1], skill)
            lines, secs = sections_of(skill, repo)
            spans = secs.get(heading, [])
            assert len(spans) == 1, ("heading found", len(spans), heading)
            s, e = spans[0]
            body = cur[2]
            assert body and body[0] != "…" and body[-1] != "…", "empty body or a gap mark at an edge"
            idx, pos = [], s + 1
            for b in body:
                if b == "…":
                    idx.append(None)
                    continue
                cand = [i for i in range(pos, e) if lines[i] == b] or [i for i in range(s + 1, e) if lines[i] == b]
                assert cand, ("not a verbatim line of the named section", skill, heading, b[:60])
                idx.append(cand[0])
                pos = cand[0] + 1
            real = [i for i in idx if i is not None]
            for k in range(1, len(idx)):                  # a gap mark sits exactly where lines are not adjacent
                if idx[k] is None:
                    assert idx[k - 1] is not None and idx[k + 1] is not None and idx[k + 1] != idx[k - 1] + 1, "stray gap"
                elif idx[k - 1] is not None:
                    assert idx[k] == idx[k - 1] + 1, ("non-adjacent lines with no gap mark", idx[k - 1], idx[k])
            blocks.append((cur[0], skill, heading, real))
            cur = None
            continue
        assert cur is not None, ("text outside a block", ln[:60])
        cur[2].append(ln)
    assert cur is None, "a block with no pointer"
    return blocks
