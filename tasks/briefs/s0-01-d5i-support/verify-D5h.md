# VERIFY-D5h — round-11 adversarial grade of lane D5h (S0-01 scripted backend credential screen)

## Premise (verified, not assumed)

| item | value |
|---|---|
| PIN (dispatch) | `e8fdfabc3dadfac756224a562901d4580050ba13` — `git cat-file -e` rc=0. Subject: "S0-01 WIP checkpoint 8o: backend fails CLOSED on invalid UTF-8, control characters join the closure, the oracle's ops each pinned (lane D5h) — REVIEW-PENDING, nothing minted" |
| shared-tree HEAD at dispatch | `e8fdfab` = the PIN (`git rev-parse HEAD`) |
| `git diff --stat e8fdfab HEAD -- <3 scope files>` | EMPTY |
| PIN parent | `d5b1b03` ("S0-01 checker round 10 brief (A5h) + the VERIFY-D5g verdict, before dispatch") |
| report's claimed PIN | `dd0cbc2bcc22fb3345f068b520c2f254247b1ed5` — EXISTS (`git cat-file -e` rc=0), but it is the *brief* commit = the PIN's **parent's parent**… see F7 below |
| shared tree dirty set (untouched) | `proofs/S0-01/check_acp_conformance.py`, `tests/test_s0_01_check_acp_conformance.py` (lane A5h) |
| scratch copy | `git archive e8fdfab | tar -x` into `scratchpad/vd11`, own `git init` + base commit; `git status --porcelain` = 0 lines |
| copy hashes (= report FILES table) | backend `e6b93b14b126075b98be13b52a8dfba15ab2219de2b745e95073195071c11afc` 635 lines · main `f4e1f51d79acc6cf7547bea67e3cf5101d799397dfc4e943ec11f9050ed3c838` 2014 lines · red `ef399b3524a8c19b0df58d3672315fd2407f66c88d3a4454e4693666f4e8eab2` 781 lines — all three match the report exactly |
| interpreter | `python3` = `/usr/local/bin/python3` 3.11.15; pytest 9.1.1; pyflakes 3.4.0 |
| `df -h /` | `/dev/vda 252G 25G 13G 68% /` |
| load average at start | `3.99 2.47 2.11` (dropped to ~1.2-1.7 during the live probes; stated per timing claim) |

## Item 1 — F1 closure at the CLASS: the precheck's exact domain

### 1a. `_has_invalid_utf8_bytes` (`proofs/S0-01/tools/scripted_backend.py:113-133`) — derived domain

Reproduced in-process against the PIN's module. The predicate is exactly
*"`s` latin-1-encodes, the resulting bytes contain at least one byte >= 0x80, and those bytes are not
well-formed UTF-8"*.

| invalid-UTF-8 class (latin-1 view) | precheck |
|---|---|
| overlong 2-byte `C0 A0`, `C1 BF` | True |
| overlong 3-byte `E0 80 A0`; overlong 4-byte `F0 80 80 A0` | True |
| surrogates encoded as bytes `ED A0 80` (D800), `ED BF BF` (DFFF) | True |
| above U+10FFFF: `F4 90 80 80`, `F5 80 80 80` | True |
| truncated 2/3/4-byte: `C3`, `E2 80`, `F0 9F 98` | True |
| lone continuation `80`, `BF` | True |
| 5-byte `F8 88 80 80 80`, 6-byte `FC 84 80 80 80 80` | True |
| `FE FF` (never valid) | True |
| valid sequence + 1 junk byte: `E2 80 80 80`, `C2 A0 80` | True |

**The whole invalid class is covered — no gap found in the predicate itself.** The intentionally-excluded
sets behave as designed: well-formed byte views (`EF BB BF` BOM, noncharacters `EF BF BE`/`EF BF BF`/`EF B7 90`,
`C3 A9`, `F0 9F 98 80`, `F4 8F BF BF`, `E2 80 8E`) → False; non-byte-view strings (real U+200B, lone
surrogates U+D800/U+DFFF, CJK, emoji, U+0100) → False (latin-1 encode raises); pure ASCII → False.

### 1b. Every invalid class × every sink, live (7 sinks × 6 separators, own subprocess backend)

Reproduced with and without the `-%25252541` saturating suffix — **identical cells both ways**, so the
report's matrix is not suffix-vacuous. Cell = `status/record-body/Connection: close`.

| sink \ sep | enquad+junk | nbsp+junk | overlong | lone_cont | DEL | SOH |
|---|---|---|---|---|---|---|
| header_value | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C |
| header_name | 400/no_rec/C | 400/no_rec/C | 400/no_rec/C | 400/no_rec/C | 400/no_rec/C | 400/no_rec/C |
| query | 400/MARKER/C | 400/no_rec/C | 400/no_rec/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C |
| path | 400/MARKER/C | 400/no_rec/C | 400/no_rec/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C |
| json_value | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C |
| json_key | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C |
| json_list | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C | 400/MARKER/C |

**Matches the report's 42-cell matrix cell-for-cell**, including its `no_rec` cells and their stated
mechanisms. `no_rec` for header_name = `_framing_gate` arm 1; `no_rec` for query/path with `nbsp+junk`
and `overlong` = `http.server` rejects the request line, because both byte strings contain `A0`, which
`str.split()` treats as whitespace in the latin-1 view (mechanism re-derived, see item 7). All fail closed.
**No finding here** — the report's F1 matrix reproduces.

### 1c. THE OTHER DIRECTION — legitimate traffic. **A legitimate-shape 400 was found (F1 below).**

Live, own backend, bodies that are well-formed UTF-8 on the wire and carry no credential anywhere:

| body content (JSON `messages[0].content`) | status | record |
|---|---|---|
| `hello` | 200 OK | VERBATIM |
| CJK (U+4E16 U+754C) | 200 OK | VERBATIM |
| emoji U+1F600 | 200 OK | VERBATIM |
| `cafe` + combining U+0301 (decomposed) | 200 OK | VERBATIM |
| **`café` (precomposed U+00E9)** | **400 Bad Request** | **MARKER** |
| **`Müller` (U+00FC)** | **400 Bad Request** | **MARKER** |
| **`señor` (U+00F1)** | **400 Bad Request** | **MARKER** |
| **`£100` (U+00A3)** | **400 Bad Request** | **MARKER** |
| **`50°C` (U+00B0)** | **400 Bad Request** | **MARKER** |
| **`© 2026` (U+00A9)** | **400 Bad Request** | **MARKER** |
| `Ã©` (U+00C3 U+00A9 — a latin-1 pair that happens to be valid UTF-8) | 200 OK | VERBATIM |

Header-value and percent-encoded query forms of the same characters are **200/VERBATIM** — the defect is
confined to the parsed-JSON string-leaf sink. See finding **D5h-F1**.

## Item 2 — `strip_ctl` domain and the invisible-separator class

### 2a. Boundary code points as a token separator (impl `_carries_secret`, both wire and str form)

| code point | impl verdict | by which op |
|---|---|---|
| U+0008, U+000E, U+001F, U+007F, U+0080, U+009F | CAUGHT | `strip_ctl` |
| U+0009 TAB, U+000A LF, U+000D CR | CAUGHT | `strip_ws` (left out of `strip_ctl` as designed) |
| U+0020 SPACE | CAUGHT | `strip_ws` |
| U+0085 NEL, U+00A0 NBSP | CAUGHT | `strip_ctl` / `strip_ws` (Python `\s` covers U+0085, U+00A0) |
| U+00AD SHY | CAUGHT | `strip_zwc` |
| U+007E `~` | served (printable — correctly out of the class) |

`strip_ctl` = `re.sub("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", x)` at `scripted_backend.py:149`,
mirrored verbatim in the oracle at `tests/red/test_s0_01_backend_credential_screen.py:111`.
**The domain is exactly the brief's spec — C0 minus TAB/LF/CR, DEL, and all of C1. No finding.**

`strip_zwc` covers exactly **U+200B, U+FEFF, U+00AD, U+2060** (read off the source class at
`scripted_backend.py:148` / red `:110`).

