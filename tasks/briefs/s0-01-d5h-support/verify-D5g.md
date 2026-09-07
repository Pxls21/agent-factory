# VERIFY-D5g — round-10 adversarial grade of lane D5g (S0-01 scripted backend credential screen)

## Premise (verified, not assumed)

| item | value |
|---|---|
| PIN | `96f5c9a452cab77329de7c780a6c508e3845b86e` — subject `S0-01 WIP checkpoint 8l: ... (lane D5g) — REVIEW-PENDING, nothing minted` |
| shared-tree HEAD at dispatch / at close | `4a54a8b` -> advanced to `9fe6691` DURING this run (other lanes committing) |
| `git diff --stat 96f5c9a HEAD -- <3 scope files>` | EMPTY at both `4a54a8b` and `9fe6691` — the graded bytes are the PIN's |
| PIN parent | `5f3fe0b` |
| lane report | `tasks/briefs/s0-01-d5g-support/D5g-report.md` |
| scratch copy | stale `vd10/repo` DELETED, re-extracted `git archive 96f5c9a | tar -x`, `git init` + base commit |
| copy hashes | backend `841b0963f74e29465d86e17c7d9147af2d969cbbd24d976db499b4b41ce23468` (= report), main `c204cb13...`, red `67e2e8ce...`; 597/2016/645 lines (= report) |
| `df -h /` before first batch | `/dev/vda 252G 24G 14G 65% /` (after: 66%) |
| interpreter | `python3` = `/usr/local/bin/python3`, 3.11.15, pytest 9.1.1, pyflakes 3.4.0 |
| shared tree | read-only git only (`show`/`diff`/`log`/`status`); its dirty set (`tests/test_s0_01_acp_probe.py`, `tests/test_s0_01_frame_tee.py`, `tasks/briefs/s0-01-n5g-support/N5g-report.md`) untouched. One other lane's live backend (pid 29807, record-dir under `/tmp/pytest-of-root`) left running; I killed only my own probe backend (record-dir under `/tmp/vd10p*`). |

## Gate runs — pasted verbatim

```
RUN 1   460 passed in 143.56s (0:02:23)   pytest-exit: 0
RUN 2   460 passed in 143.21s (0:02:23)   pytest-exit: 0
RED STANDALONE  119 passed in 40.49s      pytest-exit: 0
pyflakes (3 files)  rc: 0
git status --porcelain on my copy: EMPTY before and after every batch
/tmp literal grep in the 3 scope files: rc=1 (no hits)
exact-reason greps: "in body" main=2 red=0 | "startswith(" main=2 red=0 backend=2 | " or " main=6 red=0
baseline-count claim re-derived: parent blobs collect-only = 442 tests -> 442 + 18 = 460 OK
```

## R10-A — the two round-9 leaks

Red-green **kept the HEAD tests and reverted only the implementation to the parent blob** (the brief's
literal "swap all three files to the parent's blobs" is degenerate — the new tests vanish).
Parent impl + HEAD tests, 35 selected tests:

```
6 failed, 29 passed in 40.66s
FAILED ...::test_credential_raw_utf8_zero_width_in_header_returns_400[ZWSP]
FAILED ...[BOM] [SOFT_HYPHEN] [WORD_JOINER] [NBSP] [IDEOGRAPHIC_SPACE]
  -> AssertionError: assert b'HTTP/1.1 200 OK' == b'HTTP/1.1 400 Bad Request'
```

- **Raw-UTF-8 family: genuinely red on the parent, green at HEAD** (6/6). Mutant `M_UTF8_DEL` dies on
  `[ZWSP]`. Confirmed.
- **V3 (`seen` -> last layer) was never a parent-state leak** — the parent already returned `seen`; it is a
  mutant only. The lane report frames it correctly ("mutant copy of backend"). `M_SEEN` dies on
  `R::test_credential_plus_split_with_pct2520_suffix_returns_400` (reproduced, batch 1).
- **12 of the 18 new tests were green on the parent** (controls, not regression proofs):
  `test_credential_plus_split_with_pct2520_suffix_returns_400`,
  `test_record_text_carries_no_token_under_any_normalization`, the 4 new `header_name` depth-5 cases,
  `test_bound_exceeded_blanks_the_record`, `test_saturating_junk_is_served`,
  `test_json_safe_does_not_mutate_request_body`, and the 3 new oracle vectors (the oracle lives in the test
  file, so its red state needs the parent ORACLE — reproduced separately as O3/O_JSONBLIND).

### Sink x separator matrix — F1 vector `TOKEN[:mid] + SEP + TOKEN[mid:] + "-%25252541"`, live subprocess

7 sinks x 5 separators = 35 cells. **All 35: `HTTP/1.1 400 Bad Request`, record body `== MARKER`, literal
TOKEN bytes absent from the record file, oracle reports absent.** FAILURES: none.

Cell legend `status/record-body/raw-token-absent/oracle-absent`:

| sink \ sep | %20 | %09 | %0A | %0d | + |
|---|---|---|---|---|---|
| header_value | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |
| header_name  | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |
| query        | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |
| path         | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |
| json_value   | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |
| json_key     | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |
| json_list    | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes | 400/MARKER/yes/yes |

### Raw-byte separators on the wire (`utf8_redecode`: fail closed or fail open?) — THE BLOCKING RESULT

