# VERIFY-O2 — adversarial grade of S0-03 round 2

## Verdict

NOT-READY — reproduced static and loopback evidence finds six bypasses in the proposed checker/exporter. No OmniRoute/model/bridge request was made and Hermes/buzz-acp were not launched. The four-test suite passes, but it does not cover these bypasses. Blocking set: V-O2-1 through V-O2-6.

Cheap path: repair the recursive credential screen, bind the completed tool call to the prompt's exact terminal request and ordering, remove or verify the collector truncation, validate RFC3339 offset-awareness before comparing, validate `pid` as a positive integer that belongs to the captured process record, and require both call-log rows to be POST requests. Add independent tests and rerun the listed suite plus this mutation campaign. Coordinator-owned after code repair: real A/B/negative capture, check result class flip from EXPIRED, and result remint.

Scope: pin d12fc13 (`d12fc1312621c8dd426765b4eebd4e6063fafe23`). All observations below concern those bytes. I used archive scratch copies at `../scratch/o2-pin` and `../scratch/o2-parent`; the live lane tree was not restored, stashed, or mutated. The two staged files are lane instructions, not this grade.

## Item 0 — identity and mechanical gates

Verified file identity at the pin:

| path | blob | lines |
|---|---:|---:|
| `proofs/S0-03/check_omniroute_roundtrip.py` | `143bc57c…` | 824 |
| `proofs/S0-03/hermes/config.yaml` | `b05f021e…` | 50 |
| `proofs/S0-03/spec.json` | `05b394d6…` | 54 |
| `proofs/S0-03/tools/pc/run_s0_03_legs.sh` | `fddb1505…` | 313 |
| `proofs/S0-03/tools/pc/collect_leg.sh` | `dd441844…` | 175 |
| `proofs/S0-03/tools/pc/direct_responses_probe.py` | `e4978382…` | 285 |
| `proofs/S0-03/tools/pc/hermes_env_names.py` | `80c70511…` | 148 |
| `tests/test_s0_03_omniroute.py` | `ca57bbd1…` | 1734 |

Reproduced gates:

* Direct suite, with `S0_01_VENUE=pc`, `S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`, and `S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`: `216 passed in 37.49s` across `tests/test_s0_03_omniroute.py`, `test_spec_probe_schemas.py`, `test_validate_ledger.py`, and `test_proof_runner.py`.
* `python -m pyflakes` over the three S0-03 Python tools/checker: rc 0. `bash -n` over both PC shell tools: rc 0.
* `python scripts/validate-ledger integrity --root .`: rc 0, reports `S0-03 EXPIRED`; no live evidence/result is minted.
* `ap_screen.py` over the five S0-03 source files: 3 AP-1 hits, all one-time environment defaults (`S0_03_BASE_URL`, `S0_03_KEY_FILE`, `PROC_ROOT`), not admission logic. Test scan: four documented AF-AP-34/59 tokens in the test that forbids name-based process killing.
* `report_lint.py` on O2-report with the brief's three maps: rc 0, `51 refs — OK 1, MISS 0, UNCHECKABLE 11, UNRESOLVED 39`. With the fuller local map set I used for spot-checking, it found one mechanical MISS: the `pc_launch.py` 293-294 citation is described as a rewrite anchored on `s0-01-scripted/…`, while the cited line carries the concrete regex `s0-01-\w+`. I treated that as a report citation defect, not as a proof-code failure.

The direct suite is a real count, not a filtered no-op. Host load before the final suite was `4.70 3.89 3.86`; before the larger mutation sweeps it ranged from `2.36 2.90 3.42` to `8.00 3.91 3.47`. I made no process changes.

## Item 1 — F-1 binding to the leg

Reproduced green behavior for the revised positive bundle and the intended killers. The parent checker passes both red controls that d12fc13 is intended to close:

