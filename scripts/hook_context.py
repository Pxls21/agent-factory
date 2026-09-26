#!/usr/bin/env python3
"""hook_context.py — run a Claude Code hook command and hand its stdout to the model as additionalContext, stamped.

Claude Code shows a PreToolUse/PostToolUse hook's plain stdout only in the transcript view; the model never reads it.
Measured live 2026-09-24 (task #214, AF-AP-172): a PostToolUse hook printing plain text ran on every Bash call and
nothing reached the model; the same hook printing {"hookSpecificOutput": {"hookEventName": ..., "additionalContext":
...}} did, and so did the PreToolUse form. edit-snapshot.py and graft-first-nag.py print plain text on purpose, because
the Codex and Hermes adapters under harness-ports/ parse it, so the conversion happens here, at the registration layer.

S1-RATE (task #295, D-092 item 3): every text this wrapper hands the model carries an id, so the agent can score it and
scripts/s1_scores.py can pair each score with its injection in the transcripts. The first line is `[S1 <id> <source>]`
(<id>: `s1-` and 8 random lowercase hex digits; <source>: the wrapped hook's file stem), the last line asks for the
score (REQUEST), and the lines between are the hook's text, byte for byte. The agent begins its next text with
`S1-RATE <id> rel=<0-3> use=<0-3>` and an optional note, one line per injection. The section "the stamp" below is the
ONE implementation of the stamp and the score syntax; s1_scores.py imports it from here.

Usage: hook_context.py <HookEventName> -- <command> [args...]
  stdin passes through unchanged. Exit 0 with output -> one JSON object carrying the stamped output as additionalContext.
  Exit 0 with no output -> no output. Exit 2 with a non-empty stderr on PreToolUse or PostToolUse (a block whose message
  the model reads, such as the search intercept's answer) -> the stderr stamped, the exit code and stdout unchanged; on
  UserPromptSubmit and SessionStart the harness shows that stderr to the person only, so it passes unstamped. Any other
  non-zero exit passes stdout, stderr and the exit code through unchanged. A usage error or a command that cannot run
  prints one stderr line and exits 0: a broken registration must never block a tool call.

The stamp never costs the context. With the file <state>/s1-rate-off the output is the unstamped form. A stamped text
over STAMP_MAX_CHARS goes out unstamped: the harness swaps a hook text over 10,000 characters for a 2 KB preview of its
head (AF-AP-183), which would drop the hook's own text. Any failure while stamping hands over the unstamped text.
Telemetry: one JSON line per stamp in <state>/injections.jsonl (time, id, source, event, tool, the payload's
tool_use_id, session, agent or `main`, exit code, and the bytes and sha256 of the stamped text as the model receives
it); never the text. A failed telemetry write loses the line, never the stamp.

<state> is <repo>/.jev. Test seam, read once at start: AF_S1_RATE_STATE (the state directory instead of <repo>/.jev).
"""
import json
import os
import re
import subprocess
import sys
import time

EVENTS = ("PreToolUse", "PostToolUse", "UserPromptSubmit", "SessionStart")
TIMEOUT_S = 55  # under Claude Code's 60 s default hook timeout
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCK_EVENTS = ("PreToolUse", "PostToolUse")   # the events whose exit-2 stderr the model reads
STAMP_MAX_CHARS = 9_500    # UTF-16 units, as the harness counts: 500 under its 10,000-character swap (AF-AP-183)
LOG_MAX_BYTES = 4_000_000  # then injections.jsonl moves to injections.jsonl.1

# ---------------------------------------------------------------- the stamp: the ONE implementation
# scripts/s1_scores.py imports these names. The tests never do: they write the expected lines as literals.

ID_RX = r"s1-[0-9a-f]{8}"
SOURCE_RX = r"[A-Za-z0-9_.-]+"
STAMP_RX = re.compile(r"\[S1 (" + ID_RX + r") (" + SOURCE_RX + r")\]")                   # the first line, whole
NOTE_MAX = 120
SCORE_RX = re.compile(r"S1-RATE (" + ID_RX + r") rel=([0-3]) use=([0-3])(?: (\S.{0,%d}))?" % (NOTE_MAX - 1))  # a line
REQUEST = ('Begin your next text with "S1-RATE {id} rel=R use=U" (+ a note <=120 chars: why, if a 0), one line per '
           'unscored injection. rel 0 unrelated,1 same area not this step,2 relevant to this step,3 governs it; '
           'use 0 noise/known,1 confirms,2 used it,3 changed what I did')