| separator bytes | header_value | header_name | raw/JSON body |
|---|---|---|---|
| `e2 80 8b` ZWSP | **400 + MARKER** | 400, NO RECORD (gate) | 400 + MARKER |
| `ef bb bf` BOM | **400 + MARKER** | 400, NO RECORD | 400 + MARKER |
| `c2 ad` soft hyphen | **400 + MARKER** | 400, NO RECORD | 400 + MARKER |
| `e2 81 a0` word joiner | **400 + MARKER** | 400, NO RECORD | 400 + MARKER |
| `c2 a0` NBSP | **400 + MARKER** | 400, NO RECORD | 400 + MARKER |
| `e3 80 80` ideographic space | **400 + MARKER** | 400, NO RECORD | 400 + MARKER |
| `c0 a0` overlong space | **200 OK, VERBATIM** | 400, NO RECORD | 400 (`<invalid json>`) |
| `80` lone continuation | **200 OK, VERBATIM** | 400, NO RECORD | 400 (`<invalid json>`) |
| `e2 80 80 80` valid sep + 1 junk byte | **200 OK, VERBATIM** | 400, NO RECORD | 400 (`<invalid json>`) |
| `7f` DEL | **200 OK, VERBATIM** | 400, NO RECORD | 200 OK, VERBATIM |

`utf8_redecode` **fails OPEN** on every invalid-UTF-8 input: `except (UnicodeEncodeError,
UnicodeDecodeError): return x` (`scripted_backend.py:127-128`). Decisive paired demo, identical on
CPython 3.11.15 / 3.12.3 / 3.13.12 (server run under each):

```
e2 80 80  = U+2000 EN QUAD (valid)   -> HTTP/1.1 400 Bad Request   MARKER (redacted)
e2 80 80 + 80 (one junk byte)        -> HTTP/1.1 200 OK            VERBATIM; lenient-decode recovers TOKEN = True
e2 80 8b  = U+200B ZWSP (valid)      -> HTTP/1.1 400 Bad Request   MARKER (redacted)
e2 80 8b + 80 (one junk byte)        -> HTTP/1.1 200 OK            VERBATIM
c2 a0     = U+00A0 NBSP (valid)      -> HTTP/1.1 400 Bad Request   MARKER (redacted)
c2 a0 + 80 (one junk byte)           -> HTTP/1.1 200 OK            VERBATIM; lenient-decode recovers TOKEN = True
```

Record dumps and recovery, from the served-200 cases (repr shown with escapes; the record file holds the
latin-1 characters that `http.server` produced):

```
[OVERLONG_c0a0]  record x-trace : 's0-01-upstream-tokÀ\xa0en-0123456789abcdef'
[LONE_CONT_80]   record x-trace : 's0-01-upstream-tok\x80en-0123456789abcdef'
[MIXED_e280_80]  record x-trace : 's0-01-upstream-tokâ\x80\x80\x80en-0123456789abcdef'
  latin1->utf8 errors=ignore  + strip \s  -> token recovered = True   (all three)
  latin1->utf8 errors=replace + strip \s  -> token recovered = True   (all three)
  drop non-ASCII bytes        + strip \s  -> token recovered = True   (all three)
```

Same leak through a **fully valid, well-formed UTF-8 JSON body** (no wire trickery needed) — separator
written as an ordinary JSON escape:

```
vector (JSON escape used as the separator)  status  record body   oracle absent  lenient recovers TOKEN
         (lone C1)                    200     verbatim      True           True
À    (overlong pair)              200     verbatim      True           True
â (mixed)            200     verbatim      True           True
​         (control, must 400)          400     MARKER        True           -
```

## R10-B — the bound pinned from both sides; accepted risk

Live, on the real backend:

```
X-Trace: %25252540   -> (200, served-verbatim)      <- D5f-F3 correction confirmed
X-Trace: %25252541   -> (400, MARKER-blanked)
X-Trace: %252540     -> (200, served-verbatim)
X-Trace: %2525252540 -> (400, MARKER-blanked)
X-Trace: %252B       -> (200, served-verbatim)      <- lower pin
X-Trace: %25252B     -> (400, MARKER-blanked)
X-Trace: %2525252B   -> (400, MARKER-blanked)
```

- MC1 (depth 5->4) dies on `B::test_saturating_junk_is_served` (main:1976). MC2 (depth 5->6) dies on
  `B::test_bound_exceeded_blanks_the_record` (main:1954). Both reproduced.
- The lane's correction of D5f ("MC1 TIGHTENS, MC2 LOOSENS — they move in OPPOSITE directions") is
  **correct** and is stated in the test docstring at main:1957-1958.
- Docstrings name `%25252541` at `scripted_backend.py:47` and `:115`. Verified correct against the live
  behaviour above.

## R10-C — the oracle

D5f Table 2 re-run at HEAD (`served` = 200 + verbatim; oracle = `_absent_under_all_normalizations(record_text)`):

| vector | sink | backend at HEAD | oracle on record | lenient decode recovers |
|---|---|---|---|---|
| NBSP U+00A0 raw | json_value | 400 REDACTED | ABSENT | - |
| ideographic space U+3000 | json_value | 400 REDACTED | ABSENT | - |
| soft hyphen raw UTF-8 | header_value | **400 REDACTED (was `served`)** | ABSENT | - |
| ZWSP/BOM raw UTF-8 | header/body | **400 REDACTED (was `served`)** | ABSENT | - |
| double `+` | json_value | 400 REDACTED | ABSENT | False |
| `%25%32%30` | json_value | 400 REDACTED | ABSENT | False |
| plain token | json_value | 400 REDACTED | ABSENT | False |
| fullwidth percent x2 | json_value | served | ABSENT | False |
| `%u200b` | json_value | served | ABSENT | False |
| `&#8203;` | json_value | served | ABSENT | False |
| `%2a` / `%2A` | json_value | served | ABSENT | False |
| token across two JSON string values | body | served | ABSENT | False |
| **`` / `À ` / `â`** | json_value | **served** | **ABSENT** | **True** |

