# VERIFY-G3 — adversarial grade of lane G3 (S0-08 gVisor containment round 3: the argv grammar closed, the observer uid read back, the image built from the pin's archive and measured, the P6 domain made explicit, the floors, the fixture split)

**AMENDMENT 2026-09-14 — the `report_lint` bar in this brief's discipline item is BOUNDED (after lane N5k looped 47 minutes on exactly that line; AF-AP-76):** run the lint LAST with the maps named there, apply the `fix:` hint the lint prints on each MISS row for at most THREE rounds, then paste the final summary line into DISCREPANCIES and finish. `MISS 0` is the target, never a stop condition — a MISS that survives three rounds is reported, not chased. A line that existed only at the PIN is written `alias@<PIN>:NN` (checked at that revision) or in words. The harvest grades the floor (`--min-refs`) plus the paste. Nothing else in this brief changes.

You are an adversarial-verifier (the PC Hermes verify lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo agent-factory,
branch claude/soundbox-kit-migration-iz1jwf. **PIN: `7f60d83`** — the S0-08 round-3 LANDING: the coordinator's harvest of lane G3's PC
tree (PIN 488b238), a straight copy plus ONE coordinator touch (an f-string without placeholders at `T:1248` — the sandbox pyflakes).
FILE IDENTITY at the PIN (lines, sha256[:8]): `proofs/S0-08/check_containment.py` (565, `52668a02`) ·
`proofs/S0-08/tools/pc/run_containment.sh` (415, `9800a372`) · `proofs/S0-08/canaries/P1.sh` (28, `744df86c`) · `P2.sh` (63, `855fa645`) ·
`P3.sh` (50, `a6c32030`) · `P4.sh` (57, `358923dc`) · `P5.sh` (46, `2ecf616c`) · `P6.sh` (61, `26cb113c`) · `P7.sh` (29, `8f082f6d`) ·
`P8.sh` (31, `74d923fe`) · `proofs/S0-08/CONTAINMENT-SPEC.md` (471, `a47e04c8`) · `proofs/S0-08/fixtures/evidence-crun/PROVENANCE.md`
(99, `75ac24ad`) · `canaries.jsonl` (8, `a83fba44`) · `runtime-identity.json` (60, `044a799b`) · `tests/test_s0_08_containment.py`
(1740, `503f4e12`); the lane's report `tasks/briefs/s0-08-support/G3-report.md`; its transcript `transcripts/pc/pc-g3.md--488b238.md`.
Grade the bytes of `git archive 7f60d83` from a scratch copy under your lane's scratch dir; every mutant on scratch copies; every pytest
run with an explicit SHORT absolute `--basetemp`, `/home/rocco/venv-agent-factory/bin` FIRST on PATH and the venue exports
(`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`); kill only
what you start, by pid; never background a run and stop; no outward actions. **NO podman — no container start, build or exec, ever,
and NEVER `run_containment.sh` for real** (lane G3 itself started an accidental 30 s `podman build` by "testing the preflight" —
its report §3; you grade the runner STATICALLY, and the live runsc leg is the coordinator's after this grade). gVisor cells, if you need
one, only through `/usr/local/bin/runsc --rootless do` on a scratch dir, PID-scoped under `timeout`. The pinned hermes-agent checkout
`/home/rocco/s0-01-pinned/hermes-agent` (527da608) is READ-ONLY. Never read, print or commit a credential. Authorization: the owner's own
containment boundary under test on the owner's system. Do NOT spawn subagents.

**Inputs (read in this order):** VERIFY-G2's report `tasks/briefs/s0-08-support/VERIFY-G2-report.md` (the round's contract: blockers
3, 4, 10, 11; findings 1, 2, 5-9; the seven mutant survivors 31, 32, 33, 38, 45, 50, 51; the six-step coordinator path) · the lane
brief `tasks/briefs/s0-08-g3-containment-the-argv-grammar-closed-the-observer-read-back-the-image-measured.md` (10 pinned items) ·
the lane's report (its evidence tiers, §3 the incident, §4 NOT-done, §8 adjacent defects; refs written as `(:133-150)` inside a table —
`report_lint` reads `3 refs — OK 0, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 2 (at 7f60d83)`) · the pack
`tasks/briefs/s0-08-support/VERIFY-G3-pack.md` · `proofs/S0-08/CONTAINMENT-SPEC.md` · the pinned Dockerfile — **the coordinator verified
at brief time (AP-43) what the lane left "Assumed": the upstream `Dockerfile` (the ROOT one; `docker/Dockerfile` does not exist — the G3
brief's pointer was wrong) declares `ARG HERMES_GIT_SHA=` at `:336`, writes `/opt/hermes/.hermes_build_sha` at `:338-339` and
`/etc/hermes/image-provenance.json` (`schema`, `deployment_kind`, `manager`, `image`, `version`, `revision`) at `:341-342`** — so the
runner's two readbacks (`R:272-273`) CAN succeed on a build that passes the arg · `docs/INCIDENT-LOG.md` (AF-AP-34, AF-AP-40, AF-AP-56,
AF-AP-59, AF-AP-63, AF-AP-65, AF-AP-72).