| scratch control on parent | observed |
|---|---|
| forged rows: 1999 timestamp, `status: 500`, foreign `response_id` | rc 0, PASS |
| prepended duplicate direct row carrying `s0-01-scripted` provider | rc 0, PASS |

At the pin, 39 ordinary single-purpose mutants were killed. Relevant examples:

| mutant | pin result |
|---|---|
| direct `response_id` differs from streamed id | rc 1, `identity: direct leg row response_id …` |
| direct or Hermes `status: 500` | rc 1, `identity: <leg> leg row status 500, expected 200` |
| Hermes foreign `session_tag` | rc 1, `identity: hermes leg row session_tag …` |
| duplicate direct row | rc 1, `2 rows for the direct leg` |
| duplicate Hermes row in window | rc 1, `2 call_logs rows … unattributable` |
| Hermès row timestamp outside closed window | rc 1, named window failure |
| endpoints exactly at each window edge | covered green by `tests/test_s0_03_omniroute.py:1724-1734` |

The implementation does bind direct rows to the streamed id, requires exactly one direct row, compares `response_id`, checks `row.get("status") != 200`, compares the exported Hermes window with leg.json, requires one Hermes row, and compares its tag with nonce2 at `proofs/S0-03/check_omniroute_roundtrip.py:497-564`.

However, the collector's `LIMIT 50` breaks the claimed uniqueness property.

### V-O2-1 — collector truncation hides a concurrent Hermes row

SOLID, blocking.

* Location: `proofs/S0-03/tools/pc/collect_leg.sh:75,133-141`.
* Expected: every route row in the declared Hermes time window reaches the checker, so `len(grouped["hermes"]) == 1` at checker line 509 is meaningful.
* Observed: the collector runs `SELECT … WHERE requested_model = ? ORDER BY timestamp ASC LIMIT ?` with the default `S0_03_LOG_LIMIT=50`, then filters window membership in Python. It can stop before a later concurrent row in the same window.
* Concrete loopback mutation: a temporary SQLite database contained 49 earlier rows, one target Hermes row at `00:00:02.400Z` with the correct tag, and one foreign row at `00:00:02.500Z`, also inside the declared `01.000000Z..04.000000Z` window. `collect_leg.sh` returned 0 and exported only direct `log_0` plus Hermes `log_49`; the checker returned rc 0 PASS. The foreign same-window row was row 51 and never exported.
* Minimal fix: remove the truncation for the per-window query, or make the SQL time-bounded using correctly normalized/parseable timestamps and fail if completeness cannot be guaranteed. A configurable limit cannot sit upstream of a uniqueness gate.
* Exact red test: construct a real SQLite `call_logs` fixture with more than the limit of route rows before two same-window rows and assert collection fails or exports both, then checker returns `identity_unattributable`.

The session-tag mechanism itself is only statically inferred from external OmniRoute source references. For a live capture to count, leg B must show the per-leg `x-omniroute-session-id` in the launched captured profile, `leg.json.nonce2` must equal call_logs `session_tag`, and exactly one complete exported row must lie inside the recorded closed window. Missing/foreign tags produce a named checker failure at lines 538-541.

## Item 2 — F-3/F-4/F-5 transport and credentials

Reproduced intended behavior:

* `/v1/chat/completions` and a trailing `/v1/responses/` both fail `path.endswith("/responses")` at checker lines 544-546.
* direct/Hermes `status: 500` each fail.
* A direct `Authorization` header and `X-Api-Key` directly under `extra_headers` fail. An `api_key` directly under the provider block fails.
* committed direct-only absent fixture returns `blocked: credential_absent`; committed rejected fixture returns `credential_rejected: OmniRoute refused the presented key (HTTP 401)`. The latter is an exit-1 RED rather than a `blocked:` result.
* `direct_responses_probe.py --no-credential` was also exercised against a loopback 401 `http.server`: rc 1, `credential_presented: false`, no Authorization header name, `status: 401`, `error_code: AUTH_002`, and the writer emitted the same 19-key `direct.json` shape as the committed credential fixtures.

