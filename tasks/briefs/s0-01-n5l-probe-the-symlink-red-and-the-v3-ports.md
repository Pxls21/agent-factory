# Lane N5l — S0-01 ACP probe round 15: VERIFY-N5k's F1 closed with a BEHAVIORAL final-symlink red (the O_NOFOLLOW drop killed), arm B v3's stronger read-primitive tests and its real-emitter census PORTED (not its comment-defeatable pin), `close_fds=True` made explicit under a scoped pin (build lane: PC Hermes `code-implementer` on the LOCAL route at `medium`, D-028; sandbox fallback `code-implementer`)

PIN: `97bb0c0` (the probe and its test are byte-identical to round 14's landing b9b6134: `proofs/S0-01/tools/acp_probe.py` 677 lines sha
`e71ec3cf…`, `tests/test_s0_01_acp_probe.py` 3592 lines sha `ee29b958…` — re-derive both with `sha256sum` + `wc -l` at the PIN and paste
them as your FILE IDENTITY block).

**Authorization + provenance.** The findings are VERIFY-N5k's (`tasks/briefs/s0-01-n5j-support/VERIFY-N5k-report.md`, in your tree — the
comparative grade of arm A (the landed bytes) against arm B v3 (`N5k-xhigh-v3.diff`, also in your tree, NOT landed): F1 BLOCKING — removing
`os.O_NOFOLLOW` from the read open at `probe:62` leaves the whole suite green (`113 passed in 52.01 s`) while `_read_regular` follows a final
symlink to a regular file and returns its content; F2 — no real-emitter fd census on arm A (the isolated census exists, the real `Popen`'s
final bytes are unobserved); F3 — v3's `close_fds=True` pin is a FILE-WIDE substring assertion that a comment satisfies (do NOT port it as
written). All three were MEASURED by the verifier on the landed bytes; take them as settled facts and build. The pack
`tasks/briefs/s0-01-n5l-support/N5l-pack.md` (skeletons, the graft ask, GitNexus impact, crg, ripwire, the registry screen over the two files)
is in your tree — START FROM IT (CODE INTEL FIRST). Boundary: `proofs/S0-01/tools/acp_probe.py` (probe), `tests/test_s0_01_acp_probe.py`
(test), `tasks/briefs/s0-01-n5l-support/mutants.sh` (D, new), `tasks/briefs/s0-01-n5l-support/N5l-report.md`. Everything else read-only.

## Items (build in order; every item = code + a deterministic LLM-free test + a pasted line)
1. **F1 — the behavioral final-symlink red.** A test that creates a REGULAR file with known content, a symlink to it at the FINAL path
   component, and calls `_read_regular(symlink)`: the call must raise `OSError` with `ELOOP` (`errno.ELOOP`; assert the errno, not a substring)
   and never return the content; a second case through the real caller chain (whichever probe function reads a leaf through `_read_regular` —
   find it in the pack) with the same symlink plant must produce the probe's named refusal at the outer boundary (the exact stderr line or
   `probe_error`, pasted). Then port v3's source-mutant guard `test_probe_read_primitive_mutants_die_at_the_open_level` (v3diff line ~401)
   adapted to `_read_regular`: it must be a BEHAVIORAL rig (it mutates a scratch copy of the primitive and observes the symlink read), never a
   substring pin on the source. The driver row `READ_NOFOLLOW_DROP` (item 5) must now be KILLED by the ELOOP test with a pasted assertion line.
2. **The v3 read-primitive ports (adapted to `_read_regular`):** v3's regular-read success test (v3diff ~344), the parametrized named
   non-regular refusals (v3diff ~356: FIFO, directory, `/dev/zero`, socket — each with the EXACT refusal text asserted), and the no-fd-leak-on-
   refusal test (v3diff ~386: the fd table before/after, `fd_delta == 0`). Keep arm A's helper name and fixtures; cite each ported test's v3 origin
   in its docstring.
