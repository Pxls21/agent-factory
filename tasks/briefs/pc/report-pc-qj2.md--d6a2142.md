Lane QJ2 (attempt 4) finished. The report file is at `/home/rocco/agent-factory/.lanes/pc-qj2.md--d6a2142/tree/tasks/briefs/jev-laya/QJ2-report.md` (byte-identical to the draft; both carry every section below). This is a PROPOSAL — it stands until the sandbox-side adversarial-verifier lane grades it; no gate verdict issued.

# QJ2 report (D-079, D-082, task #241) — Qwen 27B Jev adapter on the DIRECT vLLM path

Role: code-implementer (local build route, medium). RESUME: attempts 1-2 ended on route refusals with no content; attempt 3 wrote the draft (three-file rewrite from the LANE_PATCH). This attempt 4 continued from the draft and re-verified its load-bearing claims by run before relying on them.

## 1. PREMISE (re-measured this lane, 04:4xZ, PC)
- `git -C ~/simple-jev rev-parse HEAD` = `5686b217dd0330b81b3325a64c8ace319017f8a2` == upstream.lock.yaml:183 [MATCH]
- venv 3.13.11 / pydantic 2.13.5 / numpy 2.5.3 / transformers 5.17.0 / tokenizers 0.23.2 / fastapi 0.141.1 / jinja2 3.1.6 [MATCH]
- key file 600/65 B under a 700 dir; port 47420 free at start and end; vLLM up on 0.0.0.0:8080 (needs auth); LANE_PATCH sha256 first16 = 37f3abc5b07239d4 [ALL MATCH]
- direct probe (scratch/premise.py, exactly D-3's 5-key body, straight to 127.0.0.1:8080): models 200 `['qwen3.8-27b-local','qwen3.8-27b']`; choice: compiler 1106, delta +0, labels A -0.0010986251290887594 / B -6.8760986328125, generated A; noul: 1034, delta +0, A -0.0706530436873436 / B -2.820652961730957, generated A. Identical to the brief's premise to the digit (the noul question is the lane's substitute — see §10).
- VERDICT: premise holds. The direct /v1/completions token-id path is exact by construction (delta +0); the chat cross-check matches it bit-for-bit.

## 2. D-4 PARITY (20 branches x 2 policies, direct vLLM; 5 per class cross-checked via chat)
- EXAMPLES_BINARY: 20/20 delta 0; every label in the top-20; ZERO bounded, ZERO refused. Chat cross-check (5 choice + 5 noul): prompt delta 0, max|label-logprob delta| = 0.0 (exact).
- BASELINE: 20/20 delta 0 on the DIRECT path; chat choice 5/5 delta 0 / 0.0; **chat noul 5/5 delta -1** (one token short, chat path only) with max|label-logprob delta| 3.5145/3.8853/4.0101/4.5698/5.2533 (> 0.01).
- VERDICT: the D-3 scoring path is EXACT (40/40 delta 0, both policies). The one non-exact result is on the cross-check-only chat path for baseline noul (a 1-token, not 12-token, chat-rendering gap) — reported as a discrepancy, not hidden (§10).

## 3. THE THREE QJ1 DEFECTS (each fixed; a mutant reds on the old code)
- Defect 1 (`_branch_logits` read `logprobs.content`, the chat shape, as the candidate list): now reads `top_logprobs[0]` (the /v1/completions dict, token string to logprob; the line reads `top = top_row[0]`) — scripts/qwen_jev.py:277-278; the non-dict (chat-shaped) case is refused, not guessed (the line reads `if not isinstance(top, dict):`) — scripts/qwen_jev.py:280-283. Killed by M7.
- Defect 2 (served-model check compared against the OmniRoute id): now compares the response `model` against the id SENT, read live from GET /v1/models at start — scripts/qwen_jev.py:270-271 ("served model %r is not the id sent %r"). Killed by M4.
- Defect 3 (fake_ok_response mirrored the code's own assumption, AF-AP-42): the test double is now built from the CAPTURED real responses — tests/fixtures/qwen_jev/completion-{choice,noul}.json (1171 B / 1201 B; verified: `choices[0].logprobs.top_logprobs[0]` is a dict of 20, `usage.prompt_tokens` 1106/1034, served id `qwen3.8-27b-local`; the choice one is the premise's 1106-token branch). A shape change reds. Killed by M6 (body-key test) and exercised by the scoring/parity tests.

## 4. TESTS (16, run twice; both runs identical counts)
Command (both runs): `PATH="$HOME/venv-qwenjev/bin:$PATH" bash scripts/test_summary.sh tests/test_qwen_jev.py --basetemp <scratch>/bt{6c,7c}` (parents pre-created)
- Run 1: `pytest-exit: 0` / `pytest-summary: 16 passed in 2.72s`
- Run 2: `pytest-exit: 0` / `pytest-summary: 16 passed in 2.75s`
Coverage (tests/test_qwen_jev.py:105-488):
- wire contract D-5 (per-chunk fan-out, a request with no `model`): test_fanout_per_chunk:274, test_no_model_key_gets_served_id:287
- scoring equal to simple-jev's `build_response` on fixed label logprobs: test_scoring_equals_oracle_on_fixed_logprobs:231
- count mismatch refused + bounded label named: test_count_mismatch_refused:156, test_bounded_label_named:209
- served model other than the id sent refused: test_served_model_other_than_sent_refused:176
- chat (list) logprob shape refused (defect 1's other face): test_chat_list_shape_refused:192
- simple-jev at another revision refused: test_make_service_refuses_unpinned_checkout:118, test_pin_refuses_when_lock_missing:131
- the FAKE key never in argv/log/error/response: test_key_file_read_and_permissions:299, test_key_in_header_only_via_live_local_http:358
- request body key set exactly D-3's (no `echo`/`prompt_logprobs`/`best_of`/`n` can be built): test_body_keys_exactly_d3:140
- the port-taken refusal (D-7): test_port_taken_refuses_to_start:475
- the J2 runner's health gate (D-7): test_runner_refuses_lane_mismatch_on_health:392, test_runner_accepts_matching_health:436

## 5. J2 on the adapter (both policies; each via its own background job + log; adapter stopped by pid before reporting)
- examples_binary (run-summary mtime 03:27Z): 800 requests, 4,178,167 input tokens, refused 0, bounded_labels 27 (ap_choice), 17 bounded answers. Per variant: v1_full 200/185.1s, v1 200/170.7s, v1_choice_rich 100/42.8s, v1_blocking 100/24.9s, ap_choice 100/169.0s, ap_noul 100/487.7s.
- baseline (run-summary mtime 04:24Z; adapter pid 1838042, port 47420, killed after the run): 800 requests, 2,117,921 input tokens, refused 0, bounded_labels 35 (ap_choice), 20 bounded answers. Per variant: v1_full 200/240.5s, v1 200/221.2s, v1_choice_rich 100/47.4s, v1_blocking 100/31.1s, ap_choice 100/248.1s, ap_noul 100/646.6s.
- Context fit (open premise question #1): the server runs `--max-model-len 131072` (read from its process args, pid 1714582). The load-bearing proof is the runs themselves: ZERO of the 800+800 requests refused (a context overflow would surface as a non-200 → refusal, scripts/qwen_jev.py:268-269); ex_binary ap_noul 1,929,316 input tokens over 1600 branches (avg 1206), baseline 940,985 (avg 588). Max-branch probe (scratch/maxbranch.py, compiler + served tokenizer, offline): the ATTEMPT-3 numbers in the earlier draft (3761/2920) came from a probe version whose question dict did not match the committed ap_probe shape (it survives in scratch only as a variant that crashes pydantic validation, so those two numbers are UNREPRODUCIBLE from the surviving artifact — see DISCREPANCIES). The fixed probe (the committed shape exactly: `{"type": "noul", "instructions": INSTRUCTION}` per row, ap-hawk-probe/ap_probe.py:35,112) gives max 1613 (examples_binary) / 1006 (baseline), 1600 branches each — ~80x under the limit.
- Open premise question #2 (any label outside the top 20 on real samples): YES, on the ap variant — 27 (ex_binary) / 35 (baseline) ap_choice branches carry a bounded label (the lowest-shown logprob is an upper bound, named in the answer's `bounded_labels`, never silently filled). v1/v1_full/v1_choice_rich/v1_blocking branches and both 20-branch parity sets had ZERO bounded.

### 5a. J2 results (Qwen vs the committed baselines, OpenJev, Haiku, Laya; same two samples, committed scripts unchanged — only the URL differs, scrub-deviation verified 4/484, re-run this lane)
V1 (j2-v1-probe/sample.json, n=100):

| row | jev_choice acc | jev_noul acc |
| --- | --- | --- |
| Qwen examples_binary | 0.40 | 0.09 |
| Qwen baseline | 0.43 | 0.27 |
| OpenJev (committed) | 0.45 | 0.10 |
| Haiku 4.5 (committed; haiku_compare.py re-run this lane) | 0.45 | n/a (choice only) |
| committed majority | 0.43 | n/a |

V1_full (j2c-fulltext/sample.json, n=100):

| row | jev_choice acc | jev_noul acc |
| --- | --- | --- |
| Qwen examples_binary | 0.54 | 0.13 |
| Qwen baseline | 0.49 | 0.24 |
| OpenJev (committed) | 0.54 | 0.14 |
| committed majority | 0.43 | n/a |

AP (ap-hawk-probe/sample.json, n=100; jev@1 / jev@3 / lexical@1 / lexical@3 / majority@1):

| row | jev@1 | jev@3 | lex@1 | lex@3 | maj@1 |
| --- | --- | --- | --- | --- | --- |
| Qwen examples_binary (ap_noul) | 0.39 | 0.61 | 0.59 | 0.69 | 0.09 |
| Qwen baseline (ap_noul) | 0.03 | 0.14 | 0.59 | 0.69 | 0.09 |
| OpenJev (committed) | 0.20 | 0.40 | 0.59 | 0.69 | 0.09 |
| Laya base (committed 2026-09-24-base-cpu) | 0.05 | 0.22 | 0.59 | 0.69 | 0.09 |

j2b variants (j2c sample; committed baseline = results.json):

| variant | Qwen ex_binary | Qwen baseline | OpenJev | committed j2b |
| --- | --- | --- | --- | --- |
| v1_choice_rich acc (bal acc) | 0.48 (0.2854) | 0.48 (0.2377) | 0.49 (0.2416) | 0.14 (0.1854) |
| v1_blocking blk_split | 0.64 | 0.91 | 0.89 | 0.87 |
| ap_choice top1/top3/recall@16 | 0.65/0.79/0.85 | 0.67/0.79/0.85 | 0.58/0.74/0.85 | 0.22/0.50/0.85 |

Laya comparison (the student the Qwen labels were meant to feed; base = committed line, head = the fresh CPU eval at ~/laya-ft/eval-head-w1, finished during this lane):

| row (same samples) | Laya base (committed) | Laya head (fresh) |
| --- | --- | --- |
| ap jev@1 / jev@3 | 0.05 / 0.22 — REJECTED | 0.07 / 0.14 — still REJECTED |
| v1 jev_choice / jev_noul | 0.21 / 0.03 — REJECTED (both, ≤ 0.43) | 0.21 / 0.05 — still REJECTED (both) |
| v1_full jev_choice / jev_noul | 0.17 / 0.10 — REJECTED (both, ≤ 0.43) | 0.17 / 0.08 — still REJECTED (both) |

Head checkpoint (224 steps; sha256 `25f94e46aafe5b74537f43e8debbc562ee001b8f9244b24b0b205cb3174e4e1e`) cleared NO KC-J3 line (ap@1 0.05→0.07, ap@3 0.22→0.14, v1 jev_noul 0.03→0.05, v1_full jev_noul 0.10→0.08; all still at or under the lexical/majority baselines). Against that, Qwen's examples_binary ap line (0.39/0.61) is well above both Laya lines and above the OpenJev teacher (0.20/0.40) on the same sample — the direct Qwen path is the stronger teacher on the AP rows. On the V1 rows, Qwen's jev_choice (0.40/0.54) is at or above the committed majority (0.43); the BASELINE policy's jev_noul (0.27/0.24) is the best noul line of any model measured (Qwen ex_binary 0.09/0.13, OpenJev 0.10/0.14, Laya 0.03/0.10 and 0.05/0.08).

## 6. MUTANTS (scratch copies only; re-run BOTH runners this lane; all 7 KILLED)
- scratch/mutant.py (aborts on a no-op/mis-targeted mutation): M1..M7 = KILLED, rc=1 each.
- scratch/run_mutants.py: "RED (as expected)" x7 (its bash -c line prints a PATH-export warning; it invokes an absolute python path, so the warning is harmless — verified, not assumed).
- M1 drop the count check → test_count_mismatch_refused
- M2 score with own scorer (deliberate argmin, a semantic wrong-ANSWER kill, not a crash) → test_scoring_equals_oracle_on_fixed_logprobs
- M3 fill a missing label silently → test_bounded_label_named
- M4 accept another served model → test_served_model_other_than_sent_refused
- M5 skip the pin check → test_make_service_refuses_unpinned_checkout
- M6 add `"echo": true` to the body → test_body_keys_exactly_d3
- M7 read `logprobs.content` again (defect 1) → test_scoring_equals_oracle_on_fixed_logprobs (the count branch passes first, so the count test cannot see defect 1 — re-pointed by attempt 3, verified this lane)

## 7. GATES (all re-run this lane)
- pyflakes (~/venv-agent-factory/bin/python -m pyflakes) on all 3 files: rc=0 (the lane venv has no pyflakes module; the agent-factory venv's copy used).
- `python3 scripts/no_laya_in_gates.py`: "no_laya_in_gates: 41 files scanned, clean" (rc 0).
- separator check (LC_ALL=C grep -c) on all five written files: 0 each (3 modified + 2 fixtures + the report).
- ap_screen: scripts/qwen_jev.py → 6 hits: AP-1 5 (env reads QWEN_JEV_VLLM x2, LANE_ID, QWEN_JEV_PORT, QWEN_JEV_KEY_FILE — the brief's own named channels) + AF-AP-175 1 (the `git -C ... rev-parse HEAD` pin call, qwen_jev.py:145). docs/research/findings/j2b-variants/qwen27b_j2.py → 2 hits: AP-1 1 (LANE_ID, qwen27b_j2.py:46), AP-51 1 (docstring "byte-identical", qwen27b_j2.py:14). tests/test_qwen_jev.py → ap_screen 4 hits (AF-AP-38 3: the .get() assertions at 172/225/257; AP-2 1: the QWEN_JEV_VLLM monkeypatch at 366); with `--tests`: AP-66 8 (the fake `_send` lambdas and the local HTTP handler — expected in a test file). (Attempt-3's draft said "4 env hits" and "6 hits, all the test's own local HTTP handler / fake send"; the measured counts are 5 and 4/8 — corrected this attempt.) All hits classified: no registry violation in the production path; the AF-AP-175 hit is the intended pin check.

## 8. FILES (this lane's writes, the boundary)
- MODIFY (from the LANE_PATCH; all three verified by run this lane): scripts/qwen_jev.py (494 lines), tests/test_qwen_jev.py (488), docs/research/findings/j2b-variants/qwen27b_j2.py (167).
- CREATE: tests/fixtures/qwen_jev/completion-choice.json + completion-noul.json (captured real /v1/completions responses, 2026-09-25, via scratch/capture_fixtures.py); docs/research/findings/j2b-variants/qwen27b/j2-examples_binary/ (6 variant files + run-summary.json) and .../j2-baseline/ (same 7); the named report tasks/briefs/jev-laya/QJ2-report.md (created by THIS attempt — it was missing in the tree after attempt 3, which had left it only as the lane-dir draft; the coordinator mirrors it).
- READ only (verified unmodified in the worktree): the committed J2 scripts ap_probe.py / v1_probe.py / j2b.py; the J2 samples; laya-ft-eval committed base; OpenJev; Haiku. The runner loads those three committed modules and swaps only their `post` (qwen27b_j2.py:116-121); the "only the URL differs" claim is honored — re-ran the committed scrubber over all 484 sample/row texts (v1 100 + ap sample 100 + ap rows 184 + j2c 100) and exactly 4 change (j2-v1 sample-23, ap sample-92, j2c sample-23, j2c sample-97), matching the runner's stated deviation.
- D-7 compliance: my adapter (pid 1838042) was started by this lane on 47420; its /health reported the lane's revision (pc-qj2.md--d6a2142) and the requested policy before the first request (run-summary health block); after the run it was killed by pid and 47420 is verified free (0 listeners). vLLM on 8080 was left up and untouched (only D-3/D-5-shaped requests to it; no echo/prompt_logprobs/best_of/n ever sent).

## 9. SELF-ATTACK (the three most likely ways this is wrong, ruled out)
1. "The parity/J2 is a hollow green — the adapter scored a model that isn't the one named." RULED OUT: the response `model` is asserted equal to the id sent, and the id is read live from GET /v1/models at start (not hard-coded; the fixtures carry it and the tests assert the echo); M4 kills a loosened check.
2. "0 refused / 0 bounded parity is because the probe is lenient." RULED OUT: the D-4 count check is a hard refusal (M1 kills it) and the cross-check compares label logprobs between two INDEPENDENT paths (chat vs completions) at 0.01 tolerance; ex_binary came back delta-0 / 0.0 on both, which a lenient reader does not produce. The one non-exact spot (baseline noul via chat, delta -1) is reported, not hidden.
3. "The J2 table overstates Qwen because the adapter is not running simple-jev's scoring." RULED OUT: D-1 is enforced (M5 kills the pin check), every answer is built by simple-jev's own `build_response` (M2 kills a re-implementation), and the teacher comparison is apples-to-apples — same two committed samples, committed scripts unchanged (only the URL swapped), scrub deviation measured.

## 10. DEVIATIONS & NOT-DONE
- NOT-DONE: no request was sent through OmniRoute (D-082: the direct path is the scoring path; OmniRoute stays for System 2). The chat cross-check goes direct to vLLM /v1/chat/completions.
- DEVIATION: the noul premise question probed ("Does it block?", scratch/premise.py:87) is not the coordinator's exact premise noul (1037/B); that exact question is not preserved in the tree. The load-bearing claim (delta +0 on the direct path) holds regardless.
- DEVIATION (named in the runner's own docstring, honored): the runner sends unscrubbed (loopback only); 4/484 texts would change under the committed scrubber, so scrubbing would have altered the scored inputs.
- DISCREPANCY (the one real finding on the model side): the BASELINE policy's NOUL question renders 1 token SHORT through the CHAT path only (5/5: prompt delta -1, max|label-logprob delta| 3.51-5.25), while the direct token-id path is delta 0 and the examples_binary chat path is delta 0 / 0.0. A 1-token (not 12) chat-rendering gap in the baseline noul branch; it does not touch the scoring path; candidate for the owner/coordinator to investigate (likely the baseline noul template's answer prefix or a single separator the chat template drops); not fixed here (out of boundary, scoring path exact).
- DISCREPANCY (this lane's own tooling): (a) M7's brief-specified kill test (test_count_mismatch_refused) cannot see defect 1 — the count check passes before the label reader runs; re-pointed to the scoring test. (b) M2's initial helper crashed on a nonexistent ScoringQuestion.type (a hollow-green crash, not a semantic kill); fixed to branch on the 9-label noul scale so the kill is a genuine wrong-ANSWER assertion. (c) attempt-3's max-branch numbers (3761/2920) came from a probe whose question dict did not match the committed ap_probe shape; the fixed probe gives 1613/1006 — the "context fits" conclusion is unchanged and is carried by the zero-refusal runs anyway.
- NOT-DONE: OpenJev, Haiku and the Laya base were NOT re-run — their committed result files were used (Haiku re-scored via its committed haiku_compare.py); the Laya head IS a fresh read of the eval that completed during this lane.

## 11. ATTEMPT-4 VERIFICATION (03:53Z-05:1xZ; the draft's claims re-verified by run before use)
Test suite re-run twice (16/16 both, 2.72s/2.75s); both mutant runners re-run (7/7 red each); premise probe re-run (identical to the brief to the digit); parity outputs re-read (all as claimed); J2 run-summary and per-variant metrics re-verified from the files (match to the digit, including mtimes 03:27Z/04:24Z); committed baselines re-verified (OpenJev, j2b results.json, Haiku via its committed comparator, Laya base + head evaluate-summary.json); scrub re-measured (4/484); gates re-run; port 47420 verified free at end; vLLM untouched. The draft's §5 and §7 contained two imprecise claims (max-branch provenance; ap_screen counts 4/6) — corrected above and flagged as such.

## 12. report_lint (the FLOOR; run LAST with --map aliases named by the lane: qwen=scripts/qwen_jev.py, testqwen=tests/test_qwen_jev.py, runner=docs/research/findings/j2b-variants/qwen27b_j2.py)
Round 1: `9 refs — OK 4, NEAR 0, MISS 3, UNCHECKABLE 2, UNRESOLVED 0 (worktree)` — three `fix:` hints, each applied exactly as printed (one backticked identifier copied from the cited line; one corrected line number 279-283→280-283; one added identifier to the upstream.lock.yaml line). Round 2 (the paste): `report_lint: 9 refs — OK 5, NEAR 1, MISS 0, UNCHECKABLE 3, UNRESOLVED 0 (worktree)`. MISS 0 in two rounds (under the three-round cap); the NEAR (qwen_jev.py:280-283, a token within 1 line of the range) and the three UNCHECKABLE (range-only citations) are as printed. The harvest grades the --min-refs floor plus this paste.

⚠️ File-mutation verifier: 1 file(s) were NOT modified this turn despite any wording above that may suggest otherwise. Run `git status` or `read_file` to confirm.
  • `/home/rocco/agent-factory/.lanes/pc-qj2.md--d6a2142/scratch/run_mutants.py` — [patch] Could not find a match for old_string in the file Did you mean one of these sections? 44| 45| 46| def run(dest, test_name): 47| """Run the named test; return (exit_code, summary_l…
