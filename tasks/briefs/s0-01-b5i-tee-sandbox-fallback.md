# Lane B5i — S0-01 frame tee, round 14: one sentence in the repo, joined to the source by EQUALITY; the census helper honest about which branch it takes; the hang class closed by a structural pin; the identity sampled at the right stage (SANDBOX fallback — Opus 4.6 `code-implementer`; the PC route refused the lane with HTTP 503 admission capacity)

PIN: 58741bb23b28ecd574b4f8472cd88dba658ceaad
(HEAD at dispatch = the commit carrying this brief; the two scope files are byte-identical to checkpoint 8v = 63b582c. Your work lands in the CHILD
commit — the report header says "PIN: `<sha>`; landing = the coordinator's checkpoint, made after this report".)

**Verdict graded:** `tasks/briefs/s0-01-b5i-support/verify-B5h.md` (VERIFY-B5h, round 13 on 8v — NOT-READY on F1/F2/F4/
F9; real F3/F5/F6/F7/F8/F10-F13; 1112 lines; every finding measured, with the exact red test — use its code verbatim).
F2 and F3a are CLOSED by the coordinator in the PIN itself: the AF-AP-59 registry row in `.claude/hooks/edit-snapshot.py`
now carries `pkill` and a non-adjacent `-f` — your test inherits it; you re-run its two mutants and paste the kills.
**Class sweep:** `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` rows #11 (AF-AP-55: the interpreter identity is sampled
right after `Popen`, 18/20 wrong-stage on a two-stage agent; `tools/acp_probe.py:296-320` has the late re-sample — port
it), #13 (`S0_01_AGENT=""` → uncaught `PermissionError`, rc 1, no status), #14 and #24 (DOCUMENTED-LIMIT / SAFE — no code
change; state why in the report), #15 (the SIGTERM window measured SAFE — no change).
**Scope (exactly two files + your report):** `proofs/S0-01/tools/frame_tee.py` · `tests/test_s0_01_frame_tee.py` · report
`tasks/briefs/s0-01-b5i-support/B5i-report.md` (write it in your worktree so it travels with the patch, AND return it
whole as your final message). `pins.py` and the vendored `proofs/S0-01/vendor/buzz-acp/acp.rs` are READ-ONLY (the
oracle is never edited; its sha256 `44e82861…` is the premise). You work in the SHARED sandbox tree /home/user/agent-factory (another lane holds uncommitted
edits to the checker files there — never `git stash/checkout/restore/reset/add/commit/push`; your two scope files are
declared in `.lanes-live`); run every gate from a `git archive <PIN>` copy under the session scratchpad
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/b5i/ + your two files; mutants on scratch copies
only; every pytest run with an explicit `--basetemp` under that scratch dir (the shared `/tmp/pytest-of-root` races);
kill only processes you started, by pid, never by name; NEVER background a run and stop — every gate is one foreground
call whose output you paste; no outward actions; no PC bridge. The interpreter is `/root/venv-agent-factory/bin/python`
(3.11; `/usr/bin/python3.12` and `/usr/bin/python3.13` exist for standalone pins, without pytest).

