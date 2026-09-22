# VERIFY-GOV2e — the independent targeted adversarial verify of the symlink refusal on the review binding

PIN: 949aa85 (origin; the GOV2e landing commit — `src/agent_factory/governance/review.py` sha256[:16] 6b64de4f9ef8a5e3, `tests/test_governance_review.py` 1631032884a0ec24)
LANE: pc-verify-gov2e
ROLE: adversarial-verifier (verify) — the STRICT local route: `HERMES_MODEL=qwen-local/qwen3.8-27b-local` (D-039(a) + D-042(2)); effort = the verify default.
COMPONENT under verify: `review.py:134-143` (the explicit-`gpg=` branch) + `tests/test_governance_review.py:479-536` (the sentinel regression). CONTRACT (frozen): `tasks/briefs/pc/pc-gov2e.md` (the repair spec, items 1-3 + mutants m1-m4) · the VERIFY-GOV2d report `tasks/briefs/stage3-governance-support/VERIFY-GOV2d-report.md` Finding 1 · the builder's report `tasks/briefs/stage3-governance-support/GOV2e-report.md` (an input to attack, never evidence). BUDGET: verify only — no repair, no edit outside a scratch copy; never commit or push; the only bridge-free gate is pytest (`python -m pytest -n 4 tests/test_governance_review.py -q -p no:cacheprovider --basetemp=/home/rocco/tmp-vgov2e/bt` after `export FUBUKI_OS_ROOT=/home/rocco/fubuki-pin/fubuki-os FUBUKI_OTHER_ROOT=/home/rocco/fubuki-pin/fubuki-os-other`; NEVER the PC's tmpfs `/tmp` for trees; every call under 420 s).

## Items (discovery exhaustive; disposition by the blocking predicate — contract-mapped · reproduced through the real path · materially effective · a concrete discriminator · in boundary)
1. Reproduce the landing gates at the PIN: the test file twice (counts bitwise-identical; the current file collects 25 tests — paste), pyflakes if present, the builder's m1-m3 kills and the m4 equivalence claim (re-run each in a scratch copy; state EQUIVALENT only if no test discriminates and say why).
2. Hostile `gpg=` shapes through the REAL `verify_review` with a counted `subprocess.run` and a marker-writing sentinel, each asserting ZERO invocation on refusal: a symlink whose target is a DIRECTORY; a symlink chain (link → link → sentinel); a relative symlink target; a symlink in a PARENT directory component (`/tmp/x/link-dir/gpg` where `link-dir` is a symlink and `gpg` a regular file — the contract refuses the pathname's own symlink-ness; state whether a symlinked parent is in contract); a hard link to the sentinel (a regular file — must PASS the check; a positive control); a FIFO at the path; a path with a trailing slash; a bytes path; `gpg=""`; `gpg=None` (the default branch — untouched, must not regress: paste its behavior at the PIN).
3. TOCTOU: the check is on the pathname, then the subprocess runs the pathname — can a regular file be swapped for a symlink between `is_symlink()` and `subprocess.run`? Reproduce with a forced race in a scratch copy (a monkeypatched `is_symlink` that swaps the file after returning False) and state whether the window is in contract (VERIFY-GOV2d's F2 class, AF-AP-70) or a declared limit; do NOT repair.
4. The test's own oracle: does the counted `subprocess.run` wrapper cover every spawn path in `review.py` (any `Popen`/`check_output`/`os.exec*` bypassing `subprocess.run`? grep and paste); would the test pass with the refusal replaced by a refusal that happens AFTER a spawn (m2's shape — re-verify the kill); is the marker asserted absent BEFORE the positive control writes it (ordering inside one test)?
5. The docstring/README claim vs behavior: `review.py:116` says "or a symlink refuse"; `docs/governance/reviews/README.md` (issue #21 F2's wording) — any contradiction is a finding, not a repair.
6. Report lint on the builder's report (`python3 scripts/report_lint.py --min-refs 10 tasks/briefs/stage3-governance-support/GOV2e-report.md`, paste) and `python3 scripts/ap_screen.py --tests src/agent_factory/governance/review.py tests/test_governance_review.py` (the FLAG form).

## Report (`tasks/briefs/stage3-governance-support/VERIFY-GOV2e-report.md`)
Every observation with `file:line`, SOLID/UNSURE, reproduced-through-the-real-path yes/no; the mutant table with your rows added; then the GATE RECOMMENDATION (`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) with the predicate applied per finding. `report_lint --min-refs 12` (≤ 3 fix rounds, then paste and finish). Never touch the ledger, the wiki, any brief, `packet.py`, the README.

## PREMISE — MEASURED at authoring (2026-09-22T17:35:44Z, sandbox @ 949aa85)
```
$ git show 949aa85:src/agent_factory/governance/review.py | sed -n '141p'
        if not gpg_path.is_absolute() or gpg_path.is_symlink() or not gpg_path.is_file():
$ git show 949aa85:tests/test_governance_review.py | grep -c 'def test_'
25
$ git show 949aa85:tests/test_governance_review.py | grep -n 'def test_explicit_gpg_symlink_is_refused_before_any_process_runs'
479:def test_explicit_gpg_symlink_is_refused_before_any_process_runs(tmp_path: Path, keys, monkeypatch) -> None:
$ sha256 (16): review.py 6b64de4f9ef8a5e3 · test 1631032884a0ec24
$ PC gate at landing: pc_suite 20260922T173331Z-a899a32 → pytest-summary: 25 passed in 0.72s (set ce6a68f1998d)
```
