# BRIEF — increment #1 REPAIR `s0-01b-repair-spine-gaps`: make the coordinator's five RED tests green
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

You are the BUILD lane (Hermes on the PC, role code-implementer). This is contract-gate round 2
for increment #1 `s0-01-registry-schemas-validator`. The coordinator harvested your round-1 work,
read the validator's spine and shipped three gaps as RED tests (five test ids). Your work: make
them green WITHOUT editing the tests, touching ONLY `scripts/validate-ledger`. The tests ARE the
contract; read them before the validator. `.hermes.md` carries the project rules. honey: ultra.

FIRST ACTION (halt loud on any mismatch): `pwd && git rev-parse HEAD` equals the PIN, tree clean,
then reproduce the premise with the venv interpreter (the suite spawns the CLI under
`sys.executable`, never through the shebang — AF-AP-11):

    $HOME/venv-agent-factory/bin/python -c "import jsonschema; assert 'date-time' in jsonschema.FormatChecker().checkers"
    $HOME/venv-agent-factory/bin/python -m pytest tests/test_validate_ledger.py -q

Expected: exactly `5 failed, 22 passed`, the failures being
  test_allowed_transitions_come_only_from_the_registry
  test_registry_alias_and_branch_classes_must_be_canonical[alias-value-typo]
  test_registry_alias_and_branch_classes_must_be_canonical[alias-key-canonical]
  test_registry_alias_and_branch_classes_must_be_canonical[branch-class-typo]
  test_cli_fails_loud_when_the_date_time_checker_is_unavailable
Any other red, or the assert failing, is an environment premise problem — report it, do not
work around it (the coordinator installed `rfc3339-validator==0.1.4` into the PC venv on
2026-09-03; `harness-ports/bin/pc-setup.sh` now pins it).

## The three gaps (what the tests demand; exact strings live in the tests)
1. **AF-AP-13 — a registry fact hardcoded in the gate.** `_allowed_transitions` injects
   `map-rust-s006`'s positive transition in code (the `allowed.setdefault("map-rust-s006", …)`
   block with its comment). The committed `proofs/registry.yaml` now declares `rule_id` on every
   class-naming branch (rust/runsc/egress positives; see its COORDINATOR DECISION — RULE IDS line).
   Delete the block; every allowed transition comes from the registry's branches and nowhere else.
2. **AF-AP-14 — an unvalidated indirection table.** Both sides of the transition check resolve
   through `class_aliases`, so a typo in the table (or in a branch) makes them agree on a class
   that does not exist. In `_registry` (or a helper it calls, running whenever the mapping is a
   list), add findings — exact text per the parametrized test:
   - every alias VALUE must be canonical → `registry-schema: class_aliases <key>-><value> is not canonical`
   - no alias KEY may itself be canonical → `registry-schema: class_aliases key <key> is canonical`
   - every branch class (`from_class`, `to_class`, `class`) must resolve through the aliases to a
     canonical class → `registry-schema: <rule_id> <branch_name> <field> <value> is not canonical`
     (the test's instance: `registry-schema: map-rust-s006 negative_effect to_class blocked_capabilty is not canonical`)
   These go through the normal findings path (exit 1). Keep the alias resolution itself as is.
3. **AF-AP-12 — a schema `format` that never ran.** jsonschema registers the `date-time` checker
   only when `rfc3339-validator` imports; without it every `"format": "date-time"` keyword in the
   three schemas is silently unchecked. Before any validation, build ONE `FormatChecker` and if
   `"date-time"` is not among its checkers, write
   `validate-ledger: date-time format checker unavailable (pip install rfc3339-validator==0.1.4)`
   to stderr and exit 3 — never fall back to unchecked formats, never print a proof state first.
   Reuse that one checker in `_validate` (no second `FormatChecker()` construction — the
   edit-snapshot screen flags the bare call, AF-AP-12).

## Constraints (deviation = STOP and report; never self-accept)
- Touch ONLY `scripts/validate-ledger`. No edit to any test, schema, registry, setup or doc
  file. Report adjacent defects (file:line, one line each); never fix them.
- No stubs, no swallowed exceptions, no new dependencies, no subagents, no outward actions (no
  push, PR, comment), no `git` beyond committing in your worktree. Commit message = reasoning
  record (what each change fixes, the rejected alternative, the literal test invocation + counts).
- The existing suites are part of your final gate: the FULL `tests/` tree must report
  `39 passed` with `$HOME/venv-agent-factory/bin/python -m pytest tests/ -q`, run TWICE, both
  summaries verbatim in the report and the commit body. `test_committed_pc_bridge_spike_validates_and_declares_all_effects`
  and `test_cli_does_not_require_undeclared_yaml_dependency` staying green is the proof that the
  rule-id and checker changes did not widen.
- Determinism: `scripts/validate-ledger integrity` on the repo root twice → byte-identical stdout.

## Report (DATA, ≤ 60 lines, no narrative)
files:lines changed · the literal pytest invocations ×2 with their summaries · per red test:
the assertion line before → green after · the exit-3 stderr line verbatim · discrepancies ·
NOT-done · adjacent defects (file:line).
