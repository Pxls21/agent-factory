# T93 — local Qwen chat-template 400 evidence

Route caveat: evidence-gatherer lane on the `agentfactory-research` route. This report makes no claim about which model produced it. Evidence only: no diagnosis, recommendation, configuration change, restart, or repair.

Evidence window: UTC 2026-09-22 00:00:00 through a fixed cutoff of 13:21:00Z. Runtime call-log artifacts have no git date; their UTC artifact timestamps are recorded instead. Repository and source citations include git dates.

## Evidence matrix (enumerated dimensions)

| Question | Dimension | Evidence status |
|---|---|---|
| Q1 | status/error counts; rejected role shapes; first producer; successful controls; artifact truncation | filled below |
| Q2 | handoff schema/config/composition/insertion/trigger/time join; Hermes no-system paths; hook behavior | filled below |
| Q3 | exact image; unit args; model template; accepted message grammar | filled below |
| Q4 | tag sequences; chain count; cloud-run length; local return; upper bound | filled below |
| Fix seams | Hermes; hook; OmniRoute combo; model template; authority | filled below |

## PREMISE — RE-MEASURED

Method: Python 3 read-only scan of every matching `call_logs` row from `file:/home/rocco/.omniroute-migrated/storage.sqlite?mode=ro`, joined to every referenced artifact under `call_logs/2026-09-22/`. Population, not sampling; noise floor is zero for row counts. Cutoff drift is expected because the database remained live during the read. No request content was printed except bounded role sequences and system-prefix excerpts.

```
local qwen status: 400 x866; 200 x784; 499 x27; 504 x22
400 text: 780 [400]: System message must be at the beginning.
           86 [400]: No user query found in messages.
refused bodies scanned: 866
largest visible groups:
  395 system-first, H+S visible, sys@[0,1], last=tool, n_user=1
  294 system-first, logged head truncated, no system/user visible, last=tool
   60 no-user-query, logged head truncated, no system/user visible, last=tool
   54 system-first, logged head truncated, no system visible, one user visible, last=tool
   25 system-first, H+S visible, sys@[0,1], last=tool, n_user=2
   24 no-user-query, two non-handoff system messages, no user, last=tool
```

| Fact | Evidence | Status |
|---|---|---|
| Counts changed from the authored cutoff (828 → 866 local 400s; 753/75 → 780/86). | SQLite population read above; the live DB continued receiving calls. | SOLID |
| The premise's `sys@[]` census treated a logger truncation marker as if it proved no leading system/user messages. | 416/866 local 400 artifacts had `_omniroute_truncated_array`, `originalLength`, and `retainedTailItems=128`; their missing head is not recoverable from the summary artifact. | SOLID |
| The complete, non-head-truncated rejected population includes 422 handoff-first `H S ...` requests, 24 compression-generated `S S A/T ...` no-user requests, 2 compression-generated `S A/T ...` no-user requests, and 2 compression-generated `S S ...` system-first requests with a visible user. | Full artifact population; examples below. | SOLID |
| The first producer of the missing leading messages in the 416 truncated artifacts is not visible in those artifacts. | Artifact marker proves omission; `request_detail_logs` has no corresponding full body. | UNSURE |

## Q1 — request shapes

Role key: `H` = `<context_handoff>` system; `S` = other system; `U` = user; `A` = assistant; `T` = tool. Role sequences below are bounded prefixes. “Previous” means the immediately preceding `call_logs` row on the same `session_tag`. Every rejected row used local step 1: `agentfactory-{build|verify}-local-model-1-qwen-local-qwen3-8-27b-local`; the `session_tag` populations were 28 unique tags for visible handoff, 30 for truncated system-first, 12 for truncated no-user, 3 for compressed `S S` no-user, and 2 each for compressed `S` no-user and compressed `S S` system-first.

