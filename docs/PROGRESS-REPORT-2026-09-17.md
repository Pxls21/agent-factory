# Agent Factory — Progress Report & Reviewer Handoff (2026-09-17)

**Audience:** an external code reviewer (e.g. OpenAI Codex) about to do a deep pass over the
commit history of branch `claude/soundbox-kit-migration-iz1jwf`.
**Purpose:** give you the context to judge the work honestly — what was built, what was only
*proven at the seams*, what was *decided*, and what is **not built yet**. This document is written
to be checked against primary sources, never to flatter. Where it claims a thing is done, the file
and mechanism are named so you can falsify it.

> **Read this first, then trust the repo over this doc.** The single source of truth for build
> status is `todo/BUILD-TASKLIST.md` (the "ledger"). The authoritative decision record is
> `docs/08_DECISION_LOG.md`. This report is a distillation and can drift; on any disagreement, the
> ledger and the decision log win.

---

## 1. What this repository actually is

Agent Factory is a **planning-stage repository** for a governed, memory-aware agent system. Two
things live here, and it is important not to confuse them:

1. **A Stage 0 "proof pack"** — an executable evidence harness that proves the *integration seams*
   of a production pipeline behave correctly, before that pipeline is built. The production
   components themselves (Buzz, Hermes, OmniRoute, Fubuki, ai-memory, gVisor) are **upstream
   dependencies**, audited and pinned by commit/digest in `upstream.lock.yaml` — they are **not**
   this repo's code. Stage 0 asks: *do the seams between them hold?*
2. **The first application code** — `src/agent_factory/` — the Stage 3 governance core, landed
   2026-09-15, built from the one proof that had been minted for it (S0-07). Its independent verify
   round is still pending.

The intended production pipeline (context, not built here):

```
people in Buzz → buzz-acp → Hermes (native ACP server, the sole stock runtime)
   → every model request through OmniRoute → approved models
   with Fubuki (hash-pinned governance), ai-memory (four logical memory scopes),
   and every tool call passing a fail-closed policy gate inside gVisor containment.
A separate improvement plane (GBrain dream cycles → JIT Harness Foundry → isolated
AlphaEval/PandaProbe evaluation → human promotion gate) feeds reviewable proposals only.
```

The 15 **Standing Project Rules** that constrain every change are in `CLAUDE.md` (and mirrored in
`AGENTS.md` / `.hermes.md`). The load-bearing ones for a reviewer: Hermes is the sole production
runtime; OmniRoute is the sole model egress; every effectful tool passes a fail-closed policy hook;
deterministic evaluation before any LLM-judge; every dependency pinned; nothing is called
"runnable" until an executable acceptance gate passes.

---

## 2. Honest status snapshot

### 2.1 Stage 0 proofs — 5 of 12 artifacts minted, 1 accepted

The proof denominator is **four-way**, not a flat count: *execution proof* vs *conformance-checked
decision* vs *blocked-on-external-input* vs *blocked-on-capability*. Current state
(`python3 scripts/validate-ledger stage1-gate`; `PROOF-STATUS:` lines in the ledger):

| Proof | What it proves | Artifact | Status |
|---|---|---|---|
| **S0-11** | evaluation/rubric isolation hardening | `result.json` minted | **ACCEPTED** (owner, after 7 review cycles) |
| **S0-07** | Fubuki governance corrections | `result.json` minted | REVIEW-PENDING |
| **S0-09** | Foundry host decision + conformance shell | `result.json` minted | decision (ADR) |
| **S0-10** | GBrain seam decision + conformance shell | `result.json` minted | decision (ADR) |
| **S0-12** | license/release policy + SBOM pin-diff shell | `result.json` minted | decision (ADR) |
| **S0-01** | ACP conformance (buzz-acp launches pinned hermes-acp) | none | in verify rounds — nothing minted |
| **S0-02** | Buzz authorization / freshness (distinct denials) | none | in verify rounds — nothing minted |
| **S0-04** | compression contract (sanctioned deterministic stub behind real OmniRoute) | none | in verify rounds |
| **S0-05** | full no-direct-egress over live units | none | in verify rounds |
| **S0-06** | four-scope memory adapter | none | in verify rounds — nothing minted |
| **S0-03** | Hermes→OmniRoute live round trip | none | **BLOCKED (credential)** — deferral expired; needs the live run |
| **S0-08** | gVisor containment | none | **BLOCKED (host)** — deferral expired; needs runsc on the PC |

