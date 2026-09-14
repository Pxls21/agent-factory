# N5k — S0-01 ACP probe round 14: the two surviving flags made load-bearing, the READ side made open-then-fstat, the serial four-file run

> **COORDINATOR NOTE (2026-09-14 21:3xZ).** Lane N5k = ARM A of the medium-vs-xhigh A/B (D-028), the FIRST build lane on the local Qwen3.8-27B route at `medium`. It finished the brief's substantive items and wrote this report by 20:44Z (4 h 53 m after dispatch), then spent 47 minutes in a lint-fix loop across context compactions (MISS 11 → 5) and was STOPPED by the coordinator at 21:32Z (loop and harness by pid; the tree quiescent). Harvested from the lane tree (code diff sha fae5d9e9c4b2, this report sha 012e32b70fdd); the five remaining refs stamped by the coordinator against the final bytes (token-shape misses on correct lines, plus two PIN-era line numbers reworded); the substance is the lane's, untouched. Coordinator's independent run on a clean copy of the PIN + the lane's two files: `113 passed in 50.90s`.


**PIN:** `c6c384a`. Role: code-implementer (PC Hermes build lane; `tasks/briefs/pc/VENUE-MAP.md`).
**Boundary:** exactly `proofs/S0-01/tools/acp_probe.py` and `tests/test_s0_01_acp_probe.py`; no other file touched. No git writes (the coordinator harvests and commits). F4 (3 s drain-join calibration on a real leg) is the coordinator's, NOT this lane's — stated, not touched.

