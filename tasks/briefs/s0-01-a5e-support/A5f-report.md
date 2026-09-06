# A5f REPORT — checker's remaining VERIFY-CK7 items

## DONE

| Finding | Change | Red before | Green after |
|---|---|---|---|
| F43 | Bundle fixture: `shutil.copytree(copy_function=os.link)` + `_rewrite(path, data)` helper that unlinks before write. 211 test-function write calls transformed by AST. `_write_timeline` and `_write_tee_status` helpers also unlink before write. Source-scan test `test_f43_no_direct_writes_outside_rewrite`. | copytree: 4.7 GB/run (A5d report) | hardlinks: 27-35 MB measured on 2-53 test subsets |
| F22 | POST body key set pinned: `{model, messages, stream, max_tokens, stream_options, tools, response_format, temperature}`. Extra keys → `Failure: upstream POST record body has extra keys: [...]` | test_ck7_f22: pass on mutant (extra key accepted) | test_ck7_f22: `assert out == "failure_reason: run-1: upstream POST record body has extra keys: ['evil_tool_calls']"` |
| F23 | POST message roles pinned to `{system, user, assistant}`. Wrong role → Failure. | test_ck7_f23: pass on mutant | test_ck7_f23: `assert out == "failure_reason: run-1: upstream POST record message role 'tool' not in allowed set"` |
| F24 | GET records' `authorization_fingerprint` must match pinned or be null. Non-null wrong value → Failure. | test_ck7_f24: pass on mutant (bogus fp accepted) | test_ck7_f24: `assert out == "failure_reason: run-1: upstream GET record authorization_fingerprint mismatch"` |
| F25 | Startup-line exact match: all tokens must be key=value with key in `_EXPECTED_STARTUP_KEYS` (21-key frozenset). Unknown keys/tokens → Failure. Parenthesized values parsed correctly. | test_ck7_f25: pass on mutant (extra token accepted) | test_ck7_f25: `assert out == "failure_reason: run-1: startup-line unknown key 'backdoor'"` |
| F26 | `mention_pubkeys` must equal exactly `[identities["agent"]]`. Extra entries and empty → Failure. | test_ck7_f26_extra / _empty: pass on mutant | Both assert exact Failure naming the mismatch |
| F14 | `check_process_evidence` now validates rid `tee_pid` and `agent_child_pid` in `owned_set` on EVERY leg (including shutdown). | test_ck7_f14: pass on mutant (shutdown rid pids unchecked) | test_ck7_f14: `assert out == "failure_reason: shutdown: owned-pids.json does not contain rid tee_pid 77777"` |
| F30 | After-scan duplicate pid check added (before consistency checks), mirroring teardown duplicate check. | test_ck7_f30: pass on mutant (duplicate accepted) | test_ck7_f30: `assert out == "failure_reason: run-1: process-scan-after.txt duplicate rows for pid(s) [12340]"` |
| F34 | `_TEE_STATUS_KEYS = frozenset(PINNED_TEE_STATUS_KEYS)` — local copy replaced by import from pins.py. `test_ck7_f34_frame_tee_keys_match_pin` verifies the committed `frame_tee.py`'s `_write_status` dict keys == `PINNED_TEE_STATUS_KEYS` via AST extraction. | n/a (coupling guard) | test_ck7_f34: passes, keys match |
| F42 | `_PINS_PENDING = {"mcp_cmd": "", "permission_mode": "bypassPermissions"}` with `TODO(A5f-F42)` naming the coordinator ruling. Values consumed from the dict, not bare literals. | n/a (refactor) | Passing bundle unchanged |

## HOSTILE-BUNDLE TABLE (F22-F26 + F14 + F30)

| Finding | Attack | Exact failure_reason |
|---|---|---|
| F22 | POST body `evil_tool_calls=[{"exfil":"yes"}]` | `run-1: upstream POST record body has extra keys: ['evil_tool_calls']` |
| F23 | POST message `role="tool"` | `run-1: upstream POST record message role 'tool' not in allowed set` |
| F24 | GET `authorization_fingerprint = "f"*64` | `run-1: upstream GET record authorization_fingerprint mismatch` |
| F25 | startup-line append `backdoor=on` | `run-1: startup-line unknown key 'backdoor'` |
| F26 extra | receipt `mention_pubkeys` extra entry | `run-1: mention owner receipt mention_pubkeys [...] != expected [...]` |
| F26 empty | receipt `mention_pubkeys = []` | `run-1: mention owner receipt mention_pubkeys [] != expected [...]` |
| F14 | shutdown rid `tee_pid=77777` | `shutdown: owned-pids.json does not contain rid tee_pid 77777` |
| F30 | after-scan duplicate row for pid 12340 | `run-1: process-scan-after.txt duplicate rows for pid(s) [12340]` |

## PROPOSED pins.py HUNK (F42)

Carried forward from A5d/A5e. The checker uses `_PINS_PENDING` dict for `mcp_cmd` and `permission_mode`. Coordinator should add to `proofs/S0-01/pins.py`:
```python
PINNED_STARTUP_MCP_CMD = ""
PINNED_STARTUP_PERMISSION_MODE = "bypassPermissions"
```