**Do not read this as "Stage 0 is done."** It is not. `validate-ledger stage1-gate` currently
reports the execution proofs for S0-01/02/04/05/06 as *missing*, and S0-03/08 as *blocked, deferral
expired*. Stage 1 is gated behind that pack closing. The `stage1-gate` CI job is intentionally
`continue-on-error` and expected-red until the pack mints.

### 2.2 First production code — landed, verify pending

`src/agent_factory/` exists (landed 2026-09-15 by decision D-029, "build what has proofs in
parallel with the remaining proofs"):

```
src/agent_factory/governance/  packet.py  bounds.py  projection.py  review.py  pin.py  __init__.py
src/agent_factory/audit/       events.py  __init__.py
```

This is the Stage 3 governance core distilled from the S0-07 proof: pinned-fubuki verification,
canonical compile + sha256 governance hash, an immutable Hermes projection written atomically, a
BoundDecision→source-record join with per-decision audit events. **Its adversarial verify round is
not complete** — treat it as landed-but-unverified.

### 2.3 Scale and cadence

- **738 commits** on the branch (branch point ~2026-09-02).
- **34 decisions** (`docs/08_DECISION_LOG.md`, D-001…D-034), **9 ADRs** (`docs/adr/`).
- **96 anti-pattern registry rows** (`AF-AP-*` atop `docs/INCIDENT-LOG.md`) — every real defect found
  is registered with a greppable signature; ~half of the value of this project is in that registry.
- **55 test files**, **2766 tests passing** in CI's blocking `tests` job (1 known-red today, see §7).

Commit histogram by day (branch), commits/day — the shape shows the parallel-lane bursts:

```
2026-09-02 |█████  9
2026-09-03 |████████████████████████████████████████████████  89
2026-09-04 |███████████████████████  42
2026-09-05 |██████████  18
2026-09-06 |████████████████████████████████████████  72
2026-09-07 |█████████████████████████████████████  67
2026-09-08 |████████████████████████████████████████████████████████████████████████████████  144
   (2026-09-09 … 2026-09-13: owner away / cloud-quota pause)
2026-09-14 |████████████████████████████  50
2026-09-15 |████████████████████████████████████████████████████████████████  117
2026-09-16 |██████████████████████  40
2026-09-17 |██████████████████████████████████████████████████  90
```

---

## 3. The Stage 0 proof system (understand this before judging any proof)

The engineering heart of this repo is not the individual proofs — it is the **machinery that makes
a proof hard to fake**. A reviewer should attack that machinery first.

- **`proofs/registry.yaml` + `proofs/schemas/`** — every proof declares its legs (positive and
  negative controls), the exact commands, expected exit codes, and per-negative failure reasons.
- **`scripts/proof-runner`** — the canonical runner. It executes the declared legs, records the
  observed outcomes, and mints `proofs/<id>/result.json` **only** if reality matches the contract.
  On a real (non-defer) failure it **deletes/invalidates** the artifact by design.
- **Attested inputs (AF-AP-56, AF-AP-31).** A `result.json` hashes its **entire trust closure** —
  the runner, the validator, the registry, the schemas, and the proof's own files. Change any of
  those and the green no longer validates; you must regenerate. This closes the "neuter the checker,
  keep the stale green" hole, which was found and fixed *repeatedly* (see the S0-11 cycle history in
  the ledger — seven review cycles, each closing an equivalent-out).
- **`scripts/validate-ledger`** — re-derives the attestation from the tree and binds every recorded
  run to the attested spec one-for-one. `integrity` must read PRESENT, never INVALID.
