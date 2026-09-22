Verified live: report written and linted.

Report file:
  /home/rocco/agent-factory/.lanes/pc-verify-gov2e.md--949aa85/tree/tasks/briefs/stage3-governance-support/VERIFY-GOV2e-report.md

Lane copies:
  /home/rocco/agent-factory/.lanes/pc-verify-gov2e.md--949aa85/report-draft.md
  /home/rocco/agent-factory/.lanes/pc-verify-gov2e.md--949aa85/report.md

Gate recommendation:
  MERGE-READY-WITH-FOLLOWUPS

Verified:
  25 passed in 7.27s
  25 passed in 7.14s
  pytest-summary: 25 passed in 1.88s
  pyflakes rc 0
  report_lint: 35 refs — OK 30, NEAR 2, MISS 0, UNCHECKABLE 3, UNRESOLVED 0
  diff check rc 0

Findings:
  1. INFO: original explicit symlink-to-gpg defect is repaired.
  2. FOLLOW-UP: explicit gpg= still has a forced t0→t1 pathname race after is_symlink().
  3. FOLLOW-UP: symlinked parent directory component is not refused.
  4. FOLLOW-UP: bytes gpg= raises raw TypeError.
  5. INFO: README is consistent but does not document the follow-up limits.
  6. INFO/DISCREPANCY: the brief’s literal builder-report-lint command lacks alias maps; mapped lint passes.

Worktree status:
  only new report file is untracked:
  tasks/briefs/stage3-governance-support/VERIFY-GOV2e-report.md

graft saved ~2,890 tokens this turn.
 regression is `TR:479`, `test_explicit_gpg_symlink_is_refused_before_any_process_runs`.

## 2. Landing gates reproduced

Commands used the declared Fubuki inputs:
`FUBUKI_OS_ROOT=/home/rocco/fubuki-pin/fubuki-os` and `FUBUKI_OTHER_ROOT=/home/rocco/fubuki-pin/fubuki-os-other`.

- `python -m pytest -n 4 tests/test_governance_review.py -q -p no:cacheprovider --basetemp=/home/rocco/tmp-vgov2e/bt`
  - run 1: `25 passed in 7.27s`; rc 0.
  - run 2: `25 passed in 7.14s`; rc 0.
- `FUBUKI_OS_ROOT=... FUBUKI_OTHER_ROOT=... bash scripts/test_summary.sh tests/test_governance_review.py`
  - `pytest-summary: 25 passed in 1.88s`; rc 0.
- `/home/rocco/venv-agent-factory/bin/python -m pyflakes src/agent_factory/governance/review.py tests/test_governance_review.py`
  - rc 0, no output.

Discrepancy: the first `scripts/test_summary.sh` attempt inherited a stale root (`/root/fubuki-pin/fubuki-os`) and produced 25 setup errors. Re-running with the declared `/home/rocco/fubuki-pin/...` inputs produced the `25 passed` summary above. The bad attempt did not produce a green claim.

## 3. Red-green and mutation audit

Red-first control against historical `c4d12d1` review.py, scratch import boundary:

- `PIN_MODULE=/home/rocco/tmp-vgov2e/redpin/src/agent_factory/governance/review.py`.
- Selected test: `TR:479`, `test_explicit_gpg_symlink_is_refused_before_any_process_runs`.
- Result: `1 failed in 0.18s`; assertion at `TR:516`, `assert excinfo.value.reason == "fubuki-review-gpg-unavailable"`; actual was `fubuki-owner-key-invalid`.
- This reproduces VERIFY-GOV2d Finding 1: the symlink target sentinel executed before the later owner-key-stage failure.

Scratch mutants, each compiled and collected before the selected test ran, and each asserted its module identity under `/home/rocco/tmp-vgov2e/mutations/.../review.py`:

| mutant | result | discriminator |
|---|---|---|
| m1 drop `gpg_path.is_symlink()` | KILLED | `TR:516` `assert excinfo.value.reason == "fubuki-review-gpg-unavailable"` failed: actual `fubuki-owner-key-invalid` |
| m2 refuse only after one spawn | KILLED | `TR:518`, `assert call_count == 0`, observed `1` |
| m3 change reason string | KILLED | `TR:516` `assert excinfo.value.reason == "fubuki-review-gpg-unavailable"` failed: actual `fubuki-review-gpg-symlink-refused` |
| m4 `is_symlink()` → `os.path.islink(str(gpg_path).rstrip('/'))` | EQUIVALENT here | selected test `1 passed in 0.09s`; no discriminator found |

