# VERIFY-D5i — round-12 adversarial grade of lane D5i (S0-01 scripted backend credential screen)

## Premise (verified first-hand, not assumed)

| item | value |
|---|---|
| PIN (dispatch) | `c4805df292497cb8074526424ec7cdec22a5d803` — `git cat-file -e` rc 0. Subject: *"S0-01 WIP checkpoint 8r: backend prechecks only wire-byte sinks, closes the invisible-separator class by Unicode category, pins the record wiring (lane D5i) — REVIEW-PENDING, nothing minted"* |
| shared-tree HEAD | `f0ae7eb` at my start, `fc35fbb` at my end (other lanes committed during the run); `git diff --stat c4805df HEAD -- <the 3 scope files>` = **EMPTY at both** |
| PIN parent | `4b432847b685a0070fc37996dd1d89cea971a337` (checkpoint 8q, lane B5f) |
| report's claimed PIN | `618749fafdc9032696729b53e8c176859e3891a8` — EXISTS, is a true ancestor, but is the **brief** commit, **3 commits back** (`618749f → 9b2803c → 4b43284 → c4805df`). See D5i-F12. |
| grade copy | `git archive c4805df \| tar -x` → scratchpad `vd12/pin`, own `git init` + base commit; `git status --porcelain` = 0 lines |
| backend sha256 / lines | `7732a6f64b495ab28a42d69f703d4ec1eadf1de34c775a544d988be715024b5a` / 676 — **matches the report's FILE IDENTITY exactly** |
| main-test sha256 / lines | `a59c63da87eb2006f8b42afcbcd1ce0e0f9c6da0248b1467a8a39dc18a14c320` / 2031 — **matches** |
| red-test sha256 / lines | `feaaf78b17a8c8e43a45346904d980cc890517649ef7ecc606499fe95a7398b8` / 967 — **matches** |
| interpreters | `python3` = /usr/local/bin/python3 **3.11.15, unicodedata 14.0.0**; python3.12.3 → UCD **15.0.0**; python3.13.12 → UCD **15.1.0**. pytest 9.1.1 (3.11 only — no pytest on 3.12/3.13). pyflakes 3.4.0 |
| load average at start | `4.89 4.38 3.28`; ranged 1.1–2.6 during the probes. **Every timing claim below carries its own load.** |
| other lanes | a foreign pytest run (`test_s0_01_check_acp_conformance.py …`, PID 2342) held the box during part of my run — noted where it matters. My mutants ran on scratchpad copies only; the shared tree saw read-only git. |

## Gate runs — reproduced first-hand, pasted verbatim (scratch copy of the PIN)

```
RUN 1            pytest-summary: 500 passed in 168.60s (0:02:48)   pytest-exit: 0     (load 2.4 → 2.6)
RUN 2            pytest-summary: 500 passed in 168.32s (0:02:48)   pytest-exit: 0     (load 1.9 → 1.6)
RED STANDALONE   pytest-summary: 166 passed in 70.81s  (0:01:10)   pytest-exit: 0
pyflakes (3 files)                                     rc: 0
collect-only, PIN         : 500 tests collected
collect-only, PIN parent  : 469 tests collected   →  delta +31, the report's DISCREPANCY #1 reproduces exactly
```

The report's `500 passed in 168.44s`, `166 passed in 70.82s`, `pyflakes rc 0` and `+31` all reproduce.

## Red-before — reproduced on the PIN's parent implementation + the PIN's tests

Separate scratch tree (`vd12/red`): the PIN's three files, backend swapped for the parent blob
(`sha256 e6b93b14b126075b98be13b52a8dfba15ab2219de2b745e95073195071c11afc` = the D5h-graded backend).

```
20 failed, 4 passed, 142 deselected in 65.71s
```

| test | report's label | my observation | verdict |
|---|---|---|---|
| `test_ordinary_latin1_text_in_json_body_is_served` ×6 | RED `assert b'400 Bad Request' == b'200 OK'` | **RED**, verbatim `AssertionError: assert b'HTTP/1.1 400 Bad Request' == b'HTTP/1.1 200 OK'` | ✔ |
| `test_credential_invisible_separator_in_header_returns_400` ×8 | RED `assert b'200 OK' == b'400 Bad Request'` | **RED**, verbatim `AssertionError: assert b'HTTP/1.1 200 OK' == b'HTTP/1.1 400 Bad Request'` | ✔ |
| `…invisible_separator_in_json_body…` ×4 | RED, same assertion | **RED**, same assertion | ✔ |
| `test_credential_function_application_separator_in_header_returns_400` | RED, same assertion | **RED**, same assertion | ✔ |
| `test_precheck_before_closure_on_invalid_utf8` | RED `TypeError: … unexpected keyword argument 'byte_view'` | **RED**, verbatim `TypeError: State._carries_secret() got an unexpected keyword argument 'byte_view'` at red `:963` | ✔ |
| `test_credential_c1_control_wire_form_returns_400` ×3 | CONTROL (green on PIN parent) | **PASS** | ✔ |
| `test_invalid_utf8_without_the_token_is_refused_not_repaired` | CONTROL | **PASS** | ✔ |
| `test_record_does_not_mutate_the_caller_body` | CONTROL | **PASS** on the parent | ✔ |
| `test_json_safe_copy_on_write` | CONTROL | **PASS** on the parent | ✔ |

**Every red-before line the report claims is the line the run actually produced.** D5h-F9 is closed.

## D5h-F1…F15 closure table

| D5h finding | closed? | by what, verified how |
|---|---|---|
| **F1** precheck rejects ordinary accented text in a JSON body | **CLOSED for the leaf walk; STILL OPEN at a second call site** | `_carries_secret(s, *, byte_view)` at `backend:325`; leaf walk at `:383` passes `byte_view=False`. Live: all six D5h vectors (`café`/`Müller`/`señor`/`£100`/`50°C`/`© 2026`) inside a JSON object → **200 OK + verbatim record**. **But** `body_str` at `:375` still passes `byte_view=True`, and `body` is a decoded `str` whenever the top-level JSON value is a string → `POST` body `"café"` → **400 + MARKER**. See **D5i-F1**. |
| **F2** 20 invisible separators split the token and are served | **CLOSED for the 20 named — the CLASS is not closed** | All 20 of D5h's served list now `_carries_secret = True` and oracle `absent = False` (in-process, PIN bytes); live on the header sink all 400/MARKER/close on 3.11+3.12+3.13. **But** the class is now defined by `unicodedata.category`, whose table is interpreter-dependent (**D5i-F3**), and the same class is re-opened through percent-encoding (**D5i-F2**) and through unassigned code points (**D5i-F11**). |
| **F3** `State.record`'s use of `_json_safe` unpinned | **CLOSED** | `test_record_does_not_mutate_the_caller_body` at main `:2019`; `JSONSAFE_INLINE_IN_RECORD` dies on it (reproduced, see mutant table). |
| **F4** `strip_ctl`'s C1 arm unpinned | **NOT closed — re-classified, not fixed** | `strip_ctl` was deleted; the C1 arm now lives in `strip_invis`'s `Cc` member. `CTL_PARTIAL_noC1` still survives (the lane says EQUIVALENT). Mechanism re-derived below — the lane's stated depth-2 mechanism reproduces, so the equivalence claim is **correct**; but the consequence is that the `Cc` member of `_INVIS_CATEGORIES` has no killer of its own. |
| **F5** nothing distinguishes "refuse" from "guess" | **CLOSED** | `test_invalid_utf8_without_the_token_is_refused_not_repaired` (red `:924`); `LENIENT_IN_IMPL` and `BYTEVIEW_ALL_FALSE` both die on it (reproduced). |
| **F6** report `file:line` wrong in 14/22 | **NOT closed** | 11 of ~22 spot-checks wrong again, with a systematic **+2** offset on every `record()` call-site line. See **D5i-F8**. |
| **F7** report PIN names the brief commit | **NOT closed** | the report names `618749f`, again the brief commit, now **3 commits back**; the word "CHILD" is wrong. See **D5i-F12**. |
| **F8** cost table not reproducible / expensive arm untabulated | **partially closed** | three columns are now published with a stated load and named vectors. My re-measurement is below; the report's own note admits all three columns converge because the chosen vectors put the expensive input in a *header*, not the body — so the bound-exceeded column still does not measure the expensive arm. See **D5i-F13**. |
| **F9** fabricated red-before line | **CLOSED** | every red-before line I ran matches the report verbatim, including the `TypeError` for the `byte_view` test. |
| **F10** wrong killer attribution (`M_MC5_NOTUPLE`) | **CLOSED in form** | the table now names the mutated line per row. Two attributions are still wrong: `M_V12_CLOSE`'s stated *mechanism* (D5i-F7) and `M_UTF8_PRECHECK_DEL`/`LENIENT_IN_IMPL` being listed as two rows for the same mutation (`:345` precheck deleted) — the report says so itself in its summary. |
| **F11** stale-last-record assertions | **CLOSED for the 3 named tests; NOT closed as a class** | deltas added at red `:705/:709`, `:730/:734`, `:768/:772`. Three other tests still read `[-1]` with no delta: red `:641`, `:662`, `:785`. See **D5i-F6**. |
| **F12** O2 qualifier not durable in-tree | **CLOSED** | red `:113-114`: *"``unquote`` is redundant with ``unquote_plus`` only for a token containing no ``+``; it stays so the oracle is token-agnostic (D5h-F12)."* |
| **F13** precheck premise falsified / FP class undocumented | **CLOSED for the leaf sink; the restated premise is itself false** | `_has_invalid_utf8_bytes` docstring (`:134-145`) and `_carries_secret` docstring (`:326-341`) both now scope the precheck to "header names, header values, path/query, the raw body". That enumeration is **wrong**: `body_str` at `:375` is a fifth `byte_view=True` sink and is *not* a byte view when the parsed body is a `str`. See **D5i-F1/F10**. |
| **F14** `PRECHECK_AFTER_CLOSURE` unpinned ordering | **CLOSED** | `test_precheck_before_closure_on_invalid_utf8` (red `:944`) monkeypatches `_normal_forms` with a counter; `PRECHECK_AFTER_CLOSURE` dies on it (reproduced). |
| **F15** report/probe-table mismatches | **partially** | the legitimate-traffic table is now published with 6 rows; the live normal-traffic + streaming control after ≥50 redactions is claimed but the report gives no redaction count. Re-run below. |

## Item 2 — the byte-view split: every `_carries_secret` call site vs the real data path

`grep -n` on the PIN, `proofs/S0-01/tools/scripted_backend.py`:

| line | call site | flag | is the string really a latin-1 view of wire bytes? |
|---|---|---|---|
| `:367` | `path` | `True` | **yes** — `http.server` splits the request line and decodes latin-1 |
| `:371` | `str(k)` header name, `str(v)` header value | `True` | **yes** — `email.parser` decodes the header block latin-1 |
| **`:375`** | **`body_str`** | **`True`** | **NO when `body` is a `str`.** `body_str = body if isinstance(body, str) else json.dumps(body)`. `json.dumps` is `ensure_ascii=True`, so the dict branch is harmless; the `str` branch reaches this line with a string `json.loads` has already **decoded** — every top-level JSON string document, plus the `"<invalid json>"` literal. **This is D5h-F1, unfixed.** |
| `:383` | `_iter_json_strings(body)` leaves | `False` | correct — decoded |
| `:386` | `raw_body.decode("latin-1")` | `True` | **yes** — constructed from the raw bytes |

