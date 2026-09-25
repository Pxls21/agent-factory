# K265 report: the Laya fan-out puts the subject first (task #265, AF-AP-208)

Lane: code-implementer (sandbox, Opus 5.5). Started 2026-09-25 11:2xZ, finished 12:0xZ. PIN 157ddd6 (my two files are
byte-identical at 157ddd6, ce2e1c5 and the local head a6dfcca). No git writes, no network, no PC bridge; the live Laya
server (127.0.0.1:47411) was never sent a request.
Boundary: MODIFY `scripts/laya_systemone_server.py`, `tests/test_laya_systemone_server.py`; CREATE this report. Nothing
else was written (scratch: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k265/lane/`).

## 0. Outcome

- **DONE (in boundary):** the three contract items are built. The new tests are red on the PIN's server
  (`7 failed, 15 passed`) and green on mine (`22 passed`, twice, set `0bd8d4de212b`). 16 of 16 non-equivalent mutants
  are killed. The venv tests use the real builder and tokenizer: the chunk the server sends is read whole, and the same
  request in the PIN's order loses it.
- **Merge BLOCKED by a test outside my boundary (measured):** `tests/test_laya_ft.py::test_ap_state_is_the_servers_fan_out_shape`
  passes at the PIN and fails with this change. It runs everywhere (no venue gate), so CI's `tests` job will go red.
  It fails for two reasons. (1) Its fake agent has no tokenizer, and `laya` is not installed in the default
  interpreter: `ModuleNotFoundError: No module named 'laya'` at line 138 of the rev-1 server (`import laya.common`; a working-tree state, never committed). (2) It pins
  the PIN's order, `list(seen[0]) == ["query", "chunk"]`, which the contract changes: the server now sends
  `['chunk', 'query']` (measured, `_chunk_state`). The test encodes a train/serve invariant: the fine-tune `ap` state
  (`scripts/laya_ft/build_dataset.py`, `{"query", "chunk"}`) equals the server's fan-out shape. The coordinator must
  choose: change the dataset order (and that test), or narrow the contract. I did not touch either file.
- The gate recommendation is not mine to give.

## 1. Premise re-measure (verified, this session, 11:3xZ): MATCHES; no CONTRACT-INVALID

```
$ sha256 (cut -c1-16) of each file at ce2e1c5, 157ddd6, HEAD (acbc9e4 then) and the working tree: identical
cba055a9dc33de21  scripts/laya_systemone_server.py
f628ce5adb9d3eaa  tests/test_laya_systemone_server.py
$ git diff --stat ce2e1c5 HEAD -- <both files>        -> empty; 157ddd6 vs ce2e1c5 changes only transcripts/sandbox/chat-2026-09-25.md
$ sed -n '130,144p' scripts/laya_systemone_server.py | grep -n 'system_one(dict'        (the PIN's bytes)
10:        one = State.agent.system_one(dict(base, chunk=chunks[qid]), {qid: q})
$ bash scripts/test_summary.sh tests/test_laya_systemone_server.py
pytest-summary: 16 passed in 0.04s
$ bash scripts/pc_suite.sh set-id -- tests/test_laya_systemone_server.py
1 files set=0bd8d4de212b
$ (the PIN's test file vs a copy of the PIN's server with dict({"chunk": chunks[qid]}, **base); scratch k265/lane/blind)
16 passed in 0.04s                                  <- the existing suite cannot see the order (reproduced)
$ /root/venv-laya-probe/bin/python k265/lane/premise_probe.py   (tokenizer only; C.DEFAULT_MODEL_DIR; synthetic: context
  900 chars, task 600, 53 history entries of 1,310-char text, command, one diagnostics line, a 20-line chunk)
{"max_len": 1024, "head_max_len": 256, "state_chars": 74526, "decode_roundtrip": true, "chunk_kept_current_order": false,
 "chunk_kept_subject_first": true, "subject_first_order": ["chunk", "command", "diagnosticsAndResults", "task", "context", "history"]}
$ grep ... bridge.mjs output.ts
scripts/jev_pipes/bridge.mjs:26:  maxStateTokens: 25_000,
vendor/jev-pruner/src/output.ts:10:const DEFAULT_MAX_STATE_TOKENS = 25_000;
```

Probe method: the kept state tokens are `ids[empty-1:len(ids)-1]` of the real `laya.common.build_sequence`. The chunk
counts as kept when its JSON-escaped text is a substring of their decode (`clean_up_tokenization_spaces=False`). The
decode of the whole tokenized state equals the state text (`decode_roundtrip: true`), so the decode shows what the model
reads. My state is 74,526 characters against the brief's 70,806 (my synthetic history is a little longer); the verdicts
match.

## 2. The brief's question: how the pruner treats a refused request and a missing answer (verified by reading)

- A refused request (any non-2xx): `parseJevResponse` throws `Jev request failed (<status>): <first 200 chars>`
  (`vendor/jev-pruner/src/jev.ts:105-107`, `if (!ok)`). In the chunk pass, `trimOutputAttempt` rethrows the rejected request
  (`vendor/jev-pruner/src/output.ts:432`, `throw response.reason`) and its catch rethrows (`output.ts:450`, `throw error`). The ONE exception is a message that
  contains `max_tokens_exceeded` (`output.ts:371-372`, `output.ts:441`, `maxTokensExceeded(error)`): the pruner then retries the whole attempt with
  half the state budget, up to two more times. The plugin hook's catch returns the original tool result unchanged
  (`decision = 'hook_error'`, `vendor/jev-pruner/hooks/fast-jev-output.ts:270-273`). The P1 replay bridge counts a
  non-2xx as the `non_200` trip and passes the original text through (`scripts/jev_pipes/bridge.mjs:112-117`,
  `bridge.mjs:303-308`, `out.fail_open = true`).
- A missing answer (a 2xx whose `answers` lack a chunk id, or a non-finite noul): `noulAnswer` throws
  `Invalid Jev answer for` (`jev.ts:138`), reached from `output.ts:435` (`noulAnswer`); the same rethrow and the same hook catch.
  The bridge counts it as the `incomplete` trip (`bridge.mjs:120-125`). The server never sends one: `do_POST` answers
  502 when the answer ids differ from the question ids (`scripts/laya_systemone_server.py:235-236`, `self._send(502`; lines 231-233 in rev 1).
- The refinement pass (`shrinkChunkWithJev`) catches any throw and keeps the chunk whole (`output.ts:646-648`, `return undefined`).

Which refusal keeps the output: every non-2xx refusal and every missing answer fail open; the agent sees its original
output. Only a refusal whose text contains `max_tokens_exceeded` costs more: the client retries up to twice before it
fails open. For an over-long chunk that retry cannot help, because the chunk's size comes from `chunkLines` /
`chunkChars`, not from `maxStateTokens`. So the fit refusal goes through the handler's existing 500 path
(rev 1: the generic `self._send(500` branch; rev 2 answers 422, R2), and its text never contains `max_tokens_exceeded`. A unit test holds both.

## 3. Design as built (files:lines are the working tree)

`scripts/laya_systemone_server.py` (45 lines changed, `git diff --stat`: 1 file, the other +384/-29 is the test):

- `:8-20` the module docstring's PER-CHUNK FAN-OUT paragraph now says what the code does (contract 3).
- `:136-139` `_laya_common()`: imports `laya.common` where the model runs (the Laya venv). It is resolved per request
  (a cached import), so `scripts/laya_ft/evaluate.py`, which sets `State.agent` without `load_agent`, keeps working. The
  model-free tests replace this function.
- `:142-147` `_chunk_state(state, text)`: `chunk` first, then the request's other fields except `chunks` and `chunk`,
  sorted by `len(json.dumps(value, ensure_ascii=False))`, a stable sort, so ties keep the request's order (contract 1).
- `:150-157` `_kept_tokens(tok, cfg, q, state, common) -> (kept, own)`: the Fitter's verdict rearranged
  (`scripts/laya_ft/build_dataset.py@157ddd6:467-468`, `fits`: whole iff the built length equals the empty-state length plus the
  state's own tokens). Called the way `Agent.system_one` calls the builder: `cfg.get("max_len", 512)`,
  `cfg.get("head_max_len", 192)`, the builder's own tokenization (the mask token blanked, no special tokens). Nothing is
  imported from `scripts/laya_ft/` (contract 2: reuse the verdict, not the module).
- `:160-179` `_answer`: the one-call path is unchanged (`:163-164`). In the fan-out path, every chunk alone
  (`{"chunk": text}`) is checked under its own question (`agent._to_internal(q)`) with the loaded agent's `tok` and
  `cfg`, BEFORE the model is asked about any chunk (`:165-170`). A misfit raises
  `ValueError("chunk %r does not fit Laya's window whole: %d of its %d state tokens kept; no chunk was asked")`. The
  handler's existing path answers it as 500 `system_one failed: ValueError: ...` (`:229-230`); `State.calls` does not
  move. Then each chunk is asked on `_chunk_state(state, chunk)` (`:174`).
- `Handler.do_POST` is unchanged. GitNexus lists the Handler methods as changed only because the docstring moved their
  lines.

Interpretations, stated so the coordinator can overrule them:
1. "the length of their JSON serialization" = the VALUE's JSON as Laya writes it (`ensure_ascii=False`, Laya's
   `serialize_state`), without the key. A unit test pins it (`diagnosticsAndResults: []` sorts first: 2 characters,
   27 with its key); the key-plus-value mutant M5 is killed.
2. A request-level `chunk` field gives way to the subject, as `dict(base, chunk=...)` did at the PIN. Without this, the
   request's `chunk` value would overwrite the subject in the first position (mutant M8, killed).
3. All chunks are checked before the first model call, not interleaved. A refused request therefore spends no forward
   pass and answers nothing (mutant M11, killed).

## 4. Tests (verified; counts pasted verbatim)

Red first, the new tests on the PIN's server (the working tree server was still `cba055a9dc33de21`):

```
$ bash scripts/test_summary.sh tests/test_laya_systemone_server.py            (11:45:58Z; scratch red.log)
pytest-exit: 1
pytest-summary: 7 failed, 15 passed in 7.86s
```

Each of the 7 fails for the expected reason:

| test | failure on the PIN |
|---|---|
| `test_chunk_state_puts_the_subject_first_then_the_fields_by_json_length` | `AttributeError: ... no attribute '_chunk_state'` (the function under test does not exist) |
| `test_answer_fans_out_each_named_chunk_without_reusing_batch_state` | the ORDER: sent `{"context": ..., "history": [...], "task": ..., "chunk": "routine output"}`, expected `{"chunk": "routine output", "task": ..., "context": ..., "history": [...]}` |
| `test_answer_refuses_the_whole_request_when_one_chunk_does_not_fit_alone` | `Failed: DID NOT RAISE ValueError` |
| `test_handler_refuses_a_chunk_that_does_not_fit_through_its_500_path` | `At index 0 diff: 200 != 500` |
| `test_fit_check_reads_the_agents_own_window_and_the_asked_question` | `Failed: DID NOT RAISE ValueError` |
| `test_laya_builder_reads_the_whole_chunk_the_fan_out_sends` (venv) | `assert ('context' == 'chunk'`: the PIN's state starts with `context`; its incident-shape guard held (> 70,000 characters, not whole) |
| `test_fit_check_is_the_builders_verdict_at_the_window_edge` (venv) | `AttributeError: ... no attribute '_kept_tokens'` |

The 15 that pass on both: `test_pick_device_matrix` (12), the chunk map, the revision guard, and
`test_answer_falls_back_once_for_a_question_without_a_matching_chunk` (the one-call path is unchanged, so it is green on
both by design).

Green, on my server, twice (11:46:48Z and after the mutation pass):

```
$ bash scripts/test_summary.sh tests/test_laya_systemone_server.py
pytest-exit: 0
pytest-summary: 22 passed in 9.41s
$ bash scripts/test_summary.sh tests/test_laya_systemone_server.py
pytest-exit: 0
pytest-summary: 22 passed in 9.63s
$ bash scripts/pc_suite.sh set-id -- tests/test_laya_systemone_server.py
1 files set=0bd8d4de212b
```

Venue states of the two venv tests (fixture `laya_venue`, `tests/test_laya_systemone_server.py:382-401` now, the
`tests/test_laya_ft.py` pattern; the declared inputs are the Laya python, the served checkpoint's
`rl_agent_config.json` and `tokenizer/tokenizer.json`):

```
S0_01_VENUE unset (CI):  20 passed, 2 skipped   SKIPPED [1] ...:401: LOUD SKIP: the Laya venv and snapshot are declared inputs ...
S0_01_VENUE=pc:          20 passed, 2 skipped
S0_01_VENUE=sandbox, LAYA_PY pointed at a missing file (scratch copy):
                         20 passed, 2 errors    E  Failed: declared input missing on the sandbox venue: ['/root/venv-laya-probe/bin/python-absent']
```

What each new test holds (`tests/test_laya_systemone_server.py`):
- `:130-150` the ORDER of `_chunk_state`'s output (`list(out)` and its exact JSON text): the subject first, a tie in
  the request's order (`zz` before `aa`), the value's JSON length, not `len()` (`[10]`), not ASCII-escaped
  (`ééé`: 5, not 20), not key plus value; `chunks` and a request-level `chunk` dropped; the request not mutated.
- `:153-188` the fan-out through `_answer`: each recorded state's exact JSON (order-aware), one question per call, and
  the fit check on each chunk alone under its own question, all before the first model call. The fixture's history
  makes the whole per-chunk state overflow the fake window while each chunk fits alone. A chunk holds `é` and `[MASK]`,
  so a wrong own-token count refuses it.
- `:191-204` the one-call path: the same bytes and key order (`json.dumps` equality), for a dict and for a string
  state; no fit check runs.
- `:207-220` the refusal: `ValueError` with the exact reason, no model call at all (a fitting chunk before the misfit is
  not asked either), and no `max_tokens_exceeded` in the text.
- `:223-250` the handler, socket-free (`Handler.__new__`, in-memory `rfile`/`wfile`): 500 with the exact error body,
  `State.calls` unchanged; then the positive control, 200 with `fan_out` 2 and `State.calls` 1.
- `:253-268` the window and the question come from the agent: `cfg` 32/8 refuses (26 of 33 kept); an empty `cfg` uses
  512/192; the builder saw `agent._to_internal(asked question)`.
- `:401-410` (venv, real builder and tokenizer, a recorder in place of the forward pass): a pruner-shaped request (53
  history entries, 73,620 characters) through `_answer`. The sent state starts with `chunk` and is read whole. The same
  request in the PIN's order (`dict(base, chunk=...)`) loses the chunk. An oversize chunk refuses the whole request, and
  the model is asked nothing.
- `:444-452` (venv) at the window's edge, for 10 chunk endings: the longest chunk that fits alone is whole by the check
  AND by an independent unbounded build (the `tests/test_laya_ft.py` FIT_CHECK oracle), and it is read whole inside the
  server's per-chunk state ahead of a 70,000-character request. One character longer, it is refused and not whole.

Measured data behind the two venv tests (their own scripts, run outside pytest; scratch `show_venv.py`):

```
THROUGH_THE_FAN_OUT {"keys": ["chunk", "category", "command", "diagnosticsAndResults", "categoryGuidance", "task", "context", "history"],
 "state_chars": 73620, "whole_state_fits": false, "chunk_seen": true, "chunk_seen_in_pin_order": false,
 "refused": "chunk 'c2' does not fit Laya's window whole: 811 of its 2003 state tokens kept; no chunk was asked",
 "asked_after_refusal": 0, "over_seen_even_alone": false}
AT_THE_WINDOW_EDGE (kept, own, unbounded-whole) at the edge / one character over, 10 endings:
 letter [811,811,true]/[811,812,false]  dot [810,810,true]/[811,812,false]  paren [810,810,true]/[811,812,false]
 quote [811,811,true]/[811,812,false]  newline [811,811,true]/[811,813,false]  digit [811,811,true]/[811,813,false]
 accent [811,811,true]/[811,812,false]  ellipsis [811,811,true]/[811,812,false]  backslash [811,811,true]/[811,812,false]
 brace [811,811,true]/[811,812,false]; seen_in_server_state true for all 10
```

## 5. Mutation pass (verified; scratch `mutate.py`, log `mutate.log`)

Each mutant ran in its own scratch tree with the lane's test file (never the shared tree), with
`PYTHONDONTWRITEBYTECODE=1` and `S0_01_VENUE=sandbox`, so the venv tests ran too. Every mutant compiled
(`py_compile`); a kill is a named failing test. The expected count is a literal: 16.

| mutant | verdict | killed by |
|---|---|---|
| M0 identity (control) | 22 passed, as required | — |
| M1 chunk last (the PIN's order) | KILLED (4) | fan-out, `_chunk_state`, both venv tests |
| M2 no sort | KILLED (2) | fan-out, `_chunk_state` |
| M3 sort by `len(value)` | KILLED (2) | fan-out, `_chunk_state` |
| M4 `ensure_ascii` default | KILLED (1) | `_chunk_state` |
| M5 key plus value length | KILLED (1) | `_chunk_state` |
| M6 longest first | KILLED (2) | fan-out, `_chunk_state` |
| M7 tie broken by key | KILLED (1) | `_chunk_state` |
| M8 request-level `chunk` kept | KILLED (1) | `_chunk_state` |
| M9 no fit check | KILLED (4) | refusal, handler, window, venv fan-out |
| M10 check the full per-chunk state | KILLED (4) | fan-out, refusal, handler, venv fan-out |
| M11 check then ask, per chunk | KILLED (4) | fan-out, refusal, handler, venv fan-out |
| M12 default window (512/192) | KILLED (5) | refusal, window, handler, both venv tests |
| M13 a generic question | KILLED (2) | fan-out, window |
| M14 mask not blanked in the own count | KILLED (1) | fan-out |
| M15 own count from ASCII JSON | KILLED (2) | fan-out, venv edge |
| M16 window arguments swapped | KILLED (1) | window |
| M17 `kept < own` for `kept != own` | 22 passed: EQUIVALENT (kept <= own always) | — |

```
EXPECTED_KILLED=16 KILLED=16 SURVIVED=0 INVALID=0
```

## 6. Timing (verified; scratch `timing.py`)

The fit check's added cost per chunk: `server._kept_tokens` exactly as `_answer` calls it, with the real tokenizer and
window and a pruner-shaped question. Sandbox CPU (4 cores, load 1.9 to 2.4, a live server and another lane on the box).
Median of 30 after 3 warm-ups (`perf_counter`), two runs:

```
typical 20-line chunk  1,430 chars    523 tokens (fits)     median 2.535 ms / 2.550 ms   (p90 2.616 / 2.713)
edge chunk             2,450 chars    811 tokens (fits)     median 3.534 ms / 3.584 ms   (p90 3.605 / 3.670)
worst case            40,009 chars 16,163 tokens (refused)  median 45.444 ms / 46.557 ms (p90 49.349 / 58.587)
```

So a 16-chunk pruner request of typical chunks adds about 40 ms of checks against the pruner's 2 s budget. A refusal
stops at the first misfit.

## 7. Consumers of the change beyond the handler (verified unless tagged)

GitNexus `impact` on `Function:scripts/laya_systemone_server.py:_answer` (upstream): 1 direct caller,
`Handler.do_POST`, risk LOW; graft agrees. GitNexus `detect_changes --scope all`: risk low, 0 affected processes. A
literal sweep (the Grep tool) found what the graph cannot see:

- `tests/test_laya_ft.py:95-110` (`test_ap_state_is_the_servers_fan_out_shape`) breaks (section 0). Measured in a scratch copy of the tree with the PIN's server:
  `1 passed`; with mine: `1 failed` (`ModuleNotFoundError: No module named 'laya'`, line 138 of the rev-1 server, `import laya.common`).
  In the repo: `env -u S0_01_VENUE python3 -m pytest tests/test_laya_ft.py` -> `1 failed, 27 passed, 14 skipped`
  (only this test fails).
- `scripts/laya_ft/evaluate.py:174-181` (`C.load_module`) calls the server's `_answer` in process for J2's scorers. The `ap` run
  (`docs/research/findings/ap-hawk-probe/ap_probe.py:111-113`, `INSTRUCTION`) and the `jev_noul` method of `v1` and `v1_full`
  (`docs/research/findings/j2-v1-probe/v1_probe.py:97-99`, `CLASSES`) take the fan-out path. With the tokenizer only, 1,600 ap,
  600 v1 and 600 v1_full per-chunk states are whole in BOTH orders, and none is refused, so J2's verdicts were not hit
  by AF-AP-208. But the key order changes the model's input, and `evaluate.py`'s no-checkpoint positive control demands
  every number equal the committed J2, J2c and AP results exactly (`scripts/laya_ft/evaluate.py:59-71`, `compare`, exit 2).
  NOT run: it loads the model (a second 2.7 GB copy beside the live server's; 5 GB free, load 5.4 at the time).
- `tests/fixtures/jev_pipes/answers.jsonl` was recorded from the live server at the PIN
  (`tests/fixtures/jev_pipes/record_answers.py`); the replay tests replay it, so they stay green, but it no longer
  describes the server's behavior once the server restarts on K265.
- The adjacent client suites use stand-ins, not the real module, and stay green:
  `bash scripts/test_summary.sh tests/test_jev_client.py tests/test_jev_context.py tests/test_jev_pipes_replay.py
  tests/test_hiccup_scan.py tests/test_jev_locate_echo.py tests/test_decide_harvest.py --basetemp /tmp/k265bt/bt` ->
  `pytest-summary: 313 passed in 94.57s (0:01:34)`.
- `tests/test_jev_context.py:270-272` pins `_chunk_map` at line 118. The docstring grew six lines, so the function is
  now at `scripts/laya_systemone_server.py:124` (`_chunk_map`). The pin is a captured fixture string (`CBM_OUT`, parsed by
  `jc.parse_cbm`); nothing reads the live file, so nothing breaks. (My earlier draft said the line would not move; that
  was wrong, corrected here.)

The refusal rate on real pruner chunks (inferred from VERIFY-P1's recorded counts, `verify-p1/probe/states40.jsonl`,
numbers only; not re-measured through the K265 code): 1,474 per-chunk states of 40 of the 254 scored P1 results, room
855 with the real pruner questions, chunk tokens min 5, p50 355, p90 720, max 2,585. 79 of 1,474 chunks do not fit
alone (the framing estimate +4 to +8 tokens gives the same count), so 54 of 366 requests would be refused, and 9 of 40
results would pass through unpruned because one chunk is too long. The pruner's line mode makes such chunks (20 lines,
lines up to 2,000 characters: `scripts/jev_pipes/bridge.mjs:24` `chunkLines`, `vendor/jev-pruner/src/output.ts:14,146-189` `MAX_LINE_CHARS`).

## 8. The echo (report only; nothing outside the boundary fixed)

Instruments: graft first. `graft ask "who calls system_one"` and `"who calls build_sequence"` return no structural
edges, since both names live in `laya`, outside the repo. Then `graft grep` for the senders
(`system_one|/v1/systemone|build_sequence|systemone`: 117 hits, 75 symbols, 30 files), for the `jev.py` API callers
(45 hits, 7 files) and for the construction itself (`dict(base, chunk|chunk=chunks[|"chunk": ...`: 22 hits, 10 files).
The Grep tool swept literal module references and line citations. Each shape was measured through the real
`laya.common.build_sequence` and tokenizer (tokenizer only) where the reader is in the sandbox.

| # | site | reader | subject position | measured through the builder | verdict |
|---|---|---|---|---|---|
| E1 | `scripts/laya_systemone_server.py` `_answer` fan-out (the pruner, via `scripts/jev_pipes/bridge.mjs`) | Laya 1024/256 | PIN: `chunk` last, behind up to 53 history segments | VERIFY-P1: 1,474 of 1,474 chunks cut; my probe: lost (PIN), whole (K265) | FIXED by K265 |
| E2 | `scripts/jev.py` `rank` -> the same fan-out; callers `scripts/jev_context.py:789-823` `jev_rank`, `scripts/hiccup_scan.py:615-648` `jev_column` | Laya via the server | PIN: `{"query" (<= 1,000 chars), "chunk"}`: a 1,000-character CJK or Hindi query alone exceeds the room | 60 shapes (`jev._build` + K265 `_answer`; VERIFY-JT1R1-JT2's generator): PIN chunk whole 18/60; K265: 15 refused, 45 answered, all 45 with the whole chunk, 0 without it; the QUERY whole in only 20 of the 45 | A PIN instance (VERIFY-JT1 F-24 found it; the client's cuts and all-equal refusal mitigated it); K265 fixes the chunk side, and the query is now the field cut |
| E3 | `scripts/laya_ft/evaluate.py` in-process `_answer` (ap_probe, v1_probe `jev_noul`) | Laya | PIN: `{"query", "chunk"}`, query bounded | ap 1,600/1,600, v1 600/600, v1_full 600/600 whole in both orders; 0 refused | Not an instance; the order change alters the model's input (section 7) |
| E4 | `scripts/qwen_jev.py:355-358` `JevService.systemone` | Qwen3.8-27B through simple-jev's `PromptCompiler` (default budget) | `dict(base, chunk=...)`: the PIN's construction verbatim, `chunk` last | NOT measured: simple-jev lives only on the PC (`~/simple-jev`), and the bridge is out of bounds | UNSURE: an instance if that compiler cuts a long state from the right; if it refuses, it fails loud |
| E5 | `docs/research/findings/j2b-variants/openjev_j2.py:83-99` `make_post` (reused by `rwkv7_g0.py` with `max_tokens=65536`) | OpenJev (hosted) / RWKV-7 | `dict(base, chunk=...)`, `chunk` last | the states are the J2/AP ones: whole in Laya's 1,024 window (E3), far under 65,536; OpenJev's window not measured (hosted) | Not a live instance (historical probe; a bounded query) |
| E6 | `scripts/laya_ft/build_dataset.py` `Fitter`, `train.py:80-92`, `teacher_label.py:173` | Laya (training) / the teacher | `{"query", "chunk"}`, query first | by construction: the Fitter cuts the query until the WHOLE state fits and raises if the chunk alone overflows | Not an instance; a train/serve ORDER skew against K265 (section 0) |
| E7 | `scripts/laya_probe.py` (fixture `tests/fixtures/decisions/probe/questions.json`) | Laya | one dict | 226 states of 90-257 JSON characters | Not an instance |
| E8 | `docs/research/findings/j2b-variants/j2b.py` | Laya | one field (`incident` / `finding`) | the subject is the only field | Not an instance |
| E9 | `scripts/jev.py` `ask` / `classify` with a dict state (`json.dumps(sort_keys=True)`, then `[:4000]`) | Laya | alphabetical keys, then a head cut | no production caller passes a dict (graft grep: only tests) | Latent shape, not live |
| E10 | the vendored pruner's `stateFor` (`output.ts:191-209`, `chunks` last) sent to TypeSafe's hosted API | TypeSafe | batch form, `chunks` last | not measurable (hosted; no network) | Out of scope (vendored; its own server) |

The test half (AF-AP-208's second shape, dict equality on an order-reading consumer):
- `tests/test_laya_systemone_server.py`: fixed; every fan-out assertion compares the key list or the JSON text.
- `tests/test_jev_client.py:178` (`req["state"]`) compares the rank request's state by dict equality. That is harmless now: the server
  rebuilds each per-chunk order itself, and `ask`/`classify` send strings.
- `tests/test_laya_ft.py:95-110` compares by ORDER, and so it catches this change (section 0).
- `tests/test_decide_harvest.py:1169` quotes a historical report sentence (VERIFY-JT1 F-24, "query first") as a
  fixture; no action.

## 9. Self-attack: the three most likely ways this change is wrong

1. **The chunk-only verdict could differ from the chunk's survival inside the full per-chunk state at a token edge**
   (a BPE merge across the closing quote). Checked: at the window edge, 10 endings (letter `.` `)` `"` newline digit
   `é` `...` backslash `}`) are each whole inside the server's state ahead of a 73,620-character request, and one
   character more is refused (`test_fit_check_is_the_builders_verdict_at_the_window_edge`). The alphabet is those 10
   endings on one base text. It is not proven for every merge in the vocabulary.
2. **The unit tests' fake window mirrors my own reading of `build_sequence`.** Checked: both venv tests run the real
   builder and tokenizer. Two independent oracles agree with the check: the decode of the kept tokens, and an
   unbounded build (`tests/test_laya_ft.py`'s FIT_CHECK). M1, M12 and M15 die in the venv tests too.
3. **The check could run on a window or question other than the ones `system_one` uses.** Checked: `_kept_tokens`
   reads `agent.cfg` with `system_one`'s defaults and gets `agent._to_internal(q)` per chunk. The window test pins the
   arguments the builder sees, and M12, M13 and M16 are killed.
   The larger risk is not in the code but in the contract's reach: the reorder breaks an out-of-boundary train/serve
   test, may move `evaluate.py`'s exact positive control, and makes the query the field `jev.py` rank loses
   (sections 0, 7 and 8).

## 10. NOT done (first-class)

- `tests/test_laya_ft.py::test_ap_state_is_the_servers_fan_out_shape`: NOT fixed (out of boundary). The merge is
  blocked until the coordinator decides (section 0).
- `scripts/laya_ft/evaluate.py` no-checkpoint positive control (v1, v1_full, ap) on the new order: NOT run (it loads
  the model). Command: `HF_HUB_OFFLINE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/evaluate.py --only v1,v1_full,ap --out-dir <scratch>`.
- The refusal rate on real pruner chunks through the K265 code: NOT measured (section 7 is an inference from counts).
- The live server: NOT restarted (the coordinator's step after the verify round); its answers file
  (`tests/fixtures/jev_pipes/answers.jsonl`) NOT re-recorded.
- E4 (the Qwen adapter's compiler budget): NOT measured (PC only).
- No server-side log of the refusal reason: the 500 body carries it, but `log_message` writes only the request line, a
  pre-existing gap for every 500. NOT changed (the contract says to use the existing path).

## 11. DISCREPANCIES and deviations (loud)

- D1 (conflict with a consumer): the contract's order breaks `tests/test_laya_ft.py:95-110` (`test_ap_state_is_the_servers_fan_out_shape`) and the fine-tune `ap`
  order (`scripts/laya_ft/build_dataset.py:20`: "the state `{"query": entry, "chunk": row text}` (the local server's
  per-chunk fan-out shape, the one J2 scored)"). That docstring is now false for the current server.
- D2 (comments my change falsifies, outside my boundary, not fixed): `scripts/jev.py:14-16` (`rank`: "the server puts the query
  first, so `rank` cuts the query to 1,000 characters"); `scripts/qwen_jev.py:387` (`Mirrors` the server's lines
  118-127; `_chunk_map` is now at lines 124-133). Older reports cite the PIN's lines
  (e.g. `tasks/briefs/jev-pipes/P1-report.md:41,50` and `tasks/briefs/jev-laya/JT2-report.md:54`, on `_answer`): historical, correct for
  their time.
- D3 (a client-side interaction): on `--venue auto`, `jev.py` treats the local 500 as "unavailable" and tries the PC
  endpoint next (`scripts/jev.py` `_ask_venues`). If the PC's server still runs the PIN's code, the PC answers without
  the check. That holds until both servers run K265.
- D4 (a count, not a contradiction): the AF-AP-208 row says the ap-hawk probe had "300 of 300 states whole"; I measured
  all 1,600 (100 incidents x 16 rows), all whole in both orders.
- D5 (an interpretation): the sort key is the value's JSON without the key (section 3, interpretation 1).
- Deviation: none from the boundary. The test file grew from 16 to 22 tests. I kept the two old fan-out test names
  (now order-aware); `Recorder` gained `tok`, `cfg` and `_to_internal`.
- Tool quirks hit: the Write tool turned my typed `é` escapes into literal `é` bytes (6; same meaning, 0 separator
  bytes; the AF-AP-132 family). My first adjacent-suite run used `--basetemp /tmp/k265bt/bt` without creating
  `/tmp/k265bt`, which gave 191 setup errors; the CLAUDE.md quirk, re-run clean. `graft ask` has no structural edges
  for names defined in `laya`; `graft grep` answers them.

## 12. Evidence tiers

- Verified (this session, primary source or probe): sections 1, 2, 3, 4, 5, 6; the section 7 bullets except the
  refusal rate; E1-E3 and E5-E9 in section 8.
- Inferred: the P1 refusal rate (section 7, from VERIFY-P1's recorded counts); "about 40 ms per 16-chunk request"
  (16 x the typical median).
- Assumed / not measured: that `evaluate.py`'s positive control moves (it may not: the discrete top-1 and top-3 rates
  can survive a small score change); E4 (the Qwen compiler); E10 (TypeSafe's window).

## 13. Gates run on the final files

```
$ sha256 (cut -c1-16) of the final files (12:07Z)
c7d48e0364e7977d  scripts/laya_systemone_server.py
163576313857e73e  tests/test_laya_systemone_server.py
$ bash scripts/test_summary.sh tests/test_laya_systemone_server.py      (the third green run, after every edit)
pytest-exit: 0
pytest-summary: 22 passed in 10.44s
$ python3 -m pyflakes scripts/laya_systemone_server.py tests/test_laya_systemone_server.py        -> rc 0
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>   -> 0 scripts/laya_systemone_server.py, 0 tests/test_laya_systemone_server.py, 0 this report
$ python3 scripts/ap_screen.py <both files>        -> 6 hits; 5 are the PIN's (the server's os.environ writes and reads in
  load_agent/main, `t0 = time.time()` in do_POST, at moved lines); the new one is the venue read
  `tests/test_laya_systemone_server.py:384` now (AP-1, `S0_01_VENUE`), copied from tests/test_laya_ft.py's declared-venue fixture
$ python3 scripts/ap_screen.py --tests <both files> -> 3 hits; 2 are the PIN's (VERIFY-T92 classed both by-design); the new one
  is `handler.headers` at `tests/test_laya_systemone_server.py:310` now (AP-66), set on the local object `_post` builds, so
  nothing leaks between tests
$ node .gitnexus/run.cjs detect-changes --scope all --repo .   -> risk low, 0 affected processes
$ python3 scripts/report_lint.py tasks/briefs/jev-pipes/K265-report.md --map jev.ts=vendor/jev-pruner/src/jev.ts \
    --map output.ts=vendor/jev-pruner/src/output.ts --map bridge.mjs=scripts/jev_pipes/bridge.mjs --min-refs 30   (rc 0)
report_lint: 45 refs — OK 44, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
  (the one UNCHECKABLE is a verbatim grep output line pasted in section 1's premise block)
```

---

# rev 2 (AMENDMENT 1, contract rev 2; started 2026-09-25 12:1xZ)

Sections 0-13 above are the rev-1 record, kept as history. The rev-1 design (chunk first, shortest fields next) is replaced:
the server keeps the PIN's order (the training shape) and fits each per-chunk state with the dataset builder's own fit.

## R0. Outcome (rev 2)

- **DONE (in boundary):** the six items of contract rev 2 are built (R2). One fit function,
  `scripts/laya_ft/fit.py`, serves both callers: the dataset builder's `Fitter.fit` delegates to it, and the server
  runs every per-chunk state through it, in the PIN's order (the chunk last), before it asks the model about any chunk.
  A chunk that does not fit with every other field empty refuses the whole request with HTTP 422, and `scripts/jev.py`
  treats a 422 as final (fail open, exit 3, no next venue).
- **Red first on the PIN:** `10 failed, 78 passed`, each for the expected reason (R3). **Gate, twice, set
  `61999ff6f3db`:** `1 failed, 129 passed` both times, the same one failure (next bullet). CI's form: `113 passed,
  17 skipped`. **Mutation:** 29 of 29 non-equivalent mutants killed, 1 equivalent control passes (R4).
- **Train/serve identity holds, and the real data does not move.** The server's fitted state equals the builder's,
  key order included (venv test, a cut case). The v1 and v2 datasets, labels and summaries rebuild byte-identical
  (R5). J2's scorers send the model byte-identical inputs: 3,000 of 3,000 calls (R7 E3).
- **One test is red on the sandbox venue, by a committed artifact outside my boundary:**
  `test_version_2_record_rebuilds_byte_identically_at_the_pin`. The record's `dataset-manifest.json` hashes the
  builder's code, and the delegation changes that hash (and adds `fit.py`). Regenerating that one file clears it: the
  whole test passes in a scratch tree with the regenerated manifest (R8, R10).
- **Measured on the real pruner sample (R7 E1):** every chunk is now whole in its state, and 10 of 40 results fail
  open on a refused chunk. Two costs for the coordinator: the history is emptied in 1,215 of 1,242 states, and 1,073
  of 1,236 model calls repeat an input already sent in the same result. The fit costs about 87 ms per chunk at the
  median P1 prefix, 1.4 s per 16-chunk request (R6).
- The gate recommendation is not mine to give.

## R1. Premise for rev 2 (verified)

```
$ sha256 (cut -c1-16) at PIN 157ddd6 / HEAD 3c77353 / working tree
1c95e37a0d99cfa8 / 1c95e37a0d99cfa8 / 1c95e37a0d99cfa8  scripts/laya_ft/build_dataset.py
b7f96af535195683 / b7f96af535195683 / b7f96af535195683  tests/test_laya_ft.py
15cff37bd20b05fc / 15cff37bd20b05fc / 15cff37bd20b05fc  scripts/jev.py
cbeaa8e07d0dc2f5 / cbeaa8e07d0dc2f5 / cbeaa8e07d0dc2f5  tests/test_jev_client.py
71a66fd1e151698c / 71a66fd1e151698c / 71a66fd1e151698c  scripts/qwen_jev.py
cba055a9dc33de21 / cba055a9dc33de21 / c7d48e0364e7977d  scripts/laya_systemone_server.py   (my rev-1 edit)
f628ce5adb9d3eaa / f628ce5adb9d3eaa / 163576313857e73e  tests/test_laya_systemone_server.py (my rev-1 edit)
$ git log --oneline 157ddd6..HEAD -- <the five new boundary files>   -> none
```

Re-checked at 12:55Z: HEAD 7b18ad5; `git diff --stat eecd786..HEAD` over the eight boundary files and the version-2
record is empty (the commits since touch other files only).

## R2. Design as built (files:lines are the working tree)

- **One fit, `scripts/laya_ft/fit.py` (new, 83 lines, stdlib-only at import).** `fit_state(tok, q, max_len, head_max_len,
  state) -> (state, cuts)` at `scripts/laya_ft/fit.py:48-83` (`fit_state`). The verdict is the dataset builder's: a state fits when
  `laya.common.build_sequence` keeps all of its tokens (built length = empty-state length + the state's own tokens,
  mask blanked, no special tokens). Unchanged (the same object) when it fits. Otherwise: a string state is cut to its
  longest fitting prefix; a dict's fields other than `chunk` are cut, the longest serialized value first
  (`json.dumps(value, ensure_ascii=False)`, the key not counted, a tie in the dict's order; `:67-68`). A string is cut
  by characters and a list by whole entries, with the builder's own binary search (`_longest_prefix`, `:35-45`). A
  field whose empty value still does not fit is emptied, and the next field is cut. A field that is neither a string
  nor a list stays whole. The key order is kept. `chunk` is never cut: `Unfit` (`:20-26`, a `ValueError` with the
  PIN's message) when the state does not fit with every other field empty (`:81-83`). `laya` is imported only when a
  fit runs (`_laya_builder`, `:29-32`, the seam the model-free tests replace).
- **The builder delegates.** `scripts/laya_ft/build_dataset.py:458-467` (`Fitter.fit`) calls `FIT.fit_state` and maps
  the one cut to the PIN's `{"chars_from", "chars_to"}`; `:41` imports the module; `:46-49` adds
  `scripts/laya_ft/fit.py` to `CODE` (the manifest hashes the code that shapes the data); the docstring (`:18-29`)
  names the shared fit. `Fitter.__init__` no longer keeps `_build`/`_serialize`/`_tokens` (no caller).
- **The server fits, then asks.** `scripts/laya_systemone_server.py:171` (`fitted`): every per-chunk state, built in the PIN's order
  (`dict(base, chunk=chunks[qid])`, the chunk last), goes through `_fit` (`:151-161`) before the model is asked about
  any chunk; `:175` asks with the fitted state. `_fit` passes the loaded agent's `tok`, `_to_internal(q)` and
  `cfg` lengths (the defaults `Agent.system_one` uses, 512/192). `_laya_fit` (`:141-148`) imports the module inside
  the fan-out path. `Unfit` becomes `FitRefused` (`:136-138`) with the reason; `Handler.do_POST` answers it 422
  (`:230-231`), before the generic 500. An agent with no tokenizer raises inside `_fit`: a 500, never a bypass. The
  one-call path (`:167-168`) is unchanged. Docstring `:12-20`.
- **The client treats 422 as final.** `scripts/jev.py:94-95` `Refused(Unavailable)`; `_http` (`:272`) and
  `parse_pc_reply` (`:349`) raise it on a 422 and only a 422; `_ask_venues` stops at it (`:397-398`): no next venue,
  the caller fails open (exit 3, one stderr line). The Venues paragraph says so (`:21-23`). Lines 14-16 stay: they
  are true again (the server keeps the query first).
- **Citation:** `scripts/qwen_jev.py:387` now cites `scripts/laya_systemone_server.py:124-133` (`_chunk_map`).

## R3. Red first (verified; scratch `red2.log`)

The red tree is `pinclone`: the PIN 157ddd6 with the new test files and the new `fit.py` copied in, so the server,
builder and client under test are the PIN's.

```
$ cd <scratch>/pinclone && bash scripts/test_summary.sh tests/test_laya_systemone_server.py \
    "tests/test_laya_ft.py::test_ap_state_is_the_servers_fan_out_shape" \
    "tests/test_laya_ft.py::test_fit_delegation_changes_no_dataset_output" \
    "tests/test_laya_ft.py::test_server_serves_the_state_the_builder_fits" tests/test_jev_client.py
pytest-exit: 1
pytest-summary: 10 failed, 78 passed in 36.77s
```

| test | failure on the PIN |
|---|---|
| `test_answer_fans_out_each_named_chunk_without_reusing_batch_state` | sent unfitted: `{"context": "ctx", "history": ["aaaaa", "bbbbb", "ccccc", "ddddd"], "task": "go", "chunk": "C1"}`, expected `{"context": "ctx", "history": ["aaaaa"], "task": "go", "chunk": "C1"}` |
| `test_answer_refuses_the_whole_request_when_one_chunk_does_not_fit` | `AttributeError: ... no attribute 'FitRefused'` |
| `test_handler_answers_a_fit_refusal_with_422_and_its_reason` | `At index 0 diff: 200 != 422` (the PIN answers) |
| `test_an_agent_without_a_tokenizer_is_a_500_refusal_never_a_bypass` | `assert (200 == 500)`: the PIN answers with no tokenizer at all |
| `test_the_fit_reads_the_agents_own_window_and_the_asked_question` | `AttributeError: ... no attribute 'FitRefused'` |
| `test_laya_builder_reads_the_whole_state_the_fan_out_sends` (venv) | `assert out["sent_whole"] is True` fails; its incident-shape guards passed first (the PIN's keys, > 70,000 characters, the chunk not seen) |
| `test_ap_state_is_the_servers_fan_out_shape` | `AttributeError: ... has no attribute '_fit'` (the named seam does not exist) |
| `test_server_serves_the_state_the_builder_fits` (venv) | `assert cut_case["same"] is True` fails: the PIN sends the unfitted state |
| `test_auto_treats_a_422_as_final_and_asks_no_other_venue` | the PIN's `jev.rank` goes on to the PC and returns its ranking (`venue: 'pc'`), not None |
| `test_a_422_and_only_a_422_is_final_on_both_paths` | `AttributeError: module 'jev_under_test' has no attribute 'Refused'` |

Green on both by design: the nine fit-module unit tests (the module was copied into the red tree),
`test_fit_delegation_changes_no_dataset_output` (an invariant: at the PIN, `BD.Fitter` IS the PIN's fit), the one-call
path, the chunk map, the revision guard, `test_pick_device_matrix` (12) and the client's other 54. One test was added
after this run, in the mutation pass: `test_fit_measures_a_value_by_its_json_as_laya_writes_it_without_the_key` (a
fit-module test, so it cannot be red on the PIN's server; its red is the mutants it kills, F4 and F5 below). The same
pass split the tie test into both key orders (F2) and added the refusal-with-a-dict case (F13). Venue states of the venv
tests are as in rev 1 (`S0_01_VENUE` unset: skipped loudly; `sandbox` with a declared input missing: a FAIL).

## R4. Mutation pass (verified; scratch `mutate2.py`, logs `mut2_F.log`, `mut2_SB.log`, `mut2_J.log`)

Each mutant ran in the scratch lane tree (a clone of HEAD plus the lane's files), never the shared tree: every
anchor must occur once, the file must compile, the selected tests run with `S0_01_VENUE=sandbox`, then the pristine
bytes are restored and their sha re-checked. Selection A: `tests/test_laya_systemone_server.py` plus the three
`tests/test_laya_ft.py` tests above (33 tests); selection B: `tests/test_jev_client.py` (56). The last edit to any
lane file was 12:42Z; the pass ran 12:45-12:50Z, so it covers the final files.

```
fit.py     14 of 14 killed: F1 shortest first · F2 tie by key name · F3 len(value) · F4 ASCII-escaped JSON ·
           F5 key plus value · F6 no emptying (refuse when the first field cannot absorb) · F7 no whole-state check ·
           F8 the search returns hi · F9 the chunk is cuttable · F10 mask not blanked · F11 own tokens from escaped
           JSON · F12 the refusal measures the request, not the emptied state · F13 dicts cuttable · F14 a string
           state not cut.  F15 (a reversed-list sort, EQUIVALENT) passes: 33 passed, as expected
server     8 of 8 killed: S1 the unfitted state to the model · S2 fit and ask chunk by chunk (a refusal after an
           answer) · S3 the refusal as 500 · S4 the default window, not the agent's · S5 a generic question ·
           S6 chunk first (killed by test_ap_state_is_the_servers_fan_out_shape too) · S7 bypass when the agent has
           no tokenizer · S8 swallow the refusal, answer the rest
builder    2 of 2 killed: B1 the cut record swapped · B2 the Fitter does not fit
jev.py     5 of 5 killed: J1 no stop on a 422 · J2 stop on any failure · J3 a local 422 not final · J4 a PC 422
           not final · J5 every 4xx final
total      29 of 29 non-equivalent mutants killed, each by a named test; 1 equivalent control passes
```

## R5. The real data does not move (verified; scratch `v1build/`, `v2build/`, `v2pin/`, `labels-*`)

```
v1 at V1_AT 0b342c7, the new code:  dataset.jsonl sha256 d7cd9b49...  == V1_AT and the committed OpenJev manifest
v2 at 434b727 (the test's PIN):     new code vs PIN code: dataset.jsonl and summary.json byte-identical;
                                    dataset.jsonl == the record's build (sha 99070c33...)
                                    manifest.json: the PIN-code build == the record's dataset-manifest.json byte for
                                    byte; the new-code build differs ONLY in `code`:
    -  "scripts/laya_ft/build_dataset.py": "1c95e37a0d99cfa874879bb0d1a9ee4674b2cfcedef9cbd749d77d6020c69297",
    +  "scripts/laya_ft/build_dataset.py": "c78d695fbc41476e5a25b1aa839d9873be28a472e34b6a07bbe927f833b7e0ae",
    +  "scripts/laya_ft/fit.py": "1f262ccad009ed828350cbcd39f08512d1c927a3b5acac517bc85e8939434542",
recorded_labels.py --out labels.jsonl --summary summary.json, on both builds:
                                    labels.jsonl == the record's (0098e52e...); summary.json == the record's (2b7f0d8a...)
```

The differential test (`tests/test_laya_ft.py:747-814`) holds the same on synthetic inputs: the PIN's `Fitter.fit`,
verbatim, against the delegating one on 7 cases: 2 that fit, 4 cuts (9,000 -> 5,246, 7,410 -> 1,823,
6,000 -> 4,366 and 5,880 -> 1,909 characters) and 1 ValueError, all identical, error text included.

## R6. Timing (verified; scratch `timing3.py`, `timing3.json`; 13:03Z)

`server._fit` exactly as `_answer` calls it, and `server._answer` for 16 chunks, with the real tokenizer, window,
builder and question form; a recorder in place of the forward pass. Sandbox CPU, 4 cores, load 0.78 before and 0.84
after (the live Laya server idle, another lane's pytest running). Median of 15 per chunk after 2 warm-ups, of 7 per
request after 1; `perf_counter`. The states are sized in TOKENS to VERIFY-P1's prefix distribution before the chunk
(p10 10,461, p50 18,166, max 22,427); the synthetic filler is denser in tokens than real text (1.9 characters per
token), so the same tokens take fewer characters:

```
fits whole (a small state, 8-line chunk)        940 chars    364 tokens   no cut           median   2.1 ms  (p90   2.2)
P1 p10 prefix, 20-line chunk                 20,911 chars 11,139 tokens   history and context emptied, task cut   64.6 ms  (p90  66.8)
P1 p50 prefix, 20-line chunk                 35,326 chars 18,864 tokens   same cuts                          86.7 ms  (p90  93.8)
P1 max prefix, 20-line chunk                 43,975 chars 23,499 tokens   same cuts                          99.3 ms  (p90 104.5)
refusal: a 40,009-char chunk, P1 max prefix  82,554 chars 39,139 tokens   Unfit 811/16196                   494.0 ms  (p90 518.4)
16-chunk request, P1 p50 prefix              _answer: 16 fits + 16 recorder calls               median 1,358.0 ms (max 1,426.6)
16-chunk request, every state fits whole     _answer                                            median    35.0 ms (max    38.4)
```

So the fit costs about 65-100 ms per chunk at the pruner's real prefix sizes, about 1.4 s for a 16-chunk request. The
rev-1 check read the chunk alone (about 40 ms per 16 chunks); the fit reads the whole state and re-tokenizes it at each
step of each search. Against the model it is small: VERIFY-P1
measured 3,800.9 ms per chunk question (p50) on this CPU. The pruner's 2 s budget was already out of reach before
K265 (no scored result met it). The worst refusal costs about 0.5 s and asks the model nothing.

## R7. The echo, re-measured through the rev-2 code (report only; nothing outside the boundary fixed)

Instruments as in section 8 (graft first; literal sweeps with the Grep tool). E4-E10 are unchanged from section 8. The
three live readers of the fan-out, each measured through the rev-2 module with a recorder in the model's place (the
checkpoint's tokenizer, config and question form):

| # | site | PIN | rev 2, measured | verdict |
|---|---|---|---|---|
| E1 | the pruner (`scripts/jev_pipes/bridge.mjs` -> the fan-out) | VERIFY-P1: 1,474 of 1,474 per-chunk states cut, 0 chunk tokens seen | VERIFY-P1's 40-result sample through its own production path (scratch `capture_rev2.py`: `transcript.windows`, `build_job`, the bridge, mode `unbudgeted`) against a loopback server running the rev-2 module's REAL `Handler` (not :47411). 310 requests; 1,242 states fitted, 1,236 sent. Every fitted state: the key order kept, the chunk unchanged and last, whole in the window (kept = own tokens, 1,242 of 1,242). 10 requests refused (422) in 10 of the 40 results: chunks of 826 to 2,567 tokens, 871 to 2,613 with the other fields emptied, against the room of 855. Those 10 results now fail open (`non_200`); at the PIN they were scored on zero chunk tokens (7 `kept_all`, 3 `incomplete_coverage`). The other 30 results keep their PIN decisions. A second run gave the same counts and the same cut for every state. | FIXED for the chunk. Two costs, below. |
| E2 | `scripts/jev.py` `rank` | chunk whole in 18 of 60 shapes | the same 60 shapes (scratch `jev_rank_shapes2.py`): 15 refused (422; the chunk was not whole at the PIN in any of the 15); 45 answered, all `["query", "chunk"]`, the chunk whole in 45 of 45; the query cut in 27 (to 58-851 of 1,000 characters, median 359) and whole in 18 | FIXED for the chunk; the query is the field cut, as in training |
| E3 | `scripts/laya_ft/evaluate.py` in-process `_answer` (ap_probe, v1_probe `jev_noul`) | the J2 inputs | evaluate.py's own call path (`C.AP.post`/`C.V1.post` -> `_answer`, `cmd_score` of each run) through the PIN's module and the rev-2 module (scratch `j2_identity.py`): every model input identical, JSON text and key order included: ap 1,600 of 1,600, v1 700 of 700 (600 fan-out), v1_full 700 of 700 (600 fan-out). Negative control, the same run with a subject-first copy of the server: ap 0 of 1,600 identical, v1 and v1_full 100 of 700 (only the one-call `choice` questions) | Not hit: J2's numbers cannot move by K265 (the committed-J2 positive control reads the same inputs) |
| E6 | `scripts/laya_ft/build_dataset.py` `Fitter` | a separate fit, `{"query", "chunk"}` | now the same function as the server's (R2, R5) | train/serve identity by construction and by test (`tests/test_laya_ft.py:863-869`) |

The two costs of E1, measured (scratch `cap40b.json`, the same run with a digest of each model input):
- **The history is gone.** Every fitted pruner state had its history cut; 1,215 of 1,242 had it emptied (the median
  state held 11 entries). The fit then cut `task` in 667 states, `command` in 228, `context` in 206 and
  `diagnosticsAndResults` in 27. A chunk of about 350 tokens plus the fixed fields leaves little of the room of 855,
  and one history entry is often larger. The model sees the chunk with the task and little else.
- **Repeated model calls.** The pruner sends each chunk once per history segment and keeps it if any segment votes to
  keep (`output.ts:16-17`, `OUTPUT_CONTEXT`). With the history emptied, the segments' states become the same: 1,073 of
  the 1,236 model inputs sent repeat an input already sent in the same result (at the PIN: 0). At VERIFY-P1's
  3,800.9 ms per question, that is about 68 minutes of CPU for this sample, spent on answers already given.
Neither is a defect against the contract (it says cut the longest first and never the chunk). Both are for the
coordinator: a memo of identical inputs in the server, or a fit that keeps the newest history entries, would change
them. The list prefix keeps the FIRST entries (the builder's prefix rule), which is the OLDEST end of a history segment.

## R8. Gates on the final files

```
$ sha256 (cut -c1-16) of the final files (13:11Z; unchanged since 12:42Z)
ea6dc2d33f75d1b7  scripts/laya_systemone_server.py
1f262ccad009ed82  scripts/laya_ft/fit.py
c78d695fbc41476e  scripts/laya_ft/build_dataset.py
7e80c76717a8c1d9  scripts/jev.py
4021d09a9ddc5fdc  scripts/qwen_jev.py
30f4345335422b00  tests/test_laya_systemone_server.py
390df824850390e9  tests/test_laya_ft.py
80e973b03dc96576  tests/test_jev_client.py
$ bash scripts/pc_suite.sh set-id -- tests/test_laya_systemone_server.py tests/test_laya_ft.py tests/test_jev_client.py
3 files set=61999ff6f3db
$ bash scripts/test_summary.sh tests/test_laya_systemone_server.py tests/test_laya_ft.py tests/test_jev_client.py --basetemp=<scratch>/bt/g1
pytest-exit: 1
pytest-summary: 1 failed, 129 passed in 439.78s (0:07:19)
$ bash scripts/test_summary.sh tests/test_laya_systemone_server.py tests/test_laya_ft.py tests/test_jev_client.py --basetemp=<scratch>/bt/g2
pytest-exit: 1
pytest-summary: 1 failed, 129 passed in 408.30s (0:06:48)
$ env -u S0_01_VENUE python3 -m pytest -q -rs <the same three files>     (CI's form: the default interpreter, no laya)
113 passed, 17 skipped in 30.26s                                           (the 17 are the loud venue skips)
$ python3 -m pyflakes <the eight files>                                     -> rc 0
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <the eight files and this report>  -> 0 each
$ python3 scripts/ap_screen.py <the five scripts>                           -> 17 hits, all on PIN lines (os.environ reads and
  writes, HEAD defaults, `t0 = time.time()` in do_POST, the `lines[-1]` status parse in jev.py) or the reflowed
  "byte-identical" docstring claim (AP-51, `scripts/laya_ft/build_dataset.py:28`, which the record tests hold); none on a new line
$ python3 scripts/ap_screen.py --tests <the three test files>               -> 15 hits; the new ones are AF-AP-33 on the
  422 test's fake endpoint (`tests/test_jev_client.py:539-544`, a double routing on "/health", not a liveness probe) and
  AP-66 `handler.headers` on the local handler object (`tests/test_laya_systemone_server.py:310`); none is an instance
$ node .gitnexus/run.cjs detect-changes --scope all --repo .                -> 8 files (7 of mine and another lane's report),
  67 symbols, 0 affected processes, risk low
$ node .gitnexus/run.cjs impact <symbol> --direction upstream               -> _http LOW (1 direct: _ask_venues), parse_pc_reply
  LOW (1: _pc), _ask_venues LOW (1: _call); Fitter.fit UNKNOWN (no resolved caller), confirmed by a literal sweep:
  `scripts/laya_ft/build_dataset.py:483` (`fitter.fit`, in fit_rows) and the two venv tests
$ python3 scripts/report_lint.py tasks/briefs/jev-pipes/K265-report.md --map jev.ts=vendor/jev-pruner/src/jev.ts \
    --map output.ts=vendor/jev-pruner/src/output.ts --map bridge.mjs=scripts/jev_pipes/bridge.mjs --min-refs 30   (rc 0)
report_lint: 60 refs — OK 59, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
  (two rounds of the lint's own fix hints: rev-1 lines that moved are cited at their new lines, at the PIN
  as path@157ddd6:NN, or in words for the uncommitted rev-1 server; the UNCHECKABLE one is section 1's pasted grep line)
```

Both gate runs fail the same one test and pass the same 129 (set `61999ff6f3db`, 130 collected: 30 + 44 + 56). CI's form
does not run that test (a venue test), so CI stays green; the sandbox venue is red until the record is regenerated.

The one failure, both runs: `test_version_2_record_rebuilds_byte_identically_at_the_pin`,
`assert (outs[0] / "manifest.json").read_bytes() == (RECORD / "dataset-manifest.json").read_bytes()`, `At index 506
diff: b'c' != b'1'`: the builder's own hash in the manifest's `code` map (R5). With the regenerated manifest copied
into the scratch lane tree's record (never the shared tree; restored after), the whole test passes, the labels, the
join and the window check after the manifest included:

```
$ S0_01_VENUE=sandbox python3 -m pytest -q "tests/test_laya_ft.py::test_version_2_record_rebuilds_byte_identically_at_the_pin"   (<scratch>/lanetree, 13:15Z)
1 passed in 95.11s (0:01:35)
```

## R9. Self-attack: the three most likely ways rev 2 is wrong

1. **Train and serve could read different windows or question forms, so the identity holds in the test and not in
   production.** The builder reads `C.model_fingerprint` and `Agent._to_internal`; the server reads the loaded agent's
   `cfg` and `_to_internal`. Ruled out: both read `max_len`/`head_max_len` from the checkpoint's `rl_agent_config.json`
   with the same defaults (`model_fingerprint`, `scripts/laya_ft/common.py:122-131`; `fit_state` called with
   `agent.cfg` at `scripts/laya_systemone_server.py:157-158`);
   the venv test runs both on the served checkpoint and compares the JSON text, a cut case and a whole case; S4 (the
   default window) and S5 (a generic question) are killed. Assumed, not re-read in rev 2: `Agent.cfg` is that same
   file's content (read in rev 1).
2. **The delegation could change dataset bytes on a shape the differential cases do not cover.** The PIN rebuilt a cut
   dict as a new `{"query", "chunk"}`; the new fit keeps the dict and its keys. Ruled out on the real data: v1 and v2
   rebuild byte-identical, labels included (R5); the builder makes only string states and `{"query", "chunk"}`
   (`make_row`'s callers), where both codes cut the one field the same way (7 differential cases, F7/F8/F11/F14/B2
   killed by the differential test). Residual: a future dict shape with more fields would be cut by the multi-field
   rule where the PIN cut only `query` (or raised `KeyError` without one).
3. **The refusal could throw away answers that carried signal.** 10 of 40 sampled P1 results and 15 of 60 rank shapes
   now fail open. Checked: at the PIN, none of the 15 rank shapes had its chunk whole, and the P1 states showed the
   model zero chunk tokens, so no whole-chunk answer is lost. But a rank chunk that just overflows was mostly seen at
   the PIN, and that partial signal is now dropped. That is the contract's rule (S8, answer the rest, is killed by
   four tests), not an accident.

Also examined: the fit runs under `State.lock` like the forward pass, so a 16-chunk pruner request holds the lock
about 1.4 s longer (R6); the refusal text carries no `max_tokens_exceeded` (the pruner retries on that text, rev 1
section 2), asserted at `tests/test_laya_systemone_server.py:301` (`max_tokens_exceeded`).

## R10. NOT done (first-class)

- **The version-2 record's manifest is NOT regenerated** (outside my boundary): `test_version_2_record_rebuilds_byte_identically_at_the_pin`
  stays red on the sandbox venue until it is. The coordinator's step, then `git diff` must show only the two `code`
  lines of R5:
  `HF_HUB_OFFLINE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --version 2 --commit 434b727dfd2b6daa5aa3cf4d638e706f5dfa59cb --out <dir> --model-dir /root/hf-laya-probe/hub/models--convaiinnovations--laya/snapshots/1c5edc17a7acd8701df6fc341c0d179f1c62c982/typed-decisions`,
  then copy `<dir>/manifest.json` over `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json`.
  The same bytes are at `<scratch>/v2build/manifest.json` (built 12:51Z from the final files).
- `scripts/laya_ft/evaluate.py`'s positive control on the model: NOT run (it loads the model). E3 shows its inputs are
  byte-identical, so K265 cannot move it.
- The live servers (sandbox 127.0.0.1:47411, pid 30467, and the PC's): NOT touched and NOT restarted (D-089 makes the
  restart the coordinator's step). Until the PC server runs K265, a PC answer is unfitted; `jev.py` asks the PC only
  when the local server is unavailable, never after a local 422.
- `tests/fixtures/jev_pipes/answers.jsonl` (recorded from the PIN's server): NOT re-recorded; the replay tests stay green
  on it, but it will not describe the restarted server's answers to pruner-shaped requests.
- The two E1 costs (the history emptied in 1,215 of 1,242 pruner states; 1,073 of 1,236 model calls repeating an input
  of the same result): NOT addressed; they follow from the contract's rule and are for the coordinator (R7).
- E4 (`scripts/qwen_jev.py`'s own order and its compiler's budget): NOT measured (PC only); its order unchanged, as the
  brief says.
- No server log line carries the 422 reason (`log_message` writes the request line and status); the body carries it.
  The pre-existing gap of every 500, unchanged.
- VERIFY-P1's scratch instrument (`<scratch>/verify-p1/probe/capture_states.py`, not committed) calls `Fitter._tokens`,
  which no longer exists; that exact script would now stop with an `AttributeError`.

## R11. DISCREPANCIES and deviations (rev 2, loud)

- RD1 (blocks the sandbox gate): the committed version-2 record pins the builder's code hashes, so the delegation this
  amendment asks for turns `test_version_2_record_rebuilds_byte_identically_at_the_pin` red until the record's
  manifest is regenerated (R10). The data, labels and summaries do not change (R5).
- RD2: `CODE` gains `scripts/laya_ft/fit.py`. The brief did not name it; without it the manifest would not change when
  the code that shapes the data changes.
- RD3: `Fitter` no longer has `_build`, `_serialize` or `_tokens` (no committed caller; literal sweep of `scripts/`,
  `tests/` and `docs/research/findings/`).
- RD4: the builder's refusal is now `fit.Unfit`, a `ValueError` subclass with the PIN's exact message; `fit_rows`
  (`scripts/laya_ft/build_dataset.py:478-493`, `fit_rows`) does not catch it, so a build stops on it as before.
- RD5 (an interpretation): item 3's "an agent without a tokenizer is a refusal" is built as HTTP 500, since item 4 keeps
  load failures at 500. So `jev.py` does try the next venue on it; only the fit's own refusal is a final 422.
- RD6 (an interpretation): "a chunk that does not fit alone" is tested with every other field EMPTY and its key kept,
  which is the PIN Fitter's own test (`cut_to(0)` = `{"query": "", "chunk": ...}`). In the pruner's shape the empty
  keys cost the chunk about 45 tokens of the room: chunks of 826 and 854 tokens were refused (E1).
- RD7 (a correction to rev 1, section 8 E2): "the QUERY whole in only 20 of the 45" counted 2 too many. The decode check
  found the query's text inside a chunk made of the same text (prose/prose, code/code). Counted by length: 18.
- RD8 (rev 1 superseded): section 7's inferred P1 refusal rate (54 of 366 requests, 9 of 40 results) is replaced by the
  measurement in E1: 10 of 310 requests, 10 of 40 results (the pruner stops asking once a request is refused).
- RD9: `scripts/jev.py:14-16` (`the server puts the query first`) unchanged, because it is true under rev 2; the 422 rule went into the Venues paragraph.
- RD10: item 3's `{"query": <long>, "chunks": [...]}` request is tested with one chunk (a cut case and a whole case);
  several chunks go through the model-free and venv fan-out tests.
- Boundary: no deviation. `tests/test_laya_systemone_server.py` holds 30 tests (rev 1's chunk-first tests replaced).
  Outside the boundary I read only; every probe wrote to scratch.

## R12. Evidence tiers (rev 2)

- Verified (this session, primary source or probe): R1-R8; E1, E2, E3 and E6 in R7; the self-attack checks in R9.
- Inferred: "about 68 minutes of CPU" (1,073 repeated calls x VERIFY-P1's 3,800.9 ms per question); "one history entry
  is often larger" than the room left (from the emptied-history counts, not measured per entry).
- Assumed: a deterministic forward pass, so identical inputs give identical J2 numbers (E3); `Agent.cfg` holds the
  checkpoint's `rl_agent_config.json` (R9.1); E4, E10 as in section 8.

Finished 13:2xZ.
