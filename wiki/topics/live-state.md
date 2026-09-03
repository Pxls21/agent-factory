---
topic: live-state
last_compiled: 2026-09-03
---

# Live State -- continuity snapshot

## Clocks

- **Origin tip:** `237192a` 2026-09-03T10:09:53+00:00 (`claude/soundbox-kit-migration-iz1jwf`) — transcript sync after the increment-#1 lane bring-up
- **Local HEAD:** 1 commit ahead of origin at write time (the increment-#1 harvest + five RED
  spine tests). SHAs are rewritten by `push_clean.sh` at push, so this page names commits by
  subject; the tree is what is pinned.
- **Today:** 2026-09-03

## Active lanes
- **Increment #1 `s0-01-registry-schemas-validator`** — contract-gate ROUND 2. Round 1 (PC Hermes
  lane, sol-ultra, four runs: wrong premise → two 503 deaths → success at pin c39b64f) was
  harvested 2026-09-03: C1–C3 green in the sandbox; the lane's 33/33 was a host-python green
  (AF-AP-11, harness fixed); the coordinator's spine read shipped three gaps as five RED tests
  (AF-AP-12/13/14). Repair brief `tasks/briefs/s0-01b-repair-spine-gaps.md` → then the verify lane
  (`harness-ports/briefs/verify-contract.md`, terra-xhigh) → coordinator final layer.
- **Continuity + offload plane** (`continuity-offload-plane`, task #25): transcript sync live
  (`transcripts/sandbox/`), lane roles/templates committed, offload map written; first route probe
  (Gemini flash as researcher) running; curator lane not yet run.

- **`port-trading-system-setup`** — DONE with this commit: batches A-D landed, the Codex/Hermes
  ports (`AGENTS.md`, `.hermes.md`) reviewed and committed, batch E (this wiki compile) landed.
  NOT done inside it: PC smoke of the harness ports (needs a bridge banner + the owner).
- **`harness-skill-rewordings`** (pending, low priority): `.agents/skills` is a verbatim mirror of
  `.claude/skills` — the source repo's 14 hand-ported skill rewordings were not carried over;
  the mechanism table in `AGENTS.md`/`.hermes.md` carries translation meanwhile.
- **Stage 0 build:** STARTED 2026-09-03 with increment #1 (above). Pipeline (findings, council,
  interview, seed, breakdown) COMPLETE, all committed. `tests/` is deliberately RED (5 contract
  tests) until the repair lane lands.

## In-flight runs
- **PC lane bring-up** (2026-09-03): DONE and PROVEN — clone at `~/agent-factory`, pc-setup complete
  (quartet, venv, gitnexus 1.6.10), Hermes profile `agentfactory` with the merged snippet; spike
  `hermes-lane-trial` runs 8-9: shell in the pinned worktree (`TERMINAL_CWD`), push/PR blocked
  under yolo, patch path home. Next lane = increment #1, after the owner's go-ahead. gVisor INSTALLED by
  the owner and a rootless runsc container verified (see PC-BRIDGE.md for the invocation + caveats).

- **Adversarial attack lane `s0-01e`** (agentfactory-verify, terra-xhigh) — running against the
  round-3 tree; RED tests under `tests/red/` come home with the patch. The mechanical contract run
  (C1–C18) was done by the coordinator in the sandbox: 18/18 PASS (the sweep combo's head routes
  are dead — flash credits depleted, antigravity flash retired; owner action in INCIDENT-LOG). Repair lane `s0-01d` DONE on
  `agentfactory-build` (44 passed ×2; first lane to run under the incremental-report rule — its
  report-draft.md was written). Verify lane `s0-01c` died mid-run after 167 calls (AF-AP-16/17);
  its transcript and red suite were recovered. Repair lane `s0-01b` DONE (39 passed ×2).

## Pending owner decisions
- **BUILD lane = Hermes on the PC (owner ruling 2026-09-03):** bring-up in progress (clone, venv,
  config merge, trial lane); the OmniRoute model id for the lane is being resolved from `/v1/models`.
- **Build-direction review** (`tasks/stage0-build-direction.md`, 2026-09-03): the owner asked for
  the direction summary before increment #1; building waits for their notes or "go ahead".

- `sudo modprobe kvm_amd` on the PC (KVM modules present but unloaded; needed before gVisor tests)
- runsc install on the PC (absent; systrap platform needs no KVM but the binary is missing)
- Keep-alive Routines: NOT enabled (owner-optional; the 2026-08-01 trigger-tool caution stands)
- PC smoke of the harness ports (owner must merge Hermes config, run MCP smoke probe)
- Five owner inputs from the decision log: first-party license, deployment target, Buzz community,
  first OmniRoute route/budget, default memory degradation policy
- podman-compose availability on the PC (absent; buzz-prod containers exist via some compose path)

## Do-not-trust

This wiki is a map, not the territory. The ledger (`todo/BUILD-TASKLIST.md`) wins on any
build-status or count disagreement.

**NOT-built (first-class):**
- No application code exists (STATUS.md: "Implementation: not started")
- Telemetry plane planned; sinks (OpenObserve 5080, Phoenix 6006) running on the PC but receive
  nothing from this project
- Harness ports unit-proven in the sandbox only; NOT smoke-tested on the PC
- Ouroboros native MCP broken (MCP-SDK v2 vs v1.x); stdio fallback (`scripts/ooo_mcp.py`) works
- Wiki compiled from planning docs, not from code
- Pre-commit now runs three gates (pyflakes delta, shell syntax, skill-sync); none of them is a
  test of the Stage 0 spine — that spine does not exist yet
- Stage 0 proof pack: 0 of 18 increments complete (only spike #0 done)

## Last updated

Increment-#1 round-3 harvest commit — 2026-09-03; next update at the two verification lanes' verdicts.
