<!-- Evidence lane report (Opus 5 evidence-gatherer), 2026-09-22, extracted verbatim from the lane transcript; file:line anchors refer to the cloned repositories at their audited heads -->

# EVIDENCE REPORT — jevcache + Aegis

Clone root: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/jev/`
Verified heads: jevcache `a211d13` (2026-09-19); Aegis `60321ed` (2026-09-20 19:25:26 +0800).
Sibling dirs `jev-pruner/`, `laya/` also exist there — out of brief, not read.

---

## PART A — jevcache

### A1. What is distributed

| Fact | Evidence | Grade |
|---|---|---|
| Repo = 2 tracked files: `README.md`, `og.png` | `git ls-files` → 2 entries | SOLID |
| **No source of any kind** — no `.rs`, `.ts`, no `Dockerfile` | `find jevcache -not -path '*/.git/*'` returns only those 2 | SOLID |
| **No LICENSE file** | `ls -la` grep for licen/copying → none | SOLID |
| License is prose only: "jevcache is **free to use**… Not affiliated with TypeSafe (Jev is their model)." | README.md:122-124 | SOLID |
| Installer `curl -fsSL jevcache.sh/install \| sh` | README.md:19, 24 | SOLID |
| Alternative: binary from GitHub Releases | README.md:19 | SOLID |
| "single static binary (~2–3 MB, no runtime) for macOS/Linux, arm64 or x64" | README.md:27 | SOLID |
| Checksum claim: "The installer verifies a SHA-256 checksum before installing." — asserted, unverifiable here (no installer in repo) | README.md:28 | SOLID (quote) |
| "The CLI is written in Rust; its fingerprint is byte-identical to this repo's TypeScript core" — no TS present in *this* repo | README.md:32-33 | SOLID (quote); claim UNVERIFIED |
| `Dockerfile` referenced ("See `Dockerfile`") but absent | README.md:59 vs file list | SOLID |

### A2. Local-backend contract, commands, serve API, env

| Item | Value | Evidence |
|---|---|---|
| `JEVCACHE_LOCAL_URL` default | `http://127.0.0.1:8080/v1/decide` | README.md:73 |
| Local endpoint shape | `{state,questions}` → `{answers}` | README.md:73 |
| `JEVCACHE_BACKEND` | default `local`; `local\|jev\|mock` | README.md:71 |
| `TYPESAFE_API_KEY` | no default; key for `jev` backend, `POST /v1/systemone`, "never stored" | README.md:72 |
| `JEVCACHE_DIR` | `~/.jevcache` (ledger + schemas) | README.md:74 |
| `JEVCACHE_HOST`/`JEVCACHE_PORT` | `127.0.0.1` / `9000` | README.md:75 |
| `JEVCACHE_SERVE_TOKEN` | none; bearer token required by `serve` when set | README.md:76, 58 |
| `JEVCACHE_API_URL` | `https://jevcache.sh/api` (hosted commons base) | README.md:116 |
| `JEVCACHE_API_KEY` | none; write key auto-minted on first `publish --remote`, cached at `~/.jevcache/apikey` | README.md:117, 111-112 |

Commands (README.md:38-48): `demo` · `decide --schema S --state F` (decide, cache on miss) · `recall` (local only) · `serve [--host][--port]` · `publish` · `add <url>` · `replay --schema S --cases cases.jsonl` · `schemas` · `stats`. Undocumented in that block but used at README.md:108: `jevcache use --schema … --state …` (recall from hosted index).

**Exit codes — only one is stated:** `recall` exits **3** on a miss, "so CI can branch on it" (README.md:41, 51-52). No other exit code documented anywhere. SOLID on the gap.

Serve API (README.md:63-64), verbatim:
```
POST /decide  { schema, state }   → { answers, cached }   # caches on a miss
POST /recall  { schema, state }   → { hit, answers }       # never calls a backend
```
`decide()` = recall, then on miss route to configured backend and cache (README.md:29-30). Schemas load from `./jevcache.schemas.json` or `~/.jevcache/schemas/*.json`; state is a JSON file or `-` for stdin; a bare string is a valid state (README.md:50-51).

