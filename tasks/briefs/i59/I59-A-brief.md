# I59-A: every file a proof's checker reads is attested (task #312, issue #59 F-1)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/i59/I59-A-report.md` (write it
incrementally from the start). PIN: origin 4b5434f. Plan: `tasks/issue59-batch-plan.md` (#312). Source finding: GitHub issue
#59 F-1 and its correction comment (VERIFY-S0-05, 2026-09-24).

## WHY

`proof_attestation()` hashes the trust closure (the runner, the validator, the registry), the schemas, and the proof's own
directory. A checker that loads or reads a file outside its directory grades against bytes nobody attested: change
`proofs/S0-01/pins.py` and S0-05's committed result stays PRESENT. The issue names S0-05 and S0-03; the coordinator's sweep
(premise) finds the class wider: S0-02, S0-03 and S0-05 load S0-01 files, S0-06 reads `upstream.lock.yaml`, S0-07 imports an
upstream checkout. After this change, a proof's attestation covers every repo file its verdict depends on, and a test keeps
it that way.

## CONTRACT

1. **The declaration.** A proof entry in `proofs/registry.yaml` may carry `extra_attested_inputs`: a list of repo-relative
   paths. The registry check accepts the key (today every unknown key is refused: "every registry key must bind a gate") and
   refuses, with a named `registry-schema: <id> extra_attested_inputs ...` finding: a non-list; a non-string item; an absolute
   path; a `..` segment; a glob character; a duplicate; a path inside `proofs/<id>/` or in the closure (already attested); a
   path that is not a regular file in the tree (a symlink is refused).
2. **The attestation.** `proof_attestation()` hashes the declared files beside the rest, with the same key form (the path
   relative to the root). It is the one function the runner and the validator share; both call sites keep working, and a
   proof with no declaration gets exactly today's key set. A declared file changed after a mint makes that proof INVALID; a
   declared file deleted makes it INVALID (the recorded key has no match).
3. **The declarations.** Declare, for each consumer, every repo file its checker reads while it grades, the transitive loads
   included (S0-01's checker imports `pins.py`, `check_initialize.py`, `negative_contract.py` and `tools/nostr_verify.py`).
   The premise lists what the coordinator found; your enumeration is the authority, and each difference from the premise is a
   DISCREPANCIES row. Answer the plan's open questions: does `pins.py` read a data file? Does S0-07's checker compare the
   Fubuki checkout to `upstream.lock.yaml` (then the lock is its declared input), and how does S0-07 attest code outside the
   repo at all (say what exists; do not build a new mechanism for it here)? Capture tools that only run on the PC and never
   run when the checker grades are out of scope: say which you excluded.
4. **The drift guard.** A new test fails when a proof's checker reads a repo file outside its directory and outside the
   closure that its entry does not declare. It must catch a path built at run time (a joined string, a `Path` expression), so
   a static pattern match alone is not enough: observe the reads while each checker grades its committed evidence (for
   example with a `sys.addaudithook` hook on `open` and `import` events in a subprocess), for every proof whose checker can
   run in the sandbox, and name the proofs it cannot cover and why. A negative control plants one undeclared read of each
   shape (a `spec_from_file_location` on a joined path, a `read_text` on a root-relative path, an `import` through a
   `sys.path` entry) in a scratch copy and must red.
5. **No re-mint in the tree.** The change makes every committed `result.json` stale (the validator and the registry are in
   every proof's closure). Do not write any `proofs/*/result.json`. Prove the landing instead, in a scratch worktree of the
   PIN with your changes applied: re-mint all twelve with `scripts/proof-runner --proof <id> --venue <the venue in its current
   result.json's env_fingerprint>`, then run `scripts/check-proof-status.py` (every proof PRESENT, every tag stale as
   expected) and `scripts/validate-ledger` there. End to end, in that worktree: change one byte of a declared outside input
   (`proofs/S0-01/pins.py`) and show S0-05, S0-03 and S0-02 turn INVALID while an undeclaring proof (S0-09) stays PRESENT.
   Write the exact command list the coordinator runs at landing (the re-mint, and `EXPECTED_PENDING` in
   `tests/test_proof_status.py` set to the twelve).

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Tests for items 1, 2 and 4 in the existing files' style (`tests/test_validate_ledger.py`, `tests/test_proof_runner.py`) or
   a new `tests/test_attested_inputs.py`; each refusal of item 1 by its exact finding text; a negative control reds for each
   on the PIN's code or on a named mutant (a kill is a FAILED test, never an error: AF-AP-223).
3. `bash scripts/test_summary.sh` twice on the floor's set below (13 files set=07f9aa59b430), with its set id: every red either fixed or shown to be
   the expected staleness of a committed `result.json` (name each test and the stale proof). The floor's counts are the
   PIN's.
4. Item 5's worktree run pasted: the twelve mints, the status output, the one-byte INVALID demonstration.
5. `pyflakes` rc 0 on the changed Python; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
6. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `scripts/validate-ledger`, `scripts/proof-runner` (only if its call needs to change), `proofs/registry.yaml` (the new
key on the consumers), `tests/test_validate_ledger.py`, `tests/test_proof_runner.py`. CREATE: `tests/test_attested_inputs.py`
(if you choose a new file), your report. READ everything else. NEVER write a `proofs/*/result.json` or anything else under
`proofs/` in the tree; the scratch worktree is yours.

## STANDING RULES

No git writes in this tree (a scratch worktree for item 5 is fine: `git worktree add --detach <scratch path> <PIN>`, removed
with `git worktree remove --force` when done); no PC bridge; no outward-facing action. Never read a real secret source
(`.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`, the GH_TOKEN and GITHUB_TOKEN variables). Other
lanes hold this tree: SYNTH1 (`scripts/s1_synth.py`, `tests/test_s1_synth.py`, its report), HCTX1
(`harness-ports/bin/lane-profile.sh`, `harness-ports/tests/test_lane_profile.sh`, its report), VERIFY-S1-RATE (its report),
and a stopped lane's untracked report (`tasks/briefs/system1/VERIFY-SCRUB2-report.md`): never touch their files. The disk is
shared (about 1.6G free): scratch under 300 MB in
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/i59a/`, the worktree included, deleted as you go;
a short `--basetemp`; never run the whole `tests/test_vendored_manifest.py`. Test counts pasted from `scripts/test_summary.sh`;
stamps substituted from `date -u`. Long commands in one foreground call; kill by pid only. A hook adds skill excerpts stamped
`[S1 <id> <source>]` with a score request: answer it as it asks (CLAUDE.md).

## PREMISE — MEASURED at authoring (2026-09-26 04:0xZ, the sandbox tree; HEAD's tree = origin 4b5434f)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-80
4b5434f transcripts: scrubbed sandbox chat digests (2026-09-26)
$ grep -n -E 'ATTESTATION_CLOSURE =|def proof_attestation|paths \+= ' scripts/validate-ledger
52:ATTESTATION_CLOSURE = ("scripts/proof-runner", "scripts/validate-ledger", "proofs/registry.yaml")
55:def proof_attestation(root, proof_id):
70:    paths += sorted((root / "proofs" / "schemas").glob("*.json"))
71:    paths += sorted((root / "proofs" / proof_id).rglob("*"))
$ grep -rn 'proof_attestation(' scripts/ tests/ | grep -v 'def proof_attestation' | cut -c1-110
scripts/validate-ledger:272:                current = proof_attestation(root, proof_id)
scripts/proof-runner:219:        "attestation": validator.proof_attestation(root, proof_id),
tests/test_validate_ledger.py:111:    result["attestation"] = _load_validator().proof_attestation(root, proof_
tests/test_validate_ledger.py:445:    result["attestation"] = _load_validator().proof_attestation(root, "S0-01
tests/test_validate_ledger.py:473:    result["attestation"] = _load_validator().proof_attestation(root, "S0-01
tests/test_ledger_gen.py:98:    result["attestation"] = _load_validator().proof_attestation(root, proof_id)
$ grep -n -E 'unknown key|"required_negative_controls",$' scripts/validate-ledger
172:            "required_negative_controls",
182:            findings.add(f"registry-schema: {proof_id} unknown key(s) {','.join(unknown)} — every registry key must bind a gate")
$ python3 <scratch>/xref.py   (string constants naming another proof, path-based imports of pins; comments and docstrings without a path excluded)
proofs/S0-01/check_acp_conformance.py:37: IMPORT  ['pins']
proofs/S0-01/check_acp_conformance.py:38: IMPORT pins ['ALLOWED_UPSTREAM_GET', 'ASYNC_SESSION_UPDATES', 'ENV_ALLOWLIST_KEY', 'EXPE
proofs/S0-01/check_initialize.py:36: IMPORT  ['pins']
proofs/S0-01/negative_contract.py:23: IMPORT  ['pins']
proofs/S0-01/tools/build_capture_record.py:20: IMPORT  ['pins']
proofs/S0-01/tools/pc/pc_launch.py:31: IMPORT  ['pins']
proofs/S0-01/tools/pc/pc_negative.py:14: IMPORT  ['pins']
proofs/S0-02/check_buzz_authz.py:47: STR 'S0-01'
proofs/S0-02/check_buzz_authz.py:48: STR 'S0-01'
proofs/S0-02/check_buzz_authz.py:49: STR 'S0-01'
proofs/S0-02/tools/build_fixtures.py:51: STR 'S0-01'
proofs/S0-02/tools/build_fixtures.py:56: STR 'S0-01'
proofs/S0-02/tools/pc/deliver_event.py:56: STR 'S0-01'
proofs/S0-03/check_omniroute_roundtrip.py:104: STR 'S0-01'
proofs/S0-05/check_egress.py:117: STR 'S0-01'
$ grep -rn -E 'spec_from_file_location|sys\.path\.(insert|append)|parents\[2\]|parents\[3\]' --include='*.py' proofs/ | grep -v -E '__pycache__|str\(HERE\)\)' | cut -c1-120
proofs/S0-07/check_fubuki_corrections.py:23:    sys.path.insert(0, str(fubuki_root / "src"))
proofs/S0-07/check_fubuki_corrections.py:24:    sys.path.insert(0, str(fubuki_root))
proofs/S0-01/check_acp_conformance.py:101:sys.path.insert(0, str(HERE / "tools"))
proofs/S0-01/tools/pc/pc_launch.py:30:sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", 
proofs/S0-01/tools/pc/pc_negative.py:13:sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."
proofs/S0-01/tools/pc/pc_negative.py:15:sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
proofs/S0-01/tools/build_capture_record.py:19:sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
proofs/S0-05/check_egress.py:125:    spec = importlib.util.spec_from_file_location(_PINS_MODULE, _PINS_FILE)
proofs/S0-03/check_omniroute_roundtrip.py:114:    spec = importlib.util.spec_from_file_location(_S0_01_MODULE_NAME, _S0_
proofs/S0-02/check_buzz_authz.py:51:sys.path.insert(0, str(HERE / "oracle"))
proofs/S0-02/check_buzz_authz.py:87:    spec = importlib.util.spec_from_file_location(name, path)
proofs/S0-02/tools/pc/deliver_event.py:64:    spec = importlib.util.spec_from_file_location(name, path)
proofs/S0-02/tools/build_fixtures.py:61:    spec = importlib.util.spec_from_file_location(name, path)
proofs/S0-02/tools/build_fixtures.py:205:    sys.path.insert(0, str(PROOF_DIR / "oracle"))
proofs/S0-06/fixtures/build_synthetic_bundles.py:22:ROOT = Path(__file__).resolve().parents[3]
proofs/S0-06/fixtures/build_synthetic_bundles.py:41:    spec = importlib.util.spec_from_file_location("s0_06_fixture_fac
proofs/S0-06/tools/pc/seed_scopes.py:35:FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
proofs/S0-06/check_four_scope.py:60:REPO_ROOT = Path(__file__).resolve().parents[2]
$ grep -n -E 'REPO_ROOT / ' proofs/S0-06/check_four_scope.py
213:        text = (REPO_ROOT / "upstream.lock.yaml").read_text(encoding="utf-8")
$ each result.json: env_fingerprint, attested-file count
S0-01 pc-bridge:vm 247
S0-02 pc-bridge:vm 208
S0-03 sandbox:vm 91
S0-04 sandbox:vm 44
S0-05 pc-bridge:vm 62
S0-06 sandbox:vm 166
S0-07 sandbox:vm 14
S0-08 sandbox:vm 29
S0-09 sandbox:vm 11
S0-10 sandbox:vm 11
S0-11 sandbox:vm 13
S0-12 sandbox:vm 14
$ bash scripts/test_summary.sh tests/test_validate_ledger.py tests/test_proof_runner.py tests/test_proof_status.py tests/test_ledger_gen.py tests/test_no_laya_in_gates.py tests/test_s0_01_spec_runner.py tests/test_s0_02_buzz_authz.py tests/test_s0_03_omniroute.py tests/test_s0_08_containment.py tests/test_s0_11_eval_hardening.py tests/test_s0_05_egress.py tests/test_s0_06_four_scope.py  tests/test_system1_context.py   (the floor at the PIN, run 04:00-04:09Z)
pytest-exit: 0
pytest-summary: 1527 passed in 503.63s (0:08:23)
$ bash scripts/pc_suite.sh set-id -- <the same 13 files>
13 files set=07f9aa59b430
```

A question for you, not a fact: S0-02's `tools/build_fixtures.py` and `tools/pc/deliver_event.py` also load S0-01 files. Do
they run when S0-02's checker grades, or only when its evidence is built? The answer decides whether they count.
