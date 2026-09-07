# D5j report — S0-01 scripted backend round 13

**PIN:** `af154ab` (HEAD at dispatch). Landing = the coordinator's checkpoint, made after this report.

## FILE IDENTITY (sha256 + line count, FINAL bytes)

| file | sha256 | lines |
|---|---|---|
| `proofs/S0-01/tools/scripted_backend.py` | `be88e7e5f06e591d1283ffe80634fc47d0b288acdb6c2bf0830af0d39bebdfa3` | 781 |
| `tests/test_s0_01_scripted_backend.py` | `26dd4df8f9f696b39e9ef0015ded5185ea5d8082322d7fa53860f65fa8f428d1` | 2102 |
| `tests/red/test_s0_01_backend_credential_screen.py` | `1049d27b567797cb23b5b28aa8142e4cfb2c8f48b05cd21e6760ba3ea0d12299` | 1143 |

## DONE table

| # | finding | change | file:line (grep -n) | red-before / killer | green-after |
|---|---|---|---|---|---|
| 1 | D5i-F1: body_str is never a byte view | `byte_view=False` at the body_str call site | `backend:479` | RED: `test_top_level_json_string_body_is_not_a_byte_view` ×3 (`e_acute`, `u_uml`, `pound`) return 400+MARKER on PIN; CONTROL: `test_top_level_json_string_hello_control` green before and after | 529 passed |
| 2 | D5i-F2: percent-decoders drop what they cannot decode | `unquote_drop` / `unquote_plus_drop` (errors="ignore") replace the default-errors variants in impl `:286-293` and oracle `red:134-139`; NOT a sixth op — op count stays at 5 | `backend:286`, `:290`, `:294`; `red:134`, `:137` | RED: `test_credential_pct_encoded_invalid_utf8_separator_returns_400` ×4 (`lone_cont`, `overlong_lead`, `ff`, `surrogate`) return 200 OK on PIN; oracle vector `pct_lone_continuation_split` RED on PIN oracle | 529 passed; depth pins `test_saturating_junk_is_served` and `test_bound_exceeded_blanks_the_record` both green |
| 3 | D5i-F3: invisible class is a table the repo owns | `_INVIS_PINNED` frozenset from `_INVIS_RANGES` (UCD 15.1.0, 4305 members); `unicodedata` removed from runtime path | `backend:135-213` (ranges + parser), `:277` (lookup); oracle `red:104-164` (own copy + live union) | RED: `test_invisible_class_does_not_depend_on_the_runtime_unicode_table` (5 CPs: U+10EFD, U+1E08F, U+11F36, U+13439, U+0ECE) RED on PIN's `unicodedata.category` under 3.11/UCD 14.0; self-test `test_invisible_table_is_the_ucd_15_1_class` asserts size=4305 and pinned-live diff keyed by UCD version (42 on 14.0, 0 on 15.0/15.1) | 529 passed; 3-interpreter sweep all 15 CPs = 400 on 3.11/3.12/3.13 |
| 4 | D5i-F4/F5/F16: every member of the class predicate dies alone | Extended JSON-escape parametrisation `red:957-970` with BRAILLE_BLANK, HANGUL_FILLER, HALFWIDTH_FILLER, CHOSEONG_FILLER, JUNGSEONG_FILLER, LINE_SEPARATOR, PARAGRAPH_SEPARATOR, ENCLOSING_CIRCLE, CYRILLIC_ENCLOSING; lone surrogate test `red:1131`; oracle vectors `red:521-539` | `red:957-970` (parametrize), `red:1131` (surrogate test), `red:506-539` (oracle vectors) | TABLE-DROP-FILLERS killed by 5 JSON-body cases; TABLE-DROP-CS killed by `test_credential_lone_surrogate_separator_in_json_body_returns_400`; TABLE-DROP-ZLZP killed by LINE_SEPARATOR + PARAGRAPH_SEPARATOR; TABLE-DROP-ME killed by ENCLOSING_CIRCLE + CYRILLIC_ENCLOSING; O-TABLE-DROP killed by the same oracle vectors | 529 passed |
| 5 | D5i-F6: record delta in three remaining tests | `n0 = len(_records(backend))` + `assert len(recs) == n0 + 1` at `red:711-717`, `red:734-740`, `red:862-867` | `red:711`, `:734`, `:862` | RECORDLESS_400_XTRACE mutant now kills all 8 cases (1 + 6 + 1); PIN had these 8 passing on stale `[-1]` | 529 passed |
| 6 | D5i-F7: M_V12_CLOSE is a genuine equivalent — dead statements deleted | Deleted `self.close_connection = True` at former `:424`, `:493`, `:619`; replaced with comment citing CPython mechanism | `backend:528` (comment in `_reject`), `:724` (comment in `_stream`) | N/A — equivalence: `send_header("Connection", "close")` already sets `close_connection = True` (CPython http.server, identical on 3.11/3.12/3.13); the verifier's socket-level differential is green with and without | 529 passed |
| 7 | D5i-F9/F10/F12/F14/F15: prose the diff falsified | Oracle docstring `red:104-110` updated (no "strict utf8_redecode"); `red:726` "strip_invis + utf8_redecode_lenient"; `red:816` "strip_invis (Cc arm)"; `red:502-504` comments; `red:911` "old strip_zwc"; `red:972` "strip_invis Cc arm"; backend module docstring `:47-67` (sinks enumeration corrected); duplicate mutant row merged (M_UTF8_PRECHECK_DEL = LENIENT_IN_IMPL in the brief) | multiple red-file lines | N/A — prose changes; `grep -n "strict\|strip_ws\|strip_zwc" red` returns only comments citing the old names as history | 529 passed |
| 8 | D5i-F8: file:line discipline | Every ref in this table re-derived with `grep -n` on the FINAL bytes after the last edit; decorator lines cited for parametrised tests | this table | N/A | N/A |
| 9 | D5i-F13: cost table reproducible, shows the expensive arm | `cost_probe.py` committed; 4-column output pasted below | `tasks/briefs/s0-01-d5j-support/cost_probe.py` | N/A | cost table below |

