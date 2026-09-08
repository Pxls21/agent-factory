# VERIFY-N5h — adversarial grade of lane N5h (S0-01 ACP probe, round 11)

VERDICT: NOT-READY (full reasoning and the cheapest path at the bottom). Written incrementally to disk after each item.

PIN `9aaefd0ab4804d74f01c1eb43f3ae80ae700d548` (local) == pushed `b4257f8c78f2db8867ad519f8c99fbc46bf90543`
— verified: both resolve to tree `86728b44ee29c22988747a8630d3a922fbd83aa3` (identical trees).
Scratch copy: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vn11/pin` (`git archive` of the PIN).
Parent scope copy (`2823f05`): `.../vn11/parent`.

## FILE IDENTITY — reproduced

```
c1a9e1734ab1653a75ee6aa4161b5a151ce49036fdf4599757091ce9c6a1cb0e  proofs/S0-01/tools/acp_probe.py   520 lines   (PIN)
f77bda15120c635d8751bb39b726a506870f0f913ad2f0e03849e94f9f9a56b4  tests/test_s0_01_acp_probe.py    2372 lines   (PIN)
b9eb56dd9a75cb34907a7fe1bf0f4b579bd20e7994273d749907b28ce934ffbf  proofs/S0-01/tools/acp_probe.py   463 lines   (parent 2823f05)
f1f016fa1a787809646f5eb54cdf61265a4809b022cb669da6ac575dc58f236b  tests/test_s0_01_acp_probe.py    2032 lines   (parent 2823f05)
```
The report's FILE IDENTITY block matches byte-for-byte. SOLID.
Corpus preflight: `bash scripts/realleg_sync.sh check` -> `realleg_sync: /root/s0-01-realleg/golden intact (142 files)`.

## Item 0 — the mechanical gates, re-run by me

`report_lint.py … --rev 9aaefd0a… --map probe=… --map test=…`:
```
report_lint: 54 refs — OK 53, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (at 9aaefd0ab4804d74f01c1eb43f3ae80ae700d548)
```
MISS 0 / NEAR 0 — the report's claim reproduced exactly. The one UNCHECKABLE row is the lane's own reference to
`if _rl_calls[0] <= 3:` on a report line carrying no other claim token, exactly as the lane described it. SOLID.

`ap_screen.py` on the PIN probe (scratch copy): 8 hits — AF-AP-55 x3 (:268 :341 :432), AP-1 x2 (:158 :222),
AP-32 x2 (:54 :91), AP-24 x1 (:446). Parent: 11 hits (AP-1 x4 incl. the two bytecode string mirrors :113 :434,
AP-24 x2 at :63 :395). Both counts reproduced exactly. The report's D2 (the pack is stale, the brief is right about
AP-24 at :63/:395) is CONFIRMED from the parent screen.

`ap_screen.py --tests` on the PIN test: 1 hit at `test:1436` `if _rl_calls[0] <= 3:`. On the parent: 1 hit at
`if _sha_call[0] == 1:`. Reproduced.

## Item 1 — gate counts

Full file, PIN scratch copy, `--basetemp` under the session scratchpad, two foreground runs:
```
80 passed in 56.09s   run1-exit: 0
80 passed in 49.96s   run2-exit: 0
```
Parent (`2823f05`) baseline, same command: `53 passed in 42.54s   parent-exit: 0`.
53 -> 80 (+27) confirmed. 62 test functions vs 53 on the parent; the 9 new ones are appended at the end of the file
(`diff` of the `def test_` lists shows `53a54,62` — no existing test was renamed or deleted).

## Item 2 — #7, the read class

Reproduced on my own rig (a private copy of `proofs/S0-01/{tools,fixtures}` per venue; probe run under `timeout`;
`env -i` so nothing leaks from my shell):

| case | parent `2823f05` | PIN `9aaefd0a` |
|---|---|---|
| real fixture (positive control) | `rc=0 elapsed=0s` | `rc=0 elapsed=0s` |
| FIFO at the fixture path | `rc=124 elapsed=20s` (HANG) | `rc=64 elapsed=0s` `acp_probe: fixture is not a regular file: <path>` |
| directory at the fixture path | not run | `rc=64 elapsed=0s` same message |
| symlink -> `/dev/zero` at the fixture path | `rc=124 elapsed=16s` (HANG) | `rc=64 elapsed=0s` same message |

Both the sweep's run and the lane's red-before reproduce. `probe:177` `fixture_st = os.stat(fixture_path)`,
`probe:181` `if not stat.S_ISREG(fixture_st.st_mode):`, `probe:184` `with open(fixture_path) as f:` — the anchors
are where the report says. The `os.path.exists` -> `os.stat` swap also fixes the descriptor leak of
`json.loads(open(path).read())`. SOLID.

**`_sha256_file`'s guard is reachable from the LIVE entry point — I proved it a way the lane did not.** The lane's
mutant 13 drove `_sha256_file` through a synthetic `sha_driver.py`; that is a unit-level exercise, not a
reachability proof. I built the production-shaped attack instead: an agent that replaces its OWN entrypoint with a
FIFO (`os.unlink(__file__); os.mkfifo(__file__)`) before answering — the same capability the repo's existing
self-deleting-agent test already assumes.

```
PARENT: rc=124 elapsed=15s   (HANG in _sha256_file's open(); runtime-identity.json ABSENT, env.json ABSENT,
                              timeline.jsonl ABSENT — zero evidence)
PIN:    rc=1   elapsed=0s    acp_probe: OSError: not a regular file: <agent path>
                              probe_error = 'OSError: not a regular file: <agent path>'
                              agent_entrypoint_sha256 = None
