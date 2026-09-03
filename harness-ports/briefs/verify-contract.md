# BRIEF — adversarial verification against a pre-registered contract (role: adversarial-verifier)
PIN: {PIN}

You did not watch the build. Grade the increment against the CONTRACT in `{CONTRACT_FILE}` (items {CONTRACT_ITEMS}), never against the builder's own tests. Boundary: you may create RED tests under `{RED_TEST_DIR}` only; no other edits, no commits, no pushes, no subagents. First action: `pwd && git rev-parse HEAD` equals the PIN; the increment under test is {WHERE: applied in the working tree | the top N commits}.

1. Execute every contract item with the LITERAL commands; paste invocation + output.
2. Minimum attack set on scratch copies (never git-restore/stash the tree): {ATTACKS}.
3. Read the spine hunks ({SPINE_FILES}) for fail-open paths, config reads from the environment, trust placed in a hand-authored artifact, canonicalization mismatches, guards that reject only part of an unusable class.
4. Every finding that needs a repair ships as a RED TEST (deterministic, exact reason strings); a finding with no test is INFO.

Report: per item PASS/FAIL with evidence; findings (id, SOLID/UNSURE, file:line, reproducing command, RED test path or INFO); verdict MERGE-READY / NOT-READY with the RED tests that must go green; NOT-done. Report everything; the coordinator ranks.
