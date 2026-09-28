# TRIM-AUDIT: where and how Jev can keep the active context at its budget, turn by turn (task #346, D-105)

Role: evidence-gatherer (sandbox EXPLORE lane, Opus 5.5). Do NOT spawn subagents. You gather and measure; you do not
decide. No verdicts, no root causes, no recommendations: the coordinator synthesizes (the Reflection Firewall). The harness
refuses a subagent's report-file writes, so return the whole evidence body as the text of your final message, in full; the
coordinator saves it as `docs/research/findings/jev-trim/TRIM-AUDIT-2026-09-28.md`.

Authored 2026-09-28 20:5xZ by the coordinator.

## THE OWNER'S ASK (D-105, `docs/08_DECISION_LOG.md`; quote it, do not re-read it as a yes/no question)

"Use Jev to trim the context window itself", so "we never get to a stage where we need compaction, because the context
stays at the optimum level" (the owner recalled "100k or something"; D-097 set 131k for the Hermes lanes). Whenever the
context goes above it, a model ("an RLM") looks at the transcript, finds "which parts ... are useless to what we're doing"
and removes them from the immediate context, "almost on a turn-by-turn basis"; "the logs are still there ... It's just the
active context". The picture: System 1 filters what reaches attention the way the brain filters most stimuli. "If it is
[feasible], it will be the final piece to all of it." Read D-105 in full, and D-053, D-079, D-082, D-087, D-093 and D-097
beside it (`python3 scripts/owner_rulings.py pruner context trim compaction` lists them).

The design question this audit feeds: **where, and how, can a turn-by-turn trimmer sit in each venue, what can decide
"useless to the current work", and what does each seam cost?** Your job is the evidence for that map.

## WHAT TO GATHER (tables with file:line, doc or commit citations and dates; a number only with the command that made it)

1. **The seams, per venue.** For each venue: the code that builds the message list sent to the model; every extension point
   (hooks, plugins, middleware, config); and whether an extension can REMOVE or REPLACE an earlier message, or only add.
   The venues:
   - this Claude Code coordinator session and its subagents (hooks: which events exist, what each may return; plugins,
     as jev-pruner wraps a tool result; compaction, automatic and manual, and what PreCompact and SessionStart:compact see);
     use the Claude Code documentation (code.claude.com) and measure what you can in this sandbox;
   - the Hermes lanes on the PC and the production Hermes (the lane-runtime pin b3399c1 and the proof pin 527da60 in
     `upstream.lock.yaml`; a blob-less clone at 527da60 is at `/home/user/nerdherderdani/hermes-agent`; fetch b3399c1 into
     your scratch if you need it): its agent loop, its prompt builder, any context compression it already has, its plugin
     hooks (the fail-closed `pre_tool_call` policy hook is one), and the per-profile context settings;
   - OmniRoute, the sole model egress: what it could transform, and what S0-04's preservation proof (`proofs/S0-04/`)
     pins about requests passing through it;
   - the Anthropic API features for Claude models (context editing, clearing old tool results, the memory tool,
     server-side compaction): what exists, and which venue could use it.
2. **What can judge "useless to the current work".** The installed jev-pruner (the `fast-jev-output` plugin, enabled here;
   `/root/jev-plugins/jev-pruner`, READ only): its question, its inputs (it already sends history), its thresholds, where
   the Jev call goes, its archive of what it removes, its evals. The local System-1 stack (simple-jev per D-079, Laya, the
   `laya-systemone` server on the PC per D-082 and D-099): the questions it answers and the measured accuracy in the
   committed findings (J2, J2b and their successors). The S1 layer (`.claude/hooks/system1-context.py`, the S1-RATE scores);
   the labels and stacks (LS-B9); the task list as a view of the ledger (D-102). For each: the question it can answer, its
   latency and cost per call where a committed finding measured them, and what it needs as input.
3. **This session, measured.** Re-run the context-budget measurement (`docs/research/findings/jev-pipes/context_budget.py`,
   if it runs; read-only) over the main transcript, `/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl`,
   for 2026-09-26 to 2026-09-28: the context size per request, the compactions per day, and, for a budget of 100k and of
   131k, how many tokens a turn-by-turn trimmer would have to remove per turn and from which sources (tool results by age,
   task reminders, file reads that were read again later, skill bodies, instruction files). Count and measure; never read the
   content of a `thinking` block.
4. **The Hermes lanes, measured from what the repo holds** (the PC is not reachable by you): the prompt sizes over a lane's
   life from committed lane reports and findings. Mark everything else `NOT measured here: PC only`.
