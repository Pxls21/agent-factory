# FT1 report: the Laya fine-tune tooling (task #233; D-075, D-078)

Lane: ft1 (sandbox, `code-implementer`, Opus 5.5, shared tree). Written incrementally; this is the final state.
PIN (local HEAD at dispatch): `af3b1a74e4e7f3de8b7bd7ac1ff73c035f6b6738` (read 2026-09-24 15:20:27Z). HEAD moved four
times during the lane (`cf8aec19`, `144c9a80`, `ec77d723`, `8c97db67`: coordinator commits); nothing here depends on it.

## Status

**DONE (tests green, live smokes run): the four tools exist, are tested (22 tests, twice), and ran on the real tree, the
real model and the real teacher API.** Nothing is committed (the brief forbids it). NOT done, first-class, in section 11:
the full labeling run and the GPU training (the coordinator's, by D-078), `--mode full` never executed, the evaluator's
`v1_full`, `ap` and blocking runs never executed live, and no PC-venue test run.

Files created (all untracked):

| File | Lines | What it is |
|---|---:|---|
| `scripts/laya_ft/__init__.py` | 1 | package marker (imports go through `laya_ft.*`, never a bare `common`) |
| `scripts/laya_ft/common.py` | 307 | pure Python: the D-6 questions, the D-3 held-out identities, the dataset loader, the label format and join |
| `scripts/laya_ft/build_dataset.py` | 248 | D-2, D-3, D-4: sources at one commit, masked, scrubbed, fitted to Laya's window |
| `scripts/laya_ft/teacher_label.py` | 247 | D-5: the resumable, rate-limited teacher client |
| `scripts/laya_ft/train.py` | 337 | D-1, D-7: the trainer (head or full, CPU or CUDA) |
| `scripts/laya_ft/evaluate.py` | 210 | D-8: J2's own scorers, in process, with the positive control |
| `tests/test_laya_ft.py` | 757 | 22 deterministic LLM-free tests |
| `tasks/briefs/jev-laya/FT1-report.md` | | this report |

## 1. Premise re-measure (2026-09-24 15:20Z): no mismatch

| Premise line | Measured now | Match |
|---|---|---|
| `laya 0.3.5 transformers 5.17.0 torch 2.14.0+cpu` | same | yes |
| `laya/common.py` greps: `build_sequence` 49, `target` 181/188, `collate_items` 247, `has_target` 257/258/266/267 | same, plus lines 276 and 279 | yes (D-P1) |
| `def forward` at 105 | 105 | yes |
| `DecisionModel` 89, `proper_reward` 150, `ece_score` 197, `collate_items` 247 | same | yes |
| `v1_probe.py` `CLASSES` 25, `BLOCKING` 33, `MASK` 34 | same | yes |
| three sample.json sha256 (b1cf78..., af4695..., c07c58...) | same | yes |
| 91 `VERIFY-*-report.md` under `tasks/briefs` at HEAD | 91 | yes |

D-P1 (a discrepancy, not a mismatch): the premise's first grep lists 8 lines; the same command prints 10. The two extra
lines (276 and 279) are inside `collate_items` and also contain `"target"`. The installed `laya/common.py` hashes to its
pip RECORD entry (`sha256=8jHUL87ITaIDIi_KqJwIOyJ3bgA0HmbhGBg9dU4dyr8`, 11,440 bytes, mtime 2026-09-22 17:06), so the file
did not change after install; the brief's output was trimmed. No seam moved.

Also verified: both copies of the snapshot under `/root/hf-laya-probe` (`hub/models--...` and `models--...`) are
byte-identical, and every blob matches its content hash (git blob sha1 or sha256): the cache is pristine. The running
server (`/health`) loaded `/root/hf-laya-probe/hub/models--convaiinnovations--laya/snapshots/1c5edc17.../typed-decisions`;
the tools default to that path (`--model-dir` for the PC).

## 2. Measured sources (verified)

| Source | at `144c9a80` (the smoke build) | at `8c97db67` (17:01Z) | Note |
|---|---:|---:|---|
| `VERIFY-*-report.md` under `tasks/briefs` | 91 | 92 | |
| reports whose findings follow decide-harvest's grammar (j2c `_blocks`) | 10 | 11 | the other 81 yield nothing to this extractor |
| findings (whole blocks) | 162 | 186 | classes at `cf8aec19`: INFO 80, FOLLOW-UP 68, BLOCKER 7, KNOWN 3, UNVERIFIED 2, CONTRACT-DEFECT 2 (counted here once; never stored) |
| held-out findings excluded (J2 = J2c: the same 100 rows) | 100 of 100 | 100 of 100 | every J2c `source` found; every J2c state equals the block's `_mask` at HEAD |
| **trainable findings** (2 rows each) | **62** | **86** | |
| incident entries (anchored) | 199 | 200 | 10 span several lines; median 1,418 chars, max 12,935 (at `cf8aec19`) |
| held-out incident entries excluded (AP sample) | 100 of 100 | 100 of 100 | by masked heading; by the sample's LINE number 0 of 100 would match |
| **trainable incident entries** (16 candidate rows each) | **99** | **100** | |
| registry rows | 191 | 191 | |
| **dataset rows** (`v1.finding_class` / `v1.blocking` / `ap.violates_row`) | **62 / 62 / 1,584 = 1,708** | **86 / 86 / 1,600 = 1,772** | ap rows cut to the window: 32 (two entries of 9,476 chars, cut to about 3,100) |

The size of the finding source is the brief's biggest practical limit: 62 (now 86) trainable findings, because only 10
(now 11) of the reports use the grammar j2c.py and decide-harvest read. See section 11.

## 3. Design decisions (with the rejected alternative)

- **Held-out incident identity = the masked heading text, not the sample's line number.** The line numbers are the sample
  commit's (2ea5f62) and all 100 drifted; the headings all match exactly. Rejected: line numbers (0 of 100 match).
- **The v1 held-out identity = J2c's `source` (path#finding id); J2 rows map to it by `row_digest`** (100 of 100;
  `heldout_identities` at `scripts/laya_ft/common.py:136`, refused by `check_no_heldout` at `scripts/laya_ft/common.py:190`
  and again on every load by `load_dataset` at `scripts/laya_ft/common.py:203`). A second
  guard refuses a v1 state equal to any held-out J2c state (0 at HEAD; mutant M1b shows it catching a leak on its own).
