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
`entries[:idx] + entries[idx+1:idx+2] + entries[idx:idx+1] + entries[idx+2:]` (the real source lines are
T:2023-2026 (`moved = (entries[:chunk_idx]` through `+ entries[chunk_idx + 2:])`) and
`moved = tc[:idx9] + tc[idx9 + 1:idx9 + 2] + tc[idx9:idx9 + 1] + tc[idx9 + 2:]` at T:2057).
That is exactly `entries[:idx] + [entries[idx+1], entries[idx]] + entries[idx+2:]` — a genuine adjacent
swap: the moved entry `entries[idx]` and its neighbour `entries[idx+1]` exchange positions, and the
tail `entries[idx+2:]` is taken once. The old defect was `... + entries[idx+1:]` (T at 955ab74), which
re-emitted the neighbour a second time (a 12-entry list, a duplicate, not a swap).

**Important qualification:** the *source formula* proves the current control is an exact adjacent swap, but
the three added self-checks (`assert len(moved) == len(entries)` at T:2027 / `len(tc)` at T:2058;
`assert sorted(json.dumps(e, sort_keys=True) for e in moved) == sorted(json.dumps(e, sort_keys=True) for e in entries)`
at T:2029-2031; / `assert sorted(json.dumps(e, sort_keys=True) for e in moved) == sorted(json.dumps(e, sort_keys=True) for e in tc)`
at T:2060-2062;
`assert moved != entries` at T:2032 / `assert moved != tc` at T:2063) do NOT prove adjacency by themselves. They reject additions/deletions/duplicates/identity,
but any changed permutation satisfies them. Scratch mutation: changed each formula into a non-adjacent
three-item rotation (`[:idx] + [idx+1:idx+3] + [idx] + [idx+3:]`) while retaining the relevant production
widening (M1 or M4). Both named tests passed the three self-checks and reached the normalized-output assertion:
M1 then failed at `assert n_orig != n_moved` (T:2035; `moving the SYNCHRONOUS agent_message_chunk did not
change the output`), `1 failed in 0.59s`; M4 then failed at `assert n_orig != n_moved` (T:2066; `moving a
NON-async (tool_call) session/update did not change the output`), `1 failed in 0.57s`. Thus, **YES**, something other than a true adjacent swap can satisfy the three checks.
This means “self-verifying” is narrower than “mathematically certifies adjacency.” A more hostile scratch
mutation then showed a FUTURE non-adjacent test-code change could make the named controls pass: with M1 widened,
a 3-item rotation `[chunk,usage,terminal] -> [terminal,usage,chunk]` gives `1 passed in 0.48s`; with M4 widened,
a 4-item rotation gives `1 passed in 0.48s`. In both cases length/multiset/order self-checks remain green while
the same widened-set mutant survives.

This is a meaningful hardening observation, but it is NOT a current contract failure. The direct source formulas
use the required `idx + 2` tail and are true adjacent swaps; the three exact required invariants are present; the
current M1/M4 production mutants die at their normalized-output assertions. The frozen brief does not require
the three generic invariants ALONE to prove adjacency under a hypothetical later change to the test formula.
The normalized assertions `assert n_orig != n_moved` (T:2035/T:2066) test the current source permutation against
`normalize_timeline`, not arbitrary future permutations. Disposition: FOLLOW-UP F1 (structural pair assertion
would make the claim stronger), not a blocker.

**M1 — widen `ASYNC_SESSION_UPDATES` with `agent_message_chunk` through the CONTROL.** Scratch copy of P
mutated to `ASYNC_SESSION_UPDATES = ("session_info_update", "agent_message_chunk")`; named control
`test_golden_synchronous_frame_order_still_binds` run on the real run-1 timeline via the in-process
`cc.normalize_timeline` (final T). Command: `python -m pytest -q -p no:cacheprovider --basetemp
../scratch/bt tests/test_s0_01_check_acp_conformance.py::test_golden_synchronous_frame_order_still_binds`
on the scratch tree. Output:

```
E       AssertionError: moving the SYNCHRONOUS agent_message_chunk did not change the output — the control is a tautology.
tests/test_s0_01_check_acp_conformance.py:2035: AssertionError (`assert n_orig != n_moved`)
1 failed in 0.99s
```

Fails at T:2035 (`assert n_orig != n_moved`) — the normalized-output assertion — NOT at a self-check (the
length/multiset/order `assert` self-checks at T:2027-2032 pass, because it is a true swap). SOLID.

**M4 — widen `ASYNC_SESSION_UPDATES` with `tool_call` through the CONTROL.** Scratch copy of P mutated to
`ASYNC_SESSION_UPDATES = ("session_info_update", "tool_call")`; named control `test_golden_async_set_is_closed`
(the real run-1 usage_update converted to tool_call, then swapped). Same command form. Output:

```
E       AssertionError: moving a NON-async (tool_call) session/update did not change the output — the async set is not closed.
tests/test_s0_01_check_acp_conformance.py:2066: AssertionError (`assert n_orig != n_moved`)
1 failed in 1.24s
```

Fails at T:2066 (`assert n_orig != n_moved`) — the normalized-output assertion — NOT at a self-check. SOLID.

**Blocking (item 2)? No.** The direct source formulas are true swaps and their M1/M4 mutations die at the
desired normalized-output assertions. The hostile non-adjacent permutations are mutations of T itself, not the
current repair; they demonstrate a hardening opportunity but do not contradict the frozen requirement (which
specifies `i+2` and exactly the three checks, all present). See FOLLOW-UP F1 in item 7.

## Item 3 — the canonical discriminators (M4, M8) re-run on the NEW T's tree (SOLID)

Rebuilt the two canonical discriminators from VERIFY-VB-F12 §V5 ("Canonical discriminators for the two
full-suite survivors", lines 77-78) — the `../scratch/canonical-mutants/run.py` was gone, so I rebuilt them
fresh on a scratch copy of the PIN tree (archive f84265f, un-mutated C/P/golden), mutating the REAL committed
evidence, regenerating golden+pin with the CORRECT checker code, and running the REAL CLI.

**(M4)** converted `usage_update` -> `tool_call` in BOTH runs and moved run-2's tool_call after the terminal
(re-stamped valid). Corrected checker regenerated golden (11 lines, sha256 048b753bdba9...). Real CLI:
- (a) corrected checker on the M4 evidence: **rc=1 `failure_reason: golden: golden mismatch between run-1 and run-2 at normalized line 6`** — unchanged from V5 (which measured line 6). The real CLI's verdict on the correct C is unchanged.
- (b) widened M4 checker (`ASYNC_SESSION_UPDATES` += `tool_call`), same evidence: **rc=1 `failure_reason: golden: normalized runs differ from the frozen golden.jsonl`**. (V5 reported the widened checker as `rc=0 PASS`. My measurement differs — see DISCREPANCIES D2 for the mechanism and why it does not weaken the conclusion.)

**(M8)** two distinct valid `session_info_update` records A/B (B adds `subtitle`, a non-volatile key that survives
`_shape`) in OPPOSITE raw orders across run-1 (A,B) / run-2 (B,A), both keeping the original sessionId (same
intro slot, so the sort is observable). Each pair replaces the real async record at its original raw position
(run-1 after prompt; run-2 after terminal); `normalize_timeline` then re-homes both to the pre-prompt session-new
intro slot, preserving raw capture validity while making the sort observable. Corrected code regenerated golden
(12 lines, sha256 c4aa0ff991db...).
- (a) corrected checker: **rc=0 `PASS: ... golden x2 identical (12 normalized lines, sha256 c4aa0ff991db)`** — matches V5's `golden x2 identical (12 normalized lines, sha256 c9e7f414126a)` (identical line count; sha differs because the subtitle VALUE I used differs from V5's — expected).
- (b) M8 mutant (the `async_lines.sort` line removed, C:880), same evidence: **rc=1 `failure_reason: golden: golden mismatch between run-1 and run-2 at normalized line 4`** — matches V5's line 4 exactly. The sort is the discriminator.

**Normalized-line numbers (why 6 vs 7, not from memory):**
- **M4 canonical = line 6** (my canonical run, and V5). The REAL committed timelines have two `usage_update`
  records each; the canonical mutator chooses the first by `next(...)` (the one immediately before raw
  `session/prompt` in both legs) and moves run-2's chosen tool_call after terminal. With the correct closed set,
  `session_info_update` is re-homed after session/new but tool_call stays in the protocol-ordered stream: after
  the re-homed session-info line (index 4) and available-commands line (index 5), run-1 has tool_call at line 6
  while run-2 has session/prompt. The first mismatch is therefore line 6; V5 and my rebuilt real CLI agree.
- **M8 = line 4** (both my canonical run and V5). Raw A/B pairs occupy their legs' original async positions
  (after prompt / after terminal), but normalization re-homes both to the PRE-PROMPT session-new slot. With the
  sort present, both runs normalize the pair to the same [A,B] order (deterministic JSON-string sort), so the
  frozen golden (12 lines) matches and the corrected checker PASSES. Without the sort (M8), the raw A,B / B,A
  orders survive at that re-homed slot, and the first divergence is normalized line 4 (the pre-prompt slot,
  hence 4 not 6).
- **G2's in-test M4 = line 7** (`match=r"^golden: golden mismatch ... line 7$"` at T:2151) is a DIFFERENT construction: it mutates the SYNTHETIC `bundle`
  fixture (not the committed evidence). I independently ran the exact T:2121-2152 transformation on that
  fixture: both first tool_idx values are 6; run-1's neighbour is `session_info_update`, run-2's is
  `agent_message_chunk`; after the true adjacent swap, normalized lines 0-6 agree and line 7 is
  `tool_call` vs `agent_message_chunk`. It therefore correctly raises at 7. This is why the brief's item 3
  (line 6, committed evidence) and G2's test (line 7, synthetic bundle) differ — both are correct for their
  own construction.

