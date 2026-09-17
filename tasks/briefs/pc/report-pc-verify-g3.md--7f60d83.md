# VERIFY-G3 — adversarial grade of S0-08 round 3

PIN: `7f60d83` · venue: PC, uid 1000 · role: adversarial verifier

## Item 0 — mechanical gates and identity

FILE IDENTITY: all 15 briefed files matched both the stated line counts/SHA-256 prefixes and an independent `git archive 7f60d83`: checker `52668a02`/565; runner `9800a372`/415; P1–P8 `744df86c`/28, `855fa645`/63, `a6c32030`/50, `358923dc`/57, `2ecf616c`/46, `26cb113c`/61, `8f082f6d`/29, `74d923fe`/31; spec `a47e04c8`/471; fixture provenance `75ac24ad`/99, canaries `a83fba44`/8, identity `044a799b`/60; tests `503f4e12`/1740.

Reproduced under `/home/rocco/venv-agent-factory/bin` first on PATH, PC venue exports and absolute lane-scratch basetemps: `145 passed in 13.95s`; second independent run `145 passed in 13.72s`; five-file set `224 passed in 32.36s`. All exited 0.

The real checker negative control exited 1 with `failure_reason: containment: P1 host kernel 6.18.44-fc-v24, not gVisor`. That is the fixture's recorded kernel, not this host (`6.17.11-200.fc42.x86_64`). `ap_screen.py` returned 0 production hits. `--tests` returned 8 AF-AP-34 hits: explanatory `pkill` prose, five guard assertions banning name-kills, and the by-handle `child.kill()` test cleanup. `bash -n` runner and `sh -n` P1–P8 all exited 0. Pyflakes on checker + tests exited 0; applying pyflakes to the bash runner was a non-applicable parser false error and is not relied upon.

Status: reproduced. No container, podman, runsc, bridge or production service was touched.

## Item 1 — F3 closed argv grammar

SOLID: `C:258-285` rejects every deviation in the recorded token list at its first position. The committed tests cover all named extra tokens, duplicate/reordered/missing pairs and static runner substrings (`T:1197-1265`, `test_host_networked_privileged_run_argv_is_refused`). My direct checker attacks confirmed uppercase/short/foreign `data_volume` names and `/opt/data2` fail; a wrong image fails at `C:224-227` in `_check_image_identity` before argv validation.

FINDING 1 — FOLLOW-UP, SOLID — runtime pathname is unconstrained metadata. `C:206-212` selects the pair grammar only by `Path(runtime).name`; `C:304-316` checks typed runsc version/digest but never binds the pathname. Scratch bundles carrying `/tmp/runsc`, bare `runsc`, `/usr/local/bin/runsc/`, or `crun` plus their matching grammar all returned `rc=0 PASS`. The frozen table `S:389-398` pins `runsc_version` and `runsc_sha256`, but does not list a runtime pathname; the brief explicitly makes path pinning conditional. Therefore this has no frozen-contract mapping and does not qualify as a blocker. The reproduction is the real checker CLI, but a forged bundle is not a canonical live capture: an actual crun capture must fail P1 before a PASS. Material effect is limited to a false runtime label in a deliberately forged artifact. Suggested next step: if pathname is intended to be attested, add it to the frozen identity contract, then require `/usr/local/bin/runsc` and add these red cases. Ownership: checker/spec/tests.

The static runner tests are source-substring mirrors, not runtime gates: a runner mutant putting the required substrings in a comment/dead branch would still satisfy `T:1170-1189` and `test_runner_builds_from_the_pin_archive_and_sets_image_provenance`. This is INFO, not a blocker: no runner can execute at this venue by instruction and the production evidence consumer does close the emitted argv grammar.

## Item 2 — F4 observer UID readback

SOLID: each P1–P8 canary reads `id -u` within the same shell execution that emits its `observed` object; the files were checked as `proofs/S0-08/canaries/P1.sh` lines 12-28, P2 27-63, P3 30-50, and the all-canary source assertion is `T:1121-1125`. The runner’s `podman exec -i --user "$CANARY_EXEC_UID" … sh -s < "$script"` is at `R:394-397`; checker ordering is P1 then observer at `C:533-536`.

Direct bundle attacks: typed uid `10000` plus P4 `observed_exec_uid="0"` failed named P4; absent uid failed named P4; `"10000\n"`, `" 10000"`, integer `10000`, and `"0"` each failed under `_check_canary_exec_user` (`C:288-301`, `exec_user`). A duplicated P1 and unknown Q1 id were refused at parser load. Every uid zero paired with typed `"0"` fails first at `C:288-301`. A P1-invalid bundle with P4 uid zero fails P1 first; that ordering hides later observer evidence only for an already-invalid partial bundle, not a green result.