**Oracle-detects-but-backend-served: `[]` — still empty** (no oracle>impl violation).
**New row class: backend-served + oracle-absent + token recoverable by a one-line lenient decode** — the
oracle inherits the implementation's fail-open `utf8_redecode`, so it cannot catch what the impl misses.
That is exactly the "strictly wider" property the D5f ruling required, and it is not satisfied on this axis.

- JSON-blindness matrix: the record-shaped row (`'{"body": "s0-01-upstream-tok\\ten-..."}'` expecting
  `False`) is present at red:405 and `ORACLE-JSONBLIND` dies on `[json_escaped_tab]`. All record-shaped
  rows now DETECT.
- Ruling 2(b): `R::test_record_text_carries_no_token_under_any_normalization` (red:629) is a BACKEND test
  killed by O1 — reproduced:
  `[O1] SUMMARY: 9 failed, 110 passed in 40.68s` with
  `FAILED ...::test_record_text_carries_no_token_under_any_normalization`.
- O3 dies on `[plus_split]` and `[pct2b_split]`. O2 (drop `unquote` from the oracle) SURVIVES and is
  equivalent **for this token** (`unquote_plus(x)` == `unquote(x.replace('+',' '))`; the fixture token
  contains no `+` and no space, and `strip_ws` is in the op set, so every `unquote`-reachable form's token
  containment is preserved). 22,073-vector differential over `%`/`+`/`2`/`5`/`0`/`4`/`B`/`a`/`b` alphabets:
  0 detection differences. The equivalence is **token-dependent** — a token containing `+` would break it.
- **O_UTF8 (drop `utf8_redecode` from the oracle) SURVIVES the whole red file (119 passed)** and is
  provably NON-equivalent:
  ```
  mojibake text (latin-1 view of a UTF-8 ZWSP): 's0-01-upstream-tokâ\x80\x8ben-0123456789abcdef'
  oracle WITH utf8_redecode    -> absent? False   (detects)
  oracle WITHOUT utf8_redecode -> absent? True    (blind)
  record-shaped WITH -> False ; record-shaped WITHOUT -> True
  ```
  The op was ADDED to the oracle this round with **no self-test vector**.

## R10-D — hygiene, structure, cost, interpreters

- `header_name` in the depth-5 parametrisation: red:458-459, 6 sinks x 4 vectors = **24 cases**, all green;
  M_HDRNAME dies on `[header_name-d5_space]`. OK
- `except RecursionError` arm: **gone** (`grep -n RecursionError` -> only comments). OK
- `_json_safe`: iterative (`while stack`), copy-on-write root at backend:299. Structurally OK — but see F2.
- `math.isfinite` negative control: there is **no `handler_timeout` knob** — `timeout = 30` is a hardcoded
  class attribute (backend:334). The only finite-float knob is `--slow-delay`, guarded at backend:212:
  ```
  _validate_slow_delay('nan')   -> SystemExit(2)  "must be a finite number >= 0"
  _validate_slow_delay('inf')   -> SystemExit(2)
  _validate_slow_delay('-inf')  -> SystemExit(2)
  _validate_slow_delay('1e400') -> SystemExit(2)   (parses to inf)
  _validate_slow_delay('-1')    -> SystemExit(2)
  _validate_slow_delay('abc')/('') -> ArgumentTypeError
  _validate_slow_delay('-0.0')/('0')/('0.5') -> accepted
  ```
  On the CLI, `--slow-delay -inf` is refused by argparse ("expected one argument"), rc=2 — still
  fail-closed, different arm.
- `Connection: close` off a real socket, header read:
  ```
  credential-400 (header)   HTTP/1.1 400 Bad Request        Connection: close = True
  bad-json-400              HTTP/1.1 400 Bad Request        Connection: close = True
  gate-400 dupCL            HTTP/1.1 400 Bad Request        Connection: close = True
  gate-411 TE               HTTP/1.1 411 Length Required    Connection: close = True
  gate-417 Expect           HTTP/1.1 417 Expectation Failed Connection: close = True
  401 no auth               HTTP/1.1 401 Unauthorized       Connection: close = True
  404 route                 HTTP/1.1 404 Not Found          Connection: close = True
  model_not_found           HTTP/1.1 404 Not Found          Connection: close = True
  ```
- Live normal-traffic control AFTER 54 redactions in the same record dir:
  ```
  GET  /v1/models            -> HTTP/1.1 200 OK; record keys = [authorization_fingerprint, body, headers,
                                method, path, received_at, remote_addr, seq, t_mono_ns]; path='/v1/models';
                                body=None; auth_fp set
  POST /v1/chat/completions  -> HTTP/1.1 200 OK; path='/v1/chat/completions';
                                body={"messages":[{"content":"hi","role":"user"}],"model":"s0-01-pong"}
                                response: {"choices":[{"finish_reason":"stop","index":0,"message":
                                {"content":"pong","role":"assistant"}}],"created":1788566400,
                                "id":"chatcmpl-s0-01","model":"s0-01-pong",...}
  new records: 2 (expected 2); marker records still served: 54
  streaming leg: HTTP/1.1 200 OK, 6 "data: " chunks, "data: [DONE]" present
  ```
- Cost table, six ops, measured with `http.client` (proper Content-Length parsing):

  | payload | ordinary path | fail-closed (`%25252541...`) path |
  |---|---|---|
  | body 1 KB | 0.001 s | 0.002 s |
  | body 10 KB | 0.003 s | 0.011 s |
  | body 100 KB | 0.020 s | 0.075 s |
  | **body 1000 KB** | **0.197 s** | **0.655 s** |
  | header 1/10/60 KB | 0.001/0.003/0.014 s | 0.001/0.004/0.014 s |

  Header values at or above ~64 KB get `431 Line too long` from `http.server` before the screen.
  **No cell > 1 s** — not a threshold failure; but the fail-closed path is 3.3x the ordinary one, and the
  lane's table (0.07 s at 1000 KB) measured neither it nor, apparently, the same thing.
