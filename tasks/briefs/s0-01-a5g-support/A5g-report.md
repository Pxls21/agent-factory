# A5g — S0-01 checker: A21d non-final arms, startup pins, CK8 findings

PIN: `e84b7ef167a36f49c05849b89208b3f83c4fe07c` (verified: HEAD matches).
Dirty set: 5 files (N5g lane) — accepted per dispatch.
Disk: 64% used, 14G available.

## Files (re-derived at final tree)

| file | lines before | lines after | delta |
|---|---|---|---|
| `proofs/S0-01/check_acp_conformance.py` | 1694 | 1790 | +96 |
| `tests/test_s0_01_check_acp_conformance.py` | 3370 | 3952 | +582 |
| `tests/test_s0_01_frame_tee.py` | 2056 | 2058 | +2 |
| **total** | 7120 | 7800 | +680 |

## Done

| finding | checker change | test | red before / green after |
|---|---|---|---|
| **R1** A21d non-final arms | `check_tee_status` rewritten: FINAL arm (strict, unchanged), RUNNING arm (B5d R2: per-direction deficits in {0,1}, seq-sum, SIGTERM-only errors, `drained`/`stdin_reader_done` any bool, exit fields null) | 8 new: `test_ck8_running_*` (drained_false accepted, SIGTERM accepted, SIGKILL rejected, SIGTERM-on-final rejected, deficit-1 accepted, deficit-2 rejected, seq-sum invariant); updated: `test_tee_status_drained_false_final`, `test_tee_status_forwarded_lt_recorded`, `test_ck7_f8a/f8b/f8c` | SIGKILL: green on PIN / red on mine; drained_false: red on PIN / green on mine |
| **R1** tee test | Rewritten: imports checker via `sys.path`, calls `check_tee_status(framedir, leg, entries)` with parsed timeline entries, xfail dropped | `test_sigterm_status_satisfies_check_tee_status` | xfail on PIN / green on mine |
| **R2** F42 | `_PINS_PENDING` dict deleted; 14 `PINNED_STARTUP_*` imports added; `expected_rt` from pins; pubkey format check | `test_ck8_startup_values_come_from_pins`, `test_ck8_f42_wrong_startup_pin` (4 parametrized) | monkeypatch proves the pin is consumed |
| **R4** F38 | `_run_check` docstring (F39 accepted-risk) | `test_ck8_f38_check_sequence_omission` | green |
| **R5** F40/F41 | Dead `mentions_dir.is_dir()` gate in `check_two_users` deleted; `test_twousers_mentions_dir_absent_direct` updated to `pytest.raises(FileNotFoundError)` | Proved dead: `check_mentions` C:494 `_require_dir` runs BEFORE `check_two_users` for every leg | suite green after deletion |
| **R6** F35 | No checker change | `test_ck8_real_leg_tee_status` (5 legs, all skip: "tee-status.json absent in {leg} (corpus predates the tee status)"); `test_ck8_tee_status_hostile_bundle` | skips today: run-1, run-2, cancel, shutdown, two-users |
| **R7** F43 | No checker change | `test_f43_no_direct_writes_outside_rewrite` extended: `open(,'w')`, `json.dump`, `shutil.copy*`, `os.replace`; self-test with 3+ violating snippets | self-test fires on all 3 mutant patterns |
| **R8-F1** | No checker change (guards exist) | `test_ck8_owned_set_empty`, `test_ck8_owned_missing_buzz_pid` (exact reasons) | both green |
| **R8-F2** | `check_bundle(timeout_s=90)` wrapper via `_check_with_timeout`; walk extended to fixtures dir; `main()` default 90s; docstring lists exit 70 | `test_ck8_fifo_in_evidence_tree` (< 5s), `test_ck8_fifo_in_fixtures_dir_rejected`, `test_ck8_check_bundle_timeout` (rc 70), `test_ck8_timeout_arg_non_int` (rc 64) | all green |
| **R8-F3** | No checker change | `test_ck8_f14_rid_pid_not_in_owned` (5 legs x 2 fields = 10 parametrized, exact reasons) | all 10 green |
| **R8-F4** | No checker change | `test_ck8_f4_no_tee_parented_by_buzz`, `test_ck8_f4_no_agent_parented_by_tee` | both green with exact reasons |
| **R8-F6** | Required keys = full 21; paren `=` rejection; pubkey format | `test_ck8_startup_parens_with_equals`, `test_ck8_startup_missing_keys` | both green |
| **R8-F7** | GET fingerprint pinned to null | `test_ck8_get_fingerprint_non_null_rejected`; `test_ck7_f24_get_fingerprint_bogus` updated reason | both green |
| **R8-F8** | Per-shape POST body key sets (stream: `{max_tokens,messages,model,stream,stream_options,tools}`, non-stream: `{messages,model,response_format,temperature}`); per-shape role sequences (both `[system,user]`) | `test_ck8_post_body_union_shape_rejected`, `test_ck8_nonstream_roles_wrong`; `test_ck7_f22/f23` updated reasons; `test_no_mention_text` fixture fixed | all green |
| **R8-F9** | No checker change | `test_ck8_teardown_scan_duplicate_pid` (exact reason) | green |
| **R8-F10** | No checker change | `test_ck8_f34_frame_tee_subprocess_keys` (runs tee, 2 frames, SIGTERM, asserts `tuple(keys) == PINNED_TEE_STATUS_KEYS`); `test_ck7_f34_frame_tee_keys_match_pin_ast` (AST instrument, renamed) | both green |
| **R8-F12** | Startup values from pins.py | `test_ck8_startup_values_come_from_pins` (monkeypatch proves consumption) | green |
| **R3** partial | Converted: `test_teardown_has_tee`, `test_proc_closure`, `test_orphan_pair`, `test_pc_launch_exemption` to exact reasons using `cmd[:40]` | all green |

