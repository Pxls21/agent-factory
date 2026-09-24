# JEV LEVERAGE RE-AUDIT — EVIDENCE LANE (task #221, D-069 item 5)

**Role:** evidence-gatherer (Opus 5.5, sandbox). EVIDENCE ONLY (Reflection Firewall): tables with file:line and pasted
command output. No proposals, no verdicts, no root causes. The coordinator writes the synthesis from your tables.

## Why (the owner's ask, 2026-09-24 10:4xZ, paraphrased)
Use "Jev" (the System-1 models: Laya, MoJev; tools jev-pruner, jevcache) for every System-1 action the System-2 models
(Opus, Fable, the Qwen lanes) do today: classify, rank, pick, screen, find context. That wastes compute and tokens, and
context management causes most of our problems. Jev could also find our recurring hiccups and score agent progress.
Everything built here gets copied into the production agent system, so the workflow in this repo is the thing to get right.

## Deliverable
Write ONE file: `docs/research/findings/JEV-LEVERAGE-EVIDENCE-2026-09-24.md` (tables over prose, under ~60 KB).
Header: date, your model, the repo HEAD you read (`git rev-parse --short HEAD`). Do not commit. Write nothing else in the repo.

### E1. What Jev is here (measured, not remembered)
- Laya: model, size, input window, the PC endpoint (loopback 47411): routes and the request/response JSON shape, from the
  code that calls it (`grep -rn 47411`, `grep -rln laya scripts harness-ports src tests`), latency and determinism from
  `docs/research/findings/LAYA-PROBE-1.md`, how the sandbox reaches it (bridge only?).
- MoJev: from `docs/research/findings/MOJEV-AUDIT-2026-09-24.md` (window, output form, limits).
- jev-pruner and jevcache: what they do and where they are wired (`harness-ports/bin/pc-lane.sh`).
- The never-a-gate mechanics: `scripts/no_laya_in_gates.py`, `scripts/gate_files.txt`, KC-J1: exactly what is forbidden.

### E2. The existing Jev roadmap and its state
Tasks #115 (ap-hawk), #116 (drift-hawk), #133 (pijev), #195 (dream-phase triage), canny C1/C2 (#147 to #160; #148 in
progress), J1 (the decision ledger J1-0 to J1-5: what it records, any committed ledger rows, its consumers), PCJ1. For each:
the status text from `todo/BUILD-TASKLIST.md` (grep the slug) and the files that exist.

### E3. System-1 decision inventory
Every place where a classify / rank / pick / route / screen / extract decision is made today:
- project skills `.claude/skills/*/SKILL.md` (build-loop, deep-work, orchestration, anti-hollow-green, session-continuity,
  code-intel-trio, contract-gate, bug-echo, and any other non-vendored project skill);
- hooks `.claude/hooks/*`; scripts under `scripts/` that decide by heuristic (wiki-context keyword matching, ap_screen
  regexes, report_lint, lane_context, ci_gate, decide-harvest grammars, others you find);
- CLAUDE.md standing reflexes that are decisions (route by stage, escalate a tier when..., is this a spine change, is a
  push transcripts-only, which doc is ground truth).
One row per decision: location (file:line), the decision, its inputs, output type (binary / k-way / ranking / extraction),
current mechanism (model judgment / regex / keyword / none), and whether a REAL label source for it exists in the repo
(git history, test outcomes, the incident log, ledger rows, CI runs), with its location. Record; do not recommend.

### E4. Hiccup and quirk corpus
- `docs/INCIDENT-LOG.md` registry: count the AF-AP rows; cluster them into a fixed set of classes you define from the rows
  (for example: stale premise, race/TOCTOU, quoting/escaping, hollow green / weak test oracle, tooling quirk,
  coordination/process, secret handling); counts and example ids per class; which rows have a mechanical screen
  (AP_SCREEN / TEST_SCREEN in `.claude/hooks/edit-snapshot.py`) and which do not.
- CLAUDE.md quirk lines ("bit 2026-..."): count and classes.
- This session's transcript `/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl`: parse it with
  a python script (NEVER read it whole; stream it line by line): tool calls by tool name; tool results marked as errors,
  clustered by the first ~60 characters of their text; counts of harness reminder types (the "hasn't heard from you"
  reminder, Stop-hook feedback, task-tool reminders); compaction count; file size. Paste the script and its output.

### E5. Context-cost evidence
From the same transcript: total bytes of tool results by tool name, and the 15 largest tool results (tool name + the
first 40 characters of the command or file path, and the byte size; never the content).

### E6. What gets copied to production
The paths that hold the workflow (skills, hooks, scripts, harness-ports roles and adapters) and which of them E3's decisions
live in.

## Constraints (standing)
- Read-only on the repository except your one deliverable file. No commits, no pushes, no GitHub writes, no PRs, no
  comments, no PC bridge use, no network. Do NOT spawn subagents.
- Never print a secret. The transcript holds credentials in places: print counts, tool names and scrubbed error classes
  only, never tool-result content beyond the first-line error class with any `KEY=value`, token or URL credential removed.
- Every count comes from a command you ran; paste the command with its output. Every claim carries file:line.
- If something the brief names does not exist, say so in the table (a row with "absent", and the command that showed it).
