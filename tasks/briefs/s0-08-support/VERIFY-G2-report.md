# VERIFY-G2 — adversarial grade of S0-08 gVisor containment round 2

PIN `887f021` · PC uid 1000 · 2026-09-08

**VERDICT: NOT-READY.** Blocking set: Findings **3, 4, 10 and 11**. A forged dangerous `run_argv` passes; observer uid is typed rather than read back; a dirty pinned checkout is accepted; and an arbitrary image/digest passes when the typed commit stays pinned. The deterministic suites are green on the shipped bytes, but the independent mutation campaign found a **7/42 = 16.7% hollow-green rate**. This verdict does not depend on the skipped Podman/container run: all four blockers were reproduced with checker bundles, source mutants, and the real preflight. Findings whose exact live image behavior remains UNSURE are marked below.

## FILE IDENTITY of graded bytes

| sha256 prefix | lines | file |
|---|---:|---|
| `bb38dddfb8825323` | 447 | `proofs/S0-08/CONTAINMENT-SPEC.md` |
| `74fc0adb1e051943` | 451 | `proofs/S0-08/check_containment.py` |
| `925b0f1706c96c4c` | 47 | `proofs/S0-08/spec.json` |
| `92c9234431f2c7be` | 332 | `proofs/S0-08/tools/pc/run_containment.sh` |
| `d9b884bf7a6c1a22` | 27 | `proofs/S0-08/canaries/P1.sh` |
| `18ef162a8ec8dba4` | 62 | `proofs/S0-08/canaries/P2.sh` |
| `25254023cf240afe` | 58 | `proofs/S0-08/canaries/P4.sh` |
| `f7ed0995f0788d11` | 8 | `proofs/S0-08/fixtures/evidence-crun/canaries.jsonl` |
| `6ac4efedaea8a395` | 44 | `proofs/S0-08/fixtures/evidence-crun/runtime-identity.json` |
| `fdf65099c866d3c6` | 94 | `proofs/S0-08/fixtures/evidence-crun/PROVENANCE.md` |
| `c66b39ccf70399c2` | 1602 | `tests/test_s0_08_containment.py` |
| `275417c9105c5697` | 350 | `tasks/briefs/s0-08-support/G1-report.md` |

Every row matched `git archive 887f021` and the builder report exactly.

## Item 0 — mechanical gates and file identity

Reproduced against the PIN. `report_lint` returned rc 0 with `MISS 0` (81 OK, 7 UNRESOLVED only for explicit read-only hermes-agent paths absent from the repo map). Shell syntax passed: `bash -n` runner and `sh -n` all eight canaries. `ap_screen` found 0 production hits; its eight test hits are two explanatory comments, five assertions that ban `pkill`/`killall`, one assertion preserving that explanatory comment, and one `Popen.kill()` comment. No call or broad process termination appears.

All 12 rows in G2’s FILE IDENTITY table match the archive bytes exactly: SHA-256 prefixes and line counts are correct. The report’s static evidence maps correctly to the pin; remaining upstream claims are re-derived separately below.

## Item 1 — D1 (`s6-svscan`) and live runsc capability cells

Reproduced more strongly than the lane. The public s6-overlay v3.2.3.0 noarch tarball was already fetched successfully by the stopped attempt; sha256 is exactly `b720f9d9340efc8bb07528b9743813c836e4b02f8693d90241f047998b4c53cf`, matching the pinned upstream Dockerfile, line 109. Its `/init` ends by execing `s6-overlay-suexec …/libexec/stage0`; `stage0` generates then execs `/run/s6/basedir/bin/init`. I also fetched/inspected the pinned x86_64 tarball and ran its real `s6-linux-init-maker`: generated `bin/init` execs `s6-linux-init`, and that pinned static binary contains the direct path `/package/admin/s6/command/s6-svscan`. Together with the pinned upstream Dockerfile’s line 68 (“PID 1 = s6-svscan”), the literal `s6-svscan` is SOLID, not merely inferred. It fits `/proc/1/comm` without truncation.

The three hostile bundles all fail closed: PID 1 uid `1000` → `P2 pid 1 uid 1000, expected 0`; `own_pid1_comm="s6-svscan "` → exact-literal refusal; P2 `systemd` vs P6 `s6-svscan` → the agreement refusal.

