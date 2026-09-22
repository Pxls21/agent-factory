# PC lane — VERIFY-G2 (targeted re-verification of ONE repair: VERIFY-VB-F12 F1, the golden's reorder controls)

PIN: f84265f

Role: adversarial-verifier. Route: the LOCAL Qwen verify route (`agentfactory-verify-local`, xhigh — the pc_lane.sh
default for adversarial-verifier; do NOT set HERMES_MODEL). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.
Report: draft after EACH item at `tasks/briefs/s0-01-vb-f12-support/VERIFY-G2-report.md`, return it whole as your
final message. You VERIFY; you never fix. A finding is file:line-bounded, reproduced through the real path, and graded
by the blocking predicate (contract-mapped · reproduced canonically · materially effective · a concrete discriminator ·
in-boundary). Emit a GATE RECOMMENDATION (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID),
never a verdict — the coordinator decides; under D-034 a non-blocking finding becomes a `verify-followup` issue.

## Scope — one blocker's repair, nothing else
VERIFY-VB-F12 (`tasks/briefs/s0-01-vb-f12-support/VERIFY-VB-F12-report.md`, §V5 and F1) found ONE blocker on PIN
955ab74: G1's two golden reorder controls built their "moved" list with a DUPLICATED neighbour (`entries[idx+1:]`
where `entries[idx+2:]` was needed), so the production mutants M4 (`ASYNC_SESSION_UPDATES` widened to `tool_call`,
`proofs/S0-01/pins.py:138`) and M8 (the async sort `proofs/S0-01/check_acp_conformance.py:880` removed) survived the
whole suite while the real checker's verdicts changed. Every other item of that round (V1-V4, V6-V8) was SOLID and is
NOT re-run here. The repair G2 (brief `tasks/briefs/pc/pc-vb-f12-g2.md`, report
`tasks/briefs/s0-01-vb-f12-support/G2-report.md`, built on PIN 85836a5) touched T ONLY:
`tests/test_s0_01_check_acp_conformance.py` T:2010-2152 (the two controls made true swaps and self-verifying; a
two-async opposite-order test through the real `check_golden`; a tool_call-order test through the real
`check_golden`). This lane grades THAT repair against the frozen contract. The mint `proofs/S0-01/result.json`
(e458801) is unchanged by G2.

## Items (each: what you did · the exact command · the exact output · SOLID/UNSURE · blocking? each predicate clause)
1. PREMISE (first; stop on failure): `git diff --stat 955ab74 f84265f -- proofs/ tests/test_s0_01_spec_runner.py
   scripts/proof-runner scripts/validate-ledger` must be EMPTY, and `git diff --stat 955ab74 f84265f -- tests/` must
   name only T. Paste both. If C, P, the golden, S, the runner or the evidence changed since the verified PIN, the
   premise of this targeted round is false: report CONTRACT-INVALID and stop.
2. The controls are TRUE swaps (T:2010-2038, T:2042-2068). Read the two functions. State whether the three
   self-checks (same length, same multiset of canonical JSON lines, different order) can be satisfied by anything
   other than a true adjacent swap of the chosen entry. Then kill M1 and M4 through the CONTROLS: on scratch copies
   of P widen `ASYNC_SESSION_UPDATES` with `agent_message_chunk` (M1) and with `tool_call` (M4) — the named control
   (`test_golden_synchronous_frame_order_still_binds` for M1, `test_golden_async_set_is_closed` for M4) must fail at
   its normalized-output assertion, never at a self-check. Paste the `E` line and the `1 failed` summary each.
