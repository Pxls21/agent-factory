# O3 — S0-03 round 3 implementation report

PIN: `a8273466ce0f`
Lane: O3, PC Hermes `code-implementer`
Timestamp: `2026-09-17T12:01:02Z`

Outcome: PROPOSAL. The six VERIFY-O2 bypass classes are repaired and deterministic gates are green. This lane cannot independently grade its own work.

NOT done: no live direct/Hermes/negative leg ran; no request was sent to OmniRoute or any model endpoint; no owner database, key file, or Hermes profile was read; EXPIRED→result flip and remint remain coordinator-owned.

## FILE IDENTITY — final bytes

- `64a61b9d6bafa00865aaccb993db6ecd5006a61d75ff0b86d68be9dcdbaca14f`  `proofs/S0-03/check_omniroute_roundtrip.py`  869 lines
- `13d1ea62a9a04916d023c61582199a1488bd89e639604868aa0714241e7f4ec6`  `proofs/S0-03/tools/pc/collect_leg.sh`  184 lines
- `27afe8a54a283e87695720f2dc2696c3ae6710711d337c5254b7a0a7bd85874d`  `proofs/S0-03/tools/pc/run_s0_03_legs.sh`  316 lines
- `688cdcbe3aa0be8129b8eefbe3706c5ff4a20ad2affd35d0f2f5eff714a3e78d`  `tests/test_s0_03_omniroute.py`  1932 lines
- `c4df34e55ad1c53adc747c8da38161118bf4355363bb5e7e8f44d937ed8ca04d`  `tasks/briefs/s0-03-support/O2-report.md`  589 lines
- `48aee1bec5b51969a9a6ede21edcd930591d30215261bc55ab99662570597169`  `proofs/S0-03/fixtures/evidence-credential-absent/omniroute-requests.json`  10 lines
- `48aee1bec5b51969a9a6ede21edcd930591d30215261bc55ab99662570597169`  `proofs/S0-03/fixtures/evidence-credential-rejected/omniroute-requests.json`  10 lines
- `18d25afac85f8942236146e133b9d75a78c98e40178e4c73562ae19b24d3136e`  `proofs/S0-03/fixtures/evidence-provider-key-present/omniroute-requests.json`  48 lines
- `5e3a3858073a3a57da3d20a8fbecb75f7621920e2f4db3c842081b1f8cfdd4a5`  `proofs/S0-03/fixtures/evidence-provider-key-present/hermes/leg.json`  9 lines
- `2fde221be65879f8ea4b946dfa778ebce520e84bcd793583f42e721a246ed553`  `proofs/S0-03/fixtures/evidence-stub-route/omniroute-requests.json`  48 lines
- `5e3a3858073a3a57da3d20a8fbecb75f7621920e2f4db3c842081b1f8cfdd4a5`  `proofs/S0-03/fixtures/evidence-stub-route/hermes/leg.json`  9 lines

## Items 1–7

### 1. Collector complete over the window

VERIFIED. Both graded SQL queries have no `LIMIT` and the `S0_03_LOG_LIMIT` knob is gone. The Hermes query uses `sql_start` and `sql_end` as a coarse one-second-before/two-seconds-after SQL prefix bound at `collect:123-145`; exact aware-instant filtering remains authoritative. The export records exact `row_counts` at `collect:153-162`.

RED before: the 49-earlier + target + foreign-row fixture exported zero Hermes rows because the cap hid both; the duplicate-direct fixture had no `row_counts`. Green after: `8 passed, 144 deselected in 0.99s`. Controls are at `T:1628-1669`.

### 2. Credential screen recursive with full path

VERIFIED. `_walk_credentials` traverses every mapping/list and names the full dotted path at `C:676-693`; `key_env` is exempt only at the exact provider-level location. Nested `api_key`, `headers.Authorization`, `extra_headers.Authorization`, and list-nested `X-Api-Key` were RED on the PIN. Green after: `5 passed, 152 deselected in 1.38s`; `test_credential_screen_recurses_over_the_whole_provider_block` starts at `T:423`.

### 3. Exact ordered terminal call

VERIFIED. The committed fixture carries ACP `kind: execute`, `rawInput.command`, and `toolCallId`. `check_roundtrip` now accepts only exact bare/single/double-quoted `printf <nonce2>`, a single exact execute start, then a later completed `tool_call_update` with the same id at `C:602-659`.

RED before: `test_roundtrip_rejects_read_file_whose_output_quotes_nonce` at `T:1229`, completion before start, and `printf other` plus unrelated nonce output. Green after: `8 passed, 153 deselected in 2.01s`; `test_roundtrip_rejects_wrong_terminal_command_with_unrelated_nonce_output` starts at `T:1256`.

Primary source: vendored `acp.rs:1762-1780` reads `tool_call.kind` and `tool_call_update.toolCallId/status`; committed `timeline.jsonl:6-8` carries `rawInput.command` and the matching completion.

### 4. Strict pid bound to the tee record