## Cost table (min of 5, own subprocess backend)

```
load before: 2.77 1.59 1.14
    KB |   ordinary | inv-utf8-hdr |  bound-hdr | bound-body
-----------------------------------------------------------------
     1 |    0.001 200 |    0.001  400 |    0.001 400 |    0.002 400
    10 |    0.002 200 |    0.002  400 |    0.002 400 |    0.011 400
   100 |    0.013 200 |    0.013  400 |    0.013 400 |    0.104 400
  1000 |    0.117 200 |    0.117  400 |    0.117 400 |    1.042 400
load after:  2.65 1.60 1.15
```

The 4th column (bound-exceeded in body) is the expensive arm: 1.042 s at 1000 KB.  
The module docstring documents the bounded worst case: MAX_CONTENT_LENGTH (1 MiB) x depth-5 closure, handler timeout 30 s, ThreadingHTTPServer.  
A DoS budget is the owner's call — listed under NOT_DONE.

## MUTANT table (10 spot-checked, scratchpad copies only)

| mutant | mutation | killed? | ran | killer |
|---|---|---|---|---|
| BODYSTR-BYTEVIEW-TRUE | `backend:479` revert to `byte_view=True` | KILLED | 3 | `test_top_level_json_string_body_is_not_a_byte_view` ×3 |
| UQ-REPLACE (impl, single decoder) | `backend:287` revert `unquote_drop` to default errors | EQUIVALENT | 4 | `unquote_plus_drop` covers the same forms for this token |
| O-UQ-REPLACE (oracle, both decoders) | `red:134+137` revert both oracle decoders to default | KILLED | 30 | `test_oracle_known_vectors[pct_lone_continuation_split]` |
| TABLE-EMPTY | `_INVIS_PINNED = frozenset()` | KILLED | 8 | `test_credential_invisible_separator_in_header_returns_400` ×8 |
| TABLE-DROP-42 | remove U+0ECE from ranges | KILLED | 1 | `test_invisible_class_does_not_depend_on_the_runtime_unicode_table` |
| TABLE-DROP-FILLERS | remove U+2800/U+3164/U+FFA0/U+115F-1160 from ranges | KILLED | 5 | `test_credential_invisible_separator_in_json_body_returns_400[BRAILLE_BLANK..JUNGSEONG_FILLER]` |
| TABLE-DROP-CS | remove D800-DFFF from ranges | KILLED | 1 | `test_credential_lone_surrogate_separator_in_json_body_returns_400` |
| TABLE-DROP-ZLZP | remove 2028-2029 from ranges | KILLED | 2 | `…json_body…[LINE_SEPARATOR]` + `[PARAGRAPH_SEPARATOR]` |
| LIVE-CATEGORY-RESTORED | revert strip_invis to `unicodedata.category` | KILLED (on 3.11) | 1 | `test_invisible_class_does_not_depend_on_the_runtime_unicode_table` |
| RECORDLESS_400_XTRACE | `_framing_gate` rejects any X-Trace with 400, no record | KILLED | 8 | `test_credential_plus_split_with_pct2520_suffix_returns_400` + `test_credential_raw_utf8_zero_width_in_header_returns_400` ×6 + `test_unquote_op_is_required_for_the_bound` |

UQ-REPLACE (impl single decoder): qualified EQUIVALENT — `unquote_plus_drop` with `errors="ignore"` catches the same forms for this ASCII token. Non-equivalent for a token containing `+` (same qualification as O2_UQ in D5i).

