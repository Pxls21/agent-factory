# VERIFY-P1 report: the P1 replay's FAIL and the instrument that measured it (task #260; seed AC7)

Lane: sandbox verify (adversarial-verifier, Opus 5.5). Brief: `tasks/briefs/jev-pipes/VERIFY-P1-brief.md`. PIN: e8c14bf.
Venue: a clean detached worktree at the PIN under the lane scratch (`.../scratchpad/verify-p1/wt`). Started 2026-09-25
08:31Z (clock `date -u`). No subagent; no git write beyond the worktree add and remove; loopback only; no PC bridge.

STATUS: DONE 09:1xZ. **GATE RECOMMENDATION: NOT-READY** on one blocker, F-PERSIST (section 11): for a pruned
persisted Bash output the harness counts the characters the pruner cut from the persisted FILE, not the characters
removed from what the model saw, so a working scorer's saving would be overstated (x2.4 on my fixture; the real
file-to-stub ratio has a median of 17x). Reproduced through the harness's own command with a loopback fake scorer; it has
NO effect on the committed FAIL, which is real and for the stated reasons: the skip counts are the pruner's own
(3,153 of 3,153 reproduced), the scorer saw no chunk token (0 of 565,206 across 1,474 rebuilt states), the trips are the
seed's rules applied by the harness, and every headline number recomputes from the logs. The instrument otherwise
measures a working pruner correctly (PASS, the 5% bar, token and re-run misses, the 20-item edges and the compaction
stop all match an independent oracle), but six of ten new mutants survive its 34 tests (G-PASS). Live scorer requests
used: 2 of 20 (one POST, section 7 R-6; one GET /health at the end, answered 200).

## 1. Premise re-measure

Measured 08:31Z in the shared tree and at the PIN (`git show e8c14bf:<file> | sha256sum | cut -c1-16`):

```
f10df15241c34828  scripts/jev_pipes/replay_pruner.py         (PIN = shared tree)
7789b1c8c983f9e6  scripts/jev_pipes/accounting.py            (PIN = shared tree)
1e6f77216996d2f5  scripts/jev_pipes/transcript.py            (PIN = shared tree)
54e1212d125e2654  scripts/jev_pipes/bridge.mjs               (PIN = shared tree)
28b097e1ad7f67f6  tests/test_jev_pipes_replay.py             (PIN = shared tree)
797329fdac2a446a  docs/research/findings/jev-pipes/P1-replay-2026-09-25.md (PIN = shared tree)
cba055a9dc33de21  scripts/laya_systemone_server.py           (PIN = shared tree)
139:        one = State.agent.system_one(dict(base, chunk=chunks[qid]), {qid: q})
```

All seven hashes and the line-139 grep match the brief.

PM-1 (a premise mismatch that does not matter): the brief's `ls .jev/pipes/` shows three logs. At 08:31Z the directory
holds FIVE, all mode 600 (`stat`, birth and mtime):

```
p1-decisions.jsonl             born 06:03:33  mtime 08:06:53  3,512,640 bytes   (the full-set replay; see section 5)
p1-decisions-sample.jsonl      born 06:15:57  mtime 06:15:57    368,438 bytes
p1-decisions-plan.jsonl        born 05:45:12  mtime 05:48:22  3,331,663 bytes
p1-decisions-plan-all.jsonl    born 08:07:40  mtime 08:09:34  3,847,328 bytes
p1-decisions-unbudgeted.jsonl  born 08:07:40  mtime 08:15:26     60,203 bytes
```

The two logs the brief's listing lacks both predate the brief's commit (2c2cb57, 08:30:45Z), so the listing was not the
directory's full state at authoring. It answers the brief's own question (the full-set log exists), so it does not
invalidate the contract.

Evidence demand 4 (the tests at the PIN, clean worktree, 08:32Z):

```
$ bash scripts/test_summary.sh tests/test_jev_pipes_replay.py     (run 1)
pytest-exit: 0
pytest-summary: 34 passed in 16.13s
$ bash scripts/test_summary.sh tests/test_jev_pipes_replay.py     (run 2)
pytest-exit: 0
pytest-summary: 34 passed in 15.97s
$ bash scripts/pc_suite.sh set-id -- tests/test_jev_pipes_replay.py
1 files set=17f6a5adc0c9
$ git status --short        (the worktree after both runs)
(empty)
```

## 2. The coordinator's data point: the one archive the live plugin wrote (answered first, as asked)

Question: the installed hook archived `.claude/fast-jev-output/bash-toolu_01DBjot1yoYr4eJmkyvL5Zfb.txt` (25,516 bytes,
02:41 container time); why did the live hook trim it while the replay pruned nothing?

Answer: **the live hook did not trim it.** It archived the output, sent 12 scoring requests, gave up waiting on them
after 30 s and passed the original through unchanged. The replay has no row for it because the call ran inside a
subagent, whose transcript the replay does not read. Evidence (read in place; no session text below):

- C-1a [verified, code-read]: the archive is written BEFORE the first scoring request, not after a trim:
  `vendor/jev-pruner/hooks/fast-jev-output.ts:212-217` (`saveOutput`) runs inside the asker's fetch wrapper at
  `vendor/jev-pruner/hooks/fast-jev-output.ts:228-230` (`if (path) await (archived ??= saveOutput())`). An archive proves
  "the hook reached scoring", never "the hook pruned". The trim path is `fast-jev-output.ts:252-269` (footer + `result`).
- C-1b [verified]: the call is `tool_use` id `toolu_01DBjot1yoYr4eJmkyvL5Zfb` in
  `/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/subagents/agent-aa842df27d05dd80d.jsonl`
  (meta: code-implementer, "Build the scrubbed session export"), record 74 (byte offset 917,202, 02:41:14.291Z), result
  record 75 (byte offset 919,609, 02:41:15.313Z). In the main transcript the id appears only in later mentions
  (records at 04:42Z, 04:49Z, 08:32Z, 08:33Z), never as a call.