| Rejected shape | Count at scan | Shape/statistics | Previous call | Three artifacts (UTC filename/id) | First producer | Status |
|---|---:|---|---|---|---|---|
| Visible handoff plus Hermes system | 422 | `H S U A/T…`; systems at 0,1; median 79 messages; median logged content 192,509 chars; 395 end in tool with one user, 25 end in tool with two users, and 2 end in user | 412 cloud-200; 7 no prior same-tag row; 2 local-200; 1 local-400 | `02-03-01.425Z_1790042581248-412011`; `02-05-15.492Z_1790042715350-d2dd0e`; `02-05-42.273Z_1790042742123-046424` | Handoff content is injected by OmniRoute; Q2 gives its composition/insertion evidence. Hermes supplies the following system prompt. | SOLID |
| Logged head omitted; system-first error | 356 | Logger retained only the last 128 of 129+ messages; visible suffixes contain 0–2 user messages; median visible 128 messages and 80,736 content chars | 338 cloud-200; 18 no prior same-tag row | `02-19-47.828Z_1790043587647-fec86c`; `02-19-56.657Z_1790043596463-0f5f7c`; `02-20-22.146Z_1790043621938-d2825f` | Unknown from these summary artifacts. The absent head prevents an exact role sequence or first-producer assignment. | UNSURE |
| Logged head omitted; no-user error | 60 | Logger retained only the last 128 of 140+ messages; visible suffix alternates `A/T`; median 72,003 visible content chars | 51 cloud-200; 2 local-200; 7 no prior same-tag row | `01-20-09.456Z_1790040008918-ab9876`; `01-20-26.915Z_1790040026344-9f5d42`; `01-23-06.826Z_1790040186561-ea4304` | Unknown from these summary artifacts. | UNSURE |
| Compression marker plus Hermes system, no user | 24 | `S S A T A T…`; median 112 messages; median 150,153 chars; message 0 starts `[Context compressed: …]`; message 1 is the Hermes system prompt | all 24 cloud-200 | `05-44-43.145Z_1790055882884-5c65d2`; `05-45-23.848Z_1790055893626-8f1770`; `05-45-30.936Z_1790055930734-395841` | OmniRoute `purify_history` produces/attaches the marker; Hermes supplies the second prompt. Q2 gives code evidence. | SOLID |
| One compression-generated system, no user | 2 | `S A T A T…`; 91 and 119 messages; 120,644/177,847 chars; system content is `[Context compressed: …]` plus the original leading content | both local-200 | `04-31-51.539Z_1790051511349-8b16c2`; `10-28-52.834Z_1790072932645-712521` | OmniRoute `purify_history` attaches the marker to the retained system; Q2 gives code evidence. | SOLID |
| Two compression-generated system messages, system-first error | 2 | `S S A/T…U`; 118 and 124 messages; a user remains at the end | both cloud-200 | `05-48-44.354Z_1790056124060-5079b6`; `12-23-59.207Z_1790079838964-232456` | OmniRoute `purify_history`; exact pre-compression origin of both retained systems is not separately logged. | UNSURE |

### Successful local-200 control

| Control fact | Count | Evidence | Status |
|---|---:|---|---|
| Complete logged `S U …` requests succeeded. | 669 | Local 200 population; median 40 messages and 164,303 chars. | SOLID |
| Complete logged user-only requests succeeded. | 12 | Complete bodies; examples `01-25-56.358Z_1790040066368-e3314f`, `01-34-24.718Z_1790040272816-75e35f`, `03-28-25.490Z_1790047482491-f4dc70`. | SOLID |
| No complete successful body carried two system messages. | 0 of 681 complete local-200 bodies | Population scan. | SOLID |
| 103 successful artifacts appeared to have no system or user only because their heads were truncated to the last 128 messages. | 103 | Every such artifact carries the truncation marker; therefore these cannot be used as no-system/no-user controls. | SOLID |
| A complete local-200 body with zero user messages was not observed. | 0 of 681 complete bodies | Population scan; the query covered every complete local-200 body in the time window. | SOLID |

Q1 artifact source date: each artifact filename embeds UTC 2026-09-22. Git date does not apply to runtime artifacts.

## Q2 — origins

### Handoff block and proactive compression

