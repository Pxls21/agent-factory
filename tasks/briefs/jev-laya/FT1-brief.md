# FT1 — the Laya fine-tune tooling: dataset, teacher labels, trainer, evaluator (task #233; D-075, D-078)

LANE: ft1 (sandbox; agent `code-implementer`, Opus 5.5, in the SHARED tree, no worktree isolation). Do NOT spawn subagents.
Report: `tasks/briefs/jev-laya/FT1-report.md` (write it incrementally from the start). PIN: the local HEAD at dispatch; re-measure
the premise block below first and stop on any mismatch.

## Why

The owner keeps Laya in the system and wants it trained (D-075): "make sure we don't abandon Laya". J2 and J2c
(`docs/research/findings/J2-SIGNAL-PROBE-2026-09-24.md` sections 1-6) show Laya below the plain baselines on our two labeled
question types, and show the input was part of the problem: with the WHOLE finding, Haiku reaches 0.60 accuracy and 4 of 7
blockers where Laya reaches 0.17 and 2 of 7. The owner approved codiv.ai's OpenJev as the teacher that generates the training
data (D-078) and ruled that training runs on the GPU in a window with no lanes live (D-078). This lane builds the TOOLING and
proves it on small real runs; the coordinator runs the large labeling job and the GPU training window.

## Boundary (CREATE only these)

`scripts/laya_ft/__init__.py`, `scripts/laya_ft/build_dataset.py`, `scripts/laya_ft/teacher_label.py`,
`scripts/laya_ft/train.py`, `scripts/laya_ft/evaluate.py`, `scripts/laya_ft/common.py` (shared helpers, optional),
`tests/test_laya_ft.py`, and your report. READ anything else. Report adjacent defects; never fix them.

## Pinned decisions (a conflict with the tree is a STOP-and-report)

- **D-1 Reuse Laya's own training pieces (vendor-first).** Sequences from `laya.common.build_sequence` with the checkpoint
  config's `max_len` and `head_max_len` (as `Agent.system_one` does); batches from `laya.common.collate_items` with a
  per-item `"target"` distribution; the loss is the NEGATED `laya.common.proper_reward` (the strictly proper scoring rule the
  model was trained with) over the softmax of the model's logits, masked by `marker_mask`. Never invent a different objective.
- **D-2 Whole text, masked, scrubbed.** Inputs are whole findings and whole incident entries, never ledger titles. Class words
  are masked exactly as `docs/research/findings/j2c-fulltext/j2c.py` does (`_mask`: J2's MASK plus a dropped parenthesised
  qualifier; a table row keeps only its title cell). Every string that leaves the machine passes `transcript_export.scrub`.
  The v1 ledger state's `disposition` field is never an input (AF-AP-189).