- C-1c [verified, measured with the vendored `dist/` in place, `probe/live_rules.mjs`]: the model-visible result in that
  record is 25,516 characters, byte-identical to the archive (`result_equals_archive: true`), with no
  `[fast-jev-output` footer. Nothing was trimmed.
- C-1d [verified]: why it reached scoring live: estimated 13,186 tokens (`estimateTokens`), so
  `exceedsOutputThreshold(output, 10000)` is true at the upstream floor; `looksBinary` false; `classifyOutput` `unknown`
  (not a document); 318 lines.
- C-1e [verified, the scorer's own log `.jev/server.log`, read only]: after the archive (born 02:41:16.041Z) the scorer
  answered exactly 12 `POST /v1/systemone` at 02:41:59, 02:42:42, 02:43:25, 02:44:08, 02:44:54, 02:45:39, 02:46:25,
  02:47:12, 02:48:01, 02:48:36, 02:49:13 and 02:50:14 (about 43 s apart, one lock), and every one ended in
  `ConnectionResetError`: the client was gone. 12 is the hook's cap: `requestLimit = min(1 + 11, ceil(25,516 / 192))`
  (`fast-jev-output.ts:205-208`). The subagent's next record (a harness attachment) is stamped 02:41:46.076Z, 30.0 s after
  the archive: the hook held the result for the fetch limit, then the asker's error propagated (measured: a throwing
  asker makes the vendored `trimOutput` reject) into the hook's catch (`fast-jev-output.ts:270-273`, `hook_error`), which
  returns the original answer.
- C-1f [verified]: with no history and an asker that answers 0.55 for every chunk (the real scorer's band, no network),
  the vendored pruner splits this output into 16 chunks, sends 1 request of 16 questions and keeps all 16 (`kept_all`).
  So even an answered request would not have pruned it.
- C-1g [verified]: why the replay has no row: its source glob is top-level transcripts only
  (`scripts/jev_pipes/replay_pruner.py:39`, `SOURCES = "/root/.claude/projects/*/*.jsonl"`), as the P1 brief's design
  item 3 ("every main-session transcript") set it. The id is in none of the five decision logs (`grep -c` 0 in each).
  Not a different scorer answer, floor or history: a different source, and live a failed-open request, not a prune.
- C-1h [verified, a scope count]: the 281 subagent transcripts under `subagents/` hold **5,774 Bash results** of 2,000+
  characters (plus Read 1,471, Grep 17), none replayed; the replay's primary set is 3,153 main-transcript Bash results.
  None of those subagent records carries a `toolUseResult` field (0 of 5,774), which `build_job`
  (`scripts/jev_pipes/replay_pruner.py:114-123`) needs for Bash; widening the glob alone would feed the bridge a
  `result` of None for every one of them. See finding F-SCOPE in section 9.

## 3. Attack 1: the FAIL's causes, each through the real code

### 1(a) The skip counts are the vendored pruner's own decisions [verified, reproduced]

Code-read: the pruner itself decides `below_threshold`, `binary`, `document`, `few_chunks` and `budget_unfit`
(`vendor/jev-pruner/src/output.ts:392-405`, `trimOutputAttempt`; `budget_unfit` again after scoring at
`vendor/jev-pruner/src/output.ts:500`, `:531` and `:536`, `assemble`). The bridge runs the same three pre-checks first, as the hook does
(`scripts/jev_pipes/bridge.mjs:243-252` mirroring `vendor/jev-pruner/hooks/fast-jev-output.ts:178-183`), by calling the
pruner's own exported predicates. `tool_error` is the hook's rule, not `src/`: `fast-jev-output.ts:153` and `:166`
(`answer.isError`), mirrored at `bridge.mjs:222` and `:231` from the transcript's `is_error`.

Reproduction (`probe/direct.mjs` + `probe/direct_drive.py`, 08:53Z): every Bash candidate at the full run's pins (main
transcript 714,514,705 bytes, prefix sha256 `12e144e361e168c6`, re-verified) was rebuilt with the harness's own
`transcript.scan`/`windows` and `replay_pruner.build_job`, then handed to the vendored `trimOutput` DIRECTLY (none of the
bridge's pre-checks, no history, an asker that refuses and records the ask). Its decisions against the full-set log:

```
candidates 3153
2351 ('document', 'document')
524 ('few_chunks', 'few_chunks')
254 ('fail_open', 'asked')
12 ('budget_unfit', 'budget_unfit')
10 ('tool_error', 'tool_error(hook)')
2 ('binary', 'binary')
```

3,153 of 3,153 on the diagonal: no harness rule mirrors-and-differs or overrides the pruner. The 254 that failed open
are exactly the 254 the pruner itself wanted to score.

### 1(b) The scorer never saw a chunk [verified, reproduced with the checkpoint's own tokenizer]

Instrument (`probe/capture_states.py`): the harness's production path (`transcript.windows` + `build_job` + the bridge +
the vendored `trimOutput`, mode `unbudgeted` so every request up to the hook's cap is sent) against a LOOPBACK capture
scorer that runs the real server's `_answer` from the PIN (`scripts/laya_systemone_server.py:130-144`), so each
per-chunk state is built by line 139 itself (`dict(base, chunk=chunks[qid])`); a spy in the model's place measures each
state with `laya.common.build_sequence` at the checkpoint's own lengths (`scripts/laya_ft/build_dataset.py:442`,
`Fitter`: `max_len 1024 head_max_len 256`, revision 1c5edc17). The live scorer was not used. Sample: 40 of the 254
scored Bash results (sha256 order of the pointer).

