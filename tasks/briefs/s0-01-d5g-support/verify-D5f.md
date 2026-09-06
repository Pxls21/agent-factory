# VERIFY-D5f — round-9 adversarial grade of lane D5f (backend credential screen)

VERDICT: **NOT-READY** — blocking **R9-D5f-F1, F2, F3, F5**.
F2 is a reproduced credential leak in the shipped code; F1 is a reproduced leak under a mutant the
binding ruling explicitly named and no test defends; F3 and F5 are contract items the report claims
as done that are false when executed. Everything in this verdict was reproduced by me except where a
finding says "reviewed statically".

## Premise

| item | value |
|---|---|
| PIN | `2a75655f159b2301dfcbd251fe79755765b8dfb1` ("S0-01 WIP checkpoint 8h: … lane D5f") |
| shared-tree HEAD at dispatch | `2a75655` = PIN ✓ |
| shared-tree HEAD at report time | `e84b7ef` — **18 commits past the PIN** (other lanes: 8i/8j, pc_suite, transcript scrub, …) |
| D5f scope files | byte-identical at PIN, at `e84b7ef`, and in the live worktree (blob-compared) — **the verdict applies to what is live** |
| my copy | `git archive <PIN-tree> \| tar -x` → `…/scratchpad/vd9/repo`; all 5 brief files blob-verified `== PIN` |
| interpreter | `/usr/local/bin/python3` = 3.11.15 (venv `/root/venv-agent-factory` is the same 3.11.15) |
| `df -h /` | `/dev/vda 252G 23G 15G 62% /` (before first batch; unchanged at close) |
| shared tree | read-only git commands only; never restored/stashed/checked-out; I wrote nothing to it |
| copy hygiene | `git status --porcelain` on the copy EMPTY before and after every batch; all 3 scope md5s == pristine at close |

Procedural note (R9-D5f-F13): the scratchpad path `…/scratchpad/vd9/repo` was **pre-populated** by an
earlier round (stale `__pycache__` dated 13:56, before my extraction). I deleted and re-extracted, then
proved the copy has exactly the archive's 10014 entries and no strays.

## Gate runs (mine, this session, pasted verbatim)

```
RUN 1  442 passed in 133.37s (0:02:13)      pytest-exit: 0
RUN 2  442 passed in 133.10s (0:02:13)      pytest-exit: 0
RED FILE STANDALONE  104 passed in 40.43s   pytest-exit: 0
FINAL (post-mutation integrity)  442 passed in 133.83s (0:02:13)   pytest-exit: 0
pyflakes (3 files) rc: 0
```
Suite RAN, not filtered-to-nothing: collection is 330 + 104 + 8 = **442** ✓ and the no-op control
mutant M00 reproduced the same split (104 red-file + 338 other-files).

## Red-green (I reverted the BACKEND ONLY to the PIN's parent and kept the HEAD tests — the brief's
literal "swap all three files" is a no-op that proves nothing)

PIN parent = `95998f1`. Backend `554` lines (md5 `0f036b3d…`) vs PIN `586` lines (md5 `35fb2ec8…`).

```
RED   (parent backend + HEAD tests)   49 failed, 385 passed in 625.92s (0:10:25)
GREEN (PIN)                           442 passed in 133.83s
```
Reconciled exactly: 40 red-file failures + 9 backend-file failures = 49.

| new/changed test | red on parent | note |
|---|---|---|
| `test_credential_depth5_percent_nesting_returns_400` | 20/20 | genuinely red |
| `test_credential_split_with_trailing_nested_escape_returns_400` | 15/15 | genuinely red |
| `test_credential_zero_width_pct_encoded_returns_400` | 3/3 | genuinely red |
| `test_credential_zero_width_json_escape_returns_400` | 1/1 | genuinely red |
| `test_credential_uppercased_token_in_header_returns_400` | 1/1 | genuinely red |
| `test_framing_domain_table` (F5 close=True) | 9 params | genuinely red |
| `test_credential_whitespace_split_in_json_list_element_returns_400` | 0 | never red — mutant-killer only (kills MC9 ✓) |
| `test_json_depth_ignores_brackets_inside_strings` / `…handles_escaped_quote` | 0 | never red — kill MG4/MG5 ✓ |
| `TestOracleSelfTests::test_oracle_known_vectors` | 0 | never red — kills O1 only (see F5) |

