# VERIFY-P5b report — adversarial grade of S0-01 PC capture tools round 2

VERDICT: NOT-READY.

Blocking set: F1 and F4. F5 is also a joint-checkpoint/A5l blocker because the checker-side consumer still computes a different pinned-process predicate from the producer. F2 and F3 are non-blocking but real.

This verdict is based on reproduced runs on a scratch `git archive 77f46a2` copy, plus direct runs from the lane worktree whose code bytes match the PIN. I did not launch buzz-acp, hermes-acp, Hermes, the tee, any real capture, any model request, or any bridge operation.

## Findings

### F1 — BLOCKING, SOLID: the P5b report fails its own mechanical reference gate at the joint PIN

Where: tasks/briefs/s0-01-p5b-support/P5b-report.md:77.

Expected: the report reference gate for the landed report has MISS 0 against the joint PIN, with maps for every bare filename it cites.

Observed: the exact command required by the brief returned rc 1:

    report_lint: 100 refs — OK 67, NEAR 2, MISS 10, UNCHECKABLE 13, UNRESOLVED 8 (at 77f46a2)

Concrete failing inputs include these references in the P5b report:

- P5b report line 77 points at pins.py line 317, which is a docstring/blank boundary after A5k added the regular-file helper; `is_pinned_argv` starts later.
- P5b report line 93 points at pins.py line 348, now a docstring line inside `is_pinned_argv`, not `hermes_home`.
- P5b report line 76 names the scripted-backend test file line 894, which is not mapped in the report's own lint command shape.

Minimal fix: update the shifted/stale citations in `P5b-report.md`, add every cited basename to the report-lint map, and rerun the lint at `--rev 77f46a2` until MISS 0. This is a report-artifact blocker, not a code execution blocker.

### F2 — NON-BLOCKING, UNSURE: `corpus_version()` is prefix-permissive for malformed headers

Where: `proofs/S0-01/pins.py` line 272 defines `_SCAN_HEADER_VERSION_RE`.

Expected: not explicit in the contract. The brief specifically asked for malformed-header attacks, so this is reported.

Observed hostile inputs:

- two headers: first header wins and returns v2.4.
- header in body: first body row governs and returns v2.2.
- trailing fields after a v2.4 header: returns v2.4.
- CRLF header: returns v2.4.

Mechanism: `_SCAN_HEADER_VERSION_RE` is prefix-only and `corpus_version()` reads only the first line. The full checker parser owns the complete v2.4 header grammar, so I did not prove a bypass through the checker.

Minimal fix: either document and test that this helper is only a version sniffer, or full-match the complete version-header grammar and reject duplicate/extra header lines.

### F3 — NON-BLOCKING, SOLID: the declared producer-idiom table has no cardinality/registry guard

Where: `tests/test_s0_01_pc_tools.py` line 340 begins the parser-idiom parametrization.

Expected: every declared parser idiom stays represented by a committed control, and deleting one row is loud.

Observed mutation: deleting the `Path(framedir, "d.json")` row leaves the filtered parser-idiom test green: `10 passed, 87 deselected`. The parser itself still handles the idiom; this is a test-integrity hole, not a runtime parser bug.

Minimal fix: make the declared idiom vocabulary a data constant with an independently asserted cardinality/coverage set, or state that test-source deletion is review-only.

### F4 — BLOCKING, SOLID: required-file presence is not content validation, so empty/malformed artifacts still mint or traceback

Where: `proofs/S0-01/tools/build_capture_record.py` line 75 computes `missing` by file existence only.

Expected: the capture record builder must not mint `capture.json` from empty required artifacts, and malformed required JSON/gzip must fail with a named deterministic reason.

Observed on scratch copies of the real v2.2 `run-1` corpus:

    required count 25
    empty passed 22
    empty failed 3

Examples that silently returned rc 0 and wrote `capture.json`:

- empty `argv.txt`
- empty `buzz-acp.exit`
- empty `process-scan-after.txt`
- empty `manifest-pre.txt.gz`
- empty `hermes-model.txt`
- empty `owned-pids.json`

The three empty failures were not all named policy failures:

- empty `timeline.jsonl` returns the intended named error.
- empty `env.json` raises a raw `JSONDecodeError` traceback.
- empty `runtime-identity.json` raises a raw `JSONDecodeError` traceback.

Additional malformed-content probes:

