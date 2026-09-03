#!/usr/bin/env python3
"""Deterministic proof that the Hermes deferred-snapshot spool works.

THE CLAIM, stated narrowly so it cannot be overstated: Hermes's `post_tool_call`
is an OBSERVER event — its return is discarded, so an edit snapshot can never
reach the model at edit time, the way Claude Code's PostToolUse does. Spooling it
to disk lets the NEXT `pre_llm_call` inject it. That is a real mechanism (two real
hooks and a file), and it costs ONE TURN of latency. It is strictly better than
discarding the snapshot and strictly worse than injecting it in place. Anything
in the docs that calls it "equivalent" is wrong.

This exercises the whole round trip through the REAL hooks, and both ways it
could be a lie: never written, or injected forever.

Run: python3 harness-ports/tests/test_hermes_spool.py
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AD = ROOT / "harness-ports" / "bin" / "hermes-hook-adapter.py"
SID = "spooltest"

# Fixtures adapted for agent-factory: edit-snapshot.py checks p.is_file()
# and wiki-context.py checks WIKI.is_dir(). Same approach as
# test_hermes_hook_adapter.py: create real files for the hooks to process.
_FIXTURE_DIR = tempfile.mkdtemp(prefix="hp-spool-test-")
_FIXTURE_PY = os.path.join(_FIXTURE_DIR, "emitter.py")
with open(_FIXTURE_PY, "w") as _f:
    _f.write("import os, math\n\ndef emit(x):\n    return x\n")

_WIKI_DIR = ROOT / "wiki" / "topics"
_WIKI_CREATED = False
_LIVE_STATE = _WIKI_DIR / "live-state.md"
if not _LIVE_STATE.is_file():
    _WIKI_DIR.mkdir(parents=True, exist_ok=True)
    _LIVE_STATE.write_text("# Live state\n\nStatus: test fixture for harness-port tests.\n")
    _WIKI_CREATED = True


def spool_for(sid: str) -> Path:
    tag = hashlib.sha256(str(ROOT).encode()).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / f"hermes-hook-spool-{tag}-{sid}"


EDIT = {"hook_event_name": "post_tool_call", "tool_name": "patch",
        "tool_input": {"path": _FIXTURE_PY,
                       "content": 'v = os.environ.get("X")\nif math.isnan(y):\n    pass'},
        "session_id": SID, "cwd": str(ROOT)}
PROMPT = {"hook_event_name": "pre_llm_call", "tool_name": None, "tool_input": None,
          "session_id": SID, "cwd": str(ROOT),
          "extra": {"user_message": "check the GA gate pipeline", "is_first_turn": False}}


def run(hook, event, payload, spool=False):
    args = [sys.executable, str(AD), hook, event] + (["--spool"] if spool else [])
    p = subprocess.run(args, input=json.dumps(payload), capture_output=True,
                       text=True, cwd=str(ROOT), timeout=180)
    return p.stdout, p.stderr, p.returncode


def ctx_of(out):
    try:
        return json.loads(out).get("context", "")
    except Exception:
        return ""


def main() -> int:
    fails = 0

    def check(label, cond, why):
        nonlocal fails
        if not cond:
            fails += 1
        print(f"[{'PASS' if cond else 'FAIL'}] {label}\n         because: {why}")

    for sid in (SID, "otherlane"):
        spool_for(sid).unlink(missing_ok=True)

    o, e, _ = run("edit-snapshot.py", "post_tool_call", EDIT, spool=True)
    sp = spool_for(SID)
    check("post_tool_call --spool writes the file and stays silent on stdout",
          o.strip() == "" and sp.exists() and "EDIT SNAPSHOT" in sp.read_text(),
          "Hermes discards observer returns, so it must not print; the snapshot "
          "has to survive on disk instead")
    check("stderr says SPOOLED, not delivered", "spooled" in e.lower(),
          "an operator reading logs must not think the model saw it this turn")

    o, _, _ = run("wiki-context.py", "pre_llm_call", PROMPT, spool=True)
    ctx = ctx_of(o)
    check("next pre_llm_call injects the spooled snapshot",
          "EDIT SNAPSHOT" in ctx and "deferred edit snapshots" in ctx,
          "the whole point: the snapshot reaches the model one turn later, "
          "labelled as deferred so it is not mistaken for live state")
    check("the same injection still carries the wiki context", "live-state" in ctx,
          "draining the spool must not displace what pre_llm_call already did")

    check("spool file removed after draining", not sp.exists(),
          "inject once; a file that is never drained repeats every turn")
    ctx2 = ctx_of(run("wiki-context.py", "pre_llm_call", PROMPT, spool=True)[0])
    check("second pre_llm_call does NOT repeat the snapshot",
          "EDIT SNAPSHOT" not in ctx2,
          "negative control — proves the drain is real, not just a read")

    o, e, _ = run("edit-snapshot.py", "post_tool_call", EDIT, spool=False)
    check("without --spool: still silent, still says OBSERVER on stderr",
          o.strip() == "" and "OBSERVER" in e,
          "the default must keep refusing to imply delivery")
    spool_for(SID).unlink(missing_ok=True)

    run("edit-snapshot.py", "post_tool_call", dict(EDIT, session_id="otherlane"),
        spool=True)
    check("spool is keyed per session",
          spool_for("otherlane").exists() and not spool_for(SID).exists(),
          "two lanes running at once must not drain each other's snapshots")
    spool_for("otherlane").unlink(missing_ok=True)

    check("spool never lands in the working tree",
          str(spool_for(SID)).startswith(tempfile.gettempdir()),
          "it must not appear in git status; and <root>/.git is a FILE inside a "
          "worktree, so writing there raises NotADirectoryError")

    if _WIKI_CREATED:
        _LIVE_STATE.unlink(missing_ok=True)
        try:
            _WIKI_DIR.rmdir()
            _WIKI_DIR.parent.rmdir()
        except OSError:
            pass

    print(f"\n{9 - fails}/9 passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
