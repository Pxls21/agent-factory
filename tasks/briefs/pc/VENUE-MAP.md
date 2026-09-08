# VENUE MAP — a lane that runs ON the owner's PC (read before the original brief)

Every PC continuation brief under `tasks/briefs/pc/` includes this file by reference. It maps the sandbox venue the original
brief was written for onto this host. Where the two disagree, THIS file wins on venue facts; the original brief wins on scope,
design, gates and report discipline.

- You are user `rocco`, uid 1000, with NO root and NO sudo. Never ask for it. A step that needs root is NOT run here — say so
  first-class in the report.
- Interpreter: `/home/rocco/venv-agent-factory/bin/python` (3.11) — every place the original brief says
  `/root/venv-agent-factory/bin/python`.
- Export on EVERY pytest and `scripts/lane_gate.sh` run:
  `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`
  (the sandbox brief's `/root/s0-01-realleg/golden` and `/home/user/nerdherderdani/buzz` map to these). `scripts/test_summary.sh`
  declares the SANDBOX defaults, so export the PC values before calling `scripts/lane_gate.sh` — it inherits them.
- Pinned checkouts on this host, READ-ONLY: hermes-agent `/home/rocco/s0-01-pinned/hermes-agent`, buzz `/home/rocco/s0-01-pinned/buzz`,
  buzz-acp `/home/rocco/s0-01-pinned/acp`. There is NO pinned ai-memory checkout and NO pinned OmniRoute checkout here: a derivation
  the original brief asks you to read from `crates/…` or from the OmniRoute source is cited from the predecessor's report and the
  committed vendored files, and stated NOT re-verified on this host.
- Your tree is the lane worktree you start in (`.lanes/<lane>/tree`, detached at the PIN, with the lane patch applied and STAGED —
  `git status --porcelain` lists the predecessor's files). Scratch: create `../scratch` beside the tree (`.lanes/<lane>/scratch/`) and
  use it for `LANE_GATE_DIR`, every `--basetemp`, every mutant copy. Every sandbox scratchpad path in the original brief
  (`/tmp/claude-0/…/scratchpad/…`) maps there. `scripts/lane_gate.sh -r <PIN> -f "<files>" -t "<tests>" -n 2` works from your tree
  (it archives the PIN and copies your working-tree files over it) — ONE foreground call per gate.
- NO bridge tools: `scripts/pc.sh`, `scripts/pc_suite.sh`, `scripts/pc_lane.sh`, `scripts/realleg_sync.sh` are the SANDBOX's way onto
  this host — never call them here.
- Never touch the owner's running servers (OmniRoute on :20128, the Buzz relay stack, Ollama, Phoenix, OpenObserve, neo4j), the Hermes
  profiles under `~/.hermes/`, or the main clone `/home/rocco/agent-factory` outside your own lane directory. Never
  `git commit`, `push`, `stash`, `checkout`, `reset` or `add` — the coordinator harvests your worktree's diff when you finish.
- No live model requests, relay deliveries or evidence captures — those legs are the coordinator's. Never read, print or copy the
  OmniRoute key, any `~/.hermes/profiles/*/.env`, or any credential.
- Processes: kill only what you start, by pid (never `pkill`/`pgrep -f`); long gates in ONE foreground call; podman and runsc only
  where the original brief's design requires them (build lanes: never). `kernel.dmesg_restrict=1` here and you are unprivileged.
- Report: the standing incremental rule applies (append each finished section to `$LANE_REPORT_DRAFT`). Your FINAL message is the
  whole report, in the shape the original brief demands — FILE IDENTITY of the final bytes, red-before/green-after, the mutant table
  with a killer line per mutant, the class sweep, `report_lint` MISS 0 run LAST, the gate RESULT lines pasted verbatim, DISCREPANCIES,
  NOT-done first-class, the process census, hygiene. Also write it to the report path the original brief names, inside your tree.
