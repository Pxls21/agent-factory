# VERIFY-J1-0-R6 — the targeted independent adversarial verify of J1-0-R6: the never-a-gate screen names a workflow `run:` value's line from its scalar token (AMENDMENT 5), and the AF-AP-159 screen row (task #201)

PIN: c6dcd61 (the origin head: "AF-AP-159 registered with a screen row …"; J1-0-R6 itself is 96c2cff, the post-push SHA of local
d116e3d, and its code is byte-identical at c6dcd61). Confirm with `git log --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf -4`.
LANE: pc-verify-j1-0-r6
ROLE: adversarial-verifier on the local route. The contract-gate predicate (D-031): a finding BLOCKS only if it is contract-mapped
(AMENDMENT 5 below), reproduced through the real screen (`python3 scripts/no_laya_in_gates.py --root <tree>`, and `--staged` in a
throwaway git repository for anything claimed about commits), materially effective (a gate file sources unlisted code and the screen
reads CLEAN; or a refusal names a line outside the value it refuses; or an rc differs from R5's on any input; or a stated claim is false
as stated), with a concrete discriminator, and inside the boundary (S, T, H, A below). Everything else is a follow-up. Emit ONE GATE
RECOMMENDATION: `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`; the coordinator owns the gate.

WHY THIS LANE EXISTS: J1-0-R6 was built by the COORDINATOR in the main loop (the fix was the previous verifier's, run on a scratch
copy). Its only gates were the coordinator's own tests and seven mutants, so it is GATED-PENDING-VERIFY under rule 0f. Your job is
new shapes, never the coordinator's.

COMPONENT: `scripts/no_laya_in_gates.py` (S; the function `_workflow_runs`, S:497-531), `tests/test_no_laya_in_gates.py` (T),
`.claude/hooks/edit-snapshot.py` (H; the AF-AP-159 row, H:188-191), `tests/test_edit_snapshot_ap_screen.py` (A).
CONTRACT (frozen): AMENDMENT 5 = the ledger note "VERIFY-J1-0-R5 HOME, NOT-READY BY RULING; J1-0-R6 UNDER AMENDMENT 5" in
`todo/BUILD-TASKLIST.md` plus the J1-0-R6 commit body (`git show 96c2cff`): (a) every refusal in a `run:` value names a line INSIDE the
value, whatever properties (`&anchor`, `!!tag`) precede the scalar and on whatever lines; (b) a literal block (`|`) keeps its
line-for-line map; any other style names its first line; (c) no rc changes from R5 on any input (the fix moves lines only);
(d) `_workflow_runs`'s docstring states exactly what the code does. AMENDMENT 4 (`tasks/briefs/laya/J1-0-R5-brief.md`, R5-1..R5-5)
still holds underneath. INPUTS TO ATTACK, not truths: the J1-0-R6 commit body, the AF-AP-159 row in `docs/INCIDENT-LOG.md`, and the
previous verifier's report `tasks/briefs/laya/VERIFY-J1-0-R5-report.md` (§ 4 and its appendix hold R5's fixture texts).
KNOWN, never blocking here: issue #50 (V5-01…V5-12 outside AMENDMENT 5), issue #46, issue #37 (class F-B3), and V-18 (an alias names
its anchor's line, twice).

## Items (report EVERY observation; no severity filter; SOLID/UNSURE per observation)

1. PREMISE. Re-measure the block below in your worktree (blob ids, the grep, the counts with the set id, the W10b pair). Note that
   the PC's PyYAML is 6.0.3 and the sandbox's is 6.0.1: if any mark or token behaves differently between them for your shapes, that is
   a finding with both outputs. A boundary mismatch is CONTRACT-INVALID for the affected items; say which.
