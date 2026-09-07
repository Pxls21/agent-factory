# Lane B5g — S0-01 frame tee, round 12: guards that can fail, pins that see dataflow, wording that matches the source (sandbox Opus 4.6 `code-implementer`)

**PIN:** the HEAD this brief is committed in (your work lands in the CHILD commit — state both in the report).
**Verdict graded:** `tasks/briefs/s0-01-b5g-support/verify-B5f.md` (VERIFY-B5f, round 11 on checkpoint 8q — NOT-READY on
F1/F3/F4/F6/F7/F9; F5/F8/F10/F11/F12/F2/F14 cheap and verified; read it whole first — EVERY fix below was written and
RUN by the verifier against the PIN and its mutant; use its code verbatim).
**Scope (exactly two files + your report):** `proofs/S0-01/tools/frame_tee.py` and `tests/test_s0_01_frame_tee.py`;
report `tasks/briefs/s0-01-b5g-support/B5g-report.md`. Never `git stash/checkout/restore/reset/add/commit/push`;
mutants on scratchpad COPIES only (the verifier's runners are under the session scratchpad `vb11mut*`, `vb11killers*.py`
— reuse them); kill only processes you started; no outward actions. Every number and every `file:line` in the report
is PASTED from a tool run on the FINAL tree (`grep -n`, `scripts/test_summary.sh`), never typed (F7, AF-AP-37).

## Design (pinned — the verifier's fixes, verbatim)
1. **F6 — the grandchild census cannot skip.** At the three `finally` sites (`test:527`, `:1091`, `:2594` on the PIN):
   `assert gc_pid_path.exists(), "agent never wrote grandchild.pid"` before the read; drop the `except (OSError,
   ValueError): pass` around `int()`/`os.kill` — keep only `ProcessLookupError` as "already gone"; the `if fd:` guard
   inside each agent source string stays (the agent has no framedir without it) but the test asserts the file. Mutant
   PIDFILE-ABSENT (the agents never write the pid file) must die at all three sites — paste the red line.
2. **F9 — the tripwire test asserts its premise (FLAG form).** `test_sigterm_status_satisfies_check_tee_status`
   (`test:2279-2320`): `loaded = False` above the wait, `loaded = True` on the break path, `assert loaded, "no recorded
   frame: the wait for updated_seq >= 1 timed out"` before the TERM. Red on a scratch copy with the break threshold
   `>= 10**9` (paste), green on the real threshold.
3. **F3 — the wording matches the pinned source at all five sites.** `frame_tee.py:422`, `:428`;
   `tests/test_s0_01_frame_tee.py:853`, `:1019`, `:1454`: replace "SIGKILLs the group after 5 s" with "SIGKILLs the group
   (`killpg`) and then waits up to 5 s for it to exit" (`acp.rs:422-444` + `:2328` at `1c8321cd`: the kill is immediate;
   the only production `from_secs(5)` is the post-kill wait).
4. **F4 — the doc-anchor pins MEANING.** Replace/extend `test_docstring_names_the_pinned_shutdown_signal` with the
   verifier's `test_docstring_pins_the_meaning_not_the_tokens` (asserts `killpg`, `SIGKILL cannot be handled`, `last
   RUNNING status` present; no `SIGTERM path … (covers it|bounds)` claim; the wrap-tolerant regex
   `SIGKILLs[\s#]+the[\s#]+group[\s#]+after[\s#]*5[\s#]*s` absent from the SOURCE, which also reads the comments and
   the three test docstrings). Mutants DOCSTRING-HYBRID and COMMENT-TERM must die — paste both red lines.
5. **F5 — the N4/D3 pin sees dataflow.** ADD the verifier's `test_write_status_reads_no_state_outside_the_lock` (no
   `state[...]`/`seq` Subscript outside `with lock:` inside `_write_status`) beside the existing pin (the existing
   `status_lock`/`os.replace` arm stays). Mutant MIRROR-SNAPSHOT must die.
6. **F11 — the pre-init pin quantifies over ALL `proc` assignments** before the install (`all(... is None ...)`, not
   `any`). Mutant MIRROR-PREINIT must die.
7. **F12 — the AF-AP-59 class pinned in the file:** `test_grandchild_cleanup_is_own_pid_scoped` (no
   `subprocess.run(["pgrep", "-f"` / `"pkill"` in the test source). Mutant CENSUS-WORLD must die.
8. **F8 — the three VALUE-form premise asserts (`test:513`, `:902`, `:1075`) become the FLAG form** (loop-only threshold
   mutation must go red — paste), the regression-class control (an agent that never emits the handshake) pasted too.
9. **F10 / F2 / F14 / F15 — report and small hygiene:** rule the seventh AP-screen hit (`test:2120`); the red-state table
   from a REAL full-suite run on the true parent `736bb94` with every row's own individual run (the verifier measured
   `8 failed, 88 passed`: `test_write_status_snapshot_and_rewrite_are_locked` is a deterministic RED on the parent, not a
   control; `test_sigterm_kills_agent_child` is red 5/5; the tripwire is green 5/5 in isolation); the header names the
   dispatch commit AND the landing commit; close the pipes inside the `finally` before the own-pid assertion (F15).
10. **F13 — identity before the kill:** before `os.kill(gc_pid, SIGKILL)` assert `/proc/<pid>/cmdline` contains
    `time.sleep` (treat a missing `/proc/<pid>` as already gone) — the mirror image of AF-AP-59.

## Mutants (scratchpad copies; `git status --porcelain` clean on both files after each; paste the table)
The verifier's 40 (its item-7 table) re-run on the final tree; every SURVIVED (real) row now KILLED by a NAMED test:
DOCSTRING-HYBRID, COMMENT-TERM, PIDFILE-ABSENT, CENSUS-WORLD, MIRROR-SNAPSHOT, MIRROR-PREINIT; PIN-LOCK-NAME stays an
accepted rename mirror (say so); DRAIN-ORDER equivalent; TRY-SHRINK2 killed (the verifier's implementation of the
mutant, not the lane's broken one). Plus NC-TRIPWIRE-LOOPONLY and the three value-site loop-only controls.

## Gates (paste verbatim)
`bash scripts/test_summary.sh tests/test_s0_01_frame_tee.py` twice idle · the red state on the true parent, full suite,
no `-x`, with every changed/new test run individually against the parent (label genuine-red / CONTROL + mutant) ·
pyflakes both files · `python3 scripts/lint_delta.py --base <PIN>` with every hit ruled REAL / FALSE POSITIVE by line ·
the cost probe at a stated load · the post-suite process census. PC leg: NOT run here (coordinator's). FILE IDENTITY
(sha256 + lines) at the end. Report shape: DONE table (finding · change · file:line by grep · red-before verbatim or
CONTROL+killer · green-after), MUTANT table, PROBE table, NOT_DONE, DISCREPANCIES, SELF-ATTACK.
