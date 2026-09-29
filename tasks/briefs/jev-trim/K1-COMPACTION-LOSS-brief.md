# K1-COMPACTION-LOSS: what does a compaction lose, and does the work get worse as the context fills? (task #352, D-106)

Written 2026-09-29 02:1xZ by the coordinator for the T0 builder, resumed (T0-REPLAY round 3). Lane: sandbox
`code-implementer`, model opus. You measure; the choice of the compaction point stays in the main loop, so: no design
recommendation. An independent verify follows this round.

## The owner's words (D-106, 2026-09-29 00:51:42Z; voice-typed, quoted where clear)

"for the Claude code sessions that we're in now, just let's just focus on finding the optimal compaction spot and then
have Jev focus on enriching the compaction message and making it better and higher quality and more relevant so that we
lose less data." The owner's first guess for 1M-context models: "maybe it's like 500k". Jev "should only act after it
beats fixed rules on replay". The plan: `docs/research/findings/jev-trim/D105-DESIGN-v1.md` §10 (READ; you build its
R-B and R-C). A sibling lane (K0) gathers the published curves; you measure ours.

## Boundary

- CREATE `scripts/jev_trim/compaction.py`, `tests/test_jev_trim_compaction.py`, and the outputs under
  `docs/research/findings/jev-trim/compaction-2026-09-29/` (written by `compaction.py`, never by hand).
- READ and import, never modify: `scripts/jev_trim/replay.py` (your rounds 1 and 2), `scripts/jev_pipes/` (the P1 walker
  and `accounting.miss`). If a small change to `replay.py` is unavoidable, stop and ask in your report instead.
- READ: `tasks/briefs/jev-trim/k1_authoring_probe.py` (the coordinator's authoring probe, below).
- No git writes, no PC bridge, no subagents, no outward action, no model or network call. Start no process that outlives
  your run. Overwrite outputs by name; never delete through a variable-built glob.
- Live lanes in this tree (`.lanes-live`): touch none of their files.
- Same safety as rounds 1 and 2: stream the transcripts; outputs carry counts, sizes, offsets, ids, tool, kind and rule
  names only; a token set is used in memory and never printed; never read a thinking block's text; read no secret or
  `*.env` file; a refused read is reported, never worked around.

## Items (each with a test and a named mutant the test kills)

1. **Premise.** Re-run the PREMISE block below; on an unexpected difference, stop and report CONTRACT-INVALID.
2. **Pins.** The main transcript from offset 0 to a size you measure at your start (a record boundary), and every
   subagent transcript of this session that holds at least one `compact_boundary` record, each pinned the same way. Report
   the list with sizes and boundary counts. If a whole-file build does not fit in memory, process segment by segment and
   say so.
3. **R-C, the loss at each compaction.** For each boundary: the pre-boundary segment's tokens by kind (what the
   compaction removed); the kept start (the summary record and the injections before the first request after it), in
   tokens; then, over the next N requests for N in {20, 100, the rest of the segment}:
   - the P1 miss (`accounting.miss` with `original` = the pre-boundary segment, `kept` = the kept start, the distinctive
     tokens the following items used), and how many of the missed tokens are paths;
   - re-fetches by call key: a Read of a path the segment read or wrote, a command identical to one the segment ran, a
     search of the transcript, the ledger or the live-state (list the call shapes you count), with the tokens and
     requests they cost;
   - for each missed path, whether the pre-boundary segment read or edited that file (a pack keyed by the path would
     have held a pointer to it).
4. **The control.** The same measures at pseudo-boundaries: request indices inside segments at least 100 requests from
   any real boundary, where nothing was removed (take `original` = the items older than the pseudo-boundary, `kept` =
   everything still in context). Report the excess of the real boundaries over the control, per N.
5. **R-B, the quality curve.** Per 100k of fill (the request's input plus cache tokens), on main and on each subagent
   file: tool errors by tool, failed edits (an Edit or Write whose result is an error), a Read of an unchanged file
   already read in the segment, a command re-run with no edit between, and hook refusals by gate (identify each gate by a
   fixed marker string in the result, matched in memory; list the markers). Rates per bin, and the same inside each
   segment for its first and last third. The coordinator's probe gives a floor to reproduce: on main, tool errors 1.4%
   to 2.1% of calls per bin from 100k to 800k.
6. **The cost model.** For a compaction point X in {300k, 400k, 500k, 600k, 700k, 785k}: from each segment's growth
   (fill per request) and its kept start, the modeled number of compactions over the pinned history, the mean fill per
   request, the cache-read tokens (read 0.05 of base, a parameter), and the modeled loss (item 3's per-boundary miss
   and re-fetch counts times the compactions). Label it a model; state every assumption.
7. **Gates**, each twice, with `--basetemp` as a pytest argument outside any work tree, pasted from
   `bash scripts/test_summary.sh` with the set id: `tests/test_jev_trim_compaction.py`, `tests/test_jev_trim_replay.py`
   and `tests/test_jev_pipes_replay.py`; rounds 1 and 2's outputs stay byte-identical (re-run and `sha256sum -c`).

## Report

Return the whole report as your final message (not a summary): the premise re-run; files with line counts and sha256;
the gates; the mutants; the pins; per run, item 3's table per N with the control and the excess, item 5's rates per bin,
item 6's table; a DISCREPANCIES list; and your self-attack. No recommendation.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin 0749fe5)

Printed by `bash scripts/premise_block.sh` from the main tree. Your round 2's landing and this brief are local at
dispatch (the push waits on CI), so the block measures the tree you work in. The boundary count is taken within your
round-2 pin of main (780,424,880 bytes), so it does not move as the session grows. Expected to differ: nothing.

```
$ git merge-base --is-ancestor 0749fe5 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git log -1 --format=%s -- scripts/jev_trim/replay.py
T0-REPLAY round 2 landed (task #346): the replay tool's round-2 grid, its tests and outputs; a record under D-106
$ sha256sum scripts/jev_trim/replay.py tests/test_jev_trim_replay.py tasks/briefs/jev-trim/k1_authoring_probe.py | cut -c1-16,65-
73a16e72ed933db5  scripts/jev_trim/replay.py
d17f19c859ed3727  tests/test_jev_trim_replay.py
a9bea1dbbd9c112a  tasks/briefs/jev-trim/k1_authoring_probe.py
$ ls scripts/jev_trim/compaction.py tests/test_jev_trim_compaction.py docs/research/findings/jev-trim/compaction-2026-09-29 2>&1 | cut -c1-90
ls: cannot access 'scripts/jev_trim/compaction.py': No such file or directory
ls: cannot access 'tests/test_jev_trim_compaction.py': No such file or directory
ls: cannot access 'docs/research/findings/jev-trim/compaction-2026-09-29': No such file or
$ head -c 780424880 /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl | grep -c '"subtype":"compact_boundary"'
138
$ grep -n '^### 10\.2 \|^- \*\*R-B\|^- \*\*R-C' docs/research/findings/jev-trim/D105-DESIGN-v1.md | cut -c1-60
251:### 10.2 Where to compact (task #352)
261:- **R-B, our own quality curve** (the replay tool; count
265:- **R-C, the loss at each compaction** (the replay tool)
$ bash scripts/pc_suite.sh set-id -- tests/test_jev_trim_replay.py tests/test_jev_pipes_replay.py | tail -1
2 files set=5365c5f240ce
$ rm -rf /tmp/k1-premise-bt; python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/k1-premise-bt tests/test_jev_trim_replay.py tests/test_jev_pipes_replay.py 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
110 passed
```
