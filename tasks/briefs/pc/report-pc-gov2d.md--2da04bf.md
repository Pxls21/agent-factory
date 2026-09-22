PROPOSAL: GOV2d F1/F2 repair is implemented and self-validated. Independent sandbox verification is still required.

Changed:
  - Fixed gpg resolution to trusted absolute paths; caller PATH is no longer a trust channel.
  - Fixed child PATH to `/usr/bin:/bin`.
  - Added nonblocking, FD-level regular-file checks for record, signature, and owner key reads.
  - Added 8 regression tests and verifier-trust documentation.
  - Added the missing existing-relative-path case that kills the m6 mutant.

Verified:
  - Review suite: 24 passed twice under xdist; 24 passed serially.
  - Six-file governance set: 57 passed.
  - Mutation audit: 8/8 killed, with scratch-module import proofs.
  - gpg-agent census: 0 → 0.
  - AF-AP-115: 0.
  - pyflakes, py_compile, and git diff check: clean.
  - Report lint: 27 refs, 27 OK, 0 MISS, rc 0.

Files:
  - `src/agent_factory/governance/review.py`
  - `tests/test_governance_review.py`
  - `docs/governance/reviews/README.md`
  - `tasks/briefs/stage3-governance-support/GOV2d-report.md`

Not done:
  - Issue #18 items remain out of scope.
  - No gpg-agent cleanup was added.
  - No commit, push, or production service change was made.

Report:
`/home/rocco/agent-factory/.lanes/pc-gov2d.md--2da04bf/tree/tasks/briefs/stage3-governance-support/GOV2d-report.md`
