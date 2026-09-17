# B4 report — S0-02 round 4 closure repairs

PIN: 6760808 · Lane: pc-b4.md--6760808 · Role: code-implementer · Venue: PC

This is a build-lane proposal, not a gate verdict. The sandbox-side adversarial-verifier lane owns the independent grade.

## Outcome

MERGE-READY — recommendation only. B3-01, B3-02, B3-03, and B3-00 are closed by this proposal and its deterministic controls. Independent verification is NOT done here.

NOT done: live eight-leg capture; revoked-leg relay membership write; EXPIRED→mint; S0-11 re-sign; independent adversarial grade. These remain coordinator/owner work and were not attempted.

## Item 1 — closure table derived from every runner write

VERIFIED. The final test defines `_runner_output_writes`, documents the bounded writer grammar, and has dedicated branches for `tee`, shell redirection, `mv`, Python `write_text` / write-mode `open`, and refused unknown forms. The same final test defines `test_leg_file_table_matches_the_runner_writes`, unions direct runner writes with producer writes, asserts exact equality with `_LEG_FILES_PLAIN` and `_LEG_FILES_REVOKED`, and binds `removed_nested` plus `REPLAY_SUBLEGS`.

Premise red-before on clean 6760808 archives:

- RUNNER-TEE-UNSEEN: `rc=0`, `1 passed in 0.31s`.
- RUNNER-HEREDOC-UNSEEN: `rc=0`, `1 passed in 0.30s`.
- RUNNER-PYTHON-UNSEEN: `rc=0`, `1 passed in 0.31s`.
- RUNNER-MV-UNSEEN: `rc=0`, `1 passed in 0.30s`.

Green-after / mutant kills on working-tree test bytes copied over fresh 6760808 archives:

- CLOSURE-POSITIVE: unmutated runner, `1 passed in 0.26s`.
- RUNNER-TEE-UNSEEN: `rc=1`; `T:1465` reported extra `x-tee`.
- RUNNER-HEREDOC-UNSEEN: `rc=1`; `T:1465` reported extra `x-heredoc`.
- RUNNER-PYTHON-UNSEEN: `rc=1`; `T:1465` reported extra `x-python`.
- RUNNER-MV-UNSEEN: `rc=1`; `T:1465` reported extra `x-mv`.

The parser is intentionally bounded. It does not claim shell dataflow analysis.

## Item 2 — replay tolerance relation and runner gap

VERIFIED. The final replay-window test keeps both loose `REPLAY_CLOCK_TOLERANCE_S` checks, adds the `< checker.RELAY_DRIFT_WINDOW_S` relation, parses `TURN_WAIT_S` from the runner, and compares `turn_wait.group(1)` with `REPLAY_CLOCK_TOLERANCE_S`. The runner source default is `R:34`.

Premise red-before on clean 6760808 archives:

- TOLERANCE-9000: `rc=0`, `1 passed in 0.30s`.
- RUNNER-GAP-151: `rc=0`, `1 passed in 0.31s`.

Green-after / mutant kills:

- TOLERANCE-POSITIVE: unmodified constants and runner, `1 passed in 0.26s`.
- TOLERANCE-9000: `rc=1`; the named relation failed because `(9000 + 120) < 900` is false.
- RUNNER-GAP-151: `rc=1`; the named runner-gap relation failed because `151 <= 150` is false.

No `spec.json` failure key exists for this relationship, so none was invented.

## Item 3 — dead removal-receipt fallback deleted

VERIFIED. I took the DELETE branch. `C:675-685` iterates every `LEG_NAMES` entry before the summary; `LEG_NAMES` includes `revoked`. A missing revoked directory therefore fails inside `_check_leg` before the summary. A passing revoked leg sets the only non-None `removal_note`. The fallback was unreachable in every graded path and is removed at `C:717`.

The missing-revoked test deletes the `revoked` leg and asserts `revoked: revoked leg directory absent` plus the no-fallback `removal_line = removal_note` source shape. The behavioral test defines `drop_revoked_note` and proves the summary `line.endswith("; None")` rather than synthesizing a label.

Premise red-before on a clean 6760808 archive:

- LABEL-FALLBACK-DROPPED: altered fallback only, `rc=0`, `2 passed in 1.50s`.

Green-after / mutant kill:

- REMOVAL-POSITIVE: pass bundle, missing-revoked negative, forced-None behavior, and both label tests, `5 passed in 4.73s`.
- LABEL-FALLBACK-DROPPED: `rc=1`, `2 failed, 1 passed in 3.65s`; both the source assertion and the behavioral forced-None note probe killed the restored altered fallback.

