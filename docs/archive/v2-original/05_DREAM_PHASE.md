# 05 — The Dream Phase (propose → dispose distillation)

**Version:** 2.0 · **Date:** 2026-09-01

The dream phase is how lessons move *up* the scopes without a stochastic model ever holding write authority. Its one rule: **the model NOMINATES (soft); a deterministic pipeline DISPOSES (hard).** Propose is cheap and fuzzy; promotion is gated and reproducible. This is the same law Fubuki encodes (`records enter as 'proposed'; the write path cannot self-approve`) and ai-memory encodes (`require_approval` pending-writes) — three designs, one principle.

---

## 1. Direction matters — only push-up is gated

- **Pull-down (higher scope → agent) is free.** It's just the read path (`ScopeResolver` union + `_global`). No mechanism, no gate. An agent absorbing useful Project/Team/Company knowledge during work is a normal read.
- **Push-up (agent → project → team → company) is the ONLY gated direction** — that's where a wrong or leaky fact does damage by spreading. Everything below is about push-up.

## 2. The pipeline

```
① NOMINATE  (soft / stochastic / prompting)
   - in-loop: the agent flags "durable lesson" or "promote this fact"
   - at session-end: an automatic pass nominates what the agent didn't (liberal over-nomination is fine)
   - produces an ai-memory auto-improve PROPOSAL (pending-write), never a direct write
        │
        ▼
② STRIP  (deterministic)
   - identifier-strip: rule scrub → independent verifier → canary-token check
   - a canary that survives the strip FAILS the promotion (catches leaks)
        │
        ▼
③ PROVENANCE + STYLE GATE  (deterministic, first-party)
   - Fubuki persona_lint: VIOLATION blocks; REVIEW → human (06)
   - every promoted claim must carry provenance_class + confidence (memory-record schema)
        │
        ▼
④ RETRO GATE  (deterministic)
   - the "lesson" must survive an independent oracle + a de-vacuoused negative control
   - a claim that only passes a vacuous check is rejected (no hollow greens)
        │
        ▼
⑤ EVAL-GATE  (ai-memory native: [auto_improve.eval] command=… targets=[_rules,procedures] min_delta=…)
   - the strip+lint+retro checks run as the executable scorer; failure ⇒ rejected candidate, not a write
        │
        ▼
⑥ APPROVE  (human gate: [auto_improve] require_approval=true)
   - proposal stays pending until a human approves; then approve_auto_improve_proposal writes it
        │
        ▼
⑦ SCOPED WRITE UP one level (Wiki::apply_batch), identifiers stripped
   - project→team→company; invalidate-don't-delete; the same entry also lands in the anti-pattern
     registry (#sec-ops corpus) when it originated from a failure
```

Steps ②–⑦ are the deterministic DISPOSE half; ① is the soft NOMINATE half. The stochastic model can only ever produce a *proposal*; nothing it says lands until the pipeline passes.

## 3. Two tiers (stakes differ, so the mechanism differs)

- **Agent → Project (low stakes, high frequency):** the agent does it in-loop and at its own session-end. Project scope is tactical and short-lived. Prompting-heavy; over-nomination encouraged; the eval-gate still guards the write.
- **Project → Team → Company (high stakes):** a **dedicated nightly CURATOR agent** runs the full deterministic pipeline across *all* scopes — dedupe across agents, synthesize a Team heuristic from what several agents nominated, enforce the hard gate before anything reaches Company. No single stochastic agent holds cross-scope write authority; the curator only proposes into the same gated pipeline.

The curator maps onto ai-memory's `[auto_improve.scheduler]` (cadence: `interval_secs`, `max_sessions_per_tick`, `min_session_age_secs`) + the rule-based `curator` (dedupe/staleness report) + the strip/lint/retro scorer + `require_approval`. It is a member of the Genesis Team (`11`) and runs like any agent (own keypair, own Fubuki brain, behind the gate).

## 4. Consolidation (tidy ≠ promote)

Separately from promotion, ai-memory's session-end consolidation ("compile-not-retrieve") and the curator's maintenance pass **tidy within a scope** (dedupe, relink, flag stale). Consolidation does **not** verify truth — its output feeds the retro gate, it never substitutes for it. Keep consolidation (tidy) and promotion (dispose) as distinct jobs.

## 5. Mechanism-source slot (bring your dream repos)

The *cadence + nominate + tidy* mechanism is ai-memory's auto-improve/curator by default. If you adopt a richer "dream" mechanism from your own repos, it plugs in at ① (nomination) and ④ (retro scoring) only — it must not gain write authority. Candidates to compare when you pick: GBrain nightly dream cycle, Letta sleeptime consolidation, ai-memory's own scheduler. **Fill this slot after you choose; do not let a new mechanism bypass steps ②–⑥.**

## 6. Invariants (never violate)
- Nomination never writes; only the approved pipeline writes.
- Identifier-strip runs before any upward write; a surviving canary fails the promotion.
- Company (`_global`) is written only by this pipeline + a human.
- `persona_lint` VIOLATION and retro-gate failure both hard-block promotion.
- Consolidation may reorganize but must never lower the retro-gate pass rate (auto-revert if it does — `09`).

Cross-refs: `persona_lint` + provenance schema → `06`; the eval-gate/`require_approval` config → `04`; the distiller companion → `08`; the curator role → `11`.
