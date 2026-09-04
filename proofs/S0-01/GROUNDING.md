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
- base_url `http://127.0.0.1:20128/v1` (live: returns 401 unauth → scoped credential required);
- credential from env `OMNIROUTE_API_KEY` (scoped internal; sourced at run time, **never copied, committed,
  or printed**; provider keys live only inside OmniRoute);
- `codex_responses` wire mode + the compression-off header (ADR 0002);
- an existing route (e.g. `codex/gpt-5.6-sol-xhigh` / `auto/best-coding-fast`).
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
- [ ] Invoke both binaries by absolute path (paths above); no ambient PATH; `PYTHONDONTWRITEBYTECODE=1`.
- [x] Record SHAs, `HEAD^{tree}`, clean-tree (`--untracked-files=all`), toolchains, build commands, binary
      sha256, editable-install provenance (direct_url, freeze, entrypoint hash). Still to record at run time: argv, transcript digests (`result.json`).
- [ ] Re-verify ALL THREE trees (commit + `HEAD^{tree}` + porcelain-empty + `git archive` sha256) immediately
      BEFORE and AFTER both proof runs; any source-tree change invalidates the run.
- [ ] Model egress ONLY through the existing OmniRoute (`:20128/v1`, `OMNIROUTE_API_KEY`); never print/commit keys. Not S0-03.
- [ ] Throwaway Buzz relay + Nostr identity kept isolated from production (`buzz-prod-*`).
- [ ] Golden normalized-compare run TWICE byte-identical (structure-preserving) + the malformed-initialize negative.
- [ ] If pinned components cannot integrate faithfully → STOP and report with evidence (no patch, no re-pin).

## NOT yet done (next increment)

- Nostr identity for buzz-acp (`buzz-admin generate-key`, register as relay member) + relay target
  (owner runs `buzz-prod-relay-1`; confirm its WS URL, or stand up a throwaway local relay).
- Canonical fixtures + the malformed-initialize negative.
- The runner: drive buzz-acp→hermes-acp over the relay, capture the ACP transcript, normalize, golden ×2,
  assert the 6 properties + the negative; emit `proofs/S0-01/result.json` via the canonical proof-runner;
  ledger integrity.
