# JT1-R1 report: the one focused repair of the Jev client and the hiccup tracker (task #235; D-076; D-031)

Role: code-implementer (sandbox, Opus 5.5), shared tree, no worktree. Brief: `tasks/briefs/jev-laya/JT1-R1-brief.md`.
Contract: `tasks/briefs/jev-laya/JT1-brief.md` as amended by D-076. Evidence: `tasks/briefs/jev-laya/VERIFY-JT1-report.md`.
Started: Thu Sep 24 15:14:22 UTC 2026 (`date -u`). Written incrementally.

## 0. Premise re-measured (15:14Z)

```
$ git log --oneline -1
a95fe0a reports: VERIFY-JT1 (NOT-READY; cited by D-076 and issue #68) and JT3 (the builder report VERIFY-JT3 attacks) committed as records
$ for f in <the seven files>; do git rev-parse --short=12 HEAD:$f; git hash-object $f | cut -c1-12; done
e2d02c35ecc8 scripts/jev.py                 (HEAD and working tree)
91ff34e0d914 scripts/jev_local.sh           (HEAD and working tree)
b1eb74892575 scripts/hiccup_scan.py         (HEAD and working tree)
e70eb70948f4 scripts/hiccup_families.tsv    (HEAD and working tree)
9491dbc0f81c tests/test_jev_client.py       (HEAD and working tree)
e37a5a228cb0 tests/test_hiccup_scan.py      (HEAD and working tree)
45d4f7ebf6fc docs/HICCUPS.md                (HEAD and working tree)
$ bash scripts/test_summary.sh tests/test_jev_client.py tests/test_hiccup_scan.py --basetemp /tmp/jt1r1p/bt
pytest-exit: 0
pytest-summary: 77 passed in 21.47s
$ grep -n -E "^def (build_page|excerpt|_plain|...)|^def (scrub|_scrub|rank|_build|cmd_rank)" scripts/hiccup_scan.py scripts/jev.py
scripts/hiccup_scan.py:77:def excerpt(text):
scripts/hiccup_scan.py:354:def _plain(text):
scripts/hiccup_scan.py:519:def build_page(sc, source, jev=None):
scripts/jev.py:141:def _build(cmd, args, max_chars):
scripts/jev.py:454:def rank(query, chunks, instructions=RANK_INSTRUCTIONS, **opts):
```

All seven blobs match the brief's PREMISE block, the working tree equals HEAD for each, and 77 passed matches. HEAD moved
from the brief's ee44b41 to a95fe0a; none of the seven files changed. No mismatch: proceeding.

Environment facts that shape the tests: `.pc-bridge.env` EXISTS in the repo root (so a `--venue auto` call that misses
the local server would reach the real bridge: every test here pins `url=` / an injected runner, and the one `--jev` CLI
run uses `--jev-venue local` on a fixture whose clusters are all covered, asserted before the run). The Laya server on
127.0.0.1:47411 answers `/health` (revision 1c5edc17..., `calls` 198 at 15:2xZ). `.jev/intercept-off` exists; not touched.

## 1. Blast radius (GitNexus CLI, `impact --direction upstream`, 15:2xZ)

| symbol (uid) | risk | upstream |
|---|---|---|
| `scripts/hiccup_scan.py:excerpt` | LOW | 7 (all in hiccup_scan.py) |
| `scripts/hiccup_scan.py:_plain` | LOW | 3: render, build_page, main |
| `scripts/hiccup_scan.py:render` | LOW | 3: build_page, main, module |
| `scripts/hiccup_scan.py:build_page` | LOW | 2 |
| `scripts/hiccup_scan.py:main` | LOW | 1 |
| `scripts/jev.py:_build` / `_result` / `_prep` | LOW | 8 / 4 / 6, all inside jev.py |
| `scripts/jev.py:rank` | **HIGH** | 6: `jev_context.jev_rank` (JT2), `jev_locate.rank_chunks` + `main`, `jev_echo.main`, the jev-locate bench `run` + `main` |

WARNING (HIGH on `rank`): D-076 (b) changes what `rank` sends and when it refuses, for every consumer. Not in GitNexus
(untracked): `.claude/hooks/search-intercept.py` (JT3) also calls `jev.rank`. JT2's committed tests pin a 1,200-character
query (`tests/test_jev_context.py:425`) and JT2's own all-equal reason text (`:456`, `tests/test_jev_locate_echo.py:207`),
so D-076 (b) is expected to turn those red; section 6 runs them.

## 2. RED on the PIN code (new tests written first; scripts/jev.py and scripts/hiccup_scan.py still at e2d02c35ecc8 / b1eb74892575)

