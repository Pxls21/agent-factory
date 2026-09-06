# A5e REPORT — 21 killing tests for previously-unkilled checker guards

## PREMISE CHECK — PASS

HEAD: `1e67982` (PIN matches). 257 `raise Failure` sites confirmed. HEAD on top of `d9d0cf2` (checkpoint 8a).
Sandbox real-leg: `41 passed, 5 skipped` (matches brief).
PC suite: NOT run here — PC clone does not have HEAD `b84c1ac` (another lane committed after PIN `1e67982`; no push authority per brief boundary).

## CHECKER MODIFICATIONS

NONE. `proofs/S0-01/check_acp_conformance.py` is unchanged (257 Failure sites, same as PIN).

## TEST MODIFICATIONS (tests/test_s0_01_check_acp_conformance.py)

450 lines added (2740 → 3190). 21 new test functions, each prefixed `test_ck7_f*`.
`tests/test_s0_01_audit_cp5_controls.py` unchanged (no control reason changed).

## PER-GUARD TABLE (21 new killing tests)

| Guard | Line | Test | Exact red on mutant |
|---|---|---|---|
| F1: A24 ingress concurrency | C:892 | `test_ck7_f1_second_mention_after_first_terminal` | AssertionError: assert 0 == 1 (PASS on mutant, test expects Failure) |
| F2: A24 observed serialization | C:899 | `test_ck7_f2_second_session_new_before_first_terminal` | AssertionError: assert 0 == 1 |
| F3: A23 response cardinality | C:320 | `test_ck7_f3_duplicate_response_id` | AssertionError: assert 0 == 1 |
| F4a: A23 a2c agent request | C:302 | `test_ck7_f4a_a2c_agent_request` | AssertionError: assert 0 == 1 |
| F4b: A23 c2a client response | C:304 | `test_ck7_f4b_c2a_client_response` | AssertionError: assert 0 == 1 |
| F5: A23 response envelope | C:326 | `test_ck7_f5_invalid_response_envelope` | AssertionError: assert 0 == 1 (wrong jsonrpc triggers disabled first clause; second clause False for normal result/error) |
| F6a: A20b tee_pid ppid | C:1187 | `test_ck7_f6a_tee_pid_wrong_ppid` | Failure: tee_pid ppid not present (guard disabled) |
| F6b: A20b agent ppid | C:1195 | `test_ck7_f6b_agent_pid_wrong_ppid` | Failure: agent ppid not present (guard disabled) |
| F7a: teardown mode | C:1215 | `test_ck7_f7a_teardown_mode_mismatch` | Failure: not raised (guard disabled) |
| F7b: teardown rows=0 | C:1217 | `test_ck7_f7b_teardown_rows_zero` | Failure: not raised |
| F7c: teardown owned | C:1219 | `test_ck7_f7c_teardown_owned_mismatch` | Failure: not raised |
| F7d: teardown owned_present | C:1222 | `test_ck7_f7d_teardown_owned_present_mismatch` | Failure: not raised |
| F8a: write_errors | C:1272 | `test_ck7_f8a_tee_status_write_errors` | AssertionError: assert 0 == 1 |
| F8b: forwarded_a2c | C:1276 | `test_ck7_f8b_tee_status_forwarded_a2c_mismatch` | AssertionError: assert 0 == 1 |
| F8c: recorded_c2a | C:1280 | `test_ck7_f8c_tee_status_recorded_c2a_wrong` | AssertionError: assert 0 == 1 |
| F8d: updated_utc format | C:1288 | `test_ck7_f8d_tee_status_updated_utc_bad_format` | TypeError (utc_re.match(42) on mutant; `if False and isinstance` leaves non-string through) |
| F8e: final returncode | C:1299 | `test_ck7_f8e_tee_status_final_returncode_not_int` | AssertionError: assert 0 == 1 |
| F8f: not-final exit_code | C:1307 | `test_ck7_f8f_tee_status_not_final_exit_not_null` | AssertionError: assert 0 == 1 |
| F9a: golden request kinds | C:1365 | `test_ck7_f9a_golden_request_kinds` | Failure: not raised (guard disabled) |
| F9b: golden sessionId identity | C:1418 | `test_ck7_f9b_golden_same_session_ids` | AssertionError: assert 0 == 1 |
| F9c: golden first t_utc identity | C:1420 | `test_ck7_f9c_golden_same_first_tutc` | AssertionError: assert 0 == 1 |

