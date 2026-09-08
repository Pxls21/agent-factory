# Lane G1 — S0-08 gVisor containment: spec, canaries, checker, marker gate, PC runner

PIN: `2ff0c31` · sandbox (Opus 4.6 `code-implementer`) · report written 2026-09-08 01:00Z (`date -u`)

**TL;DR.** The spec, eight canaries, the checker, the marker gate, the fixtures and the PC runner are
built and gated: **74 passed** (three runs), **21/21 mutants killed**, pyflakes/`sh -n`/`bash -n` clean,
`ap_screen` 0 production hits, `validate-ledger integrity` rc 0 with the new `spec.json` in place.
**The PC run did not happen — no bridge from this lane** — so the positive leg correctly reports
`deferred: containment evidence not captured` (exit 2).

**Three of the brief's pinned design items were false against the pinned image and were built
differently, deliberately and loudly** (§DISCREPANCIES): `main-hermes` is a root no-op, not the
privilege-drop seam; `import hermes` does not exist; and `mount -t proc` / `unshare -n` are **not**
denied under gVisor — I measured both succeeding. Building P2/P3/P6 as written would have produced
canaries that fail against a correctly-contained container.

---

## FILE IDENTITY (all 18 files NEW; nothing tracked was modified)

> **Amended at `517c65e` by the coordinator (VERIFY-G1 F16):** four rows below describe this
> lane's own PIN `2ff0c31`, not the bytes that shipped — `CONTAINMENT-SPEC.md`
> (`4ba53788f9a385dd`/312), `check_containment.py` (`73ab20c3e88a5f0a`/299), `canaries/P4.sh`
> (`6967eb755a60be25`/57) and `tests/test_s0_08_containment.py` (`aec5799b95e3d48f`/757).
> **Every `file:line` in this report resolves against `517c65e`.** Lane G2 later rewrote
> `check_containment.py`, `P1.sh`, `P2.sh`, `P4.sh`, `run_containment.sh`, `spec.json`,
> `CONTAINMENT-SPEC.md`, the crun fixture and the test file, so these citations do **not** resolve
> against a later HEAD.

| sha256 (16) | lines | file |
|---|---|---|
| `bb84ed9301ba4b15` | 312 | `proofs/S0-08/CONTAINMENT-SPEC.md` |
| `e6204abbee8626d2` | 299 | `proofs/S0-08/check_containment.py` |
| `093d7412f237ede8` | 125 | `proofs/S0-08/marker_gate.py` |
| `016ad55ad7c3a8e2` | 34 | `proofs/S0-08/spec.json` |
| `ff7a9fe20047073e` | 278 | `proofs/S0-08/tools/pc/run_containment.sh` |
| `c01522f048c1533e` | 19 | `proofs/S0-08/canaries/P1.sh` |
| `945440826395447d` | 50 | `proofs/S0-08/canaries/P2.sh` |
| `bac5716ec9cb80ac` | 48 | `proofs/S0-08/canaries/P3.sh` |
| `952aa3cd38532bd4` | 50 | `proofs/S0-08/canaries/P4.sh` |
| `db2d6bb50a00bfad` | 45 | `proofs/S0-08/canaries/P5.sh` |
| `53ba2810b75e4531` | 59 | `proofs/S0-08/canaries/P6.sh` |
| `dd19f775744672b3` | 27 | `proofs/S0-08/canaries/P7.sh` |
| `851f229a358ccfaf` | 29 | `proofs/S0-08/canaries/P8.sh` |
| `aeadecfa1c0a5165` | 8 | `proofs/S0-08/fixtures/evidence-crun/canaries.jsonl` |
| `f747583007770c90` | 23 | `proofs/S0-08/fixtures/evidence-crun/runtime-identity.json` |
| `0d2858d69d08adae` | 31 | `proofs/S0-08/fixtures/evidence-crun/PROVENANCE.md` |
| `21f3965de28195f3` | 14 | `proofs/S0-08/fixtures/malformed-marker/blocked.json` |
| `cbcdbca7183ff003` | 751 | `tests/test_s0_08_containment.py` |

**Boundary held.** `git status --porcelain` shows my paths only as `??` (new); I modified **zero**
tracked files. Every forbidden path byte-identical to `2ff0c31`, verified by sha256:
`blocked.json`, `probe.json`, `probe_runsc.sh`, `registry.yaml`, `scripts/validate-ledger`,
`scripts/proof-runner`, and all five `proofs/schemas/*`.

