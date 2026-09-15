# PC continuation — VERIFY-CK14 (the adversarial grade of S0-01 checker round 14, lane A5l's landing)

PIN: b6483df

Role: adversarial-verifier. Route: the CLOUD verify route (`HERMES_MODEL=agentfactory-verify`, `HERMES_REASONING=ultra`) — the one
local slot holds VERIFY-N5k. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

## CONTINUATION (read second)
This lane is the FIRST run of the grade — nothing precedes it; start at item 0.

**The brief governs**: `tasks/briefs/s0-01-a5l-support/VERIFY-CK14-brief.md` — READ IT WHOLE and follow it item by item (0-11).
Your worktree IS `git archive <PIN>` plus the lane patch (the brief, this file, the pack `VERIFY-CK14-pack.md`); the lane's
report `tasks/briefs/s0-01-a5l-support/A5l-report.md`, its `mutants.sh`, `red-before.patch`, the A5l build brief, VERIFY-CK13's
report and `pins.py` are IN the archive. Save your report at `tasks/briefs/s0-01-a5l-support/VERIFY-CK14-report.md` inside your
tree, draft after EACH item (the incremental rule), and return it whole as your final message.

Venue notes specific to this grade:
- The checker lives at `proofs/S0-01/check_acp_conformance.py` (NOT under `tools/`); the build brief's stale `tools/` paths were
  the lane's first discrepancy — the pack and this brief use the real path.
- Hermes's `terminal` tool caps ONE call at 420 s on this host: run the checker suite with `-n 1` twice rather than `-n 2` once;
  the four-file xdist run fits (`-n 4`, ~145 s); the joint set fits on 8 workers (~200 s).
- Venue exports `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`;
  `/home/rocco/venv-agent-factory/bin` FIRST on PATH; a SHORT absolute `--basetemp` under your lane's scratch dir, its parent
  `mkdir -p`'d. The real corpus is READ-ONLY: copy a leg under your scratch dir (`cp -a`) before any mutation. You never launch
  buzz-acp, hermes-acp, Hermes, the tee or the relay.
- Code intel FIRST: the pack is attached; `graft ask` / `graft skeleton` in your tree; `scripts/ripwire_review.sh for|callers|
  impact|edit-check <symbol>` from your TREE's own wrapper (`edit-check` works since the landing — it was dead before it);
  `node /home/rocco/agent-factory/.gitnexus/run.cjs impact "<symbol>" --direction upstream --repo /home/rocco/agent-factory`
  (clone HEAD line numbers); `python3 scripts/ap_screen.py <file>`; `python3 scripts/report_lint.py`. `scripts/lane_context.sh`
  now REFUSES a nonexistent FILE (rc 64) — a pack over a stale path is a hollow pack.
- Other Stage 0 lanes share this host (VERIFY-N5k on the local model): never touch their trees, `proofs/`, or `tests/test_s0_*`
  outside your own private copy; every mutant on a scratch copy of your archive; kill only what you start, by pid.
