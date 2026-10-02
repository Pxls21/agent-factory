# S4-3-HEADS report (task #472) — written incrementally

Lane: code-implementer (sandbox, Opus 5.5). Started 2026-10-02 09:4xZ. HEAD at start: b0039f4d4bbf4c052837433487774b252212d4ab.

## 1. Premise (re-measured at HEAD b0039f4, 2026-10-02 09:4xZ)

Every line of the brief's premise block matched (verified, exit codes 0):

- PIN b1df2d35 resolves; the PIN is an ancestor of HEAD.
- `git diff --stat PIN HEAD -- features.py, test_s1_train_features.py, PREREG-441.md, test_laya_ft.py | wc -l` = 0.
- heads.py, evaluate.py, test_s1_train_heads.py absent.
- test_laya_ft.py: `48:LAYA_PY = "/root/venv-laya-probe/bin/python"`, `680: pytest.skip("LOUD SKIP: ...`.
- Laya venv: `3.11.15 2.14.0+cpu`. Main python3: `[]` (no numpy, no torch).
- PREREG block: 1 block; keys bar, comparison, controls, cv, determinism, features, grid, inputs, prereg, question, rows, word_overlap; bar and rows as the brief prints.
- tests/test_s1_train_features.py: `16 passed`.

## 2. Brief vs pre-registration (read before coding, 10:0xZ)

Checked E-1..E-9 against PREREG-441 §3, §4, §5, §8 line by line. One real difference, and several places where
neither document says (each gap-fill below is mine, chosen conservatively, and named so the coordinator can rule).

**D-1, the one difference (coordinator ruling needed): the InfoNCE mask of family A.** PREREG §3 (line 56): "another
row with the same candidate is masked out of a row's denominator, in both directions". Brief E-4 masks a row j unless
"j = i, or row j shares neither the candidate (candidate_sha256) nor the state (the same src and state_end) with row
i": it also masks a row with the same STATE. These are different losses whenever a batch holds two yes rows at one
step with different candidates (common in the real data: several hooks inject at one step). I did not stop the lane:
the prereg itself permits this class of change (its STATUS line, verbatim: "After the features exist, nothing in §4
(the bar), §5 (the controls) or the grid of §3 changes; any other deviation is reported in the run's record as a
deviation."), and the mask is in §3's model text, not its grid.
So the code implements the brief's E-4 (the pinned decision) AND writes the difference into every record under
`deviations`, as the prereg demands. The coordinator rules: keep it (and amend the prereg before the window, then drop
the record line), or take the prereg's text (a one-clause change in `heads.pair_loss` plus its test). The test
`test_pair_loss_masks_same_candidate_and_same_state` pins E-4's version.

Gap-fills (neither document says; my choice, recorded here):
- G-1 Standard deviation: population (divide by n), floored at cv.std_floor.
- G-2 Threshold: a tie between two candidates equally close to 0.5 (e.g. 0 and 1) goes to the smaller one.
- G-3 Word overlap: two empty word sets have Jaccard 0. Its log loss is computed on the Jaccard score (E-5 nulls the
  log loss only for a 0/1 baseline); it is not a probability, so read it as a ranking-only baseline.
- G-4 C1: a fresh `random.Random(seed)` per kind (the literal `random.Random(seed).shuffle` of E-8), kinds sorted.
- G-5 C2 and C3: the chosen configuration's hyperparameters on the swapped inputs (PREREG §5 "the chosen
  configuration"; E-8's "the chosen configuration's family" read the same way), with its own threshold chosen by §3's
  rule on its own out-of-fold probabilities.
- G-6 Claims: "beats" = the full model right on more rows than the control (b > c) AND two-sided p < alpha.
- G-7 Balanced accuracy and AUC are null when a class is absent from the rows scored.
- G-8 `time` is parsed with datetime.fromisoformat (chronological order whatever the ISO spelling); unparseable refused.
- G-9 A held-out row whose kind has no training row is refused (the kind rule is undefined there).
- G-10 `explore` runs the controls for the named configuration too (the same record shape), with no verdict, no void
  checks and no claims.
- G-11 `--out` is also refused when its directory does not exist (checked before the fits run, not after).

Noted, not changed:
- N-1 E-7 makes a missing `--read-repeat` INCOMPLETE but says nothing of a missing `--twice`; by its letter the counts'
  verdict then stands. Implemented by the letter, with `void_checks.twice = "not run"` in the record and on stdout.
  PREREG §5 voids a run whose two records differ, so the coordinator's real run should pass `--twice` (or rule that a
  missing `--twice` is INCOMPLETE: a one-line change in `verdict`).
