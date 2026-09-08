# VERIFY-G2 — adversarial grade of lane G2 (S0-08 gVisor containment round 2: the runtime user observes, P6 under the real capability set, an unambiguous main program from one source, the evidence bound to image + argv, the crun fixture re-captured, the eight survivor killers)

You are an adversarial-verifier (Opus 5 in the sandbox, or the PC Hermes `adversarial-verifier` role). Repo /home/user/agent-factory,
branch claude/soundbox-kit-migration-iz1jwf. **PIN: `887f021`** (the commit carrying the lane's 12 rewritten files + its report). Grade
the bytes of `git archive 887f021` from a copy under the session scratchpad /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/
(`vg2/`; delete it when done). Read-only git on the shared tree (other lanes' uncommitted edits — none in your scope); every mutant on
scratch copies; every pytest run with an explicit `--basetemp`; kill only what you start, PID-targeted; never background a run and
stop; no outward actions; NO podman, NO container start anywhere; gVisor cells only through `/tmp/runsc --rootless do` on scratch dirs
(`setpriv --reuid=65534 --regid=65534 --clear-groups` for the non-root cell — VERIFY-G1's method); never read, print or commit a
credential. Interpreter `/root/venv-agent-factory/bin/python`. Authorization: the owner's own containment boundary under test.

**The ONE bridge action you MAY take:** the pytest-only PC gate `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_08_containment.py`
from a clean detached worktree of the PIN, then `wait <RUN_ID>`. Nothing else on the bridge — NEVER `run_containment.sh`, podman or
runsc on the PC.

**Inputs (read in this order):** VERIFY-G1's report `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/wf-results-r5/VERIFY-G1.md`
(the round's contract) · the lane brief `tasks/briefs/s0-08-g2-containment-the-runtime-user-observes.md` · the lane's report
`tasks/briefs/s0-08-support/G2-report.md` (the red-before/green-after table, the 29 mutants, DISCREPANCIES D1-D8 — D1 rejects the
brief's pinned literal `init` for `s6-svscan` from a sha-verified s6-overlay tarball + `Dockerfile:68`) · `proofs/S0-08/CONTAINMENT-SPEC.md`
(§1 the derivations, §P6 the capability-set table, §6 the PC notes) · the pinned hermes-agent checkout `/home/user/nerdherderdani/hermes-agent`
(527da608, READ-ONLY): `Dockerfile` (`:68`, `:95`, `:150`, `:298`, the `S6_OVERLAY_*` pins), `docker/entrypoint-dispatch.sh`,
`docker/main-wrapper.sh`, `docker/s6-rc.d/**`, `docker/hermes-exec-shim.sh:54` · `docs/INCIDENT-LOG.md` (AF-AP-4, AF-AP-26, AF-AP-34,
AF-AP-40, AF-AP-42, AF-AP-56, AF-AP-59) · `scripts/proof-runner` (the Deferred path, the leg order).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-08-support/G2-report.md --rev 887f021 --map C=proofs/S0-08/check_containment.py
--map T=tests/test_s0_08_containment.py --map R=proofs/S0-08/tools/pc/run_containment.sh` — MISS 0 or a finding; `ap_screen.py
proofs/S0-08 proofs/S0-08/tools/pc` (0) and `--tests` (AF-AP-34 ×8, all bans/comments — classify by run); `bash -n`/`sh -n`; the
FILE IDENTITY table against the PIN (every row — the lane re-stamped it; VERIFY-G1's F16 was a stale table).

## Items
1. **D1 — `s6-svscan`, the one assertion the lane could not reproduce.** Reproduce the chain the lane cites: the s6-overlay noarch
   tarball's sha256 in the Dockerfile (`S6_OVERLAY_NOARCH_SHA256`), its `/init` exec'ing `stage0` → `bin/init` (s6-linux-init stage
   1) — fetch the same tarball ONLY if the sandbox can reach it (a read of a public release artefact; if it cannot, grade from the
   Dockerfile's own words and say so); then the hop the lane marks INFERRED: does s6-linux-init's stage 1 exec `s6-svscan` as PID 1
   with comm `s6-svscan`? (`/proc/1/comm` is 15 chars — `s6-svscan` fits; would `s6-linux-init` truncate to `s6-linux-init`?) State
   whether the literal is SOLID or UNSURE and what the first PC run must read before trusting a red. Then attack: a bundle whose
   `own_pid1_comm` is `s6-svscan` but whose `pid1_uid` is not 0; `own_pid1_comm` = `s6-svscan ` (trailing space); P2's
   `pid1_comm` = `s6-svscan` while P6's is `systemd` (the agreement check at `check_containment.py:364`).
2. **`CONTAINER_MAX_PIDS = 32` — a derived bound or a typed number?** Re-derive from `docker/s6-rc.d/user/contents.d/` (two services)
   and the s6 supervision tree; the lane's ≈12 at steady state; the Dockerfile's `:95` per-profile gateways — could the real image
   exceed 32 with a configured profile, and does the runner guarantee none is configured (the CMD is `sleep 2147483647`; is a
   profile mounted or generated at start)? Attack: `own_pid_count` `"32"` (the bound — inclusive?), `"0"`, `"-1"`, `"32 "`, `"1e1"`.
3. **The run_argv screen.** Required adjacent pairs + banned tokens + every `--network` value `none`. Attack: `--network=none`
   (the `=` form — required pair absent?), `--network none --network host`, `--privileged=true`, `--cap-add=SYS_ADMIN`, `-v` as
   `--volume`, `--mount type=bind,…`, `--pid host` vs `--pid=host`, `--security-opt=label=disable`, a `run_argv` that is a string
   instead of a list (`:218`), an argv carrying the required pairs twice. Say which forms the runner itself can emit
   (`run_containment.sh` builds the argv — cite the lines) and which only a forged bundle can; a forged form that passes is a finding.
4. **The exec identity.** `canary_exec_user` recorded from `CANARY_EXEC_UID` — the runner's own constant (a typed echo, like
   VERIFY-M1 F-4) or a readback (`id -u` inside the exec)? If typed: a bundle records `10000` while the exec ran as root — can the
   checker tell? Attack: `"10000 "`, `10000` (int), `"1e4"`, absent key. Then P4/P5 under `--user 10000`: re-derive from
   `docker/hermes-exec-shim.sh:54` that P3 still works, and from `main-wrapper.sh` that the env P4 observes under a non-root exec is
   the env the MAIN program inherits (or state the residual: `with-contenv` + `HOME=/opt/data` exports before the drop).
5. **P2's every-holder collection.** The live two-process test (`tests/test_s0_08_containment.py:926`): does it prove the checker's
   ambiguity reason (2 processes) AND the single-holder positive control (1 process, uid 65534 → the checker requires 10000 — how
   does the test pass the uid check in the sandbox?)? Attack: `main_pids` `"1,2"` with `main_uids` `"10000"` (`:267` disagreement),
   `main_pids` `""` (no holder — which reason?), `main_pids` `"1"` `main_uids` `"10000,10000"`, a cmdline holder whose uid is
   unreadable (the `_csv` empty-entry drop the lane mentions — reproduce `1 pid(s), 0 uid(s)`).
6. **The `exec_rc` fix (`run_containment.sh:315`).** Read the capture block: is the exec's status read BEFORE any pipeline, and does
   a canary that prints its line and then exits non-zero produce a named failure in the bundle (or does the runner abort the whole
   run — `set -e`?). Which is the intended behaviour, and does the checker's `rc` field agree with the exec's status?
7. **The crun fixture re-capture (F5) and its host-dependent guard.** `test_crun_fixture_is_producible_by_the_shipped_canaries`
   compares venue-independent values unconditionally and host-dependent ones only on the capture host (detected from `uname_r`).
   Is the guard a skip in disguise (AF-AP-40 shape: `if same_host: assert …` with no else)? What does the test assert on the PC?
   Run it here (the capture host) and with a forged `uname_r` in a scratch copy: does the host-dependent half silently pass? The
   fixture's `runtime-identity.json` is typed (valid pinned runsc identity by design, VERIFY-G1 item 7) — still labelled so?
8. **F14 — the proof-runner test.** Reproduce the three-run demonstration (`tests/test_s0_08_containment.py:1485`); confirm
   `negative-control-unmet: S0-08` is the runner's real reason string and that the leg reorder changes nothing else the runner
   records (`runs` order in a minted result — does `validate-ledger` care about leg order?).
9. **The eight survivor killers (35, 37, 38, 39, 40, 41, 42, 45) + G1's 21** — re-run every mutant on scratch copies; paste; add
   yours: the sentinel generator with `SENTINEL_READABLE` unset (not `false`); `P1.sh` with `dmesg` present but printing nothing;
   the pinned-source preflight against a repo at the right commit but with a DIRTY tree; the readiness gate matching the new cmdline
   inside another container on the same host (`podman exec` is container-scoped — is the readiness scan?).
10. **The 18-class re-scan** — the lane closed classes 1, 3, 11, 18; verify each closure by RUN (the `if mount_rc == "0"` else-arm
    raises; the readiness gate's `[-1]`; every `if <field> == <literal>:` in the checker has a raising other arm — enumerate them
    mechanically and list any without). The registry row the lane flagged for the coordinator ("assertion skipped when its
    precondition fails") — confirm no instance remains in the checker.
11. **The PC gate (the carve-out)**; paste beside the checkpoint's line; agree.
12. **Mutants ≥ 40** (29 + yours from items 1-9).
13. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census (the `/proc` scan
    self-match the lane names — exclude your own shell by pid, never by pattern).
14. **The design.** Is `s6-svscan` + `own_pid_count ≤ 32` + P2/P6 agreement an adequate capability-independent containment
    signature for P6, given that a gVisor sandbox with the image's real init would also show the same three (what distinguishes
    "contained" from "the image's init running on the host as root"? — the kernel string P1 and the device census P6 are the other
    instruments; state the whole set that together implies containment and which single mutation defeats it). Is the run_argv
    screen the right place for the network claim P7 makes, or should P7 read the netns (`readlink /proc/self/ns/net` vs the host's)?
15. **The amendment after the coordinator's PC gate (§PC GATE FINDING in the report).** The report was amended after its first round:
    the venue-derived two-arm tests (`dmesg_works()` `tests/test_s0_08_containment.py:52`, `venue()` `:63`), the live-binding test's
    `observed_live = dict(live, rc=0)` (`:714` — is forcing the canary's own status to 0 on a live line a MIRROR? what does the
    class-14 guard still prove on a venue where P1 cannot read dmesg?), the fixture test's derived `0 if readable else 1` (`:1497`),
    the bare-word rename guard narrowed to `"observation '"` (`:689` — attack: a renamed field whose absence message differs; a
    canary that prints the marker itself). Re-run mutant 46 (P1-PIPED-RC-FAIL-OPEN) on THIS root venue — it must die through the
    `dmesg` stand-in test alone. Reproduce the whole file as uid 65534 (`setpriv`, a world-executable interpreter such as
    `/usr/local/bin/python3`, a basetemp outside `/tmp/claude-0`): the lane reports `122 passed` both as root and as 65534 — paste
    both; a count that differs is a finding. The coordinator's PC gate on the amended bytes: `197 passed in 6.41s`
    (20260908T050153Z-2c497ee, uid 1000).

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-G2.md` — draft after EACH item — then return it whole. Findings: ALL, no
severity filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact red test,
SOLID/UNSURE; reproduced vs reviewed vs skipped; shared-tree hygiene; verdict MERGE-READY or NOT-READY with the blocking set, the
cheapest path, and the exact PC steps for the coordinator's containment run (VERIFY-G1's eight + the lane's three additions).
