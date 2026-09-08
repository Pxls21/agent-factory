# Lane O2 — S0-03 round 2: the call_logs row BOUND to the leg, conjunct (v) read from the wire, a negative leg its producer can make, leg B on the real S0-01 capture path, the profile's model where Hermes reads it (build lane: PC Hermes `code-implementer` when the slot is free, else sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".) Lane O1's landing is `b5670c1`
(pushed); its 30 files are unchanged at HEAD. **Dispatch order:** this lane starts only after lane P5b's landing — leg B rides the
S0-01 launcher seam P5a/P5b built (`pins.hermes_home()` with the `S0_01_HERMES_HOME` override, `pc_launch.py --profile`); read the
LANDED `proofs/S0-01/tools/pc/pc_launch.py` and `proofs/S0-01/pins.py` — never the shared tree's uncommitted bytes.

**Why:** VERIFY-O1 (report `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/wf-results-r5/VERIFY-O1.md` —
READ IT WHOLE FIRST; it is the contract for this round) graded lane O1 NOT-READY: the sandbox artefacts are real, 95 green on both
venues, the probe → marker → validator chain correct end to end — but the proof's headline assertion rests on a file nothing binds
to the leg, and neither live leg can run. Blocking, every one reproduced on the PIN: **F-1** conjunct (iii) grades an
`omniroute-requests.json` row by `requested_model`/provider/model only — a row from 1999 with status 500 and a foreign `response_id`
PASSES; on the PC the route `agentfactory-build` is the owner's own build-lane route, and `collect_leg.sh` attributes the earliest
row after a wall-clock window to the leg, so a concurrent foreign request becomes "our" identity; the binding already exists
unused: `call_logs.response_id` (`callLogs.ts:521-524`, from `extractResponsesId`) equals the `resp_…` id `direct.json` records as
`id`; **F-7** `hermes_env_names.py:66` looks for `agent_pid/child_pid/hermes_pid/pid` — the tee writes `agent_child_pid`; leg B's env
instrument fails loud on a REAL `runtime-identity.json`; **F-8** leg B's invocation passes `--config`/`--prompt` flags `pc_launch.py`
does not have, S0-01 prompts travel through `pc_mention.sh` (a relay mention), `S0_01_FRAMEDIR` is SET by the launcher, and the
launcher is detached so `wait` returns immediately; **F-9** the negative leg runs the probe with `S0_03_KEY_FILE=/dev/null`, which
exits 1 before writing anything — the committed `credential-absent` bundle cannot be produced (tactic 7), and `collect_leg.sh` is
never run on the negative root; **F-3** conjunct (v) grades a `profile.yaml` the runner COPIES from the committed template after
the leg — a mirror; the wire's `path` (`/v1/chat/completions` vs `/v1/responses`) is SELECTed and thrown away; **F-4** the inline-key
guard is the literal `api_key` — a `Bearer …` under `extra_headers` (Hermes' documented custom-auth place) passes; **F-5** a REJECTED
credential (401 with the key present) is graded `blocked: credential_absent` — the seed says `credential_rejected` maps to RED,
never blocked; **F-13** the profile's top-level `default:` is a key Hermes never reads (`cli.py:5359-5361` reads `model.default`),
so leg B would not go through the declared provider. Non-blocking, same increment: F-2 duplicate leg rows shadow a stub, F-6 the
round trip accepts a quoted-back prompt, F-11 the env record's `exe`/`pid` never asserted, F-12 `GITHUB_PAT`/`ANTHROPIC_AUTH`/`DB_PW`
accepted, F-16 nine recorded fields never read, F-17 NaN accepted, F-14/F-15/F-21/F-22/F-23 small.

**Inputs (read in this order):** VERIFY-O1 whole · the lane brief `tasks/briefs/s0-03-o1-omniroute-roundtrip-identity-checker-pc-legs.md`
and `tasks/briefs/s0-03-support/O1-report.md` · the LANDED S0-01 launcher path: `proofs/S0-01/tools/pc/pc_launch.py` (its
`add_argument` set — the CONSUMER contract), `proofs/S0-01/tools/pc/run_leg.sh` (`setsid` + `launch.ready` + `pc_mention.sh`),
`proofs/S0-01/tools/pc/pc_mention.sh`, `proofs/S0-01/pins.py` (`hermes_home()`, `PINNED_AGENT_REALPATH`), `proofs/S0-01/tools/frame_tee.py:249-260`
(the runtime-identity keys) · the pinned OmniRoute source `/home/user/nerdherderdani/OmniRoute` (488f57e9, READ-ONLY):
`src/lib/usage/callLogs.ts:480-580` (every column: `response_id`, `status`, `path`, `method`, the correlation/session columns and
WHAT populates them — a client header? read `open-sse/handlers/chatCore/attemptLogging.ts` around :501), `src/server/authz/policies/clientApi.ts:77`
and `src/server/authz/pipeline.ts:79-95` (the real no-bearer 401) · the pinned Hermes source `/home/user/nerdherderdani/hermes-agent`
(527da608): `cli.py:5359-5361`, `hermes_cli/model_switch.py:202-204`, `cli-config.yaml.example:141-154` · `seeds/seed-stage0-v1.yaml:382-405`
(`reason_enum`, the rejected→RED mapping) · `docs/INCIDENT-LOG.md` (AF-AP-23, AF-AP-35, AF-AP-39, AF-AP-42, AF-AP-56) · the pack
`scripts/lane_context.sh -q 'what binds an omniroute-requests row to a leg' -s check_identity_route check_transport load_bundle
-o pack.md proofs/S0-03/check_omniroute_roundtrip.py` (run it first; attach it).
**Scope (under S0-03 + its test + your report):** `proofs/S0-03/check_omniroute_roundtrip.py` · `proofs/S0-03/probe_omniroute.py`
(only if an item needs it) · `proofs/S0-03/tools/pc/{run_s0_03_legs.sh, collect_leg.sh, direct_responses_probe.py, hermes_env_names.py}`
· `proofs/S0-03/hermes/config.yaml` · `proofs/S0-03/spec.json` (REASONS/negatives) · `proofs/S0-03/fixtures/**` (regenerated where
an item says) · `tests/test_s0_03_omniroute.py` · report `tasks/briefs/s0-03-support/O2-report.md`. NOT yours: anything under
`proofs/S0-01/` (read-only — the landed launcher IS the contract; if `--profile` is not there, STOP and report it as a blocker,
never substitute a launcher), `proofs/registry.yaml`, `proofs/S0-03/blocked.json`, the ledger. Shared-tree rules: never
`git stash/checkout/restore/reset/add/commit/push`; every gate from a `git archive <PIN> | tar -x` copy under
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/o2/ with your files copied in (`scripts/lane_gate.sh -r <PIN>
-f "<your files>" -t "tests/test_s0_03_omniroute.py tests/test_spec_probe_schemas.py tests/test_validate_ledger.py tests/test_proof_runner.py"
-n 2`, ONE foreground call, `LANE_GATE_DIR` under your scratch dir); explicit `--basetemp`; kill only your own processes by pid
(never pkill/pgrep -f); NEVER background a run and stop; no outward actions; NO PC bridge from a sandbox lane; NO network call to
any OmniRoute or model endpoint (loopback servers you start are the only sockets); never read, print or commit a credential
(scratch key files carry a literal non-secret). Authorization: the owner's own egress boundary under test; the forged/credential
fixtures are defensive. Interpreter `/root/venv-agent-factory/bin/python`.

## Design (pinned — build it, do not redesign it; line numbers are `b5670c1`'s)
1. **F-1 — the row is BOUND to the leg, or the leg is unattributable.** `collect_leg.sh:49-50` SELECTs `response_id`, `status`,
   `path`, `method`, `timestamp` and the correlation/session columns for EVERY row of the route inside a CLOSED window the runner
   records at both ends (`window_start`/`window_end` written to the leg's `leg.json` before and after the request — the runner
   already emits `%6NZ` stamps: parse both sides with `datetime.fromisoformat`, never compare strings — F-14). `check_identity_route`
   (`:340-384`): the direct leg's row must carry `response_id == direct["id"]` and `status == 200`; the hermes leg's row must be the
   ONLY route row inside its window (two or more → `identity: N call_logs rows in the hermes leg's window — unattributable`, never
   the earliest one) with `status == 200`; if `callLogs.ts` records a client-supplied correlation header (READ it — cite the line),
   the runner injects a per-leg tag through the profile's `extra_headers` (a runner-written copy of the profile, which F-3 makes
   honest) and the checker requires the row's tag == the leg's nonce2 — state in the report which of the two bindings leg B got and
   why. Red tests: the verifier's V1 (a 1999/500/foreign-id row) → RED; a second route row inside the hermes window → RED; V2 (a
   duplicate `direct` label) → `bundle: two rows for the direct leg` (F-2).
