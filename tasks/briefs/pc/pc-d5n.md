# PC lane — D5n (S0-01 scripted backend round 17: one atomic open-validate-write primitive, the drain bounded, the evasions documented, one cost table)

PIN: 887f341

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-d5n-backend-one-atomic-write-primitive-the-drain-bounded.md` — READ IT WHOLE and build
items 1-9 in order. Your worktree IS `git archive <PIN>`: VERIFY-D5m's report (`tasks/briefs/s0-01-d5m-support/VERIFY-D5m-report.md`),
the D5m brief and report are in the tree. Save your report at `tasks/briefs/s0-01-d5n-support/D5n-report.md` inside your tree,
draft after EACH item (the incremental rule), and return it whole as your final message.

Venue notes specific to this build:
- Venue exports `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`; `/home/rocco/venv-agent-factory/bin`
  FIRST on PATH (pyflakes from that venv, never `compileall` in its place); an absolute `--basetemp` under your lane's scratch dir.
- The two-file gate runs about 3 minutes with `-n 8` — ONE foreground `lane_gate.sh` call, pasted.
- Every FIFO / race / drain probe standalone under `timeout 12` with your own watchdog that kills your helper by pid. The owner's
  production backend is running on :20201 — you never touch it, never bind its port, never read its token file; every backend you
  start is yours, on an ephemeral port, killed by the pid you recorded.
- Lanes N5j (the probe), B5k (the tee), P5c (the PC tools) and VERIFY-CK13 (the checker) are working in their own trees — never
  edit `acp_probe.py`, `frame_tee.py`, `pins.py`, `check_acp_conformance.py` or the PC tools.
