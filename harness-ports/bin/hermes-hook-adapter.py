#!/usr/bin/env python3
"""Hermes -> project-hook adapter.

Hermes shell hooks are deliberately Claude-Code-compatible on the INPUT side
(JSON on stdin: hook_event_name, tool_name, tool_input, session_id, cwd, extra)
and accept Claude-Code block shapes on the output side. But the RETURN CONTRACT
is per-event, and it is not the same as Claude Code's:

  pre_llm_call   Directive. Injects into the user message, but ONLY via
                 {"context": "..."} on stdout. Plain text is NOT injected.
  pre_verify     Directive. Uses {"decision":"block","reason":...} /
                 {"action":"continue","message":...}. Exit-2-plus-stderr is
                 documented for pre_tool_call, not for this event.
  pre_tool_call  Directive. block / modify / approve only — there is NO
                 advisory channel, so a warn-don't-block hook cannot speak here.
  post_tool_call Observer. RETURN IS IGNORED. Nothing it prints reaches the
                 model, ever.
  on_session_start Observer. Return ignored; side effects still happen.

The project hooks were written for Claude Code (plain stdout = context, exit 2 +
stderr = block). Wiring them straight into Hermes would produce hooks that run
and are silently discarded. This adapter translates where translation is
possible and REFUSES to pretend where it is not: for observer events it emits
nothing and says so on stderr, rather than implying the model saw the output.

Usage: hermes-hook-adapter.py <hook-file-name> <hermes-event>
  e.g. hermes-hook-adapter.py wiki-context.py pre_llm_call
       hermes-hook-adapter.py turn-retro-gate.sh pre_verify

Docs: hermes-agent website/docs/user-guide/features/hooks.md (shell hooks: the
configuration schema, the JSON wire protocol, and the per-event return table).
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Events whose return value Hermes discards. Listed explicitly so a future
# mis-wiring fails loudly here instead of silently doing nothing.
OBSERVER_EVENTS = {
    "post_tool_call", "post_llm_call", "on_session_start", "on_session_end",
    "subagent_start", "subagent_stop", "pre_api_request", "post_api_request",
}
INJECT_EVENTS = {"pre_llm_call"}
BLOCK_EVENTS = {"pre_verify", "pre_tool_call"}


def repo_root() -> Path:
    try:
        p = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, timeout=5)
        if p.returncode == 0 and p.stdout.strip():
            return Path(p.stdout.strip())
    except Exception as e:  # fail-LOUD: say which root we fell back to and why
        print(f"hermes-hook-adapter: git rev-parse failed ({e}) — using the script-relative repo root", file=sys.stderr)
    return Path(__file__).resolve().parents[2]


def spool_file(root: Path, session_id: str) -> Path:
    """Where a session's deferred hook output waits for the next turn.

    The OS temp dir, not the repo. Two reasons, both learned the hard way:
      - `<root>/.git` is a FILE inside a git worktree, not a directory, so
        writing under it raises NotADirectoryError. (The repo's own post-commit
        hook has the same bug; it prints "/.git/wiki-stale: Not a directory".)
      - The spool is ephemeral per-session scratch. It must never land in the
        working tree, where it would show up in `git status` and risk being
        committed.

    The repo path is hashed into the name so two clones on one machine, and two
    lanes in one clone, never share a spool.
    """
    tag = hashlib.sha256(str(root).encode()).hexdigest()[:12]
    sid = "".join(c for c in session_id if c.isalnum() or c in "-_")[:64] or "default"
    return Path(tempfile.gettempdir()) / f"hermes-hook-spool-{tag}-{sid}"


def main() -> int:
    if len(sys.argv) < 3:
        print("hermes-hook-adapter: usage: <hook-file> <hermes-event> [--spool]",
              file=sys.stderr)
        return 0
    hook_name, event = sys.argv[1], sys.argv[2]
    root = repo_root()
    hook = root / ".claude" / "hooks" / hook_name
    if not hook.is_file():
        print(f"hermes-hook-adapter: {hook} not found — hook did NOT run", file=sys.stderr)
        return 0

    # stdin is a pipe: read it exactly ONCE, before anything that needs the
    # payload. (An earlier revision read it twice — once to derive the spool
    # name, once for the payload — and the second read got an empty string.)
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception as e:  # fail-LOUD: a malformed payload is a harness bug, not silence
        print(f"hermes-hook-adapter: unreadable hook payload on stdin ({e}) — treating as empty", file=sys.stderr)
        payload = {}

    # Spool file: keyed per repo AND per session, so parallel lanes never
    # cross-inject each other's snapshots.
    spool_path = None
    if "--spool" in sys.argv[3:]:
        spool_path = str(spool_file(root, str(payload.get("session_id") or "default")))

    # Hermes carries the user message in extra.user_message; the project hooks
    # read Claude Code's top-level `prompt`. Codex happens to use `prompt` too
    # (codex-rs/hooks/src/events/user_prompt_submit.rs:32), so only Hermes needs
    # this. Without it wiki-context.py reads "" and returns nothing forever —
    # caught by the pre_llm_call case in test_hermes_hook_adapter.py, which is
    # why that case has no "or silent" escape.
    if not payload.get("prompt"):
        extra = payload.get("extra") or {}
        msg = extra.get("user_message") or payload.get("user_message") or ""
        if msg:
            payload = dict(payload, prompt=msg)

    # Hermes names the search tool `search_files`; the project's graft-first nag
    # keys on Claude Code's `Grep`. Same concept, different label.
    if payload.get("tool_name") == "search_files":
        payload = dict(payload, tool_name="Grep")
    # Hermes edits arrive as `patch` / `write_file`.
    elif payload.get("tool_name") in ("patch", "write_file"):
        ti = dict(payload.get("tool_input") or {})
        ti.setdefault("file_path", ti.get("path") or ti.get("file") or "")
        ti.setdefault("new_string", ti.get("content") or ti.get("new_str") or "")
        payload = dict(payload, tool_name="Edit", tool_input=ti)

    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root))
    runner = ["python3", str(hook)] if hook.suffix == ".py" else ["bash", str(hook)]
    try:
        p = subprocess.run(runner, input=json.dumps(payload), capture_output=True,
                           text=True, cwd=str(root), env=env, timeout=280)
    except Exception as e:
        print(f"hermes-hook-adapter: {hook_name} failed: {e}", file=sys.stderr)
        return 0

    out, err, rc = p.stdout.strip(), p.stderr.strip(), p.returncode

    if event in OBSERVER_EVENTS:
        # Hermes discards returns here, so printing to stdout would imply the
        # model saw something it did not. Two honest options:
        #
        #   default  — say so on stderr (which Hermes logs) and drop it.
        #   --spool  — append to the spool file, which the NEXT pre_llm_call
        #              drains and injects. This is a real mechanism (two real
        #              hooks and a file), not a claim — but note the LATENCY:
        #              pre_llm_call fires once per turn BEFORE the tool loop, so
        #              output spooled during turn N reaches the model at the
        #              START of turn N+1, not immediately after the tool call.
        #              That is strictly better than discarding it and strictly
        #              worse than Claude Code's PostToolUse, which injects in
        #              the same turn. Do not describe it as equivalent.
        if out:
            if spool_path:
                try:
                    with open(spool_path, "a", encoding="utf-8") as fh:
                        fh.write(out.rstrip() + "\n\n")
                    print(f"hermes-hook-adapter: {hook_name} spooled {len(out)} bytes "
                          f"for the next turn's pre_llm_call injection "
                          f"('{event}' is an observer — nothing reaches the model now).",
                          file=sys.stderr)
                except OSError as e:
                    print(f"hermes-hook-adapter: spool write failed ({e}) — "
                          f"{hook_name} output DISCARDED.", file=sys.stderr)
            else:
                print(f"hermes-hook-adapter: {hook_name} produced {len(out)} bytes on "
                      f"'{event}', which is an OBSERVER event — Hermes discards it. "
                      f"The model did NOT see this.", file=sys.stderr)
        return 0

    if event in INJECT_EVENTS:
        # Drain anything observer hooks spooled since the last turn and prepend
        # it, so the edit snapshots taken during the previous turn are not lost.
        parts = []
        if spool_path and os.path.exists(spool_path):
            try:
                with open(spool_path, "r", encoding="utf-8") as fh:
                    spooled = fh.read().strip()
                os.unlink(spool_path)      # drain: inject once, never repeat
                if spooled:
                    parts.append("[deferred edit snapshots from the previous turn — "
                                 "Hermes cannot inject these at edit time]\n" + spooled)
            except OSError as e:
                print(f"hermes-hook-adapter: spool drain failed ({e})", file=sys.stderr)
        if out:
            parts.append(out)
        if parts:
            print(json.dumps({"context": "\n\n".join(parts)}))
        return 0

    if event in BLOCK_EVENTS:
        # Claude Code's block contract is exit 2 with the reason on stderr.
        if rc == 2 and err:
            print(json.dumps({"decision": "block", "reason": err}))
            return 0
        if out:
            print(json.dumps({"decision": "block", "reason": out}))
        return 0

    print(f"hermes-hook-adapter: unmapped event '{event}' — nothing emitted",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