## COMBINED MUTANT (24/24)

Combined 24-guard mutant (`if False and ...` on all 24 IF conditions), run against the killing tests:

```
21 ck7_f tests + test_proc_closure + test_orphan_pair + test_pc_launch_exemption:
24 failed, 1 passed, 235 deselected
(the 1 passed is test_proc_closure_seed, which tests a different check, not one of the 24 guards)
```

**24/24 guards each killed by a named test.**

## GATE

```
pyflakes: rc=0, no output (all 3 files)

sandbox real-leg: 41 passed, 5 skipped in 10.19s
sandbox broader subset (ck7_f + proc + v23 + tee_status + passing_v2 + audit_p1):
  48 passed, 212 deselected in 284.94s

PC lane suite: NOT run here — PC clone does not have HEAD b84c1ac
  (another lane committed b84c1ac after PIN 1e67982; this lane has no push authority;
   the coordinator must push and re-run the PC suite)

combined-mutant killing tests: 21 failed (all 21 new ck7_f tests RED), 0 passed
combined-mutant full 24-guard check: 24 failed, 1 passed (test_proc_closure_seed — not a guard test)
```

Temp footprint (sandbox 48-test subset): 1013 MB per run. Disk before: 22 GB free. After cleanup: 17 GB free.

## HOSTILE-BUNDLE TABLE

| Finding | Attack | Exact failure_reason |
|---|---|---|
| F1 | two-users user2 created_at after first terminal | `two-users: second mention not pending during the first turn` |
| F2 | two-users second session/new frame before first terminal | `two-users: second session/new precedes the first terminal` |
| F3 | duplicate a2c error response with same id before end_turn | `run-1: duplicate response for id <id> at seqs [<N>, <M>]` |
| F4a | a2c notification given an id (becomes agent request) | `run-1: a2c frame at seq <N> is an agent request (method=<M>)` |
| F4b | c2a request method removed (becomes client response) | `run-1: c2a frame at seq <N> is a client response (id=<id>)` |
| F5 | a2c terminal response jsonrpc set to "3.0" | `run-1: response at seq <N> is not a valid JSON-RPC envelope` |
| F6a | tee_pid ppid != buzz_acp_pid (intermediary tee) | `run-1: tee_pid 12340 ppid is not buzz_acp_pid` |
| F6b | agent_child_pid ppid != tee_pid (parented by buzz) | `run-1: agent_child_pid 12345 ppid is not tee_pid` |
| F7a | teardown header mode=after | `run-1: process-scan-teardown.txt header mode is 'after', expected 'teardown'` |
| F7b | teardown header rows=0 | `run-1: process-scan-teardown.txt header rows=0 (enumeration did not run)` |
| F7c | teardown header owned=1 (real: 3) | `run-1: process-scan-teardown.txt header owned=1 != owned-pids.json (3)` |
| F7d | teardown header owned_present=1 (body: 0) | `run-1: process-scan-teardown.txt header owned_present=1 inconsistent with body (0)` |
| F8a | tee-status write_errors non-empty | `run-1: tee-status.json write_errors is not empty` |
| F8b | tee-status forwarded_a2c = recorded_a2c - 1 | `run-1: tee-status.json forwarded_a2c != recorded_a2c` |
| F8c | tee-status recorded_c2a += 1 | `run-1: tee-status.json recorded_c2a <N+1> != timeline c2a count <N>` |
| F8d | tee-status updated_utc = 42 (non-string) | `run-1: tee-status.json updated_utc does not match format` |
| F8e | final=true, agent_returncode="zero" | `run-1: tee-status.json final but agent_returncode is not int` |
| F8f | final=false, exit_code=42 | `run-1: tee-status.json not final but exit_code is not null` |
| F9a | extra tools/list request in both runs | `golden: golden does not have exactly one of each request kind` |
| F9b | run-2 sessionId == run-1 sessionId everywhere | `golden: run-1 and run-2 raw sessionIds are identical` |
| F9c | run-2 first t_utc == run-1 first t_utc | `golden: run-1 and run-2 first t_utc are identical` |

