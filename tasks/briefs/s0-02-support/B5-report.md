# B5 report — S0-02 round 5 closure-oracle refusal hardening

PIN: `0c67ae9` · Lane: `pc-b5.md--0c67ae9` · Role: code-implementer · Venue: PC

This is a build-lane proposal, not a gate verdict. The sandbox-side adversarial-verifier lane owns the independent grade.

## Outcome

MERGE-READY — recommendation only. The closure oracle now fails loud on dynamic `$out` assignments and unresolved variable-target writer forms. The named B4-01 survivor and new assignment/target mutations are killed. Independent verification is NOT done here.

NOT done: the preferred structural execution control; live eight-leg capture; revoked-leg membership write; F3 execute-the-CLI strengthening; EXPIRED→mint; S0-11 re-sign; independent adversarial grade. These remain coordinator/owner work and were not attempted.

## Premise verification

VERIFIED. On a clean PIN archive I inserted `f="$out"` and `: > "$f/x-indirect"` after the runner's `out` assignment. The unchanged closure test returned `1 passed in 0.30s`, rc 0. Executing the same shell statements created `x-indirect` (`emitted=true`). This reproduced B4-01: the oracle omitted a real output write.

The other required red-before archive mutations also survived the PIN oracle:

- EDGE-VARIABLE-ASSIGN: `out2="$out"`, `1 passed in 0.33s`, rc 0.
- EDGE-VARIABLE-TARGET-WRITE: `tee "$g/y"` plus `cp /dev/null "$g/y"`, `1 passed in 0.35s`, rc 0.

The finding source was read whole from the harvested `tasks/briefs/pc/report-pc-verify-b4.md--95c0bb1.md`. The brief-named `tasks/briefs/s0-02-support/VERIFY-B4-report.md` is absent from this PIN.

## Implementation

VERIFIED. `_runner_output_writes` now inventories `static_roots` at `T:1411-1416`, identifies `variable_path` tokens at `T:1417`, and examines `dynamic_out_assignment` and `unresolved_variable_target` before the former no-literal-path skip at `T:1422-1449`.

A line is refused when it assigns a value containing `$out` to a variable, except the existing `local_first_t0` read form. Redirect, `tee`, `cp`, `mv`, `write_text`, and write-mode `open` are refused when their quoted target starts at a shell variable that is neither literal `out` nor a statically assigned non-output root. The real runner's `MARKERS`, `FD`, and other fixed roots therefore remain outside output closure, while an undeclared `$g/...` target fails loud.

The literal `$out/` writer grammar remains unchanged at `T:1451-1478`. The existing allow-list starts with `if (` at `T:1480-1487` and still covers grep / rm / deliver|collect_leg / --reuse / local_first_t0.

## Test-first evidence

RED before implementation: the added direct tests returned `8 failed in 0.66s`, rc 1. Every failure was the exact expected empty-`unrecognised` mismatch for the dynamic assignment/root or variable-target writer form.

GREEN after implementation: the direct assignment, indirect redirect, six variable-target writer cases, static non-output-root control, and unmodified runner closure returned `10 passed in 0.28s`, rc 0.

The tests at `T:1492-1525` assert exact refused line text and include a positive control for a statically assigned non-output root. The real closure test at `T:1528-1549` still binds the parsed producer/direct write sets to `C:143-152` and replay subleg closure.

## Named mutant inventory

