# SYNTH1 report (task #308, D-096)

Lane: code-implementer (sandbox, Opus 5.5). Started 2026-09-26 03:37Z. Written incrementally; each section carries its stamp.
Tree: HEAD 635a260 (the brief's commit) on origin fb7f614 + the brief. No git writes, no PC bridge, no real labeler endpoint.

**Resume (06:0xZ).** A container restart at about 05:40Z stopped the lane mid-gate; the files were intact. The coordinator
stopped the orphaned gate run at 43% (it included the whole tests/test_vendored_manifest.py, about 75 MB per test on a
shared disk with 1.48 GB free) and sent three facts, all applied: (1) VERIFY-S1-RATE (task #309) found that a reply over
about 200 characters before a tool call is recorded as thinking with no text block, so the validator now uses `scored`
rows ONLY and states the caveat in its output (section 5); (2) S1-RATE-R1 (task #318) will add a status to
scripts/s1_scores.py, so the tool relies only on `scored` and the fields it reads today; (3) each S1-RATE score is now a
short text of its own. The gate re-ran with tests/test_vendored_manifest.py one test at a time (section 9); the
mutation run and the dry run re-ran on the final code.

**Round 2 (07:4xZ), section 14.** After the landing (origin 626fc4c) two findings came back, both fixed in this lane's
own files: (A) the PC smoke stored 74 of 108 answers as malformed because their reasons ran past 120 characters, so
the parse now takes a reason of any length (stored cut to 120) and a resume re-parses the stored answers with no
request; (B) stage0-ci failed on the Laya-venue test, whose skip guard raised PermissionError on a non-root runner, so
the guard now treats an unreadable path as absent and skips loudly. Sections 1 to 13 are round 1's record; where
round 2 changed a fact, the passage points to section 14.

## 1. Premise re-measure (EVIDENCE DEMANDS 1), 03:5xZ

Every line of the brief's PREMISE block was re-run. Verdict: **the premise holds; no CONTRACT-INVALID.** The deltas are
growth since authoring (03:3xZ), not mismatches.

| premise line | at authoring | now (03:37-03:45Z) | verdict |
|---|---|---|---|
| origin tip | fb7f614 transcripts: scrubbed sandbox chat digests | fb7f614 (same) | holds |
| main transcript human-origin prompts | 224 | 225 (one more at 03:33Z, after authoring) | holds (growth) |
| main transcript tool calls | Bash 16350, Read 542, Write 569, Edit 682, Grep 82 | Bash 16376, Read 542, Write 569, Edit 682, Grep 82 | holds (growth) |
| subagent transcripts | 305 files, 516,715,032 bytes | 306 top-level agent-*.jsonl (305 + this lane's own) plus 38 files under subagents/workflows/: 344 .jsonl, 552,025,244 bytes | holds; the premise counted top level only |
| Appendix E header, line 832 | "## Appendix E. The labels (463; ..." | same line; parsed: 463 labels, R 59 / P 127 / N 277, 153 prompts, 29 skills, 0 duplicate pairs | holds |
| hook functions (lines 531, 568, 695, 725, 749, 803) | as quoted | identical | holds |
| hook gates (lines 65, 67, 68, 69, 71) | as quoted | identical | holds |
| scripts/laya_ft/ listing, teacher_label.py usage line | as quoted | identical | holds |
| session_export.py line 21 (thinking kind) | as quoted | identical | holds |
| PC-BRIDGE.md vLLM lines 61, 163, 166, 168 | as quoted | identical | holds |
| PC state (qwen active, no lane, 24060 MiB) | measured by the coordinator | NOT re-measured: this lane has no PC bridge | not re-run (bridge excluded by the brief) |

How "human-origin" was measured (the rule the candidates use): a `user` record, not `isMeta`, not `isCompactSummary`, no
`tool_result` block, `origin.kind == "human"` (the harness's own marker; S1-ALL used it for its 219), and then the hook's own
harness-event rule (`HARNESS_EVENT_PREFIXES`, the hook's constant, imported) and an empty-text check. In the main
transcript the other user-text records are 556 `origin.kind == "task-notification"` (all start with a harness-event prefix)
and 30 with no origin (16 "[Request interrupted by user...", 7 `<command-name>`, 7 `<local-command-stdout>`). In the 344
subagent files, the 353 user-text records are the coordinator's dispatch prompts: no `origin`, none human-origin, none
harness-prefixed. They are not items (the brief: human-origin prompts only).

**The brief's question 1: real S1-RATE scores at my start** (`python3 scripts/s1_scores.py <main transcript>`, 03:39Z): 345
transcript files, 22 stamped injections (hook_additional_context 21, tool_result 1), **8 scored**: edit-snapshot 4,
wiki-context 3, system1-context 1. Re-counted at 03:5xZ with the state join (`.jev/injections.jsonl`, `.jev/system1.jsonl`): system1-context has 17
stamped injections, **7 scored** (all PreToolUse, all in the main thread: rel 1, 2, 2, 3, 3, 3, 3), carrying 8 skill
sections; it was 12 stamped and 3 scored a few minutes earlier, so it grows while the coordinator works. That is the whole real gold for System-1 sections so far. Question 2 (how many the validator needs) is
answered in section 5 from the confidence intervals.

## 2. Seams read (build-loop step 1), 04:1xZ

Every seam the tool calls was read at its current state before code was written (the consumer's contract, not a doc):

| seam | file:line | what the tool relies on |
|---|---|---|
| harness-event rule | .claude/hooks/system1-context.py:84 | `HARNESS_EVENT_PREFIXES`, imported, applied as plan_prompt applies it (line 810) |
| tool path fields | .claude/hooks/system1-context.py:382 | `tool_fields`: a Bash call's command; a Write's path and content; an Edit's path and new_string |
| situation rows | .claude/hooks/system1-context.py:531 | `match_rows(table, tool, ti, cwd)`; rows exist for Bash, Write and Edit only (40 rows) |
| a row block and its sha | .claude/hooks/system1-context.py:568 | `plan_tool`; the sha is sha256 of each block from label to pointer (lines 597-599) |
| the ranking and its gates | .claude/hooks/system1-context.py:749 | `rank_prompt`; the four floors are module globals read at call time (lines 790-796) |
| an excerpt and its sha | .claude/hooks/system1-context.py:803 | `plan_prompt`: the chosen sections, each composed with its sha (lines 852-854) |
| the index | .claude/hooks/system1-context.py:725 | `corpus_index(cache_path)`: rebuilt and REWRITTEN when stale, so the tool gives it a temporary path, never .jev/ |
| S1-RATE rows | scripts/s1_scores.py:287 | `read_session`, `join_state` (line 364) for tool_use_id; `transcript_files` (line 91) = main + subagents/** |
| the scrubbers | scripts/transcript_export.py:182 | `scrub_payload`; `scrub_strict` (line 228) rewrites every assignment line and long mixed run |
| the value gate | scripts/transcript_export.py:286 | `known_values(sources)` + `value_hits` (line 323); sources passed explicitly, KNOWN_VALUE_SOURCES (line 273) read at run time |
| the OpenJev client | scripts/laya_ft/teacher_label.py:118 | `Client` (ask, safe, usage), `Limiter` (line 49, not thread-safe), `read_env` (line 74), `scrubbed` (line 84) |
| label and row shapes | scripts/laya_ft/common.py:238 | `distribution`; `join_labels` (line 291); `load_dataset` refuses a question id outside QUESTIONS (line 228) |
| the dataset row | scripts/laya_ft/build_dataset.py:468 | `make_row`'s shape; `Fitter` (line 445) needs the Laya venv |

Findings from the reading that shaped the design:
- **OpenJev is not a chat endpoint.** It answers typed questions with probability distributions (`/v1/systemone`). So the
  openjev backend asks two choice questions (`skill.governs` on the rel scale, `skill.helps` on the use scale) in ONE
  request per pair (`openjev_j2.py` sends several questions in one body), and "malformed" there is what
  `common.distribution` refuses.
- **`teacher_label.Limiter` is not thread-safe**, so the backend wraps ONE Limiter in a lock and gives each thread its
  own `Client` (their usage summed at the end). Nothing of teacher_label is copied.
- **`common.load_dataset` refuses the new rows today** (question ids outside `QUESTIONS`; source kind `transcript` is
  unknown to `row_identities`). `common.join_labels` accepts them. See section 5 and NOT-done.
- **The prompt-path link.** A prompt-path injection's attachment does not point at its prompt (parentUuid reaches a human
  prompt within two steps for 5 of 10). By time it is exact: 5 of 10 follow a human prompt by 0.1 s; the other 5 follow
  task notifications. So a prompt-path score joins the human prompt at most 2 s before it.
- **The vLLM tell.** `.claude/hooks/edit-snapshot.py:375` flags `prompt_logprobs` or `best_of` followed by `:` or `=`.
  The tool names the forbidden keys only as strings in a tuple, and the tests plant them by variable, so the tell stays
  a true signal.

## 3. The design as built, and the dry run (CONTRACT 1; EVIDENCE DEMANDS 2), 04:1xZ

**The scrubber: `transcript_export.scrub_payload`, with its plain marker.** It is the exporters' payload scrubber:
scrub's rules plus the shapes a tool input carries (JSON-escaped credentials, `curl -u`, `*_PASS` values, URL
userinfo). Every string of an item goes through it before anything else reads it (the situation rows are matched on the
scrubbed input too), and the text is cut after it (scrub, then cut: AF-AP-127). Not `scrub_strict`: it replaces every
`NAME = value` line and every 20+ character mixed run, which wrecks the code in a Write or Edit input and the hashes in a
command, and session_export runs it only on the OUTPUT of a command that names a secret file; an item is never an output.
Not session_export's pseudonym callable: its key (`/root/.config/session-export/pseudonym.key`) is a secret source this
lane may not read, and a labeler needs no stable pseudonyms. The cut is the hook's own `PROMPT_SCAN_CHARS` (4,000): all
the ranking reads of a text, so the cut changes no candidate. Before any write, transcript_export's VALUE gate counts the
known secrets' values in the exact bytes and refuses on a hit (exit 4, nothing written). A dry run writes nothing and
opens no secret source, so this lane never ran the value gate on real data (NOT run here: it reads the real secret
sources).

**The candidates: the live hook's own functions, loaded by path twice.** `ungated` is the hook with its four score
floors lifted (`MIN_PROMPT_SCORE`, `ONE_LEAD_MIN_SCORE`, `SHORT_MIN_SCORE`, `NAMED_MIN_SCORE` set to -inf on that
private module); its `rank_prompt` gives the top 10. What still decides whether a section gets a score at all is the
ranking's scope, not a gate: a lead word, and a library skill's name in the text. Each candidate is composed by the live
`plan_prompt` ALONE in a fresh window (its `rank_prompt` answering with that one section), so the section text and its
`sha` are exactly the hook's; the code asserts sha16(text) equals the hook's sha. A tool call also gets each row
`match_rows` finds, composed alone by `plan_tool` (a one-row table). `gate` marks what the live hook injects in a
fresh window: for a ranked section, the prompt path's choice (the live hook runs it on prompts only; on a tool call it
is what the prompt path WOULD inject); for a row, the tool path's. A gold item gets its gold section even below the top
10 (S1-ALL: the skill's best-ranked section; S1-RATE: the exact section).

**The sample: two-level round-robin.** One call per tool a round (Bash, Read, Write, Edit, Grep), and within a tool one
call per stratum a round (the stratum is the sorted set of situation rows the call matches), each stratum in a
seeded shuffle (seed 308). A repeated input (same tool, text and rows) counts once; the calls with a stamped System-1
injection go first. The first design (one round-robin over all 299 strata, sorted) would have given Read and Grep about
7 items each, because the Bash strata sort first; the small dry run showed it, and the two-level rule replaced it.

**The dry run** (`python3 scripts/s1_synth.py candidates --transcript <main> --dry-run --cache <scratch>/cache.json`,
this session's real transcripts, in process, on the final code: 05:58:22Z to 06:00:01Z, 98.6 s; stdout is counts only;
earlier runs at 04:0xZ, 04:3xZ and 05:3xZ gave the same shape, and the transcripts grow while they are read):

| measure | value |
|---|---|
| population | 349 transcript files; human-origin prompts 226; tool calls Bash 42076, Read 2811, Write 1421, Edit 3493, Grep 226; 47004 distinct inputs (3023 repeats left out); 299 strata; 6 lines not valid JSON, skipped |
| items | 2226: prompts 226, Bash 475, Read 430, Write 436, Edit 445, Grep 214; gold tool calls forced in: 67 |
| candidates | 21960 pairs (18264 ranked, 3696 rows); per item min 0, median 11.0, mean 9.87, max 20; items with none: 276 (84 prompts and 192 tool calls: nothing in the ranking's scope and no situation row) |
| unique sections | 705 (each composed text stored once) |
| gate, prompts | the live gate injects the top ranked section for 36 of the 142 prompts that have one (36 of all 226) |
| gate, tool calls | 1271 of 2,000 match a situation row, and the live tool path injects a row for all 1271; the prompt path would inject the top section for 912 of 1792 |
| scrub | prompts changed 33 of 226; tool inputs changed 391 of 2,000; redaction markers added: <bridge-link-redacted> 18, <opaque-redacted> 2128, <private-key-redacted> 8, <redacted> 199, AIza<redacted> 2, gh<redacted> 1, sk-<redacted> 24 |
| cut | 445 items longer than 4,000 characters after scrubbing |
| gold, S1-ALL | of 463 labels: 354 have the skill in the top 10, 38 lower (added at their rank), 71 have no section of that skill in the ranking at all (no lead word now) |
| gold, S1-RATE | the System-1 rows by status: missing 39, open 1, scored 28; every section of a `scored` row (32, from 28 injections) has its item and section: 28 with the identical text, 4 composed differently (lines the live window had already seen) |
| gold first | 220 gold items carry 1993 pairs: the labeler sends them first |
| request size | step 1388 characters on average, section 1259, both 3015; the rubric and the template add 867 |
| would write | items.jsonl 9336309 bytes, sections.jsonl 1045959 bytes |

Reading it: about 22,000 pairs is the full labeling job. The ranked sections are mostly negatives by design (the live
gate injects the top section for 36 of 226 prompts). The 71 S1-ALL labels with no section now are pairs that the
old hook's ranking produced (the PIN arm) and that the current ranking gives no lead word; the validator counts them as
"no section", never as a disagreement.

## 4. The labeler (CONTRACT 2), 05:0xZ

**One request per (item, section).** The system message is the rubric `r1` (its sha256 over the rubric, the user template,
the step kinds and the questions starts `212765b5f2ea0ef5`): `rel` on the S1-RATE scale (0 unrelated; 1 same area, not
this step; 2 relevant to this step; 3 governs this step) and `use` as "would this section help with this step" (0 no;
1 it confirms what the step does; 2 the step would use it; 3 it would change what the step does). The user message holds
the step (its kind, then its text) and then the section as the hook would show it. The step comes first, so vLLM's
prefix cache (the quadlet sets `PREFIX_CACHE=1`, deploy/qwen.container:30) serves the rubric and the step for the other
sections of the same item; the pairs go out item by item, the gold items first.

**The answer** is exactly one line `rel=<0-3> use=<0-3> <a reason of 1-120 characters>`, matched whole
(`ANSWER_RX.fullmatch` on the stripped text). (Round 2: a reason of any length parses and is stored cut to 120
characters, marked `reason_cut`; section 14.) A leading EMPTY `<think></think>` is dropped first (a chat template can emit
one with thinking off); a think block with content is dropped only under `--thinking`, and is never stored. Anything
else is stored with `status: malformed`, `rel` and `use` null and the raw answer (300 characters): never guessed.

**vllm.** `POST http://127.0.0.1:8080/v1/chat/completions`, model `qwen3.8-27b-local`, the key read in this process from
`~/.config/qwen-builder/api-key` (never argv, never printed; a message that would carry it shows `<key>`). ONE function,
`chat_body`, builds the body with exactly five keys: model, messages, max_tokens (64; 1024 with `--thinking`),
temperature 0, and chat_template_kwargs with enable_thinking false unless `--thinking`. `check_body` refuses any other key
before a byte is sent, and names prompt_logprobs, best_of, echo and n on their own (AF-AP-201). A 429, a 5xx, a
connection error or a 200 that is not a chat completion retries after 2, 4, 8, 16, 32 and 60 s (7 attempts); any other
status refuses (exit 3).

**openjev.** teacher_label's `Client`, `Limiter`, `scrubbed`, `read_env`, `http_post`, `MODEL` and `input_tokens`, by
import. `Limiter` is not thread-safe, so ONE limiter serves every thread behind a lock (`LockedLimiter`): 60 requests a
minute, at least 1 s apart, whatever `--concurrency` is; each thread has its own `Client`, and their usage is summed. The
body: model `openjev-latest`, the state `{query: the step, chunk: the section}`, and both questions in one request; every
string through `scrubbed`. The answers are distributions (`common.distribution`); rel and use are their most probable
options, and the distributions are kept (`target_rel`, `target_use`). An answer `common.distribution` refuses is stored
as malformed.

**Both.** An append-only JSONL, locked (a second run exits 75): one record per pair, keyed
`<item id>|<section sha>|<backend>|<rubric>`, with the served model, the endpoint, the sha256 of the request body as sent
(`sent_sha`), the item text's sha, the section text's sha256, the tokens, the attempts and the time. A rerun skips the done
keys (ok and malformed alike; round 2: after it re-parses the stored malformed answers, section 14). The first failure sets a stop flag: no task starts after it and no vLLM attempt follows
(the resume test found the gap: section 7). The usage line prints at the end, also after a failure: stored, ok,
malformed, skipped, pending, seconds, pairs per second, and the backend's own counters.

**Not proved here:** no request reached the real vLLM or OpenJev (the brief forbids it). The real server's answer format,
its behavior with `enable_thinking: false` and its throughput are the smoke run's to measure (section 8).

## 5. The validator, the brief's question 2 and the proposed bar (CONTRACT 3), 05:0xZ

**The gold and its join.**
- S1-RATE: scripts/s1_scores.py's rows (`read_session`, `join_state`) of the System-1 hook with the status `scored`
  ONLY, their notes dropped. **Caveat (VERIFY-S1-RATE, task #309), printed in the validator's output:** a reply over
  about 200 characters before a tool call is recorded as thinking with no text block, so the scored rows are a subsample
  selected by reply length, and a `missing` row is no evidence of a non-answer. Then each section of an injection gets the injection's rel and use. A tool-path injection joins its item by
  tool_use_id (the wrapper's telemetry); a prompt-path one joins the human prompt of its session at most 2 s before it.
  Then the item's candidate with the same skill and heading (the identical text first).
- S1-ALL: Appendix E's 463 labels, each (prompt id, skill, R/P/N). The prompt whose promptId (else uuid) starts with the
  id: 153 of 153 found, 0 ambiguous. A label names a skill, not a section, so it joins the BEST-ranked candidate section
  of that skill: the one the hook would inject first.
- **The mapping.** Gold ordinal N=0 < P=1 < R=2. The labeler's rel maps by **A (primary, fixed before any label): 0 and
  1 to N; 2 to P; 3 to R.** Reason: S1-ALL's N is "incidental word overlap" (a section that shares words but not the
  task: S1-RATE's "unrelated" or "same area, not this step"), P is "plausibly useful" ("relevant to this step"), R is
  "the section is what the prompt is about" ("governs it"). B (0 to N; 1 and 2 to P; 3 to R) is reported beside it,
  and Spearman on the raw 0-3 rel is the number that needs no mapping. S1-ALL's labels are one agent's judgment (its own
  report calls them the INFERRED tier), a weaker gold than the real scores.
- **Per source:** exact and within-one agreement (Wilson 95%), Spearman's rho (Fisher-z 95%, variance 1.06/(n-3)),
  Kendall's tau-b, linear-weighted kappa, the confusion table, the counts (gold, joined, no item, no section, unlabeled,
  malformed, labeled), and the plain order on the same pairs.

**Measured now, with no labels** (the final dry run's `baseline_without_labels`, section 3):

| source | gold | joined | the plain order | a constant answer |
|---|---|---|---|---|
| S1-ALL | 463 (R 59, P 127, N 277) | 392 (71 no section) | Spearman with R/P/N: the hook's score 0.47, the live gate's flag 0.4316, the rank 0.1272 | the majority class (N) holds 0.5408 of the joined |
| S1-RATE (`scored` rows only) | 32 sections from 28 injections (rel 1: 3, 2: 19, 3: 10); the rows by status: scored 28, missing 39, open 1 | 32 | none: every gold section is a row the tool path injected (no score; its gate is always on) | the majority rel (2) is exact on 0.5938; a constant 2 is within one of all 32 |

**The brief's question 2: how many real scores the validator needs.** Computed with the tool's own `wilson` and
`fisher_ci`: at 32 scored sections (the final dry run) a Wilson interval at p = 0.70 is [0.5143, 0.8205] (+-0.15) and a
Spearman interval at rho = 0.47 is [0.1345, 0.7088]. The constant answer is strong, because rel 2 holds 59% of the
gold: an exact agreement of 0.75 clears the 0.5938 majority baseline (by its Wilson lower bound) from 34 sections, 0.80
from 21, and 0.70 only from 78. So: **at least 40 scored System-1 sections from at least 30 injections before the
S1-RATE numbers carry weight (+-0.14), 60 for +-0.12, and about 80 to separate a 0.70 labeler from the constant
answer.** Three limits of this gold: it holds only sections the live hook injected (no rel 0, so it cannot check the
labeler's negatives); its within-one says nothing while the gold spans 1-3 (a constant 2 is within one of every section); and the scored rows are a subsample selected by
reply length (the caveat), which may not be random with respect to rel. S1-ALL's 392 joinable pairs are enough now: a Spearman of 0.60 has the interval [0.53, 0.66] there.

| n | Wilson 95% half-width at p = 0.70 | Fisher-z 95% interval at rho = 0.47 |
|---|---|---|
| 20 | 0.187 | [0.0207, 0.7614] |
| 40 | 0.137 | [0.1765, 0.6868] |
| 60 | 0.113 | [0.2381, 0.6512] |
| 100 | 0.088 | [0.296, 0.6138] |
| 392 | 0.045 | [0.3866, 0.5458] |

**Proposed bar (the coordinator decides).** D-096 (2): the labeler is checked against the real scores BEFORE its labels
are used.
1. Format: malformed at most 2% of the pairs labeled.
2. S1-ALL (n about 392): `beats_plain_order` (the Fisher-z 95% lower bound of the labeler's Spearman above the plain
   order's Spearman on the same pairs: 0.47 now, so the labeler needs about 0.55 at n = 392), AND map-A exact at least
   0.64 (the 0.54 majority baseline plus 0.10), AND linear kappa at least 0.40.
3. S1-RATE (`scored` rows only), once there are at least 40 sections from at least 30 injections: exact at least 0.75
   with its Wilson lower bound above the majority baseline (0.59 now). Within-one is not a criterion while the gold spans
   1-3.
4. A labeler that passes 1 and 2 may keep labeling while 3 waits for scores; its labels feed GEPA or a fine-tune only
   after 3 passes.

## 6. The dataset (CONTRACT 4), 05:0xZ

**What matches scripts/laya_ft/.**
- Rows in `build_dataset.make_row`'s shape: item_id `s1-<state_sha[:20]>`, question_id, question_sha, state_sha, options,
  question, state, sources (and cut, when fitted). The state is `{query, chunk}`, the shape of the `ap.violates_row`
  rows: fit.py cuts the query and never the chunk. Two rows per pair, one per question.
- Labels in teacher_label's record shape: key (`common.label_key`), item_id, question_id, question_sha, sent_state_sha,
  options, target (one-hot for vllm, the distribution for openjev), answer, model, endpoint, input_tokens, attempts, ts;
  and backend, rubric, synth_key, labeled_state_sha. `common.join_labels` (the trainer's own join) accepts them (test).
- Laya's own window fit, `build_dataset.Fitter` in the Laya venv (the checkpoint's max_len 1024, head_max_len 256,
  revision 1c5edc17): a short state stays whole; a long step is cut (15,034 to 2,794 characters in the probe) and its
  section kept whole; a section that alone overflows the window gives no row, counted `unfit.<question>` (the probe found
  this crash path; the test runs in the Laya venue here and skips loudly where the venv is absent).
- The manifest: kind, version, backend, rubric and its sha, the candidates' manifest sha and file digests, the labels
  file's sha, the counts (rows per question, answers per option, cut, unfit, merged duplicates, conflicts), fitted and
  the model's fingerprint, the questions' shas, the code digests, the dataset file's sha and bytes.

**What differs, and what that blocks.**
- Two new question ids, `skill.governs` (the rel scale) and `skill.helps` (the use scale), choice questions over four
  options each. `common.QUESTIONS` does not hold them, so **`common.load_dataset` refuses these rows today** ("the question
  is not this code's 'skill.governs'"); a test pins that refusal, so it goes red when common.py learns them. The source
  kind `transcript` is new too, and `common.row_identities` would refuse it next. Both are changes to
  scripts/laya_ft/common.py, outside this lane's boundary (MODIFY: none): NOT done (section 11).
- No held-out sample exists for this data (build_dataset's D-3 samples are J2, J2c and AP rows). The held-out test
  D-096 (1) names, real scores Laya never trained on, belongs to the training lane.
- A label was given on the uncut state. A fitted row's `sent_state_sha` is the fitted state's (so `join_labels` holds),
  and `labeled_state_sha` keeps the state the labeler saw.

**Where it goes.** `dataset --out <scratch or PC>` writes dataset.jsonl (the texts), manifest.json and labels.jsonl after
the value gate. `--commit-dir docs/research/findings/laya-ft-labels/2026-09-26-synth/` writes only
`dataset-manifest.json` and `labels.jsonl` (ids, digests, targets; a test proves no step or section text reaches it): the
two files the recorded label directories hold. The directory does not exist yet: no pair is labeled (NOT done).

## 7. Tests and the mutation run (EVIDENCE DEMANDS 3), 05:1xZ

`tests/test_s1_synth.py`: 21 tests, fixture transcripts in the real record shapes (fake content, fake secrets), local fake
HTTP servers for both backends (`ThreadingHTTPServer` on 127.0.0.1:0, proxies unset), the value gate reading a fixture
env file, the vLLM key a fixture file. The oracles are independent of the tool: the hook's ranking is recomputed by the
test's own instances of the hook (the four floors lifted by name there), a section's text is checked against its skill
file line by line, the servers keep the raw bytes they receive, and every validator number is worked out by hand in
the test's docstring.

| brief demand | test | mutants it reds |
|---|---|---|
| the thinking and assistant-text exclusion | `test_items_are_human_prompts_and_tool_inputs_only` (the exact item set; 10 canaries in thinking, text, dispatch, task-notification, interrupt, meta, compaction and tool-result records absent from every byte; the prompt's and the command's canaries present) | M01 items-origin-dropped, M02 items-assistant-blocks, M32 gold-dropped |
| scrubbing before any byte leaves | `test_scrubbing_happens_before_any_byte_leaves` (the three shaped values absent from the files and from every request of both backends); `test_the_value_gate_refuses_before_any_write` (exit 4, nothing written); `test_the_cut_comes_after_the_scrub` (AF-AP-127); `test_a_dry_run_writes_nothing_opens_no_secret_and_prints_counts_only` | M03 scrub-identity, M04 gate-skipped, M05 dry-run-writes, M29 cut-before-scrub, M30 cut-dropped |
| the candidate set equal to the hook's own ranking | `test_the_candidates_are_the_hooks_own_ranking` (the top 10 and their scores; the gate flags; the rows; the skill-file oracle; the live gate's first sha equal to the stored one; a gold skill added at its real rank) | M06 floors-kept, M07 ranking-reversed, M08 top-cut, M09 rows-dropped, M10 section-without-pointer |
| the forbidden vLLM parameters never sent | `test_the_vllm_body_never_carries_a_forbidden_parameter` (every body has exactly the five keys; each of the four forbidden keys refused with 0 requests sent) | M11 guard-off, M12 body-adds-n, M28 thinking-on |
| concurrency held at its bound | `test_concurrency_reaches_and_never_passes_its_bound` (the server holds the first 3 until 3 are in flight; never 4) | M13 pool-plus-two, M14 pool-of-one |
| resume skips done keys | `test_a_rerun_skips_the_done_keys` (3 stored, then 503 until the retries are spent: exactly the sleeps 2, 4, 8, 16, 32, 60; the rerun sends 5 of 8) | M15 done-keys-ignored, M33 stop-ignored |
| a malformed answer stored as malformed | `test_a_malformed_answer_is_stored_as_malformed_never_guessed` (8 answers: 2 parse, 6 malformed with their raw text; the rerun sends 0) | M16 lenient-parse, M34 empty-think-kept, M35 any-think-dropped |
| the validator's numbers on hand-made gold | `test_the_validator_numbers_on_hand_made_gold`, `test_the_validator_numbers_on_hand_made_s1_rate_gold`; end to end through s1_scores: `test_the_validator_joins_the_real_readers_output_on_the_fixture` | M20 exact-is-within-one, M21 spearman-no-ties, M22 map-a-is-b, M23 prompt-link-10s, M24 s1all-worst-rank, M38 late-counted (a `late` row taken as gold) |
| the openjev backend (reuse, limits, key) | `test_the_openjev_backend_reuses_teacher_label` (one limiter for three threads: arrivals 1 s apart on a real clock); `test_the_key_never_reaches_a_message`; `test_a_second_run_on_the_same_labels_file_is_refused` | M17 limiter-per-thread, M18 safe-keeps-key, M19 lock-dropped, M27 openjev-malformed-guessed |
| the dataset | `test_the_dataset_rows_join_with_laya_ft_and_the_loader_names_its_gap`; `test_the_dataset_command_keeps_text_out_of_the_commit_dir`; `test_the_dataset_fits_laya_window_in_the_laya_venue` (the real Fitter; loud skip where the Laya venv is absent) | M25 target-off-by-one, M26 question-sha-swapped, M36 unfit-not-caught |
| the sample | `test_the_sample_takes_tools_in_turn_then_strata_in_turn` (worked by hand; the same seed, the same calls) | M31 tools-not-in-turn |
| ASCII JSON | `test_the_files_are_ascii_json_and_a_line_separator_round_trips` | M37 non-ascii-json |

Round 2 (section 14) changed the malformed-answer test to 10 answers (3 parse, 7 malformed), added
`test_a_resume_reparses_a_stored_answer_and_asks_nothing` and
`test_an_unreadable_laya_path_counts_as_absent_and_the_laya_test_skips` (23 tests), and added nine mutants, M39 to
M47 (Appendix B).

**The mutation run** (`<scratchpad>/synth1/mut/mutants.py`, Appendix A): each mutant of scripts/s1_synth.py runs the test
file in its own mirror of the tree; a kill is a FAILED test, never an error (AF-AP-223); the unmutated baseline must pass
first and a control mutant (a comment) must stay green. On the final code, after the resume (05:45Z-05:58Z):
**baseline 21 passed; control green (twice); 38 of 38 mutants KILLED, each by FAILED tests, 0 errors, 0 invalid, 0
survived.** (Before the resume, 37 of 37 on the code before the scored-only change.) The lines are in Appendix A.

**Defects the tests and the probes found in my own code, all fixed before the final run:**
- The resume test found that after a refusal the one worker had already taken the next task, which retried 7 more
  times (17 requests, 12 sleeps where 7 and 6 were due). A real run would keep every in-flight worker retrying for about
  two minutes after a failure. Fix: a stop flag, set by the task that fails, checked before each task and each vLLM
  attempt (M33 proves the test sees it).
- The Laya probe found that a section which alone overflows Laya's window raised `fit.Unfit` and would abort the whole
  dataset step. Fix: no row, counted `unfit.<question>` (M36).
- `dumps_line` wrote non-ASCII JSON, so a raw U+2028 or U+2029 could reach items.jsonl and split a record for a
  `str.splitlines()` reader (`common.jsonl_lines` documents the trap). Fix: ASCII JSON (M37).
- One-level round-robin over the 299 sorted strata would have given Read and Grep about 7 items each (the small dry run
  showed it). Fix: two-level round-robin (M31).
- My own fake server counted a request as in flight until after its response was written, so the client's next request
  could briefly read as a fourth in flight: one flake in the first 14 full runs (in the M03 run). Fix: count out before the
  answer is written; then 25 runs of the concurrency and OpenJev tests: 0 failures, and M03 now reds only its two
  scrubbing tests.

## 8. The PC commands, the time estimate and what must not run beside it (EVIDENCE DEMANDS 4), 05:3xZ

Paths: the texts stay in the session scratchpad and in `/home/rocco/synth1` on the PC (outside the clone); the PC clone
is `/home/rocco/agent-factory` (scripts/pc_suite.sh:27). Every step that runs longer than a few seconds on the PC runs in
the background, because one `pc.sh` call is capped at 120 s and may re-run its command (pc-bridge-lanes).

```bash
# 0. After landing and pushing scripts/s1_synth.py, ff-sync the PC clone the usual way, then compare the bytes
sha256sum scripts/s1_synth.py
bash scripts/pc.sh 'sha256sum /home/rocco/agent-factory/scripts/s1_synth.py'          # must be equal

# 1. Sandbox: the real candidate set (the value gate reads the known secret sources; about 100 s)
SCR=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/synth1-run
MAIN=/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl
mkdir -p $SCR
python3 scripts/s1_synth.py candidates --transcript $MAIN --out $SCR/cand > $SCR/candidates.json; echo rc=$?
#    rc 4: the value gate found a known secret's value in the texts; nothing was written. Do not ship; report it.

# 2. Sandbox -> PC: 40,000-character base64 parts (the pc_suite.sh pattern), then the sha256 on both sides
tar -C $SCR/cand -czf $SCR/cand.tgz items.jsonl sections.jsonl manifest.json
sha256sum $SCR/cand.tgz
base64 -w0 $SCR/cand.tgz > $SCR/cand.b64
split -b 40000 -d -a 4 $SCR/cand.b64 $SCR/part.
bash scripts/pc.sh 'mkdir -p /home/rocco/synth1/parts && rm -f /home/rocco/synth1/parts/part.*'
for f in $SCR/part.*; do bash scripts/pc.sh "printf %s '$(cat $f)' > /home/rocco/synth1/parts/${f##*/}" > /dev/null || { echo "FAILED $f"; break; }; done
bash scripts/pc.sh 'cd /home/rocco/synth1 && cat parts/part.* | base64 -d > cand.tgz && sha256sum cand.tgz && mkdir -p cand && tar -C cand -xzf cand.tgz && ls -la cand'
#    the sha256 must equal the sandbox's; the labeler checks each file against the manifest again before any request

# 3. PC: the smoke, 120 pairs (gold items first), in the background
bash scripts/pc.sh 'cd /home/rocco/agent-factory; setsid nohup python3 scripts/s1_synth.py label --candidates /home/rocco/synth1/cand --out /home/rocco/synth1/labels.jsonl --backend vllm --limit 120 > /home/rocco/synth1/smoke.log 2>&1 < /dev/null & echo started'
bash scripts/pc.sh 'tail -3 /home/rocco/synth1/smoke.log; wc -l < /home/rocco/synth1/labels.jsonl'      # repeat until the usage line
#    the counts are the usage line's file_ok, file_reparsed and file_malformed (the file as the tool reads it; round 2);
#    a run with --limit 0 prints them at any time and sends nothing. Never count with grep: a re-parsed key keeps
#    its round-1 line. The served model (a re-parsed key's two lines count twice; only the name matters):
bash scripts/pc.sh 'grep -o "\"model\": \"[^\"]*\"" /home/rocco/synth1/labels.jsonl | sort | uniq -c'

# R2. Round 2, on the smoke file already on the PC (108 rows, 74 malformed by round 1's parse), after step 0 with the
#     round-2 code. R2-1 re-parses it (appends a reparsed record per answer that parses now; no request; seconds):
bash scripts/pc.sh 'cd /home/rocco/agent-factory && python3 scripts/s1_synth.py label --candidates /home/rocco/synth1/cand --out /home/rocco/synth1/labels.jsonl --backend vllm --limit 0 2>&1 | tail -2'
#     expect stored=0 reparsed=74 reparse_unchecked=0 file_ok=34 file_reparsed=74 file_malformed=0; an answer stored
#     cut at 300 characters shows as reparse_unchecked and stays malformed. A second R2-1 appends nothing.
#     R2-2 finishes the smoke's 120 (120 - 108 = 12 pending; --concurrency 3 while a Hermes lane holds the route):
bash scripts/pc.sh 'cd /home/rocco/agent-factory; setsid nohup python3 scripts/s1_synth.py label --candidates /home/rocco/synth1/cand --out /home/rocco/synth1/labels.jsonl --backend vllm --limit 12 --concurrency 3 > /home/rocco/synth1/smoke2.log 2>&1 < /dev/null & echo started'
bash scripts/pc.sh 'tail -2 /home/rocco/synth1/smoke2.log'                                             # repeat until the usage line
#     then decide by the stop rule below, on that usage line's file_malformed.

# 4. PC: the full run; it resumes after the smoke's 120. A second launch while one runs exits 75, so a re-run is safe.
bash scripts/pc.sh 'cd /home/rocco/agent-factory; setsid nohup python3 scripts/s1_synth.py label --candidates /home/rocco/synth1/cand --out /home/rocco/synth1/labels.jsonl --backend vllm > /home/rocco/synth1/label.log 2>&1 < /dev/null & echo started'
bash scripts/pc.sh 'wc -l < /home/rocco/synth1/labels.jsonl; tail -2 /home/rocco/synth1/label.log'       # poll every 10 to 20 min
#    rc 3 in label.log (refused: a non-retryable status, or 7 attempts over about 2 minutes): read the reason, fix it, re-run step 4.

# 5. PC -> sandbox: the labels (pc_fetch.sh checks the size)
bash scripts/pc.sh 'cd /home/rocco/synth1 && gzip -kf labels.jsonl && sha256sum labels.jsonl'
bash scripts/pc_fetch.sh /home/rocco/synth1/labels.jsonl.gz $SCR/labels.jsonl.gz
gunzip -f $SCR/labels.jsonl.gz && sha256sum $SCR/labels.jsonl                                           # must equal the PC's

# 6. Sandbox: the validator. It can run as soon as the 1,993 gold-first pairs are labeled (steps 5-6 on a partial file).
python3 scripts/s1_synth.py validate --candidates $SCR/cand --transcript $MAIN --labels $SCR/labels.jsonl --backend vllm --out $SCR/validate.json

# 7. Sandbox: the dataset, only after the bar passes (the Laya venv fits each state to Laya's window)
/root/venv-laya-probe/bin/python scripts/s1_synth.py dataset --candidates $SCR/cand --labels $SCR/labels.jsonl --backend vllm --out $SCR/dataset --model-dir /root/hf-laya-probe/hub/models--convaiinnovations--laya/snapshots/1c5edc17a7acd8701df6fc341c0d179f1c62c982/typed-decisions --commit-dir docs/research/findings/laya-ft-labels/2026-09-26-synth

# 8. When done: delete $SCR (it holds session text, scrubbed) and /home/rocco/synth1 on the PC
```

The OpenJev alternative runs from the sandbox (the API is external; D-078): step 3 and 4 with
`--backend openjev --env-file /root/.codiv/api.env` and `--out $SCR/labels-openjev.jsonl`, no PC step. At its limit of 60
requests a minute, 21,960 pairs take at least 21,960 / 60 = 366 minutes (6.1 h), whatever `--concurrency` is.

**Decide after the smoke (step 3, or R2-2 in round 2):** at most 2 malformed of 120 (the usage line's
`file_malformed`; the rule is unchanged in round 2), else stop and look at their `raw` answers (the rubric or
the parse); the served model is `qwen3.8-27b-local`; `pairs_per_s` in the usage line gives the full run's time as
21,960 / pairs_per_s seconds; `prompt_tokens` / stored gives the real tokens per request.

**The estimate** (computed from the final dry run; the smoke replaces it). Requests: 21,960 pairs of about 3,882
characters each (the step 1,388, the section 1,259 on average for a unique section, 3,015 per pair, the rubric and
template 867). At an ASSUMED 3.5 characters per token that is about 1,109 prompt tokens, and about 30 output tokens (an
assumption; max_tokens 64).
- Decode: 21,960 x 30 = 658,800 tokens at about 6 x 45 = 270 tokens/s aggregate (measured 2026-09-16: about 45 for one
  request, near-linear to about 310 at 7: `~310 tok/s aggregate`, PC-BRIDGE.md:168): 2,440 s, **0.7 h**.
- Prefill: 24.4M tokens with no reuse; about 9.7M with the prefix cache (each item's step and the rubric once, then
  the section per pair; `PREFIX_CACHE=1` in deploy/qwen.container:30, not verified on the running server). The only
  prefill rate measured on this GPU is llama.cpp's 1,007.5 tokens/s at a 67,250-token prompt
  (`1,007.5 t/s`, docs/research/FINDINGS-LOCAL-BUILDER-QWEN38.md:150): another engine at a long context, so a floor, not a vLLM number.
  At that floor: **2.7 h** with the cache, **6.7 h** without.
- **Total: about 3.4 h with the prefix cache, 7.4 h without, at the prefill floor; vLLM's batched prefill of short
  prompts is likely faster.** The gold-first 1,993 pairs (9% of the job) come first, so the validator can run after
  roughly the first 20 to 40 minutes.

**What must not run beside it:**
- A restart or stop of `qwen.service`, or a GPU window (D-078, D-081, D-088 stop the vLLM service): in-flight requests
  fail, the labeler retries for about 2 minutes (2+4+8+16+32+60 s) and then stops with exit 3; a re-run of step 4
  resumes.
- A local-route Hermes lane, or the owner's own local-route Hermes session: the KV cache is not the limit (6 requests of
  about 1,200 tokens use about 7,000 of its 222,822 tokens, D-097), but the GPU's throughput is shared and both slow
  down. If a lane must run, use `--concurrency 3`.
- Anything that sends `prompt_logprobs`, `best_of`, `echo` or `n` to the server (AF-AP-201); the labeler cannot.
- A second labeler on the same labels file (the lock refuses it, exit 75).

## 9. The gates (EVIDENCE DEMANDS 5), 06:2xZ

**The set.** tests/test_s1_synth.py and every test file that names a file this tool imports or loads (transcript_export,
the hook system1-context.py and its hook_context.py, s1_scores, teacher_label, laya_ft's common, build_dataset and fit):
`grep -l -E 'transcript_export|s1_scores|hook_context|system1-context|teacher_label|build_dataset|laya_ft|s1_synth' tests/*.py`
gives 18 files, set=337985e6e726 (`sort <list> | sha256sum | cut -c1-12`; the same list at 05:00Z and at 06:2xZ);
harness-ports/tests/ names none of them. On this disk the set runs in two parts (env-tool-quirks): part 1 is the 17 files
without tests/test_vendored_manifest.py (set=ac3b6ebef974), whole, twice; part 2 is tests/test_vendored_manifest.py, its
57 tests one at a time, each through `bash scripts/test_summary.sh <node id> --basetemp <fresh>` with the basetemp deleted
right after, twice. The bytes under test: scripts/s1_synth.py sha256 374cc5ede5b3ec32..., tests/test_s1_synth.py
9f3bdde0847eb666... (neither changed after 05:44:22Z). The tree's HEAD moved from 2a50a65 to 5673d6e during run A (the
coordinator's four commits, 06:06:59Z to 06:09:18Z: briefs, the ledger, the wiki, the incident log, the orchestration
skill and the manifest); none touches a file of the set or of the tool's imports. Some tests read files those commits
changed (the orchestration skill through the hook's corpus, which this lane's tests rank on; the wiki live-state; the
ledger): run A saw the change mid-run and run B saw only the new bytes, and both pass.

| run | start, duration | pasted |
|---|---|---|
| part 1, run A (17 files) | 06:00:16Z, 631 s | `pytest-exit: 0`; `pytest-summary: 1106 passed in 631.43s (0:10:31)` |
| part 1, run B (17 files) | 06:11:12Z, 574 s | `pytest-exit: 0`; `pytest-summary: 1106 passed in 573.84s (0:09:33)` |
| part 2, pass A (57 tests, one at a time) | 06:20:53Z to 06:23:47Z | 49 x `pytest-summary: 1 passed` (exit 0), 8 x `pytest-summary: 1 failed` (exit 1) |
| part 2, pass B (57 tests, one at a time) | 06:24:09Z to 06:27:10Z | 49 x `pytest-summary: 1 passed` (exit 0), 8 x `pytest-summary: 1 failed` (exit 1): the same 8 |
| tests/test_s1_synth.py alone (set=7f2ad640fd36), twice | 06:27:38Z, 06:27:57Z | `pytest-summary: 21 passed in 19.05s`; `pytest-summary: 21 passed in 18.87s` (exit 0 both) |

Per pass, the whole set: 1106 + 49 = 1155 passed, 8 failed, 0 skipped, of 1163 (part 1 prints no skip line under `-rs`;
the Laya-venue test ran). The same totals as the two pre-resume whole-file runs, which ended 05:13Z and 05:28Z on the code
before the scored-only change: `pytest-summary: 8 failed, 1155 passed in 781.90s (0:13:01)` and
`pytest-summary: 8 failed, 1155 passed in 846.88s (0:14:06)`.

**The 8 failures** are the same in both passes and in both pre-resume runs (D3). Their first assertion lines:
- test_committed_manifest_matches_fresh_generation, test_committed_manifest_passes_check_at_a_later_head,
  test_declared_root_symlink_is_refused_by_name: `AssertionError: FAIL: vendored manifest drift: line 21: committed='| `
  followed by the `.claude/ (first-party)` row.
- test_changed_vendored_byte_names_root_and_returns_one, test_docs_byte_change_names_docs_row:
  `assert 'sandbox-kit/docs/' in "FAIL: vendored manifest drift: line 21: ...` (the same drift is reported first).
- test_real_claude_split_counts_and_class_file: `assert ['20', '0'] == ['18', '0']`;
  test_k1h_claude_classification_and_remainder: `assert 20 == 18`;
  test_k1h_honey_copy_byte_change_falls_back_to_first_party: `assert 21 == 19`.

The cause, verified: a re-run of test_committed_manifest_matches_fresh_generation alone (06:3xZ) prints
`.claude class drift: fast-jev-output/.gitignore: committed=<missing> generated=first-party`, and the counts match the
generator's code: scripts/vendored_manifest.py hashes the roots `.claude/` and the declared `sandbox-kit/` folders
(`VENDORED_ROOTS`, line 54) and excludes only `.git`, `__pycache__`, `node_modules` and `*.pyc` (lines 38-39), not
git-ignored files. The working tree's `.claude/` holds
two git-ignored files, `.claude/fast-jev-output/.gitignore` and one `bash-toolu_*.txt` (both dated 2026-09-25 02:41,
ignored by the folder's own `*`; `git ls-files --others --ignored --exclude-standard .claude/`), so the fresh first-party
count is 18 + 2 = 20, and 21 after the honey test's byte change. This lane's files are under scripts/, tests/ and tasks/,
not generator inputs. Not proven by a run without the two files: that would change the tree outside this lane's boundary.

**Static checks** (06:1xZ, the final bytes):
- `python3 -m pyflakes scripts/s1_synth.py tests/test_s1_synth.py`: rc 0, no output.
- `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>`: 0 for scripts/s1_synth.py, tests/test_s1_synth.py and this report
  (re-run after this report's last edit; the lane's final message pastes that result).
- `python3 scripts/report_lint.py` on this report: `11 refs — OK 11, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
- `python3 scripts/ap_screen.py scripts/s1_synth.py`: 19 hits in two classes, both explained, neither changed. AP-32 x 18:
  the hashing lines (the rubric sha, the item and section shas, the manifest's file hashes): sha256 is the tool's
  identity key by design. AF-AP-72 x 1, line 1224, `int(c["gate"])`: `c["gate"]` is the tool's own bool from the hook's
  plan, not external data.
- `python3 scripts/ap_screen.py --tests tests/test_s1_synth.py`: 3 hits. AP-66 x 2: line 77 lifts the floors on the
  test's own hook instance (the oracle's, the same move the tool makes on its own instance); line 259 is the fake
  server's own counter. AF-AP-80 x 1, line 662: the key's absence from the output and from the written file is the
  assertion itself.

## 10. Self-attack: the three most likely ways this change is wrong, 05:3xZ

1. **The candidates are ranked on the scrubbed text, not on the raw prompt the live hook saw.** Measured on the 33
   prompts the scrubber changed (in process, counts only): the top section is the same for 33 of 33, and the live
   gate's choice for 32 of 33; the top-10 set is the same for 25, in the same order for 16. So the lower ranks move for
   8 of the 226 prompts (4%); tool inputs (391 changed) move the same way, not measured. This is the brief's order
   (scrub the item, then rank the item), and the stored item reproduces its candidates exactly (the ranking test). What
   is ruled out: a secret reaching the ranking's output. What is not: the candidate set of those items is not exactly
   the one the live hook ranked.
2. **The real labeler's answers.** Every test uses a fake server. The real Qwen's compliance with the one-line format, its
   output with `enable_thinking: false` (an empty think block is handled; one with content is malformed) and whether
   64 tokens suffice are unproven. The smoke's stop rule (at most 2 malformed of 120) catches a format failure before
   the other 21,840 requests, at the cost of 120. (Round 2: the smoke found exactly this, 74 of 108 answers with a
   reason past 120 characters; section 14.)
3. **The gold is thin and selected.** S1-RATE: 32 sections from 28 scored injections, all tool-path rows the live hook
   injected, rel 1-3, none 0, and a subsample selected by reply length (the caveat): it cannot check the labeler on
   negatives, which are most of the 21,960 pairs. S1-ALL: one
   agent's labels on pairs that the old and the new ranking selected, and 71 of its 463 have no section in today's
   ranking. What is ruled out: the join itself (the hand-made gold tests pin every count, including each failure path;
   the end-to-end test runs through the real s1_scores reader; 32 of 32 real scored sections and 392 of 463 S1-ALL
   labels join). What is not: that agreement on this gold predicts agreement on the ungated negatives.

Also weighed: the sample gives each tool an equal share, so 646 of the 2,226 items are Read and Grep calls whose text is
a path or a pattern, mostly negatives (by design; drop them with a filter if the labels show them useless: not built).
The value gate was never run on real data by this lane (it reads the real secret sources); fixtures prove it, and step 1
of section 8 runs it for real.

## 11. NOT done

- **No real labeling.** No request reached vLLM or OpenJev (the brief: the coordinator runs the PC steps). So there are no
  labels, no validator numbers on real labels, no dataset rows, and nothing under
  `docs/research/findings/laya-ft-labels/2026-09-26-synth/` (the dataset step creates it after the bar passes).
- **The value gate did not run on the real candidate set** (this lane may not read the real secret sources; a dry run
  writes nothing). Section 8 step 1 runs it.
- **scripts/laya_ft/common.py does not know the new questions** (`skill.governs`, `skill.helps`) or the source kind
  `transcript`: `common.load_dataset` refuses these rows, which a test pins. Before `train.py` can read the dataset,
  `QUESTIONS` needs both entries (the dicts are `s1_synth.QUESTIONS`) and `row_identities` the `transcript` kind.
  Outside this lane's boundary (MODIFY: none); a change for the coordinator.
- No held-out split of real scores for D-096 (1): the training lane's.
- S1-RATE-R1 (task #318) will add a status to scripts/s1_scores.py after this lane lands; the tool reads only the
  `scored` status and the fields it reads today, so a new status is simply not gold. Not re-checked against R1 (it does
  not exist yet).
- The time estimate rests on assumed characters per token and answer length and on a llama.cpp prefill floor; the smoke
  measures all three.
- The bar is a proposal; the coordinator decides it.
- The anti-pattern screen's tells (section 9) are explained, not changed.
- The 8 tests/test_vendored_manifest.py failures (D3) are traced by their message, the generator's code and the
  count, not by a run without the two ignored files: that needs a tree change outside this boundary (or task #232).
- Round 2's NOT-done items are in section 14.

## 12. DISCREPANCIES

- **D1. The premise's subagent count.** "subagent transcripts 305" counted the top-level agent-*.jsonl only; the brief's
  "every file under its subagents/" is `s1_scores.transcript_files`, which also reads the files under
  `subagents/workflows/` (344 subagent files at 03:4xZ; 349 transcript files in all at the final dry run). Not a
  mismatch that matters.
- **D2. This lane's own S1-RATE lines read as missing, CONFIRMED by VERIFY-S1-RATE (task #309).** `s1_scores.py` marked
  s1-efe951f5 (and this lane's other early lines) `missing`: at 03:4xZ my subagent transcript held 19 text records
  against 57 tool_use records. VERIFY-S1-RATE found the cause: a reply over about 200 characters before a tool call is
  recorded as thinking with no text block. My early replies put the score line at the top of a longer text, so they
  were lost. Since the resume each score is a short text of its own. The validator uses `scored` rows only (the caveat).
- **D3. 8 failures in tests/test_vendored_manifest.py in every run of the gate set, the same 8, not caused by this
  lane.** `.claude/fast-jev-output/` (a tool-output folder dated 2026-09-25 02:41 whose own `.gitignore` holds `*`, so
  git never shows it) is in the working tree's `.claude/`; the test's fixture copies that tree, so a fresh manifest
  differs from the committed one ("`.claude class drift: fast-jev-output/.gitignore: committed=<missing>`"). My files
  are not generator inputs. This is the known class of task #232 (env-tool-quirks: the copy takes ignored files under
  `.claude/`); not fixed here.
- **D4. Scratch over 300 MB during the gate set.** The set's basetemp reached 551 MB and 697 MB: test_vendored_manifest.py
  copies the whole `.claude/` for each test (73 MB each), and the Laya trainer test writes 100 MB. Each basetemp was
  deleted as soon as its run ended; this lane's own tests use 8.9 MB. I had missed the env-tool-quirks rule (run that
  file one test at a time); the third whole-file run was orphaned by the restart and stopped by the coordinator at 43%.
  After the resume the file ran one test at a time (section 9).
- **D5. Six transcript lines are not valid JSON:** 2 in the main transcript (lines 16261 and 67409) and 4 in subagent
  files, whole lines, not torn tails. The tool skips and counts them (`unparseable_lines`).
- **D6. Another live lane in this tree.** Besides VERIFY-SCRUB2, `git status` at 05:1xZ showed modified
  proofs/registry.yaml, scripts/validate-ledger and tests/test_validate_ledger.py, and untracked
  tasks/briefs/i59/I59-A-report.md and tests/test_attested_inputs.py. Not touched. At 06:1xZ
  (`git --no-optional-locks status --short`) only untracked files remained: this lane's three, VERIFY-SCRUB2's report
  and tasks/briefs/i59/VERIFY-I59-A-report.md; the I59-A changes had been committed as a patch file (4b1980c). The
  coordinator's commits during gate run A are listed in section 9.
- **D7. S1-ALL labels name a skill, not a section.** The brief says "per prompt and skill"; the validator joins each to
  the best-ranked section of that skill (section 5).
- **D8. The scrubber's opaque rule** replaced 2,128 runs of 40 or more `[A-Za-z0-9_-]` characters (hashes, long names) in
  the items (the final dry run's count): the labeler sees `<opaque-redacted>` there. The exporters accept that cost; session_export's pseudonym
  callable would keep such runs apart, but it needs a key this lane may not read.
- **D9. The transcripts grew during the lane:** 225 human prompts at 03:4xZ, 226 at the final dry run; the gold grew
  from 3 to 28 scored System-1 injections.
- **D10 (round 2). The model does not keep the rubric's reason length.** Round 1 put the 120-character limit inside
  the match, and round 1's own test pinned a 121-character reason as malformed: a strict parse built on an
  assumption about the real model that the smoke proved false (74 of 108). The rubric is unchanged; the parse now
  cuts instead of refusing (section 14).
- **D11 (round 2). The sandbox runs as root; CI does not.** The Laya-venue test's guard used `Path.exists()`, which
  raises PermissionError under /root on a non-root runner, so CI (run 36224456809) failed where the docstring
  promised a loud skip. Every gate this lane ran was as root, so none could see it; the round-2 fix was checked as
  `nobody` too (section 14).

## 13. Files (round 1 created them; round 2 changed the two code files; no git write)

- `scripts/s1_synth.py` (1,473 lines after round 2; 1,424 in round 1): the rubric 125-162, the vLLM wire contract
  164-217, reading the transcripts 220-365, the hook's own ranking 368-452, candidates 455-699, loading 702-757,
  the labeler 760-1077, statistics 1080-1178, the validator 1181-1305, the dataset 1308-1405, the command line
  1408-1473.
- `tests/test_s1_synth.py` (1,125 lines, 23 tests after round 2; 1,017 lines, 21 tests in round 1).
- `tasks/briefs/system1/SYNTH1-report.md` (this report).
- Scratch (`<scratchpad>/synth1/` in round 1, `<scratchpad>/synth1r2/` in round 2; each deleted at the end but for
  the harness text kept in Appendices A and B): the dry-run JSONs, the gate logs, the mutation harness.

## 14. Round 2: the long-reason answers and the CI failure (task #308 round 2), 07:4xZ

Round 2 fixes two findings in this lane's landed files (origin 626fc4c): (A) the PC smoke stored most answers as
malformed, and (B) stage0-ci failed on this lane's Laya-venue test. Both fixes stay inside the lane's own files.

### A. The long-reason answers

**The finding (the coordinator's PC smoke).** The smoke ran with `--limit 120 --concurrency 3` and was stopped by pid
at 108 rows. All 108 carry the model `qwen3.8-27b-local`. 74 were `malformed`, each with the why "not one line
`rel=<0-3> use=<0-3> <reason>`". The raw answers were well-formed single lines whose reason ran past 120 characters
(completion_tokens 31 to 42 in the three examples). The model does not keep the rubric's "at most 120 characters".

**The premise, re-measured before any change (verified).** At 73261cd, `ANSWER_RX` (scripts/s1_synth.py@73261cd:154) was
`rel=([0-3]) use=([0-3]) (\S.{0,119})` in a fullmatch. In process, a synthetic answer with a 149-character reason
parsed to None; with a 120-character reason it parsed; with 121 it did not. No commit had touched the file since
73261cd. This lane did not read the 108-row file (it is on the PC); its facts come from the coordinator's message.

**The fix (scripts/s1_synth.py).**
- The parse goes by structure: `ANSWER_RX = re.compile(r"rel=([0-3]) use=([0-3]) (\S.*)")`, still a fullmatch on the
  stripped answer (line 158). `.` stops at a newline, so two lines still fail. The reason may be of any length.
  `parse_answer` (789-801) returns (rel, use, reason, cut): the reason kept to REASON_MAX (120) characters, and `cut`
  true when it was longer. A new record stores the flag as `reason_cut` (905). Everything else stays malformed as in
  round 1: two lines, a rel or use outside 0-3, the fields out of order, text before `rel=`, no reason, and a think
  block with content while thinking is off.
- The rubric is unchanged (it still asks for at most 120 characters), so RUBRIC_SHA and every `r1` key stay valid for
  the 108 rows.
- **A resume re-parses; it never re-asks.** `reparse` (804-815) turns a stored `malformed` record whose raw answer
  parses today into a `reparsed` record. The key, sent_sha, raw and ts stay the same. rel, use, reason and reason_cut
  come from the parse, `why` becomes null, and `reparsed_ts` is added. `cmd_label` (1010-1021) runs it over every
  record of the file, under the file lock, before any request, and APPENDS each reparsed record (then one fsync).
- The file stays append-only, as the brief's CONTRACT 2 demands: the round-1 line stays as it was. `read_labels`
  (733-757) lets a later `reparsed` record replace the `malformed` record of its key and counts it in a new
  `reparsed` stat; any other repeat is still a duplicate, and the first record is kept. A re-parsed key is a done key,
  so no request goes out for it. A second resume finds no malformed record to re-parse and appends nothing.
  `--limit 0` re-parses and sends nothing.
- **A stored raw of 300 characters or more is never re-parsed (a deliberate limit).** The raw is the answer cut to
  RAW_MAX (300). If the answer was that long, a second line after character 300 was never stored, so the head could
  parse while the whole answer would not. Such a record stays malformed and is counted `reparse_unchecked`. A new
  answer is parsed whole at label time, so the limit touches only records stored before round 2.
- The re-parse uses the run's own `--thinking` flag, as a new answer does. The PC commands run with thinking off.
- **The usage line** adds `reparsed=` and `reparse_unchecked=` (this run's), and `file_ok=`, `file_reparsed=` and
  `file_malformed=`: the file's records of this backend and rubric as the tool reads them, after this run
  (1067-1076).

**How validate and dataset treat a `reparsed` row: the same as `ok`.** Both use `LABELED = ("ok", "reparsed")` (162).
- validate (1239-1245): a reparsed label counts as `labeled` and joins its gold exactly as an ok label does. The
  counts add `labeled_reparsed`, only when there is one.
- dataset (1321-1328): a reparsed label gives the same two rows and label records as an ok label. The manifest's
  counts add `labels_reparsed`, only when there is one. The reason never reaches the dataset, as before.

**Tests (synthetic answers only, never the real ones).**
- `R150` (tests/test_s1_synth.py:42-43) is a synthetic 150-character reason in the real answers' shape. `ROUND1_RX`
  (44) is round 1's capped match, this file's own copy.
- `test_a_malformed_answer_is_stored_as_malformed_never_guessed` (618-647), 10 answers: `rel=1 use=0 <R150>` is now
  ok, with the first 120 characters as its reason and reason_cut true (round 1's test pinned a 121-character reason as
  malformed; that case is replaced). Added: the fields swapped, and a use out of range; both malformed.
- `test_a_resume_reparses_a_stored_answer_and_asks_nothing` (650-704, new). A labels file made the round-1 way (this
  code with ROUND1_RX put back by monkeypatch): 3 items x 4 sections, answered by section with R150, a short reason,
  two lines, and one line of 312 characters. Round 1 with `--limit 8`: 2 ok, 6 malformed.
  - The resume with `--limit 0` sends no request and appends 2 records (the R150 answers: reparsed, rel 1, use 0, the
    reason cut to 120, every other field unchanged).
  - The two-line and the 312-character answers stay malformed (`reparse_unchecked=2`). read_labels gives the stats
    `{"records": 8, "torn": 0, "duplicates": 0, "reparsed": 2}`, and the usage line `file_ok=2 file_reparsed=2
    file_malformed=4`.
  - The next run labels only the 4 pending pairs. There the 312-character answer, parsed whole, is ok with
    reason_cut true: `file_ok=5 file_reparsed=2 file_malformed=5`. A last run sends nothing and appends nothing.
- `test_the_validator_numbers_on_hand_made_gold` (lines 850-857 added) and
  `test_the_dataset_rows_join_with_laya_ft_and_the_loader_names_its_gap` (940-943 added): the same labels marked
  `reparsed` give the same numbers, rows and records as when they are `ok`.
- **Red-green (verified).** Today's test file against the landed code (73261cd's s1_synth.py, sha256
  374cc5ede5b3ec32..., in the harness's mirror): `4 failed, 19 passed in 19.65s`. The 4 are the tests above, each
  FAILED, with 0 errors. On the new code, all 23 pass.

### B. The CI failure (stage0-ci run #1102, run id 36224456809, origin 626fc4c)

**The finding (the coordinator's message).** The `tests` job: `1 failed, 5380 passed, 336 skipped, 8 xfailed`. The
one failure: `tests/test_s1_synth.py::test_the_dataset_fits_laya_window_in_the_laya_venue - PermissionError: [Errno
13] Permission denied: '/root/venv-laya-probe/bin/python'`, raised at the skip guard
`if not Path(LAYA_PY).exists() or not Path(C.DEFAULT_MODEL_DIR).exists():` (line 972 at 626fc4c).

**The premise, re-measured two ways (verified).**
- In process, with `os.stat` patched to raise EACCES for the venv's python: `Path.exists()` raised PermissionError
  (errno 13), and `os.path.exists()` returned False. pathlib swallows only ENOENT, ENOTDIR, EBADF and ELOOP; this
  sandbox runs as root, so the failure never showed here.
- For real, as a non-root user (`runuser -u nobody`, with /root at mode 700, the CI runner's condition): the landed
  test file (a mirror of HEAD's) failed with `E PermissionError: [Errno 13] Permission denied:
  '/root/venv-laya-probe/bin/python'` at pathlib.py:1013 (`1 failed, 20 deselected in 0.20s`): the CI failure,
  reproduced.

**The fix (tests/test_s1_synth.py).** `_present(path)` (1048-1052) returns `os.path.exists(path)`, which treats any
OSError as absent. The guard (1061) uses it for both paths, and the skip reason now says "absent or unreadable". The
test therefore skips loudly on a venue that cannot see the venv, as its docstring promises. As `nobody`, today's file
gives `SKIPPED [1] tests/test_s1_synth.py:1062: LOUD SKIP: the Laya venv (/root/venv-laya-probe/bin/python) or its
model is absent or unreadable on this venue` and `1 passed, 1 skipped, 21 deselected in 0.06s`.

**The test** `test_an_unreadable_laya_path_counts_as_absent_and_the_laya_test_skips` (1091-1107, new) patches
`os.stat` to raise EACCES for the venv's python. It asserts that `_present` answers absent for it and present for a
readable file, and that the Laya-venue test then raises pytest's Skipped with "LOUD SKIP" (never PermissionError).
Two test-file mutants: M46 present-bare-exists (the helper back to `Path(path).exists()`) and M47 guard-bare-exists
(the guard back to the landed `Path(...).exists()` form). Each is killed by this test as a FAILED test.

**The sweep of this lane's files for the same pattern:** no other site. scripts/s1_synth.py:737 uses `os.path.exists`
(it never raises), and tests/test_s1_synth.py:455 checks `out.exists()` on a path under pytest's tmp_path (always
readable).

### The run, the gates and the PC

**The mutation run (Appendix B), 07:20Z to 07:37Z, on the final bytes** (scripts/s1_synth.py sha256
8dfa6755876cb403..., tests/test_s1_synth.py b84ac40ceecfeabf...): the baseline passed 23 of 23; the control stayed
green twice; **47 of 47 mutants were KILLED, each by FAILED tests, with 0 errors.** The nine new mutants, with the
number of tests that killed each:

| mutant | killed by |
|---|---|
| M39 reason-cap-restored (the cap back inside the match: the coordinator's named mutant) | 2 |
| M40 reason-not-cut | 2 |
| M41 reparse-skipped | 1 |
| M42 cut-raw-trusted | 1 |
| M43 validator-reparsed-malformed | 1 |
| M44 dataset-reparsed-dropped | 1 |
| M45 reparsed-never-replaces | 1 |
| M46 present-bare-exists (the coordinator's named mutant for B) | 1 |
| M47 guard-bare-exists (the landed guard) | 1 |

**Gates (pasted).**
- `bash scripts/test_summary.sh tests/test_s1_synth.py` (set=7f2ad640fd36), twice, at 07:38:01Z and 07:38:21Z:
  `pytest-exit: 0` / `pytest-summary: 23 passed in 19.91s`, and `pytest-exit: 0` / `pytest-summary: 23 passed in
  19.24s`. Neither run printed a SKIPPED or an ERROR line (the Laya venue is present here).
- `python3 -m pyflakes scripts/s1_synth.py tests/test_s1_synth.py`: rc 0.
- `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: 0 for scripts/s1_synth.py, tests/test_s1_synth.py and this report (re-run
  after this report's last edit; the lane's final message pastes that result).
- Only tests/test_s1_synth.py imports scripts/s1_synth.py (a text search of scripts/ and tests/), and round 2 adds no
  import to the tool, so no other test file's result can change.

**On the PC, what changes (section 8 is updated).** Land and sync first (step 0). Then R2-1 re-parses the 108-row
file with `--limit 0` (no request), and R2-2 finishes the smoke's 120 with `--limit 12`. The stop rule is unchanged;
read it on `file_malformed`. Read every count from the usage line, never with grep: the file keeps each superseded
malformed line. Fix B changes nothing on the PC.

### Round 2, NOT done
- The re-parse did not run on the real 108-row file (the PC is the coordinator's). If all 74 raws are whole single
  lines under 300 characters (completion_tokens of 31 to 42 suggest about 150 to 200 characters), R2-1 prints
  `reparsed=74 reparse_unchecked=0 file_ok=34 file_reparsed=74 file_malformed=0`. A raw of 300 characters shows as
  `reparse_unchecked`, and its record stays malformed; it is NOT re-asked.
- The rubric still asks for at most 120 characters. A new rubric (r2) that allows a longer reason would change every
  key and re-ask the done pairs. Not done; not asked.
- max_tokens stays 64. A reason cut by the token limit (finish "length") still parses when rel and use come first.
  Such a reason stops short, but it is only a note.
- On CI the Laya-venue test now skips (loudly), as it was designed to; the Laya fit is proven only where the Laya venv
  is (this sandbox). The fix was not run on CI itself: the non-root run above is this lane's stand-in.

### Round 2, self-attack
1. *A re-parse that accepts what the whole answer would refuse.* Only a raw cut at 300 characters can hide the rest of
   an answer, and it is never re-parsed (M42 proves the test sees it). A raw under 300 characters is the whole answer
   (raw = answer[:300]).
2. *A reparsed record that the readers miss, or count twice.* read_labels puts the later reparsed record in place of
   the malformed one (M45). A second resume appends nothing (the test's last run). validate and dataset treat the
   record as ok (M43 and M44, and the same-numbers checks).
3. *A skip that hides a real failure.* The guard now treats an unreadable path as absent, so a venue where the venv is
   present but unreadable skips instead of running. That is the intended reading ("absent or unreadable"), and the
   skip is loud: its reason names the path. Where the venv is readable (this sandbox), the test runs in full.
Also weighed: the re-parse uses the resume's `--thinking` flag. With thinking off in both runs (the PC commands), a
stored think block with content stays malformed, as in round 1. Not guarded: a resume with `--thinking` over a file
labeled without it would drop such a block and re-parse the answer.

## Appendix A. The mutation harness (`<scratchpad>/synth1/mut/mutants.py`) and its final run

Run on the final scripts/s1_synth.py (sha256 374cc5ede5b3ec32..., 05:43:49Z) and tests/test_s1_synth.py (9f3bdde0847eb666...,
05:44:22Z), after the resume: `python3 mutants.py BASE M00 M01 ... M12`, then `M13 ... M25`, then `M26 ... M38 M00`
(three calls, 05:45:07Z to 05:58:14Z; the harness runs the named mutants in its own order, so the second M00 prints
before M26). Every line of the run, pasted from its output:

```
BASELINE unmutated: rc 0 failed 0 errors 0 | 21 passed in 18.52s
M00 CONTROL a comment            CONTROL-GREEN          by 0:  | 21 passed in 18.60s
M01 items-origin-dropped         KILLED                 by 3: a_dry_run_writes_nothing_opens_no_secret, items_are_human_prompts_and_tool_inputs_, the_validator_joins_the_real_readers_out | 3 failed, 18 passed in 19.28s
M02 items-assistant-blocks       KILLED                 by 3: a_dry_run_writes_nothing_opens_no_secret, items_are_human_prompts_and_tool_inputs_, the_candidates_are_the_hooks_own_ranking | 3 failed, 18 passed in 18.72s
M03 scrub-identity               KILLED                 by 2: scrubbing_happens_before_any_byte_leaves, the_cut_comes_after_the_scrub | 2 failed, 19 passed in 18.28s
M04 gate-skipped                 KILLED                 by 1: the_value_gate_refuses_before_any_write | 1 failed, 20 passed in 17.45s
M05 dry-run-writes               KILLED                 by 1: a_dry_run_writes_nothing_opens_no_secret | 1 failed, 20 passed in 18.77s
M06 floors-kept                  KILLED                 by 1: the_candidates_are_the_hooks_own_ranking | 1 failed, 20 passed in 18.47s
M07 ranking-reversed             KILLED                 by 1: the_candidates_are_the_hooks_own_ranking | 1 failed, 20 passed in 18.48s
M08 top-cut                      KILLED                 by 1: the_candidates_are_the_hooks_own_ranking | 1 failed, 20 passed in 18.64s
M09 rows-dropped                 KILLED                 by 2: the_candidates_are_the_hooks_own_ranking, the_validator_joins_the_real_readers_out | 2 failed, 19 passed in 18.63s
M10 section-without-pointer      KILLED                 by 1: the_candidates_are_the_hooks_own_ranking | 1 failed, 20 passed in 18.70s
M11 guard-off                    KILLED                 by 1: the_vllm_body_never_carries_a_forbidden_ | 1 failed, 20 passed in 18.58s
M12 body-adds-n                  KILLED                 by 7: a_malformed_answer_is_stored_as_malforme, a_rerun_skips_the_done_keys, concurrency_reaches_and_never_passes_its, scrubbing_happens_before_any_byte_leaves | 7 failed, 14 passed in 18.39s
M13 pool-plus-two                KILLED                 by 2: a_rerun_skips_the_done_keys, concurrency_reaches_and_never_passes_its | 2 failed, 19 passed in 19.59s
M14 pool-of-one                  KILLED                 by 1: concurrency_reaches_and_never_passes_its | 1 failed, 20 passed in 28.28s
M15 done-keys-ignored            KILLED                 by 2: a_malformed_answer_is_stored_as_malforme, a_rerun_skips_the_done_keys | 2 failed, 19 passed in 18.52s
M16 lenient-parse                KILLED                 by 1: a_malformed_answer_is_stored_as_malforme | 1 failed, 20 passed in 18.85s
M17 limiter-per-thread           KILLED                 by 1: the_openjev_backend_reuses_teacher_label | 1 failed, 20 passed in 16.64s
M18 safe-keeps-key               KILLED                 by 1: the_key_never_reaches_a_message | 1 failed, 20 passed in 18.61s
M19 lock-dropped                 KILLED                 by 1: a_second_run_on_the_same_labels_file_is_ | 1 failed, 20 passed in 18.80s
M20 exact-is-within-one          KILLED                 by 2: the_validator_numbers_on_hand_made_gold, the_validator_numbers_on_hand_made_s1_ra | 2 failed, 19 passed in 18.61s
M21 spearman-no-ties             KILLED                 by 2: the_validator_numbers_on_hand_made_gold, the_validator_numbers_on_hand_made_s1_ra | 2 failed, 19 passed in 18.65s
M22 map-a-is-b                   KILLED                 by 1: the_validator_numbers_on_hand_made_gold | 1 failed, 20 passed in 18.98s
M23 prompt-link-10s              KILLED                 by 1: the_validator_numbers_on_hand_made_gold | 1 failed, 20 passed in 19.03s
M24 s1all-worst-rank             KILLED                 by 1: the_validator_numbers_on_hand_made_gold | 1 failed, 20 passed in 18.80s
M25 target-off-by-one            KILLED                 by 1: the_dataset_rows_join_with_laya_ft_and_t | 1 failed, 20 passed in 18.55s
M00 CONTROL a comment            CONTROL-GREEN          by 0:  | 21 passed in 18.44s
M26 question-sha-swapped         KILLED                 by 1: the_dataset_rows_join_with_laya_ft_and_t | 1 failed, 20 passed in 18.65s
M27 openjev-malformed-guessed    KILLED                 by 1: the_openjev_backend_reuses_teacher_label | 1 failed, 20 passed in 19.17s
M28 thinking-on                  KILLED                 by 1: the_vllm_body_never_carries_a_forbidden_ | 1 failed, 20 passed in 18.75s
M29 cut-before-scrub             KILLED                 by 1: the_cut_comes_after_the_scrub | 1 failed, 20 passed in 18.59s
M30 cut-dropped                  KILLED                 by 1: the_cut_comes_after_the_scrub | 1 failed, 20 passed in 18.70s
M31 tools-not-in-turn            KILLED                 by 1: the_sample_takes_tools_in_turn_then_stra | 1 failed, 20 passed in 18.90s
M32 gold-dropped                 KILLED                 by 6: a_dry_run_writes_nothing_opens_no_secret, items_are_human_prompts_and_tool_inputs_, scrubbing_happens_before_any_byte_leaves, the_candidates_are_the_hooks_own_ranking | 6 failed, 15 passed in 18.18s
M33 stop-ignored                 KILLED                 by 1: a_rerun_skips_the_done_keys | 1 failed, 20 passed in 18.64s
M34 empty-think-kept             KILLED                 by 1: a_malformed_answer_is_stored_as_malforme | 1 failed, 20 passed in 18.55s
M35 any-think-dropped            KILLED                 by 1: a_malformed_answer_is_stored_as_malforme | 1 failed, 20 passed in 18.63s
M36 unfit-not-caught             KILLED                 by 1: the_dataset_fits_laya_window_in_the_laya | 1 failed, 20 passed in 18.62s
M37 non-ascii-json               KILLED                 by 1: the_files_are_ascii_json_and_a_line_sepa | 1 failed, 20 passed in 18.71s
M38 late-counted                 KILLED                 by 2: the_validator_numbers_on_hand_made_gold, the_validator_numbers_on_hand_made_s1_ra | 2 failed, 19 passed in 18.63s
```

Every verdict line reads "N failed, M passed" with no error: the harness prints "KILLED (+N errors)" or "INVALID" when
an ERROR is seen. Section 7 maps the tests. The pre-resume run (04:46Z to 04:59Z, the code before the scored-only change)
killed M01 to M37 with the same counts. The harness, verbatim (the file's bytes):

```python
"""SYNTH1 mutation run: each mutant of scripts/s1_synth.py runs tests/test_s1_synth.py in its own mirror of the tree.

A kill is a FAILED test (AF-AP-223): pytest's non-zero exit alone also covers setup and collection errors. The unmutated
baseline must pass whole first, and the CONTROL mutant (a comment) must stay green; an ERROR with no FAILED test is
reported INVALID, never a kill. Usage: python3 mutants.py [NAME-PREFIX ...]
"""
import os
import re
import shutil
import subprocess
import sys

REPO = "/home/user/agent-factory"
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(REPO, "scripts", "s1_synth.py"), encoding="utf-8").read()
TEST = "tests/test_s1_synth.py"

M = {
    "M00 CONTROL a comment": [("import argparse\n", "import argparse  # a control mutant: no behavior change\n")],
    "M01 items-origin-dropped": [('    if (r.get("origin") or {}).get("kind") != "human":\n        return None\n', "")],
    "M02 items-assistant-blocks": [(
        '    return [(b["name"], b["input"], b["id"]) for b in (content if isinstance(content, list) else [])\n'
        '            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in TOOLS\n'
        '            and isinstance(b.get("input"), dict) and isinstance(b.get("id"), str)]\n',
        '    blocks = content if isinstance(content, list) else []\n'
        '    return [(b["name"], b["input"], b["id"]) for b in blocks\n'
        '            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in TOOLS\n'
        '            and isinstance(b.get("input"), dict) and isinstance(b.get("id"), str)] + [\n'
        '        ("Bash", {"command": b.get("text") or b.get("thinking") or ""}, "x-%s-%d" % (r.get("uuid"), i))\n'
        '        for i, b in enumerate(blocks) if isinstance(b, dict) and b.get("type") in ("text", "thinking")]\n')],
    "M03 scrub-identity": [("def scrub(text):\n    return TE.scrub_payload(text)\n", "def scrub(text):\n    return text\n")],
    "M04 gate-skipped": [("    hits = TE.value_hits([data for _, data in files], TE.known_values(sources))\n    if hits:\n"
                          "        raise TE.KnownValueRefusal(hits)\n", "")],
    "M05 dry-run-writes": [("    if args.dry_run:\n        print(", "    if False:\n        print(")],
    "M06 floors-kept": [('        for name in FLOORS:\n            setattr(self.ungated, name, float("-inf"))\n', "")],
    "M07 ranking-reversed": [("        picks = list(enumerate(scored[:self.top], 1))\n",
                              "        picks = list(enumerate(scored[::-1][:self.top], 1))\n")],
    "M08 top-cut": [("        picks = list(enumerate(scored[:self.top], 1))\n",
                     "        picks = list(enumerate(scored[:self.top - 1], 1))\n")],
    "M09 rows-dropped": [('        cands += [r for r in rows if r["sha"] not in {c["sha"] for c in cands}]\n', "")],
    "M10 section-without-pointer": [
        ('        if sha16(text) != sha:\n            raise AssertionError("the hook\'s sha does not match its own text (%s)"'
         ' % sha)\n', ""),
        ('        self._section(e["sha"], out, skill=e["skill"]', '        self._section(e["sha"], out.rsplit("\\n", 1)[0], '
                                                               'skill=e["skill"]')],
    "M11 guard-off": [('    keys = set(body)\n    bad = sorted(keys - ALLOWED_BODY_KEYS)', '    return None\n    keys = set(body)\n'
                                                                                          '    bad = sorted(keys - ALLOWED_BODY_KEYS)')],
    "M12 body-adds-n": [('            "chat_template_kwargs": {"enable_thinking": bool(thinking)}}\n',
                         '            "chat_template_kwargs": {"enable_thinking": bool(thinking)}, "n": 1}\n')],
    "M13 pool-plus-two": [("ThreadPoolExecutor(max_workers=args.concurrency)",
                           "ThreadPoolExecutor(max_workers=args.concurrency + 2)")],
    "M14 pool-of-one": [("ThreadPoolExecutor(max_workers=args.concurrency)", "ThreadPoolExecutor(max_workers=1)")],
    "M15 done-keys-ignored": [('args.backend, args.rubric) not in done]', 'args.backend, args.rubric) not in set()]')],
    "M16 lenient-parse": [("    m = ANSWER_RX.fullmatch(content.strip())", "    m = ANSWER_RX.search(content.strip())")],
    "M17 limiter-per-thread": [("            c.limiter = shared\n", "            c.limiter = TL.Limiter(clock, sleep)\n")],
    "M18 safe-keeps-key": [('        return TE.scrub(str(text).replace(self._key, "<key>"))',
                            "        return TE.scrub(str(text))")],
    "M19 lock-dropped": [("            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)\n", "            pass\n")],
    "M20 exact-is-within-one": [("    exact = sum(1 for g, x in zip(gold, lab) if g == x)\n",
                                 "    exact = sum(1 for g, x in zip(gold, lab) if abs(g - x) <= 1)\n")],
    "M21 spearman-no-ties": [("            out[order[k]] = (i + j) / 2 + 1\n", "            out[order[k]] = k + 1\n")],
    "M22 map-a-is-b": [("MAP_A = {0: 0, 1: 0, 2: 1, 3: 2}", "MAP_A = {0: 0, 1: 1, 2: 1, 3: 2}")],
    "M23 prompt-link-10s": [("PROMPT_LINK_S = 2.0", "PROMPT_LINK_S = 10.0")],
    "M24 s1all-worst-rank": [('                       key=lambda c: c["rank"])\n',
                              '                       key=lambda c: -c["rank"])\n')],
    "M25 target-off-by-one": [("[1.0 if i == value else 0.0 for i in range(4)]",
                               "[1.0 if i == (value + 1) % 4 else 0.0 for i in range(4)]")],
    "M26 question-sha-swapped": [('"question_id": qid, "question_sha": C.question_sha(q),',
                                  '"question_id": qid, "question_sha": C.question_sha(Q_REL),')],
    "M27 openjev-malformed-guessed": [('            return dict(rec, status="malformed", rel=None, use=None, why=c.safe(e), '
                                       'raw=None)', '            return dict(rec, status="ok", rel=0, use=0, why=c.safe(e), '
                                                    'raw=None)')],
    "M28 thinking-on": [('"chat_template_kwargs": {"enable_thinking": bool(thinking)}}',
                         '"chat_template_kwargs": {"enable_thinking": True}}')],
    "M29 cut-before-scrub": [("                    clean = scrub_value(text, counts)\n",
                              "                    clean = scrub_value(text[:4000], counts)\n")],
    "M30 cut-dropped": [("    text = clean[:cap]\n", "    text = clean\n")],
    "M31 tools-not-in-turn": [("interleave([interleave(per_tool[t]) for t in TOOLS])",
                               "interleave([g for t in TOOLS for g in per_tool[t]])")],
    "M32 gold-dropped": [('    picked = [c for c in calls if c["gold"]]\n', "    picked = []\n")],
    "M33 stop-ignored": [("            if stop is not None and stop.is_set():\n                raise Stopped()\n", ""),
                         ("            if stop.is_set():\n                raise Stopped()\n", "")],
    "M34 empty-think-kept": [('    content = (THINK_RX if thinking else EMPTY_THINK_RX).sub("", content, count=1)\n',
                              '    content = THINK_RX.sub("", content, count=1) if thinking else content\n')],
    "M35 any-think-dropped": [('    content = (THINK_RX if thinking else EMPTY_THINK_RX).sub("", content, count=1)\n',
                               '    content = THINK_RX.sub("", content, count=1)\n')],
    "M36 unfit-not-caught": [("            try:\n                st, cut = fitter.fit(state, q) if fitter is not None else (state, None)\n"
                              "            except FIT.Unfit:                          # the section alone overflows Laya's window: no row\n"
                              '                counts["unfit." + qid] += 1\n                continue\n',
                              "            st, cut = fitter.fit(state, q) if fitter is not None else (state, None)\n")],
    "M37 non-ascii-json": [("    return json.dumps(obj, ensure_ascii=True, sort_keys=True) + \"\\n\"\n",
                            "    return json.dumps(obj, ensure_ascii=False, sort_keys=True) + \"\\n\"\n")],

    "M38 late-counted": [('        if r["status"] != "scored":\n            continue\n        if r["event"] == "UserPromptSubmit":\n',
                          '        if r["status"] not in ("scored", "late"):\n            continue\n        if r["event"] == "UserPromptSubmit":\n')],
}


def mirror(dst, src_text):
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(os.path.join(dst, "scripts"))
    os.makedirs(os.path.join(dst, "tests"))
    for name in os.listdir(REPO):
        if name not in ("scripts", "tests", ".git"):
            os.symlink(os.path.join(REPO, name), os.path.join(dst, name))
    for name in os.listdir(os.path.join(REPO, "scripts")):
        if name not in ("s1_synth.py", "__pycache__"):
            os.symlink(os.path.join(REPO, "scripts", name), os.path.join(dst, "scripts", name))
    open(os.path.join(dst, "scripts", "s1_synth.py"), "w", encoding="utf-8").write(src_text)
    for name in ("test_s1_synth.py", "conftest.py"):
        shutil.copy(os.path.join(REPO, "tests", name), os.path.join(dst, "tests", name))


def run(dst, bt):
    shutil.rmtree(bt, ignore_errors=True)
    os.makedirs(os.path.dirname(bt), exist_ok=True)
    r = subprocess.run([sys.executable, "-m", "pytest", TEST, "-q", "-p", "no:cacheprovider", "--basetemp", bt],
                       cwd=dst, capture_output=True, text=True, timeout=600)
    shutil.rmtree(bt, ignore_errors=True)
    failed = sorted(set(re.findall(r"^FAILED tests/test_s1_synth\.py::(\S+)", r.stdout, re.M)))
    errors = sorted(set(re.findall(r"^ERROR tests/test_s1_synth\.py::(\S+)", r.stdout, re.M)))
    last = [line for line in r.stdout.splitlines() if line.strip()][-1] if r.stdout.strip() else "(no output)"
    return r.returncode, failed, errors, last


def main(only):
    dst, bt = os.path.join(HERE, "mirror"), os.path.join(HERE, "bt", "m")
    if not only or any("BASE".startswith(o) for o in only):
        mirror(dst, SRC)
        rc, failed, errors, last = run(dst, bt)
        print("BASELINE unmutated: rc %d failed %d errors %d | %s" % (rc, len(failed), len(errors), last), flush=True)
        if rc != 0:
            sys.exit("the unmutated baseline is not green: no mutant verdict means anything")
    for name, edits in M.items():
        if only and not any(name.startswith(o) for o in only):
            continue
        text = SRC
        for a, b in edits:
            assert SRC.count(a) == 1, (name, SRC.count(a), a[:60])
            text = text.replace(a, b)
        mirror(dst, text)
        rc, failed, errors, last = run(dst, bt)
        if name.startswith("M00"):
            verdict = "CONTROL-GREEN" if rc == 0 and not failed and not errors else "CONTROL-RED (invalid harness)"
        elif failed and not errors:
            verdict = "KILLED"
        elif failed:
            verdict = "KILLED (+%d errors)" % len(errors)
        elif errors:
            verdict = "INVALID (errors only)"
        else:
            verdict = "SURVIVED"
        print("%-32s %-22s by %d: %s | %s" % (name, verdict, len(failed), ", ".join(f[5:45] for f in failed[:4]),
                                              last[:70]), flush=True)
    shutil.rmtree(dst, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1:])
```

## Appendix B. The round-2 mutation run (`<scratchpad>/synth1r2/mut/mutants.py`) and the red-green check

The harness is Appendix A's with the changes below: the nine new mutants, and a second table, T, whose
mutants edit the TEST file's own helper and guard (the CI fix) in the mirror's copy of it. Applied with `patch`
to Appendix A's text, the diff rebuilds the round-2 file byte for byte (checked in process before the scratch
was deleted). Run on scripts/s1_synth.py sha256 8dfa6755876cb403... and tests/test_s1_synth.py
b84ac40ceecfeabf...: `python3 mutants.py BASE M00 M01 ... M12`, then `M13 ... M25`, then `M26 ... M38`, then
`M39 ... M47 M00` (four calls, 07:20:36Z to 07:37:30Z; the harness runs the named mutants in its own order, so the
second M00 prints first in the last call). Every line of the run, pasted from its output:

```
BASELINE unmutated: rc 0 failed 0 errors 0 | 23 passed in 19.82s
M00 CONTROL a comment            CONTROL-GREEN          by 0:  | 23 passed in 19.73s
M01 items-origin-dropped         KILLED                 by 3: a_dry_run_writes_nothing_opens_no_secret, items_are_human_prompts_and_tool_inputs_, the_validator_joins_the_real_readers_out | 3 failed, 20 passed in 19.81s
M02 items-assistant-blocks       KILLED                 by 3: a_dry_run_writes_nothing_opens_no_secret, items_are_human_prompts_and_tool_inputs_, the_candidates_are_the_hooks_own_ranking | 3 failed, 20 passed in 19.40s
M03 scrub-identity               KILLED                 by 2: scrubbing_happens_before_any_byte_leaves, the_cut_comes_after_the_scrub | 2 failed, 21 passed in 19.15s
M04 gate-skipped                 KILLED                 by 1: the_value_gate_refuses_before_any_write | 1 failed, 22 passed in 18.36s
M05 dry-run-writes               KILLED                 by 1: a_dry_run_writes_nothing_opens_no_secret | 1 failed, 22 passed in 19.88s
M06 floors-kept                  KILLED                 by 1: the_candidates_are_the_hooks_own_ranking | 1 failed, 22 passed in 19.41s
M07 ranking-reversed             KILLED                 by 1: the_candidates_are_the_hooks_own_ranking | 1 failed, 22 passed in 19.36s
M08 top-cut                      KILLED                 by 1: the_candidates_are_the_hooks_own_ranking | 1 failed, 22 passed in 19.56s
M09 rows-dropped                 KILLED                 by 2: the_candidates_are_the_hooks_own_ranking, the_validator_joins_the_real_readers_out | 2 failed, 21 passed in 19.25s
M10 section-without-pointer      KILLED                 by 1: the_candidates_are_the_hooks_own_ranking | 1 failed, 22 passed in 19.42s
M11 guard-off                    KILLED                 by 1: the_vllm_body_never_carries_a_forbidden_ | 1 failed, 22 passed in 19.75s
M12 body-adds-n                  KILLED                 by 8: a_malformed_answer_is_stored_as_malforme, a_rerun_skips_the_done_keys, a_resume_reparses_a_stored_answer_and_as, concurrency_reaches_and_never_passes_its | 8 failed, 15 passed in 19.28s
M13 pool-plus-two                KILLED                 by 2: a_rerun_skips_the_done_keys, concurrency_reaches_and_never_passes_its | 2 failed, 21 passed in 20.26s
M14 pool-of-one                  KILLED                 by 1: concurrency_reaches_and_never_passes_its | 1 failed, 22 passed in 28.84s
M15 done-keys-ignored            KILLED                 by 3: a_malformed_answer_is_stored_as_malforme, a_rerun_skips_the_done_keys, a_resume_reparses_a_stored_answer_and_as | 3 failed, 20 passed in 19.61s
M16 lenient-parse                KILLED                 by 2: a_malformed_answer_is_stored_as_malforme, a_resume_reparses_a_stored_answer_and_as | 2 failed, 21 passed in 19.64s
M17 limiter-per-thread           KILLED                 by 1: the_openjev_backend_reuses_teacher_label | 1 failed, 22 passed in 17.72s
M18 safe-keeps-key               KILLED                 by 1: the_key_never_reaches_a_message | 1 failed, 22 passed in 19.69s
M19 lock-dropped                 KILLED                 by 1: a_second_run_on_the_same_labels_file_is_ | 1 failed, 22 passed in 19.63s
M20 exact-is-within-one          KILLED                 by 2: the_validator_numbers_on_hand_made_gold, the_validator_numbers_on_hand_made_s1_ra | 2 failed, 21 passed in 19.69s
M21 spearman-no-ties             KILLED                 by 2: the_validator_numbers_on_hand_made_gold, the_validator_numbers_on_hand_made_s1_ra | 2 failed, 21 passed in 19.99s
M22 map-a-is-b                   KILLED                 by 1: the_validator_numbers_on_hand_made_gold | 1 failed, 22 passed in 19.90s
M23 prompt-link-10s              KILLED                 by 1: the_validator_numbers_on_hand_made_gold | 1 failed, 22 passed in 19.75s
M24 s1all-worst-rank             KILLED                 by 1: the_validator_numbers_on_hand_made_gold | 1 failed, 22 passed in 19.52s
M25 target-off-by-one            KILLED                 by 1: the_dataset_rows_join_with_laya_ft_and_t | 1 failed, 22 passed in 19.59s
M26 question-sha-swapped         KILLED                 by 1: the_dataset_rows_join_with_laya_ft_and_t | 1 failed, 22 passed in 19.63s
M27 openjev-malformed-guessed    KILLED                 by 1: the_openjev_backend_reuses_teacher_label | 1 failed, 22 passed in 19.66s
M28 thinking-on                  KILLED                 by 1: the_vllm_body_never_carries_a_forbidden_ | 1 failed, 22 passed in 19.46s
M29 cut-before-scrub             KILLED                 by 1: the_cut_comes_after_the_scrub | 1 failed, 22 passed in 19.48s
M30 cut-dropped                  KILLED                 by 1: the_cut_comes_after_the_scrub | 1 failed, 22 passed in 19.83s
M31 tools-not-in-turn            KILLED                 by 1: the_sample_takes_tools_in_turn_then_stra | 1 failed, 22 passed in 19.74s
M32 gold-dropped                 KILLED                 by 6: a_dry_run_writes_nothing_opens_no_secret, items_are_human_prompts_and_tool_inputs_, scrubbing_happens_before_any_byte_leaves, the_candidates_are_the_hooks_own_ranking | 6 failed, 17 passed in 19.11s
M33 stop-ignored                 KILLED                 by 1: a_rerun_skips_the_done_keys | 1 failed, 22 passed in 19.57s
M34 empty-think-kept             KILLED                 by 1: a_malformed_answer_is_stored_as_malforme | 1 failed, 22 passed in 19.50s
M35 any-think-dropped            KILLED                 by 1: a_malformed_answer_is_stored_as_malforme | 1 failed, 22 passed in 19.68s
M36 unfit-not-caught             KILLED                 by 1: the_dataset_fits_laya_window_in_the_laya | 1 failed, 22 passed in 19.86s
M37 non-ascii-json               KILLED                 by 1: the_files_are_ascii_json_and_a_line_sepa | 1 failed, 22 passed in 19.57s
M38 late-counted                 KILLED                 by 2: the_validator_numbers_on_hand_made_gold, the_validator_numbers_on_hand_made_s1_ra | 2 failed, 21 passed in 19.39s
M00 CONTROL a comment            CONTROL-GREEN          by 0:  | 23 passed in 19.31s
M39 reason-cap-restored          KILLED                 by 2: a_malformed_answer_is_stored_as_malforme, a_resume_reparses_a_stored_answer_and_as | 2 failed, 21 passed in 19.43s
M40 reason-not-cut               KILLED                 by 2: a_malformed_answer_is_stored_as_malforme, a_resume_reparses_a_stored_answer_and_as | 2 failed, 21 passed in 19.45s
M41 reparse-skipped              KILLED                 by 1: a_resume_reparses_a_stored_answer_and_as | 1 failed, 22 passed in 19.34s
M42 cut-raw-trusted              KILLED                 by 1: a_resume_reparses_a_stored_answer_and_as | 1 failed, 22 passed in 19.67s
M43 validator-reparsed-malformed KILLED                 by 1: the_validator_numbers_on_hand_made_gold | 1 failed, 22 passed in 19.83s
M44 dataset-reparsed-dropped     KILLED                 by 1: the_dataset_rows_join_with_laya_ft_and_t | 1 failed, 22 passed in 19.82s
M45 reparsed-never-replaces      KILLED                 by 1: a_resume_reparses_a_stored_answer_and_as | 1 failed, 22 passed in 19.80s
M46 present-bare-exists          KILLED                 by 1: an_unreadable_laya_path_counts_as_absent | 1 failed, 22 passed in 19.79s
M47 guard-bare-exists            KILLED                 by 1: an_unreadable_laya_path_counts_as_absent | 1 failed, 22 passed in 19.80s
```

The harness changes, a unified diff against Appendix A's text:

```diff
--- appendix-a/mutants.py
+++ round-2/mutants.py
@@ -16,2 +16,3 @@
 TEST = "tests/test_s1_synth.py"
+TEST_SRC = open(os.path.join(REPO, TEST), encoding="utf-8").read()
 
@@ -95,2 +96,18 @@
                           '        if r["status"] not in ("scored", "late"):\n            continue\n        if r["event"] == "UserPromptSubmit":\n')],
+    "M39 reason-cap-restored": [('ANSWER_RX = re.compile(r"rel=([0-3]) use=([0-3]) (\\S.*)")',
+                                 'ANSWER_RX = re.compile(r"rel=([0-3]) use=([0-3]) (\\S.{0,%d})" % (REASON_MAX - 1))')],
+    "M40 reason-not-cut": [("reason[:REASON_MAX], len(reason) > REASON_MAX", "reason, len(reason) > REASON_MAX")],
+    "M41 reparse-skipped": [("            new = reparse(done[key], args.thinking)\n", "            new = None\n")],
+    "M42 cut-raw-trusted": [(" or not isinstance(raw, str) or len(raw) >= RAW_MAX:", " or not isinstance(raw, str):")],
+    "M43 validator-reparsed-malformed": [('            elif rec.get("status") not in LABELED:\n',
+                                          '            elif rec.get("status") != "ok":\n')],
+    "M44 dataset-reparsed-dropped": [('lab.get("rubric") != rubric or lab.get("status") not in LABELED:',
+                                      'lab.get("rubric") != rubric or lab.get("status") != "ok":')],
+    "M45 reparsed-never-replaces": [('            if rec.get("status") == "reparsed" and recs[key].get("status") == "malformed":\n',
+                                     "            if False:\n")],
+}
+T = {   # round 2: mutants of the TEST file's own helper and guard (the CI fix), applied to the mirror's copy of it
+    "M46 present-bare-exists": [("    return os.path.exists(path)\n", "    return Path(path).exists()\n")],
+    "M47 guard-bare-exists": [("    if not _present(LAYA_PY) or not _present(C.DEFAULT_MODEL_DIR):\n",
+                               "    if not Path(LAYA_PY).exists() or not Path(C.DEFAULT_MODEL_DIR).exists():\n")],
 }
@@ -98,3 +115,3 @@
 
-def mirror(dst, src_text):
+def mirror(dst, src_text, test_text=None):
     shutil.rmtree(dst, ignore_errors=True)
@@ -111,2 +128,4 @@
         shutil.copy(os.path.join(REPO, "tests", name), os.path.join(dst, "tests", name))
+    if test_text is not None:
+        open(os.path.join(dst, "tests", "test_s1_synth.py"), "w", encoding="utf-8").write(test_text)
 
@@ -133,10 +152,13 @@
             sys.exit("the unmutated baseline is not green: no mutant verdict means anything")
-    for name, edits in M.items():
+    for name, edits, base in [(n, e, SRC) for n, e in M.items()] + [(n, e, TEST_SRC) for n, e in T.items()]:
         if only and not any(name.startswith(o) for o in only):
             continue
-        text = SRC
+        text = base
         for a, b in edits:
-            assert SRC.count(a) == 1, (name, SRC.count(a), a[:60])
+            assert base.count(a) == 1, (name, base.count(a), a[:60])
             text = text.replace(a, b)
-        mirror(dst, text)
+        if base is SRC:
+            mirror(dst, text)
+        else:
+            mirror(dst, SRC, text)
         rc, failed, errors, last = run(dst, bt)
```

The red-green check (`redgreen.py` beside the harness: today's tests in the harness's own mirror, with the landed
scripts/s1_synth.py from `git show HEAD:scripts/s1_synth.py`, sha256 374cc5ede5b3ec32..., the bytes of 73261cd),
run at 07:37:41Z on the final test bytes, pasted:

```
LANDED HEAD code, today's tests: rc 1 failed 4 errors 0 | 4 failed, 19 passed in 19.65s
  FAILED test_a_malformed_answer_is_stored_as_malformed_never_guessed
  FAILED test_a_resume_reparses_a_stored_answer_and_asks_nothing
  FAILED test_the_dataset_rows_join_with_laya_ft_and_the_loader_names_its_gap
  FAILED test_the_validator_numbers_on_hand_made_gold
```

`redgreen.py`, verbatim:

```python
"""SYNTH1 round 2, red-green: today's tests/test_s1_synth.py against the LANDED scripts/s1_synth.py (git HEAD), in the
mutation harness's own mirror. The round-2 tests must fail there, each as a FAILED test (not an error)."""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mutants as MU  # noqa: E402

head = subprocess.run(["git", "--no-optional-locks", "show", "HEAD:scripts/s1_synth.py"], cwd=MU.REPO,
                      capture_output=True, text=True, check=True).stdout
dst, bt = os.path.join(MU.HERE, "mirror"), os.path.join(MU.HERE, "bt", "rg")
MU.mirror(dst, head)
rc, failed, errors, last = MU.run(dst, bt)
shutil.rmtree(dst, ignore_errors=True)
print("LANDED HEAD code, today's tests: rc %d failed %d errors %d | %s" % (rc, len(failed), len(errors), last))
for f in failed:
    print("  FAILED", f)
for e in errors:
    print("  ERROR", e)
```
