Work is complete. Final report follows.

---

## C2 BUILD REPORT — REVIEW-PENDING

**STATUS: REVIEW-PENDING.** C2 is implemented and self-validated. This build lane cannot issue a gate verdict; independent adversarial verification and a real Hermes-lane test are the coordinator's, after landing.

### PREMISE (verified live)

- Blob/line identities matched the brief: lane-profile `145d8c40abcb`/209; test_lane_profile `02bc97314c56`/152; run-all `6c45009c3486`/78; verify_command `daf605f480a0`/351; test_verify_command `6af9a516adf5`/490.
- All three create targets were absent. Profile baseline before change: `lane profile: 9 passed, 0 failed`.
- C1 has three `VERIFY` patterns; accepted the six supplied pytest interpreter forms plus cargo/npm/make/ruff; rejected all project runner and pipefail-wrapper forms.
- The Hermes payload excerpts and the 109-command corpus are the coordinator's read-only measurements; I did not read `~/.hermes/`. Fixtures use the supplied shapes.
- `canny:39-50`: the selected predicate is "code changed since the last passing check".

### IMPLEMENTATION

- `gate:24-44` (`CODE_SUFFIXES`, `PROJECT_PATTERNS`, `PATCH_PATH`, `RC_WRAPPER`): closed code-suffix list, project check patterns, V4A path matcher, and the exact pipefail/tee wrapper grammar.
- `gate:54-58` (`ledger_file`): ledger names keyed by SHA-256 of the repository root (first 12 hex) plus the sanitized session id, under the OS temp directory — the `spool_file` scheme reimplemented, not imported.
- `gate:85-97` (`counts_as_check`): C1's three pattern strings plus the project patterns passed to `is_verify` (replaces the default list); a separate narrow recognizer handles the rc-wrapper idiom.
- `gate:110-179` (`_result_exit_code`, `record`): the recorder validates integer-not-bool exit codes, records not-passing reasons, expands V4A paths, keeps stdout empty, exit code always 0, one stderr line per error.
- `gate:207-292` (`_is_code`, `gate`): closed code-file rule (`*.md`/`*.txt`/`transcripts/` never count; extensionless `#!` counts), edit/check sequence-order comparison, terminal-only unknown-order rule, at most 5 paths named plus "and N more", `final_response` never echoed, directive bounded to 1,500 bytes.
- `profile:25-85` (`verify_lane`): verify accepts a clone with or without exactly the two done-gate hook entries and refuses any other hooks delta.
- `profile:89-277` (`create_lane`): switch OFF leaves `config.yaml` byte-identical to today's output (byte-compare regression test); switch ON appends the recorder after the existing post_tool_call entries and installs one pre_verify directive. Hook commands resolve from the helper's own repository root (main clone), never a lane tree (AF-AP-148).
- `gatetest:93-382`: deterministic LLM-free tests, all brief cases (a)–(l), negative controls failing for the exact expected reasons.
- `profiletest:155-240`: switch-OFF byte identity, switch-ON exact entries, verify refuses a third entry and a changed command.
- `runall:12-13`: registers the new Python test.

`scripts/verify_command.py` and `tests/test_verify_command.py` are untouched. Lanes run Hermes with `--accept-hooks` (premise excerpt `agent/shell_hooks.py:139-176` + `pc-lane.sh:463`), so no hook allowlist edit is needed. Forwarding `LANE_DONE_GATE` from `scripts/pc_lane.sh` is out of this lane (VERIFY-T94), per the brief.

### C1-CORPUS RECLASSIFICATION

