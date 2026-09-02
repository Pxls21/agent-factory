---
name: vendor-first
description: "BEFORE designing any integration, port, adapter, cache, or replacement that touches a vendored/third-party library (vectorbtpro, pymoo, cupy...): check whether the library already ships the mechanism. Triggers: designing a new seam around vendored code, caching/injecting/overriding library-computed values, porting library behavior to another substrate, working around a library limitation, or any plan that re-implements something a library plausibly does. Born from the in_outputs incident (owner mandate 2026-08-22)."
---

# vendor-first — the library probably already built it

**The incident (2026-08-22):** wave-2 GPU readout was DESIGNED as a custom
accessor-from-arrays seam. The blocking dispatch-trace gate failed it (10/17 metrics
unreachable), and only THEN did a deeper look find `Portfolio(in_outputs=...)` —
vectorbtpro's PURPOSE-BUILT mechanism for exactly this (attach precomputed arrays;
the property surface reads them instead of re-deriving). The final design was
cheaper, safer, and needed zero new metric code. The custom design was unnecessary
from the first minute; we just hadn't looked. (AP-28 in docs/INCIDENT-LOG.md.)

## The mandatory pre-design pass (cheap — minutes, not hours)

Before ANY design that adds a seam around, replaces, caches, or ports vendored
behavior:

1. **Grep the vendored tree for the capability noun**, not the API you imagine:
   `grep -rn "in_output\|precomputed\|override\|cache" vendored-tree/` — search for
   what you NEED (e.g. "attach precomputed", "custom", "callback", "hook", "registry",
   "adapter"), including docstrings. Vendored docstrings are searchable design docs.
2. **Runtime-introspect the live object**: `dir(obj)`, `obj.__init__` signature,
   class docstring. The wave-2 answer was literally a documented `__init__` kwarg.
3. **Check the capability ledger** (docs/research/VBT-PRO-CAPABILITY-LEDGER.md for
   vbt) — and if your pass discovers a capability the ledger lacks, ADD it there in
   the same increment.
4. **Ask the inversion question**: "if the library authors had this exact problem,
   where would they have put the solution?" Then look there.
5. Only if 1–4 come up empty: design custom — and record the negative search in the
   design doc ("vendored tree searched for X/Y/Z, nothing found") so the next reader
   knows the reinvention is justified.

## Scope notes

- Applies to DESIGN time (research prompts, seeds, briefs) — a research prompt about
  a vendored-adjacent subsystem must contain the instruction to do this pass.
- A deliberate substrate port (e.g. the CUDA kernel port of from_signals) is NOT a
  violation — that reimplementation is the point. The violation is re-plumbing
  around a library SURFACE the library already lets you plumb.
- Sibling class AP-27: when you DO use the library as an oracle, pin the VENDORED
  path, never a public mirror.
- **The inverse trap (AP-44, 2026-08-31): the library's defaults are part of YOUR
  config surface.** Wrapping a vendored constructor and passing only the kwargs you
  care about leaves every unpinned behavior-gating default ARMED — caps, limits,
  tolerances, thread counts, eval budgets. pymoo's `DefaultTermination` silently
  carries `n_max_evals=100000`; `build_termination` passed only `n_max_gen`, and the
  hidden ceiling truncated a production run at gen 179/200 the first time
  pop×gens crossed 100k. The pass: when wrapping a vendored constructor, read the
  FULL `__init__` signature (and its base classes'), enumerate every behavior-gating
  default, and either pin it explicitly or record in a comment why the default is
  intended. A negative-control test pinning the vendored default (fails loudly if
  the library changes it) turns the silent default into a watched contract.
