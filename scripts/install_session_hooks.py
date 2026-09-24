#!/usr/bin/env python3
"""install_session_hooks.py — register the five project hooks for a session rooted ABOVE the repository.

Claude Code loads `.claude/settings.json` from the session's project root only. A session rooted in `/home/user` (the
CCR default here) never loads `agent-factory/.claude/settings.json`, so none of the five project hooks fired there
(AF-AP-172: the turn-end retro ran 0 times in 834 Stop runs). This script writes the same five hooks, with absolute
paths, into `<repo parent>/.claude/settings.json`. Measured 2026-09-24 (task #214): a settings file created
mid-session takes effect on the next tool call, so running this script IS the manual start; no restart is needed.

The two hooks that print plain text (edit-snapshot, graft-first-nag) run through scripts/hook_context.py, which turns
their output into additionalContext the model reads. The hook scripts themselves are unchanged (the Codex and Hermes
adapters parse their plain text).

Merge rule: entries whose command names `<repo>/.claude/hooks/` are ours and are replaced; every other key and entry
in the file is kept. An existing file that is not a JSON object is refused (exit 1), never overwritten.

Usage: install_session_hooks.py [--target PATH] [--check | --remove]
  (default)  write or refresh our entries; prints `session hooks: installed|unchanged ...`
  --check    exit 0 when the file already holds exactly our entries, 1 otherwise; writes nothing
  --remove   delete our entries (the owner's opt-out); keeps everything else
"""
import argparse
import json
import os
import shlex
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def our_hooks(root: Path) -> dict:
    r = shlex.quote(str(root))
    cd = f"cd {r} && "
    wrap = f"python3 {r}/scripts/hook_context.py"
    return {
        "SessionStart": [{"hooks": [{"type": "command",
                                     "command": f"{cd}CLAUDE_PROJECT_DIR={r} bash {r}/.claude/hooks/session-start.sh"}]}],
        "UserPromptSubmit": [{"hooks": [{"type": "command", "command": f"{cd}python3 {r}/.claude/hooks/wiki-context.py"}]}],
        "PostToolUse": [{"matcher": "Edit|Write|Read", "hooks": [{"type": "command",
                         "command": f"{cd}{wrap} PostToolUse -- python3 {r}/.claude/hooks/edit-snapshot.py"}]}],
        "PreToolUse": [{"matcher": "Grep", "hooks": [{"type": "command",
                        "command": f"{cd}{wrap} PreToolUse -- python3 {r}/.claude/hooks/graft-first-nag.py"}]}],
        "Stop": [{"hooks": [{"type": "command", "command": f"{cd}bash {r}/.claude/hooks/turn-retro-gate.sh"}]}],
    }


def _ours(entry: object, marker: str) -> bool:
    hooks = entry.get("hooks") if isinstance(entry, dict) else None
    return isinstance(hooks, list) and any(isinstance(h, dict) and marker in str(h.get("command", "")) for h in hooks)


def merged(current: dict, root: Path, remove: bool) -> dict:
    marker = f"{root}/.claude/hooks/"
    out = dict(current)
    hooks = dict(out.get("hooks") or {})
    for event in sorted(set(hooks) | set(our_hooks(root))):
        kept = [e for e in (hooks.get(event) or []) if not _ours(e, marker)]
        if not remove:
            kept += our_hooks(root).get(event, [])
        if kept:
            hooks[event] = kept
        else:
            hooks.pop(event, None)
    if hooks:
        out["hooks"] = hooks
    else:
        out.pop("hooks", None)
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
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
    os.chmod(tmp, 0o644)
    os.replace(tmp, target)
    verb = "removed ours from" if args.remove else "installed 5 in"
    print(f"session hooks: {verb} {target} (live from the next tool call)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