**The mutants now die by the NEW tests (item 3's second half):**
- M4 by `test_golden_non_async_kind_order_binds_through_check_golden` (`def ...` at T:2121 through
`cc.check_golden(bundle / "golden")` at T:2152): on the widened-M4 tree,
  the test's `with pytest.raises(...)` at T:2149 does not fire -> `E  Failed: DID NOT RAISE Failure`,
  `1 failed in 2.47s`. (The test pins the regenerated golden, so the widened checker no longer
  reaches the mismatch.)
- M8 by `test_golden_two_async_records_in_opposite_raw_orders_normalize_identically` (T:2080-2118): on the
  M8 tree, `E  AssertionError: opposite raw orders changed the normalized async multiset`,
  `E  assert [ ... "session_info_update","update":{"updatedAt":"str"}}'] == [ ... "subtitle":"str","updatedAt":"str"}}']`,
  `At index 4 diff`, `1 failed in 1.90s`. The failure is `assert expected == cc.normalize_timeline(raw_ba)` at T:2094 (message `opposite raw orders changed the
  normalized async multiset`); its distinctness prerequisite `assert normalized_a != normalized_b` at T:2091
  (`assert normalized_a != normalized_b`; message `the two async records do not have distinct normalized lines`) passes because
  subtitle IS non-volatile.

SOLID. Not a blocker — item 3 confirms both canonical discriminators reproduce through the real CLI and the
new tests kill the two former full-suite survivors. The M4 widened-checker divergence from V5 is a DISCREPANCY
(D2), not a blocker (D2 does not change that M4 is a real, material, contract-mapped defect, now killed by the
new test).

## Item 4 — the new tests are GATES, not mirrors (SOLID)

**(a) the `check_golden` path is real.** Read `check_golden` (C:1559-1581) first: line 1562 `if n1 != n2:` ->
1563 `first = next(...)` -> 1564 `raise Failure(f"{leg}: golden mismatch between run-1 and run-2 at normalized
line {first}")`; then `if frozen_sha != PINNED_GOLDEN_SHA256` at C:1570 and
`if frozen_lines != n1` at C:1577. (The brief said "C:1578 region";
the actual mismatch raise is C:1562-1564 — I used the real line. The later frozen-lines branch is
`raise Failure(f"{leg}: normalized runs differ from the frozen golden.jsonl")` at C:1578.) On a scratch copy of C I turned the
n1!=n2 mismatch raise into a pass (`if False: pass`). Ran the two new G2 tests:
- `test_golden_non_async_kind_order_binds_through_check_golden`: **DIED** -> `E  Failed: DID NOT RAISE Failure`,
  `with pytest.raises(
            cc.Failure, match=...)` at T:2149 fails with `1 failed`. With the mismatch suppressed the expected Failure
  no longer fires, so it fails. This proves the test exercises the mismatch raise (it is a GATE on that path).
- `test_golden_two_async_records_in_opposite_raw_orders_normalize_identically`: **PASSED** (1 passed) — it
  constructs a valid order-free pair (n1==n2 holds), so suppressing the mismatch does not affect it and its
  later `check_golden(...) == expected` return assertion completes. The mismatch-raise GATE is therefore carried
  by the M4 test; the M8 test separately carries the frozen-bytes + `check_golden`-return path.
Conclusion: the `check_golden` path is real — a test dies when the mismatch raise is removed. Not a mirror.

**(b) the monkeypatched `PINNED_GOLDEN_SHA256` bypass is BY DESIGN and the pin keeps independent gates.**
The new tests set `check_acp_conformance.PINNED_GOLDEN_SHA256` (T:2115, T:2147) to the sha of a REGENERATED
fixture golden — that is the only way a synthetic/regenerated golden can pass `check_golden`'s frozen-sha check
(C:1570). This is the established pattern (the same `monkeypatch.setattr(... PINNED_GOLDEN_SHA256 ...)` also
appears in pre-existing test setup `monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", golden_sha)`
at T:483 (`monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", golden_sha)`) and in the
frozen-lines test at T:1879 (`monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", _sha256(new_text.encode()))`). The
REAL pin therefore stays independently gated by:
- `test_cli_pass_path_fails_on_golden_pin` (T:568): runs the checker as a SUBPROCESS, which does NOT inherit the
  in-test monkeypatch, so it sees the REAL pin from pins.py; the synthetic bundle's golden sha (93b3122bc208)
  does not match the real pin (6225adb8ecc2) -> `assert r.returncode == 1` at T:579 and exact
  `assert r.stdout.strip() == "failure_reason: golden: golden.jsonl sha256 93b3122bc208 != pinned 6225adb8ecc2"`
  at T:580. This is the real pin binding exercised in a subprocess against a synthetic
  golden; the subprocess reads the unpatched real pin from pins.py.
- `test_golden_regen` (T:2170): regenerates a synthetic golden that cannot satisfy the real sha pin -> asserts
  `rc==1` and `out.startswith("failure_reason: golden: golden.jsonl sha256")` at T:2188-2189. No monkeypatch —
  the real pin is used.
- `test_golden_frozen_lines` (T:1872): rewrites the frozen golden.jsonl to a different (mutant) byte string and
  monkeypatches the pin to the NEW text's sha (T:1879 `monkeypatch.setattr("check_acp_conformance.PINNED_GOLDEN_SHA256", _sha256(new_text.encode()))`) so the sha passes but the frozen LINES differ from the
  normalized runs -> `assert rc == 1` at T:1881 and exact `assert out == "failure_reason: golden: normalized
  runs differ from the frozen golden.jsonl"` at T:1882 (`assert out == "failure_reason: golden: normalized runs differ from the frozen golden.jsonl"`; frozen LINES). This gates the frozen-LINES check (C:1577) independently of the sha.
So the pin is not hollowed out: `test_cli_pass_path_fails_on_golden_pin` gates the real sha binding,
`test_golden_regen` gates regen-rejection on the real pin, `test_golden_frozen_lines` gates the frozen-lines
check. The new tests' monkeypatch only bypasses the sha for the regenerated fixture golden, which is correct.

**(c) the `subtitle` discriminator.** From C:104 (`VOLATILE_UPDATE_FIELDS = {"content","text","title","rawInput",
"rawOutput","locations","_meta","usage"}`) and C:787 (`_shape` drops keys in `VOLATILE_UPDATE_FIELDS` when
building the normalized update dict): `title` IS in the volatile set (dropped); `subtitle` is NOT (survives).
So record A (the original session_info_update, whose normalized update keeps only `updatedAt`) and record B
(original + `subtitle`="second async record") have DISTINCT normalized lines: A keeps `{"updatedAt":"str"}`,
B keeps `{"subtitle":"str","updatedAt":"str"}`. The test asserts `normalized_a != normalized_b` at T:2091 (message: `the two async records do not have
distinct normalized lines`; it passes on the un-mutated new T). I then mutated record B on a copy of T to use `title` instead of `subtitle`
(`record_b["frame"]["params"]["update"]["title"] = "second async record"`): because `title` is dropped by
`_shape`, A and B normalize to the SAME line, and the test's own distinctness assertion `assert normalized_a != normalized_b` at T:2091 goes red:
- `E  AssertionError: the two async records do not have distinct normalized lines`,
  `E  assert '{... "sessionUpdate":"session_info_update","update":{"updatedAt":"str"}}' != '{... same ...}'`,
  `1 failed in 1.79s`.
This proves the `subtitle` choice (G2's DISCREPANCIES) is load-bearing: a volatile field (title) would make the
two records indistinguishable and the whole test a no-op; a non-volatile field (subtitle) is what gives the
sort a real discriminating key. SOLID. Not a blocker — the test is a genuine gate.

## Item 5 — the full M1-M8 table re-run on the new T (SOLID — every row KILLED by a NAMED test)

Re-ran all eight production mutants on a fresh scratch archive of the PIN with the final T copied in; for
each I ran the named killer test and captured its exact failing assertion line. A pristine run (no mutation)
first confirmed the two new G2 tests PASS on the un-mutated new T (`2 passed in 1.89s`), so a later failure is
caused by the mutant, not the test.

| mutant | production mutation | named test (new T) | failing assertion line (measured) | `N failed` |
|---|---|---|---|---|
| M1 | P:138 `ASYNC_SESSION_UPDATES` += `agent_message_chunk` | `test_golden_synchronous_frame_order_still_binds` (T:2010) | `E  AssertionError: moving the SYNCHRONOUS agent_message_chunk did not change the output — the control is a tautology.` (T:2035) | `1 failed in 0.52s` |
| M2 | C:879 `async_lines.append((intro.get(rec.get("sessionId")), line))` -> `(None, line)` | `test_golden_async_notification_is_order_free` (T:1943) | `E  AssertionError: last normalized line is not the end_turn terminal: {"dir":"a2c",..."session_info_update"...}`; assertion `assert last["dir"] == "a2c" and last.get("stopReason") == "end_turn"` at T:1966 | `1 failed in 0.56s` |
| M3 | replace C:868 `sync = [norm(entry) for entry in entries if not is_async(entry)]` with `sync = [norm(entry) for entry in entries]` | `test_golden_async_placement_is_independent_of_the_session_new_response` (T:1977) | `E  AssertionError: async notification before the session/new response changed the output`; assertion `assert out_before == out_after` at T:1997 | `1 failed in 0.50s` |
| M4 | P:138 `ASYNC_SESSION_UPDATES` += `tool_call` | `test_golden_non_async_kind_order_binds_through_check_golden` (T:2121, NEW) | `E  Failed: DID NOT RAISE Failure` (T:2149) | `1 failed in 1.94s` |
| M5 | skip C:1570 `if frozen_sha != PINNED_GOLDEN_SHA256` | `test_golden_regen` (T:2170) | `E  assert 0 == 1`; assertion `assert rc == 1` at T:2188 | `1 failed in 4.70s` |
| M6 | force C:1694 `check_bundle` to `raise Failure("MUTANT broken checker")` | `test_committed_bundle_runner_mints_a_result` (S:106) | `E  AssertionError: expected exit 0, got 1: ... stderr='leg-exit-mismatch: S0-01 positive expected 0 got 1\n'` | `1 failed in 0.39s` |
| M7 | delete `golden/negative` evidence leg | `test_committed_negative_leg_cmd_reports_the_protocol_violation` (S:127) | `E  AssertionError: expected exit 1, got 2: 'deferred: negative probe not captured\n'` | `1 failed in 0.28s` |
| M8 | remove C:880 `async_lines.sort(key=lambda item: item[1])` | `test_golden_two_async_records_in_opposite_raw_orders_normalize_identically` (T:2080, NEW) | `E  AssertionError: opposite raw orders changed the normalized async multiset`; assertion `assert expected == cc.normalize_timeline(raw_ba)` at T:2094 | `1 failed in 1.94s` |

**M4 and M8 die by the NEW tests** (`test_golden_non_async_kind_order_binds_through_check_golden`,
`test_golden_two_async_records_in_opposite_raw_orders_normalize_identically`), NOT by
`test_real_bundle_passes_every_check` — the brief's explicit requirement is met. (On the old 955ab74 T both
M4 and M8 SURVIVED the named tests and the whole two-file suite, 476 passed; that is exactly the F1 defect the
repair removes.) No survivor in the frozen M1-M8 table: every row is KILLED by a named test. M2, M3, M5, M6, M7 are
unchanged from V5 (SOLID killers, still kill). SOLID. This supports closure of F1's stated M1-M8 mutation set;
FOLLOW-UP F1 separately identifies an un-frozen future-test-regression hardening case.

## Item 6 — gates on the PIN's final bytes (SOLID)

Environment: `PATH=/home/rocco/venv-agent-factory/bin:$PATH`, `S0_01_VENUE=pc`,
`S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`,
`S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`; `--basetemp` parent exists at `../scratch/bt`.

1. `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/bt/vg2i6a tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py`
   -> **`478 passed in 80.38s (0:01:20)`**, `RC=0`.
2. Same final T bytes, `--basetemp ../scratch/bt/vg2i6b`
   -> **`478 passed in 84.95s (0:01:24)`**, `RC=0`.
3. Final clean rerun after the report artifact was written, `--basetemp ../scratch/bt/vg2i6c`
   -> **`478 passed in 84.98s (0:01:24)`**, `RC=0`.
   Counts agree (`478 passed` ×3), exercising the requested two-file set.
4. `python -m pyflakes tests/test_s0_01_check_acp_conformance.py` -> **`pyflakes_rc=0`**.
5. `python3 scripts/ap_screen.py --tests tests/test_s0_01_check_acp_conformance.py` ->
   `--- TEST_SCREEN over 1 path(s): 4 hits over 1 files ---`; the only hits are the four stated pre-existing,
   unchanged, out-of-hunk sites:
   - AP-66 T:88: `nv._point_mul = _cached_pm`.
   - AP-66 T:90: `nv._point_mul = _orig_pm`.
   - AF-AP-57 T:5590: `if call_count[0] == 2`.
   - AF-AP-48 T:6147: `assert all(site[3] in {"walk", "require_regular_file", "stdin", "consumer"}`)). No new hit in
   test function `test_golden_synchronous_frame_order_still_binds` at T:2010-2152. The last
   printed hit line is T:5590 (the screen groups by registry key; the last output block is AF-AP-57), while
   the summary is the authoritative result above.
