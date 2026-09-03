---
name: contract-gate
description: The adversarial contract loop for build increments — negotiate a concrete testable contract BEFORE building, build with a separate executor, grade with an independent adversarial evaluator against the FULL contract (never the builder's own cases), feed failures back in a bounded repair loop, fail CLOSED at the round budget. Use for every serious build increment and for any workflow that has build + verify stages; also when the user says "contract gate", "run it through the gate", or asks how to structure a build/verify fan-out.
---

> **HARNESS PORT.** This copy is read by Codex CLI (`.agents/skills/`) and by Hermes
> (via `skills.external_dirs`). It is the same protocol as `.claude/skills/contract-gate/SKILL.md`;
> only lines naming a Claude-Code-specific mechanism were reworded — see `docs/HARNESS-PORTS.md`.
> "the project instructions file" = `AGENTS.md` on Codex, `.hermes.md` on Hermes.
> Model-tier names below ("Fable light", "Opus 5 lane") are PROTOCOL LABELS, not routing
> instructions: these harnesses run ONE model. Where the protocol calls for an independent
> verifier, hand the work BACK to the sandbox lane — never self-accept.

# Contract gate

Source: Anthropic, *Build Agents That Run for Hours* (39:00 — "self-evaluation, very much a
trap. Just use an adversarial evaluator."), via the Archive228/adversarial-contract-gate
distillation (MIT). Mapped onto THIS repo's stack. The already-standing laws it extends —
never self-accept, Phase-5 adversarial verify, negative controls — remain; this skill adds the
SPECIFIC loop shape and the contract negotiation step that precedes building.

## Why (the two lecture facts that shape the loop)

- **Critique is cheaper than creation** (20:05): a harsh standalone critic is tractable; a
  self-critical builder is not. So the evaluator is a SEPARATE agent with its own context and
  no stake in passing — never the builder re-reading its own diff.
- **The evaluator grades against the CONTRACT, not the original spec** (26:00): the loose spec
  is one-shotted; the contract is the negotiated list of concrete, testable assertions —
  including the edges the builder would skip.

## The loop (this repo's shape)

```
brief/seed ─► 1. NEGOTIATE contract ─► recorded in the task/breakdown (pre-registered)
                        │
              2. BUILD (code-implementer agent — Opus 4.6 lane)
                        │  self-declared cases prove nothing
              3. EVALUATE (adversarial-verifier agent — Opus 5 lane, separate context,
                        │  graded against the FULL contract)
              4. failures ──► back to 2 (builder receives the verbatim failure list)
                        │
              ≤3 rounds; still failing ─► FAIL CLOSED: surface the blocker to the
                                          main loop / owner. Never soften the contract
                                          to mint a pass.
```

1. **Negotiate the contract BEFORE any code.** The coordinator (main loop) turns the brief /
   seed acceptance_criteria into a numbered list of concrete, executable assertions. It MUST
   include:
   - the edge classes this repo's incident log keeps paying for: NaN / ±inf / empty /
     zero-range / post-scaling degenerates / timeout / stale-or-truncated identifiers;
   - at least one NEGATIVE control (a violating input that must fail for the exact expected
     reason);
   - identity/state assertions (the exact entity served, the artifact actually changed), not
     returned flags.
   Record the contract in the task/breakdown BEFORE dispatching the builder — pre-registered,
   like an empirical-validation verdict rule; it cannot be quietly edited after seeing the
   build. Amending the contract mid-loop requires a stated reason at coordinator level (the
   drop-don't-rewrite oracle rule applies).
2. **Build.** Dispatch `code-implementer` (Opus 4.6) with the brief + contract — on a
   single-model harness, build it yourself against the contract. The builder's own test runs
   are working feedback, not acceptance evidence.
3. **Adversarially evaluate.** Dispatch `adversarial-verifier` (Opus 5) with the contract and
   the diff — a separate context that did not watch the build. It executes the full contract
   plus its minimum attack set and returns the verbatim failure list. **On a single-model
   harness this step cannot run locally — hand it back (see "Harness mapping" below).**
4. **Repair loop.** Failures go back to the builder as data (`build(failures)`), not as a new
   design conversation. Bounded: 3 rounds default. Budget exhausted → the increment is BLOCKED,
   reported honestly; never route around with a stub or a softened assertion.
5. **Coordinator verdict.** The main loop re-runs the deterministic gates itself before commit
   (never self-accept applies to delegates too — an evaluator PASS is evidence, not authority).

## Harness mapping — ON THIS HARNESS YOU ARE NOT THE EVALUATOR

The sandbox lane runs steps 2 and 3 as two different models in two contexts: a builder, and an
adversarial evaluator that did not watch the build. **Codex and Hermes run ONE model.** You
cannot supply step 3 by grading your own diff — an evaluator that watched the build is the
hollow green this whole loop exists to prevent.

So on this harness:
- You may do step 1 (negotiate the contract) and step 2 (build against it).
- **Step 3 is HANDED BACK.** Emit the contract, the diff, and your own test output as a
  package for the sandbox `adversarial-verifier` lane. Say plainly that step 3 has not run.
- Steps 4 and 5 belong to whoever ran step 3. You never issue the verdict.

A single-model harness may run the contract's deterministic assertions and report their raw
output — that is instrument data, not an evaluation. Never label it a PASS.

## Lessons baked in from live rounds (SF-4, 2026-07-28)

1. **Every contract PINS the gate instrument**: the exact interpreter/entrypoint for test runs
   (here: `/root/venv-agent-factory/bin/python -m pytest` from repo root). The SF-4 builder graded
   itself on a python that couldn't import the vendored engine — all its numbers were
   artifacts, and only the evaluator's re-run in the right env exposed 3 new reds. An
   unpinned instrument makes every downstream clause unfalsifiable.
2. **Scope contracts by CHANGE-CLASS, not file count.** "Touches exactly N files" collided
   with the stale-comment law and the pad-stage precedent, forcing a mid-loop amendment.
   Say instead: "the scaffold-emitted class + count-assert class + pad/compat class +
   doc-count class; anything outside these classes is a violation."
3. **The evaluator diffs PROVENANCE ARTIFACTS against the commit.** The saved scaffold
   output (`runs/gene_scaffold/x60.diff`) caught a silent post-apply hand-edit that no test
   could see. Any generator-produced increment: regenerate/compare, or diff the emitted
   artifact.
4. **Acceptance = ONE full-tree sweep, never directory batches.** The repair round's
   batched runs looked green but didn't sum to the collection count; only the coordinator's
   single sweep was admissible. Batched runs are working feedback, not acceptance evidence.
   **Corollary (SF-3b): VERIFY the pinned instrument actually TERMINATES before writing it
   into a contract** — the SF-3b contract pinned "full-tree from repo root", an invocation
   that does not exist (no pytest config; 45 pre-existing collection errors, RC=2, zero
   tests executed), which made the builder's honest report look like the artifact and the
   contract clause unfalsifiable in the other direction. Until #395 lands a canonical
   sweep, contracts pin an explicit blast-radius PATH SET instead.
5. **A guard clause needs a REACHABILITY check and an ORIGIN-traced raise (SF-3b F1/F4).**
   Two paired hollow forms, both shipped green in one increment: the production guard
   compared a hardcoded literal against itself (constant-False dead code), and its test
   re-implemented the guard INSIDE the test body and asserted its own inline raise —
   never invoking the production function at all. Evaluators: trace the exception's
   traceback to the PRODUCTION frame, and prove the guard's condition is reachable from
   a real call path (a parameter, not a literal).

## Honest limits (from the source, still true here)

The adversary is only as good as the contract — a weak contract passes weak builds. The value
is in negotiating assertions that cover the edges, which is why step 1 is coordinator work,
not boilerplate.
