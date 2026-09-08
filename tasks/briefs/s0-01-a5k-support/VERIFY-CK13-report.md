# VERIFY-CK13 — adversarial grade of S0-01 checker round 13

PIN: 77f46a2de386054dd7a7b662e5fa8e024f93049a

PC-lane assessment: NOT-READY. This is not a gate verdict. The PC lane is single-model and cannot self-accept; the sandbox adversarial-verifier / contract-gate lane still owns the independent verdict.

## NOT_DONE first

- The brief asked for the builder's exact 34 mutants plus at least six novel mutants. I ran 40 expected-kill mutants from fresh git-archive copies, but they are a class reconstruction, not byte-identical recovery of the builder's unpublished driver. Twenty-seven died and thirteen survived.
- A5k's exact claimed red-before tree cannot be reconstructed from git: its base was commit 545a9ff8 plus an uncommitted P5a patch. The A5k report supplies hashes but not those blobs. Three nearest archive reconstructions all produced 3 passed, not the claimed 2 failed / 1 passed, so I do not claim red-before.
- I did not launch the real agent, buzz-acp, Hermes, a producer capture, or an os._exit probe. I also did not establish the read-only corpus's provenance independently.
- The direct real-corpus checker has no complete checker-shaped bundle. The parent root fails because manifests/ is absent; the golden child is not the checker root and defers.
- The previous attempt accidentally overwrote the early incremental draft. This report preserves the recovered results and adds fresh reruns; byte-for-byte incremental history is not available.

## Blocking set

1. CK13-02: producer and checker apply different pinned-process predicates.
2. CK13-03: corpus-version policy is duplicated and disagrees on an unknown header.
3. CK13-04/05/07: the read, AP-40 and F43 class scanners miss requested hostile syntax families.
4. CK13-06: SystemExit("text") escapes as ValueError.
5. CK13-08: 13 of 40 expected-kill mutants survive; hollow-green rate 32.5%.
6. CK13-09: the shared required-file list can be weakened while the representative pin test stays green.
7. CK13-10: the claimed red-before cannot be reproduced from available bytes.
8. CK13-11: the real corpus is not a complete direct-checker bundle.
9. CK13-01: the builder report does not meet the requested report-lint MISS-0 discipline.

## Item 0 — identity and mechanical gates

### File identity — VERIFIED

| path | sha256 | lines |
|---|---|---:|
| proofs/S0-01/check_acp_conformance.py | 25b89431ac41719d0d3987bcc6d1bac23c18aed86158b297609b7d0cfb496b1d | 1911 |
| proofs/S0-01/check_initialize.py | 304d44d6f8dcdbad6c41931ffbb8f6d45e3c2cf3456dd6285848581a39872c28 | 222 |
| proofs/S0-01/negative_contract.py | b397f6b71b674000c8bc521cfe5e0a30c0f1e517de841639f98aed987cbdcf9f | 222 |
| proofs/S0-01/pins.py | 84a1e5c86ed2be331d6f4afda86d105c00bb3f86f187b718aec6cca9d5d8e711 | 381 |
| tests/test_s0_01_check_acp_conformance.py | ce62bc6265baf15b2254cbf1162e567c57c595c36cef2658c9ed181c85439658 | 5275 |
| tests/test_s0_01_check_initialize.py | 6281dab78b77d82d616d6b31e19a5909fa8c15c68279b7a05a88e3825ee49bb2 | 863 |
| tests/test_s0_01_negative_contract.py | fe4378fad63084cb6a678667f24c3ae09cf94a26d67c1f642703bcd0460c11be | 473 |
| tests/test_s0_01_audit_cp5_controls.py | 457430b171230ffc464091560bdda88514c3ccc5961d89562cd5d3a74edf9f5a | 144 |

This verifies that the graded subject contains the coordinator's 381-line merged pins.py, not A5k's 251-line lane file.

### Finding CK13-01 — SOLID — builder report reference fails against the joint PIN

Expected: the mandated A5k report linter returns MISS 0 on the landed bytes.

Observed:

    report-lint identified the stale agent-stderr source range on the builder report's line 50.
    report_lint: 52 refs — OK 51, NEAR 0, MISS 1, UNCHECKABLE 0, UNRESOLVED 0 (at 77f46a2)
    a5k_report_lint_rc=1

