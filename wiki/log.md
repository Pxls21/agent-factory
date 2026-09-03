# Wiki Compile Log

## 2026-09-03 -- initial compile (codebase mode, planning docs only)

**Scope.** Repo root per `.wiki-compiler.json`, excluding `wiki/`, `.gitnexus/`, `graft/`,
`.claude/`, `.agents/`, `sandbox-kit/`, `docs/archive/`, `node_modules/`, `dist/`, `.git/`,
`vendor/`, `__pycache__/`, `.build/`, `target/`, `coverage/`.

**Trigger.** Batch E of `port-trading-system-setup` -- the first wiki compile for this repo.
Config `.wiki-compiler.json` authored in batch B; `wiki-init` had not run (no prior
`.compile-state.json`).

**Method.** Sequential manual compile (no sub-agents) following the `wiki-compiler` skill
phases. All corpus files read from disk; `file:line` anchors where sections cite them.

**Produced.**
- 12 topic articles under `topics/`, using the 8-section codebase article structure declared
  in `.wiki-compiler.json`: project-overview, production-spine, memory-and-governance,
  security-and-containment, evaluation-and-improvement, stage0-proof-pack,
  decisions-and-premortem, research-and-seeds, infrastructure-and-tooling,
  pc-bridge-and-environment, incident-lessons, harness-ports.
- 3 concept articles under `concepts/`: hollow-green-discipline, fail-closed-fail-loud,
  isolation-by-design.
- `schema.md` (topic/concept registry, article structure, naming + honesty conventions,
  evolution log), `INDEX.md`, `CONTEXT.md`, `log.md`, `.compile-state.json`.
- `topics/live-state.md` (the continuity snapshot, required by CLAUDE.md).

**Source counts by topic:** project-overview 13, production-spine 8, memory-and-governance 6,
security-and-containment 6, evaluation-and-improvement 6, stage0-proof-pack 7,
decisions-and-premortem 5, research-and-seeds 6, infrastructure-and-tooling 12,
pc-bridge-and-environment 6, incident-lessons 5, harness-ports 5. Sum = 85 topic-source pairs;
distinct-file count is lower (CLAUDE.md, docs/02_COMPONENT_AUDIT.md, docs/09_PREMORTEM.md,
todo/BUILD-TASKLIST.md each feed many topics).

**Coverage notes:**
- This is a planning-stage repo with zero application code. All articles are compiled from
  architecture docs, research artifacts, configuration examples, and tooling scripts.
- API Surface and Data sections are `[coverage: low]` in most topics because no runtime API or
  data store exists.
- The `sandbox-kit/` tree was scanned selectively (OPERATING-GUIDE.md, VENDORED-FROM.md only);
  its 372+ vendored skills, plugin code, and reference scripts were not read.
- `.claude/` hooks were listed and headers read; bodies not deep-read.
- `scripts/*.sh` headers read; implementations not deep-read.
- The v2 original documents (`docs/archive/v2-original/`) were excluded per config.

**Gaps remaining (named):**
- No application code to compile -- every Gotchas section states this first-class.
- Telemetry plane planned but not built; observability sinks receive nothing.
- Harness ports unit-proven only; NOT smoke-tested on the PC.
- Ouroboros native MCP broken (SDK version conflict); stdio fallback documented but not compiled
  as a separate topic.
- No call-graph trace was run (no application code to trace).
