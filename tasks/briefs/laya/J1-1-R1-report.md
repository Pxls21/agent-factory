# J1-1-R1 — report (build lane j1-1-r1, sandbox, task #139, AMENDMENT 1 to J1-1 under D-056)

ROLE: code-implementer (sandbox, Opus 5.5). PIN 519e7b2 (origin head 11195d9 at start). Brief: `tasks/briefs/laya/J1-1-R1-brief.md`.
Scratch: `/tmp/j11r1/` (removed at the end). Interpreter: `/root/venv-agent-factory/bin/python`. All secrets in probes and tests are FAKE.
Status: BUILT, with the D-1 ruling (option D) applied (section 12): A1-A5, privkey, C-F3a and C-F3b, the TOKEN name included in the widened envval behind a placeholder guard; 72 passed x2, 23/23 mutants killed, the golden digests unchanged. Round 1 (sections 1-11) stopped on D-1 with 64 passed and 18/18 mutants killed; those numbers are kept below, marked SUPERSEDED. Nothing committed (the coordinator commits).

## 0. PREMISE re-measured (2026-09-23T11:42Z, sandbox, working tree = PIN on the boundary)

```
$ git log --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf -8 | cut -c1-80
11195d9 transcripts: scrubbed sandbox chat digests (2026-09-23)
dd9f76f Ledger plane 2026-09-23 11:3xZ: J1-0-R4 and E3-R1 landed, VERIFY-J1-1 answered by D-0
97b589a E3-R1 landed (task #175; GATED-PENDING-VERIFY): a second signal cannot abort the S0-05
519e7b2 D-056 and the J1-1-R1 brief (task #139): the decision state is bounded after redactio
$ blob at 519e7b2 | blob in the working tree | lines
00c00847b33d 00c00847b33d 21 src/agent_factory/decisions/__init__.py
cda5c198d321 cda5c198d321 77 src/agent_factory/decisions/canonical.py
6d3d6a34150c 6d3d6a34150c 295 src/agent_factory/decisions/volatile.py
9531cff7d697 9531cff7d697 617 src/agent_factory/decisions/ledger.py
aa22d19cb94d aa22d19cb94d 340 tests/test_decisions_canonical.py
132f9d4e1df0 132f9d4e1df0 1468 tests/test_decisions_ledger.py
(the seven golden fixtures: blob at PIN == working tree, all seven)
$ git log --format='%h %s' 519e7b2..HEAD -- src/agent_factory/decisions tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/fixtures/decisions
(end)      <- nothing after the PIN touches the boundary
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/j11r1/bt/r0
53 passed in 0.31s
rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
```
The blobs equal the brief's authoring measure byte for byte (`tasks/briefs/laya/J1-1-R1-brief.md:115-120`, from `00c00847b33d` to `132f9d4e1df0`).

The defects, reproduced through the real code (probe `/tmp/j11r1/probes/premise.py`; `volatile from /home/user/agent-factory/src/agent_factory/decisions/volatile.py`):
```
privkey RSA PRIVATE KEY        body-left=False placeholder=True
privkey PGP PRIVATE KEY BLOCK  body-left=True placeholder=False
privkey PGP SECRET KEY BLOCK   body-left=True placeholder=False
privkey RSA, no END            body-left=True placeholder=False
C-F3a token = 0123456789abcdef0123   leak=True
C-F3a access_token=0123456789abcde   leak=True
C-F3a "token": "0123456789abcdef01   leak=True
C-F3a PC_BRIDGE_TOKEN: 0123456789a   leak=True
C-F3a AGENT_TOKEN: 0123456789abcde   leak=True
C-F3a token: 0123456789abcdef01234   leak=False        <- control, caught today
C-F3b password=Fake0Pass9Word7Valu   leak=True
C-F3b PASSWORD = Fake0Pass9Word7Va   leak=True
C-F3b password: Fake0Pass9Word7Val   leak=True
C-F3b SECRET_KEY: Fake0Pass9Word7V   leak=True
C-F3b "api_key": "Fake0Pass9Word7V   leak=True
C-F3b API_KEY=Fake0Pass9Word7Value   leak=False        <- control, caught today
C-F1 sk straddle 400        APPENDED secret_bytes_in_ledger=True len=400
C-F1 bearer straddle 200    APPENDED secret_bytes_in_ledger=True len=200
C-F1 token straddle 120     APPENDED secret_bytes_in_ledger=True len=120
C-F1 PEM body 1500          APPENDED secret_bytes_in_ledger=True len=400
F-3 trailing space at the cut      REFUSED decision-row-state-not-canonical
```
The PREMISE HOLDS: the cut at `src/agent_factory/decisions/volatile.py@519e7b2:143` (`s = s[: f.limit]`) runs before redaction, and secret bytes of four classes reach the ledger file through `make_row` -> `append`; `_TOKEN` (`src/agent_factory/decisions/volatile.py@519e7b2:48`) misses the five C-F3a forms; `_ENVVAL` (`src/agent_factory/decisions/volatile.py@519e7b2:52-54`) misses the five C-F3b forms; `_PRIVKEY` (`src/agent_factory/decisions/volatile.py@519e7b2:56-59`) misses GnuPG armor and an END-less block. No STOP on the premise.

## 1. RED at the PIN, GREEN after (the round-1 test files)

SUPERSEDED by section 12: these are round 1's counts, and the file:line refs inside the pasted block are the round-1 test file's lines (section 12 inserted two `_forms` rows, so the same asserts now sit 2 lines lower; the report lint checks these refs against the final file and reads them as MISS, which is expected for this verbatim record). The final test files at the PIN: `19 failed, 54 passed` (section 12.3).

RED: the final test files run on a scratch copy whose four `src/agent_factory/decisions/*.py` blobs equal 519e7b2 byte for byte (`6d3d6a34150c`, `cda5c198d321`, `9531cff7d697`, `00c00847b33d`); `tests/test_zz_where.py` in the copy asserts that pytest imports the copy's own modules (AF-AP-78). 2026-09-23T12:18:17Z. One line per failed test (`--tb=line`; the `<-` notes are mine, one identifier from each cited line):
```
tests/test_decisions_canonical.py:475: AssertionError: assert 'aaaaaaaaaaaa...aaaaaaaaaaaa ' == 'aaaaaaaaaaaa...c c c c c c c'   <- `normalize("ap.violates_row", state)`
tests/test_decisions_canonical.py:508: AssertionError: b2.hit_role.sym sk k=1: the straddling secret does not hash as its placeholder form   <- `state_digest(qid, state) == state_digest(qid, clean)`
tests/test_decisions_canonical.py:532: AssertionError: b2.hit_role.sym sk: an over-limit field breaks the secret/placeholder identity   <- `state_digest(qid, state) == state_digest(qid, clean)`
tests/test_decisions_canonical.py:568: AssertionError: RSA PRIVATE KEY end=True: 'block follows: -----BEGIN RSA PRIVATE KEY----- QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQ'   <- `redacted["observed"] == want`
tests/test_decisions_canonical.py:596: AssertionError: 'token = QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJ' -> 'set token = QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJ now'   <- `got == "set " + want`
tests/test_decisions_canonical.py:620: AssertionError: 'password=QZXJQZXJQZXJQZXJQZXJ' -> 'set password=QZXJQZXJQZXJQZXJQZXJ now'   <- `got == "set " + want`
tests/test_decisions_canonical.py:657: Failed: redact backtracked for over 5 s on 'A_A_A_A_A_A_A_A_A_A_A_A_'...   <- `pytest.fail`
tests/test_decisions_canonical.py:369: ImportError: cannot import name 'decision_state' from 'agent_factory.decisions' (/tmp/j11r1/lit/src/agent_factory/decisions/__init__.py)
tests/test_decisions_canonical.py:369: ImportError: cannot import name 'decision_state' from 'agent_factory.decisions' (/tmp/j11r1/lit/src/agent_factory/decisions/__init__.py)
tests/test_decisions_canonical.py:756: AssertionError: assert 'decision_state' in ['DecisionStateError', 'normalize', 'redact', 'state_digest']
tests/test_decisions_ledger.py:1529: AssertionError: sk, 7 body characters before the limit: secret body bytes ['J', 'Q', 'X', 'Z'] reached the ledger file   <- `assert not leaked`
11 failed, 54 passed in 5.37s
rc=1
```
The 54 passed are the 53 tests of the PIN plus the import check. The two ImportError rows are the bound test and the idempotence test: `decision_state` does not exist at the PIN, which is their honest red. Every other row fails for the defect itself. The backtracking row is a PRE-EXISTING hang in the PIN's own `_ENVVAL` (D-3).

