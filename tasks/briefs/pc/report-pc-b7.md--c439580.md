PIN: c4395803c43963dd80f2b4e9db9411ad973b6eab
ROLE: code-implementer
STATUS: PROPOSAL — sandbox adversarial verification still required.

FILE IDENTITY

- `runner:52-65` now validates the actual S0-02 pins through `PINNED_ENV_KEYS_S0_02`: `PINNED_ENV_KEYS_S0_02` contains `RUST_LOG`, and `PINNED_ENV_VALUES_S0_02` maps it to `debug`.
- `runner:70-74` explicitly launches through `launch_leg` with `--env-set s0-02`.
- `test:807-816` recognizes the shipped partial-capture state in `test_real_evidence_root_is_not_a_passing_bundle_today` as a deterministic failure, not the old all-absent deferral.
- `test:1725-1742` pins `test_pc_runner_preflights_and_selects_the_s0_02_env_set` to the new preflight and launcher selection.
- Final SHA-256:
  - `c092e8797ee7c42b06e578a2887b3905555fff65472c913effd039e4ff7123cb  proofs/S0-02/tools/pc/run_s0_02_legs.sh`
  - `4444842b886ac7debf3bccceaba8cb55eae83e577ebbfb491bc0b3f147426dc6  tests/test_s0_02_buzz_authz.py`

ITEM 1 — PREMISE AND HARNESS

VERIFIED
- Lane HEAD: c4395803c43963dd80f2b4e9db9411ad973b6eab; initial `git status --porcelain` was empty.
- `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3999/` returned `200`.
- `ss -ltn` showed listeners on 127.0.0.1:3999 and 127.0.0.1:20201.
- `podman ps` showed `s0-01-harness-postgres`, `s0-01-harness-redis`, and `s0-01-harness-minio` each `Up 14 hours`.

DISCREPANCY
- The stated exit-3 premise did not reproduce. `bash proofs/S0-02/tools/pc/run_s0_02_legs.sh /tmp/b7-probe pos-allowed` passed the stale preflight, launched the leg, delivered the positive event (`http=200 accepted=True`), then exited 1 after `[: 0\n0: integer expression expected` and `cp: cannot stat .../buzzacp.log`. There was no BLOCKER/exit-3 line to paste.
- Cause verified from the PIN bytes: `proofs/S0-01/pins.py:76` already defines `PINNED_ENV_KEYS_S0_02` with `RUST_LOG`; the old runner range began at the first `PINNED_ENV_KEYS` and ended at the later one-line S0-02 set, so it falsely succeeded.
- Cleanup: the probe-owned PID was checked through `/proc/<pid>/exe` as the pinned `buzz-acp`, sent SIGTERM by PID, and confirmed gone. No production process was touched.

ITEMS 2-3 — RUNNER SELECTION, PREFLIGHT, TEST PIN, RED CONTROL

VERIFIED
- The runner now checks both exact S0-02 pin definitions before creating the evidence root (`runner:52-68`, `PINNED_ENV_VALUES_S0_02`). A scratch mutation from `debug` to `info` produced the exact BLOCKER text, exit 3, and `EVIDENCE_DIR_CREATED=no`.
- `launch_leg` now passes `--env-set s0-02` (`runner:72-74`).
- The test pins both preflight strings and the launch selection (`test:1725-1742`, `PINNED_ENV_KEYS_S0_02`).
- Scratch red control: removing only `--env-set s0-02` made `test_pc_runner_preflights_and_selects_the_s0_02_env_set` fail at `assert '--env-set s0-02' in launch`; `RED_CONTROL_EXIT=1`.
- `bash -n` is clean. The runner-output-closure test stays green.

ITEM 4 — LIVE CAPTURE

CAPTURED
- `pos-allowed`: exit 0, `http=200 accepted=True`.
- `neg-bad-signature`: exit 0, relay receipt `http=400 accepted=False`, `invalid schnorr signature`.
- `neg-replayed`: exit 0, first and second HTTP submissions both returned accepted receipts, but this captured bundle is INVALID: both sub-leg timelines contain one prompt and the expected buzz-acp duplicate-drop line is absent.
- `neg-stale`: exit 0, relay receipt `http=400 accepted=False`, `event timestamp too far from server time`.
- `neg-self-authored`: exit 0, `http=200 accepted=True`, zero prompts.
- `neg-not-allowlisted`: exit 0, `http=200 accepted=True`, zero prompts.

