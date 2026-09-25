# K265: the Laya server's per-chunk fan-out puts the subject first (task #265, AF-AP-208)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/jev-pipes/K265-report.md` (write it
incrementally from the start). PIN: 157ddd6 (origin; the boundary files are unchanged from ce2e1c5 to the local head, measured).

## WHY

The P1 replay measured FAIL: the local Laya scorer answered every chunk question without seeing the chunk (every answer 0.52-0.60,
nothing pruned, no error). `scripts/laya_systemone_server.py` `_answer` builds each per-chunk state as the request's fields plus
`chunk` added LAST (`dict(base, chunk=chunks[qid])`); Laya serializes the state as JSON in key order and `laya.common.build_sequence`
keeps only its first tokens (`st[:room]`; max_len 1,024 with a 256-token head for the `typed-decisions` checkpoint). The pruner's
state carries `context`, `task` and up to 53 `history` segments (3,133-70,112 characters) before the chunk, so the chunk was cut
every time. The existing unit test could not see this: it compares the recorded states with dict equality, which ignores key order.

## CONTRACT (the coordinator's design call; do not redesign)

1. **Subject first.** In the fan-out path, each per-chunk state is `chunk` first, then the request's other fields except `chunks`,
   ordered by the length of their JSON serialization, shortest first (ties keep the request's order). Laya's builder then cuts the
   longest field, never the subject. The one-call path (no fan-out) is unchanged.
2. **A fit check per state, by the consumer's own verdict.** Before asking the model about a chunk, the server checks with the
   loaded agent's own tokenizer and config (`State.agent.tok`, `State.agent.cfg` max_len/head_max_len, the same call
   `Agent.system_one` makes) that the chunk-only state `{"chunk": text}` survives `build_sequence` whole (the Fitter's verdict:
   the built length equals the empty-state length plus the state's own token count; `scripts/laya_ft/build_dataset.py` `Fitter.fit`
   `fits`). A chunk that does not fit whole gets NO model answer: the whole request is refused with a reason, through the handler's
   existing refusal path (read `Handler.do_POST`), so a client fails open and keeps its output. Never answer about a chunk the model
   did not see whole; never cut the chunk.
3. The module docstring's PER-CHUNK FAN-OUT paragraph says what the code now does (a change that falsifies a comment fixes it).

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Order-aware unit tests (fake agent, run everywhere): the recorded state's key ORDER (e.g. `list(state)` or its `json.dumps`), the
   shortest-first rule with a tie, the one-call path unchanged, and the refusal. Red first: paste them failing on the PIN's server and
   passing on yours.
3. A consumer-verdict test in the Laya venv, on the pattern of `tests/test_laya_ft.py` `laya_venue` + `_laya` (a LOUD SKIP unless
   `S0_01_VENUE=sandbox`; a declared input missing on that venue FAILS): the per-chunk state your code builds for a long-history
   pruner-shaped request keeps the whole chunk through the real `build_sequence` and tokenizer (tokenizer only; do not load the
   model), and the same request built in the PIN's order loses it. Factor the state construction and the fit check so both are
   testable without a loaded model.
4. `bash scripts/test_summary.sh tests/test_laya_systemone_server.py` twice with the set id (`bash scripts/pc_suite.sh set-id -- ...`);
   pyflakes rc 0 on every file you touch; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
5. The echo (report only, fix nothing outside the boundary): every other place in this repo that sends a state to Laya or another
   fixed-window reader with the subject after a field of unbounded length. Name the instruments you used (graft first), and measure
   each hit's real state shape through the builder where you can (the AF-AP-208 row says `scripts/jev.py` callers were not measured).
6. A timing line: the fit check's added cost per chunk on the sandbox CPU (median of a small sample), so the coordinator can weigh it
   against the pruner's 2 s budget.
7. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `scripts/laya_systemone_server.py`, `tests/test_laya_systemone_server.py`. CREATE: your report. READ everything else. Not
`vendor/jev-pruner/`, not `scripts/jev_pipes/`, not `scripts/laya_ft/` (read its `Fitter`; do not import `build_dataset` into the
server if that drags its dependencies in: reuse the verdict, not the module). Scratch:
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k265/lane/`.

## STANDING RULES

The live Laya server (127.0.0.1:47411, pid 30467) is NOT touched: never send it a request, never stop or restart it (the restart on
the new code is the coordinator's step after the verify round). No network; no PC bridge; no git writes; no outward-facing action.
Never read a real secret file (`.pc-bridge.env`, `/root/.codiv/api.env`, any `*.env`, any key file). Fixtures are synthetic; no
session text enters a committed file. Another lane is live in this tree on other files: touch nothing outside your boundary.

## PREMISE — MEASURED at authoring (2026-09-25 11:2xZ, the sandbox, the PIN's bytes)

```
$ git show ce2e1c5:<file> | sha256sum | cut -c1-16      (git diff ce2e1c5 HEAD on these files: empty; 157ddd6 only adds transcripts)
cba055a9dc33de21  scripts/laya_systemone_server.py
f628ce5adb9d3eaa  tests/test_laya_systemone_server.py
$ sed -n '130,144p' scripts/laya_systemone_server.py | grep -n 'system_one(dict'
10:        one = State.agent.system_one(dict(base, chunk=chunks[qid]), {qid: q})
$ bash scripts/test_summary.sh tests/test_laya_systemone_server.py
pytest-summary: 16 passed in 0.04s
$ bash scripts/pc_suite.sh set-id -- tests/test_laya_systemone_server.py
1 files set=0bd8d4de212b
$ (the PIN's test file against a copy of the server with the subject first: dict({"chunk": chunks[qid]}, **base))
16 passed in 0.03s                                      <- the existing suite cannot see the order
$ /root/venv-laya-probe/bin/python order_probe.py       (tokenizer only; C.DEFAULT_MODEL_DIR, the typed-decisions checkpoint;
                                                         context 900 chars, 53 history segments of about 1,310, command, results)
{"max_len": 1024, "head_max_len": 256, "state_chars": 70806, "chunk_kept_current_order": false, "chunk_kept_subject_first": true}
$ grep -n 'maxStateTokens: 25_000\|DEFAULT_MAX_STATE_TOKENS = 25_000' scripts/jev_pipes/bridge.mjs vendor/jev-pruner/src/output.ts
scripts/jev_pipes/bridge.mjs:26:  maxStateTokens: 25_000,
vendor/jev-pruner/src/output.ts:10:const DEFAULT_MAX_STATE_TOKENS = 25_000;   <- the client's budget is sized for a 25k window (READ only)
```

A question for you, not a fact: how does the pruner (`vendor/jev-pruner/src/jev.ts`, `output.ts`) treat a refused request and a
missing answer? Read it and say which refusal keeps the output.

## AMENDMENT 1: contract rev 2 (the coordinator, 2026-09-25 12:1xZ; replaces CONTRACT items 1 and 2)

WHY: the lane's hand-back found that `tests/test_laya_ft.py::test_ap_state_is_the_servers_fan_out_shape` locks a train/serve
invariant this brief missed: the fine-tune `ap` rows are `{"query", "chunk"}` in that order, with the query cut by
`build_dataset.Fitter` so the whole state fits, and J2 scored that shape through this server. Chunk-first serving would show the
student a shape it never trained on, for most `scripts/jev.py` rank requests (the lane's echo E2: the state does not fit whole
in most of them). So the server serves the training shape, fitted by the training transformation.

1. **The training order, fitted as in training.** The per-chunk state keeps the PIN's order (the request's fields except
   `chunks`, then `chunk` last). It goes through ONE fit function that the dataset builder also uses: returned unchanged when
   it fits whole (the builder's verdict), otherwise its non-chunk fields are cut, the longest serialized value first (a string to
   its longest fitting prefix by the Fitter's own search, a list to its longest fitting prefix of whole entries), until the whole
   state fits. The chunk is never cut; a chunk that does not fit alone gets no answer and the request is refused.
2. **One function, two callers.** The fit lives in a small module under `scripts/laya_ft/` that both import in the Laya venv (the
   server imports it inside the fan-out path, so the default interpreter never needs `laya`); `build_dataset.Fitter.fit`
   delegates to it. A differential test in the Laya venv (the `laya_venue` pattern) shows the delegation changes no output for
   the dataset's shapes (a string state, `{"query", "chunk"}`) against the PIN's Fitter, on synthetic inputs that include cuts.
3. **Train/serve identity, through the real tokenizer.** In the Laya venv: for a `{"query": <long>, "chunks": [...]}` request, the
   server's per-chunk state equals the dataset builder's fitted state for the same query and chunk, key order included (a cut
   case). The default-interpreter test keeps its assertion with the fit replaced through a named seam; an agent without a tokenizer
   in production is a refusal, never a bypass.
4. **A refusal is final for the client.** The fit refusal answers HTTP 422 with its reason (a model or load failure stays 500);
   `scripts/jev.py` treats 422 as a final no-answer (fail open, exit 3), never as a reason to try the next venue: the PC runs the
   PIN's server until the owner approves its restart (your D3).
5. Comments your change falsifies are fixed in the same change: `build_dataset.py:20`, `scripts/jev.py:14-16` if still false,
   `scripts/qwen_jev.py:387`'s line citation. E4 (`qwen_jev.py`'s own order) stays a question for the PC; do not change it.
6. Re-measure the timing line for the new fit (per chunk and per 16-chunk request, median, sandbox CPU); the searches cost more
   than one check.

BOUNDARY, rev 2 (adds to the original): MODIFY `scripts/laya_ft/build_dataset.py` (the delegation and its docstring),
`tests/test_laya_ft.py` (the seam in the invariant test, the new venv tests), `scripts/jev.py` (the 422 rule and the comment
only), `tests/test_jev_client.py` (the 422 test), `scripts/qwen_jev.py` (the citation only). CREATE the fit module under
`scripts/laya_ft/`. Evidence demands 2-7 apply to the new contract (red first on the PIN where it applies; `tests/test_laya_ft.py`
and `tests/test_jev_client.py` join the gate set, with its set id).
