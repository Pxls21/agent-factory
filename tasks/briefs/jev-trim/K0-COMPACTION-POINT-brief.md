# K0-COMPACTION-POINT: where does each model we run work best? The published evidence (task #352, D-106)

Written 2026-09-29 01:0xZ by the coordinator. Lane: sandbox `evidence-gatherer`, model opus. An EXPLORE lane: you gather
and measure; you give no verdict and no recommended point (the choice stays in the main loop, design §10.2).

## The owner's words (D-106, 2026-09-29 00:51:42Z; voice-typed, quoted where clear)

"Each model has its optimal context size." "For 1 million [context] models, it's like there's a specific sweet spot of
token context size." Models are "bad at ... working with the full 1 million co contexts and they perform better when you
compact them earlier maybe do some research in that find the optimal spot for the models we're using." The owner's first
guess for this session: "maybe it's like 500k". For the Hermes lanes the owner set 131k as "a good sweet spot for hermes"
(D-097).

## Your question

For each model we run, what do published measurements say about how its work changes as the input grows, and where does
it start to fall? Gather the evidence that lets the main loop choose a compaction point per model. Design:
`docs/research/findings/jev-trim/D105-DESIGN-v1.md` §10.2 (READ; you are its R-A). This session compacts at about 784k
today (`docs/research/findings/jev-trim/TRIM-AUDIT-2026-09-28.md` A1.14, A1.15; READ).

The models (the premise shows where each is configured):
- **Opus 5.5** (`claude-opus-5-5`): this session's main loop now, and every sandbox lane. 1M context.
- **Fable 5**: the main loop by CLAUDE.md's routing table. Find its context size and any published curve.
- **Qwen3.8-27B**: the PC build and verify lanes (vLLM, 131k by D-097). Find its native context and published curve.
- Where a model has no published curve, its nearest measured siblings (earlier Claude models at 1M, other Qwen3.x
  sizes), each row marked as a sibling.

## What to gather (each row: model, task or benchmark, the length points, the scores, the source URL, its date, who
measured it (the vendor or an independent group), and SOLID if you read it in the primary source, else UNSURE)

1. **Vendor numbers:** model cards, system cards and launch posts with long-context results by length (for example
   multi-needle retrieval such as MRCR at 128k, 256k and 1M; graph walks; long-document QA).
2. **Independent curves by length:** RULER, NoLiMa, HELMET, LongBench v2, Fiction.LiveBench, the context-rot studies,
   needle-in-a-haystack variants; for each, the length at which a model falls below a stated fraction of its
   short-context score, where the source gives one.
3. **Agents at long context:** any measured result for coding or tool-using agents as the context fills (task success
   or error rate against context length or against the number of turns), and any measured comparison of compaction
   thresholds or strategies for agents.
4. **What a compaction costs:** measured information loss in agent summaries or compaction (for example the LCM paper
   by Ehrlich and Blackman, 2026-02, and other agent-memory work), and the vendors' own guidance on when to compact
   (Anthropic's context-engineering guidance; Claude Code's documented defaults, `model-config.md` 734-757 in the audit).
5. **Position effects:** whether the evidence says WHERE in a long context the losses fall (the start, the middle, the
   most recent turns), since a compaction keeps the start and the end.

## Boundary

- Read-only web research (WebSearch, WebFetch; load them with ToolSearch). Scratch under `/tmp/k0-ctx/`, removed at the
  end. Download nothing to run; run no third-party code.
- No git writes, no PC bridge, no subagents, no outward action (no issue, comment or post anywhere).
- Never read a secret source (`.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, the GH_TOKEN and GITHUB_TOKEN variables).
- A refused fetch or read is reported verbatim with its time, never worked around.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own. Stamps come from `date -u`, never typed. Cite commits by subject or by an origin id.

## Report

Return the whole report as your final message (a report-file write is refused for subagents): the premise re-run; one
evidence table per model (siblings marked); the tables for items 3 to 5; a list of what you looked for and did not find
(with the queries you ran); a DISCREPANCIES list (anything in this brief that did not match what you found); every
refusal. No verdict and no recommended point.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin 0e6d4a1)

Printed by `bash scripts/premise_block.sh` from the main tree. The D-106 row, the design's §10, this brief and the
probe are local at dispatch (the push waits on a gate), so the block measures the tree you read. Expected to differ
when you re-run it: nothing.

```
$ git merge-base --is-ancestor 0e6d4a1 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ grep -n '^model:' .claude/agents/evidence-gatherer.md .claude/agents/code-implementer.md .claude/agents/adversarial-verifier.md
.claude/agents/evidence-gatherer.md:4:model: claude-opus-5-5
.claude/agents/code-implementer.md:4:model: claude-opus-5-5
.claude/agents/adversarial-verifier.md:4:model: claude-opus-5-5
$ grep -c '^| D-106 |' docs/08_DECISION_LOG.md
1
$ grep -o '^| D-097 | OWNER DIRECTION 2026-09-26 03:3xZ.\{0,150\}' docs/08_DECISION_LOG.md
| D-097 | OWNER DIRECTION 2026-09-26 03:3xZ (chat, voice-typed; transcript 03:32:41Z and 03:33:51Z): "im thinking to reduce the context to 131k instead of full 262k since 131k is a good sweet s
$ grep -n '^## 10\. \|^### 10\.2 ' docs/research/findings/jev-trim/D105-DESIGN-v1.md
235:## 10. D-106 (2026-09-29): the re-scope and the plan
251:### 10.2 Where to compact (task #352)
$ grep -n '^| A1.14 \|^| A1.15 ' docs/research/findings/jev-trim/TRIM-AUDIT-2026-09-28.md | cut -c1-40
70:| A1.14 | Auto-compaction window | Se
71:| A1.15 | Measured compaction point |
$ env | grep -o '^CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=[0-9]*'
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
$ sha256sum tasks/briefs/jev-trim/k1_authoring_probe.py | cut -c1-16
a9bea1dbbd9c112a
$ ls /tmp/k0-ctx 2>&1 | head -1
ls: cannot access '/tmp/k0-ctx': No such file or directory
```
