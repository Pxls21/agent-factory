# PC continuation — lane D5m (S0-01 backend round 16: the --pidfile guard, the ban by glob, failure-aware waits, the cost sentence)

PIN: 246bec7

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the original brief.

## CONTINUATION (read second)
This lane CONTINUES sandbox lane D5m, which the sandbox's model quota stopped on 2026-09-08 at ~05:18Z. Its last words were
"Now gate run 2." — it believed its edits complete and was on the second run of its gate. Its partial work is ALREADY APPLIED
on your worktree as the lane patch (`git status --porcelain` lists the files: the predecessor's edits to the backend, its main
test, the red-state test and the cost probe, plus the sibling S0-01 lanes' uncommitted files the tests depend on — `pins.py`,
`tests/conftest.py`, the PC tools and their tests, the hook screen). Treat every one of them as a predecessor's DRAFT, not as
ground truth: verify its premises (your role's rule 1), finish the original brief on top of it, and re-run every gate on the
FINAL bytes.

The predecessor's report draft is at `tasks/briefs/s0-01-d5m-support/D5m-report.md` — its claims are unverified until you
re-run them; re-stamp every FILE IDENTITY row and every `file:line` on the FINAL bytes, and re-run its mutant table on scratch
copies (paste the killer lines you observe, never the draft's).

**The original brief governs** (scope, the pinned design, gates, mutants, report discipline):
`tasks/briefs/s0-01-d5m-backend-the-startup-class-closed-the-ban-scoped-by-glob.md` — READ IT WHOLE. This round's contract, the
verifier's report, is shipped in the patch at `tasks/briefs/s0-01-d5m-support/VERIFY-D5l-report.md` (the original brief cites it at
a sandbox scratchpad path). The original brief pins the sandbox-local revision `218dc2f` (= `327c3b3` plus lane P5b's files); the
equivalent here is this PIN plus the lane patch — gate with `-r 246bec7`. Scope stays exactly the original brief's four files plus
the report; the sibling lanes' files in the patch are context, never yours to edit.
