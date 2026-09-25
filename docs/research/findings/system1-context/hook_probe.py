#!/usr/bin/env python3
"""hook_probe.py — S1A evidence demand 1: the size and latency of each hook that is safe to run on a sample input.

Runs each hook command as its registration runs it (the same interpreter and wrapper), with a synthetic hook payload
built from a real file of this repository, N times, and prints one markdown row per case: output bytes (stdout and
stderr), exit code, wall-clock median / min / max in ms, the load average before and after, and the output's first
marker word (never the text). The hook's own output is kept in memory only.

NOT run, and why: session-start.sh (runs scripts/setup.sh and appends to CLAUDE_ENV_FILE), turn-retro-gate.sh (writes
its sentinel into .git), stop-hook-git-check.sh (git index refresh risk; 774 real runs are in the records instead),
the fast-jev-output function hook (it runs inside the harness, not as a command), honey-subagent.js and
logcompress-hook.js (inactive: no /root/.claude/.honey-active). search-intercept.py runs with
AF_SEARCH_INTERCEPT_STATE pointed at a fresh scratch folder per run, so .jev/intercept-seen.json is never written and
the 120 s repeat window never lets a sample through.

Usage: hook_probe.py --scratch DIR [-n 5]
"""
import argparse
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time

REPO = "/home/user/agent-factory"
HOOKS = REPO + "/.claude/hooks"
WRAP = ["python3", REPO + "/scripts/hook_context.py"]
AEGIS = "/root/.claude/plugins/cache/aegis-dev/aegis/2.10.6"
HONEY = "/root/.claude/plugins/cache/greenpt/honey/1.3.1"
CBM = "/root/.local/bin/codebase-memory-mcp"
SAMPLE_PY = REPO + "/scripts/hook_context.py"
SAMPLE_LINE = "    event, cmd = argv[1], argv[3:]"  # a line inside main() of the sample file: the enclosing symbol resolves


def payload(event, tool=None, tool_input=None, **extra):
    d = {"session_id": "s1a-probe", "transcript_path": "/dev/null", "cwd": REPO, "hook_event_name": event}
    if tool:
        d["tool_name"] = tool
        d["tool_input"] = tool_input or {}
    d.update(extra)
    return json.dumps(d).encode()