### 2b. The class the brief names — "invisible separator inside a recorded credential"

**20 invisible / non-printing separators split the token and are SERVED VERBATIM.** Reproduced live.
The 7×6 matrix for six of them (no saturating suffix), cell = `status/record/close`:

| sink \ sep | U+200E LRM | U+200C ZWNJ | U+3164 HANGUL FILLER | U+2800 BRAILLE BLANK | U+FE00 VS1 | U+180E MVS |
|---|---|---|---|---|---|---|
| header_value | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC |
| header_name | 400/no_rec/C | 400/no_rec/C | 400/no_rec/C | 400/no_rec/C | 400/no_rec/C | 400/no_rec/C |
| query | 200/VERBATIM/noC | 200/VERBATIM/noC | 400/no_rec/C | 400/no_rec/C | 200/VERBATIM/noC | 400/no_rec/C |
| path | 404/VERBATIM/C | 404/VERBATIM/C | 400/no_rec/C | 400/no_rec/C | 404/VERBATIM/C | 400/no_rec/C |
| json_value | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC |
| json_key | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC |
| json_list | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC | 200/VERBATIM/noC |

**30 of 42 cells leak.** Token recovery from the written record file, one line each:

```
header X-Trace split by U+200E LRM     -> 200 OK; record x-trace = 's0-01-upstream-tok\xe2\x80\x8een-0123456789abcdef'
     value.encode("latin-1").decode("utf-8") + drop Cf/Cc/Zs/Mn  -> TOKEN recovered = True
same for U+200C ZWNJ, U+2800 BRAILLE, U+3164 HANGUL FILLER, U+E0020 TAG SPACE  -> True (5/5)

json value split by U+200E LRM (ordinary JSON \u escape) -> 200 OK; record body.t = 's0-01-upstream-tok‎en-...'
     drop Cf/Cc/Zs/Mn/Cs  -> TOKEN recovered = True
same for U+200C, U+3164, U+FE00 VS1, and U+D800 LONE SURROGATE   -> True (5/5)
```

Paired negative control on the identical sinks (the neighbouring, covered code points):
```
header/json split by U+200B ZWSP     -> 400 Bad Request / MARKER
header/json split by U+2000 EN QUAD  -> 400 Bad Request / MARKER
header/json split by U+FEFF BOM      -> 400 Bad Request / MARKER
```
U+200B is closed; **U+200C — the next code point — is open.** See finding **D5h-F2**.

Full served list (both wire and str form, `_carries_secret` = False):
U+034F CGJ · U+061C ALM · U+115F/U+1160 HANGUL FILLERS · U+180E MVS · U+200C ZWNJ · U+200D ZWJ ·
U+200E LRM · U+200F RLM · U+202A LRE · U+202E RLO · U+2061 FUNCTION APPLICATION · U+2800 BRAILLE BLANK ·
U+3164 HANGUL FILLER · U+FE00 VS1 · U+FFA0 HALFWIDTH HANGUL FILLER · U+1D173 · U+E0001 LANGUAGE TAG ·
U+E0020 TAG SPACE · lone surrogate U+D800 (str form only).
Of the brief's named probes: U+200E/U+200F **served**; U+2028/U+2029 caught (Python `\s`); U+FEFF and
U+00AD caught (`strip_zwc`).

The oracle agrees ("absent") on every one of these, so **no test in the suite can see them** — the oracle
is not wider than the impl on this axis; both share the same blind spot.

## Gate runs — reproduced first-hand, pasted verbatim (scratch copy of the PIN, load 1.10 → 2.62)

```
RUN 1            469 passed in 138.80s (0:02:18)   pytest-exit: 0
RUN 2            469 passed in 138.15s (0:02:18)   pytest-exit: 0
RED STANDALONE   136 passed in 40.70s              pytest-exit: 0
pyflakes (3 files)  rc: 0
git status --porcelain (3 scope files, scratch copy): EMPTY before and after every mutant
```

The report's `469 passed` / `136 passed` / `pyflakes rc 0` all reproduce exactly. The **+17 arithmetic
re-derived independently**: 7 new test functions (4+3+2+2+1+1+1 = 14 cases after parametrisation) + 4 new
oracle self-test vectors − 1 deleted test (`test_json_safe_does_not_mutate_request_body`) = **+17**.
`lint_delta.py` was re-run read-only on the shared tree — rc 0, `0 NEW pyflakes hit(s)`; see item 8.

## Item 3 — is the oracle STRICTLY wider? (verify-D5g F3)

### 3a. Every oracle op drop goes red on a NAMED self-test — reproduced, all 9

Scope `R::TestOracleSelfTests`, scratch copy, `git status` clean after each.

| oracle mutant | verdict | killer (mine) | report's claim | match |
|---|---|---|---|---|
| O2_UQ (drop `unquote`) | SURVIVED | — | EQUIVALENT | ✔ |
| O3_UQP | KILLED | `test_oracle_known_vectors[plus_split]` | `[plus_split]` | ✔ |
| O4_WS | KILLED | `[junk_suffix]` | `[junk_suffix]` | ✔ |
| O5_LOWER | KILLED | `[uppercased]` | `[uppercased]` | ✔ |
| O6_ZWC | KILLED | `[zwsp_split]` | `[zwsp_split]` | ✔ |
| **O_UTF8_LENIENT** | KILLED | `[raw_utf8_mojibake]`, `[raw_utf8_mojibake_junk]` | `[raw_utf8_mojibake]` | ✔ |
| **O_CTL** | KILLED | `[del_split]` | `[del_split]` | ✔ |
| O1 (`return True`) | KILLED | `[junk_suffix]` (+3) | `[junk_suffix]` | ✔ |
| O7_DEPTH1 | KILLED | `[junk_suffix]` (+3) | `[junk_suffix]` | ✔ |
| O_JSONBLIND | KILLED | `[json_escaped_tab]` | `[json_escaped_tab]` | ✔ |

**O_UTF8 (strict) is genuinely gone** — `grep -n utf8_redecode` on the red file shows the identifier only in
prose (`:96,:97,:104,:105,:635`); the ops tuple at `:117-118` carries `utf8_redecode_lenient` alone. The
"N/A" row is honest.

### 3b. O2_UQ is EQUIVALENT ONLY for this token — confirmed non-equivalent in general

Built a no-`unquote` variant of the oracle in-process and drove it with a `+`-bearing token:

```
TOKEN='a+b'  text='%61+%62'        full-oracle absent=False   no-unquote absent=True   DIVERGES
TOKEN='a+b'  text='%2561%2B%2562'  full-oracle absent=False   no-unquote absent=True   DIVERGES
TOKEN='x+y'  text='%78+%79'        full-oracle absent=False   no-unquote absent=True   DIVERGES
```
Mechanism: `unquote_plus(x) == unquote(x.replace('+',' '))`, so dropping `unquote` destroys every literal
`+` before percent-decoding; a token containing `+` then has no reachable form. The report's qualifier
"for a token containing no `+`" is **correct** — but it lives only in the report's mutant table; **no
docstring or code comment in any of the three files carries it** (`grep -i "containing no|token containing"`
→ no hit in all three). See finding **D5h-F12**.

### 3c. Directed + random differential — the oracle IS wider than the impl's closure

| test | corpus | violations |
|---|---|---|
| directed (4 prefixes × 24 separators × 7 suffixes × 3 case-folds + token-free junk) | 1512 unique | **0** |
| random (seeded 11, token-splitting + noise vectors) | 25 000 | **0** |

Violation = "impl closure FINDS the token AND the oracle says absent". Result: `[]` on both.
Mechanism re-derived: `lenient(x) ⊇ strict(x)` for every `x` (when the strict decode succeeds the two agree;
when it fails, strict returns `x` — already in the form set — while lenient adds the ignore-decoded form),
and the oracle's depth is 6 vs the impl's 5. So the oracle is wider by construction, not by luck.

