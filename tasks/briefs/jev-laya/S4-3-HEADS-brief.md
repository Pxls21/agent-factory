# S4-3-HEADS (task #472): the heads and the one evaluator of the first S1 training

Role: code-implementer (sandbox, Opus 5.5). PIN: b1df2d35 (the code commit under the origin head at authoring, which adds only transcripts; full id in the premise). Report:
`tasks/briefs/jev-laya/S4-3-HEADS-report.md` (write it incrementally from the start). Do NOT spawn subagents. Touch ONLY
the files in the boundary; report adjacent defects, never fix them.

## WHY

Task #441 is the first S1 training (`tasks/s1-heads-breakdown.md`): a frozen RWKV-7 reads the session, and small heads
learn on the CPU whether an injected context helps the step it was injected at. Its pre-registration
`docs/research/findings/s1-train/PREREG-441.md` fixes, before any feature exists, how the heads are chosen and how the
one chosen model is scored against the 0.809 kind rule on 220 held-out rows. This task builds the code that does
exactly that, and nothing the pre-registration does not say. A wrong green here is expensive: the owner retires the
older System-1 model on this verdict (D-126). So the code is built and proven on SYNTHETIC features before the real
ones exist; the coordinator runs it once on the real features.

Task #471 (the reading program, `scripts/s1_train/read.py`) runs beside you on disjoint files. Its outputs reach you
only through `scripts/s1_train/features.py` (the coordinator's; you read it, never change it) and through the tails
file and the compare output, whose shapes THE INPUTS and E-7 below copy from that task's brief (its R-7 and R-8).

## GOAL

`scripts/s1_train/heads.py` (the configurations, the folds, the training, the predictions) and
`scripts/s1_train/evaluate.py` (a CLI: `run` and `explore`; the one evaluator), and their tests.

## BOUNDARY

- CREATE `scripts/s1_train/heads.py`, `scripts/s1_train/evaluate.py`, `tests/test_s1_train_heads.py`.
- READ, never modify: `docs/research/findings/s1-train/PREREG-441.md` (§3, §4, §5, §8: copy, do not redesign);
  `scripts/s1_train/features.py` and `tests/test_s1_train_features.py` (the features format: `features.read` only);
  `tests/test_laya_ft.py` lines 40-60 and 660-700 (how a test runs torch code in the Laya venv,
  `/root/venv-laya-probe/bin/python`, as a subprocess, and its LOUD SKIP outside the sandbox venue).
- Every other file is out of bounds. Task #471 creates `scripts/s1_train/read.py` and its tests at the same time: never
  touch them, and never import read.py (it does not exist at your PIN).

## THE INPUTS (shapes; copy, do not redesign)

**The pre-registration's block:** the file's only fenced ```json block (none, two, or invalid JSON: refused). The keys
you use are in §8 of the file at your PIN. Every number you need (the folds, the seed, the grid, the bar, the controls'
seeds and void rule, the word-overlap settings, the row counts, the input sha256s) comes from it; a number written in
your code instead is a defect.

**The view:** `<view dir>/view.jsonl`, one JSON row per line with (among others) `id`, `split` (`train` or `heldout`),
`label` (true or false), `source` (the injection's kind), `time` (an ISO string), `src`, `state_end`, `candidate`
(the injected text) and `candidate_sha256`; its sha256 must be
the block's `inputs.view_jsonl_sha256`.

**The features:** `features.read(<dir>)` returns the index and the matrices: row arrays `s`, `c_ctx`, `q_ctx`, `s_w`,
`c_ctx_w`, `q_ctx_w` keyed by row id, free arrays `c_free`, `q_free` keyed by candidate sha256. The index's `meta`
holds `prereg_block` (the block the read used) and `prereg_sha256`.

**The tails:** `<tails dir>/manifest.json` (`prereg_sha256`, `view_jsonl_sha256`, `view_summary_sha256`,
`export_manifest_sha256`, `count`, `tails_sha256`) and `<tails dir>/tails.jsonl` (one `{"id", "tail"}` per row, sorted
by id): the last `word_overlap.state_tail_chars` characters of the session before the row.

## PINNED DECISIONS (a conflict with the pre-registration is a STOP-and-report)

**E-1 Inputs verified.** The view's sha256 equals the block's; the counts equal `rows` (train, train yes, held-out,
held-out yes); the features' `meta.prereg_block` equals the current block on the keys `inputs`, `rows`, `features`,
`cv`, `grid`, `bar`, `controls`, `word_overlap` (any difference refused; a difference elsewhere is recorded); every row
of the view has a vector in every row array and its candidate in both free arrays; the tails manifest's `view_jsonl_sha256`,
`view_summary_sha256` and `export_manifest_sha256` equal the block's, its `tails_sha256` is its file's own, and its
`count` is the view's row count. The kind rule (each kind's majority label on the training rows; a tie is
refused) must be right on exactly `bar.kind_rule_heldout_correct` held-out rows, else refused: that check catches a
wrong join of labels, splits or kinds.

**E-2 Folds, standardization, configurations, training, the choice, the held-out score: §3 of the pre-registration,
exactly.** The configuration order is the grid's order as §3 writes it (A: hidden layers, then learning rate, then
epochs; then B (i) by λ, B (ii) by epochs; then C the same); each has a stable name. Every training row's out-of-fold
probability comes from the fold model that did not train on it. A function that trains or scores a fold refuses a
held-out row (`heads.HeldOut`). The held-out probability is the mean of the five fold models'; nothing is retrained on
all training rows.

**E-3 Torch only inside the training.** `heads.py` and `evaluate.py` import with no torch, so CI imports them and runs
the pure parts (the prereg block, the input checks, the folds, the thresholds, the metrics, McNemar, the verdict, the
controls' rules, the record). The training runs in a Python that has torch: `torch.set_num_threads(1)`,
`torch.use_deterministic_algorithms(True)`, `torch.manual_seed(seed + fold)` before each fit, and a `torch.Generator`
with the same seed for the batch order. The real run uses the sandbox's `/root/venv-laya-probe/bin/python` (torch 2.14.0+cpu) or the PC's
`~/venv-rwkv-b` (torch 2.7.1, on its CPU): use only APIs both versions have; byte identity is required within one
Python (`--twice`), never across the two.

**E-4 The model families (§3).** A: two MLPs, `Linear(d, 256) → LayerNorm → GELU → Dropout(0.1)`, repeated for each
hidden layer (`Linear(256, 256)` after the first), then `Linear(256, 128)`; outputs L2-normalized; `t` learnable from
`logit_scale_init`, `exp(t)` clamped at `logit_scale_max`; `L[i, j] = exp(t) * <state_i, action_j>`. Its loss: over the
batch's yes rows Y (|Y| < 2 gives 0), state to action `-log(exp(L[i,i]) / Σ_j exp(L[i,j]))` and action to state
`-log(exp(L[i,i]) / Σ_j exp(L[j,i]))`, j over Y where j = i, or row j shares neither the candidate (`candidate_sha256`) nor the
state (the same `src` and `state_end`) with row i; their mean, plus the BCE
of `sigmoid(a * L[i,i] + b)` against the label over every batch row (`a` from 1, `b` from 0, learnable); P(yes) =
`sigmoid(a * L[i,i] + b)`. B and C: (i) `Linear(d, 1)`, BCE plus `λ * ||w||²` (not the bias), `torch.optim.LBFGS`
(`max_iter` the block's steps, `line_search_fn="strong_wolfe"`), full batch; (ii) `Linear(d, 256) → GELU → Dropout(0.1)
→ Linear(256, 1)`, AdamW. Batches of the block's size, shuffled per epoch, the last partial batch kept.

**E-5 Metrics and tests.** Accuracy; balanced accuracy (the mean of the yes and no rates); AUC (Mann-Whitney, a tie
counts one half); log loss (probabilities clipped to [1e-7, 1 - 1e-7]; null for a 0/1 baseline); the confusion counts;
accuracy per kind. McNemar against the kind rule on the same rows: b = model right and rule wrong, c = the reverse,
n = b + c; one-sided p = Σ_{k=b..n} C(n, k) / 2^n (1.0 when n = 0); two-sided p = min(1, 2 * min(P(X ≥ b), P(X ≤ b))).
Exact integer arithmetic for the binomial sums.

**E-6 Baselines through the same code.** Always-yes; the kind rule (E-1); word overlap: the Jaccard of the sets of
`re.findall(r"[a-z0-9_]{N,}", text.lower())` (N the block's `min_word_len`) of the candidate's body and the row's tail,
its threshold chosen on the training rows by §3's threshold rule. The candidate's body for this baseline is the view
row's `candidate`.

**E-7 The verdict (§4).** PASS, NOT SHOWN or FAILED from the counts and the one-sided p. VOID overrides it when: C1's
rule fires (§5: at least `C1_void_if_passing_seeds_at_least` of the C1 seeds meet the PASS rule); the read-repeat
comparison (`--read-repeat <file>`, the JSON `read.py compare` prints, `{"arrays": {...}, "min": ...}`: its `min`) is below
`determinism.read_repeat_cosine_min`; or `--twice` finds the two records differ. Without `--read-repeat` the verdict is
INCOMPLETE, never PASS. The claims of §5 (the state helps, the stream helps) are written only when their two-sided p is
below the block's alpha.

**E-8 The controls (§5).** C1: per seed, the training labels permuted within each kind (`random.Random(seed).shuffle`
over each kind's training rows sorted by id), then the whole choice and scoring re-run. C1b: one permutation of all
training labels. C2: the chosen configuration's family on the state-free inputs (`c_free` or `q_free` by the row's
candidate; for A, the standardized `s` replaced by zeros). C3: the chosen configuration on `s_w`, `c_ctx_w`, `q_ctx_w`.
Each through the same metrics, with McNemar against the full model (two-sided) and against the kind rule.

**E-9 The record.** `evaluate.py run --prereg <file> --view <dir> --features <dir> --tails <dir> [--read-repeat
<file>] [--twice] --out <file>`: one JSON file (sorted keys, indent 1, no clock, no host path; refused if `--out`
exists or has a `..` part), with the prereg's sha256, every input sha256, every configuration's out-of-fold accuracy,
threshold and log loss, the chosen one, the held-out metrics of the model, the baselines and the controls, the McNemar
numbers, the void checks and the verdict. stdout: one line (the verdict and the counts). `evaluate.py explore --config
<name> ...` scores one named configuration on the held-out rows and writes the same shape with `"exploratory": true`
and no verdict. No session text in any output.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below at your HEAD; stop and report on a mismatch.
2. Synthetic fixtures built in the test: a view (`view.jsonl` with the fields above; three kinds, one of them with
   fewer than five training rows), features written with `features.write` (dimension 8), a tails directory, and a
   pre-registration file whose block carries the fixture's sha256s, row counts and its own `kind_rule_heldout_correct`
   (computed in the test from the fixture's labels); the grid of the real block, but small epochs so the file runs in
   under five minutes.
3. Normal tests (torch ones through the Laya venv as a subprocess, with the LOUD SKIP outside the sandbox venue): with a
   planted signal (one feature dimension carries the label in `c_ctx`, `q_ctx` and `s`, with noise) the verdict is
   PASS; with no signal it is never PASS; C1 on the planted data does not fire; two
   runs give byte-identical records; `--twice` passes.
4. Pure tests in the main interpreter (no torch): McNemar one-sided and two-sided against hand values (n = 10, b = 9:
   11/1024; n = 10, b = 8: 56/1024; n = 0: 1.0); AUC with ties against a hand value; the threshold rule on a hand
   example (the tie goes to the threshold closest to 0.5); the folds of a hand example (a kind with three rows fills
   parts 0 to 2); the verdict table for each branch (PASS, NOT SHOWN, FAILED, VOID by C1, VOID by the read repeat,
   VOID by `--twice`, INCOMPLETE); the word-overlap words.
5. Failure tests, each asserting the named reason: a prereg with no block, or two; the view's sha256 not the block's;
   a row count off; a features byte changed (features.read's refusal surfaces); a features block that differs on `bar`;
   a row missing from a row array; the kind rule's held-out count not the block's; a held-out row handed to a fold's
   training (`heads.HeldOut`); `--out` that exists; a tails file whose sha256 is not its manifest's.
6. Mutants on a scratch copy of your files (one exact edit each, the baseline green first), each red on a named test:
   the threshold chosen on the held-out rows; the configuration chosen on the held-out rows; McNemar two-sided where
   one-sided is pinned; b and c swapped; the kind rule taken from the held-out rows; C1 shuffled across kinds; folds
   assigned in id order instead of time order; the held-out score from fold 0's model alone; the C1 void rule off; the
   read-repeat rule off; a seed not set. Paste the table.
7. Tests run twice: `bash scripts/test_summary.sh --basetemp <scratch dir> tests/test_s1_train_heads.py` (the counts
   pasted from its `pytest-summary:` line) and `bash scripts/pc_suite.sh set-id -- tests/test_s1_train_heads.py`; also
   `tests/test_s1_train_features.py` once (you do not change it).
8. Gates: pyflakes on every file you write; `python3 scripts/ap_screen.py <your files>` (paste its tells and answer
   each); the separator check (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0).
9. NOT run here: the real features (they do not exist yet). Say so in the report.

## STANDING RULES

No outward-facing action (no push, PR or comment); no network; no PC bridge. Never commit, stash, checkout or reset in
`/home/user/agent-factory` (the coordinator commits). Never read `.jev/`, the coordinator's scratchpad, `/root/.codiv/`,
`.pc-bridge.env`, any `*.env`, or a real transcript under `/root/.claude/projects/`. In the session scratchpad, read
nothing outside a directory you create there. Long commands in ONE foreground call; no background job. A pytest
`--basetemp` parent must exist first. Every test run with `PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox
HF_HUB_OFFLINE=1`, no `-n`. Your final message is the report: files and lines, the pasted counts, the mutant table,
discrepancies, and what is NOT done.

## PREMISE — MEASURED at authoring (2026-10-02 09:3xZ, /home/user/agent-factory@b1df2d35)

Re-run each command at your HEAD; its output must match.

```
$ git rev-parse --verify b1df2d3508155b8b664750e715f680505e113eb7^{commit}
b1df2d3508155b8b664750e715f680505e113eb7
$ git merge-base --is-ancestor b1df2d3508155b8b664750e715f680505e113eb7 HEAD && echo the PIN is an ancestor of HEAD
the PIN is an ancestor of HEAD
$ git diff --stat b1df2d3508155b8b664750e715f680505e113eb7 HEAD -- scripts/s1_train/features.py tests/test_s1_train_features.py docs/research/findings/s1-train/PREREG-441.md tests/test_laya_ft.py | wc -l
0
$ test -e scripts/s1_train/heads.py || echo heads.py absent; test -e scripts/s1_train/evaluate.py || echo evaluate.py absent; test -e tests/test_s1_train_heads.py || echo test_s1_train_heads.py absent
heads.py absent
evaluate.py absent
test_s1_train_heads.py absent
$ grep -n -E '^LAYA_PY = |LOUD SKIP' tests/test_laya_ft.py | cut -c1-80
48:LAYA_PY = "/root/venv-laya-probe/bin/python"
680:        pytest.skip("LOUD SKIP: the Laya venv and snapshot are declared inpu
$ /root/venv-laya-probe/bin/python -c "import sys, torch; print(sys.version.split()[0], torch.__version__)"
3.11.15 2.14.0+cpu
$ python3 -c "import importlib.util as u; print([m for m in ('numpy', 'torch') if u.find_spec(m)])"
[]
$ python3 -c "import json, re; t = open('docs/research/findings/s1-train/PREREG-441.md').read(); b = re.findall(chr(96) * 3 + 'json\\n(.*?)\\n' + chr(96) * 3, t, re.S); d = json.loads(b[0]); print(len(b), sorted(d)); print(d['bar']); print(d['rows'])"
1 ['bar', 'comparison', 'controls', 'cv', 'determinism', 'features', 'grid', 'inputs', 'prereg', 'question', 'rows', 'word_overlap']
{'kind_rule_heldout_correct': 178, 'heldout_rows': 220, 'alpha': 0.05, 'test': 'one-sided exact McNemar against the kind rule'}
{'train': 871, 'train_yes': 513, 'heldout': 220, 'heldout_yes': 147}
$ B=$(mktemp -d) && PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1 python3 -m pytest -q -p no:cacheprovider tests/test_s1_train_features.py --basetemp $B/bt 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
16 passed
```
