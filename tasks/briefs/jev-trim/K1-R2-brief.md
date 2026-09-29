# K1 round 2 (T0-REPLAY round 4): the re-fetch shapes this session really uses, reads apart from writes, a sliding control, a position-aware cost model (task #352, D-106)

Written 2026-09-29 from 04:2xZ (clock read at 04:22:32Z) by the coordinator, for the original K1 builder, resumed. This
is ONE focused repair (D-031) and a contract amendment: VERIFY-K1 (`tasks/briefs/jev-trim/VERIFY-K1-report.md`, READ in
full) found your round faithful to its brief and the brief's shape list too narrow (its F3, a CONTRACT-DEFECT that is
the coordinator's, not yours). The disposition: MERGE-READY-WITH-FOLLOWUPS; F2, F3, F5, F7, F9 and F11's gap come back
to you here. F8 closes task #357 (holding a segment's last-request items moves nothing). Why it matters: R-C is the
score §10.3 plans for K2's file packs and for Jev (K6), so a score blind to Bash views would mis-score both, and the
design's §10.6 reading (now marked struck) rested on it.

## Boundary

- MODIFY: `scripts/jev_trim/compaction.py`, `tests/test_jev_trim_compaction.py`.
- CREATE: the round-2 outputs under `docs/research/findings/jev-trim/compaction-2026-09-29-r2/`, written by
  `compaction.py`, never by hand.
- READ, never modify: `scripts/jev_trim/replay.py`, `scripts/jev_pipes/`, `tests/test_jev_trim_replay.py` (its fixture
  builders), the round-1 outputs under `docs/research/findings/jev-trim/compaction-2026-09-29/` (they stay as they are),
  `docs/research/findings/jev-trim/D105-DESIGN-v1.md` §10.6.
- Another lane (K2) works beside you on `scripts/filepacks.py`, `scripts/codemap.py` and their tests: touch none of them.
- Same safety as your rounds 1 to 3: stream the transcripts; outputs carry counts, sizes, offsets, ids, tool, kind, shape
  and rule names only; a token set lives in memory and is never printed; never read a thinking block's text; read no
  secret or `*.env` file; no git writes, no PC bridge, no subagents, no outward action, no model or network call; start no
  process that outlives your run.

## Items (each with a test and a named mutant the test kills)

1. **Premise.** Re-run the PREMISE block below. On a difference, stop and report CONTRACT-INVALID.
2. **Red first.** Add the verifier's two red tests (its report, "Red tests and discriminator": R1
   `test_a_write_is_not_a_search`, R2 `test_a_bash_view_of_a_file_read_before_is_a_refetch`) to the test file as they
   are. Paste them failing on your round-3 code (`2 failed`), then passing on the final code.
3. **A shape set option.** `--shapes v1|v2`, default `v1`. Under `v1` every round-1 output stays byte-identical (item
   9). Under `v2` items 4 to 7 apply. Round 2's run uses `v2` and writes the new directory.
4. **Reads apart from writes (F2).** Classify each matched call's direction by the verifier's rules (its item 3): a read;
   a write (an edit tool; `scripts/anchor_edit.py`; `sed -i`, `tee`, `cp` or `mv` into the file; a redirect into a file
   other than `/dev/null`); a commit (`scripts/safe_commit.sh`, `scripts/push_clean.sh`, `git commit`, `git add`,
   `git push`); a script; other. Parse Bash with the shell rules your round-1 code uses for commands (heredoc bodies
   excluded). A `search_*` shape counts reads only; writes and commits are reported beside it, per shape, never in the
   re-fetch total.