- `env.json` as `[]` returns rc 1 with raw `AttributeError: 'list' object has no attribute 'keys'`.
- `runtime-identity.json` as `[]` returns rc 0 and writes a record.
- corrupt `manifest-pre.txt.gz` returns rc 1 with raw `gzip.BadGzipFile`.

Minimal fix: define per-artifact nonempty/parseable content constraints in the shared pin/validator; validate them before record construction; catch JSON, gzip, and Unicode parse failures into named errors. Add a parametrized empty-required class test plus malformed JSON/gzip controls. This is the same hollow-green class as the fixed empty-timeline case, left incomplete for the wider required-file set.

### F5 — JOINT-CHECKPOINT/A5l BLOCKER, SOLID: producer and checker still disagree on pinned-process identity

Where: `proofs/S0-01/check_acp_conformance.py` line 1198 defines `_is_pinned_process`.

Expected: the producer, checker, and tests compute one pinned-process predicate, or the report states the checker side is not done.

Observed: the producer calls `pins.is_pinned_argv`, but the checker has a private `_is_pinned_process` that omits the producer's interpreter-name guard. Same-row probe results:

    producer checker command
    True     True    <pinned buzz-acp> --relay-url ws://x
    True     True    /usr/bin/python3 <frame_tee.py>
    True     True    /venv/python <hermes-acp>
    False    True    /usr/bin/cat <frame_tee.py>
    False    False   /usr/bin/env python3 <frame_tee.py>
    False    False   python3 -m frame_tee
    False    False   bash -c "python3 <frame_tee.py>"
    False    False   python3 -u <frame_tee.py>
    False    False   /alt/path/buzz-acp --relay-url ws://x

Concrete failing input: `/usr/bin/cat <frame_tee.py>`.

Minimal fix: in the checker, import and call `pins.is_pinned_argv(cmd.split())` and remove the private predicate. Also replace the sibling substring predicates over the same process body so the checker has one meaning. This is already named as P5b NOT_DONE 3 / A5l work, but the joint checkpoint is not merge-ready while the two consumers disagree.

## Item 0 — mechanical gates and identity

Scratch identity: `git archive 77f46a2` was unpacked under `../scratch/resume-pin`; all mutation and hostile probes ran on copies under `../scratch`, never by `git checkout`, `git restore`, or `git stash`.

Load before the direct focused gate: `13.38 7.43 4.41` with 22 users. Load before lane_gate: `3.38 3.08 3.40` with 22 users.

Direct focused pytest, with PC venue exports and an absolute basetemp:

    194 passed in 8.73s

Same test set from a fresh `git archive 77f46a2` scratch copy:

    194 passed in 8.83s

`lane_gate.sh` on the 13 P5b files plus the brief's five test files:

    RESULT: rev=77f46a2de386 files=13 deleted=0 runs=1 identical=yes rc=0 summary="194 passed in 10.96s"

File identity from lane_gate, sha256 / lines:

    84a1e5c86ed2be331d6f4afda86d105c00bb3f86f187b718aec6cca9d5d8e711  proofs/S0-01/pins.py  381 lines
    f57ebe22272b73082cba21dd9bd8b227ca37671f795089a38109edc861a756f4  proofs/S0-01/tools/build_capture_record.py  211 lines
    1cc78bad5a99a0f8e044032e9ea44b8d56735078b64674df5bed91c6c317e52f  proofs/S0-01/tools/pc/pc_launch.py  406 lines
    92bf9609f54652d398c201beb49540d4922a9dd739963845181cc0f507432714  proofs/S0-01/tools/pc/pc_post.sh  155 lines
    326b620baa269e2bc4b83034a82834cf39c866196f63bdbc13f0ea6a0da4d4e9  proofs/S0-01/tools/pc/pc_negative.py  54 lines
    4017b53887573017c9f259d66d92b0673192bc5777849dc18184601d7e333e61  proofs/S0-01/tools/pc/collect_leg.sh  29 lines
    b06375eeaeced8b407b8a0cf33f4b6fd80bbf5de631d75d907432c91b263a115  proofs/S0-01/tools/pc/run_leg.sh  68 lines
    9620fa6923969c381e2ec4874fc0be1f6db367f479b9217e9ca6b1a6f7e6e51f  tests/test_s0_01_pc_tools.py  961 lines
    7bdaa3cb0ba6a1dfeafbf9df81b9a568c818ffca9bdd53cb228c04f37b17a670  tests/test_s0_01_pc_post_scan.py  395 lines
    4cd4f18b8f9e4411274c95a777df19374beb86c5532496333fa4a1df1be8e725  tests/conftest.py  61 lines
    5129db9d3111dc2dafcac69fdb1ee3b266b43abf26ffcbbe0ca9fec5530e9fe3  .claude/hooks/edit-snapshot.py  425 lines
    c21fe3b969611492751a12a57832a00c6acc552fa9d2219009e1d4f67e93f73c  tests/test_ap_screen.py  82 lines
    ad42f6fdd0ad36af9485f8751a9edebe66a11670fe207535f2b4b84ccf1bc70f  tests/test_edit_snapshot_ap_screen.py  361 lines

