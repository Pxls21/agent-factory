Build proposal complete. Independent sandbox adversarial verification is pending; this lane does not issue a gate verdict.

ARTIFACT

/home/rocco/agent-factory/.lanes/pc-t92.md--879c6f9/tree/tasks/briefs/pc-t90-support/T92-report.md

IMPLEMENTED

- Added `harness-ports/bin/lane-profile.sh`.
  - Creates `aflane<normalized-lane-id>`.
  - Clones the read-only `agentfactory` profile.
  - Removes `fallback_providers`.
  - Adds the exact lane ID as `x-omniroute-session-id`.
  - Verifies the chain is absent, the header is exact, and `.env` hashes match.
  - Refuses non-`aflane` deletion targets.
- Updated `pc-lane.sh` to create and verify the profile before launch, pass `-p <profile>`, write `profile.txt`, and add the profile to transcript metadata.
- Updated provider-mix harvesting to query exact `session_tag` first and report `requested_model × provider × status × count`.
- Preserved legacy raw-ID visibility as `untagged-raw-rows=N`.
- Added served model and profile to harvest output.
- Added deterministic tests and registered them in `run-all.sh`.
- Updated the spawn-path section in `docs/HARNESS-PORTS.md`.

PREMISES

- Hermes v0.21.1 supports `model.default_headers` for OpenAI-compatible requests.
- OmniRoute maps `x-omniroute-session-id` directly to `call_logs.session_tag`.
- A real clone preserved `.env` exactly and included `cron/`; the source had no `hooks/` directory to copy.

LIVE PROOF

- Profile: `aflanet92live879c6f9`
- Profile verification: rc 0
- All unrelated config semantics remained equal.
- Source and clone `.env` SHA-256:

  ebe5da3161fd3f71ab3210cf73ee3692851c5848fb474d7d956eee7fde1de6a5

- Real Hermes one-shot:
  - rc 0
  - stdout: `PONG`
  - served model: `qwen-local/qwen3.8-27b-local`
- OmniRoute recorded the exact `session_tag=t92live879c6f9`.
- The tagged request had a successful status 200 row. A later status 499 `Request aborted` row appeared after `PONG`; this discrepancy is recorded in the report.
- The throwaway profile was removed and confirmed absent.

TESTS

- RED before helper existed: `0 passed, 9 failed`
- `lane profile: 9 passed, 0 failed` twice
- `pc_lane dispatcher: 39 passed, 0 failed` twice
- `test_pc_lane.sh: 60 passed, 0 failed`
- Full gate producer output: `ALL SUITES PASSED`
- `no_laya_in_gates: 33 files scanned, clean`
- Report lint: `16 refs — OK 16, MISS 0`
- All four required mutants were killed.

NOT DONE

- No commit or push.
- No server was stopped, restarted, or reconfigured.
- The owner’s interactive profile was not modified.
- No live lane profile was touched.
- Independent adversarial verification remains required before acceptance.

Retro: nothing to bake.
