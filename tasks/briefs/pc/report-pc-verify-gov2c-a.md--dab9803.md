Verified live: items 1–4 found no qualifying blocker. Recommendation: MERGE-READY for this split only.

Report written:
`/home/rocco/agent-factory/.lanes/pc-verify-gov2c-a.md--dab9803/tree/tasks/briefs/stage3-governance-support/VERIFY-GOV2c-A-report.md`

Key evidence:
- PIN `dab9803`; GOV2c files byte-identical to `b1dba7b`.
- `tests/test_governance_review.py`: `16 passed in 0.79s`.
- Six governance files: `49 passed in 0.94s`.
- F1 races: record flip, signature flip, and hardlink swap each measured `0/400` unsigned acceptances.
- F2/F6: BADSIG, expired-key, expired-signature, and revoked-key forms refused. Signing subkey accepted; VALIDSIG field 2 was the subkey and final field the primary key.
- Detached-signature cases: clear/inline signed messages rejected with `gpg: not a detached signature`; unrelated/tag signatures refused; binary detached signature accepted; trailing attacker block refused.
- `report_lint`: `8 refs — OK 8, ... MISS 0`.
- Scratch clean; no `/tmp/vg2c-a` gpg-agent remained.

Findings:
- INFO: brief’s six-file set ID is stale (`f3baa8cf79c7` versus measured `892ef4ebb5b8`); 49 tests collected and passed.
- INFO: a symlinked `reviews_dir` parent is followed, but unsigned data still refused. F8 covers final record/sig/key components.

Not done: master items 5–13 were intentionally left to the other split lanes. No production code changed.

GRAFT SAVED: ~17,853 tokens this turn.
