Proposal ready, pending the sandbox-side adversarial-verifier lane.

→ Changed `review.py:116,134-143` to reject explicit `gpg=` symlinks before `is_file()` or subprocess execution.

→ Added `test_governance_review.py:479-536` covering absolute symlinks, dangling symlinks, zero subprocess attempts, and a real-path positive control.

→ Verified RED at PIN: `1 failed in 0.21s`; the sentinel executed and wrote its marker.

→ Verified GREEN twice: `25 passed in 1.79s` and `25 passed in 1.77s`. Counts match.

→ Mutants: m1, m2, and m3 killed. m4 passed as an equivalent `os.path.islink()` implementation.

→ Static checks: pyflakes rc 0, py_compile rc 0, `git diff --check` rc 0. Report lint: `28 refs — OK 18, NEAR 4, MISS 0, UNCHECKABLE 6, UNRESOLVED 0`, rc 0.

→ Report: `tasks/briefs/stage3-governance-support/GOV2e-report.md`

→ NOT done: VERIFY-GOV2d F2/F3/F4 remain issue #21. GitNexus could not map this detached lane; the discrepancy is recorded in the report. No commit or push was made.
