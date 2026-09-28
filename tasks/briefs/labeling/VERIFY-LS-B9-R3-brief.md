# VERIFY-LS-B9 round 3: attack the gate's runner routing and round 3's new runner features (task #339)

Role: the VERIFY-LS-B9 verifier, resumed (sandbox adversarial-verifier, Opus 5.5). Do NOT spawn subagents. Report: append
`## Round 3` to `tasks/briefs/labeling/VERIFY-LS-B9-report.md` (your own file) as you go; if the harness refuses the write,
return the rest as the text of your final message, in full.

Authored 2026-09-28 21:3xZ by the coordinator.

The change under test: LS-B9 round 3 (the lane's seven files in the main tree, untracked; hashes in the premise). Its
contract: `tasks/briefs/labeling/LS-B9-R3-brief.md` (items 1-7: F-1 every union file under its own runner or named not run;
F-3 the header counts; F-2 the width bound and the vendored-manifest test never run whole; F-7; F-8; F-11; F-14). The
builder's account: the `## Round 3` section of `tasks/briefs/labeling/LS-B9-report.md`; its claims and its eight
discrepancies are hypotheses.

## WHAT TO ATTACK (report every observation; no severity filter)

1. **F-1, through your own reproductions.** Re-run your three faces (the `scripts/pc_bridge_exec.py` break, the
   `harness-ports/bin/lane-done-gate.py` break, the `omniroute_local_builder.py` abort) in a scratch copy: does each now
   fail or pass for the right reason? Then hunt the class further: a harness file the classifier sends to the wrong runner,
   a runner failure that still reads ok, a file dropped without a "not run" line, a `sources` headline that disagrees with
   what ran.
2. **The four runner features round 3 added on its own design** (its discrepancy 1): `foreach = "@<step>"` (a line that
   escapes the path checks, an empty line, a very long list), `empty_ok` (an empty input that hides a real failure),
   `needs` (a prerequisite that failed, timed out or was unmapped), `headline` (a forged or multi-line first line; the cut
   at `HEADLINE_MAX`). And the changed semantics: an empty pytest list no longer fails the gate (discrepancy 2); scripts
   and shell tests run once while pytest runs `runs` times (NOT-done 2).
3. **F-2 and F-3.** The bound at, below and above `max_files`; the heavy-file rule; the headline's counts against the
   actual run.
4. **F-7, F-8, F-11, F-14.** The at-once SIGKILL; the stray kill (a pid reused between the reap and the kill, a child in
   its own session); the harvest's bounded search on real transcripts; each new test against its mutant.
5. **Your pre-wiring list of six.** Which items hold now, which still need a catalog note.
6. **Mutation.** Reproduce at least five of the builder's 29 round-3 mutants as FAILED tests (T1, W1, K1, S1 and B1 among
   them); add one for each round-3 clause no row covers, and name the survivors.

## GATE

The blocking predicate of skill `contract-gate` and D-034 (only a CORE-BLOCKING finding re-opens the build). One
recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID, each blocking finding with its
reproduction command; then what must hold before the stacks are wired into CLAUDE.md, the output styles and the
SessionStart catalog.

## BOUNDARY AND RULES

READ everything; write only your report and scratch under `/tmp/vlsb9r3/` (removed at the end); no git writes; never write
the main tree's other files, its `.jev/`, `.sentrux-runtime/` or `/root/.claude/`; stack runs against the main tree only
with `--log-dir` in your scratch and only for `list`, `explain`, `premise` and `gate mode=plan`. No PC bridge, no
outward-facing action; never read a real secret source or a thinking block's content. Other lanes are live (VERIFY-I59-F
round 4, SCRUB2-R1 round 3, TRIM-AUDIT); touch none of their files. A private `--basetemp` outside every work tree for every
pytest run; never run the whole `tests/test_vendored_manifest.py`; counts pasted from `scripts/test_summary.sh` with set
ids; stamps from `date -u`; long commands in one foreground call each, under 10 minutes; kill by pid only. When a hook
injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text of its own.

## PREMISE — MEASURED at authoring (2026-09-28 21:3xZ, the main tree; `bash scripts/premise_block.sh`)

```
$ git status --porcelain --untracked-files=all -- scripts/stack.py scripts/stacks.toml scripts/gate_files.py scripts/handback_extract.py scripts/gate_union.py scripts/lint_files.py tests/test_stack.py tasks/briefs/labeling/LS-B9-report.md
 M tasks/briefs/labeling/LS-B9-report.md
?? scripts/gate_files.py
?? scripts/gate_union.py
?? scripts/handback_extract.py
?? scripts/lint_files.py
?? scripts/stack.py
?? scripts/stacks.toml
?? tests/test_stack.py
$ sha256sum scripts/stack.py scripts/stacks.toml scripts/gate_files.py scripts/handback_extract.py scripts/gate_union.py scripts/lint_files.py tests/test_stack.py | cut -c1-16,65-
a3a24981247588c7  scripts/stack.py
e44d0f5d94d57a41  scripts/stacks.toml
b732d35f2c649045  scripts/gate_files.py
382646e573354170  scripts/handback_extract.py
40b64972b40423a8  scripts/gate_union.py
546400ab9781e56f  scripts/lint_files.py
96c44e0a388ca856  tests/test_stack.py
$ grep -c '' scripts/stack.py scripts/stacks.toml scripts/gate_union.py scripts/handback_extract.py tests/test_stack.py
scripts/stack.py:1381
scripts/stacks.toml:499
scripts/gate_union.py:166
scripts/handback_extract.py:151
tests/test_stack.py:2021
$ grep -n '^foreach\|^empty_ok\|^needs\|^headline\|foreach = "@\|empty_ok = \|needs = \|headline = ' scripts/stacks.toml | head -12
157:headline = true
189:empty_ok = true
201:needs = ["sources"]
202:empty_ok = true
209:foreach = "@union_py"
211:needs = ["sources"]
212:empty_ok = true
219:foreach = "@union_sh"
221:needs = ["sources"]
222:empty_ok = true
375:foreach = "files"
$ mkdir -p /tmp/vlsb9r3-premise
$ bash scripts/test_summary.sh --basetemp=/tmp/vlsb9r3-premise/bt tests/test_stack.py | tail -1 | sed -E 's/ in [0-9.]+s.*//'
pytest-summary: 177 passed
$ rm -rf /tmp/vlsb9r3-premise
$ df -m / | tail -1
/dev/vda          258020 26113     11826  69% /
```
