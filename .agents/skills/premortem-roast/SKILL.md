---
name: premortem-roast
description: Run an adversarial pre-mortem / roast swarm over the trading system (or a subsystem) — parallel auditors hunt every fake, stub, dead-wire, hollow-green, honesty hole and profit blocker, then a judge dedups and ranks them into one ledger with a build order. Use whenever the owner asks to "roast", "pre-mortem", "find every crack/fake/stub", "audit the system", or between build waves to catch regressions the last pass missed.
---

> **HARNESS PORT.** This copy is read by Codex CLI (`.agents/skills/`) and by Hermes
> (via `skills.external_dirs`). Same protocol as `.claude/skills/premortem-roast/SKILL.md`;
> the "How to run" section is REWRITTEN because neither harness has a Workflow runtime —
> see `docs/HARNESS-PORTS.md`. Auditor prompts and schemas live in `dimensions.md` beside
> this file. "the project instructions file" = `AGENTS.md` on Codex, `.hermes.md` on Hermes.

# premortem-roast

A reusable multi-agent pre-mortem. It has repeatedly surfaced P0 defects the
build missed (the 56-defect PREMORTEM-LEDGER, the 32-finding R2, the hollow-green
that made every real champion fail). Run it between waves — the point is to keep
finding the cracks until they're ironed out.

**Luck-lens auditor angle (skill `luck`, owner mandate 2026-08-27):** when the
roast target is the SETUP/workflow (not a measurement), include one auditor
armed with the seven-facet diagnostic — hunting insolvent artifacts (docs/tools
nobody can maintain), pooled knowledge (lessons that never circulated back into
skills/briefs), and fragmented ecology (subsystems that never talk). Never a
lens on gate verdicts.

## How to run — HARNESS PORT (there is no Workflow runtime here)

In the sandbox this is a saved Workflow invoked with the Workflow tool. **Codex
and Hermes have no Workflow API** — no `agent()`, no `parallel()`, no
`pipeline()`. There is no shim and none is coming: a fake runtime that "ran the
swarm" without running it is exactly the hollow green this skill hunts.

So it runs here as an explicit two-stage procedure. Same stages, same lenses,
same schemas — driven by real process calls instead of a runtime.

**Stage 1 — Audit (parallel).** One lane per dimension. Prompts and the findings
JSON schema are in `dimensions.md` next to this file; read it first.

```bash
# from the repo root on the PC; SCOPE/REPO/KNOWN substituted into the preamble
mkdir -p .lanes/roast/out
for KEY in fakes-stubs dead-wiring correctness-hollow-green data-integrity \
           honesty-ux safety-compliance test-rigor ops-resilience \
           telemetry-gaps premortem-profit; do
  bash harness-ports/bin/pc-lane.sh ".lanes/roast/brief-$KEY.md" codex evidence-gatherer &
done
wait
```

Build each `brief-$KEY.md` as the shared preamble from `dimensions.md` plus that
row's DIMENSION text. Run them under the **evidence-gatherer** role: auditors
collect evidence and must not conclude. Pass the findings schema through
`codex exec --output-schema` so stage 2 gets structured JSON rather than prose.

**Stage 2 — Synthesize (single lane).** Concatenate every stage-1 `report.md`
into one findings array, then run the synthesis prompt from `dimensions.md` with
the ledger schema. One lane, not parallel — it is a dedup/rank pass over the
whole set.

**Parallelism is real, but bounded.** Ten concurrent lanes each take a git
worktree and a model session. Start with 3–4 in flight on the PC and raise it
only if the box keeps up; `pc-lane.sh` gives each lane a disjoint worktree, so
they cannot collide on the tree, but they do share CPU, RAM and rate limits.

**On Hermes** the same two stages run through `delegate_task(tasks=[...])`, which
spawns isolated subagents for a parallel batch. Note the tradeoff before using
it: `delegate_task` children share the parent session's terminal container, so
concurrent `cd`/writes can collide — prefer the `pc-lane.sh` path, which gives
each lane its own worktree.

### args (all optional — sensible defaults for THIS repo)
- `scope` — what's under audit (default: the whole system). E.g. `"the Wave-2 money spine (champion decode → validator → runner wiring)"`.
- `repo` — backend path (default `/home/user/agent-factory`).
- `frontend` — frontend src path to also roast (e.g. the PC ValueCell copy under scratchpad).
- `known` — known gaps to NOT re-report as-is (auditors find the specifics beneath them).
- `extra_dimensions` — `[{key, prompt}]` run-specific lenses APPENDED to the defaults (e.g. a money-spine-correctness lens, a fork-harness-design lens).
- `dimensions` — `[{key, prompt}]` to REPLACE the default lens set entirely.
- `model` — agent model (default `sonnet`).
- `ledger_prefix` — id prefix for synthesized findings (default `FIND`; use `R3`, `R4`, … for successive between-wave rounds).

### Default lenses (used when `dimensions` not given)
fakes-stubs · dead-wiring (dead knobs/genes) · correctness-hollow-green ·
data-integrity (train vs validate/execute divergence) · honesty-ux ·
safety-compliance · test-rigor · ops-resilience · telemetry-gaps · premortem-profit.

## After it returns (the coordinator's job — do NOT skip)
1. **Read the full result** from the task output file (the notification truncates it).
2. **Verify the load-bearing P0s yourself** — an agent finding is a claim until re-derived in the main loop (reproduce the top compliance/correctness ones live).
3. **Persist** a ranked ledger doc (e.g. `docs/PREMORTEM-N-LEDGER.md`) with your verification verdicts, and cross-link to prior ledgers (dedupe against R2/etc.).
4. Feed the build_order into the plan; fix confirmed self-inflicted P0s promptly.

## Tuning it per round
To target a specific subsystem, narrow `SCOPE` and add lenses that name exact
files/functions and your suspicions (loaded briefs → evidence; vague briefs →
vibes). Extra lenses are extra rows appended to the table in `dimensions.md` for
that round; to replace the default set entirely, use only your own rows.

The sandbox-side script `.claude/workflows/premortem-roast.js` remains the
reference implementation of the stages. It does not run here — if you change the
lenses there, mirror them into `dimensions.md`, which is what this harness reads.
