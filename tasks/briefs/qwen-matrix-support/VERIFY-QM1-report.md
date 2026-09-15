COORDINATOR DISPOSITION (2026-09-15): findings ACCEPTED (findings-only, single-model rule — a cloud verify grading a cloud build). The six findings on the L1 matrix runner (M=qwen_matrix.py, R=qwen-matrix.sh) are REAL and feed QM1-c (a repair increment): F1 [BLOCKER] R reuses an existing CELL_DIR and never clears a prior result.json before a run -> a stale result survives a failed rerun and the table accepts it; F2 [BLOCKER] R stores BASELINE_SHA=absent when the unit is initially absent but cannot restore absence -> a failed cell leaves a new persistent unit; F3 log-rotation blind (size-decrease only); F4 the table accepts a cell record without validating its argv/unit identity; F5 render_table does not require requests>0; F6 build_corpus accepts unscrubbed export input without a trusted-producer assertion. F6 is PARTLY addressed by the coordinator's exporter change (commit 54dea67: hermes-session-export.py --tool-body-cap scrubs tool bodies through SECRET_PATTERNS), but M itself still needs the scrub-or-attest at persist (QM1-c). The two guard/restore/overlap/table controls the lane reproduced hold; six scratch mutants died. NEXT: QM1-c (the six fixes) before any real matrix cell; the 100K corpus is now staged PC-side (n5k-armA export, 101,474 tokens) but the matrix also waits for the local slot (VERIFY-GOV1 holds it).

NO VERDICT (single-model rule): findings only

Maps: M=harness-ports/bin/qwen_matrix.py; R=harness-ports/bin/qwen-matrix.sh; T=harness-ports/tests/test_qwen_matrix.py; X=harness-ports/tests/test_qwen_matrix_sh.sh; S=harness-ports/bin/qwen-server.sh.

FINDINGS

1. [BLOCKER] R:55-63 reuses an existing cell directory and never removes its prior `result.json` before a new run. A successful cell A record followed by a failed rerun returns rc 7, but the old result remains and M:386-394 `def _load_cell` plus M:471-476 `def main` accepts it as a current table input. Scratch probe: `V1_RERUN first_rc=0 failed_rerun_rc=7 stale_result_retained=yes table_rc=0`. This can publish a result whose argv/unit identity belongs to a prior run after a later cell execution failed. Minimal fix: refuse an existing CELL_DIR before any write, or atomically replace into a run-specific directory and remove/invalidate result.json before the lifecycle effect; add a rerun-after-success then failure control that table rejects.

2. [BLOCKER] R:80-85 stores `BASELINE_SHA=absent` when the initial unit does not exist, but R:96-114 restores by calling launcher install and then merely reports `baseline unit restore missing`; it cannot restore absence. Scratch probe: `V2_ABSENT_BASELINE rc=8 initial_absent=yes unit_left_present=yes`. The failed cell leaves a new persistent unit although the initial state was no unit. Minimal fix: snapshot both presence and bytes before install; if initially absent, remove/disable the runner-created unit through an authorized launcher-owned restore operation and verify absence. Add an initially-absent success/failure test.

3. [SHOULD-FIX] M:257-277 detects only a log size decrease. Rotation that produces a new file at least as long as its former offset is read from the old offset, so it silently misses a new `forcing full prompt re-processing` line. Scratch probe: `V6_LOG_ROTATION old_offset=111 counted=0 expected_new_prefill=1`. The resulting decision can claim `re-prefills < A` from an incomplete counter. Minimal fix: record log inode/device with offset and refuse when either changes, or use an externally reliable counter. Add a rotation-with-larger-replacement negative control.

