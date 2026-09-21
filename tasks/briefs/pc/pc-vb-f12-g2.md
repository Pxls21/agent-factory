# PC lane — VB-F12-G2 (repair round: the S0-01 golden's reorder controls must KILL the widened-set and dropped-sort mutants — VERIFY-VB-F12 F1)

PIN: 85836a5

Role: code-implementer. Route: the LOCAL Qwen build route (the pc_lane.sh default; do NOT set HERMES_MODEL). Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first (the pytest gate on this host is `python -m pytest -n 8 …` directly).
Report: draft after EACH item at `tasks/briefs/s0-01-vb-f12-support/G2-report.md`, return it whole as your final message.
ONE focused repair (D-031): close F1 exactly; nothing else. The normalizer (C) is CORRECT — do not touch it.

## The blocker (read `tasks/briefs/s0-01-vb-f12-support/VERIFY-VB-F12-report.md` §V5/V6 WHOLE first)
T=tests/test_s0_01_check_acp_conformance.py · C=proofs/S0-01/check_acp_conformance.py · P=proofs/S0-01/pins.py.
`test_golden_synchronous_frame_order_still_binds` (T:2010-2033) and `test_golden_async_set_is_closed` (T:2036-2056) build
their "moved" list as `entries[:i] + entries[i+1:i+2] + entries[i:i+1] + entries[i+1:]` — the last slice must start at
`i+2`; as written the neighbour is DUPLICATED (12 entries), so "the output differs" holds because a frame was ADDED and
the controls kill nothing: with M4 (`ASYNC_SESSION_UPDATES` widened to `tool_call`) and M8 (`async_lines.sort(...)`
at C:880 removed) the whole 476-test suite stays green while the real checker's verdicts change (AF-AP-109,
docs/INCIDENT-LOG.md item 14). The verifier's canonical discriminators live on this host under
`/home/rocco/agent-factory/.lanes/pc-verify-vb-f12.md--955ab74/scratch/canonical-mutants/` (read-only; copy, never edit).

## The repair (T only)
1. Fix both controls: a TRUE adjacent swap (`… + entries[i+2:]`), and make the control mutation SELF-VERIFYING before
   the effect is asserted: `len(moved) == len(entries)`, `sorted(json.dumps(e, sort_keys=True) for e in moved) ==
   sorted(… for e in entries)`, `moved != entries`. Red-first record: with the slice still wrong, the new length assertion
   must FAIL (paste the line); then the fix → green.
2. Add `test_golden_two_async_records_in_opposite_raw_orders_normalize_identically` (kills M8): from the real run-1
   entries build two lists with TWO async `session_info_update` records whose NORMALIZED lines differ (different KEY
   sets — the shape normalizer maps values to types, so two records that differ only in values normalize identically and
   the sort is a no-op; give record B an extra key, e.g. `title`), raw order A,B in one list and B,A in the other:
   `normalize_timeline` must return the IDENTICAL list for both. Then the same property through `check_golden`: build a
   two-leg golden dir from the `bundle` fixture (run-1 A,B; run-2 B,A; seq/tee re-synced as the fixture helpers do),
   regenerate its golden.jsonl from run-1, `monkeypatch.setattr(cc, "PINNED_GOLDEN_SHA256", <its sha>)` (the pattern
   of `test_golden_frozen_lines` T:1872) → `cc.check_golden(dir)` must NOT raise.
3. Add `test_golden_non_async_kind_order_binds_through_check_golden` (kills M4): the same two-leg construction, run-2's
   `usage_update` converted to `tool_call` in BOTH runs and TRUE-swapped with its neighbour in run-2 only →
   `cc.check_golden` MUST raise `golden mismatch between run-1 and run-2 at normalized line N` (paste N).
4. Mutation audit, on SCRATCH copies of C/P (never the tree): re-run the verifier's M1-M8 exactly (the table in
   VERIFY-VB-F12 §V5) — EVERY mutant must now be KILLED by a NAMED test; paste the table (mutant · test · the failing
   assertion line). M4 and M8 must die by the tests of items 1-3, not only by `test_real_bundle_passes_every_check`.
5. De-vacuous each new assertion (one character of an expected value → red at its own assert → restore); paste.

## Boundary
T only. C, P, `proofs/S0-01/evidence/golden/golden.jsonl`, `tests/test_s0_01_spec_runner.py` and every other file:
BYTE-IDENTICAL to the PIN (`git status --porcelain` lists exactly T + your report). A production change you believe
necessary is a FINDING to report, never a fix here.

## Gate (paste every line verbatim; each call under Hermes's 420 s terminal cap)
- `export S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`;
  `/home/rocco/venv-agent-factory/bin` first on PATH; `mkdir -p ../scratch/bt` (pytest creates only the LAST component).
- `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/bt/<run> tests/test_s0_01_check_acp_conformance.py
  tests/test_s0_01_spec_runner.py` TWICE on the final bytes (expected `N passed`, ZERO failed/xfailed);
  `python -m pyflakes tests/test_s0_01_check_acp_conformance.py` (rc 0); `python3 scripts/ap_screen.py --tests
  tests/test_s0_01_check_acp_conformance.py` (paste the last line); `sha256sum tests/test_s0_01_check_acp_conformance.py`
  (FILE IDENTITY) + `git diff --quiet <PIN> -- proofs/S0-01/` (rc 0, paste).
- CODE INTEL FIRST: `graft skeleton` / `graft ask` before any whole-file read (T is >6,000 lines — read by range).
  `report_lint` gates on a FLOOR (`--min-refs 10`); apply its `fix:` hints for at most THREE rounds, then paste and
  finish; paste its summary as PLAIN text.
- Attack through SCRATCH COPIES only; never git-restore/stash/checkout the shared tree; never `git add/commit/push`;
  never touch the corpus, the model server, any unit or another lane's tree.

## Report shape (DATA)
FILE IDENTITY · the red-first lines (item 1's length assertion red, items 2-3 red against M8/M4 scratch mutants, then
green) · the M1-M8 table · the de-vacuous lines · the two pytest summary lines · pyflakes/ap_screen lines ·
DISCREPANCIES · NOT-done · GATE RECOMMENDATION (a proposal; the coordinator grades and a targeted re-verify follows).
