# BRIEF — increment #1 `s0-01-registry-schemas-validator`: proof registry + artifact schemas + ledger validator with EMPTY-SET semantics
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

> **STATUS 2026-09-03: DONE.** Landed through four PC Hermes lanes (build round 1 at pin c39b64f; repair rounds s0-01b, s0-01d; adversarial verify s0-01e) plus the coordinator's own harvest fixes; final layer 45 tests ×2, C1–C18 PASS, attacks A1–A8 SOLID. Commits: `git log --oneline c39b64f..HEAD -- proofs scripts/validate-ledger tests`.

> **AMENDED 2026-09-03 after lane round 1 (coordinator-level, reason stated):** round 1 halted on a
> premise the brief got wrong — `spikes/pc-bridge/result.json` carries a THREE-effect ARRAY with
> rule ids `map-pcbridge-s003`, `map-pcbridge-s008`, `map-rust-s006` and one `blocked_capability`
> value; the brief had described a single object "lacking a rule_id" and invented `map-bridge-s003`.
> The spike-schema, registry-mapping, C8 and C9 clauses below are rewritten to the record's actual
> shape; nothing else changed. (docs/INCIDENT-LOG.md, AP-43 instance.)

You are the BUILD lane (Hermes on the PC, role code-implementer). The coordinator keeps the seed
and the contract below; you implement, test, commit in your worktree, and report DATA. The
adversarial verifier grades against the CONTRACT, not against your own tests.

