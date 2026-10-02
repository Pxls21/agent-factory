# S4-2-READ (task #471) report: the reading program of the first S1 training

Lane: sandbox code-implementer (Opus 5.5). Brief: `tasks/briefs/jev-laya/S4-2-READ-brief.md`, PIN b1df2d35.
Report started 2026-10-02 09:4xZ. Written incrementally; the final section is the verdict.

## 1. Premise (evidence demand 1), re-measured at HEAD b0039f4d4bbf4c052837433487774b252212d4ab

Every command of the brief's premise block was re-run at HEAD. Every output matches the brief:

- the PIN resolves to b1df2d3508155b8b664750e715f680505e113eb7 and is an ancestor of HEAD;
- `git diff --stat PIN HEAD -- <the five paths>` is 0 lines;
- `scripts/s1_train/` holds `__init__.py features.py render.py view.py`; read.py and the test file are absent;
- sha256 prefixes: features.py 6a32c42d16299365, render.py 901c086a6a90f90a, view.py 4629e0c720edaa82;
- view.py: read_manifest L161, stream_events L191, check_out L376;
- render.py: VERSION L34, CAP L35, body L71, block L100, render L117;
- features.py: VERSION L21, ROW_ARRAYS L22, FREE_ARRAYS L23, write L47, read L104;
- rwkv7_g0.py lines 137-149 hold 2 `from_pretrained`;
- numpy, torch, transformers, fla: none importable (`[]`);
- features + view tests: `112 passed`.

Verdict: the premise holds. No STOP.

## 2. Build status (written 10:2xZ)

- `scripts/s1_train/read.py` written: the five subcommands `tokens`, `read`, `tails`, `compare` and `smoke`; the fake
  and fla backends; the fake and hf tokenizers.
- `tests/test_s1_train_read.py` written: 52 tests. The fixtures go through the real producers: the exporter CLI
  (init-key, a fixture repo, `--known-values key-only`), `build_s1.write_split` and `view.py`. The oracle is the
  test's own.