**Nuance worth recording:** under the brief's *literal* wording ("impl says secret ∧ oracle says absent"),
173 of the 1512 directed vectors "diverge" — every one of them is an impl **fail-closed arm**
(bound-exceeded or the invalid-UTF-8 precheck), not a detection claim, e.g.
`'s0-01-upstream-tok‎en-0123456789abcdef-%25252541'` (closure-found=False, saturated=False).
The oracle has no counterpart to either arm by design. Not a finding, but the wording should say
"impl **closure** finds".

## Item 4 — `_json_safe` (verify-D5g F2)

- `_json_safe` is at module scope, `proofs/S0-01/tools/scripted_backend.py:249-280`; the **only** caller is
  `State.record` at `:362` (`grep -n _json_safe` → `:249`, `:362`). Reachability confirmed from the live
  record-write statement, not from an import.
- `M_JSONSAFE_INPLACE` (`root = o` + both copy branches collapsed to `stack.append(v)`) → **KILLED** by
  `B::test_json_safe_copy_on_write`, verbatim failure
  `{'a': [{'x': '<non-finite>'}]} != {'a': [{'x': nan}]}`. The report's row reproduces.
- The inlining mutant the brief demanded (`JSONSAFE_INLINE_IN_RECORD` — module function kept but
  `record` calls a private in-place copy) is reported in item 5.

## Item 5 — the mutant table on the final tree

### 5a. Reproduction of the report's rows — 25 KILLED rows spot-checked, **25/25 reproduce with the report's named killer test**

Method: run the report's named killer first; escalate to the full two-file scope on survival. Pristine-copy
restore + `git status --porcelain` on the three scope files asserted empty after every mutant (100% clean).

| mutant | my verdict | my killer | report's killer | match |
|---|---|---|---|---|
| NOOP | SURVIVED (narrow **and** full) | — | SURVIVED (intended) | ✔ |
| M_SAT_IGNORE | KILLED | `depth5_percent_nesting[header-d5_space]` | `[header-d6_space]` | ✔ same test |
| M_SAT_INV | KILLED | `R::test_post_content_length_exactly_max_is_accepted` | same | ✔ |
| M_SEEN | KILLED | `test_credential_plus_split_with_pct2520_suffix_returns_400` | same | ✔ |
| M_D4 | KILLED | `B::test_saturating_junk_is_served` | same | ✔ |
| M_D6 | KILLED | `B::test_bound_exceeded_blanks_the_record` | same | ✔ |
| M_SENTINEL | KILLED | `whitespace_split_in_valid_json_body[TAB]` | same | ✔ |
| M_MC5_NOTUPLE | SURVIVED narrow → KILLED full | `B::test_bound_exceeded_blanks_the_record` | `whitespace_split…[TAB]` | ✖ see F10 |
| M_UTF8_DEL | KILLED | `raw_utf8_zero_width_in_header[ZWSP]` | same | ✔ |
| M_LOWER_DEL | KILLED | `uppercased_token_in_header` | same | ✔ |
| M_ZWC_DEL | KILLED | `zero_width_pct_encoded[ZWSP]` | same | ✔ |
| M_WS_DEL | KILLED | `whitespace_split_in_valid_json_body[TAB]` | same | ✔ |
| M_UQP_DEL | KILLED | `encoded_whitespace_split[header-PLUS]` | same | ✔ |
| **M_UQ_DEL** | KILLED | `test_unquote_op_is_required_for_the_bound` | same | ✔ |
| **M_CTL_DEL** | KILLED | `control_char_in_header_value[DEL]` | same | ✔ |
| **M_UTF8_PRECHECK_DEL** | KILLED | `invalid_utf8_separator_in_header[enquad_plus_junk]` | same | ✔ |
| **M_UTF8_PRECHECK_INV** | KILLED | `R::test_post_content_length_exactly_max_is_accepted` | same | ✔ |
| M_HDRNAME | KILLED | `depth5_percent_nesting[header_name-d5_space]` | `[header_name-d5_space]` | ✔ |
| M_HDRVAL | KILLED | `authorization_prefixed_header_name_is_not_exempt[Authorization-X]` | same | ✔ |
| M_RAWBODY | KILLED | `duplicate_json_key_hiding_token_returns_400` | same | ✔ |
| M_PATH | KILLED | `encoded_whitespace_split[query-%20]` | same | ✔ |
| M_JSONSTRINGS | KILLED | `whitespace_split_in_valid_json_body[TAB]` | same | ✔ |
| M_MC9_LISTS | KILLED | `whitespace_split_in_json_list_element[TAB]` | same | ✔ |
| M_V12_CLOSE | KILLED | `B::test_framing_domain_table[no_cl/GET/v1/models/nocred]` | same | ✔ |
| M_DEPTHGATE_OFF | KILLED | `json_depth_over_limit_returns_400_no_record` | same | ✔ |
| **M_JSONSAFE_INPLACE** | KILLED | `B::test_json_safe_copy_on_write` | same | ✔ |

### 5b. The four mutants the brief told me to ADD, plus two of my own — **4 SURVIVED**

Full two-file scope (`469 passed` = survival), pristine restore + scope-clean assertion after each.

| mutant | mutation | verdict | killer / consequence |
|---|---|---|---|
| **PRECHECK_PARTIAL** | precheck removed from `_carries_secret`, re-added at the header-VALUE call site only | **KILLED** | `invalid_utf8_separator_in_json_body[overlong_pair]`, `[enquad_plus_junk]` — the precheck is proven to run past header values |
| **CTL_PARTIAL_noC1** | `strip_ctl` class narrowed to `[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]` (C1 arm removed) | **SURVIVED (469 passed)** | non-equivalent — see F4 |
| **LENIENT_IN_IMPL** | precheck deleted, impl's `utf8_redecode` made lenient (`errors="ignore"`) — the brief's *rejected alternative* | **SURVIVED (469 passed)** | non-equivalent — see F5 |
| **PRECHECK_AFTER_CLOSURE** | precheck call moved below the `any(t in f …)` check | **SURVIVED (469 passed)** | genuinely EQUIVALENT at the boundary (both arms `return True`); the only difference is cost — see F8/F14 |
| **JSONSAFE_INLINE_IN_RECORD** (brief item 4) | module `_json_safe` kept and still tested; `record` calls a private in-place walk instead | **SURVIVED (469 passed)** | see F3 |
| RECORDLESS_400_HDR (mine) | invalid-UTF-8 header rejected in `_framing_gate` (400, **no record**) instead of in `_carries_secret` | SURVIVED the F1 header tests; KILLED on the full red file only by the **JSON-body twin** | see F11 |

Non-equivalence proofs (in-process, real modules loaded from the PIN's bytes):

```
CTL_PARTIAL_noC1   TOKEN split by the WIRE form of U+0080 (bytes C2 80 — VALID UTF-8, so the
                   precheck passes and utf8_redecode turns it into U+0080):
                       HEAD          _carries_secret = True   (400, blanked)
                       CTL_PARTIAL   _carries_secret = False  (200, token served verbatim)
                   same for the wire forms of U+0081, U+008D, U+009F.

LENIENT_IN_IMPL    "invalid UTF-8, NO token present"        HEAD=True   LENIENT=False   DIVERGES
                   "caf" + U+00E9 (ordinary latin-1 text)   HEAD=True   LENIENT=False   DIVERGES
                   token split by 0x80 (the F1 vector)      HEAD=True   LENIENT=True    (same)
```

### 5c. O2_UQ and O_UTF8, the two claimed equivalents

- **O2_UQ** — reproduced as SURVIVED. Non-equivalent in general (item 3b): a `+`-bearing token diverges.
  The qualifier is in the report but **nowhere in the tree** (F12).
- **O_UTF8 (N/A)** — confirmed: `utf8_redecode` (strict) is absent from the oracle's ops tuple; the
  identifier survives only in prose at red `:96,:97,:104,:105,:635`. The "N/A" row is honest.

## Item 6 — red-before discipline (parent impl `d5b1b03` + HEAD tests)

Separate scratch tree (`vd11red`): the PIN's three files, backend swapped for the parent blob
(`sha256 841b0963f74e2946…` = the D5g-graded backend). Result: **`12 failed, 17 passed in 45.84s`**.

| new test | report's label | my observation | verdict |
|---|---|---|---|
| `invalid_utf8_separator_in_header` ×4 | RED | **RED**, verbatim `AssertionError: assert b'HTTP/1.1 200 OK' == b'HTTP/1.1 400 Bad Request'` (red `:689`) | ✔ |
| `invalid_utf8_separator_in_json_body` ×3 | RED | **RED**, same assertion | ✔ |
| `control_char_in_header_value` ×2 | RED | **RED**, same assertion | ✔ |
| `control_char_in_json_body` ×2 | RED | **RED**, same assertion (red `:746`) | ✔ |
| `test_json_safe_copy_on_write` | RED — *"`AssertionError: _json_safe mutated the input`"* | **RED**, but `AttributeError: module 'scripted_backend' has no attribute '_json_safe'` | ✖ **F9** |
| 4 oracle vectors | CONTROL | **PASS** on parent impl (they exercise the HEAD oracle) | ✔ |
| `test_unquote_op_is_required_for_the_bound` | CONTROL (kills M_UQ_DEL) | **PASS**; M_UQ_DEL dies on it | ✔ |
| `test_raw_non_ascii_header_name_rejected_by_gate_no_record` | CONTROL | **PASS** | ✔ |

Baseline arithmetic re-derived independently: parent collect-only **452 tests**, HEAD collect-only
**469 tests** → **+17**. The report's DISCREPANCIES #1 (brief said 460, from D5g's isolated copy) is correct.

