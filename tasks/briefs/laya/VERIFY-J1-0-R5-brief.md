# VERIFY-J1-0-R5 — the targeted verify of the never-a-gate screen's fifth round (task #193)

PIN: 10f1823 ("J1-0-R5 landed (task #188; GATED-PENDING-VERIFY; …)", the post-push SHA of local ee67995). The boundary files are
byte-identical at origin 98e2efc and later heads until another J1-0 round lands (blob ids below; re-measure them first).
COMPONENT: `scripts/no_laya_in_gates.py` (S, the screen), `tests/test_no_laya_in_gates.py` (T), `scripts/gate_files.txt` (L, the
list), `scripts/hooks/pre-commit` (H). The builder's report `tasks/briefs/laya/J1-0-R5-report.md` is an INPUT TO ATTACK, not a truth.
LANE: verify-j1-0-r5 (sandbox; agent `adversarial-verifier`, in the SHARED tree, no worktree isolation). Honey `full`: line-bounded
findings, evidence anchors, SOLID/UNSURE. Do NOT spawn subagents.

WHY THIS LANE EXISTS: J1-0-R5 is GATED-PENDING-VERIFY (rule 0f). Its gates were the builder's own 20 tests, its own 15 mutants and its
rebuilt fixtures; the coordinator re-ran the tests and both screen modes, which is a second run of the same oracle. The screen runs in
the pre-commit hook on every commit (H): a fail-open lets a gate source or load unlisted code (the KC-J1 property); a false refusal
blocks every commit on the branch.

CONTRACT (frozen): AMENDMENT 4, R5-1..R5-5, in `tasks/briefs/laya/J1-0-R5-brief.md` (section "The contract"), on top of AMENDMENT 3
(`tasks/briefs/laya/J1-0-R4-brief.md`) and AMENDMENT 2 (`tasks/briefs/laya/J1-0-R3-brief.md`). KNOWN, filed as issue #46 (do not
re-derive; report as KNOWN if you meet them): V-02 (`time` before `((`/`case`: TK1-TK5, CA5), V-03 (`$[ … ]`: DA1), V-07 (GitHub
`${{ }}` substitution: Y7b, Y7c), V-08 (`shell: python` steps: Y9, Y9b, Y9c), V-09 to V-18, and the R5 lane's D8 (the nested `((`
command form is quadratic) and D9 (a test docstring). Issue #37's F-B3..F-B11 stay KNOWN too. The R5 brief's differential rule 2
covered the issue-#46 rows by mistake: that is the coordinator's defect, graded at landing, and not a finding here.

## Items (report EVERY observation; no severity filter; rank downstream)

1. PREMISE. Re-measure the block below on the PIN (blob ids, the line map, the gate run with its set id, both screen modes). A
   mismatch that changes an item is CONTRACT-INVALID for that item; say which.