I ran `/usr/local/bin/runsc --rootless do` with the host root mounted read-only and P6 via an inner privilege drop. The outer PC user remains uid 1000; inside the runsc cell the `setpriv --reuid=1000` subject reported gVisor `4.19.0-gvisor`, PID 1 `sh`, P6 `mount_proc_rc=32` with “must be superuser”, `own_pid_count=4`, and canary rc 0. The inner uid-65534 cell also ran and gave the same capability result. A full-capability inner-root control gave mount rc 0 and matching mounted/own PID 1 `sh`. No root host action occurred.

## Item 2 — `CONTAINER_MAX_PIDS`

The source derivation starts from two declared s6-rc services (`main-hermes`, `dashboard`) plus the s6 supervision/init processes, the main program and transient canary processes. The lane’s ≈12 estimate is plausible for a blank data volume. But `/home/rocco/s0-01-pinned/hermes-agent/docker/cont-init.d/02-reconcile-profiles` walks persistent `$HERMES_HOME/profiles/` and can recreate dynamic gateway service slots before the main program starts. The runner neither mounts a fresh empty `/opt/data` nor suppresses this reconciliation, so `CONTAINER_MAX_PIDS = 32` is not a source-derived upper bound for every configuration of the image; it is an asserted operational ceiling. This is Finding 1.

Boundary attacks: `32` passes (inclusive); `0` also passes; `-1`, `32 ` and `1e1` fail as non-counts. Zero is not a valid process-table observation because PID 1 and the canary itself exist. That missing positivity floor is Finding 2.

## Item 3 — `run_argv` screen

Reproduced the required adjacent-pair checks and every briefed form. `--network=none` alone fails because the required `--network none` pair is absent; appended beside the required pair it passes. `--network none --network host` fails. The following forged argv pass: `--privileged=true`, `--cap-add=SYS_ADMIN`, `--volume=/host:/host`, `--mount=type=bind,src=/,dst=/host`, two-token `--pid host`, and appended `--network=none`. Exact `--pid=host` fails. A string instead of a list fails. Duplicating all required pairs passes.

The shipped runner itself emits only the array forms at `proofs/S0-08/tools/pc/run_containment.sh:165-178`: exact two-token `--runtime[-flag]`, `--security-opt label=disable`, and `--network none`. The alternates require a forged bundle, but `runtime-identity.json` is untrusted evidence, and the spec claims the screen bans privileged/bind/host-namespace/cap-add forms. This is Finding 3.

## Item 4 — exec identity and runtime environment

`canary_exec_user` is a typed echo: `CANARY_EXEC_UID=10000` is written to metadata, not read back by `id -u` in the exec. Therefore a runner regression that executes canaries as root while retaining the constant is invisible to the checker. `"10000 "`, `"1e4"`, and absence fail, but JSON integer `10000` passes because `check_identity` coerces it with `str()`. Findings 4 and 5.

The pinned `docker/hermes-exec-shim.sh` does short-circuit directly to the real binary for non-root, so P3’s Hermes invocation remains reachable under `--user 10000`. P4’s `env` observes the exec process environment, which Podman initializes from the container config plus explicit exec overrides. It is close to the main program environment after `/init`’s `with-contenv`; however the main wrapper explicitly resets `HOME=/opt/data`, while P4 does not, and dynamic/runtime mutations after startup are not proven equal. The claim “IS the env the main program inherits” is too strong; this is residual Finding 6.

## Item 5 — P2 every-holder collection

The live test starts two same-uid processes, proves P2 reports both PIDs, then splices that live line into a passing bundle and proves the checker emits the exact 2-process ambiguity reason. It does not include a single-holder positive control, and it cannot produce uid 10000 as PC uid 1000 without a container. Synthetic bundle attacks fail closed: `1,2` vs one uid is refused as ambiguity first; no holder gets the named not-found reason; one pid vs two uids is a disagreement; one pid with unreadable/empty uid becomes `1 pid(s), 0 uid(s)` because `_csv` drops empty entries. No new blocker beyond the missing explicit single-holder control; recorded as Finding 7.

## Item 6 — `exec_rc`

The capture is sound for process status: `set +e`; command substitution around `podman exec`; immediate `exec_rc=$?`; then `set -e`. The last-line extraction happens later. A canary that prints a valid line and exits nonzero aborts the whole evidence run with exit 4 and a named stderr reason; no bundle line is written. That is the intended fail-closed producer behavior. The checker’s per-record `rc` is the canary-authored observation status, not Podman exec status; the two are deliberately different.