## Item 7 — report discipline (verify-D5g F8/F9/F10/F12)

### 7a. PIN — half closed (F7 below)
`git cat-file -e dd0cbc2bcc22fb3345f068b520c2f254247b1ed5` → rc 0, so the sha **exists** (D5g-F8's literal
complaint is fixed). But `dd0cbc2` is *"S0-01 backend round 11 brief (D5h) + the VERIFY-D5g verdict, before
dispatch"* — the brief commit, **two commits before** the checkpoint that actually carries the work
(`e8fdfab`, via `d5b1b03`). The shipped bytes match the PIN's blobs exactly (sha256 + line counts, all
three), so this is a provenance defect, not a content defect — but a reader who checks out `dd0cbc2`
gets the **parent** implementation, i.e. the code the round exists to replace.

### 7b. file:line — NOT closed. **14 of 22 spot-checked refs are wrong.**

| report claim | true anchor | what sits at the claimed line |
|---|---|---|
| `scripted_backend.py:250-251` (precheck call) | **:303** | inside `_json_safe`'s docstring |
| `scripted_backend.py:247-249` (F11 docstring clause) | **:299-301** | `return v` / blank / `def _json_safe` |
| `scripted_backend.py:153` (`strip_ctl` lambda) | **:149** | inside `utf8_redecode`'s docstring |
| `scripted_backend.py:168` (ops tuple) | **:159** | `seen.add(v)` |
| `scripted_backend.py:476` (F6 comment) | **:481** | `self._last_raw_body = raw if raw else None` |
| red `:103` (oracle `strip_ctl`) | **:111** | docstring prose |
| red `:104-107` (lenient fn) | **:112-116** | docstring prose |
| red `:416/:418/:420/:422` (the 4 new oracle vectors) | **:418/:420/:422/:424** | each ref points at the **previous** vector |
| red `:720-733` (`control_char_in_header_value`) | def at **:718**, decorator **:715** | range starts after the def |
| red `:754-760` (`unquote_op…`) | def at **:752** | range starts after the def |
| main `:2002-2013` (`json_safe_copy_on_write`) | def at **:2001** | off by one |
| correct: precheck func 108-128⊃113 · `_json_safe` 219-249⊃249 · red ops `:117-118` · oracle docstring 92-101⊃93 · F1 hdr 674-696⊃677 · F1 json 699-717⊃703 · F13 json 736-751⊃738 · F5 763-781⊃764 | | |

### 7c. cost table — NOT reproducible; the expensive path is still untabulated (F8)

My measurement, same box, **load average 1.69 → 1.96** (min of 5 per cell, `http.client`, own subprocess
backend on the shared tree's unmodified file):

| body KB | ordinary (s) | invalid-UTF-8 fail-closed (s) | **bound-exceeded fail-closed (s)** | report says |
|---|---|---|---|---|
| 1 | 0.001 | 0.001 | 0.002 | 0.001 / 0.001 |
| 10 | 0.003 | 0.003 | 0.007 | 0.002 / 0.002 |
| 100 | 0.024 | 0.021 | 0.058 | 0.011 / 0.011 |
| 1000 | **0.227** | 0.203 | **0.584** | **0.099 / 0.098** |

All statuses 200/400/400 as expected. verify-D5g measured 0.197 ordinary / 0.655 fail-closed at 1000 KB —
**my numbers reproduce D5g's, not D5h's.** No cell exceeds 1 s, so this is not a threshold failure.

### 7d. sink × separator matrix — reproduced (item 1b). Both stated mechanisms re-derived from primary source:

```
email.parser.Parser(_class=http.client.HTTPMessage).parsestr(<header block with 0xC2 0xA0 in a NAME>)
   -> defects = [MissingHeaderBodySeparatorDefect()]     -> _framing_gate arm 1 -> 400, no record
"POST /v1/x?q=tok<C2 A0 80>en HTTP/1.1".split()          -> 4 words -> http.server 400 before dispatch
"POST /v1/x?q=tok<C0 A0>en HTTP/1.1".split()             -> 4 words -> 400 before dispatch
"POST /v1/x?q=tok<E2 80 80 80>en HTTP/1.1".split()       -> 3 words -> dispatched (hence MARKER, not no_rec)
```
Mechanism: `str.split()` treats latin-1 `\xa0` as whitespace, so only the two `A0`-bearing separators
break the request line. The report's `no_rec` legend is correct. **D5g-F5's false mechanism is closed.**

## Item 8 — live controls

```
redaction records written before the controls : 95   (brief asked >= 50)
GET  /v1/models             -> 200 OK ; record path='/v1/models' body=None auth_fp=set
POST /v1/chat/completions   -> 200 OK ; reply='pong' ; record kept verbatim = True
streaming leg (s0-01-slow)  -> 200 OK ; 6 data lines ; [DONE] present = True
MARKER records still on disk-> 95 (none overwritten)
```

`Connection: close` on every rejection (raw socket, 8 classes):

| case | status line | `Connection: close` |
|---|---|---|
| 400 invalid-UTF-8 header | `HTTP/1.1 400 Bad Request` | True |
| 400 control char header | `HTTP/1.1 400 Bad Request` | True |
| 400 control char JSON body | `HTTP/1.1 400 Bad Request` | True |
| 401 no auth | `HTTP/1.1 401 Unauthorized` | True |
| 404 unknown path | `HTTP/1.1 404 Not Found` | True |
| Transfer-Encoding present (no CL) | `HTTP/1.1 411 Length Required` | True |
| header parse defect | `HTTP/1.1 400 Bad Request` | True |
| JSON depth > 32 | `HTTP/1.1 400 Bad Request` | True |

`--slow-delay` isfinite guard (negative controls, verbatim stderr):
```
nan     rc=2  scripted_backend: --slow-delay nan must be a finite number >= 0
inf     rc=2  scripted_backend: --slow-delay inf must be a finite number >= 0
-1      rc=2  scripted_backend: --slow-delay -1.0 must be a finite number >= 0
1e400   rc=2  scripted_backend: --slow-delay inf must be a finite number >= 0
--slow-delay=-inf  rc=2  scripted_backend: --slow-delay -inf must be a finite number >= 0
-nan    rc=2  scripted_backend.py: error: argument --slow-delay: expected one argument   (argparse, D5g-F14)
abc     rc=2  scripted_backend.py: error: argument --slow-delay: invalid float: 'abc'
```
The whole unusable class is refused; `=`-form reaches the guard, bare `-inf`/`-nan` is caught by argparse
first. verify-D5g F14 reproduces exactly.

**Interpreter sweep — server run under each (pytest is 3.11-only in this sandbox, so no pytest leg on
3.12/3.13; stated as skipped):**

| separator | 3.11.15 | 3.12.3 | 3.13.12 |
|---|---|---|---|
| enquad+junk / nbsp+junk / overlong / lone_cont / DEL / SOH | 400 MARKER | 400 MARKER | 400 MARKER |
| U+200B ZWSP (covered) | 400 MARKER | 400 MARKER | 400 MARKER |
| **U+200C ZWNJ (not covered)** | **200 VERBATIM** | **200 VERBATIM** | **200 VERBATIM** |

The precheck and `strip_ctl` are interpreter-independent; so is the F2 leak.

`lint_delta` (run read-only on the shared tree): `4 .py changed, 0 NEW pyflakes hit(s), 0 removed`, rc 0.
Its advisory anti-pattern TELLs are all on **other lanes'** files (`check_acp_conformance.py`,
`frame_tee.py`) — none on the three D5h scope files. The report's claim reproduces.