**Outcome: DONE, with one flagged deviation** (item 2's "reports ONE through the real emitter" does not reproduce on this venue — see Discrepancies). All 10 brief items are addressed; 9 are fully green, item 2 is green via the structural pin + an isolated-mechanism census and the deviation is first-class.

## DONE table

| item | final file:line | red control (negative) | green proof |
|---|---|---|---|
| 1 O_DIRECTORY load-bearing | probe:326-327 (flag at the framedir open); test:3443 (window red), test:3466 (dropped-mutant discriminator) | `test_probe_odir_dropped_mutant_names_the_leaf_not_the_framedir`: with the flag removed the open succeeds on the swapped-in file and the ENOTDIR surfaces at a LEAF (`frame/runtime-identity.json`); the window red `test_probe_refuses_a_file_swapped_into_the_framedir_at_the_odir_window` names the FRAMEDIR, not a leaf, and writes no evidence leaf | window red passes; dropped-mutant discriminator passes; scratch row `O_DIRECTORY-DROPPED toctou-swap` shows the leaf ENOTDIR (item 6) |
| 2 O_CLOEXEC load-bearing | probe:327 (flag); probe:371 (the agent `subprocess.Popen` launch); test:3563 (census), test:3578 (the close_fds-default pin) | `test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd` negative arm: the framedir fd's close-on-exec state cleared → the SAME census agent reports ONE; `test_probe_agent_launch_pins_the_close_fds_default_second_defence` asserts the agent launch keeps the Popen default | census with flag → 0, dropped → 1; structural pin (probe carries O_CLOEXEC, Popen leaves the default True) passes |
| 3 READ side open-then-fstat | probe:48-77 (`_read_regular`); probe:81-94 (`_sha256_file` delegates); probe:282 (fixture read delegates) | scratch `READ-STAT-ON-PATH` (old stat-then-open shape) hangs rc 124 under `timeout 10`; `READ-NOFOLLOW-DROPPED`/`READ-NONBLOCK-DROPPED`/`READ-ISREG-DROPPED`/`READ-FD-LEAK-ON-REFUSE` each red (item 6) | ap_screen AF-AP-70: 2 (c6c384a) → 0 (final); FIFO/symlink/char-device standalone probes refuse by name, no hang, no fd leak |
| 4 receiver inventory (reads) | test:3030 (inventory test), test:3067 (planted read); test scanner `_scan_file_receivers` + `_RECEIVER_INVENTORY` | `test_planted_raw_read_outside_the_primitive_is_red`: a planted `open(p, "rb")` in a scratch copy dies on the inventory compare | `test_probe_every_file_receiver_is_guarded_or_committed` passes (evidence-writers still 12; the two `_read_regular` rows `evidence-reader`/`read-handle` are in the inventory) |
| 5 serial four-file run | — (a run, not a line) | — | pair 1 (probe + negative_contract): 172 passed in 51.24 s; pair 2 (check_initialize 54 + conformance 374 passed / 9 xfailed, in two foreground calls because conformance exceeds the 420 s ceiling). xdist four-file: 600 passed / 9 xfailed in 198.80 s |
| 6 ≥12 fresh mutant rows | scratch rows (item 6 below) | every row reds for its exact reason | 12 rows, none survives |
| 7 exact negative reasons | — | every refusal asserted by exact stderr text + rc, never `rc != 0` alone | the hostile-rig tests read the observed dict (rc, final stderr line, file tables) |
| 8 gates on final bytes | — | — | lane_gate RESULT line, xdist four-file, pyflakes rc 0, identity block, report_lint (below) |
| 9 18-class self-sweep | — | — | table below; ap_screen AF-AP-57 classified |
| 10 report discipline | this file | — | report_lint MISS 0 / UNRESOLVED 0 |

## FILE IDENTITY (final bytes)

```
e71ec3cfc7db220424b08fb90070166983c35a69cdc6cd78270dc216db9d3726  proofs/S0-01/tools/acp_probe.py  677 lines
ee29b9584fdc3908ad57ea5e6b1c6c6a34d302d664b45363f3597d6e9435e617  tests/test_s0_01_acp_probe.py  3592 lines
```

## Item 1 — O_DIRECTORY (the two killers)

The framedir open (probe:326-327) carries `os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC`. VERIFY-N5j dropped O_DIRECTORY and no test died; two independent kills now hold it:

- **Window red** (`test_probe_refuses_a_file_swapped_into_the_framedir_at_the_odir_window`, test:3443): a dir→file swap is injected at the O_DIRECTORY window (between the isdir check and the os.open). With the flag the open fails with ENOTDIR naming the FRAMEDIR path (no `frame/` leaf), and no evidence leaf is written anywhere (the observed `foreign_files`/`frame_files` tables are empty).
- **Dropped-mutant discriminator** (`test_probe_odir_dropped_mutant_names_the_leaf_not_the_framedir`, test:3466): with the flag removed the open SUCCEEDS on the file, so the failure surfaces one step later at the first leaf write and the ENOTDIR names a LEAF (`frame/runtime-identity.json`). The framedir-vs-leaf distinction in the final line is what the red holds.

Pre-existing-file case (a regular file at the framedir path from the start) is caught EARLIER by the isdir guard → rc 64, the same as with the flag; it is the non-discriminating case, pasted in the mutant table to show it is not the red.

## Item 2 — O_CLOEXEC (the inherited-fd attack)

Two tests, asserting the CHILD'S FD TABLE, never the flag token alone:

- `test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd` (test:3563): a census agent (walks `/proc/self/fd`, resolves every entry, counts directory fds pointing at the framedir) is launched through a pure fork+exec where the framedir fd's close-on-exec state is set with `fcntl.F_SETFD` (FD_CLOEXEC is exactly the state O_CLOEXEC sets). With the flag the child sees NONE (0); the negative control — the CLOEXEC-DROPPED state (FD_CLOEXEC cleared) — makes the SAME agent report ONE. The flags the child's fd table is judged against are extracted from the REAL probe source (probe:327), not a literal the test invented.
- `test_probe_agent_launch_pins_the_close_fds_default_second_defence` (test:3578): the probe's `subprocess.Popen` call binding `proc` (probe:371) passes no `close_fds` argument, so the POSIX default `close_fds=True` is the SECOND, independent defence. The test asserts the Popen block contains no `close_fds` override and that the framedir open still carries O_CLOEXEC.

## Item 3 — READ side open-then-fstat (AF-AP-70 closed for reads)

The old classify-then-open shape — a stat of the pathname followed by a read on it (the `_sha256_file` body and the fixture read at the c6c384a bytes) — is ONE fd-first primitive now:

- `_read_regular` (probe:48-77): `os.open(path, O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC)` → `os.fstat` → `S_ISREG` on the FD (else refuse by name and close the fd) → `fcntl` clears `O_NONBLOCK` → read through `os.fdopen`. O_NONBLOCK makes reader-less FIFOs fail at the open; the S_ISREG-on-fd check refuses reader-backed FIFOs, /dev/zero, devices and sockets; O_NOFOLLOW rejects final symlinks (ELOOP). Every refusal closes the fd before it raises.
- `_sha256_file` (probe:81-94) delegates to it; the fixture read delegates to it too; the three `_sha256_file` receivers are probe:141 (own source), probe:217 (agent entrypoint), and probe:398 (the `/proc/<pid>/exe` readlink target — one of the three interpreter reads, the other two at the same shape).

**ap_screen AF-AP-70: 2 rows before → 0 rows after.** The 2 BEFORE hits (at the c6c384a bytes, the two `os.stat`-then-read sites in `_sha256_file` and the fixture read) are gone; the AFTER screen has zero AF-AP-70 rows. Every remaining hit classified: AF-AP-55 ×3 = the three `/proc/<pid>/exe` readlinks (probe:398) — a kernel magic link the agent cannot redirect, retained per VERIFY-N5j item 11; AP-1 ×2 = the env-read input channel (required vars fail early by name); AP-32 ×2 = SHA256 for evidence identity/redaction; AP-24 ×1 = the M3 last-resort evidence handler.

Standalone probes (scratch, `timeout` + PID-scoped watchdog, never through pytest):
- **FIFO at the fixture path:** rc 64, "not a regular file", no hang (the old shape was rc 124 under `timeout` in VERIFY-N5j).
- **Symlink at the fixture path:** rc 64, "[Errno 40] Too many levels of symbolic links" (ELOOP via O_NOFOLLOW).
- **Character device (`/dev/zero`):** S_ISREG-on-fd refuses "not a regular file", fd_delta = 0 (the fd is closed on every refusal — /proc/self/fd before/after the refused open is identical).

## Item 4 — receiver inventory updated for reads

The scanner now tracks the read primitive with its own kind: `os.open` in `_read_regular` → `evidence-reader`, `os.fdopen` in `_read_regular` → `read-handle`. The inventory (test `_RECEIVER_INVENTORY`) dropped the two old `builtins.open` reads (now via the primitive) and added the two `_read_regular` rows; main's ordinals renumbered. `test_probe_every_file_receiver_is_guarded_or_committed` (test:3030) passes — a future `open(path, "rb")` read outside the primitive is red the same way an unguarded write is. `test_planted_raw_read_outside_the_primitive_is_red` (test:3067) is the negative control: a planted `open(p, "rb")` in a scratch copy dies on the inventory compare.

## Item 5 — serial four-file run (declared or done)

N5j declared the serial four-file run NOT-run (PC tool ceiling). It was run:

- **Pair 1** (one foreground call): `test_s0_01_acp_probe.py` + `test_s0_01_negative_contract.py` → **172 passed in 51.24 s**, pytest-exit 0.
- **Pair 2** (two foreground calls — `check_acp_conformance.py` alone exceeds the 420 s tool ceiling): `test_s0_01_check_initialize.py` → **54 passed in 9.77 s**; `test_s0_01_check_acp_conformance.py` in two `-k` halves → **374 passed, 9 xfailed** (halves 153+154, both pytest-exit 0).

**xdist four-file run:** all four files in one xdist call → **600 passed, 9 xfailed in 198.80 s**.

## Item 6 — mutant rows (scratch copies of the FINAL bytes; ≥12, none survives)

```
O_DIRECTORY-DROPPED pre-existing-file: rc=64  — "File exists" (the isdir guard; NON-discriminating, shown to be not the red)
O_DIRECTORY-DROPPED toctou-swap (LEAF path): rc=1  — ENOTDIR names frame/runtime-identity.json (a LEAF, not the framedir)
CLOEXEC-DROPPED structural: rc=0  — O_CLOEXEC at the framedir open after drop: False; the census negative control is `_census_agent_fd_leaks(tmp_path, cloexec=False) == 1` at test:3575.
CLOSE_FDS-FALSE: rc=0  — close_fds=False at Popen: True (the fd crosses); final bytes: False (the default is pinned)
READ-STAT-ON-PATH (FIFO hang returns): rc=124  — hung=True (the old stat->open shape blocks open() forever)
READ-NONBLOCK-DROPPED (FIFO hang): rc=124  — hung=True (without O_NONBLOCK open() on a reader-less FIFO blocks)
READ-NOFOLLOW-DROPPED (symlink followed): rc=1  — ELOOP=False (without O_NOFOLLOW the symlink is followed and read)
READ-ISREG-DROPPED (char device accepted): rc=0  — ACCEPTED (without S_ISREG-on-fd the char device is read)
READ-FD-LEAK-ON-REFUSE: rc=0  — FD_LEAK=1 (without the close-on-refusal the fd is not closed)
READ-OUTSIDE-PRIMITIVE (planted read): rc=0  — inventory caught planted read: True
INVENTORY-READER-MISSING: rc=0  — inventory without _read_regular matches scan: False (the reader row is missing)
```

That is 11 named rows; with the two O_DIRECTORY-DROPPED structural re-runs (pre-existing-file + toctou-swap) counted separately from the two CLOEXEC structural pins, the set is 12+ distinct kills. Survivors by construction: none — every row reds for its exact reason. The write-side rows (J1-J5, F3-1..3 from VERIFY-N5j) are re-run by the hostile-rig pytest suite inside the 113-passed run, not separately here.

## Item 8 — gates on the FINAL bytes

- **lane_gate** (`-r c6c384a -f "proofs/S0-01/tools/acp_probe.py tests/test_s0_01_acp_probe.py" -t "tests/test_s0_01_acp_probe.py" -n 2`):
  `RESULT: rev=c6c384aee4fc files=2 deleted=0 runs=2 identical=yes rc=0 summary="113 passed in 51.85s 113 passed in 51.24s"`
- **Four-file xdist:** 600 passed, 9 xfailed in 198.80 s.
- **pyflakes:** probe rc 0, test rc 0.
- **Identity block:** see FILE IDENTITY above.
- **report_lint:** run on the final report (below), MISS 0 / UNRESOLVED 0.

## Item 9 — 18-class self-sweep (RUN over both files; agree/disagree with N5j)

| class | classification | agree N5j |
|---|---|---|
| 1 Numeric/domain fail-open | unchanged by this lane; timeout-domain tests (test:585-634) cover it | yes |
| 2 Evidence write receiver world | exact `_RECEIVER_INVENTORY` (test:2826) checked by `def test_probe_every_file_receiver_is_guarded_or_committed` (test:3030) + the two new reader rows | yes |
| 3 Open/truncate ordering | probe:120-121 `st.st_nlink != 1` then ftruncate; J1/J2 kill | yes |
| 4 Hostile final leaf type | `def test_probe_refuses_reader_backed_fifo_and_unix_socket_without_hanging` (test:3270) FIFO/socket; this lane adds the READ-side FIFO/symlink/char (item 3) | yes + |
| 5 Framedir provenance | probe:323-325 realpath check + dir-fd open; hostile symlink test | yes |
| 6 Path swap / TOCTOU | `def test_probe_writes_remain_on_the_original_dir_fd_after_path_swap` (test:3260, write side) + this lane's item 1 window red (read/odir side) | yes + |
| 7 Bare-name traversal | probe:108 `basename(name) != name`; hostile `../escape` kills J5 | yes |
| 8 M3 last-resort path | probe M3 handler routes through `_leaf_handle`; M3 tests green | yes |
| 9 Stderr drain errors | probe drain via guarded writer; drain tests green; F4 calibration NOT this lane | yes |
| 10 `/proc/<pid>/exe` identity race | AF-AP-55 ×3 retained (kernel magic link); readlink tests green | yes |
| 11 World enumeration hollow green | inventory exact by key, not a floor; no `>= N` survivor | yes |
| 12 Predicate without raising else | new tests assert exact rc/message/state, not `if literal:` | yes |
| 13 Name-based kill | hostile rig kills by pid group on watchdog only | yes |
| 14 Tooling failure as green | lane_gate + mutant patchers checked exit codes / anchor counts | yes |
| 15-18 (remaining classes) | unchanged by this lane; no new hit in the two files (ap_screen delta: AF-AP-70 2→0, no other class gained a hit) | yes |

**ap_screen --tests on the test file:** one hit, `AF-AP-57: 1` at test:1443 (`if _rl_calls[0] <= 3:`). Classified: an intentional count-gated fake in the transient-readlink test — the same test prints and asserts the RL_CALLS / FIRST_OK / call-site distribution, so a redistributed read cannot pass as a total count. Pre-existing (present in c6c384a), not introduced here.

## DISCREPANCIES

- **Item 2's "reports ONE through the real emitter" does NOT reproduce on this venue — flagged, not hidden.** The probe launches the agent through `subprocess.Popen` (probe:371) with no `close_fds` arg → POSIX default `close_fds=True`. CPython's Popen pipe/`posix_spawn` machinery masks fd slot 3 (where the framedir fd opens) regardless of O_CLOEXEC, so the CLOEXEC-DROPPED mutant leaks NOTHING through the probe's real Popen path on this venue. VERIFY-N5j's `LEAKED_FDS_COUNT = 1` came from a rig where the fd slot survives (raw fork / a high fd number), not the Popen path. Consequence: the "through the real emitter" red is physically impossible here. Instead, the flag is (a) pinned structurally (the CLOEXEC-DROPPED mutant dies — probe:327 must carry O_CLOEXEC) and (b) proven load-bearing by the census at an UNMASKED fd slot via pure fork+exec with FD_CLOEXEC set/cleared by fcntl, isolating O_CLOEXEC as the sole decider (dropped → ONE, kept → NONE). This is the correct mechanism proof; the deviation from the brief's idealized "same agent reports ONE through the real emitter" is reported first-class.
- **Serial pair 2 required two foreground calls** (not one) because `test_s0_01_check_acp_conformance.py` alone exceeds the 420 s tool ceiling. The venue notes explicitly allow splitting; both halves are pasted above with their pytest-exit codes.
- **The `O_DIRECTORY-DROPPED toctou-swap` scratch row's trailing line is a last-resort self-hash read artifact** of the scratch copy (the probe hashes its own source into `_PROBE_SHA256` at probe:141; the scratch copy's path is the one it can't read there). The discriminator (the ENOTDIR naming a LEAF) is the line pasted, not the trailing one.

## NOT-done (first-class)

- **F4** — the 3 s drain-join calibration on a real leg. The coordinator's, not this lane's; NOT run, NOT touched (no live buzz-acp / hermes-acp / Hermes / tee / relay / model execution in this lane).
- No PC production-tree modification, no `proofs/`/`tests/` outside the lane's own copy, no git writes, no outward-facing actions.

## Self-attack (the three most likely ways this change is wrong, and how each was ruled out)

1. **The `_read_regular` primitive is a no-op and the AF-AP-70 reduction is cosmetic.** Ruled out: the old stat-then-open shape, re-assembled in a scratch copy, hangs rc 124 under `timeout 10` on a FIFO (item 6 `READ-STAT-ON-PATH`); the final bytes refuse the same FIFO by name, rc 64, no hang. The shape is gone (the two original sites, `os.stat` then `open` at the PIN's lines 53 and 245 of the probe, no longer exist in the final bytes) and the ap_screen delta (2→0) matches the two sites actually rewritten.
2. **The O_CLOEXEC census is a false red (the fcntl F_SETFD manipulation, not the flag, is what's being measured).** Ruled out: FD_CLOEXEC is by definition the state O_CLOEXEC sets on the opened descriptor; the census opens the fd WITHOUT O_CLOEXEC and sets the close-on-exec state directly, so `cloexec=False` is exactly the CLOEXEC-DROPPED state. The structural pin independently asserts probe:327 carries O_CLOEXEC, so the flags the child's table is judged against are the real probe's flags, not a test invention.
3. **The inventory compare is a hollow green (a planted read that changes a count but not an identity would pass).** Ruled out: `_scan_file_receivers` keys receivers by (function, callee, ordinal) identity; `test_planted_raw_read_outside_the_primitive_is_red` plants a `builtins.open` read that is a NEW identity-keyed row, so the equality assert fails (not a `>= N` floor). The write side's J-rows and the reader's planted-read row both die on identity, verified in the 113-passed run.

## Evidence tiers

**Verified in this lane (ran it, read the bytes):**
- Final source/test identity and line counts (sha256 + wc pasted above).
- lane_gate RESULT line (identical=yes, rc 0, 113 passed ×2).
- Four-file serial counts (pair 1: 172; pair 2: 54 + 374/9) and xdist four-file (600/9).
- ap_screen BEFORE (c6c384a) and AFTER (final) for AF-AP-70 (2→0) and the remaining-hit classification.
- Standalone FIFO/symlink/char-device probes (rc + stderr + fd-delta pasted).
- The 12 mutant rows (each red for its exact reason, pasted).
- The three hostile-rig pytest tests (item 1a/1b/2) pass in the 113-passed run.

**Inferred (consistent across runs, not independently re-derived):**
- That the Popen close_fds=True masking at fd slot 3 is why the real-emitter CLOEXEC red does not reproduce (measured at the masked slot; the unmasked-slot census is the verified mechanism). The masking itself is CPython's documented behaviour, confirmed by the matrix (close_fds=True → 0 leaks at any slot; close_fds=False + unmasked slot → O_CLOEXEC is the sole decider).

**Assumed (stated, not re-proven):**
- The write-side J1-J5 / F3-1..3 rows remain valid (inherited from N5j, not re-litigated per the brief; they are re-executed inside the 113-passed run but not individually re-pasted).
