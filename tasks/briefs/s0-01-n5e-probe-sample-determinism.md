# BRIEF — S0-01 lane N5e: the probe's interpreter sample is deterministic and truthfully attributed, its placement is pinned, the evidence writes sit inside the M3 handler (VERIFY-N5d, round 8)
PIN: (set at dispatch)

You are the BUILD lane (Hermes on the PC, model ollama-cloud/kimi-k3, role code-implementer). honey: ultra. `.hermes.md` carries the
project rules. Your output is a PROPOSAL graded by the sandbox adversarial verifier; never self-accept. This brief is SELF-CONTAINED
(the verdict file is not in the tree at your PIN). Interpreter: `$HOME/venv-agent-factory/bin/python`. Write `report-draft.md` in your
lane dir as you go. Long runs in ONE foreground call.

FIRST ACTION (halt loud on any mismatch): `git rev-parse HEAD` equals the PIN; `git log --oneline -6` contains a commit whose subject
starts `S0-01 WIP checkpoint 8b:` (lane N5d — the code you are hardening); tree clean;
`$HOME/venv-agent-factory/bin/python -m pytest tests/test_s0_01_acp_probe.py tests/test_s0_01_check_initialize.py tests/test_s0_01_spec_runner.py tests/test_s0_01_negative_contract.py tests/test_s0_01_nostr_verify.py -q -p no:cacheprovider`
→ `234 passed`. Then reproduce R8-N5d-F3 before touching code: an agent whose shebang is a hardlink of `/bin/dash` that unlinks its own
interpreter at start, closes stdout and sleeps 3 s → today the probe writes `probe_error = "interpreter sample failed: agent exited
before its first a2c byte"` although `agent_exit_code` is 0 and `agent_interpreter_realpath` ends in ` (deleted)` — paste it.

## The verdict you are closing (VERIFY-N5d) — all four round-7 blockers are CLOSED; these are the residue
BLOCKING:
- F2: the post-loop sample block in `proofs/S0-01/tools/acp_probe.py` (~:258-265) sits inside `if c2a_delivered:`; dedenting it one level
  survives the whole suite while changing the evidence (on a BrokenPipe capture the interpreter fields become non-null). Pin the placement:
  in `tests/test_s0_01_acp_probe.py::test_probe_broken_pipe_deterministic` assert `rid["agent_interpreter_realpath"] is None and
  rid["agent_interpreter_sha256"] is None` (red on the dedented copy, green on HEAD).
- F3: that block catches `(OSError, IOError)` around BOTH `os.readlink` and `_sha256_file` but always writes the fixed string
  `interpreter sample failed: agent exited before its first a2c byte`. Rule: `except (OSError, IOError) as exc:` — the fixed wording only
  when `interp_realpath is None` (nothing was ever sampled); otherwise `f"interpreter sample failed: {exc}"`. Red test: the self-unlinking
  agent above → `probe_error == "interpreter sample failed: [Errno 2] No such file or directory: '<path>'"` (compute the path).
- F5: three stale comments the N5d diff falsified — `tests/test_s0_01_acp_probe.py` ~:259 and ~:285 ("V2: interpreter fields must NOT be
  null (sampled before proc.wait)" — those assertions were deleted) and ~:645-647 ("uses `#!/usr/bin/env python3`" — the fixtures now use
  `#!{sys.executable}`). Fix the words.
NON-BLOCKING, ship them:
- F1: the fail-loud is race-decided for an agent that exits between its first stdout byte and the sample (`sys.stdout.write('x'); os._exit(0)`
  → rc flips 70 %/43 %/0 % across load shapes). Rule: sample right after `Popen` in a bounded retry loop (≤ 200 ms; retry while
  `/proc/<pid>/exe` still resolves to the probe's own interpreter or raises), the first success is authoritative, the in-loop and
  post-loop samples stay as the fallback, and "never sampled" stays a loud `probe_error`. Red test: `test_probe_fast_exit_agent_is_deterministic`
  runs that agent 20× in-test and asserts the (rc, interpreter-is-null) pair is constant. Prove the old mutant AP-F1a ("sample once at
  Popen, too early") stays killed — the retry loop must not make it equivalent.
- F4: two other fixtures still run the real probe with a non-stdin-blocking agent and assert rc 0: `tests/test_s0_01_check_initialize.py`
  ~:689 (`test_make_capture_dir_keys_match_live_producer`, still `#!/usr/bin/env python3`) — give it `#!{sys.executable}` and a trailing
  `sys.stdin.read()`. (`tests/test_s0_01_negative_contract.py` is READ-ONLY for you: report the same change for the coordinator.)
- F8: the identity/env/timeline writes (~:303-333) sit OUTSIDE the M3 `except Exception` handler (~:287): an agent that unlinks its own
  script file makes `_sha256_file(agent_realpath)` raise, the probe dies with an uncaught traceback, the capture dir holds only
  `agent-stderr.txt`, and `check_initialize.py request` classifies it DEFERRED (rc 2) — a producer crash reads as "venue cannot run the
  leg". Rule: the evidence writes move inside the wrapped body (or the handler wraps them) so a crash there is `probe_error` + rc 1 with
  `runtime-identity.json` written. Red test: the self-deleting agent → rc 1, `"Traceback" not in stderr`, `rid["probe_error"].startswith("FileNotFoundError")`.
- F10: `test_probe_sigterm_killed_agent_exit_code` now drives an exit-1 probe run — assert `r.returncode == 1` and the exact `probe_error`.
- F11: `tests/test_s0_01_acp_probe.py` ~:344 `st_size >= 200000` → `== 204800`; ~:888 `redacted_seen >= 1` → the exact count.
- F7 (runner, READ-ONLY file `scripts/proof-runner` — tests only): add `test_runner_reason_match_is_case_sensitive` (checker prints the
  reason upper-cased, expected lower-case → rc != 0 and the exact `negative-control-unmet: S0-9x` line) and
  `test_runner_records_the_first_matching_line` (two lines both containing the reason → `observed_failure_reason` is the FIRST) in
  `tests/test_s0_01_spec_runner.py`; report SR-06/SR-09 (strip variants) as equivalent or not with a live differential.

## Boundary (touch ONLY): `proofs/S0-01/tools/acp_probe.py`, `tests/test_s0_01_acp_probe.py`, `tests/test_s0_01_check_initialize.py`,
`tests/test_s0_01_spec_runner.py`. READ-ONLY: `scripts/proof-runner`, `proofs/S0-01/negative_contract.py`, `proofs/S0-01/pins.py`,
`tests/test_s0_01_negative_contract.py`, `proofs/S0-01/check_initialize.py`.

## Acceptance bar
Mutants (build each on a scratch copy, paste killed/total): N8 (post-loop block dedented), the F3 reason mutant (fixed string kept),
AP-F1a (sample once at Popen), G2 (re-introduce `if proc.poll() is None:`), and a no-op control — every non-equivalent one killed by a
NAMED test; the fast-exit determinism test 20/20 constant; the five-file suite TWICE (`-q -p no:cacheprovider`, paste both summary
lines); pyflakes rc 0 on the four files. Report fields: done (finding → test → red before / green after), not_done → reason, files,
summaries, discrepancies, adjacent defects (report only), the proposed `tests/test_s0_01_negative_contract.py` hunk (F4).
Standing rules: no subagents; no outward-facing actions; never `git stash`/reset the worktree; tests write only under tmp_path.
Authorization context: defensive verification tooling on the owner's own pinned ACP agent; no credentials are involved.
