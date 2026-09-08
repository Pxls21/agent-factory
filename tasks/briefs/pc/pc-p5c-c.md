# PC lane — P5c-c (S0-01 PC capture tools round 3, CONTINUED after the second item-1 blocker: the constraint table is version-aware, measured from the real corpus)

PIN: 3614dc9

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

## CONTINUATION (read second)
This lane CONTINUES lanes P5c and P5c-b, which each stopped correctly at item 1: first on the two zero-byte completion markers
(AMENDMENT 1), then on the two v2.2 scan files that are validly empty in the real corpus (AMENDMENT 2). READ, IN THIS ORDER:
`tasks/briefs/s0-01-p5c-support/P5c-AMENDMENT-2.md` (item 1 as it now stands: a constraint that is a function of
`(version, name)`, the kinds `utf8-text-maybe-empty` and `scan-headed`, the invalid mutation defined per (version, file), the
v2.2 sweep on the real `run-1` copy plus the `shutdown` copy untouched, the v2.4 sweep on a synthetic v2.4 leg; the corpus
measurement table it is grounded on), then `P5c-AMENDMENT-1.md` (the marker kind — still in force), then the original brief
`tasks/briefs/s0-01-p5c-pc-tools-every-required-artifact-validated-the-header-strict-the-s0-02-env-extension.md` for items 2-10.
The two blocker reports are in your tree at `tasks/briefs/s0-01-p5c-support/P5c-report.md` (the second embeds the first); keep
them as the final report's "Blocker (resolved by AMENDMENT 1)" and "Blocker (resolved by AMENDMENT 2)" sections — their
verified rows are the red-befores for items 1-3. Build item 1 (amended twice) then items 2-10 in order. Your worktree IS
`git archive 3614dc9` plus the lane patch (the brief, both amendments, the blocker report, this file). Save your report at
`tasks/briefs/s0-01-p5c-support/P5c-report.md` inside your tree, draft after EACH item (the incremental rule), and return it
whole as your final message.

If you measure anything on the PC that differs from AMENDMENT 2's corpus table, STOP and report the difference — never widen a
kind to fit.

Venue notes specific to this build:
- The real v2.2 corpus for the sweep: copy `/home/rocco/s0-01-pinned/realleg/golden/run-1` (and `shutdown` for the empty
  after-scan case) under your scratch dir per probe; NEVER write into the golden tree. Venue exports
  `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`.
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH (pyflakes from that venv); an absolute `--basetemp` under your lane's scratch
  dir; the joint S0-01 set is long (about 3-4 minutes with `-n 8`) — run it ONCE in the foreground, paste it.
- No live buzz-acp / hermes-acp / Hermes / tee / relay / model execution. Lanes N5j (the probe), B5k (the tee), D5n (the backend),
  O3 (S0-03), B3 (S0-02) work in their own trees — never touch `acp_probe.py`, `frame_tee.py`, `scripted_backend.py`,
  `check_acp_conformance.py`, anything under `proofs/S0-02/` or `proofs/S0-03/`, or their tests. `pins.py` IS yours this round
  (the constraint table lives there); lane A5l reads it and is queued behind you.
