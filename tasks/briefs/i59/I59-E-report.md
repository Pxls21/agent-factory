# I59-E report: S0-03's YAML reader never lets a parse error print a value (task #327)

Lane: code-implementer, sandbox, Opus 5.5. PIN: origin 3ee246d (HEAD f68b23c adds only the brief). Written incrementally;
this final form 2026-09-26 09:2xZ. Evidence tiers: VERIFIED = run here, output pasted; INFERRED = read, not run.

## 0. Verdict

DONE, not landed, not re-minted (the brief's rule). VERIFIED: `_read_yaml` now turns every error of the read and the parse
into `Failure("bundle: <name> is not valid YAML (<Class>)")`, raised `from None`. The 14 new cases: 12 red at the PIN, all 14
green after. Kill table: 6 of 6 mutants KILLED by FAILED cases, 0 errors, after a green CONTROL and a surviving equivalent
mutant. The test file: `209 passed` twice, set 696563f67d3c (floor 195). EXPECTED red, by the batch plan: S0-03's
attestation is now stale (`validate-ledger integrity`: `S0-03 INVALID`), so `tests/test_proof_status.py` is red until the
batch re-mint (section 7).

## 1. Premise: re-measured, it holds (no CONTRACT-INVALID)

- Both files are byte-identical to the PIN (sha256 of the working tree == `git show 3ee246d:<path>`):
  checker 757abf9eb75a..., tests 01bc5d437129....
- The greps match the brief verbatim, at the PIN (the refs below read the PIN; my hunk moved every later line down by 5):
  - `def _read_yaml` C@3ee246d:263
  - its handler `except (yaml.YAMLError, UnicodeDecodeError) as exc` C@3ee246d:269
  - `def main` C@3ee246d:936, `except Deferred as exc` C@3ee246d:945, `except Failure as exc` C@3ee246d:948
  - the last commit on the checker is 5977bc0 (2026-09-19).
- `grep -rl -E 'check_omniroute_roundtrip|S0-03/check' tests/ harness-ports/tests/` names one test file only:
  `tests/test_s0_03_omniroute.py` (plus its own `__pycache__`).
- `_read_yaml` has ONE call site: `load_bundle` C@3ee246d:891 (`profile = _read_yaml`), for `hermes/profile.yaml`, after `direct.json`,
  `hermes-env-names.json` and `leg.json` are read and the credential gate has run.
- Escape probe at the PIN (C loaded through importlib, `_read_yaml` on a scratch file; value = `sk-FAKE-` + 24 random
  letters, every other one upper-case, built in the probe). Extended from the brief's three rows to all five, plus the
  two errors the PIN's `raise Failure` at C@3ee246d:270 already handled:

```
!!int -> ESCAPES ValueError | exact value in msg: True | casefolded in msg: True
!!float -> ESCAPES ValueError | exact value in msg: False | casefolded in msg: True
!!bool -> ESCAPES KeyError | exact value in msg: False | casefolded in msg: True
!!timestamp -> ESCAPES AttributeError | exact value in msg: False | casefolded in msg: False
deep nesting -> ESCAPES RecursionError | exact value in msg: False | casefolded in msg: False
syntax (YAMLError) -> Failure: bundle: hermes/profile.yaml is not valid YAML (ScannerError) | ctx=ScannerError
bad utf-8 (read) -> Failure: bundle: hermes/profile.yaml is not valid YAML (UnicodeDecodeError) | ctx=UnicodeDecodeError
```

- Finding beyond the brief (inferred from the `ctx=` column, proven red in section 3): the PIN's `raise Failure` (C@3ee246d:270) chains the
  original exception as `__context__` (no `from None`). `main` prints `str(exc)` only, so the CLI never shows it, but
  a traceback of that Failure would print PyYAML's message, and a ScannerError's snippet quotes the value.
- Suite at the PIN (`bash scripts/test_summary.sh tests/test_s0_03_omniroute.py --basetemp=<scratch>/bt`, rc 0):

```
pytest-exit: 0
pytest-summary: 195 passed in 22.12s
1 files set=696563f67d3c
```

- Toolchain: Python 3.11.15, PyYAML 6.0.1 (no libyaml), pytest 9.1.1, recursion limit 1000.

## 2. The change

- `proofs/S0-03/check_omniroute_roundtrip.py` C:269-275 (`except Exception as exc` down to the `raise Failure` line),
  `_read_yaml` only; diffstat 9 lines, 7 in, 2 out. The handler catches `Exception` around the read and `yaml.safe_load`
  (both already inside the try block) and raises the PIN's form (`raise Failure` at C@3ee246d:270), the class name only,
  now `from None`. `_require_file` and the lazy `import yaml` stay outside the `try`, unchanged. `git diff -U1` shows one hunk.
- GitNexus `impact _read_yaml --direction upstream`: risk LOW, epistemic exact, 1 direct caller (`load_bundle`), then
  `check_bundle`. The grep agrees: one call site, `profile = _read_yaml` at C:896 in the working tree.
- `tests/test_s0_03_omniroute.py`: three stdlib imports (`secrets`, `string`, `traceback`) and one block after
  `test_malformed_json_is_a_named_failure`: T:826-913 (`PROFILE_PARSE_ERRORS`, three helpers, two parametrized tests,
  7 rows each, 14 cases). Diffstat 93 lines in, 0 out.

## 3. Tests: red at the PIN, green after

Rows. The key is `sk-FAKE-` + 24 random ASCII letters, every other one upper-case, built per case by `_fake_key()`, added
as a line `api_key: ...` under the provider block of the passing bundle's `hermes/profile.yaml`:

| row | line added | exact class | PyYAML's message carries the key |
|---|---|---|---|
| int-tag | `api_key: !!int <key>` | ValueError | verbatim |
| float-tag | `api_key: !!float <key>` | ValueError | lower-cased only |
| bool-tag | `api_key: !!bool <key>` | KeyError | lower-cased only |
| timestamp-tag | `api_key: !!timestamp <key>` | AttributeError | no |
| deep-nesting | `api_key: ` + 5,000 `[` + key + 5,000 `]` | RecursionError | no |
| syntax-error (preservation) | `api_key: <key>: x` | yaml.scanner.ScannerError | verbatim (the snippet) |
| invalid-utf8 (preservation) | `api_key: <key>` + byte 0xff | UnicodeDecodeError | no |

The two tests:

1. `test_profile_parse_error_is_a_named_failure_that_never_prints_the_key[<row>]`, the contract test, through the real
   CLI (`run_checker`: a subprocess of `main`). In process first: parsing the file raises exactly the row's class
   (`type(...) is cls`); where the class quotes, the message carries the key (verbatim, or lower-cased and NOT verbatim),
   and the leak screen finds it there. Then the CLI run and the four CLI assertions below.
2. `test_profile_parse_failure_chains_no_error_that_quotes_the_key[<row>]`, in process on `check._read_yaml`: the four
   in-process assertions below. It locks the `from None` (deviation D1).

The assertion legend (the names the tables below use):

- stdout screen: T:894 `_leaked_runs(key, result.stdout)` is empty
- stderr screen: T:895 `_leaked_runs(key, result.stderr)` is empty
- exit 1: T:896 `result.returncode == 1`
- exact line: T:897 `result.stdout.strip()` equals `failure_reason: bundle: hermes/profile.yaml is not valid YAML (<Class>)`
- escape: T:908 `check._read_yaml(profile, "hermes/profile.yaml")` raises the builtin, not a Failure
- exact message: T:910 `str(failure)` equals `bundle: hermes/profile.yaml is not valid YAML (<Class>)`
- render screen: T:912 `_leaked_runs(key, rendered)` over `traceback.format_exception` of the Failure is empty
- from-None check: T:913 `failure.__suppress_context__` is set and `__cause__` is None

Red at the PIN. The tree's checker was still the PIN's (sha256 757abf9eb75a); `-k profile_parse --tb=line -rA`; the reason
per case is read from its `--tb=line` output:

| case | CLI test | in-process test |
|---|---|---|
| int-tag | FAILED: stderr screen (`the key leaked to stderr`) | FAILED: escape (`ValueError: invalid literal for int() with base 10: 'sk-FAKE-...'`) |
| float-tag | FAILED: stderr screen | FAILED: escape (`ValueError: could not convert string to float: 'sk-fake-...'`) |
| bool-tag | FAILED: stderr screen | FAILED: escape (`KeyError: 'sk-fake-...'`) |
| timestamp-tag | FAILED: exact line (stdout empty; a traceback) | FAILED: escape (`AttributeError: 'NoneType' object has no attribute 'groupdict'`) |
| deep-nesting | FAILED: exact line (stdout empty; a traceback) | FAILED: escape (`RecursionError: maximum recursion depth exceeded while calling a Python object`) |
| syntax-error | PASSED | FAILED: render screen (`the key rides the rendered traceback`) |
| invalid-utf8 | PASSED | FAILED: from-None check (`assert (None is None and False)`) |

```
12 failed, 2 passed, 195 deselected in 3.14s
```

The keys in those messages were fake, built in the test. The float-tag and bool-tag leaks are all lower-case, and every
8-run of the key holds an upper-case letter (the helper asserts it), so only the case-folded screen sees them: a
case-sensitive screen would have passed both rows at the PIN. The syntax-error red in the in-process test is the PIN's
latent leak, proven: a traceback of the PIN's `raise Failure` (C@3ee246d:270) prints the chained ScannerError, whose snippet
quotes the key.

Green after the fix (`-k profile_parse --tb=short -rA`): all 14 PASSED.

```
14 passed, 195 deselected in 3.14s
```

## 4. The kill table

Harness: `<scratch>/i59e/killtable.py` (deleted after the run). Every variant runs in a scratch tree, never in the real
tree (anti-hollow-green 3a): `git archive 3ee246d -- proofs/S0-03 proofs/schemas tests/conftest.py pyproject.toml`, the
working tree's test file on top (sha-checked), the variant written as the tree's checker, `__pycache__` cleared,
`PYTHONDONTWRITEBYTECODE=1` (AF-AP-192), `PYTHONPATH` dropped. Each variant must compile and collect exactly 14 cases
(3c). The tests are proven to load the scratch checker (`CHECKER` and `check.__file__` both resolve into the scratch tree:
True; 3b). The CONTROL runs first and must pass 14/14, and an equivalent mutant must SURVIVE (AF-AP-223). A kill needs a
FAILED junit case with 0 errors and 0 skips. The denominator is a literal, `EXPECTED=6` (AF-AP-84). The real checker's
sha256 was 3dbf485fc95c before and after.

| id | variant | pytest | verdict | the assertions that fired (each a FAILED case, 0 errors) |
|---|---|---|---|---|
| CONTROL | the fixed checker | 14 passed | green (required) | none |
| EQUIV | `exc.__class__.__name__` to `type(exc).__name__` | 14 passed | SURVIVED (required) | none |
| K1 (brief) | the PIN's handler `(yaml.YAMLError, UnicodeDecodeError)`: the PIN file verbatim | 2 passed, 12 failed | KILLED | CLI int/float/bool: stderr screen; CLI timestamp/deep: exact line; in-process int/float/bool/timestamp/deep: escape; in-process syntax-error: render screen; in-process invalid-utf8: from-None check |
| K2 (brief) | the PIN's tuple + `ValueError` + `KeyError` | 10 passed, 4 failed | KILLED | CLI timestamp/deep: exact line; in-process timestamp/deep: escape |
| K3 (brief) | the message carries `str(exc)` | 0 passed, 14 failed | KILLED | CLI int/float/bool/syntax-error: stdout screen; CLI timestamp/deep/invalid-utf8: exact line; in-process all 7: exact message |
| K4 (lane) | `from None` dropped | 7 passed, 7 failed | KILLED | in-process int/float/bool/syntax-error: render screen; in-process timestamp/deep/invalid-utf8: from-None check |
| K5 (lane) | the read moved outside the `try` (S0-04's do_config shape) | 12 passed, 2 failed | KILLED | CLI invalid-utf8: exact line; in-process invalid-utf8: escape |
| K6 (lane) | an enumerated builtin handler without `yaml.YAMLError` | 12 passed, 2 failed | KILLED | CLI syntax-error: stderr screen; in-process syntax-error: escape |

```
EXPECTED=6 RAN=6 KILLED=6 SURVIVED=0 INVALID=0
KILL-TABLE GATE: PASS
```

A test-aware rule set classified every failed case from its junit message; CLI cases can match only the four CLI
assertions, in-process cases only the four in-process ones: `cases not matched by exactly one rule: 0`. The exit-1 check
fires under no mutant: an uncaught exception also exits 1, so the exact line is the discriminating check there. K3 proves
the stdout screen has teeth; K1 and K6 prove the stderr screen.

Driver self-test (`KILLTABLE_DROP=K3`, one row deleted): harness rc 1, `EXPECTED=6 RAN=5 KILLED=5 SURVIVED=0 INVALID=0`,
`KILL-TABLE GATE: FAIL`. The five variants it re-ran reproduced the same counts with fresh keys: a second observation of
the table.

## 5. Gates (VERIFIED, pasted)

`bash scripts/test_summary.sh tests/test_s0_03_omniroute.py --basetemp=<scratch>/bt`, twice (deviation D5), then the set id:

```
run 1 rc=0
pytest-exit: 0
pytest-summary: 209 passed in 24.70s
run 2 rc=0
pytest-exit: 0
pytest-summary: 209 passed in 25.35s
1 files set=696563f67d3c
```

- pyflakes on both files: rc 0, no output.
- `python3 scripts/no_laya_in_gates.py`: `no_laya_in_gates: 41 files scanned, clean`, rc 0.
- `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: 0 for the checker, 0 for the test file, 0 for this report.
- `python3 scripts/ap_screen.py` on the whole checker: `--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---`.
- `python3 scripts/ap_screen.py --tests` on the whole test file: 6 hits, none in my block; the PIN's copy of the file
  screens the same 6, 93 lines earlier:
  - the `pkill` docstring: T:1068, at the PIN T@3ee246d:975 (`pkill`)
  - `pc_mention.sh`: T:1785, at the PIN T@3ee246d:1692 (`pc_mention.sh`)
  - `current-framedir`: T:1794, at the PIN T@3ee246d:1701 (`current-framedir`)
- Build-loop gate rule (every test that names the changed path): `grep -rl -E 'check_omniroute_roundtrip|S0-03/check'
  tests/ harness-ports/tests/` names only `tests/test_s0_03_omniroute.py`. The attestation reads the path as data; its
  test is in section 7.
- report_lint: see the last line of this report.

## 6. Deviations (each one loud)

- D1, `from None` added. The contract asks for the form the PIN's `raise Failure` (C@3ee246d:270) uses; the brief also names S0-04's
  `do_config` as the shape to copy, and that shape raises `from None`. Evidence that it matters: at the PIN, the Failure
  chains the original error, and a traceback of it prints the ScannerError's snippet, which quotes the key (section 3, the
  syntax-error row of the in-process test). `main` prints `str(exc)` only, so the CLI never showed it; the leak was
  latent. Revert: drop ` from None` at C:275, delete the in-process test, drop K4.
- D2, two preservation rows beyond the brief's five: syntax-error (a ScannerError that quotes the key) and invalid-utf8.
  Both were green at the PIN in the CLI test. They kill K6 (a handler that lists builtins and drops the YAMLError base)
  and K5 (the read moved outside the `try`: the sibling's shape, which this brief rejects for S0-03).
- D3, a second test, in process rather than through the CLI. The CLI test is the contract's test; the in-process test
  locks D1 only.
- D4, the kill table carries three extra mutants (K4-K6) and an EQUIV control beside the brief's three (K1-K3). K1 is
  the PIN file verbatim: the PIN's handler, and nothing else differs, since my hunk is the only change.
- D5, `test_summary.sh` ran with one extra argument, `--basetemp=<scratch>/bt` (the brief's disk rule). The set id is
  computed over the file list alone, so it is unchanged.
- D6, the premise probe covers all five contract rows plus the two preservation rows; the brief's measured block had three.

## 7. NOT done

- Not landed: no git write of any kind (the brief). The coordinator commits the two files and this report.
- Not re-minted (the brief). VERIFIED consequence, as the batch plan intends: `python3 scripts/validate-ledger integrity
  --root .` exits 1 with `S0-03 INVALID` and `attestation-mismatch: S0-03 proofs/S0-03/check_omniroute_roundtrip.py`.
  In this tree `tests/test_proof_status.py::test_committed_state_passes_status_and_ledger` FAILED (`1 failed in 0.80s`;
  its body is at tests/test_proof_status.py:85, `def test_committed_state_passes_status_and_ledger`). The same run also
  shows `S0-05 INVALID` from I59-B's `run_s0_05_units.sh`; S0-03 is INVALID from my change alone. CI would be red if
  this change landed without the batch re-mint (the plan's #315).
- Not run on the PC (no bridge, the standing rules), not run on CI (no push). The deep-nesting row depends on the
  recursion limit: 5,000 levels need about 10,000 frames (494 levels trip the default 1,000), and the row's in-process
  precondition fails loud, never green, where a raised limit stops the error.
- The full repository suite was not run; the brief names one test file.
- AF-AP-232's registry row in `docs/INCIDENT-LOG.md` is not updated (outside the boundary): section 10's verified
  sibling belongs in it.

## 8. Discrepancies

- None with the brief's measured premise: every cited line, the commit, the grep, the count and the set id matched.
- The brief's WHY names the `!!bool` KeyError and the bad-`!!timestamp` AttributeError; its measured block did not. I
  measured both: they hold (section 1).
- The brief names the PIN's `raise Failure` (C@3ee246d:270) as the form to keep. At the PIN it chains the quoting error into `__context__`, a latent
  leak; see D1.
- Two corrections of my own, both before any conclusion rested on them. I first cited the hunk as ending one line late (on
  the blank context line after the `raise Failure` line); section 2 has the right range. My first classifier of the kill reasons put five CLI cases under the in-process
  escape rule (the stderr tail carried by the exact-line message names the class); the test-aware rewrite classified all
  41 failed cases, 0 unmatched, and only its output is used here.

## 9. Self-attack: the three likeliest ways this is wrong

1. `except Exception` is too broad and hides a checker bug as "not valid YAML". Ruled out: the `try` body is two library
   calls, the read and `yaml.safe_load`, so every exception there is a failure to read or parse the evidence file. The
   result fails closed (exit 1, a named reason, the class kept, so an OSError or MemoryError stays distinguishable).
   BaseException (KeyboardInterrupt, SystemExit) still propagates. `_require_file` keeps its own reasons outside the
   `try`: the FIFO, directory and absent-file tests for `hermes/profile.yaml` pass within the 209.
2. The oracle is blind (a hollow green): the key never reaches PyYAML's message, or the screen misses a changed copy.
   Ruled out. Each row's precondition asserts the exact class and, where the class quotes, that the message carries the
   key and that the screen finds it there. At the PIN the stderr screen fired on the three quoting rows; under K3 the
   stdout screen fired on four rows. The lower-cased leaks are visible only case-folded, and the helper asserts that
   every 8-run of the key holds an upper-case letter. The screen's alphabet (anti-hollow-green 3f): the generator draws
   `sk-FAKE-` + 24 ASCII letters in alternating case. It cannot draw digits, `_` or non-ASCII; `!!int` and `!!float`
   strip `_` before they quote, so a key holding `_` would print altered, which this alphabet does not cover.
3. The change moves a verdict elsewhere (a passing bundle fails, or a negative bundle's reason changes). Ruled out: the
   handler runs only on an exception, and the passing fixture and every committed negative bundle's exact reason are
   pinned by existing tests, all within the 209 passed, twice.

Residual, stated: with `from None`, `failure.__context__` still references the quoting error (Python sets it on any
raise inside a handler; `from None` only hides it from a rendered traceback). A caller that walks `__context__` by hand
would reach it. Nothing in the repository does this for this checker; `main` prints `str(exc)` only.

## 10. Adjacent findings: the AF-AP-232 echo, read only, never fixed

- VERIFIED, a new sibling: harness-ports/bin/hermes-config-merge.py:83 runs `yaml.safe_load(cfg_path.read_text())` on the
  owner's Hermes config (`--config ~/.hermes/config.yaml`, run on the PC at bring-up, over the bridge), with no handler.
  A Hermes config can hold an inline provider key. Probe on scratch files only (a fake config holding
  `api_key: !!int <fake key>`, `--dry-run`): rc 1, and the traceback printed the fake key verbatim on 1 line. It is not
  in AF-AP-232's row.
- INFERRED, low: tests/test_skill_frontmatter.py:28 has `except yaml.YAMLError as e` around committed SKILL.md
  frontmatter. A tagged value would crash the label function with a traceback instead of returning a reason. No secret
  source (committed files). Not in the row.
- Already in the row (task #328): scripts/vendored_manifest.py:322 (`except yaml.YAMLError as error`),
  scripts/no_laya_in_gates.py:518 (`except yaml.YAMLError`); S0-04's proofs/S0-04/tools/pc/capture_leg.py:241
  (`except yaml.YAMLError as exc`), fixed by the held I59-C patch, which is not in the tree.
- Checked, not siblings: scripts/qwen_jev.py:153 (`yaml.safe_load(fh)` on `upstream.lock.yaml` inside `except Exception`,
  which falls back). The other `yaml.safe_load` sites under `proofs/`, `scripts/` and `src/` parse committed key-free
  files (lock files, an SBOM, seeds).
- INFERRED: `_read_json` in the same checker also chains, but JSON's messages carry positions, not content
  (`JSONDecodeError`, the `_reject_constant` ValueError, UnicodeDecodeError). Not a leak carrier; unchanged (boundary).

---
report_lint (`--map C=<checker> --map T=<test file> --min-refs 20`, working tree), rc 0: `report_lint: 37 refs — OK 37, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`
