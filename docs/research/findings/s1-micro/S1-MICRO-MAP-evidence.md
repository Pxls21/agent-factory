> **Coordinator's note (2026-10-02 07:5xZ).** The S1-MICRO-MAP lane's final message (task #467, step 1), whole, saved from its transcript by the harvest (run s-20261002T075349Z-36b3c1; the hand-back was absent, task #426). One edit: two local commit ids that the push rewrote are cited by what they are: the brief's commit by its origin id 851134bc, and the coordinator's retro commit as "the retro commit" (subject: "Retro: a CI quirk baked (an interpreter's error text can change inside one Python minor); task 460: the B1 re-check dispatched at 6c14466f"). Served model: one, on all 316 assistant records; 0 refusal stops. The design built on this evidence: `S1-MICRO-DESIGN.md` beside it.

# S1-MICRO-MAP evidence: where a System-1 micro-output could sit (task #467, step 1)

- **Lane.** Evidence-gatherer in the sandbox, Opus 5.5, read-only. The contract is `tasks/briefs/jev-laya/S1-MICRO-MAP-brief.md` (10-02, 851134bc).
- **Root.** Repo paths are relative to `/home/user/agent-factory`. Paths outside the repo are absolute.
- **Premise.** I re-ran the brief's premise block (brief L94-116) at 851134bc (the brief's commit, under its local id before the push), at 1ffee610 and at the retro commit. Every line matched each time. The PIN d2408a84 is an ancestor of HEAD.
- **HEAD drift.** One commit landed during the run: the retro commit, the coordinator's retro. It changed five files. Of the files this report cites, only the ledger changed: two lines were added after L1973. Every ledger line cited here is the same at both heads.
- **Dates.** A date is `git log -1 --format=%cs -- <file>` at the retro commit. All dates are in 2026 and are written MM-DD.
- **Marks.** SOLID means I read the line myself in this lane. UNSURE means one of two things:
  - the cell rests on a claim: a comment, a figure in a docstring, another agent's report, or a vendored skill;
  - or I could fill the cell only in part.
- **Counts I could not check.** The coordinator's tool-call counts come from transcripts I did not read. D-133 records the totals (decision log L144). The per-kind shares are in the brief, L29-47. I use them only to label the T4 rows.

---

## T1. System-1 decision points

**Where the hooks are registered:**
- The repo copy is `.claude/settings.json` (10-01).
- The live copy is `/home/user/.claude/settings.json`. It is untracked. `scripts/install_session_hooks.py` (10-01) writes it there because the session is rooted at /home/user (docstring L4-10, AF-AP-172).
- I compared the `hooks` key of the two copies. They hold the same 14 hooks, with the same matchers and timeouts; the live copy uses absolute paths.
- The live copy has one more hook: the stack catalog on SessionStart, matcher `startup|resume|compact`, timeout 30 (installer L96-99).

**Plugins enabled:** the `enabledPlugins` key of `/root/.claude/settings.json` (untracked) is:
`{"aegis@aegis-dev": true, "fast-jev-output-floor@agent-factory-vendor": true, "fast-jev-output@fast-jev-output": false, "honey@greenpt": true}`

**The wrapper:** `scripts/hook_context.py` (09-26) runs each child hook with `timeout=TIMEOUT_S`, which is 55 s (L42, L156). The comment on L42 says Claude Code's default hook timeout is 60 s. That is a claim; see C9.

### T1a. Built and wired into the harness

