Verified live: the real checker CLI and two final xdist runs pass. This is a build-lane proposal, not an independent acceptance verdict.

# VB-F12-G1 — S0-01 golden order-free async session metadata

PIN: `772ce3b`  
LANE: `pc-vb-f12-g1.md--772ce3b`  
STATUS: PROPOSAL ONLY. The sandbox adversarial-verifier lane must grade this increment. Nothing was committed, pushed, or minted.

## NOT-done

- Independent verification is NOT done. A separate sandbox-side adversarial-verifier must grade this proposal.
- The coordinator has NOT harvested/committed these bytes and has NOT rebuilt the read-only real-leg corpus.
- No `proofs/S0-01/result.json` was minted in the working tree. The runner check wrote it only in a scratch copy.
- The literal C6(i) wording, “move the first `agent_message_chunk` before the `session/prompt` request and expect a golden mismatch,” is structurally unreachable: `check_prompt_turn` runs before `check_golden` and rejects that capture first. Three bounded probes reached, in order: timeline-seq rejection; route-window rejection after repairing seq; then exact `failure_reason: run-2: no agent_message_chunk between prompt and terminal` after repairing timestamps/splits. The nearest valid order mutation, swapping the chunk with its following in-window `usage_update`, reaches `check_golden` and is recorded below.

## FILE IDENTITY

The five code/evidence boundary paths are modified; `tasks/briefs/s0-01-vb-f12-support/G1-report.md` is the requested untracked handoff artifact. `git diff --check` rc 0.

- C `proofs/S0-01/check_acp_conformance.py`: `868b8705699b5e78b1468252ecbdec93736d2a7e2f4819424311c31c243db46a`
- P `proofs/S0-01/pins.py`: `1a2f9a38ddba14e3ea75c06e77e43083a059e8dc5caf5499c7e54e9013921981`
- G `proofs/S0-01/evidence/golden/golden.jsonl`: `6225adb8ecc21a24d578696e2b9c25c81ebd5a82068c4411f780930c2fa54221`
- T `tests/test_s0_01_check_acp_conformance.py`: `a09e96ad4ab7741891ab5c28bf17ae01989a09c9de2c521e75416098e4670935`
- S `tests/test_s0_01_spec_runner.py`: `8c0e280c17bb5afbdfe5876c5ffe7f64aebe8fa54f0cb112467fdb18ad45ea96`

## VERIFIED changes

- P:130-145 defines the closed tuple `ASYNC_SESSION_UPDATES = ("session_info_update",)` and pins G to `6225adb8ecc21a24d578696e2b9c25c81ebd5a82068c4411f780930c2fa54221`.
- C:38-41 imports `ASYNC_SESSION_UPDATES` beside the other pins.
- C:795-887 rewrites `normalize_timeline`: pass 1 normalizes only synchronous records and assigns `<IDn>` / `<SIDn>` placeholders; pass 2 normalizes pinned async notifications, sorts their JSON lines, and slots each after the first synchronous a2c response that introduced its session. A malformed unknown-session async record goes after the last synchronous record.
- G:1-11 is regenerated from real run-1. Per-record shapes are unchanged; only `session_info_update` moves to G:5, immediately after the session/new response at G:4. G remains 11 lines.
- T:523-580 retires the strict AF-AP-107 xfail, pins the exact real-bundle PASS line, and updates the subprocess pin-mismatch expectation.
- T:1943-2056 adds `test_golden_async_notification_is_order_free`, `test_golden_async_placement_is_independent_of_the_session_new_response`, `test_golden_synchronous_frame_order_still_binds`, and `test_golden_async_set_is_closed` (5a–5d).
- T@772ce3b:112-145 carried the now-dead `_ASYNC_UPDATES`, `_session_update_kind`, and `_align_async_order`; the current tree removes them and the synthetic run-2 alignment call.
- T:2074-2093 updates `test_golden_regen`: regenerated synthetic golden bytes now fail against the set REAL golden pin.
- S:1-20 starts `S0-01 through the CANONICAL proof-runner`; it documents `test_committed_bundle_runner_mints_a_result`.
- S:102-119 defines `test_committed_bundle_runner_mints_a_result`: rc 0, silent stdout/stderr, and `result.is_file()`.
- S:122-139 keeps `test_committed_negative_leg_cmd_reports_the_protocol_violation` unchanged in behavior.

## RED-FIRST / GREEN

Exact deterministic reproduction against the PIN’s real `normalize_timeline`, then the current implementation:

- 5a RED PIN: `11 distinct normalized outputs over 11 insertion positions (expected 1)`
- 5a GREEN CURRENT: `1 distinct normalized output over 11 insertion positions`
- 5b RED PIN: `before==after is False; sid before/after <SID1>/<SID1>`
- 5b GREEN CURRENT: `before==after is True; sid before/after <SID1>/<SID1>`
- 5c CONTROL PIN: `moved!=original is True`
- 5c CONTROL CURRENT: `moved!=original is True`
- 5d CONTROL PIN: `moved!=original is True`
- 5d CONTROL CURRENT: `moved!=original is True`

