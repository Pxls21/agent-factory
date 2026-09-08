# VERIFY-N5j — adversarial grade of lane N5j (S0-01 ACP probe round 13: open-validate-truncate with one link, the framedir held open as a directory fd with every evidence leaf created relative to it, the receiver scan by identity with an exact inventory)

You are an adversarial-verifier (the PC Hermes verify lane by default — `agentfactory-verify`; sandbox Opus 5 is the fallback). Repo
agent-factory, branch claude/soundbox-kit-migration-iz1jwf. **PIN: `fe2dc3b`** (checkpoint 9d — the commit carrying the lane's two files
+ its report). Grade the bytes of `git archive fe2dc3b` from a private copy (`vn5j/` under your scratch dir; delete it when done). Read-only
git on any shared tree; every mutant on scratch copies; every pytest run with an explicit `--basetemp`; every FIFO/hang probe under `timeout`
and standalone (never a hang shape through pytest); kill only what you start, PID-targeted (never `pkill`/`pgrep -f`); never background a run
and stop; no outward actions; never read, print or commit a credential. `S0_01_VENUE` + `S0_01_REAL_LEG_DIR` exported per venue on every
pytest run (the sandbox: `S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden`, interpreter `/root/venv-agent-factory/bin/python`).
Authorization: the owner's own ACP probe under test — defensive work on their system.

