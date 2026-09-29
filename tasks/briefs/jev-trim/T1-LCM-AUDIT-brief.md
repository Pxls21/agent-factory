# T1-LCM-AUDIT: does an existing Hermes context engine already do D-105's job? (task #346)

Lane: sandbox `evidence-gatherer`, model opus. An EXPLORE lane: you gather and measure; you give no verdict, root cause
or recommendation (the design choice stays in the main loop).

## The owner's words (D-105, 2026-09-28 18:23:30Z)

Keep the context "at the optimum level" so "we never get to a stage where we need compaction"; remove "which parts of
the transcripts are useless to what we're doing" from the active context, "almost on a turn-by-turn basis"; "the logs
are still there ... It's just the active context."

## Your question

Hermes selects its context engine by `context.engine` in the profile config (READ: our clone at 527da60,
`agent/agent_init.py:2726-2760`, `agent/context_engine.py`). Upstream names "lcm" (Lossless Context Management) as an
example engine. For each candidate below, gather what it does per request, what it keeps and where, what it asks a
model to do, what it would need from our setup, and what it would risk against our standing rules. The design this
feeds is `docs/research/findings/jev-trim/D105-DESIGN-v1.md` (READ §3.2 and §6 T1).

Candidates (from a web search, not yet read):
- `stephenschoettler/hermes-lcm` on GitHub ("a DAG-based context engine that never loses a message");
- `hermes-lcm-x` (the Hermes plugin catalog page `hermes-agent.nousresearch.com/docs/plugins/hermes-lcm-x`);
- `lossless-hermes-py` on PyPI;
- the LCM paper they cite (Ehrlich and Blackman, Voltropy PBC, 2026-02), and Hermes issue #5701 ("Pluggable context
  engines — enabling LCM as a plugin").

## Boundary

- READ only. Clone or download into `/tmp/t1-lcm/` at a named commit or version, and remove it at the end. Never run
  third-party code: no `pip install`, no running its tests or scripts (standing rule: third-party code is read before
  anything is run; T1 only reads).
- No git writes in the repo, no PC bridge, no subagents, no outward action (no issue, comment or post anywhere).
- Take a repository URL from its public page or the package metadata. Never read a clone's `git remote -v` (the
  auto-mode classifier refuses it; `docs/INCIDENT-LOG.md`, 2026-09-28 21:3xZ). If a read or a fetch is refused, do not
  work around it; report it verbatim with its time.

## What to gather, per candidate (cite file:line at the pinned commit; mark each cell SOLID or UNSURE)

1. Identity: the URL, the commit sha or version you read, its date, the license (and whether our
   `LICENSE-DECISION.md` allows it).
2. The engine's surface: which `ContextEngine` methods it implements (`select_context`, `compress`, `should_compress`,
   `get_tool_schemas`, `handle_tool_call`, the session hooks), and the ABC version it targets. Does it load on our pins,
   527da60 and b3399c1 (the lane runtime, `upstream.lock.yaml:242`)? Read b3399c1's `agent/context_engine.py` from a
   blob-less fetch of the public URL `upstream.lock.yaml` records.
3. Per request: what the model sees (summaries, recent turns, a budget), what decides it, and whether the stored
   history changes (request-only or persisted).
4. Model calls: does it summarize with a model? Which one, through which endpoint and credentials, how often, and at
   what token cost per call? Our rule: every model request goes through OmniRoute (standing rule 3), with no provider
   credentials in Hermes.
5. Storage: where it writes (e.g. `lcm.db`), its schema, whether raw messages are kept verbatim, its growth and
   retention, and who can read it.
6. Recall tools: names, arguments, output size caps, and scope (only the current session, or others too).
7. Security surface: network calls, files read and written, subprocesses, environment variables read; each item
   checked against our standing rules 3, 9, 10, 11, 12 and 13 (CLAUDE.md "STANDING PROJECT RULES").
8. Evidence of quality: its tests (count, what they assert), any measured results (recall, cost, latency), and the
   LCM paper's claims from its abstract (SOLID) or body (UNSURE).
9. Upkeep: the last commit date, open issues, contributors, stars.

Also record the same facts, where they apply, for Hermes's own built-ins that do part of the job (audit B7, the proactive
tool-result prune; B8, micro-compaction), so the table compares like with like.

## Report

Return the whole report as your final message (a report-file write is refused for subagents): the premise re-run, one
table per candidate (the nine rows above), the built-ins' rows, a DISCREPANCIES list (anything in this brief that did not
match what you found), and every refusal you met. No recommendation.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin 0e6d4a1)

Printed by `bash scripts/premise_block.sh` from the main tree. Expected to differ when you re-run it: nothing, unless
HEAD moved past the PIN (the first line checks it is still an ancestor).

```
$ git merge-base --is-ancestor 0e6d4a1 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git -C /home/user/nerdherderdani/hermes-agent log -1 --format='%h %ci'
527da60844 2026-09-02 06:36:16 -0700
$ grep -n 'Select context engine\|plugins/context_engine/<name>/ directory (repo-shipped)' /home/user/nerdherderdani/hermes-agent/agent/agent_init.py
2726:    # Select context engine: config-driven (like memory providers).
2728:    # 2. Check plugins/context_engine/<name>/ directory (repo-shipped)
$ grep -n 'def get_tool_schemas\|def handle_tool_call\|def select_context' /home/user/nerdherderdani/hermes-agent/agent/context_engine.py
215:    def select_context(
413:    def get_tool_schemas(self) -> List[Dict[str, Any]]:
421:    def handle_tool_call(self, name: str, args: Dict[str, Any], **kwargs) -> str:
$ grep -n 'commit: b3399c1' upstream.lock.yaml
242:    commit: b3399c139624a0081d70397741a5b45f60fbe1f4
$ grep -n '^### 3.2 Hermes\|^| T1 ' docs/research/findings/jev-trim/D105-DESIGN-v1.md
103:### 3.2 Hermes: the lanes first, then production
181:| T1 | The LCM audit: hermes-lcm and its forks at a pinned commit (what runs per request, recall tools, license, tests, fit with our pins). Adopt or build. | sandbox EXPLORE | no |
$ ls /tmp/t1-lcm 2>&1 | head -1
ls: cannot access '/tmp/t1-lcm': No such file or directory
```
