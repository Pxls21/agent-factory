# VERIFY-S4-3-HEADS report (task #472), round 1

**Gate recommendation: MERGE-READY-WITH-FOLLOWUPS.** No finding meets the whole blocking predicate. Every question Q1 to Q7 checks out through the real code path, on synthetic features written by `features.py`. The follow-ups are:
- 23 non-equivalent surviving mutants (test gaps; I checked the code itself correct on each);
- three record and input-check gaps;
- one property of the pre-registered C1 control (F-1).

Two notes belong on the recommendation line:
- **HEAD moved twice during the lane** (6b8c026, then d85d17a4, then e4b894e1). The premise's diff-stat line now reads 2 instead of 0. The whole difference is `scripts/s1_train/view.py`: task 460's `--out '..'` refusal, D-134. `evaluate.py` and `heads.py` never import `view.py`, and all seven hashed premise files are unchanged at e4b894e1. The premise matched exactly at lane start; whether this move needs a fresh premise is your call.
- **Nothing ran on real features or on the PC.** HEAD's commit ded4af91 says task 441's window 1 read the features; I used none of them.

Round table (D-115): round 1, 0 blockers.

## 1. Premise and the builder's tests

- **Premise at lane start** (11:27Z, HEAD 6b8c026b): every line matched. Output is in `…/verify-s4-3-heads/premise.txt`:
  - the PIN resolves to `daa2075724b4…` and is an ancestor of HEAD;
  - diff-stat `0`;
  - the 7 sha256 prefixes are the brief's;
  - the prereg diff has `12` lines; the json block reads `1 43580dab3a486cd3`;
  - `wc` gives 340/640/931; `grep -c '^def test_'` gives `41`;
  - set-id `1 files set=e8d6713191fd`.
- **At e4b894e1**: diff-stat gives `scripts/s1_train/view.py | 16 ++++++++++------`; the 7 hashes are unchanged.
- **Builder's tests at the PIN bytes, twice** (`bash scripts/test_summary.sh tests/test_s1_train_heads.py --basetemp <scratch>/…`):
  - `pytest-summary: 51 passed in 90.46s (0:01:30)`
  - `pytest-summary: 51 passed in 87.47s (0:01:27)`
  - `bash scripts/pc_suite.sh set-id -- tests/test_s1_train_heads.py` gives `1 files set=e8d6713191fd`.
  - Scratch-copy baseline before the mutants: `pytest-summary: 51 passed in 88.98s (0:01:28)`.

## 2. Answers

**Q1, the held-out wall: it holds.**
- **Metamorphic test** (`vlib/laya.py wall`). I built 4 fixtures with 129 training and 54 held-out rows:
  - f0: the base, with a planted signal;
  - f1: 27 held-out labels flipped;
  - f2: a ±6 held-out-only label leak in 6 of 8 dimensions;
  - f3: every held-out label flipped plus a ±9 leak.

  Everything the record decides before a held-out score (19,956 bytes) is byte-identical to f0's in f1, f2 and f3. That covers all 20 configuration rows (τ, rows right, log loss), the choice, τ, the fold sizes, the rule, the word-overlap τ, and every control's table, choice, labels and τ. The held-out metrics change, as they should (model right: f0 51, f1 26, f2 52, f3 12).
- **Trace of each evaluation**:
  - 510 fits with 0 held-out ids, each on exactly the other four folds;
  - 510 out-of-fold scorings with 0 held-out ids, each on exactly its own fold;
  - all 103 `threshold` calls take 129 inputs (the training rows);
  - all 7 `choose` calls take labels for exactly the training rows.
- **"Only label of its value" kind**: kind-z has 6 training rows, all no, and one held-out row, a yes. Its training yes count is 0 under the real labels and under each C1 seed. It is 5 under C1b, which shuffles across kinds by design.

**Q2, the configurations, folds and fits: exact** (`vlib/laya.py fits`, `seedcheck.py`, `paircheck.py`, `probscheck.py`; all 20 configs at the real 20/60 epochs).
- **Family A:**
  - AdamW gets each configuration's own lr (0.001 or 0.0003) and weight decay 0.01.
  - t, a and b start at `[2.6592600345611572, 1.0, 0.0]`.
  - The towers are exactly E-4's.
  - exp(t) at t=10 gives `100.0`.
  - Batches per epoch are 64 + 38.
