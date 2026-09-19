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
- **Direct leg** — the `x-omniroute-request-id == call_logs.id` binding stated here was
  **SUPERSEDED / FALSIFIED 2026-09-19 (see Blocker 4):** on the live 3.8.50 instance
  `x-omniroute-request-id` is a UUID and `call_logs.id` is an epoch-suffix key — different id-spaces,
  never equal; a streaming `/v1/responses` returns no `x-omniroute-*` headers at all. The real direct
  binding is the FRESH NONCE recorded in OmniRoute's artifact `requestBody.input` (Blocker 4),
  mirroring the hermes leg's `session_tag == nonce2`.
- **Hermes leg** binds by **`session_tag == the leg nonce2`** + `combo_name == route_id`
  + `provider` not in the stub set + `status=200`. The nonce2 is FRESH per leg, so every row
  carrying it is unambiguously this leg's — the attribution is the tag, not window-uniqueness.

**CHECKER RE-DESIGN — the round trip makes MANY model calls, not one.** The load-bearing gate
changes here are semantic, not cosmetic; the O2/O3 checker + collect_leg.sh assumed one upstream
call per leg:
1. **Route filter is on the wrong column (the root of `{direct:0, hermes:0}`).** `collect_leg.sh`
   (both queries, :137/:145) filters `requested_model = route` — but `requested_model` holds the
   resolved ref `codex/gpt-5.6-sol-ultra`, never the route id. It must filter `combo_name = route`.
   The direct query's second predicate `response_id = <direct.json.id>` is doubly dead — it becomes
   `id = <x-omniroute-request-id header>`.
2. **The "exactly ONE hermes row in the window" rule (`check_identity_route:539`,
   `len(grouped["hermes"]) != 1`) is WRONG for a real round trip.** The proven leg-B round trip
   logged **3** rows (prompt→tool decision, tool-result→answer, one more turn), all
   `session_tag=e4d3442ad554b25a`, all `combo_name=agentfactory-build`, `status=200`,
   `provider=codex`, path `/v1/chat/completions`. Bind the hermes leg to **every** row whose
   `session_tag == nonce2` (≥ 1), validate each (status 200, combo_name, non-stub provider,
   permitted-transport path), and keep the window only as a sanity bound that all tagged rows fall
   within — never a uniqueness rule. The direct leg stays exactly-one, bound by the request-id.
3. **Per-leg transport, recorded not pinned (conjunct v).** `check_transport` pins the profile
   `api_mode == 'codex_responses'` (`:723`, `REQUIRED_API_MODE`) — RED on the proven
   `chat_completions` leg-B profile. Per ADR 0002 (amended) record the observed mode and assert it
   is in the permitted set. The WIRE says which transport ran: the direct row's path is
   `/v1/responses`, the hermes rows' path is `/v1/chat/completions` — the checker reads the path
   per leg, records it, and asserts each is one of the two permitted paths, never one fixed path.
4. **Model cross-check** compares `call_logs.model` (`gpt-5.6-sol-ultra`) to the
   `x-omniroute-model` header (same), NOT `direct.json.model` (the normalized `gpt-5.6-sol`,
   `check_identity_route:592`).

---

## Blocker 3 — the round-trip conjunct (iv) + the runner assertion bind a FICTIONAL tool_call shape (a SECOND fixtures-as-mirror layer, caught by the live re-capture 2026-09-18)

The O4 realign (commit `be083e3`) fixed the call_logs bindings and gated green in the sandbox
(193 passed ×2), but the first live re-capture with the realigned tooling **crashed** and would
have red-ed the checker — because the round-trip parsing (conjunct iv) was built from an ASSUMED
ACP `tool_call` shape, never a real one. The REAL shape (golden, from the live leg-B timeline):

```json
{"sessionUpdate":"tool_call","kind":"execute","locations":[],
 "title":"terminal: printf 3ee033173c9eafc2",
 "content":[{"content":{"text":"$ printf 3ee033173c9eafc2","type":"text"},"type":"content"}],
 "toolCallId":"tc-8d38ea4c7025"}
```
and the completion:
```json
{"sessionUpdate":"tool_call_update","kind":"execute","status":"completed",
 "content":[{"content":{"text":"terminal result\n- **output:** 3ee033173c9eafc2\n- **exit_code:** 0","type":"text"}, ...}],
 "toolCallId":"tc-8d38ea4c7025"}
```

Two real defects the synthetic fixtures hid (both = AF-AP-101 recurring):
1. **Runner AF-AP-100 assertion CRASHES** (`run_s0_03_legs.sh:256`): `update.get("content", {}).get("title", "")`
   — but `content` is a **list** of content blocks and the title is `update["title"]`, not
   `content.title`. Live rc: `AttributeError: 'list' object has no attribute 'get'`. The whole
   re-capture aborts before collect. Fix: read `update.get("title", "")` (and/or the content
   blocks' `content.text`).
2. **Checker conjunct (iv) binds a field that DOES NOT EXIST** (`check_omniroute_roundtrip.py`
   `check_roundtrip:671-677`): it requires `update["rawInput"]["command"] in {printf <nonce>, …}`.
   The real ACP tool_call has **no `rawInput`** — the command is in `title`
   (`terminal: printf <nonce>`) and in `content[].content.text` (`$ printf <nonce>`). Against a real
   bundle `exact_starts` is empty → conjunct (iv) reds. Fix: bind the execute tool_call by
   `kind == "execute"` + the command parsed from `title`/`content[].content.text` matching the
   expected `printf <nonce>` set + a `toolCallId`; then a later `tool_call_update status=completed`
   with the same `toolCallId` whose content contains the nonce (the tool output).

The fix touches: `run_s0_03_legs.sh` (the assertion), `check_omniroute_roundtrip.py`
(`check_roundtrip`), and the fixtures' `hermes/timeline.jsonl` (regenerate the tool_call frames to
the REAL shape — content list + title, no rawInput — so the sandbox tests exercise the real shape).
Then re-capture to validate end-to-end. This is the round-trip half of the "pin a real row before
you trust the checker" rule — the call_logs half was fixed in O4; the ACP-timeline half is this.

