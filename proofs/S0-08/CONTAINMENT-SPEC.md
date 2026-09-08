# S0-08 — gVisor containment spec

**What this proves:** the pinned Hermes runtime (`hermes-agent` @ `527da608`, `upstream.lock.yaml:10-15`)
starts as root, completes its s6-overlay setup, drops the workload to the non-root `hermes` user, keeps
its required tools working, and cannot read the host or acquire host state — all while running under
gVisor (`runsc`).

It encodes `docs/05_SECURITY.md:56-72` § "Production Hermes":

> Run the entire Hermes runtime under `runsc`. Validate root-start/s6 setup, privilege drop to `hermes`,
> required tools, narrow mounts, no Docker socket/home/provider secrets, resource limits, and enforced
> egress.

as eight numbered properties. **Six are asserted (P1-P6). Two are recorded and explicitly NOT asserted
(P7 egress, P8 resource limits)** — the reasons are stated in full below rather than left as a silent
gap.

**Venue.** The proof runs on the owner's PC over the bridge (`PC-BRIDGE.md:60`), the only host with
podman + the owner-installed `runsc`. `proofs/S0-08/blocked.json` reads `blocker_status: "expired"`
and `validate-ledger stage1-gate` prints "deferral expired — the proof must run": the deferral is over.

---

## 0. How the parts fit

| part | file | role |
|---|---|---|
| canaries | `proofs/S0-08/canaries/P1.sh` … `P8.sh` | run INSIDE the container; each prints ONE JSON line of **observations**, never a verdict |
| runner | `proofs/S0-08/tools/pc/run_containment.sh` | PC-side: builds/starts the container under runsc, runs every canary, writes the evidence bundle |
| checker | `proofs/S0-08/check_containment.py` | deterministic, LLM-free; asserts P1-P6 against the bundle, records P7-P8 |
| marker gate | `proofs/S0-08/marker_gate.py` | the seed's `marker_control`: a deferral may not outlive its blocker |
| spec | `proofs/S0-08/spec.json` | the three legs the proof-runner executes |

