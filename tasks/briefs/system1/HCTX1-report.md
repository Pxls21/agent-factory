# HCTX1 report: lane profiles carry the local models' real context length (task #310)

Lane: code-implementer (sandbox, Opus 5.5). Brief: `tasks/briefs/system1/HCTX1-brief.md` (6a430bf). PIN: origin fb7f614.
Started 2026-09-26 03:4xZ, finished 04:2xZ.

**Status: DONE in the sandbox; NOT verified live** (the PC check in section 6 is written out, not run: no bridge in this lane).
Premise CONTRACT-VALID. `lane-profile.sh create` writes `providers.<lane provider>.models.<id>.context_length` for
`agentfactory-build-local`, `agentfactory-verify-local` and `qwen-local/qwen3.8-27b-local`, from the quadlet's `[Container]`
`MAX_LEN` (131072 with one stderr line when unreadable or unset; a non-integer fails the create); `verify` names a missing or
wrong override. Gate: `lane profile: 24 passed, 0 failed` and `67 passed, 0 failed` (test_pc_lane.sh), twice, identical;
`run-all.sh` ALL SUITES PASSED. Negative controls: the PIN helper fails 13 checks; 15 of 15 named mutants killed.
Read first: D-1 (a lane relaunched on an old PIN needs its old `aflane*` profile removed) and A-1 (an adjacent latent defect).

## 1. Premise check

- [verified] `harness-ports/` is unchanged between the PIN fb7f614 and HEAD 6a430bf (`git diff --stat fb7f614 HEAD -- harness-ports/` is empty).
- [verified] `bash harness-ports/tests/test_lane_profile.sh` on the PIN helper, rc 0, last line pasted:
  `lane profile: 13 passed, 0 failed`
- [verified] anchors: `25:verify_lane() {`, `89:create_lane() {`, `113:  # Preserve every untouched byte in config.yaml. ...` (match the brief).
- [verified] a local Hermes checkout exists (`/home/user/nerdherderdani/hermes-agent`, HEAD 527da60 = the S0-01 proof pin, a
  `blob:none` partial clone); the lane-runtime pin b3399c139624 (`upstream.lock.yaml` `lane_runtime`) is present as a commit and its
  `agent/agent_init.py` and `hermes_cli/config.py` blobs are local (`GIT_NO_LAZY_FETCH=1 git cat-file -e`), so the brief's Hermes
  claims are checked below at the exact lane pin, read-only (`git show`, no fetch, no checkout).

### 1a. The brief's Hermes claims, checked at the lane pin b3399c1 (03:5xZ)

