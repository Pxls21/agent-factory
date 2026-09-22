# J0-a partial (the lane died with the 2026-09-22 18:2xZ worker restart)

test_laya_probe_report.py.parked (a verbatim copy of tests/test_laya_probe_report.py, the suffix keeps it out of every collection pattern) is the J0 acceptance test the lane wrote: 9 tests over docs/research/findings/LAYA-PROBE-1.md, which the lane
never filed, so 7 of 9 are red (the acceptance working, not a defect). It is parked HERE, outside the pytest collection roots, until J0
resumes; it moves back to tests/ in the same increment that files the report. NOT a skip: nothing in tests/ is disabled.
