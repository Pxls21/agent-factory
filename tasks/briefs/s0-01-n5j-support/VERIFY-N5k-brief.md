# VERIFY-N5k — adversarial grade of lane N5k ARM A (S0-01 ACP probe round 14, landed b9b6134: the two surviving flags made load-bearing, the READ side made open-then-fstat, the receiver inventory taught reads, the serial four-file run) — WITH the comparative grade of ARM B v3's unlanded build of the same brief

**PIN: `3277373`** (the branch head; arm A's two files are byte-identical to the landing b9b6134 — `proofs/S0-01/tools/acp_probe.py`
677 lines sha `e71ec3cfc7db2204…`, `tests/test_s0_01_acp_probe.py` 3592 lines sha `ee29b9584fdc3908…`; re-derive both with `sha256sum`
and `wc -l` at the PIN and paste them as your FILE IDENTITY block). Role: adversarial-verifier on the PC Hermes lane (route
`agentfactory-verify-local`, the local Qwen3.8-27B at `xhigh` — D-028: xhigh verifies). Repo agent-factory, branch
claude/soundbox-kit-migration-iz1jwf. Venue: `tasks/briefs/pc/VENUE-MAP.md` applies. Authorization: the owner's own ACP probe under test —
defensive work on their system.

**You grade; you do not build.** Never edit `proofs/`, `tests/`, `scripts/` in your tree: every mutant, every rig, every reconstruction runs
on a SCRATCH COPY under your lane's scratch dir. Your only deliverable is the report `tasks/briefs/s0-01-n5j-support/VERIFY-N5k-report.md`
(drafted after EACH item — the incremental rule — and returned whole as your final message).

**Inputs (read in this order):**
1. `tasks/briefs/s0-01-n5k-probe-the-flags-load-bearing-the-read-side-atomic-the-serial-run.md` — the round's contract: items 1-10 AND its
   two amendments at the top. AMENDMENT 2 is a settled, measured fact (CPython PEP 446: `os.open` returns a non-inheritable fd regardless of
   `O_CLOEXEC`; `subprocess.Popen` defaults to `close_fds=True`; so the CLOEXEC-DROPPED mutant leaks NOTHING through the real emitter — the
   replacement negative control is the isolated `F_SETFD` census plus a structural pin). Do NOT re-litigate it; grade against it.
2. `tasks/briefs/s0-01-n5j-support/N5k-report.md` — ARM A's report (the landed build; `113 passed`; its DONE table names every anchor).
3. `tasks/briefs/s0-01-n5j-support/VERIFY-N5k-pack.md` — the code-intel pack over the two files at the PIN (graft skeletons, graft ask,
   GitNexus impact, crg callers/tests, ripwire callers + test-gate, the registry screen). Start from it; cite it where it answers a question.
4. `tasks/briefs/s0-01-n5j-support/N5k-xhigh-report.md` + `tasks/briefs/s0-01-n5j-support/N5k-xhigh-v3.diff` — ARM B v3's build of the SAME
   brief (xhigh; NOT landed; `119 passed` on its own tree; 8 new tests). Its diff is against `c6c384a`'s bytes (the PIN of the build round),
   NOT against arm A's. Material for item 8 only — nothing in it is a fact about the landed code until you reproduce it.
5. `tasks/briefs/s0-01-n5j-support/VERIFY-N5j-report.md` — the predecessor verdict (the two survivors that opened this round; the READ-side
   finding; its mutant rows J1-J5, F3-1..3).
6. `docs/INCIDENT-LOG.md` rows AF-AP-70, AF-AP-64, AF-AP-65, AF-AP-73, AF-AP-76 — the classes you grade against and the loop you must not enter.

