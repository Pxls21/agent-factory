GOV2e — the ONE focused repair of VERIFY-GOV2d Finding 1 (the `gpg=` symlink acceptance)

Outcome: MERGE-READY-WITH-FOLLOWUPS recommendation. The defect is repaired and proven
red→green with a zero-invocation negative control; F2/F3/F4 of VERIFY-GOV2d are filed as
issue #21 and are NOT this lane's (boundary: review.py + test_governance_review.py only).

DATA — files:lines changed
- RV:116 — `absolute path to a regular file` now explicitly says a bare name, missing path, directory,
  or symlink refuses with `fubuki-review-gpg-unavailable`.
- RV:136 — `gpg_path = Path(gpg)` remains the explicit-`gpg=` pathname conversion.
- RV:141 — `if not gpg_path.is_absolute() or gpg_path.is_symlink() or not gpg_path.is_file():`
  evaluates `is_symlink()` BEFORE `is_file()` (which follows symlinks).
- RV:142 — `raise GovernanceError("fubuki-review-gpg-unavailable"` keeps the stable reason; the detail
  names the pathname and says "must be an absolute regular file, not a symlink".
- RV:143 — `gpg = str(gpg_path)` is unchanged. The `_GPG_PATHS` default branch, the FD regular-file
  proof, and the child env are untouched (they HELD under VERIFY-GOV2d).
- TR:479 — `test_explicit_gpg_symlink_is_refused_before_any_process_runs` is the new regression.
- TR:515 — `gpg=link` exercises the absolute symlink; TR:516 asserts the exact stable reason.
- TR:518 — `assert call_count == 0` proves no child-process attempt; TR:519 corroborates that the sentinel
  marker does not exist.
- TR:524 — `gpg=sentinel` passes the SAME sentinel by its real absolute regular path.
- TR:526 — `assert call_count == 1` proves the positive control reaches exactly one subprocess; TR:527
  corroborates that the sentinel marker exists.
- TR:533 — `gpg=dangling` exercises the missing-target symlink; TR:534 asserts the same reason.
- TR:536 — `assert call_count == 1` proves the call count is unchanged (no process for the dangling path).
  File grows 476 → 536 lines; `def test_` count 24 → 25.
- File identity at the PIN (c4d12d1): `sha256sum | cut -c1-16` → RV `06da43e1024e548b`, TR `1ec52c579c7b4558`
  (both byte-identical to the GOV2d PIN d116cbc; verified in this tree before any edit).

DATA — RED→GREEN (pasted)
- Baseline at the PIN: `24 passed in 1.71s` (FUBUKI_OS_ROOT/FUBUKI_OTHER_ROOT set; `--basetemp=/home/rocco/tmp-gov2e/bt`).
- RED — the new regression run against the PIN's review.py (`RV@c4d12d1:137`,
  `if not gpg_path.is_absolute() or not gpg_path.is_file():`):
  `1 failed in 0.22s`, `E       AssertionError: assert 'fubuki-owner-key-invalid' == 'fubuki-revie...g-unavailable'`
  — the absolute symlink passed `is_file()`, the sentinel subprocess RAN (its `exit 2` surfaced at the later
  import step as `fubuki-owner-key-invalid`, the exact coordinator signature), and its marker file
  `sentinel-ran` was written on disk during the run (zero-invocation broken — this is the red proof).
- GREEN — the same suite with the fix: run 1 `25 passed in 1.79s`, run 2 `25 passed in 1.77s` (counts
  bitwise-identical). In (a) the subprocess-attempt count is exactly 0; in (b) it is exactly 1 and the marker
  exists; after (c) it remains 1 (the dangling path spawned nothing).