## Item 7 — crun fixture guard

On this PC, the fixture producer test passed and exercised the different-host else arm: the committed sandbox kernel is `6.18.44-fc-v24`, while this host is `6.17.11-200.fc42`. A scratch test with a forged live `uname_r` also passed, confirming the host-dependent comparisons become unreachable while only `assert live uname_r` remains. That is a skip in disguise for four producer values on every non-capture venue, contrary to the report’s claim that both arms assert the binding; Finding 8. The fixture’s identity remains explicitly labelled DELIBERATELY TYPED in the provenance section “Why runtime-identity.json is typed” and in the identity file’s `runtime_argv_note`.

## Item 8 — proof-runner ordering

The real three-run test passed in the fresh 122-test baseline. Source confirms the first exit-2 leg raises Deferred immediately; a broken first negative fixture therefore yields exact stderr `negative-control-unmet: S0-08`, while moving the positive leg first hides it behind capability deferral. The validator’s recorded-run/spec comparison (lines 275-305) does care about order: it zips recorded runs to spec legs and requires same count/order/type/cmd/exit plus each negative reason. So the reorder affects no recorded result today because deferral mints none, but would require a newly minted result to follow the new order.

## Items 11 and 15 — PC and venue gates

Fresh direct PC run with all required venue exports: `122 passed in 16.44s`, uid 1000, `kernel.dmesg_restrict=1`; `${PIPESTATUS[0]}=0`. Resume verification re-ran the same file with explicit PC exports and `--basetemp`: `122 passed in 13.06s`, `${PIPESTATUS[0]}=0`. This reproduces the amended venue arm. Host-root and whole-suite uid-65534 runs are NOT run: this PC lane has no host root and cannot `setpriv` from uid 1000 to uid 65534. The stopped attempt’s mislabeled `uid65534-full.log` is actually another uid-1000 pass; its real setpriv logs say `setresuid failed: Operation not permitted`, so I do not rely on that claim. I later reproduced the coordinator’s wider count directly: `197 passed in 39.49s`.

Mutant 46 was re-run by the stopped attempt on this uid-1000 venue and its full file still reported 122 passes. That does not reproduce the brief’s requested ROOT-venue death. The committed focused stand-in test does exercise the mutant-independent mechanism on this host; root venue remains NOT run.

## Items 9 and 12 — mutation audit (42 independently counted mutants)

Re-ran G1’s 21 named mutants on fresh scratch copies against the final tests: all 21 were KILLED. Representative counts: FIFO evidence guard removed → `1 failed, 38 passed in 62.92s`; result FIFO guard removed → `1 failed, 54 passed in 64.04s`; canary field renamed → `1 failed, 65 passed`; all others failed before completing the 122. I did not reconstruct the lane’s separate eight-survivor driver because those eight closures are covered by the fresh 15 below and the baseline; the exact G1 21 requirement is reproduced. I also reproduced the whole red build independently: final tests copied over `517c65e` yielded `71 failed, 51 passed`, including exact red failures for P1 piped status, P2 shape/main-cmdline, P6 mount-failure assertions, exec-user identity, image/argv binding, fixture producer binding and negative-leg ordering.

Fresh targeted source mutants against the final 122-test file, each on its own archive/copy, add 21 distinct mutants beyond G1’s 21. Results for additions M31-M51:

