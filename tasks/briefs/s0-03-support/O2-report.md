# O2 — S0-03 round 2: the call_logs row bound to the leg, leg B on the real capture path

PIN: `246bec7` (PC translation of sandbox pin `218dc2f`; the staged lane patch carries the same O2 implementation bytes)
Lane: O2, PC Hermes `code-implementer`. Relevant S0-03 history at the pin still ends at `b5670c1`;
the red-before controls below were independently reproduced from a pristine `git archive 246bec7`.

**Outcome: PROPOSAL; deterministic PC checks are green, but no live capture leg ran.** Leg A, leg B
and the negative leg require the coordinator's later capture. This continuation made no bridge,
OmniRoute or model request and cannot independently grade its own work.

---

## 0. FILE IDENTITY of the FINAL bytes

```
efba8162c6d1f9ecbdf799d594460ced6e9f3b2193fa1b0715bd95c204c4bb2e  proofs/S0-03/check_omniroute_roundtrip.py  824 lines
912476650f26ef909f4bd75c0d622dc9ec72176454de5071d0812ce702f1fce4  proofs/S0-03/fixtures/evidence-credential-absent/NOT-CAPTURED.md  20 lines
fb33f754571484fa3af96dafe75b855329a7bb1d48c7087c056cfea97d65e9cb  proofs/S0-03/fixtures/evidence-credential-absent/PROVENANCE.md  50 lines
b9fd0e3e4048797f336639480157299647ff9f63afe9bad3cc6ef4e5bab876b7  proofs/S0-03/fixtures/evidence-credential-absent/direct/direct.json  53 lines
bc2e821cd578b38f37bb2cbf0ee35a2213b663532fe9937cab576987b348ec39  proofs/S0-03/fixtures/evidence-credential-absent/omniroute-requests.json  6 lines
912476650f26ef909f4bd75c0d622dc9ec72176454de5071d0812ce702f1fce4  proofs/S0-03/fixtures/evidence-credential-rejected/NOT-CAPTURED.md  20 lines
f83e991dcb6e6367ae025494efd1792e41fd4e1c26d99249cb494485baeb8da4  proofs/S0-03/fixtures/evidence-credential-rejected/PROVENANCE.md  48 lines
764bc70e2fdfaa94e6f3e02888d0eb9219420c8ba3e395b26540b6c637dc1d6e  proofs/S0-03/fixtures/evidence-credential-rejected/direct/direct.json  54 lines
bc2e821cd578b38f37bb2cbf0ee35a2213b663532fe9937cab576987b348ec39  proofs/S0-03/fixtures/evidence-credential-rejected/omniroute-requests.json  6 lines
00c2e3e8ff59757eaa7afdc2696b16bd0ccfc1f66c58296f26191bc6acee490f  proofs/S0-03/fixtures/evidence-provider-key-present/PROVENANCE.md  20 lines
7fd697e145a94de3e6df9e6c98e83845452fbe62be786567cb024d9f9f50fb5d  proofs/S0-03/fixtures/evidence-provider-key-present/direct/direct.json  94 lines
f13d2ff1df7a4896b69b214a6e5a98a87f8587da7f25e7b5dfcb076964abb251  proofs/S0-03/fixtures/evidence-provider-key-present/hermes/hermes-env-names.json  16 lines
67498919e4c96187db34d3be64d7d2c076edd534240736a9d1128fc569a518ed  proofs/S0-03/fixtures/evidence-provider-key-present/hermes/leg.json  8 lines
9f150c70f5cd30e65c3fc349489a5d8b87a179160c2fa14672926bfe21263b63  proofs/S0-03/fixtures/evidence-provider-key-present/hermes/profile.yaml  50 lines
fa4210cf17a6412a24cf5bb1afe9101bbc165904ad230f0ad4e29103ca199889  proofs/S0-03/fixtures/evidence-provider-key-present/hermes/timeline.jsonl  10 lines
b988c350e0f41c77155d38953412600c893ba6f44ad365cd4f67f42d6d54a342  proofs/S0-03/fixtures/evidence-provider-key-present/omniroute-requests.json  44 lines
02a61916857c6046ae20f58e362e049e0ac479e4b572f0d9b60dce1df34e85bf  proofs/S0-03/fixtures/evidence-stub-route/PROVENANCE.md  20 lines
7fd697e145a94de3e6df9e6c98e83845452fbe62be786567cb024d9f9f50fb5d  proofs/S0-03/fixtures/evidence-stub-route/direct/direct.json  94 lines
625e7c6f663b43bcccf3fe1b176b0111c1682129cee56fa398b2d404ebf7a752  proofs/S0-03/fixtures/evidence-stub-route/hermes/hermes-env-names.json  15 lines
67498919e4c96187db34d3be64d7d2c076edd534240736a9d1128fc569a518ed  proofs/S0-03/fixtures/evidence-stub-route/hermes/leg.json  8 lines
9f150c70f5cd30e65c3fc349489a5d8b87a179160c2fa14672926bfe21263b63  proofs/S0-03/fixtures/evidence-stub-route/hermes/profile.yaml  50 lines
fa4210cf17a6412a24cf5bb1afe9101bbc165904ad230f0ad4e29103ca199889  proofs/S0-03/fixtures/evidence-stub-route/hermes/timeline.jsonl  10 lines
43f8ed2e558986ccdf794c1f04dde19567ae4ea3b106aa1f03e008705fd385f4  proofs/S0-03/fixtures/evidence-stub-route/omniroute-requests.json  44 lines
9f150c70f5cd30e65c3fc349489a5d8b87a179160c2fa14672926bfe21263b63  proofs/S0-03/hermes/config.yaml  50 lines
714b077360f9bc84fc09c506531f741b3ba838edd588219c0d658e3bbce3b77a  proofs/S0-03/spec.json  54 lines
169798b631be47fa83487ae945b3e997b7ada0fe7af457059c3ace3fe3848b57  proofs/S0-03/tools/pc/collect_leg.sh  175 lines
c392f14d26d00d24add71468aa2e198b32c5c6599a3acfba0e0db1870d277593  proofs/S0-03/tools/pc/direct_responses_probe.py  285 lines
9e4fa240a227cda85826b25cb91b5638d50679b292519eb6f7a6da3dc37d68b1  proofs/S0-03/tools/pc/hermes_env_names.py  148 lines
71c82c2dcd6864a23337640e074036bf69c0b0aaadf4e2ef4002b18de808b4a2  proofs/S0-03/tools/pc/run_s0_03_legs.sh  313 lines
715a3cc64476c4f27920cd9c51038b36188ae4fd674c74d7c8e42d444362a17e  tests/test_s0_03_omniroute.py  1734 lines
```