## Table 1 — F1 vector `TOKEN[:mid] + sep + TOKEN[mid:] + "-%25252541"`, 7 sinks × 5 separators

Live, real subprocess, real record dir. **35/35 = `HTTP/1.1 400 Bad Request` + record `REDACTED`.**

| sink \ sep | %20 | %09 | %0A | %0d | + |
|---|---|---|---|---|---|
| header_value | 400/RED | 400/RED | 400/RED | 400/RED | 400/RED |
| **header_name** | 400/RED | 400/RED | 400/RED | 400/RED | 400/RED |
| query | 400/RED | 400/RED | 400/RED | 400/RED | 400/RED |
| path | 400/RED | 400/RED | 400/RED | 400/RED | 400/RED |
| json_value | 400/RED | 400/RED | 400/RED | 400/RED | 400/RED |
| json_key | 400/RED | 400/RED | 400/RED | 400/RED | 400/RED |
| json_list | 400/RED | 400/RED | 400/RED | 400/RED | 400/RED |

**Control (no `-%25252541` suffix), same 35 cells: 35/35 400 + REDACTED.** The marker record is written
each time and normal traffic afterwards is unaffected (Table 7 below). R1's decision is correct as shipped.

## Open item (a) — the depth-5 vector in a header NAME: **PROBED LIVE, the lane's fear is falsified**

| vector | header NAME | header value |
|---|---|---|
| `%25252520` | 400 + REDACTED | 400 + REDACTED |
| `%2525252520` | 400 + REDACTED | 400 + REDACTED |
| `%25252B` | 400 + REDACTED | 400 + REDACTED |
| `%2+B` | 400 + REDACTED | 400 + REDACTED |
| raw TAB / raw SP in a name | 400, **no record** (framing gate: `headers.defects`) | n/a |

`%`, `+`, digits and letters are all RFC 9110 `tchar`, so these names parse cleanly and reach the screen.
The screen handles all four. The lane's stated reason for omitting the sink ("percent-encoded characters
in HTTP header names may cause parser-level defects that trigger the framing gate before the credential
screen runs") is **false** — see R9-D5f-F8.

## Table 2 — oracle-wider probes (is the oracle strictly wider than the implementation?)

`served` = 200 OK and the value recorded verbatim. `oracle` = `_absent_under_all_normalizations(record_text)`.

| vector | sink | backend | oracle on the record |
|---|---|---|---|
| NBSP U+00A0 split (JSON) | json_value | 400 REDACTED | ABSENT |
| ideographic space U+3000 (JSON) | json_value | 400 REDACTED | ABSENT |
| ZWSP / BOM raw in JSON | json_value | 400 REDACTED | ABSENT |
| VT raw in JSON | json_value | 400 REDACTED | ABSENT |
| uppercased token | header_value | 400 REDACTED | ABSENT |
| double `+` | header_value | 400 REDACTED | ABSENT |
| `%20` split | header_value | 400 REDACTED | ABSENT |
| mixed-case + `%2520` | header_value | 400 REDACTED | ABSENT |
| fullwidth `％20` | json_value | **served** | ABSENT |
| `%u0020` | header_value | **served** | ABSENT |
| `&#32;` | header_value | **served** | ABSENT |
| `%2a` / `%2A` | header_value | **served** | ABSENT |
| soft hyphen as raw UTF-8 | header_value | **served** | ABSENT |
| token split across two JSON string values | body | **served** | ABSENT |

**Oracle-detects-but-backend-served: `[]` — empty.** The oracle is never wider. Three reasons, all
reproduced: (i) it models the same 5 ops, so on saturating inputs its form set equals the
implementation's; (ii) it does not model the fail-closed arm, so on non-saturating inputs the
implementation is strictly *stricter*; (iii) as actually used it is applied to JSON-serialised record
text and is blind to JSON escaping — see R9-D5f-F4. The `served` rows are out-of-contract classes the
docstring never claims (`%u`, HTML entities, fullwidth) plus one that IS in contract and leaks (soft
hyphen / ZWSP as raw UTF-8 — R9-D5f-F2).

## Mutant table — 27 mutants, **21 KILLED / 6 SURVIVED** (1 intended control, 1 equivalent, 4 real)

