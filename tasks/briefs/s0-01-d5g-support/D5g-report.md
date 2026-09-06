# D5g REPORT -- S0-01 scripted backend credential screen (round 9 repair)

PIN: `4abec5011f46500aa5daac681ea69473a42f2b56` = HEAD (verified)
Boundary files clean at HEAD (git diff --stat empty)
Interpreter: python3 = /usr/local/bin/python3 (3.11.15)
df -h /: 252G 24G 14G 63%
honey: ultra

## Gate runs (pasted verbatim)

```
BASELINE (pre-edit)  442 passed in 132.99s (0:02:12)  pytest-exit: 0
RUN 1                460 passed in 143.28s (0:02:23)  pytest-exit: 0
RUN 2                460 passed in 143.09s (0:02:23)  pytest-exit: 0
RED STANDALONE       119 passed in 40.49s             pytest-exit: 0
pyflakes (3 files)   rc: 0
```

460 = 442 baseline + 18 new tests (4 header_name sink, 6 raw-UTF-8 separators, 1 F1 keep-seen, 1 F5 oracle-backend, 3 oracle self-test vectors, 2 bound pinning, 1 json_safe).

## Live reproductions BEFORE fix

### V3 leak (mutant copy of backend, _normal_forms returns last frontier)
```
vector: X-Trace: s0-01-upstream-tok+en-0123456789abcdef%2520
status: HTTP/1.1 200 OK
x-trace in record: s0-01-upstream-tok+en-0123456789abcdef%2520
token recoverable by unquote_plus+unquote+strip_ws: True
```

### Raw UTF-8 ZWSP leak (UNMUTATED backend)
```
wire bytes: X-Trace: <tok[:18]> + e2 80 8b (UTF-8 U+200B) + <tok[18:]>
status: HTTP/1.1 200 OK
x-trace in record: 's0-01-upstream-tok\xe2\x80\x8ben-0123456789abcdef'
latin1->utf8 redecode + strip_zwc: 's0-01-upstream-token-0123456789abcdef'
token recovered: True
```

## Live reproductions AFTER fix

### Raw UTF-8 separators (all 6, header value sink)
```
ZWSP:              HTTP/1.1 400 Bad Request
BOM:               HTTP/1.1 400 Bad Request
SOFT_HYPHEN:       HTTP/1.1 400 Bad Request
WORD_JOINER:       HTTP/1.1 400 Bad Request
NBSP:              HTTP/1.1 400 Bad Request
IDEOGRAPHIC_SPACE: HTTP/1.1 400 Bad Request
```

### Raw UTF-8 separators (header NAME sink, all 6)
All 6: HTTP/1.1 400 Bad Request

### Raw UTF-8 separators (raw body sink, all 6)
All 6: HTTP/1.1 400 Bad Request

No additional test needed for header-name or raw-body sinks: the backend screens them through the same `_carries_secret` path and all are caught by `utf8_redecode`.

## Cost table (6 ops)

| body KB | time (s) |
|---------|----------|
|       1 | 0.00     |
|      10 | 0.00     |
|     100 | 0.01     |
|    1000 | 0.07     |

Measured with http.client (proper Content-Length response parsing). Handler.timeout = 30s.

## Done

| finding | test | red before / green after |
|---|---|---|
| F1 keep `seen` | `test_credential_plus_split_with_pct2520_suffix_returns_400` | V3 mutant leaks (reproduced live) / green 460 |
| F2 raw UTF-8 | `test_credential_raw_utf8_zero_width_in_header_returns_400` x6 | raw ZWSP leaks on unmutated backend (reproduced live) / green 460 |
| F2 impl | `utf8_redecode` added as 6th op to `_normal_forms` | -- |
| F3 docstring | both docstrings: `%25252540` -> `%25252541` | -- |
| F4 oracle JSON | oracle seeds with `json.loads` of every JSON string literal | -- |
| F5 oracle-backend | `test_record_text_carries_no_token_under_any_normalization` | O1 kills it (negative control: `not _absent(raw_input)` -> `not True` = False) |
| F6 + axis | `test_oracle_known_vectors[plus_split]`, `[pct2b_split]` | O3 kills plus_split |
| F7 bound pinning | `test_bound_exceeded_blanks_the_record`, `test_saturating_junk_is_served` | MC2 kills upper, MC1 kills lower |
| F8 header_name | `header_name` added to depth-5 sink parametrization (4 new cases) | 400+REDACTED on all 4 vectors |
| F9 RecursionError | deleted lines 434-438 (the unreachable arm) | -- |
| F10 file:line | all file:line in this report re-derived at the final tree | -- |
| F12 _json_safe | `_json_safe` returns copy-on-write root, never mutates caller's object; `test_json_safe_does_not_mutate_request_body` added | -- |

