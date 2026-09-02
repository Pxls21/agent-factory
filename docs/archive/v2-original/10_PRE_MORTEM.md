# 10 — Pre-Mortem (v2)

**Version:** 2.0 · **Date:** 2026-09-01

Assume it's six months on and the system failed or is fragile. Ranked by severity × likelihood; each mitigation is reflected in the specs. A living skeleton follows — add a row every time something breaks.

---

## 1. Ranked failure modes

| # | Failure mode | Trigger | Blast radius | Detection | Mitigation (see) |
|---|---|---|---|---|---|
| 1 | **OmniRoute mutates code bytes** | compression left on the code lane | every agent (sole egress); corrupted diffs merge | byte-echo canary; span compare | compression OFF on code lane; canary in CI+runtime; re-verify patches post-egress (`08` G) |
| 2 | **Gate bypass on Buzz-managed / Pi path** | Buzz auto-approves; Pi has no perms | any such agent; `rm -rf`, exfil | no approval; unlogged shell | **gVisor mandatory & independent**; forbid Buzz-managed runtime for privileged agents; Pi only in gVisor (`07`, D3) |
| 3 | **Distillation leaks identifiers UPWARD** | strip misses a datum on promotion | Team/Company scopes poisoned | secret scanner + canary on promotion | two-stage strip + independent verifier; surviving canary fails promotion (`05`, `07`) |
| 4 | **ai-memory scope-escape** | compromised agent queries sibling scopes | cross-agent memory leak | per_actor fallback test; audit | `per_actor` + capability auth + **dedicated instance for sensitive agents** (single-tenant, no RBAC) (`04`, `07`) |
| 5 | **auto-improve auto-approves** | `require_approval` left false | ungated promotions land | pending-writes audit shows auto-approve | set `require_approval=true`; register the eval-gate scorer (`04`, `05`) |
| 6 | **Fubuki packet hash not enforced** | `pre_llm_call` hook not wired / flaky | brain tampering undetected | hash-pin heartbeat; verify at loader too | verify at BOTH loader and hook; block on mismatch (`06`, `08` A) |
| 7 | **Company summary shadows Project findings** | over-general heuristic promoted | agents reading `_global`; confident-wrong | provenance labels + scope precedence | summary links to evidence; contradiction ⇒ `uncertain`; Project>Company for specifics (`02`) |
| 8 | **Wiki↔SQLite divergence** | direct SQLite write / crash mid-write | memory correctness | reindex-from-wiki diff | markdown authoritative; only `Wiki::write_page/apply_batch`; reindex on divergence (`04`, `09`) |
| 9 | **Bounds engine bypassed** | compiler receives raw memory | restricted/sensitive leak into packet | packet audit vs bounds decisions | compiler only ever gets `bounded_context` from `bounds.py`; never raw (`06`, `08` B) |
| 10 | **Root container escape** | Dockerfile without `USER` | host compromise despite runsc | image scan for USER | non-root USER + runsc + dropped caps + socket unexposed (`07`) |
| 11 | **Retry spawns a second writer** | idempotency-less retry | duplicated/corrupted page | duplicate-write detector | ai-memory single-writer actor serializes; idempotency key on turns (`04`) |
| 12 | **ai-memory eval-gate can't hard-block** | `[auto_improve.eval]` advisory only | un-vetted promotion writes | promotion audit | verify it blocks; else patch pending-writes→approval in `ai-memory-consolidate` (D9, `04` §7) |
| 13 | **Fubuki floats/non-determinism** | a float sneaks into a canonical structure | hash instability | `_reject_floats` raises; conformance vs golden packet | ints/strings only; test against `expected-packet.json` (`06`) |
| 14 | **OmniRoute single point of failure** | egress process down/quota | all model calls stop | health probe `/v1/models` | supervised restart + fallback tiers; gate-critical calls off shared egress (`03`) |
| 15 | **Fallback swaps provider mid-task** | quota trip → tier drop | quality drift; nondeterministic verifier | per-span model attribution | pin model on gate-critical turns (`08` G) |
| 16 | **Buzz single-relay downtime / random key** | relay dies; `BUZZ_RELAY_PRIVATE_KEY` unset | whole Interface plane; discovery breaks | health probe; roster gap | HA relay; PG/Redis replicas; **pin the relay key** (`03`) |
| 17 | **PandaProbe silently on** | env vars present (auto-init) | unexpected tracing/egress | startup env audit | keep env unset / `PANDAPROBE_ENABLED=false`; judge via OmniRoute (`03`) |
| 18 | **NIP-OA revocation misunderstood** | key rotation/revocation semantics unverified | agent accountability ambiguous | read `buzz-acp` NIP-OA path | confirm revocation removes agent without touching human identity (D4) |
| 19 | **Hollow greens** | gate reports pass without running check | bad merges | evidence commit-lint | ban "verified" w/o command+output; roles can't grade own work (`06`) |
| 20 | **Licensing trap** | Hermes license unconfirmed; Intelligence dependency | redistribution risk | license audit | verify Hermes before imaging; reimplement CEL first-party (`06` D5) |

## 2. Living skeleton (copy per incident)
```
### PM-<n>  <title>
- Date / stage:
- Trigger:
- Blast radius (scopes/agents/data/plane):
- Detection (canary? gate? human?):
- Root cause:
- Fix:
- Mechanism added (test/gate/monitor so it can't recur silently):
- Anti-pattern registry id:
- Fault class (protocol/containment/data-integrity/data-authority/verification/isolation/SPOF/config/licensing):
```
Every entry ends with a *mechanism*, not just a fix, and is written to the anti-pattern registry (feeds `05`).

## 3. The one-question gate audit
Count how many of a gate's inputs are self-reports from the component being gated. Drive it to zero.
