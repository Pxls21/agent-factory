# Lane D5l report -- S0-01 scripted backend round 15

PROPOSAL only: this is PC Hermes build-lane output. It is not a gate verdict until the sandbox-side adversarial verifier grades it.

PIN: `13c1bd2`; landing = the coordinator's checkpoint, made after this report.
Lane worktree HEAD while editing: `58741bb23b28ecd574b4f8472cd88dba658ceaad`.
Actual local ref checked during the run: detached HEAD at `58741bb23b28ecd574b4f8472cd88dba658ceaad`; origin/claude/soundbox-kit-migration-iz1jwf at `545a9ff87124a5345f51c9aee2c0e98697bc7dc4`.

Scope: `proofs/S0-01/tools/scripted_backend.py`, `tests/test_s0_01_scripted_backend.py`, `tests/red/test_s0_01_backend_credential_screen.py`, `tasks/briefs/s0-01-d5j-support/cost_probe.py`, plus this report.

## FILE IDENTITY (FINAL bytes, four files)

| file | sha256 | lines | bytes |
|---|---|---:|---:|
| `proofs/S0-01/tools/scripted_backend.py` | `04da144a507e0887c49a7d82c392f0464ac80e19688a1e7142d355e174189a4b` | 819 | 41010 |
| `tests/test_s0_01_scripted_backend.py` | `cd51ed6520391955e6395174d6f2ec0e2986dad06d27e65e8c2933087f41ef8c` | 2177 | 95972 |
| `tests/red/test_s0_01_backend_credential_screen.py` | `40455da91d8a84d985b5797eb540dde4168013d54f1b2c11a8cf39600b91b7d0` | 1234 | 59655 |
| `tasks/briefs/s0-01-d5j-support/cost_probe.py` | `a1b8600830af5f48efeab994ee45279441562e064399d110861f5f37405b3ef5` | 128 | 4478 |

## DONE table