### False-positive direction, live (own subprocess backend, PIN bytes, load 2.4 to 2.6)

| vector | sink | observed | verdict |
|---|---|---|---|
| percent-encoded `%C3%A9` in query | query | `200 OK`, record verbatim | ok |
| percent-encoded `%C3%A9` in path | path | `404 Not Found` (route), record verbatim, no blanking | ok |
| header value, wire bytes `C3 A9` / `E4 B8 96` / `F0 9F 98 80` / `C2 A3` | header_value | `200 OK`, record verbatim (`'v-Ã©-w'` etc.) | ok |
| plain-text POST, valid UTF-8 "cafe-acute" (not JSON) | raw body | `400 Bad Request` "body is not JSON", record **NOT** blanked | ok (route 400, not a precheck 400) |
| plain-text POST, ASCII `hello` | raw body | `400`, record not blanked | ok |
| "cafe-acute" inside a JSON object leaf (the D5h-F1 vector, 6 forms) | json leaf | `200 OK`, record verbatim | **D5h-F1 closed here** |
| **`"cafe-acute"` as the whole body (a valid JSON document)** | **body_str** | **`400 Bad Request`, record `{"credential_in_unexpected_location": true}`** | **FAIL — D5i-F1** |
| **`"café"` — pure ASCII on the wire** | **body_str** | **`400 Bad Request` + MARKER** | **FAIL — D5i-F1** (no byte-view story exists at all here) |
| `"CJK"` as the whole body (not latin-1-encodable) | body_str | `400` route error, record verbatim | ok |
| `"hello"` as the whole body | body_str | `400` route error, record verbatim | ok |

### Fail-closed direction, live — invalid wire bytes (`0x80 0xC0`) on every byte-view sink

| sink | observed |
|---|---|
| header value | `400` + MARKER + close + record delta 1 |
| header name | `400` + close + **record delta 0** (`_framing_gate` arm 1 — the mechanism D5h re-derived) |
| query | `400` + MARKER + close |
| path | `400` + MARKER + close |
| raw body (non-JSON) | `400` + MARKER + close |
| raw body (JSON-shaped) | `400` + MARKER + close |

**No fail-open on any byte-view sink.** (My first pass showed a false "200 OK" on the header-value row —
that was **my harness** encoding the wire bytes as UTF-8 rather than latin-1; corrected and re-run. Stated
so the number is not taken from the wrong run.)

### The leaf walk is caught through the LENIENT op, not the precheck (in-process, PIN bytes)

| D5g JSON twin (JSON escape) | `_has_invalid_utf8_bytes` | 5-op closure finds | closure **without** the lenient op |
|---|---|---|---|
| `<U+0080>` (`u0080`) | True (but unreachable — `byte_view=False`) | **True** | True (`strip_invis` Cc arm) |
| `À ` (`overlong_pair`) | True (unreachable) | **True** | **False, saturates, served** |
| `â<U+0080><U+0080><U+0080>` (`enquad_plus_junk`) | True (unreachable) | **True** | **False, saturates, served** |

Two of the three twins are caught **only** through `utf8_redecode_lenient`. `LENIENT_DEL_IMPL` therefore dies
on `[overlong_pair]` and `[enquad_plus_junk]` — the report's named killer is right.

## Item 3 — the invisible class closed by CATEGORY: exact domain, class boundary, false positives

### 3a. `strip_invis`'s domain, derived from the code (`backend:176-184`, `:120-125`)

```
strip_invis(x) = "".join(c for c in x
                         if unicodedata.category(c) not in {Cf,Cs,Cc,Mn,Me,Zs,Zl,Zp}
                         and c not in {U+115F,U+1160,U+3164,U+FFA0,U+2800,U+180E})
```
Mirrored **verbatim** in the oracle at red `:117-119` with the same two frozensets at red `:93-99`.
Membership count on this interpreter: **4263 code points** (python3.11 / UCD 14.0.0).

### 3b. D5h's 20 "served" code points — all now CAUGHT

In-process against the PIN's module, `_carries_secret(TOKEN[:mid] + chr(cp) + TOKEN[mid:], byte_view=False)`
and the oracle's `_absent_under_all_normalizations` on the same string:

U+034F, U+061C, U+115F, U+1160, U+180E, U+200C, U+200D, U+200E, U+200F, U+202A, U+202E, U+2061,
U+2800, U+3164, U+FE00, U+FFA0, U+1D173, U+E0001, U+E0020, lone U+D800 —
**20/20 `impl_caught=True`, 20/20 `oracle_absent=False`. STILL OPEN: none.**

Live on the header sink (7 sinks were checked; the header row is representative), all three interpreters:
`400 Bad Request` + MARKER + `Connection: close` + record delta 1 for every one.

### 3c. Class boundary — what survives

| code point | category | caught? | invisible/zero-width? | verdict |
|---|---|---|---|---|
| U+E0100…U+E01EF variation selectors supplement | Mn | **yes** | yes | closed |
| U+2062 / U+2063 / U+2064 invisible times/separator/plus | Cf | **yes** | yes | closed |
| U+FFF9 / U+FFFA / U+FFFB interlinear annotation | Cf | **yes** | yes | closed |
| U+1BCA0…U+1BCA3 shorthand format | Cf | **yes** | yes | closed |
| U+180B / U+180C / U+180D / U+180F Mongolian FVS | Mn | **yes** | yes | closed |
| U+FE0F VS16 | Mn | **yes** | yes | closed |
| U+0300 / U+0301 combining marks | Mn | **yes** | yes (nonspacing) | closed |
| U+20DD / U+0488 enclosing marks | Me | **yes** | yes | closed |
| U+115F / U+1160 Hangul jamo fillers | Lo | **yes** (via `_INVISIBLE_EXTRA`) | yes | closed but **unpinned** (D5i-F4) |
| U+0903 / U+093F Devanagari matras | **Mc** | no | **no** — spacing marks, visible | correct exclusion |
| U+FFFD replacement / U+FFFC object replacement / U+1D159 null notehead | So | no | **no** — visible glyphs | correct exclusion; but see **D5i-F2**, U+FFFD is exactly what `unquote` manufactures |
| U+0F0C Tibetan delimiter | Po | no | no | correct exclusion |
| **U+2065** | **Cn (unassigned, permanently reserved)** | **no** | reserved slot inside the U+2060–U+2064 invisible-operator run; renders as nothing-or-tofu | **D5i-F11** |
| **U+10EFD, U+1E08F, U+11F36, U+13439, U+0ECE, U+11241, U+1E4EC (+35 more)** | **Mn/Cf in UCD 15.x, Cn in UCD 14.0** | **no on python3.11**, yes on 3.12/3.13 | yes (nonspacing / format) | **D5i-F3 — BLOCKING** |

### 3d. FALSE-POSITIVE direction of category stripping — clean

`_carries_secret(..., byte_view=False)` and `(..., byte_view=True)` both **False** for every one:
Vietnamese decomposed and precomposed, Hindi with matras (Mc + Mn), Arabic with harakat, Hebrew niqqud,
Thai, the family-emoji ZWJ sequence, VS16 emoji, plain Latin with `%`, the `a+b=c` plus token, the MARKER
record itself, a Mozilla UA string, `café`, and the full chat-body JSON. **No legitimate body 400s through
`strip_invis`.** The single space-stripping "false positive" (`"…tok en-…"` with a real U+0020) is
identical to the old `strip_ws` behaviour, i.e. not a regression.

## Item 4 — removed ops: subsumption differential, and the depth bound with 5 ops

Old ops read from the **parent commit's** source (`4b43284`, backend `:147-149`), not from memory:
`strip_ws = re.sub(r"\s+","",x)` · `strip_zwc = re.sub("[U+200B U+FEFF U+00AD U+2060]","",x)` ·
`strip_ctl = re.sub("[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f\\x7f-\\x9f]","",x)`.

**Per-character differential over the entire code-point space (0…0x10FFFF, 1 114 112 characters):**

| old op | characters it removed that `strip_invis` does NOT remove |
|---|---|
| `strip_ws` | **0** |
| `strip_zwc` | **0** |
| `strip_ctl` | **0** |

Subsumption is complete **on this interpreter's UCD**. (It is *not* version-stable — see D5i-F3; on UCD 14
`strip_invis` is 42 code points narrower than on UCD 15.1, and the three removed regex ops were
version-independent, so this round traded a fixed domain for a moving one.)

**Whole-closure differential, parent (7 ops) vs PIN (5 ops):** 3 096 directed vectors
(4 prefixes × 43 separators × 6 suffixes × 4 case-folds, deduplicated) + 25 000 random seeded vectors.

| comparison | violations |
|---|---|
| parent closure FINDS the token and PIN closure MISSES it | **0** (directed), **0** (random) |
| parent screens by ANY arm (found or bound-exceeded) and PIN serves | **0** (directed) |

**No detection regression from the op removal.**

**Depth pins with 5 ops** (in-process): `%25252540` → `found=False, saturated=True` → served
(`test_saturating_junk_is_served`); `TOKEN + "-%25252541"` → `saturated=False` → fail-closed/blanked
(`test_bound_exceeded_blanks_the_record`). `M_D4` (`range(4)`) and `M_D6` (`range(6)`) both die on those two
tests (reproduced). **No bound movement.**

## Item 5 — is the oracle strictly wider?

**Op sets side by side (read off the source, not the prose):**

| | ops | depth | extra |
|---|---|---|---|
| impl `_normal_forms` (`backend:193`, `:196`) | `unquote, unquote_plus, str.lower, utf8_redecode_lenient, strip_invis` | 5 | — |
| oracle `_absent_under_all_normalizations` (red `:126`, `:135`) | `unquote, unquote_plus, str.lower, utf8_redecode_lenient, strip_invis` | 6 | seeds with `json.loads` of every JSON string literal |

Identical op sets; the oracle is wider by one depth level and by the JSON seeding, exactly as the brief expects.

**Differential (violation = impl closure FINDS the token AND the oracle says absent):**

| corpus | violations |
|---|---|
| 3 096 directed | **0** |
| 25 000 random (seeded 11) | **0** |

**Every oracle op dropped alone goes red on a named vector** (full two-file scope, `ran` count verified > 0):

| oracle mutant | verdict | killer that actually fired |
|---|---|---|
| `O_INVIS` | KILLED | `test_oracle_known_vectors` — 16 of 21 vectors, incl. `[zwnj_split]` |
| `O2_UQ` | **SURVIVED** | equivalent *for this token*; reproduced non-equivalence: `TOKEN='a+b'`, `text='%61+%62'` → full oracle finds it, no-`unquote` oracle does not (3/3 `+`-bearing vectors diverge). Qualifier now in-tree at red `:113-114`. |
| `O5_LOWER` | KILLED | 1 vector (`[uppercased]`) |
| `O3_UQP` | KILLED | 2 vectors (`[plus_split]`, `[pct2b_split]`) |
| `O_UTF8_LENIENT` | KILLED | 2 vectors (`[raw_utf8_mojibake]`, `[raw_utf8_mojibake_junk]`) |

