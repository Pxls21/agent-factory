> **COORDINATOR NOTE (2026-09-26 08:5xZ):** the harness refused the lane's report-file write at 08:50:13Z ("Subagents should return findings as text, not write report files"), after sections 1-2 were written. The lane returned the rest as its hand-back text and did not work around the refusal. The coordinator assembled this file from the lane's own sections 1-2 and its returned text, extracted from the lane's transcript (never retyped): the hand-back summary follows section 2, then sections 3-15 as the lane wrote them. The coordinator re-ran the gate: `178 passed`, 1 files set=2e5825a9019e; pyflakes rc 0. Served model: claude-opus-5-5 on 218 of 218 assistant records, no refusal stop.

# I59-C report: S0-04 capture tool never prints a profile value; K2 bounds pinned (task #314)

Lane: sandbox code-implementer (Opus 5.5). Brief: `tasks/briefs/i59/I59-C-brief.md`. PIN 7a050b6; tree HEAD 59229eb.
Status: DONE (the lane); held as `tasks/briefs/i59/I59-C.patch` for the issue #59 batch landing (opened 2026-09-26 08:2xZ). This file is written incrementally.

## 1. Premise re-measured (2026-09-26 08:2xZ, sandbox tree)

All load-bearing premise lines reproduce. Pasted output:

```
$ git log --oneline 2a50a65..HEAD -- <the 3 files> | wc -l
0
$ grep -n -E '^def do_config|except yaml.YAMLError|except Exception as exc|^def main' proofs/S0-04/tools/pc/capture_leg.py
232:def do_config(args) -> int:
241:    except yaml.YAMLError as exc:
271:def main(argv=None) -> int:
319:    except Exception as exc:                                   # noqa: BLE001 - fail closed
$ grep -n 'passw' ... | cut -c1-110
proofs/S0-04/check_compression.py:92:        r"(?i)(?<![A-Za-z0-9])(?:api[_-]?key|apikey|secret|password|passw
proofs/S0-04/tools/pc/capture_leg.py:49:    r"|(?<![A-Za-z0-9])(?:api[_-]?key|apikey|secret|password|passwd|to
$ grep -l -E 'capture_leg|test_s0_04_compression' tests/*.py
tests/test_s0_04_compression.py
$ git diff --stat 7a050b6 -- <the 3 files>   (empty: identical to the PIN)
$ bash scripts/test_summary.sh tests/test_s0_04_compression.py
pytest-exit: 0
pytest-summary: 156 passed in 7.35s
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_04_compression.py
1 files set=2e5825a9019e
$ sha256sum pc-lane-partial.diff | cut -c1-16 ; stat -c %s ; git apply --check
1f6f47b47bc91fee
8703
applies to HEAD
```

PyYAML table (6.0.1, cext False, Python 3.11.15), fake value built at run time:

```
deep nesting -> RecursionError | msg holds FAKE: False
!!int tag -> ValueError | msg holds FAKE: True
!!float tag -> ValueError | msg holds FAKE: False | lower: True
!!bool tag -> KeyError | msg holds FAKE: False | lower: True
!!timestamp bad (month 13) -> ValueError | msg holds FAKE: False
huge int (5000 digits) -> ValueError | msg holds FAKE: False
ParserError -> ParserError | msg holds FAKE: True | mark: True
ComposerError -> ComposerError | msg holds FAKE: True | mark: True
ScannerError -> ScannerError | msg holds FAKE: True | mark: True
```

Extra finding (not in the brief): `api_key: !!timestamp 2026-99-99<fake>` raises **AttributeError** (a second class
outside YAMLError, ValueError and KeyError, besides RecursionError).

## 2. Design (08:3xZ) and the PC lane's partial diff, judged

**The PC lane's partial diff is NOT used.** Judged against the contract:
- G2: it adds `except (ValueError, KeyError)` beside `except yaml.YAMLError`. That handler IS the kill table's second G2
  mutant: a RecursionError (deep nesting) or an AttributeError (a bad `!!timestamp`) still reaches `main`'s catch-all,
  which prints the exception's message. Its comment's reason for staying narrow does not hold for a single handler.
- G2: the YAMLError path still reports no class; contract item 1 wants the class on every parse exception.
- G5: its fixtures were never measured; the composer row's alias is `*y`, not the value, so its message quotes no value.
- G6: in-process `LEAK_RE`/`_leak_hit` only, lower-case names; the brief's `API_KEY_ENV=` control is there.

