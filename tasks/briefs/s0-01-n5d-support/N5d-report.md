# N5d — build report

## done

### F1 (BLOCKING) — probe never exits 0 with unsampled interpreter identity
- `proofs/S0-01/tools/acp_probe.py:209-210`: removed `proc.poll() is None` guard; every readlink failure is now `probe_error`.
- `proofs/S0-01/tools/acp_probe.py:258-265`: added post-loop sampling block inside `if c2a_delivered:` — attempts readlink at EOF/exit if the in-loop sampling never ran; failure message = `"interpreter sample failed: agent exited before its first a2c byte"`.
- `proofs/S0-01/tools/acp_probe.py:151`: updated comment to match (was "AFTER the first a2c byte and BEFORE wait", now "at the first a2c byte OR at EOF/exit").
- Red observed before fix: shape A agent (`import sys; sys.exit(0)`) exited `probe_rc=0, probe_error=None, interp fields null`. After fix: `probe_rc=1, probe_error="interpreter sample failed: agent exited before its first a2c byte"`.
- `tests/test_s0_01_acp_probe.py:1000` `test_probe_agent_exits_without_output_is_fail_loud`: shape A → rc 1, exact probe_error, exact stderr. Red before fix (on pristine HEAD), green after.
- `tests/test_s0_01_acp_probe.py:1018` `test_probe_interpreter_sample_failure_after_child_exit`: uses a dedicated quick-exit agent (writes response, exits without `sys.stdin.read()`), readlink patched to sleep 1 s then raise (child dead by then) → rc 1, probe_error = "interpreter sample failed: No such process". Red on pristine HEAD (the `poll()` guard sees the child dead and suppresses the error), green after.
- All fixture agents in `tests/test_s0_01_acp_probe.py` that write stdout now call `sys.stdin.read()` after their response to block until the probe closes stdin — this eliminates the readlink race (F9) by keeping the child alive during sampling.

### F2 (BLOCKING) — SR-03 gets a real killer
- `tests/test_s0_01_spec_runner.py:363` `test_runner_records_the_observed_line_not_the_expected_reason`: checker prints a superset line (`"failure_reason: negative: <R> (seq 2, id 0)"`), test asserts `observed_failure_reason` equals the FULL observed line, not the expected reason string. Red on SR-03 mutant: mutant returns `expected_reason` verbatim. Green on pristine runner.
- `tests/test_s0_01_spec_runner.py:437` `test_runner_unmet_when_expected_reason_is_multiline`: expected reason contains `\n`, checker prints the two halves as two lines. Per-line rule cannot match → unmet. Red on SR-03 mutant: whole-text substring matches across the newline. Green on pristine runner.
- Replaced the tautological `test_runner_unmet_when_reason_split_across_lines` (its docstring "Kills the 'whole-output substring' mutant" was false — both builds rejected the test's needle).

### F4/F8 (BLOCKING) — fixture agents run under the runner's interpreter by construction
- All 9 fixture agents in `tests/test_s0_01_acp_probe.py` changed from `#!/usr/bin/env python3` to `#!{sys.executable}` (the pattern `tests/test_s0_01_negative_contract.py:363` already uses). Producer's `/proc/<pid>/exe` and the test's `sys.executable` expectation are the same interpreter BY CONSTRUCTION.
- PATH-shim run (python3 → /usr/bin/python3.13, sys.executable = python3.11): all 4 interpreter-sensitive tests green. Verified with and without shim.
- Files: `agent_result` :40, `agent_error` :68, `agent_silent` :88, `agent_stderr_heavy` :100, `agent_partial_line` :126, `agent_notification_then_response` :140, `agent_non_json` :193, `agent_sigterm` :225, inline agent in `test_probe_identity_fields_all_pinned` :824.

### F7 — exact-reason violations fixed
- `tests/test_s0_01_check_initialize.py:837`: `in r.stdout.strip()` → exact `==` with full `"failure_reason: malformed evidence: ValueError: NaN/Infinity not allowed in timeline: 'NaN'"`.
- `tests/test_s0_01_check_initialize.py:850`: `"usage:" in r.stderr` → exact `== "usage: check_initialize.py request|response <file|dir> [--fixtures-dir <dir>]"`.
- `tests/test_s0_01_check_initialize.py:393,403`: added exact usage stderr assertion to `test_usage_error_exits_64` and `test_usage_error_no_args_exits_64`.
- `tests/test_s0_01_acp_probe.py:565`: `>= 1` → `== 1`.

### F10 — redundant assertions deleted, load-bearing ones kept
- Deleted 5 genuinely redundant lines from `test_probe_result_response_and_check_initialize`: `"probe_sha256" in rid` (covered by `test_probe_identity_fields_all_pinned`), `agent_exit_code == 0` (covered by `test_probe_error_response`), `"spawned_at_utc" in rid` (covered by `test_probe_spawned_at_two_sided`), `agent_interpreter_realpath is not None` (covered by `test_probe_interpreter_fields_pinned`), `agent_interpreter_sha256 is not None` (same).
- Kept `:287` `agent_argv` (sole killer of AP-20) and `:288` `"probe_path" in rid` (only probe_path assertion in probe test suite).

## mutant table (SR-03 and AP-32 now killed)

| # | id | result | first killing test |
|---|---|---|---|
| 1-27 | CI-06 through SR-02 | KILLED (unchanged) | (see verify-N5c table) |
| 28 | **SR-03 whole-output-substr** | **KILLED** | `spec_runner::test_runner_records_the_observed_line_not_the_expected_reason` + `test_runner_unmet_when_expected_reason_is_multiline` |
| 29-51 | SR-04 through AP-28 | KILLED (unchanged) | (see verify-N5c table) |
| 52 | **AP-32 probe-path-wrong** | **KILLED** | `negative_contract::test_build_valid_matches_the_live_producer_shape` |
| 53-58 | CI-21 through AP-35 | KILLED (unchanged) | (see verify-N5c table) |

CI-10 (true equivalent) remains SURVIVED. TOTAL 58: 57 KILLED / 1 SURVIVED (equivalent).

## PATH-shim run

```
PATH=shim:$PATH /usr/local/bin/python3 -m pytest (4 interpreter tests)
4 passed in 5.55s
```

## gates

```
pytest-summary: 234 passed in 39.66s
pytest-summary: 234 passed in 39.69s
```

```
pyflakes rc=0
```

## files

- `proofs/S0-01/tools/acp_probe.py`: 3 edits (guard removed, post-loop sampling added, comment updated)
- `tests/test_s0_01_acp_probe.py`: fixture shebangs + stdin.read, 5 redundant assertions deleted, `>= 1` → `== 1`, 2 new F1 tests
- `tests/test_s0_01_check_initialize.py`: 4 exact-reason assertions tightened
- `tests/test_s0_01_spec_runner.py`: 1 tautological test replaced by 2 SR-03 killers

## not_done

None. All 4 blocking findings (F1, F2, F4/F8) and both non-blocking (F7, F10) are closed.

## discrepancies

- `tests/test_s0_01_check_acp_conformance.py` appeared in `git diff --stat` as a new 438-line file. This is from another lane editing the shared tree. Not in my boundary.

## adjacent defects (report only)

- F3 (probe_path unread identity field) and F5 (7-way set assertion) and F6 (fake agent duplicates pins as literals) are in the coordinator's F3 checkpoint (READ-ONLY `tests/test_s0_01_negative_contract.py`). No action from this lane.
- F9 (interpreter sample flake) is closed by F1 — the fixture agents now block on `sys.stdin.read()` ensuring the child is alive during sampling, and the probe now fails loud on sample failure instead of silently accepting null identity.