- Interpreter sweep: the depth family run with the SERVER under `/usr/bin/python3.11` (3.11.15),
  `/usr/bin/python3.12` (3.12.3) and `/usr/bin/python3.13` (3.13.12) — **identical on all three**:
  depth 32 -> 200 + 1 record; depth 33 -> 400, 0 records, `Connection: close`; depth 1000 -> 400,
  0 records; depth 100,000 -> 400, 0 records. **The CI 3.12 pytest leg is NOT run here** — pytest is
  installed only for 3.11 in this sandbox (3.12/3.13 report `NO pytest`); I substituted the
  server-interpreter sweep.
- `/tmp/...` literals in the three scope files: none (grep rc=1). `tmp_path` hygiene: copy clean
  before/after every run.
- File:line refs re-derived on my copy: backend `47`, `115`, `120-128`, `129`, `132`, `141/143`, `212`,
  `239`, `299`, `334`, `443`; red `92`, `95-98`, `102`, `107`, `112`, `116`, `127`, `410`, `458-459`,
  `593`, `611`, `629`; main `1954`, `1976`, `2000`.

## Extra grade item — mutant-leftover check on the SHIPPED (committed) files

The lane disclosed a timed-out background mutant run that contaminated its saved copies. Verified on the
**committed blobs** (`git show 96f5c9a:<path>`), not on my working copy:

```
A. generic markers (# MUT / MUTANT / MUTATED / mutant_ / _MUT_):  ZERO hits
B. per-mutant shape checks (17/17 OK)
   V1/SAT       OK: _carries_secret returns 'not saturated'
   V3/MC5       OK: both returns are (frozenset(seen), bool)
   MC1/MC2      OK: depth bound = 5
   V13-16/UTF8  OK: all 6 ops present (impl)
   O2-O6/O_UTF8 OK: all 6 ops present (oracle)
   V17/hdrval   OK: header name AND value screened
   V18          OK: raw body screened
   V19          OK: path screened
   MC9          OK: JSON walk descends lists
   V12          OK: _error sends Connection: close
   MG4          OK: depth scan tracks strings   <- the disclosed contaminant, ABSENT
   MG5          OK: depth scan tracks escapes
   F12          OK: _json_safe copy-on-write root
   DEPTHGATE    OK: depth gate live
   O1           OK: oracle not 'return True'
   O7           OK: oracle depth 6
   O_JSONBLIND  OK: oracle JSON seeding present
C. committed blobs byte-identical to my scratch copy (3/3 `diff -q` clean)
D. py_compile OK on all three
E. no xfail / skipif / pytest.skip smuggled into the scope test files
F. full parent->PIN diff of all three files read line by line: only intended changes, no stray edits
G. no-op control: 460 passed (three files) / 119 passed (red standalone)
```

**Explicit verdict on this item: the three shipped files carry NO mutant leftover — V1 and MG4 in
particular are absent, and the no-op control is green.** The lane's recovery (re-read HEAD blobs, re-apply
edits) produced a clean tree.

## Mutant table — my set: 33 mutants + 1 no-op control. 29 KILLED / 4 SURVIVED (3 non-equivalent, 1 equivalent)

Restore from a pristine copy of the three files, never git; `git status --porcelain` asserted CLEAN after
every mutant (33/33 CLEAN). Selection = red file (119) + 5 named main-file tests = **355 tests**; both
implementation survivors re-run against the **full 460**.