2. SHAPES (new ones; never T's W10, W10b, W11, W12, W12b, MX6 or the empty-value test). For each: the file text, whether bash runs the
   helper when given PyYAML's value (`bash --noprofile --norc -c "$value"` from the tree root), R5's line and rc (S at b91673e), R6's
   line and rc, and whether R6's line is inside the value (for `|`, the helper's own line). At least:
   (a) an anchor and a tag on separate lines before the scalar, in both orders; (b) a property on the SAME line as the indicator
   (`run: &x |`); (c) a comment line between the property and the scalar; (d) `|-`, `|+`, `>-`, `|2` and `>2` behind a property;
   (e) two YAML documents in one file (`---`), each with a sourcing `run:`; (f) an alias `run: *x` whose anchor is a block elsewhere
   (V-18 is KNOWN; report only what is new); (g) a flow mapping `{run: &x ". scripts/h.sh"}` and a flow sequence element holding a
   mapping; (h) a quoted key `"run":` and a complex key `? run`; (i) a property on the key (`&k run: …`); (j) Windows line endings
   (`\r\n`) and a tab where YAML allows one; (k) a value that is a block scalar whose FIRST content line is blank, behind a property.
3. THE DOCSTRING (S:498-504). Quote each sentence and say, for your shapes, whether it is true as stated. Name any word that claims
   more than the code does.
4. DIFFERENTIAL. Write your own generator of workflow texts (properties, styles, indentation, documents, comments, blank lines; at
   least 20,000 inputs, bash-parseable values only) and run R5 (S at b91673e) and R6 over the same texts. Paste: the count of inputs
   where the rc differs (the contract says zero; each one is a finding), and every input class where the named lines differ, with R5's
   and R6's line and which is inside the value.
5. COST. The fix adds one `yaml.scan` pass per workflow file. Time R5 and R6 on workflow files of 1, 10, 100 and 1000 steps (each step
   behind a property), median of 5 runs each, with the per-doubling ratio. Say whether anything grows faster than linearly.
6. THE SCREEN ROW (H:190, `\.start_mark\.line\s*\+`). (a) Does it fire on R5's line (S:521 at b91673e) and on nothing in S at the PIN?
   (b) Run `python3 scripts/ap_screen.py` over `scripts/ proofs/ src/ harness-ports/` and paste its AF-AP-159 hits (a hit outside a
   YAML line map is a false positive: say so). (c) Name any spelling of the defect the regex misses (for example a start mark bound to a
   variable first, or `start_mark.line` added on the right: `2 + node.start_mark.line`), and say whether A's four tests would catch
   the regex being widened or narrowed.
