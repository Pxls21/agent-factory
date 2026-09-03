# BUILD TASK LIST — agent-factory (Stage 0, end-to-end, durable)

> **This file is the SINGLE SOURCE OF TRUTH for live build status.** The in-session task tool
> does NOT survive a new chat; this committed file does. In any new session: *"Read
> `todo/BUILD-TASKLIST.md`, load it into your task list, then start at the first `pending` task."*
>
> **TASK-DB MIRROR RULE (owner mandate 2026-08-10, ported from trading-system).** The container
> task DB rolls back with disk resets and reuses its slot numbers, so it silently loses completed
> programs. Standing protocol: (1) every task CREATE and every status CLOSE is mirrored into
> this file's §LIVE ledger in the SAME increment, committed and pushed; (2) on every resume the
> task DB is restored FROM this ledger + the transcript's TaskCreate/TaskUpdate record — never
> from memory; (3) task KEYS are the SUBJECT SLUGS below, never bare #N (slot numbers collide
> across containers).
>
> **Branch:** `claude/soundbox-kit-migration-iz1jwf` (designated). **Authoritative design:**
> `seeds/seed-stage0-v1.yaml` (the contract) + `tasks/stage0-breakdown.md` (the decomposition)
> + `docs/research/COUNCIL-VERDICT-STAGE0-v1.md` (why) + `docs/07_BUILD_PLAN.md` (the stage plan).
> Each row is a distillation; the SEED is the full spec.
>
> **How to execute:** one increment at a time respecting `blocked-by`; one increment = code +
> deterministic test + commit (`S0-#n: <proof> — <what>`); the main loop re-runs every gate
> before marking done. Heavy/live/container work runs ON THE PC via `scripts/pc.sh`
> (`PC-BRIDGE.md`); `NOT run here` is stated, never skipped silently.

## 0. STATUS (updated 2026-09-03)

Pipeline (findings → council → interview → seed → breakdown): **COMPLETE**, all committed.
Build: **NOT STARTED** — first pending increment is `s0-01-registry-schemas-validator`.
PC bridge: live this session (spike `pc-bridge` recorded); Buzz relay stack, OmniRoute,
Phoenix/OpenObserve already running on the PC; runsc absent; rustup has 1.95.0.

## 1. Tasks

| slug | increment | status | blocked-by | gate (deterministic) |
|---|---|---|---|---|
| s0-00-pc-bridge-probe | #0 spike: bridge liveness + PC capability probe | done 2026-09-03 (`abb16a0`) | — | `spikes/pc-bridge/result.json` present, redacted |
| s0-01-registry-schemas-validator | #1 registry + schemas + validator (empty-set semantics) | pending | — | integrity green on empty set, stage gate RED, forged-digest/drift/unclassified negatives RED |
| s0-02-runner-ledger-ci-markers | #2 runner + ledger generator + CI split checks + probe-backed markers | pending | s0-01 | generator byte-identical ×2; validator mutation audit kills forge/drift/marker mutants |
| s0-03-spike-rust-ai-memory | #3 spike rust-ai-memory (PC: `cargo +1.95.0`) | pending | s0-02 | fact recorded either way; classification_effect per map-rust-s006 |
| s0-04-spike-dockerd | #4 spike dockerd-in-sandbox (secondary; PC uses podman) | pending | s0-02 | fact recorded |
| s0-05-spike-runsc | #5 spike runsc install ON THE PC (systrap, no KVM needed) | pending | s0-02 | fact recorded; map-runsc-s008 |
| s0-06-spike-selective-egress | #6 spike selective egress (S0-05 mechanism; veth/proxy, never bare unshare) | pending | s0-02 | positive leg reaches the allowed target, negative leg denied with exact reason |
| s0-07-s0-01-acp-conformance | #7 S0-01 ACP conformance (PC podman stack; real pinned hermes-acp) | pending | s0-02 | normalized-golden transcripts ×2; `protocol-violation: missing required initialize field` |
| s0-08-s0-02-buzz-auth | #8 S0-02 Buzz authorization (four DISTINCT denials) | pending | s0-02 | one turn on allowed; four named denials |
| s0-09-s0-07-fubuki | #9 S0-07 Fubuki corrections | pending | s0-02 | ordered lint fixture; record_id join; hash stable ×2 |
| s0-10-s0-09-foundry-adr | #10 S0-09 ADR + conformance shell | pending | s0-02 | section removal → RED |
| s0-11-s0-10-gbrain-adr | #11 S0-10 ADR + conformance shell | pending | s0-02 | credential-isolation statement removal → RED |
| s0-12-s0-12-license-sbom | #12 S0-12 license/notices/SBOM pin-diff shell | pending | s0-02 | pin mutation → RED |
| s0-13-s0-06-four-scope | #13 S0-06 four-scope adapter proof (real ai-memory on the PC) | pending | s0-02, s0-03 | leak fixture never crosses; unauthorized tuple denied |
| s0-14-s0-03-omniroute-roundtrip | #14 S0-03 Hermes→OmniRoute live round trip (OmniRoute already up on the PC; identity = routed model id) | pending | s0-02 | tool-call round trip; upstream identity asserted; key-disable → RED; stub FORBIDDEN |
| s0-15-s0-04-compression | #15 S0-04 compression contract (sanctioned stub behind real OmniRoute) | pending | s0-14 | header asserts; request preservation; header-path mutation → RED |
| s0-16-s0-05-full-egress | #16 S0-05 full canary suite over live units | pending | s0-06, s0-07, s0-14 | every unit's canary FAILS after its positive control; gate-off → RED |
| s0-17-s0-08-gvisor | #17 S0-08 containment spec + fixtures; live run on the PC after the runsc spike | pending | s0-02, s0-05 | marker re-probed every CI run; grep-gate fails on missing marker |
| s0-18-s0-11-eval-hardening | #18 S0-11 runner design + rubric isolation | pending | s0-02 | unprivileged/no-cred/no-net rubric; zero chmod-777/host-net hits |
| port-trading-system-setup | tooling: port the trading-system setup wholesale (hooks, ops scripts, ledgers, CLAUDE.md, harness-ports, wiki) | in_progress 2026-09-03 | — | hooks active; lint test green; harness-ports tests pass; wiki compiled |

## 2. LIVE ledger (append-only sync blocks; newest first)

**2026-09-03 sync (batch C):** `port-trading-system-setup` — CLAUDE.md rewritten onto the clean-build
structure (skills authoritative, GIT BRANCH RULES → push_clean/safe_commit, QUARTET section, the planning
repo's 15 standing rules folded in); SHELL SYNTAX GATE added to pre-commit (+ `tests/test_shell_syntax.py`)
after batch A shipped a dead syntax tail in post-commit; project MCP servers registered at user scope by
setup.sh (gitnexus/aleph/phoenix-docs); `code-intel-trio` re-pointed at this repo's slug. Batch D
(harness-ports/Codex/Hermes) in flight on a delegate; AGENTS.md/.hermes.md ports + E (wiki-init) next.

**2026-09-03 sync:** pipeline tasks (council, interview→seed, breakdown) DONE; `s0-00-pc-bridge-probe`
DONE (`abb16a0`); `port-trading-system-setup` OPENED (in_progress) — batches A (scripts/hooks) + B
(ledgers/docs/tests/wiki config) landing this commit; C (CLAUDE.md rewrite), D (harness-ports),
E (wiki-init) next. Task DB slots: #1–#3 pipeline, #4–#21 = increments #1–#18, #22 = spike #0,
#23 = the port. Owner rulings recorded: PC via bridge is the host; OmniRoute (already running) is
the model egress — no vLLM dependency.