GREEN: the working tree (the two gate runs are pasted in section 6): `64 passed`.

## 2. Per contract line: what changed and what pins it

The line refs are re-pointed to the final tree. The C-F3b row and the form count (8) are round 1's, SUPERSEDED by section 12.1.

| line | change (files:lines, working tree) | tests that pin it |
|---|---|---|
| A1 normalize never cuts | the two lines `if f.limit is not None: s = s[: f.limit]` are removed from `_normalize_field` (`src/agent_factory/decisions/volatile.py:157`, hunk at old 142-143); every other step unchanged | `test_normalize_never_cuts` (`tests/test_decisions_canonical.py:474`) |
| A2 bound after redact | new `def bound` (`bound(question_id, state)`, `src/agent_factory/decisions/volatile.py:337`): `value[: spec.limit].rstrip()` for each bounded str field; lists and unbounded fields pass unchanged; an unknown question id is refused `decision-question-unknown` | `test_bound_cuts_code_points_strips_trailing_whitespace_every_field_within_limit` (`tests/test_decisions_canonical.py:667`), `test_straddle_every_class_every_bounded_key` (`tests/test_decisions_canonical.py:495`) |
| A3 ONE composition | new `decision_state` (`src/agent_factory/decisions/volatile.py:355`) = `bound(question_id, redact(normalize(question_id, state, root)))`; exported (`src/agent_factory/decisions/__init__.py:18`, `__all__` at `src/agent_factory/decisions/__init__.py:24`); `state_digest` = `sha256(canonical(decision_state(...)))` (`src/agent_factory/decisions/canonical.py:77`); the fixed-point check (`src/agent_factory/decisions/ledger.py:273`) and `make_row` (`src/agent_factory/decisions/ledger.py:404`) call it; docstrings that stated the old composition updated (`src/agent_factory/decisions/volatile.py:1-20`, `src/agent_factory/decisions/canonical.py:5-12`, `src/agent_factory/decisions/__init__.py:3-13`, the (d) comment at `src/agent_factory/decisions/ledger.py:270`, the test module docstring `tests/test_decisions_canonical.py:9-17`) | `test_state_digest_is_sha256_of_canonical_decision_state` (`tests/test_decisions_canonical.py:753`), `test_decision_state_idempotent_including_a_cut_inside_each_placeholder` (`tests/test_decisions_canonical.py:722`), `test_over_limit_straddling_secret_appends_and_replays` (`tests/test_decisions_ledger.py:1480`) |
| A4 C-F3a token | `_TOKEN` (`src/agent_factory/decisions/volatile.py:53`): left context `(?:\b|(?<=_))` (`*_token`, `*_TOKEN`), an optional quote after the name, `(?: ?[:=] ?| )?` (at most one space on each side, never a run), an optional quote before the run | `test_token_assignment_forms_redacted` (`tests/test_decisions_canonical.py:577`) |
| A4 C-F3b envval | SUPERSEDED by section 12.1 (two passes; TOKEN included; the guard; `\s?`). Round 1: `_ENVVAL` (now `src/agent_factory/decisions/volatile.py:73`): the upper-case `NAME=\S+` form kept, plus a case-insensitive form `name["']?\s*[:=]\s*["']?` + a value of `[^\s"'&,;]{8,}` (the scrubber's shape); the name and separator are kept, the value becomes `<redacted:envval>`; TOKEN is NOT in the widened form (D-1); no name-prefix group (D-3) | `test_env_assignment_forms_redacted_and_prose_kept` (`tests/test_decisions_canonical.py:602`), `test_env_assignment_redaction_does_not_backtrack_exponentially` (`tests/test_decisions_canonical.py:636`) |
| A4 privkey | `_PRIVKEY` (`src/agent_factory/decisions/volatile.py:82`): the scrubber's label family `[A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?`, END or `\Z` | `test_private_key_blocks_longer_than_the_limit_gnupg_and_endless` (`tests/test_decisions_canonical.py:544`) |
| A5 identity + no body byte | follows from A1-A3 | `test_straddle_every_class_every_bounded_key` (16 bounded keys x 8 forms x every straddle position), `test_over_limit_identity_every_class` (`tests/test_decisions_canonical.py:520`), the ledger test (the file's bytes) |

The body check is one character wide: every FAKE secret body uses only the letters Q Z X J, which no name, separator, placeholder, filler, hex digest or source_ref field in these tests contains (`_BODY_ALPHABET`, `tests/test_decisions_canonical.py:358`).

## 3. Golden digests

| fixture | committed digest (PIN) | `state_digest` now, state | now, variant | A-line |
|---|---|---|---|---|
| ap.violates_row.json | 594584bde9869086 | 594584bde9869086 | 594584bde9869086 | unchanged |
| b1.finding_kind.json | 9e18ed7e5146a2c3 | 9e18ed7e5146a2c3 | 9e18ed7e5146a2c3 | unchanged |
| b1.finding_sev.json | 8c42d5dd1e8c349e | 8c42d5dd1e8c349e | 8c42d5dd1e8c349e | unchanged |
| b2.hit_role.json | 3ced4cd39a61faa5 | 3ced4cd39a61faa5 | 3ced4cd39a61faa5 | unchanged |
| d1.bug_echo_scores.json | 5a8c4ad2659c0e6b | 5a8c4ad2659c0e6b | 5a8c4ad2659c0e6b | unchanged |
| v1.finding_class.json | f41a299c4a38ab30 | f41a299c4a38ab30 | f41a299c4a38ab30 | unchanged |
| wf.drift.json | a51a56c48e98cca6 | a51a56c48e98cca6 | a51a56c48e98cca6 | unchanged |

No fixture file changed (`git status --short tests/fixtures/decisions/` is empty). The seven states are short and carry no secret shape, so A1-A4 change none of them.

## 4. The brief's open questions (`tasks/briefs/laya/J1-1-R1-brief.md:180-182`, the J0 probe fixture `tests/fixtures/decisions/probe/questions.json`)

- Does any golden digest change? No (section 3).
- Does the widened class set redact non-secret text in the seven golden states or the J0 probe fixture? Probe `/tmp/j11r1/probes/fp_count.py` compares the PIN's `_redact_str` with the new one on every string value after the collapse:
```
string values: golden=52 probe=822
values whose redaction changed: 0
values the NEW redact changes at all: 0
```
  Count: 0 non-secret redactions in both sets (and 0 redactions of any kind).
- Wider evidence (not asked; the harvest will read reports and code): over 178,368 committed lines (754 files under `tasks/`, `docs/`, `scripts/`, `src/`, `tests/`) the widened envval redacts 199 lines the PIN form does not. A random sample of 24 held about 3 secret-shaped FAKE fixture values (`password=hunter2secret`, `"OMNIROUTE_API_KEY": "fixture-value-not-a-key"`) and about 21 non-secrets: keyword arguments (`owner_key=owner_key)`, `key=os.path.getmtime)`), `pubkey: expected str,`, `_PRIVKEY = re.compile(`, and this module's own refusal texts (`decision-state-missing-key: b1.finding_sev.file`). This over-redaction is the safe direction for secrets, but it can merge distinct states (the C-F2 class). Filed as observation O-1 in section 8, not changed: the brief fixed the class shape.

## 5. Mutation audit (driver `/tmp/j11r1/probes/mutants.py`, scratch copies of the working tree only)

SUPERSEDED by section 12.6 (23 mutants after the ruling; x9 below is retired, because TOKEN is now in the widened form by ruling).

Each mutant: exact-count string edits (anchor count asserted == 1), `py_compile` of every edited file, the collected count compared with the unmutated copy (AF-AP-78), the run, then every killing test re-run on the UNMUTATED copy (AF-AP-138). The mutants that restore `redact(normalize(...))` also restore that module's `normalize, redact` import, so they fail on meaning, not on a NameError. 2026-09-23T12:21:46Z to 12:23:06Z.
```
BASELINE (unmutated copy of the working tree): rc=0 65 passed collected=65
```
| # | mutant | compile / collected | run | verdict | killing tests (each re-run on the unmutated copy) |
|---|---|---|---|---|---|
| m1 | bound before redact (the old order) | ok / 65 | 5 failed, 60 passed | KILLED | idempotence, over-limit identity, privkey, straddle, ledger (`5 passed` unmutated) |
| m2 | bound without the trailing-whitespace strip | ok / 65 | 4 failed, 61 passed | KILLED | bound, idempotence, straddle, ledger (`4 passed`) |
| m3 | `make_row` back to `redact(normalize(...))` | ok / 65 | 1 failed, 64 passed | KILLED | `test_over_limit_straddling_secret_appends_and_replays` (`1 passed`) |
| m4 | the fixed-point check back to `redact(normalize(...))` | ok / 65 | 1 failed, 64 passed | KILLED | `test_over_limit_straddling_secret_appends_and_replays` (`1 passed`); its "cut inside the envval placeholder" case is the discriminator |
| m5 | `_TOKEN` back to its PIN pattern | ok / 65 | 4 failed, 61 passed | KILLED | over-limit identity, straddle, `test_token_assignment_forms_redacted`, ledger (`4 passed`) |
| m6 | envval back to upper case and `=` only (the PIN regex and replacement) | ok / 65 | 5 failed, 60 passed | KILLED | `test_env_assignment_forms_redacted_and_prose_kept`, the backtracking test, over-limit identity, straddle, ledger (`5 passed`) |
| m7 | privkey back to the PIN label (`PRIVATE KEY-----` only; the END-less alternative kept) | ok / 65 | 4 failed, 61 passed | KILLED | over-limit identity, privkey, straddle, ledger (`4 passed`) |
| m8 | privkey without the END-less alternative | ok / 65 | 1 failed, 64 passed | KILLED | `test_private_key_blocks_longer_than_the_limit_gnupg_and_endless` (`1 passed`) |
| m9 | bound without the cut | ok / 65 | 5 failed, 60 passed | KILLED | bound, idempotence, over-limit identity, straddle, ledger (`5 passed`) |
| x1 | the widened envval value floor 8 -> 1 (de-vacuums the prose control) | ok / 65 | 1 failed, 64 passed | KILLED | `test_env_assignment_forms_redacted_and_prose_kept` (`1 passed`) |
| x2 | the widened envval without the optional quote after the name | ok / 65 | 3 failed, 62 passed | KILLED | env forms, over-limit identity, straddle (`3 passed`) |
| x3 | `state_digest` back to `redact(normalize(...))` | ok / 65 | 2 failed, 63 passed | KILLED | `test_state_digest_is_sha256_of_canonical_decision_state`, ledger (`2 passed`) |
| x4 | `decision_state` without redact | ok / 65 | 9 failed, 56 passed | KILLED | 9 tests incl. `test_order_is_normalize_then_redact`, `test_secret_redacted_every_class`, `test_state_not_canonical` (`9 passed`) |
| x5 | the nested name-prefix group back in the widened envval | ok / 65 | 1 failed, 64 passed | KILLED | `test_env_assignment_redaction_does_not_backtrack_exponentially` (`1 passed`) |
| x6 | `_TOKEN` left context back to `\b` only | ok / 65 | 4 failed, 61 passed | KILLED | over-limit identity, straddle, token forms, ledger (`4 passed`) |
| x7 | `_TOKEN` separator bridges a whitespace run | ok / 65 | 1 failed, 64 passed | KILLED | `test_order_is_normalize_then_redact` (`1 passed`): the in-force order discriminator still discriminates |
| x8 | `EXCERPT_LIMIT` 400 -> 401 (VERIFY-J1-1 m11 survived at the PIN) | ok / 65 | 5 failed, 60 passed | KILLED | bound, idempotence, over-limit identity, straddle, ledger (`5 passed`) |
| x9 | TOKEN added to the widened envval (the literal C-F3b reading, D-1) | ok / 65 | 3 failed, 62 passed | KILLED | idempotence (`AssertionError: ('b2.hit_role', 'sym', 'token: <redacted:token>', 18, 'aaaaaaaaaaaaaaaaaaaaa token: <redacted:e')`: a clean `token: <redacted:token>` is re-labelled envval), `test_order_is_normalize_then_redact`, token forms (`3 passed`) |

Survivors: none. The full per-row output with the killing-test node ids is the driver's log (removed with the scratch; every row is reproduced by re-running the driver).

## 6. Gates (every command pasted with its output)

SUPERSEDED by section 12.7 (the counts below are round 1's: 64 tests).

```
$ date -u; mkdir -p /tmp/j11r1/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/j11r1/bt/r1   (then rm -rf)
2026-09-23T12:23:36Z
64 passed in 2.22s
r1-rc=0
$ ... --basetemp=/tmp/j11r1/bt/r2   (then rm -rf)
64 passed in 2.27s
r2-rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
$ per-test outcomes of two -v runs
run1: 64 outcome lines, sha=540a63a226a8a86c, PASSED=64
run2: 64 outcome lines, sha=540a63a226a8a86c, PASSED=64
per-test outcomes bitwise equal
$ /root/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/*.py tests/test_decisions_canonical.py tests/test_decisions_ledger.py
pyflakes-rc=0
$ python3 scripts/ap_screen.py src/agent_factory/decisions/volatile.py src/agent_factory/decisions/canonical.py src/agent_factory/decisions/ledger.py
--- AP_SCREEN over 3 path(s): 4 hits over 3 files ---
AP-32: 4
    src/agent_factory/decisions/canonical.py:7: state_digest = sha256(canonical(decision_state(state)))
    src/agent_factory/decisions/canonical.py:72: """sha256(canonical(decision_state(state))), hex. The pipeline is
    src/agent_factory/decisions/canonical.py:78: return hashlib.sha256(text.encode("utf-8")).hexdigest()
    src/agent_factory/decisions/ledger.py:76: return hashlib.sha256(text.encode("utf-8")).hexdigest()
(the same screen on the PIN's three files, `git show 519e7b2:<file>`: 4 hits, AP-32: 4, the same four statements at canonical.py:7/71/77 and ledger.py:77)
$ python3 scripts/ap_screen.py --tests tests/test_decisions_canonical.py tests/test_decisions_ledger.py
--- TEST_SCREEN over 2 path(s): 1 hits over 2 files ---
AP-70: 1
    tests/test_decisions_ledger.py:1292: except Exception:
(the same screen on the PIN's two test files: 1 hit, the same line 1292)
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean
no-laya-rc=0
```
New AP hits vs the PIN: 0 (production) and 0 (tests). The set id `16a7b628685e` equals the brief's (the same two files); the count moved 53 -> 64 (11 new tests).
GitNexus `detect-changes --scope all`: `Changes: 6 files, 32 symbols / Affected processes: 11 / Risk level: high` -- the six files are exactly this lane's boundary; every affected flow is inside the decisions module (`Make_row -> ...`, `Append -> ...`). HIGH is the expected rating for a change to the ledger's state pipeline; the module has no consumer outside its two test files (the pack's callers plus a literal sweep of `agent_factory.decisions` over `*.py`).
Performance (A1 now hands `redact` a whole unbounded field): the full `_redact_str` on 12 adversarial repeats at 2k/8k/32k characters took at most `0.0049 s` at 32k, linear in every row.

## 7. DISCREPANCIES

**D-1 -- RESOLVED by the coordinator's ruling (option D), applied in section 12. The round-1 record follows.** **STOP on one sub-line: the TOKEN name in the widened envval class (A4 C-F3b vs A4's own last sentence, C-F3a, J1-1 item 3 in force, the in-force order test and the brief's m5).** A4 C-F3b lists TOKEN among the names matched without regard to case with a `:` separator; the class order (envval before token, "an assignment wins its own class") then hands every C-F3a form, and the PIN's own token form `token: <run>`, to envval. Measured on a scratch copy of the PIN with the literal reading applied (`/tmp/j11r1/probes/literal_patch.py`), the UNCHANGED suite (L1 = the scrubber's `\s*[:=]\s*`, L2 = `\s?[:=]\s?`; the runs include the import check):
```
patched L1
compile-ok
E       assert '0123456789abcdef0123456789abcdef' in '{"file":"src/a.py","kind":"k","msg":"token: <redacted:envval>"}'
FAILED tests/test_decisions_canonical.py::test_order_is_normalize_then_redact
1 failed, 53 passed in 0.37s
===
patched L2
compile-ok
E       assert '<redacted:token>' in '{"file":"src/a.py","kind":"k","msg":"token: <redacted:envval>"}'
FAILED tests/test_decisions_canonical.py::test_order_is_normalize_then_redact
1 failed, 53 passed in 0.30s
```
and the C-F3a forms on the L2 copy (`as-built` = L2's widened `_TOKEN`; `m5(PIN)` = the same copy with `_TOKEN` reverted to the PIN; probe `/tmp/j11r1/probes/cf3a_m5.py`):
```
as-built  token = 0123456789abcdef   -> token = <redacted:envval>                  leak=False
as-built  access_token=0123456789a   -> access_token=<redacted:envval>             leak=False
as-built  "token": "0123456789abcd   -> "token": "<redacted:envval>"               leak=False
as-built  PC_BRIDGE_TOKEN: 0123456   -> PC_BRIDGE_TOKEN: <redacted:envval>         leak=False
as-built  AGENT_TOKEN: 0123456789a   -> AGENT_TOKEN: <redacted:envval>             leak=False
as-built  token: 0123456789abcdef0   -> token: <redacted:envval>                   leak=False
as-built  token 0123456789abcdef01   -> token <redacted:token>                     leak=False
as-built  access_token 0123456789a   -> access_token <redacted:token>              leak=False
m5(PIN)   token = 0123456789abcdef   -> token = <redacted:envval>                  leak=False
m5(PIN)   access_token=0123456789a   -> access_token=<redacted:envval>             leak=False
m5(PIN)   "token": "0123456789abcd   -> "token": "<redacted:envval>"               leak=False
m5(PIN)   PC_BRIDGE_TOKEN: 0123456   -> PC_BRIDGE_TOKEN: <redacted:envval>         leak=False
m5(PIN)   AGENT_TOKEN: 0123456789a   -> AGENT_TOKEN: <redacted:envval>             leak=False
m5(PIN)   token: 0123456789abcdef0   -> token: <redacted:envval>                   leak=False
m5(PIN)   token 0123456789abcdef01   -> token <redacted:token>                     leak=False
m5(PIN)   access_token 0123456789a   -> access_token 0123456789abcdef0123456789a   leak=True
```
So the literal reading (a) breaks the in-force contract test `test_order_is_normalize_then_redact` (its discriminator dies under the scrubber's `\s*`; its `<redacted:token>` assertion dies under `\s?`), (b) moves the PIN form `token: <run>` from the token class to envval, against "the existing forms stay" and J1-1 item 3 ("a 32+ hex/base64 run after `token` -> token"), and (c) makes the `_TOKEN` widening unreachable for all five listed C-F3a forms, so the brief's m5 could not be killed by them. Mutant x9 (section 5) measures the same on the built tree: `3 failed`.
BUILT (the uncontested lines): the widened envval covers KEY, SECRET, PASSWORD, PASSWD, API_KEY/APIKEY; TOKEN keeps its PIN envval form (upper-case `NAME=value`); the five C-F3a forms go to the token class through `_TOKEN` (C-F3a's own pointer at `_TOKEN`); every in-force test stays green and m5 is killed.
NOT BUILT (the contested region stays at its PIN behavior -- no regression, no fix): a TOKEN-named assignment in the widened forms whose value is NOT a 32+ `[A-Za-z0-9+/]` run. Measured on the built tree:
```
'token: QZXJQZXJ12'                        -> 'token: QZXJQZXJ12'                            body_left=True
'access_token=QZXJQZXJ12'                  -> 'access_token=QZXJQZXJ12'                      body_left=True
'PC_BRIDGE_TOKEN: QZXJQZXJ12'              -> 'PC_BRIDGE_TOKEN: QZXJQZXJ12'                  body_left=True
'SECRET_TOKEN = QZXJQZXJ12'                -> 'SECRET_TOKEN = QZXJQZXJ12'                    body_left=True
'token: QZXJQZXJQZXJQZXJ-QZXJQZXJQZXJQZXJ' -> 'token: QZXJQZXJQZXJQZXJ-QZXJQZXJQZXJQZXJ'     body_left=True
'TOKEN=QZXJQZXJ12'                         -> 'TOKEN=<redacted:envval>'                      body_left=False
'token: QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJ'  -> 'token: <redacted:token>'                      body_left=False
```
The coordinator's options: (C) the literal reading -- add TOKEN to the widened form; envval then owns every token assignment (the rows above are redacted, base64url included); rewrite the in-force order test's input to a colon-less split (`token  <run>`) and its `<redacted:token>` expectation; the C-F3a forms and `token: <run>` become `<redacted:envval>`; m5 needs an unlisted form such as `access_token <run>`. (D) keep the token class for a TOKEN-named 32+ run and give envval the rest of the TOKEN names: needs a TOKEN-only alternative with a negative lookahead for a pure run AND a guard so the widened form never re-labels a `<redacted:` placeholder (x9 shows the re-label), which is new design this lane did not build or measure. Either option is one small edit to `_ENVVAL` and its tests.

**D-2 -- A3's idempotence has one counterexample that A1 + A2 fix in place (pre-existing, fail-closed; not fixed).** A3 says `decision_state` is idempotent on its own output; A1 keeps normalize's pin-suffix strip as it is and A2 fixes bound as cut + strip. A v1 lane whose cut (or a double suffix) exposes a PIN-shaped suffix is stripped again on the next pass (`/tmp/j11r1/probes/strip_pin_idem.py`):
```
== PIN copy
redact(normalize): cut exposes --<8 hex>  once='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx--01234567' twice='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' fixed_point=False ledger=REFUSED decision-row-state-not-canonical
redact(normalize): double PIN suffix      once='lane--0123456'              twice='lane'                     fixed_point=False ledger=REFUSED decision-row-state-not-canonical
redact(normalize): control: one suffix    once='lane'                       twice='lane'                     fixed_point=True ledger=APPENDED
== working tree
decision_state: cut exposes --<8 hex>  once='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx--01234567' twice='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' fixed_point=False ledger=REFUSED decision-row-state-not-canonical
decision_state: double PIN suffix      once='lane--0123456'              twice='lane'                     fixed_point=False ledger=REFUSED decision-row-state-not-canonical
decision_state: control: one suffix    once='lane'                       twice='lane'                     fixed_point=True ledger=APPENDED
```
The row is refused, never written wrong. A fix needs either a strip that loops to a fixed point (A1 keeps the step as is) or a pin strip inside bound (A2 names bound's two steps), so it is reported, not built. The `decision_state` docstring names the exception (`src/agent_factory/decisions/volatile.py:355`).

**D-3 -- implementation choice, flagged: the envval name-prefix group is gone (output-identical; removes an exponential backtrack that exists at the PIN).** The PIN's `_ENVVAL` carries `(?:[A-Z][A-Z0-9_]*_)*`, a nested quantifier (`/tmp/j11r1/probes/redos.py`, a child process per call; four of its lines):
```
PIN  'A_'*22    len=    44 0.5041s
PIN  'A_'*26    len=    52 8.6478s
FLAT 'A_'*26    len=    52 0.0000s
CUR  'a_'*22    len=    44 1.0052s      <- the same group made case-insensitive for C-F3b
```
Measured end to end on the PIN copy: `PIN state_digest, msg='A_'*24 (48 chars): 2.05s` and `PIN state_digest, msg='A_'*26 (52 chars): 8.14s` (the time about doubles per `A_`); the working tree: `working tree state_digest, msg='A_'*26: 0.0001s`. `make_row` runs the same pipeline, so a short upper-case snake chain in any bounded field stalls it at the PIN. A case-insensitive copy of the group would have made lower-case snake_case trigger it too. The prefix never changes the output: the scan finds the name where it starts and the text before it is kept (`/tmp/j11r1/probes/envval_equiv.py`, 754 files, the probe fixture and 14 adversarial lines):
```
files=754 corpus lines=178368
{'a1_diff': 0, 'a1_slow': 0, 'cur_flat_diff': 3, 'cur_slow': 0, 'flat_changes': 331, 'pin_changes': 141}
  CUR/FLAT: '            key_file.write_text(f"TERMINAL_DEBUG=1\\nOMNIROUTE_API_KEY={SCRATCH_KEY}\\n")'
  CUR/FLAT: 'db_PASSWORD="abcdefgh,ijk"'
  CUR/FLAT: 'x_SECRET=abcdefgh;rest'
```
`a1_diff: 0`: the PIN form without its group equals the PIN regex on every line (it changed 141). The three `cur_flat_diff` lines show a second defect of a prefixed widened form: a lower-case prefix lets it start before the PIN form and stop at a comma (`db_PASSWORD="<redacted:envval>,ijk"` against the PIN's `db_PASSWORD=<redacted:envval>`). The flat form keeps the PIN's output. Pinned by `test_env_assignment_redaction_does_not_backtrack_exponentially` (red at the PIN, row 657 in section 1; kills x5).

**D-4 -- `ledger.py` scope: one import line besides the two call sites.** The brief's boundary names the two call sites and the composition docstrings. Switching the call sites requires importing `decision_state`, and removes the last use of `normalize` and `redact` there; pyflakes flags an unused import even under `# noqa` (measured: `'os.path' imported but unused` with `# noqa: F401`). So the import block changed (`src/agent_factory/decisions/ledger.py:40-44`); nothing else in `ledger.py` changed (4 hunks: the import, the (d) comment, :273, :404). The same reason removed the unused `normalize, redact` re-export from `canonical.py` (no importer: a literal sweep of `from agent_factory.decisions.canonical import`).

## 8. Adjacent findings (reported, not fixed)

- O-1: the widened envval over-redacts real text: 199 committed lines newly redacted, a random sample of 24 held about 21 non-secrets (keyword arguments like `owner_key=owner_key)`, `pubkey: expected str,`, this module's own refusal texts `decision-state-missing-key: b1.finding_sev.file`). Safe for secrets; distinct states can merge (the C-F2 class). A left boundary on the name would cut most of it. Contract follow-up.
- O-2: the pre-existing exponential backtrack (D-3) is a registry-worthy class: "a nested quantifier (a group that ends in a starred class, itself starred) in a redaction regex hangs on a short input". Sweep for siblings (`grep -F -e '*_)*' -e '+_)*' -e '*)*' -e '+)+' -e '*)+'` over `scripts/ src/ proofs/ harness-ports/` `*.py`): none left.
- O-3: the transcript scrubber's credential rule (`scripts/transcript_export.py:33`, the rule with `api[_-]?key`) misses two C-F3b shapes itself (measured): `'"api_key": "QZXJQZXJ12"' -> unchanged` and `'SECRET_KEY: QZXJQZXJ12' -> unchanged` (only 40+ runs reach its opaque rule). The decisions class covers both (the optional quote after the name, the name found inside a prefix).
- O-4: `src/agent_factory/decisions/ledger.py:9-10` says "``normalize`` does not report which classes it stripped"; `redact` strips classes, so the line was imprecise at the PIN already. Not a composition statement, not touched.

## 9. NOT-done (first-class)

- D-1: CLOSED by the ruling (section 12). Round 1's text: TOKEN-named assignments in the widened forms with a value that is not a 32+ run still leak (the rows in D-1), exactly as at the PIN. Awaiting the coordinator's choice between (C) and (D).
- D-2: the pin-suffix idempotence edge (refused rows, never leaked). Filed at landing as a follow-up (the ruling).
- O-1 over-redaction, O-3 scrubber gaps, O-4: not in this boundary; filed at landing as follow-ups (the ruling; O-3 is handled by the coordinator).
- The VERIFY-J1-1 follow-ups the brief excludes (C-F2 `sk-` word boundary, base64url token runs F-12, C-F4, C-F5, C-F7, F-2, F-5, F-8): not touched.
- No PC or bridge run; no full-tree suite (the decisions package has no consumer outside its two test files).
- Scratch `/tmp/j11r1/` is removed at the end of this lane (the probes quoted here die with it; each is described well enough to rebuild).

## 10. Self-attack: the three likeliest ways this change is wrong

SUPERSEDED in part by section 12.8 (the ruling's delta); the three items below still hold.

1. The leak tests pass vacuously (the body could be hidden by the filler or never reach the output). Ruled out: the body alphabet (Q Z X J) is checked one character at a time and nothing else in the states contains it; at the PIN the same tests are red on found body bytes (`secret body bytes ['J', 'Q', 'X', 'Z'] reached the ledger file`), and m1, m5, m6, m7, m9 are killed by the straddle and ledger tests.
2. The rewritten envval changes an existing output (the "existing forms stay" rule). Ruled out for the PIN form: 0 of 178,368 lines differ between the PIN regex and the flat PIN form (D-3), and the PIN-era envval tests stay green; the only new outputs are the widened forms, and the golden and probe sets show 0 changed redactions (section 4).
3. `decision_state` is not idempotent somewhere, so the ledger refuses rows `make_row` built. Ruled out where it matters: the straddle sweep asserts idempotence at every cut position inside every placeholder form for all 16 bounded keys; the ledger test appends and replays ten over-limit rows, including a cut inside the envval placeholder (the m4 discriminator); the one counterexample found (D-2) is pre-existing and fails closed.

## 11. Evidence tiers

SUPERSEDED by section 12.8 for the ruling's counts.

- VERIFIED (this session, pasted): the premise; RED at the PIN (11 failed, 54 passed); GREEN twice (64 passed, bitwise-equal outcomes); the golden table; the probe-fixture count; 18 mutants killed with unmutated re-runs; pyflakes; both AP screens vs the PIN; no_laya; the D-1 literal-reading runs; the D-2 and D-3 measurements; linear redact timing.
- INFERRED: that the widened-envval false positives in committed text predict the harvest's (O-1) -- a 24-line sample, not a census.
- ASSUMED: none load-bearing.

## 12. D-1 ruling applied (the coordinator's ruling: option D; applied 2026-09-23T12:36Z to 12:44Z)

The ruling (class order, first match wins; the placeholders do not change): 1 privkey · 2 the PIN's upper-case `NAME=\S+` env form, TOKEN included, unchanged · 3 the token class (the PIN's `_TOKEN` forms plus the five C-F3a forms) · 4 the widened C-F3b env form WITH TOKEN, after the token class, with a guard so it never replaces a value that already is a placeholder. sk and bearer, which the ruling does not name, keep their PIN place between privkey and class 2.

### 12.1 What changed (files:lines, final tree)

| item | change | pinned by |
|---|---|---|
| class 2 | `_ENVVAL` (`src/agent_factory/decisions/volatile.py:73`) is the PIN's upper-case form alone (the flat form of D-3); its pass runs before the token class (`src/agent_factory/decisions/volatile.py:331`) | `test_token_assignment_forms_redacted` (`PC_BRIDGE_TOKEN=<run>` keeps envval) |
| class 3 | `_TOKEN` unchanged since round 1 (`src/agent_factory/decisions/volatile.py:53`); its pass at `src/agent_factory/decisions/volatile.py:332` | `test_token_assignment_forms_redacted`, the no-relabel test |
| class 4 | `_ENVVAL_WIDE` (`src/agent_factory/decisions/volatile.py:74`): `(?i:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)["']?\s?[:=]\s?["']?` then `(?P<value>[^\s"'&,;]{8,})`; its pass runs last (`src/agent_factory/decisions/volatile.py:333`) | the seven `test_token_named_residual_shape_redacted[...]` items (`tests/test_decisions_canonical.py:813`) |
| the guard | `_envval_wide` (`src/agent_factory/decisions/volatile.py:311`): a value that is a placeholder, or a prefix of one (the bound cut), comes back unchanged; any other value becomes envval whole | `test_token_run_keeps_the_token_placeholder_and_no_placeholder_is_relabelled` (`tests/test_decisions_canonical.py:825`); the idempotence test (mutant x12) |
| the order | `_redact_str` (`src/agent_factory/decisions/volatile.py:322`) | mutant x11 |
| tests | `_forms` gains two envval forms (`tests/test_decisions_canonical.py:448-449`), so the straddle, over-limit-identity and idempotence sweeps cover them; the idempotence texts gain `AGENT_TOKEN: <redacted:token>` and `SECRET_TOKEN = <redacted:envval>`; `_PLACEHOLDER_TEXTS` (`tests/test_decisions_canonical.py:787`) pins the five placeholders instead of importing them; `_RESIDUAL_SHAPES` (`tests/test_decisions_canonical.py:797`); the ledger test gains two cases (`tests/test_decisions_ledger.py:1502-1503`) | |
| unchanged | `test_order_is_normalize_then_redact`, `test_secret_redacted_every_class`, `test_golden_digests_exact` and `test_relanding_stable` are byte-identical to the PIN (an AST extract of each: `byte-identical to the PIN = True`); every golden digest; `ledger.py`, `canonical.py`, `__init__.py` | |

### 12.2 Two points the ruling left open (flagged)

- N-1: the widened separator takes at most ONE whitespace character on each side (`\s?`), not the scrubber's `\s*`. With TOKEN in the widened form, `\s*` bridges `token:  <run>` when redact runs first and kills the order test's discriminator (round 1 measured it as L1 in D-1; mutant x10 measures it again now). In production the two forms act the same: normalize collapses every whitespace run to one space before redact runs.
- N-2: the guard is exact-or-prefix. A placeholder followed by more of the value is not a placeholder, so `token: <run>-tail` ends as `token: <redacted:envval>` and no byte of the tail survives. A guard that skipped every value STARTING with a placeholder would keep `-tail` (mutant x13, killed by the `run-then-base64url-tail` item).
- Consequences of N-2, disclosed: a base64-padded run (`token: <run>==`) is not a pure run, so it ends as envval, not token. A placeholder of another class after a widened-form name keeps its class (`password: sk-...` gives `password: <redacted:sk>`; round 1 gave `<redacted:envval>`). Class 2 has no guard, as at the PIN (`KEY=sk-...` still gives `KEY=<redacted:envval>`).

The class order on concrete inputs (FAKE values; the display truncates each input to 44 characters, and rows 13 and 14 are `token: <40-run>-QZXJQZXJ` and `token: <40-run>==`):
```
rule 2 (PIN form)  'PC_BRIDGE_TOKEN=QZXJQZXJQZXJQZXJQZXJQZXJQZXJ'   -> 'PC_BRIDGE_TOKEN=<redacted:envval>'
rule 2 (PIN form)  'TOKEN=QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZ'   -> 'TOKEN=<redacted:envval>'
rule 3 (token)     'token = QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJ'   -> 'token = <redacted:token>'
rule 3 (token)     'access_token=QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZX'   -> 'access_token=<redacted:token>'
rule 3 (token)     '"token": "QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZ'   -> '"token": "<redacted:token>"'
rule 3 (token)     'PC_BRIDGE_TOKEN: QZXJQZXJQZXJQZXJQZXJQZXJQZX'   -> 'PC_BRIDGE_TOKEN: <redacted:token>'
rule 3 (token)     'AGENT_TOKEN: QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZX'   -> 'AGENT_TOKEN: <redacted:token>'
rule 3 (token)     'token: QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQ'   -> 'token: <redacted:token>'
rule 4 (widened)   'token: QZXJQZXJ12'                              -> 'token: <redacted:envval>'
rule 4 (widened)   'access_token=QZXJQZXJ12'                        -> 'access_token=<redacted:envval>'
rule 4 (widened)   'SECRET_TOKEN = QZXJQZXJ12'                      -> 'SECRET_TOKEN = <redacted:envval>'
rule 4 (widened)   'token: QZXJQZXJQZXJQZXJ-QZXJQZXJQZXJQZXJ'       -> 'token: <redacted:envval>'
rule 4 (widened)   'token: QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQ'   -> 'token: <redacted:envval>'
guard consequence  'token: QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQ'   -> 'token: <redacted:envval>'
guard consequence  'password: sk-QZXJQZXJQZXJQZXJ'                  -> 'password: <redacted:sk>'
prose control      'key: sorted order'                              -> 'key: sorted order'
prose control      'token: abc'                                     -> 'token: abc'
```

### 12.3 RED, then GREEN

RED on the round-1 tree, which is the tree as handed back (src blobs `b7d92a665261` volatile, `607b65b613e2` canonical, `71fc398a5340` ledger, `377ccd53da0c` __init__), with the ruling's tests, 2026-09-23T12:37:53Z (`--tb=line`; the `<-` notes are mine):
```
tests/test_decisions_canonical.py:510: AssertionError: b2.hit_role.sym envval TOKEN name, short value k=16: the straddling secret does not hash as its placeholder form   <- `state_digest(qid, state) == state_digest(qid, clean)`
tests/test_decisions_canonical.py:534: AssertionError: b2.hit_role.sym envval TOKEN name, short value: an over-limit field breaks the secret/placeholder identity   <- `state_digest(qid, state) == state_digest(qid, clean)`
tests/test_decisions_canonical.py:820: AssertionError: 'token: QZXJQZXJQZ' -> 'set token: QZXJQZXJQZ now'   <- `got == "set " + want`
tests/test_decisions_canonical.py:820: AssertionError: 'access_token=QZXJQZXJQZ' -> 'set access_token=QZXJQZXJQZ now'   <- `got == "set " + want`
tests/test_decisions_canonical.py:820: AssertionError: 'SECRET_TOKEN = QZXJQZXJQZ' -> 'set SECRET_TOKEN = QZXJQZXJQZ now'   <- `got == "set " + want`
tests/test_decisions_canonical.py:820: AssertionError: 'PC_BRIDGE_TOKEN: QZXJQZXJQZ' -> 'set PC_BRIDGE_TOKEN: QZXJQZXJQZ now'   <- `got == "set " + want`
tests/test_decisions_canonical.py:820: AssertionError: 'token: QZXJQZXJQZXJQZXJ-QZXJQZXJQZXJQZXJ' -> 'set token: QZXJQZXJQZXJQZXJ-QZXJQZXJQZXJQZXJ now'   <- `got == "set " + want`
tests/test_decisions_canonical.py:820: AssertionError: 'token: QZXJQZXJQZXJQZXJ_QZXJQZXJQZXJQZXJ' -> 'set token: QZXJQZXJQZXJQZXJ_QZXJQZXJQZXJQZXJ now'   <- `got == "set " + want`
tests/test_decisions_canonical.py:820: AssertionError: 'token: QZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJQZXJ-QZXJQZXJQZXJ' -> 'set token: <redacted:token>-QZXJQZXJQZXJ now'   <- `got == "set " + want`
tests/test_decisions_canonical.py:848: AssertionError: password: <redacte   <- `assert redact({"msg": text})["msg"] == text`
tests/test_decisions_ledger.py:1531: AssertionError: a TOKEN name with a short value (the D-1 ruling): secret body bytes ['J', 'Q', 'X', 'Z'] reached the ledger file   <- `assert not leaked`
11 failed, 61 passed in 0.80s
rc=1
```
Every residual shape leaks on the round-1 tree (the run-then-tail row keeps its tail after the token placeholder), and the unguarded widened form relabels a cut placeholder (`password: <redacte`). The first half of the no-relabel test (a 32+ run after a TOKEN name) is green on the round-1 tree by construction, because TOKEN is not in its widened form there; mutant d1a de-vacuums it (12.6).

RED at the PIN with the final test files (a fresh `git archive 519e7b2` copy whose four src blobs equal the PIN: `6d3d6a34150c`, `cda5c198d321`, `9531cff7d697`, `00c00847b33d`; the import check proves the copy's modules run), 2026-09-23T12:43:54Z:
```
FAILED tests/test_decisions_canonical.py::test_normalize_never_cuts
FAILED tests/test_decisions_canonical.py::test_straddle_every_class_every_bounded_key
FAILED tests/test_decisions_canonical.py::test_over_limit_identity_every_class
FAILED tests/test_decisions_canonical.py::test_private_key_blocks_longer_than_the_limit_gnupg_and_endless
FAILED tests/test_decisions_canonical.py::test_token_assignment_forms_redacted
FAILED tests/test_decisions_canonical.py::test_env_assignment_forms_redacted_and_prose_kept
FAILED tests/test_decisions_canonical.py::test_env_assignment_redaction_does_not_backtrack_exponentially
FAILED tests/test_decisions_canonical.py::test_bound_cuts_code_points_strips_trailing_whitespace_every_field_within_limit
FAILED tests/test_decisions_canonical.py::test_decision_state_idempotent_including_a_cut_inside_each_placeholder
FAILED tests/test_decisions_canonical.py::test_state_digest_is_sha256_of_canonical_decision_state
FAILED tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[token-colon-short]
FAILED tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[underscore-token-equals-short]
FAILED tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[prefixed-upper-spaced-short]
FAILED tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[bridge-name-colon-short]
FAILED tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[base64url-dash]
FAILED tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[base64url-underscore]
FAILED tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[run-then-base64url-tail]
FAILED tests/test_decisions_canonical.py::test_token_run_keeps_the_token_placeholder_and_no_placeholder_is_relabelled
FAILED tests/test_decisions_ledger.py::test_over_limit_straddling_secret_appends_and_replays
19 failed, 54 passed in 5.42s
rc=1
```
All 19 new tests are red at the PIN; the 53 tests of the PIN plus the import check pass.

GREEN (the final tree), 2026-09-23T12:42:08Z:
```
72 passed in 2.37s
r1-rc=0
72 passed in 2.50s
r2-rc=0
2 files set=16a7b628685e
run1: 72 outcome lines, sha=56605e846dc83c2a, PASSED=72
run2: 72 outcome lines, sha=56605e846dc83c2a, PASSED=72
per-test outcomes bitwise equal
```

### 12.4 Golden digests (unchanged; no fixture touched)
```
ap.violates_row.json       committed=594584bde9869086 now(state)=594584bde9869086 now(variant)=594584bde9869086 unchanged=True
b1.finding_kind.json       committed=9e18ed7e5146a2c3 now(state)=9e18ed7e5146a2c3 now(variant)=9e18ed7e5146a2c3 unchanged=True
b1.finding_sev.json        committed=8c42d5dd1e8c349e now(state)=8c42d5dd1e8c349e now(variant)=8c42d5dd1e8c349e unchanged=True
b2.hit_role.json           committed=3ced4cd39a61faa5 now(state)=3ced4cd39a61faa5 now(variant)=3ced4cd39a61faa5 unchanged=True
d1.bug_echo_scores.json    committed=5a8c4ad2659c0e6b now(state)=5a8c4ad2659c0e6b now(variant)=5a8c4ad2659c0e6b unchanged=True
v1.finding_class.json      committed=f41a299c4a38ab30 now(state)=f41a299c4a38ab30 now(variant)=f41a299c4a38ab30 unchanged=True
wf.drift.json              committed=a51a56c48e98cca6 now(state)=a51a56c48e98cca6 now(variant)=a51a56c48e98cca6 unchanged=True
```

### 12.5 The brief's open question, re-answered with TOKEN in the widened form
```
string values: golden=52 probe=822
values whose redaction changed vs the PIN: 0
values the NEW redact changes at all: 0
```
Timing of the full `_redact_str` on adversarial repeats (linear, at most `0.0059` s at 32k):
```
token-colon    n=2k/8k/32k: 0.0004 0.0014 0.0059 s
token-eq-short n=2k/8k/32k: 0.0003 0.0012 0.0045 s
a_token_       n=2k/8k/32k: 0.0003 0.0010 0.0042 s
tok-quote      n=2k/8k/32k: 0.0003 0.0013 0.0055 s
key-sep        n=2k/8k/32k: 0.0003 0.0011 0.0041 s
A_             n=2k/8k/32k: 0.0002 0.0025 0.0039 s
a_             n=2k/8k/32k: 0.0002 0.0008 0.0033 s
BEGIN-block    n=2k/8k/32k: 0.0000 0.0002 0.0006 s
```

### 12.6 Mutation audit (23 mutants; the same driver, re-anchored; scratch copies of the final tree only)

Each mutant: exact-count edits, `py_compile`, collected equal to the baseline (AF-AP-78), the run, then every killing test re-run on the UNMUTATED copy (AF-AP-138). 2026-09-23T12:40:07Z to 12:41:52Z.
```
BASELINE (unmutated copy of the working tree): rc=0 73 passed collected=73
```
The two mutants the ruling asked for, pasted whole:
```
d1a [the widened form's placeholder guard removed] compile=ok collected=73 -> 4 failed, 69 passed :: KILLED
    killing test: tests/test_decisions_canonical.py::test_decision_state_idempotent_including_a_cut_inside_each_placeholder
    killing test: tests/test_decisions_canonical.py::test_order_is_normalize_then_redact
    killing test: tests/test_decisions_canonical.py::test_token_assignment_forms_redacted
    killing test: tests/test_decisions_canonical.py::test_token_run_keeps_the_token_placeholder_and_no_placeholder_is_relabelled
    the killing test(s) on the UNMUTATED copy: rc=0 4 passed
d1b [TOKEN removed from the widened form] compile=ok collected=73 -> 10 failed, 63 passed :: KILLED
    killing test: tests/test_decisions_canonical.py::test_over_limit_identity_every_class
    killing test: tests/test_decisions_canonical.py::test_straddle_every_class_every_bounded_key
    killing test: tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[base64url-dash]
    killing test: tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[base64url-underscore]
    killing test: tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[bridge-name-colon-short]
    killing test: tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[prefixed-upper-spaced-short]
    killing test: tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[run-then-base64url-tail]
    killing test: tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[token-colon-short]
    killing test: tests/test_decisions_canonical.py::test_token_named_residual_shape_redacted[underscore-token-equals-short]
    killing test: tests/test_decisions_ledger.py::test_over_limit_straddling_secret_appends_and_replays
    the killing test(s) on the UNMUTATED copy: rc=0 10 passed
```
All rows (every row: `compile=ok collected=73`, KILLED, and its killing tests `rc=0 ... passed` on the unmutated copy):

| # | mutant | run | killing tests (unmutated re-run) |
|---|---|---|---|
| m1 | bound before redact | 5 failed, 68 passed | idempotence, over-limit identity, privkey, straddle, ledger (`5 passed`) |
| m2 | no trailing-whitespace strip | 4 failed, 69 passed | bound, idempotence, straddle, ledger (`4 passed`) |
| m3 | `make_row` back to `redact(normalize(...))` | 1 failed, 72 passed | ledger (`1 passed`) |
| m4 | fixed-point check back | 1 failed, 72 passed | ledger (`1 passed`) |
| m5 | `_TOKEN` back to the PIN | 4 failed, 69 passed | over-limit identity, straddle, `test_token_assignment_forms_redacted`, no-relabel (`4 passed`) |
| m6 | envval back to upper case and `=` only (no widened pass) | 12 failed, 61 passed | env forms, backtracking, over-limit identity, straddle, the seven residual shapes, ledger (`12 passed`) |
| m7 | privkey back to the PIN label | 4 failed, 69 passed | over-limit identity, privkey, straddle, ledger (`4 passed`) |
| m8 | no END-less alternative | 1 failed, 72 passed | privkey (`1 passed`) |
| m9 | bound without the cut | 5 failed, 68 passed | bound, idempotence, over-limit identity, straddle, ledger (`5 passed`) |
| d1a | the guard removed | 4 failed, 69 passed | pasted above (`4 passed`) |
| d1b | TOKEN removed from the widened form | 10 failed, 63 passed | pasted above (`10 passed`) |
| x1 | widened value floor 8 -> 1 | 1 failed, 72 passed | env forms, the prose control (`1 passed`) |
| x2 | no optional quote after the name | 3 failed, 70 passed | env forms, over-limit identity, straddle (`3 passed`) |
| x3 | `state_digest` back to `redact(normalize(...))` | 2 failed, 71 passed | composition, ledger (`2 passed`) |
| x4 | `decision_state` without redact | 16 failed, 57 passed | 16 tests (`16 passed`) |
| x5 | the nested prefix group back in the widened form | 1 failed, 72 passed | backtracking (`1 passed`) |
| x6 | `_TOKEN` left context back to `\b` | 4 failed, 69 passed | over-limit identity, straddle, token forms, no-relabel (`4 passed`) |
| x7 | `_TOKEN` bridges a whitespace run | 1 failed, 72 passed | `test_order_is_normalize_then_redact` (`1 passed`) |
| x8 | `EXCERPT_LIMIT` 400 -> 401 | 5 failed, 68 passed | bound, idempotence, over-limit identity, straddle, ledger (`5 passed`) |
| x10 | widened separator `\s*` (the scrubber's; N-1) | 1 failed, 72 passed | `test_order_is_normalize_then_redact` (`1 passed`) |
| x11 | widened pass before the token class | 6 failed, 67 passed | order test, over-limit identity, `test_secret_redacted_every_class`, straddle, token forms, no-relabel (`6 passed`) |
| x12 | guard for whole placeholders only (N-2's prefix half) | 3 failed, 70 passed | idempotence, straddle, no-relabel (`3 passed`) |
| x13 | guard skips a value that STARTS with a placeholder (N-2) | 1 failed, 72 passed | `test_token_named_residual_shape_redacted[run-then-base64url-tail]` (`1 passed`) |

Survivors: none. x9 of round 1 (TOKEN added to the widened form) is retired: the ruling adds TOKEN, and d1b is its inverse.

### 12.7 Gates (after the ruling)
```
$ /root/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/*.py tests/test_decisions_canonical.py tests/test_decisions_ledger.py
pyflakes-rc=0
$ python3 scripts/ap_screen.py src/agent_factory/decisions/volatile.py src/agent_factory/decisions/canonical.py src/agent_factory/decisions/ledger.py
--- AP_SCREEN over 3 path(s): 4 hits over 3 files ---
AP-32: 4
(the same four statements as round 1 and the PIN: two docstrings and two sha256 returns)
$ python3 scripts/ap_screen.py --tests tests/test_decisions_canonical.py tests/test_decisions_ledger.py
--- TEST_SCREEN over 2 path(s): 1 hits over 2 files ---
AP-70: 1
    tests/test_decisions_ledger.py:1292: except Exception:
(the PIN's screens, re-run on `git show 519e7b2:<file>` copies: 4 production hits, 1 test hit -- the same statements)
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean
no-laya-rc=0
$ node .gitnexus/run.cjs detect-changes --scope all --repo .
Changes: 6 files, 35 symbols
Affected processes: 11
Risk level: high
```
New AP hits vs the PIN: 0 and 0. `detect-changes` names the same six boundary files (35 symbols: round 1's plus `_ENVVAL_WIDE`, `_envval_wide` and the new tests); every affected flow is inside the decisions module; HIGH is the expected rating for this pipeline change.

### 12.8 DISCREPANCIES, NOT-done and the self-attack delta

- DISCREPANCIES: D-1 is resolved by the ruling. No new discrepancy. N-1 and N-2 (12.2) are my calls inside the ruling, flagged, each pinned by a killed mutant (x10, x12, x13).
- NOT-done: D-2, O-1, O-3 and O-4 (filed at landing as follow-ups, per the ruling; O-3 is the coordinator's); the VERIFY-J1-1 follow-ups the brief excludes (C-F2, F-12 beyond the TOKEN-named assignment forms this ruling closes, and the rest); no PC run; no full-tree suite (the package has no consumer outside its two test files).
- Self-attack delta:
  1. The guard could let a secret through. It skips only a value that is a placeholder or a prefix of one; such text is never secret material. Every residual shape, the run-then-tail shape included, ends with no body byte (the residual tests assert the body alphabet is gone), and x13 shows a looser guard fails.
  2. The order test could be green by luck. It is byte-identical to the PIN, and x7 and x10 show its discriminator still fails on either class bridging a whitespace run.
  3. Idempotence with TOKEN in the widened form. A cut `token: <redacted:tok` after a TOKEN name is guarded by the prefix half; x12 shows the check is load-bearing, and the straddle and idempotence sweeps now include the two new TOKEN forms at every cut position.
- Evidence tiers: VERIFIED this session -- every run pasted in this section. INFERRED -- none new. ASSUMED -- none load-bearing.

Report lint after the ruling (round 2 of 3; `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/J1-1-R1-report.md --root .`): `report_lint: 80 refs — OK 66, NEAR 4, MISS 6, UNCHECKABLE 4, UNRESOLVED 0 (worktree)`. The 6 MISS are the refs inside section 1's verbatim round-1 RED block: its test-file lines sit 2 lower in the final file (the note under section 1 says so), and the round-1 tree was never committed, so no `@<sha>` pin exists for them. The 4 UNCHECKABLE are inside verbatim `ap_screen` output.
