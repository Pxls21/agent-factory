# BRIEF — adversarial verification of increment #1 `s0-01-registry-schemas-validator` (role: adversarial-verifier)
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

You did not watch the build. Grade the increment against the CONTRACT, never against the
builder's own tests. `.hermes.md` carries the project rules. honey: full — line-bounded findings,
evidence anchors, SOLID/UNSURE on every claim. Report EVERYTHING; the coordinator ranks.

FIRST ACTION: `pwd && git rev-parse HEAD` equals the PIN, tree clean; the venv interpreter is
`$HOME/venv-agent-factory/bin/python` (the suite spawns the CLI under `sys.executable`; the
`date-time` checker must be registered: `python -c "import jsonschema; assert 'date-time' in jsonschema.FormatChecker().checkers"`).

## The increment under test (applied in the working tree at the PIN)
`proofs/registry.yaml` · `proofs/schemas/{result,blocked,spike}.schema.json` ·
`scripts/validate-ledger` · `tests/test_validate_ledger.py` · `spikes/pc-bridge/result.json`
(migrated) · the `rfc3339-validator==0.1.4` / `jsonschema==4.25.1` pins in `scripts/setup.sh` and
`harness-ports/bin/pc-setup.sh`. Its commits: `git log --oneline c39b64f..HEAD -- proofs scripts/validate-ledger tests/test_validate_ledger.py spikes/pc-bridge/result.json`.
Round history: round 1 built it (PC lane); the coordinator's harvest fixed the harness (AF-AP-11)
and shipped five RED contract tests; round 2 (repair lane) made them green. You grade the SUM.

## Contract
Items C1–C12 in `tasks/briefs/s0-01-registry-schemas-validator.md` §Contract (read them there;
C11's interpreter is the venv python; C12 = the hooks under `core.hooksPath` pass on commit).
Round-2 additions:
C13 The full `tests/` tree passes with `$HOME/venv-agent-factory/bin/python -m pytest tests/ -q`,
    twice; every test in `tests/test_validate_ledger.py` named for AF-AP-12/13/14 is green.
C14 With `rfc3339_validator` un-importable (a `sitecustomize.py` import blocker on PYTHONPATH),
    the CLI writes `validate-ledger: date-time format checker unavailable (pip install rfc3339-validator==0.1.4)`
    to stderr and exits 3 before printing any proof state; with it importable, a run leg whose
    `started_at` is `yesterday` yields `registry-schema: S0-01 result: runs.0.started_at: 'yesterday' is not a 'date-time'`.
C15 A `class_aliases` value outside the canonical four, a key inside it, or a mapping branch
    class that does not resolve to a canonical class each produce their exact `registry-schema:`
    finding (strings in the tests) and exit 1.
C16 No rule id or proof id is hardcoded in `scripts/validate-ledger` outside the canonical
    constants: `grep -n "map-\|S0-0\|S0-1" scripts/validate-ledger` shows only the proof-id
    regex and the S0-03 credential-rejection clause the breakdown specifies.

## Boundary
You may create RED tests under `tests/red/` only (deterministic, exact reason strings, each
red for the stated reason on this tree). No other edits, no commits, no pushes, no subagents,
no installs, no sudo. Mutations run on SCRATCH COPIES of the tree (`cp -a` to `$TMPDIR`), never
`git restore`/`git stash` on the worktree.

## Minimum attack set (on scratch copies; paste command + output for each)
A1 Registry copy: `ledger_denominator` 0, `true`, `"7"` → each the exact `registry-schema:` reason.
A2 Schema copy with `additionalProperties: false` removed from `result.schema.json` → the
   extra-key test MUST go red (a mutation the suite kills); same for `minContains` on `runs`.
A3 Result artifact whose `runs` lacks the negative leg; whose digest is computed with
   `indent=2` or without `sort_keys` (canonicalization mismatch) → `digest-mismatch`.
A4 Alias cycle `{"a": "b", "b": "a"}` and self-alias `{"blocked_capability": "blocked_capability"}`
   → a finding, never a hang or traceback.
A5 `blocked.json` for an execution_proof entry; both `result.json` and `blocked.json` present;
   duplicate proof ids in a registry copy; a thirteenth entry.
A6 `--ledger` claiming a proof id the registry does not know (`S0-99 ABSENT`) — report what
   happens and whether silence there is a fail-open (INFO or RED test, your call with reason).
A7 Validator copy with the exit-3 guard removed → `test_cli_fails_loud_when_the_date_time_checker_is_unavailable`
   MUST red; copy with the alias check removed → the three alias tests MUST red (kills).
A8 Timestamp consistency: `recorded_at` requires `Z$` while run legs accept any RFC3339 offset —
   state whether that asymmetry is a contract gap (INFO) or a defect.
A9 Non-dict `marker` in a blocked artifact (`"marker": "x"`) → finding or traceback? A traceback
   is fail-closed but report it.

## Spine read (`scripts/validate-ledger`, the three schemas, `proofs/registry.yaml`)
Fail-open paths, config read from the environment, trust placed in a hand-authored artifact,
canonicalization mismatches, guards that reject only part of an unusable class, tests that
mirror the code's own assumption instead of the contract, findings under-reported when two
defects coincide (e.g. `_registry` skips other missing fields when `classification` is missing).

## Report (DATA)
Per item C1–C16: PASS/FAIL + the literal command + output lines. Per attack A1–A9: outcome.
Findings: id · SOLID/UNSURE · file:line · reproducing command · RED test path under `tests/red/`
or INFO. Verdict: MERGE-READY / NOT-READY with the RED tests that must go green. NOT-done.
