# Lane B5f — S0-01 frame tee, round 11: deterministic pins for the races, the honest shutdown bound, the report's red state measured (sandbox Opus 4.6 `code-implementer`)

**PIN:** the HEAD this brief is committed in. **Verdict graded:** `tasks/briefs/s0-01-b5f-support/verify-B5e.md`
(VERIFY-B5e, round 10 on checkpoint 8n — NOT-READY: F-B5e-1..4 blocking; F-B5e-5..14 verified cheap fixes; read it
whole first — every killer it proposes was RUN by the verifier and its PIN/mutant result is pasted there).
**Scope (exactly two files + your report):** `proofs/S0-01/tools/frame_tee.py` and `tests/test_s0_01_frame_tee.py`;
report `tasks/briefs/s0-01-b5f-support/B5f-report.md`. Another lane holds uncommitted checker edits in this tree —
never `git stash/checkout/restore/reset/add/commit/push`; mutants on scratchpad COPIES only (the verifier's runner is
under the session scratchpad `mutb10.py` / `mutb10b.py` — reuse it); kill only processes you started; no outward
actions (no network, no PC). Test counts and red states are PASTED from real runs, never typed, never with `-x`.

## Design (pinned by the coordinator — build it, do not redesign it)
1. **F-B5e-1 — the honest shutdown bound.** buzz-acp at the pinned commit (`upstream.lock.yaml:16-19`, buzz
   `1c8321cd`, `crates/buzz-acp/src/acp.rs:421-444` + `:2323-2328`) ends a leg with `killpg(SIGKILL)` on the process
   group and a bounded 5 s wait; it never sends SIGTERM (0 occurrences; `docs/INCIDENT-LOG.md:36` records the same
   reading — it is why ruling A21d exists). Reword the tee module docstring (`:16-20`), the in-code comments
   (`:416-418`, `:422-424`) and the three test docstrings (`T:817-820`, `:978-982`, `:1375-1379`) to say exactly that:
   a client that never closes (c2a) or a grandchild holding the agent's stdout (a2c) keeps the tee alive; buzz-acp
   SIGKILLs the group after 5 s; SIGKILL cannot be handled, so that leg's evidence is its last RUNNING status (A21d);
   the SIGTERM path covers an operator/systemd TERM, not buzz-acp. Add the verifier's doc-anchor test
   (`test_docstring_names_the_pinned_shutdown_signal`: the module docstring contains `SIGKILL` and `acp.rs` and not
   `TERMs/KILLs`) — it is RED today; paste the red line.
2. **F-B5e-3 — N4/D3 deterministic.** Add `test_write_status_snapshot_and_rewrite_are_locked` exactly as the verifier
   wrote it (AST: `_write_status` takes `with lock:` containing the `seq` snapshot and `with status_lock:` containing
   `os.replace`). Keep the race test as a stress. Prove: PIN pass, N4 KILLED, D3 KILLED — deterministic (run each
   mutant 3×).
3. **F-B5e-2 — S1 deterministic.** Add `test_status_write_follows_timeline_write_in_pumps` exactly as the verifier
   wrote it (AST: inside each pump's `with lock:` the `tl.write` lineno < the `_write_status()` lineno), AND add the
   existing lag assertion `0 <= tl_last_seq - status["updated_seq"] <= 1` to `test_directional_trails_timeline_after_sigkill`'s
   per-trial block (12 samples). Prove S1 KILLED 3/3 by the AST pin.
4. **F-B5e-5 + F-B5e-6 — the F13 pin closes its two gaps.** In `test_no_statement_between_signal_and_try` add the
   verifier's two asserts: no `Popen` call precedes the handler install in `main()`'s body, and `proc = None` is
   assigned before the install. Prove INSTALL-LATE-B and NO-PREINIT KILLED (both survived the full suite before).
5. **F-B5e-7 + F-B5e-11 — success-only waits assert their premise.** `T:1566` gets the FLAG form (`loaded = False`
   above the loop, `loaded = True` on the break path, `assert loaded, "no contention: …"`) — the verifier proved the
   value form does NOT kill; `T:501`, `T:857`, `T:1021` get the VALUE form (`s = None` hoisted;
   `assert s is not None and s.get("recorded_a2c", 0) >= 1, "…"` before the SIGTERM). For each, prove red on a scratch
   copy with the wait threshold made unreachable (`>= 10**9`), then green on the real threshold — paste both lines.
6. **F-B5e-12 — fixture grandchildren die in `finally`.** Every fixture agent that spawns a grandchild (`T:468`, `T:990`,
   `T:2381-2387`) writes the grandchild pid to `<framedir>/grandchild.pid`; the test's `finally` kills it (SIGKILL,
   ignore ESRCH). A post-test census (`pgrep -f "import time; time.sleep"` filtered to your own agents) must be empty —
   add it as an assertion inside those tests' `finally`.
