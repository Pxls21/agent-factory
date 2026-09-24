[wiki live-state — turn-maintained continuity snapshot]
---
topic: live-state
last_compiled: 2026-09-03
---

# Live State -- continuity snapshot

## Clocks

- **Clocks re-synced 2026-09-22 12:1xZ:** origin tip dc5e378 (transcripts sync, 2026-09-22 ~12:0xZ) → local HEAD f3a9ea3 (the Jev/Laya audit commit) + this wiki delta, pushed together at the end of the turn; the sandbox tree is clean of lanes; four PC lanes live (the 2026-09-22 block under Active lanes). The two lines below are the 2026-09-15 snapshot, kept for the record.

- **Origin tip:** 2026-09-15 17:5xZ (`claude/soundbox-kit-migration-iz1jwf`) — de71481 = VERIFY-QM1 findings, on top of ca4dd20 (QM0-b restart-when-idle + AF-AP-87), 60615c9 (N5m probe r16) and 2e8f5b6 (the exporter --tool-body-cap); this ledger plane follows.- **Local HEAD:** = origin + this ledger plane (pushed at the end of the turn); the sandbox tree is CLEAN of lanes — NO sandbox lane is live; TWO PC lanes are live — VERIFY-GOV1 on the LOCAL verify route (since 15:01Z) and A5n (checker round 16, cloud build, since 16:50Z); QM0-b (ca4dd20), N5m (60615c9) and VERIFY-QM1 (de71481) are HOME and LANDED; two cloud slots are free; the next dispatch (QM1-c, VERIFY-N5m) follows.  survivors) landed with verifier verdicts; checkpoint 7a (A5c header requirement) and 6 are on origin. SHAs are rewritten by `push_clean.sh` at push, so this page names commits by subject.
- **Local HEAD:** = origin + this ledger plane; the sandbox tree is CLEAN of lanes; FOUR PC lanes are live — VERIFY-GOV1 on the LOCAL verify route (since 15:01Z, no draft yet at 18:0xZ — a long xhigh verify), A5n (checker r16, cloud, since 16:50Z), VERIFY-N5m (probe r16 verify, cloud, pid 71913, since 18:14Z) and QM1-c (the six matrix-runner fixes, cloud build, pid 75312, since 18:16Z) — the cloud slots are full; the matrix waits on the local slot (VERIFY-GOV1) + QM1-c.

## Active lanes

