# Project status

**Phase:** architecture and repository setup
**Implementation:** not started
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

- The local Git remote is configured for `https://github.com/Pxls21/agent-factory.git`, but no files have been pushed because the GitHub integration lacks repository Contents write access.
- No production container image or Compose deployment has been built.
- No Hermes Fubuki or composite ai-memory adapter has been implemented.
- No policy decision service has been implemented.
- No JIT Foundry, GBrain dream worker, evaluation runner, or HarnessRouter integration has been implemented.
- No provider credentials, relay keys, or production secrets have been configured.
- No live model, Buzz, memory, or gVisor smoke test has been run.

## Next decision needed from the owner

The target repository is `Pxls21/agent-factory`. GitHub read access is working, but the connected GitHub integration returned HTTP 403 for repository content writes. Grant/reinstall the integration with Contents write access to this repository, then publish this planning tree to `main`.