SCRIPT_RX = re.compile(r"(" + SOURCE_RX + r")\.(?:py|sh|js|mjs|cjs|rb|pl)")


def new_id():
    return "s1-" + os.urandom(4).hex()


def request(sid):
    """The last line of a stamped text: what to write, and the scale."""
    return REQUEST.format(id=sid)


def stamp(text, source, sid):
    """The stamped form of `text`: the stamp line, `text` as it is (with a newline after it when it has none), the
    request line."""
    return f"[S1 {sid} {source}]\n{text}{'' if text.endswith(chr(10)) else chr(10)}{request(sid)}"


def source_of(cmd):
    """The wrapped hook's file stem: the first argument that names a script file, else the command's own name."""
    for arg in cmd:
        m = SCRIPT_RX.fullmatch(os.path.basename(arg))
        if m:
            return m.group(1)
    return re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(cmd[0]))[:64] or "hook"


# ---------------------------------------------------------------- the wrapper

def fields(data):
    """The telemetry fields the payload gives: tool, tool_use_id, session, agent (`main` outside a subagent)."""
    try:
        p = json.loads(data.decode("utf-8")) if data.strip() else {}
    except ValueError:
        p = {}
    p = p if isinstance(p, dict) else {}

    def s(key):
        v = p.get(key)
        return v if isinstance(v, str) and v else None
    return {"tool": s("tool_name"), "tool_use_id": s("tool_use_id"), "session": s("session_id"),
            "agent": s("agent_id") or "main"}


def log(state, rec):
    """Append `rec`, with the time, as one line to <state>/injections.jsonl (0600, never through a link, never blocking
    on a FIFO)."""
    try:
        import stat
        rec = {"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **rec}
        path = os.path.join(state, "injections.jsonl")
        if not os.path.isdir(state):
            os.makedirs(state, mode=0o700, exist_ok=True)
        try:
            if os.path.getsize(path) > LOG_MAX_BYTES:
                os.replace(path, path + ".1")
        except FileNotFoundError:
            pass
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NONBLOCK | os.O_NOFOLLOW, 0o600)
        try:
            if stat.S_ISREG(os.fstat(fd).st_mode):
                os.write(fd, (json.dumps(rec, sort_keys=True) + "\n").encode("utf-8"))
        finally:
            os.close(fd)
    except Exception:
        pass                                                    # telemetry never costs the stamp or the context


def stamped(text, event, cmd, data, code, state, tail=""):
    """`text` stamped (and `tail` after it), or `text` itself: with the off switch, when the stamped text would pass
    STAMP_MAX_CHARS (logged as `too-long`), and on any failure (its type logged), so the context always goes out."""
    try:
        if os.path.lexists(os.path.join(state, "s1-rate-off")):  # a dangling link counts too
            return text
        sid, source = new_id(), source_of(cmd)
        out = stamp(text, source, sid) + tail
        if len(out.encode("utf-16-le")) // 2 > STAMP_MAX_CHARS:
            log(state, {"event": event, "source": source, "skipped": "too-long"})
            return text
        import hashlib
        raw = out.encode("utf-8")
        log(state, {"id": sid, "source": source, "event": event, **fields(data), "exit": code, "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest()})
        return out
    except Exception as exc:
        log(state, {"event": event, "error": type(exc).__name__})
        return text


def main(argv: list[str]) -> int:
    if len(argv) < 4 or argv[1] not in EVENTS or argv[2] != "--":
        print("hook_context: usage: hook_context.py {%s} -- <command> [args...]" % "|".join(EVENTS), file=sys.stderr)
        return 0
    event, cmd = argv[1], argv[3:]
    state = os.environ.get("AF_S1_RATE_STATE") or os.path.join(ROOT, ".jev")
    data = sys.stdin.buffer.read()
    try:
        proc = subprocess.run(cmd, input=data, capture_output=True, timeout=TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"hook_context: {cmd[0]} did not run: {exc}", file=sys.stderr)
        return 0
    out = proc.stdout.decode("utf-8", "replace")
    if proc.returncode != 0:
        sys.stdout.write(out)
        err = proc.stderr.decode("utf-8", "replace")
        if proc.returncode == 2 and err.strip() and event in BLOCK_EVENTS:
            err = stamped(err, event, cmd, data, 2, state, tail="\n")
        sys.stderr.write(err)
        return proc.returncode
    if out.strip():
        ctx = stamped(out.rstrip("\n"), event, cmd, data, 0, state)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": ctx}}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
