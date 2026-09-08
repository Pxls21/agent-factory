# Lane G2 — S0-08 containment round 2: the canaries observe as the RUNTIME USER

PIN: `d35960b` · sandbox · report written 2026-09-08T04:28:56Z, amended 2026-09-08T04:5xZ after the
coordinator's PC gate (`date -u`) · contract: VERIFY-G1
(graded at `517c65e`; my scope's bytes are identical at `517c65e` and `d35960b` — `git diff 517c65e d35960b`
over `proofs/S0-08 tests/test_s0_08_containment.py tasks/briefs/s0-08-support/` shows only the VERIFY-G1
brief being added, so every VERIFY-G1 line number resolves at my PIN too).

**TL;DR.** All three blockers and every HIGH/MEDIUM/LOW/INFO finding F1-F20 are closed. Every hostile
bundle VERIFY-G1 built now reds with a named reason, and the baseline still passes. **30/30 mutants
killed** — G1's 21, all eight of VERIFY-G1's survivors (35, 37, 38, 39, 40, 41, 42, 45), and one new
one this round. **186 passed** as root and **122 passed as uid 65534**, four `lane_gate` runs across two
invocations, counts identical. `report_lint` MISS 0.

**The coordinator's PC gate found a real defect in two of MY tests and it is fixed** (§PC GATE FINDING):
they assumed the sandbox's root venue. Both are now derived from a direct probe of the running user, both
arms assert, and the whole S0-08 file passes as an unprivileged uid as well as as root.

**One pinned design item was FALSE against the pinned image and was built differently, loudly**
(§DISCREPANCIES D1): the brief's item 3 says to pin `own_pid1_comm` to the literal `init` and to assert
that P2's `pid1_cmdline` starts with `/init /opt/hermes/docker/main-wrapper.sh`. Both are falsified by the
image's own sources — PID 1 is `s6-svscan` — and building them as written would have produced the exact
class of false red this round exists to remove.

**NOT done, first-class:** the PC containment run (the coordinator's — VERIFY-G1's eight PC steps), the
image build, `podman exec --user 10000` against a live container, and the confirmation of
`sha256sum /usr/local/bin/runsc` on the PC. No bridge, no podman, no container was started by this lane.

---

## FILE IDENTITY (sha256 of the FINAL bytes, `sha256sum | cut -c1-16`)

| sha256 (16) | lines | file |
|---|---|---|
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

(This report is `tasks/briefs/s0-08-support/G2-report.md`; its own sha and line count are omitted
because recording them inside itself would change them. The twelve rows above are the bytes the gate ran on — each
one matches the gate's own identity table line for line, pasted below. **Re-stamped after the PC gate
round**: three files changed — `CONTAINMENT-SPEC.md`, `PROVENANCE.md` and the test file; the other nine
are byte-identical to the first round.)

**In scope and deliberately UNCHANGED** — byte-identical to `517c65e`, verified by `sha256sum` against
`git show 517c65e:<path>`: `canaries/P3.sh` `bac5716ec9cb80ac` · `P5.sh` `db2d6bb50a00bfad` ·
`P6.sh` `53ba2810b75e4531` · `P7.sh` `dd19f775744672b3` · `P8.sh` `851f229a358ccfaf` ·
`marker_gate.py` `093d7412f237ede8` · `blocked.json` `4c6267b8b64b493f` · `probe.json` `d91f8091094c0bd9` ·
`probe_runsc.sh` `bebc21bacf30e650` · `fixtures/malformed-marker/blocked.json` `21f3965de28195f3`.

**Boundary.** `git status --porcelain` lists exactly my 12 files as ` M` plus the other lanes' own
entries (S0-01 lanes P5b/N5i/A5k, `.claude/hooks/edit-snapshot.py`, their untracked files). I ran no
`git stash/checkout/restore/reset/add/commit/push`; `git stash list` is empty. The branch tip moved five
commits during the lane (`d35960b` → `d9334b8`); `git diff --stat d35960b HEAD` over my scope is **empty**,
so none of them touched my files. One stray file of my own (`userpid.txt`, written by a reproduction
command that ran with the repo root as cwd) was removed — `git status` is clean of it.

---

## Item 0 — the premise, verified before any code was written