| item | file:line on FINAL bytes | red-before line | green line |
|---|---|---|---|
| 1. Structural `MARKER` NotEq ban | `def test_no_not_equal_marker_assertions` covers scratch BREAK/EVADE/POSITIVE controls and both real-file zero checks at red:1184-1216. | MARKER-GUARD-BREAK and MARKER-GUARD-EVADE are killed by `test_no_not_equal_marker_assertions`; BREAK log: `1 failed in 0.42s`; EVADE+BODYSTR log: `1 failed, 4 passed in 0.59s`. | `test_no_not_equal_marker_assertions` is included in the two-file gate: `539 passed in 176.44s` and `539 passed in 176.48s`. |
| 2. Every served/verbatim path pins the positive record value | Existing `test_saturating_junk_is_served` pins header value with `assert rec["headers"]["x-trace"] == "%252B"` at main:2041. D5l `test_pct_dense_junk_that_now_saturates_is_served` pins `x-trace` with `assert json.loads(recs[-1].read_text())["headers"]["x-trace"] == vec` at red:1233. | RECORD-HDRVAL-BLANKED previously passed; now log shows `2 failed in 11.25s`. | Two-file archive gates both passed: `539 passed in 176.44s` and `539 passed in 176.48s`. |
| 3. One extras literal linked to impl and oracle | `assert sb._INVISIBLE_EXTRA == extra` at main:2100 and `{ord(c) for c in red._INVISIBLE_EXTRA} == sb._INVISIBLE_EXTRA` at main:2172. | IMPL-EXTRA-DRIFT log: `2 failed in 0.81s`; ORACLE-EXTRA-DRIFT log: `1 failed in 0.77s`. | Impl/oracle probe says `impl - oracle = 0` and `oracle_pinned == impl: True`. |
| 4. Token FIFO and dangling record-dir symlink refuse at startup | Backend takes `st = args.token_file.stat()` at backend:778; non-regular token path emits `token file is not a regular file` at backend:780. Dangling record-dir symlink guard and stderr `scripted_backend: --record-dir {args.record_dir} is a dangling symlink` live at backend:791-792. Tests are `def test_token_file_fifo_refuses_startup_without_reading` at main:330 and `def test_dangling_record_dir_symlink_refuses_startup` at main:345. | Parent-copy red-before: FIFO `TimeoutExpired ... timed out after 10 seconds`; dangling symlink `TimeoutExpired ... timed out after 10 seconds`; summary `2 failed in 20.95s`. | Targeted tests in the self-sweep selection: `12 passed in 11.00s`; full two-file gates: `539 passed` twice. |
| 5. Cost prose states the measured mechanism honestly | Backend docstring says `MAX_CONTENT_LENGTH` cost is measured in both harnesses and that earlier higher D5i timings are load, not harness overhead at backend:77-82. | Old report claim said the raw-socket probe skipped http.client overhead. | Cost probe re-run below and head-to-head dual probe: `http.client=0.731s (200) raw-socket=0.717s (200) raw/http=0.98x`. |
| 6. Dead helper deleted | `_last_record_text` is absent from the final red test file; self-sweep C3 reports zero stale `[-1]` over produced records and pyflakes is clean. | Dead helper had zero callers and hid the stale-tail audit. | Self-sweep line: `C3 stale [-1] over produced records | 0`; pyflakes rc 0. |
| 7. Registry screen at zero | AP screen command over both test files returned `--- TEST_SCREEN over 2 path(s): 0 hits over 2 files ---`. | PIN screen had AF-AP-60/AF-AP-61 hits in the old grep-based marker guard. | AP screen rc 0; no AF-AP-60, AF-AP-61, or other hit remained. |
| 8. Report discipline | This report uses worktree refs for changed files and was linted without `--rev`, per the brief carve-out for changed files. | D5k had seven wrong file:line refs. | Report lint summary after this file was written is in the Gate evidence section; MISS is 0 and NEAR is 0. |
| 9. 18-class self-sweep | Self-sweep script scanned both test files by AST/regex and exercised selected planted controls plus the full two-file pytest gates. Representative source samples and verdicts are tabled below. | AP screen plus pyflakes plus selected class run caught AP-66 during this lane; fixed by replacing direct module reassignment with `monkeypatch`. | Final self-sweep rc 0; `12 passed in 11.00s`; AP screen rc 0; pyflakes rc 0. |

## Served/200/verbatim record-audit list

| test | positive record assertion |
|---|---|
| `test_post_content_length_exactly_max_is_accepted` | `json.loads(recs[-1].read_text())["body"] == json.loads(core)` at red:295 |
| `test_json_depth_at_limit_is_served` | `json.loads(recs[-1].read_text())["body"] == json.loads(_nested_note_body(MAX_JSON_DEPTH))` at red:445 |
| `test_json_depth_ignores_brackets_inside_strings` | `json.loads(recs[-1].read_text())["body"] == json.loads(body)` at red:668 |
| `test_json_depth_handles_escaped_quote` | `json.loads(recs[-1].read_text())["body"] == json.loads(body)` at red:680 |
| `test_ordinary_latin1_text_in_json_body_is_served` | `json.loads(recs[-1].read_text())["body"]["messages"][0]["content"] == content` at red:943 |
| `test_non_finite_float_body_coerced_and_recorded` | `rec["body"]["x"] == "<non-finite>"` and `rec["body"]["y"] == "<non-finite>"` at red:479 and red:480 |
| `test_saturating_junk_is_served` | `rec["headers"]["x-trace"] == "%252B"` at main:2041 |
| `test_pct_dense_junk_that_now_saturates_is_served` | `json.loads(recs[-1].read_text())["headers"]["x-trace"] == vec` at red:1233 |
| Credential-shaped 400 record pins retained | `json.loads(recs[-1].read_text())["body"] == MARKER` at red:1140, red:1157, and red:1179 |

## MUTANT table (scratchpad copies; `ran` = tests executed)

