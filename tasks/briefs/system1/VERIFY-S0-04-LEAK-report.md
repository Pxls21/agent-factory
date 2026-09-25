# VERIFY-S0-04-LEAK report (task #287)

Lane: adversarial-verifier (sandbox, Opus 5.5). Started 2026-09-25T21:20:13Z (bucket 21:2xZ). Written incrementally.
Target: the commit whose subject starts "S0-04-LEAK landed (task #287" (local 1f764fe; called the PIN below).
Tree at start: HEAD = 9d66c6e (a wiki-only commit after the brief commit 7cdf08f); nothing under test changed after the PIN.
Scratch: `<scratch>/vs004/` (`<scratch>` = the session scratchpad); short basetemps under `/tmp/vs4/`.
Contract: `tasks/briefs/system1/S0-04-LEAK-brief.md` items 1-5, the lane report beside it, AF-AP-224.

## STATUS

DONE. **Gate: MERGE-READY-WITH-FOLLOWUPS** (section 10). Items 1-6 all run. The detectors meet contract item 1 (the `_` and `__` glued keys and the `<PREFIX>_API_KEY=` names caught through the real checker, no lost hit, the ordinary text passes). The re-mint reproduces: the ledger is byte-identical, and the result differs only in the two tool hashes and six volatile fields. Every anchor state gives the README's error or warning. Mutation: the lane's nine reproduce; 15 killed, 10 survived; the survivors are test-coverage gaps. Both sibling findings are confirmed. 15 findings (F1, F1b, F2-F14), none blocking. Settle F1/F1b (the capture guard; contract item 2 unmet as written) and F5 (STATUS.md stale) before the owner re-signs.

## 1. PREMISE, re-measured (21:2xZ, in the tree; every file under test is byte-identical to the PIN)

`git diff --stat 1f764fe HEAD` touches only the brief, `wiki/topics/live-state.md`, the env-tool-quirks skill copies and
`sandbox-kit/VENDORED-MANIFEST.md` (three coordinator commits after the PIN: 7cdf08f, 9d66c6e, 5dd79a9); no file under
test, no attested input, no ledger line. Tracked dirt at start: none.