Each mutation asserts its anchor matched exactly once before running, so no mutant can silently no-op.
Restore is from a pristine file copy; never git. Red file first, then the other two files if it survived.

| id | mutation | verdict | killer / equivalence |
|---|---|---|---|
| M00 | no-op control | SURVIVED (intended) | 104 + 338 = 442 — harness sound |
| **V3** | `_normal_forms` returns the **last frontier layer** instead of `seen` | **SURVIVED — LEAKS** | see R9-D5f-F1 |
| V1 | `_carries_secret` returns `False` instead of `not saturated` | KILLED | `R::test_credential_depth5_percent_nesting_returns_400` (5 failed, 99 passed) |
| V2 | `not saturated` inverted → `saturated` | KILLED | `R::test_json_depth_at_limit_is_served` (5 failed, 99 passed) |
| V6 | decision back to a set element (membership only, sentinel style) | KILLED | `R::test_credential_depth5_percent_nesting_returns_400` (5 failed, 99 passed) |
| V7 | `_normal_forms` always reports saturated | KILLED | `R::test_credential_depth5_percent_nesting_returns_400` (5 failed, 99 passed) |
| MC5 | `return frozenset(seen)` (no tuple) | KILLED | 82 failed, 22 passed (unpack TypeError) |
| MC1 | depth 5 → 4 | SURVIVED (non-equivalent) | distinguishing input `%252B` — see R9-D5f-F7 |
| MC2 | depth 5 → 6 | SURVIVED (non-equivalent) | distinguishing input `%25252541` — see R9-D5f-F7 |
| MC9 | JSON walk skips nested lists | KILLED | `R::test_credential_whitespace_split_in_json_list_element_returns_400` (5 failed, 99 passed) |
| MG4 | depth scan ignores strings | KILLED | `R::test_json_depth_handles_escaped_quote` (2 failed, 102 passed) |
| MG5 | depth scan ignores escapes | KILLED | `R::test_json_depth_handles_escaped_quote` (1 failed, 103 passed) |
| V12 | `_error()` drops `Connection: close` | KILLED | `test_s0_01_scripted_backend.py::test_framing_domain_table` (9 failed, 329 passed). NOTE: the red file stayed **104 passed but took 425.97s vs 40.43s** — it has no close assertion at all |
| V13 | drop `str.lower` from the ops | KILLED | `R::test_credential_uppercased_token_in_header_returns_400` (1 failed, 103) |
| V14 | drop `strip_zwc` | KILLED | `R::test_credential_zero_width_json_escape_returns_400` (4 failed, 100) |
| V15 | drop `strip_ws` | KILLED | `R::test_credential_depth5_percent_nesting_returns_400` (46 failed, 58) |
| V16 | drop `unquote_plus` | KILLED | `R::test_credential_depth5_percent_nesting_returns_400` (13 failed, 91) |
| V17 | header NAME not screened | KILLED | `test_s0_01_scripted_backend.py::test_credential_in_header_name_returns_400` (2 failed, 336) |
| V18 | raw body not screened | KILLED | `R::test_duplicate_json_key_hiding_token_returns_400` (1 failed, 103) |
| V19 | path not screened | KILLED | `R::test_credential_depth5_percent_nesting_returns_400` (18 failed, 86) |
| O1 | oracle → `return True` | KILLED | **only** `TestOracleSelfTests::test_oracle_known_vectors` (5 failed, 99 passed; n_failing_functions=1) |
| O2 | oracle drops `unquote` | SURVIVED | **EQUIVALENT** — `unquote_plus` subsumes `unquote`; 0 differences in a 50 000-string search |
| O3 | oracle drops `unquote_plus` | **SURVIVED — non-equivalent** | 4358/50 000 differ; see R9-D5f-F6 |
| O4 | oracle drops `strip_ws` | KILLED | `TestOracleSelfTests::test_oracle_known_vectors` (3 failed, 101) |
| O5 | oracle drops `lower` | KILLED | `TestOracleSelfTests::test_oracle_known_vectors` (1 failed, 103) |
| O6 | oracle drops `strip_zwc` | KILLED | `TestOracleSelfTests::test_oracle_known_vectors` (1 failed, 103) |
| O7 | oracle depth 6 → 1 | KILLED | `TestOracleSelfTests::test_oracle_known_vectors` (2 failed, 102) |

