# S0-03 live-capture findings (coordinator, 2026-09-18)

Live capture of the S0-03 legs on the PC (`~/agent-factory/proofs/S0-03/evidence`) exposed **two
real, independent defects**, both invisible to the synthetic-fixture suite (rounds O2–O4, 8/8
green) because the fixtures encoded the builder's *assumed* OmniRoute/Hermes behaviour, never a
live row. This is "the live run is the real proof; live failures are FINDINGS" working: the gate
passed on fiction, and the first real run broke it.

**STATUS 2026-09-18 (evening): BOTH ROOT CAUSES FOUND; blocker 1 FIXED and the fix PROVEN LIVE
(a real tool-call round trip); blocker 2 fully characterised against real rows. The tooling
realign + re-capture + mint are the ordered remaining work. Nothing minted yet.**

Every fact here is a primary-source probe from the 2026-09-18 session (the live `call_logs` DB
read-only, the captured bundle, the pinned hermes-agent 0.21.0 source at
`/home/rocco/s0-01-pinned/hermes-agent`, and in-process resolver probes). Redaction: no key value,
bridge token, or secret was read, printed, or copied (AF-AP-39).

---

## Blocker 1 — leg B never completed a round trip — ROOT CAUSE FOUND, FIXED, PROVEN LIVE

**Symptom (5 failed captures).** The hermes leg-B timeline was 11 frames (`initialize`,
`session/new`, updates, `session/prompt`, `end_turn`), **zero `tool_call`**, and the single
`agent_message_chunk` was:

> `HTTP 401: No active credentials for provider: custom:s0-03-omniroute.`

**The wrong track (recorded so it is not re-run).** The message reads like a Hermes credential
failure, so five config/credential shapes were tried — bare provider; `custom:` prefix + `key_env`;
provider-block `base_url`; S0-01's exact structure; an `auth.json` credential pool written by
`hermes auth add`. **All five produced the identical 401.** Two in-process probes then falsified the
credential-failure hypothesis outright: `resolve_runtime_provider()` (the exact function
`acp_adapter/auth.py:22` calls) **resolves the api_key cleanly** for every one of these shapes
(key_env resolves from the environ; `api`/`base_url` resolve). Hermes-side credential resolution
was never the problem.

**ROOT CAUSE (proven live, 2026-09-18).** The 401 is **OmniRoute's**, not Hermes'. Hermes forwards
`model.default` **verbatim** as the model name on the wire. The proof profile set
`model.default: custom:s0-03-omniroute/agentfactory-build` — carrying the *Hermes-internal* provider
prefix. OmniRoute parses a leading `custom:s0-03-omniroute/` as a **provider** it has no connection
for and rejects it. A direct 3-way `chat/completions` probe with the real key isolates it exactly:

| model sent to OmniRoute | result |
|---|---|
| `agentfactory-build` (bare combo id) | **200**, real `gpt-5.6-sol-ultra` |
| `custom:s0-03-omniroute/agentfactory-build` | **401 "No active credentials for provider: custom:s0-03-omniroute."** — the exact leg-B error |
| `custom:s0-03-omniroute` | 400 "Unable to determine provider for model … Use a provider/model prefix … or ensure the model is added as a combo entry." |

**THE FIX.** The provider prefix belongs on `model.provider` (Hermes selects the provider config
from it) and must **never** appear in `model.default` (which reaches OmniRoute). So:

- `model.provider: custom:s0-03-omniroute` — the `custom:` prefix is required for Hermes to resolve
  a custom OpenAI-compatible aggregator provider (`doctor.py:1636-1637`, `auth.py:1681`).
- `model.default: agentfactory-build` — the **bare** OmniRoute combo id, no `custom:<name>/` prefix.

In-process, `resolve_runtime_provider()` on this shape returns `provider=custom`, api_key PRESENT,
`model=agentfactory-build`, source `custom_provider:S0-03 OmniRoute`. The runner reads the route id
back from `model.default` (split on `/`, `[-1]`) → `agentfactory-build`, unchanged.

**PROVEN LIVE (config v4, 2026-09-18).** Leg B timeline is now **33 frames**:
`tool_call: 2`, `tool_call_update: 2` (one `completed`), `agent_thought_chunk: 8`,
`agent_message_chunk: 10`, terminal `end_turn`. The first tool call is
`terminal: printf e4d3442ad554b25a` → `completed`; the agent's final message is the nonce
`e4d3442ad554b25a`. That is a real Hermes tool-call round trip driven by the real model through
real OmniRoute — seed A1's "completes a real Hermes tool-call round trip", live.

**The earlier `auth.json` / credential-activation narrative in prior revisions of this doc is
SUPERSEDED and wrong.** The ACP path resolves the key from `key_env`; there is no missing-active-
credential problem. No inline `model.api_key` is needed — the committed config stays key-free (A3's
`_walk_credentials` screen holds) and `key_env` (the NAME only) carries the credential, read from
the launch environ that `pc_launch.py:261` injects.

