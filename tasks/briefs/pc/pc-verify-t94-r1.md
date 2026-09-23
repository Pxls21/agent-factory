# VERIFY-T94-R1 — the targeted re-verify of T94 after its one focused repair (tasks #200 + #167)

PIN: 6963f00
ROLE: adversarial-verifier (read-only against production; every mutation on a scratch copy)
REPORT: write `tasks/briefs/pc-t90-support/VERIFY-T94-R1-report.md` (untracked is fine) and paste its summary as your final answer.

## Why this lane exists

VERIFY-T94 (`tasks/briefs/pc-t90-support/VERIFY-T94-report.md`, PIN 4a38190) returned NOT-READY on ONE blocker, F-1: the
FAILED-UNRETRIED branch of the dispatcher's poll probe (`scripts/pc_lane.sh:391`) reads `lane.pid` through its own remote
command substitution, and no executed case reached that branch, so a doubled escape there survived T2. T94-R1 (commit 2f055f7,
test-only) added three executed cases to `harness-ports/tests/test_pc_lane_dispatcher.sh` (T2:493, :499, :504). The same report
left two of its contract items UNVERIFIED for lack of time: the stale-FAILED file forms (original item 4) and the named
mutation matrix (original item 7). This lane closes F-1 as the LANE USER and finishes those two items. The frozen contract is
the original brief `tasks/briefs/pc/pc-verify-t94.md`; read it first, then the VERIFY-T94 report.

Out of scope (already filed as follow-ups on issue #54; do not re-litigate): a stale `usage.json` across attempts, the
failed-harvest exit skipping the patch/provider-mix fetch, `cp -f` over an older `report.failed-output.md`.

## Items (report EVERY observation; no severity filter; SOLID/UNSURE per observation)

1. PREMISE. Re-measure the block below in your worktree (the blob ids, the line counts, the two test counts, the grep lines).
   A mismatch is CONTRACT-INVALID: stop and report it.
2. F-1 CLOSED, AS THE LANE USER. Paste `id -u` first. On a scratch copy under `../scratch/mut/` (never in your tree), double
   the escape (`\$(` → `\\$(`) at each of the four remote lookups in the probe line, ONE mutant at a time: the three
   `kill -0 \$(cat …lane.pid…)` sites in order (FAILED-UNRETRIED, READY, RUNNING) and the one `\$(find …launch.log…)`. For
   each: `bash -n` on the mutated D, then T2 against it; paste the count and every `[FAIL]` name. Then the unmutated copy.
   The coordinator ran this as ROOT (uid 0) and pasted the results below. QUESTION (measure; do not assume): as your user, which
   `EXECUTED probe:` case kills the FAILED-UNRETRIED mutant? The coordinator's reading: the mutant hands the PC
   `kill -0 \ 2>/dev/null`, bash reads " 2" as pid 2, root may signal it and a normal user may not, so the killing case can
   differ between root and a user. Confirm or refute with the pasted output. A mutant that survives here is a blocker.
3. THE STALE-FAILED FILE FORMS (the original item 4, left UNVERIFIED). With T1's fake-repo pattern (never a real lane
   directory): FAILED as a directory, a symlink (to a file outside the lane directory, and dangling), a FIFO, an unreadable
   file; `FAILED.stale-<ts>` already present (the `.$$` suffix); the rename failing (a read-only lane directory). For each:
   the runtime's exit code, its stderr line, the files left behind, and whether the new loop runs. A hang is a finding: run
   every case under `timeout 60`.
4. THE NAMED MUTANTS (the original item 7, left UNVERIFIED). Each on a scratch copy: the lane's m1-m6
   (`tasks/briefs/pc-t90-support/T94-report.md` section 5, the Mutation audit table; the original brief says section 6) and the coordinator's Ma-Me (the body of commit 1a94bbb), on the
   PIN's bytes; plus at least four of your own (for example: the rename moved before the state guard; `completed is False`
   dropped from the runtime verdict; the harvest header check shortened to a prefix of one word; FAILED-UNRETRIED's grep
   anchored without `^`). Paste each mutant's diff (one line is enough), its count, and the killing test name. A survivor is a
   finding against the tests: name the missing state.
5. GATES (each call under the 420 s cap): `bash -n harness-ports/bin/pc-lane.sh`, `bash -n scripts/pc_lane.sh`; T1 twice and
   T2 twice, counts pasted; `bash harness-ports/tests/run-all.sh` once. VERIFY-T94 saw one host failure in run-all
   (`test_qwen_matrix_sh.sh`, `SECOND_SIGINT`) that also fails on a clean archive of the PIN; if it recurs, show it on a clean
   `git archive 6963f00` copy before calling it pre-existing.
6. REPORT AND GATE RECOMMENDATION. Every finding with file:line, the reproduction command, and SOLID/UNSURE. End with
   `GATE RECOMMENDATION: MERGE-READY | MERGE-READY-WITH-FOLLOWUPS | NOT-READY | CONTRACT-INVALID` and the blocking predicate
   applied to each blocker (contract-mapped, reproduced on the real path, material, a concrete discriminator, in-boundary).

