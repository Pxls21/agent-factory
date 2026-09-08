# PC continuation — lane M2 (S0-06 round 2: the leak agent seeded, the oracles scoped, the shapes named, the digest bound to the run)

PIN: 246bec7

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the original brief.

## CONTINUATION (read second)
This lane CONTINUES sandbox lane M2, which the sandbox's model quota stopped on 2026-09-08 at ~05:18Z. Its last words were
"V18 (a NaN hand-edited into a bundle) still passes the checker — closing that at the oracle too." — it was mid-way through its
mutant campaign; no M2 report exists. Its partial work is ALREADY APPLIED on your worktree as the lane patch
(`git status --porcelain` lists the files: the predecessor's edits under `proofs/S0-06/` — adapter, checker, fixtures including
many added files, the PC tools — its test, the F-17 correction inside `tasks/briefs/s0-06-support/M1-report.md` (in scope per
the original brief, ONLY that correction), plus the sibling S0-01 lanes' uncommitted files the checker imports). Treat every one
of them as a predecessor's DRAFT: verify its premises, finish the original brief's design items and the mutant campaign (V18
open), run the gates on the FINAL bytes, write the report from scratch.

**The original brief governs**:
`tasks/briefs/s0-06-m2-four-scope-the-leak-agent-seeded-the-oracles-scoped-the-shapes-named.md` — READ IT WHOLE. This round's
contract, the verifier's report, is shipped in the patch at `tasks/briefs/s0-06-support/VERIFY-M1-report.md`. Gate with
`-r 246bec7`.

There is NO pinned ai-memory checkout on this host: the derivations the original brief asks you to read from
`/home/user/nerdherderdani/ai-memory` (`crates/…`, `scope.rs`) are cited from the predecessor's and VERIFY-M1's reports and
stated NOT re-verified on this host. No ai-memory build or run here (the PC tools under `proofs/S0-06/tools/pc/` are bytes to be
tested statically and with stand-ins, exactly as the original brief says for the sandbox). Scope stays exactly the original
brief's files plus the report `tasks/briefs/s0-06-support/M2-report.md`.
