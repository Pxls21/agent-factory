# N5f REPORT — S0-01 ACP probe: the later interpreter reading wins

## PIN check
- `git rev-parse HEAD` = `303600a80465521acde1cbe7f87dd85b83252bdf` (matches override)
- dirty set: exactly 5 D5f/B5d files (M frame_tee.py, scripted_backend.py, 3 test files)
- `git log --oneline -5` contains `S0-01 WIP checkpoint 8f:` at 3cba9b9
- `df -h /`: 16G free

## Baseline
```
pytest-summary: 242 passed in 48.72s
```
(Coordinator's F7 hunk raised the baseline to 246 mid-lane; all subsequent runs reflect 252 = 246 + 6 new tests.)

## R9-N5e-F1 reproduction (BEFORE code changes)
- Wrapper agent (`#!/bin/sh` + `sleep 0.05` + `exec python`): `agent_interpreter_realpath` = `/usr/bin/dash` 3/3
- Env-shebang agent (`#!/usr/bin/env python3`): `agent_interpreter_realpath` = `/usr/bin/env` 12/12
- Both WRONG (expected `/usr/bin/python3.11`)

## R9-N5e-F1 post-fix verification
- Wrapper agent: `agent_interpreter_realpath` = `/usr/bin/python3.11` 3/3
- Env-shebang agent: `agent_interpreter_realpath` = `/usr/bin/python3.11` 12/12

## Done

### F1 + F8 + F2 — the later reading wins
- `proofs/S0-01/tools/acp_probe.py`: deleted `_last_good` arm; removed `_interp_sampled` flag; renamed to `_late_sampled`; early loop uses `_EARLY_SAMPLE_DEADLINE_S` and `_EARLY_SAMPLE_STEP_S` module constants; at the first a2c chunk the late sample ALWAYS re-reads `/proc/<pid>/exe` (once, `_late_sampled` flag), overwrites interp_realpath/sha256, and clears `interpreter sample failed:` errors on late success.
- `tests/test_s0_01_acp_probe.py`: added `test_probe_interpreter_is_the_final_exec_not_a_wrapper` (wrapper agent, assert python interp) and `test_probe_env_shebang_interpreter_is_constant` (env-shebang 12x, exactly one distinct pair).
- RED before: wrapper 3/3 `/usr/bin/dash`, env 12/12 `/usr/bin/env`. GREEN after: wrapper 3/3 python, env 12/12 python.

### F2 — _last_good deleted
- The `_last_good` variable and its fallback arm are gone from the code. LG1 mutant is equivalent by construction.

### F3 — exact equality assertion
- `tests/test_s0_01_acp_probe.py:1239`: changed from `"No such file or directory" in rid["probe_error"]` to `rid["probe_error"] == "interpreter sample failed: [Errno 2] No such file or directory: '/tmp/fake_interp (deleted)'"`.
- RED before (F3PREFIX mutant survived). GREEN after (F3PREFIX killed, 4 failed).

### F4 — early loop bound pinned
- `proofs/S0-01/tools/acp_probe.py`: module constants `_EARLY_SAMPLE_DEADLINE_S = 0.2`, `_EARLY_SAMPLE_STEP_S = 0.002`.
- `tests/test_s0_01_acp_probe.py`: `test_probe_early_sample_loop_bound_is_pinned` — fake clock, always-failing readlink, asserts exactly 101 early-loop readlinks. DL_DOUBLE (0.2 -> 0.4) gives 201 -> killed.

### F5 — test rename + exact assertions
- `test_probe_agent_exits_without_output_is_fail_loud` renamed to `test_probe_agent_exits_without_output_keeps_interpreter_identity`.
- Docstring: "rc is race-decided (the c2a write lands before or after the exit); the interpreter triple is constant".
- Assertions: `r.returncode in (0, 1)`; rc 1 -> exact BrokenPipeError probe_error + stderr; rc 0 -> `"probe_error" not in rid`; interpreter triple non-null in both arms.

### F6 — crash path writes complete evidence
- `proofs/S0-01/tools/acp_probe.py`:
  - `_write_evidence`: guarded `_sha256_file(agent_realpath)` with `except OSError as exc: agent_entrypoint_sha256 = None; probe_error = ...`; returns `probe_error`.
  - Extracted `_write_env(framedir)` for reuse.
  - Pre-initialised all identity fields to `None` before the `try` block.
  - Captured `child_pid = proc.pid` right after Popen.
  - M3 handler: writes all four files (rid with 11 keys + probe_error, env.json via `_write_env`, timeline.jsonl, agent-stderr.txt).
- `tests/test_s0_01_acp_probe.py`:
  - `test_probe_self_deleting_script_is_probe_error_not_traceback`: assert 4 files, 12 keys (11 + probe_error), exact probe_error string, `agent_entrypoint_sha256 is None`, checker prints `probe reported an error: FileNotFoundError: ...` (never `env.json absent`).
  - `test_probe_m3_handler_writes_complete_evidence`: `_write_evidence` patched to raise `RuntimeError("boom")`, assert 4 files, 12 keys, exact probe_error, stderr.

### F9 — failure_reason whitespace pattern + runner raw line test
- `proofs/schemas/spec.schema.json`: added `"pattern": "^\\S(.*\\S)?$"` to `failure_reason` (alongside `minLength`).
- `tests/test_spec_probe_schemas.py`: `test_spec_failure_reason_rejects_edge_whitespace` (leading space, trailing space -> rejected, error path names `failure_reason`).
- `tests/test_s0_01_spec_runner.py`: `test_runner_records_the_raw_line_not_the_stripped_line` — checker prints padded line, assert `observed_failure_reason` keeps padding (kills SR-09).
- `tests/test_s0_01_spec_runner.py`: `test_runner_unmet_when_expected_reason_is_multiline` updated to strip the new pattern from its schema copy (the multiline reason itself contains `\n` which the pattern rejects).
- SR-06 equivalence: once the schema forbids edge whitespace in `expected`, `expected in line.strip()` is equivalent to `expected in line` for any `expected` matching `^\S(.*\S)?$`. A non-whitespace-bounded substring present in `line.strip()` is present in `line` (strip removes only characters not covered by the substring). The converse holds because `line.strip()` is a contiguous subsequence of `line`.
- Committed specs: all 14 failure_reasons pass the new pattern (verified).

### F12 — realpath(sys.executable) assertions (REPORT ONLY)
- Three assertions at lines 457, 659, 895 (final tree). Each fixture's shebang is `#!{sys.executable}`, so the assertion matches the shebang interpreter. No code change per the brief; PC leg is the coordinator's.

### F13 — docstrings/comments
- `acp_probe.py:210-214`: comment now reads "the reading at the first a2c byte is authoritative; the early loop covers agents that never write" (no "last good reading", no false determinism claim).
- `acp_probe.py:204`: restored "never from /proc/self/exe" clause.
- `_write_evidence` docstring: now says "a self-deleting agent degrades gracefully" (not "crash here is probe_error").
- `test_s0_01_acp_probe.py` test docstring at `test_probe_agent_exits_without_output_keeps_interpreter_identity`: "rc is race-decided; the interpreter triple is constant".
- `test_probe_sigterm_killed_agent_exit_code` docstring: "samples right after Popen, before the agent reaches stdin" (not "samples while the agent still blocks on stdin").

### LATE-NOCLEAR test
- `test_probe_late_sample_clears_early_interpreter_error`: `_sha256_file` patched to fail on the first call during the early loop (readlink succeeds, sha256 fails -> `probe_error = "interpreter sample failed: early sha failure"`). At the late sample, sha256 succeeds and the early error is cleared. Asserts `"probe_error" not in rid`, rc 0.

## Not_done
(none — all brief items addressed)

## Files touched
- `proofs/S0-01/tools/acp_probe.py` — sha256: `b60ba85e2f1df0e147cb9f3b2167bdf26ff33a9d4413d560be843d49589da187`
- `tests/test_s0_01_acp_probe.py`
- `tests/test_s0_01_spec_runner.py`
- `proofs/schemas/spec.schema.json`
- `tests/test_spec_probe_schemas.py`
- `tests/test_s0_01_check_initialize.py` — NOT touched (read-only per boundary)

## Suite summaries (pasted from `scripts/test_summary.sh`)
```
pytest-summary: 252 passed in 56.51s
pytest-summary: 252 passed in 55.59s
```
Schema/runner:
```
pytest-summary: 31 passed in 7.57s
```
Pyflakes: rc=0 on all touched `.py` files.

## Mutant table (every run = the full five-file suite, 252 tests)

| id | mutation | result | killing test(s) |
|---|---|---|---|
| NOOP | unmodified | 252 passed | -- |
| EARLY-DEL | delete the early sample loop | KILLED 7 failed | `test_probe_early_retry_recovers_from_transient_readlink_failure` + 6 others |
| LATE-DEL | delete the late a2c-triggered sample | KILLED 5 failed | `test_probe_interpreter_sample_failure` + 4 others |
| LATE-GATE | gate late sample on `interp_realpath is None` | KILLED 3 failed | `test_probe_interpreter_is_the_final_exec_not_a_wrapper` |
| LATE-NOCLEAR | remove clearing of early `interpreter sample failed:` error | KILLED 1 failed | `test_probe_late_sample_clears_early_interpreter_error` |
| LATE-NULL | late readlink failure nulls the early reading | KILLED 1 failed | `test_probe_fast_exit_agent_is_deterministic` |
| APF1A | single readlink, no retry loop | KILLED 2 failed | `test_probe_early_retry_recovers_from_transient_readlink_failure` |
| F3PREFIX | `probe_error = f"{exc}"` (drop prefix) | KILLED 4 failed | `test_probe_post_loop_sha256_failure_truthful_error` |
| DL_DOUBLE | deadline 0.2 -> 0.4 | KILLED 1 failed | `test_probe_early_sample_loop_bound_is_pinned` |
| EV_OUTSIDE | `_write_evidence` moved outside handler | KILLED 1 failed | `test_probe_self_deleting_script_is_probe_error_not_traceback` |
| EV_SWALLOW | handler swallows exceptions | KILLED 3 failed | `test_probe_self_deleting_script_is_probe_error_not_traceback` |
| M3-NOENV | M3 handler skips `env.json` | KILLED 1 failed | `test_probe_m3_handler_writes_complete_evidence` |
| LG1 | delete `_last_good` arm | EQUIVALENT by construction (arm deleted in the fix) | -- |

All 11 non-equivalent mutants killed. 1 proven-equivalent.

## Discrepancies
- The brief's PIN line `220ffde` was overridden by the dispatch to `303600a` per explicit instructions. No other discrepancies found between the brief's claims and the tree.
- The baseline moved from 242 to 246 mid-lane (coordinator's F7 hunk); final suite shows 252 (246 + 6 new tests).

## Adjacent defects (REPORT ONLY)
- F7 from the verdict (negative_contract.py falsy non-string `probe_error` message) was fixed by the coordinator mid-lane. Not my boundary.
- The three `realpath(sys.executable)` assertions (F12) will fail on the PC where the fixture shebang resolves to a different interpreter. The PC leg fix is the coordinator's.

## Self-attack

1. **The late sample fires only when a2c data arrives. Agents that never write stdout will never get the late sample.** RULED OUT: the early loop is the fallback for exactly that case. The post-loop block (inside `if c2a_delivered:`) is the additional fallback after the a2c timeout. Both are tested (EARLY-DEL kills the early-loop-only path, POST-DEL mutants from the verdict kill the post-loop path).

2. **The LATE-NOCLEAR test uses a timing gate (0.3s). Could the early loop succeed on a loaded box?** RULED OUT: the early loop is bounded at 0.2s by the constant. The `_sha256_file` patch fails on the FIRST call (call count == 1, not time-based), so even if the early loop completes faster, the first sha256 call always fails. The time check `time.monotonic() - _start < 0.3` is a secondary guard that is not the sole mechanism.

3. **The `_write_evidence` return-value pattern is fragile — the caller must use the returned probe_error.** RULED OUT: the call site explicitly captures the return value (`probe_error = _write_evidence(...)`). A future editor who drops the assignment would break `test_probe_self_deleting_script_is_probe_error_not_traceback` (rc 0 instead of 1).
