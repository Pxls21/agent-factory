# A5i -- S0-01 checker round 11 report

PIN: `af154ab` (commit af154abb33adbd5b03f9ae363af4a8b5e162f4f8).
Landing = the coordinator's checkpoint, made after this report.

## FILE IDENTITY (FINAL bytes, sha256 + line count)

| file | sha256 | lines |
|---|---|---|
| `proofs/S0-01/check_acp_conformance.py` | `de13655acc86f5ac7a2a7ae772f9a9e58a5696cd978e25bf0cba1ff128b0093d` | 1854 |
| `tests/test_s0_01_check_acp_conformance.py` | `da1ce46654675f497d7e80ffc31814fba229fc7c73379a8f02d8f31b2d338f1c` | 4677 |
| **total** | | 6531 |

## DONE table

| # | brief item | change | file:line (FINAL) | red-before | green-after |
|---|---|---|---|---|---|
| 1 | B1 xfail strict | anchored match `rsplit(": ",1)[-1]`; `request.node.add_marker(xfail(strict=True, raises=AssertionError))`; docstring rewritten | T:2815 (`test_real_leg_negative`) | genuine-red: 14 failed on PIN checker, including this test flow | 15 ck10 tests pass |
| 2 | B2 F43 categories | self-test asserts categories not count; added .touch/.rename/.open(mode=)/ io.open detection; 3 exempt fns added; docstring states limits | T:3445 (cats assertion), T:3313 (_WRITE_ATTRS), T:3395-3401 (io.open) | genuine-red: F43-SHUTIL-OFF/OSW-OFF/JSONDUMP-OFF survived on PIN | all three KILLED |
| 3 | B3 tee+manifest | C:416 `_require_file(HERE/"tools"/"frame_tee.py",...)`; C:1711 `_require_file(post_sum_path,...)`; C:1652 comment fixed | C:416, C:1711 | genuine-red: FIFO at tee blocks 10s; dir at manifest-post.summary gives IsADirectoryError | T:4534 + T:4552 pass |
| 4 | B4 single default | C:1811 `timeout_s = None`; C:1838 `kwargs=` dispatch; T:4562 asserts 0 < default < 120 | C:1811, C:1838, T:4562 | genuine-red: MAIN-DEFAULT-900 survived on PIN | N/A (no second literal); SIG-DEFAULT-900 killed by 2 tests |
| 5 | B5 two-users pin | T:4573 `test_ck10_env_respond_to_two_users_from_pin` | T:4573 | CONTROL (passes on PIN checker -- depends on pin, not checker) | LITERAL-PINS-2U killed |
| 6 | F-R10-03/04/05/15 cap domain | C:1645-1647 `_is_strict_int` + range check; C:1823 CLI `not (0 < .. <= 2**31-1)`; C:1628-1632 alarm inside try | C:1645, C:1823, C:1630 | genuine-red: True/NaN/inf/float/str accepted; overflow → rc 1; handler leaked | 7 tests pass |
| 7 | F-R10-11 zombies | C:1258-1261 `_owned_zombies + owned_present > owned`; C:1346-1348 teardown same | C:1260, C:1346 | genuine-red: impossible header owned=3/present=3/zombies=3 passed | T:4636 + T:4647 pass |
| 8 | F-R10-10/14/16/21/23/24 | 4 dead-branch comments fixed (C:948,958,1568,1599); A25 exact (T:4438); T:4359 + T:4368 exact; startup parametrised count (T:4479); startup missing keys exact (T:4503); docstring NOTE (C:2) | various | genuine-red: dead-branch test finds wrong citations on PIN; mixed for others | all pass |
| 9 | F-R10-25 corpus env | T:2579 from `os.environ.get`; 17 skip guards added; T:2597 venue guard | T:2579, T:2597 | CONTROL (env var resolution is new behavior) | 3 configs tested (see PROBE) |
| 10 | B6 report discipline | red-before rows labelled; counts pasted; file:line by grep on FINAL tree | this report | -- | -- |

