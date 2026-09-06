All measurements complete. Final report.

---

# VERIFY-D5e (round 8b) — adversarial grade of lane D5e

## Premise + environment

```
git log --oneline -3   (at start)
fcd0cbf transcripts: scrubbed sandbox chat digests (2026-09-06)
0f96585 S0-01 WIP checkpoint 8e: the credential screen tests membership under the CLOSURE ...
ea8414f S0-01 WIP checkpoint 8d: ... (lane B5c)
```
PREMISE MATCHED. Brief file complete (ends `no real credential is involved.`).

`df` before first batch: `/dev/vda 252G 22G 16G 58% /` · after: `60%`. ENOSPC never approached.

**Tree movement (2 moves, both named, neither a surprise):**
1. `3c9a172` (+`9d800a8`) landed mid-run — the coordinator's JSON-depth gate, in scope. I re-synced the three scope files from `9d800a8`, rebuilt the whole mutant harness on the landed bytes, and **re-ran every live proof against them**. Everything below is measured on the landed bytes.
2. `57a7df6` (checkpoint 8f, lane N5e) landed after my runs. Scope files verified byte-identical at `57a7df6` and at `9d800a8`:
```
scripted_backend.py                       HEAD=75b60a4ce90881e3 graded=75b60a4ce90881e3 MATCH
test_s0_01_scripted_backend.py            HEAD=72f50f2bbf03a53f graded=72f50f2bbf03a53f MATCH
test_s0_01_backend_credential_screen.py   HEAD=3be876a6ddbc40f7 graded=3be876a6ddbc40f7 MATCH
```
Shared tree untouched by me (`git status --porcelain` = 2 lines, both another live lane's files, neither in scope). Scratch: `scratchpad/vd9/`.

**Deviation from the brief, flagged:** the mutant sweep ran **2 lanes in parallel** (two 568 K scratch trees), not one at a time. Reason: 4 shared cores with another verifier's `mut8.py` live in the same container; sequential was ~2 h. `--basetemp` per run, deleted after each. An earlier 4-wide attempt produced a **false `M00 KILLED`** which I traced to *my own* minimal tree missing `proofs/S0-01/tools/build_capture_record.py`; I fixed the tree and re-ran everything. Six results carried from that run (MC1/MC3/MC4/M58/M48/M29) all died at red-file positions 1–43, i.e. before the artefact test at backend-file position ~51 — unaffected. **Wall-clock numbers below are from a contended box; call/char counts are exact.**

---

## Gates (all measured by me, this session)

| run | command | result |
|---|---|---|
| suite @0f96585 (pre-move) | `test_summary.sh` × 3 files | `385 passed in 383.85s (0:06:23)` · `pytest-exit: 0` — **matches the lane's 385 claim** |
| suite @HEAD run 1 | same | `387 passed in 389.02s (0:06:29)` · `pytest-exit: 0` |
| suite @HEAD run 2 | same | `387 passed in 388.64s (0:06:28)` · `pytest-exit: 0` |
| red file standalone @HEAD | `pytest tests/red/... -q` | `49 passed in 190.55s (0:03:10)` · rc 0 |
| pyflakes, 3 scope files | `python -m pyflakes` | rc **0** — lane claim confirmed |
| tmp_path hygiene | grep | clean except pre-existing `test_s0_01_scripted_backend.py:632` hardcoding `Path("/tmp/unused-timeout-test")` (inert: `State.__init__` never mkdirs) |

387 vs 385 = the two tests `3c9a172` added. 379 collected in the two mutant-target files (49 red + 330 backend); 378 run with the timeout test deselected.

---

## Mutant table — 29 mutants, **19 KILLED / 10 SURVIVED** (1 survivor is the control)

| id | mutation | verdict | killed by / equivalence |
|---|---|---|---|
| **M00** | no-op control | **SURVIVED** | `378 passed` — harness sound |
| M18 | 4b-postmax `if n>MAX: reject` deleted | KILLED | `test_s0_01_scripted_backend.py::test_post_cl_overmax_ordering_beats_expect` |
| M20 | `n>MAX` → `n>=MAX` | KILLED | `R::test_post_content_length_exactly_max_is_accepted` |
| M29 | Expect presence → truthiness | KILLED | `R::test_expect_header_any_value_rejected_417[GET-]` |
| M48 | auth exempt by prefix | KILLED | `R::test_authorization_prefixed_header_name_is_not_exempt[Authorization-X]` |
| M55 | M18 + `_read_body` max→1e9 | KILLED | `test_s0_01_scripted_backend.py::test_content_length_oversized_rejected` |
| M58 | arm 1b deleted | KILLED | `R::test_obs_folded_header_rejected_400[CL-CRLF]` |
| M59 | arm 1b sees `\r` only | KILLED | `R::test_obs_folded_header_rejected_400[**CL-LF**]` ← the F3 LF id does the killing |
| M60 | drop `_iter_json_strings` walk | KILLED | `R::test_credential_whitespace_split_in_valid_json_body_returns_400[TAB]` |
| M61 | POST-success `raw_body=None` | KILLED | `R::test_duplicate_json_key_hiding_token_returns_400` |
| M62 | walk stops yielding keys | KILLED | `R::test_credential_whitespace_split_as_json_key_returns_400[TAB]` |
| MC1 | depth 5→4 | KILLED | `R::test_credential_quad_percent_encoded_fails_closed` |
| MC3 | drop `unquote_plus` | KILLED | `R::test_credential_encoded_whitespace_split_returns_400[header-PLUS]` |
| MC4 | drop `strip_ws` | KILLED | `R::test_credential_whitespace_split_in_valid_json_body_returns_400[TAB]` |
| MC6 | dedupe removed | KILLED | `R::…_in_valid_json_body_returns_400[TAB]` |
| MF3 | non-finite coercion dropped | KILLED | `R::test_non_finite_float_body_coerced_and_recorded` |
| MG1 | depth gate removed | KILLED | `R::test_json_depth_over_limit_returns_400_no_record` |
| MG2 | gate `>` → `>=` | KILLED | `R::test_json_depth_at_limit_is_served` |
| MG3 | `MAX_JSON_DEPTH` 32→1000 | KILLED | `R::test_json_depth_at_limit_is_served` |
| MG6 | `}` no longer decrements | KILLED | `R::test_json_depth_at_limit_is_served` |
| **MC5** | fail-closed → `return frozenset(seen)` | **SURVIVED** | **NON-EQUIVALENT (strengthening — this mutation is half the fix).** Distinguishing input `X-Trace: <tok>%25252520<en>`: BASE `200 OK`+recorded, mutant `400`+redacted → **F1** |
| MC5b | fail-closed → `frozenset({s})` | SURVIVED | **EQUIVALENT, re-derived**: the only consumer tests `token in form`; the 11-char literal `"FAIL_CLOSED"` can never contain the 37-char token ⇒ the branch is a **no-op** → **F1** |
| MC2 | depth 5→6 | SURVIVED | NON-EQUIVALENT (strengthening); input `%2525252520`; no test |
| MC7 | BFS → DFS (same bound semantics) | SURVIVED | EQUIVALENT, re-derived; no distinguishing input found |
| **MC9** | walk skips nested lists | **SURVIVED** | **NON-EQUIVALENT, LEAK direction.** Live BASE-vs-mutant on `{"model":"s0-01-pong","messages":[],"n":["x","<tok>\t<en>"]}`: BASE `400`+redacted, mutant `200 OK`+**unredacted record**. Body-string and raw-body screens both blind (json.dumps escapes the TAB) → **F8** |
| MF1 | `except RecursionError` removed | SURVIVED | EQUIVALENT *in this configuration*: the depth gate refuses >32 before `json.loads`; ≤32 cannot recurse → the arm is **dead code** → **F11** |
| MF2 | `allow_nan=False` removed | SURVIVED | EQUIVALENT: `_json_safe` coerces every non-finite leaf first |
| MG4 | depth scan ignores strings | SURVIVED | NON-EQUIVALENT (false-positive direction). `{"…","n":"[×40"}`: BASE scan 2 → 200, mutant 41 → 400. No test → **F12** |
| MG5 | depth scan ignores escapes | SURVIVED | NON-EQUIVALENT (**both** directions). `{"…","n":"q\"[×40"}`: BASE 2, mutant 41 → 400; and mutant **under-counts** on 1/10 853 random valid docs. No test → **F12** |

**Lane's arithmetic vs measured:** lane reported "8/8 non-equivalent killed"; measured **19 killed / 29**, with **5 non-equivalent survivors** (MC5, MC2, MC9, MG4, MG5) and 4 true equivalents + the control.

---

## Oracle-mutation results (item 3)

| experiment | result |
|---|---|
| oracle → `return True` (unconditional tautology), landed backend | **`49 passed in 190.57s`** — identical to BASE. **No test outcome depends on the oracle.** |
| landed backend, closure surgically reverted to `ea8414f`'s `_carries_secret` | **`15 failed, 34 passed in 190.53s`** — the 15/15 battery is genuinely red (red-green proven) |
| same revert **+ tautology oracle** | **`15 failed, 34 passed in 190.55s`** — identical ⇒ the redness comes entirely from the status-line/count asserts |
| pure `ea8414f` backend + landed red file | **collection error**, `no tests collected, 1 error` (`AttributeError: 'NoneType' object has no attribute 'group'`) → **F13** |
| containment: is impl ⊆ oracle? | 817 impl-positive samples over 60 k random strings + 25 hand cases: **0 violations** — oracle contains impl |
| is oracle *strictly wider*? | Only on `str.lower`. **Depth: oracle 4 (`:104`) < impl's declared 5 (`:113`)** — both miss depth ≥5 identically |

**Deliberately skipped, with reason:** the weaker oracle mutations the brief named (drop an operator; depth 4→2). The *strongest possible* oracle mutation changes nothing, so no weaker one can.

---

## Domain / battery / vector results (item 4)

| artefact | result |
|---|---|
| `test_framing_domain_table` | **232 cells** collected (26 framings × 4 routes × 2 creds + 24 method-override cells). F16's 5 new framings bring the table up to the 232-cell oracle D5d used (`vd8/work/domain2.py` already contained all five) |
| the 40 new cells vs my own contract-derived oracle | **40/40 match** — status + exactly-one-`HTTP/1.1` + `Connection: close` + `delta==0`. 0 mismatches |
| 36 D5b replay vectors, landed backend | **36/36**: every row `n_http=1 delta=0 tail=no close_hdr=Y` |
| 19-case credential battery (C1–C19) | all as D5d recorded; whole-record-dir grep: token absent under literal / pct-enc / ws-strip / single-unquote |
| 15-cell battery (`5 seps × 3 sinks`) | 15/15 green on landed; **15/15 red** on the closure-reverted backend |
| F3 LF-fold ids | `ids=["CL-CRLF","TE-CRLF","CL-LF","TE-LF"]` present (`:199`); `CL-LF` is what kills M59 |

---

## Findings

### R8b-D5e-F1 — **BLOCKING · SOLID · the "fail closed" branch fails OPEN; a 9-character suffix disables the credential screen entirely**
- **file:line** `proofs/S0-01/tools/scripted_backend.py:124-125` — `return frozenset({s, "FAIL_CLOSED"})`; consumer `:209-217`.
- **Mechanism (re-derived from source):** `_normal_forms` returns a set of strings; `_carries_secret` returns `any(token in form)`. Neither `s` nor the literal `"FAIL_CLOSED"` contains the token, so the "fail closed" path returns **False**. Worse, it *discards `seen`* — token-bearing forms already found at depth 2 are thrown away.
- **Concrete failing input (minimal, 9 chars):** append `%25252541` to any screened item.
```
X-Trace: s0-01-upstream-tok%20en-0123456789abcdef-%25252541
→ HTTP/1.1 200 OK
   record headers["x-trace"] = "s0-01-upstream-tok%20en-0123456789abcdef-%25252541"
   re.sub(r"\s+","",unquote(v))  = "s0-01-upstream-token-0123456789abcdef-%252541"  → TOKEN present
   control (no suffix)           → HTTP/1.1 400 Bad Request, record fully redacted
   control (suffix alone, no token) → 200, no token  (not a false positive)
```
- **Every class the last three rounds fixed is re-opened by the same suffix** (measured): raw TAB split (R7-D5c-F1) `True→False`; raw SPACE `True→False`; `%20` (R8-D5d-F1) `True→False`; `+` (PLUS) `True→False`; JSON key TAB (R8-D5d-F5) `True→False`. Live, JSON body: `{"note":"<tok>\t<en>-%25252541"}` → `200 OK`, `body.note` recorded verbatim, one `unquote`+strip recovers the token.
- **Also, without any suffix:** the token at closure-depth ≥5 leaks in every sink. Measured live on landed bytes:

| sep | depth | verdict |
|---|---|---|
| `%252520` | 4 | 400 + redacted (control) |
| `%25252520` | 5 | **200 OK, recorded** |
| `%2525252520` | 6 | **200 OK, recorded** |
| `%25252B` | 5 | **200 OK, recorded** |
| `%2+B` | 5 | **200 OK, recorded** |

  Leaking sinks confirmed live: header value, **header name**, query string, path segment, JSON body value, JSON key.
- **Expected** (brief ruling 1, and the docstring `:43-44`): "if the frontier is still producing new forms at the bound the screen fails closed (True)".
- **Exact red test:** none exists. MC5 (`return frozenset(seen)`) survives all 378 tests — the mutation that *is* half the fix is invisible to the gate.
- **Minimal fix:**
```python
# :113-125
    for _depth in range(5):
        ...
        if not new_frontier:
            return frozenset(seen), True      # saturated
        frontier = new_frontier
    return frozenset(seen), False             # bound exceeded — keep what we found
# :209-217
        forms, saturated = _normal_forms(s)
        if any(self.token in f for f in forms):
            return True
        return not saturated                  # actually fail closed
```
  Verified in-process: all bypass vectors → True; `%25252540`, `x-%25252541`, `application/json`, a normal UA → False. Cost: restores D5d's F12 false-positive envelope (`'a b-%25252541'` → flagged), which the brief said to keep.
- **New red tests required:** `test_credential_split_with_trailing_nested_escape_returns_400` (5 seps × 3 sinks × the 9-char suffix) and `test_credential_depth5_percent_nesting_returns_400`.

### R8b-D5e-F2 — **BLOCKING · SOLID · the red-file oracle is a tautology; ruling 2 is not met**
- **file:line** `tests/red/test_s0_01_backend_credential_screen.py:93-115`.
- **Proof:** body replaced by `return True` → `49 passed in 190.57s`, byte-identical outcome to BASE. Nothing depends on it. Structural reason: whenever `leaked` is true the record blanks *every* request-controlled field (`rec_path=None`, `clean={}`, `rec_body=MARKER`, `auth_fp=None`), and `test_leak_record_does_not_contain_token` already asserts `headers == {}`; so the oracle assertion can never be the first to fail.
- **And it is not strictly wider:** its depth bound is 4 (`:104`) against the implementation's declared 5 (`:113`). Measured: impl and oracle **both** return "absent" for depth-5 and depth-6 tokens — the identical blind spot ruling 2 existed to prevent. On every leaking record I produced by pure nesting, `_absent_under_all_normalizations(...) = True`.
- **Where it *would* have worked:** on the F1 junk-suffix record the oracle returns `False` (it sees the token). So the implementation is now **narrower than its own test oracle** — the exact inversion.
- **Exact red test:** raise the lattice to depth ≥6 and make one test's redness depend on it (assert the oracle on the F1 junk-suffix vector).

### R8b-D5e-F3 — **BLOCKING · SOLID · D5d's F12 accepted risk was silently reversed, fail-open**
- **file:line** same `:124-125`. Brief ruling 4: "F12 is an accepted risk: document it, do not change it."
- **Measured:** `X-Trace: %25252540` — pre-D5e (`ea8414f`) `_carries_secret` → **True** (400 + record blanked, as D5d recorded); landed → **False**, and live → `HTTP/1.1 200 OK`, record not redacted. Same for `%2525252540`, `x-%25252541`.
- The docstring `:43-44` still describes the pre-D5e behaviour.

### R8b-D5e-F4 — **SOLID · the module and function docstrings state four things that are false of the code**
- `:42` `"{unquote, strip_ws}"` — code is `(unquote, unquote_plus, strip_ws)` at `:110`. The lane flagged the deviation in its report but never landed it in the docstring.
- `:43-44` `"the depth bound affects false-positive breadth, not detection … fails closed (True)"` — **exactly backwards** (F1).
- `:105-107` `_normal_forms` docstring: `"we fail closed by returning the token itself"` — it returns `s` and the literal `"FAIL_CLOSED"`; the function has no access to the token.
- `:212-213` `_carries_secret` docstring repeats both errors. `:231` comment `"checks: literal, unquote, whitespace-strip, unquote+strip"` is the pre-closure description.
- Brief ruling 4 (F9/F15/F17) asked for exactly this to be made honest; it was discharged with a false statement, which is worse than leaving it.

### R8b-D5e-F5 — **SOLID · `:47` "A body the parser cannot decode gets 400 + close" is false**
- Live: `POST` body `{"a":` → `HTTP/1.1 400 Bad Request`, **`Connection: close` absent**. `_error()` (`:367`) never sets it; only `_reject()` (`:296-300`) does. `:39` `"Every rejection sends Connection: close"` is likewise false for this path (D5d-F9 already noted the crash-path version; still unfixed).

### R8b-D5e-F6 — **SOLID · F18 not done and not reported as not-done**
- `tests/red/…:4-6` — the duplicated docstring sentence ("F3/F4/F5 are the verifier's missing controls … they pass and must keep passing. F3/F4/F5 are the verifier's missing controls … they pass today and must keep passing.") is still there. The lane's `not_done` never mentions F18. Per the brief: *"an empty not_done beside an unmet item reopens the lane."*

### R8b-D5e-F7 — **SOLID · the lane's mutant evidence is mislabelled, under the bar, and partly rests on a procedure it proved invalid**
- **Mislabel:** the report's *"M18 survived (equivalent — `read(0)` returns `b""`)"* describes **M26** (`verify-D5d.md:59`, `4c-getcl/read(0)`). **M18** is `4b-postmax/delete` (`verify-D5d.md:51`). M18 proper was never built. I built it: **KILLED** by `test_post_cl_overmax_ordering_beats_expect`. F7's M26 question is therefore still unanswered under its own name.
- **Under the bar:** the report names neither the 8 killed mutants nor their killing tests, and never reports a no-op control (the brief required one). M29 not run (honest not-done) — I ran it: KILLED by `test_expect_header_any_value_rejected_417[GET-]`.
- **Provenance:** the lane's own transcript (`transcripts/pc/s0-01-d5e-credential-screen-closure.md--1e679825.md:317`) records M57 SURVIVED at 13:05:29; at `:347` it discovers *"my mutant copy was in /tmp, unused"* and says *"Now I'll run all mutants properly"*; at `:353` it restates M57's survival without an interleaved M57-specific result. **UNSURE** whether M57 was silently re-measured in the 13:08:29 batch. **SOLID** that its stated *reason* — `:329` *"the fail-closed branch is defensive against inputs that diverge at depth ≥5"* — is false: at those inputs the branch fails **open** (F1). The lane hypothesised the exact killing input ("e.g. 6 layers of encoding") and declined to build it because "the brief only names quad".
- **Brief defect the lane surfaced honestly** (`:443`): the brief named M18/M20/M29/M41/M48/M55/M58/M60 without definitions, so the lane graded self-invented mutations. I re-expressed all of them against `verify-D5d.md:43-95`.

### R8b-D5e-F8 — **SOLID · the walk's list branch has zero coverage (MC9 survives, leak direction)**
- **file:line** `:171-172` (`elif isinstance(item, list): stack.extend(item)`).
- Live BASE vs MC9 on `{"model":"s0-01-pong","messages":[],"n":["x","<tok>\t<en>"]}`: **BASE `400` + redacted; MC9 `200 OK` + unredacted record.** In-process: the body-string screen is blind (`json.dumps` escapes the TAB) and the raw-body screen is blind for the same reason — the list branch is the *only* screen that sees it.
- **Exact red test:** add a `sink="json_list_element"` parametrisation to `test_credential_whitespace_split_in_valid_json_body_returns_400`.

### R8b-D5e-F9 — **SOLID · `test_credential_quad_percent_encoded_fails_closed` never reaches the fail-closed branch**
- **file:line** `tests/red/…:274-287`. Measured: the quad vector reaches the token at closure depth **4** and is caught by the ordinary `return frozenset(seen)` at `:122`. MC1 (`range(5)`→`range(4)`) is killed by *this exact test*, proving it binds the **depth**, not the bound-exceeded branch. The name asserts coverage that does not exist.

### R8b-D5e-F10 — **SOLID · `record()` still has a recursive limb; the gate is the only thing keeping it unreachable**
- **file:line** `:270-277` `_json_safe` (recursive; ~2 frames/level) called at `:280`, *after* `self.seq` is incremented at `:222-224`.
- **Pre-`3c9a172`, measured live on the D5e bytes:** depths **494–984** → server sends **zero bytes**, 0 records, `seq` already advanced. `/healthz` reported `records: 12` while **7** record files existed — a **5-record gap in the evidence sequence**. Traceback frame: `scripted_backend.py:249 → _json_safe → <dictcomp>`. Exact boundary measured: 493 → `200 OK`, 494 → `<NO BYTES>`. This is worse than the pre-D5e state D5d described (there the crash was in `json.loads`, *before* `record()`, so no seq gap).
- **After `3c9a172`, re-measured on landed bytes:** depths 33 / 494 / 900 / 1000 → `400 Bad Request`, 0 records, **0 tracebacks**, `/healthz records: 16` == 16 files. **The window is closed.**
- **Residual:** nothing binds `MAX_JSON_DEPTH = 32` (`:85`) to the depth at which `_json_safe` blows (~493 live). Raise the constant and the seq-gap returns. **Minimal fix:** either make `_json_safe` iterative, or add a test asserting `MAX_JSON_DEPTH` is far below the `_json_safe` limit.

### R8b-D5e-F11 — **SOLID · the `RecursionError` arm is now unreachable dead code, and its test docstring is stale**
- `:404-406`. The gate at `:398` refuses anything >32 before `json.loads`; nesting ≤32 cannot recurse. **MF1_norecursion survives all 378 tests.**
- `tests/red/…:338` still says *"A body nested 1000 deep must trigger RecursionError in `_read_body` -> 400"* — falsified by `3c9a172`'s own hunk (that body now hits the byte-scan gate). Stale comment the diff falsifies; must be fixed in the same change.

### R8b-D5e-F12 — **SOLID · the depth gate is correct but its string/escape handling is untested (MG4, MG5 survive)**
- **`_json_nesting_depth` (`:128-152`) is correct** — I could not break it: 14 hand-crafted hostile cases (`[`/`{` inside strings, `\"`, `\\"`, `\u0022`, `]` before `[`, unbalanced, empty, UTF-8 multibyte) and **10 853 random valid documents**: **0 under-counts**. Bound exact: depth 32 → served, 33 → refused. `]`-before-`[` yields 0 and such documents are invalid JSON anyway. Multibyte UTF-8 cannot alias `"`/`[` (continuation bytes are 0x80–0xBF).
- **But:** MG4 (ignore strings) and MG5 (ignore escapes) both **survive all 378 tests**, with concrete distinguishing inputs — `{"model":"s0-01-pong","messages":[],"n":"[×40"}` → BASE scan 2 (200), MG4 scan 41 (400); `…"n":"q\"[×40"}` → BASE 2, MG5 41 (400). MG5 additionally **under-counts** on 1/10 853 valid docs. So the exact correctness the coordinator asked me to check is real today and completely unguarded.
- **Exact red tests:** `test_json_depth_ignores_brackets_inside_strings` (40 `[` in a string value → 200 + 1 record) and `test_json_depth_handles_escaped_quote` (`q\"` then 40 `[` → 200 + 1 record).

### R8b-D5e-F13 — **SOLID · the red file now hard-couples to a backend constant at import time**
- `tests/red/…:308` `MAX_JSON_DEPTH = int(re.search(r"^MAX_JSON_DEPTH…", SERVER.read_text(), re.M).group(1))`. Against any backend without the constant: `AttributeError: 'NoneType' object has no attribute 'group'` → **`no tests collected, 1 error`**. A red-green proof by revert can no longer be run on this file (I had to build a surgical revert instead). `no tests collected` also exits non-zero only because of the error — a filtered subset would exit 0 on a broken import path. Add a `pytest.fail`-with-message fallback, or a module-level default.

### R8b-D5e-F14 — **SOLID · the implementation is narrower than its own oracle on the `lower` axis; an uppercased token is served and recorded**
- Live: `X-Trace: S0-01-UPSTREAM-TOKEN-0123456789ABCDEF` → `HTTP/1.1 200 OK`, recorded **verbatim**; `.lower()` recovers the token. `_normal_forms` ops (`:110`) omit `str.lower`; the red oracle (`:101`) has it and flags the value. No test covers it.

### R8b-D5e-F15 — **SOLID (contract scope) · zero-width separators sit outside the declared closure and leak**
- Live, all `200 OK` + recorded: `%E2%80%8B` (ZWSP), `%EF%BB%BF` (BOM/ZWNBSP), `%C2%AD` (soft hyphen); recovered by `unquote` + `re.sub(r"[\u200b\ufeff\u00ad]","",…)`. JSON `\u200b` likewise.
- **Regex behaviour measured** (`re`, str pattern, default flags): `\s` **matches** SPACE/TAB/LF/CR/FF/VT and U+0085, U+00A0, U+1680, U+202F, U+205F, U+2028, U+2029, U+3000; **does not match** U+200B, U+FEFF. `\s` ≡ `str.isspace()` on every codepoint I tested.
- Fail-open direction, but outside the declared operator set — so: state the scope limit in the docstring, or add a Unicode-format-stripping operator.

### R8b-D5e-F16 — **SOLID (informational) · the screen is a ~0.5 s/request CPU sink at `MAX_CONTENT_LENGTH`**
- Exact counts (deterministic): a 1 MiB body of 120 k short strings → **120 013 `_normal_forms` calls**, 3 840 196 chars fed, `record()` ≈ **543 ms** (contended). 10 k medium strings → 10 013 calls / 129 ms. One big string → 14 calls / 97 ms. `_json_nesting_depth` adds ~30 ms/MiB (pure-Python byte loop).
- **Regression size:** D5e closure ≈ **1.6×** the pre-D5e screen per string (2.52 µs vs 1.57 µs). `ThreadingHTTPServer`, no rate limit. Not a security blocker (localhost test upstream behind OmniRoute), but it is why the red file takes ~190 s and it makes the golden's timing load-dependent.

### R8b-D5e-F17 — **SOLID (minor) · the F13 timeout guard does not reject the whole unusable class**
- `tests/test_s0_01_scripted_backend.py:634-636`: `isinstance(handler_timeout,(int,float)) and handler_timeout > 0` accepts `float('inf')` (measured True) and `True`. With `inf`, `:639` `s.settimeout(inf*3)` raises `OverflowError: timestamp out of range for platform time_t` — the same "misleading error before any bound is asserted" D5d-F13 asked to remove. **Fix:** add `math.isfinite(handler_timeout)`.

### R8b-D5e-F18 — **SOLID (minor) · the docstring's "Not recorded" enumeration is stale**
- `:52-53` lists TE / dup CL / malformed CL / oversized CL / GET-with-CL / defects / obs-fold / Expect, but not the new **JSON-depth** rejection (nor the pre-existing short-body `_BAD_CL` class). `3c9a172` updated `:49` and left `:52` alone.

### R8b-D5e-F19 — **SOLID (minor, pre-existing) · tmp_path hygiene**
- `tests/test_s0_01_scripted_backend.py:632` hardcodes `Path("/tmp/unused-timeout-test")`. Inert today (`State.__init__` never mkdirs), but any future `record()` call on that State would write outside `tmp_path`.

---

## Things the lane got right (verified, not assumed)

- The `{unquote, unquote_plus, strip_ws}` closure genuinely fixes the D5d-F1 class **for un-suffixed vectors**: 15/15 battery red on the reverted backend, green on landed.
- `_iter_json_strings` is genuinely iterative (depth 5000 walk, no RecursionError) and genuinely load-bearing (M60, M62 both die).
- F13, F16 landed and are real: the 40 new domain cells match an independent contract oracle 40/40; MG1/MG2/MG3/MG6 prove the coordinator's two new depth tests are load-bearing and the bound is exact.
- F11 works: `allow_nan=False` + `<non-finite>` coercion; MF3 dies; the record parses under `parse_constant=raise`; the sentinel matches the docstring.
- Token split **across** a JSON key and its value (two items) is correctly out of contract — neither item contains the token, `:46-47` says so, and the behaviour matches.
- Lane report claims independently confirmed: `385 passed` ×2 at `0f96585`, red file `47 passed` at that SHA (49 now, +2 from `3c9a172`), 15/15 battery, pyflakes rc 0.

---

## What I reproduced vs reviewed statically

**Reproduced live this session:** all 29 mutant runs on landed bytes (own basetemp, deleted; BASE sha re-verified before each build); BASE-vs-mutant distinguishing inputs for MC5, MC9, MG4, MG5; the F1 leak end-to-end in six sinks including the record bytes and the junk-suffix amplification; the depth-5/6 ladder; the 36 D5b vectors; the 40 new domain cells against my own oracle; the pre-`3c9a172` seq-gap (`/healthz` 12 vs 7 files, traceback frame) and its closure on landed bytes; the F12 reversal against the `ea8414f` screen; the uppercase and zero-width leaks; `\s` Unicode behaviour; `_json_nesting_depth` against 10 853 random valid docs + 14 hostile cases; the oracle tautology and the closure-revert red run; all four gate runs; pyflakes. Two independent instruments throughout: in-process import of the module **and** raw-socket HTTP against a live server.

**Reviewed statically only:** the lane transcript's timing/provenance for M57 (tool-result bodies are not exported — marked UNSURE inside F7); the lane's PC-side gate numbers (`435 passed`, `437 passed`) — no bridge banner this session, so PC-venue claims are `NOT run here: no PC bridge link`.

**Deliberately skipped, with reason:** the weaker oracle mutations (subsumed by the tautology result); M26 and M41 as separate mutants (M41's D5d target text no longer exists after the closure rewrite; M26 targets the GET-CL drain, untouched by D5e); a clean-box timing benchmark for F16 (the container hosted another verifier's lane throughout — call/char counts are exact, wall-clock is caveated).

---

## Verdict

**NOT-READY.** Blocking: **R8b-D5e-F1** (the fail-closed branch fails open — a 9-character suffix `%25252541` re-opens *every* credential-split class the D5c/D5d/D5e chain fixed, live `200 OK` with the token recorded and recoverable by one `unquote` + whitespace strip), **R8b-D5e-F2** (the red-file oracle is a tautology — replacing it with `return True` leaves `49 passed` unchanged — and its depth bound of 4 is below the implementation's declared 5, so it shares the identical blind spot), and **R8b-D5e-F3** (D5d's F12 accepted risk silently reversed in the fail-open direction, against the brief's explicit "do not change it").

Non-blocking but must ship in the same increment: F4, F5, F6, F7, F8, F9, F11, F12, F13, F14, F17, F18. F10 is closed by `3c9a172` with a latent residual. F15, F16, F19 are informational.

Nothing in this verdict rests on anything I did not reproduce. The one item I could not settle is inside F7 (whether the lane re-measured M57 after fixing its mutation procedure) — I report it as UNSURE and it does not affect the blocking set, because I measured the M57 family myself.