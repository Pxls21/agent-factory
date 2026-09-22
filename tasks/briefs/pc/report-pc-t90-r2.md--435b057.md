REVIEW-PENDING: F1 and F3 are repaired and self-validated. This remains a proposal until the sandbox adversarial-verifier grades it.

CHANGED

- scripts/pc_lane.sh:52-78
  - Trusts PC_LANE_SELF_COPY only when it equals $0 and PC_LANE_ORIG exists.
  - Clears inherited self-copy variables before the mktemp/cp/exec path.
  - EXIT trap removes only $0.

- scripts/pc_lane.sh:203-211
  - Replaces substring binding with cwd containment or exact NUL-delimited argv-token equality.
  - Accepts only the lane directory or lane-directory/brief.md.
  - Preserves paths containing spaces through base64 transfer.

- harness-ports/tests/test_pc_lane_dispatcher.sh
  - Adds sibling-suffix, argv-mention, exact-token, inherited-variable, and trap-ownership controls.

VERIFIED

- RED before repair: 33 passed, 4 failed.
- GREEN after repair, twice:
  pc_lane dispatcher: 37 passed, 0 failed
- Normalized outputs were bitwise identical.
- Five required mutants were killed by their named tests.
- bash -n passed for both shell files.
- Full harness suite:
  ALL SUITES PASSED
- Report lint:
  13 refs — OK 10, NEAR 3, MISS 0
- git diff --check: rc=0.
- Forbidden files, ledger, wiki, and PC runner remain untouched.

NOT DONE

- F2, F4, F5, F6, and F7 remain issue #20.
- No commit, push, PR, or external action.
- Independent verification has not run.

Full evidence report:

/home/rocco/agent-factory/.lanes/pc-t90-r2.md--435b057/tree/tasks/briefs/pc-t90-support/T90-R2-report.md
