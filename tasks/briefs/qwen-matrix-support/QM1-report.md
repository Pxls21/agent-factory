# QM1 report — L1 concurrency-matrix runner

## Outcome

REVIEW-PENDING — built the corpus/load/table tool and per-cell runner against QM0's real seams. The focused static-copy gates are deterministic. The full harness suite reached the new tests but remains red on an unchanged dispatcher-suite venue problem. The supplied scrubbed exports are too small for a 100K-token corpus, so the live matrix remains blocked on external input. This build lane does not issue a gate verdict; sandbox-side adversarial verification still owns acceptance.

## NOT done

- No real matrix cell ran. No server stop, restart, reinstall, live load, or real GPU sampling occurred.
- No 100K corpus exists. Live `/apply-template` + `/tokenize` measured the supplied medium export at 29,824 tokens and xhigh export at 47,865; the builder refuses both with rc 2 and leaves no prompt file.
- `harness-ports/tests/run-all.sh` did not print `ALL SUITES PASSED`: unchanged `test_pc_lane_dispatcher.sh` printed `0 passed, 9 failed` on both the lane and `git show HEAD` bytes.
- Independent adversarial verification has not run. These bytes are a proposal.

## Built

- `harness-ports/bin/qwen_matrix.py`: parses the actual Hermes export grammar, turns the first user turn into the system message, preserves summarized tool turns as user-wrapped `<tool_response>` content, asks live `/apply-template` then `/tokenize` for prompt size, and fails closed if the export cannot reach the target (M:85-98, M:100-121, M:129-180).
- The load path validates OpenAI chat messages, reads the keyed `/props` and five pinned `/metrics` values, dispatches N requests together, rotates prompt indices each round, records response usage and timings, computes aggregate rates from counter deltas, and counts only re-prefill log lines after the round's byte offset (`REQUIRED_METRICS`, `_read_prompt`, `message`, `request_rows`, `parse_metrics`, `_count_reprefills`; M:183-233, M:236-259, M:285-301, M:304-322, M:345-385).
- The table rejects missing/duplicate A and non-finite metrics, prints the measured fields, and evaluates `>= 1.5x A` plus `re-prefills < A` (M:401-436).
- `harness-ports/bin/qwen-matrix.sh`: calls the launcher-owned `guard` before creating a `CELL_DIR`, binds overrides plus execution controls, captures exact rendered argv text/hash and unit hash, installs the cell through the launcher, samples GPU memory with `sample_gpu`, runs the Python tool, and restores the baseline unit through launcher `install` on success or failure (R:27-53, R:55-85, R:87-128, R:130-159).
- `harness-ports/tests/test_qwen_matrix.py` and `harness-ports/tests/test_qwen_matrix_sh.sh` cover corpus cut/exhaustion, keyed HTTP, metrics/aggregation, actual request overlap, prompt rotation, table decisions, guard ordering, artifact identity, baseline restoration, and exact negative exit paths. Both are wired into `harness-ports/tests/run-all.sh`.

## Seam evidence

- QM0 exposes the six matrix controls and validates their domains before argv/unit rendering: `QWEN_CACHE_RAM`, `QWEN_CTXCP`, `QWEN_CMS`, `QWEN_UBATCH`, `QWEN_SPEC_P_MIN`, and `QWEN_SPEC_TYPE` (S:43-49, S:66-89, S:91-114).
- The launcher-owned side-effect-free guard classifies live lane routes and returns rc 7 for any LOCAL lane (S:159-185). Changed `install` calls it before persistent paths and systemd operations (S:223-249).
- Live read-only probes through the implementation accepted `/props`: model `qwen3.8-27b-local`, one slot, context 262,144, build `b1-00139b6`; and exactly the five values in `REQUIRED_METRICS` (M:21-27). The API key stayed in a process-local variable and was never printed.
- The real export shape comes from `hermes-session-export.py`: ordered rows from `messages`, tool result summaries, and capped scrubbed non-tool bodies (E:48-65). The supplied export begins at `## user @ 15:51:45` with the full lane brief in its first body (X:9-21).
- The real launcher guard refused a dry runner invocation with rc 7 because VERIFY-GOV1 is LOCAL-classified. The unit SHA stayed `50de3abf9dbb7d1da152a2ecbcd227cd0045d8de4dd988fabff88258b2cf64ca` before and after; no cell directory appeared.

## Test evidence

