# PC lane — P5c (S0-01 PC capture tools round 3: every required artifact validated, the header strict, the idiom table as data, the S0-02 env extension)

PIN: 3614dc9

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-p5c-pc-tools-every-required-artifact-validated-the-header-strict-the-s0-02-env-extension.md`
— READ IT WHOLE and build items 1-10 in order. Your worktree IS `git archive 3614dc9`: VERIFY-P5b's report, the P5b brief and report
and the S0-02 runner are in the tree at the paths the brief names. Save your report at
`tasks/briefs/s0-01-p5c-support/P5c-report.md` inside your tree, draft after EACH item (the incremental rule), and return it whole
as your final message.

Venue notes specific to this build:
- The real v2.2 corpus for the empty/malformed sweep: copy `/home/rocco/s0-01-pinned/realleg/golden/run-1` under your scratch dir per
  probe; NEVER write into the golden tree. Venue exports `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`.
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; an absolute `--basetemp` under your lane's scratch dir; the joint S0-01 set is
  long (about 3-4 minutes with `-n 8`) — run it ONCE in the foreground, paste it.
- No live buzz-acp / hermes-acp / Hermes / tee / relay / model execution; lane N5j is editing the probe in its own tree — never touch
  `acp_probe.py` or its test.
