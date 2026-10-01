#!/usr/bin/env python3
"""install_session_hooks.py — register the project hooks for a session rooted ABOVE the repository.

Claude Code loads `.claude/settings.json` from the session's project root only. A session rooted in `/home/user` (the
CCR default here) never loads `agent-factory/.claude/settings.json`, so none of the five project hooks fired there
(AF-AP-172: the turn-end retro ran 0 times in 834 Stop runs). This script writes the project hooks, with absolute
paths, into `<repo parent>/.claude/settings.json`. Measured 2026-09-24 (task #214): a settings file created
mid-session takes effect on the next tool call, so running this script IS the manual start; no restart is needed.
The repo's own `.claude/settings.json` is not written here (its commands spell `$CLAUDE_PROJECT_DIR`); it holds the
same hooks except the stack catalog below.

scripts/task_sync.py (LS-B7, D-102) is registered twice, on Stop and on SessionStart, each with an explicit 30-second
timeout: it writes the harness task list from the ledger. It never blocks (never exit 2), and while
`<repo>/.jev/task-sync-off` exists both registrations exit 0 at once.

`scripts/stack.py catalog` (LS-B9 round 4, D-103) is registered on SessionStart for start, resume and compact, with a
30-second timeout: the stack catalog (a heading line, `stack.py list`, one line on ratings) under 4,000 characters,
since the harness shows only a 2,000-character preview of a hook text over 10,000 (AF-AP-183). Such a session loaded
no output style, so this line did the style's job (LS-DESIGN v2 §6, LS-B6); it stays. Since task #440 the repo's
`outputStyle` (its `.claude/settings.json`; the owner's default, Attention-kind) is also written at the session root
when the root sets none, and `--remove` takes it out only when it is still the repo's; a style the root already sets
is kept. A style takes effect when Claude Code next starts. When the catalog cannot be built it prints
ONE line naming why, and the command exits 0 always: stack.py catches its own failures, and a python3 that cannot run
at all ends in the echo.

scripts/ls_req.py (LS-B10, task #364, D-108 item 6: the chat form of the stack runner) is registered three times, each
group LAST in its list: on UserPromptSubmit (`prompt`: mints the turn's nonce, reconciles the ended turn; 30-second
timeout), on Stop (`stop`: runs the turn's request lines through scripts/stack.py and answers each with a receipt, as
blocking feedback; 300-second timeout, over its 240-second round budget) and on SessionStart for every source
(`session-start`: re-injects the nonce after a compaction, reconciles an ended query; 30-second timeout). It runs
directly, not through hook_context.py: it prints its own hookSpecificOutput JSON, and a Stop round outlasts the
wrapper's 55-second limit. While `<repo>/.jev/req-off` exists every subcommand exits 0 at once.

scripts/filepacks.py (K2, task #353, D-106) is registered twice: PreToolUse on Read, Edit, Write and Bash through the
wrapper, last in its list (the first time a context window touches a tracked file, its context pack), and SessionStart
with no matcher, before the chat form's group (`hook --reset`: a compaction forgets the compacted window, a resume or a
clear every window of its session). Neither has a timeout: the hook reads its stdin within 2 s and exits 0 on every
path.

The tool hooks run through scripts/hook_context.py: edit-snapshot prints plain text, which the wrapper turns into
additionalContext the model reads (the Codex and Hermes adapters parse that plain text); search-intercept (task #228,
PreToolUse on Grep and Bash) answers a semantic search or stops a known Bash quirk with exit 2 and its text on stderr,
which the wrapper stamps and passes on with its exit code (S1-RATE). graft-first-nag.py stays for the Codex and Hermes
adapters; search-intercept runs its classifier. system1-context (S1-L1, D-090) is registered twice through the wrapper:
PreToolUse on Write, Edit and Bash (the governing skill lines for the situation) and UserPromptSubmit (the skill sections
that match the prompt, beside wiki-context); session-start.sh resets its once-per-window marker. wiki-context runs through
the wrapper too since D-095, so its excerpt carries the S1-RATE stamp and score request like every other injection.

Merge rule, hook by hook: an install replaces every hook whose command names `<repo>/.claude/hooks/`,
`<repo>/scripts/task_sync.py`, `<repo>/scripts/stack.py catalog`, `<repo>/scripts/ls_req.py` or
`<repo>/scripts/filepacks.py` (an older spelling of ours included); --remove takes out only our exact current
commands. A foreign hook in the same group as one of ours stays, in that group with its matcher (S1-L1-R1 F19); every
other key and entry in the file is kept. An existing file that is not a JSON object is refused (exit 1), never
overwritten.

The count of hooks an install registers is counted from our_hooks() (hook_count), never written as a literal: --help
states it and the install line prints it (VERIFY-LS-B10 F10: a literal count went stale when the chat form's hooks
were added).

Usage: install_session_hooks.py [--target PATH] [--check | --remove]
  (default)  write or refresh our entries; prints `session hooks: installed N in ...` (N from hook_count) or
             `session hooks: unchanged in ...`
  --check    exit 0 when the file already holds exactly our entries, 1 otherwise; writes nothing
  --remove   delete our entries (the owner's opt-out); keeps everything else
"""
import argparse
import json
import os
import shlex
import stat
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def our_hooks(root: Path) -> dict:
    r = shlex.quote(str(root))
    wrap = f"python3 {r}/scripts/hook_context.py"

    def guarded(script: str, cmd: str, wrapped: bool = False) -> str:
        # Fail open (VERIFY-COORD-0924 F-L1-2): exit 2 is the blocking code, and a failed `cd` under dash and python's
        # can't-open error both exit 2, so a missing repo or script ends the hook with 0 before anything runs.
        need = f"[ -f {r}/{script} ]" + (f" && [ -f {r}/scripts/hook_context.py ]" if wrapped else "")
        return f"{need} || exit 0; cd {r} || exit 0; {cmd}"

    def task_sync(event: str) -> dict:
        return {"hooks": [{"type": "command", "command": guarded(
            "scripts/task_sync.py", f"python3 {r}/scripts/task_sync.py --hook {event}"), "timeout": 30}]}

    def req(event: str, timeout: int) -> dict:       # LS-B10: the chat form, last in each list
        return {"hooks": [{"type": "command", "command": guarded(
            "scripts/ls_req.py", f"python3 {r}/scripts/ls_req.py {event}"), "timeout": timeout}]}

    catalog = {"matcher": "startup|resume|compact", "hooks": [{"type": "command", "command": guarded(
        "scripts/stack.py",
        f'python3 {r}/scripts/stack.py catalog || echo "stacks: no catalog (scripts/stack.py catalog exited $?)"'),
        "timeout": 30}]}
    filepacks = {"matcher": "Read|Edit|Write|Bash", "hooks": [{"type": "command", "command": guarded(
        "scripts/filepacks.py", f"{wrap} PreToolUse -- python3 {r}/scripts/filepacks.py hook", True)}]}
    filepacks_reset = {"hooks": [{"type": "command", "command": guarded(
        "scripts/filepacks.py", f"python3 {r}/scripts/filepacks.py hook --reset")}]}

    return {
        "SessionStart": [{"hooks": [{"type": "command", "command": guarded(
            ".claude/hooks/session-start.sh", f"CLAUDE_PROJECT_DIR={r} bash {r}/.claude/hooks/session-start.sh")}]},
            task_sync("session-start"), catalog, filepacks_reset, req("session-start", 30)],
        "UserPromptSubmit": [{"hooks": [{"type": "command", "command": guarded(
            ".claude/hooks/wiki-context.py", f"{wrap} UserPromptSubmit -- python3 {r}/.claude/hooks/wiki-context.py",
            True)}]},
            {"hooks": [{"type": "command", "command": guarded(
                ".claude/hooks/system1-context.py",
                f"{wrap} UserPromptSubmit -- python3 {r}/.claude/hooks/system1-context.py", True)}]},
            req("prompt", 30)],
        "PostToolUse": [{"matcher": "Edit|Write|Read", "hooks": [{"type": "command", "command": guarded(
            ".claude/hooks/edit-snapshot.py", f"{wrap} PostToolUse -- python3 {r}/.claude/hooks/edit-snapshot.py", True)}]}],
        "PreToolUse": [{"matcher": "Grep|Bash", "hooks": [{"type": "command", "command": guarded(
            ".claude/hooks/search-intercept.py", f"{wrap} PreToolUse -- python3 {r}/.claude/hooks/search-intercept.py",
            True)}]},
            {"matcher": "Write|Edit|Bash", "hooks": [{"type": "command", "command": guarded(
                ".claude/hooks/system1-context.py", f"{wrap} PreToolUse -- python3 {r}/.claude/hooks/system1-context.py",
                True)}]},
            filepacks],
        "Stop": [{"hooks": [{"type": "command", "command": guarded(
            ".claude/hooks/turn-retro-gate.sh", f"bash {r}/.claude/hooks/turn-retro-gate.sh")}]},
            task_sync("stop"), req("stop", 300)],
    }