| # | mutant | result | killer / meaning |
|---|---|---|---|
| 31 | add positivity guard for P6 count | **SURVIVED** (`122 passed`) | confirms no test expects zero to fail |
| 32 | strict string type for `canary_exec_user`, preserving the absent-field reason | **SURVIVED** (`122 passed`) | no int-identity rejection test; current integer coercion is unguarded |
| 33 | close `--flag=value` + two-token `--pid host` forms | **SURVIVED** (`122 passed`) | current tests do not cover equivalent spellings |
| 34 | tautology P6 init literal | KILLED (`2 failed, 120 passed`) | own-init hostile inputs |
| 35 | tautology P2/P6 agreement | KILLED (`1 failed, 121 passed`) | explicit disagreement test |
| 36 | remove P6 high-count bound | KILLED (`1 failed, 121 passed`) | 112-process input |
| 37 | skip P6 failed-mount error branch | KILLED (`1 failed, 121 passed`) | failed mount without reason |
| 38 | identity generator always records exec uid 0 | **SURVIVED** (`122 passed`) | generator test accepts whichever supplied value it emits; typed echo is not readback |
| 39 | force `exec_rc=0` | KILLED (`1 failed, 121 passed`) | runner-source status test |
| 40 | erase every P2 collected PID | KILLED (`1 failed, 121 passed`) | live two-holder test |
| 41 | restore colliding `sleep infinity` main command | KILLED (`2 failed, 120 passed`) | collision/static single-source tests |
| 42 | tautology pinned-source commit comparison | KILLED (`1 failed, 121 passed`) | wrong-commit test |
| 43 | force fixture same-host guard true | KILLED (`1 failed, 121 passed`) | PC differs from capture host |
| 44 | restore P1 piped-rc fail-open | KILLED (`3 failed, 119 passed`) | stand-in and venue tests |
| 45 | allow negative P6 count through numeric parser | **SURVIVED** (`122 passed`) | no negative-count input test |
| 46 | remove image-source commit check | KILLED (`1 failed, 93 passed`) | alternate-image hostile test |
| 47 | remove all required argv-pair checks | KILLED (`1 failed, 94 passed`) | host-network/privileged bundle |
| 48 | remove exec-user identity check | KILLED (`1 failed, 91 passed`) | root-observer bundle |
| 49 | accept mismatched P2 pid/uid list sizes | KILLED (`1 failed, 83 passed`) | explicit disagreement test |
| 50 | canary `podman exec` runs as root while preserving a static-test decoy string | **SURVIVED** (`122 passed`) | typed `canary_exec_user` is not read back from the executed process |
| 51 | runner inserts `--privileged=true` before the image while preserving required pairs | **SURVIVED** (`122 passed`) | tests inspect required pairs, not forbidden runner-emitted equivalents |

Independent score: 35 killed / 42 distinct mutants, 7 survived; hollow-green rate 7/42 = 16.7%. The seven survivors correspond to Findings 2, 3, 4/5. This independently satisfies the brief’s ≥40 distinct requirement. The builder’s separate documented 30-mutant campaign plus these new source attacks gives broader reviewed coverage, but its exact runs are not counted in my 42.

## Item 10 — 18-class re-scan

The load-bearing closures run: failed P6 mount with host init fails; failed mount with empty error fails; readiness uses an exact cmdline scan and producer `exec_rc` is captured before last-line extraction. Mechanical review of checker conditionals found no remaining AF-AP-65 shape where a value precondition has a successful-only assertion and no refusing other arm. The remaining domain holes are adjacent classes, not the original one: count positivity (Finding 2), option-normalization closure (Finding 3), and identity self-report/type coercion (Findings 4/5).

## Item 13 — design grade

The whole P1+P2+P6 set is a reasonable multi-instrument containment signature only when all instruments and producer identity are trusted together: P1 pins gVisor kernel+dmesg; P2 pins root PID 1 and exactly one non-root main holder; P6 bans dangerous devices, pins image init identity, cross-checks P2 and bounds the process table; identity pins runsc/image/argv. `s6-svscan` + count + P2/P6 agreement alone does not distinguish the image’s init running directly on the host. A single forged P1 pair (`uname_r` and `dmesg_first_line`) defeats that observation layer because all evidence is self-authored files; the evidence trust ultimately comes from the controlled runner and reviewed capture.

P7 does not prove a network namespace. The `run_argv` screen says what Podman was asked to do; P7 records only the container’s own namespace inode with no host-side paired control. A stronger P7 would record host and container netns identities from the producer and require inequality, plus a negative control. This is Finding 9.

## Item 15 — amendment attacks

Forcing P1’s canary `rc` from 1 to 0 in the live-binding test is a synthetic continuation, not an independent live observation. It still proves field-name reachability: removing/renaming a field yields `observation '<field>' absent`; a canary printing that marker in some unrelated value does not satisfy the assertion because the checker constructs the reason. It does not prove that P1 successfully observed dmesg on this venue. The direct `dmesg_works()` arm separately proves that it did not.

The narrowed `"observation '"` marker is precise for every `_field` absence because `_field` owns one fixed message. It would miss a future parser with a different absence message; that is normal scope, not a current defect. The fixture forged-uname test passed and demonstrated the non-capture guard weakness recorded as Finding 8.

## Additional brief attacks