Every VERIFY-G1 blocker was reproduced on the graded bytes first, from a `git archive 517c65e` copy
(`check_containment.py` sha `73ab20c3e88a5f0a…`, matching VERIFY-G1's F16 table for that commit).

**RED-BEFORE — the hostile bundles against the SHIPPED checker:**

```
A0             exit=0  PASS: S0-08 gvisor-containment - 6 properties asserted over A0
A5b            exit=0  PASS: S0-08 gvisor-containment - 6 properties asserted over A5b
A5c            exit=0  PASS: S0-08 gvisor-containment - 6 properties asserted over A5c
A7             exit=0  PASS: S0-08 gvisor-containment - 6 properties asserted over A7
A8             exit=0  PASS: S0-08 gvisor-containment - 6 properties asserted over A8
A12            exit=0  PASS: S0-08 gvisor-containment - 6 properties asserted over A12
A16-execroot   exit=0  PASS: S0-08 gvisor-containment - 6 properties asserted over A16-execroot
```

**GREEN-AFTER — the same seven bundles against the final checker:**

```
A0             exit=0  PASS: S0-08 gvisor-containment - 6 properties asserted over A0
A5b            exit=1  failure_reason: containment: P6 container PID 1 is systemd, not the image's own s6-svscan
A5c            exit=1  failure_reason: containment: P6 container PID 1 is systemd, not the image's own s6-svscan
A7             exit=1  failure_reason: containment: image_source_commit deadbeef, expected 527da60844d4dced37879ea50259675371abe10e
A8             exit=1  failure_reason: containment: run_argv is missing --network none
A12            exit=1  failure_reason: containment: P7 recorded canary did not observe (rc 7)
A16-execroot   exit=1  failure_reason: containment: canaries were exec'd as uid 0, expected 10000
```

A0 still passing is the de-vacuousing control: every red above is the checker acting on the mutation,
not a bundle the checker can no longer read at all.

**RED-BEFORE — the two-process P2 collision, live on the `517c65e` bytes.** Two processes carrying the
byte-identical cmdline `sleep infinity`, one root and one uid 65534 (the image's real pair is the root
`main-hermes` sleeper and the dropped CMD):

```
--- processes carrying 'sleep infinity':
  pid=31954 uid=0
  pid=32690 uid=65534
--- P2.sh @517c65e verdict, 3 runs:
  run1: main_pid='31954' main_uid='0' proc_count='116'
  run2: main_pid='31954' main_uid='0' proc_count='115'
  run3: main_pid='31954' main_uid='0' proc_count='115'
```

The shipped canary reports the ROOT process's uid on a container where the main program is correctly
dropped — `containment: P2 main program uid 0, expected 10000`, decided by `/proc` glob order.

**GREEN-AFTER** — `test_p2_reports_every_holder_of_the_main_cmdline` (`tests/test_s0_08_containment.py:985`)
starts two processes with one cmdline unique to the test, requires `main_pids` to name **both**, and
requires the checker to answer `containment: P2 main program cmdline is ambiguous (2 processes)`. It is
in the 186.

**RED-BEFORE — the uid-65534 gVisor P6 cell** (`/tmp/runsc --rootless do` + `setpriv --reuid=65534
--regid=65534 --clear-groups`, `/tmp/runsc` at sha `048b89aada69dc33…`, `runsc version release-20260817.0`):

```
{"canary":"P6", … "mount_proc_rc":"32","mount_proc_error":"mount: /tmp/s0-08-p6-proc.2: must be superuser
 to use mount.       dmesg(1) may have more information after failed mount system call.",
 "mounted_pid1_comm":"","mounted_pid_count":"","own_pid1_comm":"sh","own_pid_count":"5",
 "unshare_net_rc":"1","unshare_net_error":"unshare: unshare failed: Operation not permitted","rc":0}
```

The same cell as root (full bounding set) returns `"mount_proc_rc":"0"` with `mounted_pid1_comm":"sh"`.
So the mount really does fail for the runtime user, and on `517c65e` that produced a silent PASS.
**GREEN-AFTER**: the bundle shape above is `test_p6_mount_failure_still_asserts_the_containment_signature` `tests/test_s0_08_containment.py:877`
(passes) and its hostile twin
`test_p6_mount_failure_is_not_a_silent_pass` `tests/test_s0_08_containment.py:887` (exit 1, named reason).

---

## PC GATE FINDING — two of my own tests assumed the sandbox's root venue

The coordinator's PC gate on my first-round bytes was **RED**: `2 failed, 120 passed in 4.23s`
(run `20260908T044128Z-1c8ec05`, 8 workers). The PC runs pytest as uid 1000 with
`/proc/sys/kernel/dmesg_restrict` = 1; the sandbox runs it as root. **The AF-AP-4 class, in my own test
file** — a venue probed on one host and asserted about the world.

**The cause is my F13 fix working exactly as designed.** On the PC,
`sh proofs/S0-08/canaries/P1.sh` → `{"canary":"P1", … "dmesg_first_line":"", "rc":1}`: `dmesg` is refused
to the unprivileged user and P1 now reports that in `rc` instead of swallowing it in a pipeline. Two of my
tests had the sandbox's answer baked in.

**Reproduced here before fixing anything**, by running the suite as uid 65534 on this host (where
`dmesg_restrict` is also 1). The pre-fix bytes, same two tests:

```
E  AssertionError: P1.sh no longer emits a field the checker reads: failure_reason: containment: P1 canary did not complete its observation (rc 1)
E  assert 'observation' not in 'failure_rea...ion (rc 1)\n'
E    'observation' is contained here:
E      plete its observation (rc 1)
E  AssertionError: P1
E  assert 0 == 1
FAILED tests/test_s0_08_containment.py::test_live_canary_output_binds_to_the_fields_the_checker_reads[P1-containment: P1 host kernel ]
FAILED tests/test_s0_08_containment.py::test_crun_fixture_is_producible_by_the_shipped_canaries
2 failed, 2 passed in 1.13s
```

**A third defect the PC log did not name, visible in that trace.** The class-14 rename guard was
`assert "observation" not in check.stdout` — and `did not complete its observation (rc 1)` contains that
bare word, so on any venue where a canary cannot observe, the rename guard fires for the wrong reason.
The detector is now the precise marker
`assert "observation '" not in check.stdout` `tests/test_s0_08_containment.py:689` — the message it is
really looking for is `containment: <Pn> observation '<name>' absent`, and the quote is what
distinguishes them.

### The fix: derive the expectation from the venue, assert both arms, skip nothing

A direct probe, not a prediction: `dmesg_works()` (`tests/test_s0_08_containment.py:52`) runs `dmesg` and
reads its status, because `os.geteuid()` + `dmesg_restrict` alone would mispredict a caller holding
`CAP_SYSLOG` and there is no such knob inside gVisor at all.
`def venue() -> str:` `tests/test_s0_08_containment.py:63` renders euid, the knob and the probe into
every assertion message, so a future red says which arm it took and why.

1. **The live-binding test.** P1's `rc` must equal
   `0 if dmesg_works() else 1` `tests/test_s0_08_containment.py:699` — its status must TRACK the real
   capability, which is the F13 property itself and is now pinned on both venues. When the canary could
   not observe, the checker must refuse the line by name:
   `canary did not complete its observation` `tests/test_s0_08_containment.py:706`. The field binding is
   then still proven by re-running with the canary's OWN STATUS forced to 0 and every OBSERVATION
   untouched — `observed_live = dict(live, rc=0)` `tests/test_s0_08_containment.py:714` — so the class-14
   guard survives on a venue where P1 cannot read dmesg, instead of being masked by the rc gate.
2. **The fixture test.** The committed line's status is asserted unconditionally:
   `committed[canary]["rc"] == 0` `tests/test_s0_08_containment.py:1484` — it was captured by a canary
   that observed. The LIVE P1's status is derived:
   `0 if readable else 1` `tests/test_s0_08_containment.py:1497`, with the boot line non-empty or empty
   to match. The other seven canaries keep the unconditional `rc == 0`. P1's boot-line comparison moved
   into the same-host block and is further gated on readability.

### The real containment run is unaffected — stated where it matters

Inside gVisor there is no `/proc/sys/kernel/dmesg_restrict` and `syslog(2)` is not gated on `CAP_SYSLOG`:
VERIFY-G1 measured `dmesg` working for uid 65534 and for root with `-syslog` dropped inside a runsc
sandbox. So P1 observes normally as the runtime user in the venue this proof actually runs in. That is
now written down twice. In the spec, beside the property —
`is the canary's own status, and for P1 it depends on the RUNNING USER` `proofs/S0-08/CONTAINMENT-SPEC.md:145`
— and in the fixture's provenance, beside the venue table:
`The real containment run is unaffected` `proofs/S0-08/fixtures/evidence-crun/PROVENANCE.md:74`.

### Verified on both venues

```
$ pytest tests/test_s0_08_containment.py -q                                  → 122 passed  (root)
$ setpriv --reuid=65534 --regid=65534 --clear-groups python3 -m pytest \
      tests/test_s0_08_containment.py -q                                     → 122 passed  (uid 65534)
```

The whole file, not just the two tests: no other test in it assumes root. (The non-root run needs a
world-executable interpreter and a world-traversable basetemp — `/root/venv-agent-factory` and
`/tmp/claude-0` are both `0700`, the same traversal block AF-AP-56's note names — so it used
`/usr/local/bin/python3` and a temp dir under `/tmp`, removed afterwards.)

---

## What was built, item by item

### 1 · F2/F12 — an unambiguous main program, one source, loud ambiguity

- `MAIN_CMD="sleep 2147483647"` (`proofs/S0-08/tools/pc/run_containment.sh:57`). The `:41` "must change in
  canaries/P2.sh too" contract is **gone**: the runner passes the same string to the canary as
  `-e S0_08_MAIN_CMDLINE="$MAIN_CMD"` (`proofs/S0-08/tools/pc/run_containment.sh:313`) and `P2.sh` reads
  `MAIN_CMDLINE="${S0_08_MAIN_CMDLINE:-}"` (`proofs/S0-08/canaries/P2.sh:27`) with **no default** —
  unset is `rc=1` (`proofs/S0-08/canaries/P2.sh:56`), never an invented subject. The readiness gate and
  the identity scan read the same shell variable, pinned by
  `test_runner_and_p2_share_one_source_for_the_main_cmdline` (`tests/test_s0_08_containment.py:1015`).
- `P2.sh` collects ALL matches: `proofs/S0-08/canaries/P2.sh:49` is `main_pids=` and
  `proofs/S0-08/canaries/P2.sh:50` is `main_uids=`; the first-match short-circuit is gone.
- The checker refuses an ambiguous set by name:
  `main program cmdline is ambiguous` `proofs/S0-08/check_containment.py:264`. It catches a disagreement at
  `proofs/S0-08/check_containment.py:267` (`len(main_pids) != len(main_uids)`), and asserts the ONE uid
  is `HERMES_UID`.

### 2 · F3 — the canaries run as the runtime user, and that is recorded and asserted

- `podman exec -i --user "$CANARY_EXEC_UID"` (`proofs/S0-08/tools/pc/run_containment.sh:311`), with
  `CANARY_EXEC_UID="10000"` (`proofs/S0-08/tools/pc/run_containment.sh:64`).
- `podman exec`'s OWN status is checked, with no pipeline between the command and `$?`:
  `exec_rc=$?` (`proofs/S0-08/tools/pc/run_containment.sh:315`), then the last line is taken from the
  captured text. A canary that dies after printing is no longer indistinguishable from one that succeeded.
- The uid is recorded:
  `"canary_exec_user": val("canary_exec_user")` `proofs/S0-08/tools/pc/run_containment.sh:286`, pinned at
  `proofs/S0-08/check_containment.py:230` (`if exec_user != CANARY_EXEC_UID:`).
- The spec and the canary now match the runner:
  `podman exec --user 10000` `proofs/S0-08/canaries/P4.sh:24`, named as the override of the image default.
- P3 keeps working because the image's shim short-circuits for a non-root caller
  (`docker/hermes-exec-shim.sh:54`, read at `527da608`) — cited in the spec's §1 table.

### 3 · F1 — P6 asserts under the capability set the runtime user HAS

`check_p6` now asserts a capability-INDEPENDENT signature in **both** branches, and only compares the
mounted procfs when the mount could actually run:

| assertion | where |
|---|---|
| PID 1 is the image's supervision root — `CONTAINER_INIT_COMM` | `proofs/S0-08/check_containment.py:356` |
| P2's independently-read comm agrees — `p2_comm != own` | `proofs/S0-08/check_containment.py:364` |
| the count is a count — `own_count.isdigit()` | `proofs/S0-08/check_containment.py:370` |
| and is under `CONTAINER_MAX_PIDS` | `proofs/S0-08/check_containment.py:374` |
| mount succeeded → `mounted != own` is refused | `proofs/S0-08/check_containment.py:388` |
| mount failed → `mount -t proc failed with rc` and no reason | `proofs/S0-08/check_containment.py:395` |

The bound is `CONTAINER_MAX_PIDS = 32` (`proofs/S0-08/check_containment.py:86`) and it is **derived, with
the derivation stated in the constant's own comment and in the spec's §P6**: s6-svscan (1) +
s6-linux-init's supervised shutdownd (2) + one `s6-supervise` per declared user service and its child —
`docker/s6-rc.d/user/contents.d/` declares exactly two, `main-hermes` and `dashboard` (4) + the main
program (1) + the canary's shell and its command substitutions (~4) ≈ 12 at steady state; 32 is ~2.5×
headroom. What it excludes is a host process table: **115** measured on the sandbox host while this was
derived, **5** inside the real gVisor cell above.

### 4 · F4 — the evidence is bound to its image and its argv

`check_identity` pins five things, not two: the runsc version and sha256 (unchanged), plus
`proofs/S0-08/check_containment.py:208` `PINNED_IMAGE_SOURCE_COMMIT`;
`proofs/S0-08/check_containment.py:221` `run_argv is missing` for a required pair;
`proofs/S0-08/check_containment.py:223` `banned in argv`;
`proofs/S0-08/check_containment.py:226` every `--network` value must be `none`; and
`proofs/S0-08/check_containment.py:230` `if exec_user != CANARY_EXEC_UID:`. The screen is an
**exact-token screen over the recorded list**.
`REQUIRED_RUN_ARGV_PAIRS` `proofs/S0-08/check_containment.py:59` is checked as adjacent pairs;
`BANNED_RUN_ARGV_TOKENS` `proofs/S0-08/check_containment.py:64` by membership. Never a substring over
a joined string, because `--network host` is two tokens and a substring screen also matches
`--network hostile`. A wrong-typed argv is named, not coerced:
`run_argv is not a list of strings` `proofs/S0-08/check_containment.py:218`.

### 5 · F5 — the crun fixture is producible by the shipped canaries

Re-captured with the shipped canaries under `env -i PATH=/usr/bin:/bin`, from the repo root, with the two
canaries that need an input given it explicitly. `PROVENANCE.md` carries the exact command, the venue
(`6.18.44-fc-v24`, the sandbox) and a table of **which values depend on the host and which on the
capture**.
`test_crun_fixture_is_producible_by_the_shipped_canaries` `tests/test_s0_08_containment.py:1470`
re-runs it and requires at
`tests/test_s0_08_containment.py:1483` that `set(committed[canary]["observed"])` equal the live one
(venue-independent); `secret_env_count` `"0"`, `secret_env_keys` `""` and
`sentinel_readable` `"yes"` to match (capture-determined, venue-independent); and the host-dependent
values (`docker_sock`, `dangerous_devices`, `dev_entries`, `home_entries`) only when the re-run is on the
capture host, detected from `uname_r` — stated in the test and in `PROVENANCE.md`, never a silent skip.
The negative leg still prints exactly the reason `spec.json` pins.

### 6 · the eight survivors, each with its killer

| # | survivor | closed by |
|---|---|---|
| 35 | RUNNER-IMAGE-PIN-REMOVED | the preflight extracted to `s0_08_require_pinned_source` (`proofs/S0-08/tools/pc/run_containment.sh:103`), driven against a scratch git repo by `test_runner_refuses_a_source_checkout_at_the_wrong_commit` (`tests/test_s0_08_containment.py:1417`) with a positive control at the repo's own commit |
| 37 | P3-PIPED-RC-FAIL-OPEN | `test_p3_records_a_failing_tools_own_status` (`tests/test_s0_08_containment.py:1247`) runs `P3.sh` live against a stand-in that prints a line and exits 3 |
| 38 | RUNNER-SENTINEL-CONTROL-HARDCODED | `proofs/S0-08/tools/pc/run_containment.sh:291` emits `val("sentinel_readable") == "true"`, fed by `proofs/S0-08/tools/pc/run_containment.sh:245` (`$SENTINEL_READABLE` written to `$META`); tested by `tests/test_s0_08_containment.py:1360` `test_identity_generator_emits_the_measured_sentinel_read` |
| 39 | P2-FIRST-MATCH-ONLY | item 1 + the live two-process test |
| 40 | P4-ENV-SOURCE-PROCFS | the P4 live-binding assertion now NAMES the planted key: `tests/test_s0_08_containment.py:735` is `assert "S0_08_LIVE_PROBE_KEY" in env_check.stdout` |
| 41 | P6-DEVICE-CENSUS-EMPTY | `test_p6_device_census_names_the_hosts_raw_devices` (`tests/test_s0_08_containment.py:1276`) — `/dev/kmsg` is present on this host (`crw-r--r-- 1 root root 1, 11 /dev/kmsg`) |
| 42 | P5-SENTINEL-ALWAYS-NO | `test_p5_detects_a_readable_sentinel_and_the_checker_refuses_it` (`tests/test_s0_08_containment.py:1295`), with a not-written negative control |
| 45 | P2-MAINCMD-DRIFT | `test_runner_main_cmd_does_not_collide_with_the_images_root_sleeper` (`tests/test_s0_08_containment.py:1028`) — the value is load-bearing, not arbitrary: `sleep infinity` IS the image's root no-op |

### 7 · F13-F19

- **F13** `proofs/S0-08/canaries/P1.sh:19` is `dmesg_all=$(dmesg 2>/dev/null); dmesg_rc=$?` with no
  pipeline, and `:24` sets `rc=1` on failure. Tested venue-independently with a `dmesg` stand-in that
  exits 1, plus a working stand-in as the negative control
  (`test_p1_records_a_failing_dmesg_as_not_observed`, `tests/test_s0_08_containment.py:1225`) — the
  `dmesg_restrict` route is pasted below as live evidence but is not what the test depends on.
- **F14** the two negative legs are FIRST in `proofs/S0-08/spec.json`.
  `test_proof_runner_executes_both_negative_legs_before_deferring` (`tests/test_s0_08_containment.py:1566`)
  drives the real `scripts/proof-runner` on a scratch copy three times: shipped order → exit 2 deferred,
  no artifact; first negative leg's fixture broken → **exit 1 `negative-control-unmet: S0-08`**, proving
  the leg executed; the same broken fixture with the positive leg restored to first → exit 2 again, which
  is the state `517c65e` shipped.
- **F15** `check_recorded` refuses a recorded canary that never observed:
  `proofs/S0-08/check_containment.py:406` is `if canaries[cid]["rc"] != 0:`.
- **F16/F17** the G1 report's identity table carries an amendment naming the four drifted rows, stating
  that every `file:line` in it resolves against `517c65e`, and warning that lane G2 rewrote nine of those
  files; the two `+6` citations are corrected.
- **F18** the `UNVERIFIED ON THE PC` note is at `proofs/S0-08/tools/pc/run_containment.sh:31` and in
  the spec's §6.
- **F19** `_field` names the type instead of coercing it:
  `if not isinstance(value, str):` `proofs/S0-08/check_containment.py:180`.
- **F20** the spec's §P6 now carries the capability-set table: which signature fires for which caller.

---

## DISCREPANCIES with the brief (loud)

**D1 — BLOCKING, and the one that mattered: item 3's pinned literals are FALSE.** The brief says to
"derive the expected comm from the image: PID 1 is `/init` from `docker/entrypoint-dispatch.sh:18` — READ
it, pin the literal in the checker" and to assert "P2's `pid1_cmdline` starts with
`/init /opt/hermes/docker/main-wrapper.sh`". I read it, and both are falsified by the pinned sources:

1. `docker/entrypoint-dispatch.sh:18` does exec `/init` — but s6-overlay's `/init` **execs away in its
   own first act**. I fetched the exact release tarball the Dockerfile pins
   (`s6-overlay-noarch.tar.xz` v3.2.3.0), verified its sha256 against the Dockerfile's
   `S6_OVERLAY_NOARCH_SHA256`
   (`b720f9d9340efc8bb07528b9743813c836e4b02f8693d90241f047998b4c53cf` — an exact match, so this IS the
   artifact the image installs), and read the file: `/init` ends with
   `exec s6-overlay-suexec … /package/admin/s6-overlay-3.2.3.0/libexec/stage0`, and `stage0` ends with
   `exec "$basedir/bin/init"` — the s6-linux-init stage 1.
2. The image states the destination itself: `Dockerfile:68` reads
   "replaces tini with s6-overlay's /init (PID 1 = s6-svscan)".

So `own_pid1_comm` is **`s6-svscan`**, and PID 1's cmdline is s6-svscan's, not `/init …main-wrapper.sh`.
Building the brief as written would have produced a **guaranteed** false red on a correctly contained
container — the exact class this round exists to remove (VERIFY-G1 F2).

What I built instead: `CONTAINER_INIT_COMM = "s6-svscan"` (`proofs/S0-08/check_containment.py:76`) with
the derivation in the constant's comment and in the spec's §1; the `pid1_cmdline` assertion **DROPPED**
rather than rewritten (anti-hollow-green tactic 4 — drop an inapplicable assertion), with P2 still
recording it; and its place as the brief's "second instrument" taken by two replacements that ARE
derivable. First, `proofs/S0-08/check_containment.py:364` is `if p2_comm != own:` — P2 read the same
PID 1 in its own process. Second, the table is bounded by
`CONTAINER_MAX_PIDS` `proofs/S0-08/check_containment.py:374`.

**Residual risk, stated rather than hidden.** The last hop — s6-linux-init stage 1 exec'ing `s6-svscan` —
is the only one not read from a sha-pinned artifact (that script is generated at boot by
`s6-linux-init-maker`), so it rests on `Dockerfile:68` plus s6's documented architecture. It is INFERRED,
not reproduced: no container was started. The spec says what to do if the first PC run disagrees — a
different **s6-overlay** process name is a pin finding to correct in the spec; a **host** init name
(`systemd`, `init`) in the same field is a containment failure. The failure is closed and named either
way; the old behaviour was a silent pass.

**D2 — a deliberate strengthening beyond item 3.** The brief scopes the new assertions to the `else`
branch. I hoisted the three capability-independent ones so they fire in **both** branches. Leaving them in
the `else` only would have meant a bundle with `mount_proc_rc "0"` and `mounted_pid1_comm == own_pid1_comm
== "systemd"` still passing P6 — the same asymmetry in the other branch. The `else` still gets everything
the brief asked for, plus the mount-error requirement.

**D3 — item 6/F9's function signature.** The brief writes `s0_08_require_pinned_source <dir>`. I gave it
**two** parameters, `<dir> <expected-commit>`:
`s0_08_require_pinned_source() {` `proofs/S0-08/tools/pc/run_containment.sh:103`. Because a
one-argument form can only be exercised against the real pinned commit, and no test can forge a git sha to
build a POSITIVE control. With two parameters the test drives a refusal AND an acceptance against the same
scratch repo, and a separate assertion pins that the runner calls it with `$PINNED_COMMIT`
(`test_runner_calls_the_preflight_with_the_pinned_commit`, `tests/test_s0_08_containment.py:1442`).

**D4 — item 6/F5's "host-independent values".** The brief names `secret_env_count`, `docker_socket` and
"the device census" as host-independent. `docker_sock` and the device census are **not** venue-independent
— this suite also runs on the PC — so comparing them unconditionally would red there. They are compared
under a measured same-host guard; `secret_env_count`/`secret_env_keys`/`sentinel_readable` are compared
unconditionally because the `env -i` capture, not the host, determines them. Stated in the test and in
`PROVENANCE.md`.

**D5 — item 6/F11's reason string.** The brief writes `P5 host control path readable`. The checker's real
reason is `containment: P5 host sentinel readable inside the container`; the test asserts the real one.

**D6 — scope.** The brief's Scope paragraph limits `G1-report.md` to "ONLY the identity-table note, F16",
but design item 7 also assigns **F17** (the two drifted refs), which live in that same file. I did both
and touched nothing else in it.

**D7 — the F13 test's venue.** The brief asks for the `dmesg` test "under `su -s /bin/sh nobody` (or
`setpriv`) on the sandbox host where `dmesg_restrict=1`". That result depends on the venue's
`kernel.dmesg_restrict`, so the committed test drives a `dmesg` stand-in — the same code path,
venue-independent, with a working-stand-in negative control. **This deviation was right for that test and
wrong as a general habit**: I applied it to the one test the brief named and left two OTHER tests holding
the sandbox's root answer, which is what the PC gate found (§PC GATE FINDING). Those two now derive their
expectation from `dmesg_works()` and assert both arms. The live `setpriv` run below is evidence in this
report, not a test the suite depends on:

```
$ cat /proc/sys/kernel/dmesg_restrict        → 1
$ setpriv --reuid=65534 --regid=65534 --clear-groups sh proofs/S0-08/canaries/P1.sh
{"canary":"P1", … "dmesg_first_line":"", … "rc":1}
```

**D8 — the scratch directory.** The brief names `…/scratchpad/g2/`. A stale 10-byte file from 2026-09-03
(content `39 passed`) already occupies that exact path. Rather than move or delete something I did not
create in a shared scratchpad, I used `…/scratchpad/g2lane/` for everything, including `LANE_GATE_DIR`.

---

## The mutant table — 30 run, 30 KILLED, 0 survived

Driver: a fresh copy of `proofs/S0-08` + `proofs/schemas` + `proofs/registry.yaml` +
`scripts/proof-runner` + `scripts/validate-ledger` + the test file under the scratch dir, ONE textual
mutation, `pytest -x -q --basetemp=<scratch>`, tree deleted after. Counts and killer lines pasted from the
runs. The shared tree was never mutated.

| # | mutant | result | killer line |
|---|---|---|---|
| 01 | P1-HOST-KERNEL-ACCEPTED | `1 failed in 0.26s` | `assert 'failure_reas...PT_DYNAMIC @0' == 'failure_reas...4, not gVisor'` |
| 02 | RUNSC-VERSION-UNPINNED | `1 failed, 20 passed in 0.92s` | `AssertionError: assert 0 == 1` |
| 03 | SHA-UNPINNED | `1 failed, 21 passed in 0.92s` | `AssertionError: assert 0 == 1` |
| 04 | CANARY-MISSING-IGNORED | `1 failed, 23 passed in 0.98s` | `assert 'containment: P1 canary line absent' in "failure_reason: containment: P1 observation 'uname_r' absent\n"` |
| 05 | P5-SENTINEL-READABLE-ACCEPTED | `1 failed, 12 passed in 0.68s` | `P5-SENTINEL-READABLE-ACCEPTED survived: PASS: S0-08 gvisor-containment - 6 properties asserted over pc-runsc` |
| 06 | P2-UID-ROOT-ACCEPTED | `1 failed, 8 passed in 0.55s` | `P2-UID-ROOT-ACCEPTED survived: PASS: S0-08 gvisor-containment - 6 properties asserted over pc-runsc` |
| 07 | FIFO-EVIDENCE-HANG | `1 failed, 38 passed in 61.56s` | `subprocess.TimeoutExpired` — the checker really hangs; the 60 s timeout is the killer |
| 08 | MARKER-MALFORMED-PASSES | `1 failed, 42 passed in 1.64s` | `assert 'marker: expi...roof must run' == 'marker: malformed: probe_run'` |
| 09 | MARKER-EXPIRED-PASSES | `1 failed, 44 passed in 1.69s` | `AssertionError: assert 0 == 1` |
| 10 | CRUN-BUNDLE-PASSES | `1 failed in 0.25s` | `assert 'failure_reas...PT_DYNAMIC @0' == 'failure_reas...4, not gVisor'` |
| 11 | SPEC-REASON-DRIFT | `1 failed in 0.26s` | `assert 'failure_reas...4, not gVisor' == 'failure_reas... wrong kernel'` |
| 12 | CANARY-VERDICT-IN-SCRIPT | `1 failed, 60 passed in 2.07s` | `AssertionError: P1 emitted 2 lines` |
| 13 | P3-TOOLS-BROKEN-ACCEPTED | `1 failed, 10 passed in 0.59s` | `P3-TOOL-BROKEN-ACCEPTED survived: PASS: S0-08 gvisor-containment - 6 properties asserted over pc-runsc` |
| 14 | P4-SECRETS-ACCEPTED | `1 failed, 18 passed in 0.84s` | `AssertionError: assert 0 == 1` |
| 15 | P6-RAW-DEVICES-ACCEPTED | `1 failed, 13 passed in 0.69s` | `P6-RAW-DEVICE-ACCEPTED survived: PASS: S0-08 gvisor-containment - 6 properties asserted over pc-runsc` |
| 16 | RECORDED-CANARIES-OPTIONAL | `1 failed, 29 passed in 1.15s` | `AssertionError: assert 0 == 1` |
| 17 | DEFERRAL-SWALLOWS-A-REAL-RUN | `1 failed in 0.25s` | `AssertionError: deferred: containment evidence not captured` |
| 18 | VERDICT-WORD-IN-CANARY | `1 failed, 61 passed in 2.01s` | `AssertionError: P2 emitted 2 lines` |
| 19 | RESULT-PRESENCE-GATE | `1 failed, 54 passed in 62.08s` | `subprocess.TimeoutExpired` — the marker gate hangs on a FIFO without the guard |
| 20 | RESULT-PROOF-ID-IGNORED | `1 failed, 53 passed in 1.92s` | `AssertionError: assert 0 == 1` |
| 21 | CANARY-FIELD-RENAMED | `1 failed, 65 passed in 2.26s` | `P1.sh no longer emits a field the checker reads: failure_reason: containment: P1 observation 'uname_r' absent` |
| **35** | RUNNER-IMAGE-PIN-REMOVED | `1 failed, 117 passed in 4.68s` | `AssertionError: ACCEPTED` (the refusal accepted a wrong-commit checkout) |
| **37** | P3-PIPED-RC-FAIL-OPEN | `1 failed, 112 passed in 4.01s` | `AssertionError: {'canary': 'P3', … 'hermes_rc': …}` — `node_rc` read `0` for a tool that exited 3 |
| **38** | RUNNER-SENTINEL-CONTROL-HARDCODED | `1 failed, 115 passed in 4.30s` | `AssertionError: {'canary_exec_user': '10000', …}` — `readable` stayed true for `SENTINEL_READABLE=false` |
| **39** | P2-FIRST-MATCH-ONLY | `1 failed, 86 passed in 3.19s` | `AssertionError: {'canary': 'P2', 'expect': 'pid 1 uid 0 running s6 init; exactly one process has the main cmdline …'}` — one pid reported, two started |
| **40** | P4-ENV-SOURCE-PROCFS | `1 failed, 67 passed in 2.58s` | `AssertionError: PASS: S0-08 gvisor-containment - 6 properties asserted over pc-runsc-env` |
| **41** | P6-DEVICE-CENSUS-EMPTY | `1 failed, 113 passed in 4.23s` | `assert '/dev/kmsg' in ['']` at `tests/test_s0_08_containment.py:1283` |
| **42** | P5-SENTINEL-ALWAYS-NO | `1 failed, 114 passed in 4.40s` | `AssertionError: {'canary': 'P5', 'expect': 'the host sentinel is UNREADABLE inside the container', …}` |
| **45** | P2-MAINCMD-DRIFT | `1 failed, 87 passed in 3.54s` | `assert 'MAIN_CMD="sleep 2147483647"' in 'set -euo pipefail…'` |
| **46** | P1-PIPED-RC-FAIL-OPEN — NEW this round: restore `dmesg_first=$(dmesg 2>/dev/null \| head -n 1); dmesg_rc=$?` | `1 failed, 111 passed in 4.16s` | `AssertionError: {'canary': 'P1', 'expect': 'uname -r is 4.19.0-gvisor …'}` — killed by the `dmesg` stand-in test on a ROOT venue too, so the F13 fix is guarded venue-independently |

