> Auditor C's design report, verbatim from its hand-back (2026-09-25; read-only audit at origin 934bc8a). One pronoun changed to "they". The plan that
> synthesizes the three areas is `PLAN-2026-09-25.md` in this directory.

# JEV-FIT area C: System 1 in the agent factory (auditor C)

I read the tree at origin 934bc8a (`claude/soundbox-kit-migration-iz1jwf`). All paths below are under `/home/user/agent-factory/`. I ran no model and did not use the PC. Stages 2, 5 and 6 are not built, so every product payoff is unmeasured unless I name a count from our records.

## Answer

System 1 fits the product in four places:
- **Beside the Hermes turn:** a loop nudge and anti-pattern warnings, returned through `pre_llm_call`.
- **At each turn end:** tags on the staged observation, which feed the dream phase.
- **In the dream and Foundry queues:** ordering and near-duplicate flags.
- **Later, in memory recall:** the order of recalled records.

System 1 has no place in the policy hook, the governance core or the evaluators. A rule is enough there, and a Jev would break fail-open.

The RWKV reader's best product use is the turn-end tag. Its state already holds the whole turn, so a tag costs one short question. A System 2 triage would have to re-read the trace.

Two gaps block every product Jev today:
1. The never-a-gate screen does not cover the product's own gate code.
2. The Hermes lane exports drop the tool results that would become the training labels.

## 1. Where System 1 can and cannot sit

- **Not in `pre_tool_call`.**
  - The hook is fail-closed with a 3 s timeout (`config/hermes/config.yaml.example:33-37`). A timeout or a malformed answer denies the call (`docs/03_INTEGRATION_CONTRACTS.md:119`). A slow Jev there would deny tools.
  - Hermes gives this event no advisory channel (`harness-ports/hermes/config-snippet.yaml:183-187`).
  - The council ruled "No tap on any policy-gate path, at any stage" (`docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md:184`).
  - A rule is enough anyway. The policy is deterministic, so its own dry run predicts its denials. Context assembly already lists only policy-filtered tools (`docs/04_MEMORY_AND_GOVERNANCE.md:44`).
- **The advisory path is `post_tool_call` → spool → `pre_llm_call`.** Injection at `pre_llm_call` fails open (`docs/02_COMPONENT_AUDIT.md:30`) and has a 30 s budget (`config-snippet.yaml:139`). The spool is built and tested for lanes (`harness-ports/bin/hermes-hook-adapter.py:146-191`). It costs one turn of delay (`config-snippet.yaml:148-153`).
- **No seat in the governance core.**
  - `load_packet`, `verify_review`, `bound_records` and the pin are hashes, signatures and Fubuki rules (`src/agent_factory/governance/packet.py:136-156`, `review.py:101-215`, `bounds.py:34-111`). A packet changes once per deployment (`docs/04:115`).
  - The only links to System 1: every Jev event carries the governance hash (the envelope requires it, `src/agent_factory/audit/events.py:35-39`), and a new packet ends every stream state.
- **Dream phase: outside GBrain.**
  - ADR 0006 wraps GBrain unchanged (`docs/adr/0006-gbrain-seam.md:28`). So a Jev cannot replace GBrain's LLM triage (`docs/02:95`) unless that ADR reopens.
  - The Jev seats are the first-party exporter and the review queue (`docs/11_DREAM_PHASE.md:13,15`).
  - The inside-worker option at `docs/11:119` is stale on two counts. It says Laya needs an OmniRoute route, which D-082 reverses (`docs/08_DECISION_LOG.md:93`). It would also change the wrapped code.
- **Foundry: the first-party host owns tool dispatch** (`docs/adr/0005-foundry-host.md:42,54`). That host is a cleaner observation seat than Hermes hooks. Evaluators stay deterministic first (`docs/06_EVALUATION.md:36`).
- **Memory recall needs an order.**
  - `merge()` sorts by scope precedence, then by stable id (`proofs/S0-06/adapter/factory_memory.py:219-249`).
  - The budget cut that `docs/03:90` requires is not built. If it keeps the head of that list, it keeps records by scope and path name, not by relevance.

## 2. Integration points

### 2a. Seam, trigger, input, question, action

