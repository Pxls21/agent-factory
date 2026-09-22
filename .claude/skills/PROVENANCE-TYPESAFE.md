# Provenance — typesafe-ai skill (the "skill for Jev")

Source: https://github.com/typesafe-ai/skills (TypeSafe AI's official agent skill; the docs page
https://docs.typesafe.ai/agent-skill.md names it as the drop-in skill for Claude Code, Codex and other agents)
Commit: 65a39f3 (2026-09-12), plugin manifest `typesafe` 0.5.7
License: MIT (Copyright (c) 2026 TypeSafe AI) — carried in the skill's frontmatter and in `typesafe-ai/LICENSE`.

Vendored VERBATIM 2026-09-22 into `.claude/skills/typesafe-ai/` and mirrored to `.agents/skills/`
(via `harness-ports/bin/sync-skills.sh`) at the owner's ask ("look for a skill for jev, I had one then lost it").
Not added to `harness-ports/lane-skills.txt` (PC lanes do not load it yet).

What it is: a markdown-only skill (10 KB) that teaches an agent the System One programming model — typed
questions (`choice` / `score` / `noul`) over a `state`, calibrated probabilities and confidence, the
fan-out / confidence-routing / composite-scoring / intent-routing patterns, and "read the live docs first"
(https://docs.typesafe.ai/llms.txt; every page has a `.md` twin). No code, no network calls of its own, no
credential handling — reviewed before adoption. The live docs are reachable from the sandbox (measured
2026-09-22: llms.txt 200, llms-full.txt 903 KB).

Adaptation: none in the skill text. Our standing constraints apply around it:
- The hosted TypeSafe API (`TYPESAFE_API_KEY`, `POST https://api.typesafe.ai/v1/systemone`) is NOT a
  production dependency here (STANDING PROJECT RULE 3: no provider credentials in Hermes or evaluators).
  The planned backend is the open, self-hosted Laya (`convaiinnovations/laya`, Apache-2.0), whose
  `Agent.system_one(state, questions)` returns the same `{model, answers, usage}` shape; the question
  grammar this skill teaches applies unchanged.
- A System One judgment is ADVISORY in this repo: pruning, triage, relevance, routing. It never decides a
  gate (CLAUDE.md: no LLM-judge in the gate spine; the rule covers any model judge).
- Task #104 (2026-09-22) carries the audit and the integration plan.