7. MUTANTS (new; never the coordinator's m1-m7, which are listed in the J1-0-R6 commit body). At least four on `_workflow_runs` and
   one on the H row. Each mutant compiles and collects (AF-AP-78); before you count a kill, run the killing test on the UNMUTATED copy
   and paste that it passes (AF-AP-138). A survivor is a finding.
8. GATES, each with its output: `python -m pytest -n 8 tests/test_no_laya_in_gates.py tests/test_edit_snapshot_ap_screen.py -q -p
   no:cacheprovider` twice (each call under the 420 s cap) with `bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py
   tests/test_edit_snapshot_ap_screen.py` (the landing: `220 passed`, set `f4e9ba5ca7d1`); `python3 scripts/no_laya_in_gates.py` and
   `python3 scripts/no_laya_in_gates.py --staged` on your worktree (both `40 files scanned, clean`); pyflakes on S, T and A.

## Boundary and standing do-nots

CREATE `tasks/briefs/laya/VERIFY-J1-0-R6-report.md` in your lane tree (write it incrementally from the start); nothing else. Every
scratch copy, mutant, fixture and throwaway repository lives under `$HOME/tmp-vj10r6/` (never the PC's tmpfs `/tmp` for trees or
basetemps, AF-AP-112) and is removed at the end. Never edit S, T, H or A in your lane tree; mutate only scratch copies. This is the
owner's PC: user scope only, no sudo; never stop, restart or edit OmniRoute, the vLLM `qwen` container, the Buzz relay, the
`laya-systemone` unit, Ollama, Phoenix, OpenObserve or neo4j; never touch another lane's tree or the lane tree
`.lanes/pc-jev-laya-pc.md--dd4c579/` (the live Laya unit runs from it); never print a `.env` file. No outward-facing action (no push,
PR, comment or issue). Fake strings only in fixtures.

CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
`scripts/lane_context.sh -q 'how does the never-a-gate screen map a workflow run: value to its file line' -s _workflow_runs -s _source_errors -o $HOME/tmp-vj10r6/pack.md scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py`

Report lint: `python3 scripts/report_lint.py --min-refs 12 tasks/briefs/laya/VERIFY-J1-0-R6-report.md --root .` (full repo-relative
paths, or `--map` flags pasted with it); apply its `fix:` hints for at most three rounds, then paste and finish. The report ends with
DISCREPANCIES and NOT-done.

## PREMISE — MEASURED at authoring (2026-09-23 15:5xZ, sandbox /home/user/agent-factory, worktree == c6dcd61 for all four files)
```
2026-09-23T15:50Z
$ git log --format='%h %s' -3 origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-90
c6dcd61 AF-AP-159 registered with a screen row (a node's start read as its content's start
96c2cff J1-0-R6 landed (task #199; GATED-PENDING-VERIFY): the never-a-gate screen names a 
b91673e Ledger plane 2026-09-23 15:3xZ: VERIFY-J1-0-R5 ruled NOT-READY (J1-0-R6 under AMEN
$ for f in <boundary>; do echo "$(git rev-parse c6dcd61:$f | cut -c1-12) $(git show c6dcd61:$f | wc -l) $f"; done
21e2bcb263e5 1457 scripts/no_laya_in_gates.py
3dee79b1e293 1294 tests/test_no_laya_in_gates.py
b52a0d8ab536 481 .claude/hooks/edit-snapshot.py
d7448f51bb89 489 tests/test_edit_snapshot_ap_screen.py
$ git diff --stat b91673e c6dcd61 -- scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py
 .claude/hooks/edit-snapshot.py        |  4 ++++
 scripts/no_laya_in_gates.py           | 17 +++++++++------
 tests/test_edit_snapshot_ap_screen.py | 18 ++++++++++++++++
 tests/test_no_laya_in_gates.py        | 40 +++++++++++++++++++++++++++++++++++
 4 files changed, 73 insertions(+), 6 deletions(-)
$ git show c6dcd61:scripts/no_laya_in_gates.py | grep -n 'def _workflow_runs\|token_line\|compose_all\|value.style == "|"'
497:def _workflow_runs(content):
511:        stack = list(yaml.compose_all(content, Loader=yaml.SafeLoader))
513:        token_line = {t.end_mark.index: t.start_mark.line for t in yaml.scan(content, Loader=yaml.SafeLoader)
526:                    line = token_line.get(value.end_mark.index, value.start_mark.line)
527:                    runs.append((line + (2 if value.style in ("|", ">") else 1), value.value, value.style == "|"))
$ grep -n 'AF-AP-159' .claude/hooks/edit-snapshot.py
188:    # AF-AP-159 (2026-09-23, VERIFY-J1-0-R5 V5-05): a PyYAML node's start_ma
190:    ("AF-AP-159", re.compile(r"""\.start_mark\.line\s*\+"""),
191:     "a line number computed from a node's start_mark — a YAML node starts
worktree == c6dcd61: scripts/no_laya_in_gates.py
worktree == c6dcd61: tests/test_no_laya_in_gates.py
worktree == c6dcd61: .claude/hooks/edit-snapshot.py
worktree == c6dcd61: tests/test_edit_snapshot_ap_screen.py
$ for i in 1 2; do python -m pytest -q -p no:cacheprovider tests/test_no_laya_in_gates.py tests/test_edit_snapshot_ap_screen.py | tail -1; done
220 passed in 9.50s
220 passed in 9.88s
$ bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py tests/test_edit_snapshot_ap_screen.py
2 files set=f4e9ba5ca7d1
$ W10b (run: &x / | / . scripts/h.sh on lines 6-8) through R5 (b91673e) and R6 (c6dcd61)
b91673e: gate-file-sources: .github/workflows/w.yml:7: scripts/h.sh rc=4
c6dcd61: gate-file-sources: .github/workflows/w.yml:8: scripts/h.sh rc=4
$ python3 -c "import yaml,sys; print(sys.version.split()[0], yaml.__version__)"   (sandbox; the PC read 3.13.11 6.0.3 at 15:5xZ)
3.11.15 6.0.1
```