```
TOTAL: 30 killed, 0 survived
```

Re-run in full after the PC-gate venue fix, because a change to the test file can resurrect a survivor.
Mutant **46 is new this round**: it restores P1's piped-rc fail-open, the defect F13 fixed. It matters
that it dies on a ROOT venue — where `dmesg` works and the live canary alone cannot tell the two versions
apart — which it does, through the `dmesg` stand-in in
`test_p1_records_a_failing_dmesg_as_not_observed`. Had that test been written the way the brief asked
(a real `setpriv` run), this mutant would have survived every sandbox run and been caught only on the PC.

---

## The gates, pasted

**`lane_gate.sh`, two invocations, four runs, static `git archive d35960b` copies with exactly my
working-tree files on top:**

```
RESULT: rev=d35960bb276e files=12 runs=2 identical=yes rc=0 summary="186 passed in 17.07s 186 passed in 16.57s"
RESULT: rev=d35960bb276e files=12 runs=2 identical=yes rc=0 summary="186 passed in 16.86s 186 passed in 16.88s"
```

(The first round's two RESULT lines, on the pre-PC-gate bytes, were
`186 passed in 17.10s 186 passed in 16.88s` and `186 passed in 16.65s 186 passed in 16.69s` — the same
counts; the venue fix is test-side and changes no count on a root venue, which is precisely why the
sandbox gate could not have caught it.)

