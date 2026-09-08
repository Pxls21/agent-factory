# N5h — S0-01 ACP probe, round 11: the sweep's six production rows + the ordinal gate, closed as CLASSES

PIN: `2823f05` (the brief's commit; `proofs/S0-01/tools/acp_probe.py` there is byte-identical to the MERGE-READY blob
`b9eb56dd…` of VERIFY-N5g-b — verified by `sha256sum` before the first edit). Lane venue: sandbox, Opus 4.6
`code-implementer`, interpreter `/root/venv-agent-factory/bin/python` (Python 3.11.15). Report written
2026-09-08T00:52Z (pasted from `date -u`). Box load during the gates: `1.34 2.16 2.32` → `1.81 2.42 2.38` (4 cores,
lanes A5j/B5i/P5a live the whole time — every elapsed figure is an upper bound).

VERDICT: **DONE** — all nine pinned design items built and proven; thirteen mutants RUN (twelve killed, one
surviving BY DESIGN because it IS the red-before); gates green. Two DEVIATIONS and two measured RESIDUALS are
stated first-class below; nothing was changed outside the two scope files.

## FILE IDENTITY (final bytes)

```
c1a9e1734ab1653a75ee6aa4161b5a151ce49036fdf4599757091ce9c6a1cb0e  proofs/S0-01/tools/acp_probe.py   520 lines
f77bda15120c635d8751bb39b726a506870f0f913ad2f0e03849e94f9f9a56b4  tests/test_s0_01_acp_probe.py    2372 lines
```

PIN bytes for comparison: probe `b9eb56dd…` / 463 lines, test `f1f016fa…` / 2032 lines.
`git status --porcelain` names exactly these two files as modified plus the untracked
`tasks/briefs/s0-01-n5h-support/` holding this report — my three declared paths and nothing else. The other dirty
paths belong to lanes A5j/B5i/P5a and were never touched; no `git stash/checkout/restore/reset/add/commit/push`
was run, and nothing was staged.

## PREMISE CHECK (first action — every red-before reproduced on the PIN before any code was written)

| row | reproduction on the PIN bytes | result |
|---|---|---|
| #7 | FIFO at `fixtures/neg-malformed-initialize.json`, probe under `timeout 20` | `RED-BEFORE-7 rc=124 elapsed=20s` |
| #10 | directory at `agent-stderr.txt` | `RED-BEFORE-10 rc=0`, `probe_error: '<ABSENT: no error reported>'` |
| #23 | agent emits `…"message":"Invalid par\xffams"` | `keys: ['dir','frame','seq','t_mono_ns','t_utc']`, `raw_b64 present: False`, frame carries `Invalid par�ams` |
| #34 | `grep -rc '_REDACTED_ENV_KEY_RE' tests/test_s0_01_acp_probe.py` | `0` — no test pinned the mirror |
| #39 | `ACP_PROBE_TIMEOUT=3_0` / `' 30 '` | `rc=0` both — accepted as 30.0 |
| #40 | `PYTHONDONTWRITEBYTECODE` ∈ {1,2,true,0,''} | recorded `True,False,False,False,False` vs CPython `True,True,True,False,False` |
| 4.1/9.3 | the sweep's R10a (gate moved to `== 99`) on the PIN test | `1 passed, 52 deselected in 0.34s` — the vacuity is real |

## DONE — item → file:line → red-before → green

**1. #7 the fixture read cannot hang.** `probe:177` `fixture_st = os.stat(fixture_path)`,
`probe:181` `if not stat.S_ISREG(fixture_st.st_mode):`,
`probe:182` `acp_probe: fixture is not a regular file:`,
`probe:184` `with open(fixture_path) as f:` (the leaked descriptor of the old `open(...).read()` closed with it);
`probe:27` `import stat`.
RED-BEFORE `rc=124 elapsed=20s` → GREEN `acp_probe: fixture is not a regular file: …` `rc=64 elapsed=0s`.
Test `test:2120` `def test_probe_refuses_a_non_regular_fixture` (a PRIVATE copy of the probe + fixtures under
`tmp_path` — the repo tree is never given a FIFO; the 5 s subprocess timeout IS the bound, so a regression hangs
and fails). Positive control in the same test: the same copied tree with the real fixture exits 0.