P1 with a stand-in `dmesg` that exits 0 but prints nothing emits `rc 0` with an empty line; the checker then fails the property, so this is a correctly observed negative, not a false pass. The pinned-source preflight accepts a dirty tree at the correct commit (`ACCEPTED`, rc 0, ` M Dockerfile`), because it checks only HEAD. That means a build can claim the pinned commit while including uncommitted source bytes: Finding 10.

The readiness scan is `podman exec "$CID" …`, therefore container-scoped; a matching cmdline in another container or on the host cannot satisfy it. This was reviewed statically because container starts are forbidden. Sentinel generation with `SENTINEL_READABLE` unset cannot happen on the live path: the variable is initialized `false`, set `true` only after a real host read, and the producer exits unless true before metadata generation.

Fresh wider PC gate with venue exports over the five-file set: `197 passed in 39.49s`, `${PIPESTATUS[0]}=0`, reproducing the coordinator’s count (timing differs). Syntax: runner `bash -n` and all eight canaries `sh -n` returned 0. `ap_screen`: 0 production hits; test screen: eight AF-AP-34 hits, all two comments/five ban assertions/one handle-owned `child.kill()` comment, no broad kill call. Last self-lint of this report returned `report_lint: 17 refs — OK 17, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (at 887f021)`.

## Finding 11 — image identity remains typed, not measured

A hostile bundle retaining `image_source_commit=527da608…` but changing `image` to Alpine and `image_digest` to `sha256:deadbeef` passes. `check_identity` asserts only the typed source-commit constant, not image tag/digest. The default build path checks source HEAD but invokes `podman build` without `--build-arg HERMES_GIT_SHA`, so the image’s baked provenance is absent; the `--image TAG` path skips source preflight entirely. This reopens VERIFY-G1 F4’s core identity question: which image produced the evidence is not measured. Finding 11.

## Reproduced gate result

The static-copy lane gate was run twice with the PC venv first on PATH and all venue exports: `RESULT: rev=887f02117c6d files=12 runs=2 identical=yes rc=0 summary="186 passed in 36.72s 186 passed in 25.75s"`. An earlier invocation without the venv on PATH correctly failed due to missing `rfc3339-validator`; a second correctly configured invocation had one timing-only failure (`2.025s <= 2`) then 186 passes. The clean third invocation above is the gate relied on.

## Findings and minimal fixes

1. **HIGH — the P6 process ceiling is not derived for the image’s full configuration domain.**
   `CONTAINER_MAX_PIDS = 32` is defined at `proofs/S0-08/check_containment.py:78-86`.
   Pinned upstream `hermes_cli/container_boot.py` lines 95-123 and 157-219 show the missing profile domain. Expected: ≤32 follows from all processes the runner can start. Observed: boot always registers a default gateway and walks every persistent named profile, registering each and starting prior-running ones; `/opt/data` is a Docker volume and the runner does not establish a fresh-empty volume. Concrete input: an existing volume with enough profile `SOUL.md` + running state entries. Minimal fix: run this proof with a newly created, runner-owned empty volume and record that volume identity, or derive/assert a configuration-aware bound. Exact red test: seed >20 running profile states into the runner-owned test volume and prove the gate either rejects the configuration before capture or computes a bound that admits the real image process tree but rejects the host table. SOLID source derivation; exact crossing count is UNSURE until the live image runs.

2. **MEDIUM — P6 accepts an impossible zero process count** (`proofs/S0-08/check_containment.py:369-378`). Expected: final numeric domain is `1..CONTAINER_MAX_PIDS`. Observed: `own_pid_count="0"` passes; `-1` and malformed strings fail. Minimal fix: reject `int(own_count) < 1` with a named reason. Exact red test: hostile mount-failed bundle with count `0` must exit 1; paired `1` control proceeds. SOLID; mutant 31/45 survived.

3. **BLOCKER — dangerous Podman option equivalents bypass the argv boundary.**
   `BANNED_RUN_ARGV_TOKENS` is defined at `proofs/S0-08/check_containment.py:54-67`.
   `argv = identity.get("run_argv")` starts the screen at `proofs/S0-08/check_containment.py:216-227`.
   The contract says `run_argv` excludes privileged/bind/host-namespace/cap-add tokens at `proofs/S0-08/CONTAINMENT-SPEC.md:371-388`.
   Expected: no privileged, bind-mount, host-PID or cap-add invocation can satisfy identity. Observed PASS: the equals forms for privileged, cap-add, volume and mount, plus the two-token pid/host form, each inserted before the image. Minimal fix: parse the closed runner grammar, not a specimen token blocklist: require the full exact argv prefix/flag multiplicity/order and exact image+command suffix, or canonicalize every Podman-supported equivalent then allowlist. Exact red table: all listed equivalent spellings exit 1; shipped argv passes. SOLID; mutant 33 survived.