The coordinator’s live per-canary line must include `"observed_exec_uid":"10000"`; `"0"` is proof that the exec observed as root. Live container readback remains coordinator-owned and unrun.

## Item 3 — F10/F11 archive and measured image

SOLID: build context derives from `git archive "$PINNED_COMMIT"` at `R:133-146`; the arg is supplied; immutable ID/digest and launched-container identity checks are `R:156-165` (`image_id`) and `R:270-292`. The pinned upstream Dockerfile accepts `HERMES_GIT_SHA`, writes `/opt/hermes/.hermes_build_sha`, and creates `/etc/hermes/image-provenance.json` as stated in the brief. `scripts/proof-runner:177-190` treats exit 2 as `capability-unavailable` deferred and a positive-leg exit 4/any mismatch as failure, so a build exit 2 could become a hollow deferral, but archive build failure legitimately means no capable evidence and is recorded as deferred by the specified runner contract.

FINDING 2 — FOLLOW-UP, SOLID — image digest is syntactic and not cross-bound to image ID/source. `C:228-255` checks image ID equality with container ID and validates `image_digest` only as `sha256:<64 hex>`. A scratch bundle with arbitrary `sha256:` plus 64 `d` characters returned PASS. `S:393-395` calls the digest measured but has no frozen equality/source relation to assert, and OCI image ID and repo digest are distinct identifiers. Thus it does not contradict a measurable frozen condition and cannot block this increment. Suggested fix: either downgrade it to recorded metadata or retain the inspect record/a registry attestation sufficient to bind it independently, then add a contract criterion and red test. Canonical check-cli reproduction exists, but no real production run was available under the venue prohibition.

FINDING 3 — FOLLOW-UP — provenance is under-bound. A bundle with only `{"revision": <commit>}` passes although upstream provenance also claims schema, deployment_kind, manager, image and version (`S:389-395`; upstream Dockerfile `:341-342`). The frozen table only pins revision, so no blocking predicate contract mapping for those other fields. Bind schema/deployment_kind/manager/image, and version if the proof is intended to attest full image provenance; add red tests.

Uppercase `image_id`/container ID passes because `C:228,236` lowercases values. That is semantically harmless canonicalization, INFO. A 63-hex digest, different container image ID, build SHA plus newline, malformed/non-object/null provenance and baked SHA mismatch all fail named; direct CLI results recorded in `item_attacks.py`.

STATIC REVIEW: archive omits `.git` (`.dockerignore`) and upstream Dockerfile’s only build-time git-relevant behaviour is avoided by the passed arg, so a dirty source cannot leak into build context. The porcelain preflight is redundant to byte provenance but remains an operator-safety check and should remain. `tar -xf` without `--no-same-owner` and fixed `/tmp/s0-08-run.err`/`/tmp/s0-08-canary.err` are FOLLOW-UP risk observations on the shared execution host; they were not demonstrated through a container path and do not meet the blocking predicate here. The readbacks execute under image default `USER root` (pinned upstream Dockerfile line 298), which is correct because they inspect image-baked root-readable locations before canaries deliberately observe as uid 10000.

## Item 4 — F1 P6 domain and hostile count parsing

SOLID/REVIEWED: `C:81-89` derives 32 from two declared user services plus image/canary processes. The pinned contents declaration lists `main-hermes` and `dashboard`; stage-2 applies data setup only. With runner-created empty `/opt/data` (`R:183-190`) the stated persistent-profile inflation is excluded. The bundle only names the volume: it cannot prove it was empty at start. A canary `ls -A /opt/data` at exec time plus the mount source/target record would be the missing observation. This is a FOLLOW-UP absent a frozen required evidence field.

Direct CLI hostile values: `0`, `-1`, `33`, `1e1`, and leading-space 32 fail; `32` and `032` pass. Arabic-Indic `٣` passes as 3. Superscript `²` reaches `int()` after `str.isdigit()` and produces an uncaught traceback/rc 1 (`C:477-482`, `own_count`; `C:553-561`); the scratch `proof-runner` consumes that as ordinary positive-leg mismatch and creates no result. This is a real diagnostic-quality defect, but its canonical consumer remains fail-closed with rc 1; ASCII-only count grammar was not frozen. Classification FOLLOW-UP: use `^[0-9]+$` and catch ValueError to retain `failure_reason:`.

## Item 5 — floors

