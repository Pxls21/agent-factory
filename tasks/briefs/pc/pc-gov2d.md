# PC lane — GOV2d (the ONE focused repair of VERIFY-GOV2c's two blockers in the review binding: the gpg trust root off the caller's PATH; the FIFO window after the pathname pre-check closed on the FD)

PIN: 2da04bf

Role: code-implementer. Route: the LOCAL build route (`agentfactory-build-local`, the vLLM server default effort; the route is
HYBRID in practice — the cloud step serves a turn when the local step refuses with the chat-template 400 — say so in the report
header, claim nothing about which model produced the code). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Honey mode:
ultra, Lever-2: the report is DATA (files:lines, verbatim counts, pasted assertions, NOT-done). Keep your context small: bounded
terminal output (`| tail -n 40`), the report drafted after each item, never a whole-file read where `sed -n` of a range answers.

AUTHORIZATION: defensive work on the owner's own governance code. The scripted `gpg` doubles and the FIFO fixtures live only in
pytest temp directories and are never installed or left behind; no production service, credential, committed key or server is
touched; the committed owner key is never used to sign anything.

## THE CONTRACT (D-031: ONE focused repair — component GOV2 · contract revision = the master brief `tasks/briefs/pc/pc-verify-gov2c.md`
items 5 and 6 · production digest RV `010054c04f697c8c` at the PIN). Anything outside items F1/F2 below is OUT of scope: issue #18
(six surviving mutants, duplicate JSON members, the owner-key deployment path, the gpg-agent census), PK, every other file.

Boundary (edit ONLY these three):
- RV `src/agent_factory/governance/review.py`
- TR `tests/test_governance_review.py`
- RM `docs/governance/reviews/README.md`
Read-only context: PK `src/agent_factory/governance/packet.py` (the sole production consumer: `load_packet` → `verify_review` at
PK:155 — never passes a gpg path; do NOT edit PK), the two verifier reports `tasks/briefs/stage3-governance-support/VERIFY-GOV2c-B-report.md`
(items 5, 6: F1, F2, the exact discriminators) and `…/VERIFY-GOV2c-C-report.md` (item 10: the reason taxonomy table you must keep true).

## PREMISE — MEASURED at authoring (2026-09-22 10:5xZ, the sandbox clone; the four files are byte-identical from dab9803 to the PIN); re-measure as item 1

```
sha256 first-16 at the PIN: RV 010054c04f697c8c · TR ea9e0a466a4807d2 · RM 662fd187a827461b · PK 5d8cf21468adb55e
git log --oneline dab9803..2da04bf -- RV TR RM PK → 0 commits
RV:51  def _read_no_symlink(path: Path) -> bytes:
RV:53      fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)          ← no O_NONBLOCK, no fstat: a FIFO planted at t1 blocks here forever
RV:109     if not record_path.is_file() or not sig_path.is_file():   ← the pathname pre-check (t0); absence → fubuki-packet-unreviewed
RV:114     gpg = shutil.which("gpg")                                 ← F1: the CALLER's PATH picks the verifier
RV:116         raise GovernanceError("fubuki-review-gpg-unavailable", "gpg is not on PATH")
RV:122-124 record_bytes / sig_bytes / owner_key_bytes = _read_no_symlink(...)   ← the three opens (t1)
RV:126         raise GovernanceError("fubuki-review-record-invalid", str(exc)) from exc
RV:136         env = {"GNUPGHOME": home, "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C"}   ← F1: the caller's PATH forwarded
RV:22-23   docstring: "gpg runs by absolute path with --no-options and a minimal environment, so an ambient gpg.conf or a
           PATH-shadowed gpg is not a trust channel (F5)" — FALSE today (B item 5); rewrite it to what the code does after this lane
RV:78-85   _keyring_shape parses `pub:` / `fpr:` colon lines (field 9 = fingerprint); RV:156-164 accept only a `[GNUPG:] GOODSIG ` LINE
           whose `[GNUPG:] VALIDSIG <fpr>` fingerprint is in that keyring set and gpg's rc is 0
TR:264     monkeypatch.setattr(shutil, "which", lambda name: None)  ← the ONE test that assumes PATH resolution (rewrite it, item 3)
TR: 16 tests; the `keys` fixture (TR:75) makes throwaway keys in its own GNUPGHOME and kills its own agent (TR:70)
sandbox 2026-09-22T10:50:33Z  tests/test_governance_review.py → 16 passed in 1.43s (rc 0)   set ce6a68f1998d
sandbox 2026-09-22T10:50:36Z  the six-file governance set → 49 passed in 1.79s (rc 0)          set f3baa8cf79c7
   (FUBUKI_OS_ROOT + FUBUKI_OTHER_ROOT exported — DECLARED inputs of the governance tests; omitted = 16 errors, never a green)
VERIFY-GOV2c-B (PC, gpg 2.4.7): a scratch gpg FIRST on PATH → the real verify_review ACCEPTED an unsigned record; /usr/bin/gpg
   → REFUSED fubuki-review-signature-invalid; a 0600 FIFO swapped in after the pre-check → `timeout 10` rc 124, wall 10003 ms (twice)
gpg-agent census through the real function: 0→0 on the PC's 2.4.7 and on the sandbox's 2.4.4 — the AF-AP-110 cleanup is NOT built here
```