- **Window fit in the builder** (`Fitter.fit`, `fit` at `scripts/laya_ft/build_dataset.py:144`). `build_sequence` cuts a long state from the right,
  and the ap state puts the chunk after the query, so a long entry loses the candidate row (D-076(b)/F-24 saw the same tie).
  The builder cuts the finding, or the query, never the chunk, to the longest prefix `build_sequence` keeps whole, judged
  by the consumer. The test re-checks every row with `build_sequence` at an unbounded length (0 truncated). Rejected: a
  character budget (JT1's 1,000/2,500 client rule), which is not exact for this tokenizer.
- **Order-preserving JSON.** The ap state must serialize `query` before `chunk` (the server's fan-out order J2 scored) and
  a choice's criteria order is its option order, which is the target order. Rows are never dumped with `sort_keys`; files
  are ASCII JSON and split on `\n` only (`str.splitlines()` splits on U+2028).
- **Content-derived item ids** (`v1-`/`ap-` + a sha256 prefix of the state). A label stays valid when the dataset is
  rebuilt at a later commit with the same text (the dataset sha256 was identical at `cf8aec19` and `144c9a80`). Each label
  records the digests of the state and question as SENT; `join_labels` (`scripts/laya_ft/common.py:284`) refuses a label
  whose digests differ from its row.
- **The evaluator runs the committed J2 scorers unchanged** (its `main` at `scripts/laya_ft/evaluate.py:117`): `v1_probe.cmd_score` and
  `ap_probe.cmd_score`, with only `post` swapped for the local server's own `_answer` in process (openjev_j2.py's pattern).
- **The teacher client takes pending keys round-robin across question ids** (`schedule`, `scripts/laya_ft/teacher_label.py:95`), so
  `--limit 5` covered all three types live.
- **The trainer uses Laya's own head-only switch** (`detach_encoder=True`) AND freezes the encoder's `requires_grad`
  (`select_trainable`, `scripts/laya_ft/train.py:51`); either alone keeps the weights, and the test also asserts the selection.
- **`save_checkpoint` refuses before writing when the disk cannot hold it** (`save_checkpoint` at `scripts/laya_ft/train.py:149`), and removes a
  partial `.tmp`. Added after this lane filled the sandbox disk (section 10).
- **The loss** is `loss_fn` at `scripts/laya_ft/train.py:97`: the negated `proper_reward` over the softmax of the logits,
  marker-masked. **The rate limit** is the `Limiter` at `scripts/laya_ft/teacher_label.py:49` (60 in any 60 s, 1 s apart).
- **Question (a) uses J2's own instruction** ("Which class did the verifier give this finding?"), so the J2 `choice` the
  evaluator scores IS the trained question (a behavioral test runs the committed scorer and compares what it sends).

## 4. Live smokes (each pasted from its run; outputs in the lane scratchpad, not the repo)

### 4a. `build_dataset.py` on the real tree (15:58:34Z; 11.5 s wall at `cf8aec19`)

`HF_HUB_OFFLINE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --out <scratch>/ds` rc=0:

```
"commit": "144c9a80e9bee50069c8aa345e32635b8290a176",
"counts": {"cut_to_window": {"ap.violates_row": 32, "v1.blocking": 0, "v1.finding_class": 0}, "merged_duplicates": 0,
           "rows": {"ap.violates_row": 1584, "v1.blocking": 62, "v1.finding_class": 62}, "rows_total": 1708,
           "trainable_entries": 99, "trainable_findings": 62},
"dataset": {"bytes": 3940077, "file": "dataset.jsonl", "sha256": "3ee28a4ea24f2211db765460b311d750f698f8d71eca4508ca13a1d6e42deaee"},
"heldout": {"incident_entries": {"excluded": 100, "identities": 100}, "text_duplicates_excluded": 0,
            "verify_findings": {"excluded": 100, "identities": 100},
            "samples": {"docs/research/findings/ap-hawk-probe/sample.json": {"rows": 100, "sha256": "c07c581a..."},
                        "docs/research/findings/j2-v1-probe/sample.json": {"rows": 100, "sha256": "b1cf7867..."},
                        "docs/research/findings/j2c-fulltext/sample.json": {"rows": 100, "sha256": "af469599..."}}},
"model": {"config_sha256": "ebf0cd52...", "head_max_len": 256, "max_len": 1024,
          "revision": "1c5edc17a7acd8701df6fc341c0d179f1c62c982", "tokenizer_sha256": "6c8aaa9a..."},
"sources": {"candidates_per_entry": 16, "entries_without_heading": 0, "incident_entries": 199, "registry_rows": 191,
            "reports_with_findings": 10, "verify_findings": 162, "verify_reports": 91}
```

The manifest also carries each question's sha256 and the sha256 of the seven code files the build used.

### 4b. `teacher_label.py --limit 5` against codiv.ai (16:38:40Z to 16:38:44Z; the one sanctioned third-party call)

`python3 scripts/laya_ft/teacher_label.py --dataset <scratch>/ds --out <scratch>/labels.jsonl --limit 5` rc=0:

```
labeled ap-217adfe91c941432c3a1|ap.violates_row type=noul k=2 attempts=1 input_tokens=503
labeled v1-04ba6bdba8481673cd9d|v1.blocking type=noul k=2 attempts=1 input_tokens=200
labeled v1-04ba6bdba8481673cd9d|v1.finding_class type=choice k=6 attempts=1 input_tokens=301
labeled ap-273641f63fe50a871f58|ap.violates_row type=noul k=2 attempts=1 input_tokens=492
labeled v1-56244741b4aa47844ae3|v1.blocking type=noul k=2 attempts=1 input_tokens=131
usage: requests=5 retries=0 answers=5 input_tokens=1627 stored=5 skipped_done=0 pending_left=1703 scrub_changed=0 endpoint=api.codiv.ai dataset=3ee28a4ea24f2211
```

The stored distributions (target = the soft target in option order; the raw answer as returned):

| Key (prefix) | Question | Model | Target (option order) | Raw answer fields |
|---|---|---|---|---|
| ap-217adfe9 | ap.violates_row | openjev-0.1 | [0.4203, 0.5797] (len 2, sum 1.0) | `noul`, `type` |
| v1-04ba6bdb | v1.blocking | openjev-0.1 | [0.381, 0.619] | `noul`, `type` |
| v1-04ba6bdb | v1.finding_class | openjev-0.1 | [0.4677, 0.5263, 0.0003, 0.001, 0.0018, 0.0028] (len 6, sum 1.0) | `choice`, `confidence`, `probabilities`, `type` |
| ap-273641f6 | ap.violates_row | openjev-0.1 | [0.8349, 0.1651] | `noul`, `type` |
| v1-56244741 | v1.blocking | openjev-0.1 | [0.9917, 0.0083] | `noul`, `type` |

OpenJev's shapes, now measured: a `choice` answer carries full-precision `probabilities` over exactly the six options (and
`choice` at the maximum); a `noul` answer carries only `noul` (no `confidence`). The labels file holds no state text and no
key (0 matches).

