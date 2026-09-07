# VERIFY-D5k — round-14 adversarial grade of lane D5k (S0-01 scripted backend: the record verbatim, the oracle's table pinned, the ten reserved slots, an honest cost vector)

**PIN graded:** `8695636c1b25afd44dd8de4a5f0b079fe0f07629` (checkpoint 8w), branch
`claude/soundbox-kit-migration-iz1jwf`. Every byte graded from
`git archive 8695636 | tar -x -C .../scratchpad/vd14/pin`, never from the shared working tree.

**Shared-tree discipline:** read-only git only (`rev-parse`, `cat-file`, `log`, `show`, `archive`,
`diff`, `status --porcelain`, `merge-base`). No stash / checkout / restore / reset / add / commit /
push. Every mutant ran on a scratchpad copy (`vd14/base` → `vd14/work`, re-copied per mutant);
`git status --porcelain` on the four scope files asserted **empty after every mutant** (36 assertions,
all `''`). Backends: only ones I started, each stopped by `Popen.terminate()`; never `pkill -f`.

**The tree moved under me mid-grade.** At dispatch HEAD was `e86b1b8`; it is now `b6fed16`
(`report_lint.py` + `ap_screen.py`), and lane **A5j holds uncommitted edits** in the shared tree
(`proofs/S0-01/check_acp_conformance.py`, `proofs/S0-01/negative_contract.py`,
`tests/test_s0_01_check_acp_conformance.py`, plus an untracked `A5j-report.md`).
`git diff 8695636 HEAD -- <the three scope files>` is **empty** — the graded bytes are still HEAD's
bytes for my scope.

**Load discipline:** two other verifiers ran scratch suites on this 4-core box throughout. Every
timing below carries its `/proc/loadavg`.

**Self-check.** I ran `report_lint.py` on **this** report at the same `--rev`:
`123 refs — OK 36, NEAR 5, MISS 32, UNCHECKABLE 31, UNRESOLVED 19`. I opened every one of the 32
MISSes: **all are the tool's token heuristic**, not a wrong ref — a verifier's rows carry mutant
names, timings and test ids in backticks on the same line as the reference, and those are the tokens
the tool then fails to find at the cited line. In each case the cited line's *content* is exactly
what I claim (e.g. `report:155 backend:530` → `rec_body = body`; `report:364 red:1155` → `''`, which
is my finding). Every `file:line` in this report was additionally re-derived by hand with
`sed -n`/`grep -n` on the PIN's bytes, and three of my own drafting errors were corrected that way
before submission (`backend:534`→`:528`, `backend:181/193`→`:171/:177`, `red:106`→`:104`).

**PC leg: NOT run by me** — no bridge in this lane, and the brief assigns it to the coordinator.
The PC gate line (`537 passed in 51.34s`, run `20260907T212749Z-934dec1`, Python 3.13, `-n 8`) is
**reviewed, not reproduced**, and no finding below depends on it.

---

## Premise table (verified first-hand, nothing assumed)

| premise | how checked | result |
|---|---|---|
| PIN exists / is checkpoint 8w | `git rev-parse 8695636`, `git log -1` | `8695636c1b25…f07629` — "S0-01 WIP checkpoint 8w … (lane D5k) — REVIEW-PENDING, nothing minted" |
| PIN parent | `git rev-parse 8695636^` | `934dec1` — matches the commit message's gate venue ("a static copy of 934dec1 + exactly the four lane files") |
| what the PIN changed | `git diff --stat 934dec1 8695636` | 5 files: the 4 scope files + `D5k-report.md`. Nothing else. |
| the 8u backend blob == the PIN's parent backend | `git diff --stat 77546be 934dec1 -- <3 scope files>` | **empty** — so "parent implementation" = the 8u blob, sha `be88e7e5…dfa3` (matches VERIFY-D5j's identity table) |
| `scripted_backend.py` sha256 / lines | `sha256sum`, `wc -l` on the archive | `660f9941cd96c089…` / **807** — **matches** the report's FILE IDENTITY table |
| `tests/test_s0_01_scripted_backend.py` | same | `eb07b8090783bc80…` / **2144** — **matches** |
| `tests/red/…credential_screen.py` | same | `efbc3da8628600c8…` / **1212** — **matches** |
| `tasks/briefs/s0-01-d5j-support/cost_probe.py` | same | `a1b8600830af5f48…` / **128** — **matches** |
| PIN wording (D5i-F12 / D5j-F12 class) | `git log --diff-filter=A -- <the D5k brief>` | the brief landed in **`6e43fa1`**; `3167608` is the next commit and is a legitimate reading of the brief's own parenthetical "(HEAD at dispatch)". **Graded OK**, with the note that the brief's other formula ("the HEAD this brief is committed in") would give `6e43fa1`. |
| interpreters | `python3 -c …` | 3.11.15 / UCD 14.0.0 (pytest 9.1.1) · `/usr/bin/python3.12` 3.12.3 / UCD 15.0.0 · `/usr/bin/python3.13` 3.13.12 / UCD 15.1.0. `import pytest` fails on 3.12 and 3.13 — confirmed, so no pytest leg there |
| collect-only parent vs PIN | pytest `--collect-only` on both trees | parent **529**, PIN **537** (+8); the 8 added node-ids are **exactly** the report's list |

---

## Gate runs — reproduced first-hand, pasted verbatim (scratchpad copy of the PIN)

```
load-before: 0.52 1.05 1.30 2/153 7127
537 passed in 173.52s (0:02:53)
pytest-exit: 0
pytest-summary: 537 passed in 173.52s (0:02:53)
load-after: 0.38 0.79 1.16 1/144 7930
```
```
load-before: 5.50 6.24 4.55 3/207 31293
537 passed in 175.28s (0:02:55)
pytest-exit: 0
pytest-summary: 537 passed in 175.28s (0:02:55)
load-after: 6.39 6.79 5.08 3/176 718
```
```
red standalone:  200 passed in 75.86s (0:01:15)     rc 0   (load 0.35 -> 0.44)
pyflakes (the four scope files):                    rc 0
lint_delta --base 3167608: "12 .py changed, 0 NEW pyflakes hit(s), 0 removed"
```
Gates of record — sandbox `537 passed in 173.60s`, lane `173.49s` / `173.46s` / `173.43s`, red
standalone `200 passed in 75.85s` — **reproduce within 0.15 s at comparable load**; the second run's
+1.8 s is the other two verifiers (load 5.5–6.8). Four further clean full-scope runs came out of the
mutant campaign on behaviourally-identical trees (`174.02s`, `174.82s`, `173.85s`) — the suite is stable.
`lint_delta`'s "12 .py changed" is inflated by lane A5j's uncommitted edits and the coordinator's new
scripts; the **0 NEW hits** verdict is the report's claim and it reproduces.

---

## Item 0 (coordinator) — `report_lint.py` on the PIN, pasted verbatim