---

## DONE — property → canary → checker assertion → test

| # | property | canary | checker | test |
|---|---|---|---|---|
| P1 | runs under gVisor | `P1.sh` — `uname -r` + `dmesg` | `check_containment.py:155` — `kernel != GVISOR_KERNEL` | `test_s0_08_containment.py:206-209` |
| P2 | root start → drop to uid 10000 | `P2.sh` — pid-1 uid + main-program uid | `check_containment.py:165-168` — `pid1_uid != "0"` / `main_uid != HERMES_UID` | `P2-UID-ROOT-ACCEPTED` (`test_s0_08_containment.py:210-213`) |
| P3 | required tools work | `P3.sh` — hermes, node, uv | `check_containment.py:179` — `python3 -c import hermes_cli` | `P3-TOOL-BROKEN-ACCEPTED` (`test_s0_08_containment.py:214-215`) |
| P4 | narrow mounts, no socket, no secrets | `P4.sh` — docker.sock + env-key names | `check_containment.py:192` — `if sock != "absent"` | `P4-DOCKER-SOCKET-ACCEPTED` (`test_s0_08_containment.py:216-217`) |
| P5 | host-read FAILS | `P5.sh` — sentinel read | `check_containment.py:230` — `if readable != "no"` (after the host control) | `P5-SENTINEL-READABLE-ACCEPTED` (`test_s0_08_containment.py:218-219`) |
| P6 | no host state via escape | `P6.sh` — devices + mounted procfs | `check_containment.py:238` — `containment: P6 raw host devices present` | `P6-RAW-DEVICE-ACCEPTED` (`test_s0_08_containment.py:220-223`) |
| P7 | egress — RECORDED, NOT ASSERTED | `P7.sh` — interfaces + netns | `check_containment.py:257` — `for cid in RECORDED` | `canary line absent` (`test_s0_08_containment.py:309`) |
| P8 | resource limits — RECORDED, NOT ASSERTED | `P8.sh` — cgroup values | `check_containment.py:257` — `for cid in RECORDED` | `canary line absent` (`test_s0_08_containment.py:309`) |

**Marker gate** — six verdicts, all tested:

| verdict | emitted at |
|---|---|
| `marker: absent` | `marker_gate.py:82` |
| `marker: malformed: {field}` | `marker_gate.py:94` |
| `marker: expired - the proof must run` | `marker_gate.py:102` |
| `marker: completed transition` | `marker_gate.py:79` |
| `marker: malformed: blocker_status {status!r}` | `marker_gate.py:98` |

On the live tree the gate is **RED by design**: exit 1, with that live state pinned by
`marker: expired - the proof must run` at `test_s0_08_containment.py:558`.

**`spec.json`** — three legs, schema-valid. The brief asked for a `marker` leg, but
`proofs/schemas/spec.schema.json` restricts `leg` to `positive|negative`, so the marker leg is a
**second negative** — the shape `proofs/S0-11/spec.json` already uses. Both negative legs are executed
by the test suite exactly as the runner would run them: `did not print its pinned reason` at `test_s0_08_containment.py:691`.
A drifted reason string fails here, not on the PC.

**Measured on real gVisor in the sandbox** (`/tmp/runsc --rootless do`, `release-20260817.0`), not
assumed: `uname -r` = `4.19.0-gvisor`; dmesg line 1 = `[    0.000000] Starting gVisor...`;
`/dev/kvm` absent (rc 2); `mount -t proc` rc **0**; `unshare -n` rc **0**; the mounted procfs showed
**3** processes with PID 1 `sh` while the host showed **99**. P1, P6, P7, P8 were smoke-run under real
gVisor; all eight were run uncontained to build the negative bundle.

---

## The mutant table — 21 run, 21 KILLED, 0 survived

Each mutant is a copy of `proofs/S0-08/` + the test file under the scratch dir; the tree is restored by
deletion after each. Killer lines pasted verbatim from the run.