### A3. Ledger design as described

| Element | Description | Evidence |
|---|---|---|
| Key domain | decision ≈ pure function of `(model, schema, state)` | README.md:3-4 |
| Store | "embedded, zero-dependency store (in-memory map + append-only log)"; point lookup = map access | README.md:9-10 |
| Order of operations | "State is redacted and canonicalized *before* it's hashed" | README.md:11-12 |
| PII redacted | emails, phones, long digit runs | README.md:12-13 |
| Volatile fields redacted | ids, timestamps — "never enter the key" | README.md:13 |
| Per-schema salt | "For sensitive schemas, a per-schema `salt` keeps outsiders from enumerating decided states." | README.md:14 |
| Publish format | one file per schema, "fingerprints and answers only, never raw state"; → `~/.jevcache/shared/<schema>.jevcache.json`; plain JSON, "inspect it before you add it" | README.md:80-82, 88, 99 |
| Publish variants | `--gist` (needs `gh` CLI, prints URL) · `--schema` · `--remote` | README.md:90-91, 107 |
| `add` side effect | "also registers the schema locally" | README.md:98 |
| Hosted index | `https://jevcache.sh/api`, reads open and keyless, writes need minted key | README.md:103, 111-112 |
| Hash algorithm, canonicalization rules, salt derivation | **not specified** | — |

### A4. Determinism / drift / CI claims (verbatim)

- "**Deterministic CI.** Publish fixtures, `replay` them, catch model drift." (README.md:15)
- "A Jev decision is (approximately) a pure function of `(model, schema, state)` — so it's memoizable." (README.md:3-4)
- "same decisions, fewer bills, and deterministic replay in CI" (README.md:4-5)
- "it never proxies or resells inference (your key stays on your machine)" (README.md:6-7)
- "so a Rust ledger, the TS internals, and the hosted commons all share the same keys" (README.md:33)
- "`recall` exits **3** on a miss so CI can branch on it." (README.md:51-52)
- "only fingerprints and answers cross the wire, never raw state" (README.md:104)
- Roadmap: "a decentralized index over the Hyperspace P2P network, and per-recall pricing" (README.md:119-120)

---

## PART B — Aegis

### B5. Identity

| Item | Content | Evidence |
|---|---|---|
| Tagline | "**Aegis Method Pack** — Make your AI coding agent trustworthy: fewer reworks, safer changes, proof before 'done'." | README.md:23-28 |
| English default | "English is now the default GitHub README" | README.en.md:1-3 |
| Version | 2.10.6 | package.json:3; .claude-plugin/plugin.json:4 |
| Derived from | Superpowers (obra/Jesse Vincent) + inspiration from mattpocock/skills | README.md:244-255; LICENSE:3-4 (dual copyright) |

CONTEXT.md vocabulary (four terms, each with `_Avoid_` + `_Authority_` lines):
- **Aegis Method Pack** — portable host-installable method layer owning skills, workflow discipline, advisory runtime-ready outputs (CONTEXT.md:9-13)
- **Host Adapter** — host-specific layer mapping host context into governance input, "without becoming the authority owner" (CONTEXT.md:15-19)
- **Runtime Core** — "**future** independent authority layer for baseline truth, policy snapshots, gate decisions, evidence sufficiency, and completion authority" (CONTEXT.md:21-25)
- **runtime-ready artifact** — advisory draft/hint/projection/evidence bundle, "without carrying authoritative decision power" (CONTEXT.md:27-31)

ADRs (`docs/adr/`, 4 files, bodies largely Chinese):
| File | Title |
|---|---|
| ADR-0001-aegis-method-pack-is-not-runtime-core.md | "`Aegis Method Pack` 不是 `Aegis Runtime Core`" |
| ADR-0002-kimi-native-plugin-is-the-automatic-entry.md | "Kimi 原生 Plugin 是 Aegis 自动入口" |
| ADR-0003-current-branch-first-git-lifecycle.md | "当前分支优先的任务级 Git 生命周期" |
| ADR-CREATION-GATE.md | "ADR Creation Gate" — Three Conditions, first = "Hard to Reverse" |