```
$ date -u; python3 -m pytest tests/test_jev_client.py tests/test_hiccup_scan.py -q -rs -p no:cacheprovider --basetemp /tmp/jt1r1/btred
Thu Sep 24 15:33:07 UTC 2026
15 failed, 78 passed in 23.88s                                                   pytest rc=1
failing (the 15):
  (b) test_rank_cuts_the_query_to_1000_and_each_chunk_to_2500_characters      query sent = the first 4,000 (the old cap), not 1,000
  (b) test_a_secret_straddling_the_window_cut_never_reaches_the_request[query-1000]   assert (1028 == 1000): no window cut
  (b) test_a_secret_straddling_the_window_cut_never_reaches_the_request[chunk-2500]   assert (2528 == 2500): no window cut
  (b) test_rank_refuses_a_signal_free_ranking_whose_scores_are_all_equal      {'fan_out': 3, 'ranking': [['c0', 0.4958], ['c1', 0.4958], ['c2', 0.4958]], ...} is None
  (a) test_page_rows_are_exact                                                 its row 5 now reads `... for sk-<redacted> password: <redacted>`
  (a) test_the_f16_shapes_leave_no_letter_of_the_value_on_the_page             password: -> assert 0 == 2 (the page shows the stub, not <redacted>)
  (a) test_excerpt_scrubs_the_raw_text_before_it_normalizes[password: ab1234cd]              + curl: server said password: abNcd then closed
  (a) test_excerpt_scrubs_the_raw_text_before_it_normalizes[Authorization: Bearer abc12345xyz] + ... Authorization: Bearer abcNxyz then closed
  (a) test_excerpt_scrubs_the_raw_text_before_it_normalizes[X-Agent-Token: zq12345678]      + ... X-Agent-Token: zqN then closed
  (a) test_excerpt_scrubs_the_raw_text_before_it_normalizes[sk-abcdef123456]                + ... sk-abcdefN then closed
  (a) test_excerpt_scrubs_the_raw_text_before_it_normalizes[xoxb-abc1234567]                + ... xoxb-abcN then closed
  (c) test_kcj1b_the_jev_page_minus_its_column_is_the_plain_page_near_the_cap   At index 1786 diff: b'5' != b'0' (the agents table)
  (c) test_kcj1b_holds_on_a_sweep_of_generated_over_cap_pages                  AssertionError: 0 (trial 0: strip(jev page) != plain page)
  (c) test_a_page_that_cannot_keep_the_column_room_is_refused_with_and_without_jev   build_page returned bytes (the plain page is written, the --jev page cannot be)
  (d) test_tool_model_and_agent_id_fields_pass_the_scrub                       | ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 | - | claude-opus-5-5 1 | ... on the page
passing controls among the new tests on the PIN: [api_key: qw12er34ty] (still redacted after normalizing: 8 left), and
test_excerpt_scrubs_again_after_it_normalizes (the PIN also scrubs after normalizing; it guards that second scrub).
```

The (c) CLI fixture is the verifier's F-18 fixture record for record (`write_kc_fixture`, from `/tmp/vjt1/kc_confirm.py`).
The pages the PIN wrote in that red run reproduce F-18 exactly:

```
PIN plain bytes=39924 agent_rows=181 not_shown=[]
PIN jev   bytes=39149 agent_rows=176 not_shown=['5 older agents active in the window are not shown (the page cap).']
```

## 3. The change (GREEN after; first green run 15:36:08Z: `93 passed in 34.83s`, pytest rc=0)

**(a) D-11 order** (`scripts/hiccup_scan.py` `excerpt`): `scrub(str(text))` first, on the raw text; then the character
hygiene (lone surrogates, control and separator characters to spaces) and the D-11 normalization (URLs, KEY=value, long
quoted strings, 20+ runs, numbers); then `scrub` again; then the 160 cut. Every excerpt path goes through it: error first
lines (`cluster_key`, both cluster tables), Agent descriptions (`Scan._user`), and the advisory column's failure reason
(`jev_column`). The second scrub is kept on purpose: it takes a head that only the hygiene reveals (a control character
between a name and its `=`), a shape the raw scrub cannot see (test `test_excerpt_scrubs_again_after_it_normalizes`).

**(d) F-17** (`_plain`): every plain table cell is `scrub`bed before its escapes: tool names (context cost, the clusters'
`tools` column), model names (served-model and agents tables), agent ids, and also the family, rule and advisory cells.
Interpretation (flagged): (d) says these fields "pass the same scrub", so they get `transcript_export.scrub`, NOT the D-11
normalization or the 160 cut. Normalizing them would merge distinct models on the page (`claude-opus-4-8` and
`claude-opus-5-5` would both read `claude-opus-N-N`) and turn 20+ character tool names (`mcp__github__get_job_logs`) into
`T`; the cut on tool names is F-20, which D-076 routes to a follow-up issue.