- **B and C logistic regression:**
  - L-BFGS runs with `{'max_iter': 200, 'line_search_fn': 'strong_wolfe'}` and converges in 8 to 19 iterations.
  - Stationarity holds for λ‖w‖²: max|∂BCE/∂w + 2λw| is 1.1e-6 to 4.7e-6. Under the λ/2 reading the residual would be 8.9e-4 to 1.1e-1.
  - The bias is not penalized: |∂BCE/∂b| is 2.5e-7 to 2.3e-6. Under a penalized bias it would be 3.1e-5 to 1.2e-2.
- **B and C MLP**: matches §3.
- **Seed**: initial weights equal `torch.manual_seed(441+fold)` followed by E-4's layers, for folds 0, 2, 3 and 4; a different seed differs.
- **Folds**: my chronological oracle agrees on 400 random cases. Those cases include `+02:00` spellings; in 80 of them a string sort of `time` would cut different folds (G-8 matters).
- **Held-out probability**: it equals the mean of the five fold models' (gap 0.0; the fold models spread by 0.356).
- **Family A's loss**, captured inside a real fit:
  - inputs standardized exactly (gap 0.0);
  - L = exp(t)·s·cᵀ exactly;
  - labels, candidate and state equality patterns: 0 mismatches;
  - 385 yes-pairs share a state with different candidates, so the amended mask is exercised;
  - `pair_loss` against my loop oracle: 400 cases, max relative gap 1.6e-15.
- **Scoring formula**: probabilities recomputed by hand match within 6.1e-7 (A), 7.3e-8 (B) and 6.5e-8 (C).

**Q3, the threshold and the choice: no difference on the real path** (`vlib/pure.py`).
- Threshold against an exact Fraction oracle: 0 mismatches in 20,000 cases with float32-valued probabilities, ties, 0 and 1 included.
- The choice against its oracle: 0 mismatches in 3,000 cases, exact duplicates included.
- One input class does differ: adjacent float64 values. The float midpoint collapses onto one of them, and 1,270 of 3,000 such cases lose a partition. The real out-of-fold probabilities are float32 values, so this cannot happen there (finding 17).

**Q4, the bar: exact.**
- McNemar against my own Pascal-triangle binomial (no `math.comb`): 24,531 (n, b) pairs for n = 0 to 220, 0 mismatches.
- The §4 table reproduces exactly: `[10,9,8,.845] [20,15,10,.855] [30,20,10,.855] [40,26,12,.864]`.
- The verdict over all 7,697 reachable (b ≤ 42, c ≤ 178) cells: 0 mismatches (FAILED 6,794, NOT SHOWN 388, PASS 515).
- Boundaries:

| Right | p (one-sided) | Verdict | Why |
|---|---|---|---|
| 178 | any | FAILED | not more than 178 |
| 179 | 1/2 exactly | NOT SHOWN | b = c + 1, always |
| 184 (b8 c2) | 7/128 | NOT SHOWN | p ≥ 0.05 |
| 185 (b9 c2) | 67/2048 | PASS | p < 0.05 |
| synthetic | exactly 1/20 | NOT SHOWN | strict inequality |
| synthetic | 1/20 − 1e-30 | PASS | strict inequality |

- The kind rule refuses a tie, and refuses a count off by +1 or by −1.

**Q5, the controls and the verdict: conformant** (`vlib/clicheck.py`, `laya.py wall`).
- **C1** runs the whole procedure for each seed: 20 cross-validations plus a `choose`, on labels equal to my own within-kind oracle.
- **C1b** runs on my own oracle's cross-kind permutation.
- **C2 and C3** run the chosen configuration, each with its own τ:
  - A's C2: `s` is all zeros in 15 of 15 fits;
  - B's C2 reads `c_free`; C's C2 reads `q_free`;
  - C3 reads `s_w`/`c_ctx_w`/`q_ctx_w`.
- **Held-out scoring** always uses the real labels.
- **Verdict paths through the CLI**:
  - planted fixture: PASS, both claims;
  - read repeat 0.9989999: VOID;
  - no read repeat: INCOMPLETE;
  - a fault injected into C3 alone in the second pass: VOID, `twice: the two records differ`. So `--twice` compares the whole record.