Also reproduced, outside the mutant count: the F17 negative control (below) fires on inf, NaN and −1.

---

# Findings

### R9-D5f-F1 — BLOCKING · SOLID · discarding `seen` (the ruling's named invariant) leaks, and nothing in the 442-test suite notices
- `proofs/S0-01/tools/scripted_backend.py:132` and `:134` (`_normal_forms`, the two `return frozenset(seen), …` sites) on my copy.
- Ruling 1 says verbatim: *"Keep `seen` — never discard forms already found."* The shipped code obeys it. **No test enforces it.**
- Mutant V3 replaces both returns with `frozenset(frontier)` (last layer only). Result: **`104 passed` on the red file and `338 passed` on the other two — the full 442-test suite is green over a mutant that leaks the credential.**
- Non-equivalence is not a judgement call: a directed search found **2458 distinguishing inputs in 200 000 random strings** and 20 in a small constructed family, every one in the leak direction (`base=True`, `V3=False`).
- Reproduced end-to-end against the real backend with its real record sink, concrete failing input
  `X-Trace: s0-01-upstream-tok+en-0123456789abcdef%2520`:
```
BASE (PIN, unmutated)      status=HTTP/1.1 400 Bad Request   record=REDACTED  x-trace=<absent>
V3 (seen -> last layer)    status=HTTP/1.1 200 OK            record=SERVED
                           x-trace=s0-01-upstream-tok+en-0123456789abcdef%2520
                           token recoverable by unquote_plus+unquote+strip_ws: True
```
- Observed: suite green, credential written to a durable record. Expected: a test that fails.
- Minimal fix — add to the red file:
```python
def test_credential_plus_split_with_pct2520_suffix_returns_400(backend):
    """Pins ruling 1's 'keep seen': the token is found at an INTERMEDIATE closure
    layer, not the final one. Red if _normal_forms returns only the last frontier."""
    port = backend["port"]; mid = len(TOKEN) // 2
    n0 = len(_records(backend))
    vec = TOKEN[:mid] + "+" + TOKEN[mid:] + "%2520"
    resp = _raw(port, _post(port, b'{"model":"s0-01-pong","messages":[]}',
                            extra_headers=f"X-Trace: {vec}\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert json.loads(_records(backend)[-1].read_text())["body"] == MARKER
```

### R9-D5f-F2 — BLOCKING · SOLID · a zero-width or Unicode-whitespace separator sent as raw UTF-8 in a header value defeats the screen; the token is written to the record and is recoverable
- `proofs/S0-01/tools/scripted_backend.py:118-120` (`strip_ws` / `strip_zwc` / `ops` — all operate on the decoded `str`) and `:250-252` (`record()` screens `str(k)`/`str(v)` from `self.headers`).
- `http.server` decodes header lines as **iso-8859-1**. A client that sends the separator UTF-8-encoded (what every real client does for non-ASCII header content) hands the screen `'â\x80\x8b'`, three latin-1 chars that neither `strip_zwc` nor `strip_ws` touches. The F15 tests only send the **percent-encoded** form (`%E2%80%8B`), which `unquote` decodes to the real U+200B — so they pass while the raw form leaks. Ruling 3/F15 asked for the zero-width class "raw and JSON `​`"; the raw-on-the-wire case is untested (`grep` for `utf-8`/`\xe2`/`\xc2` in both test files: no hits).
- Reproduced live, verbatim:
```
REQUEST  X-Trace: <tok[:18]> + e2808b (UTF-8 U+200B ZWSP) + <tok[18:]>
RESPONSE HTTP/1.1 200 OK
RECORD   headers['x-trace'] = 's0-01-upstream-tokâ\x80\x8ben-0123456789abcdef'
         latin1->utf8 redecode + strip_zwc -> 's0-01-upstream-token-0123456789abcdef'
         TOKEN RECOVERED FROM THE RECORD: True
```
- Whole class, all served 200 + recorded verbatim, all recoverable: U+200B, U+FEFF, U+00AD, U+2060, U+00A0, U+3000 as UTF-8 bytes. The single-byte latin-1 forms (`\xad`, `\xa0`) ARE caught — which is exactly why this hid.
- Observed: 200 OK + credential in the record. Expected: 400 + `credential_in_unexpected_location`.
- Minimal fix — one more closure op in `_normal_forms` (and the same op in the red-file oracle, or the oracle stops being wider):
```python
def utf8_redecode(x):
    try: return x.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError): return x
ops = (unquote, unquote_plus, strip_ws, str.lower, strip_zwc, utf8_redecode)
```
plus the red test:
```python
@pytest.mark.parametrize("sep", ["​", "﻿", "­", "⁠", " ", "　"])
def test_credential_raw_utf8_zero_width_in_header_returns_400(backend, sep):
    """F15 'raw': the separator arrives as UTF-8 BYTES; http.server decodes latin-1."""
    port = backend["port"]; mid = len(TOKEN) // 2; n0 = len(_records(backend))
    body = b'{"model":"s0-01-pong","messages":[]}'
    payload = (f"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\n"
               f"Authorization: Bearer {TOKEN}\r\nContent-Type: application/json\r\n"
               f"X-Trace: ").encode() + TOKEN[:mid].encode() + sep.encode("utf-8") \
              + TOKEN[mid:].encode() + f"\r\nContent-Length: {len(body)}\r\n\r\n".encode() + body
    resp = _raw(port, payload)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert json.loads(_records(backend)[-1].read_text())["body"] == MARKER
```

