# C1 — scripts/verify_command.py: Canny's verify-command classifier, ported (D-052, task #147)

**Role:** `code-implementer`, IN THE SANDBOX, in the shared tree (no worktree isolation; it fails on this tree). Honey `ultra`
Lever-2: your report is DATA — files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

**PIN:** `4e6adfc` (origin head at authoring). **Boundary (touch ONLY these):** CREATE `scripts/verify_command.py`, CREATE
`tests/test_verify_command.py`, CREATE `tasks/briefs/canny/C1-report.md` (write it incrementally from the start). READ-ONLY:
the Canny clone at `/home/user/qkal/canny` (@ f2c5e53, MIT) — static reading only: never run, build, install or import
anything from it. Do NOT touch `sandbox-kit/` (a live PC lane, K1-h, is rewriting the vendored manifest; the coordinator adds
the THIRD-PARTY-AGENT-TOOLS.md row after it lands). Two sandbox verifier agents run beside you on disjoint files; never touch
`tasks/briefs/s0-05-support/` or `tasks/briefs/laya/`. Never `git add` / commit / push / stash / checkout / restore; never
open issues, PRs or comments.

## Why (owner ruling D-052, 2026-09-23)

A lane can report "tests pass" while the command it ran hid the test's exit status (`pytest | tail`, `pytest || true`,
`pytest; echo done`). Canny's `isVerify` decides, from the command text alone, whether a command is a test, build or lint
check whose exit status reaches the caller. We port its deterministic core as first-party code (never install Canny), with
its tables as our tests. C2 (task #148, a later PC lane) will consume this module for a lane done-gate. No Jev, no model, no
network anywhere in this module.

## The contract (decided; a line you cannot meet is a DISCREPANCY with its measurement, never a silent change)

1. **Port, do not redesign.** Translate `canny/src/checks.ts:8-12` (the three `VERIFY` regexes, 78 alternatives, verbatim),
   `:35-45` (`PRINTS_OR_INSPECTS`, `ASKS_ONLY`, `NEGATED`, `notACheck`), `:48-50` (`executed`), `:58-80` (`isVerify`) and
   `:88-93` (`withPipefail`) into Python with the same behavior. Public names: `VERIFY` (the three compiled patterns),
   `executed(command) -> str`, `is_verify(command, patterns=None) -> bool`, `with_pipefail(command, patterns=None) -> str |
   None`. `patterns` is the equivalent of Canny's `config.verify`: a list of regex strings that REPLACES the defaults when
   given (not added to them), each tested against the check command with `re.search`.
2. **Regex semantics.** The JS regexes carry no `u` flag, so `\b` and `\w` are ASCII: compile with `re.ASCII`. JS `^` without
   `m` matches only at the string start, as Python's does without `re.MULTILINE`; keep that. JS `\s` also matches Unicode
   spaces (NBSP, U+2028) while Python's `\s` under `re.ASCII` does not; bash does not split words on NBSP either. State your
   choice in the module docstring and pin it with one test row (a command holding U+00A0 before `--help`).
3. **One deliberate deviation, fail-loud.** Canny's `safeRegex` turns an invalid configured pattern into "never matches".
   Here an invalid pattern in `patterns` raises `ValueError` naming the pattern (a silently dead pattern is a fail-soft). Say
   so in the docstring.
4. **The MIT notice.** The module header carries Canny's copyright line (`Copyright (c) 2026 Kal`, from
   `/home/user/qkal/canny/LICENSE:3`), the full MIT permission notice, the source (`qkal/canny @ f2c5e53, src/checks.ts`), and
   the sentence "Ported by agent-factory (D-052); behavior matches src/checks.ts:8-93 except where this docstring says
   otherwise." The test file header names `test/checks.test.ts:47-137` and `:238-242` as the source of its tables.
5. **CLI.** `python3 scripts/verify_command.py [--pattern REGEX]... [--with-pipefail] -- COMMAND`: without `--with-pipefail`
   prints `counts` and exits 0, or prints `does-not-count` and exits 1; with it, prints the rewritten command and exits 0, or
   prints nothing and exits 1. Usage errors (no `--`, an empty COMMAND, an invalid `--pattern`) exit 2 with one stderr line.
   Standard library only; no import of anything under `src/` or `sandbox-kit/`.

## Tests (`tests/test_verify_command.py`; each written RED first against a stub-free empty module, then GREEN; paste both)