### 4c. Eleven more labels through the same client, from the LOCAL Laya server (16:39:13Z to 16:39:40Z)

The train smoke needs 16 labeled items and the brief allows only 5 codiv requests. The other 11 came from the same client
pointed at the local server on 127.0.0.1:47411 (not third-party; a scratch env file, a dummy key the server ignores):

```
usage: requests=11 retries=0 answers=11 input_tokens=2679 stored=11 skipped_done=5 pending_left=1692 scrub_changed=0 endpoint=127.0.0.1:47411 dataset=3ee28a4ea24f2211
```

`skipped_done=5`: the resume path worked live (the codiv keys were never asked again). The labels file: 16 records, 5 from
`openjev-0.1 @ api.codiv.ai`, 11 from `laya-rl-agent @ 127.0.0.1:47411`. So 11 of the 16 smoke targets are the base model's
own answers (self-distillation): the smoke proves the pipeline runs and moves the loss, not that the targets are good.

### 4d. `train.py --mode head --device cpu` on 16 items, one epoch (16:39:48Z to 16:45:13Z)

`/root/venv-laya-probe/bin/python scripts/laya_ft/train.py --dataset <scratch>/ds --labels <scratch>/labels.jsonl --out
<scratch>/train1 --mode head --device cpu --limit 16 --epochs 1 --batch-size 4 --threads 4 --eval-loss` rc=0:

```
epoch 1/1 loss 0.616080 (4 steps, 266 s)
{"checkpoint": {"bytes": 105002916, "file": "checkpoint.pt", "sha256": "3515d2197af76d652830ce7306f8981e68ed3ed324ef71711794d5ce0e2682e8"}, "device": "cpu", "eval_loss_after": 0.5971451103687286, "eval_loss_before": 0.6163741201162338, "examples": {"by_question": {"ap.violates_row": 6, "v1.blocking": 6, "v1.finding_class": 4}, "n": 16}, "guards": {"act_head_unchanged": true, "encoder_unchanged": true, "model_dir_unchanged": true}, "per_epoch_loss": [0.616080142557621], "steps": 4, "trained": {"parameters": 26248193, "prefixes": ["head", "scorer", "type_emb"], "tensors": 31}, "wall_seconds": 323.2}
```

`train-manifest.json` also records: the dataset sha256 and commit, the labels sha256 (`705a5717...`) and teachers, the base
revision `1c5edc17...`, `model.safetensors` sha256 `4fa56de7...`, every hyperparameter (mode head, device cpu, epochs 1,
batch 4, lr 0.0001, weight decay 0.01, seed 1234, max grad norm 1.0, limit 16, threads 4, grad checkpointing false, AdamW,
amp none (fp32), the loss formula, the data order rule), torch 2.14.0+cpu, laya 0.3.5, transformers 5.17.0. The checkpoint
was deleted after its sha256 was recorded (the coordinator asked for small scratch).

### 4e. `evaluate.py`, NO checkpoint, the v1 sample: the positive control (15:59:00Z to 16:06:48Z)

`/root/venv-laya-probe/bin/python scripts/laya_ft/evaluate.py --only v1 --out-dir <scratch>/eval-base --threads 4` rc=0:

```
== v1 (439 s) ==
KC-J3 v1 jev_choice: accuracy 0.2100 vs max(majority 0.4300, heuristic 0.4100) = 0.4300 -> REJECTED (at or under)
KC-J3 v1 jev_noul: accuracy 0.0300 vs max(majority 0.4300, heuristic 0.4100) = 0.4300 -> REJECTED (at or under)
{"agreement_with_committed_base": {"jev_choice": "100/100", "jev_noul": "100/100"}, ..., "differences_from_committed_base": [], "ece": 0.0481, "seconds": 439.0}
POSITIVE CONTROL (no checkpoint): PASS
```

The in-process base model reproduces every committed J2 v1 number (jev_choice 0.21 / 0.1331 / 0.82 / BLOCKER 0/7;
jev_noul 0.03 / 0.1944 / 0.58 / 0/7; majority and heuristic too) and all 100 per-row predictions of both methods.

