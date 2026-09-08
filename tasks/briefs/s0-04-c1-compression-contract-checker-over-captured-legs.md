# Lane C1 — S0-04 compression contract: the checker over captured legs, the PC leg runner, the S0-01 backend as the sanctioned preservation instrument (sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".)

**Why:** S0-04 has nothing built (no `proofs/S0-04/`, ledger ABSENT). The seed (`seeds/seed-stage0-v1.yaml:406-422`): three assertions —
the Hermes-side request carries `x-omniroute-compression: off`; the response carries `X-OmniRoute-Compression` reporting off; the stub
upstream's received request byte-compares equal to the sent fixture — and the negative control `compression-header-missing`. The
contract is docs/03 §2 (the Hermes provider block with `extra_headers: x-omniroute-compression: "off"`) and docs/02:54 ("send
`x-omniroute-compression: off`, assert `X-OmniRoute-Compression`, and compare a deterministic stub request at the boundary").
**Inputs (read in this order):** `tasks/briefs/stage0-parallel-support/material-S0-04.md` (whole) · the sanctioned instrument
`proofs/S0-01/tools/scripted_backend.py` (its `State.record` writes every request VERBATIM — headers lowercased, body verbatim, `raw_body`
where the D5k round pinned it — read `record()` and the record file shape; its tests `tests/test_s0_01_scripted_backend.py` show the record
files) · task #36 in `todo/BUILD-TASKLIST.md` (the OmniRoute provider connection `s0-01-scripted` → `http://127.0.0.1:20201/v1` on the PC —
the model ids it exposes) · `docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md` and `PC-BRIDGE.md` (OmniRoute :20128, `REQUIRE_API_KEY=true`, the live
Hermes profiles use `chat_completions` — owner task #35 records the ADR deviation; do not resolve it, record it) · the exemplar specs
(S0-07, S0-11) and `proofs/schemas/spec.schema.json`.
**Scope (all NEW + one test + your report):** `proofs/S0-04/spec.json` · `proofs/S0-04/check_compression.py` · `proofs/S0-04/fixtures/`
(the sent request fixture with a nonce; a synthetic PASSING bundle; the NEGATIVE bundles) · `proofs/S0-04/tools/pc/run_s0_04_legs.sh` +
`capture_leg.py` (PC-side) · `tests/test_s0_04_compression.py` · report `tasks/briefs/s0-04-support/C1-report.md`. Nothing under
`proofs/S0-01/` is edited (the backend is USED, by absolute path on the PC, by import in tests). Shared-tree rules as every lane: never
`git stash/checkout/restore/reset/add/commit/push`; gates from a `git archive <PIN>` copy under
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/c1/ + your files; explicit `--basetemp`; kill only your own
processes by pid; NEVER background a run and stop; no outward actions; NO PC bridge; never read or print credentials — the OmniRoute key
is read IN PLACE on the PC by the runner (an env file path, never a value in any artifact; the captured headers REDACT `authorization`
before writing, and the checker REJECTS a bundle that carries a bearer value — the S0-01 `_STDERR_LEAK_RE` idea).

## Design (pinned — build it, do not redesign it)
1. **The instrument is the S0-01 scripted backend** — no new stub (the project sanctions exactly two stubs; S0-04's is "the deterministic
   upstream-request-preservation instrument" and the S0-01 backend already records requests verbatim behind the real OmniRoute route
   `s0-01-scripted`). The runner starts it on the PC (or uses the running one — by pid file, never by name), points the leg at OmniRoute's
   `s0-01-scripted` provider, and reads the record dir for the request carrying the fixture's nonce.
2. **The sent fixture** `fixtures/request-<name>.json`: `{"method": "POST", "path": "/v1/chat/completions", "headers": {"content-type":
   "application/json", "x-omniroute-compression": "off"}, "body_b64": "<a chat-completions body with model s0-01-pong and a nonce string
   in the user message>"}`; the body is committed as BYTES (b64) so the byte-compare is exact; a second fixture with a 64 KB body (a long
   user message) — the size where a compressing proxy would act.
3. **The evidence bundle per leg** (`evidence/<leg>/`): `request.json` (the fixture as sent + the exact argv/URL used), `response.json`
   (status, headers verbatim with `authorization` redacted at capture, body_b64), `upstream-record.json` (the backend's record file for the
   nonce, copied verbatim), `hermes-provider.json` (the provider block of the PC Hermes profile with the key REDACTED at capture — only
   `base_url`, `api_mode`, `key_env` NAME, `extra_headers`). Captured by `capture_leg.py` on the PC (stdlib `http.client` against
   `127.0.0.1:20128`, the key from the env file named by `OMNIROUTE_KEY_FILE`, read in place).
4. **The checker `check_compression.py <evidence-root>`** — deterministic: leg `off`: response header `x-omniroute-compression` (case-
   insensitive name) present with value exactly `off` (else `compression-header-missing` when absent, `compression-header-value: <v>` when
   present with another value); the upstream record's body bytes == the fixture's body bytes (else `request-not-preserved: first diff at
   byte N` — print the offset, never the bodies); the record's nonce == the fixture's; the record's headers carry no `x-omniroute-compression`
   directive (OmniRoute consumed it — RECORD the observation; assert only what docs/03 requires); the 64 KB leg the same; leg `config`:
   `hermes-provider.json` has `extra_headers["x-omniroute-compression"] == "off"`, `base_url` ends with `:20128/v1`, `key_env` is a NAME
   (no value), `api_mode` RECORDED (the ADR deviation goes into the report, not the verdict — owner task #35). Absent root ⇒ `deferred:
   S0-04 evidence not captured` exit 2. Reads under the S_ISREG rule. Any bundle file containing a bearer-shaped value ⇒ FAIL
   `credential-in-evidence`. PASS line `PASS: S0-04 compression-contract - 3 assertions over N legs`.
5. **The negative control** = a committed bundle whose response lacks the header (`fixtures/evidence-header-missing/`) ⇒ exit 1 with
   `failure_reason: compression-header-missing` (exact); a second committed bundle whose upstream record differs by one byte ⇒
   `request-not-preserved: first diff at byte N`. The seed's "mutate OmniRoute's real header-set path" is NOT done (never modify the owner's
   running OmniRoute) — say so under DISCREPANCIES with the substitute.
6. **`spec.json`**: positive `check_compression.py proofs/S0-04/evidence` (expect 0), negative `check_compression.py
   proofs/S0-04/fixtures/evidence-header-missing` (expect 1 + `failure_reason: compression-header-missing`). The evidence root does not
   exist yet — `deferred:` exit 2 shown in the report.
7. **The PC runner `tools/pc/run_s0_04_legs.sh`** (NOT run here): preflight `curl -s http://127.0.0.1:20128/api/health` and the
   `s0-01-scripted` model listing through OmniRoute; ensure the S0-01 backend is up (its pidfile from the S0-01 tools; start it the
   S0-01 way if not, record dir under `~/s0-01-pinned/records/s0-04-<run>`); run `capture_leg.py` for each fixture; copy the record; write
   `hermes-provider.json` from the profile with redaction; `bash -n` clean; every external call listed.
8. **Tests**: the checker over a synthetic passing bundle built from the fixtures (exit 0, the PASS line); both negative bundles (exact
   reasons); header name case-insensitivity; a value `on` ⇒ `compression-header-value: on`; the nonce mismatch; the bearer-in-evidence
   rejection; the FIFO read; `deferred:`; the fixture bytes round-trip (b64 → bytes → b64 identical); a test that the S0-01 backend's
   record shape the checker reads is the CURRENT one (import `scripted_backend` and record one request through a live local instance —
   the S0-01 tests show how). Preflight the 18 classes.
9. **Report discipline**: report_lint MISS 0, ap_screen classified, file:line by grep, counts pasted twice, pyflakes + bash -n, census.

## Mutants (≥ 10): HEADER-ABSENT-ACCEPTED · HEADER-VALUE-ON-ACCEPTED · BODY-DIFF-ACCEPTED · NONCE-MISMATCH-ACCEPTED · BEARER-IN-EVIDENCE-ACCEPTED ·
CONFIG-HEADER-MISSING-ACCEPTED · FIFO-HANG · DEFERRED-AS-PASS · CASE-SENSITIVE-HEADER (a `X-OmniRoute-Compression` spelled differently must
still pass) · OFFSET-WRONG (the diff offset must be the first differing byte).

## Report shape
FILE IDENTITY · DONE (assertion → capture field → checker rule → test) · mutants · NOT_DONE (the PC legs; the config capture) ·
DISCREPANCIES (the mutation control substitute; `chat_completions` vs `codex_responses`; anything the pack got wrong) · SELF-ATTACK.
