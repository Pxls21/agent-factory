# VB-F12-G2 report — repair round for VERIFY-VB-F12 F1

PIN: 85836a5 · lane: pc-vb-f12-g2.md--85836a5 · role: code-implementer (local Qwen build route)
Scope: T only. C/P/golden/S and all other files byte-identical to the PIN. This is a proposal; the coordinator and targeted adversarial re-verify own the verdict.

## FILE IDENTITY

- T = `tests/test_s0_01_check_acp_conformance.py`: `a71f6c44fc9d9c050448c1223d0bbfbd4143a4951a011f307d2288ba2d8401d1` (PIN: `a09e96ad4ab7741891ab5c28bf17ae01989a09c9de2c521e75416098e4670935`).
- C = `proofs/S0-01/check_acp_conformance.py`: `868b8705699b5e78b1468252ecbdec93736d2a7e2f4819424311c31c243db46a`, byte-identical to PIN.
- P = `proofs/S0-01/pins.py`: `1a2f9a38ddba14e3ea75c06e77e43083a059e8dc5caf5499c7e54e9013921981`, byte-identical to PIN.
- Golden = `proofs/S0-01/evidence/golden/golden.jsonl`: `6225adb8ecc21a24d578696e2b9c25c81ebd5a82068c4411f780930c2fa54221`, byte-identical to PIN.
- S = `tests/test_s0_01_spec_runner.py`: `9e1dfc609d8f42454d49aa64ae131966ddf8ee627ceef9e420303b9d3e3fa627`, byte-identical to PIN.
- `git status --porcelain`: ` M tests/test_s0_01_check_acp_conformance.py` and `?? tasks/briefs/s0-01-vb-f12-support/G2-report.md`; exactly T plus this report.

## CHANGE

- T:2010-2038 repairs the synchronous control to a true adjacent swap ending at `entries[chunk_idx + 2:]`, then self-verifies length, multiset, and changed order before asserting the normalized effect.
- T:2042-2068 applies the same repair and three self-verifying assertions to the closed-async-set `tool_call` control.
- T:2071-2118 adds `_golden_async_pair` and `test_golden_two_async_records_in_opposite_raw_orders_normalize_identically`. The test first proves records A/B have distinct normalized lines, then proves A,B and B,A normalize identically, and finally builds two fixture legs, re-syncs timeline/split files plus tee status, pins regenerated run-1 bytes, and requires `check_golden` to return the canonical 12-line result.
- T:2121-2152 adds `test_golden_non_async_kind_order_binds_through_check_golden`. Both fixture legs convert the first `usage_update` to `tool_call`; run-2 alone true-swaps it with its neighbor; regenerated run-1 golden bytes are pinned; `check_golden` must raise exactly `golden mismatch between run-1 and run-2 at normalized line 7`.

## RED-FIRST

### Item 1: duplicated-neighbor controls

Command: `python -m pytest -q -p no:cacheprovider --basetemp ../scratch/bt/red-length T::test_golden_synchronous_frame_order_still_binds T::test_golden_async_set_is_closed`, after adding length assertions but before fixing either final slice.

- T:2027 `len(moved)`: `E       AssertionError: adjacent swap changed entry count: 12 != 11`
- T:2058 `len(moved)`: `E       AssertionError: adjacent swap changed entry count: 12 != 11`
- Summary: `2 failed in 0.67s` / rc 1.

The new assertion rejected the duplicated neighbor before either normalized-output assertion ran.

### Item 2: M8 sort deletion

Scratch mutation only: removed C:880 `async_lines.sort(key=lambda item: item[1])`.

Named test: `test_golden_two_async_records_in_opposite_raw_orders_normalize_identically`.

- `E       AssertionError: opposite raw orders changed the normalized async multiset`
- First difference: normalized index 4.
- Summary: `1 failed in 1.94s` / rc 1.

### Item 3: M4 widened set

Scratch mutation only: widened P:138 to `ASYNC_SESSION_UPDATES = ("session_info_update", "tool_call")`.

Named test: `test_golden_non_async_kind_order_binds_through_check_golden`.