- N-2 PREREG §5 says a run is VOID when a §1 identity differs; E-1 refuses instead (no record at all). Stricter, kept.
- N-3 E-6 pins the word regex `[a-z0-9_]`; PREREG §4 says "letters, digits or underscores", so a non-ASCII letter is
  not a word character here. A reported baseline only.

## 3. Built (10:1xZ)

- `scripts/s1_train/heads.py`: the configurations (the block's grid, §3's order, stable names), the folds, `Data`, and
  the fits (torch imported inside `train` only): `train`, `score` (a fold's rows), `score_heldout`, `fit_fold`,
  `cross_validate` (out-of-fold per training row; held-out = the mean of the five fold models), `pair_loss` (E-4).
- `scripts/s1_train/evaluate.py`: the block (`prereg_block`, `check_block`), the input checks (`load`), the kind rule,
  the word overlap, the threshold rule, the metrics, McNemar (exact integers, `Fraction`), the PASS rule and the
  verdict, the choice, the controls, the record, and the CLI (`run`, `explore`); exit 3 on a refusal.
- `tests/test_s1_train_heads.py`: synthetic fixtures built in the test; pure tests and failure tests in this
  interpreter; torch tests in the Laya venv as subprocesses, LOUD SKIP outside the sandbox venue.
- Record fields beyond E-9's list:
  - `deviations` (D-1);
  - `counts_outcome` and `void_reasons` (what the counts alone say, and why VOID overrode it);
  - per control, a `labels` fingerprint (training yes rows per kind, labels changed) and `vs_full_model`;
  - `rows.fold_sizes`;
  - in `inputs`: `features_block_differences` (E-1's "recorded"), `features_extra_rows` and
    `features_extra_candidates`, and the `prereg_sha256` the features and tails were made with.
  Every McNemar entry carries `b_is`, which names what b counts.

Finding F-1 (first run, measured, not a code defect): on the planted fixture, C1 seed 1 MEETS the PASS rule (56 of 66
right, one-sided p 0.0047), seeds 2 and 3 do not, so C1 does not fire (1 of 3; the void rule needs 2). Cause, measured:
seed 1's within-kind shuffle still agrees with the true training labels on 91 of 143 rows (about 85 expected by
chance), and the planted signal is so clean (5 standard deviations) that a probe trained on those labels finds its
direction (held-out AUC 0.925). The labels did move (52 changed). So C1 is a null in expectation only: with a strong
real signal it can void a real PASS. Pre-registered (§5), not mine to change; the coordinator may want it in view.
My first test demanded 0 passing seeds (stricter than the brief) and was red; it now asserts the brief's property
(fewer than `C1_void_if_passing_seeds_at_least`), plus the count's consistency with the per-seed records.

## 4. Mutants (10:3xZ; a scratch copy of the five files, an empty package `__init__.py`; one exact edit each, the anchor
asserted unique; runner `<scratchpad>/s4-3-heads/mutants.py`)

Three runs, each over a green baseline on the scratch copy:
- 10:19Z: `BASELINE rc=0 46 passed in 62.74s (0:01:02)`. M1 to M16 red; M17 SURVIVED (46 passed).
- 10:32Z, after `claims()` and the new tests: `BASELINE rc=0 50 passed in 85.04s (0:01:25)`. Every mutant red.
- 10:47:51Z to 10:54:17Z, on the FINAL bytes (sha256 in section 5): `BASELINE rc=0 51 passed in 95.42s (0:01:35)`.
  Every mutant red, with the same first assertion line as at 10:32Z.

The table shows the final run.
M1 to M11 are the brief's eleven (M1b and M6b the same fault at its other site); M12 to M29 are mine, each aimed at a
behaviour the self-attack found unpinned (M17 first SURVIVED, before `claims()` and its test existed: 46 passed).