### 4f. `evaluate.py` WITH the 4d checkpoint, the v1 sample (16:45:26Z to 16:53:52Z; beyond the brief's list)

Run so the `--checkpoint` path ran end to end once: rc=0, checkpoint loaded (31 tensors; head, scorer, type_emb; sha256
`3515d219...`), every J2 v1 number and all 100 predictions per method unchanged, ECE 0.0481 -> 0.0325. The probabilities
moved; four small steps on 16 items flipped no argmax.

## 5. Tests (`tests/test_laya_ft.py`; set id `8b147318aa48` from `scripts/pc_suite.sh set-id -- tests/test_laya_ft.py`)

Final gate, `bash scripts/test_summary.sh tests/test_laya_ft.py --basetemp=/tmp/ft1/bt` (it exports `S0_01_VENUE=sandbox`),
run twice on the final files:

```
16:54:31Z  pytest-exit: 0
           pytest-summary: 22 passed in 173.55s (0:02:53)
16:57:29Z  pytest-exit: 0
           pytest-summary: 22 passed in 179.33s (0:02:59)
```

(Two earlier runs at 16:07Z and 16:08Z, before three test additions, read `22 passed in 106.29s` and `22 passed in
107.75s`.) With no venue declared, the CI shape: `18 passed, 4 skipped in 4.56s`, each skip reading "LOUD SKIP: the Laya
venv and snapshot are declared inputs of the sandbox venue only (S0_01_VENUE=None; ...)".

| Test | Proves | Venue |
|---|---|---|
| `test_questions_are_j2s_own_and_the_briefs` | D-6 texts and option order | here |
| `test_the_trained_class_question_is_the_one_j2_asked` | the committed J2 scorer sends exactly question (a) | here |
| `test_rank_reproduces_the_committed_lexical_picks` | the candidates are ap_probe's lexical top 16 (top 3 = committed, 100 of 100) | here |
| `test_ap_state_is_the_servers_fan_out_shape` | the ap state is what the server's fan-out passed to `system_one` | here |
| `test_collect_masks_scrubs_and_excludes_on_a_fixture_repo` | D-2 masking (no class word), table rows keep the title cell, the scrub (FAKE secrets), D-3 exclusion, the ap key order | here |
| `test_collect_resolves_the_commit_once_even_when_the_ref_moves` | D-4: one rev-parse, every read names the sha, a commit landing mid-run changes nothing | here |
| `test_collect_excludes_every_heldout_row_on_the_real_tree` | D-3 on the real tree against the test's own reading of the samples | here |
| `test_a_planted_heldout_row_is_refused` | D-3: a planted held-out source, heading or text is refused; `load_dataset` refuses a leak and a stale digest | here |
| `test_distribution_orders_validates_and_normalizes` | soft targets in option order; NaN, negatives, missing or extra options, a non-argmax choice, bad sums, bools refused | here |
| `test_join_refuses_a_stale_label` | a label for another state or question never trains | here |
| `test_teacher_resume_skips_done_keys` | resume, round-robin, stored targets | stand-in HTTP |
| `test_teacher_rate_limit_never_exceeds_60_per_minute` | never 61 requests in 60 s, at least 1 s apart (fake clock) | stand-in HTTP |
| `test_teacher_retries_429_and_5xx_with_backoff` | Retry-After, backoff, give-up after 7 attempts | stand-in HTTP |
| `test_teacher_key_stays_out_of_argv_output_and_labels` | the FAKE key only in the header; never in output, labels or error text (a server echoing it back); no argv option takes a key | stand-in HTTP |
| `test_teacher_scrubs_every_string_before_it_leaves` | no FAKE secret reaches a request body; the scrubbed row's label is refused as stale | stand-in HTTP |
| `test_teacher_refuses_a_malformed_answer_without_storing_it` | a NaN answer: exit 4, nothing stored | stand-in HTTP |
| `test_positive_control_comparison_flags_any_changed_number` | the evaluator's comparison catches one changed number | here |
| `test_kc_j3_lines_reject_at_or_under_the_bar` | KC-J3 verdict lines (a tie rejects) | here |
| `test_builder_is_deterministic_and_every_state_fits_the_window` | two builds byte-identical; every row kept whole by `build_sequence` | Laya venv |
| `test_trainer_three_steps_lower_the_loss_on_the_real_model` | the overfit check AND the true proper reward rises; the loss is minimal at the target | Laya venv |
| `test_trainer_head_mode_leaves_every_encoder_parameter_bitwise_unchanged` | encoder and act head bitwise unchanged; the selection; full mode trains the encoder, never the act head | Laya venv |
| `test_trainer_checkpoint_loads_into_a_fresh_model_and_changes_its_outputs` | base differs from trained; after loading, outputs bitwise equal | Laya venv |