6. `sha256sum tests/test_s0_01_check_acp_conformance.py` ->
   **`a71f6c44fc9d9c050448c1223d0bbfbd4143a4951a011f307d2288ba2d8401d1  tests/test_s0_01_check_acp_conformance.py`**,
   exactly the expected final-T sha.
7. `git diff --check 955ab74 f84265f -- tests/test_s0_01_check_acp_conformance.py` -> `rc=0` (no whitespace error).
8. Authoritative count command: `scripts/test_summary.sh tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py` ->
   `478 passed in 351.11s (0:05:51)`; `pytest-exit: 0`; `pytest-summary: 478 passed in 351.11s (0:05:51)`.

SOLID. No blocking predicate clause is met; all requested final-byte gates passed three times/cleanly.

## Item 7 — exhaustive bounded review of G2 hunks (FOLLOW-UP F1; no blocker)

Reviewed the complete `955ab74..f84265f` test hunk, beginning at `def test_golden_synchronous_frame_order_still_binds()`
(T:2010) through the final added control `cc.check_golden(bundle / "golden")` (T:2152), plus direct production consumers:
C:785-887 (`def _shape` / `def normalize_timeline`), C:1559-1660 (`def check_golden`), P:130-145
(`# ASYNC_SESSION_UPDATES` and `ASYNC_SESSION_UPDATES = ("session_info_update",)` closed contract; owner decision (a)), and the predecessor verifier's V5 contract (`## V5/V6` at V:60-84). Static mapping: `graft ask` maps the four G2 tests to
T:2010-2039 (`test_golden_synchronous_frame_order_still_binds`), T:2042-2068
(`def test_golden_async_set_is_closed()` / `test_golden_async_set_is_closed`), T:2080-2118 (`test_golden_two_async_records_in_opposite_raw_orders_normalize_identically`),
T:2121-2152 (`test_golden_non_async_kind_order_binds_through_check_golden`) and `_check` T:510-522; the `lane_context` final pack is
`../scratch/vg2-final-pack.md` (237 lines). Ripwire's callers query finds no caller because pytest discovers the
test functions, which is expected; its test-gate flags checker `main`/`check_bundle` as statically impacted but
we ran the checker test suite and the real CLI canonical M8 path. GitNexus cannot map the new test symbol in the
clone index (`risk=UNKNOWN`), so it supplies no reachability claim. The two independent actual-path instruments
are the real CLI canonical discriminators (item 3) and pytest mutation runs (items 2/5).