**(b) the rank window budget** (`scripts/jev.py`): `RANK_QUERY_CHARS = 1000`, `RANK_CHUNK_CHARS = 2500`; `_build` passes
`min(max_chars, budget)` to `_prep`, which scrubs and then cuts, so the order is scrub, then cut (AF-AP-127) and a smaller
`--max-chars` still wins. `_result` refuses a rank of two or more chunks whose scores are all equal at 4 decimals
(`round(x, 4)`), after the fan-out and per-answer checks: `Unavailable("signal-free rank: all N chunks scored X")`, so the
CLI exits 3 with one line and the import API returns None, like every other reply check. The cut keeps the HEAD of the
text, as the D-5 cap and D-11's "cut" do (see section 6 for JT2's tail window).

**(c) KC-J1b as bytes** (`build_page`, new `jev_room`, new `_jev_cell`). The rule: the agent trim is decided once, on the
page WITHOUT the column, against one budget = the cap (40,000) less `jev_room(sc)`, the most bytes the column can add to
this scan's page: its head and rule cells in both cluster tables (2 x 30 bytes) plus, per cluster row shown (top 25 + new
this week, at most 45), `' ' + cell + ' |'` with the printed cell cut to at most `JEV_CELL_BYTES = 100` bytes
(`_jev_cell`: scrub the whole text, then cut, then escape). The `--jev` page renders the same agents and adds only its
column, so it is the plain page plus at most `jev_room` bytes: under the cap by construction, and equal to the plain page
once the column is stripped. When even the page with no agent row cannot keep that room, `build_page` returns None and
`main` exits 2 for BOTH runs (`the page does not fit the 40000-byte cap with N bytes kept for the Jev column, even with
no agent row; nothing written`). The old `len(page) >= PAGE_MAX_BYTES` guard in `main` stays as a last guard; it is
unreachable while `jev_room` bounds the column (commented as such).