(test set: `tests/test_s0_08_containment.py tests/test_spec_probe_schemas.py tests/test_validate_ledger.py
tests/test_proof_runner.py`. Counts pasted from `scripts/test_summary.sh`, never typed.)

**Adjacent consumers** (not in the brief's gate set; run because the `spec.json` leg reorder could have
reached them):

```
$ pytest tests/test_ledger_gen.py -q          → 11 passed in 2.50s
$ python3 scripts/validate-ledger integrity --root .   → rc 0, S0-12 PRESENT, no INVALID
$ git diff --stat proofs/ledger.json          → empty
```

And the coordinator's wider set, re-run here after the venue fix — the gate set plus the two ledger
consumers, matching the `197 ×2` the coordinator measured:

```
$ pytest tests/test_s0_08_containment.py tests/test_spec_probe_schemas.py \
      tests/test_validate_ledger.py tests/test_proof_runner.py tests/test_ledger_gen.py -q
197 passed in 19.38s
```

S0-08 has no minted `result.json` (it is still `blocked_host`), so its `spec.json` is not an attested
input of any existing artifact and AF-AP-56's regeneration gate does not fire for this change. The four
denominators are unchanged: `blocked_credential 0/1`, `blocked_host 0/1`,
`conformance_checked_decision 3/3`, `execution_proof 2/7`.

