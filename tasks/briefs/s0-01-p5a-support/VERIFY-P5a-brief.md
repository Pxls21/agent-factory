# VERIFY-P5a — adversarial grade of lane P5a (S0-01 PC capture tools, round 1: ONE pinned leg-file list, the v2.4 scan header, fail-loud pc_launch, the negative wrapper's exit code)

You are an Opus-5 `adversarial-verifier`. Repo /home/user/agent-factory, branch claude/soundbox-kit-migration-iz1jwf.
**PIN: `582ada4ca1b50deb4c8cc8e15c7f0980831653f4`** — a DETACHED local commit (never pushed, not on the branch): the lane's nine
files + its report on top of the pushed head `6a41bd2`. Grade the bytes of `git archive 582ada4c` (the object is in the shared
store) from a copy under the session scratchpad /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ (`vp5a/`).
Parent for every scope file = `6a41bd2`. Why detached: the lane's `pc_post.sh` emits the v2.4 scan header and the CHECKER at HEAD
still parses v2.3 (`tests/test_s0_01_audit_cp5_controls.py` goes 2-of-3 RED — the lane measured it, NOT_DONE 2) — the files land on
the branch together with the checker's adoption (lane A5k). Read-only git on the shared tree (the lane's files sit there UNCOMMITTED
and declared; three other lanes hold other files); every mutant on scratch copies; every pytest run with an explicit `--basetemp`
under your scratch dir; kill only what you start, PID-targeted; never background a run and stop; no outward actions.

**The ONE bridge action you MAY take (owner ruling 2026-09-07):** a pytest-only PC gate through `scripts/pc_suite.sh launch -n 8 --
tests/test_s0_01_pc_tools.py tests/test_s0_01_pc_post_scan.py` then `wait <RUN_ID>` — from a CLEAN detached worktree of the PUSHED
head `6a41bd2` with the PIN's nine files copied in (`git archive 582ada4c <paths> | tar -x -C <worktree>`; pc_suite ships the
working tree as a patch on a pushed base, and 582ada4c is not on origin). Nothing else on the bridge — in particular NEVER run
`pc_launch.py`/`pc_post.sh`/`run_leg.sh` on the PC: that is the coordinator's re-capture, and the owner's buzz relay is live there.

