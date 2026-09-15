# QM1-d — close VERIFY-QM1-c's two findings (matrix runner)

**Authorization.** Defensive tooling on the owner's own qwen-builder throughput matrix. Every effect
is a FAKE (fake QWEN_HOME/QWEN_LANES_DIR/proc/curl/systemctl); no live model, unit, or GPU is
touched. The real matrix runs later, on the PC, after this lands and is verified.

**Ground.** QM1-c landed the L1 matrix runner (`harness-ports/bin/qwen_matrix.py` = M,
`harness-ports/bin/qwen-matrix.sh` = R, tests T=`harness-ports/tests/test_qwen_matrix.py`,
X=`harness-ports/tests/test_qwen_matrix_sh.sh`). VERIFY-QM1-c
(`tasks/briefs/qwen-matrix-support/VERIFY-QM1c-report.md`) returned TWO findings; controls V2-V6 held
and the six mutants killed. Fix both before any real matrix cell. PIN: c728be5. The launcher-owned
`guard` (R, rc 7 on a live LOCAL lane) stays the sole lifecycle seam. READ the VERIFY-QM1-c report
whole first; its repros are your acceptance targets.

## Items (in order; each = code + a deterministic LLM-free test + its negative control)

1. **F1 [BLOCKER] the table reader has no completion-state trust boundary (M:409-414, R:60/151-170).**
   `_load_cell` accepts a cell from `result.json` + identity + summary without requiring a completed
   launcher run; a fully-valid `result.json` from a FAILED/aborted run (no run marker, or a
   `run-error`) renders an A row with `TABLE_RC 0` (repro: `MARKER_EXISTS False` → a rendered row).
   FIX: the launcher writes an IMMUTABLE per-run completion record (e.g. `run-complete` with the
   run id) ONLY AFTER result post-processing AND successful baseline restoration; bind that record
   (its id/hash) into the cell record; `_load_cell` REQUIRES the matching completion record and
   REJECTS an `error`/unfinished/absent state before the cell can enter the table. TEST: a cell with
   a valid `result.json` but no completion record is REFUSED by the table; a `run-error` state is
   REFUSED; a genuinely completed cell renders. Build the failed-after-result fixture through
   `qwen-matrix.sh` (a real launcher path that writes the result then fails restoration), not only
   the existing-directory refusal. Negative control: the completion-record requirement removed →
   the incomplete cell renders (red).

2. **F2 [SHOULD-FIX, AF-AP-88] unit identity is checked as format, not recomputed from bytes
   (M:417-427).** `unit_sha256` is validated only as lowercase 64-hex; unlike `argv_sha256` (M:424,
   recomputed via `hashlib.sha256`) it is never recomputed from a persisted unit-text, so
   `unit_sha256 = 'b'*64` loads as the claimed identity. FIX: persist the EXACT rendered unit text
   beside the cell result (the launcher writes `unit-text` alongside `unit-sha256` at R:69-72);
   `_load_cell` recomputes `sha256(unit_text)` and REQUIRES it to equal the persisted `unit_sha256`.
   TEST: a cell whose `unit_sha256` is a canonical lowercase 64-hex that does NOT match the persisted
   unit text is REFUSED (reproduce `ARBITRARY_LOWERCASE_UNIT_SHA_ACCEPTED` going to a refusal).
   Negative control: the recompute-and-compare removed → the mismatched digest loads (red).

## Gates (paste every line)

- `python3 -m py_compile M`, `pyflakes M`, `bash -n R`, `bash -n X`, `git diff --check` → rc 0 each.
- `python3 harness-ports/tests/test_qwen_matrix.py` and `bash harness-ports/tests/test_qwen_matrix_sh.sh`
  twice each → paste the exact `N tests passed` / `N passed, 0 failed` (both counts will rise with the
  new tests).
- `PATH=/home/rocco/venv-agent-factory/bin:$PATH bash harness-ports/tests/run-all.sh` → ALL SUITES
  PASSED (the NORMAL environment, not a lane TMPDIR).
- Two scratch mutants (one per fix), each compiling/parsing before its test (AF-AP-78), each killed by
  the matching negative control; paste each killer line.
- FILE IDENTITY: sha256 + line count of M, R, T, X before → after.
- `scripts/report_lint.py` with `--map M=… --map R=… --map T=… --map X=…`.

**Boundary.** M, R, T, X, and your report `tasks/briefs/qwen-matrix-support/QM1d-report.md`. Nothing
else. The class list AF-AP-78/79/80/83/84/85/86/87/88 is your preflight. CODE INTEL FIRST: `graft ask`
/ `ripwire` on M and R before editing; attach the pack. The report lint's `fix:` hints apply for at
most three rounds, then paste and finish. NOT for you: no real matrix cell, live load, GPU sampling,
unit change, commit, push, or tag. Retro: name any new class for the coordinator; bake nothing yourself.
