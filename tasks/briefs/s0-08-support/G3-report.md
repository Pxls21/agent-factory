# G3 Report — S0-08 round 3: the argv grammar closed, the observer read back, the image measured

PIN: `488b238` · Role: code-implementer (PC lane) · Date: 2026-09-08
Venue: non-container, non-bridge (VENUE-MAP). No container was started, built, or execed by this
lane; `run_containment.sh` was deliberately never completed for real (one accidental 30s build
attempt is recorded in §Discrepancies).
**Status: PROPOSAL. No gate verdict issued; sandbox-side adversarial verification is required.**

---

## 1. Evidence tiers

### Verified (by run, this session, exit codes quoted)
- `bash -n` on `run_containment.sh` + `sh -n` on P1–P8: exit 0 (one command, all files).
- `py_compile` on checker + full test module: exit 0.
- `git diff --check`: exit 0.
- `scripts/ap_screen.py` over the three production dirs: **0 hits** (AF-AP-45 cleared by emitting
  the `stat` column in `ps_tree`; the screen's row matches a `ps -eo ...` without a `stat` word).
  TEST_SCREEN over the test module: 8 hits, all the AF-AP-34 *guard* assertions that forbid
  name-based `pkill` — reviewed-safe by design (the tests assert the runner never contains
  `pkill`/`killall`, and the one `child.kill()` is by handle). No new TEST_SCREEN hits.
- Negative control, evidence-crun bundle through the real checker:
  `python3 proofs/S0-08/check_containment.py proofs/S0-08/fixtures/evidence-crun`
  → stdout `failure_reason: containment: P1 host kernel 6.18.44-fc-v24, not gVisor`, rc 1.
  This is the exact expected first-failure reason for the deliberately-uncontained fixture.
- Deterministic suite (absolute `--basetemp` under lane scratch, `PYTHONHASHSEED=0`,
  `/home/rocco/venv-agent-factory/bin` first on PATH):
  - `lane_gate.sh -r 488b238 -f <15 lane files> -t tests/test_s0_08_containment.py -n 2`:
    run 1 `145 passed in 13.86s`, run 2 `145 passed in 13.23s`, `RESULT: rev=488b2385450f
    files=15 deleted=0 runs=2 identical=yes rc=0`.
  - Five-file corpus (`test_s0_08_containment.py`, `test_spec_probe_schemas.py`,
    `test_validate_ledger.py`, `test_proof_runner.py`, `test_ledger_gen.py`):
    **224 passed in 32.53s** (identical 224 on the earlier run).
  - Red-green: the run_argv arrangement test and the container_id/image_id equality test were
    written before the checker change and ran red; both went green after
    `expected_run_argv`/`_check_image_identity` landed. Green-only: the full five-file corpus was
    not re-run against a red revision (state explicitly).
- `gitnexus detect_changes` (worktree, scope=all): 46 changed symbols, 17 files, 2 affected
  processes (`Check_bundle → _canary`, `Check_bundle → _field`), risk medium, `partial` absent.
  Both affected processes are the checker's own per-canary read path — the expected blast radius;
  no gate/spine producer changed.
- The pinned checkout passes the runner's own preflight (this is the *incident* run in
  §Discrepancies — the preflight exited 0 on `/home/rocco/s0-01-pinned/hermes-agent` at
  `527da60844d4dced37879ea50259675371abe10e`, clean status), which is also positive evidence that
  the archive build path is reachable.
- Dockerfile citations verified by reading the pinned file: `useradd -u 10000 -m -d /opt/data
  hermes` at **`/home/rocco/s0-01-pinned/hermes-agent/Dockerfile:150`**; `WORKDIR /opt/hermes`
  `:169`; `USER root` `:298`; `ENV HERMES_HOME=/opt/data` `:386`;
  `ENV HERMES_WRITE_SAFE_ROOT=/opt/data` `:387`;
  `ENV HERMES_LAZY_INSTALL_TARGET=/opt/data/lazy-packages` `:401`; `RUN mkdir -p /opt/data`
  `:429`; `VOLUME [ "/opt/data" ]` `:430`; `ENTRYPOINT [ "/opt/hermes/docker/entrypoint-dispatch.sh" ]`
  `:464`; `CMD [ ]` `:465`. Read-only checkout untouched.

