# MATERIAL PACK — S0-04 (compression contract; the sanctioned deterministic stub behind real OmniRoute)

> EVIDENCE ONLY. Verbatim extraction + located inventory. No design, no judgement, no
> recommendation. Assembled 2026-09-07/08 from the working tree at branch
> `claude/soundbox-kit-migration-iz1jwf`, HEAD `cc46704`. Other lanes hold uncommitted edits.
> **The 18 defect classes and the mint-wide AF-AP rows are carried once in
> `material-S0-02.md` §7 — read that section with this pack.**

---

## 0. INVENTORY TABLE

| item | source file:line | exists? | venue |
|---|---|---|---|
| Seed per-proof block S0-04 | `seeds/seed-stage0-v1.yaml:406-422` | yes | — |
| Seed `spike_to_class_mapping` entry for S0-04 | `seeds/seed-stage0-v1.yaml:564-586`; `proofs/registry.yaml:29-35` | **no** — no rule names S0-04 (`spike_dependency: []`, seed:411) | — |
| Breakdown increment #15 | `tasks/stage0-breakdown.md:66` | yes | in-sandbox (row) / PC (venue update) |
| Pinned decision — stub is forbidden for S0-03, sanctioned here | `tasks/stage0-breakdown.md:21,25` | yes | — |
| Findings per-proof constraint | `docs/research/FINDINGS-STAGE0-v1.md:45` | yes | — |
| Findings §4 NO-STUBS carve-out | `docs/research/FINDINGS-STAGE0-v1.md:57-59` | yes | — |
| CLAUDE.md two-sanctioned-stubs statement | `CLAUDE.md:154-162` | yes | — |
| Council acceptable compromise 2 | `docs/research/COUNCIL-VERDICT-STAGE0-v1.md:27` | yes | — |
| Council next-step 5 (S0-04 mutation kill) | `docs/research/COUNCIL-VERDICT-STAGE0-v1.md:59` | yes | — |
| Plan-doc seam `docs/03` §2 | `docs/03_INTEGRATION_CONTRACTS.md:31-51` | yes | — |
| Plan-doc seam `docs/02` OmniRoute compression bullet | `docs/02_COMPONENT_AUDIT.md:54` | yes | — |
| ADR 0002 (compression-off header) | `docs/adr/0002-omniroute-sole-model-egress.md:12` | yes | — |
| upstream pin `omniroute` | `upstream.lock.yaml:21-26` | yes | — |
| `proofs/S0-04/` directory | `ls proofs/` | **no** | — |
| `proofs/S0-04/spec.json` / `result.json` / fixtures / checker | — | **no**; ledger state `ABSENT` | — |
| Registry entry S0-04 | `proofs/registry.yaml:15` | yes | — |
| Existing deterministic upstream instrument (sibling, S0-01) | `proofs/S0-01/tools/scripted_backend.py` (57 defs; docstring `:1-95`) | yes | PC (by absolute path) |
| Its tests | `tests/test_s0_01_scripted_backend.py` | yes | sandbox |
| Result/spec schemas S0-04 must satisfy | `proofs/schemas/result.schema.json`, `proofs/schemas/spec.schema.json` | yes | — |
| Minted exemplars (S0-07, S0-11 execution; S0-09 decision) | see `material-S0-02.md` §5.4 | yes | sandbox |
| Runner mint path / validator checks | `scripts/proof-runner:131-223`; `scripts/validate-ledger:216-342` | yes | either |
| OmniRoute live on the PC | `spikes/pc-bridge/result.json:19`; `PC-BRIDGE.md:153-163` | yes | PC |
| Transport deviation (`chat_completions` in the live profiles) | `docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md:17` | yes — OPEN owner decision (task #35) | PC |
| Wave-0 spike bearing on S0-04 | — | **none** — no spike's `classification_effect` names S0-04 | — |
| Blocked marker for S0-04 | — | **no** (execution_proof) | — |
| Ledger task row | `todo/BUILD-TASKLIST.md:72` (`s0-15-s0-04-compression … pending`) | yes | PC |

---

## 1. THE SEED

### 1.1 `seeds/seed-stage0-v1.yaml:406-422` (verbatim)

```yaml
- proof_id: S0-04
  classification: execution_proof
  wave: 2
  increment_index: 15
  ledger_denominator: execution
  spike_dependency: []
  fixture_format: deterministic stub UPSTREAM (the one sanctioned boundary instrument)
    behind REAL OmniRoute; committed request fixtures
  assertions:
  - the Hermes-side request carries 'x-omniroute-compression: off'
  - the response carries the X-OmniRoute-Compression header reporting off
  - the stub upstream's received request byte-compares equal to the sent fixture
    (request preservation)
  negative_control:
    mutation: mutate OmniRoute's real header-set path in the mutation audit -> proof RED
    expected_failure_reason: 'compression-header-missing'
  owner_placeholder: none
```

### 1.2 Frozen `spike_to_class_mapping` entry for S0-04

**NOT SPECIFIED in `seeds/seed-stage0-v1.yaml` or `proofs/registry.yaml`** — no mapping rule's
`affected_proof` is `S0-04`; the seed block carries `spike_dependency: []` (`:411`) and
`proofs/registry.yaml:15` carries `"spike_dependencies": []`.

### 1.3 Seed constraints binding S0-04 (`seeds/seed-stage0-v1.yaml:106-113`, verbatim excerpts)

```yaml
- Execution proofs are exactly S0-01, S0-02, S0-04, S0-05-mechanism, S0-07, S0-11;
  conformance-checked decisions are exactly S0-09, S0-10, S0-12
- Every proof ships a spec-time negative control that fails for a named exact reason
- All gates are deterministic and LLM-free; no LLM judge anywhere in the gate spine
```

Seed constraint on the machinery order (`:121-122`, verbatim):
```yaml
- Shared machinery (schemas, runner harness, ledger generator, CI validator, mutation
  audit) is specified as numbered increments preceding any proof increment
```

---

## 2. THE BREAKDOWN

### 2.1 Increment #15 (`tasks/stage0-breakdown.md:66`, verbatim row)

```
| 15 | S0-04 compression contract | `proofs/s0-04/` + the ONE sanctioned deterministic upstream stub behind real OmniRoute | Request carries `x-omniroute-compression: off`; response `X-OmniRoute-Compression` asserted; stub-received request byte-equals sent fixture | Mutate OmniRoute's real header path ⇒ RED (`compression-header-missing`) | in-sandbox (Wave 2, after #14's OmniRoute install) |
```

### 2.2 Pinned decisions with rejected alternatives that bear on S0-04 (`tasks/stage0-breakdown.md:21,25`, verbatim)

```
| Committed canonical fixtures drive the REAL pinned binaries; normalized-then-golden compare; `expected_failure_reason` inside each negative fixture | Byte-exact goldens (volatile fields) / test-time generation (oracle drift) / stub of the SUT (NO-STUBS) | interview Q3 |
```
```
| S0-03 blocks on a real credential; pass asserts upstream model identity, never a 200; the S0-04 stub is forbidden for S0-03 | Run S0-03 against the S0-04 stub (stub-drift hollow green) | council (Socrates) |
```

Full table: `material-S0-02.md` §2.2.

### 2.3 Venue update clause (`tasks/stage0-breakdown.md:31`, verbatim excerpt)

```
podman-compose stacks for S0-01/S0-02 (#7, #8), S0-03/S0-04 (#14, #15) and
S0-06 (#13); S0-05's full canaries (#16).
```

**Contradiction recorded, not resolved:** the increment table's venue cell for #15 reads
`in-sandbox (Wave 2, after #14's OmniRoute install)` (`:66`) while the venue update and
`PC-BRIDGE.md:69` assign S0-03/S0-04 (OmniRoute + vLLM upstream) to the PC.

### 2.4 Ordering rationale clause (`tasks/stage0-breakdown.md:74-75`, verbatim excerpt)

```
#14–16 the
spine (credential-gated S0-03 first so its RED-pending state is visible early);
```

### 2.5 NOT-built ledger lines touching S0-04

Breakdown-time (`:79-82`): "Nothing below exists yet: … any proof, any fixture …".
Live (`todo/BUILD-TASKLIST.md:32`, verbatim excerpt): "· ABSENT 4 — S0-02, S0-04, S0-05, S0-06".
Live task row (`todo/BUILD-TASKLIST.md:72`, verbatim):
```
| s0-15-s0-04-compression | #15 S0-04 compression contract (sanctioned stub behind real OmniRoute) | pending | s0-14 | header asserts; request preservation; header-path mutation → RED |
```

### 2.6 Owner answers (`tasks/stage0-breakdown.md:84-89`)

None names S0-04. The credential answer for #14 (quoted in `material-S0-03.md` §2.3) is the
upstream dependency the #15 row declares (`blocked-by: s0-14`).

---

## 3. FINDINGS + COUNCIL

### 3.1 Per-proof constraint (`docs/research/FINDINGS-STAGE0-v1.md:45`, verbatim)

```
| S0-04 | Compression contract | `x-omniroute-compression: off` + assert `X-OmniRoute-Compression` response header + deterministic stub upstream proving request preservation — the stub is the planned boundary instrument (`02` §2, `03` §2), not a spine stub |
```

### 3.2 Cross-cutting invariant naming S0-04's stub (`docs/research/FINDINGS-STAGE0-v1.md:57-59`, verbatim)

```
- NO STUBS in the spine (CLAUDE.md #1): every proof exercises the REAL pinned component; the
  one sanctioned stub is S0-04's deterministic upstream-request-preservation instrument, which
  sits BEHIND real OmniRoute at the boundary the plan itself specifies.
```

**Superseded count, recorded:** the findings say "the one sanctioned stub"; `CLAUDE.md:156-162`
now says TWO (see §4.6 below), the second added 2026-09-04 for S0-01's golden.

### 3.3 Environment rows (`docs/research/FINDINGS-STAGE0-v1.md:22,28`, verbatim)

```
| Node 22.22.2 / npm 10.9.7 | present | OmniRoute (3.8.51, Node) plausibly runnable in-sandbox |
```
```
| **PC bridge** (learned 2026-09-03 from the owner) | The owner's PC is the execution host: Fedora 42 bare metal (KVM), podman + podman-compose, local vLLM OpenAI-compatible endpoint `localhost:8010/v1` (`sim9b`), reached via a token-gated HTTP bridge with per-session ephemeral links (`PC-BRIDGE.md`) | S0-08 (runsc/KVM), all container stacks (Buzz relay, OmniRoute, ai-memory), and S0-03's model upstream run THERE. No third-party model credential is needed: OmniRoute's upstream = the PC's vLLM, identity asserted as `sim9b` |
```

Capability ledger: `material-S0-02.md` §3.1.

### 3.4 Council lines that touch S0-04 (verbatim)

Acceptable compromise 2 (`docs/research/COUNCIL-VERDICT-STAGE0-v1.md:27`):
```
2. **S0-04's deterministic upstream stub stands as the one sanctioned instrument**, because the plan itself specifies it at the boundary behind real OmniRoute (findings §4). This is a boundary instrument, not a spine stub.
```

Recommended next step 5 (`:59`, verbatim; the S0-04 clause):
```
5. Author every proof's negative control at spec time, before its positive leg, each naming the exact expected error or exit code. Feynman's four kills are the seed set: S0-05 asserts the exact denial reason and dies when the gate is mutated off; S0-04 dies when OmniRoute's real header-set code is mutated; S0-02 demands four *distinct* error reasons, not four failures; S0-08's `NOT run here` marker is grep-checked and gates Stage 1.
```

Socrates' key insight, which binds S0-03 and S0-04 together (`:75`):
```
- **Socrates** — *stub-drift as the pack's characteristic hollow green.* S0-03 and S0-04 both terminate at OmniRoute's upstream edge; if S0-03 runs against the sanctioned S0-04 instrument, the instrument silently becomes the spine and S0-03 proves only that Hermes reaches OmniRoute — never that a model answered. The remedy (assert upstream model identity, with a credential-disable kill switch) is the strongest single control the council produced. Equally sharp: a gate that cannot fail is not a proof, and counting it inflates the denominator.
```

Wave placement (seed constraint `seeds/seed-stage0-v1.yaml:103-105`): "Wave 2 spine
(S0-03/04/05)".

No Kill Criterion names S0-04 (`docs/research/COUNCIL-VERDICT-STAGE0-v1.md:32-39`: KC-1 S0-05,
KC-2 S0-03, KC-3 S0-06, KC-4 status lines, KC-5 negative controls, KC-6 dockerd/S0-08, KC-7 S0-07
clearance measurement).

---

## 4. PLAN-DOC SEAMS AND PINS

### 4.1 `docs/03_INTEGRATION_CONTRACTS.md:31-51` (verbatim — §2, the contract S0-04 encodes)

```
## 2. Hermes → OmniRoute

```yaml
providers:
  factory-router:
    base_url: http://omniroute:20128/v1
    api_mode: codex_responses
    key_env: OMNIROUTE_INTERNAL_API_KEY
    extra_headers:
      x-omniroute-compression: "off"
```

Required assertions:

- Hermes has no upstream provider key and cannot reach public model endpoints.
- A `/v1/responses` request streams text and completes a real Hermes tool-call round trip.
- OmniRoute reports compression off, and a deterministic stub proves request preservation.
- OmniRoute failure does not trigger direct fallback.
- State is persistent; bootstrap secrets are non-default; provider setup is explicit and audited.
- `codex_app_server` and OpenAI Codex OAuth remain disabled.
```

### 4.2 `docs/02_COMPONENT_AUDIT.md:54` (verbatim — the header-name facts and the dead variable)

```
- The old `OMNIROUTE_COMPRESSION_CODE_LANE` variable is unsupported. Send `x-omniroute-compression: off`, assert `X-OmniRoute-Compression`, and compare a deterministic stub request at the boundary.
```

Surrounding OmniRoute bullets (`docs/02_COMPONENT_AUDIT.md:49-56`) are quoted verbatim in
`material-S0-03.md` §4.2.

`docs/02_COMPONENT_AUDIT.md:27` (verbatim — the Hermes capability the header rides on):
```
- Custom providers support `base_url`, `api_mode`, `key_env`, and `extra_headers`.
```

### 4.3 `docs/01_ARCHITECTURE.md:118` (verbatim)

```
| Hermes → OmniRoute | Internal scoped key, fixed base URL, no upstream keys, compression assertion |
```

### 4.4 `docs/07_BUILD_PLAN.md:12` (verbatim)

```
| S0-04 | Compression contract | Response header plus deterministic stub request preservation |
```

### 4.5 `docs/adr/0002-omniroute-sole-model-egress.md:12` (verbatim)

```
All model and embedding traffic uses internal, scoped OmniRoute credentials and tested routes. Provider credentials exist only in OmniRoute. Hermes uses `codex_responses` against the internal `/v1` endpoint and sends the compression-off header.
```

### 4.6 `CLAUDE.md:154-162` (verbatim — the two sanctioned stubs, the project's own rule)

```
**Every benchmark/eval MUST exercise the ACTUAL pipeline**, score against a **real independent
oracle**, and report the **hollow-green (gate-false-positive) rate**. A harness that
re-implements or stubs the spine it claims to prove is forbidden. In THIS project the
sanctioned stubs are TWO, both sitting BEHIND real OmniRoute at the boundary the plan itself specifies
(`docs/03` §2): S0-04's deterministic upstream-request-preservation instrument, and S0-01's deterministic
scripted model backend behind a dedicated OmniRoute test route (owner-sanctioned 2026-09-04 for the
golden, after two live runs proved the model route's ACP event structure non-reproducible) — every other
proof exercises the REAL pinned component, and a proof that cannot run in the sandbox runs on the PC or
is delivered as spec + fixture + an explicit `NOT run here: <reason>` marker, never a fake green.
```

### 4.7 `docs/09_PREMORTEM.md:8` (verbatim — the failure mode S0-04's byte-compare targets)

```
| 2 | OmniRoute works for text but corrupts/drops tool calls | Text test passes; tool args change or hang | Real tool round-trip and deterministic gateway fixture |
```

### 4.8 `upstream.lock.yaml:21-26` (verbatim)

```yaml
  omniroute:
    repository: https://github.com/diegosouzapw/OmniRoute.git
    commit: 488f57e9d3fccc8d1741fdf21d35d5730b118a18
    observed_version: 3.8.51
    license: MIT
    role: sole_model_api_gateway
```

`docs/08_DECISION_LOG.md:25` (D-019) records why this pin advanced — quoted verbatim in
`material-S0-03.md` §4.8. `upstream.lock.yaml:10-15` pins `hermes-agent` at
`527da60844d4dced37879ea50259675371abe10e` (v0.21.0), the client side of the header.

### 4.9 `.env.example:24` (verbatim)

```
OMNIROUTE_INTERNAL_API_KEY=replace-from-omniroute-key-creation
```

**NOT SPECIFIED in `.env.example`:** no compression variable — consistent with
`docs/02:54` ("The old `OMNIROUTE_COMPRESSION_CODE_LANE` variable is unsupported"); the header is
set through the Hermes provider's `extra_headers`, per `docs/03` §2.

---

## 5. WHAT EXISTS TODAY

### 5.1 `ls -la proofs/S0-04/`

```
ls: cannot access 'proofs/S0-04/': No such file or directory
```

No spec, no checker, no fixtures, no result, no blocked marker.

### 5.2 Registry entry (`proofs/registry.yaml:15`, verbatim)

```json
  {"proof_id": "S0-04", "title": "Compression contract", "classification": "execution_proof", "wave": 2, "spike_dependencies": [], "required_negative_controls": 1, "assertion_count": 3},
```

Ledger state (`proofs/ledger.json`):
```json
    {
      "classification": "execution_proof",
      "proof_id": "S0-04",
      "state": "ABSENT"
    },
```

### 5.3 Schemas the artifact must satisfy

Full verbatim `spec.schema.json` and `result.schema.json` bodies are in `material-S0-02.md` §5.3.
Points that bind S0-04's shape:
- `spec.schema.json:11-17` — at least two legs, at least one `positive` and one `negative`.
- `spec.schema.json:40-41` — a `negative` leg MUST carry `expect.failure_reason`.
- `spec.schema.json:27` — `cwd` must be relative and may not traverse (`^(?!/)(?!.*(^|/)\.\.(/|$)).*$`).
- `spec.schema.json:28` — `timeout_s` ∈ [1, 3600].
- `result.schema.json:10` — `classification` enum `["execution_proof",
  "conformance_checked_decision"]`.
- `result.schema.json:12` — `env_fingerprint` must match `^(pc-bridge|sandbox):.+$`.
- `result.schema.json:31-36` — `attestation` is required and non-empty.

### 5.4 Exemplars

S0-07 and S0-11 (`execution_proof`) and S0-09 (`conformance_checked_decision`): full verbatim
`spec.json`, `graft skeleton` of each checker, and S0-07's complete `result.json` attestation
block are in `material-S0-02.md` §5.4.

### 5.5 Runner and validator

`scripts/proof-runner:131-223` (mint) and `:226-271` (probe) — verbatim in `material-S0-02.md`
§5.5 and `material-S0-03.md` §5.6. `scripts/validate-ledger` check map — `material-S0-02.md` §5.6.

The two runner behaviours that most constrain an S0-04 spec:
- a leg exiting **2** is a DEFER that PRESERVES the previous artifact (`scripts/proof-runner:181-185`);
- a negative leg's `expect.failure_reason` must appear as a **substring of some stdout/stderr
  line** (`:192-199`), and the validator re-checks that binding against the attested spec
  (`scripts/validate-ledger:303-306`).

### 5.6 The existing deterministic-upstream instrument (S0-01's, the sibling sanctioned stub)

`proofs/S0-01/tools/scripted_backend.py` — module docstring `:1-20` (verbatim):

```python
#!/usr/bin/env python3
"""S0-01 deterministic scripted model backend — the golden's upstream, BEHIND real OmniRoute.

Owner-sanctioned 2026-09-04 ("a deterministic scripted backend behind a dedicated OmniRoute test
route"), needed because two live runs proved the model route's ACP event structure non-reproducible
(proofs/S0-01/evidence/determinism-live-route.json). Everything under test stays REAL — buzz-acp,
hermes-acp, OmniRoute's routing and credential handling; only the model upstream is scripted.
Not S0-03 evidence. Stdlib only; runs on the PC by absolute path.

OpenAI-compatible surface (what OmniRoute's `openai-compatible` provider speaks):
  GET  /v1/models                -> the two scripted models
  POST /v1/chat/completions      -> `s0-01-pong`: reply "pong" (stream or not), never a tool call
                                    `s0-01-slow`: the same reply streamed as 4 chunks with a delay
                                    between them (the cancellation leg needs a turn that is still
                                    running when session/cancel arrives)
Auth: every request must carry `Authorization: Bearer <token>`; the token is read from
`--token-file` (a 0600 file with `UPSTREAM_TOKEN=...`), never from argv. A request without it gets
401 — this proves the call came through OmniRoute carrying the connection's configured credential.
Authorization equality is == (Bearer <token>X -> 401; Bearer <token> extra -> 401).
/healthz matches the exact path only (/healthzXYZ -> 401 + record).
```

Its request-recording contract (the mechanism an S0-04 byte-compare would meet) — docstring
`:90-95` (verbatim):

```
Not recorded: GET /healthz (operational, pre-auth); any gate rejection (TE, dup CL,
  malformed CL, oversized CL, GET with CL > 0, defects, obs-fold, Expect,
  JSON depth > MAX_JSON_DEPTH, short body). These all close the connection.  Duplicate non-framing headers collapse to the last value in
  the record (email.message.Message.items() yields all, but dict() takes the last --
  documented, not a defect; the dropped duplicate values are discarded and
  unrecoverable from the record).
```

`graft skeleton proofs/S0-01/tools/scripted_backend.py` — the recording/serving surface (verbatim
tail of the tool output):

```
- L366-L383  function _iter_json_strings  def _iter_json_strings(obj)
- L386-L387  function _fingerprint  def _fingerprint(value: str) -> str
- L390-L396  function load_token  def load_token(path: Path) -> str
- L399-L409  function _validate_slow_delay  def _validate_slow_delay(s)
- L412-L443  function _json_safe  def _json_safe(o)
- L446-L538  class State  class State
- L447-L452  method __init__  def __init__(self, token: str, record_dir: Path, slow_delay: float)
- L454-L477  method _carries_secret  def _carries_secret(self, s: str, *, byte_view: bool) -> bool
- L479-L538  method record  def record(self, method: str, path: str, headers, body, remote_addr: str, bearer_token: str | None, *, raw_body: bytes | None = None) -> tuple[int, bool]
- L541-L752  function make_handler  def make_handler(state: State)
- L542-L750  class Handler  class Handler(BaseHTTPRequestHandler)
- L547-L548  method log_message  def log_message(self, fmt, *args): # quiet; the record dir is the log
- L551-L555  method _reject  def _reject(self, code: int)
- L557-L603  method _framing_gate  def _framing_gate(self) -> bool
- L605-L608  method handle_expect_100  def handle_expect_100(self)
- L611-L619  method _send_json  def _send_json(self, code: int, obj, extra=None)
- L621-L623  method _error  def _error(self, code: int, message: str, err_type: str, err_code: str)
- L625-L627  method _authorized  def _authorized(self) -> bool
- L629-L631  method _bearer_token  def _bearer_token(self)
- L633-L658  method _read_body  def _read_body(self)
- L661-L682  method do_GET  def do_GET(self)
- L684-L723  method do_POST  def do_POST(self)
- L725-L750  method _stream  def _stream(self, model: str)
- L734-L736  function emit  def emit(obj)
- L755-L803  function main  def main(argv=None) -> int
```

**Recorded fact, not a recommendation:** this instrument speaks
`POST /v1/chat/completions` (docstring `:11-15`), while `docs/03` §2 pins
`api_mode: codex_responses` and the S0-04 assertion set is about
`x-omniroute-compression` / `X-OmniRoute-Compression`. The docstring makes no mention of
compression headers; `grep -in "compression" proofs/S0-01/tools/scripted_backend.py` → no match.

Its committed tests: `tests/test_s0_01_scripted_backend.py` (in `tests/`, run by
`.github/workflows/stage0-ci.yml:20-23` with `S0_01_VENUE: ci`).

---

## 6. VENUE FACTS

### 6.1 Which host each leg needs

`PC-BRIDGE.md:66-70` (verbatim) — quoted in full in `material-S0-02.md` §6.1; the S0-04 clause:
"- **PC via bridge:** … S0-03/S0-04 (OmniRoute + vLLM upstream) …".

`PC-BRIDGE.md:70` (verbatim): "- Every bridge-side proof still writes the same `result.json`
artifact family; the runner records `env_fingerprint = pc-bridge:<hostname>` so ledger entries
name their venue."

`PC-BRIDGE.md:153-163` (the authoritative OmniRoute unit, env-file load order, and the
"health 200 says nothing about WHICH instance answers" rule) — verbatim in `material-S0-03.md`
§6.1.

Sandbox alternative recorded by the findings (`docs/research/FINDINGS-STAGE0-v1.md:22`): "Node
22.22.2 / npm 10.9.7 | present | OmniRoute (3.8.51, Node) plausibly runnable in-sandbox" — the
word used is "plausibly"; no probe of an in-sandbox OmniRoute run exists in `spikes/`.

### 6.2 What the Wave-0 spikes proved for S0-04

**No spike names S0-04.** `spikes/*/result.json` `classification_effect` entries name S0-03
(pc-bridge), S0-05 (selective-egress), S0-06 (rust-ai-memory, pc-bridge), S0-08 (runsc, dockerd,
pc-bridge). The OmniRoute facts S0-04 would rely on come from the `pc-bridge` spike
(`spikes/pc-bridge/result.json:19`, verbatim):

```json
  "omniroute": "port 20128 listening on 0.0.0.0 -> HTTP 307 to /dashboard (OmniRoute already running)",
```

and its `not_verified` list (`:52-56`, verbatim) explicitly leaves open: "who launched OmniRoute
on 20128 and its persistence/config state".

### 6.3 The live transport deviation (`docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md:17`, verbatim)

```
> | Hermes transport | DEVIATION from ADR 0002 / `docs/03_INTEGRATION_CONTRACTS.md` §2 (`api_mode: codex_responses`, `x-omniroute-compression: off`): both repaired profiles use `chat_completions`. Owner decision (task #35): amend the ADR or revert the transport. The pinned S0-01 Hermes (0.21.0) supports both modes and per-provider `extra_headers` |
```

Task row for that decision (`todo/BUILD-TASKLIST.md:262`, verbatim excerpt): "`owner-adr-0002-wire-mode`
(#35, OWNER decision)".

### 6.4 Observability

`docs/OBSERVABILITY-RUNBOOK.md:44-46` (verbatim): "`NOT built.` here: no exporter, no envelope
emitter, no dashboards wired — this runbook records the live PC endpoints and the lessons so the
first telemetry increment starts from facts."

### 6.5 Blocked marker

**None.** S0-04 is `execution_proof` (`proofs/registry.yaml:15`); no `blocked` object, no
`probe.json`, no `blocked.json`.

---

## 7. CLASS PREFLIGHT

**The 18 defect classes** — verbatim in `material-S0-02.md` §7.2-§7.3.
**Mint-wide AF-AP rows** (AF-AP-36, AF-AP-56, AF-AP-27, AF-AP-29, AF-AP-30) — verbatim in
`material-S0-02.md` §7.5.

### 7.1 AF-AP rows whose mechanism names the S0-04 subject (headers, config echoes, OmniRoute, stub-vs-real)

`docs/INCIDENT-LOG.md:182` (AF-AP-38 — presence instead of exact value; the class an
`X-OmniRoute-Compression` assertion sits in):
```
| AF-AP-38 | presence instead of exact value — a checker asserts that a configuration/echo field EXISTS or is truthy where the contract pins a VALUE, so drift (and outright contract breaches) pass | `if echo.get(x):` / `assert field` on a contract-pinned value; a capture that echoes a default the contract forbids and still passes | S0-01 2026-09-05: `max_turn` accepted `1s` and the recorded `7200s` while docs/03 pins `BUZZ_ACP_MAX_TURN_DURATION=3600`; four checkers per the owner's review | OPEN(2026-09-05) — every contract-pinned value is asserted EXACTLY against the contract document's value; each exact assertion has a mutant test (one off / default / absent) |
```

`docs/INCIDENT-LOG.md:185` (AF-AP-41 — last-wins parse of an echo; header duplication is the same
mechanism, and the scripted backend's own docstring `:92-95` records that duplicate non-framing
headers collapse to the last value in its record): quoted verbatim in `material-S0-02.md` §7.4.

`docs/INCIDENT-LOG.md:186` (AF-AP-42 — fixture-shaped hollow green; names the header **key case**
mismatch between a synthetic fixture and the real backend): quoted verbatim in
`material-S0-02.md` §7.4.

`docs/INCIDENT-LOG.md:184` (AF-AP-40 — presence-gated check; a required artifact made optional):
```
| AF-AP-40 | presence-gated check — `if path.exists(): check()` in a checker turns a required artifact into an optional one: deleting the file switches the check off and the success line still prints (fail-open by omission) | `if\s+\w[\w.]*\.(exists/is_dir/is_file)\(\)\s*:` guarding an assertion in `proofs/**/check_*.py`; a required-file list that is only consulted when the file is present | S0-01 2026-09-05 verify round 1: 40+ hostile bundles PASSed the new checker because every optional-if artifact could simply be deleted | OPEN(2026-09-05) — once a bundle claims completeness every required artifact is REQUIRED (absence = Failure naming leg + file); deferral exists only for "nothing captured"; edit-snapshot screen row; recurrence 2 (2026-09-06): round-5 lane A5 wrote `if mentions_dir is not None and mentions_dir.is_dir():` around the NEW two-users ingress-concurrency assertion while closing the audit's findings — the class named in its own brief; caught by the lane's self-report, fixed in lane A5b; recurrence 3 (2026-09-06): the coordinator's OWN amendment A20d inverted the class — it demanded a non-empty scan where a successful shutdown produces an empty one; the correct evidence is an enumeration header, not rows (Codex audit of 541648c) |
```

`docs/INCIDENT-LOG.md:177` (AF-AP-33 — health-200 ≠ the right OmniRoute instance): quoted verbatim
in `material-S0-03.md` §7.1.

`docs/INCIDENT-LOG.md:179` (AF-AP-35 — redaction keyed on the secret's VALUE; the scripted
backend's `_carries_secret` screen is the class's countermeasure): quoted verbatim in
`material-S0-03.md` §7.1.

`docs/INCIDENT-LOG.md:191` (AF-AP-47 — guard narrowed to a specimen; the framing/`Content-Length`
domain finding came out of exactly this instrument class, "2026-09-06 D5b"): quoted verbatim in
`material-S0-02.md` §7.4.

`docs/INCIDENT-LOG.md:171` (AF-AP-27 — a frozen seed contract, e.g. the `compression-header-missing`
expected reason, changed as a side effect): quoted verbatim in `material-S0-02.md` §7.5.
