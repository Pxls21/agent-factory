# VERIFY-S3-5-VIEW (task #444): adversarial verify of the RWKV view of the S1 dataset

PIN 3d05e645, checked at HEAD f8596924 (the premise diff over the named files is 0 at both start and end). Verifier: sandbox Opus 5.5, no subagents, no bridge, no network. Finished 2026-10-01T22:26:42Z (from `date -u`). Scratch directory: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vfy444-02lBWH` (called `<W>` below).

## Gate recommendation

**MERGE-READY-WITH-FOLLOWUPS — this depends on one measurement I could not run (I may not read the real export).**

No finding meets the whole blocking predicate on the evidence I reproduced. Three findings show the headline claim can fail through the real exporter and the view CLI, on record shapes I built:
- **F1:** a hook of the carrier's own run in its state.
- **F2:** the call's own result in a PreToolUse state.
- **F3:** a candidate missing its middle.

The coordinator settles whether the real export holds those shapes with one counts-only run (it prints counts and S1 ids, never text):

```
PYTHONDONTWRITEBYTECODE=1 python3 <W>/measure_d3.py --export <the 2026-10-01 export copy> --view <the real run's --out dir>
```

How to read the result:
- All three counts 0: MERGE-READY-WITH-FOLLOWUPS holds.
- `same_call_hook_in_state` > 0 or `own_result_in_state` > 0: F1 or F2 becomes a CONTRACT-DEFECT. D-3 needs an amendment; the builder cannot fix it inside the contract.
- `carrier_truncated` > 0: F3 becomes NOT-READY. The repair is inside the boundary.

I validated the script on my fixtures (pasted under F1). It flags exactly the rows it should and 0 elsewhere.

## Summary

- **The code against the contract:** the code does what D-1 to D-7 say, word for word, on every rule I probed:
  - 43 of 43 written-out D-1 checks;
  - the Q5 to Q7 input and output probes;
  - a direct probe of every rule a surviving mutant touches.
- **The builder's tests:** they pass twice at the PIN (`61 passed in 5.73s`, `61 passed in 5.46s`), set `1 files set=470c76f8303f`.
- **New mutants:** 27, of which 15 were killed, 12 survived and 0 were invalid. Every survivor is a test gap: the real code is right on that rule.
- **Where the risk is:** in the contract and its inputs, not in the code. D-3 finds a run by adjacency (F1, F2), and the view ignores the exporter's `truncated` mark (F3).

## Evidence demand 1: the premise

I re-ran every premise command at HEAD f8596924. Each output matched the brief line for line:
- the PIN resolves to `3d05e645c219924ebd97d0816cb1d85645203e1b`, and it is an ancestor of HEAD;
- both commit subjects match;
- both diffs count 0 lines;
- the sha256 prefixes are `e3b0c44298fc1c14`, `901c086a6a90f90a`, `16f1905ce72aee78`, `439c3fc55d0d5c3f`;
- `wc` gives 125, 357 and 888 lines (1370 total);
- every `grep -n` line number matches;
- the test file has 40 test functions;
- `s1_scores.py` has lines 67, 70, 117 and 160, and `_text_of` is at 254.

I re-measured the diff at the end: still 0. Not CONTRACT-INVALID.

## Evidence demand 2: the builder's tests at the PIN (from a `git archive 3d05e645` copy)

```
61 passed in 5.73s
pytest-exit: 0
pytest-summary: 61 passed in 5.73s
run 1 rc=0
61 passed in 5.46s
pytest-exit: 0
pytest-summary: 61 passed in 5.46s
run 2 rc=0
1 files set=470c76f8303f
```

`pc_suite.sh set-id` is a local hash of the sorted path list. I read it before running it: it makes no bridge call and reads no env file.

## Answers to Q1–Q8 (my fixtures: raw transcripts → real `session_export.py export` with init-key FAKE key, fixture repo, `--known-values key-only` → `build_s1.write_split` build → `view.py` CLI)

### Q1. D-3, the state's end

**Exact D-3 behaviour (verified).** The state is the render up to the start of the contiguous run of `hook` events that holds the carrier. A state never holds:
- the carrier itself;
- its contiguous run;
- the id's first mention (when the id appears earlier, the whole view refuses).

My fixture once put an id into a call's input by accident. The refusal: `s1-view: refused: s1-0000e001: the rendered stream of ... holds the id before its state ends (offset 55 < 70)`.

Record orders through the real exporter and the view CLI (`q1_orders.py`, `q1b_interleave.py`; both exit 0):

```
rc=0 stdout='s1-view: 14 build ids, 14 found, 0 not in the export, 0 ambiguous; 6 files, 61 events, 46 blocks, 5731 characters rendered' stderr=''
000001.jsonl s1-00001a01 PreToolUse state_event 4 step 2 end 153 state holds []
000001.jsonl s1-00001b01 PreToolUse state_event 4 step 3 end 153 state holds []
000001.jsonl s1-00001a02 PostToolUse state_event 9 step 2 end 844 state holds ['PRE-CONTEXT-OF-s1-00001a01', 'PRE-CONTEXT-OF-s1-00001b01', 'RESULT-OF-A']
000001.jsonl s1-00001b02 PostToolUse state_event 12 step 3 end 1209 state holds ['PRE-CONTEXT-OF-s1-00001a01', 'PRE-CONTEXT-OF-s1-00001b01', 'POST-CONTEXT-OF-s1-00001a02', 'RESULT-OF-A', 'RESULT-OF-B']
000002.jsonl s1-00002b01 PreToolUse state_event 6 step 2 end 484 state holds ['PRE-CONTEXT-OF-s1-00002a01', 'RESULT-OF-A2']
000003.jsonl s1-00003a01 UserPromptSubmit state_event 2 step None end 48 state holds []
000003.jsonl s1-00003a02 UserPromptSubmit state_event 2 step None end 48 state holds []
000004.jsonl s1-00004a01 PreToolUse state_event 4 step 1 end 93 state holds ['SUMMARY-WRITTEN-AT-COMPACTION']
000004.jsonl s1-00004b01 PreToolUse state_event 10 step 7 end 523 state holds ['PRE-CONTEXT-OF-s1-00004a01', 'RESULT-OF-O4A', 'SUMMARY-WRITTEN-AT-COMPACTION', 'SECOND-SUMMARY']
000005.jsonl s1-00005a02 PostToolUse state_event 6 step 1 end 460 state holds ['POST-CONTEXT-OF-s1-00005a01', 'RESULT-OF-O5']
000006.jsonl s1-00006a01 PreToolUse state_event 3 step 1 end 106 state holds ['RESULT-OF-O6-THE-CALLS-OWN-OUTPUT']
--- q1b
s1-00007a02 PostToolUse call toolu_o7_a state_event 7 end 492 state holds ['POST-CONTEXT-OF-s1-00007a01', 'RESULT-OF-A7', 'RESULT-OF-B7']
s1-00008a01 UserPromptSubmit call zq-ups-8 state_event 3 end 48 state holds ['WIKI-HINT-SAME-RUN']
s1-00009a01 PreToolUse call toolu_o9 state_event 3 end 53 state holds []
```

What each order shows:
- **O1, two parallel calls (both Pre runs, then each result with its Post run):** the two Pre states are correct. B's walk crosses A's Pre run, and its state excludes it. A PostToolUse state holds the other parallel call's Pre and Post injected texts and results. D-3 allows this: they are written before the run (F4).
- **O2, a PostToolUse run followed by the next call's PreToolUse run:** the walk crosses from Pre(B) into Post(A). `state_event` 6 is Post(A)'s run start. The state holds A's result and excludes A's Post text. No text the agent had read is lost: no model call lies between them.
- **O3, a Stop hook summary and feedback next to a prompt-time run:** the walk crosses both. If the model's turn between two prompt-time runs exports no event (an assistant record with empty content), the walk crosses into the earlier run. The state of `s1-00003a02` then loses the feedback and `s1-00003a01`'s context, both of which the agent had read (F5).
- **O4, compaction:**
  - Between a call and its hooks, the summary sits in the state and the call is still found (`step 1`).
  - Inside a run, the summary splits it, and the state ends at the summary.
- **O5, O7, O8, a run split by a non-hook event:** the state holds a hook of the carrier's own call or prompt (F1). The split comes from a task notification (O5), another concurrent call's result (O7), or a prompt-time notification (O8).
- **O6, a call's result written before its PreToolUse run:** the state holds the call's own output, and `step_found` is still true (F2).
- **O9, the id in a thinking block before its run:** thinking never renders, so no refusal. No state holds it.

### Q2. D-2, the tool_result carrier (the builder's I-1)

`q2_carrier.py`: the live scorer (`s1_scores.py --jev <empty scratch dir>` over the raw transcript) against the view (over the export).

```
rc=0 stdout='s1-view: 6 build ids, 2 found, 4 not in the export, 0 ambiguous; 1 files, 14 events, 14 blocks, 3513 characters rendered' stderr=''
true                         live=('tool_result', True)  view.carriers=('tool_result', 'PreToolUse') view row=('tool_result', 'GRAFT-ANSWER-OF-s1-0000e001') outcome={'is_error': True}
false                        live=None                   view.carriers=None   view row=None outcome={'is_error': False}
absent                       live=None                   view.carriers=None   view row=None outcome={}
one                          live=('tool_result', True)  view.carriers=None   view row=None outcome={}
parts-split-at-stamp         live=('tool_result', True)  view.carriers=None   view row=None outcome={'is_error': True} first line='...search-intercept.py]: '
parts-stamp-line-then-body   live=None                   view.carriers=('tool_result', 'PreToolUse') view row=('tool_result', 'GRAFT-ANSWER-OF-s1-0000e006')
```

- A denial with `is_error` false or absent is found by neither reader. They agree, so the build can never hold such an id.
- They disagree in two shapes:
  - `is_error: 1`: the exporter keeps only a bool in `outcome`, so the view misses it.
  - A list content of two text parts: `s1_scores.py:140` joins with `""` and `_text_of` (`session_export.py:273`) joins with `"\n"`. Split before the stamp, the view misses it; split after the stamp line, the live scorer misses it.
- A missed id counts as `not_in_export`, so no wrong row is written (F6).
- Whether the harness ever records a denial with `is_error` false or absent, I cannot measure without real transcripts.
- The real run found 4 of 4 tool_result carriers and 0 `not_in_export`.

### Q3. D-2, the candidate

`q3_candidate.py` and `q3b_cut.py` (the FAKE key is `session_export.CANARIES["hook-bearer"]`, built at import; never printed):

```
crlf                         cand_len=10    vs_chunk=equal        candidate == expected: True 'alpha\nbeta'
trailing blank lines         cand_len=5     vs_chunk=equal        candidate == expected: True 'gamma'
request line not last        cand_len=297   vs_chunk=equal        request_in_cand=True ... tail: '...3 changed what I did\nTRAILER-AFTER-REQUEST'
own id inside                cand_len=20    vs_chunk=equal        candidate == expected: True
a FAKE key the scrub takes   cand_len=292   vs_chunk=equal_prefix leaks=[]
uncommitted 40+ run          cand_len=28    vs_chunk=differs      'digest [opaque:eacf75ada34a]'
committed 40+ run            cand_len=22    vs_chunk=equal        'name <opaque-redacted>'
JSON over the exporter cap   NOT FOUND
f005 leak: False | content after the stamp line: 'token AGENT_TOKEN=<redacted> your next text with "S1-RATE s1-0000f005 rel=R use=U" (+ a no'
f008 truncated {'kept_head': 24576, 'kept_tail': 8192, 'dropped': 39698} parses: NO: Invalid \uXXXX escape
--- q3b (the cut lands on an escape boundary)
rc=0 stdout='s1-view: 1 build ids, 1 found, 0 not in the export, 0 ambiguous; 1 files, 5 events, 5 blocks, 4131 characters rendered'
event truncated: {'kept_head': 24576, 'kept_tail': 8192, 'dropped': 39699}
found; candidate len 5407 | HEAD-PART True | MIDDLE-PART False | TAIL-PART True | control chars 5384 of 12000 | cut mark False
whole {'false': 0, 'true': 1} candidate_vs_chunk {'differs': 0, 'equal': 0, 'equal_prefix': 1}
```

The candidate is the stamped text without its stamp and request lines, under the body rules without the cap, for:
- CR LF;
- trailing blank lines;
- the id inside the text;
- a committed long run.

It is not that text in four cases:
- **The request line is not the last line:** D-2's `whole` rule keeps the request line and the trailer, and the build does the same (F22).
- **A credential value just before the request line:** the exporter scrubs the canonical JSON and eats the escaped `\n` and the next word. The request line merges into the line above, so `whole` becomes false (F7, an adjacent exporter defect; the real run has `whole` false 0).
- **An uncommitted 40+ character run:** the export holds a pseudonym where the build holds `<opaque-redacted>`. The summary counts it `differs` (F8).
- **A carrier whose canonical JSON passes the exporter's 32,768-character cap:** the candidate silently loses its middle, and the counts hide it (F3).

### Q4. D-1, the render

`q4_render.py`: `Q4 checks: 43 of 43`, every expected string written out in the script. Covered:
- every row of D-1's table (`?` only for a null tool; an empty-string tool renders `Result of : r`);
- refusal by name, and the hook body rules;
- the body rules in order;
- 4,000 not cut; 4,001 cut with N=1; 9,000 (8,999 once stripped) cut with N=4,999;
- the scrub growing a body from 3,999 to 4,001 (cut, N=1, counts `scrub_changed` and `cut`), and shrinking one from 4,041 to 3,998 (not cut);
- an empty or whitespace-only body;
- `starts` for silent and empty events (`[0, 10, 10, 10, 20, 20]`);
- each block equal to its slice;
- blocks that do not depend on their neighbours (real export events, shuffled).

So a block is a function of its event alone, as task #448 needs.

One consequence of D-1's literal order: a cut body whose head ends with LF, or whose tail starts with LF, puts a blank line (the block separator) inside a block. Both checks confirm it (F17).

### Q5. D-5, the inputs

`q567.py` over copies of `base.py`'s export and build, all through the CLI:

```
Q5a output ../ escapes the export dir        rc=0 wrote=['summary.json', 'view.jsonl'] found=[all 6]
Q5b output is an absolute path               rc=0 wrote=[...] found=[all 6]
Q5c output is a symlink out of the dir       rc=0 wrote=[...] found=[all 6]
Q5d one file named twice by two spellings    rc=0 wrote=[...] found=['s1-0000ff02'] not_found={'ambiguous': 5, 'not_in_export': 0} files=3
Q5e an xz file of two streams (same events)  rc=2 wrote=None | s1-view: refused: ...agent-azqbase01.jsonl: 680 bytes follow the xz stream
Q5f seq is a bool                            rc=2 wrote=None | s1-view: refused: ...: line 1 is not an event of the export's schema
Q5g labels.jsonl with a blank line           rc=0 wrote=[...] rows same as base=True
Q5h a dataset row with an empty sources list rc=2 wrote=None | s1-view: refused: the build's train split: row s1-22084fb621ec5c6b10c4: no source identity
```

- **Refused:** two streams, a bool `seq`, empty `sources`.
- **Passed with correct rows:** `../`, an absolute path, a symlink (F9), a blank labels line.
- **Passed, ids lost (no wrong row):** one file under two spellings. Its 5 ids are counted ambiguous, and the summary shows 3 streams and 32 events (F10).

### Q6. D-6 and D-7, the outputs

```
Q6 row keys ['id', 'item_id', 'split', 'label', 'source', 'time', 'src', 'carrier', 'hook_event', 'call_id', 'step_event', 'state_event', 'state_end', 'candidate', 'candidate_sha256'] | label types ['bool'] | sorted by (src,state_event,id): True
Q6 --out symlink to an empty dir             rc=0 wrote=['summary.json', 'view.jsonl'] target now=['summary.json', 'view.jsonl']
Q6 --out dangling symlink                    rc=2 ... exists and is not an empty directory
Q6 --out is a file                           rc=2 ... exists and is not an empty directory
Q6 --out non-empty dir                       rc=2 wrote=['keep'] ...
s1-view: refused: --out .../probe/race/out exists and is not an empty directory
Q6 a dir that appears between the two checks: rc=2, out holds ['planted']
Q6 byte identity: other code tree + other cwd + relative inputs: rc=0 identical=True stdout same=True
```

- **Rows and sort:** the base fixture's ids are deliberately out of `state_event` order, and the rows still sort by (`src`, `state_event`, `id`).
- **No session text in `summary.json`:** every string in it is one of:
  - a version;
  - a sha256;
  - the build's commit;
  - the export's `export_id` (here `2026-10-01T22:14:36Z`: the input's own id, not the view's clock);
  - a `src` path key;
  - a `hookEvent` or carrier name.
- **The `code` hashes:** my own import-closure measurement gives 20 files. The 12 under `scripts/` are hashed. The 8 outside are not: `docs/research/findings/{ap-hawk-probe/ap_probe.py, j2-v1-probe/v1_probe.py, j2c-fulltext/j2c.py}` and 5 under `src/agent_factory/`. That follows D-6's wording ("each module they import from `scripts/`"), so it is not a contract gap (F19).
- **`--out`:** the second check works; a symlink to an empty directory writes through the link (F14).

### Q7. Failure behaviour

```
Q7a hook text nested past the recursion limit rc=1 wrote=None | RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string
Q7b an event whose role is a list            rc=1 wrote=None | TypeError: unhashable type: 'list'
Q7c a manifest output with a NUL             rc=1 wrote=None | ValueError: embedded null byte
Q7d --out under /proc (not writable)         rc=1 wrote=None | FileNotFoundError: [Errno 2] No such file or directory: '/proc/vfy444'
Q7e a manifest with no sources               rc=0 wrote=[...] found=[] | s1-view: 6 build ids, 0 found, 6 not in the export, 0 ambiguous; 0 files, ...
Q7f a manifest missing one entry             rc=0 wrote=[...] found=[5 ids] | ... 1 not in the export
Q7g the build commit is NaN                  rc=0 summary commit line=['"commit": NaN,']
both files listed : rc=0 ... 5 found, 0 not in the export, 1 ambiguous
lane entry dropped: rc=0 ... 6 found, 0 not in the export, 0 ambiguous | ff02 found in e-4c4c-9d9d-400000000001.jsonl
swapped entries   : rc=0 ... every row's src is the other file's (s1-0000ff02 under the main src, the main ids under the lane src)
```

**Exit 1 instead of 2.** Four inputs exit 1 with nothing written: Q7a, Q7b and Q7c need a hand-made export with its sha256 recomputed, and Q7d is an `--out` that cannot be created (F13). Nesting depth, through the real exporter:
- depths 500 to 985 and 990 to 2,000 all exported, and the view read every export it got (exit 0);
- at 986 the exporter itself failed;
- at 990 and above it exported 3 of 4 records (F24, adjacent).

**Exit 0 with a wrong or partial output.** All need a hand-edited manifest:
- an empty manifest (counted);
- a dropped entry (counted);
- a dropped entry that hides an ambiguous id, which then writes a wrong row (F11);
- swapped entries, which write a wrong `src` on every row (F12).

### Q8. The tests

- **One partial mirror:** `test_no_hook_text_of_the_carriers_run_is_in_its_state` (test file lines 656-672) finds the run with the code's own adjacency loop (`while j > 0 and events[j - 1]["kind"] == "hook"`), and it builds blocks and the state with `R.block` and `R.render`. It checks D-3's procedure, not D-3's stated invariant, so it cannot see F1 (F16).
- **A pin by design:** `test_a_tool_result_carries_a_stamp_only_as_a_hook_error` pins the builder's own I-1 choice.
- **Independent oracles:** the other tests compare against hand-written strings, `state_end` sums and texts.
- **Fixture gaps:** the fixture lacks:
  - a split run;
  - a denial with its call's PreToolUse hooks before it;
  - a run at a file's first event;
  - a run of exactly two LFs;
  - ids out of state order;
  - a candidate over 4,000 characters;
  - a CR or double LF in a chunk;
  - `step_found` false;
  - duplicated call ids.

New mutants are in the table below.

## Evidence demand 4: the mutant table

`<W>/mutants.py`: a full scratch copy of the PIN. Each mutant is one exact edit, checked unique in the file, then compiled, with 61 tests collected. Settings: `COLUMNS=1000`, no `PYTHONPATH`, the pristine file restored after each. The modules were confirmed to load from the copy.

```
BASELINE rc=0 total=61: 61 passed in 5.67s
MUT TREE RESTORED: True
KILLED 15 SURVIVED 12 INVALID 0
```

| # | File | Exact edit (old → new) | Result: tests that failed |
|---|---|---|---|
| N1 | render.py | `re.compile(r"\n{2,}")` → `re.compile(r"\n{3,}")` | **SURVIVED** (61 passed) |
| N2 | render.py | `return newlines(out).strip()` → `.rstrip()` | KILLED, 12 failed: `test_a_hook_renders_what_it_handed_the_model`, `test_an_absent_build_id_is_counted_not_in_export_and_the_run_exits_0`, 8 rows of `test_each_rendered_pair_has_its_label_and_the_newline_rule`, `test_the_render_of_the_fixture_is_the_text_written_out_here`, `test_the_summary_holds_counts_and_digests_and_no_session_text` |
| N3 | render.py | `if len(out) > CAP:` → `>= CAP` | KILLED, 1 failed: `test_an_empty_body_renders_nothing_and_the_cap_keeps_head_and_tail` |
| N4 | render.py | `CUT_MARK % (len(out) - CAP)` → `- HEAD` | KILLED, 3 failed: `test_an_empty_body...`, `test_the_render_of_the_fixture...`, `test_the_summary...` |
| N5 | render.py | `return "\n".join(t for _kind` → `"".join` | KILLED, 1 failed: `test_a_hook_renders_what_it_handed_the_model` |
| N6 | render.py | `a["type"].startswith("hook_")` → `a["type"] == "hook_additional_context"` | KILLED, 5 failed: `test_a_hook_renders...`, `test_an_absent_build_id...`, `test_every_present_id_is_found_once_where_it_sits`, `test_the_render_of_the_fixture...`, `test_the_summary...` |
| N7 | render.py | `if not out: return ""` → `if out is None:` | KILLED, 7 failed: `test_a_hook_renders...`, `test_an_absent_build_id...`, `test_an_empty_body...`, `test_every_present_id...`, `test_no_hook_text_of_the_carriers_run_is_in_its_state`, `test_the_render_of_the_fixture...`, `test_the_summary...` |
| N36 | render.py | `+ out[-TAIL:]` → `+ out[-TAIL - 1:]` | KILLED, 4 failed: `test_an_absent_build_id...`, `test_an_empty_body...`, `test_the_render_of_the_fixture...`, `test_the_summary...` |
| N10 | view.py | `events[before[-1]]["seq"]` → `before[0]` | **SURVIVED** |
| N12 | view.py | `whole = stamped.rstrip("\n").split("\n")[-1]` → `stamped.split("\n")[-1]` | KILLED, 2 failed: `test_every_present_id...`, `test_the_summary...` |
| N14 | view.py | sort key `(src, state_event, id)` → `(src, id)` | **SURVIVED** |
| N15 | view.py | that sort → `rows.sort(key=lambda r: 0)` | **SURVIVED** |
| N19 | view.py | `os.path.lexists(out)` → `os.path.exists(out)` | **SURVIVED** |
| N20 | view.py | the second `check_out(out)` in `write` → `pass` | **SURVIVED** |
| N26 | view.py | `chunk = R.newlines(b["chunk"]).strip()` → `chunk = b["chunk"]` | **SURVIVED** |
| N31 | view.py | `while j > 0 and ...` → `while j > 1 and ...` | **SURVIVED** |
| N33 | view.py | `type(ev["seq"]) is int` → `isinstance(ev["seq"], int)` | **SURVIVED** |
| N39 | view.py | `R.clean(B.chunk_of(stamped, whole))` → `R.body(...)` (the cap on the candidate) | **SURVIVED** |
| N49 | view.py | `while j > 0 and ...` → `while kind != "tool_result" and j > 0 and ...` | **SURVIVED** |
| N53 | view.py | `counts["step_found"][_flag(f["step_event"] is not None)] += 1` → `["true"] += 1` | **SURVIVED** |
| N57 | view.py | `for ... in found:` → `in found[:1]:` | KILLED, 1 failed: `test_an_id_the_render_holds_nowhere_is_refused` |
| N27 | view.py | (control) `f["candidate"].startswith(chunk)` → `chunk.startswith(f["candidate"])` | KILLED, 1 failed: `test_the_summary...` |
| N43 | view.py | (control) `text.find(sid)` → `text.rfind(sid)` | KILLED, 1 failed: `test_an_id_the_stream_holds_before_its_state_ends_is_refused` |
| N48 | view.py | (control) `"chunk": row["state"]["chunk"]` → `"chunk": ""` | KILLED, 1 failed: `test_the_summary...` |
| N52 | view.py | (control) `if f["first"] < f["state_end"]:` → `if 0 <= f["first"] < ...` | KILLED, 1 failed: `test_an_id_the_render_holds_nowhere_is_refused` |
| N54 | view.py | (control) `if f["has_step"]:` → `if True:` | KILLED, 1 failed: `test_the_summary...` |
| N55 | view.py | (control) `["0" if f["run_before"] == 0 ...]` → `<= 1` | KILLED, 1 failed: `test_the_summary...` |

**The survivors are N1, N10, N14, N15, N19, N20, N26, N31, N33, N39, N49 and N53.** For each, the real code is right on the rule; I probed it directly:
- N1: my Q4 check on a run of two LFs;
- N14 and N15: the base fixture sorts by `state_event`;
- N19 and N20: the `--out` probes;
- N26: Q3's CR LF chunk compares `equal`;
- N31: a SessionStart run at a file's first event gives `state_event 0 state_end 0`, and the same-run hook text is not in the state;
- N33: Q5f;
- N39: a 6,159-character candidate, uncut and equal to the text;
- N49: the base denial's walk gives `state_event` 9;
- N53: `step_found {'false': 1, 'true': 2}`;
- N10: `step_event` 9 among call seqs `[7, 9]`, which is the last call (D-3 does not say which).

**Spot check of the builder's claims** (its exact edits, run by me):
- `M1 6 failed, 55 passed`, named test `test_a_thinking_marker_is_in_no_output_and_no_rendered_stream` included;
- `M2 3 failed, 58 passed`, named test `test_no_hook_text_of_the_carriers_run_is_in_its_state` included.

Both match its report.

## The builder's readings graded (section 0 of its report)

| Item | Grade | Evidence |
|---|---|---|
| D-0 (did not stop when the tree changed) | A process deviation from its dispatch; no code effect | `git diff --stat 610cb123 92d74958^ -- <read set>` gives 0 lines |
| I-1 (`is_error` required through `injections_of`) | Conformant: D-2's parenthetical names `injections_of`'s rule | Q2: agrees with the live scorer for true, false and absent; diverges only for a non-bool `is_error` and split list content (F6) |
| I-2 (`lstrip` before the feedback test) | Sound reading | Matches the exporter's own classification (`session_export.py:599-603`) |
| I-3 (`?` for a null tool in a tool_call) | Sound reading | D-1 does not cover it |
| I-4 (8 imports outside `scripts/` not hashed) | D-6's wording; reproduced exactly | Provenance gap only (F19) |
| I-5 (an id the render holds nowhere is refused) | Conformant: the formula as written | Its test kills N52 |
| I-6 (a file named twice is refused) | Sound extension | Compares strings, so another spelling passes (F10) |
| I-7, I-8 (extra counts) | Conformant ("and the render's counts") | Real-run counts are consistent |
| I-9 (extra fixture item) | Sound | |
| I-10 (each line one schema event) | Sound, fail-closed | A bool `seq` is refused (Q5f) but untested (N33) |
| I-11 (`--out` outside git not enforced) | Sound reading of an open point | A symlink writes through it (F14) |
| I-12 (`hook_unparsed` scope) | Conformant to D-1's sentence | JSON `123` renders nothing and is not counted (Q4) |
| I-13 (read once, hashed, compared) | Sound TOCTOU guard | |
| I-14 (offsets in code points) | Sound | D-1 says "offset in `text`", a str |
| I-15 (output forms) | Sound | D-6 does not set them; see F23 |

## Finding inventory (no severity filter)

**F1. FOLLOW-UP. UNVERIFIED on the real export; a CONTRACT-DEFECT if `measure_d3` counts any.** A non-hook event that splits a run lets a hook of the carrier's own call or prompt into its state.
- **Evidence:** reproduced through the real exporter and the view CLI, exit 0, uncounted and unrefused:
  - O5, a task notification between two PostToolUse hooks of one call: `s1-00005a02` holds `POST-CONTEXT-OF-s1-00005a01`;
  - O7, a concurrent call's result between them: `s1-00007a02` holds `s1-00007a01`'s text;
  - O8, a prompt-time plain-stdout hook, then a notification, then the stamped hook: `s1-00008a01` holds `WIKI-HINT-SAME-RUN`.
- **Contract mapping:** the code follows D-3's procedure word for word ("walk back over events whose kind is hook"). It breaks D-3's own rationale ("the hooks of one call run in parallel and never see each other's output, so no hook text of that run is in the state") and the brief's headline claim.
- **Canonical path:** yes, on record orders I built. No committed measurement says whether the harness writes them, and I may not read real transcripts. Claude Code runs concurrency-safe tools (Read, Grep, Glob) in parallel, which makes O7 plausible (INFERRED). The published counts (`hook_run_before 0` = 30) cannot be split by cause.
- **Material effect:** unknown on the real build.
- **Discriminator:** `measure_d3.py` checked on my fixtures:
  ```
  q1  {"carrier_not_relocated": 0, "carrier_truncated": 0, "own_result_in_state": 1, "rows": 14, "same_call_hook_in_state": 1} ids: {"own_result_in_state": ["s1-00006a01"], "same_call_hook_in_state": ["s1-00005a02"]}
  q1b {... "rows": 4, "same_call_hook_in_state": 2} ids: {"same_call_hook_in_state": ["s1-00007a02", "s1-00008a01"]}
  base, surv, q3, q2: all 0;  q3b: "carrier_truncated": 1 ["s1-0000f018"]
  ```
- **Fix:** amend D-3 so the run is the carrier's hook events by `toolUseID` and `hookEvent`, not by adjacency. Inside the boundary meanwhile: refuse, or count and drop, a row whose state holds a rendering hook event with the carrier's `toolUseID` and `hookEvent`, and add a split-run fixture. This lower-bounds UserPromptSubmit runs if the harness gives each prompt-time hook its own `toolUseID`.

**F2. FOLLOW-UP. UNVERIFIED (a CONTRACT-DEFECT if counted).** A call's tool_result written before its PreToolUse run leaves the call's own output in the state. `step_found` stays true and nothing checks it.
- **Evidence:** reproduced (O6: `RESULT-OF-O6-THE-CALLS-OWN-OUTPUT`).
- **Contract mapping:** D-3, procedure followed; headline claim broken.
- **Canonical path:** yes. I have no evidence the harness writes this order.
- **Fix:** count or refuse a PreToolUse carrier whose call has a tool_result before `state_event` (`measure_d3.py` `own_result_in_state`).

**F3. FOLLOW-UP. UNVERIFIED on the real export; NOT-READY if counted (the fix is inside the boundary).** A carrier whose canonical JSON the exporter cuts on an escape boundary still parses, and its candidate silently loses the middle.
- **Evidence:** reproduced (q3b):
  - `MIDDLE-PART False`;
  - `control chars 5384 of 12000`;
  - no cut mark;
  - `whole` true;
  - counted `equal_prefix`, so the summary hides it.
- **Mechanism:** the event's `truncated` is set, and the view never reads `truncated`. A cut that splits an escape loses the id instead (f008, counted `not_in_export`).
- **Reachability:** `STAMP_MAX_CHARS` is 9,500 and the exporter's CAP is 32,768, so only a stamped text whose JSON escaping grows it more than 3.4 times (mostly control characters) gets here. The real export's 3 truncated hook events most likely are hook_success records, whose stdout is JSON escaped twice and which are never carriers (INFERRED).
- **Contract mapping:** D-2 procedure followed; breaks demand 2's "candidate (equal to the text that was stamped)" and the headline.
- **Fix:** refuse, or count and drop as `truncated`, a carrier whose event has a non-null `truncated`.

**F4. INFO.** Parallel calls: a PostToolUse state holds the other parallel call's injected texts and results (O1). In O2, Pre(B)'s walk crosses into Post(A)'s run; A's result stays in the state.
- **Contract mapping:** D-3-conformant: everything there was written to the stream before the run. The model had read none of it when the hook ran (one batch). The live reader of task #448 would hold it.
- **Fix:** name which "seen" the heads train on, before task #441.

**F5. INFO.** The walk crosses into an earlier run the agent had read when the model's turn between them exports no event (an assistant record with empty content).
- **Cost:** the state of `s1-00003a02` loses the Stop feedback and `s1-00003a01`'s context.
- **Frequency:** rare.
- **Fix:** none needed now; `measure_d3` could also count crossings.

**F6. INFO.** The two tool_result readers diverge for `is_error: 1` and for two-part list content (Q2 table).
- **Effect:** each miss counts as `not_in_export`; no wrong row. The real run had 4 of 4 tool_result carriers found and 0 `not_in_export`.
- **Fix:** none in this component; a note for `s1_scores` and the exporter.

**F7. INFO (adjacent defect, out of boundary: `session_export.py` scrubbing the canonical JSON with `transcript_export` rules).** A credential value followed by an escaped `\n` takes the newline and the next word.
- **Evidence:** `token AGENT_TOKEN=<redacted> your next text with "S1-RATE s1-0000f005 ...` — the word `Begin` and the line break are gone. This is over-redaction (text lost), not a leak.
- **Effect on the view:** `whole` becomes false and the candidate keeps the request text. `counts.whole.false` shows it; the real run reads 0.
- **Route:** VERIFY-SESSION-EXPORT or the scrub owner.

**F8. INFO.** For an uncommitted 40+ character run, the export carries a pseudonym `[opaque:<12 hex>]` while the build's chunk and any live render of raw text carry `<opaque-redacted>`.
- **Evidence:** `candidate_vs_chunk` reads `differs` (q3). The real run reads 0 `differs`.
- **Note for task #448:** if it renders raw transcripts, its states will differ from the trained ones on such texts.

**F9. FOLLOW-UP.** A manifest `output` may leave the export directory (`../`, an absolute path, a symlink).
- **Evidence:** all accepted, with correct rows: the sha256 pins the bytes.
- **Classification:** defence in depth.
- **Fix:** refuse an output that does not resolve inside the export directory.

**F10. FOLLOW-UP.** One file named by two entries under two spellings (`x` and `./x`) passes I-6's string check.
- **Evidence:** read twice; 5 ids lost as `ambiguous`; the summary shows 3 streams and 32 events.
- **Classification:** hand-made manifest only.
- **Fix:** compare resolved paths.

**F11. FOLLOW-UP.** A manifest with one entry removed exits 0. If an id's second carrier sat in the dropped file, it writes that id as found, a wrong row.
- **Evidence:** `s1-0000ff02`: `ambiguous` with both files listed, found with the lane's entry dropped.
- **Contract mapping:** D-5 does not require the manifest to be complete. The manifest carries `totals.sources` and per-entry counts the view could check.
- **Classification:** hand-made input only.

**F12. FOLLOW-UP.** Two entries swapped, each sha256 kept consistent with its file: exit 0, and every row's `src` is wrong.
- **Fix:** each event's own `src` would catch it — refuse an event whose `src` differs from its entry's. Hand-made input only.

**F13. FOLLOW-UP.** Four inputs exit 1 (traceback), not 2 as D-5 asks; nothing is written in any of them (Q7a to Q7d).
- **Reach:** the real exporter never produced a depth the view could not read.
- **Fix:** catch `RecursionError`, `TypeError` and `ValueError` on input paths, and `OSError` in `write`, as Refused (exit 2).

**F14. FOLLOW-UP.** `--out` as a symlink to an empty directory is accepted, and the view writes into the link's target. I-11 leaves the "outside git" rule unenforced.
- **Fix:** refuse a symlinked `--out` and an `--out` inside a git work tree.

**F15. FOLLOW-UP.** The 12 surviving mutants are test gaps on D-1, D-2, D-3, D-5 and D-6 rules (table above).
- **Fix:** add the missing fixture items listed under Q8.

**F16. FOLLOW-UP.** The run test mirrors D-3's adjacency loop, so it cannot catch F1.
- **Fix:** derive the run from the fixture's hook records by call id and hook event.

**F17. INFO.** A cut body whose head ends with LF, or whose tail starts with LF, holds a blank line, the block separator.
- **Cause:** D-1's literal order. `starts` stays right; only a reader that splits on `"\n\n"` would mis-split.

**F18. INFO (report accuracy).** The builder's §2 claims "a cut JSON hook event no longer parses", and its §8 infers `hook_unparsed` of about 3.
- **Correction:** a cut inside one string value leaves valid JSON (q3b). That explains the real run's `hook_unparsed` 0 with 3 truncated hook events.

**F19. INFO.** I-4: 8 imported modules outside `scripts/` are unhashed, as D-6's wording allows.
- **Traced statically:** none of them can change an `s1.inject` row. `S1_QUESTIONS` lives in `common.py`, which is hashed.

**F20. INFO.** A non-string build commit (NaN) is copied into `summary.json` as `NaN`, which strict JSON forbids. Hand-made build only.

**F21. INFO.** One id seen before its state ends refuses the whole view. D-3 asks for this fail-closed behaviour.

**F22. INFO.** A request line that is not last makes `whole` false, and the candidate keeps the request line and the trailer. The build does the same (`equal`).

**F23. INFO. INFERRED, not reproduced.** A crash between the two output writes leaves `view.jsonl` without `summary.json` (I-15).

**F24. INFO (adjacent, exporter).** At JSON nesting depth 986 the exporter crashed while encoding. At 990 to 2,000 it exported 3 of 4 records, without the attachment. I did not check whether the exporter counts that drop.

**F25. INFO.** With duplicated call ids, `step_event` is the last call before the run (N10). D-3 does not say which.

## Evidence demand 5: the blocking predicate applied

| Finding | 1 Contract | 2 Real path | 3 Material on real data | 4 Discriminator | 5 Owned here | Blocks? |
|---|---|---|---|---|---|---|
| F1 | D-3's procedure followed; its rationale and the headline broken | yes, on built orders | UNVERIFIED | `measure_d3`, q1/q1b | no (D-3 amendment) | no; a CONTRACT-DEFECT if counted |
| F2 | same as F1 | yes, on a hypothetical order | UNVERIFIED | O6 / `measure_d3` | no | no; a CONTRACT-DEFECT if counted |
| F3 | D-2's procedure followed; demand 2 and the headline broken | yes | UNVERIFIED (unlikely: needs more than 3.4x JSON escaping growth) | q3b / `measure_d3` | yes | no; NOT-READY if counted |
| F13 | D-5's "exit 2" broken | hand-made exports and an operator error | none: nothing is written either way | Q7a to Q7d | yes | no (hypothetical misuse) |
| F11, F12 | D-5 does not require it | hand-made manifests | wrong rows, on hand-made input only | reproduced | yes | no (defence in depth) |
| All others | none, or conformant | — | — | — | — | no |

## Reproduced vs static vs skipped

**Reproduced:**
- the premise, at start and at end;
- the builder's tests twice, and `set-id`;
- Q1 to Q7, all through the real exporter and the view CLI, or the module functions over real exports;
- 27 new mutants, and the M1/M2 spot checks;
- pyflakes (rc 0 on all four files) and the separator check (0 on all four);
- the D-0 read-set diff (0 lines);
- the I-4 closure;
- `measure_d3` on 7 fixtures.

**Static:**
- F19's "cannot change a row";
- F23;
- the harness's real record order. There is no committed measurement, and I may not read real transcripts.

**Skipped:**
- **The real export and build:** forbidden. The coordinator's real-run counts are internally consistent: 1087 + 4 = 1091 carriers; 724 + 4 = 728 PreToolUse; 323 + 724 + 4 = 1051 `step_found`; 30 + 1061; 220 + 871; 431 + 660; 432 + 659.
- **The builder's other 34 mutants:** not my brief.
- **The builder's mutation driver:** it sits in the shared scratchpad root, which I do not read.
- **`ap_screen`:** the builder's gate.

## Hygiene

- **The main tree:** I wrote no tracked file. Its tracked changes at the end are other sessions' edits, none in the premise list: the skills, `docs/08_DECISION_LOG.md`, `docs/INCIDENT-LOG.md`.
- **A trimmed output:** one output was trimmed by a plugin that pointed at an archive under `.jev/`. I did not read it; I re-ran into my own file.
- **Disk:** I deleted my two 250 MB copies (`<W>/pin`, `<W>/mut`) to free space (92% to 90%).
- **Re-running my scripts:** recreate the copy with `git -C /home/user/agent-factory archive 3d05e645 | tar -x -C <W>/pin`, or set `VFY_TREE=/home/user/agent-factory`. The code there is identical to the PIN.

## Files

All are in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vfy444-02lBWH/`:
- `measure_d3.py`: the coordinator's check (sha256 prefix `c164711747e6be4d`).
- `h.py`: the fixture harness.
- `mutants.py` and `mutants.out`: the mutant run and its full output.
- `q567.out` and `q4.out`: probe outputs.
- Q1: `q1_orders.py`, `q1b_interleave.py`.
- Q2 and Q3: `q2_carrier.py`, `q3_candidate.py`, `q3b_cut.py`.
- Q4 to Q7: `base.py`, `q4_render.py`, `q567.py`.
- Survivor probes: `survivors.py`.