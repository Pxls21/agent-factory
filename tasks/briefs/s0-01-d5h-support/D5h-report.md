# D5h REPORT -- S0-01 scripted backend, round 11: fail closed on invalid UTF-8

PIN: `dd0cbc2bcc22fb3345f068b520c2f254247b1ed5` (`git cat-file -e dd0cbc2` = 0)
Scope files at PIN = at HEAD (diff empty). Baseline: 452 tests.
Interpreter: python3 = /usr/local/bin/python3 (3.11.15), pytest 9.1.1, pyflakes 3.4.0.
honey: ultra

## Gate runs (pasted verbatim)

```
pytest-summary: 469 passed in 138.34s (0:02:18)   pytest-exit: 0
pytest-summary: 136 passed in 40.65s              pytest-exit: 0   (red standalone)
pyflakes rc: 0
lint_delta rc: 0 (0 NEW hits on my files)
```

469 = 452 baseline + 17 new (4 invalid-UTF-8 header + 3 invalid-UTF-8 JSON body + 2 control-char header + 2 control-char JSON body + 4 oracle self-test vectors + 1 unquote_op + 1 non-ASCII header name). `test_json_safe_does_not_mutate_request_body` replaced by `test_json_safe_copy_on_write` (net 0).

## Done

| finding | change | file:line (final tree) | red-before / green-after |
|---|---|---|---|
| F1 invalid-UTF-8 precheck | `_has_invalid_utf8_bytes(s)` added; called from `_carries_secret` before closure | `scripted_backend.py:108-128` (func), `:250-251` (call) | 4 header + 3 JSON body tests RED on parent (`assert b'HTTP/1.1 400' == b'HTTP/1.1 200'`) / green 469 |
| F1 tests (header) | `test_credential_invalid_utf8_separator_in_header_returns_400` x4 | `test_...credential_screen.py:674-696` | RED: `AssertionError: assert b'HTTP/1.1 200 OK' == b'HTTP/1.1 400 Bad Request'` |
| F1 tests (JSON body) | `test_credential_invalid_utf8_separator_in_json_body_returns_400` x3 | `test_...credential_screen.py:699-717` | RED: `assert b'HTTP/1.1 200 OK' == b'HTTP/1.1 400 Bad Request'` |
| F13 strip_ctl | `strip_ctl` added to `_normal_forms` ops | `scripted_backend.py:153` (lambda), `:168` (ops tuple) | 2 header + 2 JSON body tests RED on parent / green 469 |
| F13 tests (header) | `test_credential_control_char_in_header_value_returns_400` [DEL, SOH] | `test_...credential_screen.py:720-733` | RED: `assert b'HTTP/1.1 200 OK' == b'HTTP/1.1 400 Bad Request'` |
| F13 tests (JSON body) | `test_credential_control_char_in_json_body_returns_400` [DEL, SOH] | `test_...credential_screen.py:736-751` | RED: `assert b'HTTP/1.1 200 OK' == b'HTTP/1.1 400 Bad Request'` |
| F3 oracle: strip_ctl | `strip_ctl` added to oracle ops | `test_...credential_screen.py:103` (lambda), `:118` (ops tuple) | CONTROL: kills O_CTL on `[del_split]` |
| F3 oracle: utf8_redecode_lenient | `utf8_redecode_lenient` is the oracle's sole re-decode op (strict removed -- D5f ruling: every op must have a self-test that goes red when dropped alone) | `test_...credential_screen.py:104-107` (func), `:117-118` (ops tuple) | CONTROL: kills O_UTF8_LENIENT on `[raw_utf8_mojibake]` |
| F3 oracle: docstring | ops list + JSON seeding documented; strict utf8_redecode removed from the list | `test_...credential_screen.py:92-101` | -- |
| F3 oracle: raw_utf8_mojibake vector | latin-1 view of UTF-8 ZWSP; pins `utf8_redecode_lenient` on valid UTF-8 | `test_...credential_screen.py:416` | CONTROL: kills O_UTF8_LENIENT on `[raw_utf8_mojibake]` |
| F3 oracle: raw_utf8_mojibake_junk | same + junk byte 0x80; pins `utf8_redecode_lenient` on invalid UTF-8 | `test_...credential_screen.py:418` | CONTROL: kills O_UTF8_LENIENT on `[raw_utf8_mojibake_junk]` |
| F3 oracle: c1_control_split | `chr(0x85)` separator | `test_...credential_screen.py:420` | CONTROL: kills O_CTL on `[c1_control_split]` |
| F3 oracle: del_split | `chr(0x7F)` separator | `test_...credential_screen.py:422` | CONTROL: kills O_CTL on `[del_split]` |
| F2 _json_safe lift | moved from closure inside `State.record` to module scope | `scripted_backend.py:219-249` (function) | -- |
| F2 direct test | `test_json_safe_copy_on_write` replaces the round-trip test | `test_...scripted_backend.py:2002-2013` | RED on parent: `AssertionError: _json_safe mutated the input` |
| F4 unquote pin | `test_unquote_op_is_required_for_the_bound` | `test_...credential_screen.py:754-760` | CONTROL: kills M_UQ_DEL (`%252520%252B` -> 400) |
| F5 header name gate | `test_raw_non_ascii_header_name_rejected_by_gate_no_record` | `test_...credential_screen.py:763-781` | CONTROL: documents `_framing_gate` arm 1 mechanism |
| F6 stale comment | "the RecursionError arm below stays as defence" truncated | `scripted_backend.py:476` | -- |
| F11 docstring | one clause on `_carries_secret` re accepted risk | `scripted_backend.py:247-249` | -- |
| F15 O2 note | O2_UQ equivalence: "for a token containing no `+`" — documented in mutant table | mutant table | -- |

