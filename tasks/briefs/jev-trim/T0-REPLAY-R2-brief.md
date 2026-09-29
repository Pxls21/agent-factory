# T0-REPLAY round 2: can wider rules and a trim guard hold the context at a set level? (task #346, D-105)

Written 2026-09-29 00:2xZ by the coordinator for the T0 builder, resumed. Lane: sandbox `code-implementer`, model opus.
Your round 1 is committed (the commit "T0-REPLAY round 1 (task #346, D-105): the replay tool, its tests and outputs
..."); your report of record is `tasks/briefs/jev-trim/T0-REPLAY-report.md`. You measure; the design stays in the main
loop, so again: no design recommendation.

## Why this round

Round 1 showed the first rule set cannot hold any budget the owner named (the design's §9,
`docs/research/findings/jev-trim/D105-DESIGN-v1.md`): with the last two stop-hook turns protected, the protected part
alone passes 200k in 63.7% of this session's requests; no rule covers the hand-back texts or the attachments; and on
the lane-like runs a trimmer that cannot reach L fires on the next request again, so the cache cost rises 57% to 368%.
The owner's words stand (D-105): keep the context "at the optimum level" so "we never get to a stage where we need
compaction", "the logs are still there ... It's just the active context".

## Boundary

- MODIFY `scripts/jev_trim/replay.py` and `tests/test_jev_trim_replay.py`. CREATE the round-2 outputs under
  `docs/research/findings/jev-trim/replay-2026-09-29/`, written by `replay.py`, never by hand. Round 1's outputs stay
  byte-identical (a test or a re-run shows it).
- READ, never modify: `scripts/jev_pipes/` (the P1 walker and miss definition) and everything else.
- No git writes, no PC bridge, no subagents, no outward action, no model or network call. Start no process that outlives
  your run. Overwrite outputs by name; never delete through a variable-built glob (a safety check refused one in round
  1, and so it should).
- Live lanes in this tree (`.lanes-live`): touch none of their files.
- Same safety as round 1: stream the transcripts in memory; outputs carry counts, sizes, offsets, ids, tool, kind and
  rule names only; never read a thinking block's text; read no secret or `*.env` file; a refused read is reported,
  never worked around.

## Items (each with a test and a named mutant the test kills)

1. **Premise.** Re-run the PREMISE block below; on an unexpected difference, stop and report CONTRACT-INVALID.
2. **Protection by a request window, in both modes.** The `request` unit with K in {3, 10, 30} (the current request and
   the last K requests protected), on the main transcript too. In `between-turn` mode a trim still fires only at a turn
   start, but it may archive items of the finished turn that lie outside the window. The other protected kinds stay
   (typed text, the segment's first user message, the newest copy of each skill body).
3. **R5, hand-backs.** A user-side item that carries a subagent hand-back or a task notification, older than A
   requests, becomes a stub. (The harvest stack saves every report of record to the repo, so the stub can point there.)
   Recognize the item by the record's structure or its envelope's opening tag (the agent-message and task-notification
   wrappers), never by printing text; report how many items the rule recognizes, and test a negative control (an
   ordinary user text is not taken).
4. **R6, attachments.** An attachment superseded by a newer one of the same type (and of the same key where the type
   has one, such as the same file for an edited-file snippet) is archived; any other attachment older than A becomes a
   stub, except a skill body. Report the attachment types found, with their counts and tokens.
5. **A trim guard**, one of: `none` (round 1's behavior); `reach` (fire only when archiving every eligible item would
   bring the context to L or below, else archive nothing at that request); `cooldown:C` (fire at most once per C
   requests; C in {10, 30}).
6. **Two cache bounds.** Round 1's model (the tail after the edit point is written again) and a pessimistic bound in
   which every trim rewrites everything after the fixed start (the system prompt and tools), for the 20-block lookback
   your D16 names. Report both, at read 0.05 and 0.1.
7. **What the active context is made of.** For each reported cell, the tokens by kind at the median request after
   trimming, so the floor is visible.
8. **The grid and the runs.** B in {100000, 131072, 200000}, L in {0.75 B, 0.6 B}, A in {10, 20}, K (requests) in
   {3, 10, 30}, rule sets {R1-R4, R1-R6}, the four guards, and both modes on the main transcript; `per-request` on the
   three subagent transcripts. Keep round 1's pins (main 780,424,880 from offset 740,755,248; the three subagent files
   at 14,082,496, 11,814,169 and 9,235,269) so the rounds compare. Put the full grid in the JSON and markdown; in the
   report, the rows that hold the median at or under B, if any, and the best row per budget.
9. **Gates**, each twice, with `--basetemp` as a pytest argument outside any work tree, pasted from
   `bash scripts/test_summary.sh` with the set id: `tests/test_jev_trim_replay.py` and `tests/test_jev_pipes_replay.py`.

## Report

Return the whole report as your final message (not a summary): the premise re-run; files with line counts and
sha256; the gates; the mutants; per run, the rows item 8 names; R5's and R6's recognition counts and attachment types;
the composition at the median; a DISCREPANCIES list; and your self-attack.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin 0c11fd1)

Printed by `bash scripts/premise_block.sh` from the main tree. Round 1's commit is local at authoring (the push waits on
CI), so its files are checked by hash and by commit subject. Expected to differ when you re-run it: nothing.

```
$ git merge-base --is-ancestor 0c11fd1 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git log -1 --format=%s -- scripts/jev_trim/replay.py
T0-REPLAY round 1 (task #346, D-105): the replay tool, its tests and outputs; the first rule set misses the budgets
$ sha256sum scripts/jev_trim/replay.py tests/test_jev_trim_replay.py | cut -c1-16,65-
ff35dbb8541818bd  scripts/jev_trim/replay.py
92b29e6d5b364b43  tests/test_jev_trim_replay.py
$ git status --porcelain -- scripts/jev_trim/ tests/test_jev_trim_replay.py docs/research/findings/jev-trim/replay-2026-09-28/ | wc -l
0
$ ls docs/research/findings/jev-trim/replay-2026-09-29 2>&1 | head -1
ls: cannot access 'docs/research/findings/jev-trim/replay-2026-09-29': No such file or directory
$ git diff --stat 0c11fd1 HEAD -- scripts/jev_pipes/ tests/test_jev_pipes_replay.py | tail -1
$ python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/t0r2-premise-bt tests/test_jev_trim_replay.py tests/test_jev_pipes_replay.py 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
78 passed
$ bash scripts/pc_suite.sh set-id -- tests/test_jev_trim_replay.py tests/test_jev_pipes_replay.py | tail -1
2 files set=5365c5f240ce
```
