# VERIFY-FT1 report: the independent verify of the Laya fine-tune tooling (task #233)

Lane: VERIFY-FT1 (sandbox adversarial-verifier, served model: claude-opus-5-5 per the session header; no model switch seen).
Brief: `tasks/briefs/jev-laya/VERIFY-FT1-brief.md`. Contract: `tasks/briefs/jev-laya/FT1-brief.md` (D-1..D-8 + evidence demands).
Lane report under review: `tasks/briefs/jev-laya/FT1-report.md`.
Status: FINAL (written incrementally, 2026-09-24 17:14:57Z to 18:22:39Z, `date -u`). Gate recommendation: **MERGE-READY-WITH-FOLLOWUPS** (section 6).

## 1. Premise re-measure (first action)

Started 2026-09-24 17:14:57 UTC (`date -u`). Local HEAD `eb256f49c0ee` ("VERIFY-FT1 brief: ...", 17:14:31Z).

```
$ for f in ...; do echo "$(git rev-parse --short=12 HEAD:$f) $f"; done
9266ba11b501 scripts/laya_ft/__init__.py
63f15afdb090 scripts/laya_ft/common.py
9ecf61065267 scripts/laya_ft/build_dataset.py
0af5dea65676 scripts/laya_ft/teacher_label.py
8d03bef2a83b scripts/laya_ft/train.py
96b0a2024012 scripts/laya_ft/evaluate.py
20409b3606f5 tests/test_laya_ft.py
$ git hash-object <each file>   (working tree): the same seven 12-char prefixes; git status clean for these paths
$ bash scripts/pc_suite.sh set-id -- tests/test_laya_ft.py
1 files set=8b147318aa48
```

All seven blob hashes MATCH (HEAD and working tree). set-id MATCHES. Test counts: see below.

Environment: `df -h /` 17:15Z: 252G size, 3.4G available (91%). 4 CPUs, 15 GiB RAM. Laya server listening 127.0.0.1:47411
(pid 30467; never touched).

```
$ bash scripts/test_summary.sh tests/test_laya_ft.py --basetemp=/tmp/vft1/bt   (17:15:26Z -> 17:21:59Z, PYTHONDONTWRITEBYTECODE=1)
......................                                                   [100%]
22 passed in 392.05s (0:06:32)
pytest-exit: 0
pytest-summary: 22 passed in 392.05s (0:06:32)
$ env -u S0_01_VENUE /root/venv-agent-factory/bin/python -m pytest tests/test_laya_ft.py -q -rs --basetemp=/tmp/vft1/bt2 -p no:cacheprovider
18 passed, 4 skipped in 4.60s     (4 LOUD SKIPs at lines 642, 739, 746, 753: "the Laya venv and snapshot are declared inputs of the sandbox venue only")
```

PREMISE: MATCH on all nine measured values (7 hashes, set id, both counts). Wall time 392 s vs the coordinator's 124 s: a
contended box (other lanes live), not a count change. Proceeding.

Note: HEAD moved during the verify (eb256f49 -> 28d5fcb5, unrelated coordinator commits); the seven files are unchanged at
28d5fcb5 (same seven blob ids, re-read 17:2xZ). My builds pin `--commit 28d5fcb5acf386e5efdd5c671f054b3ff35c63e9`.
The session scratchpad is SHARED with the coordinator (its live labeling run writes `laya-ft-data/`); my files live in
`<scratchpad>/vft1/`, and I only READ the coordinator's and the lane's files.

## 2. Reproduced through the real path

### 2a. The builder on the real tree (D-2, D-3, D-4, D-6)

`HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --commit 28d5fcb5... --out <scratch>/vft1/ds`
rc=0, 14.4 s wall:

```
"counts": {"cut_to_window": {"ap.violates_row": 32, "v1.blocking": 0, "v1.finding_class": 0}, "merged_duplicates": 0,
           "rows": {"ap.violates_row": 1616, "v1.blocking": 86, "v1.finding_class": 86}, "rows_total": 1788,
           "trainable_entries": 101, "trainable_findings": 86}
"dataset": {"bytes": 4077876, "sha256": "d7cd9b49abac267bb9b5290641ea353180a9a61047ce6c590809520b085cea1c"}
"heldout": {"incident_entries": {"excluded": 100, "identities": 100}, "text_duplicates_excluded": 0,
            "verify_findings": {"excluded": 100, "identities": 100}}
"sources": {"incident_entries": 201, "registry_rows": 193, "reports_with_findings": 11, "verify_findings": 186, "verify_reports": 93}
```

Determinism, independently: my build at 28d5fcb5 and the coordinator's build at eb256f49 (`laya-ft-data/ds`, 17:15Z) are
byte-identical (`sha256sum`: both `d7cd9b49...`), and the two manifests agree on code, model and counts.

Read-only analysis of that dataset (`<scratch>/vft1/analyze_ds.py`, pasted):

