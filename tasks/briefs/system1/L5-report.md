# L5 report: the chat bug locator, `scripts/chat_find.py` (D-090)

Lane: L5 build (sandbox, Opus 5.5, code-implementer). Started 2026-09-25 16:4xZ. Written incrementally.

**RESUMED after a container restart** (2026-09-25 16:5xZ, `date -u`): the first run died while re-measuring the premise; this continuation re-measured the premise again (section 1b) and wrote everything after section 1.

Tree (first run): branch claude/soundbox-kit-migration-iz1jwf, HEAD = origin = abae110 (see 1b for the resumed run).

## 1. PREMISE re-measured (2026-09-25 16:4xZ)

| Premise line | Brief (authoring) | Now | Matters? |
|---|---|---|---|
| origin head | 2ff48df | abae110 (one commit on top: adds the L5 and VERIFY-S1-L1 briefs + 1 ledger line; no script touched) | no |
| S1-L1 landed commit | 6195b77 | 6195b77 | match |
| free disk on / | 2.0G | 2.0G | match |
| first_seen.py, locator_trial.py | present | present | match |
| jev_context.py ORDERS / DEFAULT_ORDER / jev_rank | 75 / 81 / 805 | 75 / 81 / 805 | match |
| hiccup_scan.py DEFAULT_PROJECT_DIR / excerpt / cluster_key / canon_ts / result_text | 51 / 87 / 103 / 153 / 171 | 51 / 87 / 103 / 153 / 171 | match |
| transcript_export.scrub | 85 | 85 | match |
| jev.py LOCAL_URL; Laya pid 5187 | 64; alive | 64; alive (same cmd line) | match |
| -home-user main / subagent JSONL | 1 / 288 | 1 / 290 | no (live lanes add files) |
| -home-user-agent-factory main / subagent JSONL | 1 / 0 | 1 / 0 | match |
| scripts/chat_find.py, tests/test_chat_find.py | absent | absent | match |

Ground-truth rows: re-measured below (section 1b).

## 1b. PREMISE re-measured again after the restart (2026-09-25 17:0xZ)

| Premise line | Brief | Now | Matters? |
|---|---|---|---|
| origin head | 2ff48df | abae110 (local HEAD f259652: two coordinator commits on top, wiki and restart records; no script touched) | no |
| S1-L1 landed commit | 6195b77 | 6195b77 | match |
| free disk on / | 2.0G | 2.0G | match |
| first_seen.py, locator_trial.py | present | present | match |
| jev_context.py ORDERS / DEFAULT_ORDER / jev_rank | 75 / 81 / 805 | 75 / 81 / 805 | match |
| hiccup_scan.py DEFAULT_PROJECT_DIR / excerpt / cluster_key / canon_ts / result_text | 51 / 87 / 103 / 153 / 171 | 51 / 87 / 103 / 153 / 171 | match |
| transcript_export.scrub | 85 | 85 | match |
| jev.py LOCAL_URL; Laya pid 5187 | 64; alive | 64; alive, started 13:37:18Z (the restart did not touch it); `jev.py health --venue local` rc 0, ok true | match |
| -home-user main / subagent JSONL | 1 / 288 | 1 / 293 | no (live lanes add files) |
| -home-user-agent-factory main / subagent JSONL | 1 / 0 | 1 / 0 | match |
| scripts/chat_find.py, tests/test_chat_find.py | absent | absent | match |

Ground truth, `first_seen.py --exclude agent-a64b2872782b28c9c.jsonl` re-run (rc 0, 7.7 s, child max RSS 13,728 KB): all five
first appearances are identical to the brief (same file, line and timestamp: 154 main line 913, 181 main line 113774, 183
repo-rooted main line 219, 201 main line 126517, 209 subagent a7c113e7a3e1d35cb line 708). Only the hit counts grew, from later
records that quote the strings: 181 1 to 8, 201 4 to 11, 209 4 to 11 (154 stays 6, 183 stays 10). Verdict: the premise holds;
no CONTRACT-INVALID.