What the plain page shows that it did not before: (1) fewer agent rows, and the line `N older agents active in the window
are not shown (the page cap).`, once the plain page passes the cap less the column's room (35,305 bytes when 45 cluster
rows are shown; 39,528 on the verifier's fixture, which has 4); before, it trimmed only at 40,000. On the verifier's
fixture the plain page now shows 176 agents and the "5 older agents" line, exactly as the `--jev` page does. (2) An
advisory cell longer than 100 printed bytes is cut (a long `n/a (<reason>)`). (3) An input whose page cannot keep the
column's room even with no agent row is refused (exit 2) where the plain run used to write it; that needs about 35 KB of
non-agent content (for example F-20's giant tool name, which was refused before too). (4) Per (a) and (d): an error line's
provider-shaped key reads `sk-<redacted>` / `xox-<redacted>` (it read `T` or leaked a stub), a 40+ identifier run reads
`<opaque-redacted>` (it read `T`), and a tool, model or agent-id cell that holds a secret shape is redacted. The header
prose says the page keeps room for the column and that tool, model and agent names are scrubbed.

### The sweep's own numbers (the test body run with its assertions turned into counters, `/tmp/jt1r1/sweep_count.py`)

```
== PIN scanner (scratch tree /tmp/jt1r1/pinroot, hiccup_scan.py blob b1eb74892575)
seen {'inputs': 60, 'over_cap': 54, 'f18_edge': 24, 'trimmed': 17}
violations (kind 0 = no cell filled, 1 = short real cells, 2 = cells that grow when printed): [((0, 'bytes'), 6), ((1, 'bytes'), 13), ((2, 'bytes'), 18)] total 37
== new scanner
seen {'inputs': 60, 'over_cap': 59, 'f18_edge': 29, 'trimmed': 60}
violations (...): [] total 0
$ python3 -m pytest tests/test_hiccup_scan.py -k sweep   (PIN scratch tree)
E               AssertionError: (1, 1, 177)          At index 1889 diff: b'g' != b'a'           1 failed, 39 deselected
```

`f18_edge` = inputs whose page WITHOUT the column is under the cap while the page WITH it is over (F-18's own zone): each
trial binary-searches the most agents whose column-less page fits, then adds a well-over-cap input. The sweep takes 7.8 s:
every plain cell now passes `scrub` (4.4 us for a short cell), and a 300-agent render went from 1.3 ms to 6.1 ms.

## 4. Live checks against the Laya server on 127.0.0.1:47411 (never stopped; `--venue local`; logs to scratch)

```
$ date -u   -> Thu Sep 24 15:42:14 UTC 2026
query = 'pytest fails: FileNotFoundError for the --basetemp directory' + 3,874 characters of pytest error lines (3,934 in all)
chunks C1 'pytest creates only the last component of --basetemp; mkdir -p its parent first'
       C2 'a trailing & backgrounds the whole && list'   C3 'sqlite over the bridge: ship the SQL as a base64-decoded script file'
== PIN client (scratch copy of jev.py, blob e2d02c35ecc8), long query
{"cmd": "rank", "fan_out": 3, "latency_ms": 13376.6, "ranking": [["c0", 0.4773], ["c1", 0.4773], ["c2", 0.4773]], ...}   rc=0 wall=13.5s
== new client (repo scripts/jev.py), the same long query (sent: its first 1,000 characters)
{"cmd": "rank", "fan_out": 3, "latency_ms": 5215.4, "ranking": [["c0", 0.5271], ["c1", 0.4983], ["c2", 0.4922]], ...}   rc=0 wall=5.3s
== new client, the verifier's short query (positive control; the verifier measured 0.4902 / 0.179 / 0.1677)
{"cmd": "rank", "fan_out": 3, "latency_ms": 1120.4, "ranking": [["c0", 0.4902], ["c1", 0.179], ["c2", 0.1677]], ...}   rc=0 wall=1.2s
== new client, a dense 1,000-character query ('§¶ ' x 333): still ranks
{"cmd": "rank", "fan_out": 3, "latency_ms": 8969.7, "ranking": [["c1", 0.4827], ["c0", 0.4573], ["c2", 0.442]], ...}   rc=0
== the refusal path, live: two chunks with the same text (the server gives both the same state)
PIN client: {"cmd": "rank", "fan_out": 2, ..., "ranking": [["c0", 0.4902], ["c1", 0.4902]], ...}   rc=0
new client: jev: unavailable: local: signal-free rank: all 2 chunks scored 0.4902                   rc=3
new client log line: 2026-09-24T15:43:11.868631Z rank None False 2 dbab32dc4b21 local: signal-free rank: all 2 chunks scored 0.4902 no-answers   (file mode 600)
```

(b) holds live: the verifier's long-query rank now ranks with distinct scores (the right note first), and a tied answer
is refused with one line and rc 3. My long query is not byte-identical to the verifier's (its 3,874 characters of error
lines are not in its report); the PIN client ties on mine too (0.4773 x 3), so it has F-24's shape.

## 5. docs/HICCUPS.md regenerated with JT1's own command (live local Laya for the column)

```
$ python3 scripts/hiccup_scan.py --jev --jev-venue local --out docs/HICCUPS.md        (15:44:01Z, wall 25.1s)
hiccup_scan: files=245 bytes=1025342819 lines=208868 unparsable=18 assistant_usage_model=81418 tool_use=39264 tool_result=39254 errors=723 clusters=424 uncovered=18 task_reminder=1816 silent_turn_reminder=1118 compactions=122 refusal_stops=27 clock=2026-09-24T15:44:01Z page=docs/HICCUPS.md page_bytes=29295 sha256=a65ddf6a1531a9f77dd46730db5b39a820834ca3143b96123a06a8ca26958ded jev: uncovered_shown=5 filled=5 run_s=15.9
old page (HEAD): 27,917 bytes, sha256 dd993ed1d9ba...; new: 29,295 bytes. Both: scrub(page) == page, 0 redaction markers,
0 runs of 40+ identifier characters, 0 U+2028/U+2029 bytes. Advisory cells (live, the same five the verifier measured
at 13:4xZ): CLAUDE.md:420 0.5146, AF-AP-148, AF-AP-102 0.4222, AF-AP-104, AF-AP-58 0.2789.
```

Live KC-J1b on ONE frozen in-process scan (no copy of the 1.2 GB input: 1.5 GB of disk free), plain vs `--jev`, the
column's rank calls with `log=False`:

```
files=245 scan_s=8.5 jev_s=15.1 cells=5 filled=5
jev_room=4695 budget=35305 plain_bytes=28962 jev_bytes=29295 column_bytes=333
KC-J1b live: jev page minus its column == plain page: True
not-shown agent line on plain: False
```
The regenerated page's clock (15:44:01Z) is this session's own transcript, which grows while the scan runs: a second
run gives another page (D-8 holds for the same input BYTES; A6's frozen-set determinism is JT1's and the verifier's).

## 6. The other consumers of `jev.rank` (run as the brief asks; their files not edited)

JT2 (`tests/test_jev_context.py`, `tests/test_jev_locate_echo.py`), after the change (final jev.py, 16:02:03Z):

```
5 failed, 73 passed in 13.08s                                                              rc=1
  test_jev_context.py:425  test_jev_call_is_per_chunk_with_the_query_capped_to_its_tail   pins len(query) == 1200 (JEV_QUERY_CHARS); rank now sends 1,000
  test_jev_context.py:447  test_a_failed_batch_fails_the_whole_ranking                    its double answers a constant 0.5 per good batch: batch 1 (8 x 0.5000) is now
                                                                                          refused as signal-free before the HTTP 500 batch it pins ('call 2 of 3: url: HTTP 500')
  test_jev_context.py:456  test_all_equal_scores_are_no_ranking                           pins JT2's own reason; now 'call 1 of 1: url: signal-free rank: all 3 chunks scored 0.4958'
  test_jev_locate_echo.py:207  test_a_signal_free_jev_gives_the_base_pack_with_its_reason  the same reason text, one level up
  test_jev_locate_echo.py:283  test_from_file_reads_the_last_4000_characters            asserts the sent query ENDS with 'open_socket failed'
```

Cause isolated: scratch trees holding JT2's three scripts and two test files plus either jev.py, the five node ids only:
PIN jev.py (e2d02c35ecc8) `5 passed in 2.95s`; new jev.py `5 failed` (both runs pasted in the transcript; /tmp/jt1r1/jt2root-*).
All five come from D-076 (b), none from another change. The one that is more than a pinned constant or wording is `:283`:
JT2 deliberately sends the LAST 1,200 characters of its question (`jev_context.jev_query`, where an error message ends), and
rank's cut keeps the HEAD of what it gets, as the D-5 cap does, so JT2's queries now lose their last 200 characters. The fix
is in JT2's lane (`JEV_QUERY_CHARS = 1000`, then its tail survives whole; and the two reason-text pins). Head vs tail for
rank's own cut is a coordinator call if wanted; I kept the head (consistency with D-5's `[:max_chars]` and D-11's "cut").

JT3 (`.claude/hooks/search-intercept.py`, untracked, VERIFY-JT3 reading it): not run (its tests are that lane's). Static:
its query is one short sentence and its chunks are at most 20 hit lines of at most 220 characters, so no cut applies; if
Laya ever tied every shown hit, the hook now gets None and keeps file order with the refusal as its reason (its D-1).

The scanner's own consumer (`jev_column`, in my boundary, NOT changed): it "stops asking after a failure", so a
signal-free refusal for one UNCOVERED cluster would mark every later UNCOVERED row `n/a (<that cluster's reason>)` without
asking: a per-query answer read as an outage (AF-AP-191's class), and a cell that names a reason that was never measured
for its row. Exposure: its queries are 160-character keys and its 8 chunks distinct candidate texts of at most 300
characters, so no window cut; no tie seen live (5 of 5 filled at 15:44Z; the verifier's J2 cross-check: 0 of 100 tied).
Reported, not fixed: it is a change to D-10's stop rule, outside D-076's four items (see section 9).

## 7. Mutation audit (scratch copies only: `/tmp/jt1r1/mut`, one anchored replacement per mutant, anchor count asserted 1; final files, 15:57-16:01Z)

```
PRISTINE  rc=0 | 53 passed in 21.36s   (tests/test_jev_client.py)
PRISTINE  rc=0 | 41 passed in 10.78s   (tests/test_hiccup_scan.py)
A1  (a) revert the order (no raw scrub)           7 failed | test_page_rows_are_exact, test_the_f16_shapes_leave_no_letter_of_the_value_on_the_page, test_excerpt_scrubs_the_raw_text_before_it_normalizes[x5]
A2  (a) drop the second scrub                     1 failed | test_excerpt_scrubs_again_after_it_normalizes
B1  (b) drop the query cut                        2 failed | test_rank_cuts_the_query_to_1000_and_each_chunk_to_2500_characters, test_a_secret_straddling_the_window_cut_never_reaches_the_request[query-1000]
B2  (b) drop the chunk cut                        2 failed | test_rank_cuts_the_query_to_1000..., test_a_secret_straddling_the_window_cut...[chunk-2500]
B3  (b) drop the all-equal refusal                1 failed | test_rank_refuses_a_signal_free_ranking_whose_scores_are_all_equal
B4  (b) cut before the scrub (AF-AP-127)          4 failed | test_a_secret_straddling_the_cap...[named-token], [sk-key], test_a_secret_straddling_the_window_cut...[query-1000], [chunk-2500]
B5  (b) refuse a one-chunk rank too               4 failed | ...straddling_the_cap[named-token], [sk-key], test_rank_refuses_a_signal_free..., test_auto_falls_back_to_the_pc...
B6  (b) exact equality, not 4 decimals            1 failed | test_rank_refuses_a_signal_free_ranking_whose_scores_are_all_equal
C1  (c) trim the two pages separately (PIN body)  3 failed | test_kcj1b_the_jev_page_minus_its_column_is_the_plain_page_near_the_cap, test_kcj1b_holds_on_a_sweep..., test_a_page_that_cannot_keep_the_column_room...
C2  (c) one trim, but against the bare cap        3 failed | the same three
C3  (c) the advisory cell unbounded               1 failed | test_kcj1b_holds_on_a_sweep_of_generated_over_cap_pages
C4  (c) jev_room counts a 1-byte cell per row     1 failed | test_kcj1b_holds_on_a_sweep_of_generated_over_cap_pages
C5  (c) no symmetric refusal                      1 failed | test_a_page_that_cannot_keep_the_column_room_is_refused_with_and_without_jev
C6  (c) the advisory cell cut before its scrub    1 failed | test_an_advisory_cell_is_scrubbed_whole_before_it_is_cut
D1  (d) skip the scrub on tool names (cost table) 1 failed | test_tool_model_and_agent_id_fields_pass_the_scrub
D2  (d) skip the scrub in every plain cell        1 failed | test_tool_model_and_agent_id_fields_pass_the_scrub
16 of 16 killed; 0 survive.
```

The brief's five (revert the order = A1; drop the query cut = B1; drop the all-equal refusal = B3; trim the two pages
separately = C1; skip the scrub on tool names = D1) all die on a named test. A first pass (15:51Z) showed C1 surviving the
near-cap CLI test: the new header sentence (+199 bytes) had moved the verifier's exact fixture out of F-18's zone under the
new render (40,123 bytes untrimmed; 39,924 on the PIN). The test now positions its fixture for the scanner under test
(`write_kc_fixture_in_the_f18_zone`: n=181/pad=3 on the PIN, exactly the verifier's; n=180/pad=45 on the new render,
39,962 bytes) and kills C1.

## 8. Gates (final files)

```
$ for i in 1 2; do rm -rf /tmp/jt1r1/bt; bash scripts/test_summary.sh tests/test_jev_client.py tests/test_hiccup_scan.py --basetemp /tmp/jt1r1/bt; done
== gate run 1: Thu Sep 24 15:56:03 UTC 2026
pytest-exit: 0
pytest-summary: 94 passed in 31.49s
== gate run 2: Thu Sep 24 15:56:35 UTC 2026
pytest-exit: 0
pytest-summary: 94 passed in 31.93s
$ (the same final test files against the PIN scripts, scratch tree /tmp/jt1r1/pinroot, 16:01:31Z)
16 failed, 78 passed in 23.94s     (the 15 of section 2 plus test_an_advisory_cell_is_scrubbed_whole_before_it_is_cut)
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean                                     rc=0
$ python3 scripts/lint_delta.py --base HEAD
lint_delta (worktree vs HEAD): 6 .py changed, 0 NEW pyflakes hit(s), 0 removed   rc=0   (6 = mine 4 + another lane's 2)
$ python3 -m pyflakes scripts/jev.py scripts/hiccup_scan.py tests/test_jev_client.py tests/test_hiccup_scan.py   rc=0
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <each file I wrote>
0 scripts/jev.py | 0 scripts/hiccup_scan.py | 0 tests/test_jev_client.py | 0 tests/test_hiccup_scan.py | 0 docs/HICCUPS.md | 0 this report
$ grep -c -E 'jev|hiccup' scripts/gate_files.txt   -> 0
```
Count arithmetic: 94 = 77 (PIN) + 4 new in the client file (53 = 49 + 4) + 13 new in the scanner file (41 = 28 + 13).
GitNexus `detect-changes --scope all`: 8 files (2 are another lane's), 45 symbols, risk high (the `rank` consumers);
the affected flows are inside hiccup_scan (Main -> Scrub, Render -> Scrub).

## 9. Files and lines changed (working tree vs HEAD a95fe0a; nothing committed)

| file | +/- | final blob | where |
|---|---|---|---|
| `scripts/jev.py` | +15 -4 | 2d419d932bf6 | docstring 14-18, 29-30; `RANK_QUERY_CHARS`/`RANK_CHUNK_CHARS` 68-69; `_build` 171-172, 177; `_result` refusal 226-228 |
| `scripts/hiccup_scan.py` | +67 -26 | 8e9ca1210551 | docstring 13-26; `JEV_HEAD/JEV_RULE/JEV_CELL_BYTES` 69-70; `excerpt` 84-91; `_plain` 365-368; `_jev_cell` 371-377; `render` prose 425-429, heads 491-492/528-529, cells 506/535; `jev_room` 542-546; `build_page` 549-563; `main` 703-707 |
| `tests/test_jev_client.py` | +56 -0 | f562602c171e | the (b) section 339-394: tests at 344, 363, 376 |
| `tests/test_hiccup_scan.py` | +268 -2 | 3cdfa67de2d6 | imports `random`, `shutil`; row 5 of `test_page_rows_are_exact` 208-210; the (a) section 435-491, (c) 494-661, (d) 663-701 |
| `docs/HICCUPS.md` | +49 -42 | d8bd3df4b632 | regenerated only, by `python3 scripts/hiccup_scan.py --jev --jev-venue local --out docs/HICCUPS.md` |
| `tasks/briefs/jev-laya/JT1-R1-report.md` | new | - | this report |

## 10. Deviations (each flagged)

1. **(d) scope read as "scrub", not "excerpt".** Tool, model and agent-id cells get `transcript_export.scrub` only (no
   normalization, no 160 cut): normalizing would merge `claude-opus-4-8` and `claude-opus-5-5` into `claude-opus-N-N` and
   turn `mcp__github__get_job_logs` into `T`; the cut is F-20, routed to a follow-up by D-076. A 40+ character identifier
   in those cells now reads `<opaque-redacted>` (none on the live page today).
2. **One existing expected row changed:** `test_page_rows_are_exact` row 5 (`for T password:` -> `for sk-<redacted>
   password:`), the change D-076 (a) makes and the verifier's FIX-F16 probe predicted.
3. **The near-cap CLI fixture positions itself** (pads the first agent's description) instead of fixing pad=3: it is the
   verifier's exact fixture on the PIN (n=181, pad=3) and n=180, pad=45 under the new render. A fixed fixture stopped
   exercising F-18's zone under the new render (section 7, C1).
4. **`main`'s old over-cap guard kept** as a last guard, commented unreachable while `jev_room` bounds the column (C2 shows
   it still catches a budget bug: that mutant's `--jev` run exits 2).
5. **Tests beyond the brief's list:** the second-scrub guard, the advisory cell's scrub-then-cut, the symmetric refusal,
   and the 4-decimal and one-chunk edges of the refusal (each kills a mutant above).
6. **The live long query is not byte-identical to the verifier's** (its 3,874 characters of error lines are not in its
   report); the PIN client ties on mine (0.4773 x 3), so it has F-24's shape.
7. **The call-log side effect of regenerating the page:** JT1's command logs its 5 live rank calls to the shared
   `.jev/calls.jsonl`, as JT1's run did. My other live calls logged to scratch or `log=False`.

## 11. Adjacent findings (reported, not fixed)

- **ADJ-1 (from (b), in my boundary but outside D-076's items): `jev_column` reads a signal-free refusal as an outage**
  and stops asking (section 6). One-line fix for a later round: skip `down` when `jev.last_reason` holds `signal-free rank:`.
- **ADJ-2 JT2 must re-pin** `JEV_QUERY_CHARS` (1,200 > the new 1,000) and two reason-text assertions; its multi-batch
  ranking now fails whole when one batch ties (section 6).
- **ADJ-3 F-19 is NOT fixed.** Its own reproduction (20,000 letters) now takes 0.00 s only because the raw scrub replaces
  the run first (PIN 3.24 s); the class remains: 20,000 characters of `a.` take 1.30 s new, 1.16 s PIN (`_URL` rescans).
- **ADJ-4 render cost:** scrubbing every plain cell made a 300-agent render 6.1 ms (PIN 1.3 ms); the trim loop renders once
  per 5 agents dropped. Fine at today's 114 agents; a cache on `_plain` would remove it if a window ever holds thousands.
- **ADJ-5 the plain page trims earlier** (35,305 bytes with 45 cluster rows): the price of KC-J1b as bytes; today's live
  page is 28,962 bytes plain, so no trim yet.
- Bug-echo for F-16's class (a transform before the scrub) over the other `scrub(` call sites (`scripts/laya_ft/*`,
  `harness-ports/bin/*`): none collapses value characters before scrubbing (`laya_ft` masks class words and AP ids; the
  exporters scrub first). F-16/F-17/F-18's classes are not in the registry: `docs/INCIDENT-LOG.md` is outside my boundary.
  Candidate rows: "a normalization that shrinks a value runs before the scrubber sees it"; "an optional column whose page
  trims on its own size, so the invariant 'page minus column = plain page' breaks near a cap".

(Section 10 item 4, verified 16:0xZ: under mutant C2 the plain run writes 39,962 bytes, rc 0, and the `--jev` run prints
`hiccup_scan: the page is 40038 bytes, over the 40000-byte cap; nothing written`, rc 2.)

## 12. Self-attack: the three most likely ways this change is wrong

1. **KC-J1b holds only on the paths I thought of.** A page byte that depends on `jev` outside the two heads, two rules and
   the per-row cells would break "page minus column = plain page", and a cell longer than its room would push the `--jev`
   page over the cap. Ruled out by: reading `render` (those four places are the only `jev` uses); the strip oracle (the
   test file's own `_strip_jev_column`, which knows nothing of `build_page`) on 60 generated inputs with cells that grow
   when printed (entities, 4-byte UTF-8, pipes), on the verifier's fixture and on the live page; the independent size
   assertions; and mutants C1-C5 (one budget, the room, the cell bound, the refusal) all dying. Residual: a future `render`
   change that adds a `jev`-dependent line must also extend `jev_room`; the sweep would catch it only if its inputs reach it.
2. **The new order lets through something the old order caught.** The final text still passes the same final `scrub`;
   the change only adds a `scrub` before normalization, so a leak needs normalization to create, from already-scrubbed
   text, a value that the old order's final scrub caught when it came from the raw text. None found: the pre-existing
   secrets test (seven fakes) still passes, the verifier's six shapes pass, and the live page has 0 markers and
   `scrub(page) == page`. INFERRED, not exhaustive: I did not fuzz the transformation space. The scrub itself stays the
   limit: a value `transcript_export.scrub` does not recognize in the raw text (a named value under 8 characters, a
   secret split by an ANSI code between the name and the value) is not redacted, now said in the module docstring.
3. **(b) breaks what depends on `rank`.** It does, by design, for JT2 (5 tests; section 6, isolated to jev.py by the swap)
   and for the scanner's own stop rule (ADJ-1, not fixed). Two more consequences, inferred and not exercised: with
   `--venue auto`, a local signal-free answer is a failed reply check, so the walk goes on to the PC venue (a bridge round
   trip to the same model, which will likely tie too; D-076 kept every other fail-open rule, the walk included); and
   `round(x, 4)` compares the server's already-rounded scores, so its half-way float cases do not arise in practice (the
   test pins 0.49581 vs 0.49584 as equal and 0.4958 vs 0.4959 as a ranking). Live, the verifier's long query now ranks
   (distinct scores, the right note first) and a real tie is refused with rc 3.

Addendum to 12.2 (verified, new `excerpt`, fake values; `<ESC>` = chr(27)):
```
'curl: password:<ESC>[0m QZJ8x4z9k2m7 then'           -> 'curl: password: [Nm QZJNxNzNkNmN then'   (an ANSI code between the name and the value: leaks)
'curl: password: <ESC>[1mQZJ8x4z9k2m7<ESC>[0m then' -> 'curl: password: <redacted> then'        (ANSI codes around the value: redacted)
'curl: password: QZJ8x4z then'                        -> 'curl: password: QZJNxNz then'            (7 characters, under the floor of 8: leaks)
```
Both leaks are limits of `transcript_export.scrub`'s patterns (the old order leaked them too); like F-2 they belong to
the scrubber's owner. Neither is one of D-076's five shapes.

## 13. NOT done

- No commit, no push, no bridge call, no PC check, no third-party API, no subagent. `.jev/intercept-off` untouched; the
  Laya server on 47411 never stopped (its `/health` answered before and after).
- Not fixed, routed by D-076 to follow-up issues: F-2, F-4, F-5, F-12, F-13, F-19 (ADJ-3: its own repro is fast now only
  by the raw scrub; the class remains), F-20 (the cut on tool names), F-29. Also untouched: F-6, and F-34's stale prose in
  `scripts/jev_local.sh:9` (outside my boundary) and `scripts/jev.py:20,28` (F-6 and the gate screen, not changed by this
  repair). F-34's `hiccup_scan.py:13` and `:20` prose IS fixed (both sentences rewritten for (a), (c) and (d)).
- ADJ-1 (`jev_column` stops asking after a signal-free refusal) reported, not fixed.
- JT2's five red tests (section 6): not edited, by the brief; the coordinator routes them to JT2.
- JT3's `tests/test_search_intercept.py` not run (VERIFY-JT3's); static reading only.
- No registry rows or skill bakes: `docs/INCIDENT-LOG.md` and the skills are outside my boundary (candidate rows in 11).
- The live refusal was driven with two identical chunks; no 1,000-character query I tried filled the window (a dense
  `§¶ ` query still ranked), so the window-filling refusal is unit-tested only.
- The regenerated `docs/HICCUPS.md` reads this session's live transcripts: it is not reproducible byte for byte later.

## 14. Evidence tiers

- **Verified (commands and outputs above, this session):** the premise; RED on the PIN (15 of the first draft, 16 of the
  final tests) and GREEN (94 passed, twice, via `scripts/test_summary.sh`); the sweep counts on PIN vs new; the live rank
  checks and the live refusal; the regenerated page's stats and its live KC-J1b; the JT2 reds and their isolation to
  jev.py; the 16-mutant table with green controls; `no_laya_in_gates`, `lint_delta`, pyflakes and the separator checks;
  F-19's timing; the C2 guard behavior.
- **Inferred:** that `render` has no other `jev`-dependent bytes (read, plus the tests); that the new excerpt order is
  never weaker than the old (argument plus tests); that the PC venue sends the same cut request (the same `_build`; the
  injected-runner PC tests pass); the auto-walk consequence in 12.3.
- **Assumed:** the window numbers (1,024 tokens, a 256-token head) and the 1,000 / 2,500 budget are D-076's, not
  re-measured with the snapshot's tokenizer by me.

Tree note: `docs/08_DECISION_LOG.md` changed during this lane (a D-079 row, owner rulings on the Jev plan after simple-jev). Not mine, and it does not amend D-076 (it keeps Laya for short decisions, point 4). My tracked changes are the five files in section 9, plus this new report.

Finished: Thu Sep 24 16:05:41 UTC 2026 (`date -u`).
