# VERIFY-VB-F12 report — adversarial verification of the S0-01 mint (v2.4 capture + order-free golden, owner decision (a))

PIN: 955ab74 · lane: pc-verify-vb-f12.md--955ab74 · role: adversarial-verifier (local Qwen, xhigh)
Scope: V1 golden-decision reach · V2 seed intent · V3 evidence bundle · V4 mint attested inputs · V5/V6 mutant audit · V7 doubled prefix · V8 lane-claim reproduction · V9 sweep.

Gate env (every run): S0_01_VENUE=pc, S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden, S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz; /home/rocco/venv-agent-factory/bin first on PATH; scratch = ../scratch.

## V1 — the golden decision's REACH (SOLID — every probe reproduced through the real checker CLI on scratch copies)

Method: scratch copies of the committed bundle; run-2 (or run-1) timeline mutated, seq 1..N re-synced, a2c/c2a splits + tee-status recomputed to the mutated timeline, then the REAL `python3 proofs/S0-01/check_acp_conformance.py <evidence>` (env per VENUE-MAP). Only the moved/inserted frames are re-stamped, so the c2a prompt/terminal frames (which define the upstream POST window, C:660-680) keep their original timestamps and the probe reaches the check under test.

Command: `cd ../scratch/v1 && python3 hostile.py` → (i) duplicate async rc=1 mismatch line 5; (ii) foreign sid rc=1 `notifications carry a foreign session id`; (iii) before-initialize rc=0 PASS; (iv) duplicate after terminal rc=1 mismatch line 5; (v) altered payload rc=1 mismatch line 4. `python3 run1_after.py` → `run-1 async moved after terminal: 0` and the 63-check PASS. `python3 hostile-one-payload.py | grep -A1 v1a-one-payload-alter` → rc=1 mismatch line 4. SOLID.

