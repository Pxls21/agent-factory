# FINDINGS — Stage 0 proof pack (v1, 2026-09-02)

Constraint set for the Stage 0 pipeline run (council → Ouroboros interview → seed → task
breakdown). Owner decision 2026-09-02: **no research prompt for this cycle** — the v3 docs are
the settled direction; this findings doc is the grounded audit standing in for research-prompt
findings, per Feature Workflow step 1. Every claim below traces to a primary source read this
session or a probe run this session.

## 1. Current-state capability ledger (honest, for council/interview briefs)

| State | Items |
|---|---|
| **Proven live this session** | Planning docs verified (`scripts/verify-planning-repo.sh` green); operating kit installed and probed: Ouroboros 0.53.0 + stdio fallback round trip (`scripts/ooo_mcp.py --list` returned full tool surface via the isolated-uvx retry), gitnexus 1.6.10, codebase-memory-mcp 0.10.8, aleph venv, /council + /wiki-* skills, graft graph built |
| **Built, never run** | Nothing — no application code exists (`STATUS.md`) |
| **Absent** | Everything in `docs/07_BUILD_PLAN.md`: all Stage 0 proofs, spine, adapters, policy service, evaluation lab. Honey meter (install blocked by network). Wiki (`wiki-init` not yet run) |

## 2. Environment reality (probed 2026-09-02, this container)

| Capability | Probe result | Stage 0 consequence |
|---|---|---|
| Python 3.11.15, uv 0.8.17 | present | Hermes (0.21.0, Python) plausibly installable in-sandbox |
| Node 22.22.2 / npm 10.9.7 | present | OmniRoute (3.8.51, Node) plausibly runnable in-sandbox |
| Rust cargo/rustc 1.94.1 | present | ai-memory needs Rust 1.95 (`docs/02` §2) — toolchain update or prebuilt needed; buildability is a spike question |
| Docker CLI 29.3.1 | present, **daemon NOT running** (no /var/run/docker.sock) | Compose topologies unavailable unless dockerd-in-sandbox proves out (untested); plan spikes process-level first |
| runsc (gVisor) | ABSENT; /dev/kvm ABSENT | S0-08 cannot run here as-is; runsc static install + systrap platform is a spike question; otherwise S0-08 needs a real host — surface, never stub |
| bwrap | ABSENT (unshare present) | no bubblewrap isolation for local gates |
| uid | 0 (root) | root-start/priv-drop tests partially representable |
| Network | pip/npm/uv installs worked; raw.githubusercontent.com curl blocked; GitHub repo access is session-scoped — upstream clones need `add_repo` per repo (public read may be proxy-served) | Pinned upstream checkouts are feasible but each repo needs explicit attachment; record every failure honestly |

## 3. What Stage 0 is (source: `docs/07_BUILD_PLAN.md:5-20`)

Twelve proofs S0-01…S0-12, each an executable gate with exit evidence — the current CLAUDE.md
gate: no broad feature work until they validate. Contracts live in `docs/03_INTEGRATION_CONTRACTS.md`
(acceptance tests §1-§9), failure semantics in `docs/01` §5 and `docs/05` §3/§8, component
corrections in `docs/02`.

Per-proof constraints (doc-sourced):