The regression's oracle order is sound: `TR:518` pins `assert call_count == 0` and `TR:519` pins `assert not marker.exists()` before the positive-control branch reaches `TR:526` `assert call_count == 1` and `TR:527` `assert marker.exists()`. The dangling-symlink branch leaves the count unchanged at `TR:536` `assert call_count == 1`.

## 4. Hostile `gpg=` shapes through real `verify_review`

The probe copied the import boundary to `/home/rocco/tmp-vgov2e/scratch2`; the module under test printed as `/home/rocco/tmp-vgov2e/scratch2/src/agent_factory/governance/review.py`. Every row used a counted `review.subprocess.run` wrapper and a marker-writing sentinel.

| shape | reproduced-through-real-verify_review | observed behavior |
|---|---:|---|
| symlink to sentinel | yes | `fubuki-review-gpg-unavailable`; calls 0; marker false |
| symlink to sentinel with trailing slash | yes | `fubuki-review-gpg-unavailable`; calls 0; marker false |
| symlink chain link→link→sentinel | yes | `fubuki-review-gpg-unavailable`; calls 0; marker false |
| relative symlink target | yes | `fubuki-review-gpg-unavailable`; calls 0; marker false |
| symlinked parent directory component | yes | `fubuki-owner-key-invalid`; calls 1; marker true |
| hard link to sentinel | yes | `fubuki-owner-key-invalid`; calls 1; marker true |
| FIFO at path | yes | `fubuki-review-gpg-unavailable`; calls 0; marker false |
| regular path with trailing slash spelling | yes | `fubuki-owner-key-invalid`; calls 1; marker true |
| bytes path | yes | raw `TypeError`; calls 0; marker false |
| `gpg=""` | yes | `fubuki-review-gpg-unavailable`; calls 0; marker false |
| `gpg=None` default branch | yes | `fubuki-review-signature-invalid`; calls 3; no sentinel marker |
| bare name | yes | `fubuki-review-gpg-unavailable`; calls 0; marker false |
| directory | yes | `fubuki-review-gpg-unavailable`; calls 0; marker false |

Disposition details:

- The frozen GOV2e contract refuses the pathname's own symlink-ness. Parent-component symlinks are outside that literal criterion: the final `gpg` pathname is a regular file, so `RV:141` (`if not gpg_path.is_absolute() or gpg_path.is_symlink() or not gpg_path.is_file():`) does not refuse it. This is a hardening follow-up, not a GOV2e blocker.
- A hard link is a regular file and correctly passes the check; it is the positive control.
- `gpg=None` exercises the untouched default branch at `RV:145-148` (`_GPG_PATHS` default branch); the behavior is unchanged and does not use the sentinel.
- Bytes are outside the `gpg: str | Path | None` annotation at `RV:106`, but the raw `TypeError` is a follow-up API hardening observation.

## 5. Explicit-gpg TOCTOU probe

A scratch copy forced this race: the first `Path.is_symlink()` call returned False on a regular executable path, then replaced that pathname with a symlink to a second marker-writing sentinel before `Path.is_file()` and `subprocess.run` used the path.

Probe output:

- `MUTANT_MODULE= /home/rocco/tmp-vgov2e/toctou-scratch/src/agent_factory/governance/review.py`.
- `SWAPPED_AFTER_FALSE= True`.
- `FINAL_PATH_IS_SYMLINK= True`.
- `RESULT_REASON= fubuki-owner-key-invalid`.
- `SUBPROCESS_RUN_CALLS= 1`.
- `SENTINEL_MARKER= True`.

Classification: SOLID follow-up. It is the AF-AP-70 class in mechanism, but GOV2e's frozen one-repair contract was the static symlink-at-pathname refusal from `GD:180-187` (`BLOCKER — explicit absolute symlink gpg is executed`) and `PC:31-33`, not an atomic executable-open or `fexecve` design. The verifier brief explicitly asked to state the window and not repair it. I therefore do not treat it as a blocker for this increment. If the coordinator rules that AF-AP-70 is in-contract for explicit `gpg=`, this row has the canonical discriminator needed to reopen the repair.

