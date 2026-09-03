# BRIEF — increment #2 `s0-02-runner-ledger-ci`: proof runner + ledger generator + CI split checks + probe-backed blocked markers
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

You are the BUILD lane (Hermes on the PC, role code-implementer). The coordinator keeps the seed
and the contract below; you implement, test, commit in your worktree, and report DATA. An
adversarial verifier grades against the CONTRACT, never against your own tests. `.hermes.md`
carries the project rules. honey: ultra.

## Read first (primary sources, in this order — the brief is a hypothesis, the tree wins)
1. `tasks/stage0-breakdown.md` — "Pinned decisions" (runner-emitted truth; execution denominator =
   digest-verified `runs[]`; two SPLIT CI checks; probe-backed markers; `credential_rejected` ⇒
   proof-RED; blocker gone ⇒ `deferral_expired` RED) and the row for increment 2.
2. `seeds/seed-stage0-v1.yaml` — `constraints`, `ontology_schema` (blocked_marker,
   ledger_denominator, fixture_format), the S0-03 and S0-08 blocks (`blocked_marker.probe`,
   `reason_enum`, `rule`, `unblock_condition`), the S0-01 block's "normalized-then-golden" rule.
3. Increment #1 as landed: `proofs/registry.yaml`, `proofs/schemas/*.json`,
   `scripts/validate-ledger` (its `--ledger` input shape is `{"proofs": [{"proof_id", "state"}]}`;
   its digest = sha256 over `json.dumps(runs, sort_keys=True, separators=(",", ":"))`; it exits
   3 without the date-time checker), `tests/test_validate_ledger.py` (the style every new test
   follows: negatives first, exact reasons, tmp_path copies, `sys.executable` spawns).
4. `.github/workflows/planning-checks.yml` (the only workflow today; it stays).
FIRST ACTION: `pwd && git rev-parse HEAD` equals the PIN, tree clean,
`$HOME/venv-agent-factory/bin/python -m pytest tests/ -q` fully green; halt loud otherwise.

## Goal
The machinery that turns REAL runs into the ledger and makes the ledger impossible to hand-edit:
a runner that writes `result.json` only from subprocesses it ran, a generator that derives the
ledger from artifacts alone (byte-identical on every regeneration, anywhere), two split CI checks
(`ledger-integrity` green on the honest empty set, `stage1-gate` RED by design), a declared
volatile-field normalization table, and blocked markers for S0-03 and S0-08 whose probe is re-run
on every generation. Nothing here runs a proof. No stub of any component.

## COORDINATOR DECISIONS (pinned; each with its rejected alternative — do not re-litigate)
D1 **Probe venue.** Marker probes run on the EXECUTION venue (the PC, or the sandbox) at
   ledger-generation time and are RECORDED (probe leg with timestamps, exit, digests,
   `env_fingerprint`). CI (GitHub-hosted) validates structure, digests, drift and the recorded
   probe; it never probes for capability itself — a GitHub runner is not the venue, so a
   runner-side `runsc` probe would say "absent" forever (a venue-blind marker is a hollow
   green in the RED direction). Rejected: CI re-probes on its runner (wrong venue); CI reaches
   the PC over the bridge (secrets in CI; the link is ephemeral).
D2 **Generation always re-probes.** `ledger-gen` has no "skip probes" mode: every generation
   re-runs every blocked proof's probe and rewrites its `blocked.json`. `ledger-gen --check` is
   the CI mode: NO probing, regenerate from committed artifacts, byte-compare to the committed
   ledger, exit 1 with a diff on drift. Rejected: a static marker checked for presence.
D3 **One canonicalization.** Exactly one digest/canonicalization implementation exists in the
   repo and the runner shares it with `scripts/validate-ledger` BY CONSTRUCTION (import the
   validator's function — e.g. `importlib.util.spec_from_file_location` on the script — or move
   it into one shared module both import). A second copy is a defect (canonicalization drift =
   AP-32 class). Do not change the digest definition.
D4 **The environment is not a config channel.** The runner builds each leg's environment from
   the spec's explicit `env` map plus `PATH`/`HOME`/`LANG` only; it never inherits the parent
   environment. Secrets reach a probe only through a spec-declared `key_env` name; no value is
   ever written to any artifact or log (the S0-03 probe records presence/acceptance, never the
   secret). Classification is read from the REGISTRY, never from a spec.
D5 **Deferral expiry is RED.** A probe whose blocker is now present and working writes
   `blocker_status: expired`; `validate-ledger` reports `deferral-expired: <id>` (exit 1) and the
   ledger shows the proof RED, never BLOCKED. `credential_rejected` keeps the existing S0-03
   rule (proof-RED). Extend `blocked.schema.json` and the validator minimally for `expired`;
   every existing test stays green unchanged.