def hook_count(hooks: dict) -> int:
    """How many hooks an our_hooks() mapping registers: every command in every group of every event."""
    return sum(len(g["hooks"]) for groups in hooks.values() for g in groups)


def _without(entry: object, ours) -> object:
    """The group without our hooks: None when it held only ours, the group itself when it held none, else a copy that
    keeps the foreign hooks under the group's matcher."""
    hooks = entry.get("hooks") if isinstance(entry, dict) else None
    if not isinstance(hooks, list):
        return entry
    kept = [h for h in hooks if not (isinstance(h, dict) and ours(str(h.get("command", ""))))]
    if len(kept) == len(hooks):
        return entry
    return dict(entry, hooks=kept) if kept else None


def repo_style(root: Path):
    """The repo's own output style (`outputStyle` in its `.claude/settings.json`), or None."""
    try:
        style = json.loads((root / ".claude" / "settings.json").read_text(encoding="utf-8")).get("outputStyle")
    except (OSError, ValueError, AttributeError):
        return None
    return style if isinstance(style, str) and style else None


def merged(current: dict, root: Path, remove: bool) -> dict:
    marker = f"{shlex.quote(str(root))}/.claude/hooks/"  # as the commands spell it (VERIFY-COORD-0924 F-L1-1)
    sync_marker = f"{shlex.quote(str(root))}/scripts/task_sync.py"
    catalog_marker = f"{shlex.quote(str(root))}/scripts/stack.py catalog"
    req_marker = f"{shlex.quote(str(root))}/scripts/ls_req.py"
    filepacks_marker = f"{shlex.quote(str(root))}/scripts/filepacks.py"
    mine = our_hooks(root)
    exact = {h["command"] for groups in mine.values() for g in groups for h in g["hooks"]}
    ours = exact.__contains__ if remove else (
        lambda c: c in exact or marker in c or sync_marker in c or catalog_marker in c or req_marker in c
        or filepacks_marker in c)
    out = dict(current)
    hooks = dict(out.get("hooks") or {})
    for event in sorted(set(hooks) | set(mine)):
        kept = [e for e in (_without(e, ours) for e in (hooks.get(event) or [])) if e is not None]
        if not remove:
            kept += mine.get(event, [])
        if kept:
            hooks[event] = kept
        else:
            hooks.pop(event, None)
    if hooks:
        out["hooks"] = hooks
    else:
        out.pop("hooks", None)
    style = repo_style(root)   # task #440: a style the root already sets is the owner's choice and stays
    if style is not None and remove and out.get("outputStyle") == style:
        out.pop("outputStyle")
    elif style is not None and not remove:
        out.setdefault("outputStyle", style)
    return out


