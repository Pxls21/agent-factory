# T92 — per-lane provenance binding: the seam, MEASURED 2026-09-22 13:3xZ-13:5xZ (coordinator, read-only over the bridge)

Every line below was pasted from a probe on the PC (OmniRoute v16.3.1 at
`/home/rocco/.omniroute-migration-npm/node_modules/omniroute`, the running Hermes at
`/home/rocco/.hermes/hermes-agent` = git `b3399c1396 2026-09-08`, the OmniRoute storage
`/home/rocco/.omniroute-migrated/storage.sqlite`). Nothing here is remembered.

## 1. What OmniRoute does with a client session header (the sink)

Chat route (minified `dist/.build/next/server/chunks/ssr/*.js`, two copies = the two chat endpoints):

```
let eG=t.headers.get("x-omniroute-session-id")?.trim()||null,eW=null;
try{({conversationId:eW}=await (0,Y.resolveConversationId)({body:E,model:ee,apiKeyId:ek?.id??null,clientSessionIdHeader:eG,correlationId:U}))}
```

`resolveConversationId` (same build):

```
async function s(e){ if(e.clientSessionIdHeader&&e.clientSessionIdHeader.trim()){
  let t=e.clientSessionIdHeader.trim().slice(0,128);
  return(0,r.touchOrCreateExternalConversation)(t,{apiKeyId:e.apiKeyId}),{conversationId:t,isNewConversation:!1}}
  … otherwise: fingerprint = sha(apiKeyId|model|sorted tool names) + a per-turn content-hash chain over the
  non-system messages (`d=c.filter(e=>"system"!==e.role)`) → agentic_conversations / conversation_turn_nodes …
```

- With the header: the conversation id IS the header value (≤ 128 chars), verbatim. It lands in
  `call_logs.session_tag` (today's rows carry `conv_<uuid4>` = the fingerprint path's ids —
  `createAgenticConversation` mints `` `conv_${v4()}` ``).
- Without the header (today): a new `conv_*` id whenever the non-system message chain does not
  match a known conversation — a RESUME (new first user message), a fallback-loop call (no system
  message, different body) and a compression rotation each mint a new tag. Measured 10:50Z-13:33Z
  (hermes key): 36 `agentic_conversations`, 41 tags in `call_logs`; the four live lanes + B8/T91/K1
  own 17 of them by first-user-message content, 19 tags are fallback-loop bodies (`msgs=129`, no
  system message, empty first user text) that cannot be bound by content at all.
- A second, separate OmniRoute session id (`generateSessionId`, `ext:<header>` from
  `x-claude-code-session-id`/`x-codex-session-id`/`x-session-id`/`x_session_id`/`session-id`/
  `session_id`/`x-omniroute-session-id`/`x-omniroute-session`, else `model:|provider:|sys:|user0:|tools`)
  feeds the per-key session LIMIT (`checkSessionLimit`), not the call log. Only
  `x-omniroute-session-id` reaches `resolveConversationId`.

Storage (read-only `pragma table_info`): `call_logs` has `session_tag`, `correlation_id`
(set on every row today: 3758/3758), `api_key_name`, `combo_name`, `combo_step_id`, `provider`,
`status`, `artifact_relpath`, `has_request_body` (1 on 3758/3758). `agentic_conversations(id,
api_key_id, fingerprint_hash, last_message_count, last_messages_hash, turn_count, first_seen_at,
last_seen_at)` = 1370 rows; `conversation_turn_nodes` = 120474 rows.

## 2. What Hermes can put on the wire (the source)

- `agent/agent_init.py:891-916` `_apply_openai_header_policy`: OpenRouter beta header →
  `model.default_headers` (`agent._apply_user_default_headers`, `agent/auxiliary_client.py:825-839`:
  `model.default_headers` + `model.extra_headers`) → `apply_custom_provider_extra_headers_to_client_kwargs`
  (`hermes_cli/config_providers.py:466-478`: `providers.<entry>.extra_headers` of the first
  route-matching entry, merged onto the OpenAI client's `default_headers` — applied LAST, "most
  specific level wins").
- NO env-var knob for headers: `grep -rnE 'environ.*HEADER|HEADER.*environ|getenv\("HERMES_[A-Z_]*HEADER'`
  over `agent/` + `hermes_cli/` (tests excluded) = 0 hits; no `expandvars` on config values.
- NO CLI flag: `hermes --help` has `-m/--provider/--reasoning/-t/-p`, nothing for headers.
- The chat transport (`agent/transports/chat_completions.py:70-112`) sends NO per-request session
  header: `session_id` only feeds `prompt_cache_key` (content hash + cache scope), and only when
  `supports_prompt_cache_key`; today's logged request bodies carry `messages, model, stream,
  stream_options, tools` (no `prompt_cache_key`, no `user`). Only the codex transport
  (`agent/transports/codex.py:617-623`) merges a conversation header (`x-grok-conv-id`).
- The dispatcher launches `hermes -p ${HERMES_PROFILE:-agentfactory} --in "$TREE" --no-restore-cwd
  -z … -m "$RUN_MODEL" --reasoning "$RUN_EFFORT" --accept-hooks --usage-file …`
  (`harness-ports/bin/pc-lane.sh:429-434`); `HERMES_PROFILE` is already a documented knob (:20)
  and the session export reads the state.db of that profile (:495).
- The lane profile: ONE profile `agentfactory` (`/home/rocco/.hermes/profiles/agentfactory`,
  config.yaml 7737 B: `model.provider: custom:omniroute-fedora`, `base_url
  http://127.0.0.1:20128/v1`, `api_mode: chat_completions`, `providers.omniroute-fedora`
  (:277-284, `transport: openai_chat`, `discover_models: true`, NO `extra_headers`); state.db
  438 MB shared by every lane; skills 10 MB; the sticky default profile is `default`, the lanes
  select `agentfactory` by `-p`).
- `hermes profile create NAME [--clone] [--clone-all] [--clone-from SOURCE] [--no-alias]
  [--no-skills]`: `--clone` copies config.yaml, `.env`, SOUL.md and skills (not state.db);
  `--clone-from agentfactory` implies `--clone`; `delete` exists.

## 3. The design this measures out (for the brief; PIN after T90-R1 lands on the dispatcher file)

Per lane: `hermes profile create <lane-profile> --clone-from agentfactory --no-alias`, inject
`extra_headers: {x-omniroute-session-id: <lane-id>}` into the CLONE's `providers.omniroute-fedora`
block (the owner's `agentfactory` config is never touched), launch with `-p <lane-profile>`, export
the session from THAT profile's state.db, delete the profile after the export. Then every call of
the lane — fallback-loop calls and resumes included — carries `session_tag = <lane-id>` and the
harvest (scripts/pc_lane.sh:394-486) keys on `session_tag = '<lane-id>'` instead of a combo-wide
time window: per-lane provider mix EXACT, the "other conversations" caveat gone, D-039(b)'s HYBRID
label lifts on a measured per-lane provider column. Side effect worth its own line: a per-lane
state.db removes the shared-DB contention class (`session_persistence_failed`, 2026-09-08).

NOT run here: the end-to-end wire proof (a throwaway profile + one short local-route call + the
tag read back) — the sandbox classifier refused the coordinator's throwaway-profile creation on
the owner's Hermes home (13:5xZ, "Modify Shared Resources"); it is the lane's item 1, run by the
lane user on the PC with the profile removed in the same step, or an owner-run command.