DATA — mutants (each in a scratch copy: `src/` + `tests/` + `upstream.lock.yaml` + `pyproject.toml`
copied to `/home/rocco/tmp-gov2e/scratch`, the mutation swapped into that copy only, the killing test = the
new regression at TR:479 (`test_explicit_gpg_symlink_is_refused_before_any_process_runs`):
- m1 drop the symlink refusal (restore the PIN's two-clause check): the sentinel ran and the early refusal
  is gone → KILLED by TR:516 (`assert excinfo.value.reason == "fubuki-review-gpg-unavailable"`).
- m2 refuse symlinks only AFTER a subprocess spawn (pre-check = the two-clause form; the symlink branch calls
  the target once, then raises the CORRECT reason): KILLED by TR:518 — `assert call_count == 0` observed 1.
  This is the structural zero-invocation discriminator, independent of the marker.
- m3 changes the reason string to `fubuki-review-gpg-symlink-refused`.
  KILLED by TR:516 (`assert excinfo.value.reason == "fubuki-review-gpg-unavailable"`); the dangling shape is
  independently pinned at TR:534 by `assert excinfo3.value.reason == "fubuki-review-gpg-unavailable"`.
- m4 `is_symlink()` → `os.path.islink(str(gpg_path))` equivalence → `1 passed` (not killed) — EQUIVALENT; no
  test discriminates the two forms (the brief anticipates this: "state EQUIVALENT if no test discriminates").

DATA — pyflakes
- `python -m pyflakes` on the system `python` (3.13): NOT run there — no module.
- Run with the project venv: `/home/rocco/venv-agent-factory/bin/python -m pyflakes` (pyflakes 3.4.0) on
  `src/agent_factory/governance/review.py tests/test_governance_review.py` → rc 0, no findings.

DISCREPANCIES
- The brief's gate text says "pyflakes … if pyflakes is present, else say NOT run (the lane environment lacked
  it 2026-09-22)". Measured in this tree: the session `python` (3.13) has no pyflakes, but
  `/home/rocco/venv-agent-factory` (pyflakes 3.4.0) does, so the gate was RUN via that venv, not skipped.
- The brief's premise block pins the two-clause check at `RV:137`; the fresh grep in this tree puts it at
  `RV:141` in the working tree (the block is `RV:134-143`), because the docstring edit added one line above.
  The PIN's bytes were verified by hash, so the premise is intact; the number cited here is the working tree's.
- First baseline attempt: the `eval` of `fubuki_pin_sync.sh` output did not carry the env into the next
  command (24 setup errors: `FUBUKI_OS_ROOT is a declared GOV1 test input`). Setting `FUBUKI_OS_ROOT` /
  `FUBUKI_OTHER_ROOT` explicitly gave the clean `24 passed` baseline. No defect in the tree.
- GitNexus: the clone-index `impact verify_review` returned `Target 'verify_review' not found` (risk UNKNOWN);
  `detect-changes --repo /home/rocco/agent-factory` returned `No changes detected` because it inspected the
  clone, not this detached lane; the lane-tree path is not registered in the index. The required post-edit
  instrument was run but is UNMAPPED here. The lane context pack instead mapped `verify_review` with graft
  and ripwire (23 caller references, capped; one hop tested) and captured the AP screens.
- Final report lint: `report_lint: 28 refs — OK 18, NEAR 4, MISS 0, UNCHECKABLE 6, UNRESOLVED 0 (worktree)`
  (rc 0).

NOT-done (issue #21 — NOT this lane's)
- F2 (README wording), F3, F4 of VERIFY-GOV2d are filed as issue #21 and are out of this lane's boundary.
  `docs/governance/reviews/README.md` and `packet.py` were not touched.
- Coordinator gates at landing (not run by this lane): `harness-ports/tests/run-all.sh`. The lane DID run
  `ap_screen` through `lane_context.sh` (RV: AP-32 x2, AF-AP-110 x1; TR: AF-AP-80 x2, all pre-existing
  named patterns) and `report_lint` on this report; the coordinator still reruns its landing forms.

SELF-ATTACK (the three most likely ways this is wrong, each ruled out)
- The fix might still run a process before the refusal. Ruled out structurally: when the fixed branch handles
  the symlink, TR:518 observes `call_count == 0`; the real regular-file positive control advances it to 1 at
  TR:526; the dangling symlink leaves it at 1 at TR:536. Mutants m1/m2 show the sentinel marker is written and
  the failure moves to a later stage when the early `is_symlink()` clause is absent or moved after spawn.
- The positive control could be a hollow green (the sentinel never really reaches the subprocess). Ruled
  out: the instrument counts exactly one `subprocess.run` attempt, the sentinel's `exit 2` surfaces as
  `fubuki-owner-key-invalid`, and its marker is written; the symlink and dangling branches attempt no process.
- The fix could have broken the default `_GPG_PATHS` branch or the FD proof. Ruled out: those are untouched
  (`git diff --stat c4d12d1` → review.py 8+/4− in that branch + docstring; test file 60+), and all
  24 pre-existing tests still pass alongside the new one.

GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS (Finding 1 repaired and proven; follow-ups = issue #21).
