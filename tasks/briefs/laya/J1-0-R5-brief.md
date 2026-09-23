# J1-0-R5 — the never-a-gate screen regresses nothing R3 refused, and its stated claims are true (task #188; the ONE focused repair under AMENDMENT 4)

PIN: the origin commit of this brief (the post-push SHA, named in the dispatch prompt). The two boundary files are byte-identical
to 0e7b6c3, the J1-0-R4 landing (measured below); re-measure them first.
LANE: j1-0-r5 (sandbox; agent `code-implementer` on the D-054 pin, in the SHARED tree, no worktree isolation). Honey `ultra`
Lever-2: your report is DATA — files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

WHY: VERIFY-J1-0-R4 (`tasks/briefs/laya/VERIFY-J1-0-R4-report.md`) reproduced everything AMENDMENT 3 names. The coordinator ruled
it NOT-READY on three findings under the brief's frozen materiality clause (the ledger note "VERIFY-J1-0-R4 HOME, NOT-READY BY
RULING", 2026-09-23 12:4xZ):
- **V-01, an R4 regression (AF-AP-153).** `_unquote` keeps the escapes of an ANSI-C `$'…'` heredoc delimiter that bash
  translates, so the screen ends the heredoc at a later line and reads a following `. scripts/h.sh` CLEAN. R3 refused the same
  text. The coordinator reproduced it (premise below: R3 rc 4, R4 rc 0, bash runs the helper).
- **V-05, a false claim.** The comment above `ALLOWED_DYNAMIC_LOADS` says an entry "cannot be re-pointed at another file" and
  allows "never more". The verifier re-pointed an entry through its base, and a wrapper carried a second load; commit 4 of its
  throwaway repository landed through the real hook.
- **V-06, a false claim.** The `_workflow_runs` docstring says every scalar style other than a literal block maps to the line the
  value starts on. Folded and quoted multi-line values map elsewhere (Y2b, Y2c, Y14), and Y13 names the NEXT step's line.

AMENDMENT 4 also takes **V-04**. R4 introduced it: a `$((` body that fails as arithmetic is restored and re-scanned as commands,
so `v=$(( $(( … x ) ) … ) )` nested k deep costs 2^k (27.62 s at 192 bytes; R3 0.04 s). The screen runs in the pre-commit hook on
every commit (AF-AP-152). This is the one repair D-031 allows for AMENDMENT 4. Everything else in the verify report is issue #46
or issue #37: do not fix it here. Say in the report which of those rows your change closes incidentally, with the evidence.

CONTRACT SOURCES (read whole before you design): `tasks/briefs/laya/J1-0-R3-brief.md` (AMENDMENT 2) and
`tasks/briefs/laya/J1-0-R4-brief.md` (AMENDMENT 3). Both stay in force: every line there stands unless a line below replaces it.
Also read the verify report: § 2 (the AQ/PQ tables and their mechanism), § 4 (the Y shapes), § 5 (E1a, E1b, E1d), § 7 (the
R3-versus-R4 table), § 8 (the throwaway-hook commits), § 9 (the cost series) and the FINDING INVENTORY. And read
`scripts/no_laya_in_gates.py` and `tests/test_no_laya_in_gates.py` as they stand at the PIN.

## The contract — AMENDMENT 4 (coordinator, 2026-09-23; decided, do not re-litigate; a contradiction is a DISCREPANCY)