| mutant | ran | failed | killer / qualification |
|---|---:|---:|---|
| MARKER-GUARD-BREAK | 1 | 1 | `test_no_not_equal_marker_assertions` detects a direct `json.loads(x)["body"] != MARKER` assert. |
| MARKER-GUARD-EVADE + BODYSTR-RECORD-BLANKED | 5 | 1 | `test_no_not_equal_marker_assertions` detects `_b = ...["body"]` followed by `_b != MARKER`; the old five-test hollow green is red. |
| RECORD-HDRVAL-BLANKED | 2 | 2 | `test_saturating_junk_is_served` and `test_pct_dense_junk_that_now_saturates_is_served`. |
| IMPL-EXTRA-DRIFT | 2 | 2 | `test_invisible_table_is_the_ucd_15_1_class` and `test_oracle_table_equals_the_impl_table`. |
| TOKEN-FIFO-UNGUARDED | 1 | 1 | `test_token_file_fifo_refuses_startup_without_reading`; failure is `TimeoutExpired ... timed out after 10 seconds`. |
| RECDIR-SYMLINK-UNGUARDED | 1 | 1 | `test_dangling_record_dir_symlink_refuses_startup`; failure is `TimeoutExpired ... timed out after 10 seconds`. |
| BODYSTR-RECORD-BLANKED | 4 | 4 | `test_top_level_json_string_body_is_not_a_byte_view[e_acute/u_uml/pound]` and `test_top_level_json_string_hello_control`. |
| BODYSTR-RECORD-ONECHAR | 4 | 3 | `test_top_level_json_string_body_is_not_a_byte_view[e_acute/u_uml/pound]`; ASCII `hello` equivalent stays pass. |
| O-TABLE-DROP | 33 | 1 | `TestOracleSelfTests.test_oracle_known_vectors[ucd15_addition_split]`. |
| ORACLE-DRIFT | 1 | 1 | `test_oracle_table_equals_the_impl_table`. |
| TABLE-DROP-RESERVED | 4 | 4 | Reserved JSON-body pins plus the two extras-equality table checks. |
| UQ-REPLACE-BOTH | 200 | 5 | Four `test_credential_pct_encoded_invalid_utf8_separator_returns_400[...]` cases plus `test_pct_dense_junk_that_now_saturates_is_served`. |
| UQ-REPLACE-UNQUOTE-ONLY | 200 | 1 | `test_pct_dense_junk_that_now_saturates_is_served`; single-decoder revert is now named separately. |
| UQ-REPLACE-UNQUOTE-PLUS-ONLY | 200 | 1 | `test_pct_dense_junk_that_now_saturates_is_served`; single-decoder revert is now named separately. |
| RECORDLESS_400_APIKEY | 2 | 2 | `test_credential_headers_dropped_from_records` and `test_credential_in_credential_header_returns_400[api-key]`. |
| RECORDLESS_400_XTRACE | 12 | 12 | X-Trace credential 400 cases; all fail because no record is written. |
| TABLE-DROP-42 | 1 | 1 | `test_invisible_class_does_not_depend_on_the_runtime_unicode_table` for U+10EFD. |
| TABLE-DROP-FILLERS | 13 | 5 | `BRAILLE_BLANK`, `HANGUL_FILLER`, `HALFWIDTH_FILLER`, `CHOSEONG_FILLER`, `JUNGSEONG_FILLER`. |
| TABLE-DROP-CS | 1 | 1 | `test_credential_lone_surrogate_separator_in_json_body_returns_400`. |
| TABLE-DROP-ME | 13 | 2 | `ENCLOSING_CIRCLE` and `CYRILLIC_ENCLOSING`. |
| TABLE-DROP-ZLZP | 13 | 2 | `LINE_SEPARATOR` and `PARAGRAPH_SEPARATOR`. |
| ORACLE-EXTRA-DRIFT | 1 | 1 | D5l extras equality converts the prior qualified equivalent into a killed oracle-extra drift; impl extras remain independently pinned by IMPL-EXTRA-DRIFT. |
| CTL_PARTIAL_noC1 predicate form | 539 | 0 | EQUIVALENT survivor as in D5k: dropping C1 only in the predicate form does not change behavior for this backend's already-covered failure modes; table-subtraction forms are killed by table tests. |