| mutant / control | result | killer |
| --- | --- | --- |
| EDGE-VARIABLE-ROOT-BYPASS | KILLED: rc 1, `1 failed in 0.39s`; assignment and redirect named unrecognised | `unresolved_variable_target` at `T:1440-1449`, asserted through `direct_writes, unrecognised` at `T:1533-1534` |
| EDGE-VARIABLE-ASSIGN | KILLED: rc 1, `1 failed in 0.39s`; `out2="$out"` named unrecognised | `T:1422`, `T:1445-1449` |
| EDGE-VARIABLE-TARGET-TEE | KILLED: rc 1, `1 failed in 0.38s`; `tee "$g/y"` named unrecognised | `T:1423-1428`, `T:1440-1449` |
| EDGE-VARIABLE-TARGET-CP | KILLED: rc 1, `1 failed in 0.39s`; `cp ... "$g/y"` named unrecognised | `T:1429-1432`, `T:1440-1449` |
| CLOSURE-POSITIVE | PASS: included in `10 passed in 0.28s` | unmodified runner at `R:20-205`, closure at `T:1528-1549` |
| PRESERVED-B4-TEE | KILLED: rc 1, `1 failed in 0.39s`; extra `x-tee` reached set equality | `re.search` literal tee parser at `T:1460-1462`, then `assert producer_writes` equality at `T:1539-1540` |
| PRESERVED-B4-HEREDOC | KILLED: rc 1, `1 failed in 0.38s`; extra `x-heredoc` | redirect `re.search` at `T:1463-1468`, then `assert producer_writes` at `T:1539-1540` |
| PRESERVED-B4-PYTHON | KILLED: rc 1, `1 failed in 0.39s`; extra `x-python` | `write_text` parser at `T:1474-1478`, then `assert producer_writes` at `T:1539-1540` |
| PRESERVED-B4-MV | KILLED: rc 1, `1 failed in 0.38s`; extra `x-mv` | `re.match` mv parser at `T:1469-1473`, then `assert producer_writes` at `T:1539-1540` |

All runner mutations ran only in fresh PIN archives under lane scratch. No shared-tree mutation remained.

## Final file identity

| path | lines | git blob sha |
| --- | ---: | --- |
| `tests/test_s0_02_buzz_authz.py` | 1784 | `7fca45e05b07713bed4d04b6e0119343a54db5b1` |
| `proofs/S0-02/check_buzz_authz.py` | 762 | `039e4170f1d80fb397ef86d41be8daa3cacdf858` (read-only) |
| `proofs/S0-02/tools/pc/run_s0_02_legs.sh` | 205 | `3b5ebf178c482d0292558269d26cf6797e8f41d1` (read-only) |
| `tasks/briefs/s0-02-support/B5-report.md` | SELF | SELF |

The report's identity is self-referential. The coordinator can hash the harvested final bytes directly.

## Mechanical gates

The venue map requires two `-n 1` runs under the 420-second cap. Both fresh `git archive` runs copied only the changed test over PIN `0c67ae9`; test-set id and count agreed:

- `RESULT: rev=0c67ae9922e5 files=1 deleted=0 runs=1 tests=f0ba2500dd96 identical=yes rc=0 summary="216 passed in 95.00s (0:01:34)"`
- `RESULT: rev=0c67ae9922e5 files=1 deleted=0 runs=1 tests=f0ba2500dd96 identical=yes rc=0 summary="216 passed in 94.41s (0:01:34)"`

The two archive gates include the complete B4 test file. Its prior edge probes, tolerance/RUNNER-GAP relations, and LABEL-FALLBACK tests all stayed green without edits.

`/home/rocco/venv-agent-factory/bin/python -m pyflakes tests/test_s0_02_buzz_authz.py`: `pyflakes-rc: 0`.

`git diff --check`: `git-diff-check-rc: 0`.

Test anti-pattern screen:

`--- TEST_SCREEN over 1 path(s): 11 hits over 1 files ---`

- AF-AP-80: 7 unchanged source-shape assertions at `T:697`, `T:698`, `T:1003`, `T:1577`, `T:1578`, `T:1610`, `T:1633`.
- AF-AP-34: 4 unchanged defensive process-safety hits at `T:1641`, `T:1645`.

The final code-intel pack is `/home/rocco/agent-factory/.lanes/pc-b5.md--0c67ae9/scratch/B5-final-pack.md`. The brief-supplied `tasks/briefs/s0-02-support/B5-pack.md` was also read whole before edit.

## Code intelligence

