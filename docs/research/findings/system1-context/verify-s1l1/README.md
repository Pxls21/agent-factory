# VERIFY-S1-L1 reproductions (verbatim record)

The independent verifier's reproduction scripts for the situation-to-skill hook (`.claude/hooks/system1-context.py`),
copied byte for byte from its scratch folder after its verdict (MERGE-READY-WITH-FOLLOWUPS; the report is
`tasks/briefs/system1/VERIFY-S1-L1-report.md`, whose FINDING INVENTORY names the script behind each finding). They are the
acceptance bar of the repair round S1-L1-R1. They are kept unedited, so pyflakes reports unused imports in six of them
(committed with `SKIP_LINT_DELTA=1`).

How to run: copy this folder to a scratch directory first. `setup_copy.sh` writes its copies (`repo/`, `repo_m/`) beside
itself, and it reads the live tree at `/home/user/agent-factory`. Then run each script from that directory, for example
`bash setup_copy.sh && python3 rows_static.py`.

Known defect (AF-AP-223): `mutate.py` marks a mutant KILLED on any non-zero pytest exit and runs no unmutated control. It
passes `--basetemp bt/mut`, and pytest creates only the last part of that path, so without a `bt/` folder every run errors
at setup and every mutant reads KILLED. Create `bt/` first, and count a kill only when a test FAILED (S1-L1-R1 fixes a
copy that way). Measured by the coordinator on 2026-09-25: with `bt/` present, 7 of 8 mutants survive the builder's 91
tests; without it, all 8 read KILLED on "2 passed, 1 error".