## PROBE tables

### Unicode / strip-domain / live controls

```
codepoint-set-size: 72
py313: header-sink+json-escape-sink over 72 code points -> non-conforming cells: 0
py313 UCD 15.1.0: impl=4315 oracle_pinned=4315 oracle_effective=4315 impl - oracle = 0 oracle_pinned == impl: True
REDACTIONS: 60/60 requests -> 400 ; records 60 ; MARKER records on disk: 60
GET  /v1/models           -> HTTP/1.1 200 OK ; record path=/v1/models ; auth_fp set: True
POST /v1/chat/completions -> HTTP/1.1 200 OK ; record verbatim: True
STREAM s0-01-slow         -> HTTP/1.1 200 OK ; 6 'data: ' frames ; [DONE] present: True
MARKER records after the controls: 60  (normal/stream added 3 records)
Connection: close on every 4xx -- 60/60 True
```

### Cost probe, committed harness, with `/proc/loadavg` before and after

```
load before: 0.36 0.52 0.66 2/2235 1649129
load before: 0.49 0.55 0.66 2/2239 1649134
    KB |   ordinary | inv-utf8-hdr |  bound-hdr | bound-body
-----------------------------------------------------------------
     1 |    0.002 200 |    0.002  400 |    0.002 400 |    0.003 400
    10 |    0.008 200 |    0.007  400 |    0.007 400 |    0.019 400
   100 |    0.071 200 |    0.061  400 |    0.060 400 |    0.187 400
  1000 |    0.715 200 |    0.591  400 |    0.595 400 |    1.864 400
load after:  0.77 0.61 0.68 1/2220 1649631
load after:  0.77 0.61 0.68 1/2219 1649632
```

The duplicated load lines are from the wrapper and `cost_probe.py` both printing load. The committed harness run returned rc 0. A separate same-window dual harness check returned:

```
load before: 0.51 0.44 0.55 2/2221 1662992
ordinary-1000KB http.client=0.731s (200) raw-socket=0.717s (200) raw/http=0.98x
load after:  0.51 0.44 0.55 1/2221 1662996
```

### 18-class self-sweep over both test files

Every executable test instance was also covered by the full two-file gates, `539 passed` twice. The class sweep's selected planted-control run returned `12 passed in 11.00s`; AP screen rc 0; pyflakes rc 0.