VERIFIED before edit: Graft and Ripwire independently resolved one caller, `test_leg_file_table_matches_the_runner_writes`. `scripts/why.sh` tied the symbol to the B4 bounded-grammar commit. Clone GitNexus did not resolve `_runner_output_writes` and returned `risk: UNKNOWN`.

After edit, GitNexus `detect-changes` reported one file and low risk, but mislabeled the changed symbol as `test_deliver_normalizer_exposes_echo_provenance`; that result is not correctness evidence. Ripwire's file-level edit-check was ambiguous because report/pack files create four path-like contracts. The regenerated pack contains the post-edit skeleton, query, impact, caller, test-gate, and scanner output.

## Self-attack

1. The refusal could classify the runner's unrelated redirects as output writes. Ruled out by pre-inventorying static non-output roots, the dedicated `MARKERS` positive control at `T:1523-1525`, the unmodified runner closure control, and both 216-test archive gates.
2. The assignment exception could reopen B4-01. Ruled out by exact direct tests at `T:1492-1506` and fresh-archive EDGE-VARIABLE-ROOT-BYPASS/ASSIGN kills. Only the pre-existing `local_first_t0` read form is exempted; it remains on the allow-list at `T:1485`.
3. A variable-target writer branch could stop older literal `$out/` mutants from reaching set equality, yielding a different but hollow mechanism. Ruled out by rerunning all four B4 writer mutants: tee, heredoc, Python, and mv each failed on its extra file through closure equality.

## Evidence tiers

VERIFIED: PIN false-green reproduction plus emitted file; exact red-before direct tests; three required fresh-archive mutant kills; all four B4 writer-mutant kills; closure positive; two 216-test archive gates; pyflakes; diff check; final identities; scanner output.

INFERRED: the bounded refusal covers the pinned forms in the brief. It does not claim arbitrary shell dataflow analysis.

ASSUMED: none of the NOT-done coordinator/owner work has occurred elsewhere.

## Discrepancies and process hygiene

- The brief says `VERIFY-B4-report.md` is in `tasks/briefs/s0-02-support/`; only the harvested PC report is in this PIN. I used the harvested report, whose line 3 names the absent destination.
- The first four-file archive gate used system `python3` because `lane_gate.sh` invokes `scripts/test_summary.sh`, which invokes `python3`. It returned `33 failed, 183 passed` because `rfc3339-validator` was unavailable. With the venue-required venv first in `PATH`, the same gate passed twice. No product code changed for this environment error.
- The brief requests one `lane_gate.sh -n 2`; the newer venue map requires two `-n 1` calls under the terminal cap. The venue map wins. Both runs have the same set id and count.
- The first final-pack command passed two symbols after one `-s`; `lane_context.sh` treated the second as a file and refused rc 64. Re-running with the changed symbol produced the 179-line pack.
- The optional structural control was not added. Running the output-emitting section safely would require replacing its launch, key, network delivery, wait, and process-stop seams, outside this one-file parser-oracle repair. The deterministic refusal controls and fresh-archive runner mutations cover the pinned design without a fake emitter.
- Final bounded report lint: `report_lint: 38 refs — OK 26, NEAR 0, MISS 0, UNCHECKABLE 12, UNRESOLVED 0 (worktree)`. The 12 uncheckable rows are line inventories without claim tokens.

No background jobs, process kills, server actions, bridge calls, live relay/model requests, membership writes, role-key reads, credential reads, git write commands, or changes outside the brief's one test file occurred. All probes ran under lane scratch and self-terminated.

## GATE RECOMMENDATION

MERGE-READY — recommendation only. The implementation satisfies the frozen B5 design and kills every named blocker mutation on fresh archive copies. The proposal still requires the sandbox-side independent adversarial-verifier grade before acceptance.

Retro: register the specified anti-pattern at landing: a text-parser oracle keyed on a literal token silently skips indirect construction. Refuse constructions not statically resolvable to the closure table, or verify produced state. No additional skill lesson arose.
