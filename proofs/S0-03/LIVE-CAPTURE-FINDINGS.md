# S0-03 live-capture findings (coordinator, 2026-09-18)

The first live capture of the S0-03 legs on the PC (evidence at
`~/agent-factory/proofs/S0-03/evidence`, codex_responses profile) exposed **two real,
independent defects**. Both were invisible to the synthetic-fixture test suite (rounds O2–O4,
8/8 green) because the fixtures encoded the builder's *assumed* OmniRoute/Hermes behaviour, never
a live row. This is the "live run is the real proof; live failures are FINDINGS" principle
working: the gate passed on fiction. **Nothing is minted; S0-03 stays BLOCKED with the exact root
causes below.**

Every fact here is a primary-source probe from the 2026-09-18 session (the live `call_logs` DB
read-only/immutable, the captured bundle, and the pinned hermes-agent 0.21.0 source at
`/home/rocco/s0-01-pinned/hermes-agent`). Redaction: no key value, bridge token, or secret was
read, printed, or copied (AF-AP-39).

---

## Blocker 1 — leg B never completes a round trip (the PRIMARY blocker)

**Symptom.** The hermes leg B timeline (`hermes/timeline.jsonl`) is 11 frames:
`initialize`, `session/new`, 5×`session/update`, `session/prompt`, `end_turn` — **zero
`tool_call`, zero `completed`**. Frame [8] is an `agent_message_chunk`:

> `HTTP 401: No active credentials for provider: s0-03-omniroute.`

A wide `call_logs` search (2026-09-18 10:54:29 → 11:10) shows **only the direct-leg row** — Hermes
made **zero** upstream model calls during leg B. No round trip happened.

**Root cause (pinned hermes-agent 0.21.0, primary source).** The proof profile
(`proofs/S0-03/hermes/config.yaml`) declares its provider as a **bare name** and references it as
`model.provider: s0-03-omniroute` / `model.default: s0-03-omniroute/agentfactory-build`. The
pinned Hermes requires the **`custom:` prefix** for a custom OpenAI-compatible aggregator provider:

- `hermes_cli/doctor.py:1636-1637`: *"a named `custom:<name>` that fronts an OpenAI-compatible
  aggregator … **requires the prefix**."*
- `hermes_cli/auth.py:1681`: `if normalized.startswith("custom:")` gates the custom-credential path.
- `hermes_cli/model_switch.py:2208`: emits *"Could not resolve credentials for provider …"* when
  the name resolves to no active credential.

Without the prefix Hermes treats `s0-03-omniroute` as a *known* provider, finds no active
credential for it, and returns the 401 above **before sending anything upstream**.
`proofs/S0-01/tools/pc/pc_launch.py:261` **does** inject `OMNIROUTE_API_KEY` into the launch env
(and refuses an empty value at :275-276), so the key is present — the failure is provider-name
resolution, not a missing key.

**The proven-working reference: the owner's live profile** (`~/.hermes/profiles/agentfactory/config.yaml`,
authenticates to the same OmniRoute daily):

| | owner's working profile | proof profile (401) |
|---|---|---|
| `model.provider` | `custom:omniroute-fedora` (**`custom:` prefix**) | `s0-03-omniroute` (bare) |
| provider-block keys | `api`, `transport: openai_chat`, `key_env`, `discover_models: true` | `base_url`, `api_mode: codex_responses`, `key_env`, `extra_headers` |
| credential | inline `model.api_key` **and** `key_env` | `key_env` only |

**Fix direction — the source-only "confirmed" was FALSIFIED by the live run (2026-09-18); the
credential activation is UNRESOLVED.** An earlier revision of this doc claimed "key_env-only
authenticates, confirmed from source, self-contained." **Four live re-captures on the PC disprove
it** — the live run is the real proof, and it caught the wrong claim before any mint. The `custom:`
prefix IS necessary (without it the bare name never resolves — `doctor.py:1636-1637`; `auth.py:1681`)
but it is NOT sufficient. Every attempt 401s `HTTP 401: No active credentials for provider:
custom:s0-03-omniroute` and makes ZERO upstream calls:
- (1) `custom:` + provider-block `base_url` + `key_env` + `api_mode: codex_responses`;
- (2) same, base_url corrected; (3) `custom:` + provider-block `api`;
- (4) S0-01's exact working structure — model-level `base_url`, `api_mode: chat_completions`,
  provider block `api`/`name`/`key_env`/`default_model`/`discover_models`.
