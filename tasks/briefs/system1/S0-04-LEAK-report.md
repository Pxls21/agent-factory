# S0-04-LEAK report (task #287, D-091 item 3)

Lane: code-implementer (sandbox, Opus 5.5). Started 2026-09-25T20:28:17Z (bucket 20:2xZ). Written incrementally.
Tree at start: HEAD = origin = 5eda746. Brief PIN: 37f720a. Scratch: `<scratch>/s004leak/`
(`<scratch>` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad`).

## STATUS

(R1, the repair round of 2026-09-25, is at the end of this report.) R0: DONE (tests green, re-minted, not committed), ONE ITEM NOT DONE: `proofs/ledger.json` was not regenerated in the tree (the permission classifier refused the in-tree write; the exact expected file and its one-line diff are in section 5; the coordinator runs `python3 scripts/ledger-gen --root .`). S1 `(?<![A-Za-z0-9])` on the three anchored rules; 19 new test cases, 7 red on the PIN for the exact reason; 6 of 6 required mutants killed; the re-mint changes the two attestation hashes and six volatile fields only. Gate: `pytest-summary: 3 failed, 128 passed` twice (2 files set=2fa20f3af1f3), the 3 the brief's by-design anchor failures. Anchor states (a) and (b) proved in a scratch clone; (b) still leaves one test red (D3). The capture question: no new capture needed (section 7). Flagged: DEVIATION X1 (the capture guard has no key-assignment rule).

## 1. PREMISE, re-measured (20:3xZ)

| # | Premise line | Measured now | Verdict |
|---|---|---|---|
| P0 | origin tip; every named file unchanged from the PIN | origin = 5eda746; `git diff --stat 37f720a HEAD` over proofs/S0-04, the S0-04 test, test_proof_status, check-proof-status, proof-runner, validate-ledger, ledger-gen, proofs/ledger.json, registry, schemas, docs/governance, the ledger: only `todo/BUILD-TASKLIST.md` (+6, the ledger, outside my boundary) | holds |
| P1 | `sed -n 75,86p` check_compression.py: the four rules, `sk-key` and `key-assignment` anchored on `\b` | identical lines | holds |
| P2 | `LEAK_PATTERNS` at :80, `_leak_hit` at :98, callers :108 and :173 | identical | holds |
| P3 | capture_leg.py:46 `LEAK_RE = ...\bsk-...`, used at :54 | identical | holds |
| P4 | the sibling sweep: 6 lines (S0-01:150, :153; S0-04:81, :82, :84; capture_leg:46) | the command as typed in the brief prints 3 lines (S0-04:82, :84, capture_leg:46): its `bearer\\\\s` matches two literal backslashes. With `bearer\\s` it prints the premise's 6 lines exactly; S0-01 unchanged since the PIN | holds (DISCREPANCY D1: the recorded command's escaping, not the code) |
| P5 | attestation: 44 entries, the checker attested, tools/ = capture_leg.py, run_s0_04_legs.sh | same; every one of the 44 hashes equals the working-tree file's sha256 | holds |
| P6 | classification execution_proof, recorded_at 2026-09-22T04:31:52.985441Z, env sandbox:vm | same | holds |
| P7 | `accepted/S0-04` -> fa20942; result.json identical at fa20942 and HEAD | `object fa20942e4dc792745c9a8338b3cfcae8d34c8779`; rc=0 | holds |
| P8 | `docs/governance/tags/accepted-S0-04.tag` exists; 0 `PROOF-ANCHOR` lines in the ledger | same (0) | holds |
| P9 | `check-proof-status.py .` rc 0; `PENDING_ANCHOR` :85, stale :136, changed-since :178 | rc=0; the same three lines | holds |
| P10 | test_summary, short basetemp: `112 passed`, `2 files set=2fa20f3af1f3` | `pytest-summary: 112 passed in 9.40s` (basetemp `/tmp/s4l/bt`); set id by pc_suite.sh:46's formula computed inline (the classifier refused running pc_suite.sh itself, the bridge launcher): `2fa20f3af1f3` | holds |
| P11 | S4H landing a815883 2026-09-22 04:34:30; recipe = proof-runner, validate-ledger integrity, ledger-gen | same commit; the grep prints 3 recipe lines (the brief shows 2: `validate-ledger integrity ... PRESENT` omitted) | holds (trivial) |
| P12 | SCRUB1 decision line 83: S1 `(?<![A-Za-z0-9])` | same line | holds |
| P13 | capture_leg last change be6be79 2026-09-19 13:19:43; evidence 5e2a541 2026-09-19 14:22:21 | same | holds |

Verdict: the premise holds. No CONTRACT-INVALID. The long-basetemp false red (9 failed) was not re-run: it is a documented
quirk, not a premise this lane depends on.

## 2. Contract item 1: which left anchor, by measurement (20:4xZ)

Instrument (scratch, not committed): `<scratch>/s004leak/instr.py` builds each candidate from the PIN's OWN rule text (it
asserts the PIN shapes first: `sk-key` == `\bsk-[A-Za-z0-9_-]{8,}`, `key-assignment` starts `(?i)\b(?:api`, `LEAK_RE` ==
`(?i)bearer\s+\S|\bsk-[A-Za-z0-9_-]{8,}`, and that the PIN candidate recompiles to exactly the PIN patterns), then
evaluates a text under every candidate: hit or not per rule, the masked shape of every match a candidate takes at a
position the PIN's rule does not ("new"), and the count the PIN takes that the candidate does not ("lost"). It never
stores or prints a text or a matched span. Shapes read `<class 2 before><class 1 before>|<literal>|len<value>|<value
classes>|word=<the whole word, only when it is on a fixed list of ordinary words>` (classes: U underscore, L ASCII
letter, D digit, N non-ASCII letter/digit, P other, ^ start).

Candidates (only the left anchor of the three anchored rules differs; bearer, hex64 and the trailing `\b` unchanged):
PIN `\b` · **S1** `(?<![A-Za-z0-9])` (SCRUB1's choice, the AF-AP-224 row's fix shape) · S1u `(?<![^\W_])` (`\b` minus
the underscore, every Unicode letter/digit refused) · S2 no left anchor.

Corpora and commands:
```
# the real evidence and every fixture, file by file, as the checker screens them (fingerprint masked)
# + the test corpus: every text the existing S0-04 tests put through either screen, logged by instrumented
#   SCRATCH copies of the two tools (git archive of HEAD; the verdict path still the PIN's; 79 passed there)
$ python3 <scratch>/s004leak/instrument.py <scratch>/s004leak/tree
$ (cd <scratch>/s004leak/tree && python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/s4l/bt1 tests/test_s0_04_compression.py)
79 passed in 13.79s                         (643 screened texts logged)
$ python3 <scratch>/s004leak/measure.py . <scratch>/s004leak/corpus.jsonl 'proofs-other=proofs/S0-0[1-35-9]/**/*' \
    'proofs-other-1x=proofs/S0-1[0-2]/**/*' 'transcripts=transcripts/sandbox/*.md' 'code-scripts=scripts/*.py' \
    'code-src=src/**/*.py' 'code-tests=tests/*.py'
```

**S0-04's own corpora (the ones the contract names). Cell = texts hit (new vs PIN / lost vs PIN).**

| Corpus | Texts | checker sk-key: PIN · S1 · S1u · S2 | checker key-assignment: PIN · S1 · S1u · S2 | capture sk: PIN · S1 · S1u · S2 |
|---|---|---|---|---|
| real evidence `proofs/S0-04/evidence` | 7 files, 163,028 chars | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 |
| fixture evidence-pass | 7 files | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 |
| fixture evidence-header-missing | 7 files | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 |
| fixture evidence-body-diff | 7 files | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 |
| fixture request-baseline.json | 1 | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 |
| fixture request-large.json | 1 | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 |
| test corpus, `_screen_tree` (bundle files) | 505 | 4 · 4 · 4 · 4 (0/0 each) | 1 · 1 · 1 · 1 (0/0) | 4 · 4 · 4 · 4 (0/0) |
| test corpus, `_redact` (reason and observation lines) | 113 | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 |
| test corpus, `_leak_hit` direct (fixtures test) | 23 | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 |
| test corpus, capture `safe()` | 2 | 1 · 1 · 1 · 1 (0/0) | 0 · 0 · 0 · 0 | 1 · 1 · 1 · 1 (0/0) |

The real evidence stays free of hits under every candidate: no leak and no false positive to report there. On the
test corpus no candidate changes any existing test's verdict (0 new, 0 lost): the PIN's hits are the existing leak
tests' own fake keys, which every candidate takes.

**Bystanders (never screened by S0-04; the false-positive profile of each anchor).** New vs PIN:

| Corpus | Size | S1 | S1u | S2 |
|---|---|---|---|---|
| proofs S0-01..S0-09 except S0-04 (every file) | 796 files, 34.8 MB | 0 | 0 | 0 |
| proofs S0-10..S0-12 | 18 files | key-assignment 1 file, 2 positions | same as S1 | same as S1 |
| transcripts/sandbox digests | 18 files, 3.49 MB | 0 | 0 | sk 3 (task x2, disk) |
| scripts/*.py | 39 files | 0 | 0 | sk 7 positions (task) |
| src/**/*.py | 13 files | 0 | 0 | sk 1 (flask), key-assignment 1 (letter-glued passwd) |
| tests/*.py | 108 files | key-assignment 13 files, 32 positions, every one an underscore-glued name with a value (`..._TOKEN`, `..._API_KEY`, `..._APIKEY`, `..._PASSWD`): the suites' own fake credentials | same as S1 | sk 106 positions (task 45+, mask, desk, flask, disk, ask) + letter-glued password/passwd/secret |

The two S0-10..S0-12 positions, classified (name side and masked value only): `proofs/S0-11/check_eval_hardening.py:71`
`"OMNIROUTE_INTERNAL_API_KEY": "<value len26>"` sits inside `DECOY_CREDENTIALS` (:70), a committed decoy, not a secret;
`:367` `_CHMOD_SYM_TOKEN = re.compile(...)` is code (the value is `re.compile`), a false positive of the rule shape.

**Decision: S1, `(?<![A-Za-z0-9])`, on the three anchored rules: checker `sk-key`, the NAME side of checker
`key-assignment` (its trailing `\b` unchanged), capture `LEAK_RE`'s `sk-` alternative.** `bearer` (no left anchor) and
`hex64` (hex-class lookarounds: `_` already counts as a separator) are already right and stay byte-identical.
- On S0-04's corpora all four candidates tie (0 hits on the evidence and the fixtures, 0 changed verdicts in the tests),
  so the contract decides: S2 is refused by definition (it does not refuse a letter before the key) and by the
  bystanders (ordinary words in every text corpus: task, disk, flask, mask, desk, ask).
- S1 and S1u never differ on any corpus (no non-ASCII letter sits before a rule prefix anywhere measured). S1 is the
  registry row's fix shape and the scrubber's anchor (SCRUB1), so both screens keep one rule shape. The one semantic
  difference: S1 also takes a key glued after a NON-ASCII letter (`ésk-...`), where S1u and the PIN refuse it; that is
  the protective direction, and it is recorded here, not tested (0 instances).
- The cost S1 adds, measured on bystanders only (0 on S0-04's corpora): an underscore-glued name that is not a
  credential, followed by `=` or `:` and an 8+ character value (`_CHMOD_SYM_TOKEN = re.compile`), now fails the
  key-assignment rule. S0-04 bundles hold JSON evidence, not code; a future capture carrying such a field fails the
  checker loudly with the rule named (fail closed), never silently.

## 3. What changed (20:4xZ)

- `proofs/S0-04/check_compression.py`, inside `LEAK_PATTERNS` only: `sk-key` and the name side of `key-assignment` take
  `(?<![A-Za-z0-9])` in place of the leading `\b`; the trailing `\b` after the key name, `bearer` and `hex64` are
  byte-identical; a three-line comment inside the tuple says why and names AF-AP-224 (the comment block above the
  tuple says nothing about the anchor, so nothing there became false).
- `proofs/S0-04/tools/pc/capture_leg.py`, `LEAK_RE` only: the `sk-` alternative takes `(?<![A-Za-z0-9])`; the
  `bearer` alternative is byte-identical. One line; no comment added (the line above LEAK_RE is outside the symbol).

Impact (before the edit): GitNexus `impact LEAK_PATTERNS` and `impact LEAK_RE` read risk UNKNOWN, 0 callers (module
constants, no edges recorded; index 2 commits behind), so confirmed by text search: `LEAK_PATTERNS` is read only by
`_leak_hit` (`impact _leak_hit`: LOW, direct `_redact` and `_screen_tree`); `LEAK_RE` only by `safe` (`impact safe
--uid Function:proofs/S0-04/tools/pc/capture_leg.py:safe`: LOW, direct `main`). Every file that names either tool: the
two tools, `run_s0_04_legs.sh` and `spec.json` (both run them as CLIs), `tests/test_s0_04_compression.py`, and
`tests/test_edit_snapshot_ap_screen.py:1132`, which only copies the old rule line as a literal string for the
AF-AP-224 screen's own test (it does not read the file; not affected).

Semantic check on the edited files (fake values built with `secrets.token_hex` at run time; shapes masked):
```
x_<sk-fake>                    checker=sk-key          capture_withheld=True
mcp__srv__<sk-fake>            checker=sk-key          capture_withheld=True
OMNIROUTE_API_KEY=<hex32>      checker=key-assignment  capture_withheld=False   <- see DEVIATION X1
task-<hex32> / risk-<hex32> / disk-<hex32>          checker=None  capture_withheld=False
x-api-key-id: <hex32> / /run/secrets/OMNIROUTE_API_KEY_FILE / "nextPageToken": "<hex32>"   checker=None  withheld=False
9<sk-fake>                     checker=None            capture_withheld=False   (a digit before still refuses)
$ python3 proofs/S0-04/check_compression.py proofs/S0-04/evidence                          -> PASS ... rc=0
$ python3 proofs/S0-04/check_compression.py proofs/S0-04/fixtures/evidence-header-missing  -> failure_reason: off: compression-header-missing rc=1
```

**DEVIATION X1 (flagged; the coordinator decides): the capture guard does not refuse the `<PREFIX>_API_KEY=<value>`
shape, under the PIN or under this fix.** `LEAK_RE` has two alternatives only (bearer, `sk-`); it has no key-assignment
rule to re-anchor. Contract item 1 changes anchors; item 2 asks that "the capture tool's guard refuses the same shapes".
With a non-`sk-` value the guard can refuse the assignment only if a new alternative is ADDED to `LEAK_RE`; with an
`sk-` value the PIN already refuses it (the `=` is a boundary), so no such test can red on the PIN. Adding a rule is
not an anchor change, and my standing rules say report an adjacent gap rather than fix it, so I did not add it. The
capture half of item 2 is done for the glued-key shapes (`_`, `__`), which red on the PIN (section 4). Why it matters:
the one capture-tool message that can carry file content is a PyYAML error from `--config` (`main`'s catch-all prints
`safe(f'{type(exc).__name__}: {exc}')`), and the live Hermes profiles hold an inline `api_key`
(`capture_leg.provider_block`'s docstring). Measured with a run-time fake value (PyYAML 6.0.1): an error on another
line carries no value (2 of 2 cases); an error ON the `api_key` line does: an unclosed quote prints `api_key: "<value>`
(name and whole value), a tab indent prints the name and a 22-character prefix, a colon after the value prints
`... <value>: x` (the value, the name cut off at the left). A non-`sk-` key in any of these reaches the PC's stderr
under the PIN and under this fix. The option, if wanted: append
`|(?<![A-Za-z0-9])(?:api[_-]?key|apikey|secret|password|passwd|token)\b\s*["']?\s*[:=]\s*["']?[A-Za-z0-9_\-.+/]{8,}`
to `LEAK_RE` (the checker's rule), plus the assignment case in the capture tests. It would withhold the first two
cases, not the third (no name in the message); only a value check (SCRUB1's known-values gate) covers that one. It
changes the attested bytes again, so it belongs in this re-mint or needs another.

## 4. Contract item 2: tests, red on the PIN, then mutation (20:5xZ)

`tests/test_s0_04_compression.py`: `import secrets`, then 19 new test cases (6 functions) beside their siblings; every
key and value is built at run time with `secrets.token_hex(16)` (`sk-` + 32 hex, or 32 hex), never a literal.
- Checker (after `test_a_second_hex64_still_fails`, the existing credential-screen tests' pattern: a copy of the
  passing bundle, one field added to `off/request.json`, the real CLI):
  `test_a_key_glued_after_an_underscore_fails_the_checker[x_ | mcp__srv__]` and
  `test_a_prefixed_api_key_assignment_fails_the_checker[OMNIROUTE | OPENAI | HERMES_PROVIDER]` assert rc 1 and the
  WHOLE output equal to the one exact line the checker emits for a leak,
  `failure_reason: credential-in-evidence: off/request.json matches sk-key` (or `... matches key-assignment`), and
  that the fake value is not echoed. `test_ordinary_text_passes_the_checker` x6 (`task-<hex>`, `risk-<hex>`,
  `disk-<hex>`, the key `x-api-key-id`, `/run/secrets/OMNIROUTE_API_KEY_FILE`, the key `nextPageToken`) asserts rc 0
  and the PASS line.
- Capture tool (after `test_capture_leg_error_messages_never_echo_a_credential`):
  `test_capture_leg_withholds_a_key_glued_after_an_underscore[x_ | mcp__srv__]` drives the REAL CLI
  (`capture_leg.py --max-seq --record-dir <tmp>/absent/<glue><fake key>`): `max_seq` raises "record dir not found:
  <path>", `main`'s handler prints it through `safe()`; the test asserts rc 1, stderr exactly
  `capture_leg: <message withheld: credential-shaped>`, and no key tail anywhere.
  `test_capture_leg_passes_ordinary_text_through` x6 asserts `safe(text) == text` for the same six ordinary texts.
- `nextPageToken` is my addition to the brief's ordinary list (flagged): none of the brief's five discriminates the
  key-assignment rule's name anchor (`x-api-key-id` and `_API_KEY_FILE` pass under every candidate, the trailing `\b`
  and the `[:=]` refuse them), so the "widen to no anchor" mutant of that rule needed a letter-glued name with a value
  to die on. `nextPageToken` is a real API field name (a pagination cursor, not a credential).

**Red run on the PIN's rules** (`<scratch>/s004leak/red`: `git archive 37f720a` of proofs/S0-04 and the test inputs,
the new test file copied in; `cmp` proves both tools are the PIN's bytes):
```
$ (cd <scratch>/s004leak/red && python3 -m pytest -q -p no:cacheprovider -rf --basetemp=/tmp/s4l/bt3 tests/test_s0_04_compression.py)
FAILED ...::test_a_key_glued_after_an_underscore_fails_the_checker[x_]
FAILED ...::test_a_key_glued_after_an_underscore_fails_the_checker[mcp__srv__]
FAILED ...::test_a_prefixed_api_key_assignment_fails_the_checker[OMNIROUTE]
FAILED ...::test_a_prefixed_api_key_assignment_fails_the_checker[OPENAI]
FAILED ...::test_a_prefixed_api_key_assignment_fails_the_checker[HERMES_PROVIDER]
FAILED ...::test_capture_leg_withholds_a_key_glued_after_an_underscore[x_]
FAILED ...::test_capture_leg_withholds_a_key_glued_after_an_underscore[mcp__srv__]
7 failed, 91 passed in 4.33s
```
Why each fails there (the `--tb=line` output, fake values masked): the five checker tests at `assert code == 1`:
`assert 0 == 1`, the PIN checker printed its observations and `PASS: S0-04 compression-contract - 3 assertions over 3
legs` over a bundle holding the fake key or assignment (the exact reason: the leak passed the screen); the two capture
tests at the stderr assertion: stderr was `capture_leg: record dir not found: <tmp>/absent/x_sk-<fake32>` (and
`mcp__srv__sk-<fake32>`), the fake key printed (the exact reason). The 12 ordinary-text cases pass on the PIN, as they
must: the PIN takes no ordinary text, so they cannot red there. **Deviation (flagged): "each new test reds on the PIN's
rules" holds for the 7 leak cases, not for the 12 ordinary-text controls;** their red state is the over-wide anchor,
shown by mutants M4 to M6 below.

Fixed tree, the new cases alone: `19 passed, 79 deselected in 0.71s` (`-k 'glued or prefixed or ordinary'`).

**Mutation pass** (`<scratch>/s004leak/mutate.py` on `<scratch>/s004leak/mut`, a `git archive HEAD` copy with the three
working-tree files; AF-AP-223 rules: the unmutated control runs first and must be green, KILLED only when a test
FAILED and is named, an error-only or empty run is INVALID, each mutant's anchor text must occur exactly once):
```
CONTROL (unmutated): rc=0 98 passed in 4.42s
M1 checker sk-key anchor back to \b: KILLED (2 failed: test_a_key_glued_after_an_underscore_fails_the_checker[mcp__srv__], [x_])
M2 checker key-assignment name anchor back to \b: KILLED (3 failed: test_a_prefixed_api_key_assignment_fails_the_checker[HERMES_PROVIDER], [OMNIROUTE], [OPENAI])
M3 capture sk anchor back to \b: KILLED (2 failed: test_capture_leg_withholds_a_key_glued_after_an_underscore[mcp__srv__], [x_])
M4 checker sk-key no anchor: KILLED (3 failed: test_ordinary_text_passes_the_checker[stray_note-disk-{}], [stray_note-risk-{}], [stray_note-task-{}])
M5 checker key-assignment no anchor: KILLED (1 failed: test_ordinary_text_passes_the_checker[nextPageToken-{}])
M6 capture sk no anchor: KILLED (3 failed: test_capture_leg_passes_ordinary_text_through[stray_note-disk-{}], [stray_note-risk-{}], [stray_note-task-{}])
M7 checker sk-key lets a digit glue: SURVIVED (98 passed in 4.25s)
M8 checker key-assignment lets a digit glue: SURVIVED (98 passed in 4.67s)
M9 capture sk lets a digit glue: SURVIVED (98 passed in 4.45s)
TOTAL {'KILLED': 6, 'SURVIVED': 3, 'INVALID': 0}
```
The six mutants the brief names (restore each old anchor alone; widen each new anchor to none) are all KILLED by named
FAILED tests. M7 to M9 are beyond the brief and survive by design, as SCRUB1's M16 did: the code refuses a digit
before the key (the contract's words; the semantic check above: `9<sk-fake>` -> `checker=None`), but no test pins it,
because a pinning test would assert that a key glued after a digit passes a credential screen. Measured cost either
way: 0 digit-glued shapes on S0-04's evidence, fixtures and every non-test bystander; 3 in other suites' test files,
each inside a long opaque run (`tests/test_decisions_canonical.py:1346` in `ghjlmqfu01235678`,
`tests/test_transcript_export.py:211` in `QZJ8QZJ8token`, `tests/test_transcript_export.py:219` in `QZJ8QZJ8QZJ8SECRET`).

## 5. Contract item 3: the re-mint (20:5xZ)

Recipe: the S4H landing's (a815883): the runner on this sandbox venue, then the ledger integrity check, then the ledger
regeneration. Safety first, because a failing runner DELETES `result.json` by design: a dry run in a scratch `git
archive` of the attested closure (proof-runner, validate-ledger, registry, schemas, proofs/S0-04) plus my two files:
`dry proof-runner rc=0`, only the two files' attestation entries changed (44 entries both sides), runs changed only in
their timestamps, negative control identical.

Controls before the real run:
```
# the edited tools against the OLD result.json: the binding catches it (the gate's negative control)
$ python3 scripts/validate-ledger integrity --root .
S0-04 INVALID ... execution_proof numerator=8 denominator=9
attestation-mismatch: S0-04 proofs/S0-04/check_compression.py
integrity rc=1
# ledger-gen over a pristine git archive of HEAD (proofs/ + the closure) reproduces the committed ledger
$ python3 <copy>/scripts/ledger-gen --root <copy> --output <scratch>/ledger/head-regen.json   -> rc 0
$ cmp <scratch>/ledger/head-regen.json <(git show HEAD:proofs/ledger.json)                  -> identical
```
(My first attempt at that control omitted `scripts/proof-runner` from the archive, so every proof read
`attestation-mismatch ... scripts/proof-runner`: my instrument's error, redone with the full closure.)

The re-mint, in the repo (20:51:59Z):
```
$ python3 scripts/proof-runner run --proof S0-04 --venue sandbox --root .
proof-runner rc=0
$ python3 scripts/validate-ledger integrity --root .
S0-01 PRESENT ... S0-04 PRESENT ... S0-12 PRESENT (all twelve PRESENT)
conformance_checked_decision numerator=3 denominator=3
execution_proof numerator=9 denominator=9
integrity rc=0
$ python3 scripts/ledger-gen --root .
  -> REFUSED by the session's permission classifier ("Modify Shared Resources"); not retried.
$ python3 scripts/ledger-gen --root . --output <scratch>/ledger/remint-regen.json     (the same tool, scratch output)
ledger-gen: wrote .../remint-regen.json (12 proofs)   rc=0
```
**NOT DONE in the tree: `proofs/ledger.json` is unchanged from HEAD** (the in-tree write was refused, section 9). The
coordinator runs `python3 scripts/ledger-gen --root .` at landing; the expected result is the scratch file, whose one
difference from the committed ledger is:
```
$ diff <(git show HEAD:proofs/ledger.json) <scratch>/ledger/remint-regen.json
23c23
<       "normalized_digest": "74fd294ad3ad8ee39b7d959402b377b1ff7ddfc956ce6ec2495e0ec2fbc6d666",
---
>       "normalized_digest": "5b49bfb5cb33a1ea5361622a83fc04bdd1013506d67ab405e7b1c6fbac271c04",
```
(line 23 is S0-04's entry; the state stays PRESENT; every other proof's line is identical.)

**`proofs/S0-04/result.json`, field by field (HEAD vs re-minted): 71 leaf fields, 63 identical, 8 changed.**

| Field | Old (HEAD, 2026-09-22 S4H mint) | New | Why |
|---|---|---|---|
| `attestation["proofs/S0-04/check_compression.py"]` | fa39bb78c7d589cc678af163075393244ec5ab7894e8a9917ac4af5363610981 | 881710af6818ee0dfb695f5b96fc5b60262c04d6914493d62c3c613ac12ea090 | the edited checker (= its sha256 now) |
| `attestation["proofs/S0-04/tools/pc/capture_leg.py"]` | 1d4234c1b39ca8594f54ccf0f8b7007c2aa23c61646b33ab1faffc23a21ba908 | 7b202db013aa597a67a4f0fb151afa11cc409efb015c7e604fb30c8c6f9eb7eb | the edited capture tool (= its sha256 now) |
| `recorded_at` | 2026-09-22T04:31:52.985441Z | 2026-09-25T20:51:59.316128Z | volatile (stripped by normalization) |
| `runs[0].started_at` / `finished_at` | 04:31:52.903034Z / .945057Z | 20:51:59.203373Z / .264970Z | volatile |
| `runs[1].started_at` / `finished_at` | 04:31:52.945268Z / .984881Z | 20:51:59.265172Z / .315284Z | volatile |
| `digest` | abc00645c2d8a24153be614690c3a747fd0c5677435d6a1d5d8d6cef7358ca98 | 5fe687a29691b64571a4cb794a55f648bec5d1f1baf646252fbc08d4ebd50d05 | sha256 of `runs`, which carry the timestamps (volatile) |

Identical: `proof_id`, `classification` (execution_proof), `env_fingerprint` (sandbox:vm), the other 42 attestation
entries, both runs' `leg`, `cmd`, `exit_code` (0 and 1), `stdout_sha256` and `stderr_sha256` (the checker's output is
byte-identical: the positive leg still prints the same three observations and `PASS: S0-04 compression-contract - 3
assertions over 3 legs`), the negative run's `failure_reason` (`failure_reason: off: compression-header-missing`), and
`negative_control`. So the result stays PASS for the same assertions, and the only changed attestation entries are
the two changed files' hashes.

The ledger line follows from those two hashes and nothing else: with ledger-gen's own `_normalized_digest` and the
committed `proofs/normalization.yaml`, old -> `74fd294a...`, new -> `5b49bfb5...`, and the new result with the two old
hashes put back -> `74fd294ad3ad8ee39b7d959402b377b1ff7ddfc956ce6ec2495e0ec2fbc6d666`, the old value exactly.

## 6. Contract item 4: the two anchor states, proved in a scratch clone (21:0xZ)

Venue: a throwaway clone, `git clone --local --no-checkout` of this repo into `<scratch>/s004leak/anchor` (objects
hardlinked, about 7 MB real), sparse checkout of what `scripts/check-proof-status.py` reads (the ledger,
`docs/governance/`, every `proofs/*/result.json`), at HEAD 58a9c6f (HEAD moved from 5eda746 during the lane: four
coordinator commits, D-092/D-093, none in my boundary or the attestation closure). The checker is the repo's,
unchanged: `python3 scripts/check-proof-status.py <clone>`. Script: `<scratch>/s004leak/anchor_states.sh`.

```
== a0 CONTROL: the clone at HEAD, nothing changed (the premise's rc 0)
   ref accepted/S0-04: present | tag file: present | PENDING line: 0 | result.json: HEAD
   rc=0
== a: AS THE TREE STANDS (the re-minted result.json, the old tag ref and tag file)
   proof-status: S0-04: the minted proofs/S0-04/result.json changed since accepted/S0-04 (regenerated after acceptance) — re-accept with a new signed tag (AF-AP-56)
   rc=1
== b: tag file removed, local ref absent, PENDING line (working tree)
   proof-status: WARNING S0-04: ACCEPTED with the anchor PENDING the owner's signed tag accepted/S0-04 (declared in the ledger) — not owner-verifiable yet
   rc=0
== b COMMITTED: the committed tag object removed, the local ref absent, the PENDING line committed
   (throwaway commit in the clone; committed tree: 0 tag-file entries; PENDING lines in HEAD: 1)
   proof-status: WARNING S0-04: ACCEPTED with the anchor PENDING the owner's signed tag accepted/S0-04 (declared in the ledger) — not owner-verifiable yet
   rc=0
```
Each of (b)'s three conditions is necessary (one condition dropped at a time, each rc 1):
```
== b-1: tag file removed + PENDING line, the local ref still present
   proof-status: S0-04: the tag accepted/S0-04 exists but the ledger still declares PROOF-ANCHOR PENDING — a stale declaration (remove it)
   proof-status: S0-04: the minted proofs/S0-04/result.json changed since accepted/S0-04 (regenerated after acceptance) — re-accept with a new signed tag (AF-AP-56)
== b-2: local ref absent + PENDING line, the tag file still present (the checker imports the committed object)
   proof-status: S0-04: the tag 1ec6cd4aa7a16ef21393e88658cd3bec0c6f7faf exists but the ledger still declares PROOF-ANCHOR PENDING — a stale declaration (remove it)
   proof-status: S0-04: the minted proofs/S0-04/result.json changed since 1ec6cd4aa7a16ef21393e88658cd3bec0c6f7faf (regenerated after acceptance) — re-accept with a new signed tag (AF-AP-56)
== b-3: local ref absent + tag file removed, no PENDING line
   proof-status: S0-04: ACCEPTED but no signed tag accepted/S0-04 and no visible `PROOF-ANCHOR: S0-04 = PENDING-OWNER-TAG` declaration — an acceptance the owner cannot verify (AF-AP-32)
```
The PENDING line used (modelled on the S0-11 precedent at cd832e9, placed directly under `PROOF-STATUS: S0-04 =
ACCEPTED`; the coordinator owns the final wording):
`PROOF-ANCHOR: S0-04 = PENDING-OWNER-TAG (requested 2026-09-25 — the owner's GPG-signed tag `accepted/S0-04` on a commit
holding the re-minted proofs/S0-04/result.json (S0-04-LEAK, D-091) makes this acceptance owner-verifiable again;
procedure in docs/governance/README.md; check-proof-status.py reports this state as a WARNING, never as verified)`

**The landing, modelled whole, and what it leaves red.** I widened the clone to the full landing (my two tools, the
re-minted result, the regenerated ledger from section 5, the tag file removed, the PENDING line; two throwaway commits)
and ran the gates there:
```
$ python3 scripts/validate-ledger integrity --root .      -> S0-04 PRESENT, execution_proof numerator=9 denominator=9, rc=0
$ python3 scripts/ledger-gen --root . --output <tmp>       -> byte-identical to the ledger I hand over (section 5)
$ python3 scripts/check-proof-status.py .                  -> the WARNING above, rc=0
$ python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/s4l/btc tests/test_proof_status.py
FAILED tests/test_proof_status.py::test_committed_tree_anchor_state_is_the_declared_pending_one
E   AssertionError: assert 'WARNING' not in 'proof-statu...fiable yet\n'
E     'WARNING' is contained here: proof-status: WARNING S0-04: ACCEPTED with the anchor PENDING ...
1 failed, 32 passed in 5.29s
```
**DISCREPANCY D3 (for the coordinator, before landing): state (b) turns two of the three by-design reds green, not the
third.** `tests/test_proof_status.py:463-479` asserts `"WARNING" not in completed.stderr` (:477) whenever S0-11's anchor is
present, so ANY proof's pending warning reds it, S0-04's included. Its docstring says the intent is "no S0-11 warning".
CI clones without tags and reads the committed tag objects, so after a (b) landing CI stays red on this one test until
the owner re-signs (and push_clean's CI gate refuses while it is red); after an (a) landing, three tests are red.
Outside my boundary, not changed. The one-line option: `assert "WARNING S0-11" not in completed.stderr` (the
docstring's own claim).

## 7. The brief's question: does attesting the new capture-tool bytes over the old evidence stay honest? (21:0xZ)

**Answer: yes; no new live capture is needed for this change.** From the spec, the runner and the checker, with the
decisive claim verified mechanically:
1. **The spec never runs the capture tool.** `proofs/S0-04/spec.json` has two legs, both the checker: positive over
   `proofs/S0-04/evidence` (exit 0), negative over `fixtures/evidence-header-missing` (exit 1,
   `compression-header-missing`). The seed's S0-04 block (`seeds/seed-stage0-v1.yaml:406-422`) grades the captured
   request, response and upstream record; it names no capture-tool bytes.
2. **The runner attests the tool because it lives in the proof directory, not because it made the evidence.**
   `proof_attestation` hashes `proofs/S0-04/**` by rglob (plus the closure); the result has no provenance field that
   names which tool bytes produced the evidence. It binds the minted result to the tree at mint time.
3. **The checker is re-proven by the re-mint itself.** Both legs ran the NEW checker: the positive leg's stdout is
   byte-identical (`stdout_sha256` unchanged) and the negative leg's reason is unchanged (section 5).
4. **The capture-tool change cannot reach an evidence byte** (`<scratch>/s004leak/capture_equiv.py`, run on the PIN
   and the fixed `capture_leg.py`):
   ```
   1. AST equal once LEAK_RE's pattern is masked: True   (and unequal unmasked, so the check can see a difference: True)
   2. LEAK_RE read in: ['safe'] | safe() called at: [('main', 'inside except handler', 304), ('main', 'inside except handler', 307)]
   3. modes: capture, --config, --find-record, --max-seq all rc 0 under both versions, with safe() replaced by a tripwire that raises
      stdout identical per mode: [True, True, True, True]
      files written: config/hermes-provider.json, off/request.json, off/response.json, off/upstream-record.json
      every written file byte-identical between the PIN and the fixed version: True
   ```
   (capture mode ran against a local responder on 127.0.0.1: an equivalence probe between two tool versions, not a
   capture. My first run read False because I gave each version its own out directory, which `request.json` records in
   `argv`; with one out directory for both: True.) The PC runner (`run_s0_04_legs.sh:140-148`) branches only on the
   tool's exit codes and reads only `--max-seq`'s stdout; `safe()`'s text goes to stderr and nothing parses it. So the
   committed evidence is exactly what the new bytes would write from the same inputs.
5. **What stays open, unchanged by this lane:** the attestation never proved which tool bytes captured the evidence.
   That is issue #7's F7 (capture provenance, the doc says `/tmp/s0-04-cap2`), which D-034 already schedules with F2
   for the next PC re-capture. This lane does not widen it: the changed line is unreachable on every evidence path.

So I did not stop for a capture.

## 8. Contract item 5: sibling leak screens (reported, not fixed) (21:0xZ)

Sweep: every compiled credential-shaped pattern in `proofs/`, `scripts/`, `src/`, `harness-ports/` (a `re.compile(`
line grep for bearer, sk-, api key, secret, passw, token, ghp, AIza, xox, 64-hex, authorization, credential, private
key: 40 lines), the rule tables that compile strings elsewhere (`src/agent_factory/decisions/volatile.py`), and the
shell scripts' grep/sed screens. Each probed with run-time fakes where it matters.

| Where | What it screens | The AF-AP-224 shape (`\b` refuses `_`-glue)? | Finding |
|---|---|---|---|
| `proofs/S0-01/check_acp_conformance.py:153` `_STDERR_LEAK_RE`, used at :1554 | the negative leg's `agent-stderr.txt` | no (no left anchor) | **gap, signed proof**: rules are only 64-hex, `bearer\s`, `token[=:]\S`. Probed: a bare `sk-` key, a glued one, `OMNIROUTE_API_KEY=<value>`, `password=<value>`, `token = <value>`, `"token": "<value>"` all pass; only `MY_TOKEN=<value>` is caught. The `token` rule assumes `=`/`:` right after the name (AF-AP-224's family: the pattern written for one context) and no `sk-` or key-name rule exists |
| `proofs/S0-01/check_acp_conformance.py:149` `_SENSITIVE_HEADER_NAME_RE`, at :642 | upstream record header NAMES | no | gap (family): `x_api_key` and `apikey` pass (only `api-key` with a hyphen); `apikey` is a real header name at some providers |
| `proofs/S0-01/check_acp_conformance.py:150` `_SENSITIVE_HEADER_VALUE_RE`, at :644 | upstream record header VALUES | no (no anchor, no length floor) | over-wide, not a leak gap: takes `x_<sk-fake>` and also `task-queue` (any value holding `sk-`); a false positive fails loud |
| `proofs/S0-01/check_acp_conformance.py:146` `_HEX64_ANYWHERE_RE` | log values | no | no gap of this class |
| `proofs/S0-01/tools/acp_probe.py:36` `_REDACTED_ENV_KEY_RE` | env NAMES to redact | no (substring) | takes glued names; no gap of this class |
| `proofs/S0-11/fixtures/neg_credential_read.py:27` `CRED_SHAPE` | a hostile fixture's idea of a credential env name | mirror image: it REQUIRES `_` before the name (`_API_KEY$`, `_TOKEN$` ...) | a bare `API_KEY`, `TOKEN` or `SECRET` env name is not attacked; the negative control is narrower than it could be (signed proof, a fixture) |
| `scripts/transcript_export.py:84-87` (SCRUB1) | transcript digests | fixed to `(?<![A-Za-z0-9])` | the right side stays open (task #292, AF-AP-224 row) |
| `scripts/session_export.py`, `harness-ports/bin/hermes-session-export.py`, `harness-ports/bin/qwen_matrix.py` | exports | use transcript_export's rules | inherit SCRUB1's fix; no own shape rule |
| `src/agent_factory/decisions/volatile.py:84-89` `_FORMS` | decision-record redaction | no: `sk-` head unanchored; `token` head `(?:\b\|(?<=_))token` accepts `_` | no gap of this class (over-redacts ordinary words by design) |
| `scripts/t93r1_apply_profile.sh:58` sed `(key_env|api_key|token|secret)` | the script's own appended profile block, printed | no (no anchor) | narrow name list (key_env, api_key, token, secret): a `password:` or `Authorization: Bearer` line would print; low exposure, the block is the script's own text |
| `scripts/known_values_check.py:31` `TOKENISH` | known secret VALUES | n/a (value windows, not shapes) | none |

Not screens (parsers or digest shapes): `proofs/S0-03/tools/pc/direct_responses_probe.py:72` and
`proofs/S0-04/tools/pc/capture_leg.py:43` (key-file line parsers), `proofs/S0-01/tools/pc/pc_launch.py:41`,
`proofs/S0-02/tools/build_fixtures.py:89`, `proofs/S0-08/check_containment.py:197`, `scripts/ci_gate.py:70`,
`scripts/ship_to_pc.py:54-55`, `scripts/jev_pipes/accounting.py:23`. Outside the four trees and not ours:
`.agents/skills/autoskill/scripts/redact.py` (vendored; already in the AF-AP-224 row).

## 9. Gates, pasted (21:0xZ)

`bash scripts/test_summary.sh --basetemp=/tmp/s4l/bt tests/test_s0_04_compression.py tests/test_proof_status.py`
(parent `/tmp/s4l` created first; set id by `scripts/pc_suite.sh:46`'s `set_id` formula, computed inline):
```
run 1: pytest-exit: 1
       pytest-summary: 3 failed, 128 passed in 10.05s
       2 files set=2fa20f3af1f3
run 2: pytest-exit: 1
       pytest-summary: 3 failed, 128 passed in 10.65s
       2 files set=2fa20f3af1f3
```
The 3 failures, read by assertion (both runs, the same three): `test_the_committed_tasklist_passes`
(`tests/test_proof_status.py:81`, `assert _run(ROOT).returncode == 0`), `test_committed_state_passes_status_and_ledger`
(:93, `assert status.returncode == 0, status.stderr`), `test_committed_tree_anchor_state_is_the_declared_pending_one`
(:472, `assert completed.returncode == 0, completed.stderr`); each one's stderr is exactly state (a)'s
`proof-status: S0-04: the minted proofs/S0-04/result.json changed since accepted/S0-04 (regenerated after acceptance) —
re-accept with a new signed tag (AF-AP-56)`. These are the brief's three committed-state tests failing BY DESIGN until
the owner re-signs. Everything else passes: all 98 S0-04 tests (the 79 at the PIN plus the 19 new) and the other 30.
128 + 3 = 131 = the premise's 112 plus the 19 new cases.

Static gates on the final bytes:
```
$ python3 -m pyflakes proofs/S0-04/check_compression.py proofs/S0-04/tools/pc/capture_leg.py tests/test_s0_04_compression.py
pyflakes rc=0
$ python3 scripts/ap_screen.py <the same three files>
--- AP_SCREEN over 3 path(s): 6 hits over 3 files ---        (at the PIN: 7 hits)
AF-AP-224: 0 (at the PIN: 2, capture_leg.py:46 and check_compression.py:82, the two lines this lane fixes)
AP-1 x2      proofs/S0-04/tools/pc/capture_leg.py:60        pre-existing (the key file's one env resolution, test-pinned)
AF-AP-70     proofs/S0-04/tools/pc/capture_leg.py:181       pre-existing
AF-AP-132    tests/test_s0_04_compression.py:796            pre-existing (was :748; my insertions moved it)
AP-32        tests/test_s0_04_compression.py:610            pre-existing (was :562)
AF-AP-39     tests/test_s0_04_compression.py:258            NEW, on my line: a false positive, see below
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>     -> 0 for check_compression.py, capture_leg.py, the test file, result.json, this report
$ git diff --check -- proofs/S0-04 tests/test_s0_04_compression.py   -> rc 0
$ python3 scripts/report_lint.py tasks/briefs/system1/S0-04-LEAK-report.md --min-refs 10
report_lint: 33 refs — OK 18, NEAR 0, MISS 0, UNCHECKABLE 15, UNRESOLVED 0 (worktree)
```
(first run: MISS 5 and NEAR 1, each a report line with no token copied from the cited line, or a range one line
short; tokens added and the range corrected, no number was wrong.)

Final identities (sha256 prefix; `git diff --numstat`): `proofs/S0-04/check_compression.py` 881710af6818ee0d (+5 -2),
`proofs/S0-04/tools/pc/capture_leg.py` 7b202db013aa597a (+1 -1), `tests/test_s0_04_compression.py` e19440111a7d805a
(+67 -0), `proofs/S0-04/result.json` b5ea7672903d9cf5 (+8 -8, regenerated by the runner).

The AF-AP-39 hit (a secret interpolated into a command line) is the tell's syntactic shape, `..._API_KEY={`, with no
`.write(` on the same line: the f-string builds a FAKE assignment that `_with_note` writes into the bundle's
`off/request.json`; argv carries only the bundle's path. Not reshaped: the build loop's rule is never to edit a test
to silence the screen. The pre-commit hook runs the screen on staged shell files only, advisory
(`scripts/hooks/pre-commit:148`, `|| true`), so it does not block the commit.

## 10. Self-attack: the three likeliest ways this is wrong

1. **The new anchor fails a FUTURE capture on a harmless field** (a snake_case name ending `_token`/`_secret`/... with
   an 8+ character value, e.g. a pagination `next_page_token`). Ruled out for everything that exists: 0 hits on the
   evidence, every fixture and the test corpus under S1. The class is real and quantified on bystanders (S0-11:367,
   `_CHMOD_SYM_TOKEN = re.compile`). It fails loudly with the rule named, never silently; the owner would see it at
   the next capture. Residual, stated in section 2.
2. **The re-mint changed more than the two hashes** (another host name in `env_fingerprint`, or a `_redact`ed
   observation line changing the positive leg's stdout). Ruled out: the field-by-field diff (63 identical, 8 changed:
   the 2 hashes and 6 volatile fields), both `stdout_sha256` values identical, and the normalized digest recomputed
   with the two old hashes put back equals the committed ledger value exactly.
3. **The tests pass for the wrong reason** (another rule firing, another file tripping, or a mirror of the code).
   Ruled out: each leak test asserts the WHOLE output is the one exact line naming the file and the rule; on the
   PIN they red at `assert 0 == 1` (the leak PASSED) or with the fake key printed; each of the six required mutants
   dies at a named test, and the ordinary-text controls die only on the over-wide mutants. Fakes are fresh per run
   (`secrets.token_hex`), so no test can pass on a memorised value.
(4. The capture answer: wrong if `safe()` were reachable on a success path. Ruled out by the tripwire run, section 7.)

## NOT DONE (first-class)

- N1. **`proofs/ledger.json` is NOT regenerated in the tree.** The session's permission classifier refused
  `python3 scripts/ledger-gen --root .` ("Modify Shared Resources"); not retried, not worked around. The coordinator
  runs it at landing; the expected output is `<scratch>/s004leak/ledger/remint-regen.json` (one line differs, section 5),
  and in the landing model the tool writes exactly that file (section 6).
- N2. DEVIATION X1: the capture guard does not refuse `<PREFIX>_API_KEY=<value>` (no rule to re-anchor; adding one is the
  coordinator's call; the option and its measured limits are in section 3).
- N3. The digit side of the anchor is not pinned by a test (M7 to M9 survive by design, section 4).
- N4. Not touched, by the boundary: no commit, no tag or ref, no `todo/BUILD-TASKLIST.md` (no PENDING line in the real
  ledger: that is the coordinator's state (b)), no `docs/governance/`, no other proof, no `tests/test_proof_status.py`
  (DISCREPANCY D3).
- N5. Siblings are reported, not fixed (section 8); the one that matters most is S0-01's stderr screen, a signed proof.
- N6. No PC capture (not needed, section 7); no PC bridge; CI not run (no push).
- N7. The owner's re-sign is the owner's action; nothing here makes S0-04 owner-verifiable again.

## DISCREPANCIES

- D1. The brief's sibling-sweep command as typed (`bearer\\\\s`) prints 3 of the premise's 6 lines; with `bearer\\s` it
  prints all 6. The recorded output holds; the recorded command has one extra escape level.
- D2. HEAD moved from 5eda746 to 58a9c6f during the lane (four coordinator commits, D-092 and D-093, 20:46:30Z): none
  touches my boundary or the attestation closure; the ledger gained two lines (the PROOF-STATUS block is unchanged).
- D3. State (b) leaves `test_committed_tree_anchor_state_is_the_declared_pending_one` red (section 6), and CI with it,
  until the owner re-signs. The brief implies (b) is the clean waiting state; for this test it is not.
- D4. The classifier refused two commands: `ledger-gen --root .` (N1) and `scripts/pc_suite.sh set-id` (the bridge
  launcher; its set-id formula at :46 was computed inline instead, same result as the premise).
- D5. "Each new test reds on the PIN's rules" holds for the 7 leak cases; the 12 ordinary-text controls cannot red on the
  PIN (it takes no ordinary text); their red state is the over-wide anchor (M4 to M6).
- D6. `nextPageToken` added to the brief's ordinary-text list (the only way to kill the key-assignment "no anchor"
  mutant; none of the brief's five reaches that rule's name anchor).
- D7. The AF-AP-39 screen hit on my new test line (a false positive of the tell's shape, section 9).
- D8. GitNexus `impact` reads risk UNKNOWN for `LEAK_PATTERNS` and `LEAK_RE` (module constants, no edges; index 2
  commits behind); confirmed by text search (section 3).
- D9. S1 is wider than `\b` for a NON-ASCII letter before the key (it takes `ésk-...`); S1u would refuse it. 0
  instances anywhere measured; the protective direction; kept for one rule shape with the scrubber.
- D10. The premise shows two recipe lines from the S4H message; the same grep prints three (the validate-ledger line too).
- D11. `docs/research/findings/system1-context/UPSTREAM-ISSUES.md` became modified in the shared tree at 20:59:30Z
  (+31 -3), during this lane. Not written by this lane (no command of mine writes under `docs/`), not declared in
  `.lanes-live`; left untouched. Whoever owns it should claim it before a `--lanes-live` push, which counts tracked
  dirty files against the declared list.

Evidence tiers: VERIFIED (run here, output pasted): the premise, the measurement, the red run, the mutation pass, the
re-mint and both diffs, the anchor states and the landing model, the capture-tool equivalence, both gate runs, the
static gates. INFERRED: that CI reads the landed state (b) as the landing model did (CI clones without tags per the test's
own docstring; CI itself not run). ASSUMED: nothing load-bearing.

---

# R1: the repair round (F1, F1b, F3, F10, F13 from VERIFY-S0-04-LEAK)

R1 STATUS: DONE (tests green, re-minted in the tree, not committed). The key-assignment rule is linear and
takes name tails (K2) in both screens; the capture guard carries it and reports a YAML error by position
only. 58 new cases, 26 red on the committed bytes for the exact reason; 37 of 39 mutants killed (2
equivalent). Gate `pytest-summary: 189 passed` twice (2 files set=2fa20f3af1f3); `tests/test_proof_status.py`
green in state (b). The in-tree `ledger-gen` is yours; the expected file is in R1.7.

Resumed 2026-09-25T22:00:50Z (bucket 22:0xZ). Tree: HEAD f15970f; my R0 landing is 1f764fe (origin), my four files byte-identical
to it; state (b) in force (no `accepted-S0-04.tag`, no local ref, the PENDING line at `todo/BUILD-TASKLIST.md:351`).
The landing already narrowed `tests/test_proof_status.py:477` to `"WARNING S0-11"` (my D3 option). Scratch:
`<scratch>/s004r1/`; short basetemps under `/tmp/s4r/`. Live beside me: S1-ALL (its three files untouched).

## R1.1 PREMISE: each finding reproduced on the committed bytes (22:0xZ)

Venue: `<scratch>/s004r1/r0` = `git archive 1f764fe proofs/S0-04` (`cmp`: both tools equal the tree's). Probe
`<scratch>/s004r1/premise.py` (real CLIs, fakes from `secrets.token_hex(16)`, verdicts and booleans only):
```
F1  capture guard, <PREFIX>_API_KEY=<v> through the real CLI (--max-seq --record-dir <tmp>/absent/<text>):
    OMNIROUTE_API_KEY=<hex32> / DB_PASSWORD=<hex32> / GITHUB_TOKEN=<hex32> / api_key: <hex32>
    each: rc=1 withheld=False fake_in_stderr=True
F3  checker, the name's right side (a bundle field, the real CLI):
    SECRET_KEY=<hex32> / AWS_SECRET_ACCESS_KEY=<hex32> / OMNIROUTE_API_KEY_2=<hex32>
    each: rc=0 verdict=PASS; capture: rc=1 withheld=False
F13 the key-assignment rule alone, ' token' + N spaces: N=2000 0.024 s, 4000 0.098 s, 8000 0.390 s, 16000 1.518 s
    (x4 per doubling: quadratic); the real checker CLI, 32,000 spaces planted: rc=0 PASS, wall 6.4 s
F1b the verifier's own x1.py on the committed capture tool (PyYAML 6.0.1; it tests the value's LAST 12 chars):
    a colon after the value (api_key: <v>: x), sk- value: printed ScannerError, value in stderr: True
    unclosed quote, hex32: printed, value in stderr: True; sk-: WITHHELD
    tab indent, hex32: printed (a 22-char PREFIX leaks, which x1's tail test cannot see; measured in R0 section 3)
    error on another line: printed, no value
```
F10 is a coverage finding (the verifier's mutants M23 to M25 survive); it is reproduced by R1.5's mutation pass.
Verdict: all five hold on the committed bytes; no CONTRACT-INVALID.

## R1.2 F3 and F13: which right side and which separator, by measurement (22:0xZ)

Instrument (scratch): `<scratch>/s004r1/instr_r1.py` builds each candidate from the COMMITTED rule text (it asserts the
text first); `measure_r1.py` walks the corpora; `timing_r1.py` times them. Masked shapes only (the NAME side is an
identifier and is shown only when every tail segment is on a fixed word list; values as length and classes).
Candidates, all on the committed left anchor and value part:
- K0 = committed: `...token)\b` + `\s*[\"']?\s*[:=]`;
- K0L = K0 with only the separator linear: `\s*(?:[\"']\s*)?[:=]` (the same language: with no quote both are `\s*`);
- K1 = K0L + underscore tails `(?:_[A-Za-z0-9]+){0,4}\b`;
- **K2 = K1 minus a last segment `_env`, `_file` or `_path`: `(?:_[A-Za-z0-9]+){0,4}(?<!_env)(?<!_file)(?<!_path)\b`**;
- K3 = K0L + any identifier tail `[A-Za-z0-9_]{0,40}\b` (to price the naive widening).

```
$ python3 <scratch>/s004r1/instrument_r1.py <scratch>/s004r1/tree        (git archive 1f764fe; verdicts stay K0's)
$ (cd <scratch>/s004r1/tree && python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/s4r/bt1 tests/test_s0_04_compression.py)
98 passed in 8.38s                                         (736 screened texts logged)
$ python3 -B <scratch>/s004r1/measure_r1.py . <scratch>/s004r1/r0 <scratch>/s004r1/corpus_r1.jsonl <scratch>/vs004/anchors.py \
    'proofs-other=proofs/S0-0[1-35-9]/**/*' 'proofs-other-1x=proofs/S0-1[0-2]/**/*' 'transcripts=transcripts/sandbox/*.md' \
    'code-scripts=scripts/*.py' 'code-src=src/**/*.py' 'code-tests=tests/*.py'
```

| Corpus | K0 hits | K0L new/lost | K1 new | K2 new | K3 new |
|---|---|---|---|---|---|
| real evidence (7 files, 163,028 chars) | 0 | 0/0 | 0 | **0** | 0 |
| every fixture (evidence-pass, -header-missing, -body-diff, request-baseline, request-large) | 0 | 0/0 | 0 | **0** | 0 |
| test corpus (736 texts: 567 bundle files, 136 reason lines, 23 fixture texts, 10 capture messages) | 4 | 0/0 | 0 | **0** | 0 |
| bystander: proofs S0-01..S0-09 except S0-04 (796 files) | 3 | 0/0 | 9 (every one a `..._SECRET_FILE` path reference in S0-02's committed evidence) | **0** | 12 |
| bystander: proofs S0-10..S0-12 | 1 | 0/0 | 0 | 0 | 0 |
| bystander: transcript digests (18) | 0 | 0/0 | 0 | 0 | 0 |
| bystander: scripts/*.py (39) | 4 | 0/0 | 3 | 2 (`..._TOKEN_<n> = re.compile` code lines) | 21 positions |
| bystander: src/**/*.py (13) | 1 | 0/0 | 0 | 0 | 0 |
| bystander: tests/*.py (108) | 21 | 0/0 | 9 positions | 6 positions (other suites' fakes of the F3 shapes: `SECRET_KEY`, `SECRET_ACCESS_KEY`, `SECRET_VALUE`) | 23 positions |

The verifier's own shapes (`anchors.py`'s SHAPES, each as the checker reads it), K0 K0L K1 K2 K3:
A20 `SECRET_KEY=`, A21 `AWS_SECRET_ACCESS_KEY=`, A22 `OMNIROUTE_API_KEY_2=`: pass pass HIT HIT HIT (F3 closed by K1-K3);
O13 `DB_PASSWORD_FILE=/run/secrets/db`, O14 `api_key_env=OMNIROUTE_API_KEY`: pass pass HIT **pass** HIT;
O10 `max_tokens: 12345678`: pass except K3; every other A and O row identical across all five.

Timing (seconds; `timing_r1.py`; K0 at small N because it is quadratic):
```
' token' + N spaces      K0: 2000 0.0249  4000 0.0989  8000 0.4557  16000 1.5066     (x4 per doubling)
                         K2: 16000 0.0018  32000 0.0034  1,000,000 0.1079  8 MiB 0.9596
' token"' + N spaces     K2: 32000 0.0030  8 MiB 0.7509        ' token=' + N spaces  K2: 32000 0.0035  8 MiB 1.0047
'_token' x N/6           K2: 32000 0.0075  1,000,000 0.2398  8 MiB 2.0328  (many name starts in one identifier)
' token_' + N letters    K2: 8 MiB 0.5437    ' token' + '_a' x N/2  K2: 8 MiB 0.3957    ' api_key_env' x N/12  K2: 8 MiB 0.4640
unbounded tail (*) on '_token' x N/6:  6000 0.1437  12000 0.5761  24000 2.3683  48000 9.2334  (quadratic; K2 at 48000: 0.0109)
```

**Decision: K2 in both screens.** It closes F3 (A20-A22) and F13 (linear on every shape to 8 MiB), adds 0 hits on the
real evidence, every fixture and the test corpus, and keeps the verifier's O13/O14 reference names passing; K1 would
fail every S0-02 evidence file that carries a `..._SECRET_FILE` path (9), K3 takes `max_tokens` and `tokenizer`. The
tail bound `{0,4}` is load-bearing: unbounded, a run of names inside one identifier is quadratic (9.2 s at 48,000
characters). K0L alone changes no verdict anywhere (0 new, 0 lost), so the separator fix is pure performance.

## R1.3 What changed (22:0xZ)

- `proofs/S0-04/check_compression.py`, inside `LEAK_PATTERNS`: the key-assignment rule becomes K2 (name list and
  left anchor unchanged; the tail, the three reference exclusions, the linear separator); the comment above `sk-key` now
  says "an ASCII letter or digit" (the verifier's F7 wording; the rule is unchanged); a comment above the rule says why.
- `proofs/S0-04/tools/pc/capture_leg.py`:
  - `LEAK_RE` gains a third alternative, the checker's key-assignment rule (without its own `(?i)`: `LEAK_RE`'s leading
    `(?i)` covers every alternative); the bearer and `sk-` alternatives are byte-identical; the comment names the pin.
  - `do_config`: `yaml.safe_load` wrapped; a `yaml.YAMLError` becomes `CaptureError("profile <path> is not valid YAML
    at line L, column C")` from the error's `problem_mark` (else `context_mark`), `from None`; no snippet, no problem
    text. Nothing else in `do_config` changed.
- Impact: GitNexus `impact do_config`: LOW, direct `main` (index 3 commits behind); `LEAK_PATTERNS`/`LEAK_RE` as in R0.

Semantic check on the new bytes (fakes at run time, masked):
```
lock: capture ends with the checker rule: True | starts (?i): True
OMNIROUTE_API_KEY=, SECRET_KEY=, AWS_SECRET_ACCESS_KEY=, OMNIROUTE_API_KEY_2=, DB_PASSWORD=, api_key: , x/api_key=
    (+<hex32>)                                   checker=key-assignment  capture_withheld=True
x_<sk-fake>, x-<sk-fake>                         checker=sk-key          capture_withheld=True
DB_PASSWORD_FILE=/run/secrets/db, api_key_env=OMNIROUTE_API_KEY, SECRET_PATH=/etc/app/secret.d, max_tokens: 12345678,
tokenizer: <hex32>, x-api-key-id: <hex32>, nextPageToken: <hex32>, task-<hex32>    checker=None  capture_withheld=False
timing: 32,006 chars of ' token'+spaces 0.0049 s (both screens); 48,000 chars of '_token' 0.0127 / 0.0132 s
yaml, api_key: <sk-fake>: x   rc 1, no 8-char window of the key in stderr,
    stderr: capture_leg: profile <profile> is not valid YAML at line 4, column 49
spec legs: PASS: S0-04 compression-contract - 3 assertions over 3 legs / failure_reason: off: compression-header-missing rc=1
```

**The verifier's hostile shapes, run unmodified as an independent oracle** (`<scratch>/vs004/anchors.py <repo>
<scratch>/s004r1/r0/proofs/S0-04 <work>`: new = these bytes, old = the committed R0 tools; 75 rows, real CLIs, fresh
fakes; 0 ECHO flags). Verdict changes new vs old, and why:
- Checker: exactly A20, A21, A22 change, `PASS` -> `LEAK:key-assignment` (F3's right side). No other checker row moves.
- Capture: `PRINTED` -> `WITHHELD` on every assignment row the checker already caught (A01-A08, A10-A17, A27-A30; F1)
  and on A20-A22 (F3), and on the three rows that were already checker false positives (O09 `next_page_token:`, O12
  `_CHMOD_SYM_TOKEN = re.compile`, O16 prose `the password: forgotten again`): the guard now shares the checker's rule,
  so it shares its false positives too; the cost is a withheld error message, nothing else.
- Nothing moved from caught to passed, in either tool.
The verifier's `x1.py` (PyYAML errors through `--config`), new vs old: every new row prints `capture_leg: profile <path>
is not valid YAML at ...` with no value and no `api_key` in stderr; the old rows print the value in three cases (the
colon row with an `sk-` key among them).

## R1.4 Tests, red first on the committed bytes (22:1xZ)

`tests/test_s0_04_compression.py`: `import re`; 58 new cases (98 -> 156), every key and value from `secrets.token_hex(16)`:
- `ORDINARY_NOTES` gains five controls, so both existing ordinary tests grow by five: `DB_PASSWORD_FILE=/run/secrets/db`,
  `api_key_env=OMNIROUTE_API_KEY`, `SECRET_PATH=/etc/app/secret.d` (reference tails), the key `max_tokens`, the key
  `tokenizer` (words that only start like a name).
- F3: `test_a_key_name_with_a_tail_fails_the_checker` x3 (`SECRET_KEY`, `AWS_SECRET_ACCESS_KEY`, `OMNIROUTE_API_KEY_2`):
  rc 1, the whole output the one exact `... matches key-assignment` line, the value not echoed.
- F10: `NO_LOSS = ("-", "/", ":", ".", '"', "'", " ")`; `test_a_key_after_a_separator_still_fails_the_checker` x14 (each
  separator x {an `sk-` key, `api_key=<v>`}: the exact `matches sk-key` / `matches key-assignment` line) and
  `test_capture_leg_withholds_a_key_after_a_separator` x14 (the real CLI: stderr exactly the withheld line).
- F13: `test_both_screens_are_linear_on_a_hostile_run[spaces | names]` (32,000 spaces after ` token`; 8,000 x `_token`;
  each screen under 1.0 s; measured 0.005 s and 0.013 s) and `test_the_checker_cli_screens_a_file_at_the_size_cap_in_bounded_time`
  (the real CLI on a bundle holding a `MAX_EVIDENCE_FILE`-sized run of spaces after ` token`, `timeout=60`; 1.35 s here).
- F1 and F3 through the capture CLI: `test_capture_leg_withholds_a_key_assignment` x7 (`OMNIROUTE_API_KEY=`, `DB_PASSWORD=`,
  `GITHUB_TOKEN=`, `api_key: `, `SECRET_KEY=`, `AWS_SECRET_ACCESS_KEY=`, `OMNIROUTE_API_KEY_2=` + a value), with a small
  `_capture_error` helper for the CLI error path.
- F1 lock: `test_capture_guard_carries_the_checker_key_assignment_rule`: both patterns start `(?i)`, and `LEAK_RE`'s text
  ends with `|` + the checker's rule minus its `(?i)`.
- F1b: `test_capture_leg_reports_a_yaml_error_by_position_only` x6 ({unclosed quote, tab indent, colon after the value} x
  {an `sk-` key, a hex value}) through `--config`: no 8-character window of the value anywhere in the output (stricter
  than x1.py's last-12 test: it also sees the tab case's prefix), rc 1, stderr exactly `capture_leg: profile <path> is not
  valid YAML at line N, column M` (N and M as digits: the line is where PyYAML's problem mark falls, which for an
  unclosed quote is the end of the stream).

**Red run** (`<scratch>/s004r1/red`: `git archive 1f764fe` of proofs/S0-04 and the test inputs, the new test file copied
in, `cmp` proves both tools are the committed R0 bytes):
```
$ (cd <scratch>/s004r1/red && python3 -m pytest -q -p no:cacheprovider -rf --basetemp=/tmp/s4r/bt3 tests/test_s0_04_compression.py)
26 failed, 130 passed in 73.75s (0:01:13)
```
| Failed (26) | Where | Exact reason on the R0 bytes |
|---|---|---|
| `test_a_key_name_with_a_tail_fails_the_checker` x3 | :286 `assert code == 1` | `assert 0 == 1`: the checker printed its observations and PASSed over the tailed assignment (F3) |
| `test_both_screens_are_linear_on_a_hostile_run[spaces]` | :314 | `AssertionError: _leak_hit`: the checker took over 1.0 s on 32,000 spaces (F13) |
| `test_the_checker_cli_screens_a_file_at_the_size_cap_in_bounded_time` | the CLI call | `subprocess.TimeoutExpired` after 60 s on the 8 MiB run (F13, at the cap) |
| `test_capture_leg_withholds_a_key_assignment` x7 | :1030 | stderr `capture_leg: record dir not found: <tmp>/absent/<name><hex>`: the fake printed (F1, F3) |
| `test_capture_leg_withholds_a_key_after_a_separator[<sep>-key-assignment]` x7 | :1041 | the same, `...x<sep>api_key=<hex>` printed (R0 has no assignment rule in the guard) |
| `test_capture_guard_carries_the_checker_key_assignment_rule` | :1049 | `endswith(...)` is False: no key-assignment alternative in `LEAK_RE` (F1) |
| `test_capture_leg_reports_a_yaml_error_by_position_only` x4 (unclosed quote/hex, tab/hex, colon/`sk-`, colon/hex) | :1070 | `<label>: part of the value printed`: the snippet carried the value (F1b; the colon/`sk-` row is the verifier's 32-of-35) |
| the same x2 (unclosed quote/`sk-`, tab/`sk-`) | :1072 | the output is `capture_leg: <message withheld: credential-shaped>`, not the position line: R0's `sk-` rule hid the snippet, the contract now asks for the position |

The 32 new cases that pass on R0, by design: the 14 checker and 7 capture `sk-` no-loss cases (F10 pins a behaviour R0
already has), the 10 new ordinary controls (R0 takes no tail), and `[names]` (R0 has no tail to backtrack). Their red
states are the mutants of R1.5. **Deviation (flagged, as in R0 D5): "red first on the current bytes" holds for 26 of the
58 new cases; the other 32 are no-loss pins and controls that cannot red there.** Fixed tree, R1-related cases:
`74 passed, 82 deselected in 4.17s`.

## R1.5 Mutation pass on each changed rule (22:2xZ)

`<scratch>/s004r1/mutate_r1.py` on `<scratch>/s004r1/mut` (a `git archive HEAD` copy with the three working-tree files).
AF-AP-223 rules: the unmutated control first and green at the full count; a mutant's edit text must occur exactly once;
KILLED only when a test FAILED (named) with no ERROR and an unchanged total; files restored and re-hashed after each run.
Group A mutates the key-assignment rule in BOTH files at once, so the lock test stays green and only behavioural tests
can kill; group B mutates one file; C pins the no-loss direction of both `sk-` rules; D is the YAML path.
```
CONTROL (unmutated): rc=0 156 passed in 7.98s            (each group re-ran it green: 8.21s, 7.96s, 8.08s)
A1  both: name tail removed (back to \b)          KILLED  the 3 tail cases (checker) + the 3 tailed capture cases
A2  both: name tail unbounded                     KILLED  test_both_screens_are_linear_on_a_hostile_run[names]
A3  both: _env tail no longer excluded            KILLED  both ordinary tests [stray_note-api_key_env=OMNIROUTE_API_KEY]
A4  both: _file tail no longer excluded           KILLED  both ordinary tests [stray_note-DB_PASSWORD_FILE=/run/secrets/db]
A5  both: _path tail no longer excluded           KILLED  both ordinary tests [stray_note-SECRET_PATH=/etc/app/secret.d]
A6  both: any identifier tail                     KILLED  10: both ordinary tests on max_tokens, tokenizer and the 3 reference tails
A7  both: hyphen tails too                        KILLED  both ordinary tests [x-api-key-id-{}]
A8  both: tail bound 1                            KILLED  [AWS_SECRET_ACCESS_KEY] (checker) and [AWS_SECRET_ACCESS_KEY=] (capture)
A9  both: the quadratic separator restored        KILLED  [spaces] and test_the_checker_cli_screens_a_file_at_the_size_cap_in_bounded_time
A10 both: name anchor back to \b                  KILLED  10 (the R0 prefixed cases, the tail cases, the capture assignment cases)
A11 both: name anchor none                        KILLED  both ordinary tests [nextPageToken-{}]
A12 both: name anchor refuses - / : . " ' space   KILLED  x7, each by its own [<sep>-key-assignment] case in the checker AND the capture test
B1  checker only: name tail removed               KILLED  the 3 checker tail cases + the lock
B2  capture only: the key-assignment alternative removed   KILLED  15 (the lock, the 7 assignment cases, the 7 separator assignment cases)
B3  capture only: name tail removed               KILLED  the 3 tailed capture cases + the lock
C1  checker sk-key refuses - / : . " ' space      KILLED  x7, each by test_a_key_after_a_separator_still_fails_the_checker[<sep>-sk-key]
C2  capture sk refuses - / : . " ' space          KILLED  x7, each by test_capture_leg_withholds_a_key_after_a_separator[<sep>-sk-key]
D1  the YAML handler removed (the error reaches main's catch-all)   KILLED  all 6 YAML cases
D2  the message carries the exception text        KILLED  all 6 YAML cases
D3  `from None` dropped                           SURVIVED (156 passed)
D4  context_mark preferred over problem_mark      SURVIVED (156 passed)
TOTAL A {'KILLED': 18} B {'KILLED': 3} C {'KILLED': 14} D {'KILLED': 2, 'SURVIVED': 2}; INVALID 0; files restored: True
```
Survivors, classified: D3 and D4 are equivalent at the CLI. `main` prints only `safe(str(error))`, never a traceback,
so the chained YAMLError is never printed with or without `from None`; either mark is a position, never content, and
the tests pin the format (`line \d+, column \d+`), not which mark. The verifier's M23-M25 (the no-loss direction)
survived R0; C1/C2 now kill each separator on each screen. Not pinned, by scope (as in R0): a digit or an uppercase
letter before the key (the verifier's M7-M9, M13-M14), because a pinning test asserts that a key-shaped string passes.

## R1.6 The capture tool's outputs outside the error paths, R0 vs R1 (22:2xZ)

`<scratch>/s004r1/capture_equiv_r1.py <R0 capture_leg.py> <R1 capture_leg.py> <repo> <scratch>`:
```
1. the same top-level definitions, in the same order: True
   definitions whose AST differs: ['LEAK_RE', 'do_config']
   | -    profile = yaml.safe_load(read_regular(Path(args.profile), 'profile'))
   | +    try:
   | +        profile = yaml.safe_load(read_regular(Path(args.profile), 'profile'))
   | +    except yaml.YAMLError as exc:
   | +        mark = getattr(exc, 'problem_mark', None) or getattr(exc, 'context_mark', None)
   | +        where = f'line {mark.line + 1}, column {mark.column + 1}' if mark is not None else 'an unknown position'
   | +        raise CaptureError(f'profile {args.profile} is not valid YAML at {where}') from None
2. LEAK_RE read in: ['safe'] | safe() called at: [('main', 'inside except handler', 317), ('main', 'inside except handler', 320)]
3. modes and rc (new): capture, --config, --find-record, --max-seq all 0 | safe() tripwire never fired
   stdout identical per mode: [True, True, True, True]
   files written: config/hermes-provider.json, off/request.json, off/response.json, off/upstream-record.json
   every written file byte-identical between the old and the new version: True
```
So R0's answer to the capture question still holds for R1: the `LEAK_RE` change sits on the error path only, and the
YAML handler runs only when `yaml.safe_load` raises, when no evidence is written; the committed evidence is what the
R1 bytes write from the same inputs. No new PC capture is needed.

## R1.7 The re-mint, by the same recipe (22:2xZ)

Dry run first in a scratch `git archive HEAD` of the attested closure plus the two R1 tools: `dry proof-runner rc=0`, only
the two tools' attestation entries changed (44 both sides), runs changed only in their timestamps, negative control
identical. Then, in the repo:
```
# the control: the R1 tools against the R0 result, the binding catches it
$ python3 scripts/validate-ledger integrity --root .
S0-04 INVALID / execution_proof numerator=8 denominator=9 / attestation-mismatch: S0-04 proofs/S0-04/check_compression.py
integrity rc=1
# the re-mint, 22:24:38Z
$ python3 scripts/proof-runner run --proof S0-04 --venue sandbox --root .        -> proof-runner rc=0
$ python3 scripts/validate-ledger integrity --root .                             -> all twelve PRESENT, execution_proof 9/9, rc=0
$ python3 scripts/ledger-gen --root . --output <scratch>/s004r1/ledger/r1-regen.json   -> rc=0 (not written in-tree: yours)
$ diff <(git show HEAD:proofs/ledger.json) <scratch>/s004r1/ledger/r1-regen.json
23c23
<       "normalized_digest": "5b49bfb5cb33a1ea5361622a83fc04bdd1013506d67ab405e7b1c6fbac271c04",
---
>       "normalized_digest": "7daeba65ace36822f232847e50e9448d76e59fa9c8269f7353e354fdb76a8b9f",
$ python3 scripts/check-proof-status.py .
proof-status: WARNING S0-04: ACCEPTED with the anchor PENDING the owner's signed tag accepted/S0-04 (declared in the ledger) — not owner-verifiable yet
check-proof-status rc=0
```
**The expected ledger file: `<scratch>/s004r1/ledger/r1-regen.json`** (one line differs from HEAD, S0-04's digest; the state
stays PRESENT). `proofs/ledger.json` in the tree is unchanged from HEAD.

**`proofs/S0-04/result.json`, field by field (HEAD = the R0 mint vs R1): 71 leaf fields, 63 identical, 8 changed.**

| Field | R0 (committed) | R1 | Why |
|---|---|---|---|
| `attestation["proofs/S0-04/check_compression.py"]` | 881710af6818ee0dfb695f5b96fc5b60262c04d6914493d62c3c613ac12ea090 | 033333c57e3c371efdd7aed17223357ad4e2dc1c397f4e11f6b187060cbf9d7f | the edited checker (= its sha256 now) |
| `attestation["proofs/S0-04/tools/pc/capture_leg.py"]` | 7b202db013aa597a67a4f0fb151afa11cc409efb015c7e604fb30c8c6f9eb7eb | f455144f8889e5ff9209f1399f4d7a9c97c83939f77e97e6e545a4f509764c5f | the edited capture tool (= its sha256 now) |
| `recorded_at` | 2026-09-25T20:51:59.316128Z | 2026-09-25T22:24:38.746170Z | volatile |
| `runs[0].started_at` / `finished_at` | 20:51:59.203373Z / .264970Z | 22:24:38.660638Z / .705154Z | volatile |
| `runs[1].started_at` / `finished_at` | 20:51:59.265172Z / .315284Z | 22:24:38.705370Z / .745708Z | volatile |
| `digest` | 5fe687a29691b64571a4cb794a55f648bec5d1f1baf646252fbc08d4ebd50d05 | 27c71a8b552268f382501a880afc2cfdb0798b0298414c655969403cd0f08cf6 | sha256 of `runs` (their timestamps) |

Identical: classification (execution_proof), `env_fingerprint` (sandbox:vm), the other 42 attestation entries, both runs'
`cmd`, `exit_code`, `stdout_sha256`, `stderr_sha256`, the negative leg's `failure_reason`, and `negative_control`: PASS for
the same assertions, with byte-identical checker output. The ledger line follows from the two hashes alone: R1 normalizes
to `7daeba65...`; R1 with the two R0 hashes put back normalizes to `5b49bfb5cb33a1ea5361622a83fc04bdd1013506d67ab405e7b1c6fbac271c04`,
the committed value exactly.

## R1.8 Gates, pasted (22:2xZ)

`bash scripts/test_summary.sh --basetemp=/tmp/s4r/bt tests/test_s0_04_compression.py tests/test_proof_status.py`
(`/tmp/s4r` created first, the basetemp deleted before each run; set id by `scripts/pc_suite.sh:46`'s `set_id`, inline):
```
run 1: pytest-exit: 0
       pytest-summary: 189 passed in 14.37s
run 2: pytest-exit: 0
       pytest-summary: 189 passed in 14.82s
       2 files set=2fa20f3af1f3
```
189 = 156 S0-04 cases (98 + 58) + the 33 of `tests/test_proof_status.py`. **`tests/test_proof_status.py` is green in state
(b)**, as expected: the landing narrowed its committed-anchor assertion to `"WARNING S0-11"` (:477), so S0-04's pending
warning no longer reds it; nothing in R1 touches that file.
```
$ python3 -m pyflakes proofs/S0-04/check_compression.py proofs/S0-04/tools/pc/capture_leg.py tests/test_s0_04_compression.py
pyflakes rc=0
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>    -> 0 for both tools, the test file, result.json, this report
$ git diff --check -- proofs/S0-04 tests/test_s0_04_compression.py    -> rc 0
$ python3 scripts/ap_screen.py <the three files>    -> 6 hits over 3 files, the same six as at R0's end, moved by the
  new lines: AP-1 x2 capture_leg.py:65, AF-AP-70 capture_leg.py:186, AF-AP-132 test:847, AP-32 test:661 (pre-existing),
  AF-AP-39 test:259 (R0's disclosed false positive); no hit on an R1 line
$ python3 scripts/report_lint.py tasks/briefs/system1/S0-04-LEAK-report.md --min-refs 10
report_lint: 35 refs — OK 20, NEAR 0, MISS 0, UNCHECKABLE 15, UNRESOLVED 0 (worktree)
```
(The R0 sections' line numbers name the R0 bytes at 1f764fe; R1's line numbers name the working tree now.)
Identities (sha256 prefix, `git diff --numstat` against HEAD): `proofs/S0-04/check_compression.py` 033333c57e3c371e
(+10 -4), `proofs/S0-04/tools/pc/capture_leg.py` f455144f8889e5ff (+16 -3), `tests/test_s0_04_compression.py` (+114 -0),
`proofs/S0-04/result.json` (+8 -8, by the runner).

## R1.9 Self-attack: the likeliest ways R1 is wrong

1. **The reference-tail exclusions open a hole:** `OMNIROUTE_API_KEY_FILE=<a real key>` (a key in a variable named like a
   reference) now passes, as it did under R0 (R0 took no tail at all), so nothing is lost versus R0; and the three
   exclusions apply only to the LAST segment, so `API_KEY_FILE_2=` is still caught. Measured cost of NOT excluding them:
   9 S0-02 evidence files (K1). Kept, and flagged as a design choice.
2. **A linearity claim that holds for my inputs only:** the tail bound was the one new backtracking risk; it is timed on
   seven shapes to 8 MiB (the worst 2.0 s), the unbounded form is shown quadratic (9.2 s at 48,000 chars), and A2/A9
   prove the two timing tests kill both quadratic mutants. The value side keeps one `\s*` and the bearer rule one `\s+`.
3. **The YAML fix hides a useful message or leaks through another path:** it keeps a position for every YAMLError that
   carries a mark (else "an unknown position"); D1/D2 prove the tests see both a missing handler and a message that
   re-adds the exception text; the other exceptions `do_config` can raise carry a path or a byte offset, not content
   (measured: a non-UTF-8 profile prints `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 29`, no
   value; and `API_KEY_FILE_2=<v>` is caught while `OMNIROUTE_API_KEY_FILE=<v>` passes, as item 1 says).
4. **The lock test is a mirror:** it pins the capture's third alternative to the checker's rule text; B1/B3 show it reds on
   drift, and the behavioural capture tests (A-group) kill every semantic mutant with the lock green.

## R1 NOT DONE

- `proofs/ledger.json` not regenerated in the tree (yours at landing; the expected file is above).
- No commit, tag, ref, ledger (`todo/BUILD-TASKLIST.md`), `docs/governance/` or `tests/test_proof_status.py` change.
- Out of R1's scope, as the brief set it: F2 (the screen reads raw text: JSON escapes, URL encoding, `body_b64`), F4 (the
  allowlist assertion in `tests/test_proof_status.py`, yours), F5 (`STATUS.md`), F8 (the checker's `sk-key` is
  case-sensitive while the capture's is not), F9 (`parse_args` outside `main`'s `try`), F11 (S0-01's stderr screen),
  F12, F14; the digit and uppercase-letter pins (M7-M9, M13-M14: a pinning test asserts that a key passes).
- D3/D4 mutants survive as equivalent at the CLI (R1.5).
- No PC run, no CI run.

## R1 DISCREPANCIES

- R1-D1. "Red first on the current bytes" holds for 26 of the 58 new cases; the other 32 are no-loss pins (F10's `sk-`
  cases), ordinary controls and the tail-timing case, whose red states are mutants (R1.4, R1.5).
- R1-D2. Beyond the brief's literal scope, one comment word: "an ASCII letter or digit" in the checker's `sk-key` comment
  (the verifier's F7), inside `LEAK_PATTERNS`, in the same edit.
- R1-D3. Design choices the brief did not dictate: the tail bound `{0,4}` and the three reference-tail exclusions
  (`_env`, `_file`, `_path`), both measured (R1.2).
- R1-D4. The capture guard now shares the checker's existing false positives (O09 `next_page_token:`, O12, O16): a
  withheld error message, nothing else.
- R1-D5. `tasks/briefs/system1/VERIFY-SCRUB1-report.md` appeared untracked in the shared tree during R1; not mine,
  untouched (an untracked file does not count against a `--lanes-live` push).
- R1-D6. The F1b test asserts the position line's format (`line \d+, column \d+`), not which mark: for an unclosed quote
  PyYAML's problem mark is the end of the stream, one line below the key.