- **Claims**: (9, 2), with one-sided p 0.033 and two-sided p 0.065, makes no claim. (1, 12) makes no claim (b < c).
- **Can a control be silently skipped, run on the real labels, or scored on permuted held-out labels?** No. The block refuses an empty seed list, and every control ran on its expected labels.
- **F-1 is a property of the pre-registered control, not of the code** (`vlib/c1rate.py`, seeds 1 to 20):

| Fixture | Seeds meeting PASS | C1 held-out AUC | P(≥2 of 3 seeds) |
|---|---|---|---|
| kinds' yes rates differ | 2 of 20 | all ≥ 0.49 | ≈ 0.028 |
| same, plus one linear kind dimension | 5 of 20 | mostly high | ≈ 0.156 |
| kinds' yes rates equal | 0 of 20 | 0.16 to 0.76, around 0.5 | 0 |

  The mechanism is the kind-rate difference. A within-kind shuffle keeps each kind's yes rate, so a label-carrying feature stays predictive of the shuffled labels across kinds. The C1 model learns it as a kind proxy, and on held-out rows that feature encodes the true label.

**Q6, the inputs: refused before any fit** (`vlib/q6.py`, CLI in the torch-less main interpreter, so exit 3 proves no fit ran).
- 103 of 109 corrupted inputs were refused with exit 3, each with its own reason. They cover:
  - the block (types, domains, NaN, 1e400, missing keys, the grid);
  - the view (sha, all 4 counts, shape, duplicates, time, UTF-8, naive/aware times, G-9, ties);
  - the features (byte flip, a difference on each of the 8 `BLOCK_KEYS`, a missing row or candidate, NaN, inf, dim, version);
  - the tails (all 3 shas, file sha, count, missing/unsorted/duplicate lines, null tail);
  - the kind-rule count, the read repeat, and `--out`.
- 6 passed and reached a fit:
  - an extra feature row, and a difference outside `BLOCK_KEYS` (E-1 says record them);
  - free text in `meta.prereg_sha256` (finding 13);
  - a 9,000-character tail (finding 14);
  - read-repeat `min` 5.0, and empty `arrays` (finding 15).

**Q7, the record and the boundary: conformant.**
- Two processes with PYTHONHASHSEED 1 and 2 give byte-identical records and stdout.
- Keys are sorted at every level and the indent is 1. stdout is one line.
- The record holds no marker, no U+2028, no host path, no candidate and no tail.
- `--out` refuses an existing file (its old bytes are kept), a `..` part, a missing directory, a dangling symlink and a directory.
- Refusal reasons reach stderr only. They can echo the `time` value, ids, kinds and host paths (finding 16).

**Q8, the tests.**
- **No tautologies.** Some tests restate the spec's literal algorithm (E-8's shuffle, E-2's loops). Several check consistency within the record rather than the values that reached a fit.
- **Planted fixture**: about AUC 1. It catches held-out leaks and wrong directions. It cannot tell which hyperparameters trained, so the Q2 wiring mutants survive.
- **No-signal test**: it can fail. A held-out label leak into held-out probabilities (L2) turns it red. A τ re-fit on held-out rows (L1) leaves it green; the builder's own M1 test catches that one.

## 3. Grades of the build report's readings

| Item | Grade | Evidence |
|---|---|---|
| D-1 | contract-conformant (amended §3) | `pair_loss` wiring + oracle; the record's `deviations` is `[]` |
| G-1 | conformant (frozen) | population-sd stats match exactly |
| G-2 | conformant | 0.25 vs 0.75 tie gives 0.25 |
| G-3 | conformant | reviewed only; a ranking-only baseline |
| G-4 | conformant | trace labels equal my oracle |
| G-5 | conformant | C2/C3 on the chosen config, each with its own τ |
| G-6 | conformant | the claims cases above |
| G-7 | conformant | reviewed; AUC fuzz |
| G-8 | conformant | folds oracle |
| G-9 | conformant | V15 refused; test gap N60 |
| G-10 | conformant | explore CLI |
| G-11 | conformant | O3 refused before any fit |
| N-1 | sound reading of E-7's letter, settled procedurally by amendment (3); not enforced in code | finding 12 |
| N-2 | sound (stricter) | every mismatch the evaluator can see is refused |
| N-3 | sound (E-6 pins the regex) | words fuzz, 0/9,000 |
| F-1 | property of the pre-registered control; the report's mechanism (chance agreement) is incomplete | Q5 table |
| F-2 | sound; not a defect | f2's held-out feature change moved no out-of-fold number |

