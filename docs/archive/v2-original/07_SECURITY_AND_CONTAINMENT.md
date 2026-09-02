# 07 — Security & Containment (#sec-ops) (v2)

**Version:** 2.0 · **Date:** 2026-09-01

The safety plane decides — before any action — whether it's allowed, contains it if it runs, scans the output, and records every failure. It is **first-party and deterministic** (principle #5).

---

## 1. Layers (defense in depth)

```
agent proposes tool/shell call
   ▼ (1) CEL POLICY GATE   deny-before-allow · missing policy denies · broken rule refuses · audit row FIRST
   ▼ (2) gVisor (runsc)     non-root USER · dropped caps · /workspace only · no docker socket exposed
   ▼ action runs
   ▼ (3) OUTPUT SCAN        secret scan · prompt-injection scan
   ▼ (4) ANTI-PATTERN REGISTRY   append-only; every failure logged (= distillation + corpus)
```

Harness hooks (Hermes `pre_tool_call`, Claude Code PreToolUse) are layer (1)'s preferred enforcement point, but **gVisor (2) is mandatory and independent** because: Hermes hooks can miss in some worker contexts, the Buzz-managed runtime auto-approves permissions, and **Pi has no built-in permission system at all**. Every harness runs under gVisor regardless of its hook support.

## 2. CEL policy gate (reimplemented first-party from OpenBot's pattern)

Do NOT adopt CopilotKit Intelligence. Extract only the rule surface + semantics.

- **Fields a rule may inspect:** `tool.name, intent, agent.id, owner.id, page.url, page.host, element.*, key, file.*, mcp.*`; helpers `contains()`, `matches()` (case-insensitive).
- **Semantics:** deny before allow; missing policy permits nothing; a rule that fails to compile refuses (malformed policy stops startup); **record-before-act** (resolve target → evaluate → write audit row → only then call the tool). Secrets in the audit row: "requested/supplied, N chars" — never the value.
- **Interface:** `evaluate(action_ctx) → ALLOW | DENY | REQUIRE_CONFIRM` (audit row already written). Wire into Hermes `pre_tool_call` / Claude Code PreToolUse; enforce inside gVisor for Pi and any hookless harness.

## 3. gVisor containment
Run every harness's tool execution under `runsc`. **Non-root `USER` in every Dockerfile** (a missing USER silently weakens the sandbox). Drop caps; mount only `/workspace`. The supervisor holds the Docker socket — never expose it. Reserve strictest isolation for untrusted stages; test builds under runsc (some syscalls unimplemented).

## 4. Secret & injection scanning
- Secret scan on every tool output and every memory write (pre-commit): entropy + known patterns; block + log on hit. Canary tokens in Project scopes detect exfiltration and distillation leaks.
- Prompt-injection scan on any external content (web, repos, docs) before it enters a brain or a model turn — and treat untrusted page content as data, never instructions.
- Distillation identifier-strip (two-stage: rule scrub → independent verifier) before any upward promotion; a surviving canary fails the promotion (`05`).

## 5. Anti-pattern registry
Append-only markdown under `_global`/`sec-ops` scope; every failure = one entry (trigger, blast radius, detection, fix). Doubles as the distillation source and #sec-ops corpus; feeds the dream-phase self-heal (`05`).

## 6. Keystore & credentials
- **nsec keys** (agent identities): `keystore/keys.db`, `chmod 600`, never in git; whoever holds `BUZZ_PRIVATE_KEY` signs as the agent — crown jewel.
- Provider keys: env-injected at process start; never in a brain or log.
- **ai-memory auth:** loopback + bearer for LAN; DB-user tokens (`token_pepper`) per agent = per-agent identity; SSO via `actor_proxy_bearer_token` + `X-Memory-Actor-*` behind a trusted gateway. Data is single-tenant, no per-page RBAC → **sensitive agents get a dedicated in-gVisor ai-memory instance** (hybrid tiering).
- OmniRoute: set `INITIAL_PASSWORD` (default `CHANGEME`). HarnessRouter (Phase 2): `HR_AUTH_PASSWORD`+`HR_SECRET_KEY`, pin ≥0.3.0.
- Per-service secrets in the OS keychain / a secrets manager, not markdown. `CREDENTIALS_ENCRYPTION_KEY` = `openssl rand -base64 32`.

## 7. Supply chain
Agent CLIs (Claude Code/Codex/Hermes/Pi) pinned + checksummed; vendor to an internal mirror where possible. Dev-plane tools audited-before-install.

## 8. Hybrid-tier isolation summary
- **Default agents:** shared ai-memory store; logical isolation (operator token + `per_actor` + gVisor on the process).
- **Sensitive agents (#sec-ops):** dedicated ai-memory instance inside the gVisor sandbox (physical brain), federating to the hub for Team/Company reads. This is the only way to get hard per-agent confidentiality given ai-memory's single-tenant model.

Cross-refs: the retro gate + persona_lint → `06`; the promotion strip/gate → `05`; adapters → `08`.