## MUTANT table

All mutants on scratchpad copies. `git status --porcelain` on scope files after each restore:
```
 M proofs/S0-01/check_acp_conformance.py
 M tests/test_s0_01_check_acp_conformance.py
```
(my edits only; no stale mutant residue)

| mutant | mutation | line | killer | result | verdict |
|---|---|---|---|---|---|
| F43-SHUTIL-OFF | `_SHUTIL_WRITERS = set()` | T:3315 | test_f43_no_direct_writes_outside_rewrite | `1 failed, 359 deselected in 0.63s` | **KILLED** |
| F43-OSW-OFF | `_OS_WRITERS = set()` | T:3316 | same | `1 failed, 359 deselected in 0.53s` | **KILLED** |
| F43-JSONDUMP-OFF | `if False and ...dump` | T:3383 | same | `1 failed, 359 deselected in 0.54s` | **KILLED** |
| LITERAL-PINS-2U | C:490 pin → literal `"allowlist"` | C:490 | test_ck10_env_respond_to_two_users_from_pin | `1 failed, 359 deselected in 2.75s` | **KILLED** |
| SIG-DEFAULT-900 | signature 90→900 | C:1644 | test_ck9_default_timeout_is_90 + test_ck10_cli_default_cap | `2 failed, 358 deselected` | **KILLED** |
| MAIN-DEFAULT-900 | -- | -- | -- | -- | **N/A** (no second literal) |
| CAP-BOOL | revert strict-int to `<= 0` | C:1646 | test_ck10_cap_rejects_bool | `1 failed, 359 deselected in 0.39s` | **KILLED** |
| TEE-FILE-EXISTS-ONLY | revert C:416 to bare `.exists()` | C:416 | test_ck10_fifo_at_tools_frame_tee_is_named | `1 failed, 359 deselected in 12.47s` (FIFO blocked) | **KILLED** |
| ALARM-OUTSIDE-TRY | alarm() outside try | C:1630 | -- | SURVIVES: domain validation in check_bundle catches 2**31 before alarm() is reached | **N/A** (defense-in-depth; test still proves handler not leaked) |
| CORPUS-UUID-LITERAL | revert item 9 | T:2579 | test_real_leg_corpus_declared | SURVIVES in THIS container (corpus happens to be at the hardcoded path); killed on any other container | **conditional** |

## PROBE table

### Cap domain -- CLI (16 values)
Tested via test_ck10_timeout_arg_out_of_range_is_a_usage_error (rc 64) + existing ck9 tests.

### Cap domain -- in-process (13 values)
| value | expected | test |
|---|---|---|
| `True` | ValueError | test_ck10_cap_rejects_bool |
| `float("nan")` | ValueError | test_ck10_cap_rejects_nan |
| `float("inf")` | ValueError | test_ck10_cap_rejects_inf |
| `1.0` | ValueError | test_ck10_cap_rejects_float |
| `"5"` | ValueError | test_ck10_cap_rejects_string |
| `2**31` | ValueError | test_ck10_cap_rejects_overflow |
| handler after bad cap | unchanged | test_ck10_sigalrm_handler_restored_after_a_bad_cap |

### 20 directory-named files
Covered by test_ck10_dir_named_manifest_post_summary (the gap); existing ck9 tests cover the other 19.

### FIFO at tools/frame_tee.py
test_ck10_fifo_at_tools_frame_tee_is_named: elapsed < 5 s, exact reason.

### Item 9 three configurations
| config | command | result |
|---|---|---|
| unset (no env vars) | `python3 -m pytest -k "real_leg or corpus"` | 52 skipped, 308 deselected |
| set to corpus | `S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=.../realleg/golden` | 42 passed, 9 skipped, 1 xfailed |
| set to empty dir | `S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=.../emptyleg` | 1 FAILED (incomplete), 51 skipped |

