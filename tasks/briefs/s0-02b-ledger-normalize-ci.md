# BRIEF — increment #2b `s0-02b-ledger-normalize-ci`: ledger generator + normalization + CI split checks (half B of increment #2)
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

You are the BUILD lane (Hermes on the PC, role code-implementer). Half A (`scripts/proof-runner`,
the spec/probe schemas, the S0-03/S0-08 markers) has LANDED; read it as the consumer of your work.
honey: ultra. The parent brief `tasks/briefs/s0-02-runner-ledger-ci.md` BINDS for §COORDINATOR
DECISIONS D1–D6 (read that section once, by line range). `.hermes.md` carries the project rules.

FIRST ACTION: `pwd && git rev-parse HEAD` equals the PIN, tree clean, full suite green (count it).

## Deliverables (boundary — touch ONLY these paths)
- CREATE `scripts/ledger-gen` — `generate --venue … --root …` (re-run every blocked proof's probe
  via `scripts/proof-runner probe`, then render), `render --root …` (deterministic over the
  committed artifacts, no wall-clock field of its own), `--check --root …` (render to a temp dir,
  byte-compare with the committed pair, exit 1 with a unified diff on drift). Writes
  `proofs/ledger.json` (`proofs: [{proof_id, classification, state}]`, per-class
  `numerator`/`denominator` from the registry, `markers: [{proof_id, blocker_status, reason,
  probed_at, probe_venue}]` copied from the artifacts) and `proofs/LEDGER.md` (four-way table;
  the string `N/12` for any N must not appear). CREATE both outputs with `render` and commit them.
- CREATE `proofs/normalization.yaml` (JSON-syntax YAML like the registry — no PyYAML) + CREATE
  `scripts/normalize`: closed table of volatile-field rules (name, regex, replacement: RFC3339
  timestamps, pids, durations, session/thread ids, absolute temp paths, hostnames), applied
  line-wise, idempotent; `normalize <file>` prints the normalized text; `normalize --compare a b`
  exits 1 with `undeclared-volatile-field: <line>` when two runs differ on a line no rule covers.
- CREATE `.github/workflows/stage0-ledger.yml` — jobs `tests` (pip pins exactly as
  `scripts/setup.sh`), `ledger-integrity` (`ledger-gen --check`, then `validate-ledger integrity
  --ledger proofs/ledger.json`), `stage1-gate` (`continue-on-error: true`, missing set in the job
  summary). `permissions: contents: read`; triggers push + pull_request.
- CREATE `tests/test_ledger_gen.py`, `tests/test_normalization.py`, `tests/test_stage0_workflow.py`.

## Contract
C1 `render` twice ⇒ byte-identical pair; after `generate`, `--check` exits 0; two `generate` runs
   differ ONLY in marker probe fields (show the confined diff).
C2 Hand-editing one state in `ledger.json` ⇒ `--check` exit 1 naming the proof AND
   `validate-ledger integrity --ledger` reports `ledger-drift: …`.
C3 Empty set: four denominators 7/3/1/1, numerators 0, no `N/12`; the two committed markers appear
   in `markers` with their true status.
C4 `normalize`: timestamp, pid and temp path replaced; idempotent; `--compare` on an undeclared
   difference ⇒ `undeclared-volatile-field:` with the line.
C5 Workflow parses; three jobs; `stage1-gate` has `continue-on-error: true`; pins equal setup.sh.
C6 Full suite green twice (counts verbatim); `validate-ledger integrity --ledger proofs/ledger.json`
   on the committed tree: exit 0 or exit 1 ONLY for `deferral-expired` (state which).
C7 One named mutant killed: `--check` without the byte-compare ⇒ C1/C2 red.
C8 Hooks pass; boundary only; no secrets.

## Non-negotiables
As the parent brief. No PyYAML. Never sudo/install. No subagents, no outward actions. Append each
finished section to `$LANE_REPORT_DRAFT`.

## Report (DATA, ≤ 50 lines)
files:lines · pytest ×2 · C1–C8 decisive lines · mutant · discrepancies · NOT-done · adjacent defects.
