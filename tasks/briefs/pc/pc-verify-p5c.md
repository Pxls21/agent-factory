# PC continuation — VERIFY-P5c (the adversarial grade of S0-01 PC capture tools round 3, the landing a91f256)

PIN: a91f256

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

## CONTINUATION (read second)
This lane is the FIRST run of the grade — nothing precedes it; start at item 0.

**The brief governs**: `tasks/briefs/s0-01-p5c-support/VERIFY-P5c-brief.md` — READ IT WHOLE and follow it item by item (0-11). Your
worktree IS `git archive a91f256` plus the lane patch (the brief + this file); the lane's report
`tasks/briefs/s0-01-p5c-support/P5c-report.md`, `P5c-BLOCKERS.md`, the two amendments, the P5c lane brief, VERIFY-P5b's report and the
pack `tasks/briefs/s0-01-p5c-support/VERIFY-P5c-pack.md` are IN the archive or the patch. Save your report at
`tasks/briefs/s0-01-p5c-support/VERIFY-P5c-report.md` inside your tree, draft after EACH item (the incremental rule), and return it
whole as your final message.

Venue notes specific to this grade:
- You are on the PC: run `tests/test_s0_01_pc_tools.py tests/test_s0_01_pc_post_scan.py` directly (expect `124 passed`), then the joint
  S0-01 set (`tests/test_s0_01_*.py`, `-n 8`, the floor `1556 passed, 9 xfailed`), with the venue exports
  (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`);
  `/home/rocco/venv-agent-factory/bin` FIRST on PATH; a SHORT absolute `--basetemp` under your lane's scratch dir; ONE foreground call
  per run, twice, counts pasted verbatim.
- The real corpus `/home/rocco/s0-01-pinned/realleg/golden` is READ-ONLY: every sweep and every mutation runs on a COPY of a leg under
  your scratch dir (`cp -a`), never in place. You never launch buzz-acp, hermes-acp, Hermes, the tee or the relay; `pc_launch.py` is
  exercised only through `--help` and its argv validation as a subprocess.
- Every FIFO/hang probe under `timeout` and standalone, never through pytest; the 1 GiB gzip-bomb row of item 1 is REASONED, never
  decompressed on this host.
- Any other Stage 0 lane sharing this host: never touch its tree, `proofs/`, or `tests/test_s0_*` outside your own private copy; every
  mutant on a scratch copy of your archive; kill only what you start, by pid.
