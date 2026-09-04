# S0-01 ACP conformance — grounding & provenance (2026-09-04)

> Status: **GROUNDING ONLY — the proof is NOT yet run.** This records the verified
> provenance and the settled harness design from the live PC-bridge session. The
> executable proof (`runner`, `fixtures/`, `result.json`) lands in a later increment.
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
  - install: `python3 -m venv ~/s0-01-pinned/.venv-hermes && .venv-hermes/bin/pip install -e '~/s0-01-pinned/hermes-agent[acp]'`
  - deps incl. `agent-client-protocol==0.9.0` (Python ACP lib); `--version` = `0.21.0`; `--check` = `Hermes ACP check OK`.
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

## Settled design decision — deterministic golden

buzz-acp requires the relay + a real agent turn, and a live model turn is not byte-reproducible. The proof
is **ACP protocol conformance**, not model content, so the golden is the **normalized protocol SHAPE**:
strip the volatile fields (JSON-RPC ids, timestamps, session ids, ports, pids, model-output text, token
counts) and keep the message-type SEQUENCE, the terminal `stop_reason`, and the capability field names.
The normalized transcript is deterministic across runs → golden ×2 byte-identical. (A deterministic hermes
backend is not required for a shape-conformance golden; normalization handles content volatility.)

## Owner constraints checklist (for the build increment)

- [ ] Fresh isolated dirs only (done for clones/build); never touch live installs or `upstream.lock.yaml`.
- [ ] Invoke both binaries by absolute path (paths above); no ambient PATH.
- [ ] Record: SHAs, clean-tree, toolchains, build commands, binary sha256, argv, transcript digests (this doc + `result.json`).
- [ ] Golden normalized-compare run TWICE byte-identical + the malformed-initialize negative.
- [ ] If pinned components cannot integrate faithfully → STOP and report with evidence (no patch, no re-pin).

## NOT yet done (next increment)

- Nostr identity for buzz-acp (`buzz-admin generate-key`, register as relay member) + relay target
  (owner runs `buzz-prod-relay-1`; confirm its WS URL, or stand up a throwaway local relay).
- Canonical fixtures + the malformed-initialize negative.
- The runner: drive buzz-acp→hermes-acp over the relay, capture the ACP transcript, normalize, golden ×2,
  assert the 6 properties + the negative; emit `proofs/S0-01/result.json` via the canonical proof-runner;
  ledger integrity.