**F1 — FOLLOW-UP: the generic self-checks do not independently prove exact adjacency.**
- **Evidence level:** verified by scratch mutation.
- **Contract mapping:** no unmet frozen criterion. the frozen G2 brief:21-24 requires source tail `i+2` plus length,
  multiset, and changed-order checks. Current T has all of those; the direct formula is an adjacent swap.
  The verification item asks whether generic checks can admit another permutation, but it does not make an
  independent mathematical proof of adjacency an acceptance criterion. The brief's actual acceptance text is
  `len(moved) == len(entries)`, `sorted(json.dumps(...)) == sorted(...)`, and `moved != entries` (G2 brief:21-24),
  all of which current T satisfies.
- **Canonical-path status:** the current controls execute through pytest against production `cc.normalize_timeline`
  (`n_orig = cc.normalize_timeline(entries)` through `assert n_orig != n_moved` at T:2033-2038 /
`n_orig = cc.normalize_timeline(tc)` through `assert n_orig != n_moved` at T:2064-2068), and current production M1/M4 mutations fail. The hostile alternative changes T
  itself, so it is a future-test-regression probe, not a defect reproducing on the current production path.
- **Material effect:** no current output, evidence, determinism, or integration effect. The exact source swap
  is correct; M1/M4 are killed by the current controls and all standard M1-M8 mutants are killed. A future
  non-adjacent formula could weaken this test gate, which is valuable hardening information but not present harm.
  Scope check: the hostile M4 full two-file suite was `1 failed, 477 passed` because the OTHER new focused M4
  checker-path test still kills widened M4; hostile M1 has broader unrelated real-bundle/pin failures. Thus this
  probe does not show the frozen suite would be green; it shows only that the specific self-checks do not certify
  adjacency independently.