## MUTANT DETAILS (combined `if False and` on 24 guard IF lines)

Guard IF lines (1-indexed): 302, 304, 320, 326, 892, 899, 1162, 1166, 1187, 1195, 1210, 1215, 1217, 1219, 1222, 1272, 1276, 1280, 1288, 1299, 1307, 1365, 1418, 1420.

## PROPOSED pins.py HUNK (F42)

Carried forward from A5d. The checker uses local literals for `mcp_cmd` ("") and `permission_mode` ("bypassPermissions") at C:1025,1031. The coordinator should add to `proofs/S0-01/pins.py`:
```python
PINNED_STARTUP_MCP_CMD = ""
PINNED_STARTUP_PERMISSION_MODE = "bypassPermissions"
```

## NOT-DONE

| Item | Reason |
|---|---|
| F22-F26 checker fixes | Upstream POST body key pinning, GET fingerprint check, startup exact-match, mention_pubkeys exact set — not implemented (brief item 2). |
| F30 after-scan duplicates | Not added (brief item 3). |
| F14 full rid-pid binding | Not expanded beyond buzz_pid (brief item 3). |
| F36-F38 substring assertions | 13 `in`/`startswith` reason assertions remain (brief item 4). |
| F39 assertion counter | `_asserted()` not implemented (brief item 5). |
| F40-F41 dead presence gates | Not deleted or converted (brief item 5). |
| F34-F35 tee-status fixture binding | Not implemented (brief item 6). |
| F42 pins.py constants | Coordinator-owned file. Hunk provided above (brief item 6). |
| F43 disk reduction | Not implemented; copytree still in use (brief item 7). |
| PC lane suite | NOT run here — PC clone does not have HEAD b84c1ac. |

## FILES

- `/home/user/agent-factory/proofs/S0-01/check_acp_conformance.py` — 0 changes
- `/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py` — 450 insertions (21 new test functions)
- `/home/user/agent-factory/tests/test_s0_01_audit_cp5_controls.py` — 0 changes

## DISCREPANCIES

- HEAD moved to `b84c1ac` after PIN `1e67982` (another lane committed). My changes are in the working tree on top of `b84c1ac`, but the checker at HEAD is byte-identical to `1e67982` (I did not modify it).
- The combined mutant's `if False and X or Y` pattern for guards with `or` clauses (F5 at C:326, F8d at C:1288) only disables the first clause. The killing tests were designed to trigger the disabled first clause specifically: F5 uses wrong jsonrpc (not both result+error), F8d uses a non-string value (not a bad-format string).
- `test_proc_closure_seed` matched the combined-mutant filter but tests a DIFFERENT check (C:1175 "no tee process parented by buzz-acp"), not one of the 24 disabled guards. It correctly passed on the mutant.

## ADJACENT DEFECTS (report only)

- F6a/F6b guards at C:1187-1188 and C:1195-1196 are reachable ONLY when the structural tee/agent checks pass first (C:1174-1178). A hostile bundle that changes ONLY the rid tee_pid's ppid also breaks the closure check (C:1162) which fires first. The killing tests use multi-process scans (two tees or two agents) so the structural checks pass while the identity binding fails. This is the CORRECT attack but means these guards are defense-in-depth behind the structural checks.
- The `or` in guards at C:326 and C:1288 means `if False and` is not a complete mutation. A proper mutation audit of these guards would use `if False:` with an unconditional pass, not `if False and <original>`.

## SELF-ATTACK

1. **Most likely wrong: PC suite not run.** The 202-passed baseline was not re-verified. Another lane's commit (`b84c1ac`) may have broken something. The coordinator must push and run the PC suite to confirm.

2. **Most likely wrong: F6a/F6b test isolation.** These tests call `check_process_evidence` directly, not `check_bundle`. They prove the guard fires in isolation but do not prove the attack reaches the guard through the full bundle flow. The multi-process scan approach is correct but adds complexity a verifier must understand.

3. **Most likely wrong: F3 assertion depends on fixture structure.** The duplicate response id and seq numbers in the assertion depend on the exact synthetic timeline. A fixture change could break the assertion. Mitigated by computing expected values from the timeline at test time.
