# VERIFY-QM1 — adversarial verification of the L1 concurrency-matrix runner as LANDED (lane QM1-b, in the PIN): `harness-ports/bin/qwen_matrix.py` (M) + `harness-ports/bin/qwen-matrix.sh` (R) + their tests (T = `harness-ports/tests/test_qwen_matrix.py`, X = `harness-ports/tests/test_qwen_matrix_sh.sh`), graded against the matrix CONTRACT (`docs/research/findings/RESEARCH-FINDINGS-1-VERIFIED.md` §4: cells A-H, the `>= 1.5x A` throughput bar, re-prefills `< A`), D-030 (the launcher-owned guard is the ONLY lifecycle seam), AF-AP-79 (nothing persistent before the guard), AF-AP-83 (an auth oracle is never unauthenticated), never against the builder's own cases (verify lane: PC Hermes `adversarial-verifier` on the CLOUD verify route — the SINGLE-MODEL RULE applies: findings, no verdict; sandbox fallback Opus 5 `adversarial-verifier`)

PIN: `c41aab6`

**What you grade.** M (507 lines at the PIN), R (159), T (301), X (132), the `run-all.sh` wiring (+10 lines); the builder's report
`tasks/briefs/qwen-matrix-support/QM1-report.md` (REVIEW-PENDING; its lint `21 refs — OK 21`); the QM1 brief with its AMENDMENT 1
(`tasks/briefs/qwen-matrix-l1-load-generator.md`) and the pack `tasks/briefs/qwen-matrix-support/QM1-pack.md`. The launcher seams are QM0's
landed `harness-ports/bin/qwen-server.sh` (S: `argv` S:91-114, `validate_knobs` S:66-89, `guard` S:159-185, `install` S:223-250). The
coordinator's sandbox gates: `4 passed in 0.58s` (T), `qwen-matrix-sh: 9 passed, 0 failed` (X), `run-all.sh` ALL SUITES PASSED. Known and
NOT yours to re-find: no 100K corpus exists yet (the builder measured the two scrubbed exports at 29,824 and 47,865 tokens and refuses with
rc 2); no real cell ran; the dispatcher suite reads `0 passed, 9 failed` inside a lane environment (a lane-environment artifact under
reproduction by the coordinator — it reads `9 passed` on the clone and in the sandbox).

**NEVER on this venue:** a real cell run, `install`/`start`/`stop`/`restart`/`uninstall` against the real unit, a load run against the live
server (it serves VERIFY-GOV1); R's lifecycle paths run ONLY with X's fake seams (read X:1-60 for the fake `qwen-server.sh`/`systemctl`/
`nvidia-smi` shims). READ-ONLY live GETs of `/props`, `/metrics` and one `/tokenize` of a short string are allowed (keyed; the key stays in a
variable, never printed).

## Items (every item = a reproduced probe with its exact command, output and file:line)
- **V1 — the guard is the only lifecycle seam (D-030, AF-AP-79).** R:27-53: `guard` runs BEFORE `CELL_DIR` is created — reproduce with X's fake
  launcher returning rc 7: no cell directory, no install call, no unit change, rc 7 with the launcher's message. Then the failure ORDER:
  what is the first persistent effect in R and is anything (a cell dir, a log, a sample file) written before the guard? Grep R for every
  write and cite each line; a write before the guard is BLOCKING. Attack: `QWEN_LANES_DIR` unset/empty for the guard; a `CELL_DIR` that
  already exists (a rerun) — refused or clobbered?
- **V2 — the restore is proven by bytes, not by a call.** R:130-159 restores the baseline through the launcher's `install` on success AND on
  failure: reproduce both with the fake seams and assert the unit SHA returns to the baseline's; then break the restore (a fake `install`
  that leaves the cell unit) — does R report the mismatch and exit non-zero, or print success? A trap/`finally` gap (a SIGTERM to R mid-cell,
  `kill -TERM` the fake sampler) — what is left behind? Cite the trap lines.
