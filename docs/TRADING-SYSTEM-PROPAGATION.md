# Propagation to the trading-system repo — checklist

**Why this exists (owner 2026-09-16):** the local Qwen model is meant to be used in the `trading-system` repo too,
and "we also changed our skills, our workflows and everything, and that also needs to be changed over there" —
flagged **more important** than copying docs. This file is the durable checklist so none of it is forgotten. It
lives here because `trading-system` is not in this session's repo scope; doing the work needs `add_repo` first
(confirm the exact GitHub path with `mcp__claude-code-remote__list_repos` — likely `pxls21/trading-system`).

**Direction of flow.** The setup here was ported FROM `trading-system@clean-build` on 2026-09-03 (see the CLAUDE.md
structure note). Since then agent-factory EVOLVED the shared skills/workflows; those evolutions now flow BACK to
trading-system. The skills are general-purpose (not agent-factory-specific), so they port cleanly.

## A. The local model (portable guide) — copy + adapt

- [ ] Copy `docs/LOCAL-MODEL-GUIDE.md` into the trading-system repo (its `docs/`). It is written portable: the
      model, OmniRoute, PC bridge, and container are shared infrastructure. Adapt only repo-specific names
      (combos: trading-system can reuse `agentfactory-*-local`, or the owner may want `trading-*-local` combos —
      an OmniRoute admin choice; the raw model id `qwen-local/qwen3.8-27b-local` is global either way).
- [ ] Confirm trading-system lanes can reach OmniRoute the same way (it has the same `scripts/pc.sh` bridge).

## B. The evolved skills / workflows — the flagged-important set

Since the 2026-09-03 port, the biggest change is **D-031 (validation-closure governance — the build-verify
infinite-loop fix): exhaustive findings, bounded blockers.** It touched, and must be re-ported to trading-system:

- [ ] `.claude/agents/adversarial-verifier.md` + `harness-ports/roles/adversarial-verifier.md` (→ `.codex/agents/*`
      via `build-roles.py`) — falsification framing, the 5-condition blocking predicate, the FINDING INVENTORY +
      GATE RECOMMENDATION split (`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`).
- [ ] Skills `contract-gate`, `build-loop`, `orchestration`, `anti-hollow-green` — the D-031 clauses (repair
      budget keyed by component/proof ID + contract revision + production digest; workload routing; red-test-
      necessary-not-sufficient). Remember the source-of-truth sync: `.claude/skills/<name>/SKILL.md` →
      `.agents/skills/` (via `sync-skills.sh`, or hand-ported per `harness-ports/hand-ported.sha256`) →
      `.agents/lane-skills/` (via `sync-lane-skills.sh`).
- [ ] `harness-ports/briefs/verify-contract.md` — the two-output report.
- [ ] The three instruction mirrors (`CLAUDE.md` Phase 5, `AGENTS.md`, `.hermes.md`) — the disposition-disciplined
      clause; re-check the mirror gate (`harness-ports/tests/test_context_mirrors.sh`) after.
- [ ] Decision-log entry (D-031 equivalent) in trading-system's log.

## C. General anti-pattern lessons worth carrying over

The AF-AP registry rows added here that are GENERAL (not agent-factory-specific) and would help trading-system:
- [ ] **AF-AP-92** — a `>120s scripts/pc.sh` bridge call is cut off and silently re-run (curl -m 120 + retry);
      background long jobs, poll with short calls; keep mutations at the top. (+ the CLAUDE.md bridge-cluster note.)
- [ ] Review AF-AP-76…AF-AP-91 for the general-lesson subset (e.g. AF-AP-78 a mutant must compile; AF-AP-79 a
      guard runs before the write; AF-AP-80 a source-text pin needs a behavioral control) and port the general ones.

## D. How to find the COMPLETE delta (don't work from memory)

Once trading-system is added:
1. `git -C <trading-system> log --oneline` to find the `clean-build` port baseline it was taken from.
2. Diff the shared trees here against there: `.claude/skills/`, `.claude/agents/`, `harness-ports/`, `scripts/hooks/`,
   `CLAUDE.md` — `diff -ru` (excluding project-specific paths like `proofs/`, `spikes/`, `seeds/`, `docs/0*`).
3. The diff is the authoritative change set; this checklist is the human summary, not a substitute.

## E. Execution

- [ ] `add_repo` trading-system (confirm the path via `list_repos`), on its own designated branch.
- [ ] Apply A + B + C; run trading-system's own gates (its `run-all.sh` / mirror gate / suites) before any push.
- [ ] Commit + push per trading-system's push rules (it has its own `push_clean.sh`); do NOT assume agent-factory's.

## Status

Created 2026-09-16 (owner ask). Nothing propagated yet — this is the plan. Task registered in the project task DB.
