Verification complete. Report follows.

---

# VERIFY-N5e (round 9) — adversarial grade of lane N5e + the coordinator's F4/F9 hunks

## Premise + disk

```
git log --oneline -2
57a7df6 S0-01 WIP checkpoint 8f: the probe's interpreter sample is deterministic and truthfully attributed, …
aa477ca briefs: lane N5e's first PC attempt died on the exhausted fallback chain; its partial diff kept as reference
```
PREMISE HOLDS. `df -h /` before the first batch: `/dev/vda 252G 22G 16G 60% /` (59% at the end, never below 16 G, no ENOSPC).
One materialised copy `scratchpad/vn9/repo` (132 M, `git archive HEAD | tar -x`, then `git init` + commit for hygiene); all 8 scope files sha256-identical to the `57a7df6` blobs (verified, and re-verified identical after every mutant). Shared tree: read-only git commands only — it carries other lanes' live edits (`check_acp_conformance.py`, `frame_tee.py`, `scripted_backend.py`, …); its `git log --oneline -1` is still `57a7df6` and I never wrote to it. Every mutant restored from `scratchpad/vn9/pristine/`, never git-restore/stash.

## 1. Agent-shape table — real probe, real agents (`ACP_PROBE_TIMEOUT` 2–5 s), HEAD

| # | agent shape | rc | `agent_interpreter_realpath` / sha8 | `agent_exit_code` | `probe_error` |
|---|---|---|---|---|---|
| A | `import sys; sys.exit(0)`, no stdout | **1** (19/20; 1/20 rc=0) | `/usr/bin/python3.11` / f56a5885 | 0 | `BrokenPipeError: agent process exited before c2a write landed` |
| B | `sys.exit(1)`, no stdout | 1 | `/usr/bin/python3.11` / f56a5885 | 1 | same |
| C | `os.close(1)` then sleep 3 | 0 | `/usr/bin/python3.11` / f56a5885 | 0 | null |
| D | 1 byte then `os._exit(0)` | **RACY** 37/40 rc=1 unloaded, 40/40 rc=1 loaded | `/usr/bin/python3.11` / f56a5885 (40/40) | 0 | BrokenPipe on the rc=1 arm |
| E | full answer + `sys.stdin.read()` | 0 | `/usr/bin/python3.11` / f56a5885 | 0 | null |
| F | full answer, exit immediately | 0 | `/usr/bin/python3.11` / f56a5885 | 0 | null |
| G | first byte after 2 s, then answer | 0 | `/usr/bin/python3.11` / f56a5885 | 0 | null |
| H | 1 byte, sleep 0.05, `os._exit` | 0 | `/usr/bin/python3.11` / f56a5885 | 0 | null |
| I | answer with no trailing newline | 0 | `/usr/bin/python3.11` / f56a5885 | 0 | null |
| J | never answers, hangs | 0 | `/usr/bin/python3.11` / f56a5885 | −9 | null |
| K | closes stdout, sleeps 60 | 0 | `/usr/bin/python3.11` / f56a5885 | −9 | null |
| L | partial line then hang | 0 | `/usr/bin/python3.11` / f56a5885 | −9 | null |
| M | self-SIGTERM after stdin, no stdout | 0 | `/usr/bin/python3.11` / f56a5885 | −15 | null |
| N | unlinks its own shebang interpreter | 0 | `…/shapes/myshell` / 86d31f6f (**no ` (deleted)` marker; sampled pre-unlink**) | 0 | null |
| BP1/BP2 | BrokenPipe (readlink patched to fail) | 1 | null / null | 0 | BrokenPipe (post-loop correctly skipped) |
| **W** | **`#!/bin/sh` wrapper, `sleep 0.05`, `exec python …`** | **0** | **`/usr/bin/dash` / 86d31f6f — WRONG, 3/3** | 0 | **null** |
| **EV** | **`#!/usr/bin/env python3`** | **0** | **`/usr/bin/env` 9/12 unloaded, 6/12 loaded; `/usr/bin/python3.11` otherwise — NON-DETERMINISTIC** | 0 | **null** |
| DASH | `#!/bin/dash`, single exec, 40× loaded | 0 | `/usr/bin/dash` 40/40 | 0 | null (no literal self-sampling found) |