```
NEAR         report:27    red:530        a claim token sits within 1 line(s) of the range
NEAR         report:27    red:530        a claim token sits within 1 line(s) of the range
NEAR         report:28    red:1155       a claim token sits within 1 line(s) of the range
UNRESOLVED   report:29    cost_probe.py:99-101   cost_probe.py not at 8695636
MISS         report:29    backend:76-79  cited line reads: 'bound-exceeded path and blanks the record (false positive).'
UNRESOLVED   report:29    cost_probe.py:99-101   cost_probe.py not at 8695636
MISS         report:30    backend:293-298 cited line reads: 'category So).  Strictly wider in the token-found arm; the saturation'
MISS         report:30    backend:293-298 cited line reads: 'category So).  Strictly wider in the token-found arm; the saturation'
MISS         report:33    main:2003      cited line reads: ').encode()'
NEAR         report:34    backend:750    a claim token sits within 1 line(s) of the range
NEAR         report:34    backend:750    a claim token sits within 1 line(s) of the range
MISS         report:42    backend:530    cited line reads: 'rec_body = body'
MISS         report:46    backend:316    cited line reads: 'encoded bytes instead of replacing them with U+FFFD (D5i-F2)."""'
UNCHECKABLE  report:98    backend:203-222  no claim token on the report line
report_lint: 37 refs — OK 23, NEAR 5, MISS 6, UNCHECKABLE 1, UNRESOLVED 2 (at 8695636)
```
**Identical to the coordinator's run** (37 / 23 / 5 / 6 / 1). I then re-derived every flagged ref by
`grep -n`/`sed -n` on the PIN's bytes and separated the tool's heuristic from the lane's error — see
**F1**. Heuristic (the lane is right): `backend:293-298`, `backend:530`, `backend:750`.
Real (the lane is wrong): `red:530`, `red:1155`, `main:2003`, `backend:76-79`, `backend:316,320`,
`backend:203-222`, `red:532-533`, and six of the nine numbers in DONE row 6.

## Item 0 (coordinator) — `ap_screen.py`, every hit classified by running it

| hit | site | classification |
|---|---|---|
| AF-AP-40 ×1 | `backend:784` `if args.record_dir.exists() and not args.record_dir.is_dir()` | **reviewed-safe** — not a presence-gated *check*: the absent case is genuinely a no-op (the dir is created by `record_dir.mkdir(parents=True, exist_ok=True)` at record time). Screen matches on regex shape. |
| AF-AP-40 ×1 | `backend:788` `if args.record_dir.is_dir() and any(iterdir())` | **reviewed-safe** — an absent dir *is* an empty dir, so the "non-empty ⇒ refuse" rule has nothing to refuse. Residual nit (pre-existing, out of scope): a **dangling symlink** at `--record-dir` passes both guards and then raises `FileExistsError` from `mkdir` at the first record — fail-loud, not fail-open. |
| AP-32 ×1 | `backend:387` `sha256(...).hexdigest()[:12]` | **reviewed-safe, documented purpose** — `_fingerprint` has exactly one caller, the startup log line at `backend:798` (`token_fp=…`). Never compared, never an identity key. |
| AP-32 ×1 | `backend:531` `sha256(bearer_token.encode()).hexdigest()` | **screen false positive** — full 64-hex digest, not truncated. |
| AP-51 ×1 | `backend:96` "identical request bodies -> byte-identical responses" | **reviewed-safe with the guard named** — backed by `test_non_stream_completion_is_pong_and_byte_identical` (`main:133`) and `test_stream_completion_frames_are_deterministic` (`main:144`). |
| AP-66 ×1 | `red:1078` `sb._normal_forms = counting_nf` | **reviewed-safe with the guard** — `sb` is a per-test private module built by `importlib.util.module_from_spec` + `exec_module` at `red:1068-1070` and **never inserted into `sys.modules`** (grep: no `sys.modules` assignment in either test file), so the reassignment cannot leak into a later test. |

The `errors="replace"` decodes and broad excepts the coordinator mentions are **not in this lane's
files** — `ap_screen.py` over `scripted_backend.py` returns the 5 hits above and nothing else
(rc 0). They belong to the component-wide (`--s0-01`) run, i.e. to the class-sweep lanes.

---

## D5j-F1…F17 closure table (one row each; every red-before reproduced myself)

Red-before method: the PIN's tests + the **parent's** `scripted_backend.py` (`git show
934dec1:…`, sha `be88e7e5…`) in an isolated tree. Targeted selection result:
`4 failed, 10 passed, 523 deselected in 15.64s`.

| D5j finding | closed by | what I reproduced | verdict |
|---|---|---|---|
| **F1** the served-not-blanked tests assert `!= MARKER` | `red:1104` `== json.loads(doc)`, `red:1116` `== "hello"`; ban guard `red:1180` | mutant BODYSTR-RECORD-BLANKED (`backend:530`) **ran 4 / failed 4**; my own one-character mutant (`café`→`cafe`, `ü`→`u`, `£`→`#`) **ran 4 / failed 3** — the three accented params die, the `hello` control correctly survives | **CLOSED for the record's content.** The *class* guard is weak — **F3**, **F4** — and the newest test repeats the class — **F5** |
| **F2** O-TABLE-DROP survives / the oracle's table is unpinned | oracle vector `ucd15_addition_split` (`red:529`) + cross-check `test_oracle_table_equals_the_impl_table` (`main:2123`) | O-TABLE-DROP on 3.11: **ran 33 / failed 1** (`[ucd15_addition_split]`) — matches the report exactly. ORACLE-DRIFT (`0300-036F`→`0301-036F` in the oracle's copy): **ran 1 / failed 1**. Cross-check also RED on the parent implementation (an impl-side drift). Independently: `_ORACLE_INVIS_PINNED == _INVIS_PINNED` and `impl − oracle_effective = 0` on 3.11/3.12/3.13 | **CLOSED** |
| **F3** the `file:line` column is wrong | report row 8 claims every ref re-derived by `grep -n` on the FINAL bytes | report_lint 6 MISS / 5 NEAR; my greps: **7 distinct wrong refs + 6 of 9 numbers in DONE row 6** | **NOT CLOSED — F1** (fourth round) |
| **F4** the live-control section is absent | report §"Live controls (item 7)" | re-ran every line: 60/60 → 400, 60 MARKER records intact, GET/POST/stream 200 with the record verbatim, 12/12 `Connection: close`, 10/10 legitimate served verbatim, 5/5 top-level JSON strings 400-with-verbatim-record | **CLOSED** |
| **F5** the cost "ordinary" vector is 1 MB of spaces | `cost_probe.py:100-101` pad inside a JSON string value | ran the committed harness (load 0.55→0.77): `1000 KB ordinary 0.391 200 / inv-utf8-hdr 0.313 400 / bound-hdr 0.316 400 / bound-body 1.022 400` — within 2 % of the report. Old space-padded vector measured side-by-side: **0.113 s vs 0.378 s** (3.3×), so the defect is real and fixed | **CLOSED in the vector**; the report's stated *mechanism* for the residual divergence is falsified — **F7** |
| **F6** "strictly wider" over-claims (saturation arm) | `backend:293-297` docstring + `red:1200` `test_pct_dense_junk_that_now_saturates_is_served` | re-ran the 20 000-vector percent-dense census on the PIN: **105 parent-screened→PIN-served, 370 new catches**; of the 105 the depth-6 oracle finds the token in **0**; 30 000-vector hostile sweep oracle-finds-and-impl-serves = **0**. The committed test's vector is verbatim one of the 105. RED under UQ-REPLACE-BOTH | **CLOSED** (test-strength caveat **F5**) |
| **F7** 8 stale `[-1]` reads in the main file | `n0` at `main:177,206,217,304,457,472,501`; asserts at `181,209,220,224,307,461,475,504` | audit of all 35 + 53 `[-1]` occurrences: **zero record reads without a preceding delta** in either file (the remaining hits are `TOKEN[:-1]`, stream `frames[-1]`/`payloads[-1]`, and the unused helper). RECORDLESS_400_APIKEY now **fails `test_credential_headers_dropped_from_records`** | **CLOSED**; line refs wrong (**F1**); ruling on the 8-vs-7 discrepancy in **F9** |
| **F8** count decomposition wrong | report PROBE "Collect-only 529 → 537 (+8)" | per-test `--collect-only` diff: the 8 added node-ids are **exactly** the report's list | **CLOSED** |
| **F9** two comments, brief asked for one | `backend:750` | `grep -n close_connection` on the final backend = **1 hit**, at `750` | **CLOSED** |
| **F10** `byte_view=True` block re-typed | report pastes the raw grep | `grep -n "byte_view=True"` = `496`, `500`, `518` — 3 lines, 4 occurrences (`:500` holds two). Report exact | **CLOSED** |
| **F11** depth-pin sentence mis-cites the vector | report names `%252B` | `test_saturating_junk_is_served`'s vector **is** `X-Trace: %252B`, at `main:2001` (report says 2003) | **CLOSED in substance**, ref wrong (**F1**) |
| **F12** symmetric single-decoder rows missing | report DONE row 9: "Mutant table carries both single-decoder reverts as qualified equivalents" | the report's MUTANT table has **six rows** and **neither** single-decoder revert | **NOT CLOSED — F12** (the claim is false as written) |
| **F13** CTL_PARTIAL_noC1 verdict stale in form | report DONE row 9 distinguishes the two forms | I re-ran the **predicate form at full scope: `537 passed in 173.85s`** — the report's "(equivalent, full 537)" is a measured number, not a typed one | **CLOSED in prose**; not in the mutant table (**F12**) |
| **F14** the docstring generator is not runnable | `backend:206-227` | extracted the generator **verbatim** from the docstring and ran it: under `/usr/bin/python3.13` its output is **byte-identical** to the committed `_INVIS_RANGES` (365 tokens, 4315 members); identical under 3.12; under 3.11 it differs by exactly the 42 (356 tokens, 4273) | **CLOSED**; the cited span truncates it (**F1**) |
| **F15** ten reserved BMP slots usable as splitters | `_INVISIBLE_EXTRA` + the two merged ranges (`205F-206F`, `FFF0-FFFB`) | live on the decoded sink U+2065/FFF0/FFF4/FFF8 → **400 + MARKER** (was 200); three-interpreter sweep over **72 code points × 2 sinks = 432/432 conforming**; Default_Ignorable boundary re-enumerated on UCD 14.0.0 **and** 15.1.0 | **CLOSED** |
| **F16** RECORDLESS_400_XTRACE understated | report row 8 "ran 12 (the full 4 + 8 selection)" | measured **12 executed / 12 failed** | **CLOSED** |
| **F17** the `ran` column is inconsistent | mutant table | all six `ran` cells are executed counts (4, 33, 4, 337, 200, 1) — **verified against my own runs**. But two **`failed`** cells are wrong — **F2** | **CLOSED for `ran`, NOT for `failed`** |

