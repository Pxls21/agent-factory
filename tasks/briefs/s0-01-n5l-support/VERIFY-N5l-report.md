> **COORDINATOR DISPOSITION (2026-09-15 16:0xZ).** F1/F3 registered as AF-AP-85 / AF-AP-84 (the driver sweep: A5l and A5m share F3's
> shape, GOV1 pins a literal); F1-F4 go to probe round 16 (N5m). V7's premise was the coordinator's brief error — the probe test file
> reads no corpus; the declared-input fail/skip contract lives in the checker and pc-tools suites. No verdict was expected (single-model rule).

NO VERDICT (single-model rule): findings only

Maps: probe=proofs/S0-01/tools/acp_probe.py; test=tests/test_s0_01_acp_probe.py; driver=tasks/briefs/s0-01-n5l-support/mutants.sh. FINAL bytes equal 8b387d2: P `f42a9025…135ec6b2` / 678 lines; T `6d5da2b…e2d65e5` / 3868 lines; D `376105a…1b39bd` / 141 lines.

FINDINGS

1. HIGH — V2 census does not prove the stated general fd-containment property. test:3820-3836 `CENSUS_AGENT` enumerates all child fds but increments only when an inherited descriptor resolves to the framedir. probe:371-374 `proc` is the real Popen, but a different parent pipe descriptor inherited through that exact Popen remains invisible to `CENSUS=0`. In a scratch P copy, I created an inheritable `os.pipe()` read end before Popen and changed probe:373 `stderr` to `close_fds=False`; a census agent counted `PIPES=4`, vs `PIPES=3` on landed bytes, while the landed framedir-only census would still print `CENSUS=0`. Concrete failing input: an inheritable non-framedir pipe fd. Minimal fix: rename the test/property to “no framedir fd” and document the deliberate limit, or make the agent enumerate and assert an expected allowlist of inherited fds. The claimed framedir-specific property itself holds; the broad “fd census” wording does not.

2. MEDIUM — V4 AST pin has a false-red maintenance limitation. test:3587-3601 walks the entire AST and selects every `proc = subprocess.Popen(...)`, including ones in nested functions. A scratch P copy containing an otherwise unused nested helper with its own safe literal-True `proc` launch made the pin red: `expected one agent Popen assigned to proc, got 2`. This does not create a false green, but a semantically safe helper makes the gate reject a correct production launch. Minimal fix: constrain selection to the top-level body of `main` (or document the intended module-wide single-Popen invariant and test that exact scope).

3. MEDIUM — V5 driver can silently lower the mutation denominator. driver:138 computes `expected` from executed rows rather than pinning the contractual ten. Deleting one row in a scratch driver returned `EXPECTED=9 KILLED=9 SURVIVED=0 INVALID=0 CONTROL=1`. Concrete failing input: deletion of any one required mutation row. Minimal fix: assert the immutable expected row count before accepting the zero-survivor result.

4. LOW — V4 short-socket fixture leaks its temporary directory when an assertion after allocation fails. test:3718-3733 calls `mkdtemp` then removes the directory only at the final normal-path line. A scratch forced assertion created a new `/tmp/n5l-sock-heg4h1sh` that remained after pytest; I removed only this lane-owned artifact. Minimal fix: use a `finally` cleanup or a pytest temporary path short enough for AF_UNIX.

V1 — SOLID (reproduced)

- Landed: `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden python -m pytest -q T --basetemp=.../v1-landed` → `124 passed in 51.79s`; `scripts/test_summary.sh T` independently returned `124 passed in 51.03s`, and `pc_suite.sh set-id -- T` returned `1 files set=a5097bab1417`.
- Scratch P removed `O_NOFOLLOW` from probe:62; whole-file result: `3 failed, 121 passed in 53.99s`. Reds: test:3656 `test_probe_read_regular_refuses_final_symlink_with_eloop`, test:3676 `test_probe_fixture_reader_refuses_final_symlink_at_outer_boundary` (`rc=0` instead of `64`), and test:3790 `test_probe_read_primitive_mutants_die_at_the_open_level` `tmp_path` (the helper correctly reports its anchor absent in an already mutated tree). An independent direct `os.open` without O_NOFOLLOW printed `open_without_O_NOFOLLOW=success bytes=x`.
- Landed test:3656 `test_probe_read_regular_refuses_final_symlink_with_eloop` asserts ELOOP/no returned bytes and test:3676 `test_probe_fixture_reader_refuses_final_symlink_at_outer_boundary` asserts `rc=64`, exact stderr, empty stdout and no evidence state. Both direct and real caller-chain guards therefore die under the mutation.