| id | mutation | verdict | killer (named) |
|---|---|---|---|
| NOOP | none | SURVIVED (intended) | 460 passed / 119 standalone — harness sound |
| M_SAT_IGNORE | `_carries_secret` -> `return False` | KILLED | `R::test_credential_depth5_percent_nesting_returns_400[header-d6_space]` |
| M_SAT_INV | `not saturated` -> `saturated` | KILLED | `R::test_post_content_length_exactly_max_is_accepted` |
| M_SEEN (V3) | `_normal_forms` returns last frontier | KILLED | `R::test_credential_plus_split_with_pct2520_suffix_returns_400` |
| M_D4 (MC1) | depth 5->4 | KILLED | `B::test_saturating_junk_is_served` |
| M_D6 (MC2) | depth 5->6 | KILLED | `B::test_bound_exceeded_blanks_the_record` |
| M_SENTINEL | decision back to a sentinel ELEMENT (no bool) | KILLED | `R::test_credential_depth5_percent_nesting_returns_400[header-d6_space]` |
| M_UTF8_DEL | drop `utf8_redecode` (impl) | KILLED | `R::test_credential_raw_utf8_zero_width_in_header_returns_400[ZWSP]` |
| M_LOWER_DEL (V13) | drop `str.lower` | KILLED | `R::test_credential_uppercased_token_in_header_returns_400` |
| M_ZWC_DEL (V14) | drop `strip_zwc` | KILLED | `R::test_credential_zero_width_pct_encoded_returns_400[ZWSP]` |
| M_WS_DEL (V15) | drop `strip_ws` | KILLED | `R::test_credential_whitespace_split_in_valid_json_body_returns_400[TAB]` |
| M_UQP_DEL (V16) | drop `unquote_plus` | KILLED | `R::test_credential_encoded_whitespace_split_returns_400[header-PLUS]` |
| **M_UQ_DEL** | **drop `unquote` (impl)** | **SURVIVED — 460 passed** | **none — NON-EQUIVALENT (F4)** |
| M_HDRNAME (V17) | header NAME not screened | KILLED | `R::test_credential_depth5_percent_nesting_returns_400[header_name-d5_space]` |
| M_HDRVAL | header VALUE not screened | KILLED | `R::test_authorization_prefixed_header_name_is_not_exempt[Authorization-X]` |
| M_RAWBODY (V18) | raw body not screened | KILLED | `R::test_duplicate_json_key_hiding_token_returns_400` |
| M_PATH (V19) | path not screened | KILLED | `R::test_credential_encoded_whitespace_split_returns_400[query-%20]` |
| M_JSONSTRINGS | parsed-JSON-string walk disabled | KILLED | `R::test_credential_whitespace_split_in_valid_json_body_returns_400[TAB]` |
| M_MC9_LISTS | JSON walk skips lists | KILLED | `R::test_credential_whitespace_split_in_json_list_element_returns_400[TAB]` |
| M_MC5_NOTUPLE | `return frozenset(seen)` (no tuple) | KILLED | `R::test_credential_whitespace_split_in_valid_json_body_returns_400[TAB]` (TypeError) |
| M_V12_CLOSE | `_error` drops `Connection: close` | KILLED | `B::test_framing_domain_table[no_cl/GET/v1/models/nocred]` |
| M_MG4_STR | depth scan ignores strings | KILLED | `R::test_json_depth_ignores_brackets_inside_strings` |
| M_MG5_ESC | depth scan ignores escapes | KILLED | `R::test_json_depth_handles_escaped_quote` |
| **M_JSONSAFE_INPLACE** | **revert `_json_safe` to in-place mutation** | **SURVIVED — 460 passed** | **none — NON-EQUIVALENT (F2)** |
| M_DEPTHGATE_OFF | `> MAX_JSON_DEPTH` -> `> 10**9` | KILLED | `R::test_json_depth_over_limit_returns_400_no_record` |
| O1 | oracle -> `return True` | KILLED | 8 self-tests **+ `R::test_record_text_carries_no_token_under_any_normalization` (backend test)** |
| O2_UQ | oracle drops `unquote` | SURVIVED | EQUIVALENT for this token (0/22,073 differences) |
| O3_UQP | oracle drops `unquote_plus` | KILLED | `R::TestOracleSelfTests::test_oracle_known_vectors[plus_split]`, `[pct2b_split]` |
| O4_WS | oracle drops `strip_ws` | KILLED | 6 self-tests + `R::test_record_text_carries_no_token_under_any_normalization` |
| O5_LOWER | oracle drops `str.lower` | KILLED | `[uppercased]` |
| O6_ZWC | oracle drops `strip_zwc` | KILLED | `[zwsp_split]` |
| O7_DEPTH1 | oracle depth 6->1 | KILLED | `[junk_suffix] [depth5_nesting] [plus_split] [pct2b_split]` |
| **O_UTF8** | **oracle drops `utf8_redecode`** | **SURVIVED — 119 passed** | **none — NON-EQUIVALENT (F3)** |
| O_JSONBLIND | oracle JSON seeding removed | KILLED | `[json_escaped_tab]` |

`R` = `tests/red/test_s0_01_backend_credential_screen.py`; `B` = `tests/test_s0_01_scripted_backend.py`.

## Findings — all of them, no severity floor

### R10-D5g-F1 — BLOCKING — SOLID — `utf8_redecode` fails OPEN; one junk byte defeats the whole raw-UTF-8 arm
- **file:line** `proofs/S0-01/tools/scripted_backend.py:120-128` (op) and `:129` (op set); mirrored in
  `tests/red/test_s0_01_backend_credential_screen.py:102-107`.
- **proof (reproduced live, subprocess backend, real record sink, on 3.11/3.12/3.13):**
  `X-Trace: <tok[:18]> + e2 80 80 + <tok[18:]>` -> `400 Bad Request`, record blanked.
  `X-Trace: <tok[:18]> + e2 80 80 80 + <tok[18:]>` -> **`200 OK`, record written verbatim**, and
  `value.encode("latin-1",errors="replace").decode("utf-8",errors="ignore")` + `re.sub(r"\s+","")`
  returns the full token. Same for `c2 a0 80`, `c0 a0`, `80`, and — through an ordinary, well-formed
  UTF-8 JSON body using the JSON escapes ``, `À `, `â`.
- **observed vs expected:** observed 200 + verbatim record with a recoverable token; expected 400 +
  `{"credential_in_unexpected_location": true}` — the outcome the identical separator gets without the
  junk byte. The separator in the `e2 80 80 80` case is U+2000 EN QUAD, **genuine Unicode whitespace the
  closure exists to strip**; only the strict decode's failure hides it. This is the exact defect class
  round 9 raised (D5f-F2) and round 10 claims closed, still open through a one-byte edit.
- **minimal fix:** make the op a one-to-many expansion instead of identity-on-error —
  ```python
  def utf8_redecode(x):
      try:
          return x.encode("latin-1").decode("utf-8")
      except (UnicodeEncodeError, UnicodeDecodeError):
          return x
  def utf8_redecode_lenient(x):        # NEW op, added to `ops` AND to the oracle
      try:
          return x.encode("latin-1").decode("utf-8", errors="ignore")
      except UnicodeEncodeError:
          return x
  ```
  — or fail closed: if the latin-1 re-encode holds any byte >= 0x80 that is not part of a valid UTF-8
  sequence, return `True` from `_carries_secret`. Mirror in the oracle or the oracle stops being wider.