**2026-09-24 05:1xZ — WHAT IS LIVE NOW (this block supersedes the 04:5xZ block and the older ones below for the live set; the ledger carries the detail).**
- **PUSHED:** origin head 942ad5e (J0-b, J1-1-R3 as fdac751, J1-4, J1-5 and its hardening, AF-AP-179).
- **LIVE, SANDBOX (two agents, Opus 5.5):** VERIFY-J1-1-R3 (#216; report `tasks/briefs/laya/VERIFY-J1-1-R3-report.md`, scratch `/tmp/vj113r3/`) and K215 (#215; report `tasks/briefs/kit-k1-support/K215-report.md`, scratch `/tmp/k215/`). Read progress from those report files and scratch dirs (AF-AP-171). `.lanes-live` lists the 17 paths they may leave dirty.
- **LIVE, PC:** the J1-5 full-suite run `20260924T051153Z-942ad5e` (no model lane).
- **NEXT:** harvest both agents; paste the full suite into J1-5 (#122); then one batched verify of J1-4 and J1-5.

**2026-09-24 04:5xZ — WHAT IS LIVE NOW (this block supersedes the 04:4xZ block and the older ones below for the live set; the ledger carries the detail).**
- **J1-4 LANDED 04:5xZ, GATED-PENDING-VERIFY:** the Laya pin in `upstream.lock.yaml` (`advisory_models.laya-typed-decisions`: revision, weights digest, `laya` 0.3.5 wheel digest, the measured runtimes and verdicts, role advisory), held equal to both J0 probe JSONs and the probe report by `tests/test_laya_pin.py` (task #121).
- **J1-5 LANDED 04:5xZ, GATED-PENDING-VERIFY:** `tests/test_decisions_no_model.py`: no J1 module imports a model package, and the four J1 test files pass while `laya`, `torch`, `transformers`, `safetensors` and `huggingface_hub` are blocked in every Python process of the run, with zero import attempts (hardened 05:0xZ before the push; AF-AP-179). Task #122 stays open for the full-suite paste (seed AC 10): the pushed head's CI run and one PC run.
- **Every J1 increment has landed.** The verifies still owed: VERIFY-J1-1-R3 (#216, which must reproduce C4a and C4b's attribution or void D-067), then one batched verify of J1-4 and J1-5.
- **NEXT:** push (CI run #1018 on f83aa36 still running at 04:59Z), then VERIFY-J1-1-R3 (#216) and K215 (#215) as sandbox Opus 5.5 agents. No PC lane is live.

**2026-09-24 04:4xZ — WHAT IS LIVE NOW (this block supersedes the 04:3xZ block and the older ones below for the live set; the ledger carries the detail).**
- **J0 DONE 04:4xZ:** the PC probe ran (task #123 closed). PC, the reference venue: ASYNC-ONLY (p50 336.18 ms at 4 threads) and DETERMINISTIC; the sandbox keeps SYNC-OK for its own instance; one digest on both. J1-4 (#121) is unblocked.
- **J1-1-R3 LANDED 04:4xZ, GATED-PENDING-VERIFY:** the redaction regressions R-1, R-2, R-4 and R-3 fixed (a813d9c locally). Its D-1 forced D-067: C4 split into C4a (nothing d556c9b hides becomes visible) and C4b (against fb016d0 only attributed, counted exposures). VERIFY-J1-1-R3 (#216) must reproduce both or D-067 is void.
- **NEXT (sandbox, two agents):** VERIFY-J1-1-R3 (#216) and K215 (#215, the owed screens and bakes plus issue #63), dispatched after the push. No PC lane is live.

**2026-09-24 04:3xZ — WHAT IS LIVE NOW (this block supersedes the 04:0xZ block and the older ones below for the live set; the ledger carries the detail).**
- **VERIFIED 04:2xZ:** K150 (VERIFY-K150 MERGE-READY-WITH-FOLLOWUPS; tasks #213 and #150 closed). Follow-ups: issue #63; the nine registry promises #150 never carried moved to task #215 `registry-owed-screens-and-bakes` (with the AF-AP-175 and AF-AP-177 screens). The three empty `r_*.txt` files were VERIFY-K150's; it removed them.
- **LANDED 04:3xZ, GATED-PENDING-VERIFY:** task #211 (AF-AP-171 baked into `orchestration` §Parallel agents) and the `evidence-gatherer` re-pin to `claude-opus-5-5` (D-065; manifest tests now 2956 kit-verbatim / 16 kit-adapted). The independent check folds into task #215's verify. Dispatches still pass `model: "opus"` this session.
- **LIVE, SANDBOX (one):** J1-1-R3 (#202). It works in the non-git copy `/tmp/j113s/work`, not the worktree `/tmp/j113s/wt`; read its progress from there (AF-AP-171).
- **LIVE, PC:** the J0-b probe (pid 1085354, `/home/rocco/j0b/`, online on a hardlinked HF cache after the offline launch died on a missing `rl_common.py`). No PC lane is live.
[incident match: docs/INCIDENT-LOG.md]
# Project incident log (`agent-factory`)

> Institutional memory: the incidents behind the rules in CLAUDE.md. **Log a one-line entry
> here the moment a CLAUDE.md rule bites for real** — which section/rule it confirms, the
> concrete trigger, the fix — don't defer it to a handoff doc; a lesson recorded only there
> WILL be re-learned the expensive way (deep-work retrospective rule). GENERAL rules distilled
> from an incident still get baked into the matching skill/CLAUDE.md section; this file carries
> the full incident detail. Ported structure from `trading-system/docs/INCIDENT-LOG.md`.

**2026-09-24 05:0xZ — J1-5's no-model closure test blocked the model packages in one process and counted only failures; fixed before the push (AF-AP-179).** The coordinator's own re-read of `tests/test_decisions_no_model.py` (committed locally, not yet pushed) found two gaps. The import blocker lived only in the test's direct subprocess, so `scripts/decide-harvest` and `scripts/no_laya_in_gates.py`, which the J1 tests start as subprocesses, ran unblocked. And the test read failures, so an import the code catches, or a test that skips on ImportError, passed. The fix: a `sitecustomize` on `PYTHONPATH` installs a `sys.meta_path` blocker in every Python process of the run; the blocker logs every attempt; the suite test asserts zero attempts; a new control reds a direct import, logs a caught one and reaches a child. Two mutants on a scratch copy, each red for its reason: M-nolog (`assert [] == ['laya']`) and M-noprop (the child's import is a plain `ModuleNotFoundError`). Sibling sweep: two `builtins.__import__` blockers in `tests/test_validate_ledger.py`, sound for their claim today.

[wiki match: topics/stage0-proof-pack.md]
## 6. Key Decisions [coverage: high -- 7 sources]

**Pinned decisions from the interview** (each with rejected alternative in
[tasks/stage0-breakdown.md](tasks/stage0-breakdown.md)):
- Runner-emitted `result.json` is SSoT; ledger GENERATED, CI drift-fails (rejected: hand-authored
  ledger)
- Two SPLIT CI checks (rejected: one check doing both -- empty repo would pass)
- Spikes classify, never gate; frozen `spike_to_class_mapping` (rejected: all spikes must pass)
- Committed canonical fixtures drive REAL binaries; normalized-then-golden compare (rejected:
  byte-exact / test-time generation / stub of SUT)
- Blocked markers carry probe re-evaluated every CI run (rejected: static presence check)
- Four-way classification; status lines never a flat N/12 (rejected: 12 undifferentiated proofs)
[wiki match: topics/harness-ports.md]
## 4. API Surface [coverage: medium -- 3 sources]

- `pc_lane.sh <role> <brief> [branch]`: sandbox-side spawn (calls `pc.sh` with the PC-side script)
- `sync-skills.sh`: one-directional sync `.claude/skills/` --> `.agents/skills/` (pre-commit
  SKILL-SYNC GATE blocks a `.claude/skills/` commit whose twin is stale; a clean sync = zero DRIFT)
- `mcp-smoke.sh`: acceptance probe for MCP server connectivity
- Bridge contract for lanes: `X-Agent-Token` + `{"cmd": "bash harness-ports/bin/pc-lane.sh ..."}` + `/exec`

## 5. Data [coverage: low -- 2 sources]

- `.codex/config.toml`: Codex project configuration
- `harness-ports/hermes/config-snippet.yaml`: Hermes merge fragment
[wiki-context: excerpts are a MAP, not gospel — verify load-bearing claims against tree/ledger]