5. **Prior art, with sources:** recursive language models (the owner's "RLM"), context editing and pruning methods for
   agent loops, and what each reports about losing a needed line.
6. **What the repo already knows about losing context:** AF-AP registry rows, incidents and rulings about dropped or
   compacted context (a hand-back summary that hid the full report; compaction summaries that went stale), and the
   no-model-in-a-gate rule (KC-J1): which gates a trimmer must never feed.

## BOUNDARY AND RULES

- READ everything; write only scratch under `/tmp/trim-audit/` (removed at the end). No git writes. No PC bridge. No
  outward-facing action. No call to any external model API (TypeSafe or codiv.ai included): read their code and docs only.
- Never read a real secret source (`.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, GH_TOKEN, GITHUB_TOKEN) and never the content of a thinking block.
- Other lanes are live and hold files in the main tree (`.lanes-live`); touch none.
- Long commands in one foreground call each, under 10 minutes. Stamps come from `date -u`.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text
  of its own.

## PREMISE — MEASURED at authoring (2026-09-28 20:5xZ, the main tree at the pushed head; `bash scripts/premise_block.sh`)

```
$ git rev-parse --short HEAD
2d46ba8
$ grep -n 'fast-jev-output\|jev-pruner\|Aegis' /root/.claude/settings.json
12:    "fast-jev-output@fast-jev-output": true
24:        "path": "/root/jev-plugins/Aegis"
27:    "fast-jev-output": {
30:        "path": "/root/jev-plugins/jev-pruner"
35:    "fast-jev-output@fast-jev-output": {
$ sed -n '1,12p' /root/jev-plugins/jev-pruner/README.md
# jev-pruner

A Claude Code plugin that uses TypeSafe's Jev to trim noisy Bash output **after
the command runs, but before its result is sent back to the main LLM**. This
reduces the output carried into later turns without generating a summary.

Using Codex? See [Codex installation and usage](#codex).

```text
Claude requests a Bash command → Command runs → Jev prunes stdout → Claude receives the result
```

$ ls /root/jev-plugins/jev-pruner/hooks /root/jev-plugins/jev-pruner/src
/root/jev-plugins/jev-pruner/hooks:
fast-jev-output.ts
hooks.json

/root/jev-plugins/jev-pruner/src:
codex
history.ts
index.ts
jev.ts
output.ts
retention.ts
secrets.ts
$ grep -n '^| ' docs/research/findings/jev-pipes/CONTEXT-BUDGET-2026-09-25.md | head -13
15:| Source | Share of the re-sent tokens | How measured |
17:| Each segment's starting context (system prompt, tools, instructions, the compaction summary) | 26.0% | first request of each segment x its requests; median start 107,989 tokens |
18:| Task-list reminders (2,038 of them) | 12.0% | the rendered list, 420 characters of header plus one line per task |
19:| Tool results, all tools | 7.5% (Bash 6.8%, Read 0.7%) | result text |
20:| CLAUDE.md re-injected after compactions (140) and as nested memory (124) | 7.1% (4.2% + 2.9%) | the files' content |
21:| Our own Bash commands (heredocs and scripts typed into the call) | 4.1% | the tool input |
22:| Tool, agent, skill and MCP listings | about 5% | record size (an upper bound) |
23:| Skill bodies loaded (78) | 1.6% | the skill text (capped at 20,000 characters each) |
24:| Typed messages, reminders and hook text in user records | 1.6% | the text |
25:| Assistant text | 0.4% | the text |
26:| Exact repeats of an earlier result, plus the shared lines of re-runs | 0.00% (61,819 tokens) | same normalized call within a segment |
$ git -C /home/user/nerdherderdani/hermes-agent log -1 --format='%h %s'
527da60844 fix(cli): report a named profile as running when the default multiplexer serves it
$ grep -n 'commit:' upstream.lock.yaml | head -3
7:    commit: 37a7d4f8a0a0632653a14084b8140ceb486ab0e8
12:    commit: 527da60844d4dced37879ea50259675371abe10e
18:    commit: 1c8321cd08feb597f8bcff5195c21148fb3e98ed
$ ls .claude/hooks/ | head -40
__pycache__
edit-snapshot.py
graft-first-nag.py
search-intercept.py
session-start.sh
system1-context.py
system1-situations.json
turn-retro-gate.sh
wiki-context.py
$ df -m / | tail -1
/dev/vda          258020 25839     12100  69% /
```
