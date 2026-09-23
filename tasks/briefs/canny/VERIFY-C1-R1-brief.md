# VERIFY-C1-R1 — the targeted adversarial verify of the C1-R1 repair (`scripts/verify_command.py`)

**Role:** `adversarial-verifier`, IN THE SANDBOX. Honey `full`: line-bounded findings, evidence anchors, SOLID/UNSURE on every
claim. Your report is DATA for the coordinator's gate; you return a GATE RECOMMENDATION, never a verdict. Do NOT spawn subagents.

**PIN:** `ee66397` (origin head; V and T are byte-identical to the C1-R1 landing `0e1deb2`, measured below). Work on the tree
READ-ONLY. Every mutant, stub and probe lives in a scratch dir under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vc1r1/`. The ONLY file you write in the tree is your
report. ANOTHER LANE (E3, the S0-05 launch recipe) is LIVE in the same working tree: never `git stash`, `checkout`, `restore`,
`add`, `reset` or `commit` in `/home/user/agent-factory`, and never touch `proofs/S0-05/` or `tests/test_s0_05_egress.py`.
Canny (`/home/user/qkal/canny`) is STATIC READING ONLY: its regex literals may be copied as text into your own `node -e` oracle,
nothing else. Every "check" binary is a local stub script that exits 3 (or 0); scope a stub `PATH` to ONE command with
`env -i` and pin interpreters by absolute path (AF-AP-134). Build every non-ASCII probe string in Python and pass it as argv,
never through a shell `$'\u…'` escape (the coordinator's own slip, recorded on AF-AP-134).

## What landed (V = `scripts/verify_command.py`, T = `tests/test_verify_command.py`)

**Frozen contract:** `tasks/briefs/canny/C1-brief.md` (items 1-7) + `tasks/briefs/canny/C1-R1-brief.md` (AMENDMENT C1-A2 and
contract items 1-8). The builder's report `tasks/briefs/canny/C1-R1-report.md` is an INPUT to attack, never evidence. Seams:
the docstring V:7-55 (the flag, C1-A2, eight declared limits), `_TRAP` V:140, `_EXEC_OR_COPROC` V:141, `_hides_status`
V:144, `is_verify` V:178 (the pipefail scan V:192-197, the pipe rule V:219, the feeder V:225), `with_pipefail` V:239, the CLI
refusals (the builder cites V:287-290, V:305-314, V:332-337: re-measure).

## PREMISE — MEASURED at authoring (2026-09-23 06:0xZ, sandbox, /home/user/agent-factory@ee66397)

```
$ identities at ee66397 (sha256[:16] lines path)
d9f71bb3962bdb4a 351 scripts/verify_command.py
195c1b6378adaad8 490 tests/test_verify_command.py
769a2b90023c422e 515 tasks/briefs/canny/C1-R1-report.md
$ bash scripts/pc_suite.sh set-id -- tests/test_verify_command.py
1 files set=d9bd6dad2d0e
$ the coordinator's landing gates on these bytes (repo root twice, then cd /tmp)
65 passed, 8 xfailed in 0.45s
65 passed, 8 xfailed in 0.45s
65 passed, 8 xfailed in 0.48s
$ the bash oracle (tasks/briefs/canny/C1-R1-brief.md's script; checks stubbed to exit 3) on these bytes
H1    port=does-not-count   port_rc=1 bash_rc=0  'pytest && false || true'
H1b   port=does-not-count   port_rc=1 bash_rc=0  'pytest && echo ok || true'
H2    port=does-not-count   port_rc=1 bash_rc=0  "trap 'exit 0' EXIT; pytest"
H3    port=does-not-count   port_rc=1 bash_rc=0  'set\xa0-o pipefail; pnpm test | tail'
H4    port=does-not-count   port_rc=1 bash_rc=0  'set -o pipefail\r\npnpm test | tail'
H5    port=does-not-count   port_rc=1 bash_rc=0  'echo \\\npytest'
H6    port=does-not-count   port_rc=1 bash_rc=0  'exec true; pytest'
H6b   port=does-not-count   port_rc=1 bash_rc=0  'coproc pytest'
CTRL  port=counts           port_rc=0 bash_rc=3  'pytest'
CTRL2 port=counts           port_rc=0 bash_rc=3  'set -o pipefail; pnpm test | tail'
$ the rule-(a) mutant (V:147 "||" in last -> False) on a scratch copy
2 failed, 63 passed, 8 xfailed   (test_c1_a2_refuses_status_hiding_shapes[a_H1], [a_H1b])
$ the builder's D1, strings built in Python; PIN = 3f531c4's V, FINAL = these bytes; bash under env -i LANG=C.UTF-8
'set -o pipefailé; pnpm test | tail'   PIN=does-not-count(1)  FINAL=counts(0)  bash_rc=0
'set -o pipefail-x; pnpm test | tail'  PIN=counts(0)          FINAL=counts(0)  bash_rc=0
'set -o pipefail\xa0; pnpm test | tail' PIN=counts(0)         FINAL=counts(0)  bash_rc=0
$ the builder's D2
with_pipefail("trap 'exit 0' EXIT; pytest | tail") -> "set -o pipefail && trap 'exit 0' EXIT; pytest | tail"
is_verify(that rewrite) -> True ; bash (pytest stubbed to exit 3) rc=0
$ python3 scripts/report_lint.py --min-refs 12 --map V=scripts/verify_command.py --map T=tests/test_verify_command.py tasks/briefs/canny/C1-R1-report.md --root .
report_lint: 96 refs — OK 96, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```

## ITEMS (discovery exhaustive; disposition disciplined)

1. **Re-measure the premise** at `ee66397`. Any mismatch: stop, return `CONTRACT-INVALID` with the diff.
2. **The contract through bash.** Each C1-A2 rule (a)-(e), R1's flag on every site, and the CLI refusals (R5-R7), each with a
   closed shape refused and the matching status-preserving shape still counted where the contract says it should. Canny's
   frozen tables must be answer-for-answer unchanged against the PIN `3f531c4` V: run your own comparator (do not reuse the
   builder's) and show it goes red on a planted change.
3. **D1 and D2, the builder's own holes.** Decide each disposition under the blocking predicate. Then grade the builder's
   candidate fixes (its report's L-PF: a separator required after `pipefail`; L-TR: `trap` at any `&&`-part start) against
   bash in BOTH directions: the hollow greens they close, and the false negatives they create over a corpus of legitimate
   shapes you write (for example `set -euo pipefail; …`, `set -o pipefail -o errexit; …`, `set -o pipefail` followed by
   spaces, a newline, `;`, `&&`; `trap 'echo done' EXIT; pytest`, a `trap` that does not change the status). These are
   questions, not measured at authoring.
4. **New hollow greens.** Hunt shapes the amendment does not name, with bash as the oracle (stubs exit 3). Include at least
   `pytest || :`, `pytest | true`, `! pytest`, `pytest &`, `(pytest; exit 0)`, `pytest; exit 0`, `set +o pipefail` after a
   `set -o pipefail`, `timeout 5 pytest`, `pytest 2>&1 | tee log`, a check inside `$( )` or backticks, and the declared limit
   families (H7, H8, H9, the here-doc) for completeness. Every shape that counts while bash exits 0 is a finding; classify it
   against C1-A2 and the declared limits.
5. **The declared limits are live.** Each strict xfail must turn into an XPASS failure when its shape is fixed on a scratch copy;
   confirm for at least four of the eight, and confirm every limit the docstring lists has a pin.
6. **Mutation audit with NEW mutants** (never the builder's rows), one at a time on scratch copies, each compiled and
   collected (AF-AP-78). Your own list, including at least: `re.ASCII` dropped at the pipefail scan; the C1-A2 check moved
   after the pattern match; `_hides_status` fed the unstripped command instead of the executed text; each CLI refusal's exit
   code changed to 1; `with_pipefail` returning a rewrite without re-checking it. A survivor with a live discriminator is a
   finding; an equivalent mutant needs a searched discriminator, not an argument (AF-AP-137's companion lesson).
7. **Gates, yourself:** T twice from the repo root and once from `/tmp`, pasted with the set id; pyflakes on V and T;
   `python3 scripts/ap_screen.py scripts/verify_command.py` and `--tests tests/test_verify_command.py`.

## Deliverable

`tasks/briefs/canny/VERIFY-C1-R1-report.md` — the finding inventory (each BLOCKER / FOLLOW-UP / INFO / UNVERIFIED with
evidence level, contract mapping, canonical-path status, material effect, reproduction and a suggested fix), the oracle tables,
the mutant table, the gates pasted verbatim, what you reproduced vs reviewed statically, and ONE gate recommendation line
(`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`). Cite as `V:<line>` / `T:<line>`, then run
`python3 scripts/report_lint.py --min-refs 12 --map V=scripts/verify_command.py --map T=tests/test_verify_command.py tasks/briefs/canny/VERIFY-C1-R1-report.md --root .`
— apply its `fix:` hints for at most three rounds, then paste the line and finish. Write the report incrementally.

**Standing do-nots:** no subagents; no outward-facing actions (no PRs, comments, pushes, issues); never touch the PC bridge;
never kill a process you did not start; touch no file in the tree except your report.
