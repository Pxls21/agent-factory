# LS-B9 round 4: four small fixes, the catalog notes, and the SessionStart wiring (task #339, D-103)

Written by the coordinator for the original LS-B9 builder, resumed. Your stack runner landed on origin (the commit "LS-B9
landed (task #339, D-103): the stack runner and wave 1 ..."); VERIFY-LS-B9 round 3 recommended MERGE-READY-WITH-FOLLOWUPS,
and its follow-ups are GitHub issue #80. This round takes the ones that make the stacks safe to put in front of every
session, and wires them in.

## The owner's words (D-103, 2026-09-28 14:45:08Z)

"Create script stacks ... that are supposed to be run and then tie them to specific labels. And then you put them in the
output styles"; "because of the way the labels are, it'll use the scripts, the tools in the correct way each every
time". Design v2 (`docs/research/findings/labeling/LS-DESIGN-v2-2026-09-28.md` §6, LS-B6): this session does not load the
output-style setting, so a SessionStart line injects the catalog and CLAUDE.md gets one pointer; the vendored style
files stay untouched.

## Boundary

- MODIFY: `scripts/stack.py`, `scripts/stacks.toml`, `scripts/handback_extract.py`, `tests/test_stack.py`,
  `scripts/install_session_hooks.py`, `tests/test_session_hooks.py`.
- `.claude/settings.json` changes ONLY through `scripts/install_session_hooks.py` (run it; never hand-edit the file).
- READ everything else. CLAUDE.md is the coordinator's: propose its one pointer line in your report, word for word.
- No git writes, no PC bridge, no subagents, no outward action. Start no process that outlives your run.
- Other lanes are live in this tree (`.lanes-live` lists their files). Touch none of them.

## Items (each with a test and a named mutant the test kills; a real run pasted where it applies)

1. **Premise.** Re-run the PREMISE block below; on an unexpected difference, stop and report CONTRACT-INVALID.
2. **R3-F3.** `harvest`'s report window starts at the first user record after the previous hand-back call (the resume
   message), so an earlier round's epilogue is never this round's `report.md`. Test: the verifier's synthetic shape
   (round-1 report, call 1, a 4,000-character round-1 epilogue, the resume, a short text, a 160-character call 2) gives no
   `report.md` from the epilogue; the control (round 2 writes its own long text) still picks round 2's text.
3. **R3-F1.** The header's counts line never falls to the print cap: print it before `params:`, or cut `params:` first.
   Test: a `paths` value of 9,562+ characters keeps the `sources ·` counts line in the print.
4. **R3-F4.** One test per surviving mutant: X1 (a stray child that ignores SIGTERM is still killed), X2 (a headline
   longer than `HEADLINE_MAX` is cut with `…`), X3 (a gate over a path that only `run-all.sh` names runs `run-all.sh` with
   bash, never NOTHING TO RUN), X6 (a refused run with a `.sh` test runs no shell test).
5. **R3-F5.** A headline's control characters (CR, ESC and the rest of C0 and C1) are escaped in the header.
6. **The catalog notes.** Each stack in `stacks.toml` may carry short notes, and `stack.py list` prints them under its
   line. Put in the seven notes of issue #80's last section, each under the stack it concerns, and an eighth under `harvest`: `report=` names an existing file to lint and hash; the hand-back itself is saved under the run directory as `handback.md` (the coordinator read `report=` as a save path on 2026-09-28 and the lint step failed on a missing file).
6b. **Local commit ids in a hand-back.** `harvest` gains one advisory step (not required, like `lint_handback`): it
   lists each commit id in the hand-back that `git log origin/<branch>..HEAD` shows as local, with its line, because
   the push rewrites those ids and `stale_ids` then refuses the push (T1-LCM-AUDIT's report cited two on 2026-09-29;
   the coordinator caught them by hand before the commit). A test with a planted local id, a control with an origin
   id, and a mutant the test kills.
7. **The SessionStart wiring.** `install_session_hooks.py` also registers a SessionStart hook (on start, resume and
   compact) that prints one short heading line, `stack.py list`'s output, and one line on ratings (`--rate <run
   id>=<rel>/<use>`, content stacks only). It exits 0 always; if the catalog cannot be built it prints ONE line naming
   why (fail loud, never silent). Its whole output stays under 4,000 characters (above 10,000 the harness shows only a
   2,000-character preview, AF-AP-183); a test pins the cap. The installer stays idempotent (a second run changes
   nothing) and keeps LS-B7's hooks as they are.
8. **Gates**, each twice, with `--basetemp` as a pytest ARGUMENT outside any work tree (never through `PYTEST_ADDOPTS`:
   the gate stack's inner pytest inherits it and deletes the outer temp tree, AF-AP-237), pasted from
   `bash scripts/test_summary.sh` with the set id from `bash scripts/pc_suite.sh set-id -- <files>`:
   `tests/test_stack.py`, `tests/test_session_hooks.py`, `tests/test_task_sync.py`, and your round-1 five-file set.
   Gate in your own tree (a git work tree); `lane_gate.sh`'s copy is not one.

## Report

Return the whole report as your final message: the premise re-run, the files with line counts and sha256, the gates
pasted, the mutants, the real runs (`stack.py list`; the SessionStart hook's output with its character count), the
CLAUDE.md pointer line you propose, and a DISCREPANCIES list.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin 0749fe5)

Printed by `bash scripts/premise_block.sh` from the main tree. Item 6b and this block are local at dispatch (the push
waits on CI), so the block measures the tree you work in. Expected to differ when you re-run it: nothing.

```
$ git merge-base --is-ancestor 0749fe5 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git log -1 --format=%s -- scripts/stack.py
LS-B9 landed (task #339, D-103): the stack runner and wave 1; VERIFY-LS-B9 round 3 MERGE-READY-WITH-FOLLOWUPS
$ sha256sum scripts/stack.py scripts/stacks.toml scripts/handback_extract.py tests/test_stack.py scripts/install_session_hooks.py tests/test_session_hooks.py | cut -c1-16,65-
a3a24981247588c7  scripts/stack.py
e44d0f5d94d57a41  scripts/stacks.toml
382646e573354170  scripts/handback_extract.py
96c44e0a388ca856  tests/test_stack.py
b78e189d0ac5b7db  scripts/install_session_hooks.py
dddd30002144af50  tests/test_session_hooks.py
$ git status --porcelain -- scripts/stack.py scripts/stacks.toml scripts/handback_extract.py tests/test_stack.py scripts/install_session_hooks.py tests/test_session_hooks.py .claude/settings.json | wc -l
0
$ grep -c '"SessionStart"' .claude/settings.json
1
$ grep -n '^6b\. ' tasks/briefs/labeling/LS-B9-R4-brief.md | cut -c1-60
40:6b. **Local commit ids in a hand-back.** `harvest` gains 
$ bash scripts/pc_suite.sh set-id -- tests/test_stack.py tests/test_session_hooks.py tests/test_task_sync.py | tail -1
3 files set=cebb397be3f6
$ bash scripts/pc_suite.sh set-id -- tests/test_stack.py tests/test_no_laya_in_gates.py tests/test_s0_01_spec_runner.py tests/test_s0_11_eval_hardening.py tests/test_search_intercept.py | tail -1
5 files set=2804489b9d6b
$ rm -rf /tmp/lsb9r4-premise-bt; python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/lsb9r4-premise-bt tests/test_stack.py tests/test_session_hooks.py tests/test_task_sync.py 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
271 passed
```
