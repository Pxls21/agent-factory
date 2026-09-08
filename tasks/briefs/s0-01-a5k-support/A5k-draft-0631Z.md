# A5k report draft

## PIN and premise evidence

VERIFIED:

- Detached HEAD is `545a9ff87124a5345f51c9aee2c0e98697bc7dc4`.
- The only pre-existing worktree delta is the seven-file staged P5a patch; there was no unstaged delta before A5k edits.
- `proofs/S0-01/pins.py` sha256 is `974b86f2445d239ff81e2df339b98f5679ee51bdec171cf5b2d06d0ededbaeaa` (required prefix `974b86f2445d239f`).
- `proofs/S0-01/tools/pc/pc_post.sh` sha256 is `8db8caeaf5e56f28e63dfd080241f8542f82fc918dd35de00177767c5cd70c36` (required prefix `8db8caeaf5e56f28`).
- Red-before on those bytes: `tests/test_s0_01_audit_cp5_controls.py` printed `2 failed, 1 passed in 2.40s`. The clean-shutdown control expected the old v2.3 header but received v2.4; the owned-survivor control reached the old checker and failed with `process-scan-after.txt has no enumeration header` rather than naming the survivor.
- `bash scripts/realleg_sync.sh check` returned rc 5: `realleg_sync: no PC manifest beside /root/s0-01-realleg/golden — run pull`.

DISCREPANCY:

- The brief requires `tasks/briefs/s0-01-a5j-support/verify-CK12.md` and `tasks/briefs/s0-01-p5a-support/P5a-report.md`, but neither path exists in this lane or the canonical checkout, and detached object `582ada4ca1b50deb4c8cc8e15c7f0980831653f4` is no longer in the shared object store. I used the committed `VERIFY-CK12-brief.md`, `VERIFY-P5a-brief.md`, A5j report, current P5a bytes, and direct reproductions as primary evidence; the two absent reports remain NOT_DONE inputs and will be named in the final report.

STATUS: premise confirmed by direct run. Implementation remains a build-lane proposal and cannot self-accept.

## Finished: presence-gated class

VERIFIED:

- The AP-40 AST pin scans all three production modules and the checker test module; exemptions are stable `(file, function, ast.unparse(test))` identities.
- Detector controls cover affirmative fall-through/else, negated predicates, ternaries, `os.path.exists`, `os.access`, glob truthiness, directories, and two `FileNotFoundError` catch forms.
- `_corpus_version` now fails loudly for missing scan evidence and malformed v2.3+ evidence; genuine legacy v2.2 remains classified only when its pre-tee-status shape is present.
- `test_real_leg_process_evidence` now validates absent/malformed evidence before installing its strict xfail marker.
- Focused final bytes: `/tmp/a5k-presence-focused5.txt`: `6 passed in 1.42s` (rc 0).

STATUS: this section is finished implementation evidence, not an independent gate verdict.

## Finished: remaining CK12/SWEEP behavior classes

VERIFIED on current bytes (builder-side instrument data, not an independent verdict):

- Negative grading now has explicit pass-is-hard-failure, known-stale-xfail, and real-failure outcomes; duplicate `negative:` output was removed.
- All six dead-branch comments must cite one or more concrete `C:a-b` guard ranges, and every cited range is checked.
- Corpus sidecar paths are compared in both directions; an undeclared corpus file and a declared-but-absent file fail by name.
- Lossy a2c entries carrying `raw_b64` fail with `timeline: lossy a2c line at seq N (raw_b64 kept)`; lossy entries without `raw_b64` retain the exact unexpected-keys failure.
- A bare `SystemExit()` maps to rc 70. The spec schema rejects `stdout_contains`, so `proofs/S0-01/spec.json` was not changed.
- `symlink_to` is restored to the F43 write-family scan; only the named fixture-mutating tests are exempt. The self-test plants and detects the `symlink_to` family.
- F9 is no longer inspection-only: the alarm-cancellation test makes `alarm(0)` raise and verifies the old handler was restored first.

Focused outputs:

    8 passed in 1.52s
    2 passed in 0.81s
    20 passed, 5 skipped, 357 deselected in 9.46s
    5 passed in 1.80s

REAL-LEG BLOCKER:

    realleg_sync: no PC manifest beside /root/s0-01-realleg/golden — run pull
    rc=5

No pull was attempted because this lane forbids network beyond localhost and modifying the corpus is outside scope.

DISCREPANCY:

- The working-tree `pins.py` SHA is `60cf04055644a201`, not the P5a patch identity, because A5k adds `require_regular_file`. The staged P5a input is still exactly `974b86f2445d239f`; staged `pc_post.sh` is exactly `8db8caeaf5e56f28`.
- GitNexus CLI could not run because `.gitnexus/run.cjs` is absent in this worktree; `scripts/why.sh` supplied history, but impact remains unmapped.

## Finished: v2.4 scan header and pinned-leg consumer

VERIFIED:

- The checker now parses v2.4's distinct `rows` and `table_rows`, rejects `table_rows=0` as `enumeration did not run`, and cross-checks persisted body count against `rows`.
- The checker and `pc_post.sh` entry-point classifiers were executed over the same synthetic table; exact argv positions classify `[true, true, true, false, false]`, including two substring near-miss controls.
- Positive-leg admission is derived from `PINNED_LEG_FILES`, `PINNED_LEG_FILES_SINCE`, and `PINNED_LEG_DIRS`; `capture.json` is admissible. `agent-stderr.txt` remains negative-required and is legacy-admissible, never positive-required.
- Red-before: the P5a audit produced `2 failed, 1 passed in 2.40s`.
- Green-after on current bytes: `tests/test_s0_01_audit_cp5_controls.py` produced `3 passed in 2.16s`.
- Focused checker controls produced `13 passed, 4 skipped, 353 deselected in 20.17s`; skips are solely the unset real-leg declaration.
- `git diff --check` and `py_compile` returned rc 0.

NOT_DONE:

- The real-leg run remains blocked because `realleg_sync.sh check` found no PC manifest beside the declared sandbox corpus.
- GitNexus impact/detect_changes is unavailable in this detached worktree (`.gitnexus/run.cjs` absent); `scripts/lane_context.sh` recorded this explicitly and supplied graft/ripwire fallback maps.

STATUS: this section is finished implementation evidence, not an independent gate verdict.

## Finished: regular-file read class

VERIFIED:

- `pins.require_regular_file` is the shared `os.stat`/`S_ISREG` guard and raises each caller's failure type with a basename-only reason.
- All filesystem read calls in the three production modules now bind the exact read receiver to `_require_file`, `_require_negative_file`, `_require_input`, or `pins.require_regular_file`; the old within-five-lines heuristic and widened receiver allowlist are gone.
- The committed AST golden list equals every `open`, `Path.open`, `read_text`, `read_bytes`, and `json.load` site by `(file, function, receiver, guard)`. Its planted unguarded and guarded controls prove additions and receiver drift are visible.
- The four negative-contract FIFO vectors (`timeline.jsonl`, `runtime-identity.json`, `env.json`, fixture JSON), file-mode FIFO, checker FIFO/directory helpers, and a symlinked `golden/` root all return named refusals before five seconds.
- Focused current-byte run: `10 passed in 3.26s`.

DISCREPANCY:

- The brief says every new test must be red-before. The read-inventory class and FIFO vectors reproduce the CK12 defects against the pre-change semantics, but the single recorded focused command above is green-only. Exact scratch-copy red evidence remains to be captured in the mutation table.

STATUS: read-class implementation is complete as builder evidence; independent adversarial verification has not run.
