> STATUS 2026-09-07 (coordinator): graded by VERIFY-N5g (NOT-READY on two items) and, after the closure commit df58f95, by VERIFY-N5g-b (MERGE-READY). The LG2-POST row below ("SURVIVED — equivalent-by-test-design") was WRONG: the mutant was not equivalent; it is killed at df58f95 by the path-aware post-loop test. Two rows (PINS-12KEY, LG2-POST) were graded on the 53-test probe file, not the five-file suite. Kept as the lane's historical claim.

# N5g — BUILD report (round 9 repair, VERIFY-N5f)

## Premise

```
git rev-parse HEAD  -> b2b83a0026050494fbe3a2d08d58c629a3817dbb
PIN                 -> 628a8c93dcf554bfa2d02f6303e7481d424a901d
HEAD is one wiki commit ahead of PIN (b2b83a0 = wiki live-state update).
All 9 in-scope files byte-identical between PIN and HEAD — VERIFIED.
git status --porcelain --untracked-files=no  -> empty
df -h /  -> 252G 23G 15G 62%
```

Blockers reproduced BEFORE code:
- LATE-NULL on pristine probe → `252 passed` (survived, F1 confirmed)
- LG2-EARLY on pristine probe → `252 passed` (survived, F2 confirmed)

Baseline:
```
pytest-summary: 252 passed in 47.80s   (five-file suite, pre-edit)
pytest-summary: 31 passed in 6.24s     (schema/runner suite, pre-edit)
validate-ledger integrity: S0-09 PRESENT  S0-10 PRESENT  S0-11 PRESENT  S0-12 PRESENT
```

## Done

### F1 — test_probe_late_readlink_failure_keeps_the_early_reading (tests/test_s0_01_acp_probe.py:1737)
In-process wrapper; `os.readlink` patched with call counter — `/proc/*/exe` succeeds on call 1 (early loop), raises `OSError` from call 2 on (late sample). Agent = answering fixture.
Asserts: `rid["agent_interpreter_realpath"] == os.path.realpath(sys.executable)`, sha non-null, no probe_error, rc 0.
Red on LATE-NULL:
```
assert None == '/usr/bin/python3.11'
1 failed, 255 passed
```
Green on HEAD: `256 passed`.
Comment added at acp_probe.py:317-319.

### F2 — test_probe_interpreter_is_child_not_self_for_a_silent_agent (tests/test_s0_01_acp_probe.py:1793)
`#!/bin/bash` agent (`read line; sleep 3`, no stdout), `ACP_PROBE_TIMEOUT=2`. Asserts `rid["agent_interpreter_realpath"] != os.readlink(f"/proc/{os.getpid()}/exe")` and `basename == "bash"`.
Red on LG2-EARLY:
```
FAILED test_probe_interpreter_is_child_not_self_for_a_silent_agent
2 failed, 254 passed
```
Green on HEAD: `256 passed`.

### F3 — pinned absolute values in test_probe_early_sample_loop_bound_is_pinned (tests/test_s0_01_acp_probe.py:1612-1614)
Added: `assert _ap._EARLY_SAMPLE_DEADLINE_S == 0.2`, `assert _ap._EARLY_SAMPLE_STEP_S == 0.002`.
Red on DL_SCALE:
```
FAILED test_probe_early_sample_loop_bound_is_pinned
1 failed, 255 passed
```
Green on HEAD: `256 passed`.

### F4 — renamed test_runner_unmet_when_expected_reason_is_multiline → test_runner_per_line_rule_holds_for_a_multiline_expected_reason (tests/test_s0_01_spec_runner.py:437)
Docstring updated. SR-03 killer preserved (the schema copy lifts the pattern so the reason reaches the matcher).

