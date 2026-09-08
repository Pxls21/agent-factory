# Lane G1 — S0-08 gVisor containment: the spec, the canaries, the checker, the PC runner — the deferral EXPIRED, so the proof must RUN (sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".)

**Why:** `proofs/S0-08/blocked.json` reads `blocker_status: "expired"` (runsc is installed on the PC and runs rootless — PC-BRIDGE.md:112-149);
`validate-ledger stage1-gate` prints "deferral expired — the proof must run". Nothing else exists: no spec, no containment spec, no
canaries, no checker, no runner. The seed (`seeds/seed-stage0-v1.yaml:477-498`) deferred "Hermes container root-start/s6 setup then privilege
drop to hermes under runsc; required tools work; escape and host-read canaries FAIL" to a gVisor-capable host — that host is the PC.
**Inputs (read in this order):** `tasks/briefs/stage0-parallel-support/material-S0-08.md` (the whole pack: seed, breakdown, findings, plan
seams, what exists, venue facts, the class preflight in material-S0-02.md §7) · the pinned Hermes source at
`/home/user/nerdherderdani/hermes-agent` (commit 527da608 = `upstream.lock.yaml` — READ-ONLY): `Dockerfile` (s6-overlay install :93-135,
`useradd -u 10000 -m -d /opt/data hermes` :150, `USER root` :298 with the comment at :309-311 "Start as root so the s6-overlay stage2 hook can
usermod/groupmod and chown the data volume. Each supervised service then drops to the hermes user via `s6-setuidgid hermes`"),
`docker/stage2-hook.sh`, `docker/s6-rc.d/main-hermes/run`, `docker/hermes-exec-shim.sh`, `docker-compose.yml` (`network_mode: host` — note
it) · `docs/05_SECURITY.md:56-72` (§5 Production Hermes profile — the spec encodes it) · the minted execution exemplars `proofs/S0-07/spec.json`
+ `proofs/S0-11/` (shape) and S0-01's capture-then-check shape (`proofs/S0-01/spec.json`, `check_acp_conformance.py`'s `deferred:` exit 2
when evidence is absent) · `proofs/schemas/spec.schema.json` · `spikes/runsc/result.json` (the sandbox runsc binary `/tmp/runsc`, release
release-20260817.0, rootless `do`) · `PC-BRIDGE.md:112-149` (the verified rootless podman+runsc run and its TWO caveats:
`--security-opt label=disable`, `--runtime-flag ignore-cgroups`; platform systrap, `/dev/kvm` absent).
**Scope (all NEW files under `proofs/S0-08/` + one test file + your report):** `proofs/S0-08/spec.json` · `proofs/S0-08/CONTAINMENT-SPEC.md` ·
`proofs/S0-08/canaries/*.sh` · `proofs/S0-08/check_containment.py` · `proofs/S0-08/marker_gate.py` · `proofs/S0-08/tools/pc/run_containment.sh`
(PC-side) · `proofs/S0-08/fixtures/` (the negative evidence bundles + a malformed marker) · `tests/test_s0_08_containment.py` · report
`tasks/briefs/s0-08-support/G1-report.md`. Do NOT touch `blocked.json`, `probe.json`, `probe_runsc.sh` (the marker stays until the mint
transition), `proofs/registry.yaml`, `scripts/validate-ledger`, `scripts/proof-runner`, `proofs/schemas/*` (attested inputs — AF-AP-56; the
coordinator changes the registry class at mint time). Shared-tree rules: other lanes hold uncommitted edits — never `git
stash/checkout/restore/reset/add/commit/push`; gates from a `git archive <PIN>` copy under
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/g1/ + your files; explicit `--basetemp`; kill only your own
processes by pid; NEVER background a run and stop; no outward actions; NO PC bridge; never read or print credentials. Interpreter
`/root/venv-agent-factory/bin/python`.

