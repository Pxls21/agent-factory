# PC lane — N5k (S0-01 ACP probe round 14: the two surviving flags made load-bearing, the READ side open-then-fstat, the serial four-file run)

PIN: c6c384a

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-n5k-probe-the-flags-load-bearing-the-read-side-atomic-the-serial-run.md` — READ IT WHOLE and follow it
item by item (1-10). Your worktree IS `git archive c6c384a` plus the lane patch (the brief + this file); VERIFY-N5j's report, the N5j report and the
9d probe bytes are all in the archive. Save your report at `tasks/briefs/s0-01-n5j-support/N5k-report.md` inside your tree, draft after EACH item
(the incremental rule), and return it whole as your final message.

Venue notes specific to this build:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; an absolute `--basetemp` under your lane's scratch dir; venue exports on every pytest run:
  `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`.
- Every FIFO/hang probe standalone under `timeout` with a PID-scoped watchdog — never a hang shape through pytest; kill only what you start, by pid.
- The serial four-file run (item 5) may exceed one tool call's ceiling: split it into two foreground calls, paste both; never background a run and stop.
- No live buzz-acp / hermes-acp / Hermes / tee / relay / model execution; the probe's real leg is NOT run here (F4 is the coordinator's).
- Other lanes may share this host: never touch `proofs/` or `tests/` outside your own private copy; every mutant on a scratch copy of your archive.