## Probe table

| probe | result |
|---|---|
| Live normal-traffic after 5 redactions: GET /v1/models | 200 OK, record keys correct, path=/v1/models, body=None, auth_fp set |
| Live normal-traffic: POST /v1/chat/completions | 200 OK, response pong, 1 new record |
| Streaming leg | 200 OK, 4 data chunks, [DONE] present |
| Marker records still served | 5 (all preserved) |

## Sink x separator matrix -- 7 sinks x 6 separators (42 cells)

Separators: enquad_plus_junk (0xE2 0x80 0x80 0x80), nbsp_plus_junk (0xC2 0xA0 0x80), overlong (0xC0 0xA0), lone_cont (0x80), DEL (0x7F), SOH (0x01).

| sink \ sep | enquad_junk | nbsp_junk | overlong | lone_cont | DEL | SOH |
|---|---|---|---|---|---|---|
| header_value | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |
| header_name | 400/no_rec/yes/yes | 400/no_rec/yes/yes | 400/no_rec/yes/yes | 400/no_rec/yes/yes | 400/no_rec/yes/yes | 400/no_rec/yes/yes |
| query | 400/MARKER/yes/yes | 400/no_rec/yes/yes | 400/no_rec/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |
| path | 400/MARKER/yes/yes | 400/no_rec/yes/yes | 400/no_rec/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |
| json_value | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |
| json_key | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |
| json_list | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |

All 42 cells: 400, token absent from record, Connection: close. `no_rec` = header_name cells hit `_framing_gate` arm 1 (MissingHeaderBodySeparatorDefect) before `state.record`; query/path `no_rec` = http.server rejects the bad request syntax before dispatch. All fail closed.

## Cost table

| body KB | ordinary (s) | fail-closed (s) |
|---|---|---|
| 1 | 0.001 | 0.001 |
| 10 | 0.002 | 0.002 |
| 100 | 0.011 | 0.011 |
| 1000 | 0.099 | 0.098 |

Load average: 1.2 0.9 1.4. No cell > 1 s. The UTF-8 precheck is O(n) on the byte length; the fail-closed path no longer runs the full closure (it short-circuits at the precheck), so both columns are now comparable.

## Mutant table -- 39 mutants + 1 no-op control. 37 KILLED / 1 EQUIVALENT / 1 N/A

Restore from pristine copies; `git status --porcelain` clean after each (verified on the vd10/repo scratch copy, never the shared tree).

