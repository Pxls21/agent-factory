# Instructions for coding agents

These rules apply to the whole repository.

1. Hermes is the sole stock production workhorse. Do not add Codex CLI, Claude Code, Pi, or their ACP adapters as parallel runtimes.
2. ACP remains the v1 interface contract: `buzz-acp` launches Hermes through `hermes-acp`. Do not replace this path without an approved ADR.
3. OmniRoute is the sole model API egress. Do not add direct provider credentials to Hermes, GBrain, JIT, or any evaluator.
4. Do not enable the Codex app-server/OAuth path in v1. Use Hermes' `codex_responses` wire mode against the internal OmniRoute endpoint.
5. Retain the JIT Harness Foundry and GBrain-informed dream phase. They are isolated proposal/generation planes with no direct production write or execution authority.
6. HarnessRouter remains conditional: use it only for an approved generated or third-party UHP-only harness that cannot use ACP.
7. Treat `docs/archive/v2-original/` as read-only evidence. Update current documents instead.
8. Treat Fubuki packets as immutable, canonical, and hash-pinned for a session.
9. All effectful Hermes tools must pass a fail-closed `pre_tool_call` policy hook. A prompt instruction is not a security control.
10. Persistent memory writes start at their authorized logical scope. Upward promotion requires an explicit reviewed proposal. Do not expose delete or promotion tools to a model or generated harness.
11. Preserve sole egress, least privilege, non-root service users, secret separation, and gVisor containment in every deployment change.
12. Prefer deterministic evaluation before LLM-as-judge. Never let JIT, GBrain, AlphaEval, or rubric code share production credentials or host networking.
13. Every upstream dependency must be pinned by immutable commit or digest and recorded in `upstream.lock.yaml`.
14. Feature PRs must include tests for normal behavior, failure behavior, and the relevant security boundary.
15. Do not claim a service is runnable or production-ready until its executable acceptance gate passes.
