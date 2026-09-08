# VERIFY-O1 — adversarial grade of lane O1 (S0-03), PIN `b5670c1`

**Verdict: NOT-READY.** The sandbox artefacts are real, the suite is green on both venues, and the
probe fix is correct and reproduced end to end. But the proof's central claim — *upstream model
identity* — rests on a file that **nothing binds to the leg**, and the two live legs cannot run:
leg B is blocked by three seam mismatches (not one), and the negative leg's producer cannot make
the bundle the committed fixture depicts. Twelve of my hostile bundles passed the checker.

Everything below marked **reproduced** I ran myself at the PIN. Nothing in my verdict rests on an
unreproduced claim except F-14 and F-15, which are marked UNSURE and labelled in place.

---

## 0. Mechanical gates (all run by me, pasted)

| gate | result |
|---|---|
| `report_lint.py … --rev b5670c1 --map C/T/P` | `30 refs — OK 12, NEAR 0, **MISS 1**, UNCHECKABLE 0, UNRESOLVED 17 (at b5670c1)` |
| `report_lint.py …` (worktree, 2026-09-08 03:52Z) | `13 refs — OK 10, NEAR 0, **MISS 3**, UNCHECKABLE 0, UNRESOLVED 0 (worktree)` |
| `ap_screen.py proofs/S0-03 proofs/S0-03/tools proofs/S0-03/tools/pc` | `4 hits over 4 files — AP-1: 4` (matches the report) |
| `ap_screen.py --tests tests/test_s0_03_omniroute.py` | `4 hits over 1 file — AF-AP-34: 3, AF-AP-59: 1` (matches) |
| `test_summary.sh tests/test_s0_03_omniroute.py` (sandbox, PIN copy) | `95 passed in 9.97s` / `pytest-exit: 0` |
| pytest ×2 with explicit `--basetemp` (PIN copy) | `95 passed in 10.39s` then `95 passed in 10.69s` — identical counts |
| **PC gate** (carve-out, clean detached worktree of the PIN, patch 0B) | RUN_ID `20260908T040612Z-b5670c1` → `pytest-exit: 0` / `pytest-summary: 95 passed in 3.48s` |
| `bash -n` on both PC shell tools | clean |
| pyflakes over all five Python files | rc 0, clean |
| `skip`/`xfail` in the suite | none (the one grep hit is prose at `tests/test_s0_03_omniroute.py:539`) |
| `report_lint.py` over **this** report, at the PIN | `74 refs — OK 17, NEAR 1, MISS 0, UNCHECKABLE 9, UNRESOLVED 47 (at b5670c1)` |
| grading copy vs the PIN, after every mutant | `check_omniroute_roundtrip.py` / `probe_omniroute.py` / `test_s0_03_omniroute.py` / `spec.json` all sha256-IDENTICAL |

The 17 UNRESOLVED refs are all in the two pinned external checkouts (OmniRoute, hermes-agent) and
are outside report_lint's reach by design. I reproduced the four load-bearing ones by hand (§1).

**ap_screen classification — I agree with the lane on all 8 hits.** I re-ran each: the four AP-1
rows are one-shot reads threaded explicitly (`probe_omniroute.py:60`, `direct_responses_probe.py:135`
and `:164`, `hermes_env_names.py:33`), each overridable by an explicit argument; the four TEST_SCREEN
hits are the docstring of `test_pc_tools_never_name_match_processes` at `tests/test_s0_03_omniroute.py:726-727`,
which is the test that BANS those tokens — a screen false positive, correctly called.

---

## Findings

### F-1 — Conjunct (iii), the identity oracle, is bound to NOTHING. A forged or foreign `omniroute-requests.json` passes. **SOLID / BLOCKER**
`proofs/S0-03/check_omniroute_roundtrip.py:340-384`; producer `proofs/S0-03/tools/pc/collect_leg.sh:48-98`.

The council's "single most important assertion" reduces, in code, to four tests on a JSON file the
runner writes: `requested_model == route_id` (`:362`), provider not a stub (`:368`), model not a
stub (`:372`), both rows' model equal and equal to `direct.json`'s `model` (`:377-383`). There is
**no** request-identity binding, no timestamp check, no nonce, no status check.

**Failing input, reproduced:** the passing bundle with each row rewritten to
`{"provider":"openai-codex", "timestamp":"1999-01-01T00:00:00.000Z", "status":500,
"response_id":"resp_SOMETHING_ELSE"}`.
Expected: RED. Observed: `rc=0  PASS: S0-03 omniroute-roundtrip - model TBD-pc-capture via
openai-codex, tool-call round trip, env clean`. A row from 1999 that FAILED, for a different
request, satisfies the identity claim.

This is not only a forgery question. On the owner's PC the route the proof uses,
`agentfactory-build`, is *the route the owner's own Hermes build lanes use* (CLAUDE.md, routing
table). `collect_leg.sh:52` selects `WHERE requested_model = '<route>'` and `:83-88` picks the
**earliest row at/after each leg's wall-clock window**, so any concurrent lane request lands in the
window and is attributed to our leg. The instrument is time-attributed, not request-identified.

**The binding exists and is unused.** `call_logs` carries `response_id`
(`/home/user/nerdherderdani/OmniRoute` `src/lib/usage/callLogs.ts:521-524`, written from
`extractResponsesId(sourceFormat, clientResponse)` at
`open-sse/handlers/chatCore/attemptLogging.ts:501`, which returns the client-visible `resp_…` id
for `sourceFormat === OPENAI_RESPONSES`), and `direct.json` already records that id as `"id"` — `proofs/S0-03/tools/pc/direct_responses_probe.py:233`.
The table also carries a correlation id and a session tag (`callLogs.ts:517-519`).

**Minimal fix:** (a) add `response_id` to the SELECT in `collect_leg.sh:49-50`; (b) in
`check_identity_route`, require `legs["direct"]["response_id"] == direct["id"]` (a Failure naming
the mismatch) and `row["status"] == 200` for both rows; (c) for leg B, bind by the leg's window as
a *closed interval the runner records at both ends* and assert the row's timestamp falls inside it,
or carry a `session_tag`. Until (b) lands, the PASS line's `via <provider>` is decoration.

**Exact red test:**
```python
def test_conjunct_iii_binds_the_row_to_the_response_the_client_saw(passing):
    _edit(passing, "direct/direct.json", lambda d: d.__setitem__("id", "resp_A"))
    _edit(passing, "omniroute-requests.json",
          lambda r: [row.__setitem__("response_id", "resp_B") for row in r["requests"]])
    result = run_checker(passing)
    assert result.returncode == 1
    assert "response_id" in result.stdout
```

### F-2 — Duplicate leg labels silently shadow a stub row. **SOLID**
`check_omniroute_roundtrip.py:346-349` — `legs[leg] = row` in a loop; the LAST row with a given
label wins and every earlier one is discarded ungraded.

