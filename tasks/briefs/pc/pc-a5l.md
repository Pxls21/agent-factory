# PC lane — A5l (S0-01 checker round 14: the ONE list consumed, the scanner domains closed, the sets pinned, the survivors killed by name, VB-F12 strict, the driver and red-befores committed)

PIN: d23762a

(RE-PINNED 2026-09-15 07:5xZ from a91f256: the three boundary files — `proofs/S0-01/tools/check_acp_conformance.py`,
`tests/test_s0_01_check_acp_conformance.py`, `proofs/S0-01/tools/pins.py` — are byte-identical between the two pins (`git log
a91f256..d23762a -- <them>` is empty); the newer pin gives this lane the ported `.hermes.md` (the full build loop, the
environment quirks, the code-intel quartet section) and the current scripts. ROUTE: this lane runs on the CLOUD build route
(`HERMES_MODEL=agentfactory-build`, `HERMES_REASONING=ultra`) because the one local slot holds VERIFY-N5k; D-028's local
default (`agentfactory-build-local`, `medium`) resumes when the slot frees — the route changes nothing in the brief.)

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-a5l-checker-the-one-list-consumed-the-scanner-domains-closed-the-sets-pinned.md` — READ
IT WHOLE and build items 1-11 in order. Your worktree IS `git archive <PIN>` plus the lane patch (this file and the
code-intel pack `tasks/briefs/s0-01-a5l-support/A5l-pack.md` — graft skeletons, the graft ask, GitNexus impact, crg
callers/tests, ripwire callers + test-gate and the registry screen over the three boundary files; START FROM IT, the
CODE INTEL FIRST rule): VERIFY-CK13's report (`tasks/briefs/s0-01-a5k-support/VERIFY-CK13-report.md`), the A5k brief and
report, and the governing brief with its AMENDMENT are in the archive. Save your report at
`tasks/briefs/s0-01-a5l-support/A5l-report.md` inside your tree, draft after EACH item (the incremental rule), and return it
whole as your final message. Your mutant driver and red-before patch go beside it (item 10).

Venue notes specific to this build:
- Venue exports `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`; the golden corpus is READ-ONLY —
  copy a leg under your scratch dir per probe. `/home/rocco/venv-agent-factory/bin` FIRST on PATH (pyflakes from that venv);
  an absolute `--basetemp` under your lane's scratch dir; the four-file gate is about 3 minutes with `-n 8` — ONE foreground
  `lane_gate.sh` call, pasted; the headline and four-file xdist counts likewise ONE foreground call each.
- `pins.py` at your PIN is P5c-c's LANDED file (the per-file constraint table): you read it, you never edit it (the brief says
  what to do if a shared function is missing — stop and report). VERIFY-N5k (the probe's verify round) runs in its own tree
  on this host on the local model; never touch its files, never touch the `qwen-builder` unit.
- No live buzz-acp / hermes-acp / Hermes / tee / relay / model execution; the owner's services on this host are never touched.
