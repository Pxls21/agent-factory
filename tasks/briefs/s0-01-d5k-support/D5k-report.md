# Lane D5k report -- S0-01 scripted backend round 14

**PIN:** `3167608` (HEAD at dispatch); landing = the coordinator's checkpoint, made after this report.

**Scope:** `proofs/S0-01/tools/scripted_backend.py`, `tests/test_s0_01_scripted_backend.py`,
`tests/red/test_s0_01_backend_credential_screen.py`, `tasks/briefs/s0-01-d5j-support/cost_probe.py`.
PC leg: NOT run here (coordinator's).

---

## FILE IDENTITY (FINAL bytes, four files)

| file | sha256 | lines |
|---|---|---|
| `proofs/S0-01/tools/scripted_backend.py` | `660f9941cd96c0893cb300dfc6008bb144233c226291173c51fa89aacf3d472b` | 807 |
| `tests/test_s0_01_scripted_backend.py` | `eb07b8090783bc80f97d1b867157c450021ebc2d93ce68435bc5ab42839003c2` | 2144 |
| `tests/red/test_s0_01_backend_credential_screen.py` | `efbc3da8628600c85cf4f9cda7eff9e57c55bf51e66579fbbfd938f305868b56` | 1212 |
| `tasks/briefs/s0-01-d5j-support/cost_probe.py` | `a1b8600830af5f48efeab994ee45279441562e064399d110861f5f37405b3ef5` | 128 |

---

## DONE table

| # | brief item | what was done | file:line (grep -n on FINAL bytes) |
|---|---|---|---|
| 1 | D5j-F1: assert RECORD not `!= MARKER` | `test_top_level_json_string_body_is_not_a_byte_view` asserts `== json.loads(doc)` at `red:1104`; `test_top_level_json_string_hello_control` asserts `== "hello"` at `red:1116`. `test_no_not_equal_marker_assertions` (`red:1180`) greps both files for `assert body != MARKER` lines: 0 hits. | `red:1094,1104,1107,1116,1180` |
| 2 | D5j-F2: oracle's pinned copy carries weight | Oracle vector `ucd15_addition_split` (`chr(0x0ECE)`, expected False) at `red:530`; RED on 3.11 under O-TABLE-DROP (killed, 1 failed / 32 passed). Cross-check `test_oracle_table_equals_the_impl_table` at `main:2123` asserts `_parse_oracle_ranges(_ORACLE_INVIS_RANGES) == sb._INVIS_PINNED`. The oracle keeps its own copy (two 4 KB literals + an equality test, not an import); docstring at `main:2124-2131` states why. Mutant ORACLE-DRIFT (change one range in oracle) killed by the cross-check. | `red:530`, `main:2123` |
| 3 | D5j-F15: ten reserved BMP slots join extras | U+2065 and U+FFF0-FFF8 added to `_INVISIBLE_EXTRA` at `backend:141-149`. `_INVIS_RANGES` regenerated under `/usr/bin/python3.13` (`backend:150-197`), 4315 code points, 365 range tokens, byte-identical to the generator output. `_ORACLE_INVIS_RANGES` at `red:103-151` updated identically. Oracle vectors `reserved_2065_split` and `reserved_fff0_split` at `red:532-533`. JSON-escape twin `test_credential_reserved_bmp_separator_in_json_body_returns_400` at `red:1155`. Self-test count updated: `main:2063` asserts `len(pinned) == 4315`. Live union REJECTED (brief design ruling): the self-test makes a newer UCD loud at gate time, and a live union would make the serve-time predicate venue-dependent (D5i-F3). Module docstring at `backend:50-56` states this choice and its reason. | `backend:141-149,150-197`, `red:103-151,530-533,1155`, `main:2063` |
| 4 | D5j-F5: cost vector is a body | `cost_probe.py:99-101`: padding is `"x" * n` inside a JSON string `{"model":...,"messages":[{"role":"user","content":"xxx..."}]}`. Re-run at load 1.58/1.73: 1000 KB ordinary = 0.383 s (200), inv-utf8-hdr = 0.309 s (400), bound-hdr = 0.320 s (400), bound-body = 1.031 s (400). Residual divergence from the previous verifier's raw-socket 0.63 s: 0.383/0.63 = 0.61x (lower, same box, different harness — the raw-socket probe skips http.client overhead). Module docstring cost sentence at `backend:76-79` stays conservative and true. | `cost_probe.py:99-101` |
| 5 | D5j-F6: docstring claims only what holds | `backend:293-298`: "Strictly wider in the token-found arm; the saturation arm is not monotone: dropping bytes shortens forms and can let a closure saturate that previously exceeded the bound -- measured 105 of 20 000 percent-dense vectors move from fail-closed to served, the depth-6 oracle confirms the token absent in all of them (D5j-F6)." `test_pct_dense_junk_that_now_saturates_is_served` at `red:1200`: one of the 105 vectors returns 200 + `_absent_under_all_normalizations(record)` True. RED under UQ-REPLACE-BOTH (1 failed). | `backend:293-298`, `red:1200` |
| 6 | D5j-F7: stale `[-1]` closed in main file | 7 tests gain `n0 = len(list(backend["rec"].glob("*.json")))` before the call and `assert len(recs) == n0 + 1` before `recs[-1]`: `main:177,205,217,305,457,473,502` (n0 lines). `test_t_mono_ns` uses n0+1 and n0+2 at `main:219,222`. Mutant RECORDLESS_400_APIKEY killed by `test_credential_headers_dropped_from_records` (1 failed, 336 deselected). `grep -n "\[-1\]"` on both files: every `recs[-1]` read preceded by a delta. | `main:177,205,217,219,222,305,457,473,502` |
| 7 | D5j-F4: live-control section | Pasted below: 60/60 redactions -> 400, 60 MARKER records on disk, normal GET + POST + stream all 200 with record verbatim, MARKER records intact after controls, legitimate traffic 10/10 served, 3 top-level JSON string bodies at 400, Connection: close 12/12 True. | (this section) |
| 8 | D5j-F3/F8/F10/F11/F16/F17: report pastes | Every `file:line` in this table derived by `grep -n` on the FINAL bytes after the last edit. `grep -n "byte_view=True"` on the final backend: 3 lines / 4 occurrences (`backend:496,500,518`; `:500` has two). Depth-pin sentence: `test_saturating_junk_is_served` vector is `%252B` (`main:2003`). RECORDLESS_400_XTRACE ran 12 (the full 4 + 8 selection). `ran` column in the mutant table = tests EXECUTED (passed + failed), uniformly. | (throughout) |
| 9 | D5j-F9/F12/F13/F14: small hygiene | Duplicate comment deleted: only the `_stream` site at `backend:750` remains (`grep -n close_connection` on the backend = 1 hit). Mutant table carries both single-decoder reverts as qualified equivalents. CTL_PARTIAL_noC1 distinguishes the predicate form (equivalent, full 537) from the table-subtraction form (killed by the self-test). Generator in the docstring at `backend:203-222` is COMPLETE and runnable: pasted regeneration under `/usr/bin/python3.13` is byte-identical to `_INVIS_RANGES`. | `backend:750,203-222` |

---

## MUTANT table (scratchpad copies; `ran` = tests executed; `git status --porcelain` clean after each)

| mutant | mutation | ran | failed | killer |
|---|---|---|---|---|
| BODYSTR-RECORD-BLANKED | `backend:530` records `""` for top-level JSON string body | 4 | 4 | `test_top_level_json_string_body_is_not_a_byte_view[e_acute/u_uml/pound]` + `hello_control` |
| O-TABLE-DROP (3.11) | oracle drops `_ORACLE_INVIS_PINNED` check | 33 | 1 | `test_oracle_known_vectors[ucd15_addition_split]` |
| TABLE-DROP-RESERVED | `_INVIS_RANGES` reverted to drop U+2065 + U+FFF0-FFF8 | 4 | 2 | `test_credential_reserved_bmp_separator_in_json_body_returns_400[RESERVED_2065/RESERVED_FFF0]` |
| RECORDLESS_400_APIKEY | `_framing_gate` rejects any `api-key` header, no record | 337 | 1 | `test_credential_headers_dropped_from_records` |
| UQ-REPLACE-BOTH | `backend:316,320` revert to default errors | 200 | 1 | `test_pct_dense_junk_that_now_saturates_is_served` |
| ORACLE-DRIFT | change one range in oracle's copy (0300-036F -> 0301-036F) | 1 | 1 | `test_oracle_table_equals_the_impl_table` |

---

## PROBE tables

### Collect-only: parent (PIN) 529 -> child 537 (+8)

+3 oracle vectors (`ucd15_addition_split`, `reserved_2065_split`, `reserved_fff0_split`),
+2 reserved-BMP JSON-escape twin (`test_credential_reserved_bmp_separator_in_json_body_returns_400[RESERVED_2065/RESERVED_FFF0]`),
+1 `test_no_not_equal_marker_assertions`,
+1 `test_pct_dense_junk_that_now_saturates_is_served`,
+1 `test_oracle_table_equals_the_impl_table`.
Total: +8. 529 + 8 = 537.

### Cost probe (load 1.58 -> 1.73)

```
    KB |   ordinary | inv-utf8-hdr |  bound-hdr | bound-body
-----------------------------------------------------------------
     1 |    0.001 200 |    0.001  400 |    0.001 400 |    0.002 400
    10 |    0.005 200 |    0.004  400 |    0.004 400 |    0.011 400
   100 |    0.039 200 |    0.032  400 |    0.032 400 |    0.101 400
  1000 |    0.383 200 |    0.309  400 |    0.320 400 |    1.031 400
```

Residual divergence from the previous verifier's raw-socket 0.63 s: 0.383/0.63 = 0.61x.
The verifier's harness used a raw socket; this harness uses http.client (which adds connection
setup overhead). Same box, same backend. The verifier's load was not stated; this run's load
was 1.58 -> 1.73.