**Failing input, reproduced:** the passing bundle with a `{"leg":"direct","provider":"s0-01-scripted"}`
row *prepended* to the list. Expected: the stub reason. Observed: `rc=0  PASS: … via openai-codex …`.
`collect_leg.sh` cannot emit duplicates today, but the checker is the gate, and the file is an
input it does not control.

**Minimal fix:** reject a repeated leg label —
```python
if leg in legs: raise Failure(f"bundle: omniroute-requests.json has two rows for the {leg} leg")
```
**Exact red test:** as above, asserting rc 1 and `"two rows for the direct leg"` in stdout.

### F-3 — Conjunct (v) (ADR-0002 transport) is a MIRROR of the repo's own template. **SOLID / BLOCKER for the claim it makes**
`proofs/S0-03/tools/pc/run_s0_03_legs.sh:186` — `cp "$CONFIG" "$framedir/profile.yaml"`.

The `profile.yaml` the checker grades is a byte copy of the committed
`proofs/S0-03/hermes/config.yaml`, made by the runner *after* the leg, from the runner's own input.
`check_transport` (`:475-491`) therefore asserts that a committed repo file says
`api_mode: codex_responses` — which `test_proof_owned_profile_pins_the_adr_transport` already
asserts. It can never observe what transport Hermes actually used. The report's claim that "this
proof PINS the ADR's transport; a failure here is a RED FINDING for the owner" is not delivered by
the code: conjunct (v) cannot go red on a real run.

**The real instrument is captured and thrown away.** `collect_leg.sh:49` already SELECTs `path`
and `method` from `call_logs`. I set the hermes row's `path` to `/v1/chat/completions` — the exact
ADR deviation the proof exists to catch — and the checker returned **`rc=0 PASS`**.

**Minimal fix:** in `check_identity_route`, assert `legs["hermes"]["path"]` ends in `/responses`
(and `legs["direct"]["path"]` likewise), with a `transport:` reason. `call_logs` also has
`source_format`/`target_format` (`callLogs.ts:573`) if a stronger form is wanted.
**Exact red test:** `test_conjunct_v_reads_the_wire_not_the_template` — mutate the hermes row's
`path` to `/v1/chat/completions`, assert rc 1 and the `transport:` reason.

### F-4 — The "no inline key" guard is one literal key name; a credential in `extra_headers` passes. **SOLID**
`check_omniroute_roundtrip.py:485` — `if "api_key" in block:`.

