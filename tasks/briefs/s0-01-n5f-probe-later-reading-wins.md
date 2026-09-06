# BRIEF — S0-01 lane N5f: the probe records the interpreter that RUNS the agent (the later reading wins), the dead fallback goes, the crash path writes a complete evidence set, the reason strings are pinned exactly (VERIFY-N5e, round 9)
PIN: 220ffde407a5a7ba3c4326a480442d2a1dedcff6

You are the sandbox BUILD lane (Opus 4.6 `code-implementer`; codex is out and Kimi K3 is cooling down). honey: ultra. `CLAUDE.md` carries
the project rules. Your output is a PROPOSAL graded by the sandbox adversarial verifier; never self-accept. Interpreter: `python3`
(= `/root/venv-agent-factory/bin/python`). Edit the shared tree IN PLACE — no worktree, no branch, no commits, no git state changes of
any kind (never `git stash`/`checkout`/`restore`/`reset`). THE TREE IS DIRTY BY DESIGN: lanes D5f (`proofs/S0-01/tools/scripted_backend.py`,
`tests/test_s0_01_scripted_backend.py`, `tests/red/test_s0_01_backend_credential_screen.py`) and B5d (`proofs/S0-01/tools/frame_tee.py`,
`tests/test_s0_01_frame_tee.py`) are live in it and a verifier reads it — never touch those files. Long runs in ONE foreground call.
Scratch under `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ln5f/`; report to
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/wf-results-r5/N5f.md` (draft `N5f-draft.md` as you go).
4 shared cores with two other lanes and a verifier live: no xdist; `--basetemp` under your scratch per pytest run, deleted after;
`df -h /` pasted before the first suite; stop under 3 GB free and say so.

FIRST ACTION (halt loud on any mismatch): `git rev-parse HEAD` equals the PIN; `git status --porcelain --untracked-files=no` lists ONLY
the five D5f/B5d files above (your boundary files are clean at HEAD); `git log --oneline -4` contains a subject starting
`S0-01 WIP checkpoint 8f:` (lane N5e — the code you are repairing); then
`bash scripts/test_summary.sh tests/test_s0_01_acp_probe.py tests/test_s0_01_check_initialize.py tests/test_s0_01_spec_runner.py tests/test_s0_01_negative_contract.py tests/test_s0_01_nostr_verify.py`
→ `242 passed`. Then reproduce R9-N5e-F1 BEFORE touching code and paste it: an agent that is a `#!/bin/sh` wrapper doing `sleep 0.05`
then `exec "<sys.executable>" real_agent.py` (real_agent answers `initialize` and blocks on `sys.stdin.read()`) → today the probe records
`agent_interpreter_realpath` = the shell's realpath (`/usr/bin/dash` here), rc 0, no `probe_error`; and `#!/usr/bin/env python3` run 12×
→ a mix of `/usr/bin/env` and python readings.

