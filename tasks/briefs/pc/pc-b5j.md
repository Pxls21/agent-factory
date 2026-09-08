# PC continuation — lane B5j (S0-01 frame tee round 15: both halves derived, the sentence rule, every mention of the pipe pinned, the zombie branch asserted, the OSError guard tested)

PIN: 246bec7

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the original brief.

## CONTINUATION (read second)
This lane CONTINUES sandbox lane B5j, which the sandbox's model quota stopped on 2026-09-08 at ~05:18Z. Its last words were
"Now the two-run sandbox gate in one foreground call." — it believed its edits complete and had not yet run its gate; no report
exists. Its partial work is ALREADY APPLIED on your worktree as the lane patch (`git status --porcelain` lists the files: the
predecessor's edits to `proofs/S0-01/tools/frame_tee.py` and `tests/test_s0_01_frame_tee.py`, plus the sibling S0-01 lanes'
uncommitted files). Treat them as a predecessor's DRAFT: verify every design item of the original brief against the bytes,
finish what is missing, run the gate on the FINAL bytes, and write the report from scratch.

**The original brief governs** (scope, the pinned design, gates, mutants, report discipline):
`tasks/briefs/s0-01-b5j-tee-the-halves-derived-the-sentence-rule-every-mention-of-the-pipe.md` — READ IT WHOLE. This round's
contract, the verifier's report, is shipped in the patch at `tasks/briefs/s0-01-b5j-support/VERIFY-B5i-report.md`. Gate with
`-r 246bec7` (the tee's last checkpoint `75998e7` is an ancestor; the two files are unchanged at the PIN). The hang probes stay
standalone and watchdogged — never a hang shape through pytest. Scope stays exactly the original brief's two files plus the
report `tasks/briefs/s0-01-b5j-support/B5j-report.md`.
