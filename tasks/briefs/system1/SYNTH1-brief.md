# SYNTH1: synthetic skill-relevance labels from our chat history, with the labeler checked against real scores first (task #308, D-096)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/SYNTH1-report.md` (write it
incrementally from the start). PIN: origin fb7f614. Rulings: D-096 (this plan), D-074 (a model must beat the plain order),
D-075 and D-078 (OpenJev may label Laya's training data; every string scrubbed first), D-082 (System 1 talks straight to
vLLM), D-092 item 3 and D-095 (the S1-RATE scale). Design: `docs/research/findings/system1-context/DESIGN-2026-09-25.md` (L6).

## WHY

Laya is to rank the skill sections the System-1 hook injects (task #297), but it has no usable signal yet: zero-shot it had
none (D-074), and the first fine-tune (1,788 examples) was rejected because its teacher was below the lexical baseline. Real
S1-RATE scores accumulate only as we work. This lane builds the machine that turns our chat history into many more labeled
(situation, skill section) pairs, with a labeler that must first agree with the real scores. The coordinator runs the
labeling on the PC; this lane builds, tests and dry-runs everything that does not need the PC or a real key.

## CONTRACT

1. **Candidates, `scripts/s1_synth.py candidates`.** From this session's transcripts (the main JSONL and every file under its
   `subagents/`, read in process): every human-origin prompt (the harness-event rule of the hook) and a sample of real tool
   calls (Write, Edit, Bash, Read, Grep; stratified by tool and by the L1 situation rows each matches; at most 2,000 by
   default). Each item's text passes the same scrubber as the exports (`transcript_export.scrub_payload` or `scrub_strict`;
   say which and why) and a cap. Its candidates are the live hook's own ranking over the item (import the hook's functions;
   never re-implement them): the top 10 sections by score WITHOUT the injection gates, so the set holds negatives as well as
   the sections the gate would inject, each with its score, skill, heading, project flag and the section's `sha` (the hook's
   definition); for a tool call, also the situation rows that match it. **Only prompts and tool INPUTS are items: never an
   assistant's text, never a `thinking` block** (the model's reasoning is not training data here).
2. **The labeler, `scripts/s1_synth.py label --backend vllm|openjev`.** One request per (item, section): a fixed rubric (the
   S1-RATE scale for `rel`, and `use` as "would this section help with this step"), the item and the section text, and a
   strict answer (`rel=<0-3> use=<0-3>`, a short reason) parsed exactly; a malformed answer is stored as such, never guessed.
   - `vllm`: straight to the PC's vLLM (`http://127.0.0.1:8080/v1/chat/completions`, model `qwen3.8-27b-local`, the key read
     in process from `~/.config/qwen-builder/api-key` when the COORDINATOR runs it on the PC); several requests in flight at
     once (`--concurrency`, default 6: vLLM batches them), thinking off unless a flag asks for it, a small `max_tokens`.
     **Never send `prompt_logprobs`, `best_of`, `echo` or `n` (AF-AP-201: one such request OOM-killed the shared server).**
   - `openjev`: reuse `scripts/laya_ft/teacher_label.py`'s client and limits (60 requests per 60 s; its scrubbing; its key
     handling) by import; do not copy it.
   - Both: append-only JSONL keyed by (item id, section sha, backend, rubric version), with the model id and the digests of
     what was sent; a rerun skips done keys; retries with backoff; the usage totals at the end.
