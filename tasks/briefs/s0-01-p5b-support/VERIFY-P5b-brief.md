# VERIFY-P5b — adversarial grade of lane P5b (S0-01 PC capture tools round 2: the list as functions, the entry point narrowed, `transient` gone, the S0-03 launcher seam) on the JOINT checkpoint

You are an adversarial-verifier (the PC Hermes verify lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo
agent-factory, branch claude/soundbox-kit-migration-iz1jwf. **PIN: `77f46a2`** — the JOINT checkpoint that lands three lanes at
once: P5b (this grade), A5k (the checker round 13 — VERIFY-CK13 grades it in parallel) and D5m (the backend — VERIFY-D5m).
P5b's bytes on the PIN: `proofs/S0-01/pins.py` (381 lines, sha `84a1e5c8…` — the coordinator's three-way merge of P5b's 367-line
file with A5k's `require_regular_file` helper; one duplicate import removed), `proofs/S0-01/tools/build_capture_record.py`,
`proofs/S0-01/tools/pc/{pc_launch.py, pc_post.sh, pc_negative.py, collect_leg.sh, run_leg.sh}`, `tests/test_s0_01_pc_tools.py`
(961 lines), `tests/test_s0_01_pc_post_scan.py` (395), `tests/conftest.py` (61, the shared `synthetic_leg` fixture),
`.claude/hooks/edit-snapshot.py` + `tests/test_ap_screen.py` + `tests/test_edit_snapshot_ap_screen.py` (the AF-AP-40 extension and
the AF-AP-57 widening), and the lane's report `tasks/briefs/s0-01-p5b-support/P5b-report.md`. Grade the bytes of
`git archive 77f46a2` from a scratch copy under your lane's scratch dir; every mutant on scratch copies; every pytest run with an
explicit `--basetemp` and the venue exports (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`); every
FIFO/hang probe standalone under `timeout`; kill only what you start, by pid; no outward actions; NEVER launch buzz-acp, the agent
or Hermes — the PC tools are graded through their shims, their unit surface and the real corpus's collected files; never read,
print or commit a credential. Authorization: the owner's own capture tools under test on the owner's system.

**Inputs (read in this order):** VERIFY-P5a's report `tasks/briefs/s0-01-p5a-support/verify-P5a.md` (the round's contract:
F1-F4 BLOCKING, F5-F16, its mutants, "CHECKER CHANGES FOR A5k") · the lane brief
`tasks/briefs/s0-01-p5b-pc-tools-the-list-as-functions-entry-point-narrow-transient-gone.md` · the lane's report `P5b-report.md`
(PREMISE, DONE, DECISIONS, 31 mutants, DISCREPANCIES D1-D9, NOT_DONE 1-6) and P5a's `tasks/briefs/s0-01-p5a-support/P5a-report.md`
· A5k's report `tasks/briefs/s0-01-a5k-support/A5k-report.md` (the checker did NOT adopt the functions — P5b's NOT_DONE 3 stands)
· `docs/INCIDENT-LOG.md` (AF-AP-40, AF-AP-57, AF-AP-64 — P5b's own mutant P8 is its instance, AF-AP-65).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-01-p5b-support/P5b-report.md --rev 77f46a2` with maps for every bare name the
report cites (`pins.py`, `pc_launch.py`, `pc_post.sh`, `pc_negative.py`, `collect_leg.sh`, `build_capture_record.py`, the test
files); the report's own pasted line was worktree-mode on the lane's bytes and pins.py has moved by 14 lines (A5k's helper) —
count the refs that shifted; `ap_screen.py --s0-01` and `--tests`; pyflakes; `bash -n` on the three scripts; the FILE IDENTITY
table against the PIN; `tests/test_s0_01_pc_tools.py tests/test_s0_01_pc_post_scan.py tests/test_ap_screen.py
tests/test_edit_snapshot_ap_screen.py tests/test_s0_01_audit_cp5_controls.py` run directly (P5b's NOT_DONE 2: the audit file was
2-of-3 red in ITS tree; A5k fixed the checker side — green on the PIN?).

## Items
1. **VERIFY-P5a F1-F16 closure by RUN, one row each.** F2: `build_capture_record.py` over EVERY leg of the real corpus (`run-*`
   under the golden dir — build then `--check`); F3/F15/AF-AP-64: the parser's 11-idiom table (`tests/test_s0_01_pc_tools.py:353`)
   — plant a 12th idiom the producers could use (`os.path.join(FD, *parts)`, `f"{FD}/{name}"` with a variable, `Path(FD) / name`,
   `"$FD"/"$sub"/…`, `printf > "$FD/…"`, heredoc redirection) and measure: the floor (D2, `>=` at 17) vs equality — a shrink by
   ONE name at the top producer: caught?; F4: `is_pinned_argv` (`pins.py:317`) attacked with rows the 9-row test lacks —
   `/usr/bin/env python3 <tee>`, `python3 -m <module>`, `bash -c "python3 <tee>"`, `python3.13 <agent> --flag`, `<venv>/python`
   without a version suffix, a pinned script as argv[2], an argv[0] that is a symlink to the pinned buzz-acp (F5's documented
   limit — measure the residual with the pidfile absent); F6 an empty required file; F7 the receipt read (both twins); F8 a
   signal the 4-row table lacks (SIGSEGV, a stop signal); F9 dir/FIFO by name (a socket? a dangling symlink?); F10 `transient`
   gone (`excluded_on_collect`, `manifest-*.txt` dropped) — the real-tar test with a traversal name, a manifest that a version
   REQUIRES; F11/F12/F13/F16.
2. **The ONE list as functions (`pins.py:255-300`).** `required_files(version)` raises on an unknown version: attack with
   `"v2.10"`, `"V2.4"`, `"v2.4 "`, `"v2.4.1"`, `""`, `None`; `PINNED_SCAN_VERSIONS` ordering (`_version_key`); `corpus_version()`
   on malformed headers (two headers, a header in the body, a header with trailing fields, CRLF); `entry_allowlist()` =
   required | optional | dirs — a name in both required and optional.
3. **Two consumers, two predicates (the coordinator's finding).** The producer (`pc_post.sh`'s heredoc) calls
   `pins.is_pinned_argv` over the live `ps` table; the checker (A5k) classifies the COLLECTED text with its own
   `_is_pinned_process`. Run both over the same rows (the tests' ps shim + the real corpus scans + your F4 rows) and paste every
   disagreement — VERIFY-CK13 does the same from the checker's side; your table is the producer's side. P5b's D6: the two
   `corpus_version` answers on a v2.4 header without `tee-status.json`.
4. **The S0-03 launcher seam (`pins.hermes_home` `:348`, `pc_launch.py:36`, `:197-267`).** The constant never moves (D3;
   `tests/test_s0_01_pc_tools.py:950`, mutant P12): attack with `S0_01_HERMES_HOME` set to a FIFO, a directory without a profile,
   a relative path, a path with a trailing slash, an empty string; the CLI really reaches the validator (3 rows) — a 4th argv
   shape; `--model` opened for a foreign leg (D4) — S0-01's own legs still refuse a foreign model?
5. **The AP screen changes (D1, F11 of VERIFY-N5h).** The AF-AP-40 `else\b` extension (mutant P19) and the AF-AP-57 alternation
   (`edit-snapshot.py:186-190`): the hook's tests end to end; D8's ordinal gate at `tests/test_s0_01_check_acp_conformance.py:4493`
   — still there on the PIN (A5k's file)?
6. **The 31-mutant table** reconstructed on YOUR scratch copies + the attacks above → ≥ 40, killers pasted with the env stated.
7. **The 18-class re-scan** on the P5b files by RUN; every `if <field> == <literal>:` without a raising other arm (AF-AP-65); the
   report's class table agreed or disagreed per row.
8. **NOT run on the PC — what CAN be run now without launching anything?** `pc_launch.py --help`/argv validation as a
   subprocess, `pc_post.sh`'s heredoc over a saved ps table, `collect_leg.sh` over a synthetic run dir, `pc_negative.py`'s
   signal table; state what remains NEVER executed end to end (the real capture) and what the S0-01 re-capture needs from
   these tools (VB-F12/F13/F14 are the coordinator's).
9. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census by pid.
10. **The design.** Floor vs equality (D2); the documented F5 limit vs `/proc/<pid>/exe` (D9); the ONE list with one consumer
    (P5b's NOT_DONE 3 — A5l's item); what round 3 (P5c) must do and what is the coordinator's.

## Report
Write it to `tasks/briefs/s0-01-p5b-support/VERIFY-P5b-report.md` inside your tree, draft after EACH item, and return it whole as
your final message. Findings: ALL, no severity filtering, each with file:line on the PIN, expected vs observed, the failing input,
the minimal fix, the exact red test, SOLID/UNSURE; reproduced vs reviewed vs skipped; verdict MERGE-READY or NOT-READY with the
blocking set and the cheapest path; the items that are the coordinator's or A5l's/P5c's named as such.
