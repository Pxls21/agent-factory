# PC lane — O3 (S0-03 round 3: the collector complete over the window, the credential screen recursive, the terminal call exact and ordered, pid bound, aware instants, POST on both rows)

PIN: 887f341

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-03-o3-omniroute-the-collector-complete-the-screen-recursive-the-call-exact.md` — READ IT
WHOLE and build items 1-9 in order. Your worktree IS `git archive <PIN>`: VERIFY-O2's report (`tasks/briefs/s0-03-support/VERIFY-O2-report.md`),
the O2 brief and report are in the tree. Save your report at `tasks/briefs/s0-03-support/O3-report.md` inside your tree, draft
after EACH item (the incremental rule), and return it whole as your final message.

Venue notes specific to this build:
- This host RUNS the owner's OmniRoute (:20128) and the owner's Hermes profiles. You do NOT send OmniRoute a single request, do not
  read its key file or its call_logs database, and do not touch `~/.hermes/`. Every SQLite database you query is a temporary one
  you created; every HTTP server is a loopback one the tests start and stop.
- Venue exports `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`;
  `/home/rocco/venv-agent-factory/bin` FIRST on PATH; an absolute `--basetemp` under your lane's scratch dir; the four-file gate
  runs about a minute with `-n 8` — ONE foreground `lane_gate.sh` call, pasted.
- The live legs A/B/negative are the coordinator's, run later over the bridge; your job is the checker, the collector, the runner's
  bytes, the fixtures and their tests. `proofs/S0-01/*` is read-only (P5c, N5j, B5k, D5n are editing S0-01 in their own trees).