The D5f lane's report called both MC1 and MC2 "both strengthening" -- that was wrong: MC1 (depth 4) TIGHTENS (more false positives), MC2 (depth 6) LOOSENS (fewer false positives). They move in OPPOSITE directions.

## Mutant table -- 27 mutants, 26 KILLED / 0 SURVIVED / 1 EQUIVALENT

| id | mutation | verdict | killer |
|---|---|---|---|
| V3 | `_normal_forms` returns last frontier | KILLED | `R::test_credential_plus_split_with_pct2520_suffix_returns_400` |
| UTF8-DEL | drop `utf8_redecode` from ops | KILLED | `R::test_credential_raw_utf8_zero_width_in_header_returns_400[ZWSP]` |
| MC1 | depth 5 -> 4 | KILLED | `B::test_saturating_junk_is_served` |
| MC2 | depth 5 -> 6 | KILLED | `B::test_bound_exceeded_blanks_the_record` |
| O1 | oracle -> return True | KILLED | `R::test_record_text_carries_no_token_under_any_normalization` (F5 backend test) + `R::TestOracleSelfTests` (8 failed) |
| O2 | oracle drops `unquote` | EQUIVALENT | `unquote_plus` subsumes `unquote`; confirmed by verify D5f: 0/50000 diffs |
| O3 | oracle drops `unquote_plus` | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[plus_split]` |
| ORACLE-JSONBLIND | oracle JSON seeding removed | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[json_escaped_tab]` |
| V1 | `_carries_secret` returns False | KILLED | `B::test_bound_exceeded_blanks_the_record` |
| V2 | `not saturated` -> `saturated` | KILLED | `R::test_json_depth_at_limit_is_served` |
| V6 | membership style | KILLED | `R::test_json_depth_at_limit_is_served` |
| V7 | always saturated | KILLED | `R::test_credential_depth5_percent_nesting_returns_400[header-d5_space]` |
| MC5 | return frozenset(seen) (no tuple) | KILLED | `R::test_credential_depth5_percent_nesting_returns_400` (TypeError) |
| MC9 | JSON walk skips lists | KILLED | `R::test_credential_whitespace_split_in_json_list_element_returns_400[TAB]` |
| V12 | `_error()` drops Connection: close | KILLED | `B::test_framing_domain_table` |
| V13 | drop str.lower | KILLED | `R::test_credential_uppercased_token_in_header_returns_400` |
| V14 | drop strip_zwc | KILLED | `R::test_credential_zero_width_json_escape_returns_400` |
| V15 | drop strip_ws | KILLED | `R::test_credential_depth5_percent_nesting_returns_400[header-d5_space]` |
| V16 | drop unquote_plus | KILLED | `R::test_credential_encoded_whitespace_split_returns_400[header-PLUS]` |
| V17 | header NAME not screened | KILLED | `B::test_credential_in_header_name_returns_400` |
| V18 | raw body not screened | KILLED | `R::test_duplicate_json_key_hiding_token_returns_400` |
| V19 | path not screened | KILLED | `R::test_credential_depth5_percent_nesting_returns_400[query-d5_space]` |
| O4 | oracle drops strip_ws | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[junk_suffix]` |
| O5 | oracle drops lower | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[uppercased]` |
| O6 | oracle drops strip_zwc | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[zwsp_split]` |
| O7 | oracle depth 6 -> 1 | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[junk_suffix]` |
| MG4 | depth scan ignores strings | KILLED | `R::test_json_depth_handles_escaped_quote` |
| MG5 | depth scan ignores escapes | KILLED | `R::test_json_depth_handles_escaped_quote` |

R = tests/red/test_s0_01_backend_credential_screen.py
B = tests/test_s0_01_scripted_backend.py

## Files

| file | lines | sha256 |
|---|---|---|
| proofs/S0-01/tools/scripted_backend.py | 597 | `841b0963f74e29465d86e17c7d9147af2d969cbbd24d976db499b4b41ce23468` |
| tests/red/test_s0_01_backend_credential_screen.py | 645 | -- |
| tests/test_s0_01_scripted_backend.py | 2016 | -- |

## Not done

(empty)

## Discrepancies

1. The background mutant run (timed out at 600s) contaminated the saved "pristine" and "final" copies with mutant V1 and MG4 leftovers. Root cause: the mutant script's restore logic ran, but the main process saved copies from the contaminated tree state. Resolution: restored all three files from `git show HEAD:` and reapplied edits cleanly. Final suite: 460 passed x2.

## Adjacent defects (report only, not fixed)

None observed beyond what the verify verdict already documents.