## ITEMS

1. **Re-measure the premise** at the PIN (the digests, the 0-commit log, the anchor lines by `grep -n`, both test sets with the
   FUBUKI exports) and paste it under `## PREMISE — RE-MEASURED` in your report. A mismatch = STOP, report `CONTRACT-INVALID`.

2. **F1 — the gpg executable is a FIXED trust decision, never the caller's PATH (RV).**
   - Module scope: `_GPG_PATHS: tuple[str, ...] = ("/usr/bin/gpg", "/usr/bin/gpg2")`, documented as THE trust root: a distro
     binary at an absolute path. `shutil` leaves RV entirely (`grep -n 'shutil\|os.environ' RV` → 0 lines after the change; paste it).
   - `verify_review(governance_hash, *, reviews_dir=None, owner_key=None, gpg: str | Path | None = None)`. Resolution: an EXPLICIT
     `gpg` must be an absolute path to a regular file (`Path.is_absolute()` and `is_file()`), else
     `GovernanceError("fubuki-review-gpg-unavailable", f"gpg must be an absolute regular file: {gpg}")`; when omitted, the first
     `_GPG_PATHS` entry that is a regular file; none → `GovernanceError("fubuki-review-gpg-unavailable", "no gpg at " + ", ".join(_GPG_PATHS))`.
     The parameter's docstring says: production (`load_packet`) never passes it; it exists so a TEST can point at a scripted gpg
     deliberately; it is a code decision, never read from the environment.
   - The child environment is exactly `{"GNUPGHOME": home, "PATH": "/usr/bin:/bin", "LC_ALL": "C"}` — the PATH a fixed literal.
   - Rewrite the RV:22-23 docstring sentence to the truth: the executable is one of `_GPG_PATHS` (or a path the CALLER's CODE passes),
     the child PATH is fixed, so neither a PATH-shadowed `gpg` nor an ambient `gpg.conf` is a trust channel.

3. **F2 — the read primitive proves a REGULAR FILE on the FD and never blocks (RV).**
   - Rename `_read_no_symlink` → `_read_regular_file(path)`: `fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)`;
     then `st = os.fstat(fd)`; `if not stat.S_ISREG(st.st_mode): raise OSError("review record is not a regular file")` (this EXACT
     text — a test pins it); then the capped read exactly as today (the cap, the `finally: os.close(fd)`). `import stat`.
   - All three reads at RV:122-124 use it (record, signature, owner key) — the F8 symmetry; the `except OSError` mapping at RV:126
     is unchanged (→ `fubuki-review-record-invalid`, detail = the OSError text).
   - The pathname pre-check at RV:109 STAYS (absence → `fubuki-packet-unreviewed`). The taxonomy is now two-level and must be
     written into RM (item 5): a non-regular NAME at t0 (directory, socket, device, FIFO, missing) → `fubuki-packet-unreviewed`;
     a non-regular FD at t1 (planted between the pre-check and the open) → `fubuki-review-record-invalid: review record is not a regular file`.

4. **Tests (TR) — every new test through the REAL `verify_review` + real gpg (the existing `keys` fixture + `_write_review`);
   named EXACTLY as below; each new test is RED at the PIN for the reason stated (run it against the unmodified RV first — a
   scratch copy or `git stash` is NOT allowed on the shared tree: run the red BEFORE you edit RV, paste the FIRST failing assertion
   line per test with `--tb=short`, AF-AP-114), then GREEN after your change.**
   - `test_gpg_is_never_resolved_from_the_callers_path` — a scratch `fake-bin/gpg` (a bash or python script, mode 0755) FIRST on
     PATH via `monkeypatch.setenv("PATH", f"{fake_bin}:{os.environ['PATH']}")`. The fake: touches a sentinel file `fake-bin/RAN`
     when executed; `--import` → exit 0; `--list-keys …` → prints `pub:u:255:22:0123456789ABCDEF:::::::::` and
     `fpr:::::::::0123456789ABCDEF0123456789ABCDEF01234567:` and exits 0; `--verify` → writes
     `[GNUPG:] GOODSIG 0123456789ABCDEF fake` and `[GNUPG:] VALIDSIG 0123456789ABCDEF0123456789ABCDEF01234567 2026-09-22 0 0 0 0 0 0 22 01 0123456789ABCDEF0123456789ABCDEF01234567`
     to the fd named by `--status-fd` and exits 0. The record is owner-shaped (`_write_review`) but its `.asc` is REPLACED by 8 bytes
     of garbage (UNSIGNED). Assert `GovernanceError` with reason `fubuki-review-signature-invalid` AND `not (fake_bin / "RAN").exists()`.
     RED at the PIN: `verify_review` RETURNS (B's exact discriminator) — paste `Failed: DID NOT RAISE` (or the sentinel assertion).
   - `test_a_hostile_path_does_not_break_the_real_gpg` — the same hostile PATH, an owner-signed record → returns (accepted). The
     positive control: the fixed child PATH suffices for the real gpg. (GREEN at the PIN too — say so; it guards item 2's PATH literal.)
   - `test_the_child_path_is_fixed` — `gpg=<scratch script passed EXPLICITLY, absolute>` that writes `os.environ.get("PATH")` to a
     file beside it and exits 1; the caller's PATH set hostile first; call `verify_review(..., gpg=script)`; expect a `GovernanceError`
     whose reason starts with `fubuki-` (the import fails: `fubuki-owner-key-invalid`) AND the dumped PATH == `"/usr/bin:/bin"`.
     RED at the PIN: `TypeError` (no `gpg` parameter) — paste it.
   - `test_an_explicit_gpg_must_be_an_absolute_regular_file` — three calls: `gpg="gpg"`, `gpg=tmp_path / "missing"`,
     `gpg=tmp_path` (a directory) → each `fubuki-review-gpg-unavailable`. RED at the PIN: `TypeError`.
   - `test_gpg_absent_raises_a_governance_error` REWRITTEN (TR:259-266): `monkeypatch.setattr(review, "_GPG_PATHS", (str(tmp_path / "no-gpg"),))`
     (import the module as `review`) → `fubuki-review-gpg-unavailable`; the `shutil.which` monkeypatch is deleted.
   - `test_a_fifo_swapped_in_after_the_precheck_is_refused_not_hung` — `monkeypatch.setattr(Path, "is_file", wrapper)` where the
     wrapper calls the original and, the FIRST time it is asked about the record path, then unlinks the record and
     `os.mkfifo(record, 0o600)` before returning the original answer (True). Call `verify_review` under a HARD guard:
     `signal.signal(signal.SIGALRM, handler)` raising `TimeoutError("hung")` + `signal.alarm(10)`, cleared in `finally`.
     Assert `GovernanceError` reason `fubuki-review-record-invalid` and `exc.value.detail == "review record is not a regular file"`,
     and wall time < 5 s. RED at the PIN by the guard: paste `TimeoutError: hung` (the guard's line, never a count).
   - `test_a_fifo_swapped_in_for_the_signature_is_refused_not_hung` — the same wrapper keyed on the `.asc` path.
   - `test_a_fifo_at_the_record_path_is_unreviewed` — a plain FIFO at the record path, no race → `fubuki-packet-unreviewed`
     (the pre-check's reason; GREEN at the PIN — say so; it pins the two-level taxonomy).
   - Keep every existing test; the symlink test (`test_a_symlinked_record_is_refused`) still passes (O_NOFOLLOW kept).

5. **RM** — a short new section `## What the verifier trusts` (the fixed `_GPG_PATHS`, the fixed child PATH, the explicit
   `gpg=` parameter for tests only) and the two-level non-regular-file taxonomy (item 3); the existing owner step is unchanged.

6. **Mutation rows (≥ 8, one at a time on a SCRATCH COPY of RV under the lane dir — never the worktree file — with a
   pytest run that imports the scratch copy: prove the import with a printed `__file__` FIRST, the C lane's VOID run was exactly
   this trap; every mutant compiled with `python -m py_compile` and collected before it runs, AF-AP-78):**
   m1 restore `shutil.which("gpg")` as the resolver → `test_gpg_is_never_resolved_from_the_callers_path` red;
   m2 child PATH = `os.environ.get("PATH", …)` → `test_the_child_path_is_fixed` red;
   m3 drop `os.O_NONBLOCK` → both FIFO-race tests red by the guard;
   m4 drop the `S_ISREG` check → the FIFO-race tests red on the DETAIL (`Expecting value` instead of `review record is not a regular file`);
   m5 `_GPG_PATHS = ("gpg",)` → `test_a_hostile_path_does_not_break_the_real_gpg` red (`fubuki-review-gpg-unavailable`);
   m6 accept a relative explicit `gpg` (drop `is_absolute()`) → `test_an_explicit_gpg_must_be_an_absolute_regular_file` red;
   m7 drop `os.O_NOFOLLOW` → `test_a_symlinked_record_is_refused` red (unchanged coverage);
   m8 `os.fstat(fd)` → `os.stat(path)` — NOT killed by these tests (the t1→t2 window is not forced): report it as a DECLARED LIMIT
   paired with a source-shape pin you add to TR (`"os.fstat(fd)" in inspect.getsource(review)` + the m8 line) and say the pin is
   the AF-AP-80 pairing, not a behavioral proof.
   Paste each row's `1 failed …` line with the failing test's name; a row that does not fail = a finding, never silently dropped.

7. **Screens** — `python3 scripts/ap_screen.py src/agent_factory/governance/review.py | grep -c 'AF-AP-115'` → `0` (the AF-AP-115
   row fires on `shutil.which(` and on `os.environ…("PATH"`; paste the line), and the whole-file screen's other hits unchanged
   from the PIN (paste the PIN's count and yours). `python -m pyflakes` on RV and TR → 0 lines if pyflakes is in the venv (say
   if it is not).

8. **Gates on the PC (every call under the 420 s terminal cap; xdist installed):**
   `export FUBUKI_OS_ROOT=/home/rocco/fubuki-pin/fubuki-os FUBUKI_OTHER_ROOT=/home/rocco/fubuki-pin/fubuki-os-other` (DECLARED
   inputs — verify both exist first) and `--basetemp <lane dir>/bt` (NEVER `/tmp` — it is a tmpfs with an inode budget, AF-AP-112;
   a short path so gpg's socket fits — under 60 characters):
   (a) `python -m pytest -q -p no:cacheprovider -n 4 --basetemp <lane>/bt tests/test_governance_review.py` — TWICE, the counts must
   agree; paste both lines + rc via `${PIPESTATUS[0]}`;
   (b) the same, serial (no `-n`), ONCE (the alarm-guard tests run in the main thread here — say both shapes pass);
   (c) the six-file set spelled EXACTLY `tests/test_governance_bounds.py tests/test_governance_packet.py tests/test_governance_pin.py tests/test_governance_pin_enforcement.py tests/test_governance_projection.py tests/test_governance_review.py`
   with `-n 4`, once; paste the line beside the set id `f3baa8cf79c7` (`bash scripts/pc_suite.sh set-id -- <the six paths>` is the
   sandbox spelling — on the PC compute it as `sha256("\n".join(sorted(files)) + "\n")[:12]`, the C lane's formula, and paste it);
   (d) a before/after `gpg-agent` census around ONE run of (a): `pgrep -fa '[g]pg-agent --homedir <lane>/bt' | wc -l` — paste both
   numbers (expected 0 and 0; a non-zero after is a FINDING, not something to clean silently; kill only agents whose homedir is
   under YOUR lane dir, by pid).

9. **Report** `tasks/briefs/stage3-governance-support/GOV2d-report.md` (draft after every item): the RE-MEASURED premise, every
   hunk as files:lines, the red-first assertion text per new test (item 4), the mutation table (item 6), the screens (item 7), the
   pasted gate lines with set ids (item 8), NOT-done (issue #18 is NOT touched — list what a reader might expect and did not get).
   Lint: `python3 scripts/report_lint.py tasks/briefs/stage3-governance-support/GOV2d-report.md --rev 2da04bf --map RV=src/agent_factory/governance/review.py --map TR=tests/test_governance_review.py --map RM=docs/governance/reviews/README.md --map PK=src/agent_factory/governance/packet.py --min-refs 12`
   (`--map` is REPEATED, one `ALIAS=path` per flag) — at most three fix rounds, then paste and finish (AF-AP-76). Cite YOUR new
   lines with the plain path (they do not exist at the PIN) and the PIN's lines with the aliases.

## VENUE NOTES (this host)

- The lane worktree is at the PIN; you edit RV/TR/RM in it; the dispatcher harvests your diff — do not commit, stash, checkout or
  push; do not create a scratch copy of the whole tree (a boundary copy of RV alone for item 6 is fine, under the lane dir).
- The venv python is `/home/rocco/venv-agent-factory/bin/python`; pyproject's `pythonpath = ["src"]` resolves the package from the
  worktree for pytest — for the mutation runs use an EMPTY `-c <lane>/pytest-empty.ini`, the scratch cwd and the absolute test path
  (the C lane's fix), and print `review.__file__` inside the run.
- `gpg` is `/usr/bin/gpg` 2.4.7 on this host. Never touch `~/.gnupg`; the tests' homes are pytest temp dirs.
- Never touch any production service (OmniRoute, the vLLM `qwen` container, `buzz-prod-*`, Ollama, Phoenix, OpenObserve, neo4j).
- CODE INTEL FIRST (the dispatcher injected the rule): `graft ask` on `verify_review` and `_read_no_symlink` callers before editing
  (expected: `load_packet` at PK:155 the sole production caller; the tests the rest); ripwire `callers` as the second instrument.
