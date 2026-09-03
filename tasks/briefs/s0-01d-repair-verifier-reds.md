# BRIEF — increment #1 REPAIR round 3 `s0-01d-repair-verifier-reds`: make the verifier's five RED tests green
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

You are the BUILD lane (Hermes on the PC, role code-implementer). Contract-gate round 3 for
increment #1: the adversarial verify lane shipped five findings as RED tests in
`tests/red/test_s0_01_adversarial.py`. Make them green WITHOUT editing any test, touching ONLY
`scripts/validate-ledger`. The tests ARE the contract; read them before the validator.
`.hermes.md` carries the project rules. honey: ultra.

FIRST ACTION (halt loud on any mismatch): `pwd && git rev-parse HEAD` equals the PIN, tree clean;
`$HOME/venv-agent-factory/bin/python -m pytest tests/ -q` reports exactly `5 failed, 39 passed`,
the five failures all in `tests/red/test_s0_01_adversarial.py`.

## The five findings (exact strings live in the tests)
1. A `--ledger` claim naming a proof id the registry does not know is silently ABSENT today →
   finding `registry-schema: ledger unknown proof_id <id>` (exit 1). Fail closed: an unknown id
   in the ledger is a defect, never a no-op.
2. `class_aliases` that is not an object → `registry-schema: class_aliases must be an object`
   (a finding on stdout, empty stderr — never a traceback).
3. `spike_to_class_mapping` that is not a list → `registry-schema: spike_to_class_mapping must be
   a list` (finding, not traceback).
4. A mapping rule whose branch is not an object →
   `registry-schema: <rule_id or spike> <branch_name> must be an object` — the test's instance is
   `registry-schema: map-rust-s006 negative_effect must be an object`; read how the test names
   the rule (the branch has no rule_id when it is not an object — derive the label the test
   expects from the test itself).
5. The negative-leg requirement must not live ONLY in the hand-authored schema file: with the
   schema's `minContains` for the negative leg mutated to 0, a result whose `runs` carry two
   positive legs must still be rejected with a finding containing `runs:` (e.g.
   `registry-schema: S0-01 result runs: missing negative leg`), exit 1. Enforce both legs in
   code; the schema stays the first line, the code the second.

## Constraints (deviation = STOP and report; never self-accept)
- Touch ONLY `scripts/validate-ledger`. No edit to any test, schema, registry, setup or doc file.
- No stubs, no swallowed exceptions, no new dependencies, no subagents, no outward actions.
- Every existing test stays green unchanged: the FULL suite must report `44 passed` with
  `$HOME/venv-agent-factory/bin/python -m pytest tests/ -q`, run TWICE, both summaries verbatim
  in the report and the commit body. `scripts/validate-ledger integrity` on the repo root twice →
  byte-identical stdout, exit 0.
- Kill-switch pass (report it): revert each of your five changes one at a time on a scratch copy
  and show its test go red; a change no test kills is not done.
- Append each finished section of your report to `$LANE_REPORT_DRAFT` as you go.

## Report (DATA, ≤ 50 lines)
files:lines changed · literal pytest invocations ×2 with summaries · per red test: assertion
before → green after · the five kill-switch results · discrepancies · NOT-done · adjacent defects.
