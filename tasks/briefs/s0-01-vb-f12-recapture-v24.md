# S0-01 — VB-F12: the COMPLETE v2.4 live recapture (the coordinator's run plan + execution log)

STATUS 2026-09-21 13:3xZ: RUNNING. Authored 2026-09-21 12:5xZ while the bridge was down (`GET /health` → HTTP 000 at
12:59Z, the 2026-09-19 banner expired); the owner pasted a fresh banner at 13:1xZ and the preflight started at once.
The PC had REBOOTED (up 1:13 at 13:14Z): the owner's production Buzz stack (`buzz-prod-*`, six containers) and my isolated
harness stack were all `Exited` — I restarted ONLY the isolated harness (§P0); the production stack is the owner's call
and is reported, not touched. The execution log is at the bottom; every count in it is pasted.

PIN: 957fb4d (HEAD = origin at authoring). The checker round 18 (A5p, 0978be3) is the DECLARED-FINAL checker (D-034); the
checker C, the tee, the probe, the backend and the launcher are FROZEN for this capture — a change to any of them is a
FINDING for the owner, never a fix. This increment changes exactly: the sandbox-side driver `run_leg.sh` (an AF-AP-105
sibling, §0), the substrate baseline (`pins.py` PINNED_BASELINE_* + the committed gz, §P4 — a measured re-pin with its
reason written into pins.py), and the test/corpus side after the capture (§4 C4).

Who runs it: the coordinator, from the sandbox, over the bridge (`proofs/S0-01/tools/pc/run_leg.sh` is the sandbox-side
driver; every PC step is one bounded bridge call). Not a lane: delegates never use the bridge.

## 0. Ancestry check (orchestration rule 0e, applied to this brief)

Identity table at the PIN (sha256[:16] · lines · last commit), pasted from `sha256sum` / `git log` on 2026-09-21:

| file | sha256[:16] | lines | last commit |
|---|---|---|---|
| proofs/S0-01/check_acp_conformance.py (C) | 7a13fbffed9fae2c | 1906 | d07c775 2026-09-15 |
| proofs/S0-01/pins.py (before this increment) | 41fa933d131ac247 | 629 | a91f256 2026-09-14 |
| proofs/S0-01/negative_contract.py | b397f6b71b674000 | 222 | 77f46a2 2026-09-08 |
| proofs/S0-01/tools/frame_tee.py (the FINAL tee) | 990a2ad24475fde3 | 567 | 01499e7 2026-09-08 |
| proofs/S0-01/tools/acp_probe.py | f42a9025ba5436c0 | 678 | 8b387d2 2026-09-15 |
| proofs/S0-01/tools/scripted_backend.py | 1968c156e3385ff3 | 894 | 77f46a2 2026-09-08 |
| proofs/S0-01/tools/build_capture_record.py | c9709755c60bfe99 | 221 | a91f256 2026-09-14 |
| proofs/S0-01/tools/pc/pc_launch.py | 1082e419b7af5847 | 429 | a91f256 2026-09-14 |
| proofs/S0-01/tools/pc/pc_post.sh | 92bf9609f54652d3 | 155 | 77f46a2 2026-09-08 |
| proofs/S0-01/tools/pc/run_leg.sh (before this increment) | b06375eeaeced8b4 | 68 | 167e063 2026-09-05 |
| proofs/S0-01/tools/pc/collect_leg.sh | 4017b53887573017 | 29 | 77f46a2 2026-09-08 |
| proofs/S0-01/spec.json | 5240f5f769c31d99 | 24 | e6f4ced 2026-09-05 |