The real-model driver's numbers (a direct run, 15:56Z, before the reward assertion was added): eval loss 0.6737 -> 0.6381,
step losses 0.6740, 0.6579, 0.6515; the loss is 0.434 at the target against 0.810, 0.638 and 2.375 elsewhere; 31 tensors in
a 105 MB checkpoint. Red-green: the tests were first run green; each mutant below is the red half.

## 6. Mutants (scratch copies only: a sparse local clone under the lane scratchpad; the shared tree was never mutated)

Every mutant restores the pristine file first, applies an exact replacement (refused unless its anchor is unique), purges
`__pycache__`, runs with `PYTHONDONTWRITEBYTECODE=1`, and restores after. Final runs 17:00:51Z (pure) and 16:23Z-16:33Z (Laya).

| Mutant | What it breaks | Red on (final run) | Reason in the failure |
|---|---|---|---|
| M1a drop the D-3 exclusion (brief) | both exclusion blocks in `collect` removed | `test_collect_masks_scrubs_and_excludes_on_a_fixture_repo`, `test_collect_excludes_every_heldout_row_on_the_real_tree` | the builder's own count check: `HeldOutError: ... excluded 0 of 1 held-out findings` |
| M1b drop the exclusion AND its count check | the production guard gone too | the same two | the tests' own oracle: `{'text_duplicates': 1} == {...: 0}` (the text guard caught it) and the real-tree identity check |
| M2a train the encoder in head mode (brief) | the encoder selected AND `detach_encoder=False` | `test_trainer_head_mode_leaves_every_encoder_parameter_bitwise_unchanged` | `'unchanged': {'encoder.': False, ...}` (eval loss fell to 0.460: the encoder trained) |
| M2b the encoder selected, the detach kept | one freeze mechanism removed | the same test | `assert ['encoder', ..., 'type_emb'] == ['head', 'scorer', 'type_emb']` |
| M3 the wrong loss sign (brief) | `return proper_reward(...)` | `test_trainer_three_steps_lower_the_loss_on_the_real_model` | `assert -0.7258351445198059 > -0.6737359762191772` (the true reward fell) |
| M4a skip the scrub, teacher (brief) | `scrubbed()` returns the text | `test_teacher_scrubs_every_string_before_it_leaves` | `b'QZJ8fakefakefake1234'` found in the request body |
| M4b skip the scrub, builder | the builder stores unscrubbed text | `test_collect_masks_scrubs_and_excludes_on_a_fixture_repo` | `'QZJ8fakefakefake1234'` found in the stored state |
| M5 drop the resume skip (brief) | done keys requested again | `test_teacher_resume_skips_done_keys` | `7 == 5` requests |
| M6 no rate limit | the limiter admits everything | `test_teacher_rate_limit_never_exceeds_60_per_minute` | `[] == [60.0]` (it never waited) |
| M7 no retry | 429/5xx not retried | `test_teacher_retries_429_and_5xx_with_backoff` | rc 3 instead of 0 |
| M8 the key not redacted | error text unredacted | `test_teacher_key_stays_out_of_argv_output_and_labels` | the FAKE key in stderr |
| M9 the ref read per call | `git show HEAD:path` | `test_collect_resolves_the_commit_once_even_when_the_ref_moves` | reads named `HEAD` |
| M10 no window fit | `fit` never cuts | `test_builder_is_deterministic_and_every_state_fits_the_window` | 32 truncated rows |
| M11 the ap state order | `{"chunk", "query"}` | `test_collect_masks_scrubs_and_excludes_on_a_fixture_repo` | the order assertion |

Both states, for the record (contract rule 5):
- **M11 first SURVIVED (16:12Z), then was killed (16:13Z).** The first run executed M9's STALE bytecode: M9's and M11's
  replacements are both length-preserving and were written in the same second, and CPython accepts a cached `.pyc` whose
  recorded source mtime (whole seconds) and size match. The cached `build_dataset` pyc recorded size 13,392 = the pristine
  size. After purging `__pycache__` and disabling bytecode writes, M11 goes red on the order assertion (added before the
  first run). Every earlier kill was re-run under the fixed runner with the same outcome.
