# N5i — S0-01 ACP probe, round 12: the WRITE class closed at every receiver, the probe's own file guarded, the blocking drain named, the AST self-scan over reads AND writes, and an honest class table

PIN: `088efef` (`088efef22b1eec2751166d5ffaabcffd8490b2b9`). Brief:
`tasks/briefs/s0-01-n5i-probe-the-write-class-and-the-honest-table.md` (committed in `4be637b`, an ancestor).
Contract read whole before any edit: `VERIFY-N5h.md` (697 lines). The probe's bytes at the PIN equal checkpoint 8z
(`b4257f8`): verified `c1a9e173…` / `f77bda15…` before the first edit.

Scope held exactly: `proofs/S0-01/tools/acp_probe.py`, `tests/test_s0_01_acp_probe.py`, this report. No other repo file
was written. No `git stash/checkout/restore/reset/add/commit/push`. No PC bridge call. No outward action.

## FILE IDENTITY (the FINAL bytes — pasted from `scripts/lane_gate.sh`)

```
3278ae2dc54eee83d384b4b86ddf6674ffaecb96bacf0d8e713a5344137ebf33  proofs/S0-01/tools/acp_probe.py  608 lines
117afaa061fae00042db3c1ab09fc9134f4d148c7c0743e769e5be7df8a82408  tests/test_s0_01_acp_probe.py  3023 lines
```
PIN was 520 / 2372 lines. Test count: `100 passed in 47.80s` on the probe file alone (PIN: 80), `155 passed` on the
declared set (PIN: 135) — every number pasted from `scripts/test_summary.sh`, none typed.

## What changed, by receiver (every line number from `grep -n` on the FINAL bytes)

| item | change | file:line |
|---|---|---|
| F5 | `_open_regular(path, mode)` — the one write primitive: `O_WRONLY\|O_CREAT\|O_TRUNC\|O_NOFOLLOW\|O_NONBLOCK`, `S_ISREG` on the OPEN fd, `O_NONBLOCK` cleared, refusal named | `probe:62` |
| F5 | all seven reachable write receivers routed through it | `probe:116` `with _open_regular(stderr_path, "wb") as f:` (drain) · `probe:144` `with _open_regular(os.path.join(framedir, "env.json"), "w") as f:` (env.json) · `probe:185` `with _open_regular(os.path.join(framedir, "runtime-identity.json"), "w` (rid) · `probe:193` `with _open_regular(tl_path, "w") as f:` (timeline) · `probe:295` (the timeout-reject rid) · `probe:576` `with _open_regular(path, "w") as f:` (`_m3_write`, used for the M3 rid, timeline and the stderr touch) |
| F4 | the probe's own file hashed ONCE at import inside a `try` → `_PROBE_PATH` / `_PROBE_SHA256` / `_PROBE_SHA256_ERROR` | `probe:95`, `probe:99` `except Exception as _exc:   # OSError today; an import must never fail` |
| F4 | both identity writes read the cached values; a `None` hash is a NAMED `probe_error` | `probe:159`, `probe:170` `"probe_sha256": _PROBE_SHA256,`, `probe:554` |
| F1 | a drain that BLOCKS is a drain failure: `is_alive()` after the join | `probe:513` `stderr_thread.join(timeout=3)`, `probe:519` |
| F2/F8 | a second failure is APPENDED, never dropped | `probe:527` `if drain_error[0] is not None:`, `probe:531` `probe_error = f"{probe_error}; stderr drain failed: {drain_error[0]}"` |
| F6 | the third timeout wording for values the pinned syntax rejects but `float()` parses | `probe:288` `msg = (f"ACP_PROBE_TIMEOUT must be plain decimal digits "` |
| F5 | the last resort never raises out of its own `except`: per-file write isolation + one extra stderr line | `probe:572` `m3_errors = []`, `probe:574` `def _m3_write(path, text):`, `probe:596` `print("acp_probe: last-resort evidence write failed: " + "; ".join(m3_` |
| F1 | the drain-failure test parametrised `dir` / `fifo`, errno text from libc, elapsed bound | `test:2228` `@pytest.mark.parametrize("kind,exc_name,err", [`, `test:2232` `def test_probe_reports_a_stderr_drain_failure(tmp_path, agent_result,` |
| F5 | the write-receiver tests (FIFO at each output; the timeout-reject receiver; symlink and reader-backed FIFO) | `test:2481` `def test_probe_evidence_writes_refuse_a_non_regular_path(tmp_path, age`, `test:2510` `def test_probe_timeout_reject_write_refuses_a_non_regular_path(tmp_pat`, `test:2992` `def test_probe_evidence_writes_refuse_a_symlink_and_a_readable_fifo(tm` |
| F4 | the probe-own-file tests (mid-run swap, clean and through the M3 handler; the import-time `None` path) | `test:2541` `def test_probe_survives_its_own_file_being_replaced_mid_run(tmp_path,`, `test:2610` `def test_probe_unreadable_own_file_is_named_not_a_traceback(tmp_path,` |
| F1/F9 | the drain-bound tests (a drain that never finishes; a late writer the join must wait for) | `test:2693` `def test_probe_reports_a_drain_that_never_finishes(tmp_path):`, `test:2732` `def test_probe_drain_join_waits_for_a_late_writer(tmp_path):` |
| F2/F8 | BrokenPipe + a directory at `agent-stderr.txt`, both substrings asserted, identity key set unchanged | `test:2766` `def test_probe_appends_a_drain_failure_to_an_earlier_error(tmp_path, a` |
| F6 | the timeout parametrisation, three wording classes | `test:2351` `_DIGITS = "must be plain decimal digits (e.g. '30' or '0.5'), got %s"`, `test:2376` `def test_probe_timeout_rejects_forms_outside_the_domain(tmp_path, agen` |
| F7 | the bytecode test extended with the `-B` flag and the M3 site | `test:2420` `def test_identity_records_the_runtime_bytecode_state_not_the_string(` |
| F10 | the early-retry fake records `FIRST_OK` and the CALLER's line per read; the test asserts the distribution | `test:1442` `_sites.append(sys._getframe(1).f_lineno)`, `test:1481`, `test:1486` `assert len(set(sites[:4])) == 1, (` |
| F13 | the AST self-scan over reads AND writes + the committed golden set | `test:2831` `_GOLDEN_UNGUARDED_RECEIVERS = {`, `test:2839` `def _scan_file_receivers(src):`, `test:2938` `def test_probe_every_file_receiver_is_guarded_or_committed():` |

