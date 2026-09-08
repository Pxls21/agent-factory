# Lane N5h — S0-01 ACP probe, round 11: the sweep's six production rows and the ordinal-gate test row closed as CLASSES (sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; `proofs/S0-01/tools/acp_probe.py` is byte-identical to the MERGE-READY
blob `b9eb56dd…` of VERIFY-N5g-b there. Your work lands in the CHILD commit; the report header says "PIN: `<sha>`".)

**Why:** VERIFY-N5g-b graded the probe MERGE-READY on its contract; the whole-tree class sweeps then found six production rows in
it and one test-file row. They are classes the S0-01 verdicts named elsewhere, found here because nobody swept the probe. One
round closes them; the verifier grades against the sweeps' runs.
**Inputs (read in this order):** `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` rows #7, #10, #23, #34, #39, #40 (each row = the
run that proves the defect, the minimal fix, the exact red test — use them verbatim) · `tasks/briefs/s0-01-sweep-support/SWEEP-tests.md`
rows 4.1 / 9.3 (the AF-AP-57 ordinal gate at tests/test_s0_01_acp_probe.py:~1681 with no positive control) and 13.1 (SAFE — confirm)
· `tasks/briefs/s0-01-sweep-support/pack-probe-pctools.md` (graft skeleton + the registry screen for the probe) · `docs/INCIDENT-LOG.md`
(AF-AP-30, AF-AP-40, AF-AP-55, AF-AP-57) · the probe's MERGE-READY verdict `tasks/briefs/s0-01-n5g-support/` (do not regress it).
**Scope (exactly two files + your report):** `proofs/S0-01/tools/acp_probe.py` · `tests/test_s0_01_acp_probe.py` · report
`tasks/briefs/s0-01-n5h-support/N5h-report.md`. Everything else READ-ONLY. The shared tree holds other lanes' uncommitted edits —
never `git stash/checkout/restore/reset/add/commit/push`; gates from a `git archive <PIN>` copy under the session scratchpad
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/n5h/ + your two files; mutants on scratch copies only;
every pytest run with an explicit `--basetemp` under that dir; kill only processes you started, by pid; NEVER background a run and
stop; no outward actions; no PC bridge. Interpreter `/root/venv-agent-factory/bin/python` (3.11).