- Red before implementation: `FileNotFoundError: .../harness-ports/bin/qwen_matrix.py`.
- Focused deterministic runs: `test_qwen_matrix: 4 tests passed` twice; `qwen-matrix-sh: 9 passed, 0 failed` twice.
- Static-copy run 1: `RESULT: rev=efde78dff749 files=5 deleted=0 runs=1 tests=9059ec51f087 identical=yes rc=0 summary="4 passed in 0.61s"`.
- Static-copy run 2: `RESULT: rev=efde78dff749 files=5 deleted=0 runs=1 tests=9059ec51f087 identical=yes rc=0 summary="4 passed in 0.61s"`.
- Static gates: `py_compile`, `pyflakes`, `bash -n`, and `git diff --check` returned rc 0.
- Full harness run reached the new suites: `qwen-server: 79 passed, 0 failed`; `test_qwen_matrix: 4 tests passed`; `qwen-matrix-sh: 9 passed, 0 failed`. Overall rc 1: `pc_lane dispatcher: 0 passed, 9 failed`; final line `1 SUITE(S) FAILED`.

## Self-attack

1. The tool could report a target-sized corpus from a shorter export. Ruled out by the committed exhaustion control and live medium/xhigh rc 2 runs; zero `prompt-*.json` files remain after refusal.
2. The runner could alter the unit before checking lane ownership or fail to restore it. Ruled out by a real-child-PID guard control (`rc 7`, no cell directory/install call), success-byte restoration, and load-failure-byte restoration. The real launcher refusal independently preserved the live unit SHA.
3. The load/table results could be hollow from serialized requests, missing counters, fixed prompt order, or a shifted threshold. Six scratch mutants compiled/parsed first and then died: required-counter deletion; fixed prompt order; one-worker pool; 1.7x threshold; guard rc forced to zero; baseline reinstall bypassed. Shell mutants printed `8 passed, 1 failed` and `6 passed, 3 failed`; Python mutants returned rc 1 at their mechanism assertions.

## Anti-pattern screen

- Production: 9 heuristic hits. AP-1 (4) is the CLI env/config surface resolved at argument parsing; AP-32 (3) is required `argv_sha256` identity; AF-AP-39 (1) records run controls; AF-AP-40 (1) resolves a supplied result file/directory before reading. No silent failure path was accepted.
- Tests: AP-66 (6) resets fixture-server state; AF-AP-33 (1) is the explicitly labelled fake health sink. The shell test states that service/network/GPU seams are fakes.
- `lane_context.sh` produced a 162-line diff pack. Ripwire mapped `run_load` to the CLI and test caller. GitNexus `detect-changes` returned `No changes detected.` because its clone index cannot see detached-lane new files; risk is UNKNOWN, not low.

## Discrepancies

- Supplied-export premise: neither scrubbed export reaches 100K tokens. A real 100K export or prebuilt corpus is required before the matrix can run.
- Full-suite premise: the unchanged dispatcher test fails 9/9 on this venue. This lane did not touch its implementation or test.
- Tooling fail-open: the first `lane_context.sh -o ../scratch/...` call ran before that parent existed. The wrapper printed shell errors, returned rc 0, and falsely claimed it wrote an empty pack. Re-running after parent creation produced 98 lines. This is outside the brief's allowed files and needs coordinator bug-echo/repair.
- Final report lint: `report_lint: 21 refs — OK 21, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## File identity

- `harness-ports/bin/qwen_matrix.py`: `c29034ebc95045c15c244da382691048e5d8e79b10c55b71007353d34aaec802`, 507 lines.
- `harness-ports/bin/qwen-matrix.sh`: `0bac99de34174c76fccc03350cd077a9f29f05d1c5dbdce80b03fd048ad4cba5`, 159 lines.
- `harness-ports/tests/test_qwen_matrix.py`: `de7a4958de020e38e1ea8a0e5a3135af3b90079262c9bdfa4485b3464a6da45c`, 301 lines.
- `harness-ports/tests/test_qwen_matrix_sh.sh`: `49196603b2b6682c930cd7b4eafefaa839137820915285aefbd049a475679383`, 132 lines.
- `harness-ports/tests/run-all.sh`: `d69b33b537ded62ee3c6a5420cbe54151f98d2417ca48f860b1ac1aef7ad7b3c`, 68 lines.

## Handoff

- Rejecting alternative: no copied guard and no direct systemctl path. The launcher remains the sole safety and lifecycle seam because QM0 already owns route classification, knob validation, and pre-write guarding.
- Ordering rationale: guard before any cell artifact; render and persist identity before service change; arm cleanup before install; install and health before load; stop owned sampler; merge VRAM; restore baseline last and verify exact unit SHA.
- Primary sources: current `qwen-server.sh`, live `/apply-template`/`/tokenize`/`/props`/`/metrics`, real exported sessions, and findings matrix §4.
- Coordinator must supply a real 100K corpus, repair or explicitly waive the unrelated dispatcher venue failure, register the `lane_context.sh` output-parent fail-open class, then dispatch the independent verifier. Retro: that output-parent fail-open is the one lesson to bake; no other protocol change proposed.
