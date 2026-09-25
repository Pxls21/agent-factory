# S1A: audit of what feeds context and what enforces the workflow, measured on the recorded sessions (D-090)

Role: evidence-gatherer (sandbox, Opus 5.5). Do NOT spawn subagents. Output: `docs/research/findings/system1-context/AUDIT-2026-09-25.md`
plus the scripts that produced every number, in the same folder. Write the document incrementally from the start. You collect
evidence; you do not propose the design (the coordinator does, from your tables). PIN: 9124b3c (origin).

## WHY

The owner (D-090): "we have a lot of skills and you barely run any of them"; the code MCP servers, the graphs and the other tools
"are basically never used", and "99% of our problems would have been avoided if they were used the way we designed them". The
direction: a System-1 layer (Laya/Jev plus scripts) runs the instruments in the background and feeds the agent the relevant skill
sections, wiki, code map and anti-pattern rows BEFORE it acts; Laya shadows the workflow; a tool finds where a bug first appeared
in the chat. Before designing it, measure what exists, what actually runs, and what it would have caught.

## EVIDENCE DEMANDS (each a table with its producing command or script; counts only)

1. **Inventory.** Every hook (event, matcher, the script chain behind it, what it injects or blocks, the size of a typical
   injection measured on a real sample input, its latency); every context or enforcement script (at least `scripts/lane_context.sh`,
   `jev_context.py`, `jev_locate.py`, `hiccup_scan.py`, `chat_tail.py`, `why.sh`, `ap_screen.py`, `report_lint.py`, `hook_context.py`,
   `install_session_hooks.py`); every instrument (graft, GitNexus, codebase-memory, code-review-graph, ripwire, sentrux, slopo, the
   prism skills); the MCP servers and their connection state; the skills (413 directories: by origin, size, and whether the
   description names concrete situations).
2. **Usage, over every transcript** (`/root/.claude/projects/*/` main and subagent files; 325 files, 1.4 GB), main and subagent
   counted apart, per day: tool calls by tool name; MCP tool calls by server; Bash commands that run each instrument or script (one
   pattern per instrument, the pattern stated); Skill calls by skill; hook injections seen in the records (by their marker text, for
   example `EDIT SNAPSHOT`, `wiki live-state`, `[wiki match`, `[incident match`, `TURN-END RETRO`, the graft-first and
   search-intercept messages).
3. **Incidents against instruments.** For the registry rows AF-AP-150 to AF-AP-218 (`docs/INCIDENT-LOG.md`): the row's class, which
   instrument, skill section or earlier registry row existed at the time and names the class (by commit date), and whether that
   instrument ran in the session in the two hours before the commit that recorded the incident (transcript timestamps). Evidence
   only: say "named by X, X did not run" or "no instrument named it"; never "would have prevented".
4. **Budgets for a hook.** Measured size and latency of one call of each: `graft ask`, `graft skeleton`, GitNexus `impact` and
   `context` (CLI), codebase-memory `search_graph` (CLI), code-review-graph `callers_of` and `tests_for`, `lane_context.sh` on one
   file, `wiki-context.py` on a sample prompt, and a Laya rank call on the local server (127.0.0.1:47411: at most 10 requests, small
   synthetic inputs; it serves the owner's tools, so no load test).
5. **The chat bug locator.** For a sample of five registry rows with a known first appearance in the chat, what each existing tool
   (`hiccup_scan.py`, `chat_tail.py`, `jev_locate.py`, `why.sh`, `replay_transcript_edits.py`) can and cannot answer about "where did
   this first appear", shown by running it.
6. NOT-measured list and DISCREPANCIES.

## BOUNDARY

CREATE: the output document and its scripts under `docs/research/findings/system1-context/`. READ everything else. Modify nothing
else. Scratch: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/s1a/`.

## STANDING RULES

Transcripts hold secrets: never print, paste or commit transcript text. Scans print counts, names, paths, dates and tool names
only; a pattern that matches a credential shape is never printed. Never read a secret file (`.pc-bridge.env`, `/root/.codiv/api.env`,
any `*.env`, any key file). No PC bridge; no git writes; no outward-facing action. Another lane (CTX1) is changing CLAUDE.md and
some skills in this tree: read them as they are, touch nothing. The disk is tight (about 2 GB free): stream the transcripts, never
copy them; delete your scratch copies as you go.

## PREMISE — MEASURED at authoring (2026-09-25 14:0xZ, the sandbox)

```
$ ls .claude/hooks/
edit-snapshot.py  graft-first-nag.py  search-intercept.py  session-start.sh  turn-retro-gate.sh  wiki-context.py
$ (hook events registered in /home/user/.claude/settings.json and .claude/settings.json)
{'PostToolUse': 1, 'PreToolUse': 1, 'SessionStart': 1, 'Stop': 1, 'UserPromptSubmit': 1}   (each file)
$ ls -d .claude/skills/*/ | wc -l
413
$ claude mcp list   (state words only)
codebase-memory-mcp Connected; ouroboros Failed to connect; graft Connected; gitnexus Connected; aleph (listed);
phoenix-docs Connected; codebase-memory Pending approval
$ find /root/.claude/projects -name '*.jsonl' | wc -l; du -sh /root/.claude/projects
325
1.4G
$ (Skill tool calls in the /home/user project folder's main transcripts, counted 2026-09-25 13:4xZ)
12: orchestration 6, council 3, deep-work 1, bug-echo 1, rwkv 1
```

A question for you, not a fact: the hook entries in the two settings files each hold one command; say what each command runs.
