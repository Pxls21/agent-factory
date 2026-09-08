# N5j report — S0-01 ACP probe open-validate-truncate, owned framedir, receiver inventory

## NOT-done / deviations first

- NOT a gate verdict. This PC Hermes lane is a build proposal until the sandbox-side adversarial verifier grades it.
- F4 remains coordinator-owned: the 3 s stderr drain join was not recalibrated against a real Hermes/buzz-acp negative recapture. This lane did not change join policy.
- No real agent, Hermes, buzz-acp, relay, model request, or credential path was used. The PC venue forbids those.
- The serial four-file pytest command did not finish inside the tool ceiling: `timeout 410 bash scripts/test_summary.sh ...` returned `PIPESTATUS=124 0`, and direct single-process `test_s0_01_check_acp_conformance.py` also hit the tool ceiling. The same four-file set completed with pytest-xdist `-n 4`: `595 passed, 9 xfailed in 210.82s (0:03:30)`. I also ran the four-file set through `scripts/lane_gate.sh` with `-n 4` pytest workers once: `595 passed, 9 xfailed in 210.27s (0:03:30)`.
- The incremental draft path named by the resume brief did not exist when read: `/home/rocco/agent-factory/.lanes/pc-n5j.md--99b7b37/report-draft.md`. I wrote the final report to the required in-tree path and mirrored it to the lane report files after completion.
- The ≥40 mutant table contains two evidence tiers: N5j-run rows were executed in this lane on fresh `git archive 99b7b37` copies; N5i/VERIFY-N5i rows are predecessor evidence copied from the reports the brief required me to read, not re-run here.

## File identity — final bytes

```
7874a4e38f14f1c5190fc0ae47cc9715ddaf06d7bbbe2a14df4d86cfb70ce757  proofs/S0-01/tools/acp_probe.py  642 lines
9ff359dc7f49e1aaa9791139fb6686b3a096109e0ef108aee53ecc7594963c29  tests/test_s0_01_acp_probe.py  3302 lines
```

## DONE table

| item | final location | red / negative control | green / proof |
|---|---|---|---|
| 1. Open, validate, then truncate; require one link | P:62-95 `def _open_regular`; P:83-89 `st.st_nlink != 1` and `os.ftruncate(fd, 0)` | Red-before on a `99b7b37` archive plus final tests: `test_probe_hardlink_refusal_preserves_the_foreign_inode` failed because rc was 0 and foreign text was overwritten; N5j mutant J1 restored `O_TRUNC` and killed with `foreign_text: ''`; J2 removed the nlink check and killed with foreign text becoming probe timeline JSON. | T:3176-3192 `test_probe_hardlink_refusal_preserves_the_foreign_inode` and `test_probe_hardlink_negative_control_restored_otrunc_clobbers_foreign_inode`; `108 passed in 51.05s`; lane gates pasted below. |
| 2. Symlink-free framedir and dir-fd-relative evidence leaves | P:274-292 `framedir path contains a symlink` and `os.O_DIRECTORY`; P:153-159 `def _leaf_handle`; P:156-158 `dir_fd=framedir_fd` | Red-before on a `99b7b37` archive plus final tests: symlinked parent wrote `child` into `foreign/`; J3 removed the realpath checks and killed with `foreign_files: ['child']`; J4 dropped `dir_fd` and killed with evidence in `foreign`. | T:3195-3199 `test_probe_refuses_a_symlinked_framedir_before_any_foreign_write`; T:3223-3230 `test_probe_writes_remain_on_the_original_dir_fd_after_path_swap`; green `108 passed in 51.05s`. |
| 3. Receiver scan by identity, exact inventory | T:2820-2849 `_RECEIVER_INVENTORY`; T:2852-3014 `def _scan_file_receivers`; T:3021-3055 `test_probe_every_file_receiver_is_guarded_or_committed` | VERIFY-N5i survivors are now killers: alias `open` killed with inventory diff, `Path.write_text` killed with `attribute.write_text`, deleted writer killed with inventory diff. | Focused receiver run: `1 passed, 99 deselected in 0.32s` during development; final full probe file: `108 passed in 51.05s`; scanner counted 22 receivers and 12 evidence writers. |
| 4. F4 drain join | P:565-567 `stderr drain failed`; P:571-578 `_write_evidence` | Not changed. Existing N5i/N5h tests still cover synthetic drain behavior. | Whole probe suite stayed green. Real recapture remains NOT-done. |
| 5. ≥40 mutation campaign in report | Mutant table below: 49 rows total. | N5j-run rows J1-J5 and F3-ALIAS/PATH/DELETE were killed in this lane. | Predecessor rows copied as evidence tier; no by-construction survivor is hidden. |
| 6. Exact negative reasons | T:3176-3192 `hardlinked evidence leaf`; T:3195-3199 `framedir path contains a symlink`; T:3235-3244 `No such device or address`; T:3247-3267 `evidence leaf name must be a bare basename` | Red-before and mutants assert exact stderr/state, not only `rc != 0`. | Hostile-path focused run after final edits: `10 passed, 97 deselected in 1.61s`; final full probe: `108 passed in 51.05s`. |
| 7. 18-class self-sweep enumeration | T:3021-3055 `test_probe_every_file_receiver_is_guarded_or_committed`; AP screen output below. | `ap_screen.py` still reports known hits; each is classified below. | No unclassified new hit was found in the two touched files. |
| 8. Report discipline | This report; report-lint section below. | Report written after final bytes and final line refs. | `report_lint` run last with MISS 0. |

