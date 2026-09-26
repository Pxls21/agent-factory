# I59-A report: every file a proof's checker reads is attested (task #312, issue #59 F-1)

Lane: code-implementer (sandbox, Opus 5.5). Brief: `tasks/briefs/i59/I59-A-brief.md` (PIN origin 4b5434f).
Started 2026-09-26 04:3xZ. Written incrementally; the sections below fill as the work lands.

## 0. Premise check (evidence demand 1)

- Tree: HEAD 1a69a94; `git diff --name-only 4b5434f HEAD` over the boundary (validate-ledger, proof-runner, proofs/,
  the five test files, check-proof-status.py) prints nothing. Only harness-ports files (HCTX1) and docs changed. VERIFIED.
- The premise block's greps (ATTESTATION_CLOSURE line 52, proof_attestation line 55, paths += lines 70-71, the six
  proof_attestation call sites, the unknown-key rule lines 172/182, the spec_from_file_location / sys.path / parents[N]
  sweep, S0-06's REPO_ROOT read at line 213, the twelve env_fingerprints and attested-file counts): re-run at HEAD,
  every line identical. VERIFIED.
- Verdict: premise HOLDS. Not CONTRACT-INVALID.

## 1. The enumeration (contract item 3; the drift guard's instrument, measured 04:4xZ)