- **V3 — the corpus builder fails closed (M:85-121, M:129-180).** With X's or a scratch fake `/apply-template` + `/tokenize` (or a live
  `/tokenize` of a SHORT string, keyed): a real export shorter than the target → rc 2 and NO `prompt-*.json`; exactly at the target; one token
  over; an export with no user turn; a tool turn without a summary; a malformed export. Then the corpus SHAPE: the first user turn becomes the
  system message, tool turns become `<tool_response>` user content — is a `<tool_response>` string a prompt-injection surface for the load
  model (harmless for a throughput matrix? state it) and does the builder scrub the secrets the export could carry (the key file path, a
  bearer)? Grep the two exports under `~/qwen-builder/ab/` for `Bearer `/`api-key` (read-only) and say what the builder would emit.
- **V4 — the keyed reads and the auth oracle (AF-AP-83).** M's `/props` + `/metrics` reads carry the key: reproduce a wrong-key read against the
  LIVE server read-only (`/props` → 401) and confirm M FAILS closed (rc ≠ 0, a named error), never records a cell with empty metrics; then T's
  fixture server (`AP-66 (6) resets fixture-server state`): does the fake validate the Bearer value or answer any request? If it answers any
  request, the same class the coordinator refuted on QM0 (AF-AP-83) — a finding with the fix shape (validate against the configured test key).
- **V5 — actual overlap, not sequential requests.** `request_rows` (M:285-322): the test claims "actual request overlap" — reproduce with the
  fixture server: N requests whose server-side handling sleeps; assert the wall time ≈ one sleep, not N; then the one-worker mutant (the
  builder killed it) — re-derive it as a scratch edit and confirm the red; then a subtler one: a pool of N but `max_workers=N-1`.
- **V6 — the metrics deltas and the re-prefill count (M:345-385).** `parse_metrics` reads exactly the five `REQUIRED_METRICS` (M:21-27): a
  missing counter → refused (the builder's mutant); a counter that WRAPS or resets between rounds (a server restart mid-matrix) → a negative
  delta: refused or reported as a rate? `_count_reprefills` counts log lines after the round's byte offset: a log that ROTATES mid-round, a
  line split across the offset, a re-prefill line format the server changes (the string it matches — cite it and check it against the live
  server's log format, read-only: `journalctl --user -u qwen-builder -n 50 | grep -i prefill` or the launcher's log path).
- **V7 — the table decisions (M:401-436).** Duplicate A, missing A, non-finite metrics refused; the thresholds `>= 1.5x A` and re-prefills
  `< A`: boundary values (exactly 1.5x, 1.4999x, A's own row), a cell with zero requests, a cell whose re-prefill count equals A's. The
  builder's `1.7x` threshold mutant died — re-derive; add `>` vs `>=` at the boundary.
- **V8 — the six scratch mutants + the artifact identity.** Reproduce the builder's six (required-counter deletion; fixed prompt order; the
  one-worker pool; the 1.7x threshold; guard rc forced to zero; the baseline reinstall bypassed) from their descriptions — each compiled/parsed
  first, each red at a named assertion; then confirm the cell record binds `argv_sha256` + the unit sha + `/props` fields (`model_alias`,
  `total_slots`, `n_ctx`, `build_info`) and that a record with a mismatching `argv_sha256` is refused by the table/reader.
- **V9 — the report.** FILE IDENTITY (M/R/T/X/run-all) against the PIN (the coordinator read 5/5); `report_lint.py --map M=harness-ports/bin/qwen_matrix.py
  --map R=harness-ports/bin/qwen-matrix.sh --map T=harness-ports/tests/test_qwen_matrix.py --map X=harness-ports/tests/test_qwen_matrix_sh.sh
  --map S=harness-ports/bin/qwen-server.sh --min-refs 12`; grade every VERIFIED claim you can reproduce in ≤ 5 min; UNSURE for the rest, never false.

**Output.** `tasks/briefs/qwen-matrix-support/VERIFY-QM1-report.md`: line 1 `NO VERDICT (single-model rule): findings only`; FINDINGS first,
ranked (a write before the guard, a restore that can leave the cell unit, or an auth oracle that validates nothing goes first), each with the fix
shape; per item SOLID/UNSURE with the command, the output and `file:line` (`M=`, `R=`, `T=`, `X=`, `S=`; declare the map at the top); a NOT-done
list. Report lint with your map, `--min-refs 15`, the bounded rule (three rounds, then paste and finish). No edits to the landed bytes; NEVER a
real cell or lifecycle command.
