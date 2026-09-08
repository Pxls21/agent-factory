# Lane G2 — S0-08 gVisor containment round 2: the canaries observe as the RUNTIME USER, P6 asserts under the real capability set, an unambiguous main program, the evidence bound to its image and argv, a fixture its producer can emit (build lane: PC Hermes `code-implementer` when the slot is free, else sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".) Lane G1's landing is
`517c65e` (pushed); its files are unchanged at HEAD.

**Why:** VERIFY-G1 (report `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/wf-results-r5/VERIFY-G1.md` —
READ IT WHOLE FIRST; it is the contract for this round) graded lane G1 NOT-READY with three reproduced blockers: **F1** the checker's
`if mount_rc == "0":` (`proofs/S0-08/check_containment.py:242`) has no else — when `mount -t proc` fails, which it DOES for uid 10000
and for root without `CAP_SYS_ADMIN` inside gVisor (measured: `mount_proc_rc=32`), P6's containment signature is silently skipped and a
bundle whose own procfs says PID 1 is `systemd` PASSES; **F2** `MAIN_CMD="sleep infinity"` (`run_containment.sh:42`, `P2.sh:23`)
collides with the image's root `main-hermes` no-op sleeper (`docker/s6-rc.d/main-hermes/run:27` `exec sleep infinity`, up by
default), so P2 picks a main program by shell-glob order — a coin-flip false red on a correctly contained container; **F3**
`podman exec -i …` (`run_containment.sh:267`) carries no `--user`, so every canary runs as container ROOT (`Dockerfile:298 USER root`)
while the spec (`CONTAINMENT-SPEC.md:152`) and `P4.sh:24-25` claim the runtime user. HIGH: **F4** `check_identity` pins only the
runsc version + sha — never the image, the source commit or the `run_argv` (a bundle from `--privileged --network host` passes);
**F5** the committed crun fixture's P4 line is the PRE-fix producer's output (the shipped `P4.sh` cannot emit it — AF-AP-42). Eight
mutants survived (F6-F12), each a missing regression test. The verifier's judgment: "everything the lane built to JUDGE evidence is
strong; what is missing is the step from 'the checker judges correctly' to 'the canaries can observe the property as the user the
container actually runs'".

