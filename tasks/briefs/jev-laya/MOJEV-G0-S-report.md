# MOJEV-G0-S report (task #230; D-072 item 3): the MoJev Gate 0 probe, built in the sandbox

Lane: MOJEV-G0-S, sandbox code-implementer (Opus 5.5). PIN named by the dispatch: local HEAD db71586. At lane start the
local HEAD was cda44b8 (one coordinator commit on top: `todo/BUILD-TASKLIST.md` and `wiki/topics/live-state.md` only, no
file this lane reads). Branch claude/soundbox-kit-migration-iz1jwf, shared tree, no worktree. Status: DONE in the sandbox (code, tests, gates); NOT run on the PC. The run and the findings are the coordinator's (section 7).

## 1. Premise re-measured (2026-09-24 13:11Z, sandbox)

### 1a. Sandbox brief (`tasks/briefs/jev-laya/MOJEV-G0-SANDBOX-brief.md`) PREMISE block

```
$ grep -n -E "^## " tasks/briefs/pc/pc-mojev-g0.md
20:## WHY (read first)
32:## BOUNDARY
43:## PINNED DECISIONS
60:## CONTRACT (each item is a JSON block and a report section)
82:## TESTS (`tests/test_mojev_probe.py`; no model load, run with `/home/rocco/venv-agent-factory/bin/python`)
92:## GATES
98:## REPORT (`tasks/briefs/jev-laya/MOJEV-G0-report.md`)
105:## PREMISE — MEASURED at authoring (2026-09-24 11:4xZ; the sandbox tree at 200ed95 over origin 8c684be, and the PC over the bridge)
$ git ls-files scripts/mojev_probe.py tests/test_mojev_probe.py | wc -l
0
$ df -h / | tail -1
/dev/vda        252G   35G  2.9G  93% /
```

Match, except free disk: 2.9G now against 957M at authoring. Not design-changing (the lane downloads nothing either way).

### 1b. PC brief (`tasks/briefs/pc/pc-mojev-g0.md`) PREMISE block, the sandbox-side lines

```
# sandbox: the Hub API for the pinned revision (read-only GET of metadata JSON, no file downloaded)
sha 0c8695b6252f4205907433d4e196a94f032e60c3 lastModified 2026-09-23T20:23:19.000Z
config.json size=5935 blob=946557eb49d7 lfs_sha256=-
model.safetensors size=1710234304 blob=8507a0ef6d04 lfs_sha256=eae27bf03e0e44501316cafab2406b1505732ddf4b836d19fbb8deb642f55f50
modeling.py size=13390 blob=8b1415ffb650 lfs_sha256=-
tokenizer.json size=19989325 blob=5520bfd2dd83 lfs_sha256=06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523
$ git ls-remote https://github.com/MoLeMo-Lab/mojev
a74d58cd19ec573e83e8e27f9fecd837b8d830fb	HEAD
a74d58cd19ec573e83e8e27f9fecd837b8d830fb	refs/heads/master
$ git show 8c684be:docs/INCIDENT-LOG.md | wc -c
548542
$ git ls-files tests/test_laya_probe_report.py docs/research/findings/jev-audit/mojev-evidence.md docs/research/findings/MOJEV-AUDIT-2026-09-24.md
docs/research/findings/MOJEV-AUDIT-2026-09-24.md
docs/research/findings/jev-audit/mojev-evidence.md
tests/test_laya_probe_report.py
$ git ls-files scripts/mojev_probe.py tests/test_mojev_probe.py docs/research/findings/MOJEV-PROBE-0.md | wc -l
0
```

All match. 8c684be is an ancestor of HEAD (`git merge-base --is-ancestor 8c684be HEAD` rc 0; full sha
8c684be8c6dc525f8eaaeab474038be7fce2987d).

### 1c. PC-side lines: NOT re-measurable here

`tail -4 ~/mojev-prep.log`, `git -C ~/mojev-pin rev-parse HEAD`, the snapshot's `auto_map` / `processor_class` /
`tokenizer_class` lines, the three `~/mojev-pin` grep hits (`mojev/evaluate.py:40`, `mojev/serve.py:142`,
`mojev/full.py:83`), nproc / avx2 / memory / disk, and the `~/venv-laya` versions and missing PIL / torchvision. They live
on the PC; this lane never touches the PC or the bridge. They are the coordinator's to re-measure before the run.

Verdict on the premise: no mismatch changes the design. Lane continues.

## 2. Seams read (static text only; nothing imported or run)

The sandbox still holds the audit's static clone `/home/user/molemo-lab/mojev` (`git rev-parse HEAD` =
a74d58cd19ec573e83e8e27f9fecd837b8d830fb, `git status --short` empty), the same commit the PC brief pins for `~/mojev-pin`.
Read as text, with line numbers:

| Seam | Where | What the probe does with it |
|---|---|---|
| `load_packed(checkpoint, device)` = `PackedScorer.from_pretrained(checkpoint).to(device).eval()` | `mojev/evaluate.py:40-54` | called unmodified (D-1) |
| `Engine.__init__` loads the processor with `trust_remote_code=True` | `mojev/serve.py:151-180` (the flag at :171) | NOT called: D-1 forbids remote code. The probe builds the Engine with `Engine.__new__` and sets the same eight attributes, the processor loaded with `trust_remote_code=False` |
| `Engine.answer(state, questions)`: sort, pack, one forward, softmax, unsort | `mojev/serve.py:182-231` | called unmodified for every scored request; `engine.model` is wrapped by a recorder that keeps the batch and times the forward |
| the candidate sort | `mojev/full.py:70-83` (`sort_candidates`), applied at `mojev/serve.py:193`, packed sorted at :196, unsorted at :225 | G0-4 cites these lines and re-reads them on the PC pin at run time |
| state truncation | `mojev/full.py:167-168` `tokenizer([...], truncation=True, max_length=context_tokens)`; budget `config.context_tokens` = 16384 (`hf/model-config.json:9`) | G0-3 |
| field prompt cut at 32 tokens; options listed only for choice menus of 8 or fewer | `mojev/full.py:150-151`; `mojev/schema.py:57-73` | recorded per request (`field_prompt_tokens`) |
| mixed dtypes are load-bearing | `mojev/modeling.py:20-27,38-39,114-120` | D-2 variants checked by a per-dtype parameter count after load; a variant that did not take is a refusal |
| the Space and the browser export set `eager` attention; the Engine does not | `space/app.py:17`; `browser/export.py:111` | the probe follows the Engine (sdpa default) and records `attn_implementation` |
| AutoProcessor with `trust_remote_code=False` | transformers 5.17.0 `models/auto/processing_auto.py:227-243,333-335` (text read of `/root/venv-laya-probe`) | `processor_class` is read from `preprocessor_config.json` first, so `config.json`'s `auto_map` is never consulted: D-1 holds as coded. What it needs is the processor's own dependencies (PIL, torchvision) in `~/venv-mojev` |
| MoJev's float32 4-D mask under a bf16 encoder | transformers 5.17.0 `masking_utils.py:782` ("an already prepared 4D mask ... returned as-is") | the Engine path upstream ran; NOT run here |

## 3. What was built (status: code and tests done; nothing run on the PC)

- `scripts/mojev_probe.py` (new). Parent: plan, G0-1, one child per task (D-4), phase limit and RSS cap by pid, partial log,
  assembly, validation, JSON writer, MD cell table. Child (`--child`): load through MoJev's own code (D-1), exact token cuts
  (D-3), every request through the real `Engine.answer`. `--dry-run` and `--only` as asked (`--only` is an addition, flagged
  in section 8).
