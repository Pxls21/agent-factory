# BRIEF — S0-01 lane N5g: every interpreter-sample site is pinned (the kept early reading, the self-sampling early site, the once-only late sample), the schema pattern closes its trailing-newline hole, the identity key set comes from pins (VERIFY-N5f, round 9)
PIN: (set at dispatch)

You are the sandbox BUILD lane (Opus 4.6 `code-implementer`). honey: ultra. Your output is a PROPOSAL graded by VERIFY-N5g; never
self-accept. Interpreter `python3` (= `/root/venv-agent-factory/bin/python`). Edit the shared tree IN PLACE — no worktree, no branch, no
commits, no git state changes (never `git stash`/`checkout`/`restore`/`reset`). The tree is CLEAN at dispatch; verifiers read archive
copies. Long runs in ONE foreground call; no xdist; `--basetemp` under …/scratchpad/ln5g/ per run, deleted after; `df -h /` before the
first suite. Report to …/scratchpad/wf-results-r5/N5g.md (draft N5g-draft.md as you go).

FIRST ACTION (halt loud on mismatch): `git rev-parse HEAD` equals the PIN; `git status --porcelain --untracked-files=no` is empty;
`bash scripts/test_summary.sh tests/test_s0_01_acp_probe.py tests/test_s0_01_check_initialize.py tests/test_s0_01_spec_runner.py tests/test_s0_01_negative_contract.py tests/test_s0_01_nostr_verify.py`
→ `252 passed`; `bash scripts/test_summary.sh tests/test_spec_probe_schemas.py tests/test_proof_runner.py` → `31 passed`;
`python3 scripts/validate-ledger integrity --root .` → PRESENT ×4 (S0-09/S0-10/S0-11/S0-12). Then reproduce the two blockers BEFORE
touching code and paste them: (a) mutant LATE-NULL on a scratch copy of `proofs/S0-01/tools/acp_probe.py` (in the late
`except (OSError, IOError)` arm set `interp_realpath = None; interp_sha256 = None; probe_error = f"interpreter sample failed: {exc}"`)
→ the five-file suite stays `252 passed`; (b) mutant LG2-EARLY (the early loop reads `/proc/self/exe`) → `252 passed`, and a
`#!/bin/bash` agent that reads one line and never writes stdout records `/usr/bin/python3.11` (the probe's own interpreter) 6/6.

## The verdict you are closing — `tasks/briefs/s0-01-n5g-support/verify-N5f.md` (read it whole; the rulings below are binding)
BLOCKING:
- F1 the kept early reading: add `test_probe_late_readlink_failure_keeps_the_early_reading` — in-process (the wrapper pattern of the F3
  test), `os.readlink` patched with a call counter: `/proc/*/exe` succeeds on call 1 (the early loop) and raises `OSError` from call 2
  on (the late sample); agent = the answering fixture. Assert `rid["agent_interpreter_realpath"] == os.path.realpath(sys.executable)`,
  `rid["agent_interpreter_sha256"] is not None`, `"probe_error" not in rid`, `r.returncode == 0`. Red on LATE-NULL (measured: rc 1,
  interp None, `interpreter sample failed: No such process`), green on HEAD. One comment line at the arm: "keeps the early reading —
  a wrong early reading fails the pinned interpreter checks downstream; pinned by <test name>".
- F2 the early site's self-sampling: add `test_probe_interpreter_is_child_not_self_for_a_silent_agent` — a `#!/bin/bash` agent
  (`read line; sleep 3`, no stdout), `ACP_PROBE_TIMEOUT=2`; assert `rid["agent_interpreter_realpath"] != os.readlink(f"/proc/{os.getpid()}/exe")`
  and `os.path.basename(rid["agent_interpreter_realpath"]) == "bash"`. Red on LG2-EARLY, green on HEAD.
NON-BLOCKING, ship them:
- F3 the bound is a ratio: in the fake-clock test also assert `acp_probe._EARLY_SAMPLE_DEADLINE_S == 0.2`, `acp_probe._EARLY_SAMPLE_STEP_S
  == 0.002` and the fake clock's final value (`200_000` µs) — mutant DL_SCALE (both doubled) must die.
- F4 the multiline runner test: keep it (it is the sole killer of SR-03 `expected in whole_text`), rename it
  `test_runner_per_line_rule_holds_for_a_multiline_expected_reason` with a docstring saying the schema forbids a multiline reason in
  production and the pattern is lifted from the schema copy only so the reason can reach the matcher; add `("a\nb", "multiline")` and
  `("foo\n", "trailing-newline")` to the schema-rejection parametrize in `tests/test_spec_probe_schemas.py` (rename it
  `test_spec_failure_reason_rejects_edge_whitespace_and_newlines`).
- F5 the pattern accepts `"foo\n"` (Python `re` lets `$` match before a final newline): change `failure_reason`'s pattern to
  `"^\\S(.*\\S)?(?![\\s\\S])"` — a true end-of-string anchor under Python `re` AND ECMA-262 — and prove the nine hostile strings of the
  verdict's F5 table (`foo\n` now rejected; `a\nb`, `\nfoo`, `foo\t`, `foo `, ` foo`, `foo\r`, `foo\xa0`, `foo\n\n` rejected; the 7
  committed spec-leg values accepted). ATTESTED INPUT (AF-AP-56, CLAUDE.md): after the schema edit regenerate the four minted artifacts
  (`python3 scripts/proof-runner run --proof S0-09 --venue sandbox --root .` and S0-10, S0-11, S0-12), then `python3 scripts/validate-ledger
  integrity --root .` → PRESENT ×4, then `python3 scripts/ledger-gen --root .` TWICE → byte-identical; paste all three. The regenerated
  `proofs/S0-*/result.json` + `proofs/ledger.json` are part of your deliverable (generated, never hand-edited).
