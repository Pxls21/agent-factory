# PC lane — G3 (S0-08 round 3: the argv grammar closed, the observer read back, the image measured)

PIN: 488b238

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-08-g3-containment-the-argv-grammar-closed-the-observer-read-back-the-image-measured.md` —
READ IT WHOLE and build items 1-10 in order. Your worktree IS `git archive 488b238`: VERIFY-G2's report, the G2 report and brief and
VERIFY-G1's report are in the tree at the paths the brief names. Save your report at `tasks/briefs/s0-08-support/G3-report.md`
inside your tree, draft after EACH item (the incremental rule), and return it whole as your final message.

Venue notes specific to this build:
- NEVER start, build or exec a container and never run `run_containment.sh` for real; the pinned upstream checkout
  `/home/rocco/s0-01-pinned/hermes-agent` is read-only (cite its Dockerfile lines by number).
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; the venue exports VERIFY-G2 used; an absolute `--basetemp` under your scratch dir.
- Every FIFO/symlink rig standalone under `timeout` with a PID-scoped watchdog, never through pytest.