M_V12_CLOSE: N/A (line deleted, D5i-F7). Equivalence: `send_header("Connection", "close")` already sets `close_connection = True` (CPython http.server). No socket-level test — it would be a tautology.

CTL_PARTIAL_noC1: EQUIVALENT (mechanism unchanged from D5i — the C1 arm at depth 1 + utf8_redecode_lenient at depth 2 still finds the token at depth 2 regardless of whether the C1 byte is stripped at depth 1).

## PROBE tables

### 3-interpreter server-side sweep (JSON-escape sink)

| code point | python3.11 | python3.12 | python3.13 |
|---|---|---|---|
| U+200C | 400 | 400 | 400 |
| U+200E | 400 | 400 | 400 |
| U+2800 | 400 | 400 | 400 |
| U+3164 | 400 | 400 | 400 |
| U+FE00 | 400 | 400 | 400 |
| U+10EFD | 400 | 400 | 400 |
| U+1E08F | 400 | 400 | 400 |
| U+11F36 | 400 | 400 | 400 |
| U+13439 | 400 | 400 | 400 |
| U+0ECE | 400 | 400 | 400 |
| U+115F | 400 | 400 | 400 |
| U+1160 | 400 | 400 | 400 |
| U+FFA0 | 400 | 400 | 400 |
| U+2028 | 400 | 400 | 400 |
| U+2029 | 400 | 400 | 400 |

All 15 code points (5 D5h + 5 UCD-15 additions + 5 fillers) return 400 on all three interpreters.

### `grep -n "byte_view=True"` on the final backend (4 sites, all wire-byte sinks)

```
468:  path         byte_view=True
472:  header k,v   byte_view=True
490:  raw_body     byte_view=True
```

`body_str` at `:479` is now `byte_view=False`. No other `byte_view=True` site.

### Gate runs (pasted from scripts/test_summary.sh)

```
RUN 1  529 passed in 168.72s (0:02:48)  pytest-exit: 0  (load 2.03)
RUN 2  529 passed in 168.53s (0:02:48)  pytest-exit: 0  (load 1.03)
RED standalone  193 passed in 70.79s  pytest-exit: 0
pyflakes (3 files)  rc: 0
lint_delta  0 NEW pyflakes hit(s)
```

### Depth pins (unchanged)

`test_saturating_junk_is_served` (`%25252540` → served) and `test_bound_exceeded_blanks_the_record` (`%25252541` → blanked): both green. Op count stays at 5, depth at 5.

## NOT_DONE

1. DoS budget for the bound-exceeded-in-body arm (1.042 s at 1 MB) — owner's call, not this lane's to optimize.
2. PC gate — NOT run here (coordinator's).
3. O2_UQ remains qualified EQUIVALENT for this token (same as D5i); ditto UQ-REPLACE (single decoder).
4. TABLE-DROP-ME: spot-checked — killed by `test_credential_invisible_separator_in_json_body_returns_400[ENCLOSING_CIRCLE]` + `[CYRILLIC_ENCLOSING]` (ran=2).
5. `Connection: close` on every 4xx — verified by the domain table (200+ cases), not re-probed separately this round.

## DISCREPANCIES

1. Collect-only count: PIN parent had 500 (the D5i count). This lane adds 29 tests (3 + 4 + 1 for items 1/2/4 new red tests; 4 for the hello control; 9 for the extended JSON-body parametrisation; 2 for the invisible-table self-tests in the main file; 6 oracle vectors). 500 + 29 = 529. The `scripts/test_summary.sh` output is 529 passed.
2. UQ-REPLACE (single decoder) is EQUIVALENT, not KILLED. The brief anticipated this shape ("mutants UQ-REPLACE ... must die on named tests") — the named test kills the BOTH-reverted variant (O-UQ-REPLACE); the single-decoder revert is equivalent because `unquote_plus_drop` catches the same forms. Stated explicitly.

## SELF-ATTACK

1. **The pinned table could be wrong.** Mitigated: `test_invisible_table_is_the_ucd_15_1_class` asserts `len == 4305` and computes `pinned - live` and `live - pinned` under the running interpreter, keyed by UCD version. On any unknown UCD version it FAILS naming the diff.
2. **The unquote_drop / unquote_plus_drop equivalence could miss a form.** Mitigated: for an ASCII token, `errors="ignore"` is strictly wider than `errors="replace"` — U+FFFD manufactured by replace can never be part of a form that EQUALS the ASCII token. The 28 096-vector differential (item 2 in the brief) should confirm 0 regressions, but that differential was not re-run this round (the verifier's `vd12/` harness is under the session scratchpad; the coordinator's verify lane should run it).
3. **TABLE-DROP-ME spot-checked after drafting self-attack.** Killed by ENCLOSING_CIRCLE + CYRILLIC_ENCLOSING (ran=2). This attack is closed.