- F6 once-only late sample: pin the rule — `test_probe_interpreter_is_sampled_once_at_the_first_a2c_byte` (patch `os.readlink` to return a
  distinct sentinel from call 3 on; assert the recorded value is the call-2 value); mutant LATE-EVERY (re-sample on every chunk) must
  die; one comment line at the once-gate: "sampled once, at the first a2c byte: the stage that wrote the first protocol byte is the
  interpreter of record; an agent that execs later is recorded as the stage that spoke first".
- F7 the `startswith("interpreter sample failed: ")` clear-guard is unreachable by construction (the only other writer, the BrokenPipe
  arm, sets `c2a_delivered = False` and skips the block): state that in the comment; no test; do not count LATE-CLEARALL as a kill.
- F8 shape N changed behaviour with no test: add `test_probe_interpreter_deleted_after_start_is_a_loud_probe_error` — an agent whose
  shebang interpreter (a hardlink of `/bin/dash`) is unlinked at start, then it closes stdout and sleeps; assert rc 1,
  `rid["agent_interpreter_realpath"].endswith(" (deleted)")`, `rid["agent_interpreter_sha256"] is None`, and
  `rid["probe_error"] == f"interpreter sample failed: [Errno 2] No such file or directory: '{path} (deleted)'"`.
- F9 the identity key set: in the self-deleting and the M3 tests import `pins` (as `tests/test_s0_01_negative_contract.py` does) and
  assert `set(rid) - {"probe_error"} == set(pins.NEGATIVE_IDENTITY_KEYS)` instead of the two literal 11-key sets; mutant PINS-12KEY
  (a 12th key added to the pin on a scratch copy of pins.py — restore it from your copy, pins.py is READ-ONLY) must die.
- F13 the env-shebang test: capture each `subprocess.run` result, `assert r.returncode == 0, r.stderr` and `"probe_error" not in rid`
  per run; use the neighbours' minimal env (PATH/HOME), not `os.environ.copy()`.
- F14 drop the `time.monotonic() - _start < 0.3` conjunct from the LATE-NOCLEAR killer's injection gate — `_sha_call[0] == 1` alone is
  the deterministic gate; say so in its docstring.
- F15 the schema hunk's gate is `tests/test_spec_probe_schemas.py tests/test_proof_runner.py`: run schema mutants SCHEMA-NOPAT (pattern
  removed) and SCHEMA-TRAILNL (the old `$`-anchored pattern) against THAT suite — both must die there.
- F11 hygiene: every `file:line` in your report re-derived at your final tree; the count of committed reasons is "7 spec-leg values
  (20 reason-bearing strings, 9 distinct)" — never "14"; the round-9 parent measurement for the env shebang was 10/12 env + 2/12 python.
  The ledger/commit corrections for 8j are the coordinator's.
- F10/F12 are informational (the post-loop block is reached only under fault injection — say so in its comment; the attestation red was
  fixed at f1e1316/9987187).

## Boundary (touch ONLY): `proofs/S0-01/tools/acp_probe.py` (comments only unless a ruling above needs code — say which),
`tests/test_s0_01_acp_probe.py`, `tests/test_s0_01_spec_runner.py`, `tests/test_spec_probe_schemas.py`, `proofs/schemas/spec.schema.json`,
plus the REGENERATED `proofs/S0-09/result.json`, `proofs/S0-10/result.json`, `proofs/S0-11/result.json`, `proofs/S0-12/result.json`,
`proofs/ledger.json`. READ-ONLY: `proofs/S0-01/pins.py`, `scripts/proof-runner`, `scripts/validate-ledger`, `scripts/ledger-gen`,
`proofs/S0-01/negative_contract.py`, `tests/test_s0_01_negative_contract.py`, `proofs/S0-01/check_initialize.py`, everything else.
Mutants: copy your FINAL file to scratch, apply the mutation to the tree file, run the suite, restore from the scratch copy — never from
git. Tests write only under `tmp_path`.

## Acceptance bar
Mutants (paste killed/total with the killing test named): LATE-NULL, LG2-EARLY, DL_SCALE, LATE-EVERY, PINS-12KEY, SCHEMA-NOPAT and
SCHEMA-TRAILNL (schema suite), plus the round-9 kills re-run (EARLY-DEL, LATE-DEL, LATE-GATE, LATE-NOCLEAR, APF1A, POST-DEL, F3PREFIX,
DL_DOUBLE, EV_OUTSIDE, EV_SWALLOW, M3-NOENV, M3-1KEY, M3-NOTIMELINE, FC-BIND, LG2-LATE, LG2-POST, SR-05/07/08/09/10) — every
non-equivalent one killed by a NAMED test; LATE-CLEARALL stated equivalent-by-reachability. The five-file suite TWICE and the schema/runner
suite TWICE (`bash scripts/test_summary.sh …`, all four lines pasted); pyflakes rc 0 on every touched `.py`; the attestation chain
(integrity PRESENT ×4, ledger-gen ×2 byte-identical) pasted. Report fields: done (finding → test → red before / green after, with the red
output pasted), not_done → reason (an empty not_done beside an unmet item reopens the lane), files (with the final
`sha256sum proofs/S0-01/tools/acp_probe.py proofs/schemas/spec.schema.json`), summaries, the mutant table, discrepancies (halt and
report rather than improvise), adjacent defects (report only). Standing rules: no subagents; no outward-facing actions; no commits.
Authorization context: defensive verification tooling on the owner's own pinned ACP agent; no credentials are involved.