2. **F-3 — conjunct (v) reads the WIRE.** In `check_identity_route`, both rows' `path` must end in `/responses` (a `transport:`
   reason naming the path); keep the profile check as a secondary pin of the DECLARED transport, and the runner's `profile.yaml` in
   the bundle is the profile the launcher actually loaded (copied from the launched Hermes home AFTER the leg, never from the
   template). Red test: the verifier's V14 (`path: /v1/chat/completions`) → RED.
3. **F-4 — the credential screen over the whole provider block.** Every key of the provider block and of `extra_headers` through
   `is_credential_name`, every string value starting with `bearer ` (case-insensitive) → `bundle: profile.yaml carries an inline
   credential under <key>`. Red test: V3.
4. **F-5 — `credential_rejected` is RED.** `_fail("credential_absent")` only when `OMNIROUTE_API_KEY` is absent from the env record;
   a 401/403 with the key present → new REASONS row `credential_rejected: OmniRoute refused the presented key (HTTP <n>)`, exit 1,
   never `blocked:`; `spec.json` carries it. Red test: V4.
5. **F-6 — the round trip is real.** nonce2 must appear in the COMPLETED tool call's `content` (the fixture already carries it), not
   merely in agent text; the completed call's id must be one that started. Red tests: V5 (the quoted-back prompt) and V6 (an
   unrelated completed tool call) → RED.
