# S0-04 compression contract — live-capture findings (2026-09-19)

The runner (`tools/pc/run_s0_04_legs.sh` + `capture_leg.py`) ran on the PC against the REAL
OmniRoute on `:20128` and the REAL S0-01 scripted backend on `:20201` (the persistent process
pid 2725343, recording to `.markers/upstream-records-v2-20260906T050930Z`). Head `ef58a28`
(routing fix `760b876` + find-record baseline `325d762`). Evidence: `/tmp/s0-04-cap2` on the PC.

## What is PROVEN LIVE (the core capability)

The compression-off directive is honoured end to end through real OmniRoute to the real scripted
upstream, with the request preserved. Both request legs (`off`, `off-large`) returned HTTP 200
and produced a full evidence triple.

- **A1 — the Hermes-side request carries `x-omniroute-compression: off`.** Checker-VALIDATED: the
  captured `request.json` equals the committed fixture byte for byte and the sent header value is
  `off` (`check_request_leg` passed A1 on both legs).
- **A2 — the response reports compression off.** The response header is present with the value
  `x-omniroute-compression: off; source=request-header` on BOTH legs. The STATE is `off`, and the
  `source=request-header` parameter is OmniRoute confirming it HONOURED our request directive (not
  a default). This is the mechanism the proof exists to demonstrate. (Checker fix pending — see
  Deviation 2.)
- **A3 — the upstream received the preserved request.** Evidence CAPTURED: the backend record
  `030102.json` (`off`) / `030103.json` (`off-large`) carries the exact request body — `model:
  s0-01-pong`, the probe message with `nonce=s0-04-nonce-3f5c9a1b7d2e4068`, `sort_keys`. (Checker
  validation of A3 is gated behind the A2 fix — `check_request_leg` stops at A2.)

The find-record baseline fix works exactly as designed against the persistent backend: `off`
baseline seq 30101 -> wrote 030102 (unique past the baseline); `off-large` baseline 30102 ->
wrote 030103. No stale-record ambiguity, no false pass.

## Deviations from the plan-doc assumptions (the live run FOUND these)

The checker/fixtures/producer were written from `docs/03 §2` (an ILLUSTRATIVE contract). The real
OmniRoute + Hermes disagree in three places. None is a stub or a shortcut — they are reality the
proof must grade against.

**Deviation 1 — the Hermes profile schema (the config leg). OWNER DECISION.**
`check_config_leg` requires the provider block to expose `base_url` (ends `:20128/v1`), a non-empty
`api_mode`, and `extra_headers: {x-omniroute-compression: off}`. `capture_leg.provider_block`
reads those same field names. But the REAL Hermes custom-provider schema (verified live, and used
by the proven-live `proofs/S0-03/hermes/config.yaml`) is `api` / `transport` / `key_env` /
`extra_headers` — NOT `base_url` / `api_mode`. And the live production `omniroute-fedora` provider
carries NO `extra_headers` at all. So the producer emitted `base_url: null, api_mode: null,
extra_headers: {}` and the config leg fails three ways.
This is a genuine design fork (it changes what the proof CLAIMS and whether it reads mutable
production state):
  - **Option A — read the LIVE production `omniroute-fedora` profile.** Requires the owner to add
    `extra_headers: {x-omniroute-compression: "off"}` to that provider (a one-line profile edit;
    the docs/03 §2 contract says production SHOULD carry it, so this fixes a real config gap).
    Strongest as a production-config check; but the proof then depends on mutable live state.
  - **Option B — a committed proof-owned `proofs/S0-04/hermes/config.yaml`** (mirroring S0-03's
    proven-live shape, with the compression `extra_headers`). Reproducible, no owner action, no
    live-state dependency; but reading our own committed config makes the config leg a
    contract-EXPRESSION check, not a live proof (the live honouring is proven by A2's
    `source=request-header` and by S0-03's live Hermes run).
Either way `capture_leg.provider_block` must be realigned to the real Hermes field names
(`api`->base_url, `transport`->api_mode, `extra_headers`).

**Deviation 2 — the response header value format (grade against reality).**
The checker asserts the whole value `== "off"`; the real value is `off; source=request-header`.
Fix: parse the STATE (`value.split(";")[0].strip() == "off"`, AF-AP-38: not mere presence) and
assert `source=request-header` (the structural signature that OmniRoute honoured OUR request
header — closing the hollow green where a gateway that ignored the header but defaults to off would
still read `off`). Touches `check_request_leg` A2 + the committed golden `response.json` in the
`evidence-pass` and `evidence-body-diff` bundles (regenerate to the real value) + the tests.

**Deviation 3 (implied) — the committed golden fixtures carry the STALE bare `off` value.** They
predate this live capture. Regenerating the response goldens to `off; source=request-header` is
part of Deviation 2's fix; the negative-control bundles must still fail for their intended reason
(`evidence-header-missing` keeps no compression header; `evidence-body-diff` keeps the real value
and still fails at A3).

## Ordered remaining work (nothing minted until all hold)

1. **Owner decides Deviation 1** (config leg: Option A live-profile+edit, or Option B proof-owned
   config). Recommendation deferred to the owner — it is a proof-integrity + reproducibility call.
2. **One realignment increment** — `capture_leg.provider_block` to the real schema; `check_config_leg`
   per the chosen option; A2 parse + source assertion (Deviation 2); regenerate the 3 fixture
   bundles' `response.json` (+ `hermes-provider.json` for the config option); update tests; a
   committed FAILING negative control per new binding (AF-AP-36) BEFORE re-mint.
3. **Re-capture on the PC** with the final tools -> a complete, gradeable bundle.
4. **Mint** — `proof-runner run --proof S0-04 --venue sandbox`, retire the deferral tests to the
   minted reality, `validate-ledger integrity` PRESENT, `ledger-gen`, ledger + task #18; class
   stays `execution_proof`.
