# PC continuation — lane A5k (S0-01 checker round 13: the consumer of the pinned list, the v2.4 header, the CK12 blockers)

PIN: 545a9ff8

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the original brief.

## CONTINUATION (read second)
This lane CONTINUES PC lane A5k. Its first Hermes session worked for five hours (04:03Z-08:10Z on 2026-09-08) and ended on
the route's capacity refusal, not on its own decision; a second fresh session then refused to build because
`proofs/S0-01/pins.py` no longer matched the original brief's P5a identity — that difference IS the first session's edit,
not corruption. Its work is ALREADY APPLIED on your worktree as the lane patch (`git status --porcelain` lists 17 files: lane
P5a's seven PC-tool files exactly as the original brief pins them, the first session's edits to `check_acp_conformance.py`,
`check_initialize.py`, `negative_contract.py`, `pins.py` and the four test files, plus three shipped documents). Treat every
edit as the predecessor's DRAFT: verify its premises and claims by RUN, finish the original brief, re-run every gate on the
FINAL bytes.

The predecessor's report draft, written at 06:31Z with two sections finished ("PIN and premise evidence", "presence-gated
class"), is at `tasks/briefs/s0-01-a5k-support/A5k-draft-0631Z.md` — its claims are unverified until you re-run them.

**The original brief governs**: `tasks/briefs/s0-01-a5k-checker-consumer-of-the-pinned-list-v24-header-ck12-blockers.md`
— READ IT WHOLE, with these corrections:
- Its P5a identity table (`pins.py` `974b86f2445d239f`, `pc_post.sh` `8db8caeaf5e56f28`, …) describes the tree BEFORE the
  predecessor's edits. Do NOT re-check it and stop: `pc_post.sh` still matches; `pins.py` differs because the predecessor
  edited it on top of P5a's bytes. The check is satisfied by construction of the patch.
- It cites the verifier's report at `tasks/briefs/s0-01-a5j-support/verify-CK12.md` — that path never existed (the file
  there is the VERIFY-CK12 *brief*). The REPORT, this round's contract, is shipped in the patch at
  `tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md`. Read it whole before any edit; the predecessor may have worked
  from the brief instead — re-derive every blocker from the report.
- It cites `tasks/briefs/s0-01-p5a-support/P5a-report.md` — shipped in the patch at that path.
- `bash scripts/realleg_sync.sh check` is a SANDBOX bridge tool (VENUE-MAP): the corpus here is
  `/home/rocco/s0-01-pinned/realleg/golden`, exported as `S0_01_REAL_LEG_DIR` with `S0_01_VENUE=pc`; the checker's
  real-leg tests read it directly.
Gate with `-r 545a9ff8` (the original brief's PIN; the lane patch supplies P5a's files and the predecessor's edits).
Scope stays exactly the original brief's files plus the report `tasks/briefs/s0-01-a5k-support/A5k-report.md`; the P5a
files in the patch are context, never yours to edit.