| Layer | Primary-source evidence | Git/build date | Status |
|---|---|---|---|
| Handoff storage | `context_handoffs` has one unique row per `(session_id, combo_name)`, stores summary/decisions/progress/entities, message count, model, last model, threshold, generated/expiry times. Its 2026-09-22 population at the cutoff was 21 rows, 01:20:26Z–13:01:47Z. | Runtime SQLite schema/data, UTC 2026-09-22 | SOLID |
| Combo protection setting | `combos.context_cache_protection` exists but is `0` for `agentfactory-build-local`, `agentfactory-verify-local`, and `agentfactory-research`. | Runtime SQLite schema/data, UTC 2026-09-22 | SOLID |
| Universal handoff is separate from combo cache protection | Built OmniRoute checks `eR.enabled` and `$?.sessionId`; when `getLastSessionModel` differs from the candidate model, it calls `injectUniversalHandoffBody` with `Model routing`. The separate cache-protection check pins a prior model only when `context_cache_protection` is true. | OmniRoute `BUILD_SHA=dea6bb8`, chunk mtime 2026-09-04; `omni-handoff:9` | SOLID |
| Composition | The injection helper serializes `<context_handoff>`, transfer reason, previous/current model, and, when present, summary/decisions/progress/entities. | `omni-handoff:47`; build date above | SOLID |
| Insertion | For chat bodies it copies the existing list then returns `messages: [{role:"system", content: handoff}, ...existing]`. For Responses bodies it prepends handoff text to `instructions`. | `omni-handoff:36-47`; build date above | SOLID |
| Trigger seen in artifacts | 422 complete rejected artifacts start `H S …`, and 412 had an immediately previous cloud-200 on the same session tag. Their transfer reason says cloud model → local Qwen. | Population artifact scan, UTC 2026-09-22 | SOLID |
| Handoff summary generation | Built code keeps system/developer messages plus a bounded recent tail, asks a separate model with one `user` message, and upserts a handoff row with the configured threshold. The 21 rows had `warning_threshold_pct=0.0`, not the 0.85 default. | `omni-handoff:20-47`; runtime SQLite, UTC 2026-09-22 | SOLID |
| Handoff-row time join | A direct join to call-log `session_tag` is unavailable: `context_handoffs.session_id` is a 16-hex internal affinity key while call logs expose `conv_<uuid>`. No reversible map was found in the readable tables. The first visible row at 02:02:24Z precedes the first complete matching handoff rejection for one build session at 02:03:01Z, but identity cannot be proved from these columns alone. | Runtime SQLite, UTC 2026-09-22 | UNSURE |
| Proactive compression marker | OmniRoute's `purify_history` keeps all system/developer rows plus a shrinking recent tail; when it drops earlier non-system rows it prepends `[Context compressed: N earlier messages removed…]` to the first system row, or unshifts a new system row if none remains. | `omni-compress:1`, built bundle mtime 2026-09-04 | SOLID |
| Combined rejected shape | On provider-switch calls, the handoff injects a leading system. Proactive compression can then prefix its marker to that handoff; the original Hermes system remains second. Artifacts `05-44-43…` and `10-29-25…` show exactly this two-system provider request. | Built code above + UTC artifacts | SOLID |

### Hermes request construction and wire-mode alternatives

The lane premise names pinned Hermes 0.21.0 at `527da60` (`upstream.lock.yaml:10-15`, commit date 2026-09-02), but the executable used by these PC lanes resolves to `/home/rocco/.hermes/hermes-agent` at `b3399c1` / package 0.21.1 (commit date 2026-09-08). Runtime evidence below cites the runtime tree.

