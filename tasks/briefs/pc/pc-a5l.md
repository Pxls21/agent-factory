# PC lane — A5l (S0-01 checker round 14: the ONE list consumed, the scanner domains closed, the sets pinned, the survivors killed by name, VB-F12 strict, the driver and red-befores committed)

PIN: 467a88e

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-a5l-checker-the-one-list-consumed-the-scanner-domains-closed-the-sets-pinned.md` — READ
IT WHOLE and build items 1-11 in order. Your worktree IS `git archive <PIN>`: VERIFY-CK13's report
(`tasks/briefs/s0-01-a5k-support/VERIFY-CK13-report.md`), the A5k brief and report are in the tree. Save your report at
`tasks/briefs/s0-01-a5l-support/A5l-report.md` inside your tree, draft after EACH item (the incremental rule), and return it
whole as your final message. Your mutant driver and red-before patch go beside it (item 10).

Venue notes specific to this build:
- Venue exports `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`; the golden corpus is READ-ONLY —
  copy a leg under your scratch dir per probe. `/home/rocco/venv-agent-factory/bin` FIRST on PATH (pyflakes from that venv);
  an absolute `--basetemp` under your lane's scratch dir; the four-file gate is about 3 minutes with `-n 8` — ONE foreground
  `lane_gate.sh` call, pasted; the headline and four-file xdist counts likewise ONE foreground call each.
- `pins.py` is being edited by lane P5c-b in ITS tree right now: you read it, you never edit it (the brief says what to do if a
  shared function is missing — stop and report). Lanes N5j (probe), B5k (tee), D5n (backend) work in their own trees; never
  touch their files.
- No live buzz-acp / hermes-acp / Hermes / tee / relay / model execution; the owner's services on this host are never touched.