Source: `git show b3399c1:<path>` in the local checkout; two absent blobs fetched raw from GitHub at the pinned commit and
proven identical by `git hash-object` (`hermes_cli/config_providers.py` = 4e6e9dd1, `hermes_cli/model_switch_providers.py` = 0d1c408b,
both equal to the pin's tree entries). No git write, no checkout.

| Claim in the brief | Verdict | Evidence at b3399c1 |
|---|---|---|
| `get_compatible_custom_providers` = legacy list + `providers_dict_to_custom_providers(config["providers"])` | verified | `config_providers.py:312-350`; re-exported by `config.py:667-677` (the brief says `config*.py`; the body is in `config_providers.py`) |
| entries normalized by `_normalize_custom_provider_entry`, base_url from `api` | verified | `config_providers.py:184-274`; `_pick_provider_base_url` tries `base_url`, `url`, `api` in that order (123-147) |
| `_normalize_provider_models`: a non-empty dict kept, list converted, both sentinels stripped | verified | `config_providers.py:150-181` |
| per-model `context_length` read for the route-matching entry | verified, with a correction | the value is SET by `get_custom_provider_context_length(model=agent.model, base_url=agent.base_url)` (`agent_init.py:1720-1727` -> `config_providers.py:481-513`: every entry whose normalized base_url equals the route, `models[<model>].context_length`, `int()`, first positive wins). The `_cp_models.get(agent.model, {}).get("context_length")` lines the brief cites (`agent_init.py:1652-1671`) are the invalid-value WARNER, called only when resolution returned nothing |
| `model.context_length` ignored when the runtime model differs from `model.default` | verified | `_scope_context_length_to_default_runtime`, `agent_init.py:1602-1646`, applied at 1711-1714 |
| the resolved value is what the compressor uses | verified (beyond the brief) | `_effective_lmstudio_context_length` returns the explicit value for a non-LM-Studio provider (`run_agent.py:427-436`; `_ensure_lmstudio_runtime_loaded` returns None unless the provider is lmstudio, `run_agent.py:446-448`); `ContextCompressor(` gets `config_context_length=_effective_context_length` (`agent_init.py:1841-1845`) -> `get_model_context_length` step 0 "Explicit config override — user knows best" returns it before any `/v1/models` lookup (`model_metadata.py:1849-1861`) |

Premise verdict: CONTRACT-VALID. No mismatch that matters. One citation correction (the resolver is
`get_custom_provider_context_length`, not the warner's lines) changes nothing in the design.

### 1b. The brief's question: does a `models` dict under a `discover_models: true` provider change listing or acceptance?

- [verified] No allowlist. `_models_config_is_allowlist` (`model_switch.py:70-84`) returns False for any dict ("per-model
  *metadata* ... not a catalog narrow"); only list and string shapes pin a row. The legacy sentinel
  `__explicit_model_allowlist__` is only stripped (`config_providers.py:163`, `model_switch.py:35`); it enables nothing at this pin.
- [verified] Listing: `_absorb_entry_models` (`model_switch_providers.py:443-455`) adds the declared ids to the `/model` picker row,
  but a successful live `/v1/models` probe replaces the row's list (`grp["models"] = discovered`, `model_switch_providers.py:990-997`). So the ids can show in the
  picker only when discovery fails.
- [verified] Discovery persistence cannot clobber the override: `_save_discovered_models_to_config` rewrites only the legacy
  `custom_providers` list, and never a hand-curated mapping (`model_switch_providers.py:27-80`). The override lives in `providers`.
- [inferred] Acceptance: custom-provider validation probes the live `/v1/models` (`probe_api_models`, `models_validate.py:248-262`), not the config dict,
  so the dict does not change which ids Hermes accepts. Not traced through every CLI path.

### 1c. Which model ids

- [verified] `scripts/pc_lane.sh:176-179` and `harness-ports/bin/pc-lane.sh:432-441` treat `agentfactory-*-local|qwen-local/*` as local
  routes; a lane can run `HERMES_MODEL=qwen-local/qwen3.8-27b-local` (`-m "$RUN_MODEL"`, `pc-lane.sh:460-461`, no `--provider`).
- Decision: the raw `qwen-local/qwen3.8-27b-local` BELONGS. It is a reachable lane model on the same vLLM, and OmniRoute's 128000 for it
  is not the server's number; with it, every local id follows MAX_LEN. The bare `qwen3.8-27b` alias is not listed by OmniRoute
  (premise), so it is not written.
- [inferred] The lookup key is `agent.model` verbatim; for a `custom` provider Hermes strips only a literal `custom/` prefix
  (`_strip_matching_provider_prefix`, `model_normalize.py:135-149`), so `qwen-local/...` should stay whole. The PC check in section 6 settles it by measurement.

### 1d. The value source

- [verified] `deploy/qwen.container` (the committed source of the PC quadlet, PC-BRIDGE.md:159-175) has `Environment=MAX_LEN=131072` in
  its `[Container]` section. Its lines sit 9 lower than the PC copy's (premise lines 18-22); the values match.
- [verified] Sibling pattern: `scripts/gpu_side_by_side.sh:88-126` already parses this unit's `[Container]` section with shlex quoting
  and never echoes an `Environment=` value. The helper follows it.

### 1e. Impact and callers (04:0xZ)

- GitNexus CLI `impact create_lane|verify_lane --direction upstream`: `Target ... not found`, risk UNKNOWN (it does not index shell
  functions). Confirmed by text search (`grep -rl lane-profile.sh`): the one runtime caller is
  `LANE_PROFILE_HELPER` in `harness-ports/bin/pc-lane.sh:447-454`, which captures `create`'s STDOUT as the profile name and treats any nonzero exit of `create` or `verify`
  as fatal. So the fallback line goes to stderr only, and stdout stays exactly the profile name.
  `harness-ports/tests/test_pc_lane.sh:55-65` writes its own labelled fake helper (`A labelled fake lane-profile helper`), so it
  does not run this file. `.github/workflows/stage0-ci.yml` names the file (CI runs the suite).
- Transition hazard (found, not fixed; see DISCREPANCIES): `pc-lane.sh` never removes lane profiles, the lane id is
  `<brief name>-<PIN[:8]>` (`LANE_ID`, `pc-lane.sh:85`), and the helper runs from the PC clone, not the lane's pinned tree. A lane relaunched on
  its old PIN after the landing reuses its pre-landing `aflane*` clone, and `create` then fails in `verify` (override missing).

## 2. The change (04:1xZ)

Files: `harness-ports/bin/lane-profile.sh` (298 -> 475 lines), `harness-ports/tests/test_lane_profile.sh` (241 -> 527 lines).
`git diff --stat`: 2 files changed, 473 insertions(+), 10 deletions(-) (before the final report edits; the report is new).

| What | Where (helper) |
|---|---|
| quadlet path default `$HOME/.config/containers/systemd/qwen.container`, overridable by `QWEN_QUADLET` like the helper's other defaults | `lane-profile.sh:15` |
| the model list, one place: `agentfactory-build-local agentfactory-verify-local qwen-local/qwen3.8-27b-local` | `lane-profile.sh:19` |
| `quadlet_context_length`: `[Container]` section only, shlex quoting, backslash continuation, last `MAX_LEN` wins; unreadable file or no `MAX_LEN` -> prints 131072 and ONE stderr line naming why; a value not matching `[0-9]+` or equal to 0, or an `Environment=` line that does not parse -> exit 64 with the reason; no message echoes any other `Environment=` value | `lane-profile.sh:32-74` |
| resolved ONCE per run in the dispatch (create's internal verify reuses it, so a fallback prints one line per run) and BEFORE any clone (a bad value leaves no profile) | `lane-profile.sh:469-472` |
| `lane_provider`: the one `providers` entry whose `api` equals `model.base_url` (strip, trailing `/` dropped); zero or several -> refuse | `lane-profile.sh:94-100`, `233-239` |
| `add_override`: sets `models.<id>.context_length` for the three ids, keeping every other id and every other setting of the same id; a non-mapping `models` (list = allowlist) or `models.<id>` -> refuse | `lane-profile.sh:103-115`, `242-254` |
| create: override added to the expected semantic config; then a text edit that APPENDS a `models:` block after the lane provider's last content line, or RE-EMITS that provider's existing `models:` block (the helper's hooks precedent); the existing guard (`after == expected`, top-level key sets) still refuses any collateral change | `lane_provider(expected)` at `lane-profile.sh:270-275`; text edit 341-381; guard 428-437 |
| verify: after the chain and header checks, each id's `context_length` must be present (`context override missing: <id>`) and be exactly the int resolved from the quadlet (`context override wrong: <id>=<got> (expected <n>)`); then the full semantic comparison includes the override | `lane-profile.sh:138-160` |
| the byte-preservation comment names the new delta | `Preserve every untouched byte`, `lane-profile.sh:212-215` |

Untouched: `discover_models`, `model.*` except the existing header, every other provider, the base profile (verified by test 24
and mutant M9), the name rule, `remove`.

Worked example (scratch smoke on the premise's base-profile shape, fake key made at run time), `diff base clone`:
```
8a9,15
>     models:
>       agentfactory-build-local:
>         context_length: 98304
>       agentfactory-verify-local:
>         context_length: 98304
>       qwen-local/qwen3.8-27b-local:
>         context_length: 98304
12a20,21
>   default_headers:
>     x-omniroute-session-id: smoke-1
```
(98304 = the smoke quadlet's `[Container]` value; its `[Service]` decoy 4096 was ignored; verify rc 0; base `cmp` equal.)

## 3. Tests (`harness-ports/tests/test_lane_profile.sh`)

Fixture style kept: the labelled fake `hermes`, throwaway profile roots, hermetic `unset` (now also `QWEN_QUADLET`, line 7).
Fixture quadlet `$TMP/qwen.container` (line 41): the premise's five `[Container]` lines with `MAX_LEN=98304` (distinct from the
131072 fallback, so a value from the file is distinguishable from a guess) and a `[Service]` decoy `MAX_LEN=4096`. Three extra
base profiles (`make_source`, line 82): the premise's order with an existing `models` block and a second provider on another
route; one with no provider on the lanes' route; one with list-shaped `models`. Keys in fixtures are fake, written at run time.

Changed existing checks (oracle extended by exactly the contract's new delta, never weakened):
- #2 `create strips only the chain, adds the exact lane header and context override, ...` (line 186): the expected semantic config
  gains the three ids at 98304, as an independent literal.
- #10 `switch OFF leaves the clone byte-identical to the chain, header and context override rewrite` (line 277): the byte oracle
  appends the exact seven block lines, guarded by an assertion that the fixture's last line is the provider's last key.
- #11 gate ON (line 312): the expected config gains the override.
- Main fixture provider gained `default_model`, `discover_models: True` and a comment line (a whole-file re-emit would lose both
  the comment and the `True` spelling; mutant M11 proves the byte checks see it).

New checks (#14-#24):

| # | Check (line) | Demand covered |
|---|---|---|
| 14 | quadlet `[Container]` MAX_LEN written for each local model under the lane provider, ints, not in `model.*`, no stderr (377) | override for each model; value from fixture quadlet |
| 15 | unreadable quadlet -> 131072, exactly one stderr line (exact text), stdout = profile name; verify prints the same one line (387) | fallback with its stderr line |
| 16 | no `[Container]` MAX_LEN -> fallback with its reason; `[Service]` MAX_LEN ignored (396) | fallback; section rule |
| 17 | 10 refusal cases, each rc 64, exact stderr, empty stdout, no clone, no `profile create` call: `128k 0 00 -1 1.5 '' +131072 0x20000`, full-width digits, an unbalanced quote (418) | non-integer value refused |
| 18 | backslash continuation read, last assignment wins (427) | parser claims in the helper's comment |
| 19 | `QWEN_QUADLET` unset -> reads `$HOME/.config/containers/systemd/qwen.container` (value 114688) (436) | the PC's real path |
| 20 | existing `models` kept (other id, the same id's `max_tokens`), other provider's `777` untouched, whole file byte-exact against a hand-written expected file, verify rc 0 (483) | existing models kept; byte preservation |
| 21 | no provider on the route, list-shaped models -> rc 64 with exact reasons (491) | fail-closed shapes |
| 22 | verify: one id deleted, whole block deleted -> `context override missing: <id>` (505) | verify fails on missing override |
| 23 | verify: 200000, a float 98304.0, and a quadlet moved to 65536 after creation -> `context override wrong: ...`; restored clone passes (519) | verify fails on wrong override |
| 24 | sha256 of every base profile's `config.yaml` and `.env` equal before and after the whole suite (524) | base profile never written |

## 4. Negative controls (scratch driver `nc.py`: the NEW test run against the PIN helper and 15 named mutants of the new helper;
each mutant is an exact-string replacement with an asserted occurrence count, so a mutant that fails to apply is an error, not a
survivor). Every kill below is a FAILED check in a suite that ran to its summary line, never an error (AF-AP-223).

```
== PIN: rc=1 | lane profile: 11 passed, 13 failed        (fails #2 #10 #11 #14-#23; the 11 unchanged checks + #24 pass)
== M1-fallback-value (131072 -> 131071): rc=1 | lane profile: 22 passed, 2 failed           kills #15 #16
== M2-no-section ([Service] counted): rc=1 | lane profile: 17 passed, 7 failed             kills #2 #10 #11 #14 #16 #20 #23
== M3-zero-accepted (<= 0 -> < 0): rc=1 | lane profile: 23 passed, 1 failed                kills #17
== M4-overwrite-models (models = {}): rc=1 | lane profile: 22 passed, 2 failed             kills #20 #21
== M5-verify-no-override-check: rc=1 | lane profile: 22 passed, 2 failed                   kills #22 #23
== M6-verify-type-lax (no int check): rc=1 | lane profile: 23 passed, 1 failed             kills #23
== M7-default-path (qwen-server.container): rc=1 | lane profile: 23 passed, 1 failed       kills #19
== M8-double-resolve (verify re-reads): rc=1 | lane profile: 22 passed, 2 failed           kills #15 #16
== M9-writes-base (appends to source): rc=1 | lane profile: 22 passed, 2 failed            kills #10 #24
== M10-url-filter-dropped: rc=1 | lane profile: 22 passed, 2 failed                        kills #20 #21
== M11-whole-file-reemit: rc=1 | lane profile: 22 passed, 2 failed                         kills #10 #20
== M12-no-continuation: rc=1 | lane profile: 23 passed, 1 failed                           kills #18
== M13-first-assignment-wins: rc=1 | lane profile: 23 passed, 1 failed                     kills #18
== M14-two-models (qwen-local id dropped): rc=1 | lane profile: 14 passed, 10 failed       kills #2 #10 #11 #14-#16 #18-#20 #23
== M15-ascii-to-str (!a -> !s): rc=1 | lane profile: 23 passed, 1 failed                   kills #17
```
(The `== ...: rc | summary` parts are pasted from the driver output; the mutant descriptions and the check numbers after them are
mine, mapped from each run's FAIL list.) Every new or changed check reds on the PIN helper or on a named mutant; #24 is the one
the PIN passes, and M9 kills it. First pass of the new suite was green (23/23, then 24/24 after adding #18 and the float case in #23:
both were added because M6 and M12/M13 would otherwise have survived; a string `'98304'` is unequal to 98304 anyway, so only a float
separates a type-strict verify from a lax one).

## 5. Gates (pasted; final files: `lane-profile.sh` sha256 `8192cb678b8cca09…`, `test_lane_profile.sh` sha256 `7e9f64d8e5480b88…`)

Set (brief demand 4): every test that names the helper, `grep -l 'lane-profile.sh' harness-ports/tests/* tests/*` =
`harness-ports/tests/test_lane_profile.sh`, `harness-ports/tests/test_pc_lane.sh`. Two runs on the final files, at 04:20Z (`date -u`):
```
run1 test_lane_profile.sh   rc=0 | lane profile: 24 passed, 0 failed | verdict-lines sha bd4d714fe8cb
run1 test_pc_lane.sh        rc=0 | 67 passed, 0 failed | verdict-lines sha fd1529455606
run2 test_lane_profile.sh   rc=0 | lane profile: 24 passed, 0 failed | verdict-lines sha bd4d714fe8cb
run2 test_pc_lane.sh        rc=0 | 67 passed, 0 failed | verdict-lines sha fd1529455606
```
(verdict-lines sha = sha256 of the run's PASS/FAIL lines without the because-lines; identical across the two runs, so the
verdicts are deterministic. The because-lines carry no temp paths except the fallback checks' expected messages.)

Full `bash harness-ports/tests/run-all.sh`, once, 04:15Z-04:16Z, same code (no edit to either file after it), rc 0:
```
test_codex_hook_adapter.py         7/7 passed
test_hermes_hook_adapter.py        6/6 passed
test_hermes_spool.py               9/9 passed
test_lane_done_gate.py             lane done gate: 19 passed, 0 failed
test_bridge_token_handling.py      test_bridge_token_handling: 9 checks passed — ALL OK
test_pc_bridge_exec.py             test_pc_bridge_exec: 8 checks passed
test_hermes_session_export.py      test_hermes_session_export: 15 checks passed
test_omniroute_local_builder.py    test_omniroute_local_builder: 24 checks passed
test_lane_profile.sh               lane profile: 24 passed, 0 failed
test_pc_lane.sh                    67 passed, 0 failed
test_pc_lane_dispatcher.sh         pc_lane dispatcher: 51 passed, 0 failed
test_pc_lane_admission.sh          22 passed, 0 failed
test_qwen_server.sh                qwen-server: 101 passed, 0 failed
test_qwen_matrix.py                test_qwen_matrix: 4 tests passed
test_qwen_matrix_sh.sh             qwen-matrix-sh: 19 passed, 0 failed
test_lane_context.sh               5 passed, 0 failed
test_context_mirrors.sh            11 passed, 0 failed
test_sync_skills.sh                34 passed, 0 failed
build-roles --check                OK: 3 role config layers match their sources
ALL SUITES PASSED
```
- `bash -n harness-ports/bin/lane-profile.sh`: rc 0 (and rc 0 for the test file).
- `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>`: `0` for the helper, the test and this report (last run in section 10).
- `python3 scripts/ap_screen.py` on both files: `13 hits over 2 files` (AF-AP-118: 12, AP-51: 1), the same 13 as on the PIN
  versions of both files (AF-AP-118: 12, AP-51: 1): no new hit. AF-AP-118 matches the `fallback_providers` strings in the code whose
  job is to strip that chain; AP-51 matches the word "byte-identical" in check #10's name, a claim backed by a real byte compare.

## 6. The coordinator's PC check (NOT run here: no PC bridge in this lane, by rule) (04:1xZ)

Run after the landing and the PC clone's ff-sync. It reads the owner's profile only through the clone, sends no model request,
prints no key, and removes the throwaway profile. Hermes's interpreter is the venv behind `~/.hermes/hermes-agent/venv/bin/hermes`
(PC-BRIDGE.md). The first probe runs the SAME two calls `agent/agent_init.py:1702-1727` makes (`get_compatible_custom_providers`,
then `get_custom_provider_context_length(model=agent.model, base_url=agent.base_url)`), with the base URL from Hermes's own runtime
resolver for the profile's `custom:omniroute-fedora`, then `get_model_context_length` with that value (its step 0 returns it before
any `/v1/models` lookup, `agent/model_metadata.py:1860-1861`).

```bash
cd ~/agent-factory && H=harness-ports/bin/lane-profile.sh
P="$(bash "$H" create hctx1-pc-check)"; echo "create rc=$? profile=$P"   # expect rc 0, aflanehctx1pccheck, and NO stderr line
bash "$H" verify hctx1-pc-check; echo "verify rc=$?"                    # expect rc 0 and no output
python3 - "$HOME/.hermes/profiles/$P/config.yaml" <<'PY'                # the override as written: ids and integers only
import sys, yaml
c = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
print("model.provider", c["model"]["provider"], "| model.base_url", c["model"]["base_url"])
for k, v in c["providers"].items():
    print(k, v.get("api"), v.get("discover_models"), {m: s.get("context_length") for m, s in (v.get("models") or {}).items()})
PY
HERMES_HOME="$HOME/.hermes/profiles/$P" ~/.hermes/hermes-agent/venv/bin/python - <<'PY'
from hermes_cli.config import load_config, get_compatible_custom_providers, get_custom_provider_context_length
from hermes_cli.runtime_provider import resolve_runtime_provider
from agent.model_metadata import get_model_context_length
cfg = load_config()
cps = get_compatible_custom_providers(cfg)
for m in ("agentfactory-build-local", "agentfactory-verify-local", "qwen-local/qwen3.8-27b-local"):
    try:
        base = resolve_runtime_provider(requested=cfg["model"]["provider"], target_model=m)["base_url"]
    except Exception as exc:  # prints the class only, never a value
        base = cfg["model"]["base_url"]; print("runtime resolver:", type(exc).__name__, "-> model.base_url")
    ctx = get_custom_provider_context_length(model=m, base_url=base, custom_providers=cps)
    print(m, "| base_url", base, "| per-model", ctx, "| resolved", get_model_context_length(m, base_url=base, config_context_length=ctx))
PY
bash "$H" remove "$P"; echo "remove rc=$?"; ls -d "$HOME/.hermes/profiles/$P" 2>&1 | tail -1   # expect: No such file or directory
```

Pass: create prints only the profile name (a `lane-profile: context_length 131072: ...` line would mean the quadlet was NOT read,
which today is invisible in the value because the fallback equals MAX_LEN); each model prints `per-model 131072 | resolved 131072`;
the owner's `~/.hermes/profiles/agentfactory/config.yaml` is byte-identical before and after (`sha256sum` it first).
A `per-model None` for `qwen-local/qwen3.8-27b-local` alone would mean Hermes rewrites that id before the lookup (section 1c,
inferred) and the id should come out of `CONTEXT_MODELS`.

## 7. Self-attack: the three likeliest ways this change is wrong (04:2xZ)

1. **The override is written but Hermes never applies it (a hollow green).** Ruled out in code at the lane pin, not by run:
   the key is `providers.<entry whose normalized base_url = agent.base_url>.models[agent.model].context_length`
   (`get_custom_provider_context_length`, `config_providers.py:481-513`), which `_resolve_context_length` calls whenever
   `model.context_length` is absent or dropped (`get_custom_provider_context_length(`, `agent_init.py:1720-1727`); the LM Studio
   step passes the explicit value through for any other provider (`_effective_lmstudio_context_length`, `run_agent.py:427-436`);
   the compressor's `get_model_context_length` returns it at step 0 before any `/v1/models` lookup
   (`Explicit config override`, `model_metadata.py:1859-1861`). Residual [inferred]: that `agent.model` is the `-m` id verbatim and `agent.base_url` is the
   provider's `api` at runtime. The PC check in section 6 measures both with Hermes's own functions and its runtime resolver.
2. **The helper reads the wrong value on the PC and hides it behind the fallback.** Today the fallback (131072) equals the served
   MAX_LEN, so a wrong path or section would be invisible in the number. Ruled out as far as the sandbox can: test #19 pins the
   default path (`$HOME/.config/containers/systemd/qwen.container`, value 114688, no stderr) and M7 is killed; tests #14/#16 pin the
   `[Container]` rule (M2 killed); the committed `deploy/qwen.container` has `MAX_LEN` in `[Container]`. On the PC, the check's pass
   condition is "no stderr line on create": any fallback prints one, naming why.
3. **The text edit damages the owner's config shape in a way the tests do not model.** The guard is the helper's existing one:
   the clone is written only when `yaml.safe_load(after) == expected` and the top-level key sets match, so a misplaced block is
   refused, never written (mutants M10/M11 show the byte checks see a wrong provider and a whole-file re-emit). Tests #10 and #20 pin
   exact bytes for both paths (append at EOF; re-emit an existing block mid-provider, with a following provider, providers first).
   Residual: shapes not covered (flow-style provider, quoted provider key, YAML anchors in `models`) are REFUSED, so the failure mode
   is a lane that does not start, loudly, not a silently wrong profile. The premise's base profile is block style (section 1).

## 8. NOT done

- NOT run: the PC check (section 6). No bridge in this lane, by rule. So the resolved value in a real Hermes on the PC is not
  measured; sections 1a and 7.1 carry the code-level evidence, and the `qwen-local/...` key match is [inferred].
- NOT done: no commit, no push (the coordinator lands); no registry row or `/bug-echo` run for the adjacent defect A-1 below
  (`docs/INCIDENT-LOG.md` is outside my boundary); a read-only sibling scan for A-1's pattern found hits only in these two files.
- NOT done: stale-profile cleanup on the PC (see D-1). Not in the brief; it is an operator step.
- NOT changed (boundary): `harness-ports/bin/pc-lane.sh` comments that still say "the one 262k slot" (lines 24, 427).

## 9. DISCREPANCIES, deviations, adjacent defects

Discrepancies with the brief:
- D-0 (citation, no effect): the brief's `agent_init.py ~1655-1675` `_cp_models.get(...)` lines are the invalid-value WARNER
  (`_warn_invalid_custom_provider_context_length`, 1652-1671); the value is resolved by `get_custom_provider_context_length`
  (`config_providers.py:481-513`), called as `get_custom_provider_context_length(` from `agent_init.py:1720-1727`. Same key
  shape, same semantics.
- D-1 (transition hazard, operational, LOUD): lane profiles persist (`pc-lane.sh` never removes them), the lane id is
  `<brief name>-<PIN[:8]>` (`LANE_ID`, `pc-lane.sh:85`), and the helper runs from the PC clone. After the landing, relaunching a brief on the
  PIN it already ran with (for example VERIFY-SCRUB2's pending relaunch, if its brief keeps its PIN) reuses a pre-landing
  `aflane*` clone; `create` then fails in verify with `lane-profile: context override missing: agentfactory-build-local` and the
  lane dies at "lane profile create failed". Fix per lane: `bash harness-ports/bin/lane-profile.sh remove aflane<id>` before the
  relaunch, or re-pin the brief. The contract requires verify to fail here, so I did not add an in-place upgrade.
- D-2 (layout, no effect): the PC's quadlet lines sit at 18-22 (premise), the repo copy's at 27-31 (`deploy/qwen.container`);
  the values match. The deployed file is not byte-identical to the committed one.

Deviations and design choices beyond the letter of the contract (each is tested and each is a refusal or a narrowing):
- Only the quadlet's `[Container]` section counts (podman passes only it to the container), with systemd quoting, backslash
  continuation and last-assignment-wins; the sibling `scripts/gpu_side_by_side.sh` parses the same section.
- An `Environment=` line in `[Container]` that shlex cannot parse FAILS the create (exit 64) instead of falling back: a line that
  may carry MAX_LEN but cannot be read is treated as "not a positive integer", never guessed.
- `+131072`, `00`, `0x20000`, full-width digits are refused: only ASCII digits, value above 0. No upper bound (the contract has
  none; an absurd 4300+ digit value fails closed with a Python traceback, exit 1).
- The lane provider is the ONE `providers` entry whose `api` equals `model.base_url` (strip, trailing `/`); none or several
  -> create refuses. A provider that spells its URL as `base_url` or `url` instead of `api` is refused (Hermes itself reads
  `base_url`, `url`, `api` in two different orders, `config_providers.py:123-147` vs `runtime_provider_custom.py:40-41`).
- A list-shaped `models` (an allowlist in Hermes's terms) or a non-mapping `models.<id>` is refused, not converted.
- verify is type-strict: `context_length` must be an `int` equal to the value (a float 98304.0 fails; Hermes would accept it).
- Two existing check NAMES changed (#2, #10) and three existing oracles gained the override (#2, #10, #11); the main fixture's
  provider gained `default_model`, `discover_models: True` and a comment. Nothing was weakened; the PIN helper fails all three.
- Pre-existing behavior kept: a create whose rewrite fails leaves the half-made clone on disk (verify then refuses it); the new
  refusals share this.

Adjacent defects (found, NOT fixed):
- A-1 (latent, switch OFF by default): both heredoc calls compute the repo root three levels above `bin/`
  (`dirname "${BASH_SOURCE[0]}")/../../..`, `lane-profile.sh:84`, `216`), which is the PARENT of the repo (`/home/user` in the sandbox; `$HOME` on the PC). With
  `LANE_DONE_GATE=1` the two hooks therefore name `<parent>/harness-ports/bin/lane-done-gate.py`, a file that does not exist; the
  real one is `<repo>/harness-ports/bin/lane-done-gate.py`. `test_lane_profile.sh:284` (`$HERE/../../..`) computes the same wrong root, so the gate-ON
  test is a mirror and passes. Class: a path oracle derived by the same arithmetic as the code under test. Verified by path
  arithmetic in the sandbox (`cd harness-ports/bin/../../.. && pwd` -> `/home/user`; `/home/user/harness-ports` absent).
- A-2 (stale prose): `pc-lane.sh:24` and `:427` say the local model has "the one 262k slot"; the served limit is 131072.

## Appendix: the 15 mutants, exact (pasted from the scratch driver `nc.py`; each `(old, new, expected count)`)

```python
MUTANTS = {
    "M1-fallback-value": [('path, fallback = sys.argv[1], 131072', 'path, fallback = sys.argv[1], 131071', 1)],
    "M2-no-section": [('if section != "Container" or not eq or key.strip() != "Environment":',
                       'if not eq or key.strip() != "Environment":', 1)],
    "M3-zero-accepted": [('or int(value) <= 0:', 'or int(value) < 0:', 1)],
    "M4-overwrite-models": [('models = {} if entry.get("models") is None else entry["models"]', 'models = {}', 2)],
    "M5-verify-no-override-check": [('for model_id in context_models:\n    settings = models.get(model_id)',
                                     'for model_id in ():\n    settings = models.get(model_id)', 1)],
    "M6-verify-type-lax": [('if type(got) is not int or got != context_length:', 'if got != context_length:', 1)],
    "M7-default-path": [('containers/systemd/qwen.container}', 'containers/systemd/qwen-server.container}', 1)],
    "M8-double-resolve": [('  local lane="$1" name target source_sha target_sha verdict rc\n',
                           '  local lane="$1" name target source_sha target_sha verdict rc\n'
                           '  CONTEXT_LENGTH="$(quadlet_context_length)" || exit $?\n', 1)],
    "M9-writes-base": [('|| fail "clone incomplete $name"\n',
                        '|| fail "clone incomplete $name"\n  printf \'# touched\\n\' >> "$SOURCE/config.yaml"\n', 1)],
    "M10-url-filter-dropped": [('and str(entry.get("api") or "").strip().rstrip("/") == url]', 'and True]', 2)],
    "M11-whole-file-reemit": [('updated = "".join(lines)',
                               'updated = yaml.safe_dump(expected, sort_keys=False, allow_unicode=True)', 1)],
    "M12-no-continuation": [('text.replace("\\\\\\n", " ")', 'text', 1)],
    "M13-first-assignment-wins": [('if eq and name == "MAX_LEN":', 'if eq and name == "MAX_LEN" and value is None:', 1)],
    "M14-two-models": [('CONTEXT_MODELS=(agentfactory-build-local agentfactory-verify-local qwen-local/qwen3.8-27b-local)',
                        'CONTEXT_MODELS=(agentfactory-build-local agentfactory-verify-local)', 1)],
    "M15-ascii-to-str": [('{value[:40]!a}', '{value[:40]!s}', 1)],
}
```

## 10. Final mechanical checks (04:24Z, `date -u`)

```
report_lint: 49 refs — OK 49, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
harness-ports/bin/lane-profile.sh: 0
harness-ports/tests/test_lane_profile.sh: 0
tasks/briefs/system1/HCTX1-report.md: 0
```
Lint command: `python3 scripts/report_lint.py tasks/briefs/system1/HCTX1-report.md --min-refs 20` with `--map` for
`lane-profile.sh`, `test_lane_profile.sh`, `pc-lane.sh` (repo paths) and for the ten Hermes files, which were exported at the lane pin
b3399c1 to scratch (`git show`, and the two raw files proven by `git hash-object`). The three numbers are
`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` (the report's own count was re-run after this section was appended; see the lane's
final message). Scratch (`.../scratchpad/hctx1/`, under 1 MB at its peak) is deleted at the end of the lane; the mutant specs survive
in the appendix above.
