# Lane G3 — S0-08 gVisor containment round 3: the runner's argv grammar closed, the observer uid read back, the image built from the pin's archive and measured, the count floor, the exact uid type, the fixture split

**PIN: `488b238`** (the current branch head; the S0-08 files are 887f021's round-2 bytes, unchanged since). Role: code-implementer (the
PC Hermes build lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo agent-factory, branch
claude/soundbox-kit-migration-iz1jwf. Boundary (yours, disjoint from every other lane): `proofs/S0-08/check_containment.py`,
`proofs/S0-08/tools/pc/run_containment.sh`, `proofs/S0-08/canaries/*.sh`, `proofs/S0-08/CONTAINMENT-SPEC.md`, `proofs/S0-08/spec.json`,
`proofs/S0-08/fixtures/**`, `tests/test_s0_08_containment.py`, your report `tasks/briefs/s0-08-support/G3-report.md`. NOT yours:
the pinned upstream checkout under `/home/rocco/s0-01-pinned/hermes-agent` (read-only), `upstream.lock.yaml`, the registry, the
ledger. NEVER start, build or exec a container, never run `run_containment.sh` for real (the venue rule — the live runsc leg is the
coordinator's after this round's verify); every hostile-path or FIFO rig standalone under `timeout` with a PID-scoped watchdog; kill
only what you start, by pid; never background a run and stop; no outward actions.

**Inputs (read in this order):** VERIFY-G2's report `tasks/briefs/s0-08-support/VERIFY-G2-report.md` (the round's contract: Findings
1-11 with minimal fixes, the 42-mutant table with its seven survivors, the "exact coordinator path after repair") · the G2 report and
brief (`tasks/briefs/s0-08-support/G2-report.md`, `tasks/briefs/s0-08-g2-*.md`) · VERIFY-G1's report (what round 2 closed — must not
regress) · `docs/INCIDENT-LOG.md` (AF-AP-34, AF-AP-40, AF-AP-59, AF-AP-63, AF-AP-65).

## Design (pinned — build it, do not redesign it; line numbers are 887f021's = the PIN's)
1. **F3 — the argv boundary is a CLOSED GRAMMAR, not a blocklist.** `BANNED_RUN_ARGV_TOKENS` (`check_containment.py:54-67`) and the
   screen at `:216-227` are replaced by an exact-shape check: `run_argv` must equal the runner's own emitted shape
   (`run_containment.sh:165-178`) — the exact prefix, every flag as the exact two-token pair the runner emits, each with multiplicity
   ONE, in the runner's order, then the exact image reference and command suffix; anything else is a named failure quoting the first
   offending token. The grammar lives ONCE (a function both the runner-source test and the checker consume, or the checker derives it
   from the runner source by parse — state which and why). VERIFY-G2's red table becomes committed tests: `--privileged=true`,
   `--cap-add=SYS_ADMIN`, `--volume=/host:/host`, `--mount=type=bind,src=/,dst=/host`, two-token `--pid host`, appended
   `--network=none`, a duplicated required pair, a reordered pair — every one rc 1 with the named token; the runner's exact argv passes.
2. **F4 — the observer uid is READ BACK.** Every canary exec wrapper (`run_containment.sh:235-250,269-292,310-320`) records
   `observed_exec_uid` from `id -u` executed INSIDE the same `podman exec` as the canary (the canary line carries it, or a paired
   line the checker joins by canary id); the checker requires `observed_exec_uid == "10000"` per record AND equal to the typed
   `canary_exec_user`; a typed 10000 with an observed 0 is a named failure. The runner's constant stays as the REQUEST, the readback is
   the OBSERVATION — the spec (`CONTAINMENT-SPEC.md`) says so. VERIFY-G2's mutant 50 (exec as root, the constant kept) is the killer.
