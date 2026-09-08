# PROVENANCE — evidence-credential-absent

Synthetic bundle, committed as a NEGATIVE control. AF-AP-42 (fixture-shaped hollow green) demands
that every file say where its shape came from and, where the shape is not yet proven against a
live producer, that it say so instead of implying it is.

| file | shape derived from | proven against a live capture? |
|---|---|---|
| `direct/direct.json` | the writer itself — `proofs/S0-03/tools/pc/direct_responses_probe.py` builds exactly these keys. Event shapes from the pinned OmniRoute `488f57e9`: `open-sse/translator/response/openai-responses.ts:199-200` (`state.model` taken from the upstream `chunk.model`), `:217` + `:229` (stamped onto `response.created`/`response.in_progress`) and `:441-442` (`response.output_text.delta`). The `X-OmniRoute-Compression` value form `off; source=request-header` is `open-sse/services/compression/planResolution.ts:41` + `:60-62`. The 401 body is `src/server/authz/pipeline.ts:84-92` rendering `src/server/authz/policies/clientApi.ts:77`. | **NO** — leg A has not run. `NOT proven against a live capture` until the PC leg runs. |
| `hermes/timeline.jsonl` | entry envelope (`seq`/`dir`/`t_utc`/`t_mono_ns`/`frame`) from the REAL corpus at `S0_01_REAL_LEG_DIR` (`/root/s0-01-realleg/golden/*/timeline.jsonl`), read this session. `tool_call` / `tool_call_update` payloads from the committed protocol schema `proofs/S0-01/fixtures/acp-schema-v1.json` (`$defs.ToolCall`, `.ToolCallUpdate`, `.ToolCallStatus`, `.ToolKind`, `.ToolCallContent`); `toolCallId` form `tc-<12 hex>` and title form `terminal: <cmd>` from hermes-agent `527da608` `acp_adapter/tools.py:90-92`, `:96-101`. | envelope **YES**; tool-call frames **NO** — *no golden leg carries a tool-call turn* (checked: the five golden legs contain only `agent_message_chunk`, `available_commands_update`, `session_info_update`, `usage_update`). `NOT proven against a live capture` until the PC leg runs. |
| `hermes/hermes-env-names.json` | the writer itself — `proofs/S0-03/tools/pc/hermes_env_names.py`. | **NO** — names only, never values. |
| `hermes/profile.yaml` | byte-identical to `proofs/S0-03/hermes/config.yaml`, which the runner copies into the bundle. | n/a — it is the committed template. |
| `omniroute-requests.json` | the writer itself — `proofs/S0-03/tools/pc/collect_leg.sh`. Column set from OmniRoute `488f57e9` `src/lib/usage/callLogs.ts:564-572` (`call_logs`: `model`, `requested_model`, `provider`, `connection_id`, `combo_name`, `status`, `path`, `method`). | **NO** — the `call_logs` rows have not been read on the PC. |

## What this bundle is for

The seed's KILL SWITCH (`seeds/seed-stage0-v1.yaml:399-401`): disable the credential and the proof must go RED with the exact reason `blocked: credential_absent`.

Two independent signals are present, either of which is decisive: the Hermes environ carries NO `OMNIROUTE_API_KEY`, and OmniRoute answered the direct leg 401. The timeline shows the consequence the seed's third assertion names: the prompt turn FAILS with the model error and NO agent text is produced — Hermes does not fall back to a direct provider, because the env record proves there is no upstream key to fall back to.

Boundary: this is the ENV and BEHAVIOUR half of "no direct fallback". The network-level proof that Hermes *could not* reach a provider even if it tried belongs to S0-05, not here.
