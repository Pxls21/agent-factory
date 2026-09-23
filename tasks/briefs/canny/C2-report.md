C2 BUILD REPORT — REVIEW-PENDING

STATUS

REVIEW-PENDING: C2 is implemented and self-validated. This build lane cannot issue a gate verdict. Independent adversarial verification and a real Hermes-lane smoke run remain NOT done.

NOT DONE / BLOCKERS

- NOT live-tested through Hermes. The boundary forbids reading `~/.hermes/` or running Hermes. The coordinator must test the installed hook after landing.
- NOT enabled by the dispatcher. Forwarding `LANE_DONE_GATE` from `scripts/pc_lane.sh` is explicitly outside C2.
- Full `harness-ports/tests/run-all.sh` is red on an unrelated read-only suite: `test_qwen_matrix_sh.sh` reports `qwen-matrix-sh: 18 passed, 1 failed`, with `FileNotFoundError` for `SECOND_SIGINT/result.json`. It reproduced twice. C2 suites inside run-all remain green. Boundary rules prohibit fixing the qwen matrix files here.
- The full raw 109-command corpus was not present in the lane tree and the boundary forbids reading its source profiles. The coordinator supplied the 0/109 baseline and representative command classes. The committed test reclassifies all 12 supplied classes, not 109 raw rows.

PREMISE — VERIFIED 2026-09-23T19:11:58Z

- PIN: HEAD and `origin/claude/soundbox-kit-migration-iz1jwf` were `4a381906c89f` at premise check.
- `git log --format='%h %s' -2 4a38190` returned `4a381906 transcripts: scrubbed sandbox chat digests (2026-09-23)` and `4f56130a ledger plane 18:4xZ: T94 LANDED ...`.
- Blob/line identities matched the brief: lane-profile `145d8c40abcb`/209; test_lane_profile `02bc97314c56`/152; run-all `6c45009c3486`/78; verify_command `daf605f480a0`/351; test_verify_command `6af9a516adf5`/490.
- All three create targets were absent. The existing profile baseline was `lane profile: 9 passed, 0 failed`.
- C1 had three `VERIFY` patterns. It accepted the six supplied pytest interpreter forms and the stock cargo/npm/make/ruff checks. It rejected all supplied project runner and pipefail-wrapper forms. This matched the brief.
- The Hermes payload excerpts and 109-command corpus are coordinator read-only measurements. I did not read `~/.hermes/`. Fixtures use the supplied shapes.
- `canny:39-50` (option 1 `Port the deterministic core as first-party code`, item 2 `done-gate predicate`): the selected stale-check predicate — "code changed since the last passing check".

IMPLEMENTATION

- `gate:24-44` (`CODE_SUFFIXES`, `PROJECT_PATTERNS`, `PATCH_PATH`, `RC_WRAPPER`): closed code-suffix list, project command patterns, V4A path matcher, and the exact pipefail/tee wrapper grammar.
- `gate:54-58` (`ledger_file`): ledger names use the repository-root SHA-256 prefix plus sanitized session id under the OS temp directory.
- `gate:85-97` (`counts_as_check`): passes C1's three pattern strings plus project patterns to `is_verify`; a separate narrow recognizer handles the rc wrapper.
- `gate:110-179` (`_result_exit_code`, `record`): the recorder validates integer-not-bool exit codes, records not-passing reasons, expands V4A paths, keeps stdout empty, and reports one-line errors on stderr.
- `gate:207-292` (`_is_code`, `gate`): the gate enforces the closed code-file rule, compares edit/check sequence order, handles unknown terminal-only ordering, names at most five paths, omits `final_response`, and bounds the JSON directive to 1,500 bytes.
- `profile:25-85` (`verify_lane`): verify accepts either the ordinary semantic clone or exactly the two done-gate hooks and refuses all other semantic deltas.
- `profile:89-277` (`create_lane`): create keeps switch-OFF bytes unchanged; switch ON appends the recorder after existing post-tool hooks and installs one pre_verify directive. Hook commands resolve from the helper's main repository root, not a lane tree.
- `gatetest:93-382` (`test_order_and_gate`, `test_classifier_and_bash_grade`, `test_corpus_reclassification`): deterministic recorder, gate, classifier, bash-grade, corpus-class, location, ordering, truncation, malformed-input, and negative-control tests.
- `profiletest:155-240` (`GATE_OFF`, `GATE_ON`): switch-OFF byte identity, exact switch-ON hooks, verify-with-either-form, third-entry rejection, and changed-command rejection.
- `runall:12-13` (`test_lane_done_gate.py`): registers the new Python test.
- `gate:46-58` (`_warn`, `ledger_file`) keeps observer diagnostics on stderr and per-session ledgers under the OS temp directory.
- `gate:61-82` (`_classifier`, `_is_direct_check`) loads C1 unchanged and rejects status-hiding suffixes on project runners.
- `gate:128-142` (`_edit_paths`) records replace-mode paths and deduplicates every V4A add/update/delete/move path.
- `gate:182-204` (`_facts`, `_relative`) reads ordered facts and normalizes absolute or relative paths against the pinned repository root.
- `gatetest:125-159` (`test_exit_codes_and_bad_result`) pins nonzero, missing, string, bool, malformed-JSON, and absent-result failure behavior.