5. **The shapes K1 could not see (F3).**
   - The strict set, added to the re-fetch total: (a) a Bash view (`cat`, `sed`, `head`, `tail`, `nl`, `less`, `awk`) of
     a file the pre segment Read, edited or viewed; (b) a Read of a file the pre segment viewed through Bash; (c) a
     `git log`, `git show`, `git diff` or `git blame` with the same non-flag arguments as one in the pre segment; (d) a
     Read of a known path spelled another way (absolute against relative, a `./` prefix).
   - The loose set, reported as its own total and never merged into the strict one: a grep (the Grep tool, `grep`, `rg`,
     `graft ask`) for a token seen before; any `git log`, `git show` or `git diff`.
   - Per label, the rate after a boundary and at the controls (the verifier's "By label" table is the shape to match).
6. **Windows and controls.** Add the window of requests 20 to 99. Beside your C1, add C2 (paired: the last 100 requests
   of each boundary's pre segment, the window's final outputs counted) and C5 (sliding: every 20 requests from request
   100, intervals resampled by segment). For each window and each control: the rate per 100 requests, the excess, and a
   95% bootstrap interval, seeded so two runs are byte-identical.
7. **A position-aware cost model (F5).** Beside the flat model, a variant whose growth per request depends on the
   position since the segment start (the verifier's: requests 0 to 19, 20 to 99, 100 and later), calibrated so it
   reproduces the observed count at 785k. For X in {300k, 400k, 500k, 600k, 700k, 785k}: the compactions, the mean fill,
   the cache reads, and both models' cache reads and writes against the session's actual usage records. The modeled
   loss per compaction takes item 5's corrected per-boundary counts.
8. **The small ones.** F9: the missed-path share is stated as measured (1.3% to 2.0% on main's 1M class at your round-1
   numbers), not "1% to 4%". F11's gap: a `--pin` beyond the file's size stops with a named error. F7: one fixture case
   per surviving clause the verifier lists (a `prompt_snapshot` in the R-C fixture; a `/tasks/…output` call; a relative
   path token; a path both read and edited; a boundary and a synthetic record in the R-B fixture; a negative step; the
   excess, postTokens and K asserted), and the mutation summary over your mutants plus its N01 to N22.
9. **Byte identity.** Under `--shapes v1`, the 19 round-1 files re-generate byte-identical (`sha256sum -c` against the
   committed files) under Python 3.11 and 3.12 (a scratch venv; the replay tool's pins are per Python family,
   AF-AP-238). Rounds 1 and 2 of the replay tool stay byte-identical too (its tests pin them).
10. **Gates**, each twice, `--basetemp` as a pytest ARGUMENT outside any work tree, pasted from
   `bash scripts/test_summary.sh` with the set id: `tests/test_jev_trim_compaction.py`, `tests/test_jev_trim_replay.py`,
   `tests/test_jev_pipes_replay.py`.

## Report

Return the whole report as your final message: the premise re-run; files with line counts and sha256; the red-first
run; per item its pasted evidence; §10.6's questions re-answered from the `v2` numbers (the first 20 requests, 20 to 99,
100, the rest, each against C1, C2 and C5, main and subagents apart); the cost-model rows, both models; the gates; the
mutants; a DISCREPANCIES list (every number that differs from VERIFY-K1's, with why); and your self-attack. No
recommendation.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin 3cd69de)

Printed by `bash scripts/premise_block.sh` from the main tree; `VERIFY-K1-report.md` is committed with this brief. Your
pins stay round 1's (`compaction-2026-09-29/pins.json`: main at 788,725,407 bytes, 16 subagent files), so round 2's
numbers compare with VERIFY-K1's. Expected to differ: nothing.

```
$ git merge-base --is-ancestor 3cd69de HEAD && echo 3cd69de-is-an-ancestor-of-HEAD
3cd69de-is-an-ancestor-of-HEAD
$ git log -1 --format=%s -- scripts/jev_trim/compaction.py
K1 landed (task #352; GATED-PENDING-VERIFY): what a compaction costs this session; the design's section 10.6
$ sha256sum scripts/jev_trim/compaction.py tests/test_jev_trim_compaction.py scripts/jev_trim/replay.py tasks/briefs/jev-trim/VERIFY-K1-report.md | cut -c1-16,65-
95e160625dd2cd10  scripts/jev_trim/compaction.py
fff6fb719740142e  tests/test_jev_trim_compaction.py
73a16e72ed933db5  scripts/jev_trim/replay.py
004df9ff8fd1980e  tasks/briefs/jev-trim/VERIFY-K1-report.md
$ ls docs/research/findings/jev-trim/compaction-2026-09-29 | wc -l
19
$ ls docs/research/findings/jev-trim/compaction-2026-09-29-r2 2>&1 | cut -c1-90
ls: cannot access 'docs/research/findings/jev-trim/compaction-2026-09-29-r2': No such file
$ grep -c '^def test_' tests/test_jev_trim_compaction.py
17
$ grep -n 'def test_a_write_is_not_a_search\|def test_a_bash_view_of_a_file_read_before_is_a_refetch' tasks/briefs/jev-trim/VERIFY-K1-report.md
423:def test_a_write_is_not_a_search(tmp_path):                 # R1 (F2): committed -> (4, 1)
438:def test_a_bash_view_of_a_file_read_before_is_a_refetch(tmp_path):   # R2 (F3, the amendment): committed -> 0
$ bash scripts/pc_suite.sh set-id -- tests/test_jev_trim_compaction.py tests/test_jev_trim_replay.py tests/test_jev_pipes_replay.py | tail -1
3 files set=74199ac6b13a
$ rm -rf /tmp/k1r2-premise-bt; python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/k1r2-premise-bt tests/test_jev_trim_compaction.py tests/test_jev_trim_replay.py tests/test_jev_pipes_replay.py 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'; rm -rf /tmp/k1r2-premise-bt
141 passed
```