## 6. Test oracle and spawn coverage

- Direct source scan found only `subprocess.run` child-spawn calls in `review.py`: `_keyring_shape` at `RV:85`, import at `RV:175`, and verify at `RV:182`.
- No `subprocess.Popen`, `subprocess.check_output`, `subprocess.call`, `subprocess.check_call`, `os.exec*`, or `os.spawn*` call exists in `RV`.
- The test monkeypatches `review.subprocess.run`, so it covers every child-spawn path in this module.
- The m2 mutant proved a refusal that happens after a spawn is killed by `TR:518` `assert call_count == 0`.

## 7. Documentation and stale-context sweep

- `RV:116` now says a symlink refuses with `fubuki-review-gpg-unavailable` before anything runs; the verified own-pathname symlink behavior matches it.
- `RM:25-26` says explicit `gpg=` is tests-only and must be an absolute path to a regular file; production never passes it. This is consistent with the own-pathname symlink refusal, though it does not spell out parent-component symlinks or the TOCTOU limit.
- `RM` was unchanged from `c4d12d1` to `949aa85`; `PK` was unchanged too. No README/packet contradiction was found inside the GOV2e scope.

## 8. Screens and report audit

- Literal builder-report lint command from the verify brief:
  - `python3 scripts/report_lint.py --min-refs 10 tasks/briefs/stage3-governance-support/GOV2e-report.md`
  - result: `report_lint: 1 refs — OK 0, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 1 (worktree)` plus `FLOOR — OK 0 < --min-refs 10`; rc 1.
  - Cause: the brief's literal command supplies no alias maps, so `RV@c4d12d1:137` is unresolved.
- Builder-report lint with aliases reproduced the builder's report claim:
  - `python3 scripts/report_lint.py --min-refs 10 ... --map RV=src/agent_factory/governance/review.py --map TR=tests/test_governance_review.py`
  - result: `report_lint: 28 refs — OK 18, NEAR 4, MISS 0, UNCHECKABLE 6, UNRESOLVED 0 (worktree)`; rc 0.
- `python3 scripts/ap_screen.py --tests src/agent_factory/governance/review.py tests/test_governance_review.py`
  - result: `--- TEST_SCREEN over 2 path(s): 2 hits over 2 files ---`; `AF-AP-80: 2`; rc 0.
- Non-test AP screen for context reported `AP-32 x3`, `AF-AP-110 x2`, `AF-AP-115 x2`, `AF-AP-58 x2`, `AP-1 x2`, `AF-AP-70 x1`, all in existing GOV2d tests or source/context lines; no GOV2e production blocker came from this screen.

## 9. Code-intel instruments

- Graft mapped `verify_review` at `RV:101-215` and saved about 2,890 tokens on `RV` skeleton.
- Ripwire caller map found `verify_review` called by production `load_packet` at `PK:136` and 22 test callers; its counts are floors.
- `lane_context.sh` wrote `/home/rocco/tmp-vgov2e/context-pack.md` with 160 lines.
- GitNexus clone-index impact was unmapped: `Target 'verify_review' not found`, `risk: UNKNOWN`; same for the new test name. This is a tool-index limitation, not an absence claim.

## 10. Finding inventory

1. INFO — original explicit symlink-to-gpg defect is repaired.
   - Evidence level: SOLID.
   - Contract mapping: GOV2e repair item 1 and regression item 2.
   - Canonical-path status: yes, real `verify_review` explicit `gpg=` branch.
   - Material effect: the symlink target no longer runs; `call_count == 0` at `TR:518` and no marker at `TR:519`.
   - Reproduction: xdist gate `25 passed` twice; red-first historical pin; m1/m2/m3 killed.
   - Suggested fix: none.

2. FOLLOW-UP — explicit `gpg=` has a t0→t1 pathname race after `is_symlink()`.
   - Evidence level: SOLID.
   - Contract mapping: AF-AP-70 mechanism; not frozen GOV2e one-repair criterion unless the coordinator expands it.
   - Canonical-path status: forced race through real `verify_review`; production `load_packet` still does not pass `gpg=` at `PK:155`.
   - Material effect: a swapped symlink target executed; marker true and `SUBPROCESS_RUN_CALLS=1`.
   - Reproduction: `/home/rocco/tmp-vgov2e/toctou.py` output in section 5.
   - Suggested fix: future explicit-executable hardening if this test-only interface remains a trust boundary; do not patch under GOV2e without contract amendment.