```
exact class words left in v1 states: 0 []
class-like words in v1 states: {'block': 9, 'blocks': 5, 'blocked': 4}
v1 items with a class-like word: 12 of 86
finding id prefixes: {'(table)': 75, 'V': 4, 'V5': 4, 'F': 3}
AF-AP-like ids left in ap queries: 7 [('AP-43', 2), ('AP-24', 2), ('AP-1', 1), ('AP-3', 1), ('AP-32', 1)]
AF-AP-like ids in ap chunks (J2 kept chunks unmasked): 6
AF-AP-? followed by /digit or , digit in queries: 1          (log line 356: "(AF-AP-16/17)" -> "(AF-AP-?/17)")
rows whose state a second scrub changes: 0
questions a scrub changes: 0
trainable v1 items with a held-out J2c text: best full SequenceMatcher ratio 0.398 (id-normalized, whitespace-collapsed)
trainable v1 items whose title equals a held-out title: 0
held-out incident headings found inside trainable ap queries: 0 []
J2c held-out rows that are table title cells: 84 of 100; trainable: 75 of 86 (title cell only, 66..499 chars, median 191)
reports with BOTH held-out and trainable findings: 9 of the 11 trainable reports
```

The bare `AP-24/AP-43/AP-1/AP-3/AP-32` ids are the source repo's inherited AP registry (another namespace, not an AF-AP
candidate). `no_laya_in_gates.py`: `40 files scanned, clean`, rc 0; no file outside the seven references `laya_ft`; CI
(`stage0-ci.yml:46`, `python -m pytest tests/ -q`) collects `tests/test_laya_ft.py` and runs its 18 non-Laya tests (the
4 Laya tests skip loudly: no venue), so no Laya output reaches a gate.

### 2b. The teacher client (D-5), against local stand-ins only (never codiv.ai)