| # | Mutant (one exact edit) | Named test | Result | First assertion line |
|---|---|---|---|---|
| M1 | threshold chosen on the held-out rows (judge re-fits τ) | test_held_out_rows_are_called_at_the_out_of_fold_threshold | RED 1 failed | `assert (0.41000000000000003 == 0.55)` |
| M1b | the same, at the call site | test_the_record_follows_the_rules_it_reports | RED 1 failed | `assert 0.5362427534535528 == 0.32803624495863914` |
| M2 | configuration chosen on the held-out rows | test_the_record_follows_the_rules_it_reports | RED 1 failed | `assert False` (accuracies not over the 143 training rows) |
| M3 | McNemar two-sided where one-sided is pinned | test_the_verdict_table | RED 8 failed, 3 passed | `AssertionError: PASS` |
| M4 | b and c swapped | test_mcnemar_is_exact_against_hand_values | RED 1 failed | `assert (1, 9, 10) == (9, 1, 10)` |
| M5 | kind rule taken from the held-out rows | test_kind_rule_is_the_training_majority_and_a_tie_is_refused | RED 1 failed | `{'j': True, 'k': False} == {'j': False, 'k': True}` |
| M6 | C1 shuffled across kinds (call site) | test_the_record_follows_the_rules_it_reports | RED 1 failed | `{'kind-a': 34...} == {'kind-a': 20...}` |
| M6b | C1 shuffled across kinds (inside the permutation) | test_c1_permutes_inside_each_kind_and_c1b_across_kinds | RED 1 failed | per-kind yes counts differ |
| M7 | folds in id order instead of time order | test_folds_cut_each_kind_by_time_then_id | RED 1 failed | `{'x1': 0, ... 'x4': 1} == {'x4': 0, ... 'x1': 1}` |
| M8 | held-out score from fold 0's model alone | test_the_held_out_probability_is_the_mean_of_the_five_fold_models | RED 1 failed | `assert (0.15304038524627683 <= 1e-12)` |
| M9 | C1 void rule off | test_the_verdict_table | RED 1 failed, 10 passed | `AssertionError: VOID by C1` |
| M10 | read-repeat rule off | test_the_verdict_table | RED 1 failed, 10 passed | `AssertionError: VOID by the read repeat` |
| M11 | a seed not set (`torch.manual_seed` before a fit) | ..._mean_of_the_five_fold_models + test_a_planted_signal_passes_and_c1_does_not_fire | RED 2 failed | `assert (False is True)`; the planted records read `VOID` by `twice: the two records differ` |
| M12 | a seed not set (the batch-order generator) | test_the_batch_order_follows_the_seed | RED 1 failed | seeds 441 and 442 give one order |
| M13 | InfoNCE state clause dropped (E-4) | test_pair_loss_masks_same_candidate_and_same_state | RED 1 failed | `assert 0.19463873972122436 < 1e-09` |
| M14 | JSONL split with `str.splitlines` (AF-AP-132) | test_the_fixture_passes_every_input_check | RED 1 failed | a raw U+2028 cut a view line: `JSONDecodeError` |
| M15 | threshold tie to the smaller τ | test_threshold_rule_takes_the_tie_closest_to_one_half | RED 1 failed | `assert (0.2, 3) == (0.75, 3)` |
| M16 | train-side HeldOut guard off | test_a_held_out_row_handed_to_a_fit_is_refused | RED 1 failed | `ModuleNotFoundError: No module named 'torch'` (no HeldOut) |
| M17 | claims without the direction check (b > c) | test_a_claim_needs_the_full_model_ahead_and_a_two_sided_p_below_alpha | RED 1 failed | `['the session state helps'] == []` |
| M18 | B's C2 reads c_ctx (the state) | test_c2_reads_no_state_and_c3_another_input | RED 1 failed | B C2 spread within a candidate > 1e-6 |
| M19 | A's C2 keeps s (no zeros) | test_c2_reads_no_state_and_c3_another_input | RED 1 failed | A C2 spread within a candidate > 1e-6 |
| M20 | seed without + fold | test_the_held_out_probability_is_the_mean_of_the_five_fold_models | RED 1 failed | `assert False is True` (seed_follows_fold) |
| M21 | scoring in train mode | test_the_held_out_probability_is_the_mean_of_the_five_fold_models | RED 1 failed | `(True is True and False is True)` (repeatable) |
| M22 | mean and sd over every row (held-out included) | test_the_held_out_probability_is_the_mean_of_the_five_fold_models | RED 1 failed | `assert 0.0718112340350331 < 1e-09` |
| M23 | sd floor off | test_the_held_out_probability_is_the_mean_of_the_five_fold_models | RED 1 failed | the constant column gives 0/0; LBFGS: `RuntimeError: value cannot be converted to type float without overflow` |
| M24 | A's tower without LayerNorm | test_the_heads_are_the_models_e4_names | RED 1 failed | the layer lists differ |
| M25 | word-overlap threshold fit on the held-out rows | test_the_record_follows_the_rules_it_reports | RED 1 failed | `assert 0.3819444444444444 == 0.256578947368421` |
| M26 | `--twice` always "identical" | test_twice_voids_a_run_whose_two_passes_differ | RED 1 failed | `('PASS', 'PASS') == ('VOID', 'PASS')` |
| M27 | C1b with C1's first seed | test_the_record_follows_the_rules_it_reports | RED 1 failed | C1b's per-kind yes counts are not seed 4's |
| M28 | McNemar's arguments swapped at the call site | test_a_planted_signal_passes_and_c1_does_not_fire | RED 1 failed | `('NOT SHOWN' == 'PASS'` |
| M29 | exp(t) not clamped | test_the_heads_are_the_models_e4_names | RED 1 failed | `assert 1000.0001220703125 == 100.0` |