Target-state one-paragraph (AEGIS_TARGET_STATE.md:27-38, Status `Approved`): the repo's target state is "not a complete platform" but `Aegis Method Pack (runtime-ready)` — a method layer integrating `ADD + TLREF + Dual-Track Governance`, retaining the superpowers distribution skeleton and plugin-installable capability, cross-host installable, "capable of stably producing runtime-ready drafts / hints / projections", "without overstepping into runtime authority".

### B6. Inventory by directory

**skills/ — 22 skills**, each a dir with `SKILL.md` (+ 0-8 reference files). Purposes from front-matter `description`:

| Skill | Purpose (front matter, condensed) |
|---|---|
| anti-entropy-governance | retiring old logic, collapsing duplicate owners, removing fallbacks, schema/source-of-truth boundaries; destructive execution needs explicit confirmation |
| brainstorming | ambiguous/high-complexity features, architecture choices, contract changes, pressure-testing a plan |
| communicating-concisely | caveman mode / fewer tokens on explicit request |
| dispatching-parallel-agents | 2+ independent tasks without a written plan, no shared mutable state |
| establishing-project-context | shared project language; conflicting/renamed/deprecated domain terms |
| executing-plans | executing a written plan across sessions or with review checkpoints |
| finishing-a-development-branch | merge/PR/branch lifecycle of task-created branch or worktree |
| first-principles-review | Occam's-razor review; competing constraints, fallback growth, duplicate owners |
| goal-framing | `/aegis-goal`: define goal, success evidence, stop condition, task boundaries |
| long-task-continuation | multi-step tasks spanning context resets/sessions; state-loss risk |
| receiving-code-review | handling review feedback that is unclear, risky, disputed, questionable |
| recording-architecture-decisions | create/amend/supersede ADRs; baseline sync |
| requesting-code-review | independent review after slices, before high-risk merges |
| subagent-driven-development | executing a written plan with independent tasks via delegation |
| systematic-debugging | any bug/test failure/unexpected behavior, **before** proposing fixes |
| test-driven-development | strict test-first TDD on explicit request or `TDD Route: strict` |
| update-aegis | `aegis:update`, upgrade installed method-pack |
| using-aegis | turn start / skill routing (the SessionStart hot path) |
| using-git-worktrees | concurrent checkout; dirty state blocking branch switch |
| verification-before-completion | before claiming complete/fixed/passing/ready to commit/merge/publish |
| writing-plans | durable plan document from an approved spec |
| writing-skills | creating/editing/verifying skills |

Multi-file skills: systematic-debugging (9 files incl. `root-cause-claim-contract.md`, `root-cause-tracing.md`, `defense-in-depth.md`, `feedback-loop-construction.md`, `find-polluter.sh`), subagent-driven-development (4, incl. three role prompts), brainstorming (3), writing-plans (3), using-aegis (SKILL.md + `references/`), requesting-code-review (+`code-reviewer.md`), verification-before-completion (+`expanded-closeout.md`), long-task-continuation (+`durable-work-guidance.md`), establishing-project-context (+`CONTEXT-FORMAT.md`), writing-skills (+`testing-skills-with-subagents.md`).

**commands/ — 3 files, all deprecated tombstones**: `brainstorm.md`, `execute-plan.md`, `write-plan.md`, each front-matter "Deprecated - use the aegis:<skill> skill instead" (commands/brainstorm.md:2; execute-plan.md:2; write-plan.md:2).