**Syntax and screens:**

```
$ bash -n proofs/S0-08/tools/pc/run_containment.sh          → OK
$ sh -n proofs/S0-08/canaries/P{1..8}.sh                    → OK (all eight)
$ python -m pyflakes check_containment.py test_s0_08_containment.py   → rc=0, no output
$ python3 scripts/ap_screen.py proofs/S0-08 proofs/S0-08/tools/pc
--- AP_SCREEN over 2 path(s): 0 hits over 2 files ---       rc=0
$ python3 scripts/ap_screen.py --tests tests/test_s0_08_containment.py
--- TEST_SCREEN over 1 path(s): 8 hits over 1 files ---  AF-AP-34: 8    rc=0
```

**`report_lint` on THIS report, MISS 0:**

```
$ python3 scripts/report_lint.py tasks/briefs/s0-08-support/G2-report.md \
    --map C=proofs/S0-08/check_containment.py \
    --map T=tests/test_s0_08_containment.py \
    --map R=proofs/S0-08/tools/pc/run_containment.sh
report_lint: 81 refs - OK 81, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```

Every `file:line` in this report was produced by `grep -n` / `sed -n` on the FINAL bytes, and the lint
resolves all 81 against the working tree. **The PC-gate round moved every line number in the test file by
+81, and the lint caught all 22 stale citations** — they were re-resolved against the final bytes rather
than adjusted by arithmetic. The references into the pinned hermes-agent checkout
(`Dockerfile`, `docker/…`) and into `PC-BRIDGE.md` are quoted from the sources named beside them; the
five `--map` aliases do not cover the hermes-agent tree, so those are quoted rather than cited by alias.