Finding F-2 (measured while building the C2 signature test, not a code defect): a CPU kernel can round two IDENTICAL
input rows apart by their place in a batch. Fold 0 scores seven identical `q_free` rows in one batch and gets
0.5550426244735718 for six and 0.555042564868927 for the seventh (one float32 ulp); scored one at a time, all seven
agree. Determinism is not affected (the same inputs in the same batch give the same bits, which the two-run and
`--twice` tests prove), but a probability is batch-dependent at about 1e-8. The test compares within 1e-6.

## 5. Gates on the final bytes (10:5xZ)

Final sha256: heads.py `f3187e1b30a9dbe990b732b5ec19e12fb73a4fc47a7b30f91668c43319b75c50`, evaluate.py
`12f8ea0d492ca27f48f361e086793c6c9fc06ccad09a22a54c44acf5e57a5407`, test_s1_train_heads.py
`8d19d90ed7e92dc65be80c80ab3f9867c903c5943c7195071a231d78ae089344`.

- `bash scripts/test_summary.sh --basetemp <scratch>/gate2/bt1 tests/test_s1_train_heads.py` (PYTHONDONTWRITEBYTECODE=1
  S0_01_VENUE=sandbox HF_HUB_OFFLINE=1), run 1: `pytest-exit: 0` / `pytest-summary: 51 passed in 82.11s (0:01:22)`
