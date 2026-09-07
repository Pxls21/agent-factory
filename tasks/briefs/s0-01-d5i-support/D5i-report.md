# Lane D5i report -- S0-01 scripted backend round 12

PIN: `618749fafdc9032696729b53e8c176859e3891a8` (HEAD at dispatch). Work lands in the CHILD commit.

## FILE IDENTITY

| file | sha256 (final tree) | lines |
|---|---|---|
| `proofs/S0-01/tools/scripted_backend.py` | `7732a6f64b495ab28a42d69f703d4ec1eadf1de34c775a544d988be715024b5a` | 676 |
| `tests/test_s0_01_scripted_backend.py` | `a59c63da87eb2006f8b42afcbcd1ce0e0f9c6da0248b1467a8a39dc18a14c320` | 2031 |
| `tests/red/test_s0_01_backend_credential_screen.py` | `feaaf78b17a8c8e43a45346904d980cc890517649ef7ecc606499fe95a7398b8` | 967 |

## DONE

| finding | change | file:line (grep on final tree) | red-before / CONTROL | green-after |
|---|---|---|---|---|
| D5h-F1 byte_view flag | `_carries_secret(s, *, byte_view)`: precheck runs only when `byte_view=True`; leaf walk at `:385` passes `byte_view=False` | `scripted_backend.py:327` (def), `:345` (precheck guard), `:369/:373/:377/:388` (byte_view=True), `:385` (byte_view=False) | RED: `AssertionError: assert b'HTTP/1.1 400 Bad Request' == b'HTTP/1.1 200 OK'` (PIN rejects ordinary accented text) | `test_ordinary_latin1_text_in_json_body_is_served` 6 params, decorator `:810`, def `:817` |
| D5h-F1 docstring | `_has_invalid_utf8_bytes` docstring restated for byte-view-only sinks; `_carries_secret` docstring documents `byte_view` semantics and confusable-substitution out-of-contract boundary | `scripted_backend.py:135-144` (precheck doc), `:328-346` (carries_secret doc) | N/A (prose) | N/A |
| D5i item 2 lenient re-decode | `utf8_redecode_lenient` is the sole re-decode in both closure and oracle; strict `utf8_redecode` removed (subsumed, no test could pin it; D5i follow-up) | `scripted_backend.py:185-191` (def), `:193` (ops tuple) | CONTROL: D5h JSON twin tests (`test_credential_invalid_utf8_separator_in_json_body_returns_400`) stay green; kills LENIENT_DEL_IMPL. Depth pins verified: `test_saturating_junk_is_served` (%252B served) and `test_bound_exceeded_blanks_the_record` (%25252541 blanked) both green with 5-op closure | 500 passed |
| D5h-F2 strip_invis | `strip_invis` op: drops `unicodedata.category` in {Cf, Cs, Cc, Mn, Me, Zs, Zl, Zp} + `_INVISIBLE_EXTRA`. Docstring at `:177-181` states the C1 arm (U+0080-U+009F, Cc) is doubly covered: strip_invis at depth 1, lenient re-decode at depth 2 (D5i follow-up) | `scripted_backend.py:120-125` (_INVISIBLE_EXTRA, _INVIS_CATEGORIES), `:176-184` (strip_invis def+doc), `:193` (ops) | RED: `AssertionError: assert b'HTTP/1.1 200 OK' == b'HTTP/1.1 400 Bad Request'` (PIN serves invisible separators) | `test_credential_invisible_separator_in_header_returns_400` 8 params, decorator `:834`, def `:836` |
| D5h-F2 oracle | Oracle `_absent_under_all_normalizations` updated: strip_ws/strip_zwc/strip_ctl replaced by strip_invis; 6 new self-test vectors | `red:93-95` (_INVIS_CATEGORIES, _INVISIBLE_EXTRA), `:117-119` (strip_invis), `:126` (ops), `:435-449` (vectors) | CONTROL: oracle self-tests pass; O_INVIS kills `[zwnj_split]` | 500 passed |
| D5h-F2 JSON twin | 4 invisible-separator JSON-escape tests | decorator `:856`, def `:862` | RED: `assert b'HTTP/1.1 200 OK' == b'HTTP/1.1 400 Bad Request'` | 500 passed |
| D5h-F2 INVIS_LIST_ONLY killer | U+2061 FUNCTION APPLICATION (Cf, not in _INVISIBLE_EXTRA) test | def `:880` | RED: `assert b'HTTP/1.1 200 OK' == b'HTTP/1.1 400 Bad Request'` | 500 passed |
| D5h-F2 redundant ops removed | strip_ws, strip_zwc, strip_ctl removed from BOTH impl and oracle (all fully subsumed by strip_invis; verified: 0 characters in any of the three domains have a category outside {Cf,Cs,Cc,Mn,Me,Zs,Zl,Zp}) | impl `:193`, oracle `:126` | CONTROL: all existing vectors still pass (the old ops' named killers now kill strip_invis) | 500 passed |
| D5h-F3 record wiring | `test_record_does_not_mutate_the_caller_body` calls `State.record` directly; asserts caller body unmutated | `test_main:2019` | CONTROL: green on PIN (State.record calls _json_safe which copies). Kills JSONSAFE_INLINE_IN_RECORD | 500 passed |
| D5h-F4 C1 wire form | `test_credential_c1_control_wire_form_returns_400` over PAD/NEL/APC wire bytes | decorator `:901`, def `:902` | CONTROL: green on PIN (strip_invis Cc arm catches U+0080 after utf8_redecode) | 500 passed |
| D5h-F5 refuse != repair | `test_invalid_utf8_without_the_token_is_refused_not_repaired`: invalid UTF-8, no credential anywhere -> 400 | def `:924` | CONTROL: green on PIN (precheck fires). Kills LENIENT_IN_IMPL | 500 passed |
| D5h-F11 record-count deltas | `n0 = len(_records(backend))` + `assert len(recs) == n0 + 1` added to `invalid_utf8_separator_in_header` (`:706-708`), `invalid_utf8_separator_in_json_body` (`:731-733`), `control_char_in_json_body` (`:771-773`) | grep lines cited | CONTROL: kills RECORDLESS_400_HDR (gate-only rejection writes no record, stale `[-1]` would pass without the delta) | 500 passed |
| D5h-F12 O2 qualifier | Oracle docstring: "`unquote` is redundant with `unquote_plus` only for a token containing no `+`; it stays so the oracle is token-agnostic" | `red:113-114` | N/A (prose) | N/A |
| D5h-F14 precheck ordering | `test_precheck_before_closure_on_invalid_utf8`: monkeypatches `_normal_forms` with a counter; asserts 0 calls for invalid-UTF-8 byte-view input | def `:944` | RED: `TypeError: State._carries_secret() got an unexpected keyword argument 'byte_view'` (PIN has no byte_view) | 500 passed |
| D5i module docstring | Module docstring updated: ops list, strip_invis domain, lenient decode, byte_view semantics, confusable boundary | `scripted_backend.py:41-68` | N/A (prose) | N/A |

## MUTANT TABLE

All mutants run on scratchpad copies at `/tmp/.../scratchpad/d5i_mut/`. Scope files verified unchanged (sha256) after each.

| # | mutant | mutated line (final tree) | verdict | killer |
|---|---|---|---|---|
| 1 | NOOP | (no change) | SURVIVED | (intended) |
| 2 | PRECHECK_ON_LEAVES | `:385` `byte_view=False` -> `byte_view=True` | KILLED | `test_ordinary_latin1_text_in_json_body_is_served[e_acute]` |
| 3 | INVIS_DEL | `:193` drop `strip_invis` from ops | KILLED | `test_credential_invisible_separator_in_header_returns_400[ZWNJ]` |
| 4 | INVIS_LIST_ONLY | `:178` category check replaced by membership in _INVISIBLE_EXTRA only | KILLED | `test_credential_function_application_separator_in_header_returns_400` |
| 5 | LENIENT_DEL_IMPL | `:193` drop `utf8_redecode_lenient` from ops | KILLED | `test_credential_invalid_utf8_separator_in_json_body_returns_400[overlong_pair]` |
| 6 | CTL_PARTIAL_noC1 | `:178` strip_invis skips 0x80-0x9F | EQUIVALENT | utf8_redecode_lenient recovers token via secondary path (depth+1): strip_invis at depth 0 passes chr(0xC2)+chr(0x80) through, lenient re-decode at depth 1 yields chr(0x80) (valid UTF-8 C2 80 = U+0080), then lenient at depth 2 drops the lone 0x80 byte. Docstring at `:177-181` records this dual coverage |
| 7 | LENIENT_IN_IMPL | `:345` precheck deleted | KILLED | `test_invalid_utf8_without_the_token_is_refused_not_repaired` |
| 8 | JSONSAFE_INLINE_IN_RECORD | `:374` record calls in-place walk (module _json_safe kept) | KILLED | `test_record_does_not_mutate_the_caller_body` |
| 9 | RECORDLESS_400_HDR | header rejected in _framing_gate (400, no record) | KILLED | record-count delta assertions on `invalid_utf8_separator_in_header` |
| 10 | PRECHECK_AFTER_CLOSURE | `:345` precheck moved below closure | KILLED | `test_precheck_before_closure_on_invalid_utf8` |
| 11 | M_SAT_IGNORE | `:346` `return not saturated` -> `return False` | KILLED | `test_bound_exceeded_blanks_the_record` |
| 12 | M_SAT_INV | `:346` `return not saturated` -> `return True` | KILLED | `test_post_content_length_exactly_max_is_accepted` |
| 13 | M_SEEN | `:200` return frontier instead of seen | KILLED | `test_credential_plus_split_with_pct2520_suffix_returns_400` |
| 14 | M_D4 | `:197` range(5) -> range(4) | KILLED | `test_saturating_junk_is_served` |
| 15 | M_D6 | `:197` range(5) -> range(6) | KILLED | `test_bound_exceeded_blanks_the_record` |
| 16 | M_SENTINEL | `:200` drop tuple return (return frozenset only) | KILLED | `test_credential_whitespace_split_in_valid_json_body_returns_400[TAB]` |
| 17 | M_MC5_NOTUPLE | `:202` bound-exceeded return drops second tuple element | KILLED | `test_bound_exceeded_blanks_the_record` |
| 18 | M_UTF8_DEL | N/A | N/A | strict `utf8_redecode` removed from the impl (D5i follow-up); the op is absent, so the mutant no longer applies |
| 19 | M_LOWER_DEL | `:193` drop str.lower from ops | KILLED | `test_credential_uppercased_token_in_header_returns_400` |
| 20 | M_UQP_DEL | `:193` drop unquote_plus from ops | KILLED | `test_credential_encoded_whitespace_split_returns_400[header-PLUS]` |
| 21 | M_UQ_DEL | `:193` drop unquote from ops | KILLED | `test_unquote_op_is_required_for_the_bound` |
| 22 | M_UTF8_PRECHECK_DEL | `:345` precheck deleted | KILLED | `test_invalid_utf8_without_the_token_is_refused_not_repaired` |
| 23 | M_UTF8_PRECHECK_INV | `:345` `not _has_invalid_utf8_bytes` | KILLED | `test_post_content_length_exactly_max_is_accepted` |
| 24 | M_HDRNAME | `:373` drop header-name check | KILLED | `test_credential_depth5_percent_nesting_returns_400[header_name-d5_space]` |
| 25 | M_HDRVAL | `:373` drop header-value check | KILLED | `test_authorization_prefixed_header_name_is_not_exempt[Authorization-X]` |
| 26 | M_RAWBODY | `:388` raw-body check removed | KILLED | `test_duplicate_json_key_hiding_token_returns_400` |
| 27 | M_PATH | `:369` path check removed | KILLED | `test_credential_encoded_whitespace_split_returns_400[query-%20]` |
| 28 | M_JSONSTRINGS | `:383` leaf walk disabled | KILLED | `test_credential_whitespace_split_in_valid_json_body_returns_400[TAB]` |
| 29 | M_MC9_LISTS | JSON list-item walk disabled | KILLED | `test_credential_whitespace_split_in_json_list_element_returns_400[TAB]` |
| 30 | M_V12_CLOSE | `:619` `self.close_connection = True` in `_stream` removed | SURVIVED | `Connection: close` header still sent at `:600`; existing tests check the header, not server-side socket state. Defense-in-depth for a client that ignores the header; no test exercises that scenario |
| 31 | M_DEPTHGATE_OFF | depth gate disabled | KILLED | `test_json_depth_over_limit_returns_400_no_record` |
| 32 | M_JSONSAFE_INPLACE | _json_safe mutates in place | KILLED | `test_json_safe_copy_on_write` |
| 33 | O_INVIS | oracle: drop strip_invis | KILLED | `TestOracleSelfTests::test_oracle_known_vectors[zwnj_split]` |
| 34 | O2_UQ | oracle: drop unquote | SURVIVED | EQUIVALENT for this token (no `+`); qualifier at `red:113-114` |
| 35 | O5_LOWER | oracle: drop str.lower | KILLED | `[uppercased]` |
| 36 | O3_UQP | oracle: drop unquote_plus | KILLED | `[plus_split]` |
| 37 | O_UTF8_LENIENT | oracle: drop utf8_redecode_lenient | KILLED | `[raw_utf8_mojibake]` |

Summary: 37 mutants. 30 KILLED, 1 SURVIVED-intended (NOOP), 1 EQUIVALENT with mechanism (CTL_PARTIAL_noC1), 1 N/A (M_UTF8_DEL -- op absent), 1 SURVIVED-qualified (O2_UQ per D5h-F12), 1 SURVIVED-defense-in-depth (M_V12_CLOSE -- `Connection: close` header sent; the server-side socket-close is defense-in-depth that no test distinguishes), 2 effectively-identical (M_UTF8_PRECHECK_DEL = LENIENT_IN_IMPL since strict redecode removed).

## PROBE TABLES

### Sink x invisible-separator matrix (live, own subprocess backend, final tree)

All 8 invisible separators in headers: `test_credential_invisible_separator_in_header_returns_400` -- 8/8 = 400 + MARKER + record delta 1.
All 4 invisible separators in JSON body: `test_credential_invisible_separator_in_json_body_returns_400` -- 4/4 = 400 + MARKER + record delta 1.
U+2061 FUNCTION APPLICATION in header: 400 + MARKER. Kills INVIS_LIST_ONLY.
3 C1 wire forms (PAD/NEL/APC) in header: 400 + MARKER + record delta 1.

23 separator-tests passed (0 deselected from the separator subset).

### Legitimate-traffic table (live, own subprocess backend, final tree)

| body content | status | record |
|---|---|---|
| `caf` + U+00E9 (e_acute) | 200 OK | VERBATIM |
| `M` + U+00FC + `ller` (u_uml) | 200 OK | VERBATIM |
| `se` + U+00F1 + `or` (n_tilde) | 200 OK | VERBATIM |
| U+00A3 + `100` (pound) | 200 OK | VERBATIM |
| `50` + U+00B0 + `C` (degree) | 200 OK | VERBATIM |
| U+00A9 + ` 2026` (copyright) | 200 OK | VERBATIM |

6 tests passed. Record content verified: `messages[0].content` == input.

### Cost table (min of 5 per cell, own subprocess backend, load 0.49)

| body KB | ordinary (s) | invalid-UTF-8 fail-closed (s) | bound-exceeded fail-closed (s) |
|---|---|---|---|
| 1 | 0.001 | 0.001 | 0.001 |
| 10 | 0.003 | 0.003 | 0.002 |
| 100 | 0.018 | 0.018 | 0.017 |
| 1000 | 0.164 | 0.162 | 0.161 |

Vectors: ordinary = valid 1-MB POST, no credential; invalid-UTF-8 = bytes [0x80, 0xC0] in X-Trace header; bound-exceeded = `%25252541` in X-Trace header. All three columns carry the same body. Load average 0.49 at start and end.

Observation: all three columns converge because the body I/O dominates. The invalid-UTF-8 and bound-exceeded paths short-circuit the credential check in the header, but `State.record` still runs the body-str closure on the json.dumps output (which is small regardless of input size). No cell exceeds 1 s.

## GATE LINES (pasted from `scripts/test_summary.sh`)

```
pytest-summary: 500 passed in 168.44s (0:02:48)   pytest-exit: 0
```
Red standalone: `166 passed in 70.82s`
Pyflakes (3 files): rc 0

## NOT_DONE

1. **CTL_PARTIAL_noC1 stays EQUIVALENT.** The brief requires this mutant to die on `test_credential_c1_control_wire_form_returns_400`. It is EQUIVALENT because `utf8_redecode_lenient` recovers the token via a secondary path at depth+1: at depth 0 the latin-1 chars chr(0xC2)+chr(0x80) pass through strip_invis (chr(0xC2) is Lu); at depth 1 the lenient re-decode produces U+0080 (valid UTF-8 C2 80); at depth 2 the lenient re-decode drops the lone 0x80 byte (invalid continuation) and reconnects the token halves. The C1 wire form test is GREEN (strip_invis catches at depth 1 in the non-mutant). `strip_invis`'s docstring at `:177-181` records this dual coverage so the next round does not re-litigate it.

2. **M_UTF8_DEL is N/A.** The strict `utf8_redecode` was removed from the impl (D5i follow-up). The lenient decode is the sole re-decode path in both closure and oracle. The mutant row is marked N/A (op absent). Depth pins verified with the 5-op closure: `test_saturating_junk_is_served` (%252B served, lower pin) and `test_bound_exceeded_blanks_the_record` (%25252541 blanked, upper pin) both green. No bound movement.

3. **M_V12_CLOSE SURVIVED.** Applied on a scratch copy (full 500 tests). The `Connection: close` header is still sent at `:600` via `send_header`; the `self.close_connection = True` at `:619` is defense-in-depth for a client that ignores the header. No existing test exercises the server-side socket-closure behavior after streaming. The prior round's killer attribution (`test_framing_domain_table[no_cl/GET/v1/models/nocred]`) was wrong (that test exercises GET, not streaming).

4. **PC leg: NOT run here.** No bridge banner this session.

## DISCREPANCIES

1. **Test count.** PIN baseline: 469 passed. Final: 500 passed. Delta: +31.

2. **CTL_PARTIAL_noC1 equivalence.** The brief (item 5) says "mutant CTL_PARTIAL_noC1 must die". It is EQUIVALENT due to the interaction between utf8_redecode_lenient (item 2) and the C1 wire form: the lenient decode provides a secondary path that recovers the token without strip_invis's C1 arm. The C1 wire form test (`test_credential_c1_control_wire_form_returns_400`) is still GREEN on the final tree (the non-mutant strip_invis catches it at depth 1), and the test IS a control that exercises the detection path. But it cannot distinguish the strip_invis path from the lenient-decode path, so the mutant survives.

3. **M_UTF8_DEL removed.** Prior rounds killed this mutant because the closure had no lenient decode. With the lenient decode added (item 2), the strict decode was subsumed. Per the follow-up directive, the unpinnable op was removed rather than kept as an optimization. M_UTF8_DEL is now N/A.

## SELF-ATTACK

1. **strip_invis is more expensive per character than the former strip_ws/strip_ctl/strip_zwc** (it calls `unicodedata.category` for each character). The cost table shows no material regression: at 1000 KB, ordinary is 0.164s (vs verify-D5h's 0.227s at load 1.69). The category lookup is O(1) per character. Ruled out as a problem by the measurement.

2. **The lenient decode creates an alternative detection path that makes CTL_PARTIAL_noC1 unpinnable.** The strip_invis Cc arm still catches C1 controls at depth 1. The lenient decode catches them at depth 2. The detection is redundant, not missing. A future refactor that removes the lenient decode would re-expose the gap. Ruled out as a current defect; the C1 test exercises the detection; `strip_invis`'s docstring at `:177-181` records the dual coverage.

3. **The closure has 5 ops (down from 7 in D5h: strip_ws/strip_ctl/strip_zwc removed, strict utf8_redecode removed, utf8_redecode_lenient and strip_invis added), which changes saturation behavior.** Tested: `test_saturating_junk_is_served` (pins depth 5 from below) and `test_bound_exceeded_blanks_the_record` (pins from above) both green. The `%252B` vector saturates at depth 5 with 5 ops; the `%25252541` vector does not. No bound movement. Ruled out by the paired pinning tests.
