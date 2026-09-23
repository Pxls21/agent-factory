# J1-1-R3 — the three regressions the second repair introduced close, R-3 closes, and the surviving mutants die (task #202; the THIRD focused repair, coordinator-authorized under D-059)

PIN: 0e60603 (the origin head at authoring). The boundary is byte-identical there and at fb016d0, the J1-1-R2 landing (blob ids in
the premise block; re-measure them first).
LANE: j1-1-r3 (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation). Honey `ultra` Lever-2: your report is
DATA: files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

WHY. VERIFY-J1-1-R2 (`tasks/briefs/laya/VERIFY-J1-1-R2-report.md`) returned J1-1-R2 NOT-READY on three regressions that R2 itself
introduced into `src/agent_factory/decisions/volatile.py`, each putting a secret body that d556c9b (R2's parent) redacted into the
decision ledger through the real `make_row` -> `append` -> ledger line -> `replay` path:
- **R-1** (`volatile.py:74-76`): the PIN's `_BEARER` had a global `(?i)`, so its run class also matched U+0130, U+0131 and U+017F; the
  new `(?i:bearer)` scoping made the run case-sensitive, and a bearer token holding one of those letters stays visible.
- **R-2** (`:71-72` against `:85`): `_YIELD`'s token branch checks and scans case-sensitively while `_TOKEN` is case-insensitive; a
  special letter inside the token run hides the next head from the chain guard, so the SECOND value is freed.
- **R-4** (`:61`, `:67-73`; pure ASCII): the chain guard judges a value before `_BEARER` runs; that pass removes the space inside
  `bearer <token>`, so a later value class swallows the next head and frees its value.
The coordinator reproduced all three at the head with the verifier's script (premise block). J1-1's headline capability is that a
secret's bytes never reach the ledger (the council's acceptance test 1), so D-059 authorizes this third repair. No fourth round is
pre-authorized: if this repair's verify finds a new regression, the class goes to a redesign of the redaction pass.

CONTRACT SOURCES (read whole before you design): D-056, D-057 and D-059 in `docs/08_DECISION_LOG.md` ·
`tasks/briefs/laya/J1-1-R1-brief.md` (A1-A5 still in force) · `tasks/briefs/laya/J1-1-R2-brief.md` (B1-B5 still in force) ·
`tasks/briefs/laya/VERIFY-J1-1-R2-report.md` sections 2, 3, 4, 7, 8, 10, 12, 13 and 14 · `tasks/briefs/laya/J1-1-R2-report.md` (the
builder's 30-mutant table) · the verifier's scratch tools under `/tmp/vj11r2/` (read-only: `repro.py`, `fixa/`, `fixb/`, `tools/`
with `fixcases.py`, `icase_ledger.py`, `diff3.py`, `idem5.py`, `cost6.py`, `guard4.py`, `guard4b.py`; copy what you use into your own
scratch directory `/tmp/j113/` and never edit `/tmp/vj11r2/`).

## The contract — AMENDMENT 3 to J1-1 (D-059; decided, do not re-litigate; a contradiction is a DISCREPANCY)

C1 **R-1, R-2 and R-4 close.** For the verifier's repro rows (report section 13) and for every case in its case files (section 10:
"R-1 10/10 and R-2 4/4 and R-4 5/5 rows"; rebuild them from `fixcases.py` / `icase_ledger.py`), no byte of the fake body is in
`decision_state`'s output, in `canonical()` of it, or in the appended ledger line on disk, and `replay` accepts every row.

C2 **R-3 closes in its `NAME= v` form** (an upper-case secret name, `=`, a space, then the value, behind sk or bearer:
`task-DB_PASSWORD= QZJ8…`, `Bearer …API_KEY= v`). The `NAME==v` padding form is a declared residue: state it in the report with its
measured row; do not write a test that pins the leak.

C3 **The three surviving mutants die.** The verifier's V-M3 (`desk-access-TOKEN <run>`), V-M11 (`desk-access_token <run>`) and V-M4
(`mask-PASSWORD=abc_TOKEN <run>`) (report section 8) each reopen a leak and pass all 121 tests at the head. Add the tests that kill
them, rebuild each mutant on a scratch copy, and paste the killing test per mutant.

C4 **No regression against EITHER reference.** Every value that d556c9b OR fb016d0 redacts stays redacted. Re-run the verifier's
differential (section 4 method; 6 seeds x 20,000 inputs, three ASCII and three with the special letters) against each reference:
`newly visible BODY inputs = 0` in all runs. Re-run its 71,280-shape grid: `new_leak: 0`. B1's eight V-1 rows stay closed.

C5 **The invariants hold** (B3-B5 of the R2 brief): the placeholders, the refusal texts, the seven schemas, the limits, `canonical()`,
the ledger's row shape and the D-1 class order stay; `decision_state` stays idempotent (the verifier's 40,000-state check: `0
NON-IDEMPOTENT`); no golden digest changes (if one does, STOP and report); cost stays linear (16k-128k adversarial inputs per changed
pattern, timings pasted; `test_env_assignment_redaction_does_not_backtrack_exponentially` green).