**Paired control on the parent commit `aa477ca`, same box, same agents:** W → `/usr/bin/python3.11` 3/3; EV → `/usr/bin/python3.11` **12/12**; shape D → 26/40 rc=0, 14/40 rc=1, 2 distinct interpreter triples.

**Retry-loop bound:** wall clock ONLY (`_sample_deadline = time.monotonic() + 0.2`, `acp_probe.py:200`); no attempt cap. Measured with readlink patched to always fail: **96–97 attempts, 0.2007–0.2019 s** (deadline test is at the END of the body, so ≥1 iteration always runs and it can overshoot by one readlink + one 2 ms sleep). `_sha256_file(/usr/bin/python3.11)` = 6,639,992 bytes, **18.8–24.9 ms**, executed between `Popen` (:182) and `proc.stdin.write` (:242).

**`_last_good`:** keeps the first successful readlink — and the branch that consumes it is **unreachable** (see F2). It can never be a pre-exec reading of the probe's own interpreter (`Popen`'s errpipe blocks the parent until the child's first `execve`; dash agent 40/40 under load never recorded python). It CAN be — and routinely is — a **pre-final-exec** reading of an intermediate stage (F1).

**rc:** race-decided for shapes A and D. The determinism test's docstring says so honestly (`"rc may vary"`); the **commit message does not** (F5).

## 2. Mutant table (every run = the full five-file suite, 242 tests)

| id | mutation | result | killing test |
|---|---|---|---|
| NOOP | unmodified | `242 passed in 52.20s` | — |
| N8 | post-loop block dedented out of `if c2a_delivered:` | **KILLED** `1 failed, 241 passed` | `test_probe_broken_pipe_post_loop_placement` |
| F3REASON | fixed string kept in the post-loop sha arm | **KILLED** | `test_probe_post_loop_sha256_failure_truthful_error` |
| F3SWAP | the two F3 wordings swapped | **KILLED** | same |
| **F3PREFIX** | **drop the `interpreter sample failed: ` prefix (`probe_error = f"{exc}"`)** | **SURVIVED** `44 passed` | — (finding F3) |
| APF1A | sample once at Popen, no retry | **KILLED** | `test_probe_early_retry_recovers_from_transient_readlink_failure` |
| G2 | re-introduce `if proc.poll() is None:` | **KILLED** | `test_probe_interpreter_sample_failure_after_child_exit` |
| **LG1** | **delete the `_last_good` fallback arm entirely** | **SURVIVED `242 passed` — proven EQUIVALENT (dead code)** | — (finding F2) |
| LG2 | seed `_last_good = readlink('/proc/self/exe')` (self-sampling) | **KILLED** `5 failed` | 5 tests incl. `test_probe_interpreter_sample_failure` |
| LG3 | `raise AssertionError` inside the `_last_good` branch | **NEVER FIRED** (148 tests + 14 shapes) | — (reachability instrument) |
| **DL_DOUBLE** | **deadline 0.2 → 0.4 s** | **SURVIVED `242 passed`** — NOT equivalent | — (finding F4) |
| DL_ZERO | deadline 0.2 → 0.0 s | **KILLED** | `test_probe_early_retry_recovers_from_transient_readlink_failure` |
| EV_OUTSIDE | `_write_evidence` moved back outside the handler | **KILLED** | `test_probe_self_deleting_script_is_probe_error_not_traceback` |
| EV_SWALLOW | handler swallows a write error (`except: pass`) | **KILLED** | same |
| INLOOP_MARK | marker in the in-loop sample block | **0 of 14 shapes reached it** | — (finding F8) |

**Probe mutants: 9 killed / 12 non-equivalent + 1 proven-equivalent + 2 instruments.** Survivors: F3PREFIX, DL_DOUBLE (both non-equivalent → real gaps); LG1 equivalent.

**Evidence-set on failure (self-deleting agent), pasted:**
```
capture dir: agent-stderr.txt (0 B)  runtime-identity.json (187 B)  timeline.jsonl (491 B)   <- env.json ABSENT
runtime-identity.json = {"probe_error": "FileNotFoundError: [Errno 2] No such file or directory: '…/agent_self_delete.py'"}   (ONE key)
probe rc=1, no Traceback
check_initialize.py request  -> failure_reason: negative: env.json absent      rc=1
check_initialize.py response -> error code=-32602 message=Invalid params        rc=1
```

