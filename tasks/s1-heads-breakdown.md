# Task breakdown — task #441: the first S1 training (a frozen RWKV-7 with contrastive heads)

STATUS: 2026-10-02 09:0xZ — AUTHORED from the owner's rulings D-125, D-126, D-127 (1) and D-133, and the step-3 plan's
decision 5 (`tasks/laya-s3-breakdown.md`). No new seed: the rulings are the spec, as for step 3. The increments are
registered as tasks #470 to #473 before any build; task #441 is the run itself (S4-4).

## The owner's words

- D-125 (2026-10-01 12:2xZ): "Maybe we can get away with [RWKV] on its own"; the same morning, on the method: "Might be
  worth leveraging the clm training methodology".
- D-126 (15:4xZ): "retire it once it beats the [0.809] rule"; "Everything else can be RL'd, can't it? Using the CLM ...
  version of the training".
- D-127 (19:5xZ): "It runs on CPUs. That means we can train it on the GPU to leverage the speed. And then once we have
  ... the final weights, we freeze those and then we load that onto the sandbox or in the PC". Task #441 (one role, the
  S1 injection decision) is unchanged by its per-role states.
- D-133 (2026-10-02): the same model later also emits a few tokens (task #467); its design note puts this run first
  (`docs/research/findings/s1-micro/S1-MICRO-DESIGN.md` §8).

## What exists (measured 2026-10-02 09:0xZ)

- **The data.** The S1 build at 5be8cc0c (summary `docs/research/findings/s1-train/2026-10-01-dataset-summary.json`) and
  its RWKV view (task #444; the guards of task #460) over the 2026-10-01 export (export id 2026-10-01T18:32:15Z, code
  e8cccfb8a8edf9fe, 390 files): 1,091 rows in 39 transcripts (the main thread 625, 38 subagent transcripts 466). Train
  871 rows (513 yes; always-yes 0.589, the kind rule 0.786); held-out 220 (147 yes; always-yes 0.668, the kind rule
  0.809, 178 of 220). The view's output sits in the session scratchpad; it holds injected text and stays out of git.
- **Where the kind rule fails.** Held-out by kind (no / yes): edit-snapshot 48 / 17, system1-context 24 / 111,
  filepacks 0 / 11, wiki-context 1 / 7, search-intercept 0 / 1. Its 42 errors are the 17 useful edit snapshots, the 24
  useless skill lines and one wiki excerpt: a model beats the rule only by telling rows of one kind apart. 140 of the
  220 sit in the main thread, late in it.
- **What a pass must read.** Up to each transcript's last row: 85,639,395 characters (60,753,072 in the main thread),
  about 28.5 million tokens at the export's 3.01 bytes a token (the rendered text's own ratio is not measured). The
  candidates: 1,265,959 characters in 1,091 rows, 361 distinct texts, median 1,230 characters.
- **RWKV-7 0.4B on the 3090** (2026-09-24 window 2, `docs/research/findings/j2b-variants/rwkv7-g0/2026-09-24-window2/`;
  `~/venv-rwkv-b`: torch 2.7.1+cu128, transformers 4.53.3, fla 0.3.0; bf16): 32,768 tokens in 0.64 s, 61,440 in 1.17 s
  (peak 10,474 MiB); a question read from a copied state in about 0.04 s; a prefix then a suffix give the same argmax as
  one whole forward (largest logit difference 0.1875). `scripts/gpu_window.sh` (D-078, D-081, D-088) stops the `qwen`
  unit, runs a jobs file, and always starts the unit again. It has not run since the unit became SGLang (2026-10-02).
- **RWKV-7 0.4B on the CPU** (`docs/research/findings/s1-train/RWKV-CPU-2026-10-01.md`): llama.cpp build 0c1e570 and the
  Q8_0 file 52294392…: about 333 tokens a second on 3 sandbox threads, a cosine of at least 0.998 against the official
  package's fp32 at every position. That build and those files went with the container (no llama.cpp binary on this
  machine, 2026-10-02 08:0xZ). The PC: an AMD Ryzen 5 5600X (6 cores, 12 threads; AVX2, FMA, F16C), gcc, g++ and
  cmake, no nvcc; its CPU speed for RWKV-7 is not measured.
- **The PC holds the same export** (its manifest: export id 2026-10-01T18:32:15Z, code e8cccfb8a8edf9fe; the per-file
  sha256 not yet checked there) and the pinned checkpoint in its Hugging Face cache.
- **The CLM method** (`docs/research/findings/CLM-AGENT-BEACON-READ-2026-09-24.md` C1, C4, C8): a dual encoder over a
  frozen LLM with last-token pooling; a state head and an action head (MLP, width 1536, depth 3, LayerNorm, to 512
  dimensions); score = exp(logit_scale) × cosine; bidirectional in-batch InfoNCE with same-group codes masked,
  logit_scale from log(1/0.07); a yes/no question is a softmax over two candidate texts.

