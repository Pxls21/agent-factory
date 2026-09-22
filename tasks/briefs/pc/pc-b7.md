# PC lane — B7 (S0-02: the leg runner selects the S0-02 pinned environment; the preflight and its test pin follow; the seven owner-free legs CAPTURED against the isolated harness; the revoked leg's owner command derived and handed over)

PIN: c439580

Role: code-implementer. Route: the LOCAL Qwen build route (`agentfactory-build-local`; the pc_lane.sh default — do NOT set
HERMES_MODEL). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Report: draft after EACH item at
`tasks/briefs/s0-02-support/B7-report.md`, return it whole as your final message. Owner authorization: this lane runs the
S0-02 capture legs against the coordinator's ISOLATED harness on this host (the throwaway `buzz-relay` on 127.0.0.1:3999,
the scripted backend on :20201, the `s0-01-harness-*` containers) — never against `buzz-prod-*` (AF-AP-34: the production
relay was restarted four times by a name-based kill on 2026-09-04; every process you stop is stopped by its OWN pidfile
after `/proc/<pid>/exe` confirms the binary — the runner already does this; do not add any other stop).

## Source (read WHOLE)
1. `proofs/S0-02/tools/pc/run_s0_02_legs.sh` (205 lines; the preflight at :45-66 greps the `PINNED_ENV_KEYS` block of
   `proofs/S0-01/pins.py` for RUST_LOG and exits 3; `launch_leg` at :69-82 calls `pc_launch.py --leg run-1 --model s0-01-pong`
   with NO `--env-set`); `proofs/S0-01/tools/pc/pc_launch.py` (`--env-set {s0-01,s0-02}` at :289, `launch_env(..., env_set)`
   at :242-271 — READ-ONLY, S0-01 is frozen); `proofs/S0-01/pins.py:63-77` (`PINNED_ENV_KEYS`, `PINNED_ENV_KEYS_S0_02 =
   PINNED_ENV_KEYS | {"RUST_LOG"}`, `PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}` — READ-ONLY).