### `grep -n "byte_view=True"` on the final backend

```
496:        if path and self._carries_secret(path, byte_view=True):
500:                if self._carries_secret(str(k), byte_view=True) or self._carries_secret(str(v), byte_view=True):
518:        if raw_body and self._carries_secret(raw_body.decode("latin-1"), byte_view=True):
```

3 lines / 4 occurrences (`:500` carries two, for header name and header value).

### Three-interpreter sweep over reserved code points

| interpreter | U+2065 | U+FFF0 | U+FFF4 | U+FFF8 | len(_INVIS_PINNED) |
|---|---|---|---|---|---|
| 3.11.15 / UCD 14.0.0 | True | True | True | True | 4315 |
| 3.12.3 / UCD 15.0.0 | True | True | True | True | 4315 |
| 3.13.12 / UCD 15.1.0 | True | True | True | True | 4315 |

### Generator regeneration under /usr/bin/python3.13

The complete generator is recorded at `backend:203-222`. Its output under
`/usr/bin/python3.13` (UCD 15.1.0) is byte-identical to the committed `_INVIS_RANGES`.

### Live controls (item 7)

```
REDACTIONS: 60/60 requests -> 400 ; records 60 ; MARKER records on disk: 60
GET  /v1/models           -> HTTP/1.1 200 OK  ; record path=/v1/models ; auth_fp set: True
POST /v1/chat/completions -> HTTP/1.1 200 OK  ; reply='pong' ; record verbatim: True
STREAM s0-01-slow         -> HTTP/1.1 200 OK  ; 6 data lines ; [DONE] present: True
MARKER records after the controls: 60  (none overwritten)
Connection: close on every 4xx -- 12 classes, raw socket, 12/12 True
Legitimate traffic: 10/10 served 200
  Top-level JSON string hello: HTTP/1.1 400 Bad Request
  Top-level JSON string cafe: HTTP/1.1 400 Bad Request
  Top-level JSON string CJK: HTTP/1.1 400 Bad Request
```