```
per-chunk states 1474, results 40, requests 366
states cut by build_sequence 1474 of 1474
chunk tokens surviving: zero in 1474 of 1474 (0 of 565,206 chunk tokens)
room (state tokens build_sequence keeps) 855
prefix tokens before the chunk: min 2382, p10 10461, p50 18166, max 22427
Fitter.fits cross-check on every 25th state: 59 of 59 agree
```

Mechanism, from primary source: `laya/common.py:84` keeps the FIRST `room` state tokens (`st[:room]`) unless
`truncate_left`, which `Agent.system_one` never passes (`laya/agent.py:286`); the server appends `chunk` as the LAST key
(line 139), after `context`, `task`, `history`, `command` and `diagnosticsAndResults`
(`vendor/jev-pruner/src/output.ts:191-209`, `stateFor`).

- 1(b)-i: the report's one "may have been partly visible" request (the Bash result at byte offset 38,608 of the main
  transcript, 3,133 characters before the chunk by the harness's count) was measured the same way: 961 tokens precede the
  chunk against a room of 855, and 0 chunk tokens survive in all 4 of its per-chunk states. It was not visible.
- 1(b)-ii: the lane's no-history probe (`scratchpad/p1/probe_scores2.mjs`, re-run against the loopback capture server,
  not the live one): 265-273 prefix tokens, every chunk token kept. So "no history, chunk visible" (F3) holds for that
  probe. It is the ONLY evidence that the model answers about 0.55 for a visible chunk.
- 1(b)-iii: the coordinator's premise line ("the ap-hawk probe's per-chunk states: 300 states cut: 0") was not re-run
  (I have no ap-hawk state set); the P1 replay's states are the opposite case: 1,474 of 1,474 cut.

### 1(c) The fail-open trips are the harness's rules, as the seed requires [verified]

The pruner has no queue or budget rule: it sends every segment request at once and waits for all of them
(`vendor/jev-pruner/src/output.ts:427-431`, `Promise.allSettled`). The trips are the seed's constraint, implemented in the
bridge: queue at `scripts/jev_pipes/bridge.mjs:145-149` (a second `ask` while one request is pending), budget at
`bridge.mjs:109` and `:300-302`, the first trip in time wins (`bridge.mjs:155-159`, `firstTrip`). In the full-set log:

```
13  budget:      1 request, sent, latency > 2,000 ms, trips (budget)
241 queue_depth: >= 2 requests, the first sent, every later one refused locally and never sent
    (queue trip at 16.3 to 1,492.6 ms after the job start, p50 228.1: the pruner's own work before its 2nd ask);
    all 241 also carry a later budget trip (recorded at 2,000 ms), so the queue trip is the earlier one
```