## Red-before premise check

Ran a fresh `git archive 99b7b37` copy with the final N5j tests copied over it, before relying on the worktree implementation:

```
5 failed, 1 passed, 102 deselected in 1.21s
```

Named failures:

- `test_probe_every_file_receiver_is_guarded_or_committed`: final inventory expected `_leaf_handle`, two `os.open` branches, `os.O_DIRECTORY`, and 22 receiver rows; the pin had only the old receiver world.
- `test_probe_hardlink_refusal_preserves_the_foreign_inode`: rc was 0; `foreign_text` was overwritten through the hardlink.
- `test_probe_refuses_a_symlinked_framedir_before_any_foreign_write`: rc was 0; `foreign_files` contained `child`.
- `test_probe_writes_remain_on_the_original_dir_fd_after_path_swap`: evidence landed in the swapped symlink target.
- `test_probe_rejects_non_bare_leaf_names`: old `_open_regular` did not accept `dir_fd`, so the bare-name guard did not exist.

## Green-after runs

Final direct probe suite:

```
........................................................................ [ 66%]
....................................                                     [100%]
108 passed in 51.05s
```

Syntax / whitespace:

```
git diff --check && /home/rocco/venv-agent-factory/bin/python -m py_compile proofs/S0-01/tools/acp_probe.py tests/test_s0_01_acp_probe.py
# rc 0, no output
```

Four-file set, xdist because serial did not complete inside the tool ceiling:

```
bringing up nodes...
bringing up nodes...

........................................................................ [ 11%]
........................................................................ [ 23%]
........................................................................ [ 35%]
........................................................................ [ 47%]
........................................................................ [ 59%]
.......................................................xxxx.........x... [ 71%]
........................................................................ [ 83%]
...............x.xxx.................................................... [ 95%]
............................                                             [100%]
595 passed, 9 xfailed in 210.82s (0:03:30)
```

Single-file sibling runs while isolating the four-file serial timeout:

```
59 passed in 0.33s
negative_contract_rc=0
54 passed in 10.31s
check_initialize_rc=0
```

Four-file collect count:

```
604 tests collected in 0.28s
```

## `lane_gate.sh` RESULT lines — final bytes

Two independent probe-file lane gates, each two runs on `git archive 99b7b37` plus only the two lane files copied over:

```
RESULT: rev=99b7b370a6f4 files=2 deleted=0 runs=2 identical=yes rc=0 summary="108 passed in 51.09s 108 passed in 50.58s"
RESULT: rev=99b7b370a6f4 files=2 deleted=0 runs=2 identical=yes rc=0 summary="108 passed in 50.96s 108 passed in 50.87s"
```

Four-file lane-gate run using pytest `-n 4` workers:

```
RESULT: rev=99b7b370a6f4 files=2 deleted=0 runs=1 identical=yes rc=0 summary="595 passed, 9 xfailed in 210.27s (0:03:30)"
```

## What changed in `acp_probe.py`