4. [SHOULD-FIX] M:386-394 `def _load_cell` / M:397-432 `def render_table` treat a cell record as usable without validating its claimed argv/unit identity fields. A record with a bogus 64-character argv SHA and malformed unit SHA table-renders successfully: `V8_MISMATCHED_IDENTITY table_rc=0 mismatched_argv_and_unit_sha_accepted=yes`. The brief requires that a mismatching argv_sha256 be refused by the table/reader. Minimal fix: make _load_cell require `argv_text`, a lowercase SHA-256 matching it, and a lowercase unit SHA; if table is intended to validate disk artifacts, bind these to the companion identity files or a signed/attested record. Add the malformed/mismatch test.

5. [SHOULD-FIX] M:397-432 `def render_table` does not require summary.requests to be positive. A baseline A with `requests: 0` and arbitrary positive rates yields a passing B performance decision: `V7_ZERO_REQUESTS table_rc=0 performance_yes_on_A_requests_0=yes`. A table must not judge throughput from a record that says it made no requests. Minimal fix: require an integer positive request count for every cell summary before decisions, with 0/negative/wrong-type controls.

6. [SHOULD-FIX] M:100-121 `def parse_export` accepts arbitrary export content and M:129-175 writes it to load prompts without a scrub or trusted-producer assertion. `parse_export` preserved synthetic `Bearer ...` and `api-key` literals exactly: `SECRET_INPUT_PARSED assistant_payload_len=77 bearer_literal_preserved=True api_key_literal_preserved=True`. The ordinary Hermes exporter does scrub through scripts/transcript_export.py:24-43 `SECRET_PATTERNS`, but M does not establish its source used that exporter. Minimal fix: restrict corpus sources to scrubbed, exporter-attested output or scrub immediately before persist/send; add a secret-shaped export refusal/redaction test. A tool-response string itself remains a prompt-injection surface for the target model; that is expected workload content but must not carry credentials.

REPRODUCED

V1: X:102-123 passes an isolated live-PID fake guard: rc 7, no cell dir or install; independent probe also passed with empty QWEN_LANES_DIR: `V1_GUARD rc=7 cell_absent=yes install_absent=yes unit_unchanged=yes`. R:50-56 places the guard before CELL_DIR creation. The actual launcher guard returns rc 7 by default on this active host and rc 0 against an empty scratch lane directory: `qwen_guard_default_rc=7 qwen_guard_overridden_empty_dir_rc=0`.

V2: X:84-123 `# Positive dry run` passes exact baseline-byte restoration on success and load failure. Independent fake-restore mutation returned named rc 8 (`V2_BROKEN_RESTORE rc=8 named_mismatch=yes unit_changed=yes`); a SIGTERM during the fake sampler/load restored byte-identical baseline (`V2_TERM rc=143 baseline_restored=yes`). Findings 1 and 2 remain.

V3: T:198-265 passes export shape/cut/exhaustion. Independent malformed/no-turn and no-user probes named MatrixError. Wrong live key got `/props` 401; M then failed build-corpus closed with rc 2 and no prompt: `qwen-matrix: /apply-template returned HTTP 401`, `wrong_key_build_corpus_rc=2 prompt_count=0`. The three committed read-only exports contained zero Bearer/api-key/key-path markers, but arbitrary input remains untrusted (finding 6). No live 100K corpus was available and no real cell/load ran.

V4/V5: The fixture validates exact bearer value at T:81-111 `def do_GET`. Independent fixture measurement: `V4_V5_AUTH_AND_OVERLAP wrong_key_fixture=401 peak=2 wall=0.208s`; M:359-362 `with ThreadPoolExecutor` has concurrency-sized pool and submits all futures before result collection. The one-worker mutant compiled then was killed by the fixture's two-party barrier. This proves overlap at the fixture, not a live model load.

V6: M:178-230 `def parse_metrics` rejects missing, NaN and reset metrics. Independent output: `V6_NAN ... must be finite`, `V6_RESET ... moved backwards`, `V6_TRUNCATED_LOG ... truncated during round`. Finding 3 remains; no live prefill log line appeared in the last 50 journal lines, so that production format was not independently confirmed.