Requests per queue row (the pruner's plan, capped at 12): 12 for 121 rows, 2 for 24, 5 for 16, 11 for 13, 4 for 12, 8 for 12.
So "queue_depth 241" is "241 results needed 2 or more requests" read through the seed's rule. The FAIL does not rest on
that reading: the budget alone fails every scored result (each chunk question takes about 3.8 s), and F6's 247 results
are unprunable at any speed.

## 4. Attack 2: the instrument on a PASS path

Instrument (`probe/pass_path.py`): a synthetic session built with the lane's own production-shape record builders
(`tests/fixtures/jev_pipes/make_fixture.py`): 20 Bash results of 60 lines, chunk c2 of each planted noise (`NOISEFILL`
plus a per-result token `noisetok_rRR_nNN`), compactions after results 5, 10 and 15, filler requests between results. A
LOOPBACK fake scorer answers noul 0.02 for a chunk holding `NOISEFILL`, 0.93 for any other. The harness runs through its
one command (`replay_pruner.main`, mode `replay`, budget 60,000 ms). The expected values come from the fixture's own
event list (an oracle in the probe, never from the harness): requests after each result up to the next compaction, the
next request's context, the pruner's compact rendering (`output.ts:560-584`), and the planted misses.

| Variant | Planted | Harness (verdict; pruned; misses; rate; saved; miss cost; net) | Oracle | Row diffs |
|---|---|---|---|---|
| v0 | nothing | PASS; 20; 0; 0.0; 37,290.1; 0; 37,290.1 | same | 0 |
| v1 | a later tool input uses a token of result 3's dropped chunk | PASS; 20; 1; 0.05; 37,768.2; 2,077; 35,691.2 | same | 0 |
| v2 | v1 + result 7's command re-run within 20 calls | FAIL (`miss rate 0.1000 > 0.05`); 20; 2; 0.10; 38,086.9; 4,273; 33,813.9 | same | 0 |
| v1neg | the token at the 21st item after result 5; result 9 re-run at the 21st call | PASS; 20; 0; 0.0; 64,221.9; 0; 64,221.9 | same | 0 |
| persisted | v0 + one persisted Bash result (a stub the model saw, the file the pruner read) | PASS; 21; 0; 0.0; **49,955.4**; 0; **49,955.4** | 43,223.9 | 1: `toolu_pp_px chars_saved 3083 vs 1261` |

Every row of v0 to v1neg matched the oracle on `pruned`, `following_calls` (so the saving stops at each compaction),
`next_context_tokens`, `chars_saved`, `miss`, `miss_rerun`, `miss_tokens > 0` and the chunk labels (c2 dropped, c1 kept
`first`, c3 kept `last`, `alignment ok`). The miss rate flips the verdict at the 5% bar exactly (5.0% PASS, 10% FAIL,
net positive in both). A token and a re-run just outside the 20-item and 20-call windows are not counted.

- F-PERSIST (the one defect): for a persisted Bash output the harness counts the characters the PRUNER dropped from the
  file, not the characters removed from the model's input. `scripts/jev_pipes/replay_pruner.py:165`
  (`chars_saved = result["charsBefore"] - result["charsAfter"]`) takes `charsBefore` = the length of the pruner's input,
  which for a persisted result is the whole file (`build_job`, `replay_pruner.py:120-123`), while the model saw only the
  stub (`result_chars`, the tool_result text; the hook caps the trimmed output at that stub,
  `fast-jev-output.ts:197-202`, `maxChars`). The row: `source_chars` 3,919 (the file), `result_chars` 2,097 (the stub),
  `chars_saved` 3,083 counted where 2,097 - 836 = 1,261 left the model's input (x2.4), `following_calls` 15,
  `tokens_saved` 11,390.4. The overcount is (file - stub) / 4.06 x `following_calls` tokens per pruned persisted result:
  6,731.5 tokens here. Blocking predicate applied in section 10.
- An earlier v0 run disagreed with the oracle on results 1 to 4 (`following_calls` 7, context 1,105). Cause: my fixture,
  not the harness: `make_fixture.assistant()` writes `cache_read_input_tokens = context - 1100`, and contexts under 1,100
  went negative, which `transcript.scan` refuses by design (`scripts/jev_pipes/transcript.py:148-151`, AF-AP-72). With
  valid contexts the rows match. The real run had no refused usage: its summary's stats carry no
  `requests_with_malformed_usage` key (17,472 requests, 127 compactions).

## 5. Attack 3: the report's numbers, recomputed from the decision logs [verified]

Which log holds the verdict: `.jev/pipes/p1-decisions.jsonl` (mode `replay`, 3,492 rows = 3,153 Bash + 321 Read + 18
Grep; truncated and rewritten by the full run 06:16Z to 08:06:53Z, the same second as the lane's `run-full/summary.json`).
My recount (`probe/recount.py`, written without the harness's `summarize()`):

| Figure | Recount | Both reports |
|---|---|---|
| Bash results; bands 2k-4k/4k-8k/8k-16k/16k+ | 3,153; 1,748/951/358/96 | same |
| document (reference, structured); few_chunks; budget_unfit; tool_error; binary | 2,351 (1,252, 1,099); 524; 12; 10; 2 | same |
| reached the scorer (by band) | 254 (138/85/28/3) | same |
| fail-open by reason | queue_depth 241, budget 13 | same |
| pruned; misses; tokens saved; miss cost; net | 0; 0; 0; 0; 0 | same |
| latency per scored result p50/p90 (ms) | 12,019.1 / 23,170.2 | same |
| per request p50/p90; per question p50/p90 (248 answered) | 11,733.7 / 22,804.4; 3,800.9 / 4,024.4 | same |
| scores min/max; within-request spread p50/max | 0.5163/0.5988; 0.0010/0.0069 | same |
| answered requests, all sets | 288 (Bash 248, Read 32, Grep 8) | same ("288") |
| requests cut by the HTTP header limit; longest answered | 6 (`UND_ERR_HEADERS_TIMEOUT`); 228,586.5 ms | same |
| Read: 321 (document 274, fail_open 32 = queue 24 + budget 8, few_chunks 15); p50/p90 14,934.8/20,314.5 | same | same |
| Grep: 18 (fail_open 8 = queue 8, few_chunks 7, document 3); p50/p90 11,450.8/45,502.4 | same | same |
| prefix before the chunk, all 294 requests: min, p10, median, max | 3,133; 27,699; **49,704**; 70,112 | "median 49,926" (N-1) |
| sample: 300 Bash (144/87/44/25), 27 reached, queue 26 + budget 1, per question p50 3,804.0 | same | same |
| unbudgeted: 60 Bash; document 50, few_chunks 6, kept_all 3, incomplete_coverage 1; 17 answered; 0.535-0.5756; 3,849.5 | same | same |
| plan-all (joined by pointer): segments 1-53 (median 11); 112 over the cap; 20,682 questions, 21.8 h | same | same |
| F6: first request covers every chunk, answered, all scores > 0.1, not persisted | 247 (6 unanswered, 1 persisted) | same |

- N-1 [verified]: the median 49,926 is the Bash-only median (254 requests); over all 294 it is 49,704. The p10 27,699
  quoted beside it IS the all-294 value (Bash-only p10: 28,442). The findings report (section 1) and the lane report (F4)
  label a mixed pair as "all 294". No effect on any conclusion.
- N-2 [verified]: "Keep rate 1.0 (chunks and characters)" is computed over rows the pruner never scored: the 1,057 chunks
  are those of `few_chunks` and `budget_unfit` rows (fail-open rows carry no `result`), which are untrimmed by
  definition. The figure is true but carries no information about scored chunks.

## 6. Attack 4: privacy [verified]

- The five decision logs (10,929 rows, `probe` scan of every string value by key): only enums (`decision`,
  `fail_open_reason`, `mode`, `band`, `set`, `stage`, `tool`, `venue`, `document_rule`, trip and error reasons), tool-use
  ids (3,525 distinct `toolu_*`), chunk ids (`c1`...), 16-hex history digests (2,578), one transcript path, the scorer
  URL and one error detail (`TypeError:UND_ERR_HEADERS_TIMEOUT`). No session text. Modes: logs 600, `.jev/` and
  `.jev/pipes/` 700.
- The lane's committed files (the 24 non-vendor paths of e8c14bf): `tests/fixtures/jev_pipes/answers.jsonl` holds the
  request-body sha256, the question ids, the HTTP status and the scorer's response (scores, usage, latency); the request
  bodies were built from the synthetic fixture (`make_fixture.py`, all synthetic, secret-shaped strings FAKE).
  `record_shapes.json` holds key names and type names only (134 leaves: type names, 4 usage key names, one source note).
  The reports quote counts, rates, pointers and code identifiers. Nothing found.
- My own report: no session text; the only session-derived items are tool-use ids, byte offsets, timestamps and counts.

## 7. Attack 5: regressions

- R-1 `.gitignore` (DEV1) [verified]: e8c14bf replaced `vendor/` with `vendor/*` + `!vendor/jev-pruner/` +
  `!vendor/jev-pruner/dist/` (`.gitignore:34-38`). Under the root `vendor/`, nothing else becomes tracked: a probe file
  `vendor/zz-new/file.txt` stays ignored, and inside `vendor/jev-pruner/` a `build/` and a `node_modules/` stay ignored.
  But the scope changed: `vendor/` (no slash in the middle) matched a directory named `vendor` at ANY depth; `vendor/*`
  is anchored at the root. Measured with `git ls-files -o -i --exclude-from=<old|new .gitignore>` on probe files in my
  worktree (removed after): `spikes/zzprobe/vendor/lib.go` and `harness-ports/zzprobe/vendor/a.txt` are ignored by the
  old file and NOT by the new one. The old file also carries `!proofs/S0-01/vendor/` (`.gitignore:52` before the change),
  which shows the any-depth reading was intended. Today no nested `vendor/` exists except `proofs/S0-01/vendor/`
  (tracked, re-included), so no file changes state now. Finding F-GITIGNORE (section 9).
- R-2 manifest counts (DEV2) [verified]: in the clean worktree at the PIN (no plugin archive directory there):
  `python3 scripts/vendored_manifest.py --check` -> `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 10 vendored roots`
  (rc 0); `bash scripts/test_summary.sh tests/test_vendored_manifest.py tests/test_vendored_manifest_parse.py` ->
  `pytest-summary: 81 passed in 114.83s (0:01:54)`. So the lane's "8 failed, 73 passed" on the shared tree is adjacent
  defect A1 (the ignored `.claude/fast-jev-output/` archive enters the `.claude/` row), not this change. The lock digest,
  recomputed with the test's own `_digest`: before e8c14bf 24 entries `f3b81f34ac1966c3`, after 25 `3c3d7af3d636a4b0`,
  one key added (`github.com/tamaratran/jev-pruner`), none removed or changed.
- R-3 the new provenance parse on hostile `VENDORED-FROM.md` lines [verified, `validate_declared_roots` on scratch
  roots]: the parse (`scripts/vendored_manifest.py:820-827`) feeds only `validate_declared_roots`
  (`scripts/vendored_manifest.py:831-850`), which refuses any root not in `VENDORED_ROOTS`, any missing root and any
  drifted line:

```
H0-unchanged ACCEPTED
H1-declared-on-two-lines REFUSED: provenance parse failure: vendor/jev-pruner/ declared twice
H2-traversal-root REFUSED: vendored-root declaration mismatch: roots missing from declared list: vendor/../
H3-twice-on-one-line REFUSED: provenance parse failure: vendor/jev-pruner/ declared twice
H4-indented-declaration REFUSED: vendored-root declaration mismatch: declared roots absent from provenance: vendor/jev-pruner/
H5-line-shift REFUSED: vendored-root declaration mismatch: declared provenance lines drifted: vendor/jev-pruner/
H6-extra-root REFUSED: vendored-root declaration mismatch: roots missing from declared list: vendor/other-tool/
H7-bold-closed REFUSED: vendored-root declaration mismatch: declared roots absent from provenance: vendor/jev-pruner/
```

  Fail-closed in every case. H1 is a usability trap: a later benign note that starts `**Added ` and names the root
  again (a refresh note) fails the check (INFO).
- R-4 the vendored pruner [verified]: of the 17 files at 47d017c (`src`, `hooks`, `package.json`, `LICENSE`,
  `README.md`, `tsconfig.json`), only `src/output.ts` differs, by the `minTokensFloor` option alone (three hunks). The
  vendored `dist/` differs from the installed plugin's `dist/` (`/root/.claude/plugins/cache/fast-jev-output/.../0.1.0`) in
  exactly `output.js`, `output.d.ts` and their maps, the same change compiled. The installed hook differs from the
  vendored one only by the uncommitted `baseUrl` patch (the lane's D2). With the option unset the floor is the upstream
  10,000; NaN and infinity fall back to it; a negative value lowers it to 0, but only when a caller passes it.
- R-5 the seed's verify commands at the PIN (worktree, after the 09:03:35Z clock line): AC1 `--help | grep -c -- --min-chars` -> `4`; AC2 ->
  `34 passed in 14.91s`; AC3 -> `PINNED`; AC5 -> `11 passed, 23 deselected in 9.36s`; AC6 -> `IGNORED` (worktree and
  shared tree).
- R-6 live determinism and the recorded fixture [verified, 1 live request]: `probe/determinism.py` rebuilt the fixture's
  request bodies with the harness (8 bodies, all 8 match a recording by sha256; the ninth recording is not produced by
  this rebuild) and sent the smallest recorded body (sha256 `dafdd05c310542cd`, 4 questions) ONCE to the live scorer:
  scores `c1 0.5672, c2 0.5673, c3 0.5671, c4 0.5672`, identical to the recording made about three hours earlier (28.1 s
  for 4 questions under the live hook's load). So the scorer is deterministic for this body, F6's "at any scorer speed"
  has its premise, and the fixture still matches the real server.

## 8. Evidence demand 3: the mutation table (new mutants of the harness and its accounting)

Method (`probe/mutate.py`): one exact replacement at a time in my clean worktree, the lane's 34 tests run, then my
PASS-path oracle variants (section 4); the file restored from a scratch copy and its sha256 checked; `git status` in
the worktree empty after every mutant (checked).

| # | Mutant (file) | Lane's 34 tests | PASS-path oracle | Reading |
|---|---|---|---|---|
| M1 | a token miss not counted: `miss=rerun` (`replay_pruner.py:187`) | **survives** (34 passed) | red: v1 misses 0 vs 1; v2 PASS vs FAIL | the verdict flips; no test drives a miss through `decision_row` |
| M2 | a re-run miss not counted: `miss=hits > 0` (`replay_pruner.py:187`) | **survives** | red: v2 PASS vs FAIL | as M1 |
| M3 | a miss costs nothing: `miss_cost = 0` (`replay_pruner.py:188`) | **survives** | red: v1 net 37,768.2 vs 35,691.2 | miss cost never tested end to end |
| M4 | a saving counted past a compaction: `Index.following` ignores the boundary (`transcript.py:79`) | red: 2 failed (`test_accounting_fixture_end_to_end[replay]`, `[unbudgeted]`) | red: v0 net 144,061.1 vs 37,290.1 | caught: the fixture pins `following_calls` |
| M5 | a saving counted past a compaction: `decision_row` multiplies by every later request (`replay_pruner.py:179`) | **survives** | red: v0 net 144,061.1 vs 37,290.1 | the multiplier in `decision_row` is untested (every fixture row saves 0) |
| M6 | a skip reason from the harness: `few_chunks` by its own line count, 60 lines or fewer (`bridge.mjs:246`) | red: 2 failed (end-to-end) | red: 60 rows differ, FAIL vs PASS | caught, but only because one fixture Read result has exactly 60 lines; 1(a)'s direct reproduction is the stronger guard |
| M7 | a skip reason from the harness: `document` by size over 12,000 (`bridge.mjs:248`) | red: 14 failed | survives (the oracle's outputs are small) | caught by the suite |
| M8 | the history not reset at a compaction (`transcript.py:217-218`) | red: 4 failed | red: v1 FAIL vs PASS | caught |
| M9 | the lookahead starts one item late (`replay_pruner.py:184`) | **survives** | survives v0-v2; red on v1neg (1 miss vs 0) | the 20-item edge is untested in the suite |
| M10 | the saving doubled (`replay_pruner.py:165`) | **survives** | red: v0 net 74,580.3 vs 37,290.1 | `chars_saved` of a pruned row is untested |

Six of ten survive the lane's suite (M1, M2, M3, M5, M9, M10); my oracle kills all ten between its variants. The brief's
three required classes: a miss not counted (M1, M2: survive), a saving counted past a compaction (M4: red; M5:
survives), a skip reason from the harness (M6, M7: red). Finding G-PASS (section 9).

## 9. Finding inventory (no severity filter)

Each: class; evidence; contract mapping; canonical path; material effect; reproduction; suggested fix.

- **F-PERSIST (BLOCKER).** For a pruned persisted Bash result, `chars_saved` counts the characters the pruner dropped
  from the persisted FILE, not the characters removed from the model's input (the stub the model saw).
  `scripts/jev_pipes/replay_pruner.py:165` (`chars_saved = result["charsBefore"] - result["charsAfter"]`), with
  `charsBefore` = the file's length because `build_job` hands the pruner the file (`replay_pruner.py:120-123`), while the
  hook caps the trimmed output at the stub the model saw (`vendor/jev-pruner/hooks/fast-jev-output.ts:197-202`). Evidence:
  verified, reproduced. Contract: seed ontology `chars_saved` ("Characters removed from the expensive model's input by
  this decision") and `tokens_saved`, seed AC2 (the row carries the characters saved), seed principle "Measured savings
  over asserted savings". Canonical path: `replay_pruner.main` at the PIN, the lane's production-shape builders, the
  vendored `trimOutput` through the bridge; the scorer is the brief's loopback fake (section 4). Material: the row
  `toolu_pp_px` counts 3,083 characters and 11,390.4 tokens where 1,261 and 4,658.9 are real; the run's net rises by
  6,731.5 tokens (49,955.4 vs 43,223.9). On this session's data the class exists: 40 persisted-like Bash candidates
  (file 38,340 vs stub 2,200 characters at the median; 18.9 M file characters behind 86,808 stub characters); if a future
  scorer let the pruner cut them, the phantom saving could reach 452 M tokens, above the 385 M ceiling of every real Bash
  saving together, enough to turn a FAIL into a PASS. The committed P1 FAIL and its numbers are NOT affected (nothing
  was pruned). Real shape checked on three of the 40 rows (numbers and key names only): `toolUseResult` carries
  `persistedOutputPath` and `persistedOutputSize`, the tool result is a 2,110-2,211-character stub naming the path, the
  files hold 32,089 to 7,804,183 characters. Reproduction: `python3 probe/pass_path.py <wt> <scratch> persisted` -> `row_diffs [["toolu_pp_px",
  "chars_saved", 3083, 1261]]`. Fix: for a persisted result, `chars_saved = cand.chars - result["charsAfter"]` (the
  model-visible length before, the rendered length after); keep `charsBefore - charsAfter` otherwise; add the persisted
  case to the pruned-row test (G-PASS). Also decide the miss baseline for persisted results (F-MISS-BASELINE). Sibling
  of the same shape (the pruner's input length used as the model's text): the character keep rate's denominator,
  `replay_pruner.py:220` (`chars_before = sum(r["source_chars"] ...)`); over the full Bash set it is 34,690,185
  characters against 15,926,739 the model saw, 18,913,387 of them persisted-file characters. Fix it in the same repair.
- **G-PASS (FOLLOW-UP, required inside the F-PERSIST repair).** No test drives a pruned result through the harness:
  every fixture row is kept, skipped or failed open, so `decision_row`'s pruned branch (`replay_pruner.py:183-188`), the
  saving multiplier and the bridge's `chunkLabels` (`bridge.mjs:173-213`, AC2's "chunks kept and dropped") never run under
  test. Evidence: verified; six of ten new mutants survive the 34 tests (M1, M2, M3, M5, M9, M10, section 8), and the
  gap is what let F-PERSIST through. Contract: the build brief's evidence demand 2 ("the accounting (saved, misses, net,
  verdict) on a small transcript fixture"), seed AC2. Material: the AC2 test evidence is empty for the pruned branch; it
  changes no output by itself. Reproduction: `probe/mutate.py`. Fix: commit a pruned-row end-to-end test in the shape of
  `probe/pass_path.py` (planted noise, a local fake scorer): saved tokens against the fixture's own arithmetic, a token
  miss and a re-run miss, the 5% edge (1 of 20 PASS, 2 of 20 FAIL), the 20-item and 20-call edges, the compaction stop,
  the miss cost, the chunk labels, and one persisted result.
- **F-SCOPE (FOLLOW-UP).** The verdict set is the main transcript's Bash results; the 281 subagent transcripts hold
  5,774 more Bash results of 2,000+ characters (plus Read 1,471, Grep 17), none replayed, and none of them carries
  `toolUseResult`, which `build_job` needs (`replay_pruner.py:114-123`). The findings report's headline says "every
  Bash result of 2,000 characters or more in this session (3,153)"; its section 2 names the two main transcripts
  correctly. Evidence: verified (C-1h). Contract: the build brief's design item 3 limits sources to main-session
  transcripts, so the harness complies; the headline overstates. Material: none for the FAIL (its causes are
  structural). Fix: say "every main-session Bash result"; a later pipeline that wants subagent results needs a
  `toolUseResult`-free job builder.
- **F-GITIGNORE (FOLLOW-UP).** `vendor/*` (`.gitignore:34`) is root-anchored; the old `vendor/` ignored a `vendor`
  directory at any depth (R-1). Evidence: verified with probe files. Contract: none frozen (a repository-wide ignore
  scope, DEV1, which the lane asked the coordinator to confirm). Material: none today (no nested `vendor/` exists except
  the tracked, re-included S0-01 one); a future `cargo vendor` or `go mod vendor` under `spikes/` or `proofs/` would show
  as untracked instead of ignored. Fix: add `*/**/vendor/` above the S0-01 negation (then `!proofs/S0-01/vendor/`, now at
  `.gitignore:56`, keeps its meaning), or record the narrowed scope.
- **F-MISS-BASELINE (UNVERIFIED, a contract question).** For a persisted result the miss check also uses the file:
  `removed = tokens(file) - tokens(kept) - history` (`replay_pruner.py:186`, `accounting.py:39`), so a later use of a
  token the stub never showed (read from the file itself, which both worlds can do) counts as a miss. The seed's and the
  brief's miss definitions say "a dropped chunk", which supports the harness literally. Not reproduced. Settle it in the
  F-PERSIST repair.
- **N-1 (INFO).** The prefix median "49,926 ... over all 294 requests" is the Bash-only median; over all 294 it is
  49,704 (the quoted p10 27,699 IS the all-294 value). Findings report section 1; lane report F4.
- **N-2 (INFO).** "Keep rate 1.0 (chunks and characters)" is computed over `few_chunks` and `budget_unfit` rows only
  (1,057 chunks the pruner never scored); true, but it says nothing about scored chunks.
- **N-3 (FOLLOW-UP, report wording).** "The one real request whose chunk may have been partly visible (3,133
  characters before it)" was not visible: 961 tokens precede the chunk against a room of 855; 0 chunk tokens survive
  (1(b)-i). The claim "the model answers near 0.55 whatever the chunk holds" then rests on the synthetic no-history probe
  alone (whose chunks were fully visible, 1(b)-ii).
- **N-4 (INFO).** "Held equal to the vendored hook by a test" (findings report section 2): the test holds five defaults and
  the goal function equal; the step order and pre-checks are mirrored by hand. 1(a)'s direct reproduction (3,153 of
  3,153) is the stronger evidence that they agree.
- **N-5 (INFO).** The row's `tokens_saved` is the gross saving; the seed ontology describes it "netted against miss
  cost". The row carries `miss_cost` beside it and the summary's `net` is right; only the field's meaning differs.
- **N-6 (INFO).** `chunks_kept` and `chunks_dropped` are null for every unpruned row (labels exist only for pruned rows);
  the counts `kept`/`dropped` are there.
- **N-7 (INFO).** The queue rule counts only the job's own pending requests (`bridge.mjs:145-149`); it cannot see other
  clients at the shared scorer, which exposes no queue signal (A3). A single-request job that waits behind another
  client records `budget`, not `queue_depth`. No effect on the verdict.
- **N-8 (INFO).** The pruner's own work before its second request took 16.3 to 1,492.6 ms (p50 228.1) in the full run:
  part of the 2 s budget even with an instant scorer. Worth a line in the findings report's "what would change the answer".
- **N-9 (INFO).** Fail-open reasons outside the seed's six are possible and recorded: `transport` (6 request errors in the
  full run, all on results already tripped by the queue rule), `request_timeout`, `pruner_error:*`.
- **N-10 (INFO).** A `--sources` glob that matches nothing prints `FAIL: no result was pruned` over 0 results, rc 0; a loud
  refusal would be clearer (FAIL is the conservative side, so no false PASS).
- **N-11 (INFO).** Scores outside [0, 1] are accepted: a scorer answering -1.0 for every chunk made the harness prune the
  signal chunk c3 and print PASS (the pruner stores `max(0, answer)`, `output.ts:435`, so a negative acts as 0). The
  seed's trips cover non-finite and missing answers only; the upstream pruner checks finiteness only.
- **N-12 (INFO).** Any `--scorer-url` is accepted; the data-boundary rule rests on the loopback default. The pruner's cloud
  default (`jev.ts:85`, `baseUrl ?? SYSTEM_ONE_URL`) cannot trigger from the CLI (argparse always passes a string; an
  empty URL fails open as `transport`, measured).
- **N-13 (INFO).** A benign later `**Added ` note naming `vendor/jev-pruner/` again fails the manifest check ("declared
  twice", H1).
- **N-14 (INFO, verified).** The coordinator's data point (section 2): the live hook archived and did not prune; the
  scorer then worked 8.5 minutes on 12 abandoned requests. This is the lane's adjacent defect A3, seen live.
- **N-15 (INFO, verified).** The 13 `budget` rows are single requests over 2 s; the 241 `queue_depth` rows need 2 or
  more requests (1(c)). The FAIL stands on three independent causes; each alone is enough.
- **N-16 (INFO).** DEV3 (`replay` waits instead of aborting) changes no trip outcome, only the latency telemetry, which it
  improves; the seed's "timeout cut to the budget" is kept in `live` mode.
- **PM-1 (INFO).** The brief's premise listing of `.jev/pipes/` showed three of the five logs (section 1).

## 10. The blocking predicate, item by item

| Finding | 1 Contract | 2 Canonical reproduction | 3 Material effect | 4 Discriminator | 5 Ownership | Result |
|---|---|---|---|---|---|---|
| F-PERSIST | yes: seed ontology `chars_saved`/`tokens_saved`, AC2, "measured savings" | yes: the one command at the PIN; the fake scorer is the brief's own attack-2 instrument (the live scorer cannot prune) | yes, on the PASS path: the row's and the run's saving are wrong for a class present in the verdict set; no effect on the committed FAIL | yes: `pass_path.py persisted` (3,083 vs 1,261) | yes: `replay_pruner.py:165`, the lane's CREATE boundary | **BLOCKER** |
| G-PASS | yes: build brief evidence demand 2, AC2 | yes: mutants on the production files | no by itself (evidence gap; it hid F-PERSIST) | yes: M1, M2, M3, M5, M9, M10 | yes | FOLLOW-UP (inside the F-PERSIST repair) |
| F-SCOPE | brief design item 3 is met; the headline overstates | yes | no (the FAIL is structural) | yes (C-1h count) | report wording: yes | FOLLOW-UP |
| F-GITIGNORE | none frozen | yes (probe files) | no today | yes | yes | FOLLOW-UP |
| F-MISS-BASELINE | the literal miss definition supports the harness | not reproduced | unknown | none built | yes | UNVERIFIED |
| N-1 to N-16, PM-1 | none, or met | - | no | - | - | INFO |

## 11. GATE RECOMMENDATION

**NOT-READY** on one blocker, F-PERSIST (the persisted-output saving is counted from the file, not from what the model
saw), reproduced through the harness's own command on a fixture with a loopback fake scorer; the real scorer cannot
produce a prune, so the defect has no effect on the committed FAIL. One focused repair (D-031, keyed by task #231,
seed `seed_5aa221965993` v1.0.0, production digest `replay_pruner.py` f10df15241c34828): fix `replay_pruner.py:165` and
commit the pruned-row end-to-end test (G-PASS), which is F-PERSIST's regression test. The P1 FAIL itself is real and
for the stated reasons (sections 3 and 5). If the coordinator rules that the harness will not grade another scorer
before a later repair, F-PERSIST and G-PASS drop to FOLLOW-UP and the recommendation becomes MERGE-READY-WITH-FOLLOWUPS.

## 12. Reproduced, reviewed statically, skipped

- Reproduced: the premise block (hashes, line 139, the checkpoint lengths through `Fitter`, the tests twice, the set
  id); the coordinator's data point (transcripts, the archive, the scorer log, the pruner's rules on the archive); 1(a)
  on all 3,153 candidates; 1(b) on 1,474 per-chunk states plus the shortest-prefix request and the no-history probe;
  1(c) from the log; every headline number of both reports from the five logs; the PASS path in five variants plus
  the multi-drop and negative-score cases; ten mutants; privacy on the logs and the committed files; the `.gitignore`
  scope, the manifest check and tests, the lock digests, seven hostile provenance lines; the vendored tree against the
  commit and the installed plugin; the seed's verify commands; one live determinism request.
- Reviewed statically: the hook's 30 s fetch limit (inferred from the 30.0 s gap between the archive and the next
  record, not read from the runtime); the runtime's `$.session.messages()` shape (the lane's modelling choices).