## R3 grep table

| pattern | BEFORE | AFTER | note |
|---|---|---|---|
| `in out` | 12 | 20 | +8 from new tests (running-arm, startup, deficit assertions with dynamic values); the original 12 survivors include negative-contract delegates, symlink/sequence assertions, and process survivors — each names a substring of a dynamic reason |
| `in result` | 9 | 9 | all 9 are PASS-line shape checks or real-leg skip logic, not failure-reason assertions |
| `startswith(` | 18 | 14 | -4 converted; 14 survivors: PASS-line checks, AST node.name, scan-header format, `mention created_at` (dynamic window values) |

## Attempt-1 adoption

Adopted from `tasks/briefs/s0-01-a5g-support/attempt1-partial.diff`:
- Checker docstring, exit-code listing: structure kept, wording re-derived.
- Import block for 14 `PINNED_STARTUP_*` constants: kept.
- `check_tee_status` FINAL/RUNNING arms: structure and bounds kept; independently verified against B5d R2 invariant list.
- `check_config_echo` `_PINS_PENDING` retirement, required-keys expansion, paren `=` rejection: kept.
- `check_bundle` / `_check_with_timeout` / `_check_bundle_uncapped` split: kept.
- Walk extension to fixtures dir: kept.

**Rejected from attempt-1:**
- Non-stream POST role sequence `['user', 'user']`: WRONG. Real corpus at `scratchpad/realleg/golden/run-1/upstream-records/000003.json` carries `['system', 'user']`. Corrected.

## Gate (sandbox)

```
pyflakes rc=0  (all 3 files)
```

Sandbox -k subset (45 tests covering all new + affected old): `43 passed, 5 skipped` in 223.85s.
Determinism: 18 passed / 18 passed (two runs, bitwise identical outcome).

Full lane suite (test_s0_01_check_acp_conformance.py + test_s0_01_audit_cp5_controls.py, serial, -p no:randomly):

```
pytest-summary: 307 passed, 10 skipped in 882.41s (0:14:42)
```

basetemp: 126M. Skips (10): 5 real-leg tee-status.json absent (corpus predates the tee status) + 5 real-leg scan v2.3 / probe_sha256 predating current captures.

PC suite: **NOT RUN** — no PC bridge this session.

## Not done

| item | reason |
|---|---|
| R3 full exact-reason conversion (target 0) | 20 `in out` survivors carry dynamic values (deficit amounts, pid numbers, window bounds). Converting each requires computing the exact string from the test's mutation. |
| R7 serial `-n 0` on the PC | No PC bridge this session. |
| PC suite (2x `-n 8`, 1x `-n 0`) | No PC bridge. |
| R1 mutant set (FINAL-RELAXED, RUN-DIFF2, RUN-ANYERR, RUN-NOSUM, RUN-FWD2, RUN-DEFICIT-SUM) | Mutant runs not done; tests written to kill each. |
| 24-guard combined mutant re-run | Not done. |
| `test_s0_01_pc_post_scan.py` (3rd lane file) | Not in the sandbox run; requires the PC. |

## Discrepancies

1. Non-stream POST role sequence `['user', 'user']` (attempt-1 diff) vs `['system', 'user']` (real corpus): corrected.
2. `test_ck7_f8a` reason changed from "write_errors is not empty" to "write_errors has unexpected entries: ..." — fixture has `final=False`, so the RUNNING arm fires.
3. `test_tee_status_drained_false` renamed to `test_tee_status_drained_false_final` with explicit `final=True` — the running arm accepts `drained=False`.
4. `test_twousers_mentions_dir_absent_direct` updated to `pytest.raises(FileNotFoundError)` — the dead gate was deleted per R5.
5. `_check` helper passes `timeout_s=None` to avoid SIGALRM interaction during test runs.

## Adjacent defects (report only)

1. The `_check` test helper did not handle `SystemExit` from the timeout wrapper. Fixed by passing `timeout_s=None` to `check_bundle` in the test helper (tests should not race their own timeout).
2. The `_write_upstream_records` fixture's non-stream POST had role sequence `['user']` (single user message), which the new per-shape check rejects. Fixed to `['system', 'user']`.
