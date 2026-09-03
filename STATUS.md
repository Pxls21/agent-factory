# Project status

**Phase:** architecture and repository setup
**Implementation:** Stage 0 MACHINERY in progress on branch `claude/soundbox-kit-migration-iz1jwf` (increment #1 registry/schemas/validator DONE 2026-09-03; #2a runner + probe-backed markers landed; #2b ledger generator + CI pending). No application code for the Buzz→ACP→Hermes→OmniRoute spine exists yet; the twelve proofs are ABSENT by design until their increments run. Live status: `todo/BUILD-TASKLIST.md`.
**Deployment readiness:** no
**Last audit snapshot:** 2026-09-02

## What is complete

- All 14 supplied documents are preserved unchanged.
- Relevant upstream repositories were inspected at exact commits recorded in `upstream.lock.yaml`.
- Hermes has been selected as the sole stock production workhorse.
- The live path remains Buzz → `buzz-acp` → Hermes' native ACP server.
- JIT, the Harness Foundry, GBrain/dream work, HarnessRouter's conditional Phase 2 role, PandaProbe, and AlphaEval remain in the roadmap.
- The model, memory, governance, containment, and evaluation seams have been re-specified against current source.
- Known configuration errors and unsupported assumptions from the v2 plan have been recorded.
- A staged backlog, acceptance gates, security model, and evaluation strategy are ready for implementation.

## What is intentionally not complete

- Pushing works: PR #2 (the planning tree + the sandbox-kit operating setup) was merged to `main` on 2026-09-02; every later increment is pushed to the working branch after its gates pass, and `main` changes only through an owner-merged PR (the Stage 0 work awaits a new one).
- No production container image or Compose deployment has been built.
- No Hermes Fubuki or composite ai-memory adapter has been implemented.
- No policy decision service has been implemented.
- No JIT Foundry, GBrain dream worker, evaluation runner, or HarnessRouter integration has been implemented.
- No provider credentials, relay keys, or production secrets have been configured.
- No live model, Buzz or memory smoke test has been run against THIS project's components. gVisor: the owner installed runsc on the PC and a rootless runsc container was verified on 2026-09-03 (`PC-BRIDGE.md`); the committed S0-08 marker therefore reads `expired` (the proof must run), and no containment test of this project's containers has run yet.

## Next decision needed from the owner

The target repository is `Pxls21/agent-factory`; read and write access work (PR #2 merged 2026-09-02). The owner's 2026-09-03 review of the working branch found the enforcement layer thin — hollow CI, a fail-open skill-sync gate, a state-mutating harness test, stale status claims, security-sensitive upstream pins — and those are being repaired first (`todo/BUILD-TASKLIST.md` tasks 26–28) before Stage 0 increments resume.