3. **The validator, `scripts/s1_synth.py validate`.** The labeler's agreement with two gold sources: the REAL S1-RATE scores
   (`scripts/s1_scores.py` rows: an injection's rel applies to the sections it carried) and S1-ALL's 463 labels (report
   Appendix E: R, P, N per prompt and skill; say how you map them to the scale). Report per source: exact and within-one
   agreement, a rank correlation, the confusion table, and the counts behind each. Propose the bar a labeler must pass
   before its labels are used, from what you measure; the coordinator decides.
4. **The dataset.** Labeled pairs in a form `scripts/laya_ft/` can train on (read `build_dataset.py` and the recorded
   dataset's manifest; say what you match and what differs), with a manifest (counts, sources, digests, the rubric
   version), under `docs/research/findings/laya-ft-labels/<date>-synth/` for what may be committed (ids, labels, digests)
   and scratch or the PC for the item texts (scrubbed, but session text).

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. A dry run of `candidates` over this session's real transcripts in process: counts per item kind and tool, candidates per
   item, the share of items whose top section the live gate would inject, the scrub's redaction counts; no text printed.
3. Tests (`tests/test_s1_synth.py`) with fixture transcripts and a local fake HTTP server for each backend's shapes: the
   thinking and assistant-text exclusion; scrubbing before any byte leaves; the candidate set equal to the hook's own ranking
   (a mutated ranking reds); the forbidden vLLM parameters never sent (a request carrying one reds); concurrency held at its
   bound; resume skips done keys; a malformed answer stored as malformed; the validator's numbers on hand-made gold. A
   negative control reds for each (a kill is a FAILED test, never an error: AF-AP-223).
4. The exact commands the coordinator runs on the PC (ship the scrubbed candidate set, label with vLLM, bring the labels
   back), an estimate of the run's time at concurrency 6 from the measured throughput, and what must not run beside it.
5. `bash scripts/test_summary.sh` twice on `tests/test_s1_synth.py` and every test file that names a file you import, with the
   set id; pyflakes rc 0; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
6. NOT-done and DISCREPANCIES.

## BOUNDARY

CREATE: `scripts/s1_synth.py`, `tests/test_s1_synth.py`, your report, and files under
`docs/research/findings/laya-ft-labels/<date>-synth/`. MODIFY: none (if `teacher_label.py` or the hook needs a change to be
reused, stop and say so). READ everything else.

## STANDING RULES

No git writes in this tree; **no PC bridge** (the coordinator runs the PC steps); no outward-facing action; no request to a
real labeler endpoint (tests use a local fake server). **Never read a real secret source** (`.pc-bridge.env`,
`/root/.codiv/api.env`, `/root/.config/session-export/pseudonym.key`, any `*.env`, `~/.config/qwen-*`, the GH_TOKEN and
GITHUB_TOKEN variables). Transcripts hold secrets: read them in process only; print ids and counts, never a prompt's, a tool
input's or a section's text. The disk is shared (1.7G free at authoring): scratch under 300 MB in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/synth1/`, deleted
as you go; a short `--basetemp` with its parent created first. Test counts pasted from `scripts/test_summary.sh`; stamps from
`date -u`. Long commands in one foreground call; kill by pid only. A PreToolUse hook adds skill excerpts with a score request
(the S1-RATE line): answer it as it asks.

## PREMISE — MEASURED at authoring (2026-09-26 03:3xZ, the sandbox tree at origin fb7f614)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-100
fb7f614 transcripts: scrubbed sandbox chat digests (2026-09-26)
$ (python, in process) human-origin prompts and tool calls in the main transcript; subagent transcripts
main transcript: human-origin prompts 224 | tool calls {'Bash': 16350, 'Read': 542, 'Write': 569, 'Edit': 682, 'Grep': 82}
subagent transcripts 305 bytes 516715032
$ grep -c . tasks/briefs/system1/S1-ALL-report.md >/dev/null; sed -n '832,834p' tasks/briefs/system1/S1-ALL-report.md | cut -c1-90
## Appendix E. The labels (463; `prompt id`, `skill`, `R`/`P`/`N`; ids and skill names onl

```
$ grep -n -E '^def (rank_prompt|corpus_index|build_index|plan_prompt|match_rows|plan_tool)' .claude/hooks/system1-context.py
531:def match_rows(table, tool, ti, cwd, skipped=None):
568:def plan_tool(payload, table, seen, budget=TOOL_BUDGET):
695:def build_index(files):
725:def corpus_index(cache_path):
749:def rank_prompt(prompt, idx, project):
803:def plan_prompt(payload, table, seen, cache_path, budget=PROMPT_BUDGET):
$ grep -n -E '^(MIN_PROMPT_SCORE|ONE_LEAD_MIN_SCORE|SHORT_MIN_SCORE|NAMED_MIN_SCORE|PROMPT_EXCERPTS)' .claude/hooks/system1-context.py
65:PROMPT_EXCERPTS = 2                  # the best one or two sections per prompt, each at most PROMPT_BUDGET // 2
67:MIN_PROMPT_SCORE = 70.0             # a project section with two or more lead words (noise is worse than absence)
68:ONE_LEAD_MIN_SCORE = 80.0           # a project section with ONE lead word (F5)
69:SHORT_MIN_SCORE = 30.0              # ... with two or more, in a short prompt: this, when they carry MIN_COVER
71:NAMED_MIN_SCORE = 40.0              # a section of a skill the prompt names: the only way a library skill counts
$ ls scripts/laya_ft/ | grep -v pycache | tr '\n' ' '
__init__.py build_dataset.py common.py evaluate.py fit.py recorded_labels.py teacher_label.py train.py 
$ sed -n 3,5p scripts/laya_ft/teacher_label.py

  teacher_label.py --dataset DIR --out LABELS.jsonl [--env-file /root/.codiv/api.env] [--limit N] [--questions a,b]
$ grep -n -E 'kind.*thinking|thinking \(' scripts/session_export.py | head -3 | cut -c1-120
21:Kinds: text; thinking (a block whose `thinking` holds plain text; a signature-only block is counted, not exported);
$ bash scripts/pc.sh '...systemctl --user is-active qwen; live lanes; nvidia-smi memory'   (at authoring)
active
(no live PC lane)
24060 MiB, 24576 MiB
$ grep -n -E 'served-model-name|127.0.0.1:8080|0.0.0.0:8080|~45 tok/s|310 tok/s' PC-BRIDGE.md | head -4 | cut -c1-140
61:| Local **vLLM** OpenAI-compatible endpoint `http://localhost:8010/v1`, served-model-name `sim9b`, guard `~/vllm_serve.sh` (setsid+flock)
163:  (MTP/batch) and serves Qwen3.8-27B under BOTH **`qwen3.8-27b-local`** and `qwen3.8-27b` on `0.0.0.0:8080`,
166:  `--served-model-name qwen3.8-27b` and appends `${EXTRA_ARGS}` last; vLLM's `--served-model-name` is
168:  OmniRoute change. Measured 2026-09-16: ~45 tok/s single-request decode, near-linear to ~310 tok/s aggregate at 7
```

Questions for you, not facts: how many real S1-RATE scores exist at your start (run `scripts/s1_scores.py` on this session),
and how many does the validator need before its agreement numbers mean anything?
