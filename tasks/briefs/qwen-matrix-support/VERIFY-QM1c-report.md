# VERIFY-QM1-c — adversarial verification of QM1-c (landed at `c728be5`)

FINDINGS ONLY. This cloud verify lane reports no merge verdict.

## Finding 1 — BLOCKER — failed/aborted runs can be rendered as valid matrix evidence

M:409 (`candidate`) accepts a cell solely from `result.json` plus its identity and summary fields at M:414 (`data.get`). It does not require a completion marker, reject `run-error`, or otherwise bind the table reader to a successfully completed launcher run. R:60 (`RESULT_FILE`) is written by the Python run at R:151-157 (`load generator failed`) before later post-processing, and the launcher has no completion marker at R:161-170 (`result.write_text`).

Repro (fresh synthetic cell, no live seam): create a cell directory containing a fully valid `result.json` and no run marker, then run the production table command. The observed output was `MARKER_EXISTS False`, a rendered A row, and exit `0`. Adding either `run-error` or an arbitrary `run-complete` file also yielded `TABLE_RC 0`. This contradicts the brief’s V1 requirement that a `result.json` whose run did not complete be rejected.

Minimal fix: write an immutable per-run completion record only after result post-processing and successful restoration, bind it into the cell record, and make `_load_cell` require that matching record while rejecting an error/unfinished state. Add a true failed-after-result fixture through `qwen-matrix.sh`, not only an existing-directory refusal before creation.

## Finding 2 — SHOULD-FIX — persisted unit identity checks format, not the actual unit bytes

M:417 (`argv_text`) through M:427 (`unit_sha`) verify only that `unit_sha256` is lower-case 64-hex. Unlike `argv_sha256` at M:424 (`hashlib.sha256`), it never recomputes it from a persisted unit-text artifact. The launcher writes only `unit-sha256` at R:69-72 (`UNIT_SHA`), not the exact rendered `UNIT_TEXT`.

Repro: a valid cell with `unit_sha256 = 'b' * 64` loads successfully: `ARBITRARY_LOWERCASE_UNIT_SHA_ACCEPTED bbbbb...`. A lower-case digest of unrelated bytes therefore passes as the claimed unit identity.

Minimal fix: persist the exact rendered unit text beside the cell result and recompute/compare its SHA-256 in `_load_cell`; test a canonical-looking lower-case SHA that does not match the persisted unit text.

## Reproduced controls and attack coverage

- V2 absence restoration: R:97-105 (`uninstall`) was exercised through the fake-only direct suite. X:145-150 (`QM_UNINSTALL_LEAVES_UNIT`) reported `13 passed, 0 failed`; its hostile fake-uninstall case returned rc `8` with `initially absent unit remains after restore`. A separately constructed present-unit fake whose baseline bytes differ from launcher defaults produced rc `8` and `baseline unit sha mismatch after restore`, so byte drift fails loud.
- V3 rotation: M:283-293 (`_count_reprefills`) raised the production `MatrixError` for same-inode truncation and a larger replacement; a simulated device change with the same inode was also refused. The F3 scratch mutant compiled, collected 4 tests, loaded from its scratch path, and died with `AssertionError: same-size-or-larger rotated log was read from a stale offset`.
- V4 argv and format controls: M:420-427 (`argv_sha`/`unit_sha`) refused mismatched argv SHA, uppercase/truncated unit SHA, and absent argv text. The format guard is not sufficient for the actual-unit binding, hence Finding 2.
- V5 requests: M:454-468 (`requests`/`verdicts`) refused `True`, `0`, `-1`, `1.0`, `'1'`, and `None` before a decision.
- V6 parsed-message scrub: M:126-137 (`_scrub_messages`) and M:145-150 (`build_corpus`) redacted synthetic Bearer, `api-key`, `sk-`, `password=`, and a bare 40-hex opaque token before the prompt file. `scripts/transcript_export.py:24` (`SECRET_PATTERNS`) declares the supported pattern policy; the two added shapes are covered by its assignment/opaque `re.compile` patterns at `scripts/transcript_export.py:26-36`. No claim is made for arbitrary shorter token-like strings outside that policy.

## V7 scratch mutation audit

All mutants were applied to independent `git archive c728be5` copies. Production bytes remained untouched.