**Wire mode.** The proven-working shape uses `api_mode: chat_completions` (the owner's live
transport). Per ADR 0002 (amended, task #35: "every proof asserts and records the wire mode it
OBSERVES"), leg B **records** `chat_completions`; leg A independently exercises `/v1/responses`
(codex_responses) for seed A1. Conjunct (v) must record-and-assert-in-permitted-set, never hard-pin
`codex_responses` (its current literal pin would RED this real bundle — a blocker-2 realign item).

---

## Blocker 2 — the call_logs identity instrument (conjunct iii + collect) is built on a dead schema

Conjunct (iii) is the load-bearing independent identity assertion (response `model` can be echoed
to the client-requested id, so an independent instrument is required against stub-drift). The
instrument is correct in principle but every binding column diverged from the live schema. With leg
B now producing real rows, the real bindings are captured directly:

**The real leg-B rows (session_tag = the injected nonce).** The runner injects the leg's nonce2 as
`x-omniroute-session-id` (config `extra_headers`); OmniRoute records it as `call_logs.session_tag`.
The round trip produced **3 rows**, all:
`combo_name=agentfactory-build`, `status=200`, `model=gpt-5.6-sol-ultra`,
`requested_model=codex/gpt-5.6-sol-ultra`, `provider=codex`, `session_tag=e4d3442ad554b25a`,
`response_id` EMPTY. (Three because the round trip made three model calls: prompt→tool decision,
tool-result→answer, and one further turn.)

The dead columns the O2/O3 checker binds on:
1. **`response_id` is dead** — 0 non-null across all rows; any `WHERE response_id=…` never matches.
2. **Route lives in `combo_name`**, not `requested_model`. The checker filtered
   `requested_model='agentfactory-build'` → 0 rows; `requested_model` holds the resolved ref
   `codex/gpt-5.6-sol-ultra`. This single mis-binding fully explains the captured
   `omniroute-requests {direct:0, hermes:0}` — the rows exist, the query excludes them.
3. **Model equality** must compare `call_logs.model` (`gpt-5.6-sol-ultra`) to the `x-omniroute-model`
   response header (same value), not the body's normalized `gpt-5.6-sol`.

**The real, stronger bindings (both legs).**
- **Direct leg** binds by the client-visible response headers OmniRoute returns:
  `x-omniroute-request-id == call_logs.id` (always-populated PK), `x-correlation-id ==
  correlation_id`, `x-omniroute-model == call_logs.model` (resolved), `x-omniroute-provider: cx` ⇒
  `provider='codex'` (the non-stub fingerprint). Stronger than the dead `response_id`.
- **Hermes leg** binds by **`session_tag == the leg nonce2`** + `combo_name == route_id` +
  `provider` not in the stub set + `status=200`. (The earlier "session_tag never recorded" note was
  an artefact of blocker 1 — before the fix leg B made no call, so no row carried the tag. With the
  fix, the tag is recorded on every leg-B row.)

---

## Reconciliation with the seed and ADR (no contract change)

- Seed A1 pins a `/v1/responses` request: the **direct leg proves it live** (200, streamed text,
  resolved `gpt-5.6-sol`, provider `codex`). Leg B proves the **round-trip** half and records its
  observed transport (`chat_completions`) per ADR 0002 (amended).
- Seed A2 "non-stub fingerprint": the row's `provider='codex'`, request-id-bound, is the independent
  non-stub instrument. Conjunct (iii) is realigned, **not dropped**.

---

## Ordered remaining work (nothing minted until all hold)

1. **Config fix — DONE, proven live.** `model.default: agentfactory-build` (bare) +
   `model.provider: custom:s0-03-omniroute`, `api_mode: chat_completions`, provider block
   `api`/`key_env`/`transport: openai_chat`. Port to the committed `proofs/S0-03/hermes/config.yaml`.
2. **Runner collect step (`collect_leg.sh`) realign** — query `call_logs` by
   `session_tag == nonce2` + `combo_name == route_id` (hermes leg) and by
   `id == x-omniroute-request-id` (direct leg); drop `response_id` and the `requested_model==route`
   filter. Also: the runner's DONE condition must assert a real `tool_call`→`completed`, not bare
   `end_turn` (AF-AP-100).
3. **Checker conjunct (iii)+(v) realign** — bind on the real columns above; record-and-assert the
   observed wire mode in the permitted set, not a `codex_responses` literal; the direct probe records
   the `x-omniroute-*` headers as first-class `direct.json` fields.
4. **PRE-MINT regression (AF-AP-36)** — a committed hostile bundle per realigned binding (wrong
   request-id; stub `provider`; `combo_name` mismatch; normalized-model mismatch; missing session_tag)
   is a FAILING test before re-mint.
5. **Re-capture on the PC with the final tools** → a complete, mintable bundle.
6. **Class flip + mint** — blocked_credential → execution_proof, remove `blocked.json`, mint,
   regenerate all attested minted results (registry is an attested input → re-stales `accepted/S0-11`
   by design → owner re-sign), ledger-gen, tests, ledger + task #17.

## Anti-patterns this exposed (registry)

- **AF-AP-103 — a Hermes-internal provider prefix leaked into the wire model name.** A custom
  aggregator provider's `custom:<name>/` selector prefix belongs only on `model.provider`; put it in
  `model.default` and Hermes forwards it verbatim as the model, and the aggregator (OmniRoute) rejects
  the unknown provider with a 401 that *reads* like a local credential failure. Rule: the model id on
  the wire is the aggregator's bare combo/route id; the provider selector never appears in it. A
  provider-auth 401 whose message names your *own* internal provider label is this class — probe the
  aggregator directly with the bare vs prefixed model before touching credentials.
- **Fixtures-as-mirror across a whole gate:** an evidence-cross-checking instrument whose binding
  columns were authored from an assumed upstream schema, never one live row — passed every synthetic
  round, bound to no real row. Rule: an evidence checker that reads an external system gets at least
  one real row of that system pinned as a fixture before it is trusted.
- **end_turn is not a success signal:** the runner's wait condition (`end_turn`) fired on a 401
  surfaced as an `agent_message_chunk` — it must assert a real tool-call round trip (AF-AP-100).
