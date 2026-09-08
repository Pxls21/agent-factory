# PC continuation — lane O2 (S0-03 round 2: the identity row bound to the leg, leg B on the real capture path, the negative leg producible)

PIN: 246bec7

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the original brief.

## CONTINUATION (read second)
This lane CONTINUES sandbox lane O2, which the sandbox's model quota stopped on 2026-09-08 at ~05:18Z. Its last words were
"Now fixing the report's citations so report_lint is MISS 0." — it believed the build complete and was correcting its report.
Its partial work is ALREADY APPLIED on your worktree as the lane patch (`git status --porcelain` lists the files: the
predecessor's edits under `proofs/S0-03/` — including deleted and added fixture files — its test, its report draft, plus the
sibling S0-01 lanes' uncommitted files the checker imports). Treat every one of them as a predecessor's DRAFT: verify its
premises, re-run the gates on the FINAL bytes, finish the report (`report_lint` MISS 0 run LAST), re-stamp every FILE IDENTITY
row and every `file:line`.

The predecessor's report draft is at `tasks/briefs/s0-03-support/O2-report.md` — unverified until you re-run its claims.

**The original brief governs**: `tasks/briefs/s0-03-o2-omniroute-the-row-bound-to-the-leg-and-the-real-capture-path.md` — READ
IT WHOLE. This round's contract, the verifier's report, is shipped in the patch at
`tasks/briefs/s0-03-support/VERIFY-O1-report.md`. The original brief pins the sandbox-local revision `218dc2f`; the equivalent
here is this PIN plus the lane patch — gate with `-r 246bec7`.

This host RUNS the owner's OmniRoute (:20128) and the owner's Hermes profiles. You do NOT send OmniRoute a single request, do not
read its key file, and do not touch `~/.hermes/`. The S0-03 capture legs are the coordinator's, run later from the sandbox over
the bridge; your job is the checker, the fixtures, the tools' bytes and their tests. Scope stays exactly the original brief's
files plus the report.