SOLID: the verifier’s bulk scratch campaign killed the typed `canary_exec_user` and `own_pid_count` guards. Direct absent field and type/value attacks preserve named refusals. The only non-ASCII count survivors are recorded under Item 4; they do not yield a false PASS for an out-of-range value.

## Item 6 — narrowed claims and fixture split

SOLID: P4 claims the exec environment exposed to the runtime uid and measures environment from that exec; `R:394-397` supplies uid 10000 through `CANARY_EXEC_UID`. `T:1607-1668` reruns shipped canaries with a clean environment and has an explicit cross-host else assertion (`uname_r` nonempty), so it is not the silent `if same_host` skip shape. I forged the fixture’s `uname_r` to `FORGED-KERNEL` in an archive copy; the reproducibility test still passed at this PC venue. This is expected from its explicitly venue-dependent branch and is a FOLLOW-UP, not a blocker: the test demonstrates producer schema and host-independent fields, not immutable fixture kernel values cross-venue.

The committed crun fixture has `observed_exec_uid="1000"` for all lines; `C:534-536` calls `check_p1` before observer identity. `T:1669-1680` asserts typed `canary_exec_user` but not individual fixture observer values. This is INFO: the negative fixture intentionally proves uncontained P1 and its current uid matches a PC-side host capture rather than a real uid-10000 container capture. Change fixture values to `10000` only if declaring it a positive-shape observer fixture; otherwise document them as unreachable under P1-first ordering.

F7’s live single-holder control is not exercised. The exact coordinator cell must show one `sleep 2147483647` holder with uid 10000; `T:1007-1037` is `test_p2_reports_every_holder_of_the_main_cmdline` and only proves a deliberate two-holder ambiguity fixture.

## Item 7 — P7

SOLID: `S:304-318` expressly records P7 and asserts no egress claim; `C:512-523` defines `check_recorded` only for P7/P8 completed records. No test claims an egress property beyond the runner’s exact `--network none` grammar. This is consistent with the frozen boundary.

## Item 8 — mutation audit

A fresh-archive, actual-suite source-mutant campaign ran 45 targeted mutations (`scratch/verify-g3/bulk_mutate.py`) against `tests/test_s0_08_containment.py`. The first 21 include every asserted P1-P6 guard and all were killed, with deterministic named killers (for example P1 kernel: `test_crun_bundle_fails_on_p1_with_the_exact_spec_reason`; P6 ceiling: `test_each_property_mutation_is_caught[P6-HOST-SIZED-PROCESS-TABLE]`). Of mutations 22-45, 22 were killed; two survivors were named, not suppressed: M22 removes the P6 mounted-procfs non-empty guard and M34 removes the data-volume format guard, each leaving `145 passed` because their tests exercise a mismatched/empty mount and invalid volume through a later argv mismatch respectively. M43-M45 independently killed runner build-arg/image-ID/digest source mutations by their named static runner tests. Those are checker-test coverage gaps, not evidence of a passing unsafe production run. The campaign met the brief’s ≥45 floor; M46-61 are outside this bounded pass.

Observed hollow-green rate: 2 / 45 product mutations = 4.4%. Both survivors are FOLLOW-UP test gaps. The seven G2 survivors were addressed by name in the covered set where applicable: provenance guards, observer wiring, and core identity/argv checks. The report does not claim every possible mutant was enumerated.

## Item 9 — bounded rescan

Class 11 grammar domain is exactly: `podman run -d --runtime <runtime>` from `RUN_ARGV_PREFIX_BEFORE_RUNTIME`; runsc basename selects three ordered pairs `--runtime-flag ignore-cgroups`, `--security-opt label=disable`, `--network none`; other basename selects the latter two; exactly `-v s0-08-data-<16 lowercase hex>:/opt/data`; `localhost/hermes-s0-08:527da608 sleep 2147483647` (`C:60-70`, `C:200-212`, `expected_run_argv`). The runtime-path finding means this is not a closed production-runtime identity domain.

Identity table: runner measures runsc version/digest, image ID/digest, launched container image ID, baked SHA/provenance, volume and argv (`R:257-375`, `runsc_version`); checker binds version/digest, tag, source commit, ID/container-ID equality, build SHA, provenance revision and argv (`C:304-331`, `check_identity`). It syntactically validates but does not bind image digest (Finding 2); it accepts typed/forged runtime pathname (Finding 1); canary facts are bundle-forgeable absent an external capture trust root, which is coordinator-supplied evidence by contract.

