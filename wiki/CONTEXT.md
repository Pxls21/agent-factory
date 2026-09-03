# CONTEXT -- how an agent should use this wiki

**Stats:** 12 topics, 3 concepts, compiled 2026-09-03, codebase mode over the repo root
(`.claude/`, `.agents/`, `sandbox-kit/`, `docs/archive/`, `.gitnexus/`, `graft/`, vendor and
build dirs excluded).

This wiki is a **distillation of planning documents at compile time**. No application code
exists; the wiki is compiled from architecture docs, research artifacts, configuration examples,
and tooling scripts. It is fast orientation, not authority.

Start at [INDEX.md](INDEX.md); the registry of topics, concepts and conventions is
[schema.md](schema.md).

## Authority order (memorize this)

1. `todo/BUILD-TASKLIST.md` -- the single source of truth for live build status, task counts, and
   what is done vs pending. It wins over this wiki on any disagreement.
2. The code and its tests -- once application code exists, a live probe beats a docstring.
3. `seeds/seed-stage0-v1.yaml` and `docs/research/FINDINGS-STAGE0-v1.md` -- the spec and the
   constraint set.
4. This wiki -- a compiled summary that will drift the moment an increment lands.

If an article and a primary source disagree, the primary source is right and the article is stale.

## How to read coverage tags

Every article section carries one, and they are honest:

- `[coverage: high -- N sources]` -- claims read out of named files this pass. Safe to act on.
- `[coverage: medium -- N sources]` -- mostly read, some parts inferred. Verify load-bearing claims.
- `[coverage: low -- N sources]` -- located but not deep-read. **Treat as a pointer, not a fact.**

## Where to start, by task

- **"What is this system?"** --> [project-overview](topics/project-overview.md), then
  [docs/01_ARCHITECTURE.md](../docs/01_ARCHITECTURE.md) for the production and improvement
  topologies.
- **"What is the current build status?"** --> `todo/BUILD-TASKLIST.md` (the SSoT), NOT this wiki.
  The wiki's [stage0-proof-pack](topics/stage0-proof-pack.md) gives context but defers to it.
- **"What components exist and what state are they in?"** -->
  [docs/02_COMPONENT_AUDIT.md](../docs/02_COMPONENT_AUDIT.md) (read FIRST among the plan docs).
- **"What decisions were made and why?"** -->
  [decisions-and-premortem](topics/decisions-and-premortem.md), then
  [docs/08_DECISION_LOG.md](../docs/08_DECISION_LOG.md) and `docs/adr/`.
- **"How does the tooling work?"** -->
  [infrastructure-and-tooling](topics/infrastructure-and-tooling.md).
- **"What runs on the PC?"** -->
  [pc-bridge-and-environment](topics/pc-bridge-and-environment.md).
- **"How do I run a Stage 0 proof?"** -->
  [stage0-proof-pack](topics/stage0-proof-pack.md), then
  [tasks/stage0-breakdown.md](../tasks/stage0-breakdown.md) for the increment details.
- **"I am about to write a gate or test."** --> read
  [hollow-green-discipline](concepts/hollow-green-discipline.md) and
  [fail-closed-fail-loud](concepts/fail-closed-fail-loud.md) before writing the first line.

## When NOT to use the wiki

- **Never as an oracle for build status.** `todo/BUILD-TASKLIST.md` is the tie-breaker.
- **Never as a substitute for reading the contract you are about to implement.** Read
  `docs/03_INTEGRATION_CONTRACTS.md` for the real acceptance tests.
- **Never as evidence in a verdict or commit message.** Cite the file and line you read.
- **Not for anything under an excluded path** -- `sandbox-kit/`, `.claude/`, `docs/archive/`
  were scanned selectively or not at all.

## Conventions

NOT-built capabilities and known failure modes are stated **first-class** in every article's
Gotchas section. An article that hides a gap is the same defect as a stub in the code.

## Maintenance

Recompile with `/wiki-compile` after any wave that lands new subsystems. Append a dated entry to
[log.md](log.md), update `.compile-state.json`, and add an Evolution Log line to
[schema.md](schema.md). Topic and concept slugs are stable identifiers.