**2. #10 the stderr drain failure is recorded.** `probe:80` `error_slot[0] = f"{type(exc).__name__}: {exc}"`,
`probe:284` `drain_error = [None]`, `probe:286` `target=_drain_stderr, args=(proc, stderr_path, drain_error)`,
`probe:461` `if drain_error[0] is not None and probe_error is None:`,
`probe:462` `probe_error = f"stderr drain failed: {drain_error[0]}"`.
RED-BEFORE `rc=0` + no `probe_error` → GREEN `rc=1` +
`probe_error: "stderr drain failed: IsADirectoryError: [Errno 21] Is a directory: '…/agent-stderr.txt'"`.
Test `test:2196` `def test_probe_reports_a_stderr_drain_failure` (exact-equality on the message; NEGATIVE CONTROL in
the same test: a writable stderr path → rc 0, no `probe_error`). First error wins, matching the entrypoint-hash
guard already in `_write_evidence`.

**3. #23 a lossy decode keeps the lossless copy.** `probe:373` `text = line_bytes.decode("utf-8")` /
`probe:374` `lossy = False` / `probe:377` `lossy = True` (strict first, `errors="replace"` only on
`UnicodeDecodeError`), `probe:389` `if lossy:`, `probe:392` `entry["raw_b64"] = base64.b64encode(`.
RED-BEFORE `raw_b64 present: False` → GREEN `keys: ['dir','frame','raw_b64','seq','t_mono_ns','t_utc']` and
`raw_b64 decodes to the exact bytes: True`. The row's second site needed no change and was NOT touched:
`probe:399` `"raw_b64": base64.b64encode(line_bytes_with_nl).decode("ascii"),` — the trailing-partial-line branch
already writes `raw` and `raw_b64` unconditionally, so its `errors="replace"` decode never loses the bytes.
Tests:
`test:2231` `def test_probe_keeps_raw_b64_when_a_byte_was_replaced`, and the NEGATIVE CONTROL
`test:2264` `def test_probe_clean_utf8_line_carries_no_raw_b64`. The parsed frame is KEPT beside the copy so the `id == 0`
response detection still fires — routing a lossy line into the `frame: None` branch instead would have made every
mangled byte cost a full `ACP_PROBE_TIMEOUT` wait against an agent that stays alive.

**4. #34 the mirror constant pinned.** Test `test:2278` `def test_probe_redaction_pattern_equals_the_pin` —
imports BOTH (`from pins import REDACTED_ENV_KEY_RE` and `import acp_probe`) and asserts
`acp_probe._REDACTED_ENV_KEY_RE.pattern == REDACTED_ENV_KEY_RE`. The probe is unchanged: it stays import-free of
`pins`, and the second assertion is the negative control on the WRONG fix — it fails if the probe ever grows an
`import pins`. Green against the PIN archive AND against the live (P5a-dirty) `pins.py`, whose value is unchanged.