- **Concrete discriminator:** two scratch combined mutations:
  1. M1: `[agent_message_chunk, usage_update, terminal] -> [terminal, usage_update, agent_message_chunk]` plus
     P:138 `ASYNC_SESSION_UPDATES = ("session_info_update",)` widened with `agent_message_chunk` -> named control **`rc=0, 1 passed in 0.48s`**.
  2. M4: non-adjacent 4-item rotation plus P:138 `ASYNC_SESSION_UPDATES = ("session_info_update",)` widened with `tool_call` -> named control **`rc=0, 1 passed in 0.48s`**.
  Both retain the generic length/multiset/different-order invariants. A scratch proposed pair-exchange assertion
  turns both red at `adjacent swap did not exchange exactly the chosen pair` (M1 `1 failed in 0.56s`, M4
  `1 failed in 0.63s`).
- **Task ownership:** T/G2 test boundary. Suggested follow-up (not made): assert exact unchanged prefix/tail
  and `moved[idx:idx + 2] == [entries[idx + 1], entries[idx]]`; rerun hostile rotations and the M1-M8 table.
  **Blocking predicate:** fails clause 1 (the frozen source/invariant requirement is met) and clause 3 (no
  present material effect); clauses 4/5 are satisfied only for the hypothetical future-test mutation. **Does not block.**