## Item 6 — the mutant table, re-run first-hand

Method: mutants applied by a Python patch script to **scratchpad copies only** (three isolated trees,
`vd12/mutA`, `vd12/mutB` and `vd12/mutC`, each with its own `git init` and pristine set). Pristine restore +
`git status --porcelain` on the three scope files asserted **empty after every mutant** (100% clean, every
row). The shared tree `/home/user/agent-factory` saw read-only git only. `ran=` (the number of tests that
actually executed) is recorded for every row — **a `-k` filter that matches nothing exits 0**, so a row
without a positive `ran` count would be a false green.

> **Discipline note, disclosed:** my first mutant batch pair shared one tree and raced. I discarded every
> result from that window and re-ran the whole campaign on isolated trees. The numbers below are from
> the clean re-run only.

### 6a. Reproduction of the report's KILLED rows — 26 spot-checked, **26/26 reproduce with the report's named killer**

| # | mutant | my verdict | tests run | killer that fired | report's killer | match |
|---|---|---|---|---|---|---|
| 2 | PRECHECK_ON_LEAVES | KILLED | 6 | `ordinary_latin1_text_in_json_body_is_served` ×6 | `[e_acute]` | yes |
| 3 | INVIS_DEL | KILLED | 8 | `invisible_separator_in_header_returns_400` ×8 | `[ZWNJ]` | yes |
| 4 | INVIS_LIST_ONLY | KILLED | 1 | `function_application_separator_in_header` | same | yes |
| 5 | LENIENT_DEL_IMPL | KILLED | 3 | `invalid_utf8_separator_in_json_body` ×2 (`overlong_pair`, `enquad_plus_junk`) | `[overlong_pair]` | yes |
| 7 | LENIENT_IN_IMPL | KILLED | 1 | `invalid_utf8_without_the_token_is_refused_not_repaired` | same | yes |
| 8 | JSONSAFE_INLINE_IN_RECORD | KILLED | 1 | `test_record_does_not_mutate_the_caller_body` | same | yes |
| 10 | PRECHECK_AFTER_CLOSURE | KILLED | 1 | `test_precheck_before_closure_on_invalid_utf8` | same | yes |
| 11 | M_SAT_IGNORE | KILLED | 1 | `test_bound_exceeded_blanks_the_record` | same | yes |
| 12 | M_SAT_INV | KILLED | 1 | `test_post_content_length_exactly_max_is_accepted` | same | yes |
| 13 | M_SEEN | KILLED | 1 | `plus_split_with_pct2520_suffix_returns_400` | same | yes |
| 14 | M_D4 | KILLED | 1 | `test_saturating_junk_is_served` | same | yes |
| 15 | M_D6 | KILLED | 1 | `test_bound_exceeded_blanks_the_record` | same | yes |
| 19 | M_LOWER_DEL | KILLED | 1 | `uppercased_token_in_header_returns_400` | same | yes |
| 20 | M_UQP_DEL | KILLED | 15 | `encoded_whitespace_split_returns_400` ×3 incl. `[header-PLUS]` | `[header-PLUS]` | yes |
| 21 | M_UQ_DEL | KILLED | 1 | `test_unquote_op_is_required_for_the_bound` | same | yes |
| 24 | M_HDRNAME | KILLED | 24 | `depth5_percent_nesting_returns_400` ×4 incl. `[header_name-d5_space]` | same | yes |
| 25 | M_HDRVAL | KILLED | 3 | `authorization_prefixed_header_name_is_not_exempt` ×3 | `[Authorization-X]` | yes |
| 26 | M_RAWBODY | KILLED | 1 | `duplicate_json_key_hiding_token_returns_400` | same | yes |
| 27 | M_PATH | KILLED | 15 | `encoded_whitespace_split_returns_400` ×5 incl. `[query-%20]` | `[query-%20]` | yes |
| 28 | M_JSONSTRINGS | KILLED | 5 | `whitespace_split_in_valid_json_body_returns_400` ×5 incl. `[TAB]` | `[TAB]` | yes |
| 31 | M_DEPTHGATE_OFF | KILLED | 1 | `json_depth_over_limit_returns_400_no_record` | same | yes |
| 32 | M_JSONSAFE_INPLACE | KILLED | 1 | `test_json_safe_copy_on_write` | same | yes |
| 33 | O_INVIS | KILLED | 21 | `test_oracle_known_vectors` 16/21 incl. `[zwnj_split]` | `[zwnj_split]` | yes |
| 35 | O5_LOWER | KILLED | 21 | `[uppercased]` | same | yes |
| 36 | O3_UQP | KILLED | 21 | `[plus_split]`, `[pct2b_split]` | `[plus_split]` | yes |
| 37 | O_UTF8_LENIENT | KILLED | 21 | `[raw_utf8_mojibake]`, `[raw_utf8_mojibake_junk]` | `[raw_utf8_mojibake]` | yes |
| 34 | O2_UQ | **SURVIVED** | 21 | — | SURVIVED (qualified) | yes |

### 6b. The two claimed equivalents and the re-attributed row

**`CTL_PARTIAL_noC1` — EQUIVALENT, and the lane's stated mechanism reproduces exactly.**
In-process BFS trace on the wire form of U+0080 (bytes `C2 80`, i.e. latin-1 `chr(0xC2)+chr(0x80)`):

```
depth 0  s0-01-upstream-tok<C2><80>en-...              (input)
depth 1  strip_invis(noC1)  -> ...tok<C2><80>en...     token NOT present (C1 kept by the mutant)
depth 1  lenient            -> ...tok<80>en...         token NOT present (C2 80 decodes to U+0080)
depth 2  lenient(lenient)   -> ...token-...            TOKEN PRESENT
HEAD strip_invis  : found at depth 2, saturated=True
noC1 strip_invis  : found at depth 2, saturated=True    -> behaviourally identical
```
So the C1 arm of `_INVIS_CATEGORIES` genuinely cannot be pinned while the lenient op is in the closure.
The docstring at `backend:177-181` records this. **Correct as reported.**

**`M_UTF8_DEL` — N/A confirmed.** `grep -n "utf8_redecode"` on the backend returns only
`utf8_redecode_lenient` (`:185`, `:193`) and the docstring mentions at `:51`, `:172-174`. The strict op is
genuinely absent. The "N/A" row is honest.

**`O2_UQ` — SURVIVED, equivalent only for this token.** Reproduced non-equivalence in-process with a
`+`-bearing token: `TOKEN='a+b'` with `text='%61+%62'`, `'%2561%2B%2562'`, and `TOKEN='x+y'` with
`'%78+%79'` — full oracle finds the token, the no-`unquote` oracle does not (3/3 diverge). The qualifier is
now durable in-tree at red `:113-114`. **Correct as reported, and D5h-F12 is closed.**

**`M_V12_CLOSE` — the coordinator's extra item. Ruling: GENUINE EQUIVALENT. Do NOT add a socket-level test.**

The lane reports it as *"defense-in-depth for a client that ignores the header; no test exercises that
scenario."* That mechanism is **wrong**, and I reproduced the exact scenario it names.

1. **Primary source.** `http.server.BaseHTTPRequestHandler.send_header` (CPython
   `/usr/lib/python3.11/http/server.py`, identical on 3.12.3 and 3.13.12):
   ```python
   if keyword.lower() == 'connection':
       if value.lower() == 'close':
           self.close_connection = True
   ```
   `_stream` sends `self.send_header("Connection", "close")` at `backend:601`, so the flag is **already
   True** long before `:619`.
2. **Runtime probe.** An instrumented copy printing the flag immediately before `:619`:
   `PROBE close_connection BEFORE line 619 = True`.
