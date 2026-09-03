---
name: premortem-roast
description: Run an adversarial pre-mortem / roast swarm over the trading system (or a subsystem) — parallel auditors hunt every fake, stub, dead-wire, hollow-green, honesty hole and profit blocker, then a judge dedups and ranks them into one ledger with a build order. Use whenever the owner asks to "roast", "pre-mortem", "find every crack/fake/stub", "audit the system", or between build waves to catch regressions the last pass missed.
---

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

## How to run

It is a saved Workflow. Invoke it via the **Workflow** tool by name:

```
Workflow({ name: 'premortem-roast', args: { ...optional... } })
```

It runs in the background (parallel `Audit` auditors → `Synthesize` judge) and
returns `{ raw_count, dimensions, ledger, build_order }`. The user must have
opted into multi-agent orchestration (they did by asking for a roast/pre-mortem).

### args (all optional — sensible defaults for THIS repo)
- `scope` — what's under audit (default: the whole system). E.g. `"the Wave-2 money spine (champion decode → validator → runner wiring)"`.
- `repo` — backend path (default `/home/user/trading-system`).
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
To target a specific subsystem, pass `scope` + `extra_dimensions` with lenses that
name exact files/functions and your suspicions (loaded briefs → evidence; vague
briefs → vibes). To iterate on the script itself, edit
`.claude/workflows/premortem-roast.js` and re-invoke with the same name.