V2 — SOLID for framedir containment; finding above for its broader name

- test:3852-3868 `test_probe_census_agent_sees_no_framedir_fd_on_final_bytes` calls test:239-254 `_run_probe`, which subprocesses P; probe:371-374 `proc` launches the census agent through the production Popen. Landed requires exact `CENSUS=0\n`.
- driver:23 plus driver:74-79 `FD_LEAK_TRIPLE` removes framedir O_CLOEXEC, makes that fd inheritable, and sets `close_fds=False`. The independently rerun driver returned `EXPECTED=10 KILLED=10 SURVIVED=0 INVALID=0 CONTROL=1`; its FD_LEAK_TRIPLE killer is test:3852 `test_probe_census_agent_sees_no_framedir_fd_on_final_bytes`.
- Scratch `close_fds=False` alone: census test passed and the AST pin red (`got False`). This is expected because the framedir fd remains non-inheritable. The stronger scratch inherited-pipe mutation exposed the scoped-census blind spot described in Finding 1.

V3 — SOLID, with the V4 maintenance finding

- test:3583-3612 `_agent_popen_close_fds_value` selects the direct `proc = subprocess.Popen` and rejects `**kwargs`; test:3615-3636 `test_probe_agent_launch_pins_the_close_fds_default_second_defence` requires exact literal True. Scratch outcomes: False → `got False`; `bool(1)` → `got 'non-literal'`; `**opts` → `must not hide close_fds`; an alias `run = subprocess.Popen; proc = run(...)` and `from subprocess import Popen; proc = Popen(...)` each red with `got 0`; absent keyword red with `must have exactly one close_fds keyword`; comment-only False red.
- The pin is stricter than the earlier “absent or True” shape: probe:371-374 `close_fds=True` now makes omission impossible. No other P launch shape exists in landed bytes, so this is deliberate hardening, not a current defect.

V4 — SOLID with a cleanup limitation outside landed behavior

- test:3709-3715 `test_probe_read_primitive_reads_a_regular_file` exact regular bytes and test:3737-3768 `test_probe_read_primitive_refuses_named_non_regular_shapes` exact FIFO/directory/devzero/socket errors passed: `6 passed in 0.06s`. Expectations are independently written literals / runtime errno formatting, not sourced from P.
- test:3771-3787 compares pre/post `/proc/self/fd` sets and exact FIFO refusal.
- test:3718-3733 twice reproduced the long AF_UNIX failure and the short-path success: `1 passed in 0.05s` each. A deliberately forced assertion failure after `_short_unix_socket_path()` left its new `/tmp/n5l-sock-*` directory behind, which required manual deletion. This is test-fixture cleanup debt, not a failure in a successful landed test; the lane owned only the manually created leftover from that hostile probe and removed it. A pre-existing `/tmp/n5l-sock-krgsc7am` remained untouched.

V5 — SOLID

- driver:81-100 `set +e` compiles and collect-only validates each mutated tree before grading; driver:102-110 `timeout` bounds the FIFO run with `timeout 15s`. An augmented scratch driver import-raise row produced `KILLED IMPORT_RAISE`, with the primary error `RuntimeError: N5L_IMPORT_SENTINEL` at probe:39 `_EARLY_SAMPLE_DEADLINE_S`; it was imported, not a false test filter.
- Landed D run output: all ten named rows KILLED; CONTROL_GREEN; `EXPECTED=10 KILLED=10 SURVIVED=0 INVALID=0 CONTROL=1`.
- A scratch driver with one of the ten rows deleted reported `EXPECTED=9 KILLED=9 SURVIVED=0 INVALID=0 CONTROL=1`. Thus driver:138 derives expected from executed rows and does not enforce the contract’s required ten rows. The committed driver currently has ten rows, but a future deletion can silently lower its denominator. Minimal fix: add an immutable expected-row count, e.g. `[[ $expected -eq 10 ]]`, before accepting the summary.
- READ_NONBLOCK_DROP is intentionally killed by timeout 124. probe:62 without O_NONBLOCK can block on the writer-less FIFO. The timeout honestly detects a liveness regression but does not distinguish a hang from another nonzero failure; retain the bounded timeout and print a dedicated timeout classification if exact diagnosis is required.