| # | mutant | killer test | killer line |
|---|---|---|---|
| 1 | P1-HOST-KERNEL-ACCEPTED | `test_crun_bundle_fails_on_p1_with_the_exact_spec_reason` | `assert 'failure_reas...PT_DYNAMIC @0' == 'failure_reas...4, not gVisor'` |
| 2 | RUNSC-VERSION-UNPINNED | `test_runsc_version_unpinned_is_caught` | `AssertionError: assert 0 == 1` |
| 3 | SHA-UNPINNED | `test_runsc_sha_unpinned_is_caught` | `AssertionError: assert 0 == 1` |
| 4 | CANARY-MISSING-IGNORED | `test_missing_canary_line_fails_by_name[P1]` | `assert 'containment: P1 canary line absent' in "failure_reason: containment: P1 observation 'uname_r' absent\n"` |
| 5 | P5-SENTINEL-READABLE-ACCEPTED | `test_each_property_mutation_is_caught[P5-…]` | `P5-SENTINEL-READABLE-ACCEPTED survived: PASS: S0-08 gvisor-containment - 6 properties asserted over pc-runsc` |
| 6 | P2-UID-ROOT-ACCEPTED | `test_each_property_mutation_is_caught[P2-…]` | `P2-UID-ROOT-ACCEPTED survived: PASS: S0-08 gvisor-containment - 6 properties asserted over pc-runsc` |
| 7 | FIFO-EVIDENCE-HANG | `test_fifo_at_an_evidence_path_is_refused_not_hung[canaries.jsonl]` | `subprocess.TimeoutExpired: … timed out after 60 seconds` |
| 8 | MARKER-MALFORMED-PASSES | `test_marker_gate_malformed_matches_the_spec_leg` | `assert 'marker: expi...roof must run' == 'marker: malformed: probe_run'` |
| 9 | MARKER-EXPIRED-PASSES | `test_marker_gate_expired_without_result_is_red` | `AssertionError: assert 0 == 1` |
| 10 | CRUN-BUNDLE-PASSES | `test_crun_bundle_fails_on_p1_with_the_exact_spec_reason` | `assert 'failure_reas...xpected 10000' == 'failure_reas...4, not gVisor'` |
| 11 | SPEC-REASON-DRIFT | `test_crun_bundle_fails_on_p1_with_the_exact_spec_reason` | `assert 'failure_reas...4, not gVisor' == 'failure_reas... wrong kernel'` |
| 12 | CANARY-VERDICT-IN-SCRIPT | `test_read_only_canaries_emit_one_parseable_line_when_run[P1]` | `AssertionError: P1 emitted 2 lines` |
| 13 | P3-TOOLS-BROKEN-ACCEPTED | `test_each_property_mutation_is_caught[P3-…]` | `P3-TOOL-BROKEN-ACCEPTED survived: PASS: S0-08 gvisor-containment - 6 properties asserted over pc-runsc` |
| 14 | P4-SECRETS-ACCEPTED | `test_each_property_mutation_is_caught[P4-…]` | `P4-DOCKER-SOCKET-ACCEPTED survived: PASS: S0-08 gvisor-containment - 6 properties asserted over pc-runsc` |
| 15 | P6-RAW-DEVICES-ACCEPTED | `test_each_property_mutation_is_caught[P6-…]` | `P6-RAW-DEVICE-ACCEPTED survived: PASS: S0-08 gvisor-containment - 6 properties asserted over pc-runsc` |
| 16 | RECORDED-CANARIES-OPTIONAL | `test_missing_canary_line_fails_by_name[P7]` | `AssertionError: assert 0 == 1` |
| 17 | DEFERRAL-SWALLOWS-A-REAL-RUN | `test_crun_bundle_fails_on_p1_with_the_exact_spec_reason` | `AssertionError: deferred: containment evidence not captured` |
| 18 | VERDICT-WORD-IN-CANARY | `test_read_only_canaries_emit_one_parseable_line_when_run[P2]` | `AssertionError: P2 emitted 2 lines` |
| 19 | RESULT-PRESENCE-GATE | `test_marker_gate_result_presence_alone_does_not_retire_the_marker` | `AssertionError: assert 0 == 1` |
| 20 | RESULT-PROOF-ID-IGNORED | `test_marker_gate_rejects_a_result_from_another_proof` | `AssertionError: assert 0 == 1` |
| 21 | CANARY-FIELD-RENAMED | `test_live_canary_output_binds_to_the_fields_the_checker_reads[P1-…]` | `AssertionError: P1.sh no longer emits a field the checker reads: failure_reason: containment: P1 observation 'uname_r' absent` |