The 8 AF-AP-34 hits are G1's 7 (2 comments, 5 assertions that BAN the token) plus one new comment of mine
at `tests/test_s0_08_containment.py:1005`, which reads `child.kill()` with a comment naming the ban. None
is a call: the only process termination this lane performs is `subprocess.Popen.kill()` on handles it
created.

---

## The 18-class self-sweep over my own files

| class | instances | verdict | the run |
|---|---|---|---|
| 1 presence-gated | 46 conditionals in the checker | **CLOSED — the class VERIFY-G1 regraded** | every conditional's body raises a NAMED `Failure`, with exactly one exception: `if mount_rc == "0":` (`proofs/S0-08/check_containment.py:384`), which now has an `elif` that raises (`:393`), and whose capability-independent siblings were hoisted ABOVE it (`:356`, `:364`, `:374`) so both branches assert. Enumerated mechanically with `grep -n '^\s*\(el\)\?if .*:\s*$'` over the final bytes |
| 2 reads outside walk / no `S_ISREG` | 5 | SAFE | unchanged from G1; mutants 07 and 19 still hang without the guards |
| 2b canary `/proc` + `/sys` reads | 12 | DOCUMENTED-LIMIT | pseudo-files by design; the rule binds evidence paths |
| 3 stale `[-1]` / `tail -n 1` | 1 | **CLOSED** | `proofs/S0-08/tools/pc/run_containment.sh:315` is `exec_rc=$?` — the exec's OWN status, read before the last line is taken; VERIFY-G1's caveat ("a canary that dies after printing is indistinguishable") no longer holds |
| 4 negative acceptance | 12 | SAFE | the pkill/host-network bans keep `test_runner_code_filter_actually_removes_comments`; my new banned-substring scan over `P2.sh` has its own negative control, `test_canary_code_filter_actually_removes_comments` (`tests/test_s0_08_containment.py:1196`) |
| 5 substring / tail anchors | ~40 | SAFE | every outcome classified by an EXACT `returncode`; the substring only names the reason |
| 6 env-domain fail-opens | 2 | SAFE | `proofs/S0-08/canaries/P5.sh:20` reads `S0_08_SENTINEL_PATH` and `proofs/S0-08/canaries/P2.sh:27` reads `MAIN_CMDLINE="${S0_08_MAIN_CMDLINE:-}"`. Both have NO default and both set `rc=1` when unset; both are RUN unset in the suite — `tests/test_s0_08_containment.py:381` `test_p5_without_the_sentinel_env_var_fails_closed` and `tests/test_s0_08_containment.py:973` `test_p2_without_the_main_cmdline_env_fails_closed` — and the checker refuses the bundle |
| 7 lossy decodes | 3 | SAFE | only in the identity recorder; a corrupted digest fails the checker's exact equality |
| 8 broad catches | 4 | SAFE | each converts a parse failure into a NAMED failure carrying the exception type |
| 9 waits / polls | 1 | DOCUMENTED-LIMIT | the readiness loop is failure-aware; PC-only, NOT executed here |
| 10 skips / xfails | 0 | SAFE | no `skip`/`xfail`/`importorskip` in the file. The one conditional comparison (the fixture's host-dependent values) still asserts on both arms and is stated in `PROVENANCE.md` |
| 11 world-scoped enumerations | 4 | **CLOSED — the class VERIFY-G1 regraded** | selecting by an exact cmdline is only safe when the cmdline is unique. `proofs/S0-08/canaries/P2.sh:49` appends to `main_pids=` for EVERY match, and `proofs/S0-08/check_containment.py:264` refuses a set larger than one with `main program cmdline is ambiguous`; the cmdline itself was changed away from the image's own root sleeper |
| 12 signal installs | 1 | SAFE | `CID`/`SENTINEL` pre-initialised before `trap cleanup EXIT` |
| 13 `/proc/<pid>/exe` races | 1 | SAFE | `readlink /proc/self/ns/net`, recorded only |
| 14 mirrors | 2 | SAFE | the live-binding test now NAMES the planted key for P4; the crun fixture is bound to its producer by a re-capture, not by a copy of its own values |
| 15 two counters, different populations | 2 | SAFE | `secret_env_count` vs its names (asserted to agree); `main_pids` vs `main_uids` (asserted to agree, `proofs/S0-08/check_containment.py:267`) |
| 16 provably redundant guards | 0 | — | empty class |
| 17 hardlink-clobbering writes | 0 | — | empty class |
| 18 other families | 2 | **CLOSED** | the piped-rc fail-open, previously fixed in P3 and now fixed at `proofs/S0-08/canaries/P1.sh:19` (`dmesg_all=$(dmesg 2>/dev/null); dmesg_rc=$?`) and at `proofs/S0-08/tools/pc/run_containment.sh:315` (`exec_rc=$?`). All three are now tested live |

---

## Self-attack: the three most likely ways this is still wrong

1. **`s6-svscan` is the wrong literal, and the first PC run reds on a correctly contained container.**
   The one assertion I could not reproduce. Ruled down, not out: the sha-verified tarball proves `/init`
   does NOT stay PID 1 (so the brief's `init` was certainly wrong), `Dockerfile:68` names the destination,
   and the s6-linux-init stage-1 → `s6-svscan` hop matches s6's documented architecture. The failure is
   **closed and named** (`containment: P6 container PID 1 is <x>, not the image's own s6-svscan`), the
   spec tells the reader how to tell a pin finding from a containment failure, and the other two
   capability-independent assertions (`own_pid_count` bound, P2/P6 agreement) do not depend on the
   literal. A wrong literal costs one PC re-run; the old code cost a silent hollow green.
2. **`CONTAINER_MAX_PIDS = 32` is too tight for the real image.** The derivation counts only the services
   the image DECLARES; `Dockerfile:95` mentions per-profile gateways registering dynamically at runtime.
   With `sleep 2147483647` as the CMD and no profile configured none should start, and 32 is ~2.5× the
   derived 12 — but the number is derived from source, not from a running container. Mitigated the same
   way: the reason prints the observed count, so a red is a one-line correction with its evidence in hand.
   The direction is safe (a host table is 100×, not 3×, the bound).
3. **The `run_argv` screen is too narrow — a dangerous flag I did not enumerate passes.** It is a
   blocklist over a recorded list, and blocklists miss. Ruled down by pairing it with a strict
   **allowlist** half: the three required pairs must be present AND every `--network` occurrence must name
   `none`, so the specific escape VERIFY-G1 built (A8) fails on the required pair rather than on the ban.
   It is still possible to construct an argv that is dangerous in a way I did not name; that is why the
   run also pins `image_source_commit` and `canary_exec_user`, and why the runner builds the argv itself.

Two more I checked and closed: the `_csv` helper drops empty entries, so a pid whose uid could not be read
gives `1 pid(s), 0 uid(s)` and a named refusal rather than a silent pass; and `check_p6` reads P2's line
through `_canary`, which already raised if P2 was absent or reported `rc != 0`.

**A fourth, which the PC gate proved I got wrong the first time and which I now treat as the standing
risk: any test that runs a canary LIVE inherits the venue's identity.** I fixed the canary's venue
sensitivity (F13) and then wrote its expectation from the venue I happened to be on. The general repair is
the one applied here — a live test must derive its expectation from a probe of the running user and assert
both arms — and I re-ran the ENTIRE S0-08 file as an unprivileged uid to look for siblings rather than
fixing only the two the gate named. It found none, but that scan is the evidence, not my confidence.

---

## NOT done — first-class

- **The PC containment run.** No bridge use of any kind by this lane. VERIFY-G1's eight PC steps are the
  coordinator's, and they still apply, with three additions from this round: (a) confirm P2's `main_pids`
  holds exactly ONE pid at uid 10000; (b) record P6's `mount_proc_rc` whatever it is — 32 is now the
  EXPECTED value and is asserted against, not skipped; (c) if P6 reds on the PID-1 comm, read the observed
  value before touching anything (see §DISCREPANCIES D1).
- **The image build** (`podman build` of `localhost/hermes-s0-08:527da608`) — PC-side.
- **`podman exec --user 10000` against a live container.** The exec identity is read from the runner's
  bytes and asserted from the evidence; it has never been executed.
- **`sha256sum /usr/local/bin/runsc` on the PC.** Still a sandbox measurement asserted about a PC binary;
  `PC-BRIDGE.md:128` records only the `048b89aa` prefix, and only that prefix matches so far.
- **P2/P3/P4/P5 under real gVisor.** `runsc --rootless do` shares the host filesystem, so it cannot test
  mounts, the sentinel or the image's tools (AF-AP-4). P1, P6, P7 and P8 were smoke-run there, root AND
  uid 65534.
- **The registry/ledger transition** (`blocked_host → execution_proof`, the mint, `blocked.json` removal)
  — outside my file boundary and gated on the PC run.
- **The anti-pattern registry row** for the "assertion skipped when its precondition fails" class. Outside
  my boundary (`docs/INCIDENT-LOG.md` is not in scope); flagged here for the coordinator, with the
  mechanical signature `if <field> == <value>:` with no `else`/`elif` and no raise on the other arm.

---

## Process census (nothing of mine left running)

- Processes: the two `sleep infinity` I started for the P2 collision (pids 31954 and 32690) were killed
  **by pid** after the reproduction. The closing `/proc` scan for `sleep infinity`, `sleep 2147483647`,
  `runsc` and `time.sleep(3600)` returns exactly one row — **the census command's own shell**, which
  carries all four patterns in its argv. That is the self-matching-scan trap the operating rules name,
  and it is the only hit; no canary, no sandbox and no sleeper of mine is running. The two
  test-started processes in `test_p2_reports_every_holder_of_the_main_cmdline` are killed by handle in a
  `finally`. No `pkill`, no `pgrep -f`, no name match anywhere.
- Final tree: `git status --porcelain` shows my 12 modified files plus the new `G2-report.md`, and the
  other lanes' own entries untouched (the coordinator's `VERIFY-G2-brief.md` also appears in my
  directory — theirs, not mine, and unmodified by me).
- Mounts: `grep -c s0-08 /proc/self/mountinfo` → `0`. `ls -d /tmp/s0-08-*` → no such file (the P6 mount
  points and the fixture sentinel are gone).
- Containers: none started. No podman, no bridge, no `/tmp/runsc` sandbox left running (the two `do` cells
  are one-shot and exited). The PC-gate round added no bridge use either: the non-root venue was emulated
  locally with `setpriv`, never on the PC.
- Scratch: everything under `…/scratchpad/g2lane/`; every pytest run carried an explicit `--basetemp`
  under it; the mutation trees and all four `lane_gate` archives were removed by their own drivers. The
  two non-root reproduction dirs had to live OUTSIDE the scratchpad — `/tmp/claude-0` is `0700`, so a run
  dropped to uid 65534 cannot traverse into it — and `/tmp/g2lane-nonroot-bt` and `/tmp/g2lane-before`
  were removed afterwards.
- Repo: `git status --porcelain` shows my 12 files and the other lanes' own entries; `git stash list`
  empty; no `git` mutation command was run.
