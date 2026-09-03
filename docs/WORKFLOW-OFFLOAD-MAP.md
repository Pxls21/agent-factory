# Workflow offload map — what runs where, every time (v1, 2026-09-03)

**Owner intent (2026-09-03):** "Look at our entire workflow end to end, break it down, and see what
can be handled by other things — things that don't require complicated thinking but need to be done
every time and consistently. Offload as much as possible." And: "this structure will be the exact
structure we use inside our first team of coding agents." So this document is two things at once:
the operating map of how THIS repo is built today (coordinator in the sandbox, lanes on the owner's
PC), and the blueprint of the first coding team the Agent Factory will run. Everything marked
PROVISIONAL is unmeasured; the probe table at the end pins routes only from evidence.

Status legend: **MECH** = mechanized (script/hook, no model) · **LANE** = runs on a PC Hermes lane
today · **MAIN** = coordinator judgment, stays in the main loop · **TODO** = designed here, not built.

## 1. The workflow, end to end, and who does each step

| # | Step (source of the rule) | Judgment | Frequency | Runs on | Route (role) | Status |
|---|---|---|---|---|---|---|
| 1 | Session resume: fetch, three-clock compare, live-state read (`session-continuity`) | low | every resume | sandbox scripts (`resume-heal.sh`, `orient.sh`, session-start hook) | none | MECH |
| 2 | Orientation questions ("where is the seam for X") (`code-intel-trio`) | low–mid | many per increment | PC lane, read-only | researcher → Gemini pro (PROVISIONAL) | LANE (template `code-search.md`) |
| 3 | Pipeline: findings → council → interview → seed → breakdown (Feature Workflow) | HIGH | per subsystem | sandbox | Fable + council agents (Opus 5) | MAIN |
| 4 | Contract negotiation: brief + pre-registered contract (`contract-gate` §1) | HIGH | per increment | sandbox | Fable | MAIN |
| 5 | Build: code + deterministic tests + worktree commits (`build-loop`) | mid | per increment | PC lane | code-implementer → `codex/gpt-5.6-sol-ultra` (owner ruling) | LANE |
| 6 | Builder's own gate pass (tests twice, hooks on commit, contract self-check) | low | per increment | PC lane, same run as 5 | same | LANE |
| 7 | Adversarial evaluation against the FULL contract (`contract-gate` §3) | HIGH-ish, separate context | per increment | PC lane (first pass) + sandbox Opus 5 verifier for spine/gate increments | adversarial-verifier → `codex/gpt-5.6-terra-xhigh` (PROVISIONAL) | LANE template `verify-contract.md`; sandbox verifier exists |
| 8 | Repair rounds (bounded, ≤3) | mid | when 7 fails | PC lane | code-implementer | LANE |
| 9 | Final verdict, harvest (patch home → `git apply --index`), commit with reasoning record, push | HIGH | per increment | sandbox | Fable | MAIN (push mechanics MECH: `push_clean.sh`) |
| 10 | Bug-echo sweep after every fixed defect (`build-loop` step 5) | low | per defect | PC lane, read-only | echo-sweeper → Gemini flash (PROVISIONAL) | LANE template `bug-echo-sweep.md`; rating review stays MAIN |
| 11 | Registry row + AP_SCREEN extension for a new anti-pattern | mid | per defect class | sandbox | Fable | MAIN (the sweep's DATA feeds it) |
| 12 | Wiki freshness: live-state + topic deltas per landed batch (wiki mandate) | low–mid | per push | PC lane | curator → Gemini flash (PROVISIONAL) | LANE template `wiki-curate.md`; review MAIN |
| 13 | Transcript continuity: chat digests into the repo; lane transcripts home | none | per push / per lane | sandbox `push_clean.sh` → `transcripts/sandbox/`; PC `pc-lane.sh` → `transcripts/pc/` | none | MECH |
| 14 | Ledger + task-DB mirror (TASK-SURFACE SYNC) | low | per status change | sandbox | Fable (a curator PROPOSAL may draft it; the coordinator writes it) | MAIN |
| 15 | Turn retro: wiki delta · bugs→registry · nuance→skill · easier-next-time (`turn-retro-gate.sh`) | mid | per landed batch | sandbox Stop hook prompts; execution by Fable, with 10/12 as lanes | Fable | MAIN (inputs LANE) |
| 16 | Gates on commit/push: pyflakes delta, AP screen, shell syntax, skill sync, trailer gate, wiki-stale | none | every commit/push | git hooks, both hosts | none | MECH |
| 17 | Spikes (Wave 0): facts recorded either way, classification through the frozen mapping | low | per spike | PC lane | code-implementer (or researcher when read-only) | LANE |
| 18 | PC bring-up / profile / tool install (`pc-setup.sh`, `hermes-config-merge.py`) | low | per host | scripts over the bridge | none | MECH |
| 19 | Model-route probing (this table's evidence) | low | per candidate route | PC lane, fixed probe brief | the candidate itself | TODO (probe brief below) |
| 20 | Research prompts / external research | HIGH to frame, low to fetch | rare | sandbox frames; PC lane fetches | researcher → Gemini pro, web allowed | MAIN + LANE |

Rules that hold across every row: a lane never pushes, never opens PRs, never issues a gate verdict;
the coordinator never self-accepts spine work; every gate is deterministic and LLM-free; briefs are
files with a PIN; reports are DATA. The only things that still cost coordinator tokens are rows
3, 4, 9, 11, 14, 15 — design, contracts, verdicts, and the ledger.

## 2. Roles → routes (PROVISIONAL until §4 pins them)

> **PINNED by the owner 2026-09-03:** the routes are now the four OmniRoute COMBOS `agentfactory-build` / `-verify` / `-research` / `-sweep` (priority failover chains created via Codex; definitions in OmniRoute's `combos` table; each answered a 24-token probe 200 and Hermes reached `agentfactory-verify` end to end). `pc-lane.sh` maps roles to them; the table below records what each combo reaches first.

| Role (`harness-ports/roles/`) | Default route (`pc-lane.sh`) | Effort | Why this class of model |
|---|---|---|---|
| code-implementer | `codex/gpt-5.6-sol-ultra` | ultra | owner ruling: "OpenAI sol 5.6 on the highest" |
| adversarial-verifier | `codex/gpt-5.6-terra-xhigh` | xhigh | a different variant than the builder so the two do not share blind spots; still strong |
| researcher / evidence-gatherer | `gemini/gemini-3.1-pro-preview` | high | owner: Gemini for search; long context over the tree |
| curator, echo-sweeper | `gemini/gemini-3-flash-preview` | medium | consistent, bounded, cheap; correctness is checked by the coordinator's review of a patch/table |
| (reserve) free grunt | `auto/best-free`, `free-reasoning`, `auto/coding:free` | — | zero-cost sweeps once a probe shows they follow the report shape |
| (reserve) review | `codex/codex-auto-review` | — | OmniRoute exposes a Codex review route; untested |

OmniRoute (2026-09-03 catalogue, 2520 ids): 38 `auto/*` aliases, 4 `free-*`, 59 direct `gemini/*`,
27 `codex/*`, Claude via several providers (`auto/claude-opus`, `auto/claude-sonnet`), plus openrouter
(1015). Every route above was seen in `/v1/models`; none but `codex/gpt-5.6-sol-ultra` has been run.

## 3. The lane kit (what makes it transportable)

`harness-ports/` is the kit: `bin/pc-lane.sh` (worktree-pinned lane runner, role→route defaults,
transcript export), `bin/pc-setup.sh` (host bring-up), `bin/hermes-config-merge.py` (profile merge),
`bin/hermes-session-export.py`, `roles/*.md`, `briefs/*.md` (templates), `hermes/config-snippet.yaml`
(skills dir, MCP servers, hooks, lane approvals with hard denies), `tests/`. Sandbox side:
`scripts/pc.sh`, `scripts/pc_bridge_exec.py`, `scripts/pc_lane.sh`, `scripts/transcript_export.py`,
`scripts/push_clean.sh`. Runbook: `PC-BRIDGE.md` §Hermes BUILD lanes. Bring-up on a new repo/host:
clone → `pc-setup.sh` → `hermes profile create --clone <name>` → `hermes-config-merge.py` → the two
diagnostic lanes (placement + guards) → first real brief. Eight things that broke here and are now
tests or defaults: `docs/INCIDENT-LOG.md` (2026-09-03 bring-up entry).

## 3b. Prompt weight and resilience (measured 2026-09-03)

`hermes prompt-size` on the lane profile: system prompt 81 KB, of which the skills index is 45 KB
(382 external + 90 bundled skill descriptions on EVERY call) plus 42 KB of tool schemas and 24 KB of
context files. The first increment lane died on `HTTP 503: Structurally heavy chat request capacity
is busy` from the Codex route after three retries. Two mechanisms now in place: (1) lanes load a
CURATED skill subset — `harness-ports/lane-skills.txt` → `harness-ports/bin/sync-lane-skills.sh` →
`.agents/lane-skills/` (25 workflow skills, 520 KB; pre-commit gate keeps it in sync) — and the lane
profile points `skills.external_dirs` there; (2) the profile carries a `fallback_providers` chain
(`sol-xhigh` → `terra-ultra` → `gpt-5.5-xhigh`, all through OmniRoute, key via `OMNIROUTE_API_KEY` in
the profile `.env`) so a busy route fails over instead of killing the lane. (3) The lane profile disables the toolsets a lane never
uses (`hermes tools disable browser vision image_gen tts memory session_search clarify delegation
cronjob computer_use`): tool schemas 42 KB → 19 KB (21 → 13 tools), system prompt 47 KB. Round 3
still died on the same 503 with the skills trimmed and the chain installed while a second lane
(the Gemini probe, itself stuck on a rate-limited key pool) was open on the gateway; round 4 runs
alone with all three trims — the outcome pins whether the 503 is request weight or gateway
concurrency.

## 4. Probe plan for the routes (pins §2; nothing above is final until this table has rows)

> Quirk (2026-09-03): the FIRST chat call on a route after idle sometimes returns HTTP 200 with an
> EMPTY body (JSON parse fails); the immediate retry succeeds. Probe scripts retry once before
> declaring a route dead; Hermes's own in-process retries already cover lanes.

Probe = the same read-only brief per candidate (`harness-ports/briefs/code-search.md` with a fixed
question that has a known answer in this tree), role researcher, `HERMES_MODEL=<candidate>`.
Recorded per candidate: wall time, `usage.json` tokens and calls, whether the report shape was
followed, whether the known answer (file:line) was found, and any refusal/format failure.

| Candidate | Wall | Calls / tokens | Shape followed | Found the fact | Verdict |
|---|---|---|---|---|---|
| `codex/gpt-5.6-sol-ultra` (baseline) | 3m43s (trial build lane); increment-#1 build round 4 landed the whole increment | 16 calls (trial) | yes | yes (spike files) | WORKS for build lanes; THREE lane runs died on `HTTP 503 structurally heavy chat request capacity is busy` (two build rounds, one repair round 2026-09-03 11:2xZ) while 24-token probes on `-sol-ultra` and `-sol-xhigh` answered 200 in 1.5-2.5 s the same minute — a weight-keyed, transient refusal; `pc-lane.sh` now retries the attempt on that exact signature (3×, doubling backoff from 60 s) — see §3b |
| `codex/gpt-5.6-sol-xhigh` | — | — | — | — | 24-token probe 200 in 1.5 s (2026-09-03); the explicit step-down route (`HERMES_MODEL`) when `-ultra` keeps refusing; not yet measured on a lane |
| `codex/gpt-5.6-terra-xhigh` | — | — | — | — | first lane measurement in flight (increment-#1 verify lane 2026-09-03 12:0xZ) |
| `gemini/gemini-3.1-pro-preview` | 7m41s (all retries) | 0 completed | — | — | UNAVAILABLE 2026-09-03 09:00Z and still 429 `model_cooldown` at 11:06Z; re-probe later |
| `gemini/gemini-3-flash-preview` | 2.2s (24-token probe) | 1 call | n/a (probe) | n/a | AVAILABLE 2026-09-03 11:06Z (200, served `gemini-3-flash-preview`); next: a real curator/researcher lane |
| `auto/best-free` | 15.2s (24-token probe) | 1 call | n/a | n/a | AVAILABLE 2026-09-03 11:06Z — resolved to `gemini-3-flash-preview`; slower than naming flash directly |
| `free-reasoning` | 8.7s to fail | 1 call | — | — | UNAVAILABLE 2026-09-03 11:06Z: 502, every upstream in the pool 403 |
| `codex/codex-auto-review` | 1.6s (24-token probe) | 1 call | n/a | n/a | AVAILABLE 2026-09-03 11:06Z (200); candidate for echo-sweeper/reviewer lanes |

## 5. The coding-team blueprint (owner: "two birds, one stone")

The first Agent Factory team mirrors this map one-to-one: a **coordinator** (plans, contracts,
verdicts, ledger), **builders** (implementation lanes, worktree-pinned, never push), **verifiers**
(separate context, graded against the contract, red tests as findings), **researchers** (evidence
tables, search-strong route), **curators** (continuity: wiki, transcripts, proposals), and the
**mechanical plane** (hooks, validators, transcript sync) that no model may bypass. The governance
the product docs already specify — sole model egress through OmniRoute, fail-closed policy gates,
hash-pinned packets, proposal planes without write authority — is the same shape this map enforces
by hand today (lanes propose patches; the coordinator commits). Formalizing the team is a later
increment with its own ADR; this map is its primary-source evidence.

## 6. NOT built (first-class)

Route probes (§4); the curator lane has not run once; `build-roles.py` generates Codex layers for
three roles only; echo-sweep and code-search templates are untested by a real run; no automatic
scheduling of curator runs (the coordinator dispatches them after a push); the trading-system
handoff is a prompt, not a port (see `docs/HANDOFF-HERMES-LANES.md` once written).
