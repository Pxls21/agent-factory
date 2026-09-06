# VERIFY-D5c (round 7, adversarial, Opus 5) — VERDICT: **NOT-READY**

## 0. Premise / hash check — PASS

```
HEAD 7cd83c7 transcripts: scrubbed sandbox chat digests (2026-09-06)
     5f81e34 S0-01 WIP checkpoint 7a …                    branch claude/soundbox-kit-migration-iz1jwf ✓
scratch copy $V/repo = git archive HEAD + overlay of the 2 lane files
c233822600f14bf6f8421719028bb42ece1f893b2e39c670b1b9d717ee06f15a  proofs/S0-01/tools/scripted_backend.py   ✓ pin
b7f583cc9ad613e4af5143895692d46808675cc4ce4c41346c3e20907e3c8e37  tests/test_s0_01_scripted_backend.py    ✓ pin
```
Shared tree `/home/user/agent-factory` never written (both files still hash to the pins at close; the 21 `git status` entries are lane N5c's). All work under `scratchpad/vd7`. Python 3.11.15, pytest 9.1.1, no pytest-randomly/reverse/xdist installed.

**ENOSPC window (coordinator notice).** Everything before 09:15Z is pre-window: harness 08:42, replay 08:43, jsonws 08:44, ows 08:45, domain 08:47, baseline `297 passed in 193.17s`. Affected and **discarded + re-run**: the first mut2 batch (`M00 rc=143` + 5 rc=0 lines). My earlier "incomplete tree" failure was **not** ENOSPC — the log reads `[Errno 2] No such file or directory … build_capture_record.py`, my own harness bug; rebuilt with full trees. Re-verified post-window: replay (byte-identical), domain table (0/192 mismatches, 10.4 s), and the full mutant set + a **no-op control mutant M00 = 288 passed** proving the harness sound. My trees were `cp -al` hardlink copies (26 MB total, not 120–680 MB); the disk cost was pytest TMPDIRs, since isolated per-run and deleted. All mutant trees deleted at close.

---

## 1. verify-D5b HIGH replay — all 7 CLOSED live (forged tail in the SAME sendall)

| vector | status | `HTTP/1.1 ` count | record Δ | tail served? | `Connection: close` |
|---|---|---|---|---|---|
| F1 GET /v1/models CL `-1` / `-0` / `-9999999999` / `+5` / `-2000000` | 400 ×5 | 1 | 0 | no | Y |
| F2 GET /healthz + /healthz?x=1, CL `-1`, nocred | 400 ×2 | 1 | 0 | no | Y |
| F3 TE `gzip`/`identity`/`CHUNKED`/`chunked, gzip`/`x-gzip`/`""` × GET+POST (12) | 411 ×12 | 1 | 0 | no | Y |
| F3 GET /healthz TE `gzip` nocred | 411 | 1 | 0 | no | Y |
| F4 dup TE `gzip`+`chunked` (GET), `chunked`+`gzip` (POST) | 411 ×2 | 1 | 0 | no | Y |
| F5 GET dup CL `0`+`53`, `5`+`5`, /healthz `0`+`9` nocred | 400 ×3 | 1 | 0 | no | Y |
| F6 POST dup CL `2`+`2` body `{}` | 400 | 1 | 0 | no | Y |
| F7 POST CL `2000000`/`-1`/`1_0`/`abc`/`1e3`/`0x10`/`""` | 400 ×7 | 1 | 0 | no | Y |
| F8 `Content-Length : 5` GET / POST / healthz-nocred | 400 ×3 | 1 | 0 | no | Y |

**36/36 vectors: one response, zero records, tail never parsed, close on every arm.** F9/F10 (pct-encoded, obs-folded, whitespace-split token in path / header name / header value / JSON body / raw body): whole-record-dir grep after a 17-record battery → literal token absent, pct-encoded absent, whitespace-stripped-bytes absent, `unquote(all bytes)` absent — **except** the case in F1 below.

---

## 2. Domain table — 192 cells, oracle re-derived from the contract's six rules (not from the lane's table)

**0/192 mismatches** against my independent oracle. Half-close vs no-half-close control on 4 representative cells: identical. Aggregated (all 4 routes × both credentials; `n_http`/Δ/tail as observed):

| framing case | contract-expected | lane-claimed | observed |
|---|---|---|---|
| no_cl, cl_0 | served: GET/v1/models 200·1rec (401·1 nocred); /healthz 200·0rec; POST 400·1rec (401·1) | same | **match** (n_http=2, tail served) |
| cl_n | GET 400·0rec; POST 200·1 (401·1) | same | **match** |
| cl_neg1, cl_neg0, cl_abc, cl_1e3, cl_0x10, cl_empty, cl_1_0, cl_5space, cl_over_max | 400·0rec·close·1 resp | same | **match** (72 cells) |
| cl_space5 | GET 400·0rec; POST **gate-accepted** → `_ParseError` 400·**1 rec** | report row says "400 / 400 / records 0"; lane's *code* says 1 rec | **observed 1 rec** → the lane's **report row is wrong**, its test is right |
| dup_cl_eq, dup_cl_diff | 400·0rec | same | **match** |
| te_chunked/gzip/identity/two | 411·0rec | same | **match** |
| defects (`Content-Length : 5`) | 400·0rec | same | **match** |
| expect (`100-continue`) | 417·0rec, exactly 1 response (no interim 100) | same | **match** |
| PUT / HEAD / OPTIONS × 4 routes × 2 creds (24) | 501·0rec·close·1 resp | same | **match** |

---

## 3. OWS ruling — printed `get_all` from the exact call `parse_request` makes

`http.client.parse_headers(fp, _class=http.client.HTTPMessage)`:
```
Content-Length: 5      -> get_all=['5']    defects=[]
Content-Length:  5     -> get_all=['5']    defects=[]      # leading OWS STRIPPED
Content-Length: 5␠     -> get_all=['5 ']   defects=[]      # trailing OWS KEPT
Content-Length: \t5\t  -> get_all=['5\t']  defects=[]
Content-Length:        -> get_all=['']     defects=[]
Content-Length : 5     -> get_all=None     defects=[MissingHeaderBodySeparatorDefect()]
Expect:                -> get_all=['']  get('Expect')=''            # present but FALSY
Expect: 100-continue   -> get_all=['100-continue']
X-Foo: bar / " Content-Length: 5"  -> get_all('Content-Length')=None ; items=[('X-Foo','bar\r\n Content-Length: 5')]
```
Mechanism (primary source, `email._policybase.Compat32.header_source_parse`): `value.lstrip(' \t') … .rstrip('\r\n')` — leading OWS removed, trailing SP/HTAB **not**.

**Ruling.** RFC 9110 §5.5: "A field value does not include leading or trailing whitespace." So:
- **`CL " 5"` — the lane is CORRECT.** The field value *is* `5`; the message is well-formed. Contract rule 4 is applied to what the parser hands the gate, so `fullmatch` passes → POST served, GET hits the `n>0` arm → 400. **Cannot smuggle**: live `POST CL:" N"` with an exactly-N-byte valid JSON body → 200, n_http=2, Δ=2, tail served — the tail begins exactly at the message boundary; no desync. This is *not* a discrepancy with the contract, it is the contract applied correctly; the lane should drop the "discrepancy" framing and state it in the docstring instead (F10).
- **`CL "5 "` — rejected (400), which is STRICTER than RFC 9110.** An RFC-conformant peer sending `Content-Length: 5 ` gets 400. Fail-closed, so safe, and it **cannot smuggle** (rejected + close, tail never served). Acceptable, but undocumented (F10).
- Neither OWS case can smuggle a second request. Same for `\t5\t` → 400.

---

## 4. http.server's own 501 path with a forged tail — PROVEN SAFE

Primary source (py3.11.15): `handle_one_request` calls `send_error(NOT_IMPLEMENTED)` **before** `getattr(self, 'do_'+command)`, so `_framing_gate` step 6 is unreachable; `send_error` emits `Connection: close`, which `send_header` turns into `close_connection = True`.

| method | status | n_http | Δ | tail served? | close hdr |
|---|---|---|---|---|---|
| PUT, HEAD, OPTIONS, DELETE, PATCH, TRACE, FOO on /v1/models | 501 | 1 | 0 | **no** | Y |
| PUT /v1/chat/completions + `Content-Length: 7` + body + tail | 501 | 1 | 0 | **no** | Y |
| PUT + `Expect: 100-continue` (no interim 100 — the override runs first) | 501 | 1 | 0 | **no** | Y |
| PUT /healthz nocred | 501 | 1 | 0 | **no** | Y |

Reply bytes: `HTTP/1.1 501 Unsupported method ('PUT')\r\n…\r\nConnection: close\r\nContent-Type: text/html…\r\nContent-Length: 356`. **Not a finding for safety** — but see F12: the arm is dead code and unkillable by any mutant.

---

## 5. My mutant set — 38 killed / 54 (+ no-op control + 1 double). The lane's harness is not evidence.

Control: **M00 no-op → rc=0, 288 passed** (harness sound). Every mutation asserted applied (snippet count == 1) and `py_compile`-clean; base file sha256 re-checked unchanged after every build.

| id | arm | kind | result | killing test |
|---|---|---|---|---|
|M01|1-defects|delete|KILLED|`test_framing_domain_table[defects/GET/v1/models/cred]`|
|M02|1-defects|invert|KILLED|`test_bearer_required_exact_401`|
|M03|1-defects|wrongcode 400→411|KILLED|`test_framing_domain_table[defects/…]`|
|M04|1-defects|noclose|KILLED|`test_framing_domain_table[defects/…]`|
|M05|2-te|delete|KILLED|`test_chunked_post_rejected_with_411`|
|M06|2-te|invert|KILLED|`test_bearer_required_exact_401`|
|M07|2-te|weaken to r5 `"chunked" in …`|KILLED|`test_framing_domain_table[te_gzip/…]`|
|M08|2-te|noclose|KILLED|`test_healthz_with_te_body_rejected…[with_cred]`|
|M09|3-dupcl|delete|KILLED|`test_duplicate_content_length_rejected_400[with_cred]`|
|M10|3-dupcl|boundary `>2`|KILLED|`test_duplicate_content_length_rejected_400[with_cred]`|
|M11|3-dupcl|invert|KILLED|`test_bearer_required_exact_401`|
|M12|3-dupcl|noclose|KILLED|`test_framing_domain_table[dup_cl_eq/…]`|
|M13|4a-clfmt|delete|KILLED|`test_framing_domain_table[cl_neg1/…]`|
|**M14**|4a-clfmt|`[0-9]+`→`\d+`|**SURVIVED**|— **true equivalent**: no latin-1 codepoint outside 0-9 matches `\d`, and headers decode iso-8859-1 (enumerated all 256)|
|M15|4a-clfmt|`fullmatch`→`match`|KILLED|`test_framing_domain_table[cl_1e3/…]`|
|M16|4a-clfmt|invert|KILLED|`test_bearer_required_exact_401`|
|M17|4a-clfmt|noclose|KILLED|`test_framing_domain_table[cl_neg1/…]`|
|**M18**|4b-postmax|delete|**SURVIVED**|**non-equivalent (order)**: `CL>MAX + Expect` → base 400, mutant **417**|
|**M19**|4b-postmax|`n > MAX+1`|**SURVIVED**|— true equivalent (`_read_body` rejects CL==MAX+1 identically)|
|**M20**|4b-postmax|`n >= MAX`|**SURVIVED**|**non-equivalent**: `CL == 1048576` + 1 MiB body → base **200, 1 rec**; mutant **400, 0 rec**|
|M21|4b-postmax|noclose|KILLED|`test_framing_domain_table[cl_over_max/POST/…]`|
|M22|4c-getcl|delete (serve)|KILLED|`test_get_with_body_rejected_no_smuggling`|
|M23|4c-getcl|boundary `n>1`|KILLED|`test_get_with_cl_1_rejected_400`|
|**M24**|4c-getcl|drop the `rfile.read`|**SURVIVED**|— true equivalent (live, no half-close: identical 400, n_http=1, Δ=0, 125-byte reply)|
|M25|4c-getcl|noclose|KILLED|`test_get_cl_over_max_smuggling…[with_cred]`|
|M26|4c-getcl|`read(0)`|KILLED|`test_framing_domain_table[cl_over_max/GET/healthz?x=1/nocred]`|
|M27|5-expect|delete|KILLED|`test_framing_domain_table[expect/…]`|
|M28|5-expect|invert|KILLED|`test_bearer_required_exact_401`|
|**M29**|5-expect|narrow to `== "100-continue"`|**SURVIVED**|**non-equivalent**: `Expect: bogus` and `Expect: 100-Continue` → base **417/0 rec**; mutant **200, 2 rec, tail SERVED**|
|M30|5-expect|noclose|KILLED|`test_framing_domain_table[expect/…]`|
|**M31**|6-501|delete|**SURVIVED**|— true equivalent, dead code|
|M32|6-501|invert|KILLED|`test_bearer_required_exact_401`|
|**M33**|6-501|wrongcode 501→200|**SURVIVED**|— true equivalent, dead code|
|M34|_reject|drop `Connection: close` hdr|KILLED|`test_framing_domain_table[cl_n/GET/…]`|
|**M35**|_reject|drop `close_connection = True`|**SURVIVED**|— true equivalent (`send_header('Connection','close')` sets it; primary source)|
|M36|_reject|drop both|KILLED|`test_healthz_with_te_body_rejected…[with_cred]`|
|M37|expect100|delete override|KILLED|`test_framing_domain_table[expect/…]`|
|**M38**|carries|drop `t in s`|**SURVIVED**|— true equivalent (subsumed by `unquote`)|
|**M39**|carries|drop `t in unquote(s)`|**SURVIVED**|— true equivalent (subsumed by `unquote(stripped)`)|
|**M40**|carries|drop `t in stripped`|**SURVIVED**|— true equivalent (subsumed by `unquote(stripped)`)|
|**M41**|carries|drop `t in unquote(stripped)`|**SURVIVED**|**non-equivalent**: pct-encoded **and** whitespace-split token → base **400**; mutant **200**|
|M42|carries|`return False`|KILLED|`test_credential_in_query_string_returns_400`|
|M43|screen|drop path screen|KILLED|`test_credential_in_query_string_returns_400`|
|M44|screen|drop header-NAME screen|KILLED|`test_credential_in_header_name_returns_400`|
|M45|screen|drop header-VALUE screen|KILLED|`test_credential_in_custom_header_returns_400`|
|M46|screen|drop body screen|KILLED|`test_credential_in_body_returns_400`|
|M47|screen|drop raw_body screen|KILLED|`test_malformed_json_with_token_in_body_redacted`|
|**M48**|screen|auth exempt by **prefix**|**SURVIVED**|**non-equivalent, LEAK**: `Authorization-X: Bearer <tok>` / `Authorizationfoo:` → base **400 + sanitized rec**; mutant **200 + token IN the record**|
|M49|screen|leak path not sanitized|KILLED|`test_leak_record_does_not_contain_token`|
|M50|auth|`==`→`startswith`|KILLED|`test_bearer_superstring_rejected_401`|
|M51|healthz|`==`→`startswith`|KILLED|`test_healthz_exact_path_no_prefix_match`|
|**M52**|readbody|`> MAX+1`|**SURVIVED**|— true equivalent (unreachable behind the gate)|
|**M53**|readbody|drop `fullmatch`|**SURVIVED**|— true equivalent (unreachable behind the gate)|
|M54|readbody|drop short-body check|KILLED|`test_short_body_returns_400_no_record`|
|**M55**|**double**: gate 4b **+** `_read_body` max limb|—|**KILLED**|`test_content_length_oversized_rejected` (5.93 s) — so the masking pair *is* jointly covered; live: base 400/0 rec, mutant 200/1 rec on a 1.5 MB body|

**16 survivors = 11 proved-equivalent + 5 hollow greens (M18, M20, M29, M41, M48)**, each with a distinguishing input reproduced live against BASE and the mutant. Per arm: 1-defects 4/4 · 2-te 4/4 · 3-dupcl 4/4 · 4a-clfmt 4/5 (1 equiv) · 4b-postmax 1/4 · 4c-getcl 4/5 (1 equiv) · 5-expect 3/4 · 6-501 1/3 (2 equiv, dead code).

---

## 6. Findings

### R7-D5c-F1 — **BLOCKING, SOLID** — credential leak: whitespace-obfuscated token in a *valid* JSON body is recorded
`proofs/S0-01/tools/scripted_backend.py:146-148` screens `json.dumps(body)`; `do_POST:323` calls `state.record(...)` **without** `raw_body=`. `raw_body=` is passed at exactly one of three record call sites (`:313`, the `_ParseError` arm) — `:292` (GET) and `:323` (POST success) never pass it. `json.dumps` re-escapes TAB/LF/CR/FF/VT into two-character sequences, so `re.sub(r"\s+","",…)` cannot rejoin the token.
**Observed vs expected** — token split by one char inside `{"note": …}` on `POST /v1/chat/completions`:
```
SPACE -> 400, sanitized                         (json.dumps keeps a real space)
TAB   -> 200 OK, 1 record, body recorded as "<TOK-A>\t<TOK-B>"   RECOVERABLE
LF, CR, FF, VT -> 200 OK, 1 record              RECOVERABLE
controls: same value in a header VALUE -> 400 ; in a NON-JSON raw body -> 400
```
Recovery is one line: `re.sub(r"\s+","", json.loads(rec)["body"]["note"]) == TOKEN`. Expected per the contract ("applied … to the serialized JSON body **and the raw body**") and per audit P1 ("rejection status does not prove the secret stayed out of evidence"): 400 + `{"credential_in_unexpected_location": true}`. **Minimal fix:** have `_read_body` stash the raw bytes and pass `raw_body=` at `:323` (and `:292`).
**Red test to add:**
```python
def test_credential_whitespace_split_in_valid_json_body_returns_400(backend):
    port = backend["port"]; mid = len(TOKEN)//2
    for sep in ("\t", "\n", "\r", "\f", "\v"):
        n0 = len(list(backend["rec"].glob("*.json")))
        body = json.dumps({"model":"s0-01-pong","messages":[],"note":TOKEN[:mid]+sep+TOKEN[mid:]})
        resp = _raw_request(port, (f"POST /v1/chat/completions HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
            f"Authorization: Bearer {TOKEN}\r\nContent-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n\r\n{body}").encode())
        assert resp.split(b"\r\n",1)[0] == b"HTTP/1.1 400 Bad Request"
        recs = sorted(backend["rec"].glob("*.json")); assert len(recs) == n0 + 1
        assert json.loads(recs[-1].read_text())["body"] == {"credential_in_unexpected_location": True}
        assert TOKEN not in re.sub(r"\s+", "", recs[-1].read_text())
```

### R7-D5c-F2 — **BLOCKING, SOLID** — the `Expect` arm tests truthiness, not presence
`scripted_backend.py:223` `if self.headers.get("Expect"):`. `get_all("Expect")` on `Expect:` returns `['']` (present) but `get()` returns `''` (falsy). Arms 2 and 3 use `get_all`; arm 5 was left on `get`.
**Observed vs expected:** `GET /v1/models` + `Expect:` (empty) + forged tail → **200 OK, n_http=2, Δ=2 records, tail SERVED**; contract and docstring `:30` say "Expect header present -> 417 + close". Corroborated from the other side by **M29** (narrowing the arm to `== "100-continue"`) surviving all 288 tests while `Expect: bogus` and `Expect: 100-Continue` flip 417 → 200 + tail served. The domain table's only `expect` row is `Expect: 100-continue`. **Fix:** `if self.headers.get_all("Expect") is not None:`.
**Red test:** `test_expect_header_any_value_rejected_417` — parametrize `["", "bogus", "100-Continue", "100-continue"]` × GET/POST, assert `resp.split(b"\r\n",1)[0].split()[1] == b"417"`, `resp.count(b"HTTP/1.1 ") == 1`, `count_after == count_before`, `b"Connection: close" in resp`.

### R7-D5c-F3 — **BLOCKING, SOLID** — the contract's named auth-exemption control is missing
`scripted_backend.py:142` `if k.lower() != "authorization":` is correct; nothing tests it. `tests/…:430` parametrizes only `api-key, x-api-key, cookie, x-auth-token, proxy-authorization` — **no name beginning with `authorization`**. **M48** (`!= "authorization"` → `not startswith("authorization")`) survives all 288 tests; live under M48, `Authorization-X: Bearer <token>` and `Authorizationfoo: …` return **200 with the token written into the record** (base: 400 + sanitized). The contract names this control verbatim.
**Red test:** `test_authorization_prefixed_header_name_is_not_exempt` — parametrize `["Authorization-X", "Authorizationfoo", "X-Authorization"]`, send `<name>: Bearer <TOKEN>`, assert status `400`, `count_after == count_before + 1`, `json.loads(recs[-1].read_text())["body"] == {"credential_in_unexpected_location": True}`, `TOKEN.encode() not in recs[-1].read_bytes()`.

### R7-D5c-F4 — **BLOCKING, SOLID** — `_carries_secret`'s 4th normalization is untested
`scripted_backend.py:122`. **M41** (drop `t in unquote(stripped)`) survives; the distinguishing input is a token that is *both* percent-encoded *and* whitespace-split: base **400**, mutant **200** with the value persisted and recoverable by the helper's own normalization. (M38/M39/M40 are provable equivalents — `unquote(stripped)` subsumes them — so "each normalization must red" is only achievable for the 4th; report that honestly rather than as 4 gaps.)
**Red test:** `test_credential_percent_encoded_and_whitespace_split_in_header_value` — `val = enc[:k] + " \t " + enc[k:]` where `enc = TOKEN[:-1] + "%%%02x" % ord(TOKEN[-1])`; assert `400`, exact `count_before + 1`, marker body, token absent under all four normalizations of the record bytes.

### R7-D5c-F5 — **SOLID** — `MAX_CONTENT_LENGTH` boundary untested on the accepting side
`scripted_backend.py:214`. **M20** (`n > MAX` → `n >= MAX`) survives. Live: `POST` with `Content-Length: 1048576` and a 1 MiB valid JSON body → base **200 OK, 1 record**; mutant **400, 0 records**. No test sends `CL == MAX`.
**Red test:** `test_post_content_length_exactly_max_is_accepted` — body padded with trailing spaces to exactly `MAX_CONTENT_LENGTH`, assert `200`, `count_after == count_before + 1`. (Pair with `MAX+1 → 400`, already covered.)

### R7-D5c-F6 — **SOLID** — obs-folded headers pass the allow-list
No gate arm inspects folded field values; `headers.defects` is empty for obs-fold (compat32 accepts it) and `get_all` sees one joined header.
**Observed vs expected:**
```
GET /v1/models  "X-Foo: bar" / " Content-Length: 5"      -> 200 OK, n_http=2, Δ=2, tail SERVED
POST                same                                  -> 400 (body-shape), n_http=2, Δ=2, tail SERVED
GET             "X-Foo: bar" / " Transfer-Encoding: chunked" -> 200 OK, n_http=2, Δ=2, tail SERVED
parser: items=[('X-Foo', 'bar\r\n Content-Length: 5')]  get_all('Content-Length')=None
```
RFC 9112 §5.2: a recipient **MUST** reject the message or replace each obs-fold with SP. A CL/TE hidden in a fold is the classic desync primitive; the credential screen *does* catch a folded token (400) — it is the *framing* side that is open. Exploitability here is low (OmniRoute → backend over loopback, no intermediary), but the contract's whole premise is an allow-list over "exactly one well-formed shape", and this is the enumerated list's blind spot.
**Red test:** `test_obs_folded_header_rejected_400` — send `X-Foo: bar\r\n Content-Length: 5` (and the TE variant) + forged tail; assert `400`, `n_http == 1`, `Connection: close`, `count_after == count_before`. Implementation: reject when any `headers.items()` value contains `\r` or `\n`.

### R7-D5c-F7 — **SOLID (spec gap, not an implementation deviation)** — double percent-encoding defeats the screen
`scripted_backend.py:122` applies exactly one `unquote`, as the contract specifies. Live: `X-Trace: <tok-prefix>%25<hex>` → **200 OK, 1 record**; the credential is recovered by two `unquote` passes over the record bytes (single-encoded control → 400). Same class as F1 (one normalization layer, two encoding layers). Ruling: the *implementation matches the contract*; the *contract* is a deny-list of two encodings. **Fix:** iterate `unquote` to a fixed point (bounded, e.g. ≤3 passes) or reject any header/body value that changes under `unquote`.
**Red test:** `test_credential_double_percent_encoded_in_header_value_returns_400`, same shape as F4's.

### R7-D5c-F8 — **SOLID** — F18 not closed; the report says `not_done: none`
`tests/test_s0_01_scripted_backend.py:174` `test_requests_are_recorded_with_fingerprint_and_token_absent_from_argv` makes **no request of its own** and asserts on `recs[-1]`. Run alone:
```
tests/test_s0_01_scripted_backend.py:176: AssertionError: no request records written
E       assert []                                             1 failed in 0.22s
```
Three neighbours I isolated (`test_record_null_fingerprint_when_no_bearer`, `test_healthz_unauthenticated_and_not_recorded`, `test_received_at_microsecond_format_kills_truncation_mutant`) pass alone. Contract: "Every test is self-contained (F18)". **Fix:** issue the POST inside the test before reading `recs[-1]`.

### R7-D5c-F9 — **SOLID** — F16/F17 violated in the tests this lane added
Contract: "Exact assertions only (F16)… using `== count_before + k`, never `>`."
- **18** `assert len(recs) > count_before` remain, **4 of them new D5c tests**: `:1663, :1684, :1709, :1737` (plus `:472, 551, 569, 593, 732, 756, 787, 896, 910, 925, 952, 965, 1271, 1338`).
- **13** substring status assertions, all in new D5c code: `:1575` `assert str(expected_status).encode() in status_line` (the domain table's own oracle — 192 cells graded by substring), `:1625, 1657, 1682, 1707, 1731, 1773, 1789, 1810, 1829, 1848, 1867, 1885`. Pre-existing tests in the same file use `resp.split(b"\r\n",1)[0] == b"HTTP/1.1 400 Bad Request"` — the new code regressed the file's own standard.
**Fix:** `assert status_line.split()[1] == str(expected_status).encode()` and `assert len(recs) == count_before + 1`.

### R7-D5c-F10 — **SOLID** — the docstring is false on the load-bearing security claim (F15 not closed)
- `:36` "…serialized JSON body, and **raw body**" — the raw body reaches `record()` at 1 of 3 call sites (`:313`); never at `:292`/`:323`. This is the sentence F1 falsifies.
- `:30` "Expect header present -> 417 + close" — false for `Expect:` (empty). See F2.
- `:26` "must match `[0-9]+` (no sign, **space**, underscore, exponent)" — does not say that leading OWS is parser-stripped so `Content-Length:  5` **is** accepted on POST, nor that trailing OWS is kept and therefore rejected more strictly than RFC 9110 §5.5. The lane files this as "discrepancy #1" in its report instead of in the artifact — a hollow green in prose.
- `:31` presents arm 6 as part of the gate without saying it is unreachable (F12).

### R7-D5c-F11 — **SOLID** — docstring `:40-42` promises evidence that is never persisted
"…duplicate non-framing headers collapse to the last value in the record … evidence combed from the full headers object when needed". `record()` writes only `clean` (`:159-160`) at the single write site `:164`; the full `headers` object is per-request and discarded. After the response, the dropped duplicate values are unrecoverable from any artifact. The F23 *choice* (flat dict + documented collapse) is within contract; the *justification sentence* is false.

### R7-D5c-F12 — **SOLID** — gate arm 6 is unreachable dead code and unkillable
`scripted_backend.py:228-230`. `self.command` can only be `GET`/`POST` inside `do_GET`/`do_POST`; `handle_one_request` sends 501 before dispatch (primary source). **M31** (delete) and **M33** (501→200) both survive all 288 tests. The contract said "keep it explicit **and tested**" — it cannot be tested as written. The behaviour it claims is delivered by http.server and is proven safe (§4). **Fix:** either delete the arm and cite the http.server proof in the docstring, or move it into an overridden `handle_one_request`.

### R7-D5c-F13 — **SOLID** — arm 4b has no independent negative control (contract's "each arm must red" unmet)
`test_negative_control_post_cl_overmax_gate_arm:1854` cannot red on arm deletion: **M18** (delete gate arm), **M19** (`>MAX+1`), **M52**, **M53** all survive because `_framing_gate:214` and `_read_body:268` mask each other. The joint mutant **M55** *is* killed (`test_content_length_oversized_rejected`, 5.93 s; live 200 + 1 record on a 1.5 MB body), so the *behaviour* is covered — this is redundancy, not a hollow green. Two residues: M18 changes the observable status when combined with `Expect` (base 400 → mutant 417, contract order says 400), and the arm-4b "negative control" test is vacuous. **Fix:** rename it to what it actually proves, and add the ordering assertion `CL>MAX + Expect: 100-continue → 400`.

### R7-D5c-F14 — **SOLID** — two negative controls are weaker than the domain cells they duplicate
`test_negative_control_defects_gate_arm:1760` sends **no forged tail** and asserts neither the record delta nor `Connection: close`. `test_negative_control_expect_gate_arm:1873` asserts no record delta. Both would still pass against a gate that rejects but leaks a record or leaves the connection open.

### R7-D5c-F15 — **SOLID** — F20 only partially closed
`tests/…:650-651` `assert elapsed >= 15` / `<= 75` with "(30s)" hand-copied into the comment. The contract asked for a bound derived from the handler's configured timeout; this is a *wider hard window*, not a derived one — changing `Handler.timeout` (`scripted_backend.py:176`) to 120 reds the test for the wrong reason. Costs **30.03 s** of the 193 s suite. **Fix:** import the module and bound by `Handler.timeout * 0.5 … * 2.5`.

### R7-D5c-F16 — **SOLID** — four inaccuracies in the lane report
1. Domain-table row `cl_space5` claims "records (rejected) = 0 / n/a" for POST; POST `cl_space5` is **gate-accepted**, hits `_ParseError`, and writes **1 record** (Δ=2 with the tail). The lane's own `_build_domain_table` sets `records = 1` — the prose contradicts the code.
2. "18 killed / 20 run … 3 wrongcode mutants survived due to inverted check-function logic in the runner but provably killed." An inverted check in a mutation runner is a **broken oracle**; a 20-mutant run cannot cover "≥3 per gate arm" across 7 arms plus 4 normalizations plus close-plumbing plus `handle_expect_100` plus the MAX boundary. My independent 54-mutant set: **38 killed, 16 survivors, 5 of them non-equivalent**.
3. Adjacent item ":1230 sends 1 MB padding × 4 cases (4MB)". Actual: `:1231` `b"X" * 1_048_577` × **2** parametrizations = 2,097,154 B, **plus** 6 domain cells (`cl_over_max` × 3 GET routes × 2 creds) at `b"X" * 1_048_576` = 6,291,456 B — **≈ 8.0 MiB across 8 invocations**, not 4 MB across 4.
4. "real legs have 27 files". The six committed golden legs hold **15–18** entries (`cancel` 18, `shutdown` 17, `two-users` 16, `run-1`/`run-2` 15, `manifests` 1).

### R7-D5c-F17 — **SOLID, INFO** — ~65 % of suite wall time is dead socket-recv timeout
`--durations=20`: 19 tests at **5.01 s** + 1 at **30.03 s** = **125 s of the 193 s run**. Every gate-*accepted* domain cell and every credential-leak test blocks the full `settimeout(5)` because served and leak responses go through `_send_json` (`:239-247`), which sends no `Connection: close`, so the socket stays open until the client's timeout. My control table shows `socket.shutdown(SHUT_WR)` after `sendall` yields **identical** verdicts on `cl_over_max/GET`, `te_gzip/GET`, `cl_n/POST`, `dup_cl_diff/GET` (with and without half-close) — it would also remove the need for most of the 8 MiB of padding in F16.3.

### R7-D5c-F18 — **SOLID, INFO (adjacent, report-only)** — `test_build_capture_record_roundtrip_check:832`, AF-AP-42 quantified
`build_capture_record.py` consumes **11** inputs: 9 named files (`timeline.jsonl`, `runtime-identity.json`, `env.json`, `startup-line.txt`, `hermes-model.txt`, `buzzacp.log`, `process-scan-after.txt`, `buzz-acp.pid`, `buzz-acp.exit`) **plus two directory scans** (`mentions/` `*.event.json` at `:104-108`, `upstream-records/` at `:119`). The hand-typed fixture supplies **7**. **Never exercised: `buzzacp.log`, `process-scan-after.txt`, `mentions/` dir scan, `upstream-records/` dir scan.** So any change to how mentions or upstream-records are folded into `capture.json` — ordering, hashing, tag derivation at `:108` — round-trips green. (Separately worth the main loop's attention: the committed golden legs contain none of `timeline.jsonl`, `env.json`, `runtime-identity.json`, `buzz-acp.pid`, `mentions/`, `upstream-records/` — they carry `frames-*.jsonl` and top-level `mention-*.json` instead. Not this lane's file; flagged, not graded.)

---

## 7. Gate — run twice on my copy, verbatim

```
pytest-exit: 0
pytest-summary: 297 passed in 193.04s (0:03:13)
pytest-exit: 0
pytest-summary: 297 passed in 192.98s (0:03:12)
```
Command: `bash scripts/test_summary.sh tests/test_s0_01_scripted_backend.py tests/test_stage0_ci_workflow.py`, wall 3m13.297s / 3m13.219s. Reproduces the lane's `297 passed`.

**pyflakes:** `python3 -m pyflakes proofs/S0-01/tools/scripted_backend.py tests/test_s0_01_scripted_backend.py` → **rc=0**, no output.

**tmp_path hygiene:** the scratch copy has no `.git`, so I diffed a full file manifest before/after both gate runs. Delta = **exactly 2 files, both `__pycache__` bytecode**:
```
> ./proofs/S0-01/tools/__pycache__/scripted_backend.cpython-311.pyc 29144
> ./tests/__pycache__/test_stage0_ci_workflow.cpython-311-pytest-9.1.1.pyc 22309
```
No test wrote outside `tmp_path`. Two full gate runs cost 1.3 MB of pytest tmp.

---

## 8. Verdict

**NOT-READY.** Blocking: **R7-D5c-F1** (live credential leak into the persisted record on the valid-JSON POST path — the exact class audit P1 required closed, and the docstring claims it *is* closed), **F2** (the `Expect` allow-list arm accepts a present-but-empty header; M29 proves the arm's domain is untested), **F3** (the contract's named `authorization-x` control is absent; M48 leaks the token), **F4** (M41: the 4th normalization untested, 400→200).

Non-blocking but should ship in the same repair: F5, F6, F7, F8, F9, F10, F11, F13, F14, F15, F16.

The framing gate itself is in good shape: **all 36 verify-D5b HIGH vectors are closed live**, the 192-cell domain table matches an oracle I re-derived from the contract with **0 mismatches**, http.server's own 501 path is proven closed against a forged tail, and 38 of 54 mutants die. Every open finding is in the **credential screen** and in **test/report hygiene**, not in the framing allow-list.

**Reproduced (live, this session):** all 36 D5b vectors; the 192-cell domain table (twice, pre- and post-ENOSPC, identical); the OWS `get_all` values; the 501 path across 7 methods; every one of the 54 mutants plus a no-op control and a double mutant; BASE-vs-mutant distinguishing inputs for all 5 non-equivalent survivors; the F18 isolation failure; both gate runs; pyflakes; the file-manifest delta.
**Reviewed statically (mechanism re-derived from primary source, not executed):** `http.server.handle_one_request` / `send_error` / `Compat32.header_source_parse` (each then confirmed by a live probe).
**Deliberately skipped:** OmniRoute reachability of the obs-fold (F6) and double-encoding (F7) vectors — that needs the PC bridge, and no bridge banner exists this session; both are reported with sandbox-only evidence and their exploit preconditions stated. I did not re-grade lane N5c's files, the golden legs, or `build_capture_record.py` itself (out of scope; F18 flags what I saw).

Scratch, probes and mutant definitions: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vd7/work/` (`harness.py`, `replay_d5b.py`, `probe_jsonws.py`, `probe_ows.py`, `domain.py`, `mutants.py`, `build_mutants2.py`, `run_one.sh`, `triage.py`). Mutant trees deleted; `/home/user/agent-factory` untouched.