Other mechanical gates:

    bash -n proofs/S0-01/tools/pc/pc_post.sh proofs/S0-01/tools/pc/collect_leg.sh proofs/S0-01/tools/pc/run_leg.sh: rc 0
    pyflakes over pins.py, build_capture_record.py, pc_launch.py, pc_negative.py: rc 0
    ap_screen.py --s0-01: rc 0, 66 hits over 11 files
    ap_screen.py --tests tests/test_ap_screen.py tests/test_edit_snapshot_ap_screen.py: rc 0, 20 hits over 2 files

The P5b report's older `ap_screen --s0-01` count of 21 hits over 4 files was not reproduced at the joint PIN; the current count is 66 over 11 because A5k/D5m files are present in the joint checkpoint.

## Item 1 — VERIFY-P5a F1-F16 closure by run

F1 and F16 are closed for the focused suite: `build_capture_record_check_mode_keeps_its_own_diagnosis` passed inside the 194-test direct run and lane_gate run.

F2 is closed only for the available `run-*` corpus leg. The PC corpus has exactly one `run-*` under golden: `run-1`. Building then checking a copied `run-1` returned:

    run-1: 9 raw files, 11 timeline entries
    run-1: capture.json matches (--check)

The phrase “every corpus leg” is not fully reproducible in this venue for `run-*`: only `run-1` exists. That is an evidence gap for absent `run-2`, not a pass for a nonexistent leg.

F3/F15 parser coverage: the current parser recognises the 11 declared idioms, catches one-name shrinkage by floor, and catches the added hostile parser mutants in Item 6. F3 remains a test-integrity concern because deleting a declared row from the test source itself is not detected.

F4 entry-point narrowing: extra hostile rows were run through `pins.is_pinned_argv`:

    /usr/bin/env python3 <tee>                      False
    python3 -m frame_tee                            False
    bash -c "python3 <tee>"                         False
    python3.13 <agent> --flag                       True
    /venv/python <agent>                            True
    python3 -u <tee>                                False
    /alt/path/buzz-acp --relay-url ws://x           False

The `python3 -u <tee>` false negative is a deliberate consequence of the current argv[1] contract: it does not admit interpreter flags before the script. I found no current corpus row using that shape.

F6 empty timeline: closed for `timeline.jsonl` by a named rc 1, but F4 above shows the wider empty-required-file class remains open.

F7 missing receipt: closed on the build path by the 194-test suite. `--check` still derives byte identity over whatever is present, as the P5b report states.

F8 signal handling: SIGKILL is covered by the suite; additional hostile signal mappings returned `-11 -> 139` and `-19 -> 147` with named messages.

F9 regular-file/dir shape: directory, FIFO, socket, and dangling symlink in place of `owned-pids.json` all returned rc 1 naming `owned-pids.json`; the FIFO probe was under timeout and did not hang.

F10 `transient` removal and collection exclusion: the focused tests passed, and a verifier-created synthetic `collect_leg.sh` probe under `timeout 45s` returned rc 0. The destination did not contain `manifest-pre.txt`, `manifest-post.txt`, `buzzacp.raw.log`, manifest logs, or launch logs; it did contain the restored baseline `manifest-pre.txt.gz` and `manifest-post.txt.gz`.

F11/F12/F13 and AF-AP-64: A5k files are present at the joint checkpoint. The P5b-focused AP tests passed, but the checker-side adoption remains separate and F5 above shows predicate drift still exists.

## Item 2 — the ONE list as functions

`pins.required_files(version)` rejects all required hostile versions: `v2.10`, `V2.4`, `v2.4 `, `v2.4.1`, empty string, and `None` each raised `ValueError` in the previous section's scratch run.