| id | Decision point (file:line, date) | Trigger | Input state | Output today | Consumer | Latency budget | In a gate or predicate? (KC-J1) | Mark |
|---|---|---|---|---|---|---|---|---|
| H1 | Situation to skill lines, by row match: `.claude/hooks/system1-context.py:531-602` (09-26), functions `match_rows` and `plan_tool`. Label text at L593: `[system1 · {id}] skill {skill}, the governing lines verbatim:`. Rows come from `.claude/hooks/system1-situations.json` (09-25): version 1, 40 rows, 10 skills. Detectors: `command`, `command_any`, `path`, `path_not`, `text`. | PreToolUse `Write\|Edit\|Bash` (settings L142-149), through the wrapper | The tool name and its fields (`tool_fields` L382-389) | The matched skill's lines, verbatim, at most 2,048 bytes (TOOL_BUDGET, L63-81) | The acting model | No `timeout` key; the wrapper's 55 s | Advisory: every path exits 0 (docstring L1-51). Not listed in `scripts/gate_files.txt` (09-24). | SOLID |
| H2 | Prompt to skill sections, by lexical rank: `system1-context.py:749-800` (`rank_prompt`) and `:803-863` (`plan_prompt`; the choice at L822, the label at L841). Thresholds at L63-81: MIN_PROMPT_SCORE 70, ONE_LEAD_MIN_SCORE 80, SHORT_MIN_SCORE 30, MIN_COVER 0.2, NAMED_MIN_SCORE 40, SECOND_EXCERPT_RATIO 0.75, LEAD_MIN_IDF 2.0. | UserPromptSubmit (settings L87-91), through the wrapper | The first 4,000 characters of the prompt | At most 2 excerpts, at most 4,096 bytes | Model | The wrapper's 55 s. The docstring (L43-48) says: warm prompt plan 23 ms median, 36 ms p95; whole process 64 ms and 90 ms. | Advisory, exits 0 | SOLID; the figures are UNSURE (docstring) |
| H3 | Search intercept and quirk guard: `.claude/hooks/search-intercept.py:1165-1202` (09-25), function `decide`. Three paths: (a) semantic search, through `bash_search` L740-773, `nag_says_semantic` L819-835, `semantic_scope` L845-863 and `answer_search` L1099-1110; (b) the quirk rules, QUIRK_RULES L574-600, with the false-positive table at L601-604 and SHIPPED at L605; (c) an identical repeat within 120 s passes (WINDOW_S L55). | PreToolUse `Grep\|Bash` (settings L133-140), through the wrapper | The command or the Grep pattern | Exit 2 with the graft or rg answer (at most 8,800 characters, L64) or with the quirk's recipe; otherwise the call passes | Model | HOOK_BUDGET_S 45: "the whole hook (hook_context.py allows 55 s, Claude Code 60 s)" (L58). GRAFT_TIMEOUT_S 20 (L57), RG_TIMEOUT_S 10 (L59). A command that matches nothing: 33.5 ms median (comment L48-50). | Blocks a tool call (exit 2) by fixed rules. Not listed in gate_files.txt. | SOLID; 33.5 ms is UNSURE |
| H3j | Jev reorder inside H3: `search-intercept.py:981-1006` (`jev_reorder`). Fixed question at L997: "Where is %s defined, and which lines show how it is used?" | Runs inside H3, only while `.jev/intercept-jev-rank-on` exists (docstring L2-40; I did not read `.jev/`) and the answer has more than 12 hits (RANK_ABOVE L61) | The pattern and its hits | A new order of the hits shown; no hit is removed | Model | RANK_TIMEOUT_S 20; "about 0.45 s per hit on the local CPU server" (L62) | Orders the answer of a blocking hook; it does not decide the block. The docstring says J2 measured it right-first 5% of the time. | SOLID; the switch state is unknown |
| H4 | Nag on a bare-identifier Grep: `.claude/hooks/graft-first-nag.py:31, 40-47` (09-15) | Registered in neither settings copy. H3 uses its classifier in-process (L819-835). Hermes maps it to `post_tool_call` with 20 s (`harness-ports/hermes/config-snippet.yaml:162-164`, 09-15). | The Grep pattern | A nag line; it never blocks | Model | 20 s on Hermes | No | SOLID; the Hermes row is UNSURE (snippet L17-21: "NOT SMOKE-TESTED") |
| H5 | Edit and Read screens: `.claude/hooks/edit-snapshot.py:617-693` (09-25). AP_SCREEN starts at L132 (about 66 rows, by a grep count). TEST_SCREEN at L409. Probes: `pyflakes_delta` L509-537, `enclosing_symbols` L550-571, `chronology` L574-585, `gitnexus_impact` L599-614. Acts on `.py` files only (L625). | PostToolUse `Edit\|Write\|Read` (settings L66-75), through the wrapper | The file, the hunk, the enclosing symbols | On Read: READ CONTEXT (L644-651). On Edit: the tells, "TELLS, not verdicts" (L686-690). | Model | The wrapper's 55 s. Each probe has PROBE_TIMEOUT 8 s, and at most 2 symbols are probed (L482-483). | Listed as a gate-defining file (`scripts/gate_files.txt:54`), but it always exits 0 (docstring L2-15) | SOLID |
| H6 | File packs and code-map lines: `scripts/filepacks.py:885-927` (09-30), the hook. `targets` L464-473, `plan` L754-804, `entry` L711-741, `render` L590-602. The code part comes from a `scripts/codemap.py` pack (L2b; filepacks docstring L25; codemap.py:5, 09-30). | PreToolUse `Read\|Edit\|Write\|Bash` (settings L151-158), through the wrapper. Also SessionStart `hook --reset` (L49-53). | The paths the call touches | "codemap …" and "filepack … ledger N · briefs N …" lines. PACK_BUDGET 1,200 and CALL_MAX 2 (L107-108). | Model | No timeout key; the wrapper's 55 s; HEAD_TIMEOUT 2 (L124). The smoke run in ledger L1888 measured a Read at 106 ms, an Edit at 90 ms and the reset at 49 ms. | Advisory; off switch `filepacks-off` (docstring L1-91) | SOLID |
| H7 | Wiki excerpts: `.claude/hooks/wiki-context.py:102-120` (09-24). Candidates at L102-105. Score = headings ×3, file stem ×2, text ×0.1 (L115-120). MAX_PAGES 3, EXCERPT_LINES 12 (L20-21). The line "MAP, not gospel" is at L138. | UserPromptSubmit (settings L79-83), through the wrapper | The prompt | At most 3 wiki excerpts | Model | The wrapper's 55 s | No | SOLID |
| H8 | Session-start pack: `.claude/hooks/session-start.sh` (09-25). Resets the window at L15-17, runs setup at L36, adds the live-state block at L44-48, cuts orient to 3,000 characters at L51-54 and cuts the whole to 9,000 at L56. The stack catalog hook exists only in the live copy (`scripts/stack.py:1196-1218`, 09-29). | SessionStart (settings L33-35, no timeout). The catalog hook has a 30 s timeout. | The tree | A fixed composition; nothing is ranked | Model | None set; the catalog has 30 s | No | SOLID |
| H9 | Turn retro gate: `.claude/hooks/turn-retro-gate.sh` (09-30). Fires once per HEAD (L13-17). Exemptions at L18-57. Defers while `ls_req.py defer-check` says so (L62-66, timeout 20). Prints the six-item checklist and exits 2 (L75-84); item 6 asks about labels (L82). | Stop (settings L106-110, no timeout) | HEAD, the tree, the ls_req state | Exit 2 with the checklist; the model answers it | Model | defer-check has 20 s | Blocks the stop on fixed conditions. Not listed in gate_files.txt. | SOLID |
| H10 | Task view: `scripts/task_sync.py` (09-28). EVENTS L87, EVENT_RE L100, `extract` L375, `build_view` L427, `main` L791. | SessionStart and Stop (settings L41-44, L114-118), timeout 30 | The ledger's headlines and its `## 1b.` overrides | The harness task list | Model and owner | 30 s | No | SOLID |
| H11 | Request boxes: `scripts/ls_req.py` (09-29). Grammar at L25-75 (REQ L25-39, box L41-75). `parse_box` L538-587, `parse_message` L590-663, nonce L116-121. `run_request` L826-869: exit 0 or 1 means it ran, 2 means refused, 3 means a runner error. `cmd_stop` L1174-1369. | SessionStart, UserPromptSubmit and Stop (settings L57-61, L95-99, L122-128); timeouts 30, 30 and 300 | The model's final message | RES receipts (L77-84) and each stack's output (FEEDBACK_CAP 9,500, L166) | Model | 300 s at Stop; ROUND_BUDGET_S 240 (L161) | Runs registry labels only. A box never carries a shell command (`.claude/skills/box-and-labels/SKILL.md:83-84`). | SOLID |
| H12 | Injection stamp and score request: `scripts/hook_context.py` (09-26). `stamp` L71-74, REQUEST L56-58, `stamped` L127-145 (off switch `s1-rate-off` at L131). `log` L103-124 writes `<state>/injections.jsonl`. STAMP_MAX_CHARS 9,500 (L45). Exits 2 when it stamps text on Pre- or PostToolUse (L164-165). | Wraps H1-H3 and H5-H7 | The child hook's text | The stamped text and the S1-RATE request | Model; `scripts/s1_scores.py` | 55 s | No. It is the feedback seam, not a decision. | SOLID |
| H13 | Honey plugin hooks: `sandbox-kit/honey-for-devs/hooks/hooks.json:3-33` (09-03): SessionStart `honey-session.js`, SubagentStart `honey-subagent.js`, PostToolUse Bash `logcompress-hook.js` (09-03). The last one loads its implementation on Node 14 or later (L10-11). | Plugin hooks; `honey@greenpt` is enabled at user scope | The Bash output | A compressed log (I did not read the implementation) | Model | No timeout key in hooks.json | Unknown | UNSURE |
| H14 | Output pruner: `vendor/jev-pruner/hooks/fast-jev-output.ts:188-366` (10-01), the `register` function. `goalFromMessages` L136-147. `recentMessages` L156-162. The Jev request uses `{ timeoutMs: 8_000 }` (L312). Decision records at L347-363. In `src/output.ts` (09-25): `exceedsOutputThreshold` L86-89, `classifyOutput` L132-143, OUTPUT_CONTEXT L16-17, `recoveryFooter` L265-267. In `src/retention.ts:54-56` (09-25), keepScore keeps a chunk when its score ≥ the threshold or > 0.1. The plugin is `fast-jev-output-floor` 0.1.1 (`.claude-plugin/plugin.json`, 10-01). Its upstream is tamaratran/jev-pruner @ 47d017c (`harness-ports/bin/jev-pruner-setup.sh:2-9`, 09-23). | Plugin module (`vendor/jev-pruner/hooks/hooks.json`, 09-25) on `tool.call` Bash; enabled at user scope | The Bash output past the floor. The goal is the last 3 user prompts, each at most 500 characters. Also the recent history. | The output with chunks dropped, a footer that names the archive, and a decision record | Model | 8 s per scoring request (L312); maxScoringRequests 11 (plugin.json default) | Not a gate. It removes text the model would see. | SOLID for the code. The live state is UNSURE: orient at this session's start said "on, floor 1000 tokens, to http://127.0.0.1:47430/v1/systemone … today past the floor: 93 (document 55, few_chunks 23, kept_all 13, pruned 2)". |
| H15 | Aegis plugin (`aegis@aegis-dev`, enabled at user scope) | SessionStart | — | A fixed "using-aegis hot path" text, seen in this session's start context | Model | Unknown | Unknown | UNSURE (not in the repo; I did not read it) |

### T1b. Built, run on demand

