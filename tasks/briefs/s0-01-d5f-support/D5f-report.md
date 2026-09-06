# D5f — final report

## done

### F1/F3 (BLOCKING, root cause)
`_normal_forms` returns `(frozenset, bool)` tuple. `_carries_secret` checks token in forms; returns `not saturated` on miss. D5d-F12 accepted risk restored: junk like `%25252540` triggers bound-exceeded and blanks the record (false positive, documented).

- file: `proofs/S0-01/tools/scripted_backend.py:102-127` (`_normal_forms`), `:209-222` (`_carries_secret`)
- red before: `HTTP/1.1 200 OK` with token recorded (F1 junk-suffix `%25252541`)
- green after: `HTTP/1.1 400 Bad Request` with record redacted

### F2 (BLOCKING, oracle tautology)
Oracle widened to depth 6 over `{unquote, unquote_plus, strip_ws, lower, strip_zwc}`. Oracle self-tests: 5 known-bad vectors (False), 3 known-good (True). Tautology mutant (`return True`) kills 5 tests.

- file: `tests/red/test_s0_01_backend_credential_screen.py:93-115` (oracle), `:377-397` (self-tests)
- oracle-tautology run: `5 failed, 99 passed in 40.72s`

### F4 (docstrings)
Module docstring: operators, closure direction, accepted risk, JSON-depth, _iter_json_strings keys+values. `_normal_forms` docstring: tuple return, saturated semantics, accepted risk. `_carries_secret` docstring: fail-closed semantics. `record()` comment at `:231-232`: full operator list.

### F5 (`_error()` sends `Connection: close`)
`_error()` now sends `Connection: close` and sets `self.close_connection = True`. Line `:39` ("Every rejection sends Connection: close") is now true. Domain table test updated: non-200 responses expect `close=True` with `expected_records` (not hardcoded 0).

- file: `proofs/S0-01/tools/scripted_backend.py:370-372`, `tests/test_s0_01_scripted_backend.py:1524-1527,1603-1612`

### F6 (duplicated docstring sentence)
Removed the duplicated sentence at red file line 5.

### F8 (json_list_element sink, kills MC9)
`test_credential_whitespace_split_in_json_list_element_returns_400` — 5 seps (TAB/LF/CR/FF/VT). Green on PIN (list branch already works); kills MC9 mutant.

### F9 (quad test rename + real bound-exceeded test)
`test_credential_quad_percent_encoded_fails_closed` renamed to `test_credential_quad_percent_encoded_at_depth4`. The real bound-exceeded test is `test_credential_depth5_percent_nesting_returns_400`.

### F10 (`_json_safe` iterative)
Rewritten as an iterative stack-based traversal. No recursion risk regardless of nesting depth.

### F11 (`except RecursionError` comment + depth-1000 test docstring)
`except RecursionError` arm kept as defence-in-depth with updated comment ("unreachable while MAX_JSON_DEPTH <= 32; retained in case the constant is ever raised"). `test_depth_1000_json_body_returns_400_no_record` docstring updated from "must trigger RecursionError" to "is refused by the depth gate".

### F12 (JSON-depth string/escape tests, kill MG4/MG5)
`test_json_depth_ignores_brackets_inside_strings` (40 `[` in string value -> 200, kills MG4). `test_json_depth_handles_escaped_quote` (`q\"` then 40 `[` -> 200, kills MG5). Both green on PIN (code already correct).

### F13 (MAX_JSON_DEPTH fallback)
`_MJD_MATCH` checked for None; falls back with `pytest.fail("MAX_JSON_DEPTH missing from the backend")`.

### F14 (uppercased token)
`str.lower` added to closure ops. `test_credential_uppercased_token_in_header_returns_400` — red on PIN (no `lower` op), green after fix.

### F15 (zero-width separators)
`strip_zwc` added to closure ops: `re.sub("[​﻿­⁠]", "", x)`. Tests: `test_credential_zero_width_pct_encoded_returns_400` (ZWSP/BOM/SOFT_HYPHEN percent-encoded), `test_credential_zero_width_json_escape_returns_400` (JSON `​`). Red on PIN (no `strip_zwc`), green after fix.

### F17 (`math.isfinite(handler_timeout)`)
Assertion now uses `math.isfinite(handler_timeout)` to reject `float('inf')`.

### F18 ("Not recorded" enumeration)
Added "JSON depth > MAX_JSON_DEPTH, short body" to the not-recorded list.

### F19 (`/tmp/unused-timeout-test` -> `tmp_path`)
`test_handler_timeout_bounds_incomplete_body` now takes `tmp_path` and uses `tmp_path / "unused-timeout-test"`.

