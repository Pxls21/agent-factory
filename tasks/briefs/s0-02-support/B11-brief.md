# B11 — S0-02's four seed negative legs, so the proof can mint under the F16 floor (task #191)

PIN: 8d8c97e (the post-push SHA of local c63a3a9, B10's landing); the boundary is byte-identical at local efb4518 and at the origin head fa4532e (the boundary's blob ids are in the premise block; re-measure them first).
LANE: s0-02-b11 (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation). Honey `ultra` Lever-2: your report is
DATA: files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

WHY: S0-02 cannot mint today. The registry row sets `required_negative_controls: 4` (`proofs/registry.yaml:13`); the seed's S0-02 block
names four negative fixtures, each with its own expected reason (`seeds/seed-stage0-v1.yaml:376-380`: `denied: sender-not-in-allowlist`,
`denied: signature-invalid`, `denied: event-replayed`, `denied: event-stale`; rule "four DISTINCT reasons required; one blanket
rejection fails the proof"); and `scripts/validate-ledger:312-324` (VERIFY-B1 F16) counts the minted result's negative legs against
that floor. `proofs/S0-02/spec.json` carries ONE negative leg (the blanket bundle), so a mint today is INVALID with
`negative-controls-short: S0-02 1 negative leg(s) recorded, registry requires 4`. The other minted proofs carry their negative legs as
runs that exit 1 with a named reason (S0-06's `factory_memory.py recall … → denied: scope-tuple-unauthorized`; S0-03's four).

CONTRACT SOURCES (read them whole before you design): the seed block above · `proofs/S0-02/check_buzz_authz.py` (C: `main` `:905`,
`_check_bundle_uncapped`, `_check_leg` `:493`, `_check_replay`, `_check_named_observable`, `_check_duplicate_receipt`, the distinctness
block) · `proofs/S0-02/oracle/denial_table.py` (`SEED_REASONS` `:39`, `ROWS`, `NEGATIVE_FIXTURES` `:298`) · `proofs/S0-02/spec.json` ·
`proofs/schemas/spec.schema.json` · `scripts/validate-ledger:297-324` (the runs-spec binding and the F16 floor).

BOUNDARY (exact): MODIFY `proofs/S0-02/check_buzz_authz.py` (C), `proofs/S0-02/spec.json`, `tests/test_s0_02_buzz_authz.py` (T2);
CREATE `tasks/briefs/s0-02-support/B11-report.md` (write it incrementally from the start). READ-ONLY: `proofs/S0-02/oracle/`,
`proofs/S0-02/tools/` (the builder and the PC runner), `proofs/S0-02/fixtures/` (B10's output; regenerate nothing), `proofs/S0-01/**`
(accepted and attested), `proofs/registry.yaml`, `proofs/schemas/`, `scripts/`, `.github/`, `.claude/`. A line you cannot meet without
another file is a DISCREPANCY, never a silent edit. Other sandbox agents may work in this tree on disjoint files: never touch, run or
revert them. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push`. No outward-facing action;
no PC or bridge use; no live relay or host secret. Scratch and every pytest `--basetemp` live under `/tmp/b11/` and are removed after
use (the sandbox disk is tight).

CODE INTEL FIRST: `graft ask` before any grep for code questions; `scripts/lane_context.sh -q 'how does the S0-02 checker grade one
negative leg' -s main -s _check_leg -s _check_replay -s _check_named_observable -s _check_duplicate_receipt -o /tmp/b11/pack.md
proofs/S0-02/check_buzz_authz.py proofs/S0-02/oracle/denial_table.py tests/test_s0_02_buzz_authz.py`.

## The contract (build to it; the HOW is yours)

1. **Premise first.** Re-measure the premise block. On a mismatch in the boundary, stop CONTRACT-INVALID and report what differs.
2. **A per-fixture denial mode.** `check_buzz_authz.py [--synthetic-root <dir>] --denial <fixture> <evidence-root>`. `<fixture>` must
   be one of `oracle.NEGATIVE_FIXTURES`; anything else (including `pos-allowed`, an empty value or a missing value) is a usage refusal,
   rc 64, with the usage line naming the new flag. Without `--denial`, the checker's output and exit codes are unchanged (a regression
   test pins the pass bundle's PASS line byte for byte).
3. **One leg, fully graded.** The denial mode grades the named leg exactly as the bundle check grades it: the anchors, the root
   closure, the leg's own checks (`_check_leg`, or `_check_replay` for `neg-replayed`), and that leg's denial grading
   (`_check_named_observable`, or `_check_duplicate_receipt` for the replay). It does not require the other legs to pass: a broken
   sibling leg does not change this leg's verdict.
4. **The reason comes from the observation.** On a proven denial the mode prints `failure_reason: denied: <reason>` and exits 1, where
   `<reason>` is the reason of the oracle row that the OBSERVED denial matched, never a string chosen from the argument. Any failure of
   the leg prints that failure's own `failure_reason:` line (exit 1), and that line never contains the named leg's `denied:` text. The
   evidence-absent path stays `deferred:` rc 2.
5. **The spec's negative legs.** `proofs/S0-02/spec.json`'s `legs` list gains four entries with `"leg": "negative"`, in the seed's
   order: `cmd` `["python3", "proofs/S0-02/check_buzz_authz.py", "--denial", "<fixture>", "proofs/S0-02/evidence"]`, `cwd` `.`, the
   blanket leg's `timeout_s`, and `expect` `{"exit_code": 1, "failure_reason": "<the seed's reason>"}` for `neg-unauthorized`,
   `neg-bad-signature`, `neg-replayed` and `neg-stale`. The positive leg and the blanket leg stay as they are. The file validates against
   `proofs/schemas/spec.schema.json`.
6. **Tests (T2).** Normal, failure and boundary behavior:
   - each of the four denial runs over the synthetic pass bundle prints its seed reason, rc 1;
   - the mismatch control: plant another class's observable in one leg of a bundle copy (for example the unauthorized relay text in
     `neg-stale`); that leg's denial run must not print its own `denied:` reason;
   - the independence control: break a sibling leg in a bundle copy; the named leg's denial verdict does not change;
   - the usage refusals of item 2, each with its exact rc;
   - the floor, mirrored where the S0-02 suite sees it: the spec's negative legs are at least the registry's
     `required_negative_controls` for S0-02, and their reasons are exactly the seed's four plus the blanket reason, read from the files
     (a future spec edit that drops a leg reds here before any mint);
   - the bundle mode's PASS line on the pass bundle is unchanged, byte for byte.

## Mutants (run each on a scratch copy under `/tmp/b11/`; a mutant must compile and collect, AF-AP-78)

m1 the reason taken from the argument, not the observation · m2 the denial mode requires the whole bundle to pass · m3 a spec with
three negative legs · m4 exit 0 on a proven denial · m5 `pos-allowed` accepted by `--denial`. For each: the named T2 test that reds and
its failure line, pasted. A mutant no test kills is a finding in your report, never a silent pass.

## Gates (paste every command with its output)

- The four denial commands over the pass bundle (`--synthetic-root proofs/S0-02/fixtures/evidence-pass --denial <fixture>
  proofs/S0-02/fixtures/evidence-pass/legs`), each rc 1 with its seed reason.
- The bundle mode on the pass bundle (rc 0, the PASS line) and the spec's blanket leg verbatim (rc 1, its exact reason).
- T2 twice, counts identical: `python3 -m pytest tests/test_s0_02_buzz_authz.py -q -p no:cacheprovider --basetemp /tmp/b11/bt`
  (`mkdir -p /tmp/b11` first). The baseline at the PIN is in the premise block; the new tests add to it and no existing test is
  skipped or deleted.
- `python3 scripts/lint_delta.py` (0 new hits) and `python3 scripts/validate-ledger integrity --root .` (S0-02 ABSENT, rc 0).
- C is a listed gate file (`scripts/gate_files.txt:34`), so the never-a-gate screen reads it on every commit: add no dynamic load
  and no new import of a model package, and paste `python3 scripts/no_laya_in_gates.py` on your tree (clean, with the file count).
- `git status --short` shows only boundary paths (and the other lanes' files, which you name and do not touch).

## Report (`tasks/briefs/s0-02-support/B11-report.md`)

The premise re-measurement; every changed file with its line ranges; the mutant table; every gate pasted; DISCREPANCIES; NOT-done.
State plainly what this does NOT prove: the four legs run over the live evidence only at mint time, after the capture.

NOT IN SCOPE (report, do not build): any runner, builder, fixture or oracle change; more denial legs than the seed's four; issue #45's
rows.

## PREMISE — MEASURED at authoring (2026-09-23 14:1xZ, sandbox @ local efb4518)

```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short HEAD
2026-09-23T14:19Z
efb4518
$ blob[:12] lines path (HEAD)
7b875de37dce   936 proofs/S0-02/check_buzz_authz.py
5b061cd1303f    26 proofs/S0-02/spec.json
b9621c9d9398  3611 tests/test_s0_02_buzz_authz.py
c8c7ac11e2ba   314 proofs/S0-02/oracle/denial_table.py
1d67210b11b8   587 proofs/S0-02/tools/build_fixtures.py
7659e4bbc4c8    36 proofs/registry.yaml
136034643765    48 proofs/schemas/spec.schema.json
2210fbff942c   522 scripts/validate-ledger
$ git log --format="%h %s" -3 -- proofs/S0-02/check_buzz_authz.py proofs/S0-02/spec.json | cut -c1-100
56a8f50 B9-R1 landed (task #168): the S0-02 replay leg is graded by the relay's duplicate: receipt a
91e33f2 s0-02: B4 (round 4 fix) — the closure table derived from every runner write, the tolerance
c6c384a S0-02 round 3 LANDED (lane B3, PC Hermes lane on 887f341) — closure is containment, the re
$ grep -n (seams)
434:def _check_named_observable(leg: str, fixture_name: str, found: frozenset, delivery: dict):
493:def _check_leg(leg_dir: Path, leg: str, fixture_name: str, identities: dict, anchors: "Anchors"):
653:def _check_replay(root: Path, identities: dict, anchors: "Anchors"):
738:def _check_duplicate_receipt(found: frozenset, delivery: dict, first_id: str) -> bool:
811:def _check_bundle_uncapped(root: Path, anchors: "Anchors") -> str:
905:def main(argv) -> int:
911:                "usage: check_buzz_authz.py [--synthetic-root <dir>] <evidence-root>",
919:            "usage: check_buzz_authz.py [--synthetic-root <dir>] <evidence-root>",
39:SEED_REASONS = (
48:ROWS = (
298:NEGATIVE_FIXTURES = tuple(r["fixture"] for r in ROWS if r["leg"] == "negative")
34:proofs/S0-02/check_buzz_authz.py
13:  {"proof_id": "S0-02", "title": "Buzz authorization and freshness", "classification": "execution_proof", "wave": 1, "spike_dependencies": [], "required_nega
  assertions:
  - an allowed fresh signed event produces exactly one ACP session/turn
  - membership removal or key rotation revokes access independent of NIP-OA created_at
  - restart/duplicate delivery does not duplicate a completed turn (idempotency by event id)
  negative_control:
    fixtures:
    - {fixture: fixtures/s0-02/neg-unauthorized.json, expected_failure_reason: 'denied: sender-not-in-allowlist'}
    - {fixture: fixtures/s0-02/neg-bad-signature.json, expected_failure_reason: 'denied: signature-invalid'}
    - {fixture: fixtures/s0-02/neg-replayed.json, expected_failure_reason: 'denied: event-replayed'}
    - {fixture: fixtures/s0-02/neg-stale.json, expected_failure_reason: 'denied: event-stale'}
    rule: four DISTINCT reasons required; one blanket rejection fails the proof
  owner_placeholder: none
- proof_id: S0-03
316:            floor = proof.get("required_negative_controls")
321:                        f"negative-controls-short: {proof_id} {negatives} negative leg(s) recorded, "
$ python3 -c (spec legs)
[('positive', {'exit_code': 0}), ('negative', {'exit_code': 1, 'failure_reason': "blanket-rejection: reasons ['delivery::restricted: not a channel member'] not distinct — 6 negative legs collapsed to 1 observable(s)"})]
$ python3 proofs/S0-02/check_buzz_authz.py --denial neg-stale proofs/S0-02/fixtures/evidence-pass/legs > /tmp/b11p.out 2>&1; echo "rc=$?"; cat /tmp/b11p.out
rc=64
usage: check_buzz_authz.py [--synthetic-root <dir>] <evidence-root>
$ python3 -c (the oracle tables, proofs/S0-02/oracle/denial_table.py)
SEED_REASONS ('denied: sender-not-in-allowlist', 'denied: signature-invalid', 'denied: event-replayed', 'denied: event-stale')
NEGATIVE_FIXTURES ('neg-unauthorized', 'neg-bad-signature', 'neg-replayed', 'neg-stale', 'neg-self-authored', 'revoked', 'neg-not-allowlisted')
$ python3 -m pytest tests/test_s0_02_buzz_authz.py -q -p no:cacheprovider --basetemp /tmp/cb10/bt1 | tail -1   (14:1xZ, the same T2 bytes)
201 passed, 24 skipped in 140.17s (0:02:20)
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
$ (the spec's legs run as validate-ledger's runs-spec binding would, 14:1xZ)
positive rc 2 deferred: S0-02 evidence not captured
negative rc 1 match blanket-rejection: reasons ['delivery::restricted: not a channel member'] not distinct — 6 negative legs collapsed to 1 observable(s)
$ grep -n (seed, validator)
seeds/seed-stage0-v1.yaml:376-380 (the four fixtures and the rule, pasted in WHY)
scripts/validate-ledger:297-310 (the runs-spec binding) and :312-324 (the F16 floor; the message at :321)
```