CASES = [
    ("wiki-context.py, a person's prompt", "UserPromptSubmit", ["python3", HOOKS + "/wiki-context.py"],
     payload("UserPromptSubmit", prompt="why did the search intercept hook block the graft ask call in the pc lane, and "
                                        "which registry row covers the trailing ampersand quirk"), {}),
    ("wiki-context.py, a harness event", "UserPromptSubmit", ["python3", HOOKS + "/wiki-context.py"],
     payload("UserPromptSubmit", prompt="<task-notification> a background task completed"), {}),
    ("edit-snapshot.py, Read of a .py (bare)", "PostToolUse", ["python3", HOOKS + "/edit-snapshot.py"],
     payload("PostToolUse", "Read", {"file_path": SAMPLE_PY}), {}),
    ("edit-snapshot.py, Read, as registered (hook_context.py wrapper)", "PostToolUse",
     WRAP + ["PostToolUse", "--", "python3", HOOKS + "/edit-snapshot.py"],
     payload("PostToolUse", "Read", {"file_path": SAMPLE_PY}), {}),
    ("edit-snapshot.py, Edit inside a function, as registered", "PostToolUse",
     WRAP + ["PostToolUse", "--", "python3", HOOKS + "/edit-snapshot.py"],
     payload("PostToolUse", "Edit", {"file_path": SAMPLE_PY, "old_string": SAMPLE_LINE, "new_string": SAMPLE_LINE}), {}),
    ("edit-snapshot.py, Read of a non-.py file", "PostToolUse",
     WRAP + ["PostToolUse", "--", "python3", HOOKS + "/edit-snapshot.py"],
     payload("PostToolUse", "Read", {"file_path": REPO + "/CLAUDE.md"}), {}),
    ("search-intercept.py, Bash `ls -la` (fast path), as registered", "PreToolUse",
     WRAP + ["PreToolUse", "--", "python3", HOOKS + "/search-intercept.py"],
     payload("PreToolUse", "Bash", {"command": "ls -la", "description": "list"}), {"STATE": 1}),
    ("search-intercept.py, Grep of an identifier in project code, as registered", "PreToolUse",
     WRAP + ["PreToolUse", "--", "python3", HOOKS + "/search-intercept.py"],
     payload("PreToolUse", "Grep", {"pattern": "file_chronology", "path": REPO + "/scripts"}), {"STATE": 1}),
    ("search-intercept.py, Grep of an identifier under .claude/hooks (outside the code prefixes), as registered",
     "PreToolUse", WRAP + ["PreToolUse", "--", "python3", HOOKS + "/search-intercept.py"],
     payload("PreToolUse", "Grep", {"pattern": "file_chronology", "path": REPO + "/.claude/hooks"}), {"STATE": 1}),
    ("search-intercept.py, Bash quirk (two revs to rev-parse --short), as registered", "PreToolUse",
     WRAP + ["PreToolUse", "--", "python3", HOOKS + "/search-intercept.py"],
     payload("PreToolUse", "Bash", {"command": "git rev-parse --short HEAD HEAD~1", "description": "x"}), {"STATE": 1}),
    ("graft-first-nag.py, Grep of an identifier (not registered in Claude; Codex/Hermes adapters)", "PreToolUse",
     ["python3", HOOKS + "/graft-first-nag.py"],
     payload("PreToolUse", "Grep", {"pattern": "file_chronology", "path": REPO + "/scripts"}), {}),
    ("cbm-code-discovery-gate (codebase-memory hook-augment), Read of a .py", "PostToolUse",
     ["bash", "/root/.claude/hooks/cbm-code-discovery-gate"],
     payload("PostToolUse", "Read", {"file_path": SAMPLE_PY}), {}),
    ("cbm-code-discovery-gate, Grep of an identifier", "PreToolUse",
     ["bash", "/root/.claude/hooks/cbm-code-discovery-gate"],
     payload("PreToolUse", "Grep", {"pattern": "file_chronology", "path": REPO}), {}),
    ("cbm-session-reminder, SessionStart", "SessionStart", ["bash", "/root/.claude/hooks/cbm-session-reminder"],
     payload("SessionStart", source="startup"), {}),
    ("aegis run-hook.cmd session-start", "SessionStart", ["bash", AEGIS + "/hooks/run-hook.cmd", "session-start"],
     payload("SessionStart", source="startup"), {"CLAUDE_PLUGIN_ROOT": AEGIS}),
    ("honey-session.js (honey mode inactive)", "SessionStart", ["node", HONEY + "/hooks/honey-session.js"],
     payload("SessionStart", source="startup"), {"CLAUDE_PLUGIN_ROOT": HONEY}),
]

MARKS = ["READ CONTEXT", "EDIT SNAPSHOT", "[wiki live-state", "SEARCH INTERCEPT", "QUIRK GUARD", "GRAFT-FIRST",
         "hookSpecificOutput", "codebase-memory", "You have Aegis", "Honey"]


def loadavg():
    with open("/proc/loadavg") as fh:
        return fh.read().split()[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("-n", type=int, default=5)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    print("| hook case | event | runs | rc | stdout bytes (median) | stderr bytes (median) | first marker | "
          "median ms | min ms | max ms | load before / after |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for name, event, argv, data, envx in CASES:
        times, outs, errs, rcs, marks = [], [], [], set(), set()
        la0 = loadavg()
        for _ in range(a.n):
            env = dict(os.environ)
            for k, v in envx.items():
                if k != "STATE":
                    env[k] = v
            if "STATE" in envx:
                env["AF_SEARCH_INTERCEPT_STATE"] = tempfile.mkdtemp(dir=a.scratch, prefix="si-state-")
            t0 = time.perf_counter()
            p = subprocess.run(argv, input=data, capture_output=True, cwd=REPO, env=env, timeout=120)
            times.append((time.perf_counter() - t0) * 1000)
            outs.append(len(p.stdout))
            errs.append(len(p.stderr))
            rcs.add(p.returncode)
            text = (p.stdout + p.stderr).decode("utf-8", "replace")
            marks.update(m for m in MARKS if m in text)
        la1 = loadavg()
        print(f"| {name} | {event} | {a.n} | {'/'.join(str(r) for r in sorted(rcs))} | {int(statistics.median(outs))} | "
              f"{int(statistics.median(errs))} | {', '.join(sorted(marks)) or '-'} | {statistics.median(times):.0f} | "
              f"{min(times):.0f} | {max(times):.0f} | {la0} / {la1} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