**hooks/ — 5 files**:
| File | Event | What it does |
|---|---|---|
| hooks.json:3-13 | `SessionStart`, matcher `startup\|clear\|compact`, `async:false` | runs `"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-start` |
| hooks-cursor.json:4-8 | `sessionStart` | runs `./hooks/session-start` |
| .github/hooks/session-start.json:4-11 | `sessionStart`, timeoutSec 30 | bash + powershell variants, sets `AEGIS_HOOK_JSON_STYLE=compact COPILOT_CLI=1` |
| session-start (bash, 140+ lines) | — | reads `~/.config/aegis/config.toml` for `activation_mode` (auto/explicit, default auto) and `tdd_mode` (auto/off, default off) (:10-59); on `explicit` prints `{}` and exits 0 (:65-68); warns if legacy `~/.config/aegis/skills` exists (:71-75); reads `skills/using-aegis/SKILL.md` and injects it as session context wrapped in `<EXTREMELY_IMPORTANT>` (:77, 95); emits host-specific JSON — Cursor `additional_context`, Claude Code `hookSpecificOutput.additionalContext`, else top-level `additionalContext` (:97-140) |
| run-hook.cmd:1-11 | — | cmd/bash polyglot wrapper; extensionless hook names chosen to dodge Claude Code's Windows `.sh` auto-detection |
| copilot-session-start.ps1:1-12 | — | pwsh variant; sets `AEGIS_HOOK_JSON_STYLE=compact`, same legacy-skills + using-aegis paths |

**extensions/ — 6 files**: `dsh/bootstrap.js`, `dsh/index.js`, `dsh/cordis.patch.yml`, `omp/index.ts`, `pi/index.ts`, `shared/aegis-bootstrap.ts`.

**scripts/ — 7 files (4,244 Python lines)**: `aegis-workspace.py` (1942 — workspace/ADR/evidence-bundle CLI) · `aegis-doctor.py` (1063 — install verification + `~/.config/aegis/config.toml` writes + Codex `AGENTS.md` routing block) · `aegis-update.py` (1053 — host-scoped updater) · `aegis-deferred-ledger.py` (186) · `sync-to-codex-plugin.sh` · `bump-version.sh` · `log-window.sh`.

**benchmarks/ — README + 12 result files (3 batches × json/svg/en.md/zh-CN.md)**. Benchmarked: frozen held-out A/B of Codex-client runs with vs without the Aegis projection, measuring **contract pass rate** and **unsafe outcomes**. Headline (README.md:52-53, 68-69): 61.67% → 93.33% (+31.67 pp), unsafe 13.33% → 0%, 95% case-cluster interval +15.00 to +50.00 pp, 120 valid runs / 20 cases, `gpt-5.6-sol`/`xhigh`, Aegis 2.7.6, 2026-08-11. Result JSON carries `attempts` {passes 93, fails 27, total 120, invalid 0}, `batchDigest`, `batchId`, per-case `{arm, caseId, contractPass, repetition, scenarioClass, unsafeOutcome}` (json:1-45). Stated limits: "bounded advisory evidence", "review was arm-hidden technical review, not independent human review", "host events did not return the observed model identity" (README.md:63-64, 69); benchmarks/README.md:30-42 adds that snapshots are "not a `GateDecision`, `PolicySnapshot`, runtime authority… or final completion authority", and that extended-profile repetitions "are not statistically independent".

**tests/ — 362 tracked files** (83 py, 82 sh, 69 json, 66 txt, 40 md, 10 jsonl). Split: `e2e/` 253 files / 56 entries (release + governance verification orchestration), `helpers/` 40 (benchmark runner, scorer, renderer, isolation, provider preflight), `explicit-skill-requests/` 20, `skill-triggering/` 17, `subagent-driven-dev/` 7, `claude-code/` 7, `opencode/` 5, `kimi-code/` 3, `antigravity/` 3, `deepseek-harness/` 2, `pi-omp-extensions/` 1, `codex-plugin-sync/` 1, `local/` 1 (gitignored, must not enter public CI — tests/README.md:31-40). Run via shell entrypoints, e.g. `tests/e2e/run-all.sh --full --host-profile none`, `tests/e2e/artifact-schema-check.sh`, `boundary-compliance-check.sh`, `tests/opencode/run-tests.sh`, `tests/codex-plugin-sync/test-sync-to-codex-plugin.sh` — all five wired into CI (.github/workflows/ci.yml:28-45). Named e2e checks include `governance-completion-contract-check.sh`, `debugging-patch-shape-gate-check.sh`, `controlled-replay-check.sh`, `minimality-reference-check.sh`, `context-budget-check.sh`, `claude-hook-permissions-check.sh`, plus per-host boundary checks. Integration tests "can take 10-30 minutes" and execute real Claude Code sessions headless (docs/testing.md:36-46). No pytest/tox config found at root; `tests/__init__.py` exists.