The report's source range is stale. The relevant exclusion says: NOT here, deliberately: agent-stderr.txt at proofs/S0-01/pins.py:203-206.

Failing input: run the exact item-0 report_lint command at the joint PIN.

Minimal fix: correct A5k-report.md's merged-PIN range and rerun report_lint until MISS 0.

Other rerun outputs:

    pyflakes_rc=0
    diff_check_rc=0
    ap_screen: 66 production hits / 6 test hits

The wider AP screen includes 19 AF-AP-40 production rows across 11 files. This is advisory and is not a finding that every row is unsafe.

## Item 1 — the ONE list still has two process predicates and two version classifiers

### Finding CK13-02 — SOLID, blocking — checker bypasses the shared process predicate

The shared predicate at proofs/S0-01/pins.py:331-359 requires the exact buzz binary or a python-named interpreter with the pinned tee/agent at argv[1]. The producer calls it at proofs/S0-01/tools/pc/pc_post.sh:36-45. The checker instead defines its own predicate at proofs/S0-01/check_acp_conformance.py:1198-1202 and never calls pins.is_pinned_argv.

Same-row reproduction, synthetic strings only:

| command | pins.is_pinned_argv | checker _is_pinned_process | expected shared-policy result |
|---|---:|---:|---:|
| /usr/bin/cat <tee> | false | true | false |
| /usr/bin/python3 -c pass <tee> | false | false | false |
| /usr/bin/env python3 <tee> | false | false | false |
| /tmp/runner <tee> | false | true | false |
| /usr/bin/python3 -c <tee> | false | false | false |
| /usr/bin/python3 <tee> | true | true | true |

Expected: producer, checker and tests use one predicate over the same collected row.

Observed failing input: /usr/bin/cat <tee> is rejected by the producer/shared policy but counted as pinned by the checker. A non-python /tmp/runner behaves the same. I did not create a real symlinked interpreter; the shared function documents symlinked paths as a known false-negative limit.

Minimal fix: delete the checker's local predicate and call pins.is_pinned_argv(cmd.split()); test the shared function through both live consumer paths.

### Finding CK13-03 — SOLID, blocking — corpus-version classification is duplicated

The shared corpus_version classifier raises an unrecognised process-scan header version at proofs/S0-01/pins.py:305-328.

The test module separately defines _corpus_version and can call pytest.fail for version disagreement at tests/test_s0_01_check_acp_conformance.py:2664-2702.

The checker derives requirements from PINNED_LEG_FILES locally at proofs/S0-01/check_acp_conformance.py:1774-1793 rather than using the shared functions.

Temporary declared-corpus reproduction:

| first scan line | test-local answer | shared answer |
|---|---|---|
| # process-scan v2.4 rows=0, tee sidecar absent | named missing tee-status failure | v2.4 |
| # process-scan v9.9 rows=0, tee sidecar absent | v2.2 | ValueError: unrecognised process-scan header version |
| malformed header, tee sidecar absent | v2.2 | v2.2 |

The brief's specific premise that v2.4-without-sidecar silently passes did not reproduce. Unknown v9.9 does produce contradictory policy: the test fold downgrades it to v2.2 while the shared contract rejects it.

Minimal fix: make checker and tests call pins.corpus_version, pins.required_files and pins.entry_allowlist; keep one explicit legacy-v2.2 rule.

## Items 2–3 — read guards and AP-40

### Read guard behavior — VERIFIED

The shared guard is proofs/S0-01/pins.py:17-26. Negative timeline reads route through it at proofs/S0-01/negative_contract.py:60-74; initialize payload reads route through it at proofs/S0-01/check_initialize.py:39-49 and :81-84.

Standalone FIFO probes used timeout --foreground 10s, never pytest:

    check_initialize request FIFO: rc=64
    input error: payload is not a regular file: timeline.jsonl

    negative validator FIFO: rc=0
    NegativeFailure: timeline.jsonl is not a regular file: timeline.jsonl

A scratch mutant that accepts a FIFO blocked until timeout rc 124. This is a real red/green proof that the guard prevents the special-file hang class. A focused selection returned 14 passed, 369 deselected in 4.46s.