- `E               Failed: DID NOT RAISE Failure`
- Summary: `1 failed in 1.87s` / rc 1.

Correct tree after the tests landed: `4 passed in 1.90s` for both repaired controls and both new checker-path tests.

## M1-M8 MUTATION AUDIT

Every mutant was made in a fresh scratch archive of PIN 85836a5 with final T copied in. The tracked tree, real corpus, verifier tree, and servers were not mutated.

| mutant | named killer | failing assertion line | result |
|---|---|---|---|
| M1 — widen P:138 `ASYNC_SESSION_UPDATES` with `agent_message_chunk` | `test_golden_synchronous_frame_order_still_binds` | `E       AssertionError: moving the SYNCHRONOUS agent_message_chunk did not change the output — the control is a tautology.` | `1 failed in 0.55s` |
| M2 — C:879 `async_lines.append` slots every async line at end | `test_golden_async_notification_is_order_free` | `E       AssertionError: last normalized line is not the end_turn terminal: {..."session_info_update"...}` | `1 failed in 0.55s` |
| M3 — C:868 `sync` includes async records in pass 1 | `test_golden_async_placement_is_independent_of_the_session_new_response` | `E       AssertionError: async notification before the session/new response changed the output` | `1 failed in 0.51s` |
| M4 — widen P:138 `ASYNC_SESSION_UPDATES` with `tool_call` | `test_golden_non_async_kind_order_binds_through_check_golden` | `E               Failed: DID NOT RAISE Failure` | `1 failed in 1.79s` |
| M5 — skip C:1570 `PINNED_GOLDEN_SHA256` guard | `test_golden_regen` | `E       assert 0 == 1` | `1 failed in 4.72s` |
| M6 — force C:1694 `check_bundle` to raise | `test_committed_bundle_runner_mints_a_result` | `E       AssertionError: expected exit 0, got 1: stdout='' stderr='leg-exit-mismatch: S0-01 positive expected 0 got 1\n'` | `1 failed in 0.47s` |
| M7 — delete `golden/negative` | `test_committed_negative_leg_cmd_reports_the_protocol_violation` | `E       AssertionError: expected exit 1, got 2: 'deferred: negative probe not captured\n'` | `1 failed in 0.29s` |
| M8 — remove C:880 `async_lines.sort` | `test_golden_two_async_records_in_opposite_raw_orders_normalize_identically` | `E       AssertionError: opposite raw orders changed the normalized async multiset` | `1 failed in 1.90s` |

M4 and M8 are killed by the new focused tests, not by `test_real_bundle_passes_every_check`.

## DE-VACUOUS ASSERTION MUTATIONS

All mutations below ran on scratch copies and were restored.

- Item 1 length: changed expected `len(entries)` by one to `len(entries) - 1` while restoring the original malformed slice. Own line failed: `E       AssertionError: adjacent swap changed entry count: 12 != 11`; `1 failed in 0.55s`.
- Item 1 multiset: changed expected source to `entries[:-1]`. Own line failed: `E       AssertionError: adjacent swap changed the entry multiset`; `1 failed in 0.53s`.
- Item 1 ordering: changed `moved != entries` to `moved == entries`. Own line failed: `E       AssertionError: adjacent swap did not change the entry order`; `1 failed in 0.52s`.
- Item 2 distinctness: changed `normalized_a != normalized_b` to `==`. Own line failed: `E       AssertionError: the two async records do not have distinct normalized lines`; `1 failed in 1.97s`.
- Item 2 checker result: changed expected list to `expected[:-1]`. Own line failed: `E       AssertionError: check_golden did not return the canonical two-async timeline`; `1 failed in 1.83s`.
- Item 3 diagnostic: changed expected normalized line `7` to `8`. The own `pytest.raises(match=...)` assertion failed, showing actual `ized line 7` versus expected `ized line 8`; `1 failed in 1.98s`.

## FINAL GATES

Environment for pytest: `PATH=/home/rocco/venv-agent-factory/bin:$PATH`, `S0_01_VENUE=pc`, `S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`, `S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`.

Run 1:

`478 passed in 77.38s (0:01:17)`

Run 2, identical final T bytes:

`478 passed in 78.41s (0:01:18)`

Other gates:

- `pyflakes rc=0`
- `git diff --check rc=0`
- `git diff --quiet 85836a5 -- proofs/S0-01/ rc=0`
- `a71f6c44fc9d9c050448c1223d0bbfbd4143a4951a011f307d2288ba2d8401d1  tests/test_s0_01_check_acp_conformance.py`
- AP screen final line (`call_count`), verbatim: `    tests/test_s0_01_check_acp_conformance.py:5590: if call_count[0] == 2:`
- Full AP screen summary: `--- TEST_SCREEN over 1 path(s): 4 hits over 1 files ---`; AP-66 at T:88 `nv._point_mul`, T:90 `nv._point_mul`; AF-AP-48 at T:6147 `assert all`; AF-AP-57 at T:5590 `call_count`. All are pre-existing, outside the changed hunks, and unchanged from the PIN.
- Final code-intel pack: `../scratch/g2-pack.md`, 300 lines. Its ripwire test-gate line reports `changed="1" impacted="0" tests="0" untested="0"`; it maps each new test symbol. GitNexus and code-review-graph were unmapped inside the pack; the direct clone GitNexus `detect-changes` result was `Changes: 1 files, 8 symbols`, `Affected processes: 0`, `Risk level: low`.

## SELF-ATTACK

1. Risk: A/B differ only in values, so the shape normalizer makes sort a no-op. Ruled out at T:2090-2092 by `normalized_b`: the test compares their normalized lines directly. The `subtitle` key exists only in B, so the key sets differ and M8 dies at normalized index 4.
2. Risk: the checker-path tests only exercise `normalize_timeline`, not `check_golden`. Ruled out at T:2117-2118 and T:2148-2152: the M8 path asserts `check_golden` returns the regenerated canonical list; the M4 path requires its exact line-7 `Failure`.
3. Risk: timeline edits fail earlier due to stale seq/split/tee artifacts. Ruled out by the green `check_golden` call for M8, the exact golden mismatch from M4, and the two final 478-test runs. Both new fixture tests renumber seq and call `_write_timeline` plus `_write_tee_status`.

## DISCREPANCIES

- The brief suggested adding `title` as B's extra key. C:104-105 defines `title` as volatile; `_shape` removes it, so A/B would normalize identically and sorting would be a no-op. T:2076 uses `subtitle`, a non-volatile extra key, preserving the brief's different-key-set requirement. Direct probe: `title` produced the original normalized line; `subtitle` produced `"subtitle":"str"`.
- The brief calls for M4's exact checker message with normalized line `N`; measured N is **7** on the fixture. The previous canonical real-evidence report measured line 6 on a different construction. This test pins the fixture's exact zero-based diagnostic.
- Initial final pack command passed multiple symbols after one `-s`; `lane_context.sh` treated later symbols as file paths and returned rc 64. Re-run with one `-s` per symbol succeeded: `lane_context: pack written to ../scratch/g2-pack.md (300 lines)`.
- Direct `ripwire edit-check` by file path was ambiguous because old report packs define the same path contract; the final lane pack supplied per-symbol ripwire callers and the test-gate instead.
- `report_lint` final bounded result: `report_lint: 25 refs — OK 25, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## NOT-done

- No production checker, pins, evidence, spec-runner, corpus, model, relay, service, ledger, wiki, or incident-log changes were made.
- No git write, commit, push, checkout, reset, stash, or outward-facing action was performed.
- This build lane did not self-accept. The coordinator must run the targeted adversarial re-verify and grade this proposal.

## GATE RECOMMENDATION

`MERGE-READY` proposal for the focused F1 repair: true swap controls are self-verifying, all M1-M8 mutants are killed by named tests, M4/M8 die through the new focused paths, and the two required final suites passed with 478 tests each. Coordinator and targeted verifier own the verdict.

retro: the brief's `title` discriminator conflicted with the production volatile-field set; recorded above as a concrete discrepancy. No general skill update is needed. The hollow-green class was already registered as AF-AP-109.

🌱 graft saved ~89,803 tokens this turn.