V7: M:397-432 `def render_table` rejects missing A, duplicate A and non-finite values. Independent boundary output: `V7_BOUNDARY ratio=1.5=>YES ratio=1.4999=>NO refill_equal=>NO`. The 1.7 threshold mutant was killed. Finding 5 remains.

V8: Six required scratch mutants parsed/compiled before test execution and all died: required-counter, fixed-order, one-worker, threshold-1.7, guard-zero, restore-bypass. Exact killer lines are in the test evidence below. Finding 4 is an independent identity-reader counterexample.

V9 / FILE IDENTITY

M c29034ebc95045c15c244da382691048e5d8e79b10c55b71007353d34aaec802, 507 lines.
R 0bac99de34174c76fccc03350cd077a9f29f05d1c5dbdce80b03fd048ad4cba5, 159 lines.
T de7a4958de020e38e1ea8a0e5a3135af3b90079262c9bdfa4485b3464a6da45c, 301 lines.
X 49196603b2b6682c930cd7b4eafefaa839137820915285aefbd049a475679383, 132 lines.
run-all d69b33b537ded62ee3c6a5420cbe54151f98d2417ca48f860b1ac1aef7ad7b3c, 68 lines. `git diff --check c41aab6 -- <five files>` returned rc 0.

TEST EVIDENCE

`python -m py_compile M; python T; bash X` => `py_compile_rc=0 python_contract_rc=0 shell_contract_rc=0`; T printed `test_qwen_matrix: 4 tests passed`; X printed `qwen-matrix-sh: 9 passed, 0 failed`.

Six scratch mutants (all compiled/parsed first):
- required-counter: test rc 1, `raise AssertionError("missing metric did not fail")`.
- fixed-order: test rc 1, assertion on `[[0, 1], [1, 0]]` prompt indices.
- one-worker: test rc 1, `BrokenBarrierError: single worker never reaches the two-party fixture barrier`.
- threshold-1.7: test rc 1, assertion `D: aggregate decode >= 1.5x A: YES (1.600x)`.
- guard-zero: test rc 1, `[FAIL] live-lane guard refuses rc 7 before cell or service side effects`.
- restore-bypass: test rc 1, `[FAIL] fake cell run restores baseline unit bytes`.

Static review: graft and ripwire map M:129 `def build_corpus`, M:343 `def run_load`, and M:397 `def render_table` to main plus their direct Python tests. The lane-context pack is `../scratch/qm1-verify-pack.md`. GitNexus clone index did not contain the new symbols: `Target 'run_load' not found`, risk UNKNOWN. This is a tool limitation, not a low-risk result. Anti-pattern screen classified M's env CLI surface/identity hash/result path and X's explicit fake fixture state; no new production write was made.

NOT DONE / UNSURE

- No real matrix cell, lifecycle action, live load, or GPU sampling ran, by venue rule.
- No live 100K corpus exists. The supplied exports remain below the target.
- No independent sandbox-model verdict: this is a single-model PC lane.
- The expected live server log prefill format was not observed in last-50 journal output; M's literal cannot be confirmed here.
- Full `PATH=/home/rocco/venv-agent-factory/bin:$PATH bash harness-ports/tests/run-all.sh` was freshly rerun: all suites other than pre-existing `test_pc_lane_dispatcher.sh` passed, including T 4 and X 9; final `1 SUITE(S) FAILED`. The dispatcher printed `0 passed, 9 failed` because it got empty route values. This does not validate all-suite wiring.
- restore semantics for a genuinely absent user unit need a launcher capability; this report did not invoke live lifecycle paths.

DISCREPANCIES

- Final report lint: `report_lint: 23 refs — OK 23, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)` under `--min-refs 15`.
- Initial lane_context invocation failed safely with rc 64 because `../scratch` did not exist; after mkdir it wrote a 154-line pack. This matches the PIN's repair, not the builder report's earlier fail-open behavior.

retro: nothing to bake; coordinator must run bug-echo and register the six findings before a repair increment.