## Item 4 — B3 stamp and report discipline

VERIFIED. The exact required `STAMP 2026-09-17 (B4)` line is directly under the B3 report title. This report contains the final identity table, line anchors, red-before/green-after evidence, named mutants, scanners, pack, gate output, self-attack, discrepancies, gaps, and recommendation.

## Final file identity

| path | lines | git blob sha |
| --- | ---: | --- |
| `proofs/S0-02/check_buzz_authz.py` | 762 | `039e4170f1d80fb397ef86d41be8daa3cacdf858` |
| `tests/test_s0_02_buzz_authz.py` | 1710 | `b2532d08fc41eb966dd12d85444c5dd02c39f40d` |
| `tasks/briefs/s0-02-support/B3-report.md` | 167 | `22843dffb7a3624659cb03b16dcee9264af85130` |
| `pack.md` | 225 | `2f77907a362f1d54cc6ad660d1eec5772fba4188` |
| `tasks/briefs/s0-02-support/B4-report.md` | SELF | SELF |

The report's own identity is self-referential and therefore cannot be embedded without changing itself. The coordinator can hash the harvested final report bytes directly.

Runner and producer were read-only. `proofs/S0-02/spec.json` was unchanged.

## Named mutant inventory

| mutant / control | result | killer |
| --- | --- | --- |
| CLOSURE-POSITIVE | PASS: `1 passed in 0.26s` | final `test_leg_file_table_matches_the_runner_writes` |
| RUNNER-TEE-UNSEEN | KILLED: rc 1, extra `x-tee` | final `_LEG_FILES_PLAIN` equality |
| RUNNER-HEREDOC-UNSEEN | KILLED: rc 1, extra `x-heredoc` | final `_LEG_FILES_PLAIN` equality |
| RUNNER-PYTHON-UNSEEN | KILLED: rc 1, extra `x-python` | final `_LEG_FILES_PLAIN` equality |
| RUNNER-MV-UNSEEN | KILLED: rc 1, extra `x-mv` | final `_LEG_FILES_PLAIN` equality |
| TOLERANCE-POSITIVE | PASS: `1 passed in 0.26s` | final `REPLAY_CLOCK_TOLERANCE_S` relations |
| TOLERANCE-9000 | KILLED: rc 1, `(9000 + 120) < 900` false | final `RELAY_DRIFT_WINDOW_S` relation |
| RUNNER-GAP-151 | KILLED: rc 1, `151 <= 150` false | final `turn_wait.group(1)` relation |
| REMOVAL-POSITIVE | PASS: `5 passed in 4.73s` | final `drop_revoked_note` tests |
| LABEL-FALLBACK-DROPPED | KILLED: rc 1, `2 failed, 1 passed` | final `removal_line = removal_note` and `line.endswith("; None")` tests |

All mutants ran only in fresh scratch archives. No shared-tree reset, checkout, stash, or mutation occurred.

## Mechanical gates

Baseline on unedited 6760808 with the PC inputs and an absolute scratch basetemp: `137 passed in 77.41s (0:01:17)`.

Final focused suite via `scripts/test_summary.sh`: `139 passed in 79.44s (0:01:19)`; `pytest-exit: 0`.

Four-file gate set: `f0ba2500dd96`. Pre-edit collection was 205 tests: 137 + 22 + 35 + 11. Final adds two tests, so the set has 207.

The venue map says split two repetitions into `-n 1` calls under the 420-second Hermes cap. Both fresh `git archive` runs copied the five lane artifacts over 6760808 and agreed:

- `RESULT: rev=6760808626ea files=5 deleted=0 runs=1 tests=f0ba2500dd96 identical=yes rc=0 summary="207 passed in 95.76s (0:01:35)"`
- `RESULT: rev=6760808626ea files=5 deleted=0 runs=1 tests=f0ba2500dd96 identical=yes rc=0 summary="207 passed in 95.20s (0:01:35)"`

`python -m pyflakes proofs/S0-02/check_buzz_authz.py tests/test_s0_02_buzz_authz.py`: `pyflakes-rc=0`.

`bash -n proofs/S0-02/tools/pc/run_s0_02_legs.sh`: `bash-n-runner-rc=0`.

`git diff --check`: rc 0.

## Scanner and code-intel evidence

Production scanner paste:

`--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---`

Test scanner paste:

`--- TEST_SCREEN over 1 path(s): 11 hits over 1 files ---`

