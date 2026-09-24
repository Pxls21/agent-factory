# VERIFY-JT1R1-JT2 report

Lane: VERIFY-JT1R1-JT2, sandbox adversarial-verifier. Model serving these turns: claude-opus-5-5 (the session's stated model; the
transcript is not readable from inside the lane, so the per-record mix is not measured here).
Brief: `tasks/briefs/jev-laya/VERIFY-JT1R1-JT2-brief.md` (committed in 0fa8960).

## 0. PREMISE re-measured (2026-09-24 16:15:55Z, local HEAD 0fa896074eb0)

All twelve blobs match the brief, at HEAD and in the working tree (`git hash-object`), and `git status --porcelain` is empty for
the twelve files and `docs/research/findings/jev-locate-bench/`. The one commit after the brief's db5df20 (0fa8960) adds only the
brief. Constants match: `scripts/jev.py:68 RANK_QUERY_CHARS = 1000`, `:69 RANK_CHUNK_CHARS = 2500`,
`scripts/jev_context.py:55 JEV_QUERY_CHARS = 1000`, `:77 DEFAULT_ORDER = "lexical"`. No mismatch: the verify proceeds.

```
2d419d932bf6 scripts/jev.py            f25e3219e9bd scripts/jev_context.py
91ff34e0d914 scripts/jev_local.sh      70720f113389 scripts/jev_locate.py
8e9ca1210551 scripts/hiccup_scan.py    79ab68f0ce63 scripts/jev_echo.py
e70eb70948f4 scripts/hiccup_families.tsv  60af25fa3823 tests/test_jev_context.py
f562602c171e tests/test_jev_client.py  b5a110aafe74 tests/test_jev_locate_echo.py
3cdfa67de2d6 tests/test_hiccup_scan.py
d8bd3df4b632 docs/HICCUPS.md
```

Other lanes' dirty files at start (not touched by this lane): `.claude/settings.json`, `scripts/install_session_hooks.py`,
`tests/test_session_hooks.py`, `.claude/hooks/search-intercept.py`, `tests/test_search_intercept.py`, `scripts/laya_ft/`,
`tests/test_laya_ft.py`, `docs/research/findings/j2b-variants/openjev/`, two report files.

## 1. Contracts read

JT1-R1: `JT1-brief.md` D-1..D-12 / A1..A8, amended by D-076 (a)-(d) (`docs/08_DECISION_LOG.md:87`), `JT1-R1-brief.md`;
evidence `JT1-R1-report.md`, `VERIFY-JT1-report.md` (F-16, F-17, F-18, F-24). JT2: `JT2-brief.md` D-1..D-7 / A1..A6, D-077
(`docs/08_DECISION_LOG.md:88`); evidence `JT2-report.md`, `docs/research/findings/jev-locate-bench/`. The landing commits:
6b171fb (JT2) and e0d2bdc (JT1-R1 plus the coordinator's JT2 alignment: `JEV_QUERY_CHARS` 1200 -> 1000 and four test pins).
Disk note: the coordinator reported the disk full until about 16:20Z. My writes before then (this report's skeleton, a
tokenizer copy) were re-checked after the note: complete (`cmp` identical, report tail intact). Scratch stays under
`/tmp/vjt12` (a few MB; no full-tree copies).

## 2. Laya's window, measured with its own code (D-076 (b))

Instrument: laya's own `build_sequence` and `_fix_tokenizer_config` (`/root/venv-laya-probe`), on a dereferenced scratch copy of
the snapshot's `tokenizer/` (`cmp`-identical to the snapshot; the snapshot is never written), the snapshot's
`rl_agent_config.json` (max_len 1024, head_max_len 256). The state is exactly the server's per-chunk state
(`laya_systemone_server.py:130-144`: `{"query": q, "chunk": text}`, serialized with `ensure_ascii=False`, cut from the right,
`laya/common.py:82-84`), where q and text are what `jev.py` sends (`_prep`: scrub, then the 1,000 / 2,500 cuts). Scripts:
`/tmp/vjt12/window.py`, `/tmp/vjt12/window_cases.py`.

```
{"max_len": 1024, "head_max_len": 256, "head_len": 36, "room": 987, "tokenizer": "TokenizersBackend", "vocab": 50280}
query(1,000 ch)  chunk      clen | q_tok  c_tok   vis  state  room  whole
prose            prose       400 |   309    128   128    438   987  True
prose            prose      2500 |   309    744   678   1054   987  False
code             code       2500 |   383    816   604   1283   987  False
trace            trace      2500 |   435    846   552   1453   987  False
zh               any         400 |  1379    128     0   1508   987  False
ja               any         400 |  1010    128     0   1139   987  False
hi               any         400 |  1039    128     0   1168   987  False
ru               prose      2500 |   514    744   473   1259   987  False
ansi (ESC codes) prose      2500 |   765    744   222   1510   987  False
json (quotes)    prose      2500 |   660    744   327   1405   987  False
short query      zh         2500 |    24   3426   963   3451   987  False
short query      ansi       2500 |    24   1154   963   1902   987  False
```

(full table: 98 rows, `/tmp/vjt12/window_rows.json`; every 400-character chunk is whole for the Latin, Cyrillic, Arabic,
emoji, ANSI, JSON, hex and number queries.) Readings: (1) the client's own maxima do not fit the window for ANY shape, even
English prose (1,054 state tokens against 987): a 2,500-character chunk loses its tail behind a 1,000-character query;
(2) a 1,000-character query in Chinese, Japanese or Hindi fills the window alone, so every chunk is cut away whole, every
state is identical, and the all-equal refusal is the only thing that stands between the caller and a hollow ranking;
(3) between those, the model sees only a chunk's head. See F-08 and F-09 (section 11) for what reaches the caller.

## 3. Gates, re-run fresh (16:26-16:28Z)

```
$ for i in 1 2; do rm -rf /tmp/vjt12/g/bt; bash scripts/test_summary.sh tests/test_jev_client.py tests/test_hiccup_scan.py --basetemp /tmp/vjt12/g/bt; done
== JT1-R1 pair run 1: Thu Sep 24 16:26:15 UTC 2026
pytest-exit: 0
pytest-summary: 94 passed in 33.35s
== JT1-R1 pair run 2: Thu Sep 24 16:26:49 UTC 2026
pytest-exit: 0
pytest-summary: 94 passed in 32.20s
$ (the same for tests/test_jev_context.py tests/test_jev_locate_echo.py)
== JT2 pair run 1: Thu Sep 24 16:27:22 UTC 2026
pytest-exit: 0
pytest-summary: 78 passed in 12.58s
== JT2 pair run 2: Thu Sep 24 16:27:34 UTC 2026
pytest-exit: 0
pytest-summary: 78 passed in 12.24s
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean          rc=0
$ python3 -m pyflakes <the 5 scripts, the 4 test files, bench.py>        rc=0
$ bash -n scripts/jev_local.sh                                             rc=0
$ python3 scripts/lint_delta.py --base HEAD
lint_delta (worktree vs HEAD): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed     rc=0   (the 2 are another lane's files)
$ grep -c -E 'jev|hiccup' scripts/gate_files.txt
0
```

94 + 78 = 172, the landing commit's `lane_gate.sh` RESULT (`172 passed` twice). Gate-file question: the screen's gate set
is `scripts/hooks/*`, the workflows, `proofs/*/check_*.py` and the 40 listed files (`no_laya_in_gates.py:1265-1297`); a
grep over `scripts/ .github/ harness-ports/ .claude/hooks/` for the five modules' names finds only JT3's untracked
`.claude/hooks/search-intercept.py` (a hook, not a listed gate) and FT1's `scripts/laya_ft/common.py` (a docstring
mention). No gate file imports or runs these files.