## verify-D5g F1-F15 closure table

| D5g finding | closed? | by what, verified how |
|---|---|---|
| **F1** `utf8_redecode` fails OPEN on invalid UTF-8 | **CLOSED for the invalid-UTF-8 class** | `_has_invalid_utf8_bytes` (`backend:113-133`) + 7 tests red on the parent; 18 invalid classes → True; 42-cell live matrix all fail-closed on 3.11/3.12/3.13. **BUT the finding's own class ("invisible separator inside a recorded credential") is still open through valid-UTF-8 separators** — see D5h-F2 |
| **F2** `_json_safe` test is a tautology | **CLOSED for the function; NOT closed for the wiring** | `test_json_safe_copy_on_write` kills `M_JSONSAFE_INPLACE` (reproduced). `JSONSAFE_INLINE_IN_RECORD` survives all 469 — see D5h-F3 |
| **F3** oracle op with no self-test (`O_UTF8` survives) | **CLOSED** | strict op removed; all 9 oracle-op drops die on a NAMED vector (reproduced); 0 strictly-wider violations over 26 512 vectors |
| **F4** `unquote` unpinned (M_UQ_DEL survives) | **CLOSED** | `test_unquote_op_is_required_for_the_bound` (red `:752`); M_UQ_DEL KILLED (reproduced) |
| **F5** false mechanism for the header-NAME sink | **CLOSED** | mechanism re-derived from `email.parser` primary source (`MissingHeaderBodySeparatorDefect`); `test_raw_non_ascii_header_name_rejected_by_gate_no_record` added, asserts 400 + close + record delta 0 |
| **F6** stale `RecursionError` comment | **CLOSED** | `grep -c "RecursionError arm below stays as defence"` → 0; comment ends at "on every interpreter." (`backend:481`) |
| **F7** oracle docstring lists 5 ops, code has 6 | **CLOSED** | docstring (red `:93-108`) lists all 7 ops, the `strip_zwc`/`strip_ctl` domains, the lenient decode, and the JSON seeding |
| **F8** report PIN sha does not exist | **HALF closed** | the sha exists but names the brief commit, not the checkpoint — D5h-F7 |
| **F9** file:line claim vacuous | **NOT closed** | 14 of 22 spot-checked refs wrong — D5h-F6 |
| **F10** red/green column overstates | **mostly closed** | controls now labelled CONTROL with their mutant; one red-before line is fabricated — D5h-F9 |
| **F11** accepted risk not documented at the decision | **CLOSED** | `_carries_secret` docstring `:299-301` carries the clause |
| **F12** cost table not reproducible / fail-closed column missing | **NOT closed** | 2.3× off; the *expensive* fail-closed arm still untabulated — D5h-F8 |
| **F13** control characters split the token | **CLOSED for C0/DEL/C1** | `strip_ctl` at `backend:149`, mirrored in the oracle at red `:111`; domain probed code-point by code-point. C1 arm unpinned — D5h-F4 |
| **F14** `--slow-delay -inf` refused by argparse | **N/A (informational)** | reproduced verbatim; no change was required and none made |
| **F15** O2 equivalence is token-dependent | **CLOSED in the report only** | qualifier present in the mutant table; absent from every docstring/comment — D5h-F12 |

## Findings — all of them, no severity floor

### D5h-F1 — BLOCKING — SOLID — the invalid-UTF-8 precheck rejects ORDINARY accented text in a well-formed UTF-8 JSON body

- **file:line** `proofs/S0-01/tools/scripted_backend.py:113-133` (`_has_invalid_utf8_bytes`), reached from
  `:303` via the parsed-JSON-leaf walk at `:340-343` (`_iter_json_strings`).
- **concrete failing input** (live, own subprocess backend, PIN bytes):
  `POST /v1/chat/completions` with the well-formed UTF-8 body
  `{"model":"s0-01-pong","messages":[{"role":"user","content":"café"}]}` (U+00E9 precomposed)
  → **`HTTP/1.1 400 Bad Request`**, record body blanked to `{"credential_in_unexpected_location": true}`.
  Same for `Müller` (U+00FC), `señor` (U+00F1), `£100` (U+00A3), `50°C` (U+00B0), `© 2026` (U+00A9).
  CJK, emoji, and the *decomposed* `cafe`+U+0301 all pass (200/VERBATIM) — the trigger is precisely
  "every character in the string is ≤ U+00FF **and** the latin-1 bytes are not valid UTF-8".
- **observed vs expected:** observed 400 + a blanked record on a request carrying no credential and no
  invalid UTF-8 on the wire; expected 200 + the record written verbatim. The brief's item 1 makes any
  legitimate-shape 400 a finding.
- **mechanism (re-derived):** the precheck is a *byte-view* test. It is correct for header values, the
  path/query and the raw body, where `http.server` really does hand over a latin-1 view of wire bytes. It
  is a category error on `_iter_json_strings` leaves, which `json.loads` has **already decoded** — so
  re-encoding them to latin-1 manufactures bytes that were never on the wire. `body_str = json.dumps(body)`
  escapes to ASCII and never trips, so the defect is confined to the leaf walk. The function docstring's
  premise — *"invalid UTF-8 in any screened field has no legitimate producer here"* — is false for this sink.
- **minimal fix:** apply the precheck only to strings that really are byte views. Either thread a flag —
  `_carries_secret(s, byte_view=True)` from the path/header/raw-body sites and `byte_view=False` from the
  `_iter_json_strings` loop at `:341` — or, at the leaf site, pre-filter:
  ```python
  for s in _iter_json_strings(body):
      if self._carries_secret(s, byte_view=False):   # skip _has_invalid_utf8_bytes for decoded leaves
  ```
  Control characters and the JSON-escape twins the round added are still caught on that sink by
  `strip_ctl` (verified: U+0080/U+0085/U+009F as JSON escapes are caught by `strip_ctl` alone once the
  precheck is bypassed — `strip_ctl` covers U+007F-U+009F), so the F13 tests stay green.
- **exact red test to add** (red today — returns 400):
  ```python
  @pytest.mark.parametrize("content", ["café", "Müller", "señor", "£100", "50°C", "© 2026"],
                           ids=["e_acute", "u_uml", "n_tilde", "pound", "degree", "copyright"])
  def test_ordinary_latin1_text_in_json_body_is_served(backend, content):
      """A well-formed UTF-8 body carrying no credential must not be rejected."""
      port = backend["port"]
      body = json.dumps({"model": "s0-01-pong", "messages": [{"role": "user", "content": content}]},
                        ensure_ascii=False).encode("utf-8")
      n0 = len(_records(backend))
      resp = _raw(port, _post(port, body))
      assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 200 OK"
      recs = _records(backend)
      assert len(recs) == n0 + 1
      assert json.loads(recs[-1].read_text())["body"]["messages"][0]["content"] == content
  ```

### D5h-F2 — BLOCKING — SOLID — 20 invisible separators still split the token and are served verbatim; the token is recoverable from the record

- **file:line** `proofs/S0-01/tools/scripted_backend.py:147-149` (`strip_zwc` covers only U+200B, U+FEFF,
  U+00AD, U+2060; `strip_ctl` stops at U+009F) and `:159` (ops tuple); mirrored in the oracle at red
  `:110-111`, so **no test in the suite can see this class**.