**5. #39 the timeout domain closed.** `probe:44` `_TIMEOUT_DOMAIN_RE = re.compile(r"[0-9]+(\.[0-9]+)?")`,
`probe:225` `if _TIMEOUT_DOMAIN_RE.fullmatch(timeout_raw) is None:` — the gate runs BEFORE the conversion, so
`float()`'s leniency is structurally unreachable;
`probe:236` `if not math.isfinite(timeout) or timeout <= 0:` still guards the FINAL value.
RED-BEFORE `3_0`→rc 0, `' 30 '`→rc 0 → GREEN, every form rc 64 with a named message:
```
TIMEOUT=[3_0] rc=64 stderr=[acp_probe: ACP_PROBE_TIMEOUT is not a valid number: '3_0']
TIMEOUT=[ 30 ] rc=64 stderr=[acp_probe: ACP_PROBE_TIMEOUT is not a valid number: ' 30 ']
TIMEOUT=[30s] rc=64 · [0x10] rc=64 · [nan] rc=64 · [inf] rc=64 · [-5] rc=64 · [0] rc=64 · [30] rc=0 · [0.5] rc=0
```
**Found this round, NOT in the sweep:** a 400-digit string passes the regex and `float()`s to `inf`
(`float('9'*400) == inf`) — the domain gate ALONE would have re-opened the NaN/inf wormhole the PIN had closed.
It is rejected: `TIMEOUT=[99999999999999…] rc=64 … must be a finite float > 0`. Adversarial edges also measured:
`'30\n'` rejected (`fullmatch`, not `match`+`$`), Arabic-Indic `'٣٠'` rejected (`[0-9]` is ASCII-only, `float()`
accepts it), `'1.5.0'` rejected, `'0.0'` rejected as non-positive, `'007'` accepted as 7.0.
Tests `test:2316` `def test_probe_timeout_rejects_forms_outside_the_domain` (11 parametrised forms, exact stderr)
and the positive control `test:2329` `def test_probe_timeout_accepts_the_domain`.
**The two existing message classes are preserved byte-for-byte** — a rejected value that `float()` parses to a
non-finite/non-positive number keeps the wording at
`probe:230` `if rejected is not None and (not math.isfinite(rejected) or rejected <= 0):`, everything else gets
`probe:233` `msg = f"ACP_PROBE_TIMEOUT is not a valid number: {timeout_raw!r}"`. All seven pre-existing timeout tests still pass unchanged.

**6. #40 the runtime state, not a string mirror.**
`probe:131` `"python_dont_write_bytecode": sys.dont_write_bytecode,` and the same at
`probe:491` `"python_dont_write_bytecode": sys.dont_write_bytecode,` in the M3 handler.
RED-BEFORE `PYTHONDONTWRITEBYTECODE=[2] recorded=False truth=True` → GREEN `recorded=True truth=True match=YES`
for all of `1,2,true,0,''` and the unset case. Test
`test:2340` `def test_identity_records_the_runtime_bytecode_state_not_the_string` — the ORACLE is CPython itself: a child
interpreter started with the SAME environment reports its own `sys.dont_write_bytecode`; no expectation is
hardcoded.

**7. 4.1/9.3 the ordinal gate gets a positive control (AF-AP-57).**
`test:1707` `if path == _interp_path and not _fired[0]:` (argument + fired-flag, no ordinal), the fake writes a SENTINEL
naming the path it failed on, and `test:1726` `assert sentinel.exists(), (` runs BEFORE the
`assert "probe_error" not in rid`.
RED-BEFORE: R10a on the PIN test → `1 passed, 52 deselected in 0.34s` (green while nothing ever failed).
GREEN: the equivalent mutation on the new test (the fake gated on a path that never matches) →
`AssertionError: the early sha256 failure never fired — the test would assert the absence of a probe_error that
was never set (AF-AP-57 vacuity)`.

**8. SWEEP-tests 13.1 — SAFE, confirmed.** `test:785` `probe_exe = os.readlink(f"/proc/{os.getpid()}/exe")` reads
the TEST's own live pid inside its own process — no spawn/exit window exists, and the value is used only as the
negative control that the probe did not sample `/proc/self/exe`. No change.

**9. Report discipline.** `report_lint` / `ap_screen` / `lint_delta` / `pyflakes` results are in GATES below.

## CLASS CLOSURES (the brief's "or a one-line reason", enumerated on the FINAL bytes)

**#7 class — every path the probe READS** (`grep -n 'open(\|read_text\|json.load\|readlink\|os.stat'`):
| site | status |
|---|---|
| `probe:52` `if not stat.S_ISREG(os.stat(path).st_mode):` in `_sha256_file` | GUARDED — one guard covers all three receivers of the shared reader: the probe's own file, the agent entrypoint, the child interpreter. `os.stat` cannot block; `open()` on a FIFO blocks forever and `/dev/zero` never reaches EOF |
| `probe:184` `with open(fixture_path) as f:` — the fixture | GUARDED (item 1) |
| `probe:268` / `probe:341` / `probe:432` `os.readlink("/proc/%d/exe" % proc.pid)` | reason: `readlink` returns a link target from the kernel and never opens the target — it cannot block, and its failures are already recorded as `probe_error` |
| `probe:380` `response_frame = json.loads(stripped)` | reason: parses an in-memory `str` already read from the pipe — no file |