| ID | Seam (file:line) | Trigger | Input | Question (type: options) | Action |
|---|---|---|---|---|---|
| C1 Loop nudge | Observer + spool: `config-snippet.yaml:154-157`, `hermes-hook-adapter.py:146-175`. Drain: `:179-191`. Fact-ledger template: `harness-ports/bin/lane-done-gate.py:145-179`. Turn caps: `docs/03:12-13` | each `terminal` / `patch` / `write_file` result | the session's fact ledger (rule); the stream state (RWKV) | Rule: same normalized command, no write since → same outcome. Jev (choice: same / different) only for a re-run after a write | one advisory line next turn; a notice in the Buzz thread; never a cancel |
| C2 Turn-end tags | End-of-turn staging write: `docs/03:95`; `factory_memory.py:388-449`, `tags` at `:438`. Follows the ACP result: `docs/01_ARCHITECTURE.md:86-88` | the turn's terminal ACP result | RWKV state at turn end (no re-read) | multi-label yes/no over the triage classes (`docs/11:38`): user correction, recurring failure, successful procedure, conflict, missing knowledge | tags on the staged observation; the exporter puts tagged turns first in a budgeted snapshot; nothing suppressed |
| C3 AP-hawk, then drift-hawk | the C1 spool; an advisory field on the tool event (`events.py:23-52`); never `pre_tool_call` | each effectful call's result | hunk or command + lexical top-k registry rows (Laya per pair); for drift, the stream with the task (RWKV) | `ap.violates_row` yes/no per row (`src/agent_factory/decisions/volatile.py:246-257`); `wf.drift` step and kind (`:258-284`) | "suggested, unverified" line next turn; ordering of the external-mutation approval queue (`docs/05_SECURITY.md:51`) |
| C4 Dream queue, near-duplicates | exporter and review queue (`docs/11:13,15,37,43`), outside the wrapper | each cycle; each proposal | proposal + lexical top-k rejected proposals (Laya per pair); source traces (RWKV) | `dp.keep` / `dp.promote` / `dp.dup_rejected` (D-058, `docs/08:69`) | queue order; "likely re-discovery of rejected X" shown beside X's rejection reason; promote one level only (`docs/11:89`); never a filter (`docs/11:113`) |
| C5 Recall order | `recall` (`factory_memory.py:346-386`), after `merge()` and Fubuki bounds (`bounds.py:34-111`), at the unbuilt budget cut (`docs/03:90`) | each recall at context assembly | up to 80 authorized, kept records (4 scopes × `DEFAULT_LIMIT` 20, `factory_memory.py:79`) + the turn | score per record: will this turn use it? | which records fill the budget; the rest stay recallable; non-overridable invariants stay outside the ranking (`docs/04:36`). Plus a rule: never re-inject a stable id the session already holds |
| C6 Eval-run early stop | the Foundry host's dispatch loop (`adr/0005:42,54`; `docs/10_HARNESS_FOUNDRY.md:34-39`) | each dispatch in a candidate run | as C1 | as C1; a failure class at run end | stop a run that repeats a failure; mark it incomplete (a gate reads that as "not evaluated"); record the stop as a ledger row so the run replays (`docs/10:98`) |
| C7 Policy hook, governance core, evaluators, route failures | `config.yaml.example:33-37`; `src/agent_factory/governance/`; `docs/06:36`; `docs/01:95` | - | - | none | **a rule is enough** |

### 2b. Payoff, labels, model, build