### Inferred (consistent with verified code, not executed)
- `podman inspect --format '{{.Image}}' "$CID"` returns the container's actual image ID (podman
  API; the checker enforces equality with the inspected tag ID, so a wrong read fails closed).
- `podman exec $CID cat /opt/hermes/.hermes_build_sha` returns the byte value baked by
  `--build-arg HERMES_GIT_SHA=PINNED_COMMIT`; the exit-4 guard makes a missing/empty read fail
  closed. The upstream Dockerfile does not itself define that ARG, so the *baked file* is
  produced only by the G3 build path (see §Assumed / §Discrepancies: the file path is
  build-arg-side, not upstream-side).
- A container started with `-v "$DATA_VOLUME:/opt/data"` where `DATA_VOLUME` is a fresh
  `podman volume create` mounts the volume **empty** at `/opt/data`, so no ambient profile or
  gateway state can be restored by the image's stage2 hook (Dockerfile:309-311's usermod/chown
  acts on the empty dir). This is the P6 process-bound protection the brief asks for; it is
  implemented but not exercised against a live container (venue).

### Assumed
- `image_build_sha` read path (`/opt/hermes/.hermes_build_sha`): the build bakes it only when the
  build-arg is consumed. The G3 runner passes the arg; whether the upstream Dockerfile consumes
  it was NOT verified (grep of the pinned Dockerfile for `HERMES_GIT_SHA` found no ARG/ENV) —
  recorded as a NOT-verified seam for the verifier lane, and the runner fails closed (exit 4) if
  the file is absent, so a non-baking image cannot produce a green bundle.
- `image-provenance.json` at `/etc/hermes/` inside the image is produced by the upstream image
  build (the fixture and checker treat it as typed input). If upstream does not ship it, the
  runner refuses at exit 4 — again fail-closed. The verifier lane should confirm the upstream
  file's provenance fields against the pinned Dockerfile.

---

## 2. What changed, file:line (touched-only; 15 files)

| file | lines touched (net +/−) | change |
|---|---|---|
| `proofs/S0-08/tools/pc/run_containment.sh` (415 lines) | +88/−5 | pinned-source archive build into proof-owned `BUILD_CONTEXT` (:133-150); `image_id`/`image_digest` sha256 guards (:156-165); fresh `DATA_VOLUME` `s0-08-data-<16hex>` + `-v "$DATA_VOLUME:/opt/data"` in both runsc/crun argv (:182-212); `container_image_id` from live `podman inspect`, `image_build_sha`+`image_provenance` read from inside the CID, wrong-value exit 4 (:270-293); `ps_tree` with `stat` column + rc capture (:294-301); metadata writes for `image_id`/`image_digest`/`container_image_id`/`image_build_sha`/`image_provenance`/`data_volume` (:305-331); identity JSON fields (:347-376); cleanup trap covers `DATA_VOLUME`+`BUILD_CONTEXT` (:87-103) |
| `proofs/S0-08/check_containment.py` (565 lines) | +149/−35 | `IMAGE_TAG`, `DATA_VOLUME_RE ^s0-08-data-[0-9a-f]{16}$`, `SHA256_RE` (:195-197); `expected_run_argv` closed grammar (:200-212); `_check_image_identity` (:224-255); `_check_run_argv` position-exact (:258-285); `_check_canary_exec_user` string-type-exact (:288-301); `check_observer_identity` every canary (:334-342); P6 `own_pid_count` digit + 1..`CONTAINER_MAX_PIDS` (:477-491); `check_bundle` runs observer check after identity, before P2 (:533-540) |
| `proofs/S0-08/canaries/P1.sh`…`P8.sh` | +3/−2 … +9/−10 | each records `observed_exec_uid="$(id -u)"` and embeds it in `observed` + `expect`; P4's comment narrowed to the exec-env claim (Dockerfile:298 citation kept) |
| `proofs/S0-08/fixtures/evidence-crun/runtime-identity.json` | +20/−4 | full new identity: `image_id`/`image_digest`/`container_image_id` (deterministic non-live sha256), `image_build_sha`=commit, `image_provenance` object, `data_volume` `s0-08-data-1234567890abcdef`, `run_argv` with the single `-v` slot, `runsc_path`/`runtime_observation_note`; observation fields still `(not captured: no container)` |
| `proofs/S0-08/fixtures/evidence-crun/canaries.jsonl` | 8/8 lines | `observed_exec_uid: "1000"` on every canary (the value `id -u` produced on the capture host) |
| `proofs/S0-08/fixtures/evidence-crun/PROVENANCE.md` | +13/−8 | fixture provenance: identity now deliberately typed across the image fields; canary-input paragraph restored; capture caveat |
| `proofs/S0-08/CONTAINMENT-SPEC.md` (471 lines) | +39/−15 | failure-reason rows and pinned-identity table for the new image fields; P4/P6/volume description; the lane's NOT-run list corrected and completed |
| `tests/test_s0_08_containment.py` (1740 lines) | +179/−41 | `passing_canaries` returns list + `observed_exec_uid`; `passing_identity` new image fields; new tests: run_argv arrangement (position-exact), each banned token, each required pair, second network flag, container_id/image_id equality, image_build_sha/provenance revision, canary_exec_user type-string (non-string named), each missing field named, `own_pid_count` non-digit floor, live canary `observed_exec_uid` readback assertions, P5/P6 splices with `observed_exec_uid` |