| class | file:line sample | verdict | the run | fix | red test |
|---|---|---|---|---|---|
| C1 presence-gated checks | `.exists()` sample at main:928 | SAFE -- fixture-local and followed by explicit subprocess/pytest state. | `539 passed`; selected run `12 passed`. | None. | Full gate. |
| C2 reads outside walk / no S_ISREG | `os.mkfifo(token_file, 0o600)` at main:334 | SAFE -- token FIFO planted input proves the startup guard. | `TOKEN-FIFO-UNGUARDED` failed by timeout; full gate passed. | Added token non-regular guard. | `test_token_file_fifo_refuses_startup_without_reading`. |
| C3 stale `[-1]` over produced records | No unguarded final `recs[-1]` sample remains. | SAFE -- zero unguarded record-tail reads. | Self-sweep C3 count 0; pyflakes clean. | Deleted `_last_record_text`. | Full gate. |
| C4 negative acceptance assertions | `assert marker_not_equal_asserts(break_file)` at red:1209 | SAFE -- structural AST NotEq/Name MARKER detector with BREAK/EVADE/POSITIVE controls. | MARKER-GUARD-BREAK and EVADE mutants failed. | Replaced grep with AST walk. | `test_no_not_equal_marker_assertions`. |
| C5 substring/tail anchors classifying outcomes | `resp.split(b"\r\n", 1)[0]` sample at red:1230 | SAFE -- status classification uses the complete HTTP status line. | Full gate `539 passed`. | None. | Full gate. |
| C6 env-domain fail-opens | Empty class. | EMPTY. | Static scan 0. | None. | N/A. |
| C7 lossy decodes on decision path | `errors="ignore"` sample at red:1129 | SAFE -- row #26 by design; UQ mutants prove the decoder choice is load-bearing. | UQ-REPLACE-BOTH failed 5; single decoders failed 1 each. | None. | UQ mutant set. |
| C8 broad catches | `except OSError:` sample at red:53 | SAFE -- bounded readiness probes only; later real calls fail loud. | Full gate `539 passed`. | None. | Full gate. |
| C9 waits/polls + ordinal gates | `deadline = time.time() + 10` sample at main:67 | SAFE -- bounded deadlines; no fake selects behavior by ordinal. | Self-sweep selected run `12 passed`. | None. | Full gate. |
| C10 skips/xfails that cannot fire | Only historical docstring text contains skip wording. | EMPTY executable class. | Static scan 0 executable markers. | None. | N/A. |
| C11 world-scoped enumerations | `glob("*.json")` sample at main:180 | SAFE -- glob scope is fixture-owned record dirs; process census is external, not a test oracle. | Full gate `539 passed`. | None. | Full gate. |
| C12 signal installs before try | Empty class. | EMPTY. | Static scan 0. | None. | N/A. |
| C13 `/proc/<pid>/exe` races | Empty class. | EMPTY. | Static scan 0. | None. | N/A. |
| C14 mirrors of code under test | `_ORACLE_INVIS_RANGES` sample at main:2156 | SAFE -- oracle data is independent copy plus equality guard; algorithm mutants still run. | ORACLE-DRIFT failed; O-TABLE-DROP failed. | Added extras equality. | `test_oracle_table_equals_the_impl_table`. |
| C15 two counters over different populations | `assert len(recs) == n0 + 1` sample at red:1232 | SAFE -- record counts compare one fixture-owned population. | Full gate `539 passed`; RECORDLESS mutants failed. | Added missing record pins. | RECORDLESS_400_APIKEY/XTRACE mutants. |
| C16 redundant/dead guards | `_last_record_text` absent; no final file:line by design. | SAFE -- helper deleted and pyflakes clean. | pyflakes rc 0. | Deleted helper. | Full gate. |
| C17 hardlink-clobbering writes | Empty class. | EMPTY. | Static scan 0. | None. | N/A. |
| C18 other families | `timeout=10` sample at main:339 | SAFE -- subprocesses have timeouts; FIFO and symlink planted controls run. | Self-sweep selected run `12 passed`; full gate `539 passed`. | Added startup guard tests. | FIFO/symlink tests. |

## GATE evidence

### `$PC_PY` two-file gates from `git archive <PIN>` copy plus the four scope files

```
archive gate 1 rc=0
539 passed in 176.44s (0:02:56)

archive gate 2 rc=0
539 passed in 176.48s (0:02:56)
```

### Red file standalone

```
red standalone rc=0
200 passed in 76.27s (0:01:16)
```

### `pyflakes` on the four files

```
pyflakes rc=0
```

### `lint_delta.py --base 58741bb23b28ecd574b4f8472cd88dba658ceaad`

```
lint_delta rc=0
lint_delta (worktree vs 58741bb23b28ecd574b4f8472cd88dba658ceaad): 3 .py changed, 0 NEW pyflakes hit(s), 0 removed
```

### `ap_screen.py`

```
ap_screen rc=0
--- TEST_SCREEN over 2 path(s): 0 hits over 2 files ---
```

### Red-before for FIFO and dangling symlink on a parent-copy backend plus final tests

```
FAILED tests/test_s0_01_scripted_backend.py::test_token_file_fifo_refuses_startup_without_reading
FAILED tests/test_s0_01_scripted_backend.py::test_dangling_record_dir_symlink_refuses_startup
2 failed in 20.95s
```

The failure lines are both `TimeoutExpired ... timed out after 10 seconds`. The final targeted class run is:

```
12 passed in 11.00s
```

### Process census after runs