- Skipped, with the reason: the full replay (6,651 s and hundreds of live requests; my budget is 20); the coordinator's
  ap-hawk echo line (no ap-hawk state set in my scope); the TypeScript rebuild of `dist/` (I compared the vendored and
  installed `dist/` directly instead); the `live` mode beyond the lane's tests.

## 13. NOT done

- No PASS path on real data: the live scorer never answers at or below 0.1, so every PASS-path result comes from
  synthetic fixtures and a loopback fake scorer.
- No full-set re-run; the recount is from the lane's logs, whose production I checked only through the code and the
  samples above.
- The ap-hawk premise line ("300 states cut: 0") is not re-measured.
- F-MISS-BASELINE is not reproduced.
- No `/bug-echo` run and no registry row for F-PERSIST or F-GITIGNORE: `docs/INCIDENT-LOG.md` is outside this lane's
  boundary (the coordinator's). Echo done read-only (a grep of `charsBefore`, `source_chars` and `source` over
  `scripts/jev_pipes/`): the shape "the pruner's input length used as the model's text" appears at three sites,
  `replay_pruner.py:165` (F-PERSIST), `:186` (F-MISS-BASELINE) and `:220` (the keep-rate denominator).
- No PC venue and no GPU scorer (out of scope by the seed).
- Live requests used: 2 of 20 (one POST, section 7 R-6; one GET /health at the end, 200); the server was never restarted.
