Cleanup done; shared tree untouched by me (the 4 dirty files are other lanes'). Report follows.

---

# VERIFY-D5d — adversarial grade of lane D5d (round 8)

## Premise + disk

```
git log --oneline -3   (at start, in /home/user/agent-factory)
1e67982 transcripts: scrubbed sandbox chat digests (2026-09-06)
d9d0cf2 S0-01 WIP checkpoint 8a: the backend's credential screen closes the four VERIFY-D5c blockers (lane D5d), ...
2466595 transcripts: scrubbed sandbox chat digests (2026-09-06)
PREMISE MATCHES.

df -h /tmp/claude-0 | tail -1   (before the first mutant batch)
/dev/vda        252G   16G   22G  42% /
   (after all 60 runs + cleanup:  /dev/vda 252G 22G 16G 57% /)
```

**Tree moved under me.** HEAD is now `b84c1ac` (lane N5d, checkpoint 8b). `git diff --stat 1e67982..HEAD` over my three scope files is **empty**, and sha256 of all three matches my copy byte-for-byte (`f532aaa2…`, `8c040e9a…`, `e9e84d65…`). **The grade applies to the landed bytes.** I never wrote to the shared tree; its 4 dirty files (`frame_tee.py`, `pc_suite.sh`, `test_s0_01_check_acp_conformance.py`, `test_s0_01_frame_tee.py`) are other lanes'.

Scratch copy: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vd8/repo` (`git archive HEAD | tar -x`). Disk discipline: mutants materialised as `cp -al` hardlink trees of `proofs`+`tests` only, each with its own `--basetemp` and `TMPDIR`, **deleted immediately after its run**; pool of 6 live at once (hardlinks ⇒ ~23 KB real bytes each, the mutated file). No ENOSPC.

---

## 1. Mutant table — 59 applicable + control M00, all re-run

Set **re-derived against the D5d source, not trusted from the label**: 41 of round-7's 54 apply verbatim; **10 had to be re-expressed** because D5d rewrote their target text (M27–M30 Expect, M38–M42 `_carries_secret`, M46 body screen); **3 are N/A — M31/M32/M33 target the 501 arm F12 deleted, so they have no target at all**; plus M55 (round-7 double) and **7 new mutants M56–M62 aimed at the code D5d added**. Every snippet asserted to occur exactly once; every mutant `py_compile`-checked; base file sha-verified unmutated after each build. Command per mutant: `pytest tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py -x -q -p no:cacheprovider --basetemp <own> --deselect …::test_handler_timeout_bounds_incomplete_body`.

| id | arm / kind | verdict | killing test (first failure under `-x`) |
|---|---|---|---|
|M00|control/noop|**SURVIVED** (required)|`310 passed, 1 deselected in 238.77s` — harness sound|
|M01|1-defects/delete|KILLED|`test_framing_domain_table[defects/GET/v1/models/cred]`|
|M02|1-defects/invert|KILLED|`test_bearer_required_exact_401`|
|M03|1-defects/wrongcode|KILLED|`test_framing_domain_table[defects/…]`|
|M04|1-defects/noclose|KILLED|`test_framing_domain_table[defects/…]`|
|M05|2-te/delete|KILLED|`test_chunked_post_rejected_with_411`|
|M06|2-te/invert|KILLED|`test_bearer_required_exact_401`|
|M07|2-te/weaken-r5regression|KILLED|`test_framing_domain_table[te_gzip/…]`|
|M08|2-te/noclose|KILLED|`test_healthz_with_te_body_rejected_one_response_zero_records[with_cred]`|
|M09|3-dupcl/delete|KILLED|`test_duplicate_content_length_rejected_400[with_cred]`|
|M10|3-dupcl/boundary|KILLED|`test_duplicate_content_length_rejected_400[with_cred]`|
|M11|3-dupcl/invert|KILLED|`test_bearer_required_exact_401`|
|M12|3-dupcl/noclose|KILLED|`test_framing_domain_table[dup_cl_eq/…]`|
|M13|4a-clfmt/delete|KILLED|`test_framing_domain_table[cl_neg1/…]`|
|**M14**|4a-clfmt/`[0-9]+`→`\d+`|**SURVIVED**|— **equivalent** (re-derived: no latin-1 codepoint outside 0-9 is `Nd`; headers decode iso-8859-1)|
|M15|4a-clfmt/weaken-prefix|KILLED|`test_framing_domain_table[cl_1e3/…]`|
|M16|4a-clfmt/invert|KILLED|`test_bearer_required_exact_401`|
|M17|4a-clfmt/noclose|KILLED|`test_framing_domain_table[cl_neg1/…]`|
|**M18**|4b-postmax/delete|**KILLED**|`test_post_cl_overmax_ordering_beats_expect` ✅ round-7 survivor closed|
|**M19**|4b-postmax/`n>MAX+1`|**SURVIVED**|— **equivalent** (`_read_body:325` rejects CL==MAX+1 identically)|
|**M20**|4b-postmax/`n>=MAX`|**KILLED**|`R:test_post_content_length_exactly_max_is_accepted` ✅ closed|
|M21|4b-postmax/noclose|KILLED|`test_framing_domain_table[cl_over_max/POST/…]`|
|M22|4c-getcl/delete-serve|KILLED|`test_get_with_body_rejected_no_smuggling`|
|M23|4c-getcl/boundary|KILLED|`test_get_with_cl_1_rejected_400`|
|**M24**|4c-getcl/drop the `rfile.read`|**SURVIVED**|— **equivalent** (connection closes; undrained bytes discarded)|
|M25|4c-getcl/noclose|KILLED|`test_get_cl_over_max_smuggling_one_response_zero_records[with_cred]`|
|**M26**|4c-getcl/`read(0)`|**SURVIVED**|— **round 7 recorded this KILLED. See F7.**|
|M27|5-expect/delete *(re-expressed)*|KILLED|`test_framing_domain_table[expect/…]`|
|M28|5-expect/invert *(re-expressed)*|KILLED|`test_bearer_required_exact_401`|
|**M29**|5-expect/narrow to PRE-D5d truthiness *(re-expressed)*|**KILLED**|`R:test_expect_header_any_value_rejected_417[GET-]` ✅ closed|
|M30|5-expect/noclose *(re-expressed)*|KILLED|`test_framing_domain_table[expect/…]`|
|~~M31~~|6-501/delete|**N/A**|target code deleted by F12 — cannot be applied|
|~~M32~~|6-501/invert|**N/A**|target code deleted by F12 (round 7 had KILLED it)|
|~~M33~~|6-501/wrongcode|**N/A**|target code deleted by F12|
|M34|`_reject`/drop `Connection: close` hdr|KILLED|`test_framing_domain_table[cl_n/GET/…]`|
|**M35**|`_reject`/drop `close_connection=True`|**SURVIVED**|— **equivalent** (`send_header('Connection','close')` sets it)|
|M36|`_reject`/drop both|KILLED|`test_healthz_with_te_body_rejected…[with_cred]`|
|M37|expect100/delete override|KILLED|`test_framing_domain_table[expect/…]`|
|**M38**|carries/drop the raw `s` base *(re-expressed)*|**SURVIVED**|— **equivalent** (token has no whitespace ⇒ `t in s ⟹ t in stripped`)|
|**M39**|carries/`v = unquote(v)` → `v = v` *(re-expressed, stronger than round 7's)*|**KILLED**|`test_credential_percent_encoded_in_query_returns_400`|
|**M40**|carries/drop the `stripped` base *(re-expressed, stronger)*|**KILLED**|`test_credential_obs_folded_in_header_value`|
|**M41**|carries/`stripped = s` *(re-expressed)*|**KILLED**|`test_credential_obs_folded_in_header_value` ✅ closed|
|M42|carries/`return False`|KILLED|`test_credential_in_query_string_returns_400`|
|M43|screen/drop path|KILLED|`test_credential_in_query_string_returns_400`|
|M44|screen/drop header-NAME|KILLED|`test_credential_in_header_name_returns_400`|
|M45|screen/drop header-VALUE|KILLED|`test_credential_in_custom_header_returns_400`|
|M46|screen/drop the whole body block *(re-expressed)*|KILLED|`R:test_credential_whitespace_split_in_valid_json_body_…`|
|M47|screen/drop raw_body screen|KILLED|`test_malformed_json_with_token_in_body_redacted`|
|**M48**|screen/auth exempt by prefix|**KILLED**|`R:test_authorization_prefixed_header_name_is_not_exempt` ✅ closed|
|M49|screen/leak path not sanitized|KILLED|`test_leak_record_does_not_contain_token`|
|M50|auth/`==`→`startswith`|KILLED|`test_bearer_superstring_rejected_401`|
|M51|healthz/`==`→`startswith`|KILLED|`test_healthz_exact_path_no_prefix_match`|
|**M52**|readbody/`>MAX+1`|**SURVIVED**|— **equivalent** (unreachable behind the gate)|
|**M53**|readbody/drop `fullmatch`|**SURVIVED**|— **equivalent** (unreachable behind the gate)|
|M54|readbody/drop short-body check|KILLED|`test_short_body_returns_400_no_record`|
|**M55**|double: postmax + `_read_body` max|**KILLED**|`test_post_cl_overmax_ordering_beats_expect`|
|**M56**|NEW `for _ in range(3)` → `range(1)`|**SURVIVED**|— **equivalent, and that is the finding** → F5|
|**M57**|NEW drop the fail-closed branch|**SURVIVED**|**NON-EQUIVALENT** → F4|
|M58|NEW delete arm 1b (obs-fold)|KILLED|`R:test_obs_folded_header_rejected_400[CL]`|
|**M59**|NEW arm 1b sees `\r` only|**SURVIVED**|**NON-EQUIVALENT** → F3|
|M60|NEW delete the `_iter_json_strings` walk|KILLED|`R:test_credential_whitespace_split_in_valid_json_body_…`|
|**M61**|NEW POST-success `raw_body=` → `None`|**SURVIVED**|**NON-EQUIVALENT** → F6|
|**M62**|NEW walk stops yielding dict KEYS|**SURVIVED**|**NON-EQUIVALENT, LEAK** → F5b/F4b (id **R8-D5d-F5**)|

**Totals (measured, replacing the lane's expectation):**
- Full re-derived set: **46 KILLED / 59 applicable · 13 survivors = 9 proven-equivalent (M14, M19, M24, M26, M35, M38, M52, M53, M56) + 4 non-equivalent hollow greens (M57, M59, M61, M62)**. M00 control survived.
- Restricted to round-7's set as re-expressed (51 applicable + M55 = 52): **44 killed, 8 survivors, all equivalent**.
- **The bar in the brief is MET for round 7's five: M18, M20, M29, M41, M48 are all killed by named tests.**
- The lane's "Expected total: 43/54 killed, 11 equivalent survivors" is **arithmetically wrong on its own terms** (F8): 3 of the 54 no longer have a target; M32 (killed in round 7) is counted inside the "preserved 38"; and 2 of the 11 labelled equivalents (M39, M40) are killed once the mutation is expressed against the rewritten `_carries_secret` rather than the old 4-term `or`.

---

## 2. Replay + domain table

**36 D5b vectors** (`vd8/work/replay_d5b.py`, forged tail in the same `sendall`): **36/36 pass** — every one `n_http=1`, `delta=0`, `tail=no`, `close_hdr=Y`. Round-7's 19-case credential battery is also clean, and the F6 fix is visible in it: C3/C5/C6 (obs-folded token) now give `400 / newrecs=0` where round 7 recorded them.

**Domain table — my oracle, extended for the new gate** (`vd8/work/domain2.py`; contract rule 1b inserted between rule 1 and rule 2, Expect re-derived as *presence*, plus 5 new framings `expect_empty`, `expect_bogus`, `fold_cl`, `fold_te`, `fold_benign`):

```
=== DOMAIN TABLE: 232 cells, contract-derived oracle ===
mismatches vs contract oracle: 0 / 232
```
(192 original cells + 40 new; every rejection = exactly one response, `Connection: close`, zero records, tail never served; every acceptance = 2 responses and the exact record delta. Half-close vs no-half-close control on 4 representative cells: identical.)

---

## 3. Findings

### R8-D5d-F1 — **BLOCKING · SOLID · live credential leak**: the screen composes strip∘unquote but never unquote∘strip
- **file:line** `proofs/S0-01/tools/scripted_backend.py:151-152` — `stripped` is computed **once, from `s` only**, and the loop then unquotes each base without ever re-stripping.
- **Concrete failing input** (dummy token, owner's own test upstream): `GET /v1/models HTTP/1.1` + `X-Trace: s0-01-upstream-tok%20en-0123456789abcdef`.
- **Observed:** `HTTP/1.1 200 OK`, 1 record written, **not** redacted:
  ```json
  "headers": { "x-trace": "s0-01-upstream-tok%20en-0123456789abcdef" }
  ```
  `TOKEN in re.sub(r"\s+","",unquote(record_text))` → **True**. **Expected:** 400 + `{"credential_in_unexpected_location": true}`.
- Reproduced on **all three sinks** and **five separators**: header value, JSON body, and path × `%20`, `%09`, `%0A`, `%0d`, `+` — 15/15 served 200 with a recoverable token. Confirmed independently against `State._carries_secret` in-process (`False` where an ≤4-step normalization oracle says `True`).
- **Minimal fix:** inside the loop in `_carries_secret`, after `v = unquote(v)`, also test the whitespace-stripped form — e.g. `if t in v or t in re.sub(r"\s+","",v): return True`, and feed `re.sub(r"\s+","",v)` back as the next base.
- **Red test to add:** `test_credential_encoded_whitespace_split_returns_400`, parametrized `["%20","%09","%0A","%0d","+"]` × `{header value, JSON body, query}` → assert `HTTP/1.1 400 Bad Request`, `body == MARKER`, and the **extended** absence oracle below.

### R8-D5d-F2 — **BLOCKING · SOLID · the test oracle shares F1's blind spot (mirror, not gate)**
- **file:line** `tests/red/test_s0_01_backend_credential_screen.py:93-95` — `_absent_under_all_normalizations` checks `(text, unquote(text), stripped, unquote(stripped), unquote(unquote(text)))` and **never `strip(unquote(text))`**.
- **Proof:** run verbatim on the leaking record text from F1 → returns **`True` ("absent")** while `TOKEN in re.sub(r"\s+","",unquote(text))` is `True`. Even if a `%20`-split token reached a record, four existing assertions would call it clean.
- **Minimal fix:** add `re.sub(r"\s+","",unquote(text))` (and `unquote(re.sub(r"\s+","",text))`) to the tuple — the oracle must be strictly wider than the implementation, never a copy of it.

### R8-D5d-F3 — **BLOCKING · SOLID · arm 1b's LF-only half has zero coverage (M59 survives, smuggles)**
- **file:line** `proofs/S0-01/tools/scripted_backend.py:251-254` (arm 1b); test gap at `tests/red/test_s0_01_backend_credential_screen.py:174` (`ids=["CL","TE"]`, both **CRLF** folds only).
- **Proof:** M59 (`if '\r' in _v or '\n' in _v:` → `if '\r' in _v:`) **survives the whole suite** (310 passed). Distinguishing input, live: `X-Foo: bar\n Content-Length: 5\r\n` (bare-LF fold) + pipelined forged POST.
  **BASE:** `400`, `n_http=1`, `0` records. **M59:** `200 OK`, **`n_http=2`, 2 records — the smuggled tail was served.**
- Parser primary source confirms the vector is real: `http.client.parse_headers` yields `('X-Foo', 'bar\n Content-Length: 5')` — **`\n` only, no `\r`** — and `get_all('Content-Length')` is `None`, so the folded CL is invisible to arms 3/4.
- **Minimal fix (tests only; the code is correct):** parametrize `test_obs_folded_header_rejected_400` with the fold terminator too — `ids=["CL-CRLF","TE-CRLF","CL-LF","TE-LF"]`.

### R8-D5d-F4 — **BLOCKING · SOLID · the fail-closed branch has zero coverage (M57 survives, non-equivalent)**
- **file:line** `proofs/S0-01/tools/scripted_backend.py:164-166` (`if unquote(v) != v: return True`).
- **Proof:** M57 (branch deleted) **survives** (310 passed). Distinguishing input: a **quadruple** percent-encoded token in `X-Trace`. **BASE:** `400`. **M57:** `200 OK` with the value recorded. Nothing in 331 tests exercises the ≥4-level path.
- **Red test to add:** `test_credential_quad_percent_encoded_fails_closed` — `X-Trace: <token percent-encoded four times>` → `400` + `body == MARKER`.

### R8-D5d-F5 — **BLOCKING · SOLID · the walk's KEY channel has zero coverage (M62 survives, leaks)**
- **file:line** `proofs/S0-01/tools/scripted_backend.py:102-104` (`yield k` for dict keys), consumed at `:197`.
- **Proof:** M62 (stop yielding keys) **survives** (310 passed). Distinguishing input: `POST /v1/chat/completions` with body `{"model":"s0-01-pong","messages":[],"s0-01-upstream-tok\ten-0123456789abcdef":1}`.
  **BASE:** `400` + redacted. **M62:** `200 OK`, record written, `body` field =
  `{'messages': [], 'model': 's0-01-pong', 's0-01-upstream-tok\ten-0123456789abcdef': 1}` — i.e. **json-decode + whitespace-strip recovers the token**. That is exactly the F1-class attack the lane just closed, surviving through the key channel.
- **Red test to add:** `test_credential_whitespace_split_as_json_key_returns_400` (same `sep` parametrization as the value test) → `400` + `MARKER` + extended absence oracle.

### R8-D5d-F6 — SOLID · the POST-success raw-body screen is untested (M61 survives, non-equivalent, cannot leak)
- **file:line** `proofs/S0-01/tools/scripted_backend.py:384` (`raw_body=self._last_raw_body`).
- **Proof:** M61 (`raw_body=None`) **survives**. Distinguishing input: **duplicate JSON key** `{"model":"s0-01-pong","messages":[],"n":"<TOKEN>","n":"safe"}` — the token is in the wire bytes but `json.loads` keeps only the last key. **BASE:** `400` + redacted. **M61:** `200 OK` + record.
- **Bounded honestly:** the token cannot reach the record either way (`rec_body` is the *parsed* value, fully covered by the walk), so this is defence-in-depth without coverage, **not** a leak.
- **Red test to add:** `test_duplicate_json_key_hiding_token_returns_400` with that exact body.

### R8-D5d-F7 — SOLID · M26 status flip: a round-7 kill is no longer reproducible
- Round 7 (`tasks/briefs/.../verify-D5c.md:123`) records **M26 `read(0)` KILLED by `test_framing_domain_table[cl_over_max/GET/healthz?x=1/nocred]`**. Round 8: M26 **survives the full suite** (310 passed), and BASE ≡ M26 on that exact cell — 3 repeats, **both** with and without half-close (`400 / n_http=1 / delta=0` in all 6). I found no distinguishing input.
- Either the round-7 kill was a TCP-RST race (an unreliable oracle) or the F9 assertion rewrite removed it. Either way the lane's *"Previously killed mutants (38/54) … structurally preserved"* is **falsified for at least M26**.
- **Minimal fix:** either accept M26 as equivalent and say so, or add a control that actually discriminates draining (assert the server consumed `min(n, MAX)` bytes, e.g. by a second pipelined request that must NOT be misframed).

### R8-D5d-F8 — SOLID · the lane's mutant arithmetic double-counts deleted code
- F12 deleted the 501 arm (`:284-286` is now only a comment), so **M31/M32/M33 have no target**. The report nonetheless claims *"Expected total: 43/54 killed, 11 equivalent survivors"* and *"The 11 equivalent survivors remain equivalent (dead code M31/M33 …)"* — M31/M33 are not survivors, they are gone; and M32, **killed** in round 7, is silently inside the "preserved 38".
- **Measured replacement:** 46/59 killed over the re-derived set; 44/52 over round-7's set as re-expressed; 8 survivors there, all equivalent.

### R8-D5d-F9 — SOLID · the docstring omits the mechanism F1 was fixed with (F10/F11 only partly discharged)
- **file:line** `proofs/S0-01/tools/scripted_backend.py:41-44`. It says the screen is applied to *"serialized JSON body, and raw body"* and **never mentions `_iter_json_strings`**, the parsed-leaf walk that is the entire F1 fix. A maintainer following the docstring would reintroduce F1 (M60 proves the walk is load-bearing: deleting it reds `test_credential_whitespace_split_in_valid_json_body_*`).
- Also imprecise: *"bounded at 3 passes"* — four decode levels are checked (0–2 in the loop, 3 in the `else`) and a **fourth** `unquote` runs in the fail-closed test at `:166`.
- Also `:39` *"Every rejection sends `Connection: close`"* is silent about the path in F10 where **nothing at all is sent**.
- Everything else in the docstring I checked is **true**: `:19` bearer superstring → 401 (replay C16/C17); `:20` `/healthzXYZ` → 401 + record (C18); `:23`–`:35` all six arms, OWS behaviour (`Content-Length:  5` → `'5'` accepted, `Content-Length: 5 ` → `'5 '` rejected — verified against `http.client.parse_headers` directly), Expect presence incl. empty; `:36-38` 501 from `handle_one_request` with no tail served and `Connection: close` (24/24 method cells); `:46-51` nothing recorded on any rejection (all 232 cells) and duplicate headers collapsing to the last value.
- **Minimal fix:** one sentence naming `_iter_json_strings` (keys and values of the parsed body); correct the pass count; note the crash path or fix F10.

### R8-D5d-F10 — SOLID · unhandled `RecursionError`: no response, no record, contradicting the docstring
- **file:line** `proofs/S0-01/tools/scripted_backend.py:335-337` — `_read_body` catches only `(ValueError, UnicodeDecodeError)`; `RecursionError` escapes `do_POST`.
- **Concrete input:** a ~2 KB POST body nested ≥ 985 deep, e.g. `{"model":"s0-01-pong","messages":[],"n":[[[…"x"…]]]}`. **Observed:** client gets **zero bytes**, `n_http=0`, `0` records, traceback on the server's stdout. **Expected:** 400 + `Connection: close`. Exact threshold measured: 984 → `400`, 985 → no bytes. Server survives (a later request returns 200) and **no seq gap** occurs, because the crash is in `json.loads`, before `record()`.
- **Pre-existing**, not introduced by D5d — but D5d added a **second** recursive consumer *inside* `record()` (`_iter_json_strings`, `:92-107`, called at `:197` **after** `self.seq` was incremented at `:172-174`). Mechanism proven in-process: at depth 950 with 50 extra stack frames `json.loads` succeeds and the walk raises `RecursionError`; were that to happen live the record file would never be written while `seq` had advanced → **a gap in the evidence sequence**. It does not open in this configuration (json.loads dies first at every depth I probed, 982–995).
- **Minimal fix:** add `RecursionError` to the `except` at `:336`; make `_iter_json_strings` iterative (explicit stack) so `record()` has no recursive limb.
- **Red test:** depth-1000 nested body → assert `HTTP/1.1 400`, `Connection: close`, `delta == 0`.

### R8-D5d-F11 — SOLID · `NaN`/`Infinity` in a request body corrupt the evidence record
- **file:line** `proofs/S0-01/tools/scripted_backend.py:216` (`json.dumps(..., indent=2, sort_keys=True)`, `allow_nan` defaulted `True`).
- **Concrete input:** POST body `{"model":"s0-01-pong","messages":[],"n":NaN,"i":Infinity}` → `200 OK`, record written containing `"i": Infinity,` / `"n": NaN`.
- **Observed vs expected:** the record is **not RFC-8259 JSON**. Python's `json.loads` accepts it; a strict parser rejects it — reproduced with `json.loads(text, parse_constant=raise)` → `ValueError: Infinity`. The record dir is the golden's evidence artifact; any non-Python consumer (`jq`, Go, Rust) fails on it.
- **Minimal fix:** `json.dumps(..., allow_nan=False)` with the non-finite leaves coerced to a sentinel string before recording.
- **Red test:** post that body, then assert `json.loads(record_text, parse_constant=lambda c: pytest.fail(c))` succeeds.

### R8-D5d-F12 — SOLID · fail-closed is over-broad: benign values can destroy a record's evidentiary content
- **file:line** `:164-166`. **Concrete input:** `X-Trace: %25252540` (no token anywhere) → `400` and the **whole record redacted** to `{"credential_in_unexpected_location": true}` with `path: null, headers: {}`. Threshold measured: any string needing ≥ 4 percent-decode passes to stabilise. Fail-closed, so not a security hole, and the docstring is honest about it — reporting as an accepted-risk with the concrete input, since a client can silently blank its own evidence.

### R8-D5d-F13 — SOLID · F15's timeout derivation is not None-guarded
- **file:line** `tests/test_s0_01_scripted_backend.py:633` `handler_timeout = mod.make_handler(_st).timeout`, used at `:636`, `:659`, `:661`.
- **Proof:** delete the `timeout = 30` class attribute (the exact mutant this test exists to kill) → `.timeout` inherits `None` from `socketserver.StreamRequestHandler` → `:636` raises `TypeError: unsupported operand type(s) for *: 'NoneType' and 'float'`. The mutant is still killed (an error is a failure) but with a misleading message and before any bound is asserted.
- **Minimal fix:** `assert isinstance(handler_timeout, (int, float)) and handler_timeout > 0, "Handler.timeout must be a positive number"` before line 636.

### R8-D5d-F14 — SOLID · lane-report accuracy
- (a) *"passed `raw_body=` at both POST success (:323) and GET (:292) record sites"* — the GET site (**`:352`** in the landed file) passes the **literal `None`**, and a GET can never carry a body (arm 4c rejects `CL>0`), so that half of the fix is a sink-of-throwaway-default. Actual sites are `:352`, `:372` (`e.raw`), `:384`; none of the quoted line numbers match.
- (b) The claimed killing tests are `-x` first-failure artifacts: M41 is reported as killed by `test_credential_percent_encoded_and_whitespace_split_in_header_value`; measured, the re-derived M41 dies first at `test_credential_obs_folded_in_header_value`.
- (c) *"test_credential_triple_percent_encoded… proves the fixed-point unquote (bounded at 3 passes)"* is **false** — see F5 note below / M56.

### R8-D5d-F15 — SOLID · the "3 passes" bound is unpinned and unobservable
- **file:line** `:154` (`for _ in range(3)`). **Proof:** M56 (`range(3)` → `range(1)`) **survives the whole suite** and returns **`400` on the lane's own triple-encoding vector** (BASE `400`, M56 `400`). Reason: `range(1)` is strictly *more* conservative — the fail-closed branch at `:166` dominates, so `range(1)` ⊇ `range(3)` in detection and no input can distinguish them. The new test proves the fail-closed branch, **not** a 3-pass bound.
- **Minimal fix:** honest docstring — the bound only affects false-positive breadth, not detection; or delete the loop and rely on the fail-closed test alone.

### R8-D5d-F16 — SOLID · the 192-cell domain table did not grow with the gate
- **file:line** `tests/test_s0_01_scripted_backend.py:1392-1532` (`_build_domain_table`) still carries 21 framings. Obs-fold and empty/bogus Expect exist only as 2 + 8 red-file params, and no framing case covers `fold_benign`. Behaviour is correct (my extended 232-cell run: 0 mismatches), but the lane's own table no longer covers its own gate. Working oracle at `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vd8/work/domain2.py` — add framings `fold_cl`, `fold_te`, `fold_benign`, `expect_empty`, `expect_bogus` (40 cells).

### R8-D5d-F17 — SOLID · cross-sink splits are **out of contract** — stating it, not inventing a requirement
- Token split across two header values (`X-A`/`X-B`), across a header value and the JSON body, and across two JSON leaves: **all served `200` with a record** (BASE). The docstring at `:41-44` scopes the screen **per item** ("path, header names, header values, serialized JSON body, and raw body"), so this is **not** a violation of the stated contract and I am not grading it as one. It is also unrecoverable from a single record field without reassembly. One sentence in the docstring would make the scope explicit.

### R8-D5d-F18 — SOLID (cosmetic) · duplicated, self-contradicting docstring sentence
- **file:line** `tests/red/test_s0_01_backend_credential_screen.py:4-6`: the F3/F4/F5 sentence is pasted twice — *"…they pass and must keep passing. F3/F4/F5 are the verifier's missing controls (…): they pass today and must keep passing."*

### Verified — NOT findings (checked, clean)
- **F9 hygiene:** `> count_before` → **0 occurrences** in both files. Substring status assertions → **0**; the five `in resp` hits (`:599`, `:1595`, `:1815`, `:1914`, `:1934`) are body-text and `Connection: close` assertions, legitimate. No `in` used on a status line.
- **F8 self-containment:** `test_requests_are_recorded_with_fingerprint_and_token_absent_from_argv` **passes alone** (`1 passed in 0.17s`). I additionally ran the other six baseline-less record readers standalone — **all 6 pass alone**; no test depends on another test's records.
- **F13/F14 negative controls:** `test_post_cl_overmax_ordering_beats_expect:1896` asserts `400` (not 417) with `Expect: 100-continue` present, `n_http==1`, `Connection: close`, `delta==0` — kills M18 and M55, verified. `test_negative_control_defects_gate_arm` and `…_expect_gate_arm` carry forged tails, exact status, `n_http==1`, `Connection: close`, `delta==0`. The TE / dup-CL / CL-format / GET-CL controls lack `Connection: close` but their `n_http==1` assertion kills M08/M12/M17/M25 anyway — **not a gap**.
- **Arm 1b reachability:** structurally first-in-`_framing_gate` after the defects arm, and `_framing_gate()` is the first statement of `do_GET`/`do_POST` — so it runs **before** `/healthz`, before auth, before the record boundary, on every path with and without a credential (232/232 cells confirm). Obs-fold produces **no** `headers.defects` in CPython 3.11.15, so arm 1 does **not** pre-empt it — arm 1b is genuinely reachable and necessary (M58 killed). I searched for a fold whose joined value carries no CR/LF (`compat32.header_source_parse` = `value.lstrip(' \t') + ''.join(sourcelines[1:])` then `.rstrip('\r\n')`) and found none: tab-continuation, bare-LF, empty continuation and empty-value folds all retain a terminator. Every header the parser **drops** (`Content-Length : 5`, no-colon line, empty name) raises a defect and is caught by arm 1 — verified for all three, and `>100 headers` / over-long lines are 431'd by `parse_request` before dispatch.
- **`_iter_json_strings` cost:** 1 MiB bodies (flat string, 60 k short leaves, 1 MiB + trailing token) all handled in **0.04–0.07 s** wall. Not a DoS surface.
- **Authorization exemption is exact-name:** `Authorization`/`authorization`/`AUTHORIZATION` exempt (200); `Authorization-X`, `Authorizationfoo`, `X-Authorization`, `Proxy-Authorization`, `X-Api-Key` all → `400` + redacted.
- **Unicode escapes / surrogates:** `\u0020`- and `\t`-escaped splits, astral surrogate pairs and a **lone** surrogate leaf all → `400` + redacted, no encode crash (`ensure_ascii` keeps the record writable).

---

## 4. Discrepancy replay and F17

**The lane's discrepancy claim — REPRODUCED.** M60 reverts *only* the `_iter_json_strings` walk (`:196-200`) and leaves the `raw_body=` plumbing at `:352/:372/:384` intact. Result: **KILLED** — `tests/red/…::test_credential_whitespace_split_in_valid_json_body_…` fails (`1 failed, 289 passed`). Mechanism re-derived from primary source: the red test builds the body with `json.dumps`, which escapes the tab to the two characters `\` + `t`, so the raw bytes contain no whitespace for `re.sub(r"\s+","",…)` to remove — `raw_body=` alone cannot see it. The walk is load-bearing. Claim stands.

**F17 not_done reason — TRUE, reproduced.** Adding `self.send_header("Connection","close")` to `_send_json` (`:299`) and running `pytest tests/test_s0_01_scripted_backend.py -k framing_domain_table`: **`20 failed, 172 passed, 98 deselected`** — exactly the keep-alive acceptance cells (`cl_0/POST/…`, `cl_n/POST/…`, `cl_space5/POST/…`, `cl_0/GET/healthz?x=1/nocred`, …), which assert `http_count == 2`. The lane's stated reason is correct and F17 is legitimately deferred.

---

## 5. Gates

```
pytest-summary: 319 passed in 268.88s (0:04:28)     [run 1]
pytest-summary: 319 passed in 268.53s (0:04:28)     [run 2]
   bash scripts/test_summary.sh tests/test_s0_01_scripted_backend.py \
        tests/red/test_s0_01_backend_credential_screen.py tests/test_stage0_ci_workflow.py
   pytest-exit: 0  (both)
red file standalone: 21 passed in 70.28s (0:01:10)   (no xfail, no skip)
pyflakes-rc: 0   (python3 -m pyflakes on all three scope files, no output)
```
**tmp_path hygiene:** file manifest of my copy before vs after both suite runs differs only by three `__pycache__/*.pyc` files — covered by `.gitignore:16 __pycache__/`. **No test writes into the repo tree.** (My copy is a `git archive` extract, so `git status --porcelain` is not available there; the manifest diff is the equivalent check. The shared tree stayed at 0 lines attributable to me.)

---

## 6. What I reproduced vs reviewed statically vs skipped

**Reproduced live, this session:** all 60 mutant runs (each a fresh hardlink tree, own basetemp, deleted after); BASE-vs-mutant distinguishing inputs for M26, M56, M57, M59, M61, M62; the 36 D5b vectors; the 232-cell domain table against my own contract-derived oracle; the F1 leak end-to-end including the record file's bytes; the `%20/%09/%0A/%0d/+` battery across three sinks; `_carries_secret` in-process against an independent ≤4-step normalization oracle; CPython 3.11.15 header-parser behaviour (defects, obs-fold joins, leading/trailing OWS) directly through `http.client.parse_headers`; the RecursionError threshold (984/985) and the walk-vs-`json.loads` attribution; NaN/Infinity record invalidity under a strict parser; the F17 `Connection: close` repro; the M60 discrepancy repro; both gate runs; the red file standalone; all seven baseline-less record readers standalone; pyflakes; the manifest diff; the scope-file sha match against the moved HEAD.

**Reviewed statically only:** the docstring↔code audit for the claims already proven by the domain table (I did not re-derive determinism, `:52`); the `_CREDENTIAL_HEADERS` drop list; `send_error`'s `Connection: close` (asserted by 24 live 501 cells rather than read from CPython source).

**Deliberately skipped:** `test_handler_timeout_bounds_incomplete_body` was deselected in all 60 mutant runs (30 s+ each; round-7 practice) — no mutant in my set touches `Handler.timeout`, so it cannot mask a kill, but every mutant "SURVIVED" verdict is over 310 tests, not 311; it **did** run in both full-suite gate runs. Nothing ran on the PC (no bridge banner this session, and none is needed — stdlib HTTP server, sandbox-reproducible). I did not grade `tests/test_stage0_ci_workflow.py` internals, `build_capture_record.py` (F18 from round 7, not this lane's file), or any file outside the three in scope.

---

## Verdict

**NOT-READY.**

The gate itself is in good shape — 232/232 domain cells and 36/36 replay vectors match an independently derived contract oracle, all five round-7 non-equivalent survivors are closed by named tests, and the F1/F2/F6/F7 fixes are real and load-bearing (M46, M58, M60, M29, M41, M48 all die). But the increment ships a **live, reproducible credential leak in the component it exists to build** (F1: `X-Trace: s0-01-upstream-tok%20en-0123456789abcdef` → `200 OK` and a record whose token is recovered by `strip(unquote(...))`), the test oracle that would have caught it has the identical blind spot (F2), and **three of the code paths D5d added carry non-equivalent mutants that the suite does not kill** (F3 M59 bare-LF fold → live smuggling; F4 M57 fail-closed branch; F5 M62 token-as-JSON-key → recoverable leak).

**Blocking: R8-D5d-F1, F2, F3, F4, F5.**

Nothing in this verdict rests on anything I did not reproduce. The one claim I could not settle either way is F7 (whether round 7's M26 kill was a TCP-RST race or was removed by the F9 assertion rewrite) — I report the flip as measured and leave the cause open; it does not affect the blocking set.