# VERIFY-G1 — adversarial grade of lane G1 (S0-08 gVisor containment)

PIN `517c65e` · Opus-5 adversarial-verifier in the sandbox · 2026-09-08 · graded from a `git archive 517c65e`
copy under `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vg1/`.

**VERDICT: NOT-READY.** Three blockers, all reproduced. The first two mean the proof, run as the runner runs
it today, would report a hollow green on P6 and a coin-flip red on P2. The third is the exec-identity mismatch
the brief flagged. Nothing here is a defect of the checker's judging logic — that part is strong (37 of 46
distinct mutants killed, every property reason reachable); the defects are in **what the canaries can observe as the
runtime user** and in **what the checker declines to assert**.

---

## What I reproduced vs reviewed vs skipped

**Reproduced (ran it myself):** the whole non-root canary matrix (host root / host `nobody` / gVisor root /
gVisor uid 65534 / gVisor root with `CAP_SYS_ADMIN` dropped); 46 distinct source mutants against the suite (54 pytest runs — mutants 01-08 were run twice, see item 11); 24 hostile
evidence bundles against the checker; the P2 cmdline-collision on two live processes; the sandbox baseline
(74 passed) and the PC gate (74 passed, `-n 8`, the owner's non-root user, from a clean detached worktree of
the PIN); `report_lint`, `ap_screen`, `bash -n`, `sh -n`; the `spec.json` / `blocked.json` schema validations;
the fixture-vs-producer comparison for P4; the D1/D2 source claims against the pinned checkout at 527da608;
the D3 gVisor measurements.

**Reviewed statically (not executed):** `run_containment.sh` end to end — no podman, no runsc, nothing on the
PC beyond the one allowed pytest gate. The `podman exec` default-user claim rests on `podman-exec(1)` semantics
plus `Dockerfile:298 USER root`, not on a run. Podman's default capability set (which is why the mount also
fails for container-root) is stated UNSURE for that reason; the uid-10000 half of the same finding is SOLID.

**Deliberately skipped:** running `run_containment.sh`, `podman`, `runsc` or anything else on the PC — the
brief forbids it; the containment run is the coordinator's. I did not re-derive the runsc sha256 on the PC
(D5) — that is a bridge action outside the carve-out.

---

## Item 0 — the mechanical gates, pasted

```
$ python3 scripts/report_lint.py tasks/briefs/s0-08-support/G1-report.md --rev 517c65e \
    --map C=proofs/S0-08/check_containment.py --map M=proofs/S0-08/marker_gate.py \
    --map T=tests/test_s0_08_containment.py --map R=proofs/S0-08/tools/pc/run_containment.sh
MISS         report:78    test_s0_08_containment.py:685   cited line reads: 'proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,'
MISS         report:194   test_s0_08_containment.py:745   cited line reads: "# The containment run must not inherit the compose file's host network"
UNRESOLVED   report:218   docker/s6-rc.d/main-hermes/run:27   (not in the repo at 517c65e)
UNRESOLVED   report:219   Dockerfile:309                      (not in the repo at 517c65e)
UNRESOLVED   report:222   docker/s6-rc.d/dashboard/run:9      (not in the repo at 517c65e)
UNRESOLVED   report:225   docker/main-wrapper.sh:31           (not in the repo at 517c65e)
UNRESOLVED   report:229   pyproject.toml:587                  (not in the repo at 517c65e)
UNRESOLVED   report:277   tests/test_s0_04_compression.py:607 (not in the repo at 517c65e)
report_lint: 49 refs — OK 41, NEAR 0, MISS 2, UNCHECKABLE 0, UNRESOLVED 6 (at 517c65e)   rc=1
```

```
$ python3 scripts/ap_screen.py proofs/S0-08 proofs/S0-08/tools/pc
--- AP_SCREEN over 2 path(s): 0 hits over 2 files ---            rc=0     (the lane's claim holds)
$ python3 scripts/ap_screen.py --tests tests/test_s0_08_containment.py
--- TEST_SCREEN over 1 path(s): 7 hits over 1 files ---  AF-AP-34: 7      rc=0
```