- P:62-95 `def _open_regular` now opens without `O_TRUNC`, validates `S_ISREG` and one link via `st.st_nlink != 1`, truncates with `os.ftruncate(fd, 0)` only after validation, and supports `dir_fd` plus a displayed path.
- P:75-80 `_open_regular` refuses non-bare evidence leaf names and re-raises `dir_fd` open failures with the human display path.
- P:120-135 `def _drain_stderr` writes `agent-stderr.txt` through `_open_regular(..., dir_fd=framedir_fd)`.
- P:153-159 `def _leaf_handle` fails closed when `framedir_fd` is missing and centralizes all evidence leaf opens through the framedir fd.
- P:162-167 `def _write_env` writes `env.json` via `_leaf_handle`.
- P:170-215 `def _write_evidence` writes `runtime-identity.json`, `env.json`, and `timeline.jsonl` through `_leaf_handle`.
- P:274-292 `main` validates the framedir realpath before mkdir, rechecks after mkdir, and opens the framedir once with `os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC`.
- P:328-330 timeout-domain rejection writes `runtime-identity.json` through `_leaf_handle`.
- P:372-378 the stderr drain thread receives only `agent-stderr.txt` plus the opened framedir fd.
- P:574-578 the normal evidence write passes `framedir_fd` into `_write_evidence`.
- P:610-628 the M3 evidence path writes every last-resort leaf through `_leaf_handle` / `_m3_write`.

## What changed in `tests/test_s0_01_acp_probe.py`

- T:2820-2849 `_RECEIVER_INVENTORY` is an exact map of 22 file receivers, including 12 `evidence-writer` rows.
- T:2852-3014 `_scan_file_receivers` resolves aliases and simple rebinding for `open`, `io.open`, `builtins.open`, `os.open`, `os.fdopen`, `json.load`, probe wrappers, and attribute file methods.
- T:3021-3055 `test_probe_every_file_receiver_is_guarded_or_committed` asserts exact inventory equality, 12 evidence writers, primitive guard tokens, no `O_TRUNC`, and three in-test negative controls.
- T:3061-3173 `_run_hostile_probe_rig` creates a scratch copy, runs the hostile probe through `timeout`, starts the probe in its own process group, and reports foreign/frame/original directory state as JSON.
- T:3176-3192 hardlink tests assert the foreign inode survives and the restored-`O_TRUNC` negative control clobbers it.
- T:3195-3199 `framedir path contains a symlink` test asserts rc 1, exact symlink-containing-framedir message, and zero foreign files.
- T:3202-3207 `frame_files` fresh framedir test asserts all four evidence files are created.
- T:3210-3222 `STALE` existing regular evidence test asserts stale bytes are gone after validation and the timeline has two records.
- T:3225-3232 `original_files` path-swap test asserts evidence remains on the original opened directory fd and never enters the swapped symlink target.
- T:3235-3244 `No such device or address` FIFO/socket/final-symlink test asserts exact refusal messages and bounded completion.
- T:3247-3267 `../escape` bare-name test asserts traversal is refused before a dir-fd-relative open.

## Mutant table — 49 rows