PROJECT CHECK LIST AND BASH GRADE

Accepted direct shapes:

1. C1 checks, including pytest in the supplied interpreter, timeout, and environment-prefix forms; cargo/npm/make and supported lint/build checks remain accepted.
2. `bash harness-ports/tests/<name>.sh`.
3. `python3 harness-ports/tests/test_<name>.py`.
4. `bash scripts/lane_gate.sh ...`.
5. `bash scripts/test_summary.sh ...`.
6. The exact wrapper `set -o pipefail; <accepted check> | tee <file>; rc=${PIPESTATUS[0]}; [one printf/echo;] exit "$rc"`.

Rejected shapes include `bash -n`, pyflakes-only commands, plain output commands, unguarded pipelines, `PIPESTATUS[1]`, fixed `exit 0`, extra `true`, `|| true`, backgrounding, trailing commands, missing pipefail, a non-test path, and a leading command before a project runner.

`bash -n` is rejected because it proves parseability, not changed behavior. It cannot cover an implementation by itself.

Bash grade: 16/16 accepted shapes exited nonzero with the failing stub and zero with the passing stub. Classifier negative control: 16/16 near misses rejected.

Corpus classification:

- Before: coordinator-supplied `0/109` under C1.
- After, available data: `7/12` supplied representative command classes count. The counted classes are direct project shell/Python runners, exact rc wrappers, test_summary, and C1 pytest forms. The rejected classes are post-processed commands whose final status does not prove the check, `bash -n`, pyflakes/screen chains, and reads.
- Exact full after-count for all 109 raw commands is NOT claimed because those raw commands are not in this lane's allowed inputs.

RED / GREEN

- First resumed run of `python3 harness-ports/tests/test_lane_done_gate.py`: `lane done gate: 14 passed, 2 failed`. It exposed one widened `&& true` shape and one representative-table expectation error.
- First resumed run of `bash harness-ports/tests/test_lane_profile.sh`: `lane profile: 11 passed, 2 failed`. It exposed an incorrect repository-root calculation and a test mutation bug.
- Final run 1: `lane done gate: 19 passed, 0 failed`.
- Final run 2: `lane done gate: 19 passed, 0 failed`.
- Final profile run 1: `lane profile: 13 passed, 0 failed`.
- Final profile run 2: `lane profile: 13 passed, 0 failed`.

MUTATION GRADE — 9/9 RED, SCRATCH ONLY

| Mutant | Named killer | Result |
|---|---|---|
| Any passing check ignores order | `passing check then edit nudges with path and last check` | RED, rc 1 |
| Passing ignores exit-code validity/value | `nonzero, missing, string and bool exit codes are never passing` | RED, rc 1 |
| Bool accepted as integer exit code | `nonzero, missing, string and bool exit codes are never passing` | RED, rc 1 |
| `.md` counted as code | `Markdown edits never trigger the gate` | RED, rc 1 |
| Ledger keyed only by repository | `sessions use separate ledgers outside the repository` | RED, rc 1 |
| Ledger written under repository | `sessions use separate ledgers outside the repository` | RED, rc 1 |
| Hooks added with switch OFF | `switch OFF leaves the clone byte-identical to today's rewrite` | RED, rc 1 |
| Semantic guard accepts extra/changed hook | `verify refuses a third hook entry`; `verify refuses a changed done-gate command` | RED, rc 1 |
| Project pattern widened before bash grade | `closed classifier accepts all intended shapes and rejects 16 near misses` | RED, rc 1 |

GATES

- `python3 harness-ports/tests/test_lane_done_gate.py` twice: `lane done gate: 19 passed, 0 failed` both runs.
- `bash harness-ports/tests/test_lane_profile.sh` twice: `lane profile: 13 passed, 0 failed` both runs. The brief's baseline was 9; four C2 checks were added.
- C1 regression: `65 passed, 8 xfailed in 1.23s`.
- `python -m pyflakes` on both Python files: rc 0.
- `bash -n` on all changed shell files: rc 0.
- `git diff --check`: rc 0.
- Archive gate A: `RESULT: rev=4a381906c89f files=5 deleted=0 runs=1 tests=1b6f2517d707 identical=yes rc=0 summary="8 passed in 9.66s"`.
- Archive gate B: `RESULT: rev=4a381906c89f files=5 deleted=0 runs=1 tests=1b6f2517d707 identical=yes rc=0 summary="8 passed in 10.04s"`.
- `harness-ports/tests/run-all.sh` twice: C2 rows were green (`lane done gate: 19 passed, 0 failed`; `lane profile: 13 passed, 0 failed`), but the script ended `1 SUITE(S) FAILED` because the read-only qwen matrix suite was `18 passed, 1 failed` both times.

FILE IDENTITY — 2026-09-23T20:50:30Z

