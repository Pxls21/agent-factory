NOT-READY recommendation — **F-1** blocks T94’s executed-poll-probe test coverage.

→ **Blocker.** A scratch mutant double-escaped the `FAILED-UNRETRIED` branch lookup. It makes `$(cat lane.pid)` expand in the dispatcher instead of the PC shell, yet T2 still passed **48 passed, 0 failed**. The six executed cases omit an `API call failed` report with a dead loop, so they do not exercise that branch.

→ **Report written.** `tasks/briefs/pc-t90-support/VERIFY-T94-report.md`  
It contains the full finding inventory, contract mapping, reproduction, unverified items, and follow-ups.

→ **Verified.**
- T1 twice: **67 passed, 0 failed**
- T2 twice: **48 passed, 0 failed**
- T2’s six executed probe lines passed on Bash 5.2.37.
- `bash -n` passed for both scripts.
- Report lint: **17 refs — OK 16, NEAR 1, MISS 0**
- Full harness run failed only on the pre-existing Qwen matrix `SECOND_SIGINT` case; reproduced from a clean `4a38190` archive.

→ **Not claimed complete.** The hostile filesystem-marker matrix and remaining named mutation matrix are marked UNVERIFIED in the report. No production code changed; only the requested verification report is untracked.