| id | Decision point (file:line, date) | Input | Output | Notes and limits | Mark |
|---|---|---|---|---|---|
| J1 | Jev client: `scripts/jev.py` (09-25). API at L465-478. Fixed instructions: RANK at L76, "Does this chunk answer, match or explain the query?"; CLASSIFY at L77, "Which label fits this text best?". `_question` L139-151 builds noul, choice or score questions. `_check_answer` L194-212. | Chunks and a query, or a text and labels | Probabilities | DEFAULT_TIMEOUT 30 s; MAX_CHUNKS 64. Fails open with exit 3. Tries :47411 first, then the PC (docstring L2-36). Gate files may not import it. `scripts/no_laya_in_gates.py` (09-24) screens the gate files and does not follow exec edges (L28-37). | SOLID |
| J2 | `scripts/jev_context.py` (09-30): `jev_rank` over at most 48 chunks, on the local endpoint only (L2-28) | Chunks | An order | Used by J3 and J4 | SOLID |
| J3 | `scripts/chat_find.py --order jev` (09-25) reorders the top N hits, N at most 48 (L30-32). JEV_WINDOW 600 (L75). The default is lexical. | A query and excerpts | An order | The `find` label runs it with `--order lexical --no-jev-log` (`scripts/stacks.toml:350-357`, 09-30) | SOLID |
| J4 | `scripts/jev_locate.py` (09-25): `--order jev` is opt-in (L2-20) | A bug text and the instrument hits | An order | The `locate` label runs it lexical (stacks.toml L679-680). `tests/test_stack.py:2557-2561` (09-30) pins that. | SOLID |
| J5 | `scripts/jev_echo.py` (09-30). Its Jev question: "Does this code show the same defect as the one fixed?". Lexical by default (L2-18). | The removed and added hunks, plus candidate sites | An order | The `fix-echo` label runs it lexical (stacks.toml L716-736; the same test pin) | SOLID |
| J6 | `scripts/hiccup_scan.py --jev` (09-25): for each UNCOVERED cluster, `jev.rank` over 8 candidates (L21-28) | The cluster's text | One advisory column (JEV_HEAD L72) | "No model runs unless --jev is given" (L10) | SOLID |
| J7 | Servers and transport. `scripts/laya_systemone_server.py` (09-25) listens on :47411 (L244) and accepts the types noul, choice and score only (L219-220). `scripts/qwen_jev.py` (09-25) listens on :47420 (L68). `scripts/jev_relay.py` (09-30) is the scrubbing relay on :47430 (L2-35). `scripts/jev_local.sh` (09-24, L1-23). `scripts/jev_relay_up.sh` (09-30, L1-33). `scripts/jev_liveness.py` (10-01, L2-16) feeds orient (`scripts/orient.sh:24-25`, 10-01). | — | — | Orient at this session's start: the relay is up; laya :47411 and qwen :47420 are down | SOLID for the code; the liveness is UNSURE (one reading) |
| J8 | SYNTH1 labeler: `scripts/s1_synth.py` (09-26). A teacher model answers ONE line, `rel=<0-3> use=<0-3> <reason>` (L45-46). ANSWER_RX (L158) parses it; the reason is at most 120 characters (REASON_MAX L157). The questions are skill.governs and skill.helps (L154). | A pair: a step or prompt, and a skill section | A label line | Batch use only; not a gate | SOLID |
| J9 | `scripts/decide-harvest` (09-25): 7 question ids at L25-33, according to LS-AUDIT §1.5 (L182) | — | — | I did not re-read it | UNSURE |
| J10 | `scripts/jev_pipes/replay_pruner.py` (09-25). P1 replays the pruner's own `trimOutput` through `bridge.mjs` (10-01). The bar: misses at or under 5% and net tokens above zero (L2-14). `accounting.py` (09-25) defines a miss (L3-8). | Recorded tool results | PASS or FAIL | `__init__.py:5`: "Advisory: nothing here is a gate" | SOLID |
| J11 | `scripts/jev_trim/replay.py` (09-29), T0 for D-105: replays the trim policy with "no model deciding anything" (L2-14). `compaction.py` (09-29) "measures and recommends nothing" (L9-13). | Transcripts | Counts | Measurement only | SOLID |

### T1c. Planned or registered

| id | What (file:line, date) | State, latency and status | Mark |
|---|---|---|---|
| P1 | `s1.inject`, a noul question: `scripts/laya_ft/common.py:55-58` (10-01). Its text: "Is the context in `chunk` relevant to the agent's next step in `step` (the agent's own words in `intent`, the person's task in `task`)?" | **State:** task, intent, step, kind, chunk (`tasks/laya-s3-breakdown.md:43-51`, 10-01).<br>**Label:** yes when rel is 2 or 3; every injection kind takes it (L52-57).<br>**Data (breakdown L38):** 1,093 scored; train 851 (512 yes); held-out 220 (147 yes); always-yes 0.668; kind rule 0.809. The word-overlap baseline is at `scripts/laya_ft/build_s1.py:289-297` (10-01).<br>**Latency:** on the 3090, a question from a copied state takes 0.04 s (breakdown L39). On the CPU, "the time of one decision through llama.cpp is not measured" (RWKV-CPU L221-222). | SOLID, as a plan |
| P2 | #441, backlog (ledger L1895): the first training on the S1 data, with pre-registered baselines (always-yes, the source-kind prior, word overlap), in a GPU window the owner approves (D-078 (1)) | The model: a frozen RWKV-7 with contrastive heads (CLM, two MLP heads, InfoNCE; breakdown L66) | SOLID |
| P3 | #448, backlog (L1911): RWKV-7's live home on the CPU | "Serving a head in the System-1 hook" is NOT built (breakdown L80-86) | SOLID |
| P4 | #453, backlog (L1921): per-role RWKV states (D-127 item 2, decision log L138) | — | SOLID |
| P5 | #467, in progress. Sources: D-133 (decision log L144); ledger L1965, L1969 and L1971. | **The output:** a label from `scripts/stacks.toml` plus "slots that point at things already in the stream, which deterministic code expands … a closed grammar, checked by deterministic code before anything runs, and never inside a gate (KC-J1)".<br>**Hybrid:** "a few generated tokens are spent only when a label's form has a free slot that no reference can fill".<br>**Budget:** the owner's "forty [milliseconds]". The decision adds "about 21 ms a token, so a 40 ms budget holds about two generated tokens there". | SOLID, as decided |
| P6 | #409 (L1867): "code shortlists the skills and a Jev picks from the shortlist … a fail-open second stage after rank_prompt in .claude/hooks/system1-context.py, measured by the S1-RATE scores" | Backlog | SOLID |
| P7 | #410 (L1867): report digests. A Jev scores each finding of a landing report. | Backlog | SOLID |
| P8 | #413 (L1867): the done check. "A Jev reads the actual state (the changed files, the last gate's result) and code confirms the files exist … advisory, never a gate" | Backlog | SOLID |
| P9 | #340, pending (L1678): Read narrowing, ported from BorisLeMeec/jev's Read hook (e81c1d0). Its rules: a 400-line floor; only when the Read has no offset or limit; one request per file; a 0.60 confidence floor; a window of a fifth of the file and at least 150 lines. | Pending | SOLID |
| P10 | #290 (L1595): an L2b situation row that asks before a command that can fill the disk or take a shared resource | Backlog | SOLID |
| P11 | #351 (L1714) and #381 (L1792): a guard against a top-level `cd` | Backlog | SOLID |
| P12 | #391 (L1823): Jev-powered labels, "an ADVISORY class of stacks" | `.claude/skills/label-authoring/SKILL.md:77-86` (09-30) lists it as ruled in, not built; see also L83 | SOLID |
| P13 | #392 (L1824): per-agent label sets | Backlog | SOLID |
| P14 | #430, #431 and #432 (L1890): a Jev compaction summary (D-123 item 3); a hypercontext map rendered by our own script (item 4); max-relevance examples that a subagent writes for each rated injection (item 2) | Backlog | SOLID |
| P15 | #346 (landed L1728) and #352 (home L1744): trimming and the compaction point | Replay and measurement only (J11) | SOLID |
| P16 | #406 (running; L1865, L1870): the pruner's first live Jev decision, with a per-call token cap, a daily budget, a decision log and a miss count. #436 (running; L1893, L1903): the pruner's history window. | Running | SOLID |
| P17 | #412 (L1867): the Jev budget. #411 (L1867): a lint for Jev questions. | These constrain callers; they are not decisions | SOLID |
| P18 | D-102 (decision log L113): a Jev classifier for task status, later | — | SOLID |
| P19 | `scripts/ls_req.py:23-24` (09-29): "a trained model may later replace this lexical parser, reading the same lines" | — | SOLID |
| P20 | The leverage audit, `docs/research/findings/JEV-LEVERAGE-AUDIT-2026-09-24.md` (09-24). | **§5 (L76-80):**<br>- a new `ap-hawk.py`: a lexical top-16 of 137 rows with no screen, then a Jev choice, the top 3 shown as "suggested, unverified";<br>- a shadow rerank in wiki-context;<br>- nothing yet for turn-retro-gate;<br>- session-start to rank open tasks and ledger lines later;<br>- the pruner.<br>**§7 (L104-109):**<br>- the registry row a change resembles (121 labels);<br>- the class of a verify finding (111 labels);<br>- the wiki section to read (no labels);<br>- the class of an error event (no labels);<br>- the shape of a lane report (regex works);<br>- tier and breadth routing (deferred).<br>**§2 (L37-38):** E3 counted 70 decision points, 28 of them model judgment in skills. | UNSURE: an audit; I did not re-count |
| P21 | #295, S1-RATE (landed L1626). #318, S1-RATE-R1 (pending, L1638). | — | SOLID |

