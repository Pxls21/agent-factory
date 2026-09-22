# VERIFY-G2 report — targeted re-verification of the G2 repair (VERIFY-VB-F12 F1)

PIN: f84265f · lane: pc-verify-g2.md--f84265f · role: adversarial-verifier (local Qwen, xhigh)  
Gate env (every run): S0_01_VENUE=pc, S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden, S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz; /home/rocco/venv-agent-factory/bin first on PATH; scratch = ../scratch.  
Verified live: the focused F1 repair's frozen M1-M8 audit is killed by named tests and final gates reproduce; gate recommendation is `MERGE-READY-WITH-FOLLOWUPS` (F1 future hardening; F2 predecessor-evidence clarification), not a final decision.  
Report timestamp (UTC): `2026-09-22T02:17:54Z`.

## Item 1 — premise (SOLID)

Command: `git diff --stat 955ab74 f84265f -- proofs/ tests/test_s0_01_spec_runner.py scripts/proof-runner scripts/validate-ledger` → EMPTY (no output, rc=0). P, the runner, validate-ledger and the whole evidence tree (including the golden) are byte-identical to the verified PIN.

Command: `git diff --stat 955ab74 f84265f -- tests/` → exactly:

```
 tests/test_s0_01_check_acp_conformance.py | 100 +++++++++++++++++++++++++++++-
 1 file changed, 98 insertions(+), 2 deletions(-)
```