R5-1 **A `$'…'` heredoc delimiter never ends the heredoc at a line bash would not.** Pick one and say which:
(a) `_unquote` translates `$'…'` as bash does (its ANSI-C escape table: `\a \b \e \E \f \n \r \t \v \\ \' \" \? \nnn \xHH
\uHHHH \UHHHHHHHH \cx`), and a delimiter it cannot translate is refused; or
(b) a heredoc word holding `$'` with a backslash inside is refused as `gate-file-unparseable: <file>:<line>: <reason>`, exit 4,
naming the operator's line.
Either way: AQ1, AQ2, AQ3, AQ4 and PQ5b (the report's § 2 shapes) are never CLEAN; `<<$'EOF'` with no escape still works; the
live tree stays `clean` in both modes.

R5-2 **The scan is linear in `$((` nesting.** The arithmetic-or-command decision for a `$((` is made once per start position
(memoized), or nesting past a fixed depth is refused with the R4-1 refusal text (fail closed). The k-series from the report's
§ 9 (`v=$(( $(( … x ) ) … ) )`, k levels) must scan k=22 in under 1 s on this sandbox, where R4 took 27.62 s. The live tree's
scan time must not grow by more than 10 %: paste before and after.

R5-3 **The `ALLOWED_DYNAMIC_LOADS` comment states what the code enforces.** An entry binds (gate file, literal repo path) and a
site count. The base directory is not bound. Re-pointing through the base, or a wrapper that carries a second load, is outside
the check (F-B5's class, issue #37). No word in the comment may claim more. Binding the base is NOT part of this repair.

R5-4 **A workflow refusal names a line inside the value.** `_workflow_runs` reports the value's start line for every scalar style
except a literal block (`|`), which keeps its line-for-line map. The docstring says exactly that. Y2b, Y2c, Y13 and Y14 (the
report's § 4 shapes) name a line inside their own `run:` value, never the next step's.

R5-5 **The R4 report's false claims are corrected.** Your report has a "Corrections to the J1-0-R4 report" section. It corrects
D4 ("which ends in an R4-1 refusal", false for `$[ … ]`, V-03), D4's "refusals that are safe" for `shell: python` steps (V-08),
and the self-attack line "Its known exotic triggers refuse instead (D4)". Quote each one, say what is true, and cite the
verify report's fixture. Do not edit `tasks/briefs/laya/J1-0-R4-report.md`.

Nothing else changes: the vocabulary, exit codes 0/3/4/64, the existing error texts, the SELF refusal, the no-bypass rule, the
output line format, AMENDMENT 2's static-import rules, AMENDMENT 3's R4-1..R4-6, and the `ALLOWED_DYNAMIC_LOADS` entries and
counts.

## Tests (in `tests/test_no_laya_in_gates.py`; each RED at the PIN, GREEN after; paste both runs)

- R5-1: AQ1, AQ2, AQ3, AQ4 and PQ5b as fixtures, each refused (never exit 0). If you chose (a), add one fixture per escape family
  whose translated delimiter bash honours, checked against bash itself at test time (`bash -n`, and a run that proves where the
  heredoc ends). If you chose (b), `<<$'EOF'` with no backslash stays clean.
- R5-2: the k-series at k=22, the whole scan under a generous bound (say 5 s; R4 takes about 28 s, so the bound discriminates).
  Plus one fixture proving the memo or depth rule did not change a decision: an R4 `$((` arithmetic case and an R4 `$( (` subshell
  case give the same verdicts as before.
- R5-4: Y2b, Y2c, Y13 and Y14, each refused with the line the contract names. Plus one literal-block case whose line map is
  unchanged.
- R5-3 needs no test (a comment). Say so in the report.
- The live-tree test stays: exit 0 on the real repo, both modes; paste the scanned-file count.

## The R3 differential (AF-AP-153's fix; a gate, not a test)

Every fixture you add, plus every AQ, PQ, TK, CA, DA and Y shape in the verify report's §§ 2-4, runs through THREE screens:
R3 (`git show 5090671^:scripts/no_laya_in_gates.py`), R4 (the PIN) and yours. Paste one table: shape → R3 rc/line → R4 rc/line →
R5 rc/line. The rule: every R3 refusal stays a refusal in R5, or the row names why the change is right. No R5 row may be exit 0
where bash runs an unlisted file. Build the fixtures in throwaway trees under `/tmp/j10r5/`.

## Mutation audit (scratch copies only: never `git checkout`, `git restore` or `git stash` in this shared tree)

At least: m1 revert R5-1 (the PIN's `_unquote`), m2 remove the memo or depth rule, m3 revert R5-4's line mapping, m4 widen the
R5-1 refusal to every `$'` delimiter (it must break the `<<$'EOF'` case). Each mutant compiles and its suite collects (AF-AP-78).
Before you count a kill, run the killing test on the UNMUTATED tree and paste that it passes (AF-AP-138). A survivor is a finding
you report.

## Gates (paste every command with its output)

- `/root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r5/bt<n>`
  TWICE, with identical counts, plus the set id (`bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py`, premise
  `e3695f80792b`).
- `python3 scripts/no_laya_in_gates.py` and `python3 scripts/no_laya_in_gates.py --staged` on the real tree: both `clean`, with the
  count, and timed before and after your change.
- The real pre-commit hook in a THROWAWAY repository (a `git archive` copy of the PIN plus your working files, `git init`, the
  repo's hooks via `core.hooksPath`). AQ1 is refused on a real `git commit`, and a clean commit lands.
- `/root/venv-agent-factory/bin/python -m pyflakes scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py` (no new hit).
- `python3 scripts/ap_screen.py` on the two files (no new hit, or say why).

## Boundary and standing do-nots

MODIFY `scripts/no_laya_in_gates.py` and `tests/test_no_laya_in_gates.py`. CREATE `tasks/briefs/laya/J1-0-R5-report.md` (write it
incrementally). Nothing else. A line you cannot meet inside the boundary is a DISCREPANCY, never a silent edit elsewhere.

Other agents work in this tree on disjoint files: `proofs/S0-05/`, `tests/test_s0_05_egress.py`, `tasks/briefs/s0-05-support/`,
`src/agent_factory/decisions/`, `tests/test_decisions_*.py` and `tasks/briefs/laya/J1-1-R1-report.md`. Never touch, run or revert
them. Nothing under `.claude/` is edited (another lane holds that tree's manifest). Never run `git stash`, `git checkout -- …`,
`git restore`, `git add`, `git commit` or `git push` in this tree; throwaway repositories under `/tmp/j10r5/` are yours.

No outward-facing action, and no PC or bridge use. Test vocabulary in fixtures is the screen's own closed list, in throwaway trees
only. Scratch lives under `/tmp/j10r5/` and is removed when you finish; the sandbox has about 1.4 GB free.

AUTHORIZATION: this is defensive work on the owner's own gate: planting helpers that source banned vocabulary into throwaway gate
trees to prove the screen refuses them.

CODE INTEL FIRST: `graft ask` before any grep for code questions. The pack:
`scripts/lane_context.sh -q 'how does the never-a-gate screen read heredoc delimiters, decide dollar-paren-paren arithmetic, and map workflow run lines' -s _unquote -s arith -s dollar -s _workflow_runs -o /tmp/j10r5/pack.md scripts/no_laya_in_gates.py`.

## Report (`tasks/briefs/laya/J1-0-R5-report.md`)

The report holds, in order:
- the PREMISE, re-measured;
- per contract line R5-1..R5-5: files:lines and the tests that pin each (R5-1 says which option you chose, and why);
- the R3 differential table;
- the mutant table;
- the gates, pasted;
- the "Corrections to the J1-0-R4 report" section (R5-5);
- which issue #46 or issue #37 rows your change closes incidentally, with evidence;
- DISCREPANCIES;
- NOT-done.

Lint floor: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/J1-0-R5-report.md --root .` (full repo-relative
paths, no `--map`). Apply its `fix:` hints for at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 12:5xZ, sandbox @ local a318b8a plus the uncommitted ledger plane; the boundary files are unchanged since 0e7b6c3)
```
$ git log -1 --format='%h %s' -- scripts/no_laya_in_gates.py | cut -c1-90
0e7b6c3 J1-0-R4 landed (task #172; GATED-PENDING-VERIFY): the never-a-gate screen scans to
$ git rev-parse HEAD:scripts/no_laya_in_gates.py
ae8b2046e118f6cc2bb8ce1b51f8600fc27dc450
$ git rev-parse HEAD:tests/test_no_laya_in_gates.py
9790cb714afa10c555467fc8f25db9aa5d7f1c4b
$ git diff --quiet HEAD -- scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py && echo 'worktree == HEAD for both boundary files'
worktree == HEAD for both boundary files
$ grep -n '^def _unquote\|^    def dollar\|^    def arith\|^def _workflow_runs\|start_mark\|^ALLOWED_DYNAMIC_LOADS\|never more\|re-pointed at another file\|a folded or flow value has no line' scripts/no_laya_in_gates.py
126:def _unquote(word):
313:    def dollar(self, in_dq):
332:    def arith(self, start, skip, what):
470:def _workflow_runs(content):
473:    starts on (a folded or flow value has no line of its own after the first)."""
492:                    runs.append((value.start_mark.line + (2 if value.style in ("|", ">") else 1), value.value))
696:# reviewed to reach) -> how many such loads the gate file may hold, never more. A load is covered only
698:# re-pointed at another file (the F-B5 class). Closed: a new entry is a reviewed change here.
699:ALLOWED_DYNAMIC_LOADS = {
$ bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py
1 files set=e3695f80792b
$ PYTHONDONTWRITEBYTECODE=1 /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r5p/bt2 | tail -1
92 passed in 7.81s
$ python3 scripts/no_laya_in_gates.py; python3 scripts/no_laya_in_gates.py --staged
no_laya_in_gates: 40 files scanned, clean
no_laya_in_gates: 40 files scanned, clean
# V-01 (AQ1's shape), a four-line gate in a fixture tree; R3 = git show 5090671^:scripts/no_laya_in_gates.py
$ cat /tmp/j10r5p/v01/scripts/g.sh
#!/bin/bash
cat <<$'echo \x41'
echo A
. scripts/h.sh
echo \x41
$ (cd /tmp/j10r5p/v01 && bash scripts/g.sh)
HELPER-RAN
x41
$ python3 /tmp/j10r5p/r3.py --root /tmp/j10r5p/v01; echo rc=$?
gate-file-sources: scripts/g.sh:4: scripts/h.sh
rc=4
$ python3 scripts/no_laya_in_gates.py --root /tmp/j10r5p/v01; echo rc=$?
no_laya_in_gates: 1 files scanned, clean
rc=0
# V-04, the nested $(( … ) ) series (v=$(( $(( … x ) ) … ) ), k levels), wall clock on this sandbox
k=14 bytes=128 bash-n=ok R3 rc=0 0.05 s
k=14 bytes=128 bash-n=ok R4 rc=0 0.17 s
k=16 bytes=144 bash-n=ok R3 rc=0 0.04 s
k=16 bytes=144 bash-n=ok R4 rc=0 0.48 s
```