## 4. Red-green, reproduced (scratch trees, 16:28Z)

Two small scratch trees with the CURRENT test files and the files they read (`/tmp/vjt12/pin`, `/tmp/vjt12/new`): one with
the PIN scripts from 764e516 (`jev.py` e2d02c35ecc8, `hiccup_scan.py` b1eb74892575), one with the landed scripts
(2d419d932bf6, 8e9ca1210551).

```
== pin: 16 failed, 78 passed in 25.64s
FAILED test_jev_client.py::test_rank_cuts_the_query_to_1000_and_each_chunk_to_2500_characters
FAILED test_jev_client.py::test_a_secret_straddling_the_window_cut_never_reaches_the_request[query-1000] / [chunk-2500]
FAILED test_jev_client.py::test_rank_refuses_a_signal_free_ranking_whose_scores_are_all_equal
FAILED test_hiccup_scan.py::test_page_rows_are_exact
FAILED test_hiccup_scan.py::test_the_f16_shapes_leave_no_letter_of_the_value_on_the_page
FAILED test_hiccup_scan.py::test_excerpt_scrubs_the_raw_text_before_it_normalizes[x5 shapes]
FAILED test_hiccup_scan.py::test_kcj1b_the_jev_page_minus_its_column_is_the_plain_page_near_the_cap
FAILED test_hiccup_scan.py::test_kcj1b_holds_on_a_sweep_of_generated_over_cap_pages
FAILED test_hiccup_scan.py::test_an_advisory_cell_is_scrubbed_whole_before_it_is_cut
FAILED test_hiccup_scan.py::test_a_page_that_cannot_keep_the_column_room_is_refused_with_and_without_jev
FAILED test_hiccup_scan.py::test_tool_model_and_agent_id_fields_pass_the_scrub
== new: 94 passed in 36.14s
```

The lane's claim ("16 failed, 78 passed" on the PIN scripts, 94 green after) holds exactly.

## 5. D-076 (a) and (d): the excerpt order and the plain cells (16:30-16:40Z)

