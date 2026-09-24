# FT1-F: the trainer refuses non-finite results and checks disk space before training (VERIFY-FT1 F-1, F-6; task #233)

Role: code-implementer (sandbox, Opus 5.5). PIN: the content of the files hashed below. Report:
`tasks/briefs/jev-laya/FT1-F-report.md` (write it incrementally from the start).

VERIFY-FT1 (`tasks/briefs/jev-laya/VERIFY-FT1-report.md`, F-1 and F-6, sections 2d and 2e) graded FT1
MERGE-READY-WITH-FOLLOWUPS and asked for two fixes BEFORE the GPU window, where the trainer runs on CUDA for the first time
and a lost run costs the owner's model server time. This is that follow-up increment. The other follow-ups (F-2, F-3, F-5,
F-7 beyond what this brief covers, F-8, F-9) go to an issue; do not fix them.

## Goal

1. **F-1: no non-finite result leaves the trainer or the evaluator as if it were fine.**
   - A run whose trained tensors are not all finite, or whose `eval_loss_after` is not finite, writes NO checkpoint (no
     `checkpoint.pt`, no `.tmp` left behind) and exits rc 5 with one stderr line naming what was non-finite.
   - A non-finite loss during training (today a raw `FloatingPointError` traceback, rc 1) becomes the same clean rc 5
     refusal (F-4's trainer half).
   - `--lr` must be finite and > 0, `--weight-decay` finite and >= 0, `--max-grad-norm` finite and > 0; anything else is a
     usage error before any model loads, the way `--epochs` is today (`ap.error`, rc 2).
   - `load_checkpoint` refuses a checkpoint with any non-finite tensor.
   - `evaluate.py` refuses to score when a served probability is not finite (fail loud, non-zero rc, a one-line reason),
     instead of counting it as an answer.
2. **F-6: the free-space refusal comes before training.** Check the disk right after `select_trainable` (the checkpoint's
   size is known then: the trainable tensors' bytes plus the existing margin), before the first step, and keep the check at
   save. A full disk costs nothing but the model load.

## Constraints

- Boundary: `scripts/laya_ft/train.py`, `scripts/laya_ft/evaluate.py`, `tests/test_laya_ft.py`. Touch nothing else; report
  adjacent defects, never fix them.
- Keep every existing behavior and exit code the tests pin; a guard that already exists is extended, not replaced.
- Tests go through the real entry points (`train.main([...])`, `evaluate.main([...])`) wherever the behavior lives there:
  - the argument domains need no model, so they run in CI;
  - a pure guard (a finiteness check over a state dict, the loader) gets a CI-runnable test on crafted tensors;
  - the end-to-end refusals use the real Laya model and are venue-gated exactly like the existing Laya tests (`laya_venue`).
  With `--lr inf` refused at parse time, reach a non-finite model another way: a fault you inject in the test (for example,
  a trained parameter set to NaN after a real step), never a stub of the guard itself.
- Each new guard has a negative control that fails for the exact reason, and a mutant that removes the guard must turn a
  named test red.
- FAKE strings only for anything secret-shaped. Never read `/root/.codiv/api.env`, never call codiv.ai or any network
  beyond 127.0.0.1.
- Other work shares this tree: VERIFY-JT2-R1 reads `scripts/jev_context.py`, `scripts/jev_locate.py`, `scripts/jev_echo.py`;
  the uncommitted JT3 files are `.claude/hooks/search-intercept.py`, `.claude/settings.json`,
  `scripts/install_session_hooks.py`, `tests/test_search_intercept.py`, `tests/test_session_hooks.py`. Never touch them, and
  never create or remove `.jev/intercept-off`.

## Evidence demands (in the report)

1. The F-1 command from the premise below, before and after: today rc 0 with a written checkpoint; after, a usage error
   (rc 2) for `--lr inf`, and your injected-fault run exits rc 5 with no checkpoint file in `--out`.
2. The F-6 order: a run whose `--out` cannot hold the checkpoint is refused before its first step. Show it on a real
   small filesystem (the sandbox runs as root: a 40 MB tmpfs, as the verifier did) and in a test.
3. `bash scripts/test_summary.sh tests/test_laya_ft.py` twice, both summary lines pasted, with the set id
   (`bash scripts/pc_suite.sh set-id -- tests/test_laya_ft.py`), and the CI view: the same file with `S0_01_VENUE` unset.
4. A mutation table: one row per new guard, the mutant, the test that turns red.
5. `pyflakes` on the three files, and `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` on every file you wrote (0 each).

## Standing rules

No commits, pushes, PRs, comments, bridge calls or other outward actions. Do not spawn subagents. Mutants run on scratch
copies only, one fresh copy per mutant, with `PYTHONDONTWRITEBYTECODE=1` (AF-AP-192); never stash, restore or check out a
tracked file in this tree. Use a short `--basetemp` (make its parent first). Kill by pid only. Your first action is to
re-measure the premise below; stop and report CONTRACT-INVALID on a mismatch.

## PREMISE — MEASURED at authoring (2026-09-24 18:3xZ, /home/user/agent-factory at local HEAD 2b2aa18)

```
$ for f in scripts/laya_ft/train.py scripts/laya_ft/evaluate.py scripts/laya_ft/common.py tests/test_laya_ft.py; do echo "$(git rev-parse --short=12 HEAD:$f) $f"; done
8d03bef2a83b scripts/laya_ft/train.py
96b0a2024012 scripts/laya_ft/evaluate.py
63f15afdb090 scripts/laya_ft/common.py
20409b3606f5 tests/test_laya_ft.py
$ /root/venv-laya-probe/bin/python scripts/laya_ft/train.py --dataset <scratchpad>/vft1/ds --labels docs/research/findings/laya-ft-labels/2026-09-24-openjev/labels.jsonl --out /dev/shm/ft1f-premise --mode head --device cpu --batch-size 4 --epochs 1 --limit 4 --lr inf --eval-loss --threads 2
epoch 1/1 loss 0.847582 (1 steps, 50 s)
{"checkpoint": {"bytes": 105002916, "file": "checkpoint.pt", "sha256": "1b8d1d4e7ba5e2e63c3e14139a4e1d383173fae32ccc9fe6d761307ff1db33f1"}, "device": "cpu", "eval_loss_after": NaN, "eval_loss_before": 0.807124137878418, "examples": {"by_question": {"ap.violates_row": 0, "v1.blocking": 2, "v1.finding_class": 2}, "n": 4}, "guards": {"act_head_unchanged": true, "encoder_unchanged": true, "model_dir_unchanged": true}, "per_epoch_loss": [0.8475820422172546], "steps": 1, "trained": {"parameters": 26248193, "prefixes": ["head", "scorer", "type_emb"], "tensors": 31}, "wall_seconds": 56.8}
rc=0
$ (the saved checkpoint, loaded with torch and checked with torch.isfinite per tensor)
/dev/shm/ft1f-premise/checkpoint.pt tensors 31 non-finite 31
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
$ bash scripts/test_summary.sh tests/test_laya_ft.py 2>&1 | tail -2; bash scripts/pc_suite.sh set-id -- tests/test_laya_ft.py
pytest-exit: 0
pytest-summary: 22 passed in 155.59s (0:02:35)
1 files set=8b147318aa48
```

`<scratchpad>` is `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad` (VERIFY-FT1 built the dataset
there; its `manifest.json` names the dataset sha d7cd9b49..., and you may rebuild it with `build_dataset.py` if it is gone).
