# JEV-FIT: audit our setup and design where Jevs fit best (owner 2026-09-25)

Three auditors, one per area (A, B, C below). Role: a software architect who READS THE REAL CODE and DESIGNS integrations. Do NOT
spawn subagents. Your final message IS your report (you cannot write files): at most 1,800 words plus the tables.

## WHAT THE OWNER ASKED FOR

"Actually auditing the system and looking where how best to fit jev into our setup." This is a DESIGN task. Do not review or grade past
experiments (the rejected fine-tune, the zero-shot probe); they are background only. The owner's direction (D-084, D-086 in
`docs/08_DECISION_LOG.md`): our own session records are the primary training data; all session data should be usable; an RWKV model
will process session data alongside Laya; the tools we use in this session are the tools the agent factory will use ("3 birds, 1 stone").

## WHAT A JEV IS (facts to design with)

- A small model that answers ONE typed question with probabilities: yes/no, a choice among fixed options, or a score over candidates. It
  writes no free text.
- **Laya** (0.4B): reads one block of 512 to 1,024 tokens; about 1 s per question on CPU.
- **The RWKV-7 student** (0.4B): a fixed-size recurrent state that reads a whole stream. On the RTX 3090: 61,440 tokens in 1.17 s; one
  question answered from a copy of the saved state in about 0.046 s (`docs/research/findings/j2b-variants/rwkv7-g0/2026-09-24-window2/README.md`).
  So it can follow a session event by event and answer many questions cheaply at any point.
- **A teacher** (Qwen3.8-27B on the PC) can label examples that have no recorded answer.
- **Labels already recorded** in our records: the verifier's class of 826 findings, 3,649 anti-pattern matches, exit codes, gate outcomes,
  stop-check outcomes, agent outcomes (`docs/research/findings/laya-ft-data/SESSION-DECISIONS-2026-09-25.md`, 26 decision types).
- **Every hook input carries `transcript_path`**, so a live reader can tail the session (`docs/research/findings/laya-ft-data/JEV-INTEGRATION-MAP-2026-09-25.md` section 3).

## RULES EVERY DESIGN KEEPS

- A Jev never decides a gate. It warns, ranks, routes, points, prefetches, or stops a waste; a deterministic rule or a person decides.
- Fail open: a Jev that is down, slow or unsure changes nothing.
- System 1 talks directly to its own model server; OmniRoute stays the path for System 2 (D-082).
- No secret leaves its boundary; a design that needs session text says how it stays scrubbed.

## YOUR DELIVERABLE (per integration point you find in your area)

1. **Seam:** the file and line where it plugs in (read it; cite it).
2. **Trigger:** the event that fires it.
3. **Input:** what the Jev reads (the stream so far, one block, a candidate list).
4. **Question:** the typed question and its options.
5. **Action:** what the answer changes, concretely.
6. **Payoff:** tokens, time, GPU hours or errors saved, estimated from counts in our records (name the count and its source); say
   "unmeasured" where you have none.
7. **Labels and test:** which recorded answer trains it, and the simple rule it must beat on held-out examples.
8. **Model fit:** the RWKV stream reader, Laya per block, or "a rule is enough" (say so when a plain rule would do; that is a good finding).
9. **Build size:** small, medium or large, and what it depends on.

Then: a ranked top five for your area (payoff against build size), the shared infrastructure your area needs (a Jev service, a
stream-state server, a hook shim, a label log), and one short paragraph on how your area's Jevs would carry over into the agent factory.
JEV-MAP's 35 points are a starting list, not a limit: find what it missed.

## THE THREE AREAS

**A. The coordinator session (Claude Code in this sandbox).** The hooks and their registration (`.claude/hooks/`, `.claude/settings.json`,
`/home/user/.claude/settings.json`, `scripts/install_session_hooks.py`, `scripts/hook_context.py`), context injection
(`.claude/hooks/wiki-context.py`, the session-start hook), the edit and search hooks (`.claude/hooks/edit-snapshot.py`,
`.claude/hooks/search-intercept.py`), the stop gate (`.claude/hooks/turn-retro-gate.sh`), and the coordinator's own habits visible in the
records (re-reads, retries, compactions). Focus: tokens in the coordinator's context and wasted calls. The earlier audit measured where
the context goes (`docs/research/findings/JEV-LEVERAGE-AUDIT-2026-09-24.md` section 2: task reminders were 44.4% of transcript bytes; the
wiki-context hook injects 6.5 to 11.5 KB per event).

**B. The build machinery.** PC lanes (`scripts/pc_lane.sh`, `harness-ports/bin/pc-lane.sh`, the lane heartbeat, Hermes on the local Qwen),
verify lanes and the contract gate (`.claude/skills/contract-gate/SKILL.md`), the commit, push and CI gates (`scripts/hooks/`,
`scripts/push_clean.sh`, `scripts/ci_gate.py`), the harvest tools (`scripts/decide-harvest`, `scripts/hiccup_scan.py`,
`scripts/report_lint.py`). Focus: GPU hours and wall time saved, failures caught early, review triage, routing.

**C. The agent factory itself (the product being built).** The plan (`docs/01_ARCHITECTURE.md` through `docs/11_DREAM_PHASE.md`; read
`docs/02_COMPONENT_AUDIT.md` first), the governance core in `src/agent_factory/`, the Hermes `pre_tool_call` policy hook design, the memory
scopes, the dream phase and the JIT Harness Foundry. Focus: where System 1 belongs in the product, and how Jevs trained on our sessions
carry over to it.

## CONSTRAINTS

Read-only: no file writes, no git writes, no network, no PC bridge. Session transcripts under `/root/.claude/projects/-home-user/` may be
counted but never quoted unless passed through `scripts/transcript_export.py`'s `scrub`; never search them for keys, tokens or passwords.
FAKE strings for anything secret-shaped.
