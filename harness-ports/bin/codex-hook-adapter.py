#!/usr/bin/env python3
"""Codex -> project-hook payload adapter.

The project's hooks (.claude/hooks/*) were written against Claude Code's hook
payloads. Codex's wire protocol is the same SHAPE (JSON on stdin with snake_case
`tool_name` / `tool_input`; plain stdout becomes additionalContext; exit 2 +
stderr blocks) but the TOOL PAYLOADS differ, so a hook wired straight through
would silently see nothing and print nothing — a hook that fires and does
nothing is a hollow green. This adapter translates, then delegates.

Verified against openai/codex @ bc39b0ed:
  - codex-rs/core/src/tools/hook_names.rs — canonical hook `tool_name` is
    `apply_patch` (matcher aliases Write/Edit), shell is `Bash`, subagent spawn
    is `spawn_agent` (alias Agent).
  - codex-rs/core/src/tools/runtimes/apply_patch_tests.rs:140 — apply_patch
    `tool_input` is `{"command": "<patch text>"}`, NOT {file_path, new_string}.
  - codex-rs/apply-patch/src/lib.rs — patch envelope is
    `*** Begin Patch` / `*** Update File:` / `*** Add File:` / `*** End Patch`.

Translations
------------
apply_patch (PostToolUse)
    One synthetic Edit payload PER FILE touched, with `new_string` = the added
    ("+") lines of that file's hunks. edit-snapshot.py then resolves the
    enclosing symbol, its blast radius, and the anti-pattern screen per file.

Bash (PreToolUse)
    Codex has no Grep tool; searches are rg/grep inside a shell command. The
    GRAFT-FIRST nag is about semantic identifier searches over project code, so
    the shell command is parsed back into a Grep-shaped payload when it is an
    rg/grep invocation. Anything else is passed through untouched (the nag then
    no-ops on its own tool_name check).

Anything else is forwarded unchanged.

Usage: codex-hook-adapter.py <hook-file-name>
Exit code and stderr come from the delegated hook, so the exit-2 block contract
survives. A translation that finds nothing to say exits 0 silently, exactly as
the underlying hook would.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

FILE_HDR = re.compile(r"^\*\*\* (?:Update|Add) File: (.+)$")
END_HDR = re.compile(r"^\*\*\* (?:End Patch|Begin Patch|Delete File: .*)$")
# rg/grep somewhere in the command (possibly after `cd x &&`), capturing the tail.
SEARCH_CMD = re.compile(r"(?:^|[;&|]\s*)(rg|grep|ripgrep)\s+(.*)$")


def repo_root() -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=5)
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except Exception as e:  # fail-LOUD: say which root we fell back to and why
        print(f"codex-hook-adapter: git rev-parse failed ({e}) — using the script-relative repo root", file=sys.stderr)
    return Path(__file__).resolve().parents[2]


def run_hook(hook: Path, payload: dict) -> tuple[str, str, int]:
    """Delegate one payload to the real hook. Returns (stdout, stderr, rc)."""
    root = repo_root()
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root))
    runner = ["python3", str(hook)] if hook.suffix == ".py" else ["bash", str(hook)]
    try:
        p = subprocess.run(runner, input=json.dumps(payload), capture_output=True,
                           text=True, cwd=str(root), env=env, timeout=60)
        return p.stdout, p.stderr, p.returncode
    except Exception as e:
        return "", f"codex-hook-adapter: delegating to {hook.name} failed: {e}\n", 0


def split_patch(patch: str) -> list[tuple[str, str]]:
    """[(file_path, added_lines_text)] for every file the patch envelope touches."""
    out: list[tuple[str, list[str]]] = []
    cur: str | None = None
    for line in patch.splitlines():
        m = FILE_HDR.match(line)
        if m:
            cur = m.group(1).strip()
            out.append((cur, []))
            continue
        if END_HDR.match(line):
            cur = None
            continue
        if cur is not None and line.startswith("+") and not line.startswith("+++"):
            out[-1][1].append(line[1:])
    return [(f, "\n".join(ls)) for f, ls in out if ls]


def parse_search(cmd: str) -> dict | None:
    """Recover a Grep-shaped tool_input from an rg/grep shell command."""
    m = SEARCH_CMD.search(cmd)
    if not m:
        return None
    try:
        import shlex
        argv = shlex.split(m.group(2))
    except ValueError:
        return None
    pattern, path, ftype, glob = "", "", "", ""
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-t", "--type"):
            ftype = argv[i + 1] if i + 1 < len(argv) else ""
            i += 2
            continue
        if a in ("-g", "--glob", "--include"):
            glob = argv[i + 1] if i + 1 < len(argv) else ""
            i += 2
            continue
        if a in ("-e", "--regexp"):
            pattern = argv[i + 1] if i + 1 < len(argv) else ""
            i += 2
            continue
        if a.startswith("-"):
            i += 1
            continue
        if not pattern:
            pattern = a
        elif not path:
            path = a
        i += 1
    if not pattern:
        return None
    return {"pattern": pattern, "path": path, "glob": glob, "type": ftype}


def main() -> int:
    if len(sys.argv) < 2:
        print("codex-hook-adapter: no hook name given", file=sys.stderr)
        return 0
    hook = repo_root() / ".claude" / "hooks" / sys.argv[1]
    if not hook.is_file():
        print(f"codex-hook-adapter: {hook} not found — hook did NOT run",
              file=sys.stderr)
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception as e:  # fail-LOUD: a malformed payload is a harness bug, not silence
        print(f"codex-hook-adapter: unreadable hook payload on stdin ({e}) — nothing delegated", file=sys.stderr)
        return 0

    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}

    if tool == "apply_patch":
        files = split_patch(ti.get("command") or "")
        if not files:
            return 0
        outs, errs, rc = [], [], 0
        for fp, added in files:
            sub = dict(payload)
            sub["tool_name"] = "Edit"
            sub["tool_input"] = {"file_path": fp, "new_string": added}
            o, e, r = run_hook(hook, sub)
            if o.strip():
                outs.append(o.rstrip())
            if e.strip():
                errs.append(e.rstrip())
            rc = r or rc
        if outs:
            print("\n".join(outs))
        if errs:
            print("\n".join(errs), file=sys.stderr)
        return rc

    if tool == "Bash":
        grep_input = parse_search(ti.get("command") or "")
        if grep_input is None:
            return 0
        sub = dict(payload)
        sub["tool_name"] = "Grep"
        sub["tool_input"] = grep_input
        o, e, r = run_hook(hook, sub)
        if o.strip():
            print(o.rstrip())
        if e.strip():
            print(e.rstrip(), file=sys.stderr)
        return r

    o, e, r = run_hook(hook, payload)
    if o.strip():
        print(o.rstrip())
    if e.strip():
        print(e.rstrip(), file=sys.stderr)
    return r


if __name__ == "__main__":
    sys.exit(main())