- **exact red test to add** (currently red — returns 200):
  ```python
  @pytest.mark.parametrize("sep", [b"\xe2\x80\x80\x80", b"\xc2\xa0\x80", b"\xc0\xa0", b"\x80"],
                           ids=["enquad_plus_junk", "nbsp_plus_junk", "overlong_space", "lone_continuation"])
  def test_credential_invalid_utf8_separator_in_header_returns_400(backend, sep):
      port = backend["port"]; mid = len(TOKEN)//2; body = b'{"model":"s0-01-pong","messages":[]}'
      payload = (f"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\nAuthorization: Bearer {TOKEN}\r\n"
                 f"Content-Type: application/json\r\nX-Trace: ").encode() + TOKEN[:mid].encode() + sep \
                + TOKEN[mid:].encode() + f"\r\nContent-Length: {len(body)}\r\n\r\n".encode() + body
      resp = _raw(port, payload)
      assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
      assert json.loads(_records(backend)[-1].read_text())["body"] == MARKER
  ```
  plus the JSON-body twin using `"\\u0080"` as the separator.

### R10-D5g-F2 — BLOCKING — SOLID — `test_json_safe_does_not_mutate_request_body` is a tautology; the F12 fix is unpinned
- **file:line** `tests/test_s0_01_scripted_backend.py:2000-2016`.
- **proof:** mutant `M_JSONSAFE_INPLACE` (the parent's in-place `_json_safe`: `root = o` at backend:299 and
  the two `elif isinstance(v,(dict,list)): stack.append(v)` branches) -> **`460 passed in 143.96s`**. The
  red-green run against the parent implementation also passes this test. Its only assertions are the
  status, the record count and `rec["body"]["x"] == "<non-finite>"` — identical under both
  implementations, because the backend discards `body` right after recording. It duplicates
  `R::test_non_finite_float_body_coerced_and_recorded`.
- **observed vs expected:** the docstring claims "`_json_safe` returns a new structure, never mutates the
  caller's body"; nothing in the test can observe mutation.
- **minimal fix:** test the function, not the round trip. `_json_safe` is a closure inside `State.record`
  (backend:293-321), so lift it to module scope and assert directly:
  ```python
  def test_json_safe_does_not_mutate_caller_object():
      body = {"a": [{"x": float("nan")}]}
      before = copy.deepcopy(body)
      out = sb._json_safe(body)
      assert body == before
      assert out is not body
      assert out["a"][0]["x"] == "<non-finite>"
  ```
  If lifting is not wanted, an end-to-end substitute: record the SAME parsed body object twice and assert
  the second record still coerces (an in-place implementation would leave `"<non-finite>"` already in
  place, so also assert the object handed in is unchanged via a second, NaN-preserving path).

### R10-D5g-F3 — BLOCKING (oracle contract) — SOLID — the oracle's new `utf8_redecode` has no self-test; O_UTF8 survives
- **file:line** `tests/red/test_s0_01_backend_credential_screen.py:102-107` (op added this round),
  `:396-411` (the vector table it is missing from).
- **proof:** `[O_UTF8] SUMMARY: 119 passed in 40.56s` — no test fails. Non-equivalence proven by direct
  call: on `'s0-01-upstream-tok' + b"\xe2\x80\x8b".decode("latin-1") + 'en-0123456789abcdef'` the oracle
  with the op returns `absent=False`, without it `absent=True`; likewise inside a record-shaped JSON string.
- **observed vs expected:** the D5f ruling required "the oracle must stay at least as wide as the
  implementation" and "drop each normalization op one at a time — every mutant killed by a NAMED
  self-test". Five of six ops have such a vector; the sixth, added this round, does not.
- **minimal fix / exact red test:** add to `test_oracle_known_vectors`
  ```python
  (TOKEN[:len(TOKEN)//2] + b"\xe2\x80\x8b".decode("latin-1") + TOKEN[len(TOKEN)//2:], False),
  ```
  with id `raw_utf8_mojibake` (passes today; red under O_UTF8).

### R10-D5g-F4 — NON-BLOCKING — SOLID — `unquote`'s membership in the impl op set is unpinned (M_UQ_DEL survives)
- **file:line** `proofs/S0-01/tools/scripted_backend.py:129`.
- **proof:** `[M_UQ_DEL-FULL] SUMMARY: 460 passed in 143.67s`. Non-equivalent: a 22,073-vector differential
  found 29 observable divergences, all where the real screen fails closed and the mutant serves, e.g.
  `X-Trace: %252520%252B` — live on the real backend `400 Bad Request` + blanked record; the mutant's
  closure saturates and would serve 200. Also `%252B%252520`, `%252520a+`, `+%2541%2520`.
- **observed vs expected:** every other op in the set is pinned by a named test; `unquote` is not. Security
  impact is nil in the direction found (the mutant is only looser on token-free junk), but the op set is a
  security-relevant constant with an unguarded member.
- **exact red test to add:**
  ```python
  def test_unquote_op_is_required_for_the_bound(backend):
      """%252520%252B fails to saturate at depth 5 only because `unquote` is in the op set."""
      resp = _raw(backend["port"], _post(backend["port"], b'{"model":"s0-01-pong","messages":[]}',
                                         extra_headers="X-Trace: %252520%252B\r\n"))
      assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
      assert json.loads(_records(backend)[-1].read_text())["body"] == MARKER
  ```

### R10-D5g-F5 — NON-BLOCKING — SOLID — the report's stated MECHANISM for the header-NAME raw-UTF-8 sink is false
- **file:line** `tasks/briefs/s0-01-d5g-support/D5g-report.md`, after "Raw UTF-8 separators (raw body sink,
  all 6)": "No additional test needed for header-name or raw-body sinks: the backend screens them through
  the same `_carries_secret` path and all are caught by `utf8_redecode`."
