# VERIFY-G1 — adversarial grade of lane G1 (S0-08 gVisor containment: the spec, eight canaries, the checker, the marker gate, the PC runner)

You are an adversarial-verifier (Opus 5 in the sandbox, or the PC Hermes `adversarial-verifier` role). Repo /home/user/agent-factory,
branch claude/soundbox-kit-migration-iz1jwf. **PIN: `517c65e`** (the checkpoint carrying the lane's 18 files + its report + the
coordinator's P4 fix). Grade the bytes of `git archive <PIN>` from a copy under the session scratchpad
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ (`vg1/`). Read-only git on the shared tree; every mutant on
scratch copies; every pytest run with an explicit `--basetemp` under your scratch dir; kill only what you start, PID-targeted; never
background a run and stop; no outward actions. Real gVisor is available in the sandbox as `/tmp/runsc --rootless do <cmd>`
(release-20260817.0; if `/tmp/runsc` is gone after the container restart, re-install it exactly as `spikes/runsc/` documents — same
digest — and say so).

**The ONE bridge action you MAY take (owner ruling 2026-09-07):** a pytest-only PC gate through `scripts/pc_suite.sh launch -n 8 --
tests/test_s0_08_containment.py` then `wait <RUN_ID>`, from a CLEAN detached worktree of the PIN. Nothing else on the bridge — NEVER
run `run_containment.sh`, `podman`, or `runsc` on the PC: the containment run is the coordinator's.

**The finding that frames this round:** the coordinator's PC gate (8 workers, the owner's non-root user) turned `P4.sh` RED where
the lane's root sandbox runs were green — the canary read `/proc/1/environ`, root-owned 0400, unreadable to any other uid — and the
real containment run execs the canaries as uid 10000, so P4 would have been a FALSE RED on the proof itself. The coordinator repointed
P4 at `/proc/self/environ` (commit message in the checkpoint). Your first job is the CLASS: **run every canary as a non-root user in
the sandbox (`su -s /bin/sh nobody -c 'sh <canary>'`) AND under `runsc --rootless do` as root, and enumerate every observation that
assumes root**: `dmesg` under `kernel.dmesg_restrict` (P1), `/proc/1/*` reads (P2), `mount -t proc` without CAP_SYS_ADMIN (P6 — inside
the pinned container the main program is uid 10000 with no caps: does P6's mount then fail, and is that failure recorded as an
OBSERVATION the checker treats as the containment signature, or as `did not complete its observation` = a false red?), device
enumeration (P6), cgroup reads (P8), the sentinel read (P5). A canary whose observation cannot complete as the runtime user is a
blocker; a canary that completes but observes something root-specific is a finding.

