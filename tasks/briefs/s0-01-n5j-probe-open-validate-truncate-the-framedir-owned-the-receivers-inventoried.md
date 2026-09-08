# Lane N5j — S0-01 ACP probe round 13: open-validate-truncate with one link, the framedir symlink-free and dir-fd-relative, every writer receiver inventoried by identity, the ≥40 campaign in the report

> **STATUS (2026-09-08 21:4xZ): LANDED as checkpoint 9d** (the commit "S0-01 checkpoint 9d: the probe round 13 …", fe2dc3b on origin; report `tasks/briefs/s0-01-n5j-support/N5j-report.md`) → VERIFY-N5j next (pinned to fe2dc3b).

**PIN: `99b7b37`** (the current branch head; the probe and its test are 628da83's round-12 bytes, unchanged since). Role:
code-implementer (the PC Hermes build lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo agent-factory, branch
claude/soundbox-kit-migration-iz1jwf. Boundary (yours, disjoint from every other lane): `proofs/S0-01/tools/acp_probe.py`,
`tests/test_s0_01_acp_probe.py`, your report `tasks/briefs/s0-01-n5j-support/N5j-report.md`. NOT yours: the PC runners under
`proofs/S0-01/tools/pc/` (lane P5b/P5c), the checker, the tee, the backend, `pins.py`. No real agent, Hermes, buzz-acp, relay or
credential (the venue rule); every hostile-path probe standalone under `timeout` with a PID-scoped watchdog, never through pytest;
kill only what you start, by pid; never background a run and stop; no outward actions.

**Inputs (read in this order):** VERIFY-N5i's report `tasks/briefs/s0-01-n5i-support/VERIFY-N5i-report.md` (the round's contract:
F1-F5 with the reproduced hostile-path table and the mutant table) · the N5i brief
`tasks/briefs/s0-01-n5i-probe-the-write-class-and-the-honest-table.md` and the N5i report (its mutant campaign, the class table) ·
VERIFY-N5g-b (the MERGE-READY round: `tasks/briefs/s0-01-n5h-support/` — what must NOT regress) · `docs/INCIDENT-LOG.md`
(AF-AP-55, AF-AP-59, AF-AP-63, AF-AP-65, AF-AP-68).

## Design (pinned — build it, do not redesign it; line numbers are `99b7b37`'s = 628da83's)
1. **F1 — open, validate, THEN truncate; exactly one link.** `_open_regular` (`acp_probe.py:73-78`) opens WITHOUT `O_TRUNC`
   (`O_WRONLY | O_CREAT | O_NOFOLLOW | O_NONBLOCK`, mode 0o644), `fstat`s the fd, requires `S_ISREG` AND `st_nlink == 1`, only then
   `os.ftruncate(fd, 0)` and clears `O_NONBLOCK`; a refusal closes the fd and names the reason (`not a regular file: …` /
   `hardlinked evidence leaf (nlink=2): …`). VERIFY-N5i's hardlink rig becomes a committed test: the foreign inode's bytes are
   UNCHANGED after the refusal (the killer: with `O_TRUNC` back, the foreign text is gone). The fresh-file path (`O_CREAT` on an absent
   name) stays green; the symlink (ELOOP), FIFO-with-reader, directory, `/dev/null`, UNIX-socket refusals stay green.
2. **F2 — the framedir is symlink-free and every leaf is opened dir-fd-relative.** After `os.makedirs(framedir)` (`:253-258`) the probe
   requires `os.path.realpath(framedir) == os.path.abspath(framedir)` (any symlink component → `framedir path contains a symlink: …`,
   rc 1 before any write) and opens the directory once with `O_RDONLY | O_DIRECTORY | O_NOFOLLOW`; every evidence leaf is opened
   with `dir_fd=` and a bare basename (a name with `/` or `..` refused by name). VERIFY-N5i's `frame-link -> foreign/` rig becomes a
   committed test: rc 1, the named line, ZERO files under `foreign/`. The runner/probe split stated in the primitive's docstring:
   the runner owns fresh framedirs; the probe refuses everything it cannot prove — the comment "can never block or write unsafely"
   rewritten to the real boundary (regular, single-link, symlink-free path, bounded).
3. **F3 — the receiver scan by IDENTITY, the inventory exact.** The AST scan (`test:2873-2895`) resolves aliases (`o = open`,
   `from os import open as raw`, `import io; io.open`, `os.fdopen`, `builtins.open`) by a name-binding pass over the module, and
   treats `.write_text(` / `.write_bytes(` / `.open(` attribute calls on any value as receivers; the floor `len(examined) >= 12`
   (`test:2955-2960`) becomes an EXACT keyed inventory `{(function, callee, ordinal): kind}` equal to the committed dict — a
   removed writer (VERIFY-N5i's deleted `_write_env`), an added one, or a re-routed one reds it by key. The three survivors
   (`o = open; o(..., "w")`, `pathlib.Path(...).write_text(...)`, the deleted writer) are the round's named killers.
4. **F5 — the campaign.** ≥40 mutants in the report: the N5i lane's 33 + VERIFY-N5i's eight focused ones + the three F3 killers +
   this round's (`O_TRUNC` restored, `st_nlink` check removed, the realpath check removed, `dir_fd` dropped, the basename check
   removed) — every one killed with its killer line pasted; by-construction survivors named as such.
5. **F4 stays the coordinator's** (the 3 s drain join calibrated on the real-leg recapture) — state it NOT-done first-class; do not
   change the join policy.
6. **Every negative control fails for the EXACT expected reason** (the named line, never `rc != 0` alone — AF-AP-63); no
   `if <field> == <literal>:` without a raising other arm (AF-AP-65); no name-based kill (AF-AP-59). VERIFY-N5g-b's MERGE-READY
   surface must not regress: the whole probe suite green.
7. **18-class self-sweep as an ENUMERATION** (counts + method; class 11 world-enumeration: the receiver inventory IS the enumeration
   now; class 2: every evidence write through the primitive — prove it by the inventory).
8. **Report discipline:** FILE IDENTITY of the FINAL bytes; every `file:line` from `grep -n` on the FINAL bytes and
   `python3 scripts/report_lint.py <report> --map P=proofs/S0-01/tools/acp_probe.py --map T=tests/test_s0_01_acp_probe.py` pasted
   with MISS 0; the direct venue suite pasted (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`, an
   absolute `--basetemp`, `/home/rocco/venv-agent-factory/bin` first on PATH) for `tests/test_s0_01_acp_probe.py` AND the four-file
   set VERIFY-N5i ran (`tests/test_s0_01_acp_probe.py tests/test_s0_01_negative_contract.py tests/test_s0_01_check_initialize.py
   tests/test_s0_01_check_acp_conformance.py`, its `568 passed, 9 xfailed` is the floor); the two `lane_gate.sh` RESULT lines
   (`scripts/lane_gate.sh -r 99b7b37 -f "<your files>" -t "tests/test_s0_01_acp_probe.py" -n 2`); `ap_screen.py` prod + `--tests`
   classified by run; NOT-done first-class.

## Report
Write it to `tasks/briefs/s0-01-n5j-support/N5j-report.md` inside your tree, draft after EACH item, and return it whole as your
final message: the DONE table (item → file:line → the red test → its killer line), the mutant table (≥40), the discrepancies, the
self-attack, the evidence tiers, NOT-done first.