3. **F10/F11 — the image is built from the pin's ARCHIVE and MEASURED.** The preflight (`run_containment.sh:98-125`) no longer trusts
   a checkout: the build context is `git -C <pinned checkout> archive <pinned commit>` extracted to a runner-owned temp dir (a dirty
   worktree cannot leak into it), built with `--build-arg HERMES_GIT_SHA=<pinned commit>` (the upstream Dockerfile's provenance
   argument — read it at `/home/rocco/s0-01-pinned/hermes-agent/docker/Dockerfile` and cite the line); the runner records the
   immutable image ID and digest from `podman image inspect` and the baked provenance read from INSIDE the running container (the
   Dockerfile's provenance file/env — cite it), all three into `runtime-identity.json`; `check_identity` (`:205-212`) binds the typed
   source commit to the baked provenance AND the recorded image ID/digest (a foreign name or digest with the right commit → rc 1 by
   name); the `--image TAG` path performs the SAME readback and refuses an image whose baked provenance is absent or differs. Static
   tests over the runner source prove the archive build context and the build arg (the container itself never runs in this lane).
4. **F1 — the P6 ceiling's domain is EXPLICIT.** The runner mounts a fresh EMPTY runner-owned `/opt/data` volume per run (created
   and removed by the runner, by name it generated) so the persistent-profile domain (`container_boot.py` walking
   `/profiles/`) is empty by construction; `CONTAINER_MAX_PIDS` (`check_containment.py:78-86`) is re-derived for THAT
   configuration and the derivation comment names the domain and its exclusions.
5. **F2/F5 — the domain floors.** `own_pid_count` (`:369-378`) must be an integer in `1..CONTAINER_MAX_PIDS` (zero and negatives
   refused by name — PID 1 and the canary exist); `canary_exec_user` (`:228-234`) must be a JSON string exactly (an int 10000 refused
   by name, the absent-field reason kept).
6. **F6/F8/F7 — the claims narrowed, the fixture split, the control declared.** P4 (`canaries/P4.sh:22-31`) and its spec prose claim
   "the exec environment exposed to the runtime uid", never the main program's env; the crun fixture test (`test:1513-1528`) splits
   into a stable fixture-shape test that asserts the same properties on every venue and a capture-host recapture test that asserts the
   four host-bound values only where they can be true, each arm stated; F7's live single-holder positive control is DECLARED NOT-run
   here (the coordinator's live-container venue) with the exact cell it must show.
7. **F9 — P7 stays recorded, documented** (no change; the spec states the gap and the future paired-netns design).
8. **Mutants:** VERIFY-G2's seven survivors (31, 32, 33, 38, 45, 50, 51) as the round's named killers, G1's 21 and VERIFY-G2's 21
   re-run — every one killed with its killer line pasted; ≥45 total; by-construction survivors named as such. Every negative control
   fails for the EXACT expected reason (AF-AP-63); no `if <field> == <literal>:` without a raising other arm (AF-AP-65); no name kill
   (AF-AP-34/59).
9. **18-class self-sweep as an ENUMERATION** (counts + method; class 11 world-enumeration: the closed argv grammar IS the enumeration;
   class 2: every identity field measured or typed — a table saying which).
10. **Report discipline:** FILE IDENTITY of the FINAL bytes; every `file:line` from `grep -n` on the FINAL bytes and
    `python3 scripts/report_lint.py <report> --map C=proofs/S0-08/check_containment.py --map R=proofs/S0-08/tools/pc/run_containment.sh
    --map T=tests/test_s0_08_containment.py --map S=proofs/S0-08/CONTAINMENT-SPEC.md` pasted with MISS 0; the direct venue suite
    pasted (`/home/rocco/venv-agent-factory/bin` first on PATH, the PC venue exports VERIFY-G2 used, an absolute `--basetemp`) for the
    S0-08 file AND the five-file set VERIFY-G2 ran (`197 passed` is the floor); the two `lane_gate.sh` RESULT lines
    (`scripts/lane_gate.sh -r 488b238 -f "<your files>" -t "tests/test_s0_08_containment.py" -n 2`); `ap_screen.py` prod + `--tests`
    classified by run; NOT-done first-class (the live runsc leg, the host-root venue, F7's live cell).

## Report
Write it to `tasks/briefs/s0-08-support/G3-report.md` inside your tree, draft after EACH item, and return it whole as your final
message: the DONE table (item → file:line → the red test → its killer line), the mutant table, the discrepancies, the self-attack, the
evidence tiers, NOT-done first.
