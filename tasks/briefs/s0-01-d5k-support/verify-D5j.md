# VERIFY-D5j — round-13 adversarial grade of lane D5j (S0-01 scripted backend credential screen)

**PIN graded:** `77546be2a05208b2d9b03aeeae7cec6c3a3448b8` (checkpoint 8u), branch
`claude/soundbox-kit-migration-iz1jwf`. Every byte graded from a
`git archive 77546be | tar -x` copy under the session scratchpad (`scratchpad/pin`), never from the
shared working tree.

**Shared-tree discipline:** read-only git only (`git cat-file -e`, `git log`, `git show`,
`git ls-tree`, `git diff`, `git status --porcelain`). No stash / checkout / restore / reset / add /
commit / push. Every mutant ran on a scratchpad copy (`scratchpad/vd13/base` → `vd13/work`, 404 KB,
re-copied per mutant). `git status --porcelain` on the shared tree asserted after each batch: clean
on the three scope files throughout. Backends: only ones I started, stopped PID-targeted via
`Popen.terminate()`; never `pkill -f`.

**Tree moved under me mid-grade** (the coordinator landed `73efb9f` checkpoint 8t and `24e0961`
transcripts). `git diff --stat 77546be HEAD -- <the three scope files> <the D5j support dir>` is
**empty** — the graded bytes are still HEAD's bytes, so this verdict describes the current tree.

**PC leg: NOT run by me** — no bridge in this lane, and the brief assigns it to the coordinator.

---

## Premise table (verified first-hand, nothing assumed)