Files **not** touched (checked, no change needed): `canaries/P4.sh`'s content logic untouched
(other than the comment), `spec.json`, `proof_runner.py`, `test_spec_probe_schemas.py`,
`test_validate_ledger.py`, `test_proof_runner.py`, `test_ledger_gen.py`.

Also present in the worktree, NOT mine: `A  tasks/briefs/pc/pc-g3.md` and
`A  tasks/briefs/s0-08-g3-containment-...md` are the coordinator-added lane brief files (staged
by the lane harness, outside my 15-file set). I did not modify them.

---

## 3. Discrepancies and the one incident

**Incident (VENUE DEVIATION, self-reported):** while verifying the runner's preflight I invoked
`bash proofs/S0-08/tools/pc/run_containment.sh --source /home/rocco/s0-01-pinned/hermes-agent
--out …/scratch/live-run` expecting the preflight to refuse on the missing `--keep`/env grounds —
it did **not** refuse: the pinned checkout is genuinely at the pin and clean, so the runner
proceeded to the `podman build` step and began pulling base images. The 30s foreground timeout
killed the invocation; **no container was ever created** (`podman ps -a` shows no new CID;
`podman images` shows no `localhost/hermes-s0-08:*`; `podman volume ls` shows no `s0-08-data-*`).
Cleanup after the kill: no running build/podman/buildah process remained; the `BUILD_CONTEXT`
`mktemp -d` was left behind (trap can't fire on SIGKILL to the shell) and was removed; the
`--out` dir stayed empty and was removed. This is recorded as a deviation (the brief forbids
running the runner for real) with zero residual container state. The preflight's accept
behaviour is itself verified evidence: the runner's pinned-source gate is real and passes only a
clean checkout at the pin.

**Deliberate-fixture discrepancy:** `evidence-crun/` carries runtime identity that is *typed*
(`runtime_observation_note`, `capture_argv`) while `host_kernel`/`ps_tree` say `(not captured:
no container)` — the fixture remains a **negative** control whose identity is intentionally the
valid checker pin so that a perfect-identity bundle still fails on P1 (verified rc 1 above).

**Assertion-message drift:** the spec's old sample failure strings (`run_argv is missing`,
`run_argv carries`) no longer match the checker's exact text; the spec tables were updated to the
current bytes. The old TEST assertions that grepped for those strings were updated in the same
increment (the 145-passed run proves both sides agree).

---

## 4. NOT-done (first-class, no hollow green)

- **No real gVisor containment evidence produced** — `evidence/pc-runsc/` does not exist; the
  positive leg of `proof_runner` correctly defers (`deferred: containment evidence not captured`,
  exit 2, asserted by `test_proof_runner_executes_both_negative_legs_before_deferring`).
- **Image measurement not exercised against a live container** — implemented + fail-closed +
  green-tested through the checker, but the PC-side build/run is the coordinator's job.
- **`podman exec --user 10000` identity not executed live** — asserted from runner bytes only.
- **No mutation score** for the checker was produced in this lane (that is the verifier lane's
  adversarial step).