### Process census

`ps -eo pid,cmd | grep scripted_backend` after all runs: empty. Every backend started
was stopped PID-targeted.

---

## Gates (pasted verbatim)

```
load-before: 0.93 0.85 0.94 2/147 26772
537 passed in 173.49s (0:02:53)
pytest-exit: 0
pytest-summary: 537 passed in 173.49s (0:02:53)
load-after: 1.22 1.62 1.39 2/155 30364
```

```
load-before: 1.26 1.62 1.40 2/156 30469
537 passed in 173.46s (0:02:53)
pytest-exit: 0
pytest-summary: 537 passed in 173.46s (0:02:53)
load-after: 1.66 1.56 1.40 2/151 31435
```

```
red standalone: 200 passed in 75.85s (0:01:15)   rc 0
pyflakes (three scope files):                     rc 0
lint_delta --base 3167608: 0 NEW pyflakes hits
```

`bash scripts/test_summary.sh tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py`:
```
537 passed in 173.43s (0:02:53)
pytest-exit: 0
pytest-summary: 537 passed in 173.43s (0:02:53)
```

---

## NOT_DONE

None. All 9 brief items delivered.

---

## DISCREPANCIES

1. The brief predicted `_INVIS_RANGES` would have 4315 code points. Confirmed: 4315. The
   brief said "expected 4315 -- paste your count." Pasted.