## Item 0 — the mechanical gates, pasted
The coordinator's gates on these bytes: sandbox `RESULT: rev=488b2385450f files=19 deleted=0 runs=2 identical=yes rc=0 summary="145 passed
in 46.62s 145 passed in 9.02s"`; the lane's own `145 passed in 13.86s` / `145 passed in 13.23s` and its five-file corpus `224 passed in
32.53s`; the PC union run on the landed tip `4 failed, 1561 passed, 9 xfailed in 232.41s` (8 workers, 20260914T121247Z-c6c384a; the four
reds are `tests/test_proof_status.py`'s S0-11 re-acceptance class, none in this suite). Agree or disagree by your own run of
`tests/test_s0_08_containment.py` (twice) AND the five-file set (`tests/test_s0_08_containment.py tests/test_spec_probe_schemas.py
tests/test_validate_ledger.py tests/test_proof_runner.py tests/test_ledger_gen.py`), counts pasted. Then: the negative control through
the real checker (`python3 proofs/S0-08/check_containment.py proofs/S0-08/fixtures/evidence-crun` → `failure_reason: containment: P1 host
kernel …, not gVisor`, rc 1 — the kernel string is the FIXTURE's recorded one, not this host's: say so); `ap_screen.py` over
`check_containment.py`, `run_containment.sh`, `canaries/` (the coordinator's run: 0 hits) and `--tests` (AF-AP-34 ×8 — the guard
assertions' own words; classify by run); pyflakes; `bash -n`; `sh -n` on P1-P8; the FILE IDENTITY table against the PIN; the report's
claims resolved against the PIN yourself (its refs are prose); the external-command census by pid.

## Items
1. **F3 — the closed argv grammar (`C:60-70` the constants; `C:200-212` `expected_run_argv`; `C:258-285` `_check_run_argv`, position-exact;
   the runner's two argv shapes `R:198-212`).** VERIFY-G2's red table as committed tests (`T:1197-1259`): `--privileged=true`,
   `--cap-add=SYS_ADMIN`, `--volume=/host:/host`, `--mount=type=bind,src=/,dst=/host`, two-token `--pid host`, an appended
   `--network=none`, a duplicated required pair, a reordered pair, mutant 51's `--privileged=true` before the image — each rc 1 naming
   the position and token; the runner's exact runsc argv AND its crun argv pass. Then the grammar's own INPUTS, all read from the
   identity: `runtime` selects the pair set by `Path(runtime).name == "runsc"` (`C:206`) and is bound nowhere else by the checker — the
   binary is bound only through `runsc_version`/`runsc_sha256` (`C:304-317`; the runner hashes `$RUNTIME` when executable, `R:259-261`) —
   attack `runtime: "/tmp/runsc"`, `"runsc"`, `"/usr/local/bin/runsc/"` (a trailing slash), `"crun"` with the runsc pairs: which pass,
   and does the spec's pinned-identity table pin the PATH (if so, the checker's silence is a finding with its red test); `data_volume`
   (`C:196`): 16 UPPERCASE hex, 15 hex, a name the runner can never generate; the `-v` value mounted at `/opt/data2`; a wrong `image`
   with a matching argv → confirm by run that `_check_image_identity` (called first, `C:326`) names it before the argv check does. The two
   static runner tests `T:1170-1178` and `T:1189`: what do they PARSE — if a runner variant that carries the same substrings in a comment
   or a dead branch stays green, they are mirrors of the runner's text: say so with the red test that would make them gates.
2. **F4 — the observer uid READ BACK (`P1.sh`-`P8.sh`: `observed_exec_uid="$(id -u)"`; `C:334-342` `check_observer_identity`, run after
   `check_p1` and before P2 (`C:534-536`); the exec wrapper `R:394-397` `podman exec -i --user "$CANARY_EXEC_UID" … sh -s < "$script"`).**
   Read each canary: is `id -u` evaluated INSIDE the same exec as the observation (the line that composes `observed`)? Attacks on the
   checker: typed `canary_exec_user: "10000"` with ONE canary's `observed_exec_uid: "0"` (mutant 50's shape — named, which canary);
   `"10000\n"`, `" 10000"`, `10000` (int — `_field` `C:176-186` names the type), the key absent on one canary and present on seven;
   every canary `"0"` with the typed value `"0"` (refused at `C:288-301` first — which message); a canary line duplicated or carrying
   another canary's id (`C:128-160` refuses — reproduce). Order: a bundle failing P1 never reaches the uid check — state whether that
   ordering hides anything for a partial-evidence reading. The live readback is NOT exercised (no container ran): write the exact
   per-canary line the coordinator's first runsc run must show and the one value that would prove the exec ran as root.
3. **F10/F11 — the archive build and the MEASURED image (`R:119-128` the preflight, `R:133-150` `git archive` of `PINNED_COMMIT` into a
   runner-owned `BUILD_CONTEXT` + `podman build --build-arg HERMES_GIT_SHA=…`; `R:156-165` the immutable id/digest guards; `R:271-292` the
   three readbacks and their exit-4 guards; `C:224-256` `_check_image_identity`; the Dockerfile `:325-342`).** Attacks on the checker:
   `image_id` in UPPERCASE hex (lowered at `C:228` — accepted; intended?); `sha256:` + 63 hex; `container_image_id` ≠ `image_id`;
   `image_build_sha` = the commit plus `\n`; `image_provenance: {"revision": <commit>}` alone (the upstream fields `image`, `version`,
   `schema`, `deployment_kind`, `manager` are UNBOUND — is `version` from the pinned `pyproject.toml` worth binding? decide);
   `image_provenance` a string; `revision: null`; `image_source_commit` right with `image_build_sha` wrong (which failure names first).
   STATIC on the runner (never run it): the archive context vs an upstream checkout build — `.git` is absent from an archive (grep the
   Dockerfile for `git ` / `.git` reads at build time; `.dockerignore`?): state what could differ; is the porcelain check `R:124-128`
   still load-bearing once the archive is the context (a dirty tree cannot leak — keep or drop, with the reason); `tar -xf` without
   `--no-same-owner` (the lane's §8); the fixed `/tmp/s0-08-run.err` and `/tmp/s0-08-canary.err` (predictable temp paths on a shared
   host — classify against the registry); the readbacks `R:272-273` run as the image's default user (`USER root`, Dockerfile `:298`) —
   correct as is? Then the exit-code semantics: `exit 2` at `R:160,164` vs `exit 4` at `R:179,276,280,292` — which does the proof-runner
   read as deferred vs failed for the positive leg (the S0-08 `spec.json` `expect` table) — a build-time `exit 2` read as "deferred"
   would be a hollow deferral: decide by reading `scripts/proof-runner`.
4. **F1 — the P6 domain made explicit (`R:186-190` the fresh `s0-08-data-<16 hex>` volume, `R:202,210` `-v …:/opt/data`, removed by
   `cleanup` `R:91-103`; `C:79-89` `CONTAINER_MAX_PIDS = 32` and its derivation comment).** Re-derive the bound for THIS configuration:
   with an EMPTY `/opt/data`, which s6 services start (the pinned `docker/s6-rc.d/user/contents.d/`), what the stage-2 hook at
   Dockerfile `:309-311` does to an empty dir, whether `container_boot.py` still walks `/profiles/` — is 32 now derived or still typed
   (VERIFY-G2 item 2)? The checker sees only the volume's NAME: nothing in the bundle proves it was EMPTY when the container started —
   name the observation that would (a canary's `ls -A /opt/data` at exec time, the `mount` line) and grade its absence. Attacks on
   `own_pid_count` (`C:477-491`): `"0"`, `"-1"`, `"32"`, `"33"`, `"032"`, `"1e1"`, `" 32"`, `"²"` (`str.isdigit()` is True for a
   superscript, `int()` then raises `ValueError` — `main` `C:552-563` catches only `Deferred`/`Failure`: reproduce the traceback, its rc,
   and what the proof-runner records for a checker that dies without a `failure_reason:` line), `"٣"` (an Arabic-Indic digit: isdigit
   True, `int()` = 3 — passes as a count; state whether the count must be ASCII).
5. **F2/F5 — the floors (`C:288-301` `canary_exec_user` string-exact, the int named; `C:477-491` the count floor).** VERIFY-G2's survivors
   31, 32 and 45 dead by NAME — re-run each; the absent-field reason preserved (`C:289-291`).
6. **F6/F8/F7 — the claims narrowed, the fixture split, the control declared.** `P4.sh` and the spec now claim "the exec environment
   exposed to the runtime uid" — quote both; is the claim exactly what P4 measures? The fixture tests `T:1607-1668` (producible by the
   shipped canaries) and `T:1669-…` (every pinned field): the venue-independent arm and the capture-host arm — run them HERE; forge
   `uname_r` in a scratch copy of the fixture: does the host-dependent half pass silently (the AF-AP-40 shape `if same_host: assert …`
   with no else)? The fixture's `canaries.jsonl` carries `observed_exec_uid: "1000"` on every line while the checker expects `"10000"`:
   the crun bundle fails at P1 BEFORE the observer check (`C:534-536`), so those eight values are never graded — state whether any test
   asserts them and whether the fixture should carry the value a real capture would. F7's live single-holder positive control is
   DECLARED NOT-run (`T:1007` `test_p2_reports_every_holder_of_the_main_cmdline` is the two-holder ambiguity test): write the exact cell the coordinator's run must show.
7. **F9 — P7 stays recorded and documented.** Confirm the spec's paragraph and that no test claims more than "recorded".
8. **Mutants ≥ 45, every one on a scratch copy, the killer line pasted, by-construction survivors named.** The lane produced NO
   mutation evidence (its §4) — this round's score is yours: VERIFY-G2's seven survivors (31, 32, 33, 38, 45, 50, 51) each dead by name;
   G1's 21 and G2's 21 re-run from YOUR reconstruction; the attacks above that no test kills (the `runtime` path, the unbound
   provenance fields, the superscript count, the empty-volume observation).
9. **The 18-class re-scan as an ENUMERATION**: class 11 (the closed grammar IS the world enumeration — state its domain); class 2 (a
   TABLE of every identity field: measured by the runner / typed constant / read back inside the container / forgeable in a bundle);
   every `if <field> == <literal>:` in the checker with its raising other arm (`C:360,400,408,446,497` and the rest — list any without,
   AF-AP-65); every negative control's exact reason (AF-AP-63); no name kill anywhere (AF-AP-34/59).
10. **Discipline** — `file:line` by `sed -n` on the PIN; `report_lint.py` on your own report with `--rev 7f60d83 --map
    C=proofs/S0-08/check_containment.py --map R=proofs/S0-08/tools/pc/run_containment.sh --map T=tests/test_s0_08_containment.py --map
    S=proofs/S0-08/CONTAINMENT-SPEC.md` pasted (MISS 0, UNRESOLVED 0); the process census by pid.
11. **The design.** With the image measured and the observer read back, which SINGLE forged field still defeats the containment
    signature set (VERIFY-G2 item 14) — the bundle is coordinator-supplied bytes; separate what an instrument the forger does not
    control measures from what the checker merely cross-checks for internal consistency. Then the exact PC steps for the coordinator's
    first runsc run (VERIFY-G2's six-step path updated for G3: the archive build with the arg, the baked provenance inspected, the run,
    the per-canary uid, the volume's emptiness, P7's netns) with what a red at each step means; and what round 4 must do, if anything,
    BEFORE the live leg — or state that nothing but the live leg remains.

## Report
Write it to `tasks/briefs/s0-08-support/VERIFY-G3-report.md` inside your tree, draft after EACH item, and return it whole as your final
message. Findings: ALL, no severity filtering, each with `file:line` on the PIN, expected vs observed, the failing input, the minimal
fix, the exact red test, SOLID/UNSURE; reproduced vs reviewed vs skipped; verdict MERGE-READY or NOT-READY with the blocking set and the
cheapest path; the items that are the coordinator's (the live runsc leg) or the owner's named as such.