def main(argv: list[str]) -> int:
    n = hook_count(our_hooks(ROOT))
    ap = argparse.ArgumentParser(description=f"{__doc__.splitlines()[0]} It registers {n} hooks.")
    ap.add_argument("--target", type=Path, default=ROOT.parent / ".claude" / "settings.json")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--remove", action="store_true")
    args = ap.parse_args(argv)
    target = args.target
    current: dict = {}
    if target.exists():
        try:
            current = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"session hooks: REFUSED — {target} is not readable JSON ({exc}); nothing written", file=sys.stderr)
            return 1
        if not isinstance(current, dict):
            print(f"session hooks: REFUSED — {target} holds a {type(current).__name__}, not an object", file=sys.stderr)
            return 1
    want = merged(current, ROOT, args.remove)
    if args.check:
        ok = want == current and not args.remove
        print(f"session hooks: {'present' if ok else 'MISSING or stale'} in {target}")
        return 0 if ok else 1
    if want == current:
        print(f"session hooks: unchanged in {target}")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".settings.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(want, fh, indent=2)
        fh.write("\n")
    if target.exists():  # keep the file's mode and owner (VERIFY-COORD-0924 F-L1-5: 0600 uid 1000 became 0644 root)
        st = target.stat()
        os.chmod(tmp, stat.S_IMODE(st.st_mode))
        try:
            os.chown(tmp, st.st_uid, st.st_gid)
        except PermissionError:
            pass
    else:
        os.chmod(tmp, 0o644)
    os.replace(tmp, target)
    verb = "removed ours from" if args.remove else f"installed {n} in"
    print(f"session hooks: {verb} {target} (live from the next tool call)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