Checker literal branches reviewed: P1 kernel/dmesg (`C:350-354`, `kernel`), P2 uid (`C:360-388`, `pid1_uid`), P3 tool statuses (`C:400-402`, `if rc != "0"`), P4 socket (`C:408-425`, `sock`), P5 readability (`C:436-447`, `host`), P6 own PID/mount (`C:464-508`) all have named raising arms. P6 `int()` after Unicode `isdigit` is the only unhandled non-literal conversion described in Item 4. Negative control reason reproduced at Item 0; no name-kill production path observed.

## Item 10 — discipline

Reproduced: file identity, all test gates, negative checker control, static syntax, pyflakes for Python, source/manual runner review, real checker hostile-bundle attacks and scratch mutations.

Reviewed statically: runner invocation, archive image provenance, Dockerfile build seam, canary inside-exec line composition, P6 service derivation and source-text runner tests.

Skipped by venue rule: every podman/runsc/container operation, live readback, live empty-volume evidence, P7 netns observation, and any owner service. No PC production resource was altered. External command census: only verifier-owned `python`, `pytest`, `git archive`, `tar`, and short shell parsing processes ran; all scratch child processes exited.

## Item 11 — design and coordinator steps

The single decisive live check remains the coordinator’s real runsc evidence. The metadata weaknesses above are forgeable only in synthetic bundles; an instrumented live runner measurement, independently preserved by the coordinator, is the trust boundary. The arbitrary digest is a follow-up attestation weakness, not proof of a different runtime execution.

Coordinator’s first live run, after blockers are repaired: (1) verify `/usr/local/bin/runsc` hash/version against `C:305-316` (`runsc_version`); red means binary/pin mismatch. (2) build from clean pinned archive with `HERMES_GIT_SHA`; red exit 2 means no evidence, not pass. (3) inspect baked SHA/provenance inside launched image; red exit 4 means image mismatch. (4) capture exact run argv and container/image IDs/digest; red checker means identity/grammar mismatch. (5) verify every canary record reports observer uid 10000; uid 0 is root observation. (6) record `ls -A /opt/data` and P7 network namespace alongside the bundle; nonempty data invalidates P6’s current bound domain and P7 is record-only. A P1/P6 red is containment failure under the checker’s specified reason.

## Finding inventory and recommendation

1. FOLLOW-UP, SOLID — runtime pathname is unconstrained metadata: synthetic `/tmp/runsc`, bare `runsc`, trailing-slash and `crun` bundles pass (`C:206-212`, `C:304-331`, `S:389-398`). Path is not a frozen pinned field; add it explicitly if desired.
2. FOLLOW-UP, SOLID — `image_digest` only has a syntax test and arbitrary digest passes (`C:228-255`, `S:393-395`). No frozen OCI-valid equality/source oracle exists; retain an independent attestation or call it recorded metadata.
3. FOLLOW-UP, SOLID — provenance fields other than revision unbound (`C:247-255`, `image_provenance`). Bind declared fields if full image provenance is claimed.
4. FOLLOW-UP, SOLID — Unicode count parser lets Arabic digit ٣ pass and superscript ² traceback (`C:477-482`, `own_count`). Use ASCII grammar and named Failure.
5. FOLLOW-UP, REVIEWED — evidence does not prove `/opt/data` empty at container start (`R:183-190`, `DATA_VOLUME`; `C:262-271`, `data_volume`). Add canary/mount observation if required.
6. FOLLOW-UP, SOLID — fixture kernel forge passes cross-host producer test by designed venue branch (`T:1654-1667`, `same_host`). Make scope explicit in fixture test name/report.
7. INFO, SOLID — runner source tests are substring mirrors (`T:1170-1194`, `test_runner_builds_from_the_pin_archive_and_sets_image_provenance`). The runner was not executed in this venue; execute it only in the authorized live coordinator leg.
8. INFO, SOLID — crun fixture’s uid 1000 values are unreachable behind expected P1 failure (`C:533-536`, `check_identity`; `T:1669-1680`, `test_crun_fixture_identity_carries_every_pinned_field`).

GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS — no observation satisfies the complete blocking predicate. The two synthetic metadata forgeries have direct check-cli discriminators but lack a frozen path/digest binding and are not canonical live captures; the live runsc leg remains coordinator-owned and unexecuted. This is a recommendation only, not final gate acceptance.

## DISCREPANCIES

* The brief says report output goes to `tasks/briefs/s0-08-support/VERIFY-G3-report.md`; it did not exist in the archive. This report creates it.
* The attempt to invoke `proof-runner` with venue `pc` returned argparse rc 2; rerun with `pc-bridge` reached the malformed superscript bundle and returned expected ordinary rc 1 mismatch.
* report_lint final bounded run: `report_lint: 55 refs — OK 55, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (at 7f60d83)`.
