NOT-READY — F1 is a reproducible, in-boundary blocker: existing controls miss both a widened async closed set and removed async sort.

Report: `tasks/briefs/s0-01-vb-f12-support/VERIFY-VB-F12-report.md`  
SHA256: `e6750c4a866d9052c542a2b79fa9e0b96c8d2c484ee5a7ef79628cf3e66fb1be`

Verified:
- Clean current bytes: 476 passed twice under xdist.
- Ledger integrity: S0-01 PRESENT.
- Mint output hashes, evidence manifests, receipts, negative-leg identity/error, and ledger generation reproduce.
- Real checker CLI mutations validate payload/count/session binding.

Blocker:
- `tests/test_s0_01_check_acp_conformance.py:2023-2026` and `:2051` duplicate the adjacent entry instead of swapping it (`entries[idx+1:]` vs required `entries[idx+2:]`).
- M4 widening `ASYNC_SESSION_UPDATES` to `tool_call` survives the full 476-test suite and accepts forbidden reordering on the real checker path.
- M8 removing the async-line sort survives the full suite and rejects a valid two-async opposite-order capture on the real checker path.

Follow-ups:
- Double `negative: observed: observed:` prefix is cosmetic.
- Decision (a) lacks a decision-log/breakdown entry.

`report_lint`: 38 refs — OK 36, NEAR 2, MISS 0.