`OMNIROUTE_API_KEY` IS in hermes-acp's environ in every attempt (verified from the env-names record).

**The split, precisely.** `resolve_runtime_provider` (the CLI resolver) DOES resolve `key_env` from
the environ with this config (verified by an isolated in-process probe — even for the bare name;
`runtime_provider.py:1372` is an env candidate). But the buzz-acp → hermes-acp ACP agent path uses a
DIFFERENT "active credentials" check that key_env does not satisfy. hermes-acp advertises a `custom`
authMethod ("the currently configured custom runtime credentials") and buzz-acp performs NO ACP
`authenticate` handshake (none in the timeline, none in the buzz source) — so a config-resolvable key
is not an ACTIVE credential for the ACP agent.

**S0-01 is NOT a valid credential reference.** Its `.hermes-home/auth.json` has `providers: {}` and
only a copilot pool row — NO omniroute credential — and its route is the SCRIPTED backend
(`s0-01-scripted/s0-01-pong`), which does not exercise the real-combo client-auth that
`agentfactory-build` needs. The owner's live `agentfactory-build` lanes DO authenticate through this
ACP path, but via an INLINE `model.api_key`, which the proof's `_walk_credentials` screen forbids in
a committed artifact.

**FIX DIRECTION (next increment, UNVERIFIED — a real blocker, not a confirmed fix).** Most promising:
populate an `auth.json` credential pool in the EPHEMERAL launch home (the `--profile` dir) from the
env key — read in place, written 0600, NEVER committed — so the ACP agent sees an ACTIVE credential
while the committed `config.yaml` stays key-free (satisfying both the ACP path and the credential
screen). Open: the auth.json credential-pool format for a custom provider, and whether `hermes auth
add` can populate it non-interactively. If that does not pan out it is an owner-facing step (register
the credential, or sanction a launch-only key the checker treats specially). **This may block S0-03
until resolved.**

