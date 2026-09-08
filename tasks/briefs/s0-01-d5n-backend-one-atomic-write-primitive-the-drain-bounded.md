# Lane D5n — S0-01 scripted backend round 17: ONE atomic open-validate-write primitive for every path the backend creates or reads (the record slot, the pidfile, the token file), the readiness drain bounded, the ban's evasions documented, one cost table (build lane: PC Hermes `code-implementer`; sandbox Opus 4.6 `code-implementer` only if the bridge is down)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".) The backend's last checkpoint is
9c = `77f46a2` and its three files are unchanged since: `proofs/S0-01/tools/scripted_backend.py` 894 lines sha `1968c156…`,
`tests/test_s0_01_scripted_backend.py` 2361 lines sha `02b4cd9a…`, `tests/red/test_s0_01_backend_credential_screen.py` 1278 lines
sha `71aafdb7…` — the exact bytes VERIFY-D5m graded (its identity table). Line numbers below are those bytes'.

**Why:** VERIFY-D5m (`tasks/briefs/s0-01-d5m-support/VERIFY-D5m-report.md` — READ IT WHOLE FIRST; it is the contract for this
round) graded round 16 NOT-READY. The direct gates are green twice (`548 passed in 178.77s` / `548 passed in 178.79s`) and every
guard D5m added holds against a FIFO planted BEFORE it runs — but both new guards are classify-then-open by pathname, and the hang
the round was opened to close comes back one race later (registry row **AF-AP-70**): **F1 BLOCKING** the per-request record slot —
`backend:572-575` is `slot = self.record_dir / f"{n:06d}.json"`, `if _refuse_non_regular(slot): raise`, `slot.write_text(...)`; with
a barrier after the classifier and a FIFO planted in the window the handler hangs (client `TimeoutError`, server alive);
**F2 BLOCKING** the pidfile — `backend:876-881` is the same shape (`_refuse_non_regular(args.pidfile)` then
`args.pidfile.write_text(...)`); the process stays alive and unbound, blocked on the FIFO. The committed tests plant the FIFO
before classification and cannot see either. The third instance is older and on the READ side: `backend:842-854` classifies the
token file (`S_ISREG` at :843) and then `load_token(args.token_file)` opens it by name (AF-AP-30's twin). **F3 SHOULD-FIX**
`_drain` (`main:58-74`) does `out.append(stream.read() or "")` at :71 after `proc.poll()` is not None — a descendant that inherited
stdout keeps the pipe open and the read never sees EOF (the verifier's watchdog fired at 4.0 s); **F4** the live-pipe branch at
`main:64-65` is necessary but not independently pinned — deleting it survives the committed wait-ready tests; **F5** the AST
ban's bare `ast.parse(path.read_text())` (`red:1212`) fails a malformed target without naming it; **F6** the `OUT OF SCOPE` text
(`red:1198-1203`) omits three evasions the verifier found (`match` statements, the affirmative `if x == MARKER: raise`, the
length-zero `x in (MARKER,)` form) — the walker itself caught 13 of 23 spellings, MORE than D5m's report claims (11 of 19);
**F8/F9** report fidelity: the cost table (PC 1.52/0.56) disagrees with the docstring (1.86/0.72) and the verifier's rerun
(1.889/0.719); "18 `_free_port()` call sites" are 16 calls + 2 definitions; **F10** pyflakes is absent on the PC image. F7 (the
`synthetic_leg` coupling) is CLOSED by 9c. What held and must stay held: the record pinned at every served path, the startup
guards' exact stderr lines and rc 2, the refusal that precedes the bind (`main:433-458`, `test_pidfile_refusal_precedes_the_bind`), the counter advancing past a refused slot,
`report_lint` MISS 0, 548 ×2 on both venues.

**Inputs (read in this order):** VERIFY-D5m whole · `tasks/briefs/s0-01-d5m-support/D5m-report.md` and the D5m brief ·
`docs/INCIDENT-LOG.md` (AF-AP-30, AF-AP-40, AF-AP-59, AF-AP-60, AF-AP-61, **AF-AP-70**, AF-AP-72) · `proofs/S0-01/pins.py`
(`require_regular_file` — the shared classifier; you do NOT edit it) · the probe's `_open_regular` (`proofs/S0-01/tools/acp_probe.py:62-78`,
READ-ONLY — lane N5j is rewriting it in its own tree; the coordinator reconciles the two primitives after both land) · the pack
`scripts/lane_context.sh -q 'where does the backend open a path by name' -s main State.record _record load_token _refuse_non_regular -o pack.md proofs/S0-01/tools/scripted_backend.py`
(run it first; attach it).
**Scope (exactly these + your report):** `proofs/S0-01/tools/scripted_backend.py` · `tests/test_s0_01_scripted_backend.py` ·
`tests/red/test_s0_01_backend_credential_screen.py` · `tasks/briefs/s0-01-d5m-support/D5m-report.md` (ONE stamp line at its top,
item 7) · report `tasks/briefs/s0-01-d5n-support/D5n-report.md`. NOT yours: `pins.py`, `acp_probe.py` (N5j), the checker (A5l),
the tee (B5k), the PC tools (P5c), `.claude/hooks/*`, `scripts/*`. Shared-tree rules: never `git stash/checkout/restore/reset/add/commit/push`;
every gate from a `git archive <PIN> | tar -x` copy under your lane's scratch dir with your files copied in
(`scripts/lane_gate.sh -r <PIN> -f "<your files>" -t "tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py" -n 2`,
ONE foreground call, `LANE_GATE_DIR` under your scratch dir; about 3 minutes with `-n 8` on the PC); explicit `--basetemp`; every
FIFO/race probe standalone under `timeout 12` with the test's OWN watchdog (a thread that kills your helper process by pid) so a
regression can never hang the suite; kill only your own processes by pid (never pkill/pgrep -f); NEVER background a run and stop;
no outward actions; never read, print or commit a credential (the token file in every test carries a labelled non-secret).
Interpreter: the venue's venv python; venue exports `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`.
Authorization: the owner's own deterministic upstream stub under test on the owner's system.

## Design (pinned — build it, do not redesign it)
1. **F1/F2/token — ONE primitive, the open IS the classification.** Add `_create_exclusive(name: str, *, dir_fd: int | None,
   mode: int = 0o600) -> int` (an fd): `os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, mode, dir_fd=dir_fd)`;
   `FileExistsError` → the NAMED refusal (anything already at a predictable name is attacker-chosen: refuse, never overwrite —
   D5m's slot semantics, now for the pidfile too); every other `OSError` (`EISDIR`, `ELOOP`, `ENXIO`, `EACCES`, `ENOTDIR`) → the
   same refusal naming `errno`; then `os.fstat(fd)`: `S_ISREG` and `st_nlink == 1` or refuse (close the fd first). Writes go
   through the fd (`os.write` loop), never through the path. And its read twin `_open_regular_ro(path: Path) -> int`:
   `O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC`, `fstat` → `S_ISREG` or the named refusal; `load_token` reads through it. There
   is NO `_refuse_non_regular`, no `write_text`, no `open(<path>)` left in the backend; the startup `--record-dir` checks stay
   as checks of a DIRECTORY the backend then holds OPEN: at startup `mkdir` (idempotent) + `self.record_fd = os.open(record_dir, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC)`,
   and every slot is `_create_exclusive(f"{n:06d}.json", dir_fd=self.record_fd)` — a swapped record directory cannot redirect a
   slot. The per-request `mkdir` at `backend:567` goes.
   **Pinned decisions:** (a) a pidfile that already EXISTS — regular, symlink, anything — is REFUSED with
   `scripted_backend: --pidfile already exists: <path>` rc 2 (the two consumers, `pc_backend_restart.sh:7-11` and
   `run_s0_04_legs.sh:88-111`, own the stale-pid case: they remove a pidfile they have proven stale before relaunching — read both
   and state in the report whether they do; if one does not, say so as a NOT-done item for that consumer's owner, never widen the
   backend to overwrite); (b) a symlink at any of the three paths is refused (`O_NOFOLLOW` is what makes the open atomic against a
   swap; D5m's "a symlink to a regular file still starts" flips to a refusal — update that test and say why); (c) the FIFO-with-a-
   reader case is the reason the `fstat` exists: `O_NONBLOCK|O_WRONLY` on a FIFO whose read end is open SUCCEEDS, and only the
   `fstat` refuses it — that is a required test (the test holds the read end open, then asserts the named refusal).
2. **The race is closed STRUCTURALLY, and the structure is pinned.** There is no window to race, so the proof is (a) the in-process
   domain table for both primitives (import the backend as a module; for each of: absent → created; a regular file; a symlink to a
   regular file; a dangling symlink; a FIFO with no reader; a FIFO WITH a reader; a directory; a socket; a hardlinked regular file
   (nlink 2) — the exact outcome, every refusal named, every call returning within 100 ms — run standalone under `timeout`), and
   (b) an AST pin in `main`: the backend module contains exactly ONE `os.open` call with `O_CREAT` and it carries `O_EXCL`,
   `O_NOFOLLOW`, `O_NONBLOCK`; no `write_text`/`write_bytes`/bare `open(` call anywhere in the module; `_refuse_non_regular` absent.
   Plus the registry screen by RUN: `python3 scripts/ap_screen.py --s0-01` must report ZERO AF-AP-70 hits on
   `scripted_backend.py` (today it reports three — paste both runs). The subprocess-level tests stay: a FIFO at the next slot →
   one 500 `record_slot_unusable` within 5 s and the next request 200; a FIFO/directory/dangling-symlink/socket pidfile → rc 2
   with the exact line and the port unbound; the refusal-precedes-bind test unchanged.
3. **F3/F4 — the drain is bounded and the live-pipe branch is pinned.** `_drain(proc, budget_s=2.0)`: after `proc.poll()` is not
   None, put both fds non-blocking (`os.set_blocking(fd, False)`) and read with `select` until EOF or the budget, then append
   `<stdout held open by a descendant; drained N bytes in {budget}s>` when it ran out. Red test (RED on the PIN — paste the
   watchdog's kill): a helper script that spawns `sleep 30` inheriting its stdout and exits 0 → `_wait_ready` raises
   `AssertionError` within 3 s naming rc 0; the test's watchdog kills the sleeper by pid in `finally`. Live-pipe pin: a helper that
   is alive and holds its pipe → `_drain` returns the marker without reading (a mutant that deletes the `proc.poll()` branch at
   `main:64-65` blocks → the watchdog's failure is the kill).
4. **F5 — the ban names the file it cannot parse.** `red:1212` (`ast.parse`): `try: tree = ast.parse(path.read_text()) except SyntaxError as exc: pytest.fail(f"cannot parse {path}: {exc}")`.
   Test: a scratch malformed matched file → the failure message carries its path.
5. **F6 — the walker's reach stated from a measured table.** Paste the verifier's 23-spelling table re-run on the final bytes (the
   number caught, the number missed, the positive control at 0) and rewrite the `OUT OF SCOPE` text (`red:1198-1203`) to name EVERY miss: the aliasing
   family, `match` statements, the affirmative `if x == MARKER: raise`, the length-zero `x in (MARKER,)` form. Documented, not
   closed — say so.
6. **F8/F9/F10 — one true table.** The docstring's cost numbers (`backend:77-82`) appear in ONE pasted `cost_probe.py` table in your
   report with the venue and load before/after; the D5m table's 1.52/0.56 line is superseded (item 7). "18 textual `_free_port`
   occurrences = 16 calls + 2 definitions" in your report. pyflakes: run it from the venue's venv (`<venv>/bin/python -m pyflakes`);
   if the venv lacks it, the report says `NOT run: pyflakes absent on this venue` — never `compileall` in its place.
7. **The D5m report stamped**, one line at its top: `STAMP 2026-09-08 (D5n): the cost table's PC cells (1.52/0.56) are superseded by D5n's table; "18 call sites" = 16 calls + 2 definitions (VERIFY-D5m F8/F9).`
8. **Mutants — the two survivors become killers, the old set stays dead.** Required, each with the killer line pasted:
   `EXCL-DROPPED` (a regular file planted at the next slot is overwritten — killed by the refusal test), `NOFOLLOW-DROPPED` (a
   symlink at the slot/pidfile written through — killed), `NONBLOCK-DROPPED` (a FIFO with no reader blocks — killed by the
   watchdog), `FSTAT-DROPPED` (the FIFO-with-a-reader passes — killed), `NLINK-DROPPED` (a hardlinked pre-existing file passes —
   killed), `DIRFD-DROPPED` (the slot created by path — killed by the AST pin), `DRAIN-UNBOUNDED` (the budget removed — killed),
   `LIVE-PIPE-DELETED` (killed), `PARSE-UNWRAPPED` (killed); then D5m's 33 rows and VERIFY-D5m's named killers (PIDFILE_*,
   RECSLOT_*, WAITREADY_*, BAN_*, the fidelity set, UQ_REPLACE_BOTH) re-run and still dead. Every mutant on a scratch copy.
9. **Report discipline:** FILE IDENTITY of the FINAL bytes; every `file:line` from `grep -n` on the FINAL bytes and
   `python3 scripts/report_lint.py <report> --map backend=proofs/S0-01/tools/scripted_backend.py --map main=tests/test_s0_01_scripted_backend.py --map red=tests/red/test_s0_01_backend_credential_screen.py`
   pasted with MISS 0; the two gate RESULT lines pasted; every red-before on the PIN pasted beside its green-after; `ap_screen.py`
   on the backend (AF-AP-70 = 0, the remaining rows classified by run) and `--tests` on both test files; the pack attached;
   NOT-done first-class. NOT this lane's: the probe's primitive (N5j), the shared primitive's home in `pins.py` (the coordinator,
   after N5j and D5n both land), the AF-AP-61b registry screen, the two pidfile consumers' stale-pid handling.