**Inputs (read in this order):** the brief `tasks/briefs/s0-01-p5a-pc-capture-tools-one-list-fail-loud.md` (the contract) · the
lane's report `tasks/briefs/s0-01-p5a-support/P5a-report.md` (DONE 1-7, 16 mutants, D1-D6, NOT_DONE 1-5, the self-attack) · the
sweep rows it answers: `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` #1, #5, #6, #12, #25, #27, #28, #31, #32, #33, #48, #52 and
`SWEEP-tests.md` 4.2 / 15.2 · the pack `tasks/briefs/s0-01-sweep-support/pack-probe-pctools.md` · the checker's consumer sites at
HEAD: `proofs/S0-01/check_acp_conformance.py:154-155` (the header regex), `:1234`, `:1338` (`rows=0` semantics), `:1249-1253` (F17's
substring `body_pinned`), `:1718-1726` (`_LEG_REQUIRED_FILES`/`_LEG_OPTIONAL_DIRS`), `:1737` (F20 `agent-stderr.txt`) · the real-leg
corpus `S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden` (`bash scripts/realleg_sync.sh check` first) · `docs/INCIDENT-LOG.md`
(AF-AP-40/45/55/59) · the producers the mapping claims to cover: `proofs/S0-01/tools/frame_tee.py` (as in the shared tree — lane B5i's
final bytes, which declare `.runtime-identity.tmp`), `proofs/S0-01/tools/acp_probe.py` (lane N5h's final bytes), `proofs/S0-01/tools/pc/*`.

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-01-p5a-support/P5a-report.md --rev 582ada4c --map pins=proofs/S0-01/pins.py --map
launch=proofs/S0-01/tools/pc/pc_launch.py --map post=proofs/S0-01/tools/pc/pc_post.sh --map tools=tests/test_s0_01_pc_tools.py --map
scan=tests/test_s0_01_pc_post_scan.py` — MISS 0 or a finding; `ap_screen.py` over `proofs/S0-01/tools/pc proofs/S0-01/tools/build_capture_record.py
proofs/S0-01/pins.py` and `--tests` over the two test files — the lane classified 21 production hits; re-classify each by RUNNING it,
and the AF-AP-40 ×10 in `build_capture_record.py` in particular: is EVERY presence-gated read dominated by the required-list check at
`:63-69`, including the two DIRS?

## Items (grade against the brief; red-before on the parent 6a41bd2 for every new test; full files, never -x)
1. **The ONE list (#1).** `PINNED_LEG_FILES` (35 names, four statuses) vs the world: (a) the corpus ⊆ mapping test — run it, then plant
   a NEW file in a scratch copy of a corpus leg and prove the test names it; (b) producers ⊆ mapping — the parser's anchor forms are
   enumerated in the report (`os.path.join(FD|framedir, …)`, `d / "…"`, `f"{fd}/…"`, `"$FD/…"`, `OUT=$FD/…`); write a producer line in
   an idiom it does NOT recognise (e.g. `Path(framedir, "x.json")`, `open(f"{framedir}/{name}")` with a variable name, a bash `>"$FD"/x`)
   and show whether `test_every_producer_write_lands_in_the_pinned_mapping` stays green — a blind spot is a finding, not a blocker,
   unless a CURRENT producer uses that idiom (check: does any?); (c) mapping ⊆ producers; (d) the four statuses — is `transient`
   (`manifest-pre.txt` replaced by gzip) really never a leg entry (a crashed `pc_manifest.sh` between write and gzip leaves it — what
   does a consumer do?), is `excluded_on_collect` proven by the real `tar` test.
2. **The v2.4 header (#5/#6, 4.2/15.2).** `rows` = body count, `table_rows` = the full table, `pinned_present` over the body by ENTRY
   POINT (`argv[0] == PINNED_BUZZ_ACP_EXE_REALPATH` or `argv[1] in (PINNED_TEE_PATH, PINNED_AGENT_REALPATH)`). Attack: a process whose
   argv[1] is the pinned tee path but argv[0] is not python (a shell `cat <tee-path>`) — counted pinned? Should it be? A process with
   argv[0] = a SYMLINK to the buzz-acp realpath (`ps` shows the symlink) — counted? The `readlink /proc/$PID/exe` at `pc_post.sh:120`
   before the signal — reproduce that it refuses a foreign pid. Then the retired v2.3 property (D5): is `table_rows > rows` really the
   only trace of a dropped helper row, and can the CHECKER still tell "a foreign helper row was dropped" from "nothing was there"?
3. **D1 — the `/proc/<pid>/exe` rule replaced by argv equality.** The lane says the exe rule cannot identify the agent (`hermes-acp` is a
   script, exe = the interpreter). Verify against the corpus's `process-scan-after.txt` + `runtime-identity.json`. Then grade the
   replacement's weakness the lane named (argv spoofable) against the oracles it names (`pc_post.sh:120` readlink before signalling,
   `runtime-identity.json`'s exe sha vs `pins.PINNED_BUZZ_ACP_SHA256`): is there a path where a spoofed argv makes `pinned_present`
   wrong AND no oracle catches it? Write the process and run it.
4. **`capture.json` fail-loud (#27/#28).** Empty dir → rc 1 naming 26 files (reproduce); each of the twelve former default-on-absent
   gates: is it now unreachable-when-absent (dominated) or still a default for some input the required check lets through (a required
   file present but EMPTY / a directory where a file is required / a FIFO)? Run all three shapes.
5. **`pc_launch.py` (#12/#25/#31/#32/#48/#52).** Six helpers; each test's red-before on the parent reproduced; then: `wait_for_manifest`'s
   failure signature (a non-empty `.log` with no `.done`) — what about a `.log` that is EMPTY and no `.done` for the whole window (a
   manifest that never started)? `session_closure` via `ps -s <buzz pid>` — reproduce the D6 narrowing (a descendant that `setsid`s
   escapes the closure) and say whether the pinned tree can ever produce that shape (the tee's `Popen` at `frame_tee.py` — cite the
   line in the SHARED tree's B5i bytes, not the parent). `redact_environ` on raw bytes: an environ value with a lone `\xff` — length
   and sha over the raw bytes, not the replaced string (the FINGERPRINT-ON-REPLACED mutant) — re-run it.
6. **`pc_negative.py` (#33).** rc propagated for 0/1/3; a probe that dies by SIGNAL (rc −9 / 137) — what does the wrapper return?
7. **D2 — `agent-stderr.txt` has no positive-leg producer.** Confirm by grep over the SHARED tree's producers (B5i's tee included —
   does the tee drain the agent's stderr anywhere?). Then rule as the verifier: should the TEE write it (evidence) or should the
   checker's F20 become negative-leg-only? Give the argument from what the corpus shows the agent's stderr contains today
   (`buzzacp.log`? nothing?). This decides A5k's item.
8. **The sequencing dependency (NOT_DONE 2/3).** Reproduce the 2-of-3 RED in `tests/test_s0_01_audit_cp5_controls.py` with the PIN's
   `pc_post.sh` over HEAD's checker; then list, from the checker at HEAD, EVERY site A5k must change to adopt v2.4 + the list + the
   entry-point rule — the lane's list of five; find the sixth if there is one (grep the checker for `rows=`, `pinned_present`,
   `_LEG_REQUIRED`, `agent-stderr`, `v2\.3`, `_parse_scan`).
9. **Forward drift (NOT_DONE 4).** B5i's tee declares `.runtime-identity.tmp` (dot-prefixed, skipped by design) and N5h's probe adds
   `raw_b64` inside timeline entries (not a file). Run P5a's producer test against the SHARED tree's B5i/N5h bytes (copy them into your
   scratch tree over the PIN) — green? Any new non-dot name?
10. **The PC gate (the carve-out)** as described above; paste beside the lane's sandbox line (`55 passed` ×2); agree.
11. **Mutants ≥ 24** (the lane's 16 + yours: at least the idiom blind spot, the symlink argv, the empty required file, the signal exit,
    the empty manifest log, a `table_rows` literal); every survivor classed; killers from the run.
12. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census (every process you
    started gone, by pid).
13. **The design.** Is `pins.PINNED_LEG_FILES` the right home (a pins module that other lanes import at collection time), and does the
    four-status vocabulary carry its weight vs two (required/admitted)? Is the entry-point rule the right identity for a SCAN whose
    consumer is a conformance checker, given the oracles elsewhere? Keep it to what you measured.

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-P5a.md` (draft after each item; return it whole). Findings: ALL, no severity
filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact red test, SOLID/UNSURE;
reproduced vs reviewed vs skipped; shared-tree hygiene; verdict MERGE-READY or NOT-READY with the blocking set — and the exact list
of checker changes for A5k, since P5a lands only with them.