## RED-BEFORE (on the PIN bytes) beside GREEN-AFTER (final bytes)

Rig: a private `git archive 088efef` copy, `env -i`-style hermetic env, probe under `timeout 12`, one process per case.
`files=` is `runtime-identity.json env.json timeline.jsonl agent-stderr.txt` (Y = present).

```
--- PIN (red) --------------------------------------------------------------------------------
CASE fifo-agent-stderr            rc=0    elapsed= 3.1s files=YYYY
     probe_error = '<ABSENT>'
CASE fifo-runtime-identity        rc=124  elapsed=12.0s files=YNNY
CASE fifo-env-json                rc=124  elapsed=12.0s files=YYNY
CASE fifo-timeline                rc=124  elapsed=12.0s files=YYYY
CASE fifo-rid+timeout-reject      rc=124  elapsed=12.0s files=YNNN
CASE agent-swaps-probe-to-fifo    rc=124  elapsed=12.0s files=NNNY
     stderr[0] = 'Traceback (most recent call last):'
CASE grandchild-holds-stderr      rc=0    elapsed= 3.1s files=YYYY
     probe_error = '<ABSENT>'          agent-stderr.txt bytes=0        <- silent truncation, rc 0
[PIN] EXEC-SWAP rc=124 elapsed=12.0s files=NNNY
[PIN]   stderr: ['Traceback (most recent call last):', '  File ".../acp_probe.py", line 469, in main']
BP+DIR rc=1 elapsed=0.1s
  probe_error = 'BrokenPipeError: agent process exited before c2a write landed'
  identity keys = ['agent_argv', 'agent_child_pid', 'agent_entrypoint_sha256', 'agent_exit_code',
                   'agent_interpreter_realpath', 'agent_interpreter_sha256', 'agent_realpath',
                   'probe_error', 'probe_path', 'probe_sha256', 'python_dont_write_bytecode',
                   'spawned_at_utc']            <- the IsADirectoryError is in none of them
acp_probe: ACP_PROBE_TIMEOUT is not a valid number: '1e3'          rc=64
```

```
--- FINAL (green) ----------------------------------------------------------------------------
CASE N-fifo-agent-stderr          rc=1    elapsed= 0.1s files=YYYY
     probe_error = "stderr drain failed: OSError: [Errno 6] No such device or address: '<fd>/agent-stderr.txt'"
CASE N-dir-agent-stderr           rc=1    elapsed= 0.1s files=YYYY
     probe_error = "stderr drain failed: IsADirectoryError: [Errno 21] Is a directory: '<fd>/agent-stderr.txt'"
CASE N-fifo-runtime-identity      rc=1    elapsed= 0.1s files=YYYY
     stderr[0] = "acp_probe: last-resort evidence write failed: runtime-identity.json: OSError: [Errno 6] ..."
CASE N-fifo-env-json              rc=1    elapsed= 0.1s files=YYYY
     probe_error = "OSError: [Errno 6] No such device or address: '<fd>/env.json'"
CASE N-fifo-timeline              rc=1    elapsed= 0.1s files=YYYY
     probe_error = "OSError: [Errno 6] No such device or address: '<fd>/timeline.jsonl'"
CASE N-fifo-rid+timeout-reject    rc=1    elapsed= 0.0s files=YYYY
     stderr[0] = "acp_probe: last-resort evidence write failed: runtime-identity.json: OSError: [Errno 6] ..."
CASE N-agent-swaps-probe-to-fifo  rc=0    elapsed= 0.1s files=YYYY
     probe_error = '<ABSENT>'   probe_sha256 = 3278ae2d…  == sha256 of the bytes that ran; path is now a FIFO
CASE N-grandchild-holds-stderr    rc=1    elapsed= 3.1s files=YYYY
     probe_error = "stderr drain failed: did not finish in 3s (the agent's stderr may still be held open by a surviving child)"
CASE N-control-clean              rc=0    elapsed= 0.2s files=YYYY   probe_error = '<ABSENT>'
[NEW] EXEC-SWAP rc=1 elapsed=0.1s files=YYYY
[NEW]   probe_error = 'probe file unreadable: OSError: not a regular file: <tree>/tools/acp_probe.py'
[NEW]   probe_sha256 = None
```
The `1e3` form now reads `ACP_PROBE_TIMEOUT must be plain decimal digits (e.g. '30' or '0.5'), got '1e3'` (rc 64), and
the BrokenPipe + drain-dir pairing now reads
`BrokenPipeError: agent process exited before c2a write landed; stderr drain failed: IsADirectoryError: [Errno 21] …`.

## MUTANT TABLE — 33 rows, every one RUN on a fresh `git archive 088efef` copy + this lane's two files

Applied by a patcher that ABORTS unless the anchor occurs exactly once; each run `-x -q -p no:randomly` with an explicit
`--basetemp` under the lane scratchpad. The shared tree was never mutated.

