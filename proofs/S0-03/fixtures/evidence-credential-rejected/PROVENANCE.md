# PROVENANCE — evidence-credential-rejected

A NEGATIVE control, minted BY ITS OWN WRITER. AF-AP-42 (fixture-shaped hollow green) demands that
every file say where its shape came from and, where the shape is not yet proven against a live
producer, that it say so instead of implying it is.

The whole bundle is what a real negative leg writes, with four volatile fields frozen so the
committed bytes are stable (`nonce`, `started_at`, `finished_at`, `duration_ms`, and `url`, which
points at the PC's OmniRoute rather than at the scratch port the mint used).

| file | shape derived from | proven against a live capture? |
|---|---|---|
| `direct/direct.json` | **the real writer, run**: `proofs/S0-03/tools/pc/direct_responses_probe.py (with a scratch key file)` against a local 401 server, through the committed helper `tests/test_s0_03_omniroute.py::build_direct_401_record`. `test_credential_fixture_matches_the_writers_key_set` re-runs that producer every suite run and compares the key set and `credential_presented` (AF-AP-42). | request side **YES** (the writer built it); response side `NOT proven against a live capture` — see below |
| `omniroute-requests.json` | the real writer, `proofs/S0-03/tools/pc/collect_leg.sh` on a negative root: no response id and no hermes turn means no rows, and an empty export is the honest result rather than an error. Exercised by `test_collect_leg_on_a_negative_root_writes_an_honest_empty_export`. | **NO** — the `call_logs` rows have not been read on the PC. |

## Which parts came from the local server, and which from OmniRoute's source

The 401 the writer recorded was served by a `http.server` handler on 127.0.0.1 whose body and
headers are TRANSCRIBED from the pinned OmniRoute `488f57e9`:

  * the body `{"error": {"code", "message", "correlation_id"}}` — `src/server/authz/pipeline.ts:79-95`
    (`rejectionResponse`), rendering `src/server/authz/policies/clientApi.ts:96`
    (`reject(401, "AUTH_002", 'Invalid API key')`).
  * the two response headers `x-request-id` and `x-omniroute-route-class` —
    `src/server/authz/headers.ts:15` and `:17`, set on the rejection at `pipeline.ts:93-94`.

Everything else in `response_headers` is the LOCAL SERVER'S OWN: `server: BaseHTTP/0.6 …`,
`date`, and `content-length` are python's, not OmniRoute's, and they are left verbatim rather
than dressed up — a fixture that hid them would be claiming a live capture it did not have. The
`correlation_id` value `req_2b8e0f31` is the local server's constant, not a real request id.

Not transcribed and NOT proven: that the owner's deployment answers an unauthenticated request
401 at all. `clientApi.ts:73-75` returns `allow({kind:"anonymous"})` first when `REQUIRE_API_KEY`
is off, so a live negative leg could legitimately observe 200. That is a FINDING about the
deployment for the PC run to report, and the runner prints the observed status.

## What this bundle is for

The seed's OTHER credential verdict (`seeds/seed-stage0-v1.yaml:400-402`):
`reason_enum: [credential_absent, credential_rejected]` and "**credential_rejected maps to
proof-RED, never to blocked**".

A key WAS presented (`credential_presented: true`, `Authorization: <redacted>` in the header
names) and OmniRoute refused it. The checker must report
`credential_rejected: OmniRoute refused the presented key (HTTP 401)` and exit 1 — never the
blocked reason. Before this round the checker had no `credential_rejected` reason at all and its
kill switch turned ANY 401 into `blocked: credential_absent`, i.e. a refused credential became a
deferral (VERIFY-O1 F-5, mutant V4).