## Item 0 — the mechanical gates, pasted
On the PIN, from your lane tree, with the venue exports (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden
S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`), `/home/rocco/venv-agent-factory/bin` FIRST on PATH, a SHORT absolute `--basetemp` under your
scratch dir (`mkdir -p` its parent first): `bash scripts/test_summary.sh tests/test_s0_01_acp_probe.py` TWICE in two foreground calls —
expect `113 passed` both times (arm A: `113 passed in 51.85s 113 passed in 51.24s`; the coordinator's clean copy: `113 passed in 50.90s`);
paste both summaries verbatim. Then `python3 -m pyflakes` on both files (rc 0), `python3 scripts/ap_screen.py proofs/S0-01/tools/acp_probe.py`
(paste the whole screen; AF-AP-70 rows must be ZERO — every other hit classified by RUN, not by reading), and the FILE IDENTITY block.

## Items
1. **O_DIRECTORY load-bearing (`probe:327` the framedir flag set; `test:3443` the window rig, `test:3466` the dropped-mutant discriminator;
   the structural pin).** On a scratch copy of the PIN, drop `os.O_DIRECTORY` from the framedir open: which tests red, and for WHICH
   reason (paste the failing assertion lines)? Then the question arm A's own DISCREPANCIES raise: does the window rig (`test:3443`) actually
   drive the mutant through the `os.open` at :327, or does an earlier check (the `makedirs`/realpath pair above it) refuse the planted file
   first, rc 64, on BOTH the final bytes and the mutant — v3 measured exactly that on its tree (0/210 window wins across three sweeps; the
   file-at-framedir shape never reaches the open). If arm A's kill rests on the structural pin alone, say so: a pin is a MIRROR of the flag
   token, not an observation of the behaviour. State what a behavioural kill at the open level would need (v3 built one: the open-level
   ENOTDIR proof — `probe@c6c384a` has no such line; v3's diff adds it) and whether the landed bytes carry it.
2. **O_CLOEXEC under AMENDMENT 2's contract (`probe:327` the flag; `probe:371` the agent `Popen` with no `close_fds` override;
   `test:3563` the isolated F_SETFD census; `test:3578` the close_fds-default pin).** Three mutants on scratch copies, each: which test
   reds and by what mechanism — (a) CLOEXEC-DROPPED (the flag removed at :327); (b) CLOSE_FDS-FALSE (`close_fds=False` added at :371);
   (c) the TRIPLE mutant that is the only real leak on CPython ≥ 3.4 — the flag removed AND `os.set_inheritable(framedir_fd, True)` after
   the open AND `close_fds=False` at :371 — launch the probe's REAL agent path with a census agent (a fixture inside the test file's own
   rig pattern, or your standalone rig) and read the child's fd table: does the framedir fd arrive in the child? Then: does ANY test in
   arm A's suite observe the child's fd table THROUGH THE REAL EMITTER (`probe:371`) rather than through an isolated fork+exec? If none,
   that is a finding with its severity argued: the isolated census (`test:3563`) proves `F_SETFD` semantics, not the probe's launch; the pin
   (`test:3578`) proves the absence of a `close_fds` token. v3's `test_probe_census_agent_sees_no_framedir_fd_on_final_bytes` observes the
   real emitter — item 8 decides whether it is port-worthy; here you decide whether the LANDED bytes are gated on this property at all.
3. **The READ primitive `_read_regular` (`probe:48-77`; its receivers `_sha256_file` `:81-94`, the fixture read `:282`, the `/proc/<pid>/exe`
   read — locate the third by `sed -n`).** Attack it STANDALONE under `timeout`, never through pytest, one probe per call, a PID-scoped
   watchdog: a FIFO swapped in after a stat (must refuse by its exact name, rc 64, in well under a second — the old shape hangs rc 124);
   a symlink (ELOOP named); `/dev/zero` (never EOF — refused by name); a directory; a fd-leak count across every refusal (`/proc/self/fd`
   before/after); the `O_NONBLOCK` clear — mutate the `fcntl` clear away on a scratch copy: which test reds, and does a read of a REGULAR
   file larger than the pipe buffer still complete (it must — `O_NONBLOCK` on a regular file is a no-op; state whether the clear is
   load-bearing or belt-and-braces, from a RUN). Then grep the probe for every `open(`, `Path(...).read_*`, `io.open`, `os.fdopen`,
   `json.load(open` spelling outside the primitive: the inventory (item 4) is only as good as its scanner's vocabulary.
4. **The receiver inventory (`test:2826-2849` `_RECEIVER_INVENTORY` incl. the `("_read_regular", "os.open", 1): "evidence-reader"` row;
   `:2857` `_scan_file_receivers`; `:3030` the equality test; `:3067` the planted read).** Plant, on scratch copies, one read each by
   `Path.read_bytes`, `Path.read_text`, `io.open`, `os.fdopen(os.open(...))` in a NEW function and in an EXISTING function: which plants
   die on the equality compare and which slip the scanner (each slip = a finding with the scanner's blind spot named). Confirm the rows are
   identity-keyed (function, callee, ordinal), not a count: a planted read that REPLACES an existing one (same ordinal) — does the compare
   still red?
5. **The serial four-file run.** Reproduce pair 1 (`tests/test_s0_01_acp_probe.py tests/test_s0_01_negative_contract.py`, one foreground
   call, arm A: `172 passed in 51.24 s`) and the xdist four-file run (`tests/test_s0_01_acp_probe.py tests/test_s0_01_negative_contract.py
   tests/test_s0_01_check_initialize.py tests/test_s0_01_check_acp_conformance.py -n 4`; arm A: `600 passed, 9 xfailed in 198.80 s`; the 9
   xfails are the corpus's known-stale `probe_sha256 mismatch`). Paste both. Pair 2 serial is NOT required (conformance alone exceeds the
   tool ceiling; arm A split it — read its two halves, do not re-run).
6. **Mutants.** Re-run arm A's 12 rows (its item 6) on FRESH scratch copies of the PIN bytes, one row per copy, the killer line pasted per
   row; then ≥ 8 rows of your own that arm A did not run (candidates: the compound of item 2(c); `S_ISREG` replaced by `not S_ISDIR`;
   the primitive's `os.close` moved before the `fstat`; the inventory row for the reader deleted; the `O_NOFOLLOW` dropped at :327 with a
   symlinked framedir; the realpath check removed with the window rig; a `try/except OSError: pass` around the fstat; the ordinal key
   collapsed to the callee name). Survivors by construction stated as such; every other survivor is a finding.
7. **Exact negative reasons (AF-AP-64/65).** Every refusal in the two files asserted by its exact stderr text AND rc, never `rc != 0` alone;
   no `if <field> == <literal>:` without a raising other arm; assertions structural, not line-number mirrors. List every violation with
   `test:NN`.
8. **THE COMPARATIVE GRADE — arm B v3's build against arm A's landed build (D-028's third data point: the QUALITY axis).** Reconstruct v3's
   two files on a scratch copy: `git show c6c384a:proofs/S0-01/tools/acp_probe.py` and `git show c6c384a:tests/test_s0_01_acp_probe.py`
   into a fresh copy of the tree at `c6c384a` (`git archive c6c384a` on the PC clone), then `git apply` `N5k-xhigh-v3.diff` — v3's identity
   block says probe 695 lines sha `d1416488…`, test 3681 lines sha `d7f033dc…`; paste yours. Run v3's test file on v3's tree (expect
   `119 passed`; paste). Then, for EACH of v3's 8 new tests (`grep '^+def test_' N5k-xhigh-v3.diff`), a row: the property it pins → the
   arm-A test that pins the same property (name, or NONE) → the mutant that discriminates (run it on BOTH trees under BOTH suites, on
   scratch copies) → verdict REDUNDANT / STRONGER (v3 kills, arm A does not) / WEAKER / DIFFERENT-PROPERTY. Three design deltas get their
   own rows: v3's explicit `close_fds=True` + the named open-level ENOTDIR refusal (`framedir is not a directory`) + the real-emitter census
   (`test:3603`/`:3623` in v3's numbering). Then THE PORT LIST: every v3 test or line whose port into the LANDED bytes closes a hole you
   demonstrated (item 1, 2, 4 or 6), with the exact adaptation each needs (v3 names the primitive `_open_regular_read`; arm A `_read_regular`;
   v3's ENOTDIR line does not exist in arm A's probe — a test that asserts it needs the probe change too). You recommend; the coordinator ports.
   Finally the two DISCREPANCIES sections side by side: every premise BOTH arms flagged, every one only ONE flagged, and which arm's
   statement the RUN supports.
9. **The two reports' discipline.** Arm A's `N5k-report.md`: `python3 scripts/report_lint.py tasks/briefs/s0-01-n5j-support/N5k-report.md
   --root <your tree at the PIN> --map probe=proofs/S0-01/tools/acp_probe.py --map test=tests/test_s0_01_acp_probe.py` (arm A pasted
   `41 refs — OK 39, NEAR 0, MISS 0, UNCHECKABLE 2` at the PIN; reproduce). V3's `N5k-xhigh-report.md` never pasted its lint (its
   DISCREPANCIES 5 is a placeholder): run the same lint against v3's RECONSTRUCTED tree and paste it. Any kill either report presents that
   its own tables do not support = a finding; any predecessor row presented as a kill of the final bytes = a finding.
10. **The design.** (a) Is AMENDMENT 2's replacement (isolated census + structural pin) an adequate gate on the O_CLOEXEC property for the
    landed code, or should the landed code ALSO carry a real-emitter fd-table observation (the one test that would catch item 2(c)'s triple
    mutant)? Argue from your runs, with the cost (one more fixture agent, one more subprocess per run). (b) The READ primitive: is
    `O_NONBLOCK` + clear the right shape, or is `fstat`-then-`S_ISREG` on an `O_RDONLY|O_NOFOLLOW|O_CLOEXEC` fd already sufficient on Linux
    for a FIFO (an `O_RDONLY` open of a FIFO with no writer BLOCKS — so the `O_NONBLOCK` IS load-bearing at the open; state it from the RUN
    of item 3). Recommend; do not build.
11. **Discipline.** `file:line` by `sed -n` on the PIN (and on the reconstructed v3 tree, cited as `v3probe:NN` / `v3test:NN` with maps
    `--map v3probe=<scratch path>`); every claim reproducible from its pasted line; kill only what you start, by pid; scratch copies only;
    FIFO/hang probes standalone under `timeout`; the real corpus `/home/rocco/s0-01-pinned/realleg/golden` READ-ONLY (copy a leg before
    any mutation). **Bounded gates (AF-AP-76): run `report_lint.py` on your own report LAST with the four maps and `--min-refs 25`; apply its
    `fix:` hints for at most THREE rounds, then paste the final summary line and finish.** **Bounded premises: a brief premise that does not
    reproduce gets at most THREE experiments, then one DISCREPANCIES line and the grade continues on the measured truth.**

## Report
`tasks/briefs/s0-01-n5j-support/VERIFY-N5k-report.md`: VERDICT first (MERGE-READY / NOT-READY on arm A's LANDED bytes at the PIN, with the
blocking findings named F1…), then the FILE IDENTITY block, the item-by-item table (item → what was attacked → pasted evidence line →
finding or HELD), the mutant table (every row: mutant, killer test or SURVIVED, pasted line), the COMPARATIVE TABLE and the PORT LIST of
item 8, the two DISCREPANCIES side by side, the design recommendations of item 10, NOT-done first-class, the lint summary line last.
Numbers pasted, never typed. Report EVERYTHING found — no severity filtering (the main loop ranks).