## 4. Mutant table (42 new edits; none is one of the builder's 31)

Each mutant ran on a scratch copy against the builder's test file with `-x`, so only the first failing test is listed. Every file was sha-restored.

| ID | Q | File | Exact edit (old → new) | Result | First failing test |
|---|---|---|---|---|---|
| N01 | Q1 | E | word-overlap `threshold([…data.train_ids], [real[i]…train_ids])` → `[…data.ids], [rows[i]["label"]…data.ids]` | KILLED | test_the_record_follows_the_rules_it_reports |
| N02 | Q1 | H | `train_ids = [i for i in data.train_ids if data.fold_of[i] != fold]` → `list(data.train_ids)` | KILLED | test_the_held_out_probability_is_the_mean_of_the_five_fold_models |
| N03 | Q1 | H | `data.tensor(torch, name)[idx]` → `[…pos of every training row…]` | KILLED | test_a_planted_signal_passes_and_c1_does_not_fire (VOID) |
| N06 | Q2 | H | `nn.Dropout(cfg["dropout"])` → `nn.Dropout(0.1)` | SURVIVED (equivalent: block value) | — |
| N07 | Q2 | H | A's `AdamW(…, lr=config["lr"],` → `lr=1e-3,` | SURVIVED | — |
| N08 | Q2 | H | `max_iter=config["steps"]` → `max_iter=20` | SURVIVED | — |
| N09 | Q2 | H | `line_search_fn="strong_wolfe"` → `None` | SURVIVED | — |
| N10 | Q2 | H | `l2 * model.weight.pow(2).sum()` → `l2 * sum(p.pow(2).sum() for p in model.parameters())` | SURVIVED | — |
| N11 | Q2 | H | `config["l2"] *` → `config["l2"] / 2 *` | SURVIVED | — |
| N12 | Q2 | H | `torch.tensor(float(config["logit_scale_init"]))` → `torch.tensor(0.0)` | SURVIVED | — |
| N13 | Q2 | H | `Data`: `…k, seed, std_floor` → `…k, 0, std_floor` | SURVIVED | — |
| N14 | Q2 | H | `(1 if part < extra else 0)` → `(1 if part >= k - extra else 0)` | KILLED | test_folds_cut_each_kind_by_time_then_id |
| N15 | Q2 | H | `torch.randperm(n, generator=g)` → `torch.arange(n)` | KILLED | test_the_batch_order_follows_the_seed |
| N16 | Q2 | H | MLP `nn.Dropout(config["dropout"])` → `nn.Dropout(0.0)` | KILLED | test_the_heads_are_the_models_e4_names |
| N17 | Q2 | H | `- d).mean()) / 2 + bce` → `- d).mean()) + bce` | KILLED | test_pair_loss_masks_same_candidate_and_same_state |
| N18 | Q2 | H | `z = model.a * (scale * (s * c).sum(-1)) + model.b` → `z = scale * (s * c).sum(-1)` | SURVIVED | — |
| N21 | Q3 | E | `choose`: `) > (table[best]` → `) >= (table[best]` | KILLED | test_the_choice_reads_out_of_fold_accuracy_then_log_loss_then_order |
| N22 | Q3 | E | `choose`: the minus signs on both log losses removed | KILLED | (same) |
| N23 | Q3 | E | `abs(t - 0.5), t)` → `-abs(t - 0.5), t)` | KILLED | test_threshold_rule_takes_the_tie_closest_to_one_half |
| N24 | Q3 | E | `judge`: `probs[i] >= tau` → `probs[i] > tau` | SURVIVED | — |
| N25 | Q3 | E | `cands = {0.0, 1.0}` → `{0.0}` | SURVIVED (equivalent with a yes-majority training set) | — |
| N26 | Q3 | E | midpoints → `cands.update(distinct)` | KILLED | test_threshold_rule_takes_the_tie_closest_to_one_half |
| N27 | Q4 | E | `if right != block["bar"]["kind_rule_heldout_correct"]` → `<` | SURVIVED | — |
| N28 | Q4 | E | `verdict`: `right <=` → `right <` | KILLED | test_the_verdict_table[FAILED…] |
| N29 | Q4 | E | `range(b, n + 1)` → `range(b + 1, n + 1)` | KILLED | test_mcnemar_is_exact_against_hand_values |
| N30 | Q4 | E | `p_one_sided < _frac(alpha)` → `<=` | SURVIVED (equivalent: no tail k/2ⁿ equals 1/20) | — |
| N31 | Q4 | E | `if yes == no:` → `if False:` | KILLED | test_kind_rule_is_the_training_majority_and_a_tie_is_refused |
| N32 | Q5 | E | `claims`: `["p_two_sided"]` → `["p_one_sided"]` | SURVIVED | — |
| N33 | Q5 | E | the C1 count also counts C1b | SURVIVED | — |
| N34 | Q5 | E | C1 `_control(…, configs, …)` → `[chosen]` | SURVIVED | — |
| N35 | Q5 | E | C1b `_control(…, configs, …)` → `[chosen]` | SURVIVED | — |
| N36 | Q5 | E | `meets_pass_rule(…, vs_rule)` → `vs_full` | KILLED | test_a_planted_signal_passes_and_c1_does_not_fire |
| N40 | Q5 | H | `("C","C3"): ("q_ctx_w",)` → `("c_ctx_w",)` | SURVIVED | — |
| N41 | Q5 | H | `("B","C2"): ("c_free",)` → `("q_free",)` | SURVIVED | — |
| N44 | Q6 | E | `for key in BLOCK_KEYS:` → `BLOCK_KEYS[1:]` | SURVIVED | — |
| N45 | Q6 | E | free-array check → `if False:` | SURVIVED | — |
| N46 | Q6 | E | tails keys without `export_manifest_sha256` | SURVIVED | — |
| N47 | Q6 | E | view count keys without `heldout_yes` | SURVIVED | — |
| N60 | Q6 | E | G-9 check → `if False:` | SURVIVED | — |
| N51 | Q7 | E | `sort_keys=True` → `False` | SURVIVED | — |
| N52 | Q7 | E | `open(args.out, "x"` → `"w"` | SURVIVED | — |
| N53 | Q7 | E | `_dumps(again) == _dumps(record)` → compare `["model"]` only | KILLED | test_twice_voids_a_run_whose_two_passes_differ |

