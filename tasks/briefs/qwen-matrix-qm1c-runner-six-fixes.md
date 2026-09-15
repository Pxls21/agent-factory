# QM1-c — L1 concurrency-matrix runner: the six VERIFY-QM1 findings fixed

**Authorization.** Defensive tooling on the owner's own PC (the qwen-builder throughput matrix). No live
model, unit, or GPU is touched here — every effect uses fakes; the real matrix runs on the PC later.

**Ground.** QM1-b landed the L1 matrix runner (`harness-ports/bin/qwen_matrix.py` = M, `harness-ports/bin/qwen-matrix.sh`
= R) with tests (`harness-ports/tests/test_qwen_matrix.py` = T, `harness-ports/tests/test_qwen_matrix_sh.sh` = X).
VERIFY-QM1 (`tasks/briefs/qwen-matrix-support/VERIFY-QM1-report.md`) returned SIX real findings, two BLOCKERS.
Fix all six; each fix = the code change + a deterministic LLM-free test with its negative control + a pasted
line. No real cell runs — the guard (R's launcher-owned `guard`, rc 7 on a live LOCAL lane) stays the sole
lifecycle seam. READ the VERIFY-QM1 report whole first; its scratch-probe repros (V1_RERUN, V2_ABSENT_BASELINE,
V6_LOG_ROTATION, V8_MISMATCHED_IDENTITY, V7_ZERO_REQUESTS, SECRET_INPUT_PARSED) are your acceptance targets.

**Boundary.** M, R, T, X, and your report `tasks/briefs/qwen-matrix-support/QM1c-report.md`. Nothing else. The
class list AF-AP-78/79/80/83/84/85/86/87 is your preflight. CODE INTEL FIRST: `graft ask` / `ripwire` on M and R
before editing; attach the pack.

## Items (1-6; in order)

1. **F1 [BLOCKER] a reused CELL_DIR must not carry a stale result.json (R:55-63, M:386-394/471-476).** Before
   any write into `CELL_DIR`, either REFUSE an existing directory or atomically use a run-specific directory
   AND remove/invalidate a prior `result.json` before the lifecycle effect. The table reader (`_load_cell` /
   `main`) must reject a `result.json` whose run did not complete. TEST: a cell A succeeds, a rerun fails
   (guard rc 7 or a forced load failure) — the table must NOT accept the stale prior result (reproduce
   `V1_RERUN first_rc=0 failed_rerun_rc=7 stale_result_retained=yes table_rc=0` going GREEN → the stale result
   rejected). Negative control: the fix removed → the stale result is accepted (red).

2. **F2 [BLOCKER] an initially-absent unit must be restored to ABSENT (R:80-114).** Snapshot BOTH the unit's
   presence and its bytes before install. On failure: if the unit was initially absent, remove/disable the
   runner-created unit through an authorized launcher-owned restore and VERIFY absence; if present, restore the
   exact bytes (the existing path). TEST: initially-absent success AND failure — the unit is absent again after
   (reproduce `V2_ABSENT_BASELINE rc=8 initial_absent=yes unit_left_present=yes` going GREEN → unit absent).
   Negative control: the absence-restore removed → a new persistent unit is left (red). Use fakes for
   systemctl/install; never touch the real qwen-builder unit.

3. **F3 log-rotation must not silently drop re-prefill lines (M:257-277).** Record the log's inode+device with
   the byte offset; if either changes, refuse (or re-read from 0) rather than reading the new file from the old
   offset. TEST: a rotation that replaces the log with a new file at least as long as the old offset, carrying a
   new `forcing full prompt re-processing` line — the counter must SEE it or the round must refuse (reproduce
   `V6_LOG_ROTATION old_offset=111 counted=0 expected_new_prefill=1` going correct). Negative control: the
   inode/device check removed → the new line is missed (red).

4. **F4 the table must validate a cell's claimed identity (M:386-394/397-432).** `_load_cell` requires
   `argv_text`, a lowercase SHA-256 that MATCHES `argv_text`, and a lowercase unit SHA; a record with a bogus or
   mismatched argv/unit SHA is REFUSED by the table. TEST: reproduce `V8_MISMATCHED_IDENTITY table_rc=0
   mismatched_argv_and_unit_sha_accepted=yes` going to a REFUSAL. Negative control: the identity check removed →
   the bogus record renders (red).

5. **F5 the table must require a positive request count (M:397-432).** `render_table` requires an integer
   positive `summary.requests` for every cell before any performance decision. TEST: a baseline A with
   `requests: 0` (and negative / non-integer) is REFUSED, not judged (reproduce `V7_ZERO_REQUESTS table_rc=0
   performance_yes_on_A_requests_0=yes` going to a refusal). Negative control: the check removed → `requests:0`
   passes (red).

6. **F6 build_corpus must not persist unscrubbed secrets (M:100-121/129-175).** The corpus source is untrusted
   input. Either (a) require a trusted-producer attestation from the scrubbing exporter, or (b) scrub the parsed
   messages through the SAME `scripts/transcript_export.py` `SECRET_PATTERNS` immediately before persist/send.
   Prefer (b) — belt-and-suspenders on top of the exporter's own scrub (the exporter now scrubs tool bodies as
   of the `--tool-body-cap` change). TEST: an export carrying `Bearer …` / `api-key` / an `sk-` token is
   redacted (or refused) before it reaches a prompt file (reproduce `SECRET_INPUT_PARSED
   bearer_literal_preserved=True api_key_literal_preserved=True` going to redacted/refused). Negative control:
   the scrub removed → the literal survives (red).

## Gates (paste every line)

- `python3 -m py_compile M`, `pyflakes M`, `bash -n R`, `git diff --check` → rc 0 each.
- `python3 harness-ports/tests/test_qwen_matrix.py` and `bash harness-ports/tests/test_qwen_matrix_sh.sh` →
  paste the exact `N tests passed` / `N passed, 0 failed`.
- `PATH=/home/rocco/venv-agent-factory/bin:$PATH bash harness-ports/tests/run-all.sh` → ALL SUITES PASSED
  (run with the NORMAL environment, not a lane TMPDIR — the path-contract tests require /tmp).
- Six scratch mutants (one per fix), each compiling/parsing BEFORE the test runs (AF-AP-78), each killed by the
  matching negative control; paste the killer line for each.
- FILE IDENTITY: sha256 + line count of M, R, T, X before → after.
- report_lint with `--map M=… --map R=… --map T=… --map X=…`.

NOT for you: no real matrix cell, live load, GPU sampling, unit change, commit, push, or tag. Retro: name any
new class for the coordinator; bake nothing yourself.
