PROPOSAL — QM1-c implementation complete; sandbox adversarial verification remains required.

No real matrix cell, live load, GPU sample, service mutation, commit, push, or tag ran. This build lane cannot issue an independent gate verdict.

SCOPE

- PIN: `f911bd033514`
- Changed only M=`harness-ports/bin/qwen_matrix.py`, R=`harness-ports/bin/qwen-matrix.sh`, T=`harness-ports/tests/test_qwen_matrix.py`, X=`harness-ports/tests/test_qwen_matrix_sh.sh`.
- Context pack: `../scratch/QM1c-final-pack.md` (200 lines).

VERIFIED IMPLEMENTATION

1. F1 stale reused cell. R refuses any existing `CELL_DIR` with rc 3 before creating files or invoking lifecycle effects (`CELL_DIR`, R:55-57). X first records cell T, retries T, then requires rc 3, the named refusal, and no `install` call (`existing cell directory`, X:104-109).

2. F2 initially absent unit. R records the absent state as `BASELINE_SHA=absent`, restores that state through the launcher-owned `uninstall` seam, verifies the unit path is absent, and reports rc 8 if restoration fails (`BASELINE_SHA`, R:81-86; `uninstall`, R:97-106). X covers success, load failure, and a fake uninstall that leaves the unit behind (`ABSENT_OK`, X:134-150).

3. F3 rotated log. M snapshots size, device, and inode in `_log_position`; `_count_reprefills` refuses replacement, disappearance, and truncation before reading from the old offset (`stat.st_dev`, M:273-298). T atomically replaces a log with a larger file that contains the prefill marker and requires `server log rotated during round` (`old_position`, T:262-273).

4. F4 cell identity. `_load_cell` requires non-empty `argv_text`, canonical lowercase argv/unit SHA-256 values, and recomputes `argv_sha256` from the exact persisted text (`argv_sha256`, M:408-428). T refuses a canonical but mismatched argv digest and a malformed unit digest (`mismatch`, T:337-357).

5. F5 positive requests. `render_table` iterates `for name, cell in by_name.items()` and accepts only an exact `int` greater than zero, so bool, zero, negative, float, and string values cannot enter performance decisions (`positive integer`, M:454-459). T tests all five invalid classes (`bad_requests`, T:329-335).

6. F6 corpus scrub. `_scrub_messages` loads the canonical repository exporter and calls its `scrub` function; `build_corpus` applies it immediately after parsing and before tokenization or persistence (`transcript_export.py`, M:126-150). T passes synthetic Bearer, api-key, and sk-shaped values through the actual `build_corpus` path, proves none survives in the prompt, and pins each redaction form (`secret_export`, T:227-239).

TEST EVIDENCE

Focused suites, twice, normal fake-only environment:

- `test_qwen_matrix: 4 tests passed`
- `qwen-matrix-sh: 13 passed, 0 failed`
- Second run returned the same two counts.

Whole harness suite, final bytes:

- `PATH=/home/rocco/venv-agent-factory/bin:$PATH bash harness-ports/tests/run-all.sh`
- `test_qwen_matrix.py                test_qwen_matrix: 4 tests passed`
- `test_qwen_matrix_sh.sh             qwen-matrix-sh: 13 passed, 0 failed`
- `ALL SUITES PASSED`

Static-copy gate on `git archive f911bd0` plus only M/R/T/X, with temporary pytest adapters for the repository's executable contract scripts:

- `RESULT: rev=f911bd033514 files=4 deleted=0 runs=2 tests=2c555550deb9 identical=yes rc=0 summary="2 passed in 5.27s 2 passed in 6.17s"`
- The direct brief-prescribed `lane_gate.sh -t "harness-ports/tests/test_qwen_matrix.py harness-ports/tests/test_qwen_matrix_sh.sh"` was also tried. It returned rc 1 and `no tests ran` because these are executable contract scripts, not pytest-collected tests. No product test failed.

Static checks on final bytes:

- Static source checks covered `python3 -m py_compile M` (`import hashlib`, M:5-8), `/home/rocco/venv-agent-factory/bin/python -m pyflakes M`, and `bash -n R` (`cleanup`, R:90-101); each returned rc 0.
- `bash -n X` (`set -uo pipefail`, X:1-4): rc 0.
- `git diff --check`: rc 0.

MUTATION EVIDENCE

Every scratch mutant was applied to a separate `git archive f911bd0` copy overlaid with M/R/T/X, parsed or compiled before its matching suite, and left the lane tree unchanged.

- F1 remove existing-directory refusal: KILLED, parse rc 0, test rc 1, `qwen-matrix-sh: 12 passed, 1 failed` at `existing cell directory is refused before lifecycle effects`.
- F2 remove launcher `uninstall`: KILLED, parse rc 0, test rc 1, `qwen-matrix-sh: 11 passed, 2 failed`; the first killer was `successful cell restores an initially absent unit to absent`.
- F3 remove device/inode comparison: KILLED, compile rc 0, test rc 1, `AssertionError: same-size-or-larger rotated log was read from a stale offset`.
- F4 remove argv digest recomputation: KILLED, compile rc 0, test rc 1, `AssertionError: mismatched argv identity was accepted`.
- F5 remove positive-integer request guard: KILLED, compile rc 0, test rc 1, `AssertionError: invalid request count was accepted: 0`.
- F6 bypass `_scrub_messages`: KILLED, compile rc 0, test rc 1, assertion that a planted literal survived.

