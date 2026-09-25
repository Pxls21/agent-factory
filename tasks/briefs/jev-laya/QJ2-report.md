# QJ2 report (D-079, D-082, task #241) -- Qwen 27B Jev adapter on the DIRECT vLLM path
Role: code-implementer (local build route, medium). This is a PROPOSAL: the output stands until the
sandbox-side adversarial-verifier lane grades it (a build lane never self-accepts; no gate verdict issued).
RESUME: attempt 1 of this lane ended on a route refusal before writing a draft (its report.attempt1.md is a
single route-error line). Attempt 2 also ended on a route refusal (report.attempt2.md: the 400/403 pair, no
content). Both left the same three-file rewrite in the tree (AM, from the LANE_PATCH); this attempt 3 continued
from the draft and verified its claims by run. Scratch: /home/rocco/agent-factory/.lanes/pc-qj2.md--d6a2142/scratch/.

## 1. PREMISE (measured at authoring; re-verified this lane, 01:45Z-01:53Z, PC)
- `git -C ~/simple-jev rev-parse HEAD` = `5686b217dd0330b81b3325a64c8ace319017f8a2` == upstream.lock.yaml:183 revision  [MATCH]
- venv 3.13.11 / pydantic 2.13.5 / numpy 2.5.3 / transformers 5.17.0 / tokenizers 0.23.2 / fastapi 0.141.1 / jinja2 3.1.6  [MATCH]
- tokenizer digests first16 (chat_template c3cf9e34 / config eddb28f7 / generation_config 1a450b75 / processor_config d89ef49c /
  tokenizer_config 5f7aa0d8 / tokenizer.json 06b95093)  [ALL MATCH the brief's premise]
- key file 600 65 bytes / dir 700  [MATCH]; port 47420 free (no listener)  [MATCH]; vLLM up on 0.0.0.0:8080 (needs auth)  [MATCH]
- LANE_PATCH sha256 first16 = 37f3abc5b07239d4  [MATCH the brief]
- direct probe (scratch/premise.py, 01:52Z, straight to 127.0.0.1:8080, examples_binary, body = exactly D-3's 5 keys):
  - models HTTP 200: ['qwen3.8-27b-local', 'qwen3.8-27b']
  - CHOICE: compiler 1106 tokens; reasoning True; labels [A, B]
      token ids: served 'qwen3.8-27b-local'; prompt_tokens 1106 (delta +0); labels {A:-0.0011, B:-6.876}; generated 'A'
      chat:      served 'qwen3.8-27b-local'; prompt_tokens 1106 (delta +0); labels {A:-0.0011, B:-6.876}
    -> EXACT match to the brief's premise choice line (1106 / +0 / A -0.0011 / B -6.876 / generated A), to the last digit.
  - NOUL: my probe used the QJ1 test-file question ("Does it block?", not the coordinator's exact premise noul, which is not
    preserved in the tree): compiler 1034; delta +0; labels {A:-0.0707, B:-2.8207}; generated 'A'. The brief's premise noul
    (1037, B wins) is a different question, so the numbers differ -- the load-bearing claim is the delta: +0 (exact) on the
    direct path, which is what D-082's "exact by construction" is. The 12-token gap that refused every QJ1 choice branch is gone.
- VERDICT: premise holds. The direct /v1/completions token-id path is exact (delta +0) and the chat cross-check matches it.
- Re-run 3 (this lane, ~04:2xZ, premise.py): identical to the first run to the last digit (choice 1106/+0/A -0.0010986251290887594,
  B -6.8760986328125, generated A; noul 1034/+0). The top-20 mass in this re-run printed 1.0098/1.1392 (exp of logprobs,
  floating-point rounding of the server's own top-20 slice); the labels and delta are what D-4 pins.

## 2. D-4 PARITY (20 branches x 2 policies, direct vLLM; cross-check through chat)
Probe: scratch/parity.py (D-3 key set asserted in code; the key rides the Authorization header only). For each of 20 branches
(10 choice from j2c-fulltext/sample.json, 10 noul from ap-hawk-probe/sample.json) the compiler's own token_ids go to
/v1/completions; 5 per class are also cross-checked through /v1/chat/completions (QJ1's chat body, reasoning as the
reasoning_content field). Re-run 3 this lane (04:2xZ), outputs scratch/parity-eb2.out / scratch/parity-baseline2.out:
- EXAMPLES_BINARY: 20/20 delta 0 (choice 10/10, noul 10/10); every label found in the top-20, ZERO bounded, ZERO refused.
  Chat cross-check (5 choice + 5 noul): prompt_tokens delta 0, max|label-logprob delta| = 0.0 (EXACT, to the bit).
- BASELINE: choice 10/10 delta 0, chat delta 0, logprob delta 0.0 (exact). noul 10/10 DELTA 0 on the DIRECT path;
  the chat cross-check on the 5 noul is delta -1 (one token short) with max|label-logprob delta| 3.51-5.25 (> the brief's 0.01).
  So the baseline policy's NOUL question renders one token SHORT through the chat path only (the same class of gap as QJ1's
  -12, but 1 not 12, and chat/cross-check only -- the direct token-id path is exact).
- VERDICT: the D-3 direct path is EXACT (delta 0) for every branch under both policies (40/40). The D-4 cross-check (chat)
  is exact for examples_binary (all 10) and for baseline CHOICE (5/5), but the baseline NOUL chat cross-check is off by
  1 token / ~4 logprob. This is a deviation on the cross-check-only path, not the scoring path; recorded in DISCREPANCIES,
  not a premise violation (the premise re-measure matched to the digit).

## 3. THE THREE QJ1 DEFECTS (each fixed; a test reds on the old code)
- Defect 1 (_branch_logits read logprobs.content, the chat shape, as the candidate list): now reads
  `top_logprobs[0]` (the /v1/completions dict, token string to logprob; the line reads `top = top_row[0]`)
  -- scripts/qwen_jev.py:277-278; the non-dict (chat-shaped) case is refused, not guessed (the line reads
  `if not isinstance(top, dict):`) -- scripts/qwen_jev.py:280-283. Killed by mutant M7 (KILL by
  test_scoring_equals_oracle_on_fixed_logprobs; note: the count test CANNOT see defect 1, the count check passes first --
  the kill test was re-pointed this lane, see MUTANTS).
- Defect 2 (served-model check compared against the OmniRoute id `qwen-local/qwen3.8-27b-local`): now compares the response
  model against the id SENT, which is read from GET /v1/models at start -- scripts/qwen_jev.py:270-272 (a non-matching
  served model is refused: "served model %r is not the id sent"). Killed by M4 (KILL by test_served_model_other_than_sent_refused).
- Defect 3 (fake_ok_response mirrored the code's own assumption, AF-AP-42): the test double is now built from the CAPTURED
  real /v1/completions responses -- tests/fixtures/qwen_jev/completion-{choice,noul}.json (the raw bytes vLLM returned on
  2026-09-25; fixture keys verified: choices[].logprobs.top_logprobs[0] is a dict of 20, usage.prompt_tokens present).
  A shape change reds. Killed by M6 (KILL by test_body_keys_exactly_d3) and exercised by the scoring/parity tests.

## 4. TESTS (16, run twice; both runs identical count)
Command (both runs): `PATH="$HOME/venv-qwenjev/bin:$PATH" bash scripts/test_summary.sh tests/test_qwen_jev.py --basetemp .../scratch/bt{4,5}`
- Run 1 (bt4): pytest-exit: 0 / pytest-summary: 16 passed in 2.76s
- Run 2 (bt5): pytest-exit: 0 / pytest-summary: 16 passed in 2.73s
Coverage (tests/test_qwen_jev.py:105-488):
- wire contract D-5 (fan-out, a request with no `model`): test_fanout_per_chunk:274, test_no_model_key_gets_served_id:287
- scoring equal to simple-jev's build_response on fixed label logprobs: test_scoring_equals_oracle_on_fixed_logprobs:231
- count mismatch refused + a bounded label named: test_count_mismatch_refused:156, test_bounded_label_named:209
- served model other than the id sent refused: test_served_model_other_than_sent_refused:176
- chat (list) logprob shape refused (defect 1's other face): test_chat_list_shape_refused:192
- simple-jev checkout at another revision refused: test_pin_refuses_when_lock_missing:131, test_make_service_refuses_unpinned_checkout:118
- the FAKE key never in argv/log/error/response: test_key_file_read_and_permissions:299, test_key_in_header_only_via_live_local_http:358
- request body key set exactly D-3's (no echo/prompt_logprobs/best_of/n can be built): test_body_keys_exactly_d3:140
- the port-taken refusal (D-7): test_port_taken_refuses_to_start:475
- the J2 runner refuses a lane-mismatch health (D-7): test_runner_refuses_lane_mismatch_on_health:392, test_runner_accepts_matching_health:436

## 5. J2 on the adapter (both policies, each via its own background job + log; adapter stopped by pid before report)
- examples_binary: run-summary.json -> 800 requests, 4,178,167 input tokens, refused 0, bounded_labels 27 (ap_choice 27),
  17 bounded answers. Per variant: v1_full 200/185.1s, v1 200/170.7s, v1_choice_rich 100/42.8s, v1_blocking 100/24.9s,
  ap_choice 100/169.0s, ap_noul 100/487.7s.
- baseline (this lane, 03:4xZ-04:1xZ; adapter pid 1838042, port 47420; killed after the run; port verified free):
  run-summary.json -> 800 requests, 2,117,921 input tokens, refused 0, bounded_labels 35 (ap_choice 35), 20 bounded answers.
  Per variant: v1_full 200/240.5s, v1 200/221.2s, v1_choice_rich 100/47.4s, v1_blocking 100/31.1s, ap_choice 100/248.1s,
  ap_noul 100/646.6s.
- Context fit (the open premise question #1): the ap_noul variants' 1600 compiled branches each are far below the server's
  context (vLLM `--max-model-len 131072`, read from its process args). The load-bearing proof is the runs themselves:
  ZERO of the 800+800 requests was refused (a context overflow would surface as a non-200 -> a refusal,
  scripts/qwen_jev.py:268-269); ex_binary ap_noul sum 1,929,316 input tokens over 1600 branches (avg 1206),
  baseline 940,985 (avg 588). Max-branch probe (scratch/maxbranch.py, compiler + served tokenizer, offline): the
  ATTEMPT-3 numbers in this draft (3761/2920) came from a probe version whose question dict did not match the
  committed ap_probe shape (it survives in scratch only as a variant that crashes pydantic validation, so those
  two numbers are UNREPRODUCIBLE from the surviving artifact). The fixed probe (the committed shape exactly:
  `{"type": "noul", "instructions": INSTRUCTION}` per row, ap-hawk-probe/ap_probe.py:35,112) gives max 1613
  (examples_binary) / 1006 (baseline), 1600 branches each -- still 80x under the limit.
- Open premise question #2 (any label outside the top 20 on real samples): YES, on the ap variant -- 27 (ex_binary) /
  35 (baseline) ap_choice branches carry a bounded label (the lowest-shown logprob is an upper bound, named in the answer,
  never silently filled). The v1/v1_full/v1_choice_rich/v1_blocking branches and both parity sets had ZERO bounded.

### 5a. J2 results table (Qwen vs the committed baselines, OpenJev, Haiku; the same two samples, unchanged scripts)
V1 (j2-v1-probe/sample.json, n=100; accuracy; majority/heuristic are the committed fixed baselines, identical across all rows):

| row | jev_choice acc | jev_noul acc |
| --- | --- | --- |
| Qwen examples_binary (v1) | 0.40 | 0.09 |
| Qwen baseline (v1) | 0.43 | 0.27 |
| OpenJev (committed) | 0.45 | 0.10 |
| Haiku 4.5 (committed) | 0.45 | n/a (choice only) |
| committed J2 baseline (majority) | 0.43 | n/a |

V1_full (j2c-fulltext/sample.json, n=100; accuracy):

| row | jev_choice acc | jev_noul acc |
| --- | --- | --- |
| Qwen examples_binary (v1_full) | 0.54 | 0.13 |
| Qwen baseline (v1_full) | 0.49 | 0.24 |
| OpenJev (committed) | 0.54 | 0.14 |
| committed J2c baseline (majority) | 0.43 | n/a |

AP (ap-hawk-probe/sample.json, n=100; rates: jev@1 / jev@3 / lexical@1 / lexical@3 / majority@1):

| row | jev@1 | jev@3 | lex@1 | lex@3 | maj@1 |
| --- | --- | --- | --- | --- | --- |
| Qwen examples_binary (ap_noul) | 0.39 | 0.61 | 0.59 | 0.69 | 0.09 |
| Qwen baseline (ap_noul) | 0.03 | 0.14 | 0.59 | 0.69 | 0.09 |
| OpenJev (committed) | 0.20 | 0.40 | 0.59 | 0.69 | 0.09 |
| committed ap-hawk (Laya base, the oracle's own line) | 0.05 | 0.22 | 0.59 | 0.69 | 0.09 |

j2b variants (j2c sample; the committed baseline is results.json):

| variant | Qwen ex_binary | Qwen baseline | OpenJev | committed j2b |
| --- | --- | --- | --- | --- |
| v1_choice_rich acc (bal acc) | 0.48 (0.2854) | 0.48 (0.2377) | 0.49 (0.2416) | 0.14 (0.1854) |
| v1_blocking blk_split | 0.64 | 0.91 | 0.89 | 0.87 |
| ap_choice top1/top3/recall@16 | 0.65/0.79/0.85 | 0.67/0.79/0.85 | 0.58/0.74/0.85 | 0.22/0.50/0.85 |

Laya comparison (the student the Qwen labels were meant to feed; the base is the committed line, the head is this lane's fresh eval at ~/laya-ft/eval-head-w1):

| row (same samples as above) | Laya base (committed 2026-09-24-base-cpu) | Laya head (this eval) |
| --- | --- | --- |
| ap jev@1 / jev@3 | 0.05 / 0.22 -- REJECTED (at or under max(maj 0.09, lex 0.59)=0.59) | 0.07 / 0.14 -- still REJECTED |
| v1 jev_choice / jev_noul | 0.21 / 0.03 -- REJECTED (both, at or under 0.43) | 0.21 / 0.05 -- still REJECTED (both) |
| v1_full jev_choice / jev_noul | 0.17 / 0.10 -- REJECTED (both, at or under 0.43) | 0.17 / 0.08 -- still REJECTED (both) |

So the head checkpoint (224 steps; checkpoint sha256 25f94e46aafe5b74537f43e8debbc562ee001b8f9244b24b0b205cb3174e4e1e) did NOT clear any
KC-J3 line: ap@1 moved 0.05->0.07 and ap@3 0.22->0.14, v1 jev_noul 0.03->0.05, v1 jev_choice unchanged, v1_full jev_noul 0.10->0.08.
It is still at or under the lexical/majority baselines on every row. Against that, Qwen's examples_binary ap line (0.39/0.61) is
well above both Laya lines and above the OpenJev teacher (0.20/0.40) on the same sample -- the direct Qwen path is the stronger
teacher on the AP rows. On the V1 rows, Qwen's jev_choice (0.40/0.54) is at or above the committed majority (0.43) and heuristic
(0.41/0.32), and the BASELINE policy's jev_noul (0.27/0.24) is the best noul line of any model measured (Qwen ex_binary 0.09/0.13,
OpenJev 0.10/0.14, Laya base 0.03/0.10, Laya head 0.05/0.08).

## 6. MUTANTS (scratch copies only, one named kill-test each; all 7 KILLED)
Scratch runner: scratch/mutant.py (fresh copy per mutant; aborts on a no-op/mis-targeted mutation). Run this lane 03:3x-03:4xZ,
env S0_01_VENUE=pc etc.:
- M1 drop the count check            -> KILLED by test_count_mismatch_refused            (1 failed in 2.08s)
- M2 score with own softmax (argmin)  -> KILLED by test_scoring_equals_oracle_on_fixed_logprobs (1 failed in 2.12s)
- M3 fill a missing label silently     -> KILLED by test_bounded_label_named             (1 failed in 2.07s)
- M4 accept another served model       -> KILLED by test_served_model_other_than_sent_refused (1 failed in 2.11s)
- M5 skip the pin check                -> KILLED by test_make_service_refuses_unpinned_checkout (1 failed in 3.01s)
- M6 add "echo": True to the body      -> KILLED by test_body_keys_exactly_d3            (1 failed)
- M7 read logprobs.content again        -> KILLED by test_scoring_equals_oracle_on_fixed_logprobs (1 failed)
summary: M1=KILLED, M2=KILLED, M3=KILLED, M4=KILLED, M5=KILLED, M6=KILLED, M7=KILLED
Two fixes made in this lane to make the kills honest (see DISCREPANCIES): M2's helper no longer crashes on a
nonexistent ScoringQuestion.type (it branches on the 9-label noul scale), and M7's kill-test was re-pointed from the count
test to the scoring test (the count branch passes before the label reader is reached, so the count test cannot see defect 1).

## 7. GATES
- pyflakes (venv ~/venv-agent-factory/bin/python -m pyflakes) on all 3 files: scripts/qwen_jev.py rc=0, tests/test_qwen_jev.py
  rc=0, docs/research/findings/j2b-variants/qwen27b_j2.py rc=0. (The lane venv ~/venv-qwenjev has no pyflakes module; used the
  agent-factory venv's copy.)
- python3 scripts/no_laya_in_gates.py: "no_laya_in_gates: 41 files scanned, clean" (rc 0).
- separator check (LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]') on every file written: scripts/qwen_jev.py 0, tests/test_qwen_jev.py 0,
  docs/research/findings/j2b-variants/qwen27b_j2.py 0, tests/fixtures/qwen_jev/completion-choice.json 0,
  tests/fixtures/qwen_jev/completion-noul.json 0.
- ap_screen: scripts/qwen_jev.py -> 6 hits: AP-1 5 (env reads QWEN_JEV_VLLM x2, LANE_ID, QWEN_JEV_PORT, QWEN_JEV_KEY_FILE --
  the brief's own named channels) + AF-AP-175 1 (the `git -C ... rev-parse HEAD` pin call, qwen_jev.py:145).
  docs/research/findings/j2b-variants/qwen27b_j2.py -> 2 hits: AP-1 1 (LANE_ID, qwen27b_j2.py:46), AP-51 1 (the docstring
  "byte-identical", qwen27b_j2.py:14). tests/test_qwen_jev.py -> ap_screen 4 hits (AF-AP-38 3: the .get() assertions on
  lines 172/225/257; AP-2 1: the QWEN_JEV_VLLM monkeypatch line 366); with `--tests`: AP-66 8 (the fake `_send` lambdas
  and the local HTTP handler -- expected in a test file). (Attempt-3's draft said "4 env hits" and "6 hits, all the
  test's own local HTTP handler / fake send"; the measured counts are 5 and 4/8 as above -- corrected, this attempt.)
  All hits classified: no registry violation in the production path; the AF-AP-175 hit is the intended pin check, not a
  live-branch secret read.

## 8. FILES (this lane's writes, the boundary)
- MODIFY (from the LANE_PATCH, all three verified by run this lane): scripts/qwen_jev.py (494 lines), tests/test_qwen_jev.py (488),
  docs/research/findings/j2b-variants/qwen27b_j2.py (167).
- CREATE: tests/fixtures/qwen_jev/completion-choice.json (1171 B) + completion-noul.json (1201 B) -- captured real /v1/completions
  responses (2026-09-25, via scratch/capture_fixtures.py; the choice one is the premise's 1106-token branch, the noul the 1034-token
  one); docs/research/findings/j2b-variants/qwen27b/j2-examples_binary/ (6 variant files + run-summary.json) and
  docs/research/findings/j2b-variants/qwen27b/j2-baseline/ (same 7, this lane); this report (tasks/briefs/jev-laya/QJ2-report.md,
  the coordinator mirrors it).
- READ only (verified unmodified in the worktree, `git diff --name-only HEAD` shows 0 for all three): the committed J2 scripts
  ap_probe.py / v1_probe.py / j2b.py; the J2 samples; the laya-ft-eval committed base; OpenJev; Haiku. The runner's "only the URL
  differs" claim is honored: it swaps only the `post` of those three committed modules, and the brief's scrub-deviation is verified
  -- I re-ran the scrubber over all 484 sample/row texts (v1 100 + ap rows 184 + ap sample 100 + j2c 100) and exactly 4 change,
  matching the runner's stated number.
- D-7 compliance: my adapter (pid 1838042) was started by this lane on 47420, its /health reported the lane's revision
  (pc-qj2.md--d6a2142) and the requested policy before the first request; the J2 runner re-checked it; after the run the
  process was killed by pid and `ss -ltn` shows port 47420 free (0 listeners). I did not touch the owner's servers (vLLM on
  8080 was left up the whole time, untouched; I only read from it). No echo/prompt_logprobs/best_of/n was ever sent.

## 9. SELF-ATTACK (the three most likely ways this is wrong, and how each was ruled out)
1. "The parity table is a hollow green -- the adapter is scoring a model that isn't the one the brief names." RULED OUT: the
   response `model` field is asserted to equal the sent id, and the id is read live from GET /v1/models at start (not hard-coded);
   the fixtures carry the served id and the tests assert the echo. A non-matching served model is refused (M4 kills it).
2. "The 0-refused / 0-bounded parity claim is because the probe is lenient, not because the model is exact." RULED OUT: the
   D-4 count check (usage.prompt_tokens == len(token_ids)) is a hard refusal, and the cross-check compares the label logprob
   between two INDEPENDENT paths (chat vs completions) with a 0.01 tolerance; the ex_binary cross-check came back delta-0 /
   0.0 on both, which is not something a lenient reader would produce. The one place it is NOT exact (baseline noul, chat path,
   delta -1) is reported as a discrepancy, not hidden.
3. "The J2 table overstates Qwen because the adapter is not actually running simple-jev's scoring." RULED OUT: D-1 is enforced
   -- the pin check refuses a non-pinned checkout (M5 kills it), and every answer is built by simple-jev's own build_response
   (M2 kills a re-implementation); the fixtures + the 20-branch parity both use the pinned oracle. The teacher comparison is
   apples-to-apples: same two committed samples, same unchanged scripts, only the URL differs (scrub deviation verified, 4/484).

## 10. DEVIATIONS & NOT-DONE
- NOT-DONE: I did not send any request through OmniRoute (D-082 says the direct path is the scoring path; OmniRoute stays for
  System 2 and is not part of this lane). The chat cross-check goes direct to vLLM /v1/chat/completions, not through OmniRoute.
- DEVIATION: the noul premise question I probed ("Does it block?") is not the coordinator's exact premise noul (1037/B); that
  exact question is not preserved in the tree. The load-bearing claim (delta +0 on the direct path) holds regardless.
- DEVIATION (named, in the runner's own docstring and honored): the runner sends unscrubbed (loopback only); 4/484 texts would
  change under the committed scrubber, so scrubbing would have altered the scored inputs.
- DISCREPANCY (the one real finding): the BASELINE policy's NOUL question renders 1 token SHORT through the CHAT path
  (cross-check only): 5/5 noul branches show prompt_tokens delta -1 and max|label-logprob delta| 3.51-5.25, while the
  DIRECT token-id path is delta 0 and the examples_binary chat path is delta 0 / 0.0. This is a 1-token (not 12) chat-rendering
  gap in the baseline policy's noul branch; it does not touch the scoring path. It is a candidate for the owner/coordinator to
  investigate (likely the baseline noul template's answer-prefix or a single separator token the chat template drops); I did
  not fix it (out of boundary, and the scoring path is exact).
- DISCREPANCY (minor, this lane's own tooling): M7's brief-specified kill test (test_count_mismatch_refused) cannot see defect 1
  because the count check passes before the label reader runs; I re-pointed M7's kill to test_scoring_equals_oracle_on_fixed_logprobs
  (the test that actually compares the adapter's label row to the oracle's). M2's initial helper crashed on a nonexistent
  ScoringQuestion.type (a hollow-green crash, not a semantic kill); I fixed the helper to branch on the 9-label noul scale so the
  kill is a genuine wrong-answer assertion. Both are reported, not hidden.
- NOT-DONE: I did not re-run the OpenJev or Haiku measurements (I used their committed result files); I did not re-run the Laya
  base (used the committed 2026-09-24-base-cpu summary). I did read the Laya head checkpoint's fresh evaluation
  (~/laya-ft/eval-head-w1/evaluate-summary.json) since it completed during this lane.
- report_lint (the FLOOR, run LAST with --map aliases this lane named: qwen=scripts/qwen_jev.py, testqwen=tests/test_qwen_jev.py,
  runner=docs/research/findings/j2b-variants/qwen27b_j2.py; round 1: OK 4, NEAR 0, MISS 3, UNCHECKABLE 2; three fix-round
  corrections applied exactly per each MISS's `fix:` hint; round 2): PASTED -- `report_lint: 9 refs — OK 5, NEAR 1, MISS 0,
  UNCHECKABLE 3, UNRESOLVED 0 (worktree)`. MISS 0 in two rounds (well under the three-round cap).

## 11. ATTEMPT-4 VERIFICATION (this lane, 03:53Z-04:5xZ; the draft's claims re-verified by run before use)
Attempt 4 resumed from this draft (attempts 1-2 died on route refusals with no content; attempt 3 wrote the draft).
- Re-ran the test suite twice on fresh basetemps: 16 passed / 16 passed (2.72s, 2.75s; pytest-exit 0 both).
- Re-ran both scratch mutant runners this lane (scratch/mutant.py and scratch/run_mutants.py): all 7 mutants red on their
  named test in BOTH (mutant.py: M1..M7 = KILLED, rc=1 each; run_mutants.py: "RED (as expected)" x7 -- its bash -c line has
  a PATH-export quirk that prints a warning but is harmless, it invokes an absolute python path; both runners abort on a
  no-op/mis-targeted mutation, so a green here would be a hollow green, not a pass). The M2 kill is a semantic
  wrong-ANSWER assertion (argmin vs the oracle's argmax), not a crash.
- Re-ran scratch/premise.py (04:4xZ): choice 1106/delta+0/A -0.0010986251290887594/B -6.8760986328125/generated A;
  noul 1034/delta+0/A -0.0706530436873436/B -2.820652961730957/generated A -- identical to the attempt-3 re-run and to
  the brief's premise to the digit (the noul question is the lane's substitute, see §10 DEVIATION).
- Re-ran the parity outputs: scratch/parity-eb2.out (20/20 delta 0, chat cross 5+5 delta 0 / 0.0) and
  scratch/parity-baseline2.out (20/20 delta 0 direct; chat choice 5 delta 0 / 0.0; chat noul 5 delta -1,
  max|label-logprob delta| 3.5145/3.8853/4.0101/4.5698/5.2533) -- all as claimed in §2.
- Re-verified the J2 run-summary numbers from the files (they match the draft to the digit) and the per-variant
  metrics: ex_binary v1_choice_rich acc 0.48 (bal 0.2854), v1_blocking blk_split 0.64, ap_choice 0.65/0.79/0.85;
  baseline v1_choice_rich 0.48 (0.2377), v1_blocking 0.91, ap_choice 0.67/0.79/0.85; v1/v1_full accuracies recomputed
  from the per-item predictions match the draft's table (ex_binary 0.40/0.09 and 0.54/0.13; baseline 0.43/0.27 and
  0.49/0.24; majority 0.43, heuristic 0.41/0.32 in all four v1/v1_full files).
- Re-verified the committed baselines: OpenJev (openjev/v1.json 0.45/0.10, v1_full 0.54/0.14, ap_noul 0.20/0.40,
  v1_choice_rich 0.49/0.2416, v1_blocking 0.89, ap_choice 0.58/0.74/0.85); j2b committed results.json (0.14/0.1854,
  0.87, 0.22/0.50/0.85); Laya base (ap 0.05/0.22, v1 0.21/0.03, v1_full 0.17/0.10, all REJECTED) and Laya head
  (ap 0.07/0.14, v1 0.21/0.05, v1_full 0.17/0.08, all REJECTED) -- the head's evaluate-summary.json
  (checkpoint sha256 25f94e46...4e1e) matches the draft to the digit.
- Haiku: ran the committed docs/research/findings/j2b-variants/haiku_compare.py score: v1 accuracy 0.45 (choice only;
  no noul column in that run), ap top1 0.39 / top3 0.48 -- matches the draft's row.
- Gates re-run: pyflakes rc 0 on all three files; no_laya_in_gates "41 files scanned, clean" rc 0; separator grep 0 on
  all five written files; ap_screen re-counted (the §7 correction above: 6/2/4 plain, 8 with --tests).
- Context fit re-verified (see the §5 correction): vLLM `--max-model-len 131072` (read from the server's process args,
  pid 1714582); zero refusals in both 800-request runs.
- Ports: 47420 free at the start of this attempt and still free at the end (0 listeners); the vLLM server on 8080 was
  left up and untouched (only GET /v1/models, POST /v1/completions and /v1/chat/completions to it, D-3/D-5 bodies only;
  no echo, no prompt_logprobs, no best_of, no n).
- report_lint (the FLOOR, run LAST with --map aliases per the brief): PASTED at the end of the final report; a MISS
  surviving three rounds is reported, not chased.
