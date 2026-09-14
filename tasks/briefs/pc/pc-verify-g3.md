# PC continuation — VERIFY-G3 (the adversarial grade of S0-08 round 3, the landing 7f60d83)

PIN: 7f60d83

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

## CONTINUATION (read second)
This lane is the FIRST run of the grade — nothing precedes it; start at item 0.

**The brief governs**: `tasks/briefs/s0-08-support/VERIFY-G3-brief.md` — READ IT WHOLE and follow it item by item (0-11). Your
worktree IS `git archive 7f60d83` plus the lane patch (the brief + this file); the lane's report `tasks/briefs/s0-08-support/G3-report.md`,
the G3 lane brief, VERIFY-G2's report and the pack `tasks/briefs/s0-08-support/VERIFY-G3-pack.md` are IN the archive or the patch. Save
your report at `tasks/briefs/s0-08-support/VERIFY-G3-report.md` inside your tree, draft after EACH item (the incremental rule), and
return it whole as your final message.

Venue notes specific to this grade:
- You are on the PC: run `tests/test_s0_08_containment.py` directly, then the five-file set the brief names, with the venue exports
  (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`);
  `/home/rocco/venv-agent-factory/bin` FIRST on PATH; a SHORT absolute `--basetemp` under your lane's scratch dir; ONE foreground call
  per run (the coordinator's counts: `145 passed` for the file, the lane's `224 passed` for the five), twice, counts pasted verbatim.
- **NO podman on this host, in any form** — no `podman build`, `run`, `exec`, `volume`, `inspect`; `run_containment.sh` is graded by
  READING, never by running (lane G3's accidental 30 s build is the warning, its report §3). A gVisor cell, only if an item needs one:
  `/usr/local/bin/runsc --rootless do` on a scratch dir under `timeout`, killed by pid.
- The pinned checkout `/home/rocco/s0-01-pinned/hermes-agent` is READ-ONLY (`git -C … show`/`grep` only). The crun fixture's negative
  control runs through the real checker on your archive copy.
- Any other Stage 0 lane sharing this host: never touch its tree, `proofs/`, or `tests/test_s0_*` outside your own private copy; every
  mutant on a scratch copy of your archive; kill only what you start, by pid.
