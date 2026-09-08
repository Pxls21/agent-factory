# PC lane — N5j (S0-01 probe round 13: open-validate-truncate, the framedir owned, the receivers inventoried, the ≥40 campaign)

PIN: 99b7b37

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-n5j-probe-open-validate-truncate-the-framedir-owned-the-receivers-inventoried.md` —
READ IT WHOLE and build items 1-8 in order. Your worktree IS `git archive 99b7b37`: VERIFY-N5i's report, the N5i brief and report
and VERIFY-N5g-b's report are in the tree at the paths the brief names. Save your report at
`tasks/briefs/s0-01-n5j-support/N5j-report.md` inside your tree, draft after EACH item (the incremental rule), and return it whole
as your final message.

Venue notes specific to this build:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; the venue exports `S0_01_VENUE=pc
  S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`; an absolute `--basetemp` under your lane's scratch dir.
- Every hostile-path rig (hardlink, symlinked parent, FIFO with a reader, a UNIX socket) standalone under `timeout` with a
  PID-scoped watchdog, never through pytest; a scratch copy of `git archive 99b7b37` per rig.
- No real agent, Hermes, buzz-acp, relay or credential; the runners under `proofs/S0-01/tools/pc/` are read-only for you.