**The fix (item 1).** In `do_config`, the profile is read BEFORE the `try` (`read_regular` raises no YAMLError, so
its errors took the same path before: "profile not found" and the rest keep their own messages), and the `try` holds
`yaml.safe_load` alone under `except Exception`. The handler reports `type(exc).__name__` and the mark (line, column;
"an unknown position" when there is none) and never `str(exc)`; `raise CaptureError(...) from None`, so rc stays 1.
Message: `profile <p> is not valid YAML (<Class>) at line L, column C`: the class in parentheses is the repo's sibling
form (`proofs/S0-03/check_omniroute_roundtrip.py:270`, `tests/test_skill_frontmatter.py:29`). Rejected: (a) two handlers
(YAMLError by position, everything else by class): two formats for one contract, and the kill table's D5 would then
land in the second handler; (b) keeping the read inside the `try` with `except CaptureError: raise`: a
PermissionError or a UnicodeDecodeError while READING would then print as "not valid YAML".

**The tests.** Through the real CLI (`capture_leg.py --config`), each with a fake value built at run time:
- `YAML_ERRORS` gains a class column and three rows (G5: a ParserError and a ComposerError; plus a ConstructorError,
  the third class the verifier's G5 fix named). The test now pins the class AND the exact position, both read from
  PyYAML's own exception for the same text in process (the oracle: the contract says "the position PyYAML gives").
  A precondition asserts that PyYAML's own message for that fixture carries an 8-character run of the value, so the
  handler is the only reason the value is absent.
- A new `NON_YAML_ERRORS` table (G2): `!!int` and `!!float` (ValueError), `!!bool` (KeyError), a 5,000-deep nesting
  (RecursionError), a bad `!!timestamp` (AttributeError); kinds `sk-key` and a MIXED-CASE non-`sk-` value.
- Every leak check folds case (`!!float`/`!!bool` lower-case the value first).
- G6: a 4-segment and a 5-segment name through the checker CLI and through the capture CLI; `API_KEY_ENV=<32 hex>`
  joins `ORDINARY_NOTES`, which both files' ordinary tests read.

## Hand-back summary (the lane's returned text)

I59-C (task #314) hand-back: all three items are built and proven. G2 is fixed, and G5 and G6 are pinned by tests. The gate passes twice at 178, and all six kill-table mutants are killed. Two things need your action:
- The report file is partial. The harness refused my report write mid-lane ("Subagents should return findings as text, not write report files"), and I did not work around it. `tasks/briefs/i59/I59-C-report.md` (untracked) holds sections 1-2 only (the premise and the design) and still says "Status: IN PROGRESS". Sections 3-15 are below, ready to paste after them.
- The landing needs the batch re-mint. `proofs/S0-04/result.json:83` attests the PIN's `capture_leg.py` hash (`f455144f…`); the fixed file is `f2e5d54c…`, so S0-04's result goes stale until #315 re-mints it.

No git writes, no PC or bridge use, no subagents. No secret source was read; every test value is a fake built at run time.

**Files changed (working tree):**
- `proofs/S0-04/tools/pc/capture_leg.py` (+14/-? lines, `do_config` only):
  - :239 `text = read_regular(...)`: the read moved before the `try`.
  - :241 `profile = yaml.safe_load(text)`.
  - :242 `except Exception as exc:` replaces `except yaml.YAMLError`.
  - :243-248 comment.
  - :251 the message is now `profile <p> is not valid YAML (<Class>) at line L, column C`, or `at an unknown position` when there is no mark.
- `tests/test_s0_04_compression.py` (+128 lines):
  - :271 `API_KEY_ENV={}` added to `ORDINARY_NOTES`.
  - :295 `_tailed_name`; :300 `test_the_checker_bounds_a_key_name_tail_at_four_segments`; :1066 `test_the_capture_guard_bounds_a_key_name_tail_at_four_segments`.
  - :1092 `YAML_ERRORS` gains a class column and three rows (:1096 ParserError, :1097 ComposerError, :1098 ConstructorError).
  - :1100-1120 the helpers `PROFILE_HEAD`, `_prints_part_of` (case-folded 8-character runs), `_yaml_error` (the oracle) and `_config_leg`.
  - :1131 the YAML test is rewritten to assert the exact class and position.
  - :1149 `NON_YAML_ERRORS` and :1160 `test_capture_leg_reports_a_non_yaml_parse_error_by_class_only` (G2).
  - `import re` removed: my change orphaned it.
- All 26 cited `file:line` references were checked against the tree: MISS 0.

**Counts (pasted):**
- Floor: `pytest-summary: 156 passed in 7.35s`, set 2e5825a9019e.
- Red, the new tests against the PIN's tool: `22 failed, 156 passed in 11.95s`.
- Gate run 1: `pytest-exit: 0`, `pytest-summary: 178 passed in 11.58s`.
- Gate run 2: `pytest-exit: 0`, `pytest-summary: 178 passed in 11.49s`.
- Set: `1 files set=2e5825a9019e`.
- Venue (PyYAML 6.0.3): `178 passed in 11.59s`.

**Kill table.** Control: `178 passed`. `GATE EXPECTED=6 RAN=6 KILLED=6 -> PASS`, 0 errors, total 178 on every row, real tree untouched.
- G2-OLD, the old `except yaml.YAMLError`: KILLED, 10 FAILED (every G2 row; the mixed-case tag rows by "part of the value printed").
- G2-VK, YAMLError plus ValueError and KeyError: KILLED, 4 FAILED (the RecursionError and AttributeError rows).
- G5-D5, narrowed to ScannerError: KILLED, 16 FAILED (including the Parser, Composer and Constructor rows).
- G6-B3, bound 3 in both files: KILLED, 2 FAILED (`...bounds...[4]`, checker and capture).
- G6-B5, bound 5 in both files: KILLED, 2 FAILED (`...[5]`, both).
- G6-ENV, upper-case `_ENV` exclusion removed in both files: KILLED, 2 FAILED (`API_KEY_ENV` ordinary tests, both files).
- 13 extras, all KILLED:
  - PIN (the whole PIN file): 22 FAILED.
  - G5-ISO: exactly the 4 Parser and Composer tests.
  - G6-B2: 2 FAILED.
  - G6-ENV0: 4 FAILED.
  - Six per-file G6 rows: each fails the lock test plus that file's own behavioural test.
  - D8 (12) and D4 (4): both survived the verifier's run; they die now because the position is pinned exactly.
  - D7: 22 FAILED.

**NOT done:**
- The report file is incomplete (harness refusal, above).
- No re-mint and no `result.json` write (per the brief).
- No commit (no git writes).
- No bug-echo and no registry row: `docs/INCIDENT-LOG.md` is outside my boundary. The class: a handler scoped to `YAMLError` while PyYAML also raises builtin exceptions that quote the input.
- ReaderError has no test row; it prints `(ReaderError) at an unknown position`.
- Read errors are unchanged by design. UnicodeDecodeError still prints one non-UTF-8 byte and an offset.

**DISCREPANCIES:**
- The PC lane's partial diff was not used. Its G2 handler is the kill-table mutant G2-VK, and its YAMLError path has no class.
- Premise "!!timestamp -> ValueError": `2026-13-01` gives ValueError, but `2026-99-99<v>` gives AttributeError. That is a second class outside the handled ones; it is in the G2 table.
- The verifier called D4 and D8 equivalent; both are killed now.
- The brief's report-file demand conflicts with the harness's refusal of subagent report files.
- The mandated pytest runs refresh gitignored `__pycache__` under `proofs/S0-04`.

**ADJACENT defects (reported, not fixed):**
- S0-03, G2's class, verified: `proofs/S0-03/check_omniroute_roundtrip.py:269` catches only `(yaml.YAMLError, UnicodeDecodeError)`, and `:936 def main` catches only Deferred and Failure. A tagged value's ValueError escapes, and its message quotes the whole value (measured on a scratch file: `ESCAPES _read_yaml: ValueError | message quotes the value: True`).
- `scripts/vendored_manifest.py:323` reads `error.problem_mark`, but a ReaderError has no such attribute (verified: False), so a NUL in a SKILL.md frontmatter crashes the handler.
- `scripts/no_laya_in_gates.py:518`: a tag's ValueError escapes and crashes the check (inferred, not run).

## 3. Files and lines changed
`git diff --stat`: 2 files changed, 122 insertions(+), 20 deletions(-). The lines are as listed above.

## 4. Contract items, their tests and their kill rows
- **Item 1 (G2).** `test_capture_leg_reports_a_non_yaml_parse_error_by_class_only` x10: {`!!int`, `!!float` (ValueError); `!!bool` (KeyError); a 5000-deep nesting (RecursionError); a `!!timestamp` that is no date (AttributeError)} x {sk-key, mixed-case}. Each asserts rc 1, the exact line `... is not valid YAML (<Class>) at an unknown position`, and no case-folded 8-character run of the value. The class also appears on all 12 YAMLError rows. Kill rows: G2-OLD and G2-VK.
- **Item 2 (G5).** `test_capture_leg_reports_a_yaml_error_by_position_only[an unclosed flow sequence-{sk-key,hex}]` (ParserError) and `[an alias the profile never defines-{sk-key,hex}]` (ComposerError). Each asserts no 8-character run of the value and the exact `line L, column C` of PyYAML's `problem_mark`. There is also a ConstructorError row. Kill rows: G5-D5, and G5-ISO (exactly these four tests).
- **Item 3 (G6).**
  - `test_the_checker_bounds_a_key_name_tail_at_four_segments[4]` is caught; `[5]` passes.
  - `test_the_capture_guard_bounds_a_key_name_tail_at_four_segments[4]` is withheld; `[5]` prints in full.
  - `test_ordinary_text_passes_the_checker[stray_note-API_KEY_ENV={}]` and `test_capture_leg_passes_ordinary_text_through[stray_note-API_KEY_ENV={}]` pass.
  - Kill rows: G6-B3, G6-B5, G6-ENV. Each edits both files, so the lock test stays green and only behavioural tests can kill.
- **De-vacuous controls.** Every YAML row first asserts, in process, that PyYAML raises exactly that class on that text. Every row whose class quotes input also asserts that PyYAML's own message carries an 8-character run of the value. The handler is then the only reason the value is absent.

## 5. Red, then green
- Red, at the PIN's tool: `22 failed, 156 passed`.
  - All 12 YAML rows failed on the format only: `...is not valid YAML at line L, column C` has no class, and no value was printed.
  - `[an !!int|!!float|!!bool tag-mixed-case]` failed with "part of the value printed". This is G2 through the real CLI. `!!float` and `!!bool` print the value lower-cased; only the case-folded check saw it.
  - The sk-key tag rows printed `<message withheld: credential-shaped>`.
  - The deep nesting printed `capture_leg: RecursionError: maximum recursion depth exceeded`.
  - The timestamp printed `capture_leg: AttributeError: 'NoneType' object has no attribute 'groupdict'`.
- Green after the fix: `178 passed in 11.33s`.

## 6. Kill table
The harness is `<scratch>/i59c/mutate_i59c.py` (kept in scratch). It follows AF-AP-223, AF-AP-78, AF-AP-84 and AF-AP-192:
- The control runs first.
- Each mutant runs in a fresh copy of the pristine tree, whose key-file hashes match the real tree.
- `PYTHONDONTWRITEBYTECODE=1`, with no `__pycache__` in the copy.
- Each edit's anchor must occur exactly once; every mutated file must pass `py_compile`.
- A collect-only pass must show rootdir = the copy and 178 items.
- The verdict comes from JUnit XML: KILLED means at least one FAILED test, 0 errors, 178 total and rc 1.
- The denominator is the literal `EXPECTED=6`; its self-test passes 6 cases.
- The real tree was hashed before and after.

Verdict lines and failing tests are in the hand-back above.

## 7. Gate
Pasted above. The command is the brief's literal one; `--basetemp` came through `PYTEST_ADDOPTS`, pointing at a short scratch dir deleted after each run. `grep -rl -E 'capture_leg|test_s0_04_compression' tests/*.py harness-ports/tests/` prints only `tests/test_s0_04_compression.py`.

## 8. Static checks
- `pyflakes` on both files: rc 0.
- `no_laya_in_gates: 41 files scanned, clean`.
- The separator count (`LC_ALL=C grep -c`) prints 0 for all three written files.
- `ap_screen`: 7 hits.
  - The one on a changed line is AF-AP-39 at T:271 `API_KEY_ENV={}`. It does not apply: that row is about a secret in a shell launcher's argv, and this is a fake value in a test fixture, the same shape as the pre-existing hit at T:258.
  - The other 6 hits are on untouched lines.
- GitNexus `impact do_config`: LOW, 1 caller (`main`).
- `detect-changes`: medium, one flow (`Main -> Provider_block`, changed: do_config). Most of the 12 listed symbols only moved lines. The third changed file is I59-B's.

## 9. Nothing else in the tool changes
`<scratch>/i59c/equiv_i59c.py` runs the PIN's tool and the fixed tool through the real `--config` on the same inputs with the same `--out`. Result: EQUIV PASS.
- Byte-identical rc, stdout, stderr and artifact on nine paths: missing profile, FIFO, directory, non-UTF-8, top-level list, empty profile, a date in `extra_headers`, provider absent, and success on the proof-owned profile.
- Differs only by the inserted class: ReaderError and ScannerError.
- On `!!int`, the fix prints `(ValueError) at an unknown position`. The PIN printed `ValueError: invalid literal for int() with base 10: '<the whole 34-character fake value, elided here>'`.
- The success output equals `proofs/S0-04/evidence/config/hermes-provider.json` byte for byte.
- The script's first run showed one BAD row. That was the instrument's fault: each tool had its own `--out` dir, which the success line prints. It was fixed and re-run.

Venues:
- Under `/root/venv-agent-factory` (PyYAML 6.0.3): `178 passed`.
- `venue_probe.py` loads the 22 YAML rows from the test file's own tables through ast, checks each premise in process, and runs the real CLI with the same interpreter. It found 22 of 22 OK under each of: Python 3.12.3 with PyYAML 6.0.3 (CI's pair), Python 3.12.3 with PyYAML 6.0.1, and Python 3.11.15 with PyYAML 6.0.1.

## 10. DEVIATIONS (flagged)
1. The existing F1b test's last assertion changed. The old regex could not hold once the class joined the message. It now asserts the exact line with the class and PyYAML's position, which is stricter and kills D4 and D8. Its leak check now folds case, and its parametrize ids are now the row labels.
2. A ConstructorError row was added. The verifier's G5 fix named it.
3. The read moved before the `try`. It changes no behaviour (section 9).
4. The wording "is not valid YAML (<Class>)" is used for every class, a RecursionError included. It follows S0-03's sibling form. No consumer parses the text: the runner reads the exit code only.
5. G2-OLD reverts the except clause only; the whole PIN file ran separately as the extra row PIN. "_ENV exclusion removed" is read as A10 (upper case only); removing it in every case (A3) ran as the extra G6-ENV0.
6. The gate's basetemp came through `PYTEST_ADDOPTS`.
7. The G2 table uses a mixed-case kind: a lower-case value cannot show that `!!float` and `!!bool` lower-case their leak.
8. The report file is partial because the harness refused report-file writes. I did not work around it.

## 11-13. NOT done, DISCREPANCIES, adjacent defects
As in the hand-back above.

## 14. Self-attack: the three most likely ways this is wrong
1. **The broad handler hides a bug or changes another path.** The `try` holds only `yaml.safe_load(text)`. Section 9 shows nine non-parse paths byte-identical, the success output equal to the committed evidence, and rc unchanged. KeyboardInterrupt and SystemExit still pass through.
2. **The tests are mirrors.** The oracles are PyYAML's own exception (class and `problem_mark`) and the fake value itself, never the tool's code, and de-vacuous preconditions guard every row. The red run failed 22 tests, each for the stated reason, and 19 of 19 mutants were killed, D4 and D8 included.
3. **The tests hold only on this venue.** They pass under PyYAML 6.0.3, and all 22 rows pass under Python 3.12.3 with PyYAML 6.0.3 and 6.0.1. One residual stays: an 8-character run cannot see a shorter leak. The fix's message holds only the class name, integers and the operator's path, and D7 (the message carrying `str(exc)`) is killed by 22 tests.

## 15. Evidence tiers
- **VERIFIED:** the premise; the red run and the green run; the gate twice and the set id; 6/6 brief mutants and 13/13 extras KILLED; the equivalence check; the three venues; the static checks; the S0-03 escape; the stale attested hash.
- **INFERRED:** that S0-03's escaped exception prints as a traceback (its `main` was not run); the `vendored_manifest.py` and `no_laya_in_gates.py` crash paths.
- **ASSUMED:** that CI's `PyYAML>=6.0` behaves like 6.0.1 and 6.0.3.

Scratch: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/i59c/` (56K). It holds `pc-lane-partial.diff` (kept, sha256 prefix 1f6f47b47bc91fee), `mutate_i59c.py`, `equiv_i59c.py`, `venue_probe.py`, `fixtures_probe.py`, `premise_yaml*.py` and `gn-detect.json`.