**Inputs (read in this order):** the lane brief `tasks/briefs/s0-08-g1-containment-spec-canaries-checker-runner.md` · the lane's report
`tasks/briefs/s0-08-support/G1-report.md` (DONE, 21 mutants, D1-D9, NOT_DONE 1-7, the self-attack) · `proofs/S0-08/CONTAINMENT-SPEC.md`
(P1-P8, the reasons table) · the material pack `tasks/briefs/stage0-parallel-support/material-S0-08.md` (the seed block, the runsc spike,
the PC facts: runsc release-20260817.0 at `/usr/local/bin/runsc`, `--security-opt label=disable`, `--runtime-flag ignore-cgroups`,
systrap, no /dev/kvm) · the pinned hermes-agent checkout `/home/user/nerdherderdani/hermes-agent` (commit 527da608: `Dockerfile`,
`docker/s6-rc.d/main-hermes/run`, `docker/main-wrapper.sh`, `docker/entrypoint-dispatch.sh`, `pyproject.toml`) — the lane's D1/D2/D3
claims are read against THIS source · `PC-BRIDGE.md` §gVisor · `docs/INCIDENT-LOG.md` (AF-AP-4, AF-AP-11, AF-AP-40, AF-AP-42, AF-AP-45,
AF-AP-59).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-08-support/G1-report.md --rev <PIN> --map C=proofs/S0-08/check_containment.py --map
M=proofs/S0-08/marker_gate.py --map T=tests/test_s0_08_containment.py --map R=proofs/S0-08/tools/pc/run_containment.sh` — MISS 0 or a
finding; `ap_screen.py proofs/S0-08 proofs/S0-08/tools/pc` (0 hits claimed) and `--tests` (7 AF-AP-34 hits claimed as comments —
confirm each is prose, not a call).

## Items
1. **The non-root class** (above) — the table: canary × (root sandbox | nobody sandbox | runsc rootless root) × (completed? rc, the
   observed fields) and the verdict per canary.
2. **The three deviations D1/D2/D3 against the pinned source.** D1: is `main-hermes` really `exec sleep infinity` as root and is the
   drop at `main-wrapper.sh:31` the only one — cite lines; what does the canary observe when the main program has not started yet
   (a race at container start)? D2: `import hermes_cli` — cite `pyproject.toml`; would `hermes --version` be a stronger P3? D3: reproduce
   `mount -t proc` rc 0 and `unshare -n` rc 0 under `runsc --rootless do`; then as a NON-ROOT uid inside runsc (`runsc … do` supports
   `--uid`? find out) — the containment signature P6 asserts must hold for the runtime user, not for root.
3. **The checker (`check_containment.py`).** Every REASON in the spec's table reachable by one mutant (the lane's table: P1-P6 property
   mutants, CANARY-MISSING, RECORDED-OPTIONAL, FIFO-EVIDENCE-HANG, SPEC-REASON-DRIFT, RESULT-PRESENCE-GATE, RESULT-PROOF-ID,
   CANARY-FIELD-RENAMED) — re-run them; then yours: a canary line with `rc` non-zero but plausible observations (does the checker
   trust observations from a canary that reported rc 1?), a duplicated canary line (two P1 rows — first wins? last? named?), an
   observation value of the wrong type (`"secret_env_count": "0 "`), a runtime-identity whose runsc sha matches but the version string
   differs, the negative bundle with a FORGED gVisor kernel string but host devices present (does P1 pass and P6 catch it — two
   independent instruments, tactic 8).
4. **The marker gate (`marker_gate.py`).** Six verdicts, each by one input; the live tree = `marker: expired - the proof must run` (rc 1)
   — and the transition rule: the coordinator's later `blocked.json` removal + `result.json` mint must flip it green ONLY when the
   result's `proof_id` matches and the file is a real regular file (AF-AP-10/40) — write the forged-result mutants.
5. **`spec.json`.** Three legs schema-valid; the positive leg `deferred: … exit 2` today; both negative legs run exactly as the runner
   runs them (`scripts/proof-runner` semantics for exit 2 = Deferred, artifact preserved — cite the runner lines); the marker leg as a
   second negative (D4) — is that honest to the seed's `blocked_marker` block, or does it hide the marker's own state from the ledger?
6. **The PC runner (`tools/pc/run_containment.sh`) — READ, never run.** `bash -n`; every external call enumerated (the lane's list);
   the podman invocation carries the PC-known flags (`--runtime runsc`, `--security-opt label=disable`, `--runtime-flag
   ignore-cgroups`) or the runner detects and reports their absence; the image build pinned to 527da608 (the runner refuses otherwise —
   find the check); the canaries exec'd as uid 10000 (`podman exec --user`?) — if the runner execs them as root, P2/P4/P5 observe the
   wrong subject (a blocker); the identity generator's JSON is valid under hostile `ps_tree` text (the lane's claim — reproduce); the
   runner never touches the owner's services (no `systemctl`, no `podman rm` of non-`hermes-s0-08` names — grep); the crun negative
   leg's expected reason equals the committed fixture's.
7. **The negative fixture (`fixtures/evidence-crun/`)** — provenance honest (D6: the sandbox's kernel string), the PROVENANCE.md names
   which fields are measured vs typed; the malformed-marker fixture's failing field is the one the gate names.
8. **D5 / D7 / D8** — the runsc sha256 (the lane pinned a digest measured from "the identical release binary" — from WHERE? cite; the
   coordinator confirms on the PC), KVM vs systrap (does any canary or checker line assume KVM?), `runsc --rootless do` sharing the
   host filesystem (the lane says P3/P4/P5 could not be smoke-run under it — agree?).
9. **The 18-class preflight** the lane ran (3 DEFECTs found in its own files: the piped-rc in P3, importorskip, the field-name mirror) —
   re-run the class scan over the 18 files yourself; a class the lane missed = a finding.
10. **The PC gate (the carve-out)**; paste beside the checkpoint's lines; agree.
11. **Mutants ≥ 30** (the lane's 21 + yours); every survivor classed; killers from the run.
12. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census (no leftover runsc,
    mounts, sentinels).
13. **The design.** Is "canaries observe, the checker judges" carried through (no canary prints a verdict — the lane's mutant 12/18)?
    Is the six-property assertion set the right closure of the seed's four assertions + KC-? Keep it to what you measured.

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-G1.md` — draft after EACH item — then return it whole. Findings: ALL, no severity
filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact red test, SOLID/UNSURE;
reproduced vs reviewed vs skipped; shared-tree hygiene; verdict MERGE-READY or NOT-READY with the blocking set, the cheapest path, and
the exact list of what the coordinator must do on the PC for the containment run.
