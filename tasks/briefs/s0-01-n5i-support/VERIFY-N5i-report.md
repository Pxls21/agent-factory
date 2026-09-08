# VERIFY-N5i — adversarial grade of S0-01 ACP probe round 12

PIN: `628da831a3dc54c874985ee05899dfc3a7e18381`.

## Scope and evidence tiers

No gate verdict is issued by this PC single-model lane. This is a handoff to the sandbox-side independent verifier. `VERIFIED` means this lane reproduced a run or hostile input; `REVIEWED` means static primary-source tracing; `NOT RUN` is a first-class gap.

## Item 0 — identity and mechanical checks

The final committed subject identity was reproduced from `628da83`:

```
3278ae2dc54eee83d384b4b86ddf6674ffaecb96bacf0d8e713a5344137ebf33  proofs/S0-01/tools/acp_probe.py  608 lines
117afaa061fae00042db3c1ab09fc9134f4d148c7c0743e769e5be7df8a82408  tests/test_s0_01_acp_probe.py  3023 lines
```

The submitted historical N5i report independently lints against the PIN: `107 refs — OK 107, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0`.

The anti-pattern screen reproduced eight production hits: three executable-identity reads, two environment reads, two hashes, and one broad M3 exception. Its test-mode run reproduced the bounded ordinal check. Classification by run is recorded below.

The supplied staged N5h report is not part of `628da83`; it is continuation input. It references prior-round bytes, so linting it against round 12 reported 66 MISS and 9 NEAR due to line movement. No subject file was modified; the inherited staged N5h report remains staged.

## Item 1 — `_open_regular`: hostile-path attack

VERIFIED: an independent standalone program against a fresh `git archive 628da83`, under `timeout 15`, exercised the evidence-write primitive. The regular control proved truncation and clearing of `O_NONBLOCK`. A final-component symlink was refused. A reader-backed FIFO reached regular-file refusal. Directory, `/dev/null`, and UNIX-domain socket inputs were refused.

```
regular_truncates_and_clears_nonblock = {"text":"after","nonblock":false,"isreg":true}
final_symlink = OSError errno=40 (ELOOP)
directory = IsADirectoryError errno=21 (EISDIR)
dev_null = OSError "not a regular file: /dev/null"
fifo_with_reader = OSError "not a regular file: .../fifo"
unix_socket = OSError errno=6 (ENXIO)
parent_symlink = write succeeded at .../outside/evidence.txt
hardlink = {"nlink":2,"same_inode":true,"foreign_text":"overwritten-through-hardlink"}
```

F1 — SOLID. A hardlink at an evidence leaf is regular, so opening it with `O_TRUNC` overwrites the foreign inode. Concrete input: `runtime-identity.json` hardlinked to an external regular file. Observed: probe rc 0, external content replaced, same inode, nlink 2. Minimal fix: open without truncation, validate regular type and a single link, then truncate through the validated fd. A post-open link-count check is too late.

F2 — SOLID provenance gap. A symlinked parent framedir redirects all evidence outside the nominal directory. Concrete input: `S0_01_FRAMEDIR=frame-link`, with `frame-link -> foreign/`; observed rc 0 and all four evidence files in `foreign/`. The normal runners create fresh framedirs before launch, narrowing this from a demonstrated normal-run escape to an arbitrary probe-input provenance gap. Minimal fix: safely owned full directory path or verified dir-fd-relative opens.

The documented hardlink limitation is real, but a one-line link-count hardening is insufficient because truncation already happens during open.

## Item 2 — receivers and AST self-scan

REVIEWED: final-source enumeration found 13 receiver calls, matching the committed scan. Ordinary evidence writes use the guarded primitive; the golden exemptions are the executable-identity reads and the primitive's own raw open.

VERIFIED scratch mutants against only the receiver-scan test:

| mutant | result |
|---|---|
| fourth `os.readlink` in `main` | KILLED: 1 failed |
| second raw `os.open` in `_open_regular` | KILLED: 1 failed |
| `io.open(..., "w")` | KILLED: 1 failed |
| `os.fdopen(os.open(...))` | KILLED through nested `os.open`: 1 failed |
| `open(..., "a")` | KILLED: 1 failed |
| `o = open; o(..., "w")` | SURVIVED: 1 passed |
| `pathlib.Path(...).write_text(...)` | SURVIVED: 1 passed |
| delete `_write_env(framedir)` from `_write_evidence` | SURVIVED: 1 passed |