## Design (pinned — build it, do not redesign it)
1. **#7 — the fixture read cannot hang (the AF-AP-30 class, probe side).** Before `open(fixture_path)` (:~156-159): `st =
   os.stat(...)`; `not stat.S_ISREG(st.st_mode)` → `SystemExit(64)` with a named message (`acp_probe: fixture is not a regular
   file: <path>`). Red-before: a FIFO at the fixture path hangs the probe (the sweep's run: rc 124 at 20 s); after: rc 64 in < 5 s.
   Then the CLASS: every other path the probe reads (grep `open(`, `read_text`, `json.load`, `readlink` receivers) gets the same
   rule or a one-line reason why it cannot be non-regular; list them in the report.
2. **#10 — the stderr drain failure is recorded, not swallowed.** `_drain_stderr`'s `except Exception: pass` records
   `f"{type(exc).__name__}: {exc}"` into a slot the main path folds into `probe_error` (and `runtime-identity.json`). Red-before: a
   directory at `agent-stderr.txt` → rc 0 and no `probe_error` (the sweep's run); after: `probe_error` names it. Then the CLASS:
   every broad `except` in the probe (the pack's AP-24 hits at :63 and :395) classified — fail-loud with the reason recorded, or
   a one-line proof the swallowed error is already recorded upstream (the sweep's #44 reasoning for `:395`).
3. **#23 — a lossy decode keeps the lossless copy.** At `:331` / `:360`: when `decode("utf-8", errors="replace")` replaced anything
   (compare against `errors="strict"` in a try), the timeline entry ALSO carries `raw_b64` (the probe already has the branch for
   non-JSON lines — use it). Red-before: an agent emitting `…"message":"Invalid par\xffams"` → `raw_b64` absent (the sweep's run);
   after: present and decodes to the exact bytes. Negative control: a clean UTF-8 line carries no `raw_b64`.
4. **#34 — the mirror constant pinned.** `_REDACTED_ENV_KEY_RE` (:34) equals `pins.REDACTED_ENV_KEY_RE` by a test that imports both
   (the probe stays import-free of `pins` on the PC — the TEST does the equality). Mutant: change one alternative in the probe's
   copy → the test goes red.
5. **#39 — the timeout domain closed.** `ACP_PROBE_TIMEOUT` accepts only `re.fullmatch(r"[0-9]+(\.[0-9]+)?", raw)` before
   `float()`: `"3_0"`, `" 30 "`, `"30s"`, `"nan"`, `"inf"`, `"0x10"`, `"-5"`, `"0"` → rc 64 named (parametrised test; the two
   leniencies the sweep found — `" 30 "` and `"3_0"` — are the red-before).
6. **#40 — the runtime state, not a string mirror.** `python_dont_write_bytecode` recorded from `sys.dont_write_bytecode`
   (both sites :113 / :434). Red-before: `PYTHONDONTWRITEBYTECODE=2` records `false` while bytecode writing is off (the sweep's
   measurement); after: `true`. Test both values and the unset case.
7. **SWEEP-tests 4.1 / 9.3 — the ordinal gate gets a positive control (AF-AP-57).** In `test_probe_late_sample_clears_early_interpreter_error`
   the fake gates on the ARGUMENT (`path == interp_path and not fired[0]`), records that it fired (a sentinel file), and the test
   asserts the sentinel BEFORE asserting `"probe_error" not in rid`. Red-before: the sweep's R10a (the gate at `== 99` → the test
   still passes); after: R10a fails on the missing sentinel. Then the CLASS over the test file: every fake selecting behaviour by
   call count (grep `calls[0]`, `_call[0]`, `count ==`) → argument/state gating; list them.
8. **13.1 — confirm SAFE** (the readlink of the test's own pid) in one line.
9. **Report discipline.** `python3 scripts/report_lint.py tasks/briefs/s0-01-n5h-support/N5h-report.md --map probe=proofs/S0-01/tools/acp_probe.py
   --map test=tests/test_s0_01_acp_probe.py` — MISS 0, every NEAR fixed, the heuristic rows named in one line; `python3
   scripts/ap_screen.py proofs/S0-01/tools/acp_probe.py` and `--tests tests/test_s0_01_acp_probe.py` — AF-AP-57 must be ZERO
   hits after item 7 (it fires on the PIN at :1681); every other hit classified by running it. Every file:line by `grep -n` on the
   FINAL bytes. Counts pasted from the run.

## Mutants (scratch copies; `git status --porcelain` clean on the scope files after each; `ran` = executed; killer line pasted)
FIXTURE-FIFO-UNGUARDED · DRAIN-SWALLOW (revert item 2) · LOSSY-NO-RAW (revert item 3) · MIRROR-DRIFT (one alternative changed) ·
TIMEOUT-LENIENT (revert item 5) · BYTECODE-STRING (revert item 6) · ORDINAL-99 (the sweep's R10a) · plus the MERGE-READY verdict's
DL-INLINE (the phase-gated killer must still die). ≥ 10 rows.

## Gates (paste verbatim; one foreground call each)
`bash scripts/test_summary.sh tests/test_s0_01_acp_probe.py` twice from the archive copy + your two files (both summary lines)
· `pyflakes` on both files · `python3 scripts/lint_delta.py --base <PIN>` · report_lint + ap_screen (item 9) · the process census
after your runs (`/proc/<pid>/cmdline` per live python; every agent/probe you started gone). NOT run here: the PC `-n 8` gate
(coordinator's). Report shape: FILE IDENTITY (FINAL bytes, sha256 + lines), DONE (item → file:line → red-before line → green
line), MUTANT table, NOT_DONE, DISCREPANCIES, SELF-ATTACK.