Corpus facts measured for the design (counts only): 329 transcripts (2 main, 293 subagent, 34 workflow-subagent files under
`<session>/subagents/workflows/<wf>/`, which `hiccup_scan.py`'s glob pair does not reach; 4 `journal.jsonl` files there are not
transcripts), 1,245,009,563 bytes, 261,109 lines. `hiccup_scan.Scan.feed` streamed all of them in 6.8 s at 18.5 MB max RSS.
Text the model saw, by kind: tool results 106 MB, tool inputs 61 MB (as JSON), assistant text 6.9 MB, thinking 1.5 MB, user
strings 6.4 MB, hook stdout 1.1 MB; the rest of the bytes are context attachments (task reminders alone 315 MB).

Lane transcripts that quote this oracle's answer key (excluded from the oracle runs, as the audit excluded its own):
`agent-a64b2872782b28c9c` (the S1A audit), `agent-aaaf9b49f45a3a67b` (L5's first run, killed), `agent-ac927ed4c0d8ab4c2`
(this run). Identified from each agent's `.meta.json` description (scrubbed, printed to this lane only).

## 2. What was built (2026-09-25 17:2xZ)

`scripts/chat_find.py "<description or error text>"`, one command. Options: `--match words|error`, `--order lexical|jev`,
`--hits N` (default 10), `--since T` / `--until T` (a date or datetime prefix, both inclusive at their precision), `--kind K`
(repeatable), `--exclude NAME` (a file name, an agent id or a main session id), `--json`, `--excerpt`, `--projects-dir DIR`,
and for tests `--jev-url URL` (a pinned loopback endpoint) and `--no-jev-log`. Exit 0 searched (with or without hits), 2 no
transcript or no projects dir, 64 usage error.

- **Corpus.** Every project folder under the projects dir (default: the parent of `hiccup_scan.DEFAULT_PROJECT_DIR`, so
  both roots): `*.jsonl`, `*/subagents/*.jsonl`, `*/subagents/workflows/*/*.jsonl`; `journal.jsonl` excluded.
- **Streaming, reused by import.** `hiccup_scan.Scan` is subclassed and only `record()` is replaced: the line loop, the byte
  counting and the unparsable-line handling are `Scan.feed`'s. The JSONL line number and byte offset of each record come
  from `Scan.inputs`' running counters (feed counts a line before it parses it). Also imported: `canon_ts`, `result_text`,
  `excerpt`, `CUT`, and the private patterns `_WORD`, `_STOP`, `_SEPARATORS`, `_CTRL`, `_URL`, `_RUN`, `_NUM`; from `transcript_export`: `scrub`, `scrub_payload`; from `jev_context` (lazily, only for `--order jev`):
  `jev_rank`, `reorder`.
- **Documents.** One per content block, kinds tool_error, tool_result, tool_input, assistant_text, thinking, user_text (a
  queued prompt too), hook, system; `attachment` only on request. Each document's text starts with its record's own fields
  (`tool_use Bash`, `tool_result Bash is_error`, `hook PostToolUse <name>`, `system api_error`, and `stop_reason refusal`
  for an assistant record whose stop is not tool_use, end_turn or stop_sequence). A text is built only for the kinds asked
  (found in code review before the first full-corpus run: the first draft would have built every attachment's text, 315 MB
  of task reminders, before the kind filter dropped it).
- **Words (default).** BM25, k1 1.2, b 0.75, over `hiccup_scan._WORD` minus `_STOP`; N, mean length and document
  frequencies over the documents the kind and time filters keep. Hits: the top N by score. **Error strings.** The query and
  each document pass the numbers, ids and paths part of `hiccup_scan.excerpt`'s normalization (control characters and
  separators to spaces, URLs U, runs of 20+ identifier characters T, numbers N), plus one space per whitespace run; a match
  is a substring match; hits are every match, earliest first. (Changed by the live finding in section 4: the first build
  used the whole chain but the scrub and cut, and its KEY=V and quoted-string rules swallowed a real error.) A pre-filter
  checks the longest piece of the normalized query that the normalization cannot write (no N, T, U, ? or space) as a raw
  substring first; it is safe because every replacement writes only those characters and never an empty string.
- **First appearance.** The earliest hit overall and per transcript (in words mode among the shown top N; in error mode
  among every match), with time, transcript, JSONL line, block, kind and the tool call (its own call, the call its result
  answers, the call a hook or system record names, or else the last call before it in that transcript).