| mutant | valid before run | scratch module identity / killer |
|---|---|---|
| F1 remove immutable cell refusal | `bash -n` passed | X:104 (`Negative control`), rc 1; `qwen-matrix-sh: 12 passed, 1 failed` |
| F2 remove `uninstall` | `bash -n` passed | X:134-150 (`ABSENT_OK`), rc 1; `qwen-matrix-sh: 11 passed, 2 failed` |
| F3 suppress device/inode guard | `py_compile`; 4 collected | M:283-293 (`_count_reprefills`), scratch `qwen_matrix.py`; `AssertionError: same-size-or-larger rotated log was read from a stale offset` |
| F4 suppress argv recomputation | `py_compile`; 4 collected | T:337-357 (`mismatch`), scratch module; `AssertionError: mismatched argv identity was accepted` |
| F5 suppress positive-int guard | `py_compile`; 4 collected | T:329-335 (`bad_requests`), scratch module; `AssertionError: invalid request count was accepted: 0` |
| F6 bypass parsed-message scrub | `py_compile`; 4 collected | T:227-239 (`secret_export`), scratch module; `AssertionError` from the planted literal-survival assertion |

## Fresh deterministic gates

- `python3 harness-ports/tests/test_qwen_matrix.py` twice: `test_qwen_matrix: 4 tests passed`, rc 0 each.
- `bash harness-ports/tests/test_qwen_matrix_sh.sh` twice: `qwen-matrix-sh: 13 passed, 0 failed`, rc 0 each.
- Normal environment: `PATH=/home/rocco/venv-agent-factory/bin:$PATH bash harness-ports/tests/run-all.sh` ended `ALL SUITES PASSED`, including `test_qwen_matrix: 4 tests passed` and `qwen-matrix-sh: 13 passed, 0 failed`.
- `python3 -m py_compile M`, `/home/rocco/venv-agent-factory/bin/python -m pyflakes M`, `bash -n R`, `bash -n X`, and `git diff --check`: rc 0.

## Statically reviewed and deliberately not reproduced

- The actual `qwen-server.sh` lifecycle integration was reviewed statically at `harness-ports/bin/qwen-server.sh:232` (`install`) through `harness-ports/bin/qwen-server.sh:259` (`wait_health`); only fake launcher effects were executed, as required by venue policy.
- No live model, unit, GPU, `qwen-builder` corpus, credential, or running lane file was read or touched.
- GitNexus and code-review-graph indices were unavailable for this detached lane. Graft and ripwire mapped `main → _load_cell/render_table/build_corpus/run_load`; ripwire independently found test callers for `_load_cell`, `render_table`, and `build_corpus`. Shell subprocess coverage is outside ripwire’s direct-call model.

## NOT-DONE

- The two findings remain unfixed. In particular, the table reader still has no completion-state trust boundary, and unit identity remains unbound to actual bytes.
- No independent human or different-model decision occurred; this report is evidence for the coordinator.

## DISCREPANCIES

- Brief ground claims `M:386-394` rejects incomplete runs, but M:387 (`_count_reprefills`) concerns log evidence and current M:408-428 contains only JSON/identity validation, with no run-state check. The V1 premise was tested with three synthetic run-state shapes, then bounded.
- `scripts/test_summary.sh` cannot count the two executable contract scripts because it delegates to pytest: `no tests ran`, `ERROR: not found ... test_qwen_matrix_sh.sh`, rc 4. Direct script counts above are the applicable instrument output.
- The brief says test T has 4 tests and X has 13. Both were reproduced, twice, with matching counts.

## FILE IDENTITY (final bytes)

- M=`harness-ports/bin/qwen_matrix.py`: SHA-256 `1e0f22df43fa26c14918e0d93edd72c23955dbb36a783ce3b29212abf76b4618`, 543 lines.
- R=`harness-ports/bin/qwen-matrix.sh`: SHA-256 `c25e1c6e8aafca995c254e2ba5725760e43f1e1cf29db9caead684219afc93a5`, 170 lines.
- T=`harness-ports/tests/test_qwen_matrix.py`: SHA-256 `c88cd20df380fc8795825a21c11d32fbc2de8f761a4717bda94c84248445995a`, 368 lines.
- X=`harness-ports/tests/test_qwen_matrix_sh.sh`: SHA-256 `214c8290e7ef5b756d2aa4bc887c17cc98c5c6afd8ca92566047b4676e7dd540`, 160 lines.

retro: new class to bake by coordinator: a persisted digest must be recomputed from a persisted preimage at the reader, not validated only as canonical format. Existing AF-AP-31 producer-binding guidance is related; no lane-side skill/doc edit made.