| Code path | What it sends | Match to Q1 | Runtime source/date | Status |
|---|---|---|---|---|
| Normal `chat_completions` main loop | The request builder sanitizes the supplied `messages` and passes them through as Chat Completions messages; the caller's normal API-message builder carries the cached system prompt. | Complete successful `S U …`; the two-system fault is introduced downstream, not by this transport. | `hermes-chat:361-375`; runtime git date 2026-09-08 | SOLID |
| Max-iteration summarizer | It appends `MAX_ITERATIONS_SUMMARY_REQUEST` as a real user request, builds API messages, conditionally prepends `effective_system`, then calls `summary_client.chat.completions.create`. | Does not match the complete no-user rejected shapes because it explicitly adds a user at `hermes-helper:2118-2124`. | `hermes-helper:1937-1977` (`effective_system`), `hermes-helper:2005-2029` (`summary_kwargs`), `hermes-helper:2087-2094` (`summary_client`), `hermes-helper:2113-2124` (`MAX_ITERATIONS_SUMMARY_REQUEST`); runtime git date 2026-09-08 | SOLID |
| Automatic conversation compaction | At `_rebuild_system_prompt_at_boundary` it invalidates and rebuilds the Hermes system prompt. It does not create the `[Context compressed: N earlier…]` string seen here. | The observed marker is OmniRoute's, not Hermes compaction's. | `hermes-compression:2779-2812`; runtime git date 2026-09-08; bounded source-wide marker search | SOLID |
| Tool continuation | No separate tool-continuation request builder was found. Tool continuations re-enter the normal message path; the wire history may end in `tool`, but Hermes still supplies its system prompt before OmniRoute transforms it. | Matches ordinary `S U A/T…` input before downstream handoff/compression. | `hermes-chat:361-375`; runtime git date 2026-09-08 | SOLID |
| `codex_responses` | Extracts a leading system message to `instructions`, removes it from payload items, and defaults instructions to the agent identity if absent. It does not emit a Chat Completions body without a system message. | Not the observed local wire: artifacts use `/v1/chat/completions`; runtime profile is reported as `chat_completions`. | `hermes-codex:480-530`; runtime git date 2026-09-08 | SOLID |
| Apparent no-system artifacts | 416 rejected summary artifacts and 103 successful summary artifacts omit the leading head and insert `_omniroute_truncated_array`; these artifacts do not prove Hermes sent no system or user message. | Explains the census's largest “no-system” rows as evidence gaps, not as request-builder shapes. | UTC artifacts, 2026-09-22 | SOLID |

### Hook adapter

| Fact | Evidence | Git date | Status |
|---|---|---|---|
| `pre_llm_call` does not edit a message list or assign a system role. | It maps Hermes's user message to hook key `prompt`, runs the hook, drains prior spool text, and emits only JSON `{"context": ...}`. | `hook-adapter:112-123`, `hook-adapter:178-196`; last commit 2026-09-15 | SOLID |
| The adapter prepends deferred hook text to the hook's returned context string, but the Hermes plugin owns where that context enters the model prompt. | `parts` order at `hook-adapter:181-195`. | last commit 2026-09-15 | SOLID |
| No source evidence in this adapter shows system-message insertion or reordering. | Full `main` skeleton and bounded read `hook-adapter:84-209`. | last commit 2026-09-15 | SOLID |

## Q3 — Qwen3.8 template rule

| Layer | Primary-source evidence | Date | Status |
|---|---|---|---|
| Pinned/live image | Quadlet uses `ghcr.io/syv-ai/qwen38-27b-rtx3090@sha256:c52d…aacb`; live `podman inspect qwen` reports the same digest. It mounts `/home/rocco/qwen-serving/models` at `/app/models`. | `qwen-unit:19-31`, git 2026-09-16; live inspect UTC 2026-09-22 | SOLID |
| No unit override | Unit `EXTRA_ARGS` only adds served model names; no `--chat-template` is passed. | `qwen-unit:27-31` | SOLID |
| Actual template file | The mounted served model contains `chat_template.jinja`, mtime 2026-09-16 06:19:56+01. It is therefore host-mounted model data, not a file inside the immutable image layer. | Live mount + file stat | SOLID |
| User requirement | The template reverse-scans messages for a `user` whose content is not a wrapped tool response. If none exists, `ns.multi_step_tool` stays true and it raises the exact no-user text. | `qwen-template:88-101` | SOLID |
| System placement | While rendering, each `system` message raises unless `loop.first`; therefore at most one system message is usable, and it must be message index 0. | `qwen-template:102-107` | SOLID |
| Tool handling | `tool` rows are accepted and wrapped as `<tool_response>`; adjacent tool rows share one user wrapper. The template does not assert that every tool row follows assistant, but malformed roles fall into `Unexpected message role`. | `qwen-template:147-160` | SOLID |
| Exact accepted grammar relevant here | Zero or one system at index 0; at least one real user query anywhere; assistant/tool rows otherwise render; a second system at any index is rejected. | Lines cited above | SOLID |

## Q4 — loop, measured

Method: read-only scan over all `agentfactory-build-local` and `agentfactory-verify-local` rows with non-null session tags from 00:00:00Z through 13:21:00Z. Population was 77 tags / 2,657 rows. A logical fallback turn is adjacent local-400 then cloud-200 on the same tag. Noise floor is zero for logged-row counts; concurrency can interleave unrelated calls with the same session tag, so the “new user message” check also hashes visible user contents and treats truncated heads as unknown.