VERIFIED. The runner copies the env writer's resolved child pid into `hermes/leg.json` at `run:253-260`. `check_env_record` rejects bool/non-int/non-positive pid values and requires exact equality with `agent_child_pid` at `C:742-773`. The two positive-shaped committed fixtures now carry this field.

RED before: string, zero, negative, `True`, mismatch, and absent `agent_child_pid` all passed. Green after including committed bundles: `11 passed, 156 deselected in 2.15s`; controls start at `T:1340`. Producer evidence: `frame_tee.py:283-290` writes `agent_child_pid`; `hermes_env_names.py:126-141` resolves and records it.

### 5. Offset-aware instants only

VERIFIED. `_instant` rejects absent/undefined offsets and normalises valid stamps to UTC at `C:456-468`. Offset-less row, window start, and window end each produced a `TypeError` traceback on the PIN; each now returns rc 1 with its named `failure_reason` and no traceback. Equivalent `+02:00` input passes. Green after with edge controls: `6 passed, 165 deselected in 1.63s`; controls start at `T:1880`.

### 6. Exact POST on both rows

VERIFIED. `transport_method` is declared at `C:148` and grades both rows at `C:546-552`. Direct GET, Hermes GET, and lowercase `post` passed on the PIN and now fail with the leg and observed method. Green after: `6 passed, 168 deselected in 1.36s`; controls start at `T:387`.

### 7. O2 report stamp

VERIFIED. `O2-report.md:1` has the exact required stamp. No other O2 report content changed.

## Item 8 — mutation disposition

VERIFIED: full S0-03 suite `174 passed in 26.56s`. The six VERIFY-O2 bypass classes are killed by named tests. The 48 earlier core controls remain represented in the same suite. VERIFY-O2's decision-irrelevant survivors are unchanged: call-log `id`, compression response headers, protocol metadata, and direct usage are not decision inputs.

## Gates

- `RESULT: rev=a8273466ce0f files=11 deleted=0 runs=2 tests=89f05701192e identical=yes rc=0 summary="242 passed in 42.26s 242 passed in 41.89s"`
- Direct S0-03 run: `174 passed in 26.56s`
- Pyflakes: `PYFLAKES_RC=0`
- Shell parse: `COLLECT_BASH_N_RC=0`; `RUNNER_BASH_N_RC=0`
- `git diff --check`: `DIFF_CHECK_RC=0`
- AP screens: checker 0; collector 0; runner 0; env writer one AP-1 hit at `env:52` (`proc_root` is an existing test seam, unchanged). Test-screen classifications: `AF-AP-34` ×3 at `T:891` (`pkill` source text); `AF-AP-80` ×2 at `T:1567` (`pc_mention.sh` source inspection); `AF-AP-59` ×1 at `T:891`. AF-AP-71: 0 hits.
- Final code-intel pack: `/home/rocco/agent-factory/.lanes/pc-o3.md--a827346/scratch/pack-o3-final.md` (386 lines). GitNexus `detect-changes`: 11 files, 30 symbols, risk high; affected execution flows are checker assembly and identity/instant checks. The clone index reports 233 commits stale; exact diff gates above are authoritative.

## Evidence tiers

VERIFIED: all code/test claims and counts above; no production sockets or databases touched.

INFERRED: the runner will copy the same child pid because `hermes_env_names.py` resolves `runtime-identity.json.agent_child_pid` and the runner reads its emitted record. A live coordinator capture must prove this in the production path.

ASSUMED: none.

## Self-attack

1. The SQL prefix bound could exclude a valid edge. Ruled out by one-second-before/two-seconds-after UTC bounds plus exact closed-window filtering and the pre-existing both-edge test.
2. Credential recursion could exempt nested `key_env`. Ruled out by an exact path-depth condition and nested mapping/list hostile controls.
3. Tool completion could bind to the wrong event. Ruled out by exact command/kind/rawInput shape, same `toolCallId`, strict later index, output nonce, and final text nonce controls.

## Discrepancies

- Initial pack invocation used repeated symbols without repeated `-s`; `lane_context.sh` parsed the extra names as file paths. Re-run with one `-s` per symbol succeeded.
- Initial credential RED run failed from the test's missing `yaml` import, not the premise. After adding the import, four bypasses reproduced as rc 0 PASS.
- The fixture regeneration required `row_counts` in all four exports and `agent_child_pid` only in the two bundles with a Hermes leg. No failure key belongs in `spec.json`; `transport_method` is a checker reason-table key, while the spec schema enumerates legs, not reason keys.
- Report lint: `21 refs — OK 21, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## Reasoning record

Rejected alternative: retaining a configurable high SQL cap. It cannot prove completeness and preserves AF-AP-71. Ordering rationale: collector completeness first, then checker dimensions, then producer/fixtures, then the frozen report stamp and whole-suite gates. The live capture remains separate because this lane was expressly forbidden from contacting OmniRoute/Hermes.

Retro: no new bug class beyond VERIFY-O2's registered AF-AP-71/72 findings; nothing to bake.
