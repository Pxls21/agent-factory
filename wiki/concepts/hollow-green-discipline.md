---
concept: Hollow-Green Discipline
last_compiled: 2026-09-03
topics_connected: [project-overview, stage0-proof-pack, security-and-containment, research-and-seeds, decisions-and-premortem, incident-lessons]
status: active
---

# Hollow-Green Discipline — never mint a green the claimed mechanism did not produce

## Pattern

The project's #1 non-negotiable rule: never replace a real component with a stub, fake, no-op,
hardcoded value, tautology, or shortcut to "get past" a blocker. A fake-substrate result is worse
than none: it mints a hollow green and destroys trust. The rule extends to prose: a doc that
flatters the system (claims unproven capability, omits a known gap) is a hollow green in words.

Three operational forms recur:
1. Never substitute a fake to get past a blocker -- surface it instead and report NOT-built
2. A gate that cannot fail is not a gate -- pair every guard with a negative control
3. Every benchmark/eval exercises the ACTUAL pipeline, scores against a real independent oracle,
   and reports the hollow-green (gate-false-positive) rate

## Instances

- **2026-09-02** in [stage0-proof-pack](topics/stage0-proof-pack.md): the council made the
  four-way classification specifically to prevent a flat "N/12" count from laundering unexecuted
  proofs into an execution denominator. Kill criterion KC-4 halts the build if any status line
  reads as a flat count.
- **2026-09-02** in [research-and-seeds](topics/research-and-seeds.md): Socrates' strongest
  control -- S0-03 must assert upstream model identity, never just a 200. Running S0-03 against
  the S0-04 stub invalidates the verdict outright. KC-2 enforces a real credential.
- **2026-09-02** in [incident-lessons](topics/incident-lessons.md): AF-AP-1 -- bare
  `unshare --net` offered as selective-egress evidence would have been a vacuous negative control
  (it blocks ALL traffic, not just the unauthorized path). Chairman probe caught it.
- **2026-09-02** in [incident-lessons](topics/incident-lessons.md): AF-AP-2 -- seed
  self-validation red because proof ids appeared collectively instead of per-item. The gate's own
  negative control worked.
- **2026-09-03** in [incident-lessons](topics/incident-lessons.md): AF-AP-4 -- venue
  classified from sandbox alone while the PC held the capability. The "blocked" label was a hollow
  green in prose.
- **Structural** in [security-and-containment](topics/security-and-containment.md): the one
  sanctioned stub (S0-04) sits BEHIND real OmniRoute at the boundary the plan itself specifies.
  Every other proof exercises the REAL pinned component.
- **Structural** in [decisions-and-premortem](topics/decisions-and-premortem.md): the
  premortem's value is the failures it names; SECURITY.md says "this repository is a design
  artifact and is not yet safe to deploy."

## What This Means

In a planning-stage repo with zero application code, the hollow-green risk lives entirely in
documentation and status claims. The project guards against it with: four-way classification
(denominator honesty), negative-control discipline (every gate paired with a failing leg), the
anti-pattern registry (AF-AP-* with /bug-echo sweeps), and honest NOT-built markers in every
article (including this wiki). The discipline is tested before any code exists because it shapes
the machinery (registry, schemas, validator) that will gate the code.

## Sources

- [project-overview](topics/project-overview.md)
- [stage0-proof-pack](topics/stage0-proof-pack.md)
- [security-and-containment](topics/security-and-containment.md)
- [research-and-seeds](topics/research-and-seeds.md)
- [decisions-and-premortem](topics/decisions-and-premortem.md)
- [incident-lessons](topics/incident-lessons.md)