F3 — SOLID. The AST classifier covers literal calls and selected attributes, but not alias-open or `Path.write_text`; its count floor accepts removal of one guarded writer from the current receiver set. Minimal fix: alias/write-method analysis plus an exact keyed receiver inventory rather than an at-least floor.

## Item 3 — cached import-time hash and checker identity

VERIFIED: the probe resolves its own real path and hashes a regular source file at import, before `main` launches the agent. Normal evidence and the M3 handler consume that cached identity; no later source path rereads the probe. The fresh three-file PC suite exercised the committed mid-run source-swap tests.

The checker asks a later question: it hashes current `tools/acp_probe.py`, requires a regular file, and rejects mismatch. Direct PC re-run of the real-negative test reproduced:

```
XFAIL tests/test_s0_01_check_acp_conformance.py::test_real_leg_negative
  real v2.2 sample: negative: negative: probe_sha256 mismatch (capture predates current probe)
1 xfailed in 0.37s
```

This confirms the stale-corpus mechanism. The probe records loaded-at-launch bytes; the checker compares check-time on-disk bytes. A post-launch swap fails closed, but a report must name the two different moments.

REVIEWED boundary: a pre-launch controller can make source and a previously validated timestamp-based `.pyc` disagree. The PC runners disable new bytecode writes but do not establish absence of a matching old cache. No stale-PYC rig was run.

## Item 4 — stderr drain lifecycle

VERIFIED synthetic behavior: after waiting for the agent, the probe joins the stderr thread for three seconds, names an unfinished drain as an error, and folds it into `probe_error`. A scratch nine-second-join mutant failed the focused grandchild-holder test in 5.43 seconds: expected rc 1, observed rc 0.

VERIFIED class-16 window: a wrapper made the drain set `sentinel-real-drain-error` then sleep beyond join. Final source returned rc 1 with exactly `stderr drain failed: sentinel-real-drain-error`. A scratch mutant removing the existing-error guard returned rc 1 but overwrote that specific error with the generic unfinished-drain message. The guard is reachable and preserves the specific cause.

REVIEWED pinned-source evidence only: ACP routes logs and incidental agent text to stderr. The pinned Hermes tree has subprocess paths that pipe stderr and start new sessions; such children may outlive a parent's process group. The adapter sweep did not establish a subprocess from this exact negative flow. The pinned ACP repository is protocol/schema source, not a buzz-acp executable implementation.

F4 — UNSURE calibration blocker. The three-second policy is synthetically tested, but venue rules prohibit a real pinned `hermes-acp` or buzz-acp capture. Coordinator-owned final-byte recapture is required to calibrate the live policy.

## Item 5 — append ordering and retry oracle

VERIFIED APPEND-ORDER: prepending rather than appending the drain failure made the appended-failure test fail because the expected first-error-first string differed from the observed reverse.

VERIFIED M23 on its required selector. A scratch extra child executable-identity read before retry failed the recovery selector:

```
RL_CALLS=6
FIRST_OK=4
SITES=[324, 324, 324, 324, 325, 398]
```

The committed test uses caller-observed distribution, not a literal typed source-line list. It requires the first four reads from one retry site and the final sample from another, so ordinary source-line drift does not itself red it.

## Item 6 — lossy producer and consumer reachability

VERIFIED source trace: the negative probe represents a lossy line with null frame, raw text, and base64 raw bytes. The negative contract permits the base64 field but fails closed on a non-dictionary agent frame. The checker invokes that contract only from the negative-leg consumer.

The positive timeline consumer rejects a null frame. The tee independently creates a base64 raw record for a lossy line. Thus a positive tee timeline can reach rejection; neither consumer silently accepts mangled frames. The predecessor's claimed path from negative-probe producer to positive timeline consumer is wrong. A5k/VERIFY-CK13 must prove the tee-positive consumer's exact lossy failure.

## Item 7 — targeted mutation campaign

Fresh scratch-copy mutations reproduced by this lane:

| mutant | focused oracle | result |
|---|---|---|
| M23 extra early child readlink | early-retry selector | KILLED, 1 failed, 99 deselected |
| APPEND-ORDER | appended-failure test | KILLED, 1 failed |
| DRAIN-BOUND-9S | never-finishing-drain test | KILLED, 1 failed in 5.43s; rc became 0 |
| remove `O_NOFOLLOW` | symlink/FIFO test | KILLED; symlink case failed, FIFO control passed |
| fstat after close | symlink/FIFO test | KILLED; FIFO case EBADF |
| remove class-16 guard | standalone injected-error/sleep rig | specific drain error overwritten |
| alias `open`, `Path.write_text`, writer deletion | AST scan test | SURVIVED; F3 |
| M3 `probe_sha256 = None` | through-M3 swap test | KILLED: expected loaded SHA, observed `None` |