- `run_leg.sh` (167e063, 2026-09-05) predates AF-AP-105 (registered 2026-09-19 on S0-03's runner) and carried the SAME
  shape: `setsid pc_launch.py … &` into the fixed-name framedir `$L/v2-<leg>`, then a poll for `$FD/launch.ready`, with
  only the launch LOG pre-removed. FIXED in this increment: the caller removes `$FD` on the launch step's own bridge
  call ahead of the setsid; red-first structural test `test_run_leg_removes_the_framedir_before_the_detached_launch`
  (RED on the PIN's driver, GREEN on the fix — pasted in §log). The pre-manifest wait also gained a failure branch
  (`pre manifest not done after the wait`, exit 5) — it was a success-only poll.
- The committed `proofs/S0-01/evidence/golden/` is the WITHDRAWN 2026-09-05 bundle (v1 shape: `capture.json`,
  `mention-*.json`, no `timeline.jsonl`, no `negative/`; it does carry a `run-2`). It is REPLACED wholesale by this
  capture (collect_leg.sh does `rm -rf $DST` per leg; `negative/` is new; `manifests/manifest-baseline.txt.gz` is the
  re-taken baseline of §P4).
- The real-leg corpus (the checker's declared input, both venues) is v2.2: legs cancel/negative/run-1/shutdown/two-users,
  NO run-2, no `tee-status.json`, headerless process scans — measured 2026-09-21 on the sandbox copy
  `/root/s0-01-realleg/golden` (the PC tree `/home/rocco/s0-01-pinned/realleg/golden` is its sha-verified source).

## 1. The 13 xfails this capture must clear — enumerated from T (`tests/test_s0_01_check_acp_conformance.py`) at the PIN

All thirteen fire only under `_CORPUS_VERSION == "v2.2"` (T:2753 folds `pins.corpus_version` over `_POSITIVE_LEGS`); a
v2.4 corpus takes the plain assertion path. 4 + 4 + 4 + 1 = 13 = the `432 passed, 13 xfailed` of the A5p gate
(20260919T215055Z-c44d906).

1-4. `test_real_leg_runtime_identity[run-1|cancel|shutdown|two-users]` (T:3477-3494; strict) — `corpus v2.2 predates the
   final tee: tee_sha256 mismatch`. C:397-421 compares the leg's recorded `tee_sha256` with the sha256 of the tree's
   `tools/frame_tee.py`; the final tee is 990a2ad24475fde35291cd940e5f02d5e8dcf8f413cb16e4948f46407362cdb0 (01499e7).
   Cleared by: every leg launched with the PC clone AT the PIN (run_leg.sh step 1 prints both sha16s = 990a2ad24475fde3).
5-8. `test_real_leg_process_evidence[run-1|cancel|shutdown|two-users]` (T:3551-3566; strict) — `corpus v2.2 predates scan
   v2.3: <leg> process-scan-after.txt`. Cleared by: pc_post.sh's v2.4 enumeration header (`# process-scan v2.4 mode=…
   rows=… buzz_acp_pid=… buzz_present=… owned=… owned_present=… pinned_present=… owned_zombies=… table_rows=… utc=…`)
   on both scans, parsed by `pins.corpus_version` (pins.py:395); every positive leg must read the SAME version
   (C `_captured_leg_version`: `positive-leg capture versions disagree` otherwise).
9-12. `test_ck8_real_leg_tee_status[cancel|run-1|shutdown|two-users]` (T:4816-4830; strict) — `corpus v2.2 predates tee
   status: <leg> tee-status.json`. Cleared by: the final tee's `tee-status.json` (frame_tee.py:206; the twelve
   `PINNED_TEE_STATUS_KEYS`, pins.py:179-183) in every leg; `check_tee_status` (C:1409) grades the FINAL arm on a clean
   exit and the RUNNING arm after a SIGTERM/SIGKILL.
13. `test_real_leg_negative` (T:3643-3659; non-strict) — `real v2.2 sample: <reason> (capture predates current probe)`,
   reason ∈ `_KNOWN_XFAIL_REASONS` = {`negative: probe_sha256 mismatch`, `negative: agent_interpreter_realpath mismatch`,
   `negative: spawned_at_utc is later than the first frame`} (T:3618-3622). Cleared by: a REGENERATED negative leg
   (never copied) from the final probe (f42a9025ba5436c0). EXPECTED CONSEQUENCE, by design: once `check_negative` PASSES
   on the new leg this test HARD-FAILS with `check_negative PASSES on the real negative leg — the known-stale reasons […]
   no longer reproduce; retire them (B1)` — the retirement (drop the three reasons, assert `ok`) is the test-side edit
   that lands WITH the corpus; C stays byte-identical.

## 2. What the capture must produce (the v2.4 contract)

- Legs: `pins.LEGS` = run-1, run-2, cancel, shutdown, two-users (pins.py:103) + `negative` + the unchanged
  `manifests/manifest-baseline.txt.gz`. `run-2` is REQUIRED by `check_golden` (C:1533-1552: the run-1/run-2 normalized
  timelines identical; C:1611-1633: distinct session ids, first t_utc and mention event ids).
- Per positive leg: `pins.required_files("v2.4")` (pins.py:369) — the `required` names of `PINNED_LEG_FILES` incl.
  `tee-status.json` (since v2.3); `manifest-pre/post.txt.gz` BYTE-IDENTICAL to the committed baseline body with
  digests == `PINNED_BASELINE_DIGESTS` and counts == `PINNED_BASELINE_FILE_COUNTS` (pins.py:93-100; C:978-1013,
  1048-1051); `pre_ts < spawned_at_utc < post_ts`; the mention window; the config echo `max_turn 3600s` (pins.py:49-61 —
  the 2026-09-05 capture ran 7200 s: the violation this capture fixes by construction).
- Negative: `NEGATIVE_REQUIRED_FILES` = {timeline.jsonl, runtime-identity.json, env.json, agent-stderr.txt}
  (pins.py:130), graded by `negative_contract.validate_negative_dir` (probe sha, interpreter realpath, spawn order, the
  exact JSON-RPC error). Captured ≥ 3× (VERIFY-N5g-b F7: the interpreter reading must be STABLE); the third take is
  the one collected.
- Then `golden/golden.jsonl` = the normalized run-1 timeline (`"\n".join(normalize_timeline(_load_timeline_raw(golden/
  run-1, "run-1"))) + "\n"`; C:794, C:1637, C:1546-1552) and `PINNED_GOLDEN_SHA256` set in pins.py:121-123 (the pin
  procedure written there; `None` = the checker FAILS `golden not pinned`).

## 3. Preflight — every step a bounded bridge call; STOP on any mismatch

P0. After a host reboot: the isolated harness stack (my own `s0-01-harness-postgres|redis|minio` containers + the throwaway
    `buzz-relay` on 127.0.0.1:3999, all created by the coordinator on 2026-09-04) — `podman start` the three containers,
    then the relay with the 2026-09-04 launch env (DATABASE_URL on :5471, REDIS_URL on :6471, BUZZ_BIND_ADDR 127.0.0.1:3999,
    BUZZ_HEALTH_PORT 3998, BUZZ_METRICS_PORT 3997, BUZZ_REQUIRE_AUTH_TOKEN false, BUZZ_AUTO_MIGRATE true, the key from
    `.secrets/relay.env` in-process) PLUS an explicit S3 block on the harness MinIO (`BUZZ_S3_ENDPOINT=http://127.0.0.1:9471`,
    bucket `buzz-media`, path addressing, creds from the container env) — the relay's default endpoint is `localhost:9000`
    and its start-up git object-store probe dies without an S3 backend (found 2026-09-21: "git conformance probe failed:
    s3 backend error … localhost:9000"; whatever served :9000 on 2026-09-04 is not part of the harness). Pidfile
    `.markers/s0-01-relay.pid`, exe verified by `readlink /proc/<pid>/exe`. NEVER `buzz-prod-*` (AF-AP-34).
P1. Banner → `.pc-bridge.env` (never echoed); `id -un; hostname; date -u; uptime`.
P2. No live lanes (`.lanes-live` absent here; every `.lanes/*/lane.pid` on the PC dead).
P3. PC clone at the PIN: `git pull --ff-only`; the identity table above re-hashed on the PC (tee 990a2ad24475fde3, probe
    f42a9025ba5436c0, backend 1968c156e3385ff3, pins 41fa933d131ac247 → the re-pinned pins.py after this increment lands,
    checker 7a13fbffed9fae2c). A dirty PC tree = STOP (read it; never reset it).
P4. Substrate identity BEFORE any leg: `PHASE=baseline FD=<tmp> pc_manifest.sh` (detached), its four digests + entry counts
    compared with `PINNED_BASELINE_DIGESTS` / `PINNED_BASELINE_FILE_COUNTS`. ANY difference = STOP: read the entry diff,
    decide with evidence (restore the tree, or a measured re-pin with the reason written into pins.py) — never launch a
    leg against a drifted substrate (each would fail `manifest body != baseline body` after ~10 minutes).
P5. Backend fresh: `pc_backend_restart.sh` → `/healthz` ok, sha16 1968c156e3385ff3, a NEW `upstream-records-v2-<ts>` dir.
P6. The route: one chat completion to `s0-01-pong` and one to `s0-01-slow` through OmniRoute `:20128` (key read in place).
P7. Relay + identities: the owner key lists the persisted channel (`buzz messages get`); secrets present by name only.
P8. Framedirs swept (`rm -rf $L/v2-<leg>` — now also done by run_leg.sh itself, AF-AP-105).
P9. Sandbox corpus intact (`realleg_sync.sh check`) — it is the BEFORE of the comparison; the A5p gate `432 passed,
    13 xfailed` (set 31306c49985e) is the BEFORE count.

## 4. The capture (one leg at a time, detached from the sandbox with its log read afterwards; a failed step is a FINDING)

C1. `bash proofs/S0-01/tools/pc/run_leg.sh run-1` → `run-2` → `cancel` → `shutdown` → `two-users`. Per leg: the PIN check,
    the detached launch (READY within 60 s, else `launch failed` rc 4 → read `$L/v2-<leg>.launch.log`), the pre manifest
    DONE before the first mention (exit 5 otherwise), the mention(s) `accepted=True`, `pc_post.sh` (scan v2.4, masked
    log, records, post manifest, teardown, leak guard), collect into `proofs/S0-01/evidence/golden/<leg>/`. After each
    collect: `python3 proofs/S0-01/tools/build_capture_record.py proofs/S0-01/evidence/golden/<leg> <leg>` (the v2.4
    content validation — 26 named constraints, P5c-c) and `pins.corpus_version(<leg>)` must print `v2.4`.
C2. Negative ×3: `run_leg.sh negative` three times; after takes 1 and 2 the PC framedir is copied aside
    (`$L/v2-negative.take<N>`) and `runtime-identity.json`'s `probe_sha256`, `agent_interpreter_realpath`,
    `spawned_at_utc` vs the first frame's `t_utc`, and the observed error line are compared across the takes (a
    difference is a FINDING). The third take is the collected `negative/`. `python3 proofs/S0-01/check_initialize.py
    request proofs/S0-01/evidence/golden/negative` must exit 1 with `protocol-violation: missing required initialize
    field` (the spec's negative leg).
C3. `golden.jsonl` + `PINNED_GOLDEN_SHA256` (§2); `python3 proofs/S0-01/check_acp_conformance.py proofs/S0-01/evidence` →
    exit 0 with the `PASS: S0-01 acp-conformance - N checks executed over 5 legs; golden x2 identical (…); negative:
    observed: …` line pasted. Exit 1 = `failure_reason:` = a FINDING (surface, decide, never patch C); exit 2 = deferred.
C4. The corpus as the declared input: `realleg_sync.sh` LEGS gains `run-2`; `pc-build` rebuilds the PC tree +
    `golden.pc.sha256`; `pull` brings it home sha-verified; `check`. Test-side (T only): `_EXPECTED_REAL_LEGS` /
    `_POSITIVE_LEGS` gain `run-2`; the declaration test's per-leg artifact set gains the v2.4 names; `_KNOWN_XFAIL_REASONS`
    retired per item 13 (C byte-identical throughout).
C5. Gates with FULL xfail diagnostics on both venues: `pc_suite.sh launch -n 8 -- tests/test_s0_01_check_acp_conformance.py`
    (`pytest-summary:` + `pytest-set:` pasted) and the sandbox static-copy gate on the edited files. Expected: ≥ 445 passed
    (432 + the 13) with ZERO xfails/skips in the real-leg set; EVERY remaining xfail/xpass/skip/fail listed by test id with
    its reason and disposition (fixed-by-capture / real finding / declared limit) — never a count alone (audit A5P-07).
C6. The AF-AP-36 pre-mint gate on the REAL bundle: the committed hostile-bundle regressions in T (they read
    `S0_01_REAL_LEG_DIR`); the A5o mutant driver re-run (`EXPECTED=24 KILLED=24` expected); the five 2026-09-05 owner
    mutations (zeroed manifests · unauthenticated/rejected mentions + non-OmniRoute route · foreign-session cancel without
    chunks · initialize-only shutdown · `max_turn` 1 s) applied to a SCRATCH COPY of the new bundle, each failing the
    checker with its named `failure_reason:` (the five lines pasted).
C7. Mint: `python3 scripts/proof-runner run --proof S0-01 --venue sandbox --root .` twice → `result.json` bitwise-identical;
    `validate-ledger integrity` PRESENT for all ten (AF-AP-56 — no other minted result attests a `proofs/S0-01/` path,
    checked 2026-09-21); `ledger-gen` + `git diff --exit-code proofs/ledger.json` clean once the ledger is regenerated.
C8. Commit (safe_commit, named paths, the reasoning record + pasted counts) and push (push_clean).

## 5. After the mint — the verifier BEFORE any ledger promotion (audit condition; the D-034 shape)

A VERIFY-VB-F12 brief (PIN = the mint commit): the minted closure (result.json ↔ the bundle ↔ the attested inputs), the
headline capability on the REAL bundle (buzz-acp launches the pinned hermes-acp through the tee; the six seed assertions
on RAW frames; the negative refusal live), the run-2 determinism claim, the manifests' pre == post == baseline, the three
negative takes, the C6 mutation gate reproduced. Route: the PC verify lane (`scripts/pc_lane.sh tasks/briefs/pc/pc-verify-
vb-f12.md hermes adversarial-verifier`) or the sandbox Opus 5 `adversarial-verifier` if the bridge is down. Until its
disposition the §LIVE ledger and STATUS.md read `MINTED <date>, REVIEW-PENDING (VERIFY-VB-F12 <state>)` — no
"closed/accepted" wording; the owner's `accepted/S0-01` signed tag comes after the verifier and the owner's review.

## 6. STOP conditions (surface; never route around)

Bridge death mid-leg (the leg is atomic: sweep its framedir, re-run the leg; never splice two runs) · P4 drift · `launch
failed` · a mention `accepted=False` · a checker `failure_reason:` · disagreeing negative takes · `corpus_version` ≠ v2.4 on
any leg · a dirty PC tree · any need to change C, the tee, the probe, the backend, the launcher or the spec — each a
FINDING for the owner; under D-034 a non-core finding is a `verify-followup` issue, not a round.

## 7. Budget

~8-10 min per positive leg (two 1.5 MB manifests over four trees + the turn + post) × 5 ≈ 50 min; negative ×3 ≈ 5 min;
gates ~3 min per PC run; ≈ 1.5 h of bridge time, all in bounded calls.

## Execution log (pasted; UTC)

- 13:13Z fresh banner stored; `rocco@fedora`, `up 1:13` (the PC rebooted ~13:01Z), load 0.12, GPU 252 MiB (the vLLM `qwen`
  container "Up 18 seconds" — the boot unit), ONE stale lane pidfile (dead), OmniRoute `:20128` up (401 without a key),
  the scripted backend `:20201` DOWN, the relay `:3999` DOWN, `podman ps` = `qwen` only; `buzz-prod-*` ×6 and
  `s0-01-harness-*` ×3 all `Exited`.
- P0 13:18-13:21Z: the three harness containers started (postgres ready after 1 s); the first relay launch (the 2026-09-04
  env verbatim) DIED: `git conformance probe failed: s3 backend error: reqwest: error sending request for url
  (http://localhost:9000/buzz-media/packs/…)` — the relay's default S3 endpoint; the harness MinIO is on :9471 (bucket
  `buzz-media` present since 2026-09-04 21:10Z). Relaunched with the explicit S3 block → `buzz-relay TCP listening
  127.0.0.1:3999` after 8 s, pid 53277, exe = the pinned binary, pidfile written.
- P3 13:22Z: PC clone `957fb4d`, clean but for an untracked `proofs/S0-05/evidence/`; identity table re-hashed on the PC:
  tee 990a2ad24475fde3 · probe f42a9025ba5436c0 · backend 1968c156e3385ff3 · pins 41fa933d131ac247 · checker
  7a13fbffed9fae2c (all = the PIN).
- P5 13:22Z: backend restarted (stale pidfile 2725343 reaped), pid 53658, `{"models":["s0-01-pong","s0-01-slow"],"ok":true,
  "records":0}`, sha16 1968c156e3385ff3.
- P6 13:23Z: `s0-01-pong: HTTP 200 content='pong' model='s0-01-pong' elapsed=0.6s`; `s0-01-slow: HTTP 200 content='pong'
  model='s0-01-slow' elapsed=0.3s`; backend records 2.
- P7 13:24Z: `relay serves the channel: 3 event(s) in the last 30 d; kinds [9]` (channel 73701f66…, the owner identity).
- P4 13:22-13:30Z — DRIFT FOUND: fresh baseline `hermes-agent d89ca2b9…` (11415 entries) vs pinned `6087cfef…` (11340);
  buzz/acp/venv-hermes digests EQUAL. Entry diff: 0 changed source lines; 101 ADDED (100 `__pycache__/*.cpython-313.pyc`
  under hermes_cli/, agent/lsp/, agent/secret_sources/, … + the root file `.bytecode-fingerprint` = `git:HEAD:527da608…`,
  written 2026-09-18 by a producer not in this repo); 26 REMOVED (`acp_adapter/`, `agent/`, `tools/` `__pycache__` files
  that the 2026-09-06 baseline had pinned). Restore attempt: 24 of the 26 regenerated byte-identically with the venv's
  CPython 3.13.11 from the unchanged sources (clone-time mtimes intact); `agent/context_compressor` and `tools/approval`
  did NOT (compiler output differs for those two large modules) → byte-identity with the old baseline is UNREACHABLE.
  A cleanup of the caches inside the pinned tree was refused by the sandbox's action classifier ("Modify Shared
  Resources") and NOT worked around. Decision: pin the tree AS MEASURED (the caches and the marker become pinned entries
  — a later foreign write fails loud; the S0-01 launcher never writes bytecode): baseline re-taken 13:29:46Z →
  `hermes-agent 31843deb9602d5299c417fcca7c435edcf365e8523cdeb3dfec3db2c4c068e96`, 11441 entries (11340 − 2 + 103), gz
  ff6af5130361cb15fa61b74627c328b0e93fcd303581589b86eb8a3b4039ca12 (1,538,753 bytes), fetched sha-verified, committed as
  the new `manifests/manifest-baseline.txt.gz`; pins.py PINNED_BASELINE_DIGESTS/FILE_COUNTS/GZ_SHA256 re-pinned with the
  reason; cross-checked through the checker's own `_parse_manifest_body`: `digests == pinned: True`, `counts == pinned:
  True`, `gz sha ok: True`. Owner note: the cache/marker writer of 2026-09-18 is outside this proof; a cleaner future
  baseline (caches stripped) is the owner's optional cleanup — not needed for this capture.
- Driver fix gate 13:3xZ: `bash -n rc 0`; the new test RED on the PIN's driver (`AssertionError: $PC "rm -f
  $L/v2-$LEG.launch.log; setsid …`), GREEN on the fix; `tests/test_s0_01_pc_tools.py` → `105 passed in 11.02s`.
- Increment 1 committed 6d196ef → pushed as 36dac29 (+ the transcript sync f74e12a); PC clone ff-synced to f74e12a.
- LEG run-1 13:38:23-13:39:03Z rc 0: PC tree f74e12a, tee sha16 990a2ad24475fde3 both sides; launch READY (buzz-acp pid
  199206, owned pids 3, `config echo: idle_timeout=900s max_turn=3600s session_policy=thread respond_to=owner-only`);
  pre manifest = the new baseline (all four digests); `send(owner,owner) accepted=True`; `timeline: 11 frames; seq ok:
  True | c2a: initialize, session/new, session/prompt | terminals: end_turn`; post: `scan-after: 3 lines, owned=3,
  owned_present=3`, `backend records window: 5 -> 7`, `scan-teardown: 0 lines, owned=3, owned_present=0`,
  `buzz-acp.exit: 0`, `leak guard: clean`; pre/post manifest gz sha == baseline ff6af513… (materialised). Validation:
  `build_capture_record.py` rc 0 (`run-1: 9 raw files, 11 timeline entries`), `corpus_version: v2.4`, required
  missing [], not admitted [], scan header `# process-scan v2.4 mode=after rows=3 … table_rows=341`.
- LEG run-2 13:39:33-13:40:10Z rc 0: same shape (11 frames, end_turn, records 7 -> 9, manifests == baseline, exit 0,
  leak guard clean); validation rc 0, v2.4, tee sha 990a2ad24475fde3 on both legs.
- LEG cancel 13:40:20-13:41:02Z rc 0 (route s0-01-slow): first chunk, then `!cancel` → `session/cancel`, 13 frames,
  `cancelled` terminal, records 10 -> 12, manifests == baseline, exit 0, leak guard clean; validation rc 0, v2.4.
- **LIVE FINDING 13:4xZ — the golden determinism claim is FALSIFIED on the real pinned agent (a real result, not a
  capture error).** `check_golden` (C:1533-1552) requires the run-1 and run-2 normalized timelines to be identical;
  through the checker's own `normalize_timeline` they differ at normalized line 7. Raw evidence (seq · t_utc · a2c
  `sessionUpdate`) after `session/prompt`:
  · new run-1: prompt 13:38:50.914 → `session_info_update` 51.701 → `agent_message_chunk` 52.217 → `usage_update`
    52.299 → result (end_turn) 52.300;
  · new run-2: prompt 13:39:59.104 → `agent_message_chunk` 00.027 → `usage_update` 00.107 → result 00.108 →
    `session_info_update` 00.218 (AFTER the terminal result);
  · the 2026-09-05 golden runs (git 957fb4d, both): `agent_message_chunk` → `session_info_update` → `usage_update`.
  Three samples, three positions: `session_info_update` (a session-metadata notification carrying only `updatedAt`) is
  emitted by an asynchronous path in the pinned hermes-acp and RACES the prompt's response stream; the protocol orders a
  request against its response and the turn-bound chunks, not this notification. The 2026-09-05 "golden x2 identical"
  was two matching dice rolls, not determinism. The scripted backend (deterministic content, 2 records per turn) is not
  the source — the race is agent-side. Disposition: NOT a capture defect, NOT re-rolled (a re-run until two samples
  agree would mint a hollow green). The checker as frozen will report `golden: golden mismatch between run-1 and run-2
  at normalized line 7` → the bundle is NOT mintable under the current golden definition → an OWNER DECISION on the
  golden's definition (recommended: the normalizer treats asynchronous session-metadata notifications as ORDER-FREE —
  counted, not positioned — under a checker round with a red-first test; alternatives: N-sample multiset equality, or
  a documented limit that abandons the byte-identical claim). The remaining legs proceed — they do not depend on it.
  Second failure mode from the same race: C:1608-1609 requires the golden's LAST normalized line to be the `end_turn`
  terminal — run-2's last line is the trailing `session_info_update`, so the frozen checker also reports `golden: last
  normalized line is not end_turn terminal`. Both are the one finding.
- LEG shutdown 13:42:04-13:42:44Z rc 0: owner mention → end_turn (11 frames), `!shutdown` as a thread reply →
  `buzz-acp exited rc=0` at 13:42:33Z, `scan-after: 0 lines, owned=3, owned_present=0` (the successful-shutdown
  enumeration), records 12 -> 14, manifests == baseline, leak guard clean; validation rc 0, v2.4.
- LEG two-users 13:42:55-13:43:36Z rc 0 (`respond_to=allowlist(1)`): owner then user2 mentions both `accepted=True`,
  `timeline: 20 frames; c2a: initialize, session/new, session/prompt, session/new, session/prompt` (two sessions, two
  end_turns), records 14 -> 18, manifests == baseline, leak guard clean; validation rc 0 (`20 timeline entries`), v2.4;
  `mentions/` = owner + user2 receipt/event pairs.
- NEGATIVE take 1 (13:43:52Z): the probe ran (`probe rc 0`, timeline 805 bytes) but `collect_leg.sh` DIED after the
  pack — a second driver defect: the remote pack command ended on `[ -f manifest-<p>.txt.gz.sha256 ] && echo …` for
  the last sidecar name, a leg with NO sidecars (the negative writes none) returned status 1, pc.sh propagated it,
  pipefail + set -e stopped the collect (tgz written, nothing fetched, the leg dir deleted and never re-made).
  FIXED (`if … fi`) with the executable red-first control
  `test_collect_leg_sidecar_loop_exits_zero_when_a_leg_has_no_manifest_sidecars` (RED on 77f46a2's script: `(1, '',
  '')`; GREEN on the fix; `tests/test_s0_01_pc_tools.py` → `106 passed in 4.72s`).
- NEGATIVE ×3 13:45:40-13:45:51Z, rc 0 each: identical across takes — files {agent-stderr.txt, env.json,
  runtime-identity.json, timeline.jsonl}, probe f42a9025ba5436c0, interpreter `/usr/bin/python3.13`, 2 frames, the
  observed error `-32602 Invalid params`, `spawned_at_utc` < the first frame's `t_utc` in every take (agent-stderr
  differs per take, unpinned). `check_initialize.py request golden/negative` → exit 1 `protocol-violation: missing
  required initialize field` (the spec's negative leg); `check_negative` → `observed: error code=-32602 message=Invalid
  params`. Take 3 is the collected `negative/`.
- `golden.jsonl` written from the normalized run-1 (11 lines, sha 265f6809747b8fa0); `PINNED_GOLDEN_SHA256` left
  `None` on purpose (the golden's definition is the owner's decision — pinning a coin toss is a hollow green).
- THE FROZEN CHECKER OVER THE WHOLE REAL BUNDLE (`check_acp_conformance.py proofs/S0-01/evidence`): exit 1,
  `failure_reason: golden: golden mismatch between run-1 and run-2 at normalized line 7` — i.e. EVERY check before
  `check_golden` in `EXPECTED_CHECK_SEQUENCE` passed on real v2.4 evidence: per leg (all five) timeline, initialize
  frames, runtime identity, env, mentions, route; the prompt turns (run-1, run-2, shutdown); config echo, manifests,
  process evidence, buzzacp log, tee status for all legs. The one open item is the golden's definition (§log finding).
- CORPUS 13:5xZ: `realleg_sync.sh` LEGS += run-2; `pc-build` (the PC tree from the fresh framedirs) → `pull` →
  `realleg_sync: /root/s0-01-realleg/golden == the PC tree (174 files, every sha256 equal)` → `check … intact (174
  files)`; six legs, `process-scan v2.4` headers.
- T (test-side only; C byte-identical): `_POSITIVE_LEGS`/`_EXPECTED_REAL_LEGS` += run-2, the declaration test grades
  `tee-status.json` on a ≥ v2.3 corpus. RED-FIRST for the B1 retirement, on the new corpus before the edit:
  `-k "real_leg or corpus"` → `1 failed, 64 passed` — the one failure `test_real_leg_negative`: `check_negative PASSES
  on the real negative leg — the known-stale reasons […] no longer reproduce; retire them (B1)` (the designed signal);
  the twelve former strict xfails PASS. After the retirement (`_KNOWN_XFAIL_REASONS = frozenset()`, the grade `pass`
  expected, a retired reason a real failure; the CK11 whole-reason equality test pinned on a one-element set):
  `-k "real_leg or corpus or grade_negative or known_stale"` → `67 passed, 389 deselected in 10.08s`; pyflakes rc 0.
- C6 — the five 2026-09-05 owner mutations on SCRATCH copies of the REAL bundle, graded by the frozen checker CLI
  (control = the unmutated copy):
  · control → `golden: golden mismatch between run-1 and run-2 at normalized line 7` (the one open finding)
  · zeroed manifests (pre+post gz emptied, all five legs) → `run-1: manifest body != baseline body`
  · rejected mention + foreign route (`accepted: false`, `hermes-model.txt` = openai/gpt-4o) → `run-1: mention owner
    receipt not accepted`
  · foreign-session cancel without chunks → `cancel: timeline seq not strictly 1..N at index 7`
  · initialize-only shutdown (timeline cut to 2 lines) → `shutdown: frames-client-to-agent.jsonl line count 3 !=
    timeline split count 1`
  · `max_turn` 1 s (startup-line.txt) → `run-1: startup-line.txt does not match buzzacp.log startup line`
  Each mutation is refused by the check that owns it, ahead of the golden check; no mutation reaches PASS.
- GATES launched 13:5xZ: PC `pc_suite.sh launch -n 8 -- tests/test_s0_01_check_acp_conformance.py
  tests/test_s0_01_pc_tools.py` (the working tree as a patch, the v2.4 PC corpus); sandbox full run of the same two
  files with `-rfExXs` detached (`t-full.log`).
- THE RACE PROPAGATES INTO THE META-TEST FIXTURE (found by the gates, 14:0xZ): the PC gate on that tree read
  `pytest-summary: 36 failed, 526 passed in 75.96s` (set f571c8c15c29); the sandbox's first sixty tests `10 failed,
  76 passed`. Root cause: the session fixture `_session_bundle` (T:426) builds the SYNTHETIC passing bundle from
  the committed legs' directional frames (`_load_frames(GOLDEN / leg)`) and re-interleaves them
  (`_make_interleaved_timeline`), so the synthetic run-2 inherited the real run-2's trailing `session_info_update`
  and the synthetic golden failed too — every `bundle`-fixture test expecting a PASS or a failure AFTER
  `check_golden` was masked by the mismatch (`test_passing_v2_bundle`, `test_del_negative*`, `test_del_golden_jsonl`,
  `test_ck7_f9*`, `test_ck8_running_*`, `test_neg_*`, …). Fix (test-side, the fixture's own artifice):
  `_align_async_order(run1_a2c, a2c)` places run-2's asynchronous notifications where run-1 has them — the
  synthetic positive control shares one async order; the real race stays a recorded finding. `test_real_bundle_cli`
  (the committed tree, PASS intent) is a STRICT xfail with the AF-AP-107 reason (an XPASS retires it), and the new
  `test_real_bundle_fails_only_at_the_golden_race` pins today's exact verdict (`failure_reason: golden: golden
  mismatch between run-1 and run-2 at normalized line 7`). Two `pc_tools` tests had assumed a v2.2 declared corpus
  (`…accepts_a_v2_2_corpus_leg` → `…accepts_a_real_corpus_leg`, version-aware; the real-scan predicate test skips the
  v2.3+ enumeration header). After: the ten early failures `12 passed, 444 deselected, 1 xfailed`;
  `tests/test_s0_01_pc_tools.py` `106 passed in 4.45s` / `106 passed in 5.22s` on the v2.4 corpus; pyflakes rc 0.
  The pre-fix sandbox run keeps running as the RED record; the PC gate re-launched on the fixed tree (below).
- RED RECORD (pre-fix tree, both venues agree): sandbox serial `36 failed, 526 passed in 984.66s (0:16:24)`, PC xdist
  `36 failed, 526 passed in 75.96s` (set f571c8c15c29) — 34 checker meta-tests (the `bundle`-fixture family masked by
  the synthetic golden mismatch: `test_del_negative_file`×4, `test_ck7_f9{a,b,c}_golden_*`, `test_ck8_running_*`×3,
  `test_ck8_f38_check_sequence_omission`, `test_ck9_a25_reorder_diagnostic`, `test_ck11_{fifo,dir}_at_tools_acp_probe_is_named`,
  `test_neg_*`×6, `test_stderr_*_token`×2, `test_golden_{regen,frozen_lines}`, `test_pass_line_has_negative_prefix`,
  `test_passing_v2_bundle`, `test_cli_pass_path_fails_on_golden_pin`, `test_del_{negative,golden_jsonl,neg_fixture}`,
  `test_session_new_resp_after_prompt`, `test_init_resp_after_session_new`, `test_sequence_guard_skip_one_leg`,
  `test_real_bundle_cli`) + 2 `pc_tools` tests that assumed a v2.2 declared corpus.
- GITIGNORE FINDING (14:1xZ, an AF-AP-62 sibling): `*.pid` (.gitignore:16) silently ignored the five legs'
  `buzz-acp.pid` — a REQUIRED leg file (`pins.PINNED_LEG_FILES`; `check_runtime_identity` binds `buzz_acp_pid` to it) —
  so the committed bundle would have failed `buzz-acp.pid absent` on any fresh clone while the working tree passed.
  Fixed with the negation `!proofs/*/evidence/**/buzz-acp.pid` (the pattern of the 2026-09-08 `*.log` negations);
  `git ls-files -o --ignored` over the evidence tree → 0.
- SPEC-RUNNER DEFERRAL TESTS (14:2xZ): the three `tests/test_s0_01_spec_runner.py` deferral tests read the committed
  tree's v1 shape as their fixture and went red on the real bundle (the eleven-file run `3 failed, 831 passed in
  362.49s (0:06:02)`); `_strip_v2_evidence(root)` strips a COPY into the deferred state (no leg timeline, no negative/)
  and the three tests use it → `13 passed in 3.83s`. The committed tree's real behaviour through the runner, measured
  14:27Z on a fresh copy: `proof-runner run --proof S0-01 --venue sandbox` → stderr `leg-exit-mismatch: S0-01 positive
  expected 0 got 1`, rc 1, no result.json; the negative leg cmd → `protocol-violation: missing required initialize
  field` / `observed: error code=-32602 message=Invalid params`, rc 1 — pinned by lane VB-F12-T2 (a PC Qwen build lane,
  `tasks/briefs/pc/pc-vb-f12-t2.md`; owner ruling 2026-09-21: build work goes to the local Hermes lane).
- GATES ON THE FIXED TREE: the two heavy files serial `562 passed, 1 xfailed in 988.03s (0:16:28)` (the xfail =
  `test_real_bundle_cli`, strict, AF-AP-107); GitNexus `detect_changes` through the stdio tier (`scripts/gn_mcp.py` —
  the CLI tier is MODULE_NOT_FOUND in this container): touched test functions only, `affected_processes: []`. The PC
  xdist gate on the pushed head is pasted in the ledger note.