## Why this round exists (read once, then build)
Round 13 vendored the pinned source as the oracle — the right instrument — and then joined it to the prose by five
substring checks on a hand-written constant: a clause with the ORDER REVERSED at all six sites passes the whole suite
(FALSECONST-ORDER). The census helper's `range(6000)` "fix" cannot work: site 3's grandchild is a zombie at census by
construction (the test waits for a tee whose exit IS the grandchild's death). The F-B5g-9 deadlock reproduces
deterministically on the PIN's tee and the structural pin the design mandated was never written. Each of these was
reported CLOSED. This round closes the classes and reports only what a paste proves.

## Design (pinned by the coordinator — build it, do not redesign it)
1. **One sentence in the repo (VERIFY-B5h F1 + F5 + F12 + F13; the verifier's design option 1).** `PINNED_SHUTDOWN_CLAUSE`
   stays the ONLY prose statement of buzz-acp's shutdown bound. The other five sites (the two R1 comments at the drain
   loops, the three test docstrings) say `buzz-acp's shutdown bound: see PINNED_SHUTDOWN_CLAUSE in frame_tee.py` and
   nothing else about SIGTERM/SIGKILL/5 s. The oracle test then asserts, in this order: (a) the sha256 premise (as now);
   (b) the derived facts (as now: SIGTERM count 0, `killpg` + `Signal::SIGKILL`, `kill_line < wait_line`, the unique
   `from_secs(N)` before `mod tests`, `sd_start`, `kpg_start`); (c) **EQUALITY**: `expected = "buzz-acp SIGKILLs the
   group (killpg) first and then waits up to %d s for the child to exit" % secs` built FROM the derived facts (secs
   parsed from the `from_secs(N)` at `wait_line`; the order of the two halves chosen by `kill_line < wait_line`) and
   `assert PINNED_SHUTDOWN_CLAUSE == expected`; (d) the module docstring of `frame_tee.py` (`ast.get_docstring`) contains
   the constant's text verbatim (whitespace-normalised) — per-site presence, not a file-wide count; (e) every
   `acp.rs:NNN-MMM` citation in BOTH files equals the derived ranges (the verifier's loop, verbatim — `:422-444` and
   `:2323-2328` are asserted, not typed); (f) the negative guard `"SIGTERM" not in doc.split("The SIGTERM path")[0]`
   over the module docstring, and no test docstring contains `SIGTERM` or `SIGKILL` or `5 s` outside the reference
   sentence (the five sites are a LIST the test enumerates by name, not a count). Mutants FALSECONST-ORDER, SITECOUNT-DUP,
   SEVENTH-SITE, CITE-421, CITE-421-TEST, CITE-KPG-2324, DOCSTRING-ORDER, DOCSTRING-WRONGEVENT, DOCSTRING-HYBRID,
   CONST-ORDER, CONST-WRONGEVENT, COMMENT-TERM, TESTDOC-TERM must ALL die — paste each pytest tail with the assertion
   line; the verifier's UNION-DOCROT must die too. Rejected: keeping six copies with a count (F13) — a count cannot say
   which site is wrong.
2. **The census helper returns the branch it took (F4; F-B5g-8 stated honestly).** `_kill_own_grandchild(framedir)`
   returns `"live"` (identified as ours, killed) or `"gone"` (zombie / already reaped). Revert `range(6000)` to
   `range(3000)` at site 3 and fix its comment (F10). Each site asserts its branch: sites 1 and 2 `== "live"`, site 3
   `== "gone"` with the docstring stating WHY site 3 can never hold a live grandchild at census (the a2c-EOF argument,
   verbatim from the verdict). GRANDCHILD-UNKILLED-S3 then still survives — by construction, and the DONE row says so
   in those words; GRANDCHILD-UNKILLED at sites 1 and 2 must die (paste). Rejected: a second independent grandchild at
   site 3 (more machinery to prove a kill the two other sites already prove).
3. **The kill around the race, and the identity read fail-closed (F6).** `os.kill(gc_pid, SIGKILL)` inside `try/except
   ProcessLookupError` (raced us to exit = success); the `/proc/<pid>/cmdline` read catches `(FileNotFoundError,
   ProcessLookupError)` → `"gone"` and `PermissionError` → raise a named AssertionError ("cannot identify pid N — not
   killing"; fail-closed). Unit test the helper directly with a monkeypatched read for all four paths (the verdict's
   driver: live-foreign refuses, zombie = gone, ProcessLookupError = gone, PermissionError = named failure).
4. **The AST kill-site pin as a SUBTRACTION (F3b) and `_KILL_SITES` gone (F11).** Collect EVERY `os.kill` / `os.killpg`
   `Call` in the module (any scope: module level, class body, lambda, comprehension), map each to its enclosing
   `FunctionDef` or `None`, and fail on any whose enclosing function is not `_kill_own_grandchild`. Mutants
   KILL-MODULE-LEVEL and KILL-LAMBDA must die (paste); the four spelling evasions (`from os import kill as k`,
   `pthread_kill`, `subprocess kill`, `send_signal`) stay the DOCUMENTED limit — say so in the test's docstring.
   Re-run CENSUS-PKILL-DQ and CENSUS-PGREP-A against `test_grandchild_cleanup_is_own_pid_scoped` — both must die on the
   PIN's registry row (paste; they inherit the coordinator's fix — if either survives, STOP and report it as a
   discrepancy, do not patch the hook).
5. **The hang class closed by a structural pin (F9).** Add `test_no_unbounded_tee_pipe_reads` (the verdict's ~15 lines,
   verbatim): every `.read`/`.readline`/`.communicate` on a tee Popen's stdout/stderr must sit inside a bounded helper
   (`_drain` / `_read_with_deadline`) or carry a timeout. It is RED on the PIN (it flags `test:2607`, `:2209`, `:1785`,
   `:459`, `:515` — paste that red run first); then fix every flagged site through a bounded reader (a reader thread
   joined with a deadline, or the existing drainer), and at site 3 close `tee_proc.stdin` immediately after the last
   write/flush. Commit the verifier's hang probe as a TEST: an agent that consumes the handshake, closes its a2c side
   with nothing written and exits, while the test holds the tee's stdin and reads — RED on the PIN as a timeout (paste
   the `TimeoutExpired`/deadline failure with the wchan line if you can read it), GREEN after. Rejected: "the fix is
   structural" without a structure.