- **proof:** raw non-ASCII bytes in a header NAME produce `400 Bad Request` with **zero records**; the
  `email` parser reports `[MissingHeaderBodySeparatorDefect()]` for that line, so `_framing_gate` arm 1
  (backend:359-361) rejects **before** `state.record` is ever called. `_carries_secret` never runs and
  `utf8_redecode` never sees those bytes. (The raw-body sink IS screened, but via `strip_zwc` on the
  json-decoded string, not via `utf8_redecode`.)
- **observed vs expected:** the "no test needed" decision rests on a mechanism that does not exist. The
  outcome (400, no record) is still fail-closed, so this is an accuracy defect, not a leak — but the
  raw-UTF-8 header-NAME sink has **no regression test** and would change silently if `http.server`'s
  defect handling changed.
- **minimal fix:** state the real mechanism in the report, and add
  `test_raw_non_ascii_header_name_rejected_by_gate_no_record` asserting `400`, `Connection: close`, and a
  record-count delta of **0**.

### R10-D5g-F6 — NON-BLOCKING — SOLID — stale comment falsified by this same commit
- **file:line** `proofs/S0-01/tools/scripted_backend.py:443`: "...on every interpreter; **the RecursionError
  arm below stays as defence**." The arm (parent lines 434-438, re-derived from `5f3fe0b`) was deleted by
  this commit (D5g-report F9).
- **proof:** `grep -n RecursionError proofs/S0-01/tools/scripted_backend.py` -> only `:89` and `:443`, both
  comments; no `except RecursionError` remains.