E = `scripts/s1_train/evaluate.py`, H = `scripts/s1_train/heads.py`.

**Tally**: 16 killed, 26 survived. Three survivors are equivalent on the real run (N06, N25, N30). For each of the other 23, I checked the unmutated code correct through the real path (sections 2 and 3).

## 5. Finding inventory

None of these is a BLOCKER. "Code correct" means I checked it through the real path.

**Test gaps (surviving mutants)**
1. **FOLLOW-UP: §3's training wiring is not pinned by any test** (N07–N13, N18). Code correct (Q2). Contract: §3. A regression would change the fits, the choice and the verdict, and the suite would stay green. Fix: capture the optimizer and L-BFGS settings and initial scalars per config, using a fixture grid whose values differ from the defaults; add a stationarity check and a hand check of P(yes).
2. **FOLLOW-UP: §5 claims are not pinned to two-sided** (N32). Code correct. Fix: add (9, 2) to the claims test.
3. **FOLLOW-UP: C1's re-choice is not pinned** (N34; N35 for C1b). Code correct (trace). Contract: §5 "the choice included". Fix: assert each C1 and C1b table has 20 rows.
4. **FOLLOW-UP: the C1 void count is not pinned to C1 only** (N33). Code correct.
5. **FOLLOW-UP: C2/C3 inputs per family are partly unpinned** (N40, N41). Code correct. Fix: assert `fit["names"]` per (family, variant).
6. **FOLLOW-UP: E-1 checks are partly unpinned** (N27, N44–N47, N60). Code correct (Q6). Fix: parametrize the failure tests over every key, count, direction and G-9.
7. **FOLLOW-UP: the record's form is not pinned** (N51; N52 is a race guard). Code correct.
8. **FOLLOW-UP (low): "at least τ" is not pinned** (N24). Code correct. The effect needs a held-out probability exactly equal to τ.
9. **INFO: three survivors are equivalent on the real run** (N06, N25, N30).