## Read first (primary sources, in this order — the brief is a hypothesis, the tree wins)
1. `tasks/stage0-breakdown.md` — "Pinned decisions" table and the row for increment 1 (deliverables,
   acceptance, negative controls). 2. `seeds/seed-stage0-v1.yaml` — `constraints`, `ontology_schema`
   (the domain model: proof_id, classification, wave, assertions, negative_control, fixture_format,
   blocked_marker, ledger_denominator …), the per-proof `stage0_proofs` blocks, and the frozen
   `spike_to_class_mapping` at the end. 3. `docs/07_BUILD_PLAN.md` §Stage 0 (the twelve proofs).
   4. `spikes/pc-bridge/result.json` (spike #0, already recorded) and `.hermes.md` (your project rules).
FIRST ACTION: `pwd && git rev-parse HEAD` must equal the PIN and the tree must be clean; halt loud
otherwise.

## Goal
Day-one machinery that is honest on an EMPTY artifact set: a registry that declares the twelve
proofs with their class/wave/spike gates, JSON schemas every future artifact must satisfy, and a
validator whose `integrity` check is GREEN on the honest empty set (all twelve ABSENT, zero
numerators, four denominators read from the registry) while its `stage1-gate` check is RED with
named reasons — and which turns RED for the exact stated reason on every forgery the breakdown
names. Nothing here runs a proof. No stub of any component.

## Deliverables (boundary — touch ONLY these paths)
- `proofs/registry.yaml` — twelve entries S0-01..S0-12. Per entry: `proof_id`, `title`,
  `classification` (exactly one of `execution_proof | conformance_checked_decision |
  blocked_credential | blocked_host`), `wave` (0-3 per the seed), `spike_dependencies` (list of
  spike names from the mapping; empty list allowed), `required_negative_controls` (int ≥ 1; S0-02
  = 4 — four DISTINCT reasons; S0-05 and S0-08 are defined by their failing legs), `assertion_count`
  (number of seed assertions), and for `blocked_*` entries a `blocked` object (`owner`: the seed's
  placeholder, `unblock_condition`, `marker_path`: `proofs/<id>/blocked.json`). Top-level:
  `classes` (the four, with their ledger denominators declared), `waves`, and
  `spike_to_class_mapping` copied from the seed VERBATIM in content, with TWO declared
  decisions, both stated in a `# COORDINATOR DECISION` comment: (a) VOCABULARY — the seed writes
  `blocked_capability` twice (map-rust-s006's `to_class`, S0-08's `ledger_denominator`) and the
  pc-bridge record writes it once, while the ontology enum says `blocked_host`; the registry's enum
  is the four canonical names, and it declares `class_aliases: {blocked_capability: blocked_host}`
  which the validator applies ON READ to spike effects and mapping rules only (proof artifacts must
  use the canonical enum). (b) ADDITION (owner answer 2026-09-03, breakdown §Owner answers) — the
  `pc-bridge` spike joins the mapping with the rule ids its EXISTING record already cites:
  `map-pcbridge-s003` positive_effect S0-03 `blocked_credential` → `execution_proof` (OmniRoute on
  the PC is the egress; identity assertable), and `map-pcbridge-s008` negative_effect S0-08
  `blocked_host` → `blocked_host` (host reachable, runsc absent at probe time — confirms deferral;
  the record's `blocked_capability` normalizes to it). The record's third effect cites the seed's
  `map-rust-s006` positive branch (S0-06 stays `execution_proof`, buildable on the PC): a rule may
  be cited by any spike whose probe satisfies it, so the validator matches an effect by
  (rule_id, from_class, to_class) against the rule's declared negative OR positive branch. Initial
  declared classes stay the SEED's (S0-03 blocked_credential, S0-08 blocked_host): a class changes
  ONLY through a spike artifact the validator reads.
- `proofs/schemas/result.schema.json`, `proofs/schemas/blocked.schema.json`,
  `proofs/schemas/spike.schema.json` — JSON Schema (draft 2020-12), `additionalProperties: false`
  at the top level. `result`: proof_id, classification, recorded_at (RFC3339 UTC), env_fingerprint
  (string; `pc-bridge:<host>` or `sandbox:<id>`), `runs` (array, min 2 items — the positive and
  negative legs — each with leg ∈ {positive, negative}, cmd (array of strings), started_at,
  finished_at, exit_code (int), stdout_sha256, stderr_sha256 (64-hex), and optional artifacts
  (list of {path, sha256})), `negative_control` ({fixture, expected_failure_reason,
  observed_failure_reason}), `digest` (64-hex sha256 over the CANONICAL JSON of `runs` — sorted
  keys, no whitespace — this is what the validator recomputes). `blocked`: proof_id,
  classification (blocked_*), env_fingerprint, `marker` ({probe_cmd, probe_run (same shape as a run
  leg), blocker_status ∈ {absent, rejecting}, unblock_condition, owner}) — a marker with
  blocker_status `rejecting` and a credential probe is NOT a valid blocked marker for S0-03 (the
  breakdown: `credential_rejected` ⇒ proof-RED); express that as a schema-level or validator-level
  rule and say which. `spike`: the field NAMES and shapes come from the existing `spikes/pc-bridge/result.json`, read it:
  `spike_id`, `schema` (string), `ran_at`, `env_fingerprint`, `runs` (array of {command: string,
  exit_code: int, stdout_digest: string} — spike runs are looser than proof runs, by design),
  `facts` (object), `classification_effect` (ARRAY, possibly empty, of {affected_proof,
  from_class, to_class, rule_id, reason?}), `not_verified` (array of strings); add `outcome` ∈
  {positive, negative, errored}. Migrate the pc-bridge record by ADDING `outcome: positive` and
  setting `schema` to the new schema's `$id`; every other key and value stays byte-for-byte. `spikes/hermes-lane-trial/` is a tooling spike, not a
  classification spike: leave it alone; the validator ignores spikes the mapping does not name.
- `scripts/validate-ledger` (python3, executable, stdlib + `jsonschema`) with two subcommands and
  deterministic output (sorted keys, no timestamps, exit codes are the contract):
  `validate-ledger integrity [--root .] [--ledger <path>]` and `validate-ledger stage1-gate [--root .]`.
  `integrity`: validates the registry (structure, the enum, twelve unique ids, every
  spike_dependency named in the mapping), every `proofs/<id>/result.json` and `blocked.json` that
  exists (schema + recomputed digest + class agreement with the registry), every mapped spike
  artifact that exists (schema + a declared effect only), and, when `--ledger` is given, that
  every claim in that ledger is backed by an artifact (a claim without one ⇒ `ledger-drift`).
  Prints one line per proof (`S0-01 ABSENT` / `PRESENT` / `BLOCKED`) and the four denominators
  (from the registry) with their numerators (from artifacts). Exit 0 iff honest, even when every
  proof is ABSENT. `stage1-gate`: exit 2 unless every registered execution proof and
  conformance decision has a valid artifact and every blocked proof has a valid marker; prints
  each missing item as `missing: <id> (<class>)`. Named failure reasons (exact strings, printed
  once per finding, exit 1 for integrity): `registry-schema: <detail>`, `unknown-class: <id>
  <value>`, `digest-mismatch: <id>`, `class-mismatch: <id> registry=<a> artifact=<b>`,
  `ledger-drift: <id> claimed <state> but <found>`, `spike-artifact-invalid: <name> <detail>`,
  `undeclared-transition: <name> <from>-><to>`.
- `tests/test_validate_ledger.py` — deterministic, LLM-free, runs in < 10 s, uses `tmp_path`
  copies of the real registry/schemas (never the real tree): empty set ⇒ integrity exit 0 with the
  exact twelve ABSENT lines and denominators execution_proof=7, conformance_checked_decision=3,
  blocked_credential=1, blocked_host=1, numerators all 0; stage1-gate exit 2 listing all twelve;
  a synthetic valid result for one proof ⇒ PRESENT and numerator 1; the SAME artifact with one
  byte of `runs` changed and the old digest ⇒ `digest-mismatch`; a hand-written ledger claiming
  S0-01 PASSED over the empty set ⇒ `ledger-drift`; a registry copy with a class removed ⇒
  `registry-schema`; a class value outside the enum ⇒ `unknown-class`; a spike artifact with an
  effect whose rule_id is not in the mapping ⇒ `undeclared-transition`; `integrity` output
  byte-identical across two runs (assert on captured bytes). Every negative test asserts the
  EXACT reason string and the exit code.
- Dependency: add `jsonschema==4.25.1` (or the newest 4.x you can install — state the version) to
  the venv install line in `scripts/setup.sh` and `harness-ports/bin/pc-setup.sh` (ONLY that
  line), and install it into `$AF_VENV` for your own run.
- `todo/BUILD-TASKLIST.md`: do NOT edit (coordinator surface). `docs/`: do NOT edit.

## Contract (pre-registered; the verifier grades against THIS list, C1–C12)
C1 `validate-ledger integrity` on the committed tree (no proof artifacts) exits 0 and prints
   twelve `ABSENT` lines and the four denominators 7/3/1/1 with numerators 0.
C2 `validate-ledger stage1-gate` on the same tree exits 2 and names all twelve missing items.
C3 Both outputs are byte-identical across two consecutive runs.
C4 Forged digest ⇒ exit 1, `digest-mismatch: <id>`; the unforged twin passes (positive control).
C5 Hand-edited ledger claiming a proof over the empty set ⇒ exit 1, `ledger-drift: …`.
C6 Registry entry without `classification` ⇒ `registry-schema`; a fifth class value ⇒ `unknown-class`.
C7 The registry's twelve classes equal the seed's: execution_proof = {01,02,04,05,06,07,11},
   conformance_checked_decision = {09,10,12}, blocked_credential = {03}, blocked_host = {08}.
C8 The registry mapping contains every rule the seed lists (map-rust-s006, map-runsc-s008,
   map-dockerd-venue, map-egress-s005) plus map-pcbridge-s003 and map-pcbridge-s008; the committed
   pc-bridge record's three effects all validate as declared (after alias normalization); an
   effect with an unknown rule_id, or a declared rule_id with a from/to pair that matches neither
   branch ⇒ `undeclared-transition`.
C9 `spikes/pc-bridge/result.json` validates against spike.schema.json; `git diff` on it shows
   exactly one added key (`outcome`) and one changed value (`schema`), nothing else.
C10 All three schemas are valid JSON Schema and reject an artifact with an extra top-level key.
C11 `python -m pytest tests/ -q` passes in full on the PC (existing suites included), twice.
C12 The lane's commits pass the repo hooks (pre-commit lint delta + shell-syntax + skill-sync run
   on commit in your worktree; `core.hooksPath` is inherited) and touch only the boundary.

## Non-negotiables (constraints, not steps)
- NO STUBS, no fake artifacts committed as if real: the only artifacts in the tree after this
  increment are the registry, the schemas, the migrated pc-bridge spike and test fixtures under
  `tests/`. Never create `proofs/<id>/result.json` in the repo.
- The negative controls are authored BEFORE the positive legs and must fail for the exact reason.
- `os.environ` is not a config channel for the validator: paths come from arguments.
- Numeric guards reject the whole unusable class (a digest is 64 lowercase hex or invalid).
- Do NOT spawn subagents. Do NOT edit files outside the boundary; report adjacent defects, never
  fix them. Do NOT push, open PRs, comment, install system packages, or use sudo.
- Commit in your worktree the moment each deliverable's tests are green (checkpoint discipline);
  commit messages carry the reasoning (rejected alternative, ordering, primary source).
- Deviation from any exact-string or byte-preservation clause above is STOP-and-report, never
  self-accepted.

## Report (DATA, verbatim)
1. `git log --oneline <PIN>..HEAD` and `git status --short`.
2. The literal invocations and full outputs of C1, C2 (once) and the two-run byte comparison (C3).
3. `pytest tests/ -q` last line, twice.
4. The jsonschema version installed; the exact normalization/addition comment text in the registry.
5. Discrepancies vs this brief (each with the tree evidence), adjacent defects found (not fixed),
   NOT-done list.