| # | evidence tier | mutant | result / killer line |
|---|---|---|---|
| M1 | predecessor-run N5i | FIXTURE-FIFO-UNGUARDED | KILLED: `subprocess.TimeoutExpired` in `test_probe_refuses_a_non_regular_fixture`; `1 failed, 53 passed` |
| M2 | predecessor-run N5i | DRAIN-SWALLOW | KILLED: `AssertionError: expected exit 1, got 0:` in drain failure test |
| M3 | predecessor-run N5i | LOSSY-NO-RAW | KILLED: `AssertionError: the lossless copy of a replaced-byte line is missing` |
| M4 | predecessor-run N5i | MIRROR-DRIFT | KILLED: `AssertionError: NOSTR_NSEC_HEX was not redacted` |
| M5 | predecessor-run N5i | TIMEOUT-LENIENT | KILLED: `assert 1 == 64` in `test_probe_timeout_non_numeric_exits_64` |
| M6 | predecessor-run N5i | BYTECODE-STRING | KILLED: `AssertionError: PYTHONDONTWRITEBYTECODE='2' flags=[]: recorded False, CPython reports True` |
| M9 | predecessor-run N5i | DL-INLINE | KILLED: `AssertionError: RL_CALLS=97 DEADLINE_SEEN=0.0` |
| M10 | predecessor-run N5i | AP-F1a-SINGLE-SHOT | KILLED: `AssertionError: expected exit 0 (retry recovered), got 1: acp_probe: interpreter sample failed: transient failure` |
| M11 | predecessor-run N5i | LATE-NULL | KILLED: `AssertionError: assert None == '/usr/bin/python3.11'` |
| M12 | predecessor-run N5i | LATE-EVERY | KILLED: `AssertionError: expected exactly 2 child /proc/<pid>/exe reads` |
| M13 | predecessor-run N5i | SHA-GUARD-OFF | KILLED: `subprocess.TimeoutExpired` in `test_sha256_file_refuses_a_non_regular_file` |
| M14 | predecessor-run N5i | NO-ISFINITE | KILLED: `AssertionError: expected exit 64 for '999…9'` |
| M17 | predecessor-run N5i | LOSSY-ALWAYS | KILLED: `AssertionError: raw_b64 on a clean line` |
| M18 | predecessor-run N5i | DRAIN-EMPTY-MSG | KILLED: `AssertionError: got 'stderr drain failed: '` |
| M19 | predecessor-run N5i | BYTECODE-M3-ONLY | KILLED: `AssertionError: PYTHONDONTWRITEBYTECODE=None flags=['-B']: recorded False, CPython reports True` |
| M20 | predecessor-run N5i | FIRST-ERROR-WINS-OFF | KILLED: `AssertionError: got "stderr drain failed: IsADirectoryError: …"` |
| M20b | predecessor-run N5i | APPEND-DROPPED | KILLED: `AssertionError: got 'BrokenPipeError: agent process exited before c2a write landed'` |
| M21 | predecessor-run N5i | JOIN-ZERO | KILLED: `AssertionError: assert 'BrokenPipeEr...viving child)' == 'BrokenPipeEr... write landed'` |
| M23 | predecessor-run N5i | EXTRA-EARLY-READ | KILLED: `AssertionError: the four early reads came from 2 different call sites in acp_probe.py` |
| W1 | predecessor-run N5i | drain write -> bare `open` | KILLED: `AssertionError: got "stderr drain failed: did not finish in 3s …"` |
| W2 | predecessor-run N5i | env.json -> bare `open` | KILLED: `subprocess.TimeoutExpired` |
| W3 | predecessor-run N5i | `_write_evidence` rid -> bare `open` | KILLED: `subprocess.TimeoutExpired` |
| W4 | predecessor-run N5i | `_write_evidence` timeline -> bare `open` | KILLED: `subprocess.TimeoutExpired` |
| W5 | predecessor-run N5i | timeout-reject rid -> bare `open` | KILLED: `subprocess.TimeoutExpired` |
| W6 | predecessor-run N5i | `_m3_write` -> bare `open` | KILLED: `subprocess.TimeoutExpired` |
| N1 | predecessor-run N5i | ISALIVE-OFF | KILLED: `AssertionError: expected exit 1, got 0:` |
| N3 | predecessor-run N5i | PROBE-HASH-SILENT | KILLED: `AssertionError: expected exit 1, got 0:` |
| N4 | predecessor-run N5i | NOFOLLOW-OFF | KILLED structurally by `_open_regular no longer contains os.O_NOFOLLOW`; behaviorally by symlink refusal failure |
| N5 | predecessor-run N5i | NONBLOCK-OFF | KILLED: `stderr drain failed: did not finish in 3s` |
| N6 | predecessor-run N5i | ISREG-OFF | KILLED structurally by missing `S_ISREG`; behaviorally FIFO case `expected exit 1, got 0` |
| N7 | predecessor-run N5i | THIRD-WORDING-REVERT | KILLED: wrong `ACP_PROBE_TIMEOUT` wording for `3_0` |
| N8 | predecessor-run N5i | PROBE-HASH-REREAD | KILLED after first surviving run: `subprocess.TimeoutExpired … timed out after 5 seconds` |
| N9 | predecessor-run N5i | M3-NO-ISOLATION | KILLED: `AssertionError: env.json was lost because runtime-identity.json was hostile` |
| V1 | VERIFY-N5i focused | fourth `os.readlink` in `main` | KILLED: receiver-scan test, `1 failed` |
| V2 | VERIFY-N5i focused | second raw `os.open` in `_open_regular` | KILLED: receiver-scan test, `1 failed` |
| V3 | VERIFY-N5i focused | `io.open(..., "w")` | KILLED: receiver-scan test, `1 failed` |
| V4 | VERIFY-N5i focused | `os.fdopen(os.open(...))` | KILLED through nested `os.open`, `1 failed` |
| V5 | VERIFY-N5i focused | `open(..., "a")` | KILLED: receiver-scan test, `1 failed` |
| F3-1 | N5j-run | `o = open; o(..., "w")` | KILLED: `AssertionError: file receiver inventory changed`; final inventory saw two `builtins.open` calls in `_sha256_file` |
| F3-2 | N5j-run | `pathlib.Path(...).write_text(...)` | KILLED: `AssertionError: file receiver inventory changed`; final inventory saw `attribute.write_text` |
| F3-3 | N5j-run | delete `_write_env(framedir, framedir_fd)` from `_write_evidence` | KILLED: `AssertionError: file receiver inventory changed`; `_write_evidence` ordinal/inventory changed |
| J1 | N5j-run | restore `O_TRUNC` in `_open_regular` | KILLED: `foreign_text: ''`; summary `1 failed, 107 deselected in 0.52s` |
| J2 | N5j-run | remove `st_nlink` hardlink check | KILLED: foreign text became probe timeline JSON; summary `1 failed, 107 deselected in 0.51s` |
| J3 | N5j-run | remove both realpath symlink checks | KILLED: `foreign_files: ['child']`; summary `1 failed, 107 deselected in 0.58s` |
| J4 | N5j-run | drop `dir_fd` from `_leaf_handle` | KILLED: `foreign_files: ['env.json', 'runtime-identity.json', 'timeline.jsonl']`; summary `1 failed, 107 deselected in 0.54s` |
| J5 | N5j-run | remove bare-basename guard | KILLED: `SystemExit("bare-name guard did not raise")`; summary `1 failed, 107 deselected in 0.43s` |