- **`--order jev`.** The shown hits (N at most 48 = `jev_context.MAX_JEV_CHUNKS`) go to `jev_context.jev_rank` (the local
  endpoint only, never the bridge), each as its kind, tool and a 600-character window of its text scrubbed by
  `scrub_payload` BEFORE the cut; `jev_context.reorder` reorders them (KC-J5: never replaces them). No answer: one stderr
  line `chat_find: --order jev fell back to the lexical order: <reason>` and the header says `order=lexical (jev fell back)`.
- **No text by default.** Counts, ids, times and positions only; the query appears as a sha256 prefix and its length; tool
  names and call ids pass `scrub`. `--excerpt`: the whole block through `scrub_payload`, then a window around the match
  through `hiccup_scan.excerpt` (scrub, normalize, scrub, cut at 160). Wall time and peak RSS go to stderr only, so stdout is
  byte-identical run to run.

## 3. Tests (`tests/test_chat_find.py`)

Fixture transcripts are written at run time in the real record shapes: a main file with a tool result error, a hook record
that names its call, an unparsable line, a refusal stop in a thinking block, the synthetic API-error record, a
thinking_drop attachment, a model switch, a system api_error record, a last-prompt record, a task reminder, a queued
prompt; a subagent file; a workflow-agent file and its `journal.jsonl`; a second root with a record that has no timestamp.
Fake secrets (a token assignment, an `sk-` key, a `ghp_` token, a Bearer token, a short password with a digit) come from a
seeded generator at run time. Pinned: the whole JSON result and the whole text output of an error-string query; every
record kind, its first line of fields and its call relation; discovery (both roots, workflow agents, never a journal, with
the control that the journal holds the query); physical line numbers after an unparsable line; BM25 scores against a hand
derivation from the formula; the first appearance and per-transcript lists in words mode, bounded by `--hits`; the
refusal field; error normalization (numbers, whitespace; a changed word matches nothing); the pre-filter anchor on seven
query and document pairs, one with a lone surrogate and one with a `KEY=value` glued to the error; attachments only on request; the time window's prefix bounds and the
record with no clock; `--exclude`; no transcript text and no fake secret in any default output (with the control that
every secret is in the fixture and in a hit); the excerpt scrubbed and at most 160 characters (with the control that the
normalization alone leaves the password); the query shown only as a hash; a secret-shaped tool name scrubbed; the Jev
fallback through the real `jev_context.jev_rank` to a dead loopback port (one loud line, lexical order unchanged, no log);
the Jev reorder through an injected ranker (a permutation of the same hits, ranks renumbered, the same first appearance,
only the shown hits sent, every chunk scrubbed, with the control that a chunk held the Bearer token's place); the shared
constant; ten usage errors (exit 64) and the two exit-2 paths; two runs byte-identical, nothing written, with the control
that one more record changes the output; an error inside a long quoted string (section 4); the stderr peak is the tool's
own, not its parent's (section 4, with the control that a parent holding 200 MB shows in `ru_maxrss`).

Mutation check (a scratch copy of `scripts/`, the real files untouched, `cmp` identical after each round): mutants of
`chat_find.py`, each run against the test file. Round 1, 26 mutants: 23 killed; the survivors were an unscrubbed tool name,
hits unbounded in words mode and whitespace not collapsed. Tests were added for each; round 2: `killed 26 of 26; survived:
[]`. After the section 4 fix, round 3 with the anchor mutant updated and two new ones (the quoted-string rule back in the
match, the KEY=value rule back in the match): `killed 28 of 28; survived: []`. The quoted-string mutant is the red-green
proof of the section 4 regression test. Round 4, after the peak-memory fix (section 4, second finding) with its mutant
added: `killed 29 of 29; survived: []`. Round 5, after removing two parameters nobody used (`cfg` of `hit_row`, `rank`
of `jev_order`) and pointing the text-leak mutant at the raw block text: `killed 29 of 29; survived: []`. Not mutated: the `--jev-url` pass-through (a mutant that drops it would send the
test's calls to the live shared Laya server).

## 4. Live finding, fixed (2026-09-25, oracle round 1 at 17:21Z)

The first oracle run gave AF-AP-181's error string `'gone' == 'Z'` 1 hit, and not the truth (main line 113774), though
`first_seen.py` finds that literal in that record. Debugged on the record (booleans and class maps only): the raw text holds
the literal, the pre-filter anchor passes, the normalized text does not hold it. The record is a CI log returned inside ONE
JSON string (literal `\n` escapes, one real newline before the match), and `hiccup_scan`'s rule "a quoted string over 40
characters becomes S" turned the whole log, the error with it, into one S. That rule and KEY=value to KEY=V hide values for
the page; over a whole document they delete what is searched for. Fix: the match uses the numbers, ids and paths rules only
(the brief's own words: "(numbers, ids, paths)"); the excerpt keeps the whole chain. Regression test
`test_an_error_inside_a_long_quoted_string_still_matches` (with the control that the quoted-string rule alone removes the
literal); mutant M28 (the rule put back) turns it red. Round 2 of the oracle: rank 1 of 2, and the first line is the truth.
Not a reversal of a conclusion: a defect of this lane's first build, found by the live run and fixed at its root.

Second finding, in this lane's own instrument (17:4xZ): the oracle harness's runs reported peaks of 142 to 241 MB for
error-string runs with 2 to 9 hits, where the first smoke run from a shell had shown 24 MB. Hypothesis tested: one
error-string run reported `peak_rss_mb=24.0` from a small parent and `peak_rss_mb=310.0` from a parent holding 300 MB, so
`ru_maxrss` carries the launching process's high-water mark across fork and exec. Fix: `peak_mb()` reads `VmHWM` from
`/proc/self/status` (per address space, reset by exec), `ru_maxrss` only as a fallback. Test
`test_the_peak_is_this_process_not_the_parent_that_launched_it` (a parent holding 200 MB; the control proves the
inheritance on this box); mutant M30 (the old source) turns it red. The section 7 peaks are the re-measured ones.

## 5. The oracle (contract item 4), on the real transcripts, counts and positions only

Corpus as run (17:29Z to 17:44Z): 326 transcripts (2 main, 290 subagent, 34 workflow), 3 excluded as answer-key lanes (the
audit `a64b2872782b28c9c`, L5's killed first run `aaaf9b49f45a3a67b`, this run `ac927ed4c0d8ab4c2`), about 260,000 records,
24 unparsable lines, 160,366 documents in the default kinds. Truth = `first_seen.py`'s first hit per row (re-measured in 1b).
Harness: a scratch script that runs the real CLI with `--json` (a `--hits 100000` run for the rank in the full order, a
default `--hits 10` run for what the tool prints) and compares (root, file, line); it printed no transcript text.

Queries. **Descriptions**, by one mechanical rule over `docs/INCIDENT-LOG.md` (the row's name cell: its capital title, then
its description up to the first `; ` or sentence end; the rule was fixed once before any rank was computed, because its
first form split at an ellipsis in 201): 154 "A LANE'S SERVED MODEL CHANGED MID-RUN AFTER A REFUSAL, WITH NO NOTICE — a
sandbox subagent dispatched on the routed model hits a content-safeguard `stop_reason: "refusal"`" (17 words); 181 "A RACE
HANDLER WHOSE FALLBACK ITS OWN ASSERT REJECTS — a liveness check reads `/proc/<pid>/stat` after `os.path.exists`,
anticipates the reaper removing the entry between the two calls, and assigns a fallback ("gone") in the `except` branch" (26);
183 the title and its first clause through "(2 of 2 compactions over the limit, max 19,145 characters)" (36); 201 the title
and "the coordinator's transport probe ... the 3090 about 95% reserved)" (30); 209 the title and "the P1 bridge passed ...
so every live request died before it left" (28). **Error strings**: `first_seen.py`'s own literals, 181 `'gone' == 'Z'`,
201 `EngineDeadError`, 209 `ERR_OUT_OF_RANGE`; 154 and 183 have none (their signatures are a refusal stop followed by a
model switch, and a hook stdout over 10,000 characters).

| row | truth (first_seen.py) | error string: rank | description: rank of the truth (of candidates); words of the query in it | description: the tool's `first:` line (default 10 hits) | description with `--order jev` |
|---|---|---|---|---|---|
| AF-AP-154 | main line 913, 2026-09-02T22:30:03.520Z, assistant_text (the synthetic API-error record, stop_reason refusal) | none in the row: not run | 393 of 54,854; 3 of 17 (a record within 2 lines at 295) | main line 94527 tool_input, 20d 14h 27m 25s later | not found: lexical rank 393, outside the at most 48 hits Jev may reorder (KC-J5); not called |
| AF-AP-181 | main line 113774, 2026-09-24T10:49:55.013Z, tool_result | 1 of 2; `first:` = the truth | 120 of 56,113; 9 of 26 | main line 113883 tool_input, 3m 19s later | not found: lexical rank 120 > 48; not called |
| AF-AP-183 | repo-rooted main line 219, 2026-09-22T16:45:55.073Z, hook (SessionStart) | none in the row: not run | 1,324 of 96,278; 26 of 36 (a record within 2 lines at 4,036) | main line 116413 tool_input, 1d 19h 42m 13s later | not found: lexical rank 1,324 > 48; not called |
| AF-AP-201 | main line 126517, 2026-09-24T23:45:38.061Z, tool_result | 1 of 9; `first:` = the truth | 442 of 74,028; 6 of 30 (records within 2 lines at 295 and 2,313) | main line 126601 tool_input, 1m 52s later | not found: lexical rank 442 > 48; not called |
| AF-AP-209 | subagent a7c113e7a3e1d35cb line 708, 2026-09-25T06:03:40.206Z, tool_result | 1 of 8; `first:` = the truth | 18 of 53,772; 3 of 28 (records within 2 lines at 11 and 25) | the same subagent's line 689 tool_input, 43 s EARLIER | LIVE, `--hits 20`: rank 17 (lexical 18); order jev, 0 fallback lines, the same 20 hits; Jev's order of the lexical ranks [5, 3, 4, 11, 10, 19, 13, 12, 14, 16, 8, 1, 17, 7, 15, 9, 18, 6, 2, 20]; the `first:` line (earliest of the 20) is another subagent's tool_input 10h 56m 20s earlier; 45.6 s, 3 requests (the server's call count 6 to 9) |

One-line summary: **error strings 3 of 3 at rank 1 (the tool's `first:` line is the true first appearance each time);
descriptions 0 of 5 in the top 10 (ranks 18, 120, 393, 442, 1,324); Jev reorder reached one row (209: 18 to 17) and cannot
reach the other four by design (KC-J5); negatives 0 false hits as error strings, 10 of 10 false hits as descriptions.**

The same descriptions asked when each row was recorded (`--until` the recording commit's time, the commits named by the
audit and read with `git log -1 --format=%cI`: e37a052, de06db6, af3ab70, b6ea4b3, e8c14bf), so no registry text yet:
154 rank 91 of 35,478; 181 92 of 43,218; 183 671 of 74,688; 201 304 of 64,391; 209 14 of 50,541; none in the top 10. The
`first:` lines then: 154 5d 02h 18m 45s later; 181 16d 20h 56m 58s EARLIER (another subagent, unrelated by position); 183
1d 19h 39m 46s later; 201 8h 27m 29s earlier; 209 43 s earlier. Why descriptions miss: the truth record holds 3 to 9 of the
description's 17 to 30 words (26 of 36 for 183, in a 42 KB hook stdout that BM25's length term pushes down), while later
records that discuss the bug (the model's own commands and edits, the registry text itself: 209's top hit holds 28 of 28
words) hold most of them.

**Negative queries** (symptoms that never happened here; each error string's absence is confirmed by a second instrument,
a raw byte count of the literal over the same files):

| id | description (words) | candidates | false hits shown | top hit's words | error string | false hits | raw byte count |
|---|---|---|---|---|---|---|---|
| N1 | a Kubernetes pod was evicted when the node ran out of ephemeral storage during a helm upgrade | 7,673 | 10 | 1 of 10 | `The node was low on resource: ephemeral-storage` | 0 | 0 |
| N2 | Postgres reported a deadlock while autovacuum held a lock on the billing ledger table | 22,811 | 10 | 3 of 10 | `ERROR:  deadlock detected` | 0 | 0 |
| N3 | the iOS simulator crashed while Xcode was signing the provisioning profile for the app | 10,629 | 10 | 2 of 9 | `Code Signing Error: No profiles for` | 0 | 0 |
| N4 | the Android emulator lost its adb connection while Gradle synced the project | 12,095 | 10 | 3 of 9 | `adb: device offline` | 0 | 0 |
| N5 | the Windows installer could not open a registry key and rolled back the MSI | 23,677 | 10 | 2 of 8 | `Error 1402. Could not open key` | 0 | 0 |

Hollow-green rate of the `first:` line: error strings 0 of 5 negatives give one (and 3 of 3 positives give the truth);
descriptions 5 of 5 negatives give one (BM25 ranks whatever shares a word; there is no "not found"), and 0 of 5 positives
give the truth. `--order jev` was not run on the negatives: it reorders the same 10 hits (KC-J5), so the false-hit count
is the lexical one by construction.

## 6. The brief's question: which rows can a text query reach, and what would `--shape` need

- **181, 201, 209: yes.** Their shape is a literal in a tool result; the error-string mode puts each truth at rank 1.
- **154: half.** chat_find indexes an unusual stop reason as the words `stop_reason refusal` on the record's first line.
  That query ranks the refusal event's first record (main line 912, the thinking record, 38 ms before the truth's line 913)
  at 1 of 4,089, and its `first:` line is line 912; the truth line 913 ranks 34. The other half of the shape, the model
  switch on the next real assistant record, is metadata, not text: no text query can see it.
- **183: no.** The hook record is text (kind hook, first line `hook SessionStart <name>`), but the shape is its stdout's
  size. `SessionStart hook` ranks the truth 8,940 of 9,983 (186 of 1,773 with `--kind hook`); the top-10 `first:` is a
  hook record of 2026-09-03, 18d 19h 39m earlier (first_seen's size shape has no hit before 2026-09-22; that record's own
  event and size were not read).
- **A `--shape` mode would need:** (1) field predicates in the same single stream, over fields the scan already reads
  (`stop_reason`, `message.model`, `hookEvent`, the length of `stdout`, `is_error`); (2) per-transcript sequence state for
  two-record shapes, the machine `first_seen.py` uses (a refusal, then the next real assistant record's model differs from
  the last real one before it), kept where chat_find already keeps its per-transcript call map; (3) a closed, named
  vocabulary of shapes (first_seen's five as the seed) in reviewed code, not free predicates; (4) the same first-appearance
  output. Not built here (the brief asked the question, not the mode).

## 7. Bounded (contract item 5)

One scan streams every transcript line by line through `Scan.feed`; memory holds one line plus the candidate list (one small
tuple per document that shares a query word). Measured on the real corpus (1.2 GB):

| run (launched from a shell unless named) | wall | peak RSS |
|---|---|---|
| error string `EngineDeadError`, default hits, VmHWM (17:51Z, load average 3.9) | 10.0 s | 24.1 MB |
| error strings in the oracle (from the harness; wall only, its peaks were the harness's, section 4) | 9.6 to 11.3 s (21.8 s once under load) | not valid |
| error string, the very first run (load average 5 to 6 on 4 cores; cause not measured: the rerun at the same load took 9.8 s, so a cold page cache is the likelier cause, unproven) | 46.3 s | 23.8 MB |
| description, 14 words, 31,096 candidates, `--hits 5` | 17.3 s | 46.2 MB |
| description, 36 words (row 183), about 96,400 candidates, default hits, VmHWM | 18.4 s | 111.0 MB |
| the same with `--json --hits 100000` (every candidate rendered), VmHWM | 20.4 s | 248.5 MB |
| description `--order jev --hits 20` (row 209, live; from the harness, before the fix) | 45.6 s | 70.4 MB, not re-measured (the harness was small then; plausible, unproven) |
| for scale: `first_seen.py` (a byte pre-filter on five fixed strings) | 7.7 s | 13.7 MB |

Peak memory grows with the candidate count (about 1 KB per candidate, mostly its per-word count tuple), not with the bytes.
No index cache was built (NOT-done 1).

## 8. Gates (pasted; final files, run at 17:56:39Z)

```
$ bash scripts/pc_suite.sh set-id -- tests/test_chat_find.py
1 files set=fd6179308190
$ bash scripts/test_summary.sh tests/test_chat_find.py --basetemp=<scratch>/pt/g1    (run 1; run 2 with g2)
pytest-exit: 0
pytest-summary: 40 passed in 4.11s
pytest-exit: 0
pytest-summary: 40 passed in 4.26s
$ python3 -m pyflakes scripts/chat_find.py tests/test_chat_find.py
pyflakes rc=0
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>
scripts/chat_find.py 0
tests/test_chat_find.py 0
tasks/briefs/system1/L5-report.md 0
$ python3 scripts/ap_screen.py scripts/chat_find.py tests/test_chat_find.py
--- AP_SCREEN over 2 path(s): 5 hits over 2 files ---   (rc 0; tells, each read:)
AP-32 x4: a sha256 of the query for display (tool) and the same hash recomputed in 3 tests; no store is hashed
AF-AP-70 x1: tests/test_chat_find.py `is_file()` then `read_bytes()` over the test's own tmp fixture; nothing plants files there
$ sha256sum scripts/chat_find.py tests/test_chat_find.py | cut -c1-12
f4fcf1be4304
2a8bfe8e63a6
$ python3 scripts/chat_find.py EngineDeadError --match error --hits 1 --json <the three exclusions>   (live smoke, final file)
chat_find: wall_s=10.2 peak_rss_mb=23.9
first 2026-09-24T23:45:38.061Z -home-user line 126517 tool_result, rank 1 of 9 (the AF-AP-201 truth)
```

## 9. NOT done

1. No index cache under `.jev/` (allowed, not required). The main transcript (731 MB of the 1.2 GB) is live and changes
   size every few seconds, so a size-and-mtime key would miss on the file that holds most of the corpus; an append-only
   cache keyed by each file's byte offset would be the design. The disk is shared (2.0 GB free, INSTALL1 must keep 1 GB).
2. No `--shape` mode (section 6 answers the question). The model switch after a refusal is not indexed.
3. `--order jev` was run live once (row 209). Rows 154, 181, 183, 201 were not sent: their truth is outside the lexical
   top 48, and Jev only reorders the shown hits. The negatives were not sent.
4. The top hit's word count was recorded for 209 (28 of 28) and the negatives, not for the other positives.
5. An error string holding hiccup_scan's `S` or `KEY=V` placeholders (a `docs/HICCUPS.md` cluster key) does not match:
   those rules are out of the match (section 4). Cluster-key equality over tool errors would be its own mode.
6. No commit, no GitNexus `detect_changes` (the coordinator commits; this lane created two files and edited no existing
   symbol). Not run on the PC (a sandbox tool; no PC bridge by rule).
7. The `--jev-url` pass-through was not mutated (the mutant would send test calls to the live shared server).

## 10. DEVIATIONS from the brief (each on purpose; flagged)

1. **Discovery is not reused by import.** `hiccup_scan.py`'s discovery is the glob pair inline in `main()`, not importable,
   and it reaches neither the 34 workflow-agent transcripts nor the second root. `chat_find.discover()` applies the same
   pair to every project folder and adds `*/subagents/workflows/*/*.jsonl`. The streaming loop IS reused (`Scan.feed`).
2. **Private names imported** from `hiccup_scan`: `_WORD`, `_STOP`, `_SEPARATORS`, `_CTRL`, `_URL`, `_RUN`, `_NUM`. A rename
   there fails chat_find at import (loud); the line-number derivation also relies on `Scan.feed` counting a line in
   `Scan.inputs` before `record()` runs (pinned by the tests, M3 killed).
3. **The error normalization is the numbers, ids and paths subset** of hiccup_scan's chain (section 4), plus one space per
   whitespace run.
4. **Options beyond the brief's list:** `--match` (the two modes need a switch), `--kind`, `--exclude` (the oracle excludes
   the answer-key lanes, as the audit excluded its own), `--projects-dir`, `--jev-url` and `--no-jev-log` (tests).
5. **`--order jev` reorders the shown hits only** (at most 48, KC-J5), so the hit set and the `first:` line are the lexical
   ones; `--order jev` with `--match error` is a usage error (exit 64).
6. "Record index" is the 1-based JSONL line (first_seen.py's numbering) plus a block index; the stats line (wall, peak) is
   on stderr only.

## 11. DISCREPANCIES (both sides, evidence)

1. Hit counts differ from `first_seen.py`'s (201: 11 there, 9 here): first_seen counts tool_result blocks in every
   transcript; chat_find counts every kind (a Grep call's input holds the literal too) and excludes the three answer-key
   lanes. The first appearance agrees on all three literals.
2. AF-AP-154: first_seen's truth is line 913 (the synthetic API-error record); the refusal event starts at line 912 (the
   refused thinking record, 38 ms earlier). first_seen keeps the LAST refusal record before the switch (its `pending` is
   overwritten per refusal record). Both are the same event; the oracle scored line 913 only.
3. `hiccup_scan.Scan.feed` kinds a workflow-agent file as "main" (its parent folder is `wf_*`, not `subagents`).
   chat_find does not use that kind (its line numbers sum both counters). An adjacent defect in hiccup_scan, not fixed.
4. The same error-string query took 46.3 s on the first run and 9.8 s on the next at the same load; the cause was not
   measured (section 7).
5. `peak_rss_mb` from the harness's runs versus from a shell (section 4, second finding): the harness's numbers were the
   harness's own memory; the re-measured ones are in section 7.

**Adjacent defects (reported, not fixed):** (a) `transcript_export.scrub`'s provider-key rule needs a word boundary:
`mcp__srv__sk-<24 random characters>` passes it, and at 37 characters it is also under the 40-character opaque floor
(measured in this lane's first draft of the tool-name test). (b) `hiccup_scan.py`'s discovery misses the workflow-agent
transcripts and the repo-rooted project folder, so `docs/HICCUPS.md` omits their errors (inferred from the globs; the page
itself was not re-measured). (c) `Scan.feed`'s workflow-agent kind (discrepancy 3).

## 12. Self-attack: the three likeliest ways this is wrong

1. **Positions off by one.** Lines come from `Scan.inputs` counters, a private order in another script. Ruled out: the
   fixture pins lines 15 and 16 after an unparsable line 6 (M3 killed); on the real corpus the three error-string truths
   came back at first_seen's exact enumerate-based lines (113774, 126517, 708).
2. **Text or a secret in the default output.** Ruled out as far as tests reach: five fake secret shapes through the text,
   JSON, excerpt and Jev-chunk paths, with controls that each secret is in the fixture and in a hit, and that the
   normalization alone leaves the password (M1, M2, M14, M15, M22 killed). The scrub itself has limits (adjacent defect a);
   the default output prints no text at all, so those limits reach only `--excerpt` and the Jev chunks.
3. **Missed matches in error mode.** It happened once for real (section 4) and is fixed; the pre-filter anchor is safe by
   construction and tested on seven pairs including lone surrogates (M12, M28, M29 killed); on the corpus 3 of 3 truths at
   rank 1, and the raw byte count agreed with 0 hits on all five negatives. Residual: a match that spans two content blocks
   of one record is not found (each block is its own document).

Evidence tiers. Verified (run here): every number in sections 1b, 4, 5, 6, 7, 8, except the Jev run's peak (section 7,
flagged). Inferred: adjacent defect (b); that peak memory tracks the candidate count (two points plus the per-tuple
estimate); the cause of the slow first run. Assumed: none load-bearing.

Files created: `scripts/chat_find.py`, `tests/test_chat_find.py`, this report. No other tracked file was touched (`git
status` shows only INSTALL1's files and another lane's report besides these three). Side effect: the one live Jev run
appended 3 lines to `.jev/calls.jsonl`, jev.py's standard call log (venue local, cmd rank, 8, 8 and 4 questions, ok; its
keys hold hashes, counts and latencies, no text; the file is git-ignored). The tests pass `--no-jev-log` and write
nothing. Scratch (`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/l5/`, 2.5 MB at most: the
harness scripts, the mutant copy, the ground-truth output) was deleted at the end; free disk on / is 2.0G.