V6 — SOLID, scoped evidence only

- test:3825-3834 `target` excludes stdio only incidentally (they resolve as pipes), ignores an fd if readlink races, and counts a descriptor only when its target is a directory whose realpath equals framedir. The census output file is opened only after the loop at test:3835-3836 `handle`; the stdin/stdout/stderr parent pipes and any other non-directory fd are excluded. This is the declared blind spot in Finding 1.

V7 — DISCREPANCY (brief premise does not match this file)

- `T` has no `S0_01_REAL_LEG_DIR` or `S0_01_VENUE` read. With the declared golden corpus, with an empty directory, and with `S0_01_VENUE` unset, the same file ran `124 passed` each time. The real-leg declared-input fail/skip contract is in other suites, e.g. `tests/test_s0_01_check_acp_conformance.py:2629-2655` and `tests/test_s0_01_pc_tools.py:40-52`, not T. I stopped after the three mandated variants; this brief’s demand for an empty-corpus failure / CI skip cannot be met by the named probe file.

V8 — SOLID static inventory

- Literal sweep of P shows only three operational file-open seams: probe:63 `fd = os.open` in `_read_regular`; probe:111/probe:115 `fd = os.open` in `_open_regular` for evidence writes; probe:326 `framedir_fd = os.open` for the directory. probe:89, probe:141, probe:217, probe:399, probe:471 and probe:566 route file reads through `_read_regular` via `_sha256_file`; probe:282 routes the fixture through `_read_regular`. probe:111/probe:115 are evidence writes and probe:326 is a directory fd, not contract read receivers. No remaining P `read_bytes`/`read_text` calls exist.

V9 — verified mechanics and static gates

- `git diff --quiet 8b387d2 -- P T D` → rc 0. `git diff --check`, pyflakes on P/T, and `bash -n D` → rc 0.
- `python3 scripts/ap_screen.py`: P has 8 pre-existing hits (AF-AP-55 x3, AP-1 x2, AP-32 x2, AP-24 x1); T has 5 pre-existing hits (AF-AP-80 x4, AF-AP-57 x1); D has deliberate AF-AP-70 lexical fixture at driver:22 `CLOSE_BEFORE_FSTAT`. No N5l-added hollow-green pattern was established by this screen.
- Code mapping: graft maps probe:48 `_read_regular` into probe:81 `_sha256_file` and probe:253 `main`; ripwire confirms those three caller symbols, but its count is a floor. GitNexus clone index is 119 commits stale and returns `_read_regular` not found/risk UNKNOWN; therefore it is not used as an absence claim. `detect-changes` on this staged lane patch reported `No changes detected`, because it compares this worktree patch rather than the landed N5l commit.

NOT DONE

- No sandbox-side independent adversarial grade or gate verdict.
- No live Buzz, ACP, Hermes, OmniRoute, corpus mutation, service action, commit, push, tag, or proof artifact.
- No 13-file suite rerun: this brief requires the targeted file plus the specific mutations; builder-reported larger-set evidence remains unverified here.

DISCREPANCIES

- V7’s corpus fail/skip premise names the wrong suite; commands and `124 passed` results are above.
- The initial hostile direct `os.open` probe used an invalid relative scratch path and failed before its intended test. I corrected it with a lane-absolute scratch directory; `open_without_O_NOFOLLOW=success bytes=x`.
- The prompt’s `test ! -e /tmp/n5l-sock-*` form is not a reliable glob-empty test when unmatched: the wildcard is literal. I used `find` for the inventory. The forced-failure cleanup probe demonstrated fixture leakage; the successful path leaves no new entry.

RETRO

- Real defect found: a census whose name claims general fd containment but counts only framedir directory fds is a scope/name mismatch. Anti-pattern: observation scope narrower than claim. The coordinator should run bug-echo and register it before accepting any fix.
- General workflow lesson: driver totals derived solely from executed rows cannot enforce a contractual row count. This belongs in anti-hollow-green / build-loop guidance.

LINT SUMMARY

Final bounded `report_lint.py` run (three rounds maximum; maps `probe`/`test`/`driver`; `--min-refs 15`):

`report_lint: 50 refs — OK 50, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`