The M3 hash mutant first survived an unrelated bytecode assertion; the correctly targeted through-M3 swap case killed it. That reversal is retained rather than hidden.

F5 — SOLID verification gap. This lane did not independently reproduce the submitted 33-mutant campaign or the brief's required at-least-40 campaign. The focused results do not substitute for it.

## Item 8 — class re-scan and stale-context sweep

The required 18-class run-based re-scan is incomplete. Confirmed by run: drain-error preservation, hardlink limit, final symlink refusal, nonregular FIFO refusal, drain-time bound, append order, and cached import-time hash. Reviewed: executable-identity reads, environment reads, hashes, broad M3 exception, and bounded ordinal. M23 confirms the ordinal's site-distribution check prevents a total-only hollow green.

The source comment that the primitive can never block or write unsafely overstates its boundary without parent-path provenance and hardlink qualification. The runner/probe split must be explicit.

## Item 9 — PC gate

VERIFIED fresh PC run with `S0_01_VENUE=pc`, `S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`, and explicit `--basetemp`:

```
tests/test_s0_01_acp_probe.py tests/test_s0_01_negative_contract.py tests/test_s0_01_check_initialize.py
208 passed in 59.41s (0:00:59)
```

A four-file PC gate was initially interrupted by the harness, so it was NOT a pass at that point. It was re-run fresh to completion with `S0_01_VENUE=pc`, `S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`, and explicit `--basetemp`:

```
tests/test_s0_01_acp_probe.py tests/test_s0_01_negative_contract.py tests/test_s0_01_check_initialize.py tests/test_s0_01_check_acp_conformance.py
568 passed, 9 xfailed in 157.22s (0:02:37)
pytest_rc=0
```

This independently reproduces the coordinator's final test count. The direct real-negative xfail above was also reproduced.

## Items 10–11 — discipline and design

`py_compile proofs/S0-01/tools/acp_probe.py tests/test_s0_01_acp_probe.py` returned rc 0; `git diff --check` was clean. Final report lint was run last against the PIN and returned `report_lint: 5 refs — OK 5, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (at 628da83)`. No subject source was modified, committed, reset, restored, or staged by this lane. Mutation and hostile-path artifacts stayed in `../scratch`. No real agent, Hermes, buzz-acp, runner, relay, production service, or credential was touched; no process started by this lane remained after probes ended.

The correct boundary is two layers: runner owns trusted framedir provenance and rejects symlink components; probe refuses nonregular final entries. The primitive must defer truncation until after regular-file and single-link validation. The normal runner's fresh-directory sequence does not make arbitrary probe input safe.

A clearer identity design uses a loaded-code digest and a checker-time file digest. Current `probe_sha256` intentionally compares moments, turning a swap into a fail-closed mismatch, but hides that temporal distinction from consumers.

## Findings and handoff

1. F1, SOLID — `proofs/S0-01/tools/acp_probe.py:73-78`: `os.open` uses `O_TRUNC` before link validation, so a hardlink clobbers another inode. Fix open/validate/truncate ordering plus single-link validation.
2. F2, SOLID — `proofs/S0-01/tools/acp_probe.py:253-258`: `os.makedirs` accepts an externally supplied framedir whose parent can be a symlink. Fix runner provenance or verified dir-fd-relative opens.
3. F3, SOLID — `tests/test_s0_01_acp_probe.py:2873-2895` classifies literal `open` calls but misses alias/open coverage. The receiver-count floor at `tests/test_s0_01_acp_probe.py:2955-2960` uses `len(examined) >= 12` and accepts writer deletion. Fix scan coverage and exact inventory.
4. F4, UNSURE — `proofs/S0-01/tools/acp_probe.py:513-521`: `stderr_thread.join(timeout=3)` has no real-negative-leg calibration. Require final-byte coordinator recapture.
5. F5, SOLID verification gap: required at-least-40 mutation campaign was not independently reproduced.

The earlier F6 whole-checker verification gap is closed by the fresh four-file PC run: `568 passed, 9 xfailed in 157.22s`, rc 0.

This report is not a gate determination. It hands independently reproduced defects and missing verification evidence to the sandbox adversarial-verifier lane.