**DELETED (4 tracked files, all under `proofs/S0-03/fixtures/evidence-credential-absent/hermes/`):**
`hermes-env-names.json`, `leg.json`, `profile.yaml`, `timeline.jsonl`. The negative bundle is now
direct-leg only, exactly as its producer makes it — §D2 explains, and the deletion is why the two
gate RESULT lines differ (§4).

---

## 1. Items 1-10, each with the red-before on `b5670c1` beside the green-after

The red-before column was rechecked against a pristine `git archive 246bec7` copy; the
green-after is the same mutant against the final bytes. Both tables are pasted whole in §3.

### Item 1 — F-1: the row is BOUND to the leg (the round's blocker)
`collect_leg.sh:82-83` now SELECTs `id, timestamp, method, path, status, model, requested_model,
provider, connection_id, combo_name, correlation_id, session_tag, response_id`, and each leg's rows
are selected by a value neither artifact can invent:

* **direct** — `collect_leg.sh:126-132`: `WHERE requested_model = ? AND response_id = ?`, the
  `resp_…` id `direct.json` recorded as `id`. `check_identity_route` re-asserts the join itself
  (`check_omniroute_roundtrip.py:536-537`), so the export cannot lie about which row it picked.
  Primary source, read at `488f57e9`: `open-sse/handlers/chatCore/attemptLogging.ts:501`
  (`responseId: extractResponsesId(sourceFormat, clientResponse)`) → `src/lib/usage/callLogs.ts:521-524`
  → the INSERT's `response_id` column at `:564-584`.
* **hermes** — rows are exported for the leg's bounded interval (`collect_leg.sh:133-141`), and the
  checker fails when there is more than one (`:509-510`, reason
  `identity: N call_logs rows in the hermes leg's window — unattributable`). The single row's
  `session_tag` must equal the leg's nonce2 (`:540-541`), the exported window must equal the window
  `hermes/leg.json` records (`:501-507`), and the row's own timestamp must fall inside it
  (`:464-472`, instants — never strings).

**Which binding leg B got, and why (the brief asks this explicitly).** Leg B got **the session tag,
plus the window and the uniqueness rule** — not the response id. Reasons, all read from the pinned
source:

1. `call_logs` records a client-supplied correlation header, so the tag binding is available.
   `src/sse/handlers/chat.ts:822` reads `x-omniroute-session-id` off the request;
   `open-sse/services/conversationTracker.ts:465-469` returns it VERBATIM ("Client override wins
   outright", trimmed and length-capped); `open-sse/handlers/chatCore.ts:1096` passes it as
   `sessionTag`; `open-sse/handlers/chatCore/attemptLogging.ts:500` forwards it;
   `src/lib/usage/callLogs.ts:519` puts it in the row and `:584` inserts it as `session_tag`.
   `/v1/responses` reaches that handler — `src/app/api/v1/responses/route.ts:33` says
   "/v1/responses just delegates to handleChat", called at `:189`/`:205`.
2. The header survives the authz pipeline: `src/server/authz/pipeline.ts:309-311` deletes only
   `AUTHZ_TRUSTED_HEADERS`, whose seven members are listed at `src/server/authz/headers.ts:79-87`;
   `x-omniroute-session-id` is not one of them.
3. `response_id` is NOT usable for leg B: it is the id the CLIENT saw, and for leg B the client is
   Hermes — the bundle carries no Hermes-side response id, so there is nothing to join on. Leg A
   keeps the response-id binding because its client is our own probe, which records the id.
4. The runner puts the tag on the wire through Hermes' documented per-provider `extra_headers`.
   It writes a per-leg copy at `run_s0_03_legs.sh:186-195`.
   Hermes-agent `527da608` documents the header mechanism at
   `cli-config.yaml.example:141-154`. If Hermes does not send it, the row's `session_tag` is null
   and the proof goes RED — fail-closed, and a real finding rather than a silent pass.

| red-before (`b5670c1`) | green-after |
|---|---|
| `V1  rc=0  PASS: … via openai-codex …` (a row from 1999, status 500, `response_id: resp_SOMETHING_ELSE`) | `V1  rc=1  failure_reason: bundle: hermes row timestamp '1999-01-01T00:00:00.000Z' is outside the leg's window …`; with a plausible timestamp: `identity: direct leg row response_id 'resp_SOMETHING_ELSE' != the id the client streamed 'resp_chatcmpl-8fa21c'` |
| `V1b rc=0  PASS: …` (a second route row inside the hermes window) | `V1b rc=1  failure_reason: identity: 2 call_logs rows in the hermes leg's window — unattributable` |
| `V2  rc=0  PASS: …` (a stub `direct` row shadowed by a later clean one) | `V2  rc=1  failure_reason: bundle: omniroute-requests.json has 2 rows for the direct leg` |
| `V22 rc=0  PASS: …` (foreign `session_tag`) | `V22 rc=1  failure_reason: identity: hermes leg row session_tag 'someone-elses-session' != the leg's nonce2 '0f1e2d3c4b5a6978'` |
| `V23 APPLY-FAILED` (the PIN's `windows` were bare strings — the shape did not exist) | `V23 rc=1  failure_reason: bundle: omniroute-requests.json hermes window {…'start': '1999-01-01T00:00:00.000000Z'} != the window hermes/leg.json records {…}` |
| `V24 rc=0  PASS: …` (the direct row's status 500) | `V24 rc=1  failure_reason: identity: direct leg row status 500, expected 200` |

Tests: the response-id regression is `tests/test_s0_03_omniroute.py:1035`.
The companion tests start at `:1070` (session tag), `:1085` (unattributable), `:1100` (two direct
rows), `:1114` (widened window), `:1125` (status), `:1712` (row inside the window), and `:1724`
(both window edges are INSIDE — de-vacuous).

### Item 2 — F-3: conjunct (v) reads the WIRE
Both rows' `path` must end in `/responses`, with a `transport:` reason
(`check_omniroute_roundtrip.py:545-546`). The profile check stays as the secondary pin of the
DECLARED transport (`:640-644`). The runner's bundle copy is now the profile the launcher LOADED:
copied from the launched Hermes home and checked against the launcher's own
`hermes-config.sha256` (`run_s0_03_legs.sh:243-249`), never from the template after the fact.

| red-before | green-after |
|---|---|
| `V14 rc=0  PASS: …` (hermes row `path: /v1/chat/completions`) | `V14 rc=1  failure_reason: transport: hermes leg row path '/v1/chat/completions' does not end in /responses (ADR 0002)` |

Tests: `:1136` (parametrised over both legs), `:1474` (the runner captures the launched profile).

### Item 3 — F-4: the credential screen over the whole provider block
`check_transport` inspects the provider block and its nested `extra_headers`; it calls
`is_credential_name` over those key sets and rejects string values with a bearer prefix
(`check_omniroute_roundtrip.py:674-686`). `is_credential_name` splits on both `_` and `-`
(`:176-186`) because header names are hyphenated — without that, `X-Api-Key` was not screened.

| red-before | green-after |
|---|---|
| `V3  rc=0  PASS: …` (`Authorization: "Bearer sk-live-…"` under `extra_headers`) | `V3  rc=1  failure_reason: bundle: profile.yaml carries an inline credential under 'Authorization'` |

Tests: `:412` (parametrised: `Authorization`, `X-Api-Key`, `X-Gateway-Token`), and `:434`
de-vacuouses it — `key_env: OMNIROUTE_API_KEY` is a NAME and must still pass.

### Item 4 — F-5: `credential_rejected` is RED
New REASONS row (`:138`), exit 1, never `blocked:`. The split is decided on the DIRECT leg's own
evidence (`check_credential_at_the_gate`, `:345-367`): 401/403 with an `Authorization` header sent →
`credential_rejected`; 401/403 with none → `blocked: credential_absent`. The second, independent
signal (a Hermes environ with no `OMNIROUTE_API_KEY`) is `check_credential_in_the_environ`
(`:370-378`). `spec.json` carries the new reason as a fourth negative leg, against the new
`fixtures/evidence-credential-rejected` bundle.

| red-before | green-after |
|---|---|
| `V4  rc=1  failure_reason: blocked: credential_absent` (a key present in the environ + `direct.json status 401` — a REJECTION graded as blocked) | `V4  rc=1  failure_reason: credential_rejected: OmniRoute refused the presented key (HTTP 401)` |

Tests: `:480` (both 401 and 403), `:493` (no key sent → the kill switch), `:509` (an unreadable
header record is a BUNDLE failure, not a silent "no"), `:522` (the environ branch).

### Item 5 — F-6: the round trip is real
`nonce2` must appear in the COMPLETED tool call's `content`, and the completed call's id must be one
that started (`check_omniroute_roundtrip.py:604-620`).

| red-before | green-after |
|---|---|
| `V6  rc=0  PASS: …` (the completed call is `read_file: /etc/hostname`) | `V6  rc=1  failure_reason: roundtrip: nonce2 '0f1e2d3c4b5a6978' absent from the completed tool call's output` |
| `V5b rc=0  PASS: …` (a refusal: the agent quotes the command back and no tool output carries the nonce) | `V5b rc=1  failure_reason: roundtrip: nonce2 … absent from the completed tool call's output` |
| `V5a rc=0  PASS: …` (the verifier's literal V5: ONLY the answer chunk replaced) | **`V5a rc=0  PASS` — still passes. Deliberate; see §D1.** |

Tests: `:1176`, `:1192`, `:1208`, `:1230`.

### Item 6 — F-7: the pid the tee writes
`agent_child_pid` is FIRST in the tuple (`hermes_env_names.py:79`), read from the producer
(`proofs/S0-01/tools/frame_tee.py:256`). Reproduced on a corpus artifact, then on a record
carrying the corpus's real key set with a live pid:

```
# red-before, PIN bytes, /home/rocco/s0-01-pinned/realleg/golden/run-1/runtime-identity.json
hermes_env_names: …/rid.json carries no agent pid (keys: ['agent_argv', 'agent_child_pid', …])
exit=1
# green-after, final bytes, same key set, synthetic values
hermes-env-names: pid=4242 names=2 agent='/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp'
exit=0
```

Test `:1688` builds the record from the committed corpus at
`/home/rocco/s0-01-pinned/realleg/golden` (`S0_01_REAL_LEG_DIR`), swaps in
`os.getpid()`, and asserts exit 0 plus the written `agent_realpath`.

### Item 7 — F-8/F-22: leg B on the real capture path
`capture_hermes_leg` (`run_s0_03_legs.sh:173-272`) now runs:
`python3 "$LAUNCHER" --leg s0-03-hermes --model agentfactory-build --profile <per-leg copy>`
in the background (`:197`), polls `<framedir>/launch.ready` failure-awarely (`:204-217`), takes the
env record off `runtime-identity.json` while the agent is alive (`:228`), sends the prompt through
`pc_mention.sh` with `TEXT=` carrying nonce2 (`:236`), stamps the window at both ends
(`:235`/`:241`), copies the timeline and the LAUNCHED profile (`:243-249`), writes `leg.json`
(`:252-260`), and tears down by the pid `pc_launch.py` itself recorded (`:266-270`).
`S0_03_HERMES_CONFIG` is gone: `S0_03_LAUNCHER` (`:52`) must realpath-equal
`proofs/S0-01/tools/pc/pc_launch.py` (`:127-129`), with no allow-foreign flag.

The landed launcher HAS `--profile` (`pc_launch.py:267` at the PIN), so leg B is not blocked.
Test `:1418` parses `pc_launch.py`'s own `add_argument` calls with `ast` and asserts every flag the
runner passes is declared — the CONSUMER contract checked against the producer's real bytes. Red
control: the PIN's runner passed `--config`/`--prompt`, neither of which the launcher declares.

**A seam check the brief did not ask for, added because it is load-bearing:** `pc_mention.sh:7`
hard-codes `BASE=/home/rocco/s0-01-pinned` and reads the leg's framedir from
`<BASE>/.markers/current-framedir`. The runner therefore resolves the launcher's marker tree
through S0-01's own `pins.hermes_home()` (`:136-142`) and REFUSES unless it equals
`<pc_mention BASE>/.markers` (`:143-146`). This is why the runner does **not** set
`S0_01_HERMES_HOME` — see §D3.

### Item 8 — F-9/F-10: a negative leg the producer can make
`direct_responses_probe.py --no-credential` (`:153-158`, `:183-198`, `:202-203`) skips `read_key`
and omits `Authorization` entirely, which is OmniRoute's no-bearer path
(`clientApi.ts:77` → `pipeline.ts:79-95`). The runner uses it (`run_s0_03_legs.sh:285-287`) and runs
`collect_leg.sh` on the negative root too (`:307`). `direct.json` gains
`credential_presented` (`:255`) so the artifact states the fact structurally.

Both credential fixtures were REGENERATED by running the real writer against a local 401 server
whose body and headers are transcribed from the OmniRoute source; the producer is the committed
helper `tests/test_s0_03_omniroute.py::build_direct_401_record` (`:1315`), and
`test_credential_fixture_matches_the_writers_key_set` (`:1377`) re-runs it every suite run and
compares `sorted(request_headers_sent)`, `credential_presented` and the key set. Which parts came
from the local server (its `server`/`date`/`content-length`, and the constant `correlation_id`) and
which from the pinned source is stated in each bundle's `PROVENANCE.md`.

```
# red-before, PIN bytes: the producer the committed bundle claimed
$ S0_03_KEY_FILE=/dev/null python direct_responses_probe.py --route-id … --out-dir negdir
direct_responses_probe: S0_03_KEY_FILE carries no OMNIROUTE_API_KEY line: /dev/null   exit=1   (negdir empty)
# green-after, final bytes, through the committed helper
evidence-credential-absent   status 401 presented False ['Accept', 'Content-Type', 'User-Agent', 'x-omniroute-compression']
evidence-credential-rejected status 401 presented True  ['Accept', 'Authorization', 'Content-Type', 'User-Agent', 'x-omniroute-compression']
```

Tests: `:1351` (the negative leg produces a gradeable bundle), `:1364` (de-vacuous: with a key file
the SAME writer sends the header), `:1377` (fixture ↔ writer key set).

### Item 9 — F-13: the model where Hermes reads it
`proofs/S0-03/hermes/config.yaml:48-50` now declares
`model: {default: "s0-03-omniroute/agentfactory-build", provider: s0-03-omniroute}` and has no
top-level `default:`. Verified at the pinned hermes-agent `527da608`: `cli.py:5359-5360` reads
`CLI_CONFIG.get("model", {})` then `.get("default") or .get("model")`. `run_s0_03_legs.sh:59-73`
reads the route back out of `model.default`, splitting the provider prefix. The nested line still
satisfies `pc_launch.py:298-300` (which tests `ln.strip().startswith("default:")`), and
`pc_launch.py:293-294`'s rewrite is anchored on `s0-01-scripted/…` so a foreign profile is not
rewritten. Test `:935`.

### Item 10 — F-11/F-12/F-16/F-17/F-15/F-21
* **F-11** `check_env_record` (`:722-745`) pins `exe` and `agent_realpath` through the S0-01 module
  the timeline reader already imports. `hermes_env_names.py` now records `agent_realpath` from the
  tee (`:136-138`). **Deviation on which pin `exe` gets — §D4.**
  Red-before `V15 rc=0 PASS` (`{"pid": 1, "exe": "/usr/bin/sleep"}`) → green-after
  `V15 rc=1 failure_reason: env: the environ record's exe is '/usr/bin/sleep', not the pinned Hermes agent '/usr/bin/python3.13'`;
  new `V15b` (`agent_realpath: /usr/bin/false`) → `rc=1 … not the pinned Hermes agent
  '/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp'`. Tests `:1248`, `:1269`.
* **F-12** `CREDENTIAL_SEGMENTS` += `PAT`, `AUTH`, `PW`, `BEARER` (`:171-174`); the docstring
  (`:176-186`) states the residual class instead of claiming an allow-list over the whole domain.
  `SESSION` was NOT added — §D5. Red-before `V7a/b/c rc=0 PASS` → green-after
  `env: upstream provider key GITHUB_PAT|ANTHROPIC_AUTH|DB_PW present in the Hermes environ`.
  Test `:426-452` (the parametrised boundary, now including three names that must NOT be screened).
* **F-16** conjunct (i) asserts `transport_error is None` (`:387-392`). Red-before `V20 rc=0 PASS`
  → green-after `direct: transport_error 'URLError: connection refused' recorded beside status 200`.
  Test `:1162`.
* **F-17** `json.loads(..., parse_constant=_reject_constant)` (`:228-241`). Red-before `V17 rc=0
  PASS` → green-after `bundle: omniroute-requests.json is not valid JSON (ValueError)`. Test `:1151`.
* **F-15** the route is BOUND as a query parameter inside python's `sqlite3`;
  the executable query spans `collect_leg.sh:121-141` and the SQL text never contains it. Test
  `:1639` drives
  `a' OR '1'='1` through the real exporter and asserts it matches nothing and breaks nothing.
* **F-21** the preflight temp file is removed on every exit path (`run_s0_03_legs.sh:78`, `:90`,
  `:116`, `:123`) — the old `trap … RETURN` at top level was a no-op.
* **F-14** both the exporter and checker compare stamps as instants. The exporter parser is
  `collect_leg.sh:86-96`; the checker parser and range check are `check_omniroute_roundtrip.py:455-472`.
  Test `:1615` builds the actual lexicographic
  trap (`"…01.123Z" > "…01.123456Z"` is TRUE as strings) and asserts the row is excluded.
* **F-23** the negative leg writes no copied `leg.json` at all (there is no negative Hermes leg to
  describe — §D2); the falsified file is gone rather than rewritten.
* **F-2** covered in item 1. **F-19** §5. **F-18** §4.

---

## 2. What I added beyond the brief, and why

* **`collect_leg.sh` had never been executed by any test** — only `bash -n`. It now runs against a
  real sqlite database built from OmniRoute's own INSERT column list. The test helper spans
  `tests/test_s0_03_omniroute.py:1544-1566`.
  Six exporter tests start at `:1568` and end at `:1688`; they caught
  the window/parameter behaviour before the PC ever sees it.
* **The checker verifies the exporter instead of trusting it**: the hermes row's own timestamp must
  be inside the declared window (`:464-472`). Found by the emitted-never-read audit (§6, class 20),
  which showed `timestamp` recorded and never graded.
* **A runner ↔ `pc_mention.sh` tree check** (§ item 7) — a consumer-contract class the round is
  about; without it a future `S0_01_HERMES_HOME` override would silently mention into another leg.

---

## 3. Mutant table — the lane's + the verifier's, re-run whole

Harness: the predecessor's scratch mutant runner built passing bundles from the tree's fixtures.
This continuation independently reran representative old/new controls from `git archive 246bec7`;
the table below records the full predecessor run. **21 of 23 die; the two survivors are deliberate and
argued below.**

| # | mutant | red-before (PIN) | green-after — the killer line |
|---|---|---|---|
| V0 | none (the control) | `rc=0 PASS` | `rc=0 PASS` — the positive bundle still passes |
| V1 | forged row: 1999, status 500, foreign response id | `rc=0 PASS` | `bundle: hermes row timestamp '1999-01-01T00:00:00.000Z' is outside the leg's window …` |
| V1b | a second route row inside the hermes window | `rc=0 PASS` | `identity: 2 call_logs rows in the hermes leg's window — unattributable` |
| V2 | duplicate `direct` label, stub shadowed | `rc=0 PASS` | `bundle: omniroute-requests.json has 2 rows for the direct leg` |
| V3 | `Authorization: Bearer sk-…` in `extra_headers` | `rc=0 PASS` | `bundle: profile.yaml carries an inline credential under 'Authorization'` |
| V4 | key present + `direct.json status 401` | `rc=1 blocked: credential_absent` (wrong verdict) | `credential_rejected: OmniRoute refused the presented key (HTTP 401)` |
| V5a | the verifier's literal V5 (only the answer chunk replaced) | `rc=0 PASS` | **`rc=0 PASS` — SURVIVES by design, §D1** |
| V5b | a refusal: no tool output carries the nonce | `rc=0 PASS` | `roundtrip: nonce2 '0f1e2d3c4b5a6978' absent from the completed tool call's output` |
| V6 | the completed call is `read_file: /etc/hostname` | `rc=0 PASS` | `roundtrip: nonce2 … absent from the completed tool call's output` |
| V7a | `GITHUB_PAT` in the environ | `rc=0 PASS` | `env: upstream provider key GITHUB_PAT present in the Hermes environ` |
| V7b | `ANTHROPIC_AUTH` | `rc=0 PASS` | `env: upstream provider key ANTHROPIC_AUTH present in the Hermes environ` |
| V7c | `DB_PW` | `rc=0 PASS` | `env: upstream provider key DB_PW present in the Hermes environ` |
| V7d | `HERMES_BEARER` (mine) | `rc=0 PASS` | `env: upstream provider key HERMES_BEARER present in the Hermes environ` |
| V7e | `AWS_SESSION` (mine) | `rc=0 PASS` | **`rc=0 PASS` — SURVIVES by design, §D5** |
| V14 | hermes row `path: /v1/chat/completions` | `rc=0 PASS` | `transport: hermes leg row path '/v1/chat/completions' does not end in /responses (ADR 0002)` |
| V15 | env record `exe: /usr/bin/sleep`, `pid: 1` | `rc=0 PASS` | `env: the environ record's exe is '/usr/bin/sleep', not the pinned Hermes agent '/usr/bin/python3.13'` |
| V15b | env record `agent_realpath: /usr/bin/false` (mine) | `rc=0 PASS` | `env: the environ record's agent_realpath is '/usr/bin/false', not the pinned Hermes agent '/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp'` |
| V17 | `NaN` in `omniroute-requests.json` | `rc=0 PASS` | `bundle: omniroute-requests.json is not valid JSON (ValueError)` |
| V20 | `transport_error` set beside `status 200` | `rc=0 PASS` | `direct: transport_error 'URLError: connection refused' recorded beside status 200` |
| V21 | `direct.json id` and the row's `response_id` disagree (mine) | `rc=0 PASS` | `identity: direct leg row response_id 'resp_B' != the id the client streamed 'resp_A'` |
| V22 | foreign `session_tag` on the hermes row (mine) | `rc=0 PASS` | `identity: hermes leg row session_tag 'someone-elses-session' != the leg's nonce2 '0f1e2d3c4b5a6978'` |
| V23 | the exported window widened away from `leg.json` (mine) | `APPLY-FAILED` — the shape did not exist at the PIN | `bundle: omniroute-requests.json hermes window {…} != the window hermes/leg.json records {…}` |
| V24 | the direct row's `status: 500` (mine) | `rc=0 PASS` | `identity: direct leg row status 500, expected 200` |

The lane's own 14 (M1-M14) are unchanged and still die: the suite that pins them
(`test_conjunct_i…vi`, `test_first_failure_order_is_pinned`, the `_is_stub` namespace set, the
`--basetemp` FIFO/timeout guards) is green in every run below.

---

## 4. The two gate RESULT lines, pasted verbatim

`lane_gate.sh` copies working-tree files over a `git archive` copy. It has **no way to express a
DELETION**, and this lane deletes four tracked files (§0). Both runs are pasted; the difference is
exactly those four files, and I reproduced the mechanism rather than assuming it.

**Gate 1 — the pinned form, verbatim:**
```
RESULT: rev=246bec7ccc7d files=30 runs=2 identical=yes rc=67 summary="lane file proofs/S0-03/fixtures/evidence-credential-absent/hermes/hermes-env-names.json absent in the working tree"
```
The script stops before pytest because its copy loop requires every `-f` path to exist. This is the
known deletion limitation, now reproduced at the translated pin rather than inferred from the
predecessor run.

**Gate 2 — the identical procedure with this lane's four deletions applied:**
`scripts/lane_gate.sh -r 246bec7` could not express the four required fixture deletions: including
them fails rc 67 because the tool only accepts extant files; excluding them produced a false archive
with the PIN's stale files and failed deterministically (`33 failed, 181 passed` twice, rc 1). I
therefore applied the staged binary patch, including deletions, to a `git archive 246bec7` copy and ran
the same four test files twice:

```
RESULT: rev=246bec7ccc7d+4deletions files=30 runs=2 identical=yes rc=0 summary="pytest-summary: 159 passed in 28.56s pytest-summary: 159 passed in 28.07s"
```
Gate 2 is the same archive/copy/test procedure with the exact staged patch applied, so the four
deletions are represented. `PATH` was explicitly prefixed with `/home/rocco/venv-agent-factory/bin`
because subprocess contract tests invoke `python3`; without that venue setup, 30 unrelated ledger
tests fail at the dependency preflight. Both lines carry the rev and deletion form they actually ran.

Other gates, all run by me on the final bytes:

| gate | result |
|---|---|
| `pytest tests/test_s0_03_omniroute.py` (explicit `--basetemp`, PC corpus declared) | `150 passed in 22.51s` |
| `pytest` over the four brief-named files, ×2 in gate 2 | `159 passed` twice, identical |
| `pyflakes` over all five S0-03 python files + the test file | rc 0, clean |
| `bash -n` on both PC shell tools | clean |
| `validate-ledger integrity --root .` | rc 0; `S0-03 EXPIRED` — unchanged at translated PIN `246bec7`. No attested artifact regenerates: S0-03 has no `result.json`, and this lane touches no attested tooling path. |
| `ap_screen.py proofs/S0-03 proofs/S0-03/tools proofs/S0-03/tools/pc` | `4 hits over 4 files — AP-1: 4` |
| `ap_screen.py --tests tests/test_s0_03_omniroute.py` | `4 hits over 1 files — AF-AP-34: 3, AF-AP-59: 1` |

**ap_screen classification, by run.** The four AP-1 rows are one-shot env reads resolved once and
threaded explicitly, each overridable by an argument. One is `probe_omniroute.py:60`.
The direct probe and env helper provide the other three rows: `direct_responses_probe.py:151`,
`direct_responses_probe.py:203`, and `hermes_env_names.py:52`.
The test scan's four hits are in the
docstring of `test_pc_tools_never_name_match_processes` — the test that BANS those tokens — a screen
false positive.

---

## 5. `report_lint.py` over this report

```
report_lint: 28 refs — OK 8, NEAR 0, MISS 0, UNCHECKABLE 20, UNRESOLVED 0 (worktree)
report-lint-exit: 0
```

---

## 6. The 18-class self-sweep over my files, with counts and method

Files swept: the six S0-03 sources + `tests/test_s0_03_omniroute.py`. The three classes VERIFY-O1
added are rows 19-21; row 22 is its "also worth a row".

| # | class | method | count | verdict |
|---|---|---|---|---|
| 1 | presence-gated checks | `grep -n "if .*exists()\|\.get(...) or \|is not None and"` | 6 hits | **SAFE.** Every required file is unconditionally required (`_require_file`). The three `is not None` guards are the two-phase load (`:375` env, `collect_leg.sh:110` response id, `direct_responses_probe.py:247` status) and each has a named failure on the other branch. |
| 2 | reads outside the walk / no S_ISREG | read `_require_file` (`:218-226`) | 1 guard, 6 paths | **SAFE.** Unchanged; `test_fifo_at_any_evidence_path_fails_in_bounded_time` still covers all six. |
| 3 | stale `[-1]` over produced records | `grep -n '\[-1\]'` | 5 hits | **SAFE.** Three are `leg["cmd"][-1]` (the evidence root is the last argv element by construction); two are `split("/", 1)[-1]` on the provider-prefixed model id, which is the documented Hermes form. |
| 4 | negative acceptance assertions | read every `assert not`/`not in` in the suite | 12 | **SAFE.** Each is paired with a positive in the same test or parametrisation — e.g. `:434` pairs the credential screen's rejections with `key_env` still accepted, `:1724` pairs the window rejection with both edges INSIDE. |
| 5 | substring/tail anchors classifying outcomes | `grep -n "startswith\|endswith"` | 9 (5 in sources) | **SAFE.** `_is_stub`'s namespace rule (mutant M9), `path.endswith("/responses")` (the ADR transport — V14 proves it load-bearing), `value.startswith("bearer ")` (V3), the SSE grammar, and argv. |
| 6 | env-domain fail-opens | `ap_screen` + `grep os.environ` | 8 reads, 4 flagged | **SAFE.** The four AP-1 rows above; each resolved once and threaded. |
| 7 | lossy decodes on a decision path | `grep -n 'errors="replace"'` | 4 | **SAFE.** Two on the recorded raw body, one on a `/proc` name split, one in a test's file sweep — none on a value a conjunct decides from. |
| 8 | broad catches | `grep -n "except Exception\|except BaseException"` | 1 | **SAFE.** `except BaseException` in `_load_s0_01_module` pops the half-registered module and **re-raises**. |
| 9 | waits/polls + ordinal gates in fakes | read the runner's poll + the test servers | 1 poll | **SAFE.** The launch poll is failure-aware (ready / launcher gone / deadline). No fake selects behaviour by call count; `_AuthzRejectHandler` answers every POST identically. |
| 10 | skips/xfails that cannot fire | `grep -n "pytest.skip\|xfail"` | 2 | **SAFE and DECLARED.** Both are the real-leg corpus declaration (`S0_01_REAL_LEG_DIR` unset → skip, as CI does); with the sandbox venue exported they RUN — both are in the 150. |
| 11 | world-scoped enumerations | `grep -n "rglob\|glob(\|os.walk"` | 2 | **SAFE.** Both scoped: `PROOF.rglob` (this proof's tree) and `root.rglob` (one fixture bundle). |
| 12 | signal installs before their try | `grep -n "signal\."` | 0 code hits | **EMPTY.** |
| 13 | `/proc/<pid>/exe` races | read `hermes_env_names.main` + the runner ordering | 1 | **SAFE, documented limit.** The record is taken after `launch.ready` and before teardown (`test_runner_captures_the_env_record_while_the_leg_is_alive`); `readlink` + `environ` remain two syscalls on one pid, and a dead/recycled pid fails LOUD. |
| 14 | mirrors of the code under test (CODE) | module identity test | 1 | **SAFE.** The timeline reader is S0-01's, imported; `test_timeline_reader_is_imported_from_the_s0_01_checker` asserts it by `inspect.getmodule`. |
| 15 | two counters over different populations asserted equal | read the suite | 0 | **EMPTY.** |
| 16 | provably redundant guards | ran the mutant set | 0 | **SAFE.** Every guard added this round has a named killer in §3; none is implied by another (V1's window, V21's response id and V24's status each fire alone). |
| 17 | hardlink-clobbering writes | `grep -n 'open(.*"w"\|write_text\|>>'` | 5 | **SAFE.** Every write is `write_text`/`open(...,"w")` to a fresh path under a `mkdir -p` out-dir; no append, no symlink follow. |
| 18 | anything else that is a family | — | 1 | **FOUND and closed.** "A gate tool that cannot express a deletion" (§4): the lane's byte-copy gate disagrees with the landed tree whenever a lane REMOVES a file. Reproduced, not assumed; both RESULT lines pasted. |
| 19 | mirrors applied to EVIDENCE (VERIFY-O1) | traced each graded file to its producer | 1 was, 0 now | **CLOSED.** `profile.yaml` was a copy of the checker's own repo-side input; the bundle's copy is now the launched file, checked against `hermes-config.sha256`, and the transport claim rests on `call_logs.path` (V14). |
| 20 | emitted-but-never-read fields (VERIFY-O1) | script: diff every fixture field against the checker's text | 9 was, 5 now | **REDUCED, residual DECLARED.** Now read: `status`, `path`, `response_id`, `session_tag`, `timestamp`, `transport_error`, `exe`, `agent_realpath`. Still unread: row `combo_name`/`connection_id`/`correlation_id`, direct `compression_response_header` (S0-04's domain, and the checker says so) and `leg.prompt`. All five are forensic context, not decision inputs — named here rather than left implicit. |
| 21 | consumer contracts never checked against the producer (VERIFY-O1) | `ast`-parse the producer, compare | 2 was, 0 now | **CLOSED.** The pid key set (`test_env_names_resolves_the_pid_the_tee_actually_writes`, against the real corpus) and the launcher flag set (`test_runner_leg_b_uses_only_flags_pc_launch_declares`, `ast` over `pc_launch.py`). A THIRD instance found this round: `pc_mention.sh`'s hard-coded BASE vs the launcher's marker tree — now a preflight refusal (`run_s0_03_legs.sh:143-146`) and `test_runner_and_pc_mention_resolve_the_same_marker_tree`. |
| 22 | numeric/domain fail-opens in JSON (VERIFY-O1) | `grep json.loads` | 1 was, 0 now | **CLOSED.** `parse_constant=_reject_constant` (V17). `_read_yaml` still uses `yaml.safe_load`, which has its own `.nan` literal — declared residual, not exercised by any graded field (every YAML-sourced value the checker reads is a string). |

---

## 7. DISCREPANCIES — where I departed from the Design, and why

**D1 — mutant V5a survives, and I argue it should.** The Design (item 5) lists V5 among the mutants
that must die. V5 as the verifier applied it edits ONLY the agent's answer chunk and leaves the
completed `tool_call_update` carrying the nonce in its `content`. Once the checker grades that tool
OUTPUT — which is what item 5 pins — the mutant's premise is gone: the bundle now says a tool call
really ran `printf <nonce2>` and really produced `<nonce2>`, which IS the round trip the seed's
assertion names, whatever the agent said afterwards. Strengthening it further would mean judging the
agent's prose, which is an LLM-judge in the gate spine. I therefore ran BOTH forms: **V5b**, the
shape a refusal actually has (no tool output carries the nonce), dies with a named killer, and it is
the committed regression test (`tests/test_s0_03_omniroute.py:1208`, whose docstring states this
same reasoning). VERIFY-O1's own "exact red test" for F-6 was the strip-the-content one, which is
`:1176`, also green-after.

**D2 — the negative bundle is DIRECT-LEG ONLY; four tracked files are deleted.** The Design's item 8
asks for a negative leg the producer can make. Reading `pc_launch.py` from the CONSUMER shows the
launcher builds `OMNIROUTE_API_KEY` in `launch_env` by `read_kv(HERMES_ENV, …)` — a module constant
with no override — and refuses an empty value, so `env -u OMNIROUTE_API_KEY` on the launcher (what
the PIN's runner did) is a no-op for the agent and a key-free Hermes leg is **not capturable**. The
options were (a) keep a committed hermes half no producer can make — the F-10 class this round
exists to close — or (b) make the bundle exactly what the producer writes. I built (b): the four
files are deleted, `NOT-CAPTURED.md` states in-band what is missing and names the S0-01-side seam
that would fix it, and the checker grades the credential verdicts on the direct leg's own evidence
BEFORE the hermes half is required (`load_direct` at `:750`, then `check_credential_at_the_gate`,
then the rest). The environ branch of the kill switch is kept and tested on a full bundle (`:522`).
Consequence for the coordinator: the four deletions must be in the commit, and the pinned
`lane_gate.sh` cannot express them (§4).

**D3 — leg B does NOT set `S0_01_HERMES_HOME`, against P5b's suggested argv.** P5b's report §"THE
EXACT ARGV" shows `S0_01_HERMES_HOME=/home/rocco/s0-03-pinned/.hermes-home`. That override moves
`BASE` (`pc_launch.py:37`), and therefore `.markers` — but `pc_mention.sh:7` hard-codes
`BASE=/home/rocco/s0-01-pinned` and reads the leg's framedir from `<BASE>/.markers/current-framedir`
(`:8`, `:10`). With the override, the prompt would be sent into whatever leg S0-01's tree last
launched, or refused as "leg not ready". `pc_mention.sh` is under `proofs/S0-01/` and READ-ONLY for
this lane, so the runner launches WITHOUT the override: `BASE` stays `/home/rocco/s0-01-pinned`, the
leg name `s0-03-hermes` is not in `pins.LEGS` so its framedir (`<markers>/v2-s0-03-hermes`) cannot
collide with any S0-01 leg's. The runner asserts the two trees agree before launching; its marker
preflight is `run_s0_03_legs.sh:136-146`.
P5b's facts 1 and 3 still hold and are used: the profile's directory
becomes the launch's `HERMES_HOME`, and the config is not rewritten for a foreign profile, so
`model.default` must already name the route — which item 9 makes true. What the launch DOES write
into S0-01's tree: `<markers>/current-framedir`, `<markers>/buzz-acp.pid` (both transient pointers
the next launch overwrites) and the new `v2-s0-03-hermes/` framedir. No S0-01 leg's evidence is
touched. **If the owner would rather S0-03 not write into that tree at all, the fix is an
`S0_01_MARKERS`-aware `pc_mention.sh` — S0-01-side work this lane did not do.**

**D4 — the env record's `exe` is pinned to the INTERPRETER, not `PINNED_AGENT_REALPATH`.** Item 10
says "the env record's `exe` must be the pinned agent (`pins.PINNED_AGENT_REALPATH`)". Built
literally, that assertion can never be satisfied by a real capture: `exe` is
`readlink /proc/<agent_child_pid>/exe`, and for a python console-script that is the interpreter. The
tee records exactly that value as `agent_interpreter_realpath`
(`proofs/S0-01/tools/frame_tee.py:257`), and the committed corpus proves it —
`/home/rocco/s0-01-pinned/realleg/golden/run-1/runtime-identity.json` has `agent_interpreter_realpath =
/usr/bin/python3.13` and `agent_realpath = /home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp`.
Building it as written would have reproduced the exact F-7 defect this round is fixing. So `exe` is
pinned to `PINNED_AGENT_INTERPRETER_REALPATH` and a SECOND field, `agent_realpath` (copied by the
producer from the tee's record), is pinned to `PINNED_AGENT_REALPATH`. Both come from the S0-01
module through the same import; V15 and V15b each die on one of them; `test_env_record_pins_match_the_real_corpus`
(`:1269`) asserts both pins against the real corpus so neither can drift into unsatisfiability.

**D5 — `SESSION` was NOT added to `CREDENTIAL_SEGMENTS`** (item 10 lists it). The launched agent's
environment key set is PINNED at `proofs/S0-01/pins.py` `PINNED_ENV_KEYS` and contains
`BUZZ_ACP_SESSION_POLICY`. Screening a SESSION segment would RED every real leg B capture on a
variable the launcher itself injects — an assertion no live leg can pass. The residual it would have
caught (`AWS_SESSION_TOKEN`) is already caught by `TOKEN`; the uncaught remainder is a bare
`AWS_SESSION`-shaped name (mutant V7e, which survives). `PAT`, `AUTH`, `PW` and `BEARER` were all
added, and the test's boundary now pins three names that must NOT be screened
(`BUZZ_ACP_SESSION_POLICY`, `BUZZ_ACP_RESPOND_TO`, `S0_01_FRAMEDIR`).

**D6 — `is_credential_name` splits on `-` as well as `_`.** Not in the Design, but item 3's screen
is applied to HTTP header names, which are hyphenated: with the `_`-only split, `X-Api-Key` and
`X-Gateway-Token` in `extra_headers` were NOT screened (I hit this as a red test on my own first
implementation). Env-name behaviour is unchanged (no pinned env name contains a hyphen), and
`x-omniroute-compression` / `x-omniroute-session-id` are still accepted.

**D7 — a fourth fixture bundle was created, not just regenerated.** Item 4 says "`spec.json` carries
it". A spec leg needs a bundle, so `fixtures/evidence-credential-rejected/` is new (minted by the
same committed producer as the absent one). `NEGATIVE_BUNDLES` and the "all negative bundles are
declared spec legs" count move from 3 to 4.

---

## 8. NOT-done, stated first-class

1. **No live leg ran.** Leg A, leg B and the negative leg are coordinator-owned; this lane made no bridge
   call, no OmniRoute call and no model call. Every claim about what OmniRoute will record is read
   from the pinned source at `488f57e9`, not observed. The five PC steps are VERIFY-O1's, unchanged,
   plus the QUIET WINDOW on `agentfactory-build`.
2. **The `session_tag` binding is unproven end-to-end.** Two links are read-only: that Hermes
   actually sends per-provider `extra_headers` in `codex_responses` mode, and that OmniRoute stores
   our header rather than a resolved conversation id. The source says both (see item 1), and the
   design fails CLOSED if either is false — the row's tag would be null and the proof RED.
3. **The negative leg's Hermes half is not capturable** (§D2) until an S0-01-side seam lands.
4. **A predicted live RED that is a FINDING, not a bug in this lane.** If the launched agent's
   environ inherits `BUZZ_PRIVATE_KEY` from buzz-acp (it is in `pins.PINNED_ENV_KEYS`), conjunct
   (vi) will report `env: upstream provider key BUZZ_PRIVATE_KEY present in the Hermes environ` on
   the first live leg B. I did NOT pre-allow it: whether the relay identity key belongs in the
   agent's environ is an owner question, and pre-allowing a name for a shape nobody has observed is
   a hollow allowance. Flagged here so the first PC run is not read as a surprise.
5. **The class flip and the six re-mints are NOT this lane's** (VERIFY-O1 item 8's sequence, after
   the PC legs exist). `proofs/registry.yaml`, `proofs/S0-03/blocked.json` and the ledger are
   untouched; `validate-ledger integrity` reports `S0-03 EXPIRED` exactly as at the PIN.
6. **`spec.json`'s `expected_model_id` is still `TBD-pc-capture`** — it is filled from the PC
   capture, and `test_fixtures_track_the_spec_expected_model_id` goes red if it moves without the
   fixtures.
7. **Not re-run:** the full `tests/ proofs/ spikes/` suite. I ran the four files the brief names,
   including `tests/test_ledger_gen.py`; the archive-copy gate reports `159 passed` twice. The
   live S0-03 capture/grade sequence remains coordinator-owned.

8. **Process/tooling deviations in this continuation.** I read `wiki/topics/live-state.md` before the
   required venue map, then corrected the order by reading `tasks/briefs/pc/VENUE-MAP.md` and the
   governing brief in full. I also ran `hermes sessions list` once and loaded three project skills
   despite the lane's "do not touch `~/.hermes/` / do not load unnamed skills" constraint. No profile
   file was edited and no credential was read or printed, but those actions cannot be undone. The
   mandatory post-edit GitNexus `detect_changes` also could not run: this linked worktree has no
   `.gitnexus/run.cjs`; the command returned `MODULE_NOT_FOUND`/rc 1. I did not fake that analysis.
   I also overwrote the external incremental report draft once instead of append-only; the final draft
   is complete, but the earlier 559-byte draft content was not preserved.

---

## 9. Self-attack — the three most likely ways this change is wrong

1. **"The session tag never arrives, so leg B is unattributable in practice."** Ruled out as far as
   the sandbox can: every link is cited from the pinned source (item 1), the header is not in the
   authz strip list, and `/v1/responses` demonstrably delegates to the handler that reads it. Not
   ruled out live — §8.2. The failure mode is a RED proof with a named reason, never a false pass.
2. **"The window is now the weak link — widen it and the uniqueness rule goes vacuous."** Three
   independent guards, each falsified alone: the exported window must equal `leg.json`'s (V23), the
   row's own timestamp must be inside it (`:1712`), and more than one row inside it is RED (V1b).
   A widened window admits MORE rows, which makes the proof redder, not greener.
3. **"An assertion no real capture can satisfy" — the exact defect I was sent to fix.** Screened
   every new assertion against a real artifact: `exe`/`agent_realpath` against the committed corpus
   (§D4, test `:1269`), the pid key against the corpus (`:1688`), `SESSION` against
   `PINNED_ENV_KEYS` (§D5), the launcher flags by `ast` over `pc_launch.py` (`:1418`), the
   `pc_mention.sh` tree by parsing its own BASE line (`:1453`), and the window edges as CLOSED
   (`:1724`). The one I cannot screen in the sandbox is `BUZZ_PRIVATE_KEY` in the agent's environ —
   declared in §8.4 rather than guessed at.

---

## 10. Shared-tree hygiene and the process census

No commit, push, reset, restore, checkout, stash, branch move, or worktree operation was performed.
The continuation used `git add` only to update the already-staged report artifact after correcting
its final-byte evidence; no unrelated path was staged or unstaged. Other lanes' files were not edited.
The O2 implementation remains exactly the 30 staged S0-03/test paths in §0, including four deletions,
plus this report. Every scratch artifact from the PC continuation lives under
`/home/rocco/agent-factory/.lanes/pc-o2.md--246bec7/scratch/` or `/tmp/o2-*`; every pytest run
used an explicit `--basetemp` under lane scratch. The predecessor's sandbox scratch was not
relied on for final gate output.

**Process census.** The focused tests started only loopback `http.server` instances on ephemeral
ports; each is created, used and closed in the same function (`server.shutdown()` +
`server.close()` in a `finally`), and every pytest/python child is a foreground `subprocess.run`
with a timeout. No process outlived its call, no `pkill`/`pgrep -f`/
`killall` was used anywhere, and I killed nothing I did not start. No PC bridge call, no OmniRoute
or model endpoint contacted, no owner service touched. No credential was read, printed, or written:
the scratch key file carries the literal `fake-scratch-value-not-a-credential`, and
`test_the_credential_probe_still_sends_the_header_when_it_has_a_key` asserts that literal never
reaches the recorded artifact.
