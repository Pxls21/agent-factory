# VERIFY-QM1-d — adversarial verification of the L1 matrix runner (QM1-d) as LANDED

**Authorization.** Defensive verification of the owner's own qwen-builder throughput matrix runner.
Every effect is a FAKE (fake `QWEN_HOME`/`QWEN_LANES_DIR`/proc/curl/systemctl); no live model, unit,
or GPU is touched. Attack the runner and its tests to prove they cannot pass a broken runner — never
to weaken them.

**Model rule — FULL VERDICT.** You run on the LOCAL Qwen verify route grading a lane built on the
CLOUD route (a DIFFERENT model), so the single-model rule does NOT apply: end with a MERGE-READY /
NOT-READY verdict plus ranked findings and a repro for each. Report everything; do not severity-filter.

**Ground (LANDED at the PIN `8c1dbe6`).** QM1-d (commit 7369632, then the pushed history) closed
VERIFY-QM1-c's TWO findings in the runner `harness-ports/bin/qwen_matrix.py` (M) and launcher
`harness-ports/bin/qwen-matrix.sh` (R), tests `harness-ports/tests/test_qwen_matrix.py` (T) and
`harness-ports/tests/test_qwen_matrix_sh.sh` (X). The launcher-owned `guard` is the sole lifecycle
seam; the QM1-c fixes (F1 reused-CELL_DIR refusal, F2 absent-unit restore, F3 log rotation, F4 argv
identity, F5 positive `requests`, F6 corpus scrub) remain in force — a regression in ANY of them is a
finding. The TWO QM1-d fixes as landed (attack PAST them, do not just re-cite):

- **QM1-d F1 (was BLOCKER) — completion-state trust boundary.** R mints a 64-hex `RUN_ID` before any
  lifecycle effect (R:65-66), passes it to M with the result inputs (R:163-167), and publishes
  `run-complete` (temp-file-plus-rename) ONLY inside `cleanup` after baseline restoration succeeds and
  only when `rc == 0` (R:129-134); the restore block sets `rc=8` on any restoration failure (R:101-128).
  INT/TERM route to explicit `exit 130` / `exit 143` (R:138-139) so cleanup never publishes at rc 0 on
  a signal. A load-generator failure writes `run-error` and fails rc 7 (R:168-169). M's `_load_cell`
  refuses `run-error` (M:425-426), requires a lowercase-sha256 `run_id` (M:427-428), reads
  `run-complete` and requires it to EQUAL `run_id` (M:430-434) before admission.
- **QM1-d F2 (was SHOULD-FIX, AF-AP-88) — unit byte identity.** R renders the unit to `unit-text`
  (R:74) and hashes THAT FILE into `unit-sha256` (R:75-76). At production M recomputes the unit-text
  sha and requires it to equal the sha file (M:560-562); at table admission `_load_cell` reads
  `unit-text` as BYTES and requires `sha256(unit_text) == unit_sha256` (M:441-448).

## Items (V1-V10; every claim gets an independent repro through a SCRATCH COPY; never git-restore/stash/checkout the tree)

1. **V1 attack the completion boundary at the reader (M).** A cell dir with a fully valid
   `result.json` but NO `run-complete` file → refused? (`run-complete` unreadable, M:430-432.) A
   `run-complete` whose content is a DIFFERENT valid 64-hex than `result.json`'s `run_id` → refused
   (M:433-434)? A `run-error` file present ALONGSIDE a valid `run-complete` → which wins (M:425-426 runs
   first — confirm error still refuses)? A `run_id` that is uppercase / 63-hex / empty → refused
   (M:427-428)? Prove each through a scratch cell dir fed to `python3 M table <dir>`.