### B7. Install / host shape

| Fact | Evidence | Grade |
|---|---|---|
| Claude Code path = plugin marketplace: `/plugin marketplace add GanyuanRan/Aegis` then `/plugin install aegis@aegis-dev --scope user` | docs/README.claude-code.md:50-60 | SOLID |
| Marketplace name `aegis-dev`, plugin `aegis`, `source: "./"` | .claude-plugin/marketplace.json:2,9,12 | SOLID |
| Per-host manifests: `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`, `.codebuddy-plugin/`, `kimi.plugin.json`; INSTALL.md in `.codex/`, `.cursor/`, `.windsurf/`, `.opencode/` | dir listing; .version-bump.json:2-10 | SOLID |
| Kimi: `sessionStart.skill = "using-aegis"`, `skills: "./skills/"` | kimi.plugin.json:18-21 | SOLID |
| Pi/OMP/DSH via package.json fields (`pi.skills`, `omp.extensions`, `dsh.bundle.patch`) | package.json:14-31 | SOLID |
| 18 host guides | docs/README.<host>.md ×18 | SOLID |
| Writes to **user home**: `~/.config/aegis/config.toml` (activation_mode, tdd_mode), `~/.config/aegis/agents-md-state.json`, and a managed routing block in `~/.codex/AGENTS.md` delimited `AEGIS-ROUTING-BEGIN/END` | aegis-doctor.py:92,133,137,156,924-943 | SOLID |
| Writes to **target project**: `docs/aegis/` workspace — dirs `adr/ baseline/ specs/ plans/ work/` + `README.md`, `INDEX.md`, `BASELINE-GOVERNANCE.md` | aegis-workspace.py:19,118-119,326-340 | SOLID |
| Workspace CLI verbs | `init check append-index validate-artifact new-adr amend-adr supersede-adr new-work add-checkpoint add-baseline-usage add-evidence add-attempt add-drift-check bundle` | aegis-workspace.py:1619-1921 | SOLID |
| Install verification gate: `python scripts/aegis-doctor.py --write-config --json` must show `"ok": true`, `"workspaceSupport": "available"`, `"configStatus": "configured"` | README.md:82-84 | SOLID |
| Global user rules templates (EN + zh-CN), explicitly optional, "does not install Aegis or prove skill discovery", not managed by `aegis:update` | GLOBAL_USER_RULES_TEMPLATE.md:1-22; README.md:107-112 | SOLID |

### B8. Governance concepts — coded vs documented

| Concept | Implemented in code | Documented only | Grade |
|---|---|---|---|
| **gate decision** / `GateDecision` | **No implementation.** 0 hits in non-test code; the only code-adjacent occurrence is a *disclaimer string* — `aegis-workspace.py:1455` "does not determine evidence sufficiency, produce authoritative `GateDecision`, or grant `completion authority`". A *gate-input artifact* is produced: `gate-input-pack.json` with `schemaVersion/baselineRefs/impactStatement/compatPlan/retirementPlan/evidenceBundle` (aegis-workspace.py:1440-1449) | CONTEXT.md:23; AEGIS_TARGET_STATE.md; AEGIS_RUNTIME_READY_BOUNDARY.md; AEGIS_WORKFLOW_QUALITY_BASELINE.md; AEGIS_TRIGGER_HEALTH_BASELINE.md (6 md hits) | SOLID |
| **evidence sufficiency** | No implementation; 5 code hits, all disclaimer strings (aegis-workspace.py:1455 et al.) | 35 md hits — goal-framing, requesting-code-review, verification-before-completion/expanded-closeout, long-task-continuation | SOLID |
| **completion authority** | No implementation; 42 code hits, all negation strings ("does not grant completion authority", aegis-workspace.py:292, 706, 962, 1161, 1456) | 184 md hits across skills + docs | SOLID |
| **baseline truth** | **0 code hits** | 4 md: CONTEXT.md:23, ADR-0001, AEGIS_TARGET_STATE.md, AEGIS_RUNTIME_READY_BOUNDARY.md | SOLID |
| **policy snapshot** / `PolicySnapshot` | **0 code hits** for the phrase | 4 md: CONTEXT.md:23, AEGIS_TARGET_STATE.md, AEGIS_PRODUCT_BASELINE.md, AEGIS_RUNTIME_READY_BOUNDARY.md; README.md:101 lists it among things Aegis "is not" | SOLID |
| Evidence *bundles* (adjacent, coded) | `evidence_bundle_path`, `load_or_create_evidence_bundle`, `merge_attempt`, `evidence_bundle_status`, `bounded_checkpoint_markdown`, `command_add_evidence/add_attempt/add_drift_check/bundle` | — | SOLID |
| Artifact schema validation (coded) | `ARTIFACT_SCHEMAS` (aegis-workspace.py:151), `validate_artifact_data/file` (:455,519), `SCHEMA_VERSION = "aegis.schema.v0"` (:20) | — | SOLID |

