# PC lane — M3 (S0-06 round 3: exact manifests, every leaf graded, the C6 truth, the raw origin bound, the query text scrubbed)

PIN: 038bc9b

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-06-m3-four-scope-exact-manifests-every-leaf-graded-the-c6-truth-the-raw-origin-bound.md` —
READ IT WHOLE and build items 1-9 in order. Your worktree IS `git archive 038bc9b`: VERIFY-M2's report, the M2 report and the M2
brief are in the tree at the paths the brief names. Save your report at `tasks/briefs/s0-06-support/M3-report.md` inside your tree,
draft after EACH item (the incremental rule), and return it whole as your final message.

Venue notes specific to this build:
- No real ai-memory: never build, clone, seed or start one (the venue rule); the loopback collector-shape exercise VERIFY-M2 ran is
  allowed (a local stub HTTP listener you start and stop by pid) to derive the 48-leaf shape — say so in the report as a SHAPE
  instrument, never as a substrate run.
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH for every pytest run; an absolute `--basetemp` under your lane's scratch dir.
- Every FIFO/symlink probe standalone under `timeout` with a PID-scoped watchdog, never through pytest.