## Standing do-nots

- Never edit `harness-ports/bin/pc-lane.sh`, `scripts/pc_lane.sh`, `harness-ports/tests/test_pc_lane.sh` or
  `harness-ports/tests/test_pc_lane_dispatcher.sh` in your tree; every mutation lives under `../scratch/`.
- Never read `~/.hermes/`; never touch any `.lanes/` directory other than your own; never kill a process you did not start.
- No outward-facing actions (no PRs, issues, comments, pushes). Do not spawn subagents.
- Bound the report lint: apply its `fix:` hints for at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 20:4xZ, /home/user/agent-factory@6963f00)

```
$ git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
6963f00
$ git log --oneline -3 6963f00
6963f00 transcripts: scrubbed sandbox chat digests (2026-09-23)
2f055f7 T94-R1: executed poll-probe cases for the FAILED-UNRETRIED branch (VERIFY-T94 F-1) + the VERIFY-T94 harvest
e110739 transcripts: scrubbed sandbox chat digests (2026-09-23)
$ git diff --stat 4a38190 6963f00 -- harness-ports scripts/pc_lane.sh
 harness-ports/tests/test_pc_lane_dispatcher.sh | 19 +++++++++++++++++++
 1 file changed, 19 insertions(+)
$ for p in R D T1 T2: git rev-parse --short=12 6963f00:<path>; git show 6963f00:<path> | wc -l
623c5e7fc8c4 581 harness-ports/bin/pc-lane.sh
cbb361842e3e 627 scripts/pc_lane.sh
c4c64d64665a 736 harness-ports/tests/test_pc_lane.sh
450073915d79 575 harness-ports/tests/test_pc_lane_dispatcher.sh
$ git diff origin/claude/soundbox-kit-migration-iz1jwf -- harness-ports scripts/pc_lane.sh | wc -l   (the working tree the counts below ran in)
0
$ bash harness-ports/tests/test_pc_lane.sh 2>/dev/null | tail -1
67 passed, 0 failed
$ bash harness-ports/tests/test_pc_lane_dispatcher.sh 2>/dev/null | tail -1
pc_lane dispatcher: 51 passed, 0 failed
$ grep -n 'EXECUTED probe:' harness-ports/tests/test_pc_lane_dispatcher.sh | cut -c1-110
459:check "EXECUTED probe: a stale FAILED (older than this dispatch's brief) with a live loop polls RUNNING; t
464:check "EXECUTED probe: this dispatch's own FAILED (not older than the brief) ends the poll with LANE FAILE
469:check "EXECUTED probe: report.md present while the lane loop is alive polls RUNNING, never READY (the pid 
475:check "EXECUTED probe: report.md present with the lane loop gone polls READY" $? \
480:check "EXECUTED probe: no pidfile yet and a fresh launch.log (the launch window) polls RUNNING (the find r
485:check "EXECUTED probe: no pidfile, no report and a stale launch.log polls GONE" $? \
493:check "EXECUTED probe: an API-failure line while the lane loop is alive polls RUNNING (the loop retries; t
499:check "EXECUTED probe: an API-failure line with the lane loop gone polls FAILED-UNRETRIED, rc 70" $? \
504:check "EXECUTED probe: a '⚠️ No reply:' line with the lane loop gone polls FAILED-UNRETRIED (the patte
$ grep -n -o 'echo FAILED-UNRETRIED' scripts/pc_lane.sh; grep -o -n 'kill -0 \\$(cat' scripts/pc_lane.sh | wc -l; grep -c -F '$(find' scripts/pc_lane.sh
391:echo FAILED-UNRETRIED
3
1
$ id -u   (the coordinator's sandbox runs the tests as root)
0
$ (scratch copy: git archive HEAD scripts harness-ports + the working-tree T2; mutate the probe line of scripts/pc_lane.sh; run T2; as uid 0)
M-unretried (FAILED-UNRETRIED cat site) bash-n=ok -> [FAIL] …API-failure line with the lane loop gone polls FAILED-UNRETRIED, rc 70 [FAIL] …'⚠️ No reply:' line with the lane loop gone… pc_lane dispatcher: 49 passed, 2 failed
M-ready (READY cat site) bash-n=ok -> [FAIL] …report.md present with the lane loop gone polls READY pc_lane dispatcher: 50 passed, 1 failed
M-running (RUNNING cat site) bash-n=ok -> [FAIL] …no pidfile, no report and a stale launch.log polls GONE pc_lane dispatcher: 50 passed, 1 failed
M-find (find site) bash-n=ok -> nine EXECUTED probe cases [FAIL] pc_lane dispatcher: 42 passed, 9 failed
M-none -> pc_lane dispatcher: 51 passed, 0 failed
```