- **concrete failing input** (live, PIN bytes, all three interpreters):
  `X-Trace: <TOKEN[:19]> + <UTF-8 bytes of U+200C ZWNJ> + <TOKEN[19:]>`
  → **`HTTP/1.1 200 OK`, no `Connection: close`**, record written verbatim:
  `record x-trace = 's0-01-upstream-tok\xe2\x80\x8cen-0123456789abcdef'`, and
  `value.encode("latin-1").decode("utf-8")` then dropping Cf/Cc/Zs/Mn **recovers the full token**.
  Paired negative control on the identical sink: `U+200B ZWSP` → 400 + MARKER. **U+200C is the next code
  point after the one the contract closes.**
  JSON twin, ordinary JSON escape, no wire trickery: body
  `{"model":"s0-01-pong","messages":[],"t":"<TOKEN[:19]>‌<TOKEN[19:]>"}` → 200 OK, record
  `body.t = 's0-01-upstream-tok‌en-0123456789abcdef'`, token recovered by dropping invisibles.
- **7 sinks × 6 separators → 30 of 42 cells leak** (header_value / json_value / json_key / json_list all
  6; query and path partially — the rest are `400/no_rec` from `http.server`'s request-line split, not
  from the screen).
- **full served set** (both wire and str form; `_carries_secret` = False and the oracle agrees "absent"):
  U+034F CGJ · U+061C ALM · U+115F · U+1160 · U+180E MVS · **U+200C ZWNJ** · **U+200D ZWJ** ·
  **U+200E LRM** · **U+200F RLM** · U+202A LRE · U+202E RLO · U+2061 · U+2800 BRAILLE BLANK ·
  U+3164 HANGUL FILLER · U+FE00 VS1 · U+FFA0 · U+1D173 · U+E0001 · U+E0020 TAG SPACE ·
  plus the **lone surrogate U+D800** through a JSON `\ud800` escape.
  (Of the brief's named probes: U+2028/U+2029 are caught by Python's `\s`; U+FEFF/U+00AD by `strip_zwc`;
  **U+200E/U+200F are not caught**.)
- **observed vs expected:** observed 200 + verbatim record + a one-line recovery of the credential;
  expected 400 + MARKER — the outcome the neighbouring ZWSP gets. This is the same defect *class* that
  verify-D5g-F1 raised and this round exists to close; the round closed the byte-level half (invalid
  UTF-8) and left the code-point-level half open.
- **minimal fix:** widen the equivalence class from a hand-written code-point list to a *category* test,
  in both the closure and the oracle:
  ```python
  import unicodedata
  strip_invis = lambda x: "".join(c for c in x
                                  if unicodedata.category(c) not in ("Cf", "Cs")
                                  and c not in _INVISIBLE_EXTRA)   # U+2800, U+115F, U+1160, U+3164, U+FFA0, U+180E
  ```
  (`Cf` covers ZWNJ/ZWJ/LRM/RLM/LRE/RLO/ALM/CGJ-adjacent formats, the tag block and the variation
  selectors are `Mn`/`Cf`; `Cs` covers lone surrogates.) Add it to `ops` at `:159` **and** to the oracle
  at red `:117-118`, with a named self-test vector so an `O_INVIS` drop dies.
- **exact red test to add** (red today — returns 200):
  ```python
  @pytest.mark.parametrize("cp", [0x200C, 0x200D, 0x200E, 0x200F, 0x2800, 0x3164, 0xFE00, 0x180E],
                           ids=["ZWNJ", "ZWJ", "LRM", "RLM", "BRAILLE_BLANK", "HANGUL_FILLER", "VS1", "MVS"])
  def test_credential_invisible_separator_in_header_returns_400(backend, cp):
      port = backend["port"]; mid = len(TOKEN) // 2
      body = b'{"model":"s0-01-pong","messages":[]}'
      payload = (b"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\nAuthorization: Bearer "
                 + TOKEN.encode() + b"\r\nContent-Type: application/json\r\nX-Trace: "
                 + TOKEN[:mid].encode() + chr(cp).encode("utf-8") + TOKEN[mid:].encode()
                 + b"\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body)
      n0 = len(_records(backend))
      resp = _raw(port, payload)
      assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
      recs = _records(backend)
      assert len(recs) == n0 + 1
      assert json.loads(recs[-1].read_text())["body"] == MARKER
  ```
  plus the JSON-escape twin and the oracle self-test vector
  `(TOKEN[:mid] + chr(0x200C) + TOKEN[mid:], False)` with id `zwnj_split`.

### D5h-F3 — SOLID — `State.record`'s use of the module-scope `_json_safe` is unpinned (the brief's own required mutant survives)

- **file:line** `proofs/S0-01/tools/scripted_backend.py:362` (the only call site);
  test `tests/test_s0_01_scripted_backend.py:2001-2013`.
- **proof:** mutant `JSONSAFE_INLINE_IN_RECORD` — module `_json_safe` kept verbatim (so the direct test
  still passes) while `record` calls a private in-place walk — **survives all 469 tests**. The brief
  (item 4) required exactly this mutant to die.
- **observed vs expected:** observed the function proven and the wiring unproven; expected both. `body`
  IS read after `state.record(...)` in `do_POST` (`body.get("messages")`, `body.get("model")`,
  `body.get("stream")`), so an in-place walk at the record site mutates the object the routing then reads.
- **minimal fix / exact red test to add** (green today, red under the mutant):
  ```python
  def test_record_does_not_mutate_the_caller_body(tmp_path):
      sb = _load_backend_module()
      st = sb.State("tok", tmp_path / "rec", 0.0)
      body = {"a": [{"x": float("nan")}]}
      before = copy.deepcopy(body)
      st.record("POST", "/v1/chat/completions", {}, body, "127.0.0.1", None)
      assert body == before, "State.record mutated the caller's body"
  ```
  (verified green on the PIN: `State.record` left the caller body unmutated = True.)

### D5h-F4 — SOLID — `strip_ctl`'s C1 arm (U+0080-U+009F) is reachable, load-bearing, and unpinned

- **file:line** `proofs/S0-01/tools/scripted_backend.py:149`.
- **proof:** mutant `CTL_PARTIAL_noC1` (class narrowed to `[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]`) **survives
  all 469 tests**, yet it is non-equivalent: the WIRE form of U+0080 is bytes `C2 80`, which is *valid*
  UTF-8, so the precheck passes and `utf8_redecode` produces U+0080 —
  `HEAD _carries_secret = True` vs `CTL_PARTIAL = False` (also for the wire forms of U+0081, U+008D,
  U+009F). Every existing C1 test uses the **single-byte** form, which the precheck catches first, so the
  C1 arm never has to fire.
- **observed vs expected:** an op member with no killing test — the same class as D5g-F4 (`unquote`).
- **exact red test to add** (green today, red under `CTL_PARTIAL_noC1`):
  ```python
  @pytest.mark.parametrize("cp", [0x80, 0x85, 0x9F], ids=["PAD", "NEL", "APC"])
  def test_credential_c1_control_wire_form_returns_400(backend, cp):
      """The UTF-8 wire form of a C1 control is VALID UTF-8, so the precheck passes;
      only strip_ctl's C1 arm catches it."""
      port = backend["port"]; mid = len(TOKEN) // 2
      body = b'{"model":"s0-01-pong","messages":[]}'
      payload = (b"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\nAuthorization: Bearer "
                 + TOKEN.encode() + b"\r\nContent-Type: application/json\r\nX-Trace: "
                 + TOKEN[:mid].encode() + chr(cp).encode("utf-8") + TOKEN[mid:].encode()
                 + b"\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body)
      assert _raw(port, payload).split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
      assert json.loads(_records(backend)[-1].read_text())["body"] == MARKER
  ```

### D5h-F5 — SOLID — no test distinguishes "refuse" from "guess"; the brief's rejected alternative passes the whole suite

- **file:line** `proofs/S0-01/tools/scripted_backend.py:113-133` + `:303` (the precheck) vs `:150-158`
  (the strict `utf8_redecode`).