BLOCKED / NOT CAPTURED
- `neg-unauthorized` could not run because `/home/rocco/s0-01-pinned/.secrets/nonmember.env` is absent. This is a blocker: the fixture requires an independent non-member signer, and I am NOT going to fake or derive a substitute key. The runner currently exits 1 with the shell's missing-file line after launching; I stopped the owned process by verified PID.
- No `launch never became ready`, `buzz-acp exited`, or `REFUSING` line appeared in the six completed capture logs.
- The final capture tree has 42 files: six plain files for each of `pos-allowed`, `neg-bad-signature`, `neg-stale`, `neg-self-authored`, and `neg-not-allowlisted`; and six files in each `neg-replayed/{first,second}` sub-leg. `neg-unauthorized` and `revoked` are absent.
- `grep -REn '[0-9a-fA-F]{64}' --include='buzzacp.log' proofs/S0-02/evidence` found no match: `UNMASKED_64HEX=NONE`.

ITEM 5 — FROZEN CHECKER

- Command: `python3 proofs/S0-02/check_buzz_authz.py proofs/S0-02/evidence`
- Exit: 1
- Whole output: `failure_reason: neg-unauthorized: neg-unauthorized leg directory absent`
- The checker stops at the first missing leg. It does not yet print a `revoked` line. The revoked leg is also absent and remains deferred to the owner step; no receipt was fabricated.

ITEM 6 — DERIVED OWNER COMMAND; NOT EXECUTED

Public fixture values:
- signer pubkey: `2267fe91571e5c9166ddf1a80176e988bdd00b9023edcc33375e1be85928000c`
- channel: `73701f66-6e12-42ff-b561-7d36db1ad91b`

Primary-source shape: `sdk:593-602` uses `build_remove_member` to build kind 9001 with `h=<channel>` and `p=<target pubkey>`; `cli:1394-1408` uses `cmd_remove_channel_member` to sign and submit it through the real client; `side:1437-1467` applies `handle_remove_user`. The owner key file's NAME is `owner.env`; its content was never printed.

Exact owner command:

`set -a; . /home/rocco/s0-01-pinned/.secrets/owner.env; set +a; BUZZ_RELAY_URL=http://127.0.0.1:3999 /home/rocco/s0-01-pinned/buzz/target/release/buzz channels remove-member --channel 73701f66-6e12-42ff-b561-7d36db1ad91b --pubkey 2267fe91571e5c9166ddf1a80176e988bdd00b9023edcc33375e1be85928000c`

Expected success output is a normalized JSON write receipt with `event_id`, `accepted`, and `message`. The runner's required receipt file is:

`{"removed":true,"removed_pubkey":"2267fe91571e5c9166ddf1a80176e988bdd00b9023edcc33375e1be85928000c","channel":"73701f66-6e12-42ff-b561-7d36db1ad91b","at_epoch_s":N,"http_status":NNN}`

Do not run the mutation without a restoration plan. A live read showed this target is the channel's only owner. The pinned relay's side-effect path explicitly guards `last-owner orphaning` (`side:1447-1457`) and returns `cannot remove the last owner`. Therefore this derived command is expected to be refused unless ownership is transferred first or a different authorized signer removes it. I did not execute it.

ITEM 7 — GATES

- Authoritative `scripts/test_summary.sh` run 1 with the declared PC corpus: `pytest-summary: 151 passed in 39.69s`.
- Authoritative `scripts/test_summary.sh` run 2 with the declared PC corpus: `pytest-summary: 151 passed in 39.85s`.
- Required `python -m pytest -n 4` run 1: `150 passed, 1 skipped in 11.14s`.
- Required `python -m pytest -n 4` run 2: `150 passed, 1 skipped in 13.13s`.
- `python -m pyflakes tests/test_s0_02_buzz_authz.py`: exit 0.
- `bash -n proofs/S0-02/tools/pc/run_s0_02_legs.sh`: exit 0.
- `git diff --check`: exit 0.
- AP screen: runner 0 hits. Test screen: 11 pre-existing enforcement/meta-test hits, AF-AP-80 ×7 and AF-AP-34 ×4; none introduced by the two changed test regions.
- GitNexus `detect-changes`: low risk, two files, one symbol; its clone index did not map the shell function and is stale/partial for this detached tree.

