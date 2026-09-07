# Lane B5h — S0-01 frame tee, round 13: the pinned source as the ORACLE for the prose, an own-pid census that cannot hang or misfire, a report that pastes (sandbox Opus 4.6 `code-implementer`)

**PIN:** the HEAD this brief is committed in (your work lands in the CHILD commit — the report header says "Dispatched at
`<PIN sha>`; landing = the coordinator's checkpoint, made after this report" — B5f and B5g both named a commit that does
not contain the work; that is F14, twice).
**Verdict graded:** `tasks/briefs/s0-01-b5h-support/verify-B5g.md` (VERIFY-B5g, round 12 on checkpoint 8s — NOT-READY on
F-B5g-2/5/6/7/9; F-B5g-1/3/4/8/10/11/12 real; 1163 lines; every finding measured — use its code and its mutants verbatim;
its runners are under the session scratchpad `vb12mut.py`, `vb12muts.py`, `vb12muts2.py`, `vb12zombie.py`, `vb12gc3.py`,
`vb12py.py`, `vb12win.py`, venues `vb12pristine`/`vb12red`/`vb12mut`/`vb12cA`/`vb12cB`/`vb12inst` — reuse them).
**Scope (exactly two files + your report):** `proofs/S0-01/tools/frame_tee.py` and `tests/test_s0_01_frame_tee.py`;
report `tasks/briefs/s0-01-b5h-support/B5h-report.md`. READ-ONLY: the vendored oracle
`proofs/S0-01/vendor/buzz-acp/acp.rs` (5030 lines, sha256 `44e82861763694d2b82d02b15ee100ffd6c78874a2b2282865e6656c539c38f1`
= `crates/buzz-acp/src/acp.rs` at the pinned buzz commit `1c8321cd`, fetched from the owner's pinned clone and equal to the
round-11 verifier's independent GitHub fetch; provenance beside it in `VENDORED-FROM.md`), `.claude/hooks/edit-snapshot.py`
(import it, never edit it), `proofs/S0-01/pins.py`, everything else. Never `git stash/checkout/restore/reset/add/commit/
push`; mutants on scratchpad COPIES only; kill only processes you started, PID-targeted (never `pkill -f`); NEVER
background a run and stop — a stopped lane is never rewoken, and B5g's backgrounded mutant run is the wedged pair of
F-B5g-9 (two processes deadlocked for three hours until the coordinator killed them); no outward actions.

## Design (pinned by the coordinator — build it, do not redesign it)
1. **F-B5g-1 — the prose is checked against the SOURCE, not against a word list.** Add
   `test_shutdown_prose_matches_the_pinned_source`: read the vendored `acp.rs`, assert its sha256 equals the constant
   above (the test's own premise), then assert the MECHANICAL facts the docstrings rest on — `"SIGTERM"` occurs 0 times;
   `fn kill_process_group` contains `killpg(` with `Signal::SIGKILL`; inside `pub async fn shutdown` the kill
   (`kill_process_group(` / `start_kill(`) PRECEDES the bounded wait (`from_secs(5)` + `self.child.wait()`), and that
   `from_secs(5)` is the only one before the `#[cfg(test)] mod tests` that opens at :2351 (there is an earlier
   `#[cfg(test)]` at :940 — resolve the module boundary from the source, not by the first hit); then DERIVE the line
   ranges (`shutdown` = :422-444, `kill_process_group` = :2323-2328 on this file — compute them, do not type them) and
   assert every docstring/comment citation in BOTH scope files cites exactly those ranges (this fixes F-B5g-11's
   `:421` by construction). Keep the existing token test but make it a SUBSET of this one (or fold it in). Mutants
   DOCSTRING-ORDER and DOCSTRING-WRONGEVENT (the verifier's texts, verbatim) must now die — through an assertion that
   the docstring's own ordering sentence agrees with the source ("kill first, then the bounded wait"): pin the docstring
   to state the order in a fixed clause that the test compares to the derived order, e.g. the constant
   `PINNED_SHUTDOWN_CLAUSE = "buzz-acp SIGKILLs the group (killpg) first and then waits up to 5 s for the child to exit"`
   defined ONCE in `frame_tee.py`, cited verbatim at all six sites (the module docstring, the two comments, the three
   test docstrings) — the test asserts each site contains the constant and the constant agrees with the derived facts.
   A false ORDER then requires changing the constant, which the source assertion rejects.
2. **F-B5g-2 / F-B5g-10 / F-B5g-11 — every artifact agrees with the source.** `tests/test_s0_01_frame_tee.py:1517`
   `# R1: SIGTERM it (buzz-acp's shutdown responsibility).` → `# R1: SIGTERM it (an operator/systemd TERM; buzz-acp
   SIGKILLs the group instead).`; extend the wording pin over `Path(__file__)` too (the verifier's regex
   `buzz-acp'?s?[\s#]+shutdown[\s#]+responsibility` RED today at :1517; TESTDOC-TERM must die), and fix the F4 test's
   docstring scope claim (`:2911-2912`); "waits up to 5 s for it to exit" → "for the child to exit" at all sites (the
   source waits on `self.child.wait()`, the direct child).
3. **F-B5g-7 — F15 as the CASE, not the letter:** the pipe closes in an INNER `try/finally` around the whole census
   (the verifier's shape) so they run after ANY assertion; prove it under PIDFILE-ABSENT by listing
   `/proc/<pytest-pid>/fd` for the tee's pipe inodes before/after (paste).
4. **F-B5g-9 — a census that cannot hang.** Root-cause the deadlock from the verifier's evidence (the test held the
   tee's stdin write end while blocking on a pipe read; the tee's c2a reader blocked on that stdin; the a2c side at
   EOF): find every blocking read of `tee_proc.stdout`/`stderr` in the file and give each a deadline (a reader thread
   joined with a timeout, or `select` with a timeout) and close `tee_proc.stdin` BEFORE any wait on the tee's exit or
   output where the test no longer writes; add a structural pin: no `.stdout.read`/`.stderr.read`/`.readline(` on a
   tee `Popen` outside a bounded reader helper. Try to REPRODUCE the hang (>= 20 runs of the three grandchild tests
   with an agent that closes its a2c early while the test still holds stdin — the verifier's mechanism); paste the
   attempts; if unreproduced, the fix still lands on the fd-table evidence (primary source), say so. The report's
   process census must be OWN-VENUE-scoped: `ps -eo pid,ppid,etimes,args` filtered to your scratchpad venue paths
   plus your pytest's descendants — pasted, not asserted.
5. **F-B5g-4 — F13's semantic corrected:** a cmdline mismatch on a ZOMBIE (`/proc/<pid>/stat` state `Z`) = already
   gone; a cmdline mismatch on a LIVE process = hard failure "refusing to kill a foreign pid" (the verifier's code,
   verbatim, at all three sites); the red test: a fourth fixture whose grandchild exits ~0.3 s before the census —
   RED on the PIN today (`pid N is not the grandchild (cmdline: )`), GREEN after. Say in the docstring that pid reuse
   is unreachable here (pid_max 32768, ~5 pids/s measured vs the ~728/s needed) and that the zombie window (~0.97 s)
   is the reachable direction.
6. **F-B5g-3 — the AF-AP-59 class pinned by the registry's own signature, and ownership by construction.** Replace
   the two hand-typed literals with the verifier's `AP_SCREEN` import (`.claude/hooks/edit-snapshot.py`, the AF-AP-59
   row) asserted over `Path(__file__).read_text()`; then ONE `_kill_own_grandchild(framedir)` helper (pid file →
   identity per item 5 → kill) used at all three sites, plus an AST pin: every `os.kill`/`os.killpg` call in the file
   sits inside `_kill_own_grandchild` or inside a function named in an explicit `_KILL_SITES` allow-list (enumerate
   the current sites — the SIGTERM tests kill their own tee — and list them). Mutants: CENSUS-WORLD, CENSUS-PGREP-TIGHT,
   CENSUS-PGREP-A, CENSUS-PS-E (the verifier's spellings) die on the AP_SCREEN pin; CENSUS-PGREP-X and CENSUS-PROC-WALK
   die on the AST pin (an `os.kill` outside the allow-list) — state which pin kills which; a census that only
   ENUMERATES the world without killing is out of the AST pin's reach — say so as the documented limit.
7. **F-B5g-8 — site 3's kill path is exercised:** lengthen site 3's grandchild past the 45 s deadline (`range(6000)`)
   or assert in the DONE table that site 3 contributes the pid-file assertion only; GRANDCHILD-UNKILLED graded on site 3
   alone must die (paste).
8. **F-B5g-5 / F-B5g-6 / F-B5g-12 — the report pastes.** The AP-screen block is the TOOL's output over your delta
   (`python3 scripts/lint_delta.py --base <PIN>` from a static copy that carries only your two files — the tool prints
   no line numbers, so a per-line list is by definition typed); every killer line is the pytest tail; the header names
   the PIN and says "landing = the coordinator's checkpoint"; the F3 red-before is COMMENT-TERM (`:2928`), not the F4
   test.

## Mutants (scratchpad copies; `git status --porcelain` clean on both files after each; `ran > 0`; paste the table)
The verifier's item-2 table (48 rows) is MEASURED at the PIN — re-run only the rows your delta can move (the docstring
tests, the census sites, the pipe closes, the F13 sites; ~18 rows) plus: DOCSTRING-ORDER, DOCSTRING-WRONGEVENT,
TESTDOC-TERM, the six CENSUS-* spellings, MIRROR-STALE (say which value assertions kill it — the pin is not the guard),
GRANDCHILD-UNKILLED-S3, PIDFILE-ABSENT ×3 with the fd listing, the zombie red test's negative (a live foreign pid →
the hard failure), ORACLE-SHA-MISMATCH (a byte changed in a scratch copy of the vendored file → the oracle test's
premise assertion fires first, never a silent pass). Every row: mutated line, killer that fired, `ran`.

## Gates (paste verbatim)
`bash scripts/test_summary.sh tests/test_s0_01_frame_tee.py` twice idle from a static copy of the PIN + your two files ·
the red state on the TRUE parent tee 736bb94, full suite, no `-x`, every changed/new test run individually (genuine-red /
CONTROL + mutant) · pyflakes · `python3 scripts/lint_delta.py --base <PIN>` (the tool's output, pasted) · the cost probe
15 reps back-to-back with the parent at a stated load · the own-venue process census before and after · the tripwire
through the PIN's checker · 3.12/3.13 standalone pins. PC leg: NOT run here (coordinator's). Report shape: FILE
IDENTITY (FINAL bytes), DONE table (finding · change · file:line by grep · red-before verbatim or CONTROL + killer ·
green-after), MUTANT table, PROBE table, NOT_DONE, DISCREPANCIES, SELF-ATTACK.
