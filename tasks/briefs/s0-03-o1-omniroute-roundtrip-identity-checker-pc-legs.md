# Lane O1 — S0-03 Hermes→OmniRoute live round trip: the identity-asserting checker, three negative bundles, the probe fixed, the PC leg runner (sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".)

**Why:** S0-03 is the council's "single most important assertion" (COUNCIL-VERDICT §consensus 4): a pass must assert UPSTREAM
MODEL IDENTITY, never a 200, and the S0-04 stub is FORBIDDEN here (Socrates: stub-drift is the pack's characteristic hollow green).
Today `proofs/S0-03/` holds only the blocked marker, a 280-byte `probe.json` and a 20-line probe (`material-S0-03.md` §5.2); ledger
state BLOCKED. The blocker is GONE: the owner's OmniRoute on the PC (`omniroute-migrated.service`, `:20128`) now enforces
`REQUIRE_API_KEY=true` (`/v1/models` → 401 without a key, verified over the bridge 2026-09-08 00:4xZ) and the owner's Hermes client key
is accepted (`docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md:15-16, 33-40`); the `pc-bridge` spike declared the transition
`blocked_credential → execution_proof` (`proofs/registry.yaml:34`, rule `map-pcbridge-s003`). The seed block is exact
(`seeds/seed-stage0-v1.yaml:382-405`): three assertions (a `/v1/responses` request through REAL OmniRoute streams text and completes a
REAL Hermes tool-call round trip · the pass asserts upstream model identity = response model id + a non-stub fingerprint · Hermes holds
no upstream provider key (env assertion) and OmniRoute failure does not trigger direct fallback), kill switch = disable the credential
⇒ RED `blocked: credential_absent`, marker reasons `[credential_absent, credential_rejected]` with `credential_rejected` ⇒ proof-RED never
blocked. **Owner rulings that bind this lane:** the model egress is the OmniRoute ALREADY RUNNING on the PC — never a sandbox model
server, vLLM is NOT a dependency (2026-09-03 "just use omniroute"): the identity asserted is the ROUTED MODEL ID OmniRoute reports for the
declared route, not `sim9b` (that PC-BRIDGE.md line predates the ruling — say so in the report, do not edit PC-BRIDGE.md) · the client key
is the one Hermes already uses, read ON THE PC IN PLACE from the owner's Hermes profile env, never copied, printed, or passed in argv
(2026-09-05 ruling, AF-AP-39) · never modify, stop or restart the owner's OmniRoute or Hermes sessions · the transport question (ADR 0002
`codex_responses` vs the live profiles' `chat_completions`, owner task #35) is OPEN — this proof PINS the ADR's transport and a failure
there is a RED FINDING for the owner, never a silent switch.
**Inputs (read in this order):** `tasks/briefs/stage0-parallel-support/material-S0-03.md` (whole — §4 the seams, §5 every existing file
verbatim, §5.6-5.7 the runner's probe path + the validator's S0-03 rule, §6 the venue facts and the three key-name spellings, §7 the
registry rows) · `material-S0-02.md` §5.4 (S0-07/S0-11 spec exemplars), §7 (the 18 classes + mint-wide AF-AP rows) · the pinned OmniRoute
source at `/home/user/nerdherderdani/OmniRoute` (commit 488f57e9, READ-ONLY): find and cite file:line for (a) the `/v1/responses` handler
and its streaming event shapes, (b) where the response `model` field is set (is it the client-requested combo id, the upstream's
reported id, or both — the proof must know WHICH identity it is asserting), (c) the auth gate (`REQUIRE_API_KEY`, the 401 body), (d) the
request-log / usage record a completed request leaves (the second instrument: provider connection + model per request — journal line,
DB row, or `/api/...` read endpoint), (e) the `X-OmniRoute-Compression` response header and the `x-omniroute-compression: off` request
header (S0-04's domain; S0-03 only asserts the header was SENT) · the pinned Hermes source at `/home/user/nerdherderdani/hermes-agent`
(commit 527da608, READ-ONLY): the custom-provider config keys `base_url`/`api_mode`/`key_env`/`extra_headers`, the `codex_responses`
client path, where a tool call is executed and reported over ACP (`session/update` tool_call kinds), what Hermes does when the provider
returns 401/5xx (any fallback provider path? cite the absence with file:line or the presence as a FINDING) · `proofs/S0-01/` (the
capture path this proof REUSES by invocation: `tools/pc/pc_launch.py`, the tee `tools/frame_tee.py`, `tools/pc/pc_post.sh`,
`check_acp_conformance.py`'s timeline reads, `acp-schema-v1.json`; the real-leg corpus `S0_01_REAL_LEG_DIR` = `/root/s0-01-realleg/golden`
for the REAL frame shapes — does any golden leg carry a tool-call turn? if not, derive the tool_call frame shape from the Hermes source
and mark it `NOT proven against a live capture` until the PC leg runs) · `scripts/omniroute_invariants.sh` (how a key file is passed via a
header FILE, never argv — copy the technique) · `proofs/schemas/{spec,result,probe,blocked}.schema.json` · `scripts/proof-runner` (probe
path :226-271 + mint path) · `scripts/validate-ledger:328-339, 373-393, 468-475` · `docs/03_INTEGRATION_CONTRACTS.md:31-51` ·
`docs/adr/0002-omniroute-sole-model-egress.md`.
**Scope (NEW files + ONE existing file + tests + your report):** `proofs/S0-03/spec.json` · `proofs/S0-03/check_omniroute_roundtrip.py` ·
`proofs/S0-03/hermes/config.yaml` (the proof-OWNED Hermes provider profile template — never the owner's live profile) ·
`proofs/S0-03/tools/pc/{run_s0_03_legs.sh, direct_responses_probe.py, hermes_env_names.py, collect_leg.sh}` (PC-side, NOT run here) ·
`proofs/S0-03/fixtures/evidence-credential-absent/`, `fixtures/evidence-stub-route/`, `fixtures/evidence-provider-key-present/` (three
committed NEGATIVE bundles) · `proofs/S0-03/probe_omniroute.py` (EDIT — the only existing file you touch) · `tests/test_s0_03_omniroute.py`
· report `tasks/briefs/s0-03-support/O1-report.md`. NOT yours: `proofs/S0-03/blocked.json`, `proofs/S0-03/probe.json`,
`proofs/registry.yaml`, `proofs/ledger.json`, anything under `proofs/S0-01/`, `PC-BRIDGE.md`, the docs, the seed (the class flip
`blocked_credential → execution_proof` in the registry + the marker removal + the re-mint of the five PRESENT proofs under AF-AP-56 are the
COORDINATOR's reviewed commit at mint time — write the exact registry diff you need into your report, do not apply it). Shared-tree rules
as every lane: never `git stash/checkout/restore/reset/add/commit/push`; gates from a `git archive <PIN>` copy under
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/o1/ + your files; explicit `--basetemp`; kill only your own
processes by pid; NEVER background a run and stop; no outward actions; NO PC bridge; NO network call to any OmniRoute or model endpoint from
the sandbox (there is none to call — a sandbox model server is forbidden); never read, print or commit a credential (AF-AP-35/39: print
lengths or digests only, redact by KEY NAME). Interpreter `/root/venv-agent-factory/bin/python`.

## Design (pinned — build it, do not redesign it)
1. **Two instruments per positive leg, correlated.** Leg A `direct` — `direct_responses_probe.py` (PC) sends ONE `POST /v1/responses`
   with `stream: true` to `http://127.0.0.1:20128/v1` for the declared route id (`spec.json` `route_id`, default `agentfactory-build` —
   the combo the owner's Hermes uses; read the id from the profile at run time, never hard-code a second copy), the key via a header FILE
   (the `omniroute_invariants.sh` technique; the env file path comes from `S0_03_KEY_FILE`, default the owner's profile env; the probe
   fails loud `S0_03_KEY_FILE unreadable` / `carries no OMNIROUTE_API_KEY line` — no default key, no argv), `x-omniroute-compression: off`,
   a prompt carrying a fresh 16-hex NONCE ("reply with exactly the token <nonce>"), and records `direct.json`: every streamed event
   (verbatim, secrets impossible — the request carries none), the response `model`, `id`, `usage`, the `X-OmniRoute-Compression` header,
   status, timing. Leg B `hermes` — the S0-01 capture path by INVOCATION (`pc_launch.py` + the tee + `pc_post.sh`, exactly as S0-01's legs
   run; the proof-owned `hermes/config.yaml` selects the route with `api_mode: codex_responses`, `key_env: OMNIROUTE_API_KEY`,
   `extra_headers: {x-omniroute-compression: "off"}`, `base_url: http://127.0.0.1:20128/v1`) with an ACP prompt that REQUIRES a tool call
   ("run the terminal command `printf <nonce2>` and reply with its output" — pick the tool the pinned Hermes exposes over ACP with the least
   side effects; cite it) ⇒ `timeline.jsonl` must show a `tool_call` update, its completion, and a final agent text carrying `<nonce2>`.
   Correlation: `collect_leg.sh` reads the OmniRoute request record (item (d) above) for BOTH requests into `omniroute-requests.json` —
   provider connection + model id + status per request — the second instrument for the identity claim. Both legs run against the REAL
   route; NEITHER may run against `s0-01-scripted` (the checker rejects it — item 3).
2. **The env assertion (assertion 3) is deny-by-default (AF-AP-23).** `hermes_env_names.py` (PC) reads `/proc/<hermes-pid>/environ` NAMES
   only (values never leave the process; the file it writes, `hermes-env-names.json`, is a sorted list of names + the pid + the exe
   readlink) for the hermes-acp process the tee spawned (pid from the tee's `runtime-identity.json`). The checker's rule: every name
   matching `(_API_KEY|_TOKEN|_SECRET|_KEY)$` must be in the ALLOWLIST `{OMNIROUTE_API_KEY}` — anything else (`OPENAI_API_KEY`,
   `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, …) is `env: upstream provider key <NAME> present in the Hermes environ`. Not a blacklist.
   "No direct fallback": the negative leg `credential-absent` (item 4) must show Hermes FAILING the turn on OmniRoute's 401 — the timeline
   carries the error and NO agent text — AND the same env-names record (no key to fall back to); plus the Hermes-source citation from
   the inputs (the fallback path's absence, or its presence as a FINDING). S0-05 owns the network-level proof; name that boundary.
3. **The identity assertion is a CONJUNCTION, each conjunct named in the PASS line.** `check_omniroute_roundtrip.py <evidence-root>` asserts:
   (i) `direct.json` status 200, ≥ 1 text delta event, the NONCE in the concatenated text; (ii) `direct.json` `model` == `spec.json`'s
   `expected_model_id` (the id OmniRoute REPORTS for the route — item (b) tells you which identity that is; the spec carries BOTH the route
   id and the expected reported id, and the report says how they relate); (iii) `omniroute-requests.json` shows both requests routed to a
   provider connection whose name is NOT `s0-01-scripted` and NOT any name in the spec's `stub_routes` list, with the same model id —
   `identity: request routed to the sanctioned stub route 's0-01-scripted', not an upstream model` otherwise; (iv) leg B's timeline: exactly
   one prompt turn, ≥ 1 tool_call update with a completed status, final text carrying `<nonce2>` (parse the timeline with S0-01's reader by
   IMPORT, never a copy); (v) the profile file captured in the leg (`profile.yaml`, the proof-owned template as launched, key-free) declares
   `api_mode: codex_responses` and the compression-off header — `transport: profile api_mode 'chat_completions' != 'codex_responses' (ADR 0002)`
   otherwise; (vi) the env allowlist (item 2). Any conjunct false ⇒ exit 1 with THAT reason, first failure wins, reasons EXACT strings from
   one table (`REASONS` dict, tested). Absent root ⇒ `deferred: S0-03 evidence not captured` exit 2. Reads under the S_ISREG rule (a FIFO
   or a directory at any evidence path ⇒ a named failure in bounded time — test it). PASS line
   `PASS: S0-03 omniroute-roundtrip - model <id> via <provider-connection>, tool-call round trip, env clean`.
4. **Three committed NEGATIVE bundles, each a real shape.** `evidence-credential-absent/` (leg B only: `hermes-env-names.json` WITHOUT
   `OMNIROUTE_API_KEY`, the timeline showing the 401 error frame and no agent text, `direct.json` status 401 with OmniRoute's real 401 body
   shape from item (c)) ⇒ exit 1 `blocked: credential_absent` — the seed's kill-switch reason, EXACT; `evidence-stub-route/` (a passing
   bundle whose `omniroute-requests.json` names `s0-01-scripted`) ⇒ the identity reason of item 3(iii); `evidence-provider-key-present/`
   (a passing bundle whose env names carry `OPENAI_API_KEY`) ⇒ the env reason. Frame shapes come from the REAL corpus where it has them and
   from the Hermes/OmniRoute source otherwise (say which, per file, in a `PROVENANCE.md` inside each bundle — AF-AP-42). `spec.json`:
   positive `check_omniroute_roundtrip.py proofs/S0-03/evidence` expect 0; negative `… proofs/S0-03/fixtures/evidence-credential-absent`
   expect 1 + `failure_reason: blocked: credential_absent`; `required_negative_controls: 1` satisfied by three (all three listed).
5. **The probe fixed (the only edit to an existing file).** `probe_omniroute.py` today maps EVERY failure to exit 11 `credential_rejected`
   (a down OmniRoute, a DNS error, a 500 — all "rejected", which the validator turns into proof-RED): HTTP 401/403 ⇒ 11; any other HTTP
   status ⇒ 12 (unmapped in `probe.json` ⇒ the runner raises `probe-invalid` — LOUD, the right outcome); URLError/timeout ⇒ 13 (unmapped,
   loud); key absent ⇒ 10; 2xx ⇒ 0. It must keep reading `OMNIROUTE_API_KEY` (the name the runner threads through `key_env`; the seed's
   `OMNIROUTE_UPSTREAM_KEY` and docs/03's `OMNIROUTE_INTERNAL_API_KEY` are the SAME credential under other names — record the three-way
   naming discrepancy in the report; the registry's `unblock_condition` string is the coordinator's edit). Tests drive the probe against a
   local `http.server` on 127.0.0.1 that answers 200 / 401 / 500 and a closed port — real sockets, no monkeypatching of urllib.
6. **The PC runner `tools/pc/run_s0_03_legs.sh` (NOT run here).** Preflight (read-only): `scripts/omniroute_invariants.sh` passes (the
   authoritative instance owns the port — AF-AP-33); the key file exists and is 0600; the route id appears in the authenticated `/v1/models`.
   Then leg A, leg B (through `pc_launch.py` with the proof-owned profile — find how S0-01's launcher takes a profile/config path; if it
   cannot, the runner needs a `S0_03_HERMES_CONFIG` seam in the LAUNCH env only and you say so — never edit S0-01's tools), the negative leg
   (`OMNIROUTE_API_KEY` unset in the LAUNCH env ONLY — the owner's profile is untouched), `collect_leg.sh` into `evidence/{direct,hermes,
   credential-absent}/`. `bash -n` clean; every external command listed in the report; every process the runner starts is killed by ITS
   pid (never `pkill`/`pgrep -f`, AF-AP-59); the owner's services are never touched.
7. **Tests** (`tests/test_s0_03_omniroute.py`): the checker over a synthetic PASSING bundle built by the test from the committed shapes
   (+ the three negative bundles ⇒ their exact reasons); each conjunct of item 3 falsified one at a time ⇒ its named reason (six mutants,
   first-failure order pinned); the stub-route name list read from the spec, never a literal; the FIFO/directory reads; the `deferred:`
   exit; the S0-01 timeline reader imported (assert by `inspect.getmodule`, not by grep); the probe's five outcomes over real sockets; the
   env allowlist rejects `FOO_API_KEY` and `OMNIROUTE_API_KEY_2` and accepts `OMNIROUTE_API_KEY` and `PATH`; `spec.json` validates against
   `spec.schema.json` and names the three bundles; `REASONS` values unique and every checker exit uses one. Preflight the 18 classes over
   your files BEFORE the report (`python3 scripts/ap_screen.py proofs/S0-03` and `--tests tests/test_s0_03_omniroute.py` — classify every hit
   by running it).
8. **Report discipline** as every lane: `report_lint.py` MISS 0 (`--map C=proofs/S0-03/check_omniroute_roundtrip.py --map
   T=tests/test_s0_03_omniroute.py --map P=proofs/S0-03/probe_omniroute.py`), ap_screen classified, file:line by grep on the FINAL bytes,
   counts pasted twice (`bash scripts/test_summary.sh tests/test_s0_03_omniroute.py`), pyflakes + `bash -n`, the process census, a
   `NOT run here` list (leg A, leg B, the negative leg, the invariants preflight — all PC), the exact registry diff for the class flip, the
   DISCREPANCIES section (the three key names; `sim9b` in PC-BRIDGE.md vs the routed-id ruling; the transport; anything the sources
   contradict), and the identity question answered from the OmniRoute source: WHICH model id does a `/v1/responses` response carry?