## Blocker 4 — the /v1/responses call_logs binding — RESOLVED 2026-09-19 (OmniRoute docs + live measurement on 3.8.50)

The owner directed: read OmniRoute's ACTUAL documentation, not just the source. OmniRoute is a
PUBLIC open-source AI gateway (an OpenAI-compatible multi-provider router). Its public docs + a
later PR ("request-id correlated routing decisions, decision lookup, diagnostics") describe the
intended correlation model; the owner's instance is 3.8.50 and was then probed directly. Docs +
live probe together resolve the binding.

**What the docs say (public OmniRoute + PR #34):** non-streaming `/v1/responses` carries
`X-OmniRoute-Decision-Id`; STREAMING responses are sent BEFORE routing finishes, so their decision
is not in headers — it is "recorded under the id the client receives" and retrieved by a lookup
(`GET /api/omniroute/route/decisions/{id}`, `GET /api/usage/route-explain/{id}`) or the
`routing_decisions` table keyed by `request_id`.

**What the owner's 3.8.50 actually does (live probes 2026-09-19, three captures):**
1. `routing_decisions` table EXISTS in the schema but is EMPTY — PR #34's population is a LATER
   version. The docs' request-id lookup path is NOT available on this instance.
2. NO client-visible header equals any `call_logs` column for `/v1/responses`. On one request:
   `x-request-id=fe09a6be…`, `x-omniroute-request-id=6e455263…`, and the row's
   `correlation_id=a2a3a6f8…` are THREE distinct UUIDs; `call_logs.id` is an epoch-suffix key
   (`1789791165766-9edc2a`). So the O4 binding `call_logs.id == x-omniroute-request-id` cannot hold
   — different id-spaces — which is exactly why it was never validated against a real row (Blocker 2
   asserted it from an assumed schema; falsified here).
3. `call_logs.response_id` == the response body's own `resp_…` id works for NON-streaming rows, but
   is NULL for STREAMING rows, and streaming returns only `x-request-id` in headers (no
   decision/model/provider headers — matching the docs). Seed A1 requires the direct leg to STREAM,
   so `response_id` is unavailable to it.
4. `request_detail_logs` is EMPTY (count 0). The per-request pipeline detail is stored as an
   ARTIFACT FILE (`call_logs.artifact_relpath` → `<DATA_DIR>/call_logs/<YYYY-MM-DD>/<…>_<id>.json`,
   with `has_request_body=1`, `detail_state='ready'`). Its `requestBody` is a dict
   `{model, input, stream, max_output_tokens}`; the client's request text is at `requestBody.input`.

**RESOLUTION — bind the direct leg by its FRESH NONCE, recorded in OmniRoute's artifact requestBody.**
This mirrors the hermes leg exactly (it binds `session_tag == nonce2`, a fresh client nonce OmniRoute
independently records). The direct leg already sends a fresh 16-hex nonce in its `/v1/responses`
`input` (conjunct i already requires that nonce in the streamed text); OmniRoute records that input
verbatim in the row's artifact. The collector selects the `/v1/responses` row (in the direct
window, `combo_name == route`) whose artifact `requestBody` contains the nonce and exports it with a
`recorded_input` field; the checker cross-checks `direct.json.nonce in recorded_input` plus
`combo_name == route`, `provider` non-stub, `status == 200`, permitted path. This is INDEPENDENT
(OmniRoute wrote the artifact), RE-VERIFIABLE in the sandbox (the recorded input travels in the
bundle), and FORGERY-RESISTANT (a fresh client nonce inside the aggregator's own record). VERIFIED
live: streaming row `1789791699678-ec4e47`, `provider=codex`, `combo_name=agentfactory-build`,
`status=200`, `response_id=NULL`, the nonce present at `requestBody.input`.

The `x-omniroute-model` header cross-check (checker ~line 613) is DROPPED for the direct leg — a
streaming `/v1/responses` returns no such header. Direct-leg model identity stays asserted by
conjunct (ii) (`direct.json.model == expected`) and by `call_logs.model` consistency across the
hermes+direct rows (the `models` set stays size 1). The hermes-leg binding (`session_tag == nonce2`)
is unchanged and proven live (3 rows). No seed/ADR contract change: A1 (leg A on `/v1/responses`,
streamed) and A2 (non-stub fingerprint, now via BOTH legs' `provider=codex` rows) both hold.

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
   `session_tag == nonce2` + `combo_name == route_id` (hermes leg, DONE) and, for the direct leg,
   select the `/v1/responses` row (in the direct window, `combo_name == route_id`) whose ARTIFACT
   `requestBody` contains `direct.json.nonce`, exporting a `recorded_input` field (Blocker 4). Drop
   `response_id`, the `requested_model==route` filter, and the dead `id == x-omniroute-request-id`
   direct binding. The runner's DONE condition asserts a real `tool_call`→`completed`, not bare
   `end_turn` (AF-AP-100, DONE in O5).
3. **Checker conjunct (iii)+(v) realign** — hermes rows bound on the real columns (DONE); direct row
   bound by `direct.json.nonce in recorded_input` (Blocker 4); drop the direct-leg `x-omniroute-model`
   header cross-check (a streaming `/v1/responses` returns no such header); record-and-assert the
   observed wire mode in the permitted set, not a `codex_responses` literal.
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