| # | mutant | verdict | killer (verbatim first `E` line / summary) |
|---|---|---|---|
| M1 | FIXTURE-FIFO-UNGUARDED | KILLED | `subprocess.TimeoutExpired` in `test_probe_refuses_a_non_regular_fixture` — `1 failed, 53 passed` |
| M2 | DRAIN-SWALLOW (`error_slot[0] = …` → `pass`) | KILLED | `AssertionError: expected exit 1, got 0:` (`…drain_failure[dir-IsADirectoryError-21]`) |
| M3 | LOSSY-NO-RAW | KILLED | `AssertionError: the lossless copy of a replaced-byte line is missing: ['dir', 'frame', 'seq', 't_mono_ns', 't_utc']` |
| M4 | MIRROR-DRIFT (`NSEC`→`NSECX`) | KILLED | `AssertionError: NOSTR_NSEC_HEX was not redacted (regex alternative missing)` |
| M5 | TIMEOUT-LENIENT (domain gate → `if False:`) | KILLED | `assert 1 == 64` in `test_probe_timeout_non_numeric_exits_64` |
| M6 | BYTECODE-STRING (both sites) | KILLED | `AssertionError: PYTHONDONTWRITEBYTECODE='2' flags=[]: recorded False, CPython reports True` |
| M9 | DL-INLINE | KILLED | `AssertionError: RL_CALLS=97 DEADLINE_SEEN=0.0` |
| M10 | AP-F1a-SINGLE-SHOT | KILLED | `AssertionError: expected exit 0 (retry recovered), got 1: acp_probe: interpreter sample failed: transient failure` |
| M11 | LATE-NULL | KILLED | `AssertionError: assert None == '/usr/bin/python3.11'` |
| M12 | LATE-EVERY | KILLED | `AssertionError: expected exactly 2 child /proc/<pid>/exe reads …` |
| M13 | SHA-GUARD-OFF | KILLED | `subprocess.TimeoutExpired` in `test_sha256_file_refuses_a_non_regular_file` |
| M14 | NO-ISFINITE | KILLED | `AssertionError: expected exit 64 for '999…9'` (`digits400_overflows_to_inf`) |
| M17 | LOSSY-ALWAYS | KILLED | `AssertionError: raw_b64 on a clean line: {…}` |
| M18 | DRAIN-EMPTY-MSG | KILLED | `AssertionError: got 'stderr drain failed: '` |
| M19 | BYTECODE-M3-ONLY (VERIFY-N5h survivor) | **KILLED** | `AssertionError: PYTHONDONTWRITEBYTECODE=None flags=['-B']: recorded False, CPython reports True` (`dash_B_at_the_m3_site`) |
| M20 | FIRST-ERROR-WINS-OFF (VERIFY-N5h survivor) | **KILLED** | `AssertionError: got "stderr drain failed: IsADirectoryError: …"` — the BrokenPipe text is gone |
| M20b | APPEND-DROPPED (the PIN's fold restored) | **KILLED** | `AssertionError: got 'BrokenPipeError: agent process exited before c2a write landed'` |
| M21 | JOIN-ZERO (VERIFY-N5h survivor) | **KILLED** | `AssertionError: assert 'BrokenPipeEr...viving child)' == 'BrokenPipeEr... write landed'` (whole file, `-x`); on the dedicated bound test alone: `AssertionError: probe failed: 1: acp_probe: stderr drain failed: did not finish in 3s …` |
| M23 | EXTRA-EARLY-READ (VERIFY-N5h survivor) | **KILLED** | on `-k early_retry_recovers` ALONE: `AssertionError: the four early reads came from 2 different call sites in acp_probe.py (lines [308, 328, 328, 328]) …` |
| W1 | drain write → bare `open` | KILLED | `AssertionError: got "stderr drain failed: did not finish in 3s …"` (`…drain_failure[fifo-OSError-6]`) |
| W2 | env.json → bare `open` | KILLED | `subprocess.TimeoutExpired` (`…refuse_a_non_regular_path[env.json]`) |
| W3 | `_write_evidence` rid → bare `open` | KILLED | `subprocess.TimeoutExpired` (`…refuse_a_non_regular_path[runtime-identity.json]`) |
| W4 | `_write_evidence` timeline → bare `open` | KILLED | `subprocess.TimeoutExpired` (`…refuse_a_non_regular_path[timeline.jsonl]`) |
| W5 | timeout-reject rid → bare `open` | KILLED | `subprocess.TimeoutExpired` (`test_probe_timeout_reject_write_refuses_a_non_regular_path`) |
| W6 | `_m3_write` → bare `open` | KILLED | `subprocess.TimeoutExpired` (`…refuse_a_non_regular_path[runtime-identity.json]`) |
| N1 | ISALIVE-OFF (this round's F1 line removed) | KILLED | `AssertionError: expected exit 1, got 0:` (`test_probe_reports_a_drain_that_never_finishes`) |
| N3 | PROBE-HASH-SILENT (`if _PROBE_SHA256 is None …` → `if False:`) | KILLED | `AssertionError: expected exit 1, got 0:` (`test_probe_unreadable_own_file_is_named_not_a_traceback`) |
| N4 | NOFOLLOW-OFF | KILLED | whole file: `AssertionError: _open_regular no longer contains os.O_NOFOLLOW`; behaviourally on `-k symlink_and_a_readable_fifo`: `assert "[Errno 40] Too many levels of symbolic links: …" in …` |
| N5 | NONBLOCK-OFF | KILLED | `AssertionError: got "stderr drain failed: did not finish in 3s …"` (the FIFO blocks again) |
| N6 | ISREG-OFF (inside `_open_regular`) | KILLED | whole file: `AssertionError: _open_regular no longer contains S_ISREG(os.fstat(fd)`; behaviourally on `-k symlink_and_a_readable_fifo[fifo_with_reader]`: `AssertionError: expected exit 1, got 0` — the evidence went into the reader's pipe |
| N7 | THIRD-WORDING-REVERT | KILLED | `assert "acp_probe: A...number: '3_0'" == "acp_probe: A...'), got '3_0'"` |
| N8 | PROBE-HASH-REREAD (the M3 site re-reads `realpath(__file__)`) | **SURVIVED, then KILLED** | first run `99 passed` — a real gap in this lane's own work; closed by the `through_the_m3_handler` case, after which: `subprocess.TimeoutExpired … timed out after 5 seconds` (the PIN's exact hang) |
| N9 | M3-NO-ISOLATION (`_m3_write`'s try/except removed) | KILLED | `AssertionError: env.json was lost because runtime-identity.json was hostile: ['agent-stderr.txt', 'runtime-identity.json']` |

Not re-run (VERIFY-N5h already ruled on them and they are parent-only or equivalent): M7/M8 (the parent's red-before),
M15/M16 (`os.stat`→`os.lstat`, equivalent-or-stricter), M22 (TIMEOUT-MSG-SWAP — superseded by N7, which is the same
class against the new three-wording branch).

## The AST self-scan (F13) — what it actually examines

13 receivers examined, 4 unguarded, all four in the committed golden set:

```
(56,  'open:r',        'path',                                        '_sha256_file')     guarded: S_ISREG(os.stat(path))
(73,  'os.open',       'path',                                        '_open_regular')    GOLDEN: the primitive itself
(116, '_open_regular', 'stderr_path',                                 '_drain_stderr')
(144, '_open_regular', "os.path.join(framedir, 'env.json')",          '_write_env')
(185, '_open_regular', "os.path.join(framedir, 'runtime-identity.json')", '_write_evidence')
(193, '_open_regular', 'tl_path',                                     '_write_evidence')
(232, 'open:r',        'fixture_path',                                'main')             guarded: fixture_st = os.stat(fixture_path) … S_ISREG(fixture_st
(233, 'json.load',     'f',                                           'main')             handle bound by the guarded `with`
(295, '_open_regular', "os.path.join(framedir, 'runtime-identity.json')", 'main')
(324, 'os.readlink',   "'/proc/%d/exe' % proc.pid",                   'main')             GOLDEN: readlink cannot block
(397, 'os.readlink',   "'/proc/%d/exe' % proc.pid",                   'main')             GOLDEN
(488, 'os.readlink',   "'/proc/%d/exe' % proc.pid",                   'main')             GOLDEN
(576, '_open_regular', 'path',                                        '_m3_write')
```
Coverage floor `len(examined) >= 12` (actual 13) makes an empty or narrowed scan red. Three negative controls run
in-process on mutated copies of the source: a planted `open(path + '.copy', 'w')`, a planted `Path(...).read_text()`
and a planted raw `os.open(..., O_WRONLY|O_CREAT)` each change the unguarded set (asserted, `test:2938` `def test_probe_every_file_receiver_is_guarded_or_committed():`).

## GATES (pasted verbatim)

```
RESULT: rev=088efef22b1e files=2 runs=2 identical=yes rc=0 summary="155 passed in 48.56s 155 passed in 48.23s"
RESULT: rev=088efef22b1e files=2 runs=2 identical=yes rc=0 summary="155 passed in 48.64s 155 passed in 48.20s"
```
Two independent `scripts/lane_gate.sh -r 088efef -f "proofs/S0-01/tools/acp_probe.py tests/test_s0_01_acp_probe.py"
-t "tests/test_s0_01_acp_probe.py tests/test_s0_01_negative_contract.py" -n 2` invocations (four pytest runs) on a
`git archive` copy of the PIN with exactly this lane's two files copied over. Both on the FINAL bytes (identity table
in each run matches the FILE IDENTITY block above).

Adjacent consumers of the probe, run because this round changes what the probe writes and what it hashes:
```
206 passed in 11.89s   tests/test_s0_01_pc_tools.py tests/test_s0_01_check_initialize.py tests/test_s0_01_negative_contract.py
46 passed, 314 deselected, 9 xfailed in 28.48s   test_s0_01_check_acp_conformance.py -k "real_leg or known_stale or fifo_at_tools_acp_probe or dir_at_tools_acp_probe"
```
`tests/test_s0_01_pc_tools.py` is lane P5b's untracked producer-parser (floor `"proofs/S0-01/tools/acp_probe.py": 4`):
the `os.path.join(framedir, …)` anchors are untouched by this round, and its floor still resolves — run, not assumed.
`proofs/S0-01/negative_contract.py:187` pins `rid["probe_sha256"]` against the CURRENT probe file, so a probe byte
change moves the real-leg corpus's known-stale reason: the corpus already carried `4e88997e…` at the PIN (probe
`c1a9e173…`), the reason string is unchanged (`negative: negative: probe_sha256 mismatch`, an entry in
`_KNOWN_XFAIL_REASONS`), and the 9 xfails above are that mechanism working. No hard-coded probe digest exists anywhere
in the tree (`grep -rn "c1a9e173\|4e88997e"` over `*.py/*.json/*.yaml` outside briefs/docs: zero hits).

`pyflakes` on both lane files: rc 0. `scripts/lint_delta.py --base 088efef`: `2 NEW pyflakes hit(s)` — both in
`tests/test_s0_06_four_scope.py`, another lane's file, not this lane's.

## Item 9 — the report's claim set, corrected

**The consumer contract (F3).** A probe capture does NOT reach `check_timeline`
(`proofs/S0-01/check_acp_conformance.py:262` `def check_timeline(entries, leg, leg_dir):`, invoked at one place only,
`proofs/S0-01/check_acp_conformance.py:1739` `c2a_split, a2c_split = _run_check(check_timeline, leg, entries, leg, d`, inside the positive-leg loop). The probe's leg goes through
`proofs/S0-01/check_acp_conformance.py:1789` `neg_observed = _run_check(check_negative, "negative", neg_dir)` into
`proofs/S0-01/check_acp_conformance.py:1494` `observed = nc.validate_negative_dir(neg_dir, _fixtures())`
(`proofs/S0-01/negative_contract.py:82` `def validate_negative_dir(neg_dir: Path, fixtures_dir: Path | None = N`). That consumer ALREADY allows `raw_b64`:
`proofs/S0-01/negative_contract.py:103` `if set(e) - {"seq", "dir", "t_utc", "t_mono_ns", "frame", "raw", "raw_`. It fails closed not on the key set but on the mangled TEXT — the verifier's
run over a real lossy capture: `NegativeFailure: agent error is code=-32602 message='Invalid par<U+FFFD>ams'`. Round
11's "Consumer contract" block and its self-attack A2 named the wrong consumer, and the A5k hand-off built on it was
misaimed; nothing about `raw_b64` needs a checker change. (Reproduced here only as far as the call chain and the key
set — the `NegativeFailure` text is VERIFY-N5h's run, re-read from primary source, not re-executed by this lane.)

**D1 restated — the write side has EIGHT receivers, not four.** At the PIN: `agent-stderr.txt` (the drain),
`env.json`, `runtime-identity.json` (in `_write_evidence`), `timeline.jsonl`, **the timeout-reject path's own early
`runtime-identity.json` write**, and the M3 handler's three (`rid`, `timeline`, the `agent-stderr.txt` touch). Three
of the four JSON outputs HANG on a planted FIFO (`rc=124`, measured above, one process per target), not one; the
`agent-stderr.txt` case is the rc-0 swallow. Round 11's proposal ("_open_regular for the four evidence writes + the
M3 rescue-write path") would have missed the timeout-reject receiver — measured on the PIN as its own case
(`fifo-rid+timeout-reject rc=124`). All seven reachable receivers are now routed; the eighth (`agent-stderr.txt` in
the M3 handler) shares `_m3_write`.

**The class-table row for `_sha256_file`'s guard restated** (line 52 of the PIN's probe; the same statement is now `probe:53` `if not stat.S_ISREG(os.stat(path).st_mode):`). Round 11 recorded "GUARDED — one guard covers all three
receivers of `_sha256_file`". True for the agent entrypoint and the child interpreter; FALSE at the outermost
boundary for receiver 1, the probe's own file: the guard's `OSError` escaped `_write_evidence`, the last-resort
handler re-ran the same unguarded read, and the second raise inside the `except` sent CPython's traceback printer
into `linecache` on the FIFO — `rc=124`, zero evidence files (reproduced on the PIN here). Correct row for this
round: *guarded against a blocking read at the receiver, and the receiver's own failure path is now guarded too —
the hash is taken once at import (`probe:95` `_PROBE_PATH = os.path.realpath(__file__)`) and both writers read the cached value (`probe:170` `"probe_sha256": _PROBE_SHA256,`, `probe:554`).*

**F14's three precision notes.** (a) The round-11 class table recorded the fake's ordinal gate as "was: same"; the
variable was RENAMED `_call_count` → `_rl_calls`, and that rename is the only reason the AF-AP-57 screen fires on it
at all — on the parent the same construct was invisible to the screen. (b) "AF-AP-57 fires on the PIN at `:1681`" was
the SCREEN's only hit, not the file's only ordinal gate. (c) The `-B`-flag case of #40 was proven by VERIFY-N5h's own
run and by no committed test; it is now a committed case (`test:2420` `def test_identity_records_the_runtime_bytecode_state_not_the_string(`, id `dash_B_env_unset`), as is the M3 site
(`dash_B_at_the_m3_site`).

## 18-class self-sweep over the two lane files

| # | class | instances in these two files | verdict + the run or guard |
|---|---|---|---|
| 1 | presence-gated checks | `probe:254` `if not os.path.isdir(framedir):` · `probe:593` `if not os.path.exists(stderr_path):` | SAFE — both are NEGATED (create-if-absent / make-the-dir), not skip gates; the second is followed by a `_open_regular` write whose refusal is recorded (N9 run: the isolation is what keeps the other three files) |
| 2 | reads outside a walk / no `S_ISREG` | 13 receivers enumerated by `test:2938` `def test_probe_every_file_receiver_is_guarded_or_committed():` | CLOSED — 9 guarded, 4 in the committed golden set; 3 planted receivers turn it red (run in-process); M1/M13/W1-W6 all KILLED |
| 3 | stale `[-1]` over produced records | 0 (`grep -n "\[-1\]"` on both files: no hits) | EMPTY CLASS — a result |
| 4 | negative acceptance assertions | every new test pairs its assertion with a positive control (`test:2510` `def test_probe_timeout_reject_write_refuses_a_non_regular_path(tmp_pat` control rc 64 · `test:2610` `def test_probe_unreadable_own_file_is_named_not_a_traceback(tmp_path,` control rc 0 with a real digest · `test:2693` `def test_probe_reports_a_drain_that_never_finishes(tmp_path):` control rc 0 · `test:2232` `def test_probe_reports_a_stderr_drain_failure(tmp_path, agent_result,` control) | SAFE — a vacuous pass would fail the control |
| 5 | substring / tail anchors classifying outcomes | `test:2500` `assert f"[Errno {errno.ENXIO}] …: '{framedir / target}'" in r.stderr` and 3 siblings | SAFE — the anchor is the FULL reason including the absolute path; exact `==` is used wherever stderr is a single line (`test:2510` `def test_probe_timeout_reject_write_refuses_a_non_regular_path(tmp_pat` control). DOCUMENTED-LIMIT: `assert "Traceback" not in r.stderr` is an absence assertion; it is paired with an exit-code and a file-set assertion in the same test |
| 6 | env-domain fail-opens | `ACP_PROBE_TIMEOUT` (`probe:270`), `PYTHONDONTWRITEBYTECODE` (runtime state) | CLOSED — 15 rejected forms + 4 accepted (`test:2376` `def test_probe_timeout_rejects_forms_outside_the_domain(tmp_path, agen`, `test:2394` `def test_probe_timeout_accepts_the_domain(tmp_path, agent_result, raw)`); M5/M14/N7 KILLED; M6/M19 KILLED |
| 7 | lossy decodes on a decision path | the a2c decode | CLOSED in round 11; M3/M17 re-run and KILLED here |
| 8 | broad catches | `probe:81` `except Exception:` (close-then-re-raise) · `probe:99` `except Exception as _exc:   # OSError today; an import must never fail` (import-time, recorded in `_PROBE_SHA256_ERROR`) · `probe:122` `except Exception as exc:` (entrypoint hash, recorded) · `probe:502` (`proc.stdin.close()`, pre-existing `pass`) · `probe:546` (the M3 handler) · `probe:578` `except Exception as exc2:`/`probe:585` (per-file, recorded) | SAFE — every catch this round adds RECORDS its exception into evidence or re-raises; N3 (silencing the import-time one) KILLED. `probe:502` is pre-existing and unchanged: closing a pipe to an exited child cannot change evidence |
| 9 | waits/polls + ordinal gates in fakes | `probe:321-336` `_sample_deadline = time.monotonic() + _EARLY_SAMPLE_DEADLINE_S` (bounded early loop) · `probe:507` `proc.wait(timeout=5)` · `probe:513` `join(timeout=3)` · `test:1442` `_sites.append(sys._getframe(1).f_lineno)` the fake's ordinal gate | CLOSED — M9 (deadline inlined) KILLED, M21 (join bound) KILLED by a dedicated test, M23 (ordinal shift) KILLED by the call-site distribution. AF-AP-57 = 1 hit, REVIEWED-SAFE only because M23 was RUN |
| 10 | skips / xfails that cannot fire | 0 (`grep -n "skip\|xfail"`: only prose inside docstrings) | EMPTY CLASS — a result |
| 11 | world-scoped enumerations (AF-AP-59) | `test:2506` `sorted(os.listdir(framedir))` inside a failure message | SAFE — scoped to the test's own tmp framedir |
| 12 | signal installs before their try (AF-AP-58) | 0 in both files | EMPTY CLASS — a result |
| 13 | `/proc/<pid>/exe` races (AF-AP-55) | `probe:324` `candidate = os.readlink("/proc/%d/exe" % proc.pid)`, `probe:397` `interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)`, `probe:488` | SAFE — the later reading wins and a multi-stage-exec fixture is in the suite; M11/M12 KILLED. The test's own `/proc/self/exe` read is SWEEP-tests 13.1, agreed SAFE by VERIFY-N5h item 9 |
| 14 | mirrors of the code under test | `_REDACTED_ENV_KEY_RE` (pinned equal to `pins`, M4 KILLED) · the scan's structural token assertions in `test:2938` `def test_probe_every_file_receiver_is_guarded_or_committed():` | DOCUMENTED-LIMIT on the second: `assert "os.O_NOFOLLOW" in prim` IS a structural mirror. It is not the only killer — N4 and N6 also die behaviourally (`-k symlink_and_a_readable_fifo`), measured separately and pasted above |
| 15 | two counters over different populations asserted equal | `RL_CALLS` / `FIRST_OK` / `SITES` are three views of ONE population (child `/proc/<pid>/exe` reads); the 131072-byte assertion is one population | SAFE |
| 16 | provably redundant / dead guards | `probe:519` `and drain_error[0] is None` | DOCUMENTED-LIMIT — not dead: it protects the race where the drain thread has recorded its exception and has not yet exited, so `is_alive()` is still true. No test forces that window (it is a scheduler race); the clause is a guard against overwriting a REAL error with a generic one, and dropping it cannot fail open |
| 17 | hardlink-clobbering writes | `probe:62` `_open_regular` uses `O_CREAT\|O_TRUNC` with no `st_nlink` check | **DOCUMENTED-LIMIT, new instance, stated first-class** — a hardlink planted at an evidence path truncates the linked inode and mirrors the evidence into it. `O_NOFOLLOW` does not cover hardlinks. Not fixed here because the brief pins the primitive's exact shape; the one-line hardening is `os.fstat(fd).st_nlink == 1` inside the same `if`. Named for the coordinator |
| 18 | other families | the daemon drain thread (`probe:519` `if stderr_thread.is_alive() and drain_error[0] is None:` bounds it) · timing assertions in two tests (`2.5 < elapsed < 10`, `elapsed < 5`) | DOCUMENTED-LIMIT on the timing bounds: they are margins over a 3 s join and a ~0.1 s refusal (measured 0.0-0.1 s and 3.1 s), so a 30x load spike would flake them LOUDLY rather than pass silently |

`scripts/ap_screen.py` on the final bytes: **8 hits on the probe, 1 on the test — the same class counts the PIN
carried**. Every hit classified by the run that exercises it:

| class | hits | verdict + the run |
|---|---|---|
| AF-AP-55 | `probe:324` `candidate = os.readlink("/proc/%d/exe" % proc.pid)`, `probe:397`, `probe:488` | REVIEWED-SAFE — sweep class 13; the later reading wins, M11/M12 KILLED |
| AP-1 | `probe:206` `v = os.environ.get(k)`, `probe:270` `timeout_raw = os.environ.get("ACP_PROBE_TIMEOUT", "30")` | REVIEWED-SAFE — the probe's DECLARED inputs, validated at the boundary; M5/M14/N7 KILLED |
| AP-32 | `probe:55` `h = hashlib.sha256()`, `probe:134` `"sha256_12": hashlib.sha256(v.encode("utf-8")).hexdigest()[:12],` | REVIEWED-SAFE — the sha256 identity and the redaction fingerprint; M4 KILLED |
| AP-24 | `probe:502` `except Exception:` | PRE-EXISTING and unchanged (`proc.stdin.close()`); the PIN carried the same single hit |
| AF-AP-57 | `test:1443` `if _rl_calls[0] <= 3:` | REVIEWED-SAFE **only because M23 was RUN** and dies on `-k early_retry_recovers` alone |

`lint_delta`'s added-line tells on the test file: AP-1 (`os.environ.get("PATH", "")` in `_hostile_env`, `test:2469` —
building a child env, the file's established pattern), AP-32 (`test:2560` `real_sha = hashlib.sha256(probe.read_bytes()).hexdigest()` — the independent oracle digest),
AP-24 (the screen matching PROSE, not code: `test:2234` `makes the drain thread's open() RAISE;` inside a docstring). All three verified by reading the added lines and by the tests that exercise them.

## DISCREPANCIES with the brief (each measured, none silent)

1. **Item 3's predicted exit code for the mid-run swap is wrong; the measured behaviour is better.** The brief says the
   `os.unlink(probe_path); os.mkfifo(probe_path)` agent must give "rc 1 within 5 s and ALL FOUR evidence files". With
   the hash cached at import (the fix the same item pins) nothing raises: the run is **rc 0** in 0.1 s with all four
   files and `probe_sha256` equal to the digest of the bytes that actually ran. Both halves are committed:
   `test:2541` `def test_probe_survives_its_own_file_being_replaced_mid_run(tmp_path,` covers the production shape (rc 0, and rc 1 through the M3 handler when a directory is also planted at
   `env.json`), and `test:2610` `def test_probe_unreadable_own_file_is_named_not_a_traceback(tmp_path,` reaches the `None` path — the probe's file already non-regular when the module body
   runs — where the brief's `rc 1 + four files + a named probe_error` is exactly what happens.
2. **Item 1's pinned wording for the blocking drain is unreachable after item 4, so the wording changed.** With
   `_open_regular` a FIFO at `agent-stderr.txt` fails ENXIO instantly, so "(stderr path may not be a regular file)"
   would name a cause that can no longer occur. The only reachable cause is a drain still reading, which this lane
   reproduced as a production shape (a grandchild inheriting the agent's stderr): the message is
   `did not finish in 3s (the agent's stderr may still be held open by a surviving child)`. The `fifo`
   parametrisation the item asks for is committed and asserts the ENXIO reason instead (`test:2228` `@pytest.mark.parametrize("kind,exc_name,err", [`).
3. **Item 8's `FIRST_OK=4` does NOT kill M23 — measured.** Under M23 the extra read consumes failure #1, so the first
   SUCCESSFUL call is still #4 and the total is still 5: `FIRST_OK=4` passed under the mutant (the run stopped at the
   next assertion). What kills it is the added call-site distribution (`test:1486` `assert len(set(sites[:4])) == 1, (`): `[308, 328, 328, 328]` — two
   distinct sites where the retry loop must be one. `FIRST_OK` is committed as the brief asks; the report records that
   it is not the killer.
4. **Item 4's golden set is keyed by `(function, category, receiver)` with counts, not by `(line, receiver)`, and the
   guard rule is "the same receiver was `os.stat`-ed and `S_ISREG`-tested earlier in the enclosing function", not a
   five-line text window.** Reasons, both measured: the probe's own fixture guard sits 8 lines above its read
   (`probe:225` `fixture_st = os.stat(fixture_path)` → `probe:232` `with open(fixture_path) as f:`, seven lines), so a five-line window would flag a genuinely guarded receiver; and VERIFY-CK12
   F-CK12-05 ruled line-keyed exemptions an anti-pattern (they go red on every unrelated edit). The golden set is
   `{(main, os.readlink, '/proc/%d/exe' % proc.pid): 3, (_open_regular, os.open, path): 1}` — the three readlinks the
   brief names, plus the primitive's own `os.open`, which is unavoidably inside the enumerated write set and is
   pinned separately by the structural assertions on its flags.
5. **Item 6 is implemented as two new parameters of the same test, not one.** `test_identity_records_the_runtime_
   bytecode_state_not_the_string` now carries `dash_B_env_unset` and `dash_B_at_the_m3_site`; the second is the one
   that kills M19.
6. **Mutant M22 (the two wordings exchanged) is superseded, not run.** With three wordings the swap is ambiguous; N7
   (revert the third wording) is the same class against the new branch and is KILLED.

## Behaviour changes the coordinator should know before this lands on the PC

- **A drain that has not finished 3 s after the agent exits is now a probe FAILURE (rc 1) instead of a silent
  truncation (rc 0).** If the real `buzz-acp`/Hermes negative leg leaves any child holding the agent's stderr, the leg
  will now fail closed with a named reason where it previously passed with a truncated `agent-stderr.txt`. That is the
  correct direction, and it is a live-behaviour change: NOT exercised against the real agent (no bridge from this lane).
- **A rejected `ACP_PROBE_TIMEOUT` still exits 64** — unless the framedir's `runtime-identity.json` is itself hostile,
  in which case the run now exits 1 through the last-resort handler with the refusal named (previously: a hang).
- **The `1e3`/`3_0`/`+30`/`.5`/`5.`/`1_000`/`' 30 '`/`'30\n'` forms now carry a different (true) message.** Any
  consumer matching the old string for these forms would need updating; `grep -rn "is not a valid number"` over
  `proofs/` and `tests/` shows the only consumers are this lane's own tests.

## NOT DONE — stated first-class

- **F11** (the AF-AP-57 screen's `call_count` regex under-reporting) — lane P5b's file, out of scope. Untouched.
- **F12** (the checker's negative-leg `read_text()` hang on a FIFO at `agent-stderr.txt`) — lane A5l's file. Untouched.
  Note for whoever takes it: this round makes the PRODUCER refuse to create that FIFO, but the checker still reads
  whatever is on disk, so the consumer-side fix is still needed.
- **The hardlink sub-class of the write receivers** (class 17 above) — a documented limit with a named one-line fix,
  not implemented, because the brief pins the primitive's exact flag set.
- **No PC-venue run of anything.** The bridge carve-out is the coordinator's; this report's every number is from the
  sandbox. The probe has NOT been run against the real Hermes agent this round.
- **The full checker suite (`tests/test_s0_01_check_acp_conformance.py`, ~17 min) was NOT run whole** — only its 46
  real-corpus / probe-file tests (pasted above). Its remaining tests never execute the probe and reference it only
  through dynamically computed digests (`tests/test_s0_01_check_acp_conformance.py:397` `probe_sha = _sha256_file(P / "tools" / "acp_probe.py")`).
- **`raw_b64`'s consumer**: no change was needed or made (item 9); nothing was handed to A5k.

## SELF-ATTACK — the three most likely ways this is wrong

1. **"The `is_alive()` branch is a false-positive machine on the real PC leg."** Ruled out as far as the sandbox can:
   the branch only fires when the drain is STILL RUNNING 3 s after `proc.wait()` returned, i.e. something other than
   the agent holds the stderr write end. Every ordinary agent (including the 200 KB `agent_stderr_heavy` fixture and
   the 128 KB late writer) finishes the drain inside the bound — 100 tests, four gate runs, zero spurious firings, and
   the negative control in `test:2693` `def test_probe_reports_a_drain_that_never_finishes(tmp_path):` asserts rc 0 for the same agent without a survivor. NOT ruled out for the real
   Hermes agent: flagged above as a live-behaviour change.
2. **"The AST scan is a tautology that would pass over an unguarded receiver."** Ruled out by running three planted
   receivers (an unguarded write, an unguarded read, a raw `os.open`) through the same function inside the test — each
   changes the unguarded set — plus the coverage floor (13 examined, floor 12) and six W-mutants that each replace a
   `_open_regular` call with a bare `open` and die. The scan's weakest point is the handle exemption (`json.load(f)`
   where `f` is bound by a guarded `with`): a read on a handle obtained some other way would be flagged, but a read on
   a handle from a `with` whose opener is itself unguarded is caught at the opener, not the read.
3. **"The cached import-time hash records a digest that is no longer true, which is a NEW lie in the evidence."**
   Considered and rejected on the direction of the error: the cached value is the digest of the bytes CPython
   compiled and ran, taken before the agent process exists; the PIN's value was the digest of whatever sat at that
   path when the run ENDED, which an agent can choose. `test:2541` `def test_probe_survives_its_own_file_being_replaced_mid_run(tmp_path,` asserts the recorded digest equals a hash the test
   took itself before the swap, and `proofs/S0-01/negative_contract.py:187` `if rid.get("probe_sha256") != _sha256_file(probe_file):` (the consumer that pins this field)
   compares it against the file on disk at check time — so a swapped probe file still fails the leg, now with
   `probe_sha256 mismatch` instead of a hang. The residual window (a swap between CPython reading the source and the
   module body running) is exactly what `test:2610` `def test_probe_unreadable_own_file_is_named_not_a_traceback(tmp_path,` covers: `probe_sha256: null` plus a named `probe_error`.

## DISCIPLINE

- Shared tree: no `git` write of any kind. Every gate, mutant and probe ran on a `git archive 088efef` copy under
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/n5i/`; every pytest run carried an explicit
  `--basetemp` under that directory; every FIFO probe ran under `timeout 12`. Mutants were applied by a patcher that
  aborts unless its anchor occurs exactly once (`W3` aborted once on a 2-occurrence anchor and was re-run with a
  disambiguated one — recorded rather than silently loosened).
- Corpus: `S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden` on every pytest run (via
  `scripts/test_summary.sh` inside `lane_gate.sh`, and exported explicitly elsewhere).
- Interpreter: `/root/venv-agent-factory/bin/python` throughout.
- **Process census** (`ps -eo pid,ppid,stat,etimes,args -ww`, after the last run): no process of this lane is alive —
  no probe, agent, grandchild, wrapper or pytest under `n5i`. The live python belongs to lanes `d5m` and `o2r2`
  (their own basetemps). Nothing was killed: every child was reaped by `timeout`, by `subprocess.run`, or exited on
  its own (the drain-test grandchildren sleep 5 s and 0.4 s). No `pkill`/`pgrep -f` was used.
- Disk: `/` was at 87% (4.9 GB free) at the start; every mutant tree is removed by the runner after its run.
- **`report_lint` on THIS report**, both maps, against the working tree (this lane's files are uncommitted, so the
  working tree IS the subject; the two cross-file consumers cited are clean and carry identical line numbers at the
  PIN and in the tree, checked both ways):

```
report_lint: 107 refs — OK 107, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```
Every reference above carries the exact source text of the line it cites, so no number in this report has to be
trusted. The one deliberate exception is prose that names a PIN line ("line 52 of the PIN's probe"), written without
the `file:line` shape precisely so it cannot masquerade as a reference to the current bytes.
