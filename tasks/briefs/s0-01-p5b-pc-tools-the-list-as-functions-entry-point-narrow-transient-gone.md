# Lane P5b — S0-01 PC capture tools, round 2: the ONE list as FUNCTIONS (the version rule in one place), `is_pinned` narrowed to a real entry point, the producer parser's idioms + a coverage pin, `transient` gone, the empty-timeline and signal-death classes, the backend test on the shared fixture, and the S0-03 launcher seam (sandbox Opus 4.6 `code-implementer`; PC Hermes when the slot frees)

PIN: (HEAD at dispatch — the commit carrying this brief; the tree ALSO carries lane P5a's uncommitted files — `sha256sum
proofs/S0-01/pins.py | cut -c1-16` = `974b86f2445d239f`, `proofs/S0-01/tools/pc/pc_post.sh` = `8db8caeaf5e56f28`; verify BEFORE the
first edit, and grade against the DETACHED verifier pin `582ada4c` (`git show 582ada4c --stat`) as the parent of P5a's bytes.)

**Why:** VERIFY-P5a (`wf-results-r5/VERIFY-P5a.md`, copied to `tasks/briefs/s0-01-p5a-support/verify-P5a.md` — read WHOLE first) is
NOT-READY with four blockers and twelve more findings, all reproduced: F1 the PIN turns `tests/test_s0_01_scripted_backend.py::
test_build_capture_record_roundtrip_check` red (a synthetic 7-file leg the new required gate rejects); F2 `build_capture_record.py`
hard-fails EVERY existing corpus leg (`missing required leg files: tee-status.json`) because the version rule
(`PINNED_LEG_FILES_SINCE`) lives only in the TEST mirror; F3 the producer-subset gate is blind to the lane's own `os.path.join(fd, …)`
idiom (mutant V1 survived) + three more idioms (F15); F4 `is_pinned` counts `/usr/bin/cat <tee> -` as pinned (a real process, reproduced)
— fail-closed at the checker for the WRONG reason (an editor open on frame_tee.py fails the leg). Lane A5k (the checker's consumer
side, on the PC) lands together with this lane; its verifier list (VERIFY-P5a §CHECKER CHANGES 1-12) is A5k's/A5l's, not yours —
EXCEPT item 12 (the backend test) and the `pins` functions A5k must call, which are yours.
**Inputs (read in this order):** `verify-P5a.md` (whole) · `tasks/briefs/s0-01-p5a-support/P5a-report.md` · the P5a brief
`tasks/briefs/s0-01-p5a-pc-capture-tools-one-list-fail-loud.md` · `proofs/S0-01/pins.py` (P5a's bytes) · the real corpus
(`S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden`; `bash scripts/realleg_sync.sh check` first) · the S0-03 lane's
blocker: `tasks/briefs/s0-03-support/O1-report.md` (leg B cannot invoke `pc_launch.py`: `pins.py:18` hard-codes S0-01's Hermes home;
`pc_launch.py:189-190` constrains `--leg`/`--model`) and `proofs/S0-03/tools/pc/run_s0_03_legs.sh` (what it needs from the launcher) ·
`docs/INCIDENT-LOG.md` (AF-AP-40, AF-AP-42, AF-AP-55, AF-AP-59) · `.claude/hooks/edit-snapshot.py` (AP_SCREEN — for the F7 ternary row).
**Scope:** `proofs/S0-01/pins.py` (P5a's bytes + your functions; NEVER touch the other pins) · `proofs/S0-01/tools/pc/{pc_post.sh,
pc_launch.py, pc_negative.py, collect_leg.sh}` · `proofs/S0-01/tools/build_capture_record.py` · `tests/test_s0_01_pc_post_scan.py` ·
`tests/test_s0_01_pc_tools.py` · `tests/conftest.py` (the shared synthetic-leg fixture — ADD-only) · `tests/test_s0_01_scripted_backend.py`
(ONLY `test_build_capture_record_roundtrip_check` and its fixture — nothing else in that file; it belongs to the backend lane) ·
`.claude/hooks/edit-snapshot.py` (ONE new AP_SCREEN row for the AF-AP-40 ternary form) · report `tasks/briefs/s0-01-p5b-support/P5b-report.md`.
NOT yours: `check_acp_conformance.py`, `negative_contract.py`, `check_initialize.py` and their tests (A5k), `frame_tee.py`,
`acp_probe.py`, `scripted_backend.py`, `proofs/S0-03/*` (the seam is on YOUR side of the boundary; O1's runner adapts after).
Shared-tree rules as every lane: never `git stash/checkout/restore/reset/add/commit/push`; gates from a `git archive <PIN>` copy + P5a's
files + yours under /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/p5b/ (delete it when done — the temp
filesystem filled tonight); explicit `--basetemp`; kill only your own pids; NEVER background a run and stop; no outward actions; NO PC
bridge; never read or print a credential. Interpreter `/root/venv-agent-factory/bin/python`.

## Design (pinned — build it, do not redesign it)
1. **The list as FUNCTIONS (F2, the design ruling).** `pins.required_files(version) -> frozenset`, `pins.entry_allowlist() -> frozenset`
   (`required | optional | PINNED_LEG_DIRS`), `pins.corpus_version(leg_dir) -> str` (from `process-scan-after.txt`'s header:
   `v2.4` / `v2.3` / `v2.2` — the ONE detector; RAISES on a malformed header, never defaults). `build_capture_record.py` (build AND
   `--check`), the tests' `_required_for`, and A5k's checker all call these; the test mirror at `tests/test_s0_01_pc_tools.py:81-87` is
   DELETED. Red-before: the tool over a copy of `golden/run-1` → `missing required leg files: tee-status.json` rc 1; green: rc 0,
   `9 raw files, 11 timeline entries`; a new `test_build_capture_record_accepts_a_v2_2_corpus_leg` (the corpus copied to tmp_path).
2. **The completeness gate on the BUILD path only (F1/F16)**; `--check` keeps its diagnosis (`differs from re-derived content` over a
   tampered record with one name absent — the red test). The backend round-trip test rebuilds its leg through ONE shared fixture
   `synthetic_leg` in `tests/conftest.py` (lifted from `tests/test_s0_01_pc_tools.py:285 _synthetic_leg`, reading `pins.PINNED_LEG_FILES`)
   — imported by both test files, never copied; no hand list of names, no xfail.
3. **`is_pinned` narrowed (F4/F5).** `argv[0] == PINNED_BUZZ_ACP_EXE_REALPATH`, OR (`basename(argv[0]).startswith("python")` AND
   `argv[1] in PINNED_SCRIPTS`); still matches all three real corpus rows (assert it against `golden/run-1/process-scan-after.txt`).
   Put the rule in `pins.is_pinned_argv(argv) -> bool` so the heredoc in `pc_post.sh`, the test shim and A5k's checker call ONE
   function (the heredoc imports pins by path — it already runs Python). F5 (a pinned BINARY by a symlink path): decide — resolve
   argv[0] through `/proc/<pid>/exe` for the binary arm only (where it works) or document the limit; state which and why.
   Red tests: the shim row `/usr/bin/cat <tee>` NOT counted; `/usr/bin/python3 <tee>` counted; `<venv>/python3.13 <agent>` counted.
4. **The producer parser (F3/F15) + a coverage pin.** Idioms: `os.path.join(FD|fd|framedir, "…")`, `Path(framedir|fd, "…")`,
   `d / "…"`, `f"{fd}/…"`, `"$FD"/…`, `"${FD}"/…`, `$FD/…`, `OUT=$FD/…`; and the per-producer NAME COUNT is pinned (a refactor that hides
   a write fails loudly). Mutants V1-V4 all die (paste).
5. **`transient` gone (F10).** `collect_leg.sh` excludes `manifest-*.txt`; the two names become `excluded_on_collect`; the `| transient`
   escape hatch at `tests/test_s0_01_pc_tools.py:605` removed; the real-tar test asserts `manifest-post.txt` is NOT unpacked.
6. **The remaining classes.** F6 an EMPTY `timeline.jsonl` → rc 1 naming it (`stat().st_size == 0`); F7 the receipt read at
   `build_capture_record.py:128` loud (`accepted: "receipt-absent"` is NOT acceptable — a missing receipt is a named failure or a
   named observation the checker can see; pick the failure) + the AP_SCREEN row for the AF-AP-40 ternary form (`if X.exists() else`)
   with its own unit test in `tests/test_edit_snapshot*.py` if one exists, else a row test beside `scripts/ap_screen.py`'s; F8
   `pc_negative.py` maps a signal death to `128 + sig` and the parametrisation gains a SIGKILLed probe (main() == 137; mutant V7
   dies); F9 the required-gate test gains `shape ∈ {dir, fifo}` (mutant V8 dies); F14 one docstring line on `wait_for_manifest`'s
   empty-log case.
7. **The S0-03 launcher seam (O1's blocker).** `pins.py:18`'s Hermes home gets an env override (`S0_01_HERMES_HOME`, validated: an
   existing directory, else exit 64 named) and `pc_launch.py` accepts `--profile <path>` (a proof-owned Hermes config) and a `--leg`
   value outside S0-01's set ONLY when `--profile` is given (the S0-01 legs keep their closed set; the constraint stays for S0-01's own
   runs). Tests: the default path unchanged (the S0-01 legs refuse a foreign `--leg` without `--profile`); with `--profile` the launch
   env carries the profile path and the leg name; the override validated. O1's runner is NOT edited by you — state in the report the
   exact argv it should use.
8. **Report discipline** as every lane: `report_lint.py` at `--rev <PIN>` (the aliases: `pins=`, `launch=`, `post=`, `neg=`, `bcr=`,
   `tools=`, `scan=`, `conftest=`) MISS 0 NEAR 0 — the lane's F13 was the worktree-mode paste; `ap_screen.py` over the production
   files + `--tests`; the gates PASTED twice from the static copy: `bash scripts/test_summary.sh tests/test_s0_01_pc_tools.py
   tests/test_s0_01_pc_post_scan.py tests/test_s0_01_scripted_backend.py tests/test_s0_01_audit_cp5_controls.py` (the audit test stays
   RED until A5k — say so with the count; the OTHER three must be green); the six-file adjacent set VERIFY-P5a ran
   (`frame_tee`, `acp_probe`, `negative_contract`, `check_initialize`, `audit_cp5`, `scripted_backend`) once, pasted; mutants ≥ 20 (the
   verifier's V1-V10 + yours), killers from the run; the 18-class self-sweep; NOT_DONE; DISCREPANCIES (anything the verdict got wrong —
   with the run).
