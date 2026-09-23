PROPOSAL COMPLETE: T94 is self-validated. Independent adversarial verification is still required.

FILES

- harness-ports/bin/pc-lane.sh:137,516-543
  - Renames and preserves stale FAILED markers.
  - Uses Hermes usage.json as the structural verdict.
  - Preserves failed output separately.
  - Promotes an incremental draft only under the failed-session header.
  - Exits 70 with no report when no draft exists.

- scripts/pc_lane.sh:389,444-453
  - Binds FAILED to the current dispatch using brief mtime.
  - Rejects failed-session output from pre-fix runners.
  - Stores it under a non-report filename.

- harness-ports/tests/test_pc_lane.sh:536-633
  - Adds runtime-verdict, warning, preservation, success, and stale-marker controls.

- harness-ports/tests/test_pc_lane_dispatcher.sh:387-414
  - Adds dispatcher defense, promoted-draft, and stale-marker controls.

- tasks/briefs/pc-t90-support/T94-report.md
  - Full 224-line evidence report.
  - SHA-256: 76adeba5b07c4ca9171da063de31b253d88d1aad570f4581e41dd07584810818

VERIFIED

- Shell syntax: rc 0.
- Diff check: rc 0.
- Runner suite, twice:
  - 67 passed, 0 failed
  - 67 passed, 0 failed
- Dispatcher suite, twice:
  - 42 passed, 0 failed
  - 42 passed, 0 failed
- Six scratch-copy mutants were killed:
  - m1: 64 passed, 3 failed
  - m2: 66 passed, 1 failed
  - m3: 64 passed, 3 failed
  - m4: 66 passed, 1 failed
  - m5: 41 passed, 1 failed
  - m6: 41 passed, 1 failed
- Report lint:
  - 31 refs
  - OK 12
  - NEAR 3
  - MISS 7
  - UNCHECKABLE 9
  - UNRESOLVED 0
  - Minimum-reference floor passed.

FULL HARNESS

run-all.sh remains red:

- test_pc_lane.sh: 67 passed, 0 failed
- test_pc_lane_dispatcher.sh: 42 passed, 0 failed
- test_qwen_matrix_sh.sh: 18 passed, 1 failed
- RUN_ALL_RC=1

The same qwen-matrix SECOND_SIGINT failure reproduced on the feb26d7 PIN. It is pre-existing, outside the T94 boundary, and was not changed.

DISCREPANCIES

- The requested report-draft.md was initially absent; report.attempt1.md contained only the route refusal. The substantive predecessor report was recovered and revalidated.
- lane_gate.sh invokes pytest and cannot run these shell suites. The brief-prescribed shell gates were run directly.
- GitNexus used a stale clone index and reported no detached-worktree changes. This was not treated as evidence of low risk.
- Original suite baselines were 60 and 39; T94’s added assertions raise them to 67 and 42.

NOT DONE

- No independent adversarial-verifier run.
- No final gate verdict.
- No live lane, bridge, real Hermes request, or server action.
- No commit, push, or outward-facing action.
- No fix to the unrelated qwen-matrix failure.

Full report:
tasks/briefs/pc-t90-support/T94-report.md