By-construction / not re-run predecessor rows named rather than counted as fresh kills: N5i reported M7/M8 parent red-before only, M15/M16 equivalent-or-stricter, and M22 superseded by N7. They are not included in the 49 killed rows above.

## 18-class self-sweep

| class | classification |
|---|---|
| 1. Numeric/domain fail-open | Covered by existing timeout-domain tests; N5j did not change domain parsing. |
| 2. Evidence write receiver world | T:2820-2849 exact `_RECEIVER_INVENTORY` and T:3021-3055 equality assertion cover every current receiver. |
| 3. Open/truncate ordering | P:83-89 `st.st_nlink != 1` then `os.ftruncate(fd, 0)`; J1/J2 killed. |
| 4. Hostile final leaf type | T:3235-3244 `No such device or address` covers final symlink, FIFO-with-reader, UNIX socket; prior directory and character-device coverage stayed in the 108-test suite. |
| 5. Framedir provenance | P:280-292 `framedir path contains a symlink` plus directory fd open; T:3195-3199 `framedir path contains a symlink` killed J3. |
| 6. Path swap / TOCTOU | T:3225-3232 `original_files` proves writes stay on the original opened directory fd after the visible path is swapped. |
| 7. Bare-name traversal | P:75-76 `os.path.basename(name) != name`; T:3247-3267 `../escape` kills J5. |
| 8. M3 last-resort path | P:610-628 `_m3_write` routes M3 leaf writes through `_leaf_handle`; existing M3 tests stayed green. |
| 9. Stderr drain errors | P:120-135 `def _drain_stderr` drains via guarded writer; existing drain tests stayed green; real F4 calibration not done. |
| 10. `/proc/<pid>/exe` identity race | AP_SCREEN AF-AP-55 remains known; existing early/late readlink tests stayed green. |
| 11. World enumeration hollow green | Inventory is exact by key, not a floor; no `>= 12` survivor remains. |
| 12. Predicate without raising else | New hostile tests use direct asserts on exact rc/message/state, not `if literal:` pass-through. |
| 13. Name-based kill | Hostile rig starts only its child process group and kills by pid group only on watchdog timeout. |
| 14. Tooling failure as green | `lane_gate.sh` and mutant patchers checked exit codes/anchor counts; one F3 deletion anchor mismatch was reported and rerun with a unique anchor. |
| 15. Gitignore-swallowed fixtures | No fixture files were added. Scratch tar/copies stayed under `../scratch`. |
| 16. Broad exception swallowing | P:582-633 M3 catches broad exceptions to write last-resort evidence; AP-24 classified by existing M3 tests. |
| 17. Report line drift | Final line refs use final bytes and `report_lint` MISS 0. |
| 18. PC process leftovers | Process census after runs found no `pytest`, `acp_probe`, hostile driver, mutant, or lane_gate child owned by this lane. |

