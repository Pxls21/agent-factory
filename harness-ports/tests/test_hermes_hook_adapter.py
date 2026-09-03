#!/usr/bin/env python3
"""Deterministic, LLM-free proof for the Hermes hook adapter.

Hermes's shell-hook RETURN contract is per-event and unlike Claude Code's:
pre_llm_call injects only via {"context": ...}; pre_verify wants
{"decision":"block","reason":...}; post_tool_call and on_session_start are
OBSERVERS whose return is discarded outright. The dangerous failure here is a
hook that runs, prints, and is silently thrown away — so the observer cases
below assert stdout is EMPTY and that the adapter said so on stderr.

Run: python3 harness-ports/tests/test_hermes_hook_adapter.py
"""
import atexit
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AD = ROOT / "harness-ports" / "bin" / "hermes-hook-adapter.py"


def _git_common_dir():
    """Works in linked worktrees where .git is a file, not a directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(ROOT), capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            p = Path(result.stdout.strip())
            if not p.is_absolute():
                p = ROOT / p
            return p.resolve()
    except (subprocess.SubprocessError, OSError):
        pass
    return ROOT / ".git"


_GIT_DIR = _git_common_dir()

# Fixtures adapted for agent-factory: the edit-snapshot hook checks
# p.is_file() and the wiki-context hook checks WIKI.is_dir(), so the test
# must supply real files. These are test fixtures, not project state.
_FIXTURE_TD = tempfile.TemporaryDirectory(prefix="hp-test-")
_FIXTURE_DIR = _FIXTURE_TD.name
_FIXTURE_PY = os.path.join(_FIXTURE_DIR, "emitter.py")
with open(_FIXTURE_PY, "w") as _f:
    _f.write("import os\n\ndef emit(x):\n    return x\n")

# wiki fixture: wiki-context.py reads wiki/topics/live-state.md relative to
# the repo root. Create it for the test if it does not exist, clean up after.
_WIKI_DIR = ROOT / "wiki" / "topics"
_WIKI_CREATED = False
_LIVE_STATE = _WIKI_DIR / "live-state.md"
if not _LIVE_STATE.is_file():
    _WIKI_DIR.mkdir(parents=True, exist_ok=True)
    _LIVE_STATE.write_text("# Live state\n\nStatus: test fixture for harness-port tests.\n")
    _WIKI_CREATED = True


def _ensure_retro_fires():
    """The retro gate keys on .git/turn-retro-acked matching HEAD. Remove the
    sentinel so the hook fires for this test, and restore it afterward. Without
    this, a prior hook firing in the same session makes the test always pass
    vacuously (exit 0, no output)."""
    sent = _GIT_DIR / "turn-retro-acked"
    saved = sent.read_bytes() if sent.is_file() else None
    sent.unlink(missing_ok=True)
    return sent, saved


_RETRO_SENTINEL, _RETRO_SAVED = _ensure_retro_fires()


def _restore_sentinel():
    """Restore the sentinel to its pre-test state."""
    if _RETRO_SAVED is not None:
        _RETRO_SENTINEL.write_bytes(_RETRO_SAVED)
    else:
        _RETRO_SENTINEL.unlink(missing_ok=True)


atexit.register(_restore_sentinel)


def run(hook, event, payload):
    p = subprocess.run([sys.executable, str(AD), hook, event],
                       input=json.dumps(payload), capture_output=True,
                       text=True, cwd=str(ROOT), timeout=300)
    return p.stdout, p.stderr, p.returncode


def is_ctx(o):
    try:
        return "context" in json.loads(o) and json.loads(o)["context"].strip() != ""
    except Exception:
        return False


def is_block(o):
    try:
        d = json.loads(o)
        return d.get("decision") == "block" and d.get("reason", "").strip() != ""
    except Exception:
        return False


SEARCH = {"hook_event_name": "pre_tool_call", "tool_name": "search_files",
          "tool_input": {"pattern": "run_gate", "path": "src/", "glob": "", "type": "py"},
          "session_id": "t", "cwd": str(ROOT)}
LITERAL = {"hook_event_name": "pre_tool_call", "tool_name": "search_files",
           "tool_input": {"pattern": "AF_OTEL=1", "path": "src/", "glob": "",
                          "type": "py"},
           "session_id": "t", "cwd": str(ROOT)}
EDIT = {"hook_event_name": "post_tool_call", "tool_name": "patch",
        "tool_input": {"path": _FIXTURE_PY,
                       "content": 'v = os.environ.get("X")'},
        "session_id": "t", "cwd": str(ROOT)}
PROMPT = {"hook_event_name": "pre_llm_call", "tool_name": None, "tool_input": None,
          "session_id": "t", "cwd": str(ROOT),
          "extra": {"user_message": "check the GA gate pipeline", "is_first_turn": True}}

CASES = [
    ("pre_verify POSITIVE: retro gate's exit-2+stderr becomes a Hermes block",
     "turn-retro-gate.sh", "pre_verify",
     {"hook_event_name": "pre_verify", "session_id": "t", "cwd": str(ROOT),
      "extra": {"changed_paths": ["src/x.py"]}},
     lambda o, e, r: is_block(o),
     'stdout is {"decision":"block","reason":<the retro checklist>}'),

    ("pre_tool_call POSITIVE: search_files is mapped to Grep so the nag can fire",
     "graft-first-nag.py", "pre_tool_call", SEARCH,
     lambda o, e, r: is_block(o) and "GRAFT-FIRST" in o,
     "tool_name search_files -> Grep; nag text carried in the block reason"),

    ("pre_tool_call NEGATIVE: a literal-token sweep stays silent",
     "graft-first-nag.py", "pre_tool_call", LITERAL,
     lambda o, e, r: o.strip() == "",
     "literal-token sweeps are legal — no block, no output"),

    ("pre_llm_call POSITIVE: wiki context is wrapped as {\"context\": ...}",
     "wiki-context.py", "pre_llm_call", PROMPT,
     lambda o, e, r: is_ctx(o) and "live-state" in json.loads(o)["context"],
     "a context envelope carrying the live-state snapshot, not an empty return"),

    ("post_tool_call OBSERVER: output is NOT emitted to stdout, and says so",
     "edit-snapshot.py", "post_tool_call", EDIT,
     lambda o, e, r: o.strip() == "" and "OBSERVER" in e,
     "Hermes discards observer returns; the adapter must not imply otherwise"),

    ("on_session_start OBSERVER: same refusal",
     "edit-snapshot.py", "on_session_start", EDIT,
     lambda o, e, r: o.strip() == "",
     "observer event -> nothing on stdout"),
]


def main() -> int:
    fails = 0
    try:
        for label, hook, event, payload, check, why in CASES:
            o, e, r = run(hook, event, payload)
            ok = check(o, e, r)
            if not ok:
                fails += 1
            print(f"[{'PASS' if ok else 'FAIL'}] {label}")
            print(f"         because: {why}")
            if not ok:
                print(f"         rc={r}\n         stdout={o[:400]!r}\n         stderr={e[:400]!r}")
    finally:
        _restore_sentinel()
        if _WIKI_CREATED:
            _LIVE_STATE.unlink(missing_ok=True)
            try:
                _WIKI_DIR.rmdir()
                _WIKI_DIR.parent.rmdir()
            except OSError:
                pass
    print(f"\n{len(CASES) - fails}/{len(CASES)} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
