# Lane O4 — S0-03 checker/collect realign to the REAL OmniRoute bindings

**Authorization.** This is defensive verification work on the owner's own OmniRoute/Hermes system
(the Agent Factory Stage-0 proof pack). Nothing here touches production credentials or external
systems; you edit sandbox tooling + tests + fixtures only.

**PIN:** work on the current HEAD of `claude/soundbox-kit-migration-iz1jwf` (commit `91da566` or
later — it carries the spec). **Do NOT** run any live capture, touch the PC bridge, mint any
artifact, edit `blocked.json`/`result.json`/the registry/the ledger, or take any outward action —
all of that is the coordinator's, AFTER this lands.

## The spec is already written — READ IT FIRST
`proofs/S0-03/LIVE-CAPTURE-FINDINGS.md` (committed) is the authoritative spec. It records the live
root cause (AF-AP-103), the proven fix, and — under "Blocker 2" and "CHECKER RE-DESIGN" — the exact
real `call_logs` bindings with the golden row values. Everything below pins those to files. On any
disagreement, the findings doc's golden values win (they are real primary-source rows).

## Real golden values (pinned from the live 2026-09-18 capture; AF-AP-101)
- Leg-B (hermes) rows — the round trip logged **3** of them, all identical on the binding columns:
  `combo_name=agentfactory-build`, `status=200`, `method=POST`, `path=/v1/chat/completions`,
  `model=gpt-5.6-sol-ultra`, `requested_model=codex/gpt-5.6-sol-ultra`, `provider=codex`,
  `session_tag=e4d3442ad554b25a` (== the leg's `nonce2`), `response_id` EMPTY.
- Direct (leg A) row: `id=1789756168915-60150b` (== the `x-omniroute-request-id` response header),
  `path=/v1/responses`, `status=200`, `model=gpt-5.6-sol-ultra`, `provider=codex`,
  `combo_name=agentfactory-build`.
- The captured `direct.json.response_headers` carries `x-omniroute-request-id`, `x-omniroute-model`
  (`gpt-5.6-sol-ultra`), `x-omniroute-provider` (`cx`), `x-correlation-id`. `direct.json.id` is the
  Responses-API `resp_…` body id — a DIFFERENT thing, do not bind on it.

## The changes (all in one atomic increment; sandbox tests must be green at the end)

### 1. `proofs/S0-03/hermes/config.yaml` — the proven config (replace the whole file)
```yaml
# S0-03 proof-OWNED Hermes provider profile.
# model.default is the BARE OmniRoute combo id, NEVER a custom:<provider>/ prefix (AF-AP-103):
# Hermes forwards model.default verbatim as the wire model and OmniRoute rejects a leading
# custom:s0-03-omniroute/ as an unknown provider (proven live: model=agentfactory-build -> 200;
# model=custom:s0-03-omniroute/agentfactory-build -> 401 "No active credentials for provider:
# custom:s0-03-omniroute"). The custom: prefix belongs on model.provider, where Hermes reads the
# provider config; key_env (the NAME only) carries the credential from the launch environ. No key
# value is in this file (A3's credential screen). Wire mode chat_completions is the owner's live
# transport and the mode leg B OBSERVES (ADR 0002); leg A independently exercises /v1/responses.
model:
  default: agentfactory-build
  provider: custom:s0-03-omniroute
  base_url: http://127.0.0.1:20128/v1
  api_mode: chat_completions
providers:
  s0-03-omniroute:
    api: http://127.0.0.1:20128/v1
    name: S0-03 OmniRoute
    key_env: OMNIROUTE_API_KEY
    default_model: agentfactory-build
    transport: openai_chat
    discover_models: true
    extra_headers:
      x-omniroute-compression: "off"
```

### 2. `proofs/S0-03/tools/pc/collect_leg.sh` — the query (the root of the captured `{direct:0, hermes:0}`)
- Both queries filter `requested_model = ?` (the resolved ref, never matches the route). Change the
  route filter to **`combo_name = ?`**.
- Direct query second predicate `response_id = ?` (dead) → **`id = ?`**, where the value is the
  `x-omniroute-request-id` read from `direct.json.response_headers` (NOT `direct.json.id`). Extract
  it in the python block; if the header is absent, exit LOUD.
- Hermes query: bind on **`session_tag = ?`** (the leg's `nonce2`) + `combo_name = ?`, keep the
  window as a sanity assertion (every returned row's timestamp inside the closed window) but NOT as
  the binding. Return EVERY matching row (the round trip logs several), leg-tagged `hermes`.
- Keep the "declared leg with no row is LOUD" exit, but "declared" now means: direct — the
  request-id header present; hermes — the window + a nonce2 present. A declared leg with 0 rows
  still exits non-zero.

### 3. `proofs/S0-03/check_omniroute_roundtrip.py`
- `check_identity_route` (~:505): route match `requested_model == route_id` → **`combo_name == route_id`**.
  Direct leg: `response_id == streamed_id` → the row's **`id` == `direct.json.response_headers['x-omniroute-request-id']`**.
  Hermes leg: keep `session_tag == nonce2`, but bind **every** row with that tag (≥ 1), validate each;
  DELETE the `len(grouped["hermes"]) != 1` uniqueness rule (`:539`) — the real round trip logs many
  rows. Keep: each row `status == 200`, `method == POST`, provider not in the stub set, model not a stub.
- Per-leg transport (conjunct v): the direct row's `path` ends `/v1/responses`, the hermes rows' path
  ends `/v1/chat/completions`. Record the observed path per leg and assert each is one of the two
  PERMITTED paths (`/responses` or `/chat/completions`); DELETE the single-path `/responses` pin and
  the `REQUIRED_API_MODE == 'codex_responses'` literal in `check_transport` (~:720) — replace with:
  read the profile `api_mode`, assert it is in `{chat_completions, codex_responses}`, and record it.
- Model cross-check (`:592`): compare `call_logs.model` to `direct.json.response_headers['x-omniroute-model']`
  (both `gpt-5.6-sol-ultra`), NOT `direct.json.model` (the normalized `gpt-5.6-sol`).
- Update the `_REASONS` strings (`:142-147`) to match (drop the codex_responses literal message; the
  identity_response_id message becomes the request-id message).

### 4. `proofs/S0-03/tools/pc/direct_responses_probe.py`
- It already records `response_headers`. Ensure `x-omniroute-request-id` and `x-omniroute-model` are
  present in the recorded headers (they are, live). Add a first-class `omniroute_request_id` field to
  `direct.json` (copied from the header) if that reads cleaner for the checker; otherwise the checker
  reads `response_headers`. Do NOT change the wire (it stays codex_responses / /v1/responses).

### 5. `proofs/S0-03/tools/pc/run_s0_03_legs.sh` — AF-AP-100 (the runner's DONE condition)
- After leg B, the runner must ASSERT the real round trip before treating the bundle as captured: a
  `tool_call` whose title contains `printf <nonce2>` reaching `tool_call_update status=completed`,
  AND the agent's final message contains the nonce. A bare `end_turn` (which fired on the 401) is NOT
  success. Exit LOUD if the round trip is absent. (Keep every existing process-safety rule — no
  name-matching killers; kill by pidfile only.)

### 6. `tests/test_s0_03_omniroute.py` — update every assertion the above moves
- `:1031` `block["api_mode"] == "codex_responses"` → `"chat_completions"`; the model.default bare-form;
  the transport test (`:407`, `:411-412`) → the observed-mode-in-permitted-set semantics.
- The identity/binding tests → the real columns (combo_name, id==request-id, session_tag, ≥1 hermes
  rows, per-leg path).

### 7. `proofs/S0-03/fixtures/*` — regenerate to the REAL schema + PRE-MINT hostile bundles (AF-AP-36)
- Regenerate the four evidence-* fixtures' `omniroute-requests.json` (and `direct.json` headers) to
  the real schema/columns above, using the golden values. `evidence-provider-key-present` /
  `evidence-stub-route` must reflect a real multi-row hermes leg.
- Add committed FAILING hostile bundles, one per realigned binding — each a `test_…` that asserts the
  checker REDS with the exact reason: (a) direct row `id` != the request-id header; (b) a stub
  `provider`; (c) a `combo_name` mismatch; (d) `call_logs.model` != the `x-omniroute-model` header;
  (e) a hermes row missing the `session_tag`; (f) a wrong transport path (neither /responses nor
  /chat/completions). Each hostile bundle is RUN and shown red-then-the-guard-green.

## Gate (do this, paste verbatim, do NOT mint)
- `bash scripts/lane_gate.sh -r <rev> -f "proofs/S0-03/hermes/config.yaml proofs/S0-03/tools/pc/collect_leg.sh proofs/S0-03/check_omniroute_roundtrip.py proofs/S0-03/tools/pc/run_s0_03_legs.sh proofs/S0-03/tools/pc/direct_responses_probe.py tests/test_s0_03_omniroute.py proofs/S0-03/fixtures" -t "tests/test_s0_03_omniroute.py" -n 2` — the two runs' counts must agree; paste the RESULT line.
- `python3 scripts/report_lint.py` and `scripts/ap_screen.py --s0-01` on your report per the checkpoint rule.
- Run the checker twice, bitwise-identical.
- Report DATA: files:lines changed, verbatim test counts (pasted from the gate, never typed), each
  hostile bundle's red→green, and anything you could NOT do (declare it).

## Boundary (exactly these files)
`proofs/S0-03/hermes/config.yaml`, `proofs/S0-03/tools/pc/collect_leg.sh`,
`proofs/S0-03/check_omniroute_roundtrip.py`, `proofs/S0-03/tools/pc/run_s0_03_legs.sh`,
`proofs/S0-03/tools/pc/direct_responses_probe.py`, `tests/test_s0_03_omniroute.py`,
`proofs/S0-03/fixtures/**`. Nothing else. NO live capture, NO mint, NO registry/ledger/blocked.json,
NO outward action — the coordinator does the real re-capture + class-flip + mint after this.