D6 **`stage1-gate` is RED by design and must not block.** Its CI job runs with
   `continue-on-error: true` and writes the missing set to the job summary; `ledger-integrity`
   and `tests` are ordinary (blocking) jobs. Rejected: one job doing both (an empty repo would
   read as passing).

## Deliverables (boundary — touch ONLY these paths; report anything else, never fix it)
- `scripts/proof-runner` — `run --proof <id> --venue sandbox|pc-bridge --root <dir>` executes
  the legs in `proofs/<id>/spec.json` (schema `proofs/schemas/spec.schema.json`: per leg `leg`,
  `cmd` argv, `cwd` relative to root, `timeout_s`, `env` map, `expect.exit_code`, and for the
  negative leg `expect.failure_reason`), records `started_at`/`finished_at` (UTC, `Z`), exit code,
  sha256 of stdout and stderr, optional artifacts, computes the digest per D3, sets
  `negative_control.observed_failure_reason` to the FIRST stdout/stderr line containing the
  expected reason (no match ⇒ the run is INVALID: exit 1 with `negative-control-unmet: <id>`,
  and NO `result.json` is written), writes `proofs/<id>/result.json` valid against
  `result.schema.json`. `probe --proof <id> --venue …` runs `proofs/<id>/probe.json`
  (`probe_cmd`, `timeout_s`, `env`, optional `key_env`, `reason_map` from exit classes to the
  seed's `reason_enum`) and writes `proofs/<id>/blocked.json` (D4, D5). Timeouts kill the
  process group and record exit `-9`/timeout as a leg failure, never a hang.
- `scripts/ledger-gen` — `generate --venue … --root …` (D2) and `--check` (CI). Writes
  `proofs/ledger.json` (`proofs: [{proof_id, classification, state}]`, per-class
  `numerator`/`denominator` read from the registry, `markers: [{proof_id, blocker_status,
  probed_at, probe_venue}]` copied from the artifacts) and `proofs/LEDGER.md` (a four-way table:
  execution / conformance-checked decision / blocked-on-external-input / blocked-on-capability,
  with the exact counts and per-proof rows; the string `N/12` for any N must not appear — the
  seed's own check greps for it). Deterministic: no wall-clock field of its own; two runs on any
  host produce identical bytes.
- `proofs/normalization.yaml` + `scripts/normalize` — the declared minimal volatile-field table
  (name, regex, replacement; at least: RFC3339 timestamps, pids, durations, session/thread ids,
  absolute temp paths, hostnames) applied line-wise; the table is CLOSED: a golden compare fails
  with `undeclared-volatile-field: <line>` when two runs differ on a line no rule normalizes.
  `normalize <file>` prints the normalized text; idempotent (normalizing twice = once).
- `proofs/S0-03/probe.json`, `proofs/S0-08/probe.json` and the markers they produce ON THIS
  VENUE via `ledger-gen generate --venue pc-bridge` (S0-08: `command -v runsc` then a trivial
  runsc invocation per the seed; S0-03: presence of the `key_env` secret, then one authenticated
  no-op against OmniRoute at `http://127.0.0.1:20128/v1` — `GET /v1/models` with the bearer —
  recorded as accepted/rejected; NEVER print, hash or store the secret). Whatever the probes
  find is the recorded truth (expired deferrals are the expected honest outcome on the PC).
- `.github/workflows/stage0-ledger.yml` — jobs `tests` (pip-pinned deps exactly as
  `scripts/setup.sh`; `python -m pytest tests/ -q`), `ledger-integrity` (`ledger-gen --check`,
  then `validate-ledger integrity --ledger proofs/ledger.json`), `stage1-gate` (D6).
  `permissions: contents: read`; triggers: push (all branches) and pull_request.
- Tests: `tests/test_proof_runner.py`, `tests/test_ledger_gen.py`, `tests/test_normalization.py`,
  `tests/test_stage0_workflow.py` (the YAML parses, the three jobs exist, `stage1-gate` carries
  `continue-on-error: true`, the pip pins equal setup.sh's). Fixtures are throwaway specs under
  tmp_path whose legs are real subprocesses (`python3 -c …`); the repo never gains a proof
  artifact except the two markers and the generated ledger.
- `scripts/setup.sh` / `harness-ports/bin/pc-setup.sh` only if a new pinned dependency is
  unavoidable (state why; PyYAML is NOT declared today — `normalization.yaml` may be JSON-syntax
  YAML like the registry, or you pin `PyYAML==6.0.2` in both setup scripts and the workflow).

## Contract (pre-registered; the verifier grades against THIS list)
C1 A throwaway spec with a positive leg (exit 0) and a negative leg whose stderr carries the
   expected reason ⇒ `result.json` valid against `result.schema.json`, digest equal to the
   validator's recomputation, `validate-ledger integrity` shows the proof PRESENT.
C2 The same spec with the negative leg's reason absent ⇒ exit 1 `negative-control-unmet: <id>`
   and NO `result.json`.
C3 A leg that sleeps past `timeout_s` ⇒ the leg records a timeout failure within 2×timeout and
   no child process survives (assert by pid).
C4 The runner's leg sees ONLY the spec's env + PATH/HOME/LANG: a leg printing
   `os.environ` shows no parent variable set by the test (`CANARY_FROM_PARENT`).
C5 `classification` in `result.json` equals the registry's, whatever the spec says (a spec
   carrying `classification` is rejected: `spec-schema: additional property classification`).
C6 `ledger-gen generate` twice ⇒ `ledger.json` and `LEDGER.md` byte-identical; `ledger-gen
   --check` exit 0 on the committed pair; hand-editing one state in `ledger.json` ⇒ `--check`
   exit 1 naming the proof, and `validate-ledger integrity --ledger` reports `ledger-drift: …`.
C7 On the empty set the ledger shows four denominators 7/3/1/1 with numerators 0 and no `N/12`.
C8 S0-08 probe on a venue without runsc ⇒ `blocked.json` valid, `blocker_status: absent`,
   integrity shows S0-08 BLOCKED; a fake `runsc` on PATH that succeeds (tmp_path fixture) ⇒
   `blocker_status: expired`, `validate-ledger` prints `deferral-expired: S0-08`, exit 1.
C9 S0-03 probe with the `key_env` unset ⇒ `credential_absent` (BLOCKED); set but rejected by a
   local HTTP double answering 401 (test fixture only — a real OmniRoute is never stubbed in a
   committed artifact) ⇒ `credential_rejected` ⇒ the existing S0-03 proof-RED rule fires; no
   artifact or log contains the secret's value (grep the tmp_path tree for it: 0 hits).
C10 `normalize` on a transcript with a timestamp, a pid and a temp path ⇒ every one replaced;
    running it twice ⇒ identical; a compare of two runs differing on an undeclared field ⇒
    `undeclared-volatile-field:` with the line.
C11 Workflow: parses; jobs `tests`, `ledger-integrity`, `stage1-gate` present; `stage1-gate`
    has `continue-on-error: true`; the pip line pins `jsonschema==4.25.1` and
    `rfc3339-validator==0.1.4` (and PyYAML iff you declared it in setup.sh).
C12 Full suite `$HOME/venv-agent-factory/bin/python -m pytest tests/ -q` green twice, counts
    verbatim; `validate-ledger integrity --ledger proofs/ledger.json` on the committed tree
    exit 0 (or exit 1 ONLY for `deferral-expired` findings that are the truth on this venue —
    state which); `validate-ledger stage1-gate` exit 2.
C13 Three named mutants killed and reported: (a) runner digest computed over `runs` with
    `indent=2` ⇒ `digest-mismatch`; (b) generator dropping the `--check` byte-compare ⇒ C6
    reds; (c) probe writer ignoring exit 0 (never writing `expired`) ⇒ C8 reds.
C14 Commits pass the repo hooks; only the boundary is touched; no secret, bridge link or model
    identifier in any committed file.

## Non-negotiables (constraints, not steps)
- NO STUBS in committed artifacts; HTTP doubles live only inside tests. Never create
  `proofs/<id>/result.json` in the repo. Never run anything with sudo; never install system
  packages; never stop or restart the owner's services (OmniRoute, Buzz, Ollama, …).
- Negative controls are authored BEFORE positive legs and fail for the exact reason.
- Numeric guards reject the whole unusable class; digests are 64 lowercase hex or invalid.
- Do NOT spawn subagents. Do NOT push, open PRs, comment, or take any outward action.
- Commit in your worktree the moment each deliverable's tests are green; commit messages carry
  the reasoning (rejected alternative, ordering, primary source, literal test invocation).
- A deviation from any exact-string, byte-preservation or boundary clause is STOP-and-report.

## Report (DATA, ≤ 80 lines)
files:lines per deliverable · literal pytest invocations ×2 with summaries · per contract item
C1–C14: the command + the decisive output line · the three mutants with their killing test ·
the two markers' recorded `blocker_status` and probe venue · discrepancies · NOT-done ·
adjacent defects (file:line).
