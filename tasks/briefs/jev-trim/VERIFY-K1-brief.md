# VERIFY-K1: attack the compaction-loss measurements before the first live arm (task #352, D-106)

Written 2026-09-29 03:2xZ by the coordinator. Role: sandbox `adversarial-verifier`, model opus. Do NOT spawn subagents.
Return the WHOLE report as your final message (a report-file write is refused for subagents).

The change under test: K1 (T0-REPLAY round 3), landed GATED-PENDING-VERIFY: `scripts/jev_trim/compaction.py`,
`tests/test_jev_trim_compaction.py` and the 19 outputs under `docs/research/findings/jev-trim/compaction-2026-09-29/`.
The builder's account: `tasks/briefs/jev-trim/K1-COMPACTION-LOSS-report.md` (every claim a hypothesis; read its
DISCREPANCIES D1-D15 first). The contract: `tasks/briefs/jev-trim/K1-COMPACTION-LOSS-brief.md`. The reading built on it:
`docs/research/findings/jev-trim/D105-DESIGN-v1.md` §10.6.

Why it matters: §10.6 reads these numbers as "a compaction costs this session little re-fetching", and the first live
arm (the owner's 500k compaction point) rests partly on that. A count that misses re-fetches, or a control that inflates
the base rate, would make compacting look cheaper than it is.

## WHAT TO ATTACK (report every observation; no severity filter)

1. **Reproduce the headline numbers with your own reader**, never `compaction.py`: the 139 boundaries of main within its
   pin (`pins.json`), the kept start per boundary, the re-fetch calls per 100 requests after the 1M-class boundaries for
   N = 20 and N = 100, and the R-B tool-error rate per 100k of fill. A difference is a finding.
2. **The control** (the report's D3, D6: 27 points at segment middles). Build at least one other control (for example
   points at the same distance from the segment start as the post-boundary windows, or matched by fill) and report the
   excess under it. Is "no excess after the first 20 requests" robust to the control?
3. **Re-fetches the shapes miss.** For example: a grep or a `graft ask` for a symbol seen before the boundary, a Bash
   `cat`, `sed -n` or `head` of a file read before it, a repeated `git log` or `git show`. Count them after boundaries
   and at control points.
4. **The miss** (D4): split the missed tokens by class (paths, identifiers, numbers, hex); what share looks incidental?
   Does the miss per boundary predict the re-fetch count?
5. **The cost model:** check that 119 of 121 on main and the exact subagent counts are not tuned to the answer, and
   test the assumption that the growth per request does not depend on X.
6. **Mutation:** reproduce at least four of the 15 mutants as FAILED tests, and add a mutant for each clause no row
   covers.
7. **Python 3.11 and 3.12:** the outputs' byte identity (`/usr/bin/python3.12` exists; a scratch venv with pytest and
   pyyaml runs the tests).

## GATE

The blocking predicate of skill `contract-gate` (D-031) with D-034. One recommendation: MERGE-READY /
MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID, each blocking finding with its reproduction command. Say
separately whether §10.6's reading ("a compaction costs this session little re-fetching") stands.

## BOUNDARY AND STANDING RULES

- READ everything; WRITE only scratch under `/tmp/vk1/`, removed at the end. No git writes, no PC bridge, no outward
  action, no model or network call.
- Stream the transcripts; outputs carry counts, sizes, offsets, ids, tool, kind and rule names only; never read a
  thinking block's text; never read a secret source (`.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`,
  `~/.config/qwen-*`, `/root/.config/session-export/pseudonym.key`, GH_TOKEN, GITHUB_TOKEN).
- Another lane is live in this tree (`.lanes-live`): touch none of its files.
- `--basetemp` as a pytest argument outside any work tree, never through `PYTEST_ADDOPTS`; counts pasted from
  `scripts/test_summary.sh` with their set ids; stamps from `date -u`; cite commits by subject or origin id; write
  `S1-RATE <id> rel=<0-3> use=<0-3>` for any `[S1 ...]` injection.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin 975523a)

Printed by `bash scripts/premise_block.sh` from the main tree; K1's files and this brief are local at dispatch. Expected to differ: nothing.

```
$ git merge-base --is-ancestor 975523a HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ sha256sum scripts/jev_trim/compaction.py tests/test_jev_trim_compaction.py docs/research/findings/jev-trim/compaction-2026-09-29/SUMMARY.md docs/research/findings/jev-trim/compaction-2026-09-29/pins.json | cut -c1-16,65-
95e160625dd2cd10  scripts/jev_trim/compaction.py
fff6fb719740142e  tests/test_jev_trim_compaction.py
a77e0c3ff1261bde  docs/research/findings/jev-trim/compaction-2026-09-29/SUMMARY.md
bff43daab618cc47  docs/research/findings/jev-trim/compaction-2026-09-29/pins.json
$ ls docs/research/findings/jev-trim/compaction-2026-09-29 | wc -l
19
$ grep -n '^### 10\.6 ' docs/research/findings/jev-trim/D105-DESIGN-v1.md
341:### 10.6 K1: what our own compactions cost (2026-09-29)
$ bash scripts/pc_suite.sh set-id -- tests/test_jev_trim_compaction.py tests/test_jev_trim_replay.py tests/test_jev_pipes_replay.py | tail -1
3 files set=74199ac6b13a
$ rm -rf /tmp/vk1-premise-bt; python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/vk1-premise-bt tests/test_jev_trim_compaction.py tests/test_jev_trim_replay.py tests/test_jev_pipes_replay.py 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
141 passed
$ ls /tmp/vk1 2>&1 | head -1
ls: cannot access '/tmp/vk1': No such file or directory
```