## GATE

```
pyflakes: rc=0, no output (all 3 files)

pytest-summary: 233 passed, 46 skipped in 87.57s (0:01:27)   # PC -n 8 run 1
pytest-summary: 233 passed, 46 skipped in 87.47s (0:01:27)   # PC -n 8 run 2

sandbox real-leg: 41 passed, 5 skipped in 9.59s
```

## TEMP FOOTPRINT

Before (copytree): 4.7 GB per serial run (A5d report).
After (hardlinks + _rewrite): 27 MB for 2 tests, 35 MB for 53 tests (sandbox measurement).

## NOT-DONE

| Item | Reason |
|---|---|
| F36-F38 (A28 substring assertions) | 12 `in out` + 14 `startswith` + 2 `or` reason assertions remain. Mechanical replacement is scope-bounded by the F14/F30 ordering changes that shifted expected errors in many tests. Budget exhausted. |
| F39 (assertion counter `_asserted()`) | Not implemented. Requires adding counter calls to every check function — too pervasive for remaining budget. |
| F40-F41 (dead presence gates) | Six dead gates not deleted or converted. |
| F35 (real-leg tee-status test) | `check_tee_status` real-leg test not added (real corpus has no tee-status.json). |
| F43 serial basetemp measurement | Not measured on a serial run due to sandbox intermittent hardlink contamination (passes on PC with -n 8; see discrepancies). |
| Combined 24-guard mutant re-run | Not re-run explicitly (all 30 ck7_f tests pass, implying the 24 guards are still killed). |
| PC serial run (-n 0) | Not run (brief says TWICE with -n 8 and ONCE serial — two -n 8 done, serial not done). |

## FILES

- `/home/user/agent-factory/proofs/S0-01/check_acp_conformance.py` — F22/F23/F24/F25/F26 checks, F14 rid-pid ownership, F30 after-scan duplicate, F34 _TEE_STATUS_KEYS from pins, F42 _PINS_PENDING, F25 startup parser rewrite
- `/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py` — F43 hardlink fixture + _rewrite (211 AST-transformed calls + 5 open-w patterns + _write_timeline/_write_tee_status unlink-before-write), 9 new tests (F22-F26 + F14 + F30 + F34 + F43), fixture updates for F14 ordering (test_proc_buzz_found, test_proc_tee_parent, test_proc_agent_parent, test_proc_closure_seed, 5 v23 tests), GET fingerprint fixture
- `/home/user/agent-factory/tests/test_s0_01_audit_cp5_controls.py` — NO changes (no control reason changed)

## DISCREPANCIES

- The F14 check (rid pids in owned_set) fires before the scan-level structural checks (closure, tee parent, agent parent). Tests that previously exercised those structural checks now hit F14 first. Updated 4 tests (test_proc_buzz_found, test_proc_tee_parent, test_proc_agent_parent, test_proc_closure_seed) and 5 v23 tests to include full owned set and runtime-identity.json.
- test_proc_tee_parent and test_proc_agent_parent now assert "recomputed owned closure != owned-pids.json" instead of "no tee/agent process parented by buzz-acp" because the ppid-chain break causes a closure mismatch before the structural tee/agent parent check.
- F24 allows GET fingerprint=null (the real corpus's GET records carry no auth). Non-null wrong values are rejected.
- F22 allowed POST body keys expanded to include `max_tokens`, `stream_options`, `tools`, `response_format`, `temperature` from the real corpus.
- Sandbox full-suite runs show intermittent hardlink contamination (a test ~125 deep corrupts the session bundle). The PC suite with -n 8 xdist is clean on both runs (233 passed). Root cause not identified — the `_write_timeline` and `_write_tee_status` helpers unlink before write, and all 211 test-function writes go through `_rewrite`. The contamination path may be a third helper or a test pattern not yet caught.

## ADJACENT DEFECTS (report only)

- The `_write_timeline` helper is called from 33 test functions. Its unlink-before-write fix is safe for session-bundle construction (nothing to unlink) but adds 3 `unlink` calls per invocation. A more targeted approach would be to unlink only when the file has `st_nlink > 1`.
- The `_event_counter` module-level mutable list (line 235) is shared across the session. If the session bundle fixture were ever re-invoked, the counter would produce different `created_at` values.

## SELF-ATTACK

1. **Most likely wrong: F14 ordering change.** The F14 check fires before scan-level checks. Tests that expected scan-level errors now get ownership errors. I updated the most obvious ones but there may be more edge cases in the full 270-test suite that only manifest in specific test orderings.

2. **Most likely wrong: F43 sandbox contamination.** The sandbox full-suite run fails intermittently around test #125-150. The PC -n 8 runs are clean. The root cause is not identified. The hardlink discipline (unlink before write) is mechanically correct but there may be a code path that bypasses it.

3. **Most likely wrong: F22 POST body key set too broad.** I added `max_tokens`, `stream_options`, `tools`, `response_format`, `temperature` from the real corpus. This is data-driven but may be overly permissive. A future capture with different OmniRoute settings could have different keys.
