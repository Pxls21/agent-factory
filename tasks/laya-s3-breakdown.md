# Task breakdown — step 3 of D-123: the Laya data path and the first training

STATUS: 2026-10-01 10:1xZ — AUTHORED from the owner's rulings D-123 item 10 (step 3) and item 2, D-124, D-100 (1), D-086,
D-078 (1) and D-118 (1). No new seed: this extends the Laya fine-tune tooling (FT1, DSV2, K265) under the program of
`seeds/seed-laya-j1-v1.yaml`, and the rulings are the spec. The increments are registered as tasks #438 to #441
before any build.

## The owner's words (transcript 2026-10-01 02:26:19Z)

"build the [Laya] data paths and its first training ... the data path should be laid out already ... The output
styles should be set up. I don't know whether you set up the output styles yet to make sure that you always use
labels ... Make sure the chat history and everything is laid out properly that way it'll be easy to train ...
[Laya] doesn't need that much data". D-100 (1) names why the output styles matter here: structured requests in the
coordinator's output are clean, pre-labeled training data for System-1 models.

## What exists (measured 2026-10-01 10:1xZ)

- The trainer, the evaluator and the window fit: `scripts/laya_ft/train.py` (`--mode head|full`, `--device
  cpu|cuda`), `evaluate.py`, `fit.py` (K265: one fit for training and serving; it never cuts the `chunk` field).
  One checkpoint was ever trained (`ckpt-head-w1`, the GPU window of 2026-09-24); it was rejected on every KC-J3
  line, because its teacher labels were below the baseline. Dataset version 2 (6,196 rows, 5,301 labels from our
  recorded answers, task #251) was never trained on.
- S1-RATE (task #295): 1,069 scored injections in this session's transcripts at the first build (10:3xZ). The
  survey's first figure, 2,124, read every transcript twice (AF-AP-254); its rates hold (rel 2 or 3 on 59.7%; by
  source, skill lines 78% and edit snapshots 18%). `scripts/s1_scores.py` pairs each injection with its score; the injection text is in
  `.jev/injections.jsonl` (3,728 rows, sha256 equal on all).
- SYNTH1 (`scripts/s1_synth.py`, task #308, closed 2026-09-28): Laya-format rows for `skill.governs` and
  `skill.helps`, the same 0-3 scale; its labels failed their validator (decision 1), so its candidate set and
  validator stay an evaluation harness. `scripts/laya_ft/common.py` refuses its rows (task #322).
- The relay log (`.jev/relay/`): OpenJev's keep or drop answers on 72 pruning states (teacher labels only).
- The chat history: the daily scrubbed digests in `transcripts/` (conversation text only) and the session stream
  (`scripts/session_export.py`, task #252: every call and result in order), shipped to the PC once
  (`/home/rocco/jev-data/session-export-2026-09-25-r1`, the transcripts up to 2026-09-25 12:4xZ). Issue #78's two
  pre-export items (R1-F-1, AF-AP-213) never landed, so no later export ran.
- The output styles (`.claude/output-styles/`) mention no label, no stack and no box.

## Pinned decisions (with the rejected alternative)

1. The first training target is the System-1 injection decision (task #297): should this injected context be shown
   before this step? The state carries the step's INTENT as well as its input: the owner's last prompt (`task`), the
   coordinator's text right before the call (`intent`), the call's tool and input (`step`), the context's kind and
   the context itself (`chunk`; `fit.py` never cuts it, and cuts the longest other field first). Rejected: the tool
   input alone. SYNTH1's validator (task #308, ledger 2026-09-28 14:0xZ) gave two labelers of different families only
   the prompt or the tool input and the section; both missed the live scores (OpenJev rel exact 0.27, the local Qwen
   0.38, against a bar of 0.75), which points at the input, not the labeler. Also rejected: dataset version 2 first
   (its signal is the finding class, and the owner's priority is System 1, D-123 item 2); the relay's pruning labels
   first (teacher labels only, 72 states).
2. One question, `s1.inject` (noul): yes when the live score was rel 2 or 3, no when it was rel 0 or 1. Every
   injection kind (a skill section, an edit snapshot, a file pack, a wiki excerpt, a search answer) takes it, with the
   kind in the state. Rejected: SYNTH1's four-way `skill.governs` and `skill.helps` (the 2026-09-24 head checkpoint
   left Laya's choice path unchanged, cause still open, while its yes/no path moved; and SYNTH1's own labels failed
   their validator, so there are no synthetic rows to share a question with); `use` as the target (it depends on what
   the step went on to do, which the state cannot hold).
3. The held-out split is by TIME, per kind: each kind's newest fifth (the cutoffs are written in the manifest), so a
   kind that began late (the file packs, 2026-09-30) is on both sides. A (step, context) pair that is in both splits leaves the training split. Rejected: a random split
   (the injections of one step would sit on both sides).
4. A row holds the step's tool INPUT only (never a tool result, never a thinking block). It is scrubbed with
   `transcript_export.scrub_payload` and checked with `scripts/known_values_check.py` before it leaves the sandbox.
   The rows and labels stay out of git (`.jev/laya-ft/`, ignored); the build's summary (counts, cutoffs, digests,
   baselines; no text) is committed, built at a pushed commit. Rejected: committing the rows (they are session text; the committed digests
   follow the exporter's own policy).
5. Training runs on the GPU, in a window the owner approves (D-078 (1): "CPU is unrealistic"; each window needs the
   owner's say-so). The acceptance lines are written before the run: Laya against always-yes (today's behaviour,
   every injection fires), the source-kind prior and a word-overlap score, on the held-out rows.

## Increments (one increment = code + deterministic test + commit; every count pasted from the test summary)

| # | Increment | Boundary | Acceptance | Negative control |
|---|---|---|---|---|
| S3-1 (#438) | `common.py` learns the `s1.inject` question and the `injection` row kind; `build_s1.py` builds the S1 dataset from the scores, the transcripts and the injections | `scripts/laya_ft/common.py`, `scripts/laya_ft/build_s1.py`, `tests/test_laya_ft_s1.py`, SYNTH1's refusal test | a fixture session gives the same rows and labels twice, byte for byte; the real run's counts land in the findings | an unknown kind is refused; an injection whose sha256 does not match its score row is refused; a planted fake key is scrubbed; a pair in both splits leaves the training split |
| S3-2 (#439) | The chat history laid out: issue #78's two pre-export items, then the export from the last offsets to now, shipped and checked on the PC | `scripts/session_export.py`, `scripts/transcript_export.py`, their tests | export rc 0, gate 0, the ship sha-checked, the PC-side known-values check NO HIT | R1-F-1's token-like NAME; the AF-AP-213 canary transcript |
| S3-3 (#440) | The output styles name the labels and the box (D-100 (1), D-123 step 3) | `.claude/output-styles/*.md`, `sandbox-kit/output-styles/`, their provenance, the manifest | each style carries the labels line; the mirrors and the manifest pass | none (a docs change) |
| S3-4 (#441) | The first training, pre-registered, and its evaluation | `docs/research/findings/laya-ft-s1/` (the pre-registration first, then the run's record) | Laya beats every pre-registered baseline on the held-out rows, or the run is reported as failed | the baselines run through the same evaluator |

Order: S3-1, then S3-3; S3-2 can run beside them; S3-4 needs S3-1 and the owner's training window.

## NOT built (declared)

- The max-relevance examples (task #432, D-123 item 2): after S3-1, on a sample, if the first training shows the
  data is thin.
- The relay's pruning labels as a Laya question (a local pruner): later; they are teacher labels only.
- Serving a trained head in the System-1 hook (the second half of task #297): after S3-4 passes.