- **D-3 Held-out rows never train.** Every row of `docs/research/findings/j2-v1-probe/sample.json`,
  `docs/research/findings/j2c-fulltext/sample.json` and `docs/research/findings/ap-hawk-probe/sample.json` is excluded from
  the dataset by source identity (report path + finding id; incident heading line), and the builder PROVES it (a count of
  excluded rows equal to the samples' sizes, and a test that fails if one leaks in).
- **D-4 Resolve the tree once.** The builder reads committed sources at ONE resolved commit (`rev-parse --verify HEAD^{commit}`,
  every later read names that sha; AF-AP-175) and records it in its manifest.
- **D-5 The teacher client is resumable and polite.** Append-only JSONL keyed by (item id, question id); a rerun skips done
  keys; at most 60 requests per minute (codiv's limit), retries on 429/5xx with backoff; the key is read from
  `/root/.codiv/api.env` in process (never argv, never printed, never logged); an ordinary User-Agent (Cloudflare refuses
  Python's default with 403 "error code: 1010"); `--limit N` for smoke runs; usage totals (requests, input tokens) at the end.
  The wire format is the one `docs/research/findings/j2b-variants/openjev_j2.py` uses (POST `/v1/systemone`, model
  `openjev-latest`, `{state, questions}`); each answer's full probability distribution is stored as the soft target.
- **D-6 Question types.** (a) `v1.finding_class`: one `choice` over the six classes, criteria = `CLASSES` from
  `docs/research/findings/j2-v1-probe/v1_probe.py`; (b) `v1.blocking`: one `noul` ("Does this finding block the merge: a
  contract break reproduced through the real path, or a contract that is itself wrong?"); (c) `ap.violates_row`: one `noul`
  per (incident, candidate row), the candidates being the lexical top 16 exactly as `ap_probe.py` ranks them.
- **D-7 Trainer modes and determinism.** `--mode head` (encoder parameters frozen) and `--mode full`; `--device cpu|cuda`;
  bf16 autocast on CUDA; AdamW; a fixed seed; the act head untouched by the loss. Output: `checkpoint.pt` (the state_dict of
  what was trained) and `train-manifest.json` (dataset sha256, base model revision, every hyperparameter, per-epoch loss, device,
  torch version, wall time). Nothing is written into the Hugging Face cache.
- **D-8 The evaluator speaks J2's metrics.** It loads the base model plus a checkpoint in process and answers the held-out
  samples with the J2 question shapes: `v1` (titles) and `v1_full` (J2c whole findings): accuracy, balanced accuracy,
  blocking split, BLOCKER recall; `ap`: top-1 and top-3 over the lexical 16; printed beside the J2 baselines (majority,
  heuristic, lexical) with the KC-J3 verdict line; also `ece_score` (laya.common) for calibration. A run with NO checkpoint
  must reproduce the base model's committed J2/J2c numbers within rounding (the evaluator's own positive control).

## Evidence demands

1. Premise: re-measure the block below; stop and report on any mismatch.
2. Tests (`tests/test_laya_ft.py`, deterministic, run twice, pasted from `scripts/test_summary.sh`): the builder's determinism
   (two runs, byte-identical output) and D-3 exclusion (a planted held-out row is refused); the masking (no class word
   survives) and the scrub (a FAKE secret never reaches a request body); the teacher client's resume, rate limit, retry and
   key handling against a local stand-in HTTP server (a unit-test double for the network only; the live API is exercised in
   item 3); the trainer's loss on the REAL model on CPU: three steps on a fixed four-item batch lower the loss (an overfit
   check), and a saved checkpoint loads into a fresh model and changes its outputs; `--mode head` leaves every encoder
   parameter bitwise unchanged.
3. Live smokes, pasted: `teacher_label.py --limit 5` against codiv (real requests; show the stored distributions' shapes and
   the usage line); `build_dataset.py` on the real tree (the manifest: counts per source, exclusions, sha256); `train.py
   --mode head --device cpu` on 16 items for one epoch; `evaluate.py` with no checkpoint on the v1 sample (the positive control).
4. Mutants on scratch copies only, each red on a named test: drop the D-3 exclusion; train the encoder in head mode; use the
   wrong loss sign; skip the scrub; drop the resume skip.
5. pyflakes on every new file; `python3 scripts/no_laya_in_gates.py` (the new scripts import laya; they must not be gate
   files); the separator check below on every file you write.
6. The report: files, pasted counts, the smokes, the mutant table, the dataset's size by source, deviations, NOT-done.

## Standing rules

No commits, no pushes, no PRs, no GitHub writes, no bridge calls. The ONLY third-party API allowed is codiv.ai through your
teacher client, for the `--limit 5` smoke only (the coordinator runs the full labeling). Never print the key or any real
secret; test secrets are FAKE strings (QZJ8... and X4Z9... style). Never stop the Laya server on 127.0.0.1:47411. The sandbox
venv for torch and laya is `/root/venv-laya-probe` (CPU torch); the project venv `/root/venv-agent-factory` has pytest; no
pytest-xdist (never pass `-n`); a short `--basetemp` with its parent created first. Other lanes: JT1-R1 edits `scripts/jev.py`,
`scripts/hiccup_scan.py` and their tests; VERIFY-JT3 reads `.claude/hooks/search-intercept.py`; an OpenJev run is writing
`docs/research/findings/j2b-variants/openjev/`: never touch those. Never create or remove `.jev/intercept-off`. Check every file
you write with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`.

## PREMISE — MEASURED at authoring (2026-09-24 15:2xZ, /home/user/agent-factory)

```
$ /root/venv-laya-probe/bin/python -c "import laya,transformers,torch;print('laya', getattr(laya,'__version__','?'), 'transformers', transformers.__version__, 'torch', torch.__version__)"
laya 0.3.5 transformers 5.17.0 torch 2.14.0+cpu
$ grep -n -E "^def (collate_items|build_sequence)|has_target|\"target\"" .../laya/common.py
49:def build_sequence(
181:    target = batch["target"].clone()
188:        y = batch["target"][idx[-1], 1]
247:def collate_items(batch, pad_id: int):
257:    has_target = any("target" in it for it in items)
258:    target = torch.zeros((n, kmax), dtype=torch.float32) if has_target else None
266:        if has_target and "target" in it:
267:            target[i, : len(it["target"])] = torch.tensor(it["target"], dtype=torch.float32)
$ grep -n "def forward" .../laya/common.py
105:    def forward(self, input_ids, attention_mask, marker_pos, marker_mask, qtype, detach_encoder: bool = False):
$ grep -n "^def \|^class " .../laya/common.py   (excerpt)
89:class DecisionModel(nn.Module):
150:def proper_reward(
197:def ece_score(conf: np.ndarray, correct: np.ndarray, bins: int = 15) -> float:
247:def collate_items(batch, pad_id: int):
$ grep -n -E "^CLASSES = |^BLOCKING = |^MASK = " docs/research/findings/j2-v1-probe/v1_probe.py
25:CLASSES = {
33:BLOCKING = {"BLOCKER", "CONTRACT-DEFECT"}
34:MASK = re.compile(r"\b(BLOCKER|FOLLOW-UP|INFO|UNVERIFIED|CONTRACT-DEFECT|KNOWN|BLOCKING|NON-BLOCKING)\b", re.I)
$ sha256sum docs/research/findings/j2-v1-probe/sample.json docs/research/findings/j2c-fulltext/sample.json docs/research/findings/ap-hawk-probe/sample.json
b1cf7867f5995280f1c9298fa48e024b3039ee50ddca1e3626367717c9f27fc9  docs/research/findings/j2-v1-probe/sample.json
af469599e3e1054241c75f7b81eec5ae0214136d88fbbbbf6b8701e404b44df3  docs/research/findings/j2c-fulltext/sample.json
c07c581ad74201e19efe8b9da61eedd4a4cfcc81c3c10f7036ba20da3aaa2044  docs/research/findings/ap-hawk-probe/sample.json
$ git ls-tree -r --name-only HEAD -- tasks/briefs | grep -c -E "/VERIFY-[^/]*-report\.md$"
91
```

The laya package path above is `/root/venv-laya-probe/lib/python3.11/site-packages/laya`. The model snapshot is under
`/root/hf-laya-probe` (revision `1c5edc17a7acd8701df6fc341c0d179f1c62c982`, subfolder `typed-decisions`; config
`rl_agent_config.json`: `max_len` 1024, `head_max_len` 256). On the owner's PC the same revision sits under `/home/rocco/hf-laya`
with a CUDA torch in `/home/rocco/venv-laya`; that is where the coordinator will train.