Full census wrote 40 python rows. One foreign production `scripted_backend.py` was already running under `/home/rocco/agent-factory/proofs/S0-01/tools/scripted_backend.py` with its token-file argument redacted; I did not touch it. Lane-filtered residue showed only the Hermes lane runner and the census command itself, not a live D5l backend child.

```
lane python/scripted-backend residue rows: 2
/proc/1465527/cmdline argv=['/home/rocco/.hermes/hermes-agent/venv/bin/python3', '...hermes lane runner...', '--in', '/home/rocco/agent-factory/.lanes/s0-01-d5l-backend-the-class-closed-struc-58741bb2/tree', '...prompt arg elided...']
/proc/1667063/cmdline argv=['/usr/bin/bash', '-c', '...process-census-filtered command...']
```

### GitNexus detect_changes

Native MCP detect_changes after the edit reported 12 changed symbols, 3 changed files, 0 affected processes, risk_level low. The changed files were the three Python scope files; `cost_probe.py` was unchanged.

### Report lint

The final report-lint command was run after this report was written, without `--rev`, because every `backend`, `main`, `red`, and `cost_probe` reference above targets the final worktree bytes.

```
report_lint rc=0
report_lint: 34 refs — OK 34, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```

## NOT_DONE

| item | reason |
|---|---|
| Sandbox 3.11 leg | Not run here by brief; coordinator/sandbox-owned. |
| PC `-n 8` gate of record | Not run here by brief; coordinator-owned. |
| Push / PR / outward action | Not allowed by lane role. |
| Commit | Not requested and branch/worktree rules reserve checkpointing to the coordinator. |

## DISCREPANCIES

1. The in-repo D5l brief file says `PIN: 13c1bd28713a61fdf1106e2872775ce47c1a7fe6`, while the live lane prompt and worktree HEAD used `58741bb23b28ecd574b4f8472cd88dba658ceaad`. I used the live worktree HEAD for diff/gate base and the requested `PIN: 13c1bd2` wording in this report header.
2. `cost_probe.py` already prints `/proc/loadavg`; my wrapper also printed it, so the pasted cost output has duplicate load-before/load-after lines. The rc was 0 and the timing table is still usable.
3. The first archive-copy gate attempted under `/tmp` failed before pytest because `/tmp` hit inode exhaustion from full-repo archive extraction. I cleaned only my own `/tmp/d5l-*` scratch dirs and re-ran both archive gates under the lane scratch directory; both then passed.
4. A process deviation occurred before this final report: I used tool/schema discovery and loaded skills during the earlier compressed context despite the lane's context-budget carve-out. After the user explicitly instructed skill reload after compression, I reloaded the three named skills and continued.
5. GitNexus CLI fallback via `scripts/gn_mcp.py` failed in the linked worktree because `.gitnexus/run.cjs` was absent there. The native GitNexus MCP `detect_changes` call with explicit worktree then returned the summary stated above.

## SELF-ATTACK

1. A hostile reviewer will try another spelling of `!= MARKER`. The guard is AST-based over both test files, not grep-based; the BREAK and EVADE scratch files prove two spellings, and the MARKER-GUARD mutants failed.
2. A hostile reviewer will blank recorded successful header/body fields while preserving status codes. The D5l served audit pins the positive record values, and RECORD-HDRVAL-BLANKED plus BODYSTR-RECORD-BLANKED/ONECHAR failed.
3. A hostile reviewer will replace regular files with special files or dangling paths to get startup/read hangs. The token FIFO and dangling record-dir tests run subprocesses with timeouts, prove parent red-before timeouts, and final backend refuses both at startup with rc 2 and named stderr.
4. A hostile reviewer will drift one invisible-table literal while another stays correct. The impl extras literal, oracle extras literal, and pinned range equality now cross-check each other; IMPL-EXTRA-DRIFT, ORACLE-DRIFT, ORACLE-EXTRA-DRIFT, and table-drop mutants ran.
5. A hostile reviewer will challenge that this PC lane self-accepted. I am not issuing a gate verdict; this report is a build-lane proposal pending sandbox adversarial verification.