3. FOLLOW-UP — symlink in a parent directory component is not refused.
   - Evidence level: SOLID.
   - Contract mapping: none for GOV2e; the contract names the pathname itself.
   - Canonical-path status: real `verify_review` explicit `gpg=` branch.
   - Material effect: sentinel executed (`calls=1`, marker true).
   - Reproduction: section 4 `symlinked_parent` row.
   - Suggested fix: only if parent-component containment becomes a frozen criterion; otherwise document the limit.

4. FOLLOW-UP — bytes `gpg=` raises raw `TypeError` instead of a `GovernanceError`.
   - Evidence level: SOLID.
   - Contract mapping: none; `RV:106` annotates `str | Path | None`.
   - Canonical-path status: real `verify_review`, but outside typed API domain.
   - Material effect: caller sees raw TypeError; no child process runs.
   - Reproduction: section 4 `bytes_path` row and independent `/usr/bin/gpg` bytes probe.
   - Suggested fix: optional API hardening: reject non-`str`/`PathLike[str]` explicit `gpg=` with `fubuki-review-gpg-unavailable`.

5. INFO — README is consistent but less explicit than behavior.
   - Evidence level: SOLID static review plus behavior probes.
   - Contract mapping: docstring/README item 5.
   - Canonical-path status: docs only.
   - Material effect: no false claim found for own-pathname symlink refusal; parent-component and TOCTOU limits are not documented.
   - Reproduction: `RV:116` and `RM:25-26`.
   - Suggested fix: future README wording if follow-up hardening is accepted or rejected explicitly.

6. INFO/DISCREPANCY — the verifier brief's literal builder-report-lint command lacks alias maps and fails its own floor.
   - Evidence level: SOLID.
   - Contract mapping: item 6 evidence audit.
   - Canonical-path status: report tooling only.
   - Material effect: not a code defect; mapped lint reproduces rc 0.
   - Reproduction: section 8.
   - Suggested fix: future verify briefs should include the same `--map` aliases they expect report_lint to resolve.

## 11. Deliberately skipped / not done

- No repair, no commit, no push, no ledger/wiki/brief edit.
- No full-tree suite. The frozen GOV2e verify scope named the review test file and targeted probes.
- No host mutation of `/usr/bin/gpg` or production service change.
- No claim that GitNexus mapped the symbols; it returned UNKNOWN.
- No final gate verdict. This report is a lane recommendation only.

## 12. Gate recommendation

GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS — no finding satisfies the complete blocking predicate under the frozen GOV2e contract. The original blocker is repaired and independently discriminated. Follow-ups F2/F3/F4 are real observations, but they are outside the one focused symlink-at-pathname contract as dispatched. If the coordinator classifies AF-AP-70 on explicit `gpg=` as in-contract, Finding 2 has the evidence needed to change the recommendation to NOT-READY.

This is a recommendation, not a final gate verdict.

## 13. Discrepancies and retro

- The exact builder-report-lint command in the verifier brief fails without `--map`; mapped lint passes. This is a brief/tooling discrepancy, not a GOV2e code defect.
- `scripts/test_summary.sh` needs the declared Fubuki roots in the same command environment; otherwise it fails closed on the wrong root. I reran it with the declared inputs.
- `ap_screen.py --tests` and non-test `ap_screen.py` intentionally report different registries; both are pasted above.
- Final verifier-report lint: `report_lint: 35 refs — OK 30, NEAR 2, MISS 0, UNCHECKABLE 3, UNRESOLVED 0 (worktree)`; rc 0; the required 12-reference floor is met.
- Retro: nothing to bake beyond the existing AF-AP-70 / AF-AP-73 lessons. No new skill update needed.

FILE IDENTITY:

- PIN `949aa85335d9637c19209110434c21b52e98f1fc`.
- `RV` `6b64de4f9ef8a5e3`.
- `TR` `1631032884a0ec24`.