This also touches conjunct (v) `check_transport`: it currently pins `api_mode == 'codex_responses'`
literally. Two realigns: (a) the pinned Hermes reads `api_mode` **or** `transport` off the entry
(`model_switch.py:202`; `providers/base.py:44` defaults `chat_completions`), so read the alias, not
a single key; (b) per ADR 0002 (amended, task #35: "every proof asserts and records the wire mode
it OBSERVES rather than assuming one"), conjunct (v) should RECORD the observed mode and assert it
is one of the permitted set (`chat_completions` | `codex_responses`), not hard-pin one — leg A
already proves the `/v1/responses` path for seed A1, so leg B may legitimately run the owner's
proven `chat_completions` transport.

---

## Blocker 2 — the call_logs identity instrument (conjunct iii) is built on a fictional schema

Conjunct (iii) is the **load-bearing** independent identity assertion (the checker's own docstring,
lines 18-44: response `model` can be echoed to the client-requested id, so an independent instrument
is required against the stub-drift hollow green). The instrument is **valuable and correct in
principle** — but every binding column it uses diverges from the live `call_logs` schema:

1. **`response_id` is a dead column.** 0 non-null across **all 40,230 rows** (every path). The
   direct-leg binding `WHERE response_id = <the streamed resp id>` can **never** match.
2. **Route match is on the wrong column.** The checker matches `requested_model == route_id`
   (`agentfactory-build`). Live, the route/combo name lives in **`combo_name`**; `requested_model`
   holds the *resolved* ref `codex/gpt-5.6-sol-ultra`. Both the direct query and the hermes window
   query filter on `requested_model='agentfactory-build'` → both return 0 rows. This single
   mis-binding fully explains the captured `row_counts {direct:0, hermes:0}`; the rows exist, the
   query excludes them.
3. **Cross-instrument model equality breaks.** The response body streams `model: gpt-5.6-sol`;
   `call_logs.model` is `gpt-5.6-sol-ultra` (a suffix normalization). The check
   `call_logs.model == response.model` (checker ~:592) fails on a real bundle.

**The real, stronger binding (from the direct leg's own client-visible response headers).** OmniRoute
returns, in the direct.json `response_headers`:

- `x-omniroute-request-id: 1789728867903-697c55` = the `call_logs` row **primary key `id`**
- `x-correlation-id: 1bdb062d-…` = `call_logs.correlation_id`
- `x-omniroute-model: gpt-5.6-sol-ultra` = `call_logs.model` (resolved)
- `x-omniroute-provider: cx` = the non-stub provider fingerprint (`call_logs.provider='codex'`)

So the direct row binds by **`id == x-omniroute-request-id`** — an always-populated,
OmniRoute-generated, client-visible primary key — which is *stronger* than the dead `response_id`.
Route match becomes **`combo_name == route_id`**; the non-stub fingerprint is **`provider` not in
the stub set** (real value `codex`); the resolved-model cross-check compares `call_logs.model`
against the `x-omniroute-model` header (both `gpt-5.6-sol-ultra`), not the normalized body model.

**Hermes-leg binding is unresolved and must NOT be redesigned against fiction.** `x-omniroute-session-id`
= the leg's nonce2 was **not** recorded as `session_tag` on any row (Hermes either does not forward
the header, or OmniRoute records its own conv id — session_tag was non-null on only 2 of the last
500 rows). The correct hermes-leg binding can only be designed **after leg B produces a real row**
(blocker 1 fixed); candidates are (a) a Hermes-side request-id capture, or (b) window + `combo_name`
uniqueness. Designing it now would repeat the exact fixtures-as-mirror error.

---

## Reconciliation with the seed and ADR (no change to the contract)

- Seed A1 (`seeds/seed-stage0-v1.yaml:390`) pins a **`/v1/responses`** request (codex_responses /
  Responses API). The **direct leg proves this works live**: 200, real streamed text, resolved
  upstream model `gpt-5.6-sol`, provider `codex`. codex_responses at the OmniRoute boundary is fine.
- ADR 0002 (amended, task #35): chat_completions is the live default, **codex_responses permitted
  per route for Codex-capable models**. S0-03 is deliberately the per-route Responses-API proof —
  no transport change is warranted. (My pre-diagnosis plan to switch leg A to chat_completions was
  **wrong** and is abandoned.)
- Seed A2 "non-stub fingerprint" is satisfiable: the direct row's `provider='codex'`, bound by the
  request-id, is the independent non-stub instrument. Conjunct (iii) is realigned, **not dropped**.

---

## What must happen before S0-03 mints (ordered; nothing minted until all hold)

1. **Fix leg B (blocker 1) — UNRESOLVED, the credential activation (see the corrected fix direction
   above).** The `custom:` prefix is necessary but not sufficient; four live re-captures 401 despite
   `OMNIROUTE_API_KEY` in the environ and a config `resolve_runtime_provider` resolves in-process.
   Next: populate an ephemeral-launch-home `auth.json` credential pool from the env key (0600, never
   committed) so the ACP agent's `custom` authMethod sees an ACTIVE credential; determine the pool
   format / whether `hermes auth add` populates it non-interactively; else surface to the owner.
   Only once leg B completes a real `tool_call`→`completed` round trip AND logs a real `call_logs`
   row (and the runner's DONE condition asserts the round trip, not bare end_turn — AF-AP-100) does
   the rest proceed.
2. **Realign conjunct (iii) + the direct probe (blocker 2)** — record the `x-omniroute-*` identity
   headers as first-class direct.json fields; bind the direct row by `id == x-omniroute-request-id`,
   match by `combo_name`, cross-check the resolved model via `x-omniroute-model`, keep the non-stub
   `provider` assertion. Design the hermes-leg binding from the real leg-B row.
3. **PRE-MINT regression (AF-AP-36)** — a committed hostile bundle for each realigned binding
   (mismatched request-id; a stub `provider`; a `combo_name` mismatch; a normalized-model mismatch)
   must be a failing test **before** re-mint.
4. **Class flip + mint** — blocked_credential → execution_proof, remove `blocked.json`, mint,
   regenerate all attested minted results (registry is an attested input; re-stales `accepted/S0-11`
   by design → owner re-sign), ledger-gen, tests, ledger + task #17.

## Anti-patterns this exposed (for the registry)

- **Fixtures-as-mirror across a whole gate:** an evidence-cross-checking instrument whose binding
  columns were authored from an assumed upstream schema, never one live row — passed every synthetic
  round, cannot bind to any real row. The general rule: an evidence checker that reads an external
  system's records gets **at least one real row of that system** pinned as a fixture before it is
  trusted (the two sanctioned deterministic stubs excepted, and those sit behind real OmniRoute).
- **A launcher built for proof A silently mis-serves proof B's provider:** the S0-01 launcher's
  credential path was validated for S0-01's provider setup; S0-03's bespoke provider name fails
  Hermes credential resolution and the launcher does not surface it (leg B "succeeds" to end_turn
  with a 401 in the transcript). The runner's wait condition (end_turn) is not a success signal — it
  must also assert a real tool-call round trip before the bundle is considered captured.
