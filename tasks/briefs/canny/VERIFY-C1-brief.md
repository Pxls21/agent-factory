# VERIFY-C1 — the targeted adversarial verify of Canny's verify-command classifier, ported (`scripts/verify_command.py`, D-052)

**Role:** `adversarial-verifier` (Opus 5), IN THE SANDBOX. Honey `full`: line-bounded findings, evidence anchors, SOLID/UNSURE on
every claim. Your report is DATA for the coordinator's gate; you return a GATE RECOMMENDATION, never a verdict. Do NOT spawn
subagents.

**PIN:** `ea9538a` (origin head at authoring). The C1 boundary is unchanged since its landing `9c70322` (measured below). Work on
the tree READ-ONLY: every mutant and every hostile corpus lives in a scratch copy under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vc1/` (a `git archive ea9538a scripts/verify_command.py
tests/test_verify_command.py pyproject.toml`). The ONLY file you write in the tree is your report
`tasks/briefs/canny/VERIFY-C1-report.md` (write it incrementally from the start). A sandbox build lane (J1-2-R1) is live in this
tree on `src/agent_factory/decisions/ledger.py`, `tests/test_decisions_ledger.py` and `tasks/briefs/laya/`: never touch, run or
read-as-evidence those. Never `git add` / `commit` / `stash` / `checkout` / `restore`; no issues, PRs or comments. The sandbox has
about 2 GB free: keep scratch small and delete it at the end. The Canny clone at `/home/user/qkal/canny` (@ f2c5e53, MIT) is
STATIC READING ONLY: never run, build, install, import or require any file of it. You MAY evaluate Canny's regex LITERALS,
copied as text into your own `node -e` one-liners (node v22.22.2 is at `/opt/node22/bin/node`), as an independent oracle for
JavaScript regex semantics.

## What landed (V = `scripts/verify_command.py` 273 lines, T = `tests/test_verify_command.py` 302 lines, at the PIN)

Contract: `tasks/briefs/canny/C1-brief.md` items 1-5 (port `canny/src/checks.ts:8-93` with the same behavior; `re.ASCII`; one
deliberate deviation — an invalid pattern raises `ValueError`; the MIT notice; the CLI's exit codes 0/1/2). Its WHY, which the
contract serves: "A lane can report 'tests pass' while the command it ran hid the test's exit status (`pytest | tail`, `pytest ||
true`, `pytest; echo done`). Canny's `isVerify` decides, from the command text alone, whether a command is a test, build or lint
check whose exit status reaches the caller." C2 (a later lane) will gate lane reports on `is_verify`, so a command that COUNTS
but hides the status is the expensive error (a hollow green); one that does not count but would have reached is cheap (a nudge).
The builder's report `tasks/briefs/canny/C1-report.md` (with the coordinator's landing touch at its end) is an INPUT to attack,
never evidence.

- V:50-76 `VERIFY` (the three regexes, 78 alternatives) · V:79-88 the deny lists · V:91 `_not_a_check` · V:100
  `_compile_patterns` · V:111 `executed` · V:123 `is_verify` (the pipefail scan V:138-142, the last segment V:145-150, the `&&`
  parts V:155-174) · V:179 `with_pipefail` · V:202 `_cli`.
- T: Canny's 27-row table, the 11 × 14 hiding and 11 × 13 keeping products, the override rows, the builder's additions, and the
  coordinator's two rows (M1, M5 kills) and `__file__`-resolved CLI path.

## PREMISE — MEASURED (coordinator, 2026-09-23 04:5x-05:0xZ, sandbox @ ea9538a)

```
$ git log --format='%h %s' -- scripts/verify_command.py tests/test_verify_command.py
9c70322 C1 landed (GATED-PENDING-VERIFY): Canny's verify-command classifier ported to scripts/verify_command.p
$ sha256[:16] + lines
8420e9a202de6afb 273 scripts/verify_command.py
a9aedce65126da71 302 tests/test_verify_command.py
$ /root/venv-agent-factory/bin/python -m pytest tests/test_verify_command.py -q -p no:cacheprovider --basetemp=/tmp/vc1p/bt
45 passed in 0.22s
$ for c in …; do python scripts/verify_command.py -- "$c"; done      (one argv string each)
pytest && false || true                  counts
pytest && true || true                   counts
pytest && echo ok || true                counts
trap 'exit 0' EXIT; pytest               counts
pytest | tee log                         does-not-count
set -o pipefail; pytest |& tee log       does-not-count
pytest <&0                               does-not-count
make test-unit                           counts
npm test -- --version                    does-not-count
(pytest || true)                         does-not-count
pytest; true                             does-not-count
time pytest                              counts
pytest & wait                            does-not-count
false || pytest                          does-not-count
$ bash as the oracle (the check stubbed to fail: a shell function returning 3)
bash rc (pytest stubbed to 3, && echo ok || true) = 0
bash rc (trap exit 0; pytest stubbed to 3) = 0
$ bash -c 'false && false || true; echo $?' ; bash -c 'true && false || true; echo $?'
rc(fail && false || true)=0
rc(pass && false || true)=0
$ python scripts/verify_command.py -- true "pytest"        (TWO argv words after --)
counts
rc=0 (argv: true, pytest)
$ python scripts/verify_command.py -- 'true "pytest"'      (ONE argv string)
does-not-count
rc=1 (argv: one string)
$ Canny src/checks.ts:67-78 (static read): `last.split("&&").some((raw) => { … if (part.includes("||") || (!pipefail &&
  part.includes("|"))) return false; …` — the `||` test is per `&&`-part, as in the port (V:155-158)
