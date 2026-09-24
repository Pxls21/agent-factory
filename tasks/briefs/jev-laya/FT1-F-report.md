# FT1-F report: the trainer refuses non-finite results and checks disk space before training (VERIFY-FT1 F-1, F-6)

Lane: FT1-F (sandbox code-implementer, Opus 5.5, served model claude-opus-5-5 per the session header).
Brief: `tasks/briefs/jev-laya/FT1-F-brief.md` (committed at origin d483505). Status: FINAL (written incrementally, 18:37:25Z to 20:04:20Z by `date -u`). Outcome: DONE (tests green, 32 passed twice; not committed, by rule). Each guard is exercised through its real entry point (`train.main`, `evaluate.main`) or on crafted tensors; the F-1 and F-6 refusals and the `--lr inf` usage error were also run live from the shell. Section 14 holds the brief's evidence.
Private scratch: `<scratchpad>/ft1f/` (`<scratchpad>` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad`).

## 1. Premise re-measure (first action)

Started 2026-09-24 18:37:25 UTC (`date -u`). Local HEAD `d483505d8bc6`.

```
$ for f in ...; do echo "$(git rev-parse --short=12 HEAD:$f) HEAD $f"; echo "$(git hash-object $f | cut -c1-12) WT   $f"; done
8d03bef2a83b HEAD scripts/laya_ft/train.py
8d03bef2a83b WT   scripts/laya_ft/train.py
96b0a2024012 HEAD scripts/laya_ft/evaluate.py
96b0a2024012 WT   scripts/laya_ft/evaluate.py
63f15afdb090 HEAD scripts/laya_ft/common.py
63f15afdb090 WT   scripts/laya_ft/common.py
20409b3606f5 HEAD tests/test_laya_ft.py
20409b3606f5 WT   tests/test_laya_ft.py
$ git status --short -- scripts/laya_ft tests/test_laya_ft.py     (empty; rc 0)
$ grep -n -E 'select_trainable\(|for epoch|train_step\(|save_checkpoint\(|GUARD FAILED|return 5' scripts/laya_ft/train.py
51:def select_trainable(model, mode):
105:def train_step(model, opt, items, mode, device, pad_id, params, max_grad_norm):
149:def save_checkpoint(sd, path, margin=64 << 20):
237:    trainable = select_trainable(model, args.mode)
249:    for epoch in range(args.epochs):
254:            total += train_step(model, opt, batch, args.mode, device, pad_id, params, args.max_grad_norm) * len(batch)
265:    save_checkpoint(sd, out / "checkpoint.pt")
331:        print("train: GUARD FAILED: %s" % m["guards"], file=sys.stderr)
332:        return 5
```

Dataset: `<scratchpad>/vft1/ds/dataset.jsonl` sha256 `d7cd9b49abac267bb9b5290641ea353180a9a61047ce6c590809520b085cea1c`
(the manifest names the same). Environment: `/` 3.4G free (91%), `/dev/shm` 16G, 4 CPUs, 15 GiB RAM.

The F-1 command, re-run into a PRIVATE out dir (the coordinator's `/dev/shm/ft1f-premise` was left untouched; its
checkpoint reads `1b8d1d4e...` too):
```
$ PYTHONDONTWRITEBYTECODE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/train.py --dataset <scratchpad>/vft1/ds --labels docs/research/findings/laya-ft-labels/2026-09-24-openjev/labels.jsonl --out /dev/shm/ft1f-lane-premise --mode head --device cpu --batch-size 4 --epochs 1 --limit 4 --lr inf --eval-loss --threads 2
(18:38:01Z -> 18:38:46Z)
epoch 1/1 loss 0.847582 (1 steps, 37 s)
{"checkpoint": {"bytes": 105002916, "file": "checkpoint.pt", "sha256": "1b8d1d4e7ba5e2e63c3e14139a4e1d383173fae32ccc9fe6d761307ff1db33f1"}, "device": "cpu", "eval_loss_after": NaN, "eval_loss_before": 0.807124137878418, "examples": {"by_question": {"ap.violates_row": 0, "v1.blocking": 2, "v1.finding_class": 2}, "n": 4}, "guards": {"act_head_unchanged": true, "encoder_unchanged": true, "model_dir_unchanged": true}, "per_epoch_loss": [0.8475820422172546], "steps": 1, "trained": {"parameters": 26248193, "prefixes": ["head", "scorer", "type_emb"], "tensors": 31}, "wall_seconds": 43.8}
rc=0
$ (torch.load + torch.isfinite per tensor)
/dev/shm/ft1f-lane-premise/checkpoint.pt tensors 31 non-finite 31
$ PYTHONDONTWRITEBYTECODE=1 bash scripts/test_summary.sh tests/test_laya_ft.py --basetemp=/tmp/ft1f/bt0   (18:39:15Z -> 18:41:19Z)
22 passed in 124.63s (0:02:04)
pytest-exit: 0
pytest-summary: 22 passed in 124.63s (0:02:04)
$ bash scripts/pc_suite.sh set-id -- tests/test_laya_ft.py
1 files set=8b147318aa48
```

CI view baseline (before any change):
```
$ PYTHONDONTWRITEBYTECODE=1 env -u S0_01_VENUE /root/venv-agent-factory/bin/python -m pytest tests/test_laya_ft.py -q -rs --basetemp=/tmp/ft1f/ci0 -p no:cacheprovider
18 passed, 4 skipped in 4.84s       (the 4 LOUD SKIPs at lines 642, 739, 746, 753)
```

Measured test-venue facts (they shape where the new tests can run; see DEVIATION-1 in section 6):
```
$ grep -n 'pip install' .github/workflows/stage0-ci.yml | head -1
      run: python -m pip install pyflakes pytest "jsonschema==4.25.1" "rfc3339-validator==0.1.4" "PyYAML>=6.0"
$ /root/venv-agent-factory/bin/python -c "import torch"    -> ModuleNotFoundError: No module named 'torch'
$ /usr/local/bin/python3 -c "import torch"                 -> ModuleNotFoundError: No module named 'torch'   (test_summary.sh's python3)
$ /usr/local/bin/python3 -c "import numpy"                 -> ModuleNotFoundError: No module named 'numpy'
$ /root/venv-laya-probe/bin/python -c "import torch, numpy" -> laya torch 2.14.0+cpu 2.4.6
```

**PREMISE: MATCH** on every measured value (4 blob hashes at HEAD and in the working tree, 9 grep anchors, rc 0 with the
same checkpoint sha `1b8d1d4e...`, `eval_loss_after` NaN, 31 of 31 tensors non-finite, 22 passed, set `8b147318aa48`).
Proceeding.

HEAD moved during the lane (`d483505` -> `67d1a25` by 18:55:52Z: the coordinator's retro, wiki and ledger commits, among
them `d7c9868`, which adds the AF-AP-196 and AF-AP-197 screen rows for F-1 and F-6). The four boundary files kept the
same blob ids at `67d1a25` (re-read 18:55:52Z).

## 2. What changed (files:lines in the working tree)

`scripts/laya_ft/train.py` (`git diff --numstat`: 67 added, 12 removed; evaluate.py 28/2; the test file 311/4):
- `train.py:48` `class NonFinite(FloatingPointError)`: the post-training refusal is a FloatingPointError, as
  train_step's own non-finite loss already was, so one except clause maps both to rc 5 with one stderr line (F-1, and
  F-4's trainer half). `train_step` itself is unchanged (the existing guard is extended, not replaced).
- `train.py:380` `except FloatingPointError as e:` in `main()`: one stderr line, then rc 5.
- `train.py:159` `def non_finite_tensors(sd):` the names of the tensors holding a NaN or an infinity
  (`torch.isfinite(t).all()`).
- `train.py:165` `def refuse_non_finite(sd, loss_after):` NonFinite when a trained tensor or `eval_loss_after` is not
  finite.
- `train.py:308` `refuse_non_finite(sd, loss_after)` in `run()`: on the state dict that would be saved, BEFORE
  `out.mkdir` (moved one line down, so a refused run creates no `--out` at all) and before `save_checkpoint`.
- `train.py:178` `def check_space(nbytes, directory, margin=64 << 20):` the free-space refusal, factored out of
  `save_checkpoint` (same message, same margin, same Refusal); it probes the nearest EXISTING ancestor and creates
  nothing.
- `train.py:282` `check_space(sum(p.numel() * p.element_size() for p in params), out)` in `run()`, right after
  `select_trainable` (F-6: before the optimizer, the `--eval-loss` pass and the first step).
- `train.py:195` `check_space(sum(t.numel() * t.element_size() for t in sd.values()), path.parent, margin)` in
  `save_checkpoint`: the check at save is kept.
- `train.py:214` `nonfinite = non_finite_tensors(sd)` in `load_checkpoint`: a checkpoint with any non-finite tensor is
  refused before `load_state_dict` (the model is left as it was).
- `train.py:370-374` `ap.error("--lr must be finite and > 0, not %r" % args.lr)` and its two siblings in `main()`:
  `--lr` finite and > 0 (when given), `--weight-decay` finite and >= 0, `--max-grad-norm` finite and > 0, each an
  `ap.error` (rc 2) naming the value, after the existing `--epochs` check.
- Module docstring: the exit line said "64 usage or refusal" while argparse usage errors exit 2 (already true of
  `--epochs`); my change adds three more rc-2 errors, so the line now reads "2 usage (argparse)", and it names rc 5's
  second meaning (a non-finite result, nothing written).

`scripts/laya_ft/evaluate.py` (28 added, 2 removed):
- `evaluate.py:44` `class NonFiniteAnswer(Exception)`.
- `evaluate.py:48` `def check_served(out):` refuses an answer whose `probabilities` values (choice, score) or `noul`
  are not all finite floats (Laya serves `round(float(v), 4)`, always a float; a NaN survives it).
- `evaluate.py:179` `out = check_served(server._answer(body["state"], body["questions"]))` in `post`: the refusal
  comes before the scorer sees the answer.
- `v1_probe.py:85-111` `def cmd_score(args):` and `ap_probe.py:97-135` `def cmd_score(args):` (both read): neither
  catches an exception from `post`.
- `evaluate.py:135` `def main(argv=None):` is now a thin wrapper: `NonFiniteAnswer` -> one stderr line, rc 5.
- `evaluate.py:143` `def _main(argv=None):` holds the old body (a rename, not a re-indent of the scoring loop). No
  `evaluate-summary.json` is written on a refusal.

`tests/test_laya_ft.py` (311 added, 4 removed; 22 -> 32 tests):
- `test_laya_ft.py:38` `from laya_ft import train as TR` (no torch at import).
- `test_laya_ft.py:263` `def _write_dataset(ddir, rows, model=None):` an optional `model` fingerprint (the existing
  callers pass none and get `{}` as before).
- `test_laya_ft.py:598` `def test_evaluator_refuses_a_served_probability_that_is_not_finite():` CI-runnable; crafted
  served answers in `system_one`'s shape (NaN, +inf, -inf, None, "0.5", 1 in a choice's probabilities and in a noul);
  the finite control passes unchanged.
- `test_laya_ft.py:616` `def _tampered_dataset(ddir):` a dataset `run()` refuses with rc 64 before any torch import.
- `test_laya_ft.py:624` `def test_train_refuses_optimizer_settings_outside_their_domain_at_parse_time(tmp_path, capsys):`
  CI-runnable; 13 out-of-domain values through `train.main`, each `SystemExit(2)` with its exact message; 3 in-domain
  controls parse and reach `run()` (rc 64 on the tampered dataset).
- `test_laya_ft.py:817` `GUARD_CHECK`: the crafted-tensor driver, run in the Laya venv (`laya_venue`, like the existing
  Laya tests).
- `test_laya_ft.py:886` `def guard_run(laya_venue, tmp_path_factory):` its module fixture, for three tests:
- `test_laya_ft.py:890` `def test_finiteness_guards_on_crafted_tensors(guard_run):` including the premise's shape
  (31 of 31 NaN plus a NaN loss).
- `test_laya_ft.py:902` `def test_load_checkpoint_refuses_a_non_finite_tensor_before_loading_it(guard_run):` a crafted
  module: the finite control loads, a NaN weight and a -inf bias are refused, the module is unchanged.
- `test_laya_ft.py:910` `def test_free_space_is_probed_without_writing_and_checked_again_at_save(guard_run):` the probe
  creates nothing and reads the nearest existing ancestor; the check at save still refuses with nothing written; the
  real-disk controls pass.
- `test_laya_ft.py:919` `TRAIN_CLI`: the `train.main` driver (a NaN after a real step, or a filesystem that reports
  40 MiB free).
- `test_laya_ft.py:963` `def _tiny_training_inputs(root, model_dir):` two rows from the real `make_row`, the model's
  real fingerprint, labels in the production record shape. Four `train.main` runs on the real model:
- `test_laya_ft.py:987` `def test_train_cli_refuses_a_non_finite_trained_tensor_and_writes_nothing(laya_venue, tmp_path):`
  a NaN written into the first trained parameter after the LAST real step: rc 5, nothing written.
- `test_laya_ft.py:995` `def test_train_cli_refuses_a_non_finite_loss_without_a_traceback(laya_venue, tmp_path):` the
  same fault before a second step (train_step's loss check): rc 5, no traceback.
- `test_laya_ft.py:1003` `def test_train_cli_refuses_a_full_disk_before_the_first_step(laya_venue, tmp_path):` a
  filesystem that reports 40 MiB free: rc 64, zero steps, one probe.
- `test_laya_ft.py:1013` `def test_train_cli_saves_a_finite_checkpoint_when_nothing_is_wrong(laya_venue, tmp_path):`
  the control: rc 0, 31 finite tensors, guards true.
- `test_laya_ft.py:1021` `EVAL_CLI`: the `evaluate.main --only v1` driver.
- `test_laya_ft.py:1058` `def test_evaluate_cli_refuses_a_non_finite_served_probability(laya_venue, tmp_path):` the
  real model serves one finite answer, then a NaN in the same head parameter; rc 5 after exactly 7 served answers,
  nothing written (a tripwire raises on an 8th answer, so a guard-less run fails fast instead of scoring 100 rows).

First green (before the red-green and mutation passes):
```
$ env -u S0_01_VENUE /root/venv-agent-factory/bin/python -m pytest tests/test_laya_ft.py -k "optimizer_settings or served_probability_that_is_not_finite"
2 passed, 30 deselected in 0.17s
$ S0_01_VENUE=sandbox python3 -m pytest tests/test_laya_ft.py -k "finiteness_guards or refuses_a_non_finite_tensor_before or probed_without_writing"
3 passed, 29 deselected in 2.14s
$ S0_01_VENUE=sandbox python3 -m pytest tests/test_laya_ft.py -k "train_cli or evaluate_cli" --durations=10   (19:02:10Z -> 19:06:38Z)
72.77s call  test_evaluate_cli_refuses_a_non_finite_served_probability
60.88s call  test_train_cli_saves_a_finite_checkpoint_when_nothing_is_wrong
60.35s call  test_train_cli_refuses_a_non_finite_trained_tensor_and_writes_nothing
46.48s call  test_train_cli_refuses_a_non_finite_loss_without_a_traceback
27.11s call  test_train_cli_refuses_a_full_disk_before_the_first_step
5 passed, 27 deselected in 267.81s (0:04:27)
```

## 3. Red-green: the new tests against the PRE-FIX code (no tree mutation)

A `git clone --shared --no-checkout` of this repo into `<scratchpad>/ft1f/rg`, sparse (`docs/ scripts/ src/ tests/
pyproject.toml`), detached at `67d1a25`, with ONLY the new `tests/test_laya_ft.py` copied in. Identity, before the run:
```
67d1a256f8fd
8d03bef2a83b scripts/laya_ft/train.py        (the HEAD blob: pre-fix)
96b0a2024012 scripts/laya_ft/evaluate.py     (the HEAD blob: pre-fix)
63f15afdb090 scripts/laya_ft/common.py
85afff079038 tests/test_laya_ft.py           (= git hash-object of the working-tree test file)
$ python3 -c "...sys.path.insert(0, '<rg>/scripts'); from laya_ft import train, evaluate; print(train.__file__, 'NonFinite' in dir(train), 'check_served' in dir(evaluate))"
<scratchpad>/ft1f/rg/scripts/laya_ft/train.py False False
```
The ten new tests (19:08:29Z -> 19:14:07Z), `PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox python3 -m pytest tests/test_laya_ft.py -k "<the 10>"`:
```
6 failed, 1 passed, 22 deselected, 3 errors in 337.24s (0:05:37)
ERROR at setup of test_finiteness_guards_on_crafted_tensors            AttributeError: module 'laya_ft.train' has no attribute 'non_finite_tensors'
ERROR at setup of test_load_checkpoint_refuses_a_non_finite_tensor_... (the same fixture)
ERROR at setup of test_free_space_is_probed_without_writing_and_...     (the same fixture)
test_evaluator_refuses_a_served_probability_that_is_not_finite         AttributeError: module 'laya_ft.evaluate' has no attribute 'check_served'
test_train_refuses_optimizer_settings_outside_their_domain_at_parse_time   Failed: DID NOT RAISE SystemExit
test_train_cli_refuses_a_non_finite_trained_tensor_and_writes_nothing  assert (0, 1, 'head....nifest.json']) == (5, 1, 'head....weight', None)
test_train_cli_refuses_a_non_finite_loss_without_a_traceback           FloatingPointError: non-finite loss nan: the step is refused  (the driver died on the raw traceback)
test_train_cli_refuses_a_full_disk_before_the_first_step               assert (64, 1, []) == (64, 0, None)   asked ['.../out']  (refused at save, after 1 step, --out created)
test_evaluate_cli_refuses_a_non_finite_served_probability              RuntimeError: the evaluator went on past a non-finite answer: 7 served
PASSED test_train_cli_saves_a_finite_checkpoint_when_nothing_is_wrong   (the control is green on the old code too)
```
Five reds are behavioral (the old code's actual F-1/F-4/F-6 behavior, read in each assertion); four are structural (the
guard functions did not exist). The loader's behavioral red, shown directly (`<scratchpad>/ft1f/old_loader.py`, a
crafted module and a checkpoint with one NaN):
```
module <scratchpad>/ft1f/rg/scripts/laya_ft/train.py has non_finite_tensors: False
old load_checkpoint -> (2, ['head']) ; model weight finite: False
module /home/user/agent-factory/scripts/laya_ft/train.py has non_finite_tensors: True
Refusal: checkpoint /tmp/ft1f/oldload/nan_weight.pt: 1 of 2 tensors are not finite: ['head.weight']
```
No `__pycache__` was written in the clone (`find <rg> -name __pycache__ | wc -l` = 0 after the run).

## 4. Mutation audit (evidence demand 4)

Driver `<scratchpad>/ft1f/mutants.py`: one FRESH `copytree` of the base per mutant (`<scratchpad>/ft1f/rgnew` = the
section-3 clone with the new train.py `94bc7db5e53f` and evaluate.py `37935e8ee8f3`, both equal to `git hash-object` of
the working tree), `PYTHONDONTWRITEBYTECODE=1` for pytest and its Laya subprocesses, the anchor asserted to occur exactly
once, the mutated file compiled in memory, a collect-only pass that must select exactly the named test, an identity
probe (`importlib.import_module('laya_ft.<file>').__file__` must be the mutant copy's; every row below printed its own
path), and `EXPECTED = 22` as a literal (the driver exits `DRIVER-INVALID` if the table and the groups disagree).
`__pycache__` directories in every mutant copy after every run: 0.

Controls (the unmutated base through the same driver):
```
control-fast  optimizer_settings                         1 passed, 31 deselected in 0.24s
control-fast  served_probability_that_is_not_finite      1 passed, 31 deselected in 0.18s
control-fast  finiteness_guards or ..._before or probed_without_writing   3 passed, 29 deselected in 1.79s
control-e2e   the four real-model CLI tests               4 passed, 28 deselected in 174.42s (0:02:54)
```

| # | Guard (file) | Mutant | Test that turns red | Kill line (pasted) |
|---|---|---|---|---|
| T1 | `--lr` domain (train.py) | the check `if False:` | `test_train_refuses_optimizer_settings_outside_their_domain_at_parse_time` | `Failed: DID NOT RAISE SystemExit` |
| T2 | `--lr` finite | `math.isfinite` dropped (`args.lr > 0` only) | same | `Failed: DID NOT RAISE SystemExit` (inf accepted) |
| T3 | `--lr` > 0 | `>= 0` | same | `Failed: DID NOT RAISE SystemExit` (0 accepted) |
| T4 | `--weight-decay` domain | the check `if False:` | same | `Failed: DID NOT RAISE SystemExit` |
| T5 | `--weight-decay` >= 0 | `> 0` (over-strict) | same, its in-domain CONTROL (line 630) | `SystemExit: 2` / `error: --weight-decay must be finite and >= 0, not 0.0` |
| T6 | `--max-grad-norm` domain | the check `if False:` | same | `Failed: DID NOT RAISE SystemExit` |
| T7 | `--max-grad-norm` > 0 | `>= 0` | same | `Failed: DID NOT RAISE SystemExit` (0 accepted) |
| T8 | `refuse_non_finite` tensor branch | `bad = []` | `test_finiteness_guards_on_crafted_tensors` | `AssertionError: {... 'finite': ...}` (the `tensor` and `premise` refusals changed) |
| T9 | `refuse_non_finite` eval_loss_after branch | `if False:` | same | `AssertionError: {... 'finite': ...}` (`loss_nan`, `loss_inf` let through) |
| T10 | the `refuse_non_finite` call in `run()` | `pass` | `test_train_cli_refuses_a_non_finite_trained_tensor_and_writes_nothing` | `AssertionError: {'steps': 1, 'poisoned': 'head.layers.0.self_attn.in_proj_weight', 'asked': [], 'rc': 0, ...}` |
| T11 | `main()`'s `except FloatingPointError` -> rc 5 | `except ZeroDivisionError` | `test_train_cli_refuses_a_non_finite_loss_without_a_traceback` | `FloatingPointError: non-finite loss nan: the step is refused` (the raw traceback) |
| T12 | `load_checkpoint` non-finite refusal | `if False:` | `test_load_checkpoint_refuses_a_non_finite_tensor_before_loading_it` | `assert None == ("Refusal: checkpoint %s/nan_weight.pt: 1 of 2 tensors are not finite: ['head.weight']" % ...)` |
| T13 | the early `check_space` in `run()` (F-6) | `pass` | `test_train_cli_refuses_a_full_disk_before_the_first_step` | `AssertionError: {'steps': 1, 'poisoned': None, 'asked': ['.../out'], 'rc': 64, ...}` (refused at save, after a step) |
| T14 | the kept `check_space` in `save_checkpoint` | `pass` | `test_free_space_is_probed_without_writing_and_checked_again_at_save` | `AssertionError: {... 'save': None, ...}` |
| T15 | `check_space`'s walk to the nearest existing ancestor | the walk removed | same | `FileNotFoundError: [Errno 2] No such file or directory: '.../ft1f-guards0/not/yet'` |
| T16 | `non_finite_tensors` covers the whole class | `~torch.isnan` (inf let through) | `test_finiteness_guards_on_crafted_tensors` | `AssertionError: {... 'order': ['d'] ... 'inf_bias': None ...}` |
| T17 | nothing written on a refusal (the order) | `out.mkdir` before `refuse_non_finite` | `test_train_cli_refuses_a_non_finite_trained_tensor_and_writes_nothing` | `assert (5, 1, 'head....j_weight', []) == (5, 1, 'head....weight', None)` / `At index 3 diff: [] != None` |
| E1 | `check_served` in `post` (evaluate.py) | `out = server._answer(...)` | `test_evaluate_cli_refuses_a_non_finite_served_probability` | `RuntimeError: the evaluator went on past a non-finite answer: 7 served` |
| E2 | `check_served` | `return out` first | `test_evaluator_refuses_a_served_probability_that_is_not_finite` | `Failed: DID NOT RAISE NonFiniteAnswer` |
| E3 | `check_served` covers the whole class | `v == v` (inf let through) | same | `Failed: DID NOT RAISE NonFiniteAnswer` |
| E4 | `check_served` reads `noul` | `+ []` | same | `Failed: DID NOT RAISE NonFiniteAnswer` |
| E5 | `main()`'s `NonFiniteAnswer` -> rc 5 | `except ZeroDivisionError` | `test_evaluate_cli_refuses_a_non_finite_served_probability` | `laya_ft.evaluate.NonFiniteAnswer: answer 'BLOCKER' serves the probability nan, not a finite float` (the raw traceback) |

Result: 22 of 22 KILLED (`GROUP fast: 16 mutants, KILLED 16`; `GROUP e2e1: 3 mutants, KILLED 3`; `GROUP e2e2: 3
mutants, KILLED 3`), 0 INVALID. The rows T5, T11, T15, T17 and E5 show the line from a second read of the preserved
mutant copy (the driver's first line extractor took `SystemExit` for no E line and a traceback header for the reason;
the driver was fixed before the e2e2 group).

## 5. Live evidence through the real CLI (evidence demands 1 and 2)

### 5a. F-1: the premise command, before and after

BEFORE (section 1, 18:38Z): `--lr inf` -> rc 0, `"eval_loss_after": NaN`, a checkpoint with 31 of 31 tensors non-finite.

AFTER, the same command verbatim into a fresh `--out` (19:28:03Z):
```
$ PYTHONDONTWRITEBYTECODE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/train.py --dataset <scratchpad>/vft1/ds --labels docs/research/findings/laya-ft-labels/2026-09-24-openjev/labels.jsonl --out /dev/shm/ft1f-lane-after --mode head --device cpu --batch-size 4 --epochs 1 --limit 4 --lr inf --eval-loss --threads 2
usage: train.py [-h] --dataset DATASET --labels LABELS --out OUT --mode
                ...
train.py: error: --lr must be finite and > 0, not inf
rc=2
$ ls -la /dev/shm/ft1f-lane-after
ls: cannot access '/dev/shm/ft1f-lane-after': No such file or directory
```
The injected fault, through `train.main`, the same dataset, labels and settings minus `--lr inf`
(`<scratchpad>/ft1f/live_f1.py fault`: a NaN written into the first trained parameter after the real step; 19:28:20Z ->
19:29:05Z):
```
module /home/user/agent-factory/scripts/laya_ft/train.py
fault: NaN written into head.layers.0.self_attn.in_proj_weight after the real step
epoch 1/1 loss 0.847582 (1 steps, 37 s)
train: refused: NonFinite: 1 of 31 trained tensors are not finite (head.layers.0.self_attn.in_proj_weight); eval_loss_after is nan: nothing is saved
rc=5
--out exists: False | listing: None
```
The premise's own mechanism, past the parse check (`live_f1.py lrinf`: `train.run()` with `lr=inf`, one AdamW step on
the same 4 rows; 19:29:05Z -> 19:30:09Z). The epoch loss equals the premise's, and the post-training guard refuses the
state the premise saved:
```
epoch 1/1 loss 0.847582 (1 steps, 54 s)
run() raised NonFinite: 31 of 31 trained tensors are not finite (head.layers.0.self_attn.in_proj_weight, head.layers.0.self_attn.in_proj_bias, head.layers.0.self_attn.out_proj.weight); eval_loss_after is nan: nothing is saved
--out exists: False | listing: None
```

### 5b. F-6: a real 40 MB tmpfs (the sandbox runs as root), before and after

```
$ mount -t tmpfs -o size=40m tmpfs /tmp/ft1f/small && df -h /tmp/ft1f/small
tmpfs            40M     0   40M   0% /tmp/ft1f/small
== BEFORE (pre-fix train.py, blob 8d03bef2a83b, the section-3 clone)          19:30:21Z -> 19:31:19Z
epoch 1/1 loss 0.847582 (1 steps, 55 s)
train: refused: Refusal: the checkpoint needs 164 MiB and /tmp/ft1f/small/before has 40 MiB free
rc=64                                   (the step ran and was lost; --out 'before' created, left empty)
== AFTER (this tree's train.py, blob 94bc7db5e53f)                             19:31:19Z -> 19:31:54Z
train: refused: Refusal: the checkpoint needs 164 MiB and /tmp/ft1f/small/after has 40 MiB free
rc=64                                   (no step, no epoch line; --out 'after' never created)
$ ls -la /tmp/ft1f/small/     (after both runs)
drwxr-xr-x  2 root root   40 Sep 24 19:31 before
$ umount /tmp/ft1f/small; findmnt /tmp/ft1f/small   -> rc 1 (not mounted); rmdir /tmp/ft1f/small
```
Both runs share the dataset, the labels and the settings (`--limit 4 --batch-size 4 --epochs 1 --threads 2`). The wall
time falls from 58 s to 35 s, which is the model load alone. In the test the same order is exact
(`test_train_cli_refuses_a_full_disk_before_the_first_step`: `steps == 0`, one `disk_usage` probe, `--out` absent).

Clean-up: my `/dev/shm/ft1f-lane-premise` (sha `1b8d1d4e...`) removed; the coordinator's `/dev/shm/ft1f-premise` left
untouched (its checkpoint still reads `1b8d1d4e...`).

## 6. A PRE-EXISTING red in this file, introduced by a tree commit during the lane (not by this change)

The CI view at 19:33Z read `1 failed, 19 passed, 12 skipped`. The one red is the EXISTING
`test_collect_excludes_every_heldout_row_on_the_real_tree` (it reads the live repo at `HEAD` through `BD.collect`):
```
E       AssertionError: assert (104 + 100) == 205
E        +  where 104 = len({('tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md', 'A-1'), ...})
```
Proof that it is pre-existing: a fresh sparse `--shared` clone at the current HEAD `c548f30`, every file UNMODIFIED
(`train.py 8d03bef2a83b`, `tests/test_laya_ft.py 20409b3606f5`, `build_dataset.py 9ecf61065267`, `common.py
63f15afdb090`), the original test file:
```
$ env -u S0_01_VENUE /root/venv-agent-factory/bin/python -m pytest tests/test_laya_ft.py -k test_collect_excludes_every_heldout_row_on_the_real_tree
E       AssertionError: assert (104 + 100) == 205
1 failed, 21 deselected in 0.86s
```
Cause (read, then counted): `src["verify_findings"] += 1` counted every finding BLOCK (`build_dataset.py@c548f30:79-82`), while the
test compares a SET of `(path, finding_id)` pairs. `tasks/briefs/jev-laya/VERIFY-JT3-R1-report.md` yields the id `N-10`
twice since `bdeaeb8` (19:09Z, "VERIFY-JT3-R1 report section 11 (the JT3-R2 reverify ...)"): the reverify section
re-lists N-10 with a new title. `J2C._blocks` over that file: `d483505` 15 blocks, 1 `N-10`; `bdeaeb8` 19 blocks,
2 `N-10`; `c548f30` 19 blocks, 2 `N-10`. The premise baseline (22 passed, 18:39Z) ran at `d483505`, before it.
NOT fixed here (adjacent to this lane's scope; see section 9, ADJ-1). Every `test_summary` count below carries this one
pre-existing failure.

Coordinator update received mid-lane (two messages): the red above is pre-existing and not this lane's; the coordinator
fixed it OUTSIDE this boundary in `scripts/laya_ft/build_dataset.py` (a finding id a report repeats counts once, the
first block kept), committed and pushed as `f1679db` (commit clock 19:40:24Z; HEAD `9eeced8` at 19:45Z). I did not
touch the builder or that test. `build_dataset.py` in the working tree now reads `b2dfcdeced34` = HEAD's blob; my three
files are unchanged (`94bc7db5e53f`, `37935e8ee8f3`, `85afff079038`; HEAD still holds the originals).

## 7. test_summary runs, the set id and the CI view (evidence demand 3)

```
$ bash pc_suite.sh set-id -- tests/test_laya_ft.py
1 files set=8b147318aa48
run 1  19:34:39Z -> 19:38:50Z  (HEAD c548f30, before the builder fix)
$ PYTHONDONTWRITEBYTECODE=1 bash scripts/test_summary.sh tests/test_laya_ft.py --basetemp=/tmp/ft1f/ts1
pytest-exit: 1
pytest-summary: 1 failed, 31 passed in 251.23s (0:04:11)
  the one failure: test_collect_excludes_every_heldout_row_on_the_real_tree, assert (104 + 100) == 205 (section 6)
run 2  19:38:55Z -> 19:44:57Z  (RACED the coordinator's builder fix: build_dataset.py mtime 19:39:15Z)
$ PYTHONDONTWRITEBYTECODE=1 bash scripts/test_summary.sh tests/test_laya_ft.py --basetemp=/tmp/ft1f/ts2
pytest-exit: 1
pytest-summary: 2 failed, 30 passed in 361.67s (0:06:01)
  test_collect_excludes_every_heldout_row_on_the_real_tree   assert (104 + 100) == 205 (it ran before 19:39:15Z)
  test_builder_is_deterministic_and_every_state_fits_the_window   AssertionError: manifest.json / At index 506 diff: b'b' != b'8'
     (its two builds ran with different build_dataset.py code: the manifest records the code digest; a race with the
      concurrent edit, not a determinism defect; neither test touches train.py or evaluate.py)
```
```
run 3  19:45:33Z -> 19:49:46Z  (HEAD 9eeced8, the builder fix in; build_dataset.py untouched during the run)
$ PYTHONDONTWRITEBYTECODE=1 bash scripts/test_summary.sh tests/test_laya_ft.py --basetemp=/tmp/ft1f/ts3
32 passed in 252.33s (0:04:12)
pytest-exit: 0
pytest-summary: 32 passed in 252.33s (0:04:12)
run 4  19:49:52Z -> 19:54:00Z
$ PYTHONDONTWRITEBYTECODE=1 bash scripts/test_summary.sh tests/test_laya_ft.py --basetemp=/tmp/ft1f/ts4
32 passed in 248.29s (0:04:08)
pytest-exit: 0
pytest-summary: 32 passed in 248.29s (0:04:08)
$ bash scripts/pc_suite.sh set-id -- tests/test_laya_ft.py     (after run 4)
1 files set=8b147318aa48
(after run 4: train.py 94bc7db5e53f, evaluate.py 37935e8ee8f3, tests/test_laya_ft.py 85afff079038; HEAD 9eeced824647)
```
Runs 3 and 4 are the demanded pair: the same count twice, 32 passed. CI view (the whole file, 19:5xZ):
```
$ PYTHONDONTWRITEBYTECODE=1 env -u S0_01_VENUE /root/venv-agent-factory/bin/python -m pytest tests/test_laya_ft.py -q -rs --basetemp=/tmp/ft1f/ci4 -p no:cacheprovider
20 passed, 12 skipped in 4.70s      (12 LOUD SKIPs at lines 697 794 801 808 890 902 910 987 995 1003 1013 1058: the
                                     4 existing Laya tests and the 8 new Laya-venue tests; "the Laya venv and snapshot
                                     are declared inputs of the sandbox venue only (S0_01_VENUE=None; ...)")
$ PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=ci /root/venv-agent-factory/bin/python -m pytest tests/test_laya_ft.py ...   (the workflow's value)
20 passed, 12 skipped in 4.50s
```
Baseline for comparison: 22 passed (sandbox venue) and 18 passed, 4 skipped (CI view) before the change.

## 8. Lint, separators and the advisory instruments

```
$ /root/venv-agent-factory/bin/python -m pyflakes scripts/laya_ft/train.py scripts/laya_ft/evaluate.py tests/test_laya_ft.py
(no output) pyflakes rc=0          (pyflakes 3.4.0, Python 3.11.15)
$ for f in <every file I wrote>; do LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' "$f"; done
0 scripts/laya_ft/train.py
0 scripts/laya_ft/evaluate.py
0 tests/test_laya_ft.py
0 tasks/briefs/jev-laya/FT1-F-report.md
0 <scratchpad>/ft1f/mutants.py
0 <scratchpad>/ft1f/live_f1.py
0 <scratchpad>/ft1f/old_loader.py
0 <scratchpad>/ft1f/probe_params.py
0 <scratchpad>/ft1f/probe_load.py
$ python3 scripts/lint_delta.py --base HEAD
lint_delta (worktree vs HEAD): 3 .py changed, 0 NEW pyflakes hit(s), 0 removed
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean
$ node .gitnexus/run.cjs detect-changes --scope all --repo .
Changes: 3 files, 32 symbols / Affected processes: 4 (Run -> Dumps, Sha256_hex, Jsonl_lines, Label_key: run()'s own
calls into common) / Risk level: medium        (impact before the edits: save_checkpoint, load_checkpoint, train_step,
run, both main functions: all LOW)
$ python3 scripts/report_lint.py tasks/briefs/jev-laya/FT1-F-report.md --map train.py=... (6 aliases) --min-refs 30
report_lint: 36 refs — OK 36, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)      (one repair round)
```
The screens' TELLS (advisory), each triaged: `lint_delta`'s AF-AP-197 (a free-space probe) and AF-AP-196 (a tensor
save) are this change's own subjects: the probe now runs before the work and at save, and the save follows
`refuse_non_finite` in `run()`. AF-AP-196 keeps firing on `torch.save(sd, str(tmp))` because the guard is at the call
site, not inside `save_checkpoint` (see ADJ-4). `ap_screen --tests`' four AP-66 hits (direct attribute reassignment)
are inside the three driver strings, which run in their own Laya-venv subprocess per test and cannot leak into the
pytest process (GUARD_CHECK restores `disk_usage` before its real-disk controls); AF-AP-40 in the tests is the
driver's `if out_dir.exists()` listing, and the control asserts `tensors` and `non_finite`, so an absent checkpoint
cannot pass silently. The production-file hits AP-2 (`os.environ.setdefault` in both loaders), AF-AP-40
(`if tmp.exists()`, `if p.is_file()`) and AP-32 (`hashlib.sha256()` in `param_digest`) are on pre-existing lines.

## 9. The evaluator's normal path with the guard in place, and a non-finite checkpoint

The v1 positive control, the base model through the guarded `post` (all 100 J2 rows, 7 served answers each; 19:55:50Z
-> 19:59:29Z, `--threads 4`):
```
$ PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 timeout 570 /root/venv-laya-probe/bin/python -B scripts/laya_ft/evaluate.py --only v1 --out-dir /tmp/ft1f/eval-base --threads 4
== v1 (194 s) ==
KC-J3 v1 jev_choice: accuracy 0.2100 vs max(majority 0.4300, heuristic 0.4100) = 0.4300 -> REJECTED (at or under)
KC-J3 v1 jev_noul: accuracy 0.0300 vs max(majority 0.4300, heuristic 0.4100) = 0.4300 -> REJECTED (at or under)
{"agreement_with_committed_base": {"jev_choice": "100/100", "jev_noul": "100/100"}, ... "differences_from_committed_base": [], "ece": 0.0481, "seconds": 194.4}
POSITIVE CONTROL (no checkpoint): PASS
rc=0
```
The same numbers VERIFY-FT1 read before the change (its sec. 2e: 100/100, [], ECE 0.0481): the guard refused none of
the base model's served answers on the real sample.

The coordinator's premise checkpoint (31 of 31 NaN; read only, sha `1b8d1d4e...` before and after):
```
$ ... evaluate.py --checkpoint /dev/shm/ft1f-premise/checkpoint.pt --only v1 --out-dir /tmp/ft1f/eval-nan --threads 4
  File "/home/user/agent-factory/scripts/laya_ft/train.py", line 216, in load_checkpoint
laya_ft.train.Refusal: checkpoint /dev/shm/ft1f-premise/checkpoint.pt: 31 of 31 tensors are not finite: ['head.layers.0.self_attn.in_proj_weight', 'head.layers.0.self_attn.in_proj_bias', 'head.layers.0.self_attn.out_proj.weight']
rc=1        (out dir empty: nothing scored)
```
VERIFY-FT1 read the same checkpoint as "every prediction BLOCKER, BLOCKER recall 7/7, ECE 0.0" with no error. Now the
loader refuses it. The refusal surfaces as a raw traceback with rc 1, because `evaluate.main` has never caught
`train.Refusal` for any loader refusal (ADJ-2).

## 10. DEVIATIONS from the brief (flagged)

- **DEVIATION-1: "a pure guard (a finiteness check over a state dict, the loader) gets a CI-runnable test on crafted
  tensors" cannot hold: CI has no torch.** `stage0-ci.yml` installs `pyflakes pytest jsonschema rfc3339-validator
  PyYAML` only, and neither sandbox test interpreter has torch (section 1). The crafted-tensor tests run in the Laya
  venv through the same `laya_venue` gate as the existing Laya tests, so they run in the sandbox venue and skip loudly
  in CI (3 of the 12 skips). What IS CI-runnable: the three argument domains (`train.main`, no model and no torch) and
  the evaluator's served-probability guard (`check_served` over the served dict, which is plain Python). I did not
  duck-type a fake tensor to force a CI run: that would test a stand-in, not `torch.isfinite`.
- **DEVIATION-2: F-6 "in a test" fakes the free space, not the filesystem.** Inside the test, `shutil.disk_usage`
  reports 40 MiB for the test's directory, and the guard runs for real. Mounting a tmpfs inside pytest needs root and
  would leak a mount if the test died. The real 40 MB tmpfs is in section 5b, before and after.
- **DEVIATION-3: `--max-grad-norm 0` used to mean "no clipping"** (`if max_grad_norm:` in `train_step`). The brief's
  "> 0" makes it a usage error. `train_step` is unchanged, so a direct caller can still pass 0 or None.
- **DEVIATION-4: shape choices the brief left open.**
  - The evaluator's refusal is rc 5 (the brief said "non-zero"), matching the trainer's non-finite rc.
  - A refused non-finite trainer run creates no `--out` at all (`out.mkdir` moved after the check), which is stricter
    than "no checkpoint.pt, no .tmp".
  - `check_space` is factored out of `save_checkpoint`, so both checks share one formula (the save-time message,
    margin and exception are unchanged; the test and mutant T14 pin it).
  - `evaluate.main` became a wrapper over `_main` (a rename).
  - The trainer docstring's exit line was corrected ("64 usage" -> "2 usage"), a comment my change would otherwise
    have left wrong.
- **DEVIATION-5: the suite's wall time grows.** The 5 real-model CLI tests take about 4 to 4.5 minutes; the whole file
  now runs in about 250 s on a quiet box (the premise baseline was 125 s). Each `train.main`/`evaluate.main` call
  loads the model, and one load measured 35-37 s here. I did not memoize the loader across scenarios: a reused agent
  keeps train-mode and grad state that a fresh load would reset.

## 11. Adjacent defects (reported, not fixed)

- **ADJ-1 (pre-existing, now fixed by the coordinator outside this boundary).** A report that restates a finding id
  (VERIFY-JT3-R1's reverify re-listed N-10) broke `test_collect_excludes_every_heldout_row_on_the_real_tree` (section
  6). `f1679db` counts a repeated id once. I did not touch the builder or that test.
- **ADJ-2: `evaluate.main` does not catch `train.Refusal`.** Every `load_checkpoint` refusal, the new non-finite one
  included, ends in a raw traceback with rc 1 instead of a one-line refusal (section 9). A `except T.Refusal` around
  the load, printing one line with rc 64, would match the trainer. It is the F-4 class, on the evaluator side.
- **ADJ-3: `--threads` is not domain-checked (train.py and evaluate.py).** `if args.threads: torch.set_num_threads(...)`
  passes a negative value to torch, which raises `RuntimeError: set_num_threads expects a positive integer` (probed in
  the Laya venv). The CLI then ends in a raw traceback; that CLI path is a static read. `--threads 0` is silently read
  as "the default".
- **ADJ-4: `save_checkpoint` itself saves a non-finite state dict.** The guard sits in `run()`, as the brief places it,
  so a direct caller of `save_checkpoint` (today only the test driver `TRAINER_CHECK`) is not covered. Adding
  `refuse_non_finite(sd, None)` inside `save_checkpoint` would make every save refuse.
- **ADJ-5: the `GUARD FAILED` rc-5 path (a frozen part changed) is still untested through `main()`,** as VERIFY-FT1
  F-7 noted. Its lines are unchanged here.
- The rest of VERIFY-FT1 (F-2, F-3, F-4's teacher half, F-5, F-7 beyond the CLI tests added here, F-8, F-9) is untouched,
  as the brief directs (they go to an issue).

## 12. Self-attack: the three most likely ways this change is wrong

1. **The early free-space check refuses a run that fits, or reads the wrong filesystem.**
   - The size is the save-time formula over the same tensors. The saved dict is `p.detach().cpu().clone()` of exactly
     the trainable parameters, so numel and dtype match; bf16 autocast changes compute, not parameter dtype.
   - The tmpfs pair printed the same `164 MiB` from the old save-time check and the new early one.
   - The probe walks to the nearest existing ancestor. A path that does not exist cannot be a mount point, so the new
     directory lands on that ancestor's filesystem, and a symlinked parent is followed by `exists()` and
     `disk_usage()` alike.
   - The real-disk control trains and saves; mutants T13 (no early check) and T15 (no walk) die.
   - Not run: CUDA and full mode (no GPU here). The byte count does not depend on the device (inferred).
2. **A finiteness guard refuses a legitimate result, or misses part of the class.**
   - Crafted cases: a 3e38 value, an empty tensor and a bf16 tensor pass; NaN, +inf, -inf and a bf16 NaN are refused.
     Mutants T16 and E3 (NaN-only checks) die.
   - The real-model control saves 31 finite tensors.
   - The guarded v1 positive control over all 100 J2 rows still PASSes (100/100, ECE 0.0481).
   - Not re-run with the guard: `v1_full`, `ap` and the blocking runs. Their answers come from the same
     `round(float(...), 4)` path in `laya.Agent.system_one` (read).
3. **The new exception mapping changes behavior someone relies on.**
   - `except FloatingPointError` in `main()` maps any FloatingPointError to rc 5; in this module only non-finite math
     raises one.
   - `--max-grad-norm 0` is now refused (DEVIATION-3).
   - The success path still creates `--out` before saving (the control test).
   - All 22 pre-existing tests stay green (runs 3 and 4), and the CI view keeps the 18 existing CI tests green.
   - The existing `GUARD FAILED` rc-5 path (checkpoint and manifest written) is unchanged by a static read, but not
     executed (ADJ-5).

## 13. Evidence tiers and NOT-done

VERIFIED by a command in this session:
- The premise (every value).
- F-1: the premise command's rc 0, then rc 2 after; the injected-fault run with rc 5 and no `--out`; the premise's own
  `lr=inf` state refused by `run()`.
- F-6: before and after on a real 40 MB tmpfs.
- The red-green on the pre-fix code (9 red for the named reasons, the control green) and the old loader accepting a
  NaN checkpoint.
- 22 of 22 mutants killed; runs 3 and 4 at 32 passed each; the CI view 20 passed, 12 skipped.
- pyflakes, the separators, `lint_delta`, `no_laya_in_gates`, `detect-changes` and `report_lint`.
- The guarded v1 positive control PASS; the evaluator refusing the NaN checkpoint.
- The pre-existing red, its cause and its commit; `torch.set_num_threads(-1)` raising.

INFERRED:
- The two CI-runnable tests pass on CI's Python 3.12 (they ran on 3.11 here). They use only stdlib and pytest, and
  `--flag=value` avoids argparse's version-dependent reading of a bare negative value.
- The early check's byte count is the same on CUDA.
- The `--threads -1` CLI path (the torch call was probed; the CLI path is a static read).

ASSUMED: none load-bearing.

NOT DONE:
- No commit, push or PR (standing rule); the coordinator commits.
- Full mode, CUDA and bf16 not run (no GPU; RAM and disk).
- The evaluator's `v1_full`, `ap` and blocking runs not re-run with the guard.
- No Python 3.12 run of the CI job (no network to install pytest for 3.12).
- ADJ-2 to ADJ-5 not fixed (out of scope); VERIFY-FT1's other follow-ups not touched.

Scratch kept for a re-run: `<scratchpad>/ft1f/` holds `mutants.py`, `live_f1.py`, `old_loader.py`, the clones `rg`
(pre-fix + new tests) and `rgnew` (new code + new tests), and `logs/`. The mutant copies, the HEAD proof clone and
every pytest basetemp were deleted to free about 1 GB (the root disk was at 95%).

## 14. Evidence, as the brief demands it (pasted from the runs above)

**1. The F-1 command, before and after.**
```
BEFORE  train.py ... --lr inf --eval-loss ...            -> rc=0, "eval_loss_after": NaN, checkpoint.pt sha256 1b8d1d4e...
        torch.isfinite per tensor                        -> /dev/shm/ft1f-lane-premise/checkpoint.pt tensors 31 non-finite 31
AFTER   train.py ... --lr inf --eval-loss ...            -> train.py: error: --lr must be finite and > 0, not inf / rc=2
                                                            (no --out created)
        the injected fault (same command minus --lr inf; a NaN written into
        head.layers.0.self_attn.in_proj_weight after the real step), through train.main:
          train: refused: NonFinite: 1 of 31 trained tensors are not finite (head.layers.0.self_attn.in_proj_weight); eval_loss_after is nan: nothing is saved
          rc=5
          --out exists: False | listing: None
```
**2. The F-6 order.** Real 40 MB tmpfs: BEFORE printed `epoch 1/1 loss 0.847582 (1 steps, 55 s)` then
`train: refused: Refusal: the checkpoint needs 164 MiB and /tmp/ft1f/small/before has 40 MiB free`, rc=64, 58 s, an
empty `before/` left. AFTER printed only `train: refused: Refusal: the checkpoint needs 164 MiB and
/tmp/ft1f/small/after has 40 MiB free`, rc=64, 35 s (the model load), no epoch line, no `after/`. In the test,
`test_train_cli_refuses_a_full_disk_before_the_first_step` asserts `(rc, steps, files) == (64, 0, None)` and one
`disk_usage` probe; on the pre-fix code it read `(64, 1, [])`.

**3. test_summary twice, the set id, the CI view.**
```
pytest-summary: 32 passed in 252.33s (0:04:12)
pytest-summary: 32 passed in 248.29s (0:04:08)
1 files set=8b147318aa48
CI view (S0_01_VENUE unset): 20 passed, 12 skipped in 4.70s        (S0_01_VENUE=ci: 20 passed, 12 skipped in 4.50s)
```
(Two earlier runs are in section 7: `1 failed, 31 passed` and `2 failed, 30 passed`. Their failures are the
pre-existing red of section 6 and a race with the coordinator's concurrent builder fix; neither involves this change.)

**4. The mutation table.** 22 of 22 KILLED, 0 INVALID. The full table with the pasted kill lines is in section 4.
| Guard | Mutant | Red test |
|---|---|---|
| `--lr` finite and > 0 | check off / `isfinite` dropped / `>= 0` (T1-T3) | `test_train_refuses_optimizer_settings_outside_their_domain_at_parse_time` |
| `--weight-decay` finite and >= 0 | check off / `> 0` (T4, T5) | same |
| `--max-grad-norm` finite and > 0 | check off / `>= 0` (T6, T7) | same |
| `refuse_non_finite`: tensors / eval_loss_after / whole class | `bad = []` (T8) / `if False` (T9) / NaN only (T16) | `test_finiteness_guards_on_crafted_tensors` |
| `refuse_non_finite` called in `run()`; nothing written | `pass` (T10) / `mkdir` first (T17) | `test_train_cli_refuses_a_non_finite_trained_tensor_and_writes_nothing` |
| `main()` maps FloatingPointError to rc 5 | `except ZeroDivisionError` (T11) | `test_train_cli_refuses_a_non_finite_loss_without_a_traceback` |
| `load_checkpoint` refuses non-finite | `if False` (T12) | `test_load_checkpoint_refuses_a_non_finite_tensor_before_loading_it` |
| early `check_space` in `run()` | `pass` (T13) | `test_train_cli_refuses_a_full_disk_before_the_first_step` |
| `check_space` at save; the ancestor walk | `pass` (T14) / walk removed (T15) | `test_free_space_is_probed_without_writing_and_checked_again_at_save` |
| `check_served` / whole class / reads `noul` | `return out` (E2) / `v == v` (E3) / `+ []` (E4) | `test_evaluator_refuses_a_served_probability_that_is_not_finite` |
| `check_served` in `post`; `main()` maps to rc 5 | removed (E1) / `except ZeroDivisionError` (E5) | `test_evaluate_cli_refuses_a_non_finite_served_probability` |

**5. pyflakes and the separator bytes.**
```
$ /root/venv-agent-factory/bin/python -m pyflakes scripts/laya_ft/train.py scripts/laya_ft/evaluate.py tests/test_laya_ft.py
pyflakes rc=0 (no output)
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <each file written>
0 train.py, 0 evaluate.py, 0 test_laya_ft.py, 0 FT1-F-report.md, 0 in each of the five scratch scripts
```