Harnesses (fake values only): `/tmp/vjt12/attack_excerpt.py` (the landed and the PIN `excerpt()` from the two scratch trees,
in process), `/tmp/vjt12/attack_excerpt2.py` (shapes the lane did not sweep), `/tmp/vjt12/fx.py` (transcript fixtures in the
real record shapes) and `/tmp/vjt12/attack_page_rows.py` (the REPO's `scripts/hiccup_scan.py` CLI, `--out` to scratch, no
`--jev`; each case carries a unique letter marker, and a leak is a 3-letter piece of THAT case's value in ITS rows).

The five F-16 shapes, every value length 8-19, four compositions (letters, mixed, digits first, dashed), in process:

```
password:              cases=48  leak(landed)=0  leak(PIN)=5  landed-leaking lengths=[]
Authorization: Bearer  cases=48  leak(landed)=0  leak(PIN)=5  landed-leaking lengths=[]
X-Agent-Token:         cases=48  leak(landed)=0  leak(PIN)=5  landed-leaking lengths=[]
sk-                    cases=48  leak(landed)=16  leak(PIN)=21  landed-leaking lengths=[8, 9, 10, 11]
xox                    cases=48  leak(landed)=8  leak(PIN)=13  landed-leaking lengths=[8, 9]
   e.g. sk- value 8 letters: 'curl: server said sk-QZJxkmrt then closed'
   e.g. xox value 8 letters: 'curl: server said xoxb-QZJxkmrt then closed'
```

Through the CLI, row-attributed (each case appears in 3 rows: the agents table, the top-25 and the new-this-week tables):

```
rc 0 page bytes 6688
password: 8                  rows=3 leaked pieces=0  | ag00xx | `mkqbb lane password: <redacted>` | ...
Bearer 8                     rows=3 leaked pieces=0  | ag01xx | `mkqbc lane Authorization: Bearer <redacted>` | ...
X-Agent-Token: 8             rows=3 leaked pieces=0  | ag02xx | `mkqbd lane X-Agent-Token: <redacted>` | ...
password: 19                 rows=3 leaked pieces=0  | ag03xx | `mkqbf lane password: <redacted>` | ...
sk- 12 (floor)               rows=3 leaked pieces=0  | ag04xx | `mkqbg lane sk-<redacted>` | ...
xox 10 (floor)               rows=3 leaked pieces=0  | ag05xx | `mkqbh lane xox-<redacted>` | ...
sk- 8 (under floor)          rows=3 leaked pieces=6  | ag06xx | `mkqbj lane sk-PTHwZsqc` | ...
xox 9 (under floor)          rows=3 leaked pieces=7  | ag07xx | `mkqbk lane xoxb-mXzGKrjNc` | ...
split run sk- (prefix)       rows=3 leaked pieces=6  | ag08xx | `mkqcb lane MqjDGvwb-sk-<redacted>` | ...
ANSI (lane's)                rows=3 leaked pieces=10 | ag09xx | `mkqcc lane password: [Nm cdzqxnGHWpGF` | ...
tool cell: password:         rows=12 leaked pieces=0
model cell: token=           rows=1 leaked pieces=0  | 2026-09-21 | claude-opus-5-5 33 · claude token=&lt;redacted&gt; 1 |
agent-id cell: AGENT_TOKEN=  rows=1 leaked pieces=0  | AGENT_TOKEN=&lt;redacted&gt; | - | claude-opus-5-5 1 | ...
```

Shapes the lane did not sweep, in process (landed vs PIN):

```
shape                                            landed     PIN        landed excerpt
zero-width space inside the name                 LEAK       LEAK       'curl: pass​word: QZJxkmrtwvXqpLbc then'
Cyrillic a inside the name                       LEAK       LEAK       'curl: pаssword: QZJxkmrtwvXqpLbc then'
lower-case bearer after Authorization:           LEAK       LEAK       'curl: Authorization: bearer QZJxkmrtwvXqpLbc then'
bare lower-case bearer                           LEAK       LEAK       'curl: header bearer QZJxkmrtwvXqpLbc then'
quote then space before the value                LEAK       LEAK       "curl: password: ' QZJxkmrtwvXqpLbc' then"
value split by a comma                           LEAK       LEAK       'curl: password: <redacted>,wvXqpLbcQZJx then'
value split by a semicolon                       LEAK       LEAK       'curl: password: <redacted>;wvXqpLbcQZJx then'
NBSP inside the value                            LEAK       LEAK       'curl: password: QZJx\xa0kmrtwvXqpLbc then'
C1 CSI between name and value                    LEAK       LEAK       'curl: password:\x9bNm QZJxkmrtwvXqpLbc then'
a CLI flag value                                 LEAK       LEAK       'mysql -u root -pQZJxkmrtwvXqpLbc then'
split run: prefix glued to an sk- key            LEAK       hidden     'curl: QZJxkmrt-sk-<redacted> then'       PIN: 'curl: T then'
split run: prefix glued to a ghp_ key            LEAK       hidden     'curl: QZJxkmrt-gh<redacted> then'        PIN: 'curl: T then'
split run: 30-char token with an in-run xox key  LEAK       hidden     'curl: wvXqpLbc-xox-<redacted> then'      PIN: 'curl: T then'
named value in JSON quotes                       hidden     hidden     'curl: {"password": "<redacted>"} then'
an Exit code line then a named value             hidden     hidden     'Exit code N :: password: <redacted>'
```

(d) hygiene, through the CLI (`/tmp/vjt12/attack_page_secrets.py`): a tool name `Bash\n| forged | row |` puts a line
break inside the cluster, context-cost and new-this-week rows (the page gains lines `\| forged \| row \| |`; the pipes are
escaped, so no row is forged, but the table breaks), and a tool name `Ba<ESC>[31msh` puts 3 raw ESC bytes on the page:
`_plain` scrubs these cells but, unlike `excerpt`, never replaces control characters.

## 6. D-076 (b): the window budget and the refusal, live (16:33-16:39Z; the real server on 127.0.0.1:47411, never stopped)

Every call: the repo's `scripts/jev.py`, `--venue local`, `--log-file /tmp/vjt12/calls.jsonl` (the shared `.jev/calls.jsonl`
gets no line from me), `--bridge-env /tmp/vjt12/none.env` (a nonexistent file: no bridge call is possible).

Genuine ties among DISTINCT chunks (the brief's "two irrelevant chunks that both score 0.0100"):

```
Q='pytest fails: FileNotFoundError for the --basetemp directory'
[the weather is sunny today] vs [a recipe for bread with flour]  rc=0  [["c1", 0.1221], ["c0", 0.0967]]
[zzzz] vs [qqqq]                                                   rc=0  [["c1", 0.235], ["c0", 0.2036]]
[a] vs [b]                                                         rc=0  [["c1", 0.3906], ["c0", 0.3849]]
[lorem ipsum dolor sit amet] vs [consectetur adipiscing elit]      rc=0  [["c1", 0.1516], ["c0", 0.1086]]
[x] vs [x ]                                                        rc=0  [["c0", 0.3307], ["c1", 0.2722]]
```

No distinct pair tied at 4 decimals; an all-equal answer comes from identical visible states (the same text twice, or every
chunk cut away). The refusal therefore fires on duplicates too (the lane's live refusal was two identical chunks); D-076 (b)'s
letter ("all equal ... two or more chunks") covers that, and a duplicate pair carries no order either way.

The window-filling query that stays INSIDE the 1,000-character cut (calibrated with `window.py`: an English lead plus Chinese
text; `/tmp/vjt12/q_partial.txt`):

```
Thu Sep 24 16:35:21 UTC 2026
chunks C1 'pytest creates only the last component of --basetemp; mkdir -p its parent first'
       C2 'a trailing & backgrounds the whole && list'   C3 'sqlite over the bridge: ship the SQL as a base64-decoded script file'
== A short query (reference)
{"cmd": "rank", "fan_out": 3, ..., "ranking": [["c0", 0.4811], ["c1", 0.1836], ["c2", 0.1825]], ...}   rc=0
== B 760-char query, 4 chunk tokens visible ("pytest creates" / "a trailing & backgrounds" / "sqlite over the")
{"cmd": "rank", "fan_out": 3, "latency_ms": 30039.9, "ranking": [["c0", 0.5079], ["c1", 0.4994], ["c2", 0.49]], ...}   rc=0
== B' the same query, chunks = their 4 visible tokens only
{"cmd": "rank", "fan_out": 3, "latency_ms": 39810.2, "ranking": [["c0", 0.5079], ["c1", 0.4994], ["c2", 0.49]], ...}   rc=0
== C 762-char query, 1 chunk token visible
{"cmd": "rank", "fan_out": 3, "latency_ms": 31306.2, "ranking": [["c0", 0.5079], ["c2", 0.5075], ["c1", 0.5011]], ...}  rc=0
== D 763-char query, 0 chunk tokens visible
jev: unavailable: local: signal-free rank: all 3 chunks scored 0.5070
rc=3
```

B equals B' to the fourth decimal: the ranking `rank` returns with rc 0 and `fan_out` 3 is the ranking of each chunk's first
4 tokens. C ranks on ONE token per chunk (and reorders c1/c2). Only D, the zero-token case, is refused: the refusal works live
(the lane had it unit-tested only), and it is the only guard. The exit-3 line and `None`:

```
auto: result None | last_reason local: signal-free rank: all 2 chunks scored 0.4902; pc: signal-free rank: all 2 chunks scored 0.4902 | runner calls [{'url': 'http://127.0.0.1:9/fake', 'cmd_len': 871, 'token_is_fake': True}]
local: result None | last_reason local: signal-free rank: all 2 chunks scored 0.4902 | runner calls 0
pc (injected): result None | last_reason pc: signal-free rank: all 2 chunks scored 0.4902 | runner calls 1
```

(the import API, two identical chunks, the REAL local server, an injected runner and a FAKE bridge env file.) `None` on every
path; with `--venue auto`, the default of the CLI, the import API and the scanner's `--jev-venue`, a signal-free LOCAL answer
walks on to the PC venue: one bridge round trip for an answer that depends on the input, not the venue.

### ADJ-1 through the scanner's CLI and the real server (16:39Z)

A byte-identical scratch copy of the landed scanner and client (`cmp` clean) under `/tmp/vjt12/adj1`, a fixture registry
where UNCOVERED cluster 1's lexical pool is two rows with the same title and cluster 2's pool is three distinct rows:

```
server calls before: 230
hiccup_scan: files=1 ... errors=3 clusters=2 uncovered=2 ... jev: uncovered_shown=2 filled=0 run_s=1.5      rc=0
server calls after: 231
46:| 1 | `flurble wibble crash in the frobnicator` | UNCOVERED | - | 2 | ... | Bash | n/a (local: signal-free rank: all N chunks scored N.N) |
47:| 2 | `zonked grommet failure while loading` | UNCOVERED | - | 1 | ... | Bash | n/a (local: signal-free rank: all N chunks scored N.N) |
scratch call log lines: 1
False local: signal-free rank: all 2 chunks scored 0.5076
```

One model call; row 2 was never asked and prints row 1's reason. Exposure today (the repo's real candidates, in process):
`candidates 206 distinct texts 205 texts shared by 2+ ids 1` (`CLAUDE.md:335` and `CLAUDE.md:335#2`, two markers in one
sentence) and `live UNCOVERED keys on the page: 6 | pools made of one repeated text: 0`.

## 7. D-076 (c): KC-J1b as bytes, and what the plain page lost (16:40-16:50Z)

In process, the landed `build_page` on generated scans (`/tmp/vjt12/attack_kc.py`), with generators the lane's sweep did not use:
agents OUTSIDE the 7-day window (they feed `build_page`'s `left` counter and never render), 0/1/10/25/30 old clusters plus
0/3/20/25 new ones (past NEW_ROWS), 1-200 models, 60-300 character tool names, 4-byte UTF-8 in descriptions, and cells that
grow when printed (`<&>|` runs, emoji plus `é`, empty, 300+ characters, a key that is not shown). Oracle, independent of
`build_page`: the two pages have the same lines except exactly 2 head lines, 2 rule lines and one line per shown cluster row,
each the plain line plus one suffix (the head suffix, the rule suffix, or ` <cell> |` without a newline); both under 40,000
bytes; each page built twice, byte-identical.

```
$ python3 attack_kc.py 60 11
{'trials': 60, 'over_budget_untrimmed': 17, 'trimmed': 38, 'none_both': 0, 'violations': 0, 'max_s': 16.997259536001366}
$ python3 attack_kc.py 80 23         (the trim counter fixed to the "older agents" line; out-of-window agents 0-500)
{'trials': 80, 'over_budget_untrimmed': 22, 'trimmed': 22, 'none_both': 0, 'violations': 0, 'max_s': 1.9765902399958577}
```

Through the CLI (the repo's scanner, plain vs `--jev --jev-venue local`, over-cap fixtures with 180-400 agents and 3-45 cluster
rows; the column filled LIVE by the real server, 35 cells):

```
0 rc 0 0 plain 35210 jev 36125 rows 45 model calls 35 hidden-line plain/jev True True oracle: OK | ... | jev note: uncovered_shown=35 filled=35 run_s=80.4
1 rc 0 0 plain 34591 jev 35506 rows 45 model calls 35 hidden-line plain/jev True True oracle: OK | ... | jev note: uncovered_shown=35 filled=35 run_s=78.5
2 rc 0 0 plain 33833 jev 33950 rows 3 model calls 3 hidden-line plain/jev False False oracle: OK | ... | jev note: uncovered_shown=3 filled=3 run_s=6.3
```

A side effect I own: my fixture's keys shared the word "failure" with registry rows, so these three runs made 73 real rank
calls, and the repo's scanner logs by default: 73 lines in the shared, gitignored `.jev/calls.jsonl`, 2026-09-24T16:45:26Z to
16:48:11Z, all synthetic keys (`qqzx <9 letters> vvkz failure`). Not deleted (a shared file); drop that window if the log
becomes labels (D-6). Every later `--jev` run of mine used a scratch copy whose `.jev/` is scratch.

ADJ-5, through both CLIs (no `--jev`) on the same over-cap fixtures:

```
/tmp/vjt12/kccli0 PIN (rc, bytes, agent rows, hidden): (0, 39494, 195, '35') | landed: (0, 35210, 170, '60')
/tmp/vjt12/kccli1 PIN (rc, bytes, agent rows, hidden): (0, 39459, 190, '210') | landed: (0, 34591, 160, '240')
```

The trim loop's cost (in process; `left` counts every agent with a timestamp, the window's or not):

```
in-window 250, out-of-window    0: renders=11 build_page=0.04s page=35196 bytes hidden-line=True
in-window 250, out-of-window 1000: renders=211 build_page=0.87s page=35199 bytes hidden-line=True
in-window 250, out-of-window 3000: renders=611 build_page=2.76s page=35199 bytes hidden-line=True
```

(d)'s scrub and long tool names: a fixture with 45 tool names of 560+ identifier characters gave the PIN page 36,882 bytes and
the landed page 6,561 (every such name reads `&lt;opaque-redacted&gt;`, the 40+ run rule). In the live transcripts (247 files)
three tool names are 40+ characters: `mcp__Claude_Code_Remote__register_repo_root` (1 call),
`mcp__codebase-memory-mcp__index_repository` (2), `mcp__Claude_Code_Remote__read_documentation` (1); the committed page shows
none of them today (`grep -c opaque-redacted docs/HICCUPS.md` = 0).

## 8. JT1-R1 mutation audit, new mutants (16:50-16:56Z; `/tmp/vjt12/mutate.py`, a fresh scratch copy per mutant, one
anchored replacement asserted unique, the module compiled; the tracked tree is never touched)

```
b1 refusal at 3 decimals                             KILLED    rc=1 1 failed, 52 passed | test_rank_refuses_a_signal_free_ranking_whose_scores_are_all_equal
b2 refusal only from 3 chunks                        KILLED    rc=1 1 failed, 52 passed | test_rank_refuses_a_signal_free_ranking_whose_scores_are_all_equal
b3 query cut keeps the tail                          KILLED    rc=1 1 failed, 52 passed | test_rank_cuts_the_query_to_1000_and_each_chunk_to_2500_characters
b4 the two budgets swapped                           KILLED    rc=1 3 failed, 50 passed | ...window_cut...[chunk-2500], [query-1000], test_rank_cuts_the_query...
b5 refusal on confidence, not noul                   SURVIVES  rc=0 53 passed in 21.08s
b6 refusal looks at the first two chunks only        SURVIVES  rc=0 53 passed in 22.10s
a2 excerpt cut before its second scrub               SURVIVES  rc=0 41 passed in 10.65s
a4 run rule at 21                                    KILLED    rc=1 3 failed, 38 passed | test_fixture_counts_are_exact, test_page_rows_are_exact, ...
c1 jev_room forgets the new rows                     SURVIVES  rc=0 41 passed in 9.95s
c2 jev_room one byte short per row                   SURVIVES  rc=0 41 passed in 10.63s
c4 trim loop > not >=                                SURVIVES  rc=0 41 passed in 10.41s
c6 jev page re-trimmed on its own size               SURVIVES  rc=0 41 passed in 10.48s     (equivalent while jev_room is right)
d1 agents-table model names unscrubbed               KILLED    rc=1 1 failed, 40 passed | test_tool_model_and_agent_id_fields_pass_the_scrub
d3 _plain without the scrub for agent ids only       KILLED    rc=1 1 failed, 40 passed | test_tool_model_and_agent_id_fields_pass_the_scrub
```

Each survivor, checked for a behavior change (the production code is right in every case; these are test gaps):
- c1 changes behavior: my independent KC-J1b harness kills it (`VIOLATION 19 {'n_in': 250, 'n_out': 0, 'n_top': 30, 'n_new': 20, ...}
  over the cap: 37152 / 40074`, 1 of 40 trials); the lane's sweep never fills 20 new-this-week rows with full cells near the
  budget. c2 survives my harness too (40 trials, 0 violations): it needs 100-byte cells at the budget's edge.
- a2 changes behavior: a secret only the second scrub sees (a control character before the `:`) straddling position 160:
  `48 landed tail: ' ab ab ab password : <reda' | a2 mutant tail: ' ab ab ab password : QZJxk' | mutant shows value piece: True`.
- b5 would refuse a real spread symmetric around 0.5 (noul 0.4 / 0.6 have one confidence, 0.6), b6 a 3-chunk answer whose
  first two scores tie (0.5, 0.5, 0.7): no test has either positive control.
- c4 bites only when the column-free page equals the budget to the byte (the `--jev` run would then hit main's last guard,
  exit 2, while the plain run writes); c6 is an equivalent mutant (the re-trim never runs while `jev_room` bounds the column).

## 9. JT2 and the alignment (16:52-17:05Z)

My own recording double (`/tmp/vjt12/double.py`, the server's answer shape; it answers any path, so it proves only what the
tools SEND: the cuts are client-side, the real server receives the same bytes), the REAL `scripts/jev_locate.py` and
`scripts/jev_echo.py` as subprocesses with `--jev-url` and `--no-jev-log`.

The alignment's claim ("the tail is kept here, so nothing is cut there"): a 2,000-character question whose last 1,000
characters hold 8-character named values (fake) and end on `LAST_WORDS_OF_THE_ERROR`:

```
rc 0 | stderr: jev_locate: 16 hits, 16 chunks, 16 ranked by Jev, 2 of 2 instruments answered, wall 0.1 s
requests 2 | sent query chars 1000 | tail chars 1000
sent query ends with the question's last words: False
sent query tail: '<redacted>; see the handshake log and th'
```

`jev_query` takes the RAW tail (`jev_context.py:755-758`); `jev.rank` scrubs it (each 8-character value becomes the
10-character `<redacted>`) and then keeps its HEAD 1,000, so the question's last characters, where an error ends, are cut.

The echo query (`jev_echo.py:318`: `"the defect: %s; fixed as: %s"`, each side up to `SIDE_CHARS = 560`, so up to 1,144
characters) now meets `jev_query`'s 1,000-character TAIL, on JT2's own two A4 commits:

```
de06db6 rc=0 built query chars=1013 sent chars=1000 starts with 'the defect: ': False | lost head: 'the defect: #'
   sent starts: ' Final assertion: gone or zombie\nif os.path.exists("/proc/%d/stat" % c'
40543ab: built 1144 sent 1000 | starts with the label: False
lost head (144 chars): 'the defect: # Timing + progress so both you and the agent know how long it took and that it\n# finished. This hook is SYNCHRONOUS by design — the'
```

Before e0d2bdc the whole query reached Jev (JT2's bound was 1,200 and rank had no 1,000 cut). Live effect on the opt-in
order (the REAL server, 40543ab, the landed tool against a scratch copy whose only change is `SIDE_CHARS = 488`, so the whole
labelled query fits 1,000):

```
Thu Sep 24 16:57:25 UTC 2026
== landed (repo script, --no-jev-log)
1. 0.498 graft harness-ports/bin/codex-hook-adapter.py:65 ...
2. 0.496 graft scripts/jev_context.py:166 ...
3. 0.492 graft harness-ports/bin/hermes-hook-adapter.py ...
4. 0.483 graft scripts/hook_context.py ...
== scratch copy with SIDE_CHARS=488 (its call log is scratch)
1. 0.542 graft scripts/hook_context.py ...
2. 0.522 graft harness-ports/bin/codex-hook-adapter.py:65 ...
3. 0.517 graft harness-ports/bin/hermes-hook-adapter.py ...
4. 0.512 graft scripts/jev_context.py:166 ...
```

D-077, both tools, the double counting requests:

```
locate default: rc 0 requests 0 | ranking: lexical order (lexical overlap), Jev not asked
locate --order lexical: rc 0 requests 0 | ranking: lexical order (lexical overlap), Jev not asked
locate default pack == --order lexical pack: True
locate --order jev: rc 0 requests 6 | ranking: Jev reorders the lexical order's selection (KC-J5: it never drops an item); 48 of 92 chunks scored, o
echo default: rc 0 requests 0 | ranking: lexical order (lexical overlap), Jev not asked
echo --order jev: rc 0 requests 6 | ranking: Jev reorders the lexical order's selection (KC-J5: it never drops an item); 48 of 119 candidate sites
```

One tied batch of six (the double answers 0.5 for every chunk of request 2 only):

```
rc 0 requests made 2
['Jev unavailable: call 2 of 6: url: signal-free rank: all 8 chunks scored 0.5000 (unranked)']
items and files equal the lexical pack's: True 22
```

JT2 mutants (`/tmp/vjt12/mutate.py`, a scratch tree with the JT2 scripts, jev.py and the two test files; baseline
`rc=0 78 passed in 12.65s`):

```
J1 JEV_QUERY_CHARS back to 1200                      KILLED    rc=1 3 failed, 75 passed | test_from_file_reads_the_last_4000_characters, test_jev_call_is_per_chunk_with_the_query_capped_to_its_tail, test_the_query_bound_leaves_room_for_a_chunk
J2 jev_query keeps the head                          KILLED    rc=1 2 failed, 76 passed | test_from_file_reads_the_last_4000_characters, test_jev_call_is_per_chunk_with_the_query_capped_to_its_tail
J3 (M4) drop JT2's own all-equal guard               SURVIVES  rc=0 78 passed in 12.60s
J4 echo SIDE_CHARS 560 -> 900                        SURVIVES  rc=0 78 passed in 12.19s
J5 echo query without 'the defect: '                 KILLED    rc=1 1 failed, 77 passed | test_echo_jev_order_keeps_the_base_selection
J6 (M6) the default back to jev                      KILLED    rc=1 3 failed, 75 passed | test_the_default_order_is_lexical_and_jev_reorders_lexical, ..._never_asks_jev, test_the_echo_default_order_...
J7 venue auto (the bridge) instead of local          SURVIVES  rc=0 78 passed in 11.99s
J8 a failed batch is skipped, not fatal              KILLED    rc=1 6 failed, 72 passed | test_a_failed_batch_fails_the_whole_ranking, ...
```

J3 survives because JT2's guard (`jev_context.py:790`) is unreachable through the real `jev.rank`: the first batch holds
min(8, N) >= 2 chunks, so an all-equal ranking is refused by `jev.rank` (4-decimal rounding, a looser test than JT2's exact
equality) before JT2 sees it, and the alignment re-pinned both guard tests to the client's reason. J5 is killed only because
the tests' diff is short (its query keeps the label); J4 shows nothing ties SIDE_CHARS to the bound. J7: the production code
passes `venue="local"`, but no test pins it (JT2 DD-1, D-7: no network but the local endpoint).

The benchmark (A3), reproduced without touching a tracked file (`select` and `report` in a scratch copy at the same depth,
`GIT_DIR` pointing at the repo's object store, read-only; `git status --porcelain docs/research/findings/jev-locate-bench/`
empty afterwards):

```
$ sha256sum cases.json results.jsonl
2beba775ccad61b3e6131733352f37edaa8793bf77f1580f30358aba5c85960a  cases.json
52f1ac186514d8efd41660f267902ec717978d53fb613b383fc8f6cc2d497b66  results.jsonl
== select --pin db71586 (scratch output)
cases.json: 20 cases of 50 eligible ids; sha256 2beba775ccad61b3e6131733352f37edaa8793bf77f1580f30358aba5c85960a
select db71586: byte-identical to the committed cases.json
== select --pin db34178
db34178 cases equal apart from pin: True db34178 db71586
== report (scratch)
report: byte-identical to the committed results.md
== rescore (repo, prints only)
| unranked | 20 | 0.125 | 4 | 0.120 |
| lexical | 20 | 0.250 | 6 | 0.210 |
| jev | 20 | 0.200 | 5 | 0.119 |
| jev>unranked | 20 | 0.200 | 5 | 0.108 |
| jev>lexical | 20 | 0.300 | 7 | 0.122 |
Decision rule winner: **jev>lexical** (mean recall@5 0.300, MRR@10 0.122).
A3 inputs: n=20, longest 933 chars, over 1000: 0
```

D-077's numbers are the bench's own; the alignment does not touch the bench's queries (none is over 1,000 characters).
The case list and the results landed in ONE commit (6b171fb); "committed before the run" rests on the digest the lane wrote
into its report before the run, and on `select` being a deterministic function of history (reproduced above).

Hostile inputs: `tokens()`, `words()` and `search_text()` stay linear on 200,000-character pathological questions (worst
0.14 s: `a/` repeated); a bug text that starts with `--` is taken as the text (argparse reads a string with spaces as
positional); rg patterns go through `-e` and before `--` (`jev_context.py:530-532`), so a question cannot inject an rg
option. A2: with PATH and HOME pointing at empty directories, `jev_locate` exits 0 with nine named `unmapped` lines and
`jev_echo --diff <patch file>` exits 0 with every instrument unmapped; `jev_echo --diff <commit>` exits 64
(`--diff de06db6 is neither a patch file nor a commit git can show (not found: git)`), its documented usage rule.

More JT2 evidence (17:03-17:10Z):

```
== the echo query at JT2's landing (6b171fb, with its jev.py e2d02c35ecc8) vs the aligned tree, the recording double
6b171fb (JT2 as landed)      40543ab rc=0 sent=1144 starts 'the defect: ': True
6b171fb (JT2 as landed)      de06db6 rc=0 sent=1013 starts 'the defect: ': True
e0d2bdc (aligned, the tree)  40543ab rc=0 sent=1000 starts 'the defect: ': False
e0d2bdc (aligned, the tree)  de06db6 rc=0 sent=1000 starts 'the defect: ': False
== one live --order jev pack on the aligned code (A1 Q1, the real server, --no-jev-log), 17:03:24Z
ranking: Jev reorders the lexical order's selection (KC-J5: it never drops an item); 48 of 78 chunks scored, one noul each
1. 0.503 rg harness-ports/tests/test_pc_bridge_exec.py:13 ...   2. 0.463 rg scripts/pc_lane.sh:163 ...   (the lane's 14:28Z scores)
jev_locate: 90 hits, 78 chunks, 48 ranked by Jev, 7 of 8 instruments answered, wall 33.4 s
== A5 through the CLI (A1 Q3)
--budget 1000 -> rc=0 chars=930 md          --budget 1000 --json -> rc=0 chars=885 json-ok
--budget 99999 -> rc=0 chars=2988 md 1 clamp-note     --budget 99999 --json -> rc=0 chars=4946 json-ok 1 clamp-note
--budget 999 -> rc=64 chars=0 md 0 clamp-note jev_locate: usage: --budget must be at least 1000 characters
```

## 10. Adjacent findings ADJ-1 to ADJ-5 and the rest (reproduce or refute)

```
ADJ-1  reproduced (section 6: one model call, row 2 prints row 1's reason; exposure today 0)
ADJ-2  reproduced: the re-pin landed with the alignment (J1 is killed by 3 tests); one tied batch fails the whole ranking (section 9)
ADJ-3  reproduced:   letters 20000  landed 0.00s  PIN 2.75s | a. x10000 (20000)  landed 1.07s  PIN 1.06s | a. x20000 (40000)  landed 4.42s  PIN 4.32s
ADJ-4  reproduced:   render, 300 agents, 45 cluster rows: landed 3.9 ms | PIN 1.6 ms
ADJ-5  reproduced (section 7: 170 vs 195 and 160 vs 190 agent rows)
the (d) control-character gap, through the CLI:
rc 0 | error-line value on the page: False | tool-name value on the page: True | raw 0x01 bytes on the page: 3
the committed page: bytes 29295 | scrub(page)==page: True | U+2028/9: 0 | ESC/control bytes: 0 | jev head lines: 2 | clock: 2026-09-24T15:44:01Z
```

## 11. Finding inventory (no severity filter)

Evidence levels: R = reproduced by a command above; S = static reading. Canonical path = the production CLI or import API
of the landed files (or a byte-identical scratch copy where the tracked tree must not be written), the real server where a
model answer matters.

### JT1-R1 (the Jev client and the hiccup tracker)

- **F-01 INFO (R).** Premise, gates and red-green hold: 12 blobs and 4 constants match; 94 passed twice, 78 passed twice
  (172 = the landing RESULT); static gates clean; no gate file imports or runs these files; the current tests against the
  PIN scripts give 16 failed, 78 passed. Contract: the brief's premise, JT1-R1 evidence demands 2-5.
- **F-02 INFO (R).** D-076 (a) holds for the five F-16 shapes at and above the scrubber's floors (named 8-19; `sk-` 12+;
  `xox` 10+): 0 leaks in 48 cases per named shape in process (the PIN: 5 of 48 each), 0 value pieces in 3 tables each
  through the CLI. Contract: D-076 (a).
- **F-03 FOLLOW-UP (R; the scrubber's owner).** `sk-` values of 8-11 characters and `xox` values of 8-9 reach the page in
  both orders (16 and 8 of 48 in process; 6 and 7 pieces through the CLI): they are under `transcript_export.scrub`'s own
  floors (12 and 10), so no order can hide them. The JT1-R1 brief's line "`sk-` and `xox` values of 8-19 characters ... must
  leave no letter" is literally false for them; D-076 (a)'s own rationale describes values the raw scrub redacts. Canonical:
  yes. Material: letters of a short prefixed value; none live. Fix: outside the boundary (the scrubber's floors), or correct
  the brief's wording to "at and above the scrubber's floors".
- **F-04 FOLLOW-UP (R; the scrubber's owner).** Twelve more shapes leak in BOTH orders (section 5): a zero-width space or a
  Cyrillic letter inside the name; lower-case `bearer` (after `Authorization:` and bare); a quote then a space before the
  value; a value split by `,` or `;` (the tail); a no-break space inside the value; a C1 CSI between name and value; a CLI
  flag value (`-pVALUE`); plus the lane's two (ANSI, under 8). The landed docstring bounds the residual honestly ("a value it
  does not recognize in the raw text stays"). Fix: scrubber hardening (case-blind Bearer, strip zero-width and C1, a
  quote-space head), with its own tests.
- **F-05 INFO (R).** One shape leaks ONLY under the landed order: a 20+ identifier run holding an in-run provider key after a
  `-` (`<prefix>-sk-<key>`, `-ghp_`, `-xoxb-`) shows its prefix, where the PIN printed `T`: the raw scrub's marker splits the
  run, so the D-11 run rule no longer applies. Caused by D-076 (a)'s pinned order; contrived (no real credential of that
  shape known). It falsifies the lane's inferred self-attack 12.2 ("never weaker than the old order", marked INFERRED).
- **F-06 FOLLOW-UP (R).** The `_plain` cells (tool, model, agent-id, family, rule) get ONE scrub and no control-character
  hygiene: a newline in a tool name breaks rows in 3 tables; raw ESC and 0x01 bytes reach the page; and a control character
  between a secret's name and its `:` in a tool name puts the value on the page, where the same text in an error line is
  redacted by the excerpt's second scrub. D-076 (d) "pass the same scrub" was read as the function (the lane's flagged
  deviation 1). Exposure: harness-set names; none today. Fix: the excerpt's hygiene (control and separator characters to
  spaces) then `scrub` in `_plain`, without the normalization, so model names stay distinct.