**F17 (LOW).** MISS 2 is a finding by the brief's own rule. Both are 6-line drifts in the same file, caused by
the coordinator's later +6-line edit to the test file: report:78 cites `test_s0_08_containment.py:685` for the
string `did not print its pinned reason`, which is at `:691`; report:194 cites `:745` for
`test_runner_code_filter_actually_removes_comments`, which is at `:751`. Minimal fix: bump both by 6.
The 6 UNRESOLVED rows are unresolvable **by construction** (five point into the pinned hermes-agent checkout,
one into another lane's file); I re-verified all five hermes-agent citations by hand against 527da608 and
every one is correct — see item 2.

**F21 (INFO) — the 7 AF-AP-34 hits are not all prose.** Two are comments (`:723`, `:732`); five are string
literals **inside assertions that ban the token** (`:736`, `:737`, `:756` ×2, `:757`, e.g.
`assert "pkill" not in code`). None is a call. The lane's "all classified" holds; the brief's "confirm each is
prose" resolves to "2 prose, 5 bans" — stronger than prose, not weaker.

---

## Item 1 — THE NON-ROOT CLASS (the item that decides the round)

`/tmp/runsc` was present at the expected digest, so nothing was re-installed:
`sha256sum /tmp/runsc` → `048b89aada69dc3333422e139d6e9d02f8ab06bda52398060e0fbdacca00074c`,
`runsc version release-20260817.0 / spec 1.2.1`.

### The matrix — canary × venue × identity (every cell RUN)

| canary | A: host, root | B: host, `nobody` | C: gVisor, root (full caps) | D: gVisor, uid 65534 | E: gVisor, root, `CAP_SYS_ADMIN` dropped |
|---|---|---|---|---|---|
| P1 | rc 0, dmesg OK | rc 0, **`dmesg_first_line` EMPTY** | rc 0, `4.19.0-gvisor` + `Starting gVisor...` | rc 0, **dmesg OK** | rc 0, **dmesg OK** (also `-syslog`) |
| P2 | rc 0, pid1 uid read | rc 0, pid1 uid read | rc 0 | rc 0, `pid1_uid` `0` | — |
| P3 | rc 0 | rc 0 | — | rc 0 | — |
| P4 | rc 0, 12 keys | rc 0, 12 keys | — | rc 0, `mount_count` 5 | — |
| P5 | rc 0, `yes` | rc 0, `no` (EACCES) | rc 0, `yes` (do-mode shares the host fs) | rc 0, `no` | — |
| P6 | rc 0, **mount rc 0** | rc 0, **mount rc 32**, `unshare` rc 1 | rc 0, mount rc 0, `mounted_pid1_comm` `sh` == own | rc 0, **mount rc 32**, signature EMPTY | rc 0, **mount rc 32**, signature EMPTY |
| P7 | rc 0 | rc 0 | rc 0 | rc 0 | — |
| P8 | rc 0 | rc 0 | rc 0 | rc 0 | — |

**Every canary completes its observation as a non-root user — no `did not complete its observation` false red.**
That half of the brief's worry is clean. The damage is in what the observations then say.

Two cells decide the round.

### F1 — BLOCKER · P6's containment signature is silently skipped in exactly the venue the proof runs in

`proofs/S0-08/check_containment.py:242` reads `if mount_rc == "0":` and has **no else branch**. When
`mount -t proc` fails, the checker asserts nothing beyond the device census — no reason, no record, no red.

Measured, three ways, all inside real gVisor:

```
uid 65534 inside runsc:        mount_proc_rc = '32'   mount_proc_error = 'must be superuser to use mount.'
root, CAP_SYS_ADMIN dropped:   mount_proc_rc = '32'   mount_proc_error = 'permission denied.'
root, full caps (the lane's measurement): mount_proc_rc = '0'  mounted_pid1_comm = 'sh' == own_pid1_comm
```

Failing input (hostile bundle A5c, run against the shipped checker):

```json
{"canary":"P6", "observed":{"dangerous_devices":"", "mount_proc_rc":"32",
 "mounted_pid1_comm":"", "own_pid1_comm":"systemd", ...}, "rc":0}
```
→ `PASS: S0-08 gvisor-containment - 6 properties asserted over pc-runsc` (exit 0).
A bundle whose own procfs says PID 1 is **systemd — the host's init** passes P6.

Reachability: the real run either execs canaries as uid 10000 (the spec's stated subject — no capabilities at
all, SOLID) or as container-root under podman's default capability set, which excludes `CAP_SYS_ADMIN`
(UNSURE — not measurable here, but the `-sys_admin` cell above is the exact emulation). **Under either
identity the mount fails and the signature never fires.** The one measurement that produced `rc 0`
(`runsc --rootless do` as root with the full bounding set) is not the target venue — the AF-AP-4 class the
lane itself names in D8.

Minimal fix (checker + spec, one increment):
```python
    mount_rc = _field(obs, "P6", "mount_proc_rc")
    if mount_rc == "0":
        ...existing signature...
    else:
        # the mount could not run: assert the capability-independent signature instead
        own = _field(obs, "P6", "own_pid1_comm")
        if own != CONTAINER_INIT_COMM:           # "init" for this image
            raise Failure(f"containment: P6 container PID 1 is {own}, not the container's own init")
        if _field(obs, "P6", "mount_proc_error") == "":
            raise Failure(f"containment: P6 mount -t proc failed with rc {mount_rc} and no reason")
```
and P6 must then be paired with a second instrument that does fire without `CAP_SYS_ADMIN` — the cheapest is
already in the bundle: P2's `pid1_cmdline` must be the image's `/init …main-wrapper.sh` and `own_pid_count`
must be under a pinned bound.

Exact red test:
```python
def test_p6_mount_failure_is_not_a_silent_pass(tmp_path):
    lines = passing_canaries()
    for rec in lines:
        if rec["canary"] == "P6":
            rec["observed"].update(mount_proc_rc="32", mounted_pid1_comm="",
                                   own_pid1_comm="systemd")
    proc = run_checker(write_bundle(tmp_path / "pc-runsc", canaries=lines))
    assert proc.returncode == 1, proc.stdout      # RED today: returncode is 0
```
SOLID.

### F13 — MEDIUM · P1's `dmesg` failure is invisible in `rc` (the piped-rc class the lane fixed in P3, still live in P1)

`proofs/S0-08/canaries/P1.sh:13` is
`dmesg_first=$(dmesg 2>/dev/null | head -n 1) || dmesg_first=""` — the `||` reads the **pipeline's** status,
which is `head`'s and always 0, and `:16` sets `rc` only from `$kernel`. Run as `nobody` on the sandbox host
(`kernel.dmesg_restrict` = 1) the canary emits `"dmesg_first_line":""` with `"rc":0`, and the checker answers
`failure_reason: containment: P1 dmesg line 1 does not announce gVisor:` — a red with an empty reason, not a
"did not observe".

**Not a blocker for the PC run:** measured inside gVisor, `dmesg` works for uid 65534 and for root with
`-syslog` dropped (gVisor has no `/proc/sys/kernel/dmesg_restrict` and does not gate `syslog(2)` on
`CAP_SYSLOG`). It bites only outside gVisor — i.e. on the crun negative leg, where P1's kernel check fails
first anyway. Still the same defect class the lane's own §18 row calls a DEFECT in P3.

Minimal fix (POSIX sh, no pipeline between the tool and `$?`):
```sh
dmesg_all=$(dmesg 2>/dev/null); dmesg_rc=$?
dmesg_first=$(printf '%s\n' "$dmesg_all" | head -n 1)
[ "$dmesg_rc" -eq 0 ] || rc=1
```
Exact red test: run `P1.sh` under `su -s /bin/sh nobody` on a host with `dmesg_restrict=1` and require `rc` 1.
SOLID.

### The rest of the class, canary by canary

- **P2 as non-root: fine** — `/proc/1/status` and `/proc/<pid>/cmdline` are world-readable; uid 65534 inside
  gVisor read `pid1_uid` `0`. No false red. (P2's real defect is F2, below, and it is identity, not privilege.)
- **P3 as non-root: fine** — no privileged call; and the image's shim short-circuits for non-root
  (`docker/hermes-exec-shim.sh:54` `if [ "$(id -u)" != "0" ]; then exec "$REAL" "$@"`), so switching the runner
  to `--user 10000` does **not** break `hermes --version`.
- **P4 as non-root: fine** — `env` and `/proc/self/mountinfo` need no privilege. The coordinator's fix is
  correct and I reproduced the reason it was needed (as `nobody`, `/proc/1/environ` is unreadable).
- **P5 as non-root: completes**, and reports `no` — but for a *different reason* (`Permission denied` rather
  than `No such file`). The checker cannot tell the two apart; in the real container the path does not exist,
  so this is not exploitable. Recorded, not a finding.
- **P6 device census as non-root: fine** — `[ -e /dev/... ]` needs no privilege.
- **P7/P8 as non-root: fine.**

**Answer to the brief's P6 question, verbatim:** the mount does fail as the runtime user; the failure is
recorded as an *observation with rc 0*; and the checker treats it as **neither** the containment signature
**nor** `did not complete its observation` — it skips the assertion entirely. That is worse than a false red:
it is a silent hollow green, and it is the expected outcome of the first PC run.

---

## Item 2 — D1 / D2 / D3 against the pinned source (`/home/user/nerdherderdani/hermes-agent` @ 527da608)

`git rev-parse HEAD` → `527da60844d4dced37879ea50259675371abe10e`. All three deviations are **correct**, and
D1's evidence is stronger than the lane realised — it is the mechanism of F2.

**D1 — CONFIRMED.** `docker/s6-rc.d/main-hermes/run:27` is exactly `exec sleep infinity`, with the comment at
`:23` "For now this service is a no-op: it sleeps forever, doing nothing." No `s6-setuidgid`, so it runs as
root. It is **up by default**: `docker/s6-rc.d/user/contents.d/` contains `main-hermes` and `dashboard`.
The real drop is `docker/main-wrapper.sh:31` — `drop() { [ "$(id -u)" = 0 ] && set -- s6-setuidgid hermes "$@"; exec "$@"; }` —
reached from `docker/entrypoint-dispatch.sh:18` (`exec /init /opt/hermes/docker/main-wrapper.sh "$@"` when
`$$ -eq 1`) and applied at `main-wrapper.sh:85-88` (`command -v "$1"` → `drop "$@"`). It is the **only** drop
on the CMD path. `Dockerfile:298` is `USER root`; `Dockerfile:150` is `RUN useradd -u 10000 -m -d /opt/data hermes`.

### F2 — BLOCKER · the runner's `MAIN_CMD` collides with the image's root sleeper; P2's subject is a coin flip

`proofs/S0-08/tools/pc/run_containment.sh:42` sets `MAIN_CMD="sleep infinity"` and
`proofs/S0-08/canaries/P2.sh:23` sets `MAIN_CMDLINE='sleep infinity'`. The supervised `main-hermes` service
runs **the identical cmdline as root**. So the container will hold **two** processes whose
`/proc/<pid>/cmdline` is byte-for-byte `sleep infinity`: the root no-op sleeper and the dropped CMD (uid
10000). `P2.sh:34-42` walks `/proc/[0-9]*` in shell glob order — lexicographic, not numeric — and `:37`
(`[ -n "$main_pid" ] && continue`) stops at the **first** match.

Reproduced in the sandbox with two live processes carrying that exact cmdline (one uid 0, one uid 65534):

```
ROOTPID=3746 (uid 0)  USERPID=3747 (uid 65534)
all matching cmdlines:  pid=3016 uid=0 · pid=3746 uid=0 · pid=3747 uid=65534
P2 verdict (3 runs):    main_pid= 3016 main_uid= 0
```
→ the checker's answer would be `failure_reason: containment: P2 main program uid 0, expected 10000` on a
**correctly contained container**. Whether it reds depends only on which pid string sorts first — roughly a
coin flip, and not reproducible run to run.

Two more consequences of the same collision:
- `run_containment.sh:163`, the readiness gate, matches the same string, so it can declare the container ready
  on the **root** sleeper before the CMD has dropped — the start-of-container race the brief asked about.
- `run_containment.sh:195` builds `main_program_user` for the identity file by the same scan, so the recorded
  identity inherits the ambiguity.

Minimal fix: make the main program unmistakable and make ambiguity loud.
```sh
MAIN_CMD="sleep 2147483647"      # run_containment.sh:42  (and P2.sh:23 to match)
```
plus, in `P2.sh`, collect **all** matches (`main_pids`, `main_uids` as comma lists, drop the `:37`
short-circuit) and, in the checker, `raise Failure` when more than one pid carries the main cmdline.
Exact red test: start two processes with the pinned cmdline (uid 0 and uid 10000), run `P2.sh`, require the
checker to fail with `containment: P2 main program cmdline is ambiguous (2 processes)`. SOLID.

**D2 — CONFIRMED.** `pyproject.toml:587` is the `[tool.setuptools.packages.find]` `include` list:
`["agent", "agent.*", "tools", "tools.*", "hermes_cli", "hermes_cli.*", "gateway", ...]` — no top-level
`hermes` package. `import hermes` would have failed against a correctly-built image. **Is `hermes --version`
stronger?** The question is moot: `P3.sh:30` already runs `/opt/hermes/bin/hermes --version` *and* `:33` the
import. That pair is the right shape — the shim proves the CLI entry point works, the import proves the
package is installed. No change needed.

**D3 — REPRODUCED.** Under `/tmp/runsc --rootless do` as root: `mount -t proc` rc 0, `unshare -n` rc 0,
`uname -r` `4.19.0-gvisor`, `dmesg` line 1 `[    0.000000] Starting gVisor...`, `mounted_pid1_comm` `sh` equal
to `own_pid1_comm`, 5 processes visible. **`runsc do` has no `--uid`** (`runsc help do` offers only
`-uid-map`/`-gid-map` for the sandbox's userns), so the non-root cell is `setpriv --reuid=65534` *inside* the
sandbox — and that is where the mount stops working (F1). The lane's D3 is right about gVisor; it is wrong to
carry the resulting assertion as if it held for the runtime user.

---

## Item 3 — the checker: mutants re-run, plus 24 hostile bundles

**Every one of the lane's 21 named mutants I re-ran was KILLED** (see item 11 for the full 54-mutant table,
with the counts pasted from the runs). Every REASON in the spec's §3 table is reachable by at least one
mutant or hostile bundle. The judging logic is sound; the gaps are in what it declines to assert.

Hostile bundles (my own; baseline `A0` passes, so every red below is the checker acting):

| # | hostile input | checker | verdict |
|---|---|---|---|
| A1 | P4 `rc` 1 with plausible observations | exit 1 `P4 canary did not complete its observation (rc 1)` | **holds** — observations from a failed canary are refused |
| A2 / A2b | duplicated P1 row (bad value second / first) | exit 1 `P1 canary line duplicated` | **holds**, order-independent |
| A3 | `"secret_env_count": "0 "` | exit 1 `secret_env_count 0  disagrees with 0 reported key name(s)` | holds |
| A3b/A3c/A15 | JSON ints where strings are expected | **PASS** | F19 (INFO): `_field` coerces with `str()`; every coercion I could build fails closed |
| A3d | `dangerous_devices: []` | exit 1 `raw host devices present: []` | fails closed |
| A4 | sha pinned OK, **version drifted** | exit 1 `runtime identity runsc release-20260901.0, expected release-20260817.0` | holds |
| A4b | version OK, sha drifted | exit 1 | holds |
| A4c | sha uppercase | PASS | by design (`.lower()`) |
| A5 | **forged gVisor kernel string + host devices present** | exit 1 `P6 raw host devices present: /dev/kmsg,/dev/loop0` | **holds — the two-instrument property works when the mount succeeds** (tactic 8) |
| A5b/A5c | **mount failed (the uid-10000 reality) + host PID 1** | **PASS** | **F1 BLOCKER** |
| A6 | P1 `dmesg_first_line` empty | exit 1 (empty reason tail) | F13 |
| A7 | identity names `docker.io/library/alpine:3.20`, `image_source_commit: deadbeef` | **PASS** | **F4** |
| A8 | identity `run_argv` = `--network host --privileged` | **PASS** | **F4** |
| A9/A10 | host-control path empty / off by a trailing slash | exit 1 `P5 sentinel path mismatch` | holds |
| A11 | `"rc": true` | exit 1 `P1 rc is not an integer` | holds |
| A12 | P7/P8 `rc` 7 | **PASS** | **F15** |
| A13 | every `observed` carries `verdict: PASS` | PASS on a good bundle; a bad one still reds on the property | design holds |
| A14 | lowercase `my_token` env key | exit 1 `P4 1 secret-bearing env key(s) in the runtime env: my_token` | holds |

### F4 — HIGH · the evidence is never bound to the image or the argv it came from

`check_identity` (`proofs/S0-08/check_containment.py:135-147`) pins **only** `runsc_version` and
`runsc_sha256`. The identity file records `image`, `image_digest`, `image_source_commit` and the exact
`run_argv` (`run_containment.sh:241-244`) and the checker reads none of them.

Failing inputs: A7 (an alpine image at commit `deadbeef`) and A8 (`--network host --privileged` in the recorded
argv) both PASS. P7's whole claim — "the containment run must not inherit host networking" — is enforced by a
**static test on the runner's source** (`test_pc_runner_pins_the_verified_runsc_flags`), never on the evidence.
A run driven with edited flags produces a bundle the checker accepts.

Minimal fix in `check_identity`:
```python
PINNED_HERMES_COMMIT = "527da60844d4dced37879ea50259675371abe10e"
if str(identity.get("image_source_commit", "")) != PINNED_HERMES_COMMIT: raise Failure(...)
argv = identity.get("run_argv") or []
for flag in ("--runtime-flag", "ignore-cgroups", "--security-opt", "label=disable", "--network", "none"):
    if flag not in argv: raise Failure(f"containment: run_argv is missing {flag}")
for banned in ("--privileged", "host", "-v", "--mount", "--pid=host"):
    if banned in argv: raise Failure(f"containment: run_argv carries {banned}")
```
Exact red test: the A7 and A8 bundles must exit 1. SOLID.

### F15 — LOW · a recorded canary that never observed still satisfies "recorded"

`check_recorded` (`proofs/S0-08/check_containment.py:254-258`) calls `_canary`, and `_canary:120` enforces
`rc == 0` only `if cid in ASSERTED`. A12 (P7 and P8 with `rc` 7) passes. The spec's promise that the run
"RECORDS its egress and cgroup posture" can be satisfied by an empty record.
Minimal fix: in `check_recorded`, `if rec["rc"] != 0: raise Failure(f"containment: {cid} recorded canary did not observe (rc …)")`.
Red test: the A12 bundle must exit 1. SOLID.

---

## Item 4 — the marker gate

All six verdicts reproduced by one input each, and every one is mutant-killed (mutants 08, 09, 20, 21, 31 in
item 11; the two FIFO mutants 29/30 make the gate **hang** and are killed by the suite's own 60 s timeout).

| state | verdict | exit |
|---|---|---|
| live tree (`expired`, no result) | `marker: expired - the proof must run` | 1 ✅ reproduced |
| result present + `blocked.json` gone | `marker: completed transition` | 0 |
| neither | `marker: absent` | 1 |
| `probe_run` missing (the committed fixture) | `marker: malformed: probe_run` | 1 |
| `blocker_status: "gone"` | `marker: malformed: blocker_status 'gone'` | 1 |
| `absent` / `rejecting`, well formed | `marker: <status>` | 0 |

The transition rule holds under forgery: `_result_is_real` (`proofs/S0-08/marker_gate.py:50-69`) rejects a
non-regular `result.json` (`:57`), an unparseable one (`:61`), a non-object (`:63`) and one carrying another
proof's id (`:64` — `payload.get("proof_id") != proof_dir.resolve().name`). Mutants 20 (presence alone retires
the marker) and 21 (proof_id ignored) were both killed; a FIFO named `result.json` hangs without `:56` and the
suite's timeout catches it. **No finding.** One note for the coordinator: the gate keys the id on
`proof_dir.resolve().name`, so a mint written into a differently-named directory would be rejected — correct,
and worth knowing before the transition.

---

## Item 5 — `spec.json`

Three legs, schema-valid (`jsonschema.validate` against `proofs/schemas/spec.schema.json`, run here: VALID).
`blocked.json` is valid against `blocked.schema.json`; the malformed-marker fixture is **invalid on exactly the
field the gate names** (`'probe_run' is a required property`) — the fixture and the gate agree.

The positive leg reports `deferred: containment evidence not captured` (exit 2) today, and
`scripts/proof-runner:181-185` turns `run["exit_code"] == 2` into `Deferred(... artifact preserved ...)`.
Both negative legs run exactly as the runner runs them, in the suite
(`test_spec_negative_legs_reproduce_their_pinned_reasons`, `tests/test_s0_08_containment.py:676-691`), and
mutant 11 (SPEC-REASON-DRIFT) is killed there. D4's "marker leg as a second negative" is forced by the schema
(`leg` enum `positive|negative`) and is the shape `proofs/S0-11/spec.json` uses. Honest so far.

### F14 — LOW/MEDIUM · while the proof is deferred, `proof-runner` never reaches either negative leg

The legs execute in list order and the **positive leg is first**, so `scripts/proof-runner:181` raises
`Deferred` on the first leg and the crun bundle and the marker gate are never executed by the runner. The
answer to the brief's question is therefore **yes, it hides the marker's state from the ledger**: the marker
leg only ever runs inside pytest until the PC run lands.
Minimal fix: put the two negative legs first in `spec.json["legs"]` (nothing in the schema or the runner
requires positive-first), or state the limitation in `CONTAINMENT-SPEC.md` §3. Cheapest is the reorder.
Exact red test: `proof-runner run --proof S0-08` on a scratch copy must record three `runs` entries, not one.
SOLID (I read the runner's loop; I did not mint an artifact from it).

---

## Item 6 — the PC runner (READ, never run)

`bash -n` clean. `sh -n` clean on all eight canaries. External calls, enumerated from the file: `podman`
(`build`, `image exists`, `run`, `inspect`, `exec`, `logs`, `image inspect`, `rm -f`), `git -C rev-parse`,
`sha256sum`, `uname`, `od`, `date`, `mktemp -d`, `python3`, `sed`, `seq`, `sleep`, `rm`, `mkdir`, `printf`,
`cat`, `tr`, `cut`, `grep`, `awk`, `ls`, `id`, `s6-svstat`, `command`, `tail`, `head` — matching the lane's
list. **No `systemctl`. No `pkill`/`killall`. `podman rm -f "$CID"` by id only** (`run_containment.sh:70`),
never by name; the cleanup trap's `CID`/`SENTINEL` are pre-initialised at `:65-66` so `set -u` cannot trip it.

Flags: `--runtime "$RUNTIME"`, `--security-opt label=disable`, `--network none`, and `--runtime-flag
ignore-cgroups` added only when `"${RUNTIME##*/}" = "runsc"` (`:126`) — so the crun leg correctly omits it.
The image pin is real: `:82-86` compares `git -C "$SOURCE_DIR" rev-parse HEAD` against
`PINNED_COMMIT="527da60844d4dced37879ea50259675371abe10e"` and exits 2 otherwise.
The identity generator hands every value to Python through **files** (`:201-217`), so hostile `ps_tree` text
cannot break or inject into the generated program. **Reproduced:** I extracted the `PYIDENT` program verbatim
from the runner and ran it over a `$META` directory carrying `"` quotes, backslashes, a `{"injected": true}`
JSON fragment, `$(rm -rf /)`, invalid UTF-8 bytes, and a NUL-joined `run_argv` whose last element was
`infinity"; rm -rf /`. Result: exit 0, valid JSON, 17 keys, every hostile string preserved as data
(`errors="replace"` turned the bad bytes into U+FFFD). The claim holds. The same run also shows F6 plainly:
`"sentinel_host_read": {"path": "…", "readable": true}` came out `true` from a `$META` that never carried a
`sentinel_readable` file at all.

### F3 — BLOCKER · the canaries are exec'd as **root**, not as the runtime user the spec says

`run_containment.sh:267` is
`line="$(podman exec -i -e S0_08_SENTINEL_PATH="$SENTINEL" "$CID" sh -s < "$script" 2>/dev/null | tail -n 1)"` —
**no `--user`**. `podman exec` defaults to the container's configured user, which is the image's
`USER root` (`Dockerfile:298`). So every canary runs as uid 0 inside the container.

That contradicts the shipped spec in two places:
`proofs/S0-08/CONTAINMENT-SPEC.md:152` — "the canary is exec'd inside the container as the runtime user, so its
environment is the one the main program inherits" — and `proofs/S0-08/canaries/P4.sh:24-25`, the same claim in
the canary's own comment. Both are false against `:267`.

Consequences: **P4** observes the container-config env of a root exec, not the env the dropped main program
holds (they can differ — `main-wrapper.sh` re-execs through `with-contenv` and exports `HOME=/opt/data` before
dropping); **P5** attempts the host read as root, a different subject from the one the security profile is
about; **P2** is unaffected (it reads other processes, not itself). It also means the brief's premise for item
1 — "the real containment run execs the canaries as uid 10000" — is **not what the runner does today**.

Minimal fix: `podman exec -i --user 10000 -e S0_08_SENTINEL_PATH=… "$CID" sh -s < "$script"`, record the exec
identity in `runtime-identity.json` (`"canary_exec_user": "10000"`), and have the checker assert it. The
image's shim short-circuits for non-root (`docker/hermes-exec-shim.sh:54`), so P3 keeps working. Note this
change makes F1 *certain* rather than merely likely — fix F1 in the same increment.
Exact red test: a bundle whose identity records `canary_exec_user` `0` must exit 1. SOLID on the spec/runner
contradiction (read from the bytes); UNSURE only on whether podman's default caps would also have blocked the
mount for the root exec.

### F6 — MEDIUM · P5's positive control is a typed literal, not a measurement

`run_containment.sh:250` emits `"sentinel_host_read": {"path": val("sentinel_path"), "readable": True}` — the
literal `True`, never the `SENTINEL_READABLE` value measured at `:105-108`. The gate at `:109-112` (exit 4 if
the sentinel is unreadable) makes the constant true *today*, but the checker's "positive control" is reading a
value the producer typed. Mutant 38 (change it to `"yes"`) **survived** the whole suite: nothing tests the
generator's output at all.
Minimal fix: `printf '%s' "$SENTINEL_READABLE" > "$META/sentinel_readable"` and
`"readable": val("sentinel_readable") == "true"`.
Exact red test: run the generator block with `SENTINEL_READABLE=false` and require the emitted JSON to carry
`"readable": false`. SOLID.

### F18 — LOW · `--network none` has never been verified with runsc on the PC

`PC-BRIDGE.md:135-136`'s verified invocation is `podman run --rm --runtime /usr/local/bin/runsc
--runtime-flag ignore-cgroups --security-opt label=disable …` — **no `--network none`**, and its note records
working HTTPS from inside. The runner adds `--network none` (`run_containment.sh:124` and `:131`), justified
in the spec's P7. Not a defect; a first-run risk the coordinator should expect to debug (rootless podman +
runsc + `none`). Naming it so a red there is read as an environment finding, not a proof failure.

---

## Item 7 — the negative fixture

`PROVENANCE.md` is honest about the two things that matter: the bundle is **constructed**, not a captured PC
run, and it records the sandbox's `6.18.44-fc-v24` rather than the PC's `6.17.11-200.fc42` (D6). It states
which half is measured (the canaries) and which is deliberately typed (the valid pinned runsc identity), and
the reason — the checker must read observations, not metadata. `test_crun_bundle_identity_is_valid_so_p1_is_what_catches_it`
holds that line and mutants 01/10 kill it. The malformed-marker fixture fails on `probe_run`, the field the
gate names (verified above).

### F5 — HIGH · the committed fixture's P4 line cannot be produced by the shipped `P4.sh`

`PROVENANCE.md:5-15` gives the capture command and says "Every observation in it is a real measurement of the
uncontained host — nothing was typed." Run that command today with the shipped canaries and the P4 line does
not come back. I ran all three:

```
committed fixture line 4 :  "secret_env_count":"0",  "secret_env_keys":"",    "mount_count":"27", "host_bind_roots":"/run/netns,net:[4026532259]"
shipped P4.sh as root    :  "secret_env_count":"12", "secret_env_keys":"AWS_ACCESS_KEY_ID,…",     "mount_count":"26", "host_bind_roots":"/run/netns"
the OLD /proc/1/environ P4:  "secret_env_count":"0",  "secret_env_keys":"",    "mount_count":"26", "host_bind_roots":"/run/netns"
```

The fixture matches the **pre-coordinator-fix** P4 (the `/proc/1/environ` reader), not
`proofs/S0-08/canaries/P4.sh` at the PIN. AF-AP-42's class: a committed fixture that its own producer can no
longer emit. It does not change the negative leg's verdict — P1 fails first, so the P4 line is never read —
but it breaks the fixture-to-producer binding the lane's own class-14 row claims to have closed, and it will
mask a P4 regression forever.

Minimal fix: re-capture `fixtures/evidence-crun/canaries.jsonl` with the shipped canaries in a **clean env**
(`env -i sh P4.sh`, so the sandbox's own secrets are not the observation) and update `PROVENANCE.md` to say so.
Exact red test: re-run each canary uncontained under `env -i` and require the committed line's `observed` key
set **and** the P4/P6 values that are host-independent to match. SOLID.

---

## Item 8 — D5 / D7 / D8

**D5 — the runsc sha.** The lane says the digest was measured "from the identical release binary in the
sandbox". I reproduced the measurement: `sha256sum /tmp/runsc` →
`048b89aada69dc3333422e139d6e9d02f8ab06bda52398060e0fbdacca00074c`, and `/tmp/runsc --version` →
`runsc version release-20260817.0 / spec: 1.2.1`. `PC-BRIDGE.md:128` records only the truncated `048b89aa` prefix for `/usr/local/bin/runsc`; the first eight hex characters match. **The pin is a sandbox
measurement asserted about a PC binary** — integrity ≠ identity (Phase 0). The lane says so plainly and names
the confirmation as the coordinator's; that is the right call. It stays NOT-confirmed until
`sha256sum /usr/local/bin/runsc` runs on the PC.

**D7 — KVM vs systrap.** `PC-BRIDGE.md:148-149` records "Platform: systrap (runsc default; `/dev/kvm`
absent)". No canary and no checker line assumes KVM: `P6.sh:24` lists `/dev/kvm` among the devices that must be
**absent**, which is consistent with systrap and with the probe. Grepped the eight canaries and the checker for
`kvm` — the only occurrence is that census entry. **Agree with D7, no finding.**

**D8 — `runsc --rootless do` shares the host filesystem.** Reproduced: from inside a `do` sandbox,
`/root/vg1-sentinel-abc123` was readable as root and `ls /home` returned the host's `claude,ubuntu,user`.
So `do` mode cannot test P4's mounts, P5's sentinel or the image's tools. **Agree with D8.** The correction I
would make: D8 is used to justify "P1, P6, P7, P8 *were* smoke-run under real gVisor" — but the P6 smoke ran as
**root with the full bounding set**, which is not the runtime identity either. `do` mode's limitation is not
only the filesystem; it is also the capability set. That is F1.

---

## Item 9 — the 18-class preflight, re-run over the 18 files

I re-scanned the lane's own file set. Agreement on 15 classes. Three rows I grade differently:

| class | the lane's verdict | mine | why |
|---|---|---|---|
| 1 presence-gated | 6 instances, **SAFE**, "every one is followed by a named refusal" | **DEFECT (missed)** | `check_containment.py:242` `if mount_rc == "0":` has no named refusal and no else — F1. The lane counted it as an assertion, not as a gate. |
| 11 world-scoped enumerations | 4, **SAFE**, "every `/proc` scan SELECTS by exact cmdline" | **DEFECT (missed)** | selecting by an exact cmdline is only safe when the cmdline is unique. It is not (F2). `P2.sh:37` resolves the ambiguity by glob order and records nothing about it. |
| 3 stale `[-1]` / `tail -n 1` | 1, **SAFE** | SAFE with a caveat | `run_containment.sh:267` also discards stderr (`2>/dev/null`) and never checks `podman exec`'s status; only the empty-output case is caught (`:269`). A canary that dies after printing its line is indistinguishable from one that succeeded. Low. |

Classes 4 (negative acceptance), 12 (signal installs), 15 (two counters), 16 and 17 (empty) I re-checked and
agree. Class 4 in particular is genuinely de-vacuoused: `test_pc_runner_tears_down_by_id_never_by_name`
(`tests/test_s0_08_containment.py:735`) carries the positive anchor `assert 'podman rm -f "$CID"' in code`, so
an empty `runner_code()` cannot satisfy it.

The lane's three self-found DEFECTs are real and its fixes are correct — but **none of the three has a
regression test** (F7, F8, and mutant 35 in item 11): see the survivors table.

---

## Item 10 — the PC gate (the one allowed bridge action)

From a clean detached worktree of the PIN (`git worktree add --detach … 517c65e`, `git status --porcelain`
empty, `HEAD=517c65e5c901101b95ba69516f155796fba8ff24`), patch 0 B:

```
$ bash scripts/pc_suite.sh launch -n 8 -- tests/test_s0_08_containment.py
pc_suite: launched 20260908T033936Z-517c65e on the PC — base 517c65e5c901101b95ba69516f155796fba8ff24
          + patch 0B (sha e3b0c44298fc), set 'tests/test_s0_08_containment.py', -n 8
$ bash scripts/pc_suite.sh wait 20260908T033936Z-517c65e
pytest-exit: 0
pytest-summary: 74 passed in 2.84s
```

**Agrees with the checkpoint's pasted PC line** (`74 passed in 2.73s`, run `20260908T030646Z-545a9ff`) and with
my sandbox baseline (`74 passed in 2.73s` on a minimal archive copy). Worktree removed afterwards; nothing else
touched the bridge.

---

## Item 11 — mutants: 46 distinct (54 runs), 37 killed, 8 genuine survivors, 1 not-applied

Driver: `scratchpad/vg1/mutate.py` — each mutant is a fresh copy of `proofs/S0-08/` + `proofs/schemas/` + the
test file under the scratch dir, one textual mutation, `pytest -q --basetemp=<scratch>`, tree deleted after.
Counts pasted from the runs. All 21 of the lane's named mutants are in the set and all 21 were KILLED.
**Honest arithmetic:** 54 pytest runs over 46 DISTINCT mutants — the first batch's stdout was truncated by a
`tail -60`, so mutants 01-08 were re-run to read their result. 37 killed + 8 survivors + 1 not-applied = 46.

**KILLED (37)** — 01 P1-HOST-KERNEL-ACCEPTED `6 failed, 68 passed` · 02 RUNSC-VERSION-UNPINNED `2 failed, 72 passed` ·
03 SHA-UNPINNED `1 failed, 73 passed` · 04 CANARY-MISSING-IGNORED `8 failed, 66 passed` · 05 P5-SENTINEL-READABLE-ACCEPTED ·
06 P2-MAINUID-ROOT-ACCEPTED · 07 FIFO-EVIDENCE-HANG `3 failed, 71 passed in 123.04s` (the checker really hangs;
the suite's 60 s subprocess timeout is the killer) · 08 MARKER-MALFORMED-PASSES `5 failed, 69 passed` ·
09 MARKER-EXPIRED-PASSES · 10 CRUN-BUNDLE-PASSES · 11 SPEC-REASON-DRIFT · 12 CANARY-VERDICT-IN-SCRIPT ·
13 P3-TOOL-BROKEN-ACCEPTED · 14 P4-SECRETS-ACCEPTED · 15 P4-DOCKER-SOCKET-ACCEPTED · 16 P6-RAW-DEVICES-ACCEPTED ·
17 RECORDED-CANARIES-OPTIONAL · 18 DEFERRAL-SWALLOWS-A-REAL-RUN · 19 VERDICT-WORD-IN-CANARY ·
20 RESULT-PRESENCE-GATE `14 failed, 60 passed` · 21 RESULT-PROOF-ID-IGNORED · 22 CANARY-FIELD-RENAMED ·
23 DUPLICATE-CANARY-ACCEPTED · 24 RC-NONZERO-TRUSTED · 25 UNKNOWN-CANARY-ID-ACCEPTED · 26 P4-COUNT-AGREEMENT-REMOVED ·
27 P5-HOST-CONTROL-READABLE-IGNORED · 28 P5-PATH-BINDING-REMOVED · 29 MARKER-FIFO-HANG `62.78s` ·
30 MARKER-RESULT-FIFO-HANG `62.86s` · 31 MARKER-STATUS-ENUM-REMOVED · 32b RUNNER-NETWORK-HOST (code line) ·
33 RUNNER-PKILL-TEARDOWN · 34 RUNNER-RM-BY-NAME · 36 P6-MOUNT-SIGNATURE-SKIPPED (killed by the
`P6-HOST-PROCFS-ACCEPTED` row — see the survivor note) · 43 CHECKER-P5-SKIPPED · 44 CHECKER-P4-SKIPPED.

**SURVIVORS (8) — every one a real gap**

| # | mutant | result | class |
|---|---|---|---|
| 35 | RUNNER-IMAGE-PIN-REMOVED — `if [ "$actual_commit" != "$PINNED_COMMIT" ]` → `if false` | `74 passed` | **F9** the pinned-image refusal has no test |
| 37 | P3-PIPED-RC-FAIL-OPEN — restore `TOOL_OUT=$("$@" 2>&1 \| head -n 1); TOOL_RC=$?` | `74 passed` | **F8** the lane's own class-18 DEFECT fix is unguarded; no test runs `P3.sh` live |
| 38 | RUNNER-SENTINEL-CONTROL-HARDCODED — `"readable": True` → `"readable": "yes"` | `74 passed` | **F6** the identity generator is untested |
| 39 | P2-FIRST-MATCH-ONLY — drop `[ -n "$main_pid" ] && continue` | `74 passed` | **F2** first-vs-last match is unobservable to the suite |
| 40 | P4-ENV-SOURCE-PROCFS — revert `env` to `/proc/1/environ` | `74 passed` | **F7** the coordinator's P4 fix has no regression test |
| 41 | P6-DEVICE-CENSUS-EMPTY — device list → one nonexistent name | `74 passed` | **F10** the census content is untested — and under F1 the census is the *whole* of P6 |
| 42 | P5-SENTINEL-ALWAYS-NO — `sentinel_readable="yes"` → `"no"` | `74 passed` | **F11** P5's own ability to detect a readable sentinel is untested |
| 45 | P2-MAINCMD-DRIFT — change `MAIN_CMD` in the runner only | `74 passed` | **F12** the runner↔canary contract at `run_containment.sh:41` is unenforced |

**NOT-APPLIED (1)** — 32 RUNNER-NETWORK-HOST as first-occurrence replace hit the explanatory **comment**, not
the code; re-run as 32b against the `RUN_ARGV` line it was killed by
`test_pc_runner_pins_the_verified_runsc_flags`. Recorded so the count is honest.

**Note on 36.** Mutating `if mount_rc == "0":` → `if False:` *is* killed, because the suite's
`P6-HOST-PROCFS-ACCEPTED` row keeps `mount_proc_rc` at `"0"`. The gate is alive for the *source* mutation and
dead for the *input* that the real venue produces — which is exactly why F1 needed a hostile bundle (A5c) and
not a mutant to surface. That asymmetry is the lesson of this round.

### F7 — MEDIUM · the P4 fix's live-binding test passes for the wrong reason on this host

`test_live_canary_output_binds_to_the_fields_the_checker_reads[P4]`
(`tests/test_s0_08_containment.py:629`) plants `"S0_08_LIVE_PROBE_KEY": "not-a-secret"` and then asserts only
`"containment: P4 " in check.stdout`. In the sandbox the checker fails first on
`containment: P4 docker socket present` — so the assertion is satisfied by the docker socket, not by the
planted key, and mutant 40 (P4 reading `/proc/1/environ` again) passes the suite.
Minimal fix: assert the reason **names the planted key**:
`assert "S0_08_LIVE_PROBE_KEY" in check.stdout`. Exact red test: that one line, with mutant 40 applied. SOLID.

---

## Item 12 — discipline

Every `file:line` above was read with `sed -n` on the PIN copy (`git archive 517c65e`), never typed from
memory; every count is pasted from the run that produced it. `report_lint` on **this** report is in the
closing block. Hygiene: I never ran `git stash/checkout/restore/reset/add/commit/push`; the shared tree's
`git status --porcelain` count is unchanged by me (23 entries, all other lanes'), `git stash list` is empty;
the one worktree I added (`git worktree add --detach … 517c65e`) was removed with `git worktree remove --force`.
**One side effect to declare:** that removal also pruned five stale worktree entries (`pc-gate-b5i.wt`,
`-c1`, `-e1`, `-g1`, `-o1`). I checked before writing this: all five directories were **already gone from
disk** — the temp filesystem cleanup had taken them — so only dead bookkeeping was cleared and no lane lost
work. The branch tip moved three times while I worked (`735c0c6` → `68fb454` → `7a848cd`); other lanes are
live, and the shared tree's dirty set is theirs, not mine.
Every mutant and every reproduction ran under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vg1/`, every pytest with an explicit
`--basetemp` under it. Process/mount census after the round: **0** `s0-08` rows in `/proc/self/mountinfo`, no
`runsc` sandbox or gofer processes, no `/tmp/s0-08-p6-proc.*`, no sentinels (mine removed), no `sleep infinity`
of mine (the two I started were killed by pid, plus one stray of my own I found and killed by pid). I killed
nothing I did not start.

`report_lint` on **this** report, same maps:

```
report_lint: 97 refs — OK 43, NEAR 1, MISS 4, UNCHECKABLE 12, UNRESOLVED 37 (at 517c65e)
```

The 4 remaining MISS rows are all **absence claims**, which the heuristic cannot express: three cite
`run_containment.sh:267` while the claim is that `--user` is *not* on that line, and one cites
`G1-report.md:78` — the finding being that the citation *on* that line is wrong. The 37 UNRESOLVED are
references into the pinned hermes-agent checkout, `PROVENANCE.md`, `docs/05_SECURITY.md`, `PC-BRIDGE.md`,
`seeds/`, `scripts/proof-runner` and my own scratch paths, which the four `--map` aliases do not cover;
every hermes-agent reference in this report I read by hand at 527da608 and quoted.

### F16 — LOW · the lane report's FILE IDENTITY table does not describe the shipped bytes

Four of the 18 rows differ at the PIN (the coordinator's later edits):

| file | report says | at 517c65e |
|---|---|---|
| `proofs/S0-08/CONTAINMENT-SPEC.md` | `bb84ed9301ba4b15` / 312 | `4ba53788f9a385dd` / 312 |
| `proofs/S0-08/check_containment.py` | `e6204abbee8626d2` / 299 | `73ab20c3e88a5f0a` / 299 |
| `proofs/S0-08/canaries/P4.sh` | `952aa3cd38532bd4` / 50 | `6967eb755a60be25` / 57 |
| `tests/test_s0_08_containment.py` | `cbcdbca7183ff003` / 751 | `aec5799b95e3d48f` / 757 |

The report's sentence "the gated bytes ARE the shipped bytes" is true of the lane's own PIN `2ff0c31`, not of
`517c65e`. The checkpoint commit message *does* disclose the coordinator's changes and re-pastes both gates, so
nothing is hidden — but a reader who grades the report against the commit will find four mismatches.
Minimal fix: a one-line "amended at 517c65e by the coordinator: <4 files>" note at the top of the identity
table, or a re-stamped table.

---

## Item 13 — the design

**"Canaries observe, the checker judges" holds.** No canary prints a verdict (mutants 12 and 19 killed by the
one-line shape test); a canary line carrying `"verdict": "PASS"` changes nothing (hostile bundle A13); the
checker rejects observations from a canary that reported `rc != 0` (A1). The split is real, not decorative.

**Is the six-property set the right closure of the seed?** The seed's S0-08 block
(`seeds/seed-stage0-v1.yaml:485-488`) asks for four things: root-start/s6 setup then drop to `hermes` under
runsc; required tools work; **escape** canaries FAIL; **host-read** canaries FAIL. The spec's P1 (under
gVisor at all), P2 (drop), P3 (tools), P5 (host read) and P6 (escape) cover them, and P4 adds `docs/05_SECURITY.md:56-72`'s
"narrow mounts, no Docker socket/home/provider secrets" — a superset, correctly justified. P7/P8 are recorded
with their gaps stated inside the artifact rather than left silent; that is the right call and the honest one.

The one place the closure does **not** hold today: the seed's "escape canaries FAIL" was replaced by P6's
containment signature (D3, correctly — gVisor does allow the mount), and that substitute assertion does not
fire under the runtime identity (F1). So the seed's third assertion is currently satisfied in **neither** form.
Fixing F1 restores it.

Two smaller design notes, neither a finding:
- Dropping "ptrace of PID 1 denied" as theatre is the right move (DROP an inapplicable assertion, never rewrite
  it) and is stated in the artifact.
- P2's choice to assert the exact main program's uid rather than "something runs non-root" is the right shape
  (AF-AP-26); it just needs an unambiguous subject (F2).

---

## The findings, in one list

| # | severity | where (at 517c65e) | one line |
|---|---|---|---|
| F1 | **BLOCKER** | `proofs/S0-08/check_containment.py:242` | `if mount_rc == "0":` — P6's containment signature is skipped whenever the mount fails — which is what happens for uid 10000 and for podman's default caps; bundle A5c passes with host PID 1 |
| F2 | **BLOCKER** | `proofs/S0-08/tools/pc/run_containment.sh:42` + `proofs/S0-08/canaries/P2.sh:23` | `MAIN_CMD="sleep infinity"` collides with the image's root `main-hermes` sleeper; P2 picks by glob order — a coin-flip false red |
| F3 | **BLOCKER** | `proofs/S0-08/tools/pc/run_containment.sh:267` | `podman exec -i -e S0_08_SENTINEL_PATH` with no `--user`: canaries run as container root |
| F4 | HIGH | `proofs/S0-08/check_containment.py:136-146` | `runsc_version` / `runsc_sha256` only — the checker binds the evidence to runsc only — never to the image, the source commit or the `run_argv` (A7, A8 pass) |
| F5 | HIGH | `proofs/S0-08/fixtures/evidence-crun/canaries.jsonl:4` | `"secret_env_count":"0"` — a line the shipped `P4.sh` cannot produce (it is the pre-fix procfs reader's output) |
| F6 | MEDIUM | `proofs/S0-08/tools/pc/run_containment.sh:250` | `"sentinel_host_read"` — P5's positive control is the literal `True`, not the measured `SENTINEL_READABLE` (mutant 38 survived) |
| F7 | MEDIUM | `tests/test_s0_08_containment.py:629` | `"S0_08_LIVE_PROBE_KEY": "not-a-secret"` is planted but never named in the assertion — the P4 live-binding test passes on the docker socket, not the planted key; mutant 40 (revert the P4 fix) survived |
| F8 | MEDIUM | `proofs/S0-08/canaries/P3.sh:25-26` | `TOOL_RC=$?` straight after `TOOL_OUT=$("$@" 2>&1)` — the piped-rc fix has no regression test; nothing runs `P3.sh` live (mutant 37 survived) |
| F9 | MEDIUM | `proofs/S0-08/tools/pc/run_containment.sh:83` | `if [ "$actual_commit" != "$PINNED_COMMIT" ]; then` — the pinned-image refusal has no test (mutant 35 survived) |
| F10 | MEDIUM | `proofs/S0-08/canaries/P6.sh:24` | `for dev in /dev/kvm /dev/mem /dev/kmsg` — the census content is untested (mutant 41 survived) — and under F1 it is the whole of P6 |
| F11 | MEDIUM | `proofs/S0-08/canaries/P5.sh:26-27` | `sentinel_readable="yes"` — P5's own detection of a readable sentinel is untested (mutant 42 survived) |
| F12 | MEDIUM | `proofs/S0-08/tools/pc/run_containment.sh:41` | `string; if it changes here it must change in canaries/P2.sh too` — that contract is unenforced (mutant 45 survived) |
| F13 | MEDIUM | `proofs/S0-08/canaries/P1.sh:13` | `dmesg_first=$(dmesg 2>/dev/null | head -n 1) || dmesg_first=""` — the failure is swallowed by the pipeline's rc; empty `dmesg_first_line` with `rc` 0 → an empty-reason red (harmless inside gVisor, measured) |
| F14 | LOW/MED | `proofs/S0-08/spec.json:5-12` + `scripts/proof-runner:181` | positive-leg-first + Deferred means the runner never executes either negative leg while the proof is deferred |
| F15 | LOW | `proofs/S0-08/check_containment.py:257-258` | `for cid in RECORDED:` — a recorded canary with a non-zero rc still satisfies it (A12) |
| F16 | LOW | `tasks/briefs/s0-08-support/G1-report.md:23-24` | `bb84ed9301ba4b15` / `e6204abbee8626d2` — the FILE IDENTITY table describes the lane's PIN, not the shipped bytes (4 of 18 rows) |
| F17 | LOW | `tasks/briefs/s0-08-support/G1-report.md:78`, `:194` | `report_lint` MISS 2 — two citations into the test file drifted by 6 lines |
| F18 | LOW | `proofs/S0-08/tools/pc/run_containment.sh:124` | `--network none` with runsc is unverified on the PC — the verified invocation carries no such flag |
| F19 | INFO | `proofs/S0-08/check_containment.py:130` | `return str(observed[key])` — the coercion accepts JSON ints where strings are expected; every case I built fails closed |
| F20 | INFO | `proofs/S0-08/CONTAINMENT-SPEC.md:192` | `So P6 asserts the **containment signature** instead` — and that substitute is satisfied in neither form until F1 is fixed |
| F21 | INFO | `tests/test_s0_08_containment.py:736` | `assert "pkill" not in code` — of the 7 AF-AP-34 hits, 2 are comments and 5 are bans; none is a call |

---

## VERDICT

**NOT-READY.** Blocking set: **F1, F2, F3.** F4 and F5 should ride the same increment — F4 because the proof
currently asserts nothing about which image produced its evidence, F5 because the negative fixture no longer
matches its producer.

This verdict does **not** depend on anything I failed to reproduce. F1 and F2 were reproduced end to end in the
sandbox; F3 is read from the bytes (`run_containment.sh:267` has no `--user`; `Dockerfile:298` is `USER root`).
The one thing I could not test is whether podman's default capability set would *also* have blocked P6's mount
for a root exec — but that only decides whether F1 fires certainly (uid 10000) or almost certainly (root
without `CAP_SYS_ADMIN`); it does not change the verdict, because F3's fix makes the uid-10000 path the real
one.

Everything the lane built to *judge* evidence is strong: 37 of 46 distinct mutants killed, every spec reason reachable,
the FIFO guards genuinely load-bearing (two mutants hang), the identity pins load-bearing, the marker gate
forgery-resistant, and the canary/checker split real. The lane's three self-found DEFECTs are real and
correctly fixed. What is missing is the step from "the checker judges correctly" to "the canaries can observe
the property as the user the container actually runs".

### The cheapest path to MERGE-READY

One increment, in this order (each step's red test is named above):

1. **F2** — change `MAIN_CMD` to `sleep 2147483647` in `run_containment.sh:42` and `P2.sh:23`; make `P2.sh`
   report all matches and the checker Fail on more than one. (2 files + 1 test.)
2. **F3** — add `--user 10000` at `run_containment.sh:267`, record `canary_exec_user`, assert it. (1 file + 1 test.)
3. **F1** — add the `else` branch to `check_p6` plus the capability-independent second instrument, and update
   `CONTAINMENT-SPEC.md` §P6 to say which signature fires under which capability set. (2 files + 1 test.)
4. **F4** — pin `image_source_commit` and screen `run_argv` in `check_identity`. (1 file + 2 tests.)
5. **F5** — re-capture the crun fixture under `env -i` with the shipped canaries; update `PROVENANCE.md`. (2 files.)
6. Then the cheap regression tests that close the eight survivors: F6, F7, F8, F9, F10, F11, F12 — six of them
   are one assertion each.

F13–F18 can ride the same increment or the next; none blocks the PC run.

### What the coordinator must do on the PC, exactly

Do **not** run the containment run until F1/F2/F3 land — the first run would produce a bundle that passes P6
hollow and reds P2 by coin flip, and re-minting after a fix means re-running the whole thing anyway.

When it lands, in this order:

1. `sha256sum /usr/local/bin/runsc` — must equal
   `048b89aada69dc3333422e139d6e9d02f8ab06bda52398060e0fbdacca00074c` (D5; a mismatch is a two-venue finding,
   not a checker bug), and `runsc --version` must print `release-20260817.0`.
2. Confirm `~/s0-01-pinned/hermes-agent` is at `527da60844d4dced37879ea50259675371abe10e` — the runner exits 2
   otherwise (`run_containment.sh:83`), and that refusal has no test (F9), so check it by hand this once.
3. `bash proofs/S0-08/tools/pc/run_containment.sh` (the runsc leg). Expect the `--network none` + runsc
   combination to be the first thing that can fail (F18); a red there is an environment finding.
4. Sanity-read the bundle before trusting the checker: `canaries.jsonl` must show **P2 `main_uid` `10000`**,
   **P6 `mount_proc_rc`** (whatever it is — record it; it is the F1 evidence either way), and
   `runtime-identity.json`'s `run_argv` must be the three pinned flags with `--network none` and nothing else.
5. `python3 proofs/S0-08/check_containment.py proofs/S0-08/evidence/pc-runsc`.
6. `bash proofs/S0-08/tools/pc/run_containment.sh --runtime crun` for the live negative, then the checker on
   `evidence/pc-crun` — expect `containment: P1 host kernel 6.17.11-200.fc42, not gVisor` (the PC's kernel;
   the committed fixture keeps the sandbox's string, by design — D6).
7. Only then the mint: `result.json`, remove `blocked.json`, flip `proofs/registry.yaml`
   `blocked_host → execution_proof`, regenerate every attested artifact in the same increment (AF-AP-56) and
   gate on `validate-ledger integrity` + `ledger-gen` + `git diff --exit-code proofs/`.
8. Never `podman rm` by name and never `pkill` on that host (AF-AP-34) — the runner is clean on this; keep any
   manual debugging step clean too.