The split is deliberate: **the canary observes, the checker judges.** A canary that printed its own
PASS/FAIL would make the container the judge of its own confinement — the AF-AP-28 class (a security
assertion that trusts the subject's self-report). `tests/test_s0_08_containment.py::test_canaries_never_print_a_verdict`
holds that line.

### The evidence bundle

```
proofs/S0-08/evidence/<venue-run>/
  canaries.jsonl        one JSON line per canary, P1..P8, no duplicates
  runtime-identity.json runsc version + sha256, podman version, image digest,
                        the exact `podman run` argv, host kernel, the ps tree,
                        and the P5 host-side sentinel control
```

Each canary line has exactly four keys:

```json
{"canary": "P1", "expect": "<the property in words>", "observed": {"<name>": "<value>", ...}, "rc": 0}
```

`rc` is the canary script's own status — whether the observation was **taken**, never whether the
property **holds**. A canary reporting `rc != 0` for an asserted property is a checker Failure: an
observation that never happened must not read as a satisfied property.

---

## 1. The Hermes lifecycle these properties rest on

Verified by reading the pinned source at `/home/user/nerdherderdani/hermes-agent` (`527da608`):

| fact | file:line |
|---|---|
| s6-overlay 3.2.3.0 installed, checksum-verified | `Dockerfile:93`-135 |
| the non-root runtime user: `useradd -u 10000 -m -d /opt/data hermes` | `Dockerfile:150` |
| the image runs as root | `Dockerfile:298` (`USER root`) |
| why root: the stage2 hook must usermod/chown the data volume | `Dockerfile:309`-311 |
| the entrypoint is a dispatcher, not `/init` | `Dockerfile:464` |
| when PID 1, the dispatcher execs `/init` with the main wrapper | `docker/entrypoint-dispatch.sh:18` |
| **the main program's privilege drop** | `docker/main-wrapper.sh:31` |
| the `docker exec` path's privilege drop | `docker/hermes-exec-shim.sh:87` |
| that path refuses to silently run as root when s6 is missing | `docker/hermes-exec-shim.sh:76` |
| the setup hook's drop helper | `docker/stage2-hook.sh:24` |
| the supervised `dashboard` service's drop | `docker/s6-rc.d/dashboard/run:55` |
| **the supervised `main-hermes` service is a root no-op** | `docker/s6-rc.d/main-hermes/run:27` |
| `dashboard` is DOWN unless `HERMES_DASHBOARD` is truthy | `docker/s6-rc.d/dashboard/run:9`-20 |
| production compose uses host networking | `docker-compose.yml:35` and `:67` |
| the installed python package is `hermes_cli` — there is no `hermes` package | `pyproject.toml:587` |

### Two corrections this spec makes to its own brief

**(a) `main-hermes` is not the privilege-drop seam.** The lane brief's P2 asked for "the supervised
`main-hermes` service runs as uid 10000 (`s6-setuidgid hermes`)". It does not, and it never did:
`docker/s6-rc.d/main-hermes/run:27` is `exec sleep infinity`, running as root, and its own comment says
"For now this service is a no-op: it sleeps forever, doing nothing." The `Dockerfile:309`-311 comment
that "Each supervised service then drops to the hermes user via `s6-setuidgid hermes` in its run script"
is true only of `dashboard` — and `dashboard` is DOWN by default. **Asserting the brief's P2 literally
would have produced a canary that fails against a correctly-built image.** The real, observable drop is
the main program's (`docker/main-wrapper.sh:31`), which is what P2 asserts; the two recorded facts are
carried as observations so the gap is visible rather than hidden.

**(b) `import hermes` does not exist.** The brief's P3 named `python3 -c 'import hermes'`. The pinned
project installs `hermes_cli`, `agent`, `tools`, `gateway`, `acp_adapter`, … (`pyproject.toml:587`) and
no top-level `hermes` module. P3 asserts `import hermes_cli`.

---

## 2. The properties

### P1 — the container runs under gVisor · **ASSERTED**

The whole proof is void if the workload is not actually inside a gVisor sandbox, so this is checked
first and its failure is the bundle's headline reason.

- **Canary:** `canaries/P1.sh` — `uname -r`, first line of `dmesg`.
- **Expected output (measured under `runsc release-20260817.0`, 2026-09-08):**

```json
{"canary":"P1","expect":"uname -r is 4.19.0-gvisor and dmesg line 1 contains Starting gVisor","observed":{"uname_r":"4.19.0-gvisor","dmesg_first_line":"[    0.000000] Starting gVisor..."},"rc":0}
```

- **Checker asserts:** `uname_r == "4.19.0-gvisor"` exactly; `"Starting gVisor"` is a substring of
  `dmesg_first_line`.
- **Source:** `PC-BRIDGE.md:137`, `spikes/runsc/result.json:35`.
- **Uncontained observation (measured on the sandbox host):** `uname_r` is the host kernel and dmesg
  line 1 reads `Linux version …` → `containment: P1 host kernel 6.18.44-fc-v24, not gVisor`.

### P2 — root start, s6 setup, privilege drop · **ASSERTED**

- **Canary:** `canaries/P2.sh` — uid/comm/cmdline of PID 1; the uid of the process whose cmdline is
  exactly `sleep infinity` (the container's main program, pinned by the runner's CMD); a process count.
- **Expected observations:** `pid1_uid` `"0"`, `main_uid` `"10000"`.
- **Checker asserts:** `pid1_uid == "0"` **and** `main_uid == "10000"`.
- **Rests on:** `Dockerfile:298`, `Dockerfile:309`-311, `docker/entrypoint-dispatch.sh:18`,
  `docker/main-wrapper.sh:31`, `Dockerfile:150`.
- **Recorded, not asserted:** `main_hermes_service` and the `ps` tree in `runtime-identity.json` record
  that the supervised `main-hermes` slot is a root sleeper (`docker/s6-rc.d/main-hermes/run:27`) and that
  `dashboard` is down (`docker/s6-rc.d/dashboard/run:9`-20). See §1(a).
- **Why `main_uid`, not "some process is non-root":** the assertion names the exact process by cmdline.
  A container where *anything* runs non-root would satisfy the weaker form — the AF-AP-26 class
  (a relative-only security predicate).

### P3 — the required tools work inside · **ASSERTED**

Derived from the image's own installs, not from a wish-list.

- **Canary:** `canaries/P3.sh` — runs `/opt/hermes/bin/hermes --version` (`Dockerfile:299`-301, and the
  shim itself drops privileges), `python3 -c 'import hermes_cli'` (`pyproject.toml:587`),
  `node --version` (`Dockerfile:154`-160), `uv --version` (`Dockerfile:152`).
- **Checker asserts:** all four exit statuses are `"0"`; the first output line of any failing tool is
  quoted in the failure reason.
- **Note on the canary's own construction:** each tool's status is captured with **no pipeline between
  the tool and `$?`**. The first draft piped through `head -n 1` and reported a missing binary as
  rc 0 — a fail-open that would have accepted a container with no working tools.

### P4 — narrow mounts, no Docker socket, no provider secrets · **ASSERTED**

- **Canary:** `canaries/P4.sh` — `/var/run/docker.sock` and `/run/docker.sock`; the **names** (never the
  values) of the canary's OWN environment (`env`, names cut before `=`) matching the redaction pattern — the canary is exec'd inside the container as the runtime user, so its environment is the one the main program inherits; PID 1's environ is root-owned 0400 and unreadable to that user (the PC gate 2026-09-08), and a shell redirect of `/proc/self/environ` read empty under the sandbox's gVisor, so the libc environment is the surface; the mount count and every bind root.
- **Pattern:** `REDACTED_ENV_KEY_RE = r"(?i)(KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV)"`, the one S0-01
  already pins at `proofs/S0-01/pins.py:50`.
- **Allowlist: EMPTY.** `grep -n "^ENV" Dockerfile | grep -Ei 'KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV'`
  over the pinned image returns nothing — no baked env key matches, so the expected count is 0 with
  nothing excused.
- **Checker asserts:** `docker_sock == "absent"`; zero matching key names outside the (empty) allowlist;
  and `secret_env_count` agrees with the number of names reported — a count of 0 beside a non-empty
  key list is a malformed observation, not a pass.
- **Secret hygiene:** key NAMES only. No value is read, printed or hashed anywhere in this proof.

### P5 — the host-read canary FAILS · **ASSERTED**

- **Mechanism:** the runner writes `$HOME/s0-08-host-sentinel-<16 hex nonce>` on the **host**, mounts it
  **nowhere**, proves it readable on the host, and records that read in
  `runtime-identity.json.sentinel_host_read`. The canary tries the same absolute path inside.
- **Checker asserts, in this order:** the host control exists **and** read the file **and** its path is
  byte-identical to the path the canary tried; only then that `sentinel_readable == "no"`.
- **Why the host half is mandatory:** "unreadable inside" alone is satisfied by a file that never
  existed — the AF-AP-22 class (a tautological isolation assertion). The pair is the evidence; either
  half alone is not.

### P6 — escape attempts do not yield HOST state · **ASSERTED**

**This property was rewritten against measurement.** The brief specified "`mount -t proc proc /mnt`
denied … `unshare -n` denied or confined". Measured under `runsc release-20260817.0` in the sandbox on
2026-09-08:

| attempt | gVisor's actual answer |
|---|---|
| `mount -t proc proc <dir>` | **succeeds, rc 0** |
| `unshare -n true` | **succeeds, rc 0** |
| `ls /dev/kvm` | fails, rc 2, `No such file or directory` |

Neither success is an escape: the mount yields **gVisor's own procfs** and the namespace is created
**inside** the sandbox. Measured side by side — the sandbox's mounted procfs listed **3** processes with
PID 1 `sh`, while the host at that moment had **99**. A canary asserting "mount is denied" would fail on
a correctly-contained container, and "fixing" that by flipping the expectation to "allowed" would assert
nothing at all.

So P6 asserts the **containment signature** instead:

- **Canary:** `canaries/P6.sh` — a named dangerous-device census (`/dev/kvm`, `/dev/mem`, `/dev/kmsg`,
  `/dev/sda`, `/dev/nvme0n1`, `/dev/loop0`, `/dev/dm-0`) plus the full `/dev` listing; `mount -t proc`
  into a per-invocation mount point, then the mounted procfs's PID 1 `comm` and process count beside the
  container's own; `unshare -n` verbatim.
- **Checker asserts:** `dangerous_devices` is empty; and when the mount succeeded, the mounted procfs's
  PID 1 `comm` is non-empty and **equals the container's own** — i.e. the mount revealed the container,
  not the host.
- **Recorded, not asserted:** the verbatim `unshare -n` status and message, the `mount` status and any
  message, and the full `/dev` listing. gVisor's exact wording is not pinned, because this lane could not
  run the property in its target venue (podman + runsc on the PC) and will not mint an expected errno
  string it has not seen there.
- **Uncontained observation (measured on the sandbox host):** `dangerous_devices` = `/dev/kmsg,/dev/loop0`
  → `containment: P6 raw host devices present: /dev/kmsg,/dev/loop0`.
- **Not asserted: ptrace of PID 1.** Inside the container PID 1 is the container's *own* `/init`;
  ptracing it is not an escape, and a host process cannot even be named from another PID namespace.
  Asserting it would be theatre.

### P7 — egress · **RECORDED, NOT ASSERTED**

S0-08 asserts **no** egress property. Enforced egress is S0-05's proof, and duplicating it here would
produce a second, weaker oracle for the same claim.

What must be recorded, because it is a real divergence from production: the shipped compose file runs
Hermes with **host networking** — `network_mode: host` at `docker-compose.yml:35` (gateway) and `:67`
(dashboard). **The containment run must not inherit that.** The runner passes `--network none`
(`tools/pc/run_containment.sh`), chosen over podman's default netns because the containment properties
need no network at all and `none` is the narrowest posture available; a test pins that the runner never
carries `--network host`.

**Documented gap:** this proof therefore says nothing about whether Hermes is contained *while using
host networking*, which is how the compose file actually deploys it. That question belongs to S0-05 and
to a later deployment ADR.

### P8 — resource limits · **RECORDED, NOT ASSERTED**

`docs/05_SECURITY.md:56-72` lists resource limits in the production profile. They **cannot be
demonstrated in this configuration**: the verified rootless podman+runsc invocation requires
`--runtime-flag ignore-cgroups` because rootless runsc cannot set up cgroups on the PC
(`PC-BRIDGE.md:144`-148 — systemd driver returns `Interactive authentication required`, cgroupfs is
denied at the root `cgroup.subtree_control`, and `--cgroups=disabled` is rejected by runsc). **No
resource limits apply to this run.**

`canaries/P8.sh` records `/proc/self/cgroup` and the `memory.max` / `cpu.max` / `pids.max` values so the
absence is on the record. The production shape (delegated systemd cgroups, or a rootful run) is an open
Wave-0 question, named as such in `PC-BRIDGE.md:147`-148. **This is a stated gap in the containment
proof, not a satisfied requirement.**

---

## 3. Failure reasons

The checker asserts in order P1 → P2 → P3 → P4 → P5 → P6, so **the first failing property is the
reason** and the reason is stable for a given bundle.

| property | reason |
|---|---|
| identity | `containment: runtime identity runsc <v>, expected release-20260817.0` |
| identity | `containment: runtime identity runsc sha256 <d>, expected 048b89aa…074c` |
| P1 | `containment: P1 host kernel <k>, not gVisor` |
| P1 | `containment: P1 dmesg line 1 does not announce gVisor: <line>` |
| P2 | `containment: P2 pid 1 uid <u>, expected 0` |
| P2 | `containment: P2 main program uid <u>, expected 10000` |
| P3 | `containment: P3 <tool> exited <rc>: <first line>` |
| P4 | `containment: P4 docker socket present` |
| P4 | `containment: P4 <n> secret-bearing env key(s) in the runtime env: <names>` |
| P5 | `containment: P5 host sentinel readable inside the container` |
| P6 | `containment: P6 raw host devices present: <list>` |
| P6 | `containment: P6 mounted procfs PID 1 is <x>, not the container's own <y>` |
| any | `containment: <Pn> canary line absent` |
| any | `containment: <Pn> canary did not complete its observation (rc <n>)` |

PASS line: `PASS: S0-08 gvisor-containment - 6 properties asserted over <run>`

Absent evidence directory: `deferred: containment evidence not captured`, exit 2. Once the directory
exists, every missing file inside it is a Failure — a half-written bundle must never read as "not run".

## 4. The runtime identity is pinned

`runtime-identity.json` must record `runsc_version == release-20260817.0` and
`runsc_sha256 == 048b89aada69dc3333422e139d6e9d02f8ab06bda52398060e0fbdacca00074c`.

`PC-BRIDGE.md:128` records only the truncated prefix `048b89aa…`. The full digest above was measured
from the identical release binary in the sandbox (`sha256sum /tmp/runsc`, 2026-09-08), and its first
eight hex characters match the PC's recorded prefix. **Before the first PC run the coordinator should
confirm `sha256sum /usr/local/bin/runsc` on the PC equals this digest**; if it does not, that is a
finding about the two venues' binaries, not a checker bug.

Pinning identity is necessary but never sufficient. `fixtures/evidence-crun` carries a **valid** pinned
identity beside observations taken outside gVisor, and must still fail on P1 — the committed test that
the checker reads observations rather than trusting metadata.

## 5. The marker control

`marker_gate.py --proof-dir <dir>` implements the seed's `marker_control`
(`seeds/seed-stage0-v1.yaml:493`):

| state | verdict | exit |
|---|---|---|
| `result.json` present, `blocked.json` gone | `marker: completed transition` | 0 |
| no marker and no result | `marker: absent` | 1 |
| marker lacking `probe_run` / `blocker_status` / `unblock_condition` | `marker: malformed: <field>` | 1 |
| `blocker_status` outside `{absent, rejecting, expired}` | `marker: malformed: blocker_status '<v>'` | 1 |
| `expired` with no `result.json` | `marker: expired - the proof must run` | 1 |
| `absent` / `rejecting`, well-formed | `marker: <status>` | 0 |

On the tree today the live marker is `expired` with no result, so the gate is **RED by design** — that
is the deferral refusing to outlive its blocker. It turns green when the PC run lands `result.json` and
the coordinator removes `blocked.json`.

## 6. What this lane did NOT run

- **The PC containment run.** No bridge access from this lane. `evidence/pc-runsc/` does not exist and
  the positive leg correctly reports `deferred: containment evidence not captured` (exit 2).
- **The image build.** `podman build` of `localhost/hermes-s0-08:527da608` is PC-side.
- **P2, P3, P4, P5 under real gVisor.** `runsc --rootless do` **shares the host filesystem** (measured:
  a host file and `/home` are both readable from inside), so it can validate P1 and P6's kernel-level
  answers but is structurally incapable of testing mounts, the sentinel or the image's tools. Treating a
  `do`-mode result as containment evidence would be a venue misclassification (the AF-AP-4 class).
  P1, P6, P7 and P8 **were** smoke-run under real gVisor here; the rest await the PC.
