# LS-B9 round 3: the gate runs every test with its own runner (task #339, D-103, D-104)

Role: the LS-B9 builder, resumed (sandbox code-implementer, Opus 5.5). Authored 2026-09-28 20:4xZ by the coordinator.

VERIFY-LS-B9 returned **NOT-READY** on one blocker, F-1 (`tasks/briefs/labeling/VERIFY-LS-B9-report.md`, "Area 2" and
"F-1, third face"; the finding table and the pre-wiring list at its end). The `gate` stack gives the nine
`harness-ports/tests/test_*.py` files to pytest, but they are scripts that `harness-ports/tests/run-all.sh` runs with
`python3` (its line 16), and ten `.sh` files there run with `bash`. pytest collects nothing from five of them, swallows the
failures of one, and stops the whole session on another's module-level `sys.exit`. A real one-line break in
`scripts/pc_bridge_exec.py` gave `gate ... mode=run` `exit 0, 49 passed` while `python3 harness-ports/tests/test_pc_bridge_exec.py`
failed. The coordinator rules F-1 CORE-BLOCKING under D-034: it shows `gate`'s headline capability fake for a whole change
class. This round is the one focused repair; it also takes the small follow-ups that sit in your own files and that the
stacks' wiring needs. Everything else in the table stays a follow-up (task #345 owns the wrappers and `lane_context.sh`).

## CONTRACT (this round)