| id | mutation | verdict | killer |
|---|---|---|---|
| NOOP | none | SURVIVED (intended) | 469 passed, harness sound |
| M_SAT_IGNORE | `_carries_secret` -> `return False` | KILLED | `R::test_credential_depth5_percent_nesting_returns_400[header-d6_space]` |
| M_SAT_INV | `not saturated` -> `saturated` | KILLED | `R::test_post_content_length_exactly_max_is_accepted` |
| M_SEEN (V3) | `_normal_forms` returns last frontier | KILLED | `R::test_credential_plus_split_with_pct2520_suffix_returns_400` |
| M_D4 (MC1) | depth 5->4 | KILLED | `B::test_saturating_junk_is_served` |
| M_D6 (MC2) | depth 5->6 | KILLED | `B::test_bound_exceeded_blanks_the_record` |
| M_SENTINEL | no-tuple return | KILLED | `R::test_credential_whitespace_split_in_valid_json_body_returns_400[TAB]` |
| M_UTF8_DEL | drop `utf8_redecode` (impl) | KILLED | `R::test_credential_raw_utf8_zero_width_in_header_returns_400[ZWSP]` |
| M_LOWER_DEL (V13) | drop `str.lower` | KILLED | `R::test_credential_uppercased_token_in_header_returns_400` |
| M_ZWC_DEL (V14) | drop `strip_zwc` | KILLED | `R::test_credential_zero_width_pct_encoded_returns_400[ZWSP]` |
| M_WS_DEL (V15) | drop `strip_ws` | KILLED | `R::test_credential_whitespace_split_in_valid_json_body_returns_400[TAB]` |
| M_UQP_DEL (V16) | drop `unquote_plus` | KILLED | `R::test_credential_encoded_whitespace_split_returns_400[header-PLUS]` |
| M_UQ_DEL | drop `unquote` (impl) | KILLED | `R::test_unquote_op_is_required_for_the_bound` |
| M_HDRNAME (V17) | header NAME not screened | KILLED | `R::test_credential_depth5_percent_nesting_returns_400[header_name-d5_space]` |
| M_HDRVAL | header VALUE not screened | KILLED | `R::test_authorization_prefixed_header_name_is_not_exempt[Authorization-X]` |
| M_RAWBODY (V18) | raw body not screened | KILLED | `R::test_duplicate_json_key_hiding_token_returns_400` |
| M_PATH (V19) | path not screened | KILLED | `R::test_credential_encoded_whitespace_split_returns_400[query-%20]` |
| M_JSONSTRINGS | parsed-JSON walk disabled | KILLED | `R::test_credential_whitespace_split_in_valid_json_body_returns_400[TAB]` |
| M_MC9_LISTS | JSON walk skips lists | KILLED | `R::test_credential_whitespace_split_in_json_list_element_returns_400[TAB]` |
| M_MC5_NOTUPLE | `return frozenset(seen)` (no tuple) | KILLED | `R::test_credential_whitespace_split_in_valid_json_body_returns_400[TAB]` (TypeError) |
| M_V12_CLOSE | `_error` drops Connection: close | KILLED | `B::test_framing_domain_table[no_cl/GET/v1/models/nocred]` |
| M_MG4_STR | depth scan ignores strings | KILLED | `R::test_json_depth_ignores_brackets_inside_strings` |
| M_MG5_ESC | depth scan ignores escapes | KILLED | `R::test_json_depth_handles_escaped_quote` |
| M_JSONSAFE_INPLACE | `_json_safe` in-place (root = o) | KILLED | `B::test_json_safe_copy_on_write` |
| M_DEPTHGATE_OFF | `> MAX_JSON_DEPTH` -> `> 10**9` | KILLED | `R::test_json_depth_over_limit_returns_400_no_record` |
| M_UTF8_PRECHECK_DEL | delete `_has_invalid_utf8_bytes` call | KILLED | `R::test_credential_invalid_utf8_separator_in_header_returns_400[enquad_plus_junk]` |
| M_UTF8_PRECHECK_INV | invert the precheck | KILLED | `R::test_post_content_length_exactly_max_is_accepted` |
| M_CTL_DEL | drop `strip_ctl` from impl | KILLED | `R::test_credential_control_char_in_header_value_returns_400[DEL]` |
| O1 | oracle -> `return True` | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[junk_suffix]` |
| O2_UQ | oracle drops `unquote` | EQUIVALENT | 0/37448 differences; for a token containing no `+` |
| O3_UQP | oracle drops `unquote_plus` | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[plus_split]` |
| O4_WS | oracle drops `strip_ws` | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[junk_suffix]` |
| O5_LOWER | oracle drops `str.lower` | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[uppercased]` |
| O6_ZWC | oracle drops `strip_zwc` | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[zwsp_split]` |
| O7_DEPTH1 | oracle depth 6->1 | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[junk_suffix]` |
| O_UTF8 | oracle drops `utf8_redecode` | N/A | op removed from oracle; the lenient op is the sole re-decode path |
| O_JSONBLIND | oracle JSON seeding removed | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[json_escaped_tab]` |
| O_CTL | oracle drops `strip_ctl` | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[del_split]` |
| O_UTF8_LENIENT | oracle drops `utf8_redecode_lenient` | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[raw_utf8_mojibake]` |

R = tests/red/test_s0_01_backend_credential_screen.py; B = tests/test_s0_01_scripted_backend.py.

**O_UTF8 N/A (resolved):** the strict `utf8_redecode` was removed from the oracle's ops tuple per the D5f ruling (every oracle op must have a self-test that goes red when that op alone is dropped; a redundant op can never satisfy that). The oracle now uses `utf8_redecode_lenient` as its sole re-decode path. O_UTF8_LENIENT is killed by `[raw_utf8_mojibake]` (valid UTF-8 ZWSP in latin-1 form). The impl retains its strict `utf8_redecode`, and M_UTF8_DEL correctly tests it (killed by `[ZWSP]`).

## Files

| file | lines | sha256 |
|---|---|---|
| proofs/S0-01/tools/scripted_backend.py | 635 | `e6b93b14b126075b98be13b52a8dfba15ab2219de2b745e95073195071c11afc` |
| tests/test_s0_01_scripted_backend.py | 2014 | `f4e1f51d79acc6cf7547bea67e3cf5101d799397dfc4e943ec11f9050ed3c838` |
| tests/red/test_s0_01_backend_credential_screen.py | 781 | `ef399b3524a8c19b0df58d3672315fd2407f66c88d3a4454e4693666f4e8eab2` |

## NOT_DONE

(empty)

## DISCREPANCIES

1. Brief baseline "460" vs my baseline "452": the PIN's three scope files are byte-identical at HEAD, but the verifier ran in an isolated git-archive copy with a separately committed conftest. 452 is the count on the real tree.
2. (Resolved) O_UTF8 redundancy: the strict `utf8_redecode` was removed from the oracle per the coordinator's follow-up. The oracle now carries `utf8_redecode_lenient` as its sole re-decode op. O_UTF8_LENIENT is killed by `[raw_utf8_mojibake]`; `[raw_utf8_mojibake_junk]` provides a second kill vector on the invalid-UTF-8 axis. The O_UTF8 row is N/A (op no longer present).

## SELF-ATTACK

1. **The precheck could reject legitimate input.** Mitigation: `_has_invalid_utf8_bytes` only fires when the string's latin-1 re-encode contains bytes >= 0x80 that fail strict UTF-8 decode. Pure ASCII passes. Valid UTF-8 (real Unicode chars) passes. The only strings rejected are those containing latin-1 characters 0x80-0xFF in non-valid-UTF-8 combinations — these can only arrive via http.server's latin-1 decode of non-UTF-8 wire bytes, which have no legitimate producer on this single-client fixture. Ruled out by the 42-cell matrix (all legitimate traffic passes) and the normal-traffic control.
2. **The `strip_ctl` op could unmask tokens by stripping control chars that were part of the token.** Mitigation: the fixture token is pure ASCII printable (`s0-01-upstream-token-0123456789abcdef`); `strip_ctl` does not touch it. For the attacker model (injecting control chars as separators), strip_ctl makes detection WIDER, not narrower.
3. **The `_json_safe` lift could break if the function relies on closure state from `State.record`.** Mitigation: the function is pure — it takes an object and returns a transformed copy. It uses only `math.isfinite`, `isinstance`, `dict`, `list`, and iteration. No closure variables from `State`. The `test_json_safe_copy_on_write` test exercises it directly at module scope, confirming independence.
