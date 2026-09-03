# BRIEF — increment #2a `s0-02a-runner-probes`: proof runner + spec/probe schemas + probe-backed markers (half A of increment #2)
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

You are the BUILD lane (Hermes on the PC, role code-implementer). Increment #2 is split in two
because one lane cannot hold it: THIS brief is half A (runner + probes). Half B (ledger generator,
normalization, CI workflow) is a later lane and is NOT yours. honey: ultra.

The parent brief `tasks/briefs/s0-02-runner-ledger-ci.md` BINDS here for: §COORDINATOR DECISIONS
D1–D6 and the probe→marker semantics paragraph under §Authoritative shapes (exit 0 ⇒ `expired`;
a `reason_map` code ⇒ its reason ⇒ `*_absent` → `absent`, `credential_rejected` /
`capability_present_but_failing` → `rejecting`; anything else or a timeout ⇒ `probe-invalid: <id>
exit <n>`, exit 1, no marker; `key_env` is the only secret channel). READ those two sections
once, by line range (`grep -n "^## " …` then `sed -n`), and do not read the rest of it.
`.hermes.md` carries the project rules.

FIRST ACTION (halt loud on any mismatch): `pwd && git rev-parse HEAD` equals the PIN, tree clean,
`$HOME/venv-agent-factory/bin/python -m pytest tests/ -q` → `63 passed` (45 + the 18 schema
closure tests). The two schemas EXIST; none of the CREATE paths below exist yet — verify with
`git ls-files proofs/schemas scripts tests | sort`.

## Deliverables (boundary — touch ONLY these paths; report anything else, never fix it)
- READ `proofs/schemas/spec.schema.json` and `proofs/schemas/probe.schema.json` — COMMITTED by the
  coordinator with their own closure tests (`tests/test_spec_probe_schemas.py`: every object
  closed, `classification` rejected, a negative leg needs `failure_reason`, both legs required).
  They ARE the contract; do not edit them — a spec that needs another field is a STOP-and-report.
- CREATE `scripts/proof-runner` with two verbs (argparse, `#!/usr/bin/env python3`, run under the
  project venv — the tests spawn it with `sys.executable`):
  `run --proof <id> --venue sandbox|pc-bridge --root <dir>` executes the legs of
  `proofs/<id>/spec.json`: clean env per leg (spec `env` + `PATH`/`HOME`/`LANG` only — D4),
  `cwd` resolved under root, `timeout_s` enforced by killing the process group, records
  `started_at`/`finished_at` (UTC `Z`), `exit_code`, sha256 of stdout and stderr, the digest per
  D3 (import the validator's canonicalization; never a second copy), `classification` READ from
  `proofs/registry.yaml` (a spec carrying `classification` is a schema error), and
  `negative_control.observed_failure_reason` = the FIRST stdout/stderr line of the negative leg
  containing `expect.failure_reason`; no match ⇒ exit 1 `negative-control-unmet: <id>` and NO
  `result.json`. Output `proofs/<id>/result.json` valid against `result.schema.json`.
  `probe --proof <id> --venue … --root …` runs `proofs/<id>/probe.json` per the parent's probe
  semantics and writes `proofs/<id>/blocked.json` (`blocker_status` absent | rejecting | expired,
  `marker.reason`, `probe_run` leg with digests, `env_fingerprint` = `<venue>:<hostname>`); the
  `key_env` variable is the ONLY value taken from the runner's own environment, passed to the
  probe and never written anywhere.
- MODIFY `proofs/schemas/blocked.schema.json`: `blocker_status` enum gains `expired`; optional
  `marker.reason` (the four reasons). MODIFY `scripts/validate-ledger`: an `expired` marker ⇒
  finding `deferral-expired: <id>` (exit 1, state INVALID, never BLOCKED); nothing else changes and
  every existing test stays green unchanged.
- CREATE `proofs/S0-03/probe.json` (probe: presence of `key_env` `OMNIROUTE_API_KEY`, then one
  authenticated `GET http://127.0.0.1:20128/v1/models` with the bearer; exit codes: 10 =
  credential_absent, 11 = credential_rejected, 0 = accepted) and `proofs/S0-08/probe.json`
  (`command -v runsc` + `runsc --version`; 10 = capability_absent, 11 =
  capability_present_but_failing, 0 = works). The probe commands are small committed shell/python
  scripts under `proofs/<id>/` (CREATE), never one-liners with secrets. Then GENERATE the two
  markers on THIS venue with `proof-runner probe --venue pc-bridge` and commit whatever they truly
  record (an `expired` S0-08 on a PC with runsc is the honest outcome; `credential_absent` for
  S0-03 if the variable is unset in your shell — do not go looking for the key).
- CREATE `tests/test_proof_runner.py` (throwaway specs under tmp_path, real subprocesses, negatives
  first; the repo never gains a `result.json`).

## Contract (pre-registered; the verifier grades against THIS list)
C1 Spec with a positive leg (exit 0) and a negative leg whose stderr carries the expected reason ⇒
   `result.json` valid, digest equal to the validator's recomputation, integrity shows PRESENT.
C2 Negative leg without the reason ⇒ exit 1 `negative-control-unmet: <id>`, no `result.json`.
C3 A leg sleeping past `timeout_s` ⇒ timeout recorded within 2×timeout, no surviving child (by pid).
C4 The leg's environment is ONLY spec env + PATH/HOME/LANG (a `CANARY_FROM_PARENT` set by the test
   is absent in the leg's `os.environ` dump).
C5 A spec carrying `classification` ⇒ rejected as an additional property; `result.json` carries
   the REGISTRY's classification.
C6 S0-08 probe with no runsc on PATH ⇒ `blocked.json` valid, `absent`, integrity BLOCKED; a fake
   `runsc` that succeeds (tmp PATH) ⇒ `expired`, `validate-ledger` prints `deferral-expired: S0-08`,
   exit 1.
C7 S0-03 probe with `key_env` unset ⇒ `credential_absent` (BLOCKED); set and refused by a local
   HTTP double answering 401 (test only) ⇒ `credential_rejected` ⇒ the S0-03 proof-RED rule fires;
   the secret's value appears nowhere under the tmp tree (grep = 0).
C8 Full suite `$HOME/venv-agent-factory/bin/python -m pytest tests/ -q` green twice (counts
   verbatim); `validate-ledger integrity` on the repo root exit 0 or exit 1 ONLY for
   `deferral-expired` findings that are true on this venue (state which); `stage1-gate` exit 2.
C9 Two named mutants killed: digest over `runs` with `indent=2` ⇒ `digest-mismatch`; probe writer
   never writing `expired` ⇒ C6 reds.
C10 Commits pass the hooks; only the boundary touched; no secret or bridge link in any file.

## Non-negotiables
NO STUBS in committed artifacts (HTTP doubles live in tests only). Never sudo, never install,
never touch the owner's services. Negatives before positives. No subagents, no outward actions.
Commit per green deliverable with a reasoning-record message. Deviation from an exact clause =
STOP and report. Append each finished section to `$LANE_REPORT_DRAFT`.

## Report (DATA, ≤ 60 lines)
files:lines · literal pytest invocations ×2 · C1–C10 with the decisive line each · the two markers'
recorded status + venue · mutants · discrepancies · NOT-done · adjacent defects.