2. The test pin `tests/test_s0_02_buzz_authz.py:1718-1731` (asserts the runner's `exit 3`, the exact `sed -n
   '/PINNED_ENV_KEYS/,/}/p'` preflight string, and that pins' block does not carry RUST_LOG — written BEFORE P5c-c landed the
   S0-02 set; it must follow the runner's new preflight, and the runner-output-closure oracle `_runner_output_writes` in the
   same file must still accept the runner's writes (it parses the runner source — do not add new write idioms).
3. The contract: `proofs/S0-02/spec.json`, `proofs/S0-02/check_buzz_authz.py` (the checker, READ-ONLY), the fixtures
   `proofs/S0-02/fixtures/*.json`, the seed's S0-02 block in `seeds/seed-stage0-v1.yaml`; the B1 brief
   `tasks/briefs/s0-02-b1-buzz-authorization-five-fixtures-checker-pc-legs.md` (the leg design) and the D-047 decision
   (ledger task #47: the revoked leg's membership removal is an OWNER-run command the coordinator hands over).

## Items
1. PREMISE (paste): on the PIN, `bash proofs/S0-02/tools/pc/run_s0_02_legs.sh /tmp/b7-probe pos-allowed` must exit 3 at the
   preflight with the BLOCKER text (no leg runs; nothing launched). Confirm the harness is up: `curl -s -o /dev/null -w
   '%{http_code}' http://127.0.0.1:3999/` = 200; `ss -ltn | grep -E ':3999|:20201'`; the three containers `Up`. If the
   harness is down, STOP and report (starting it is the coordinator's; never `podman start` anything yourself).
2. The runner selects the S0-02 set: `launch_leg` passes `--env-set s0-02`; the preflight checks the RIGHT pin — that
   `PINNED_ENV_KEYS_S0_02` carries `"RUST_LOG"` and `PINNED_ENV_VALUES_S0_02` maps it to `debug` (grep the exact lines, fail
   loud with the same BLOCKER shape if absent). No other runner change; `bash -n` clean; the closure oracle's tests stay green.
3. The test pin follows (`tests/test_s0_02_buzz_authz.py` :1718-1731 only — B6's hunks elsewhere in the file are landed and
   untouched): assert the new preflight strings and the `--env-set s0-02` selection; a red control: revert item 2 on a scratch
   copy of the runner → this test red at its own assert (paste).
4. CAPTURE the seven owner-free legs into `proofs/S0-02/evidence/` (the spec's positive-leg root; `S0_02_MEMBERSHIP` unset):
   `bash proofs/S0-02/tools/pc/run_s0_02_legs.sh /home/rocco/agent-factory/.lanes/<your lane>/tree/proofs/S0-02/evidence
   pos-allowed neg-unauthorized neg-bad-signature neg-replayed neg-stale neg-self-authored neg-not-allowlisted` — ONE leg per
   `terminal` call if a call would exceed 420 s (each leg is a fresh buzz-acp launch + a 100 s turn window). Paste the
   runner's `find` listing, every `launch never became ready` / `buzz-acp exited` / `REFUSING` line if any (each is a
   FINDING, not a retry), and confirm no unmasked 64-hex survives in any collected `buzzacp.log` (the runner's own guard).
5. Grade the capture with the frozen checker: `python3 proofs/S0-02/check_buzz_authz.py <evidence>` — paste the exit code and
   the whole output. The `revoked` leg is ABSENT by design (owner step) — state exactly what the checker says about it
   (deferred / missing leg), never work around it.
6. The owner's revoked-leg command, DERIVED not run: from the pinned relay source at `/home/rocco/s0-01-pinned/buzz`
   (READ-ONLY; NIP-29 member removal — the B1 brief cites `relay.rs` members :826-870, `membership_dropped_since`) and the
   delivery route (`deliver_event.py`, NIP-98 auth from the owner identity `owner.env` — the secret's NAME only, never its
   content), write the exact command that removes the `revoked` fixture's signer pubkey (read the pubkey from the fixture,
   paste it — a PUBLIC key) from the channel, and the exact receipt JSON the runner expects at `$S0_02_MEMBERSHIP`
   (`{"removed":true,"removed_pubkey":"<hex>","channel":"<uuid>","at_epoch_s":N,"http_status":NNN}`). Do NOT execute it.
7. Gates: `python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/<run> tests/test_s0_02_buzz_authz.py` TWICE
   (`S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz` exported; paste; ZERO failed); `bash -n` the runner; `python -m pyflakes`
   on the test file; `sha256sum` of the runner and the test file (FILE IDENTITY); `git status --porcelain` = the runner, the
   test file, `proofs/S0-02/evidence/**` (new) and your report.

## Boundary
`proofs/S0-02/tools/pc/run_s0_02_legs.sh`, `tests/test_s0_02_buzz_authz.py` (the preflight pin only), `proofs/S0-02/evidence/**`
(new, the capture), your report. `proofs/S0-01/**` is FROZEN (a needed change there is a FINDING). No relay membership
write, no `podman`/`systemctl`, no git write, no outward action. The capture delivers events to the ISOLATED relay only.

## Gate mechanics
`/home/rocco/venv-agent-factory/bin` first on PATH; `mkdir -p ../scratch/bt`; every call under Hermes's 420 s cap; CODE INTEL
FIRST (`graft skeleton` / `graft ask` before whole-file reads); `report_lint --min-refs 10`, at most THREE fix rounds.

## Report shape (DATA)
FILE IDENTITY · item 1's exit-3 line + the harness probe · the runner diff summary · the red control · the capture listing
and every runner warning · the checker's exit code + output · the derived owner command + receipt shape · the two pytest
summaries · DISCREPANCIES · NOT-done (the revoked leg; the mint — the coordinator's) · GATE RECOMMENDATION (a proposal).