7. **F-B5e-13 + F-B5e-14 — small truths.** Move the two `state` reads in `_write_status` (`:174` `stdin_reader_done`,
   `:179` `write_errors`) inside the `with lock:` snapshot so a published status is one consistent instant; pre-bind
   `identity = None` in `test_sigterm_kills_agent_child` and assert with a reason.
8. **F-B5e-8 + F-B5e-9 — docstring truth.** The window test's docstring states the STRUCTURAL guarantee (the child
   cannot be visible to `pgrep -P` before the fork at `:209`, which follows the install at `:207`; measured 0/12 runs
   reach the 234 MB sha256 — the big file is load insurance, not the mechanism). `test_grandchild_straggler_recorded`'s
   docstring: kills a2c stall timeouts shorter than the 6 s gap (0, 5 s); the 30 s case is the structural pin's.
9. **F-B5e-4 + F-B5e-10 — the report.** RED STATE = `git show 736bb94:proofs/S0-01/tools/frame_tee.py` (the TRUE
   parent; `c227f8d` is B5c, two generations back) + your tests, NO `-x`, full suite: paste the summary line and every
   FAILED name; every new test labelled genuine-red or CONTROL + the mutant it kills. Popen census pasted from the
   AST tool (27 sites at the PIN). Every file:line on the FINAL tree.

## Mutants (scratchpad copies; `git status --porcelain` clean on both files after each; paste the table)
The verifier's 26 (its item-3 table) re-run on the final tree, plus its four verified killers' targets: every one
KILLED by a NAMED test — S1, N4, D3 deterministic (3/3 each), INSTALL-LATE, INSTALL-LATE-B, GAP-1, NO-PREINIT,
EXCEPT-WRONG, EXIT-0, STATUS-FINAL-TRUE, ERR-MISSING, ORPHAN, TRY-SHRINK2, A2-t0/t1/t5/t30, a2c-t0/t5/t30,
A2C-DELETE, A2C-WRONG-THREAD, N3, PUMP-TIMEOUT; DRAIN-ORDER stays equivalent (say why); plus new: LOCK-READS-OUT
(move the two state reads back outside the lock — name the killer or add one), DOCSTRING-TERM (revert the docstring
wording — killed by the doc-anchor test), GRANDCHILD-UNKILLED (drop a `finally` kill — killed by the census assert).

## Gates (paste verbatim)
`bash scripts/test_summary.sh tests/test_s0_01_frame_tee.py` twice idle · `python3 -m pyflakes` on both files ·
`python3 scripts/lint_delta.py --base origin/claude/soundbox-kit-migration-iz1jwf` (report each hit as REAL or FALSE
POSITIVE with the line) · the real tee under SIGTERM and clean exit through the checker (the tripwire test) still green
· the cost probe (15 reps, load stated) · post-suite process census empty. PC leg: NOT run here (coordinator's).
Report shape: DONE table (finding · change · file:line · red-before verbatim or CONTROL+killer · green-after), MUTANT
table, PROBE table, NOT_DONE, DISCREPANCIES, SELF-ATTACK.