```

So the coordinator already holds three hollow-green seeds that count while bash returns 0 with the check failing (a `||` in a
LATER `&&`-part than the check; an EXIT trap that exits 0), and one CLI shape (separate argv words lose their quoting before
`executed` runs). They are upstream-faithful (Canny has the same `||` rule). Your value is the whole class and the shapes nobody
tried; do not spend your budget re-deriving the seeds.

## ITEMS (discovery exhaustive; disposition disciplined)

Number your findings F1…; for each: evidence level (reproduced / read / inferred), file:line, expected vs observed, the cheapest
red control, and the blocking predicate (contract-mapped · reproduced through the real production path · materially effective ·
a concrete discriminator · in boundary). A red test is necessary, never sufficient. An upstream-FAITHFUL shape that defeats the
WHY above is a CONTRACT-DEFECT (the contract said "port, do not redesign"): write the one-line amendment you would propose
(for example "deviation 2: …"), never a BLOCKER against a faithful port.

1. **Port fidelity, regex by regex.** Compare, character by character, every regex and split in V with `checks.ts:8-93`:
   the three `VERIFY` literals (78 alternatives), `PRINTS_OR_INSPECTS`, `ASKS_ONLY`, `NEGATED`, both `executed` replacements
   (including `$1` vs `\1`), the pipefail scan and its "last one wins" (`.at(-1)?.[1] === "-"`), `split(/[;\n]/)` +
   `.findLast(Boolean)`, `split("&&")`, the lone-`&` test, `part.split("|")[0]`, and the `withPipefail` tail test. For every
   semantic difference between JS (no `u` flag) and Python (`re.ASCII`) — `\b`, `\w`, `\s`, lookbehind, `^` — build the input
   that shows it, and use `node -e` on the copied literal as the JS oracle. List any divergence that changes an `is_verify` or
   `with_pipefail` answer.
2. **THE hollow-green class — bash is the oracle.** For every command the port COUNTS, the check's failure must reach bash's exit
   status. Build a harness: run the command in `bash -c` inside a scratch dir with every check word stubbed to exit 3 (shell
   functions for bare words such as `pytest`, `npm`, `make`, `python`; stub executables on a scratch `PATH` or at `./gradlew` for
   path forms), under `timeout 10`, and flag every command that counts but exits 0. Seed it with the premise's three shapes, then
   hunt: `||` in any later `&&`-part; `trap … EXIT` / `trap … ERR`; `exec`; subshells and brace groups `( … )` / `{ …; }`;
   functions; `set +e` / `set -e` interplay; `; exit 0` vs `&& exit 0`; `:` and `true` tails; here-docs and `$( … )` /
   backticks; `time`, `nice`, `env X=1`, `timeout`, `xargs`; `if …; then …; fi` and `while`; `!` in later positions; line
   continuations; CRLF; the 11 × 14 hiding forms re-run through bash (every one must be a real hide); and the 11 × 13 keeping forms
   (every one must be a real keep — a "keep" bash says hides is also a finding). Report the class, not just instances: which
   rule of `is_verify` each shape slips, and the smallest rule change that closes it without flipping a Canny table row.
3. **False negatives (the cheap direction).** List, as INFO, shapes whose status reaches bash but the port refuses (for example
   `pytest | tail; exit ${PIPESTATUS[0]}`, `pytest <&0`, `set -o pipefail; pytest |& tee log`). One line each; no disposition
   beyond INFO unless one is a Canny table row the port gets wrong.
4. **`with_pipefail`.** Every rewrite it returns must (a) count under `is_verify` and (b) keep the check's failure in bash's
   exit status with pipefail on — run each through the item-2 harness. Try pipes into `tail -f`, `tail --pid`, `tail` with a
   file argument, `tailx`, `| tail | head`, `| tail || true`, multiple pipes, `|&`.
5. **The CLI (V:202-273).** The premise measured the argv-join hazard: map it (which quoting the caller's shell removes, and
   whether any shape turns a does-not-count command into counts or the reverse), then attack the rest: `--` twice, an argument
   starting with `-` after `--`, `--pattern` without a value, an invalid `--pattern`, an empty or whitespace-only COMMAND, a
   NUL-free non-UTF-8 argv byte (`surrogateescape`), and the exit codes 0/1/2 with the exact stdout/stderr lines the contract
   names. Grade the join against contract item 5 and the WHY: is a single-string COMMAND the contract, and should the CLI
   refuse more than one word after `--`?
6. **`patterns` (the override).** `[]` (never counts), a catch-all `.*`, an anchored `^npm test$` against the pipe feeder,
   Unicode in a pattern, a pattern with a lookbehind, an invalid one (`ValueError` naming it), `patterns=None` vs omitted.
   Compare each with Canny's `config.verify ? … : VERIFY` truthiness (an empty JS array is truthy).
7. **New mutants (never the builder's M1-M11).** At least: N1 the `.strip()` of the check (V:166) removed · N2 the LAST segment
   replaced by the FIRST · N3 `re.split(r"[;\n]", …)` → `split(";")` · N4 the lookbehind in `executed`'s comment regex dropped ·
   N5 `re.ASCII` dropped from one `VERIFY` regex · N6 the lone-`&` regex → `&` · N7 `with_pipefail`'s `&&` → `;` · N8 the CLI's
   missing-`--` refusal removed. One row each: mutant · compiles (`py_compile`) · collected count · killed-by / SURVIVED /
   EQUIVALENT with the reason (AF-AP-78: a syntax kill is not a kill).
8. **The report.** Any claim in `C1-report.md` the PIN does not support is a finding (line cites, counts, the mutant table,
   DISCREPANCIES, NOT-done, the landing touch).
9. **Out of scope, do not re-litigate:** C2 (not built), Canny code outside `checks.ts:8-93`, the MIT notice text beyond its
   presence. Note a touchpoint in one line if a finding bears on C2's design.

## Deliverable

`tasks/briefs/canny/VERIFY-C1-report.md` — sections: OUTCOME (one paragraph, the GATE RECOMMENDATION first: `MERGE-READY` /
`MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) · IDENTITY (the digests you measured vs the table above) · ITEMS
1-9 with findings F1… · THE HOLLOW-GREEN CLASS (a table: shape · port answer · bash rc with the check stubbed to fail · the rule it
slips · the smallest closing rule) · MUTATION TABLE · GATES (every count PASTED with its exact invocation; the test file twice,
`--basetemp` under your scratch dir, from the repository root and once from `/tmp`) · FOLLOW-UPS (non-blocking, one line each,
for the coordinator to file under D-034) · NOT-done (first-class). Lint floor: `python3 scripts/report_lint.py --min-refs 12 --map
V=scripts/verify_command.py --map T=tests/test_verify_command.py tasks/briefs/canny/VERIFY-C1-report.md --root .`; apply its
`fix:` hints for at most three rounds, then paste and finish. Run gates in ONE foreground call. Remove your scratch root before
you finish. Do not commit, push, post, or open issues — the coordinator does.