## 3. Runner mutants + live differentials (full five-file suite)

| id | mutation | result | killer |
|---|---|---|---|
| NOOP | — | `242 passed` | — |
| SR-05 | per-line `in` → `==` | KILLED (2) | `…observed_line_not_the_expected_reason`, `…first_matching_line` |
| SR-06 | match against `line.strip()` | **SURVIVED** | — |
| SR-07 | case-folded match | **KILLED** | `test_runner_reason_match_is_case_sensitive` (new) |
| SR-08 | record the LAST match | **KILLED** | `test_runner_records_the_first_matching_line` (new) |
| SR-09 | record `line.strip()` | **SURVIVED** | — |
| SR-10 | `in line` → `line.startswith` | KILLED (2) | as SR-05 |

**SR-06 live differential (settles "equivalent under use" = NO):** spec `failure_reason = " protocol-violation: indented reason"` (leading space), checker prints `"  protocol-violation: indented reason"` →
`HEAD rc=0 observed='  protocol-violation: indented reason'` · `SR-06 rc=1 stderr='negative-control-unmet: S0-93'`.
**SR-09 live differential:** checker prints `"   failure_reason: negative: <reason>   "` →
`HEAD observed='   failure_reason: negative: protocol-violation: whitespace line   '` · `SR-09 observed='failure_reason: negative: protocol-violation: whitespace line'` (both rc 0, nothing distinguishes).
**Non-tautology of the two new tests: reproduced** — each is the sole killer of its mutant and green on the unmutated runner.

## Findings