C1 baseline on the supplied corpus: **0/109**. The closed project set accepts exactly **7** of the 12 representative command shapes (the reads are never checks on either side): `bash harness-ports/tests/<name>.sh`; `python3 harness-ports/tests/test_<name>.py`; `bash scripts/lane_gate.sh …`; `bash scripts/test_summary.sh …`; the exact pipefail/tee/rc wrapper (two corpus variants); the env-prefixed pytest form. Rejected: output-redirect+`rc=$?` capture (last-stage rc), `bash -n` (syntax check, not behavioral verification — a passed syntax check proves nothing about the changed code's behavior), `&&`-chained runs (first-command failure masks), `pytest | tail` without pipefail, reads and screens. **16 explicit near-miss shapes** are rejected; every accepted shape and every near-miss was run through `bash` with a failing stub (exit 1) and a passing stub in a scratch directory — all 16 accepted shapes exit non-zero with the failing stub and zero with the passing stub.

### GATES — verbatim counts, this session

- `python3 harness-ports/tests/test_lane_done_gate.py` (twice, identical): `lane done gate: 19 passed, 0 failed`
- `bash harness-ports/tests/test_lane_profile.sh` (twice, identical): `lane profile: 13 passed, 0 failed`
- `python -m pytest -q -p no:cacheprovider --basetemp ../scratch/bt tests/test_verify_command.py` (C1 untouched): `65 passed, 8 xfailed in 0.94s`
- lane_gate archive A: `RESULT: rev=4a381906c89f files=5 deleted=0 runs=1 tests=1b6f2517d707 identical=yes rc=0 summary="8 passed in 10.04s"` — archive B: same summary
- pyflakes (venv), `bash -n` on the three shell files, `git diff --check`: all clean
- `report_lint`: `report_lint: 16 refs — OK 16, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`; floor 12 satisfied.

### MUTANTS (`../scratch/mut/`, each on a scratch copy)

| Mutant | Died in | Reason red |
|---|---|---|
| Any pass anywhere silences (order ignored) | `test_order_and_gate` | b- and f-class facts |
| `passing` without exit-code test | `test_exit_codes_and_bad_result` | 1/missing/"0"/true accepted |
| `bool` as exit code | same | `true` accepted as passing |
| `.md` counts as code | `test_order_and_gate` | report edit nudges |
| Ledger keyed by repo only (sessions share) | `test_session_isolation` | sessions cross-talk |
| Recorder writes inside repo root | `test_session_isolation` | ledger under `git status` |
| lane-profile adds hooks with switch OFF | `test_lane_profile.sh` | byte-identity compare fails |
| Semantic guard not widened (extra key passes) | `test_lane_profile.sh` | third entry accepted |
| Accepted shape widened past its grade | `test_classifier_and_bash_grade` | near-miss accepted |

### DISCREPANCIES / NOT done

- Full `harness-ports/tests/run-all.sh` ends `1 SUITE(S) FAILED`, twice identically. Both C2 rows are green (`lane done gate: 19 passed, 0 failed`; `lane profile: 13 passed, 0 failed`); the failure is the read-only qwen matrix suite at `18 passed, 1 failed` both times on this tree. I cannot touch that suite (read-only boundary), and the pinned `tests/test_verify_command.py` invocation alone passes (`65 passed, 8 xfailed`), so it is not a C1 regression. Reported, not chased.
- `lane_gate.sh` cannot combine the Python script and shell script as test targets through `test_summary.sh` (`no match in any of [<Dir tests>]`); the archive gate ran the Python suite twice and the shell suite ran directly twice.
- Ripwire `edit-check` takes a symbol, not file paths; the initial file-form call failed and was rerun symbol-qualified, successfully.
- Real-lane live check: NOT done (the coordinator's, after landing; the brief forbids running `hermes` here).

### SELF-ATTACK — the three most likely ways this is wrong

1. **A lane-running command shape I didn't witness gets rejected** (closed set is under-inclusive). Ruled out for the witness set: the corpus shapes all reclassify as measured (classifier table asserted in the test). A new shape would nudge falsely — mitigated by design: the recorder records the check as not-passing with its reason in the ledger, and the fix is adding one graded pattern. Flagged as a known closed-set property, not hidden.
2. **The `cwd` from the hook payload redirects the ledger.** Ruled by construction: `_repo_root` returns the module's trusted `ROOT.resolve()` and ignores event `cwd`; the session-isolation test fires a foreign-`cwd` probe and asserts both ledgers unchanged in content and location.
3. **A wrapper silently masks the real check's status and the gate goes quiet.** Ruled by the bash grade: every accepted wrapper form exits non-zero under a failing stub (16/16 asserted in-tree), and near-misses (`; true`, `|| true`, `&`, missing pipefail, wrong index, `exit 0`) are all rejected.

### REASONING RECORD (for the coordinator's commit message)

- Decoupled `LANE_DONE_GATE` (create-time switch) from `verify` (accepts either exact form): otherwise a valid gate-enabled lane profile would fail verification when the verifying shell has the switch off.
- Closed classifier, not substring: C1's patterns use `search`, so `bash harness-ports/tests/test_pc_lane.sh && true` would be accepted by pattern alone; `_is_direct_check` requires the complete command shape.
- Ledger root is the module's trusted location, never hook-supplied `cwd` (hook input is not a trust anchor).
- `bash -n` rejected by decision: a syntax check is not behavioral verification.
- Terminal-only edits: unknown order after a passing check produces one stderr naming line, not a nudge — a nudge with unknown order would be the hollow-red counterpart of the hollow green this lane removes.
- Report sha (before harvest): `dea78df86cc2889d6c614382e6a5cb15748c10ba10be26e317ddbb7354f700b3` (`tasks/briefs/canny/C2-report.md`).

### FILES

- CREATE `harness-ports/bin/lane-done-gate.py` (314 lines)
- CREATE `harness-ports/tests/test_lane_done_gate.py` (404)
- CREATE `tasks/briefs/canny/C2-report.md`
- MODIFY `harness-ports/bin/lane-profile.sh` (298)
- MODIFY `harness-ports/tests/test_lane_profile.sh` (241)
- MODIFY `harness-ports/tests/run-all.sh` (78)

Retro: one reusable lesson — a closed acceptance set for gate-recognized commands must be graded by execution (failing stub / passing stub through real bash), not by pattern look; patterns using `search` accept compound commands that mask status. This lesson belongs in the `anti-hollow-green` tactic index (tactic 1, negative control on every gate); the coordinator may want a one-line ADD there, since I do not edit skills mid-lane.