### Finding CK13-04 — SOLID — read inventory misses externally sourced read families

The inventory recognizes builtin open, read_text/read_bytes/open attributes, and json.load at tests/test_s0_01_check_acp_conformance.py:5010-5043. Direct plants returned:

| source shape | inventory |
|---|---|
| io.open(p).read() | named, unguarded |
| aliased Path.open() | named, unguarded |
| lambda / ExitStack .open() | named, unguarded |
| json.load(p.open()) | named twice |
| os.fdopen(fd).read() | not named |
| shutil.copyfile(a, b) | not named |
| subprocess consuming a path | not named |

The three missing families also survived the committed golden-list test as independent mutants.

Expected: every in-scope externally sourced filesystem read is named by the inventory or formally excluded.

Failing input: append def ck13_mut(fd): return os.fdopen(fd).read() to the production module. Observed: 1 passed, 382 deselected.

Minimal fix: define the read API domain, enumerate every supported family, add self-tests per family, and narrow the claim if copy/subprocess consumers are intentionally excluded.

### Finding CK13-05 — SOLID — AP-40 scanner misses requested absence shapes

The detector handles FileNotFoundError specially at tests/test_s0_01_check_acp_conformance.py:4931-4935; its ten committed self-test forms are at tests/test_s0_01_check_acp_conformance.py:4976-4991.

| source shape | detector |
|---|---|
| walrus if (q := p).exists() | named |
| except FileNotFoundError: continue | named |
| p.stat() under caught OSError | not named |
| os.path.getsize(p) condition | not named |
| next(p.glob(...), None) | not named |

The 20-line comment shift stayed green. A renamed enclosing function went red, proving stable function identity is enforced. But the novel p.stat/OSError plant survived: 1 passed, 382 deselected.

Minimal fix: add the missing probe/catch forms to the detector and self-test or state and enforce a narrower domain.

## Item 4 — v2.4 header, counters and reachability

The live checker path parses the v2.4 header at proofs/S0-01/check_acp_conformance.py:1175-1195 and invokes process evidence from the bundle at proofs/S0-01/check_acp_conformance.py:1709-1744 onward. It checks table_rows at :1261-1264, pinned_present at :1279-1282, teardown table_rows and body counters at :1361-1378, and names any survivor at :1388-1390.

Fresh focused contract selection:

    16 passed, 367 deselected in 27.65s
    contract_selection_rc=0

This covered the exact entry point, after/teardown table_rows, survivor naming, symlink cases, alarm order, dead comments, lossy reason and F43. The v2.3/v2.4 label-reversal matrix was not separately reproduced.

### Finding CK13-10 — SOLID on available bytes, UNSURE on the builder's unavailable patch — red-before is not reproducible

The builder's red-before claim is 2 failed, 1 passed at tasks/briefs/s0-01-a5k-support/A5k-report.md:22.

Expected from the brief and builder report: tests/test_s0_01_audit_cp5_controls.py on the pre-A5k tree gives 2 failed, 1 passed.

Observed on three nearest scratch reconstructions:

- joint PIN parent + PIN audit test: 3 passed;
- joint PIN parent + PIN audit test + joint pins.py: 3 passed;
- joint PIN parent + PIN audit test + joint pins.py + joint pc_post.sh: 3 passed.

A reconstruction from 545a9ff8 likewise gave 3 passed. The exact pre-edit pins.py and pc_post.sh were uncommitted blobs identified only by short hashes in A5k-report.md, so they cannot be recovered from git archive.

Failing evidence demand: the requested 2-fail red state is absent from every available archive combination I could construct.

Minimal fix: preserve the exact red fixture as a committed patch/blob or include a reproducible script in the report. Do not treat 2 failed / 1 passed as verified at the joint PIN.

## Item 5 — corpus, sidecar and negative grading

The bidirectional sidecar check is implemented at tests/test_s0_01_check_acp_conformance.py:2770-2803. The negative classifier uses exact whole-reason equality at tests/test_s0_01_check_acp_conformance.py:3028-3051.

Fresh focused run:

    8 passed, 375 deselected in 0.36s