4. **BLOCKER — observer identity is self-reported, not read back** (`proofs/S0-08/tools/pc/run_containment.sh:59-64,235-250,269-292,310-320`; `tests/test_s0_08_containment.py:1377-1379`). Expected: evidence proves who executed each canary. Observed: the runner writes its `CANARY_EXEC_UID` constant to identity; changing that metadata writer to always emit `0` leaves all 122 tests green, and executing as root while leaving the constant at 10000 would still record 10000. Minimal fix: each exec wrapper must emit/read `id -u` from inside that same `podman exec`, bind it to the canary line, and checker-assert every line’s observed uid. Exact red test: stand-in exec runs as uid 0 while requested/typed uid remains 10000; checker exits 1 for measured observer mismatch. SOLID; mutant 38 survived.

5. **LOW — identity uid accepts the wrong JSON type.**
   `exec_user = str(identity.get("canary_exec_user", ""))` appears at `proofs/S0-08/check_containment.py:228-234`.
   Expected: identity schema is type-exact. Observed: integer 10000 passes via string coercion, while a trailing-space string, scientific-notation string and missing value fail. Minimal fix: require exact string type before equality. Exact red test: int 10000 exits 1; string 10000 passes. SOLID; strict-type mutant preserving the existing absent reason survived.

6. **MEDIUM — P4 overstates environment identity.**
   `Secret-bearing env keys in the RUNTIME env (this process's own)` is at `proofs/S0-08/canaries/P4.sh:22-31`.
   Pinned upstream `docker/main-wrapper.sh` lines 23-31 and 61-65 show the different main-program path. Expected by prose: P4’s exec env IS the main program’s inherited env. Observed: P4 measures a later Podman exec’s libc environment; the main wrapper rehydrates from the container environment then overrides HOME, and P4 is a separate process. Minimal fix: narrow the claim to “exec environment exposed to the runtime uid”, or capture the main process env from a privileged producer-side read and compare secret-key names without values. Exact red test: container config HOME `/root`; main wrapper HOME `/opt/data`; P4 exec sees `/root`, proving non-identity. SOLID statically, live value UNSURE because container start was forbidden.

7. **LOW — P2 every-holder test lacks its required live single-holder control.**
   `def test_p2_reports_every_holder_of_the_main_cmdline` is at `tests/test_s0_08_containment.py:985-1012`.
   Expected: prove two holders fail and one holder reaches the uid assertion/pass path. Observed: only two same-uid processes are started; synthetic data supplies the uid-10000 positive. Minimal fix: run a single-holder cell as uid 10000 in the allowed live-container venue and prove the checker accepts it; keep the two-holder refusal. Exact red test: first-match-only mutant must fail two-holder while one-holder remains green. Test inspection is complete; live uid-10000 arm NOT run.

8. **MEDIUM — crun fixture’s host-dependent producer binding disappears off-host** (`tests/test_s0_08_containment.py:1513-1528`; `proofs/S0-08/fixtures/evidence-crun/PROVENANCE.md:39-59`). Expected by report: both venue arms assert the producer binding. Observed on this PC and a forged-uname scratch copy: four values (`docker_sock`, dangerous devices, dev entries, home entries) are not compared; else asserts only non-empty `uname_r`. Minimal fix: split stable fixture-shape tests from capture-host recapture and run the host-dependent equality at the capture venue as an explicit gate, with a recorded venue discriminator; do not describe the off-host arm as equivalent binding. Exact red test: forge live `uname_r` and one host-dependent field; test must fail rather than pass. SOLID.

9. **INFO — P7 records no paired network-namespace control.**
   `netns=$(readlink /proc/self/ns/net 2>/dev/null)` is at `proofs/S0-08/canaries/P7.sh:19-27`.
   P7 is explicitly recorded, not asserted, so this is a documented design gap rather than a contract breach. Minimal future fix: producer records host netns plus canary netns and checker requires inequality with a same-netns negative control if S0-08 is ever made to assert this boundary. Static review is complete.