**Failing input, reproduced:** the passing bundle's `hermes/profile.yaml` with
`Authorization: "Bearer sk-live-REDACTEDVALUE"` added under `extra_headers`. Expected: RED (the
launched profile carries a key value). Observed: `rc=0 PASS`. Hermes' own config example documents
`extra_headers` as the place operators put custom auth
(`/home/user/nerdherderdani/hermes-agent/cli-config.yaml.example:141-154`, "Header values are
treated as secrets"), so this is the likely shape, not a contrived one.

**Minimal fix:** screen the whole provider block —
```python
for k, v in list(block.items()) + list(headers.items()):
    if is_credential_name(str(k)) or (isinstance(v, str) and v.lower().startswith("bearer ")):
        raise Failure(f"bundle: profile.yaml carries an inline credential under {k!r}")
```
**Exact red test:** `test_conjunct_v_rejects_a_credential_in_extra_headers`.

### F-5 — A credential that was REJECTED is graded `blocked: credential_absent`. **SOLID**
`check_omniroute_roundtrip.py:293` — `if direct is not None and direct.get("status") == 401: _fail("credential_absent")`.

The seed is explicit (`seeds/seed-stage0-v1.yaml:400-402`): `reason_enum: [credential_absent,
credential_rejected]` and "**credential_rejected maps to proof-RED, never to blocked**". The
checker has no `credential_rejected` reason at all, and its kill switch turns *any* 401 into the
blocked reason.

**Failing input, reproduced:** the passing bundle with `direct.json status = 401` while
`hermes-env-names.json` still lists `OMNIROUTE_API_KEY` (I verified the name is present).
Expected: a RED naming rejection. Observed: `rc=1  failure_reason: blocked: credential_absent`.
The probe gets this distinction right (10 vs 11); the checker inverts it.

**Minimal fix:** split the switch —
```python
if env is not None and "OMNIROUTE_API_KEY" not in env: _fail("credential_absent")
if direct is not None and direct.get("status") in (401, 403):
    _fail("credential_rejected")     # new REASONS row: "credential_rejected: OmniRoute refused the presented key (HTTP {})"
```
and add the row to `REASONS`. **Exact red test:** `test_a_present_but_refused_key_is_rejected_not_absent`.

### F-6 — Conjunct (iv) does not prove a tool-call round trip: an agent that quotes the prompt back passes. **SOLID**
`check_omniroute_roundtrip.py:415-452`. The conjunct needs (a) one prompt turn carrying nonce2,
(b) *some* `tool_call` reaching `completed`, (c) nonce2 anywhere in concatenated
`agent_message_chunk` text. Nothing joins (b) to (c) or either to the nonce.

**Failing inputs, both reproduced on the committed timeline shape:**
1. replace the answer chunk with `"I was asked to run the terminal command 'printf <nonce2>' but I
   will not run it."` — the agent refuses and merely quotes the question. Observed `rc=0 PASS`.
2. keep the answer, but rewrite the completed tool call to `read_file: /etc/hostname` with
   unrelated `rawInput` and `content`. Observed `rc=0 PASS`.

Seed assertion 1 says "completes a **real** Hermes tool-call round trip". As written the conjunct
proves "a tool call finished, and the nonce string appears in some agent text".

**Minimal fix — the evidence is already in the fixture:** the completed `tool_call_update` carries
`content: [{"content": {"text": "<nonce2>"}}]`. Require the nonce in the COMPLETED call's content:
```python
completed_rows = [u for u in _updates(entries) if u.get("status") == "completed"
                  and u.get("toolCallId") in started_ids]
if not any(nonce2 in json.dumps(u.get("content"), ensure_ascii=False) for u in completed_rows):
    _fail("roundtrip", f"nonce2 {nonce2!r} absent from the completed tool call's output")
```
**Exact red test:** `test_conjunct_iv_requires_the_tool_output_to_carry_the_nonce` — strip the
nonce from the tool_call_update content only, assert rc 1.

### F-7 — `hermes_env_names.py` cannot read a REAL `runtime-identity.json`. Leg B's env instrument is dead on arrival. **SOLID / BLOCKER**
`proofs/S0-03/tools/pc/hermes_env_names.py:66` — `for key in ("agent_pid", "child_pid", "hermes_pid", "pid"):`.
The producer, `proofs/S0-01/tools/frame_tee.py:249-260`, writes the pid under **`agent_child_pid`**.
None of the four names it looks for exists.

**Reproduced against a real corpus artefact** (`/root/s0-01-realleg/golden/run-1/runtime-identity.json`,
keys `['agent_argv','agent_child_pid','agent_entrypoint_sha256','agent_interpreter_realpath',
'agent_interpreter_sha256','agent_realpath','buzz_acp_exe_realpath','buzz_acp_exe_sha256',
'buzz_acp_pid','buzz_acp_version','launch_argv','python_dont_write_bytecode','spawned_at_utc',
'tee_path','tee_pid','tee_sha256']`):
```
hermes_env_names: …/runtime-identity.json carries no agent pid (keys: [...])   exit=1
```
The runner's only call site is the `--runtime-identity` path
(`run_s0_03_legs.sh:175-176`), so `capture_hermes_leg` would poll for 60 s, never capture, and
return 6. The suite never covers this: both env-tool tests drive `--pid` explicitly, so the
consumer contract was never checked against the producer (build-loop step 1).

**Minimal fix:** add `"agent_child_pid"` **first** in the key tuple, and add a test that reads a
real `runtime-identity.json` key set. **Exact red test:**
`test_env_names_resolves_the_pid_the_tee_actually_writes` — write
`{"agent_child_pid": os.getpid(), "tee_pid": 1}` and assert exit 0.

### F-8 — Leg B's invocation does not fit `pc_launch.py` in three further ways; the report's "one-line seam" is not sufficient. **SOLID / BLOCKER**
`run_s0_03_legs.sh:163-166`:
```
env … S0_01_FRAMEDIR="$framedir" S0_01_AGENT="…" python3 "$S0_03_HERMES_CONFIG" --config "$CONFIG" --prompt "$PROMPT" &
```
Against `proofs/S0-01/tools/pc/pc_launch.py` (graded at the PIN **and** at the shared tree's P5a bytes):
1. **No `--config` and no `--prompt` argument exists.** PIN args: `--leg --model --respond-to
   --allowlist --settle-seconds` (`pc_launch.py:82-86`); P5a adds `--profile` (`:265-271`). Neither
   version accepts `--config` or `--prompt` — `grep -ni prompt` over both files returns **nothing**.
2. **S0-01 prompts do not travel through the launcher at all.** The capture path is
   `pc_launch.py` (detached, `setsid`, `proofs/S0-01/tools/pc/run_leg.sh:36`) → poll `launch.ready` →
   `pc_mention.sh` sends the prompt as a Buzz relay mention (`run_leg.sh:48`). There is no prompt
   seam to open; a nonce-carrying prompt needs `pc_mention.sh` (`TEXT=…`).
3. **`S0_01_FRAMEDIR` is set BY the launcher, not read from its env** (`pc_launch.py:161-162` at the
   PIN, `:249-250` at P5a). The runner's `framedir` is ignored, so the polled
   `runtime-identity.json` never appears there.

Also: `pc_launch.py` is a **detached** launcher ("the caller returns immediately", `pc_launch.py:13`),
so `wait "$leg_pid"` returns while the agent keeps running, and `stop_all`'s `kill` would target a
finished launcher, not the agent — the tee and hermes-acp would be left running on the owner's PC.
(That last consequence is **UNSURE** — reviewed from the source, not run.)

**Good news the report missed:** the seam it asks for **already exists in the shared tree**, in
lane P5a's UNCOMMITTED bytes (these line numbers are the worktree's, not the PIN's — the PIN has
neither): `proofs/S0-01/pins.py` line 348 defines `hermes_home()`, reading an `S0_01_HERMES_HOME`
override at line 361; `proofs/S0-01/tools/pc/pc_launch.py` line 267 adds `--profile <config.yaml>`
and lines 265-266 open `--leg` / `--model`. So the blocker's *first* leg is already solved by
another lane; items 1-3 above are not.

**Minimal fix:** rewrite `capture_hermes_leg` against the real path once P5a lands —
`pc_launch.py --profile proofs/S0-03/hermes/config.yaml --leg s0-03 --model agentfactory-build`
(detached, poll `launch.ready`), then `pc_mention.sh` with `TEXT="Run the terminal command 'printf
<nonce2>' …"`, then read the framedir from `$L/current-framedir`. **Exact red test:**
`test_runner_leg_b_uses_only_flags_pc_launch_declares` — parse `pc_launch.py`'s `add_argument`
calls and assert every flag the runner passes is among them.

### F-9 — The negative leg's producer cannot make the committed `credential-absent` bundle. **SOLID / BLOCKER**
`run_s0_03_legs.sh:202-204` runs the direct probe with `S0_03_KEY_FILE=/dev/null`.
`direct_responses_probe.py:164` calls `read_key` **before** anything is written, and an empty file
raises `SystemExit("… carries no OMNIROUTE_API_KEY line")`.

**Reproduced:**
```
$ S0_03_KEY_FILE=/dev/null python direct_responses_probe.py --route-id agentfactory-build --out-dir negdir
direct_responses_probe: S0_03_KEY_FILE carries no OMNIROUTE_API_KEY line: /dev/null   exit=1
$ ls negdir → empty
```
So `evidence/credential-absent/direct/direct.json` is never written, and `load_bundle` reads
`direct/direct.json` first (`proofs/S0-03/check_omniroute_roundtrip.py:514`): the real negative leg
grades `failure_reason: bundle: direct/direct.json absent`, **not** the seed's pinned
`blocked: credential_absent`. The negative bundle also never gets an `omniroute-requests.json` —
`collect_leg.sh` is invoked once, on the positive root (`run_s0_03_legs.sh:215`) — which is the
next Failure it would hit.

The kill switch is therefore proven only against a hand-written bundle that the capture path cannot
produce (anti-hollow-green tactic 7).

**Minimal fix:** make the negative direct leg send a request with **no** Authorization header
(a `--no-credential` flag on the probe that skips `read_key` and omits the header — this is what
produces OmniRoute's real no-bearer 401, `src/server/authz/policies/clientApi.ts:77` →
`src/server/authz/pipeline.ts:79-95`), and run `collect_leg.sh` for the negative root too.
**Exact red test:** `test_negative_leg_produces_a_gradeable_bundle` — run the probe with
`--no-credential` against a local 401 server and assert `direct.json` exists with `status == 401`
and no `Authorization` in `request_headers_sent`.

### F-10 — The `credential-absent` fixture's `request_headers_sent` is not what the writer emits; its PROVENANCE row says it is. **SOLID**
`proofs/S0-03/fixtures/evidence-credential-absent/direct/direct.json` (`request_headers_sent`) vs
`proofs/S0-03/tools/pc/direct_responses_probe.py:188-189`, which maps **every** header including
`Authorization → "<redacted>"`.

**Reproduced** — I ran the real writer against a local 401 server with a scratch key file:
```
producer request_headers_sent keys: ['Accept', 'Authorization', 'Content-Type', 'User-Agent', 'x-omniroute-compression']
fixture  request_headers_sent keys: ['Accept',                  'Content-Type', 'User-Agent', 'x-omniroute-compression']
producer Authorization value: '<redacted>'
```
The bundle's `PROVENANCE.md` row says "the writer itself — `direct_responses_probe.py` builds
exactly these keys". It does not; and the shape it does depict (a request sent with no bearer) is
one the probe structurally cannot make. AF-AP-42 is the class this exact row was written to prevent.

**Minimal fix:** regenerate the fixture from the real writer once F-9's `--no-credential` path
exists, or correct the row to say the header set was hand-edited and why.
**Exact red test:** `test_credential_absent_fixture_matches_the_writers_key_set` — build the record
by calling the probe against a local 401 server and compare `sorted(request_headers_sent)`.

### F-11 — The env record's process identity (`exe`, `pid`) is captured and never asserted. **SOLID**
`hermes_env_names.py:100-110` writes `{"pid", "exe", "names"}`; `check_omniroute_roundtrip.py:512-518`
reads only `names`.

**Failing input, reproduced:** the passing bundle with `hermes-env-names.json` rewritten to
`{"pid": 1, "exe": "/usr/bin/sleep", "names": [...]}`. Expected: RED (the env belongs to another
process). Observed: `rc=0 PASS`. Assertion 3 is "**Hermes** holds no upstream provider key"; the
checker proves "some process holds none".

**Minimal fix:** assert `Path(record["exe"]).name == "hermes-acp"` (or `== pins.PINNED_AGENT_REALPATH`
via the same import used for the timeline reader), with a `bundle:` reason.
**Exact red test:** `test_env_record_must_come_from_the_hermes_agent`.

### F-12 — The env allow-list is a marker-shape screen, not deny-by-default over the name domain. **SOLID**
`check_omniroute_roundtrip.py:141-146` (`CREDENTIAL_SEGMENTS`, `is_credential_name`) + `:494-503`.

I ran the whole boundary the brief names, one name at a time, on the passing bundle:

| name | verdict | correct? |
|---|---|---|
| `OMNIROUTE_API_KEY` | accepted | yes (allow-list) |
| `OMNIROUTE_API_KEY_2`, `FOO_API_KEY`, `MY_TOKEN`, `PRIVATE_KEY`, `HERMES_API_KEY`, `AWS_SESSION_TOKEN`, `OPENAI_APIKEY`, `openai_api_key` | rejected | yes — the segment rule beats the brief's literal regex (M8 is a fair mutant) |
| `PATH`, `HOME`, `KEYBOARD_LAYOUT` | accepted | yes |
| **`GITHUB_PAT`, `ANTHROPIC_AUTH`, `DB_PW`** | **accepted** | **no — real credential-name shapes with no marker segment** |
| `OMNIROUTE_API_KEY_FILE` | rejected | over-broad: a *path* pointer would RED the proof |

The exact boundary: a name is screened iff at least one `_`-separated segment (upper-cased) is in
`{KEY, KEYS, TOKEN, TOKENS, SECRET, SECRETS, PASSWORD, PASSWD, CREDENTIAL, CREDENTIALS, APIKEY}`;
screened names must be exactly `OMNIROUTE_API_KEY`. **This is not AF-AP-23's deny-by-default** —
deny-by-default is an allow-list over the *whole* domain; this is a blacklist of name shapes with an
allow-list inside it. It is a defensible engineering choice (an environ has hundreds of benign
names), but the docstring at `:494-497` calls it "an allow-list over the WHOLE name domain", which
is not what the code does. Every *provider* key the plan names is caught; `PAT`/`AUTH`/`PW` are not.

**Minimal fix (smallest honest one):** add `PAT`, `AUTH`, `PW`, `BEARER`, `SESSION` to
`CREDENTIAL_SEGMENTS`, and correct the docstring to say "every name whose segments mark it a
credential", naming the residual class. **Exact red test:** extend
`test_env_allowlist_is_a_closed_exact_set` with `("GITHUB_PAT", True)`, `("ANTHROPIC_AUTH", True)`.

### F-13 — The proof-owned Hermes profile puts the model default where Hermes never reads it. **SOLID**
`proofs/S0-03/hermes/config.yaml:39` — top-level `default: agentfactory-build`.

At the pinned hermes-agent `527da608`, the default model is read from the **`model:`** section:
`cli.py:5359-5361` — `_model_config = CLI_CONFIG.get("model", {})`, then
`_model_config.get("default") or _model_config.get("model")`. A top-level `default:` is never read
by anything. (The `providers:` block at `:29-37` IS correct — `cli.py:5388` passes
`CLI_CONFIG.get("providers")` — and `api_mode` inside an entry IS honoured,
`hermes_cli/model_switch.py:202-204`. So **item 4's answer is: yes, the pinned Hermes supports
`codex_responses` against a custom `base_url`; the design does not produce a guaranteed RED on
transport grounds and owner task #35 need not be decided first.**)

The consequence is worse than a no-op: with no `model:` section Hermes resolves no model from the
profile and there is nothing binding the route `agentfactory-build` to the provider
`s0-03-omniroute` — the leg would fall through to whatever Hermes resolves by default, i.e. it could
silently NOT go through the declared provider. `run_s0_03_legs.sh:48` also reads the route id from
this top-level key, so the route id and the launched model come from a key Hermes ignores.

**Minimal fix:**
```yaml
model:
  default: "s0-03-omniroute/agentfactory-build"
  provider: s0-03-omniroute
```
and read the route in `run_s0_03_legs.sh:48` from `model.default` (splitting the provider prefix).
**Exact red test:** `test_proof_owned_profile_declares_the_model_where_hermes_reads_it` — assert
`yaml["model"]["default"]` names the route and that no top-level `default` key exists.

### F-14 — `collect_leg.sh` compares RFC3339 stamps of different precision, lexicographically. **UNSURE (reviewed, not run — no OmniRoute here)**
`run_s0_03_legs.sh:66` emits `%Y-%m-%dT%H:%M:%S.%6NZ` (6 fractional digits); OmniRoute writes
`new Date().toISOString()` — 3 digits (`src/lib/usage/callLogs.ts:487`). `collect_leg.sh:85-88`
compares them with `>=` on strings. Within the same millisecond `'Z' (0x5A) > '4'`, so a row up to
~1 ms *before* a window start reads as inside it. Sub-millisecond in practice; it matters only
because F-1 already leaves the window as the sole attribution mechanism.
**Minimal fix:** parse both with `datetime.fromisoformat` before comparing.

### F-15 — `WHERE requested_model = '$ROUTE'` interpolates an argv value into SQL. **UNSURE (reviewed; input is proof-owned)**
`collect_leg.sh:52`. `$ROUTE` comes from `--route-id` or from a YAML file (`run_s0_03_legs.sh:48`).
A value containing `'` breaks or extends the query. Low reachability, one-line fix: bind the value
(`sqlite3 … "SELECT … WHERE requested_model = ?" ` is not available in the CLI, so pass it through
the python heredoc instead of the shell query).

### F-16 — Five recorded evidence fields are decision-irrelevant; the checker asserts none of them. **SOLID (reproduced where marked)**
`omniroute-requests.json`: `status`, `path`, `method`, `connection_id`, `combo_name` — none read.
`direct.json`: `compression_response_header`, `transport_error` — none read. `hermes-env-names.json`:
`pid`, `exe` — none read (F-11). Reproduced survivors: a row with `status: 500` (inside F-1), a
hermes row with `path: /v1/chat/completions` (F-3), `transport_error: "URLError: connection
refused"` alongside `status: 200` (rc 0 PASS), `compression_response_header: "on; source=policy"`
(rc 0 PASS — this one is legitimately S0-04's domain and the checker says so).
**Minimal fix:** fold `status` and `path` into conjunct (iii) (F-1/F-3); assert `transport_error is
None` in conjunct (i).

### F-17 — `json.loads` accepts `NaN`/`Infinity` in the evidence files. **SOLID, low**
`proofs/S0-03/check_omniroute_roundtrip.py:187` — `json.loads(path.read_text(encoding="utf-8"))`. Reproduced: `"status": NaN` in
`omniroute-requests.json` → `rc=0 PASS`. Harmless today only because `status` is unread (F-16);
it is the same fail-open wormhole class the incident log records twice. S0-01's timeline reader
already rejects NaN — the same discipline is missing here.
**Minimal fix:** `json.loads(text, parse_constant=_reject_nan)`.
**Exact red test:** `test_nan_in_any_evidence_file_is_a_named_failure`.

### F-18 — The report's own gate ran at a rev that is NOT an ancestor of the landed commit. **SOLID**
The report header says **PIN `773091c1a196…`** and §4 pastes
`RESULT: rev=773091c1a196 files=30 runs=2 identical=yes rc=0`. `git merge-base --is-ancestor
773091c b5670c1` → **NO**; their merge base is `8a978fe`, and `773091c..b5670c1` contains 10
commits including `75998e7` (S0-01 checkpoint 8y), which touches the very module this checker
imports (`proofs/S0-01/check_acp_conformance.py`). The lane's green therefore did not, at the time
it was pasted, cover the tree the coordinator is grading.
**I re-ran it at the PIN and it holds** (95 passed, twice in the sandbox, once on the PC) — so this
is a discipline finding, not a live defect. **Minimal fix:** the checkpoint commit's RESULT line
must carry the rev that is actually being landed.

### F-19 — `report_lint` MISS at the PIN and 3 MISSes on today's worktree. **SOLID**
`tasks/briefs/s0-03-support/O1-report.md:228` cites `proofs/S0-01/tools/pc/pc_launch.py:216` for
"reads config.yaml from `pins.PINNED_HERMES_HOME`". At `b5670c1` line 216 reads
`for _ in range(60):`; on today's worktree it reads `capture can never silently be taken against a
foreign config.` Its lines 229 and 240 both cite
`PINNED_HERMES_HOME = "/home/rocco/s0-01-pinned/.hermes-home"` at `proofs/S0-01/pins.py:18` —
correct at the PIN; on today's worktree that constant has moved to line 21. The lane's pasted `report_lint: 16 refs — OK 16 … MISS 0` is
no longer reproducible on any tree I can reach. The *substance* of the citations is correct at the
PIN (`pins.py:18` at `b5670c1` IS `PINNED_HERMES_HOME = "/home/rocco/s0-01-pinned/.hermes-home"`),
so this is drift against a live lane's file, not a false claim — but it must be re-linted against
the landed bytes before the checkpoint stands.

### F-20 — `blocked.json`'s recorded probe run cannot have come from the venue that minted it. **SOLID (the lane surfaced it; I reproduced the mechanism)**
`proofs/S0-03/blocked.json` carries `probe_run.exit_code: 0` and `blocker_status: expired` with
`env_fingerprint: "pc-bridge:fedora"`. Exit 0 requires a 2xx from `http://127.0.0.1:20128/v1/models`.
The lane's discrepancy §7.1 says the sandbox cannot produce it; the fingerprint says pc-bridge, so
the marker is *probably* honest — but nothing in the artefact records the venue's hostname
(`platform.node()` produced the literal string `fedora`). Flagged for the coordinator to confirm the
marker was minted on the PC, not to re-mint blindly.

### F-21 — `mktemp` leak on the preflight's failure paths. **SOLID, cosmetic**
`run_s0_03_legs.sh:87` — `trap 'rm -f "$models_body"' RETURN` at top level is a no-op outside a
function (and does not disturb the EXIT trap). On the `exit 3` paths at `:91` and `:93` the temp
file survives. One-line fix: `trap 'rm -f "$models_body"' EXIT` merged into `stop_all`.

### F-22 — The leg-B escape hatch defeats the blocker it was written to enforce. **SOLID**
`run_s0_03_legs.sh:126-135` refuses unless `S0_03_HERMES_CONFIG` is set, and the refusal text says
"Set `S0_03_HERMES_CONFIG` to a launcher that accepts a profile path". The comment three lines above
says substituting a different launcher "is not acceptable". So the guard is bypassed by an env var
whose whole purpose is the substitution the comment forbids, and there is no check that the named
launcher is `pc_launch.py`. The variable is also misnamed — it holds a *launcher script path*
(`python3 "$S0_03_HERMES_CONFIG"` at `:166`), not a config.
**Minimal fix:** rename to `S0_03_LAUNCHER`, and assert its realpath is
`proofs/S0-01/tools/pc/pc_launch.py` unless `S0_03_ALLOW_FOREIGN_LAUNCHER=1` is set explicitly.

### F-23 — The negative bundle's `leg.json` is copied from the positive leg. **SOLID, low**
`run_s0_03_legs.sh:209` — `cp "$EVIDENCE/hermes/leg.json" "$EVIDENCE/credential-absent/hermes/leg.json"`.
The negative bundle then claims a nonce2 that belongs to a different prompt. Harmless while the kill
switch fires first (F-5 ordering), but it is falsified evidence inside an evidence bundle.
**Minimal fix:** write the negative leg's own `leg.json` from its own prompt/nonce.

---

## Item-by-item answers

**Item 1 — the identity assertion.** All four OmniRoute citations reproduce by `sed -n` at
`488f57e9`: `openai-responses.ts:198-200` (`state.model = chunk.model.trim()`), `:217` / `:229`
(stamped into `response.created` / `response.in_progress`), `:763-766` (terminal); `chatCore.ts:1013-1015`
(`isCodexResponsesEcho`) and `:1017-1026` (the `echoModel` rewrite, three conditions);
`codexIdentity.ts:536-537` (`originator`/`user-agent` startswith `"codex"`); `callLogs.ts:564-572`
(the INSERT naming `model, requested_model, provider` as separate columns). **The lane's analysis is
correct**: the response `model` is the upstream-resolved id by default and a mirror of the request
under the echo, so `call_logs` is the right *place* to look. But see **F-1**: nothing binds the
exported rows to the leg. The design question's answer is *nothing* — not timestamps (a window
open to the owner's own `agentfactory-build` traffic), not request ids (`response_id` exists and is
not selected), not the nonce. The forged-bundle mutant passes. That is the round's blocker.

**Item 2 — six conjuncts, one mutant each.** The lane's six mutants (M1-M7, M11) are fair and all
died in my re-run of the suite (95/95 green, twice). The first-failure order is pinned and I
confirmed the kill switch outranks conjunct (i). The stub list IS read from `spec.json` and covers
both stub ids plus the bare connection name plus the `stub + "/"` namespace (M9 is a real mutant).
The nonce-present-in-text rule **accepts an answer that quotes the prompt back** — it should not
(F-6). The S0-01 timeline reader IS imported: `test_timeline_reader_is_imported_from_the_s0_01_checker`
asserts module identity via `inspect.getmodule`, and `check_omniroute_roundtrip.py:96-116` loads it
by `importlib.util.spec_from_file_location` — a pasted copy would fail the identity assert.

**Item 3 — the env allowlist.** Boundary measured in full: see **F-12**.

**Item 4 — the transport pin.** The pinned Hermes **does** support `codex_responses` against a
custom `base_url`: `agent/agent_init.py:723-726` accepts it as an api_mode override,
`hermes_cli/model_switch.py:202-204` reads `api_mode` off a `providers:` entry, and
`cli-config.yaml.example:147-154` documents `base_url` / `key_env` / `extra_headers` as the entry's
keys. So the round does **not** produce a guaranteed RED and owner task #35 does not gate it. Two
real problems remain: the profile declares the model in the wrong place (**F-13**), and conjunct
(v) cannot observe the transport that was actually used (**F-3**).

**Item 5 — the probe.** All outcomes reproduced over real sockets (a local `http.server` on
127.0.0.1 and a real closed port — never an OmniRoute or model endpoint):

| input | exit |
|---|---|
| HTTP 200 | 0 |
| HTTP 401 | 11 |
| HTTP 403 | 11 |
| HTTP 500 | 12 |
| HTTP 404 | 12 |
| server sleeping 8 s vs the 5 s timeout | **13, after 5 s** |
| closed port | 13 |
| `OMNIROUTE_API_KEY` unset | 10 |
| no URL argument | 64 |

The LOUD outcome is real, not just an exit code — I ran the runner's probe path on a scratch copy
against a local server:
```
$ proof-runner probe --proof S0-03 --venue sandbox --root <scratch>
probe-invalid: S0-03 exit 12        (rc 1; proofs/S0-03/blocked.json REMOVED, not minted)
$ …same with a closed port
probe-invalid: S0-03 exit 13        (rc 1)
$ …against a 401 server
blocker_status= rejecting  reason= credential_rejected
$ validate-ledger integrity → S0-03 INVALID
  registry-schema: S0-03 credential rejection is not a valid blocked marker
```
The whole probe → marker → validator chain behaves exactly as the report claims. **The probe fix is
correct and is the strongest part of this lane.**

**Item 6 — the three negative bundles.** Each produces its exact reason (their suite + my re-run).
`PROVENANCE.md` exists in all three and is honest about the tool-call frames (I confirmed
independently: the five golden legs under `/root/s0-01-realleg/golden` carry no `tool_call` line).
The 401 body shape **matches OmniRoute's real one** — `src/server/authz/pipeline.ts:79-95`
renders `{error:{code,message,correlation_id}}`, `clientApi.ts:77` is `reject(401,"AUTH_002",
"Authentication required")` (the no-bearer path, which is the right message for *absent*), and the
two response headers are `x-request-id` / `x-omniroute-route-class` (`src/server/authz/headers.ts:15,17`).
Two defects: **F-9** (the producer cannot make this bundle) and **F-10** (the `Authorization` key is
missing from a header set the PROVENANCE says the writer builds).

**Item 7 — the PC runner and the direct probe, read never run.** The key is never in argv: the
runner uses `curl -H @<(printf …)` (`run_s0_03_legs.sh:88-89`) — a bash builtin inside a process
substitution, so no argv carries it — and the Python probe puts it straight into a header dict
(`direct_responses_probe.py:180`), redacting it at the point of the write (`:188-189`, verified by
my producer run: `'Authorization': '<redacted>'`). The 0600 check is `:78-79`; the preflight is
`omniroute_invariants.sh` + key-file mode + the route id in the authenticated `/v1/models` (`:73-93`).
The negative leg unsets the key in the launch env only (`:202`, `:208` `env -u`) and never touches
the owner's profile. Every process is killed by its own pid via `$WORK/pids/*.pid` (`:55-64`) — no
`pkill`/`pgrep -f` anywhere, and the suite asserts their absence over the whole file. **Blockers:
F-7, F-8, F-9, and F-22.** Between the two options the brief names, **the cheaper one is now the
S0-01 seam**, because P5a has already built it: `pins.hermes_home()` + `--profile`. What is left is
S0-03-side work (F-8 items 1-3 + F-7), not S0-01-side work. A proof-owned launcher would duplicate
the tee/relay spine and lose the "same capture path as S0-01" property the seed's assertion leans on
— higher risk, more code, and it would need the relay mention path anyway.

**Item 8 — the class flip.** Reproduced on a scratch copy of `proofs/` + `scripts/`:
- The registry diff the report proposes is schema-valid (`validate-ledger` accepted the edited row;
  the `blocked` block is optional).
- Flipping to `execution_proof` while `blocked.json` remains → `class-mismatch: S0-03
  registry=execution_proof artifact=blocked_credential` → **S0-03 INVALID**, integrity rc 1. Good.
- Both artefacts present is caught explicitly at `scripts/validate-ledger:224-227`
  (`"{proof_id} has both result and blocked artifacts"` → INVALID), so the brief's expectation holds.
- **The flip alone reds five other proofs** (AF-AP-56 attestation over `proofs/registry.yaml`):
  `attestation-mismatch: S0-07 / S0-09 / S0-10 / S0-11 / S0-12 proofs/registry.yaml`.

**Exact sequence for the coordinator's reviewed commit, in one increment:**
1. capture `proofs/S0-03/evidence/` on the PC and confirm the checker exits 0 there;
2. fill `expected_model_id` in `spec.json` and regenerate the two passing-shaped fixtures
   (`test_fixtures_track_the_spec_expected_model_id` enforces this);
3. edit `proofs/registry.yaml:14` to the report's line (class `execution_proof`, `blocked` block
   removed) and fix `unblock_condition`'s stale key name if the row is kept anywhere;
4. `git rm proofs/S0-03/blocked.json` **and** `proofs/S0-03/probe.json` stays (it is the probe
   declaration, not a marker) — the marker must be gone before the mint;
5. `python3 scripts/proof-runner run --proof <id> --venue sandbox --root .` for **S0-03, S0-07,
   S0-09, S0-10, S0-11, S0-12** (the five attested + the new one), from the repo tree, never a
   root-only scratch copy;
6. gate: `python3 scripts/validate-ledger integrity --root .` (every proof PRESENT, never INVALID)
   + `python3 scripts/ledger-gen --root .` + `git diff --exit-code proofs/ledger.json`.

**Item 9 — the 18-class preflight.** I re-scanned the 30 files. The lane's table is accurate as far
as it goes, and its class-13 self-catch (M14) is a genuine find. **Three classes it missed:**
- *mirrors of the code under test*, applied to **evidence** rather than code: `profile.yaml` is a
  copy of the checker's own repo-side input (**F-3**). The lane checked this class only for the
  timeline reader.
- *emitted-but-never-read fields*: nine recorded fields no conjunct consults (**F-16**, **F-11**),
  the inverse of the build-loop's "emit only shapes that can fire".
- *consumer contract never checked against the producer*: `hermes_env_names.py`'s pid key set
  (**F-7**) and the leg-B flag set (**F-8**) — build-loop step 1, the seam verified from the
  CONSUMER. The lane's own §8 row for `/proc` races is about the *timing* of the read, not about
  whether the record can be read at all.
Also worth a row: *numeric/domain fail-opens in JSON* (**F-17**).

**Item 10 — the PC gate.** Run, and I agree with the checkpoint. From a clean detached worktree of
`b5670c1` (`git status --porcelain` empty, patch **0B**):
`RUN_ID 20260908T040612Z-b5670c1` → `pytest-exit: 0`, `pytest-summary: 95 passed in 3.48s`.
Same 95 as the sandbox. Worktree removed; `git worktree list` shows only the main tree.

**Item 11 — mutants.** The lane's 14 all die (verified by re-running the suite at the PIN; M10's
killer is a `TimeoutExpired`, which is the guard's purpose). I added **23** of my own, of which
**12 survived**:

| # | mutant | verdict |
|---|---|---|
| V1 | requests row forged/unbound (1999 timestamp, status 500, foreign response_id) | **SURVIVES** (F-1) |
| V2 | duplicate `leg: direct` rows, stub shadowed by a later clean row | **SURVIVES** (F-2) |
| V3 | `Authorization: Bearer sk-…` in the profile's `extra_headers` | **SURVIVES** (F-4) |
| V4 | key present in environ + `direct.json status 401` | misgraded `blocked: credential_absent` (F-5) |
| V5 | agent quotes the prompt back instead of answering | **SURVIVES** (F-6) |
| V6 | the completed tool call is `read_file: /etc/hostname` | **SURVIVES** (F-6) |
| V7a-c | `GITHUB_PAT` / `ANTHROPIC_AUTH` / `DB_PW` in the environ | **SURVIVE** (F-12) |
| V7d | `OMNIROUTE_API_KEY_FILE` | killed (over-broad, F-12) |
| V7e-l | `HERMES_API_KEY`, `OMNIROUTE_API_KEY_2`, `FOO_API_KEY`, `MY_TOKEN`, `PRIVATE_KEY`, `AWS_SESSION_TOKEN`, `OPENAI_APIKEY`, `openai_api_key` | killed |
| V7m-o | `PATH`, `HOME`, `KEYBOARD_LAYOUT` | correctly accepted |
| V8 | `hermes_env_names.py` against a REAL `runtime-identity.json` | tool fails loud — **producer/consumer mismatch** (F-7) |
| V13 | negative direct leg with `S0_03_KEY_FILE=/dev/null` | writes nothing — **bundle unproducible** (F-9) |
| V14 | hermes row `path: /v1/chat/completions` | **SURVIVES** (F-3) |
| V15 | env record `exe: /usr/bin/sleep`, `pid: 1` | **SURVIVES** (F-11) |
| V16 | `direct.json status` as the string `"200"` | killed |
| V17 | `NaN` in `omniroute-requests.json` | **SURVIVES** (F-17) |
| V18 | `compression_response_header: "on; source=policy"` | survives — legitimately S0-04's domain |
| V19 | two rows both labelled `direct` | killed |
| V20 | `transport_error` set with `status 200` | **SURVIVES** (F-16) |

Total mutants exercised this round: **14 (lane) + 23 (mine) = 37**, well past the brief's 24.

**Item 12 — discipline.** Every `file:line` above was read by `sed -n`/`grep -n` on the PIN copy
(`git archive b5670c1`), or on the two pinned external checkouts at their stated commits (verified:
OmniRoute `488f57e9d`, hermes-agent `527da6084`), or — where explicitly labelled — on the shared
tree's uncommitted P5a bytes. `report_lint.py` over **this** report, at the PIN:
`74 refs — OK 17, NEAR 1, MISS 0, UNCHECKABLE 9, UNRESOLVED 47` (the 47 are the two external
checkouts, the 9 UNCHECKABLE are section headers that carry a path but no claim token, and the
1 NEAR is a two-line docstring range).

**Item 13 — the design.** `call_logs` is the right *place* — it is the only instrument that can name
the provider connection, and the response body structurally cannot (the lane's reasoning here is
sound and I reproduced its mechanism). But a DB row the runner exports is only an oracle if the
export is *identified*, and today it is *time-attributed* on a route the owner's own lanes share.
Two independent instruments (tactic 8) are only two instruments if the second one is about the same
event. The cheapest way to make it genuinely two-instrument is already in the schema:
`call_logs.response_id` equals the `resp_…` id the client streamed, so the two artefacts can be
joined on a value neither side can invent. A third instrument (the service journal line) is not
needed once that join exists. I would also fold `path`/`status` into the same conjunct — they are
already selected, already recorded, and they carry the transport claim conjunct (v) cannot make.

---

## Reproduced / reviewed / skipped

**Reproduced (I ran it):** both gate scripts and the whole 95-test suite at the PIN, twice, with
explicit `--basetemp`; the PC gate on the PIN's exact bytes; all four OmniRoute citations and the
two Hermes ones by `sed -n` on the pinned checkouts; the probe's nine outcomes over real sockets;
the runner's probe path (exits 12 and 13 → `probe-invalid`, marker removed) and the 401 →
`rejecting` → `validate-ledger` INVALID chain; the registry class flip and its five
attestation-mismatches; the fixture-vs-producer key-set diff by running the real writer against a
local 401 server; `hermes_env_names.py` against a real corpus `runtime-identity.json`; the negative
direct leg with `/dev/null`; 23 hostile bundle mutants.

**Reviewed statically (not run):** `run_s0_03_legs.sh` end to end and `collect_leg.sh`'s SQL (no
OmniRoute, no sqlite DB here — PC-only by design); `pc_launch.py` / `pc_mention.sh` / `run_leg.sh`
as the capture path; the Hermes config-resolution chain in `cli.py` / `model_switch.py`; the
detached-launcher consequence in F-8 (marked UNSURE); the timestamp-precision arithmetic in F-14
(marked UNSURE).