Mutant 7 is the strongest: without the `S_ISREG` guard at `check_containment.py:66` the checker
**actually hangs** on a FIFO and the test's subprocess timeout is what fires. Mutants 18 and 12 were
killed by the one-line test first (pytest `-x`); I re-ran mutant 18 with `-k never_print_a_verdict` and
confirmed `test_canaries_never_print_a_verdict` fails independently — that guard is not dead.

---

## Gate results (pasted, not typed)

```
$ bash scripts/test_summary.sh tests/test_s0_08_containment.py     # run 1
74 passed in 3.22s
pytest-exit: 0
pytest-summary: 74 passed in 3.22s

$ bash scripts/test_summary.sh tests/test_s0_08_containment.py     # run 2
74 passed in 2.59s
pytest-exit: 0
pytest-summary: 74 passed in 2.59s

$ bash scripts/test_summary.sh tests/test_s0_08_containment.py     # run 3, on the shipped bytes
74 passed in 3.72s
pytest-exit: 0
pytest-summary: 74 passed in 3.72s
```

The FILE IDENTITY sha256s above were re-verified after this run: the gated bytes ARE the shipped bytes.

From a clean `git archive 2ff0c31` copy + only my files (identity of all six proven by sha256 before
running), my suite **plus every adjacent consumer of `spec.json` and the ledger**:

```
$ python -m pytest tests/test_s0_08_containment.py tests/test_spec_probe_schemas.py \
                   tests/test_validate_ledger.py tests/test_proof_runner.py -q
138 passed in 13.98s

$ python scripts/validate-ledger integrity --root .
blocked_host numerator=0 denominator=1
…
rc=0

$ python scripts/validate-ledger stage1-gate --root . | grep S0-08
missing: S0-08 (blocked_host; deferral expired — the proof must run)
```

The positive leg, run exactly as the proof-runner would:

```
$ python3 proofs/S0-08/check_containment.py proofs/S0-08/evidence/pc-runsc
deferred: containment evidence not captured
rc=2
```

`scripts/proof-runner:180-184` turns a leg's `exit_code == 2` into `Deferred` and **preserves the
artifact**, so this is the honest pre-run state, not a failure.

Lint: `pyflakes` on all three Python files — **0 findings**. `sh -n` on all eight canaries and
`bash -n` on the runner — **clean**. `ap_screen.py proofs/S0-08` — **0 hits over 2 files**.
`ap_screen.py --tests` — 7 hits, all AF-AP-34, all classified below.

**Process census.** Nothing of mine is left running: no `runsc`, `podman`, `sleep infinity` or canary
process. Zero leftover `s0-08-p6-proc` mounts in `/proc/self/mountinfo`; no leftover sentinels or temp
files. The rows the census *did* show are admissible foreign rows — lane B1's mutation loop over
`tests/test_s0_02_buzz_authz.py` and a VCK12 gate over the S0-01 tests — neither started by me
(AF-AP-59: assert the owned subset, account for the rest).

---

## 18-class preflight over MY OWN files (material-S0-02.md §7)