3. YOUR canonical discriminators (VERIFY-VB-F12 §V5 items 1-2: `../scratch/canonical-mutants/run.py` — rebuild it
   from the report's description if the scratch is gone: for M4, `usage_update` → `tool_call` in both runs and run-2's
   moved after the terminal, golden+pin regenerated with the correct code; for M8, two distinct valid
   `session_info_update` records A/B in opposite raw orders) re-run on the NEW T's tree: (a) the real-CLI outcomes on
   the correct C are unchanged (paste rc + failure_reason / PASS line); (b) the mutants now die by the NEW tests —
   M4 by `test_golden_non_async_kind_order_binds_through_check_golden` (T:2121-2152), M8 by
   `test_golden_two_async_records_in_opposite_raw_orders_normalize_identically` (T:2080-2118). Paste each `1 failed`
   summary with its assertion line. The normalized-line numbers differ between constructions (yours measured 6, G2's
   fixture 7) — state why from the two constructions, not from memory.
4. The new tests are GATES, not mirrors: (a) the `check_golden` path is real — on a scratch copy of C turn the
   n1 != n2 mismatch raise (C:1578 region; read `check_golden` C:1533-1660 first) into a pass: name the test that
   dies. (b) the `monkeypatch.setattr(... PINNED_GOLDEN_SHA256 ...)` inside T:2080-2152 bypasses the pin BY DESIGN for
   a regenerated fixture golden — confirm the pin itself keeps independent gates (`test_cli_pass_path_fails_on_golden_pin`,
   `test_golden_regen`, `test_golden_frozen_lines` T:1872: name each and the line it asserts). (c) the `subtitle`
   discriminator (G2 DISCREPANCIES): confirm from C:104 (`VOLATILE_UPDATE_FIELDS`) and C:787 (`_shape`) that `title`
   is dropped and `subtitle` survives, and that record B's normalized line differs from A's (T:2090-2092) — then
   mutate record B on a copy of T to use `title`: the test's own distinctness assertion must go red (paste).
5. The full M1-M8 table (VERIFY-VB-F12 §V5) re-run on the new T: every row KILLED by a NAMED test — paste the table
   (mutant · test · the failing assertion line · `N failed`). A survivor is a finding. M4 and M8 must die by the tests
   of items 3-4, not only by `test_real_bundle_passes_every_check`.
6. Gates on the PIN's bytes: `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/bt/<run>
   tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py` TWICE (the lane pasted `478 passed`
   ×2 — paste yours); `python -m pyflakes tests/test_s0_01_check_acp_conformance.py` rc 0; `python3
   scripts/ap_screen.py --tests tests/test_s0_01_check_acp_conformance.py` last line (the four pre-existing hits at
   T:88, T:90, T:5590, T:6147 are known — anything else is a finding); `sha256sum
   tests/test_s0_01_check_acp_conformance.py` (expected a71f6c44fc9d9c050448c1223d0bbfbd4143a4951a011f307d2288ba2d8401d1).
7. Anything else INSIDE the G2 hunks (T:2010-2152). Exhaustive discovery; disciplined disposition.

## Boundary
READ-ONLY on the tree: attack through SCRATCH COPIES only (`../scratch`); never git-restore/stash/checkout the shared
tree; never `git add/commit/push`; never touch the corpus `/home/rocco/s0-01-pinned/realleg/golden`, the model server,
any unit, or another lane's tree. No live captures, no relay deliveries.

## Gate mechanics (each call under Hermes's 420 s terminal cap)
- `export S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`;
  `/home/rocco/venv-agent-factory/bin` first on PATH; `mkdir -p ../scratch/bt`; an absolute SHORT `--basetemp`.
- pytest on this host: `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/bt <files>` DIRECTLY
  (`scripts/pc_suite.sh` is the SANDBOX's launcher and cannot run here). T alone is ~15 min serial — always `-n 8`.
- CODE INTEL FIRST: `graft skeleton` / `graft ask` before any whole-file read (T is >6,000 lines — read by range).
  `report_lint` gates on a FLOOR (`--min-refs 12`); apply its `fix:` hints for at most THREE rounds, then paste and
  finish; paste its summary as PLAIN text.

## Report shape (DATA)
Per item: command · exact output · SOLID/UNSURE · blocking? (the predicate, each clause answered) · the file:line.
Then: the M1-M8 table (item 5), DISCREPANCIES, NOT-done, GATE RECOMMENDATION. Never a fix, never a verdict.
