PROPOSAL — QM1-d implementation is self-validated; independent sandbox adversarial verification remains required.

NOT DONE

- Independent sandbox `adversarial-verifier` grading has not run. This single-model build lane does not issue the gate verdict.
- By brief boundary, no real matrix cell, live load, GPU sample, real service-unit mutation, commit, push, or tag ran.

SCOPE / PREMISE

- PIN: `c728be5`.
- Boundary: M=`harness-ports/bin/qwen_matrix.py`, R=`harness-ports/bin/qwen-matrix.sh`, T=`harness-ports/tests/test_qwen_matrix.py`, X=`harness-ports/tests/test_qwen_matrix_sh.sh`, plus this report.
- VERIFIED: the named verifier report was absent from the PIN/tree and recovered read-only from its verifier lane. Its two counterexamples reproduced before the change: `MARKER_EXISTS False` still rendered the A row, and canonical lowercase `unit_sha256 = 'b' * 64` loaded without byte verification.
- VERIFIED: final code-intelligence pack is `/home/rocco/agent-factory/.lanes/pc-qm1d.md--c728be5/scratch/QM1d-final-pack.md` (169 lines). Graft mapped M; Ripwire mapped two `_load_cell` callers. GitNexus and code-review-graph were unavailable to the pack, so no reachability/dormancy claim relies on them.

ITEM 1 — COMPLETION-STATE TRUST BOUNDARY

- R generates a fresh 64-hex `RUN_ID` before lifecycle effects (`R:63-66`), passes it to M with the result inputs (`R:163-167`), and publishes `run-complete` only in cleanup after result post-processing and byte-verified baseline restoration (`R:94-137`). EXIT owns cleanup; INT/TERM handlers preserve nonzero interruption status. The marker uses temp-file-plus-rename publication.
- M reads `run_id` from the result, refuses `run-error`, refuses malformed/missing run ids or completion records, and requires the completion value to equal the result identity before admission (`M:408-434`).
- T drives missing completion, explicit `run-error`, matching completion, mismatched completion, directory input, direct-result input, and a genuinely completed A row through `_load_cell` into `render_table` (`T:349-390`).
- X drives the required failed-after-result fixture through the fake-only production launcher: it writes `result.json`, forces wrong restoration bytes, observes rc 8, and requires `run-complete` to be absent (`X:142-169`). X also makes result post-processing fail, verifies `run-error`, exact baseline restoration, and no completion record (`X:171-187`), then sends TERM during the matrix step and verifies rc 143, restoration, and no marker (`X:189-203`).

ITEM 2 — UNIT BYTE IDENTITY

- R redirects exact `qwen-server unit` stdout bytes to `unit-text`, then hashes that file into `unit-sha256` (`R:73-76`). Shell command substitution is deliberately not used because it strips trailing newlines.
- M requires `unit-text`, checks its SHA against `unit-sha256` before result production (`M:549-567`), and independently recomputes the digest from the sibling persisted bytes at table admission (`M:441-448`).
- T sets `unit_sha256` to canonical lowercase `"b" * 64`, then refuses that mismatch against valid persisted bytes (`T:413-421`). T also rewrites `unit-text` with `tampered` bytes and refuses the changed artifact (`T:422-430`). X reads `completion` and verifies the successful-launch result identity against the persisted unit bytes (`X:100-110`).

TEST EVIDENCE

- Static gates, final bytes:
  - `py_compile_M_rc=0`
  - `pyflakes_M_rc=0`
  - `bash_n_R_rc=0`
  - `bash_n_X_rc=0`
  - `git_diff_check_rc=0`
- Focused deterministic runs, final bytes:
  - `test_qwen_matrix: 4 tests passed`
  - `python_run_1_rc=0`
  - `test_qwen_matrix: 4 tests passed`
  - `python_run_2_rc=0`
  - `qwen-matrix-sh: 16 passed, 0 failed`
  - `shell_run_1_rc=0`
  - `qwen-matrix-sh: 16 passed, 0 failed`
  - `shell_run_2_rc=0`
- Full harness, normal environment:
  - `test_qwen_matrix.py                test_qwen_matrix: 4 tests passed`
  - `test_qwen_matrix_sh.sh             qwen-matrix-sh: 16 passed, 0 failed`
  - `ALL SUITES PASSED`
- Static-copy gate:
  - `RESULT: rev=c728be59526a files=4 deleted=0 runs=2 tests=9059ec51f087 identical=yes rc=0 summary="4 passed in 0.61s 4 passed in 0.57s"`

MUTATION CONTROLS — SCRATCH COPIES ONLY

- F1 mutant removed the completion-record read/compare from M. It compiled, then the focused test killed it exactly:
  - `F1 compile_rc=0 test_rc=1 killer=raise AssertionError("cell without completion record rendered")`
- F2 mutant removed the unit-byte digest compare from M. It compiled, then the focused test killed it exactly:
  - `F2 compile_rc=0 test_rc=1 killer=raise AssertionError("mismatched unit identity was accepted")`
- Production M remained unchanged across the audit:
  - `production_hash_after_mutants=9dc6521f3ab923a3acf21991c62a43369554cc0e98be2416fb20e7fb6da3d9de`