Scratch mutants for missing-sidecar handling, malformed-newer downgrade and widened negative grading all went red. I did not construct a same-text/different-cause real capture, so causal uniqueness remains unproven.

Real-corpus selections, with the PC venue exports:

    44 passed, 330 deselected, 9 xfailed in 9.83s
    6 passed, 377 deselected in 0.66s
    1 passed, 373 deselected, 9 xfailed in 1.61s

The nine xfails executed; no zero-test filter is being mistaken for a pass.

## Item 6 — CLI, alarm, symlinks, citations and F43

### Finding CK13-06 — SOLID — SystemExit("text") escapes advertised conversion

The CLI catch at proofs/S0-01/check_acp_conformance.py:1893-1907 maps None to 70 and otherwise calls int(se.code). Direct seam run:

    SystemExit(None)=70
    SystemExit(0)=0
    SystemExit(7)=7
    SystemExit('text')=ValueError: invalid literal for int() with base 10: 'text'

Expected: any SystemExit is converted to a documented integer result, not an uncaught ValueError.

Failing input: a check raises SystemExit("text").

Minimal fix: preserve integer codes, map None to 70, and map noninteger codes to one documented nonzero result. Add exact None, zero, integer and text tests. os._exit was deliberately skipped because it terminates the process without exercising the catch.

Alarm-order, symlink-root, symlinked-record, symlinked-manifest, lossy-reason and all six dead-comment controls passed in the 16-test contract selection. The dead-comment implementation enumerates six comments and every regex match at tests/test_s0_01_check_acp_conformance.py:5244-5275.

### Finding CK13-07 — SOLID — F43 misses requested writers

F43's finite scanner is tests/test_s0_01_check_acp_conformance.py:3537-3646. The self-test's committed family set is at :3649-3700.

| writer | F43 result |
|---|---|
| os.replace | named |
| os.rename | named |
| os.link | not named |
| shutil.move | not named |
| tarfile.extractall / tar.extractall | not named |

Each of the three missing forms survived independently with 1 passed, 382 deselected.

Minimal fix: either add these write-capable operations and exact family self-tests or formally exclude them from fixture policy and prevent their use by another enforced mechanism.

## Item 7 — direct real-corpus root

Only the checker was run:

    direct_checker_root=/home/rocco/s0-01-pinned/realleg
    failure_reason: golden: manifests/ absent
    direct_checker_rc=1

    direct_checker_root=/home/rocco/s0-01-pinned/realleg/golden
    deferred: v2 evidence not captured
    direct_checker_rc=2

### Finding CK13-11 — SOLID — no complete direct-checker corpus bundle exists at the mapped path

The production interface constructs root/golden at proofs/S0-01/check_acp_conformance.py:1709-1719. Therefore /home/rocco/s0-01-pinned/realleg is the checker root; .../realleg/golden is the test-corpus root. The former lacks checker-required manifests/ and other top-level bundle material.

Expected: the S0-01 mint has a complete root whose golden child satisfies the production checker.

Failing input: invoke the checker on /home/rocco/s0-01-pinned/realleg.

Minimal fix, coordinator-owned: build a complete checker bundle, document the parent-root versus child-corpus interfaces, and rerun the checker directly at the parent root.

## Item 8 — mutation audit

All mutations ran one at a time on fresh git archive 77f46a2 copies below the lane scratch directory. Every pytest command had the PC venue exports and a unique basetemp. No guard-disabled mutant touched the real corpus or another protected resource.

Summary:

    EXPECTED=40 KILLED=27 SURVIVED=13 OTHER=0 CONTROL=1
    CONTROL_COMMENT_ONLY: 1 passed, 382 deselected

Hollow-green rate: 13/40 = 32.5%.

