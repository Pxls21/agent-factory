# PC lane — A5m (S0-01 checker round 15: the exclusivity pin, the valid mutant driver, VERIFY-CK14's F1/F2 closed)

PIN: 1231624

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`, `HERMES_REASONING=ultra`) — the one
local slot holds VERIFY-N5k; D-028's local default resumes when the slot frees, the route changes nothing in the brief. Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-a5m-checker-the-exclusivity-pin-and-the-valid-mutant.md` — READ IT WHOLE and build
items 1-6 in order. Your worktree IS `git archive <PIN>` plus the lane patch (the brief, this file, the pack
`tasks/briefs/s0-01-a5m-support/A5m-pack.md`, the VERIFY-CK14 report `tasks/briefs/s0-01-a5l-support/VERIFY-CK14-report.md`);
A5l's report, its `mutants.sh` and `red-before.patch` are IN the archive. Save your report at
`tasks/briefs/s0-01-a5m-support/A5m-report.md` inside your tree, draft after EACH item (the incremental rule), and return it
whole as your final message. Your driver goes beside it.

Venue notes specific to this build:
- Venue exports `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`; the golden corpus is READ-ONLY and
  has FIVE legs (no `run-2` — the coordinator's, not yours). `/home/rocco/venv-agent-factory/bin` FIRST on PATH; an absolute
  `--basetemp` under your lane's scratch dir.
- Hermes's `terminal` tool caps ONE call at 420 s on this host: the checker file ONLY with `-n 8` (serial is ~680 s and dies at
  the cap — VERIFY-CK14's first call did exactly that), every gate ONE foreground call, never backgrounded.
- `scripts/pc_suite.sh set-id -- <files>` works without the bridge; paste its line beside every count.
- VERIFY-N5k runs in its own tree on this host on the local model: never touch its files, never touch the `qwen-builder` unit.