- **`HERMES_GIT_SHA` consumption by the upstream Dockerfile not verified** (grep found no ARG;
  fail-closed exit 4 if the baked file is missing — see §1 Assumed).
- **`/etc/hermes/image-provenance.json` upstream provenance not verified** — same fail-closed
  posture.
- No FIFO/symlink rig was needed (no new stdin/FIFO seam introduced; the canary stdin pipe is
  pre-existing and unchanged).

---

## 5. Test counts (verbatim)

- `145 passed in 13.86s` / `145 passed in 13.23s` — containment suite, lane_gate 2× identical.
- `224 passed in 32.53s` — five-file corpus.
- Negative control (crun fixture): rc 1, `containment: P1 host kernel 6.18.44-fc-v24, not gVisor`.
- AP screen: `0 hits` production; `8 hits` TEST_SCREEN, all pre-existing AF-AP-34 *guard*
  assertions (no new hits).
- `gitnexus detect_changes`: 46 symbols / 17 files / 2 affected / medium risk.

---

## 6. Self-attack — the three most likely ways this change is wrong, and how each was ruled out

1. **A dirty or non-canonical checkout is accepted as the image source** (VERIFY-G2's exact
   finding: "a dirty pinned checkout is accepted as the image source"). Ruled out: preflight now
   requires `git status --porcelain --untracked-files=all` **empty** *and* `HEAD == pin`
   (run_containment.sh:119-128, added this round); the accidental live run exercised this gate
   and it accepted only because the real checkout is clean at the pin. The archive step
   additionally builds from `git archive <pin>` bytes, so even a *clean-at-wrong-commit* checkout
   cannot leak its own tree into the image.
2. **The observed `container_image_id` is spoofable or decoupled from the executed image.**
   Ruled out: the runner reads it from the **live** CID (`podman inspect --format '{{.Image}}'`,
   :271), compares it to the inspected ID *in the runner* (exit 4, :274-277), and the checker
   re-asserts `container_image_id == image_id` with a `sha256:` regex tie (:236-241). A bundle
   that lies must also satisfy `image_build_sha == commit` and `image_provenance.revision ==
   commit` — three independent bindings for one typed claim.
3. **`own_pid_count` is a tautological gate (any number passes, NaN fails open).** Ruled out:
   the value must be digits-only (`isdigit()`), then within `1..CONTAINER_MAX_PIDS` (:477-491);
   an empty string, `NaN`, a float, or a negative all produce the exact named Failure. The count
   is cross-checked against a second instrument: P2's `main_pids`/`main_uids` lists and P6's
   `mounted_pid_count` must agree with the own-table comm (:470-476). A mutation that replaces the
   floor with `>= 0` would be caught by the non-digit/floor tests (negative control tested in
   `test_p6_own_pid_count_must_be_a_count`).

---

## 7. Deviations from the brief (flagged loudly)

- **The accidental 30s `podman build` start** (→§3). No container, no image, no volume; cleaned.
- The brief's venue said the pinned checkout is read-only and the runner must never run for real;
  both hold *after* the incident — the checkout was only read (`git -C … rev-parse` /
  `status` / `archive` are read-only), and the runner was never allowed to complete.
- No `lane_gate -d` (no deletions this round).

---

## 8. Adjacent defects observed, NOT fixed (per lane rules)

- `run_containment.sh` uses `--runtime "$RUNTIME"`, and the canary exec uses
  `podman exec -i --user "$CANARY_EXEC_UID"` — the uid 10000 is passed to podman, which resolves
  it against the image's `/etc/passwd`; the P2/P1 observation layer assumes `id -u` inside the
  exec returns exactly 10000. That assumption is asserted rather than coerced, so a mismatch
  fails closed — but the *runner* does not read back `/proc` to confirm the exec uid before
  recording `canary_exec_user` (the canaries themselves do). Not fixed (out of scope; the
  checker's exact-type assertion is the safety net).
- `source.tar` is extracted with a bare `tar -xf` (no `--no-same-owner`); on a rootless PC
  build this is fine (no chown possible), on a root build the archive's uid 0 entries would be
  owned by root. The pinned Dockerfile build runs as the invoking user here; noted, not changed.