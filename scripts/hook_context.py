#!/usr/bin/env python3
"""hook_context.py — run a Claude Code hook command and hand its stdout to the model as additionalContext.

Claude Code shows a PreToolUse/PostToolUse hook's plain stdout only in the transcript view; the model never reads it.
Measured live 2026-09-24 (task #214, AF-AP-172): a PostToolUse hook printing plain text ran on every Bash call and
nothing reached the model; the same hook printing {"hookSpecificOutput": {"hookEventName": ..., "additionalContext":
...}} did, and so did the PreToolUse form. edit-snapshot.py and graft-first-nag.py print plain text on purpose, because
the Codex and Hermes adapters under harness-ports/ parse it, so the conversion happens here, at the registration layer.

Usage: hook_context.py <HookEventName> -- <command> [args...]
  stdin passes through unchanged. Exit 0 with output -> one JSON object carrying the output as additionalContext.
  Exit 0 with no output -> no output. A non-zero exit passes stdout, stderr and the exit code through unchanged, so a
  blocking hook (exit 2) keeps its meaning. A usage error or a command that cannot run prints one stderr line and
  exits 0: a broken registration must never block a tool call.
"""
import json
import subprocess
import sys

EVENTS = ("PreToolUse", "PostToolUse", "UserPromptSubmit", "SessionStart")
TIMEOUT_S = 55  # under Claude Code's 60 s default hook timeout


def main(argv: list[str]) -> int:
    if len(argv) < 4 or argv[1] not in EVENTS or argv[2] != "--":
        print("hook_context: usage: hook_context.py {%s} -- <command> [args...]" % "|".join(EVENTS), file=sys.stderr)
        return 0
    event, cmd = argv[1], argv[3:]
    data = sys.stdin.buffer.read()
    try:
        proc = subprocess.run(cmd, input=data, capture_output=True, timeout=TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"hook_context: {cmd[0]} did not run: {exc}", file=sys.stderr)
        return 0
    out = proc.stdout.decode("utf-8", "replace")
    if proc.returncode != 0:
        sys.stdout.write(out)
        sys.stderr.write(proc.stderr.decode("utf-8", "replace"))
        return proc.returncode
    if out.strip():
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": out.rstrip("\n")}}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