| mutant/class | result | killer or survivor evidence |
|---|---|---|
| M03 negative ordering | KILLED | three-outcome test failed |
| M06 read enumerator off | KILLED | golden-list test failed |
| M08 missing-sidecar check off | KILLED | bidirectional sidecar test failed |
| M11 alarm order swap | KILLED | alarm-order test failed |
| M14 ignore later citations | SURVIVED | 1 passed, 382 deselected |
| M16 allow citationless comment | SURVIVED | 1 passed, 382 deselected |
| M21 rebind expected read set to actual | SURVIVED | 1 passed, 382 deselected |
| M23 malformed newer to v2.2 | KILLED | malformed-newer test failed |
| six documented read plants | KILLED x6 | each golden-list test failed |
| ten documented AP-40 plants | KILLED x10 | each AP-40 equality test failed |
| v2.4 header literal | KILLED | audit file: 2 failed, 1 passed |
| table_rows replaced by rows | SURVIVED | 1 passed, 382 deselected |
| substring entry point | KILLED | exact-entry test failed |
| required argv.txt made optional | SURVIVED | 1 passed, 382 deselected |
| optional teardown.txt made required | SURVIVED | 1 passed, 382 deselected |
| lossy reason made generic | KILLED | lossy-reason test failed |
| bare SystemExit mapped to zero | KILLED | bare-exit test failed |
| symlink root followed | KILLED | symlink-root test failed |
| F43 symlink category dropped | KILLED | F43 family self-test failed |
| novel OSError/stat presence gate | SURVIVED | 1 passed, 382 deselected |
| novel os.fdopen read | SURVIVED | 1 passed, 382 deselected |
| novel shutil.copyfile read/write | SURVIVED | 1 passed, 382 deselected |
| novel subprocess path consumer | SURVIVED | 1 passed, 382 deselected |
| novel os.link write | SURVIVED | 1 passed, 382 deselected |
| novel shutil.move write | SURVIVED | 1 passed, 382 deselected |
| novel tar.extractall write | SURVIVED | 1 passed, 382 deselected |
| comment-only control | CONTROL survived | 1 passed, 382 deselected |

### Finding CK13-08 — SOLID, blocking — mutation gate has thirteen hollow greens

Expected: all 40 expected-kill mutations go red; the comment-only mutation remains green.

Observed: 27 kills, 13 survivors, control green. The survivors reproduce the scanner/class gaps above and reveal four additional pin weaknesses.

Minimal fix: add independent killers for every survivor, then rerun the same archive-based audit until expected-kill survivors are zero.

### Finding CK13-09 — SOLID, blocking — representative required-file pin does not protect the shared list

The single assertion at tests/test_s0_01_check_acp_conformance.py:5122-5124 only pins timeline.jsonl. Changing argv.txt from required to optional at proofs/S0-01/pins.py:207-215 leaves it green. Changing teardown.txt from optional to required at :223-230 also leaves it green.

Expected: changing any shared required/optional status changes a full-contract test.

Failing input: set PINNED_LEG_FILES["argv.txt"] = "optional". Observed: 1 passed, 382 deselected.

Minimal fix: assert the complete required_files(version) and entry_allowlist() sets for every supported version, and drive a bundle missing each required name through the checker.

### Finding CK13-13 — SOLID — the read golden-list and citation pins remain self-trusting

M21 rebinds expected = actual immediately before the equality and survives. M14 checks only matches[:1] and survives; M16 allows a comment with no citation and survives because the current source happens to be well formed.

Expected: gate-integrity mutations that disable full-set/full-citation enforcement go red.

Failing input: replace expected with actual in the read test. Observed: 1 passed, 382 deselected.

Minimal fix: add independent self-tests that feed a planted drift set and comments with zero and multiple bad citations through extracted pure validators.

## Item 9 — production re-scan

An AST enumeration found 18 production if-equality-to-literal branches. Rows with no raise in that local branch are mostly dispatch/classification forms, plus the __main__ guard; no new standalone production defect was established from that syntax census alone.

The checker rejects symlinks/non-regular evidence nodes before read_text, as stated in its walk comment at proofs/S0-01/check_acp_conformance.py:1720-1744.

The local AP-40 test is named test_ck12_no_presence_gated_check_in_the_proof at tests/test_s0_01_check_acp_conformance.py:4939-4973. The repo-wide AP screen found 19 AF-AP-40 rows, so broader S0-01 production is outside that local assertion's scope.

## Headline and aggregate suites — fresh

Headline, one foreground xdist call, PC exports, -n 8, unique basetemp:

    8 workers [383 items]
    374 passed, 9 xfailed in 149.97s (0:02:29)
    headline_rc=0

Load was 1.82 2.34 2.97 before and 13.47 7.39 4.80 after.