6. **F-7 — the pid the tee writes.** `agent_child_pid` FIRST in the tuple; a test reads a `runtime-identity.json` with the corpus's
   real key set (copy the keys from `/root/s0-01-realleg/golden/run-1/runtime-identity.json`, values synthetic) and asserts exit 0.
7. **F-8 — leg B on the real capture path.** `capture_hermes_leg` = `pc_launch.py --profile proofs/S0-03/hermes/config.yaml --leg
   s0-03 --model agentfactory-build` (detached, then poll `launch.ready`), the prompt through `pc_mention.sh` (`TEXT=…` carrying
   nonce2), the framedir read from where the launcher publishes it (READ `pc_launch.py` for the exact file), the env record from
   `agent_child_pid`, teardown by the launcher's own pidfiles. A test parses `pc_launch.py`'s `add_argument` calls and asserts every
   flag the runner passes is declared (the runner-vs-launcher contract from the CONSUMER); `bash -n` clean. F-22: rename
   `S0_03_HERMES_CONFIG` → `S0_03_LAUNCHER`, realpath pinned to `proofs/S0-01/tools/pc/pc_launch.py` (no foreign launcher, no escape
   hatch). If the landed launcher lacks `--profile`: STOP, report the blocker, leave leg B refusing with exit 5 as today.
8. **F-9/F-10 — a negative leg the producer can make.** `direct_responses_probe.py --no-credential` skips `read_key` and sends NO
   `Authorization` header (OmniRoute's real no-bearer 401, `clientApi.ts:77` → `pipeline.ts:79-95`); the runner uses it for the
   negative leg and runs `collect_leg.sh` on the negative root too, with the negative leg's OWN `leg.json` (F-23). Regenerate
   `fixtures/evidence-credential-absent/direct/direct.json` by running the real writer against a local 401 server whose body and
   headers are transcribed from the OmniRoute source (cite the lines in `PROVENANCE.md`; say which parts are from the local server);
   a test builds the record the same way and asserts `sorted(request_headers_sent)` equals the fixture's (AF-AP-42).
9. **F-13 — the model where Hermes reads it.** `model: {default: "s0-03-omniroute/agentfactory-build", provider: s0-03-omniroute}`;
   no top-level `default`; `run_s0_03_legs.sh:48` reads the route from `model.default`; the test asserts the shape against
   `cli.py:5359-5361`'s reading.
10. **F-11/F-12/F-16/F-17/F-15/F-21:** the env record's `exe` must be the pinned agent (`pins.PINNED_AGENT_REALPATH` by the same
    import the timeline reader uses; V15 → RED); `CREDENTIAL_SEGMENTS` += `PAT`, `AUTH`, `PW`, `BEARER`, `SESSION` and the docstring
    says "every name whose segments mark it a credential" naming the residual class (V7a-c → RED); conjunct (i) asserts
    `transport_error is None` (V20 → RED); `json.loads(..., parse_constant=_reject)` in `load_bundle` (V17 → RED); the route bound
    into the SQL through the python heredoc, never interpolated; the preflight temp file removed on every exit path.
11. **Mutants:** the lane's 14 + the verifier's 23 re-run — every survivor (V1, V2, V3, V4, V5, V6, V7a-c, V14, V15, V17, V20) must
    DIE with a named killer; paste the killer line per mutant.
12. **18-class self-sweep** with counts and the method per class (the verifier regraded three classes the lane missed: evidence
    mirrors, emitted-never-read fields, consumer contracts never checked against the producer — your table shows each closed).
13. **Report discipline:** FILE IDENTITY of the FINAL bytes; every `file:line` from `grep -n` on the FINAL bytes and
    `python3 scripts/report_lint.py <report> --map C=proofs/S0-03/check_omniroute_roundtrip.py --map T=tests/test_s0_03_omniroute.py
    --map P=proofs/S0-03/probe_omniroute.py` pasted with MISS 0 at the rev you gate (F-19); the two `lane_gate.sh` RESULT lines
    pasted (the coordinator re-runs them at the landed rev — F-18); every red-before on `b5670c1` pasted beside its green-after;
    `ap_screen.py` on `proofs/S0-03 proofs/S0-03/tools proofs/S0-03/tools/pc` and `--tests`, classified by run; NOT-done first-class.
    NOT this lane's: the class flip and the six re-mints (the coordinator, VERIFY-O1 Item 8's sequence, AFTER the PC legs exist);
    the PC legs (VERIFY-O1's five steps, with the QUIET WINDOW on `agentfactory-build`).
