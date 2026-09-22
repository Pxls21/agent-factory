<!-- Evidence lane report (Opus 5 evidence-gatherer), 2026-09-22, extracted verbatim from the lane transcript; file:line anchors refer to the cloned repositories at their audited heads -->

## EVIDENCE LANE — long-output sinks, model-made decisions, protected gates

Read-only. Graft index present (`graft/INDEX.md`). Rows marked SOLID (read this session) / UNSURE. Git dates from `git log -1 --date=short`.

---

## T1 — Tool-output volume sinks (where stdout/stderr enters a model context)

| # | path:line | What bounds it TODAY | Size evidence | Grade |
|---|---|---|---|---|
| 1 | Claude Code Bash tool → coordinator context (registration absent from `/home/user/agent-factory/.claude/settings.json:40-50`, which matches only `Edit\|Write\|Read`) | **Nothing in-repo.** The only compressor is the honey plugin's PostToolUse hook | unbounded | SOLID |
| 2 | `/home/user/agent-factory/sandbox-kit/honey-for-devs/hooks/logcompress-hook-impl.js:46-49` — gate reads `~/.claude/.honey-active` | **The compressor is INERT in this container**: probe 2026-09-22 → `/root/.claude/.honey-active` does not exist, so `passthrough()` fires. Plugin IS enabled (`/root/.claude/settings.json:86-88 "honey@greenpt": true`) | — | SOLID |
| 3 | same file :13-15 | Even when active, `updatedToolOutput` is ignored for built-in Bash on affected builds (anthropics/claude-code#68951); the hook "runs and stashes but the rewrite is dropped" | — | SOLID (upstream claim, not reproduced here) |
| 4 | same file :27-28 (`CRUSH_MIN_ITEMS=20`, `CRUSH_MIN_CHARS=2000`) + `eso/ccr.js:17` (`maxItems:15, firstFraction .3, lastFraction .15`) | JSON-array crush: head/tail + change-points, capped at 15 rows | "measured -38..-84% on ≥5-item arrays" (:7-8) | SOLID |
| 5 | `sandbox-kit/honey-for-devs/hooks/logcompress.js:22-23` (`MIN_RUN=3`, `GATE_LINES=25`) | Collapses only CONSECUTIVE same-template lines after ANSI strip + volatile masking | "measured 0.4% on typical coding output — real wins are retry storms/installers" (`logcompress-hook-impl.js:9`) | SOLID |
| 6 | `.claude/hooks/edit-snapshot.py:250` (`MAX_SYMBOLS=2`), `:340` (`n=4`), `:354` (`n=3`), `:365-380`, `:251` (`PROBE_TIMEOUT=8`) | PostToolUse on every `.py` Edit/Write/Read: ≤2 symbols × 1 impact line, ≤4 history lines, 1 line per AP_SCREEN hit | ~10-25 lines typical | SOLID (2026-09-22) |
| 7 | `.claude/hooks/wiki-context.py:20-21` (`MAX_PAGES=3`, `EXCERPT_LINES=12`), `:48` (`body[:40]`) | UserPromptSubmit, EVERY prompt: 40 live-state lines + 3 × 12-line excerpts | ≤76 lines/prompt | SOLID (2026-09-02) |
| 8 | `.claude/hooks/session-start.sh:35` (`head -60`), `:42` (`orient.sh … \| head -80`) | Session start / compaction resume | ≤140 lines | SOLID |
| 9 | `scripts/orient.sh:30-31` (`--turns 6 … \| head -40`), `:42,45,57` (`-12`, `head -12`, `head -5`) | Layered caps inside orient | ≤80 lines | SOLID |
| 10 | `scripts/chat_tail.py:126` (`[:600]`), `:78` (`txt[:4000]`) | Per-turn 600 chars inline; 4000 chars/message in `--export` day files | SOLID |
| 11 | `scripts/lane_context.sh:61` (`head -80`), `:63` (`--limit 6`), `:68` (`head -60`), `:75` (`head -8`), `:81-82` (`head -12`×2), `:85` (`head -12`), `:89` (`head -40`), `:39,46` (`timeout 90`) | The pack attached to every build/verify brief; `run()` prints `unmapped — …` instead of silence | ~4 s to build; line count printed at `:98` | SOLID (2026-09-15) |
| 12 | `harness-ports/bin/pc-lane.sh:217-245` — prompt = role file + brief + five standing-rule blocks; shipped whole via `hermes -z "$(cat "$PROMPT_RUN")"` (`:425`) | Only prose bounds it: CONTEXT BUDGET rule (`:229`) tells the lane not to reload skills and to read by line range | **~47 KB lane prompt** (`docs/INCIDENT-LOG.md:151, :202`); **81 KB system prompt/call, 45 KB of it a 472-skill index** before the fix (`docs/INCIDENT-LOG.md:147`) | SOLID |
| 13 | Hermes `terminal` tool output inside a PC lane | **No byte cap found in repo.** The cap is TIME: 420 s per call | `docs/INCIDENT-LOG.md:236` | SOLID |
| 14 | `scripts/pc_lane.sh:370` (report fetched whole, base64), `:346` (`head -c 300` on FAILED), `:381-395` (patch in 40 000-char slices) | Bridge caps a reply at ~45 KB → slicing + char-count verify | `pc_lane.sh:381-383`; `docs/INCIDENT-LOG.md:149` | SOLID (2026-09-22) |
| 15 | `harness-ports/bin/pc-lane.sh:464` (`head -c 200` of FAILED), `:468-469` (draft promoted to report with a PARTIAL banner) | Failure text bounded; draft unbounded | SOLID |
| 16 | `scripts/pc_suite.sh:114` (`head -40` FAILED/ERROR), `:115-118` (summary = last non-empty line + `pytest-set:` id), `:11` (log tail-bytes) | SOLID |
| 17 | `scripts/test_summary.sh:25` — `echo "$output"` prints the FULL pytest run, then `:30-31` the two mechanical lines | **Unbounded**: whatever context runs it receives the whole suite output | 1556+ test suite per CLAUDE.md | SOLID |
| 18 | `scripts/lane_gate.sh:66-68` (`head -12` of `E `/`___` lines, full log to file), `:74` (one RESULT line) | SOLID |
| 19 | `harness-ports/bin/hermes-hook-adapter.py:150-175` | Hook output on an observer event is spooled to a file and injected at the NEXT turn's `pre_llm_call`, or DISCARDED with a stderr line | latency noted explicitly at `:155-160` | SOLID |

---

## T2 — Binary / probability-shaped decisions made today

| # | path:line | Decision | Who makes it today | Inputs | Lands where |
|---|---|---|---|---|---|
| 1 | `harness-ports/roles/adversarial-verifier.md:105-113`; `.claude/agents/adversarial-verifier.md:94-97` | Gate recommendation: `MERGE-READY` / `-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID` | Qwen3.8-27B local `agentfactory-verify-local` @ xhigh on PC lanes (`pc-lane.sh:414`); Opus 5 in sandbox | diff, frozen contract, pack, tree | Lane report artifact (`tasks/briefs/pc/report-*.md`); coordinator owns final gate (`:112`) — **advisory by contract, archived as evidence** |
| 2 | same :99-100 | Per-finding class `BLOCKER`/`FOLLOW-UP`/`INFO`/`UNVERIFIED` | same | one finding + contract | **Gate-adjacent**: the verifier's mutant set becomes the NEXT repair brief's acceptance bar (`.claude/skills/contract-gate/SKILL.md:173`) |
| 3 | same :75-90 | Five-condition blocking predicate (contract mapping · canonical reproduction · material effect · concrete discriminator · task ownership) — five binary judgments per finding | same | finding + PIN tree | feeds #1 |
| 4 | `harness-ports/roles/code-implementer.md:27-31` | Premise true/false → build vs STOP-and-report | local Qwen `agentfactory-build-local` @ medium (`pc-lane.sh:413`); Opus 4.6 fallback | brief + `git log` on cited files | bounded to THREE experiments by `pc-lane.sh:242`; outcome is a DISCREPANCIES entry |
| 5 | same :40-42 | "Did I reverse a conclusion mid-task" → escalate | same | own trace | report |
| 6 | `.claude/agents/hive-reviewer.md` (frontmatter `model: haiku`; return block ~:33-38) | Per-finding `sev ∈ H\|M\|L` + `kind` slug, columnar JSON | Haiku 4.5 | diff/files | advisory; safety carve-out never compressed |
| 7 | `.claude/agents/hive-scout.md:27` | `role ∈ def\|caller\|config\|test\|other` per hit | Haiku 4.5 | grep/read hits | advisory map |
| 8 | `sandbox-kit/honey-for-devs/hooks/honey-subagent.js:27` | WORKER vs REVIEWER directive per subagent | **a regex** — `/review\|audit\|critic\|judge/i.test(agentType)` | agent_type string | prompt injection only |
| 9 | `.claude/skills/bug-echo/SKILL.md:40` | Six-dimension rating per finding (Urgency, Risk of Fixing, Risk of Not Fixing, ROI, Blast Radius, Fix Effort) + BUG/OK/REVIEW/WATCH | whichever model runs the skill (Fable today) | source tree + fix pattern | **Gate-adjacent**: a confirmed class becomes an ANTI-PATTERN REGISTRY row, which extends the deterministic `AP_SCREEN` |
| 10 | same :198-219 | Breadth routing on candidate count (full sweep / tighten / 10-site sample) | same | match count | advisory |
| 11 | `.claude/skills/prism-scan/SKILL.md:1-12` (+ `prism-full/3way/discover/reflect`) | Findings table: location · what breaks · severity · fixable-or-structural | any model | one artifact | explicitly advisory (CLAUDE.md: "a prism FINDS and INFORMS; it never DECIDES a green") |
| 12 | `.claude/hooks/wiki-context.py:67-74` | Relevance: which ≤3 wiki/incident pages to inject | **lexical score, no model** — `\|q∩headings\|×3 + \|q∩stem\|×2 + \|q∩text\|×0.1`, top-3 | prompt tokens | injected context |
| 13 | `.claude/hooks/graft-first-nag.py:40` | "Is this Grep a semantic identifier search?" | **a regex** — `re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*(\|…)*")` + path prefix test (`:31-38`) | tool_input | warns, never blocks (`:8`) |
| 14 | `.claude/hooks/turn-retro-gate.sh:48-53` | Five retro questions answered by DOING or "retro: nothing to bake" | Fable | the turn | the hook's own fire/skip is deterministic (sentinel keyed on HEAD sha, `:15-38`) |
| 15 | `scripts/pc_lane.sh:343`; `harness-ports/bin/pc-lane.sh:269,300,462` | Lane state READY / RUNNING / FAILED / FAILED-UNRETRIED; refusal class capacity vs quota vs persistence | **regexes** — `CAPACITY_RX='^API call failed after [0-9]+ retries: '`, `PERSIST_RX='^(⚠️ )?No reply: '`, `QUOTA_RX` | report.md first bytes + pidfile + launch.log mtime | decides retry vs FAILED vs harvest — **artifact-landing** |
| 16 | `docs/WORKFLOW-OFFLOAD-MAP.md:42` | "The only things that still cost coordinator tokens are rows 3, 4, 9, 11, 14, 15 — design, contracts, verdicts, and the ledger" | Fable | — | the repo's own statement of what is not offloaded |
| 17 | CLAUDE.md §SWARM (SCENARIO→FORMAT auto-switch: Attention-kind / Rundown / Spartan) | Which chat format this message takes | Fable, reflexively — **no code implements it**; styles are files in `.claude/output-styles/`, default set at `.claude/settings.json:83` | message content type | chat only |

---

## T3 — Deterministic gates / oracles that must stay model-free

Governing text, verbatim: **`.claude/skills/anti-hollow-green/SKILL.md:120-121`** — "**No LLM-judge in the gate spine.** Gate/oracle/assertion execution is deterministic exit-code / set-hash comparison; an LLM enters ONLY at codify/generate/tune time." **`docs/WORKFLOW-OFFLOAD-MAP.md:40`** — "a lane never pushes, never opens PRs, never issues a gate verdict; the coordinator never self-accepts spine work; every gate is deterministic and LLM-free." **`.claude/skills/contract-gate/SKILL.md:109-110`** (D-031's disposition rule) — "Coordinator verdict. The main loop re-runs the deterministic gates itself before commit (never self-accept applies to delegates too — an evaluator PASS is evidence, not authority)." **`.claude/skills/luck/SKILL.md:3`** — "BARRED from the gate spine, delegate briefs, and any measurement/certification verdict (no-LLM-judge law)."

| # | path:line | Rule / mechanism |
|---|---|---|
| 1 | `scripts/report_lint.py:127-140` | Token-in-cited-lines check; exit 1 on any MISS; `--min-refs` FLOOR (`:137-139`). Self-described: "Heuristic by design — it proves nothing about a report" (`:28`) |
| 2 | `scripts/ap_screen.py:43-71`, loads `AP_SCREEN`/`TEST_SCREEN` from the hook at `:25-29` | Regex registry screen over WHOLE files; "Advisory (exit 0)… never a verdict by itself, and never silently ignored" (`:9-10`) |
| 3 | `scripts/lane_gate.sh:38` (sha256+lines identity table), `:66-71` (N runs, counts must agree), `:74` (RESULT line with `tests=<sha12>`) | Static-copy gate, one pasteable line |
| 4 | `scripts/test_summary.sh:14-18` (declared inputs exported), `:30-31` | Counts are PASTED, never typed (CLAUDE.md AF-AP-37) |
| 5 | `scripts/pc_suite.sh:118-119` | `pytest-set:` id + RED rule: a summary with no `passed` count → exit 3, "pytest rc is not trusted" |
| 6 | `scripts/validate-ledger:46-49, 55-78, 262-264, 325` | Schema + canonical digest + per-file sha256 attestation → `PRESENT` / `INVALID`; four canonical classes at `:12-17` |
| 7 | `scripts/proof-runner:113-114, 219` | Per-leg stdout/stderr sha256; attestation embedded in the minted result |
| 8 | `seeds/seed-stage0-v1.yaml:570-583` | FROZEN `spike_to_class_mapping` — reclassification by `rule_id`, never judgment |
| 9 | `scripts/pc_lane.sh:169-191` | **Premise gate**: awk state machine over the brief; rc 64; "There is NO environment escape hatch for a first launch" (`:45-46`); fail-closed on an unreachable bridge (`:182-185`) |
| 10 | `scripts/pc_lane.sh:68-81` | Headroom admission: numeric floors (256 MB disk / 512 MB mem), `-1 = unknown` fails OPEN |
| 11 | `scripts/hooks/pre-commit:16-20` | pyflakes DELTA gate — blocks on NEW hits only |
| 12 | same `:26-39` / `:42-49` / `:52-62` / `:65-71` / `:74-86` | ANCHOR check · SKILL-SYNC · **MIRROR gate** (`harness-ports/tests/test_context_mirrors.sh --check`: section parity + size caps + standing-rules hash) · LANE-SKILLS · SHELL SYNTAX (`bash -n`) |
| 13 | `scripts/push_clean.sh:72-83, 96` | Tree identity across filter-branch (`:78` ABORT on mismatch), zero-trailer count (`:80-81` ABORT), push the rev-parsed SHA never HEAD |
| 14 | `harness-ports/bin/pc-lane.sh:140, 144, 152` | `git` / `gh` shim inside a lane: `push`, `remote add\|set-url`, all `gh` → exit 13 |
| 15 | `scripts/lane_context.sh:36-38, 94-97` | Refuses a nonexistent FILE (rc 64) and an empty pack — a hollow pack is not produced |

---

## T4 — Cost/time sinks already quantified in-repo

| Quote | path:line |
|---|---|
| "the lane profile shipped **81 KB of system prompt per call, 45 KB of it the index of 472 skills** (382 external + 90 bundled)" | `docs/INCIDENT-LOG.md:147` |
| "a request classified heavy … **a Hermes lane turn is ~47 KB of system prompt plus tools** … waits `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS` (default 5000)" | `docs/INCIDENT-LOG.md:202` (also `:151`) |
| "`request (**96944 tokens**) exceeds the available context size (**65536 tokens**)` four times (**97k → 104k tokens**) … Hermes compacts only at 75 % of the context length OmniRoute reports (200,000) … never compacts below ~150k on its own" | `docs/INCIDENT-LOG.md:254` |
| one verify-local turn "**95,908 tokens in**"; the silent cloud-fallback row "**93,642 in / 618 out**"; "`System message must be at the beginning.` **×343**" in 7 h; cloud rows "**105k-220k tokens each**" | `docs/INCIDENT-LOG.md:33` |
| "Final session: 21:56Z-00:02Z, **186 messages, 96 tool calls, 127 API calls, 536k input / 284k output tokens**, a 3.7 KB draft" (stopped at 2 h 05 m) | `docs/INCIDENT-LOG.md:243` |
| "spent its first **60 minutes** on item 2 — **45 tool calls, 130k output tokens, no file written**" | `docs/INCIDENT-LOG.md:246` |
| "finished the build at **4 h 53 m of lane time** … then spent **20 consecutive turns / 47 minutes** on `report_lint`" (AF-AP-76) | `docs/INCIDENT-LOG.md:248` |
| "Hermes's `terminal` tool caps one call at **420 s** on the PC" | `docs/INCIDENT-LOG.md:236` |
| lane poll ceiling: `POLL_SECONDS=15`, `MAX_POLLS=240` = **60 min** | `scripts/pc_lane.sh:119-120` |
| "the checker set is **~17 min per run**" | `scripts/lane_gate.sh:9` |
| "the bridge caps a reply at **~45 KB**" (patch came back as its last 45 KB) | `scripts/pc_lane.sh:381-383`; `docs/INCIDENT-LOG.md:149` |
| "arm B v3: x0 [graft calls], **132 whole-file reads, 456 shell calls**"; `graft build` **4 s**, `ask` **1 s**, whole pack **4 s** | `harness-ports/bin/pc-lane.sh:195-198`, `:245` |
| "single-user 118–133 tok/s … **batch C64 ≈ 1,035 tok/s aggregate**"; the running config "**~45 tok/s single-request decode, near-linear to ~310 tok/s aggregate at 7 concurrent lanes**" | `docs/research/findings/VLLM-MIGRATION.md:32-33`, `:91-92` |
| nine-lane steady state: "**six refusals in 30 minutes across five of the nine lanes**… each a lost in-flight turn and a resume from the draft"; launch-burst: "TWO lanes … each lost one in-flight turn" | CLAUDE.md §SWARM (owner rulings 2026-09-08) |

---

## UNSURE / not found

- **`.honey-active` absent → the Bash compressor never fires in this container.** Probed once (2026-09-22, `ls /root/.claude/.honey-active`). Whether it is set in PC-side or other sessions: **not checked**.
- **No byte cap on Hermes `terminal` output** found anywhere in `harness-ports/` or `scripts/`. Absence read off targeted greps (`tail -`, `head -`, `MAX_`, `truncat`) over `pc-lane.sh` — not proven exhaustively; Hermes's own source is not in this tree. UNSURE.
- **The honey plugin's hooks.json is the vendored copy** (`sandbox-kit/honey-for-devs/hooks/hooks.json:23-33`). Whether Claude Code actually loaded it this session was not verified (the plugin is enabled in `/root/.claude/settings.json:86-88`; the hook registration path was not traced).
- **CLAUDE.md is stale on the wiki**: it states "`wiki-init` has NOT run yet … until `wiki/INDEX.md` exists the ledger is the only continuity source." `wiki/INDEX.md` EXISTS (probed 2026-09-22), so `wiki-context.py` is live, not silent. Recorded as a contradiction between two sources; not resolved.
- **`.claude/skills/contract-gate/SKILL.md` line numbers** for §5 come from a targeted grep (`:109-110`, `:173`), not a full read.
- **`docs/08_DECISION_LOG.md` D-031** was not opened this session; the D-031 disposition rule is cited from CLAUDE.md and the verifier role text that names it.
- **`.claude/skills/honey*` (14 skills) and the remaining ~460 skills' front matter** were not read — only `bug-echo`, `prism-scan`, `luck`, `contract-gate`, `anti-hollow-green` were inspected for decision rules. Other model-scored decisions may exist in unread skills.
- **Sandbox-side Agent dispatch transcripts** (how much of a delegate's report enters the coordinator context) — no instrument in-repo measures this; not found.