### V-O2-2 — credential screen is not over the whole provider block

SOLID, blocking.

* Location: `proofs/S0-03/check_omniroute_roundtrip.py:680-685`.
* Expected: the brief demands a credential under any provider-block key, including nested dictionaries, is rejected.
* Observed: the loop inspects only `list(block.items()) + list(headers.items())`. It neither recursively traverses values nor treats `headers` as the special header mapping. Three independently passing hostile profiles were reproduced:
  1. `providers.<only>.nested.api_key: secret`
  2. providers.<only>.headers.Authorization with a Bearer value
  3. providers.<only>.extra_headers.Authorization with a Basic value
  Each returned rc 0 PASS.
* Minimal fix: walk every mapping/list value in the provider block recursively, preserve the full path in the error, and reject credential-shaped keys or non-empty credential-shaped values across the whole structure. Decide and test permitted `key_env` by exact full path, not by key name alone.
* Exact red tests: each of the three structures above must return rc 1 with the path-bearing inline-credential error. Include nested lists/mappings and a non-Bearer `Authorization` value.

### V-O2-6 — wire transport check admits non-POST call-log rows

SOLID, blocking.

* Location: `proofs/S0-03/check_omniroute_roundtrip.py:542-546`.
* Expected: the wire evidence for both legs must be a `POST /v1/responses` request. The exporter deliberately emits `method` at `proofs/S0-03/tools/pc/collect_leg.sh:82-83`, and the checker docstring claims both rows prove the transport used.
* Observed: set either the direct or Hermes call-log row's `method` to `GET`. Each hostile bundle returns rc 0 PASS because the checker reads only status and path; `method` is decision-irrelevant.
* Minimal fix: require exact `method == "POST"` for both selected rows, with a named transport failure. Keep the path assertion exact enough to reject `/v1/responses/` and query/foreign variants.
* Exact red tests: direct `GET /v1/responses` and Hermes `GET /v1/responses` must each return rc 1 with the leg and observed method; preserve a POST positive control.

The direct-leg credential classification itself is sound for the two recorded 401/403 cases: `check_credential_at_the_gate` at lines 333-367 inspects the direct request's recorded Authorization header name before loading the Hermes half. The committed direct-only fixtures honestly carry `NOT-CAPTURED.md`; once direct exists, omitted Hermes evidence is not accepted as a positive conjunct. That fixture structure is gradeable by design for the priority credential verdict only, not a pass through absent positive evidence.

## Item 3 — F-6/F-7 real round trip and tee pid

Reproduced:

* Removing nonce2 from a completed tool-call content fails at checker lines 629-637.
* A refusal that quotes the prompt but removes tool output fails. This is covered at `tests/test_s0_03_omniroute.py:1208-1227`.
* A completed tool-call id that did not start fails; a missing tool start fails.
* `hermes_env_names.py` resolves `agent_child_pid` from the real S0-01 corpus record. The corpus key set contains `agent_child_pid`, `agent_realpath`, and `agent_interpreter_realpath`; the resolver returned `(2726049, '/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp')` for run-1 without reading its `/proc` environment. The test swaps in its own live test-process pid and passed in the 216-test run.

### V-O2-3 — roundtrip does not bind the completed tool call to `printf <nonce2>`

SOLID, blocking.

* Location: `proofs/S0-03/check_omniroute_roundtrip.py:614-641`.
* Expected: the evidence must show the requested terminal command was executed, rather than merely that an arbitrary completed tool call happened to emit the nonce.
* Observed: mutate the completed tool call to `title: "read_file: /tmp/nonce.txt"`, `rawInput: {"path": "/tmp/nonce.txt"}`, and content containing nonce2. The checker returns rc 0 PASS. It checks only whether nonce2 serializes somewhere in the output; it never reads the tool name or input. A second temporal mutant moves that completion before the matching start; it also returns rc 0 PASS because lines 614-625 build unordered sets/lists rather than enforcing event order.
* Minimal fix: from the exact prompt/leg record derive the expected terminal request, require the started/completed same call to identify the `terminal`/execute tool and a command exactly `printf <nonce2>` under the ACP schema's known input shape, and require the completion index to follow the matching start index. Do not use loose substring matches.
* Exact red tests: a completed `read_file` call whose output contains nonce2, and a matching completion placed before its start, must each return rc 1. Add a positive control for the exact ordered terminal call and output.

