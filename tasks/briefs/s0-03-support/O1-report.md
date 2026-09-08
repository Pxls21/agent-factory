# O1 — S0-03 Hermes → OmniRoute round trip: spec, checker, PC legs, probe fix

**Lane:** O1 (sandbox, Opus 5). **PIN:** `773091c1a196ac538aab5002f32a43cfb407d9d4`.
**Status: BUILD COMPLETE, PROOF NOT MINTED.** Everything gradeable in the sandbox is built and
green; the two capture legs are PC-only and did not run here, and leg B is **BLOCKED** on a seam
in S0-01's launcher that this lane may not edit (§6). No stub was written to get past it.

---

## 1. The identity question, answered from the OmniRoute source

The brief asked which identity a `/v1/responses` response's `model` field actually carries.
Read at the pinned OmniRoute `488f57e9`, READ-ONLY at `/home/user/nerdherderdani/OmniRoute`.

**By default it carries the UPSTREAM-RESOLVED model id.** The Responses translator copies it off
the upstream chunk: `open-sse/translator/response/openai-responses.ts:199-200` sets
`state.model` from `chunk.model`, and `:217` / `:229` stamp it onto the `response.created` and
`response.in_progress` payloads (`:763-764` for the terminal one). For a **combo route** such as
`agentfactory-build` that is the id of whichever member served the call — **not** the combo name.

**But it is rewritten to the CLIENT-REQUESTED id under three conditions**, at
`open-sse/handlers/chatCore.ts:1022-1026`:

```
  let echoModel =
    (settings.echoRequestedModelName === true || isCodexResponsesEcho || isClaudeCodeClient) &&
```

`isCodexResponsesEcho` is built at `open-sse/handlers/chatCore.ts:1013-1015` and is **header-only**:
`open-sse/config/codexIdentity.ts:537-538` returns true when `originator` **or** `user-agent`
starts with `"codex"`. A fourth rewrite exists at `chatCore.ts:1030`
(`resolveNoAuthEchoModel`, defined `open-sse/handlers/chatCore/noAuthEchoModel.ts:15-25`).

### Why this decides the proof's shape

When the echo fires, `response.model` is a **mirror of the request**: asserting
`model == <the route we asked for>` becomes a tautology that a stub route satisfies just as well.
That is exactly the stub-drift hollow green the council named. So:

- **Conjunct (ii)** (response model id) is kept, but it is **not** the identity assertion.
- **Conjunct (iii)** is: OmniRoute's own `call_logs` row for each request, which records
  `provider` (the provider **connection** that served it), `model` (resolved) and
  `requested_model` (what the client asked) as **separate columns** —
  `src/lib/usage/callLogs.ts:564-566`. A stub connection is visible there and **nowhere in the
  response body**. The checker's PASS therefore rests on a conjunction of two independent
  instruments, and the committed `evidence-stub-route` bundle proves (iii) is load-bearing: it
  passes every other conjunct and is caught only by that row.

**Does Hermes trip the echo?** No, on the pinned `hermes-agent 527da608`. The Codex identity
headers are built by `agent/codex_headers.py:49-59`, and both call sites are **host-gated on
`chatgpt.com`** (`agent/agent_init.py:1349-1352`, `run_agent.py:6891-6895`); a custom base URL
like `http://127.0.0.1:20128/v1` never reaches them, so no `originator: codex_cli_rs` is sent.
This lane's own leg-A probe also deliberately sends a non-Codex `User-Agent` and no `originator`
(`USER_AGENT = "agent-factory-s0-03/1.0"`, `proofs/S0-03/tools/pc/direct_responses_probe.py:58`; test
`test_direct_probe_does_not_impersonate_the_codex_cli`). **The checker does not depend on any of
this holding** — that is the point of conjunct (iii).

**What this cannot see (stated, not hidden):** the value of OmniRoute's global
`echoRequestedModelName` setting. If it is ON, conjunct (ii) compares the requested id with
itself; (iii) still discriminates.

---

## 2. What was built