| class | instances | verdict | the run |
|---|---|---|---|
| 1 presence-gated | 6 | SAFE | every one is followed by a named refusal; the deferral boundary `if not evidence_dir.is_dir()` (`check_containment.py:264`) is pinned by mutant 17. **1 DEFECT found and FIXED** — the `result.json` presence gate, below |
| 2 reads outside walk / no S_ISREG | 5 checker/gate reads | SAFE | all behind `S_ISREG` checks (`check_containment.py:66`, `marker_gate.py:42`, `marker_gate.py:56`); mutant 7 proves the guard load-bearing |
| 2b canary `/proc` + `/sys` reads | 12 | DOCUMENTED-LIMIT | these are pseudo-files — `S_ISREG` would reject them by design. The rule binds evidence paths (the checker), not in-container `/proc` reads |
| 3 stale `[-1]` / `tail -n 1` | 1 (`run_containment.sh:267`) | SAFE | the canary emits exactly one line, pinned by `test_read_only_canaries_emit_one_parseable_line_when_run`; a stray trailing line makes the checker fail "not JSON" — closed, not open |
| 4 negative acceptance | 8 | SAFE | 7 are the pkill/host-network bans with their own negative control, `test_runner_code_filter_actually_removes_comments` (`test_s0_08_containment.py:751`); the 8th is a premise guard that fails **loudly** with instructions when the PC run lands |
| 5 substring / tail anchors | 20 | SAFE | every outcome is classified by an EXACT `returncode`; the substring only names the reason. One loose anchor (`assert "P1" in stdout`) was tightened to `startswith("failure_reason: containment: P1 host kernel ")` |
| 6 env-domain fail-opens | 1 (`S0_08_SENTINEL_PATH`) | SAFE | **RUN:** unset → canary rc 1, then `S0_08_SENTINEL_PATH not supplied` (`test_s0_08_containment.py:345`), and the checker refuses the bundle |
| 7 lossy decodes | 3 (`errors="replace"`) | SAFE | only in the runner's identity recorder; a corrupted digest makes the checker's exact equality FAIL — closed, not open |
| 8 broad catches | 4 | SAFE | each converts a parse failure into a NAMED `Failure`/`Fail` carrying the exception type; none swallow |
| 9 waits / polls | 1 — `for _ in $(seq 1 60)` (`run_containment.sh:154`) | DOCUMENTED-LIMIT | failure-aware: it re-checks container state each iteration and exits 4 loudly, and exits 4 after 60 s. **NOT executed here** — PC-only |
| 10 skips / xfails | 1 | **DEFECT — FIXED** | `pytest.importorskip("jsonschema")` on a HARD dependency (CI installs it at `.github/workflows/stage0-ci.yml:19`; `scripts/validate-ledger:10` imports it unconditionally). A missing jsonschema would have silently skipped the schema gate. Now a module-scope `import jsonschema`, matching `tests/test_proof_runner.py:14` |
| 11 world-scoped enumerations | 4 | SAFE | every `/proc` scan SELECTS by exact cmdline and asserts only that owned process's uid; `proc_count` and `ps_tree` are RECORDED, never asserted equal to a spawn set |
| 12 signal installs | 1 (`trap cleanup EXIT`) | SAFE | `CID` and `SENTINEL` are pre-initialised to `""` before the trap is installed, so the handler cannot trip `set -u` |
| 13 `/proc/<pid>/exe` races | 1 | SAFE | `readlink /proc/self/ns/net` — self, and RECORDED only (P7) |
| 14 mirrors | 1 | **DEFECT — FIXED** | the synthetic bundles mirrored the canaries' field NAMES, so a rename would pass every test while the real proof broke. Closed by `test_live_canary_output_binds_to_the_fields_the_checker_reads` (`test_s0_08_containment.py:611`), proven by mutant 21 |
| 15 two counters, different populations | 1 | SAFE | `secret_env_count` vs the reported names is a same-population cross-check and is asserted to AGREE (`test_p4_count_and_names_must_agree`) |
| 16 provably redundant guards | 0 | — | empty class |
| 17 hardlink-clobbering writes | 0 | — | empty class; all writes go to proof-owned paths the runner creates |
| 18 other families | 1 | **DEFECT — FIXED** | the piped-rc fail-open in `P3.sh` (below) |

**Empty classes (a result): 16 and 17.** Three DEFECTs found in my own work, all fixed in this round.

---

## DISCREPANCIES

