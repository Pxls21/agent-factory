# PC lane — N5n (S0-01 probe round 17: broaden the close-fds AST walker)

PIN: c728be5

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`,
`HERMES_REASONING=ultra`). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/s0-01-n5n-probe-round-17-close-fds-walker.md` — READ IT WHOLE and
build items 1-3 in order. Your worktree IS `git archive <PIN>` plus the lane patch (the two briefs,
this file). Save your report at `tasks/briefs/s0-01-n5l-support/N5n-report.md`, draft after EACH item,
return it whole as your final message.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; `S0_01_VENUE=pc
  S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden` exported before every `scripts/lane_gate.sh`
  run; an absolute, SHORT `--basetemp` under your lane's `../scratch` (AF_UNIX path length).
- Hermes's `terminal` tool caps ONE call at 420 s: the probe file alone runs serial ~1 min — one
  `lane_gate.sh … -n 2` foreground call fits; the driver + self-test in their own calls.
- Other lanes run on this host in their own trees (VERIFY-GOV1 on the local model, plus cloud lanes):
  never touch their files, the `qwen-builder` unit, or any server.
- Attack through SCRATCH COPIES only — never git-restore/stash/checkout the shared tree. CODE INTEL
  FIRST: `graft ask` / `ripwire` before grep. The lint's `fix:` hints apply for at most three rounds,
  then paste and finish.
- The production probe `proofs/S0-01/tools/acp_probe.py` stays BYTE-IDENTICAL unless item 2 surfaces a
  real second launch in it — then surface it, do not edit it to hide it.