2. R5-1, the `$'…'` family, by bash itself (a throwaway directory where the sourced file writes a marker, so bash's own execution
   says whether a `.`/`source` ran). NEW shapes, never the builder's AQ1-AQ5, PQ5a/b or `E$'\x4f'F`: `<<-$'\tEOF'` with tab-indented
   body and delimiter; `<<$'EOF'x` and `<<x$'EOF'` (an ANSI-C segment beside a plain one); `<<"$'EOF'"` (inside double quotes `$'` is
   literal); `<<\$'EOF'`; `<<$''EOF`; an unterminated `<<$'EOF`; and, OUTSIDE heredocs, a source target spelled through ANSI-C quoting:
   `. $'scripts/h\x2esh'`, `source $'\x73cripts/h.sh'`, `. scripts/$'h.sh'`, `. "$(printf %s $'scripts/h.sh')"`. For each: bash's
   verdict (ran or not), the screen's verdict, agreement. A shape where bash RUNS an unlisted file and the screen says CLEAN is a
   fail-open; the other way is a false refusal (say whether any live gate file holds that shape). Does R5-1's rule, as built, cover
   `$'` in a source ARGUMENT, or only in a heredoc word? The contract names heredoc delimiters; a source-argument gap is still a
   finding (classify it against AMENDMENT 2's source rules).
3. R5-2, the memo and its new refusal (D2: `$(( re-read with other heredocs pending`, `S:354`). (a) Can the start-only memo return a
   WRONG non-refusal: a `$((` whose first visit decides arithmetic under one pending-heredoc state and whose revisit, under another,
   would decide command substitution with a `.`/`source` inside? Build it, run it under bash, compare. (b) False refusals R5 adds:
   search bash-valid texts that R4 read CLEAN and R5 refuses with the D2 text (the builder's sweep found 4 of 25 bash-valid variants
   reach the guard, all refused by R4 too; widen the family: heredocs opened inside `$(( … ))` operands, `$((` inside a heredoc body
   that is later re-read, several pending heredocs with different quoting). (c) Is D2's text within "the existing error texts" rule
   (the contract keeps existing texts; does it forbid a new one)? Read the R5 brief and say.
4. R5-4, the workflow line map. New YAML scalar styles: `>-`, `>+`, `|-`, `|+`, `|2` (explicit indentation), a plain multi-line
   scalar, double-quoted with `\n` escapes and an escaped line break, single-quoted with `''`, a `run:` inside a flow mapping
   `{run: …}`. For each: does bash run the helper (run the value as GitHub would: PyYAML's value through `bash -c`), is it refused, and
   is the named line inside the value? State for each style which text GitHub runs (folded or literal), from the YAML spec.
5. R5-3 and R5-5. The `ALLOWED_DYNAMIC_LOADS` comment claims only what the code enforces (quote it; name any word that claims more).
   The report's "Corrections to the J1-0-R4 report" section: is each correction true (reproduce the cited fixture)?
6. The real hook. In a THROWAWAY repository under `/tmp/vj10r5/` (a `git archive` subset of the PIN plus your fixtures), with
   `core.hooksPath` pointed at a temporary directory that holds ONLY a copy of H (no post-commit hook runs): commit one clean change,
   AQ1 (must be blocked, rc 4), your strongest new fail-open from items 2-4, and your strongest new false refusal. Paste each
   commit's outcome and rc.
7. Cost, through the real screen: the `$((` k-series up to the recursion guard (the builder: k=330 in 0.59 s, k=400 refused);
   D8's `((` form at k=2000 (KNOWN; measure only to compare); a 5 MB gate-shaped shell file with deep `$( "$( … )" )` nesting;
   50,000 heredocs; a 2 MB single line. A super-linear case outside D8 is a finding.
8. MUTANTS (new; never the builder's m1-m13, N13 or N19): scratch copies under `/tmp/vj10r5/mut/` only. At least one per contract
   line R5-1, R5-2 and R5-4, each targeting a line the builder's rows did not touch. Each mutant compiles and collects (AF-AP-78);
   before you count a kill, run the killing test on the UNMUTATED copy and paste that it passes (AF-AP-138). A survivor is a finding.
9. GATES, each command with its output and the set id (`bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py`):
   T twice; `python3 scripts/no_laya_in_gates.py` and `--staged` on the shared tree (read-only use of the index); pyflakes on S and T.

## Boundary

CREATE `tasks/briefs/laya/VERIFY-J1-0-R5-report.md` (write it incrementally from the start); nothing else in the repository.
NEVER place a modified screen, list or test in the SHARED tree, not even for a moment: the pre-commit hook runs the screen from the
working tree (AF-AP-148), and a modified copy there blocks every commit on the branch. Every mutant, fixture tree and throwaway
repository lives under `/tmp/vj10r5/` and is removed at the end (the sandbox had about 1.8 GB free at authoring). pytest:
`-p no:cacheprovider --basetemp=/tmp/vj10r5/bt<n>` (create the parent first), removed after each run. Other sandbox agents work in this
tree on disjoint files: J1-1-R2 (`src/agent_factory/decisions/volatile.py`, `tests/test_decisions_canonical.py`,
`tests/test_decisions_ledger.py`, `tasks/briefs/laya/J1-1-R2-report.md`) and possibly B11 (`proofs/S0-02/check_buzz_authz.py`,
`proofs/S0-02/spec.json`, `tests/test_s0_02_buzz_authz.py`, `tasks/briefs/s0-02-support/`): never touch, run or revert them. Nothing
under `.claude/` is edited. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push` in the
shared tree. No outward-facing action; no PC or bridge use.

CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
`scripts/lane_context.sh -q 'how does the never-a-gate screen decide a gate file sources unlisted code through a heredoc, an ANSI-C word or a workflow run value' -s _unquote -s _ShellScan -s arith -s _workflow_runs -o /tmp/vj10r5/pack.md scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py scripts/hooks/pre-commit`.

PREDICATE: a finding blocks only if it is contract-mapped (R5-1..R5-5, or AMENDMENT 2/3 where R5 changed the code that enforces
them), reproduced through the real screen (and, for anything claimed about commits, through the real hook in the throwaway
repository), materially effective (a gate file sources or loads unlisted code and the screen reads CLEAN; or a live-tree shape is
falsely refused; or a stated claim is false as stated), with a concrete discriminator, and in-boundary (S, T, L). Everything else is a
follow-up. Emit ONE GATE RECOMMENDATION: `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`. The
coordinator owns the final gate.

Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-0-R5-report.md --root .` (cite full
repo-relative paths, or pass `--map` flags and paste them); apply its `fix:` hints for at most three rounds, then paste and finish.
The report ends with DISCREPANCIES and NOT-done.

## PREMISE — MEASURED at authoring (2026-09-23 14:0xZ, sandbox @ local 1a952ca; origin 98e2efc)
```
$ date -u +%Y-%m-%dT%H:%MZ
2026-09-23T14:07Z
$ git log -1 --format="%h %s" 10f1823 | cut -c1-90
10f1823 J1-0-R5 landed (task #188; GATED-PENDING-VERIFY; VERIFY-J1-0-R5 = task #193): the 
$ git diff --stat 10f1823^ 10f1823
 scripts/no_laya_in_gates.py         |  81 +++--
 tasks/briefs/laya/J1-0-R5-report.md | 581 ++++++++++++++++++++++++++++++++++++
 tests/test_no_laya_in_gates.py      | 157 ++++++++++
 3 files changed, 795 insertions(+), 24 deletions(-)
$ blob[:12] lines path (at 10f1823)
4f88fbb47d02  1452 scripts/no_laya_in_gates.py
d2e04630f09d  1254 tests/test_no_laya_in_gates.py
8eaccfa87a98    53 scripts/gate_files.txt
7731a91c7d3e   133 scripts/hooks/pre-commit
$ git diff --quiet 10f1823 origin/claude/soundbox-kit-migration-iz1jwf -- scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py scripts/gate_files.txt scripts/hooks/pre-commit && echo "boundary identical at origin head"
boundary identical at origin head
$ grep -n (R5 seams, the screen)
128:def _unquote(word):
150:class _ShellScan:
174:    def scan(self):
338:    def arith(self, start, skip, what):
354:            raise _Open(self.line(start), what + " re-read with other heredocs pending")
454:            raise _Open(self.line(start), "heredoc <<%s: $'...' escape not translated" % word)
493:        opened = (first_line, "constructs nested too deep to scan")
497:def _workflow_runs(content):
732:ALLOWED_DYNAMIC_LOADS = {
$ python3 -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp /tmp/pm2/bt | tail -1
112 passed in 8.64s
$ bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py
1 files set=e3695f80792b
$ python3 scripts/no_laya_in_gates.py; echo rc=$?; python3 scripts/no_laya_in_gates.py --staged; echo rc=$?
no_laya_in_gates: 40 files scanned, clean
rc=0
no_laya_in_gates: 40 files scanned, clean
rc=0
$ grep -c . scripts/gate_files.txt
53
```
