# MATERIAL PACK — S0-08 (gVisor containment spec + fixtures; run deferred / blocked_host)

> EVIDENCE ONLY. Verbatim extraction + located inventory. No design, no judgement, no
> recommendation. Assembled 2026-09-07/08 from the working tree at branch
> `claude/soundbox-kit-migration-iz1jwf`, HEAD `cc46704`. Other lanes hold uncommitted edits.
> **The 18 defect classes and the mint-wide AF-AP rows are carried once in
> `material-S0-02.md` §7 — read that section with this pack.**

---

## 0. INVENTORY TABLE

| item | source file:line | exists? | venue |
|---|---|---|---|
| Seed per-proof block S0-08 | `seeds/seed-stage0-v1.yaml:477-498` | yes | — |
| Frozen mapping (`runsc`) | `seeds/seed-stage0-v1.yaml:575-578`; `proofs/registry.yaml:31` | yes | — |
| Frozen mapping (`dockerd`, venue note) | `seeds/seed-stage0-v1.yaml:579-582`; `proofs/registry.yaml:32` | yes | — |
| Mapping (`pc-bridge`, negative branch → S0-08) | `proofs/registry.yaml:34` | yes — registry only, not the seed | — |
| Breakdown increment #17 | `tasks/stage0-breakdown.md:68` | yes | deferred run / spec in-sandbox |
| Breakdown increment #5 (runsc spike) | `tasks/stage0-breakdown.md:56` | yes | sandbox |
| Owner answer #17 / KC-1 | `tasks/stage0-breakdown.md:88` | yes | PC |
| Findings per-proof constraint | `docs/research/FINDINGS-STAGE0-v1.md:49` | yes | — |
| Findings runsc environment row | `docs/research/FINDINGS-STAGE0-v1.md:25` | yes | — |
| Council compromise 1 (deferral rules) | `docs/research/COUNCIL-VERDICT-STAGE0-v1.md:26` | yes | — |
| Council KC-6, unresolved 5 | `docs/research/COUNCIL-VERDICT-STAGE0-v1.md:38, 49` | yes | — |
| Plan-doc seam `docs/05` §5 containment profiles | `docs/05_SECURITY.md:56-72` | yes | — |
| Plan-doc seam `docs/02` Hermes container lifecycle | `docs/02_COMPONENT_AUDIT.md:32`, `:78-80` | yes | — |
| upstream pin `gvisor` | `upstream.lock.yaml:39-43` | yes | — |
| `proofs/S0-08/` directory | `ls -la proofs/S0-08/` | yes — 3 files | — |
| `proofs/S0-08/blocked.json` | (whole file in §5.2) | yes — `blocker_status: "expired"` | recorded `pc-bridge:fedora` |
| `proofs/S0-08/probe.json` | (whole file in §5.2) | yes | — |
| `proofs/S0-08/probe_runsc.sh` | (whole file in §5.2) | yes | either |
| `proofs/S0-08/spec.json` / containment spec / canary fixtures | — | **no** | — |
| `proofs/S0-08/result.json` | — | **no**; ledger state `EXPIRED` | — |
| Registry entry S0-08 | `proofs/registry.yaml:19` | yes | — |
| Wave-0 spike `runsc` | `spikes/runsc/result.json` (55 lines) | yes — POSITIVE | sandbox |
| Wave-0 spike `dockerd` | `spikes/dockerd/result.json` (49 lines) | yes — POSITIVE | sandbox |
| Wave-0 spike `pc-bridge` (S0-08 branch) | `spikes/pc-bridge/result.json:37-43` | yes | PC |
| PC-side runsc install + verified rootless run | `PC-BRIDGE.md:112-149` | yes — installed 2026-09-03 | PC |
| The Stage-1 grep-gate behaviour on an EXPIRED marker | `scripts/validate-ledger:460-478` | yes | either |
| Ledger task rows | `todo/BUILD-TASKLIST.md:62` (spike DONE), `:74` (#17 pending) | yes | — |

---

## 1. THE SEED

### 1.1 `seeds/seed-stage0-v1.yaml:477-498` (verbatim)

```yaml
- proof_id: S0-08
  classification: blocked_host
  wave: 2
  increment_index: 17
  ledger_denominator: blocked_capability
  spike_dependency: [runsc]
  fixture_format: containment test SPEC + canary fixtures authored and lint-checked now;
    execution deferred to a gVisor-capable host
  assertions:
  - 'deferred live assertions (spec now, run on host): Hermes container root-start/s6 setup
    then privilege drop to hermes under runsc; required tools work; escape and host-read
    canaries FAIL'
  negative_control:
    marker_control: the Stage-1 grep-gate FAILS when the NOT-run marker is absent or malformed
    expected_failure_reason: 'NOT run here: runsc unavailable (no KVM, install blocked)'
  blocked_marker:
    probe: 'command -v runsc plus a trivial runsc invocation'
    reason_enum: [capability_absent, capability_present_but_failing]
    rule: probe re-runs every CI execution; runsc appearing flips the deferral RED
      (deferral_expired) forcing the proof to run
    unblock_condition: 'runsc executable and a trivial runsc container run succeeds'
  owner_placeholder: TBD-owner-gvisor-host
```

### 1.2 Seed header note on S0-08's host (`seeds/seed-stage0-v1.yaml:17-19`, verbatim excerpt)

```
# Owner answers (2026-09-03), superseding the placeholders in-body: the execution
# host is the owner's PC via the token-gated bridge (PC-BRIDGE.md). S0-08's host
# = the PC (bare-metal KVM).
```

### 1.3 Frozen `spike_to_class_mapping` entries touching S0-08 (`seeds/seed-stage0-v1.yaml:575-582`, verbatim)

```yaml
- spike: runsc
  probe: static runsc install attempt plus a trivial runsc container run
  negative_effect: {affected_proof: S0-08, from_class: blocked_host, to_class: blocked_host, rule_id: map-runsc-s008, note: confirms deferral, marker re-probed every CI run}
  positive_effect: {affected_proof: S0-08, class: execution_proof, note: deferral_expired, proof must run}
- spike: dockerd
  probe: start dockerd in-sandbox and run hello-world
  negative_effect: {affected_proof: null, rule_id: map-dockerd-venue, note: venue note only, process-level-first premise holds}
  positive_effect: {affected_proof: S0-08, note: KC-6 re-test whether S0-08 is procurement-blocked or merely container-blocked}
```

Registry copies (`proofs/registry.yaml:31-32, 34`, verbatim — note the reshaped branches and the
coordinator's stated reason at `:28`):

```json
  {"spike": "runsc", "probe": "static runsc install attempt plus a trivial runsc container run", "negative_effect": {"affected_proof": "S0-08", "from_class": "blocked_host", "to_class": "blocked_host", "rule_id": "map-runsc-s008", "note": "confirms deferral, marker re-probed every CI run"}, "positive_effect": {"affected_proof": "S0-08", "from_class": "blocked_host", "to_class": "execution_proof", "rule_id": "map-runsc-s008", "note": "deferral_expired, proof must run"}},
  {"spike": "dockerd", "probe": "start dockerd in-sandbox and run hello-world", "negative_effect": {"affected_proof": null, "rule_id": "map-dockerd-venue", "note": "venue note only, process-level-first premise holds"}, "positive_effect": {"affected_proof": "S0-08", "from_class": "blocked_host", "to_class": "blocked_host", "rule_id": "map-dockerd-venue", "note": "KC-6 re-test: dockerd works but S0-08 stays blocked_host until gVisor proof runs"}},
```

```json
  {"spike": "pc-bridge", "probe": "probe the owner PC for OmniRoute identity and gVisor host capability", "positive_effect": {"affected_proof": "S0-03", "from_class": "blocked_credential", "to_class": "execution_proof", "rule_id": "map-pcbridge-s003"}, "negative_effect": {"affected_proof": "S0-08", "from_class": "blocked_host", "to_class": "blocked_host", "rule_id": "map-pcbridge-s008"}}
```

`proofs/registry.yaml:28` (verbatim, the coordinator note that explains the reshaping):
```
# COORDINATOR DECISION — RULE IDS (2026-09-03, updated 2026-09-04): every branch that names a class carries its rule_id IN THIS FILE (the seed's positive branches had none). The validator honours ONLY transitions declared here — no rule id lives in code (AF-AP-13). The runsc positive branch uses from_class/to_class (not the shorthand class) because the transition is cross-class (blocked_host→execution_proof). The dockerd positive branch declares an identity transition (blocked_host→blocked_host) because Docker working does not unblock S0-08.
```

`proofs/registry.yaml:19` records `"spike_dependencies": ["runsc", "pc-bridge"]` for S0-08 — the
seed's list is `[runsc]` only (`:482`).

### 1.4 Seed constraints binding S0-08 (`seeds/seed-stage0-v1.yaml:110-115`, verbatim excerpts)

```yaml
- S0-08 is blocked on a gVisor-capable host, with owned procurement and a machine-checkable
  NOT-run marker
- Every proof ships a spec-time negative control that fails for a named exact reason
- All gates are deterministic and LLM-free; no LLM judge anywhere in the gate spine
- Every acceptance criterion is either executable in this environment or explicitly
  deferred with a machine-checkable reason
```

Seed acceptance criterion for blocked markers (`seeds/seed-stage0-v1.yaml:154-164`, verbatim):

```yaml
- description: S0-03 and S0-08 are specified as blocked with a machine-checkable NOT-run
    marker that distinguishes credential-absent from credential-rejected and turns
    RED once the blocker disappears
  semantic_ac_key: ac_bb8de4775a2c69e5
  verify_command: python3 -c "import glob; t=open(sorted(glob.glob('seeds/seed-stage0*.yaml'))[-1]).read();
    assert 'S0-03' in t and 'S0-08' in t; assert 'not_run' in t or 'NOT-run' in t
    or 'not-run' in t; assert 'gVisor' in t or 'gvisor' in t; print('BLOCKED MARKERS
    OK')"
  expected_artifacts:
  - seeds
  output_assertion: BLOCKED MARKERS OK
```

Seed evaluation principle for blocked proofs (`seeds/seed-stage0-v1.yaml:283-287`, verbatim):

```yaml
- name: Blocked means fail-closed
  description: A blocked proof records an actual attempted probe distinguishing blocker-absent
    from blocker-rejected, and flips RED the moment the blocker lifts, never becoming
    a permanent excuse
  weight: 0.9
```

---

## 2. THE BREAKDOWN

### 2.1 Increment #17 (`tasks/stage0-breakdown.md:68`, verbatim row)

```
| 17 | S0-08 gVisor spec + fixtures | `proofs/s0-08/` containment test spec + canaries, lint-checked; marker live from #2 | Spec + fixtures parse and lint; marker's probe re-runs every CI run | Stage-1 grep-gate FAILS when marker absent/malformed; runsc appearing ⇒ `deferral_expired` | deferred run (owner TBD-owner-gvisor-host); spec increment in-sandbox |
```

### 2.2 Increment #5 — the gating spike (`tasks/stage0-breakdown.md:56`, verbatim row)

```
| 5 | Spike: runsc | `spikes/runsc/result.json` | static runsc install attempt + trivial run; confirms/expires S0-08 deferral via `map-runsc-s008` | as above | in-sandbox (Wave 0) |
```

(`as above` refers to `:54`'s cell: "spike-errored (crash/timeout) is distinct from
spike-negative and blocks only S0-06".)

### 2.3 Pinned decision on blocked markers (`tasks/stage0-breakdown.md:22`, verbatim)

```
| Blocked markers carry a probe run re-evaluated every CI run; `credential_rejected` ⇒ proof-RED, never blocked; blocker gone ⇒ `deferral_expired` RED | Static marker checked for presence | interview Q5 |
```

Also (`:20`, verbatim):
```
| Spikes classify, never gate; frozen `spike_to_class_mapping` applied mechanically; undeclared transitions need a reviewed commit | All spikes must pass before Wave 1 (runsc would deadlock Stage 0) | interview Q2 |
```

Full table: `material-S0-02.md` §2.2.

### 2.4 Owner answer (`tasks/stage0-breakdown.md:88`, verbatim)

```
- **#17 / KC-1:** gVisor host = the PC (bare metal, KVM). S0-08 runs live via the bridge.
```

Original (now-answered) question kept in the file (`:93`, verbatim):
```
- **#17 / KC-1:** is a gVisor-capable host (runsc + KVM) going to be procured, by whom, by when? Until then S0-08 is spec+fixtures with a re-probed NOT-run marker.
```

**Recorded:** the answer's parenthetical says "bare metal, KVM"; the live probe
(`spikes/pc-bridge/result.json:17`) records `/dev/kvm` ABSENT with the modules unloaded, and
`PC-BRIDGE.md:148-149` records the platform actually used as "systrap (runsc default;
`/dev/kvm` absent)".

### 2.5 Venue update clause (`tasks/stage0-breakdown.md:30-31`, verbatim excerpt)

```
Bridge-side (via `scripts/pc.sh`, results still written as
`result.json` with `env_fingerprint = pc-bridge:<host>`): the runsc/KVM spike and S0-08's live
run (#5, #17);
```

### 2.6 Ordering rationale clause (`tasks/stage0-breakdown.md:75`, verbatim excerpt)

```
#17 spec now, run
later;
```

### 2.7 NOT-built ledger lines touching S0-08

Breakdown-time (`:79-82`): "Nothing below exists yet: … any spike, any proof, any fixture …".
Live (`todo/BUILD-TASKLIST.md:32`, verbatim excerpt): "**BLOCKED 2 — S0-03 (credential) and S0-08
(host; marker EXPIRED).**"

Live rows (`todo/BUILD-TASKLIST.md:62, 74`, verbatim excerpts):
```
| s0-05-spike-runsc | #5 spike runsc install (sandbox + PC confirmed) | DONE 2026-09-04 — POSITIVE: runsc release-20260817.0 downloaded and runs rootless in sandbox (systrap, 4.19.0-gvisor kernel); PC also has it (owner-installed). S0-08 deferral expired → `execution_proof` per map-runsc-s008 | s0-02 | `spikes/runsc/result.json` present; classification_effect applied |
```
```
| s0-17-s0-08-gvisor | #17 S0-08 containment spec + fixtures; live run on the PC after the runsc spike | pending | s0-02, s0-05 | marker re-probed every CI run; grep-gate fails on missing marker |
```

`todo/BUILD-TASKLIST.md:566` (verbatim excerpt): "container-blocked. Venue note for S0-08."
`todo/BUILD-TASKLIST.md:571` (verbatim excerpt): "same release). Classification effect: S0-08
deferral EXPIRED → `execution_proof` per"
`todo/BUILD-TASKLIST.md:597` (verbatim excerpt): "cgroups rootless). Effect: S0-08 is no longer
blocked on capability once spike #5 lands its artifact"
`todo/BUILD-TASKLIST.md:255` (verbatim excerpt, an S0-08 observation recorded during S0-01): "the
pinned hermes-acp ran a terminal tool with no policy gate (S0-08 territory)."
`todo/BUILD-TASKLIST.md:480` (verbatim excerpt): "gVisor+userns at the PC boundary (S0-08) and
listed as not-verified in `runner_design.md`."

---

## 3. FINDINGS + COUNCIL

### 3.1 Per-proof constraint (`docs/research/FINDINGS-STAGE0-v1.md:49`, verbatim)

```
| S0-08 | gVisor compatibility | Hermes container root-start/s6 → drop to `hermes` under runsc; escape canaries fail (`02` §2, `05` §5) — environment-gated, see §2 |
```

### 3.2 Environment rows (`docs/research/FINDINGS-STAGE0-v1.md:24-28`, verbatim)

```
| Docker CLI 29.3.1 | present, **daemon NOT running** (no /var/run/docker.sock) | Compose topologies unavailable unless dockerd-in-sandbox proves out (untested); plan spikes process-level first |
| runsc (gVisor) | ABSENT; /dev/kvm ABSENT | S0-08 cannot run here as-is; runsc static install + systrap platform is a spike question; otherwise S0-08 needs a real host — surface, never stub |
| bwrap | ABSENT (unshare present) | no bubblewrap isolation for local gates |
| uid | 0 (root) | root-start/priv-drop tests partially representable |
| **PC bridge** (learned 2026-09-03 from the owner) | The owner's PC is the execution host: Fedora 42 bare metal (KVM), podman + podman-compose, local vLLM OpenAI-compatible endpoint `localhost:8010/v1` (`sim9b`), reached via a token-gated HTTP bridge with per-session ephemeral links (`PC-BRIDGE.md`) | S0-08 (runsc/KVM), all container stacks (Buzz relay, OmniRoute, ai-memory), and S0-03's model upstream run THERE. No third-party model credential is needed: OmniRoute's upstream = the PC's vLLM, identity asserted as `sim9b` |
```

Capability ledger: `material-S0-02.md` §3.1.

### 3.3 Cross-cutting invariants (`docs/research/FINDINGS-STAGE0-v1.md:62-69`, verbatim excerpts)

```
- Negative-control discipline: S0-02/S0-05/S0-08 are *defined by* their failing legs; every
  other proof needs at least one violating fixture failing for the exact expected reason.
- Environment blockers are surfaced, not routed around: if gVisor (or dockerd) cannot run here,
  the proof is delivered as spec + fixture + explicit `NOT run here: <reason>` + host runbook,
  never a fake green.
```

### 3.4 Findings PATH-2 resolution (`docs/research/FINDINGS-STAGE0-v1.md:79-82`, verbatim excerpt)

```
**PATH 2 — RESOLVED by the owner 2026-09-03 ("the system runs on my PC via the PC bridge"):**
gVisor host = the PC (bare-metal Fedora 42, KVM); S0-03 credential = the PC's local vLLM behind
OmniRoute (no third-party key); container stacks = podman on the PC.
```

### 3.5 Council lines that touch S0-08 (verbatim)

Acceptable compromise 1 (`docs/research/COUNCIL-VERDICT-STAGE0-v1.md:26`):
```
1. **S0-08's live run is deferred; its resolution is not.** Spec + fixture + a machine-checkable `NOT run here: <reason>` marker is accepted evidence *only* when paired with procurement of a real gVisor host as a named Wave-0 action item. Socrates' distinction — deferring the run ≠ deferring the resolution — carried unopposed.
```

Kill Criterion 6 (`:38`):
```
6. **If the dockerd-in-sandbox Wave-0 spike succeeds**, the process-level-first premise weakens — within that session, re-test whether S0-08 is procurement-blocked or merely container-blocked.
```

Unresolved question 5 (`:49`):
```
5. **Does a real gVisor host exist to procure?** Socrates demanded a named owner and date. The transcript contains no owner. Procurement is asserted as possible, never as available.
```

Recommended next step 5 (`:59`, the S0-08 clause) — quoted verbatim in `material-S0-02.md` §3.6:
"S0-08's `NOT run here` marker is grep-checked and gates Stage 1."

Chairman reservation (`:88`) — quoted verbatim in `material-S0-03.md` §3.6; it names S0-08's host
as one of the two unowned external dependencies.

Follow-up Trigger A (`:97`, verbatim excerpt): "if the selective-egress spike fails (KC-1) or
dockerd succeeds (KC-6), the wave plan's premises changed and the panel should re-cut Waves 1-2 on
the new capability table, with a seat added to argue schedule cost."

Recommended next step 3 (`:57`, verbatim) — the denominator S0-08 counts toward:
```
3. Resolve the classification arithmetic to a **four-way** ledger — execution / conformance-checked decision / blocked-on-external-input (S0-03) / blocked-on-capability (S0-08, provisionally S0-06) — with separate denominators and no flat "N/12" anywhere.
```

---

## 4. PLAN-DOC SEAMS AND PINS

### 4.1 `docs/05_SECURITY.md:56-72` (verbatim — §5 containment profiles, the spec S0-08 encodes)

```
## 5. Containment profiles

### Production Hermes

Run the entire Hermes runtime under `runsc`. Validate root-start/s6 setup, privilege drop to `hermes`, required tools, narrow mounts, no Docker socket/home/provider secrets, resource limits, and enforced egress. This is whole-runtime containment, not per-tool isolation.

### Dream and Foundry workers

Use separate gVisor profiles with immutable sanitized inputs, scratch-only writes, no production network, no production credentials, strict CPU/memory/time/process limits, and artifact-only output. Destroy the worker after each job.

### Candidate/evaluation runners

Separate candidate execution from evaluator/rubric execution. Neither receives production credentials or network membership. Evaluators consume exported artifacts rather than sharing the candidate's writable workspace.

### Conditional HarnessRouter

Do not deploy until an approved candidate requires UHP. At activation, verify the official one-container topology, root-to-session-user privilege drop, UHP request semantics, session isolation, resource cleanup, and model egress through OmniRoute.
```

### 4.2 `docs/05_SECURITY.md` other verbatim lines

`:7` — "3. Compromised runtime and research code is contained from host, other scopes, secrets, and unrestricted egress."
`:25` — "| Malicious JIT/evaluator/rubric code | gVisor, no host network/secrets, read-only inputs, separate evaluator | Ephemeral teardown, escape/exfiltration tests |"
`:106` — "- gVisor host-read/escape and evaluation exfiltration canaries fail."

### 4.3 `docs/02_COMPONENT_AUDIT.md` (verbatim lines)

`:32` — "- The container starts as root for s6/UID setup, then services drop to `hermes`; test that exact lifecycle under gVisor."
`:78-80` (verbatim):
```
### gVisor and policy service — selected security controls

gVisor initially contains the whole Hermes runtime, including tools; it is not per-tool isolation without a broker. The first-party policy service provides fail-closed semantic authorization. Research/evaluation workers also use isolated gVisor profiles.
```
`:144` (verbatim, §6 Audit limits): "This is a source-level planning audit, not production
qualification. No target-host Docker/gVisor deployment, live Buzz relay, live provider, end-to-end
ACP turn, four-scope adapter, JIT run, dream cycle, or hardened evaluation execution has yet
passed. The build plan makes those executable gates rather than assumptions."

### 4.4 `docs/01_ARCHITECTURE.md` (verbatim lines)

`:24` — "| Tool security | Policy service + gVisor | Fail-closed authorization and runtime containment |"
`:85` — "    Hermes->>Hermes: Execute allowed tool in gVisor"
`:121` — "| Runtime → host/network | gVisor, narrow mounts, resource limits, controlled egress |"

### 4.5 `docs/09_PREMORTEM.md` (verbatim lines)

`:18` — "| 12 | gVisor incompatibility causes bypass | Developers switch to default runtime | Target-host proof; no waiver without ADR |"
`:20` — "| 14 | AlphaEval/rubric compromises host or secrets | Runner uses host network/777/shared env | Separate gVisor candidate/evaluator, minimal UID/GID, test credentials |"
`:41` (stop-the-line) — "- production or research containment is bypassed."

### 4.6 `docs/07_BUILD_PLAN.md:16` (verbatim)

```
| S0-08 | gVisor compatibility | Hermes root-init/drop and required tools work; escape canaries fail |
```

### 4.7 `docs/06_EVALUATION.md:16` (verbatim — the adjacent gVisor requirement)

```
- run rubric code in a separate unprivileged gVisor sandbox;
```

`docs/10_HARNESS_FOUNDRY.md:67` (verbatim): "- JIT runs offline in an ephemeral gVisor worker."

### 4.8 ADR / decision-log entries

`docs/08_DECISION_LOG.md:16` (verbatim): "| D-010 | gVisor contains the whole Hermes runtime
initially | Honest achievable boundary; per-tool isolation requires a broker |"
`docs/08_DECISION_LOG.md:42` (owner input still needed, verbatim): "2. Initial deployment target
and Docker `runsc` availability."
**No ADR under `docs/adr/` is specifically about gVisor containment — NOT SPECIFIED in `docs/adr/`.**

### 4.9 `upstream.lock.yaml:39-43` (verbatim)

```yaml
  gvisor:
    repository: https://github.com/google/gvisor.git
    commit: 80bb741691be65cedb6688ac518bef3664af0fcc
    license: Apache-2.0
    role: runtime_and_research_worker_containment
```

**Recorded:** the pin is a source commit; the artifact actually installed on both venues is a
release binary — `spikes/runsc/result.json:30-31` records `"runsc_version":
"release-20260817.0"`, `"oci_spec": "1.2.1"`, and `PC-BRIDGE.md:127-130` records the same release
installed by the owner. No line in `upstream.lock.yaml` maps `80bb7416…` to
`release-20260817.0` — **NOT SPECIFIED in `upstream.lock.yaml`.**

`upstream.lock.yaml:10-15` pins `hermes-agent` (the runtime whose container lifecycle S0-08
tests) at `527da60844d4dced37879ea50259675371abe10e` (v0.21.0).

---

## 5. WHAT EXISTS TODAY

### 5.1 `ls -la proofs/S0-08/`

```
total 20
drwxr-xr-x  2 root root 4096 Sep  3 18:40 .
drwxr-xr-x 11 root root 4096 Sep  4 20:00 ..
-rw-r--r--  1 root root  787 Sep  3 18:40 blocked.json
-rw-r--r--  1 root root  208 Sep  3 18:40 probe.json
-rwxr-xr-x  1 root root  127 Sep  3 18:40 probe_runsc.sh
```

No `spec.json`, no containment spec document, no canary fixtures, no `result.json`.

### 5.2 Verbatim content of every file in `proofs/S0-08/`

**`proofs/S0-08/blocked.json`:**

```json
{
  "proof_id": "S0-08",
  "classification": "blocked_host",
  "env_fingerprint": "pc-bridge:fedora",
  "marker": {
    "probe_cmd": [
      "sh",
      "proofs/S0-08/probe_runsc.sh"
    ],
    "probe_run": {
      "leg": "negative",
      "cmd": [
        "sh",
        "proofs/S0-08/probe_runsc.sh"
      ],
      "started_at": "2026-09-03T18:33:34.707753Z",
      "finished_at": "2026-09-03T18:33:34.722402Z",
      "exit_code": 0,
      "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    "blocker_status": "expired",
    "unblock_condition": "runsc executable and a trivial runsc container run succeeds",
    "owner": "TBD-owner-gvisor-host"
  }
}
```

**Facts recorded from this file, without interpretation:** `blocker_status` is `"expired"`
(probe exit code 0); the optional `reason` field is ABSENT (the runner only writes it when
`reason_map` maps the exit code — `scripts/proof-runner:262-263` — and `0` is not in the map);
`env_fingerprint` is `pc-bridge:fedora`; both output digests are the sha256 of the empty string.

**`proofs/S0-08/probe.json`:**

```json
{
  "proof_id": "S0-08",
  "probe_cmd": [
    "sh",
    "proofs/S0-08/probe_runsc.sh"
  ],
  "timeout_s": 10,
  "reason_map": {
    "10": "capability_absent",
    "11": "capability_present_but_failing"
  }
}
```

**`proofs/S0-08/probe_runsc.sh`:**

```sh
#!/bin/sh
if ! command -v runsc >/dev/null 2>&1; then
    exit 10
fi
if ! runsc --version >/dev/null 2>&1; then
    exit 11
fi
```

(No trailing explicit `exit 0`; the script falls off the end after the two guards.)

### 5.3 Registry entry (`proofs/registry.yaml:19`, verbatim)

```json
  {"proof_id": "S0-08", "title": "gVisor compatibility", "classification": "blocked_host", "wave": 2, "spike_dependencies": ["runsc", "pc-bridge"], "required_negative_controls": 1, "assertion_count": 1, "blocked": {"owner": "TBD-owner-gvisor-host", "unblock_condition": "runsc executable and a trivial runsc container run succeeds", "marker_path": "proofs/S0-08/blocked.json"}},
```

Ledger state (`proofs/ledger.json`):
```json
    {
      "classification": "blocked_host",
      "normalized_digest": "110d5b2bd415fe16ae315f620cbe705d857f70bb430d233c40eab2163388ece8",
      "proof_id": "S0-08",
      "state": "EXPIRED"
    },
```

### 5.4 Schemas

`blocked.schema.json` and `probe.schema.json` verbatim: `material-S0-03.md` §5.4.
`spec.schema.json` / `result.schema.json` verbatim: `material-S0-02.md` §5.3.
`spike.schema.json` verbatim: `material-S0-05.md` §5.3.

The two schema clauses that bind S0-08's current artifact:
- `blocked.schema.json:19` — `"blocker_status": {"enum": ["absent", "rejecting", "expired"]}`.
- `blocked.schema.json:20` — `reason` is OPTIONAL and its enum is
  `["credential_absent", "credential_rejected", "capability_absent",
  "capability_present_but_failing"]`.

### 5.5 Exemplars

S0-07 / S0-11 (execution) and S0-09 (decision): verbatim `spec.json`, checker skeletons and
S0-07's attestation block in `material-S0-02.md` §5.4.

S0-11 is the committed example of a *design-document + isolation-fixture* proof: its inputs are
`proofs/S0-11/runner_design.md` (9,262 bytes), `proofs/S0-11/fixtures/`, and
`proofs/S0-11/check_eval_hardening.py`, and its checker contains a design-document conformance
leg (`check_runner_design` L336-350) and a machine-readable policy-block parser
(`_extract_policy` L353-362) alongside the runtime isolation legs.

### 5.6 Runner and validator — how an EXPIRED marker behaves

`scripts/proof-runner:226-271` (probe path, verbatim) — `material-S0-03.md` §5.6. The line that
produced this marker (`:248-249`, verbatim):

```python
    if run["exit_code"] == 0:
        blocker_status = "expired"
```

`scripts/validate-ledger:328-339` (verbatim) — an expired deferral is honest for `integrity`:

```python
            blocker_status = artifact.get("marker", {}).get("blocker_status")
            # COORDINATOR DECISION (2026-09-03, increment #2a): an expired deferral is an honest
            # STATE for `integrity` (the marker is well-formed and truthful: the blocker is gone)
            # and a RED for `stage1-gate` (the proof must now run). Reporting it as an integrity
            # finding made the committed tree's integrity red forever, contradicting the split-check
            # design (integrity green when honest, even empty; the gate carries the RED).
            expired = blocker_status == "expired"
```

`scripts/validate-ledger:460-478` (verbatim) — and RED for the Stage-1 gate:

```python
def stage1_gate(root):
    registry, states, findings = _inspect(root)
    if findings.items:
        for finding in sorted(findings.items):
            print(finding)
        return 1
    missing = []
    for proof in registry["proofs"]:
        expected = "BLOCKED" if proof["classification"].startswith("blocked_") else "PRESENT"
        state = states.get(proof["proof_id"])
        if state == "EXPIRED":
            missing.append(
                f"missing: {proof['proof_id']} ({proof['classification']}; deferral expired — the proof must run)"
            )
        elif state != expected:
            missing.append(f"missing: {proof['proof_id']} ({proof['classification']})")
    for line in missing:
        print(line)
    return 2 if missing else 0
```

Also (`scripts/validate-ledger:449-453`, verbatim) — the numerator counts `BLOCKED`, not
`EXPIRED`:

```python
            numerator = sum(
                1 for proof in registry["proofs"]
                if proof.get("classification") == classification
                and states.get(proof.get("proof_id")) in ("PRESENT", "BLOCKED")
            )
```

CI wiring: `.github/workflows/stage0-ci.yml:47-61` (integrity, must be green) and `:63-65`
(`stage1-gate`, `continue-on-error: true`) — quoted in `material-S0-02.md` §5.6.

**NOT SPECIFIED anywhere in the tree:** a literal `NOT run here:` grep-gate. The seed's negative
control names the string `'NOT run here: runsc unavailable (no KVM, install blocked)'`
(`seeds/seed-stage0-v1.yaml:491`) and the breakdown names a "Stage-1 grep-gate" (`:68`);
`grep -rn "NOT run here" scripts/ .github/ proofs/` finds the string in no gate implementation —
the machine check that exists is `validate-ledger stage1-gate`'s state comparison quoted above.

---

## 6. VENUE FACTS

### 6.1 Which host each leg needs

`PC-BRIDGE.md:60` (verbatim): "| Bare-metal Fedora 42 → KVM available (verify `/dev/kvm`) | gVisor
`runsc` install + the S0-08 containment run happen HERE |"
`PC-BRIDGE.md:69` (verbatim excerpt): "- **PC via bridge:** `runsc`/KVM spike + S0-08 live run …"

### 6.2 The PC-side runsc install and the verified rootless run (`PC-BRIDGE.md:112-149`, verbatim)

```
### gVisor install (owner-run, needs sudo)

The release binaries are staged and checksum-verified in `~/gvisor-install` (`runsc
release-20260817.0`, sha512 OK). The owner runs:

```bash
sudo install -m 0755 -o root -g root ~/gvisor-install/runsc /usr/local/bin/runsc
sudo install -m 0755 -o root -g root ~/gvisor-install/containerd-shim-runsc-v1 /usr/local/bin/containerd-shim-runsc-v1
sudo restorecon -v /usr/local/bin/runsc /usr/local/bin/containerd-shim-runsc-v1
runsc --version
```

The user-level podman runtime entry is already written (`~/.config/containers/containers.conf`:
`runsc = ["/usr/local/bin/runsc"]`). Optional, not required: `sudo modprobe kvm_amd`.

**Status 2026-09-03: `runsc` INSTALLED by the owner (`/usr/local/bin/runsc`, root:root, `bin_t`, sha256
`048b89aa…` = the staged file; `runsc version release-20260817.0, spec 1.2.1`). The shim was not
installed — podman does not need it (it is for containerd/docker); install it only if Docker ever
enters the picture. Silent success is normal: `install` and `restorecon` print nothing.**

**Verified rootless gVisor run (the runsc spike's positive control):**

```bash
podman run --rm --runtime /usr/local/bin/runsc --runtime-flag ignore-cgroups \
  --security-opt label=disable docker.io/library/alpine:3.20 sh -c 'uname -r; echo runsc-ok'
# -> 4.19.0-gvisor / runsc-ok   (dmesg inside: "Starting gVisor..."; HTTPS to example.com from inside: ok)
# negative control: the same command on the default runtime (crun) prints the HOST kernel 6.17.11-200.fc42
```

Two caveats, stated first-class for the S0-08 spec: (1) `--security-opt label=disable` — runsc refuses
an OCI spec carrying an SELinux process label (`FetchSpec failed: SELinux is not supported`), so the
gVisor sandbox, not SELinux, is the container's confinement; the host still confines the runsc process.
(2) `--runtime-flag ignore-cgroups` — rootless runsc cannot set up cgroups here (systemd driver: `Interactive
authentication required`; cgroupfs: root `cgroup.subtree_control` denied; `--cgroups=disabled` rejected by
runsc), so NO resource limits apply in this configuration even though `user@1000.service` delegates
`cpu io memory pids`. The production shape (delegated systemd cgroups or rootful) is a Wave-0 spike
question; the containment proof itself does not depend on cgroups. Platform: systrap (runsc default;
`/dev/kvm` absent).
```

`PC-BRIDGE.md:164-169` (the process-kill rule on this shared host) — verbatim in
`material-S0-02.md` §6.1.

### 6.3 What the Wave-0 spikes proved for S0-08

**`spikes/runsc/result.json` (verbatim, whole file):**

```json
{
  "spike_id": "runsc",
  "schema": "proofs/schemas/spike.schema.json",
  "outcome": "positive",
  "ran_at": "2026-09-04T08:25:05+00:00",
  "env_fingerprint": "ccr-sandbox:linux:6.18.44-fc-v24",
  "runs": [
    {
      "command": "curl -fsSL -o /tmp/runsc https://storage.googleapis.com/gvisor/releases/release/latest/x86_64/runsc",
      "exit_code": 0,
      "stdout_digest": "empty"
    },
    {
      "command": "/tmp/runsc --version",
      "exit_code": 0,
      "stdout_digest": "04f241b14923f59833180e9b98db87c13af5dd5299c1af95f6910d3824dc7c6d"
    },
    {
      "command": "/tmp/runsc --rootless do /bin/true",
      "exit_code": 0,
      "stdout_digest": "75a945167a71ca011fa66ec16c3589ce73287b1e585349e52ac64d558795d144"
    },
    {
      "command": "/tmp/runsc --rootless do uname -r",
      "exit_code": 0,
      "stdout_digest": "9c8baf29a8924748fc00eb3844bc9c83e3eedc43e6a3602569887dcbf2e65c7e"
    }
  ],
  "facts": {
    "runsc_version": "release-20260817.0",
    "oci_spec": "1.2.1",
    "platform": "systrap (inferred; no KVM, no /dev/kvm)",
    "rootless": true,
    "sandbox_network": "not supported rootless (host network used)",
    "gvisor_kernel": "4.19.0-gvisor",
    "host_kernel": "6.18.44-fc-v24",
    "kvm": "ABSENT",
    "install_method": "static binary download (no package manager)"
  },
  "classification_effect": [
    {
      "affected_proof": "S0-08",
      "from_class": "blocked_host",
      "to_class": "execution_proof",
      "rule_id": "map-runsc-s008",
      "reason": "deferral_expired: runsc installs and runs in the sandbox (rootless, systrap platform); the containment proof must run"
    }
  ],
  "not_verified": [
    "Docker + runsc integration (--runtime=runsc not tested; requires Docker daemon configuration)",
    "Podman + runsc integration (podman absent in sandbox; available on the PC)",
    "Network namespace isolation under gVisor (rootless mode uses host network)",
    "cgroup enforcement under gVisor rootless"
  ]
}
```

**`spikes/dockerd/result.json` (verbatim, whole file):**

```json
{
  "spike_id": "dockerd",
  "schema": "proofs/schemas/spike.schema.json",
  "outcome": "positive",
  "ran_at": "2026-09-04T08:25:25+00:00",
  "env_fingerprint": "ccr-sandbox:linux:6.18.44-fc-v24",
  "runs": [
    {
      "command": "dockerd --log-level error (backgrounded, 30s timeout)",
      "exit_code": 0,
      "stdout_digest": "empty"
    },
    {
      "command": "docker info",
      "exit_code": 0,
      "stdout_digest": "a632de89aa25037e4e2c2f8db76d7f455bd625d9efadfb6e794a54f48ac3adc2"
    },
    {
      "command": "docker run --rm hello-world",
      "exit_code": 0,
      "stdout_digest": "0a8d675a2077a48c8e8a813ef6fd095cc6b5c456f685e6eff55ddc9363cb8fed"
    }
  ],
  "facts": {
    "docker_version": "29.3.1",
    "storage_driver": "overlayfs",
    "cgroup_driver": "cgroupfs",
    "security_options": [
      "seccomp (builtin profile)"
    ],
    "network": "outbound pull from Docker Hub succeeded",
    "kvm": "ABSENT (/dev/kvm not present)"
  },
  "classification_effect": [
    {
      "affected_proof": "S0-08",
      "from_class": "blocked_host",
      "to_class": "blocked_host",
      "rule_id": "map-dockerd-venue",
      "reason": "KC-6 re-test: dockerd works in the sandbox — S0-08 is not container-blocked; gVisor containment proof can use Docker as the runtime if needed"
    }
  ],
  "not_verified": [
    "Docker Compose (not tested)",
    "Container networking beyond outbound pull (no port-mapping or inter-container test)",
    "Privileged container or --security-opt modes",
    "Docker-in-Docker nesting"
  ]
}
```

**`spikes/pc-bridge/result.json:37-43` (verbatim — the S0-08 branch):**

```json
  {
   "affected_proof": "S0-08",
   "from_class": "blocked_host",
   "to_class": "blocked_capability",
   "rule_id": "map-pcbridge-s008",
   "reason": "host reachable but runsc absent; KVM modules unloaded (owner sudo). gVisor systrap platform needs no KVM -> runsc install spike moves to the PC"
  },
```

and its host facts (`spikes/pc-bridge/result.json:15, 17, 21, 25`, verbatim):

```json
  "host": "fedora (rocco), kernel 6.17.11-200.fc42.x86_64, up 51 days, 12 cores, 125 GB RAM, 701 GB free on /home, SELinux Enforcing",
  "kvm": "/dev/kvm ABSENT; CPU has SVM (12 flags); kvm/kvm-amd modules present on disk but NOT loaded -> fix is `sudo modprobe kvm_amd` (sudo needs the owner's password)",
  "runsc": "ABSENT",
  "sudo": "NEEDS_PASSWORD (no NOPASSWD)",
```

**Recorded, not resolved:** the `pc-bridge` spike's declared effect is
`blocked_host → blocked_capability`, which the registry's `class_aliases`
(`"blocked_capability": "blocked_host"`, `:9`) normalizes to `blocked_host → blocked_host`,
matching the declared `map-pcbridge-s008` transition (`:34`). The `runsc` spike declares
`blocked_host → execution_proof` on `map-runsc-s008`, also declared (`:31`). Both artifacts are
present and both transitions are declared, so `scripts/validate-ledger:373-393` raises no
`undeclared-transition` finding; the registry still classifies S0-08 `blocked_host` (`:19`) and
the ledger reads `EXPIRED`.

### 6.4 The blocked marker's stated reason

`proofs/S0-08/blocked.json` carries **no `reason` field** (the marker's `blocker_status` is
`"expired"`, exit code `0`, which `proofs/S0-08/probe.json`'s `reason_map` does not name). The
seed's `reason_enum` for S0-08 is `[capability_absent, capability_present_but_failing]`
(`seeds/seed-stage0-v1.yaml:494`), and its negative-control string is
`'NOT run here: runsc unavailable (no KVM, install blocked)'` (`:491`) — a reason the current
marker does not and cannot record, because the probe now exits 0.

### 6.5 Observability

`docs/OBSERVABILITY-RUNBOOK.md:44-46` (verbatim): "`NOT built.` here: no exporter, no envelope
emitter, no dashboards wired — this runbook records the live PC endpoints and the lessons so the
first telemetry increment starts from facts."

---

## 7. CLASS PREFLIGHT

**The 18 defect classes** — verbatim in `material-S0-02.md` §7.2-§7.3.
**Mint-wide AF-AP rows** (AF-AP-36, AF-AP-56, AF-AP-27, AF-AP-29, AF-AP-30) — verbatim in
`material-S0-02.md` §7.5.

### 7.1 AF-AP rows whose mechanism names the S0-08 subject (gVisor, containment, venue classification, escape canaries)

`docs/INCIDENT-LOG.md:148` (AF-AP-4 — the class that governs a `blocked_host` label; its own
greppable signature names this proof's classification):
```
| AF-AP-4 | sandbox-probe-as-world: venue classification from the sandbox alone while the owner's live host holds the capability | any "blocked_host/blocked_credential" label with no PC-bridge probe record | findings v1 §2 + council KC-1/KC-2 | SWEPT(2026-09-03) — spike #0 |
```

`docs/INCIDENT-LOG.md:166` (AF-AP-22 — tautological isolation/reachability assertion; the class an
escape/host-read canary sits in): quoted verbatim in `material-S0-05.md` §7.1.

`docs/INCIDENT-LOG.md:172` (AF-AP-28 — a security assertion that trusts the SUBJECT's self-report;
a container reporting its own confinement): quoted verbatim in `material-S0-05.md` §7.1.

`docs/INCIDENT-LOG.md:168` (AF-AP-24 — proxy capability preflight, and the runner-level DEFER
contract for an incapable venue; five reopen cycles recorded): quoted verbatim in
`material-S0-05.md` §7.1.

`docs/INCIDENT-LOG.md:169` (AF-AP-25 — the only registry row whose text names gVisor, verbatim):
```
| AF-AP-25 | regex-list gate where a PARSER is required — a security check scans structured input (Python, YAML, JSON) with regexes, so real calls/keys in a form the regex does not spell out slip through, and the checker must self-exclude to avoid matching its own pattern strings | a `re`-only sweep over `.py`/`.yaml` for security ops; a checker that excludes itself from its own sweep | S0-11 round-2 sweep missed `os.chmod(…,0o777)`, `subprocess.run(["chmod","-R","0777"])`, `hostNetwork: True`; self-exclusion hid an op in the checker file | SWEPT(2026-09-04) — Python via AST (call-based, ignores string literals → no self-exclusion), YAML via `safe_load` walk, regex only for shell/text. **Round-3 extension:** even AST is specimen-matching (missed `import subprocess as sp`, `from subprocess import run`, `cmd=[…]; run(cmd)`, `mode=0o777`, `0o700\|0o077`, `network_mode: ${VAR:-host}`, and prose "isolation unnecessary / chmod 777 mandatory"). Two-part fix: (a) the DESIGN gate is now a machine-readable ```yaml `policy:` block the checker parses — prose cannot satisfy or invert it; (b) the sweep is reframed as a BEST-EFFORT LINT (alias resolution + constant folding added) whose limits are stated — the real boundary is the runtime isolation + gVisor, not a complete static scan. `test_sweep_catches_mutant` (12 equivalents), `test_runner_design_{ignores_inverted_prose,rejects_permissive_policy,rejects_missing_policy}`. Siblings OPEN: S0-09/S0-10 checkers still use regex matching (owner "3 checkers"). Design signature |
```

`docs/INCIDENT-LOG.md:170` (AF-AP-26 — permissive-default / relative-only security predicate; the
`uid != parent` vs `uid != 0` distinction is exactly S0-08's privilege-drop assertion): quoted
verbatim in `material-S0-05.md` §7.1.

`docs/INCIDENT-LOG.md:203` (AF-AP-59 — world-scoped enumeration asserted against an empty world;
the class for any process/port/mount census inside or outside a container):
```
| AF-AP-59 | world-scoped enumeration asserted against an empty world — a test over a system-wide listing (ps/proc rows, listening ports, a directory walk, a pinned-path census) asserts the WHOLE result equals its own spawn set, which holds only when the test is alone on the box; a parallel venue (xdist workers, a sibling lane's live tee) puts admissible foreign rows in the result | `assert rows == []` / `assert {row[0] for row in rows} == {…}` over a scan that keeps rows by a world-wide rule; a `pinned_present == 0` style assertion — screen signature (TEST_SCREEN): a `pgrep`/`pkill` argv or shell string carrying `-f` in any position (extended 2026-09-07 after VERIFY-B5h F2/F3a: a double-quoted world-scoped `pkill -f` and `pgrep -a -f` had slipped it), `ps -e*`; `pgrep -P <own pid>` stays legal | assert the owned subset exactly and the ADMISSIBILITY of every other row under the producer's rules (an unexplained row still fails); gate on the serial venue AND the parallel venue | 2026-09-07 PC run 20260907T161133Z gw6 (a sibling worker's frame_tee.py sleeper in the teardown body); fix in tests/test_s0_01_pc_post_scan.py |
```

`docs/INCIDENT-LOG.md:188` (AF-AP-44 — module-scope environment probe that RAISES; the class for a
`runsc`/`/dev/kvm` availability probe at import time): quoted verbatim in `material-S0-06.md` §7.2.

`docs/INCIDENT-LOG.md:178` (AF-AP-34 — name-based process kill on the shared PC host, which S0-08's
container teardown meets): quoted verbatim in `material-S0-02.md` §7.4.

`docs/INCIDENT-LOG.md:184` (AF-AP-40 — presence-gated check; a required canary artifact made
optional): quoted verbatim in `material-S0-04.md` §7.1.

`docs/INCIDENT-LOG.md:154` (AF-AP-10 — one artifact's identity inflating another proof's state;
the marker/result pairing rule for a blocked proof):
```
| AF-AP-10 | one artifact's identity inflating another proof's state (payload `proof_id` ≠ its directory) | `proofs/<id>/{result,blocked}.json` whose `proof_id` differs from `<id>` | lane red-first test, increment #1 (2026-09-03) | SWEPT(2026-09-03) — both artifact paths reject the mismatch (`test_artifact_proof_id_must_match_its_directory`) |
```