### R9-D5f-F3 — BLOCKING · SOLID · the "restored D5d-F12 accepted risk" is documented in two places and is false of the code
- `proofs/S0-01/tools/scripted_backend.py:47-48` (module docstring) and `:115-116` (`_normal_forms` docstring), both: *"Accepted risk (D5d-F12, restored): junk like `%25252540` triggers the bound-exceeded path and blanks the record (false positive)."* Ruling 1 required that risk RESTORED **and documented as such**.
- At the shipped bound of 5, `%25252540` **saturates** (saturation depth 5) → `not saturated` is `False` → **no blanking**. Live, with a valid body so a 400 could only come from the screen:

| `X-Trace:` value | status | reason | record |
|---|---|---|---|
| `%25252540` | **200 OK** | — | **served** |
| `%25252541` | 400 | credential in unexpected location | REDACTED |
| `%252B` | **200 OK** | — | **served** |
| `%252540` | **200 OK** | — | **served** |
| `%2525252540` | 400 | credential in unexpected location | REDACTED |
| `%25252520` | 400 | credential in unexpected location | REDACTED |

- The mechanism (re-derived from primary source, not adopted): `%2540` → `@`, and `@`.lower() == `@`, so that chain terminates one layer earlier than `%2541` → `A` → `a`. The documented example is off by exactly one closure layer.
- Observed: the doc names a behaviour the code does not have; no test covers either side. Expected: the docstring names a vector that actually blanks, and a test pins it.
- Minimal fix: change both docstrings to `%25252541` and add the pinning test in F7 below.