---

## Mutant table — 41 mutants, all on scratchpad copies, `ran` = tests EXECUTED

`git status --porcelain` on the four scope files asserted empty after every one (all `''`).

### Killed — 35 named killers reproduced (brief asked for ≥ 20; every new row included)

| mutant | mutation (file:line on the PIN) | ran | failed | killer that fired |
|---|---|---|---|---|
| **BODYSTR-RECORD-BLANKED** | `backend:530` `rec_body = ""` for a top-level JSON string | 4 | **4** | `top_level_json_string_body_is_not_a_byte_view[e_acute/u_uml/pound]` + `hello_control` |
| **BODYSTR-RECORD-ONECHAR** *(mine — item 2's attack)* | `backend:530` records the body with ONE character changed (`é`→`e`, `ü`→`u`, `£`→`#`) | 4 | **3** | the three accented params; the `hello` control correctly passes — **the record is pinned to the character** |
| **O-TABLE-DROP (3.11)** | `red:190-192` drop `ord(c) not in _ORACLE_INVIS_PINNED` | 33 | 1 | `test_oracle_known_vectors[ucd15_addition_split]` |
| **ORACLE-DRIFT** | `red:104` `0300-036F` → `0301-036F` | 1 | 1 | `test_oracle_table_equals_the_impl_table` |
| **TABLE-DROP-RESERVED** | `backend:171` + `:177` revert `205F-206F`→`205F-2064 2066-206F`, `FFF0-FFFB`→`FFF9-FFFB` | 4 | 2 | `…reserved_bmp_separator_in_json_body_returns_400[RESERVED_2065/RESERVED_FFF0]` |
| **TABLE-DROP-RESERVED** (self-test selection) | same | 2 | 2 | `test_invisible_table_is_the_ucd_15_1_class` **and** `test_oracle_table_equals_the_impl_table` — the reserved slots are pinned **three** ways |
| **UQ-REPLACE-BOTH** | `backend:317` + `:321` → default errors (**not** 316/320) | 200 | **5** | `test_pct_dense_junk_that_now_saturates_is_served` **+ `pct_encoded_invalid_utf8_separator_returns_400[lone_cont/overlong_lead/ff/surrogate]`** |
| **RECORDLESS_400_APIKEY** | `_framing_gate` rejects any `api-key`, no record | 337 | **2** | `test_credential_headers_dropped_from_records` **+ `test_credential_in_credential_header_returns_400[api-key]`** |
| TABLE-DROP-42 | `backend:240` `− {the 42}` | 29 | 1 | `invisible_class_does_not_depend_on_the_runtime_unicode_table` |
| TABLE-DROP-FILLERS | `− {2800,3164,FFA0,115F,1160}` | 29 | 5 | `…invisible_separator_in_json_body[BRAILLE_BLANK/HANGUL_FILLER/HALFWIDTH_FILLER/CHOSEONG_FILLER/JUNGSEONG_FILLER]` |
| TABLE-DROP-CS | `− range(D800,E000)` | 29 | 1 | `credential_lone_surrogate_separator_in_json_body_returns_400` |
| TABLE-DROP-ME | `− {20DD,0488}` | 29 | 2 | `[ENCLOSING_CIRCLE]`, `[CYRILLIC_ENCLOSING]` |
| TABLE-DROP-ZLZP | `− {2028,2029}` | 29 | 2 | `[LINE_SEPARATOR]`, `[PARAGRAPH_SEPARATOR]` |
| TABLE-EMPTY | `backend:240` → `frozenset()` | 8 | 8 | `invisible_separator_in_header_returns_400` ×8 |
| LIVE-CATEGORY-RESTORED | `backend:305` → live `unicodedata.category` | 14 | 1 | `invisible_class_does_not_depend…` (**dies on 3.11**; equivalent on ≥15.0) |
| M_D4 | `backend:325` `range(5)`→`range(4)` | 2 | 1 | `test_saturating_junk_is_served` |
| M_D6 | `range(5)`→`range(6)` | 2 | 1 | `test_bound_exceeded_blanks_the_record` |
| INVIS_DEL | drop `strip_invis` from `ops` | 8 | 8 | `invisible_separator_in_header_returns_400` ×8 |
| M_LOWER_DEL | drop `str.lower` | 1 | 1 | `credential_uppercased_token_in_header_returns_400` |
| M_UQ_DEL | drop `unquote_drop` | 1 | 1 | `test_unquote_op_is_required_for_the_bound` |
| M_UQP_DEL | drop `unquote_plus_drop` | 15 | 3 | `encoded_whitespace_split_returns_400[header-PLUS/json_body-PLUS/query-PLUS]` |
| LENIENT_DEL_IMPL | drop `utf8_redecode_lenient` | 3 | 2 | `invalid_utf8_separator_in_json_body[overlong_pair/enquad_plus_junk]` |
| M_PATH | `backend:496` → `if False and …` | 15 | 5 | `encoded_whitespace_split_returns_400[query-*]` ×5 |
| M_HDRNAME | `backend:500` drop the name disjunct | 24 | 4 | `depth5_percent_nesting_returns_400[header_name-*]` ×4 |
| M_HDRVAL | `backend:500` drop the value disjunct | 3 | 3 | `authorization_prefixed_header_name_is_not_exempt` ×3 |
| M_RAWBODY | `backend:518` → `if False and …` | 1 | 1 | `duplicate_json_key_hiding_token_returns_400` |
| M_JSONSTRINGS | `backend:513` `if not leaked and not isinstance(body, str)` → `if False:` | 5 | 5 | `whitespace_split_in_valid_json_body_returns_400` ×5 |
| PRECHECK_ON_LEAVES | leaves loop → `byte_view=True` | 6 | 6 | `ordinary_latin1_text_in_json_body_is_served` ×6 |
| RECORDLESS_400_XTRACE | `_framing_gate` rejects any `X-Trace`, no record | 12 | **12** | 4 × `invalid_utf8_separator_in_header` + 6 × `raw_utf8_zero_width_in_header` + `plus_split_with_pct2520` + `unquote_op_is_required_for_the_bound` |
| O_INVIS | drop `strip_invis` from the oracle's ops | 33 | 27 | `test_oracle_known_vectors` 27/33 |
| O5_LOWER | drop `str.lower` from the oracle | 33 | 1 | `[uppercased]` |
| O3_UQP | drop `unquote_plus_drop` from the oracle | 33 | 2 | `[plus_split]`, `[pct2b_split]` |
| O-UQ-REPLACE | both oracle decoders → default errors | 33 | 1 | `[pct_lone_continuation_split]` |
| O_UTF8_LENIENT | drop the lenient op from the oracle | 33 | 2 | `[raw_utf8_mojibake]`, `[raw_utf8_mojibake_junk]` |
| **MARKER-GUARD-BREAK** *(mine)* | re-introduce `red:1104` `!= MARKER` | 5 | 1 | `test_no_not_equal_marker_assertions` — the guard has teeth for the exact form |

### Survivors — every one classed

| mutant | scope run | verdict | evidence |
|---|---|---|---|
| **IMPL-EXTRA-DRIFT** *(mine)* | **full 537** | **SURVIVES — `537 passed in 174.02s`** (load 3.10→2.18) | delete the ten reserved entries from the impl's `_INVISIBLE_EXTRA` (`backend:146-148`), ranges intact → nothing notices. **F6** |
| **RECORD-HDRVAL-BLANKED** *(mine)* | **full 537** | **SURVIVES — `537 passed in 174.82s`** (load 2.18→7.75) | record every `x-trace` header **value** as `""` (record kept, 200 served) → nothing notices. **F5** |
| **MARKER-GUARD-EVADE + BODYSTR-RECORD-BLANKED** *(mine)* | targeted 5 | **SURVIVES — `5 passed`** | `_b = json.loads(...)["body"]` then `assert _b != MARKER` evades the guard's regex and restores the exact D5j-F1 hollow green. **F4** |
| **MARKER-GUARD-BREAK under a `grep` without `-P`** *(mine)* | targeted 1 | **SURVIVES — `1 passed`** | a real `!= MARKER` violation present, guard green, because the guard never checks grep's exit code. **F3** |
| **ORACLE-EXTRA-DRIFT** *(mine)* | 34 oracle tests | **EQUIVALENT, qualified — `34 passed`** | removing the ten from the oracle's `_INVISIBLE_EXTRA` (`red:97-102`) changes nothing **while the oracle's pinned table is intact**; the extras are a second, table-independent path for exactly those 10 (this is why they still die under O-TABLE-DROP). The lane's SELF-ATTACK §1 reasoning is **correct**. |
| **CTL_PARTIAL_noC1 (predicate form)** | **full 537** | **EQUIVALENT — `537 passed in 173.85s`** | reproduces the report's DONE-row-9 number; the D5i depth-2 mechanism still holds |

---

## PROBE tables — every number below is my own run

### Generator, extracted verbatim from the docstring and executed

| interpreter | UCD | tokens | members | byte-identical to the committed `_INVIS_RANGES` |
|---|---|---|---|---|
| `/usr/bin/python3.13` | 15.1.0 | **365** | **4315** | **YES** |
| `/usr/bin/python3.12` | 15.0.0 | 365 | 4315 | YES |
| `python3` (3.11) | 14.0.0 | 356 | 4273 | no — differs by exactly the 42, as designed |

### Self-test expectations, standalone on three interpreters (pytest exists only on 3.11)

```
py3.11 UCD 14.0.0: len(pinned)=4315 True | live-pinned=0 | pinned-live=42 == the _UCD_15_ADDITIONS literal | PASSES
py3.12 UCD 15.0.0: len(pinned)=4315 True | live-pinned=0 | pinned-live=0  | PASSES
py3.13 UCD 15.1.0: len(pinned)=4315 True | live-pinned=0 | pinned-live=0  | PASSES
  the 10 reserved slots are in `pinned` AND in the test's `live` on all three
```
DISCREPANCY §2 of the report ("no change in the self-test expectations") is **correct**.

### Impl-vs-oracle strip domain (no pytest needed)

| interpreter | impl | oracle pinned | oracle effective (pinned ∪ live ∪ extras) | `impl − oracle` | `oracle_pinned == impl` |
|---|---|---|---|---|---|
| 3.11 / 14.0.0 | 4315 | 4315 | 4315 | **0** | **True** |
| 3.12 / 15.0.0 | 4315 | 4315 | 4315 | 0 | True |
| 3.13 / 15.1.0 | 4315 | 4315 | 4315 | 0 | True |

### Three-interpreter server-side sweep — 72 code points × 2 sinks × 3 interpreters = 432 cells

Union of the 20 D5h code points, the 42 UCD-15 additions, the 5 fillers **and the 10 reserved slots**;
header sink (raw UTF-8 wire bytes, `surrogatepass`) and JSON-escape sink (`\uXXXX`, surrogate pairs).
Conforming = `400` + MARKER + `Connection: close` + record delta 1.
```
py311: header-sink+json-escape-sink over 72 code points -> non-conforming cells: 0
py312: header-sink+json-escape-sink over 72 code points -> non-conforming cells: 0
py313: header-sink+json-escape-sink over 72 code points -> non-conforming cells: 0
```

### Class boundary against Default_Ignorable_Code_Point (17 ranges, 4 174 members)

```
UCD 14.0.0 and UCD 15.1.0, identical:
  ASSIGNED members NOT in the pinned table: 0
  UNASSIGNED (Cn) members OUT of class:     3759  {U+E0000-E0FFF: 3759}   <- the documented D5i-F11 ruling
  the 10 reserved BMP slots IN the table:   True (2065 / FFF0 / FFF8 all True)
  the assigned tag characters (E0001, E0020-E007F, E0100-E01EF, all Cf) are IN
```
Live on the **decoded** (JSON-escape) sink:
```
  U+2065  reserved, inside the U+2060-2064 run   HTTP/1.1 400 Bad Request   MARKER=True   <- was 200 on the parent
  U+FFF0 / U+FFF4 / U+FFF8  reserved             HTTP/1.1 400 Bad Request   MARKER=True   <- was 200 on the parent
  U+FFFD REPLACEMENT / U+FFFC OBJECT REPL. (So)  HTTP/1.1 200 OK            MARKER=False  (unchanged, documented)
  U+E0FFF reserved tag-plane (Cn)                HTTP/1.1 200 OK            MARKER=False  (unchanged, the ruling)
  U+2060 WORD JOINER / U+200B ZWSP (controls)    HTTP/1.1 400 Bad Request   MARKER=True
```

### Saturation arm — the census re-run on the PIN (the predecessor's corpus, seed 3)

```
vectors 20000: parent-screened -> PIN-served = 105   PIN-screened -> parent-served (new catches) = 370
  of the 105, the depth-6 oracle FINDS the token while the PIN serves = 0
global hostile sweep, 30000 vectors: oracle-finds-but-impl-serves = 0
```
The committed test's vector — `s0-01-upstream-tok%2B%C0%252520%209\t %C0en-0123456789abcdef` — appears
**verbatim** in the census output, so `red:1200` pins one of the real 105. The docstring's
"105 of 20 000 … the depth-6 oracle confirms the token absent in all of them" is **true on the PIN**.

### False-positive direction (26 legitimate values, PIN vs parent)

```
legitimate values screened by PIN: 1 / 26  ['%25 %2520 %252520 100%25 50%']    <- the documented D5d-F12 accepted risk
divergences PIN vs parent: none printed  -> adding the ten reserved slots introduced NO new false positive
```
Live legitimate-traffic table: **10/10 served 200 and recorded verbatim** (CJK · accented · emoji ZWJ
family · Devanagari matras · Arabic harakat · Hebrew niqqud · Thai · `a+b=c` · `100% of 50%` · base64 JWT).

### Cost — the committed harness, re-run by me (load 0.55 → 0.77)

```
    KB |   ordinary | inv-utf8-hdr |  bound-hdr | bound-body
     1 |    0.001 200 |    0.001  400 |    0.001 400 |    0.002 400
    10 |    0.005 200 |    0.004  400 |    0.004 400 |    0.011 400
   100 |    0.038 200 |    0.031  400 |    0.032 400 |    0.098 400
  1000 |    0.391 200 |    0.313  400 |    0.316 400 |    1.022 400
```
Reproduces the report (0.383 / 0.309 / 0.320 / 1.031 at load 1.58→1.73) within ~2 %.
The pad is inside a JSON string value — read at `cost_probe.py:100-101`, and confirmed by the
side-by-side below. `--slow-delay 0.05` affects only the `s0-01-slow` model (`backend:727`), so it
does not distort these columns. Docstring cost sentence (`backend:77-80`): "~2 s on a quiet 4-core
box … bounded by handler timeout (30 s) and `ThreadingHTTPServer`" — **conservative and true**:
measured 1.02 s; `timeout = 30` at `:545`, `ThreadingHTTPServer` at `:794`,
`MAX_CONTENT_LENGTH = 1_048_576` at `:119`.

### The two harness styles, identical vector, ONE window, ONE backend (item 5's explicit ask)

```
load before 0.39 / after 0.52 ; backend pid 16943 (started and terminated by me)
  ordinary-1000KB (committed vector, pad in a JSON string)  http.client=0.378s (200)  raw-socket=0.378s (200)  raw/http = 1.00x
  old space-padded vector (the D5j-F5 defect)               http.client=0.113s (200)  raw-socket=0.113s (200)  raw/http = 1.00x
```
**The harness style explains none of the gap** (see **F7**). It does confirm the vector fix: the old
"ordinary" column measured a string that `strip_invis` collapses — 0.113 s vs 0.378 s, **3.3×**.

### Live controls (re-run in full)

```
REDACTIONS: 60/60 requests -> 400 ; records 60 ; MARKER records on disk: 60
GET  /v1/models           -> HTTP/1.1 200 OK  ; record path=/v1/models ; auth_fp set: True
POST /v1/chat/completions -> HTTP/1.1 200 OK  ; reply='pong' ; record verbatim: True
STREAM s0-01-slow         -> HTTP/1.1 200 OK  ; 6 'data: ' frames ; [DONE] present: True
MARKER records after the controls: 60  (none overwritten)
Connection: close on every 4xx -- 12 classes, raw socket, 12/12 True
header-ignoring pipelining on the stream leg: responses seen 1 | data lines 6 | second response: False
Top-level JSON string bodies, 400 with the record VERBATIM:
  hello 'hello' | café 'café' | CJK '北京市海淀区' | Müller 'Müller' | £100 '£100'   (5/5, delta 1, close=True)
```

### `--slow-delay` guard (verbatim) and the round-12 hostile battery

```
nan     rc=2  scripted_backend: --slow-delay nan must be a finite number >= 0
inf     rc=2  scripted_backend: --slow-delay inf must be a finite number >= 0
-1      rc=2  scripted_backend: --slow-delay -1.0 must be a finite number >= 0
1e400   rc=2  scripted_backend: --slow-delay inf must be a finite number >= 0
-nan    rc=2  scripted_backend.py: error: argument --slow-delay: expected one argument
abc     rc=2  scripted_backend.py: error: argument --slow-delay: invalid float: 'abc'
=-inf   rc=2  scripted_backend: --slow-delay -inf must be a finite number >= 0
```
15-case hostile battery: **no crash, no hang, every record valid JSON**, `GET /healthz` after the
battery `200 OK`. Depth 32 → 200; depth 33 → 400 + close + **zero** records; top-level `null` /
empty body → 400; `NaN` / `-Infinity` / `1e400` → 200 with a valid record; `%80`×2000 header → 200.

### Process census (precise, argv-matched)

```
mid-grade, argv-matched:  2 backend processes, NEITHER mine --
  29094  .../scratchpad/arch/proofs/S0-01/tools/scripted_backend.py     (another verifier's tree)
  29156  .../scratchpad/mut/w1/proofs/S0-01/tools/scripted_backend.py   (another verifier's tree)
  processes under vd14/ or /tmp/vd14_*: none
final, read from /proc/<pid>/cmdline for every live python process:
  scripted_backend.py processes on the box: 0
  (the two python3 pids alive, 659 and 7051, are another lane's pytest runs on
   test_s0_01_check_acp_conformance.py / audit_cp5_controls.py / pc_post_scan.py)
```
Every backend I started was stopped PID-targeted. I did not touch the two foreign ones; they exited
on their own. Caution recorded for the next verifier: a `ps | grep scripted_backend` census
self-matches its own command line, and a `grep -o … | head -1` idiom returns rc 0 with no output —
read `/proc/<pid>/cmdline` per python process instead.

---

## Findings — all of them, no severity filtering

### F1 — BLOCKING — SOLID — the `file:line` discipline fails the brief's own three-strikes gate (fourth round of D5i-F8 / D5j-F3)

- **file:line** `D5k-report.md` DONE rows 2, 3, 4, 5, 6, 8, 9 and the MUTANT table row 5; row 8 asserts
  *"Every `file:line` in this table derived by `grep -n` on the FINAL bytes after the last edit."*
- **expected** brief item 8: *"every `file:line` by `grep -n` on the committed FINAL bytes … the
  verifier greps ten; **three wrong = discipline failed**."*
- **observed** — `report_lint.py` at the PIN: **OK 23, NEAR 5, MISS 6, UNCHECKABLE 1** (identical to the
  coordinator's run). I then re-derived every flagged ref by hand and cleared the tool's heuristic:

  | report ref | claim | what is actually at the cited line | verdict |
  |---|---|---|---|
  | `red:530` | the `ucd15_addition_split` vector | `# D5k item 3: permanently-reserved BMP slots` — the vector is at **529** | **WRONG (−1)** |
  | `red:532-533` | `reserved_2065_split` **and** `reserved_fff0_split` | 532 = the `0xFFF0` vector, 533 = `# Known-good:` — the pair is at **531-532** | **WRONG (−1)**, and the span holds only one of the two |
  | `red:1155` | `test_credential_reserved_bmp_separator_in_json_body_returns_400` | **blank line**; the section comment is 1156, the decorator 1158, the `def` **1161** | **WRONG (−6)** |
  | `main:2003` | `test_saturating_junk_is_served`'s vector is `%252B` | `).encode()` — `X-Trace: %252B` is at **2001** | **WRONG (−2)** |
  | `backend:76-79` | the module docstring's cost sentence | 76 = "bound-exceeded path and blanks the record" — the sentence is **77-80** | **WRONG (−1)** |
  | `backend:203-222` | "the generator … is **COMPLETE** and runnable" | 203 is the docstring's first line and **222 cuts the generator mid-loop** (`start = end = cp`); the generator is **206-227** | **WRONG** — the span contradicts the very word "COMPLETE" |
  | `backend:316,320` (MUTANT table, UQ-REPLACE-BOTH) | the two reverted return statements | 316/320 are **docstring lines**; the returns are **317/321** | **WRONG (−1)** |
  | `main:177,205,217,219,222,305,457,473,502` (DONE row 6, labelled "(n0 lines)") | the n0 lines and the `n0+1`/`n0+2` asserts | n0 lines are **177, 206, 217, 304, 457, 472, 501**; the `t_mono_ns` asserts are **220 and 224** | **6 of the 9 numbers WRONG** |

  Two further spans are imprecise rather than wrong: `main:2124-2131` (the docstring ends at **2129**)
  and `backend:150-197` (the literal's last line is **198**, the closing `)` at **199**).
  Cleared as tool heuristic, the lane is right: `backend:293-298`, `backend:530`, `backend:750`,
  `red:103-151`, `cost_probe.py:99-101` (the tool cannot resolve that alias), `backend:141-149`,
  `backend:50-56`, `main:2063`, `main:2123`, `red:1104`, `red:1116`, `red:1180`, `red:1200`,
  `backend:496/500/518`.
- **7 distinct wrong refs and 13 wrong line numbers** against a stated threshold of three.
- **minimal fix** run `scripts/report_lint.py` (it now exists, at `b6fed16`) before submitting, fix
  every MISS/NEAR by `grep -n` on the committed blob, and re-state row 8 only if it is then true.
  The tool's `--map` needs a `cost_probe=tasks/briefs/s0-01-d5j-support/cost_probe.py` entry to stop
  the two UNRESOLVED lines.

### F2 — BLOCKING — SOLID — two `failed` cells in the mutant table under-report the kill; four killers go unnamed

- **file:line** `D5k-report.md` MUTANT table rows `UQ-REPLACE-BOTH` (ran 200 / failed **1**) and
  `RECORDLESS_400_APIKEY` (ran 337 / failed **1**).
- **expected** brief item 8 closed D5j-F17 by making the columns honest; a `failed` column that omits
  failures defeats the same purpose the `ran` column serves.
- **observed / reproduced**
  - `UQ-REPLACE-BOTH` over the whole red file (the only natural 200-test selection):
    **`5 failed, 195 passed in 91.03s`** — `test_pct_dense_junk_that_now_saturates_is_served`
    **plus** `test_credential_pct_encoded_invalid_utf8_separator_returns_400[lone_cont/overlong_lead/ff/surrogate]`.
  - `RECORDLESS_400_APIKEY` over the whole main file: **`2 failed, 335 passed in 98.50s`** —
    `test_credential_headers_dropped_from_records` **plus** `test_credential_in_credential_header_returns_400[api-key]`.
  - `ran` is right in all six rows (I measured 4 / 33 / 4 / 337 / 200 / 1) — this is a `failed`-column defect only.
- **minimal fix** put the true failure count in the cell and name every killer, or add "(new killer;
  N other pre-existing failures)".

### F3 — BLOCKING — SOLID — the new `!= MARKER` ban is fail-open: it never checks grep's exit code

- **file:line** `tests/red/test_s0_01_backend_credential_screen.py:1189-1195` —
  `r = subprocess.run(["grep","-cP", …], capture_output=True, text=True)` then
  `count = int(r.stdout.strip()) if r.stdout.strip() else 0`. **`r.returncode` is never inspected.**
- **mechanism** any grep failure yields rc 2 with empty stdout → `count = 0` → the assertion passes.
- **reproduced, two ways**
  - a renamed/missing file: `grep rc=2 stdout='' -> count=0 -> guard passes: True`;
  - a `grep` without PCRE (BSD/busybox venue, simulated with a PATH shim that prints
    `grep: invalid option -- P` and exits 2), **with a real violation present** (mutant
    MARKER-GUARD-BREAK re-introducing `assert …["body"] != MARKER` at `red:1104`):
    `1 passed, 199 deselected in 0.14s` — **the guard is green over the very defect it exists to catch.**
- **anti-hollow-green tactic 1** (assert the exact exit code) is directly on point; this guard was
  added *this round* and was never negatively controlled against its own tooling failing.
- **minimal fix / exact red test** drop the subprocess and walk the AST — de-vacuoused by me:
  ```python
  import ast
  for p in (red_file, main_file):
      for n in ast.walk(ast.parse(p.read_text())):
          if isinstance(n, ast.Assert):
              for c in ast.walk(n.test):
                  if isinstance(c, ast.Compare) and any(isinstance(o, ast.NotEq) for o in c.ops) \
                     and "MARKER" in [x.id for x in ast.walk(c) if isinstance(x, ast.Name)]:
                      raise AssertionError(f"{p.name}:{n.lineno} asserts != MARKER")
  ```
  Measured: **0 hits on the PIN**, **1 on MARKER-GUARD-BREAK** (line 1104), **2 on MARKER-GUARD-EVADE**
  (lines 1105, 1118). If the subprocess is kept, `assert r.returncode in (0, 1), r.stderr` is the
  one-line floor.

### F4 — BLOCKING — SOLID — the guard bans one syntactic form, not the class; a two-line edit restores the exact D5j-F1 hollow green

- **file:line** `red:1191`, the pattern `r'^\s*assert\s.*\["body"\]\s*!=\s*MARKER'` (the guard is `red:1180-1195`).
- **expected** brief item 1: *"then the CLASS: `grep -n "!= MARKER"` over both test files → zero hits
  (every 'served' test asserts the recorded value); pin it with a text assertion in the red file."*
- **observed** the pattern requires the literal `["body"]` on the same line as the `assert`.
  Mutant **MARKER-GUARD-EVADE** — `_b = json.loads(recs[-1].read_text())["body"]` then
  `assert _b != MARKER`, applied to both tests, **together with BODYSTR-RECORD-BLANKED** —
  gives **`5 passed, 532 deselected`**: the record-blanking mutant is invisible again.
  The lane disclosed the limitation honestly (SELF-ATTACK §3) but shipped it; the brief asked for the class.
  (Note also that `grep -n "!= MARKER"` over the two files returns **4 hits today** — all inside the
  guard itself — so the brief's literal "zero hits" formulation is not met either, harmlessly.)
- **minimal fix** the AST check in **F3** — it catches `_b != MARKER` with any left-hand expression,
  and it is 0-hit on the PIN so it is not vacuous.

### F5 — BLOCKING — SOLID — the newest test repeats the D5j-F1 class: it does not pin the record's content, and a header-value-blanking mutant passes all 537

- **file:line** `tests/red/test_s0_01_backend_credential_screen.py:1200-1212`
  (`test_pct_dense_junk_that_now_saturates_is_served`, the oracle assert at `:1212`): it asserts `200 OK`, `len(recs) == n0 + 1`, and
  `_absent_under_all_normalizations(recs[-1].read_text())` — **never that the vector was recorded**.
- **observed / reproduced** mutant **RECORD-HDRVAL-BLANKED** (`backend:528`,
  `clean = {k.lower(): ("" if k.lower()=="x-trace" else v) …}` — record kept, path kept, 200 served):
  **`537 passed in 174.82s`**, zero failures. Nothing in the tree pins a recorded header value for this
  class, so the record could silently stop carrying what the client sent while every gate stays green.
  This is a fidelity defect in a fixture whose entire purpose is a faithful record — not a leak.
- **minimal fix / exact red test** one line in that test, de-vacuoused live by me
  (`recorded x-trace == the wire vector: True` on the PIN, False under the mutant):
  ```python
  assert json.loads(recs[-1].read_text())["headers"]["x-trace"] == vec
  ```

### F6 — SOLID — the extras literal exists in three unlinked copies; deleting the ten reserved entries from the impl's copy passes all 537

- **file:line** impl `proofs/S0-01/tools/scripted_backend.py:141-149`; self-test's own copy
  `tests/test_s0_01_scripted_backend.py:2066-2068`; oracle's copy
  `tests/red/test_s0_01_backend_credential_screen.py:94-103`.
- **mechanism** the impl's `_INVISIBLE_EXTRA` is **never read at runtime** — the only runtime use of the
  class is `_INVIS_PINNED` at `backend:305` (grep over the file: `_INVISIBLE_EXTRA` appears at :50, :133,
  :139, :141 only — docstring, comments, definition). Nothing compares the three copies.
- **observed / reproduced** mutant **IMPL-EXTRA-DRIFT** (delete `0x2065` and `0xFFF0-0xFFF8` from
  `backend:146-148`, ranges untouched): **`537 passed in 174.02s`**.
- **why it matters** the report presents item 3's mechanism as *"U+2065 and U+FFF0-FFF8 added to
  `_INVISIBLE_EXTRA` at `backend:141-149`"*. The load-bearing change is actually the two merged range
  tokens (`205F-206F`, `FFF0-FFFB`). The D5j-F2 fix (two copies + an equality test) was applied to the
  4 KB range string and **not** to the extras that generate it — the same drift surface, one level up.
  Worst case is a confusing gate failure after a regeneration, not a leak.
- **minimal fix** one line in `test_invisible_table_is_the_ucd_15_1_class`, next to the existing local
  literal: `assert sb._INVISIBLE_EXTRA == extra` (and, if you want the third copy covered, extend
  `test_oracle_table_equals_the_impl_table` with `{ord(c) for c in red._INVISIBLE_EXTRA} == sb._INVISIBLE_EXTRA`).

### F7 — BLOCKING — SOLID — the cost section's stated mechanism for the residual divergence is falsified by measurement

- **file:line** `D5k-report.md` DONE row 4 and PROBE §"Cost probe": *"0.383/0.63 = 0.61x (lower, same
  box, different harness — **the raw-socket probe skips http.client overhead**)"*.
- **observed** the claim is self-contradictory as written (skipping overhead would make the raw-socket
  number *lower*, not higher), and it is false on measurement. Item 5's explicit ask, executed: same
  1000 KB vector, one window, one backend, load 0.39→0.52 —
  **`http.client = 0.378 s`, `raw socket = 0.378 s`, ratio 1.00×**.
- **what the gap actually is** the harness style contributes **nothing**. The 0.63 s figure came from
  D5i at an unstated load; on a quiet box the honest vector costs **0.378-0.391 s** by either harness.
  The residual is venue/contention, not instrumentation.
- **minimal fix** replace the sentence with: *"the D5i figure was taken at an unstated load; measured
  head-to-head in one window the two harness styles are identical to 3 decimal places (0.378 s each),
  so the residual is load, not harness."*

### F8 — SOLID (informational) — `_last_record_text` is dead code

- **file:line** `red:80-81` `def _last_record_text(backend): return _records(backend)[-1].read_text()`.
- **observed** zero callers in either test file. It is also the single `[-1]` record read with no delta
  — i.e. the "or is the helper" carve-out DONE row 6 leans on covers a function nothing calls.
- **pre-existing**, not introduced by this lane; per the repo's surgical-changes rule I mention rather
  than ask for deletion. If it is deleted, DONE row 6's carve-out becomes unconditional.

### F9 — SOLID (informational) — the report's DISCREPANCY §3 ruling is CORRECT; the brief's list carried one non-record location

- **ruling** the brief's eight locations (`main:144, 175, 202, 212, 296, 446, 459, 487`) are **def lines**
  on the 8u bytes. I mapped them: `144` is `test_stream_completion_frames_are_deterministic`, whose
  `[-1]` reads are `frames[-1]` / `payloads[-1]` — **stream frame lists, not records**. The real set is
  **7 tests / 8 record reads** (parent lines 181, 207, 216, 219, 300, 452, 464, 491), exactly as the lane
  reports. All 7 carry deltas on the PIN, and my audit of every `[-1]` in both files finds **zero**
  record reads without one.

### F10 — SOLID (informational) — the AP screen's six hits are all classifiable as safe; see the Item-0 table above. No defect.

### F11 — SOLID (minor) — `--record-dir` as a dangling symlink escapes both startup guards

- **file:line** `backend:784` and `:788`.
- **observed** a dangling symlink satisfies neither `exists()` nor `is_dir()`, so neither refusal fires;
  `record_dir.mkdir(parents=True, exist_ok=True)` then raises `FileExistsError` at the first record.
  Fail-loud, not fail-open, and pre-existing (untouched by this lane) — reported for completeness only.

### F12 — BLOCKING — SOLID — the mutant table under-delivers the brief, and DONE row 9 states something the table does not contain

- **file:line** `D5k-report.md` MUTANT table (six rows) and DONE row 9.
- **expected** brief §Mutants names eleven mutants — BODYSTR-RECORD-BLANKED, O-TABLE-DROP,
  TABLE-DROP-RESERVED, RECORDLESS_400_APIKEY, UQ-REPLACE-BOTH, **TABLE-DROP-42 / FILLERS / CS / ME /
  ZLZP ("unchanged killers, **re-measured with executed counts**")**, ORACLE-DRIFT — *"plus ten of the
  verifier's reproduced rows"*.
- **observed** the table has **six** rows. The five re-measured TABLE-DROP-* rows are absent; the ten
  reproduced rows are absent. DONE row 9 asserts *"Mutant table carries both single-decoder reverts as
  qualified equivalents"* — **the table contains neither**.
- **substance is fine**: I re-measured all five TABLE-DROP-* rows (29 executed each; 1/5/1/2/2 failures
  with the named killers) and 30 further mutants; every brief-named mutant dies.
- **minimal fix** paste the rows, or move the prose claims out of DONE row 9.

### F13 — BLOCKING — SOLID — "NOT_DONE: None. All 9 brief items delivered" is false

- **file:line** `D5k-report.md` §NOT_DONE.
- **observed** four gates the brief lists by name are not in the report: the **7 sinks × {6 + 8 + 5 + 2}
  matrix**; the **three-interpreter sweep over the 62 + 10 code points on both sinks** (the report
  pastes a 12-cell reserved-only table instead); the **impl-vs-oracle differential**; the
  **parent-vs-child detection differential**. Add F12's missing mutant rows and F1's ref failures and
  the completeness claim cannot stand. This is the D5j-F4 class (asserting a closure the artifact does
  not contain) in a smaller form.
- **I ran the two that were cheapest to settle**: the 72-code-point × 2-sink × 3-interpreter sweep
  (**432/432 conforming**) and the impl-vs-oracle domain differential (**0 on all three interpreters**),
  plus a 30 000-vector oracle-vs-impl leak sweep (**0**). The tree passes them; the report does not say so.
- **minimal fix** paste them, or list them under NOT_DONE with a reason.

### F14 — SOLID (informational, design, item 12) — where I would still change the design

1. **Pinned-only impl vs `pinned ∪ live` (ruling 1).** I now agree with the coordinator's ruling and
   record why: the union's cost is a **venue-dependent serve-time predicate**, which is exactly D5i-F3,
   and today the two sets are provably equal on all three interpreters (`impl − oracle_effective = 0`,
   measured). The self-test plus the new cross-check make a newer UCD loud at gate time in **two**
   places. The residual risk — a UCD > 15.1 on the PC making the impl narrower than the runtime — is
   real but is a *gate* failure the moment the suite runs there, and this suite is a gate on the PC leg.
   **Keep the ruling.** One cheap hardening: the self-test's `else:` branch already fails loudly on an
   unknown UCD; make sure the PC leg actually runs `test_invisible_table_is_the_ucd_15_1_class` (it does
   — it is in the 537).
2. **The ten reserved slots (ruling 2).** Correct and now verified from both directions: every assigned
   Default_Ignorable member was already in the table, the ten reserved BMP slots are the only BMP Cn
   members of that list, and adding them cost **no** new false positive on 26 legitimate values or on
   the 10 live legitimate traffic shapes. The plane-14 run stays out, documented at `backend:50-56`.
   **No change.**
3. **Two copies + an equality test (ruling 3).** Right call — ORACLE-DRIFT dies, and O-TABLE-DROP still
   dies on 3.11, so the oracle's data stays independent while drift is loud. **But apply the same rule
   one level up**: the *extras* that generate both literals are three unlinked copies (**F6**). One
   assertion closes it.
4. **The saturation-flip test should assert the record, not only the oracle** (**F5**) — the D5j-F1
   lesson applies to the test written to close D5j-F6.
5. **A guard implemented as a subprocess grep is a guard that can fail open** (**F3**/**F4**). In this
   repo's own terms: every gate needs a negative control *including one on its own tooling*.

---

## What I reproduced vs reviewed statically vs deliberately skipped

**Reproduced first-hand (executed or live):** both gate runs and the red standalone · pyflakes on all
four scope files · `lint_delta --base 3167608` · `report_lint.py` (identical counts to the
coordinator's) · `ap_screen.py` on the backend and on both test files, every hit classified by reading
the site · the red-before state on the parent implementation (4 named failures) · the parent/child
collect counts (529 → 537) and the exact per-test delta · **41 mutants** (35 killed with named killers,
6 survivors classed), each on a scratchpad copy with the shared tree asserted clean after every one ·
the docstring generator extracted verbatim and executed on 3.13/3.12/3.11 (byte-identical, 365 tokens,
4315 members) · the self-test's expectations standalone on all three interpreters · the impl-vs-oracle
strip-domain differential on all three · the 72-code-point × 2-sink × 3-interpreter live sweep
(432 cells) · the Default_Ignorable boundary enumeration on UCD 14.0.0 and 15.1.0 · the live class
boundary on the decoded sink · the 20 000-vector saturation-flip census (105 / 370) and the oracle
check on all 105 (0) · the 30 000-vector oracle-finds/impl-serves sweep (0) · the 26-value
false-positive census · the committed cost probe · a **dual-harness** cost measurement on the identical
vector in one window · the full live-control section (60 redactions, normal + streaming, 12-class
`Connection: close`, 10/10 legitimate, 5/5 top-level JSON strings) · the pipelining differential · the
`--slow-delay` guard · the 15-case hostile battery · the `[-1]` audit over both files and over the
parent · every `file:line` in the tables above · the process census.

**Reviewed statically (read, not executed):** the **PC gate line** `537 passed in 51.34s` (run
`20260907T212749Z-934dec1`) · `cost_probe.py`'s pad construction (read at `:100-101`; corroborated by
measurement) · the report's prose about D5h/D5i-era findings that predate this lane · lane A5j's
uncommitted edits in the shared tree (confirmed disjoint from my scope by `git diff`, not opened).

**Deliberately skipped, with the reason:** the **PC leg** — no bridge in this lane, the brief assigns it
to the coordinator, and nothing in my verdict rests on it · the **28 096-vector parent-vs-child
detection differential** — D5j re-ran it at that size on the same corpus, this diff does not touch the
decoder set or the depth, and my 20 000-vector census plus the 30 000-vector oracle sweep cover the same
two directions more aggressively · the **7 sinks × 21 separators matrix** — D5j ran 56 of those cells at
the previous checkpoint and this diff changes only the class membership of 10 code points, which I
covered instead with 432 live cells across three interpreters · **re-running D5h-era mutants** neither
the brief nor this diff touches · **`CTL_PARTIAL_noC1` in its table-subtraction form** — D5j proved it
dies by the self-test; I ran the predicate form at full scope instead, which is the one the report
quotes a number for.

---

## VERDICT — **NOT-READY**

**The code is right, and I could not break it.** The record is pinned to the character (a one-character
mutation dies), the oracle's table now carries weight (O-TABLE-DROP dies on 3.11, ORACLE-DRIFT dies), the
ten reserved slots are closed on both sinks on all three interpreters (432/432) and pinned three ways,
the generator is runnable verbatim and byte-identical, the cost vector is honest, the saturation-arm
docstring is true (105/20 000 with 0 oracle finds), the main file's stale-`[-1]` class is closed, and
across 30 000 hostile vectors, 432 live cells, 26 legitimate values and 41 mutants **there is no
credential leak and no new false positive**. Every blocking item below is a report defect or a
test-strength defect, each with a one- or two-line fix.

**Blocking set**

| # | why it blocks |
|---|---|
| **F1** | the brief's own rule — "three wrong = discipline failed". 7 distinct wrong refs / 13 wrong line numbers, while row 8 asserts they were all re-derived by `grep -n` on the final bytes. Fourth consecutive round, and the mechanical checker that would have caught it now exists. |
| **F2** | two `failed` cells under-report the kill (1 vs 5, 1 vs 2) and four killers go unnamed — the D5j-F17 column-honesty item the brief told this lane to close. |
| **F3** | the guard added this round passes with a real `!= MARKER` violation present whenever grep fails (missing file, or a grep without `-P`) — a gate with no negative control on its own tooling. |
| **F4** | the same guard bans a syntactic form, not the class: a two-line edit restores the exact D5j-F1 hollow green (measured, `5 passed`). |
| **F5** | the test written to close D5j-F6 repeats the D5j-F1 class — a mutant that blanks the recorded header value passes all 537. |
| **F7** | the cost section replaces D5j-F5's wrong number with a wrong explanation: measured head-to-head the two harness styles are identical (1.00×), so the stated mechanism is false. |
| **F12** | the mutant table delivers 6 of the 21 rows the brief names, and DONE row 9 claims two rows the table does not contain. |
| **F13** | "NOT_DONE: None. All 9 brief items delivered" is false — four brief-named gates are absent from the report (I ran two of them; they pass). |

**Non-blocking, real:** F6 (three unlinked copies of the extras literal; IMPL-EXTRA-DRIFT survives the
full 537), F8 (dead `_last_record_text`), F9 (the lane's 8-vs-7 ruling is correct), F10 (AP screen: no
defect), F11 (dangling-symlink `--record-dir`). **Design (item 12):** F14 — I would keep all three
rulings and add one assertion (F6) plus one assertion (F5).

**This verdict does not depend on anything I did not reproduce**, with one stated exception: the PC gate
line is reviewed, not reproduced, and no finding rests on it.