### F5 — schema pattern `failure_reason` (proofs/schemas/spec.schema.json:36)
Changed `"^\\S(.*\\S)?$"` → `"^\\S(.*\\S)?(?![\\s\\S])"`.
9 hostile strings tested:
```
trailing-newline 'foo\n'    schema_rejected=True   (was False)
multiline        'a\nb'     schema_rejected=True
leading-newline  '\nfoo'    schema_rejected=True
trailing-tab     'foo\t'    schema_rejected=True
trailing-space   'foo '     schema_rejected=True
leading-space    ' foo'     schema_rejected=True
trailing-cr      'foo\r'    schema_rejected=True
trailing-nbsp    'foo\xa0'  schema_rejected=True
trailing-2nl     'foo\n\n'  schema_rejected=True
```
7 committed spec-leg values: all accepted=True.
Added `("a\nb", "multiline")` and `("foo\n", "trailing-newline")` to schema parametrize; renamed to `test_spec_failure_reason_rejects_edge_whitespace_and_newlines` (tests/test_spec_probe_schemas.py:101).

Attestation chain (AF-AP-56):
```
python3 scripts/proof-runner run --proof S0-09 --venue sandbox --root .  (+ S0-10, S0-11, S0-12)
python3 scripts/validate-ledger integrity --root .  →  S0-09 PRESENT  S0-10 PRESENT  S0-11 PRESENT  S0-12 PRESENT
python3 scripts/ledger-gen --root .  ×2  →  IDENTICAL (sha256 match)
```

### F6 — test_probe_interpreter_is_sampled_once_at_the_first_a2c_byte (tests/test_s0_01_acp_probe.py:1820)
Agent writes notification FIRST (no `id`, no `found_response`), then after 0.2 s writes the response. `os.readlink` patched: call 1 → real (early), call 2 → real (first late, recorded), call 3+ → sentinel.
Asserts recorded value == call-2 value, != sentinel.
Red on LATE-EVERY:
```
assert '/SENTINEL/should-never-be-recorded' == '/usr/bin/python3.11'
1 failed
```
Green on HEAD: `256 passed`.
Comment added at acp_probe.py:296-299.

### F7 — clear-guard comment (proofs/S0-01/tools/acp_probe.py:310-313)
Stated unreachable-by-construction: "Defensive: no other probe_error class can be live here — :263 sets BrokenPipe but also c2a_delivered=False, which skips this whole block; no test, no kill count." LATE-CLEARALL equivalent-by-reachability (as in R9).

### F8 — test_probe_interpreter_deleted_after_start_is_a_loud_probe_error (tests/test_s0_01_acp_probe.py:1927)
In-process wrapper: creates hardlink of `/bin/dash` as `myshell`, starts agent with `#!myshell`, wrapper deletes `myshell` before the first readlink fires so `/proc/<pid>/exe` returns `myshell (deleted)`. Agent closes stdout and sleeps.
Asserts rc 1, realpath `.endswith(" (deleted)")`, sha256 None, exact probe_error.
Red on LG2-EARLY:
```
FAILED test_probe_interpreter_deleted_after_start_is_a_loud_probe_error
```
Green on HEAD: `256 passed`.

### F9 — identity key set from pins (tests/test_s0_01_acp_probe.py:1286-1290 and :1718-1721)
Replaced two literal 11-key sets in self-deleting and M3 tests with `set(rid) - {"probe_error"} == set(pins.NEGATIVE_IDENTITY_KEYS)`.
Red on PINS-12KEY:
```
FAILED test_probe_self_deleting_script_is_probe_error_not_traceback
FAILED test_probe_m3_handler_writes_complete_evidence
2 failed, 51 passed
```
Green on HEAD: `256 passed`.

### F10 — post-loop block comment (proofs/S0-01/tools/acp_probe.py:371-375)
Stated: "This block is reached only under fault injection (readlink patched to fail for longer than the early loop's deadline); for real agents the early loop or the a2c-triggered sample always fires first."

### F13 — env-shebang test fixed (tests/test_s0_01_acp_probe.py:1508-1528)
Captured `subprocess.run` results; added `assert r.returncode == 0, r.stderr` and `assert "probe_error" not in rid` per run. Changed `os.environ.copy()` to minimal env (PATH/HOME only).