- **minimal fix:** end the comment at "on every interpreter." (or "...; the RecursionError arm was removed
  as unreachable — D5f-F9").

### R10-D5g-F7 — NON-BLOCKING — SOLID — the oracle docstring lists five ops; the code has six
- **file:line** `tests/red/test_s0_01_backend_credential_screen.py:95-97`: "Enumerates every word over
  {unquote, unquote_plus, strip_ws, lower, strip_zwc} up to depth 6 (the backend uses depth 5 with the
  same operators...)". `utf8_redecode` (defined `:102`, in `ops` at `:107`) and the F4 JSON-literal seeding
  (`:110-114`) are both absent from the prose.
- **minimal fix:** add `utf8_redecode` to the set and one clause for the JSON seeding.

### R10-D5g-F8 — NON-BLOCKING — SOLID — the report's PIN sha does not exist
- **file:line** `D5g-report.md` line 3: "PIN: `4abec5011f46500aa5daac681ea69473a42f2b56` = HEAD (verified)".
- **proof:** `git cat-file -t 4abec50...` -> `fatal: git cat-file: could not get object info`. The object is
  not in `/home/user/agent-factory`. The shipped bytes are nonetheless correct (sha256 and line counts
  match the PIN blobs exactly), so this is a provenance-record defect, not a content defect.
- **minimal fix:** record the sha the coordinator actually committed (`96f5c9a`), or the pre-commit
  worktree sha with that fact stated.

### R10-D5g-F9 — NON-BLOCKING — SOLID — the F10 "every file:line re-derived" claim is vacuous
- **file:line** `D5g-report.md`, Done table row F10: "all file:line in this report re-derived at the final
  tree".
- **proof:** the report contains exactly one line reference — "deleted lines 434-438" — and those are the
  **parent's** line numbers, not the final tree's (the final tree has no such arm). D5f-F10 asked for the
  opposite: file:line refs, re-derived at the final tree.
- **minimal fix:** cite `file:line` for each Done row against the final tree (I have re-derived them in
  R10-D above; every claim is correct as a symbol reference).

### R10-D5g-F10 — NON-BLOCKING — SOLID — 12 of 18 new tests were never red; the report's red/green column overstates
- **file:line** `D5g-report.md` "Done" table, "red before / green after" column.
- **proof:** parent-impl + HEAD-tests run: `6 failed, 29 passed` — only the raw-UTF-8 family was red. The
  report is honest for V3/O1/MC1/MC2 (it names mutants, not a parent-red), but the F8 header_name row
  offers "400+REDACTED on all 4 vectors" as evidence when those four cases were already green at the
  parent, and the F12 row lists a test with no obtainable red state at all (see F2).
- **minimal fix:** label control tests as controls with the mutant each kills, and mark F12 **not proven**
  rather than Done.

### R10-D5g-F11 — NON-BLOCKING — SOLID — the accepted risk is not documented where the decision is made
- **file:line** documented at `scripted_backend.py:47` (module docstring) and `:115` (`_normal_forms`
  docstring); **absent** from `_carries_secret`'s docstring (`:226-234`) and from the line that turns the
  flag into a blanked record (`:239  return not saturated`).
- **proof:** live directionality confirmed (`%25252540` -> 200 served; `%25252541` -> 400 blanked), so the
  documented example is now correct; it is filed one level above the decision it explains.
- **minimal fix:** one clause on `_carries_secret`: "...returns True; the false-positive cost of this arm is
  the D5d-F12 accepted risk (see `_normal_forms`)."

### R10-D5g-F12 — NON-BLOCKING — SOLID — the report's cost table is not reproducible and omits the fail-closed path
- **file:line** `D5g-report.md` "Cost table (6 ops)": 1000 KB -> 0.07 s.
- **proof:** `http.client` measurement gives **0.197 s** ordinary and **0.655 s** on the fail-closed
  (`%25252541...`) path at 1000 KB, on 4 contended cores. Neither is 0.07 s; the fail-closed path is the
  expensive one and is untabulated. Still under the brief's 1 s threshold — **not a threshold failure**.
- **minimal fix:** publish both columns plus the machine/contention context.

### R10-D5g-F13 — NON-BLOCKING — SOLID — control characters (0x7F, C0/C1) split the token and are served verbatim
- **file:line** `proofs/S0-01/tools/scripted_backend.py:129` (op set has no control-character strip);
  module docstring `:41-52` does not list this as an accepted risk.
- **proof:** `X-Trace: <tok[:18]> + 7f + <tok[18:]>` -> `200 OK`, record verbatim
  (`'s0-01-upstream-tok\x7fen-0123456789abcdef'`); same through a JSON body. The six-op closure cannot
  recover it and the oracle agrees it is absent, so it is out of the *stated* contract — but it is the same
  "invisible separator inside a recorded credential" family the contract does cover for ZWSP.
- **minimal fix:** either add `strip_ctl` (`re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", x)`) to
  both the closure and the oracle, or name control characters explicitly in the accepted-risk paragraph.

### R10-D5g-F14 — INFORMATIONAL — SOLID — `--slow-delay -inf` is refused by argparse, not by the isfinite guard
- **file:line** `proofs/S0-01/tools/scripted_backend.py:212` (guard), `:530` (`add_argument`).
- **proof:** CLI `--slow-delay -inf` -> rc 2 `error: argument --slow-delay: expected one argument` (argparse
  treats `-inf` as an option); the guard rejects it correctly when called directly
  (`_validate_slow_delay('-inf') -> SystemExit(2)`). `-1` does reach the guard. Fail-closed either way.
- **minimal fix:** none required; note it if the exact refusal string is ever asserted.

### R10-D5g-F15 — INFORMATIONAL — SOLID — the O2 equivalence claim is token-dependent
- **file:line** `D5g-report.md` mutant table, row O2 ("EQUIVALENT — `unquote_plus` subsumes `unquote`").
- **proof:** true only because the fixture token contains no `+` and no whitespace (0/22,073 differences in
  my differential). A token containing `+` would make `unquote` strictly necessary in the oracle. The claim
  as written reads as unconditional.
- **minimal fix:** append "for a token containing no `+`" to the equivalence claim.

## What I reproduced vs reviewed statically vs deliberately skipped

- **Reproduced, first-hand:** both gate runs and the red standalone; pyflakes; the baseline-442 count; the
  red state on the PIN's parent; **all 33 mutants + a no-op control**, each with pristine-copy restore and
  a post-run `git status` clean assertion, both implementation survivors escalated to the full 460; the
  35-cell sink x separator matrix; the 33-cell raw-byte matrix; the decisive `e2 80 80` vs `e2 80 80 80`
  pair on three interpreters; the record dumps and lenient-decode recovery; the JSON-body leak twin; D5f
  Table 2 re-run; the JSON-blindness self-tests; `Connection: close` off a real socket for 8 response
  classes; the live normal-traffic and streaming controls after 54 redactions; the live accepted-risk
  directionality table; the `--slow-delay` negative control; the depth family on 3.11 / 3.12 / 3.13; both
  cost tables; the mutant-leftover sweep on the committed blobs; every `file:line`.
- **Reviewed statically only:** the full parent->PIN diff of all three files (read line by line, no stray
  edits found); the D5f verdict text and the D5g brief text.
- **Deliberately skipped, with reason:** the **CI 3.12 pytest leg** — pytest is installed only for 3.11 in
  this sandbox (`python3.12`/`python3.13` report `NO pytest`); I substituted a server-interpreter sweep,
  which covers the interpreter-dependence claim but not pytest-level collection on 3.12. The **PC/bridge
  venue** — no bridge banner this session. The **rest of the repo suite** — other lanes hold the tree; I ran
  exactly the three files the brief names. **D5f's 50,000-vector `unquote` differential** — replaced by my
  own 22,073-vector directed differential, which found the 29 divergences D5f's did not.

## Summary lines (both, pasted)

```
pytest-summary: 460 passed in 143.56s (0:02:23)     pytest-exit: 0
pytest-summary: 460 passed in 143.21s (0:02:23)     pytest-exit: 0
pytest-summary: 119 passed in 40.49s                pytest-exit: 0   (red standalone)
pyflakes rc: 0
```

## VERDICT

**NOT-READY** — blocking: **R10-D5g-F1**, **R10-D5g-F2**, **R10-D5g-F3**.

- **F1**: the raw-UTF-8 arm this round exists to add fails open on invalid UTF-8; one appended junk byte
  restores the exact leak D5f-F2 raised — 200 OK, verbatim record, token recoverable by a one-line lenient
  decode; reproduced live on 3.11/3.12/3.13 and through an ordinary well-formed JSON body.
- **F2**: `test_json_safe_does_not_mutate_request_body` is a tautology; `M_JSONSAFE_INPLACE` survives all
  460 tests, so the F12 fix ships unproven.
- **F3**: the oracle's newly added sixth op has no self-test; `O_UTF8` survives the whole red file and is
  provably non-equivalent, so the oracle is not "at least as wide" in the sense the D5f ruling required.

Everything else the round set out to do is real and reproduced: the six named raw-UTF-8 separators are
genuinely closed (red on the parent, green at HEAD), `seen` is kept and proven, the depth bound is pinned
from both sides by two tests that die to MC1 and MC2 respectively, the accepted-risk example is corrected
and matches live behaviour, the header-NAME sink is covered at 24 cases, the oracle's JSON blindness is
fixed, ruling 2(b) holds (O1 now kills a backend test), the `RecursionError` arm is gone, and the shipped
files carry **no mutant leftover** from the timed-out background run.

This verdict does not depend on anything I failed to reproduce.
