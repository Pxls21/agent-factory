# VERIFY-O1 — adversarial grade of lane O1 (S0-03 Hermes→OmniRoute: the identity-asserting checker, the proof-owned Hermes profile, three negative bundles, the probe's error mapping, the PC leg runner)

You are an adversarial-verifier (Opus 5 in the sandbox, or the PC Hermes `adversarial-verifier` role). Repo /home/user/agent-factory,
branch claude/soundbox-kit-migration-iz1jwf. **PIN: `b5670c1`** (the commit carrying the lane's 30 files + its report). Grade
the bytes of `git archive <PIN>` from a copy under the session scratchpad /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/
(`vo1/`; delete it when done). Read-only git on the shared tree; every mutant on scratch copies; every pytest run with an explicit
`--basetemp`; kill only what you start, PID-targeted; never background a run and stop; no outward actions; NO network call to any
OmniRoute or model endpoint (there is none in the sandbox; the PC's is the owner's — never touched by a verifier).

**The ONE bridge action you MAY take:** the pytest-only PC gate `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_03_omniroute.py`
from a clean detached worktree of the PIN, then `wait <RUN_ID>`. Nothing else on the bridge — in particular NEVER run the S0-03
runner, the direct probe, or anything that sends a request to `:20128`.

**Inputs (read in this order):** the lane brief `tasks/briefs/s0-03-o1-omniroute-roundtrip-identity-checker-pc-legs.md` (the contract:
Design 1-8) · the lane's report `tasks/briefs/s0-03-support/O1-report.md` (the identity answer with file:line into the pinned OmniRoute
source, the two defects fixed, the leg-B blocker, the 14 mutants, the registry diff) · the material pack
`tasks/briefs/stage0-parallel-support/material-S0-03.md` (the seed block :382-405, the council's "single most important assertion",
the marker/runner/validator rules) · the pinned OmniRoute source `/home/user/nerdherderdani/OmniRoute` (commit 488f57e9, READ-ONLY):
`openai-responses.ts`, `chatCore.ts`, `codexIdentity.ts`, `callLogs.ts` — the lane's four citations · the pinned Hermes source
`/home/user/nerdherderdani/hermes-agent` (527da608): the custom-provider keys, the `codex_responses` client, the 401 path · the S0-01
launcher the lane could not invoke: `proofs/S0-01/pins.py:18`, `proofs/S0-01/tools/pc/pc_launch.py:189-190` (the shared tree carries
lane P5a's uncommitted versions — grade the blocker against BOTH the committed and the P5a bytes) · `docs/INCIDENT-LOG.md`
(AF-AP-23, AF-AP-35, AF-AP-39, AF-AP-42) · the PC facts the coordinator measured 2026-09-08 00:4xZ (in the lane's report's inputs):
`/v1/models` 401 without a key, 200 with the owner's Hermes key; the routes `agentfactory-build/-verify/-research/-sweep`; the stub
routes `s0-01-scripted/s0-01-pong` and `s0-01-scripted/s0-01-slow`; the key name `OMNIROUTE_API_KEY` in the owner's profile env.

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-03-support/O1-report.md --rev <PIN> --map C=proofs/S0-03/check_omniroute_roundtrip.py
--map T=tests/test_s0_03_omniroute.py --map P=proofs/S0-03/probe_omniroute.py` — MISS 0 or a finding; `ap_screen.py proofs/S0-03
proofs/S0-03/tools proofs/S0-03/tools/pc` (four AP-1 hits) and `--tests` (AF-AP-34 prose hits) — each classified by RUNNING it.

## Items
1. **The identity assertion, against the source.** Reproduce the lane's four citations by `sed -n` on the pinned OmniRoute checkout:
   does `/v1/responses` echo the requested model id for codex-originated callers, and is `call_logs` the row that carries
   provider/model/requested_model separately? Then the design question the council asked (Socrates): with conjunct (iii) on
   `omniroute-requests.json` (a copy of the call_logs rows the runner exports), what stops a FORGED requests file from naming a real
   provider? Enumerate what binds the requests file to the leg (timestamps? request ids matching the streamed response id?
   the nonce?) and write the forged-bundle mutant. If nothing binds it, that is the round's blocker: the identity claim rests on a
   file the runner writes from a query the checker cannot re-run.
2. **The six conjuncts, one mutant each** (the lane's REASONS table): the falsified-one-at-a-time set, first-failure order pinned; the
   stub-route list read from the spec (both stub ids + the bare connection name); the nonce present-in-text rule (a response that
   quotes the prompt back — does the nonce check accept it? should it?); the tool-call leg's parse of the timeline by S0-01's reader by
   IMPORT (assert `inspect.getmodule`).
3. **The env allowlist as a segment rule.** `OMNIROUTE_API_KEY` accepted; `OMNIROUTE_API_KEY_2`, `FOO_API_KEY`, `MY_TOKEN`, `PRIVATE_KEY`
   rejected; `PATH`, `HOME` accepted; the brief's literal regex shipped as mutant M8 dies. Then: `HERMES_API_KEY`? `OMNIROUTE_API_KEY_FILE`?
   State the rule's exact boundary and whether it matches AF-AP-23 (deny-by-default, an explicit allowlist).
4. **The transport pin (conjunct v).** The proof-owned `hermes/config.yaml` declares `api_mode: codex_responses` + the compression-off
   header; the checker rejects `chat_completions` with the ADR-0002 reason. Verify the pinned Hermes (527da608) actually SUPPORTS
   `codex_responses` against a custom `base_url` (cite the client path) — if it does not, the round's design produces a guaranteed
   RED on the PC and the owner's task #35 must be decided first; say which.
5. **The probe (`probe_omniroute.py`)** — the five outcomes over real sockets (200 / 401 / 403 / 500 / closed port / a slow server that
   exceeds the 5 s timeout → which code?); exits 12 and 13 unmapped in `probe.json` → `scripts/proof-runner` raises `probe-invalid`
   (run the runner's probe path on a scratch copy with a local server to prove the LOUD outcome, not just the exit code).
6. **The three negative bundles** — each produces its exact reason; `PROVENANCE.md` per bundle says which frames are from the real
   corpus and which from the sources (AF-AP-42); the `credential-absent` bundle's 401 body shape matches OmniRoute's real 401 (cite
   the source line that builds it).
7. **The PC runner + the direct probe — READ, never run.** The key never in argv (the header-file technique — find it); the key file's
   permission check; the runner's preflight (`omniroute_invariants.sh`, 0600, the route id in `/v1/models`); the negative leg unsets
   the key in the LAUNCH env only; every process the runner starts is killed by its own pid; the leg-B blocker reproduced by READING
   `pc_launch.py` (committed and P5a's bytes): exactly what refuses, and the minimal seam (an env override for the Hermes home + a
   `--profile` path? a proof-owned launcher?) — give the coordinator the smaller of the two with its risk.
8. **The class flip.** The report's `registry.yaml:14` diff — schema-valid? does `validate-ledger` accept a proof whose class changed
   while `blocked.json` still exists (it must not — both present = INVALID); what must be deleted/regenerated in the same reviewed
   commit (AF-AP-56: the five PRESENT proofs' result.json)? List the exact sequence.
9. **The 18-class preflight** the lane ran (its class-13 find) — re-scan the 30 files; a class the lane missed = a finding.
10. **The PC gate (the carve-out)**; paste beside the checkpoint's lines; agree.
11. **Mutants ≥ 24** (the lane's 14 + yours: the forged requests file, the echoed-model tautology, the nonce-quoted-back, the
    `HERMES_API_KEY` name, a 401 body of another shape, a bundle whose `profile.yaml` carries an inline `api_key` value).
12. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census.
13. **The design.** Is the call_logs row the right identity oracle for a proof whose consumer is a ledger (a DB query the runner
    exports vs a response the checker parses)? Would a second, independent instrument (e.g. OmniRoute's request log line in the
    journal) make the identity claim two-instrument (tactic 8)? Keep it to what you measured.

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-O1.md` — draft after EACH item — then return it whole. Findings: ALL, no severity
filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact red test, SOLID/UNSURE;
reproduced vs reviewed vs skipped; shared-tree hygiene; verdict MERGE-READY or NOT-READY with the blocking set, the cheapest path, and
the exact PC steps for the coordinator's live legs.