Only T is named under tests/. The full 955ab74..f84265f path list (`git diff --name-status`) shows the rest are docs/skills/briefs/transcripts/todo (the D-035 + issue #9 + G2-brief plane) — outside the premise set. Final file identity also matches the G2 report: T=a71f6c44fc9d9c050448c1223d0bbfbd4143a4951a011f307d2288ba2d8401d1; C=868b8705699b5e78b1468252ecbdec93736d2a7e2f4819424311c31c243db46a; P=1a2f9a38ddba14e3ea75c06e77e43083a059e8dc5caf5499c7e54e9013921981; golden=6225adb8ecc21a24d578696e2b9c25c81ebd5a82068c4411f780930c2fa54221; S=9e1dfc609d8f42454d49aa64ae131966ddf8ee627ceef9e420303b9d3e3fa627. `git diff --quiet 85836a5 -- proofs/S0-01/` and the S check both returned rc=0. Premise HOLDS: this targeted round is valid. SOLID. Not blocking (it is the gate on the round itself).

## Item 2 — the controls are TRUE swaps; M1 and M4 die at the normalized-output assertion (SOLID)

**True-swap analysis (T:2010-2038, T:2042-2068).** Both repaired controls now build `moved` as  
`entries[:idx] + entries[idx+1:idx+2] + entries[idx:idx+1] + entries[idx+2:]` (the real source lines are T:2023-2026 (`moved = (entries[:chunk_idx]` through `+ entries[chunk_idx + 2:])`) and `moved = tc[:idx9] + tc[idx9 + 1:idx9 + 2] + tc[idx9:idx9 + 1] + tc[idx9 + 2:]` at T:2057).

That is exactly `entries[:idx] + [entries[idx+1], entries[idx]] + entries[idx+2:]`: a genuine adjacent swap. The chosen entry and its neighbour exchange positions, and the tail is taken once. The old form used `entries[idx+1:]`, re-emitting the neighbour and producing a 12-entry duplicate list.

**Important qualification.** The source formula proves the current control is an adjacent swap. The three generic self-checks do not independently prove adjacency: another permutation can preserve length, multiset, and changed-order.

A scratch non-adjacent permutation passed those three generic checks. With a carefully selected hostile reordering plus the widened M1 or M4 production mutation, the individual named control passed (`1 passed in 0.48s` for each). This is a future test-regression hardening observation, not a current contract defect: the current source formulas use the required `idx + 2` tail, and their current M1/M4 mutations fail at the normalized-output assertions.

**M1.** Scratch P mutation:

```
ASYNC_SESSION_UPDATES = ("session_info_update", "agent_message_chunk")
```

Named control: `test_golden_synchronous_frame_order_still_binds`.

```
E       AssertionError: moving the SYNCHRONOUS agent_message_chunk did not change the output — the control is a tautology.
tests/test_s0_01_check_acp_conformance.py:2035: AssertionError (`assert n_orig != n_moved`)
1 failed in 0.99s
```

Fails at T:2035, not at a self-check. SOLID.

**M4.** Scratch P mutation:

```
ASYNC_SESSION_UPDATES = ("session_info_update", "tool_call")
```

Named control: `test_golden_async_set_is_closed`.

```
E       AssertionError: moving a NON-async (tool_call) session/update did not change the output — the async set is not closed.
tests/test_s0_01_check_acp_conformance.py:2066: AssertionError (`assert n_orig != n_moved`)
1 failed in 1.24s
```

Fails at T:2066, not at a self-check. SOLID.

**Blocking?** No. The current direct source formulas are true swaps and current M1/M4 mutations die. The hostile permutations mutate T itself and are a hardening follow-up, not a defect reproducing on the current implementation.

## Item 3 — canonical discriminators on the new T (SOLID)

Rebuilt the V5 canonical discriminators in fresh scratch archives of f84265f with unmodified C/P/golden, generated golden/pin with the correct checker, and executed the real CLI.

**M4.** Converted `usage_update` to `tool_call` in both runs; moved run-2 tool_call after terminal and re-stamped its time.

* Correct checker, regenerated correct-code golden:  
  `rc=1 failure_reason: golden: golden mismatch between run-1 and run-2 at normalized line 6`
* Widened M4 checker against that correct-code golden:  
  `rc=1 failure_reason: golden: normalized runs differ from the frozen golden.jsonl`

The latter differs from V5’s reported widened-checker PASS. See F2/D2.

**M8.** Built two distinct `session_info_update` records A/B, B containing non-volatile `subtitle`; placed A,B and B,A in opposite raw orders across the two legs. Their raw locations remained valid. The normalizer re-homes both to the session-new intro slot.

* Correct checker:  
  `rc=0 PASS ... golden x2 identical (12 normalized lines, sha256 c4aa0ff991db)`
* M8 checker with C:880 sort removed:  
  `rc=1 failure_reason: golden: golden mismatch between run-1 and run-2 at normalized line 4`

**Why line 6 vs line 7.**

* The real canonical M4 construction uses committed evidence and reports line 6.
* The synthetic G2 test fixture reports line 7. I independently ran the exact T:2121-2152 construction: after the swap, the first difference is tool_call vs agent_message_chunk at normalized index 7.
* The two cases have different fixture shapes, so both values are correct for their respective construction.

**New-test mutation kills.**

* M4 by `test_golden_non_async_kind_order_binds_through_check_golden`: widened M4 causes `with pytest.raises(...)` at T:2149 to fail with `Failed: DID NOT RAISE Failure`; `1 failed in 2.47s`.
* M8 by `test_golden_two_async_records_in_opposite_raw_orders_normalize_identically`: removing the sort fails `assert expected == cc.normalize_timeline(raw_ba)` at T:2094; `1 failed in 1.90s`.

SOLID. No blocker.

## Item 4 — new tests are gates, not mirrors (SOLID)

**(a) `check_golden` mismatch path.** C:1562-1564 computes and raises the normalized mismatch. On a scratch C copy, I changed that branch into `if False: pass`.

* `test_golden_non_async_kind_order_binds_through_check_golden` died: `Failed: DID NOT RAISE Failure` at T:2149.
* `test_golden_two_async_records_in_opposite_raw_orders_normalize_identically` passed, as expected, because it constructs a valid n1==n2 pair.

Thus the M4 test exercises the real mismatch raise. The M8 test separately exercises the valid `check_golden` return path.

**(b) pin bypass is deliberate.** The new tests monkeypatch `PINNED_GOLDEN_SHA256` only for regenerated fixture goldens. Independent pin gates remain:

* `test_cli_pass_path_fails_on_golden_pin`, T:568-T:580: subprocess sees the real pin and rejects a synthetic golden.
* `test_golden_regen`, T:2170-T:2189: regenerated synthetic golden fails against the real pin.
* `test_golden_frozen_lines`, T:1872-T:1882: monkeypatches the changed sha specifically to reach and validate the frozen-lines check at C:1577.

**(c) subtitle discriminator.** C:104 makes `title` volatile; C:787 drops volatile keys. `subtitle` survives. Changing record B’s `subtitle` to `title` made:

```
E       AssertionError: the two async records do not have distinct normalized lines
1 failed in 1.79s
```

at T:2091. The G2 use of `subtitle`, rather than the brief’s suggested `title`, is correct and required.

## Item 5 — full M1–M8 audit (SOLID)

Fresh archive per mutant; final T copied in. Pristine new focused tests first passed: `2 passed in 1.89s`.

| Mutant | Named killer | Measured result |
|---|---|---|
| M1: widen async set with `agent_message_chunk` | `test_golden_synchronous_frame_order_still_binds` | T:2035, `1 failed in 0.52s` |
| M2: slot async at end | `test_golden_async_notification_is_order_free` | T:1966, `1 failed in 0.56s` |
| M3: include async in pass 1 | `test_golden_async_placement_is_independent_of_the_session_new_response` | T:1997, `1 failed in 0.50s` |
| M4: widen async set with `tool_call` | `test_golden_non_async_kind_order_binds_through_check_golden` | T:2149, `1 failed in 1.94s` |
| M5: skip real-pin check | `test_golden_regen` | T:2188, `1 failed in 4.70s` |
| M6: force `check_bundle` failure | `test_committed_bundle_runner_mints_a_result` | `1 failed in 0.39s` |
| M7: delete `golden/negative` | `test_committed_negative_leg_cmd_reports_the_protocol_violation` | `1 failed in 0.28s` |
| M8: remove async-line sort | `test_golden_two_async_records_in_opposite_raw_orders_normalize_identically` | T:2094, `1 failed in 1.94s` |

M4 and M8 die by the new focused tests, not `test_real_bundle_passes_every_check`. No survivor in the frozen M1-M8 table.

## Item 6 — final-byte gates (SOLID)

Three direct xdist runs:

```
478 passed in 80.38s (0:01:20)
478 passed in 84.95s (0:01:24)
478 passed in 84.98s (0:01:24)
```

Authoritative count command:

```
478 passed in 351.11s (0:05:51)
pytest-exit: 0
pytest-summary: 478 passed in 351.11s (0:05:51)
```

Other gates:

* `python -m pyflakes tests/test_s0_01_check_acp_conformance.py` → rc=0.
* AP screen → exactly four known pre-existing hits at T:88, T:90, T:5590, T:6147; no new in-hunk hit.
* `sha256sum tests/test_s0_01_check_acp_conformance.py`:

```
a71f6c44fc9d9c050448c1223d0bbfbd4143a4951a011f307d2288ba2d8401d1
```

* `git diff --check` → rc=0.

## Item 7 — bounded hunk review

### FOLLOW-UP F1 — generic self-checks do not independently certify exact adjacency

**Evidence:** solid scratch future-regression probe. A non-adjacent mutation to T can retain the generic length/multiset/changed-order checks while a named control passes under widened M1/M4.

**Why it does not block:**

1. The frozen requirement explicitly requires the `i+2` source formula plus those three generic checks. Current T has all of them.
2. Current M1/M4 mutations against current T fail.
3. The surviving cases require changing T itself, so they do not reproduce as a present production-path defect.
4. The hostile M4 full suite still had `1 failed, 477 passed`: the other new M4 checker-path test catches the mutant.

Suggested future hardening: assert unchanged prefix/tail and exact pair exchange:

```
moved[idx:idx + 2] == [entries[idx + 1], entries[idx]]
```

Scratch testing showed that assertion turns both hostile permutations red.

### FOLLOW-UP F2 / D2 — V5 widened-M4 PASS claim differs from clean reconstruction

A clean `python3 -B` reconstruction found:

* Correct-code golden + correct checker → line-6 mismatch.
* Correct-code golden + widened M4 → frozen-lines mismatch.
* Widened-code golden + widened M4 → PASS.

Thus V5’s stated widened-M4 PASS does not reproduce from its written “correct code” golden description. This is predecessor-report evidence clarification, not a G2 behavior defect.

## Finding inventory

1. **FOLLOW-UP F1:** generic checks do not independently prove adjacency. No current material effect; requires a future T mutation. Does not block.
2. **FOLLOW-UP F2:** predecessor V5 M4 canonical PASS narrative does not reproduce under a clean correct-code-golden reconstruction. Does not block.
3. **INFO:** `subtitle` is correctly used instead of volatile `title`.
4. **INFO:** final suite, hash, pyflakes, AP screen, and whitespace gates reproduce cleanly.

## NOT-done

* No source repair made.
* No evidence, golden, pin, checker, corpus, runner, ledger, model, relay, or service changed.
* V1-V4/V6-V8, mint, capture, runner/ledger, corpus, and adjacent components were not re-run by design.
* No commit, push, add, checkout, reset, or stash.
* Report artifact: `tasks/briefs/s0-01-vb-f12-support/VERIFY-G2-report.md`.

## GATE RECOMMENDATION

`MERGE-READY-WITH-FOLLOWUPS` — no finding satisfies the complete blocking predicate.

The frozen G2 repair is reproduced: true `i+2` swaps, all standard M1-M8 mutants killed by named tests, M4/M8 focused new-test kills, canonical real-CLI M4/M8 discriminators, three 478-pass final suites, pyflakes, AP screen, and final-T hash are solid.

F1 is future hardening only. F2 is predecessor-evidence clarification. The coordinator owns the final decision.

## Report-lint bounded result

* Initial scan: `99 refs — OK 44, NEAR 3, MISS 30, UNCHECKABLE 22, UNRESOLVED 0`.
* Cleanup pass 1: `104 refs — OK 61, NEAR 5, MISS 18, UNCHECKABLE 20, UNRESOLVED 0`.
* Cleanup pass 2: `107 refs — OK 82, NEAR 3, MISS 12, UNCHECKABLE 10, UNRESOLVED 0`.
* Cleanup pass 3: `107 refs — OK 89, NEAR 3, MISS 5, UNCHECKABLE 10, UNRESOLVED 0`.

The remaining five misses are line-wrap/adjacent-reference heuristic artifacts; no unresolved reference remains.