| Measurement | Result | Status |
|---|---:|---|
| Adjacent `local-400 → cloud-200` pairs | 854 | SOLID |
| Adjacent `local-400 → cloud-200 → local-400` chains | 793 | SOLID |
| Adjacent `local-400 → cloud-200 → local-400 → cloud-200` chains | 783 across 55 tags | SOLID |
| Runs of consecutive logical fallback turns | 71 runs / 854 turns; min 1, median 6, max 65; 21 runs were 11+ turns | SOLID |
| Example premise tag | `conv_ed17…`: 38 consecutive logical fallback turns from 02:16:22Z to 02:30:11Z; its opening rows alternate local-400/cloud-200 at 1–52-second gaps. | SOLID |
| “Stays on cloud” interpretation | The combo does not stop attempting local. It retries local each logical turn and then gets the cloud fallback. Adjacent raw cloud-200 streaks were only 1 (49 tags) or 2 (7 tags). | SOLID |
| Returns to local 200 after fallback | 3 tags had any later local-200, but one was a concurrent different user hash. Two had local-200 with the same visible user hash; neither proves “without a new user” because call interleaving and head truncation remain possible. | UNSURE |
| Upper bound on cloud turns avoidable by template compatibility | 854 direct fallback cloud-200s / 919 cloud-200s in these two combos = **92.93% upper bound**. This assumes every local 400 would otherwise have completed locally; it is not a causal estimate. | SOLID as arithmetic; UNSURE as counterfactual |

The sequence establishes temporal repetition after provider switches. The injection condition establishes that a model switch can add a handoff system. The evidence does not isolate the handoff from proactive compression as the sole cause for all 866 refusals because 416 summary artifacts omit their request heads and 26 complete no-user refusals have compression-generated system rows.

## Fix seams (candidates only; no repair or verdict)

| Mechanism | Candidate seam | What that seam can change | Authority | Cost/evidence status |
|---|---|---|---|---|
| A: handoff creates a second system | OmniRoute `injectUniversalHandoffBody` | Merge handoff text into the existing leading system message instead of prepending a second system; or choose a role compatible with the target template. | Owner, because this is built OmniRoute behavior/settings. | Direct seam at `omni-handoff:36-47`; SOLID. |
| A: feature trigger | OmniRoute universal-handoff per-combo/global config | Disable or target the handoff feature for local Qwen while preserving other combos. `context_cache_protection=0` does not disable universal handoff in the measured build. | Owner. | Runtime setting location was not exposed in `key_value`; exact UI/API field remains UNSURE. |
| A/B: proactive compression creates/augments system | OmniRoute `purify_history` | Preserve one canonical system message and place the compression notice inside it without adding another system; preserve a user-query sentinel only if semantically valid. | Owner. | Direct built-code seam at `omni-compress:1`; SOLID. |
| A/B: template compatibility | Mounted Qwen `chat_template.jinja` | Change the `namespace(multi_step_tool=true...)` and `loop.first` checks to accept and merge multiple leading system messages, and/or define a guarded continuation mode when no user remains. | Owner, because it changes the live vLLM model template and requires service lifecycle action. | Exact checks at `qwen-template:88-107`; SOLID. |
| A/B: Hermes request builder | Normal Chat Completions `build_kwargs` / request metadata | Supply explicit routing/session metadata or shape the initial system prefix so downstream middleware can identify it. It cannot by itself prevent OmniRoute from prepending after Hermes sends. | Owner for profile/runtime; upstream Hermes change also needs project governance. | Main wire source at `hermes-chat:361-375`; indirect seam, UNSURE. |
| A/B: project hook | `pre_llm_call` hook adapter | The first-party adapter can change injected hook context but currently has no access to or control over the outgoing message array. A new first-party policy/hook contract could normalize prompt content before Hermes builds messages, if Hermes exposes such a seam. | Coordinator for adapter/dispatcher; owner for live hook profile. | Current `INJECT_EVENTS` branch at `hook-adapter:178-196`; SOLID. |
| Cheapest entirely first-party candidate | Change OmniRoute's already-first-party `injectUniversalHandoffBody`/`purify_history` assembly so only one leading system message reaches Chat Completions. | One downstream compatibility layer covers every Hermes caller without changing the model image/template. | Owner for the deployed OmniRoute build; coordinator for a reviewed repo patch if vendored. | Candidate only; no implementation or test in this lane. |

