# BRIEF — adversarial attacks on increment #1 (role: adversarial-verifier, route agentfactory-verify)
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

You did not watch the build. A sibling lane executes the contract items mechanically; YOUR job is
the judgment half: break the validator. honey: full — line-bounded findings, evidence anchors,
SOLID/UNSURE on every claim. Report EVERYTHING; the coordinator ranks. Append each finished
section to `$LANE_REPORT_DRAFT` as you go (this brief is sized for one context; do not expand it).

FIRST ACTION: `pwd && git rev-parse HEAD` equals the PIN, tree clean;
`$HOME/venv-agent-factory/bin/python -m pytest tests/ -q` fully green (44 passed).

## Under test
`scripts/validate-ledger`, `proofs/schemas/*.json`, `proofs/registry.yaml`, and whether
`tests/test_validate_ledger.py` + `tests/red/test_s0_01_adversarial.py` are gates or mirrors.
Prior rounds already fixed: host-python spawn, hardcoded rule id, alias validation, date-time
checker guard, unknown ledger id, three traceback paths, negative-leg code check.

## Boundary
Create RED tests under `tests/red/` only (deterministic, exact reason strings, each red for the
stated reason on this tree; a new file `tests/red/test_s0_01_round4.py`). No other edits, no
commits, no pushes, no subagents, no installs. Mutations run on SCRATCH COPIES (`cp -a` of the
tree into `$TMPDIR`), never `git restore`/`git stash` on the worktree.

## Attack set (all on scratch copies; paste command + output)
A1 Registry copy: `ledger_denominator` 0 / `true` / `"7"` → each an exact `registry-schema:` reason.
A2 Schema copy with `additionalProperties: false` removed from `result.schema.json` → the
   extra-key test MUST go red (a mutation the suite kills); same for `minContains` on `runs`
   (now also enforced in code — confirm the code path fires with the schema mutated).
A3 Result artifact whose digest is computed with `indent=2` / without `sort_keys` → `digest-mismatch`.
A4 Alias cycle `{"a": "b", "b": "a"}` and self-alias → a finding, never a hang or traceback.
A5 `blocked.json` for an execution_proof entry; both artifacts present; duplicate proof ids;
   a thirteenth entry; a `marker` that is a string (`"marker": "x"`) — finding or traceback?
A6 Timestamp asymmetry: `recorded_at` requires `Z$`, run legs accept any RFC3339 offset — gap or
   defect? (INFO or RED test with reason.)
A7 Mirror check: for each of the three round-2 fixes and the five round-3 fixes, revert it on a
   scratch copy and name the test that reds; any fix with no killer is a finding.
A8 Under-reporting: `_registry` skips other missing fields when `classification` is missing —
   demonstrate and decide (INFO or RED test).

## Spine read (`scripts/validate-ledger` in full)
Fail-open paths, trust placed in a hand-authored artifact, canonicalization mismatches, guards
that reject only part of an unusable class, exceptions swallowed, exit codes that collapse
distinct failures.

## Report (DATA)
Per attack A1–A8: outcome. Findings: id · SOLID/UNSURE · file:line · reproducing command ·
RED test path or INFO. Verdict: MERGE-READY / NOT-READY with the RED tests that must go green.
NOT-done.