```
The guard `probe:52` `if not stat.S_ISREG(os.stat(path).st_mode):` is live and reachable, and converts a total
evidence loss into a named `probe_error`. SOLID.

### Item 2, continued — the write side (the lane's D1), measured on all FOUR outputs

The lane measured two output paths. I measured all four, on both venues (FIFO planted at the path before the run,
probe under `timeout 12`):

| FIFO planted at | parent `2823f05` | PIN `9aaefd0a` |
|---|---|---|
| `agent-stderr.txt` | `rc=0 elapsed=3s` | `rc=0 elapsed=4s`, **`probe_error` ABSENT** |
| `runtime-identity.json` | `rc=124 elapsed=12s` | `rc=124 elapsed=12s` (HANG) |
| `env.json` | `rc=124 elapsed=12s` | `rc=124 elapsed=12s` (HANG) |
| `timeline.jsonl` | `rc=124 elapsed=12s` | `rc=124 elapsed=12s` (HANG) |

D1 is confirmed and is WIDER than the report states: three of the four evidence writes hang, not one.

### Item 2, continued — a FIFTH read receiver the class table calls GUARDED but is not

The class table marks `probe:52` (`_sha256_file`'s `S_ISREG` guard) as covering "all three receivers". At receiver
1 — the probe's own file, read unguarded at `probe:122` `"probe_sha256": _sha256_file(os.path.realpath(__file__)),`
and again at `probe:483` `"probe_sha256": _sha256_file(os.path.realpath(__file__)),` — the guard does not close the
class at the outermost boundary. An agent that makes the probe's own script non-regular mid-run (it can read the
path from `/proc/<ppid>/cmdline`; I passed it in the env to keep the probe deterministic):

```
probe file UNLINKED   parent: rc=1 0s  Traceback x2, runtime-identity.json NO env.json NO timeline.jsonl NO
probe file UNLINKED   PIN:    rc=1 0s  Traceback x2, runtime-identity.json NO env.json NO timeline.jsonl NO
probe file -> FIFO    parent: rc=124 15s (HANG)  zero evidence files
probe file -> FIFO    PIN:    rc=124 15s (HANG)  zero evidence files
```
Mechanism on the PIN, re-derived from primary source, one hop per line:
- `probe:122` `"probe_sha256": _sha256_file(os.path.realpath(__file__)),` raises the guard's OSError;
- it escapes `_write_evidence`, because only the entrypoint hash is wrapped: `probe:115` `agent_entrypoint_sha256 = _sha256_file(agent_realpath)`;
- the last-resort handler catches it: `probe:477` `except Exception as exc:`;
- and immediately re-runs the same unguarded read: `probe:483` `"probe_sha256": _sha256_file(os.path.realpath(__file__)),`.
The second OSError is raised
*inside* the `except`, so CPython prints a traceback -> the traceback printer calls `linecache.getline()` on the
probe's source, which `open()`s the FIFO and blocks forever. The stderr file confirms it: it contains
`Traceback (most recent call last):` and `File ".../acp_probe.py", line 469, in main` and then stops — killed
mid-print while linecache was blocked.

## Item 3 — #10, the drain failure recorded

Reproduced (my rig, `env -i`, probe under `timeout 20`):

```
PARENT, directory at agent-stderr.txt   -> rc=0  probe_error = '<ABSENT>'          (the sweep's red-before)
PIN,    directory at agent-stderr.txt   -> rc=1  probe_error = "stderr drain failed: IsADirectoryError:
                                                  [Errno 21] Is a directory: '<framedir>/agent-stderr.txt'"
PIN,    self-deleting agent only        -> rc=1  probe_error = "FileNotFoundError: [Errno 2] No such file or
                                                  directory: '<agent>'"   agent_entrypoint_sha256 = None
PIN,    BOTH planted                    -> rc=1  probe_error = "stderr drain failed: IsADirectoryError: ..."
                                                  agent_entrypoint_sha256 = None   <- the ONLY residual of error 2
```
Exact message reproduced. **Which survives:** the drain error, because the fold
`probe:461` `if drain_error[0] is not None and probe_error is None:` runs before
`_write_evidence` and both use `if probe_error is None`. The entrypoint error's *message* is lost; a residual
signal (`agent_entrypoint_sha256: null`) survives, so that pairing is recoverable.

**A pairing where the second error is lost with NO residual at all** — planted with the repo's own BrokenPipe
monkeypatch shape plus a directory at `agent-stderr.txt`:
```
rc=1   probe_error = 'BrokenPipeError: agent process exited before c2a write landed'
       identity keys = [agent_argv, agent_child_pid, agent_entrypoint_sha256, agent_exit_code,
                        agent_interpreter_realpath, agent_interpreter_sha256, agent_realpath, probe_error,
                        probe_path, probe_sha256, python_dont_write_bytecode, spawned_at_utc]
```
The `IsADirectoryError` is nowhere in the evidence. Any earlier `probe_error` (BrokenPipe, an interpreter-sample
failure) re-creates exactly the swallow #10 set out to remove.

## Item 4 — #23, the lossless copy

Reproduced end-to-end with an agent emitting the sweep's exact byte
(`b'{"jsonrpc":"2.0","id":0,"error":{"code":-32602,"message":"Invalid par\xffams"}}\n'`):

```
PARENT lossy: keys = ['dir','frame','seq','t_mono_ns','t_utc']                       (raw_b64 ABSENT — red-before)
PIN    lossy: keys = ['dir','frame','raw_b64','seq','t_mono_ns','t_utc']
              raw  = b'{"jsonrpc":"2.0","id":0,"error":{"code":-32602,"message":"Invalid par\xffams"}}\n'  (exact)
PIN    clean: keys = ['dir','frame','seq','t_mono_ns','t_utc']                        (negative control holds)
```
Strict-then-replace order confirmed: `probe:373` `text = line_bytes.decode("utf-8")` first, and only in the
`probe:375` `except UnicodeDecodeError:` branch does `probe:376` `text = line_bytes.decode("utf-8", errors="replace")` run.

**The invalid-escape case the brief asked for.** A line whose BYTES are valid UTF-8 but whose JSON string carries
a lone-surrogate escape `\udc80`: `json.loads` **does not raise** (CPython's json accepts lone surrogates), so
`lossy=False`, the frame branch is taken, and no `raw_b64` is kept. That is CORRECT here — nothing was lost:
`timeline.jsonl` is written with the default `ensure_ascii=True`, and `od -c` shows the bytes round-trip as the
literal escape `"\udc80"`. No finding.

### Item 4, continued — the report's consumer claim is about the WRONG consumer

The report's DISCREPANCIES "Consumer contract" block and its self-attack A2 rest on running
`check_acp_conformance.check_timeline()` over a synthetic entry and observing
`timeline entry at seq 2 has unexpected keys [...]`. **A probe capture never reaches `check_timeline`.** Traced
from the live entry point with three independent instruments:

1. Call-site enumeration: `check_timeline` is invoked at exactly one place,
   `proofs/S0-01/check_acp_conformance.py:1739` `c2a_split, a2c_split = _run_check(check_timeline, leg, entries, leg, d)`,
   inside the `for leg in LEGS:` POSITIVE-leg loop (`:1727`).
2. Shape: that loop's `_LEG_REQUIRED_FILES` (`:1718-1725`) is 20 files — `frames-client-to-agent.jsonl`,
   `tee-status.json`, `buzz-acp.pid` ... — the `frame_tee.py`/`run_leg.sh` product. The probe writes four files.
   `check_timeline` itself `_require_file`s the two `frames-*.jsonl` at `:296-297`. The report saw this and
   explained it away as "my synthetic dir's missing sibling file".
3. The probe's leg goes through `check_negative` (`:1485`, called at `:1789`), which delegates at `:1494` to
   `negative_contract.validate_negative_dir`. Its key check:
   `proofs/S0-01/negative_contract.py:103` `if set(e) - {"seq", "dir", "t_utc", "t_mono_ns", "frame", "raw", "raw_b64", "delivered"}:` —
   **`raw_b64` is already allowed.**

Empirical confirmation — the REAL consumer run against my REAL PIN captures:
```
PIN lossy capture   entry keys ['dir','frame','raw_b64','seq','t_mono_ns','t_utc']
  validate_negative_dir -> NegativeFailure: agent error is code=-32602 message='Invalid par�ams',
                            expected code=-32602 message='Invalid params'
```
It is NOT a key-set rejection; the real consumer already fails closed on the mangled TEXT and prints the
replacement character in the message. So the brief's item-4 ruling premise ("`check_timeline` REJECTS a lossy
entry with `unexpected keys` ... rule whether it should be a named checker failure rather than a key-set message")
does not apply to this producer, and the A5k hand-off the report proposes is aimed at the wrong file.

## Item 5 — #34, the mirror pinned

```
probe pattern = (?i)(KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV)
pins  pattern = (?i)(KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV)
equal = True
```
`test:2291` `assert acp_probe._REDACTED_ENV_KEY_RE.pattern == REDACTED_ENV_KEY_RE, (` asserts the equality;
`test:2295` `assert not _re.search(r"^\s*(import|from)\s+pins\b", PROBE.read_text()` is the negative control on
the wrong fix. Static check on the PIN
bytes: the probe's only `pins` mentions are two comments (`probe:34`, `probe:84`) — no import. SOLID.

**Why the probe must stay import-free — verified from primary source, and the brief's stated reason is wrong.**
The production launcher, read at the PIN (the working-tree copy has moved, so these lines are the PIN's):
`proofs/S0-01/tools/pc/pc_negative.py:27` `rc = subprocess.run(["/usr/bin/python3", os.path.join(REPO, "proofs/S0-01/tools/acp_probe.py")], env=env).returncode`,
with `env` built as a hermetic dict at `proofs/S0-01/tools/pc/pc_negative.py:21-26` `"PATH": pins.PINNED_PATH, "HOME": pins.PINNED_HOME,`
(PATH/HOME/HERMES_HOME/PYTHONDONTWRITEBYTECODE/OMNIROUTE_API_KEY/S0_01_AGENT/S0_01_FRAMEDIR) — **no `PYTHONPATH`**.
So the probe's `sys.path[0]` is its own directory,
`proofs/S0-01/tools/`, and `pins.py` sits one level up in `proofs/S0-01/`. Reproduced:
```
script-in-tools: sys.path[0]= .../proofs/S0-01/tools
IMPORT pins: ModuleNotFoundError No module named 'pins'
```
The constraint is REAL. It is NOT "a pinned venv where pins.py is not on the path" (the brief's wording) — the PC
launch uses the SYSTEM interpreter `/usr/bin/python3` and the reason is `sys.path[0]` plus a `PYTHONPATH`-free
env. Correcting the reason matters for the next edit: adding `PYTHONPATH` to `pc_negative.py`'s env dict, or
moving the probe up one directory, would silently dissolve the constraint the test's second assertion protects.

## Item 6 — #39, the timeout domain

All 14 forms the brief enumerates, plus the sweep's 11+4, run against the PIN probe (`env -i`, one process each):

```
1e3      rc=64 not a valid number: '1e3'        NaN      rc=64 must be a finite float > 0, got 'NaN'
+30      rc=64 not a valid number: '+30'        Infinity rc=64 must be a finite float > 0, got 'Infinity'
.5       rc=64 not a valid number: '.5'         -0       rc=64 must be a finite float > 0, got '-0'
5.       rc=64 not a valid number: '5.'         0.0      rc=64 must be a finite float > 0, got '0.0'
٣٠       rc=64 not a valid number: '٣٠'         1e400    rc=64 must be a finite float > 0, got '1e400'
'30\n'   rc=64 not a valid number: '30\n'       '30\r'   rc=64 not a valid number: '30\r'
' 30'    rc=64 not a valid number: ' 30'        '\t30'   rc=64 not a valid number: '\t30'
0x1p3    rc=64 not a valid number: '0x1p3'      '30 '    rc=64 not a valid number: '30 '
1_000    rc=64 not a valid number: '1_000'      ''       rc=64 not a valid number: ''
3_0      rc=64   ' 30 '  rc=64   30s rc=64   0x10 rc=64   nan/inf/-5/0 rc=64   1.5.0 rc=64
'9'*400  rc=64 must be a finite float > 0, got '999...'          007/30/0.5/5.25  rc=0
```
D3 (the 400-digit overflow to inf) reproduced. The final-value guard: `probe:236` `if not math.isfinite(timeout) or timeout <= 0:`.
The case is parametrised into the suite: `test:2313` `pytest.param("9" * 400, "must be a finite float > 0, got '%s'" % ("9" `.
A real find beyond the sweep's row. SOLID.
(One self-correction: my first `'30\n'` run showed rc=0. That was my own bash artifact — `$( )` strips trailing
newlines, so the probe received `'30'`. Re-run with `$'30\n'`: rc=64. The report is right; my first run was not.
`ACP_PROBE_TIMEOUT=$'30\x00'` also reads rc=0, but `env -i X=$'30\x00' python -c` shows the process receives
`'30'` — execve truncates at the NUL, so there is no NUL input to reject. Not a finding.)

### Item 6, continued — DEVIATION 2: the message MISNAMES a whole class

The reject branch opens at `probe:225` `if _TIMEOUT_DOMAIN_RE.fullmatch(timeout_raw) is None:` and calls `float()`
once to pick between two pre-existing wordings. The
discriminator is "does `float()` parse it to a finite positive number", which is NOT the reason for rejection.
Result: every form that is a perfectly valid Python number but outside the pinned SYNTAX is told it "is not a
valid number".

Failing inputs: `ACP_PROBE_TIMEOUT=1e3` -> `acp_probe: ACP_PROBE_TIMEOUT is not a valid number: '1e3'`.
1e3 IS a valid number (1000.0); the real reason is "not plain decimal digits". Same for `+30`, `.5`, `5.`,
`1_000`, `3_0`, `' 30 '`, `'30\n'`, `٣٠`. The inconsistency is visible inside the feature itself: `1e400` — also
scientific notation, also outside the syntax — gets the OTHER message ("must be a finite float > 0"), purely
because `float()` overflows. An operator debugging `1e3` is told something false.

Minimal fix (keeps both pinned wordings for the cases that already own them): in the reject branch, when
`rejected is not None and math.isfinite(rejected) and rejected > 0`, emit a third wording, e.g.
`ACP_PROBE_TIMEOUT must be plain decimal digits (e.g. '30' or '0.5'), got {timeout_raw!r}`; leave `float()`-raises
forms on "is not a valid number" and non-finite/non-positive forms on "must be a finite float > 0".
Exact red test: extend `test:2302` `@pytest.mark.parametrize` with
`("1e3", "must be plain decimal digits (e.g. '30' or '0.5'), got '1e3'")` — it fails on the PIN with
`AssertionError` naming the current wording. SOLID (measured, 9 failing inputs). Severity: diagnostic only; the
rejection SET and the exit code are correct, so nothing fails open.

## Item 7 — #40, the runtime state

Recorded value vs an independent oracle (a child CPython launched with the same flags/env reporting its own
`sys.dont_write_bytecode`), read from `runtime-identity.json`:

```
-B, env UNSET       recorded=True   cpython_truth=True   match=YES     <- the brief's case
no flag, env UNSET  recorded=False  cpython_truth=False  match=YES
env=1               recorded=True   truth=True   YES     env=2      recorded=True   truth=True   YES
env=true            recorded=True   truth=True   YES     env=0      recorded=False  truth=False  YES
env=<empty>         recorded=False  truth=False  YES     -B, env=0  recorded=True   truth=True   YES
```
The `-B` case the brief asked for records true. The second site is `probe:491` `"python_dont_write_bytecode": sys.dont_write_bytecode,`
in the last-resort handler; it also records the runtime state — driven by planting a directory at `env.json` so
`_write_evidence` raises into it:
`M3 rid python_dont_write_bytecode = True` under `-B`. SOLID.
Note: the suite's parametrisation covers env VALUES only; the `-B`-flag case and the M3 site are proven by my runs,
not by a committed test. Not a defect — a coverage note.

## Items 8 / 11 — the mutant audit (22 rows: the lane's 13 re-run + 9 of mine)

Every mutant applied to a fresh minimal tree under my scratchpad (`proofs/` + `tests/test_s0_01_acp_probe.py` from
`git archive` of the PIN or of the parent), by an exact-string patcher that ABORTS unless the anchor appears
exactly once, with an explicit `--basetemp`. The shared repo tree was never touched. `ran` = executed here.

| # | mutant | src | ran | outcome | killer line / evidence |
|---|---|---|---|---|---|
| M1 | FIXTURE-FIFO-UNGUARDED (`if not stat.S_ISREG(fixture_st...)` -> `if False:`) | PIN | yes | KILLED | `E subprocess.TimeoutExpired: ... timed out after 5 seconds` -> `1 failed, 79 deselected in 5.59s` |
| M2 | DRAIN-SWALLOW (`error_slot[0] = ...` -> `pass`) | PIN | yes | KILLED | `E AssertionError: expected exit 1, got 0:` -> `1 failed, 79 deselected in 0.59s` |
| M3 | LOSSY-NO-RAW (`if lossy:` -> `if False:`) | PIN | yes | KILLED | `E AssertionError: the lossless copy of a replaced-byte line is missing: [...]` -> `1 failed, 1 passed, 78 deselected` |
| M4 | MIRROR-DRIFT (`NSEC` -> `NSECX`) | PIN | yes | KILLED | `E AssertionError: probe copy '(?i)(KEY|TOKEN|SECRET|PASSWORD|NSECX|PRIV)' has drifted ...` |
| M5 | TIMEOUT-LENIENT (domain gate -> `if False:`) | PIN | yes | KILLED | `E AssertionError: expected exit 64 for '3_0', got 0` -> `6 failed, 9 passed, 65 deselected in 3.18s` |
| M6 | BYTECODE-STRING (both sites -> `os.environ.get(...) == "1"`) | PIN | yes | KILLED | `E AssertionError: PYTHONDONTWRITEBYTECODE='2': recorded False, CPython reports True` -> `2 failed, 4 passed, 74 deselected` |
| M7 | ORDINAL-99 (the sweep's R10a) on the PARENT test | parent | yes | **SURVIVED — by design, it IS the red-before** | `1 passed, 52 deselected in 0.29s` |
| M8 | ORDINAL-99 equivalent on the PIN test (fake gated on a path that never matches) | PIN | yes | KILLED | `E AssertionError: the early sha256 failure never fired — ... (AF-AP-57 vacuity)` |
| M9 | DL-INLINE (`_EARLY_SAMPLE_DEADLINE_S` inlined as `0.2`) | PIN | yes | KILLED | `E AssertionError: RL_CALLS=96 DEADLINE_SEEN=0.0` -> `1 failed, 79 deselected in 6.52s` |
| M10 | AP-F1a-SINGLE-SHOT (early retry loop -> one attempt) | PIN | yes | KILLED | `E AssertionError: expected exit 0 (retry recovered), got 1: acp_probe: interpreter sample failed: transient failure` |
| M11 | LATE-NULL (late readlink failure nulls the early reading) | PIN | yes | KILLED | `E AssertionError: assert None == '/usr/bin/python3.11'` |
| M12 | LATE-EVERY (in-loop `if not _late_sampled:` -> `if True:`) | PIN | yes | KILLED | `E AssertionError: expected exactly 2 child /proc/<pid>/exe reads ...: 'CALL2=...\nRL_CALLS=3\n'` |
| M13 | SHA-GUARD-OFF (guard removed inside `_sha256_file`) | PIN | yes | KILLED | `E subprocess.TimeoutExpired: ... sha_driver.py ... timed out after 5 seconds` -> `1 failed, 79 deselected in 5.24s` |
| M14 | NO-ISFINITE (accept branch -> `if timeout <= 0:`) | PIN | yes | KILLED (full file) | `FAILED ...::test_probe_timeout_rejects_forms_outside_the_domain[digits400_overflows_to_inf]` -> `1 failed, 79 passed in 55.16s` |
| M15 | LSTAT-FIXTURE (`os.stat` -> `os.lstat` on the fixture) | PIN | yes | SURVIVED — **equivalent-or-stricter** | `80 passed in 49.96s`; I checked the direction: `lstat` on a symlink returns S_IFLNK, so the guard gets STRICTER (a symlink to a FIFO is still rc 64 in 0s, measured). Untested delta = a symlink to a REGULAR fixture would be rejected. No fail-open. |
| M16 | LSTAT-SHA (`os.stat` -> `os.lstat` inside `_sha256_file`) | PIN | yes | SURVIVED — same class as M15 | `80 passed in 43.20s` |
| M17 | LOSSY-ALWAYS (`if lossy:` -> `if True:`) | PIN | yes | KILLED (full file) | `E AssertionError: raw_b64 on a clean line: {...}` -> `1 failed, 79 passed in 43.74s` |
| M18 | DRAIN-EMPTY-MSG (record `""` instead of the exception text) | PIN | yes | KILLED (full file) | `E AssertionError: got 'stderr drain failed: '` -> `1 failed, 79 passed in 47.92s` |
| M19 | BYTECODE-M3-ONLY (revert only the handler's `probe:491` `"python_dont_write_bytecode": sys.dont_write_bytecode,`) | PIN | yes | **SURVIVED — real coverage gap** | `80 passed in 46.59s` |
| M20 | FIRST-ERROR-WINS-OFF (`and probe_error is None` dropped from the drain fold, `probe:461`) | PIN | yes | **SURVIVED — real coverage gap** | `80 passed in 43.80s` |
| M21 | JOIN-ZERO (`probe:457` `stderr_thread.join(timeout=3)` -> `timeout=0`) | PIN | yes | **SURVIVED — real coverage gap** | `80 passed in 47.23s` |
| M22 | TIMEOUT-MSG-SWAP (the two wordings exchanged) | PIN | yes | KILLED (full file) | `18 failed, 62 passed in 46.56s` |

17 killed / 1 survivor by design / 2 equivalent-or-stricter / **3 real survivors (M19, M20, M21)**.

Stability (item 8, re-run by me on the box as it is, load average 3.67 / 5.49 / 5.23 on 4 cores):
```
run1..run10:  4 passed, 76 deselected in 0.73-0.92s   [exit 0]  (10/10)
```
The `RL_CALLS` mechanism assertions are stable under heavier load than the lane measured. SOLID.

## Item 9 — SWEEP-tests 13.1, the SAFE ruling

**AGREE, SAFE.** `test:785` `probe_exe = os.readlink(f"/proc/{os.getpid()}/exe")` reads the TEST process's own
live pid, synchronously, from inside that process. The AF-AP-55 hazard is a child that exits or execs between the
spawn and the read; a process cannot exit while executing this line and CPython never execs mid-test, so the race
window does not exist. Its use is a negative control:
`test:786` `assert rid["agent_interpreter_realpath"] != probe_exe, (`. Added nuance the sweep did not state: the control
discriminates only because the agent is a `#!/bin/bash` script the test WRITES itself at `test:773-780`, so
`/proc/<child>/exe` is `/bin/bash` by construction, not by luck. No change needed.

## Item 10 — the PC gate (the carve-out)

Clean detached worktree of the PUSHED pin, `.pc-bridge.env` copied in, nothing else on the bridge:
```
$ git rev-parse HEAD            -> b4257f8c78f2db8867ad519f8c99fbc46bf90543
$ git status --porcelain        -> (empty)
$ scripts/pc_suite.sh launch -n 8 -- tests/test_s0_01_acp_probe.py tests/test_s0_01_negative_contract.py
pc_suite: launched 20260908T032705Z-b4257f8 on the PC — base b4257f8c78f2db8867ad519f8c99fbc46bf90543
          + patch 0B (sha e3b0c44298fc), set 'tests/test_s0_01_acp_probe.py tests/test_s0_01_negative_contract.py', -n 8
$ scripts/pc_suite.sh wait 20260908T032705Z-b4257f8 8
pytest-exit: 0
pytest-summary: 135 passed in 8.34s
```
`patch 0B` proves the PC ran the pushed pin's exact bytes. Count integrity checked, not assumed: the sandbox gives
`80 passed` for `test_s0_01_acp_probe.py` and `55 passed in 0.26s` for `test_s0_01_negative_contract.py` — 80+55 =
135, so the PC's 135 is the whole declared set, not a filter that matched nothing. The worktree was removed
(`git worktree remove --force`); `git worktree list` back to the 6 other lanes'. AGREE with the lane's sandbox
line; the PC venue adds nothing new.

## Item 13 — the design question

**No. The read side is closed by a GREP in a report, not by a self-scan the next edit cannot drift past.**
- The checker has the instrument
  `tests/test_s0_01_check_acp_conformance.py:4718` `def test_ck11_every_read_is_under_the_walk_or_require_file():`,
  which AST-walks `check_acp_conformance.py`,
  `negative_contract.py` and `check_initialize.py`, finds every `open`/`read_text`/`read_bytes` call, and asserts
  each is `_require_file`d, S_ISREG-guarded within 5 lines, or under a walked root.
- `tests/test_s0_01_acp_probe.py` on the PIN contains **no `ast` import at all** (grep: zero hits). The lane's
  class table is a `grep -n` pasted into a markdown file. Add a receiver next to `probe:200` `child_pid = None`
  tomorrow and every gate stays green.

I enumerated the receivers myself on the PIN bytes. The reads:
- `probe:55` `with open(path, "rb") as f:` — guarded two lines above;
- `probe:184` `with open(fixture_path) as f:` — guarded by `probe:181` `if not stat.S_ISREG(fixture_st.st_mode):`;
- three `os.readlink("/proc/%d/exe" % proc.pid)` calls, `probe:268` / `probe:341` / `probe:432`, which cannot block.
That part is genuinely complete today.

**The same self-scan should cover the WRITE side, and the lane's proposed fix does not cover it.** The write
receivers on the PIN are EIGHT, not four:
`probe:73` `with open(stderr_path, "wb") as f:` · `probe:101` `with open(os.path.join(framedir, "env.json"), "w") as f:` ·
`probe:137` `with open(os.path.join(framedir, "runtime-identity.json"), "w") as f:` · `probe:145` `with open(tl_path, "w") as f:` ·
**`probe:239` `with open(os.path.join(framedir, "runtime-identity.json"), "w") as f:`** (the timeout-reject path) ·
`probe:497` `with open(rid_path, "w") as f:` · `probe:503` `with open(tl_path, "w") as f:` ·
`probe:509` `open(stderr_path, "wb").close()` (unreachable with a FIFO present — gated on `not os.path.exists`).
The site `probe:239` `with open(os.path.join(framedir, "runtime-identity.json"), "w") as f:` is a hang the
report's own recommendation ("_open_regular for the four evidence writes + the M3 handler's rescue-write path")
would miss. Proved:
```
FIFO at runtime-identity.json + ACP_PROBE_TIMEOUT='30s'   -> rc=124 elapsed=10s  (hang at the early rid write)
control, no FIFO, same rejected timeout                    -> rc=64 'ACP_PROBE_TIMEOUT is not a valid number: '30s''
```

## Item 0, the requested RULING — DEVIATION 1 (AF-AP-57 = 1, not 0)

**Ruling: the count is a legitimate exception, the lane was right not to dodge the regex, and the three named
guards are NOT sufficient on their own — a fourth, unnamed guard is what actually kills the attack.**

Why the count is legitimate: the property under test is
`test:1402` `def test_probe_early_retry_recovers_from_transient_readlink_failure(tm` — the early loop retries across
K transient failures. "Transient" is defined by a count; the loop is a tight `time.sleep(0.002)` spin in the main
thread before the drain thread exists, so there is no observable PHASE that separates attempt 1 from attempt 4.
A phase gate is not available here, and rewriting the fake to dodge the regex would be a hollow green in the
screen — the lane's refusal is correct.

Why the three guards are insufficient — **the mutant that fools it, RUN**: `M23-EXTRA-EARLY-READ`, an unguarded
extra readlink of the child's `/proc/<pid>/exe` inserted right after `probe:250` `child_pid = proc.pid`. That is
exactly the AF-AP-57 hazard: a shape change shifts every ordinal, so the fake's three failures are consumed one
call earlier and the early loop only ever retries twice — while the TOTAL stays 5.
```
M23, the flagged fake alone (-k early_retry_recovers):   1 passed, 79 deselected in 0.30s   <- FOOLED
M23, the whole file:                                     4 failed, 76 passed in 44.30s
   killer: E AssertionError: RL_CALLS=3 DEADLINE_SEEN=0.0  (test_probe_post_loop_sha256_failure_truthful_error)
```
So `RL_CALLS=5` pins a TOTAL, and a redistribution that preserves the total walks straight through. What kills M23
is the NEIGHBOURING phase-gated tests that pin the read count from a different angle
(`test_probe_post_loop_sha256_failure_truthful_error` -> `RL_CALLS=2`,
`test_probe_interpreter_is_sampled_once_at_the_first_a2c_byte` -> `RL_CALLS=2`). The report's DEVIATION 1 names
three guards; the load-bearing one is the fourth it does not name.

Minimal strengthening (no redesign, ~3 lines): have the fake record the call index at which it first SUCCEEDED and
assert the DISTRIBUTION, not the total — `print(f"FIRST_OK={_rl_calls[0]}")` inside the `return _orig_readlink(path)`
path on the first non-failing child read, and `assert "FIRST_OK=4" in r.stdout.splitlines()`. Under M23 that reads
`FIRST_OK=5` and the flagged test kills its own mutant. Exact red test: apply M23 and run
`-k early_retry_recovers`; it must go from `1 passed` to `1 failed`.
Verdict on the screen count: AF-AP-57 = 1 is ACCEPTABLE as REVIEWED-SAFE with the strengthening above, not as-is.

### A tooling finding found while grading this: the AF-AP-57 screen under-reports

`.claude/hooks/edit-snapshot.py:186` — the pattern is
`\bif\s+(?:not\s+)?\w*(?:calls?\[0\]|call_count|n_calls|attempts?\[0\])\s*(?:==|!=|<=|>=|<|>)\s*\d`.
The `call_count` alternative has no `\[0\]` suffix option, so `if _call_count[0] <= 3:` does NOT match. Measured:
on the parent, `ap_screen.py --tests` reports ONE hit (`:1681`) while my own broad grep finds FIVE ordinal-gate
lines in four fakes (`:1428`, `:1681`, `:1793`, `:1912`, `:1915`). The screen missed 3 of the 4 fakes. The lane's
"AF-AP-57 fires on the PIN at :1681" and its "1 hit" on the child are both true readings of a leaky instrument;
the class closure the lane actually did (4 fakes found, 3 converted) came from its own grep, not the screen.
Minimal fix: `(?:calls?|call_count|n_calls|attempts?|count)\s*(?:\[0\])?` in the alternation.
Exact red test: add `if _call_count[0] == 1:` to a fixture file under `tests/red/` and assert `ap_screen --tests`
reports it. (Out of the lane's two-file scope — a coordinator/tooling item.)

## FINDINGS — all of them, no severity filter

**F1 — SWEEP row #10's class is closed only for drain failures that RAISE; one that BLOCKS is still swallowed.**
Sites: `probe:73` `with open(stderr_path, "wb") as f:`
· `probe:457` `stderr_thread.join(timeout=3)`
· `probe:461` `if drain_error[0] is not None and probe_error is None:`.
Failing input: `mkfifo <framedir>/agent-stderr.txt`, then run the probe normally.
Expected (the row's own contract): rc 1 and a `probe_error` naming the failure.
Observed on the PIN: `rc=0 elapsed=4s`, `probe_error = '<ABSENT>'`, `agent-stderr.txt` a 0-byte FIFO, all other
evidence written — byte-for-byte the signature the sweep pinned as the DEFECT. Mechanism: opening a FIFO for
write blocks until a reader appears, so `except Exception` never fires and `error_slot[0]` stays `None`; the
`join(timeout=3)` returns with the thread still alive and NOTHING checks `is_alive()`.
The lane DID measure this (D1, first row) but filed it as an out-of-scope write-side residual rather than as
"row #10 is half-closed". Minimal fix (3 lines, no redesign):
```python
        stderr_thread.join(timeout=3)
        if stderr_thread.is_alive() and drain_error[0] is None:
            drain_error[0] = "drain did not finish in 3s (stderr path may not be a regular file)"
```
Exact red test: parametrise `test_probe_reports_a_stderr_drain_failure` over `("dir", "fifo")`; the `fifo` case
must go from `rc 0 / no probe_error` to `rc 1 / probe_error names it`. **SOLID (reproduced).**

**F2 — the drain error is lost with no residual whenever any earlier probe_error is live.**
Site: `probe:461` `if drain_error[0] is not None and probe_error is None:` — the fold is skipped. Failing input: the repo's own BrokenPipe monkeypatch
shape plus a directory at `agent-stderr.txt`. Expected: both failures visible. Observed:
`probe_error = 'BrokenPipeError: agent process exited before c2a write landed'`, the `IsADirectoryError` absent
from every identity key. (With a self-deleting agent instead, the entrypoint error's message is also dropped but
`agent_entrypoint_sha256: null` survives as a residual — a partial loss.) Minimal fix: on the shadowed path append
rather than skip — `probe_error = f"{probe_error}; stderr drain failed: {drain_error[0]}"` (keeps the pinned
identity key set, so no `pins.py` change). Exact red test: the BrokenPipe + drain-dir pairing above, asserting both
substrings. **SOLID (reproduced).**

**F3 — the report's cross-tool consumer analysis names the WRONG consumer, and the A5k hand-off it proposes is
misaimed.** The line `proofs/S0-01/negative_contract.py:103` `if set(e) - {"seq", "dir", "t_utc", "t_mono_ns", "frame", "raw", "raw_b64", "delivered"}:`
already allows `raw_b64`, and the probe's leg goes through
`proofs/S0-01/check_acp_conformance.py:1789` `neg_observed = _run_check(check_negative, "negative", neg_dir)`
into `proofs/S0-01/check_acp_conformance.py:1494` `observed = nc.validate_negative_dir(neg_dir, _fixtures())`,
never through `check_timeline` (single call site, positive legs only). Observed with the real consumer on my real PIN
capture: not a key-set rejection but
`NegativeFailure: agent error is code=-32602 message='Invalid par<U+FFFD>ams', expected ... message='Invalid params'`.
Minimal fix: replace the report's "Consumer contract" block and A2 with the `validate_negative_dir` result, and
re-aim the A5k suggestion (if any is still wanted) at `negative_contract.py` — e.g. name the cause when an entry
carries `raw_b64`. **SOLID (reproduced, three instruments).**

**F4 — the class table's "GUARDED - one guard covers all three receivers" is false at the outermost boundary for
receiver 1 (the probe's own file).** `probe:122` and `probe:483` call `_sha256_file(os.path.realpath(__file__))`
with no `try`. Failing input: an agent that replaces the probe's own script with a FIFO (path discoverable from
`/proc/<ppid>/cmdline`). Expected after the round: a named `probe_error`, bounded. Observed on the PIN:
`rc=124 elapsed=15s` — a hang, zero evidence files — identical to the parent. Mechanism: the guard's OSError
escapes `_write_evidence`; the last-resort handler `probe:477` `except Exception as exc:` re-runs the same
unguarded read `probe:483` `"probe_sha256": _sha256_file(os.path.realpath(__file__)),`; the second OSError is
raised inside the `except`, and the traceback printer's `linecache` blocks opening the FIFO.
With a plain unlink instead of a FIFO: rc 1, traceback, and `runtime-identity.json` / `env.json` /
`timeline.jsonl` all ABSENT — the M3 "write all four files" invariant broken (pre-existing on the parent too).
Minimal fix: compute `probe_sha256` ONCE at import time into a module global inside a `try`, and have both
`_write_evidence` and the M3 handler read that global. Exact red test: an agent that does
`os.unlink(probe_path); os.mkfifo(probe_path)`; assert rc == 1 within 5 s and all four files present.
**SOLID (reproduced, both venues).**

**F5 — D1 is wider than the report states, and the fix the report proposes would miss a site.** Measured on the
PIN: a FIFO at `runtime-identity.json`, `env.json` and `timeline.jsonl` each hangs (`rc=124`), only
`agent-stderr.txt` is the rc-0 swallow. There are eight write receivers, not four: `probe:73` `with open(stderr_path, "wb") as f:`
and the seven enumerated in the item-13 section above, of which
`probe:509` `open(stderr_path, "wb").close()` is unreachable with a FIFO present (gated on `not os.path.exists`). `probe:239` is the timeout-reject path's early `runtime-identity.json` write and is NOT one of "the four
evidence writes" the report's `_open_regular` proposal enumerates. Proved:
`FIFO at runtime-identity.json + ACP_PROBE_TIMEOUT='30s'` -> `rc=124 elapsed=10s`; control -> `rc=64` named.
Minimal fix: `_open_regular(path, mode)` applied at all seven reachable write sites, and the next brief should
name them by line. **SOLID (reproduced).**

**F6 — the deviation-2 message misnames a whole class of rejected values.**
Site: `probe:233` `msg = f"ACP_PROBE_TIMEOUT is not a valid number: {timeout_raw!r}"`.
Failing input: `ACP_PROBE_TIMEOUT=1e3`
-> `acp_probe: ACP_PROBE_TIMEOUT is not a valid number: '1e3'`. 1e3 IS a valid number; the reason is "outside the
pinned syntax". Same for `+30`, `.5`, `5.`, `1_000`, `3_0`, `' 30 '`, `'30\n'`, `٣٠` (9 measured). The feature
contradicts itself: `1e400`, also scientific notation, gets the OTHER wording purely because `float()` overflows.
Minimal fix + exact red test: in the reject branch add a third wording when the value parses finite and positive,
and extend the parametrisation `test:2302` `@pytest.mark.parametrize("raw,expected", [`
with `("1e3", "must be plain decimal digits (e.g. '30' or '0.5'), got '1e3'")`.
Diagnostic only — the rejection SET and exit code are correct. **SOLID (reproduced).**

**F7 — the M3 handler's `python_dont_write_bytecode` site is untested.** `probe:491`. Mutant M19 reverts ONLY that
site to the string mirror: `80 passed in 46.59s` — the full suite does not notice. I proved by hand that the site
is correct today (driven via a directory at `env.json`, `-B` set: `M3 rid python_dont_write_bytecode = True`), but
nothing pins it. Minimal fix / exact red test: extend
`test_identity_records_the_runtime_bytecode_state_not_the_string` with a case that forces the M3 path (plant a
directory at `env.json`) and read the same key. **SOLID (mutant run).**

**F8 — "first error wins" is an unpinned claim.** `probe:461`. Mutant M20 drops `and probe_error is None`:
`80 passed in 43.80s`. The report states the ordering as a design property; no test holds it. Minimal fix: the F2
fix makes the question moot; otherwise add the BrokenPipe + drain-dir test asserting which message survives.
**SOLID (mutant run).**

**F9 — the 3-second drain-join bound is unpinned.** `probe:457` `stderr_thread.join(timeout=3)`. Mutant M21 (`join(timeout=0)`):
`80 passed in 47.23s`, even though `test:342` asserts `stderr_file.stat().st_size == 204800` — the heavy agent
writes its 200 KB before answering, so the drain has already finished by the time `join` runs. A slow sink or a
large post-response stderr would truncate silently. Minimal fix / exact red test: an agent that writes to stderr
AFTER its a2c response and then sleeps; assert the full byte count. **SOLID (mutant run).**

**F10 — DEVIATION 1: the count-gated fake is individually foolable; the file, not the three named guards, is what
kills the attack.** `test:1436` `if _rl_calls[0] <= 3:`, `test:1458` `assert "RL_CALLS=5" in r.stdout.splitlines()`.
Mutant M23-EXTRA-EARLY-READ (an extra child `/proc/<pid>/exe` readlink after `probe:250` `child_pid = proc.pid`): `-k
early_retry_recovers` -> `1 passed, 79 deselected` (FOOLED); whole file -> `4 failed` (killed by
`test_probe_post_loop_sha256_failure_truthful_error`'s `RL_CALLS=2`). Ruling and the 3-line strengthening are in
the DEVIATION 1 section above. **SOLID (mutant run).**

**F11 — the AF-AP-57 screen itself under-reports (tooling, outside the lane's scope).**
`.claude/hooks/edit-snapshot.py:186` — the `call_count` alternative lacks a `\[0\]` option, so
`if _call_count[0] <= 3:` never matches. Measured: on the parent the screen reports 1 hit while my broad grep finds
5 ordinal-gate lines in 4 fakes (`:1428`, `:1681`, `:1793`, `:1912`, `:1915`). Minimal fix:
`(?:calls?|call_count|n_calls|attempts?|count)\s*(?:\[0\])?` in the alternation. **SOLID (reproduced).**

**F12 — a hang in the CONSUMER, reachable from a capture the PIN probe produces with rc 0 (outside the lane's
scope, for A5k).** `proofs/S0-01/check_acp_conformance.py:1502` `stderr_text = stderr_path.read_text()`, in context:
```
    stderr_path = neg_dir / "agent-stderr.txt"
    if stderr_path.exists():
        stderr_text = stderr_path.read_text()
```
No `_require_file`. `Path(fifo).exists()` is True and `read_text()` blocks forever (measured: `rc=124` under a 5 s
watchdog). Reachable: `check_negative` is called at `:1789` and registered in `EXPECTED_CHECK_SEQUENCE` at `:247`.
The positive legs use `_require_file` at `:1737`; the negative leg does not. The checker's own AST class gate
misses it because of the walked-root whitelist entry
`tests/test_s0_01_check_acp_conformance.py:4769` `"post_sum", "c2a_path", "a2c_path", "stderr_path",` — that gate
reasons about path traversal, not file type. Minimal
fix: `_require_file(neg_dir / "agent-stderr.txt", leg, "agent-stderr.txt")` before the read. Exact red test:
`mkfifo` at the negative leg's `agent-stderr.txt`; `check_negative` must raise "is not a regular file" instead of
hanging. **SOLID (mechanism reproduced, reachability traced from the live entry point).**

**F13 — the read class is closed by a GREP, not by a self-scan (item 13's answer).** No `ast` import exists in
`tests/test_s0_01_acp_probe.py`; the checker has
`tests/test_s0_01_check_acp_conformance.py:4718` `def test_ck11_every_read_is_under_the_walk_or_require_file():`.
The probe's enumeration is complete today (I re-derived it) but nothing holds it. Minimal fix: port that AST scan to the probe, covering `open`/`read_text`/`read_bytes`/`json.load` AND
write-mode `open` (an `S_ISREG`/`_open_regular` guard within 5 lines of the receiver). **SOLID.**

**F14 — precision notes on the report (no behaviour impact).** (a) The class table's row for
`test:1436` `if _rl_calls[0] <= 3:` records
"was: same"; the variable was RENAMED `_call_count` -> `_rl_calls`, and that rename is the only reason the screen
now fires — on the parent the same construct was invisible to it (F11). (b) The report says AF-AP-57 "fires on the
PIN at :1681"; that was the screen's only parent hit, not the file's only ordinal gate. (c) The `-B`-flag case of
#40 is proven by my run, not by a committed test. **SOLID.**

**F15 — two mutants survived that are equivalent-or-stricter, not defects.** M15/M16 (`os.stat` -> `os.lstat` in
the fixture guard and in `_sha256_file`): `80 passed` both times. I checked the direction rather than reporting a
hole: `lstat` on a symlink returns `S_IFLNK`, so the guard gets STRICTER (symlink -> FIFO is still `rc=64` in 0 s,
measured on both the mutant and the PIN). The untested delta is that a symlink to a REGULAR file would be
rejected. No fail-open; recorded so the next reviewer does not re-chase it. **SOLID.**

## Item 1 — the closure table (one row per sweep row)

| row | red-before RE-RUN by me on the parent | green on the PIN | verdict |
|---|---|---|---|
| #7 read | FIFO at the fixture -> `rc=124 elapsed=20s`; symlink->`/dev/zero` -> `rc=124 elapsed=16s` | `rc=64 elapsed=0s` named, for FIFO / directory / `/dev/zero`; real fixture `rc=0` | **CLOSED at the fixture, and the shared `_sha256_file` guard is reachable (agent self-FIFO: parent hangs, PIN names it). NOT closed at the probe's own file (F4)** |
| #10 drain | directory at `agent-stderr.txt` -> `rc=0`, `probe_error '<ABSENT>'` | `rc=1` + exact message | **HALF-CLOSED — the raising sub-case is fixed, the blocking sub-case (FIFO) still gives rc 0 / no probe_error (F1); a second error is lost (F2)** |
| #23 lossy | `raw_b64 present: False` | `raw_b64` present, decodes to the exact bytes; clean line carries none | **CLOSED. The consumer analysis attached to it is wrong (F3)** |
| #34 mirror | no test pinned it (`grep -rc` = 0 on the parent) | equality + import-free negative control, both green; production launch shape verified | **CLOSED** |
| #39 timeout | `3_0` -> rc 0, `' 30 '` -> rc 0 | 25 forms measured, all correct; D3's `'9'*400` -> inf rejected by `isfinite` | **CLOSED; message wording misnames a class (F6)** |
| #40 bytecode | `PYTHONDONTWRITEBYTECODE=2` -> recorded False, truth True | 8/8 match against a child-CPython oracle incl. `-B` | **CLOSED; the M3 site untested (F7)** |
| 4.1/9.3 ordinal | R10a on the parent test -> `1 passed, 52 deselected in 0.29s` | sentinel asserted first + argument identity asserted; R10a-equivalent kills | **CLOSED for the converted fake; the retained count gate is individually foolable (F10)** |
| 13.1 | n/a | n/a | **SAFE confirmed, agreed** |

## DISCIPLINE

- **Shared-tree hygiene.** No `git stash/checkout/restore/reset/add/commit/push` was run. The only write to the
  shared repo was `git worktree add -q --detach` at `b4257f8` for the sanctioned PC gate, removed afterwards with
  `git worktree remove --force`; `git worktree list` is back to the 6 other lanes'. `git status --porcelain`
  reported 15 dirty paths when I started and 23 when I finished — all of them other lanes' (P5a's pc tools, the
  S0-02/04/05/06 lanes, the coordinator's ledger and docs). I created and modified nothing in the repo. All grading ran on `git archive`
  copies under `.../scratchpad/vn11/`; every mutant on a fresh minimal copy, applied by a patcher that ABORTS
  unless the anchor occurs exactly once; every pytest run with an explicit `--basetemp` under that directory.
- **Process census.** `ps -eo pid,args -ww | grep "[v]n11" | grep -v "bash -c"` -> empty. No probe, agent,
  wrapper or pytest of mine is alive; no zombies. Live python belongs to lanes vd15 / vg1 and the pre-existing
  `aleph` server — none signalled. I ran no `pkill`/`killall`; every child was reaped by `timeout` or by
  `subprocess.run`.
- **Disk.** Mid-run the container's `/` hit 0 MB free (a shared condition — other lanes were writing too) and one
  command lost its output to ENOSPC. I removed only MY OWN pytest basetemps and re-ran the affected read. No
  measurement in this report comes from a truncated run.
- **Corpus preflight.** `bash scripts/realleg_sync.sh check` -> `intact (142 files)`. All sandbox pytest runs
  carried `S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden`.
- **Interpreter.** `/root/venv-agent-factory/bin/python` (3.11.15) throughout.
- **`report_lint.py` on THIS report**, same rev and maps as item 0:
  `report_lint: 89 refs — OK 89, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (at 9aaefd0ab4804d74f01c1eb43f3ae80ae700d548)`.
  It caught one of my own AF-AP-37 errors before you did: my first draft cited the production launcher at line 34
  of `pc_negative.py`, which is its line number in the DIRTY working tree (another lane has edits there). At the
  PIN the same statement is at line 27. The substantive claim was unaffected; the reference was wrong. Read
  every cross-file line number off the PIN, never off the shared tree.

### Reproduced / reviewed / skipped

**Reproduced (I ran it):** file identity sha256 for both files on both revisions · `report_lint` at the PIN rev ·
`ap_screen` on probe and tests, both revisions · 80 passed x2 sandbox · 53 passed parent baseline · 55 passed
negative_contract · 135 passed on the PC · every #7/#10/#23/#39/#40 red-before and green · the fixture guard
against FIFO / directory / `/dev/zero` · the `_sha256_file` guard's live-entry-point reachability (agent
self-FIFO) · the probe-own-file hang and the zero-evidence traceback · all four write-side FIFO sites plus
`probe:239` `with open(os.path.join(framedir, "runtime-identity.json"), "w") as f:` · the double-failure orderings
(drain+entrypoint, BrokenPipe+drain) · 25 timeout forms · 8 bytecode
cases incl. `-B` and the M3 site · the lone-surrogate escape end to end · `validate_negative_dir` on real lossy and
clean captures · the probe's inability to `import pins` at its production launch shape · 22 mutants + M23 ·
10 consecutive killer runs · the `read_text()`-on-a-FIFO block · the process census.

**Reviewed statically (read, not executed):** the two phase-gate conversions
`test:1838` `if threading.active_count() > 1:` and `test:1974` `if _late1_value[0] is None:`
(their original mutants M11/M12 were re-run, so the conversions are proven by kill, not by reading) · `check_acp_conformance.py`'s leg loop and required-file sets ·
the checker's AST self-scan bodies · `pc_negative.py`'s env construction.

**Deliberately skipped:** `pyflakes` and `scripts/lint_delta.py` re-runs (the lane's outputs are mechanical, the
PIN's bytes are what the two gate runs and the PC gate already exercised, and a 0-new-hit delta claim is not
load-bearing for any finding) · `slopo` / `sentrux` / `ripwire` advisory passes (advisory by owner ruling, never
gates) · any PC bridge call beyond the one sanctioned pytest gate · re-running the lane's `lane_gate.sh` wrapper
(I ran the same two-run identity gate directly with explicit basetemps) · a live PC-venue probe run (no
carve-out for it).

## VERDICT — NOT-READY

The verdict does not depend on anything I did not reproduce. Every blocking item below was run here.

**The CODE is sound and I found no regression.** All six production rows and the ordinal-gate row are genuinely
built; every red-before reproduced on the parent; every green reproduced on the PIN; all 13 of the lane's mutants
reproduced with their stated outcomes (12 killed, 1 surviving by design); 9 of my own added 6 kills and 3 real
survivors; gates are real on both venues (`80 passed` x2 sandbox, `135 passed` on the PC over the exact pushed
bytes with a 0-byte patch, 53 -> 80 with no test renamed or deleted). The `_sha256_file` guard is reachable from
the live entry point in a way the lane did not prove and I did.

**What blocks is the claim set plus one three-line behaviour gap:**

1. **F3 — the report's consumer analysis names the wrong consumer** and routes work to lane A5k on that basis.
   `raw_b64` is already allowed at `proofs/S0-01/negative_contract.py:103`; a probe capture never reaches `check_timeline`.
   Report-only correction.
2. **F4 — the class table asserts "one guard covers all three receivers"; at receiver 1 the PIN still hangs**
   (`rc=124`, zero evidence files). Either fix it (hoist `probe_sha256` to an import-time global inside a `try`)
   or restate the claim honestly and file the residual.
3. **F5 — D1 understates the write side** (3 of 4 outputs hang, and there are 8 write receivers including
   `probe:239` `with open(os.path.join(framedir, "runtime-identity.json"), "w") as f:`, which the proposed
   `_open_regular` fix would miss). Report + next-brief correction.
4. **F1 — SWEEP row #10 is half-closed**: a FIFO at `agent-stderr.txt` still exits 0 with no `probe_error`, the
   exact signature the row named as the defect. 3-line fix + a parametrised red case.

Items 2, 3 and 4 above are the round's own D1 measurements re-framed; the lane found them and filed them under a
heading that reads as "out of scope" rather than "the class named in the brief is still open". That framing is
what makes this NOT-READY rather than a clean MERGE-READY-with-notes: the next brief would inherit a class the
title says is closed.

**Cheapest path to MERGE-READY (one short round, ~30 minutes of lane time):**
- **Report-only, no code (unblocks 1 and 3):** replace the "Consumer contract" block and self-attack A2 with the
  `validate_negative_dir` result (F3); change D1's "the four evidence writes" to the eight enumerated receivers,
  adding `probe:239` `with open(os.path.join(framedir, "runtime-identity.json"), "w") as f:` (F5); restate the
  class-table row for `probe:52` `if not stat.S_ISREG(os.stat(path).st_mode):` as "guarded against a blocking
  read; receiver 1's own failure path is unguarded — measured hang, F4"; add F14's three precision notes.
- **Code, ~6 lines + 2 test cases (unblocks 2 and 4):** an `is_alive()` check right after
  `probe:457` `stderr_thread.join(timeout=3)`, with a `fifo` parametrisation of the drain-failure test (F1), and the
  import-time `probe_sha256` global with the self-FIFO red test (F4).
- **Optional in the same round, 3 lines:** the `FIRST_OK=4` distribution assertion that makes the retained count
  gate kill its own ordinal-shift mutant (F10), which is what would let AF-AP-57=1 stand as REVIEWED-SAFE.
- **Not this lane's:** F11 (the screen regex), F12 (the checker's FIFO hang on the negative leg), F13 (port the
  AST self-scan to the probe), F6/F7/F8/F9 (diagnostic wording and three coverage gaps) — file them, do not hold
  the merge for them.
