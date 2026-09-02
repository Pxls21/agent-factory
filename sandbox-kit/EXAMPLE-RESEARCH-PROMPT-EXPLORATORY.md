<!-- WHY (whole file): worked example for sandbox-kit/RESEARCH-PROMPT-GUIDE.md's EXPLORATORY-
     HYPOTHESIS mode. Same invented neutral subject as the SETTLED-SPEC example (`cfgmig`, a
     config-migration tool) so the two are comparable side-by-side and both copy cleanly into any
     repo. Here the SOLUTION is genuinely open (three architectures, no incumbent), but the SCOPE
     is fenced per the guide's "exploratory must stay QUESTION-PROOF" rules — every fork the agent
     could hit is pre-resolved below so it never has to stop and ask. -->

# RESEARCH-PROMPT-EX2 — THIRD-SCHEMA-VERSION CONVERTERS: hand-written, plugin-loaded, or DSL-declared?

<!-- WHY: house-structure "question-first" — the title names the open architectural QUESTION
     (which converter mechanism), not a pre-picked answer, which is the correct posture for
     exploratory mode ("the answer is NOT known — only the constraints are"). -->

> **At a glance:** `cfgmig` has hand-written Python converters for its two shipped schema
> transitions (v1→v2, v2→v3), each ~150 lines, each with its own golden-file test. A third schema
> version is coming, and two external teams have asked to contribute converters for their own
> internal config dialects without depending on a `cfgmig` release. The solution space is genuinely
> open — this brief researches which converter-extension architecture to build, not whether to
> build one (that decision is already made: task #EX-9 approved the extension effort).
> Status: RESEARCH ONLY — nothing is being built until findings return. Tracker: task #EX-9.
> Council: **RUN, not skipped** — `/council` already deliberated the "extend at all?" question
> (verdict: yes, approved #EX-9) but explicitly punted the mechanism to research; this brief picks
> up from that verdict's unresolved-questions list, per RESEARCH-PROMPT-GUIDE step 1.5.

<!-- WHY: satisfies "Lead with the real question, not the substrate" (mechanism, not "should we
     extend") and records which prior step (council) already ran, so the research agent doesn't
     re-litigate a settled prerequisite decision. -->

## Current-state capability ledger (proven-live vs built-never-run vs absent)

<!-- WHY: guide's mandatory exhaustive "what-the-system-IS" inventory — module:function, what it
     does, so the agent can't propose rebuilding something that exists or miss something that
     constrains the design. -->

- **Proven live:** `cfgmig/converters/v1_to_v2.py` and `v2_to_v3.py` — hand-written, imported
  directly by `cfgmig/cli.py:main` via a hardcoded `if` chain on the detected schema version. Each
  has a golden-file regression test in `tests/converters/`. No plugin/entry-point loading exists
  anywhere in the codebase today.
- **Built-never-run:** none — there has been no prior extension-mechanism spike.
- **Absent:** any sandboxing, capability-scoping, or code-signing story for executing code not
  authored by this repo's maintainers. No versioned "converter contract" (interface, error
  contract, or manifest schema) is documented anywhere — today's two converters share conventions
  only by copy-paste.
- **Falsified already (do NOT propose again):** an informal 2026-04 spike loaded third-party
  converter code via `eval()` on a string pulled from a config file's `converter_source` field.
  Rejected outright at review — arbitrary code execution from an untrusted config value, no
  sandbox, no review gate. Any candidate below that reintroduces unreviewed dynamic code execution
  from an unvetted source is disqualified regardless of ergonomics gains; this is not up for
  re-litigation, only *how* to load reviewed, vetted converter code is open.

## SETTLED (guardrails only — NOT the solution)

<!-- WHY: guide's exploratory rule — "SETTLED holds only constraints/guardrails, never the
     solution." Distinguishes this from the SETTLED-SPEC example, where SETTLED holds the actual
     answer. Also satisfies "CORE SYSTEM INVARIANTS ARE SETTLED GUARDRAILS — NEVER expose them as
     open / pressure-test / paradigm questions." -->

1. **Security-never-worse (NON-NEGOTIABLE).** Whatever mechanism ships, converter code must be
   reviewed and merged/vetted through this repo's normal review process before it can run — no
   architecture may let an untrusted party's code execute without a human review step. (Rejected
   alternative: the `eval()`-on-config-value spike, above — dead, not a fallback.)
2. **Determinism-never-worse (NON-NEGOTIABLE).** The migration spine's no-LLM-judge, exit-code-only
   contract (parse → convert → validate) is untouched by this research; a converter is a pure
   function from legacy dict to canonical dict, same as today's two.
3. **Backward compatibility (NON-NEGOTIABLE).** Whatever mechanism ships must keep `v1_to_v2` and
   `v2_to_v3` working unmodified, or migrate them to the new mechanism with a byte-identical golden
   test re-run proving no regression — never a rewrite that isn't re-verified.
4. These three are guardrails, not candidates — do not present "should converter code be
   reviewed?" or "should determinism be preserved?" as open questions.

## PRIMARY DELIVERABLE (one)

<!-- WHY: guide's "ONE primary deliverable... Add a one-line PRIORITY line" + exploratory's
     "each architecture fork: evaluate all, RECOMMEND by criteria X — do NOT ask which we want."
     The three named criteria below are the "criteria X." -->

**PRIORITY (SETTLED — do not ask which is primary):** a single recommended converter-extension
architecture, chosen from the candidates below (or a primary-sourced alternative), evaluated
against three named criteria: (i) security posture given guardrail 1, (ii) onboarding cost for an
external team contributing one converter, (iii) long-term maintenance cost inside this repo.
**Evaluate all candidates against all three criteria and RECOMMEND — do not ask which we want.**

- **(a) Entry-points plugin loading** (e.g. Python packaging entry-points / a discovered-package
  convention) — converters ship as separately-installed packages, discovered at runtime, still
  reviewed via a required allowlist file committed to this repo (satisfies guardrail 1: only
  allowlisted package names load). `[DESIGN fork — DECIDE by the three criteria]`
- **(b) Hand-written-in-repo, same as today, just more of them** — external teams submit a PR
  adding `converters/<name>_to_v3.py`; no new mechanism at all, only a documented contract +
  template. `[DESIGN fork — DECIDE by the three criteria]`
- **(c) A declarative DSL** (e.g. a committed YAML/JSON key-mapping spec, interpreted by a single
  generic engine — structurally similar to the flatten mechanism in the companion SETTLED-SPEC
  example) for the common case, with an documented escape hatch to (a) or (b) for conversions a
  declarative mapping can't express. `[DESIGN fork — DECIDE by the three criteria]`
- **(d) Any published/primary-sourced alternative** (e.g. a WASM-sandboxed plugin model) that
  clears guardrail 1 without a review-gate workaround — bring evidence, not vibes.
  `[DESIGN fork — DECIDE by the three criteria]`

<!-- WHY: each candidate carries its own inline resolution-KIND token per the guide ("its inline
     resolution-KIND token... maps to a concrete metric/control/module change") — here all four are
     the same DESIGN-fork kind because the guardrails already bound the design space; a brief
     mixing DESIGN forks with genuinely primary-source-technical or empirical questions would tag
     each differently (see the SETTLED-SPEC example's mixed [PRIMARY-SOURCE TECHNICAL] +
     [EMPIRICAL GATE] tokens for a contrast). -->

**Thesis-stance dial (SETTLED):** the core thesis — "an extension mechanism should exist" — is
FIXED, not on trial (task #EX-9 already approved it); what's on trial is only WHICH mechanism.
Do not reopen "should we extend at all."

**Paradigm/substrate dial (SETTLED):** the parse → convert → validate pipeline substrate itself is
FIXED and out of scope to challenge; only the *loading/authoring* of the convert step is open.

Subordinate (relationship stated):

- **Converter contract formalization** [DESIGN fork — DECIDE, downstream of the primary] — once a
  mechanism is chosen, specify the interface/error contract/manifest every converter (including the
  existing two) must satisfy; migrate the existing two converters to it with a golden-test re-run.
- **Validity gate on the primary** [EMPIRICAL GATE — run on the chosen candidate before it ships] —
  build one converter for a synthetic third schema version under the recommended mechanism; run the
  full golden-test suite (existing two converters unmodified + the new one); measure onboarding
  time against a documented "write a converter" walkthrough with a person unfamiliar with the
  codebase. Acceptance: zero regression on the existing two, the new converter's golden test passes,
  the walkthrough is completable without maintainer help.

**Self-resolution / "what would change the plan":** if primary-source research surfaces a security
flaw in ALL FOUR candidates (none can satisfy guardrail 1 without an unacceptable review bottleneck
at scale), the report still returns a ranked recommendation among them under a stated residual risk
(per the guide's UNCONFIRMED-after-exhausting-sources triple: default candidate to proceed on +
residual risk + the first task that would settle it) — it does NOT return "still uncertain, please
advise," and it does NOT propose reopening guardrail 1.

<!-- WHY: satisfies exploratory's mandatory "every open question + every 'what would change the
     plan' trigger carries HOW to resolve it without us" and the "truly UNCONFIRMED-after-
     exhausting-sources ships ONLY as a triple" rule — this is the ONLY sanctioned shape for
     residual uncertainty; a bare hedge is a rejected deliverable. -->

Deliverable shape: a findings report with (1) the three-criteria comparison table across all four
candidates (or the primary-sourced fifth), (2) the recommended mechanism + why the runners-up lose,
(3) the exact seams (`file:line`) an implementing engineer touches, (4) the converter-contract spec
and the existing-converter migration plan, (5) the honest NOT-resolved list (empirical gate results
only — never a strategic hedge).
Decide; do not ask.

<!-- WHY: guide's mandatory closing line, verbatim. Also the "pre-flight (author's check)" from the
     guide — before shipping, this file was checked for any fork the agent could rationally pause
     on (thesis? fixed. paradigm? fixed. which architecture? bounded by 3 named criteria + a
     do-NOT-ask instruction. residual uncertainty? has an attached triple.) — none survive, so the
     brief is exploratory-complete per the guide's own pre-flight test. -->