3. **Socket differential with a client that ignores the header** (the lane's own hypothesis): after
   `data: [DONE]`, the client pipelines a second full POST on the same socket.

   | build | outcome | data lines |
   |---|---|---|
   | HEAD (`:619` present) | `<socket closed, no 2nd response>` | 6 |
   | `M_V12_CLOSE` (`:619` deleted) | `<socket closed, no 2nd response>` | 6 |

**Therefore a socket-level killer cannot exist.** Writing one would produce a test that is green with and
without the mutation — a tautology, i.e. exactly the hollow green `anti-hollow-green` tactic 3 forbids. The
correct close-out is to record the equivalence and its mechanism in the tree (one comment at `:619`), or
delete the line as dead. The same argument applies verbatim to the other two redundant
`self.close_connection = True` statements at `:424` (after the `Connection: close` header at `:422`) and
`:493` (after `_send_json(..., extra={"Connection": "close"})`).

### 6c. The four mutants the brief told me to ADD — **2 KILLED, 2 SURVIVED**

| mutant | mutation | scope | verdict | killer / consequence |
|---|---|---|---|---|
| `BYTEVIEW_ALL_FALSE` | `:342` `if byte_view and …` → `if False and …` | red file (166) | **KILLED** | `invalid_utf8_without_the_token_is_refused_not_repaired`, `precheck_before_closure_on_invalid_utf8` (2 failed, 164 passed). Note only **2** tests die — every invalid-UTF-8 *separator* test still passes without the precheck, because the lenient op now finds the token anyway. |
| `BYTEVIEW_ALL_TRUE` | `:342` → `if True and …` | red file (166) | **KILLED** | all six `ordinary_latin1_text_in_json_body_is_served` params (6 failed, 160 passed) — café returns, as the brief predicted |
| `INVIS_NO_EXTRA` | drop `and c not in _INVISIBLE_EXTRA` | **full 500** | **SURVIVED (500 passed)** | **no vector dies. D5i-F4.** Non-equivalent: in the decoded sink U+2800, U+3164, U+FFA0, U+115F, U+1160 are all missed by the mutant and caught by HEAD |
| `INVIS_NO_CS` | drop `"Cs"` from `_INVIS_CATEGORIES` | **full 500** | **SURVIVED (500 passed)** | **no vector dies. D5i-F5.** Non-equivalent: lone surrogates U+D800 / U+DFFF via a JSON escape are missed by the mutant and caught by HEAD |
| `INVIS_NO_MN` | drop `"Mn"` | red file (166) | **KILLED** | `invisible_separator_in_json_body_returns_400[COMBINING_ACUTE]` |

### 6d. My own additional category-subset audit — every member of the class must die alone or be declared unpinned

Non-equivalence established in-process for **every** member first (decoded sink, named code points), then
the suite verdict. Red-file scope (166) first; every survivor escalated to the **full 500** on an isolated
tree.

| dropped member | HEAD catches / mutant misses (decoded sink) | suite verdict | killer that fired |
|---|---|---|---|
| `Cf` | U+200C, U+200E, U+2060 | **KILLED** (7 failed, 159 passed) | `zero_width_pct_encoded[ZWSP]`, `[BOM]`, `zero_width_json_escape`, `raw_utf8_zero_width_in_header[BOM]`, `invisible_separator_in_json_body[ZWNJ/ZWJ/LRM]` |
| `Cc` | U+0001, U+007F | **KILLED** (30 failed, 136 passed) | `whitespace_split_in_valid_json_body[TAB/LF/CR/FF/VT]`, … |
| `Mn` | U+0301, U+FE00, U+E0100, U+0651 | **KILLED** (1 failed, 499 passed on the full scope) | `invisible_separator_in_json_body[COMBINING_ACUTE]` |
| `Zs` | U+0020, U+3000, U+1680 | **KILLED** (25 failed, 141 passed) | `encoded_whitespace_split`, … |
| **`Cs`** | U+D800, U+DFFF (lone surrogate via a JSON escape) | **SURVIVED — `500 passed in 168.40s`** | none — **D5i-F5** |
| **`Me`** | U+20DD, U+0488 | **SURVIVED — `500 passed in 168.48s`** | none — **D5i-F16** |
| **`Zl` + `Zp`** | U+2028, U+2029 | **SURVIVED — `500 passed in 168.59s`** | none — **D5i-F16** |
| **`_INVISIBLE_EXTRA`** | U+2800, U+3164, U+FFA0, U+115F, U+1160 | **SURVIVED — `500 passed in 168.47s`** | none — **D5i-F4** |

`grep -n "2028\|2029\|20DD\|0488\|d800\|D800\|dfff\|DFFF"` over **both** test files returns **no
hit** — four members of the nine-member class have no vector anywhere in the suite.

**Oracle-side asymmetry** (mutating the oracle's copy of the same predicate, `test_oracle_known_vectors`,
`ran=21` both):

| oracle mutant | verdict | killer |
|---|---|---|
| `O_INVIS_EXTRA` (drop `_INVISIBLE_EXTRA` from the oracle) | **KILLED** | `[braille_split]`, `[hangul_filler_split]` |
| `O_INVIS_NOCS` (drop `Cs` from the oracle) | **SURVIVED** | none — `Cs` is unpinned on **both** sides |

So the oracle self-tests at red `:436-437` pin the extras **in the oracle** while the impl's copy of the
same set is free — the two mirrors are not equally guarded, and a reader who sees `[braille_split]` green
may reasonably think the impl is pinned. It is not.

### 6e. My own mutant for the record-delta class (item 7)

`RECORDLESS_400_XTRACE` — `_framing_gate` rejects any request carrying an `X-Trace` header with `400` and
**writes no record** (the D5h-F11 class, generalised from the header-name arm).

```
MUTANT=RECORDLESS_400_XTRACE  rc=1 :: 4 failed, 13 passed, 149 deselected
    FAILED  invalid_utf8_separator_in_header[enquad_plus_junk]      <- HAS the new delta
    FAILED  invalid_utf8_separator_in_header[nbsp_plus_junk]        <- HAS the new delta
    FAILED  invalid_utf8_separator_in_header[overlong_space]        <- HAS the new delta
    FAILED  invalid_utf8_separator_in_header[lone_continuation]     <- HAS the new delta
    PASSED  plus_split_with_pct2520_suffix_returns_400              <- NO delta  (red :641)
    PASSED  raw_utf8_zero_width_in_header_returns_400 x6            <- NO delta  (red :662)
    PASSED  unquote_op_is_required_for_the_bound                    <- NO delta  (red :785)
```
Eight test cases assert `[-1]["body"] == MARKER` while the server wrote **no record for their request**.
See **D5i-F6**.

## Findings — all of them, no severity filtering

### D5i-F1 — BLOCKING — SOLID — D5h-F1 survives at a second `byte_view=True` call site: a top-level JSON string body

- **file:line** `proofs/S0-01/tools/scripted_backend.py:374-375`
  ```python
  body_str = body if isinstance(body, str) else json.dumps(body)
  if self._carries_secret(body_str, byte_view=True):
  ```
  reaching `_has_invalid_utf8_bytes` at `:342` → `:134`.
- **concrete failing input** (live, own subprocess backend, PIN bytes, load 2.4):
  `POST /v1/chat/completions` with `Content-Type: application/json` and the body being the **valid JSON
  document** `"caf\u00e9"` — **pure ASCII on the wire, no credential anywhere**:
  → **`HTTP/1.1 400 Bad Request`**, record body = `{"credential_in_unexpected_location": true}`.
  Same for the raw-UTF-8 form of the same document, and for `"Müller"`.
  Paired negative controls on the identical sink: `"hello"` → `400` with the record **verbatim**
  (`"hello"`) and the ordinary route message; `"世界"` (not latin-1-encodable) → `400`, record verbatim;
  the *same* `café` inside a JSON object leaf → **`200 OK`, record verbatim**.
- **observed vs expected:** observed a false credential-leak verdict — a blanked record and the
  "credential in unexpected location" error — on a request that carries no credential and (for the
  `é`-escaped form) not one non-ASCII byte on the wire. Expected the ordinary route rejection with
  the record written verbatim, exactly as `"hello"` gets.
- **mechanism (re-derived):** `_read_body` returns `json.loads(raw.decode())`. For a top-level JSON string
  document that return value **is a `str`**, so `body_str = body` — a string `json.loads` has already
  decoded. `:375` then declares it a byte view. `"café"` decodes to `café`; `café.encode("latin-1")`
  is `b'caf\xe9'`, which is not valid UTF-8, so the precheck fails closed. The guard at `:381`
  (`not isinstance(body, str)`) correctly skips the leaf walk for this case but the *earlier*
  `body_str` line is unguarded. The `_carries_secret` docstring's enumeration of byte-view sinks
  ("header names, header values, path/query, the raw body") omits `body_str` entirely.
- **minimal fix:** decide the flag from what the string is, not from where the loop sits:
  ```python
  body_str = body if isinstance(body, str) else json.dumps(body)
  #  a parsed body that is already a str is DECODED, not a byte view
  if self._carries_secret(body_str, byte_view=not isinstance(body, str)):
  ```
  (`json.dumps` output is ASCII, so `byte_view=True` on that branch is harmless but also useless —
  `byte_view=False` there is equally correct and simpler.)
- **exact red test to add** (RED today — returns 400 + MARKER):
  ```python
  @pytest.mark.parametrize("doc", [b'"caf\\u00e9"', b'"M\\u00fcller"', b'"\\u00a3100"'],
                           ids=["e_acute", "u_uml", "pound"])
  def test_top_level_json_string_body_is_not_a_byte_view(backend, doc):
      """A top-level JSON string is DECODED by json.loads; the precheck must not
      re-encode it. Pure ASCII on the wire, no credential -> ordinary route 400,
      record verbatim, NOT the credential MARKER."""
      port = backend["port"]
      n0 = len(_records(backend))
      resp = _raw(port, _post(port, doc))
      assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
      recs = _records(backend)
      assert len(recs) == n0 + 1
      assert json.loads(recs[-1].read_text())["body"] != MARKER
  ```
  Control (green today and after the fix): the same test with `doc = b'"hello"'`.

### D5i-F2 — BLOCKING — SOLID — a percent-encoded invalid UTF-8 byte splits the token on all 7 sinks; the record keeps it and the token is recovered by one line

- **file:line** `proofs/S0-01/tools/scripted_backend.py:193` (`ops` — `unquote`/`unquote_plus` run with
  CPython's default `errors="replace"`), and `:176-184` (`strip_invis` does not remove U+FFFD, category
  `So`). Mirrored **identically** in the oracle at red `:126` / `:117-119`, **so no test in the suite can
  see this class** — the impl and the oracle share the blind spot exactly as in verify-D5g-F1 / D5h-F2.
- **concrete failing input** (live, own subprocess backend, PIN bytes, 35 cells):
  `X-Trace: s0-01-upstream-tok%80en-0123456789abcdef` → **`HTTP/1.1 200 OK`, no `Connection: close`**,
  record `x-trace = "s0-01-upstream-tok%80en-0123456789abcdef"`, and
  `urllib.parse.unquote(value, errors="ignore")` **returns the token exactly**.
- **7 sinks × 5 separators, all leak** (`%80`, `%C0`, `%FF`, `%ED%A0%80`, `%E2%80`):

  | sink | status | record blanked | token recovered from the record |
  |---|---|---|---|
  | header_value / header_name / query / json_value / json_key / json_list | `200 OK` | no | **yes** (5/5 separators each) |
  | path | `404 Not Found` (route) | no | **yes** — the path is recorded verbatim |

  **Paired negative control on the identical sinks:** `%20` → `400 Bad Request` + MARKER + close on
  **7/7**. `%00` and `%7F` and `%E2%80%8B` (ZWSP) also 400. `%80` — the very next byte value — is open.
- **in-process confirmation** (`_carries_secret` on the PIN's module):
  `%80`, `%C0`, `%FF`, `%FE%FF`, `%ED%A0%80`, `%C3`, `%E2%80`, `%81%82` → **False for both
  `byte_view=True` and `byte_view=False`**, and the oracle says `absent=True` for all eight.
- **mechanism (re-derived from primary source):** `urllib.parse.unquote(string, encoding='utf-8',
  errors='replace')` — the default `errors` is `'replace'`, so `%80` becomes **U+FFFD REPLACEMENT
  CHARACTER**, whose category is `So`, which is deliberately *not* in `_INVIS_CATEGORIES` (it is a visible
  glyph). The closure's whole form set for the vector is only two strings:
  `{'…tok%80en…', '…tok�en…'}` — saturated, token in neither. The invalid-UTF-8 precheck cannot
  help: the wire bytes are pure ASCII (`%`, `8`, `0`). This is the same defect *class* as D5h-F2, reached
  through percent-encoding instead of a raw code point.
- **minimal fix:** add the ignoring decode to the closure and the oracle, so the byte the client hid is
  dropped rather than replaced by a surviving glyph:
  ```python
  def unquote_ignore(x):
      return unquote(x, errors="ignore")
  ops = (unquote, unquote_plus, str.lower, utf8_redecode_lenient, strip_invis, unquote_ignore)
  ```
  (Alternatively add U+FFFD to `_INVISIBLE_EXTRA`; that closes the reported vectors but not
  `%C3` followed by a legitimate continuation, so the ignoring decode is the wider fix. Whichever is
  chosen must go into **both** the impl `ops` and the oracle `ops`, and the depth pins
  `test_saturating_junk_is_served` / `test_bound_exceeded_blanks_the_record` must be re-checked, since a
  sixth op changes the branching factor.)
- **exact red test to add** (RED today — returns 200 OK):
  ```python
  @pytest.mark.parametrize("sep", ["%80", "%C0", "%FF", "%ED%A0%80"],
                           ids=["lone_cont", "overlong_lead", "ff", "surrogate"])
  def test_credential_pct_encoded_invalid_utf8_separator_returns_400(backend, sep):
      """unquote() defaults to errors='replace', so a percent-encoded invalid byte
      becomes U+FFFD (So) and survives strip_invis. The record then holds the token
      under unquote(..., errors='ignore')."""
      port = backend["port"]; mid = len(TOKEN) // 2
      split = TOKEN[:mid] + sep + TOKEN[mid:]
      body = b'{"model":"s0-01-pong","messages":[]}'
      n0 = len(_records(backend))
      resp = _raw(port, _post(port, body, extra_headers=f"X-Trace: {split}\r\n"))
      assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
      recs = _records(backend)
      assert len(recs) == n0 + 1
      assert json.loads(recs[-1].read_text())["body"] == MARKER
  ```
  plus the oracle self-test vector `(TOKEN[:mid] + "%80" + TOKEN[mid:], False)` with id
  `pct_lone_continuation_split`, which is RED against the current oracle.

### D5i-F3 — BLOCKING — SOLID — the invisible class is defined by a table that differs per interpreter; 42 code points leak on Python 3.11, the interpreter the whole gate runs on

- **file:line** `proofs/S0-01/tools/scripted_backend.py:183` (`unicodedata.category(c)`), red `:119`.
- **measurement:** enumerating the full code-point space under each interpreter, the membership of
  `{Cf,Cs,Cc,Mn,Me,Zs,Zl,Zp} ∪ _INVISIBLE_EXTRA` is

  | interpreter | `unicodedata.unidata_version` | members |
  |---|---|---|
  | python3.11.15 (**= `python3`, the one pytest runs under**) | 14.0.0 | **4263** |
  | python3.12.3 | 15.0.0 | 4305 |
  | python3.13.12 | 15.1.0 | 4305 |

  **42 code points are stripped on 3.12/3.13 and not on 3.11**; 0 in the other direction. They are the
  Unicode 15.0 `Mn`/`Cf` additions: U+0ECE, U+10EFD–U+10EFF, U+11241, U+11F00, U+11F01, U+11F36–U+11F3A,
  U+11F40, U+11F42, U+13439–U+13455, U+1E08F, U+1E4EC–U+1E4EF, …
- **concrete failing input** (live, decoded sink = a JSON `\u`-escape, own backend, PIN bytes):
  body `{"model":"s0-01-pong","messages":[],"t":"<TOKEN[:19]>𐻽<TOKEN[19:]>"}` (U+10EFD ARABIC
  SMALL LOW WORD SAKTA, a nonspacing mark)

  | interpreter | status | record |
  |---|---|---|
  | **python3.11 (UCD 14.0)** | **`200 OK`** | `t = 's0-01-upstream-tok\U00010efden-0123456789abcdef'` — **written verbatim** |
  | python3.12 (UCD 15.0) | `400 Bad Request` | MARKER |
  | python3.13 (UCD 15.1) | `400 Bad Request` | MARKER |

  Identical split for U+1E08F, U+11F36, U+13439, U+0ECE. **Token recovery from the 3.11 record**, using the
  module's own transform run on a current table: `"".join(c for c in v if unicodedata.category(c) not in
  _INVIS_CATEGORIES)` under UCD 15.1 → `token_recovered = True` for **5/5**.
  Paired negative control on the same sink and interpreter: U+200C ZWNJ, U+FE00 VS1, U+0301 →
  `400` + MARKER on all three interpreters.
- **observed vs expected:** the round's contract is "the invisible-separator class, closed by category".
  What is actually closed is "the invisible-separator class **as the runtime's bundled UCD happened to
  define it when the process started**". The sandbox gate (500 tests, 3.11) therefore proves the narrower
  domain; the PC gate proves whichever domain the PC's interpreter carries; and the fixture's own docstring
  says it "runs on the PC by absolute path", so the two venues are not proving the same predicate.
  This also falsifies the D5h verdict's line *"The precheck and `strip_ctl` are interpreter-independent"*
  for the op that replaced `strip_ctl`.
- **note on the header sink:** the header sink does **not** leak these, because the wire form arrives as
  latin-1 bytes and `strip_invis` removes the `C1`/`Zs` bytes inside the UTF-8 sequence, after which the
  lenient decode drops the remainder. The gap is confined to sinks that hand over a **decoded** string —
  the parsed-JSON leaf walk. That is why a header-only probe (the report's) cannot see it.
- **minimal fix (two options, both cheap):**
  1. **Pin the table.** Replace the live category lookup with a frozenset built once from an explicit
     range list committed in the file, so the domain is a property of the repo, not of the runtime; or
  2. **Assert the floor.** Add a module-level guard, e.g.
     ```python
     _MIN_UNIDATA = (15, 1)
     if tuple(int(p) for p in unicodedata.unidata_version.split(".")[:2]) < _MIN_UNIDATA:
         raise SystemExit(f"scripted_backend: unicodedata {unicodedata.unidata_version} is older than "
                          f"{'.'.join(map(str,_MIN_UNIDATA))}; the invisible-separator class would be "
                          f"narrower than the contract")
     ```
     which fails **loud** on 3.11 instead of silently narrowing a security screen.
  Either way the choice must be stated in the module docstring, which currently claims the class without
  qualification.
- **exact red test to add** (RED today on python3.11):
  ```python
  def test_invisible_class_does_not_depend_on_the_runtime_unicode_table():
      """The screen's domain must be a property of the repo, not of the interpreter's
      bundled UCD. RED on python3.11 (UCD 14.0): U+10EFD is Mn in 15.0, Cn in 14.0."""
      sb = _load_backend_module()
      st = sb.State(TOKEN, pathlib.Path("/dev/null"), 0.0)
      mid = len(TOKEN) // 2
      for cp in (0x10EFD, 0x1E08F, 0x11F36, 0x13439, 0x0ECE):
          assert st._carries_secret(TOKEN[:mid] + chr(cp) + TOKEN[mid:], byte_view=False), \
              f"U+{cp:04X} splits the token and is served on unicodedata {unicodedata.unidata_version}"
  ```
  plus the live twin through a JSON escape, and the same five as oracle self-test vectors.

### D5i-F4 — SOLID — `_INVISIBLE_EXTRA` is entirely unpinned: dropping it passes all 500 tests

- **file:line** `proofs/S0-01/tools/scripted_backend.py:120-124` and `:184`; oracle red `:94-99`, `:120`.
- **proof:** mutant `INVIS_NO_EXTRA` (delete `and c not in _INVISIBLE_EXTRA` from `strip_invis`) →
  **`500 passed in 168.47s`** on an isolated tree, scope clean after restore.
- **non-equivalent:** in the decoded sink, HEAD catches and the mutant misses **U+2800 BRAILLE BLANK,
  U+3164 HANGUL FILLER, U+FFA0 HALFWIDTH HANGUL FILLER, U+115F and U+1160 HANGUL JAMO FILLERS**
  (U+180E is `Cf` on this UCD, so it is covered by the category arm regardless). All five are
  zero-width-or-blank renderers and all five were on D5h-F2's served list.
- **why the existing tests miss it:** the eight-code-point header test
  (`test_credential_invisible_separator_in_header_returns_400`, red `:834/:836`) *does* include
  BRAILLE_BLANK, HANGUL_FILLER and MVS — but on the **header** sink the separator arrives as UTF-8 wire
  bytes, whose latin-1 view contains a `Cc` or `Zs` byte that `strip_invis`'s **category** arm removes;
  the lenient decode then reconnects the halves. The extras never have to fire. The JSON-escape twin
  (red `:858/:862`) — the only decoded sink — covers ZWNJ/ZWJ/LRM/COMBINING_ACUTE, none of them extras.
- **minimal fix / exact red test to add** (green today, RED under `INVIS_NO_EXTRA`): extend the JSON-escape
  parametrisation at red `:858` with the five extras:
  ```python
  @pytest.mark.parametrize("cp,cp_id", [
      (0x200C, "ZWNJ"), (0x200D, "ZWJ"), (0x200E, "LRM"), (0x0301, "COMBINING_ACUTE"),
      (0x2800, "BRAILLE_BLANK"), (0x3164, "HANGUL_FILLER"), (0xFFA0, "HALFWIDTH_FILLER"),
      (0x115F, "CHOSEONG_FILLER"), (0x1160, "JUNGSEONG_FILLER"),
  ], ids=["ZWNJ", "ZWJ", "LRM", "COMBINING_ACUTE", "BRAILLE_BLANK", "HANGUL_FILLER",
          "HALFWIDTH_FILLER", "CHOSEONG_FILLER", "JUNGSEONG_FILLER"])
  ```
  and add the matching oracle self-test vectors so `O_INVIS_EXTRA` also dies.

### D5i-F5 — SOLID — the `Cs` member of `_INVIS_CATEGORIES` is unpinned on BOTH sides: dropping it passes all 500 tests

- **file:line** `proofs/S0-01/tools/scripted_backend.py:125`; oracle red `:93`.
- **proof:** mutant `INVIS_NO_CS` → **`500 passed in 168.40s`** on an isolated tree, scope clean. The
  oracle-side twin `O_INVIS_NOCS` also **SURVIVED** (`21 passed` on `test_oracle_known_vectors`), so
  neither mirror pins `Cs`.
- **non-equivalent:** HEAD catches and the mutant misses the lone surrogates **U+D800** and **U+DFFF**
  reached through an ordinary JSON `\ud800` escape — a vector D5h-F2 listed explicitly and the D5i brief
  named ("including the lone surrogate `\ud800` escape").
- **minimal fix / exact red test to add** (green today, RED under `INVIS_NO_CS`):
  ```python
  def test_credential_lone_surrogate_separator_in_json_body_returns_400(backend):
      """A lone surrogate escape (category Cs) splitting the token must be caught."""
      port = backend["port"]; mid = len(TOKEN) // 2
      body = (b'{"model":"s0-01-pong","messages":[],"t":"'
              + TOKEN[:mid].encode() + b'\\ud800' + TOKEN[mid:].encode() + b'"}')
      n0 = len(_records(backend))
      resp = _raw(port, _post(port, body))
      assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
      recs = _records(backend)
      assert len(recs) == n0 + 1
      assert json.loads(recs[-1].read_text())["body"] == MARKER
  ```
  plus the oracle vector `(TOKEN[:mid] + "\ud800" + TOKEN[mid:], False)`, id `lone_surrogate_split`.


### D5i-F16 — SOLID — two more members of the class are unpinned: `Me`, and `Zl`+`Zp`

- **file:line** `proofs/S0-01/tools/scripted_backend.py:125`; oracle red `:93`.
- **proof:** `INVIS_NO_ME` → **`500 passed in 168.48s`**; `INVIS_NO_ZLZP` → **`500 passed in 168.59s`**.
  Both on isolated trees, scope clean after restore.
- **non-equivalent:** `Me` — HEAD catches and the mutant misses U+20DD COMBINING ENCLOSING CIRCLE and
  U+0488 COMBINING CYRILLIC HUNDRED THOUSANDS SIGN. `Zl`/`Zp` — U+2028 LINE SEPARATOR and U+2029
  PARAGRAPH SEPARATOR, which the D5h verdict recorded as *"caught (Python `\s`)"* under the now-deleted
  `strip_ws`; this round moved them into the `Zl`/`Zp` members and no test followed them there.
- **observed vs expected:** counting `Cs`, `Me`, `Zl`, `Zp` and `_INVISIBLE_EXTRA`, **five of the nine
  members of the class predicate have no killing vector**, and `grep` confirms none of their code points
  appears anywhere in either test file. The lane's own design rule (brief item 3) says an op member that
  cannot be pinned must be removed rather than kept; these members must instead be **pinned**, because all
  five are non-equivalent.
- **exact red tests to add** (green today, RED under the respective mutants) — extend the JSON-escape
  parametrisation at red `:858`:
  ```python
  (0x2028, "LINE_SEPARATOR"), (0x2029, "PARAGRAPH_SEPARATOR"),
  (0x20DD, "ENCLOSING_CIRCLE"), (0x0488, "CYRILLIC_ENCLOSING"),
  ```
  and add the four matching oracle self-test vectors so the oracle mirrors are pinned too.

### D5i-F6 — SOLID — D5h-F11 was fixed in the three named tests, not in the class: eight cases still assert off a stale `[-1]`

- **file:line** `tests/red/test_s0_01_backend_credential_screen.py:641`
  (`test_credential_plus_split_with_pct2520_suffix_returns_400`), **`:662`**
  (`test_credential_raw_utf8_zero_width_in_header_returns_400`, 6 params), **`:785`**
  (`test_unquote_op_is_required_for_the_bound`) — each reads
  `json.loads(_records(backend)[-1].read_text())["body"] == MARKER` with **no `n0` delta**.
- **proof:** mutant `RECORDLESS_400_XTRACE` (any `X-Trace`-bearing request rejected in `_framing_gate`
  with `400` and **no record**): the four `invalid_utf8_separator_in_header` cases that received the delta
  this round **FAIL**; those eight cases **PASS** on a record they did not cause
  (`4 failed, 13 passed`).
- **observed vs expected:** the assertion claims "the record was blanked"; it is satisfied by an earlier
  test's MARKER. Same defect the round fixed three doors down.
- **minimal fix / exact red test:** the two-line delta already used at red `:705/:709`, applied to those
  three tests:
  ```python
  n0 = len(_records(backend))
  ...
  recs = _records(backend)
  assert len(recs) == n0 + 1
  assert json.loads(recs[-1].read_text())["body"] == MARKER
  ```

### D5i-F7 — SOLID — the `M_V12_CLOSE` row states a mechanism that does not hold; the mutant is a genuine equivalent

- **file:line** report `tasks/briefs/s0-01-d5i-support/D5i-report.md`, mutant row 30 and NOT_DONE #3:
  *"defense-in-depth for a client that ignores the header. No existing test exercises the server-side
  socket-closure behavior after streaming."*
- **proof:** three independent lines, all above in item 6b — CPython `send_header` sets
  `close_connection = True` on `Connection: close` (primary source, identical on 3.11/3.12/3.13); a runtime
  probe shows the flag is already `True` immediately before `backend:619`; and a socket-level client that
  ignores the header and pipelines a second request gets the identical result with and without `:619`.
- **observed vs expected:** observed a survivor filed as "untested behaviour"; it is untestable behaviour.
  The distinction matters because "no test exercises it" invites the next round to write one — which
  would be green either way.
- **minimal fix:** replace the line with a comment recording the equivalence, or delete it:
  ```python
  # send_header("Connection", "close") at :601 already sets close_connection (CPython
  # http.server); this statement is redundant and cannot be pinned by any test.
  ```
  and correct the mutant row to `EQUIVALENT (redundant with send_header)`. The same applies to `:424`
  and `:493`.
- **exact red test to add:** **none — deliberately.** Writing a socket-level test here would be a
  tautology (green with and without the mutation), the exact hollow green `anti-hollow-green` tactic 3
  forbids. I ran the candidate killer and it does not discriminate; that is the answer to the
  coordinator's question.

### D5i-F8 — SOLID — the report's `file:line` column is wrong again, with a systematic +2 offset on every `record()` call site (D5h-F6 NOT closed)

- **file:line** `D5i-report.md`, DONE table and MUTANT table.
- **proof** (all re-derived with `grep -n` on the tree whose sha256 the report itself publishes):

  | report claim | true line | what actually sits at the claimed line |
  |---|---|---|
  | `:327` `def _carries_secret` | **:325** | the third line of its docstring |
  | `:345` precheck guard | **:342** | `forms, saturated = _normal_forms(s)` |
  | `:369` path `byte_view=True` | **:367** | `leaked = True` |
  | `:373` header `byte_view=True` | **:371** | `leaked = True` |
  | `:377` `body_str` `byte_view=True` | **:375** | `# F1: json.dumps re-escapes …` |
  | `:385` leaf `byte_view=False` | **:383** | `leaked = True` |
  | `:388` raw-body `byte_view=True` | **:386** | `leaked = True` |
  | `:328-346` `_carries_secret` docstring | **:326-341** | the range runs 5 lines into executable code |
  | `:600` `send_header("Connection","close")` in `_stream` | **:601** | `send_header("Cache-Control", …)` |
  | decorator `:810` for the café test | **:812** | a `# ---- D5i-F1 …` comment |
  | decorator `:856` for the JSON twin | **:858** | a `# ---- D5i-F2 …` comment |
  | correct: `:120-125`, `:176-184`, `:193`, `:619`, red `:93`, `:113-114`, `:117-119`, `:126`, decorator `:834` / def `:836`, def `:880`, decorator `:901` / def `:902`, def `:924`, def `:944`, main `:2019` | | |

  **11 of ~22 spot-checks wrong.** Every one of the `State.record` call-site rows is off by exactly +2,
  which is the signature of lines derived from a draft and never re-grepped.
- **minimal fix:** re-derive each ref with `grep -n` against the final tree *after* the last edit, and
  cite the decorator line (not the comment above it) for a parametrized test.

### D5i-F9 — SOLID — stale prose the diff falsified: the oracle docstring still describes the strict re-decode this round deleted

- **file:line** `tests/red/test_s0_01_backend_credential_screen.py:104-105` — *"up to depth 6 (the backend
  uses depth 5 with the same operators **plus utf8_redecode strict**; this oracle goes one depth level
  further)"* — and `:111-112` — *"utf8_redecode_lenient: … **strictly wider than the impl's strict
  utf8_redecode**."* The impl has had no strict decode since this round removed it (`grep -n
  "utf8_redecode"` on the backend returns only `utf8_redecode_lenient`).
- **also stale:** red `:652`, the docstring of `test_credential_raw_utf8_zero_width_in_header_returns_400`
  — *"…that neither **strip_ws** nor **strip_zwc** touches without utf8_redecode"* — names two ops this
  round deleted and one that no longer exists under that name.
- **observed vs expected:** a reader of the oracle's own contract is told the impl has an op it does not
  have, and is told the oracle is wider on an axis where the two are now identical. The oracle's real
  claim to be wider rests on depth 6 vs 5 and the JSON seeding.
- **minimal fix:** `:104-105` → *"up to depth 6; the backend uses the same five operators at depth 5"*;
  `:111-112` → drop the "strictly wider than the impl's strict utf8_redecode" clause; `:652` →
  *"…that strip_invis does not touch until utf8_redecode_lenient has recovered the real code point"*.
- **exact red test:** none needed — this is prose; the check is `grep -n "strict\|strip_ws\|strip_zwc"
  tests/red/test_s0_01_backend_credential_screen.py` returning no live claim.

### D5i-F10 — SOLID — the restated precheck docstring enumerates four byte-view sinks; there are five

- **file:line** `proofs/S0-01/tools/scripted_backend.py:138-139` (*"Called ONLY on byte-view sinks
  (headers, path/query, raw body)"*) and `:331-333` (*"`byte_view` is True for strings `http.server` hands
  over as a latin-1 view of wire bytes (header names, header values, path/query, the raw body)"*), plus
  the module docstring at `:54-56`.
- **proof:** `grep -n "byte_view=True"` returns **four** call sites — `:367`, `:371`, `:375`, `:386` — and
  `:375` is `body_str`, which is not in either enumeration and is not a byte view for a `str` body
  (D5i-F1).
- **minimal fix:** land the D5i-F1 fix and then the enumeration becomes true; if the behaviour is kept
  deliberately, the docstring must name `body_str` and list "a top-level JSON string document" as an
  accepted false-positive next to the D5d-F12 paragraph, with a test that pins it.
- Same class as D5h-F13 — a docstring premise that the code falsifies.

### D5i-F11 — UNSURE (on the "invisible" criterion) / SOLID (on the mechanism) — unassigned code points are outside the class on every interpreter

- **file:line** `proofs/S0-01/tools/scripted_backend.py:183`.
- **observation:** `U+2065` — the reserved slot inside the U+2060…U+2064 invisible-operator run, whose
  four assigned neighbours are all `Cf` and all caught — has category `Cn` on 3.11, 3.12 and 3.13, is not
  in `_INVISIBLE_EXTRA`, and **splits the token in a JSON body and is served `200 OK` with the record
  verbatim on all three interpreters** (reproduced live).
- **UNSURE on:** whether U+2065 "renders invisible or zero-width" — an unassigned code point is normally
  drawn as `.notdef` (a box), so it is arguably visible. I report it because the mechanism is the same one
  D5i-F3 exposes: `Cn` today can become `Cf`/`Mn` tomorrow, at which point the screen's behaviour changes
  without any code change. The same is true of `U+1CBB` and every other reserved slot.
- **minimal fix:** covered by D5i-F3's option 1 (pin the table in-repo). If the coordinator prefers the
  live table, add `Cn` to `_INVIS_CATEGORIES` only after checking the false-positive direction — `Cn` is a
  very large class (about 800 000 code points) and stripping all of it changes the closure's cost.
- **exact red test (only if the coordinator rules U+2065 in-class):** the JSON-escape twin with
  `cp = 0x2065`, id `RESERVED_INVISIBLE_OPERATOR`.

### D5i-F12 — SOLID (minor) — the report's PIN is the brief commit again, three commits back, and "CHILD" is wrong (D5h-F7 not closed)

- **file:line** `D5i-report.md` line 3: ``PIN: `618749fafdc9032696729b53e8c176859e3891a8` (HEAD at
  dispatch). Work lands in the CHILD commit.``
- **proof:** `git cat-file -e 618749f` rc 0; `git log --oneline -1 618749f` → *"S0-01 backend round 12
  brief (D5i) + the VERIFY-D5h verdict, before dispatch"*. `git rev-list --count 618749f..c4805df` = **3**;
  the first-parent chain is `618749f → 9b2803c (lane A5h) → 4b43284 (lane B5f) → c4805df (this lane)`.
  Checking out the named PIN yields the **pre-D5i** implementation.
- The lane did add the brief's required "work lands in the CHILD commit" sentence, so the intent is there;
  the commit named is the great-grandparent and the word "CHILD" is false.
- **minimal fix:** name the checkpoint the coordinator actually made (`c4805df`), or write "PIN = the HEAD
  at dispatch, `618749f`; this lane's work is checkpoint `c4805df`, three commits later".

### D5i-F13 — SOLID — the cost table's third column still does not measure the expensive arm; the "no cell exceeds 1 s" claim is false for the arm it omits

- **file:line** `D5i-report.md`, "Cost table (min of 5 per cell, own subprocess backend, load 0.49)".
- **proof:** the report's own note explains why all three of its columns converge — *"the invalid-UTF-8 and
  bound-exceeded paths short-circuit the credential check **in the header**"* — i.e. its bound-exceeded
  vector is `%25252541` in `X-Trace`, so the 1 MB body never goes through the un-saturating closure. Put
  the bound-exceeding token **in the body** and the arm appears. My measurement (min of 5, own subprocess
  backend, **load 1.74 → 2.17**, with another lane's suite on the box):

  | body KB | ordinary (s) | invalid-UTF-8 in header (s) | bound-exceeded in header (s) | **bound-exceeded IN BODY (s)** |
  |---|---|---|---|---|
  | 1 | 0.002 | 0.001 | 0.001 | 0.003 |
  | 10 | 0.007 | 0.006 | 0.006 | 0.022 |
  | 100 | 0.064 | 0.053 | 0.053 | 0.223 |
  | 1000 | 0.657 | 0.530 | 0.518 | **2.105** |

  statuses 200 / 400 / 400 / 400 in every row. **Repeated on a quiet box (load 0.83 → 0.94, nothing else
  running), the numbers are unchanged:** 0.002 / 0.001 / 0.002 / 0.003 at 1 KB and
  **0.630 / 0.516 / 0.538 / 2.161** at 1000 KB. So the gap to the report is **not load**.
- **secondary finding — the cost table is still not reproducible (D5h-F8's own complaint, third round
  running).** At a load *lower* than the report's stated 0.49 I measure **0.630 s** for the ordinary
  1000 KB cell against the report's **0.164 s**, a 3.8× gap that neither load nor run-to-run variance
  explains (my two runs agree to 4%). verify-D5h measured 0.227 s and verify-D5g 0.197 s on the same box,
  so the historical range is 0.16–0.23 s and mine is an outlier in the other direction — most likely a
  harness difference (I count connect + full send + full read per request; the report does not say what it
  counts). I could not identify it, so I report the non-reproduction rather than adjudicating it. The
  *shape* — all three published columns converging — reproduces exactly.
- The fourth column is the substantive finding: **3.2–3.4× ordinary and 2.1 s at the 1 MB
  `MAX_CONTENT_LENGTH` ceiling**, against the report's flat *"No cell exceeds 1 s."*
- **not a hang:** the cost is bounded by `MAX_CONTENT_LENGTH` (1 MiB) and the handler's `timeout = 30`;
  `ThreadingHTTPServer` means one slow request does not block others. So this is a reporting defect and a
  documented cost, not a DoS.
- **minimal fix:** publish the fourth column (vector: `content` = 1 MB padding + `-%25252541`), state the
  load actually measured, and drop or qualify the "no cell exceeds 1 s" claim.

### D5i-F14 — INFORMATIONAL — SOLID — `M_UTF8_PRECHECK_DEL` and `LENIENT_IN_IMPL` are the same mutation counted twice

- **file:line** `D5i-report.md` mutant rows 7 and 22 — both are *"`:345` precheck deleted"*, and the
  report's own summary says *"2 effectively-identical"*. The table's headline "37 mutants. 30 KILLED"
  therefore counts 36 distinct mutations, one of which (`M_UTF8_DEL`) is N/A and one of which (`NOOP`) is
  not a mutation. The honest count is **34 real mutants, 29 distinct KILLED**.
- **minimal fix:** merge the two rows, or give one of them a genuinely different mutation (e.g. the
  precheck kept but inverted only on the raw-body site).

### D5i-F15 — INFORMATIONAL — SOLID — the report's live-control section does not state the redaction count the brief asked for

- **file:line** `D5i-report.md`, PROBE TABLES. The brief's gate list requires *"the live normal-traffic +
  streaming control after ≥ 50 redactions"*; the report's probe tables give separator counts (23 tests)
  and the legitimate-traffic table but never state how many MARKER records existed before the control.
- **I ran it:** 60 redaction records written (60/60 requests → 400), then `GET /v1/models` → `200 OK`
  with `path='/v1/models'` and `authorization_fingerprint` set; `POST /v1/chat/completions` → `200 OK`,
  `reply='pong'`, record verbatim; streaming leg (`s0-01-slow`) → `200 OK`, 6 `data:` lines, `[DONE]`
  present; **60 MARKER records still on disk, none overwritten**. The substance holds.

## Item 7 — record-count deltas and `RECORDLESS_400_HDR`

`grep -n "_records(backend)\[-1\]"` on the red file returns **four** sites: the helper `_last_record_text`
at `:81` and three test bodies at `:641`, `:662`, `:785`. `grep -n "n0 = len(_records"` returns **36**
delta sites, including the three the round added (`:705/:709`, `:730/:734`, `:768/:772`).

| test | reads `[-1]` | has a delta | verdict |
|---|---|---|---|
| `test_credential_invalid_utf8_separator_in_header_returns_400` (4 params) | via `recs[-1]` | **yes** (added this round) | closed |
| `test_credential_invalid_utf8_separator_in_json_body_returns_400` (3 params) | via `recs[-1]` | **yes** (added) | closed |
| `test_credential_control_char_in_json_body_returns_400` (2 params) | via `recs[-1]` | **yes** (added) | closed |
| **`test_credential_plus_split_with_pct2520_suffix_returns_400`** (red `:641`) | `_records(backend)[-1]` | **no** | **open — D5i-F6** |
| **`test_credential_raw_utf8_zero_width_in_header_returns_400`** (red `:662`, 6 params) | `_records(backend)[-1]` | **no** | **open — D5i-F6** |
| **`test_unquote_op_is_required_for_the_bound`** (red `:785`) | `_records(backend)[-1]` | **no** | **open — D5i-F6** |

`RECORDLESS_400_XTRACE` kills the fixed tests and leaves those eight cases green (item 6e). The brief's
item 7 asked me to *"confirm the delta asserts exist in **every** test that reads `[-1]`"* — they do not.

## Item 8 — report discipline

| brief requirement | verdict |
|---|---|
| every `file:line` re-derived with `grep -n` on the final tree | **FAILED** — 11 of ~22 spot-checks wrong, systematic +2 on the `record()` call sites (**D5i-F8**) |
| PIN wording per the brief's header | **FAILED** — names the brief commit, 3 commits back, calls it the CHILD (**D5i-F12**) |
| cost table with THREE columns, the load, and the vector per column | **PARTIAL** — three columns and a load are published, and the vectors are named; but the third column measures a *header* vector so it does not exercise the expensive arm (**D5i-F13**) |
| red-before lines PASTED from the parent run | **PASSED** — every line I ran matches verbatim, including the `TypeError` where a plain `AssertionError` would have been the easy fabrication |
| each mutant row names the mutated line and the killer that fired | **PASSED in form**, with two content errors (**D5i-F7**, **D5i-F14**) |
| stale-context sweep (mine, not the brief's) | **FAILED** — the oracle docstring and one test docstring still describe ops this round deleted (**D5i-F9**), and the precheck docstrings enumerate four byte-view sinks where there are five (**D5i-F10**) |

Every claimed artifact I checked exists at the stated path and says what the report says it says, with the
line-number exceptions above: `tasks/briefs/s0-01-d5i-support/D5i-report.md` (148 lines),
`tasks/briefs/s0-01-d5i-support/verify-D5h.md` (820 lines),
`tasks/briefs/s0-01-d5i-byte-view-sinks-and-invisible-class.md` (78 lines).

## Item 9 — live controls

**Normal traffic + streaming after ≥ 50 redactions** (own subprocess backend, PIN bytes, load 1.1):
```
redaction records written before the controls : 60   (60/60 requests -> 400; brief asked >= 50)
GET  /v1/models             -> 200 OK ; record path='/v1/models' ; authorization_fingerprint set
POST /v1/chat/completions   -> 200 OK ; reply='pong' ; record kept verbatim = True
streaming leg (s0-01-slow)  -> 200 OK ; 6 data lines ; [DONE] present = True
MARKER records still on disk-> 60 (none overwritten)
```

**`Connection: close` on every 4xx** (raw socket, 12 classes, all `close=True`):

| case | status line | `Connection: close` |
|---|---|---|
| 400 invalid-UTF-8 header | `HTTP/1.1 400 Bad Request` | True |
| 400 invisible separator, header | `HTTP/1.1 400 Bad Request` | True |
| 400 invisible separator, JSON body | `HTTP/1.1 400 Bad Request` | True |
| **400 top-level JSON string `"café"` (the D5i-F1 false positive)** | `HTTP/1.1 400 Bad Request` | True |
| 401 no auth | `HTTP/1.1 401 Unauthorized` | True |
| 404 unknown path | `HTTP/1.1 404 Not Found` | True |
| 411 Transfer-Encoding | `HTTP/1.1 411 Length Required` | True |
| 400 header parse defect | `HTTP/1.1 400 Bad Request` | True |
| 400 JSON depth > 32 | `HTTP/1.1 400 Bad Request` | True |
| 417 Expect | `HTTP/1.1 417 Expectation Failed` | True |
| 400 duplicate Content-Length | `HTTP/1.1 400 Bad Request` | True |
| 400 malformed Content-Length | `HTTP/1.1 400 Bad Request` | True |

**`--slow-delay` guard** (verbatim stderr, 7 inputs):
```
nan                rc=2  scripted_backend: --slow-delay nan must be a finite number >= 0
inf                rc=2  scripted_backend: --slow-delay inf must be a finite number >= 0
-1                 rc=2  scripted_backend: --slow-delay -1.0 must be a finite number >= 0
1e400              rc=2  scripted_backend: --slow-delay inf must be a finite number >= 0
--slow-delay=-inf  rc=2  scripted_backend: --slow-delay -inf must be a finite number >= 0
-nan               rc=2  scripted_backend.py: error: argument --slow-delay: expected one argument   (argparse)
abc                rc=2  scripted_backend.py: error: argument --slow-delay: invalid float: 'abc'
```
The whole unusable class is refused. Reproduces D5g-F14 / D5h exactly; no change was needed and none made.

**Interpreter sweep, server side, 3.11.15 / 3.12.3 / 3.13.12.** pytest is installed for 3.11 only
(`python3.12 -c "import pytest"` → no module), so **no pytest leg on 3.12/3.13** — stated as skipped and
substituted with a server-side sweep. Header sink: all 20 invisible separators plus the 42-code-point
divergence set → `400` + MARKER on all three. Decoded (JSON-escape) sink: **the 3.11 column diverges on
the 42-code-point set** (D5i-F3) and U+2065/U+FFFD are served on all three (D5i-F11); everything else
matches.

## Hostile-input battery on the record path (my own addition — positive control, no finding)

Live, own backend, PIN bytes. The `25.0s` cells are my harness's own socket read-timeout on a `200 OK`
that keeps the connection open — not a server delay (the `400` rows return in 0.00 s; box at load 1.35).

| input | status | record valid JSON | close |
|---|---|---|---|
| lone surrogate `\ud800` in a JSON value | 200 OK | yes | no |
| lone surrogate `\ud800` as a JSON key | 200 OK | yes | no |
| valid astral surrogate pair | 200 OK | yes | no |
| `1e400` (to inf) | 200 OK | yes (`"<non-finite>"`) | no |
| `-Infinity` literal | 200 OK | yes | no |
| `NaN` literal | 200 OK | yes | no |
| `<U+0000>` in a JSON string | 200 OK | yes | no |
| JSON nesting depth exactly 32 | 200 OK | yes | no |
| JSON nesting depth 33 | 400 Bad Request | yes | **yes** |
| top-level JSON list carrying a ZWNJ-split token | 400 Bad Request | yes | yes |
| top-level JSON `null` | 400 Bad Request | yes | yes |
| empty body, `Content-Length: 0` | 400 Bad Request | yes | yes |
| 20 000-key flat object | 200 OK | yes | no |
| 30-deep legal nested list | 200 OK | yes | no |

**No crash, no hang, no unhandled exception, no invalid record.** `GET /healthz` after the battery is
`200 OK`. The `allow_nan=False` + `_json_safe` path (F11) and the pre-parse depth gate (F10) both hold,
and `strip_invis` does not raise on lone surrogates (`unicodedata.category` accepts them and returns `Cs`).

## What I reproduced vs reviewed statically vs deliberately skipped

**Reproduced first-hand (live or in-process against the PIN's bytes):**
both gate runs (`500 passed` ×2), the red standalone (`166 passed`), pyflakes rc 0, and the
469→500 collect arithmetic against the true parent commit; the red-before state on the parent
implementation for all 20 new cases with verbatim failure lines (both assertion directions and the
`TypeError`); the four `byte_view` call sites traced from `State.record` to the wire; the false-positive
and fail-closed directions on every byte-view sink, live; the top-level-JSON-string false positive (F1);
the 7-sink × 5-separator percent-encoding leak with token recovery from the written record (F2), with a
7/7 negative control on `%20`; the full-code-point-space membership count of `_INVIS_CATEGORIES` under
three interpreters and the 42-code-point divergence set (F3), plus the live 3.11/3.12/3.13 decoded-sink
sweep and the token recovery from the 3.11 record; D5h's 20 served code points now all caught; the class
boundary over 50 code points; the false-positive direction over 15 legitimate-text vectors; the
per-character subsumption differential for all three removed ops over 1 114 112 characters (0 regressions,
and the report's own "0 outside the category set" claim re-derived independently for each of the three
domains); the parent-vs-PIN whole-closure differential over 3 096 directed + 25 000 random vectors (0
detection regressions); the impl-vs-oracle differential over the same 28 096 vectors (0 violations); the
depth pins from both sides; **37 mutant runs** on three isolated scratchpad trees (27 report rows including
`O2_UQ`; the 4 the brief required; `RECORDLESS_400_XTRACE`; 7 category-subset mutants and 2 oracle-side
mutants of my own; plus full-500 escalations for every survivor), each with pristine restore and a post-run
`git status --porcelain` scope-clean assertion (**100% clean, every row**), and each with its `ran` count
verified > 0; the `CTL_PARTIAL_noC1` depth-2 trace; the `O2_UQ` token-dependence over 4
vectors; `M_V12_CLOSE` settled three ways (CPython `send_header` source on all three interpreters, a
runtime flag probe, and a header-ignoring socket-pipelining differential); the four-column cost table with
its load stated; the live normal-traffic + streaming control after 60 redactions; `Connection: close` on
12 rejection classes; the `--slow-delay` guard over 7 inputs; every `file:line` in the D5i-F8 table,
re-derived with `grep -n`; the report's PIN sha, its subject line and its distance from the graded commit.

**Reviewed statically only:** the full parent→PIN diff of all three files; the D5i lane brief, the D5i
report text, and the VERIFY-D5h verdict; the `anti-hollow-green` and `adversarial-review` skills.

**Deliberately skipped, with the reason:**
- **The pytest leg on 3.12/3.13** — pytest is installed for 3.11 only in this sandbox. Substituted with a
  server-side sweep under all three interpreters, which is what surfaced D5i-F3; it covers interpreter
  dependence of the *screen* but not of collection.
- **The PC/bridge venue** — no bridge banner this session, so the PC gate line in the report
  (`500 passed in 32.10s`, 12 cores, `-n 8`) is **not reproduced**; it is not load-bearing for any finding
  below.
- **The rest of the repo suite** — other lanes hold the shared tree (a foreign pytest run was live during
  part of my window). I ran exactly the two files the brief names, on a `git archive` copy of the PIN.
- **Mutating the shared tree** — every mutant ran on scratchpad copies under `vd12/mutA` and `vd12/mutB`;
  the shared tree saw read-only git only, and `git status --porcelain` on the three scope files there is
  empty.
- **Disclosed process defect:** my first two mutant batches shared one scratch tree and raced. I discarded
  every result from that window and re-ran the entire campaign on two isolated trees; only the clean
  re-run is reported. I also mis-encoded wire bytes as UTF-8 in my first byte-view probe, which produced a
  spurious "200 OK" on the invalid-UTF-8 header row; corrected and re-run, and both the wrong and the
  right result are stated above.
- **Backends** — I killed only the backends I started (record dirs under `/tmp/vd12_*`); a `pkill -f`
  of mine matched its own command line and killed my shell (the bracket rule), after which I switched to
  PID-targeted kills. Other lanes' processes were never signalled.

## VERDICT

**NOT-READY** — blocking set: **D5i-F1**, **D5i-F2**, **D5i-F3**.

- **D5i-F1** — the defect this round exists to close survives at a second call site. `body_str` at
  `backend:375` still passes `byte_view=True`, and `body` is a decoded `str` for every top-level JSON
  string document. `POST` with the body `"caf\u00e9"` — **pure ASCII on the wire, no
  credential** — returns `400 Bad Request` with the record blanked to
  `{"credential_in_unexpected_location": true}`. Reproduced live on the PIN's bytes with three paired
  negative controls. One expression fixes it.
- **D5i-F2** — the invisible-separator class is re-opened through percent-encoding. `unquote` defaults to
  `errors="replace"`, so `%80` becomes U+FFFD, whose category `So` is deliberately outside
  `_INVIS_CATEGORIES`. The token splits on **all 7 sinks for 5 separators**, is served `200 OK` with no
  `Connection: close`, is written verbatim, and is recovered from the record by
  `unquote(value, errors="ignore")`. The oracle uses the same `unquote`, so **no test in the suite can
  see it** — the identical shared-blind-spot shape as verify-D5g-F1 and D5h-F2. Negative control `%20`
  is 400 on 7/7.
- **D5i-F3** — the class is closed by a table the runtime supplies, not one the repo owns.
  `unicodedata.category` gives 4263 members on python3.11 (UCD 14.0) and 4305 on 3.12/3.13 (UCD 15.0/15.1).
  **42 Unicode-15 nonspacing and format marks are stripped on 3.12/3.13 and not on 3.11** — the
  interpreter every one of the 500 tests runs under here. Live: U+10EFD, U+1E08F, U+11F36, U+13439 and
  U+0ECE each split the token in a JSON body, return `200 OK`, are written verbatim, and the token is
  recovered by the module's own transform on a current table; the same vectors are `400` + MARKER on
  3.12/3.13. The sandbox gate and the PC gate are therefore not proving the same predicate, and the
  fixture's own docstring says it runs on the PC.

Non-blocking but real, all reproduced: **D5i-F4** (`_INVISIBLE_EXTRA` unpinned in the impl — survives all
500, non-equivalent on five zero-width fillers, while the *oracle's* copy IS pinned), **D5i-F5** (the `Cs`
member unpinned on **both** sides — survives all 500, non-equivalent on lone surrogates), **D5i-F16**
(`Me` and `Zl`+`Zp` unpinned — each survives all 500; with F4 and F5 that is **five of the nine members of
the class predicate with no killing vector anywhere in either test file**), **D5i-F6** (eight test cases still assert off a stale `[-1]`;
`RECORDLESS_400_XTRACE` leaves them green), **D5i-F7** (`M_V12_CLOSE` is a genuine equivalent, not
untested defence-in-depth; no killer can exist and writing one would be a tautology), **D5i-F8** (11 of 22
`file:line` refs wrong, systematic +2 — D5h-F6 not closed), **D5i-F9** (the oracle docstring still
describes the strict re-decode this round deleted), **D5i-F10** (the restated precheck docstring
enumerates four byte-view sinks where there are five), **D5i-F11** (unassigned code points such as U+2065
are outside the class on every interpreter — UNSURE on the "invisible" criterion), **D5i-F12** (the PIN
names the brief commit again, three commits back — D5h-F7 not closed), **D5i-F13** (the cost table's
bound-exceeded column uses a header vector, so the expensive arm is still untabulated — with the vector in
the body it is 2.1 s at 1 MB, against the report's "no cell exceeds 1 s" — and the table is still not
reproducible: 0.630 s vs the report's 0.164 s for the ordinary 1000 KB cell at a *lower* load, D5h-F8's
complaint for the third round), **D5i-F14** (two mutant rows
are the same mutation), **D5i-F15** (the live-control redaction count is not stated in the report).

What the round genuinely delivered, reproduced and confirmed: the `byte_view` split is correct at four of
five call sites and closes D5h-F1 on the leaf walk (`café` and its five siblings are served 200 +
verbatim, red on the parent); the invisible class closes **all 20** of D5h-F2's served code points on all
three interpreters, and closes 20 more boundary points I probed (variation-selector supplement, the
U+2062-U+2064 invisible operators, interlinear annotation, shorthand format, Mongolian FVS, enclosing
marks) while correctly *not* touching visible spacing marks — with **zero** false positives across
Vietnamese, Hindi, Arabic, Hebrew, Thai, ZWJ emoji and the MARKER record itself; the removal of
`strip_ws`/`strip_zwc`/`strip_ctl` and the strict re-decode is a genuine subsumption with **0** detection
regressions over 28 096 vectors and no depth-bound movement; the oracle now carries the identical op set
one depth deeper and is **0**-violation wider over the same corpus, with every op but the qualified
`O2_UQ` dying to a named self-test; `JSONSAFE_INLINE_IN_RECORD`, `LENIENT_IN_IMPL` and
`PRECHECK_AFTER_CLOSURE` all now die (D5h-F3/F5/F14 closed); D5h-F9 and D5h-F12 are closed; and **26 of 26**
spot-checked KILLED mutant rows reproduce with the report's named killer, each with a verified non-zero
test count.

**This verdict depends on nothing I failed to reproduce.** Each of D5i-F1, F2 and F3 was observed live
against the PIN's bytes with a paired negative control; F3 on all three interpreters. The one thing I could
not run — the PC gate leg — bears on no finding here.