C6 **The comments tell the truth.** The statements the verifier lists as falsified in `volatile.py` (report section 12: `:45-46`
"each fires where its PIN form fires", `:52-54` "so the run keeps its PIN form", `:64-65` "whose \S+ value runs further") are rewritten
so each sentence is true of the new code. Report files and the incident log are the coordinator's.

THE MEASURED CANDIDATE (report section 10; adopt it as written or improve it, but any other form must meet C1-C5 with the same
evidence): FIX-A, one line each — `_ASSIGNMENT_HEAD` gains `|(?i:bearer)\s` (R-4); the token branch's check and scan become
`(?i:[A-Za-z0-9+/])` (R-2); the bearer lookahead and run become `(?i:[A-Za-z0-9._~+/-])` (R-1). FIX-B adds, on the widened branch,
`(?!" + _ENVVAL_HEAD + r"\S)` (R-3). The verifier measured on scratch copies: FIX-A and FIX-B each `122 passed` on R2's tests and
`73 passed` on the PIN's, `leaking: 0` on its 14-shape driver, 0 newly visible bodies in 12 differential runs, the goldens unchanged,
40,000 states idempotent, cost linear. NOT measured: either fix against the builder's full 30-mutant table. That is your job.

## Work in a scratch copy, write the shared tree once

The J1-3 lane runs in this tree and imports `agent_factory.decisions` from `src/`. Build and test in a scratch copy
(`git archive HEAD | tar -x -C /tmp/j113/work`, then your edits there). Write `volatile.py` and the two test files into the shared tree
ONCE, after every gate passes in the scratch copy, then re-run the gates in the shared tree and paste both runs.

## Tests (each new test RED at the head, GREEN after; paste both runs)

In `tests/test_decisions_ledger.py`: one test per C1 row class (R-1, R-2, R-4) and one for C2's `NAME= v` form, each through
`make_row` -> `append` -> the file bytes -> `replay` (the body must be absent from the file); the C3 killing tests. In
`tests/test_decisions_canonical.py`: the same rows at `decision_state` level, with idempotence on each. None is skipped or deleted.

## Mutation audit (scratch copies only: never `git checkout`, `git restore` or `git stash` in this shared tree)

At least: m1-m3 each of FIX-A's three changes reverted alone (each must red the named test of its R row: line 61 → R-4, line 72 → R-2,
line 75 → R-1); m4 FIX-B reverted (the C2 test reds); m5-m7 V-M3, V-M11 and V-M4 (C3); then the builder's 30-mutant table from the
R2 report, rebuilt on your code. Each mutant compiles and collects (AF-AP-78); before you count a kill, run the killing test on the
UNMUTATED tree and paste that it passes (AF-AP-138). Paste the killing test per row. A survivor is reported, never hidden.

## Gates (paste every command with its output)

`mkdir -p /tmp/j113/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/j113/bt/r<n>`
twice (rm -rf after each), with `bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py`
(the head: `121 passed`, set `16a7b628685e`; your tests add to it) · the PIN's own tests (`git archive d556c9b tests/test_decisions_canonical.py tests/test_decisions_ledger.py`) run against your code, pasted ·
`/root/venv-agent-factory/bin/python /tmp/vj11r2/repro.py /home/user/agent-factory/src` after the write (R-1, R-2, R-4 and R-3 all
`body-in-ledger-line=False`) · the differential and the grid (C4) · the idempotence and cost runs (C5) ·
`/root/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/volatile.py tests/test_decisions_canonical.py tests/test_decisions_ledger.py` ·
`python3 scripts/ap_screen.py src/agent_factory/decisions/volatile.py` and
`python3 scripts/ap_screen.py --tests tests/test_decisions_canonical.py tests/test_decisions_ledger.py` (new hits vs the head) ·
`python3 scripts/no_laya_in_gates.py` (read-only; the tree must stay clean).

## Boundary and standing do-nots

MODIFY ONLY: `src/agent_factory/decisions/volatile.py` (the class forms and their comments), `tests/test_decisions_canonical.py`,
`tests/test_decisions_ledger.py`. CREATE `tasks/briefs/laya/J1-1-R3-report.md` (write it incrementally from the start). READ-ONLY:
every other file, including `src/agent_factory/decisions/ledger.py`, `src/agent_factory/decisions/canonical.py`,
`tests/fixtures/decisions/**` and `scripts/transcript_export.py`. Other lanes are live in this tree: S198A on
`scripts/transcript_export.py` and `tests/test_transcript_export.py`; T94 on `harness-ports/bin/pc-lane.sh`, `scripts/pc_lane.sh` and
`harness-ports/tests/test_pc_lane*.sh`; J1-3 creating `scripts/decide-harvest`, `tests/test_decide_harvest.py` and
`tests/fixtures/decisions/sources/`. Never touch their files. Never run git add, commit, stash, checkout, restore, reset or clean in the
shared tree. No PC or bridge use. Take no outward-facing action. Fake strings only (bodies like `QZJ8…`, `X4Z9…`). Paste every count
and timestamp from command output. Long gates in ONE foreground call. A deviation from any contract line is STOP-and-report, never a
self-accepted change. Report adjacent defects; never fix them.