### T1d. LS-AUDIT's decision families F1-F46

- **Source.** `tasks/briefs/labeling/LS-AUDIT-report.md:131-176` (09-28). Family Fn is on line 130+n.
- **Mark.** UNSURE: this is another agent's inventory, and I did not re-verify it.
- **Label classes (L127).** D1 is a harness field, D2 a fixed tool line, D3 a committed rule, D4 the actor's own choice, D5 human text.

| F | Family | Status as filed | F | Family | Status as filed |
|---|---|---|---|---|---|
| F1 | Bash exit class ("doomed call") | seam exists; advisory PROPOSED | F24 | Verify recommendation | no seam |
| F2 | Sleep-first block | harness rule | F25 | Finding class and blocking | capture and trainer BUILT; no model accepted |
| F3 | Tool denial | no seam | F26 | Repair round | the contract gate |
| F4 | Will an Edit or Write apply; Read first? | no hook | F27 | One model served the dispatch | counted by hiccup_scan |
| F5 | Redundant Read | a rule | F28 | Refusal | none |
| F6 | Test outcome, loop nudge | rule PROPOSED | F29 | Bug-echo | the skill; B4 |
| F7 | Error family | BUILT, deterministic (hiccup_scan) | F30 | Factory tool-call advisory | PROPOSED; never pre_tool_call |
| F8 | AP-hawk | regex screen LIVE; Jev hawk NOT built (#115) | F31 | Drift hawk | NOT built (#116) |
| F9 | Output pruning | B7 (failed at the 2k floor then) | F32 | Dream triage | Stage 5, NOT built |
| F10 | File changed outside the model | no model needed | F33 | Turn-end tags | PROPOSED |
| F11 | Stop git check | A2 rule PROPOSED | F34 | Recall order | an FTS5 rule today |
| F12 | Retro answer, bake target | gate LIVE; Laya hint PROPOSED | F35 | Hit role, finding severity | capture types only |
| F13 | Context per prompt | lexical LIVE; Laya NOT built (#297) | F36 | Search prefetch | PROPOSED |
| F14 | Situation to lines | LIVE; ranking when several rows match NOT built | F37 | Report digests | PROPOSED (#410) |
| F15 | The owner's answer | no seam | F38 | Wake filter | PROPOSED |
| F16 | Files needed after a compaction | pack LIVE; ranker PROPOSED | F39 | Finding dedup across rounds | PROPOSED |
| F17 | Commit gate outcome | gates LIVE | F40 | Report claim check | report_lint LIVE; Laya PROPOSED |
| F18 | Push and CI-gate outcome | gates LIVE | F41 | Lane rules with no model | PROPOSED |
| F19 | Will CI pass | rule PROPOSED | F42 | Read narrowing | NOT built (#340) |
| F20 | Background command outcome | none | F43 | Labeled output blocks `book` and `ask` | NOT built |
| F21 | Dispatch outcome | "not a lever at dispatch" | F44 | Menial bookkeeping | the coordinator today; stamps are scripted |
| F22 | PC lane end, stuck or progress | recorder OFF | F45 | RF2-only items | not built |
| F23 | Agent type, tier and effort routing | the CLAUDE.md table; deferred | F46 | Jev codebase explorer | not designed |

Two cells have changed since 09-28: see C4 and C5.

---

## T2. Free-text slots per T1 row

Classes: (a) a closed set, (b) a reference to something an earlier event names, (c) free text.

| T1 | Slot | Today | Example from the code or docs (file:line, date) | Class |
|---|---|---|---|---|
| H1 | Which lines to show | Hard-coded per row (the `lines` key) | The situation keys `command`, `command_any`, `path`, `path_not`, `text`, `lines` (system1-situations.json, 09-25) | No free slot |
| H2 | Which excerpt | Derived by lexical rank | Thresholds at system1-context.py:63-81 (09-26) | (a), over the candidates |
| H3 | The graft question | Hard-coded: the raw grep pattern becomes the question | `search-intercept.py:1104` (09-25): `gargs = [graft, "ask", spec["pattern"], "-n", "5"]` | (c), filled by copy |
| H3j | The Jev question | A template filled with the pattern | L997: "Where is %s defined, and which lines show how it is used?" | (c), with a (b) fill |
| H5 | Which registry row a hunk resembles | Hand-written regex rows | AP_SCREEN at edit-snapshot.py:132 (09-25) | (a), row ids |
| H9 | The six checklist answers | Typed by hand by the model | turn-retro-gate.sh:75-84 (09-30); item 6 asks which labels (L82) | (c); the label names are (a) |
| H10 | The event word and the task id | Typed by hand in ledger headlines | CLAUDE.md task tracking: `TASK #N REGISTERED`, `DISPATCHED`, `HOME`, `LANDED`, `CLOSED`; EVENTS at task_sync.py:87 (09-28) | (a) and (b) |
| H11 | Label, request id, nonce, parameters, body | Typed by hand | ls_req.py:216-221 (09-29): `┌─ find · r1 · {n}` / `│ q: who calls parse_message` / `└─`. The body is one line of at most 500 characters (L58-59). | Label (a); nonce (b); parameters as in T3; body (c) |
| H12 | The S1-RATE line | Typed by hand by the model | hook_context.py:55 (09-26): `S1-RATE (s1-[0-9a-f]{8}) rel=([0-3]) use=([0-3])(?: (\S.{0,%d}))?`, where %d is NOTE_MAX − 1 = 119 | id (b); rel and use (a); note (c), at most 120 characters |
| H14 | The goal | Derived by code | fast-jev-output.ts:136-147 (10-01): the last 3 user prompts, each at most 500 characters | (c), derived |
| H14 | The instruction text | Hard-coded | output.ts:16-17 (09-25), OUTPUT_CONTEXT | — |
| J1 | The query and the labels | Supplied by the caller; the instructions are fixed | jev.py:76-77 (09-25) | (c); (a) |
| J3 | The description | Typed by hand | chat_find.py:4 (09-25): `usage: chat_find.py "<description or error text>"` | (c) |
| J4 | The bug text | Typed by hand | `locate q=` (stacks.toml:693-695, 09-30) | (c) |
| J5 | The defect | A diff file | `fix-echo diff=` (stacks.toml:726-728) | (b) |
| J6 | The query | Derived from the cluster's text | hiccup_scan.py:21-28 (09-25) | (b), derived |
| J8 | The reason | Generated by a teacher model and checked by a regex | s1_synth.py:45-46 and :157-158 (09-26) | rel and use (a); reason (c), at most 120 characters |
| P1 | `intent` | Derived from the stream: "the agent's own words" | common.py:56-57 (10-01) | (b) |
| P5 | A label and its slots | Missing (not built) | D-133 (decision log L144) | (a) and (b); (c) only "when a label's form has a free slot that no reference can fill" |
| P6 | The skill pick | Missing | #409 (L1867) | (a), from the shortlist |
| P8 | The state behind a done claim | Missing | #413 (L1867): the changed files and the last gate's result | (b) |
| P9 | The line window and a confidence | Missing | #340 (L1678): a window of a fifth of the file, at least 150 lines, a 0.60 floor | A bounded number |
| P14 | The compaction summary; the max-relevance example text | Missing | #430 and #432 (L1890) | (c) |
| P19 | REQ and box lines | Typed by hand, as in H11 | ls_req.py:23-24 | As in H11 |

Other places where values are typed by hand today, as named in code or in CLAUDE.md:

| Slot | Example (file:line, date) | Class |
|---|---|---|
| Commit message | `scripts/safe_commit.sh -m "<msg>" <path>…` (CLAUDE.md; safe_commit.sh:2-7, 09-25) | (c); the paths are (b) |
| Stamp | The `{STAMP}` and `{DATESTAMP}` tokens are filled from the clock (stamp.sh:6-7, 09-25; stamp_fill.py:2-14, 09-25) | Derived by code |
| Lane id | `harvest agent=<agent>`, where the agent type is `a[0-9a-f]{16}` (stacks.toml:41-43; stack.py:81-84) | (b) |
| Lane dispatch | `scripts/pc_lane.sh <brief-file> [codex\|hermes] [role]` (pc_lane.sh:5, 09-29) | (b), (a), (a) |
| A command on the PC | `scripts/pc.sh '<command>'` (pc.sh:3, 09-24) | (c), a shell command |
| CI wait | `python3 scripts/ci_gate.py --branch <branch> --wait 1800` (CLAUDE.md) | (b) and an int |
| The owner's rulings | `python3 scripts/owner_rulings.py <topic words>` (CLAUDE.md) | (c) |

---

## T3. The label registry

- **Source.** I parsed `scripts/stacks.toml` (09-30) with tomllib: 14 stacks and 27 parameters. The value checks are in `scripts/stack.py` (09-29).
- **Class.** It is my reading of each parameter's role, against the brief's definitions. The basis is given where it is not plain.

### T3a. Parameters

| Label (lines) | Parameter | Declared type | Required or default | Class | Basis | Line |
|---|---|---|---|---|---|---|
| harvest (L32-108) | agent | agent `a[0-9a-f]{16}` | required | (b) | The id the harness returned at dispatch | L41-43 |
| harvest | report | path | — | (b) | A file the lane wrote | L45-46 |
| gate (L111-250) | paths | paths | required | (b) | The changed files | L121-123 |
| gate | mode | choice: plan, run | plan | (a) | | L125-128 |
| gate | runs | choice: 1, 2 | 2 | (a) | | L130-133 |
| gate | graph | choice: yes, no | yes | (a) | | L135-138 |
| gate | max_files | int `[0-9]{1,6}` | 40 | bounded int | | L141-143 |
| ctx (L253-278) | files | paths | required | (b) | | L261-263 |
| ctx | q | text (the body) | — | (c) | | L265-266 |
| ctx | sym | symbols | — | (b) | | L268-269 |
| impact (L281-317) | sym | symbol | required | (b) | | L287-289 |
| find (L320-366) | q | text (the body) | required | (c) | | L327-329 |
| find | words | words, split from q | derived | derived | | L331-333 |
| premise (L369-406) | files | paths | required | (b) | | L374-376 |
| echo (L409-456) | pattern | text (the body) | required | (c) | | L416-418 |
| echo | roots | paths | `scripts,harness-ports,src,proofs,.claude/hooks,.github` | (b) | A list of paths with a fixed default | L420-422 |
| review (L460-516) | files | paths | — | (b) | | L470-471 |
| review | mode | choice: check, save, compare | check | (a) | | L473-476 |
| ci (L519-535) | branch | text | `{branch}` | (b) | A branch. It is text, not word, because a branch name can hold '/' (L524). | L525-527 |
| cbm (L548-566) | q | text (the body) | required | (c) | | L555-557 |
| changes (L580-640) | scope | choice: all, staged, unstaged, compare | all | (a) | | L586-589 |
| changes | base | text | — | (b) | A git ref; the text type refuses a leading '-' (L591-593) | L594-595 |
| why (L649-676) | file | path | required | (b) | | L655-657 |
| why | fn | symbol | — | (b) | | L659-660 |
| locate (L686-705) | q | text (the body) | required | (c) | | L693-695 |
| locate | scope | path | — | (b) | | L698-699 |
| fix-echo (L716-736) | diff | path | required | (b) | "a path, not text" (L723-725) | L726-728 |

### T3b. Counts

- **By class.**
  - (a): 5 (gate.mode, gate.runs, gate.graph, review.mode, changes.scope).
  - Bounded int: 1 (gate.max_files).
  - (b): 15.
  - (c): 5 (ctx.q, find.q, echo.pattern, cbm.q, locate.q).
  - Derived: 1 (find.words).
  - Total: 27.
- **By declared type.**
  - text: 7, which is the five (c) bodies plus ci.branch and changes.base.
  - paths 5, path 4, choice 5, symbol 2.
  - symbols 1, agent 1, int 1, words 1.
- **Required or not.**
  - Required: 11.
  - With a default: 8.
  - Optional, with no default: 7.
  - Derived: 1.
- **Bodies.** The body parameters are exactly the five (c) parameters.
- **Ratings.** 9 of the 14 stacks are rated: ctx, impact, find, echo, review, cbm, why, locate and fix-echo.

### T3c. What the notes and docs say a label cannot take

1. **A bad text value.** A text value must be 1 to 500 characters. It cannot hold a NUL or a newline, and it cannot start with '-' (`check_scalar`, stack.py:491-508; TEXT_MAX at L74).
2. **A value outside its pattern.** symbol, word, agent and int values must fully match VALUE_RE (stack.py:81-84). A choice must be one of its listed values.
3. **A bad path.** A path cannot be empty, start with '-', or hold a NUL or a newline. It cannot match the deny list or lie outside the tree (`check_path` L462-488; the deny lists at L113-118).
4. **A literal brace.** No argv element may hold one (stacks.toml:8-9).
5. **Shell syntax.** No pipe, `&&` or redirection: argv words only (`.claude/skills/label-authoring/SKILL.md:25`, 09-30). stack.py runs argv only, never a shell (L18). Every parameter check runs before any step (L17).
6. **A long or split body.** A body is one line of at most 500 characters (box-and-labels SKILL.md:23-24, 09-30; ls_req.py:58-59). Each value is one argv element, never a shell word (ls_req.py:54-55). The value is one argument (box-and-labels:66).
7. **A shell command or a script inside a box** (box-and-labels:83-84; D-111).
8. **An outward action.** `outward = true` is refused at load (stack.py:355-356; stacks.toml:20-21). Labels are read-only and inward (label-authoring:68-75).
9. **A tool that writes or leaves the machine.** "Tools that write or leave the machine (commit, push, the PC bridge) stay out of boxes by design" (D-113 item 2, decision log L124).
10. **A model call** (stacks.toml:20-21; label-authoring:72-73 and :83; box-and-labels:88). See C1 for how this is enforced.
11. **A positional argument from `{fn?:FLAG}`.** That form cannot write one, so `why` has two steps (stacks.toml:642-648).
12. **A body parameter that cannot be set** (stack.py:377-380).
13. **Limits from the notes.**
    - `gate mode=run` refuses more than max_files (40) (stacks.toml:115-119).
    - `gate graph=no` is for a deleted path or a missing ripwire (F-18) (stacks.toml:115-119).
    - `gate runs=2` re-runs the pytest files only (stacks.toml:115-119).
    - `ctx` does not show a missing ripwire as unmapped (F-6, L258).
    - `review mode=save` overwrites the shared baseline (F-5, L465-468).
    - `changes` covers indexed symbols only (L584).
    - `fix-echo` reads unmapped when no instrument answered (L721).
14. **Limits from the ledger.** `gate paths=` splits on commas only (#445, L1905). `echo` has no literal mode (#435, L1892).

---

## T4. Command kinds no label covers

The shares are the coordinator's (brief L29-47), and I could not check them (UNSURE). The script rows are SOLID.

| Kind (share) | Label today | Closest scripts (usage line, date) | Slot values the scripts or the command form take (class) |
|---|---|---|---|
| other (27.0%: "compound commands no rule below caught", brief L34) | Unknown | No breakdown seen | Unknown |
| read: sed -n, head, tail, cat (14.9%) | None. `premise` gives only tracked status, sha256, line count and last commit (stacks.toml:369-406). | Nothing in scripts/. #340 Read narrowing is pending (L1678). | A path (b); a line range, start and count (a bounded int, often (b): a line an earlier event named) |
| tests (11.9%) | `gate mode=run`, in part | `test_summary.sh:3` `[pytest paths...]` (09-29); `lane_gate.sh:7` `-r <rev> -f "<lane file>…" -t "<pytest path>…" [-n RUNS] [-o OUTDIR] [-d "<deleted file>…"]` (09-24); `pc_suite.sh:8` `launch [-n <workers>] [-- <pytest paths/args>]` (09-15); `gate_union.py:6-8` `--graph yes\|no … [--mode plan\|run] [--max-files N] PATH...` (09-28) | Test paths (b); a rev (b); runs and workers (bounded int); a node id (b) or a `-k` expression (c) |
| search (11.5%) | echo, find, cbm, locate, in part | The four labels; #435 (a literal mode for echo); `lane_context.sh:12` `[-q "<question>"] [-s SYMBOL]... [-o out.md] FILE...` (09-15) | A pattern (c), or a literal token an earlier event named (b); roots or scope (b); flags (a) |
| PC bridge (8.6%) | None, by design (D-113 item 2) | `pc.sh:3` `'<command>'` (09-24); `pc_lane.sh:5` `<brief-file> [codex\|hermes] [role]` (09-29); `pc_suite.sh:8` `launch\|wait` (09-15); `ship_to_pc.py:5` `<export dir> <remote dir>` (09-25); `gpu_window.sh:2-8` (09-24; it runs on the PC) | A shell command (c); a brief path (b); a runtime and a role (a); a run id (b) |
| echo, date, printf (5.8%) | None | `stamp.sh:2-8` `[-b]` (09-25); `stamp_fill.py:12` `FILE...` (09-25) | A mode (a); files (b) |
| git (5.6%) | changes, premise and why cover the read-only part | `safe_commit.sh:2-7` `-m "<msg>" <path>…` (09-25); `push_clean.sh:2-9`, `--no-delegates-live` or `--lanes-live` (09-25); `ci_gate.py:2-10` (09-23); `why.sh:9` `<file> [function_name]` (09-03); `stale_ids.py:2-10` (09-24) | A message (c); paths (b); a flag (a); a branch (b) |
| write a file: cat >, tee, sed -i (5.1%) | None; labels are read-only (label-authoring:68-75; #399 pending, L1839) | `anchor_edit.py:2-8` (09-25); `stamp_fill.py` | A file (b); an anchor text that must match exactly once (b); the replacement (c) |
| list and size: ls, wc, stat, du (5.0%) | `premise`, in part | — | Paths (b); flags (a) |
| another repo script (1.6%) | None | `handback_extract.py:6-7` `--transcript PATH --out FILE [--report-out REPORT]` or `--local-ids FILE...` (09-29); `known_values_check.py:12` (10-01); `report_lint.py:10` `REPORT.md --map C=…` (09-23); `gate_files.py:5-6` (09-28); `relaunch-suite.sh` (09-07); `resume-heal.sh` (09-25) | Files (b); flags (a) |
| inline python (1.1%) | None | — | (c) |
| wait (0.6%) | None; #398 (L1837) asks for a wait mode for `ci` | `ci_gate.py --wait` (CLAUDE.md: `--wait 1800`) | A branch (b); seconds (bounded int) |

Labels already registered and not built:

| Label | Task (ledger line) |
|---|---|
| warm | #388 (L1815) |
| prepush | #390 (L1820), #424 (L1877), #446 (L1905), #465 (L1953) |
| pcgpu | #465 (L1953) |
| pcship, pcjob and commit | named at L1967 |
| whois `agent=<id>` | #367 (L1755) |
| a detached gate runner | #401 (L1844) |
| an upstream file at a pinned tag | #459 (L1935) |
| a wait mode for `ci` | #398 (L1837) |
| a literal mode for `echo` | #435 (L1892) |

---

## T5. The layers, located

| Layer | What exists (file:line, date) | What does not exist (where I looked) | Mark |
|---|---|---|---|
| 1. State stream | **The export.** `scripts/session_export.py:2-3, 8` (10-01) writes one JSON object per event, in source order, "for the RWKV student". It also writes pruner_archive events (L25-26).<br>**The render.** `scripts/s1_train/render.py` (10-01) is the one render, one event at a time (L5-8). LABELS L40-45. CAP, HEAD and TAIL are 4000, 3000 and 1000 (L35). `block` L100-114, `render` L117-125.<br>**The view.** `scripts/s1_train/view.py` (10-02): the state D-3 (L16-21), the guards (L23-31; GUARDS L69), TARGETS L75, STEP_EVENTS L76.<br>**The joins.** The injections log (hook_context.py:103-124). The join itself: build_s1.py:326-329 and s1_scores.py `join_state` L364-388 (09-26). | No live reader that streams events into a hidden state: #448; breakdown L80-86. No per-role states: #453. | SOLID |
| 2. Choice heads (#441) | The question (common.py:55-58). The dataset and the baselines (build_s1.py:40 and 289-297; breakdown L38). The plan (breakdown L66). | No head code. `git grep -i InfoNCE` hits only `tasks/laya-s3-breakdown.md:66` and `docs/research/findings/CLM-AGENT-BEACON-READ-2026-09-24.md:60` (09-24). No pre-registration doc in `docs/research/findings/s1-train/`. | SOLID |
| 3. Micro-output head | D-133 (decision log L144); the brief, L73; the ledger, L1965, L1969 and L1971 | No code. `git grep -i -E 'micro-output\|micro output\|microoutput'` hits only those five lines. | SOLID |
| 4. Deterministic expansion and checks | **stack.py:**<br>- types and limits: VALUE_RE L81-84, TEXT_MAX L74, Param L161-199, Stack L349-412;<br>- loading: `load_registry` L415-434, `deny_rule` L443-459;<br>- checks: `check_path` L462-488, `check_scalar` L491-508, `validate` L511-519;<br>- expansion: `derive_words` L522-531, `parse_tokens` L605-637, `invocations` L666-680, `pre_resolve` L683-713, `build_plan` L726-736. `pre_resolve` fills placeholders from the request's values, from `each`, `run` and `tmp`, and from the environment, such as `{branch}`.<br>**ls_req.py:** regexes L174-187, `parse_box` L538-587, `parse_message` L590-663, the nonce L116-121.<br>**Answer-shape checks:**<br>- `_check_answer` in jev.py (L194-212);<br>- laya_systemone_server.py:219-220;<br>- `why_malformed` in s1_scores.py (L211-224);<br>- ANSWER_RX in s1_synth.py (L158). | No function resolves a value from the event stream. `pre_resolve` reads the request, the registry and the environment only (L683-713). | SOLID |
| 5. Runner and policy hooks | **stack.py:** Runner L752-982, `cmd_run` L1298-1382, exit codes L46-47, the run log `.jev/stacks/runs.jsonl` (L40, L1222).<br>**ls_req.py:** `run_request` L826-869, `cmd_stop` L1174-1369.<br>**The KC-J1 screen:** `no_laya_in_gates.py` over `gate_files.txt`. Its vocabulary is `laya`, `systemone`, `system_one`, `decide ask`, `sieve` and `jev` (COUNCIL-VERDICT-JEV-LAYA-v1.md:45, 09-22).<br>**Blocking hooks:** H3 and H9.<br>**Endpoints:** J7.<br>**Hermes:** the snippet maps session-start, wiki-context, edit-snapshot, graft-first-nag and turn-retro (config-snippet.yaml:129-172) and is marked "NOT SMOKE-TESTED" (L17-21). RESEARCH-FINDINGS-2-part1:51 (09-22) says Hermes `pre_tool_call` runs under `plugins.hook_callback_timeout` (default 30 s, maximum 600) and fails closed on timeout. | Hermes has no mapping for system1-context, search-intercept, filepacks, ls_req, task_sync or the pruner (snippet L108-116). | SOLID; the Hermes rows are UNSURE |
| 6. Feedback signals | **S1-RATE:** the request (hook_context.py:56-58) and SCORE_RX (L55).<br>**s1_scores.py** (09-26): statuses L24-34, `read_session` L287-342, `join_state` L364-388.<br>**Stack ratings:** RATE_RE (stack.py:85), `parse_ratings` L640-648, `check_ratings` L1138-1168, `rating_lines` L1171-1174.<br>**ls_req:** the receipts (L77-84) and the ledger file `.jev/req/ledger.jsonl` (L130-140).<br>**Pruner:** decision records (fast-jev-output.ts:347-363).<br>**Logs:** jev.py writes `.jev/calls.jsonl` (docstring); the relay keeps a data log (jev_relay.py:2-35).<br>**Misses:** the miss accounting (jev_pipes/accounting.py:3-8). | S1-RATE-R1 (#318, pending, L1638). The max-relevance examples (#432). I report no live counts because I read nothing under `.jev/`. | SOLID |

---

## T6. Instruments for a constrained output

| Instrument | Where and version | Constrained output | Evidence | Mark |
|---|---|---|---|---|
| llama.cpp, the build the RWKV-CPU run used | **On this machine:** no.<br>**Pin:** `docs/research/findings/s1-train/RWKV-CPU-2026-10-01.md:33` (10-01): "as vendored in llama-cpp-python 0.3.36 (PyPI sdist sha256 832db069…), build 0c1e570; CMake Release, `GGML_NATIVE=ON`, CPU only".<br>**Tools the run used:** llama-completion (L50), llama-embedding (L60-61), llama-bench and llama-quantize. The run patched embedding.cpp (L218-220).<br>**The build path:** `hidden.py:16-17` (10-01) sets EMBD to the script's own directory + `/lcpp/llama_cpp_python-0.3.36/vendor/llama.cpp/build/bin/llama-embedding`. That tracked directory holds only bench.py and hidden.py. | Unknown for build 0c1e570. I did not run `--help`, because there is no binary.<br>Claims only: `.claude/skills/llama-cpp/SKILL.md:184-191` (09-02) shows `./llama-cli … --grammar-file grammars/json.gbnf` and says "Outputs valid JSON only". `.claude/skills/gguf/references/advanced-usage.md:247-288` (09-02) shows `LlamaGrammar.from_string` in llama-cpp-python. | The find over / (pruned paths below) found no llama-* binary, no libllama, no llama_cpp module and no GGUF file | UNSURE |
| BlinkDL `rwkv` package | **On this machine:** not installed.<br>- `find_spec('rwkv')` is None in the system python.<br>- It is absent from /root/venv-agent-factory, /root/venv-crg, /root/venv-laya-probe and /root/venv-slopo.<br>- No site-packages/rwkv turned up in the find.<br>**Pin:** the run used 0.8.32 (RWKV-CPU L32). | I did not read the sampling source.<br>Claim: `.claude/skills/rwkv/SKILL.md:61-77` (09-02) shows `PIPELINE` and `pipeline.sample_logits(out)`.<br>`bench.py` (10-01) uses only forward, argmax and PIPELINE; it calls no sampler. | RWKV-CPU L157-171 has the package's numbers; L224-226 has a note on its model.py:185 (not restated here) | UNSURE |
| vllm-rwkv | **Where:** `/home/user/rwkv-rs/vllm-rwkv`, a git checkout outside the repo. Branch rwkv-torch, HEAD 67f0c59 (08-04), origin https://github.com/rwkv-rs/vllm-rwkv.<br>**State:** no compiled `.so`; `vllm` does not import here. | `vllm/v1/structured_output/` holds backend_guidance.py, backend_lm_format_enforcer.py, backend_outlines.py and backend_xgrammar.py.<br>The RWKV-7 model files are `vllm/model_executor/models/rwkv7.py` and `rwkv7_wkv_backend.py`.<br>`tests/model_executor/models/test_rwkv7.py:4360` is the unit test `test_rwkv7_rapid_sampler_receives_grammar_masked_logits`; it uses stubs (L4369-4402). | `docs/research/findings/jev-pipes/VLLM-RWKV-2026-09-25.md:13-25` (09-25): BLOCKED on the 3090, because FlashRWKV needs SM90 and the card is SM86. L95: parked. | UNSURE (not run) |
| SGLang, the PC's local route (Qwen) | On the PC, not on this machine | The grammar kernel `apply_token_bitmask_inplace_kernel` loads at the first constrained request. It took 642 MiB at first use. The out-of-memory event was at 03:53:58Z. | `PC-BRIDGE.md:196-200` (10-02).<br>`tasks/briefs/serving/SGLANG-EVIDENCE-report.md` (10-02): L612, L615, L624 (a JSON-schema answer returned 200) and L642.<br>`docs/INCIDENT-LOG.md:12` and `:925`, AF-AP-260 (10-02).<br>D-132 (decision log L143).<br>Skill claim: `.claude/skills/sglang/SKILL.md:173-210` (09-02). | SOLID as recorded by others. The route serves Qwen, not RWKV. |
| Python constrained-decoding packages | None of these import in the system python: xgrammar, llguidance, outlines, guidance, llama_cpp, vllm, rwkv. None of these names is in the four venvs' site-packages. | — | Vendored skills only: outlines SKILL.md:81-155 and guidance SKILL.md:102-119 (09-02) | SOLID, for absence on this machine |
| TypeSafe/Jev answer types | noul, choice and score only; there is no text type | `vendor/jev-pruner/src/jev.ts:7-50` (09-25). `laya_systemone_server.py:219-220` answers 400 for any other type. | RESEARCH-FINDINGS-2-part1:16 (09-22): `answers[qid] = {type, choice, probabilities, confidence}`. `.claude/skills/typesafe-ai/SKILL.md:20-23` (09-22): typed answers and probabilities, "rather than generating text". | SOLID |
| Closed grammars in our own code | Four grammars:<br>- the REQ grammar in ls_req.py (L25-39) and the box grammar (L41-75); L23-24 calls it "a labeling scheme as well as a detector";<br>- VALUE_RE in stack.py (L81-84);<br>- SCORE_RX in hook_context.py (L55);<br>- ANSWER_RX in s1_synth.py (L158). | Each one parses text after it is written. None of them constrains decoding. | — | SOLID |

**Speed figures for a micro-output.** I did not reproduce any of them, so all are UNSURE for me:

| Figure | Source |
|---|---|
| RWKV-7 0.4B, Q8_0, through llama.cpp on 3 sandbox threads, generates 46.0 and 47.7 tokens per second. These are the premise rows. | RWKV-CPU L82-87, rows L85 and L87 |
| On the 3090, 61,440 tokens take 1.17 s, and a question from a copied state takes 0.04 s. | breakdown L39 |
| "The time of one decision through llama.cpp is not measured." | RWKV-CPU L221-222 |
| J0 measured Laya FP32 (not RWKV) at p50 260 ms in the sandbox and p50 336 ms on the PC. | leverage audit §4, L67-68 |

---

## Contradictions between cells (both sides; not resolved)

| # | One side | Other side |
|---|---|---|
| C1 | **Model calls in labels.** stacks.toml:20-21: "No stack calls a model (KC-J1 …)". label-authoring SKILL.md:83: "Until task #391 builds the class, scripts/stack.py still refuses a model call in any stack." box-and-labels SKILL.md:88: "No stack calls a model (KC-J1) or acts outward; `scripts/stack.py` refuses a registry that tries." | stack.py refuses `outward = true` (L355-356). It has no model-call check: `grep -n -i -E 'jev\|laya\|model\|kc-j1\|systemone\|system_one' scripts/stack.py` returns 3 lines, all `.jev/stacks` log paths (L40, L1222, L1412). The only other enforcement I found: tests/test_stack.py:2557-2561 pins `--order lexical` and `--no-jev-log` for locate and fix-echo, and find's chat step passes the same flags (stacks.toml:350-357). |
| C2 | The audit's §5 ap-hawk row (JEV-LEVERAGE-AUDIT L76) cites `scripts/gate_files.txt:53` for edit-snapshot. | The path is on L54. L52-53 are a comment. |
| C3 | LS-AUDIT S6 (L120, 09-28): AP_SCREEN has "53 entries (38 AF-AP ids plus 15 inherited)". | My grep count of the rows from edit-snapshot.py:132 is about 66. The two methods differ. |
| C4 | LS-AUDIT S3 (L117, 09-28): "L2b (a hook that reads the cache) is NOT built". | filepacks.py (09-30) reads codemap packs (docstring L25). Ledger L1888 says "K2 LIVE". This session's PreToolUse injections carry "codemap … symbols" lines. |
| C5 | The audit's §5 (L80) says the pruner "engages over 10,000 estimated tokens". LS-AUDIT B7 (L105): `fast-jev-output@0.1.0` with a floor of about 10,000. plugin.json (10-01): version 0.1.1, default minTokens 10000. | Orient at this session's start: the installed floor is 1,000 tokens; the ledger names commit 625278c. The installed options are not in the tree. |
| C6 | KC-J5 (COUNCIL-VERDICT-JEV-LAYA-v1.md:50, 09-22): "If one incident occurs in which a dropped or hidden item changed a decision, at any date, drop mode is off permanently and everywhere; the layer is reorder/shadow only." chat_find.py:31 restates it as "it reorders the hits, it never replaces them". | The pruner runs in drop mode (retention.ts:54-56). Orient today: "pruned 2". #406 is running. |
| C7 | **RWKV latency.** D-133 (L144): "about 21 ms a token, so a 40 ms budget holds about two generated tokens there". That figure comes from the generation speed in RWKV-CPU. D-133 also says "the speed is measured on the PC's CPU and GPU before any budget claim". | RWKV-CPU L221-222: one decision through llama.cpp "is not measured". breakdown L39: a question from a copied state takes 0.04 s on the 3090. |
| C8 | Commit 4bfa4da3 (09-24) message: search-intercept "stays OFF until a deliberate re-arm". | Both settings copies register it today (settings L133-140). |
| C9 | hook_context.py:42 and search-intercept.py:58 say Claude Code's default hook timeout is 60 s. | I found no harness source in the tree to check this against. |

---

## What I could not find, and where I looked

1. **No llama.cpp build and no rwkv package on this machine.**
   - I ran `find /` with these paths pruned: /proc, /sys, /dev, /tmp/claude-0, /root/.claude/projects, /root/.codiv, /root/.config/session-export, every `.jev` directory, and /home/user/agent-factory/.git.
   - It found no llama-* binary, no libllama, no llama_cpp module, no site-packages/rwkv and no GGUF file.
   - The run's directory holds only bench.py and hidden.py.
   - Builds in other sessions' scratchpads under /tmp/claude-0 are not checked; the rules forbid reading them.
2. **The grammar flags of llama.cpp build 0c1e570.** Unknown, because I did not run `--help`.
3. **The JEV-MAP report (35 decision points).** `git ls-files | grep -i JEV-MAP` finds only its brief.
4. **A pre-registration document for #441.** None under `docs/research/findings/s1-train/`.
5. **The installed pruner options.** They are not in the tree. The ledger names them: a floor of 1,000 (commit 625278c), maxStateTokens 8000 (L1870), historyTokens 3000 (L1893), baseUrl :47430, model openjev-latest.
6. **The coordinator's command-kind counts.** They come from transcripts I may not read, so I did not verify them.
7. **The `.jev/` state.** I read none of it, by rule, so T5 layer 6 has no live counts. This covers:
   - the switches, such as `intercept-jev-rank-on`;
   - `injections.jsonl`;
   - `calls.jsonl`;
   - the stack run log;
   - the req ledger.
8. **The honey `logcompress` implementation and the Aegis plugin's contents.** Not read. Both plugins are enabled.
9. **Documents I did not read in detail.**
   - JEV-LEVERAGE-EVIDENCE: E3 (L104-180) and the unfilled cells (L588).
   - D105-DESIGN-v1.md (09-29): §3.1 and §10.
   - The system1-context design doc.
   - LS-AUDIT §4.1 (L280).
   - decide-harvest L25-33.
10. **Open tasks I did not inspect.**
    - These are the not-closed tasks with no System-1 or Jev keyword hit: 59 ids, listed below.
    - The keyword pass used task_sync's own extractor at 1ffee610: 249 tasks placed, 144 not closed, 85 keyword hits.
    - Since then the ledger has only gained two lines.

    148, 170, 289, 291, 302, 304, 305, 306, 307, 319, 320, 324, 328, 329, 330, 331, 333, 336, 337, 338, 342, 343, 347, 350, 354, 355, 356, 358, 365, 366, 371, 372, 376, 383, 384, 386, 387, 402, 403, 405, 416, 417, 421, 425, 427, 429, 433, 437, 442, 450, 452, 455, 456, 457, 458, 461, 463, 464, 466.
11. **A test or measurement of constrained decoding with RWKV.** None in the tree. The only related item is the stubbed unit test in vllm-rwkv, which sits outside the repo.

## What I did NOT do

- **No outside actions.** No network, no PC bridge, no subagent, no background job, no download.
- **No forbidden reads.** I read none of these:
  - `.jev/`, `/root/.codiv/`, `.pc-bridge.env` or any `*.env`;
  - the pseudonym key, any export, or any transcript under `/root/.claude/projects/`;
  - `transcripts/sandbox/chat-2026-10-02.md` or the pruner's archive;
  - the session scratchpad outside the `s1micro/` directory I made.
- **Settings files.** I read `/home/user/.claude/settings.json` only to compare its `hooks` key. I read `/root/.claude/settings.json` only for its `enabledPlugins` key.
- **No tree changes.** I changed no tracked file and made no commit, stash, checkout or reset. At the end, `git status --porcelain` and `git stash list` were both empty at the retro commit.
- **No label runs.** I ran no label and wrote no box. stack.py was not run. I used task_sync only as an in-process extractor, with `PYTHONDONTWRITEBYTECODE=1`.
- **Nothing executed.** I did not run llama.cpp `--help`. I did not build or run vllm-rwkv.
- **No conclusions.** No root causes, verdicts, designs or fixes.