**D1 — the brief's P2 names a service that does not drop privileges (design item 1).** The brief pinned
"the supervised `main-hermes` service runs as uid 10000 (`s6-setuidgid hermes`)". It does not.
`docker/s6-rc.d/main-hermes/run:27` is `exec sleep infinity` and its own comment says "For now this
service is a no-op: it sleeps forever, doing nothing" — it runs as **root**. The `Dockerfile:309`-311
comment the brief quotes ("Each supervised service then drops to the hermes user via `s6-setuidgid
hermes` in its run script") is true only of `dashboard`, and `dashboard` exits 0 unless
`HERMES_DASHBOARD` is truthy (`docker/s6-rc.d/dashboard/run:9`-20), so **by default no supervised
service runs as uid 10000**. Building P2 literally would have produced a canary that fails against a
correctly-built image. P2 asserts the drop that is real and observable — the **main program's**, at
`docker/main-wrapper.sh:31` — and RECORDS the `main-hermes`/`dashboard` facts so the gap is visible.
*The brief was right that a privilege drop exists; it named the wrong seam.*

**D2 — `import hermes` does not exist (design item 1, P3).** The pinned project installs `hermes_cli`,
`agent`, `tools`, `gateway`, `acp_adapter`, … (`pyproject.toml:587`) and no top-level `hermes` module.
P3 asserts `import hermes_cli`.

**D3 — gVisor does NOT deny `mount -t proc` or `unshare -n` (design item 1, P6).** The brief pinned
"`mount -t proc proc /mnt` denied … `unshare -n` denied or confined". **Measured** under
`release-20260817.0`: both return **rc 0**. Neither is an escape — the mount yields gVisor's own
procfs and the namespace is created inside the sandbox. A canary asserting denial would fail on a
correctly-contained container, and flipping the expectation to "allowed" would assert nothing. P6
therefore asserts the **containment signature**: no raw host devices, and the mounted procfs's PID 1 is
the container's own. Measured differential: 3 sandbox processes vs the host's 99.
**This is the single most important finding in the lane** — the brief's P6, implemented as written,
would have been a false red; implemented as "allowed", a hollow green.

**D4 — the brief's `marker` leg is not schema-valid (design item 6).** `spec.schema.json` restricts
`leg` to `positive|negative`. The marker leg is a second **negative** leg, the shape
`proofs/S0-11/spec.json` already uses.

**D5 — the full runsc sha256 was never in the runbook.** The brief said to read the full digest from
line 128; that line carries only the truncated `048b89aa` (`PC-BRIDGE.md:128`). I pinned
`048b89aada69dc3333422e139d6e9d02f8ab06bda52398060e0fbdacca00074c`, **measured** from the identical
release binary in the sandbox (`sha256sum /tmp/runsc`), whose first eight hex characters match the PC's
recorded prefix (`PC-BRIDGE.md:128` — `048b89aa`). **The coordinator should confirm
`sha256sum /usr/local/bin/runsc` on the PC equals it before the first run**; a mismatch is a finding
about the two venues, not a checker bug.

**D6 — the negative fixture's kernel is the sandbox's, not the PC's.** The brief's exemplar reason
named `6.17.11-200.fc42` (the PC host). `fixtures/evidence-crun` was captured by really running all
eight canaries uncontained **here**, so it records `6.18.44-fc-v24` and the spec pins
`containment: P1 host kernel 6.18.44-fc-v24, not gVisor`. Pinning the PC's string would have meant
typing a value I did not measure. The fixture is committed, so the leg is venue-stable; the PC's own
`--runtime crun` control will produce the same shape with its own kernel.
`fixtures/evidence-crun/PROVENANCE.md` states all of this inside the fixture.

**D7 — the owner answer says KVM; the probe says systrap.** `gVisor host = the PC (bare metal, KVM)` is recorded at `tasks/stage0-breakdown.md:88`.
But `/dev/kvm ABSENT` with the modules unloaded is what `spikes/pc-bridge/result.json:17` records,
and `systrap (runsc default` is the platform `PC-BRIDGE.md:148` records as actually used.
Not blocking — gVisor's systrap platform needs no KVM — but P6 asserts `/dev/kvm` **absent**, which is
consistent with the probe and would fail if someone loaded `kvm_amd` and exposed the device.

**D8 — `runsc --rootless do` shares the host filesystem.** Measured: a host file and `/home` are both
readable from inside a `do` sandbox. So `do` mode can validate P1/P6's kernel-level answers but is
structurally incapable of testing P4 mounts, the P5 sentinel, or the image's tools. Treating a `do`
result as containment evidence would be the AF-AP-4 class. This is why P2/P3/P4/P5 are `NOT run here`.

**D9 — an adjacent sibling that fixed itself mid-lane.** When I ran the class-10 sweep,
`tests/test_s0_04_compression.py` carried the same `importorskip` on jsonschema at line 560. I left it
alone (another lane's file) and cited it. By the time `report_lint.py` checked that citation the line
was **empty**: the owning lane had already fixed it, and more strictly than I did — it now calls
`pytest.fail` with `jsonschema absent: only the structural half of this check ran` (`tests/test_s0_04_compression.py:607`).
A repo-wide `grep -rn "importorskip" tests/*.py` on current bytes returns **nothing**.
Recorded because the stale citation is itself the finding: line references
into a live lane's file go stale within the session, which is exactly what `report_lint.py` is for.

---

## NOT_DONE — all the coordinator's, by name

1. **The PC containment run.** No bridge access from this lane, by brief. `evidence/pc-runsc/` does not
   exist; the positive leg reports `deferred:` exit 2. Run:
   `bash proofs/S0-08/tools/pc/run_containment.sh` then
   `python3 proofs/S0-08/check_containment.py proofs/S0-08/evidence/pc-runsc`.
2. **The image build.** `podman build -t localhost/hermes-s0-08:527da608` from
   `~/s0-01-pinned/hermes-agent`. The runner does it and refuses (exit 2) if that checkout is not at
   the pinned `527da608`.
3. **The NEGATIVE bundle on the PC.** `run_containment.sh --runtime crun` — the live counterpart of the
   committed fixture.
4. **The registry class transition** `blocked_host → execution_proof` (`map-runsc-s008`), the
   `result.json` mint, and removing `blocked.json`. `proofs/registry.yaml` is an attested input and was
   not touched (AF-AP-56).
5. **P2, P3, P4, P5 under real gVisor.** Only P1/P6/P7/P8 could be smoked here — see D8.
6. **`sha256sum /usr/local/bin/runsc` on the PC** — the D5 confirmation.
7. **The runner end-to-end.** `bash -n` clean and its identity generator was exercised in isolation with
   hostile input (quotes and backslashes in `ps_tree` → valid JSON), but **no podman/runsc container was
   ever started by this lane**. Its external calls: `podman build`, `podman image exists`,
   `podman run`, `podman inspect`, `podman exec`, `podman logs`, `podman image inspect`, `podman rm -f`,
   `git -C rev-parse`, `sha256sum`, `uname -r`, `od`, `date -u`, `mktemp -d`, `python3`, `sed`, `seq`,
   `sleep`, `rm`, `mkdir`.

---

## SELF-ATTACK — the three most likely ways this is wrong

**1. "P6 was weakened to make it pass."** The likeliest reading of D3 is that I moved a goalpost. Ruled
out three ways: the measurement is reproducible in one command
(`/tmp/runsc --rootless do sh -c 'mount -t proc proc /mnt2; echo rc=$?'` → `rc=0`); the replacement
assertion is **falsifiable and did fire** — run uncontained it reports `/dev/kmsg,/dev/loop0` and the
checker fails; and mutants 15 and 21 kill both the property and its field binding. The residual risk is
real and stated: P6 no longer asserts anything about `unshare -n`, and gVisor's exact denial wording is
not pinned, because this lane could not run P6 in the target venue (podman + runsc). I would rather
record a message I have not seen than mint one.

**2. "The synthetic passing bundle is a mirror, so the PASS proves nothing."** Half true, and it was a
real defect (class 14): the synthetic fixtures encode the canaries' own field names, so a rename would
have passed every test. Closed by `test_live_canary_output_binds_to_the_fields_the_checker_reads`, which
runs P1/P2/P4 **for real** and requires the checker to fail on the PROPERTY rather than on
`observation` `absent`; mutant 21 proves it kills a rename. What remains unproven is P3's and
P5's field binding under a real container — the tools and the sentinel do not exist here.

**3. "The checker passes a bundle that never ran under gVisor."** This is the hollow green that matters,
so it is attacked from both sides. `fixtures/evidence-crun` carries a **valid** pinned runsc identity
next to uncontained observations and must still fail on P1
(`test_crun_bundle_identity_is_valid_so_p1_is_what_catches_it`) — the checker reads observations, not
metadata. Conversely mutants 2 and 3 prove the identity pins are load-bearing. And a canary that never
took its observation cannot pass — `cid in ASSERTED and rec["rc"] != 0` raises at `check_containment.py:120`.
The honest residual: **nothing here proves the PC run will pass.** If P1's
`dmesg` assertion or P4's zero-secret expectation is wrong under podman+runsc, the first PC run goes
RED — and that is a finding to adjudicate, not a bug to paper over. I deliberately did not loosen either
assertion to protect a run I have not seen.

**Kill-switch question.** If the coordinator deletes `proofs/S0-08/evidence/` after a successful PC run,
the proof reverts to `deferred:` exit 2 and the marker gate goes RED again — the deferral cannot be
retired by anything except a real `result.json` whose `proof_id` matches its directory
(`def _result_is_real` at `marker_gate.py:50`, mutants 19 and 20).