**Deliberately skipped:** any network call to `:20128` or to any model endpoint, from either venue
(brief prohibition, and it is the owner's service); running `run_s0_03_legs.sh`, the direct probe,
or `collect_leg.sh` on the PC; re-running the full `tests/ proofs/ spikes/` suite (out of this
lane's boundary — other lanes hold the tree; the S0-03 file set is what I was asked to grade, and I
ran it on both venues); mutating any file in the shared tree.

## Shared-tree hygiene and the process census

Read-only git on `/home/user/agent-factory` throughout: no `stash`/`checkout`/`restore`/`reset`/
`add`/`commit`/`push`. The one write was the brief-authorised `git worktree add -q --detach` of the
PIN, removed with `git worktree remove --force`; `git worktree list` now shows only the main tree.
The tree's HEAD moved from `7a848cd` to `e27eaaa` during my run and the dirty set changed — other
lanes, not me. Every mutant, every pytest run and every scratch server lived under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/`; every pytest run used
an explicit `--basetemp` under it.

**Process census:** I started 8 local `http.server` processes (127.0.0.1, ephemeral ports) and a
handful of short-lived python/pytest children. Every server was killed by its own recorded pid;
`ps -eo pid,ppid,etimes,args | grep -E "srv\.py|probe_omniroute"` returns **nothing**. No
`pkill`/`pgrep -f`, no process I did not start, nothing on the PC beyond the one authorised
pytest-only gate. No credential was read, printed, or written — the scratch key file contains the
literal string `fake-scratch-value-not-a-credential`.

---

## Verdict

**NOT-READY.**

**Blocking set (must land before the class flips and before the PC legs are attempted):**
1. **F-1** — bind conjunct (iii)'s rows to the leg (`response_id` join + `status == 200`). Until
   this lands, the proof's headline assertion is satisfied by a row from any request, including the
   owner's own concurrent `agentfactory-build` traffic.
2. **F-7** — `agent_child_pid`: leg B's env instrument cannot read a real `runtime-identity.json`.
3. **F-8** — the leg-B invocation must use `pc_launch.py`'s real flags and the relay prompt path.
4. **F-9** — the negative leg must produce a gradeable bundle (a `--no-credential` probe mode +
   `collect_leg.sh` on the negative root), otherwise the seed's kill switch is unproven by the
   producer.
5. **F-3 / F-4** — conjunct (v) must read the wire (`call_logs.path`) and must reject a credential
   anywhere in the provider block, not just under the literal key `api_key`.
6. **F-5** — a refused credential must not be graded `blocked:`.
7. **F-13** — the profile must declare the model where Hermes reads it, or leg B does not go through
   the declared provider.

**Non-blocking but fix in the same increment:** F-2, F-6, F-11, F-12, F-16, F-17, F-19 (re-lint at
the landed rev), F-21, F-22, F-23. F-10 rides on F-9. F-14/F-15 are cheap and can ride along.
F-18 and F-20 are for the coordinator's checkpoint discipline, not the code.

**Cheapest path.** One follow-up lane, sandbox-only, ~9 checker edits and ~4 runner edits, all
inside `proofs/S0-03/` and `tests/test_s0_03_omniroute.py`: (a) add `response_id`/`status`/`path` to
`collect_leg.sh`'s SELECT and to conjunct (iii); (b) `agent_child_pid` in the pid tuple; (c) rewrite
`capture_hermes_leg` against `pc_launch.py --profile` + `pc_mention.sh`; (d) `--no-credential` on
the direct probe and `collect_leg.sh` on the negative root; (e) the `credential_rejected` reason;
(f) the profile's `model:` section; (g) the `extra_headers` credential screen; (h) the tool-output
nonce assertion; (i) the `exe` assertion. Each of the nine has a red test named above. **Do not flip
the class yet** — the flip reds five minted proofs and gains nothing until `evidence/` exists.

**Exact PC steps for the coordinator's live legs, once the follow-up lands** (the whole leg
sequence is one bridge call per step; nothing here restarts the owner's services):
```
# 0. ff-sync the PC clone to the commit carrying the fix
scripts/pc.sh 'cd /home/rocco/agent-factory && git fetch -q origin && git merge --ff-only origin/claude/soundbox-kit-migration-iz1jwf && git rev-parse --short HEAD'
# 1. preflight only — read-only, proves the authoritative instance owns :20128 and the route exists
scripts/pc.sh 'cd /home/rocco/agent-factory && OMNIROUTE_API_KEY_FILE=$HOME/.hermes/profiles/agentfactory/.env bash scripts/omniroute_invariants.sh'
# 2. QUIET WINDOW — no other agentfactory-build traffic while the legs run (F-1's window is shared
#    with the owner's own Hermes lanes; pause them or accept the attribution risk)
# 3. the legs, detached, marker-polled (they exceed the bridge's ~120 s cap)
scripts/pc.sh 'cd /home/rocco/agent-factory && setsid bash proofs/S0-03/tools/pc/run_s0_03_legs.sh --evidence proofs/S0-03/evidence </dev/null > /tmp/s0-03-legs.log 2>&1 & sleep 1; echo launched'
scripts/pc.sh 'tail -40 /tmp/s0-03-legs.log'          # poll until "S0-03 bundle captured"
# 4. grade ON THE PC, then bring the bundle home
scripts/pc.sh 'cd /home/rocco/agent-factory && /home/rocco/venv-agent-factory/bin/python proofs/S0-03/check_omniroute_roundtrip.py --route-id agentfactory-build --expected-model-id <the id leg A reports> --stub-route s0-01-scripted --stub-route s0-01-scripted/s0-01-pong --stub-route s0-01-scripted/s0-01-slow proofs/S0-03/evidence; echo rc=$?'
# 5. only then: fill spec.json, regenerate the fixtures, flip the class, re-mint the six result.json,
#    and run the three attestation gates (Item 8 sequence above)
```