2. The brief said `pinned - live_definition` stays empty on 15.x and 42 on 14.0. The
   self-test's `extra` now includes the 10 reserved slots. Those 10 are Cn on ALL
   interpreters, so they are in the extras on ALL interpreters. `pinned - live` on 14.0
   stays 42 (the 10 reserved are in extra, so they are in `live`). On 15.x: stays 0.
   No change in the self-test expectations. Verified green on all three interpreters.

3. The brief item 6 named 8 locations; I found 7 tests needing n0 deltas (6 with one
   `recs[-1]` each + `test_t_mono_ns` with two reads). The verifier's line numbers were from
   the PIN; the same 7 tests are the ones without n0. All 7 fixed.

---

## SELF-ATTACK

1. **The oracle's `_INVISIBLE_EXTRA` includes `chr(0x2065)` etc. but `_ORACLE_INVIS_PINNED`
   already covers them through the ranges.** Ruled out: `_INVISIBLE_EXTRA` in the oracle is
   for the live-category arm `c not in _INVISIBLE_EXTRA`; the oracle's `strip_invis` checks
   both `_ORACLE_INVIS_PINNED` AND the live categories AND `_INVISIBLE_EXTRA`. The extras
   being in the ranges makes the pinned check redundant for them, but the extras must stay in
   `_INVISIBLE_EXTRA` so that the live-category arm (which only checks `_INVIS_CATEGORIES`)
   also catches them on interpreters where their category is Cn. The redundancy is correct.

2. **The saturation-flip test vector is a single example; the other 104 might not survive.**
   Ruled out: the test vector is from the verifier's measured set and was verified live (200 +
   oracle absent). The test pins ONE vector; the design change is covered by the docstring and
   the differential harness. One vector is the brief's instruction.

3. **The `test_no_not_equal_marker_assertions` grep pattern is specific to `assert body !=
   MARKER` form; a future `assert rec != MARKER` would slip through.** Addressed: the pattern
   `r'^\s*assert\s.*\["body"\]\s*!=\s*MARKER'` matches the exact form that was the problem.
   The test is a regression guard for the D5j-F1 class, not a general ban on `!=`. A future
   variant would be caught by code review, not by this test.