- **F-07 INFO (R).** (d)'s scrub prints a 40+ character tool name as `&lt;opaque-redacted&gt;`; three live MCP tool names
  are 40-43 characters (1-2 calls each); none is on today's page; two would print the same cell.
- **F-08 CONTRACT-DEFECT (R, live; returned to the coordinator).** D-076 (b)'s character budget does not keep a chunk
  visible. (i) The client's maxima exceed Laya's room for every shape measured, English prose included (1,054 state tokens
  against 987): a 2,500-character chunk loses its tail behind a 1,000-character query. (ii) Inside the 1,000-character cut, a
  dense-script query fills the window: live, a 760-character query leaves each chunk 4 tokens and `rank` returns rc 0,
  `fan_out` 3 and distinct scores identical to ranking the chunks' first 4 tokens (B = B'); at 762 characters it ranks on ONE
  token per chunk; only the zero-token case (763) is refused. The code matches D-076 (b) to the letter; the criterion
  (characters, all-equal) cannot see a near-total cut, which is F-24's class surviving the repair. Exposure today: the repo's
  consumers send English with chunks of at most 400 characters (JT2), 300 (the scanner) or 220 (JT3), which fit (section 2);
  the generic CLI and import API do not. Proposal: a token-aware bound (the server reports each chunk's visible tokens and
  the client refuses below a floor), or state the limit in D-076 and the docstring.
