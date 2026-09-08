# Lane N5i — S0-01 probe round 12: the WRITE class closed at every receiver, the probe's own file guarded, the drain that blocks named, the AST self-scan over reads AND writes, and an honest class table (build lane: PC Hermes `code-implementer` when the slot is free, else sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".) The probe's last checkpoint is
8z = `b4257f8` (pushed; local `9aaefd0`, identical tree): `proofs/S0-01/tools/acp_probe.py` 520 lines sha `c1a9e173…`,
`tests/test_s0_01_acp_probe.py` 2372 lines sha `f77bda15…` — these bytes are unchanged at HEAD; gate against HEAD.

**Why:** VERIFY-N5h (report `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/wf-results-r5/VERIFY-N5h.md`,
697 lines — READ IT WHOLE FIRST; it is the contract for this round) graded round 11 NOT-READY: "the CODE is sound and I found no
regression … what blocks is the claim set plus one three-line behaviour gap". Every finding below was REPRODUCED by the verifier on
the PIN; none is inferred. This round closes the write class the verifier measured (three of four evidence writes HANG on a FIFO;
eight write receivers, not four), guards the probe's own file (an agent that replaces the probe's script with a FIFO hangs the PIN with
zero evidence), names a drain that BLOCKS instead of raising (SWEEP #10 half-closed), and makes the report's class table true.

**Scope (exactly two files + your report):** `proofs/S0-01/tools/acp_probe.py` · `tests/test_s0_01_acp_probe.py` · report
`tasks/briefs/s0-01-n5i-support/N5i-report.md`. NOT yours: `proofs/S0-01/pins.py` (lane P5b holds it — the probe MUST stay
import-free of `pins`, see N5h item 5: the PC launch runs `/usr/bin/python3 proofs/S0-01/tools/acp_probe.py` with no PYTHONPATH,
so `import pins` is a ModuleNotFoundError there), `negative_contract.py`, the checker (lane A5k/A5l), `.claude/hooks/*` (P5b).
Shared-tree rules: never `git stash/checkout/restore/reset/add/commit/push`; every gate on a `git archive <PIN> | tar -x` copy under
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/n5i/ with your two files copied in
(`scripts/lane_gate.sh -r <PIN> -f "proofs/S0-01/tools/acp_probe.py tests/test_s0_01_acp_probe.py" -t "tests/test_s0_01_acp_probe.py
tests/test_s0_01_negative_contract.py" -n 2` does exactly that and prints the RESULT line you paste); explicit `--basetemp`; kill
only your own processes by pid; NEVER background a run and stop; no outward actions; NO PC bridge from a sandbox lane (the coordinator
runs the PC gate). Interpreter `/root/venv-agent-factory/bin/python`; corpus `S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden`.

## Design (pinned — build it, do not redesign it; line numbers are the PIN's)
1. **F1 — the drain that BLOCKS is named (SWEEP #10 fully closed).** After `probe:457` `stderr_thread.join(timeout=3)`:
   `if stderr_thread.is_alive() and drain_error[0] is None: drain_error[0] = "drain did not finish in 3s (stderr path may not be a
   regular file)"`. Parametrise `test_probe_reports_a_stderr_drain_failure` over `("dir", "fifo")`; the `fifo` case is RED on the PIN
   (`rc=0`, `probe_error` absent — paste the red run) and green after: rc 1, `probe_error` carries the text. The thread is a daemon —
   the probe must still EXIT (it does today; assert elapsed < 10 s).
2. **F2/F8 — a second error is never lost.** `probe:461` `if drain_error[0] is not None and probe_error is None:` → when
   `probe_error` is already set, APPEND: `probe_error = f"{probe_error}; stderr drain failed: {drain_error[0]}"` (the identity key set
   is unchanged — no `pins.py` change). Test: the repo's BrokenPipe monkeypatch shape + a directory at `agent-stderr.txt`, asserting
   BOTH substrings in `probe_error`; the verifier's M20 (`and probe_error is None` dropped) must die.
3. **F4 — the probe's own file is read ONCE, under a guard.** `probe:122` and `probe:483` both call
   `_sha256_file(os.path.realpath(__file__))` unguarded; the M3 handler re-runs it inside its `except`, and the traceback printer's
   `linecache` then blocks on a FIFO. Compute `_PROBE_SHA256` once at import time inside a `try` (`None` + a named
   `_PROBE_SHA256_ERROR` on failure); `_write_evidence` and the M3 handler read the global; if it is `None`, `probe_error` names it
   (`probe file unreadable: <reason>`) — never a traceback. Red test on the PIN: an agent that does `os.unlink(probe_path);
   os.mkfifo(probe_path)` (the path handed in the env, as the verifier did) → the PIN hangs (`rc=124`); after: rc 1 within 5 s and ALL
   FOUR evidence files present (the M3 "write all four files" invariant).
4. **F5 + F13 — the WRITE class closed at every receiver, held by an AST self-scan.** The eight write receivers on the PIN:
   `probe:73` (`agent-stderr.txt`, "wb"), `:101` (`env.json`), `:137` (`runtime-identity.json`), `:145` (`timeline.jsonl`), `:239`
   (the timeout-reject path's early `runtime-identity.json`), `:497` (M3 `rid_path`), `:503` (M3 `tl_path`), `:509`
   (`open(stderr_path, "wb").close()`, unreachable with a FIFO present). Add ONE primitive `_open_regular(path, mode)` that can NEVER
   block and names its refusal: `fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW | os.O_NONBLOCK, 0o644)`
   (a FIFO with no reader fails with ENXIO instead of blocking; a symlink fails with ELOOP), then `os.fstat(fd)` must be `S_ISREG`
   (else close + raise `OSError("not a regular file: <path>")`), then clear `O_NONBLOCK` with `fcntl` and return `os.fdopen(fd, mode)`.
   Route ALL seven reachable receivers through it (`:509` too — make it `_open_regular(...).close()` so the class has no exception).
   The refusal surfaces as a named `probe_error` where a `probe_error` can still be written, and as a one-line stderr message + rc 1
   where it cannot (the M3 handler's own writes). Red-before on the PIN: a FIFO at each of `runtime-identity.json`, `env.json`,
   `timeline.jsonl` → `rc=124`; at `runtime-identity.json` + `ACP_PROBE_TIMEOUT='30s'` → `rc=124` (the `:239` site); after: rc 1 in
   < 5 s with the reason. THEN the self-scan: port `tests/test_s0_01_check_acp_conformance.py:4718`'s AST walk to the probe test,
   over `acp_probe.py` ONLY, in the shape VERIFY-CK12 item 11 recommends — enumerate every read call (`open` in a read mode,
   `io.open`, `os.open`, `Path.open`, `.read_text`, `.read_bytes`, `json.load`) AND every write call (`open` in a write/append mode,
   `os.open` with `O_WRONLY`/`O_RDWR`/`O_CREAT`) and assert the set of (line, receiver) that is NOT wrapped by `_open_regular` /
   guarded by `S_ISREG` on the same receiver within five lines equals a COMMITTED golden set (today: the three `os.readlink` sites,
   which cannot block, and nothing else) — a coverage floor `len(examined) >= 12` so an empty scan is red; a planted unguarded
   `open(x, "w")` and a planted `Path(x).read_text()` each turn it red (paste both).
5. **F6 — the timeout message names the real reason.** In the reject branch after `probe:225`, when `float(timeout_raw)` parses
   finite and > 0, emit `ACP_PROBE_TIMEOUT must be plain decimal digits (e.g. '30' or '0.5'), got {timeout_raw!r}`; keep the two
   pinned wordings for the cases that own them (`float()` raises → "is not a valid number"; non-finite/non-positive → "must be a
   finite float > 0"). Extend the `test:2302` parametrisation with `1e3`, `+30`, `.5`, `5.`, `1_000`, `' 30 '`, `'30\n'`.
6. **F7 — the M3 site's `python_dont_write_bytecode` pinned.** Extend `test_identity_records_the_runtime_bytecode_state_not_the_string`
   with a case that forces the M3 path (a directory at `env.json`) under `-B` and asserts the same key from `runtime-identity.json`;
   the verifier's M19 (revert only `probe:491` to the string mirror) must die.
7. **F9 — the drain-join bound pinned.** An agent that writes ≥ 64 KB to stderr AFTER its a2c response, then sleeps 1 s; assert the
   full byte count lands in `agent-stderr.txt`; the verifier's M21 (`join(timeout=0)`) must die.
8. **F10 — the retained count gate kills its own ordinal-shift mutant.** In the fake at `test:1436`, print `FIRST_OK=<call index>` on
   the first non-failing child read and assert `FIRST_OK=4`; the verifier's M23 (an extra unguarded child `/proc/<pid>/exe` readlink
   after `probe:250`) must die on `-k early_retry_recovers` ALONE (paste the run).
9. **The report's claim set made true (F3, F5, F14):** replace the "Consumer contract" block and self-attack A2 with the REAL
   consumer — a probe capture goes through `check_negative` → `negative_contract.validate_negative_dir`
   (`proofs/S0-01/negative_contract.py:103` already allows `raw_b64`; the real consumer fails closed on the mangled TEXT:
   `agent error is code=-32602 message='Invalid par�ams'`) — never `check_timeline` (single call site, positive legs only);
   D1 restated with the eight receivers; the class-table row for `probe:52` restated ("guarded against a blocking read; receiver 1's
   own failure path was unguarded — F4, fixed this round"); F14's three precision notes (the `_call_count`→`_rl_calls` rename is why
   the screen now fires; `:1681` was the screen's only parent hit, not the file's only ordinal gate; the `-B` case is now a committed
   test, say so).
10. **Mutants:** the lane's 13 + the verifier's M19/M20/M21/M23 + one per write receiver (the `_open_regular` call replaced by a bare
    `open`) — every one must die; paste the killer line for each. Every FIFO probe under `timeout 12`.
11. **18-class self-sweep** over the two files (the S0-01 sweep's classes; `material-S0-02.md` §7): one row per class with the run
    or the guard; `scripts/ap_screen.py proofs/S0-01/tools/acp_probe.py` and `--tests tests/test_s0_01_acp_probe.py` — every hit
    classified by RUNNING it (AF-AP-57 = 1 is REVIEWED-SAFE only with item 8 landed).
12. **Report discipline:** FILE IDENTITY (sha256 + lines of the FINAL bytes); every `file:line` from `grep -n` on the FINAL bytes and
    `python3 scripts/report_lint.py <report> --map probe=proofs/S0-01/tools/acp_probe.py --map test=tests/test_s0_01_acp_probe.py`
    pasted with MISS 0; the two static-copy gate RESULT lines pasted from `lane_gate.sh`; the red-before runs pasted; NOT-done stated
    first-class. NOT this lane's: F11 (the screen regex — P5b), F12 (the checker's negative-leg FIFO hang — A5l).