2. **V2 attack the completion boundary at the producer (R).** Drive the FAKE launcher (X's harness) so
   that: (a) the load generator fails — is `run-error` written AND `run-complete` ABSENT (R:168, R:129)?
   (b) restoration fails after a good result — does `rc` become 8 so `run-complete` is NOT written
   (R:117-134)? (c) a TERM arrives during the matrix step — rc 143, restoration attempted, `run-complete`
   absent (R:139)? Attack the ORDERING: is there ANY path where `run-complete` is written before
   restoration completes, or where a non-zero `rc` still reaches the write at R:129? Consider the window
   between `trap cleanup EXIT` (R:137) and the INT/TERM traps (R:138-139), and a signal DURING cleanup.
3. **V3 completion record binds the RUN, not the CELL — transplant probe.** The completion record binds
   `run-complete`↔`run_id`↔`result.json.cell.run_id`, but nothing binds the cell `name` or the
   `summary` measurements to that run. Copy a genuinely-completed cell's `{result.json, run-complete,
   unit-text, unit-sha256}` into a new dir, edit only `result.json.cell.name` (leave argv/unit/run_id) —
   does the table admit it under the new name with the transplanted numbers? State whether this is in
   the matrix's threat model (the owner's own tool) or a real binding gap; rank accordingly.
4. **V4 unit-text integrity vs the INSTALLED unit.** M's recompute proves `unit-text` was not tampered,
   but nothing reads the ACTUALLY-INSTALLED unit (`$QWEN_MATRIX_UNIT_PATH` after `install`, R:144) back
   and compares it to `unit-text` (rendered separately by `qwen-server unit`, R:74). Construct a fake
   `qwen-server` whose `unit` output differs from what `install` writes — does any gate catch the
   divergence, or does the cell record a `unit-sha256` that does not describe the running unit? Rank
   (likely a declared limit, but state it).
5. **V5 baseline chain-of-custody.** `BASELINE_SHA` is captured per-cell from the LIVE unit at R:85-90,
   not from a pinned golden; restoration verifies the restored unit's sha equals THAT captured value
   (R:122-125). Force a cell whose restoration leaves a subtly-different-but-self-consistent unit and
   show whether the NEXT cell inherits the drift as its "baseline". A tampered
   `$QWEN_MATRIX_BASELINE_ENV` line — is it rejected by the `QWEN_[A-Z0-9_]*=` case (R:114) and does a
   line that passes the shape but changes the restored sha still fail at R:122-125?
6. **V6 the F2 recompute is byte-exact and mandatory.** `unit_sha256 = 'b'*64` against valid persisted
   bytes → refused (M:441-448)? A `unit-text` mutated by one trailing byte with the OLD sha → refused? A
   MISSING `unit-text` file with a valid `unit_sha256` → refused (M:444-446)? Confirm `read_bytes` (not
   `read_text`) so a trailing newline or non-UTF-8 byte cannot desync producer vs reader.
7. **V7 the two QM1-d scratch mutants are VALID (AF-AP-78) and the QM1-c six did not regress.** Remove
   the completion read/compare from M (F1 mutant) → it must COMPILE and its suite COLLECT, then the
   focused test kills it. Remove the unit-byte recompute from M (F2 mutant) → same. Paste each killer
   line and confirm no mutant "kills" through a SyntaxError. Spot-check that F1/F2 fixes did not weaken
   the QM1-c argv-identity (M:435-440) or positive-`requests` (M:478-479) gates.
8. **V8 negative-control discipline.** For each of V1-V6, name the exact assertion and show it RED when
   the guard is removed (scratch copy) and GREEN with the guard present. A gate that survives no mutant
   is a tautology — flag any you find.
9. **V9 identities + gates.** Recompute sha256 + line count of M/R/T/X and compare to the report's FINAL
   (M `9dc6521f…`/578, R `5c0fc7b1…`/187, T `3404d8f9…`/440, X `a7be1e90…`/231). Re-run:
   `python3 harness-ports/tests/test_qwen_matrix.py` (`4 tests passed`),
   `bash harness-ports/tests/test_qwen_matrix_sh.sh` (`16 passed, 0 failed`), and
   `PATH=/home/rocco/venv-agent-factory/bin:$PATH bash harness-ports/tests/run-all.sh`
   (ALL SUITES PASSED, the NORMAL environment, not a lane TMPDIR). Paste every count.
   `python3 -m py_compile M`, `pyflakes M`, `bash -n R`, `bash -n X`, `git diff --check` → rc 0 each.
10. **V10 report + VERDICT.** Rank findings BLOCKER/SHOULD-FIX/NIT with a one-line repro each; a
    NOT-DONE list; `scripts/report_lint.py` with `--map M=… --map R=… --map T=… --map X=…`; the four
    file identities; then a single MERGE-READY / NOT-READY verdict with its one-line reason.

## Gates (paste every line)

- The V9 identities, suite counts, and static checks above.
- Each V7 mutant's compile_rc / test_rc / killer line; each V8 negative control's red-then-green.
- `scripts/report_lint.py --min-refs 12 --map M=harness-ports/bin/qwen_matrix.py
  --map R=harness-ports/bin/qwen-matrix.sh --map T=harness-ports/tests/test_qwen_matrix.py
  --map X=harness-ports/tests/test_qwen_matrix_sh.sh` on the report.

**Boundary.** M, R, T, X (READ-ONLY — copy into `../scratch` for any hostile edit, never the tracked
files), and your report `tasks/briefs/qwen-matrix-support/VERIFY-QM1d-report.md`. Nothing else. The
class list AF-AP-78/79/80/83/84/85/86/87/88 is your preflight. Hermes's `terminal` caps ONE call at
420 s: `run-all.sh` is ~2 min (fits); the focused suites are seconds; one heavy call at a time. The
corpus at `~/qwen-builder/corpus/` is a coordinator input — read nothing there. CODE INTEL FIRST:
`graft ask` / `ripwire` on M and R before grep; attach the pack. The report lint's `fix:` hints apply
for at most three rounds, then paste and finish. NOT for you: no real matrix cell, live load, GPU
sample, unit change, commit, push, or tag. Retro: name any new class for the coordinator; bake nothing
yourself.
