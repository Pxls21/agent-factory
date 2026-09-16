# ADR 0007 — buzz-agent permitted for lightweight local-model teammates

- Status: accepted
- Date: 2026-09-16
- Owner decision: 2026-09-16 ("use Buzz's local models feature with Qwen 3.8 as a teammate; we'll still have
  Hermes for the coding teams")
- Relates to: ADR 0001 (Hermes-only runtime), ADR 0002 (OmniRoute sole egress), rule 1, rule 9

## Context

Buzz ships its own minimal ACP agent, `buzz-agent` (block/buzz `crates/buzz-agent`), configurable to any
OpenAI-compatible endpoint by env var. The owner wants to create Buzz teammates backed by the **local Qwen3.8-27B
model** (the vLLM `qwen` container, D-032) for cheap chat teammates that do not need a frontier model, while
Hermes remains the runtime for coding and governed work. ADR 0001 makes Hermes the sole stock runtime; rule 1
forbids adding parallel *coding* runtimes (Codex CLI, Claude Code, Pi). `buzz-agent` is Buzz's own bundled
teammate agent, not a bolted-on coding runtime — so this ADR scopes a carve-out rather than overturning 0001.

## Decision

`buzz-agent` is permitted as a **lightweight local-model teammate runtime**, alongside Hermes, under these bounds:

1. **Sole egress holds.** A `buzz-agent` teammate reaches its model **through OmniRoute** (`:20128`, model id
   `qwen-local/qwen3.8-27b-local` or a local-first combo) — never the container's `:8080` directly (rule 3 /
   ADR 0002). Proven live 2026-09-16 (`buzz_agent::llm: call completed model="qwen-local/qwen3.8-27b-local"
   provider=OpenAi`).
2. **Hermes remains primary.** Coding, tool-effectful, and governed teammates stay on Hermes (rule 1). This
   carve-out is for chat teammates on a cheap local model, not a general second runtime.
3. **Policy gate is not bypassed (rule 9).** A `buzz-agent` teammate's own tools do NOT pass Hermes'
   fail-closed `pre_tool_call` policy hook. Therefore a Qwen teammate runs **chat-only — no effectful MCP
   tools** — until a policy gate is wired for the `buzz-agent` path. A prompt instruction is not a security
   control.
4. **Cost honesty.** Prefer the raw model id (`qwen-local/qwen3.8-27b-local`) so a teammate never silently
   falls back to a paid cloud model; use a local-first combo only where resilience is worth a silent cloud spend.
5. **Credentials.** A teammate authenticates to OmniRoute with an OmniRoute-issued key. Reusing the Hermes
   profile's `OMNIROUTE_API_KEY` works today; a **dedicated OmniRoute connection/key for Buzz teammates**
   (scoped, revocable, meterable) is the preferred end state (ADR 0002's scoped-credential spirit).

## Consequences

The ability to spin up a Qwen-3.8 teammate is available and verified end-to-end (see `docs/LOCAL-MODEL-GUIDE.md`
consumer pattern 2). Pairing a specific teammate into a community is an owner step (Nostr identity + community,
in the Buzz app). Wiring a policy gate for the `buzz-agent` path, and the dedicated OmniRoute Buzz key, are
follow-ups before a teammate is given effectful tools or exposed beyond the owner's own communities.