10. **HIGH — dirty pinned source is accepted as the pinned image source** (`proofs/S0-08/tools/pc/run_containment.sh:98-125`). Expected: build bytes equal commit 527da608. Observed: a repo at the expected HEAD with modified Dockerfile returns `ACCEPTED`, rc 0. Minimal fix: require a clean index/worktree for every build-context path or build from `git archive` of the pin. Exact red test: modify tracked Dockerfile at correct HEAD; preflight exits 2 with dirty-source reason; clean same-HEAD control passes. SOLID.

11. **BLOCKER — image/source identity is typed, not measured.**
   `commit = str(identity.get("image_source_commit", ""))` is at `proofs/S0-08/check_containment.py:205-212`.
   Image build/prebuilt selection begins with `if [ "$BUILD" -eq 1 ]; then` at `proofs/S0-08/tools/pc/run_containment.sh:118-130`; metadata collection/writing is at lines 225-250 and 269-292.
   Expected: checker binds evidence to the exact built image. Observed PASS: a different image name and `sha256:deadbeef` digest while typed source commit remains pinned. Default build omits the upstream Dockerfile’s build-provenance argument; prebuilt image selection skips source verification. Minimal fix: build from archive with a pinned provenance build argument, read image provenance from the running container, bind it to the inspected immutable image ID/digest, and assert all in the checker; disallow unverified prebuilt images or require an approved digest. Exact red test: alternate image/tag/digest with typed pinned commit must exit 1; actual pinned provenance+digest control passes. SOLID.

## Reproduced vs static vs skipped

**Reproduced:** PIN/file identity; 122-test PC suite; 197-test wider PC set; 186-test static-copy lane gate twice; final tests over 517c65e red build (71 failed/51 passed); G1’s 21 mutants; 21 new source mutants; all hostile bundles named above; s6 tarball hashes and generated stage-1 chain; runsc sha/version; real rootless `runsc do` P6 cells with inner uid 1000, uid 65534 and full-capability sandbox-root control; proof-runner three-order test; crun fixture on different-host and forged-uname arms; dirty-source preflight; syntax/screens.

**Reviewed statically:** full runner flow; Podman option syntax from installed `podman run --help`; pinned image entrypoint/wrapper/shim/profile reconciliation; readiness container scope; exec failure flow; P4 env claim; validator order binding.

**Deliberately skipped:** `run_containment.sh`, all Podman container starts/builds/execs, and the real evidence capture, expressly forbidden by this PC lane. No host-root test; no host `setpriv` uid-65534 whole-suite run. I did not run a real image’s P2/P3/P4/P5 canaries or validate `--network none` with rootless Podman+runsc. The coordinator’s original 197-in-6.41s output is cited only; my own count-equivalent run is 197 in 39.49s.

## Exact coordinator path after repair

1. Confirm `/usr/local/bin/runsc` digest `048b89aada69dc3333422e139d6e9d02f8ab06bda52398060e0fbdacca00074c` and release `20260817.0` (done on this host in this grade).
2. Fix Findings 3, 4, 10 and 11 together: exact argv grammar; observer uid readback; archive-clean source; image provenance+digest readback. Add Findings 2/5 tests in the same small checker batch; resolve Finding 1 by an explicit empty runner-owned volume or configuration-aware bound.
3. Build only from `git archive 527da608…` with `HERMES_GIT_SHA` set; inspect the baked provenance and immutable image identity.
4. Run the repaired `run_containment.sh` runsc leg. First inspect P2 exactly one holder at uid 10000; P6 mount rc/error, init comm and count; measured observer uid per canary; argv; image provenance/digest; and P7 netns record. Treat failure of `--network none` as the already-named environment finding.
5. Run checker on pc-runsc. Then run the crun negative capture/check and require the PC kernel reason.
6. Only after independent sandbox verification, mint result, remove marker, transition registry, regenerate attested artifacts, run integrity + ledger-gen + clean diff. All manual cleanup remains by container ID, never process/name matching.

## Hygiene

No production service touched; no bridge; no Podman command that starts/builds/execs a container; no secret read; no git mutation command in the lane tree; no commit/push. All mutations stayed under `../scratch`. Runsc cells exited; no runsc/gofer comm remains; the resume census's only text hit was this Hermes process argv quoting the brief. No S0-08 or lane mount remains, no `/tmp/s0-08-p6-proc.*` remains, and no lane sleeper remains. Worktree status still contains only the two coordinator-shipped staged files (`VERIFY-G1-report.md`, transcript) plus the report written below.

