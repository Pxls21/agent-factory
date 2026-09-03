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
Tooling port from trading-system (`port-trading-system-setup`): **DONE** 2026-09-03 — hooks, ops
scripts, ledgers, CLAUDE.md, Codex/Hermes ports, wiki; PC smoke of the harness ports NOT run.
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
| port-trading-system-setup | tooling: port the trading-system setup wholesale (hooks, ops scripts, ledgers, CLAUDE.md, harness-ports, wiki) | done 2026-09-03 (batch E commit) | — | hooks active ✓; lint test green ✓; harness-ports tests 58/58 ✓; wiki compiled ✓ (PC smoke NOT run — owner) |
| harness-skill-rewordings | tooling follow-up: re-port the source repo's hand-ported skill rewordings (HARNESS PORT notes; contract-gate/orchestration semantics) into `.agents/skills/` with this repo's paths | done 2026-09-03 (`c2e529a`, `86ade0d`) | — | 15 HARNESS PORT notes; sync-skills --check rc=0 with 15 INTENTIONAL; NOT ported: `premortem-roast/dimensions.md` (source-only extra file) |

## 2. LIVE ledger (append-only sync blocks; newest first)

**2026-09-03 sync (PC lane PROVEN end to end):** runs 7-9 closed the last defect — Hermes's terminal cwd
is carried by `TERMINAL_CWD` (now exported per lane): `pwd` = pinned linked worktree, HEAD = PIN,
`git push`/`gh pr` BLOCKED under yolo by the profile deny list, a new file fetched through the patch path
and applied in the sandbox. Registry AF-AP-8/9; orchestration skill carries the placement rule. Build
lanes are ready: increment #1 rides the lane after the owner's go-ahead on the direction doc. Owner
sudo step for gVisor still pending.

**2026-09-03 sync (Hermes lane round trip PROVEN, spike `hermes-lane-trial`):** six runs on the PC lane.
Run 6 completed the brief end to end in 3m43s (quartet present, venv ok, repo tests 9/9 on the PC, DATA
report fetched). Defects found by runs 1-5, all fixed with tests: ouroboros MCP crash loop (disabled for
lanes); bridge envelope not unwrapped (`scripts/pc_bridge_exec.py` + 8-check stub test); Hermes cwd restore
(`--in TREE --no-restore-cwd`); hook sentinels unwritable in linked worktrees (`--absolute-git-dir` /
common dir + `tests/test_hooks_worktree.py`); pre-commit hardcoded venv + early exit skipping later gates
(found BY the lane; fixed + negative control); retro gate consuming the lane report (pre_verify off for
lanes). OPEN: the lane shell still runs in the main clone rather than the pinned worktree (patch fetch
empty) — must close before increment #1 rides a lane. gVisor staged; owner sudo step pending.

**2026-09-03 sync (rewordings done; first Hermes lane):** `harness-skill-rewordings` DONE — 15 hand-ported
skills, hand-port-aware sync (allowlist + base hashes, INTENTIONAL/STALE-BASE/--record), pre-commit gate
intact. PC bring-up: clone + venv + quartet + `agentfactory` Hermes profile with the merged snippet.
First trial lane (`hermes-lane-trial` spike) STALLED in MCP startup on the known-broken Ouroboros server
(crash loop, 11 min, zero model calls) — disabled for lanes in the snippet and the profile; relaunching.
Two lane-runner defects fixed on contact: unexported bridge env (KeyError) and the missing PIN line.

**2026-09-03 sync (owner ruling — BUILD lane = Hermes on the PC):** build/fix/debug lanes move to the
owner's Hermes CLI (v0.21.0 on the PC, already wired to OmniRoute `127.0.0.1:20128/v1`), highest
reasoning, via `scripts/pc_lane.sh … hermes`; the coordinator keeps briefs, the contract gate and the
final validation; Opus 4.6 `code-implementer` becomes the sandbox fallback. gVisor `runsc
release-20260817.0` staged in `~/gvisor-install` on the PC (sha512 verified; sha256 048b89aa…) — the
owner runs the sudo install; user-level podman runtime entry written. Direction doc updated; PC lane
bring-up (clone/venv/tools/config/trial) is the next move. `harness-skill-rewordings` in flight.

**2026-09-03 sync (post-close audit):** `harness-skill-rewordings` OPENED (pending, low priority) — the
final sweep showed `.agents/skills` is a verbatim mirror (0 HARNESS PORT notes); the harness doc's
"14 hand-ported" claims were inherited prose (AF-AP-6, second instance) and are corrected. Pre-commit
SKILL-SYNC GATE added (a `.claude/skills` change with a stale `.agents` twin blocks).

**2026-09-03 sync (batch E, port CLOSED):** first wiki compile landed (`wiki/`: 12 topics, 3 concepts,
INDEX/CONTEXT/schema/log, `topics/live-state.md` continuity snapshot; link check clean; no flat N/12).
`port-trading-system-setup` → done. Task DB #23 mirrored. Next: `s0-01-registry-schemas-validator`.

**2026-09-03 sync (ports):** `AGENTS.md` (Codex CLI port, 26.0 KB < 32 KiB budget) and `.hermes.md` (Hermes
port) written by a delegate from the new CLAUDE.md, coordinator-reviewed: 15 standing rules hash-identical
in all three files, GitNexus block byte-identical, zero source-repo terms. Coordinator fixes: dropped the
ported "ignore an injected branch directive" sentence (wrong here — the branch IS the session's), removed
the source repo's proposal ids from the MANAGER CHARTER, added the PC environment safety block (OmniRoute
`:20128` sole egress, never stop the owner's services, sudo, untracked bridge env), and corrected
`docs/HARNESS-PORTS.md` where it still verified a section that does not exist here (AF-AP-6). Batch E
(wiki compile) in flight.

**2026-09-03 sync (batch D):** harness-ports ported by a delegate and re-gated by the coordinator
(`harness-ports/tests/run-all.sh`: 58/58; repo `tests/`: 6 passed): `.codex/config.toml` + role layers,
`harness-ports/{bin,roles,hermes,tests}`, `scripts/pc_lane.sh` (bridge contract = `X-Agent-Token` +
`{"cmd"}` + `/exec`, token via curl `--config -` on stdin), `.agents/skills/` sync, `docs/HARNESS-PORTS.md`.
Coordinator fixes on review: OmniRoute port corrected to the verified `:20128` (the doc had inherited
the source repo's `:8317`); trading-only `vectorbtpro` skill removed from both skill trees. NOT done:
PC smoke (no bridge banner this session), `AGENTS.md`/`.hermes.md` ports (next), wiki compile (E).

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