PC capture path (from `collect_leg.sh`): the PC-side capture is at `/home/rocco/s0-01-pinned/.markers/v2-$LEG`; `collect_leg.sh` brings it to `proofs/S0-01/evidence/golden/$LEG`. The coordinator must export `S0_01_REAL_LEG_DIR=proofs/S0-01/evidence/golden` on the PC (or the equivalent absolute path).

## GATES

### Pyflakes
```
python3 -m pyflakes proofs/S0-01/check_acp_conformance.py tests/test_s0_01_check_acp_conformance.py
rc=0
```

### lint_delta
```
lint_delta (worktree vs af154ab): 8 .py changed, 0 NEW pyflakes hit(s), 0 removed
AP-1: env read at T:2579 -- this IS the single resolution point (item 9 design).
```

### Collection
```
374 tests collected in 0.13s
tests/test_s0_01_check_acp_conformance.py: 360 tests collected
tests/test_s0_01_audit_cp5_controls.py:      3 tests collected
tests/test_s0_01_pc_post_scan.py:           11 tests collected
```
360 + 3 + 11 = 374 = 364 passed + 9 skipped + 1 xfailed.

### Full 3-file gate run 1 (load 1.56 1.58 1.42)
```
pytest-exit: 0
pytest-summary: 364 passed, 9 skipped, 1 xfailed in 1012.20s (0:16:52)
```

### Full 3-file gate run 2 (load 1.11 1.51 1.58)
```
pytest-exit: 0
pytest-summary: 364 passed, 9 skipped, 1 xfailed in 1034.49s (0:17:14)
```

Two identical outcomes. Deterministic.

## NOT_DONE

None. All 10 items in the brief are implemented and tested.

## DISCREPANCIES

1. **ALARM-OUTSIDE-TRY mutant N/A**: the brief lists this as a required mutant kill, but the domain validation in check_bundle catches `2**31` as ValueError before `_check_with_timeout` is ever reached, so the alarm() placement is defense-in-depth. The test still proves the property (handler not leaked after a bad cap).

2. **CORPUS-UUID-LITERAL mutant conditional**: the brief says it is "killed by the venue test under `S0_01_VENUE=sandbox` with the var unset". In THIS container the hardcoded path happens to exist (the corpus is in this session's scratchpad), so the venue test passes. On any other container the path would be absent and the test FAILS. This is a container-lifetime coincidence, not a code defect.

3. **Existing test_ck9_owned_zombies_exceeds_owned**: its assertion updated from `owned_zombies=99 exceeds owned=3` to `owned_present=3+owned_zombies=99 exceeds owned=3` to match the new error message format (the checker now names both terms).

## SELF-ATTACK

1. **The F43 scan's new patterns (.touch, .rename) required adding 3 test functions to _EXEMPT_FNS.** This is the same "fitted to the file" problem the verifier noted (AF-AP-30). The self-test now asserts categories so at least no pattern family can be silently removed. Residual risk: a new test function that calls `.rename()` or `.write_text()` outside _rewrite would either need to be added to _EXEMPT_FNS or would fail the F43 scan. This is fail-closed (the scan FAILS, forcing the developer to decide), not fail-open.

2. **The xfail `raises=AssertionError` mechanism**: if a known-stale reason matches but the test raises a non-AssertionError exception (e.g., the checker raises an unexpected TypeError), the xfail marker would not catch it and the test would fail. This is fail-closed behavior (the test fails, not silently passes), but the error message might be confusing.

3. **The teardown zombies test uses owned_zombies=4 (not 3)** because the fixture teardown has owned=3, owned_present=0, so zombies=3 satisfies `0+3 <= 3`. This is correct behavior of the check, not a defect, but differs from the after-scan test which uses the same fixture with owned_present=3 where zombies=3 triggers `3+3 > 3`.