- **The mint gate** is deliberately conservative: a proof that cannot run in the sandbox runs on the
  owner's PC over a bridge, or is delivered as *spec + fixture + an explicit `NOT run here: <reason>`
  marker* — **never a fake green**.

**The governing rule (CLAUDE.md #1):** *no stubs, no fakes, no shortcuts — surface the blocker
instead.* The only two sanctioned stubs in the whole repo are named explicitly (S0-04's
deterministic upstream-request instrument and S0-01's scripted model backend), and both sit *behind
real OmniRoute* at the boundary the plan itself specifies. Everything else exercises the real pinned
component. The anti-hollow-green tactics (negative control on every gate, mutation-testing as the
hollow-green detector, oracle independence, two independent instruments for any reachability claim)
are in the `anti-hollow-green` skill and are applied throughout — **please try to break them.**

---

## 4. The governance ACCEPTED anchor (you will hit this in CI)

Acceptance of a proof is **owner-only and cryptographically anchored**, not a word in a file
(`docs/governance/README.md`, `scripts/check-proof-status.py`):

- A proof the owner accepts is anchored by a **GPG-signed annotated tag** `accepted/<proof-id>`,
  verified against the owner's committed public key (`docs/governance/owner-signing-key.asc`) in an
  isolated keyring at check time, on a commit holding a byte-identical `result.json`.
- Because the sandbox git proxy refuses tag pushes and CI clones without tags, the signed tag
  **object** is *also committed as a content-addressed file* (`docs/governance/tags/accepted-<id>.tag`).
  The checker imports and verifies that object when the ref is absent — this is the designed CI path.
- The coordinator (the AI build loop) can write a `REVIEW-PENDING` line and a visible
  `PROOF-ANCHOR: <id> = PENDING-OWNER-TAG` *warning*, but it **cannot** mint an ACCEPTED — only the
  owner's signature can. This separation (AF-AP-32) was itself the subject of three review cycles.

Reviewer note: a stale test that keyed on the git ref alone (not the committed object) was fixed
2026-09-17 (`tests/test_proof_status.py`, commit on this branch) — worth confirming the fix matches
the checker's real predicate (`_anchor_findings`, ref **or** committed object).

---

## 5. What was built with the Qwen models

This is a real, load-bearing piece of infrastructure, built 2026-09-14…16 (decisions D-027, D-028,
D-032, D-033; ADR-0007; `docs/LOCAL-MODEL-GUIDE.md`, `PC-BRIDGE.md`).

**The problem it solved:** ~3 weeks of build time were lost to cloud model quota. The owner's PC has
one RTX 3090.

**What was built:**
- A **local Qwen3.8-27B** server on the 3090, reachable **only through OmniRoute** (rule 3 — sole
  egress preserved; nothing talks to the model port directly). First as a llama.cpp unit
  (`qwen-builder`, D-027), then productionized as a **digest-pinned vLLM container** (D-032,
  `deploy/qwen.container`, image `ghcr.io/syv-ai/qwen38-27b-rtx3090@sha256:c52d9033…`, boot-persistent
  Quadlet). The vLLM container is the keeper because of concurrency: measured ~45 tok/s single-request
  decode scaling near-linearly to **~310 tok/s aggregate at 7 concurrent lanes** (vs llama.cpp's
  ~62 single / ~93 at 4-up). That concurrency is what makes many parallel build/verify lanes affordable.
- **Two OmniRoute routes:** `agentfactory-build-local` (BUILD lanes, effort `medium`) and
  `agentfactory-verify-local` (VERIFY lanes, effort `xhigh`). The effort split is decision **D-028**,
  chosen from a real A/B: `medium` reached `113 passed` in 4h53m and flagged a false brief premise at
  14 min; `xhigh` reached `119 passed` in 6h41m — so `medium` builds, `xhigh` verifies, and speed is
  pursued only on lossless levers, never by raising build effort.
- **A production carve-out (D-033, ADR-0007):** Buzz's own `buzz-agent` can use the same local Qwen
  as a **chat-only teammate** through OmniRoute (proven live 2026-09-16). Hermes stays the primary
  runtime for coding/governed work; the teammate path is chat-only until a rule-9 policy gate is
  wired.

So: the Qwen model is not a product feature — it is the **compute substrate** that let a single
coordinator run many disjoint implementation and verification lanes in parallel at near-zero marginal
cost, behind the same sole-egress boundary the production system requires.

---

## 6. How the work was actually produced (the multi-agent build system)

The commits you'll review were not written by one linear author. The build ran as a **coordinator +
fan-out-of-lanes** system, and understanding it explains the commit shape:

- **Coordinator (the main loop)** owns design, root-cause, the contract gate, and the final verdict.
- **BUILD lanes** run on the PC via Hermes (`scripts/pc_lane.sh`), each on a disjoint set of files,
  pinned to a specific commit ("PIN"), producing code + a deterministic LLM-free test + its own
  contract-gate pass. The coordinator grades a *self-validated* report, then re-runs the gates itself
  (a "Reflection Firewall" — the coordinator never self-accepts a lane's spine work).
- **VERIFY lanes** (`adversarial-verifier`) attack a finished increment against the *frozen contract*,
  reproducing every load-bearing claim through the real production path, and emit a **GATE
  RECOMMENDATION** (`MERGE-READY` / `-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) — never a
  self-serving verdict. The coordinator owns the final gate. This is decision **D-031** (validation
  closure: exhaustive discovery, bounded blocking — a finding blocks only if it meets a 5-part
  predicate).
- **The PC bridge** (`scripts/pc.sh`, `PC-BRIDGE.md`) is the remote-execution host for everything
  heavy or live: containers, gVisor, model round-trips, long suites. The sandbox is for parallel
  development and rollback safety.
- **A code-intelligence quartet** (Graft + GitNexus + Codebase-Memory + code-review-graph, plus
  ripwire/sentrux/slopo as advisory-only instruments) is used as a *reflex* before edits and for
  reachability claims — `scripts/lane_context.sh` bundles it into one "pack" per lane.
- **Honey** is a reflexive compression style for agent-to-agent handoffs; safety-critical content
  (auth, secrets, validation) is never compressed.

Reviewer caution: the commit messages are **reasoning records** (rejected alternatives, ordering
rationale, primary sources) — they're worth reading, not skipping. Test counts and timestamps in them
are pasted from tooling, not typed (AF-AP-37).

---

## 7. The pipeline that produced the plan ("committees")

Before any Stage 0 code, the direction was settled by a deliberate pipeline (this is what the phrase
"the committees" refers to — the deliberation stages), all preserved in the repo:

1. **Findings** — `docs/research/FINDINGS-STAGE0-v1.md` (capability ledger, environment table,
   per-proof constraints).
2. **Council debate** — a multi-persona `/council` deliberation over the *findings* (facts, not
   hypotheses), landing `docs/research/COUNCIL-VERDICT-STAGE0-v1.md` (the wave plan + kill criteria
   KC-1…KC-7).
3. **Ouroboros interview** — an automated requirements interview seeded with the findings + verdict,
   driving ambiguity toward zero.
4. **Seed** — `seeds/seed-stage0-v1.yaml` (the frozen Stage 0 contract, self-validation 8/8, twelve
   per-proof blocks).
5. **Task breakdown** — `tasks/stage0-breakdown.md` (the 18-increment decomposition with pinned
   decisions and rejected alternatives).

The rule the pipeline enforces: **name which document is ground truth and read it before planning.**

---

## 8. CI and quality gates

`.github/workflows/stage0-ci.yml` has five jobs:

- **`tests`** (blocking) — `pytest tests/ -q`; currently **2766 passed** after the three baseline
  fixes this session (S0-02 venue gates `d2196bb`, CI git identity `a06641c`, the stale anchor test).
- **`harness-suites`**, **`ledger-integrity`**, **`planning`** — all green.
- **`stage1-gate`** — `continue-on-error: true`, **expected-red** until the Stage 0 pack mints. A red
  here is honest forward-gate behavior, not a regression — do not read it as a failure.

**Recent process decision D-034 (2026-09-17, "good-state"):** the build/verify loop drives each proof
to a GOOD STATE (headline capability proven through the real path, deterministic gates green) and
**stops** — only a *core-blocking* finding (headline capability actually fake) re-opens the build;
every other finding (oracle-completeness gaps, test-strength on pinned artifacts, edge cases) is filed
as a GitHub issue labelled `verify-followup` + `stage0` for later batch triage, not looped. Open
follow-up issues #3–#6 are exactly these deferred subtleties, and are worth a reviewer's eye as a list
of *known, deliberately-parked* imperfections. (D-034 was briefly mislabeled "D-033", which collided
with the Buzz-teammate ADR; that numbering collision was found and corrected the same day.)

---

## 9. What is NOT built (read this section twice)

A progress report that omits gaps is a hollow green in prose. The gaps:

- **There is no running production pipeline.** Buzz→ACP→Hermes→OmniRoute is upstream, pinned, and
  proven only at the seams Stage 0 covers. This repo does not run that pipeline end-to-end.
- **Stage 0 is incomplete.** 7 of 12 proofs are unminted: S0-01/02/04/05/06 are in adversarial verify
  rounds (nothing minted); S0-03 and S0-08 are **blocked on live/host runs** (a real OmniRoute round
  trip and gVisor/runsc on the PC) whose deferrals have expired — they must actually run.
- **Only S0-11 is owner-ACCEPTED.** S0-07 is minted but REVIEW-PENDING; S0-09/10/12 are decision
  shells, not live executions.
- **GOV1 (the first production code) has not passed an independent verify round.** It is landed, not
  blessed.
- **Observability ships nothing yet.** The PandaProbe plane is planned; components emit structured
  events but the PC-side sinks (OpenObserve, Phoenix) receive nothing (`docs/OBSERVABILITY-RUNBOOK.md`).
- **The wiki continuity spine is not initialized** (`wiki-init` has not run); the ledger is the only
  continuity source, by design, until it does.
- **Several proofs' live legs remain the owner's to capture** (e.g. S0-01's real-leg corpus needs a
  `run-2` leg; S0-02's live eight-leg capture; the S0-03 live legs). These are explicitly *not* faked
  — they are marked as pending real runs.

---

## 10. Suggested reviewer punch-list (where to push hardest)

1. **Attack the proof harness, not the proofs.** Can you mutate a checker or the runner and still get
   a green through `validate-ledger integrity`? The attestation (AF-AP-56/31/32) claims you cannot —
   verify that claim with a real mutation.
2. **The governance anchor.** Confirm `check-proof-status.py` cannot be satisfied by a
   coordinator-writable artifact, and that the committed tag-object path (`_anchor_findings`) verifies
   the owner's real signature — not merely the presence of a file.
3. **GOV1** (`src/agent_factory/governance/`): check the atomic write of the Hermes projection, the
   sha256 governance-hash canonicalization, the fubuki pin verification-before-use, and the
   BoundDecision→source join for a fail-open on malformed input.
4. **The two sanctioned stubs** (S0-04, S0-01): confirm they sit behind real OmniRoute at the declared
   boundary and don't stand in for the thing being proven.
5. **The blocked proofs (S0-03, S0-08):** confirm they are genuinely blocked-on-live-run, not quietly
   stubbed — and that the deferral markers are honest.
6. **The `verify-followup` issues (#3–#6):** sanity-check that each parked subtlety is genuinely a
   subtlety (test/oracle strength) and not a masked core-capability gap.

**Ground-truth reading order:** `todo/BUILD-TASKLIST.md` → `docs/02_COMPONENT_AUDIT.md` →
`docs/01_ARCHITECTURE.md` → `seeds/seed-stage0-v1.yaml` → `docs/08_DECISION_LOG.md` +
`docs/adr/` → `docs/INCIDENT-LOG.md` (the AF-AP registry) → the code under `proofs/`, `scripts/`,
`src/`, `tests/`.

*Prepared 2026-09-17. Every claim here is checkable against the named files; where this report and the
repo disagree, the repo is right.*