- `6ffe061625d22a47e99ddfbfa9f10a4fb612435b45d926790717f19e76230e25`  `harness-ports/bin/lane-done-gate.py`  314 lines.
- `74456d3213a15aa65d83470e86291cc993d039206ba2868a8dea211c166c28a0`  `harness-ports/bin/lane-profile.sh`  298 lines.
- `6fa6177d428f30cbc79b60a80005702cd52db1fd0dcd693764dca6087bcfe2fa`  `harness-ports/tests/test_lane_done_gate.py`  404 lines.
- `35ed2bd01e16b281e3160027e57d46b6bc94bfa126f331cdda1bccb3636f2f77`  `harness-ports/tests/test_lane_profile.sh`  241 lines.
- `a1637708edfc3d49ab99387f610587204c8f3b10115616107daad08e032ad1b9`  `harness-ports/tests/run-all.sh`  78 lines.
- Report identity before this self-reference line: `fba1d58a9771b10e0f7c8ac4c3cc58574e00f53557b15117e4d323a269761d8f`, `tasks/briefs/canny/C2-report.md`, 148 lines.

SCREENS / CODE INTELLIGENCE

- Final lane context pack: `../scratch/c2-final-pack.md`.
- Graft mapped the new Python symbols. Ripwire reported `counts_as_check` and the production `gate` as new symbols with zero incompatible callers; `verify_lane` and `create_lane` contracts are unchanged with zero incompatible callers.
- GitNexus clone index is 839 commits stale and cannot map the shell symbols/new file. Final `detect-changes` returned `No changes detected.` because it examines the indexed main clone, not this detached lane. Risk remains UNKNOWN; this is not evidence of no blast radius.
- AP screen: production helper has one AP-32 hash-prefix hit. This is the contract-required repository SHA-256 prefix, not weak credential hashing. Lane-profile's seven AF-AP-118 hits are the existing deliberate fallback-chain removal contract. Test screens are clean after narrowing temp-ledger cleanup to this repository hash.

SELF-ATTACK

1. Wrong command accepted as proof. Ruled down by a closed project runner grammar, 16 bash fail/pass grades, 16 near misses, and the widened-pattern mutant. Residual: the unavailable 109 raw rows need coordinator reclassification after landing.
2. A late edit can be hidden by an earlier pass. Ruled out by ordered JSONL facts, the pass-then-edit test, unknown-order branches, and the order-ignoring mutant.
3. A lane can edit its own gate or profile semantics can drift. The installed command resolves to the main clone, switch-OFF output is byte-identical, verify permits only the exact ordinary or exact gated semantic forms, and extra-entry/changed-command mutants die. Residual: dispatcher forwarding and a real Hermes launch are outside C2.

DISCREPANCIES

- The brief asks for a full 109-command before/after count, but only a coordinator summary and representative rows were supplied; exact raw after-count is unavailable under the no-`~/.hermes/` boundary.
- The brief says the profile baseline is 9. The extended suite correctly reports 13 after adding four C2 checks.
- `lane_gate.sh` cannot combine the Python script and shell script as test targets through `test_summary.sh`; the mixed attempt returned `no match in any of [<Dir tests>]`. The archive gate therefore ran the Python suite twice, while the shell suite ran directly twice.
- Ripwire `edit-check` takes a symbol, not file paths. The initial file-form call failed; symbol-qualified reruns succeeded.
- Full run-all is blocked by the unrelated qwen matrix failure described above.
- `report_lint`: `report_lint: 16 refs — OK 16, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`; floor 12 satisfied.

REASONING RECORD

- Rejected alternative: count `bash -n` as a check. It is syntax-only and can yield a hollow green after semantic edits.
- Rejected alternative: add broad regexes directly to C1. C2 reuses C1 unchanged and narrows project-specific forms around it.
- Ordering rationale: append facts atomically; derive the last passing check and last path edit by sequence; nudge only known edits after the pass, or unknown edits when no pass exists.
- Primary sources: current C1 implementation/tests, current lane-profile implementation/tests, the supplied Hermes runtime excerpts, and the Canny finding cited in the premise.
- Disjoint hunks: deterministic hook helper; optional profile wiring/semantic guard; direct tests; run-all registration.

HYGIENE

- Worktree contains only the five boundary implementation/test paths plus this report. No commit, add, reset, checkout, stash, push, bridge call, Hermes call, profile read, credential read, or server action occurred.
- Scratch mutants and archive gates are under this lane's `../scratch/` only.
- `--accept-hooks` already exists in the lane launcher per the supplied premise, so no allowlist edit is needed.
- Proposal only until the sandbox adversarial-verifier grades it.

RETRO

- Real defect found and fixed during self-validation: the first profile-hook command resolved two levels up to `harness-ports/`, not the repository root. Class: wrong-root path derivation. The exact semantic hook test caught it before report. Coordinator should run `/bug-echo` and decide whether this warrants an incident row.
- Real defect found and fixed during self-validation: a project runner followed by `&& true` initially counted because C1 searches each `&&` segment. Class: accepted check whose final status can be forced green. The near-miss test and widened-shape mutant now pin rejection. Coordinator should run `/bug-echo` and register the reusable anti-hollow-green lesson if not already covered.