1. **F-1 (the blocker).** Every file in the union runs under its own runner, or is named "not run" with its reason, never
   silently. pytest files under `tests/`: pytest, as now. `harness-ports/tests/*.py`: `python3 <file>`, one run per file, as
   `run-all.sh` runs them. `harness-ports/tests/*.sh`: `bash <file>`, one run per file (this closes round 2's NOT-done 2). Any
   other union file that is not a runnable test (a fixture module, say): "not run" and why. A nonzero exit from any runner
   fails the run. Tests (red first on round 2's bytes, then green): the three faces of the report (a failing script test fails
   the gate; a script that ends in `sys.exit` no longer stops the other tests; a script that counts failures without raising
   is decided by its own exit code), each through the real registry in a temporary tree, as your
   `test_the_gates_run_step_gives_pytest_a_basetemp_outside_every_work_tree` does.
2. **F-3.** The header carries the counts (files run by pytest, by `python3`, by `bash`, and not run), so the print cap can
   never cut them.
3. **F-2.** `mode=run` refuses a run list wider than a bound (default 40 files; a parameter lifts it) and names the count.
   `tests/test_vendored_manifest.py` is never run whole by the gate: it is named "not run" with the reason (a whole-file run
   copies about 3.4 GB) and the command for its one relevant test
   (`-k test_committed_manifest_matches_fresh_generation`).
4. **F-7.** A step that passes its save cap is killed with SIGKILL at once, with no grace.
5. **F-8.** When a step's leader exits, the runner kills the step's process group, so a child left behind stops writing.
6. **F-11.** `harvest` looks for a lane's long text report only after the previous hand-back call, so an earlier round's
   text is never this round's report.
7. **F-14.** One test each for V1 (the flock), V2 (SIGINT and SIGHUP), V3 (a `\r` in text), V4 (the timeout bound),
   V5 (the label regex) and V9 (the cap boundary); each kills the verifier's mutant.

## EVIDENCE DEMANDS

1. Premise: re-run the block below with `bash scripts/premise_block.sh` from the main tree; stop and report
   CONTRACT-INVALID on a difference in a lane file's hash.
2. Each item: its test, the mutant its test kills (a FAILED line), and a real run on this tree, pasted.
3. The verifier's reproductions, re-run: the `pc_bridge_exec.py` break and the `lane-done-gate.py` break each make
   `gate ... mode=run` exit 1 (in a scratch copy; never edit those files in the main tree); `gate
   paths=harness-ports/bin/omniroute_local_builder.py mode=run graph=no` reports the script's own result.
4. Gates: `tests/test_stack.py` twice and your round-1 set twice, pasted with set ids; `bash harness-ports/tests/run-all.sh`
   once; the CI rehearsal (Python 3.12, no instrument on the PATH, a non-root user if you can).
5. NOT-done and DISCREPANCIES, first in the section.

## BOUNDARY

Your seven files: `scripts/stack.py`, `scripts/stacks.toml`, `scripts/gate_files.py`, `scripts/handback_extract.py`,
`scripts/gate_union.py`, `scripts/lint_files.py`, `tests/test_stack.py`; plus a new helper script if an item needs one (name
it in the section's first lines). Never edit `harness-ports/tests/*`, `run-all.sh`, `scripts/ripwire_review.sh`,
`scripts/sentrux_review.sh`, `scripts/lint_delta.py` or `lane_context.sh`. Write scratch under `/tmp/lsb9r3/` and remove it
at the end.

## STANDING RULES

- Do NOT spawn subagents. No git writes, no PC bridge, no outward-facing action (no PR, comment, issue or publish).
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables. Test secrets are fakes built at
  run time. Never read a `thinking` block's content in any transcript.
- Touch ONLY the files in the boundary; report adjacent defects, never fix them. Other lanes hold other files (`.lanes-live`).
- A private `--basetemp` outside every work tree for every pytest run (`mkdir -p` its parent); never run the whole
  `tests/test_vendored_manifest.py`. Test counts are pasted from `scripts/test_summary.sh` with their set ids
  (`scripts/pc_suite.sh set-id -- <files>`). Stamps come from `date -u`, never typed.
- Long commands in one foreground call each, under 10 minutes; kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text
  of its own.
- The harness refuses a subagent's report-file writes: return the whole round-3 section as the text of your final hand-back
  message, in full, never a summary.

## PREMISE — MEASURED at authoring (2026-09-28 20:4xZ, the main tree at the pushed head; `bash scripts/premise_block.sh`)

```
$ git rev-parse --short HEAD
0d06ae7
$ sha256sum scripts/stack.py scripts/stacks.toml scripts/gate_files.py scripts/handback_extract.py scripts/gate_union.py scripts/lint_files.py tests/test_stack.py | cut -c1-16,65-
84d738b331127be0  scripts/stack.py
0b4eef56349bc5be  scripts/stacks.toml
b732d35f2c649045  scripts/gate_files.py
115416a0624bc59b  scripts/handback_extract.py
ed9de9247b58a31b  scripts/gate_union.py
546400ab9781e56f  scripts/lint_files.py
da6f1fb42b393a94  tests/test_stack.py
$ ls harness-ports/tests/
__pycache__
run-all.sh
test_bridge_token_handling.py
test_codex_hook_adapter.py
test_context_mirrors.sh
test_hermes_hook_adapter.py
test_hermes_session_export.py
test_hermes_spool.py
test_lane_context.sh
test_lane_done_gate.py
test_lane_profile.sh
test_omniroute_local_builder.py
test_pc_bridge_exec.py
test_pc_lane.sh
test_pc_lane_admission.sh
test_pc_lane_dispatcher.sh
test_qwen_matrix.py
test_qwen_matrix_sh.sh
test_qwen_server.sh
test_sync_skills.sh
$ grep -n 'python3\|bash ' harness-ports/tests/run-all.sh | head -12
5:#   bash harness-ports/tests/run-all.sh
16:  out="$(python3 "$HERE/$t" 2>&1)"; rc=$?
22:out="$(bash "$HERE/test_lane_profile.sh" 2>&1)"; rc=$?
27:out="$(bash "$HERE/test_pc_lane.sh" 2>&1)"; rc=$?
32:out="$(bash "$HERE/test_pc_lane_dispatcher.sh" 2>&1)"; rc=$?
37:out="$(bash "$HERE/test_pc_lane_admission.sh" 2>&1)"; rc=$?
42:out="$(bash "$HERE/test_qwen_server.sh" 2>&1)"; rc=$?
47:out="$(python3 "$HERE/test_qwen_matrix.py" 2>&1)"; rc=$?
52:out="$(bash "$HERE/test_qwen_matrix_sh.sh" 2>&1)"; rc=$?
57:out="$(bash "$HERE/test_lane_context.sh" 2>&1)"; rc=$?
62:out="$(bash "$HERE/test_context_mirrors.sh" 2>&1)"; rc=$?
67:out="$(bash "$HERE/test_sync_skills.sh" 2>&1)"; rc=$?
$ python3 harness-ports/tests/test_pc_bridge_exec.py 2>&1 | tail -1
test_pc_bridge_exec: 8 checks passed
$ python3 -m pytest --collect-only -q -p no:cacheprovider harness-ports/tests/test_pc_bridge_exec.py 2>&1 | tail -1
no tests collected in 0.04s
$ python3 scripts/stack.py --log-dir /tmp/lsb9r3-premise-logs gate paths=scripts/pc_bridge_exec.py mode=plan graph=no 2>&1 | grep -E 'harness-ports|not run|run list' | head -8
harness-ports/tests/test_bridge_token_handling.py
harness-ports/tests/test_pc_bridge_exec.py
harness-ports/tests/test_bridge_token_handling.py  code:23  comment:1
harness-ports/tests/test_pc_bridge_exec.py  comment:1
harness-ports/tests/test_bridge_token_handling.py
harness-ports/tests/test_pc_bridge_exec.py
harness-ports/tests/test_bridge_token_handling.py  gate_files
harness-ports/tests/test_pc_bridge_exec.py  gate_files
$ rm -rf /tmp/lsb9r3-premise-logs
```