| file | lines | what |
|---|---|---|
| `proofs/S0-03/check_omniroute_roundtrip.py` | 581 | the checker: one kill switch + six conjuncts, one `REASONS` table, exit 0/1/2/64 |
| `proofs/S0-03/spec.json` | 44 | 1 positive + **3** negative legs (registry requires 1) |
| `proofs/S0-03/hermes/config.yaml` | 39 | the proof-owned provider profile (`api_mode: codex_responses`, `key_env`, compression-off) |
| `proofs/S0-03/tools/pc/direct_responses_probe.py` | 252 | leg A: one `/v1/responses` POST, events recorded verbatim |
| `proofs/S0-03/tools/pc/hermes_env_names.py` | 117 | assertion-3 instrument: env **NAMES** of the live hermes-acp process |
| `proofs/S0-03/tools/pc/collect_leg.sh` | 112 | the second identity instrument: `call_logs` rows, read-only |
| `proofs/S0-03/tools/pc/run_s0_03_legs.sh` | 217 | the PC runner: preflight → leg A → leg B → negative leg → collect |
| `proofs/S0-03/fixtures/evidence-*/` | 3 bundles | committed negative controls, each with `PROVENANCE.md` |
| `proofs/S0-03/probe_omniroute.py` | 88 | **the one existing file edited** — the exit-code fix (§3) |
| `tests/test_s0_03_omniroute.py` | 902 | 95 tests |

