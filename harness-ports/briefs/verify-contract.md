# BRIEF — adversarial verification against a pre-registered contract (role: adversarial-verifier)
PIN: {PIN}

You did not watch the build. Grade the increment against the CONTRACT in `{CONTRACT_FILE}` (items {CONTRACT_ITEMS}), never against the builder's own tests. Boundary: you may create RED tests under `{RED_TEST_DIR}` only; no other edits, no commits, no pushes, no subagents. First action: `pwd && git rev-parse HEAD` equals the PIN; the increment under test is {WHERE: applied in the working tree | the top N commits}.

1. Execute every contract item with the LITERAL commands; paste invocation + output.
2. Minimum attack set on scratch copies (never git-restore/stash the tree): {ATTACKS}.
3. Read the spine hunks ({SPINE_FILES}) for fail-open paths, config reads from the environment, trust placed in a hand-authored artifact, canonicalization mismatches, guards that reject only part of an unusable class.
4. Classify every finding `BLOCKER` / `FOLLOW-UP` / `INFO` / `UNVERIFIED`. A `BLOCKER` ships a RED TEST (deterministic, exact reason strings) AND satisfies the WHOLE blocking predicate — contract-mapped, canonically reproduced through the real production path, materially effective, a concrete discriminator, in-boundary (skill `adversarial-verifier`; D-031). A red test is NECESSARY but NOT SUFFICIENT; a finding with no red discriminator, or one that fails the predicate, is `INFO`/`FOLLOW-UP`, never a repair item.

Report TWO outputs. (1) FINDING INVENTORY — no severity filter: per item PASS/FAIL with evidence; each finding (id, class, contract mapping or "none", canonical-path status, file:line, reproducing command, RED test path or INFO). (2) GATE RECOMMENDATION (exactly one): `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` (name the qualifying blockers + the RED tests that must go green) / `CONTRACT-INVALID`. Plus NOT-done. Report everything on discovery; the coordinator owns the final gate.