### R9-D5f-F4 — SOLID · the oracle is blind to JSON escaping, so `assert _absent_under_all_normalizations(record_text)` is vacuous for the entire whitespace and zero-width family
- `tests/red/test_s0_01_backend_credential_screen.py:92-116` (the oracle) used at `:131`, `:179`, `:224`, `:254`, `:271`, `:288`, `:305`, `:429`, `:475`, `:493`, `:530`, `:551`, `:566` (13 record-text call sites) plus the self-test at `:397`.
- The oracle is fed `recs[-1].read_text()` — the JSON-serialised record. `json.dumps` renders a TAB as the two characters `\` `t` and a ZWSP as the six characters `​`. `strip_ws`/`strip_zwc` match real characters, so they never fire. Measured:

| separator | `oracle(raw)` | `oracle(record-shaped)` |
|---|---|---|
| TAB | False (detects) | **True (blind)** |
| LF | False | **True** |
| CR | False | **True** |
| VT | False | **True** |
| FF | False | **True** |
| ZWSP | False | **True** |

- Consequence: if the backend regressed and recorded `"s0-01-upstream-tok\ten-0123456789abcdef"` verbatim, that assertion would still pass. The only load-bearing assertion in those tests is `== MARKER`. The self-tests hide this because they feed the oracle the **raw** form, never the record form it is actually given.
- Observed: a control that cannot fail on the family it was written for. Expected: the oracle decodes JSON escapes before normalising.
- Minimal fix: in the oracle, seed the form set with the JSON-unescaped text too —
  `forms = {text} | {json.loads(m) for m in re.findall(r'"(?:[^"\\]|\\.)*"', text)}` — and add a self-test vector that is the **record-shaped** (escaped) string and asserts `False`.

### R9-D5f-F5 — BLOCKING · SOLID · ruling 2(b) is not met: no backend test's redness depends on the oracle
- Ruling 2 requires *"at least one backend test whose redness depends ONLY on the oracle (mutate the oracle to `return True` → that test must fail)"*.
- Reproduced: O1 (`return True`) → `5 failed, 99 passed in 40.62s`, and the failures are **one test function**, `TestOracleSelfTests::test_oracle_known_vectors` (5 parametrised known-bad vectors). Zero backend tests fail. The lane's own report states the same five ids and still records the item as done.
- Observed: the oracle can be replaced by `return True` and every request-level test stays green. Expected: at least one backend test goes red.
- Minimal fix: drop the `== MARKER` assertion from exactly one credential test and let the oracle carry it (after F4 is fixed, or the test becomes vacuous), e.g. a new
  `test_record_text_carries_no_token_under_any_normalization` that asserts only `_absent_under_all_normalizations(...)` on the record of a TAB-split request.

### R9-D5f-F6 — SOLID · the oracle's own operator set is unpinned on the `+` axis
- `tests/red/test_s0_01_backend_credential_screen.py:102` (`ops = (unquote, unquote_plus, strip_ws, str.lower, strip_zwc)`), self-test vectors at `:383-395`.
- O3 (drop `unquote_plus`) **SURVIVES** the full 442-test suite and is **non-equivalent**: 4358 differences in 50 000 strings. Concrete: `oracle("s0-01-upstream-tok+en-0123456789abcdef")` = `False` (detects) with the full set, `True` (blind) without `unquote_plus`. None of the five known-bad self-test vectors uses `+` or `%2B`, so nothing catches it — even though the backend-side `+` axis is tested (`…encoded_whitespace_split_returns_400[PLUS]`).
- O2 (drop `unquote`) is **equivalent** — `unquote_plus` subsumes `unquote`; 0/50 000 differences. Admissible survivor.
- Minimal fix: add `(TOKEN[:mid] + "+" + TOKEN[mid:], False)` and `(TOKEN[:mid] + "%2B" + TOKEN[mid:], False)` to the `test_oracle_known_vectors` parametrisation.

### R9-D5f-F7 — SOLID · the depth bound is UNPINNED; MC1 and MC2 are both non-equivalent and the lane's reasoning for MC2 is backwards. **This is my answer to open item (b): a survivor that only tightens would be admissible — but MC2 does not only tighten, and neither bound is pinned.**
- `proofs/S0-01/tools/scripted_backend.py:123` (`for _depth in range(5)`), documented at `:43`, `:112`, `:223`.
- Both survive red file + other files (`104 passed` / `338 passed`), and **both have concrete distinguishing inputs, live-confirmed**:

| mutant | distinguishing input | base (depth 5) | mutant | direction |
|---|---|---|---|---|
| MC1 (→4) | `X-Trace: %252B` | 200 OK, served | 400, blanked | tightening (more false positives) |
| MC2 (→6) | `X-Trace: %25252541` | **400, blanked** | **200 OK, served** | **loosening (fewer false positives)** |

- The lane's report says MC2 is *"strictly more aggressive"* and that *"no input leaks through depth 6 that leaks through depth 5"*. The second clause is true (no leak escapes at any bound — the docstring at `:44-45` says so correctly). The first clause is **false**: raising the bound lets inputs saturate that previously tripped the fail-closed arm, so depth 6 blanks strictly *fewer* records. MC1 and MC2 move in opposite directions and the report calls both "strengthening".
- Verdict on admissibility: **the depth is unpinned.** No test distinguishes 4, 5 or 6, while the docstring makes an explicit behavioural claim about exactly that class (and gets it wrong — F3). Two assertions pin the constant from both sides:
```python
def test_bound_exceeded_blanks_the_record(backend):
    """Pins depth == 5 from above: %25252541 saturates only at 6, so it must
    trip the fail-closed arm. Red at depth 6 (MC2)."""
    ... X-Trace: %25252541 ... assert 400 and record body == MARKER

