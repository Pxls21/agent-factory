# ADR 0001 — Hermes is the sole stock production runtime

- Status: accepted
- Date: 2026-09-02

## Context

The original plan included Hermes, Codex CLI, Claude Code, Pi, and corresponding ACP adapters. Maintaining all four as stock workhorses duplicates process, credential, permission, prompt, memory, and containment paths. Hermes already exposes a native ACP server and can use Codex-capable model routes through a Responses-compatible provider.

The surrounding design—ACP, `buzz-acp`, memory/governance, GBrain dream cycles, JIT Harness Foundry, AlphaEval, PandaProbe, and conditional HarnessRouter—solves different problems and is not redundant with the workhorse choice.

## Decision

Use `buzz-acp` to launch `hermes-acp`. Hermes is the only stock production workhorse. Route Codex-capable models through Hermes `codex_responses` and OmniRoute. Do not deploy Codex CLI/app-server, Claude Code, Pi, `codex-acp`, `claude-agent-acp`, or `pi-acp` as parallel runtimes.

Retain JIT/GBrain/evaluation and conditional harness research under isolated proposal/candidate gates. An approved generated harness normally becomes a Hermes plugin/profile. A standalone harness or HarnessRouter activation requires a later ADR.

## Consequences

The production path has one runtime policy surface while the full improvement roadmap remains. ACP stays live. Codex model capability remains available. Generated or third-party harnesses cannot silently become peers of Hermes.