Version ordering is numeric for the declared tuple: `v2.3` precedes `v2.4` by `_version_key`.

`entry_allowlist()` equals required-or-optional files plus `PINNED_LEG_DIRS`; the file/dir overlap invariant is pinned by `test_the_status_vocabulary_is_closed_and_the_dirs_are_named`.

Malformed-header attacks are reported as F2. I did not prove that permissive prefix matching can bypass the full checker parser.

## Item 3 — producer/checker predicate agreement

Producer side: `pc_post.sh` imports `pins` and calls `pins.is_pinned_argv(cmd.split())`.

Checker side: `check_acp_conformance.py` still owns a private `_is_pinned_process` and does not call `pins.is_pinned_argv`.

The two predicates agree on the current real corpus rows and most synthetic F4 rows. They disagree on `/usr/bin/cat <frame_tee.py>`: producer false, checker true. This is F5.

The version consumers also still differ mechanically: `pins.corpus_version()` returns a per-leg header version, while the checker has `_captured_leg_version(golden)` as a private corpus fold. On a v2.4 header without `tee-status.json`, the tool side treats it as v2.4 and the required-file gate must fail completeness; checker adoption is still its own lane's work.

## Item 4 — S0-03 launcher seam

The constant `PINNED_HERMES_HOME` remains immutable. `pc_launch.py` resolves `HERMES_HOME = pins.hermes_home()` once at import and threads that value explicitly.

Subprocess probes through the real CLI, without launching service code:

- FIFO override: exits 64 with `S0_01_HERMES_HOME=... is not an existing directory`.
- relative nonexistent path: exits 64 with the same validator.
- empty override: exits 64.
- existing directory without a profile: `--help` exits 0 because `hermes_home()` only validates the directory; profile semantics are checked later.
- existing directory with trailing slash: `--help` exits 0.
- foreign leg plus `--profile <directory>`: exits 1, `--profile ... is not an existing file`.

S0-01 leg rules remain closed: a foreign model on `run-1` is refused before any PC path, and an S0-01 leg with a foreign profile is refused. A foreign model is intentionally open only for a foreign leg with an existing profile. No actual launch was attempted.

## Item 5 — AP screen changes

End-to-end hook tests passed in the 194-test direct run and lane_gate run.

AF-AP-40: `.claude/hooks/edit-snapshot.py` extends the existing row with `else\b` rather than adding a duplicate row id. The hook has fire/no-fire tests for the ternary presence-gate shape.

AF-AP-57: `.claude/hooks/edit-snapshot.py` makes `[0]` optional for `call_count` as well as the sibling names. The direct AP test exercises the hook's real row.

D8 line drift: the ordinal gate is not at the old P5b report reference. It is at line 4687 of `tests/test_s0_01_check_acp_conformance.py` in this joint checkpoint.

## Item 6 — mutation audit

All mutations were on scratch copies under `../scratch`, with PC exports and absolute basetemps. No protected resource was contacted. FIFO/hang probes ran under `timeout`.

Mutation summary: 40 valid attacks, 39 killed, 1 survived. Hollow-green rate among expected-kill attacks: 1/40. The survivor is F3, the deleted parser-idiom test row.

First continuation batch, carried from the previous attempt and spot-verified by focused suite behavior:

    M1 remove Python-entry arm from pins.is_pinned_argv: KILLED
    M2 ignore PINNED_LEG_FILES_SINCE: KILLED
    M3 remove empty-timeline guard: KILLED
    M4 remove missing-receipt failure: KILLED
    M5 replace regular-file/dir gates with exists(): KILLED under timeout, no hang
    M6 map signal death to success: KILLED
    M7 restore transient/remove manifest text exclusion: KILLED
    M8 apply completeness gate in --check: KILLED
    M9 remove lowercase fd parser support: KILLED
    M10 delete one declared Path(framedir, ...) idiom fixture row: SURVIVED, F3
    M11 remove _PY_PATH: KILLED
    M12 default malformed headers to v2.2: KILLED
    M13 remove Hermes-home validation: KILLED
    M14 move PINNED_HERMES_HOME with env override: KILLED
    M15 remove AF-AP-40 else alternative: KILLED
    M16b forbid bracketed call_count: KILLED

The first M16 was malformed because another regex alternative still matched the suffix of `call_count`; I discarded that mutant and reran the corrected M16b.