## Report (`tasks/briefs/laya/J1-1-R3-report.md`)

DATA: the diff of `volatile.py` with the reason per changed line; the RED→GREEN pairs; the mutant table; the differential, grid,
idempotence and cost numbers; the gate outputs; the declared residues (the `NAME==v` form and anything else); DISCREPANCIES; NOT-done.
`python3 scripts/report_lint.py --min-refs 10 tasks/briefs/laya/J1-1-R3-report.md` (at most three fix rounds, then paste and finish).

## PREMISE — MEASURED at authoring (2026-09-23 16:2xZ, /home/user/agent-factory, the boundary worktree == origin 0e60603)
```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
2026-09-23T16:27Z
0e60603
$ (blob ids of the two boundary files at d556c9b, fb016d0, origin, and the worktree)
src/agent_factory/decisions/volatile.py d556c9b=20ebcd54f3ed fb016d0=bf04415d72c1 origin=bf04415d72c1 worktree=bf04415d72c1 lines=395
tests/test_decisions_canonical.py d556c9b=0afbf1b821ed fb016d0=440ac2426d8f origin=440ac2426d8f worktree=440ac2426d8f lines=1060
$ grep -n (the class definitions and the three FIX-A lines) src/agent_factory/decisions/volatile.py
61:_ASSIGNMENT_HEAD = _SECRET_NAME + r"[\"']?\s?[:=]|(?i:(?:\b|(?<=_))token)[\"'\s]"
62:_ENVVAL_HEAD = r"(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)="
67:_YIELD = (
69:    r"|(?!" + _ENVVAL_HEAD + r")" + _SECRET_NAME + r"[\"']?\s?[:=]\s?[\"']?"
72:    r"(?=[A-Za-z0-9+/]{32})(?![A-Za-z0-9+/]*?(?:" + _ASSIGNMENT_HEAD + r"))"
74:_BEARER = re.compile(
75:    r"(?i:bearer)\s+(?=[A-Za-z0-9._~+/-]{16})(?:(?!" + _YIELD + r")[A-Za-z0-9._~+/-])*=*"
77:_SK = re.compile(r"sk-(?=[A-Za-z0-9_-]{8})(?:(?!" + _YIELD + r")[A-Za-z0-9_-])*")
85:_TOKEN = re.compile(r"(?i)(?:\b|(?<=_))token[\"']?(?: ?[:=] ?| )?[\"']?([A-Za-z0-9+/]{32,})")
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/j113/bt | tail -1
67 passed in 3.26s
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py
1 files set=d3c0129cf7f3
$ /root/venv-agent-factory/bin/python /tmp/vj11r2/repro.py src   (the verifier repro, report section 13; worktree == origin)
R-1 body-in-ledger-line=True  state.msg='Authorization: Bearer QZJ8QZJ8ıQZJ8QZJ8QZJ8QZJ8QZJ8'
R-2 body-in-ledger-line=True  state.msg='<redacted:sk>token <redacted:token>: X4Z9X4Z9X4Z9'
R-4 body-in-ledger-line=True  state.msg='ta<redacted:sk>password:<redacted:envval> X4Z9X4Z9X4'
R-3 body-in-ledger-line=True  state.msg='ta<redacted:sk>= QZJ8QZJ8QZJ8QZJ8QZJ8'
replayed rows: 4
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/j113/bt2 | tail -1
121 passed in 3.70s
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
$ /root/venv-agent-factory/bin/python /tmp/vj11r2/repro.py <git archive d556c9b src>   (the coordinator, 16:2xZ)
R-1 body-in-ledger-line=False state.msg='Authorization: <redacted:bearer>'
R-2 body-in-ledger-line=False state.msg='<redacted:sk> QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8ıpassword: <redacted:envval>'
R-4 body-in-ledger-line=False state.msg='ta<redacted:sk>:QZJ8QZJ8<redacted:bearer>token: <redacted:envval>'
R-3 body-in-ledger-line=True  state.msg='ta<redacted:sk>= QZJ8QZJ8QZJ8QZJ8QZJ8'
replayed rows: 4
$ ls /tmp/vj11r2/ /tmp/vj11r2/tools | head   (the verifier's scratch, kept 1.1 MB)
fixa fixb guard4_worse.json guard4_worse_fixb.json pinsrc repro.py tools treenew treepin v1_rows.py
b1extra.py b1grid.py b1grid_cls.py b4_worker.py chained5.py cost6.py diff3.py fieldsweep.py fieldsweep_grade.py fixcases.py guard4.py guard4b.py icase_ledger.py idem5.py ledger_worker.py ledger_worker2.py …
```
