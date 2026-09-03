---
topic: security-and-containment
last_compiled: 2026-09-03
---

# Security and Containment — policy gate, gVisor, egress, threat model

## 1. Purpose [coverage: high -- 6 sources]

Security is structural: the system enforces that a model, generated harness, or dream worker
cannot bypass human authorization. All model/embedding traffic goes through OmniRoute. Runtime
and research code is contained from host, other scopes, secrets, and unrestricted egress.
Inbound/recalled/generated content cannot silently become governance. Memory and harness promotion
is attributable, tested, reviewable, and reversible.

**No security control has been implemented.** The threat model, policy semantics, and acceptance
gates are specified in the planning docs; the Stage 0 proof pack validates them.

## 2. Architecture [coverage: high -- 5 sources]

**Policy service** (planned first-party): deny before allow; any deny wins; broken deny rule
denies; broken allow grants nothing; no match/unknown denies; canonical modified arguments
re-evaluated; every decision includes its policy and governance hashes. May use CEL-compatible
engine. Hermes `pre_tool_call` hook with `fail_closed: true`.

**gVisor** (runsc): contains the whole Hermes runtime initially. Not per-tool isolation without
a broker. Research/evaluation workers also use isolated gVisor profiles. Container starts as root
for s6/UID setup, then drops to `hermes` user -- test this lifecycle under runsc.

**Egress enforcement**: no upstream model/embedding keys outside OmniRoute. Network canaries
fail from every non-OmniRoute unit (S0-05). OmniRoute is sole model API egress, not
automatically sole web/tool egress -- tool/web needs its own proxy and policy.

**Egress mechanism**: bare `unshare --net` is proven TOTAL isolation (blocks host-local
listeners too -- Chairman probe, AF-AP-1). Selective egress (allow OmniRoute, deny model
endpoints) requires veth/proxy, never bare unshare. S0-05 is split: mechanism in Wave 0,
full architectural proof in Wave 2.

Key files: [docs/05_SECURITY.md](docs/05_SECURITY.md),
[SECURITY.md](SECURITY.md),
[docs/03_INTEGRATION_CONTRACTS.md](docs/03_INTEGRATION_CONTRACTS.md) SS5-SS8.

## 3. Talks To [coverage: medium -- 4 sources]

- Policy service <-- Hermes `pre_tool_call` hook (every effectful tool call)
- gVisor contains the whole Hermes runtime (networking, filesystem, syscall filtering)
- Egress enforcement --> OmniRoute (allowed) / model endpoints (denied)
- Fubuki governance hash --> policy decisions, audit trail
- Evaluation/research workers --> separate gVisor profiles, no production secrets

## 4. API Surface [coverage: medium -- 3 sources]

Planned policy semantics (from [docs/05_SECURITY.md](docs/05_SECURITY.md) SS3):
- Deny before allow; any deny wins
- Broken deny rule denies; broken allow grants nothing
- No match/unknown input denies
- Canonical modified arguments re-evaluated
- Every decision includes policy and governance hashes
- `POLICY_URL`, `POLICY_CLIENT_TOKEN`, `POLICY_BUNDLE` in [.env.example](.env.example)

## 5. Data [coverage: low -- 2 sources]

- Policy bundle: `POLICY_BUNDLE=/etc/agent-factory/policy/policy.bundle.json`
- Audit decisions: versioned decision log with policy/governance hashes
- Canary and honeytoken records: planned for leak detection and egress tests

## 6. Key Decisions [coverage: high -- 5 sources]

- D-009: fail-closed `pre_tool_call` hook for tool authorization
- D-010: gVisor contains whole runtime initially (per-tool needs a broker)
- S0-05 split (council + Chairman): mechanism (selective egress) in Wave 0, full proof in Wave 2
- AF-AP-1: bare `unshare --net` is total isolation, not selective egress -- veth/proxy required
- Council KC-1: if Wave-0 mechanism spike cannot demonstrate selective egress, S0-05 placement
  is invalidated
- Prompt instruction is not a security control (AGENTS.md rule 9)
- No secret in any subprocess, trace, memory, dream, Foundry, or evaluation artifact

## 7. Gotchas [coverage: high -- 6 sources]

**NOT-built (first-class):**
- No policy hook or decision service
- No gVisor deployment proven on any host
- No egress enforcement or canary suite
- No memory delete/promotion surface restrictions
- No Buzz membership revocation or independent freshness
- No GBrain/JIT sandbox, no AlphaEval runner hardening
- runsc absent on the PC; KVM modules unloaded (owner `sudo modprobe kvm_amd`)

**S0-08 status:** blocked on capability -- runsc install spike on the PC pending. gVisor's
systrap platform does not need KVM, but the install itself has not been attempted.

**Premortem risks (#5, #6, #7, #8, #13, #14):** dream worker as hidden writer, JIT candidate
reaching production without review, generated harness passing quality but violating security,
policy outage failing open, direct provider path returning during debugging, AlphaEval runner
compromising host.

**Stop-the-line conditions** (10 enumerated in [docs/09_PREMORTEM.md](docs/09_PREMORTEM.md)):
any of them halts deployment/promotion.

## 8. Sources

- [docs/05_SECURITY.md](docs/05_SECURITY.md)
- [SECURITY.md](SECURITY.md)
- [docs/02_COMPONENT_AUDIT.md](docs/02_COMPONENT_AUDIT.md)
- [docs/03_INTEGRATION_CONTRACTS.md](docs/03_INTEGRATION_CONTRACTS.md)
- [docs/09_PREMORTEM.md](docs/09_PREMORTEM.md)
- [docs/INCIDENT-LOG.md](docs/INCIDENT-LOG.md)