Additional independent mutation batch, direct output summaries:

    M17 | KILLED | 1 failed, 110 deselected in 0.33s
    M18 | KILLED | 1 failed, 110 deselected in 0.37s
    M19 | KILLED | 1 failed, 110 deselected in 0.28s
    M20 | KILLED | 1 failed, 110 deselected in 0.29s
    M21 | KILLED | 2 failed, 2 passed, 107 deselected in 0.19s
    M22 | KILLED | 1 failed, 3 passed, 107 deselected in 0.12s
    M23 | KILLED | 3 failed, 6 passed, 102 deselected in 0.23s
    M24 | KILLED | 1 failed, 110 deselected in 0.12s
    M25 | KILLED | 1 failed, 110 deselected in 0.23s
    M26 | KILLED | 1 failed, 3 passed, 107 deselected in 0.40s
    M27 | KILLED | 1 failed, 110 deselected in 0.16s
    M28 | KILLED | 2 failed, 109 deselected in 0.26s
    M29 | KILLED | 1 failed, 110 deselected in 0.22s
    M30 | KILLED | 1 failed, 110 deselected in 0.16s
    M31 | KILLED | 1 failed, 110 deselected in 0.11s
    M32 | KILLED | 1 failed, 110 deselected in 0.14s
    M33 | KILLED | 1 failed, 110 deselected in 0.12s
    M34 | KILLED | 1 failed, 110 deselected in 0.21s
    M35 | KILLED | 1 failed, 110 deselected in 0.11s
    M36 | KILLED | 1 failed, 6 passed, 104 deselected in 0.27s
    M37 | KILLED | 1 failed, 10 passed, 100 deselected in 0.24s
    M38 | KILLED | 3 failed, 8 passed, 100 deselected in 0.30s
    M39 | KILLED | 1 failed, 6 passed, 104 deselected in 0.24s
    M40 | KILLED | 1 failed, 110 deselected in 0.10s

What those additional mutants attacked: unknown-version logic, since-file gating, allowlist union, excluded-on-collect admission, header defaulting, pinned argv widening/narrowing, producer import wiring, signal mapping, empty timeline, non-regular file shape, check-mode byte-identity, missing receipt, foreign profile validation, leg/model closure, Hermes-home validation, producer parser idioms, dot-file exclusion, and collect exclusion.

## Item 7 — 18-class re-scan and hostile content

The class re-scan found the same main P5b-owned defect as the hostile content sweep: presence gates are dominated for existence, but not for content validity. That is F4.

AST scan for literal equality conditionals in the P5b Python implementation scope found only these meaningful sites beyond `__main__` guards:

- `build_capture_record.py`: empty timeline guard. This is a real guard and was mutation-killed.
- `pc_launch.py`: allowlist/respond-to mode, `len(parts) == 2` parser acceptance, and launcher `__main__`. The mode guard is paired with the exact `two-users` invariant in tests; the parser acceptance is not a security decision by itself.

`ap_screen.py --s0-01` found 66 production hits across the joint checkpoint. The P5b-owned ones remain: AP-1 for `S0_01_HERMES_HOME`, AF-AP-40 in `build_capture_record.py`, AP-32 hashing, AF-AP-45 process session closure, AF-AP-55 `/proc/<pid>/exe`, and AF-AP-41 startup regex. The P5b report's classifications generally hold for existence and identity, except F4 shows the AF-AP-40 domination statement is too narrow if read as content validation.

`ap_screen.py --tests tests/test_ap_screen.py tests/test_edit_snapshot_ap_screen.py` found 20 hits over 2 files. They are expected fixture literals for the AP screen tests, not a claim of zero hits.

Hostile content sweep details are in F4.

## Item 8 — PC-carve-out executable surfaces

No service or live capture was launched.

Executed without launching anything:

- `pc_launch.py --help` and refusal argv paths as subprocesses.
- `pc_post.sh scan` through saved/synthetic process tables and test-owned process trees.
- `pc_negative.py` signal mapping through a stub probe subprocess and monkeypatched return codes.
- `collect_leg.sh` over a verifier-created synthetic run dir and local bridge shims under `timeout 45s`.

The synthetic `collect_leg.sh` probe proved only the local pack/exclude/materialise path. It did not prove bridge transfer or a real PC capture.

Still never executed end to end: buzz-acp, hermes-acp, Hermes, frame_tee, a real PC capture, relay delivery, a model request, or bridge operation. A real S0-01 recapture still needs the coordinator's VB-F12/F13/F14 live evidence steps.

