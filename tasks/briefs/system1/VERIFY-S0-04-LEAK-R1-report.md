# VERIFY-S0-04-LEAK-R1 report (task #287, round 2)

Lane: adversarial-verifier (sandbox, Opus 5.5). Started 2026-09-25T22:35:16Z (bucket 22:3xZ). Written incrementally.
Target: the commit whose subject starts "S0-04-LEAK R1 landed (task #287" (origin a525376, pushed from a local pre-push id; called R1 below). Its parent
tree carries R0 (the first landing, now 1f764fe on origin). The question: may the owner sign R1's `result.json` now?
Scope: only what R1 changed (the brief's items 1-5). Record under test: the "R1" section at the end of
`tasks/briefs/system1/S0-04-LEAK-report.md`. Scratch: `<scratch>/vs004r1/` (`<scratch>` = the session scratchpad);
short basetemps under `/tmp/v4r/`. My first report stays as it is.

## STATUS

DONE. **Gate: MERGE-READY-WITH-FOLLOWUPS: the owner may sign the R1 landing's `result.json` now** (section 9). Items 1-5 all run through the real code. The new rule is a superset of R0's: structurally, and 0 losses in 1.3 million fuzz strings. F3's shapes are caught and the rule is linear to the 8 MiB cap (at most 2.43 s through the real CLI). Every YAMLError class now reports only a position. The re-mint reproduces: the ledger is byte-identical and the result differs only in the two hashes and six volatile fields. The F4 test reds on every neighbouring state and holds in the CI shape. Mutation: 21 of 32 killed, the survivors classified. 7 findings (G1-G7), none blocking. G2 (an explicit YAML type tag prints a non-`sk-` value through the catch-all, R0 and R1 alike) is the only one whose fix touches an attested file; batch it with the issue #59 re-sign. G4: the re-sign landing must set `EXPECTED_PENDING = set()`.

## 1. PREMISE, re-measured (22:3xZ, in the tree)

HEAD is 7ecd6c2, a retro commit after R1 that touches only `docs/INCIDENT-LOG.md`, the ledger (+1 line, task #302) and
the wiki. No file under test changed after R1: `cmp` of the two tools and the S0-04 test file against a `git archive` of
a525376 is equal. Tracked dirt: none. Identities (sha256 prefix): R0 checker 881710af6818ee0d (the first round's),
R1 checker 033333c57e3c371e, R1 capture tool f455144f8889e5ff (the builder's R1.8 values).
```
$ python3 scripts/check-proof-status.py .   -> proof-status: WARNING S0-04: ACCEPTED with the anchor PENDING ... ; rc=0
$ python3 scripts/validate-ledger integrity --root . | tail -3   -> blocked_host 0/1, conformance 3/3, execution_proof 9/9; rc=0
$ bash scripts/test_summary.sh --basetemp=/tmp/v4r/bt tests/test_s0_04_compression.py tests/test_proof_status.py
pytest-exit: 0
pytest-summary: 189 passed in 13.32s          (2 files set=2fa20f3af1f3; the builder's R1.8 count)
```

## 2. Item 1: the new key-assignment rule (22:4xZ)

Venue: `<scratch>/vs004r1/r1` = `git archive a525376 proofs scripts tests/test_s0_04_compression.py tests/conftest.py
tests/test_proof_status.py` (the three files under test `cmp`-equal to the tree); `<scratch>/vs004r1/r0` = R0's two tools
(`git show a525376~1:...`). Every key and value is `secrets.token_hex(16)` at run time; outputs are reduced to verdicts
and booleans.

**No loss: R1's rule is a superset of R0's, structurally and by fuzz.**
- Structure: with zero tail segments the new rule is the old one. The three look-behinds test the last 4 or 5 characters
  of the bare name, and no listed name ends in `_env`, `_file` or `_path`. The separator `\s*(?:["']\s*)?[:=]`
  accepts the same language as `\s*["']?\s*[:=]`: `\s*[:=]` with no quote, `\s* Q \s* [:=]` with one. The name list,
  the left anchor and the value part are byte-identical. The checker's `bearer`, `sk-key` and `hex64` are byte-identical
  to R0. R1's `LEAK_RE` text is R0's text + `|` + the new rule (checked by `startswith`).
- Fuzz (`<scratch>/vs004r1/fuzz.py`, the rules imported from the real files): 900,000 structured strings (names in 11
  cases and spellings, 18 tail segments including `_env`/`_ENV`/`_File`, 19 prefixes, 17 separators, 11 values; two
  seeds) and 400,000 character-level strings. **0** strings that R0's rule matches and R1's does not; 80,781 new-only
  hits (the tails). The capture guard: 300,000 strings, **0** that R0's guard withholds and R1's prints.

**The verdicts through the real CLIs.** First, my round-1 harness (`<scratch>/vs004/anchors.py`, 75 rows, unmodified) with
new = R1 and old = R0. The checker changes on exactly A20, A21, A22 (`SECRET_KEY=`, `AWS_SECRET_ACCESS_KEY=`,
`OMNIROUTE_API_KEY_2=`: PASS -> key-assignment). The capture guard now withholds every assignment row except A18
(`9API_KEY=`) and A19 (`MYAPI_KEY=`), glued by a digit or letter as the contract wants, and A23 (JSON-in-JSON escaped
quotes: F2's class, still open as task #300). No row went from caught to passing, and there were 0 echo flags. This matches
the builder's R1.3 claim.

Then 70 new shapes (`<scratch>/vs004r1/anchors_r1.py`, the same method: a scratch copy of `fixtures/evidence-pass`, the
text planted as a raw file or a serialized JSON field, the real checker CLI; the real capture CLI's `--max-seq` error path):

| Group | Shapes | Checker R1 (R0) | Capture R1 (R0) |
|---|---|---|---|
| tails 1-4 | `token_a=`, `token_a_b=`, `token_a_b_c=`, `token_a_b_c_d=`, `SECRET_A_B_C_D=`, `AWS_SECRET_ACCESS_KEY_ID=` (3 after SECRET), `OMNIROUTE_API_KEY_PROD_EU_WEST_1=` (4 after API_KEY) | caught (PASS) | withheld (printed) |
| tails of 5 | `token_a_b_c_d_e=`, `PASSWORD_1_2_3_4_5=`, `GITHUB_TOKEN_FOR_CI_BOT_V2_PROD=`, `OMNIROUTE_API_KEY_PROD_EU_WEST_1_B=` | **PASS** (PASS) | **printed** (printed) |
| exclusions, any case | `api_key_env=`, `API_KEY_ENV=`, `Api_Key_Env=`, `token_File=`, `SECRET_PATH=`, `password_Path=`, `SECRET_ENV=`, `api_key_env_file=` (last is `_file`), `OMNIROUTE_API_KEY_FILE=` | PASS (PASS) | printed (printed) |
| exclusion in the middle, or not exact | `api_key_env_2=`, `token_file_x=`, `secret_path_prod=`, `api_key_envx=`, `api_key_xenv=` | caught (PASS) | withheld (printed) |
| inside longer identifiers | `MY_TOKEN=` caught (caught); `x-token_a=`, `APIKEY_ID=` caught (PASS); `ACCESS_TOKEN_SECRET=` caught (caught); `MYTOKEN=`, `x9token_a=` (glued), `TOKENS=`, `SECRETS_KEY=` (plural), `token_é=`, `tokenizer_x=` PASS (PASS) | as listed | withheld where caught, else printed |
| quotes, `:` and `=`, spaces | `"api_key_2": "v"`, `'api_key_2' = 'v'`, `api_key_2="v"`, `api_key_2: v`, `api_key_2   =   v`, newlines around `=`, `api_key_2 "= v`, a serialized JSON field `api_key_2` or `SECRET_KEY` | caught (PASS) | withheld (printed) |
| quote shapes both refuse | `api_key_2 '' = v` (two quotes), `api_key_2 := v` | PASS (PASS) | printed (printed) |
| several on one line | `a=1 token_x=v b=2`, `x=1;api_key_2=v;y=2` caught (PASS); `token_count=1 password=v` caught (caught); `token_count=1, secret_name=abc` PASS (PASS) | as listed | as listed |
| the 8-character floor | `token_a=abcdefgh` (8), `token_a=abc.defg` (8) caught (PASS); `token_a=abcdefg` (7), `token_a="abcdefg"`, `token_a=abc defgh` PASS (PASS) | as listed | as listed |

Every verdict follows from the rule as written: the bound `{0,4}`, the exclusions only on the LAST segment, the `\b` after
the tail, `[A-Za-z0-9]` segments. Two residuals follow from the design (finding G1): a credential name with five or more
segments after its last listed word, like `GITHUB_TOKEN_FOR_CI_BOT_V2_PROD=`, and a key stored under a reference-named
variable, like `OMNIROUTE_API_KEY_FILE=<key>` (the builder disclosed the second in R1.9). Both pass both screens, as they did
under R0: nothing is lost.

**The other direction: ordinary text the rule now takes.** `token_count: 12345678`, `password_hash: <hex>`,
`secret_name: mysecretname`, `api_key_id: <hex>`, `token_type: bearer_token`, `secret_version: 12345678`,
`token_limit: 100000000`, `password_policy: minimum8`, `secret_ref: vault/kv/app`: all caught by R1, all PASS under R0.
`token_type: Bearer` (6 characters), `max_tokens: 12345678`, `prompt_tokens=12345678` and `token_ids: [1, 2]` still pass.
**Does any such text occur in S0-04's evidence?** No. I scanned `proofs/S0-04/evidence` and every fixture (the three bundles
and the two request fixtures) raw, with the fingerprint masked as the checker does. I also scanned them decoded (every JSON
key and string, every base64 body). Result: R1 rule 0, R0 rule 0, R1 capture guard 0, raw and decoded. The only name-like
identifiers there are `api-key` (4), `api_key` (8) and `token` (40, inside `max_tokens` and the like), with no tail at all.
**Does it matter?** Not for this mint: the positive leg PASSes (section 4). For a future capture, a response body is base64
(never screened raw), `response.json` stores headers as `[name, value]` pairs (a comma, never `[:=]`), and the upstream body
must equal the committed fixture. So a new false positive needs an `extra_headers` key or an upstream-record header named
like `x_token_id`. It would fail closed and name the rule (finding G3).

**Backtracking** (`<scratch>/vs004r1/timing.py`; the checker's `_leak_hit` runs all four rules, the capture's `safe`; seconds
at 32,000 / 1,000,000 / 8,388,608 characters, checker/capture):
```
' token' + spaces                  0.006/0.007 | 0.205/0.157 | 1.307/1.374
' token=' + spaces (no value)      0.005/0.005 | 0.146/0.154 | 1.339/1.320
'_token' x N                       0.013/0.013 | 0.292/0.281 | 2.391/2.304      (the worst)
'token_' x N                       0.009/0.009 | 0.284/0.278 | 2.274/2.324
'token' + '_x' x N                 0.003/0.003 | 0.088/0.089 | 0.802/0.740
'_token_a_b_c_d' x N               0.003/0.003 | 0.109/0.110 | 0.907/0.972
'_api_key_env' x N                 0.005/0.005 | 0.144/0.143 | 1.193/1.183
'token' + quotes                   0.003/0.004 | 0.118/0.121 | 0.935/1.013
'token' + quote-space pairs        0.004/0.004 | 0.118/0.120 | 0.990/1.044
'token' + '=' x N                  0.004/0.004 | 0.121/0.123 | 1.001/1.087
(21 shapes in all, every one about x8 from 1 M to 8 M characters: linear)
```
Through the real checker CLI, a bundle file of exactly 8,388,608 characters took 2.39 s (`_token` run), 2.43 s (`token_` run)
and 1.29 s (` token` + spaces): rc 0 and PASS each time. F13 is closed: in round 1 the old separator took 6.3 s at 32,000
spaces.

## 3. Item 2: the YAML path (`do_config`) (22:4xZ)

Driver `<scratch>/vs004r1/yamlprobe.py`: the REAL CLI (`capture_leg.py --config --profile <file> --out <dir>`, PyYAML 6.0.1),
R1 and R0 tools, 26 malformed profiles × {a hex32 value, an `sk-`+hex32 value}, the value on the line the error points at.
Per run: rc, the longest run of the value found anywhere in stdout+stderr, and stderr with every run of 5 or more
characters of the value masked as `<v:N>`.

| Error class | Cases (all with the fake value on the marked line) | R1: stdout+stderr | Longest run of the value in R1 output (R0) |
|---|---|---|---|
| ScannerError | unclosed double quote; tab indent; a colon after the value; a bad escape in a quoted value; `@` before the value; an unclosed single quote at EOF | `capture_leg: profile <p> is not valid YAML at line L, column C`, rc 1 | 1-2 (R0: 22-32 for hex; the colon row 32 for `sk-` too, F1b) |
| ParserError | an unclosed flow sequence; bad indentation after the key line; a flow mapping missing a comma | the position line, rc 1 | 1-2 (R0: up to 32) |
| ComposerError | an undefined alias named by the value; a second document | the position line, rc 1 | 1-2 (R0: 32 for the alias, the value is the alias name) |
| ConstructorError | an unknown `!!python/name` tag; an unhashable key; a bad `!!binary` (`sk-` value; the hex one decodes and is not an error); `!!str` on a mapping; a merge of a scalar | the position line, rc 1 | 1-2 (R0: up to 32) |
| ReaderError | a NUL after the value; C1 controls after the value | `... is not valid YAML at an unknown position` (a ReaderError has no mark), rc 1 | 1-2 |

**Every YAMLError class: no part of the value reaches stdout or stderr.** A run of 1-2 characters is a chance overlap with
the path or the position digits. F1b is closed for all five classes; R0 printed up to 32 characters.

**The paths that are not a YAMLError:**
- no content: a non-UTF-8 byte (`UnicodeDecodeError ... in position 129`); deep nesting (`RecursionError`); `!!timestamp`
  on the value (`AttributeError: 'NoneType' object has no attribute 'groupdict'`); a list at the top (`profile <p> is not a YAML
  mapping`); a date in `extra_headers` (`TypeError: Object of type date is not JSON serializable`).
- **the whole value printed (finding G2):** an explicit scalar tag on the value: `api_key: !!int <v>` ->
  `capture_leg: ValueError: invalid literal for int() with base 10: '<v:32>'`; `!!float` -> `ValueError: could not convert string
  to float: '<v:32>'`; `!!bool` -> `KeyError: '<v:32>'`. The value appears in full (32 of 32), R1 and R0 alike; an `sk-` value is
  withheld by the `sk-` rule (`'sk-` has a quote before it). PyYAML's constructors raise plain `ValueError`/`KeyError` for a bad
  explicit tag, so `except yaml.YAMLError` does not see them and `main`'s catch-all prints the message through `safe()`, which
  has no rule for a bare value. The builder's R1.9 item 3 ("the other exceptions `do_config` can raise carry a path or a
  byte offset, not content") is therefore not true for these three. Exposure is F1's: `HERMES_PROFILE` pointed at a live
  profile whose inline key is not `sk-`-shaped and carries an explicit type tag. Implicit resolution does not echo a value:
  the implicit scalars that make a constructor raise print no content (measured: `0x_` and `0b_` give `invalid literal for int()
  with base 16: ''`, and `2026-13-45` gives `month must be in 1..12`). Fix: catch every exception
  of `yaml.safe_load` in `do_config` (`except Exception`) and report the position when a mark exists, else "an unknown position".

## 4. Item 3: the re-mint, reproduced from a git archive of R1 (22:4xZ)

Venue: `<scratch>/vs004r1/remint` = a copy of `git archive a525376 proofs scripts` (the whole attested closure, no `.git`).
```
# controls
$ python3 scripts/validate-ledger integrity --root .      (the archive as committed)   -> 12 PRESENT, execution_proof 9/9, rc=0
$ python3 scripts/ledger-gen --root . --output <scratch>/l0.json ; cmp with R1's proofs/ledger.json    -> rc=0, byte-identical
# negative control: R0's result.json (a525376~1) beside R1's tools
$ python3 scripts/validate-ledger integrity --root .      -> S0-04 INVALID; attestation-mismatch: S0-04 proofs/S0-04/check_compression.py; rc=1
# the re-mint (R1's result restored first), 2026-09-25T22:45:31Z
$ python3 scripts/proof-runner run --proof S0-04 --venue sandbox --root .   -> rc=0
$ python3 scripts/validate-ledger integrity --root .                        -> 12 PRESENT, execution_proof 9/9, rc=0
$ python3 scripts/ledger-gen --root . --output <scratch>/l2.json ; cmp with R1's proofs/ledger.json      -> rc=0, byte-identical
```

| Pair (`proofs/S0-04/result.json`, every leaf) | Leaves | Identical | Changed |
|---|---|---|---|
| R0 (a525376~1) -> R1 (committed) | 71 | 63 | 8: `attestation["proofs/S0-04/check_compression.py"]` 881710af... -> 033333c5..., `attestation["proofs/S0-04/tools/pc/capture_leg.py"]` 7b202db0... -> f455144f..., `digest`, `recorded_at`, the four run timestamps |
| R1 (committed) -> my re-mint | 71 | 65 | 6: `digest`, `recorded_at`, the four run timestamps (all volatile) |

- All 44 attestation entries of R1's result equal the sha256 of the R1 archive's bytes (0 mismatches). Both legs' exit codes
  (0, 1) and `stdout_sha256` (9166513f18cb..., caf92711fbc2...) are the same in R0, R1 and my re-mint, and so are
  `negative_control` and the negative leg's `failure_reason: off: compression-header-missing`. `env_fingerprint` is `sandbox:vm`
  throughout. PASS for the same three assertions, with byte-identical checker output.
- The ledger line follows from the two hashes alone (ledger-gen's own `_normalized_digest`): my re-mint normalizes to
  7daeba65ace36822 (R1's committed value); with R0's two hashes put back it normalizes to 5b49bfb5cb33a1ea (R0's committed
  value). `proofs/ledger.json` R0 -> R1: one line, S0-04's `normalized_digest`.
- The capture question for R1: top-level AST, R0 -> R1: `capture_leg.py` differs in `LEAK_RE` and `do_config` only, and
  `check_compression.py` in `LEAK_PATTERNS` only (same definitions in the same order). `LEAK_RE` sits on the error path,
  and the new `do_config` branch runs only when `yaml.safe_load` raises, before anything is written. So no evidence byte
  depends on R1, and attesting R1's bytes over the committed evidence stays honest (the builder's R1.6 holds).

Verdict item 3: **met, reproduced.**

## 5. Item 4: the F4 fix in `tests/test_proof_status.py` (22:4xZ)

Venue: `git clone --shared --no-tags --no-checkout` of this repo into `<scratch>/vs004r1/clone` (no `accepted/*` ref: the CI
shape; objects read through alternates, nothing written to the real repository), sparse checkout of `proofs/ scripts/
todo/ docs/governance/ tests/test_proof_status.py tests/conftest.py`, detached at R1. The clone's own checker and test
file (R1's bytes); `tests/test_proof_status_r0.py` = R0's file (`git show a525376~1:...`). The old S0-04 tag object was
recovered from the parent of 1f764fe (R0's landing on origin, which deleted it). For the "new tag" states a throwaway key
(GNUPGHOME `/tmp/v4r/g1`) signs, and its public half is APPENDED to the clone's owner key file. Driver
`<scratch>/vs004r1/f4states.sh`, three committed-state tests per run (`-k`), short basetemp.

| State | Checker | R1 test file | R0 test file |
|---|---|---|---|
| S1 (b) as committed, CI shape | S0-04 WARNING, rc 0 | 3 passed | 3 passed |
| S1r (b) with every tag object also a ref (the dev-tree shape) | the same | 3 passed | 3 passed |
| S2 a second pending proof (S0-03's tag file removed, PENDING declared) | WARNING S0-03 and S0-04, rc 0 | **FAILED** `test_committed_tree_anchor_state_is_the_declared_pending_one` | 3 passed (the hole) |
| S3a pending S0-04 whose OLD tag object is present | stale declaration + `changed since`, rc 1 | 3 FAILED | 3 FAILED |
| S3b pending S0-04 whose NEW valid tag object is present | stale declaration, rc 1 | 3 FAILED | 3 FAILED |
| S4a an undeclared warning of another kind (the checker mutated to print `WARNING S0-05: a warning of another kind`) | two warnings, rc 0 | **FAILED** (the `len(pending) == len(warnings)` assertion) | 3 passed |
| S4b an undeclared PENDING-style warning for S0-05 (the checker mutated; no declaration in the ledger) | two warnings, rc 0 | **FAILED** | 3 passed |
| S4c the checker mutated to print no warning at all | nothing, rc 0 | **FAILED** | 3 passed |
| S5 after the owner's re-sign: a NEW valid S0-04 tag file, PENDING removed, `EXPECTED_PENDING` not edited | nothing, rc 0 | **FAILED** | 3 passed |
| S6 neither (S0-04's PENDING removed, no tag) | AF-AP-32 error, rc 1 | 3 FAILED | 3 FAILED |

The clone ended reset (0 changed tracked paths, 0 refs).

**Each assertion line carries weight** (weakened copies of the R1 test, run on the same states; `<scratch>/vs004r1/f4tm.sh`):
```
state                                        R1 test | TM1: no len assertion | TM2: <= in place of == | TM3: >= in place of ==
S1 (b) as committed                          green   | green                 | green                  | green
S2 a second pending proof                    RED     | RED                   | RED                    | green   <- missed
S4a a warning of another kind                RED     | green   <- missed     | RED                    | RED
S4b an undeclared PENDING-style warning      RED     | RED                   | RED                    | green   <- missed
S4c the checker prints no warning            RED     | RED                   | green   <- missed      | RED
S5 after the re-sign, set not edited         RED     | RED                   | green   <- missed      | RED
```

Verdict item 4: **the F4 fix reds on every neighbouring state asked for** (a second pending proof, a pending S0-04 whose tag
object is present, an undeclared warning), **holds in the CI shape** (S1, no refs) and in the dev shape (S1r), and every
one of its assertions is needed. One consequence to plan for (finding G4): S5 shows that the owner's re-sign alone turns the
test red. The landing that commits the owner's tag object and removes the PENDING line must also set `EXPECTED_PENDING`
to `set()` in the same commit, or CI goes red and push_clean's CI gate refuses the next push. The comment above the
constant says S0-04 "leaves this set"; the governance README's re-sign block does not mention the test.

## 6. Item 5: mutation on R1's code (22:5xZ)

Harness `<scratch>/vs004r1/mutate_r1.py` on `<scratch>/vs004r1/mut` (a copy of the R1 archive: `proofs/`, `tests/`). AF-AP-223
rules: the unmutated CONTROL first, green at the full count; each edit text found exactly once in its file; both files
restored and re-hashed after every run; KILLED only on a named FAILED test with no ERROR and an unchanged total; else
INVALID. Group A edits the rule in BOTH files at once, so the lock test stays green and only behavioural tests can kill.
```
CONTROL (unmutated): rc=0 156 passed in 7.84s          (re-run green before each batch: 8.39s, 8.26s)
A1  both: name tail removed (back to \b)        KILLED  6: the three tail cases (checker) + the tailed capture cases
A2  both: name tail unbounded                   KILLED  test_both_screens_are_linear_on_a_hostile_run[names]
A3  both: _env no longer excluded               KILLED  both ordinary tests [api_key_env=OMNIROUTE_API_KEY]
A4  both: _file no longer excluded              KILLED  both ordinary tests [DB_PASSWORD_FILE=/run/secrets/db]
A5  both: _path no longer excluded              KILLED  both ordinary tests [SECRET_PATH=/etc/app/secret.d]
A6  both: tail bound 1                          KILLED  [AWS_SECRET_ACCESS_KEY] in the checker and the capture test
A7  both: tail bound 2                          SURVIVED (156 passed)
A8  both: tail bound 3                          SURVIVED (156 passed)
A9  both: tail bound 5                          SURVIVED (156 passed)
A10 both: _env excluded only in lower case      SURVIVED (156 passed)
A11 both: _file excluded only in lower case     KILLED  both ordinary tests [DB_PASSWORD_FILE=...]
A12 both: the \b after the tail removed         SURVIVED (156 passed)   equivalent: [:=] must follow at once
A13 both: the quadratic separator restored      KILLED  [spaces] and the size-cap CLI test (the run took 73 s)
A14 both: the separator takes = only            KILLED  capture [api_key: ] + test_inline_api_key_in_the_config_leg_is_a_credential_finding
A15 both: the separator takes no quote          KILLED  test_inline_api_key_in_the_config_leg_is_a_credential_finding
A16 both: tail segments letters only            KILLED  [OMNIROUTE_API_KEY_2] in the checker and the capture test
A17 both: hyphen tails too                      KILLED  both ordinary tests [x-api-key-id]
B1  checker only: tail removed                  KILLED  the three checker tail cases + the lock
B2  capture only: its key-assignment alternative removed   KILLED  15 (the lock, the assignment and separator capture cases)
B3  capture only: its alternative's left anchor removed    KILLED  the lock + capture ordinary [nextPageToken]
C1  checker sk-key refuses a hyphen before (round-1 M23)   KILLED  test_a_key_after_a_separator_still_fails_the_checker[--sk-key]
C2  both: the name refuses a hyphen before (round-1 M24)   KILLED  [--key-assignment] in the checker and the capture test
C3  capture sk refuses a slash before (round-1 M25)        KILLED  test_capture_leg_withholds_a_key_after_a_separator[/-sk-key]
C4  checker sk-key lets a digit glue (round-1 M7)          SURVIVED (by design: a pin would assert a key passes)
D1  the YAML handler never catches              KILLED  all 6 YAML cases
D2  the message carries the exception text      KILLED  all 6 YAML cases
D3  `from None` dropped                         SURVIVED (equivalent at the CLI: main prints str(error) only)
D4  context_mark preferred                      SURVIVED (equivalent: either mark is a position)
D5  the handler narrowed to ScannerError        SURVIVED (156 passed)   NOT equivalent, see below
D6  the handler narrowed to MarkedYAMLError     SURVIVED (a ReaderError then reaches the catch-all, whose message holds no value)
D7  the message adds the problem text           KILLED  all 6 YAML cases (the format is fullmatched)
D8  the column off by one                       SURVIVED (the tests pin the format, not the numbers)
A: KILLED 12, SURVIVED 5 | B: KILLED 3 | C: KILLED 3, SURVIVED 1 | D: KILLED 3, SURVIVED 5 | INVALID 0 | files restored: True
```
- R1 closes round 1's F10: the no-loss mutants that survived R0 (M23-M25) are now killed (C1-C3).
- **D5 is not equivalent (finding G5).** With the handler narrowed to `ScannerError`, the real CLI prints the WHOLE fake
  value for a ParserError (`api_key: [<v>` unclosed) and a ComposerError (`api_key: *<v>`), and all 156 tests stay green.
  I checked this with a mutated copy through `--config`: whole value in the output, True for both. The six F1b cases are all
  ScannerErrors, so the handler's breadth is not pinned. Fix: one `YAML_ERRORS` case each for a parser, a composer and a
  constructor error.
- A7-A9 and A10 (finding G6): the tests pin a bound of at least 2 (`AWS_SECRET_ACCESS_KEY`), not the chosen 4, and not
  the upper edge (a five-segment tail passes by design). They pin `_file` and `_path` in upper case and `_env` in lower
  case only. A12, D3 and D4 are equivalent; D6 and D8 change no content (a ReaderError message holds a character code and
  a position; the column is cosmetic).
- The F4 test's own mutation is in section 5: three checker mutants (S4a-S4c) killed, and three weakened copies of the test
  (TM1-TM3) each let a bad state through.
- One more check of the other direction, the capture tool's OWN error messages under the wider guard. None became
  withheld: `no OMNIROUTE_API_KEY= line in <tmp>/omniroute_api_key.env`, `key file <tmp>/OMNIROUTE_API_KEY_FILE is
  group/other readable; ...`, `key file not found: <tmp>/secrets/token_store.env`, `record dir not found: <tmp>/token_records`,
  `profile has no provider named 'my_token_router'` all print in full.

## 7. Other checks (23:0xZ)

- **Red-green:** R1's test file run against R0's tool bytes (`cmp` against `git show a525376~1:...`) gives `26 failed, 130 passed
  in 73.62s`. The failures are the three tail cases, the seven capture assignment cases, the seven capture
  separator-assignment cases, the lock, the six YAML cases, and the two linearity tests. This reproduces the builder's R1.4
  count; the other 32 new cases are no-loss pins and controls that pass on R0 by design, as the builder's R1-D1 says.
- **Static gates (in the tree):** `python3 -m pyflakes` on both tools and both test files: rc 0. `LC_ALL=C grep -c
  $'\xe2\x80[\xa8\xa9]'`: 0 for both tools, both test files, `result.json` and `proofs/ledger.json`.
- **The push rewrote R1's id while I worked:** origin now holds it as a525376 (`git log`, 22:34:24Z, the same subject).
  `git diff --quiet <the pre-push id> a525376` over `proofs/S0-04`, `proofs/ledger.json`, both test files and
  `scripts/check-proof-status.py` is equal. From a525376 to the local HEAD then (a live-state commit) and to origin's tip, `proofs/S0-04` and the ledger
  are unchanged; `result.json` has sha256 fbb3f8495389caa9 at both ids. So the tip holds exactly the result under test, and
  `check-proof-status.py .` gives rc 0 with the one S0-04 WARNING.
- **Stale context:** R1's two new code comments (the rule's tail, bound and separator in `check_compression.py`; the
  YAML handler in `capture_leg.py`) say what the code does, and the `sk-key` comment now says "an ASCII letter or digit"
  (round 1's F7). STATUS.md's headline and S0-04 row now say re-minted and PENDING. One parenthetical, `STATUS.md:12` `(the eight tag objects committed as`
  `docs/governance/tags/accepted-<id>.tag` ...), still says eight; seven of those eight remain, since S0-04's was removed (finding G7). The builder's R1.9 item 3 is false for three paths (section 3, G2).

## 8. FINDING INVENTORY (no severity filter)

| # | Class | Finding | Evidence | Contract mapping | Canonical path | Material effect | Reproduction | Suggested fix |
|---|---|---|---|---|---|---|---|---|
| G1 | INFO (design residuals, disclosed in part by the builder) | These pass both screens, as they passed R0 (nothing lost): a name with five or more segments after its last listed word (`GITHUB_TOKEN_FOR_CI_BOT_V2_PROD=`, `PASSWORD_1_2_3_4_5=`); a key stored under a reference name (`OMNIROUTE_API_KEY_FILE=<key>`, `API_KEY_ENV=<key>`); plural names (`SECRETS_KEY=`, `TOKENS=`) | VERIFIED (section 2) | none: R1 closes the three F3 shapes it was asked to | yes | none today | `<scratch>/vs004r1/anchors_r1.py` T5-T8, T11, E1-E6, E12-E14, L4, L5 | none required; a value gate (`known_values_check.py`) behind the shapes covers any name |
| G2 | FOLLOW-UP | `do_config` catches `yaml.YAMLError` only. An explicit scalar tag on the value makes PyYAML's constructor raise a plain `ValueError` or `KeyError`, and `main`'s catch-all prints the whole value: `!!int` -> `ValueError: invalid literal for int() with base 10: '<v>'`, `!!float` -> `could not convert string to float: '<v>'`, `!!bool` -> `KeyError: '<v>'` (32 of 32 characters, R1 and R0 alike; an `sk-` value is withheld). The builder's R1.9 item 3 says these paths carry no content | VERIFIED (section 3) | none: R1's F1b scope is the YAMLError snippet, and the message holds no assignment shape | yes: the real CLI `--config` | hypothetical: an operator-set live profile whose inline non-`sk-` key carries an explicit type tag | `<scratch>/vs004r1/yamlprobe.py` | catch every exception of `yaml.safe_load` in `do_config` and report the position only. It changes an attested file, so batch it with the issue #59 tooling re-sign (STATUS.md: that batch already needs one re-sign of every accepted proof) |
| G3 | INFO | New fail-closed false positives on ordinary tailed names: `token_count: 12345678`, `password_hash`, `secret_name`, `api_key_id`, `token_type: bearer_token`, `secret_version`, `token_limit`, `password_policy`, `secret_ref`. S0-04's evidence and fixtures hold 0 hits, raw or decoded, and no tailed name at all. The capture guard shares them (a withheld message only), and its own error messages still print in full | VERIFIED (sections 2, 6) | none | yes | none for this mint; a future capture fails loudly, naming the rule | `anchors_r1.py` N1-N10 | none now |
| G4 | FOLLOW-UP (procedure) | The F4 test reds at the owner's re-sign unless the same landing sets `EXPECTED_PENDING = set()` (S5). The governance README's re-sign block does not mention it | VERIFIED (section 5, S5) | none (by design: a conscious edit) | yes | CI red and the CI gate refusing pushes if the edit is forgotten | `<scratch>/vs004r1/f4states.sh` S5 | put the edit in the re-sign handoff (and the README's re-sign block), in the same commit that adds the tag object and removes the PENDING line |
| G5 | FOLLOW-UP (test gap) | The six F1b tests are all ScannerErrors. With the handler narrowed to `ScannerError` (mutant D5), a ParserError or a ComposerError prints the whole fake value and all 156 tests pass | VERIFIED (section 6) | none | yes | none today (R1 catches every class, section 3) | `mutate_r1.py D5` + the mutated-copy probe | add a parser, a composer and a constructor case to `YAML_ERRORS` (tests only, no re-mint) |
| G6 | INFO (test gap) | The chosen tail bound 4 is pinned only as "at least 2" (A7-A9 survive), and the upper-case `_ENV` exclusion is unpinned (A10) | VERIFIED (section 6) | none | n/a | none | `mutate_r1.py` | a 4-segment catch, a 5-segment pass and `API_KEY_ENV=` as an ordinary control (tests only) |
| G7 | INFO (prose) | The parenthetical at `STATUS.md:12` (`the eight tag objects committed as`) still says eight; seven remain | VERIFIED | CLAUDE.md prose rule | n/a | none (the headline and the S0-04 row are right) | `ls docs/governance/tags \| wc -l` -> 11 | one word, or task #302's check |

**Citations (path:line at R1 = the tree; each line quotes a token of the cited line):**
- `proofs/S0-04/check_compression.py:93`: the tail `(?:_[A-Za-z0-9]+){0,4}(?<!_env)(?<!_file)(?<!_path)\b` (G1, G6).
- `proofs/S0-04/check_compression.py:94`: the linear separator `\s*(?:[\"']\s*)?[:=]` (F13 closed, section 2).
- `proofs/S0-04/tools/pc/capture_leg.py:50`: the same tail, `(?:_[A-Za-z0-9]+){0,4}(?<!_env)(?<!_file)(?<!_path)\b`, in the guard's third alternative (F1 closed).
- `proofs/S0-04/tools/pc/capture_leg.py:241`: `except yaml.YAMLError as exc:`, the handler that type-tag errors bypass (G2) and that the D5 mutant narrows (G5).
- `proofs/S0-04/tools/pc/capture_leg.py:247`: `raise CaptureError(f"profile {args.profile} is not valid YAML at {where}") from None`, the position-only message (section 3).
- `proofs/S0-04/tools/pc/capture_leg.py:319`: `except Exception as exc:`, the catch-all that prints the `ValueError`/`KeyError` value (G2).
- `tests/test_proof_status.py:469`: `EXPECTED_PENDING = {"S0-04"}`, the pinned set the re-sign must edit (G4).
- `tests/test_proof_status.py:492`: `assert len(pending) == len(warnings)`, the assertion TM1 removes (S4a).
- `tests/test_proof_status.py:493`: `assert pending == EXPECTED_PENDING | ...`, the equality TM2/TM3 weaken (S2, S4b, S4c, S5).
- `tests/test_s0_04_compression.py:1054`: `YAML_ERRORS = (`, the three ScannerError shapes (G5).
- `tests/test_s0_04_compression.py:308`: `def test_both_screens_are_linear_on_a_hostile_run(text):`, which kills A2 and A13.
- `tests/test_s0_04_compression.py:1044`: `def test_capture_guard_carries_the_checker_key_assignment_rule():`, the lock that B1-B3 red.
- `STATUS.md:5`: `the issue #59 tooling batch will need one re-sign of every` accepted proof (the batch G2 can ride with).
- `STATUS.md:12`: `(the eight tag objects committed as` ... (G7).

**Verified and holding (for the record):** no loss against R0 (section 2); every contract shape caught by the checker and now
withheld by the capture guard; F3's three shapes caught; linear to the 8 MiB cap (F13); the builder's 75-row harness claim
and red run reproduced; every YAMLError class reports the position only (F1b); the re-mint reproduced (the ledger
byte-identical, the result's diff only the two hashes and six volatile fields); the F4 test reds on every neighbouring state
and holds in the CI and dev shapes; round 1's no-loss survivors now killed; 21 of 32 R1 mutants killed, with the survivors
classified.

**Reproduced vs reviewed:** every VERIFIED row ran here. **Deliberately skipped:** the coordinator's 8-file gate (the 2-file
premise set ran: 189 passed); the builder's bystander measurement over other proofs (outside S0-04; my scan covered S0-04's
evidence and fixtures raw and decoded); anything on the PC.

## 9. GATE RECOMMENDATION (23:0xZ)

**MERGE-READY-WITH-FOLLOWUPS. Yes: the owner may sign the R1 landing's `result.json` now** (the commit whose subject starts
"S0-04-LEAK R1 landed (task #287", a525376 on origin; `result.json` sha256 fbb3f8495389caa9, unchanged at the tip). I
reproduced every claim this rests on.

**The blocking predicate applied** (a finding blocks only if ALL hold: 1 it maps to a criterion frozen before dispatch, or to
an explicit repository-wide invariant; 2 it reproduces through the exact production path at the PIN; 3 it has a material
effect on output, state, evidence, determinism or integration behaviour, and hypothetical misuse or defence-in-depth does not
count by itself; 4 a concrete discriminator exists; 5 the fix lies inside this component's boundary):

| Finding | 1 | 2 | 3 | 4 | 5 | Blocks? |
|---|---|---|---|---|---|---|
| G1 residuals of the bound and the exclusions | no (a disclosed design choice; nothing lost against R0) | yes | no | yes | yes | no |
| G2 type-tag constructor errors print a value | no (outside F1b's YAMLError scope; no assignment shape) | yes | no (hypothetical: a tagged non-`sk-` inline key in an operator-set profile) | yes | yes | no |
| G3 new false positives | no | yes | no (0 in the evidence; fails closed) | yes | - | no |
| G4 the re-sign must edit `EXPECTED_PENDING` | no (the designed behaviour) | yes | no (a procedure step) | yes | yes | no |
| G5, G6 test gaps | no | n/a | no (tests only; the code is right, section 3) | yes | yes | no |
| G7 one stale parenthetical | partly (the prose rule) | n/a | no | yes | yes | no |

No CONTRACT-DEFECT (no falsified evidence, corrupted state or lost data) and no CONTRACT-INVALID.

**For the coordinator:**
1. G2 is the only finding whose fix touches an attested file. Doing it now means one more re-mint before the signature.
   Doing it with the issue #59 tooling batch costs no extra re-sign, since that batch already re-signs every accepted proof.
   My recommendation is to batch it.
2. G4 belongs in the re-sign handoff. The landing that adds the owner's `accepted-S0-04.tag` object and removes the PENDING
   line must set `EXPECTED_PENDING = set()` in the same commit.
3. G5 and G6 are test-only and need no re-mint. G7 is one word in STATUS.md.