- **F-09 INFO (R, live).** The refusal works live on the zero-token case (the lane had it unit-tested only) and on duplicate
  texts; five distinct irrelevant pairs never tied at 4 decimals. The CLI's exit 3 is one line; the import API returns
  `None` on the local, PC (injected) and auto paths; the log line holds `ok false` and the reason.
- **F-10 FOLLOW-UP (R, injected runner).** With `--venue auto` (the default of the CLI, the import API and the scanner's
  `--jev-venue`), a signal-free local answer walks on to the PC venue: one bridge round trip for a property of the input
  (`.pc-bridge.env` exists in the repo root, so it would be a real one). D-076 kept every other fail-open rule, the walk
  included. Fix: a signal-free refusal ends the walk.
- **F-11 FOLLOW-UP (R, live; in boundary).** ADJ-1: after one signal-free refusal, `jev_column` stops asking and prints that
  row's reason in every later UNCOVERED row (one model call; row 2 never asked). Contract: D-10 ("for each UNCOVERED
  cluster ... jev.rank"; "Jev unavailable: n/a (<reason>)"). Exposure today 0 (206 candidates, one duplicate text pair,
  `CLAUDE.md:335` and `#2`, which forms no pool). Fix (one line): do not set `down` for a `signal-free rank:` reason.
