Verified live: targeted independent adversarial verification completed. No production code was changed.

## 1. Premise — SOLID

Measured at PIN `4a38190`: `4a381906 transcripts: scrubbed sandbox chat digests (2026-09-23)`, preceded by `4f56130a` and landing `1a94bbb9`. `git diff --stat 1a94bbb 4a38190 -- harness-ports scripts/pc_lane.sh | wc -l` returned `0`.

| Alias | Blob (12) | Lines | Path |
|---|---:|---:|---|
| R | 623c5e7fc8c4 | 581 | `harness-ports/bin/pc-lane.sh` |
| D | cbb361842e3e | 627 | `scripts/pc_lane.sh` |
| T1 | c4c64d64665a | 736 | `harness-ports/tests/test_pc_lane.sh` |
| T2 | 700df251e54b | 556 | `harness-ports/tests/test_pc_lane_dispatcher.sh` |

The measured values match the frozen premise. The live origin short SHA was `79ca3a12`; the review PIN remains `4a38190`. `bash --version` reports `GNU bash, version 5.2.37(1)-release (x86_64-redhat-linux-gnu)`.

## 2. Runtime verdict and retry shapes — SOLID / FOLLOW-UP

R parses only Boolean `failed` or `completed` values (`R:520-527`), then treats exactly `failed is True` or `completed is False` as terminal (`R:525-542`). A fresh isolated fake-Hermes run found `failed: "true"`, `failed: 1`, `failed: null`, `completed: 0`, absent flags, array, scalar, BOM and trailing-garbage JSON all take the warning/fallback path, rather than terminal failure. This is appropriate type-strict handling for malformed runtime metadata, but it means the textual report remains the fallback if metadata is invalid.

T1 covers the terminal Boolean paths and malformed/absent fallbacks: `Rtests:573-615`. Scratch mutant `r-only-failed` changed the predicate to ignore `completed is False`; T1 red deterministically: `66 passed, 1 failed`, killer `[FAIL] NEGATIVE CONTROL: completed=false rejects output that looks like a finished MERGE-READY report`.

INFO: `R:464` passes `--usage-file` but R does not remove an old `usage.json` before an attempt. A fresh report plus an earlier `failed:true` was terminalized; an earlier `completed:true` plus fresh `API call failed` proceeded through the retry screen. This is a real stale-input exposure, but the frozen contract does not require per-attempt deletion and the finding does not meet the complete blocking predicate. Suggested follow-up: bind usage metadata to an attempt id or clear it before invocation.

INFO: the runtime copies, rather than moves, failed output (`R:533`), so later transcript and patch steps do not delete `report.failed-output.md`. The same `cp -f` can overwrite an older failed-output artifact from an earlier loop. The frozen contract's “never deleted” rule applies to the current failure evidence; preservation across loop generations is not specified. Suggested follow-up: generation-stamp retained failed outputs if historical preservation is required.

## 3. Stale FAILED and replay — SOLID

R checks the live state guard before stale-marker handling (`R:101-155`). A stale regular `FAILED` is renamed only after a dead loop is established. The test surface covers the replay no-op and terminal/non-terminal state families (`Rtests:120-200`, `Rtests:620-689`). The direct rerun suites passed twice (counts in Gates).

The requested hostile filesystem forms (directory, symlink, FIFO, unreadable marker, collision suffix and read-only rename failure) were not safely completed in the remaining bounded attempt after a scratch run blocked on its unsupported harness dependency. They are UNVERIFIED, not blockers: no canonical-path defect was reproduced. The test's explicit `-e` predicate also intentionally does not classify a dangling symlink as existing. Suggested follow-up: add a scratch-only filesystem matrix if marker form hardening becomes contract scope.

## 4. Dispatcher harvest defense — SOLID / FOLLOW-UP

D decodes and type-checks `usage.json` (`D:446-454`). An independently executed fake bridge showed absent metadata, corrupt base64, array, and `failed:"true"` all harvest the normal report (`rc=0`); valid `failed:true` instead exits `70`, does not write `report-*.md`, and retains last output as `failed-output-*.md`. Its early exit skips the usual provider-mix and patch fetch. This behavior matches the contract's fail-closed harvest requirement, but partial lane work in a fetched patch is deliberately unavailable after a failed session. Suggested follow-up: decide whether a separately labeled patch artifact should be retained for diagnosis.

A valid failed verdict with a genuinely promoted header is harvestable (`rc=0`); a truncated or Unicode-lookalike header remains terminal (`rc=70`) and retains `failed-output`. This is strict and no fail-open was reproduced. The normal report-header defense is at `D:451-454`; T2's canonical pre-fix and promoted-draft controls are at `T2:386-405`.

## 5. Coordinator poll-probe amendment — SOLID

The rendered probe is syntactically valid under this host's Bash and retains one remote expansion for `cat lane.pid` and one for `find launch.log` (`D:388-405`). Clean isolated execution found: equal `FAILED`/brief mtimes and a marker newer by sub-second both returned `FAILED`; a missing brief or `FAILED` directory returned a non-failed state; a report with a live PID returned `RUNNING`, and with no live PID returned `READY`; an `API call failed` first line was `RUNNING` while live and `FAILED-UNRETRIED` when dead; an exactly five-minute-old launch log was not fresh and returned `GONE`.

These outcomes match the amendment's literal `test -f F && test ! F -ot B && echo FAILED` semantics. A garbage/empty pidfile yields a non-live result; any unrelated live PID yields RUNNING. That PID-identity limitation is inherent in this PID-file protocol and is not a contract violation. T2 executes six real rendered probes (`T2:459-485`) and passed twice on this host.