**Inputs (read in this order):** VERIFY-G1 whole · the lane brief `tasks/briefs/s0-08-g1-containment-spec-canaries-checker.md` (or
the one brief under `tasks/briefs/` whose title starts `Lane G1`) and `tasks/briefs/s0-08-support/G1-report.md` ·
`proofs/S0-08/CONTAINMENT-SPEC.md` · the pinned hermes-agent checkout `/home/user/nerdherderdani/hermes-agent` (527da608,
READ-ONLY): `Dockerfile:150,298`, `docker/entrypoint-dispatch.sh:18`, `docker/main-wrapper.sh:31,85-88`,
`docker/s6-rc.d/main-hermes/run`, `docker/s6-rc.d/user/contents.d/`, `docker/hermes-exec-shim.sh:54` · `PC-BRIDGE.md:120-150` (the
verified runsc invocation, the platform, the runsc digest prefix) · `docs/INCIDENT-LOG.md` (AF-AP-4, AF-AP-26, AF-AP-34, AF-AP-40,
AF-AP-42, AF-AP-55, AF-AP-58, AF-AP-59) · `scripts/proof-runner:170-190` (the Deferred path) · `/tmp/runsc` (present in the
sandbox at sha `048b89aa…`; `--rootless do` works as root; a non-root cell = `setpriv --reuid=65534 --regid=65534 --clear-groups`
INSIDE the sandbox, the verifier's method).
**Scope (all under S0-08 + its test + your report):** `proofs/S0-08/check_containment.py` · `proofs/S0-08/canaries/{P1,P2,P6}.sh`
(others only if an item requires) · `proofs/S0-08/tools/pc/run_containment.sh` · `proofs/S0-08/spec.json` ·
`proofs/S0-08/CONTAINMENT-SPEC.md` · `proofs/S0-08/fixtures/evidence-crun/` (re-captured) + its `PROVENANCE.md` ·
`tests/test_s0_08_containment.py` · `tasks/briefs/s0-08-support/G1-report.md` (ONLY the identity-table note, F16) · report
`tasks/briefs/s0-08-support/G2-report.md`. NOT yours: `proofs/registry.yaml`, `blocked.json`, the ledger, anything under other
proofs, `.claude/`, `scripts/`. Shared-tree rules: never `git stash/checkout/restore/reset/add/commit/push`; every gate from a
`git archive <PIN> | tar -x` copy under /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/g2/ with your
files copied in (`scripts/lane_gate.sh -r <PIN> -f "<your files>" -t "tests/test_s0_08_containment.py tests/test_spec_probe_schemas.py
tests/test_validate_ledger.py tests/test_proof_runner.py" -n 2`, ONE foreground call, `LANE_GATE_DIR` under your scratch dir);
explicit `--basetemp`; kill only your own processes by pid (never pkill/pgrep -f); NEVER background a run and stop; no outward
actions; NO PC bridge, NO podman, NO container start anywhere (the runner is READ and syntax-checked, never run; gVisor cells run
only through `/tmp/runsc --rootless do` on a scratch dir); never read, print or commit a credential. Authorization: this is the
owner's own containment boundary under test; the canaries and hostile bundles are defensive fixtures. Interpreter
`/root/venv-agent-factory/bin/python`.

## Design (pinned — build it, do not redesign it; line numbers are `517c65e`'s)
1. **F2 — an unambiguous main program, and ambiguity is loud.** `MAIN_CMD="sleep 2147483647"` at `run_containment.sh:42`; ONE source
   for the string: the runner passes it to the canary as `S0_08_MAIN_CMDLINE` in the exec env and `P2.sh` reads it (a missing env =
   rc 1, never a default) — the `:41` "must change in canaries/P2.sh too" contract disappears (F12). `P2.sh` collects ALL matches
   (`main_pids`, `main_uids` as comma lists; drop the `:37` first-match `continue`); the checker raises
   `containment: P2 main program cmdline is ambiguous (<n> processes)` when more than one pid carries it, and asserts the ONE uid is
   `10000`. The readiness gate (`:163`) and the identity scan (`:195`) use the same string. Red test: two live processes carrying the
   pinned cmdline (uid 0 and uid 65534 in the sandbox), `P2.sh` run, the checker → the ambiguity reason; the verifier's mutant 39 and
   45 die.
2. **F3 — the canaries run as the runtime user.** `podman exec -i --user 10000 -e S0_08_SENTINEL_PATH=… -e S0_08_MAIN_CMDLINE=… "$CID"
   sh -s < "$script"` at `:267`; check `podman exec`'s status (not only an empty line — `:269`); record `canary_exec_user` in
   `runtime-identity.json`; `check_identity` requires it equal `"10000"` (a bundle recording `0` → `containment: canaries were exec'd
   as uid 0, expected 10000`). `P3` keeps working: cite `docker/hermes-exec-shim.sh:54` (the shim short-circuits for non-root) in the
   spec. Update `CONTAINMENT-SPEC.md:152` and `P4.sh:24-25` so the claim and the runner agree.
3. **F1 — P6 asserts under the capability set the runtime user HAS.** `check_p6`: keep the mount signature when `mount_proc_rc == 0`;
   ELSE require `mount_proc_error` non-empty AND the capability-independent signature: `own_pid1_comm` equals the container's own
   init (derive the expected comm from the image: PID 1 is `/init` from `docker/entrypoint-dispatch.sh:18` — READ it, pin the
   literal in the checker with the citation) and P2's `pid1_cmdline` starts with `/init /opt/hermes/docker/main-wrapper.sh` (pin from
   the same source), and `own_pid_count` ≤ a bound you DERIVE from the image's s6 service set (state the derivation in the spec; a
   typed number with no derivation is a finding). Red test: the verifier's bundle A5c (`mount_proc_rc: "32"`, `mounted_pid1_comm:
   ""`, `own_pid1_comm: "systemd"`) → exit 1 with a named reason — RED on `517c65e` (paste). Produce the real observation for the
   fixture path by running `P6.sh` under `/tmp/runsc --rootless do` + `setpriv --reuid=65534` (paste the line: `mount_proc_rc=32`,
   `must be superuser to use mount.`). `CONTAINMENT-SPEC.md` §P6 says which signature fires under which capability set (F20).
4. **F4 — the evidence is bound to its image and argv.** `check_identity` pins `image_source_commit` =
   `527da60844d4dced37879ea50259675371abe10e` and screens `run_argv`: required tokens `--runtime-flag ignore-cgroups`
   `--security-opt label=disable` `--network none` present; banned `--privileged`, `--network host`, `-v`, `--mount`, `--pid=host`,
   `--cap-add` absent (an exact-token screen over the recorded list, not a substring over a joined string). Red tests: the
   verifier's A7 (alpine image at `deadbeef`) and A8 (`--network host --privileged`) exit 1; both PASS on `517c65e` (paste).
5. **F5 — the crun fixture is producible by the shipped canaries.** Re-capture `fixtures/evidence-crun/canaries.jsonl` uncontained on
   the sandbox host under `env -i PATH=/usr/bin:/bin sh proofs/S0-08/canaries/P<n>.sh` (so the sandbox's own env is not the
   observation); `PROVENANCE.md` states the exact command, the venue kernel (`6.18.44-fc-v24`, the sandbox — D6 stands), and which
   values are host-dependent. Test: re-run each canary the same way and require the committed line's `observed` KEY SET to equal the
   producer's, and the host-independent P4/P6 values to match (`secret_env_count`, `docker_socket`, the device census).
6. **The eight survivors get their killers** (one assertion each unless noted): F6 the identity generator emits the MEASURED
   `sentinel_readable` (write it to `$META`, `"readable": val("sentinel_readable") == "true"`; a test runs the generator block with
   `SENTINEL_READABLE=false` and reads `false`); F7 `test_live_canary_output_binds_to_the_fields_the_checker_reads[P4]` asserts the
   reason NAMES the planted key `S0_08_LIVE_PROBE_KEY`; F8 a live run of `P3.sh` with a tool that prints a line and exits 3 →
   `rc` 1 (the piped-rc regression); F9 the runner's pinned-commit refusal — extract the preflight into a function the test can
   source (`s0_08_require_pinned_source <dir>` → exit 2 on a wrong commit) and run it against a scratch git repo at the wrong commit;
   F10 the device census content: `P6.sh` run on the host reports `dangerous_devices` containing `/dev/kmsg` (present on the sandbox
   host — paste `ls -l /dev/kmsg`) and the checker's P6 reasons name it; F11 `P5.sh` with a readable sentinel → `yes` and the checker
   → `P5 host control path readable`; F12 closed by item 1.
7. **F13** `P1.sh:13` — `dmesg_all=$(dmesg 2>/dev/null); dmesg_rc=$?` (no pipeline between the tool and `$?`); rc 1 on failure; test
   under `su -s /bin/sh nobody` (or `setpriv`) on the sandbox host where `dmesg_restrict=1`. **F14** `spec.json`: the two negative
   legs FIRST (the runner stops at the first Deferred leg — `scripts/proof-runner:181`); prove with `proof-runner run --proof S0-08`
   on a scratch copy recording three `runs`. **F15** `check_recorded`: a recorded canary with `rc != 0` → `containment: <id> recorded
   canary did not observe (rc <n>)`; A12 exits 1. **F16** a one-line "amended at 517c65e by the coordinator: <4 files>" note atop
   the G1 report's identity table. **F17** the two drifted refs (+6). **F18** a header note in the runner + the spec: `--network none`
   with runsc is UNVERIFIED on the PC (`PC-BRIDGE.md:135-136` verified without it) — a red there is an environment finding. **F19**
   `_field` coerces ints with `str()` — replace with a type check that names the field (`containment: P<n> <key> is not a string`).
8. **Mutants:** G1's 21 + the verifier's 8 survivors (35, 37, 38, 39, 40, 41, 42, 45 — every one must DIE, paste the killer line) +
   the hostile bundles A5b/A5c/A7/A8/A12 → exit 1 with the named reason.
9. **18-class self-sweep** over the lane's files — the verifier regraded class 1 (the `if mount_rc == "0"` gate) and class 11 (the
   cmdline selection is safe only when unique) as DEFECTs the lane missed: your table must show both closed, and every `if <field>
   == <value>:` in the checker paired with its else-branch reason or named as an assertion the else of which raises.
10. **Report discipline:** FILE IDENTITY (sha256 + lines of the FINAL bytes); every `file:line` from `grep -n` on the FINAL bytes and
    `python3 scripts/report_lint.py <report> --map C=proofs/S0-08/check_containment.py --map T=tests/test_s0_08_containment.py
    --map R=proofs/S0-08/tools/pc/run_containment.sh` pasted with MISS 0; the two `lane_gate.sh` RESULT lines pasted; every red-before
    run on `517c65e` pasted beside its green-after; `bash -n`/`sh -n` on every script; `ap_screen.py proofs/S0-08 proofs/S0-08/tools/pc`
    and `--tests`; NOT-done first-class (the PC containment run is the coordinator's, after this lands: VERIFY-G1's eight PC steps).