- **F-12 INFO (R).** D-076 (c) holds: 0 violations on 140 generated inputs (39 over budget before the trim) under an
  independent line-structural oracle, and through the CLI on 3 fixtures with 35 live-filled cells; both pages under 40,000.
- **F-13 INFO (R).** ADJ-5: the plain page shows 25-30 fewer agent rows on pages with 45 cluster rows (170 vs 195; 160 vs
  190); today's live page (28,962 bytes plain) is below the new budget (35,305 at 45 rows).
- **F-14 FOLLOW-UP (R; performance).** The trim loop's `left` counts agents outside the window: 3,000 of them cost 611 renders
  (2.76 s) against 11, and each render is 2.4 times slower since (d) (ADJ-4). It grows with transcript history. Fix: count
  the window's agents; binary-search the cut.
- **F-15 FOLLOW-UP (R; test gaps, the code is right).** Behavior-changing mutants the suite does not kill: c1 (`jev_room`
  without the new-this-week rows: my harness kills it with a 40,074-byte `--jev` page), a2 (the 160 cut before the second
  scrub: leaks `QZJxk`), b5 (the refusal on `confidence`), b6 (the first two chunks only); c2 and c4 are exact-edge mutants.
- **F-16 FOLLOW-UP (R).** ADJ-3: F-19's quadratic class remains (`a.` repeated: 1.07 s at 20,000 characters, 4.42 s at
  40,000); its own repro is fast only because the raw scrub replaces a 40+ letter run.