**Inputs (read in this order):** VERIFY-N5i's report `tasks/briefs/s0-01-n5i-support/VERIFY-N5i-report.md` (the round's contract: F1 the
O_TRUNC-before-nlink clobber, F2 the symlinked parent, F3 the blind receiver scan + the `>= 12` floor, F4 the drain join UNSURE, F5 the
campaign) · the lane brief `tasks/briefs/s0-01-n5j-probe-open-validate-truncate-the-framedir-owned-the-receivers-inventoried.md` · the lane's
report `tasks/briefs/s0-01-n5j-support/N5j-report.md` (NOT-done first, the DONE table, the 49-row two-tier mutant table, the 18-class sweep,
the ap_screen classification, DISCREPANCIES, the self-attack) · the checkpoint commit body (`git show -s fe2dc3b`; it names what the
coordinator already knows: AF-AP-70 fires on the probe's READ side) · `proofs/S0-01/negative_contract.py` (`:187` the probe_sha256 pin) ·
`proofs/S0-01/tools/frame_tee.py` (the other timeline writer) · `docs/INCIDENT-LOG.md` (AF-AP-40, AF-AP-42, AF-AP-55, AF-AP-57, AF-AP-59,
AF-AP-63, AF-AP-64, AF-AP-65, **AF-AP-70** — classify-then-open by pathname, registered AFTER the lane's own screen ran).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-01-n5j-support/N5j-report.md --rev fe2dc3b --map probe=proofs/S0-01/tools/acp_probe.py
--map test=tests/test_s0_01_acp_probe.py` — the lane read `62 refs — OK 54, NEAR 3, MISS 0, UNCHECKABLE 5` on its tree: reproduce, then
resolve the 3 NEAR and 5 UNCHECKABLE rows BY HAND (each named: the ref, what it points at on the PIN, right or drifted); `ap_screen.py
proofs/S0-01/tools/acp_probe.py` — 10 hits NOW (the lane's screen read 8: the two **AF-AP-70** rows at `probe:53` (`os.stat(path)`) and `probe:245` (`os.stat(fixture_path)`) are new
since) — classify every hit by RUN; `--tests` (AF-AP-57 ×1); `--s0-01`; pyflakes rc 0; the FILE IDENTITY block against the PIN (both rows:
`acp_probe.py` 642 lines `7874a4e3…`, the test 3302 lines `9ff359dc…`).

## Items
1. **`_open_regular` (`probe:62-95`) — open, validate on the fd, then truncate.** Attack the primitive on the FINAL bytes: a hardlinked leaf
   (nlink 2) → refused by the exact message, the foreign inode's bytes INTACT (`test:3178` `test_probe_hardlink_refusal_preserves_the_foreign_inode` — reproduce; the restored-O_TRUNC control `:3185`);
   the fd CLOSED on every refusal path (`:93` — count `/proc/self/fd` before/after each refusal kind in one process); a symlink (ELOOP —
   the text pasted), a FIFO with and without a reader (O_NONBLOCK — which arm refuses, `S_ISREG` on the fd?), a directory, `/dev/null`, a
   socket, an existing regular leaf with nlink 1 (truncated — fine, prove it); the bare-basename guard (`:73-75`): `"a/b"`, `".."`, `"."`,
   `""`, a name with a NUL byte — each refused before `os.open`? A hard link ADDED between the fstat and the ftruncate: state which invariant
   survives that race (the inode is ours — the attacker shares OUR leaf; not a foreign clobber) and whether any test can pin it. Is the
   guard reachable in production (the runners create FRESH framedirs) or only by a hostile framedir owner — rule on the trust boundary as
   VERIFY-N5i item 1 did, and say whether the answer changed.
2. **The framedir (`probe:274-292`): realpath-checked before and after mkdir, opened `O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC`.**
   Reproduce `test:3197` `test_probe_refuses_a_symlinked_framedir_before_any_foreign_write` (the symlinked parent → rc 1, the exact message,
   NO foreign write) and `test:3225` `test_probe_writes_remain_on_the_original_dir_fd_after_path_swap` (writes stay on the original dir fd). Attack: a symlink in a MIDDLE component vs the LAST component (which check catches which); the
   lane's self-attack #1 (a component swapped between the second realpath and `os.open` — what does an attacker who WINS the race obtain:
   a real directory of their own opened, every leaf then created there without O_EXCL — a foreign-inode clobber, or the attacker's own
   files in the attacker's own directory? rule, with a probe); a bind mount (realpath is blind to it — declared limit, or does the
   O_DIRECTORY fd make it moot?); `os.makedirs` mode/umask on the created dir; the directory fd is NEVER closed (`os.close(framedir_fd)` is
   absent — process exit closes it): is the fd opened BEFORE the agent child is spawned, does `close_fds`/`O_CLOEXEC` keep it out of the
   agent's fd table (a probe that HANDS the agent under test a directory capability is the attack — prove the child's `/proc/self/fd` has no
   entry for the framedir; then mutant CLOEXEC-DROPPED in item 6).
3. **The receiver scan (`test:2826-2849` `_RECEIVER_INVENTORY`, `:2852-3014` `_scan_file_receivers`, `:3021-3055` the test).** Enumerate the file receivers on
   the FINAL bytes yourself — every `open`/`os.open`/`os.fdopen`/`io.open`/`io.FileIO`/`Path.write_*`/`Path.open`/`codecs.open`/`gzip.open`/
   `NamedTemporaryFile`/`shutil.*`/`print(file=)`/`json.dump(…, fp)`/`os.write`/`os.replace`/`os.rename`/`os.link`/`os.symlink`/`os.mkfifo`
   — and diff against the 22-row inventory (keyed by callee identity: is it? read the key). Plant on scratch copies: `from builtins import
   open as o`, `getattr(os, "open")`, `functools.partial(open, "w")`, a lambda wrapper, `io.FileIO`, `os.fdopen(os.open(...))` OUTSIDE
   `_open_regular`, `pathlib.Path.open`, `os.write(fd, …)` on a raw `os.open` fd, `subprocess.run(stdout=open(...))`, a write inside a nested
   function / lambda / comprehension, a write reached through `exec`/`importlib`. Which evade? Each evader: SOLID/UNSURE, the failing input,
   the minimal walker fix, the exact red test. The three negative controls (`:3045`, `:3051`, `:3055`) assert `!= _RECEIVER_INVENTORY` —
   an ORDER-BLIND set-diff: plant one receiver AND delete one entry so the inventory's SIZE is unchanged — does `:3025` still go red (the
   exact dict compare should) and do the controls prove the planted receiver was SEEN, or only that "something changed"? The residual
   count at `:3031` (`== 12` evidence-writers) — derived from the exact inventory or a second floor?
4. **The READ side — classify-then-open by pathname (AF-AP-70 by RUN at `probe:53` `os.stat(path)` in `_sha256_file`, `probe:245` `os.stat(fixture_path)` the fixture read).** The
   WRITE side is atomic now; the READ side is `os.stat(path)` then a path `open()`. Reproduce the class on a scratch copy: swap a FIFO in
   between the stat and the open (a hook/sleep in the copy, or a race harness) — `open()` blocks; under `timeout` paste rc 124. Then rule the
   trust boundary per receiver of `_sha256_file`: the probe's own file (`_PROBE_PATH`, the operator's), the agent entrypoint (the runner's
   argument), the child interpreter (`os.readlink("/proc/%d/exe")` at `:357`/`:433`/`:524` — a path the AGENT under test controls after
   exec: a hostile negative-leg agent that replaces its own interpreter path with a FIFO after exec — reachable? reproduce or refute with a
   fixture agent), and the fixture path (`:240-252`, the repo's). Is the mechanical fix `os.open(path, O_RDONLY|O_NOFOLLOW|O_NONBLOCK)` +
   `fstat` + `os.fdopen` (a FIFO opened O_RDONLY|O_NONBLOCK returns without a writer, then `S_ISFIFO` refuses; a regular file reads normally
   once O_NONBLOCK is cleared) — write the red test and state whether it is round 14's item or a declared limit with the boundary named.
5. **The drain join (`probe:549` `join(timeout=3)`, `:555` `is_alive() and drain_error[0] is None`, `:565-567` the wording) — unchanged this
   round; F4's calibration stays the coordinator's recapture.** Your part: the dir-fd refactor of `_drain_stderr` (`:120-135`, opens the
   stderr leaf through `_open_regular(..., dir_fd=framedir_fd)` on the drain THREAD): the open races nothing in the main thread? (the M3
   handler `:583-630` writes its leaves through the same fd while the drain may still be alive — any shared mutable state, any ordering
   where the drain's open happens AFTER the main path decided the leaf set?); a drain that dies on its open (a FIFO planted at
   `agent-stderr.txt` in a fresh framedir is impossible — say why; a hardlinked one is not — reproduce: the drain refuses, `drain_error`
   set, rc 1 with the exact message).
6. **Mutants ≥ 40 on the FINAL bytes, on scratch copies.** Re-run the lane's N5j-run rows J1-J5 and F3-1..3 (report `:183-190`). Then the
   PREDECESSOR tier (41 rows carried, not re-run — the lane says so): every carried row whose mutant SITE was rewritten this round
   (`_open_regular`, the framedir block, the leaf writers, the walker) is STALE evidence until re-run — re-run those (name each), carry the
   rest. Add yours: NLINK-AFTER-TRUNCATE (the check moved below the ftruncate), FSTAT-ON-PATH (`os.stat(path)` in place of `os.fstat(fd)`
   — the classify-then-open shape must die), NOFOLLOW-DROPPED, O_DIRECTORY-DROPPED (which test dies? none = a finding), CLOEXEC-DROPPED
   (the child inherits the directory fd — which test dies? none = a finding + the red test from item 2), DIRFD-NONE-FOR-ONE-LEAF (one leaf
   path-based — the inventory must die), REALPATH-ONCE (only the pre-mkdir check kept), BASENAME-GUARD-DOTDOT-ONLY, INVENTORY-EMPTY (the
   walker returns `{}`), NEG-CONTROL-CONSTANT (the walker returns a constant ≠ the inventory: `:3025` dies — do the three controls still
   pass? that is their coverage), the item-3 evaders, DRAIN-BOUND-9S, HASH-NONE-AT-M3. Paste every killer line; survivors by construction
   stated as such; every survivor that is a hole is a finding.
7. **The 18-class re-scan by RUN** (the lane's table, report `:194-216`): agree or disagree per row; the AF-AP-70 rows classified (the lane's
   screen predates the registry row); every `if <field> == <literal>:` without a raising other arm listed (AF-AP-65); the `sum(...) == 12`
   at `test:3031` (`== 12`) classified.
8. **The gates.** Reproduce `108 passed` on the PIN (the lane: `108 passed in 51.05s`; the coordinator: sandbox `108 passed in 47.36s` /
   `47.04s`, PC `108 passed in 11.33s` with 8 workers); the four-file set with xdist on the PC (`tests/test_s0_01_acp_probe.py
   tests/test_s0_01_negative_contract.py tests/test_s0_01_check_initialize.py tests/test_s0_01_check_acp_conformance.py`, the lane's
   `595 passed, 9 xfailed in 210.82s (0:03:30)` with `-n 4` — the 9 xfails are the corpus's known-stale `probe_sha256 mismatch`, paste the
   reason once). The SERIAL four-file run hit the lane's tool ceiling and is declared NOT-run: state whether xdist can hide an order/
   isolation defect in THIS set (shared tmp paths, module state, the fixture sockets) — a reasoned ruling with evidence, or the serial run
   if your ceiling allows it in ONE foreground call.
9. **The report's own discipline.** The two evidence tiers are labelled — is any predecessor row presented as a kill of the FINAL bytes?
   The "final collection is 604 tests" note (report DISCREPANCIES) — reconcile 604 with `595 passed, 9 xfailed`; the report was written
   AFTER the final bytes (its own claim) — check the refs it cites against the identity block; the process census by pid; the path-swap
   rig strengthened after the first green run and the gates re-run — confirm the pasted gates postdate that edit (the transcript
   `transcripts/pc/pc-n5j.md--99b7b37.md` is on `57e7703` if you need the order).
10. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; kill by pid; scratch copies only.
11. **The design.** Is `st_nlink == 1` the right invariant for an evidence leaf (a backup tool's hard link → refused; acceptable for fresh
    framedirs — say so or not); the fd-relative model's boundary — the runner creates the framedir, the probe owns the fd: which invariant
    does each own now, and does `pc_negative.py` / `collect_leg.sh` still pre-validate anything the probe no longer needs; the READ side's
    boundary (item 4): one primitive for reads and writes, or two, and which round owns it; the M3 last-resort leaves when the framedir
    open ITSELF fails (`:280`/`:290` raise before `:291`): no leaf can be written — the exit code and the stderr line are the only
    evidence; is that asserted, and is it the right shape for `negative_contract.validate_negative_dir`?

## Report
Save to `tasks/briefs/s0-01-n5j-support/VERIFY-N5j-report.md` inside your tree — draft after EACH item — then return it whole. Findings:
ALL, no severity filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact red test,
SOLID/UNSURE; reproduced vs reviewed vs skipped; verdict MERGE-READY or NOT-READY with the blocking set and the cheapest path; the items
that belong to OTHER lanes (A5l, D5n, the coordinator's recapture) named as such.
