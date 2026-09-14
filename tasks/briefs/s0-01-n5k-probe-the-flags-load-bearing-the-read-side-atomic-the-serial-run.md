# Lane N5k — S0-01 ACP probe round 14: the two surviving flags made load-bearing by tests, the READ side made open-then-fstat, the serial four-file run (build lane: PC Hermes `code-implementer`; sandbox fallback `code-implementer`)

**PIN: `c6c384a`** (the branch head carrying the four 2026-09-14 landings; the probe and its test are checkpoint 9d's bytes, unchanged since —
`proofs/S0-01/tools/acp_probe.py` 642 lines sha `7874a4e3…`, `tests/test_s0_01_acp_probe.py` 3302 lines sha `9ff359dc…`). Role: code-implementer (the PC
Hermes build lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo agent-factory, branch claude/soundbox-kit-migration-iz1jwf. Boundary:
EXACTLY those two files (fixture agents live INSIDE the test file, as `_run_hostile_probe_rig` does today). Never touch `pins.py`, `conftest.py`, the
checker, the tee, the backend, the PC tools, or their tests. Report at `tasks/briefs/s0-01-n5j-support/N5k-report.md` (drafted after EACH item), returned
whole as the final message. Authorization: the owner's own ACP probe under test — defensive work on their system.

**Inputs (read in this order):** `tasks/briefs/s0-01-n5j-support/VERIFY-N5j-report.md` (the round's contract: the two SURVIVORS O_DIRECTORY-DROPPED and
CLOEXEC-DROPPED, the READ-side finding at item 4 with its trust-boundary ruling, the drain and design items, the fresh mutant rows at item 6) · the
9d checkpoint's commit body (`git show -s fe2dc3b`) · `tasks/briefs/s0-01-n5j-support/N5j-report.md` (the write-side design you inherit — never
re-litigate it) · `docs/INCIDENT-LOG.md` rows AF-AP-70 (classify-then-open by pathname), AF-AP-59, AF-AP-64, AF-AP-65, AF-AP-73 · the preflight
class list of the S0-01 sweeps (every S0-01 brief's): the 18 classes named in the N5j report's self-sweep table.

## Items
1. **O_DIRECTORY made load-bearing (`acp_probe.py:291-292`).** VERIFY-N5j dropped `os.O_DIRECTORY` from the framedir open and no test died. Two
   independent kills: (a) a hostile rig in the shape of `test_probe_writes_remain_on_the_original_dir_fd_after_path_swap` (`test:3225`) where the
   framedir path passes both realpath checks as a directory and is then replaced by a REGULAR FILE before the `os.open` — the probe must exit 1 with
   one exact stderr line naming ENOTDIR / "framedir is not a directory", no leaf written anywhere, the fd table unchanged; (b) the structural flag
   mirror the primitive test already uses for the write flags (`test:3031-3035` pins tokens of `_primitive_source`) extended to the framedir open's
   exact flag set (`O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC`). Paste the mutant (the flag removed) dying under BOTH.
2. **O_CLOEXEC made load-bearing (`:291-292`) — the inherited-fd attack.** VERIFY-N5j's rig measured `LEAKED_FDS_COUNT = 1`: with the flag dropped
   the agent child inherits the open framedir fd — a directory capability handed to the process under test. The red test: a fixture agent (inside
   the test file, launched through the probe like every other fixture agent) that walks its own `/proc/self/fd`, resolves every entry, and reports
   any directory fd pointing at the framedir in its stdout; the test asserts NONE on the final bytes and asserts the SAME agent reports ONE on the
   CLOEXEC-DROPPED mutant (the negative control through the real emitter). Pin `subprocess.Popen(..., close_fds=True)` separately (the default —
   assert it is not overridden anywhere in the probe: a second, independent defence; the test asserts the child's fd table, never the flag alone).
3. **The READ side made open-then-fstat (AF-AP-70 closed for reads).** `_sha256_file` (`:48-59`: `os.stat(path)` then `open(path, "rb")`) and the
   fixture read (`:240-252`: `os.stat` then `open`) become ONE read primitive: `os.open(path, O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC)` →
   `os.fstat` → `S_ISREG` on the FD (else refuse by an exact name and CLOSE the fd) → clear `O_NONBLOCK` with fcntl → read through `os.fdopen`.
   The red test is VERIFY-N5j's own rig: `os.stat` passes on a regular file, a FIFO is swapped in before the open — today `open()` hangs (rc 124
   under `timeout 10`); after: refused by name, rc 1, no hang. Run every FIFO/hang probe STANDALONE under `timeout` with a PID-scoped watchdog,
   never through pytest (the house rule). Also: a symlink at the path (ELOOP named), a character device (`/dev/zero` — never reaches EOF —
   refused by name), the fd closed on every refusal (count `/proc/self/fd`). The three `_sha256_file` receivers (`:357`, `:433`, `:524` via
   `/proc/<pid>/exe`, the agent entrypoint, the probe's own file) all go through it; `python3 scripts/ap_screen.py proofs/S0-01/tools/acp_probe.py`
   must show ZERO AF-AP-70 rows afterwards — paste the screen before and after, every remaining hit classified by RUN.
4. **The receiver inventory (`test:2826-2849` `_RECEIVER_INVENTORY`) updated for reads.** The write scan stays exact; add the read primitive to the inventory with its
   own kind (`evidence-reader`) so a future `open(path)` read outside the primitive is red the same way an unguarded write is — a planted
   `open(p, "rb")` in a scratch copy must die on the inventory compare (`:3025`), paste it.
5. **The serial four-file run, declared or done.** N5j declared the SERIAL run of `tests/test_s0_01_acp_probe.py tests/test_s0_01_negative_contract.py
   tests/test_s0_01_check_initialize.py tests/test_s0_01_check_acp_conformance.py` NOT-run (the PC tool ceiling). Run it in TWO foreground calls
   if one is too long (the two S0-01 pairs), each through `scripts/test_summary.sh` with the venue exports, and paste both summaries; the xdist
   four-file run as well (`-n 4`; the 9 xfails are the corpus's known-stale `probe_sha256 mismatch`).
6. **Mutants ≥ 12 fresh rows, on scratch copies of the FINAL bytes, killer lines pasted:** O_DIRECTORY-DROPPED (two killers), CLOEXEC-DROPPED,
   CLOSE_FDS-FALSE, READ-STAT-ON-PATH (the old shape restored), READ-NONBLOCK-DROPPED (the FIFO hang returns — the rig must red within its
   timeout), READ-NOFOLLOW-DROPPED, READ-ISREG-DROPPED (a char device accepted), READ-FD-LEAK-ON-REFUSE (the close removed), READ-OUTSIDE-PRIMITIVE
   (a planted path open), INVENTORY-READER-MISSING, plus the write-side rows VERIFY-N5j re-ran (J1-J5, F3-1..3) re-run once more on the final bytes.
   Survivors by construction stated as such; none of the above may survive.
7. **Exact negative reasons.** Every refusal above asserted by its exact stderr text and rc, never `rc != 0` alone (AF-AP-64/65: no
   `if <field> == <literal>:` without a raising other arm; the assertions structural, not line-number mirrors).
8. **Gates on the FINAL bytes:** `scripts/lane_gate.sh -r c6c384a -f "proofs/S0-01/tools/acp_probe.py tests/test_s0_01_acp_probe.py" -t
   "tests/test_s0_01_acp_probe.py" -n 2` (its RESULT line pasted, `identical=yes`); the four-file xdist run; pyflakes rc 0; the FILE IDENTITY block
   (sha256 + line count of both files); `python3 scripts/report_lint.py <your report> --root <your tree> --map probe=proofs/S0-01/tools/acp_probe.py
   --map test=tests/test_s0_01_acp_probe.py` — MISS 0 AND UNRESOLVED 0 (VERIFY-N5j's report carried ten prose refs the linter could not check;
   yours cites `probe:NN` / `test:NN` only).
9. **The 18-class self-sweep** over both files by RUN, one row each, agree/disagree with N5j's table; `ap_screen.py --tests` on the test file
   (the AF-AP-57 row classified).
10. **Report discipline.** DONE table (item → final `file:line` → red control → green proof), the mutant table, the identity block, DISCREPANCIES,
    NOT-done first-class. F4 (the 3 s drain-join calibration on a real leg) stays the coordinator's — NOT this lane's; say so, do not touch it.

## Pinned decisions (do not re-open)
- One READ primitive, fd-first, exactly mirroring the write side's shape (`_open_regular`): open → fstat → validate → use; never stat-then-open.
- The framedir stays the runner's to create and the probe's to own through the fd (VERIFY-N5j item 11); no runner change.
- `/proc/<pid>/exe` reads stay (a kernel magic link the agent cannot redirect — VERIFY-N5j's ruling), but through the primitive.
- No new dependency, no new file; fixture agents stay inline in the test file.