## Item 9 — discipline, report lint, process census, hygiene

File:line references in this report were checked against the worktree/PIN bytes by direct reads. The report-lint result on this report is recorded in the final self-lint line below.

Process census after the mutation, AP, syntax, and focused gates: 669 total processes. Filtered signatures for `resume-mutants`, `resume-pin-pytest`, `run_remaining_mutants`, and `time.sleep(120)` returned 0 rows. Every process started by this lane was bounded and ended; no name-based kill was used.

Git hygiene before writing this report showed only the two staged coordinator brief files. After writing this report, this report file is the only additional worktree output this lane intentionally adds inside the tree. Scratch helper scripts live under `../scratch` and are not committed.

No `git add`, `git commit`, `git push`, `git reset`, `git checkout`, `git restore`, or `git stash` was run. No credential file was read or printed. The real corpus under `/home/rocco/s0-01-pinned/realleg/golden` was copied for tests and never modified.

## Item 10 — design review

Floor vs equality: P5b's per-producer parser count as a floor is the right direction for current producers. The defect direction was shrinkage; a floor catches that without false-reding a later legitimate producer addition in another lane. It does not protect a declared idiom with no live site, which is F3.

The documented F5 limit vs `/proc/<pid>/exe`: keeping `pins.is_pinned_argv` text-only is defensible for producer/checker parity, because the checker only has collected text. The cost is real and documented: a pinned buzz-acp binary invoked through another path is invisible unless the pidfile/proc guard catches it before launch. Do not claim that limit is closed.

The ONE list: exporting `required_files()` and `entry_allowlist()` fixed the P5a class where the tool and tests had divergent derived lists. The joint checkpoint still has two consumers because the checker reimplements the version and pinned-process predicates privately. A5l should import the pins functions instead of copying their logic.

Round 3 / P5c should do the P5b-owned fixes:

1. Add content validation for all required artifacts before `capture.json` construction.
2. Convert JSON/gzip/Unicode failures into named deterministic errors.
3. Add mutation tests for the whole empty/malformed-required class.
4. Add an independent cardinality/registry assertion for the parser-idiom control table, or explicitly mark deletion of test rows as review-only.
5. Decide and document whether `corpus_version()` is a permissive version sniffer or a strict header parser.

Coordinator/A5l work:

1. Make the checker call `pins.is_pinned_argv`, `pins.required_files`, `pins.entry_allowlist`, and the shared version detector instead of private copies.
2. Replace the checker sibling substring predicates over process rows with the same shared predicate.
3. Run the real recapture and VB-F12/F13/F14 live evidence steps; this verifier did not and cannot certify them.
4. Repair the stale `P5b-report.md` citations or accept F1 as a known report-artifact blocker.

## Reproduced vs reviewed vs skipped

Reproduced by run:

- Direct focused suite: 194 passed.
- Fresh archive focused suite: 194 passed.
- lane_gate focused suite: 194 passed, rc 0.
- P5b report_lint at the joint PIN: rc 1, 10 MISS.
- build/check over the available real `run-1` corpus copy.
- hostile version strings for `required_files()`.
- malformed `corpus_version()` header cases.
- producer/checker predicate disagreement table.
- `pc_launch.py` help/refusal argv probes.
- AF-AP-40/57 tests through the focused suite.
- 40 mutation attacks on scratch copies.
- empty/malformed required-file content sweep.
- synthetic `collect_leg.sh` local packing probe under timeout.
- AP scans, syntax checks, pyflakes, and process census.

Reviewed statically:

- The checker private version fold and private pinned predicate.
- The P5b report's S0-03 argv derivation and NOT_DONE claims.
- The fact that A5k adopted some checker list/header work but not the shared predicate/function imports.

Deliberately skipped:

- Any live buzz-acp, hermes-acp, Hermes, frame_tee, relay, bridge, or model execution, because the PC venue brief forbids it.
- Full `tests/` in one run; the brief named the focused files, and the focused direct/lane_gate runs were green.
- Any write to `docs/INCIDENT-LOG.md`; this verifier reports the new defect class but does not mutate project documentation outside the lane report.

Final self-lint:

    report_lint: 1 refs — OK 0, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (at 77f46a2)

The one UNCHECKABLE ref is the report path in F1; it has no claim token on that line and is not a failed line reference. MISS 0.
