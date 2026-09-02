---
name: contract-gate
description: The adversarial contract loop for build increments — negotiate a concrete testable contract BEFORE building, build with a separate executor, grade with an independent adversarial evaluator against the FULL contract (never the builder's own cases), feed failures back in a bounded repair loop, fail CLOSED at the round budget. Use for every serious build increment and for any workflow that has build + verify stages; also when the user says "contract gate", "run it through the gate", or asks how to structure a build/verify fan-out.
---

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
2. **Build.** Dispatch `code-implementer` (Opus 4.6) with the brief + contract. The builder's
   own test runs are working feedback, not acceptance evidence.
3. **Adversarially evaluate.** Dispatch `adversarial-verifier` (Opus 5) with the contract and
   the diff — a separate context that did not watch the build. It executes the full contract
   plus its minimum attack set and returns the verbatim failure list.
4. **Repair loop.** Failures go back to the builder as data (`build(failures)`), not as a new
   design conversation. Bounded: 3 rounds default. Budget exhausted → the increment is BLOCKED,
   reported honestly; never route around with a stub or a softened assertion.
   **THE CAP IS ENFORCED, NOT ADVISORY (owner mandate 2026-09-02 — RP-30b I3 ran SEVEN
   verify rounds under this very rule).** Round 3 returns NOT-READY → the coordinator does
   NOT author a round-4 repair brief. It stops, root-causes the CHURN in the main loop
   (why did the builder's exit gate pass what the verifier failed?), fixes the process
   defect (a missing gate stage, a mirror test class, a brief that named lines instead of
   tests), and only then re-enters at round 1 with the fixed process. A fourth brief for the
   same wave is a process failure by definition.
   **Round mechanics that stop the churn:**
   (a) **Verifier output = RED TESTS, not prose.** Every finding the verifier wants fixed
   ships as a committed failing test (or a mutant in the lane's `scripts/mutants/<lane>.py`
   manifest) in its report; a finding with no test is INFO, not a repair item. The repair
   brief is then literally "make these N tests green; do not edit them" — a builder cannot
   mis-read a red test the way it mis-reads a file:line paragraph, and cannot mark it fixed
   without it going green.
   (b) **Every lane exits through `scripts/lane_gate.sh <push-base> <gate-files.txt>
   [--mutants …] [--digest …]`** (builder AND verifier run the same script; the VERDICT
   block is pasted verbatim in the report and the commit body). It computes what rounds
   5-6 got wrong by hand: NEW pyflakes hits vs the push base, run1==run2 bitwise, reds
   partitioned NEW / PRE-EXISTING / FIXED against a `git archive <push-base>` run, mutant
   kill table, byte-identical-surface digest. A builder report without the VERDICT block is
   not a report.
   (c) **"Pre-existing" is proven ONLY against the PUSH BASE** (the SHA origin pointed at
   when the wave started) — never a mid-stack SHA. lane_gate.sh's `reds pre-existing=` line
   is the only admissible source of that word (I3g called a range regression pre-existing
   by comparing against 3c7ff08d, a mid-stack commit; the verifier caught it a round later).
   (d) **`scripts/hooks/pre-commit` blocks NEW pyflakes hits at commit time** (delta vs
   HEAD; `SKIP_LINT_DELTA=1` bypass is printed). Orphaned imports / AP-60 / AP-61 each
   cost a round before this hook existed; they now cannot reach a verifier.
   (e) **The gate file list is DERIVED, not curated (AP-63).** Gate set = the lane's own
   test files ∪ every test file that references a production symbol the diff touched
   (`git diff <push-base>..HEAD` function/method names ∩ `grep -l` over tests/). Write the
   derivation rule into the gate file's header and re-derive it at every repair brief — a
   diff that changes a shared symbol's contract is green on the lane's own files and red
   everywhere else (I3c-7 made `run_ga` require `problem.n_ieq_constr`; 13 of 14 run_ga
   consumer test files were outside the gate; 42 reds hid for four rounds). Until lane_gate
   grows a stage-0 derivation check, the brief author owns this step.
5. **Coordinator verdict.** The main loop re-runs the deterministic gates itself before commit
   (never self-accept applies to delegates too — an evaluator PASS is evidence, not authority).

## Workflow mapping

In a Workflow script: build stages use `opts.agentType: 'code-implementer'`, verify stages use
`opts.agentType: 'adversarial-verifier'` (owner stage-routing rule 2026-07-28: plan=Fable,
verify=Opus 5, build=Opus 4.6). The contract travels in both prompts; the failure list is the
only state the loop threads.

## Lessons baked in from live rounds (SF-4, 2026-07-28)

1. **Every contract PINS the gate instrument**: the exact interpreter/entrypoint for test runs
   (here: `/root/venv-trading/bin/python -m pytest` from repo root). The SF-4 builder graded
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
