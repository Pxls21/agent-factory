# VERIFY-C1 — adversarial grade of lane C1 (S0-04 compression contract: the checker over captured legs, two request fixtures, three real-producer bundles, the capture tool, the PC leg runner)

You are an adversarial-verifier (Opus 5 in the sandbox, or the PC Hermes `adversarial-verifier` role). Repo /home/user/agent-factory,
branch claude/soundbox-kit-migration-iz1jwf. **PIN: `6d54935`** (the commit carrying the lane's 28 files + its report). Grade
the bytes of `git archive <PIN>` from a copy under the session scratchpad (`vc1/`; delete it when done). Read-only git on the shared
tree; every mutant on scratch copies; explicit `--basetemp`; kill only what you start, PID-targeted; never background a run and stop;
no outward actions; NO request to any OmniRoute or model endpoint. **The ONE bridge action:** the pytest-only PC gate
`scripts/pc_suite.sh launch -n 8 -- tests/test_s0_04_compression.py` from a clean detached worktree of the PIN, then `wait <RUN_ID>`.

**Inputs (read in this order):** the lane brief `tasks/briefs/s0-04-c1-compression-contract-checker-over-captured-legs.md` · the report
`tasks/briefs/s0-04-support/C1-report.md` (D1-D8, the 16 mutants, the 18-class table with six fixed defects, the discarded first
mutation run) · the material pack `tasks/briefs/stage0-parallel-support/material-S0-04.md` (the seed block :406-421, docs/03 §2, the
council's "sanctioned instrument" line) · the S0-01 scripted backend `proofs/S0-01/tools/scripted_backend.py` (checkpoint 8aa bytes —
`State.record`, what the record file holds, `raw_body`) · `scripts/proof-runner:181-199` (Deferred; the negative leg's SUBSTRING bind)
· `docs/INCIDENT-LOG.md` (AF-AP-27, AF-AP-29, AF-AP-38, AF-AP-41, AF-AP-42, AF-AP-47).

## Item 0 — the mechanical gates, pasted
`report_lint.py … --rev <PIN> --map C=proofs/S0-04/check_compression.py --map T=tests/test_s0_04_compression.py --map
K=proofs/S0-04/tools/pc/capture_leg.py --map R=proofs/S0-04/tools/pc/run_s0_04_legs.sh` — MISS 0 or a finding; `ap_screen.py proofs/S0-04
proofs/S0-04/tools/pc` (two AP-1 hits, one line) and `--tests` (the banned-token enumeration line) — classified by running.

## Items
1. **D1 — A3 without raw bytes.** Verify from the backend's bytes (8aa) that `raw_body` is never persisted and the record body is
   parsed + `sort_keys`; then attack the substitute: the equal-length key permutation the lane names as the residual — build it (a
   body whose keys reorder without changing the byte length) and show the checker PASSES; is there a second invisible rewrite
   (unicode escape vs raw UTF-8 of the same length? `1.0` vs `1.00`? a duplicate key the parser collapses)? Then rule: is the
   residual acceptable for a proof whose seed says "a deterministic stub proves request preservation", or must the backend
   persist raw bytes (an S0-01 backend change — a D5m item) before S0-04 mints? Give the argument from the seed's words.
2. **A2 the response header rules.** Absent / duplicated / wrong value / wrong case of the NAME / wrong case of the VALUE ("Off") —
   each one's exact reason; the ordered-pairs representation vs a dict (mutant 15); a header split across two lines (HTTP folding)?
3. **The leg set closed and declared** (`REQUIRED_LEGS`, `LEG_FIXTURE`): an extra leg refused; a missing leg FAILS (not defers); the
   `config` leg's `api_mode` RECORDED not asserted (D5) — should the proof instead assert the ADR-0002 transport like S0-03 does
   (the coordinator's ruling there: a RED finding for task #35, never a silent switch)? Argue from the two proofs' different seeds.
4. **The credential screen** (`LEAK_PATTERNS`, `_screen_tree`, the fingerprint carve-out shape-validated): a bearer split across
   two fields; a base64 key; the fingerprint field carrying a 64-hex that IS a real sha of a real key (indistinguishable by shape —
   is that the accepted limit?); the redaction of the checker's own reason lines.
5. **D4 the reason-substring collision** — reproduce the class with the REAL runner (`scripts/proof-runner` over the spec's negative
   leg with a bundle whose config leg fails): does the runner bind only the response-leg reason? Then sweep the OTHER proofs'
   specs on the branch (S0-01, S0-03, S0-05, S0-07, S0-08, S0-11) for the same collision shape (a failure_reason that is a substring
   of another reason the same checker can print) — a finding per proof, not this lane's blocker.
6. **The fixtures.** `request-baseline.json` / `request-large.json` canonical (the checker's `fixture-not-canonical` gate — mutant
   12); the 64 KiB body's provenance; the model id question (NOT_DONE 4: `s0-01-pong` vs `s0-01-scripted/s0-01-pong` — the coordinator
   measured the authenticated `/v1/models` on the PC: the stub ids are `s0-01-scripted/s0-01-pong` and `s0-01-scripted/s0-01-slow`;
   so the fixture's `"model": "s0-01-pong"` is WRONG for OmniRoute's edge and the runner's preflight would refuse — rule what the
   fixture must carry and whether the committed bundles (built from the bare id) stay valid).
7. **The three bundles from the REAL producer** (AF-AP-42): re-run the backend over the fixture bytes yourself and diff the record
   against the committed `upstream-record.json` (byte-identical? volatile fields?); `test_record_shape_is_the_current_producer_shape`
   pins the key set — mutate the backend's record writer (scratch copy) and show the test goes red.
8. **The capture tool + runner — READ, never run.** `capture_leg.py`: the key file at exactly one site, never in argv; `--config` drops
   the inline `api_key` (the test); the FIFO/symlink guards the lane added; `run_s0_04_legs.sh`: every external call enumerated;
   the reuse branch requiring a live `:20201/healthz` (class 13 fix); `bash -n`; never kills by name; the preflight refuses an unknown
   model id.
9. **The 18-class table** — re-scan the 28 files; the six fixed defects each have a red test (run them); a class the lane missed = a
   finding.
10. **The PC gate (the carve-out)**; paste beside the checkpoint's lines; agree.
11. **Mutants ≥ 26** (the lane's 16 + yours: the key permutation, the folded header, the split bearer, the wrong-model fixture, a
    bundle captured straight at the backend (`request-url-unexpected`), a leg dir that is a symlink).
12. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census.
13. **The design.** Is "canonical-bytes + wire-length" the honest name for A3 (the checker's docstring says so — does the PASS line?);
    should S0-04's mint wait for raw bytes in the backend record? Keep it to what you measured.

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-C1.md` — draft after EACH item — then return it whole. Findings: ALL, no severity
filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact red test, SOLID/UNSURE;
reproduced vs reviewed vs skipped; shared-tree hygiene; verdict MERGE-READY or NOT-READY with the blocking set, the cheapest path, and
the exact PC steps for the coordinator's three legs.