- `tests/test_mojev_probe.py` (new). Doubles: `FakeEngine` (Engine.answer's contract as read at `mojev/serve.py:182-231`),
  `FakeTokenizer` and two boundary variants, scripted child processes. The brief's numbers are restated in the test file,
  so the plan is checked against the brief, not against the probe's own constants.

### 3a. Mutation audit (scratchpad copy only; the shared tree was never mutated)

30 mutants of the probe, each run against the test file in a copy (the 4 subprocess tests that need `git show` in the repo
were deselected there, since the copy is not a checkout). First pass: 23 killed, 1 survived, 1 anchor miss. Survivor M22
(p50 computed as the mean) lived because the fake clock gave timed runs of 30, 10 and 20 ms, whose mean equals their median.
Fixed in the test double (runs 30, 10, 70 ms), and the per-candidate change of G0-4 pinned to the brief's definition.
Second pass, verbatim from the runner (`scratchpad/mutate.py`; per-test timings stripped; probe sha256 4ab75259...,
tests dc6dc708..., the files in section 14):

```
M01 hash check off: rc=1 KILLED | 1 failed, 5 passed, 4 deselected | first red: ['test_weights_refuse_a_wrong_hash']
M02 size check off: rc=1 KILLED | 1 failed, 4 passed, 4 deselected | first red: ['test_weights_refuse_a_wrong_size']
M03 missing cell not named: rc=1 KILLED | 1 failed, 42 passed, 4 deselected | first red: ['test_writer_refuses_a_missing_cell_by_name[2048x5/released_bf16]']
M04 missing block not named: rc=1 KILLED | 1 failed, 66 passed, 4 deselected | first red: ['test_writer_refuses_a_missing_block_by_name[g0_3_truncation]']
M05 ERROR cell accepted: rc=1 KILLED | 1 failed, 70 passed, 4 deselected | first red: ['test_writer_refuses_an_unmeasured_cell_and_unverified_weights']
M06 kept end swapped: rc=1 KILLED | 1 failed, 22 passed, 4 deselected | first red: ['test_truncation_task_names_the_kept_end[right-first]']
M07 argmax changes zero: rc=1 KILLED | 1 failed, 26 passed, 4 deselected | first red: ['test_order_task_detects_a_slot_dependent_scorer']
M08 change vs wrong reference: rc=1 KILLED | 1 failed, 26 passed, 4 deselected | first red: ['test_order_task_detects_a_slot_dependent_scorer']
M26 orderings floor off: rc=1 KILLED | 1 failed, 71 passed, 4 deselected | first red: ['test_writer_names_an_incomplete_part[<lambda>-incomplete-block:g0_4_order/released_bf16]']
M27 validator p50 check off: rc=1 KILLED | 1 failed, 75 passed, 4 deselected | first red: ['test_writer_names_an_incomplete_part[<lambda>-bad-p50-or-max:8192x10/fp32]']
M28 validator run count off: rc=1 KILLED | 1 failed, 74 passed, 4 deselected | first red: ['test_writer_names_an_incomplete_part[<lambda>-bad-runs:8192x10/fp32]']
M29 slots from wrong index: rc=1 KILLED | 1 failed, 26 passed, 4 deselected | first red: ['test_order_task_detects_a_slot_dependent_scorer']
M30 projection check off: rc=1 KILLED | 1 failed, 78 passed, 4 deselected | first red: ['test_writer_names_an_incomplete_part[<lambda>-missing-projection:8192x10/fp32]']
M09 timeout off: rc=1 KILLED | 1 failed, 33 passed, 4 deselected | first red: ['test_run_child_stops_a_run_past_the_limit']
M10 rss cap off: rc=1 KILLED | 1 failed, 35 passed, 4 deselected | first red: ['test_run_child_stops_a_child_over_the_rss_cap']
M11 cut not re-counted: rc=1 KILLED | 1 failed, 13 passed, 4 deselected | first red: ['test_cut_head_scans_past_a_boundary_miscount']
M12 probabilities in sorted order: rc=1 KILLED | 1 failed, 17 passed, 4 deselected | first red: ['test_score_request_maps_probabilities_back_to_the_callers_order']
M13 state-token check off: rc=1 KILLED | 1 failed, 28 passed, 4 deselected | first red: ['test_task_refuses_a_state_the_batch_did_not_keep']
M14 fresh compared to itself: rc=1 KILLED | 1 failed, 41 passed, 4 deselected | first red: ['test_determinism_block_reports_a_fresh_process_difference']
M15 projection x10: rc=1 KILLED | 1 failed, 39 passed, 4 deselected | first red: ['test_complete_result_writes_and_projects']
M16 fp32 dtype check off: rc=1 KILLED | 1 failed, 20 passed, 4 deselected | first red: ['test_dtype_variant_must_take']
M17 dirty pin accepted: rc=1 KILLED | 1 failed, 9 passed, 4 deselected | first red: ['test_code_pin_refuses_a_tracked_change_and_a_non_checkout']
M18 splitlines numbering: rc=1 KILLED | 1 failed, 11 passed, 4 deselected | first red: ['test_citations_count_lines_on_newline_only']
M19 no g0_4 dtype pairs: rc=1 KILLED | 1 failed, 40 passed, 4 deselected | first red: ['test_result_compares_dtypes_on_every_request_scored_in_both']
M20 refusal does not stop: rc=1 KILLED | 1 failed, 31 passed, 4 deselected | first red: ['test_run_tasks_logs_every_record_and_stops_at_the_first_refusal']
M21 capture drops warnings: rc=1 KILLED | 1 failed, 25 passed, 4 deselected | first red: ['test_truncation_task_keeps_what_a_caller_could_see']
M22 p50 is the mean: rc=1 KILLED | 1 failed, 21 passed, 4 deselected | first red: ['test_cell_task_measures_the_planned_state']
M23 image marker allowed: rc=1 KILLED | 1 failed, 30 passed, 4 deselected | first red: ['test_task_refuses_an_image_marker_in_the_state']
M24 budget check off: rc=1 KILLED | 1 failed, 29 passed, 4 deselected | first red: ['test_truncation_task_refuses_another_budget']
M25 control compare skipped: rc=1 KILLED | 1 failed, 26 passed, 4 deselected | first red: ['test_order_task_detects_a_slot_dependent_scorer']
```

One red on the way was mine, not the probe's: the first `FakeEngine` added its state term equally to every candidate, and
a softmax cancels a shared shift, so the double's probabilities never depended on the state. The G0-3 full-vs-tail
assertion caught it; the term is now per candidate.

## 4. Contract map (PC brief D-1..D-4, G0-1..G0-6) to code and JSON

| Item | Code (`scripts/mojev_probe.py`) | JSON block |
|---|---|---|
| D-1 MoJev's own code, no remote code | `load_engine` :718 (`load_packed` via `mojev.evaluate`; `AutoProcessor.from_pretrained(snapshot, trust_remote_code=False)` :753; `Engine.__new__` :759 plus the attributes `Engine.__init__` sets at `mojev/serve.py:151-180`); a failed processor load is `Refusal("processor")`, the run stops, exit 3 | `environment.child` (versions, `mojev_file`, `attn_implementation`, processor and tokenizer class) |
| D-2 two dtypes | `load_engine` casts `model.encoder` for `fp32`; `check_dtypes` :705 refuses a variant that did not take | every cell and block is per dtype; `g0_2_matrix.dtype_agreement` (argmax agreement and the largest difference on every request scored in both: 12 matrix pairs, 3 G0-3, 9 G0-4) |
| D-3 deterministic inputs | `read_source` :291 (`git show 8c684be:docs/INCIDENT-LOG.md` as bytes, sha256 re-checked in each child); `cut_head` :582 / `cut_tail` :597 cut at token boundaries and re-count with the collator's own call until the count is exact, else `Refusal("exact-cut-failed")`; `order_plan` seed 20260924 | `plan` (question, 16 answers, 16 labels, seed, text source); each task's `setup.state` (tokens, chars, sha256) |
| D-4 one process per task | `run_child` :359 (events on a private fd; phase limit 600 s for the load, each run and any silence; VmRSS cap 32 GiB polled every 0.5 s; SIGTERM then SIGKILL by pid); `run_tasks` :1169 appends every record to `partial.jsonl` before the next task and stops at the first refusal; children run a frozen copy of the probe (:1261) | per cell `peak_rss_kb` (the child's VmHWM), `parent_max_rss_kb`, `stop` |
| G0-1 integrity | `check_weights` :238 (size, then sha256; exit 2, no load), `check_code` :255 (HEAD a74d58c and no tracked change; exit 2), `snapshot_files`, `verify_citations` :279 | `g0_1_integrity` |
| G0-2 matrix | `build_plan` :171 (24 cells, cheap first), `assemble_cell` :821 (warm-up, 3 timed runs, p50 = median, max, load, cast and processor times, RSS after load, VmHWM) | `g0_2_matrix.cells` |
| G0-3 truncation | `prepare_requests` :516 (20,000-token state, its exact first and last 16,384), `capture_reports` :640 (warnings, log records, text on fds 1 and 2 per request), `assemble_truncation` :849 (kept end from token digests, not from probabilities) | `g0_3_truncation.<dtype>`: `kept`, `dropped_tokens`, `compare.full_vs_head/full_vs_tail`, `reported`, `usage_input_tokens`, `setup.truncation_side` |
| G0-4 order | `prepare_requests` (3 plain orders as control; identity plus 5 seeded label assignments), `assemble_order` :877 | `g0_4_order.<dtype>`: `sort_site`, `control`, `labeled.per_candidate[].max_abs_change`, `largest_change`, `argmax_changes`, `method` |
| G0-5 determinism | `assemble_determinism` :910: the 4 runs of cell 4096x10 in one process, plus task `g0_5-fresh/4096x10/<dtype>` in a fresh process | `g0_5_determinism.<dtype>` |
| G0-6 Gate 1 feasibility | `projections` :957: `100 * p50_ms / 1000`, plus one load; a TIMEOUT cell gives the lower bound 60,000 s | `g0_6_gate1_feasibility` |
| the hollow-result refusal | `validate_result` :1069 / `write_result` :1098: names every missing or unmeasured cell or block; exit 4 | none written |

## 5. Gates (pasted)

```
$ /root/venv-agent-factory/bin/python -m pytest tests/test_mojev_probe.py -q --basetemp /tmp/mj/bt   (run 1, 2026-09-24T13:56:22Z)
88 passed, 1 skipped in 6.47s
run 1 rc=0
$ (run 2)
88 passed, 1 skipped in 6.54s
run 2 rc=0
# pytest set: 1 files set=010915e76590 (the pc_suite.sh set_id hash, computed locally)
# the 1 skip: test_committed_findings_hold_every_cell_block_and_quoted_p50, SKIPPED BY DECLARATION (section 8, A7)
# confirmation after HEAD moved to cb131aa (files unchanged, same sha256): 88 passed, 1 skipped in 6.77s, rc=0

$ python3 scripts/lint_delta.py --base HEAD
lint_delta (worktree vs HEAD): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed
rc=0
# VACUOUS for this lane: git diff --name-only HEAD lists no untracked file. The 2 files it linted were
# scripts/install_session_hooks.py and tests/test_session_hooks.py (JT3's). The real check on the two new files:
$ python3 -m pyflakes scripts/mojev_probe.py tests/test_mojev_probe.py
rc=0

$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean
rc=0

$ python3 scripts/ap_screen.py scripts/mojev_probe.py tests/test_mojev_probe.py
--- AP_SCREEN over 2 path(s): 15 hits over 2 files ---
AP-32: 12
    scripts/mojev_probe.py:229: h = hashlib.sha256()
    scripts/mojev_probe.py:304: "sha256": hashlib.sha256(data).hexdigest(),
    scripts/mojev_probe.py:506: digest = hashlib.sha256(data).hexdigest()
    scripts/mojev_probe.py:513: return {"tokens": tokens, "chars": len(text), "sha256": hashlib.sha256(text.encode("utf-8")).hexdige
    scripts/mojev_probe.py:557: return hashlib.sha256(json.dumps(list(ids), separators=(",", ":")).encode()).hexdigest()
    scripts/mojev_probe.py:1108: return hashlib.sha256(text.encode("utf-8")).hexdigest()
    tests/test_mojev_probe.py:228: source_sha256=hashlib.sha256(data).hexdigest(), threads=6)
    tests/test_mojev_probe.py:356: def test_weights_refuse_a_wrong_hash(tmp_path):
    ... +4
AF-AP-175: 3
    scripts/mojev_probe.py:260: head = git("rev-parse", "HEAD")
    scripts/mojev_probe.py:1264: "repo_head": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True,
    tests/test_mojev_probe.py:400: head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True,
rc=0
$ python3 scripts/ap_screen.py --tests tests/test_mojev_probe.py
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---
rc=0
# the AP-32 and AF-AP-175 hits are classified in section 11

$ for f in scripts/mojev_probe.py tests/test_mojev_probe.py tasks/briefs/jev-laya/MOJEV-G0-S-report.md; do printf '%s %s\n' "$(LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' $f)" "$f"; done
0 scripts/mojev_probe.py
0 tests/test_mojev_probe.py
0 tasks/briefs/jev-laya/MOJEV-G0-S-report.md

$ sha256sum scripts/mojev_probe.py tests/test_mojev_probe.py
4ab75259308e0d55e5caae591bab4a1b4d33928d75f5e2047b9dbeeda222ece7  scripts/mojev_probe.py
dc6dc7081f32ef840b99406dc029969f5a107965d5e8d9b43514b2f293fe9cc7  tests/test_mojev_probe.py
$ wc -l scripts/mojev_probe.py tests/test_mojev_probe.py
  1306 scripts/mojev_probe.py
   893 tests/test_mojev_probe.py
  2199 total
```

## 6. The dry run (sandbox, `--pin` = the static clone at a74d58c, so the 11 citations are re-read; rc 0)

The dry run needs no torch, no tokenizer and no weights: it prints the planned cuts (the realized cuts, with their sha256,
are in each task's `setup` record on the PC). Without `--pin`/`--snapshot` it prints "not given"; a given path that is
missing, or a weights file of the wrong size, prints MISSING or MISMATCH and exits 2.

```
$ cd /tmp && python3 /home/user/agent-factory/scripts/mojev_probe.py --dry-run --pin /home/user/molemo-lab/mojev
MOJEV-G0 dry run: no model, no torch import, nothing written.
probe scripts/mojev_probe.py sha256 4ab75259308e0d55e5caae591bab4a1b4d33928d75f5e2047b9dbeeda222ece7
state source: git show 8c684be:docs/INCIDENT-LOG.md (commit 8c684be8c6dc525f8eaaeab474038be7fce2987d): 548542 bytes, sha256 550c58743e7fef4877f024b97178e907de01dc115c69dc0add3eb735a64b6b19, image markers 0
pin: /home/user/molemo-lab/mojev present
  citations: 11 of 11 lines match
snapshot: not given (required for a run)
question: subsystem_of_the_first_incident (one question per request, through Engine.answer)
candidates (5 = the first five, 10 = the first ten, 16 = all):
   1. PC bridge
   2. push script
   3. CI gate
   4. wiki hooks
   5. lane dispatcher
   6. vLLM server
   7. OmniRoute route
   8. proof runner
   9. ledger file
  10. gVisor sandbox
  11. egress policy
  12. Hermes profile
  13. task database
  14. GitNexus index
  15. Ouroboros server
  16. test suite
G0-4 labels (answer i gets LABELS[assignment[i]]): A. B. C. D. E. F. G. H. I. J. K. L. M. N. O. P.
tasks, in run order (one process each):
  01 2048x5/released_bf16: state = first 2048 tokens (exact), candidates = first 5, warm-up + 3 timed runs
  02 2048x5/fp32: state = first 2048 tokens (exact), candidates = first 5, warm-up + 3 timed runs
  03 2048x10/released_bf16: state = first 2048 tokens (exact), candidates = first 10, warm-up + 3 timed runs
  04 2048x10/fp32: state = first 2048 tokens (exact), candidates = first 10, warm-up + 3 timed runs
  05 2048x16/released_bf16: state = first 2048 tokens (exact), candidates = first 16, warm-up + 3 timed runs
  06 2048x16/fp32: state = first 2048 tokens (exact), candidates = first 16, warm-up + 3 timed runs
  07 4096x5/released_bf16: state = first 4096 tokens (exact), candidates = first 5, warm-up + 3 timed runs
  08 4096x5/fp32: state = first 4096 tokens (exact), candidates = first 5, warm-up + 3 timed runs
  09 4096x10/released_bf16: state = first 4096 tokens (exact), candidates = first 10, warm-up + 3 timed runs
  10 4096x10/fp32: state = first 4096 tokens (exact), candidates = first 10, warm-up + 3 timed runs
  11 4096x16/released_bf16: state = first 4096 tokens (exact), candidates = first 16, warm-up + 3 timed runs
  12 4096x16/fp32: state = first 4096 tokens (exact), candidates = first 16, warm-up + 3 timed runs
  13 g0_5-fresh/4096x10/released_bf16: state = first 4096 tokens (exact), candidates = first 10, 1 run (G0-5 fresh process)
  14 g0_5-fresh/4096x10/fp32: state = first 4096 tokens (exact), candidates = first 10, 1 run (G0-5 fresh process)
  15 g0_4/released_bf16: state = first 4096 tokens, 16 candidates, seed 20260924
       control-0 (listed order of answers): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
       control-1 (listed order of answers): [9, 4, 1, 5, 3, 7, 11, 6, 15, 12, 2, 14, 8, 10, 13, 0]
       control-2 (listed order of answers): [15, 10, 8, 9, 2, 14, 6, 5, 1, 13, 12, 3, 4, 0, 11, 7]
       label-0 (answer i -> slot): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
       label-1 (answer i -> slot): [13, 5, 2, 3, 1, 14, 0, 4, 10, 6, 11, 12, 15, 9, 8, 7]
       label-2 (answer i -> slot): [12, 1, 13, 11, 5, 0, 10, 15, 6, 9, 14, 7, 2, 4, 8, 3]
       label-3 (answer i -> slot): [9, 12, 5, 11, 8, 3, 14, 6, 4, 10, 0, 15, 7, 2, 1, 13]
       label-4 (answer i -> slot): [1, 15, 2, 10, 9, 14, 11, 4, 8, 0, 5, 3, 12, 7, 13, 6]
       label-5 (answer i -> slot): [3, 10, 9, 4, 7, 2, 1, 0, 8, 14, 6, 13, 11, 12, 5, 15]
  16 g0_4/fp32: state = first 4096 tokens, 16 candidates, seed 20260924
       control-0 (listed order of answers): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
       control-1 (listed order of answers): [9, 4, 1, 5, 3, 7, 11, 6, 15, 12, 2, 14, 8, 10, 13, 0]
       control-2 (listed order of answers): [15, 10, 8, 9, 2, 14, 6, 5, 1, 13, 12, 3, 4, 0, 11, 7]
       label-0 (answer i -> slot): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
       label-1 (answer i -> slot): [13, 5, 2, 3, 1, 14, 0, 4, 10, 6, 11, 12, 15, 9, 8, 7]
       label-2 (answer i -> slot): [12, 1, 13, 11, 5, 0, 10, 15, 6, 9, 14, 7, 2, 4, 8, 3]
       label-3 (answer i -> slot): [9, 12, 5, 11, 8, 3, 14, 6, 4, 10, 0, 15, 7, 2, 1, 13]
       label-4 (answer i -> slot): [1, 15, 2, 10, 9, 14, 11, 4, 8, 0, 5, 3, 12, 7, 13, 6]
       label-5 (answer i -> slot): [3, 10, 9, 4, 7, 2, 1, 0, 8, 14, 6, 13, 11, 12, 5, 15]
  17 8192x5/released_bf16: state = first 8192 tokens (exact), candidates = first 5, warm-up + 3 timed runs
  18 8192x5/fp32: state = first 8192 tokens (exact), candidates = first 5, warm-up + 3 timed runs
  19 8192x10/released_bf16: state = first 8192 tokens (exact), candidates = first 10, warm-up + 3 timed runs
  20 8192x10/fp32: state = first 8192 tokens (exact), candidates = first 10, warm-up + 3 timed runs
  21 8192x16/released_bf16: state = first 8192 tokens (exact), candidates = first 16, warm-up + 3 timed runs
  22 8192x16/fp32: state = first 8192 tokens (exact), candidates = first 16, warm-up + 3 timed runs
  23 16384x5/released_bf16: state = first 16384 tokens (exact), candidates = first 5, warm-up + 3 timed runs
  24 16384x5/fp32: state = first 16384 tokens (exact), candidates = first 5, warm-up + 3 timed runs
  25 16384x10/released_bf16: state = first 16384 tokens (exact), candidates = first 10, warm-up + 3 timed runs
  26 16384x10/fp32: state = first 16384 tokens (exact), candidates = first 10, warm-up + 3 timed runs
  27 16384x16/released_bf16: state = first 16384 tokens (exact), candidates = first 16, warm-up + 3 timed runs
  28 16384x16/fp32: state = first 16384 tokens (exact), candidates = first 16, warm-up + 3 timed runs
  29 g0_3/released_bf16: state = first 20000 tokens; head cut = its first 16384; tail cut = its last 16384; budget = checkpoint context_tokens (16384 planned); candidates = first 5
  30 g0_3/fp32: state = first 20000 tokens; head cut = its first 16384; tail cut = its last 16384; budget = checkpoint context_tokens (16384 planned); candidates = first 5
matrix cells: 24 (planned 24); tasks: 30; model loads: 30; scored requests: 122
limits: 6 threads, nice >= 10, 600 s per load or run, RSS cap 33554432 kB (32 GiB); child env {'CUDA_VISIBLE_DEVICES': '', 'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1', 'OMP_NUM_THREADS': '6', 'MKL_NUM_THREADS': '6', 'OPENBLAS_NUM_THREADS': '6', 'TOKENIZERS_PARALLELISM': 'false'}
rc=0
```

## 7. PC command lines for the coordinator

Run from the PC clone at the pushed PIN (`/home/rocco/agent-factory`, `PC_AF_REPO` in `scripts/pc_suite.sh:27`;
push_clean rewrites SHAs, so read the PIN from origin after the push). Each `pc.sh` call stays short: the long runs are
backgrounded with `nohup` on their own line and polled with separate calls (the 120 s `pc.sh` cap).

```
# 1. Dry run (seconds; no model): the plan, the 11 citations re-read on ~/mojev-pin, the weights size. Expect rc 0.
cd /home/rocco/agent-factory && ~/venv-mojev/bin/python scripts/mojev_probe.py --dry-run --pin ~/mojev-pin --snapshot ~/mojev-snapshot/0c8695b6252f

# 2. Smoke: 2 tasks (includes the full G0-1 hash of 1.7 GB). Expect exit=0 with two OK lines, or exit=3 and a named refusal.
mkdir -p ~/mojev-g0-run
cd /home/rocco/agent-factory && nohup bash -c 'CUDA_VISIBLE_DEVICES= HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 nice -n 10 ~/venv-mojev/bin/python scripts/mojev_probe.py --pin ~/mojev-pin --snapshot ~/mojev-snapshot/0c8695b6252f --out ~/mojev-g0-run/smoke.json --only 2048x5/released_bf16 --only 2048x5/fp32; echo "exit=$?"' > ~/mojev-g0-run/smoke.log 2>&1 < /dev/null &

# 3. The full run: 30 tasks, 122 scored requests, 30 model loads.
cd /home/rocco/agent-factory && nohup bash -c 'CUDA_VISIBLE_DEVICES= HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 nice -n 10 ~/venv-mojev/bin/python scripts/mojev_probe.py --pin ~/mojev-pin --snapshot ~/mojev-snapshot/0c8695b6252f --out ~/mojev-g0-run/mojev-probe-0.json; echo "exit=$?"' > ~/mojev-g0-run/run.log 2>&1 < /dev/null &

# 4. Poll (separate short calls); done when the log's last line is exit=N.
tail -n 3 ~/mojev-g0-run/run.log
```

Exit codes: 0 = the JSON is written and its sha256 printed, and `~/mojev-g0-run/mojev-probe-0.json.work-<stamp>/cells.md`
holds the cell table for `MOJEV-PROBE-0.md`; 2 = G0-1 refused, nothing loaded; 3 = a child refused and the run stopped;
4 = a cell or block is unmeasured (each named on stderr). In every case the work directory keeps `partial.jsonl` (one
record per finished task, written before the next starts), one `<task>.stderr.log` per child, the frozen probe and the
state source. The env exports and `nice` above are belt and braces: every child sets them itself and refuses a visible
CUDA device, a thread count other than 6, a mojev imported from outside `--pin`, and a dtype variant that did not take.

Harvest (the coordinator's): copy the JSON to `docs/research/findings/mojev-probe-0.json`, write `MOJEV-PROBE-0.md` quoting
`cells.md` (the committed-findings test looks for each cell id with its p50 at one decimal on one line), and set
`FINDINGS_FILED = True` (`tests/test_mojev_probe.py:36`) in the same commit. The test file then checks the committed pair.

Prerequisites (ASSUMED, not checked here): `~/venv-mojev` holds transformers 5.17.0 (the release's `transformers_version`),
a torch build that runs on this CPU, and what the processor needs to load without remote code: pillow and a torchvision
matching the torch (the Space pins torch 2.13.0, torchvision 0.28.0, transformers 5.17.0; `mojev/space/requirements.txt`).
Nothing else on the probe's import path is third-party (`mojev/{evaluate,full,data,calibrate,serve,schema,modeling}.py`
import only torch and transformers at module level; PIL only on the image path, which the probe refuses).

Run time: unknown until measured. At the audit's own unmeasured estimate (about 20 s per 4k decision and 60 s per 16k,
section 4 item 3) the full run takes about 75 minutes; bf16 on a CPU without bf16 instructions may be several times slower.
Every load, every run, and any silence is capped at 600 s. Run it when no other heavy CPU job runs: the host's load
average is recorded at start and end (`host.loadavg`, `host.loadavg_end`).

## 8. Deviations and additions (flagged)

- A1 `--only TASK_ID` (repeatable): a smoke mode, not in either brief. It writes the partial log, never the final JSON.
- A2 G0-1 also REFUSES a `--pin` whose HEAD is not a74d58c or that has a tracked change (the brief asks to record the code
  HEAD; refusing is stricter). The snapshot's other top-level files are recorded (size, sha256), not refused.
- A3 G0-3 and G0-4 run in BOTH dtypes (the brief names no dtype for them): so a TIMEOUT in one dtype cannot leave G0-3
  empty, and D-2's "every request scored in both" covers them. G0-5 is per dtype too.
- A4 G0-5 "twice in one process": the four runs (warm-up and three timed) of matrix cell 4096x10 are the same request in
  one process; "once in a fresh process" is a dedicated one-run task per dtype. No second in-process pass was added.
- A5 The writer refuses an UNMEASURED cell or block (a child error), not only a missing one; TIMEOUT and RSS_CAP count,
  each with its phase and elapsed time.
- A6 The phase limit (600 s) covers the load and any silence between phases, not only a single run.
- A7 The committed-findings test (TESTS, third bullet) cannot pass in the sandbox: the findings do not exist until the PC
  run. It is SKIPPED BY DECLARATION (`FINDINGS_FILED = False`, `tests/test_mojev_probe.py:36`), not by file presence
  (AF-AP-44's class), and `test_findings_declaration_matches_the_tree` turns red if either file appears without the flag.
  Its checker is tested now against a complete fixture and a damaged one.
- A8 The RSS cap is 32 GiB = 33,554,432 kB of VmRSS, polled every 0.5 s: a poll, not a kernel limit. A child that grows
  faster than that between polls can pass the cap by the growth of 0.5 s before it is stopped.
- A9 The state source is fixed at `8c684be:docs/INCIDENT-LOG.md` (the PC brief's PIN; `--text-rev` overrides), not the
  copy at the pushed PIN, so the inputs do not change when the tree moves.
- A10 D-1 names "the path `serve.py`'s `Engine` uses", but `Engine.__init__` loads the processor with
  `trust_remote_code=True` (`mojev/serve.py:171`), which D-1 forbids. The probe calls `Engine.answer` unmodified on an
  Engine built with `Engine.__new__` and the attributes `__init__` sets, the processor loaded with `trust_remote_code=False`.
- A11 G0-4 uses leading labels "A. " to "P. " to move answers between packed slots, as the brief prescribes. The label
  text moves with the slot, so a change mixes the slot effect and the label text; the JSON says so (`g0_4_order.*.method`).
  A plain reorder is the control (the sort makes it invisible). A measurement with the sort bypassed (the same strings in
  different slots, `mojev/consistency.py:83-86` calls it "raw packing position") would separate the two; NOT built.

## 9. NOT done (first-class)

- N1 Nothing ran on the PC. No model was loaded; no latency, memory, probability or truncation number exists. G0-1 to G0-6
  results, `docs/research/findings/mojev-probe-0.json`, `MOJEV-PROBE-0.md` and the PC brief's report
  (`tasks/briefs/jev-laya/MOJEV-G0-report.md`) are the coordinator's, after the run.
- N2 The real loader `load_engine` (:718) never ran with torch. Only its no-torch failure path ran
  (`test_real_child_without_torch_fails_loudly_and_measures_nothing`: status ERROR, exit 1, no phase ended, no number).
- N3 `main` past G0-1 (the task loop with real children, assembly from real records, the JSON write) needs the 1.7 GB
  weights and did not run here. Its parts are tested: `run_tasks`, `run_child`, `assemble_result`, `write_result`.
- N4 Whether the real BPE tokenizer's head and tail cuts reproduce the exact token ids is unknown until the PC run; each
  G0-3 record says (`setup.head_cut.equals_first`, `setup.tail_cut.equals_last`).
- N5 The sort-bypass order measurement (A11): NOT built.
- N6 No GitNexus impact or detect_changes: every symbol is new and nothing is committed; the coordinator's pre-commit
  detect_changes covers it.
- N7 No commit, no staging (the shared index was not touched), no push, no bridge call.
- N8 The PC-side premise lines (section 1c) were not re-measured.

## 10. Discrepancies

- X1 Snapshot path: the PC brief (`pc-mojev-g0.md:40`) names `~/mojev-snapshot/0c8695b6252f4205907433d4e196a94f032e60c3/`;
  the sandbox brief (line 10), `todo/BUILD-TASKLIST.md:1432` and `wiki/topics/live-state.md:58` name
  `~/mojev-snapshot/0c8695b6252f/`. The probe takes the path as an argument; the command lines above use the ledger's.
- X2 The named lint gate is vacuous for new files: `lint_delta.py --base HEAD` diffs tracked files only, so it linted
  JT3's two files and neither of this lane's. Already known: CLAUDE.md since 503c3e2 (JT1 DISC-1) says a lane's new
  files are linted by `pyflakes` directly until staged, which is the check pasted in section 5 (clean). The sandbox
  brief's gate line predates that note.
- X3 Free disk 2.9G against the premise's 957M (not design-changing).
- X4 HEAD moved during the lane: db71586 (the dispatch PIN), then cda44b8, then a push_clean rewrite and more commits
  to cb131aa (db71586's twin on origin is db34178). Checked at cb131aa: both briefs are byte-identical to what this lane
  read (`git diff db71586 HEAD -- <the two briefs>` empty); 8c684be is still an ancestor of HEAD; the state source
  `8c684be:docs/INCIDENT-LOG.md` still hashes to 550c58743e7fef4877f024b97178e907de01dc115c69dc0add3eb735a64b6b19.
  `docs/INCIDENT-LOG.md` did change at HEAD, which is why the probe reads it at a fixed revision (A9).
- X5 The tracked-file dirt of other lanes changed during the lane (at start: J1-1-R4's `volatile.py` and
  `test_decisions_*.py`; at the lint gate: JT3's `install_session_hooks.py` and `test_session_hooks.py`). Not touched.

## 11. Screen hits, classified

- AP-32 (12, hashing): each digest is compared only with a digest of the same byte form. The weights: `sha256_file` of the
  file bytes against the Hub's LFS sha256, which is the sha256 of the same bytes (the premise's Hub listing, and the PC
  prep log's own `OK sha256 model.safetensors eae27bf0...`). The state source: the parent's sha256 of the `git show` bytes
  against the child's sha256 of the same file's bytes (`read_bytes` on both sides, no newline translation). The token-id
  and packed-input digests (`ids_digest`) are produced and compared inside the probe with one function. Reviewed-safe.
- AF-AP-175 (3, a quoted HEAD): `check_code` reads the pin's HEAD once, and its second git call (`status --porcelain`)
  compares the working tree with the index, not a second read of the ref. The probe repo's HEAD is read once at the run
  start, beside the sha256 of the frozen probe copy the children run. The third is the test's own temp repo. Residual,
  stated: a change to `~/mojev-pin` after the start check is not detected (the pin is read-only by rule).

## 12. Self-attack: the three likeliest ways this is wrong, and what rules each out

1. The real MoJev path fails on the PC in a way the doubles cannot show (the processor's dependencies, the bf16 encoder
   with MoJev's float32 4-D mask under SDPA, offsets from the tokenizer). Ruled out as far as the sandbox allows: every seam
   read in the a74d58c source and in transformers 5.17.0 (section 2); the 11 cited lines re-read on the PC pin by the dry
   run and by every run; a two-task smoke before the long run. A failure is loud by construction: a refusal stops the run
   (exit 3), an error leaves the cell unmeasured and the writer refuses the result (exit 4). The probe has no code path
   that makes a number without the real model (`test_real_child_without_torch_fails_loudly_and_measures_nothing`).
2. The tests mirror my own reading of `Engine.answer`. The doubles copy the contract from cited lines
   (`mojev/serve.py:122-127,182-231`, `mojev/full.py:83,167-192`), and 30 of 30 mutants of the probe die (section 3a), but
   a misreading shared by the probe and the double would pass both. The PC run is the only check of that; its first sign
   would be a `state-tokens` refusal or an ERROR in the smoke.
3. The measurements answer a slightly different question than asked. G0-4 mixes slot and label text (A11, stated in the
   JSON). G0-3's probability comparison is bitwise only when the head and tail cuts reproduce the token ids (recorded
   per run); the kept-end verdict uses token digests, so it does not depend on that. Timings share a CPU with whatever
   else runs (load average recorded; run when the box is quiet).

## 13. Evidence tiers

- VERIFIED (this session, primary): the sandbox-side premise lines (section 1); the MoJev seams by static reading of the
  a74d58c clone and the transformers 5.17.0 source; the 11 citations against that clone (11 of 11); both test runs
  (88 passed, 1 skipped, set 010915e76590); 30 of 30 mutants killed; the gates in section 5; the dry run in section 6.
- INFERRED: the PC's `~/mojev-pin` holds the same bytes as the sandbox clone (same commit a74d58c, per the premise); the
  run re-reads the 11 lines there. AutoProcessor resolves Qwen3VLProcessor from `preprocessor_config.json` without
  remote code (read, not run; holds for transformers 5.17.0 only).
- ASSUMED: `~/venv-mojev`'s contents; that the Engine path runs on this CPU in both dtypes; the run time; that 32 GiB is
  enough for the 16,384-token cells.

## 14. Files (untracked; not staged, not committed)

- `scripts/mojev_probe.py` (new, 1306 lines, sha256 4ab75259308e0d55e5caae591bab4a1b4d33928d75f5e2047b9dbeeda222ece7)
- `tests/test_mojev_probe.py` (new, 893 lines, 56 test functions, 89 collected; sha256
  dc6dc7081f32ef840b99406dc029969f5a107965d5e8d9b43514b2f293fe9cc7)
- `tasks/briefs/jev-laya/MOJEV-G0-S-report.md` (this report)
