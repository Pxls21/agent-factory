# T92 build report

DATA STATUS

- Build proposal complete. Independent sandbox adversarial verification is NOT done; this lane does not issue a gate verdict.
- NOT-done: no commit, push, owner profile mutation, server restart, or live-lane profile mutation.
- DISCREPANCY: real live proof produced one successful status `200` row and one later `499 Request aborted` row under the same exact tag after stdout had returned `PONG`. The required tagged success exists; the extra row is reported, not hidden.
- DISCREPANCY: the installed source profile has no `hooks/` directory. `hermes profile create --clone-from` carried `.env`, config, skills, and `cron`, but no source `hooks/` existed to copy.
- DISCREPANCY: `scripts/test_summary.sh` is pytest-only; passing shell suite paths returned `pytest-exit: 4` / “no match”. Counts below are pasted from each shell suite producer instead.
- Report lint: `report_lint: 16 refs — OK 16, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
- DISCREPANCY: the system Python has no pyflakes. The project venv’s pyflakes treats shell files and embedded Python heredocs as Python and reports shell syntax. `bash -n` is the applicable syntax gate.

## Premise checks

### 0a — Hermes request-header support: VERIFIED

Installed runtime: `Hermes Agent v0.21.1 (2026.9.7) · upstream b3399c13`.

The wrapper is `/home/rocco/.local/bin/hermes`; it execs `/home/rocco/.hermes/hermes-agent/venv/bin/hermes`. The editable package maps to `/home/rocco/.hermes/hermes-agent`.

Primary-source chain:

- `/home/rocco/.hermes/hermes-agent/agent/agent_init.py:893-916`: `_apply_openai_header_policy` applies model default headers, then custom-provider headers, to OpenAI client kwargs.
- `/home/rocco/.hermes/hermes-agent/agent/auxiliary_client.py:825-842`: `_apply_user_default_headers` reads `model.default_headers` and the `model.extra_headers` alias from config and merges string-coerced values.
- `/home/rocco/.hermes/hermes-agent/hermes_cli/config_providers.py:442-478`: `extra_headers` normalization and per-provider merge into OpenAI `default_headers`.

The implemented config form is `model.default_headers.x-omniroute-session-id`, because the installed runtime applies it to primary and auxiliary OpenAI-compatible calls.

### 0b — OmniRoute header to `call_logs.session_tag`: VERIFIED

Primary-source chain:

- `/home/rocco/.omniroute-migration-npm/node_modules/omniroute/src/sse/handlers/chat.ts:744-752`: reads `request.headers.get("x-omniroute-session-id")` and passes it as `clientSessionIdHeader`.
- `/home/rocco/.omniroute-migration-npm/node_modules/omniroute/open-sse/services/conversationTracker.ts:459-469`: the trimmed header value is used directly as `conversationId`, capped at 128 characters.
- `/home/rocco/.omniroute-migration-npm/node_modules/omniroute/src/sse/handlers/chat.ts:1200-1209`: records `sessionTag: conversationId`.
- `/home/rocco/.omniroute-migration-npm/node_modules/omniroute/src/lib/usage/callLogs.ts:547-567`: inserts `@sessionTag` into `call_logs.session_tag`.

### 0c — profile clone semantics: VERIFIED

Command:

    hermes profile create --clone-from agentfactory --no-alias t92probe

Observed clone files/directories: `config.yaml`, `.env`, `SOUL.md`, `skills/`, `cron/`, `home/`, `logs/`, `memories/`, `plans/`, `sessions/`, `skins/`, `workspace/`. The clone retained top-level `fallback_providers`.

`.env` SHA-256, source and clone:

    ebe5da3161fd3f71ab3210cf73ee3692851c5848fb474d7d956eee7fde1de6a5
    ebe5da3161fd3f71ab3210cf73ee3692851c5848fb474d7d956eee7fde1de6a5

`cron/` came along. `hooks/` did not, because neither the source nor clone had that directory. The probe was removed with typed confirmation; its path is absent.

## Implementation evidence

### Files and lines

- `harness-ports/bin/lane-profile.sh:17-23`: `profile_name` implements exact profile-name normalization.
- `harness-ports/bin/lane-profile.sh:25-67`: fail-closed verification of no chain, exact lane header, and `.env` SHA equality.
- `harness-ports/bin/lane-profile.sh:69-190`: clone/reuse, conditional `hooks`/`cron` copy, byte-preserving targeted YAML edit, semantic key-set assertion, atomic replace.
- `harness-ports/bin/lane-profile.sh:192-201`: `aflane` deletion boundary and read-back absence assertion.
- `harness-ports/bin/pc-lane.sh:429-450`: default create+verify, explicit profile override, `profile.txt`, `-p <lane-profile>`.
- `harness-ports/bin/pc-lane.sh:509-517`: `LANE_DIR/usage.json` gates export, `HDB` selects the profile-specific state DB, and the transcript footer includes `profile:`.
- `scripts/pc_lane.sh:435-441`: read served model from `usage.json` and profile from `profile.txt`.
- `scripts/pc_lane.sh:443-535`: session-tag-first SQL; raw-id `requested_model` visibility; combo-only fallback.
- `scripts/pc_lane.sh:546-568`: tagged-lane/combo-window harvest lines, `served=`, profile, and `untagged-raw-rows=N`.
- `harness-ports/tests/test_lane_profile.sh:68-150`: checks `NAME1`, `fallback_providers`, `VERIFY_OUT`, and removal controls.
- `harness-ports/tests/test_pc_lane_dispatcher.sh:384-429`: checks `SQL_CAPTURE`, `MIX_TAGGED`, `served=`, and `untagged-raw-rows`.
- `harness-ports/tests/test_pc_lane.sh:525-587`: `assert_role_route` checks generated `-p`; `profile-override` checks the explicit escape hatch.
- `harness-ports/tests/run-all.sh:21-24`: registers `test_lane_profile.sh`.
- `docs/HARNESS-PORTS.md:364-376`: the updated section names `lane-profile.sh`, `fallback_providers`, `session_tag`, and `untagged-raw-rows=N`.

Name examples produced by the implementation:

    pc-t92 -> aflanepct92
    PC_T92.R2 -> aflanepct92r2
    ABCDEFGHIJKLMNOPQRSTUVWXYZ-1234567890-abcdefghijk -> aflaneabcdefghijklmnopqrstuvwxyz1234567890abcd

### RED to GREEN

Initial test before the helper existed:

    0 passed, 9 failed

Final focused result:

    lane profile: 9 passed, 0 failed

Dispatcher final focused result:

    pc_lane dispatcher: 39 passed, 0 failed

PC lane integration final result:

    60 passed, 0 failed

## Mutants

| Mutant | Killing test | Result |
|---|---|---|
| m1: drop chain stripping | `create strips only the chain...` / chain verification | killed, rc 1; `lane profile: 2 passed, 7 failed` |
| m2: write profile name instead of lane id | exact header checks | killed, rc 1; `lane profile: 2 passed, 7 failed` |
| m3: allow arbitrary delete target | `remove refuses a profile without the aflane prefix...` | killed, rc 1; `lane profile: 8 passed, 1 failed` |
| m4: change `lane_rows` from `session_tag` to `combo_name` | raw-id SQL/session-tag checks | killed, rc 1; `pc_lane dispatcher: 37 passed, 2 failed` |

## Live proof

Live ID/profile:

    lane-id=t92live879c6f9
    profile=aflanet92live879c6f9
    verify_rc=0

Redacted semantic config diff:

    removed-top-level: ['fallback_providers']
    added-header: model.default_headers.x-omniroute-session-id = t92live879c6f9
    all-other-semantics-equal: True
    top-level-key-diff: ['fallback_providers'] []

Redacted byte diff from an additional real clone (`t92diff879c6f9`, removed after the diff):

    --- agentfactory/config.yaml
    +++ aflanet92diff879c6f9/config.yaml
    @@ -4,19 +4,8 @@
       base_url: http://127.0.0.1:20128/v1
       api_key: <redacted>
       api_mode: chat_completions
    -fallback_providers:
    -- provider: custom
    -  model: codex/gpt-5.6-sol-xhigh
    -  base_url: http://127.0.0.1:20128/v1
    -  key_env: <redacted>
    -- provider: custom
    -  model: codex/gpt-5.6-terra-ultra
    -  base_url: http://127.0.0.1:20128/v1
    -  key_env: <redacted>
    -- provider: custom
    -  model: codex/gpt-5.5-xhigh
    -  base_url: http://127.0.0.1:20128/v1
    -  key_env: <redacted>
    +  default_headers:
    +    x-omniroute-session-id: t92diff879c6f9
     agent:

Source and clone `.env` SHA-256:

    ebe5da3161fd3f71ab3210cf73ee3692851c5848fb474d7d956eee7fde1de6a5
    ebe5da3161fd3f71ab3210cf73ee3692851c5848fb474d7d956eee7fde1de6a5

One-shot command result:

    hermes -p aflanet92live879c6f9 -z 'reply with the single word PONG' -m qwen-local/qwen3.8-27b-local --usage-file <temp>
    rc=0
    stdout=PONG
    usage_model=qwen-local/qwen3.8-27b-local
    session_id=20260923_014651_d9d158

Read-only `call_logs` rows:

    session_tag     requested_model               provider                                                     status
    t92live879c6f9  qwen-local/qwen3.8-27b-local  openai-compatible-chat-98fcb302-795d-4db5-baee-2754a5723a39  200
    t92live879c6f9  qwen-local/qwen3.8-27b-local  openai-compatible-chat-98fcb302-795d-4db5-baee-2754a5723a39  499

The `499` row’s stored error was `Request aborted`; it followed the successful tagged row. The profile was then removed:

    remove_rc=0
    profile_absent_rc=0

## Gates

Focused suites, twice:

    lane profile: 9 passed, 0 failed
    lane profile: 9 passed, 0 failed
    pc_lane dispatcher: 39 passed, 0 failed
    pc_lane dispatcher: 39 passed, 0 failed

`test_lane_profile.sh` output was byte-identical. Dispatcher output includes expected random temp paths, PIDs, and current timestamps; after normalizing only those fields, substantive output was byte-identical.

Full suite:

    test_lane_profile.sh               lane profile: 9 passed, 0 failed
    test_pc_lane.sh                    60 passed, 0 failed
    test_pc_lane_dispatcher.sh         pc_lane dispatcher: 39 passed, 0 failed
    ALL SUITES PASSED

Other gates:

    bash-n-ok
    no_laya_in_gates: 33 files scanned, clean
    no_laya_rc=0

AP screen:

    --- TEST_SCREEN over 4 path(s): 3 hits over 4 files ---
    AF-AP-87: 2 at scripts/pc_lane.sh:384 (`probe=`)
    AF-AP-59: 1 at scripts/pc_lane.sh:376 (`no-pidfile fallback`)

All three are pre-existing lines outside the T92 hunks. No new T92 screen hit.

Code intelligence:

    lane_context: pack written to /tmp/t92-pack.md (112 lines)
    GitNexus detect-changes: Changes: 6 files, 5 symbols; Risk level: low

GitNexus mapped Markdown sections but not shell symbols. This is an instrument limitation, not proof that shell changes have no callers.

## Self-attack

1. The header might only affect the main OpenAI client, not real requests. Ruled out by the installed primary/auxiliary header paths and the live exact `call_logs.session_tag=t92live879c6f9` rows.
2. The config rewrite might alter unrelated source config. Ruled out by byte-preserving block edits plus parsed semantic equality after removing only `fallback_providers` and the new header; live `all-other-semantics-equal=True`.
3. Harvest might silently use combo attribution for raw IDs. Ruled out by the raw-id SQL fixture requiring `AND 0 = 1` for combo rows, the exact lane-tag predicate, the `requested_model` untagged aggregate, and mutant m4.

## Reasoning record

Rejected alternative: mutate the owner’s interactive `agentfactory` profile in place. That would alter concurrent sessions and preserve cross-lane state contention.

Ordering: clone and verify before `hermes -p`; record profile before launch; query exact `session_tag` before any combo fallback; retain untagged raw rows as a separately labelled count.

Primary sources: installed Hermes v0.21.1 header loaders and client policy; installed OmniRoute v16.3.1 request, conversation, and call-log writers; live one-shot and SQLite rows.

Retro: nothing to bake. No new general defect class was found; the one implementation bug (stale line indices after deleting the fallback YAML block) is already guarded by semantic parse-after-write and the create test.