| ID | Proof | Load-bearing constraints from the docs |
|---|---|---|
| S0-01 | buzz-acp launches pinned hermes-acp | ACP initialize/prompt/stream/cancel/shutdown fixture vs pinned protocol (`03` §1.3); pin Buzz+buzz-acp+ACP+Hermes together; idle 900s selected over source-default 1500s / README 620s (`02` §2) |
| S0-02 | Buzz authorization/freshness | Negative legs are the point: unauthorized/invalid/replayed/stale/self-authored produce NO turn (`03` §1.2); NIP-OA `created_at` is not revocation (`02` §2) |
| S0-03 | Hermes→OmniRoute | `codex_responses` provider, key_env only, no upstream key in Hermes, real tool-call round trip; failure ≠ fallback (`03` §2) |
| S0-04 | Compression contract | `x-omniroute-compression: off` + assert `X-OmniRoute-Compression` response header + deterministic stub upstream proving request preservation — the stub is the planned boundary instrument (`02` §2, `03` §2), not a spine stub |
| S0-05 | No direct model egress | Network canaries FAIL from every non-OmniRoute unit (`05` §8) |
| S0-06 | Four-scope adapter design | Auth tuple validated outside model control; Agent→Project→Team→Company precedence; write only active scope; leak fixtures; same-workspace tokens ≠ RBAC (`03` §4, `04` §2) |
| S0-07 | Fubuki corrections | `persona_lint` exit-2 ordering bug fix/wrap + ordered regression fixture; `BoundDecision.record_id` join (no payload field); upstream suite ran 129 cases with one import failure = partial evidence (`02` §2, `04` §7) |
| S0-08 | gVisor compatibility | Hermes container root-start/s6 → drop to `hermes` under runsc; escape canaries fail (`02` §2, `05` §5) — environment-gated, see §2 |
| S0-09 | Foundry host decision | JIT five-file translation + OpenHarness extract/integrate/decline ADR; OpenHarness is a full harness, not a skeleton (`02` §3) |
| S0-10 | GBrain seam decision | wrap vs adapt spike, proposal-only proof, no admin creds (`02` §3, `04` §8) |
| S0-11 | Evaluation hardening | Hermes runner design + rubric isolation; stock AlphaEval runner unsafe (host net, chmod 777, cred passing) (`02` §3, `06` §2) |
| S0-12 | License/release policy | First-party license, notices, pins, SBOM/update procedure (`upstream.lock.yaml` is the pin set; LICENSE-DECISION.md exists) |

## 4. Cross-cutting invariants that bind the seed

- NO STUBS in the spine (CLAUDE.md #1): every proof exercises the REAL pinned component; the
  one sanctioned stub is S0-04's deterministic upstream-request-preservation instrument, which
  sits BEHIND real OmniRoute at the boundary the plan itself specifies.
- No-LLM-judge spine: all Stage 0 exit evidence is deterministic (exit codes, fixtures, header
  asserts, canary failures).
- Negative-control discipline: S0-02/S0-05/S0-08 are *defined by* their failing legs; every
  other proof needs at least one violating fixture failing for the exact expected reason.
- Fail-closed semantics: policy outage/malformed ⇒ deny (`03` §5, `05` §3); recall degradation
  is visible, `memory_required` uses a separate preflight because `pre_llm_call` fails open
  (`01` §5, `04` §4).
- Environment blockers are surfaced, not routed around: if gVisor (or dockerd) cannot run here,
  the proof is delivered as spec + fixture + explicit `NOT run here: <reason>` + host runbook,
  never a fake green.

## 5. Open questions

**PATH 1 (code/doc-answerable — resolve during interview from primary sources):**
1. Per-proof execution venue: which of S0-01…S0-08 run fully in-sandbox vs spec+fixture-only
   (resolved by attempting pinned installs — Hermes pip, OmniRoute node, ai-memory cargo).
2. Repo layout for first code (proofs/, adapters/, policy/ …) — pick the convention in the seed.
3. Fixture format for ACP conformance (pinned protocol commit supplies the schema).

**PATH 2 (human tradeoffs — put to the owner as text, don't block):**
1. Stage 0 ordering/parallelism: strict S0-01→S0-12 vs seam-parallel batches (spine proofs
   S0-01…S0-05 first, decisions S0-09/S0-10/S0-12 interleaved)?
2. Is a bridged host (real VM with gVisor+docker) planned for S0-08, or should Stage 0 accept
   spec+canary-fixture evidence with live execution deferred to Stage 1 infrastructure?
3. Which OmniRoute upstream provider(s) get real credentials for S0-03's live round trip, and
   who supplies them (secrets never enter the repo)?

## 6. Sources

`docs/01_ARCHITECTURE.md`, `docs/02_COMPONENT_AUDIT.md`, `docs/03_INTEGRATION_CONTRACTS.md`,
`docs/04_MEMORY_AND_GOVERNANCE.md`, `docs/05_SECURITY.md`, `docs/06_EVALUATION.md`,
`docs/07_BUILD_PLAN.md`, `STATUS.md`, `upstream.lock.yaml`, `.env.example` — all read in full
this session; environment table from probes run this session (recorded above).