| case | mutation (run-2 unless noted) | outcome (exact) |
|---|---|---|
| V1(b) duplicate | a SECOND `session_info_update` appended after the terminal | rc=1 `golden: golden mismatch between run-1 and run-2 at normalized line 5` — the count binds (n1 has 1, n2 has 2). |
| V1(c) foreign sid | the async frame's `sessionId` changed to a foreign uuid | rc=1 `run-2: notifications carry a foreign session id` (C:775, `raise Failure` inside `check_prompt_turn`) — that check runs ahead of `golden_lines = _run_check(check_golden, "golden", golden)` (C:1856). |
| V1(d) before-init | the async frame moved to BEFORE the `initialize` request | **rc=0 PASS** — intended by the decision: the normalizer (C:795-811) slots every `ASYNC_SESSION_UPDATES` frame right after the `session/new` response, so it normalizes to the SAME position the golden was generated from. The first-line rule (C:1582-1584: first normalized line must be the c2a `initialize` request) still holds — the moved frame is a2c, so it never becomes first. |
| V1(d) after-terminal | the ONE run-2 `session_info_update` occurs after the raw `end_turn` terminal (committed baseline), and run-1's one async was independently moved there | **rc=0 PASS**; normalization re-homes it after the session/new response, so the first normalized line remains initialize and the last remains end_turn. |
| V1(d) duplicate after-terminal | a SECOND async frame appended after terminal | rc=1 `golden: golden mismatch ... at normalized line 5` — the count binds. |
| V1(e) payload-alter | a second async frame whose `update` carries an extra key (`extra:1`) | rc=1 `golden: golden mismatch ... at normalized line 4` — `first = next((i for i, (a, b) in enumerate(zip(n1, n2)) if a != b), min(len(n1), len(n2)))` at C:1563-1564 detects the differing normalized line. |
| V1(d') run-1 side (symmetric) | run-1's single async frame moved AFTER its terminal | **rc=0 PASS** — symmetric: both runs normalize to the same 11 lines regardless of where the async landed. This is exactly the race the decision redefines. |

V1(a) (a DIFFERENT payload in run-2): reproduced against ONE existing `session_info_update` frame, with the count and position unchanged, by adding non-volatile `extra:1`; real checker result: rc=1 `failure_reason: golden: golden mismatch between run-1 and run-2 at normalized line 4`. The normalized line is `{"dir":"a2c","kind":"notif","method":"session/update","sessionId":"<SID1>","sessionUpdate":"session_info_update","update":{"updatedAt":"str"}}`; a changed payload changes the sorted JSON line and the `n1 != n2` comparison catches it. SOLID.

V1(e) (other checks consuming raw order for the async frame): **no other check binds the async frame's relative raw position** — deliberately. V1(d)'s valid before-initialize and after-terminal moves both PASS, proving that raw position is the exception the owner decision makes order-free. Raw timeline integrity still applies: `check_timeline` enforces seq 1..N, monotonic `t_mono_ns`/`t_utc`, and exact timeline→a2c/c2a split parity (C:267-340); `check_tee_status` binds per-direction counts/last seq. The protocol-ordered sub-stream (the ten non-async normalized lines) remains fully order-bound: the prompt must precede its terminal with an `agent_message_chunk` between (C:765-775), and all non-async normalized lines are golden-compared. Thus the only order information lost is the explicitly designated async frame's relative position, not its count, session identity, payload shape, or the order of the protocol-defined stream.

## V4 — the mint's attested inputs (AF-AP-56) (SOLID — all three sub-claims reproduced)

1. `scripts/validate-ledger integrity --root .` → rc 0, prints `S0-01 PRESENT` (full 12-line table: S0-01/03/04/06/07/08/09/10/11/12 PRESENT, S0-02/05 ABSENT; four-way numerators as printed). SOLID.
2. Commands in fresh archive copy: `python3 proofs/S0-01/check_acp_conformance.py proofs/S0-01/evidence` → rc=0 and `ae7ea2ee…` stdout / `e3b0c442…` stderr; `python3 proofs/S0-01/check_initialize.py request proofs/S0-01/evidence/golden/negative` → rc=1 and `319663a8…` stdout / `e3b0c442…` stderr.
   - positive: `ae7ea2ee…` (stdout) / `e3b0c442…` (stderr, empty) — EXACTLY the committed result.json values.
   - negative: `319663a8…` (stdout) / `e3b0c442…` (stderr) — EXACTLY the committed result.json values.
   The mint's `stdout_sha256`/`stderr_sha256`/`exit_code`/`failure_reason` are therefore byte-faithful to what the two commands produce today. SOLID.
3. Re-ran `python3 scripts/proof-runner run --proof S0-01 --venue pc-bridge --root <scratch>` (rc 0). The re-minted `result.json` differs from the committed one only in non-deterministic fields:
   - `recorded_at` (2026-09-21T20:59:09.915655Z → …21:34:18.480262Z)
   - `env_fingerprint` (`pc-bridge:vm` → `pc-bridge:fedora`) — the mint ran on the VM; this PC is fedora.
   - the per-run `started_at`/`finished_at` timestamps, and
   - the derived whole-record `digest` (`86118573…` → `aeb7da57…`) which hashes those fields.
   Every deterministic field (both legs' `cmd`, `exit_code`, `stdout_sha256`, `stderr_sha256`, `failure_reason`, `negative_control`) is IDENTICAL. The digest difference is expected: it is derived from the wall-clock fields. This is NOT a defect — the mint's digest is valid for the mint's own recorded fields; a different host timestamp legitimately yields a different digest. SOLID.
4. `python3 scripts/ledger-gen --root <scratch>` reproduces `proofs/ledger.json` BYTE-IDENTICAL (diff rc 0). SOLID.

## V8 — the lane process claims (reproduced)

The G1 report (PIN 772ce3b) claims: (i) `n1 == n2` after the normalizer change; (ii) a 5a red line against the PIN's OLD normalizer (reproduced via `git show 772ce3b:proofs/S0-01/check_acp_conformance.py` on a scratch copy); (iii) the C6 (i)-(v) table.

- (i) `n1 == n2` SOLID: the current normalizer produces 11 normalized lines, identical for run-1 and run-2 (see V1's `n1n2_new.py` output: `NEW n1==n2: True`). The golden is 11 lines, sha `6225adb8…`.
- (ii) 5a red against the OLD normalizer SOLID: in the `772ce3b` (old) tree, `n1==n2: False; checker index: 7` — run-1's normalized line 7 is `session_info_update`, run-2's is `agent_message_chunk`. This is EXACTLY the failure the pre-decision test pinned (`golden mismatch between run-1 and run-2 at normalized line 7`). So the test was genuinely RED on the old normalizer and is GREEN on the new one. The golden's pre-decision sha was `265f6809…` (now `6225adb8…`). SOLID.
- (iii) C6 table SOLID, independently reproduced by `cd ../scratch/c6 && python3 run.py`: (i) protocol-valid chunk/usage adjacent swap → rc=1 `golden mismatch ... normalized line 8`; (ii) ONE existing async payload altered → rc=1 mismatch line 4; (iii) golden byte changed → rc=1 `golden.jsonl sha256 28a8d82018de != pinned 6225adb8ecc2`; (iv) pin reset to old `265f6809…` → rc=1 current sha != pinned; (v) untouched control → rc=0 exact 63-check PASS. The original literal C6(i) is unreachable because `check_prompt_turn` precedes `check_golden`; this uses the nearest protocol-valid swap.

## V3 — the evidence bundle's integrity, independently (SOLID — every sub-claim reproduced from the committed bytes)

- Manifests: command `python3 ../scratch/v3/manifests.py` → for all five positive legs `pre==post: True pre==baseline: True baseline-gz==PINNED_GZ: True`; negative `NO-MANIFESTS` (correct different leg shape).
- Per-tree digests: independently recomputed each tree section's sha256 (concatenated body lines) and compared to `PINNED_BASELINE_DIGESTS` — hermes-agent `31843deb…`, buzz `a5614f3c…`, acp `0039fb35…`, venv-hermes `c181f47c…` ALL match for the baseline and for every leg's manifest-pre. SOLID.
- `buzz-acp.pid` committed in every positive leg (AF-AP-62 sibling, fixed in .gitignore): `git ls-files proofs/S0-01/evidence/golden | grep buzz-acp.pid` → run-1, run-2, cancel, shutdown, two-users (5 files). SOLID.
- Mention receipts bound to the relay: for all five legs, `mentions/owner.receipt.json: event_id` == `mentions/owner.event.json: id` (e.g. run-1 `835a139f…`). The receipt carries the relay's `event_id` + the recipient pubkey; the event carries the relay's `id`, `sig`, and `created_at`. SOLID.
- Negative leg: observed error code/message (`-32602`/`Invalid params`) == `pins.PINNED_NEGATIVE_ERROR_CODE`/`_MESSAGE`; `runtime-identity.json` carries `probe_sha256` (`f42a9025…`), `agent_interpreter_sha256` (`8be0f8e5…`) == pin, `agent_interpreter_realpath` (`/usr/bin/python3.13`), `agent_exit_code: 0`. The `agent-stderr.txt` (933 bytes) contains ZERO matches of the checker's `_STDERR_LEAK_RE` secret-shape regex (the leak guard). SOLID.
- `tee-status.json`: validated by `check_tee_status` (the 12-key shape + the recorded/forwarded counts equal the timeline's per-dir counts, `updated_seq` within one of the last seq) — the real checker PASS already exercised this; I additionally confirmed the counts recompute to the timeline for the V1-mutated trees (see V1's `_fix_tee`). SOLID.

## V5/V6 — the meta-tests as gates, not mirrors (BLOCKER F1; canonical scratch reproduction)

### Mutant table (all scratch copies of `git archive 955ab74`; no production tree changed)

| ID | production mutation | named test first run | outcome | disposition |
|---|---|---|---|---|
| M1 | `ASYNC_SESSION_UPDATES += agent_message_chunk` | T:2010 `test_golden_synchronous_frame_order_still_binds` | **SURVIVED** (`1 passed`). The test's `moved` expression duplicates `entries[idx+1]`, so it observes a 12-entry addition, not a swap. `test_real_bundle_passes_every_check` kills M1 because the committed frozen golden disagrees, but that is an accidental golden mismatch, not a direct closed-set test. | covered for today only; test-specific hollow green (see F1) |
| M2 | slot every async line at end (`intro.get(...)`→`None`) | T:1943 `def test_golden_async_notification_is_order_free()` | **KILLED**: `last normalized line is not the end_turn terminal` at T:1966. | SOLID |
| M3 | include async records in pass 1 (`sync = [norm(entry) for entry in entries]`) | T:1977 `def test_golden_async_placement_is_independent_of_the_session_new_response()` | **KILLED**: `async notification before the session/new response changed the output` at T:1997. | SOLID |
| M4 | `ASYNC_SESSION_UPDATES += tool_call` | T:2036 `def test_golden_async_set_is_closed()` | **SURVIVED** (`1 passed`) for the same duplicated-neighbour defect. Full two-file suite also SURVIVES: `476 passed in 77.84s`. Canonical real-checker path below proves material loss. | **BLOCKER F1** |
| M5 | skip `if frozen_sha != PINNED_GOLDEN_SHA256` (C:1570) | T:2074 `test_golden_regen` | **KILLED**: `assert rc == 1` at T:2092 sees success. | SOLID |
| M6 | force `check_bundle` to raise `Failure("MUTANT broken checker")` | `S:106 def test_committed_bundle_runner_mints_a_result` | **KILLED**: expected runner rc=0, got 1; actual canonical runner stderr `leg-exit-mismatch: S0-01 positive expected 0 got 1`. | SOLID |
| M7 | delete `golden/negative` evidence leg | `S:127 def test_committed_negative_leg_cmd_reports_the_protocol_violation` | **KILLED**: expected rc=1, got 2 (`deferred: negative probe not captured`). | SOLID |
| M8 | remove `async_lines.sort(key=lambda item: item[1])` (C:880) | 5a/5b/5c/5d/regen/real-bundle and full two-file suite | **SURVIVED**: each named test passed; whole current evidence suite `476 passed in 81.32s`. Canonical real-checker path below proves material loss. | **BLOCKER F1** |

### Canonical discriminators for the two full-suite survivors

1. **M4 closed-set violation — command `cd ../scratch/canonical-mutants && python3 run.py`:** fresh scratch evidence converted ordinary `usage_update` to `tool_call` in both runs, moved run-2's tool_call after terminal, regenerated golden+pin with correct code. Widened M4 checker rc=0 PASS; corrected checker on SAME evidence rc=1 `failure_reason: golden: golden mismatch between run-1 and run-2 at normalized line 6`. This proves M4 makes forbidden `tool_call` ordering irrelevant while the frozen tuple is closed. Canonical path: real CLI. SOLID.
2. **M8 sort deletion — same command:** fresh scratch evidence contains TWO distinct valid `session_info_update` metadata records (A/B) in opposite raw orders; golden+pin generated with correct canonical sort. Correct checker rc=0 `golden x2 identical (12 normalized lines, sha256 c9e7f414126a)`; M8 rc=1 `failure_reason: golden: golden mismatch between run-1 and run-2 at normalized line 4`. Thus sort deletion breaks valid multi-async order-freedom, while all existing tests miss it because committed data has only one async line (sort no-op). Canonical path: real CLI. SOLID.

**F1 — BLOCKER.** Contract mapping: the frozen decision defines a CLOSED `ASYNC_SESSION_UPDATES` set and sorted JSON-line multiset canonicalization (pins.py:130-145; C:874-880; T:2036-2056). Canonical reproduction: M4/M8 reproduce through the real checker CLI on a scratch copy. Material effect: M4 accepts a forbidden non-async order; M8 rejects valid order-free multiple async notifications. Concrete discriminator: exact CLI commands/outcomes above. Task ownership: checker tests/normalizer boundary. All five blocking-predicate clauses are met.

Root cause: T:2023-2026 and T:2051 compute `moved` as `... + entries[idx+1:]`; the adjacent neighbour occurs twice. Correct adjacent-swap form ends with `entries[idx+2:]`. My exact comparison: on current code the malformed variant has len=12 and differs (as it should); on M1/M4 it ALSO differs because it added a second frame, while the correct 11-entry adjacent swap is equal (the actual violation). The controls appear green for the wrong reason.

`test_golden_regen` coverage conclusion: C:1578 (`raise Failure` for normalized runs differing from frozen golden) remains independently tested by T:1872 `test_golden_frozen_lines`, which mutates frozen golden bytes while monkeypatching the hash and gets exactly `failure_reason: golden: normalized runs differ from the frozen golden.jsonl`. The *regen path* has changed purpose: T:2074 now proves the set REAL sha pin rejects synthetic regenerated bytes; it does NOT exercise a multi-async sort case, as M8 demonstrates.

## V7 — doubled `observed` prefix (FOLLOW-UP)

Producer chain: `negative_contract.validate_negative_dir` returns `observed: error code=…`; `check_negative` wraps it at C:1556 as `observed: {observed}`; `_check_bundle_uncapped` then formats `negative: {neg_observed}` at C:1876. Thus the PASS line is mechanically `negative: observed: observed: error code=-32602 message=Invalid params`.

Consumers: `scripts/proof-runner` only matches the spec's `expected_reason = leg["expect"]["failure_reason"]` by a per-line substring on stdout+stderr (runner:193-203); it does NOT consume the PASS line. `proofs/S0-01/spec.json` specifies no PASS-text matcher. The ledger stores only command, exit, stdout/stderr SHA256, and the negative leg's classified failure reason; it does NOT parse that prose. Tests T:552-556 pin the whole current PASS line, so a text cleanup would require a test update but cannot affect protocol evidence, mint attestation, or ledger state.

Classification: FOLLOW-UP / `verify-followup` (D-034), not a blocker: no frozen S0-01 criterion requires a single prefix, and the exact expected negative classification is separately bound by spec.json and `assert r.stdout.splitlines() == [...]` at S:141-144. Suggested repair (out of scope): make `check_negative` return the raw `observed` from the validator rather than prepending it again, then update the exact PASS-line test.

## V2 — seed intent (FOLLOW-UP: documentation decision, not a blocker)

Seed S0-01's `fixture_format:` at seed:347-350 says `normalized-then-golden transcript compare (declared minimal volatile-field list), run twice byte-identical`. It does not literally say that raw transcript order must be preserved; the current normalizer's declared exception defines `ASYNC_SESSION_UPDATES` as the closed tuple `("session_info_update",)` and moves that record after the session/new response (pins.py:130-145; `sync = [norm(entry) for entry in entries if not is_async(entry)]` at C:868-886). Therefore owner decision (a) satisfies the seed's high-level words **only if the decision record is treated as the declared normalization rule**.

The decision is in the authoritative incident/brief evidence (AF-AP-107; G1 specification, pc-vb-f12-g1.md:22-40; tests' decision-a docstrings), but NOT in `tasks/stage0-breakdown.md` (it remains at the older general phrase, line 21) or `docs/08_DECISION_LOG.md` (no D-row for decision (a)). This is a precise stale-context/documentation finding. It does not contradict an executable seed assertion, does not affect the minted evidence, and is outside the checker/test component boundary. Disposition: FOLLOW-UP / `verify-followup`; recommend a decision-log or breakdown amendment that names the closed order-free `session_info_update` exception and its count/payload binding.

## V9 — additional observation

No other in-boundary production defect found beyond F1. `build_capture_record.py --check proofs/S0-01/evidence/golden/run-1 run-1` → `run-1: capture.json matches (--check)` / rc=0. The real checker CLI, proof-runner, ledger integrity, bundle manifests, and attested output digests reproduce as recorded above.

## Clean final-byte gates (SOLID)

- `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/bt/final1 tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py` → `476 passed in 79.05s (0:01:19)` / rc=0.
- Same command with `final2` → `476 passed in 82.16s (0:01:22)` / rc=0.
- `scripts/test_summary.sh tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py` → `pytest-summary: 476 passed in 343.93s (0:05:43)` / rc=0 (the only authoritative summary count).
- `python -m pyflakes proofs/S0-01/check_acp_conformance.py proofs/S0-01/pins.py tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py` → rc=0; `git diff --check` → rc=0.

## Finding inventory

1. **BLOCKER F1 — V5 controls do not kill widened closed-set and missing-sort production mutants.** Evidence SOLID. Contract mapping: exact closed tuple/sorted canonicalization. Canonical path: real CLI scratch copies. Material: M4 accepts forbidden `tool_call` reordering; M8 rejects valid multiple-async order-free captures. Concrete discriminator: M4/M8 commands/outcomes in V5. In boundary: normalizer + its tests. Suggested fix: repair the adjacent-swap expressions to end `entries[idx+2:]`; add a two-distinct-async opposite-order real-checker regression; rerun mutation audit. **Blocks.**
2. **FOLLOW-UP F2 — doubled `negative: observed: observed:` prefix.** Evidence SOLID. Contract mapping: none beyond readability. Canonical path: `def check_negative` at C:1536-1556 and `f"sha256 {golden_sha_12}); negative: {neg_observed}")` at C:1876. Material effect: none on state/evidence/consumer. Suggested fix: remove the second prefix in a future focused round. Does not block.
3. **FOLLOW-UP F3 — decision (a) lacks a durable D-row/breakdown amendment.** Evidence SOLID. Contract mapping: seed's declared-normalization wording; the owner decision has been made but the cross-reference is stale. Canonical path: N/A (documentation only). Material effect: future maintenance ambiguity, not current checker behavior. Suggested fix: document the closed exception in the decision log/breakdown. Does not block.

## DISCREPANCIES

1. The initial direct xdist command failed before collection because `rm -rf ../scratch/bt/final1` also removed the parent `../scratch/bt`; pytest creates only its final component and returned `FileNotFoundError .../scratch/bt/final1`. Re-created the parent (`mkdir -p ../scratch/bt`) and both final xdist gates passed. Tooling/fixture setup issue only; no source behavior changed.
2. The brief's C6(i) literal mutation (move a chunk before `session/prompt`) is structurally rejected by `check_prompt_turn` before `check_golden`, as G1 reported. I used the nearest protocol-valid chunk/usage adjacent swap; it reached the golden checker and failed at normalized line 8.
3. report_lint final bounded result: report_lint: 38 refs — OK 36, NEAR 2, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree).

## NOT-done

- No repair was made. This lane is read-only; F1 requires a new focused build/repair increment and independent re-verification.
- No live captures or relay/model/server action was performed. All attacks used fresh scratch copies.
- No decision-log/breakdown amendment was made; F3 is a coordinator follow-up.
- The local route cannot independently self-accept. This report is a recommendation only.

## GATE RECOMMENDATION

`NOT-READY` — F1 satisfies the complete blocking predicate (frozen closed-set/sort contract; real production CLI reproduction; material accept/reject behavior; deterministic mutants; normalizer/test boundary). F2/F3 are non-blocking verify-followups. Coordinator owns the final gate decision.

retro: found a real test-oracle defect (duplicated-neighbour “swap” makes closed-set tests hollow) — coordinator must register the bug-echo/incident entry before repair closes.

🌱 graft saved ~34,247 tokens this turn.


