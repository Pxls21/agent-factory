# VERIFY-N5f (round 9) — adversarial grade of lane N5f (the later interpreter reading wins)

## 0. Premise + disk + hygiene

```
git rev-parse HEAD  -> 98792f5bb231a862afecde1972c78bc9c2536956          == PIN
git log --oneline -3
98792f5 transcripts: scrubbed sandbox chat digests (2026-09-06)
d08c7bf S0-01 WIP checkpoint 8j: the probe records the interpreter that RUNS the agent … (lane N5f) — REVIEW-PENDING
736bb94 S0-01 WIP checkpoint 8i: the tee drains client frames until client EOF … (lane B5d)
df -h /  (before first batch)  /dev/vda 252G 23G 15G 61% /     (62% at the end; never below 15 G; no ENOSPC)
```
PREMISE HOLDS. Shared tree was CLEAN at dispatch (`git status --porcelain` empty) and I never wrote to it — read-only git only.
All work on `scratchpad/vn10/repo` (`git archive HEAD | tar -x`, `git init` + `base` commit). Every mutant restored from
`scratchpad/vn10/pristine/`, never git-restore/stash. Final check: all 8 in-scope files byte-identical to the `98792f5` blobs
(`PRISTINE ×8`), shared tree still `git status` clean. `--basetemp` per run, deleted after. No xdist.

**Tree drift note:** the shared tree advanced during my run to `9987187` (b1eb0fa, 5e93585, 9987187). **All six scope files are
sha-identical between 98792f5 and 9987187** — this grade applies unchanged to the current tree.

Lane report graded: `tasks/briefs/s0-01-n5f-support/N5f-report.md`. Probe sha reproduced:
`b60ba85e2f1df0e147cb9f3b2167bdf26ff33a9d4413d560be843d49589da187` (matches report, commit body and ledger).

## 1. Gate lines (mine, pasted verbatim)

```
pytest-summary: 252 passed in 49.73s      (five-file suite, run 1)
pytest-summary: 252 passed in 49.51s      (five-file suite, run 2)
pytest-summary: 31 passed in 6.39s        (tests/test_spec_probe_schemas.py tests/test_proof_runner.py)
pyflakes rc=0   (acp_probe.py, test_s0_01_acp_probe.py, test_s0_01_spec_runner.py, test_spec_probe_schemas.py,
                 negative_contract.py, test_s0_01_negative_contract.py)
```
Denominator verified, not assumed: parent `736bb94` collects **246**, HEAD collects **252**; the diff is exactly 6 new tests
+ 1 rename (`…_is_fail_loud` → `…_keeps_interpreter_identity`). The lane's "246 + 6" arithmetic is correct.

**Red-green reproduced** (parent probe `736bb94` dropped into the HEAD test file, `28819d90…` blob):
```
6 failed, 2 passed, 54 deselected in 1.80s
FAILED test_probe_self_deleting_script_is_probe_error_not_traceback
FAILED test_probe_interpreter_is_the_final_exec_not_a_wrapper
FAILED test_probe_env_shebang_interpreter_is_constant
FAILED test_probe_early_sample_loop_bound_is_pinned
FAILED test_probe_late_sample_clears_early_interpreter_error
FAILED test_probe_m3_handler_writes_complete_evidence
   (E: "env.json absent after M3 crash")
```
The 2 that pass on the parent are `test_probe_agent_exits_without_output_keeps_interpreter_identity` (a rename + assertion
tightening — **never red**, correctly not claimed as such) and `test_runner_records_the_raw_line_not_the_stripped_line`
(runner-side; its red state is mutant SR-09, reproduced below).

## 2. Agent-shape table + block attribution (real probe, instrumented copy, HEAD)

Instrument: markers at all three sample sites on my copy (`EARLY` = `acp_probe.py:235`, `LATE`/`LATE_EXC` = `:297`/`:308`,
`POST_RL`/`POST_SHA` = `:366`/`:372`).

| shape | rc | interp realpath | sha8 | agent_exit | probe_error | site(s) fired |
|---|---|---|---|---|---|---|
| A `sys.exit(0)`, no stdout | 1 | /usr/bin/python3.11 | f56a5885 | 0 | BrokenPipeError: agent process exited before c2a write landed | EARLY |
| B `sys.exit(1)`, no stdout | 1 | /usr/bin/python3.11 | f56a5885 | 1 | same | EARLY |
| C `os.close(1)` + sleep | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY |
| D 1 byte then `os._exit(0)` | 1 | /usr/bin/python3.11 | f56a5885 | 0 | BrokenPipe… | EARLY |
| E full answer + `stdin.read()` | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY,LATE |
| F answer, exit at once | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY,LATE |
| G first byte after 2 s | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY,LATE |
| H 1 byte, sleep .05, `_exit` | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY,LATE |
| I answer, no trailing NL | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY,LATE |
| J never answers, hangs | 0 | /usr/bin/python3.11 | f56a5885 | −9 | null | EARLY |
| K closes stdout, sleeps | 0 | /usr/bin/python3.11 | f56a5885 | −9 | null | EARLY |
| L partial line then hang | 0 | /usr/bin/python3.11 | f56a5885 | −9 | null | EARLY,LATE |
| M self-SIGTERM, no stdout | 0 | /usr/bin/python3.11 | f56a5885 | −15 | null | EARLY |
| **N unlinks its own interpreter** | **1** | `…/myshell (deleted)` | **null** | 0 | **interpreter sample failed: [Errno 2] …** | EARLY,LATE |
| **W** `#!/bin/sh` + sleep + exec py | **0** | **/usr/bin/python3.11** | f56a5885 | 0 | null | EARLY,LATE |
| **EV** `#!/usr/bin/env python3` | **0** | **/usr/bin/python3.11** | f56a5885 | 0 | null | EARLY,LATE |
| DASH `#!/bin/dash` single exec | 0 | /usr/bin/dash | 86d31f6f | 0 | null | EARLY,LATE |
| BP1 (A + readlink always fails) | 1 | null | null | 0 | BrokenPipe… | — |
| BP2 (D + readlink always fails) | 1 | null | null | 0 | BrokenPipe… | — |