DISCREPANCIES

1. The brief's item-1 exit-3 premise was stale; the S0-02 pin set already existed at the PIN.
2. The live runner has independent pre-existing execution defects outside item 2: `grep -c ... || echo 0` can produce `0\n0`, it attempts to copy `buzzacp.log` before the S0-01 post step creates it, and stale `buzz-acp.exit` / `launch.ready` files can affect a later leg. I diagnosed these while exercising the real runner. They are NOT fixed in this proposal because the brief ordered no other runner change. Their effects were bypassed only in the temporary diagnostic edit and then reverted before the final diff.
3. The negative-unauthorized key is absent from the host key store. Six legs were captured; the required seventh is blocked on real external input. I did not create a fake key.
4. The replay capture is invalid: the relay's persistent-event dedup returns `accepted=true, message='duplicate:'` before fan-out, so the second HTTP submission never reaches buzz-acp's `seen_ids` guard. The second sub-leg therefore copied the first timeline and lacks the expected duplicate-drop observable. No checker or fixture was weakened.
5. The requested owner command cannot presently remove the revoked fixture's signer: it is the only owner, and the pinned relay refuses last-owner self-removal. A real prerequisite is ownership transfer or an authorized distinct remover.
6. The checker output names the earlier missing `neg-unauthorized` leg and does not reach the later missing `revoked` leg.
7. Gate tooling discrepancy: `scripts/test_summary.sh` defaulted to the sandbox corpus `/root/s0-01-realleg/golden` on this PC and failed with PermissionError. Re-running it with the brief's declared PC pair (`S0_01_VENUE=pc`, `S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`) passed 151 tests twice.
8. Code-intel discrepancy: the first `lane_context.sh` invocation treated a symbol name as a file and exited 64; the corrected pack was written. GitNexus `detect-changes` reads the clone index rather than this lane worktree. Graft reported about 82,362 tokens saved across its two quantified calls.
9. Boundary deviation: `test:807-816` also had to change because the new evidence root is partial and deterministically fails with rc 1; leaving the old "real root defers" assertion would make the final tree falsely expect rc 2. The replacement still forbids `PASS:` and accepts only failure (1) or absent-root deferral (2). No B6 behavior hunk was changed.

NOT DONE

- `neg-unauthorized` live capture: blocked on absent `nonmember.env`.
- A checker-accepted seven-leg capture: not produced. Five ordinary legs are valid-looking; replay is invalid; negative-unauthorized is absent.
- Revoked leg and owner receipt: not run.
- Key rotation: synthetic-only per task #47; not run.
- Mint: coordinator-owned and not attempted.
- No commit, push, service restart, podman mutation, membership write, or outward action occurred.

SELF-ATTACK

1. Wrong environment could still launch: ruled out for the proposed diff by exact source assertions, the scratch red control, and the live `env.json` observed during diagnostics naming `env_set: s0-02` with `RUST_LOG: debug`.
2. Partial evidence could be mistaken for proof: ruled out by the frozen checker exit 1 and the changed real-evidence test, which requires partial=1 or absent=2 and forbids `PASS:`.
3. Captured logs could leak key material: ruled out over all collected `buzzacp.log` files by the case-insensitive 64-hex sweep; no raw log was copied into evidence.

GATE RECOMMENDATION

NOT-READY. The proposed item-2/3 code is tested, but the live proof is blocked by the missing non-member key, the replay path cannot reach the claimed buzz-acp dedup mechanism through the relay's HTTP ingest dedup, and the revoked target is the only channel owner. This report is a build-lane proposal until the sandbox adversarial verifier grades it.

REPORT LINT

`report_lint: 13 refs — OK 13, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`

RETRO

Real defects found: stale preflight premise; duplicated grep-count output; collect-before-mask ordering; stale launch-marker reuse; missing non-member key; relay dedup prevents the claimed buzz-acp replay path; revoked signer is the only owner. These are named here for coordinator `/bug-echo` and incident-registry handling. No shared skill was modified from this lane.