| ID | Payoff (count, source) | Labels; rule to beat on held-out examples | Model | Build (depends on) |
|---|---|---|---|---|
| C1 | 193 of 3,337 test runs repeat an identical command; with no write between, the outcome repeats 86 of 89 (`docs/research/findings/laya-ft-data/JEV-INTEGRATION-MAP-2026-09-25.md:251-255`). The cost sits in long loops: one lane spent 47 min re-running a lint between edits (AF-AP-76, `docs/INCIDENT-LOG.md:575`), the case the rule misses. Product: unmeasured | R17 (3,337) and R1 (34,486) outcomes. The rule is the incumbent. The Jev must beat "same outcome" on re-runs after a write (60 of 104 repeat) | **rule** for exact repeats; RWKV for the residual | small (rule + profile hooks); medium (RWKV) |
| C2 | The retro gate led to a bake at 36 of 965 turn ends (R8, R7; `docs/research/findings/laya-ft-data/SESSION-DECISIONS-2026-09-25.md:120-121`), a lower bound. Lessons are sparse, so tag-first ordering shrinks what GBrain reads. The reader follows a session for about 1.1 s of 3090 time per active hour (`JEV-INTEGRATION-MAP:522`, UNSURE). Tag recall: unmeasured | R8: 52 (under KC-J7's 200); registry rows added: 242 (D-085, `docs/08:96`); owner "no": 13 of 224 (R13, `SESSION-DECISIONS:126`). Rule: deterministic tags (a failed check that later passes; a denial; an owner reply that opens with "no") | RWKV | medium (stream server; Stage 2 write path) |
| C3 | 137 registry rows have no mechanical screen (`docs/research/findings/JEV-LEVERAGE-AUDIT-2026-09-24.md:76`); 86 of 346 edit snapshots trip a mechanical tell (R18, `SESSION-DECISIONS:131`). Product volume: the PC lane digests hold `terminal` 11,931, `patch` 5,632 and `write_file` 1,017 results (`SESSION-DECISIONS:314,319`). Errors saved: unmeasured | `ap.violates_row`: 242 positives + not-cited negatives (D-085); beat lexical top-1 0.59 / top-3 0.69 (`docs/research/findings/j2b-variants/rwkv7-g0/2026-09-24-window2/README.md:13`). `wf.drift`: 3 labels (`JEV-LEVERAGE-AUDIT:19`), a KC-J7 famine | Laya per pair (ap); RWKV (drift) | medium (spool; registry seeded into Company scope) |
| C4 | reviewer time; unmeasured (Stage 5) | 0 outcome records today; 200 human labels before any ordering (`docs/11:115`). Beat digest suppression (`docs/11:79`) + lexical overlap. Pre-train on `ap.violates_row` (same two-stage shape) | Laya per pair; RWKV per trace | large (Stage 5) |
| C5 | unmeasured; the sandbox analog injects 6.5 to 11.5 KB per event (`JEV-LEVERAGE-AUDIT:34`) | none recorded. Shadow-log both orders; the label is a later cite or read of the record in the stream. Beat the substrate's FTS5 `rank` (`factory_memory.py:195-207`) | **rule today** (FTS5 within precedence); RWKV later | medium (Stage 2) |
| C6 | eval compute; unmeasured (Stage 6) | lane ends R24: report 45, patch 43, timed out 34, premise gate 8 lanes (`SESSION-DECISIONS:137`, UNSURE). Rule first | rule, then RWKV | large (Stage 6); reuses C1 |
| C7 | - | Route failures cluster: 10 of 13 failed agents followed a sibling failure within 15 min, against 0 of 215 completions. The error is the last record, with 0 s lead (`JEV-INTEGRATION-MAP:19,367`). A circuit breaker beats any predictor | **rule** | - |

Not designed, with the reason:
- **Routing Buzz messages to a chat-only Qwen teammate (D-033):** no seam in this repo, and the council deferred tier routing.
- **A keep-list for Hermes compaction:** no seam has been proven to fire. (Both findings: `COUNCIL-VERDICT-JEV-LAYA-v1.md:137`.)
- **An injection detector over recalled text:** no labels in our records.

## 3. Top five (payoff against build size)

| Rank | Point | Why this rank | First step |
|---|---|---|---|
| 1 | C1 loop nudge (rule) | smallest build; strongest measured rule (86 of 89); serves production turns and C6 | add `post_tool_call` and `pre_llm_call` to the product profile (it has only `pre_tool_call`, `config.yaml.example:33-37`); reuse the done-gate fact ledger |
| 2 | C2 turn-end tags | a job only the stream reader does; it turns the dream phase's read cost into a tag query | a closed tag schema; shadow rows in the ledger |
| 3 | C3 AP-hawk | same question and registry as our sessions, so the most direct carry-over; drift waits for labels | seed the registry into Company scope; add the spool line |
| 4 | C4 dream queue | choosing the seat now costs nothing; the model waits for 200 human outcomes | amend `docs/11:117-120` |
| 5 | C5 recall order | ship the FTS5 order now; the model earns its place in shadow | a budget step that orders by FTS5 rank within precedence |

C6 rides on C1: the same detector with a second consumer.

## 4. Shared infrastructure

1. **Stream tap.**
   - A hook shim or a Hermes plugin (D-013's promotion target, `docs/08:24`) emits each tool call, each result and each ACP turn end as one event in SESSION-EXPORT's schema (`tasks/briefs/jev-laya/SESSION-EXPORT-brief.md:40-50`).
   - It scrubs inside the Hermes container, before the event leaves. It uses `scripts/transcript_export.py`'s `scrub`, which the Hermes exporter already imports (`harness-ports/bin/hermes-session-export.py:22-30`).
   - The built `Event` has no top-level `session_id`, `turn_id` or `redaction_version` (`events.py:23-31`). `docs/03:165-178` requires all three.
2. **Stream-state server (System 1, D-082).** Not built.
   - It runs locally with no egress (KC-J9). One RWKV state exists per (session, scope tuple, governance hash). States live in memory only and are dropped at session end or on a new packet.
   - A state never answers for another session. It is derived from that session's authorized recall, so sharing it would cross scopes.
   - Size by arithmetic: about 1.6 million values per session (24 layers × 16 heads × 64², assuming a head size of 64), about 3 MB in bf16. Unmeasured.
   - If the server is down, slow or unsure, each consumer keeps its rule order.
   - OmniRoute does not log System 1 calls, so the ledger is their provenance record (KC-J6).
3. **Per-block service.** `scripts/laya_systemone_server.py` (loopback-only bind, `:205-214`) and `scripts/jev.py` (fail-open with exit 3, `:546-549`; it keeps a call log).
4. **Return path.** The spool, plus queue labels.
5. **Label log.** The decision ledger (`src/agent_factory/decisions/ledger.py`) is already in the product package. It needs three changes:
   - product source kinds (`_VALID_KINDS`, `:46-52`, has none for Hermes sessions, audit events or dream outcomes);
   - a model-answer row form (`:216-223` forces `checkpoint_digest` "none" and `calibration_state` "incumbent");
   - closed schemas for C1, C2, C4 and C5 (`volatile.py:214-285`).

   Its redaction is verified MERGE-READY-WITH-FOLLOWUPS (`todo/BUILD-TASKLIST.md:1453`).
6. **Screen the product's gates.**
   - `scripts/no_laya_in_gates.py:1265-1288` walks only `scripts/hooks/*`, `.github/workflows/*.yml` and `proofs/*/check_*.py`. `scripts/gate_files.txt` lists no `src/` file.
   - So `src/agent_factory/governance/`, the future policy service, the adapter's `authorize`, the dream validator and the promotion service are outside KC-J1 today.
   - Add a fourth pattern before the first product Jev lands.
7. **Containment.**
   - Neither the Hermes allow-list (`docs/05:79`) nor S0-05's pinned allow-set (D-055, `docs/08:66`) includes a System 1 server.
   - Prefer a file seam: events are appended to a mounted sink, and advisories are written to the spool. Then no new network edge enters Hermes's containment. A socket would need an ADR and a new S0-05 proof.
   - Dream and Foundry workers get no route to the server (`docs/05:83`). Their Jev seats are system-side.
8. **GPU.**
   - vLLM holds 24,022 of 24,576 MiB (D-040, `docs/08:51`). Co-residency with a reader is unmeasured (`JEV-INTEGRATION-MAP:495-499`).
   - Live updates are small (median 143 tokens per event, `:514`), far below the 10,474 MiB of one 61,440-token forward.
9. **Injection.** Every Jev reads untrusted text. A crafted message can at most flip a typed label. Labels only warn or reorder; the validator, the deterministic tests and a person decide (`docs/11:41-43`).

Items 3, 4 and 5 exist in our workflow today, and item 1 reuses our scrubber and export schema. This is D-084's "3 birds, 1 stone" (`docs/08:95`).

## 5. Carry-over from our sessions

Our workflow is the blueprint of the factory's first coding team (`docs/WORKFLOW-OFFLOAD-MAP.md:5-8`), and the PC lanes already run Hermes, the product's only runtime. So Hermes lane streams are in-distribution for the product, and Claude Code sessions are close to it. What carries over is the question, not the tool name: the closed schemas ask the same `ap.violates_row` of a Claude Code Edit and a Hermes `patch`. The generic questions transfer: exit class, edit applies, test outcome, verify class, the anti-pattern and drift questions, and the retro gate's bake-or-nothing answer as C2's lesson tag. Harness-specific questions do not: the sleep block, the Stop git check, push_clean. One gap blocks the in-distribution half. The Hermes exporter keeps tool-result bodies out by default (`hermes-session-export.py:44-45`), so 29,211 PC tool results carry no outcome (`SESSION-DECISIONS:343-344`). The first step is a SESSION-EXPORT mode in that exporter. It should carry the exit code the done-gate already parses (`lane-done-gate.py:110-125`) and one tool vocabulary (`terminal` = Bash, `patch` = Edit, `write_file` = Write). In the product, a session-trained Jev ships as a Hermes plugin (D-013). It must beat the Hermes baseline on the Foundry's task pack (`docs/10:101`), so the factory's own promotion gate decides whether it earns its place. Our data is single-tenant. Students trained on product sessions stay per tenant, and the owner's personal chat text stays out of training unless they agree.

## 6. NOT done

- **Not read (no PC access):** the Hermes `state.db`, live hook payloads (C2 used coordinator excerpts, `tasks/briefs/canny/C2-report.md:21`), and the reader's CPU and GPU speeds.
- **Not built or scored:** no model was trained or scored, and the Hermes plugin API was not read.
- **Counts reused, not re-run:** every count comes from JEV-MAP, DATA-SESSION or JEV-LEVERAGE.

### Critical Files for Implementation
- /home/user/agent-factory/config/hermes/config.yaml.example
- /home/user/agent-factory/harness-ports/bin/hermes-hook-adapter.py
- /home/user/agent-factory/src/agent_factory/decisions/ledger.py
- /home/user/agent-factory/scripts/no_laya_in_gates.py
- /home/user/agent-factory/harness-ports/bin/hermes-session-export.py