The controls remained position-sensitive under both implementations. They did not become tautologies.

## REAL GOLDEN EQUALITY

- `OLD n1==n2: False; checker index: 7`
- OLD run-1 index 7: `{"dir":"a2c","kind":"notif","method":"session/update","sessionId":"<SID1>","sessionUpdate":"session_info_update","update":{"updatedAt":"str"}}`
- OLD run-2 index 7: `{"dir":"a2c","kind":"notif","method":"session/update","sessionId":"<SID1>","sessionUpdate":"agent_message_chunk","update":{}}`
- `NEW n1==n2: True; normalized lines: 11`
- First: `{"clientCapabilities":{"auth":{"terminal":true}},"clientInfo.name":"buzz-acp","dir":"c2a","id":"<ID1>","kind":"req","method":"initialize","protocolVersion":2}`
- Last: `{"dir":"a2c","error":false,"id":"<ID3>","kind":"resp","result_keys":["stopReason","usage"],"stopReason":"end_turn"}`
- `sha256sum G`: `6225adb8ecc21a24d578696e2b9c25c81ebd5a82068c4411f780930c2fa54221`

The checker intentionally reports the zero-based first-difference index (`C:1563-1564`), so historical “normalized line 7” means Python index 7, the eighth JSONL record.

## ITEM 8 — REAL CHECKER CLI

Command: `python C proofs/S0-01/evidence` with the §Gate environment.

- rc: `0`
- stdout, whole:

`PASS: S0-01 acp-conformance - 63 checks executed over 5 legs; golden x2 identical (11 normalized lines, sha256 6225adb8ecc2); negative: observed: observed: error code=-32602 message=Invalid params`

- stderr: empty

## ITEM 7 — REAL PROOF-RUNNER ON AN UNSTRIPPED SCRATCH COPY

- rc: `0`
- stdout: `''`
- stderr: `''`
- `proofs/S0-01/result.json` present in the COPY: `True`

De-vacuous mutation in S:113 changed `assert r.returncode == 0` to expected runner rc `1` on a scratch test copy:

- RED: `1 failed in 4.00s`
- Exact assertion: `AssertionError: expected exit 0, got 0: stdout='' stderr=''`
- Restored: `1 passed in 3.66s`
- Source restored: `True`

## C6 PRE-MINT GATE

All mutations ran through the real checker CLI on scratch copies. No tracked evidence leg was changed.

| Case | Mutation | rc | Exact verdict |
|---|---|---:|---|
| i | Nearest protocol-valid substitute: run-2 `agent_message_chunk` swapped with following `usage_update`, coherently in timeline + a2c split | 1 | `failure_reason: golden: golden mismatch between run-1 and run-2 at normalized line 8` |
| ii | run-2 `session_info_update` payload added non-volatile key `extra=1`; position unchanged | 1 | `failure_reason: golden: golden mismatch between run-1 and run-2 at normalized line 4` |
| iii | G byte 10 flipped | 1 | `failure_reason: golden: golden.jsonl sha256 bd9784be4294 != pinned 6225adb8ecc2` |
| iv | P scratch copy set to the PIN’s OLD G sha `265f6809747b…` | 1 | `failure_reason: golden: golden.jsonl sha256 6225adb8ecc2 != pinned 265f6809747b` |
| v | untouched scratch copy | 0 | `PASS: S0-01 acp-conformance - 63 checks executed over 5 legs; golden x2 identical (11 normalized lines, sha256 6225adb8ecc2); negative: observed: observed: error code=-32602 message=Invalid params` |

Literal C6(i) bounded experiments:

1. Raw move: `failure_reason: run-2: timeline seq not strictly 1..N at index 5`.
2. Seq/timestamps repaired: `failure_reason: run-2: upstream POST record received_at 2026-09-21T13:39:59.834877Z outside all prompt windows`.
3. Capture envelope and split repaired: `failure_reason: run-2: no agent_message_chunk between prompt and terminal`.

This follows check ordering: `check_prompt_turn` runs at C:1826; `check_golden` runs later at C:1856.

## TEST GATES

The required bridge launcher could not run: private bridge endpoint probe returned `bridge_http_code=000`. I did not fabricate bridge output. This lane is already on the PC, so I ran the same two test files directly under pytest-xdist `-n 8`, twice, on final bytes:

- `pytest-summary: 476 passed in 75.49s (0:01:15)` — rc 0
- `pytest-summary: 476 passed in 76.41s (0:01:16)` — rc 0
- `pytest-set: 2 files set=fa5f94aece8d — tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py`