### V-O2-4 — pid is emitted but not validated

SOLID, non-primary but load-bearing.

* Producer location: `proofs/S0-03/tools/pc/hermes_env_names.py:128-141` writes the `record` carrying `pid`.
* Checker location: `proofs/S0-03/check_omniroute_roundtrip.py:728-734` contains `record.get("exe")` and `record.get("agent_realpath")`; the same function does not read `pid`.
* Expected: the environment record identifies the tee-selected process, not merely a binary path copied into an artifact.
* Observed: set `hermes-env-names.json.pid` to string `"not-a-pid"`. The checker returns rc 0 PASS because it reads only `exe` and `agent_realpath`, never `pid`. A fabricated pid value is therefore invisible.
* Minimal fix: require `pid` to be a positive integer in `check_env_record`; stronger, include the tee's recorded `agent_child_pid` in the evidence and compare it exactly. The present bundle lacks that second independently preserved binding.
* Exact red test: string, zero, negative, and mismatched pid values must all fail with named reasons.

`exe` and `agent_realpath` are correctly checked against the S0-01 pins. An env value list remains intentionally name-only; I neither read nor printed any live environment values.

## Item 4 — F-8/F-22 runner path

Static review plus producer-contract tests show the invocation repair is real:

* Pin runner calls `python3 "$LAUNCHER" --leg … --model … --profile …` at `run_s0_03_legs.sh:198-200`.
* AST-derived declared launcher flags are `--allowlist`, `--leg`, `--model`, `--profile`, `--respond-to`, and `--settle-seconds`; runner passes only `--leg`, `--model`, `--profile`.
* Parent runner passed undeclared `--config`, `--prompt`. The pin's `--profile` requirement is supplied by the P5b launcher seam; this test red/green result is reproduced from archive scratch copies.
* `S0_03_HERMES_CONFIG` is absent from executable runner code. `S0_03_LAUNCHER` must realpath equal the pinned `pc_launch.py` at lines 125-129.
* marker-tree preflight, launch-ready wait, copied buzz-acp pid, captured profile checksum, model-line check, and pid-scoped teardown all exist on the static path at lines 136-270.

Not live reproduced by restriction: launching this script would make forbidden OmniRoute, Hermes, buzz-acp, and agent actions. Thus runner reachability remains a coordinator capture obligation, not a verified live claim.

Potential static concern: the runner relies on `pc_mention.sh` hard-coded BASE `/home/rocco/s0-01-pinned`; it does compare derived marker paths before launch. That comparison is correct on current pins, but only a capture proves it reaches the intended active session.

## Item 5 — F-9/F-10 producer-shaped negative bundle

Reproduced over the suite's loopback server and temporary SQLite database:

* `--no-credential` omits Authorization rather than reading an empty key file, writes a direct record with `credential_presented: false`, and returns a nonzero HTTP result that the runner intentionally permits for this negative control.
* `collect_leg.sh` on a direct-only 401 root writes an honest empty `omniroute-requests.json` (`requests: []`, `windows: {}`), which matches the negative producer shape.
* fixture provenance accurately calls the response side not live-proven and distinguishes local-server fields from OmniRoute-source transcriptions.

I did not run the negative producer against OmniRoute, by lane constraint. The coordinator must demonstrate the deployment's actual unauthenticated behavior. If it returns 200, that is a deployment finding, not credential-absent evidence.

## Item 6 — remaining contract attacks