## File/date identity

| Alias | Identity/date |
|---|---|
| `omni-handoff` | `/home/rocco/.omniroute-migration-npm/node_modules/omniroute/dist/.build/next/server/chunks/_04g0p_r._.js`; `BUILD_SHA=dea6bb8`; mtime 2026-09-04 06:40:21+01 |
| `omni-compress` | `/home/rocco/.omniroute-migration-npm/node_modules/omniroute/dist/.build/next/server/chunks/open-sse_0jdsfef._.js`; same built installation/date |
| `hermes-chat` | `/home/rocco/.hermes/hermes-agent/agent/transports/chat_completions.py`; runtime HEAD `b3399c1`, 2026-09-08 |
| `hermes-helper` | `/home/rocco/.hermes/hermes-agent/agent/chat_completion_helpers.py`; runtime HEAD/date above |
| `hermes-compression` | `/home/rocco/.hermes/hermes-agent/agent/conversation_compression.py`; runtime HEAD/date above |
| `hermes-codex` | `/home/rocco/.hermes/hermes-agent/agent/transports/codex.py`; runtime HEAD/date above |
| `hook-adapter` | `harness-ports/bin/hermes-hook-adapter.py`; last commit `569914b`, 2026-09-15 |
| `qwen-unit` | `deploy/qwen.container`; last commit `6dc160f`, 2026-09-16 |
| `qwen-template` | `/home/rocco/qwen-serving/models/Qwen3.8-27B-W4A16-AutoRound/chat_template.jinja`; mtime 2026-09-16 06:19:56+01; host-mounted, not git-tracked here |
| `upstream-lock` | `upstream.lock.yaml`; Hermes pin at lines 10-15 and OmniRoute pin at lines 21-24; last relevant commit `6dc160f`, 2026-09-16 |

## DISCREPANCIES

- The authored premise ended near 13:0xZ; the reproducible fixed cutoff through 13:21Z is 866 local 400s (780 system-first, 86 no-user), not 828/753/75. Later live rows were excluded from Q1-Q4 calculations.
- The premise classified 416 logger-head-truncated artifacts as exact no-system/no-user shapes. The `_omniroute_truncated_array` marker proves that their leading messages were omitted. They are reported as UNSURE, not as exact shapes.
- The premise says 55 handoff rows today. At this lane's fixed cutoff, the live `context_handoffs` table had 21 rows generated today. The table is unique/upserted per `(session_id, combo_name)`, so it is not an append-only event count.
- The premise associates handoff with `context_cache_protection`; both local combos have that setting `0`. The built runtime has a separate enabled universal-handoff path, while cache protection controls pinning/history recording.
- The premise calls no-system requests a Hermes builder path. Complete provider-request evidence instead shows OmniRoute compression markers and double-system assembly; the 416 apparent no-system bodies are truncated logs. No Hermes no-system call path was matched to a complete rejected artifact.
- The premise says pinned Hermes 0.21.0/`527da60` is the profile runtime. `hermes` resolves to an editable 0.21.1 tree at `b3399c1`; the pinned checkout remains `527da60`. Runtime behavior was cited from `b3399c1`, and pin drift is first-class.
- The template is not inside the immutable image layer and no `--chat-template` is passed. It comes from the host model directory mounted at `/app/models`.
- `request_detail_logs` has no full body for the calls. Summary artifacts preserve top-level transformed `requestBody` but cap nested pipeline bodies and long arrays, so exact first-producer attribution is impossible for the truncated subset.
- `report_lint` final: `report_lint: 29 refs — OK 26, NEAR 3, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## NOT-DONE

- No repair, mutation, model call, service restart, configuration/profile edit, `podman exec` against the live container, or outward action. Read-only `podman run --rm` inspected the pinned image filesystem.
- No causal estimate that all 400s would become successful local completions. The 92.93% value is explicitly an upper bound.
- No exact body recovery for 416 head-truncated rejected artifacts.
- No verified reversible mapping between `context_handoffs.session_id` and `call_logs.session_tag`; only time/shape association is available.
- No claim that changing the Qwen template is safe for model quality or tool-call grammar; that requires a separate adversarial test lane.
- No gate verdict. This evidence report is for the coordinator and remains a proposal until independent review.
