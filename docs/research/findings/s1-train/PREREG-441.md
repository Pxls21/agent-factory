# Pre-registration — task #441: the first S1 training (a frozen RWKV-7 with heads)

STATUS: PRE-REGISTERED 2026-10-02 09:1xZ by the coordinator (task #470, S4-1 of `tasks/s1-heads-breakdown.md`), before
any feature exists. The plan and its rejected alternatives are in the breakdown; this file fixes what the run is scored
by. Amendments before the GPU window opens are dated here with their reason and pushed before the window. After the
features exist, nothing in §4 (the bar), §5 (the controls) or the grid of §3 changes; any other deviation is reported
in the run's record as a deviation.

## 1. The frozen inputs

| Input | Identity |
|---|---|
| The S1 build | commit 5be8cc0c7329a4ffdbed65274032790988f81211; its committed summary `docs/research/findings/s1-train/2026-10-01-dataset-summary.json`, sha256 ce04b35c8cd43b37caabe8f968d487a3d7174cdb978a13b6ea627f47e6fec4db |
| The view (task #444, version s1-view-v2, render s1-render-v1) | `view.jsonl` sha256 29c5207de39d8f8b5c59b769ed2d56c577566189bb1d05c738ff714e09587a66; its `summary.json` sha256 3c6cddc5ea182331ccbcc70d10e6ca93436bbfe66e4b298c9a067c0ab4bd917c; 1,091 rows found of 1,091, none dropped; made by `scripts/s1_train/view.py` sha256 9ca2bece43af9a9f… (the copy before task #460's B1 repair, which changed only where `--out` may write) |
| The export | export id 2026-10-01T18:32:15Z, code e8cccfb8a8edf9fe, 390 files; `manifest.json` sha256 ff049420ec74d5b044f84df7f2a75a265f01540836b4283986b626003bf060f6 |
| The model | `RWKV/RWKV7-Goose-World2.9-0.4B-HF` at e94655a9fad2c8da9f25aba575d8f0fdedc05931, `model.safetensors` sha256 e162387e439dfa3387a0ca7da61638749d00c9862b8cc0192ae5d366c8c1a524; bf16 |
| The reading runtime | the PC's `~/venv-rwkv-b` (torch 2.7.1+cu128, transformers 4.53.3, fla 0.3.0, triton 3.3.1), on the 3090 |
| The serving runtime (the comparison, §6) | llama.cpp build 0c1e570 as vendored in llama-cpp-python 0.3.36 (sdist sha256 832db0699007f1be95a7e41ef12e88926b02ba836461e36a36372db2760c1a2e), CPU; the Q8_0 file sha256 52294392f54da107a50bf7cfb2ef189cd5892beb0ddfa88f969f7fcf77e449fa |

The rows: train 871 (513 yes), held-out 220 (147 yes); labels and split are the build's, never recomputed. Held-out by
kind (no / yes): edit-snapshot 48 / 17, system1-context 24 / 111, filepacks 0 / 11, wiki-context 1 / 7,
search-intercept 0 / 1.

## 2. The features

The reading program renders each transcript with `scripts/s1_train/render.py` and refuses a transcript whose rendered
sha256 is not the view summary's. It tokenizes each event's block on its own, with the checkpoint's tokenizer, and
reads the blocks in file order from the zero state, carrying the state across the whole transcript. A readout is the
model's final hidden state (after `ln_out`; 1,024 values) at the last token read.

| Feature | Per | What is read |
|---|---|---|
| `s` | row | the stream up to the row's `state_end` (the readout at the last token before it) |
| `c_ctx` | row | the candidate block, read from a copy of the state at `state_end`; the copy is then dropped |
| `q_ctx` | row | the question block, read after the candidate block on the same copy |
| `c_free`, `q_free` | distinct candidate | the candidate block, then the question block, read from the zero state |
| `s_w`, `c_ctx_w`, `q_ctx_w` | row | as `s`, `c_ctx`, `q_ctx`, but the state reads only the last 2,048 tokens before `state_end`, from the zero state (control C3) |

The candidate block is the block `render.py` makes for a hook that hands the model the candidate:
`"Hook: " + render.body(candidate) + "\n\n"`. The question block, verbatim: `"Question: Is the hook text above useful for
the next step?\n\nAnswer:"`. Both are fixed in §8's block.

## 3. The heads and the choice among them (on the CPU, the training rows only)

Every feature is standardized with the training fold's mean and standard deviation (floor 1e-6). The folds: each kind's
training rows sorted by (time, id) and cut into 5 contiguous parts as equal as possible; fold k is every kind's part k.
For each configuration, each fold's model is trained on the other four folds and scores its own fold, giving one
out-of-fold probability per training row.

| Family | Model | Grid |
|---|---|---|
| A, CLM's pair | a state head over `s` and an action head over `c_free`, each an MLP (LayerNorm, GELU, dropout 0.1, hidden width 256) to 128 values; score = exp(t) × cosine, t from log(1/0.07), exp(t) at most 100. Loss: bidirectional in-batch InfoNCE over the batch's yes rows (another row with the same candidate is masked out of a row's denominator, in both directions), plus a yes/no term on every row, BCE of sigmoid(a × score + b); P(yes) = sigmoid(a × score + b); AdamW, weight decay 0.01, batch 64 | hidden layers 1 or 2; learning rate 1e-3 or 3e-4; epochs 20 or 60 (8 points) |
| B, a probe on `c_ctx` | (i) logistic regression, L2 weight λ, full-batch L-BFGS, 200 steps; (ii) an MLP, one hidden layer of 256, dropout 0.1, AdamW 1e-3, weight decay 0.01, batch 64 | (i) λ in 1e-4, 1e-3, 1e-2, 1e-1; (ii) epochs 20 or 60 (6 points) |
| C, a probe on `q_ctx` | as B | as B (6 points) |

The choice: for each of the 20 configurations, the threshold τ that maximizes the out-of-fold accuracy over the 871
training rows (candidates: the midpoints between sorted distinct probabilities, plus 0 and 1; on a tie, the one closest
to 0.5). The configuration with the highest out-of-fold accuracy is chosen; a tie goes to the lower out-of-fold log loss,
then to the earlier configuration in the order written above. The chosen model's held-out probability is the mean of
its five fold models' probabilities, and a row is called yes when it is at least τ. Nothing is retrained on all 871 rows.
Seeds: 441 plus the fold index for each fit; one CPU thread; deterministic torch algorithms.

## 4. The bar (one evaluation of the chosen model on the 220 held-out rows)

The kind rule is each kind's majority label on the training rows: edit-snapshot no (215 no, 43 yes); every other kind
yes. On the held-out rows it is right on 178 of 220 (0.809).

- **PASS:** the chosen model is right on more than 178 of the 220 rows AND a one-sided exact McNemar test against the
  kind rule on the same rows gives p < 0.05 (b = rows the model gets right and the rule wrong, c = the reverse;
  p = P(X ≥ b) for X binomial with n = b + c, p = 0.5).
- **NOT SHOWN:** more than 178 right, p ≥ 0.05.
- **FAILED:** 178 or fewer right.

What PASS takes in practice (the exact test at p < 0.05):

| Rows where the two disagree | The model must be right in at least | Net gain over the rule | Accuracy at least |
|---|---|---|---|
| 10 | 9 | 8 rows | 0.845 |
| 20 | 15 | 10 rows | 0.855 |
| 30 | 20 | 10 rows | 0.855 |
| 40 | 26 | 12 rows | 0.864 |

Reported beside the verdict, through the same evaluator: accuracy, balanced accuracy, AUC (Mann-Whitney), log loss,
the confusion counts, and accuracy per kind; the same for always-yes, the kind rule and word overlap (the Jaccard of
the lowercase word sets, words of 3 or more letters, digits or underscores, of the candidate and of the last 4,000
characters of the state before `state_end`; its threshold fit by accuracy on the 871 training rows).

The 220 rows give ONE claim. A model changed after its held-out score is scored again only as EXPLORATORY; a new claim
needs new held-out rows (a new frozen build).

## 5. The controls (each through the same evaluator; expected outcome and when the run is void)

| Control | What changes | Expected | Void when |
|---|---|---|---|
| C1, labels shuffled within each kind | the training labels permuted inside each kind (seeds 1, 2, 3); the whole §3 procedure re-run, the choice included | the kind rule's level or below | 2 or more of the 3 seeds meet the PASS rule |
| C1b, labels shuffled across kinds | one permutation of all training labels (seed 4); the whole §3 procedure | always-yes's level or below | never (reported) |
| C2, no session state | the chosen configuration with `c_free` for `c_ctx` (B), `q_free` for `q_ctx` (C), or zeros for `s` after standardization (A) | below the full model if the state helps | never (reported) |
| C3, a short window | the chosen configuration on `s_w`, `c_ctx_w`, `q_ctx_w` | below the full model if the whole stream helps | never (reported) |

The record claims "the session state helps" only if the full model beats C2 with a two-sided exact McNemar p < 0.05,
and "the whole stream helps over a short window" only if it beats C3 the same way. The run is also VOID when any §1
identity differs at run time, when two reads of the same two transcripts (the two smallest that hold rows, read twice
in the window) give any row a readout cosine below 0.999, or when two runs of §3 and §4 on the same features do not
give byte-identical records.

## 6. The serving-feature comparison (task #473, after the run)

On the 103 rows (24 held-out) of the 22 transcripts whose stream before their last row is at most 500,000 characters:
llama.cpp reads the SAME token ids with the Q8_0 file on the sandbox's CPU; the record gives the cosine of `s`,
`c_ctx` and `q_ctx` against fla's per row, and the chosen model's decisions on both feature sets. **Bar:** at least 98
of the 103 decisions equal, so the heads may serve on llama.cpp's features as trained (task #448); otherwise task #448
reads the training rows with llama.cpp and trains the heads again before anything serves. The share of blocks whose ids
from llama.cpp's own tokenizer equal the checkpoint tokenizer's is reported (a live reader tokenizes with llama.cpp).

## 7. After each outcome

- **PASS:** the comparison (task #473), then RWKV-7's live home (task #448, its own plan); Laya retires once RWKV serves
  live (D-126).
- **NOT SHOWN or FAILED:** the record gives the controls' readings, and the coordinator puts the next step to the owner
  with them: more data (D-126 item 3), a tuned state per role (task #453, D-127), or tuned weights in a training window
  (D-125, D-078).

## 8. The machine-read block

The evaluator (task #472) reads its numbers from this block only and records this file's sha256 in its output.

```json
{
  "prereg": "s1-prereg-441-v1",
  "question": "s1.inject",
  "inputs": {
    "build_commit": "5be8cc0c7329a4ffdbed65274032790988f81211",
    "dataset_summary_sha256": "ce04b35c8cd43b37caabe8f968d487a3d7174cdb978a13b6ea627f47e6fec4db",
    "view_jsonl_sha256": "29c5207de39d8f8b5c59b769ed2d56c577566189bb1d05c738ff714e09587a66",
    "view_summary_sha256": "3c6cddc5ea182331ccbcc70d10e6ca93436bbfe66e4b298c9a067c0ab4bd917c",
    "export_id": "2026-10-01T18:32:15Z",
    "export_manifest_sha256": "ff049420ec74d5b044f84df7f2a75a265f01540836b4283986b626003bf060f6",
    "model_repo": "RWKV/RWKV7-Goose-World2.9-0.4B-HF",
    "model_revision": "e94655a9fad2c8da9f25aba575d8f0fdedc05931",
    "model_safetensors_sha256": "e162387e439dfa3387a0ca7da61638749d00c9862b8cc0192ae5d366c8c1a524",
    "model_dtype": "bfloat16",
    "serving_file_sha256": "52294392f54da107a50bf7cfb2ef189cd5892beb0ddfa88f969f7fcf77e449fa"
  },
  "rows": {"train": 871, "train_yes": 513, "heldout": 220, "heldout_yes": 147},
  "features": {
    "candidate_block": "Hook: {body}\n\n",
    "question_block": "Question: Is the hook text above useful for the next step?\n\nAnswer:",
    "readout": "final hidden state after ln_out at the last token read",
    "short_window_tokens": 2048
  },
  "cv": {"folds": 5, "seed": 441, "std_floor": 1e-06},
  "grid": {
    "A": {"hidden_width": 256, "out_dim": 128, "dropout": 0.1, "hidden_layers": [1, 2], "lr": [0.001, 0.0003],
          "epochs": [20, 60], "batch": 64, "weight_decay": 0.01, "logit_scale_init": 2.6592600369327779,
          "logit_scale_max": 100.0},
    "B": {"logreg_l2": [0.0001, 0.001, 0.01, 0.1], "logreg_lbfgs_steps": 200,
          "mlp": {"hidden_width": 256, "dropout": 0.1, "lr": 0.001, "weight_decay": 0.01, "batch": 64, "epochs": [20, 60]}},
    "C": "same as B"
  },
  "bar": {"kind_rule_heldout_correct": 178, "heldout_rows": 220, "alpha": 0.05,
          "test": "one-sided exact McNemar against the kind rule"},
  "controls": {"C1_seeds": [1, 2, 3], "C1_void_if_passing_seeds_at_least": 2, "C1b_seed": 4,
               "state_claim_alpha": 0.05, "window_claim_alpha": 0.05},
  "determinism": {"read_repeat_cosine_min": 0.999},
  "comparison": {"max_prefix_chars": 500000, "rows": 103, "decisions_equal_min": 98},
  "word_overlap": {"state_tail_chars": 4000, "min_word_len": 3}
}
```
