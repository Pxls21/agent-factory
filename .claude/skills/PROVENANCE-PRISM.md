# Provenance — prism-* analysis skills

Source: https://github.com/Cranot/super-hermes
Commit: ffe2d10042041dcc23325f013e8b7e607e069952
License: MIT (Copyright (c) 2026 Cranot) — carried in each skill's frontmatter.

Vendored VERBATIM 2026-09-17 into `.claude/skills/` and mirrored to `.agents/skills/`
(via `harness-ports/bin/sync-skills.sh`):

- prism-scan  (+ `references/`: claim, deep_scan, error_resilience, identity, l12, optimize, simulation)
- prism-discover
- prism-full
- prism-3way
- prism-reflect

What they are: markdown-only analytical prompts ("cognitive lenses"). `prism-scan` generates a
custom per-artifact lens then executes it to a findings table (location / breaks / severity /
fixable-or-structural); `prism-full` adds a mandatory adversarial self-correction pass, aligning
with our adversarial-verify / anti-hollow-green discipline. No code, network calls, or credential
handling — reviewed before adoption.

Adaptation: none (copied as-is). The `prism-reflect` growth log `.prism-history.md` is gitignored
(per-project, untracked).

NOT adopted from the same ecosystem, and why:
- `42-evey/hermes-plugins` — 34 "evey" persona plugins for NousResearch hermes-agent (a different
  runtime); 21 touch external egress / credentials / subprocess (a crypto wallet, MQTT, Telegram,
  email, a code-exec sandbox). Wrong framework + breaches our sole-egress / least-privilege rules.
- `Yonkoo11/hermes-dojo` — a self-improvement agent that auto-patches its own skills (self-
  modification) + Telegram; its `failure_patterns.md` catalog is subsumed by our AF-AP registry.
