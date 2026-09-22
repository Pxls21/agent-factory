NOT-READY recommendation for GOV2c items 1, 5, 6, 8.

→ **F1 blocker:** caller-controlled `PATH` selects a fake `gpg`; real `verify_review` accepts an unsigned record. Fresh discriminator: fake path accepted; real `/usr/bin/gpg` refused `fubuki-review-signature-invalid`.

→ **F2 blocker:** a FIFO swapped after `is_file()` hangs real `verify_review`: `timeout 10` → `rc=124`, `wall_ms=10003`.

→ **Verified:** declared-input gates re-ran clean: `16 passed in 0.73s`; six-file set `49 passed in 0.96s`. Size boundary and hostile-environment probes re-ran. Lane-owned gpg-agent census is `0`.

→ **Report:** `tasks/briefs/stage3-governance-support/VERIFY-GOV2c-B-report.md`  
`report_lint`: `14 refs — OK 13, NEAR 1, MISS 0, UNCHECKABLE 0, UNRESOLVED 0`; rc 0.

→ **Not done:** master items 2–4, 7, and 9–13 belong to other lanes. No commit or push.