- AF-AP-80: 7 hits at `T:697`, `T:698`, `T:1003`, `T:1503`, `T:1504`, `T:1536`, `T:1559`. RUN classification: the two new hits deliberately bind removal of an unreachable fallback; the five older source-shape assertions are unchanged.
- AF-AP-34: 4 hits at `T:1567`, `T:1571`. RUN classification: unchanged defensive no-process-name-kill gate and its own documented tokens.

The requested code-intel pack is attached as `/home/rocco/agent-factory/.lanes/pc-b4.md--6760808/tree/pack.md`. It was regenerated after the final code edit. It contains the skeletons, query, symbol sections, scanner output, and ripwire test-gate. The pack reports GitNexus and code-review-graph as unmapped in the lane tree; the mandated clone-index `impact` and `detect-changes` commands were also run separately. Clone GitNexus was 233 commits stale and returned UNKNOWN for unresolved test symbols; post-edit `detect-changes` said `Changes: 3 files, 4 symbols`, `Affected processes: 0`, `Risk level: low`, but misidentified changed symbols, so it is not used as correctness evidence. Ripwire's final test-gate reported `changed="1" impacted="27" tests="4" untested="0"`; it is advisory and over-broad relative to the brief's pinned gate.

## Self-attack

1. The bounded parser could miss a new writer that constructs `$out` indirectly. Ruled out for the frozen contract by enumerating every current literal `$out` occurrence in `R`; future unknown literal forms fail closed. Indirect variable propagation is outside the documented grammar and is not claimed.

2. The parser could confuse reads/removals with writes. Ruled out by the separate allowed non-writer forms, exact direct-write set equality, replay subdirectory assertion, `.probe` removal assertion, and four writer-form mutations.

3. Deleting the fallback could expose `None` on a legitimate graded path. Ruled out by the canonical leg loop and by a negative bundle missing `revoked`, which fails before summary construction. The `drop_revoked_note` control confirms `line.endswith("; None")`, so no fallback supplies a label.

## Evidence tiers

VERIFIED: final source/test behavior, seven mutant kills, three positive controls, 139-test component suite, two 207-test archive gates, pyflakes, bash syntax, scanner output, final identities, and B3 stamp.

INFERRED: the bounded parser covers the permitted grammar, not arbitrary shell/Python dataflow; the line-by-line source analysis plus four named mutations is the basis.

ASSUMED: none of the NOT-done live capture, membership write, EXPIRED→mint, S0-11 re-sign, or independent grade has occurred elsewhere.

## Discrepancies and process hygiene

- The brief's pack command places three symbols after one `-s`; `lane_context.sh` accepts one symbol per `-s`. I used three `-s` flags. The first literal attempt refused with `lane_context: FILE absent: removal_note`.
- Initial baseline without an explicit basetemp hit `/tmp` inode exhaustion: `1 failed, 113 passed, 23 errors` with `No space left on device`. `/tmp` was 94% inode-used. Re-running with the venue-required absolute lane-scratch basetemp yielded the clean 137-pass baseline.
- First four-file archive gate selected system `/usr/bin/python3`, so 33 tests failed on missing `rfc3339-validator`. With the venue-mapped venv first in PATH, the same archive gate passed twice at 207. This matches the older B2 report's recorded venue dependency; no product code changed for it.
- The brief asks for one `lane_gate.sh -n 2` call, while the current venue map says `-n 1` twice under the 420-second Hermes cap. The current venue map wins. Counts and set id agreed.
- `ripwire_review.sh edit-check` could not disambiguate the checker path because report/pack files also define path-like contracts. The final `test-gate` command succeeded and is reported above.
- Report lint was run last under the bounded rule: `report_lint: 16 refs — OK 3, NEAR 4, MISS 0, UNCHECKABLE 9, UNRESOLVED 0 (at 6760808)`. The four NEAR rows are the four named runner mutants citing the exact equality assertion one line from the matched token. The nine UNCHECKABLE rows are the scanner location inventory, which intentionally carries only line numbers.

No background jobs, process kills, server actions, bridge calls, live model/relay requests, membership writes, credential reads, or git write commands occurred. All probes ran in this lane's scratch directory and self-terminated.

## GATE RECOMMENDATION

MERGE-READY — recommendation only. The B4 implementation satisfies the frozen brief and kills every named blocker mutant on fresh archive copies. The proposal still requires the sandbox-side independent adversarial grade before acceptance.

Retro: no new general anti-pattern beyond the already documented basetemp/inode and PATH venue hazards; nothing to bake into a skill from this lane.