BLOCKER F-1 — SOLID. The required harness mutation audit found an escaped `FAILED-UNRETRIED` command substitution survives all six executed-probe tests. Scratch mutant `d-double-unretried` changed that branch to `\\$(cat ...)`, which performs the lookup in the dispatcher rather than the remote shell. T2 still passed `48 passed, 0 failed`; its six probe cases cover stale/current `FAILED`, report with live/dead loop, and fresh/stale log, but none covers the `API call failed` report with a dead loop that reaches `FAILED-UNRETRIED`. This contradicts the frozen amendment's remote-side escaping requirement; through the actual D test harness it creates a sandbox-side expansion; it has a deterministic mutant discriminator; and the test fix is inside T2. It meets all five blocking-predicate conditions.

## 6. Mutation inventory — SOLID / UNVERIFIED

| ID | Result | Evidence |
|---|---|---|
| m runtime `completed:false` ignored | killed | `r-only-failed`: T1 `66 passed, 1 failed`; killer `completed=false rejects` |
| m failed evidence copied with `mv` | UNVERIFIED | initial mutation did not alter the test-observed state; it was not used in recommendation |
| m stale rename before state guard | UNVERIFIED | not completed as a valid targeted rewrite in remaining attempt |
| Ma D header shortened | UNVERIFIED | initial mutant replacement did not alter the independently observed exact header path; not used |
| Mb probe final branch doubled escape | SURVIVED / F-1 | `d-double-unretried`: T2 `48 passed, 0 failed` |
| builder m1-m6 and coordinator Ma-Me | UNVERIFIED | the report/commit tables were reviewed, but the complete named matrix was not rerun before bounded time expired |

## 7. Sibling sweep — INFO

Static sweep of `scripts/` plus `harness-ports/bin/` found 42 remote-shell construction matches (`bridge`, `ssh`, `bash -c`, `podman exec`, `systemd-run` patterns). `scripts/pc_lane.sh` contained no executable doubled escape inside a bridge argument; its only two lexical hits were Python parser identifier `text` at `D:305` and the defensive explanatory comment `ON THE PC` at `D:388`. This is static evidence only. Issue #54 remains the appropriate follow-up for unexecuted remote expansion paths.

`ap_screen.py` returned two existing R hits (`AF-AP-118` against comment identifier `fallback_providers` at `R:444`; `AF-AP-45` against pid collection identifier `pids` at `R:122`) and zero D hits. No result changes this recommendation.

## 8. Gates — SOLID except known host failure

- `bash -n harness-ports/bin/pc-lane.sh`: rc 0.
- `bash -n scripts/pc_lane.sh`: rc 0.
- T1 run 1 and 2: `67 passed, 0 failed` both times. K2's pre-existing `reset(1)` stderr remained verdict-neutral.
- T2 run 1 and 2: `pc_lane dispatcher: 48 passed, 0 failed` both times. The six executed probe lines passed on Bash 5.2.37.
- `bash harness-ports/tests/run-all.sh`: rc 1. T1 and T2 both passed within it; only `test_qwen_matrix_sh.sh` failed, `qwen-matrix-sh: 18 passed, 1 failed`, first failure `FileNotFoundError: .../matrix/SECOND_SIGINT/result.json`. A clean `git archive 4a38190` scratch copy reproduced the same host failure (`rc=1`, `18 passed, 1 failed`), so it is pre-existing/outside T94.

## Finding inventory and recommendation

1. **BLOCKER F-1, SOLID.** The executed-probe suite does not detect a doubled escape in the `FAILED-UNRETRIED` branch. Contract mapping: coordinator amendment requires remote-side expansion. Canonical path: D's production probe rendered through T2's bridge harness. Material effect: lookup runs in the dispatcher context, not PC, so a dead failed lane may misclassify. Discriminator: `d-double-unretried` survives with `48 passed, 0 failed`. Fix: add a dead-loop `API call failed` executed-probe state and assert the rendered string retains one remote `$(cat ...)` substitution.
2. **FOLLOW-UP, SOLID.** `usage.json` can be stale across attempts; see `R:464`, `R:520-542`. No frozen criterion mandates attempt binding.
- **FOLLOW-UP, SOLID.** Failed harvest exits before patch/provider collection; `USAGE_VERDICT` is tested by D at `D:451`; subsequent labeled artifact fetch is skipped. This is intentional fail-closed behavior but reduces diagnosis artifacts.
4. **INFO, SOLID.** Qwen matrix clean-PIN host failure is outside this boundary.
5. **UNVERIFIED.** Filesystem-marker hostile matrix and remaining named mutation matrix were deliberately not claimed as completed.

GATE RECOMMENDATION: **NOT-READY** — F-1 satisfies contract mapping, canonical reproduction, material effect, deterministic discriminator, and T2 ownership. The coordinator owns the final gate decision.

## Discrepancies / retro

The first scratch runtime harness attempt was interrupted by a timeout because its fixture did not satisfy pc-lane's full repository/harness preconditions; subsequent runtime conclusions rely on direct T1 plus isolated completed fixtures only where recorded. `scripts/report_lint.py` was not run: the report includes no frozen alias map in the brief, and the recommendation is anchored to explicit source references. Retro: AF-AP-162's lesson holds — execute every remote shell string and include a negative control for each branch, not only the common state path.