## Design (pinned — build it, do not redesign it)
1. **CONTAINMENT-SPEC.md** encodes docs/05 §5's Production Hermes profile as NUMBERED, machine-checkable properties, each mapped to a canary
   and to the Hermes lifecycle fact it rests on (file:line in the pinned Dockerfile / s6 scripts): P1 the container runs under gVisor
   (`uname -r` == `4.19.0-gvisor`; `dmesg` first line "Starting gVisor"); P2 PID 1 is s6-overlay's `/init` (root) and the supervised
   `main-hermes` service runs as uid 10000 (`s6-setuidgid hermes`); P3 required tools work inside (`hermes --version` or the pinned CLI's
   cheapest self-check, `python3 -c 'import hermes'`, node, uv — derive the list from the Dockerfile's installs); P4 narrow mounts: no
   `/var/run/docker.sock`, no host `$HOME`, no provider-secret env (`grep -c` over `/proc/1/environ` for the redaction pattern
   `pins.REDACTED_ENV_KEY_RE` == 0 apart from an allowlisted set you name); P5 host-read canary FAILS: a sentinel file the runner writes
   on the host (`$HOME/s0-08-host-sentinel-<nonce>`) is unreadable inside, and `/proc/1/root` of the HOST is not the container's; P6 escape
   canaries FAIL: `mount -t proc proc /mnt` denied, `/dev/kvm` and raw host devices absent, `ptrace` of PID 1 denied, `unshare -n` denied
   or confined (gVisor's answer recorded verbatim — assert the exact errno/message); P7 egress note: the compose file uses
   `network_mode: host` — the spec RECORDS that S0-08 does not assert egress (S0-05's job) and the runner must NOT use host networking for
   the containment run (`--network none` or the default podman netns) — state which and why; P8 resource limits: NOT enforced under
   rootless runsc (`ignore-cgroups`) — recorded as a documented limit, not asserted. Every property carries its expected canary OUTPUT
   verbatim (the exact line the checker compares).
2. **Canaries** — one shell script per property under `canaries/`, run INSIDE the container by the runner (`podman exec`), each printing ONE
   JSON line `{"canary": "P5", "expect": "denied", "observed": "...", "rc": N}` — never a verdict (the checker decides). Smoke-test the
   identity canaries in the sandbox under `/tmp/runsc --rootless do sh canaries/P1.sh` (if `/tmp/runsc` is absent, fetch is NOT yours —
   say `NOT run here`) and the same scripts under plain `sh` (the crun/host stand-in) to produce the NEGATIVE evidence bundle.
3. **The runner `tools/pc/run_containment.sh`** (PC-side, NOT run here): builds the image from `~/s0-01-pinned/hermes-agent` (`podman build`,
   the Dockerfile as-is, tag `localhost/hermes-s0-08:527da608`) — OR consumes a prebuilt tag passed in; runs it under runsc with EXACTLY the
   verified flags (`--runtime /usr/local/bin/runsc --runtime-flag ignore-cgroups --security-opt label=disable`), a private network, the
   sentinel mounted NOWHERE; waits for s6 readiness (the `main-hermes` service up — derive the readiness signal from the s6 run script);
   records `runtime-identity.json` (runsc version + sha256 of `/usr/local/bin/runsc`, podman version, image digest, the exact `podman run`
   argv, host kernel, `id` of the main-hermes process from `podman exec`, the `ps` tree inside); runs every canary via `podman exec`, writes
   `evidence/<venue-run>/canaries.jsonl`; tears down by container id (never by name/pkill); exit codes: 0 evidence written, 2 the image
   could not build/pull (named), 3 runsc refused (named). A second invocation with `--runtime crun` produces the NEGATIVE bundle. The
   script is `bash -n` clean and its every external call is listed in the report; it is run by the coordinator over the bridge.
4. **The checker `check_containment.py <evidence-dir>`** — deterministic, LLM-free, the S0-01 shape: absent dir → `deferred: containment
   evidence not captured` exit 2; present → every property P1-P6 asserted EXACTLY against the canary lines (P7/P8 recorded, not asserted);
   the identity file's runsc version must equal the pinned release (`release-20260817.0` — pin it in the checker with the source: PC-BRIDGE.md
   and the spike) and its runsc binary sha256 must equal the PC's (`048b89aa…` — read the full digest from PC-BRIDGE.md:128 and pin it);
   any missing canary line = FAIL by name; the first failing property is the `failure_reason:` line (`containment: P1 host kernel
   6.17.11-200.fc42, not gVisor` is the exemplar for the crun bundle). Reads under the S_ISREG rule (a FIFO at any evidence path → named
   refusal, never a hang). PASS line: `PASS: S0-08 gvisor-containment - N properties asserted over <run>`.
5. **`marker_gate.py`** — the seed's `marker_control`: given a proof dir, FAIL (exit 1, `marker: absent`) when the classification is blocked
   and `blocked.json` is absent; FAIL (`marker: malformed: <field>`) when it lacks `marker.probe_run`/`blocker_status`/`unblock_condition`
   or `blocker_status` is outside `{absent, rejecting, expired}`; FAIL (`marker: expired — the proof must run`) when `expired` and no
   `result.json`; PASS when `result.json` exists and `blocked.json` is gone (the completed transition). Fixtures: `fixtures/malformed-marker/`
   (a `blocked.json` missing `probe_run`), tested.
6. **`spec.json`** (schema-valid; run `python3 scripts/validate-ledger` on a scratch copy to prove it parses): legs `positive`
   (`check_containment.py proofs/S0-08/evidence/pc-runsc`, expect 0), `negative` (`check_containment.py proofs/S0-08/fixtures/evidence-crun`,
   expect 1 + `failure_reason: containment: P1 …` exact), `marker` (`marker_gate.py --proof-dir proofs/S0-08/fixtures/malformed-marker`,
   expect 1 + `marker: malformed: probe_run`). The positive leg's evidence does not exist yet — say so in the report (`NOT run here: the PC
   run is the coordinator's`) and show the checker's `deferred:` exit 2 on the absent dir.
7. **Tests (`tests/test_s0_08_containment.py`)** — deterministic: the checker over the committed crun bundle (exit 1, the exact reason); over a
   synthetic PASSING bundle built by the test from the spec's expected lines (exit 0, the PASS line); every property mutated one at a time
   in a scratch copy → the named failure (P1..P6 each); the missing-canary case; the FIFO case; the marker gate's four verdicts; the
   canaries' JSON shape (every script's output parses, `canary` ∈ P1..P8). Preflight the 18 classes of the sweep (material-S0-02.md §7)
   over your own files and say so in the report.
8. **Report discipline:** `report_lint.py` on your report (map every scope file; MISS 0; heuristic rows named); `ap_screen.py` over
   `proofs/S0-08` and `--tests` over your test — every hit classified by running it; file:line by `grep -n` on the FINAL bytes; counts
   pasted from `bash scripts/test_summary.sh tests/test_s0_08_containment.py` (twice); `pyflakes` + `bash -n`; the process census.

## Mutants (scratch copies; ≥ 12; killer line pasted)
P1-HOST-KERNEL-ACCEPTED · RUNSC-VERSION-UNPINNED · SHA-UNPINNED · CANARY-MISSING-IGNORED · P5-SENTINEL-READABLE-ACCEPTED ·
P2-UID-ROOT-ACCEPTED · FIFO-EVIDENCE-HANG · MARKER-MALFORMED-PASSES · MARKER-EXPIRED-PASSES · CRUN-BUNDLE-PASSES · SPEC-REASON-DRIFT ·
CANARY-VERDICT-IN-SCRIPT (a canary printing "PASS" instead of observations must be rejected by the shape test).

## Report shape
FILE IDENTITY (every new file, sha256 + lines) · DONE (property → canary → checker assertion → test) · the mutant table · NOT_DONE (the PC
run; the image build; the registry transition — all the coordinator's, by name) · DISCREPANCIES (anything the pack or the seed got wrong —
e.g. the owner answer says KVM, the probe says systrap) · SELF-ATTACK.