6. **The interpreter identity sampled at the first a2c byte (SWEEP-prod #11; AF-AP-55).** Port `tools/acp_probe.py`'s
   late re-sample: when the first a2c byte arrives, re-read `/proc/<pid>/exe` (+ its sha256) and overwrite
   `agent_interpreter_*` in `runtime-identity.json` — the tee's copy of the probe's mechanism, same field names. Test:
   a two-stage agent (a bash wrapper that `exec`s python) recorded as the python interpreter 20/20 (the sweep measured
   18/20 `bash` on the PIN — that is your red-before; paste it). Guard the readlink for the target exiting between spawn
   and read (AF-AP-55's own rule: a `try/except OSError` that records `"exited before identity"` rather than crashing).
7. **`S0_01_AGENT` validated like `S0_01_FRAMEDIR` (SWEEP-prod #13).** Empty → `frame_tee: S0_01_AGENT is empty`, rc 64,
   no traceback; a path that is not an executable regular file → rc 64 named; `Popen` `OSError` → rc 64 named. Tests for
   each with the rc and the stderr line asserted exactly (the PIN gives `PermissionError` + rc 1 — red-before, paste).
8. **Hygiene and the report (F7 / F8 / F10 / F14).** The stale `# grandchild streams a2c frames for 30 s` comment matches
   the code; one line atop `frame_tee.py`: `# imported by tests/test_s0_01_frame_tee.py — keep this module
   import-side-effect free`. Before returning: `python3 scripts/report_lint.py tasks/briefs/s0-01-b5i-support/B5i-report.md
   --map tee=proofs/S0-01/tools/frame_tee.py --map test=tests/test_s0_01_frame_tee.py` on the WORKTREE (your final bytes);
   paste the summary line; MISS 0, every NEAR fixed. Every `file:line` from `grep -n` on the FINAL bytes. Every mutant row
   carries the pytest tail it was killed by — the assertion LINE of the killer, from the run, never from memory (F7: the
   docstring mutant died at :3104, not the :3086 the report named). NOT_DONE lists what you did not run, with the reason.

9. **The 18-class self-sweep over YOUR test file(s) (the owner's mandate: classes, not instances).** Run the class list of
   `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` § "The classes" (presence-gated checks, reads outside the walk / no
   S_ISREG, stale `[-1]` over produced records, negative acceptance assertions, substring/tail anchors classifying outcomes,
   env-domain fail-opens, lossy decodes on a decision path, broad catches, waits/polls + ordinal gates in fakes (AF-AP-57),
   skips/xfails that cannot fire, world-scoped enumerations (AF-AP-59), signal installs before their try (AF-AP-58),
   `/proc/<pid>/exe` races (AF-AP-55), mirrors of the code under test, two counters over different populations asserted
   equal, provably redundant guards, hardlink-clobbering writes, anything else that is a family) over your test files by AST
   or grep, RUN every instance (a mutant or a planted input), and table them: `class | file:line | verdict (DEFECT / SAFE —
   guard named / DOCUMENTED-LIMIT / EQUIVALENT) | the run | fix | red test`. Fix every DEFECT row in THIS round. An Opus-5
   sweep lane is grading the same files in parallel; its table reaches the verifier — a class you missed and it found is a
   blocker, a class you both found is closed. An empty class is a result: say so.

## Mutants (scratchpad copies under your worktree's `$TMPDIR`; `git status --porcelain` clean on the scope files after each)
The thirteen of item 1 · GRANDCHILD-UNKILLED ×3 (S3 survives by construction — say so) · ZOMBIE-OLDSEMANTIC ·
PROCESSLOOKUP-UNGUARDED (revert item 3 → the unit test's reaped-pid path raises) · KILL-MODULE-LEVEL · KILL-LAMBDA ·
CENSUS-PKILL-DQ · CENSUS-PGREP-A · CENSUS-WORLD · CENSUS-PGREP-X · PIPEREAD-UNBOUNDED (revert one bounded reader →
the structural pin goes red) · HANG-REINTRODUCED (re-open stdin at site 3 → the hang probe times out) ·
IDENTITY-EARLY-ONLY (drop the re-sample → the two-stage test records bash) · AGENT-EMPTY-UNGUARDED · PIDFILE-ABSENT ×3
(unchanged killers, re-measured). ≥ 30 rows, `ran` = executed, `failed` = the true count, killer line pasted.

## Gates (paste verbatim; one foreground call each; `--basetemp` always)
`bash scripts/test_summary.sh tests/test_s0_01_frame_tee.py` twice from the `git archive <PIN>` copy + your two files (both summary lines, pasted) · `pyflakes` on both files · `python3 scripts/lint_delta.py
--base <PIN>` · `report_lint.py` and `ap_screen.py --tests tests/test_s0_01_frame_tee.py` (every hit classified by
running it; the AF-AP-59 row must produce ZERO hits on the test file — your own pin test reads the row and asserts the
same) · the standalone pins on 3.11 / 3.12 / 3.13 · the cost probe of VERIFY-B5h item 6 (15 reps × 3 batches, PIN vs your tee,
load stated) · the process census after your runs (`/proc/<pid>/cmdline` per live python; zero orphaned `time.sleep`
grandchildren). NOT run here: the PC `-n 8` gate of record (coordinator's). Report shape: FILE
IDENTITY (FINAL bytes, sha256 + lines, two files), DONE table (item → file:line → the red-before line → the green line),
MUTANT table, PROBE tables, NOT_DONE, DISCREPANCIES, SELF-ATTACK.
