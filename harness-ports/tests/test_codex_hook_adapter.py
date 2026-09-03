#!/usr/bin/env python3
"""Deterministic, LLM-free proof that the Codex hook adapter actually translates.

Runs the REAL .claude/hooks scripts through harness-ports/bin/codex-hook-adapter.py
with real Codex-shaped payloads. Every case is a PAIR: a positive that must produce
a specific string, and a negative control that must produce NOTHING for a stated
reason. Without the negatives an adapter that printed a constant would pass.

Why this test exists: Codex's hook wire protocol matches Claude Code's (snake_case
tool_name/tool_input on stdin, plain stdout -> additionalContext, exit 2 + stderr
blocks) but its TOOL PAYLOADS do not — apply_patch carries {"command": <patch>},
not {file_path, new_string}. A hook wired straight through would fire and print
nothing, forever, and look fine.

Run: python3 harness-ports/tests/test_codex_hook_adapter.py
Exit 0 = all pass. No network, no LLM, no clock dependence.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "harness-ports" / "bin" / "codex-hook-adapter.py"

# The edit-snapshot hook checks p.is_file() before processing, so the test
# fixture needs a real .py file on disk. This is a setup concern, not a
# trading-specific expectation: the adapter test needs ANY parseable .py file
# whose enclosing function can be resolved by the hook's AST walk.
_FIXTURE_DIR = tempfile.mkdtemp(prefix="hp-test-")
_FIXTURE_PY = os.path.join(_FIXTURE_DIR, "emitter.py")
with open(_FIXTURE_PY, "w") as _f:
    _f.write("import os, math\n\ndef emit(x):\n    old = 1\n    return old\n")

PATCH = """*** Begin Patch
*** Update File: {path}
@@ def emit
-    old = 1
+    val = os.environ.get("AF_OTEL")
+    if math.isnan(x):
+        return None
*** End Patch"""


def payload(tool, tool_input, event):
    return json.dumps({"hook_event_name": event, "tool_name": tool,
                       "tool_input": tool_input, "cwd": str(ROOT),
                       "session_id": "test"})


def run(hook, body):
    p = subprocess.run([sys.executable, str(ADAPTER), hook], input=body,
                       capture_output=True, text=True, cwd=str(ROOT), timeout=120)
    return p.stdout, p.stderr, p.returncode


CASES = [
    # --- apply_patch -> edit-snapshot.py -------------------------------------
    # Assertion adapted for agent-factory: uses a temp fixture .py file instead
    # of a repo-internal path (the original used trading/telemetry/emitter.py
    # which existed in trading-system). The premise being tested is unchanged:
    # the adapter translates apply_patch into per-file Edit payloads that the
    # hook processes, and AP-1 (env read) + AP-3 (isnan) are flagged.
    ("apply_patch POSITIVE: .py edit is translated and screened",
     "edit-snapshot.py",
     payload("apply_patch", {"command": PATCH.format(path=_FIXTURE_PY)},
             "PostToolUse"),
     lambda o, e, r: "EDIT SNAPSHOT" in o and "AP-1" in o and "AP-3" in o and r == 0,
     "snapshot printed; AP-1 (env read) and AP-3 (isnan w/o isfinite) both flagged"),
    ("apply_patch NEGATIVE: non-.py file is rejected by the hook's own filter",
     "edit-snapshot.py",
     payload("apply_patch", {"command": PATCH.format(path="docs/NOTES.md")}, "PostToolUse"),
     lambda o, e, r: o.strip() == "" and r == 0,
     "no output — proves the adapter is not manufacturing a snapshot"),
    ("apply_patch NEGATIVE: envelope with no added lines yields nothing",
     "edit-snapshot.py",
     payload("apply_patch",
             {"command": "*** Begin Patch\n*** Update File: src/x.py\n@@\n-gone\n*** End Patch"},
             "PostToolUse"),
     lambda o, e, r: o.strip() == "" and r == 0,
     "deletion-only hunk has no new code to screen"),

    # --- Bash -> graft-first-nag.py ------------------------------------------
    ("Bash POSITIVE: rg on a bare identifier over .py trips the GRAFT-FIRST nag",
     "graft-first-nag.py",
     payload("Bash", {"command": "rg -t py run_gate src/"}, "PreToolUse"),
     lambda o, e, r: "GRAFT-FIRST" in o and r == 0,
     "nag printed — this is the exact shape the owner mandate targets"),
    ("Bash NEGATIVE: quoted literal-token sweep stays legal and silent",
     "graft-first-nag.py",
     payload("Bash", {"command": "rg -t py 'AF_OTEL=1 enabled' src/"}, "PreToolUse"),
     lambda o, e, r: o.strip() == "" and r == 0,
     "literal-token sweeps are explicitly permitted by the mandate"),
    ("Bash NEGATIVE: a non-search shell command is not rewritten into a Grep",
     "graft-first-nag.py",
     payload("Bash", {"command": "pytest -q tests/"}, "PreToolUse"),
     lambda o, e, r: o.strip() == "" and r == 0,
     "parse_search returns None; nothing is delegated"),

    # --- passthrough ---------------------------------------------------------
    ("passthrough NEGATIVE: an unrelated tool reaches the hook unchanged",
     "graft-first-nag.py",
     payload("spawn_agent", {"goal": "x"}, "PreToolUse"),
     lambda o, e, r: o.strip() == "" and r == 0,
     "hook's own tool_name check no-ops; adapter adds nothing"),
]


def main() -> int:
    fails = 0
    for label, hook, body, check, why in CASES:
        o, e, r = run(hook, body)
        ok = check(o, e, r)
        if not ok:
            fails += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
        print(f"         because: {why}")
        if not ok:
            print(f"         rc={r}\n         stdout={o[:400]!r}\n         stderr={e[:400]!r}")
    print(f"\n{len(CASES) - fails}/{len(CASES)} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