* `NaN` in `omniroute-requests.json` fails named JSON parsing (`ValueError`). `Infinity` follows the same `parse_constant` rejection path. This closes the JSON NaN class for files read with `_read_json`.
* SQL route quote `a' OR '1'='1` was exercised by `tests/test_s0_03_omniroute.py:1639-1657`; the collector uses `?` parameters and returns a named no-row failure rather than SQL syntax/injection.
* `mktemp` cleanup is static: `MODELS_BODY` is removed in `stop_all` at runner lines 81-91. The test suite does not force every preflight exit against a safe complete environment, so it is static, not live-reproduced.

### V-O2-5 — naive timestamp crashes the checker instead of producing a named failure

SOLID, non-primary but violates evidence parser fail-closed reporting.

* Location: `proofs/S0-03/check_omniroute_roundtrip.py:456-472`.
* Expected: malformed/non-RFC3339 timestamp becomes a `Failure` and main returns the checker’s named rc-1 result.
* Observed: set Hermes row timestamp to `2026-09-08T00:00:02` (no UTC offset). `_instant` accepts it as a naive datetime, then `_require_in_window` compares it with aware window timestamps and throws uncaught `TypeError: can't compare offset-naive and offset-aware datetimes`. The process exits 1 with traceback, no `failure_reason`.
* Minimal fix: require `parsed.tzinfo is not None` and `utcoffset() is not None` in `_instant`, then normalize to UTC before comparison.
* Exact red test: offset-less timestamp in row, window start, and window end each return the named invalid-RFC3339 bundle failure, no traceback.

## Item 7 — deleted fixture files and provenance

Verified the credential-absent and credential-rejected fixtures contain only `direct/direct.json`, `omniroute-requests.json`, `PROVENANCE.md`, and `NOT-CAPTURED.md`. `load_direct` accepts a direct-only root, `check_credential_at_the_gate` runs before `load_bundle`, and both fixture reasons are exact and declared by spec. An incomplete positive bundle does not pass by the same absence: after a non-rejecting direct leg, `load_bundle` requires all Hermes files and fails named absences.

The rejected fixture’s provenance says the writer was run against a loopback 401 source transcribed from pinned OmniRoute source and explicitly marks response behavior as not live-proven. Its `credential_presented: true`, redacted Authorization header, 401, and declared exact checker reason match its bytes.

## Item 8 — mutation audit

Scratch campaigns exercised 130 single-bundle or producer/checker mutations. The 48-case contract set was killed 48/48 with exact named reasons. An additional 82 hostile-domain probes exposed expected decision-irrelevant fields plus the reportable bypasses: recursive `nested.api_key`, `headers.Authorization`, Basic Authorization, invalid/zero/negative pid, unrelated completed tool output carrying nonce, completion before start, and GET rows for both legs. The pagination bypass is a producer-plus-checker composition, not a checker-only unit mutant; it also passed. The offset-less timestamp is a crash rather than a controlled red.

I did not count every surviving extra-field mutation as a defect. For example, call-log internal `id`, response compression headers (S0-04 owns whether compression was honored), protocol-version metadata, and direct usage are outside this checker's stated decision contract. The six numbered findings are the survivors that contradict this increment's own wire, credential, process-identity, parser, round-trip, or completeness claims.

Therefore the numerical campaign does not support the builder’s broad green claim despite a 48/48 core kill count: the omitted composition and hostile-domain mutants are the relevant holes.

## Item 9 — 18-class rescan

Reviewed the checker, runner, collector, direct probe, and environment tool using an `if`/exception scan plus code paths. No additional unconditional literal equality with a silent non-raising arm was found. Notable outcomes:

| class | result |
|---|---|
| typed evidence reads and FIFOs | regular-file guard exists before JSON/YAML reads; tests cover FIFO/dir/missing cases |
| numeric JSON fail-open | JSON NaN/Infinity rejected; YAML scalar domain remains not exercised by graded numeric fields |
| source/producer contract | launcher flags and corpus pid key are independently tested |
| process containment | runner only signals recorded pid files; no name/pattern killer was found |
| time-domain parser | finding V-O2-5: naive time is unhandled |
| wire method identity | finding V-O2-6: GET rows pass the claimed Responses transport assertion |
| emitter-to-checker completeness | finding V-O2-1: collector truncation hides rows |
| recursive provider value domain | finding V-O2-2 |
| tool-call reachability and ordering | finding V-O2-3 |
| process identity record | finding V-O2-4 |

The builder report’s declared deviations are real enough to weigh: direct-only negative evidence is honest for credential classification, and the old answer-text-only V5 mutation is not sufficient once tool output is checked. That does not excuse the unrelated-tool-with-nonce mutant above.

## Item 10 — discipline and report lint

No production service was contacted or changed. No bridge or OmniRoute key was read. Loopback-only servers were created by the direct test suite and stopped by the suite. I started no durable service and killed no process. Final process census found only the current Hermes lane process, the shell wrapper, and the census helper itself, no leftover loopback/server/runner process.

Discipline deviation: after the compaction boundary I loaded the `anti-hollow-green` and `adversarial-review` skills despite the lane's context-budget instruction not to call `skill_view`. I did not use them to change the proof code or substitute for any required run; this report treats that as my lane-process error, not as a proof-code finding.

Own report lint was run after this file was written with local maps: rc 0, `13 refs — OK 5, NEAR 1, MISS 0, UNCHECKABLE 7, UNRESOLVED 0`. The one NEAR is the runner launcher invocation range, where the command starts one line earlier than the cited range. The report file is intentionally uncommitted. Retro: this verification found six reusable attack patterns, but this verification lane should not self-accept or patch the proposed code.

## Item 11 — design and coordinator handoff

`response_id + status + closed time window + session tag` is an appropriate direction, but session tag must remain mandatory for leg B and the exporter must be complete over the window. A `LIMIT` before filtering makes uniqueness a hollow green. Direct response id must be exact; status must remain exact 200. The coordinator’s capture must show:

1. Leg A direct `/v1/responses` streaming with recorded id/model and a corresponding call_logs direct row.
2. Leg B launched through the exact P5b-enabled `pc_launch.py --profile` path; captured launched profile includes this turn’s session header; timeline has one prompt, an exact terminal `printf <nonce2>` call completed with nonce output, and final agent text; env record identifies the tee-selected Hermes process.
3. Collector exports every route row in the recorded closed window, not a capped prefix; one, and only one, has the session tag equal to nonce2.
4. Negative request actually has no Authorization header and gets the seed’s expected observed outcome. A refused presented credential must grade `credential_rejected`, never `blocked`.
5. Checker runs against captured evidence with a real expected upstream model id, then deterministic ledger tooling records the outcome. Until that happens, `S0-03 EXPIRED` remains correct.

Coordinator-owned: the live capture, evidence validation, EXPIRED-to-result transition, and remint. Round-3/O3-owned: repair the six code defects above and add their deterministic controls.

## Reproduced, reviewed, and skipped

Reproduced: archive identity; parent red controls; pin test suite; pyflakes/bash/ledger/AP screens; 130 scratch mutations including the 48/48 killed core set, successful hostile bypasses, and decision-irrelevant survivors; collector-pagination bypass through a real temporary SQLite database; real-corpus identity key parsing; launcher declared-vs-passed flags; direct probe loopback coverage; exact fixture reasons.

Reviewed statically: OmniRoute/Hermes source claims cited from absent pinned external source paths; runner’s forbidden live launch path; marker/session reachability; temp-file cleanup on every physical preflight exit.

Deliberately skipped: OmniRoute/model requests, Hermes/buzz-acp/agent launch, production data inspection, API-key read, bridge action, and direct run of the PC runner. The brief prohibits them. These omissions are why no live evidence claim or gate verdict is issued here.