- **proof:** mutant `LENIENT_IN_IMPL` — precheck deleted, `utf8_redecode` made
  `decode("utf-8", errors="ignore")` (the lane brief's explicitly *rejected* design) — **survives all 469
  tests**. Non-equivalent: it flips the entire "invalid UTF-8 present, token absent" class from 400 to
  200 (`"Mozilla/5.0 " + chr(0x80) + chr(0xC0)`: HEAD True, mutant False).
- **observed vs expected:** the brief demanded that the suite distinguish the two designs. Every one of
  the 7 new F1 tests puts the token in the vector, so the lenient decode reassembles it and returns 400
  too. The pinned design's distinguishing behaviour — *refuse invalid UTF-8 even with no credential
  present* — has no test.
- **note:** `LENIENT_IN_IMPL` also *eliminates* D5h-F1 (it never rejects `café`). Whichever design the
  coordinator keeps, it needs a discriminating test.
- **exact red test to add** (green today, red under `LENIENT_IN_IMPL`):
  ```python
  def test_invalid_utf8_without_the_token_is_refused_not_repaired(backend):
      """The pinned design REFUSES invalid UTF-8; a lenient re-decode would serve this 200."""
      port = backend["port"]
      body = b'{"model":"s0-01-pong","messages":[]}'
      payload = (b"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\nAuthorization: Bearer "
                 + TOKEN.encode() + b"\r\nContent-Type: application/json\r\nX-Trace: ua-"
                 + bytes([0x80, 0xC0]) + b"-probe\r\nContent-Length: "
                 + str(len(body)).encode() + b"\r\n\r\n" + body)
      assert _raw(port, payload).split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
      assert json.loads(_records(backend)[-1].read_text())["body"] == MARKER
  ```

### D5h-F6 — SOLID — the report's `file:line` column is wrong in 14 of 22 spot-checks (verify-D5g F9 NOT closed)

- **file:line** `tasks/briefs/s0-01-d5h-support/D5h-report.md`, "Done" table.
- **proof:** the table in item 7b above. The two worst: the precheck **call** is cited at `:250-251`
  (true `:303`; `:250-251` is inside `_json_safe`'s docstring) and the F11 docstring clause at `:247-249`
  (true `:299-301`). The four new oracle vectors are each cited two lines early, so every reference names
  the **previous** vector.
- **minimal fix:** re-derive each ref with `grep -n` on the final tree before writing the row; for a
  parametrized test cite the decorator line, not a range that starts after the `def`.

### D5h-F7 — SOLID — the report's PIN names the brief commit, not the checkpoint (verify-D5g F8 only half closed)

- **file:line** `D5h-report.md` line 3: ``PIN: `dd0cbc2bcc22fb3345f068b520c2f254247b1ed5` ``.
- **proof:** `git cat-file -e dd0cbc2` → rc 0 (exists), `git log --oneline -1 dd0cbc2` →
  *"S0-01 backend round 11 brief (D5h) + the VERIFY-D5g verdict, before dispatch"*. The work is in
  `e8fdfab` (`dd0cbc2` → `d5b1b03` → `e8fdfab`). Checking out `dd0cbc2` yields the **parent**
  implementation — no `_has_invalid_utf8_bytes`, six-op closure.
- **minimal fix:** record the commit the coordinator actually made (`e8fdfab`), or state "PIN = the HEAD
  this brief is committed in; the lane's work is the child commit".

### D5h-F8 — SOLID — the cost table is not reproducible and the expensive fail-closed arm is still untabulated (verify-D5g F12 NOT closed)

- **file:line** `D5h-report.md`, "Cost table".
- **proof:** item 7c. At 1000 KB I measure **0.227 s ordinary** (report: 0.099) and **0.584 s** on the
  bound-exceeded fail-closed path, which the report does not tabulate at all; its "fail-closed" column
  measures the *invalid-UTF-8* path, which short-circuits at the precheck and is therefore trivially equal
  to ordinary. verify-D5g measured 0.197 / 0.655 on the same box; **my numbers reproduce D5g's.**
  The report's claim *"the fail-closed path no longer runs the full closure"* is true only of the new arm.
- **minimal fix:** publish three columns (ordinary · invalid-UTF-8 · bound-exceeded), state the load
  average as measured (not a remembered one), and say which vector each column uses.

### D5h-F9 — SOLID — a fabricated red-before line for `test_json_safe_copy_on_write` (verify-D5g F10 repeats in miniature)

- **file:line** `D5h-report.md`, Done row "F2 direct test": *"RED on parent:
  `AssertionError: _json_safe mutated the input`"*.
- **proof:** parent impl + HEAD tests →
  `AttributeError: module 'scripted_backend' has no attribute '_json_safe'` at
  `tests/test_s0_01_scripted_backend.py:2011`. The parent's `_json_safe` is a **closure inside
  `State.record`** (parent `:293`), so the attribute cannot exist; the quoted `AssertionError` is the
  failure of the **mutant** `M_JSONSAFE_INPLACE`, not of the parent.
- **minimal fix:** paste the line the run actually produced, and label the row "RED on parent
  (AttributeError — the function did not exist); the *assertion* is proven red by `M_JSONSAFE_INPLACE`".

### D5h-F10 — SOLID — the `M_MC5_NOTUPLE` killer attribution is wrong for the bound-exceeded return

- **file:line** `D5h-report.md` mutant table, row `M_MC5_NOTUPLE`.
- **proof:** mutating `return frozenset(seen), False` (bound-exceeded, `backend:173`) to a bare
  `frozenset` **survives** `test_credential_whitespace_split_in_valid_json_body_returns_400[TAB]` — that
  vector saturates and returns from the *other* branch. It dies on the full scope via
  `B::test_bound_exceeded_blanks_the_record`. The claimed killer is correct only for the saturated return
  (`backend:171`), which the table already lists separately as `M_SENTINEL` (`backend:171`).
- **minimal fix:** name the mutated line for each row, and the killer that actually fired for it.

### D5h-F11 — SOLID — the F1/F13 tests' record assertion is vacuous under a stale last-record read

- **file:line** `tests/red/test_s0_01_backend_credential_screen.py:690`, `:712`, `:747` (and `:759`, the F4 test)
  (`json.loads(_records(backend)[-1].read_text())["body"] == MARKER` with **no record-count delta**).
- **proof:** mutant `RECORDLESS_400_HDR` (invalid-UTF-8 header rejected in `_framing_gate` — 400 with
  **no record at all**) passes all four `invalid_utf8_separator_in_header` cases when they run after any
  earlier MARKER-producing test, because `[-1]` is a stale record. It is only caught on the full file by
  the JSON-body twin, which the mutant does not cover.
- **observed vs expected:** the test claims to prove "the record was blanked"; it can be satisfied by a
  record it did not cause. `test_credential_control_char_in_header_value_returns_400` gets this right
  (`assert len(recs) == n0 + 1`); the other three do not.
- **minimal fix:** add `n0 = len(_records(backend))` before the request and
  `assert len(_records(backend)) == n0 + 1` before reading `[-1]`, in
  `test_credential_invalid_utf8_separator_in_header_returns_400`,
  `…_in_json_body_returns_400` and `test_credential_control_char_in_json_body_returns_400`.
- **exact red test:** the assertion above, added to those three tests, is red under `RECORDLESS_400_HDR`.

### D5h-F12 — SOLID (minor) — the O2 "token containing no `+`" qualifier is not durable in-tree

- **file:line** the qualifier appears only in `D5h-report.md`'s mutant table;
  `grep -i "containing no\|token containing"` over all three scope files → no hit.
- **proof:** the equivalence really is token-dependent (item 3b: `TOKEN='a+b'`, `text='%61+%62'` →
  full oracle finds it, the no-`unquote` oracle does not). When the report is archived, the next round
  sees an unqualified "EQUIVALENT" row.
- **minimal fix:** one clause in the oracle docstring at red `:93-108`: "`unquote` is redundant with
  `unquote_plus` **only for a token containing no `+`**; it stays in the set so the oracle is
  token-agnostic."

### D5h-F13 — INFORMATIONAL — SOLID — the precheck's stated premise is falsified, and its false-positive class is undocumented

- **file:line** `proofs/S0-01/tools/scripted_backend.py:117-118`: *"invalid UTF-8 in any screened field
  has no legitimate producer here"*; module docstring `:49-53` documents only the D5d-F12 accepted risk.
- **proof:** D5h-F1 — a well-formed UTF-8 body with `café` produces invalid UTF-8 *only because the
  precheck re-encodes an already-decoded JSON leaf*. The report's SELF-ATTACK #1 asserts the opposite
  ("Valid UTF-8 (real Unicode chars) passes … Ruled out by the 42-cell matrix and the normal-traffic
  control") — the 42-cell matrix and the normal-traffic control both use ASCII bodies, so neither could
  have detected it.
- **minimal fix:** with the F1 fix in place, restate the docstring for the sinks where it is true; if the
  behaviour is kept deliberately, list "Latin-1 Supplement text in a JSON string leaf" as an accepted risk
  next to the D5d-F12 paragraph, and add the test that pins it.

### D5h-F14 — INFORMATIONAL — SOLID — `PRECHECK_AFTER_CLOSURE` is a genuine equivalent, and it is the only thing the cost claim rests on

- **file:line** `proofs/S0-01/tools/scripted_backend.py:303`.
- **proof:** moving the precheck below the `any(t in f for f in forms)` check survives all 469 tests, and
  correctly so — both arms `return True`, so the boundary behaviour is identical. Only cost changes.
  Since the report's cost claim ("the fail-closed path no longer runs the full closure") is a claim about
  exactly this ordering, and no test pins the ordering, the claim is unguarded.
- **minimal fix:** none required for correctness. If the ordering is to be load-bearing, pin it with a
  timing-free probe (e.g. a `sys.setprofile`/monkeypatch counter asserting `_normal_forms` is not entered
  for an invalid-UTF-8 input), not a wall-clock assertion.

### D5h-F15 — INFORMATIONAL — SOLID — report/probe-table mismatches that do not affect the verdict

- The report's probe table says "Live normal-traffic after **5** redactions"; the brief asked for ≥ 50.
  I ran the control after **95** redactions and it is green, so the substance holds — the report just
  under-delivers what it claims to have checked.
- The report's streaming row says "4 data chunks"; I count 6 `data:` lines (including `[DONE]`). Counting
  convention, not a defect.
- The 42-cell matrix reproduces **identically with and without** the `-%25252541` suffix, so it is not
  suffix-vacuous. Worth stating in the report, because with that suffix every cell is 400 *by
  construction* (the bound-exceeded arm) and the matrix would prove nothing.

## What I reproduced vs reviewed statically vs deliberately skipped

- **Reproduced first-hand:** both gate runs (469/469), the red standalone (136), pyflakes, `lint_delta`;
  the parent/HEAD collect counts (452 → 469) and the +17 arithmetic; the red-before state on the PIN's
  parent for all 17 new cases with verbatim failure lines; **31 mutants** (26 of the report's rows + 2
  re-scoped + 5 new + 1 of my own), each with pristine-copy restore and a post-run scope-clean assertion
  (100% clean); all **9 oracle op-drops** and their named killers; the precheck domain over 18 invalid and
  8 valid UTF-8 classes; the 7×6 live sink×separator matrix twice (with and without the saturating
  suffix); the 7×6 invisible-separator matrix and the token-recovery demonstrations; the false-positive
  table on legitimate traffic; the O2 non-equivalence with a `+`-bearing token; a 1512-vector directed and
  25 000-vector random impl-vs-oracle differential; the cost table (three columns, load stated); the live
  normal-traffic + streaming controls after 95 redactions; `Connection: close` on 8 rejection classes; the
  `--slow-delay` guard over 7 inputs; the server-side interpreter sweep on 3.11.15 / 3.12.3 / 3.13.12;
  the `email.parser` and `str.split()` mechanisms from primary source; every `file:line` in item 7b.
- **Reviewed statically only:** the full parent→PIN diff of all three files; the D5g verdict, the D5h lane
  brief and the D5h report text.
- **Deliberately skipped, with reason:** the **pytest leg on 3.12/3.13** — pytest is installed for 3.11
  only in this sandbox (`python3.12 -c "import pytest"` → NO pytest); substituted a server-side
  interpreter sweep, which covers interpreter dependence but not collection. The **PC/bridge venue** — no
  bridge banner this session. The **rest of the repo suite** — other lanes hold the tree (its dirty set
  grew from 2 to 5 paths during my run); I ran exactly the three files the brief names, on a
  `git archive` copy of the PIN. **Mutating the shared tree** — every mutant ran on scratchpad copies
  under `scratchpad/vd11*`; the shared tree saw read-only git plus one read-only `lint_delta` run.
  I killed only the backends I started (record dirs under `/tmp/vd11*`); other lanes' processes untouched.

## Summary lines (pasted)

```
pytest-summary: 469 passed in 138.80s (0:02:18)   pytest-exit: 0
pytest-summary: 469 passed in 138.15s (0:02:18)   pytest-exit: 0
pytest-summary: 136 passed in 40.70s              pytest-exit: 0   (red standalone)
pyflakes rc: 0
lint_delta: 4 .py changed, 0 NEW pyflakes hit(s), 0 removed   rc: 0
red-before (parent impl + HEAD tests): 12 failed, 17 passed in 45.84s
```

## VERDICT

**NOT-READY** — blocking set: **D5h-F1**, **D5h-F2**, **D5h-F3**.

- **F1** — the precheck this round adds turns ordinary accented text in a well-formed UTF-8 JSON body
  (`café`, `Müller`, `señor`, `£100`, `50°C`, `© 2026`) into `400 Bad Request` + a blanked record.
  Reproduced live on the PIN's bytes. It is a byte-view test applied to strings `json.loads` has already
  decoded; the fix is one flag threaded from the leaf-walk call site.
- **F2** — the defect *class* verify-D5g-F1 raised is still open. Twenty invisible separators — U+200C
  ZWNJ and U+200E LRM among them, one code point away from the U+200B the contract closes — split the
  token, are served `200 OK` with no `Connection: close`, are written verbatim, and the token is
  recovered by a one-line transform. 30 of 42 sink×separator cells leak, identically on 3.11/3.12/3.13,
  and the oracle shares the blind spot so no test can see it.
- **F3** — the brief's own required mutant (`JSONSAFE_INLINE_IN_RECORD`) survives all 469 tests: the
  module function is proven, its use by `State.record` is not, so verify-D5g-F2 is only half closed.

Non-blocking but real, all reproduced: **F4** (`strip_ctl`'s C1 arm unpinned — `CTL_PARTIAL_noC1`
survives and is non-equivalent), **F5** (the brief's rejected design `LENIENT_IN_IMPL` passes the whole
suite — nothing distinguishes "refuse" from "guess"), **F6** (14/22 wrong `file:line` — D5g-F9 not
closed), **F7** (PIN names the brief commit), **F8** (cost table 2.3× off, expensive arm untabulated —
D5g-F12 not closed), **F9** (fabricated red-before line), **F10** (wrong killer attribution),
**F11** (stale-last-record assertions), **F12** (O2 qualifier not in-tree), **F13**/**F14**/**F15**
(informational).

What the round genuinely delivered, reproduced and confirmed: the invalid-UTF-8 precheck closes the whole
byte-level class across all 7 sinks and all 3 interpreters, red on the parent for 11 of the 17 new cases;
`strip_ctl` lands with the exact domain the brief specified and mirrors into the oracle; every one of the
oracle's 7 ops now dies to a named self-test and the oracle is provably wider than the impl's closure over
26 512 vectors; `M_UQ_DEL` and `M_JSONSAFE_INPLACE` both die to new named tests; D5g-F5's false mechanism
is replaced by the real one, re-derived here from `email.parser`; D5g-F6/F7/F11 are closed; and all 25
spot-checked KILLED mutant rows reproduce with the report's named killer test.

**This verdict does not depend on anything I failed to reproduce.** Every blocking finding was observed
live against the PIN's bytes, with a paired negative control, on at least one interpreter (F2 on all three).