- **Canny's 27-row table** (`test/checks.test.ts:49-75`), every row with its expected value, as one parametrized test.
- **The product tables** (`:80-131`): the 11 checks × 14 hiding forms (none may count, 154 commands) and 11 × 13 keeping forms
  (all must count, 143 commands), each as ONE test that collects every failing command and asserts the list is empty (so a
  red prints every offender, as Canny's does).
- **The override** (`:133-136` and `:238-242`): `patterns=["^just check$"]` turns `pnpm test` off and `just check` on;
  `patterns=["^npm test$"]` counts `set -o pipefail; npm test | tail -5`, and `with_pipefail("npm test | tail -5", …)` returns
  `set -o pipefail && npm test | tail -5`.
- **Our additions (label them as ours in a comment):** `   echo tsc` (leading spaces; Canny's own comment at `checks.ts:33-34`
  names it as a past bypass) does not count; the NBSP row of item 2; `with_pipefail` returns None for `npm test | head -5`
  (only `tail` qualifies) and for a command that already counts; an invalid `patterns` entry raises `ValueError`; the CLI's
  three exit codes, run as a subprocess with `sys.executable`.

## Mutants (scratch-copy restore only, never a git restore; each must compile and collect — AF-AP-78; paste the failing test per row)

At least: M1 quoted-string removal dropped from `executed`; M2 comment removal dropped; M3 pipefail always false; M4 pipefail
from the FIRST `set` instead of the last; M5 the `||` rule dropped; M6 the lone-`&` rule dropped; M7 `NEGATED` dropped; M8
`ASKS_ONLY` dropped; M9 the `\s*` in `PRINTS_OR_INSPECTS` dropped; M10 `with_pipefail`'s tail-only test dropped; M11
`patterns` added to the defaults instead of replacing them. Each: mutant · compiles · collected count · killed by (test id)
or SURVIVED / EQUIVALENT with the reason.

## Gates (paste verbatim)

`mkdir -p /tmp/c1/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_verify_command.py -q -p no:cacheprovider
--basetemp=/tmp/c1/bt` twice (`rm -rf /tmp/c1/bt` after each) · `/root/venv-agent-factory/bin/python -m pyflakes
scripts/verify_command.py tests/test_verify_command.py` · `python3 scripts/ap_screen.py scripts/verify_command.py` and
`python3 scripts/ap_screen.py --tests tests/test_verify_command.py` · `python3 scripts/no_laya_in_gates.py` (must stay clean) ·
the report lint: `python3 scripts/report_lint.py --min-refs 8 --map V=scripts/verify_command.py --map
T=tests/test_verify_command.py tasks/briefs/canny/C1-report.md --root .` (cite `V:<line>` / `T:<line>`; apply its `fix:`
hints for at most three rounds, then paste and finish).

## Report (`tasks/briefs/canny/C1-report.md`)

Sections: premise re-measured (item 1 of the lane: re-run the premise commands below and stop CONTRACT-INVALID on a mismatch)
· what was built (V:/T: refs) · the RED then GREEN runs · the mutant table · gates (pasted) · DISCREPANCIES (every place the
port differs from Canny, with the reason) · NOT-done.

## PREMISE — MEASURED at authoring (2026-09-23, sandbox @ 4e6adfc; the Canny clone @ f2c5e53)

```
$ git -C /home/user/qkal/canny log -1 --format='%h %s'
f2c5e53 chore(release): 0.3.0 (#21)
$ wc -l src/checks.ts test/checks.test.ts ; sha256sum (first 16) src/checks.ts test/checks.test.ts LICENSE
  250 src/checks.ts
  266 test/checks.test.ts
1d3f36a1063542ee  src/checks.ts
d5297358e03e58cc  test/checks.test.ts
0ba25891a959268c  LICENSE
$ head -3 LICENSE
MIT License

Copyright (c) 2026 Kal
$ the VERIFY alternatives, split at the top-level '|' of each regex (checks.ts:9-11)
checks.ts:9 alternatives=33 first=pytest last=nox
checks.ts:10 alternatives=20 first=tsc last=webpack
checks.ts:11 alternatives=25 first=eslint last=shellcheck
total 78
$ the test tables (checks.test.ts): the isVerify rows are lines 49-75 (27 rows); checks :80-92 (11); hides :93-108 (14
  forms); keeps :109-123 (13 forms); the override :133-136; the pipefail-feeding config test :238-242
$ ls scripts/verify_command.py tests/test_verify_command.py
ls: cannot access 'scripts/verify_command.py': No such file or directory
ls: cannot access 'tests/test_verify_command.py': No such file or directory
$ grep -rn -l -E 'verify_command|is_verify|isVerify' scripts tests harness-ports
tests/test_laya_probe_report.py      (its own docstring words "verify_command equivalent"; no symbol clash)
```