Pattern: every one of the five named governance concepts is reserved for the unbuilt **Runtime Core**; the shipped code emits *inputs and disclaimers*, never a decision.

### B9. Overlap-candidate skills (facts only)

| Our concept | Aegis artifact | Evidence |
|---|---|---|
| Contract gate | `skills/verification-before-completion/` — required evidence slots `Evidence action / Result / Covered scope / Uncovered scope / Residual risk / Confidence grade A\|B\|C`; stop signals; "never claim complete then verify later" | SKILL.md:14-48 |
| Contract gate (debug) | `systematic-debugging/root-cause-claim-contract.md` — "Pre-Claim Gate", mechanical falsifiable checks before a root-cause claim; "Causal Topology Gate" replacing the single-root default | :1-20 |
| Adversarial review | `requesting-code-review/` (+`code-reviewer.md`), `receiving-code-review/`, `subagent-driven-development/{spec,code-quality}-reviewer-prompt.md`, `brainstorming/spec-document-reviewer-prompt.md`, `writing-plans/plan-document-reviewer-prompt.md`, `first-principles-review/` | dir listing |
| Root-cause debugging | `systematic-debugging/` (9 files): `root-cause-tracing.md`, `defense-in-depth.md`, `feedback-loop-construction.md`, `condition-based-waiting.md`, `find-polluter.sh` | dir listing |
| Empirical validation | `verification-before-completion/expanded-closeout.md`; "fresh falsifying check"; call-site-seam evidence rule — "a shallower seam gives false confidence. Missing seam is an architecture gap" | SKILL.md:16, 44-47 |
| Anti-pattern registry | **No registry skill.** Single "anti-pattern" hit in `brainstorming/expanded-design-guidance.md`. `debugging-patch-shape-gate-check.sh` + Patch-Shape Triage signals H1/H3/H8/H10/H11/H13 are the nearest coded analogue | grep; root-cause-claim-contract.md:23-26 |
| Session continuity | `long-task-continuation/` (+`durable-work-guidance.md`); hook re-injects `using-aegis` on `startup\|clear\|compact`; routing prefix says re-check after "continuation, session resume, context compaction" | hooks.json:5; GLOBAL_USER_RULES_TEMPLATE.md:19 |
| Orchestration | `dispatching-parallel-agents/`, `subagent-driven-development/`, `executing-plans/`, `using-git-worktrees/`, `finishing-a-development-branch/`; "orchestrat" appears once, in `using-aegis/references/complexity-governance.md` | dir listing; grep |
| Evidence tables | Slot-based text blocks (B8/B9 above), not tables. **Zero** hits for "evidence table" in `skills/` | grep |
| Hollow-green / tautology detection | **Zero** hits for "tautology" or "hollow" anywhere in `skills/` | grep |
| Governance/retirement | `anti-entropy-governance/` — fallback removal, duplicate-owner collapse, retirement triggers; `scripts/aegis-deferred-ledger.py`; `docs/current/AEGIS_DEFERRED_LEDGER.md` | front matter; file list |

### B10. License, size, languages, dates, dependencies

