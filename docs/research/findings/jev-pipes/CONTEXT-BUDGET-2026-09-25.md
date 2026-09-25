# Where our session's context goes (measured 2026-09-25 11:1xZ)

Every model request re-sends the whole context. This session (one chat, 130 compactions, 17,811 requests, both project
folders' main transcripts) re-sent **8.15 billion tokens**, a median of 461,918 per request. Before the Jev pipelines chase
savings, this measures where those tokens come from. Probes (counts only, no transcript text leaves the process):
`repeat_probe.py`, `context_budget.py` and `inject_cost.py` in this folder, all built on the P1 replay's own transcript walk
and its residency formula (characters / 4.06 x the requests until the next compaction, `scripts/jev_pipes/accounting.py`).

## Result

**The largest shares are what the harness injects (task lists, instruction files, listings), not tool outputs. Tool
outputs are 7.5% of the re-sent tokens, so a tool-output pruner (P1) can never save more than that. Collapsing repeated
results saves 0.00%.**

| Source | Share of the re-sent tokens | How measured |
|---|---|---|
| Each segment's starting context (system prompt, tools, instructions, the compaction summary) | 26.0% | first request of each segment x its requests; median start 107,989 tokens |
| Task-list reminders (2,038 of them) | 12.0% | the rendered list, 420 characters of header plus one line per task |
| Tool results, all tools | 7.5% (Bash 6.8%, Read 0.7%) | result text |
| CLAUDE.md re-injected after compactions (140) and as nested memory (124) | 7.1% (4.2% + 2.9%) | the files' content |
| Our own Bash commands (heredocs and scripts typed into the call) | 4.1% | the tool input |
| Tool, agent, skill and MCP listings | about 5% | record size (an upper bound) |
| Skill bodies loaded (78) | 1.6% | the skill text (capped at 20,000 characters each) |
| Typed messages, reminders and hook text in user records | 1.6% | the text |
| Assistant text | 0.4% | the text |
| Exact repeats of an earlier result, plus the shared lines of re-runs | 0.00% (61,819 tokens) | same normalized call within a segment |

About a third of the in-segment growth stays unattributed: the 4.06 characters per token undercounts code and JSON, and
some record kinds were not priced. The shares are lower bounds for what is measured and do not add to 100.

## What it means for the pipelines (D-087)

1. **P1-style output trimming has a low ceiling here (7.5%).** P1 measured FAIL for its own reasons; even a perfect pruner
   would touch under a tenth of the cost.
2. **The biggest levers need no model:**
   - **The task-list reminder (12.0%).** The harness repeats the whole open-task list whenever the task tools sit unused.
     Every task in the list is paid on every request after each reminder. A list of the ACTIVE tasks only (the backlog
     stays in the ledger) cuts this in proportion.
   - **CLAUDE.md (7.1% in re-injections, plus its share of every segment start).** It is 92,412 bytes now (about 23k
     tokens). This session starts at `/home/user`, so the repo's CLAUDE.md also arrives as nested memory each time it
     changes on disk, and the GitNexus banner rewrites it on every re-index. A shorter CLAUDE.md (war stories and quirk
     lists moved into skills loaded on demand), a session started in the repo, and a banner that does not rewrite the
     file would each cut every request.
   - **Our own long Bash commands (4.1%).** Scripts typed into a Bash call stay in the context; a script written to a
     file and run by name costs its bytes once.
3. **Calls still beat bytes.** A call saved removes a whole re-send (a median 461,918 tokens), which is why P2 (prefetch)
   and P3 (digests) stay next in the plan.

## NOT measured

Subagent transcripts (their own contexts, not this one's); the system prompt and tool schemas inside the segment start,
split by part; the unattributed third of the growth; token counts from a real tokenizer.
