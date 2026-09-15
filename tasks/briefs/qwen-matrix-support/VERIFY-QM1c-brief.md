# VERIFY-QM1-c — adversarial verification of the L1 matrix runner (QM1-c) as LANDED

**Authorization.** Defensive verification of the owner's own qwen-builder throughput matrix runner.
Every effect is a FAKE (fake `QWEN_HOME`/`QWEN_LANES_DIR`/proc/curl/systemctl); no live model, unit,
or GPU is touched. Attack the runner and its tests to prove they cannot pass a broken runner — never
to weaken them.

**Single-model rule.** You run on the cloud verify route grading a cloud-built lane. Report FINDINGS
only, ranked, with a repro for each. NO merge verdict. Report everything; do not severity-filter.

**Ground (LANDED at the PIN `c728be5`).** QM1-c closed VERIFY-QM1's six findings in the runner
`harness-ports/bin/qwen_matrix.py` (M) and launcher `harness-ports/bin/qwen-matrix.sh` (R), with
tests `harness-ports/tests/test_qwen_matrix.py` (T) and `harness-ports/tests/test_qwen_matrix_sh.sh`
(X). The launcher-owned `guard` (R, rc 7 on a live LOCAL lane) is the sole lifecycle seam. The six
fixes as landed (attack past them, do not just re-cite):
- **F1** a reused `CELL_DIR` is REFUSED with rc 3 before any write or lifecycle effect (R:55-63; the
  table reader rejects a `result.json` whose run did not complete, M:386-394/471-476).
- **F2** an initially-absent unit is restored to ABSENT through the launcher's `uninstall` and
  absence VERIFIED (rc 8 on failure) (R:80-114).
- **F3** log rotation refused on a size+device+inode change before reading from the old offset
  (M:257-277).
- **F4** `_load_cell` requires `argv_text`, a lowercase argv SHA-256 that MATCHES `argv_text`, and a
  lowercase unit SHA (M:386-432).
- **F5** `render_table` requires an integer positive `summary.requests` per cell (M:397-432).
- **F6** `build_corpus` scrubs the parsed messages through the SAME `scripts/transcript_export.py`
  `SECRET_PATTERNS` immediately before persist (M:100-175).

## Items (V1-V9; every claim gets an independent repro through a scratch copy; never git-restore the tree)

1. **V1 attack F1.** Can a stale `result.json` survive a failed rerun into the same `CELL_DIR`?
   Reproduce QM1-c's `V1_RERUN` target: cell A succeeds; a rerun fails (guard rc 7 or a forced load
   failure). Does the table READER accept the prior result, or reject it? Try a run-specific dir with
   a leftover `result.json` from an aborted run; a `result.json` present but its run marker absent.
   Confirm the refusal is BEFORE any lifecycle effect (no `install` call on the rerun).
2. **V2 attack F2.** Force an initially-absent-unit install to FAIL. Is the runner-created unit
   removed and its absence VERIFIED, or does a fake `uninstall` that leaves the unit behind still
   report success? Reproduce `V2_ABSENT_BASELINE`. Also: an initially-PRESENT unit restored to its
   exact prior bytes (the existing path) — does a byte change slip?
3. **V3 attack F3.** A rotation that replaces the log with a NEW file at least as long as the old
   offset, carrying a new `forcing full prompt re-processing` line — does the counter SEE it or
   REFUSE, or read the new file from the old offset (the bug)? Try same-inode truncation; a device
   change with the same inode number; a rotation shorter than the offset.
4. **V4 attack F4.** A record with a canonical-looking but MISMATCHED argv SHA (a valid lowercase
   64-hex that is not `sha256(argv_text)`); a uppercase or truncated unit SHA; an absent `argv_text`
   with a present SHA. Does `_load_cell` refuse each, or render the bogus cell?
5. **V5 attack F5.** `summary.requests` as `True` (a bool, an int subclass), `0`, `-1`, `1.0`, `"1"`,
   absent — does `render_table` refuse each before any performance decision, or judge a cell on a
   non-positive count?
6. **V6 attack F6.** An export carrying `Bearer …`, an `api-key: …`, and an `sk-…` token through the
   REAL `build_corpus` path — is each redacted (or the corpus refused) before it reaches a prompt
   file? Try a secret shape the exporter's `SECRET_PATTERNS` might miss (a bare 40-hex token, a
   `password=` field) — state which are caught and which are declared out of scope. Confirm the scrub
   runs on the PARSED messages, not only the raw file.
7. **V7 the mutants are valid (AF-AP-78).** Each of QM1-c's six scratch mutants compiles/parses and
   its suite collects before running; no mutant "kills" through a SyntaxError. Re-run the six with
   the matching negative control; paste each killer line.
8. **V8 identities + gates.** Recompute sha256 + line count of M/R/T/X against the report's After
   values. Re-run the suites: `python3 harness-ports/tests/test_qwen_matrix.py` (`4 tests passed`),
   `bash harness-ports/tests/test_qwen_matrix_sh.sh` (`13 passed, 0 failed`), and
   `PATH=/home/rocco/venv-agent-factory/bin:$PATH bash harness-ports/tests/run-all.sh`
   (ALL SUITES PASSED, run with the NORMAL environment). Paste every count. `python3 -m py_compile M`,
   `pyflakes M`, `bash -n R`, `bash -n X`, `git diff --check` → rc 0.
9. **V9 report.** Rank findings BLOCKER/SHOULD-FIX/NIT with a one-line repro each; a NOT-DONE list;
   `scripts/report_lint.py` with `--map M=… --map R=… --map T=… --map X=…`; end with the four file
   identities. No verdict (single-model rule).

**Boundary.** M, R, T, X (READ-ONLY — copy into `../scratch` for any hostile edit, never the tracked
files), your report `tasks/briefs/qwen-matrix-support/VERIFY-QM1c-report.md`. The class list
AF-AP-78/79/80/83/84/85/86/87 is your preflight. CODE INTEL FIRST: `graft ask` / `ripwire` on M and R
before grep. Retro: name any new class for the coordinator; bake nothing yourself.