Four-file aggregate, one foreground xdist call, same exports and -n 8:

    8 workers [499 items]
    490 passed, 9 xfailed in 162.27s (0:02:42)
    four_file_xdist_rc=0

This reconciles the apparent count discrepancy: 374/9 is the named headline checker file; 490/9 is A5k's four-file aggregate. Both actually ran their declared item counts. A serial four-file attempt exceeded the terminal's 420-second ceiling and left no process; the successful bounded rerun used xdist.

## Item 10 — report discipline, process census and hygiene

### Report lint — VERIFIED, with a limitation

Final report lint returned:

    report_lint: 26 refs — OK 1, NEAR 0, MISS 0, UNCHECKABLE 25, UNRESOLVED 0 (worktree)
    latest_report_lint_rc=0

The mechanical MISS-0 bar is met, but 25 references are uncheckable because their lines have no claim token the heuristic recognizes. I inspected those source ranges directly; the linter does not prove their semantics.

Final process census after the gates found lane_owned_test_or_checker_processes=0, other_lane_test_or_checker_processes=1, total_ps_rows=676, load 3.37 3.02 2.90. The other process was a pytest run in pc-n5j's lane; no VERIFY-CK13-owned pytest/checker process remained. An earlier broad filter matched seven live Hermes lane prompts because their argv contained historical pytest text; the refined lane-owned filter excludes Hermes prompt argv and other lane worktrees.

Worktree hygiene:

    A  tasks/briefs/pc/pc-verify-ck13.md
    A  tasks/briefs/s0-01-a5k-support/VERIFY-CK13-brief.md
    ?? tasks/briefs/s0-01-a5k-support/VERIFY-CK13-report.md

The two staged files were coordinator inputs present at lane start. My only tree edit is this untracked report. Scratch scripts/results live outside the tree. No add, commit, push, checkout, reset, restore or stash occurred. No PC production service, bridge, credential, real capture, agent, buzz-acp or Hermes process was touched.

## Item 11 — required design / cheapest path

1. A5l: make the checker and test consumers call pins.is_pinned_argv, pins.corpus_version, pins.required_files and pins.entry_allowlist. Delete the local policy copies.
2. A5l: fix SystemExit noninteger handling and add exact None/zero/int/text tests.
3. A5l: define and enforce the read, absence-gate and write-family domains; add independent pure-validator self-tests for every supported syntax family.
4. A5l: pin complete per-version required/allowed sets, not one representative filename.
5. A5l: add killers for table_rows-vs-rows and the read/citation gate-integrity survivors.
6. Coordinator: preserve a reproducible red-before patch/blob; correct the joint-PIN A5k report reference.
7. Coordinator: construct a complete parent-root checker corpus and document its distinction from the golden child used by corpus tests.
8. Sandbox verifier: independently grade these bytes and every eventual repair. This PC report is evidence, not acceptance.

What is merge-ready today: the shared regular-file helper and its exercised FIFO refusal, alarm restore order, sidecar bidirectionality, exact negative reason grading, lossy reason, symlink-root refusal, and the 27 mutation-killed assertions are supported by reproduced runs.

What blocks S0-01 re-capture/mint: the divergent process/version consumers, incomplete direct-checker corpus, mutation survivors, SystemExit text escape, scanner-domain holes, and report/red-before discipline.

## Evidence tiers

VERIFIED by run: PIN hashes/lines; A5k report-lint failure; pyflakes; diff check; AP-screen counts; predicate/version tables; FIFO refusal and guard-removal hang; direct SystemExit outcomes; direct checker roots; focused, headline and aggregate pytest counts; all 40 expected-kill mutants plus control; survivor confirmations; nearest available red-before reconstructions; process/worktree hygiene.

REVIEWED statically: call paths and line ranges, production equality census, intended checker-root relationship, and the distinction between local and repo-wide AP-40 scope.

UNSURE / deliberately skipped: exact unavailable red-before bytes, real symlinked-interpreter process behavior, v2.3/v2.4 full reversal matrix, same-text/different-cause real negative capture, os._exit, real agent/buzz-acp/Hermes/capture launch, corpus provenance, and whether a repaired complete corpus passes the production checker.