FILE IDENTITY

- M before: `c29034ebc95045c15c244da382691048e5d8e79b10c55b71007353d34aaec802`, 507 lines. After: `1e0f22df43fa26c14918e0d93edd72c23955dbb36a783ce3b29212abf76b4618`, 543 lines.
- R before: `0bac99de34174c76fccc03350cd077a9f29f05d1c5dbdce80b03fd048ad4cba5`, 159 lines. After: `c25e1c6e8aafca995c254e2ba5725760e43f1e1cf29db9caead684219afc93a5`, 170 lines.
- T before: `de7a4958de020e38e1ea8a0e5a3135af3b90079262c9bdfa4485b3464a6da45c`, 301 lines. After: `c88cd20df380fc8795825a21c11d32fbc2de8f761a4717bda94c84248445995a`, 368 lines.
- X before: `49196603b2b6682c930cd7b4eafefaa839137820915285aefbd049a475679383`, 132 lines. After: `214c8290e7ef5b756d2aa4bc887c17cc98c5c6afd8ca92566047b4676e7dd540`, 160 lines.

CODE-INTEL / SCREEN DATA

- Final lane-context pack mapped all six fixes and four files.
- Ripwire found `_scrub_messages` and `_log_position` as new symbols, one and two callers respectively, with `incompatible="0"`; `_count_reprefills`, `_load_cell`, `render_table`, and R's qualified `cleanup` had no signature change and `incompatible="0"`.
- GitNexus `detect-changes` against the clone index printed `No changes detected.` This is an index/worktree limitation, not a low-risk finding.
- AP screen: M had 9 classified hits (four existing env CLI defaults, four identity-hash sites, one result path); R had one matrix-input recording hit; T had fixture-state/health fake hits; X had zero. These are the intended CLI, identity, result-reader, and deterministic fake surfaces. No hit identified a new bypass.

SELF-ATTACK

1. The stale result could remain readable after a retry. Ruled out at the writer boundary: retry exits rc 3 before any cell write or install. The removal mutant makes X fail.

2. Cleanup could claim success while leaving an initially absent unit installed. Ruled out by state inspection after launcher `uninstall`, both success/failure-path tests, and a hostile fake that leaves the unit and must force rc 8. The bypass mutant makes X fail.

3. Tests could validate helpers but miss the consumed boundaries. Ruled out by testing secrets through `build_corpus` to the prompt file, identity through `_load_cell`, request validity through `render_table`, rotation through `_count_reprefills`, and lifecycle behavior through R with a fake launcher. Six corresponding mutants die.

INFERRED

- Loading `scripts/transcript_export.py` by repository-relative path keeps M on the same scrub policy as the exporter without copying regexes. This assumes the deployed runner keeps the repository layout, as all harness scripts do.
- Refusing a rotated log is intentionally conservative. It prevents a performance verdict from incomplete evidence but does not recover the new file's count.

ASSUMED

- The launcher's existing `uninstall` command remains the authorized restoration operation for a previously absent unit. This was traced in `harness-ports/bin/qwen-server.sh`; no live invocation was permitted.

NOT DONE

- No independent sandbox adversarial verification. This report is a proposal until that lane grades it.
- No real 100K corpus, matrix cell, live model request, GPU measurement, or real systemd operation.
- No commit, push, tag, ledger edit, incident-log edit, or skill edit.

DISCREPANCIES

- Final report lint: `report_lint: 16 refs — OK 16, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)` under `--min-refs 15`.
- GitNexus reads the production clone index rather than this detached dirty lane and reported no changes. Ripwire and the final lane-context pack mapped the lane bytes instead.
- `lane_gate.sh` always delegates `-t` to pytest, while T/X are directly executable Python and Bash contract scripts. The literal invocation produced `no tests ran`; temporary pytest adapters exercised those exact scripts twice in the archive gate. The direct suites and whole `run-all.sh` also passed.
- RED/GREEN history was not captured before the implementation edits. Negative-control proof comes from six post-build scratch mutants, all compiled/parsed before execution and all killed.

REASONING RECORD

- Rejected deleting/reusing an old cell directory because failure between deletion and completion would make run identity ambiguous. Immutable cell names fail before lifecycle effects.
- Restored absence through launcher `uninstall`, not direct `rm` or `systemctl`, to preserve the guarded lifecycle ownership boundary.
- Refused log replacement rather than reading from zero because a rotation race can still make the count interval ambiguous.
- Validated persisted identity in `_load_cell`, the disk trust boundary, rather than only when producing the record.
- Used `type(requests) is int` because `bool` is an `int` subclass and must be refused.
- Reused exporter `scrub` by import rather than copying `SECRET_PATTERNS`, so one canonical policy protects export and corpus persistence.

retro: nothing new to bake. The six defect classes were already recorded by VERIFY-QM1; coordinator should run bug-echo during landing closeout.