- **F-17 INFO (R).** ADJ-4: 3.9 ms against 1.6 ms for a 300-agent render.
- **F-18 INFO (S).** Stale prose: `jev.py:14-18` says the cuts make the query and chunk share the window (F-08 shows they
  need not); VERIFY-JT1 F-34's `jev.py:20`, `:33` and `jev_local.sh:9` are unchanged (routed by D-076, outside this repair).
- **F-19 INFO (R; my own side effect).** 73 synthetic lines in the shared, gitignored `.jev/calls.jsonl`,
  2026-09-24T16:45:26Z to 16:48:11Z (section 7). Not deleted.

### JT2 (the Jev bug locator and bug-echo, with the alignment)

- **F-20 BLOCKER (R, live).** The alignment cut the echo query's HEAD. `jev_echo` builds `"the defect: " + removed[:560] +
  "; fixed as: " + added[:560]` (up to 1,144 characters, `jev_echo.py:318`); since e0d2bdc, `jev_query` keeps its LAST 1,000
  (`jev_context.py:755-758`, `JEV_QUERY_CHARS` 1200 -> 1000) while `SIDE_CHARS` stayed 560. On JT2's own A4 commits the query
  Jev gets lacks the `the defect:` label (de06db6: 13 characters lost) and, for 40543ab, the first 132 characters of the
  removed lines (144 lost). At 6b171fb both queries reached Jev whole. Live, the opt-in `--order jev` output changes against
  a query that fits (top site `codex-hook-adapter.py:65` vs `hook_context.py`). Contract: JT2 D-6 ("Jev scores each against
  'the defect: <removed>; fixed as: <added>'"). Discriminator: `jev_echo.py --diff de06db6 --order jev --jev-url <recording
  double>`, sent query `startswith("the defect: ")` False now, True at 6b171fb; mutant J4 shows no test ties SIDE_CHARS to the
  bound. Fix (JT2 boundary): size each side so the whole query fits `JEV_QUERY_CHARS` (for example SIDE_CHARS 488), or cut
  the sides rather than the joined query; a test with a maximum-size diff.
- **F-21 FOLLOW-UP (R).** The alignment's other claim ("the tail is kept here, so nothing is cut there") fails when the
  scrub LENGTHENS the tail: 8-9 character named values become the 10-character `<redacted>`, and rank's head cut then drops
  the question's last characters (`LAST_WORDS_OF_THE_ERROR` lost). Rare input (short named values in a question's tail).
  Fix: scrub before taking the tail in `jev_query`.
- **F-22 FOLLOW-UP (R).** JT2's own all-equal guard (`jev_context.py:790-795`) is dead on the production path: `jev.rank`
  refuses a tied first batch (at least 2 chunks, a looser 4-decimal test) before JT2 sees it, and the alignment re-pinned
  both guard tests to the client's reason, so mutant J3 (M4) survives. Delete it, or keep it with a test that injects a rank
  without the client's refusal.
- **F-23 FOLLOW-UP (R; test gap, the code is right).** `venue="local"` is unpinned: mutant J7 (`"auto"`, which reaches the
  bridge through the repo's `.pc-bridge.env`) passes all 78 tests. JT2 DD-1 and D-7 (no network but the local endpoint).
  Fix: a test that fails if the PC path is ever taken.
- **F-24 INFO (R).** One tied batch of six fails the whole ranking; the pack falls back to the lexical order with the reason
  `call 2 of 6: url: signal-free rank: ...` and the other batches are not asked: D-3's fail-open plus the lane's flagged X-13.
- **F-25 INFO (R).** D-077 holds for both tools: no `--order` asks Jev zero times and equals `--order lexical` byte for byte;
  `--order jev` asks.
- **F-26 INFO (R).** A3 reproduced: `select` rebuilds the committed `cases.json` byte for byte (db71586) and the same cases
  from db34178; `report` rebuilds `results.md` byte for byte; `rescore` with the final library gives D-077's table; no A3
  input exceeds 1,000 characters. The case list and the results landed in one commit (6b171fb).
- **F-27 INFO (R).** A2 and A5 hold; the question parser is linear on 200,000-character pathological input; rg patterns go
  through `-e`; `jev_echo --diff <commit>` without git exits 64 (its documented usage rule).
- **F-28 INFO (R, live).** After the alignment a live Jev pack works (48 of 78 chunks in 33.4 s) with the lane's scores.
- **F-29 INFO (R).** The pin test ties `JEV_QUERY_CHARS` to `jev.RANK_QUERY_CHARS` (J1 killed by 3 tests).

## 12. The blocking predicate, per candidate

| finding | 1 contract | 2 canonical path | 3 material | 4 discriminator | 5 in boundary | disposition |
|---|---|---|---|---|---|---|
| F-20 echo head cut | JT2 D-6 | yes: `jev_echo.py --order jev`, live and with a recording double | yes: the query Jev gets loses the label and up to 132 defect characters on both A4 commits; the live order changes | yes: sent query starts with `the defect: ` False now, True at 6b171fb; J4 survives | yes (`jev_echo.py` SIDE_CHARS / `jev_context.jev_query`) | **BLOCKER (JT2)** |
| F-08 window budget | D-076 (b) met to the letter; its purpose defeated | yes, live on the real server | yes: rc 0 rankings on 1-4 chunk tokens | yes: B = B', the 763-character control | the fix needs a token-aware criterion (the server file is outside JT1's boundary) | **CONTRACT-DEFECT** (returned) |
| F-11 ADJ-1 | D-10 | yes (a byte-identical scratch copy, the real server) | only on a pool of identical texts: none today | yes | yes | FOLLOW-UP |
| F-03 short prefixed values | the brief's wording, not D-076 (a)'s rationale | yes | letters of an `sk-`/`xox` value under the scrubber's floor; none live | yes | no (the scrubber's floors) | FOLLOW-UP |
| F-06 `_plain` hygiene | D-076 (d), read as the function (flagged) | yes | contrived names; none live | yes | yes | FOLLOW-UP |
| F-21 scrub expansion | the alignment's claim | yes | rare input | yes | yes | FOLLOW-UP |
| F-23 venue unpinned | JT2 DD-1, D-7 | the code is right | none until a regression | J7 | yes | FOLLOW-UP |

## 13. Gate recommendations

- **JT1-R1: MERGE-READY-WITH-FOLLOWUPS.** No finding meets the whole blocking predicate: D-076 (a), (c) and (d) hold on new
  shapes, and (b) is implemented to the letter. **F-08 is returned to the coordinator as a CONTRACT-DEFECT**: the character
  budget and the all-equal refusal let a ranking on 1-4 chunk tokens through with rc 0 (live), and the maxima do not fit the
  window even for prose. That is a contract decision (a token-aware amendment, or a stated limit for today's English-only
  consumers), not a builder defect. FOLLOW-UPs: F-03, F-04, F-06, F-10, F-11, F-14, F-15, F-16. This recommendation
  depends on no unreproduced claim.
- **JT2: NOT-READY.** One finding meets the whole predicate: **F-20** (the alignment in e0d2bdc cut the head of the echo's
  Jev query, against D-6, on both of JT2's own A4 commits, with a live change in the opt-in order). The repair is one
  constant or one cut in `jev_echo.py` plus a maximum-size-diff test. Everything else is FOLLOW-UP (F-21, F-22, F-23) or INFO.
  The default path (`lexical`, D-077) is unaffected. This recommendation depends on no unreproduced claim.

## 14. What I reproduced, read only, and skipped

- Reproduced (commands and outputs above): the premise; both gate pairs twice; the static gates; the red-green; D-076 (a)
  on 240 in-process cases plus 17 other shapes and through the CLI; (b) with laya's own tokenizer and window code, and live
  (11 rank calls, the refusal, the venue walk with an injected runner); (c) on 140 generated inputs and 3 CLI runs; ADJ-1 to
  ADJ-5; 14 JT1-R1 and 8 JT2 mutants; D-077, the alignment's two claims, the echo head cut (double, 6b171fb vs now, live),
  the tied batch, A2, A3 (select, report, rescore), A5, hostile question shapes; one live Jev pack.
- Read only: `laya/common.py` and `laya/agent.py` (the window, the tokenizer fix-up); the server's `_answer`;
  `no_laya_in_gates.py`'s gate set; the lanes' test helpers.
- Skipped, and why: the lanes' own 16 and 6 mutant tables (their claims; my mutants are new ones); the PC venue live and
  the bridge (forbidden; injected runners only); JT3's hook and tests, FT1 and the OpenJev files (other lanes); a full-tree
  `lane_gate.sh` copy (about 1 GB on a disk that was full at 16:20Z); the live `docs/HICCUPS.md` regeneration (it reads this
  session's growing transcripts, so it is not reproducible byte for byte; its committed bytes were checked).
- My writes: this report only in the tracked tree (`git status --porcelain` shows the other lanes' files and this file); scratch
  under `/tmp/vjt12` (6.8 MB after cleanup); 73 lines in the shared call log (F-19). No commit, push, bridge call or subagent;
  the Laya server on 127.0.0.1:47411 never stopped (`/health` ok throughout); `.jev/intercept-off` untouched.
- Served model: my transcript (`agent-a55096d60845bfe72.jsonl`, counted per assistant record at 17:1xZ): 273 of 273
  `claude-opus-5-5`, 0 `"stop_reason":"refusal"`.