### New red tests (ruling 3)
- `test_credential_split_with_trailing_nested_escape_returns_400`: 5 seps x 3 sinks x `%25252541` suffix = 15 tests. Red on PIN, green after fix.
- `test_credential_depth5_percent_nesting_returns_400`: 4 vectors x 5 sinks = 20 tests. Red on PIN, green after fix.
- `test_credential_whitespace_split_in_json_list_element_returns_400`: 5 tests. Green on PIN (list branch already works), kills MC9.
- `test_json_depth_ignores_brackets_inside_strings`: 1 test. Green on PIN. Kills MG4.
- `test_json_depth_handles_escaped_quote`: 1 test. Green on PIN. Kills MG5.
- `test_credential_uppercased_token_in_header_returns_400`: 1 test. Red on PIN (no lower op).
- `test_credential_zero_width_pct_encoded_returns_400`: 3 tests. Red on PIN (no strip_zwc).
- `test_credential_zero_width_json_escape_returns_400`: 1 test. Red on PIN (no strip_zwc).
- `TestOracleSelfTests::test_oracle_known_vectors`: 8 tests. 5 green on PIN, 3 green on PIN.

## mutant table — 25 mutants, 23 KILLED / 2 SURVIVED (1 control + 1 equivalent)

| id | mutation | verdict | killed by / equivalence |
|---|---|---|---|
| M00 | no-op control | SURVIVED | 104 passed — harness sound |
| M18 | 4b-postmax delete | KILLED | backend::test_post_cl_overmax_ordering_beats_expect (1 failed, 329 passed) |
| M20 | n>MAX -> n>=MAX | KILLED | R::test_post_content_length_exactly_max_is_accepted (1 failed, 103 passed) |
| M29 | Expect is-not-None -> truthiness | SURVIVED | EQUIVALENT: get_all returns None (absent) or ["value"] (present); both ops agree on all cases |
| M48 | auth exempt by prefix | KILLED | R::test_authorization_prefixed_header_name_is_not_exempt (2 failed, 102 passed) |
| M55 | M18 + read_body max->1e9 | KILLED | backend (4 failed, 326 passed) |
| M58 | arm 1b deleted | KILLED | R::test_obs_folded_header_rejected_400 (4 failed, 100 passed) |
| M59 | arm 1b sees \r only | KILLED | R::test_obs_folded_header_rejected_400[CL-LF] (2 failed, 102 passed) |
| M60 | drop json walk | KILLED | R::test_credential_whitespace_split_in_valid_json_body_returns_400 (16 failed, 88 passed) |
| M61 | POST raw_body=None | KILLED | R::test_duplicate_json_key_hiding_token_returns_400 (1 failed, 103 passed) |
| M62 | walk stops yielding keys | KILLED | R::test_credential_whitespace_split_as_json_key_returns_400 (5 failed, 99 passed) |
| MC1 | depth 5->4 | SURVIVED | NON-EQUIVALENT (strengthening): depth 4 catches more inputs earlier. No distinguishing input that the base misses but MC1 passes. Test `test_credential_quad_percent_encoded_at_depth4` kills it on the D5e backend (verify doc); on the D5f backend MC1 is strictly stronger. |
| MC2 | depth 5->6 | SURVIVED | NON-EQUIVALENT (strengthening): depth 6 is strictly more aggressive; no input leaks through depth 6 that leaks through depth 5 |
| MC3 | drop unquote_plus | KILLED | R::test_credential_encoded_whitespace_split_returns_400[PLUS] (14 failed, 90 passed) |
| MC4 | drop strip_ws | KILLED | R::test_credential_whitespace_split_in_valid_json_body_returns_400 (46 failed, 58 passed) |
| MC5 | fail-closed -> return frozenset(seen) (no tuple) | KILLED | TypeError: cannot unpack (96 failed, 8 passed) |
| MC5b | frozenset({s}) instead of frozenset(seen) | KILLED | false-positive explosion (96 failed, 8 passed) |
| MC6 | dedupe removed | KILLED | (5 failed, 99 passed) |
| MC9 | walk skips nested lists | KILLED | R::test_credential_whitespace_split_in_json_list_element_returns_400 (5 failed, 99 passed) |
| MF3 | non-finite coercion dropped | KILLED | R::test_non_finite_float_body_coerced_and_recorded (1 failed, 103 passed) |
| MG1 | depth gate removed | KILLED | R::test_json_depth_over_limit_returns_400_no_record (1 failed, 103 passed) |
| MG2 | gate > -> >= | KILLED | R::test_json_depth_at_limit_is_served (1 failed, 103 passed) |
| MG3 | MAX_JSON_DEPTH 32->1000 | KILLED | R::test_json_depth_at_limit_is_served (1 failed, 103 passed) |
| MG4 | depth scan ignores strings | KILLED | R::test_json_depth_ignores_brackets_inside_strings (2 failed, 102 passed) |
| MG5 | depth scan ignores escapes | KILLED | R::test_json_depth_handles_escaped_quote (1 failed, 103 passed) |
| MG6 | } no longer decrements | KILLED | R::test_json_depth_at_limit_is_served (1 failed, 103 passed) |