- the same, run 2: `pytest-exit: 0` / `pytest-summary: 51 passed in 83.99s (0:01:23)`
- `bash scripts/pc_suite.sh set-id -- tests/test_s1_train_heads.py`: `1 files set=e8d6713191fd`
- `tests/test_s1_train_features.py` once (not changed): `pytest-exit: 0` / `pytest-summary: 16 passed in 0.08s`
- pyflakes on heads.py, evaluate.py, test_s1_train_heads.py: rc 0, no output.
- Separator check `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: heads.py 0, evaluate.py 0, test_s1_train_heads.py 0, this report 0.
  (The first check found 4 in the test file: the Write tool had turned my `\u2028` escapes into the raw character, and
  `\u00e9` into a raw é. Rewritten by a byte-exact script; every string constant of the file's AST proven identical
  before and after, so no runtime value changed.)
- `python3 scripts/ap_screen.py heads.py evaluate.py test_s1_train_heads.py`: 9 hits; `--tests` on the test file: 1 hit.
  Each answered:
  - AF-AP-72 x5 (heads.py:252 `float(config["logit_scale_init"])`; evaluate.py:379 x2, :597, :607 `float(...p_one_sided)`):
    no upstream field is coerced. heads.py:252 converts a value `configurations()` already checked as a finite
    non-bool int or float (an int init needs the float for a trainable tensor); the evaluate.py ones convert the
    `Fraction`s `mcnemar()` itself made, for the record and the stdout line.
  - AP-32 x2 (evaluate.py:49, test:60 `hashlib.sha256(b).hexdigest()`): the hashed form is the file's raw bytes, which
    is what the block pins (`view_jsonl_sha256` of view.jsonl) and what E-1 says of `tails_sha256` ("its file's own").
  - AP-1 (test:507 `os.environ.get("S0_01_VENUE")`): the venue declaration read once in the module fixture for the
    LOUD SKIP, the pattern tests/test_laya_ft.py:680 uses (the brief's model); not a config channel of the code under test.
  - AP-51 (test:16, the docstring's "byte-identical records"): I did not read the registry row (out of my boundary);
    the matched text is a byte-identity claim, and it is backed by a test that runs twice and compares bytes
    (`test_two_runs_give_byte_identical_records`) and by `--twice` (identical in the planted runs, VOID under an
    injected fault and under mutant M11).
  - AF-AP-80 (test:488 `(tmp_path / "taken.json").read_text() == "OLDER RECORD\n"`): reads the older OUTPUT after the
    refusal to prove it was not overwritten (state, not source text), paired with the refusal message.

## 6. Evidence tiers

Verified (run here, exit codes read):
- The premise (section 1); the 51 tests twice; the features file's 16; set-id; pyflakes; separators; 31 mutants red.
- In the Laya venv (torch 2.14.0+cpu, Python 3.11.15) on synthetic features:
  - the planted signal gives PASS (65 of 66 held-out rows right, the kind rule 42);
  - C1 does not fire (1 of 3 seeds meets the PASS rule; F-1);
  - two processes give byte-identical records and stdout; `--twice` gives "identical", and VOID under a fault the
    test injects into the second pass;
  - no signal is not PASS; no read repeat gives INCOMPLETE over a PASS count;
  - explore, the held-out mean of the five fold models, the out-of-fold split, the HeldOut refusals;
  - the C2 and C3 signatures, E-4's layer stacks, the exp(t) clamp, family A's loss against a plain-math oracle.
- Single-fit times at the real size (696 training rows per fold, d = 1024): B logreg 1.2 s, B MLP 0.8 s (20 epochs) and
  1.8 s (60), A 1.7 s (1 layer, 20 epochs) and 6.8 s (2 layers, 60).

Inferred (not run end to end):
- The real run's wall time: about 230 s per §3 procedure, so about 20 min per evaluation (main, 3 C1 seeds, C1b, C2,
  C3) and about 40 min with `--twice`; extrapolated from the single fits on random features (LBFGS may converge
  sooner or later on real ones).
- torch 2.7.1 (the PC) has every API used: nn.Module, Linear, LayerNorm, GELU, Dropout, F.normalize, logsumexp,
  masked_fill, eye(bool), LBFGS(line_search_fn), AdamW, Generator, randperm(generator=), use_deterministic_algorithms.
  Read from the APIs, not run there.
- CI: the 38 main-interpreter tests ran here with no torch, so they need none; the 13 Laya tests take the LOUD SKIP
  (the same fixture as test_laya_ft.py). Not run without the venue, because every run here set S0_01_VENUE=sandbox
  per the standing rules.

Assumed:
- That read.py's real outputs carry the shapes THE INPUTS copies: features `meta.prereg_block` / `prereg_sha256`, the
  tails manifest keys, and `read.py compare`'s `{"arrays": ..., "min": ...}`. read.py landed at b9f835de during this
  lane; I did not read it (boundary). Every key is checked, so a mismatch REFUSES with its reason rather than
  mis-scoring; the first real run is the check.
- That the view's `time` is an ISO string; parsed with fromisoformat, a trailing Z read as +00:00.

## 7. Self-attack: the three most likely ways this change is wrong

1. **Family A trains the wrong loss (D-1).** The brief masks same-state rows; the prereg's text masks same-candidate
   rows only. Not ruled out: SURFACED for a ruling, recorded in every record's `deviations`, and pinned by
   `test_pair_loss_masks_same_candidate_and_same_state` (mutant M13 drops the state clause: red).
2. **A seam with read.py differs, so the real run refuses (or, worse, reads the wrong field).** Ruled in part: each
   key is read by name and checked, so a missing or different key refuses with its reason (the tests show each
   refusal). That holds for the view and tails sha256s, the counts, the block keys, and coverage of every row and
   candidate. Not ruled out: that the names match read.py's actual output. Assumed, not verified (section 6).
3. **Held-out information leaks into the choice or the training.** Ruled out by:
   - mutants M1, M1b (threshold re-fit on held-out), M2 (configuration chosen on held-out), M16 (HeldOut guard off),
     M22 (standardization over every row) and M25 (word-overlap threshold on held-out), all red;
   - the HeldOut refusals, tested in both interpreters.
   The held-out probabilities of every configuration exist in memory, but `choose()` reads only "oof", and M2 is red.

## 8. Discrepancies and findings (beyond section 2's D-1, G-1..G-11, N-1..N-3)

- F-1 (section 3): C1's within-kind shuffle is a null only in expectation. On a strong signal, one seed met the PASS
  rule. With a strong REAL signal, C1 could void a real PASS (2 of 3 seeds); pre-registered, for the coordinator's view.
- F-2 (section 4): CPU kernels round identical rows apart by batch position (about 1e-8). Determinism holds within one
  Python, but probabilities are batch-dependent at that level.
- T-1: the Write tool converts `\uXXXX` escapes in file content into raw characters (4 raw U+2028 and one é landed in
  the test file). Caught by the brief's separator gate and fixed. A candidate env-tool-quirks entry (the coordinator's
  call; skills are out of my boundary).
- HEAD moved during the lane: b0039f4 at the start, f2e32df5 at the end. Task #471 landed at b9f835de; the coordinator
  also modified todo/BUILD-TASKLIST.md and wiki/topics/live-state.md and added VERIFY-S4-2-READ-brief.md (none mine).
  `git diff --stat PIN HEAD` over features.py, test_s1_train_features.py and PREREG-441.md: 0 lines at the end too.
- The edit-snapshot hook's registry screen (after my first Write of evaluate.py) flagged AF-AP-132 (`str.splitlines`
  on JSONL that can hold a raw U+2028) before any run. Fixed (`_lines` splits on "\n" only), and pinned by a fixture whose candidates and
  tails carry a raw U+2028, with mutant M14 red. Not logged in docs/INCIDENT-LOG.md (out of my boundary).

## 9. NOT done

- NOT run on the real features: they do not exist yet (demand 9). The coordinator runs `evaluate.py run ...
  --read-repeat <compare output> --twice` once they do.
- NOT run on the PC's venv-rwkv-b (torch 2.7.1): no bridge in this lane.
- NOT checked against read.py's real outputs (boundary); see the Assumed tier.
- NOT pinned by any test or mutant:
  - LBFGS's `max_iter` and `strong_wolfe` wiring;
  - AdamW's lr and weight-decay values;
  - the L2 term excluding the bias;
  - `t`'s initial value (the clamp IS pinned);
  - the exact cv seed value 441 (seed + fold IS pinned).
- No commit, no push, no ledger or incident-log edit (the coordinator's). `report_lint.py` not run: the files are new,
  absent at any committed rev.

## 10. Files and lines (all new; nothing else touched)

- `scripts/s1_train/heads.py`, 340 lines. Symbols start at: configurations 66, when 99, folds 110, Data 135,
  _batches 174, _inputs 185, _tower 193, _pair 202, pair_loss 209, train 227, _probs 290, score 309,
  score_heldout 315, fit_fold 323, cross_validate 332.
- `scripts/s1_train/evaluate.py`, 640 lines: prereg_block 85, check_block 120, load_view 148, load_features 178,
  load_tails 208, load_read_repeat 236, kind_rule 245, words 261, jaccard 266, load 272, threshold 306, log_loss 319,
  auc 326, metrics 337, mcnemar 364, meets_pass_rule 386, verdict 392, choose 417, judge 436,
  permute_within_kind 446, permute_all 461, evaluate 499, claims 555, run 579, explore 602, main 611.
- `tests/test_s1_train_heads.py`, 931 lines: 41 test functions, 51 items (the verdict table has 11 cases). 13 run
  in the Laya venv; 38 run in this interpreter.
- `tasks/briefs/jev-laya/S4-3-HEADS-report.md`: this report.
- Scratch, not for commit: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/s4-3-heads/`
  (mutants.py, the mutant copies, the gate logs).

## Coordinator's harvest notes (2026-10-02 11:0xZ)

- **D-1 ruled: keep E-4.** Two yes rows at one state share `s`, so either direction would score a positive as a
  negative. `docs/research/findings/s1-train/PREREG-441.md` was amended at 11:0xZ, before the GPU window and before
  any feature existed, as its STATUS line allows: §3 now names the same-state mask; the amendment also freezes this
  report's §2 readings (G-1 to G-11) and says the run of record passes `--read-repeat` and `--twice` (N-1). Its §8
  block is byte-identical to the one before the amendment.
- **`scripts/s1_train/evaluate.py` changed by the coordinator:** `DEVIATIONS` is now `[]` (with a three-line
  comment that keeps the file at 640 lines, so this report's line citations hold). Its sha256 is now
  `aa76246b0237f43d1b5e94bbb0ccf76e5ae00b965485a762655c2310bc7610d6`, not §5's. `heads.py` and the test file are
  unchanged.
- **One citation corrected:** §5's AP-1 line cited the venue lookup two lines above the skip; the `LOUD SKIP` is
  at `tests/test_laya_ft.py:680`.