| Item | Value | Evidence |
|---|---|---|
| License | MIT; dual copyright Jesse Vincent (2025) + Ganyuan Ran (2025-2026) | LICENSE:1-4 |
| Size | 7.9 MB working tree (excl .git); pack 3.33 MiB; 536 tracked files | `du -sh`, `git count-objects -vH` |
| Languages | 166 md · 87 py · 86 sh · 84 json · 66 txt · 10 jsonl · 9 js · 4 yml · 4 ts · 4 svg · 1 ps1 · 1 mjs · 1 cmd | `git ls-files` ext histogram |
| Last commit | 2026-09-20 19:25:26 +0800, "docs: restore compact benchmark placement" | `git log -1` |
| **History unavailable** — clone is shallow, 1 commit | `.git/shallow` present; `git rev-parse --is-shallow-repository` → true | SOLID |
| Python deps | **stdlib only** across `scripts/` and `tests/helpers/` (argparse, json, pathlib, subprocess, hashlib, urllib.parse, ipaddress, ctypes, fcntl, resource, …) + local modules | import histogram |
| npm deps | none required; `peerDependencies` `@deepseek-ai/dsh-{agent,llm,skill-filesystem}` ^0.1.0-rc.6, all marked **optional** | package.json:32-46 |
| CI system deps | `bubblewrap` (apt), Python 3.11, actions/checkout@v4, actions/setup-python@v5 | ci.yml:14-26 |
| **Network calls in hooks/** | **None.** `hooks/session-start`, `run-hook.cmd`, `copilot-session-start.ps1` read local config + local SKILL.md and print JSON | read in source |
| **Network calls in scripts/** | **None at runtime.** All `https://` occurrences are literals inside help/doc strings: aegis-update.py:32 (dsh install hint), aegis-doctor.py:301 (`/plugins install` hint), sync-to-codex-plugin.sh:466,476,484,499 (commit/PR URLs in generated text) | grep |
| Network-adjacent code | `tests/helpers/agentic_benchmark_provider_preflight.py` — imports `ipaddress` + `urllib.parse.urlsplit` to *validate/classify* proxy URLs (`PROXY_SCHEMES` http/https/socks5/socks5h, :32) and redact credentials (`access_token|api_key|secret|password` regex, :40); `agentic_benchmark_isolation.py:690` opens a `socket.socket()` as an egress probe; benchmark runner shells out to the host CLI via `subprocess.run` and `resolve_permission_backend_bwrap` | cited lines |
| Update mechanism | `scripts/aegis-update.py` — host-scoped, `shutil.copytree/copy2` + `subprocess` (git), sync modes `junction\|symlink\|copy-skills\|plugin-managed\|repo-only`; "Aegis does not run background automatic updates by default" | aegis-update.py:23,362,555-564; README.md:93-94 |

---

## UNSURE / not found

- **jevcache:** every functional claim is UNVERIFIABLE from the repo — no installer, no binary, no checksum file, no Rust or TypeScript source, no `Dockerfile` (referenced at README.md:59), no schema/bundle sample. The SHA-256 verification, the "byte-identical fingerprint" parity between Rust and TS, the redaction rules, the salt derivation, the hash function, and all exit codes other than `recall`=3 are README assertions only. The `jevcache use` subcommand (README.md:108) and `jevcache demo` (README.md:39) are absent from the CLI block at README.md:38-48. Repo age/history: single commit, unknown whether squashed.
- **Aegis:** history unavailable (shallow clone) — no commit cadence, contributor count, or file-level chronology. I did not read `RELEASE-NOTES.md` (247 KB), `README.zh-CN.md`, the 18 host guides beyond `README.claude-code.md`, the 25 `docs/current/` docs beyond `AEGIS_TARGET_STATE.md` head + `docs/testing.md`, ADR bodies (Chinese), or 530 of 536 files. Benchmark **reproducibility not assessed** — I read result JSON structure and the README's stated limits, did not inspect the case corpus, the scorer, or whether the published numbers regenerate. `extensions/*` bodies (dsh/omp/pi bootstraps) unread. Whether any `e2e` check currently passes was **not run** (read-only posture). The `.opencode/plugins/aegis.js` body unread. `tests/local/` is gitignored, so its content is not observable from this clone.
- Neither repo was resolved against its live GitHub remote; head SHAs are as cloned.