## The verdict you are closing — `tasks/briefs/s0-01-n5f-support/verify-N5e.md` (read it whole first; the rulings below are binding)
BLOCKING:
- F1 + F8 + F2 (one change): `proofs/S0-01/tools/acp_probe.py` samples `/proc/<pid>/exe` right after `Popen` and accepts the first
  reading — for a multi-stage-exec agent that is an INTERMEDIATE stage (`/usr/bin/env`, the shell wrapper), wrong, silent and run-to-run
  variable; the in-loop sample at the first a2c byte (~:276) is gated by `_interp_sampled` and therefore dead for every real agent (F8);
  the `_last_good` arm (~:205-215) is unreachable (F2). RULING — "the later reading wins": (a) keep the early bounded loop exactly as
  the fallback for agents that exit before their first a2c byte, but DELETE the `_last_good` arm (the `except` arm becomes
  `candidate = None`); (b) at the FIRST a2c chunk ALWAYS re-read `/proc/<pid>/exe` (once — a `_late_sampled` flag, no `_interp_sampled`
  gate): on success overwrite `interp_realpath`, recompute `interp_sha256` (a sha failure there is `probe_error = f"interpreter sample
  failed: {exc}"` with the late realpath kept — the F3 test's `(deleted)` shape), and if `probe_error` starts with
  `interpreter sample failed: ` set it back to `None` (ONLY that class — never clear another error); on a readlink `OSError` keep the
  early reading silently when there is one (the child exited between its first byte and the readlink; a wrong early reading fails the
  pinned interpreter checks downstream, never a hollow green) and set the truthful `interpreter sample failed: {exc}` when there is
  none; (c) the post-loop block inside `if c2a_delivered:` (~:333-346) stays as the last fallback, unchanged. Red tests (RED on HEAD,
  paste the failures): `test_probe_interpreter_is_the_final_exec_not_a_wrapper` (the wrapper agent above → `rid["agent_interpreter_realpath"]
  == os.path.realpath(sys.executable)` and `rid["agent_interpreter_sha256"]` == the sha256 of that file, `"probe_error" not in rid`,
  rc 0) and `test_probe_env_shebang_interpreter_is_constant` (`#!/usr/bin/env python3`, 12 runs in-test → exactly one distinct
  `(realpath, sha256)` pair, equal to `os.path.realpath(shutil.which("python3"))` + its sha, and never `os.path.realpath("/usr/bin/env")`).
  Prove with mutants that each of the three sample sites has its own killer: EARLY-DEL (delete the post-Popen loop → the no-stdout
  shapes lose their identity), LATE-DEL / LATE-GATE (delete the late sample or re-introduce the `_interp_sampled` gate → the wrapper
  test), POST-DEL (the existing post-loop killers `test_probe_broken_pipe_post_loop_placement` / `…_truthful_error`), LATE-NOCLEAR (the
  early `interpreter sample failed:` error not cleared on late success → a test with `os.readlink` patched to fail for the early loop
  and succeed later: `"probe_error" not in rid`, rc 0), LATE-NULL (a late readlink failure nulls the early reading → shape D, 1 byte then
  `os._exit(0)`, 20× in-test: `agent_interpreter_realpath` non-null every run), APF1A (sample once at Popen, no retry → must stay
  killed). Delete-only mutant LG1 is now equivalent by construction (the arm is gone) — say so.
- F3: `tests/test_s0_01_acp_probe.py` ~:1239 asserts a substring. Rule: equality — `rid["probe_error"] ==
  "interpreter sample failed: [Errno 2] No such file or directory: '/tmp/fake_interp (deleted)'"` (build it from the fixture's path
  constant). Mutant F3PREFIX (`probe_error = f"{exc}"` in the sha arms) must die on this test.
- F5 (the words + the test name): `test_probe_agent_exits_without_output_is_fail_loud` (~:1025) no longer asserts fail-loud. Rename it
  `test_probe_agent_exits_without_output_keeps_interpreter_identity`; assert per arm exactly: `r.returncode in (0, 1)`; rc 1 ⇒
  `rid["probe_error"] == "BrokenPipeError: agent process exited before c2a write landed"` and `r.stderr.strip() == "acp_probe:
  BrokenPipeError: agent process exited before c2a write landed"`; rc 0 ⇒ `"probe_error" not in rid`; interpreter triple non-null in
  both arms. Docstring: "rc is race-decided (the c2a write lands before or after the exit); the interpreter triple is constant" —
  the OLD claim "Python startup outlasts the loop" is the wrong mechanism (the loop breaks on iteration 1; it runs ~100 iterations
  only when readlink FAILS). The commit/ledger wording is the coordinator's to correct — not yours.
- F6: the M3 crash path (~:378-392) writes a 1-key `runtime-identity.json` and no `env.json`; `_write_evidence` (~:78) raises at
  `_sha256_file(agent_realpath)` before writing anything, so a self-deleting agent yields a capture the checker reports as
  `env.json absent` — the producer crash is misattributed. RULING, two layers: (a) in `_write_evidence` guard the entrypoint hash:
  `except OSError as exc: agent_entrypoint_sha256 = None` and, if `probe_error is None`, `probe_error = f"{type(exc).__name__}: {exc}"`
  — the normal path for a self-deleting agent then writes all four files, all 11 pinned identity keys + `probe_error`, rc 1; (b) the
  M3 handler stays the last resort but writes the four files too: extract `_write_env(framedir)` from `_write_evidence` and reuse it,
  and build the identity with ALL 11 pinned keys (`pins.NEGATIVE_IDENTITY_KEYS` is the set; pre-initialise every field to `None`
  BEFORE the `try` so they are always in scope, fill what was reached) + `probe_error`. Red tests: (1) the self-deleting agent →
  the four files exist, the identity has the 11 keys + `probe_error == f"FileNotFoundError: [Errno 2] No such file or directory:
  '{agent_realpath}'"`, `agent_entrypoint_sha256 is None`, rc 1, `"Traceback" not in r.stderr`, and the REAL checker
  (`python3 proofs/S0-01/check_initialize.py request <capture>` exactly as `tests/test_s0_01_check_initialize.py` drives the live
  producer) prints `failure_reason: negative: probe reported an error: FileNotFoundError: …` (exact line) with rc 1 — never
  `env.json absent`; (2) the M3 path: in-process (`acp_probe.main()` under `unittest.mock.patch.object`, the pattern of the F3 test)
  with `_write_evidence` patched to raise `RuntimeError("boom")` → four files, 11 keys + `probe_error == "RuntimeError: boom"`, rc 1,
  `r.stderr.strip() == "acp_probe: RuntimeError: boom"`.
NON-BLOCKING, ship them:
- F4: the early loop's bound is unpinned (0.2 → 0.4 s survives). Rule: module constants `_EARLY_SAMPLE_DEADLINE_S = 0.2` and
  `_EARLY_SAMPLE_STEP_S = 0.002` consumed by the loop, and `test_probe_early_sample_loop_bound_is_pinned`: in-process with
  `acp_probe.time` replaced by a fake clock object (`monotonic`/`monotonic_ns` read an integer-microsecond counter that advances ONLY
  in `sleep`, which never waits) and `os.readlink` counting calls and always raising for the early loop → the attempt count is exact
  (`0.2/0.002 + 1 = 101`; assert `== 101`); a doubled deadline gives 201 → killed with no wall clock involved. Never a timing assertion
  on a contended box.
- F9 (runner — `scripts/proof-runner` is READ-ONLY; schema + tests only): add `"pattern": "^\\S(.*\\S)?$"` to `failure_reason` in
  `proofs/schemas/spec.schema.json` (keep `minLength`); in `tests/test_spec_probe_schemas.py` a leading-space and a trailing-space reason
  are each rejected (assert the validator's message names `failure_reason`); the 14 committed reasons carry no edge whitespace (checked
  2026-09-06) — run `tests/test_spec_probe_schemas.py tests/test_proof_runner.py` and `scripts/validate-ledger` if it validates specs.
  In `tests/test_s0_01_spec_runner.py` add `test_runner_records_the_raw_line_not_the_stripped_line` (checker prints a padded line;
  `observed_failure_reason` keeps the padding — kills SR-09, `line.strip()` recorded). SR-06 (`expected in line.strip()`) is EQUIVALENT
  once the schema forbids edge whitespace in `expected` (a substring with non-blank ends lies inside `line.strip()` iff inside `line`) —
  state that argument in the report instead of a killer; if you find a counter-example, add the killer.
- F12: the three `realpath(sys.executable)` assertions (~:457, ~:659, ~:895) — confirm in the report that each fixture's shebang is
  `#!{sys.executable}` (they are at HEAD); change nothing for F12; the PC leg is the coordinator's.
- F13: fix the words the verdict lists — `acp_probe.py` ~:196-199 (no "last good reading"; the determinism claim becomes "the reading
  at the first a2c byte is authoritative; the early loop covers agents that never write"), ~:189 restore the "never from
  `/proc/self/exe`" clause, `_write_evidence`'s docstring (the crash path now degrades, it no longer implies survival), the tests'
  ~:1028 and ~:449-451 docstrings ("samples right after Popen, before the agent reaches stdin"). No other prose edits.
- F10/F11 (report hygiene): every `file:line` in your report re-derived at your final tree; the no-op control and every mutant run
  are the FULL five-file suite, never a subset.

## Boundary (touch ONLY): `proofs/S0-01/tools/acp_probe.py`, `tests/test_s0_01_acp_probe.py`, `tests/test_s0_01_check_initialize.py`,
`tests/test_s0_01_spec_runner.py`, `proofs/schemas/spec.schema.json`, `tests/test_spec_probe_schemas.py`. READ-ONLY: `scripts/proof-runner`,
`proofs/S0-01/negative_contract.py` (F7 is the coordinator's hunk), `proofs/S0-01/pins.py`, `tests/test_s0_01_negative_contract.py`,
`proofs/S0-01/check_initialize.py`, and the five D5f/B5d files. Mutants: copy your FINAL boundary file to scratch, apply the mutation to
the tree file, run the full suite, restore from the scratch copy — never from git. Tests write only under `tmp_path`.

## Acceptance bar
Mutants (paste killed/total with the killing test named): EARLY-DEL, LATE-DEL, LATE-GATE, LATE-NOCLEAR, LATE-NULL, APF1A, F3PREFIX,
DL_DOUBLE (0.2 → 0.4), EV_OUTSIDE (`_write_evidence` outside the handler), EV_SWALLOW (handler swallows), M3-NOENV (handler skips
`env.json`), a no-op control — every non-equivalent one killed by a NAMED test. The wrapper and env-shebang tests 12/12 constant; shape D
20/20 non-null. The five-file suite TWICE (`bash scripts/test_summary.sh …`, paste both lines) + `tests/test_spec_probe_schemas.py
tests/test_proof_runner.py` once; pyflakes rc 0 on every touched `.py`. Report fields: done (finding → test → red before / green
after, with the red output pasted), not_done → reason (an empty not_done beside an unmet item reopens the lane), files (with the final
`sha256sum proofs/S0-01/tools/acp_probe.py`), summaries, the mutant table, discrepancies (anything the brief says that the tree
contradicts — halt and report rather than improvise), adjacent defects (report only). Standing rules: no subagents; no outward-facing
actions; no commits. Authorization context: defensive verification tooling on the owner's own pinned ACP agent; no credentials involved.