FILE IDENTITY — PIN → FINAL

- M: `1e0f22df43fa26c14918e0d93edd72c23955dbb36a783ce3b29212abf76b4618`, 543 lines → `9dc6521f3ab923a3acf21991c62a43369554cc0e98be2416fb20e7fb6da3d9de`, 578 lines.
- R: `c25e1c6e8aafca995c254e2ba5725760e43f1e1cf29db9caead684219afc93a5`, 170 lines → `5c0fc7b1313c09271065e5a7aabb5adebc8dc1c3d673787b94997bb16f6188a7`, 187 lines.
- T: `c88cd20df380fc8795825a21c11d32fbc2de8f761a4717bda94c84248445995a`, 368 lines → `3404d8f9f3733155da37be93c41e3be27b4a8d2ea8c1c161d2ae0b0e3fb825f3`, 440 lines.
- X: `214c8290e7ef5b756d2aa4bc887c17cc98c5c6afd8ca92566047b4676e7dd540`, 160 lines → `a7be1e90adedf1a69fc00de1121d348da0d5eabe7c9e9959e196e68602339acc`, 231 lines.

ANTI-PATTERN SCREEN

- M: 13 reported hits. AP-32 hits are the intended SHA identity checks. AP-1 hits are unchanged explicit runtime configuration seams. AF-AP-40 hits are filesystem state checks required by this trust boundary.
- R: one AF-AP-39 line, unchanged matrix input recording.
- T: seven fixture/test hits (AP-66 mutable fixture resets; AF-AP-33 fake health endpoint), all pre-existing test machinery.
- X: zero hits.
- No new anti-pattern class was discovered. The work closes existing AF-AP-88; no incident-log edit is in this lane's boundary.

SELF-ATTACK

1. Completion could be published before restoration actually succeeded or after an interrupt was misclassified as success. Ruled out locally because R checks `RESTORE_NEEDED` and only writes `RUN_COMPLETE` after restoration (`R:94-137`); X's `AFTER_RESULT_FAIL` fixture returns rc 8 with a result present and no completion marker (`X:142-169`), and its TERM fixture returns rc 143 after restoration with no marker (`X:189-203`).
2. A stale or unrelated completion marker could authorize a result. Ruled out locally because M requires `completed_run_id != run_id` to be false (`M:427-434`); T writes a canonical-but-different `"f" * 64` marker and checks rejection (`T:380-390`).
3. A syntactically valid unit hash or changed persisted bytes could survive. Ruled out locally because M compares `hashlib.sha256(unit_text).hexdigest()` to `unit_sha` (`M:441-448`); T's `mismatched_unit` case rejects (`T:413-421`) and its `tampered` byte case rejects (`T:422-430`), while the guard-removal scratch mutant dies.

DISCREPANCIES / LIMITS

- The staged brief names `tasks/briefs/qwen-matrix-support/VERIFY-QM1c-report.md`, but that artifact is absent at PIN `c728be5`; it was read from `/home/rocco/agent-factory/.lanes/pc-verify-qm1c.md--c728be5/tree/tasks/briefs/qwen-matrix-support/VERIFY-QM1c-report.md`.
- `lane_context.sh` reports `unmapped — GitNexus index absent` and `unmapped — code-review-graph graph absent`; direct `GitNexus detect-changes` also reports `No changes detected` because it reads the clone index, not this detached lane diff. Graft/Ripwire and direct primary-source reads were used; no unsupported absence claim was made.
- Ripwire reports `script_gates_unmodelled="9"` and no mapped tests for this shell-driven boundary. The brief-prescribed focused suites, full `run-all.sh`, and static-copy gate were therefore run directly.
- Red-green evidence is mutation-based against final tests. The two final extra assertions were not rerun against the historical pre-fix file as a whole; the required guard-removal mutants both compiled and failed for the exact target reasons.
- During self-attack, a standalone signal probe showed that trapping EXIT/INT/TERM with one cleanup function can enter cleanup with rc 0 on TERM and falsely publish completion. R now routes INT/TERM to explicit 130/143 exits, and X locks the TERM path. This is the same completion-state trust-boundary class, not a new incident class.
- Report lint: `report_lint: 22 refs — OK 22, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

HANDOFF

- Treat these bytes as a build-lane proposal. Dispatch the separate sandbox `adversarial-verifier` against both findings and the full brief contract before acceptance.
- Suggested commit reasoning record: two disjoint trust-boundary changes. (1) Launcher-owned completion is published only after post-processing and verified restoration; rejected result-file existence because an aborted run can leave it behind. (2) Unit identity is recomputed from exact persisted renderer bytes; rejected a format-only SHA because arbitrary lowercase 64-hex values satisfy it. Primary sources: VERIFY-QM1-c counterexamples and current M/R consumers.

Retro: no separate lesson to bake. The signal-path defect was an instance of the existing completion-state trust-boundary rule and is now covered by a production-path regression; exact-byte persistence, value-bound completion, scratch-only mutants, and independent-verifier handoff are already standing protocol.