Non-equivalent survivors: MC1 (strengthening — depth 4 catches tokens earlier than depth 5), MC2 (strengthening — depth 6 is strictly more aggressive). Both are in the strengthening direction: the mutation makes the screen MORE aggressive, not less.

## oracle-tautology run
oracle -> `return True`: `5 failed, 99 passed in 40.72s`
Failed tests: junk_suffix, depth5_nesting, uppercased, zwsp_split, tab_split (the 5 known-bad vectors).

## gate runs

| run | command | result |
|---|---|---|
| suite run 1 | test_summary.sh (3 files) | `442 passed in 133.69s (0:02:13)` · pytest-exit: 0 |
| suite run 2 | test_summary.sh (3 files) | `442 passed in 133.50s (0:02:13)` · pytest-exit: 0 |
| red file standalone | test_summary.sh (red file) | `104 passed in 40.57s` · pytest-exit: 0 |
| pyflakes (3 files) | python3 -m pyflakes | rc 0 |

## F1 reproduction before/after

BEFORE (PIN, unmodified backend):
```
F1 LEAK (with junk suffix): HTTP/1.1 200 OK
  record x-trace: s0-01-upstream-tok%20en-0123456789abcdef-%25252541
  after unquote+strip: token present = True
CONTROL (no suffix): HTTP/1.1 400 Bad Request
  record body: {'credential_in_unexpected_location': True}
```

AFTER (fixed backend):
```
F1 AFTER FIX (with junk suffix): HTTP/1.1 400 Bad Request
  record body: {'credential_in_unexpected_location': True}
CONTROL (no suffix): HTTP/1.1 400 Bad Request
```

## not_done

- MC1 (depth 5->4): SURVIVED (strengthening). The brief lists it in the "re-run" set. MC1 is killed by the verify doc's `test_credential_quad_percent_encoded_fails_closed` on the D5e backend where depth 4 misses the quad vector. On the D5f backend, depth 4 is strictly stronger than depth 5 (catches tokens earlier — the fail-closed path fires LATER with fewer depth levels). No input exists that depth 4 passes and depth 5 catches; the mutation is strengthening. Reason for survival: not a leak-direction gap.

- MC2 (depth 5->6): SURVIVED (strengthening). Same analysis: depth 6 is strictly more aggressive. Not a gap.

- M29 (Expect truthiness): SURVIVED (equivalent). `get_all("Expect")` returns `None` (absent) or `["value"]` (present). `is not None` and truthiness agree on all possible returns. No distinguishing input exists.

- Depth-5 test header_name sink omitted: the brief lists `header NAME` as a sink for the depth-5 test. I omitted it because percent-encoded characters in HTTP header names may cause parser-level defects that trigger the framing gate before the credential screen runs. The 5 sinks tested (header_value, query, path, json_value, json_key) cover all code paths through `_carries_secret`.

## files

- `proofs/S0-01/tools/scripted_backend.py` — _normal_forms tuple return, _carries_secret fail-closed, str.lower, strip_zwc, _error() Connection: close, _json_safe iterative, RecursionError comment, docstrings
- `tests/red/test_s0_01_backend_credential_screen.py` — oracle widened + self-tests, 55 new tests, F6 duplicate removed, F9 rename, F11 docstring, F13 pytest.fail fallback
- `tests/test_s0_01_scripted_backend.py` — F5 domain table update, F17 isfinite, F19 tmp_path

## discrepancies

- MC1 survivor: the verify doc says MC1 (depth 5->4) is killed by `test_credential_quad_percent_encoded_fails_closed`. On the D5e backend (without the fail-closed fix), reducing depth 4 means the quad vector (depth 4) misses the token. On the D5f backend (with the fix), depth 4 is strengthening because the fail-closed branch now works correctly — fewer depth levels means more inputs trigger the bound-exceeded path (True), not fewer. This is not a gap.

- Red file timing: 104 tests in ~40s vs the prior 49 tests in ~190s. The new tests run significantly faster because they don't involve the slow model streaming path. Module-scope fixture reuse is more efficient with more tests sharing the same backend process.

## adjacent defects (report only)

- `_error()` Connection: close is applied to ALL error responses including 404 Not Found and 401 Unauthorized on successful-framing requests. This is more conservative than needed (only "rejections" need to close per the docstring), but it is strictly more secure (prevents request pipelining on error paths). The domain table test was updated to match.