ZERO failed, skipped, or xfailed. The three conditional corpus markers in T did not fire on the declared v2.4 corpus. The removed static strict xfail is absent.

- `python -m pyflakes C P T S`: rc 0, no output.
- `python3 scripts/ap_screen.py --s0-01 C`: rc 0. Screen reports pre-existing project hits; no new C hit from this diff.
- `python3 scripts/ap_screen.py --tests T S`: rc 0. Last classes: `AP-66: 2`, `AF-AP-48: 1`, `AF-AP-57: 1`; all cited lines pre-exist this diff.
- `git diff --check`: rc 0.
- GitNexus `detect-changes`: `Changes: 5 files, 30 symbols`, `Affected processes: 0`, `Risk level: low`; clone-index line mapping is noisy, so this is advisory only.
- ripwire callers: `normalize_timeline` has 15 indexed callers; `check_golden` is the production caller. Added test definitions: T:1943 `test_golden_async_notification_is_order_free`, T:1977 `test_golden_async_placement_is_independent_of_the_session_new_response`, T:2010 `test_golden_synchronous_frame_order_still_binds`, T:2036 `test_golden_async_set_is_closed`.

## DISCREPANCIES

1. **Item 6 corpus premise does not reproduce.** `/home/rocco/s0-01-pinned/realleg/golden` has no `golden.jsonl` at top level or recursively. AST inspection of every `test_real_leg_*` found no test reading `golden.jsonl` or `PINNED_GOLDEN_SHA256`. No corpus-bound red exists to paste. The coordinator must rebuild the corpus at harvest, but this lane cannot demonstrate a nonexistent stale file.

2. **C6(i) literal move is structurally blocked before `check_golden`.** The nearest valid in-window order mutation proved that `check_golden` acts and names normalized index 8.

3. **Bridge gate unavailable.** `pc_suite.sh launch` could not reach its private bridge (`HTTP 000`); direct PC xdist was used twice instead. This is a gate-mechanism deviation, not a test-content deviation.

4. **Historical line wording is zero-based.** `check_golden` reports enumerate index 7, not human line 8.

5. **report_lint:** `24 refs — OK 22, NEAR 2, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## SELF-ATTACK

1. **Risk: async placement still changes placeholder assignment.** Ruled out by 5a over all 11 insertion positions (NEW distinct=1), 5b before-vs-after equality with `<SID1>` on both paths, and real `n1 == n2`.

2. **Risk: the implementation accidentally made all session updates order-free.** Ruled out by T:2010 `test_golden_synchronous_frame_order_still_binds` (`agent_message_chunk`) and T:2036 `test_golden_async_set_is_closed` (`tool_call` outside the closed tuple). Both controls differ under the current normalizer. P:138 contains exactly one pinned kind: `ASYNC_SESSION_UPDATES`.

3. **Risk: tests are green while the real outer boundary still fails.** Ruled out by the checker CLI (63 checks, rc 0), real proof-runner on an unstripped scratch copy (rc 0 + `result.json`), two full xdist passes, and four hostile C6 mutations that fail at the intended golden boundary while untouched control passes.

## EVIDENCE TIERS

- VERIFIED: file hashes, diffs, red-first lines, real CLI output, runner output, C6 outputs, two xdist summaries, pyflakes, ap_screen, Git status, and item-6 filesystem/AST probes were produced on final bytes.
- INFERRED: coordinator corpus rebuild should populate harvest-specific derived corpus state; this lane did not mutate the read-only corpus.
- ASSUMED: no claim depends on an unstated external service. The bridge was unavailable and is reported as such.

## REASONING RECORD FOR COORDINATOR COMMIT MESSAGE

- Primary source: AF-AP-107 plus real v2.4 run-1/run-2 timelines.
- Rejected alternative: preserve test-only `_align_async_order`; it hides the production normalizer race and leaves the real checker red.
- Ordering rationale: normalize the synchronous protocol stream first so IDs/SIDs are position-independent; normalize and sort only the closed pinned async kind; attach it to the session-introducing response. All other notification order remains binding.
- Disjoint hunks: P pin/constant; C import+normalizer; G regenerated order; T red-first/xfail/artifice retirement; S real runner success.

## GATE RECOMMENDATION

`MERGE-READY-WITH-FOLLOWUPS` as a build-lane proposal, not a verdict.

Follow-ups before acceptance:

1. Sandbox adversarial-verifier grades this proposal.
2. Coordinator rebuilds the derived real-leg corpus.
3. Coordinator decides whether to rewrite C6(i)’s impossible literal wording for future briefs.
4. Coordinator mints only after independent verification passes.

Report artifact: `/home/rocco/agent-factory/.lanes/pc-vb-f12-g1.md--772ce3b/tree/tasks/briefs/s0-01-vb-f12-support/G1-report.md`