**#10 class — every broad `except` in the probe** (`grep -n 'except'`, 3 broad of 23 total):
| site | status |
|---|---|
| `probe:79` `except Exception as exc:` in `_drain_stderr` | FIXED (item 2) — records into `error_slot` |
| `probe:446` `except Exception:` on `proc.stdin.close()` | EQUIVALENT, one-line proof: a close failure means only that the agent's read end is already gone, and the probe records the agent's fate independently two lines later (`proc.wait` → `agent_exit_code`). Matches the sweep's own #44 ruling |
| `probe:477` `except Exception as exc:` (the M3 handler) | fail-LOUD by construction — sets `probe_error`, writes all four files, exits 1 |
| the other 20 | narrow (`OSError`, `IOError`, `ValueError`, `OverflowError`, `UnicodeDecodeError`, `BrokenPipeError`, `json.JSONDecodeError`, `subprocess.TimeoutExpired`, `SystemExit`) and each records or is a documented control-flow branch |

**4.1/9.3 class — every fake selecting behaviour by call count in the test file** (`grep -n 'calls\[0\]\|call\[0\]\|call_count\|n_calls\|attempts\?\[0\]'`). The sweep named one; the file had four:
| site (final bytes) | was | now |
|---|---|---|
| `test:1707` `if path == _interp_path and not _fired[0]:` (LATE-NOCLEAR killer) | `_sha_call[0] == 1` | argument + fired-flag + asserted sentinel, `test:1726` `assert sentinel.exists(), (` |
| `test:1838` `if threading.active_count() > 1:` (LATE-NULL killer) | `_call_count[0] >= 2` | PHASE gate — the early loop runs with the main thread alone, every later sample with the drain thread alive (the same gate the DL-INLINE killer uses) + `RL_CALLS=2` asserted |
| `test:1974` `if _late1_value[0] is None:` (LATE-EVERY killer) | `_call_count[0] == 1 / == 2 / else` | PHASE + a fired-flag; an extra early retry used to shift every ordinal and hand the sentinel to the FIRST late sample. `RL_CALLS=2` asserted |
| `test:1436` `if _rl_calls[0] <= 3:` (AP-F1a retry killer) | same | count KEPT — "transient" IS defined by a count, and K must exceed the sample count a single-shot shape makes (proved: with K=1 the AP-F1a mutant survives). Mitigated the way the registry row prescribes: argument gating (a `/proc/self/exe` read returns a sentinel instead of consuming a failure) + the mechanism printed and asserted, `test:1458` `assert "RL_CALLS=5" in r.stdout.splitlines(), (` |

Each converted killer was re-run against ITS original mutant — mutant rows 8 (LATE-NOCLEAR), 10 (AP-F1a),
11 (LATE-NULL) and 12 (LATE-EVERY) — so the conversions cost no kill. Mutant row 9 proves the neighbouring
phase-gated DL-INLINE killer, untouched this round, still dies.

## MUTANTS (13 rows, all `ran` on scratch copies; `git status --porcelain` clean on the scope files after each — final sha256 identical to the pre-audit pristine copies)