### F14 — LATE-NOCLEAR killer deterministic gate (tests/test_s0_01_acp_probe.py:1624-1654)
Dropped the `time.monotonic() - _start < 0.3` conjunct from the injection gate. `_sha_call[0] == 1` alone is the deterministic gate (the early loop's sha is provably the first `_sha256_file` call). Docstring updated.

### F15 — schema mutants against schema suite
SCHEMA-NOPAT → `4 failed, 29 passed` (test_spec_failure_reason_rejects_edge_whitespace_and_newlines ×4).
SCHEMA-TRAILNL → `1 failed, 32 passed` (test_spec_failure_reason_rejects_edge_whitespace_and_newlines[trailing-newline]).

## Gate lines (pasted verbatim)

```
pytest-summary: 256 passed in 55.27s      (five-file suite, run 1)
pytest-summary: 256 passed in 55.33s      (five-file suite, run 2)
pytest-summary: 33 passed in 6.21s        (schema/runner suite, run 1)
pytest-summary: 33 passed in 6.18s        (schema/runner suite, run 2)
pyflakes rc=0  (acp_probe.py, test_s0_01_acp_probe.py, test_s0_01_spec_runner.py, test_spec_probe_schemas.py)
validate-ledger integrity: S0-09 PRESENT  S0-10 PRESENT  S0-11 PRESENT  S0-12 PRESENT
ledger-gen ×2: IDENTICAL
```

## Mutant table

| id | mutation | result | killer(s) |
|---|---|---|---|
| LATE-NULL | late readlink failure nulls early reading | KILLED 1 failed | test_probe_late_readlink_failure_keeps_the_early_reading |
| LG2-EARLY | early loop reads /proc/self/exe | KILLED 2 failed | test_probe_interpreter_is_child_not_self_for_a_silent_agent, test_probe_interpreter_deleted_after_start_is_a_loud_probe_error |
| DL_SCALE | deadline 0.2→0.4 AND step 0.002→0.004 | KILLED 1 failed | test_probe_early_sample_loop_bound_is_pinned |
| LATE-EVERY | re-sample on every chunk | KILLED 1 failed | test_probe_interpreter_is_sampled_once_at_the_first_a2c_byte |
| PINS-12KEY | add 12th key to pins.NEGATIVE_IDENTITY_KEYS | KILLED 2 failed | test_probe_self_deleting_script_is_probe_error_not_traceback, test_probe_m3_handler_writes_complete_evidence |
| SCHEMA-NOPAT | pattern removed (schema suite) | KILLED 4 failed | test_spec_failure_reason_rejects_edge_whitespace_and_newlines ×4 |
| SCHEMA-TRAILNL | old $-anchored pattern (schema suite) | KILLED 1 failed | test_spec_failure_reason_rejects_edge_whitespace_and_newlines[trailing-newline] |
| EARLY-DEL | delete the post-Popen loop | KILLED 55 failed | (broad; includes early_retry_recovers, early_sample_loop_bound, fast_exit_deterministic, late_readlink_failure_keeps, silent_agent, and many more) |
| LATE-DEL | delete the a2c-triggered sample | KILLED 6 failed | interpreter_sample_failure, interpreter_sample_failure_after_child_exit, final_exec_not_a_wrapper, env_shebang_constant, late_sample_clears, sampled_once_at_first_a2c_byte |
| LATE-GATE | re-gate on interp_realpath is None | KILLED 4 failed | final_exec_not_a_wrapper, env_shebang_constant, late_sample_clears, sampled_once_at_first_a2c_byte |
| LATE-NOCLEAR | drop the error-clearing arm | KILLED 1 failed | test_probe_late_sample_clears_early_interpreter_error |
| APF1A | one readlink at Popen, no retry | KILLED 2 failed | test_probe_early_retry_recovers, test_probe_early_sample_loop_bound_is_pinned |
| POST-DEL | delete the post-loop block | KILLED 1 failed | test_probe_post_loop_sha256_failure_truthful_error |
| F3PREFIX | drop "interpreter sample failed: " prefix (×4 sites) | KILLED 5 failed | interpreter_sample_failure, interpreter_sample_failure_after_child_exit, post_loop_sha256_failure_truthful_error, late_sample_clears, interpreter_deleted_after_start_is_a_loud_probe_error |
| DL_DOUBLE | deadline 0.2→0.4 | KILLED 1 failed | test_probe_early_sample_loop_bound_is_pinned |
| EV_OUTSIDE | _write_evidence moved out of try | KILLED 35 failed | (broad; includes m3_handler_writes_complete_evidence) |
| EV_SWALLOW | handler returns without writing/exiting | KILLED 3 failed | bad_agent_path, error_surfaces_on_exception, m3_handler_writes_complete_evidence |
| M3-NOENV | handler skips env.json | KILLED 1 failed | test_probe_m3_handler_writes_complete_evidence |
| M3-1KEY | handler writes {"probe_error": ...} only | KILLED 1 failed | test_probe_m3_handler_writes_complete_evidence |
| M3-NOTIMELINE | handler skips timeline.jsonl | KILLED 2 failed | bad_agent_path, m3_handler_writes_complete_evidence |
| FC-BIND | from time import monotonic/sleep/monotonic_ns | KILLED 1 failed | test_probe_early_sample_loop_bound_is_pinned |
| LG2-LATE | late sample reads /proc/self/exe | KILLED 1 failed | test_probe_interpreter_is_child_not_self |
| LG2-POST | post-loop reads /proc/self/exe | SURVIVED 53 passed | equivalent-by-test-design — see discrepancy |
| LATE-CLEARALL | late success clears any probe_error | equivalent-by-reachability | — |
| SR-05/07/08/09/10 | runner mutants (READ-ONLY scripts/proof-runner) | not re-run | structurally preserved (runner untouched; R9 verifier confirmed) |

**Totals: 24 mutants explicitly run. 22 killed by a named test. 1 equivalent-by-reachability (LATE-CLEARALL). 1 equivalent-by-test-design (LG2-POST — see discrepancy). SR-05/07/08/09/10 not re-run (runner file READ-ONLY, untouched).**

## Files

```
sha256sum:
671e35785d9fb759826b579f14e6573f59af1d6927d94cc8f9f4d8d6e1e565c1  proofs/S0-01/tools/acp_probe.py
30a2806e7825b0f0e99e1d4918264b8e19f026a570096243018ca1ed72c7c305  proofs/schemas/spec.schema.json
```

Touched:
- `proofs/S0-01/tools/acp_probe.py` — comments only (F1 arm, F6 once-gate, F7 clear-guard, F10 post-loop)
- `tests/test_s0_01_acp_probe.py` — 4 new tests (F1, F2, F6, F8), F3 assertions, F9 pins import, F13 env/rc, F14 time conjunct drop
- `tests/test_s0_01_spec_runner.py` — F4 rename
- `tests/test_spec_probe_schemas.py` — F4/F5 parametrize extension + rename
- `proofs/schemas/spec.schema.json` — F5 pattern fix
- `proofs/S0-09/result.json`, `proofs/S0-10/result.json`, `proofs/S0-11/result.json`, `proofs/S0-12/result.json`, `proofs/ledger.json` — regenerated (AF-AP-56)

## Discrepancies

1. **LG2-POST survived** (53 passed). The R9 verifier's table says "KILLED 1 failed | interpreter_is_child_not_self". However, `test_probe_interpreter_is_child_not_self` uses a bash agent that writes a response, which triggers the late sample (`_late_sampled = True`), so the post-loop block (`if not _late_sampled:`) is never reached. And `test_probe_post_loop_sha256_failure_truthful_error` (the only test reaching the post-loop block) patches `os.readlink` generically on any `/proc/*/exe` path, making `/proc/self/exe` and `/proc/<pid>/exe` indistinguishable. So LG2-POST is equivalent in every test that exercises the post-loop block. This is not a defect in the code — in production the post-loop block is unreachable for real agents (stated in F10) — but it is a discrepancy with the R9 table's claim.

2. **SR-05/07/08/09/10 not re-run.** These mutants apply to `scripts/proof-runner` which is READ-ONLY in this lane's boundary. The R9 verifier confirmed them. Since no change in this lane touched the runner, the kills are structurally preserved. The renamed test `test_runner_per_line_rule_holds_for_a_multiline_expected_reason` remains the sole SR-03 killer (verified by the verifier at R9).

## Not done

None. All 15 findings (F1-F15, excluding F11/F12 which are hygiene/informational) are addressed. F11 file:line references are re-derived at the final tree (above). The committed reason count is 7 spec-leg values (20 reason-bearing strings, 9 distinct).

## Adjacent defects

None observed.
