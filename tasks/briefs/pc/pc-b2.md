# PC continuation — lane B2 (S0-02 round 2: the scan whole, the receipt kept, the removal before the delivery, the level-aware canary, the neg-not-allowlisted leg)

PIN: 246bec7

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the original brief.

## CONTINUATION (read second)
This lane CONTINUES sandbox lane B2, which the sandbox's model quota stopped on 2026-09-08 at ~05:18Z, minutes after it started
editing. Its last words were "Given the file's length and complexity, let me apply the needed test changes surgically." — expect
HALF-APPLIED work: the fixtures for the `neg-not-allowlisted` leg exist in both synthetic bundles, the checker and the test may
carry partial edits. Its partial work is ALREADY APPLIED on your worktree as the lane patch (`git status --porcelain` lists the
files; diff each against the PIN before trusting it). No report exists. Treat all of it as a predecessor's DRAFT: verify its
premises, finish the original brief's twelve items, run the gates on the FINAL bytes, write the report from scratch.

**The original brief governs**:
`tasks/briefs/s0-02-b2-buzz-authz-the-scan-whole-the-receipt-kept-the-removal-before-the-delivery.md` — READ IT WHOLE. This
round's contract, the verifier's report, is shipped in the patch at `tasks/briefs/s0-02-support/VERIFY-B1-report.md` (the
original brief cites it at a sandbox scratchpad path). The original brief's PIN `6cf9179` and this PIN carry identical S0-02
bytes — gate with `-r 246bec7`. The pinned buzz source is `/home/rocco/s0-01-pinned/buzz` (export `S0_02_BUZZ_SRC` to it; the
test's default is the sandbox path).

No relay delivery, no live leg, no membership write on this host — the live legs are the coordinator's. The relay's key and
the NIP-98 identities are never read or printed beyond the test identities' pubkeys. Scope stays exactly the original brief's
files plus the report `tasks/briefs/s0-02-support/B2-report.md`.
