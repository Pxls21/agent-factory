# PC continuation — VERIFY-B3 (the adversarial grade of S0-02 round 3, the landing c6c384a)

PIN: c6c384a

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

## CONTINUATION (read second)
This lane is the FIRST run of the grade — nothing precedes it; start at item 0.

**The brief governs**: `tasks/briefs/s0-02-support/VERIFY-B3-brief.md` — READ IT WHOLE and follow it item by item (0-12). Your
worktree IS `git archive c6c384a` plus the lane patch (the brief + this file); the lane's report `tasks/briefs/s0-02-support/B3-report.md`,
the B3 lane brief, VERIFY-B2's report and the pack `tasks/briefs/s0-02-support/VERIFY-B3-pack.md` are IN the archive or the patch. Save
your report at `tasks/briefs/s0-02-support/VERIFY-B3-report.md` inside your tree, draft after EACH item (the incremental rule), and
return it whole as your final message.

Venue notes specific to this grade:
- You are on the PC: run `tests/test_s0_02_buzz_authz.py` directly with the venue exports
  (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`);
  `/home/rocco/venv-agent-factory/bin` FIRST on PATH; a SHORT absolute `--basetemp` under your lane's scratch dir; ONE foreground call
  per run (the coordinator's PC count for this file: `137 passed`), twice, counts pasted verbatim.
- The pinned Buzz source `/home/rocco/s0-01-pinned/buzz` is READ-ONLY: every regex attack of item 5 runs on a scratch COPY of the one
  file. You never deliver to the live relay, never write relay membership, never read a role key; every key of item 3 is a throwaway
  you mint on scratch and never print.
- Every FIFO/hang probe under `timeout` and standalone, never through pytest.
- Any other Stage 0 lane sharing this host: never touch its tree, `proofs/`, or `tests/test_s0_*` outside your own private copy; every
  mutant on a scratch copy of your archive; kill only what you start, by pid.