| # | Premise line | Measured | Verdict |
|---|---|---|---|
| P1 | `git show --stat` of the PIN: 10 files, 621 insertions, 27 deletions | same 10 files, same counts | holds |
| P2 | `check-proof-status.py .`: the S0-04 PENDING WARNING, rc 0 | `proof-status: WARNING S0-04: ACCEPTED with the anchor PENDING the owner's signed tag accepted/S0-04 (declared in the ledger) — not owner-verifiable yet`, rc=0 | holds |
| P3 | `validate-ledger integrity` tail: blocked_host 0/1, conformance 3/3, execution_proof 9/9 | identical three lines, rc=0 | holds |
| P4 | `test_summary.sh --basetemp=<short> tests/test_s0_04_compression.py tests/test_proof_status.py`: 131 passed | `pytest-summary: 131 passed in 10.05s`, `pytest-exit: 0` (basetemp `/tmp/vs4/bt`); `2 files set=2fa20f3af1f3` (pc_suite.sh's `set_id` formula, run inline) | holds |
| P5 | the diff lines of the two tools and of test_proof_status.py | identical lines | holds |

Verdict: the premise holds; no CONTRACT-INVALID.

## 2. Item 1: the anchors, hostile shapes through the real CLIs (21:3xZ)

Harness `<scratch>/vs004/anchors.py` (scratch, not committed). Venue: `git archive` of the PIN (`proofs scripts tests/test_s0_04_compression.py tests/conftest.py`, 98 S0-04 tests green there) plus the parent's two tool files (`git show 1f764fe~1:...`). Per shape: a fresh copy of `fixtures/evidence-pass`, the text planted either as a new raw file `off/zz-note.txt` or as a new field of `off/request.json` written by the tests' own serializer (`json.dumps(indent=2, sort_keys=True)`, ensure_ascii); the REAL checker CLI run on it (`--fixtures-dir` the PIN's fixtures), new and old bytes. The capture tool: the REAL CLI, `--max-seq --record-dir <tmp>/absent/<text>` (`max_seq` raises `record dir not found: <path>`, `main`'s handler prints it through `safe()`). Every key or value is `secrets.token_hex(16)` at run time; the harness prints rc, the rule the checker names, withheld-or-printed, and whether the fake appears in the output, never an output text. Two full runs with fresh fakes gave identical verdicts (75 rows). A planted benign raw file passes (O10, O11, O13-O15, O18), so planting alone never fails a bundle; the reason line names the planted file (`failure_reason: credential-in-evidence: off/zz-note.txt matches sk-key`, rc=1).

**Contract shapes (item 1 and item 2):**

| Shape | Checker new / old | Capture new / old | Contract wants | Verdict |
|---|---|---|---|---|
| `x_`+key (S01), `mcp__srv__`+key (S02), `x_`+key inside a JSON string (S22) | sk-key / PASS | WITHHELD / PRINTED (S01, S02) | caught | met |
| `OMNIROUTE_API_KEY=`, lower, mixed case, spaces and quotes around `=` and `:`, a JSON pair raw and through the serializer, `export ...`, `DB_PASSWORD=`, `DB_PASSWD=`, `APP_SECRET=`, `GITHUB_TOKEN=`, `MY_APIKEY=`, `X_API-KEY=`, a URL query `?x_api_key=` (A01-A16, A26, A30) | key-assignment / PASS | PRINTED / PRINTED, the fake in stderr | checker: caught; capture: "refuses the same shapes" (item 2) | checker met; **capture NOT met** (finding F1) |
| key after `-` `.` `/` `:` `"` `'`, at file start, at line end, at EOF with no newline, after a real newline, after an escaped `\"` or `\\` in JSON, after a fullwidth low line (S03-S08, S13-S16, S20, S21, S27); `OMNIROUTE-API-KEY: `, `api_key=` at line start, `api_key : "v"` (A17, A28, A29) | caught / caught | WITHHELD / WITHHELD (sk); PRINTED / PRINTED (assignments) | no loss | met (the new anchor is a strict superset of `\b` on the left: any char `\b` accepts as non-word is outside `[A-Za-z0-9]`) |
| key glued after a digit, a lowercase or an uppercase ASCII letter (S10-S12); a digit or letter glued before the name (A18 `9API_KEY=`, A19 `MYAPI_KEY=`) | PASS / PASS | PRINTED / PRINTED | "still refuses a letter or digit before it" | met, by design (the residual the contract accepts; the capture prints such a key) |
| key after a non-ASCII letter `é` (S09), an Arabic-indic digit U+0663 (S25); `éAPI_KEY=` (A27) | caught / PASS | WITHHELD / PRINTED | silent (ASCII read) | wider than `\b`, protective (finding F7) |

**Ordinary text (item 2's list and more):** `task-`, `risk-`, `disk-`, `flask-`, `ask-` + hex; `x-api-key-id: <hex>`; `/run/secrets/OMNIROUTE_API_KEY_FILE`; `nextPageToken: <hex>`; `max_tokens: 12345678`; `key_env: OMNIROUTE_API_KEY`; `DB_PASSWORD_FILE=/run/secrets/db`; `api_key_env=OMNIROUTE_API_KEY`; `x-api-key: <redacted>`; the compression header value: PASS under both checkers (O01-O08, O10, O11, O13-O15, O18). NEW false positives (fail closed, the checker names the rule): `next_page_token: <hex>` (O09) and the code line `_CHMOD_SYM_TOKEN = re.compile(...)` (O12): any snake_case name ending in a listed word with an 8+ character value (finding F6, disclosed by the lane). Pre-existing false positives under both: prose `the password: forgotten again` (O16), `task-sk-runner-bootstrap` (O17).

**Gaps of the same class that the anchor does not reach (both checkers PASS; pre-existing, not regressions):**
- A key after a JSON escape: `\n`+key and `\t`+key inside a JSON string (S17, S18), `é`+key written by `ensure_ascii` as `\u00e9` (S19), `api_key=<v>` after an escaped newline (A25), JSON-in-JSON `{\"api_key\": \"<v>\"}` raw and through the serializer (A23, A24). The screen reads the RAW file text, so the character before the key is the escape's last letter or hex digit (finding F2).
- URL-encoded contexts: `%5F`+key, `%20`+key (S23, S24) (finding F2).
- The name's RIGHT side: `SECRET_KEY=<v>`, `AWS_SECRET_ACCESS_KEY=<v>`, `OMNIROUTE_API_KEY_2=<v>` (A20-A22): the trailing `\b` and the closed name list (finding F3).
- Case: `SK-<hex>` passes the checker (its `sk-key` rule has no `(?i)`) but the capture guard withholds it (`LEAK_RE`'s leading `(?i)` covers both alternatives) (S26; finding F8).
- The capture CLI's argparse errors print outside `main`'s `try`: `--after-seq x_sk-<fake>` exits 2 with the fake in stderr (`invalid int value: 'x_sk-<hex32>'`), `safe()` never runs (finding F9).

## 3. Item 2: the re-mint, reproduced from a git archive of the PIN (21:3xZ)

Venue: `<scratch>/vs004/remint` = `git archive 1f764fe proofs scripts` (the whole attested closure; no `.git`). Commands and output:
```
# controls first
$ python3 scripts/validate-ledger integrity --root .            (the archive as committed)
  12 PRESENT; blocked_host 0/1, conformance_checked_decision 3/3, execution_proof 9/9; rc=0
$ python3 scripts/ledger-gen --root . --output <scratch>/ledger0.json ; cmp with the PIN's proofs/ledger.json
  rc=0, byte-identical
# negative control: the PARENT's result.json beside the PIN's tools
$ python3 scripts/validate-ledger integrity --root .
  S0-04 INVALID; attestation-mismatch: S0-04 proofs/S0-04/check_compression.py; execution_proof numerator=8 denominator=9; rc=1
# the re-mint (PIN result restored first), 2026-09-25T21:32:04Z
$ python3 scripts/proof-runner run --proof S0-04 --venue sandbox --root .            -> rc=0
$ python3 scripts/validate-ledger integrity --root .                                 -> 12 PRESENT, execution_proof 9/9, rc=0
$ python3 scripts/ledger-gen --root . --output <scratch>/ledger2.json ; cmp with the PIN's proofs/ledger.json
  rc=0, byte-identical (normalized_digest 5b49bfb5cb33a1ea...)
```

**`proofs/S0-04/result.json`, field by field** (`<scratch>/vs004/fielddiff.py`, every leaf):

| Pair | Leaves | Identical | Changed |
|---|---|---|---|
| parent (1f764fe~1) -> PIN (committed) | 71 | 63 | 8: `attestation["proofs/S0-04/check_compression.py"]` fa39bb78... -> 881710af..., `attestation["proofs/S0-04/tools/pc/capture_leg.py"]` 1d4234c1... -> 7b202db0..., `digest`, `recorded_at`, `runs[0..1].started_at/finished_at` |
| PIN (committed) -> my re-mint | 71 | 65 | 6: `digest`, `recorded_at`, the four run timestamps (all volatile) |

- The two changed hashes are the files' real sha256 at the PIN (`git show 1f764fe:<file> | sha256sum`: 881710af6818ee0d, 7b202db013aa597a; at the parent: fa39bb78c7d589cc, 1d4234c1b39ca859). All 44 attestation entries equal the sha256 of the PIN archive's bytes (0 mismatches).
- `digest` is `canonical_digest(runs)` and the runs carry the timestamps: it moves between my re-mint and the committed one with no attestation or output change, so it is volatile by construction; `proofs/normalization.yaml` strips it with `recorded_at`, `env_fingerprint` and the run timestamps.
- Both legs' `exit_code` (0, 1), `stdout_sha256` (9166513f18cb..., caf92711fbc2...), `stderr_sha256` and the negative leg's `failure_reason: off: compression-header-missing` are identical across all three results: PASS for the same three assertions.
- The ledger line follows from the two hashes alone (ledger-gen's own `_normalized_digest` and the committed normalization): my re-mint -> 5b49bfb5cb33a1ea (the committed PIN value); my re-mint with the parent's two hashes put back -> 74fd294ad3ad8ee3 (the parent's ledger value, exactly). `proofs/ledger.json` parent -> PIN: one line removed, one added (S0-04's `normalized_digest`).

**The capture question (the lane's section 7), re-derived:** `ast` of the parent and PIN `capture_leg.py`: 1,917 nodes each, the only differing node the `LEAK_RE` string constant at :46; `LEAK_RE` is read only in `safe()` (:54); `safe()` is called only in `main`'s two `except` handlers (:304, :307), which print to stderr; `run_s0_04_legs.sh` never records the tool's stderr in the evidence (it branches on exit codes). So no evidence byte depends on the change and attesting the new bytes over the old evidence is honest. I agree: no new PC capture is needed.

Verdict item 2 (contract item 3): **met, reproduced.**

## 4. Item 3: the anchor state, every neighbouring state in a scratch clone (21:3xZ)

Venue: `git clone --local --no-checkout` of this repo into `<scratch>/vs004/clone` (objects hardlinked), sparse checkout of `proofs/ scripts/ todo/ docs/governance/ tests/test_proof_status.py tests/conftest.py`, detached at the PIN. The checker is the clone's own `scripts/check-proof-status.py` (the PIN's bytes), run on the clone root. Script: `<scratch>/vs004/states.sh`. The old owner-signed tag object is recovered from history (`git show 1f764fe~1:docs/governance/tags/accepted-S0-04.tag`, object 1ec6cd4a, on fa20942). For the "new tag" states a throwaway ed25519 key (GNUPGHOME `/tmp/vs4/g1`) signs the tag and its public half is APPENDED to the clone's `owner-signing-key.asc`, so the owner's eleven real tags still verify (a scratch-only substitution: I cannot sign with the owner's key). Where origin stands: `git ls-remote origin` advertises no tag at all, and the GitHub API (`list_tags`, read-only) returns `[]`, so CI (`fetch-tags: true`) sees no `accepted/*` ref and verifies through the committed tag files only (T2 models it).

| State | Checker output (verbatim, the old tag id masked) | rc | README's words | Verdict |
|---|---|---|---|---|
| T1 (b) as committed: no tag file, no ref, PENDING line | `WARNING S0-04: ACCEPTED with the anchor PENDING the owner's signed tag accepted/S0-04 (declared in the ledger) — not owner-verifiable yet` | 0 | "reported as a WARNING and never counts as verified" | as described |
| T2 (b) as CI sees it: every `accepted/*` ref deleted, the eleven committed tag files imported | the same WARNING only | 0 | the committed-object path | as described; CI stays green on this checker |
| T3 neither: no tag, no PENDING line | ``S0-04: ACCEPTED but no signed tag accepted/S0-04 and no visible `PROOF-ANCHOR: S0-04 = PENDING-OWNER-TAG` declaration — an acceptance the owner cannot verify (AF-AP-32)`` | 1 | refused | as described |
| T4 the OLD tag as a ref + PENDING | `the tag accepted/S0-04 exists but the ledger still declares PROOF-ANCHOR PENDING — a stale declaration (remove it)` and `the minted proofs/S0-04/result.json changed since accepted/S0-04 (regenerated after acceptance) — re-accept with a new signed tag (AF-AP-56)` | 1 | "a tag and a pending declaration together are a stale ledger and an error"; item 4 | as described |
| T5 the OLD tag as a ref, no PENDING (a tag on a commit whose result differs) | the `changed since` error only | 1 | item 4, "must be re-accepted" | as described |
| T6 the OLD tag as a committed file, no ref, + PENDING | stale declaration + changed since (naming the imported object id) | 1 | both | as described |
| T7 the OLD tag file, no ref, no PENDING (the landing without step (b), in CI) | changed since | 1 | item 4 | as described |
| T8 a NEW signed tag on the PIN, no PENDING (after the re-sign) | (nothing) | 0 | "expect rc 0 and no WARNING once the declaration is removed" | as described |
| T9 a NEW signed tag on the PIN + PENDING (declaration left behind) | stale declaration only | 1 | stale ledger, an error | as described |
| T10 a NEW signed tag on the PARENT commit (its result differs), no PENDING | changed since | 1 | item 4 | as described |
| T11 a NEW tag by a key NOT in the committed key file | `the signature on accepted/S0-04 does not verify against the committed owner key docs/governance/owner-signing-key.asc (AF-AP-32): ... No public key` | 1 | item 2 | as described |
| T12 the NEW tag as a committed-object file only (CI after the re-sign) | (nothing) | 0 | "the checker imports and verifies it whenever the ref is absent" | as described |
| T13 a LIGHTWEIGHT tag on the PIN | ``accepted/S0-04 is a lightweight tag — the anchor must be a SIGNED annotated tag (`git tag -s`)`` | 1 | item 1 | as described |

The clone ended reset (0 changed paths, the eleven real refs restored, no S0-04 ref).

Verdict item 3 (contract item 4 and the landing's state (b)): **met.** State (b) is the only neighbouring state with rc 0 short of a valid new signature; it warns and is never counted verified.

## 5. Item 4: the narrowed test in `tests/test_proof_status.py` (21:3xZ)

Same clone. `tests/test_proof_status_prenarrow.py` = the parent's file (`git show 1f764fe~1:tests/test_proof_status.py`; the one-line difference is the assertion at :477). Both run with `-k committed` (the three committed-state tests plus four fixture tests whose names contain "committed"), short basetemp. Driver `<scratch>/vs004/states2.sh`.

| State | Checker | Narrowed file (the PIN's) | Pre-narrowing file |
|---|---|---|---|
| T1 (b) as committed | S0-04 WARNING, rc 0 | 7 passed | 1 failed: `test_committed_tree_anchor_state_is_the_declared_pending_one` (so the narrowing was needed for (b)) |
| T3 neither (an accepted proof with no anchor, no declaration) | rc 1 | 3 failed: `test_the_committed_tasklist_passes`, `test_committed_state_passes_status_and_ledger`, `test_committed_tree_anchor_state_is_the_declared_pending_one` | the same 3 failed |
| T5 the old tag, no PENDING | rc 1 | the same 3 failed | the same 3 failed |
| T8 a new signed tag, no PENDING | rc 0, no WARNING | 7 passed | 7 passed |
| M-B S0-05 loses its ref and tag file, NO declaration | `S0-05: ACCEPTED but no signed tag ... (AF-AP-32)`, rc 1 | the same 3 failed | the same 3 failed |
| **M-A S0-05 (verified) downgraded: ref and tag file removed, a PENDING line declared** | WARNING S0-04 and WARNING S0-05, rc 0 | **7 passed** | 1 failed (the anchor-state test) |
| M-C S0-11 downgraded the same way | WARNING S0-04 and WARNING S0-11, rc 0 | 7 passed | 7 passed (the test's else-branch expects exactly this pre-signing state) |

- An accepted proof with no anchor and no declaration is still caught, by two tests (rc 0 asserted) and by `scripts/verify-planning-repo.sh:71` (`|| exit 1`, run by `planning-checks.yml` and `stage0-ci.yml`).
- An UNDECLARED warning cannot exist: `_anchor_findings` appends a warning only inside `if pending:` (`scripts/check-proof-status.py`, the `if not ref_exists:` block); a missing anchor without a declaration is an error (M-B).
- **The gap (finding F4):** after the narrowing no guard notices a DECLARED downgrade of a verified proof other than S0-04 (M-A: every guard green, only a WARNING line on stderr that nothing asserts). The old assertion was stricter than its docstring and was the only tripwire for that; nothing else reads the WARNING lines (the only callers of the checker are this test file and `verify-planning-repo.sh`, which tests the exit code). The declaration is visible in the ledger by design (AF-AP-32: "the coordinator can write the declaration; it cannot write the signature"), so this is a weakened tripwire, not a broken invariant. Option: assert the set of warned proofs is a subset of an explicit allowlist, e.g. `set(re.findall(r"WARNING (S0-\d\d):", completed.stderr)) <= {"S0-04"}`; it stays green after the owner re-signs (the empty set) and reds on the next unplanned downgrade.

## 6. Item 5: red-green and mutation (21:4xZ)

**Red run (technique 3).** `<scratch>/vs004/mut` (a copy of the PIN archive) with the two tools replaced by the parent's bytes (`cmp` against `git show 1f764fe~1:...`), the PIN's tests kept:
```
FAILED ...::test_a_key_glued_after_an_underscore_fails_the_checker[x_]
FAILED ...::test_a_key_glued_after_an_underscore_fails_the_checker[mcp__srv__]
FAILED ...::test_a_prefixed_api_key_assignment_fails_the_checker[OMNIROUTE]
FAILED ...::test_a_prefixed_api_key_assignment_fails_the_checker[OPENAI]
FAILED ...::test_a_prefixed_api_key_assignment_fails_the_checker[HERMES_PROVIDER]
FAILED ...::test_capture_leg_withholds_a_key_glued_after_an_underscore[x_]
FAILED ...::test_capture_leg_withholds_a_key_glued_after_an_underscore[mcp__srv__]
7 failed, 91 passed in 4.59s
```
The five checker cases fail at `assert code == 1` (the parent's checker printed its observations and PASSed over the planted leak); the two capture cases at the stderr assertion (`capture_leg: record dir not found: .../absent/x_sk-<hex32>`, the fake printed). The lane's red run reproduced exactly; the 12 ordinary-text cases cannot red on the parent (it takes no ordinary text), as the lane disclosed (its D5).

**Mutation** (`<scratch>/vs004/mutate.py`, AF-AP-223 rules: the unmutated CONTROL first and green, each mutant's anchor text found exactly once, the file restored and re-hashed after every run, KILLED only on a named FAILED test with no ERROR, a collection change or error-only run INVALID; basetemp parent recreated per run):
```
CONTROL (unmutated): rc=0 98 passed in 4.83s
M1  checker sk-key anchor back to \b                       KILLED  test_a_key_glued_after_an_underscore_fails_the_checker[mcp__srv__], [x_]
M2  checker key-assignment name anchor back to \b          KILLED  test_a_prefixed_api_key_assignment_fails_the_checker[HERMES_PROVIDER], [OMNIROUTE], [OPENAI]
M3  capture sk anchor back to \b                           KILLED  test_capture_leg_withholds_a_key_glued_after_an_underscore[mcp__srv__], [x_]
M4  checker sk-key no anchor                               KILLED  test_ordinary_text_passes_the_checker[stray_note-disk-{}], [..risk..], [..task..]
M5  checker key-assignment no anchor                       KILLED  test_ordinary_text_passes_the_checker[nextPageToken-{}]
M6  capture sk no anchor                                   KILLED  test_capture_leg_passes_ordinary_text_through[stray_note-disk-{}], [..risk..], [..task..]
M7  checker sk-key lets a digit glue                       SURVIVED (98 passed)
M8  checker key-assignment lets a digit glue               SURVIVED (98 passed)
M9  capture sk lets a digit glue                           SURVIVED (98 passed)
M10 checker sk-key refuses _ again (ASCII \w)              KILLED  the two glued checker cases
M11 checker key-assignment refuses _ again                 KILLED  the three prefixed-assignment cases
M12 capture sk refuses _ again                             KILLED  the two glued capture cases
M13 checker sk-key lets an UPPERCASE letter glue           SURVIVED (98 passed)
M14 capture sk lets an UPPERCASE letter glue               SURVIVED (98 passed)
M15 checker sk-key lets a lowercase letter glue            KILLED  the task-/risk-/disk- checker cases
M16 checker key-assignment loses (?i)                      KILLED  the three prefixed-assignment cases
M17 checker key-assignment name list neutered              KILLED  the three prefixed cases + test_inline_api_key_in_the_config_leg_is_a_credential_finding
M18 checker sk-key neutered (length floor 800)             KILLED  the two glued checker cases
M19 capture safe() never withholds (guard unwired)         KILLED  test_capture_leg_error_messages_never_echo_a_credential + the two glued capture cases
M20 checker screen unwired (_screen_tree not called)       KILLED  13 failed (the new leak cases, test_a_second_hex64_still_fails, +7)
M21 checker sk-key anchor as (?<![^\W_]) (Unicode refuses) SURVIVED (98 passed)
M22 capture sk case-sensitive ((?i) scoped to bearer)      SURVIVED (98 passed)
M23 checker sk-key refuses a hyphen before                 SURVIVED (98 passed)
M24 checker key-assignment refuses a hyphen before         SURVIVED (98 passed)
M25 capture sk refuses a slash before                      SURVIVED (98 passed)
TOTAL {'KILLED': 15, 'SURVIVED': 10, 'INVALID': 0}; files restored: True
```
- The lane's M1-M9 reproduce exactly (six killed by the same named tests, three survive). Every mutant on the contract's required behaviour (accept `_`, keep refusing lowercase letters, the flags, the wiring) is killed.
- Survivors, classified: M7-M9 and M13-M14: the contract's "still refuses a letter or digit" is pinned for lowercase letters only (no test has a digit or an uppercase letter before `sk-` or a key name); M21: equivalent on ASCII input (the S1 vs S1u choice is unpinned); M22: the capture guard's case-insensitive `sk-` is unpinned (see F8); **M23-M25: the NO-LOSS direction is unpinned**: a later edit that stops catching a key after `-` or `/` (which `\b` caught and the new anchor catches) stays green. All are test-coverage gaps beyond contract item 2's list (finding F10); none changes the landed behaviour, which section 2 measured directly.

## 7. Item 6: the lane's sibling findings, through the real code (21:4xZ)

**S0-01's `_STDERR_LEAK_RE` (a signed proof): CONFIRMED.** Driver `<scratch>/vs004/s001.py` imports the PIN's `proofs/S0-01/check_acp_conformance.py` and calls its real `check_negative()` on a scratch copy of the committed negative leg (`proofs/S0-01/evidence/golden/negative`), with one fake line appended to `agent-stderr.txt`:
```
control (committed negative leg, unmodified): PASS        control (an ordinary appended line): PASS
bare sk- key -> PASS          sk- key glued after _ -> PASS        OMNIROUTE_API_KEY=<v> -> PASS
password=<v> -> PASS          api_key: <v> -> PASS                  token = <v> (spaces) -> PASS
"token": "<v>" (JSON) -> PASS MY_TOKEN=<v> -> FAIL: secret-shaped   Authorization: Bearer <v> -> FAIL: secret-shaped
a 64-hex run -> FAIL: secret-shaped
```
Exactly the lane's table: the screen has no `sk-` rule and no key-name rule beyond `token[=:]\S` (finding F11).

**The capture guard's missing key-assignment rule: CONFIRMED, and one case is wider than the lane said.** Section 2's harness already shows every `<PREFIX>_API_KEY=<v>` shape printed through the real CLI's `CaptureError` handler. The realistic path is `--config`: driver `<scratch>/vs004/x1.py` writes a fake Hermes profile whose `api_key` line is malformed and runs the REAL CLI (`--config --profile <file> --out <dir>`, PyYAML 6.0.1), PIN and parent tools, fresh fake values; it prints only booleans and lengths:

| YAML error on the `api_key` line | hex32 value | `sk-`+hex32 value | hex64 value | PIN = parent? |
|---|---|---|---|---|
| unclosed double quote | printed: the name and all 32 chars | WITHHELD | printed: 31 chars | yes |
| tab indent | printed: the name and a 22-char prefix | WITHHELD | printed: 22 chars | yes |
| a colon after the value (`api_key: <v>: x`) | printed: all 32 chars, no name | **printed: 32 of 35 chars** (PyYAML's snippet window starts inside the value, so the `sk-` prefix is cut and no rule sees a key) | printed: 32 chars | yes |
| error on ANOTHER line | printed, no value | printed, no value | - | yes |

The lane wrote that "a non-`sk-` key in any of these reaches the PC's stderr"; the third row leaks the tail of an `sk-` key too, under the old and the new guard alike (finding F1b). The OmniRoute key is `sk-`-shaped (`docs/INCIDENT-LOG.md:296`: after its echo, "an `sk-…` rule added if absent"). Exposure: the runner's default profile is the proof-owned `proofs/S0-04/hermes/config.yaml` (`run_s0_04_legs.sh:36`), which holds no inline key (its key names: `api`, `name`, `key_env`, `default_model`, `transport`, `discover_models`, `extra_headers`); a live profile with an inline key is read only when an operator sets `HERMES_PROFILE`. The checker's key-assignment rule appended to `LEAK_RE` (the lane's option) would withhold rows 1 and 2 for a non-`sk-` value and never row 3; a `yaml.YAMLError` re-raised as `CaptureError` with its line and column only (no snippet) would withhold all three whatever the key shape.

**Also measured here (not asked):** the screen never decodes `body_b64`: a fake `sk-` key inside a base64 response body passes the real checker (`PASS`, rc 0; part of finding F2). The committed evidence and every fixture, screened DECODED (every JSON string and every base64 body) with both tools' rules: 0 bearer, 0 sk-key, 0 key-assignment, 0 capture hits; the only hex64 hit per upstream record is its own `authorization_fingerprint` (8 of 8 records), which the checker masks by design. No present leak hides in the blind spots.

## 8. Other checks (21:4xZ)

- **Static gates on the landed files (in the tree):** `python3 -m pyflakes` on both tools, `tests/test_s0_04_compression.py` and `tests/test_proof_status.py`: rc 0. `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: 0 for both tools, both test files, `result.json`, `proofs/ledger.json`, the ledger. `scripts/ap_screen.py` on the four files: no AF-AP-224 hit; the AF-AP-39 hit at `tests/test_s0_04_compression.py:258` is the lane's disclosed false positive (`_with_note` writes the fake assignment into the bundle's JSON; argv carries only the bundle path; read here); the others (AP-1 x2 at capture_leg.py:60, AF-AP-110, AF-AP-132, AF-AP-70, AP-32) are on lines the diff did not touch.
- **CI paths:** `bash scripts/verify-planning-repo.sh` (the planning-checks job): `planning repository verification passed`, rc 0, with the S0-04 WARNING. No test, script or proof outside `check-proof-status.py` and its test reads `docs/governance/tags/` or `PROOF-ANCHOR` (`git grep` at the PIN), so removing the S0-04 tag file breaks no other consumer. `stage0-ci.yml` fetches tags, and origin holds none (section 4), so CI takes the committed-file path (T2: rc 0).
- **Reachability:** the new rules are live on the entry points: `check_compression.py main -> check_bundle -> _screen_tree -> _leak_hit -> LEAK_PATTERNS` (M20 unwires the screen: 13 tests fail) and `capture_leg.py main -> except -> safe -> LEAK_RE` (M19: 3 fail). `_redact` also reads `_leak_hit`, and the positive leg's `stdout_sha256` is unchanged by the re-mint, so no observation line became withheld.
- **The superset property, from the regex semantics:** the old left anchor `\b` (before a word character) holds when the previous character is a non-word character or absent; `(?<![A-Za-z0-9])` holds when it is not an ASCII letter or digit or absent; ASCII letters and digits are word characters (also under `(?i)`, whose four extra case-fold letters are word characters too), so every old match is a new match: 0 lost hits is structural, not only measured.
- **Performance (finding F13):** the key-assignment rule backtracks quadratically on whitespace after a name. Regex alone: 2,000/4,000/8,000/16,000 spaces after ` token` take 0.024/0.095/0.393/1.693 s (old and new alike); after `x_token` the same for the new rule and 0.000 s for the old. Through the real checker CLI with 32,000 spaces planted in a bundle file: ` token` 6.3 s (new) and 6.4 s (old); `x_token` 6.4 s (new) and 0.0 s (old); all PASS. At the 8 MiB file cap the run would take days; the proof-runner's 120 s leg timeout bounds the mint, the bare CLI has no timeout.
- **Ledger hygiene (finding F14):** the landing's ledger entry ends in a literal, unfilled DATESTAMP token in braces (13 such tokens in `todo/BUILD-TASKLIST.md` at the PIN, 12 at its parent); `scripts/stamp_fill.py` says "nothing calls it automatically".
- **The tree:** no tracked file touched (`git status --porcelain --untracked-files=no` empty); scratch deleted as I went.

## 9. FINDING INVENTORY (no severity filter)

Evidence levels: VERIFIED = reproduced here through the named path; STATIC = read from source; UNVERIFIED = not reproduced.

| # | Class | Finding | Evidence | Contract mapping | Canonical path | Material effect | Reproduction | Suggested fix |
|---|---|---|---|---|---|---|---|---|
| F1 | FOLLOW-UP (a CONTRACT DEVIATION: declared by the lane as X1 and in the landing as "Not done", never amended) | The capture guard does not refuse `<PREFIX>_API_KEY=<value>` in an exception message; contract item 2 says "the capture tool's guard refuses the same shapes in an exception message" | VERIFIED (section 2 rows A01-A16, A26, A30: PRINTED with the fake in stderr, PIN and parent; section 7 rows 1-2 through `--config`) | S0-04-LEAK brief item 2 | yes: the real CLI, `main`'s `CaptureError` handler | only a NON-`sk-` inline key in a profile the operator points `HERMES_PROFILE` at, on a malformed line; the OmniRoute `sk-` key is already withheld in those cases; the default profile holds no key | `capture_leg.py --max-seq --record-dir <tmp>/absent/OMNIROUTE_API_KEY=<fake>` -> rc 1, the fake in stderr; `<scratch>/vs004/x1.py` | before the owner signs: either amend item 2 on record, or append the checker's key-assignment rule to `LEAK_RE` with a CLI test (a non-`sk-` value reds on the PIN) and re-mint; the F1b fix covers more |
| F1b | FOLLOW-UP (new; pre-existing) | A YAML "mapping values" error on the `api_key` line (`api_key: <v>: x`) prints 32 of 35 chars of an `sk-` key, under the old and the new guard: PyYAML's snippet (`Mark.get_snippet`, 75 chars, head cut at 36) starts inside the value, so the `sk-` prefix is gone and no shape rule can see it | VERIFIED (section 7 row 3; the snippet code read) | none (not a contract shape) | yes: the real CLI `--config` | as F1 (non-default profile, malformed line), but it hits the real key shape | `<scratch>/vs004/x1.py` | `do_config`: catch `yaml.YAMLError`, raise `CaptureError` with the mark's line and column only; take it with F1 in the same re-mint |
| F2 | FOLLOW-UP (pre-existing; AF-AP-224's class) | The screen reads raw file text: a key after a JSON escape (`\n`, `\t`, `\u00e9`), JSON-in-JSON escaped quotes, `api_key=` after an escaped newline, URL-encoded contexts (`%5F`, `%20`) and anything inside a base64 `body_b64` pass, before and after the fix | VERIFIED (section 2 S17-S19, S23-S24, A23-A25; section 7 base64 probe) | none (the contract scopes the left anchor; its "refuses a letter" makes `\nsk-` refused by definition) | yes: the real checker CLI | none today: the committed evidence and fixtures, screened decoded, hold 0 hits | `<scratch>/vs004/anchors.py` | also run `LEAK_PATTERNS` over every decoded JSON string and every decoded `body_b64` (fingerprint masked as now) |
| F3 | FOLLOW-UP (pre-existing) | The name's RIGHT side: `SECRET_KEY=<v>`, `AWS_SECRET_ACCESS_KEY=<v>`, `OMNIROUTE_API_KEY_2=<v>` pass (the trailing `\b` and the closed name list) | VERIFIED (A20-A22) | none (task #292 covers the scrubber's key rules, not this name side) | yes | none today | as F2 | widen the name side on the right (for example `(?:_[A-Za-z0-9]+)*` before the separator), measured for false positives like SCRUB1's first: the naive form also takes key-name references such as `api_key_env=OMNIROUTE_API_KEY` and `DB_PASSWORD_FILE=/run/secrets/db` (O13, O14 pass today) |
| F4 | FOLLOW-UP | After the narrowing, a DECLARED downgrade of a verified proof other than S0-04 passes every guard (M-A); the old assertion was the only tripwire; an undeclared loss is still an error (M-B, T3) | VERIFIED (section 5) | none (AF-AP-32 allows a declared PENDING state) | yes: the committed-state tests on a scratch clone | a weakened tripwire, no false state | `<scratch>/vs004/states2.sh` M-A | `assert set(re.findall(r"WARNING (S0-\d\d):", completed.stderr)) <= {"S0-04"}` |
| F5 | FOLLOW-UP (stale owner-facing prose the landing falsified; fix before the owner reads it) | `STATUS.md:3`, `:10`, `:70` still say all twelve proofs are ACCEPTED by the owner's GPG-signed tags and cite `docs/governance/tags/accepted-S0-04.tag` on fa20942; the landing deleted that file and the checker reports S0-04 "not owner-verifiable yet". The wiki live-state (9d66c6e) is right | VERIFIED (`git show 1f764fe:STATUS.md`, `git show 1f764fe:docs/governance/tags/accepted-S0-04.tag` absent) | CLAUDE.md #1 rule, prose clause (a status doc that flatters the system) | n/a (a document) | not this increment's required evidence (STATUS.md says the ledger wins, and the ledger is right) | `grep -n accepted-S0-04.tag STATUS.md` -> :70 | edit the S0-04 row and the two headline lines to "re-minted 2026-09-25, anchor PENDING the owner's re-sign" |
| F6 | INFO (disclosed by the lane) | New fail-closed false positives: `next_page_token: <hex>`, `_CHMOD_SYM_TOKEN = re.compile(...)` | VERIFIED (O09, O12) | contract item 1 accepts the cost (0 on S0-04's corpora) | yes | a future capture holding such a field fails loudly, naming the rule | as F2 | none now; recheck at the next capture |
| F7 | INFO | The anchor also takes a key after a non-ASCII letter or digit (`é`, U+0663); the new comment's "a letter or digit before still refuses" holds for ASCII only | VERIFIED (S09, S25, A27) | contract item 1 read as ASCII | yes | protective | as F2 | say "an ASCII letter or digit" in the comment |
| F8 | INFO (pre-existing) | Case: the checker's `sk-key` is case-sensitive, the capture's `LEAK_RE` is not (its leading `(?i)` covers both alternatives): `SK-<hex>` passes the checker and is withheld by the capture | VERIFIED (S26); unpinned (M22) | none | yes | none (`SK-` is not a key shape) | as F2 | pick one and pin it |
| F9 | INFO | `parse_args` runs outside `main`'s `try`, so an argparse error echoes argv unscreened: `--after-seq x_sk-<fake>` -> rc 2, the fake in stderr | VERIFIED | none | yes | operator misuse only (the key never goes in argv by design) | section 2 | move `parse_args` inside the `try`, or subclass the parser's `error` to pass through `safe()` |
| F10 | FOLLOW-UP (test coverage beyond item 2's list) | Mutants survive: digit or uppercase glue allowed (M7-M9, M13-M14), the Unicode variant (M21), the capture's case (M22), and the NO-LOSS direction: refusing a key after `-` or `/` (M23-M25) | VERIFIED (section 6) | none | n/a | none today | `<scratch>/vs004/mutate.py` | add `9`+key and `X`+key (must pass), `-`+key and `/`+key (must fail) through both CLIs |
| F11 | FOLLOW-UP (sibling; the signed proof S0-01; the lane's finding, confirmed) | `_STDERR_LEAK_RE` misses bare and glued `sk-` keys, `OMNIROUTE_API_KEY=`, `password=`, `api_key:`, `token = `, JSON `"token":` | VERIFIED (section 7, the real `check_negative`) | S0-04-LEAK item 5 (report, do not fix) | yes | a leak in a future negative leg's stderr would pass | `<scratch>/vs004/s001.py` | a task of its own (a fix re-mints S0-01 and needs the owner's re-sign); not registered in the ledger yet |
| F12 | INFO | Report accuracy: "19 new test cases (6 functions)": the diff adds 5 test functions (19 cases) and 2 helpers; "red on the PIN" holds for the 7 leak cases only (the lane's own D5) | STATIC | none | n/a | none (no required evidence false) | `git show 1f764fe -- tests/test_s0_04_compression.py` | none |
| F13 | FOLLOW-UP (pre-existing; the new anchor widens its triggers) | Quadratic backtracking in the key-assignment rule's `\s*["']?\s*[:=]` on long whitespace | VERIFIED (section 8) | none | yes: the real CLI | a hostile bundle can stall the bare CLI; the mint path is bounded by the 120 s leg timeout | section 8 | `\s*(?:["']\s*)?[:=]` (linear), or a possessive `\s*+` |
| F14 | INFO | The landing's ledger entry carries a literal, unfilled DATESTAMP token in braces | VERIFIED | CLAUDE.md stamp rule (a missing stamp, not a wrong one) | n/a | none | `git show 1f764fe:todo/BUILD-TASKLIST.md \| grep -c 'DATESTAMP}'` -> 13 | `python3 scripts/stamp_fill.py todo/BUILD-TASKLIST.md` before the next commit |

**Citations (path:line at the PIN; each line quotes a token of the cited line):**
- `proofs/S0-04/check_compression.py:85`: the new `"sk-key"` rule, `(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{8,}` (section 2).
- `proofs/S0-04/check_compression.py:87`: the key-assignment name side, `(?i)(?<![A-Za-z0-9])(?:api[_-]?key|apikey|secret|password|passwd|token)\b` (F3: the trailing `\b`).
- `proofs/S0-04/check_compression.py:88`: the separator `\s*[\"']?\s*[:=]` that backtracks quadratically (F13).
- `proofs/S0-04/tools/pc/capture_leg.py:46`: `LEAK_RE`, its leading `(?i)` covering both alternatives (F8) and no key-assignment alternative (F1).
- `proofs/S0-04/tools/pc/capture_leg.py:275`: `args = parser.parse_args(argv[1:])`, outside the `try` (F9).
- `proofs/S0-04/tools/pc/capture_leg.py:303`: `except CaptureError as error:`, the handler every capture probe went through (F1).
- `proofs/S0-04/tools/pc/run_s0_04_legs.sh:36`: `PROFILE="${HERMES_PROFILE:-$PROOF_DIR/hermes/config.yaml}"`, the default profile with no inline key (F1, F1b exposure).
- `scripts/check-proof-status.py:126`: `if pending:`, the only place a WARNING is appended (section 5: no undeclared warning).
- `scripts/check-proof-status.py:178`: the `changed since` error of T4-T7 and T10.
- `tests/test_proof_status.py:477`: `assert "WARNING S0-11" not in completed.stderr`, the narrowed assertion (F4).
- `STATUS.md:70`: the S0-04 row still citing `docs/governance/tags/accepted-S0-04.tag` (F5); `STATUS.md:3` and `STATUS.md:10`: "all twelve" proofs ACCEPTED by signed tags (F5).
- `scripts/verify-planning-repo.sh:71`: `python3 "${repo_root}/scripts/check-proof-status.py" "${repo_root}" || exit 1`, the planning-checks consumer (section 8).
- `docs/INCIDENT-LOG.md:296`: the OmniRoute key echo, "an `sk-…` rule added if absent" (the key shape behind F1b).

**Verified and holding (for the record):** item 1's contract shapes caught through the checker (the capture half except F1), no lost hit, ordinary text passes (section 2); the re-mint reproduced byte for byte in the ledger and field by field in the result, the capture answer re-derived (section 3); every anchor state behaves as the governance README says (section 4); the narrowed test still catches an accepted proof with no anchor (section 5); the lane's red run and six required mutants reproduce, plus nine more kills (section 6); both sibling findings confirmed (section 7); the premise and the gate count (`pytest-summary: 131 passed in 10.05s`, `2 files set=2fa20f3af1f3`).

**Reproduced vs reviewed statically:** every row above marked VERIFIED ran here; F12 and the snippet mechanism of F1b were also read from source. **Deliberately skipped:** anything on the PC (no bridge by rule; the brief's capture question needs none, section 3); the full `tests/` suite (the change class is two regexes, one assertion, a ledger line and a tag file; I ran the two named files, the planning-checks script, and swept for other consumers of the tag files: none); the lane's own measurement instrument and bystander table (its scratch is gone; my harness measured S0-04's evidence and fixtures directly, raw and decoded); NaN/inf inputs (no numeric input in the changed code).

## 10. GATE RECOMMENDATION (21:5xZ)

**MERGE-READY-WITH-FOLLOWUPS** — no finding meets the whole blocking predicate; every load-bearing claim was reproduced here (nothing on the recommendation rests on an unreproduced step). One judgement call is named below (F1, condition 3).

**The blocking predicate applied** (a finding blocks only if ALL five hold: 1 contract mapping to a criterion frozen before dispatch or an explicit repository-wide invariant; 2 canonical reproduction through the exact production path at the PIN; 3 material effect on the claimed output, state, evidence, determinism or integration behaviour, where style, optional hardening, hypothetical misuse and defence-in-depth do not qualify by themselves; 4 a concrete discriminator; 5 the fix inside this component's boundary):

| Finding | 1 | 2 | 3 | 4 | 5 | Blocks? |
|---|---|---|---|---|---|---|
| F1 capture guard misses `<PREFIX>_API_KEY=<v>` | yes (item 2) | yes | **no**: the effect needs an operator-set live profile with an inline NON-`sk-` key on a malformed line; the real OmniRoute `sk-` key is already withheld in those shapes; the guard is a defence-in-depth net on exception text | yes | yes | no |
| F1b `sk-` key tail via the YAML snippet | no (not a contract shape) | yes | no (the same hypothetical trigger) | yes | yes | no |
| F2, F3, F13 screen blind spots and backtracking | no (pre-existing, outside the left-anchor contract) | yes | no (0 instances in the evidence; the mint path is time-bounded) | yes | yes | no |
| F4 narrowed test | no (AF-AP-32 allows a declared PENDING) | yes | no (a weakened tripwire, no false state) | yes | yes | no |
| F5 STATUS.md stale | partly (CLAUDE.md's prose rule) | n/a (a document) | no (not this increment's required evidence; the ledger, which wins, is right) | yes | yes | no |
| F6-F12, F14 | no | - | no | - | - | no |

No CONTRACT-DEFECT (nothing falsifies evidence, corrupts state or loses data) and no CONTRACT-INVALID: the contract is satisfiable as written; the one literal impossibility, "each new test reds on the PIN's rules" for the 12 ordinary-text controls, is met in intent by the over-wide-anchor mutants M4-M6, which I reproduced.

**For the coordinator, before the owner signs (the landing is not on origin yet; origin is at a67489f):**
1. **F1 and F1b are the items to settle now.** Contract item 2 is not met as written for the capture guard, and the landing records it as "not done" rather than amending the contract. Either amend item 2 on record, or fix now: the capture tool is an attested input, so a fix is one more sandbox re-mint and no extra owner signature today, but a second re-sign if it comes after. If you read item 2 literally and count the stderr leak as material, F1 is the single blocker candidate (conditions 1, 2, 4 and 5 hold).
2. **F5**: correct `STATUS.md:3`, `:10` and `:70` (a doc edit; no re-mint).
3. Register F11 (S0-01's stderr screen, a signed proof) as a task; it is only in the landing's "Not done" text.
4. The rest are follow-ups: F2, F3, F4, F10, F13; the INFO rows need no action.

## 11. Scratch and reruns (21:5xZ)

Deleted: every scratch tree (the PIN archive, the mutation copy, the re-mint copy, the clone, the throwaway GnuPG home under `/tmp/vs4`). Kept (52 KB, not committed): the harness scripts in `<scratch>/vs004/` (`anchors.py`, `fielddiff.py`, `mutate.py`, `states.sh`, `states2.sh`, `lib.sh`, `s001.py`, `x1.py`). To rerun, rebuild their inputs first: `git archive 1f764fe proofs scripts tests/test_s0_04_compression.py tests/conftest.py | tar -x -C <scratch>/vs004/pin`; the parent's two tools from `git show 1f764fe~1:<path>` into `<scratch>/vs004/old/`; the clone as in section 4; a throwaway key as in section 4. The shared tree: no tracked file touched; this report is the only new file.

Observation for the coordinator (21:5xZ): during this lane, `scripts/push_when_green.sh` and `tests/test_push_when_green.py` became modified in the shared tree. This lane did not write them (every write of mine went to scratch or this report), and `.lanes-live` does not declare them (it lists this report and S1-ALL's four paths). Whoever owns them should claim them before a `--lanes-live` push, which counts tracked dirty files against the declared list.