**D2 — DISCREPANCY: V5's documented widened-M4 canonical CLI outcome does not reproduce in a clean reconstruction.** The V5 report says
that after correct-code golden+pin regeneration the widened M4 checker `rc=0 PASS` (V:77). I rebuilt the documented construction (ordinary `usage_update` -> `tool_call` in both runs; run-2 moved after terminal; raw time re-stamped;
golden+pin regenerated with the correct checker): corrected CLI is the stated rc=1 mismatch line 6, but widened
M4 makes its normalized runs equal THEN the `if frozen_lines != n1` check at C:1577 fails because their widened
normalization differs from the correct-code frozen golden: **`rc=1 failure_reason: golden: normalized runs differ from the frozen golden.jsonl`**.
This is expected from C:868-884 (`sync = [norm(entry) for entry in entries if not is_async(entry)]`, then
`async_lines.sort(key=lambda item: item[1])`): widening makes tool_call async and re-homes/sorts it at the session/new slot,
while the correct-code regenerated golden leaves it in its raw ordered position. I then verified the only state
that yields V5's claimed PASS: regenerate golden+pin AFTER widening, under the mutant normalizer; that yields
**`rc=0 PASS ... golden x2 identical (11 normalized lines, sha256 214feef93312)`**. Therefore, in this clean
reconstruction, V5's reported `rc=0 PASS` requires a MUTANT-CODE golden, contrary to its "correct code" wording.
This discrepancy does NOT weaken the canonical proof: corrected code still rejects the forbidden reordering at
line 6; M4's focused G2 test dies at `with pytest.raises(
            cc.Failure, match=...)` (T:2149) when the set is widened; M4 is killed in the full M1-M8 audit. It is
not a new production defect and has no material effect on G2. Suggested follow-up: correct V5's canonical-run
narrative to distinguish "correct-code golden" from "mutant-code golden". Reported first-class; no repair here.

No other meaningful observation inside `def test_golden_synchronous_frame_order_still_binds` (T:2010) through
`cc.check_golden(bundle / "golden")` (T:2152) beyond FOLLOW-UP F1 and discrepancy D2. This bounded item deliberately did not re-run V1-V4/V6-V8,
the mint, real capture, runner, ledger, corpus, or neighboring components: the brief explicitly excludes them,
and G2 touches T only.

## Finding inventory

1. **FOLLOW-UP F1 — generic self-checks do not independently certify exact adjacency.**
   - Evidence: **SOLID** for the future-test-regression probe: fresh scratch copies produce deterministic
     M1/M4 `rc=0, 1 passed` after the non-adjacent test-formula mutations.
   - Contract mapping: the actual frozen `i+2` formula and three required checks exist, so no current
     criterion is contradicted. Item 2 asks the question and the answer is yes: other permutations can pass.
   - Canonical path: current controls and current production M1/M4 mutations run through the real
     `cc.normalize_timeline` and fail. The observed survivor requires changing T itself.
   - Material effect: no current state/evidence/output change; this is future hardening, not a present defect.
   - Reproduction: `scratch/vg2-selfcheck-hollow.py`; proposed structural red-control:
     `scratch/vg2-structural-fix-probe.py`.
   - Task ownership: T:2010-2068 (`test_golden_synchronous_frame_order_still_binds` / `test_golden_async_set_is_closed`). Suggested follow-up (not made): exact prefix/tail and pair-exchange assertions;
     rerun hostile rotations. **Does not block.**

2. **FOLLOW-UP F2 — V5's documented widened-M4 canonical CLI `rc=0 PASS` does not reproduce with a correct-code regenerated golden.**
   - Evidence: **SOLID** (fresh clean scratch runs with `python3 -B` / no stale bytecode).
   - Contract mapping: none to G2's focused acceptance beyond evidence accuracy.
   - Canonical path: real checker CLI. Correct-code golden -> corrected C `rc=1 mismatch line 6`; widened C against that golden -> `rc=1 normalized runs differ from frozen golden`; widened golden+pin -> `rc=0 PASS`.
   - Material effect: no G2 production behavior changes. It is a predecessor-report evidence discrepancy, not the repair's root cause.
   - Reproduction: `scratch/vg2-m4-d2-clean.py`.
   - Task ownership: predecessor verification report / coordinator documentation, not the focused T repair. Suggested action: amend V5 narrative to say the PASS used a widened-code golden, or retain only the corrected-code reject proof. Does not block.

3. **INFO — the M8 fixture correctly uses `subtitle`, not the brief's suggested `title`.** Evidence SOLID: C:104/C:787, and `assert normalized_a != normalized_b` at T:2091 turns red when B uses title. This is an intentional and necessary correction, not a defect.

4. **INFO — final suite, pyflakes, hash, whitespace, and AP screen all reproduce cleanly** (item 6). These
   support the frozen G2 repair; they do not address the separate FOLLOW-UP F1 future-test-regression probe.

## DISCREPANCIES

1. **D1 (scope nuance):** generic self-checks do not prove adjacency. Measurement: a non-adjacent permutation preserves all three and can make M1/M4 survive only after T itself is mutated (`scratch/vg2-selfcheck-hollow.py`, rc=0/1 passed each). This is FOLLOW-UP F1, not a current contract failure.
2. **D2 (predecessor report):** VERIFY-VB-F12 V5 says widened M4 `rc=0 PASS` after correct-code golden+pin regeneration. Measured cleanly: it is `rc=1 normalized runs differ from frozen golden`; PASS requires a widened-code golden (`scratch/vg2-m4-d2-clean.py`).
3. **D3 (brief source location):** item 4 names the n1!=n2 mismatch raise as “C:1578 region”; actual raise is C:1562-1564. C:1578 is the later frozen-lines failure. The requested mutation was applied to the actual mismatch branch.
4. **D4 (tooling):** GitNexus clone index cannot map the new G2 test symbol (`risk=UNKNOWN`); ripwire finds pytest test functions have no in-code callers. Reachability is established by actual pytest runs plus real CLI canonical discriminators, not inferred from either static result.
5. **D5 (report lint):** initial scan had 99 refs, OK 44, NEAR 3, MISS 30, UNCHECKABLE 22, UNRESOLVED 0. Three bounded cleanup passes reached 107 refs, OK 89, NEAR 3, MISS 5, UNCHECKABLE 10, UNRESOLVED 0. A post-bound no-improvement confirmation followed an extra citation-format adjustment; it had the same summary. This exceeded the three-pass lane rule, so it is disclosed rather than hidden; the remaining line-wrap heuristic artifacts are recorded below.

## NOT-done

- No source repair was made; this is a read-only verifier lane. FOLLOW-UP F1 may warrant a focused hardening increment; it is not required for the frozen G2 repair to proceed.
- No evidence, golden, pin, checker, corpus, runner, ledger, model, relay, service, or external system was changed.
- V1-V4/V6-V8, the mint, capture, runner/ledger, corpus, and neighboring components were deliberately not re-run; the brief limits this round to the F1 repair.
- No git add/commit/push/checkout/reset/stash occurred. Scratch artifacts only were mutated.
- The coordinator owns the final gate decision; this is a recommendation, not a verdict.

## GATE RECOMMENDATION

`MERGE-READY-WITH-FOLLOWUPS` — no finding satisfies the complete blocking predicate. The frozen G2 repair is
present and reproduced: true `i+2` swaps, M1-M8 standard mutants all killed by named tests, M4/M8 focused
new-test kills, canonical real-CLI M4/M8 discriminators, three 478-pass final suites, pyflakes, AP screen, and
final T hash are SOLID. FOLLOW-UP F1 is a future-test-hardening opportunity that fails blocking clauses 1 and 3:
its survivor requires mutating T itself, while the current source meets the frozen requirement and current M1/M4
die. Full-suite scope confirms hostile M4 still has `1 failed, 477 passed` because the separate new M4
checker-path test catches it; the generic self-check limitation is therefore not a current suite-wide survivor. FOLLOW-UP F2/D2 is predecessor-report evidence clarification. Coordinator owns the final decision.

retro: nuance found — generic permutation checks cannot independently prove adjacency. Record as a FOLLOW-UP hardening lesson (not an incident-level current gate defect); coordinator may add it to the relevant skill/decision context.

## Report-lint bounded result

- Initial scan: `report_lint: 99 refs — OK 44, NEAR 3, MISS 30, UNCHECKABLE 22, UNRESOLVED 0 (worktree)`.
- Cleanup pass 1: `report_lint: 104 refs — OK 61, NEAR 5, MISS 18, UNCHECKABLE 20, UNRESOLVED 0 (worktree)`.
- Cleanup pass 2: `report_lint: 107 refs — OK 82, NEAR 3, MISS 12, UNCHECKABLE 10, UNRESOLVED 0 (worktree)`.
- Cleanup pass 3: `report_lint: 107 refs — OK 89, NEAR 3, MISS 5, UNCHECKABLE 10, UNRESOLVED 0 (worktree)`.
- Post-bound confirmation after an extra citation-format adjustment: same `107 refs — OK 89, NEAR 3, MISS 5,
  UNCHECKABLE 10, UNRESOLVED 0`; no further adjustment was attempted.

The remaining heuristic misses are line-wrap / adjacent-reference artifacts (not unresolved paths; UNRESOLVED=0),
including ranges with the source token on the next report line. The three bounded hint-driven passes are complete;
the extra no-improvement confirmation is disclosed as a lane-process discrepancy, and remaining misses are reported rather than chased.