### R9-N5e-F1 — BLOCKING · SOLID · the early sample records an INTERMEDIATE exec stage: wrong interpreter, silently, and non-deterministically
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vn9/repo/proofs/S0-01/tools/acp_probe.py:200-227` (accept-first-readlink at `:216-224`).
`Popen`'s errpipe guarantees the child has completed its **first** `execve` — not its last. Concrete failing inputs, both run against HEAD and against the parent commit on the same box:
* `#!/bin/sh` wrapper → `sleep 0.05` → `exec $PY real_agent.py`: **HEAD 3/3 records `/usr/bin/dash`, sha `86d31f6fb799…`, rc 0, no probe_error**; `aa477ca` 3/3 records `/usr/bin/python3.11`, sha `f56a588548dd…`.
* `#!/usr/bin/env python3`: **HEAD 9/12 `/usr/bin/env` (sha `595f3912fa7d…`) + 3/12 `/usr/bin/python3.11` unloaded; 6/12 + 6/12 under 4 hogs**; `aa477ca` **12/12** `/usr/bin/python3.11`.
Observed vs expected: `agent_interpreter_realpath`/`_sha256` must name the interpreter that RUNS the agent (they are pinned exactly at `negative_contract.py:181-182` against `pins.PINNED_AGENT_INTERPRETER_REALPATH`); HEAD records a transient stage, with a run-to-run flip. The suite is blind because every fixture is single-exec (`#!{sys.executable}`; `test_probe_interpreter_is_child_not_self` uses `#!/bin/bash`). The report's Self-attack #1 rules this out citing "exec completes within microseconds" and that bash test — **falsified**.
Exact red test I would add: `test_probe_interpreter_is_the_final_exec_not_a_wrapper` — the `/bin/sh`+`sleep 0.05`+`exec` agent above, assert `rid["agent_interpreter_realpath"] == os.path.realpath(sys.executable)`; plus `test_probe_env_shebang_interpreter_is_constant` — the `#!/usr/bin/env python3` agent 12×, assert one distinct `(realpath, sha256)` pair equal to python's.
Minimal fix (built and measured on my copy): make the **later** successful reading authoritative — keep the post-`Popen` loop as a fallback and re-read `/proc/<pid>/exe` once at the first a2c byte, overwriting (and clearing an `interpreter sample failed:` probe_error on late success). Measured on that variant: env-shebang **12/12** python, wrapper **4/4** python, dash agent **4/4** dash, shape D **20/20** constant triple. (Attempt-1's rejected `_exec_window_end`/`_self_exe` guard does NOT fix it — I built it: env-shebang **12/12 `/usr/bin/env`**, deterministically wrong.)

### R9-N5e-F2 — BLOCKING · SOLID · the `_last_good` fallback is DEAD CODE; the commit message, the code comment and the report all claim a capability that cannot execute
`acp_probe.py:205-215`. `_last_good` is assigned only at `:217`, immediately before the unconditional `break` at `:224`, so at the `except` arm it is always `None`. Two independent instruments: mutant **LG1** (delete the arm) → `242 passed`; **LG3** (`raise AssertionError` inside it) → never fired across 148 tests and 14 real agent shapes.
Observed vs expected: the comment at `:206` ("Child may have died — accept the last good reading if any"), the commit message ("`_last_good` keeps the first successful reading"), and the report's kept/modified table ("added `_last_good` fallback for children that die mid-loop") describe behavior that does not exist.
Exact red test: none is possible for unreachable code — either delete `:206-214` (surgical) or make it reachable as part of F1's fix (re-read until the deadline, keep the last good), then pin it with an agent killed mid-loop.

### R9-N5e-F3 — BLOCKING · SOLID · the F3 killer asserts a substring, so the reason prefix is unpinned
`tests/test_s0_01_acp_probe.py:1239` — `assert "No such file or directory" in rid["probe_error"]`. Mutant **F3PREFIX** (`probe_error = f"{exc}"`, `acp_probe.py:345`) → `44 passed`, SURVIVES: a capture whose `probe_error` is a bare `[Errno 2] No such file or directory: '…'` passes. The brief demanded `probe_error == "interpreter sample failed: [Errno 2] No such file or directory: '<path>'"`. Attempt-1's rejected `test_probe_interpreter_sample_reason_is_truthful` carried exactly `assert rid["probe_error"].startswith("interpreter sample failed: ")` — dropped without replacement (item 7).
Fix: assert equality against the computed string (or at minimum add the `.startswith("interpreter sample failed: ")` line).

### R9-N5e-F4 — SOLID · the F3 test does not pin WHICH block produced the value; the 200 ms bound is unpinned
Mutant **DL_DOUBLE** (0.2 → 0.4 s) → `242 passed`, non-equivalent. Block-attribution instrument (markers in both sha-failure arms, run under the F3 test): **HEAD → `POST_LOOP`; DL_DOUBLE → `RETRY_LOOP`; the test passes both times.** The report's Self-attack #2 ("`agent_interpreter_realpath == "/tmp/fake_interp (deleted)"` … confirming the post-loop block ran") is unsupported by the assertions.
Red test: assert the loop's bound directly (count `/proc/*/exe` readlink attempts under an always-failing patch: `assert 90 <= n <= 105`, measured 96–97) and add a variant whose gate window exceeds the deadline so only the post-loop can produce the value.

### R9-N5e-F5 — BLOCKING (the CLAIM, not the behavior) · SOLID · F1's actual defect is not closed, and the commit message/ledger say it is
Behaviour, measured: shape D 40 runs — HEAD **37/40 rc=1 unloaded, 3/40 rc=0; 40/40 rc=1 loaded**; `aa477ca` **26/40 rc=0, 14/40 rc=1**. Shape A — HEAD **19/20 rc=1, 1/20 rc=0** (round 8: 20/20 rc=1, deterministic, exact reason). Mechanism re-derived from primary source + measurement: the early sample hashes the 6.64 MB interpreter (18.8–24.9 ms) between `Popen` (`:182`) and `stdin.write` (`:242`), widening the BrokenPipe window.
The landed determinism test drops `rc` from the assertion the brief specified (`(rc, interpreter-is-null)` pair); its docstring is honest. The **commit message and `todo/BUILD-TASKLIST.md` checkpoint 8f are not**: "now yields a constant interpreter triple 20/20 where round 8 measured 70 %/43 %/0 % flips" sets the new triple against round 8's *rc-flip* rate. rc still flips, worse for shape D and newly for shape A.
Also `tests/test_s0_01_acp_probe.py:1026` `test_probe_agent_exits_without_output_is_fail_loud` no longer asserts fail-loud: it accepts rc 0 or 1 and dropped `assert r.stderr.strip() == "acp_probe: …"`. The name is now false.
Fix: one-line correction in the commit/ledger wording ("the interpreter triple is constant; rc stays race-decided for agents that exit before the c2a write"), and either rename the test or restore an rc assertion for the shapes where rc IS deterministic.

### R9-N5e-F6 — BLOCKING · SOLID · F8's crash path writes a PARTIAL evidence set and the checker misattributes the reason
`acp_probe.py:378-392` (M3 handler) writes a **1-key** `runtime-identity.json` and **no `env.json`**; `_write_evidence` raises at `:88` (`_sha256_file(agent_realpath)`) before any file is written. Measured (self-deleting agent): capture = `agent-stderr.txt`, `runtime-identity.json` (probe_error only), `timeline.jsonl`. `check_initialize.py request` → `failure_reason: negative: env.json absent` rc 1. DEFERRED is avoided (the brief's letter is met) but the surfaced reason names a missing file, not the producer crash — the R7-N5c-F1 misattribution class. `_write_evidence`'s docstring (`:79-82`) implies the evidence survives.
Fix: in the handler, write `env.json` too and merge the identity fields already in scope (all of them are) instead of a 1-key object — or have `_write_evidence` degrade `agent_entrypoint_sha256` to `None` with a note.
Red test: assert the crash capture holds all four files and that `check_initialize.py request` prints a reason naming the producer error.

### R9-N5e-F7 — SOLID · F9's message loses the value for falsy non-string `probe_error` (same lying-message class as F3)
`proofs/S0-01/negative_contract.py:164` — `f"probe reported an error: {rid['probe_error'] or '(empty reason)'}"`. Differential (PRE `aa477ca` vs HEAD): `probe_error` = `0` / `[]` / `{}` / `false` → PRE printed `0` / `[]` / `{}` / `False`; **HEAD prints `(empty reason)` for all four**. No falsy carve-out remains (`is not None` catches every non-None), but an explicit `"probe_error": null` still validates OK on both — the probe never writes null, so a forged null is a signature that goes unnoticed.
Fix: `{'(empty reason)' if rid['probe_error'] == '' else rid['probe_error']!r}`. Red test: `_set_rid(neg, probe_error=0)` → expect `probe reported an error: 0`.

### R9-N5e-F8 — SOLID · the in-loop and post-loop samples are dead for every real agent
Marker instrument planted at `acp_probe.py:277`: `IN_LOOP_SAMPLE_REACHED` fired in **0 of 14** agent shapes. The comment at `:276` ("sample interpreter after first a2c byte, before wait") and the commit's "the in-loop and post-loop samples stay as fallbacks" describe paths reachable only when `/proc/<pid>/exe` is unreadable for a full 200 ms — i.e. only under a patched readlink. This is the structural reason F1's wrong first reading is never corrected. Fixing F1 as proposed restores the in-loop sample to live duty.

### R9-N5e-F9 — SOLID · SR-06 and SR-09 settled: both NON-equivalent, both survive
`scripts/proof-runner:194-197`. Differentials pasted in §3. "Equivalent under use" holds only while every spec's `failure_reason` carries no leading/trailing whitespace — nothing enforces that.
Fix/red test: a `pattern` on `failure_reason` in `proofs/schemas/spec.schema.json` forbidding leading/trailing whitespace, plus `test_runner_records_the_raw_line_not_the_stripped_line` (checker prints a padded line; assert `observed_failure_reason` keeps the padding — kills SR-09) and a spec whose expected reason begins with a space (kills SR-06).

### R9-N5e-F10 — SOLID · the report's `file:line` refs are stale (recurrence of R8-N5d-F6)
Re-derived at HEAD: `test_probe_stderr_heavy_no_deadlock` "line 344" → `:342`; `test_probe_identity_fields_all_pinned` "line 895" → `:911`; `test_make_capture_dir_keys_match_live_producer` "line 688" → `:681`; `negative_contract.py:162` → `:163/:164`; `_FAKE_AGENT` "364-372 / line 372" → `:370-379`, the added line is `:378`; F5 "258-259 / 284 / 644-647" → `:257` / (removed) / `:651-654`.

### R9-N5e-F11 — SOLID · the lane's no-op control ran a 109-test subset, not its 241-test bar
Collected counts on my copy: acp_probe 44 + check_initialize 53 + spec_runner 12 = **109** (the three touched files); negative_contract 51 + nostr_verify 82 → 242 total. The report's mutant table control reads `109 passed`; the acceptance bar is the five-file suite. Every mutant above was graded by me against 242.

### R9-N5e-F12 — UNSURE (not reproduced on the PC — no bridge banner this session) · a third `realpath(sys.executable)` interpreter assertion added, in the family the ledger records RED on the PC
New: `tests/test_s0_01_acp_probe.py:457` (`test_probe_sigterm_killed_agent_exit_code`). Existing family: `:659` (`test_probe_interpreter_fields_pinned`), `:895` (`test_probe_identity_fields_all_pinned`) — the ledger names both as PC reds ("the fixture agent runs under the shebang interpreter `/usr/bin/python3.13`, the test expects `sys.executable`'s realpath"). Forward risk: the PC red set grows from 2 to 3. Fix: compare against the shebang interpreter resolved at fixture-write time, not the runner's `sys.executable`.

### R9-N5e-F13 — SOLID · docstrings/comments the diff touched vs the code
`acp_probe.py:196-199` — "fall back to the last good reading" (dead, F2) and "deterministic for any child that lives long enough" (falsified, F1). `:189` — the deleted "not from `/proc/self/exe`" clause leaves the anti-self-sampling rule undocumented at the site the LG2 mutant attacks. `:79-82` `_write_evidence` — implies the evidence survives an M3 crash (F6). `tests/…:1028` — "Python startup outlasts the loop" is the wrong mechanism (the loop breaks on iteration 1 at ~0 ms; it runs 96–97 iterations only when readlink FAILS), and the test name still says `is_fail_loud`. `tests/…:449-451` — "samples while the agent still blocks on stdin"; the sample is taken immediately after `Popen`, before the agent reaches stdin. The three F5 comments themselves are correctly fixed.

## 4. Coordinator hunks F4/F9 — verified clean

* `_run_real_probe` with the stdin-blocking `_FAKE_AGENT`: **0.070–0.074 s** over 5 runs (`ACP_PROBE_TIMEOUT=20`, subprocess timeout 60) — the probe breaks on the `id==0` frame then closes stdin; no stall. Interpreter sampled `/usr/bin/python3.11` 5/5, `probe_error=None` 5/5.
* Live-producer test still asserts the exact venue reason: `NegativeFailure: agent_argv mismatch` **5/5 deterministic**.
* F9 red-green reproduced: `negative_contract.py` swapped to `aa477ca` → `1 failed, 1 passed` (`test_empty_probe_error_is_still_an_error`: DID NOT RAISE); HEAD → `2 passed`. Falsy carve-outs: none left (`0`/`[]`/`{}`/`false` all raise) — but see F7 for the message.

## 5. Real negative capture through `check_initialize.py`

Live capture (real probe + the pinned-error fake agent), 4 files, all 11 identity keys:
```
check_initialize.py request  -> failure_reason: negative: agent_argv mismatch      rc=1
check_initialize.py response -> error code=-32602 message=Invalid params            rc=1
validate_negative_dir        -> NegativeFailure: agent_argv mismatch
```
On a sandbox capture the sole failure ground is the venue pin `agent_argv mismatch`, NOT the probe sha — `negative_contract.py:175` re-derives `probe_sha256` from the LIVE file, so it matches by construction. **The probe changed again: new sha `28819d9011f908c0cc98e02752333997ed9963a3f65c45f0a2ed0456bc4211bf`.** Any PC capture taken before this commit now fails `probe_sha256 mismatch` (checked at `:175`, ahead of the agent pins at `:181`), so the PC re-capture must be re-taken with exactly this probe.

## 6. Hygiene

Exact-reason discipline in `tests/test_s0_01_acp_probe.py`: 23 `==` reason assertions; the inexact ones are `:1043` (`"BrokenPipeError" in …`), `:1239` (`"No such file or directory" in …` → F3), `:1283` (`.startswith("FileNotFoundError")`). `tmp_path`: `git status --porcelain` on my copy **empty before and after** every run. Scope files sha-identical to the `57a7df6` blobs at the end.

```
pytest-summary: 242 passed in 48.94s
pytest-summary: 242 passed in 49.01s
pyflakes rc=0        (acp_probe.py, test_s0_01_acp_probe.py, test_s0_01_check_initialize.py,
                      test_s0_01_spec_runner.py, negative_contract.py, test_s0_01_negative_contract.py)
```

## 7. Attempt-1 bookkeeping

Kept, verified present in the tree: `_write_evidence` (structure, one whitespace diff in the docstring); the post-loop F3 split; the evidence-writes removal; `test_probe_self_deleting_script_…` (assertions byte-identical, docstring trimmed — the dropped clause was "NOT a DEFERRED-classifiable bare dir", which F6 shows would have been false anyway); `_register_runner_proof` **verbatim**; both runner tests (quote style + docstring wording only); F5 comments; F10/F11 assertions; the check_initialize F4 change. Modified as claimed: the determinism test (rc dropped from the tuple — attempt-1's docstring says "(rc, interpreter-nullness, exit-code) triple"); the agent-exits-without-output update.
Rejected and correctly ABSENT from the tree: `test_probe_interpreter_sample_reason_is_truthful`, `test_probe_never_sampled_surfaces_oserror`, `_exec_window_end`, `_self_exe`.
**Something that should have been kept:** attempt-1's `assert rid["probe_error"].startswith("interpreter sample failed: ")` (inside the rejected truthful-reason test). The rejection rationale (wrong sample path for N8) is sound, but the prefix assertion was dropped **without replacement** — that is exactly the hole mutant F3PREFIX walks through (R9-N5e-F3). The exact-string assertion from the other rejected test is already covered by `test_probe_interpreter_sample_failure_after_child_exit`, so nothing was lost there.

## What I reproduced vs reviewed statically vs skipped

**Reproduced (ran it):** 14 agent shapes + BP1/BP2 + the wrapper and env-shebang shapes, both on HEAD and on the parent commit; 40× loaded/unloaded fast-exit and dash batteries; the retry-loop bound (attempts + wall clock); the interpreter sha256 cost; 12 probe mutants + 2 reachability instruments + 7 runner mutants, each against the full 242-test suite; two live runner differentials; the block-attribution instrument; the self-deleting capture through both checker modes; the live negative capture through both checker modes and `validate_negative_dir`; the F9 PRE/HEAD falsy differential and the committed F9 red-green; `_run_real_probe` timing ×5; the proposed F1 fix variant and attempt-1's guard variant; the suite twice; pyflakes; blob identity; attempt-1 function-level comparison.
**Reviewed statically only:** the downstream consequence of the rare shape-A rc=0 arm (`negative_contract.py:142` `no agent response captured`) — I could not capture that run again in 60 further attempts, so the rc=0 arm's downstream reason is inferred from the code, not executed.
**Deliberately skipped:** anything on the PC (no bridge banner this session) — so F12's PC-red prediction, the real `hermes-acp` agent's exec shape, and whether F1 changes the PC capture's recorded interpreter are NOT reproduced. F1's blocking status does **not** depend on the PC: it is proven on two sandbox agent classes with a paired pre/post control.

---

## VERDICT: **NOT-READY**

Blocking: **R9-N5e-F1** (wrong, silent, non-deterministic interpreter evidence for any multi-stage-exec agent — a regression against the parent commit, unreproduced on the PC but proven twice in the sandbox), **R9-N5e-F2** (the `_last_good` fallback is dead code claimed as built in the code comment, the commit message and the report), **R9-N5e-F3** (the F3 killer's substring assertion lets mutant F3PREFIX through), **R9-N5e-F5** (the commit message and ledger checkpoint 8f claim the fast-exit flips were fixed; rc still flips, measured worse — one-line correction), **R9-N5e-F6** (the M3 crash path writes a 1-key identity and no `env.json`; the checker reports `env.json absent` instead of the producer crash).

Non-blocking, reported: F4, F7, F8, F9, F10, F11, F12 (unsure, PC), F13.