| premise | how checked | result |
|---|---|---|
| PIN exists and is checkpoint 8u | `git cat-file -e 77546be` + `git log -1` | yes — "S0-01 WIP checkpoint 8u … (lane D5j) — REVIEW-PENDING, nothing minted" |
| PIN parent | `git rev-parse 77546be^` | `9da1041` ("anti-hollow-green tactic 10 …") |
| files the PIN touched | `git diff --stat 9da1041 77546be` | 7 files, +667/−58; the 3 scope files + report + cost_probe + ledger + wiki |
| `scripted_backend.py` sha256 / lines | `sha256sum`, `wc -l` on the archive | `be88e7e5…dfa3` / 781 — **matches the report's FILE IDENTITY table** |
| `tests/test_s0_01_scripted_backend.py` | same | `26dd4df8…428d1` / 2102 — **matches** |
| `tests/red/…credential_screen.py` | same | `1049d27b…12299` / 1143 — **matches** |
| `cost_probe.py` | `sha256sum` | `9f0fc936…3bb39` / 126 lines (not in the report's table; committed as the brief required) |
| PIN wording (D5i-F12) | `git log -1 af154ab`, `git log af154ab..77546be` | report says "PIN: `af154ab` (HEAD at dispatch); landing = the coordinator's checkpoint". `af154ab` **is** the commit that added this brief + `verify-D5i.md`. **Correct this round.** |
| interpreters | `python3 -c "…"` | 3.11.15/UCD 14.0.0 (pytest 9.1.1) · /usr/bin/python3.12 3.12.3/UCD 15.0.0 · /usr/bin/python3.13 3.13.12/UCD 15.1.0. `import pytest` fails on 3.12 and 3.13 — confirmed, so no pytest leg there |
| collect-only parent vs child | pytest `--collect-only` on a parent-file tree and on the PIN | parent **500**, PIN **529** (+29) |

---

## Gate runs — reproduced first-hand, pasted verbatim (scratchpad copy of the PIN)

```
load-before: 1.53 1.91 1.65 2/157 6104
529 passed in 168.71s (0:02:48)
pytest-exit: 0
pytest-summary: 529 passed in 168.71s (0:02:48)
load-after: 1.61 1.73 1.63 2/156 6879
```
```
load-before: 0.53 0.83 1.48 1/146 20258
529 passed in 168.34s (0:02:48)
pytest-exit: 0
pytest-summary: 529 passed in 168.34s (0:02:48)
load-after: 0.06 0.50 1.24 1/147 21051
```
```
red standalone:  193 passed in 70.77s (0:01:10)     rc 0
pyflakes (the three scope files):                   rc 0
```
Gates of record (sandbox `529 passed in 168.62s`, lane `168.72s` / `168.53s`) reproduce within
0.4 s. PC run `20260907T192543Z-9da1041` (`529 passed in 51.30s`, Python 3.13, `-n 8`) is
**reviewed, not reproduced** — no bridge in this lane.

Three further clean full-scope runs came out of the mutant campaign on behaviourally-identical
trees: `529 passed in 168.52s`, `168.52s`, `168.58s`, `168.72s`. The suite is stable.

---

## D5i-F1…F16 closure table (one row each; every red-before reproduced myself)

Red-before method: PIN tests + the **parent's** `scripted_backend.py` (`git show 9da1041:…`) in an
isolated tree. Result of the targeted selection: `9 failed, 15 passed, 505 deselected in 20.55s`.

| D5i finding | closed by | red-before I reproduced | verdict |
|---|---|---|---|
| **F1** byte-view on a top-level JSON string body | `backend:479` `byte_view=False`; `red:1081-1094` | `test_top_level_json_string_body_is_not_a_byte_view[e_acute/u_uml/pound]` **FAIL** on the parent; control `…hello_control` **PASS** before and after | **CLOSED in code** — but the closing test does not pin the record (**D5j-F1**) |
| **F2** percent-decoders replace instead of drop | `unquote_drop` `backend:286-289`, `unquote_plus_drop` `:290-293`, both in `ops` `:294`; oracle `red:195-198` | `test_credential_pct_encoded_invalid_utf8_separator_returns_400[lone_cont/overlong_lead/ff/surrogate]` **FAIL** on the parent | **CLOSED** — 12/12 pct-invalid separators go False→True; caveat **D5j-F6** |
| **F3** invisible class = the runtime's table | `_INVIS_RANGES` `backend:137-186`, `_parse_invis_ranges` `:189-210`, `_INVIS_PINNED` `:213`, lookup `:277` | `test_invisible_class_does_not_depend_on_the_runtime_unicode_table` **FAIL** (`U+10EFD splits the token and is served`) and `test_invisible_table_is_the_ucd_15_1_class` **FAIL** (`no attribute '_INVIS_PINNED'`) on the parent | **CLOSED for the impl**; the **oracle's** copy is still unpinned (**D5j-F2**) |
| **F4** `_INVISIBLE_EXTRA` unpinned | 5 new params in `red:958-970` | n/a (green before — it is a mutation-killer, and the report says so) | **CLOSED** — TABLE-DROP-FILLERS dies on 5 named cases |
| **F5** `Cs` unpinned | `red:1131-1143` lone-surrogate test + oracle vector `lone_surrogate_split` | n/a | **CLOSED** — TABLE-DROP-CS dies on the named test |
| **F16** `Me`, `Zl`+`Zp` unpinned | `red:964-965` params + oracle vectors `line_sep/para_sep/enclosing_circle/cyrillic_enclosing` | n/a | **CLOSED** — TABLE-DROP-ME (2 cases), TABLE-DROP-ZLZP (2 cases) |
| **F6** stale `[-1]` in 8 cases | `n0`/`n0+1` added at `red:710/714`, `727/733`, `749/758`, `865/869` | RECORDLESS_400_XTRACE kills **12 / 12** (I ran the full 4+8 selection: `12 failed, 517 deselected`) | **CLOSED in the red file** (33/33 last-record reads carry a delta). 8 residual cases in the **main** file (**D5j-F7**) |
| **F7** `M_V12_CLOSE` mechanism wrong / dead statements | all three `self.close_connection = True` deleted; comments at `backend:528`, `:724` | n/a | **CLOSED** — `grep -n close_connection` returns only the 2 comments; no socket test added; pipelining differential still closes; 12/12 4xx carry `Connection: close`. Two comments, brief said one (**D5j-F9**) |
| **F8** `file:line` discipline | report row 8 claims every ref re-derived by `grep -n` | — | **NOT CLOSED** — ≥6 of 17 refs wrong (**D5j-F3**) |
| **F9** oracle docstring says "strict utf8_redecode" | oracle docstring rewritten `red:168-183` | `grep -n "strict\|strip_ws\|strip_zwc"` on the red file → **one** hit, `red:939`, a historical mention | **CLOSED** (the report's line ref for it is wrong) |
| **F10** precheck docstring enumerates 4 sinks, there are 5 | `body_str` moved to `byte_view=False`, so there are now genuinely 4 | `grep -n "byte_view=True"` → `468`, `472` (×2), `490` = 4 call sites | **CLOSED** |
| **F11** unassigned (Cn) code points out of class | module docstring `backend:50-52` states the ruling and the reason | live: U+2065 / U+FFF0-F8 / U+E0FFF served on the decoded sink | **CLOSED as documented** (design note **D5j-F15**) |
| **F12** PIN wording | report header | `af154ab` is the dispatch HEAD | **CLOSED** |
| **F13** cost table omits the expensive arm | `cost_probe.py` committed, 4 columns published, "no cell exceeds 1 s" dropped, docstring `backend:74-77` | I re-ran the committed harness: matches within 2 % | **PARTLY CLOSED** — the "ordinary" vector is 1 MB of spaces (**D5j-F5**) |
| **F14** duplicate mutant rows | report merges `M_UTF8_PRECHECK_DEL` = `LENIENT_IN_IMPL` | 10-row table has no duplicate | **CLOSED in form** (no campaign total is published; the brief allowed a 10-row spot-check) |
| **F15** live-control section omits the redaction count | — | `grep -in "redaction\|streaming\|live\|legitimate"` on `D5j-report.md` → **no hit** | **NOT CLOSED — the section is absent entirely**, yet row 7 claims it (**D5j-F4**) |

---

## Mutant table — 41 mutants, all on scratchpad copies, `ran` = tests EXECUTED

`git status --porcelain` on the shared tree's three scope files asserted empty after every batch.

### Killed (35 named killers reproduced; brief asked for ≥ 20)

| mutant | mutation (file:line) | ran | failed | killer that fired |
|---|---|---|---|---|
| BODYSTR-BYTEVIEW-TRUE | `backend:479` → `byte_view=True` | 4 | 3 | `top_level_json_string_body_is_not_a_byte_view[e_acute/u_uml/pound]` (control `hello` passed) |
| **UQ-REPLACE-BOTH (impl)** | `backend:289` + `:293` → default errors | 4 | 4 | `pct_encoded_invalid_utf8_separator_returns_400[lone_cont/overlong_lead/ff/surrogate]` |
| TABLE-EMPTY | `backend:213` → `frozenset()` | 8 | 8 | `invisible_separator_in_header_returns_400` ×8 |
| TABLE-DROP-42 (all 42) | `backend:213` `− {42 cps}` | 1 | 1 | `invisible_class_does_not_depend_on_the_runtime_unicode_table` |
| TABLE-DROP-42 (U+0ECE only) | `backend:213` `− {0x0ECE}` | 1 | 1 | same |
| TABLE-DROP-FILLERS | `− {2800,3164,FFA0,115F,1160}` | 13 | 5 | `invisible_separator_in_json_body_returns_400[BRAILLE_BLANK/HANGUL_FILLER/HALFWIDTH_FILLER/CHOSEONG_FILLER/JUNGSEONG_FILLER]` |
| TABLE-DROP-CS | `− range(D800,E000)` | 2 | 1 | `credential_lone_surrogate_separator_in_json_body_returns_400` |
| TABLE-DROP-ZLZP | `− {2028,2029}` | 13 | 2 | `…json_body…[LINE_SEPARATOR]`, `[PARAGRAPH_SEPARATOR]` |
| TABLE-DROP-ME | `− {20DD,0488}` | 13 | 2 | `…json_body…[ENCLOSING_CIRCLE]`, `[CYRILLIC_ENCLOSING]` |
| LIVE-CATEGORY-RESTORED | `backend:277` → `unicodedata.category` | 24 | 1 | `invisible_class_does_not_depend_on_the_runtime_unicode_table` (**dies on 3.11**; equivalent on ≥ 15.0) |
| RECORDLESS_400_XTRACE | `_framing_gate` rejects any `X-Trace`, no record | 12 | **12** | all four `invalid_utf8_separator_in_header` + `plus_split_with_pct2520` + `raw_utf8_zero_width_in_header` ×6 + `unquote_op_is_required_for_the_bound` |
| M_D4 | `backend:297` `range(5)`→`range(4)` | 2 | 1 | `test_saturating_junk_is_served` |
| M_D6 | `range(5)`→`range(6)` | 2 | 1 | `test_bound_exceeded_blanks_the_record` |
| O-UQ-REPLACE (both oracle decoders) | `red:196` + `:198` | 30 | 1 | `test_oracle_known_vectors[pct_lone_continuation_split]` |
| PRECHECK_ON_LEAVES | `backend:487` → `byte_view=True` | 6 | 6 | `ordinary_latin1_text_in_json_body_is_served` ×6 |
| INVIS_DEL | drop `strip_invis` from `ops` | 8 | 8 | `invisible_separator_in_header_returns_400` ×8 |
| LENIENT_DEL_IMPL | drop `utf8_redecode_lenient` | 3 | 2 | `invalid_utf8_separator_in_json_body[overlong_pair/enquad_plus_junk]` |
| PRECHECK_DEL (= LENIENT_IN_IMPL) | `backend:443` → `if False and …` | 2 | 2 | `invalid_utf8_without_the_token_is_refused_not_repaired`, `precheck_before_closure_on_invalid_utf8` |
| M_SAT_IGNORE | `backend:449` → `return False` | 1 | 1 | `test_bound_exceeded_blanks_the_record` |
| M_SAT_INV | `:449` → `return saturated` | 1 | 1 | `post_content_length_exactly_max_is_accepted` |
| M_SEEN | `:306`/`:308` return `frontier` not `seen` | 1 | 1 | `plus_split_with_pct2520_suffix_returns_400` |
| M_LOWER_DEL | drop `str.lower` | 1 | 1 | `uppercased_token_in_header_returns_400` |
| M_UQP_DEL | drop `unquote_plus_drop` | 15 | 3 | `encoded_whitespace_split_returns_400[header-PLUS/json_body-PLUS/query-PLUS]` |
| M_UQ_DEL | drop `unquote_drop` | 1 | 1 | `unquote_op_is_required_for_the_bound` |
| M_PATH | `backend:468` → `if False and …` | 15 | 5 | `encoded_whitespace_split_returns_400[query-*]` ×5 |
| M_HDRNAME | `:472` drop the name disjunct | 24 | 4 | `depth5_percent_nesting_returns_400[header_name-*]` ×4 |
| M_HDRVAL | `:472` drop the value disjunct | 3 | 3 | `authorization_prefixed_header_name_is_not_exempt` ×3 |
| M_RAWBODY | `:490` → `if False and …` | 1 | 1 | `duplicate_json_key_hiding_token_returns_400` |
| M_JSONSTRINGS | `:485` → `if False:` | 5 | 5 | `whitespace_split_in_valid_json_body_returns_400` ×5 |
| M_DEPTHGATE_OFF | `:627` → `if False:` | 1 | 1 | `json_depth_over_limit_returns_400_no_record` |
| M_JSONSAFE_INPLACE | `:393` → `root = o` | 1 | 1 | `test_json_safe_copy_on_write` |
| O_INVIS | drop `strip_invis` from the oracle ops | 30 | 24 | `test_oracle_known_vectors` 24/30 incl. `[zwnj_split]` |
| O5_LOWER | drop `str.lower` from the oracle | 30 | 1 | `[uppercased]` |
| O3_UQP | drop `unquote_plus_drop` from the oracle | 30 | 2 | `[plus_split]`, `[pct2b_split]` |
| O_UTF8_LENIENT | drop the lenient op from the oracle | 30 | 2 | `[raw_utf8_mojibake]`, `[raw_utf8_mojibake_junk]` |

### Survivors — classed

| mutant | scope run | verdict | evidence |
|---|---|---|---|
| **UQ-REPLACE (impl, `unquote_drop` only)** | **full 529** | **EQUIVALENT, qualified** — `529 passed in 168.52s` | matches the report. Non-equivalent for a `+`-bearing token: with `TOKEN='tok+en-with+plus'` the revert MISSES `%80/%C0/%FF/%ED%A0%80/%E2%80` splits that the PIN finds (5/5 diverge) |
| **UQP-REPLACE (impl, `unquote_plus_drop` only)** — *not in the report's table* | **full 529** | **EQUIVALENT** — `529 passed in 168.52s` | equivalent for BOTH the ASCII token and the `+`-bearing token (`unquote_drop` alone catches every form). Symmetric row missing (**D5j-F12**) |
| **O-TABLE-DROP** (oracle drops its pinned copy) | **full 529** | **SURVIVED — `529 passed in 168.58s`** | the report says **KILLED**. **D5j-F2 — real finding** |
| **O-UQ-REPLACE (single, `unquote_drop` only)** — *not in the report's table* | 30 oracle vectors | **SURVIVED** (`30 passed`) | same asymmetry as O2_UQ |
| **O2_UQ** (drop `unquote_drop` from the oracle ops) | 30 oracle vectors | **SURVIVED** — qualified equivalent | matches the report |
| **CTL_PARTIAL_noC1** (predicate form, table intact) | **full 529** | **EQUIVALENT — `529 passed in 169.32s`** | the D5i depth-2 mechanism holds: `strip_invis(noC1)` leaves `…tok<C2><80>en…` at depth 1; `utf8_redecode_lenient` reaches `…tok<80>en…` at depth 1 and the token at depth 2 |
| CTL_PARTIAL_noC1 (table-subtraction form) | full 529 | **KILLED — but by the self-test**, `test_invisible_table_is_the_ucd_15_1_class` (1 failed / 528 passed) | see **D5j-F13** |
| **BODYSTR-RECORD-BLANKED** (my own: `backend:502` records `""` for a top-level JSON string body) | **full 529** | **SURVIVED — `529 passed in 168.72s`** | **D5j-F1 — real finding** |
| RECORDLESS_400_APIKEY (my own) | whole main file | 335 passed / 1 failed — `credential_headers_dropped_from_records` stays **green** with no record written | **D5j-F7** |

`M_V12_CLOSE`: N/A (line deleted) — equivalence independently re-confirmed by the pipelining
differential below.

---

## PROBE tables — everything below is my own run, not the report's

### Live 7 sinks × 8 separators (56 cells) — every cell `400` + MARKER + `Connection: close` + record delta 1

Sinks: `header_value`, `header_name`, `query`, `path`, `json_value`, `json_key`, `json_list`.
Separators: `%80`, `%C0`, `%FF`, `%ED%A0%80`, `%E2%80` (the five the brief names) plus the negative
controls `%20`, `%00`, `%E2%80%8B`.

```
CELLS 56  ALL-400+MARKER+close+delta1: 56/56
```
True negatives on the same backend: ordinary POST → `200 OK`; `X-Trace: %25252540` → `200 OK`;
`X-Trace: junk%80junk` → `200 OK`, none blanked.

**The path sink 400s because the screen precedes routing** — confirmed from the code:
`do_GET` calls `state.record(...)` at `backend:645` and returns `self._error(400, …)` at `:648-650`
*before* `self._authorized()` (`:651`) and before any route match (`:653`, `:656`); `do_POST` does
the same at `:677-682` before `:683`/`:685`.

### Parent-vs-child detection differential — re-run by me, 28 096 vectors

Same corpus construction as the predecessor's `vd12/h/p7_diff.py` (3 096 directed + 25 000 random,
seed 11):
```
directed corpus: 3096
TOTAL vectors: 28096
PARENT-found  but PIN-missed          : 0
PARENT-screened but PIN-serves (any)  : 0
PIN-screened but PARENT-served (new)  : 0
ORACLE-not-wider violations           : 0
```
Depth pins from both sides, and the op count:
```
%252B (must SERVE/saturate)        found=True  saturated=True  carries=True
%25252541 suffix (must BLANK)      found=True  saturated=False carries=True
saturating junk %25252540          found=False saturated=True  carries=False
blanking  junk %25252541           found=False saturated=False carries=True
impl: ops = (unquote_drop, unquote_plus_drop, str.lower, utf8_redecode_lenient, strip_invis)  n_ops = 5
depth: for _depth in range(5)
```
**Note the third line: this corpus contains no vector that the change newly catches.** It proves
"no regression", not "the change works" — and it is blind to the saturation flip (**D5j-F6**).
The widening is proved separately:

| separator | parent finds | PIN finds | parent screens | PIN screens | oracle says absent |
|---|---|---|---|---|---|
| `%80` `%C0` `%FF` `%ED%A0%80` `%E2%80` `%C2` `%F5` `%FE` `%C0%80` `%E0%80%80` `%F0%80%80%80` `%ED%BF%BF` | **False** ×12 | **True** ×12 | False ×12 | True ×12 | False ×12 |
| `%20` `%00` `%E2%80%8B` `%2B` (negative controls) | True | True | True | True | False |
| `%25` `%41` (no token) | False | False | False | False | True |

### Invisible table — regenerated by me

| interpreter | UCD | generated members | generated range string == the committed `_INVIS_RANGES` |
|---|---|---|---|
| `/usr/bin/python3.13` | 15.1.0 | **4305** | **byte-identical** (366 tokens both sides) |
| `/usr/bin/python3.12` | 15.0.0 | 4305 | byte-identical |
| `python3` (3.11) | 14.0.0 | 4263 | differs by exactly the 42, as expected |

`_ORACLE_INVIS_RANGES` (`red:100-149`) is **byte-identical** to `_INVIS_RANGES` (`backend:137-186`).
On 3.11 `sorted(pinned − live)` is exactly the 42 code points, and **equals the
`_UCD_15_ADDITIONS` literal in `tests/test_s0_01_scripted_backend.py:2062-2069`**; `live − pinned`
is empty. The 42: `0ECE 10EFD 10EFE 10EFF 11241 11F00 11F01 11F36 11F37 11F38 11F39 11F3A 11F40
11F42 13439 1343A 1343B 1343C 1343D 1343E 1343F 13440 13447 13448 13449 1344A 1344B 1344C 1344D
1344E 1344F 13450 13451 13452 13453 13454 13455 1E08F 1E4EC 1E4ED 1E4EE 1E4EF` — the predecessor's
named subset is contained in it.

### `unicodedata` is out of the runtime path — probed, not read

`grep -n unicodedata` on the backend returns only docstring/comment/generator mentions (`:54`,
`:132`, `:192-198`). Import-time probe with `builtins.__import__` guarded to raise on
`unicodedata` **and** `sys.modules["unicodedata"] = None`:
```
IMPORTED WITH unicodedata BLOCKED: OK; _INVIS_PINNED size = 4305
  U+200B  carries_secret=True     U+10EFD carries_secret=True   U+0ECE  carries_secret=True
  U+2800  carries_secret=True     U+D800  carries_secret=True   U+2028  carries_secret=True
  U+20DD  carries_secret=True     'hello' carries_secret=False
```

### Three-interpreter server-side sweep — 62 code points × 2 sinks × 3 interpreters = 372 cells

Union of the 20 D5h code points, the 42 UCD-15 additions and the five fillers; header sink (raw
UTF-8 wire bytes, `surrogatepass`) and JSON-escape sink (`\uXXXX`, surrogate pairs for astral):
```
py311: header-sink+json-escape-sink over 62 code points -> non-conforming cells: 0
py312: header-sink+json-escape-sink over 62 code points -> non-conforming cells: 0
py313: header-sink+json-escape-sink over 62 code points -> non-conforming cells: 0
```
(conforming = `400` + MARKER + `Connection: close` + record delta 1). The report's table shows 15
of these; I ran 62.

### Impl-vs-oracle differential, standalone on all three interpreters

(oracle imported with a minimal `pytest` shim so the module loads without pytest on 3.12/3.13)

| interpreter | impl strip domain | oracle strip domain | `impl − oracle` | self-test `pinned − live` | differential violations (impl finds ∧ oracle absent), 9 680 vectors |
|---|---|---|---|---|---|
| 3.11.15 / 14.0.0 | 4305 | 4305 | **0** | **42** | **0** |
| 3.12.3 / 15.0.0 | 4305 | 4305 | 0 | 0 | 0 |
| 3.13.12 / 15.1.0 | 4305 | 4305 | 0 | 0 | 0 |

The oracle is `≥` the impl on every interpreter (equal today — it becomes strictly wider only on a
UCD newer than 15.1). The self-test's per-version expectation reproduces standalone under 3.12 and
3.13 (empty) exactly as the brief specified.

### Class boundary against Default_Ignorable_Code_Point

Over the 15 ranges the brief names (4 172 code points), on 3.13 **and** 3.11:
```
ASSIGNED members NOT in the pinned table: 0
UNASSIGNED (Cn) members out of class:     3769   {U+2065:1, U+FFF0-FFF8:9, U+E0000-E0FFF:3759}
```
No assigned zero-width code point sits outside the table. The Cn exclusions are exactly the
documented D5i-F11 ruling (`backend:50-52`, "renders as tofu (visible); a future assignment enters
through table regeneration, never silently"). Live on the **decoded** (JSON-escape) sink:
U+2065, U+FFF0, U+FFF4, U+FFF8, U+FFFD, U+FFFC, U+E0FFF → `200 OK`, not blanked; controls U+2060
and U+200B → `400` + MARKER. On the **header** (byte-view) sink the same Cn code points are caught
incidentally — their UTF-8 continuation bytes land in U+0080-U+009F (Cc, in the table) and the
lenient re-decode drops the remnant at depth 2. See **D5j-F15**.

### Cost — the committed harness, re-run by me

`python3 tasks/briefs/s0-01-d5j-support/cost_probe.py`, load 2.25 → 2.21:
```
    KB |   ordinary | inv-utf8-hdr |  bound-hdr | bound-body
     1 |    0.001 200 |    0.001  400 |    0.001 400 |    0.002 400
    10 |    0.002 200 |    0.002  400 |    0.002 400 |    0.011 400
   100 |    0.013 200 |    0.013  400 |    0.013 400 |    0.102 400
  1000 |    0.118 200 |    0.118  400 |    0.117 400 |    1.027 400
```
**Reproduces the report within 2 %** — D5i-F13's "not reproducible" complaint is closed for this
harness. But the *vector* is the problem (**D5j-F5**); same harness, same box, load 1.52:

| 1 000 KB vector | min-of-5 | status |
|---|---|---|
| ordinary, LANE (tiny object + ~1 MB of trailing SPACES) | **0.120 s** | 200 |
| ordinary, D5i (1 MB payload inside a JSON string) | **0.391 s** | 200 |
| inv-utf8-hdr, LANE (space-padded body) | 0.120 s | 400 |
| inv-utf8-hdr, D5i (`x`-filled body) | 0.311 s | 400 |
| bound-body, LANE (`note` leaf) | 1.007 s | 400 |
| bound-body, D5i (`content` leaf) | 1.286 s | 400 |

Module docstring `backend:74-77` ("~2 s on a quiet 4-core box … bounded by handler timeout (30 s)
and `ThreadingHTTPServer`") is **conservative and true** — `timeout = 30` at `:517`,
`ThreadingHTTPServer` at `:768`, `MAX_CONTENT_LENGTH = 1_048_576` at `:116`, all verified.

### Live controls (the section the report omits)

```
REDACTIONS: 60/60 requests -> 400 ; records 60 ; MARKER records on disk: 60
GET  /v1/models           -> HTTP/1.1 200 OK  ; record path=/v1/models ; auth_fp set: True
POST /v1/chat/completions -> HTTP/1.1 200 OK  ; reply='pong' ; record verbatim: True
STREAM s0-01-slow         -> HTTP/1.1 200 OK  ; 6 data lines ; [DONE] present
MARKER records after the controls: 60  (none overwritten)
```

`Connection: close` on every 4xx — 12 classes, raw socket, **12/12 True**: invalid-UTF-8 header ·
invisible separator header · invisible separator JSON body · **top-level JSON string `"café"` (the
D5i-F1 case, now 400-verbatim)** · 401 no auth · 404 unknown path · 411 Transfer-Encoding · 400
header parse defect · 400 JSON depth > 32 · 417 Expect · 400 duplicate Content-Length · 400
malformed Content-Length.

Header-ignoring socket pipelining on the stream leg: `responses seen: 1 | data lines: 6 | second
response present: False` — the socket still closes with all three `close_connection = True`
statements deleted. M_V12_CLOSE equivalence re-confirmed.

Legitimate-traffic table — **10/10 served 200 and recorded verbatim**: CJK · accented ·
emoji ZWJ family · Devanagari matras · Arabic harakat · Hebrew niqqud · Thai · `a+b=c` ·
`100% of 50%` · a base64 JWT. No false positive from the pinned table.

`--slow-delay` guard, verbatim:
```
nan     rc=2  scripted_backend: --slow-delay nan must be a finite number >= 0
inf     rc=2  scripted_backend: --slow-delay inf must be a finite number >= 0
-1      rc=2  scripted_backend: --slow-delay -1.0 must be a finite number >= 0
1e400   rc=2  scripted_backend: --slow-delay inf must be a finite number >= 0
-nan    rc=2  scripted_backend.py: error: argument --slow-delay: expected one argument
abc     rc=2  scripted_backend.py: error: argument --slow-delay: invalid float: 'abc'
=-inf   rc=2  scripted_backend: --slow-delay -inf must be a finite number >= 0
```

Round-12 hostile-input battery, re-run (15 cases incl. one of my own, `X-Trace: %80`×2000):
**no crash, no hang, every record valid JSON, `GET /healthz` after the battery `200 OK`.**
Depth 32 → 200; depth 33 → 400 + close + **zero** records; top-level `null` / empty body → 400;
`NaN` / `-Infinity` / `1e400` → 200 with a valid record.

**Process census after all my runs:** `ps -eo pid,cmd | grep scripted_backend` → **empty**. Every
backend I started was stopped PID-targeted. (Two unrelated `frame_tee` processes from another
lane's verifier, PIDs 17819/17907, were already running when I started and I did not touch them.)

### `file:line` spot-check — 17 refs grepped on the PIN's final bytes

| # | report ref | claim | what is actually there | verdict |
|---|---|---|---|---|
| 1 | `backend:479` | `byte_view=False` at `body_str` | exact | OK |
| 2 | `backend:286` | `unquote_drop` | `def unquote_drop(x):` | OK |
| 3 | `backend:290` | `unquote_plus_drop` | `def unquote_plus_drop(x):` | OK |
| 4 | `backend:294` | the `ops` tuple | exact | OK |
| 5 | `backend:135-213` / `:277` | ranges + parser / lookup | exact | OK |
| 6 | `backend:528` / `:724` | the two comments | exact | OK |
| 7 | `red:1131` | lone-surrogate test | exact | OK |
| 8 | `red:506-539` / `:521-539` | oracle vectors | exact | OK |
| 9 | `red:957-970` | extended parametrisation | decorator at `:958`, ids end `:970` | OK |
| 10 | `red:502-504` | Cc-arm comments | exact | OK |
| 11 | **`red:134`, `:137`** (and `red:134-139`) | the oracle's two drop-decoders | inside `_ORACLE_INVIS_RANGES`; the defs are at **`red:195`, `:197`** | **WRONG (−61)** |
| 12 | **`red:104-110`** | the rewritten oracle docstring | inside the range string; the docstring is **`red:168-183`** | **WRONG (−64)** |
| 13 | **`red:104-164`** | "own copy + live union" | own copy is `red:100-164`; the **live union is `red:186-189`**, outside the span | **WRONG** |
| 14 | **`red:726`** | "strip_invis + utf8_redecode_lenient" | `mid = len(TOKEN) // 2`; the prose is at **`red:745`** | **WRONG (−19)** |
| 15 | **`red:816`** | "strip_invis (Cc arm)" | an oracle vector tuple; the prose is at **`red:840`** | **WRONG (−24)** |
| 16 | **`red:911`** | "old strip_zwc" | blank line; the prose is at **`red:939`** | **WRONG (−28)** |
| 17 | **`red:711-717`, `:734-740`, `:862-867`** | the three record-delta insertions | the `n0`/`n0+1` pairs are at **`710/714`, `727/733`, `749/758`, `865/869`** — no cited span contains both halves of any of them | **WRONG (−15…−17)** |

**7 of 17 wrong.** The brief's own rule: "three wrong = report discipline failed."

---

## Findings — all of them, no severity filtering

### D5j-F1 — BLOCKING — SOLID — the D5i-F1 test does not pin the record; a record-blanking mutant passes all 529

- **file:line** `tests/red/test_s0_01_backend_credential_screen.py:1094` —
  `assert json.loads(recs[-1].read_text())["body"] != MARKER` (and `:1106` in the control).
- **expected** (brief item 1, verbatim): *"the ordinary route 400 with the record **VERBATIM**, not
  MARKER, record delta 1"*.
- **observed** the assertion is a negation. It passes for **any** non-MARKER body — `None`, `""`, a
  truncated or mangled string.
- **reproduced** mutant `BODYSTR-RECORD-BLANKED`: `backend:502` `rec_body = body` →
  `rec_body = ("" if (isinstance(body, str) and body != "<invalid json>") else body)`.
  Targeted: `4 passed`. **Full scope: `529 passed in 168.72s`, zero failures.** Nothing in the tree
  pins the recorded content of a top-level JSON string body.
- The behaviour itself is correct — I probed live: the records are `'café'`, `'Müller'`, `'£100'`,
  `'hello'`, all delta 1, all `400 Bad Request`. This is a test-strength defect, not a code defect.
- **minimal fix / exact red test**: in `test_top_level_json_string_body_is_not_a_byte_view` replace
  `!= MARKER` with
  `assert json.loads(recs[-1].read_text())["body"] == json.loads(doc.decode("utf-8"))`,
  and the same in `test_top_level_json_string_hello_control` (`== "hello"`). Red under
  BODYSTR-RECORD-BLANKED, green on the PIN.

### D5j-F2 — BLOCKING — SOLID — the report claims `O-TABLE-DROP` is KILLED; it survives the full suite. The oracle's pinned table is unpinned

- **file:line** `D5j-report.md` DONE row 4 — *"O-TABLE-DROP killed by the same oracle vectors"*;
  brief item 3 — *"O-TABLE-DROP (the oracle drops its pinned copy: **killed on 3.11** by the F3
  oracle vectors)"*.
- **observed** dropping `and ord(c) not in _ORACLE_INVIS_PINNED` from the oracle's `strip_invis`
  (`tests/red/test_s0_01_backend_credential_screen.py:186-189`) → **`529 passed in 168.58s`**.
  Targeted at the 30 oracle vectors: `30 passed`.
- **mechanism** the oracle's vector list (`red:485-528`) contains **no** UCD-15 addition — none of
  U+0ECE, U+10EFD, U+1E08F, U+11F36, U+13439. On 3.11 the surviving live-category union alone
  satisfies every vector, so the pinned copy carries no test weight. On 3.12/3.13 it is redundant
  by construction.
- **compounding** nothing in the tree asserts the two 4 KB literals agree:
  `grep -n "_ORACLE_INVIS_RANGES\|_INVIS_RANGES"` over both test files returns only their own
  definitions and two docstring mentions. They are byte-identical today (I diffed them) and can
  silently diverge tomorrow.
- **minimal fix / exact red tests**: (a) add one oracle vector —
  `(TOKEN[:len(TOKEN)//2] + chr(0x0ECE) + TOKEN[len(TOKEN)//2:], False)` with id
  `ucd15_addition_split` — RED on 3.11 under O-TABLE-DROP, green on the PIN; (b) add a cross-check
  in the main test file: load the backend module and
  `assert _parse_oracle_ranges(_ORACLE_INVIS_RANGES) == sb._INVIS_PINNED`.

### D5j-F3 — BLOCKING — SOLID — the `file:line` column is wrong again; row 8's "re-derived with grep on the FINAL bytes" is false (D5i-F8 not closed, third round)

- **file:line** `D5j-report.md` DONE rows 2, 4, 7 and row 8 (*"Every ref in this table re-derived
  with `grep -n` on the FINAL bytes after the last edit"*).
- **observed** 7 of the 17 refs I grepped are wrong, in three distinct systematic bands: −61/−64 on
  the oracle refs, −19/−24/−28 on the prose refs, −15/−17 on the record-delta refs. Full table
  above. `red:134` and `red:137`, cited as the oracle's two decoders, are lines of the
  `_ORACLE_INVIS_RANGES` string literal.
- **minimal fix** re-derive every ref with `grep -n` against the committed blob (not a draft) and
  re-state row 8 only if it is then true.

### D5j-F4 — BLOCKING — SOLID — the report has no live-control section at all, yet claims D5i-F15 closed

- **file:line** `D5j-report.md` DONE row 7 (heading lists `D5i-…/F15`); brief item 7 —
  *"the live-control section states the redaction COUNT"*; brief gate list — *"live normal +
  streaming after >= 50 redactions with the COUNT … the legitimate-traffic table (+ the three
  top-level JSON string bodies at 400-verbatim, `"hello"`, the CJK body)"*.
- **observed** `grep -in "redaction\|streaming\|live\|legitimate"` over the whole report returns
  **nothing** (rc 1). Neither the control, the count, nor the legitimate-traffic table is present.
  D5i-F15 is not closed; it regressed from "count missing" to "section missing".
- **I ran it** (above): 60/60 redactions → 400, 60 MARKER records intact after the controls,
  GET/POST/stream all 200 with the record verbatim, 10/10 legitimate bodies served verbatim,
  the three top-level JSON string bodies 400-with-verbatim-record. **The substance holds** — the
  defect is the omission.
- **minimal fix** paste the section, with the count.

### D5j-F5 — BLOCKING — SOLID — the cost table's "ordinary" column is not an ordinary body, and the brief's >2× disclosure was not made

- **file:line** `tasks/briefs/s0-01-d5j-support/cost_probe.py:100` —
  `body_ord = core + b" " * max(0, size - len(core))`.
- **mechanism** U+0020 is `Zs` and therefore **in `_INVIS_PINNED`**, so `strip_invis` deletes the
  entire 1 MB pad at depth 1 of the very closure the probe is timing. The "ordinary" column
  measures a string that collapses, not a 1 MB body.
- **observed / expected** same harness, same box, load 1.52: lane vector **0.120 s**; a 1 MB
  payload inside a JSON string **0.391 s** — **3.3×**. Same for the `inv-utf8-hdr` column
  (0.120 vs 0.311). D5i's raw-socket harness measured 0.63 s for the honest vector.
- **brief non-compliance** item 9 ends: *"If your ordinary 1000 KB cell differs from the verifier's
  0.63 s by more than 2×, say so with the load — do not tune the vector until the numbers agree."*
  0.117 vs 0.63 is **5.4×** and the report says nothing.
- **minimal fix** put the pad inside a JSON string value
  (`{"model":…,"messages":[{"role":"user","content":"x"*size}]}`), re-run, and state the residual
  divergence from D5i with the load.

### D5j-F6 — SOLID — "strictly wider" is true only of the token-found arm; the saturation arm is not monotone, and the pinned corpus cannot see it

- **file:line** `proofs/S0-01/tools/scripted_backend.py:266-269` (op docstring) and
  `D5j-report.md` SELF-ATTACK §2 (*"for an ASCII token, `errors='ignore'` is strictly wider than
  `errors='replace'`"*).
- **observed** `_carries_secret` has two arms — `any(t in f)` **and** `not saturated`. The
  monotonicity argument covers only the first. Over a 20 000-vector percent-dense corpus (alphabet
  `%20 %80 %C0 %FF %25 %2B %2520 %252520 + space tab ZWSP` + alphanumerics, seed 3), **105 vectors
  move from parent-screened (bound exceeded → record blanked) to PIN-served**, e.g.
  `'s0-01-upstream-tok%2B%C0%252520%209\t %C0en-0123456789abcdef'` and
  `'s0-01-upstream-tok0%C0b%252520%C0+en-0123456789abcdef'`. In the same corpus 370 vectors move
  the other way (the intended widening).
- **not a leak** for all 105 the depth-6 oracle agrees the token is absent (`0` of 105), and an
  independent 30 000-vector hostile sweep found **0** cases of oracle-finds-and-impl-serves. So
  this is a false-positive reduction, not a detection regression.
- **evidence-scope point** the brief's pinned proof — the 28 096-vector corpus — returns
  `PARENT-screened but PIN-serves: 0`, because that corpus never places percent-encoded junk
  densely enough to flip saturation. "0 regressions" on it is not evidence about the fail-closed
  arm. (I re-ran it; the result is genuine, just narrower than it reads.)
- **minimal fix** amend `backend:266-269` to: *"strictly wider in the token-found arm. The
  saturation arm is not monotone: dropping bytes shortens forms and can let a closure saturate that
  previously exceeded the bound (measured: 105 of 20 000 percent-dense vectors move from
  fail-closed to served; the depth-6 oracle confirms the token is absent in all of them)."*
  Exact red test to pin it: a `test_pct_dense_junk_that_now_saturates_is_served` asserting one of
  the 105 vectors returns 200 **and** `_absent_under_all_normalizations(record)` is True.

### D5j-F7 — SOLID — the stale-`[-1]` class is closed in the red file but 8 tests in the main file still read the last record with no delta

- **file:line** `tests/test_s0_01_scripted_backend.py:144, 175, 202, 212, 296, 446, 459, 487`.
  (The red file is clean: 33 of 33 last-record reads carry a `== n0 + 1` / `== count_before + 1`.)
- **reproduced** mutant `RECORDLESS_400_APIKEY` (`_framing_gate` rejects any request carrying an
  `api-key` header with 400 and writes no record). Over the whole main file: `1 failed, 335 passed`
  — the only casualty is `test_credential_in_credential_header_returns_400[api-key]`, while
  **`test_credential_headers_dropped_from_records` stays green reading a record written by an
  earlier test**. That is the D5h-F11 / D5i-F6 class, unclosed.
- Out of this lane's pinned three-test scope, so **non-blocking** — but the class the report and
  brief describe as closed is not closed tree-wide.
- **minimal fix** add `n0 = len(list(backend["rec"].glob("*.json")))` before the call and
  `assert len(recs) == n0 + 1` before the `recs[-1]` read in the 8 tests.

### D5j-F8 — SOLID (minor) — the test-count decomposition in DISCREPANCIES §1 is wrong in two places; the errors cancel

- **file:line** `D5j-report.md:123`.
- **report** *"4 for the hello control; … 6 oracle vectors"*.
- **measured** per-test `--collect-only` diff, parent 500 → PIN 529: `top_level_json_string_hello_control`
  **+1** (not 4); `TestOracleSelfTests::test_oracle_known_vectors` **21 → 30 = +9** (not 6). Every
  other term is right, and 4+6 = 1+9, so the total 29 is correct by coincidence.
- **minimal fix** restate: 3 + 1 + 4 + 1 + 9 (parametrisation) + 9 (oracle vectors) + 2 = 29.

### D5j-F9 — SOLID (minor) — brief item 6 asked for ONE comment; the tree has two

- **file:line** `backend:528` (in `_reject`) and `:724` (in `_stream`). Brief: *"ONE comment at the
  `_stream` site cites the mechanism"*. The report discloses both, so this is a disclosed
  deviation, not a concealed one. Harmless.
- **minimal fix** delete the `:528` comment, or leave it and note the deliberate deviation.

### D5j-F10 — SOLID (minor) — the `byte_view=True` PROBE block is an annotated rendering, not the pasted grep

- **file:line** `D5j-report.md:89-97`, headed *"`grep -n "byte_view=True"` on the final backend
  (4 sites…)"* but showing three re-typed lines with added labels.
- **actual** `grep -n "byte_view=True"` yields three lines — `468`, `472`, `490` — carrying **four**
  occurrences (`:472` holds two, for header name and header value). The count and line numbers are
  right; the brief said "paste it".
- **minimal fix** paste the raw grep output and say "3 lines / 4 occurrences".

### D5j-F11 — SOLID (minor) — the depth-pin sentence mis-cites the test's vector

- **file:line** `D5j-report.md:111` — *"`test_saturating_junk_is_served` (`%25252540` → served)"*.
- **actual** that test's vector is `X-Trace: %252B` (`tests/test_s0_01_scripted_backend.py:1987`).
  Both saturate and are served — I measured `%252B` `found=True saturated=True carries=True` and
  `%25252540` `found=False saturated=True carries=False` — so the claim is true of the code but not
  of the named test. (The brief made the same slip; the report copied it.)

### D5j-F12 — SOLID (informational) — the mutant table names only one of each pair of symmetric single-decoder reverts

- **impl** `UQP-REPLACE` (revert only `unquote_plus_drop`, `backend:293`) also **survives the full
  529** and is equivalent for *both* an ASCII token and a `+`-bearing token — measured; the table
  lists only `UQ-REPLACE`.
- **oracle** the single-decoder oracle revert (only `unquote_drop`, `red:196`) survives all 30
  oracle vectors; the table lists only the both-decoder `O-UQ-REPLACE`.
- Neither is a code defect; the mutant table's coverage claim is incomplete.

### D5j-F13 — SOLID (informational) — the `CTL_PARTIAL_noC1` row's verdict is stale in form

- **file:line** `D5j-report.md:63` — *"CTL_PARTIAL_noC1: EQUIVALENT (mechanism unchanged from D5i)"*.
- **observed** expressed the D5i way (subtract U+0080-U+009F from the class) it is now **KILLED** —
  by `test_invisible_table_is_the_ucd_15_1_class`, i.e. by the table's size/diff self-test, not by
  any behavioural vector (`1 failed, 528 passed`). Expressed at the predicate with the table intact
  (`ord(c) not in _INVIS_PINNED or 0x80 <= ord(c) <= 0x9F`) it **survives the full 529**, so the
  behavioural equivalence the report asserts does hold.
- **corollary worth stating**: with a pinned table, *every* `TABLE-DROP-*` mutant is killed twice —
  once behaviourally and once by the self-test. I ran each with a behavioural-only `-k` filter to
  prove the behavioural killer exists independently; all five do.
- **minimal fix** one sentence in the row distinguishing the two forms.

### D5j-F14 — SOLID (informational) — the generator recorded in the docstring is not runnable as written

- **file:line** `backend:192-201` ends `# ... build ranges, join as 'start-end' hex pairs,
  space-separated`; the module comment at `:132` elides further:
  `Generated by: /usr/bin/python3.13 -c "import unicodedata; cats = ..."`.
- Brief item 3: *"generated by a generator recorded **VERBATIM** in the docstring"*. A reader
  cannot copy-paste and regenerate. I reconstructed the missing run-length step and the output is
  **byte-identical** to the committed string under 3.13 and 3.12, so the table is correct — only
  its provenance is not self-contained.
- **minimal fix** paste the complete ~12-line generator.

### D5j-F15 — SOLID (informational, design) — 10 permanently-reserved BMP code points remain usable as invisible splitters on the decoded sink

- U+2065 (inside the U+2060-U+2064 invisible-operator run) and U+FFF0-U+FFF8 are `Cn` and out of
  class by the pinned D5i-F11 ruling. Live on the JSON-escape sink they are **served 200, record
  kept** (measured above); on the header sink they are caught incidentally.
- This is the coordinator's ruling, followed correctly by the lane — raised under item 11, not as a
  lane defect.

### D5j-F16 — SOLID (informational) — the `RECORDLESS_400_XTRACE` row understates the kill the brief asked for

- **file:line** `D5j-report.md:57` (`ran 8`) and DONE row 5 (*"now kills all 8 cases (1 + 6 + 1)"*).
- Brief item 5: *"must now fail **ALL twelve** cases (4 + 8) — paste the line."*
- **I ran the twelve-case selection**: `12 failed, 517 deselected in 0.49s` — all four
  `invalid_utf8_separator_in_header` params plus the eight newly-fixed. **The tree meets the
  brief; the report does not say so.**

### D5j-F17 — SOLID (informational) — the mutant table's `ran` column is inconsistent (sometimes failures, not tests executed)

- **file:line** `D5j-report.md:48-57`. `TABLE-DROP-ZLZP ran=2` and `TABLE-DROP-FILLERS ran=5` —
  but the parametrisation they name has **13** cases and all 13 execute (I measured
  `ran=13 failed=2` and `ran=13 failed=5`). `BODYSTR-BYTEVIEW-TRUE ran=3` — 4 execute.
  `O-UQ-REPLACE ran=30` and `TABLE-EMPTY ran=8` are executed counts.
- The `ran > 0` discipline exists because a `-k` filter matching nothing exits 0; a column that
  sometimes reports failures defeats it.
- **minimal fix** record the executed count (`failed + passed`) in that column, uniformly.

---

## Item 11 — the design itself, where I would have designed it differently

1. **The pure pinned table in the IMPL, versus `pinned ∪ live`.** I would have kept the pinned set
   as a **floor** and unioned the live categories in the impl:
   `if ord(c) in _INVIS_PINNED or unicodedata.category(c) in _INVIS_CATEGORIES`.
   *Evidence:* today the two are **equal** on 3.11/3.12/3.13 (I measured `impl − oracle = 0` and
   `oracle − impl = 0` on all three), so the union costs nothing now. On a UCD newer than 15.1 the
   pinned-only impl becomes **strictly narrower than the interpreter's own knowledge** — a code
   point the runtime knows is a format character is not stripped. The self-test
   `test_invisible_table_is_the_ucd_15_1_class` fails loudly in that world, which is good design —
   but it fails at *gate* time, not at *serve* time, and this fixture is meant to run on the PC
   whose interpreter the repo does not pin. The union keeps determinism of the floor (the pinned
   set is stripped on every interpreter, which is what D5i-F3 actually demanded) while making the
   runtime monotone. *Counter-argument, stated fairly:* a wider runtime re-introduces
   interpreter-dependent **false positives** (a newly-assigned Mn starts blanking records on one
   venue and not another). I weigh a venue-divergent blanked record below a venue-divergent leak,
   so I would take the union. The brief's stated reason ("the table is a property of the repo, not
   the runtime") is a real principle; my disagreement is that it should govern the floor, not the
   ceiling.

2. **The drop-variant as a replacement rather than a sixth op — right call, wrong justification.**
   Replacing keeps `n_ops = 5` and leaves the depth pins untouched (verified: `%252B` saturates and
   is served, `%25252541` does not and blanks; M_D4 and M_D6 both still die). Adding drop-variants
   as ops 6 and 7 would have been monotone in the token-found arm but would have raised the
   branching factor and moved both depth pins — a much larger change for no measured gain.
   **But the "strictly wider" justification is not sound as written**: replacement is not monotone
   in the saturation arm (105/20 000 pct-dense vectors move from fail-closed to served — D5j-F6).
   I would have shipped the same code with the honest justification, and with one committed test
   pinning a saturation-flip vector so the next round cannot regress it silently.

3. **Cn out of class — I would carve out the permanently-reserved BMP slots.** The ruling is
   correct for the ~800k unassigned code points (tofu, and a future assignment should come through
   regeneration). But U+2065 and U+FFF0-U+FFF8 are *permanently reserved* slots sitting **inside**
   Default_Ignorable runs, and several renderers draw them as nothing. They are exactly 10 code
   points, they can never be assigned to a visible character, and they are the only Cn members of
   the Default_Ignorable list in the BMP (I enumerated: `{U+2065: 1, U+FFF0-FFF8: 9,
   U+E0000-E0FFF: 3759}`). Adding those 10 to `_INVISIBLE_EXTRA` costs 10 entries and closes a hole
   I demonstrated live (`U+2065` splits the token on the decoded sink and is served `200 OK`). The
   plane-14 reserved run I would leave out, as the ruling says.

4. **The oracle should not be a second hand-maintained copy of a 4 KB literal.** Two literals that
   must stay identical, with no test that they are, is a defect waiting to happen (D5j-F2). I would
   have the oracle read the impl's string out of the source file with the same regex the red file
   already uses for `MAX_CONTENT_LENGTH` (`red:24`) — that keeps the oracle *independent in
   algorithm* (its own depth-6 BFS, its own JSON seeding, its own live-category union) while
   removing the duplicated data. Oracle independence is about the *decision procedure*, not about
   re-typing a table.

5. **`!= MARKER` should never be an acceptance assertion in this suite.** The whole point of the
   record is its content. Every "served, not blanked" test should assert the recorded value
   (D5j-F1). Cheap, and it would have caught this one at write time.

---

## What I reproduced vs reviewed statically vs deliberately skipped

**Reproduced first-hand (live or by execution):** both gate runs · the red standalone · pyflakes ·
the red-before state on the parent implementation (9 failures, named) · the parent/child collect
counts (500 → 529) and the per-test delta · 41 mutants (35 killed with named killers, 6 survivors
classed), each on a scratchpad copy with the shared tree asserted clean · the 28 096-vector
parent-vs-child differential · a 20 000-vector saturation-flip census and a 30 000-vector
oracle-finds/impl-serves sweep · the 56-cell live 7×8 sink matrix · the 372-cell three-interpreter
server-side sweep · the invisible-table regeneration under 3.13/3.12/3.11 (byte-identical) · the
oracle/impl range-string identity · the 42-code-point computation vs the committed literal · the
`unicodedata`-blocked import probe · the impl-vs-oracle differential standalone on all three
interpreters · the Default_Ignorable boundary enumeration · the class boundary live on both sinks ·
the committed cost probe plus a vector-vs-harness isolation · the 12-class `Connection: close`
table · the header-ignoring pipelining differential · 60 redactions + normal + streaming controls ·
the legitimate-traffic table · the `--slow-delay` guard · the hostile-input battery · the process
census · all 17 `file:line` spot-checks.

**Reviewed statically (read, not executed):** the CPython `send_header` mechanism behind
M_V12_CLOSE — I re-confirmed the *behaviour* with the pipelining differential rather than re-reading
`/usr/lib/python3.11/http/server.py`, since the predecessor quoted it and the behaviour is what
matters · the wiki/ledger lines in the PIN commit (outside the three scope files) · the report's
prose claims about D5h-era findings that predate this lane.

**Deliberately skipped, with reason:** the **PC leg** — no bridge in this lane and the brief
assigns it to the coordinator; the PC gate line (`529 passed in 51.30s`, run
`20260907T192543Z-9da1041`) is reviewed, not reproduced, and nothing in my verdict depends on it ·
`scripts/lint_delta.py --base <PIN>` — it needs the shared repo's git and the PIN is now two
commits back; pyflakes rc 0 on the three files covers the same ground and the report's "0 NEW hits"
is consistent with it · a full 529-run for every mutant — I used behavioural `-k` filters with the
executed count recorded, and escalated only the six survivor claims to full scope · re-running the
D5h-era mutants that neither the brief nor this diff touches.

---

## VERDICT — **NOT-READY**

The three D5i BLOCKING findings are genuinely fixed **in the code**, and I could not break the
screen: 0 leaks over 30 000 hostile vectors, 56/56 live sink cells, 372/372 three-interpreter
cells, 0 impl-vs-oracle violations on three interpreters, and no false positive on 10 legitimate
traffic shapes. **Nothing in the blocking set is a credential leak.** What blocks is that the
report asserts closures the tree does not have, and two of the brief's named proof obligations are
unmet.

**Blocking set**

| # | why it blocks |
|---|---|
| **D5j-F1** | brief item 1 required the record **VERBATIM**; the test asserts `!= MARKER`, and a mutant that records an empty body passes all 529. A guard that was never red for the property it claims is a hollow green. |
| **D5j-F2** | brief item 3 named `O-TABLE-DROP` as a mutant that must die; it survives the full 529, and the report states it KILLED. A false KILLED claim is worse than a disclosed survivor. |
| **D5j-F3** | brief item 8's own rule — "three wrong = report discipline failed"; 7 of 17 refs are wrong and row 8 asserts they were all re-derived. Third round of the same defect. |
| **D5j-F4** | the brief's gate list required a live-control section with the redaction count and the legitimate-traffic table; the report has neither, and claims D5i-F15 closed. |
| **D5j-F5** | brief item 9 gave an explicit disclosure instruction (>2× divergence) that was not followed, and the published "ordinary" baseline is 3.3× low because its 1 MB pad is spaces that `strip_invis` deletes. |

**Non-blocking, real:** D5j-F6 (docstring over-claims monotonicity — the code is fine), D5j-F7
(8 stale-`[-1]` tests in the main file, out of this lane's scope), D5j-F8, F9, F10, F11, F12, F13,
F14, F16, F17. **Design disagreements for the coordinator:** item 11 above, of which the
`pinned ∪ live` question (§1) and the 10 reserved BMP code points (§3) are the two I would actually
change.

Every blocking item is a small, mechanical fix: two assertion strengthenings, one oracle vector plus
one cross-check test, one re-derivation of line numbers, one pasted section, and one one-line change
to the cost vector. None requires re-opening the design.

**This verdict does not depend on anything I did not reproduce**, with one stated exception: the PC
gate line is reviewed, not reproduced, and no finding rests on it.