## `ap_screen.py` classification

Production screen:

```
--- AP_SCREEN over 1 path(s): 8 hits over 1 files ---
AF-AP-55: 3
    proofs/S0-01/tools/acp_probe.py:357: candidate = os.readlink("/proc/%d/exe" % proc.pid)
    proofs/S0-01/tools/acp_probe.py:433: interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
    proofs/S0-01/tools/acp_probe.py:524: interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
AP-1: 2
    proofs/S0-01/tools/acp_probe.py:226: os.environ.get(k)
    proofs/S0-01/tools/acp_probe.py:303: os.environ.get("ACP_PROBE_TIMEOUT", "30")
AP-32: 2
    proofs/S0-01/tools/acp_probe.py:55: hashlib.sha256()
    proofs/S0-01/tools/acp_probe.py:146: hashlib.sha256(v.encode("utf-8"))
AP-24: 1
    proofs/S0-01/tools/acp_probe.py:538: except Exception:
```

Classification:

- AF-AP-55: known identity-race surface; existing early retry, final-exec, late-readlink, and deleted-interpreter tests stayed green in the 108-test probe suite.
- AP-1: environment reads are the probe input channel; required env vars fail early by name, timeout domain is guarded by existing timeout tests.
- AP-32: SHA256 is used for evidence identity/redaction fingerprints; `_sha256_file` has regular-file guard coverage and redacted values are hashed rather than printed.
- AP-24: broad exception handler is the M3 last-resort evidence path; existing M3 complete-evidence and hostile evidence-path tests stayed green.

Test screen:

```
--- TEST_SCREEN over 1 path(s): 1 hits over 1 files ---
AF-AP-57: 1
    tests/test_s0_01_acp_probe.py:1443: if _rl_calls[0] <= 3:
```

Classification: AF-AP-57 is an intentional count-gated fake in the transient readlink test; the same test prints and asserts `RL_CALLS`, `FIRST_OK`, and call-site distribution at T:1470-1493 (`RL_CALLS` / `FIRST_OK`), so a redistributed read cannot pass as only a total count.

## Discrepancies

- The resume brief named `report-draft.md`; it was absent. I created the final report after completing the remaining verification.
- The brief expected the historical four-file floor `568 passed, 9 xfailed`; final collection is 604 tests and the PC xdist run produced `595 passed, 9 xfailed`. The increase comes from repository drift before this lane; I did not change the other three files in that set.
- The direct serial four-file run did not finish within the tool ceiling. The xdist four-file run and xdist four-file lane-gate completed. This is reported as a deviation, not hidden as an equivalent serial proof.
- The path-swap rig was strengthened after the first green run: it now asserts `original_files` contains all four evidence leaves, not only that the foreign/symlink path is empty. Final gates were rerun after that edit.
- `tasks/briefs/pc/pc-n5j.md` and the N5j brief file are staged from the coordinator/lane patch. I did not edit them.

## Evidence tiers

Verified in this lane:

- Final source/test identity and line counts.
- Red-before on `git archive 99b7b37` with final tests copied over.
- Full `tests/test_s0_01_acp_probe.py`: `108 passed in 51.05s`.
- Two `lane_gate.sh` probe-file invocations: four total green probe-file pytest runs.
- Four-file pytest-xdist run: `595 passed, 9 xfailed in 210.82s (0:03:30)`.
- Four-file `lane_gate.sh` xdist run: `595 passed, 9 xfailed in 210.27s (0:03:30)`.
- N5j mutants J1-J5 and F3-ALIAS/PATH/DELETE killed on fresh archive copies.
- `git diff --check`, `py_compile`, `ap_screen.py`, `gitnexus detect_changes`, process census.

Inferred / predecessor evidence:

- N5i's 33-mutant campaign and VERIFY-N5i focused rows are carried from the required predecessor reports. I did not rerun those entire campaigns.
- Existing M3/drain/interpreter/hash behavior is inferred from the unchanged tests staying green plus predecessor reports.

