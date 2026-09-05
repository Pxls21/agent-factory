# S0-01 ACP conformance — grounding & provenance (2026-09-04)

> Status: **BUILD COMPATIBILITY VERIFIED; RUNTIME INTEGRATION UNVERIFIED until the relay
> handshake.** The three pinned components clone/build/install and run standalone by absolute
> path — that is *build compatibility*, not integration. Integration (buzz-acp actually launching
> and speaking ACP to hermes-acp) becomes verified only after the first real relay-driven
> handshake. The executable proof (`runner`, `fixtures/`, `result.json`) lands in a later increment.
> Owner ruling 2026-09-04: build+test against FRESH pinned clones; do NOT touch the
> live installs or `upstream.lock.yaml`; invoke by ABSOLUTE PATH; if the pinned
> components cannot integrate, STOP and report (no silent patch/re-pin).

## Provenance — pinned clones on the PC (isolated, clean)

Base dir: `/home/rocco/s0-01-pinned/` (fresh; separate from the owner's live installs).

| component | pin (`upstream.lock.yaml`) | checked-out HEAD | clean-tree |
|---|---|---|---|
| hermes-agent | `527da60844d4dced37879ea50259675371abe10e` (v0.21.0) | `527da60…` | yes |
| buzz | `1c8321cd08feb597f8bcff5195c21148fb3e98ed` | `1c8321c…` | yes |
| agent-client-protocol | `37a7d4f8a0a0632653a14084b8140ceb486ab0e8` | `37a7d4f8…` | yes |

Fetched by exact SHA (`git init && git fetch --depth 1 origin <sha> && git checkout <sha>`);
`git status --porcelain` empty at each pin.

Toolchains (PC): `rustc 1.93.0`, `cargo 1.93.0`, `Python 3.13.11`, `git 2.52.0`.

## Built binaries (invoke by ABSOLUTE PATH only)

- **buzz-acp** — `/home/rocco/s0-01-pinned/buzz/target/release/buzz-acp`
  - build: `cargo build --release -p buzz-acp` (from `~/s0-01-pinned/buzz`), finished 1m39s.
  - sha256: `a5a17ffc0c7ef878648a506b9d5066120b91984d1158a60e6ce9664a39f88064`
- **hermes-acp** — `/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp`
  - **Install method (owner Option 2, 2026-09-04): editable install, NOT a built wheel.** hermes-agent's
    `setup.py` is a deliberate guard that REFUSES `bdist_wheel`/`sdist` (`RuntimeError: Building wheels
    or sdists for hermes-agent is not supported`); its only sanctioned wheel path is uv2nix (Nix), and
    Nix is not installed on the PC (owner declined to install it for this proof). The component's docs
    direct developers to an editable install. Immutability is anchored not by a wheel file but by the
    clean-pinned-tree content hash below, re-verified before AND after each proof run.
  - install: `PYTHONDONTWRITEBYTECODE=1 python3 -m venv .venv-hermes && .venv-hermes/bin/pip install -e '~/s0-01-pinned/hermes-agent[acp]'` (fresh venv). deps incl. `agent-client-protocol==0.9.0`.
  - **Provenance record** (`~/s0-01-pinned/.markers/hermes-provenance.json`):
    - commit `527da60844d4dced37879ea50259675371abe10e`; `HEAD^{tree}` `a36bba5ee05b1b27eaee510287e74f976e2bbf21`
    - `git status --porcelain --untracked-files=all` = empty; submodules = none
    - `git archive --format=tar HEAD | sha256sum` = `b65c49908d8bba3e87e234a5fc972ac294d6411aa3f794d82c706aff97302ee3`
    - `direct_url.json` = `{"dir_info":{"editable":true},"url":"file:///home/rocco/s0-01-pinned/hermes-agent"}` — points to the PINNED clone, NOT `~/.hermes/hermes-agent`
    - python `3.13.11`; venv `/home/rocco/s0-01-pinned/.venv-hermes`; `pip freeze` sha256 `352babfa576c5774e8fc710b4fce82aaeb7758c3116da70928e0239539922aab`
    - entrypoint sha256 `f90a0cc333fa86d99495c7c984e4e11a1b83a7e3dc92883b7fd295ae70358ef1`; `--version` `0.21.0`; `--check` OK
  - **Pre/post-run recheck (owner mandate):** commit + `HEAD^{tree}` + porcelain-empty + archive-sha256 are
    re-verified against these values immediately BEFORE and AFTER each of the two proof runs; any source-tree
    change (or byte differing) invalidates the run. `PYTHONDONTWRITEBYTECODE=1` on every invocation.
- **ACP schema (pinned)** — `/home/rocco/s0-01-pinned/acp/schema/v2/schema.json` (also v1). Used by the negative control.

## Topology (verified from source + the built binary's `--help`)

```
Buzz relay ──WS──> buzz-acp (ACP client, relay daemon) ──stdio(ACP JSON-RPC)──> hermes-acp (ACP agent)
```

- `buzz-acp` is a **relay daemon**: `main() -> buzz_acp::run()`; requires `--private-key` (Nostr) and
  `--relay-url` (default `ws://localhost:3000`). It launches the agent via
  `--agent-command <bin> --agent-args <...>` (defaults `goose acp`) and drives it over stdio.
  Its `AcpClient` (spawn → initialize → session_new → session_prompt_with_idle_timeout →
  cancel_with_cleanup → shutdown) is in a **private** `mod acp` — NOT externally linkable, and there
  is **no fixture/oneshot/stdin drive mode**. So a faithful "launched by the real buzz-acp" run must
  go through the relay path.
- To launch the pinned hermes-acp:
  `--agent-command /home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp` (agent-args empty — hermes-acp
  *is* the ACP server, no subcommand).
- `hermes-acp` is a standard ACP stdio agent implementing `initialize`, `prompt`
  (emits `session/update` notifications then a `PromptResponse{stop_reason}` ∈ {end_turn, refusal, cancelled}),
  `cancel`, shutdown.

## Assertion map (seed S0-01, 6 assertions)

1. **initialize returns required capability fields** — capture the `initialize` request/response between
   buzz-acp and hermes-acp; assert the response carries the pinned protocol's required fields.
2. **prompt streams updates → terminal** — a canonical prompt yields ≥1 `session/update` then a terminal `stop_reason`.
3. **cancel mid-turn → cancelled terminal + no orphan** — `session/cancel` yields `stop_reason=cancelled`;
   assert no child process survives (buzz-acp kills the process group in `cancel_with_cleanup`).
4. **clean shutdown exits 0 + session closed.**
5. **thread↔session mapping, no collision across two concurrent fixture users** — two sessions, distinct
   session ids, no cross-talk.
6. **`BUZZ_ACP_IDLE_TIMEOUT=900` + max turn duration observed (config echo)** — NOTE the buzz-acp default
   idle timeout is **1500s** (`DEFAULT_IDLE_TIMEOUT_SECS = 1_500`), so the proof must SET
   `BUZZ_ACP_IDLE_TIMEOUT=900` and assert the resolved-config echo shows 900; max turn duration default 7200.

## Negative control (schema-layer, per the seed)

`fixtures/s0-01/neg-malformed-initialize.json` omits a required field. The pinned ACP v2 schema
(`acp/schema/v2/schema.json`) `InitializeRequest` **required = [`protocolVersion`, `info`]**. The fixture
omits `protocolVersion`; the harness schema-validates it against the pinned schema → expected failure
`protocol-violation: missing required initialize field`.
(hermes-acp's own `initialize` handler is LENIENT — a missing `protocol_version` DEFAULTS to
`acp.PROTOCOL_VERSION` rather than erroring — so the violation is enforced at the schema layer against
the pinned protocol commit, exactly as the seed's fixture_format specifies.)

## Settled design — model egress (OmniRoute-only) + deterministic golden

**Model egress is OmniRoute-exclusive (ADR 0002; owner correction 2026-09-04). NO direct Ollama or canned
model endpoint.** The pinned hermes-acp is configured to reach models ONLY through the EXISTING OmniRoute
instance:
- base_url `http://127.0.0.1:20128/v1` — the MANAGED instance `omniroute-migrated.service` (2026-09-05: an
  unmanaged orphan had squatted the port serving a reduced DB — every key got `401 AUTH_002`; fixed by the
  owner's Codex session; `docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md`, AF-AP-33);
- credential from env `OMNIROUTE_API_KEY` = **the same client key the owner's Hermes uses** (owner ruling
  2026-09-05: "one key, many models — use the setup Hermes has"; the earlier new-scoped-key directive dated from
  the orphan-instance 401s and is withdrawn). Read from the owner's Hermes config at launch; never copied into
  the repo, printed, or passed in argv. **Finding 2026-09-05:** that key's prefix matches no row of the authoritative
  `api_keys` table (`/v1/models` → 401 with it); the owner's Hermes works only because the plane runs
  `REQUIRE_API_KEY=false` (task #34). So the owner's earlier `/v1/models` → 200 precondition is unsatisfiable until the
  owner regenerates the `hermes` key; the exploratory prompt turn below runs the way the owner's Hermes runs today —
  credential NOT validated by OmniRoute — and says so. That is not S0-03 evidence.
- wire mode: ADR 0002 / `docs/03_INTEGRATION_CONTRACTS.md` §2 pin `api_mode: codex_responses` + `extra_headers:
  {x-omniroute-compression: "off"}`; the pinned hermes 0.21.0 supports both (`agent/codex_responses_adapter.py`,
  `hermes_cli/config.py normalize_extra_headers`). The bring-up config currently says `chat_completions` (it mirrored
  the live profiles, which the Codex repair set to `chat_completions` — an ADR deviation, task #35); the proof run
  switches the pinned config to the ADR shape and records any failure as a finding.
- an existing route: `auto/best-coding-fast` (the model the key is restricted to).
This is **NOT** S0-03: S0-01 proves ACP behavior; S0-03 later proves OmniRoute's upstream identity and the
credential boundary. No new OmniRoute deploy; no OmniRoute config change unless the existing route genuinely
cannot support a deterministic test.

**Determinism procedure (owner-directed):** make a NORMAL model request through OmniRoute; normalize only
volatile VALUES. Try the existing route first; if its ACP event STRUCTURE is not reproducible under
structure-preserving normalization, add a dedicated OmniRoute test route to a deterministic scripted backend
(sanctioned; a scripted backend behind OmniRoute is preferred over Ollama) — after demonstrating the need.

**Normalization discipline (STRUCTURE-PRESERVING):** strip volatile VALUES only — JSON-RPC id values,
timestamps, session-id values, ports, pids, model-output TEXT, token counts. **PRESERVE protocol structure
and ordering:** message-type sequence, event COUNTS, terminal `stop_reason`, cancellation, and session
separation. Missing, duplicated, reordered, or cross-session events are REAL failures and must NOT be
normalized away. The normalized transcript is then deterministic across runs → golden ×2 byte-identical.

## Owner constraints checklist (for the build increment)

- [x] Fresh isolated dirs only; never touch live installs or `upstream.lock.yaml`.
- [x] Invoke both binaries by absolute path (paths above); no ambient PATH; `PYTHONDONTWRITEBYTECODE=1` (argv + env names recorded per run).
- [x] Record SHAs, `HEAD^{tree}`, clean-tree (`--untracked-files=all`), toolchains, build commands, binary
      sha256, editable-install provenance (direct_url, freeze, entrypoint hash). Still to record at run time: argv, transcript digests (`result.json`).
- [x] Re-verify ALL THREE trees immediately BEFORE and AFTER each run (recursive manifests; identical across the initialize capture and both exploratory turns) — repeated for the proof runs.
- [ ] Model egress ONLY through the existing OmniRoute (`:20128/v1`, `OMNIROUTE_API_KEY`); never print/commit keys. Not S0-03.
- [x] Throwaway Buzz relay + Nostr identity isolated from production (`buzz-prod-*`): own ports (3999/3998/3997,
      postgres 5471, redis 6471, minio 9471), own containers `s0-01-harness-*`, own keys. **CAVEAT (AF-AP-34):** four
      `pkill -x buzz-relay` calls on 2026-09-04 aimed at THIS relay restarted the production `buzz-prod-relay-1`
      (its binary shares the bare name in the host process table) — reported to the owner; teardown now goes
      through pidfiles + `/proc/<pid>/exe`, never names.
- [ ] Golden normalized-compare run TWICE byte-identical (structure-preserving) + the malformed-initialize negative.
- [ ] If pinned components cannot integrate faithfully → STOP and report with evidence (no patch, no re-pin).

## Reached 2026-09-04/05 (relay path) — still RUNTIME INTEGRATION UNVERIFIED

- Isolated relay stack up on the PC (relay `127.0.0.1:3999`, `RELAY_URL=ws://127.0.0.1:3999` — identical
  authority everywhere, the fail-closed tenant binding bit once as a WebSocket 404); relay/agent/owner Nostr
  identities registered; channel `73701f66-…` created (kind 9007) with the agent as member (kind 39002);
  buzz-acp (`BUZZ_ACP_RESPOND_TO=owner-only`, `SESSION_POLICY=thread`, idle timeout set) subscribed; an owner
  `buzz messages send --mention` was `accepted: true` with the `h` + `p` tags. buzz-acp prompted hermes-acp,
  hermes reached OmniRoute — and hit the orphan's `401`. Frame capture (`frame_tee.py` as `--agent-command`
  wrapper) and the recursive checkout manifest (`manifest.sh`, baselines for all three trees) are in place.
- **Initialize milestone (recorded precisely, owner wording 2026-09-05): the pinned `buzz-acp` launched the
  pinned `hermes-acp` and exchanged ACP initialize messages. Client offered protocol `2`. Agent returned
  protocol `1`. Initialize exchange succeeded with the required capabilities** (the pinned v1
  `InitializeResponse` requires only `protocolVersion`; the response carried it plus `agentCapabilities`,
  `agentInfo`, `authMethods`; v1 defines the returned value as "the protocol version the client specified if
  supported by the agent, or the latest protocol version supported by the agent"). Evidence = RAW JSON-RPC
  frames, not logs: `evidence/initialize-20260905T062959Z/` (`frames-client-to-agent.jsonl` sha256 `1df85efc…`,
  `frames-agent-to-client.jsonl` sha256 `af61e42a…`, `argv.txt`, `env-names.txt`, `capture.json`) bound to the
  pinned binaries (buzz-acp `a5a17ffc…`, hermes-acp entrypoint `f90a0cc3…`), the three source trees (recursive
  manifests pre = post = baseline), the pinned v1 schema (`fixtures/acp-schema-v1.json`, sha256 `caf62ff9…`,
  acp@37a7d4f8) and the tee instrument (`tools/frame_tee.py`, `a7a0c367…`). buzz-acp spawns the agent at daemon
  start, so the capture issued NO prompt and carried NO OmniRoute credential (env names recorded). Checked by
  `check_initialize.py` (schema layer) and `tests/test_s0_01_initialize_capture.py` (5 tests, incl. the seed's
  negative `fixtures/neg-malformed-initialize.json` ⇒ `protocol-violation: missing required initialize field`,
  de-vacuoused both ways). **S0-01 overall REMAINS INCOMPLETE:** nothing here proves relay-authenticated
  prompting, OmniRoute egress, streaming/terminal behavior, cancellation, shutdown, concurrent-session mapping,
  timeout configuration, determinism, or the negative control in a live run; assertion 1 closes only inside the
  full proof run.

## Reached 2026-09-05 (relay-driven prompt turn, exploratory runs 1 and 2) — still NOT the proof

- **Milestone 2, recorded precisely:** an owner mention (kind 9, `h`+`p` tags, `accepted: true`, relay-authenticated
  under `respond_to=owner-only`) drove the pinned `buzz-acp` to `session/new` + `session/prompt` on the pinned
  `hermes-acp`; hermes-acp streamed `session/update` notifications and returned `PromptResponse
  stopReason=end_turn`; Hermes reached the managed OmniRoute (`model=auto/best-coding-fast provider=custom`, 3 API
  calls, 2 tool turns, `finish_reason=stop`) — twice, with identical inputs (`evidence/turn-20260905T070807Z/`,
  `evidence/turn-20260905T071639Z/`: raw frames, argv, env names, the config-echo startup line, capture records;
  three-tree manifests identical before and after both runs). Every frame of both turns validates against the pinned v1
  schema (`NewSessionRequest/Response`, `PromptRequest/Response`, `SessionNotification`); all notifications carry the
  session id from `session/new`; the config echo reads `idle_timeout=900s max_turn=7200s session_policy=thread`
  (`tests/test_s0_01_turn_capture.py`, 5 tests).
- **Credential caveat (first-class):** OmniRoute did NOT validate the key — the instance runs `REQUIRE_API_KEY=false`
  and the key the owner's Hermes carries is in no row of its key table (`/v1/models` → 401). The turns ran exactly the
  way the owner's own Hermes runs today. Not S0-03 evidence.
- **Repaired later on 2026-09-05 (owner via Codex):** the `hermes` key was rotated into every Hermes profile and
  `REQUIRE_API_KEY=true` enabled; reproduced read-only (no key 401, bogus 401, rotated key 200 / 2,625 ids, monitor 7/7).
  The tee'd buzz-acp was restarted with the rotated key (`.markers/buzz-acp.pid`). Runs 1 and 2 keep their caveat; every
  later run is credential-validated by OmniRoute.
- **Determinism finding (`evidence/determinism-live-route.json`):** identical inputs, same client sequence, same
  terminal state, DIFFERENT `session/update` structure (run 1: 49 thought + 27 message chunks, one post-terminal
  `session_info_update`; run 2: 59 + 1, none). Structure-preserving normalization cannot yield a byte-identical golden on
  the live route — the model chooses chunking and tool rounds. Per the owner's determinism procedure (2026-09-04) the
  golden runs against a deterministic scripted backend behind a dedicated OmniRoute test route; the need is now
  demonstrated. The live route stays a separate leg asserting only the run-invariant structure.
- **Pipeline notes (not S0-01 assertions):** (1) no agent reply reached the channel thread in either run — this pinned
  buzz-acp hands the reply job to the AGENT (the `<base>` prompt names the reply destination) and was started with
  `--mcp-command` empty (`session/new mcpServers: []`), so the agent had no Buzz tool; the model tried the owner's `buzz`
  CLI through Hermes' terminal tool and hit `BUZZ_PRIVATE_KEY is required` (the agent env carries no relay key — correct
  by design). Reply delivery belongs to the production wiring (S0-02 territory: a Buzz MCP server or CLI credentials for
  the agent identity). (2) The pinned hermes-acp executed a terminal tool with the owner's `HOME` and `PATH` and NO
  policy gate — standing rule 9's fail-closed `pre_tool_call` hook is absent at the pin; Stage 0 must not treat the ACP
  proof as containment evidence (S0-08).
- **Fixtures staged 2026-09-05 for the remaining legs (no model calls):** second fixture user `user2`
  (`.secrets/user2.env`/`.pub`, relay-admitted with the relay signing key, channel member via the owner). Gate
  observation: under `respond_to=owner-only` a user2 mention was ACCEPTED by the relay yet produced NO prompt
  (client→agent frames stayed at the initialize) — the owner gate holds; assertion 5 runs under
  `respond_to=allowlist` with user2 listed. Relay membership facts: only the agent was relay-admitted before, yet the
  owner posted fine — this isolated relay does not gate writes on relay-level membership (S0-02 territory). The
  scripted backend runs on the PC (`.markers/scripted-backend.pid`, port 20201; no-bearer 401, bearer 200,
  `s0-01-pong` streams 4 SSE frames; requests recorded under `.markers/upstream-records/`), waiting for the
  OmniRoute provider connection (task #36, owner/Codex).
- **What this does NOT prove:** cancellation (assertion 3), clean shutdown (4), two-user session separation (5),
  the negative control in a live run, the golden ×2, validated egress. Assertions 1, 2 and 6 have raw-frame evidence
  from exploratory runs; they close only inside the runner's recorded proof run.

## NOT yet done (next increment)

- **Golden route (owner or Codex — a config change on the running OmniRoute):** the scripted backend is built and tested
  (`tools/scripted_backend.py`, `tests/test_s0_01_scripted_backend.py`). Recipe: (1) on the PC start it by absolute path —
  `setsid /usr/bin/python3 ~/agent-factory/proofs/S0-01/tools/scripted_backend.py --port 20201 --token-file
  ~/s0-01-pinned/.secrets/scripted-upstream.env --record-dir ~/s0-01-pinned/.markers/upstream-records --pidfile
  ~/s0-01-pinned/.markers/scripted-backend.pid </dev/null >~/s0-01-pinned/.markers/scripted-backend.log 2>&1 &`
  (the token file is a 0600 `UPSTREAM_TOKEN=…` line); (2) in OmniRoute add an `openai-compatible` provider connection
  named `s0-01-scripted` with base URL `http://127.0.0.1:20201/v1` and that token as its API key; (3) confirm the model ids
  OmniRoute exposes for it (expected `s0-01-pong`, `s0-01-slow` under that connection) and tell the coordinator, which
  then points the pinned hermes config's `model.default` at the pong id for the golden and at the slow id for the
  cancellation leg. The backend never emits tool calls, so the ACP structure is fixed; it records every upstream request
  with the bearer reduced to a fingerprint (S0-04-grade evidence later). Not S0-03 evidence.
- **Checker + spec BUILT (2026-09-05):** `check_acp_conformance.py` grades the evidence bundle `evidence/golden/{run-1,run-2,
  cancel,shutdown,two-users}` against all six assertions and the golden discipline (structure-preserving normalizer:
  ids/session ids → order-of-appearance placeholders, text/paths/timestamps/token counts dropped; message-type sequence,
  event counts, tool-call structure, stop reasons and session separation preserved; run-1 == run-2 == frozen
  `golden.jsonl`). Exit 0 PASS · 1 FAIL with `failure_reason:` · 2 DEFERRED while the bundle is absent — which is
  today's state: `spec.json` is wired into the canonical proof-runner and its positive leg DEFERS (no `result.json`
  minted); the negative leg is `check_initialize.py` on the seed fixture. Tests: `tests/test_s0_01_check_acp_conformance.py`
  (bundles built from the REAL frames; missing/duplicated/reordered/cross-session events, cancel/shutdown/two-user/echo/
  provenance negatives, deferral) and `tests/test_s0_01_spec_runner.py` (the real runner defers and preserves).
  Normalizer note: two adjacent chunks of the same kind are interchangeable once text is stripped — not a reorder.
- CAPTURE still to run (needs task #36): golden ×2 on `s0-01-pong`, cancel on `s0-01-slow` (`session/cancel` →
  `cancelled`, agent process gone), clean shutdown after a completed turn (exit code captured by a wrapper), two
  users under `respond_to=allowlist` (owner + user2, two top-level mentions under `session_policy=thread`); then freeze
  `golden.jsonl` from a reviewed run-1 normalization, run the proof-runner on the PC venue, ledger integrity.
- Stack state: the isolated relay stack and the tee'd buzz-acp (pidfile `.markers/buzz-acp.pid`) stay up on the PC
  for the next runs; teardown goes through pidfiles, never names (AF-AP-34).