- **M3 was first killed only by the separate sign assertion**: under the flipped sign the mutant's own "loss" also fell
  (-0.674 to -0.726), so "three steps lower the loss" is sign-blind. I added an independent check (laya's `proper_reward`
  computed in the driver, not through `train.loss_fn`, must rise); M3 now fails on it.
- **M2a and M2b first ERRORED (16:14Z-16:19Z)**: with the encoder counted as trained, the driver tried to save a ~1.6 GB
  checkpoint and hit a full disk. The driver now writes no checkpoint when head mode's invariants already failed; the
  re-runs (16:23Z-16:30Z) fail on the exact assertions above.

## 7. Static checks

- pyflakes on every new file (`scripts/laya_ft/*.py`, `tests/test_laya_ft.py`): rc 0, no output.
- `python3 scripts/no_laya_in_gates.py`: `no_laya_in_gates: 40 files scanned, clean`, rc 0 (the new files are not gate files).
- U+2028/U+2029 bytes (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`): 0 in every file written (the 7 above and this report).
- `python3 scripts/ap_screen.py` over the six scripts: 12 tells, each checked. AP-2 (4): the offline switches, set before
  laya/transformers are first imported (as the server does). AP-32 (3): each digest hashes exactly the form it is
  compared against (tested). AF-AP-175 (2): the `HEAD` default is resolved once (tested; M9). AF-AP-40 (2): a temp-file
  cleanup and a file enumeration, not presence-gated checks. AP-51 (1): the byte-identity claim is about JSONL files and is
  tested. `--tests` over the test file: 1 tell (AF-AP-80) on a check of the client's OUTPUT file, not of source text.

## 8. Deviations from the brief (flagged)

1. **Labels for the train smoke: 5 from codiv, 11 from the local Laya server** (section 4c). The brief asks for 16 items and
   allows 5 codiv requests. Rejected: a 5-item train smoke, or more codiv calls.
2. **The evaluator has extra runs** `v1_blocking` and `v1_full_blocking` for the trained D-6(b) question, with no committed
   base number. J2's shapes are unchanged. None was run live.
3. **The builder cuts long states to Laya's window**, so "whole" means whole up to 1,024 tokens: 32 ap rows (two entries).
   The finding texts were never cut.
4. **A second D-3 guard** (a v1 text equal to a held-out J2c text) beyond the brief's source identity; it counts separately,
   so the brief's "excluded = the samples' sizes" still holds exactly.
5. **The held-out incident identity is the masked heading, not the line number** (the brief says "incident heading line";
   the numbers drifted: 0 of 100 would match).
6. **Tests key on `S0_01_VENUE`** (the venue `scripts/test_summary.sh` exports): sandbox = the Laya venv is a declared input
   (absent = FAIL); unset (CI) and `pc` = a loud skip. The PC's Laya paths (`/home/rocco/venv-laya`; the timing probe used
   `~/laya-venv`) are not verified from here, so they are not declared.
7. **`save_checkpoint`'s free-space refusal** is an unrequested addition, made after the disk incident.
8. **The key reached `grep`'s argv once** (a leak check of the labels file at 16:38Z). It was never printed or logged, but
   the brief says never in argv. Later checks ran in process.

## 9. Adjacent observations (not fixed; outside the boundary)

- `laya.agent.Agent.__init__` calls `_fix_tokenizer_config`, which WRITES `tokenizer_config.json` inside the model
  directory when its class is missing or `extra_special_tokens` is a list. For this snapshot it is a no-op (verified: the
  blob is pristine); the trainer's `model_dir_unchanged` guard would catch a write.
- `laya.load(..., device="cuda")` falls back to CPU with a printed warning when CUDA is missing; `train.py` and
  `evaluate.py` refuse instead (a silent CPU fallback would run for hours).
- Only 10 (now 11) of the 91 (now 92) committed verify reports use the finding grammar decide-harvest and j2c.py read.
- The premise's first grep output was trimmed (D-P1).

## 10. Incidents in this lane (for the coordinator's incident log; the log is outside my boundary)

1. **I filled the sandbox disk (about 16:14Z to 16:21Z).** Mutants M2a and M2b made the test driver save the whole encoder
   (~1.6 GB) with about 1 GB free; the second attempt ended in `No space left on device`, and my restore `cp` of the
   scratch clone's `train.py` was truncated (restored and verified byte-equal since). The coordinator's 16:2xZ warning (325
   MB free) matches this window. Checked after: my smoke artifacts from before it verify (the dataset sha256; the
   evaluator outputs parse), the shared tree's files are byte-equal to their pristine copies, and the OpenJev run wrote its
   last outputs at 16:34:10Z, after the disk recovered. Other lanes' writes in that window may have failed. Fixes:
   `save_checkpoint` refuses before writing, the driver writes no oversized checkpoint, and every large output is deleted
   once its numbers are recorded (my scratch is 6.5 MB now).
2. **A new class for the registry (proposed): a mutation audit that runs STALE bytecode.** Mechanism: a runner rewrites a
   source file with a length-preserving change within the same second as the previous write; CPython validates a cached
   `.pyc` by source mtime (whole seconds) and size, so the mutant's run executes the previous version's bytecode. A mutant
   can then survive (M11 did), or be killed by another mutant's code, without its own code ever running. Signature: a
   mutation or restore loop that writes `.py` files without purging `__pycache__` or setting `PYTHONDONTWRITEBYTECODE=1`
   / `python -B`. Proven instance: FT1 M11, 2026-09-24 16:12Z (the pyc recorded the pristine size, 13,392). Fix: purge
   `__pycache__` and disable bytecode writes in every mutant run (done in the FT1 runner).
3. **The key once reached a local process's argv** (deviation 8).

## 11. NOT done (first-class)

- **The full labeling run** (about 1,772 codiv requests at HEAD, about 30 minutes at 60 per minute): the coordinator's.
- **The GPU training** (D-078): `--device cuda`, bf16 autocast and `--grad-checkpointing` never executed (CPU torch here).
- **`--mode full` never executed** (a CPU run needs about 7 GB of RAM and a 1.6 GB checkpoint on a disk with about 3 GB
  free); only its parameter selection is tested (it trains the encoder, never the act head).
- **The evaluator's `v1_full` and `ap` runs, and both blocking runs, never ran live.** Only `v1` ran, with and without a
  checkpoint. `ap` is about 1,600 forward passes (J2 took 1,951 s); `v1_full` about 700 longer ones.
- **No temperature refit** for a fine-tuned checkpoint: the evaluator serves it with the base config's temperatures, so its
  ECE reads through calibration fitted for the base model.
- **No PC-venue test run**, and no bridge call (forbidden); the PC paths are unverified.
- **The finding source is small**: 62 (now 86) trainable findings, because only 10 (now 11) reports use the grammar. A
  wider extractor is a separate design decision.
- **No gold-label training mode**: the targets are the teacher's; the verifier's class is never stored (AF-AP-189).
- **No commit, no push** (the brief). The registry row in section 10 is not written (the log is outside the boundary).

## 12. Self-attack: the three most likely ways this is wrong

1. **The dataset leaks a held-out row by another identity.** Ruled out as far as the tree allows: source identity
   (100 of 100 each), a text-identity guard, the test's own reading of the samples on the real tree, planted rows refused at
   `check_no_heldout` and at `load_dataset`, and mutants M1a/M1b red. Residual: a held-out finding rewritten under a new id
   in a new report, with different text, would not be caught.
2. **The trainer trains something other than the model J2 measured**, or with a wrong objective. Ruled out: the evaluator's
   in-process base model reproduces all 100 committed J2 predictions of both methods; the items come from Laya's own
   `build_sequence` and `collate_items`; the loss is laya's `proper_reward`, negated, and the test proves it minimal at the
   target and the true reward rising (M3 red); head mode's encoder and act head are bitwise unchanged (M2a/M2b red).
   Residual: the CUDA/bf16 path is unexercised.
3. **The teacher client sends something it should not** (a secret, the key), or stores a label for the wrong text. Ruled out:
   every string scrubbed (M4a red); the key only in the Authorization header, redacted from every message (M8 red); each
   label records the digests of what was SENT, and a mismatch is refused at the join. Live: 16 real requests (5 codiv, 11
   local), `scrub_changed=0`, and 0 key bytes in the labels file.

Evidence tiers. **Verified** (this session, by command): everything in sections 1, 2, 4, 5, 6, 7. **Inferred**: that
other lanes' writes may have failed during the disk-full window (not observed); that a full-mode GPU run fits a 3090
(from D-078's timing and the parameter counts). **Assumed**: that the PC snapshot is byte-identical to the sandbox's (same
revision id; not hashed from here).