**Contract-level observations**
10. **FOLLOW-UP for you: F-1, C1 is not a null under a strong signal when kinds' yes rates differ.** Measured in Q5; not a code fault. Material: C1 can VOID a genuine PASS (about 3% to 16% per run in my fixtures; unknown on the real data). By the STATUS line, §5 freezes once features exist, so this is for reading the record.
11. **FOLLOW-UP: claims are written even when the verdict is VOID or INCOMPLETE.** The VOID records (read repeat, `--twice`) and the INCOMPLETE one all carry both claims. §5 is silent. Fix: suppress or mark claims under VOID. Your ruling.
12. **FOLLOW-UP: N-1 is not enforced.** A run without `--twice` can still record "PASS" (the record shows `twice: "not run"`). Fix: INCOMPLETE without `--twice` (one line in `verdict`), or a run checklist.

**Input and record gaps**
13. **FOLLOW-UP: two unvalidated fields pass into the record.** `features_prereg_sha256` and `tails_prereg_sha256` are copied verbatim; F15 put `"free text vfymarkqqz"` into the record. read.py writes a sha there, so this is not session text on the real path. Fix: accept only 64-hex.
14. **FOLLOW-UP: tail length is not checked** against `word_overlap.state_tail_chars` (T12). This affects the reported baseline only.
15. **FOLLOW-UP (low): the read repeat accepts `min` above 1 and an empty `arrays`**, and does not check `min` against `arrays`.

**Information only**
16. **INFO: refusals on stderr echo some input values**: the `time` value (V8 echoed the marker), ids, kinds, and host paths. Never in a record. The view's sha is checked before any row is parsed.
17. **INFO: the float midpoint collapses on adjacent float64 values.** Unreachable on the real path (Q3).
18. **INFO: `--twice` runs in one process.** I found no hash-order dependence (Q7).
19. **INFO: `check_block` does not check** that the C1 void count is at most the number of seeds, or that the seeds are distinct. The frozen block is 2 of [1, 2, 3].
20. **INFO: non-refusal exceptions exit 1 with a traceback and write no record.** Fail-closed.
21. **INFO: G-4 gives two kinds with equal training counts the same position permutation.** This is E-8's literal.
22. **INFO: Q8's fixture strength** is as described in section 2.
23. **INFO: the premise moved mid-lane** (view.py only).

**Not verified**
24. **UNVERIFIED: the PC runtime** (torch 2.7.1, its Python version). Before Python 3.11, `heads.when` accepts fewer ISO spellings; an unreadable time refuses, it never mis-scores. Not run: no bridge.
25. **UNVERIFIED: real-size wall time.**

## 6. Reproduced, reviewed, skipped

- **Reproduced**: everything in sections 2 and 4, with commands and outputs in the scratch directory.
- **Reviewed statically**: G-3, G-7, E-3's thread and determinism settings, N52.
- **Skipped**:
  - the builder's 31 mutants (the brief asks for new ones);
  - `tests/test_s1_train_features.py` (unchanged);
  - real features, the real view and read.py's outputs (out of bounds, and another lane's subject);
  - the PC (no bridge).
- I touched no tracked file (`git status` is clean) and spawned no subagent.

## 7. Files

Everything is in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-s4-3-heads/`:
- **Scripts** (`vlib/`): `fx.py` (my fixture builder), `pure.py`, `q6.py`, `laya.py`, `seedcheck.py`, `paircheck.py`, `probscheck.py`, `clicheck.py`, `c1rate.py`, `mutants.py`, `drive.py`.
- **Outputs** (`runs/`): `pure.json`, `q6.json`, `wall.json`, `fits.json`, `cli.json`, `c1rate.json`.
- **Mutants**: `mut/results.jsonl`, one log per mutant in `mut/logs/`.
- **Premise**: `premise.txt`.

Report written 2026-10-02 12:2xZ.

## Coordinator's harvest notes (2026-10-02 12:2xZ)

- The report is the lane's final message, whole, with its first line (an S1-RATE line) dropped. The hand-back was absent (task #426), so the local-id, known-value and canary checks ran by hand: no known value, no canary.
- One local commit id (the task #460 redesign's id before `scripts/push_clean.sh` rewrote it) is replaced by its pushed id, d85d17a4, in the second note of the opening section.
- `vfymarkqqz` is the verifier's own fixture marker (finding 13), not session text.