**Repeat measurements (12× / 20×, unloaded AND under 4 CPU hogs):**

| agent | HEAD unloaded | HEAD 4-hogs | PARENT `736bb94` unloaded | PARENT 4-hogs |
|---|---|---|---|---|
| W (sh wrapper) | **1 pair, /usr/bin/python3.11 12/12, rc 0 ×12** | **1 pair, python 12/12** | 1 pair, **/usr/bin/dash 12/12** | **/usr/bin/dash 12/12** |
| EV (env shebang) | **1 pair, python 12/12** | **1 pair, python 12/12** | **2 pairs — /usr/bin/env 10/12 + python 2/12** | **2 pairs — env 10/12 + python 2/12** |
| A ×20 | 1 triple; rc {1:19, 0:1}; **0 arms with a wrong exact reason** | 1 triple; rc {1:20}; 0 wrong | — | — |
| D ×20 | 1 triple; rc {1:20}; **0 wrong** | 1 triple; rc {1:20}; 0 wrong | — | — |

R9-N5e-F1 is genuinely fixed and the paired control reproduces the defect on the parent. Every rc-1 arm of shapes A/D carried
**both** `rid["probe_error"] == "BrokenPipeError: agent process exited before c2a write landed"` **and**
`stderr == "acp_probe: BrokenPipeError: agent process exited before c2a write landed"`; every rc-0 arm had no `probe_error` key.

**Docstring-mechanism measurement** (readlinks on `/proc/*/exe` per run, 6 runs each): shape A → **1**, shape M → **1**,
shape E → **2** (early + late). The renamed test's mechanism claim ("the loop breaks on iteration 1") is confirmed; the
101-iteration figure holds only under an always-failing readlink.

**Post-loop attribution:** `POST_RL` / `POST_SHA` fired in **0 of 19** real shapes (see F11).

## 3. Mutant table — every run is the FULL five-file suite (252 tests) unless noted