3. **F2 — the real-emitter census.** Port v3's `test_probe_census_agent_sees_no_framedir_fd_on_final_bytes` (v3diff ~523) adapted to arm A's
   fixtures: the REAL `Popen` launch of the agent, the child's fd table read at the moment the final bytes are written, `CENSUS=0` on the landed
   bytes; the driver's `FD_LEAK_TRIPLE` row (`set_inheritable` + `close_fds=False` + the CLOEXEC drop, the verifier's measured leak shape) must
   give `CENSUS=1` and RED this test (pasted). Keep arm A's isolated F_SETFD control (v3's isolated control is redundant — skip it).
4. **`close_fds=True` explicit, under a SCOPED pin (F3 done right).** Make `close_fds=True` explicit at the real `Popen`; replace arm A's
   absence-only pin (`test_probe_agent_launch_pins_the_close_fds_default_second_defence`) with an AST pin on THAT `Popen` call's keywords:
   `close_fds` absent or `True` passes, `close_fds=False` fails — a comment containing `close_fds=True` anywhere must NOT satisfy it (write the
   comment mutant as a driver row `CLOSE_FDS_COMMENT_ONLY` → the pin stays RED; and `CLOSE_FDS_FALSE` → RED). No file-wide `in source` assertion
   anywhere in the new tests (AF-AP-80).
5. **The driver (D) — `tasks/briefs/s0-01-n5l-support/mutants.sh`, AF-AP-78 obeyed:** copy the shape of `tasks/briefs/s0-01-a5l-support/
   mutants.sh` but with `py_compile` on every mutated file and a collect-only pass before the verdict; `INVALID` printed and counted; the summary
   `EXPECTED=<n> KILLED=<k> SURVIVED=<s> INVALID=<i> CONTROL=<c>`, gate on `INVALID=0` and `SURVIVED=0`; every kill line pastes the pytest
   failure (`FAILED …::<test> - <Exception>`). Rows (at least): `READ_NOFOLLOW_DROP` (F1), `READ_NONBLOCK_DROP` (kills through the FIFO
   timeouts — keep the timeout bounded), `READ_SISREG_DROP`, `READ_NO_CLOSE_ON_REFUSAL`, `CLOSE_BEFORE_FSTAT`, `FD_LEAK_TRIPLE`,
   `CLOSE_FDS_FALSE`, `CLOSE_FDS_COMMENT_ONLY`, one CONTROL (a comment-only change → green). ≥ 2 rows of your own on the ported tests.
6. **Gates on the PC (one foreground call each; Hermes's `terminal` tool caps a call at 420 s).** `python -m pytest
   tests/test_s0_01_acp_probe.py -q -p no:cacheprovider --basetemp=<your scratch>` TWICE serial (~52 s each — paste both; the landing floor
   `113 passed` + your new tests), the four-file set (`tests/test_s0_01_acp_probe.py tests/test_s0_01_check_acp_conformance.py
   tests/test_s0_01_pc_tools.py tests/test_s0_01_pc_post_scan.py`) with `-n 8` ONCE (paste; ~3-4 min), the 13-file glob `tests/test_s0_01_*.py
   -n 8` ONCE (paste; ~204 s); beside EVERY count paste `bash scripts/pc_suite.sh set-id -- <the same files>` (no bridge needed). Floors at the
   PIN: the glob `1341 passed, 13 xfailed` (13 files) — state your delta in tests. pyflakes rc 0 on both files. Never background a gate.
7. **Report** at `tasks/briefs/s0-01-n5l-support/N5l-report.md`: FILE IDENTITY before/after, per item the pasted line, the driver's full output +
   summary, the gate lines with set ids, DISCREPANCIES, NOT-done. Lint LAST: `python3 scripts/report_lint.py --map probe=proofs/S0-01/tools/
   acp_probe.py --map test=tests/test_s0_01_acp_probe.py --min-refs 12 <report>`, at most THREE rounds, then paste and finish (AF-AP-76).
8. **Discipline.** `file:line` by `sed -n` at the PIN; hostile FIFO/symlink rigs under your scratch dir with bounded timeouts; kill only what
   you start, by pid; never launch Buzz/ACP/Hermes services; no git writes; the `qwen-builder` unit is YOUR model server — never touch it.