Evidence-bundle layout (documented in the checker's docstring): `direct/direct.json`,
`hermes/{timeline.jsonl,hermes-env-names.json,profile.yaml,leg.json}`, `omniroute-requests.json`.
The runner writes the positive bundle at `evidence/` and the negative bundle at
`evidence/credential-absent/`, which has the same internal shape.

### The checker's graded sequence (first failure wins)

| # | conjunct | `REASONS` row |
|---|---|---|
| 0 | credential-absent **kill switch** | `blocked: credential_absent` |
| i | a real streamed answer carrying a fresh 16-hex nonce, compression-off header sent | `direct: {}` |
| ii | response model id == declared upstream id | `identity: response model {!r} != declared upstream model {!r}` |
| iii | both `call_logs` rows: our route, non-stub connection, one agreed model id | `identity: request routed to the sanctioned stub route {!r}, not an upstream model` |
| iv | exactly one prompt turn, a `tool_call` reaching `completed`, nonce2 in the final text | `roundtrip: {}` |
| v | profile `api_mode: codex_responses` + compression-off + no inline key | `transport: profile api_mode {!r} != 'codex_responses' (ADR 0002)` |
| vi | deny-by-default env allow-list | `env: upstream provider key {} present in the Hermes environ` |

The kill switch runs **first by design**: a 401 also breaks conjunct (i), and grading it as "no
streamed answer" would lose the seed's pinned reason. Pinned by
`test_credential_absent_outranks_the_stream_conjunct`.

`spec.schema.json` sets `additionalProperties: false` over exactly `{proof_id, legs}`, so the
declarations (`--route-id`, `--expected-model-id`, `--stub-route` ×3) ride each leg's `cmd`. The
tests read them back out of `spec.json`, never from a literal.

---

## 3. The probe fix (`proofs/S0-03/probe_omniroute.py`)

**The defect:** every failure returned `11 credential_rejected`. The runner looks the exit code
up with `probe["reason_map"].get(str(run["exit_code"]))` (`scripts/proof-runner:245`), and
`if proof_id == "S0-03" and blocker_status == "rejecting":` (`scripts/validate-ledger:336`) turns
that marker into **proof-RED**. So a stopped OmniRoute, a DNS failure and a 500 all reported that
the owner's credential had been refused.

Root cause: `urllib.error.HTTPError` **is a subclass of** `URLError`, and the original code had a
single handler. The fix catches `HTTPError` first and separates four outcomes:

| exit | meaning | mapped in `probe.json`? |
|---|---|---|
| 0 | 2xx — credential accepted | n/a (`blocker_status: expired`) |
| 10 | key absent | yes → `credential_absent` |
| 11 | **401/403 only** — the gate refused the presented key | yes → `credential_rejected` |
| 12 | any other HTTP status | **NO — deliberately unmapped** |
| 13 | transport error / timeout / DNS | **NO — deliberately unmapped** |

12 and 13 are unmapped **on purpose**: `reason_map` has no entry, so the runner raises
`probe-invalid` and the run fails LOUD instead of minting a marker that misnames the blocker.
401/403 is the only refusal the gate can express — `src/server/authz/policies/clientApi.ts:77`
(no bearer) and `:96` (invalid bearer), both `AUTH_002`.

**Reproduced in this sandbox, both directions:**

```
$ python proofs/S0-03/probe_omniroute.py http://127.0.0.1:20128/v1/models        → exit 10
$ OMNIROUTE_API_KEY=x python proofs/S0-03/probe_omniroute.py http://…:20128/…   → exit 13
```

Before the fix the second case returned 11. Tested over **real sockets** (a bound
`http.server` for 200/401/403/500, a real closed port, a `.invalid` host) — no monkeypatching of
urllib, so the taxonomy under test is urllib's own.

---

## 4. Verification

**Static-copy gate at the PIN, twice** (`scripts/lane_gate.sh -r 773091c1a196…`), pasted verbatim:

```
RESULT: rev=773091c1a196 files=30 runs=2 identical=yes rc=0 summary="95 passed in 11.26s 95 passed in 10.65s"
```

`scripts/test_summary.sh` on the working tree, pasted verbatim: `95 passed in 11.37s`,
`pytest-exit: 0`. pyflakes over all five Python files: clean, rc 0.
`validate-ledger integrity --root .` → every proof `PRESENT`, rc 0; `ledger-gen` produces no
`proofs/ledger.json` diff (no S0-03 `result.json` is minted, so no attested artifact regenerates).

### Mutant table — 14 mutants, 0 survivors

Each mutant breaks ONE thing in a **scratchpad copy** of the tree (the shared tree was never
mutated; final sha256 of the checker re-verified identical). Killer lines pasted from the runs.

| mutant | row / guard | what it breaks | verdict | killer |
|---|---|---|---|---|
| M1 | `credential_absent` | kill switch never runs | **KILLED** | `test_committed_negative_bundle_exact_reason[evidence-credential-absent…]` — `assert 'failure_reas... expected 200' == 'failure_reas...ential_absent'` |
| M2 | `direct_stream` | streamed-answer conjunct never runs | **KILLED** | `test_conjunct_i_direct_stream` — `assert 0 == 1` |
| M3 | `identity_model` | response-model conjunct never runs | **KILLED** | `test_conjunct_ii_identity_model` — `assert 0 == 1` |
| M4 | `identity_route` | stub rejection always false | **KILLED** | `test_committed_negative_bundle_exact_reason[evidence-stub-route…]` — `PASS: … via s0-01-scripted, tool-call round trip, env clean` |
| M5 | `roundtrip` | tool-call round trip never checked | **KILLED** | `test_conjunct_iv_roundtrip_requires_a_completed_tool_call` — `assert 0 == 1` |
| M6 | `transport` | ADR transport never checked | **KILLED** | `test_conjunct_v_transport` — `assert 0 == 1` |
| M7 | `env_provider_key` | env allow-list never runs | **KILLED** | `test_committed_negative_bundle_exact_reason[evidence-provider-key-present…]` — `PASS: … via openai-codex, …, env clean` |
| M8 | `env_provider_key` | env screen reverted to the brief's literal anchored suffix regex | **KILLED** | `test_env_allowlist_is_a_closed_exact_set[OMNIROUTE_API_KEY_2-True]` — `Failed: DID NOT RAISE Failure` |
| M9 | `identity_route` | stub match exact-only (namespace rule dropped) | **KILLED** | `test_conjunct_iii_catches_every_declared_stub_id_and_its_namespace` — `AssertionError: s0-01-scripted/a-route-nobody-listed` |
| M10 | S_ISREG guard | non-regular-file guard removed | **KILLED** | `test_fifo_at_any_evidence_path_fails_in_bounded_time[direct/direct.json]` — `subprocess.TimeoutExpired` (the checker **hung on the FIFO**) |
| M11 | ordering | kill switch demoted below the stream conjunct | **KILLED** | `test_committed_negative_bundle_exact_reason[evidence-credential-absent…]` — same diff as M1 |
| M12 | `identity_route` | route correlation (`requested_model`) dropped | **KILLED** | `test_conjunct_iii_binds_the_row_to_our_route` — `assert 0 == 1` |
| M13 | `direct_stream` | nonce domain floor removed | **KILLED** | `test_conjunct_i_rejects_a_vacuous_nonce` — `AssertionError: x` |
| M14 | runner ordering | env record taken after the leg is reaped (**the original defect**, §5) | **KILLED** | `test_runner_captures_the_env_record_while_the_leg_is_alive` — `AssertionError: the env record is taken after the leg is reaped / assert 1039 < 979` |

M10's killer is a **timeout**, not an assertion: with the guard removed the checker blocks
forever on the FIFO. That is the guard's whole purpose demonstrated.

---

## 5. DEFECT found and fixed by the 18-class sweep

**Class 13 (`/proc/<pid>/exe` races, AF-AP-55 family) — DEFECT in my own runner, fixed this round.**

The first version of `run_s0_03_legs.sh` did:

```
wait "$(cat "$WORK/pids/hermes-leg.pid")"      # leg finishes, agent process exits
python3 …/hermes_env_names.py --runtime-identity …   # then reads /proc/<pid>/environ
```

The agent is **dead** by then, so `/proc/<pid>/environ` does not exist: leg B could never produce
`hermes-env-names.json` at all, and a **recycled pid** would have handed back a different
process's names — a silent wrong-identity read on the assertion-3 instrument. The negative leg
captured no env record either, though the checker requires one from every bundle and its
*absence* of `OMNIROUTE_API_KEY` is half the kill switch's evidence.

**Fix:** `capture_hermes_leg()` launches the leg in the background, then runs a **failure-aware**
poll — exits on (a) the record taken, (b) `kill -0` showing the leg gone, (c) a deadline — and
only then `wait`s. A leg that produced no record returns 6 and prints the captured stderr; it is
never a silently short bundle. Both hermes legs now go through it.
Pinned by three tests; proven red-then-green by mutant **M14**.

---

## 6. NOT run here — and one BLOCKER, surfaced not stubbed

Nothing in this section was faked. There is no OmniRoute in the sandbox and a sandbox model
server is forbidden (owner ruling 2026-09-03).

| item | why not here |
|---|---|
| leg A (`direct_responses_probe.py`) against real OmniRoute | PC-only; needs `:20128` + the owner's key file |
| leg B (the Hermes ACP capture) | PC-only **and BLOCKED** — see below |
| the negative (credential-absent) leg | PC-only |
| `collect_leg.sh` reading `call_logs` | PC-only; reads `/home/rocco/.omniroute-migrated/storage.sqlite` |
| `run_s0_03_legs.sh` end to end | PC-only; `bash -n` clean and its argument handling is tested |
| `spec.json`'s **positive** leg | fails until `evidence/` exists — by design, not a skip |
| the tool-call frame shapes in the fixtures | **no golden leg carries a tool-call turn** (§7) |

### BLOCKER — leg B cannot invoke S0-01's launcher

The brief pins leg B to the S0-01 capture path by invocation. **`pc_launch.py` cannot be pointed
at another proof's profile**, and S0-01's tools are out of this lane's scope to edit:

- `proofs/S0-01/tools/pc/pc_launch.py:216` reads `config.yaml` from `pins.PINNED_HERMES_HOME`,
  which `proofs/S0-01/pins.py:18` hard-codes to `/home/rocco/s0-01-pinned/.hermes-home` — there
  is **no environment override anywhere in `pins.py`** (checked: no `os.environ`/`getenv` in the
  file);
- `pc_launch.py:189-190` constrains `--leg` to `pins.LEGS` (`pins.py:76` — no S0-03 leg) and
  `--model` to `pins.EXPECTED_MODEL.values()` (`pins.py:78` — the S0-01 scripted models).

Writing an S0-03 config into that pinned tree would mutate S0-01's evidence base; forking the
launcher would duplicate the spine. **The runner therefore REFUSES** (exit 5) with a named,
actionable message rather than substituting a different launcher and calling the result the
S0-01 capture path. The seam it asks for, LAUNCH-env only and behaviour-neutral for S0-01:

The line to change is `PINNED_HERMES_HOME` at `proofs/S0-01/pins.py:18`:

```python
PINNED_HERMES_HOME = os.environ.get("S0_03_HERMES_CONFIG_HOME", "/home/rocco/s0-01-pinned/.hermes-home")
```

plus opening `--leg`/`--model` to a caller-supplied value. **Coordinator decision needed:** land
that seam in S0-01, or accept a proof-owned launcher for leg B. Pinned by
`test_runner_refuses_leg_b_without_the_declared_seam`.

---

## 7. DISCREPANCIES

1. **`blocked.json`'s recorded probe run cannot have come from this sandbox.**
   `proofs/S0-03/blocked.json` carries `probe_run.exit_code: 0` and `blocker_status: expired`
   (run stamped `2026-09-08T00:50:33Z`). Exit 0 requires a 2xx from `http://127.0.0.1:20128`;
   nothing listens on that port in the sandbox — the probe returns 10 or 13 here (§3, reproduced).
   Not my file to edit (the brief names `probe_omniroute.py` as the one existing file I touch).
   **Coordinator: re-mint the marker on the venue that actually ran it, or record the venue.**

2. **The credential has three names across the plan.** `probe.json`/the owner's Hermes env use
   `OMNIROUTE_API_KEY`; the seed (`seeds/seed-stage0-v1.yaml:404`) says `OMNIROUTE_UPSTREAM_KEY`;
   `key_env: OMNIROUTE_INTERNAL_API_KEY` at `docs/03_INTEGRATION_CONTRACTS.md:38`, matching
   `.env.example:24`. The registry's `unblock_condition` string still names the seed's.
   Recorded in the probe's docstring, **not resolved here** — it is a registry/seed edit.

3. **The brief's literal env regex admits a second credential.** The brief specified
   `(_API_KEY|_TOKEN|_SECRET|_KEY)$`, but also required `OMNIROUTE_API_KEY_2` to be rejected.
   `OMNIROUTE_API_KEY_2` does not end in any of those alternatives, so under the literal regex it
   is **never screened at all**. Implemented as a **segment** rule instead
   (`is_credential_name`, split on `_`), which satisfies every example the brief lists plus
   `OPENAI_KEY_OLD`, `ANTHROPIC_TOKEN_BACKUP` and the rest of the decoration family. Mutant **M8**
   is the brief's literal regex; it dies on `OMNIROUTE_API_KEY_2`.

4. **`spec.json`'s `expected_model_id` is the placeholder `TBD-pc-capture`.** Which id OmniRoute
   reports for a **combo** route is only knowable from the first PC capture (§1). The placeholder
   cannot pass silently — conjunct (ii) fails loudly against any real bundle. The two
   passing-shaped fixtures carry the same value so they still reach *their own* reasons, and
   `test_fixtures_track_the_spec_expected_model_id` goes **red** the moment the spec is filled in
   without regenerating the fixtures in the same edit.

5. **No golden leg carries a tool-call turn.** All five legs under `S0_01_REAL_LEG_DIR`
   (`/root/s0-01-realleg/golden`) contain only `agent_message_chunk`,
   `available_commands_update`, `session_info_update`, `usage_update` — zero `tool_call` lines.
   The `tool_call`/`tool_call_update` frames in the fixtures are therefore derived from the
   **committed protocol schema** (`proofs/S0-01/fixtures/acp-schema-v1.json` `$defs.ToolCall`,
   `.ToolCallUpdate`, `.ToolCallStatus`, `.ToolKind`, `.ToolCallContent`) plus hermes-agent
   `527da608` `acp_adapter/tools.py:90-92` (`tc-<12 hex>`) and `:96-101` (`terminal: <cmd>`), and
   every `PROVENANCE.md` marks them **`NOT proven against a live capture`**. The timeline
   *envelope* IS taken from the real corpus.

6. **`/api/usage/request-logs` is unusable for conjunct (iii).** It requires management auth
   (`src/app/api/usage/request-logs/route.ts:6-7`), which the owner ruled out. `collect_leg.sh`
   reads the same rows from the service's own SQLite in immutable mode
   (`src/lib/db/core.ts:104-106` gives `$DATA_DIR/storage.sqlite`). Consequence, stated: rows
   still only in the WAL are invisible, so the runner settles first.

---

## 8. `ap_screen` — every hit classified

**Production (`AP_SCREEN`), 4 hits over 4 files, all `AP-1` ("env read — config channel?"):**

| file:line | verdict |
|---|---|
| `proofs/S0-03/probe_omniroute.py:60` | **SAFE.** `key = os.environ.get("OMNIROUTE_API_KEY")` is not a config channel — this IS the credential, and `probe.json`'s `key_env` declares the env as its interface. Read once, threaded into a header dict. Guard: `test_probe_json_reason_map_covers_exactly_the_credential_verdicts`. |
| `proofs/S0-03/tools/pc/direct_responses_probe.py:135` | **SAFE.** `base_url = os.environ.get("S0_03_BASE_URL", DEFAULT_BASE_URL)` is read once inside `parse_args`, immediately overridable by `--base-url`, threaded through the returned dict. Never re-read. |
| `proofs/S0-03/tools/pc/direct_responses_probe.py:164` | **SAFE.** A file PATH, not a value; read once in `main`. The value is read from the file by `read_key`, tested by `test_direct_probe_key_reader_extracts_only_the_omniroute_line`. |
| `proofs/S0-03/tools/pc/hermes_env_names.py:33` | **SAFE.** `proc_root = os.environ.get("PROC_ROOT", "/proc")` is read once in `parse_args`, overridable by `--proc-root`, threaded; the tests drive it through the explicit argument. |

**Tests (`TEST_SCREEN`), 4 hits over 1 file, `AF-AP-34`(3) + `AF-AP-59`(1):** all four are the
**docstring of the test that enforces the rule** (`test_pc_tools_never_name_match_processes`,
which asserts those tokens are absent from the PC scripts). **SCREEN FALSE POSITIVE** — the screen
cannot distinguish "names the anti-pattern in prose while banning it" from "calls it". Note the
runner's own comment was reworded to drop the literals so the whole-file ban stays maximally
strict.

### 18-class sweep over my files — full table

| class | verdict |
|---|---|
| presence-gated checks | **EMPTY.** Every required file is unconditionally required; absence is a Failure naming the file. `test_absent_file_is_a_failure_not_a_deferral` covers all six paths. |
| reads outside the walk / no S_ISREG | **SAFE.** `_require_file` guards every read; mutant M10 proves it load-bearing (checker hangs without it). |
| stale `[-1]` over produced records | **SAFE** (3 hits, all `leg["cmd"][-1]`) — the evidence root is by construction the last argv element; `test_every_leg_declares_the_same_inputs` pins the shape. |
| negative acceptance assertions | **SAFE.** Every `assert not` is paired with a positive case in the same test or its parametrisation. |
| substring/tail anchors classifying outcomes | **SAFE.** `_is_stub`'s `startswith(stub + "/")` is a deliberate namespace rule (mutant M9 proves the exact-only version dies); `parse_sse`'s `startswith("data:")` is the SSE grammar; the `startswith("--")` is argv. |
| env-domain fail-opens | **SAFE** — the four AP-1 rows above. |
| lossy decodes on a decision path | **SAFE.** `errors="replace"` appears only on the recorded raw body / a `/proc` name split, never on a value a conjunct decides from. |
| broad catches | **SAFE** (1 hit) — `except BaseException` in `_load_s0_01_module` exists only to pop the half-registered module from `sys.modules` and **re-raises**. |
| waits/polls + ordinal gates in fakes (AF-AP-57) | **EMPTY.** No fake selects behaviour by call count. The runner's one poll is failure-aware (§5). |
| skips/xfails that cannot fire | **EMPTY.** No `skip`/`xfail` in the suite. |
| world-scoped enumerations (AF-AP-59) | **SAFE.** One `rglob` (`test_no_credential_value_in_any_committed_s0_03_file`) is scoped to `proofs/S0-03/` — this lane's own tree, not the world. |
| signal installs before their try (AF-AP-58) | **EMPTY.** No signal handlers. |
| `/proc/<pid>/exe` races (AF-AP-55) | **DEFECT — FIXED this round.** See §5, mutant M14. Residual **DOCUMENTED-LIMIT:** `readlink exe` and the `environ` read are two syscalls on one pid; the window is now bounded by the live-process poll, and a dead/recycled pid fails LOUD rather than yielding an empty list. |
| mirrors of the code under test | **SAFE.** The timeline reader is S0-01's, **imported** — `test_timeline_reader_is_imported_from_the_s0_01_checker` asserts module identity via `inspect.getmodule`, which a pasted copy would fail. |
| two counters over different populations asserted equal | **EMPTY.** |
| provably redundant guards | **SAFE.** The nonce domain floor (M13) and the empty-environ guard both have killers; neither is redundant. |
| hardlink-clobbering writes | **SAFE.** Both PC writers use `write_text` to a fresh path under a `mkdir -p` out-dir; no append-to-existing, no symlink follow into a shared location. |
| anything else that is a family | **FOUND:** the fixture↔spec `expected_model_id` coupling (§7.4) — a family of "static fixture silently stops testing what it names when a declared constant moves". Closed by `test_fixtures_track_the_spec_expected_model_id`. |

`scripts/report_lint.py` over this report, pasted verbatim:

```
report_lint: 16 refs - OK 16, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```

---

## 9. The exact registry diff for the class flip

S0-03's transition is already declared: `proofs/registry.yaml:34`, rule `map-pcbridge-s003`,
`blocked_credential` → `execution_proof` on the pc-bridge positive effect. **Apply only once the
PC legs have actually run and `evidence/` grades green** — the probe marker alone is not the proof.

```diff
--- a/proofs/registry.yaml
+++ b/proofs/registry.yaml
@@ -14 +14 @@
-  {"proof_id": "S0-03", "title": "Hermes to OmniRoute", "classification": "blocked_credential", "wave": 2, "spike_dependencies": ["pc-bridge"], "required_negative_controls": 1, "assertion_count": 3, "blocked": {"owner": "TBD-owner-credential", "unblock_condition": "secret OMNIROUTE_UPSTREAM_KEY present and accepted", "marker_path": "proofs/S0-03/blocked.json"}},
+  {"proof_id": "S0-03", "title": "Hermes to OmniRoute", "classification": "execution_proof", "wave": 2, "spike_dependencies": ["pc-bridge"], "required_negative_controls": 1, "assertion_count": 3},
```

Notes for whoever applies it: the `blocked` block goes away with the class (no other proof keeps
one while `execution_proof`); `required_negative_controls: 1` stays — this lane ships **3**, which
satisfies it; `assertion_count: 3` matches the seed's three assertions, mapped to the conjuncts in
§2. `proofs/registry.yaml` is an **attested input** (AF-AP-56), so the same increment must
regenerate every minted `result.json` and gate on `validate-ledger integrity` + `ledger-gen` +
`git diff --exit-code proofs/ledger.json`. Today S0-03 has **no** minted `result.json`, and both
gates are green on the current tree (§4).

---

## 10. Self-attack — the three most likely ways this is wrong

1. **"The identity assertion is still a mirror."** Ruled out by construction and by fixture:
   conjunct (iii) reads a column (`provider`) that the response body cannot carry, and
   `evidence-stub-route` is a bundle that passes everything else and dies only there (mutants M4,
   M9, M12). The residual — a hostile PC operator forging `omniroute-requests.json` — is out of
   scope for any checker that reads captured files, and is named in the checker docstring.
2. **"The fixtures encode the checker's own assumptions, so the tests are a mirror."** Partly
   true and stated: the tool-call frames are schema-derived, not capture-derived (§7.5), and every
   `PROVENANCE.md` says so in the row for that file. What keeps it from being a tautology is that
   the *envelope* comes from the real corpus, the shapes come from the committed protocol schema
   rather than from my reading of the checker, and 14 mutants of the **checker** all die.
3. **"The suite is green because the PC legs never ran."** Correct, and that is why §6 exists as a
   first-class NOT-run list and why the positive spec leg fails today. The one thing I could have
   done to hide it — writing a fake bundle into `evidence/` — is the thing the #1 rule forbids;
   leg B refuses with exit 5 instead.

---

## 11. What the coordinator must decide

1. **Land the `pins.py` seam** (§6) or authorise a proof-owned launcher for leg B. Until then
   S0-03 cannot capture.
2. **Re-mint or re-venue `blocked.json`** (§7.1).
3. **Fill `expected_model_id`** from the first PC capture, regenerating the two fixtures in the
   same edit (the test enforces it).
4. **Resolve the credential's three names** (§7.2) in the seed/registry.