| id | mutation | result | killer(s) I observed |
|---|---|---|---|
| NOOP | — | `252 passed in 49.73s` / `49.51s` | — |
| EARLY-DEL | delete the post-Popen loop | KILLED `7 failed` | early_retry_recovers, early_sample_loop_bound, fast_exit_deterministic, agent_exits_without_output_keeps, broken_pipe_deterministic, sigterm_killed, late_sample_clears |
| LATE-DEL | delete the a2c-triggered sample | KILLED `5 failed` | final_exec_not_a_wrapper, env_shebang_constant, interpreter_sample_failure(+after_child_exit), late_sample_clears |
| LATE-GATE | re-gate on `interp_realpath is None` | KILLED `3 failed` | final_exec_not_a_wrapper, env_shebang_constant, late_sample_clears |
| LATE-NOCLEAR | drop the error-clearing arm | KILLED `1 failed` | late_sample_clears_early_interpreter_error |
| **LATE-NULL** | **late readlink failure nulls the early reading** | **SURVIVED `252 passed`** (0/5 unloaded; killed only 2/6 under 8 hogs) | **NONE — finding F1** |
| APF1A | one readlink at Popen, no retry | KILLED `2 failed` | early_retry_recovers, early_sample_loop_bound |
| POST-DEL | delete the post-loop block | KILLED `1 failed` | post_loop_sha256_failure_truthful_error |
| F3PREFIX | drop the `interpreter sample failed: ` prefix (×4 sites) | KILLED `4 failed` | post_loop_sha256_failure_truthful_error +3 |
| DL_DOUBLE | deadline 0.2 → 0.4 | KILLED `1 failed` | early_sample_loop_bound_is_pinned |
| **DL_SCALE** | **deadline 0.2 → 0.4 AND step 0.002 → 0.004** | **SURVIVED `252 passed`** | **NONE — finding F2** |
| EV_OUTSIDE | `_write_evidence` moved out of the `try` | KILLED `1 failed` | m3_handler_writes_complete_evidence (**not** the lane's named test) |
| EV_SWALLOW | handler returns without writing/exiting | KILLED `3 failed` | m3_handler…, bad_agent_path…, error_surfaces_on_exception |
| M3-NOENV | handler skips `env.json` | KILLED `1 failed` | m3_handler_writes_complete_evidence |
| M3-1KEY | handler writes `{"probe_error": …}` only | KILLED `1 failed` | m3_handler_writes_complete_evidence |
| M3-NOTIMELINE | handler skips `timeline.jsonl` | KILLED `2 failed` | m3_handler…, bad_agent_path… |
| **LATE-CLEARALL** | late success clears **any** `probe_error` | **SURVIVED `252 passed`** | equivalent-by-reachability — finding F5 |
| LATE-DISCARD-DIFF | late reading discarded when ≠ early | KILLED `2 failed` | final_exec_not_a_wrapper, env_shebang_constant |
| **LATE-EVERY** | re-sample on **every** chunk (drop the once-gate) | **SURVIVED `252 passed`** | **NONE — finding F6** |
| FC-BIND | `from time import monotonic/sleep/monotonic_ns` (bypass the module-attr patch) | KILLED `1 failed` | early_sample_loop_bound_is_pinned |
| LG2 | seed the early reading from `/proc/self/exe` before the loop | KILLED `1 failed` | early_sample_loop_bound (incidental — via the readlink counter) |
| **LG2-EARLY** | **early loop reads `/proc/self/exe`** | **SURVIVED `252 passed`** (probe file alone `49 passed`) | **NONE — finding F7** |
| LG2-LATE | late sample reads `/proc/self/exe` | KILLED `1 failed` | interpreter_is_child_not_self |
| LG2-POST | post-loop reads `/proc/self/exe` | KILLED `1 failed` | interpreter_is_child_not_self |
| **PINS-12KEY** | add a 12th key to `pins.NEGATIVE_IDENTITY_KEYS` | **SURVIVED** (probe suite `49 passed`) | **NONE — finding F9** |
| SR-05 | `in` → `==` | KILLED `3 failed` | records_the_first_matching_line, observed_line_not_expected, **raw_line_not_stripped** |
| SR-06 | match `line.strip()` | SURVIVED `252 passed` | equivalent by proof (see §5) |
| SR-07 | case-folded | KILLED `1 failed` | reason_match_is_case_sensitive |
| SR-08 | record the LAST match | KILLED `1 failed` | records_the_first_matching_line |
| **SR-09** | record `line.strip()` | **KILLED `1 failed`** | **records_the_raw_line_not_the_stripped_line** |
| SR-10 | `in` → `startswith` | KILLED `3 failed` | as SR-05 |
| SCHEMA-NOPAT | drop the `failure_reason` pattern | SURVIVED the five-file suite; KILLED in the schema suite `2 failed, 29 passed` | spec_failure_reason_rejects_edge_whitespace[leading/trailing-space] — finding F15 |
| CLEAR-GUARD-RAISE | raise if a non-`interpreter sample failed:` error reaches the clear guard | **NEVER FIRED** (252 tests) | reachability instrument — F5 |
| LATE-EXC-RAISE | raise on entry to the late `except` arm | fired: KILLED `2 failed` | interpreter_sample_failure(+after_child_exit) |
| **SILENT-KEEP-RAISE** | raise when the late `except` arm keeps a **non-null** early reading | **NEVER FIRED** (252 tests) | reachability instrument — **F1** |

**Totals: 33 mutants + instruments run. 22 killed by a named test · 5 survivors (LATE-NULL, DL_SCALE, LATE-EVERY, LG2-EARLY,
PINS-12KEY) · 2 equivalent-by-reachability (LATE-CLEARALL / CLEAR-GUARD-RAISE, proven with the raise instrument) ·
SR-06 equivalent by proof · SCHEMA-NOPAT killed only outside the lane's stated gate suite.** LG1 is equivalent by construction
(`_last_good` absent from the tree — `grep -rn "_last_good" proofs tests scripts` returns 0 code hits; `_interp_sampled` also 0).

## 4. F6 — the crash path, live (real probe, real checker, real validator)

```
probe rc= 1
probe stderr= "acp_probe: FileNotFoundError: [Errno 2] No such file or directory: '…/livecap/agent_self_delete.py'"
Traceback in stderr: False
files: ['agent-stderr.txt(0B)', 'env.json(9473B)', 'runtime-identity.json(1002B)', 'timeline.jsonl(491B)']
rid key count: 12   (11 pinned + probe_error)
probe_error: "FileNotFoundError: [Errno 2] No such file or directory: '…/livecap/agent_self_delete.py'"
agent_entrypoint_sha256: None

check_initialize.py request  <cap> -> rc=1
    failure_reason: negative: probe reported an error: FileNotFoundError: [Errno 2] No such file or directory: '…/agent_self_delete.py'
check_initialize.py response <cap> -> rc=1
    error code=-32602 message=Invalid params
negative_contract.validate_negative_dir(cap) -> NegativeFailure: probe reported an error: FileNotFoundError: [Errno 2] …
```
`env.json absent` is gone; the producer error is named at every layer. SOLID.

**F7 (coordinator hunk), reproduced both ways.** Current validator:
`0 → "probe reported an error: 0"` · `False → …False` · `[] → …[]` · `{} → …{}` · `"" → …(empty reason)` · `"x" → …x`.
Red on the previous validator (`f"…{rid['probe_error'] or '(empty reason)'}"`), pasted:
`4 failed, 1 passed, 50 deselected in 0.09s` — exactly the claimed shape.

## 5. F9 — schema + runner

* `proofs/schemas/spec.schema.json:36` — `{"type":"string","minLength":1,"pattern":"^\\S(.*\\S)?$"}`.
* Committed reason strings, re-counted from primary source: **7** `expect.failure_reason` values across the 6 committed
  `proofs/*/spec.json`; **20** reason-bearing strings across all `proofs/**/*.json`; **9** distinct values. **None** carries edge
  whitespace. The "**14** committed reasons" figure in the brief, the report, the commit body and the ledger is **not
  reproducible under any counting I could construct** (substance is fine, the denominator is invented).
* **SR-06 equivalence — CONFIRMED, no counter-example.** Proof: for `expected` matching `^\S(.*\S)?$`, `expected[0]` and
  `expected[-1]` are non-whitespace, so no occurrence of `expected` in `line` can begin inside `line`'s leading-whitespace run or
  end inside its trailing run; hence `expected in line ⇒ expected in line.strip()`. Conversely `line.strip()` is a contiguous
  substring of `line`, so `expected in line.strip() ⇒ expected in line`. The premise is really enforced: `scripts/proof-runner:154`
  validates every spec against the schema **before** the leg loop at `:186-208`. Mutant SR-06 survives, as ruled.
* **SR-09 killer reproduced red/green**: red on the mutant (`1 failed`, sole killer
  `test_runner_records_the_raw_line_not_the_stripped_line`), green on the unmutated runner. Non-tautologous.
* SR-05/07/08/10 all still killed (counts above).

## Findings

### R9-N5f-F1 — BLOCKING · SOLID · the acceptance bar's LATE-NULL mutant is NOT killed, and the branch the ruling added is never executed by any test
`vn10/repo/proofs/S0-01/tools/acp_probe.py:308-312` (the late `except (OSError, IOError)` arm; `:311` `if interp_realpath is None:`).
Two independent instruments:
1. **Mutant LATE-NULL** (`interp_realpath = None; interp_sha256 = None; probe_error = f"interpreter sample failed: {exc}"` in that
   arm) → **`252 passed`**. Its named killer `test_probe_fast_exit_agent_is_deterministic`
   (`tests/test_s0_01_acp_probe.py:1129`, assertion `:1167`) passed **5/5 unloaded**, and a direct 40-run measurement of shape D
   on the mutant gave **`interp null in 0/40`**. Under 8 CPU hogs it flipped: **killed 2/6, survived 4/6**.
2. **Reachability instrument SILENT-KEEP-RAISE** (`raise AssertionError` when that arm is entered with a non-null early reading)
   → **NEVER FIRED across the full 252-test suite**.
Observed vs expected: the brief's acceptance bar demands "every non-equivalent one killed by a NAMED test"; the report
(`| LATE-NULL | … | KILLED 1 failed | test_probe_fast_exit_agent_is_deterministic |`), the commit body ("Lane mutants: … LATE-NULL
… all KILLED by named tests (11/11)") and `todo/BUILD-TASKLIST.md:94` ("11/11 non-equivalent killed") all assert a kill I cannot
reproduce. The commit body further claims the behaviour itself — "a late readlink failure keeps the early reading, which fails the
pinned interpreter checks downstream rather than minting a hollow green" — for a branch no test executes. This is the same
class as the R9-N5e-F2 dead `_last_good` arm this round was convened to remove.
**Exact red test I would add** (built and measured on my copy — deterministic, no race, no wall clock):
in-process wrapper, `os.readlink` patched with a **call counter** so `/proc/*/exe` succeeds on call 1 (the early loop) and raises
`OSError` from call 2 on (the late sample); agent = the answering fixture. Measured:
`HEAD → rc=0 interp='/usr/bin/python3.11' sha_null=False probe_error=None` · `LATE-NULL → rc=1 interp=None sha_null=True
probe_error='interpreter sample failed: No such process'`. Assert `rid["agent_interpreter_realpath"] == os.path.realpath(sys.executable)`,
`rid["agent_interpreter_sha256"] is not None`, `"probe_error" not in rid`, `r.returncode == 0`.
**Minimal fix:** add that test; correct the LATE-NULL row in the report, the commit body and ledger `8j` to "killed by <new test>"
(or, until it exists, "not killed — race-only detection measured 0/5 unloaded").

### R9-N5f-F2 — BLOCKING · SOLID · the early interpreter fallback can read `/proc/self/exe` with the whole gate green (self-sampling hollow green at the only site that decides identity for silent agents)
`acp_probe.py:229-243` (early loop; readlink at `:231`).
Mutant **LG2-EARLY** (`os.readlink("/proc/self/exe")` in the early loop) → **`252 passed`** (probe file alone `49 passed`).
Concrete failing input, measured on my copy — a `#!/bin/bash` agent that reads one line and **never writes stdout**
(so only the early loop determines the identity):
```
HEAD       silent bash agent -> {'/usr/bin/bash': 6}
LG2-EARLY  silent bash agent -> {'/usr/bin/python3.11': 6}       <- the PROBE's own interpreter, gate green
```
`test_probe_interpreter_is_child_not_self` (`tests/test_s0_01_acp_probe.py:769`) is the only self-sampling killer, and its bash
agent **writes a response line**, so it exercises the LATE site only (LG2-LATE and LG2-POST both die on it; LG2-EARLY does not).
Every no-output shape (A, B, C, D, J, K, M — and any real agent that exits silently on the malformed initialize) takes its
identity from the untested site, and every such fixture in the suite is `#!{sys.executable}`, i.e. the wrong reading and the
right reading are the same file — the exact blind spot AF-AP-55 names, one site over.
Observed vs expected: `agent_interpreter_realpath` must be the CHILD's exe at every site; only two of three sites are pinned.
**Exact red test:** `test_probe_interpreter_is_child_not_self_for_a_silent_agent` — the bash agent above (`read line; sleep 3`,
no stdout), `ACP_PROBE_TIMEOUT=2`; assert `rid["agent_interpreter_realpath"] != os.readlink(f"/proc/{os.getpid()}/exe")` and
`os.path.basename(rid["agent_interpreter_realpath"]) == "bash"`. Green on HEAD, red on LG2-EARLY (measured above).

### R9-N5f-F3 — SOLID · F4's "the bound is pinned" pins only the deadline/step RATIO, not the bound
`acp_probe.py:36-38`; `tests/test_s0_01_acp_probe.py:1542-1609`, assertion `:1607` `assert count == 101`.
Mutant **DL_SCALE** (`_EARLY_SAMPLE_DEADLINE_S 0.2 → 0.4` **and** `_EARLY_SAMPLE_STEP_S 0.002 → 0.004`) → **`252 passed`**,
non-equivalent (the real early-loop wall bound doubles from 0.2 s to 0.4 s — the very window R9-N5e-F5 measured as widening the
BrokenPipe race, since `_sha256_file(/usr/bin/python3.11)` already costs 18–25 ms inside it). DL_DOUBLE alone dies only because the
test reads `_dl = acp_probe._EARLY_SAMPLE_DEADLINE_S` at run time and the counter is expressed in loop iterations.
**Exact red test:** add, in the same fake-clock wrapper, `assert acp_probe._EARLY_SAMPLE_DEADLINE_S == 0.2` and
`assert acp_probe._EARLY_SAMPLE_STEP_S == 0.002`, or assert the fake clock's final value
(`_clock_us[0] == 200_000`) rather than only the attempt count.
**Fake-clock coverage question (asked in the brief) — answered SOLID:** the loop's clock IS the module attribute the test patches
(`acp_probe.time`), and mutant **FC-BIND** (`from time import monotonic, sleep, monotonic_ns` used in the loop) is **KILLED** by
`test_probe_early_sample_loop_bound_is_pinned`. No wall-clock assertion exists in the new tests (`time.time`/`perf_counter`: 0 hits;
the only `< 10` / `< 15` elapsed bounds are pre-existing, at `:327` and `:380`).

### R9-N5f-F4 — SOLID · **the extra item: `test_runner_unmet_when_expected_reason_is_multiline` should KEEP its runner role AND gain a schema-rejection sibling**
`tests/test_s0_01_spec_runner.py:437-509`; the pattern strip at `:447-450`.
Decision, with the reasons:
1. **It still proves something real about the runner under use.** It is the sole killer of SR-03 (`expected in whole_text`), which
   is a live property of `scripts/proof-runner:193-198` (`.splitlines()` + per-line `in`), independent of the schema. Deleting it
   would lose that killer. **Keep it.**
2. **But it no longer describes production behaviour, and its docstring now lies by omission.** In production a multiline
   `failure_reason` never reaches the leg loop: `proof-runner:154` rejects it at `_validate` and the runner raises a schema error,
   not `negative-control-unmet`. I reproduced the schema rejection: `"a\nb"` → rejected with an error whose path names
   `failure_reason`.
3. **Nothing currently tests that rejection.** `tests/test_spec_probe_schemas.py:94-111` parametrizes only `" leading-space"` and
   `"trailing-space "`; `grep -n "multiline\|newline"` over that file returns **0 hits**.
**Verdict: keep it as the SR-03 killer, rename/redocument it, and ADD the schema-rejection test.**
Minimal change: (a) rename to `test_runner_per_line_rule_holds_for_a_multiline_expected_reason`, docstring "the schema forbids a
multiline reason in production (see `test_spec_failure_reason_rejects_multiline`); this pins the matcher itself, with the pattern
lifted from the schema copy so the reason can reach the loop"; (b) add `"a\nb"` (and `"foo\n"` — see F5) to the
`test_spec_failure_reason_rejects_edge_whitespace` parametrize list, renaming it `…rejects_edge_whitespace_and_newlines`.

### R9-N5f-F5 — SOLID · the `failure_reason` pattern does NOT reject a trailing newline; the stated guarantee is false for that class
`proofs/schemas/spec.schema.json:36`. Python's `re` (which `jsonschema` uses) lets `$` match before a final newline, so
`^\S(.*\S)?$` accepts `"foo\n"`. Measured against the real schema:
```
trailing-newline 'foo\n'   schema_rejected=False     <- HOLE
leading-newline  '\nfoo'   schema_rejected=True
trailing-tab     'foo\t'   schema_rejected=True
trailing-space   'foo '    schema_rejected=True
leading-space    ' foo'    schema_rejected=True
multiline        'a\nb'    schema_rejected=True
cr-trail         'foo\r'   schema_rejected=True
nbsp-trail       'foo\xa0' schema_rejected=True
trailing-2nl     'foo\n\n' schema_rejected=True
```
Observed vs expected: the report, the commit body and the ledger all say "leading or trailing whitespace rejected"; one class is
not. Consequence, re-derived from primary source (`proof-runner:193-198` splits on lines, so no candidate line ever contains `\n`):
such a spec is **fail-closed** (`negative-control-unmet`), not fail-open, and the SR-06 equivalence proof still holds — so this is
a broken guarantee, not a hollow green.
**Exact red test:** add `("foo\n", "trailing-newline")` to the parametrize at `tests/test_spec_probe_schemas.py:94`.
**Minimal fix:** `"pattern": "^\\S(.*\\S)?(?![\\s\\S])"`, or keep the pattern and add `"allOf": [{"not": {"pattern": "\\s$"}}]`
(both reject `"foo\n"` under Python `re` and under ECMA-262). Note this is an **attested** input — see F12.

### R9-N5f-F6 — SOLID · the "sample once, at the FIRST a2c byte" choice is neither pinned nor stated
`acp_probe.py:294-295` (`if not _late_sampled: _late_sampled = True`).
Mutant **LATE-EVERY** (re-sample on every chunk) → **`252 passed`**: neither the once-only rule nor its opposite is gated.
The comment at `:292-293` states the timing ("at the first a2c chunk, ALWAYS re-read") but is silent on what happens to an agent
that execs **after** its first byte — the residual of the very class (AF-AP-55) this round closes. Measured with a purpose-built
agent (writes one byte, flushes, then `os.execl("/bin/dash", …)`): recorded interpreter `/usr/bin/dash` **12/12** — i.e. which
exec stage is recorded is decided by scheduling, not by a stated rule.
**Exact red test / choice statement:** either add `test_probe_interpreter_is_sampled_once_at_the_first_a2c_byte` (patch
`os.readlink` to return a distinct sentinel from call 3 on, assert the recorded value is the call-2 value), or adopt LATE-EVERY as
the rule and pin it. Either way, one line in the `:292-293` comment saying which.

### R9-N5f-F7 — SOLID · the `startswith` clear-guard is unreachable (equivalent-by-reachability), so the "ONLY that class" rule is untestable
`acp_probe.py:304-307`. Two instruments: mutant **LATE-CLEARALL** (unconditional `probe_error = None`) → `252 passed`;
**CLEAR-GUARD-RAISE** (raise if a non-`interpreter sample failed:` error reaches the guard) → **never fired** over 252 tests.
Mechanism re-derived from primary source: only two writers precede `:305` — `:239` (always the `interpreter sample failed: ` class)
and `:263` (BrokenPipe, which sets `c2a_delivered = False` and therefore skips the whole `if c2a_delivered:` block at `:275`). So
no other class can be live there. This is defensive code, correctly written, that **cannot** be gated.
**Recommended:** state it in the comment ("defensive: no other probe_error class can be live here — `:263` excludes itself via
`c2a_delivered`") so the next verifier does not re-open it; no test is possible. Do NOT count it as a killed mutant.

### R9-N5f-F8 — SOLID · shape N's behaviour changed (rc 0 → 1) with no test and no mention anywhere
Shape N (an agent whose shebang interpreter is unlinked at start): parent `736bb94` recorded `…/myshell`, sha `86d31f6f`, rc 0,
`probe_error` null. HEAD records `…/myshell (deleted)`, `agent_interpreter_sha256: null`, **rc 1**,
`probe_error = "interpreter sample failed: [Errno 2] No such file or directory: '…/myshell (deleted)'"`.
This is a direct, correct consequence of the later-reading-wins rule (the late sample runs after the unlink) and is arguably more
truthful — but it flips a previously-clean capture to a **failing negative leg** (`validate_negative_dir` raises on any non-null
`probe_error`), and it appears in no test, no report line, no commit line and no ledger line.
**Exact red test:** `test_probe_interpreter_deleted_after_start_is_a_loud_probe_error` — the shape-N agent; assert rc 1,
`rid["agent_interpreter_realpath"].endswith(" (deleted)")`, `rid["agent_interpreter_sha256"] is None`, and
`rid["probe_error"] == f"interpreter sample failed: [Errno 2] No such file or directory: '{path} (deleted)'"`.

### R9-N5f-F9 — SOLID · the 11-key identity set is hardcoded in three places; a `pins` change is invisible to the probe gate
`acp_probe.py:104-116` (`_write_evidence`), `acp_probe.py:410-423` (M3 handler), `tests/test_s0_01_acp_probe.py:1285-1291` and
`:1717-1723` (two literal `expected_keys` sets). `grep -rn NEGATIVE_IDENTITY_KEYS proofs tests` → only `pins.py:104` and
`negative_contract.py:174`; the probe tests never reference pins.
Mutant **PINS-12KEY** (add `"agent_cgroup"` to `pins.NEGATIVE_IDENTITY_KEYS`) → probe suite **`49 passed`**. The brief's ruling
said "build the identity with ALL 11 pinned keys (`pins.NEGATIVE_IDENTITY_KEYS` is the set)".
Consumer-side drift IS caught (`negative_contract.py:174-176` raises `runtime identity key <k> absent`) — but only when a real
capture is validated, never by the lane's own gate.
**Exact red test:** in `tests/test_s0_01_acp_probe.py`, import `pins` and assert
`set(rid) - {"probe_error"} == set(pins.NEGATIVE_IDENTITY_KEYS)` in both the self-deleting and the M3 tests (replacing the two
literals). Red on PINS-12KEY, green on HEAD.

### R9-N5f-F10 — SOLID · the post-loop fallback contributes nothing for any real agent; only fault injection reaches it
`acp_probe.py:359-375`. Block-attribution instrument: `POST_RL`/`POST_SHA` fired in **0 of 19** real shapes. For shapes C/J/K/M
(c2a delivered, no a2c byte ever) the block *runs* but both inner guards are false because the early loop already filled the pair.
The lane's Self-attack #1 ("The post-loop block … is the additional fallback after the a2c timeout. Both are tested") is true only
under a patched readlink; POST-DEL is killed solely by `test_probe_post_loop_sha256_failure_truthful_error`, which patches
`os.readlink`. Not a defect — but the claim "tested for real agents" is unsupported. Informational; no fix required beyond wording.

### R9-N5f-F11 — SOLID · report / commit / ledger hygiene (file:line + counts + one non-reproducible mutant row)
Re-derived at my copy of the PIN:
| claim | in the report | actual |
|---|---|---|
| F13 comment "the reading at the first a2c byte is authoritative" | `acp_probe.py:210-214` | **`:224-227`** |
| F13 "never from /proc/self/exe" restored | `acp_probe.py:204` | **`:219`** |
| F12 `realpath(sys.executable)` assertions | "Three … 457, 659, 895" | **four** — 457, 659, 895 and **1468** (the lane's own new wrapper test); plus a docstring mention at `:652` |
| F3 equality assertion | `tests/test_s0_01_acp_probe.py:1239` | `:1241` (message string starts `:1237`) |
| "the 14 committed reasons" | report, commit, ledger | **7** spec-leg values / 20 reason strings / 9 distinct — see §5 |
| EV_OUTSIDE killer | `test_probe_self_deleting_script_is_probe_error_not_traceback` | my implementation dies on `test_probe_m3_handler_writes_complete_evidence` (both killed; the named test differs) |
| LATE-NULL | "KILLED 1 failed" | **not reproducible** — see F1 |
| red-before, env shebang | "12/12 `/usr/bin/env`" | parent measured **10/12 env + 2/12 python** unloaded and loaded (direction right, figure not) |
Report claim I did verify as stated: `tests/test_s0_01_check_initialize.py` **NOT touched** — `git diff --stat 736bb94 d08c7bf`
lists 8 files and that is not one of them.

### R9-N5f-F12 — SOLID (informational; already remediated downstream) · at the PIN, `validate-ledger integrity` is RED — the schema `pattern` is an attested input
Reproduced at `98792f5` on my copy:
```
S0-09 INVALID  S0-10 INVALID  S0-11 INVALID  S0-12 INVALID
conformance_checked_decision numerator=0 denominator=3
execution_proof numerator=0 denominator=7
attestation-mismatch: S0-09 proofs/schemas/spec.schema.json   (+ S0-10, S0-11, S0-12)
rc=1
```
Attested `spec.schema.json` at the PIN = `0485e31e…`; the actual file = `5f50497a…`. **Already fixed downstream**: `b1eb0fa`
regenerates the four attestations to `5f50497a…`. Not blocking; recorded because neither the lane report nor the 8j commit body
mentions that the F9 hunk breaks the four minted proofs, and a reader taking 98792f5 as the gate state would be misled.

### R9-N5f-F13 — SOLID · `test_probe_env_shebang_interpreter_is_constant` never asserts the probe's exit code, and runs with the full inherited environment
`tests/test_s0_01_acp_probe.py:1479-1536`. The 12 `subprocess.run(...)` results at `:1519-1522` are discarded; the test would pass
with the probe exiting 1 on every run as long as `runtime-identity.json` carried the right pair. It also uses
`env = os.environ.copy()` where the neighbouring probe tests use a 6-key minimal env (`PATH`/`HOME` only), so any inherited
`ACP_PROBE_*`/`S0_01_*` would silently take effect.
**Exact red test / fix:** capture the result and add `assert r.returncode == 0, r.stderr` inside the loop, and
`assert "probe_error" not in rid`.

### R9-N5f-F14 — UNSURE (measured low risk) · the LATE-NOCLEAR killer carries a 0.3 s wall-clock conjunct it does not need
`tests/test_s0_01_acp_probe.py:1645` — `if _sha_call[0] == 1 and time.monotonic() - _start < 0.3:`. If the first `_sha256_file`
call ever lands past 0.3 s, the injected failure does not fire, no early error is created, and the test passes **vacuously**
(LATE-NOCLEAR would survive). Measured margin: elapsed-to-first-sha over 10 runs `min=0.0006 max=0.0009 median=0.0007` s —
about 400×; and LATE-NOCLEAR was killed **6/6 under 8 CPU hogs**. The lane's Self-attack #2 has the polarity backwards
("a secondary guard" — it is the switch that can silently disable the injection), but the risk is small.
**Minimal fix:** drop the time conjunct; `_sha_call[0] == 1` alone is already the deterministic gate (the early loop's sha is
provably the first `_sha256_file` call — `:237` precedes `:299`, `:372`, `:99`, `:106`).

### R9-N5f-F15 — SOLID · the F9 hunk's only killer lives outside the gate the lane and the ledger quote
Mutant SCHEMA-NOPAT survives the five-file suite (`252 passed`) and dies only under
`tests/test_spec_probe_schemas.py` (`2 failed, 29 passed`). The lane's acceptance bar says "every mutant run = the full five-file
suite"; for the schema hunk that suite is blind. The lane did run the schema suite once (`31 passed`) but never mutated the schema.
**Minimal fix:** none in code — record in the ledger that the F9 hunk's gate is
`tests/test_spec_probe_schemas.py tests/test_proof_runner.py`, and run schema mutants against it.

## What I reproduced vs reviewed statically vs skipped

**Reproduced (ran it myself):** the premise and file identity; both five-file suite runs and the schema/runner run; the 246→252
denominator; the 6-test red state on the parent probe; the 19-shape table with a 3-site block-attribution instrument; W/EV 12×
unloaded and under 4 hogs, on HEAD **and** the parent; A/D 20× each with per-arm exact reason and stderr checks, unloaded and
loaded; 33 mutants/instruments each over the full five-file suite; the live self-deleting capture through the real
`check_initialize.py request|response` and `validate_negative_dir`; the F7 red (`4 failed, 1 passed`) and all six current messages;
the schema pattern probe (9 hostile strings); the committed-reason census; `validate-ledger integrity`; pyflakes; the exact-reason
grep census (13 equality / 0 substring survivors / 16 exact stderr / 4 `"Traceback" not in`).
**Reviewed statically (no execution):** the SR-06 equivalence proof (the schema-enforcement premise itself was reproduced at
`proof-runner:154`); the consequence of F5's trailing-newline hole for the runner (re-derived from `.splitlines()` at `:193-198`);
`tmp_path` hygiene (all probe writes go to `tmp_path`; `tests/test_s0_01_spec_runner.py::_copy` copies `proofs/` + `scripts/`
under `tmp_path`; the only absolute literal, `/tmp/fake_interp (deleted)`, is a fake readlink return, never written).
**Deliberately skipped:** the PC leg — Python 3.13 and the real `hermes-acp` multi-stage exec shape are **NOT run here**; no bridge
banner this session. (The ledger records a coordinator PC gate on this same `98792f5`: `283 passed in 15.12s` and a 3.13 leg
`102 passed in 48.92s`; I did not reproduce either, and neither covers a real multi-stage-exec agent, which is precisely the class
F2 above leaves unpinned at the early site.) I also did not re-run the tree-wide suite (`proofs/ spikes/ tests/`) — out of scope
and unaffected by these six files beyond the attestation item in F12.

## Verdict

**NOT-READY** — blocking: **R9-N5f-F1** (the acceptance bar's LATE-NULL mutant survives `252 passed`; the ruling's
"keep the early reading silently" branch is never executed by any test — proven twice, by the surviving mutant and by a
never-firing raise instrument — while the report, the commit body and ledger 8j all assert 11/11 killed) and **R9-N5f-F2**
(the early fallback site can read `/proc/self/exe` with the entire gate green; a silent `#!/bin/bash` agent records the probe's own
python 6/6 under the mutant — the AF-AP-55 class surviving one site over from the one this round fixed).

Both are closable with the two red tests specified above (each measured red-on-mutant / green-on-HEAD on my copy) plus the
report/commit/ledger corrections in F11. The F1/F8/F2/F3/F5/F6/F7/F9 substance of the lane is otherwise **verified**: the
later-reading-wins fix is real and reproduces against a paired parent control, the crash path writes a complete, correctly
attributed evidence set through the real checker, and every reason string is now asserted exactly (0 substring survivors).
Nothing in this verdict depends on the PC leg, which I did not run.