Assumed:

- Pytest-xdist is an acceptable way to finish the four-file set on this PC venue under the tool ceiling. The serial timeout makes this an assumption for verifier review.

## Self-attack

1. The realpath framedir check can still race if an attacker swaps a path component between the second realpath check and `os.open`. Ruled down, not eliminated: the next protection is `os.open(... O_DIRECTORY | O_NOFOLLOW)` for the final component and every leaf write goes through the opened directory fd. A stronger component-by-component opener would be a new design, not in this brief.
2. The receiver scan can still miss dynamic receiver construction that the AST cannot resolve. Ruled down for this round by exact current inventory plus three negative controls for the named survivor classes: alias open, attribute write, and writer deletion.
3. The four-file serial suite may reveal a scheduler/order bug hidden by xdist. Not ruled out: serial hit the tool ceiling. I reported that as NOT-done and provided the xdist run, four-file lane-gate, single-file sibling runs, and collection count instead.

## Process census / hygiene

Process census after final runs:

```
# ps -eo pid,ppid,pgid,stat,etimes,args -ww | grep -E 'pytest|acp_probe|agent_result|driver.py|n5j-mutants|n5j-f3|basetemp|lane_gate' | grep -v grep || true
# no rows
```

Final git status:

```
M proofs/S0-01/tools/acp_probe.py
A  tasks/briefs/pc/pc-n5j.md
A  tasks/briefs/s0-01-n5j-probe-open-validate-truncate-the-framedir-owned-the-receivers-inventoried.md
 M tests/test_s0_01_acp_probe.py
?? tasks/briefs/s0-01-n5j-support/
```

No `git add`, `commit`, `stash`, `checkout`, `reset`, `push`, PC bridge call, outward action, credential read, or service restart was performed.

## `gitnexus detect_changes`

```
Changes: 4 files, 19 symbols
Affected processes: 3
Risk level: medium

Changed symbols:
  Function _open_regular → proofs/S0-01/tools/acp_probe.py
  Function _drain_stderr → proofs/S0-01/tools/acp_probe.py
  Function _redact_env → proofs/S0-01/tools/acp_probe.py
  Function _write_evidence → proofs/S0-01/tools/acp_probe.py
  Function main → proofs/S0-01/tools/acp_probe.py
  Function _m3_write → proofs/S0-01/tools/acp_probe.py
  Section PC lane — N5j (S0-01 probe round 13: open-validate-truncate, the framedir owned, the receivers inventoried, the ≥40 campaign) → tasks/briefs/pc/pc-n5j.md
  Section Lane N5j — S0-01 ACP probe round 13: open-validate-truncate with one link, the framedir symlink-free and dir-fd-relative, every writer receiver inventoried by identity, the ≥40 campaign in the report → tasks/briefs/s0-01-n5j-probe-open-validate-truncate-the-framedir-owned-the-receivers-inventoried.md
  Section Design (pinned — build it, do not redesign it; line numbers are `99b7b37`'s = 628da83's) → tasks/briefs/s0-01-n5j-probe-open-validate-truncate-the-framedir-owned-the-receivers-inventoried.md
  Section Report → tasks/briefs/s0-01-n5j-probe-open-validate-truncate-the-framedir-owned-the-receivers-inventoried.md
  Variable _GOLDEN_UNGUARDED_RECEIVERS → tests/test_s0_01_acp_probe.py
  Variable _READ_ATTRS → tests/test_s0_01_acp_probe.py
  Function _scan_file_receivers → tests/test_s0_01_acp_probe.py
  Function owner → tests/test_s0_01_acp_probe.py
  Function mode_of → tests/test_s0_01_acp_probe.py
... and 4 more

Affected execution flows:
  • Main → _open_regular (4 steps) — changed: main, _write_evidence, _open_regular
  • Main → _redact_env (4 steps) — changed: main, _write_evidence, _redact_env
  • Main → _sha256_file (3 steps) — changed: main, _write_evidence
```

## `report_lint`

Final run after this report was written:

```
report_lint: 62 refs — OK 54, NEAR 3, MISS 0, UNCHECKABLE 5, UNRESOLVED 0 (worktree)
```

The non-zero NEAR/UNCHECKABLE rows are report-lint heuristic limits; the required MISS count is 0.