## Pinned decisions (with the rejected alternative)

1. **The question and the data are frozen.** `s1.inject` on the view's rows, with the S1 build's labels and split
   (decisions 1 to 3 of the step-3 plan): the build at 5be8cc0c and the view's output by its sha256, both written into
   the pre-registration. Rejected: a rebuild on the session as it is now (the held-out rows would move after their
   baselines were read; a new build is a new pre-registration).
2. **The reading pass runs on the 3090 in a D-088 GPU window.** The frozen RWKV-7 0.4B (the pinned checkpoint, bf16,
   fla, `~/venv-rwkv-b`) reads each of the 39 transcripts' rendered streams once, in order, and carries its state across
   the whole transcript. Each event's block is tokenized on its own, as a live reader reads each event when it arrives;
   the tokens are made before the window, on the CPU. The window's GPU work is about 15 minutes at the measured speed.
   Rejected: llama.cpp on the PC's CPU (the serving runtime, so its features would serve as they are; but about 8 to 12
   hours if its 6 cores read two to three times as fast as 3 sandbox threads, not measured, while the owner's services
   share those cores); llama.cpp on the sandbox's CPU (about 24 hours, longer than a container is sure to live); a CUDA
   build of llama.cpp (no nvcc on the PC, and its kernels differ from the CPU's, so it needs the same comparison as fla);
   a short window per row in place of the whole stream (not how the live reader works; decision 6 measures it).
3. **The features per row** (1,024 dimensions each: the final hidden state after `ln_out` at the last token read):
   `s`, the session state's readout at `state_end`; `c_ctx`, the readout after the candidate is read from a COPY of that
   state (the copy is dropped, and the stream goes on from the original); `q_ctx`, the readout after a fixed question
   prompt read after the candidate on the same copy (D-127 (2): a role's prompt read at the decision end). Per distinct
   candidate, from the initial state: `c_free` and `q_free`. Rejected: inner layers (more choices to tune on 871 rows);
   pooling over the candidate's tokens (CLM uses the last token, and so does a live readout).
4. **The heads train on the CPU**, and a 5-fold time-blocked cross-validation on the TRAINING rows picks one
   configuration: (A) CLM's pair, a state head over `s` and an action head over `c_free` into one space, trained with
   bidirectional in-batch InfoNCE (rows with the same candidate masked as one group) plus a yes/no term on each row's
   own pair, so its "no" rows are hard negatives; (B) a probe over `c_ctx`; (C) a probe over `q_ctx`. Each has a small
   grid that the pre-registration lists. Rejected: choosing on the held-out rows (they are scored once, by the one
   chosen configuration); CLM's sizes as they are (9.4 million parameters a head against 871 rows); tuning RWKV first
   (D-125: only if this falls short).
5. **One evaluator and the bar.** One evaluator scores the chosen model and every baseline (always-yes, the kind rule
   taken as each kind's majority label on the training rows, word overlap between the candidate and the step) on the 220
   held-out rows, at a threshold fixed on the training rows' out-of-fold scores. PASS: accuracy above 0.809 AND a
   one-sided exact McNemar test against the kind rule on the same rows gives p < 0.05. NOT SHOWN: above 0.809 with
   p ≥ 0.05. FAILED: 0.809 or less. Reported beside it: AUC, balanced accuracy, accuracy per kind, the confusion counts.
   The numbers live in one machine-read block of the pre-registration; the evaluator reads them from there and records
   its sha256. Rejected: accuracy alone (on 220 rows its standard error is about 2.7 points, so a few rows either way
   is noise); AUC as the bar (the owner's bar is the rule's accuracy).
6. **Controls**, each through the same evaluator, with the expected outcome and the void condition written before the
   run: labels shuffled within each kind on the training rows (the model can then learn only the kind, so the run is
   void if it beats the kind rule with p < 0.05); the chosen configuration without the session state (`c_free` or
   `q_free` in place of `c_ctx` or `q_ctx`; a fixed vector in place of `s`): what the state adds; a readout from a fresh
   state over only the last 2,048 tokens before each row: what the whole stream adds over a short window. Rejected: no
   controls (a pass without them cannot say what was learned).
7. **Train on the features that serve (D-126)** by a measured comparison. The serving runtime is llama.cpp on the CPU
   (task #448). After the run, the 22 transcripts whose stream before their last row is at most 500,000 characters (103
   rows, 24 held-out; 5,323,915 characters) are read again with llama.cpp 0c1e570 and the Q8_0 file on the sandbox's
   CPU (about 1.5 hours), from the same token ids; the readouts' cosine per row and the chosen heads' decisions on both
   feature sets are compared, and llama.cpp's own tokenizer is checked against those ids. The pre-registration names
   the agreement bar. Rejected: serving fla on the GPU (D-126: the CPU is the live home); reading the whole history
   twice (about 24 hours in the sandbox).
8. **Session-derived data stays out of git.** The token files and the features sit under `.jev/s1-train/` (ignored) on
   the PC and in the sandbox; the commits carry code, counts, digests and metrics. Features are made only from verified
   inputs: the export's per-file sha256 against its manifest, and each rendered stream's sha256 against the view's
   summary.
9. **Determinism, stated per part.** bf16 GPU kernels are not bit-exact, so two reads of two transcripts are compared
   to a tolerance the pre-registration states; the head training on the CPU is seeded and repeats byte for byte; the
   evaluator's record repeats byte for byte from the same features.

## Increments (one increment = code + deterministic test + commit; every count pasted from the test summary)

| # | Increment | Boundary | Acceptance | Negative control |
|---|---|---|---|---|
| S4-1 (#470) | The pre-registration: the frozen inputs by sha256, the question prompt verbatim, the configurations and their grids, the cross-validation, the threshold rule, the bar and its test, the controls with their expected outcomes and void conditions, the comparison's bar, the next step after each outcome; committed before any feature exists | `docs/research/findings/s1-train/PREREG-441.md` | every number in it comes from a run or a file named beside it; it is on origin before the window opens | its machine-read block is the only copy of the bar: the evaluator refuses to run without it |
| S4-2 (#471) | `scripts/s1_train/read.py`: verifies its inputs as `view.py` does, renders each transcript with `render.py` and checks the rendered sha256 against the view's summary; a `tokens` step (CPU) and a `read` step behind one backend interface: `fla` (the GPU pass; torch imported only inside it) and a deterministic fake for the tests (the `llamacpp` backend is S4-5's); writes the features in a standard-library format (raw float32 and a JSON index with per-array digests: no numpy, which CI and the sandbox's main Python lack) and a manifest (counts, digests, the model and tokenizer identity, timings); resumable per transcript | `scripts/s1_train/read.py`, `tests/test_s1_train_read.py` | with the fake backend: each readout lands at its row, the state copy leaves the stream unchanged, a resumed run equals a whole run byte for byte; the `fla` backend first runs in the window's smoke job, never in CI | a rendered sha256 that differs from the view's is refused; a `state_end` that is not a block start is refused; a thinking block never reaches the tokens (render's rule, checked on the token stream) |
| S4-3 (#472) | `scripts/s1_train/heads.py` (the configurations, the cross-validation, the training) and `scripts/s1_train/evaluate.py` (the one evaluator: the threshold, the metrics, McNemar, the controls, the record) | those two files and their tests | on synthetic features with a planted signal the chosen model passes the bar; with no signal it fails and the shuffled control reads chance; two runs give byte-identical records | a held-out row reaching the cross-validation is refused; a feature file whose digest is not the reading manifest's is refused; any second held-out evaluation is written as exploratory, never as the result |
| S4-4 (#441) | The run: the tokens on the PC's CPU; a GPU window with a smoke job (fla against llama.cpp's readouts of one short text), then the read job; the features' digests; the heads, the controls and the one evaluation on the CPU | `docs/research/findings/s1-train/` (the record), `.jev/s1-train/` (not in git) | the record says PASS, NOT SHOWN or FAILED by the pre-registration's rule, every number from the evaluator's output; after the window the `qwen` unit answers the request shapes its clients send (AF-AP-260), not only `/v1/models` | the controls of decision 6, as pre-registered |
| S4-5 (#473) | The serving-feature comparison of decision 7 on the sandbox's CPU: the `llamacpp` backend of `read.py` (llama.cpp 0c1e570 built from its pinned sdist; the Q8_0 file built again and checked against its 2026-10-01 sha256) reads the same token ids | `scripts/s1_train/read.py` (the backend), `docs/research/findings/s1-train/` | the cosine, the decision agreement and the token check against the pre-registered bar; NOT run in CI | a model file whose sha256 is not the pinned one stops the comparison |

Order: S4-1; then S4-2 and S4-3 in parallel (disjoint files); then S4-4 in a window (D-088: no PC lane live); then
S4-5. The micro-output (task #467) reads the same state and is scored by the same evaluator later.

## NOT built (declared)

- Serving the heads in the System-1 hook, and RWKV-7's live home (task #448).
- Per-role states (task #453); tuning RWKV's state or weights (D-125, D-127: only if this run falls short).
- More data (D-126 item 3: other projects' histories and the Hermes logs, only if this run shows the data is thin).
- The 0.1B model; the PC's CPU speed for RWKV-7 (task #467 step 2).
