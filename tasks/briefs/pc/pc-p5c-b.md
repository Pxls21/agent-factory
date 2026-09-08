# PC lane — P5c-b (S0-01 PC capture tools round 3, CONTINUED after the item-1 blocker: the constraint table per file, the two markers valid only when empty)

PIN: 3614dc9

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

## CONTINUATION (read second)
This lane CONTINUES lane P5c, which stopped correctly at item 1 with a blocker report: the brief's "every required file emptied →
rc 1, 25/25" contradicted the producer's contract for the two zero-byte completion markers. The coordinator resolved it as
**AMENDMENT 1** — `tasks/briefs/s0-01-p5c-support/P5c-AMENDMENT-1.md` — READ IT FIRST: it replaces item 1 in full (a per-file
constraint kind, the new kind `empty-marker` for `manifest-pre.done` / `manifest-post.done`, the sweep as 25 per-file invalid
mutations: 23 emptied, 2 given one byte). Items 2-10 of the original brief stand unchanged. The blocker report is in your tree at
`tasks/briefs/s0-01-p5c-support/P5c-report.md`: keep it as the report's "Blocker (resolved by AMENDMENT 1)" section and build the
final report on top of it; its verified rows are the red-befores for items 1-3.

**The original brief governs items 2-10**:
`tasks/briefs/s0-01-p5c-pc-tools-every-required-artifact-validated-the-header-strict-the-s0-02-env-extension.md` — READ IT WHOLE.
Build item 1 (amended) then items 2-10 in order. Your worktree IS `git archive 3614dc9` plus the lane patch (the brief, the
amendment, the blocker report, this file). Save your report at `tasks/briefs/s0-01-p5c-support/P5c-report.md` inside your tree,
draft after EACH item (the incremental rule), and return it whole as your final message.

Venue notes specific to this build:
- The real v2.2 corpus for the per-file sweep: copy `/home/rocco/s0-01-pinned/realleg/golden/run-1` under your scratch dir per
  probe; NEVER write into the golden tree. Venue exports `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`.
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH (pyflakes from that venv); an absolute `--basetemp` under your lane's scratch
  dir; the joint S0-01 set is long (about 3-4 minutes with `-n 8`) — run it ONCE in the foreground, paste it.
- No live buzz-acp / hermes-acp / Hermes / tee / relay / model execution. Lanes N5j (the probe), B5k (the tee), D5n (the backend)
  and VERIFY-CK13 (the checker) are working in their own trees — never touch `acp_probe.py`, `frame_tee.py`,
  `scripted_backend.py`, `check_acp_conformance.py` or their tests.