Static: no `subprocess`, `os.system`, `popen` or `exec*` in `teacher_label.py`, `common.py`, `transcript_export.py`,
`ap_probe.py`, `v1_probe.py`; `j2c.py` uses `subprocess` only inside `cmd_sample`; decide-harvest runs nothing at import.
So the TOOL never places the key in any argv (the lane's one argv exposure was its own `grep` command, not the tool).

The coordinator's LIVE labeling run (read only, `<scratch>/laya-ft-data/labels.jsonl`, 17:3xZ):
```
label stats {'records': 957, 'torn': 0, 'duplicates': 0}
teachers Counter({'openjev-0.1 @ api.codiv.ai': 957})
stale 0 orphan 0
attempts Counter({1: 956, 2: 1})
joined 957 by question Counter({'ap.violates_row': 785, 'v1.finding_class': 86, 'v1.blocking': 86})
v1.finding_class n 86 min 0.3572 median 0.8078 max 0.9989      (max probability)
v1.blocking n 86 min 0.0006 median 0.0401 max 0.9973           (p(true))
ap.violates_row n 785 min 0.0019 median 0.7338 max 0.9993      (p(true))
labels file mentions 'Bearer': 0 'TYPESAFE': 0 'Authorization': 0
```

Hostile stand-ins through the REAL CLI (`<scratch>/vft1/hostile_teacher.py`: `teacher_label.py` as a subprocess, a FAKE
33-char key file, `--limit 2`):
```
== h1_200_echo_in_answer: rc=0 requests=2 stored_lines=2 usage_line=True
   key (full, any 12-char piece) in: {'argv': (False, False), 'stdout': (False, False), 'stderr': (False, False), 'labels': (True, True)}
== h2_401_echo_split_at_300: rc=3 ... stderr tail: 'teacher_label: refused: HTTP 401: <opaque-redacted>'   (padding joined the key: redacted)
== h2b_401_echo_split_standalone: rc=3 requests=1 stored_lines=0 usage_line=True
   key (full, any 12-char piece) in: {'argv': (False, False), 'stdout': (False, False), 'stderr': (False, True), 'labels': (False, False)}
== h3_200_huge_int: rc=1 requests=1 stored_lines=0 usage_line=False
   stderr tail: 'OverflowError: int too large to convert to float'
== h4_200_answers_list: rc=4 ... 'malformed answer, not stored: the response has no answer for v1.blocking'
== h5_200_choice_not_argmax: rc=4 requests=2 stored_lines=1 ... "choice 'BLOCKER' is not the most probable option"
== h6_200_noul_as_choice: rc=4 ... 'probability None is not a finite number in [0, 1]'
== h7_200_html: rc=4 ... 'malformed answer, not stored: the response is not JSON'
```
Limiter and retry, in process on a fake clock (`<scratch>/vft1/retry_rate.py`; `post` is the network double):
```
== every_other_429_x130rows: rc=0 posts=260 stored=130 max-in-[t,t+60)=40 max-in-[t,t+60]=41 min-gap=1.0
== retry_after_nan / -5 / HTTP-date / 0.25: sleeps [2.0] (the default backoff)
== retry_after_1e9 / inf: sleeps [120.0] (the cap)
== conn_reset: rc=3 posts=7 sleeps [2.0, 4.0, 8.0, 16.0, 32.0, 60.0]
== lowercase_retry_after: sleeps [7.0]
```

Resume across a changed dataset (`<scratch>/vft1/resume_changed.py`, in process, fake clock, `post` = network double):
```
A: 4 asked (2 findings x 2 questions)
B: rc 0 asked 4 [re-worded finding x2, new finding x2]; B join: 6 of 6 rows; labels on file 8   (unchanged finding reused)
C (question re-worded in code): rc 0 asked 0 (the re-worded question's keys count as done)  usage: ... skipped_done=8
C join: LabelError: 3 stale label(s) name a row whose state or question changed: [...]
```

### 2c. AF-AP-193: where each cut and each scrub happens

Order, read from source and reproduced: builder `scrub(_mask(block))` then `Fitter.fit` cut (`build_dataset.py:87-91` then
`:186`), `ap` query `scrub(AP_ID.sub(...))` then cut (`:109`, `:186`), chunk `scrub(registry row)` (`:111`); the teacher
scrubs AGAIN after the cut (`teacher_label.py:173`), and each label records the digest of the state AS SENT
(`teacher_label.py:181`), which `join_labels` (`common.py:292`) compares with the row's. Measured:
- real dataset: `rows whose state a second scrub changes: 0` of 1,788 (32 of them cut to the window);
- 16 crafted cut rows (one incident entry, committed in my scratch clone only, built by the real builder with
  `--repo <clone>`): 0 changed; cut ends `token=<red`, `token=<redacted>`, `token=`;
- 400 synthetic cuts through the real `Fitter.fit` (chunks scrubbed as the builder does): `cuts a second scrub changes: 0`;
  cut endings `{'token=<': 67, 'token=': 67, 'cted> ': 67, 'token=<red': 66, 'token=<redacted>': 45, 'd> tok': 44,
  'token': 23, 'token=<redact': 21}`. The hazardous prefixes are 8 or 9 characters into the marker (`<redacte`,
  `<redacted`, the scrub's 8-character floor); the Laya tokenizer makes `token=<redacted` 5 tokens and `token=<redacte` 6
  (`['token','=','<','red','acted','>']`), and the character binary search never selected them.
- held-out evaluation states the scrub would change (the student trains scrubbed, is evaluated unscrubbed): J2 v1 1 of
  100, J2c 2 of 100, AP 1 of 100.
So the teacher labels the text the student trains on; the evaluator's inputs differ by the scrub on 1-2 rows per sample.
One AF-AP-193-class order DOES exist in FT1, in the error path: `ask()` cuts the response body to 300 bytes
(`teacher_label.py:149`) and only then redacts it (`safe()`, `:128`), see finding F-3.

### 2d. The trainer through its real entry point (`train.py run()`, which no test calls)

All runs: `/root/venv-laya-probe/bin/python scripts/laya_ft/train.py --dataset <scratch>/vft1/ds --labels <snapshot of the
coordinator's live codiv labels, 1,183 lines> --mode head --device cpu --batch-size 4 --epochs 1`, checkpoints in
`/dev/shm` (RAM), each deleted once used (t1 after the loader probe below).
```
t1 --limit 8 --threads 2 --seed 1234: epoch 1/1 loss 0.947316 (2 steps, 45 s)  checkpoint sha256 6821bac205cc17fc...  guards all true
t2 (same, in parallel):               epoch 1/1 loss 0.947316 (2 steps, 45 s)  checkpoint sha256 6821bac205cc17fc...  guards all true
t5 --seed 1235 (negative control):    epoch 1/1 loss 0.926193 (2 steps, 40 s)  checkpoint sha256 daaeb89e49a043b2...
t3 --out on a REAL 40 MB tmpfs:        epoch 1/1 loss 0.947316 (2 steps, 46 s) ; rc=64
    train: refused: Refusal: the checkpoint needs 164 MiB and /tmp/vft1/small/t3 has 40 MiB free   (directory left EMPTY)
t4 --lr inf, 2 steps:                  rc=1  FloatingPointError: non-finite loss nan: the step is refused  (raw traceback)
t6 --lr inf, --limit 4 (ONE step), --eval-loss:  rc=0
    "eval_loss_after": NaN, "eval_loss_before": 0.807124137878418, guards {act_head_unchanged, encoder_unchanged,
    model_dir_unchanged: true}; checkpoint: tensors 31, non-finite tensors 31
```
`--limit 8` took v1 rows only (`by_question: ap.violates_row 0`): dataset order puts every v1 row first.

The loss over the right mask (D-1), checked without the model: on a mixed batch (one 6-option choice, two 2-option nouls
padded to 6, logits masked to -1e4 as `DecisionModel.forward` does at `laya/common.py:117`), `train.loss_fn` against an
independent per-item `proper_reward` over each item's real options only:
```
loss_fn 5.181834698  independent 5.181834539  |diff| 1.59e-07
  at target  loss 0.230076
  uniform    loss 0.339594
  wrong peak loss 4.051609
```

`load_checkpoint` against hostile state dicts (the real loader on the real model):
```
head ckpt t1 (real)              loaded: (31, ['head', 'scorer', 'type_emb'])
full-like (an encoder tensor)    loaded: (1, ['encoder'])
act head key                     Refusal: ... 2 tensors, 1 not loadable: ['act_head.0.weight']
wrong shape                      Refusal: ... 1 tensors, 1 not loadable: ['head.layers.0.self_attn.in_proj_weight']
empty                            Refusal: ... 0 tensors, 0 not loadable: []
a buffer key (temperature)       Refusal: ... 1 tensors, 1 not loadable: ['temperature']
an unknown key                   Refusal: ... 1 tensors, 1 not loadable: ['head.bogus']
```
HF cache: `find /root/hf-laya-probe -newermt '2026-09-24 17:14:00' | wc -l` = 0 after every train and eval run above.

### 2e. The evaluator (D-8), through `evaluate.py main()`

```
eval-base: evaluate.py --only v1 --threads 2 (no checkpoint), 17:41:57Z -> 17:52Z
  KC-J3 v1 jev_choice: accuracy 0.2100 vs max(majority 0.4300, heuristic 0.4100) = 0.4300 -> REJECTED (at or under)
  KC-J3 v1 jev_noul: accuracy 0.0300 vs max(majority 0.4300, heuristic 0.4100) = 0.4300 -> REJECTED (at or under)
  "agreement_with_committed_base": {"jev_choice": "100/100", "jev_noul": "100/100"}, "differences_from_committed_base": [], "ece": 0.0481
  POSITIVE CONTROL (no checkpoint): PASS
eval-nan: evaluate.py --only v1 --checkpoint <t6: the 31/31 non-finite checkpoint> --threads 2
  jev_choice: accuracy 0.07, blocking_split 0.09, per_class_recall BLOCKER "7/7"   (every prediction 'BLOCKER')
  jev_noul:   accuracy 0.07, blocking_split 0.09, per_class_recall BLOCKER "7/7"   (every prediction 'BLOCKER')
  ece 0.0, positive_control None (not evaluated with a checkpoint), no traceback in the log
```
```
eval-full: evaluate.py --only v1_full --threads 4 (no checkpoint), 18:02:49Z -> 18:21Z (NEVER run by the lane)
  KC-J3 v1_full jev_choice: accuracy 0.1700 vs max(majority 0.4300, heuristic 0.3200) = 0.4300 -> REJECTED (at or under)
  KC-J3 v1_full jev_noul: accuracy 0.1000 vs max(majority 0.4300, heuristic 0.3200) = 0.4300 -> REJECTED (at or under)
  positive_control PASS agreement {'jev_choice': '100/100', 'jev_noul': '100/100'} diffs [] ece 0.1181 seconds 1064.3
  committed jev_choice 0.17 BLOCKER 2/7, jev_noul 0.1
```
The lane's positive control (its smoke 4e) is reproduced exactly, and the J2c (`v1_full`) positive control, which no one
had run, passes too. KC-J3 compares against max(majority, heuristic) for v1,
the council's definition (`COUNCIL-VERDICT-JEV-LAYA-v1.md:48`, "post-temperature argmax accuracy ... <= max(majority-class
baseline, regex/heuristic baseline)"); for ap it uses max(majority@1, lexical@1), the lexical order standing in for the
heuristic. With all-NaN noul scores the committed ap sort key (`ap_probe.py:117`) returns the lexical order unchanged
(shown on the key alone: `jev == lexical order: True`), so a NaN checkpoint would read ap top-1 = lexical top-1.

### 2f. D-3 guard reach, through the real `collect()` on a fixture (`<scratch>/vft1/d3_reach.py`)

One held-out finding and one held-out incident, then copies of each under another identity:
```
excluded: {'verify_findings': 1, 'incident_entries': 1, 'text_duplicates': 2}
  moved verbatim (same id)               caught (not emitted)
  moved, renumbered F-2 -> F-7           LEAKS (emitted for training)
  moved, re-classed INFO -> FOLLOW-UP    caught (not emitted)
  moved, one word re-worded              LEAKS (emitted for training)
  moved, a table row                     LEAKS (emitted for training)
  moved, trailing space added            LEAKS (emitted for training)
  incident copied under a new heading    LEAKS (emitted)
```
On the REAL tree none of these shapes occurs: trainable findings vs held-out J2c texts, best full ratio 0.398 (id and
whitespace normalized); trainable incident bodies vs the 100 held-out entry bodies (found in the log by masked heading),
`trainable entries with a held-out body at ratio > 0.7: 0` (best 0.33).

Also verified: `train.py --device cuda` -> `Refusal: --device cuda but CUDA is unavailable (no silent CPU fallback)` rc 64;
`train.py --out /root/hf-laya-probe/hub/vft1-out` -> `Refusal: --out ... is inside the Hugging Face cache` rc 64 (nothing
created); `evaluate.py --device cuda` -> rc 64. pyflakes over the seven files: rc 0, no output. U+2028/U+2029 bytes: 0 in
each of the seven files and in the lane's report.

## 3. Mutation audit (fresh `cp -a` of a pinned sparse clone per mutant; `PYTHONDONTWRITEBYTECODE=1` and `python -B`)

Clone: `git clone --shared` of this repo, sparse (`scripts/ src/ tests/test_laya_ft.py tests/conftest.py docs/research/findings/
docs/INCIDENT-LOG.md pyproject.toml`), detached at 28d5fcb5, the seven blob ids re-verified; no `__pycache__` before or after
any run (asserted by the runner). The first control run ERRORED (`No module named 'agent_factory'`: decide-harvest imports
`src/`), so the clone was widened before any verdict counted. Non-Laya mutants run without a venue (18 tests), Laya mutants
with `S0_01_VENUE=sandbox -k trainer` (3 tests). Runner: `<scratch>/vft1/mutants.py`.

| Mutant | What it breaks | Result |
|---|---|---|
| CONTROL (no venue) | nothing | `18 passed, 4 skipped` |
| CONTROL (Laya, -k trainer) | nothing | `3 passed, 19 deselected in 155.43s` |
| M1a (lane) | both D-3 exclusion blocks in `collect` removed | KILLED: 3 red (collect x2 and the D-4 test), `HeldOutError: ... excluded 0 of 1` |
| M3 (lane) | `return proper_reward(...)` (sign flipped) | KILLED: `test_trainer_three_steps_lower_the_loss...` (the reward-rise assertion; the flipped "loss" fell) |
| M4a (lane) | teacher `scrubbed()` returns strings raw | KILLED: `b'QZJ8fakefakefake1234' not in b'...'` |
| M5 (lane) | resume skip dropped | KILLED: `7 == 5` |
| M8 (lane) | key not replaced in `safe()` | KILLED: the FAKE key in stderr |
| M9 (lane) | `git show <rev>:path` per call | KILLED: reads named `HEAD` |
| M11 (lane) | ap state `{"chunk", "query"}` | KILLED: the order assertion |
| N1 | `collect`'s text-duplicate skip removed | SURVIVED (18 passed) |
| N2 | `check_no_heldout`'s text guard removed | KILLED: `DID NOT RAISE HeldOutLeak` |
| N3 | `collect`'s D-3 count check removed (exclusions kept) | SURVIVED (18 passed) |
| N4 | `load_dataset` skips the held-out check | KILLED: `DID NOT RAISE HeldOutLeak` |
| N5 | `join_labels` ignores `sent_state_sha` | KILLED: 2 red |
| N6 | the positive control never records a difference | SURVIVED (18 passed) |
| N10 | limiter without the 1 s gap | KILLED |
| N11 | label records the row's digest, not the sent one | KILLED |
| N12 | `build()`'s second D-3 check removed | SURVIVED (18 passed) |
| N13 | no class mask | KILLED: 2 red |
| N14 | a choice not at the argmax accepted | KILLED: `DID NOT RAISE LabelError` |
| N15 | the samples' uniqueness check made one-sided | SURVIVED (pinned samples: no reachable effect) |
| N16 | 429 not retried | KILLED: `3 == 0` |
| N9 | `train_step`'s non-finite loss check removed | SURVIVED (`3 passed`) |
| N17 | `forward()` never detaches the encoder | SURVIVED: EQUIVALENT (head mode's frozen `requires_grad` alone keeps the encoder) |
| N7 | `run()` selects `"full"` in head mode | SURVIVED (`3 passed`): no test calls `train.run()`/`main()` or `evaluate.main()` (grep rc 1) |

All seven lane mutants I re-ran reproduce the lane's kills (M1a now reddens three tests, not two). My new mutants: 16 run,
8 killed (N2, N4, N5, N10, N11, N13, N14, N16); of the 8 survivors, N17 is equivalent and N15 unreachable under the sha256
pin, so 8 of 14 non-equivalent reachable mutants are killed and 6 survive (N1, N3, N6, N7, N9, N12).

## 4. Finding inventory (no severity filter)

Evidence levels: VERIFIED = reproduced by a command in this session; STATIC = read from source only.

**F-1 FOLLOW-UP (top priority; fix before the GPU window) - a non-finite checkpoint is saved with rc 0, and the evaluator
scores it as a perfect blocker detector.** VERIFIED. `train_step` checks the loss BEFORE each step (`train.py:110`); nothing
checks the weights the LAST step produced, `eval_loss_after`, or the tensors `save_checkpoint` writes. `--lr` accepts `inf`
(also a negative `--max-grad-norm`, any `--weight-decay`: the parameter domains are not validated). Repro (sec. 2d, t6):
`train.py ... --limit 4 --batch-size 4 --lr inf --eval-loss` -> rc 0, guards all true, `"eval_loss_after": NaN` (the
manifest carries a bare `NaN`), 31 of 31 checkpoint tensors non-finite. `load_checkpoint` (`train.py:167`) accepts it, and
`evaluate.py --only v1 --checkpoint <it>` reports every prediction `BLOCKER`, BLOCKER recall 7/7 on both methods and
`ece 0.0` (NaN confidences fall in no bin), no error (sec. 2e). On ap the committed sort key returns the lexical order for
NaN scores (shown on the key only), so ap top-1 would read the lexical 0.59. Contract: none of D-7/D-8 names finiteness;
the repository invariant (CLAUDE.md #1, tactic 1: guards check the FINAL value, NaN is a fail-open wormhole) applies to the
trainer's own guard. Canonical path: yes, both real CLIs. Material effect: yes, IF a non-finite checkpoint exists; my
trigger is `--lr inf` (operator misuse); a last-step divergence with the production settings (lr 1e-4 head, 2e-5 full, bf16)
was not demonstrated. Discriminator: the t6 command (rc 0 now; rc 5 or 64 after a fix). In boundary. NOT a blocker: it fails
the predicate's material-effect clause (hypothetical misuse, defence in depth). Fix: `torch.isfinite` over every trained
tensor before `save_checkpoint` and over `eval_loss_after` (rc 5); `load_checkpoint` refuses non-finite tensors; the
evaluator refuses a non-finite served probability; `--lr`, `--weight-decay`, `--max-grad-norm` must be finite and in range;
catch `FloatingPointError` into a clean refusal.

**F-2 FOLLOW-UP - a 200 answer that echoes the key is stored verbatim in the labels file.** VERIFIED (h1). `label_row`
stores the raw `answer` object and the response's `model` field (`teacher_label.py:182`); neither passes the key
replacement that error text gets. Contract: D-5 ("never printed, never logged"); the VERIFY brief lists "a stored label".
Canonical: the real CLI against a local stand-in. Material: only if the teacher echoes the key in a 200 body; the live codiv
labels hold no `Bearer`, `Authorization` or `TYPESAFE` string (957 records, sec. 2b). Discriminator: h1 (key present in
`labels.jsonl`). In boundary. Fix: store only the validated distribution plus whitelisted scalar fields, or apply the key
replacement to the serialized record before the write.

**F-3 FOLLOW-UP - cut, then redact: a key echoed across the 300-byte cut prints its first 20 characters.** VERIFIED (h2b).
`ask()` keeps `raw[:300]` (`teacher_label.py:149`), and only then `safe()` replaces the key (`:128`); a key split by the cut
no longer matches, and a 20-character piece is below the scrubber's 40-character opaque floor. This is AF-AP-193's class
(a cut taken before a transform) in FT1's error path. Material: needs a server that echoes the key after byte ~280 of an
error body; defence in depth. Fix: `safe()` the whole body read (600 bytes), then cut.

**F-4 FOLLOW-UP - two uncaught exceptions end a run with a raw traceback, rc 1 and no usage line.** VERIFIED. A JSON
integer too large for a float (`1` followed by 400 zeros) makes `math.isfinite` raise `OverflowError` (`common.py:248`;
h3: rc 1, `usage_line=False`), although the docstring promises the usage totals "also after a failure"; the same check
guards `join_labels` (`common.py:300`). `train.py`'s `FloatingPointError` (t4) is not caught by `main()` either; neither
docstring lists rc 1. Nothing wrong is stored. Fix: treat any non-float-convertible value as malformed (rc 4); catch the
trainer's non-finite refusal into rc 5 or 64.

**F-5 FOLLOW-UP - the resume key does not cover the question text, and a stale label blocks all training with no in-place
recovery.** VERIFIED (sec. 2b, resume C). After a question is re-worded in code, the client asks nothing (`skipped_done=8`,
rc 0) and `join_labels` refuses the whole file (`3 stale label(s)`). `read_labels` keeps the FIRST record per key
(`common.py:276`), so appending a fresh label cannot replace a stale one; the same holds for any label whose sent digest
differs (`scrub_changed>0`, 0 on the live data). The key is exactly D-5's "(item id, question id)", so this is a contract
property. Fail-closed. Fix: `schedule` treats a label whose `question_sha` or `sent_state_sha` differs from its row as not
done, and `read_labels` keeps the last well-formed record (or key by question sha).

**F-6 FOLLOW-UP - the free-space refusal runs after training, so a full disk discards the trained weights.** VERIFIED (t3,
a real 40 MB tmpfs): rc 64, `the checkpoint needs 164 MiB and ... has 40 MiB free`, the directory left empty, so the claim
"refused before any byte is written" holds; but the 2 training steps ran first and were lost. On the GPU window a full-mode
run (a 1.6 GB checkpoint) would lose the whole run. Fix: check free space right after `select_trainable` (the size is known
then) and again at save.

**F-7 FOLLOW-UP - no test exercises the CLI entry points.** VERIFIED. `tests/test_laya_ft.py` never calls `train.run()`,
`train.main()` or `evaluate.main()` (grep rc 1); mutants N7 (`run()` selects full mode), N6 (the positive control never
records a difference) and N9 (the non-finite loss check removed) survive. The run-level guards (rc 5), refusals (rc 64),
data order and the positive control's FAIL wiring (rc 2) are covered only by live smokes (the lane's and mine). Evidence
demand 2's "`--mode head`" is met through the pieces (`select_trainable(model, "head")`), not the flag. Fix: a CPU CLI test
(`train.py --mode head --limit 4`, ~45 s here) asserting rc, guards and trained prefixes, plus a wiring test for
`evaluate.main()`'s FAIL path.

**F-8 FOLLOW-UP - the D-3 tripwires are untested, and the text guard's reach is exact match.** VERIFIED (sec. 3, sec. 2f).
N3 (the count check removed), N1 (collect's text-duplicate skip removed) and N12 (build's second check removed) survive: no
fixture has a held-out identity missing from the tree or a held-out text under another id. The text guard compares the
same `_mask` normalization the J2c sample holds (answer to the brief: yes, same normalization), with no whitespace or id
normalization: a renumbered, re-worded, table-row or trailing-space copy leaks, and incidents have no text guard at all.
The count check is a real check, not equal by construction (M1a: `excluded 0 of 1`). Real tree: clean (sec. 2a, 2f). Fix:
fixtures for a renamed held-out source (expect `HeldOutError`) and a copied text under a new id; normalize whitespace and
drop the finding id before the text comparison; a body-text guard for incidents.

**F-9 FOLLOW-UP - the positive control gates on aggregate numbers only.** VERIFIED + STATIC. It IS a real recomputation
(the in-process model through the committed scorer, sec. 2e: `100/100` agreement, PASS), not a reading of committed
numbers. But `failures` holds only `compare()`'s aggregate differences (`evaluate.py:179`); per-row agreement, ECE and ap's
committed per-sample `jev_scores` are printed, not gated. The lane's own smoke 4f (a trained checkpoint: "every J2 v1 number
and all 100 predictions per method unchanged, ECE 0.0481 -> 0.0325") shows the control cannot tell the base model from a
lightly trained one, and a harness error that moves probabilities but no argmax (a wrong temperature) would PASS. It meets
D-8's letter. Fix: gate on per-row agreement, ap per-sample scores (4 decimals) and a pinned base ECE.

**F-10 INFO - mask residue.** VERIFIED. Exact class words left: 0. Class-like words in 12 of 86 trainable findings
(`block` 9, `blocks` 5, `blocked` 4; e.g. "A broken registration BLOCKS.", VERIFY-COORD-0924 F-L1-2) and in 11 of 100 held-out
J2c states; `(AF-AP-16/17)` keeps `17` (log line 356); 6 ap chunks name OTHER AF-AP rows (J2 kept chunks unmasked too;
a chunk never names its own id); 7 queries carry the inherited source-repo ids `AP-1/3/24/32/43` (another namespace).
This is exactly j2c.py's and ap_probe.py's masking, which D-2 requires; the eval set has the same residue. The builder
never reads the v1 ledger; `_blocks`' class is discarded (`build_dataset.py:81`); rows carry only item/question ids,
digests, options, question, state, sources (and `cut`); the trainer and teacher read only `state` and `question`. No
`disposition` word, class field or label-derived field reaches an input (AF-AP-189 holds).

**F-11 INFO - most "whole findings" are table title cells.** VERIFIED. 75 of 86 trainable findings (84 of 100 held-out
J2c rows) are a table row's title cell (66..499 chars, median 191), as D-2 specifies.

**F-12 INFO - a within-report split.** VERIFIED. 9 of the 11 trainable reports also supply held-out rows.

**F-13 INFO - ap trains on whole entries and is evaluated on headings.** STATIC + VERIFIED. The builder's query and its
lexical ranking use the whole entry (D-2); J2's ap sample, which D-8 evaluates, uses the heading.

**F-14 INFO - the live teacher's ap targets lean to "yes".** VERIFIED (read only). Over 785 live ap labels, median
p(true) 0.7338 across each entry's lexical 16, where J2's AP labels name one or two rows per incident; v1.blocking median
p(true) 0.0401. A data-quality fact for the GPU window, not a tooling defect.

**F-15 INFO - the student trains on scrubbed text and is evaluated on raw text.** VERIFIED: 1 of 100 (J2 v1), 2 of 100
(J2c), 1 of 100 (AP) held-out states change under the scrub.

**F-16 INFO - limiter edges.** VERIFIED. At most 60 admissions in any half-open 60 s window, 61 in a closed one (t=0..60:
the lane's passing test asserts the 61st admission at exactly t=60.0; my 130-row run with backoff peaked at 40/41);
retries count; NaN, negative, HTTP-date and huge Retry-After values fall back or cap (2 s default, 120 s cap).

**F-17 INFO - a key in the base URL's userinfo would leak.** STATIC. `client.endpoint` is the URL's netloc, printed in the
usage line and stored in every label; a misconfiguration only.

**F-18 INFO - determinism.** VERIFIED on CPU: two runs, one seed, bitwise-equal checkpoints (`6821bac2...`); another seed
differs (`daaeb89e...`). CUDA runs set no deterministic algorithms under bf16 autocast, so the GPU run is seeded, not
necessarily bitwise reproducible; D-7 asks for a fixed seed, which holds.

**F-19 INFO - the tool never places the key in argv.** STATIC (no process spawn in the import chain) + VERIFIED (the key
absent from every subprocess argv in h1..h7). The lane's one exposure was its own `grep`.

**F-20 INFO - `--limit N` takes v1 rows only for small N** (dataset order puts every v1 row first); by design.

**F-21 INFO - the manifest's revision is null off the HF layout.** STATIC. `model_fingerprint` reads the revision from a
`snapshots/<rev>/` parent; a PC path outside that layout records `null` (the safetensors sha256 still pins the weights).

**F-22 INFO - AF-AP-193 in the builder-to-teacher chain: not reachable here.** VERIFIED (sec. 2c): the builder scrubs before
it cuts; the teacher's second scrub changed 0 of 1,788 real, 16 crafted and 400 synthetic cut states. If it ever fires, the
sent-digest check makes it fail closed (and F-5 applies).

**F-23 INFO - reproduction of the lane's claims.** VERIFIED: the premise; determinism across commits; the positive control
(v1); M1a, M3, M4a, M5, M8, M9, M11 kills; pyflakes; separators; `no_laya_in_gates` clean. Discrepancies: M1a now reddens 3
tests (the report says 2); the counts moved with the tree (86 findings, 1,788 rows at 28d5fcb5; the report's 62/1,708 and
86/1,772 were at earlier commits).

**F-24 UNVERIFIED - not executed by the lane or by me:** `--mode full`, `--device cuda` with bf16 autocast,
`--grad-checkpointing`, the evaluator's `ap` run (its positive control and the NaN reading), the blocking runs
(`v1_blocking`, `v1_full_blocking`), the PC venue. (`v1_full`'s positive control, also never run by the lane, now PASSES:
sec. 2e.)

**F-25 INFO - the option order of a stored distribution.** VERIFIED + STATIC. `distribution()` reads a choice's
probabilities by option NAME in the dataset question's criteria order (`common.py:239-244`; the lane's test reverses the
teacher's key order), the record stores `options`, and a reordered criteria dict changes `question_sha`, which the join
refuses. The live choice labels carry exactly the six option names (86 of 86 joined).

**F-26 INFO - process.** The session scratchpad is shared with the coordinator's live labeling run (`laya-ft-data/`) and
the lane (`ft1/`); a verifier writing a generic name such as `<scratch>/ds` could collide. I moved my outputs to
`<scratch>/vft1/` at 17:30Z (nothing pre-existed at the name). Future briefs could name a private scratch subdirectory.

## 5. What I reproduced, what I read, what I skipped

Reproduced by command (this session): the premise (9 values); the builder on the real tree and its determinism across two
commits; the dataset's masking, scrub, D-3 and AF-AP-189 properties; the D-3 guard reach on a fixture; the teacher CLI
against hostile local stand-ins (h1..h7, h2b), its limiter and retries on a fake clock, its resume across a changed dataset;
the coordinator's live labels (read only); the AF-AP-193 chain (real, crafted, 400 synthetic cuts); the trainer through
`train.py` (determinism pair, seed control, free-space refusal on a real tmpfs, `--lr inf` on 1 and 2 steps, cuda and
HF-cache refusals); the loss over the mask; `load_checkpoint` on seven state dicts; the evaluator's v1 and v1_full positive
controls and its NaN-checkpoint reading; 7 lane mutants and 16 new ones; pyflakes; separators; `no_laya_in_gates`.

Read only (STATIC): the CUDA/bf16 branch, `--grad-checkpointing`, the manifest revision rule, the base-URL userinfo path,
KC-J3's council definition, decide-harvest's import-time behaviour.

Skipped, with the reason: the codiv API (forbidden); `--mode full` and any full checkpoint (about 7 GB RAM and 1.6 GB of
checkpoint on a shared box with 3.2-3.5 GB free disk); CUDA (none here); the evaluator's `ap` run (1,951 s committed; the
NaN ap reading is shown on the sort key only); the lane's M2a/M2b re-run (trains the whole encoder on CPU, same memory
reason; its effect is covered by the passing trainer tests and the run-level guard in t1/t2/t5/t6); mutant N8 (same reason
as N7: `run()` is untested); the PC venue (no bridge calls).

Served model: claude-opus-5-5 (the session header); I cannot see a per-record mix from inside the lane.

## 6. Blocking predicate and gate recommendation

No finding meets all five conditions:
- F-1 (non-finite checkpoint, rc 0; the evaluator reads it as BLOCKER 7/7, ECE 0.0) meets conditions 2, 4 and 5 and maps to
  the repository's NaN invariant, but its trigger here is `--lr inf`, an operator misuse; a divergence under the
  production settings was not shown. It fails condition 3 (hypothetical misuse, defence in depth). It is the first
  follow-up to fix, before the GPU window, and the fix is small.
- F-2, F-3 need a server that echoes the key; the live codiv responses do not (0 of 957). Defence in depth.
- F-4, F-5, F-6 fail closed (nothing wrong trains or leaks); they cost operability, not correctness. F-5 is D-5's own key.
- F-7, F-8, F-9 are test and oracle gaps beyond the frozen evidence demands, which are all met; the real tree is clean
  (no held-out leak found by identity, exact text or fuzzy comparison).
- No CONTRACT-DEFECT: no production-path defect falsified evidence, corrupted state or lost data under the contract's use.
- No CONTRACT-INVALID: D-1..D-8 are consistent and measurable.

**Gate recommendation: MERGE-READY-WITH-FOLLOWUPS.** Follow-up order: F-1 (before the GPU window), F-6 (before the GPU
window: a full-mode run is the one that can lose hours), F-5, F-7, F-2/F-3, F-4, F-8, F-9. This depends on two things I
did not run: the full-mode/CUDA/bf16 path (F-24) and the ap evaluator path.