| # | mutant | ran | outcome | killer line (pasted) |
|---|---|---|---|---|
| 1 | FIXTURE-FIFO-UNGUARDED (revert item 1) | yes | KILLED | `E subprocess.TimeoutExpired: Command '[…acp_probe.py]' timed out after 5 seconds` → `1 failed, 79 deselected in 5.32s` |
| 2 | DRAIN-SWALLOW (revert item 2) | yes | KILLED | `E AssertionError: expected exit 1, got 0:` → `1 failed, 79 deselected in 0.14s` |
| 3 | LOSSY-NO-RAW (revert item 3) | yes | KILLED | `E AssertionError: the lossless copy of a replaced-byte line is missing: ['dir', 'frame', 'seq', 't_mono_ns', 't_utc']` → `1 failed, 1 passed, 78 deselected in 0.22s` |
| 4 | MIRROR-DRIFT (`NSEC`→`NSECX` in the probe's copy) | yes | KILLED | `E AssertionError: probe copy '(?i)(KEY|TOKEN|SECRET|PASSWORD|NSECX|PRIV)' has drifted from pins.REDACTED_ENV_KEY_RE '(?i)(KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV)'` → `1 failed, 79 deselected in 0.06s` |
| 5 | TIMEOUT-LENIENT (domain gate → `if False:`) | yes | KILLED | `E AssertionError: expected exit 64 for '3_0', got 0` → `6 failed, 9 passed, 65 deselected in 1.42s` (the 6 = `3_0`, `' 30 '`, `+30`, `1e3`, `30s`, `0x10`) |
| 6 | BYTECODE-STRING (revert item 6) | yes | KILLED | `E AssertionError: PYTHONDONTWRITEBYTECODE='2': recorded False, CPython reports True` → `2 failed, 4 passed, 74 deselected in 1.22s` |
| 7 | ORDINAL-99 on the PIN test (the sweep's R10a) | yes | SURVIVED **by design — this is the red-before** | `1 passed, 52 deselected in 0.34s` |
| 8 | ORDINAL-99 equivalent on the N5h test (fake never fires) | yes | KILLED | `E AssertionError: the early sha256 failure never fired — the test would assert the absence of a probe_error that was never set (AF-AP-57 vacuity)` |
| 9 | DL-INLINE (`_EARLY_SAMPLE_DEADLINE_S` inlined as `0.2`) — the MERGE-READY verdict's mutant must still die | yes | KILLED | `E AssertionError: RL_CALLS=97 DEADLINE_SEEN=0.0` → `1 failed, 1 passed, 78 deselected in 6.60s` |
| 10 | AP-F1a-SINGLE-SHOT (early retry loop → one attempt) | yes | KILLED | `E AssertionError: expected exit 0 (retry recovered), got 1: acp_probe: interpreter sample failed: transient failure` |
| 11 | LATE-NULL (late readlink failure nulls the early reading) | yes | KILLED | `E AssertionError: assert None == '/usr/bin/python3.11'` |
| 12 | LATE-EVERY (in-loop `if not _late_sampled:` → `if True:`) | yes | KILLED | `E AssertionError: expected exactly 2 child /proc/<pid>/exe reads (early loop + ONE late sample); a third read is the LATE-EVERY shape: 'CALL2=/usr/bin/python3.11\nRL_CALLS=3\n'` |
| 13 | SHA-GUARD-OFF (remove the `S_ISREG` guard inside `_sha256_file`) | yes | KILLED | `E subprocess.TimeoutExpired: Command '[…sha_driver.py]' timed out after 5 seconds` → `1 failed, 79 deselected in 5.13s` |

## GATES (each one foreground call; output pasted verbatim)

**Static-copy gate — `git archive 2823f05` + exactly my two files, two runs** (`scripts/lane_gate.sh`, every pytest
run with `--basetemp` under the session scratchpad):
```
lane_gate: archive of 2823f05dffa1 at …/scratchpad/n5h/gate; 2026-09-08T00:43:04Z
== identity (working-tree bytes copied over the archive) ==
c1a9e1734ab1653a75ee6aa4161b5a151ce49036fdf4599757091ce9c6a1cb0e  proofs/S0-01/tools/acp_probe.py  520 lines
f77bda15120c635d8751bb39b726a506870f0f913ad2f0e03849e94f9f9a56b4  tests/test_s0_01_acp_probe.py  2372 lines
80 passed in 43.12s   (pytest-exit: 0)
80 passed in 44.40s   (pytest-exit: 0)
RESULT: rev=2823f05dffa1 files=2 runs=2 identical=yes rc=0 summary="80 passed in 43.12s 80 passed in 44.40s"
```
**PIN baseline, same command on the archive bytes alone:** `pytest-summary: 53 passed in 40.76s` → **53 → 80
(+27 tests), zero regressions.**

**Determinism beyond the two gate runs:** the four converted killers run 10× consecutively —
`4 passed, 76 deselected` in every run (0.67–0.71s), so the newly asserted `RL_CALLS` mechanisms are stable on a
contended box.

**pyflakes** (both scope files): `pyflakes rc=0` — no output.

**`python3 scripts/lint_delta.py --base 2823f05`**:
```
lint_delta (worktree vs 2823f05): 12 .py changed, 0 NEW pyflakes hit(s), 0 removed
```
Advisory tells on MY added lines, each classified by reading them: `AP-1 tests/test_s0_01_acp_probe.py` — the
bytecode test builds the child env explicitly (resolve once, thread explicitly: that IS the pattern);
`AP-32 tests/test_s0_01_acp_probe.py` — `hashlib.sha256(b'n5h').hexdigest()` is the positive-control ORACLE for the
digest; `AP-24 tests/test_s0_01_acp_probe.py` — a pre-existing `except SystemExit as e: pass` re-emitted by the
phase-gate rewrite of the f6 wrapper, whose test asserts on `runtime-identity.json` + stdout rather than rc (the
sibling wrappers that DO assert rc use `sys.exit(e.code)`). The remaining rows belong to lanes P5a/B5i/A5j.

**`scripts/ap_screen.py proofs/S0-01/tools/acp_probe.py`** — 11 hits at the PIN → **8 now**:
```
AF-AP-55: 3   :268 :341 :432   os.readlink("/proc/%d/exe" % proc.pid)
AP-1: 2       :158 :222        os.environ.get(...)
AP-32: 2      :54 :91          hashlib.sha256(...)
AP-24: 1      :446             except Exception:
```
Classified by running them: **AF-AP-55 ×3** — pre-existing and reviewed by N5f/N5g; the reading is pinned to the
first a2c byte (the final exec stage) and the suite carries multi-stage fixtures
(`test_probe_interpreter_is_the_final_exec_not_a_wrapper`, `test_probe_env_shebang_interpreter_is_constant`); not
touched this round. **AP-1 ×2** — `probe:158` `v = os.environ.get(k)` is the required-variable validation
(exit 64 named when unset or empty) and `probe:222` `timeout_raw = os.environ.get("ACP_PROBE_TIMEOUT", "30")`
is the timeout, whose domain item 5 just closed; both are read once at the top of
`main` and threaded explicitly. **AP-32 ×2** — the two sha256 uses are the identity digest and the redaction
fingerprint, both consumed only by the probe's own evidence files.
**AP-24 ×1** — `probe:446` `except Exception:`, the `proc.stdin.close()` swallow ruled EQUIVALENT above. AP-1 fell 4→2 and AP-24 2→1 as a direct result of items 6
and 2.

**`scripts/ap_screen.py --tests tests/test_s0_01_acp_probe.py`**:
```
AF-AP-57: 1
    tests/test_s0_01_acp_probe.py:1436: if _rl_calls[0] <= 3:
```
**DEVIATION 1 — the brief required AF-AP-57 ZERO after item 7; it is 1.** The `:1681` specimen the brief named is
gone; the surviving hit is the transient-retry fake, where the count is the SEMANTICS (see the class table). I did
not rewrite it into a form that merely dodges the regex — that would be a hollow green in the screen. It is
classified REVIEWED-SAFE with three named guards (argument gating, the asserted `RL_CALLS=5` mechanism, and the
AP-F1a mutant RUN and killed in row 10). A coordinator who wants a literal zero should rule on the fake's shape;
I would not change it without that ruling.

**`scripts/report_lint.py … --map probe=… --map test=…`** — summary line as the tool printed it before this
paragraph existed:
```
report_lint: 54 refs — OK 53, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
```
**MISS 0, NEAR 0.** The single heuristic row is named here in one line: the one UNCHECKABLE is the verbatim
`ap_screen` output line quoted inside the fenced block above — tool output I will not edit to please a linter, and
it carries no backticked claim token, only a lowercase symbol. (Quoting this summary inside the report does NOT
add a self-referential reference, measured: the tool prints a space after the colon and the reference pattern
needs a digit there.)

**Consumer contract (cross-tool, run against the REAL checker):** `check_acp_conformance.check_timeline()` enforces
an EXACT key set on every timeline entry, so the new `raw_b64` on a lossy entry is rejected:
```
clean 5-key a2c entry: ACCEPTED by check_timeline (fails later only on my synthetic dir's missing sibling file)
lossy 6-key a2c entry (raw_b64): Failure -> neg: timeline entry at seq 2 has unexpected keys ['dir', 'frame', 'raw_b64', 'seq', 't_mono_ns', 't_utc']
```
This is the fail-CLOSED direction and no golden is affected (clean lines carry no `raw_b64` — proved by the
negative-control test), but it IS a cross-tool behaviour change: a leg whose agent emitted an undecodable byte now
FAILS the conformance run instead of passing silently with mangled text. Flagged for the coordinator / lane A5j —
the message names the key, not the cause, and a friendlier `Failure` would live in the checker, outside my scope.

**DEVIATION 2 — item 5 is implemented as "the regex gates the ACCEPT path", not "the regex is the only call
before `float()`".** The pinned wording is `re.fullmatch(...)` before `float()`. Taken literally, the three
existing tests that assert `must be a finite float > 0` for `nan`, `inf` and `-1` would have had to be rewritten,
because the regex rejects those before the numeric check can classify them. I kept the domain gate FIRST for the
accepted value — `float()` never runs on a value outside the domain on the path that produces a timeout — and,
inside the reject branch only, call `float()` once to choose which of the two EXISTING messages names the reason —
`probe:230` `if rejected is not None and (not math.isfinite(rejected) or rejected <= 0):`. Net effect on behaviour: identical rejection set, identical exit code, and every pre-existing
message assertion still passes untouched. Rejected alternative: regex-only, rewriting three pinned assertions of a
MERGE-READY verdict — more churn, no added safety.

**Process census after every run** (`ps -eww … | grep -E 'n5h|acp_probe|agent_result|agent_lossy'`): no match —
nothing I started is alive; no zombie older than 60 s with ppid 1. The only live pytest/python processes belong to
lane P5a (`…/scratchpad/p5a/…`) and the pre-existing `aleph` server; none were signalled. Every kill in this lane
was `subprocess.run(timeout=…)` reaping its own child — no `pkill`/`killall` was used.

**NOT run here:** the PC `-n 8` gate (the coordinator's, per the brief) and any PC-bridge call.

## NOT_DONE

1. **The write-side siblings of #7 are NOT fixed** (measured, see DISCREPANCIES). The brief scoped the class to
   paths the probe READS; the four output files are paths it WRITES, and closing them safely needs a ruling on the
   M3 handler's own failure path (its rescue write would raise inside the `except`, turning a hang into a
   traceback). Named, measured, left alone.
2. **AF-AP-57 is 1, not 0** (DEVIATION 1 above).
3. No PC-venue execution, no commit, no push, no outward action — per the standing rules.
4. `docs/INCIDENT-LOG.md` was NOT touched: the bug-echo / registry duty for these classes belongs to the
   coordinator's checkpoint (the file is outside my two-file scope). Candidate rows are named in DISCREPANCIES.

## DISCREPANCIES

**D1 — RESIDUAL: a FIFO planted at an output path still hangs or is silently swallowed.** Same defect class as
row 7, on the write side. Measured on the FINAL bytes:
```
FIFO at agent-stderr.txt      → rc=0  elapsed=3s   probe_error: '<ABSENT>'   (the drain thread blocks in open();
                                                    join(timeout=3) bounds it, the daemon thread dies at exit)
FIFO at runtime-identity.json → rc=124 elapsed=15s (my `timeout 15` killed it — the probe hangs)
```
The second is a genuine hang of the same shape the brief set out to remove. Recommendation: a single
`_open_regular(path, mode)` helper for the four evidence writes, decided together with the M3 handler's own
rescue-write failure path. Registry candidate: extend the row that covers "a non-regular file where a tool expects
a regular one" from reads to writes.

**D2 — the brief's pack does not show the AP-24 hits it cites.** The brief points at "the pack's AP-24 hits at
`:63` and `:395`"; `tasks/briefs/s0-01-sweep-support/pack-probe-pctools.md` lists 9 hits with no AP-24 section. The
hits are REAL — `scripts/ap_screen.py` on the PIN bytes returns 11 hits including `AP-24: 2` at `:63` and `:395` —
so the brief is right and the pack is stale (generated before that row was in the screen, or truncated). Read the
screen, not the pack, for AP counts.

**D3 — `float()` overflow was not in the sweep's row 39.** The pinned regex alone re-opens the inf wormhole for a
long digit string; the `isfinite` guard on the FINAL value is what closes it. Stated so the verifier grades the
implementation against the defect, not only against the row's eight named forms.

**D4 — HEAD moved during the lane.** PIN `2823f05` → HEAD `f7b45f2` → `4d2f313` (coordinator ledger/wiki/scripts
commits). `git diff --stat 2823f05 f7b45f2 -- <my two files>` is empty: neither scope file moved, so the gate at
the PIN is still the right gate. The mirror test (item 4) was additionally run against the LIVE `pins.py` (dirty
under lane P5a) and is green — `REDACTED_ENV_KEY_RE` is unchanged there.

**D5 — a shell-quoting trap that briefly produced a wrong measurement.** My first item-5 sweep printed `rc=0` for
every rejected value because `$?` was expanded AFTER a `$( … )` inside the same `echo` argument, which resets it.
Re-run with `rc=$?` captured on its own line before any substitution. Same class as the `${PIPESTATUS[0]}` rule;
no result in this report comes from the discarded run.

## SELF-ATTACK — the three most likely ways this change is wrong

**A1 — "the `S_ISREG` guard inside `_sha256_file` changes a pinned `probe_error` message."** The guard adds an
`os.stat` in front of the shared reader, and four existing tests assert EXACT `probe_error` strings built from
`FileNotFoundError`. Ruled out two ways: `os.stat` on a missing path raises the identical
`[Errno 2] No such file or directory: '<path>'` that `open` raised (same `filename` field), and
`test_probe_interpreter_deleted_after_start_is_a_loud_probe_error` — which pins
`interpreter sample failed: [Errno 2] No such file or directory: '<myshell> (deleted)'` — passes in all four full
runs. The guard is also proven live by mutant 13 (removing it hangs the driver).

**A2 — "the extra `raw_b64` key silently breaks the checker."** Not silently: I ran the REAL
`check_acp_conformance.check_timeline()` over both shapes (output pasted in GATES). A clean entry is accepted, a
lossy entry is rejected by name. No golden is affected because a clean line never carries the key
(`test_probe_clean_utf8_line_carries_no_raw_b64`, and mutant 3 proves the key is not decoration). The residual
risk is a HUMAN one — a reader seeing "unexpected keys" may not realise the cause was an undecodable byte — which
is why it is flagged for the checker's owner rather than papered over here.

**A3 — "the new `RL_CALLS` assertions are flaky, so a green is luck."** They pin exact call counts on a contended
4-core box. Attacked by running the four converted killers 10× consecutively (`4 passed` every time) plus the two
gate runs and two earlier full-file runs — 14 consecutive greens. The failure mode is also benign by construction:
`RL_CALLS=5` can only differ if the early retry loop broke early, which already fails the test's FIRST assertion
(`rc == 0`), and `RL_CALLS=2` can only differ if an extra `/proc/<pid>/exe` read appeared — which is exactly the
shape change the assertion exists to catch. A flake here is loud, never a silent pass.

**Runner-up attacks, for completeness.** (a) *The timeout gate rejects something legitimate*: probed `007` (7.0,
accepted), `0.5`, `5.25`, `30` — accepted; and the four accept-cases are a parametrised positive control, so a
gate that rejected everything would be red. (b) *The drain fold invents an error on normal runs*: 4 full-file runs
× 80 tests, plus the explicit negative control inside `test_probe_reports_a_stderr_drain_failure`, all show no
`probe_error`. (c) *The mutant audit contaminated the shared tree*: after every mutant the scope files' sha256 was
compared to pre-audit pristine copies and matched (`c1a9e173…` / `f77bda15…`); every mutation was applied to a
`git archive` copy under the session scratchpad by a helper that ABORTS unless the anchor appears exactly once.