- Mutants: 23 run on a scratch copy of the tree (the brief's 12 and 11 extras). All 23 are KILLED; the table is in §5.
- One harness finding, fixed in the test and the driver: M4's first run read SURVIVED, but the mutant had made the
  `world` fixture fail. `read` refused the shifted positions, 47 tests errored, and the driver's regex counted the
  errors as tests. The read run now has its own fixture (`feats`), so the position test fails by name, and the driver
  reports an error-only mutant as ERRORED, never as KILLED.

## 3. Files and lines (evidence tier: verified, `wc -l`, `grep -n`)

All three files are new and untracked. I touched no other file; `git status --short` shows no modified tracked file.
The other lane's files (`scripts/s1_train/heads.py`, `scripts/s1_train/evaluate.py`, `tests/test_s1_train_heads.py`) are
in the tree, and I did not open them.

- `scripts/s1_train/read.py` (789 lines, sha256 8af6a2bced1fef74…):
  - R-1: read.py:143 `read_prereg`, read.py:126 `json_blocks`.
  - R-2: read.py:181 `read_inputs`.
  - R-3 and R-4: read.py:441 `stream` (each block tokenized on its own), read.py:454 `cmd_tokens`.
  - R-4's tokenizers: read.py:286 `FakeTokenizer`, read.py:312 `HFTokenizer`.
  - R-5: read.py:488 `load_tokens` (every token file's sha256 checked first), read.py:526 `forward`.
  - R-5: read.py:535 `read_file`, read.py:606 `cmd_read`.
  - --work: read.py:557 `open_work`, read.py:574 `load_record`, read.py:590 `save_record`.
  - R-6: read.py:344 `FakeBackend`, read.py:378 `FlaBackend`.
  - R-7 and R-8: read.py:680 `cmd_tails`, read.py:695 `cmd_compare`, read.py:715 `cmd_smoke`.
  - R-9: read.py:248 `_named` (refuses a dot-dot part), read.py:255 `check_out` (view.py's D-10 rule, reused).
  - The CLI: read.py:752 `main`.
- `tests/test_s1_train_read.py` (870 lines, sha256 ea91d683d53c384f…):
  - Fixtures: test:394 `world`, test:430 `feats`, test:439 `oracle`.
  - The oracle: test:95 `encode` (a regex tokenizer), test:109 `fold` (the fake update rule, written out).
  - 52 tests, from test:473 `test_the_fixture_holds_the_shapes_the_rules_need`
    to test:854 `test_a_resumed_run_equals_an_uninterrupted_run_byte_for_byte`.
- `tasks/briefs/jev-laya/S4-2-READ-report.md`: this report.

## 4. Test counts (pasted; evidence tier: verified)

Environment of every run: `PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1`, no `-n`. I also set
`TMPDIR=<my scratch>/tmp`, so the test's output root (`tempfile.mkdtemp`, outside any git work tree) lands in my
scratch directory. Without TMPDIR it lands in the system temp directory, as the view test's does.

`bash scripts/test_summary.sh --basetemp <scratch>/gateN/bt tests/test_s1_train_read.py`, run twice:

```
pytest-exit: 0
pytest-summary: 52 passed in 7.51s
pytest-exit: 0
pytest-summary: 52 passed in 7.25s
```

`bash scripts/pc_suite.sh set-id -- tests/test_s1_train_read.py` prints `1 files set=9b7b5a45ec51`. The file runs in
about 7.5 s, under the brief's two minutes.

The sibling tests, run once (I changed neither file): `tests/test_s1_train_features.py tests/test_s1_train_view.py`
print `pytest-summary: 112 passed in 10.05s`, over `2 files set=97c76a7319da`.

Final check (10:3xZ), at HEAD (b0039f4d plus the coordinator's local 09:5xZ ledger commit), with both files unchanged (the sha256 prefixes in §3), one more run:

```
pytest-exit: 0
pytest-summary: 52 passed in 7.31s
```

Red-green: I wrote the tests after the code, so no test was first run red against a version without the code. The red
proof is the mutant table in §5: each mutant makes a named test fail with an assertion.

## 5. Mutants (evidence demand 7; evidence tier: verified)

Method (anti-hollow-green 3a to 3c). The scratch tree is `git archive HEAD` (that same HEAD) of `scripts src
docs/research/findings pyproject.toml tests/conftest.py`, plus my two working files, `cmp`-equal to the tree's. Each
mutant is one exact edit, whose old text occurs exactly once in the file. The baseline runs first: `52 passed`. Each
mutant must compile and must collect all 52 tests, or it is INVALID. KILLED means at least one FAILED line, with an
assertion. An error-only run is ERRORED, never KILLED. Every run uses `PYTHONDONTWRITEBYTECODE=1`, with `__pycache__`
removed first. The denominator is the literal `EXPECTED=23`. A copy of the driver with one row deleted stops at once
(`AssertionError: 22`, rc 1).

Final run, on the final files (read.py 8af6a2bced1fef74…, test ea91d683d53c384f…):
`BASELINE rc=0 n=52 | 52 passed`, then `EXPECTED=23 KILLED=23 SURVIVED=0 ERRORED=0 INVALID=0`.

| id | mutant (one exact edit) | verdict | first named test that fails, and its assertion |
|---|---|---|---|
| M1 | the candidate read on the original state (`cp = backend.copy(state)` to `cp = state`) | KILLED | `test_every_feature_equals_the_oracle`: `('s', 's1-00004a02')`, s[0] −105.6484375, oracle −89.640625 |
| M2 | `s` taken after the candidate (`"s": s` to `"s": c_ctx`) | KILLED | `test_every_feature_equals_the_oracle`: `('s', 's1-00004a01')` |
| M3 | the whole text tokenized at once (`ids += tok.encode(text[a:b])` to `ids = tok.encode(text[:b])`) | KILLED | `test_the_token_streams_and_positions_equal_the_oracle`: the ids differ (and 3 more tests) |
| M4 | a row position one block late (`at[a] = len(ids)` plus the block's own tokens) | KILLED | `test_the_token_streams_and_positions_equal_the_oracle`: `['s1-00004a01', 683] != ['s1-00004a01', 329]`; the `feats` fixture errors too (read refuses the shifted last position) |
| M5 | the short window not from the zero state (`backend.zero()` to `backend.copy(state)`) | KILLED | `test_every_feature_equals_the_oracle`: `('s_w', 's1-00004a01')` |
| M6 | the window length ignored (`ids[max(0, pos - window):pos]` to `ids[:pos]`) | KILLED | `test_every_feature_equals_the_oracle`: `('s_w', 's1-00004a02')` (a row past the window) |
| M7 | the render sha256 check off | KILLED | `test_a_summary_stream_sha256_that_is_not_the_renders_is_refused[tokens]` and `[tails]`: `(0, '')`, the run passed |
| M8 | the token-file sha256 check off | KILLED | `test_a_token_file_whose_bytes_changed_is_refused[1.tok]` and `[candidates.tok]`: the read ran (rc 0) |
| M9 | the free arrays keyed by row | KILLED | `test_every_feature_equals_the_oracle`: the free keys are the row ids (and 4 more tests) |
| M10 | the git-work-tree refusal off (`V.check_out(out)` to `pass`) | KILLED | `test_an_output_inside_git_named_with_dotdot_or_not_empty_is_refused[git_work_tree-tokens]`: `(0, 's1-read ... 17 blocks\n') == (2, '')` (9 tests in all) |
| M11 | the `..` refusal off | KILLED | `…[dotdot-tokens]`: `(0, 's1-read ... 17 blocks\n') == (2, '')`; also `[dotdot-tails]`, `[dotdot-work]`, `test_reads_own_arguments_are_refused_before_the_run[out_dotdot]` |
| M12 | the question block read from the zero state (`backend.read(cp, q_ids)` to `backend.read(backend.zero(), q_ids)`) | KILLED | `test_every_feature_equals_the_oracle`: `('q_ctx', 's1-00004a01')` |
| X1 | extra: the three input sha256 checks off | KILLED | `test_an_input_whose_sha256_is_not_the_blocks_is_refused` (6 cases) |
| X2 | extra: the `state_end > 0` check off | KILLED | `test_a_state_end_that_is_not_a_block_start_or_is_zero_is_refused[zero-*]` |
| X3 | extra: the block-start check off | KILLED | `…[inside_a_block-*]` |
| X4 | extra: two prereg blocks taken | KILLED | `test_a_prereg_without_exactly_one_valid_block_is_refused[two]` |
| X5 | extra: the `{body}` exactly-once check off | KILLED | `test_a_candidate_block_without_body_exactly_once_is_refused` (4 cases) |
| X6 | extra: the candidate sha256 check off (my added refusal, §8 D-5) | KILLED | `test_a_candidate_whose_sha256_is_not_its_rows_is_refused` |
| X7 | extra: a resumed file's forwards not restored | KILLED | `test_a_resumed_run_equals_an_uninterrupted_run_byte_for_byte`: `index.json` differs |
| X8 | extra: `c_free` read from a state that is not zero | KILLED | `test_every_feature_equals_the_oracle`: `('c_free', 'cfce96d9…')` |
| X9 | extra: each tail one character too long | KILLED | `test_tails_hold_each_rows_last_characters` |
| X10 | extra: the smoke's copy check always passes | KILLED | `test_smoke_fails_a_backend_that_breaks_a_check[copy_is_the_original]`: `0 == 1` |
| X11 | extra: the --work binding check off | KILLED | `test_a_work_dir_of_another_run_is_refused` |

The harness finding from the first run is in §2. M4 first read SURVIVED: the driver's regex counted 47 fixture errors
as tests and found no FAILED line. The repair is in the test (read has its own fixture, so the position test fails by
name) and in the driver (an error-only run is ERRORED). The driver and its logs are in my scratch directory
(`s4-2-read/mut/`), not in the tree.

## 6. Gates (evidence demand 9; evidence tier: verified)

- pyflakes on both new files: rc 0, no output. The report holds no code.
- The separator check, `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: read.py 0, test 0, report 0.
- `python3 scripts/ap_screen.py --limit 100 scripts/s1_train/read.py tests/test_s1_train_read.py` gives
  `17 hits over 2 files`. `--tests` over the test file gives `0 hits`. Each tell, answered:
  - AP-32 (is the hashed form exactly what the store holds?), 16 tells:
    - read.py:81 and read.py:82: the `sha256` helper hashes the bytes it is given.
    - read.py:171: `sha256` of the prereg file's bytes, read once and parsed from the same bytes.
    - read.py:189: `sha256` of view.jsonl, summary.json and the export manifest, each read once, hashed and parsed
      from the same bytes.
      `view.read_manifest` reads the manifest again, so its parse is compared with the hashed parse (refused as "changed
      while it was read").
    - read.py:466 and read.py:479: `sha256` of each .tok file's bytes, exactly as `_put` writes them.
    - read.py:500: `sha256` of each token file's bytes, read once and decoded from the same bytes.
    - read.py:523: `sha256` of the tokens manifest's bytes, the ones parsed.
    - read.py:689: `tails_sha256` over the bytes written as tails.jsonl.
    - read.py:346 and read.py:368: `sha256` in the fake embedding, not a stored hash.
    - test:70: `MARK`, the marker's name.
    - test:105: `sha256` in the oracle's embedding, over the same bytes as read.py's (the oracle test agrees bit for
      bit).
    - test:282: `sha256` of file bytes, as read.py hashes them.
    - test:628: `tails_sha256` of tails.jsonl read back.
    - test:664: a `sha256` planted wrong (a negative control).
  - AP-51 (a byte-identity claim), 1 tell, read.py:40 (`byte-identical`): there is no dataclass and no asdict sink. The claim is tested
    file by file by `test_two_runs_give_byte_identical_outputs` and by the resumed-run test.
- `python3 scripts/report_lint.py` over this report, with the aliases read.py, test, view and pyproject.toml mapped:
  `report_lint: 52 refs — OK 52, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`. The two earlier runs had
  MISS and UNCHECKABLE lines. Each one was a token missing from the report line, never a wrong line number.

## 7. Evidence demands, one by one

1. The premise: §1, all matched. HEAD later moved one ledger commit past b0039f4d (the coordinator's 09:5xZ retro entry). I re-measured the premise diff over
   the five paths at that HEAD: 0 lines. (verified)
2. The fixtures, through the real producers: the exporter CLI (`init-key` FAKE key, a fixture repo,
   `--known-values key-only`), `build_s1.write_split`, then `view.py`. The fixture block is PREREG-441's own block with
   the fixture's sha256s (computed in the test), `short_window_tokens` 400 and `state_tail_chars` 150. The session
   holds:
   - six scored injections in two files;
   - ID_TWO1 and ID_TWO2 on one call (one position, 1821; two rows);
   - two rows with one candidate;
   - one candidate over the render's cap (4,034 tokens);
   - a thinking block with a marker in each file;
   - rows at positions 329 and 286 (inside the window) and 730, 1821, 1821 and 770 (past it).

   `test_the_fixture_holds_the_shapes_the_rules_need` asserts these shapes. (verified)
3. Normal tests (verified):
   - every row's six arrays and every candidate's two equal the oracle, through float32
     (`test_every_feature_equals_the_oracle`);
   - the positions, the ids, the block counts and the candidate spans equal the oracle's
     (`test_the_token_streams_and_positions_equal_the_oracle`);
   - `compare` of a run with itself reads 1.0, and `compare` over known vectors reads 1/sqrt 2, 1 and −1;
   - `smoke --backend fake` passes; each of its two checks fails against a broken backend (exit 1);
   - the tails hold each row's last 150 characters;
   - the meta holds exactly the five keys, its forward count derived independently.
4. Failure tests, each with the exact exit code (2) and the named reason (verified):
   - the view's, the summary's or the export manifest's sha256 not the block's (×2: tokens and tails);
   - a summary stream sha256 that is not the render's (×2);
   - a `state_end` inside a block, the view and its block sha256 both changed (×2);
   - a `state_end` of 0 (×2; the test asserts 0 is a block start, so only `> 0` can refuse it);
   - a token file whose bytes changed (1.tok, candidates.tok);
   - a prereg with no block, two blocks or invalid JSON;
   - a `candidate_block` with `{body}` missing or twice (×2);
   - an output inside a git work tree, named with `..`, or not empty, for tokens, tails and --work (9 cases; for `..`,
     the test asserts the missing part was never created and the full directory is unchanged);
   - a --work of another run; an unknown `--only`; read's own arguments; a candidate whose sha256 is not its row's.
5. The security boundary (verified):
   - the thinking marker reaches the export (before every state) and is in no token stream (decoded with the test's
     own fake decoder), no question ids, no manifest and no tail;
   - a FAKE key (`session_export.CANARIES["gh-result"]`, built at run time, never printed) is planted after the export
     in a coordinator text and in a candidate. The export manifest's sha256 and the block's sha256s follow (view.py
     re-run). The key is in no token stream, no tail and no output of the runs, checked by 8-character windows. The
     scrub's mark ` key gh<redacted>` is read twice (in the state and in the candidate): the text was read, not lost;
   - the copy rule is the oracle's (`s` is a fold of the stream alone). The fixture test shows that a candidate read
     on the original state changes ID_POST's `s`.
6. Determinism: two runs of tokens, read and tails are byte-identical, every file. `--only=` the first file into a
   --work, then a full run with the same --work, equals the full run without it, byte for byte. That run prints
   `2 files (1 resumed)`, and timings.json marks file 0 resumed. (verified)
7. Mutants: §5. (verified)
8. Test runs: §4. (verified)
9. Gates: §6. (verified)
10. NOT run here: §10.

## 8. Discrepancies and deviations (flagged)

- **D-1, inside the brief: R-1 against R-7.** R-1 says every output's manifest records the prereg file's sha256 and a
  copy of the whole block. R-7 gives the tails manifest "exactly the keys" prereg_sha256, view_jsonl_sha256,
  view_summary_sha256, export_manifest_sha256, count and tails_sha256. I followed R-7: the tails manifest holds the
  prereg sha256 and not the block. The tokens manifest and the features meta hold both.
- **D-2, a gap in R-4.** The rows pair `[row id, token position]` names no candidate, but `read` must know each row's
  candidate. So the tokens manifest has one more top-level key, `candidate_of` ({row id: candidate sha256}); the rows
  pair is as the brief specifies.
- **D-3.** R-4's per-file "key" is the field `src` (the export's key); the entry also names its `file` (`<k>.tok`).
- **D-4.** An exported src starts with `-`, which argparse reads as an option. So `--only` takes one src per occurrence,
  in the `--only=SRC` form, repeatable, not `--only <src> ...`.
- **D-5, an added refusal.** A row whose `candidate_sha256` is not the sha256 of its candidate is refused: the free
  arrays and candidates.tok are keyed by it. It has a test, and mutant X6 is killed.
- **D-6, added.** `smoke --out` must not exist (a result is never written over). A failing smoke exits 1 and still
  writes its result; a refusal exits 2.
- **D-7, added.** `read` checks its own --out (no `..`, missing or empty) and `--segment >= 1` before the run.
  features.write would refuse such an --out only after every read, and a GPU window is scarce. It has a test.
- **D-8, how I read --work.** R-9 refuses a non-empty --work, and R-5 resumes from one. A non-empty --work is taken
  only when it holds this run's `work.json` (the tokens manifest sha256, the backend identity and the segment). Any
  other non-empty --work is refused, as "holds another run's work" or by view.py's "not an empty directory". On a
  resumed run, D-10's git rule runs on a probe path inside --work, which covers --work and every parent. Each record is
  a features-format directory `<work>/<k>`, written as `<k>.part` and then renamed; a stale `<k>.part` is removed
  (`shutil.rmtree`) before it is written again.
- **D-9.** The candidate and the question blocks are read in one forward each. The `--segment` limit applies to the
  stream and the window reads, where R-5 names it. This makes no difference with the fake backend; with fla, the
  largest candidate block is about 4,030 tokens.
- **D-10.** The fake tokenizer has R-4's five pieces plus `"\n\nA"` (the Agent label after a blank line).
- **D-11.** Backend identities. The fake's: name, version, decay table and device `cpu` (it has no weights). The
  fla's: the torch, transformers and fla versions, `weights_sha256` over each `*.safetensors` file in the model
  directory (file names only), dtype and the device name.
- **D-12.** `counts.tokens` is keyed by src: the stream tokens read per file. `counts.forwards` counts every
  `backend.read` call (stream, window, candidate, question and free reads).

## 9. Adjacent observations (reported, not fixed)

- **A-1, a latent collision in a sibling test.** In `tests/test_s1_train_view.py`, view:573 `_out` keys each test's
  output directory by `tmp_path.name`. Under pyproject.toml:19 `tmp_path_retention_policy` ("failed"), a passing test's
  tmp_path is deleted and its number is reused, so two tests in one session can get the same `tmp_path.name`. My first
  `_root` did the same, and four of my parametrized tests collided (`FileExistsError` on `<root>/full`). My `_root`
  now makes a new directory on each call. The view test passes today (112 passed). That a future test of it that writes
  an --out would collide is inferred, not measured.

## 10. NOT done

- **NOT run here: the hf tokenizer and the fla backend.** `HFTokenizer` (read.py:312), `FlaBackend` (read.py:378),
  `tokens --tokenizer hf`, `read --backend fla`, and `smoke --backend fla` with its head check have never executed.
  The sandbox has no torch, transformers or fla, and the brief forbids a test to import them. They follow
  `rwkv7_g0.py` lines 135 to 149 (the load) and 87 to 114 (the forward with a cache, the deep copy). The coordinator's
  PC smoke runs them first.
- No run over the real view and export (they live on the PC).
- No commit, no push, no PR, no PC bridge, no `pc_suite.sh launch` (`set-id` only, which is local).
- Red-green: the tests were written after the code. Their red proof is the mutant table (23 of 23), not a red run of
  each test before the code existed.

## 11. Self-attack: the three most likely ways this change is wrong

1. **A misreading shared by the code and the oracle.** I wrote both from one reading of R-3 and R-5.
   - What reduces it: the oracle is a different implementation (a regex tokenizer, a fresh fold for every readout, no
     copy and no segment logic), checked against PREREG-441 §2's feature table as well as the brief. The fixture holds
     the edge cases: each wrapped hook's `hook_success` renders "" at its carrier's offset (a `state_end` shared with
     an empty block), two rows at one position, a shared candidate, a candidate over the cap, and rows inside and past
     the window.
   - Residual: a misreading common to both would still pass. A verifier should re-read R-3 and R-5 against the code:
     read.py:441 (`stream`) and read.py:535 (`read_file`). (partly verified; the residual is assumed)
2. **The PC adapters fail on first contact.**
   - The likely failure points: the attribute names `model.model` and `last_hidden_state` on the checkpoint's fla
     class; `tok.vocab_size` on the RWKV World tokenizer; and the smoke's EQUAL copy check if the bf16 kernels are not
     deterministic (the check would then fail, never pass falsely). `fla.__version__` is already read guarded.
   - Not ruled out here. `smoke --backend fla` and `tokens --tokenizer hf` on the PC are the check, before any
     feature run. (assumed)
3. **The tails manifest's keys (D-1).**
   - If task #472 expects the prereg block in the tails manifest (R-1's reading), its comparison fails.
   - Not ruled out: I followed R-7's "exactly the keys", and task #472's brief is outside my boundary. The coordinator
     should confirm which reading task #472 built. (inferred)

Also checked, with a test: a resumed run's byte identity rests on float32. The records are features-format float32,
and the final `features.write` rounds fresh doubles to float32 too, so the two are equal. This is verified for the fake
backend by the resumed-run test. For fla, the readouts are bf16 values, which float32 holds exactly (inferred).

## 12. Verdict (written 10:3xZ)

DONE: `scripts/s1_train/read.py` and `tests/test_s1_train_read.py`. The test count is `pytest-summary: 52 passed`
(twice, set 9b7b5a45ec51). The mutants read `EXPECTED=23 KILLED=23 SURVIVED=0 ERRORED=0 INVALID=0`. The siblings read
`112 passed`.

NOT run here: the hf tokenizer and the fla backend (§10). NOT verified live: no real-data run. Discrepancies: D-1 to
D-12, of which D-1 (R-1 against R-7) and D-2 (`candidate_of`) need the coordinator's eye. GATED-PENDING-VERIFY: the
coordinator commits.