def test_saturating_junk_is_served(backend):
    """Pins depth == 5 from below: %252B saturates at 5. Red at depth 4 (MC1)."""
    ... X-Trace: %252B ... assert 200 and the record is NOT the marker
```

### R9-D5f-F8 — SOLID · ruling 3's `header NAME` sink was dropped from the depth-5 test, and the reason given for dropping it is falsified by experiment
- Ruling 3 enumerates six sinks for `test_credential_depth5_percent_nesting_returns_400`: *"header value / header NAME / query / path / JSON value / JSON key"*. The test at `tests/red/test_s0_01_backend_credential_screen.py:440-442` parametrises five — `header_name` is absent (20 tests instead of 24).
- The lane's `not_done` reason: *"percent-encoded characters in HTTP header names may cause parser-level defects that trigger the framing gate before the credential screen runs."* I probed it: **all four vectors in a header NAME return 400 + REDACTED** (table under "Open item (a)"). `%` and `+` are RFC 9110 `tchar`s; there is no parser interaction. The excuse was never tested before being written down.
- Observed: an enumerated contract item omitted on an untested premise. Expected: either the 4 extra tests, or a reason that survives a probe.
- Minimal fix: add `"header_name"` to the `sink` parametrisation at `:440-442` and the branch
  `if sink == "header_name": resp = _raw(port, _post(port, VALID, extra_headers=f"X-{split_token}: v\r\n"))`.

### R9-D5f-F9 — SOLID (minor) · ruling 4/F11 offered two options and the lane took neither
- `proofs/S0-01/tools/scripted_backend.py:434-438`. Ruling 4: *"F11 **delete** the dead `except RecursionError` arm **or make it reachable**"*. The lane kept it and rewrote the comment. The arm is genuinely unreachable (`_json_nesting_depth(raw) > 32` returns first; CPython's limit is 1000) — I confirmed this behaviourally across four interpreters, so the comment is now *accurate*, but the arm is still untestable dead code and the binary choice was not made.
- Minimal fix: delete lines 434-438, or drop `MAX_JSON_DEPTH` far below the recursion limit in a test that reaches the arm.

### R9-D5f-F10 — SOLID (minor) · every `file:line` reference in the lane report is stale by 6-9 lines
Re-derived at the PIN on my copy:

| report claim | actual |
|---|---|
| `_normal_forms` `:102-127` | **108-134** |
| `_carries_secret` `:209-222` | **218-230** |
| `_error` `:370-372` | **395-398** |
| `record()` comment `:231-232` | **241-243** |
| oracle `:93-115` | 92-116 (ok) |
| self-tests `:377-397` | class 379, `def` 396 |
| `tests/test_s0_01_scripted_backend.py:1524-1527` | ok |
A reviewer following the backend refs lands 6-9 lines above the cited code. Fix: re-derive before minting.

### R9-D5f-F11 — SOLID (informational) · D5f roughly 2.4× the screen's CPU cost at `MAX_CONTENT_LENGTH`
Measured with a length-aware client (my first attempt read 30 s of keep-alive idle and I discarded it):

| body | PIN (5 ops) | PIN-parent (3 ops) |
|---|---|---|
| 1 KB | 0.00 s | 0.00 s |
| 10 KB | 0.00 s | 0.00 s |
| 100 KB | 0.02 s | 0.01 s |
| 1000 KB | **0.22 s** | 0.09 s |

Not a DoS at `Handler.timeout = 30`, and D5e-F16's "~0.5 s" was the same order. Recorded because `str.lower` and `strip_zwc` widen the branching factor from 3 to 5 and F2's fix adds a sixth.

### R9-D5f-F12 — SOLID (informational) · `_json_safe` mutates the parsed request body in place
`proofs/S0-01/tools/scripted_backend.py:283-305` (`def _json_safe` at `:283`): it is correctly iterative (F10 delivered), but it assigns
`item[k] = "<non-finite>"` into the caller's object and returns the same object. `rec_body` **is** `body`, so
the request body is mutated before the response path reads it. Harmless today (non-finite floats never reach
a response) — flagged because it is an aliasing hazard, not a defect I could trigger.

### R9-D5f-F13 — SOLID (procedural) · premise drift and a dirty scratchpad
- The shared tree advanced from the PIN to `e84b7ef` (**18 commits**) during this review; the brief's PREMISE (`HEAD == PIN`) is false at report time. All three D5f scope files are byte-identical at PIN, at HEAD and in the worktree, so the verdict holds — but a later verifier must re-pin rather than assume.
- `…/scratchpad/vd9/repo` already existed with a previous round's `__pycache__`. I deleted and re-extracted and proved the copy has exactly the archive's 10014 entries. A round that had reused it would have run against stale bytecode.

---

## What the lane got right (verified by me, not adopted)

- The R1 decision as shipped: `(forms, saturated)` + `not saturated` — 70/70 live cells (F1 vector and control × 7 sinks × 5 separators) are 400 + REDACTED, including the header-NAME sink the lane never tested. V1, V2, V6, V7, MC5 all die.
- `Connection: close` on **every** rejection, read off the wire: credential-400, 404, 401, bad-JSON-400, messages-400, model-404, 417, 411, dup-CL-400, depth-400 all carry `Connection: close`; the 200 control carries none. `:39` is true. V12 dies on the domain table.
- F17: the `math.isfinite` guard rejects the **whole** unusable class. Negative control run by me on `Handler.timeout`:
  `inf` → `AssertionError: Handler.timeout inf is not a finite positive number`; `nan` → same; `-1` → same.
- F10 depth gate is interpreter-independent — I ran the real backend under **every** `python3.*` in the sandbox:

| interpreter | depth 32 | depth 33 | depth 1000 |
|---|---|---|---|
| 3.10.20 / 3.11.15 / 3.12.3 / 3.13.12 / 3.11.15 (`/usr/local`) | passes the gate (record written) | 400, **no record** | 400, **no record** |

  identical on all five. **The CI leg (3.12) as a pytest run is NOT executed here** — only the backend behaviour under 3.12 is.
- F19: no `/tmp/` literal in any of the three files. `tmp_path` hygiene clean — `git status --porcelain` on my copy empty before and after every batch.
- MC9, MG4, MG5 all die on the new tests, exactly as claimed. M00 control sound.
- Normal traffic unchanged after 30+ redactions: `GET /v1/models` → 200 with both models and `FIXED_CREATED`; `POST /v1/chat/completions` → 200 `{"content":"pong"}` with `FIXED_USAGE`; records carry `authorization_fingerprint` and the `authorization` header is dropped.

## Reproduced vs reviewed statically vs skipped

- **Reproduced:** both gate runs and the final integrity run; the red state on the PIN's parent; all 27 mutants with anchor assertions and pristine-copy restore; the 70-cell sink×separator matrix; the header-NAME sink; the accepted-risk table; the oracle-wider matrix; the oracle JSON-blindness matrix; the V3 leak and the raw-UTF-8 leak end-to-end with record dumps; `Connection: close` off a real socket; the isfinite negative control; the interpreter matrix; the cost table; pyflakes; every `file:line` re-derivation.
- **Reviewed statically:** the `RecursionError` arm's unreachability *argument* (its behavioural consequence I did reproduce); `_json_safe`'s aliasing (F12) — I did not construct a request that observes the mutation.
- **Deliberately skipped:** the CI 3.12 pytest leg (no 3.12 pytest in this sandbox — the backend behaviour under 3.12 is covered instead); `xdist` (4 shared cores, other lanes live); anything touching the shared tree or the PC.

## Verdict

**NOT-READY.** Blocking: **R9-D5f-F1** (ruling 1's `seen` invariant unpinned; mutant leaks with 2458 distinguishing inputs, reproduced live), **R9-D5f-F2** (raw-UTF-8 zero-width separator in a header value leaks the configured token into the record, reproduced live, ruling 3/F15's "raw" case), **R9-D5f-F3** (ruling 1's restored accepted risk is documented in two docstrings and false of the code), **R9-D5f-F5** (ruling 2(b) not met — the oracle can be `return True` and no backend test notices).
Non-blocking but must be answered before minting: F4, F6, F7, F8, F9, F10.
No part of this verdict rests on anything I did not reproduce.