Instrument: every spec leg of every proof run as the runner runs it (the literal command, the runner's clean
environment PATH/HOME/LANG plus the leg's env), with a `sys.addaudithook` hook loaded through a `sitecustomize` on
`PYTHONPATH`, a fresh empty `PYTHONPYCACHEPREFIX` and `PYTHONDONTWRITEBYTECODE=1` (so every import opens its source).
Recorded: `open` events (path, any mode) and `exec` events (the code object's `co_filename`), resolved against the
repo root; kept: repo files outside `proofs/<id>/` and outside the closure. Every leg's exit code equalled its spec's.

| Proof | Outside repo reads while grading (measured) | Premise said | Row |
|---|---|---|---|
| S0-01 | none | (not a consumer) | agrees |
| S0-02 | `proofs/S0-01/check_acp_conformance.py`, `check_initialize.py`, `negative_contract.py`, `pins.py`, `tools/nostr_verify.py`, `fixtures/identities.json` | the same six | agrees |
| S0-03 | `proofs/S0-01/check_acp_conformance.py`, `check_initialize.py`, `negative_contract.py`, `pins.py`, `tools/nostr_verify.py` | the same five | agrees |
| S0-04 | none | - | agrees |
| S0-05 | `proofs/S0-01/pins.py` | the same | agrees |
| S0-06 | `upstream.lock.yaml`, `fixtures/s0-06/neg-unauthorized-tuple.json` | `upstream.lock.yaml` only | DISCREPANCY D1 |
| S0-07 | none in the repo (reads the Fubuki checkout outside the repo) | "imports an upstream checkout" | agrees; see Q3 |
| S0-08 | none | - | agrees |
| S0-09 | `docs/adr/0005-foundry-host.md` | none ("an undeclaring proof") | DISCREPANCY D2 |
| S0-10 | `docs/adr/0006-gbrain-seam.md` | none | DISCREPANCY D3 |
| S0-11 | none observed; two child kinds unobserved (see the guard's coverage) | - | agrees |
| S0-12 | `SBOM.yaml`, `upstream.lock.yaml` | none | DISCREPANCY D4 |

Answers to the plan's open questions:
- Q1 `pins.py` reads no data file. In the S0-05 run the only S0-01 file opened is `pins.py` itself; in the S0-03 run
  only the five S0-01 modules are opened. S0-02 opens `proofs/S0-01/fixtures/identities.json` from its own checker
  (`check_buzz_authz.py:47-49`, `S0_01_CHECKER`, `NOSTR_VERIFY`, `IDENTITIES`), not through `pins.py`.
- Q2 (the brief's S0-02 question): `tools/build_fixtures.py` and `tools/pc/deliver_event.py` do NOT run while S0-02
  grades. Measured: the modules executed while S0-02's six legs grade are `check_buzz_authz.py`,
  `oracle/denial_table.py` and the five S0-01 modules; no process was spawned. They build evidence (fixtures, the PC
  delivery), so they are out of scope.
- Q3 S0-07: its checker does NOT compare the checkout to `upstream.lock.yaml` (no read of the lock observed; the code
  checks only that `<root>/src/fubuki_os` is a directory, `check_fubuki_corrections.py:217`, `fubuki_root`). So the lock is not its
  declared input. What exists for code outside the repo: `upstream.lock.yaml` pins fubuki-os at 7375e56d;
  `scripts/fubuki_pin_sync.sh` provisions and verifies a pinned checkout for the governance TESTS; and
  `src/agent_factory/governance/pin.py:67` (`verify_pinned_fubuki`) verifies a checkout against the lock
  for the Stage 3 core. None of them binds S0-07's verdict: S0-07 attests no byte of the Fubuki code it grades
  against. The local checkout happens to be at the lock's commit (HEAD 7375e56d, clean). No new mechanism built here
  (the brief). Follow-up named in NOT-done.
- Excluded capture tools (never run while a checker grades; measured by the executed-module list above and by
  zero spawns outside S0-11): S0-01 `tools/build_capture_record.py`, `tools/pc/pc_launch.py`, `tools/pc/pc_negative.py`;
  S0-02 `tools/build_fixtures.py`, `tools/pc/deliver_event.py`; S0-06 `fixtures/build_synthetic_bundles.py`,
  `tools/pc/seed_scopes.py`, `tools/pc/run_s0_06_legs.sh`. All sit inside their own proof directory (attested with it).

## 2. The change (contract items 1, 2 and 3; landed in the tree 04:5xZ, uncommitted)

`scripts/validate-ledger`:
- `_read_registry(root)`: the one comment-stripping parser, now used by `_registry` and by the attestation (so the
  check and the hash read the same declarations). Extracted from `_registry`'s first lines, behaviour unchanged.
- `_extra_inputs(proof)`: splits an entry's `extra_attested_inputs` into attestable paths and one named finding per
  refused item (texts in section 3).
- `_is_regular_file(root, rel)`: `is_file()` and `resolve()` equal to `root.resolve()/rel` (a symlink at any step
  below the root resolves elsewhere, so it is refused).
- `_declared_inputs(root, proof_id)`: the entry's attestable paths; none when the registry is absent or unreadable
  (the registry check names why).
- `proof_attestation`: after today's loop, hashes each declared regular file under its root-relative path. The
  signature is unchanged, so both call sites (`_artifact_states`, `scripts/proof-runner:219` `proof_attestation`) and the three test
  helpers keep working with no edit. `scripts/proof-runner` is NOT modified.
- `_registry`: the key joins the closed key set; each refusal is added; a declared path that EXISTS as anything but
  a regular file (a symlink, a directory, a path through a symlinked directory) is refused.
- `_artifact_states`: a result whose declared input is not a regular file in the tree is INVALID with the same
  finding. This is where an ABSENT declared path is refused (deviation X1, section 9).

`proofs/registry.yaml`: `extra_attested_inputs` on S0-02, S0-03, S0-05, S0-06, S0-09, S0-10, S0-12 (sorted lists,
the section 1 table). S0-01, S0-04, S0-07, S0-08, S0-11 declare nothing.

Measured on the tree after the edit (pasted):
- `pyflakes scripts/validate-ledger` rc 0.
- `validate-ledger integrity --root . --ledger proofs/ledger.json`: all twelve INVALID, each by one
  `attestation-mismatch` (the expected staleness: the validator and the registry are in every closure), plus twelve
  `ledger-drift`; no `extra_attested_inputs` finding (every declared file is a regular file). rc 1.
- Key-set diff, recorded attestation vs recomputed, per proof: S0-01, S0-04, S0-07, S0-08, S0-11 unchanged sets
  (247, 44, 14, 29, 13 keys), only `proofs/registry.yaml` and `scripts/validate-ledger` hashes changed; S0-02
  208 -> 214, S0-03 91 -> 96, S0-05 62 -> 63, S0-06 166 -> 168, S0-09 11 -> 12, S0-10 11 -> 12, S0-12 14 -> 16, each
  adding exactly its declared paths, none removed.

## 3. The tests (evidence demand 2; written 05:0xZ)

New file `tests/test_attested_inputs.py` (61 tests). Two edits in `tests/test_validate_ledger.py`:
`test_result_with_fewer_negative_legs_than_the_registry_floor_is_invalid` copies S0-02's declared S0-01 files into its
minimal root (S0-02 is PRESENT only with them in the tree); `test_registry_rows_carry_no_key_the_validator_does_not_read`
lists the new key in its closed set. `tests/test_proof_runner.py` needs no change (its 11 tests pass as they are).

Item 1, the registry key, each refusal by its exact whole-line finding (`registry-schema: S0-05 extra_attested_inputs ...`):
`must be a non-empty list of paths` (a string, an empty list), `item 0 is not a string`, `<p> is absolute`,
`<p> has a .. segment`, `<p> has a glob character` (`*`, `?`, `[`), `<p> is not in canonical form` (`./x`, `a//b`),
`<p> is a duplicate`, `<p> is inside proofs/S0-05/ (already attested)`, `<p> is in the attestation closure (already
attested)` (a closure script, a schema), `<p> is not a regular file` (a symlink, a directory, a path through a
symlinked directory, a dangling symlink). Positive controls: a declared regular file is no finding (rc 0); the committed
registry's seven declarations raise no finding.

Item 2, the attestation: over the real tree, `proof_attestation` equals an independent derivation (os.walk, the
registry read in the test) for all twelve proofs; a one-byte change to a declared file turns its proof INVALID with
`attestation-mismatch: S0-05 docs/input.md` while an undeclaring proof (S0-04) stays PRESENT; a deleted declared file
is INVALID (the mismatch and `... is not a regular file`); a result minted while its declared file was absent is
INVALID (`... is not a regular file`, no mismatch); a declared symlink to a file outside the root is never hashed; the
canonical runner (`scripts/proof-runner run`) records the declared file and a one-byte change invalidates the mint.

Item 4, the drift guard: `test_every_repo_file_a_checker_reads_is_attested[S0-01..S0-12]` runs every leg with the
audit hook and requires (a) each leg's spec exit code, (b) each leg's own script observed (the hook fired), (c) every
repo file read outside the proof's directory in its attestation, (d) every file read inside it attested too, bar the
pinned `KNOWN_UNATTESTED_INSIDE` (A1), (e) no child process unless the proof is named in `UNOBSERVED_CHILDREN` (S0-11).
Skips, by name only: a leg that exits 2 (the runner's defer signal) or a leg argument that is an absolute path the
venue lacks. Negative controls, in a scratch copy of S0-09 with every planted target present and precompiled: one
undeclared read of each shape (`spec_from_file_location` on an `os.path.join`, `read_text` on a `Path.parents[2]`
expression, `import` through a `sys.path.insert`) reds naming exactly that path; the same read declared passes (the
de-vacuousing pair); plus an in-directory fixture named `result.json`, a leg that dies before grading, an unnamed
child process, a hook that saw nothing, and the two skip helpers.

Red on the PIN's code (the new file copied alone into a worktree of 4b5434f): `40 failed, 18 passed in 25.33s`; every
failure an AssertionError at its assertion, except two KeyErrors (`recorded["docs/input.md"]`), since rewritten as
`.get(...)` assertions. The guard reds on exactly the seven consumers, each naming exactly the section 1 paths. The 18
that pass on the PIN are the twelve attestation-equality tests (no declaration on the PIN: the invariant holds), five
real-tree guard tests (S0-01, S0-04, S0-07, S0-08, S0-11) and the did-not-grade control (since pinned to the planted exit
code 3).

Mutation (the scratch harness `scratchpad/i59a/mutate.py`, in the worktree with the change applied; AF-AP-223 rules:
the unmutated control first, every mutant compiled, a kill is every named test FAILED with no ERROR, a literal
denominator, each file restored and hash-checked):
```
CONTROL (unmutated, 39 named tests): rc=0 39 passed in 8.18s
EXPECTED=26 KILLED=26 SURVIVED=0 INVALID=0
```
Validator mutants V1a-V14 (each refusal clause, the registry-level and verdict-level regular-file checks, the resolve
comparison, the extras loop, the key allowance) and guard mutants G1-G10 (hook never installed, each assertion off, the
own-artifact exemption, the bytecode prefix, both skip helpers widened). Two first attempts were refused by the
harness's own checks before any verdict: the denominator self-check (25 vs 26, my miscount) and the control run
(`36 errors`: `--basetemp`'s parent did not exist, AF-AP-223's exact scenario).
Removed as untested redundancy after this pass showed it: the hook's `exec` branch (the empty bytecode prefix makes
every import open its source; 60 passed without it), `_is_regular_file`'s `not is_symlink()` (subsumed by the resolve
comparison), `PYTHONDONTWRITEBYTECODE` in the guard (a per-leg empty prefix already forces the source read).

## 4. Item 5: the landing proven in a scratch worktree (scratch file times 05:03:45Z to 05:39:22Z; written 05:4xZ)

Worktree of the PIN (`git worktree add --detach <path> 4b5434f`) with the four changed files copied in, each
sha256-identical to the tree (b8957b28 validate-ledger, ad9a8d77 registry, dae0cd1c test_validate_ledger, f1beacdf
test_attested_inputs; re-hashed after the restart, unchanged). Location: `/tmp/i59a-wt/wt`, not the scratchpad
(deviation X4). 214 MB, removed with `git worktree remove --force`.

The re-mint, `python3 scripts/proof-runner run --proof <id> --venue <recorded venue> --root .` (pasted):
```
S0-01 venue=pc-bridge rc=0 attested=247      S0-07 venue=sandbox rc=0 attested=14
S0-02 venue=pc-bridge rc=0 attested=214      S0-08 venue=sandbox rc=0 attested=29
S0-03 venue=sandbox rc=0 attested=96         S0-09 venue=sandbox rc=0 attested=12
S0-04 venue=sandbox rc=0 attested=44         S0-10 venue=sandbox rc=0 attested=12
S0-05 venue=pc-bridge rc=0 attested=63       S0-11 venue=sandbox rc=0 attested=13
S0-06 venue=sandbox rc=0 attested=168        S0-12 venue=sandbox rc=0 attested=16
```
Then, in the worktree (pasted):
- `validate-ledger integrity --root . --ledger proofs/ledger.json`: S0-01 ... S0-12 PRESENT, `conformance_checked_decision
  numerator=3 denominator=3`, `execution_proof numerator=9 denominator=9`, rc=0.
- `validate-ledger stage1-gate --root .`: rc=0.
- `check-proof-status.py .`: twelve lines `proof-status: S0-NN: the minted proofs/S0-NN/result.json changed since
  accepted/S0-NN (regenerated after acceptance) — re-accept with a new signed tag (AF-AP-56)`, rc=1. Every tag stale,
  as expected.
- Old vs new runs (leg, exit, stdout/stderr sha256, failure_reason, cmd): identical for 11 proofs. S0-07's positive
  stdout sha256 differs (committed 87cac7a8..., worktree 9f6f6d90...): its checker prints absolute fixture paths. The
  same leg run read-only in the main tree gives 87cac7a832176d52..., the committed value. Same verdict (A3).
- `ledger-gen --root .`: `proofs/ledger.json | 24 ++++++++++++------------` (the twelve normalized digests); a second run
  byte-identical; integrity with it rc=0. Digests old -> new (first 12 hex): S0-01 6aec5f91144e -> 96ca6cb45aef,
  S0-02 33bc63f3564e -> 9eb5fca0bbbc, S0-03 249b4b3808d5 -> be2bce851248, S0-04 7daeba65ace3 -> 1dcf65754c3d,
  S0-05 f753754f2c6f -> 1da86182088a, S0-06 c09aed66e8f1 -> 81adcbffc673, S0-07 d2a31be15a58 -> 551f0821e9e6 (path
  dependent, A3), S0-08 c73ccdf454ff -> 4559ad1f7c35, S0-09 7cd77bc1bcf5 -> 6059c896bb07, S0-10 2052e3eb2494 ->
  5a033b98f09e, S0-11 ed25e4a5ed7a -> 84fa02245184, S0-12 e547bf539d55 -> 4ebc589d1798. They hold only for this
  change alone: #313 and #314 change S0-05's and S0-04's files, so those two will differ at the batch landing.

End to end, one byte of the worktree's `proofs/S0-01/pins.py` (byte 1190, `-` to `X`, `cmp -l` 1 byte), then
`validate-ledger integrity --root . --ledger proofs/ledger.json` (pasted):
```
S0-01 INVALID / S0-02 INVALID / S0-03 INVALID / S0-04 PRESENT / S0-05 INVALID / S0-06 PRESENT / S0-07 PRESENT
S0-08 PRESENT / S0-09 PRESENT / S0-10 PRESENT / S0-11 PRESENT / S0-12 PRESENT
execution_proof numerator=5 denominator=9
attestation-mismatch: S0-01 proofs/S0-01/pins.py
attestation-mismatch: S0-02 proofs/S0-01/pins.py
attestation-mismatch: S0-03 proofs/S0-01/pins.py
attestation-mismatch: S0-05 proofs/S0-01/pins.py
rc=1          (restored byte-identical: all twelve PRESENT again)
```
S0-01 turns INVALID too (its own file). S0-09, which declares its ADR but not `pins.py`, stays PRESENT, as do the
other seven. The "before" half, the same byte on the PIN's own code and committed results (a `git archive` of
4b5434f in scratch, 38 MB, removed): only `S0-01 INVALID`, and S0-02, S0-03, S0-05, S0-09 PRESENT. That is issue #59
F-1 as filed, reproduced.

The tests on the re-minted worktree:
```
4 files set=379203742124  (test_validate_ledger, test_proof_status, test_s0_11_eval_hardening, test_attested_inputs)
pytest-summary: 3 failed, 170 passed in 43.21s
10 files set=c25c3d0a0bbc (the other ten floor files)
pytest-summary: 1415 passed in 492.63s (0:08:12)
```
The 3 are all in `tests/test_proof_status.py` and all read `check-proof-status.py` rc 1 (the stale tags):
`test_the_committed_tasklist_passes` (:82), `test_committed_state_passes_status_and_ledger` (:94),
`test_committed_tree_anchor_state_is_the_declared_pending_one` (:482). The landing's anchor step resolves them, and
it could not run in the worktree, which shares the main repo's `refs/tags/accepted/*` (a `git tag -d` there would
delete the owner's local refs). So it was dry-run in a no-tags clone (deviation X5): `git clone --no-tags --shared
--no-checkout` of this repo, checkout 4b5434f, the four files and the 13 re-minted artifacts copied in
(sha256-identical to the worktree's), then the anchor step below (section 5, steps 3 and 4). Pasted:
```
check-proof-status.py .: twelve `proof-status: WARNING S0-NN: ACCEPTED with the anchor PENDING the owner's signed
                          tag accepted/S0-NN (declared in the ledger) ...` lines, rc=0
4 files set=379203742124  pytest-summary: 173 passed in 42.49s
1 files set=65d0b153796b  (test_system1_context.py, the one floor file that names BUILD-TASKLIST)
                          pytest-summary: 141 passed in 32.89s
validate-ledger integrity --root . --ledger proofs/ledger.json: rc=0; stage1-gate: rc=0;
ledger-gen reproduces the re-minted ledger byte for byte
```
The landing state is green over the floor set and the new file: 173 + 1415 tests. The remaining ten floor files
read neither the tag objects nor the task ledger (grep), so the worktree run of those ten stands for it.

## 5. The landing command list (for the coordinator)

Run in the tree, in the sandbox, as root, AFTER #312-#314 are applied and verified (the plan's #315). Why this
venue: S0-07's spec grades `/home/user/nerdherderdani/fubuki-os` (present here, absent on CI), and S0-11's positive
legs need root and `nsenter` (a non-root runner defers with exit 2 and PRESERVES the stale result, which then stays
INVALID). The tree is world-traversable (S0-11's uid 65534 child reads its fixtures). A failing leg DELETES that
proof's `result.json` by design: stop at the first failure and restore it with `git checkout -- proofs/<id>/result.json`.
```bash
cd /home/user/agent-factory
export PYTHONDONTWRITEBYTECODE=1
# 1. The re-mint (the venue label each current result.json records):
for id in S0-01 S0-02 S0-05; do python3 scripts/proof-runner run --proof $id --venue pc-bridge --root . || { echo "FAILED $id"; break; }; done
for id in S0-03 S0-04 S0-06 S0-07 S0-08 S0-09 S0-10 S0-11 S0-12; do python3 scripts/proof-runner run --proof $id --venue sandbox --root . || { echo "FAILED $id"; break; }; done
# 2. The recipe's gates:
python3 scripts/validate-ledger integrity --root .                              # 12 PRESENT, execution_proof 9/9, conformance 3/3, rc 0
python3 scripts/ledger-gen --root .                                             # the twelve normalized digests change
cp proofs/ledger.json /tmp/ledger.1 && python3 scripts/ledger-gen --root . && cmp proofs/ledger.json /tmp/ledger.1   # idempotent
python3 scripts/validate-ledger integrity --root . --ledger proofs/ledger.json  # rc 0
python3 scripts/validate-ledger stage1-gate --root .                            # rc 0
# 3. The anchors go PENDING (the S0-04 precedent, 1f764fe): the tag objects leave the tree, the local refs go
for n in 01 02 03 04 05 06 07 08 09 10 11 12; do git rm -q docs/governance/tags/accepted-S0-$n.tag; git tag -d accepted/S0-$n; done
#    and todo/BUILD-TASKLIST.md gains, directly under each `PROOF-STATUS: S0-NN = ACCEPTED` line:
#    PROOF-ANCHOR: S0-NN = PENDING-OWNER-TAG (requested <date> — the owner's GPG-signed tag `accepted/S0-NN` on a commit
#    holding the re-minted proofs/S0-NN/result.json (the issue #59 batch) makes this acceptance owner-verifiable again;
#    procedure in docs/governance/README.md; check-proof-status.py reports this state as a WARNING, never as verified)
# 4. tests/test_proof_status.py: EXPECTED_PENDING = {"S0-01", "S0-02", "S0-03", "S0-04", "S0-05", "S0-06", "S0-07",
#    "S0-08", "S0-09", "S0-10", "S0-11", "S0-12"} (its comment: re-minted by the issue #59 batch, waiting for the re-sign)
# 5. python3 scripts/check-proof-status.py .                                    # rc 0, twelve WARNING lines, nothing else
# 6. The gate, twice: the floor set (13 files set=07f9aa59b430) plus tests/test_attested_inputs.py
```
The owner's re-sign then reverses steps 3 and 4 (tag objects committed, PENDING lines removed, `EXPECTED_PENDING`
empty), as d00455f did for S0-04.

## 6. The gate in the tree (evidence demand 3)

Floor set, `bash scripts/test_summary.sh --basetemp=<short> <13 files>` (13 files set=07f9aa59b430), pasted:
```
run 1: pytest-exit: 1  pytest-summary: 5 failed, 1522 passed in 510.65s (0:08:30)
run 2: pytest-exit: 1  pytest-summary: 5 failed, 1522 passed in 517.79s (0:08:37)
```
The PIN's floor is 1527 passed. Here 1522 + 5 = 1527: the same tests, the same five red in both runs. Each red is the
expected staleness of the committed `result.json` files (the validator and the registry are in every proof's closure,
so all twelve read `attestation-mismatch`), and each passes on the re-minted worktree (section 4):
1. `tests/test_validate_ledger.py::test_registry_rows_carry_no_key_the_validator_does_not_read` (:573), integrity on
   the real root rc 1: all twelve stale (S0-01..S0-12).
2. `tests/test_validate_ledger.py::test_committed_pc_bridge_spike_validates_and_declares_all_effects` (:592), the same.
3. `tests/test_proof_status.py::test_committed_state_passes_status_and_ledger` (:95), ledger integrity rc 1 (S0-11
   among the twelve). On the re-minted worktree it moves to :94 (the stale tags) and passes after the anchor step.
4. `tests/test_s0_11_eval_hardening.py::test_attestation_binds_artifact_to_source` (:153): `S0-11 PRESENT` absent in
   its proofs+scripts copy (S0-11 stale).
5. `tests/test_s0_11_eval_hardening.py::test_tooling_mutation_breaks_attestation` (:197), the same.

New file, `bash scripts/test_summary.sh --basetemp=<short> tests/test_attested_inputs.py` (1 files set=96d60da64331):
```
run 1: pytest-exit: 0  pytest-summary: 61 passed in 27.43s
run 2: pytest-exit: 0  pytest-summary: 61 passed in 27.73s
```

Evidence demand 5: `python3 -m pyflakes scripts/validate-ledger tests/test_validate_ledger.py tests/test_attested_inputs.py
scripts/proof-runner` rc=0. `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` prints 0 for `scripts/validate-ledger`,
`proofs/registry.yaml`, `tests/test_validate_ledger.py`, `tests/test_attested_inputs.py` and this report. The whole-file
screen, `scripts/ap_screen.py`: on the validator, AF-AP-40 x3 (pre-existing `_artifact_states` branches) and AP-32 x3 (two
pre-existing lines and my extras hash, which hashes exactly as the pre-existing line above it, one function serving the
store and the check); on the tests (`--tests`), AP-70 x2 (the audit hook's `except Exception: pass`, deliberate: a
raising audit hook fails the audited call; guarded by the own-script assertion, G7) and AF-AP-80 x1 (a pre-existing
line).
`scripts/report_lint.py` over this report (short names mapped to their paths): `report_lint: 5 refs — OK 5, NEAR 0,
MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`, rc 0.

Files touched (hunks at the working tree; the counts are corrected in section 15): `scripts/validate-ledger` +117/-18 (import line 8; `_read_registry` 56,
`_extra_inputs` 66, `_is_regular_file` 106, `_declared_inputs` 114, `proof_attestation` 127-160, `_registry` 163-166
and the key rule and extras check at 256-258 and 285-294, `_artifact_states` 368-374). `proofs/registry.yaml` 7 lines (the
S0-02, S0-03, S0-05, S0-06, S0-09, S0-10, S0-12 rows). `tests/test_validate_ledger.py` +5 at 500, +1 at 567. New:
`tests/test_attested_inputs.py` (606 lines, 61 tests), this report. `scripts/proof-runner` and
`tests/test_proof_runner.py` unchanged.

## 7. NOT done

- N1. No `proofs/*/result.json`, `proofs/ledger.json`, tag object or ledger line written in the tree. The re-mint and
  the anchor step are the coordinator's landing (section 5).
- N2. (RESOLVED in round 2, section 15.) A1 not fixed: `proof_attestation` still drops fixture files named `result.json` or `blocked.json`. Pinned in
  `KNOWN_UNATTESTED_INSIDE`. The fix narrows the filter to `proofs/<id>/result.json` and `proofs/<id>/blocked.json`. It
  changes S0-08's key set (29 to 30), so it can ride this batch's re-mint if the coordinator adds it before landing;
  the pinned entry then goes in the same change (the guard reds until it does).
- N3. S0-07's outside code (the Fubuki checkout) is attested by nothing. No mechanism built (the brief). Options: the
  checker verifies its checkout with `verify_pinned_fubuki` against `upstream.lock.yaml` (the lock then becomes its
  declared input), or its spec grades `$FUBUKI_OS_ROOT` from `scripts/fubuki_pin_sync.sh`.
- N4. The guard's blind spots, named in the test: children that do not load the hook (S0-11's isolated rubric
  children, whose allow-listed environment drops PYTHONPATH), non-Python children, a verdict that rests on a stat or a
  directory listing, reads outside the repo root.
- N5. CI: the guard skips S0-07 there (its checkout path is absent) and S0-11 (non-root: its legs defer with exit 2).
  Emulated here by running every leg as uid 65534 (S0-11 legs 0 and 2: `isolation-capability-unavailable:
  nsenter-unavailable`, exit 2; every other proof graded). Not run on CI.
- N6. Not run: the whole `tests/` suite, `tests/red/*` (collected by CI; they copy `proofs/` and assert rc 1 plus
  substrings, so extra findings cannot break them: reasoned, not run), the PC suite.
- N7. GitNexus `impact proof_attestation`: "Target not found", risk UNKNOWN (the suffix-less script is not indexed).
  Callers confirmed by a literal sweep (the two call sites and three test helpers). `detect_changes` not run: I made
  no commit.
- N8. A2 (S0-11 re-reads its previous result) unchanged.

## 8. DISCREPANCIES (premise and brief vs measured)

- D1. S0-06 also reads the root-level `fixtures/s0-06/neg-unauthorized-tuple.json` (its negative leg's
  `--tuple-file`). The premise listed only `upstream.lock.yaml`. Declared.
- D2. S0-09 is not undeclaring: its positive leg grades `docs/adr/0005-foundry-host.md`. Declared. It still serves as
  item 5's control: it does not declare `pins.py` and stays PRESENT.
- D3. S0-10 grades `docs/adr/0006-gbrain-seam.md`. Declared.
- D4. S0-12 reads `SBOM.yaml` and `upstream.lock.yaml`. Declared.
- D5. S0-07 reads no repo file outside its directory and never reads `upstream.lock.yaml`. Nothing declared (Q3).
- D6. The premise says HEAD's tree equalled origin 4b5434f at authoring. HEAD then carried docs-only commits
  (c29063e..331a20c). My boundary was unaffected (diff empty).
- D7. S0-08 and S0-11 read files inside their own directories that their attestations do not cover (A1, A2). The
  premise had no in-directory class.
- D8. Item 5's "`check-proof-status.py` (every tag stale)" and "`EXPECTED_PENDING` set to the twelve" are not enough
  alone. Measured: `test_proof_status.py` needs the full S0-04 procedure (tag objects out of the tree, local refs
  deleted, PENDING lines, `EXPECTED_PENDING`) before its three committed-state tests pass. Section 5 carries it all.

## 9. Deviations from the brief (loud)

- X1. An ABSENT declared path is refused where it binds a verdict: a proof with a `result.json` is INVALID with
  `... is not a regular file`. The registry check alone refuses it only when the path exists as a non-regular file
  (a symlink, a directory, a path through a symlinked directory). Why: `tests/test_ledger_gen.py::test_validates_with_integrity`
  (outside my boundary) copies the real registry into a minimal root and expects integrity rc 0; an unconditional
  refusal reds it. The closure already sets the precedent (an absent closure file is skipped). In the real tree every
  proof has a result, so every absent declared path is refused there.
- X2. Two refusals the brief does not list: an empty list (it shares the non-list finding, "must be a non-empty list
  of paths"), and a non-canonical spelling ("is not in canonical form": `./x`, `a//b`, `a/./b`, a trailing `/`, the
  empty string). One spelling per file keeps the duplicate, own-directory and closure checks exact.
- X3. The guard is stricter than item 4's minimum. Every file read must be in the attestation, inside the proof's
  directory too, minus two named carve-outs: the proof's own two artifacts, and the pinned `KNOWN_UNATTESTED_INSIDE`
  (S0-08, A1; gone in round 2, section 15). It also refuses unnamed child processes (`UNOBSERVED_CHILDREN` = S0-11).
- X4. The worktree was not under the scratchpad: `/tmp/claude-0` is mode 700, so S0-11's uid 65534 child cannot
  traverse it and its re-mint would fail (deleting that result). It lived at `/tmp/i59a-wt/wt` (755), 214 MB, removed.
  The pytest basetemps sat there too (the scratchpad path is too long for the gpg-agent sockets of `test_proof_status.py`).
- X5. A second scratch copy: a no-tags `git clone --shared` at the PIN (about 200 MB, removed) for the anchor step's
  dry run. It read this repo's objects and wrote nothing to this tree.
- X6. `_read_registry` extracted from `_registry` (a small in-file refactor), so the registry check and the attestation
  share one parser.

## 10. Adjacent defects and observations (reported, not fixed)

- A1. (FIXED in round 2, section 15.) `proof_attestation`'s name filter drops every file named `result.json` or `blocked.json` under the proof's
  directory, fixtures included. `proofs/S0-08/fixtures/malformed-marker/blocked.json` (the only such tracked file) is
  graded by S0-08's `marker_gate.py` leg and is not attested: a change to it leaves S0-08 PRESENT. Found by the guard's
  first run.
- A2. S0-11's `check_forbidden_ops` (`proofs/S0-11/check_eval_hardening.py:534`) reads every non-`.md` file of its
  directory, the previous `result.json` included, so each re-mint reads the result it replaces. Benign today.
- A3. S0-07's positive leg prints absolute paths, so its recorded `stdout_sha256` and its ledger digest depend on the
  checkout directory. Same verdict everywhere.
- A4. `tests/test_s0_11_eval_hardening.py::_repo_copy()` copies only `proofs/` and `scripts/`. After this change S0-06,
  S0-09, S0-10 and S0-12 read INVALID in such a copy (their declared inputs live outside). The S0-11 tests assert only
  S0-11 and pass. Any other tool that validates a proofs+scripts copy will see those four INVALID.

## 11. Self-attack: the three most likely ways this is wrong

1. The guard misses a real read, so its green is hollow. Ruled out by: the own-script assertion (the hook must see
   each leg's own script; the dead-hook control, G7 killed); three planted shapes, each red with exactly its path and
   green once declared (G2 killed); the bytecode prefix proven needed (G8 killed on precompiled planted modules); the
   exit-code check (G3 killed); the PIN red on exactly the seven consumers with exactly the measured paths. The residual
   is N4, named in the test.
2. X1 opens a hole: a result minted without its declared input stays PRESENT. Ruled out: `_artifact_states` refuses
   any result whose declared input is not a regular file (its test; V12 killed). In the real tree all twelve have
   results.
3. The change moves the attestation of undeclaring proofs, or breaks the runner's call site. Ruled out: an independent
   os.walk derivation equals `proof_attestation` for all twelve proofs on the real tree; the re-mint's key counts for
   S0-01, S0-04, S0-07, S0-08, S0-11 equal the committed ones (247, 44, 14, 29, 13); a real `scripts/proof-runner run`
   records the declared file (its test); the runner is unmodified and its 11 tests pass. A fourth: a declaration
   escaping the root. `root / "/abs"` would escape, and the absolute refusal (V3), the resolve check (V11) and the
   never-hashed-through-a-symlink test each close a path.

## 12. Evidence tiers

- VERIFIED (run here, output pasted): the premise; the enumeration; the key-set diff; 61 new tests; the PIN reds;
  mutation 26/26 with a passing control; the floor twice; the new file twice; the worktree re-mint and its gates; the
  one-byte demo and its PIN "before"; the anchor-step dry run; the six-file identity after the restart.
- INFERRED: CI's skips of S0-07 and S0-11 (from the uid 65534 emulation and the absent path); `tests/red/*` unaffected
  (from their assertions).
- ASSUMED: nothing load-bearing. PC behaviour is not claimed.

## 13. Continuity

A container restart at about 05:40Z (the coordinator's message) came after the clone dry run finished (`clone2.log`
05:39:22Z) and after I had removed the worktree, the clone and `/tmp/i59a-wt` myself. Nothing of mine was running.
Verified at 05:42:54Z: `git worktree list` shows only the main tree and `git worktree prune --dry-run` finds nothing;
the tree's `proofs/S0-01/pins.py` is unchanged (the demo edited only the worktree copy); the six boundary files
re-hashed equal to the bytes every piece of evidence used; the PIN..HEAD boundary diff is still empty.

## 14. Status

DONE for the lane, round 2 included (GATED-PENDING-VERIFY): the change is in the tree, uncommitted; the landing waits
for #313 and #314 and the section 5 steps. Round 2 is section 15.

## 15. Round 2: the S0-08 gap closed (2026-09-26 06:0xZ, the coordinator's round-2 request)

The change. `proof_attestation` now skips only the proof's OWN two artifacts, `proofs/<id>/result.json` and
`proofs/<id>/blocked.json` directly in its directory, plus `__pycache__`. A file of either name deeper down is an input
and is hashed. `scripts/validate-ledger`: the skip is `if path in own_artifacts` (a set of those two paths) instead of
`if path.name in ("result.json", "blocked.json")`, and the docstring says so. The old rule dropped exactly one file in
the tree, tracked or not (`find proofs -name result.json -o -name blocked.json`, minus the twelve top-level ones):
`proofs/S0-08/fixtures/malformed-marker/blocked.json`. S0-08's key set goes from 29 to 30; every other proof's is
unchanged.

The tests (`tests/test_attested_inputs.py`, now 63):
- The pin is gone. `KNOWN_UNATTESTED_INSIDE` is deleted and the guard's inside rule is `assert not inside`, so
  `test_every_repo_file_a_checker_reads_is_attested[S0-08]` passes only while the fixture is attested.
- New `test_only_the_proofs_own_artifacts_are_left_out_of_its_attestation`: in a minimal root, `fixtures/result.json` and
  `fixtures/marker/blocked.json` are attested with their exact sha256, the top-level `result.json` and `blocked.json` are
  not; on the real tree S0-08's attestation holds `proofs/S0-08/fixtures/malformed-marker/blocked.json`.
- New `test_a_changed_fixture_named_like_an_artifact_makes_its_proof_invalid`: a minted S0-04 result, then one byte of its
  `fixtures/marker/blocked.json` changed, is INVALID by `attestation-mismatch: S0-04 proofs/S0-04/fixtures/marker/blocked.json`.
- The independent oracle (`_independent_attestation`) skips only the two top-level artifacts.
- The inside-rule negative control now plants a data file under `fixtures/__pycache__/`, the one class the attestation
  still leaves out inside a directory.
- My own first run caught a fixture error: that integrity test first used S0-05, whose copied registry entry declares
  `proofs/S0-01/pins.py` (absent in a minimal root), so its fresh mint read INVALID by the verdict-level absence rule.
  It uses S0-04, which declares nothing.

Named mutants, in a scratch mirror (`git archive 4b5434f` of `proofs`, `scripts`, `tests/conftest.py`, `pyproject.toml`
and the two ADRs, plus the three changed files; round 1's harness rules), pasted:
```
CONTROL (unmutated, 5 named tests): rc=0 5 passed in 0.94s
KILLED         M1 skip-anywhere (the old rule): 4/4 named FAILED; 4 failed in 0.75s
KILLED         M2 skip nothing: 2/2 named FAILED; 2 failed in 0.26s
KILLED         G5 inside rule off: 1/1 named FAILED; 1 failed in 0.29s
EXPECTED=3 KILLED=3 SURVIVED=0 INVALID=0
```
M1, the old skip-anywhere rule, fails `test_only_the_proofs_own_artifacts_are_left_out_of_its_attestation`,
`test_a_changed_fixture_named_like_an_artifact_makes_its_proof_invalid`, `test_every_repo_file_a_checker_reads_is_attested[S0-08]`
(the test that carried the pin) and `test_the_attestation_is_the_closure_the_directory_and_the_declared_files[S0-08]`.
M2 (skip nothing) proves the own-artifact exclusion is needed. The harness's first control run refused (1 failed: the
mirror lacked `docs/adr/0005-foundry-host.md`, which `_scratch_s0_09` copies); with the ADRs added the control passed.

The re-runs (pasted):
```
tests/test_attested_inputs.py (1 files set=96d60da64331)
run 1: pytest-exit: 0  pytest-summary: 63 passed in 27.27s
run 2: pytest-exit: 0  pytest-summary: 63 passed in 26.99s
floor (13 files set=07f9aa59b430), once
pytest-exit: 1  pytest-summary: 5 failed, 1522 passed in 506.27s (0:08:26)
```
The same five reds as round 1, at the same lines, each the committed results' expected staleness (section 6):
`test_validate_ledger.py::test_registry_rows_carry_no_key_the_validator_does_not_read` (:573),
`test_validate_ledger.py::test_committed_pc_bridge_spike_validates_and_declares_all_effects` (:592),
`test_proof_status.py::test_committed_state_passes_status_and_ledger` (:95),
`test_s0_11_eval_hardening.py::test_attestation_binds_artifact_to_source` (:153) and
`test_s0_11_eval_hardening.py::test_tooling_mutation_breaks_attestation` (:197). No test is newly red. The one visible
change inside them: S0-08's first mismatched key is now `proofs/S0-08/fixtures/malformed-marker/blocked.json` (round 1:
`proofs/registry.yaml`), the key its committed result lacks. pyflakes rc 0; the separator grep prints 0 on both changed
files; the screen shows round 1's hits only (line numbers shifted by 3).

The landing: its outcome does not change, so the full worktree proof was not re-run. S0-08 alone, in the same mirror:
`proof-runner run --proof S0-08 --venue sandbox --root .` rc 0; attested 29 -> 30 keys, the fixture among them;
`S0-08 PRESENT`; one byte of the fixture changed -> `S0-08 INVALID` with
`attestation-mismatch: S0-08 proofs/S0-08/fixtures/malformed-marker/blocked.json`; restored -> PRESENT. The landing
command list (section 5) is unchanged: S0-08 re-mints like the rest and now records 30 keys. Mirror removed.

A correction to section 6's files-touched line (round 1): `scripts/validate-ledger +117/-18` was read off a `--stat` bar,
not measured. Measured now (`git diff --numstat`): `scripts/validate-ledger` +111/-13, `proofs/registry.yaml` +7/-7,
`tests/test_validate_ledger.py` +7/-1; `tests/test_attested_inputs.py` 638 lines, 63 tests.

Superseded by this round: section 7 N2 and section 10 A1 (the gap is closed); section 9 X3's pinned carve-out (gone:
the guard's one carve-out is the proof's own two artifacts); the `KNOWN_UNATTESTED_INSIDE` mentions in sections 3 and 11,
and round 1's inside-rule control (a fixture-named read, now a `__pycache__` read).

NOT done after round 2:
- N1 unchanged: no `result.json`, ledger, tag object or ledger line written in the tree. No patch file (the coordinator
  writes the patch).
- N2 RESOLVED here.
- N3 unchanged: S0-07's Fubuki checkout is attested by nothing.
- N4 unchanged (the guard's blind spots), plus: the attestation still leaves out `__pycache__` contents; a checker that
  read data there would red the guard (its control) instead of being attested.
- N5-N8 unchanged: CI's skips of S0-07 and S0-11 are emulated, not run on CI; the whole `tests/`, `tests/red` and the
  PC suite not run; GitNexus cannot index the suffix-less validator; S0-11 still re-reads its previous result (A2).
