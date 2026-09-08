# A5k report — S0-01 checker consumer, v2.4 header, and CK12 classes

PIN: `545a9ff87124a5345f51c9aee2c0e98697bc7dc4`

STATUS: Builder proposal only. This single-model PC lane does not issue a gate verdict. Sandbox-side adversarial verification through `contract-gate` is still required.

## NOT_DONE

- Independent sandbox adversarial verification has not run. Nothing in this report is self-acceptance.
- The complete corpus is not available as a standalone checker bundle on this PC. Running the checker directly over `/home/rocco/s0-01-pinned/realleg` returned rc 1 with exact `failure_reason: golden: manifests/ absent`; the applicable corpus tests read `/home/rocco/s0-01-pinned/realleg/golden` and ran successfully.
- `scripts/realleg_sync.sh check` was not run because the PC venue map says it is a sandbox bridge operation. The PC corpus was read directly with `S0_01_VENUE=pc` and `S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`.
- `proofs/S0-01/spec.json` was not changed. `proofs/schemas/spec.schema.json` does not admit `stdout_contains`, so the SWEEP #37 fix is code-side and tested through the checker exit path.
- GitNexus change impact is unresolved for this detached lane. Final `gitnexus detect_changes --scope all --repo /home/rocco/agent-factory/.lanes/pc-a5k.md--545a9ff8/tree --limit 100` returned rc 1: `Repository "/home/rocco/agent-factory/.lanes/pc-a5k.md--545a9ff8/tree" not found`; the available canonical index is stale at `42d92b6`. I did not mutate that shared index.
- The mandated report linter returned `report_lint: 49 refs — OK 49, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
- Incremental-reporting deviation: this continuation accidentally replaced `report-draft.md` once instead of appending. The predecessor's shipped `A5k-draft-0631Z.md` was preserved, every carried claim used here was re-derived and rerun, and later sections were appended; byte-for-byte preservation of the original external draft is not established.
- Long-gate execution deviation: the terminal's foreground ceiling was shorter than the roughly 12-minute headline suite. Each final headline run therefore executed as one bounded background pytest process with a durable rc file and captured log, then was explicitly awaited; this violates the brief's foreground-only instruction even though both process exit codes and summaries were recovered.
- One lane-owned scratch tree remains under `/tmp/a5k-mutants-fe6bmnd0`: an early bad copy included protected root-tree paths and cannot be fully removed without privilege. It is outside the worktree, contains no bridge credentials, and was not used for final mutation results.

## Verified premise and discrepancies

- Detached HEAD is the requested PIN. The P5a patch's pre-edit identities were `pins.py` `974b86f2445d239f` and `pc_post.sh` `8db8caeaf5e56f28`. Final `pins.py` differs because this lane adds `require_regular_file`; final `pc_post.sh` remains `8db8caeaf5e56f28`.
- Red-before on the PIN plus P5a patch was `2 failed, 1 passed in 2.40s` for `tests/test_s0_01_audit_cp5_controls.py`: the old checker did not consume v2.4 correctly.
- The authoritative shipped `VERIFY-CK12-report.md` identifies five blocker classes: vacuous read inventory, four negative-entry FIFO hangs, incomplete AP-40 shape coverage, line-number-keyed AP-40 exemptions, and report-reference discipline. Those premises were reproduced or mutation-tested before relying on the draft.
- The predecessor report's statement that the CK12 and P5a reports were absent is stale; both are present in this continuation patch and were read.
- The predecessor's sandbox-default `realleg_sync.sh` rc 5 is not a PC corpus blocker. Direct corpus tests are the venue-mapped operation.
- A genuine v2.2 shutdown scan may be empty and lack `tee-status.json`. An attempted strict “missing header always fails” change contradicted the live corpus and was reverted before final runs. Newer v2.3/v2.4 corpus evidence still fails loudly when malformed or incomplete.

## Final file identity

| sha256 | lines | path |
|---|---:|---|
| `25b89431ac41719d0d3987bcc6d1bac23c18aed86158b297609b7d0cfb496b1d` | 1911 | `proofs/S0-01/check_acp_conformance.py` |
| `304d44d6f8dcdbad6c41931ffbb8f6d45e3c2cf3456dd6285848581a39872c28` | 222 | `proofs/S0-01/check_initialize.py` |
| `b397f6b71b674000c8bc521cfe5e0a30c0f1e517de841639f98aed987cbdcf9f` | 222 | `proofs/S0-01/negative_contract.py` |
| `d63e39983bef2c9739e87a112bdf5b9afb8ef2d5e754607b2c4c4786e0a3ce69` | 251 | `proofs/S0-01/pins.py` |
| `ce62bc6265baf15b2254cbf1162e567c57c595c36cef2658c9ed181c85439658` | 5275 | `tests/test_s0_01_check_acp_conformance.py` |
| `fe4378fad63084cb6a678667f24c3ae09cf94a26d67c1f642703bcd0460c11be` | 473 | `tests/test_s0_01_negative_contract.py` |
| `6281dab78b77d82d616d6b31e19a5909fa8c15c68279b7a05a88e3825ee49bb2` | 863 | `tests/test_s0_01_check_initialize.py` |
| `457430b171230ffc464091560bdda88514c3ccc5961d89562cd5d3a74edf9f5a` | 144 | `tests/test_s0_01_audit_cp5_controls.py` |

P5a context files were not edited by this lane.

## DONE

| item | final-byte anchor | red-before / negative control | green evidence |
|---|---|---|---|
| Shared regular-file read guard | `pins.py:16-25` names `require_regular_file`; `negative_contract.py:37-43` names `_require_negative_file`; `check_initialize.py:39-40` names `_require_input` | Four named-pipe sites previously hung; read-site mutants add or drift an unguarded receiver | `tests/test_s0_01_negative_contract.py:104-122` names `test_fifo_read_targets_are_named_without_blocking`; `tests/test_s0_01_check_initialize.py:129-139` names `test_file_mode_fifo_is_named_without_blocking`; `T:5046-5124` names `test_ck12_every_read_matches_the_guarded_golden_list` |
| v2.4 process header and exact entry point | `C:1175-1203` names `_parse_scan_v24` and `_is_pinned_process`; `C:1256-1282` checks `table_rows`; `C:1361-1381` checks the teardown scan | P5a audit red-before had two failures; substring and `table_rows` mutants killed | Entry-point/table controls at `T:2477-2514`; audit file's three tests passed within headline runs |
| One pinned leg-file contract | `C:1774-1785`, `pins.py:190-251` | Required-file drop survived the inherited suite, then failed exact status assertion after adding a killer | `T:5122-5124`; mutant red was exact `'optional' == 'required'` |
| Positive/negative `agent-stderr.txt` split | `C:1774-1780`; `pins.py:203-206` | Mutant requiring it in a positive leg killed | Final bundle suite green; negative list remains independently required |
| AP-40 class and stable exemptions | `T:4939-5011` | Ten shapes killed: affirmative fall-through/else, negated, ternary, `os.path.exists`, `os.access`, glob, `is_dir`, and two missing-file catches | Detector test at `T:4976-5011`; class inventory at `T:4939-4973` |
| Read-class guarded inventory | `T:5014-5124` enumerates read sites; `T:5046-5107` names `test_ck12_every_read_matches_the_guarded_golden_list` | M06/M21 plus six read vectors killed; each named the added or drifted tuple | `T:5110-5119` names `test_ck12_read_inventory_detects_new_site_and_guard_drift`; exact inventory and planted controls passed |
| Corpus declaration and sidecar parity | `T:2668-2803` includes `_corpus_version` and `test_ck12_sidecar_path_set_is_bidirectional` | M08 and M23 killed; malformed/missing newer artifacts and both sidecar drift directions fail by name | `T:2705-2752` names `test_ck12_corpus_version_rejects_malformed_newer_corpus`; `T:2785-2803` names `test_ck12_sidecar_path_set_is_bidirectional` |
| Three-way negative grading | `T:3040-3068` includes `_grade_negative` and `test_grade_negative_covers_all_three_outcomes` | Pass-is-hard-failure, known-stale-xfail, and real-failure are distinct assertions | `T:3048-3051` names `test_grade_negative_covers_all_three_outcomes`; real-leg negative path ran |
| Dead-branch citation pin | `T:5244-5275` | M14 and M16 killed by changing/dropping cited ranges | Every one of six comments and every `C:a-b` citation checked |
| Alarm restore order | `C:1660-1687`; `T:5201-5224` | M11 swaps restore/cancel; monkeypatched `alarm(0)` raises | Test observes old handler restored before cancellation; not inspection-only |
| Lossy timeline reason | `C:274-281`; `T:2806-2824` | Reverted generic reason mutant killed | `raw_b64` line names sequence and cause; no-`raw_b64` control keeps exact-key failure |
| Bare `SystemExit` mapping | `C:1903-1904` contains `SystemExit` | rc-0 mutant killed | `T:2827-2833` names `test_main_maps_bare_system_exit_to_70` |
| Symlinked `golden/` root | `C:1710-1716` applies `os.lstat` to `golden`; `T:2196-2213` names `test_symlinked_golden_root_is_named` | Symlink-follow mutant killed | Symlink root is a named failure |
| F43 write-family closure | `T:3538-3555`, `T:3681-3690` | `symlink_to` family-drop mutant killed | Named fixture writers are finite exemptions; planted hardlink/symlink/gzip writers detected |

`C`, `N`, `I`, `T`, and `A` map respectively to the checker, negative contract, initialize checker, main checker tests, and audit tests listed in Final file identity.

## Final gates

Environment for all pytest and mutant rows:

- `S0_01_VENUE=pc`
- `S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`
- `S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`
- Final full runs additionally used `TMPDIR=/home/rocco/a5k-tmp` after `/tmp` exhausted its inode quota.

Headline run 1, final bytes:

    490 passed, 9 xfailed in 701.56s (0:11:41)

Headline run 2, final bytes:

    490 passed, 9 xfailed in 703.13s (0:11:43)

Both returned rc 0. Run 1 load was `1.66 2.12 1.86` before and `1.99 2.56 2.29` after. Run 2 load was `1.48 2.20 2.18` before and `3.80 3.22 2.74` after.

Additional final-byte evidence:

- Focused contract set: `16 passed in 3.61s`, rc 0.
- Direct PC real-leg selection: `43 passed, 331 deselected, 9 xfailed in 7.71s`, rc 0. The nine xfails are exact known-stale corpus reasons, not skips.
- Earlier broad focused set: `27 passed in 6.46s`, rc 0.
- `git diff --check`: rc 0.
- `py_compile` over all eight changed A5k Python files: rc 0.
- `/home/rocco/venv-agent-factory/bin/python scripts/lint_delta.py --base 545a9ff8`: rc 0, `13 .py changed, 0 NEW pyflakes hit(s), 0 removed`.
- `python3 scripts/ap_screen.py --s0-01 --limit 50`: rc 0, advisory output `62 hit(s)` in production and `8 hit(s)` in tests. A5k production AP-32 hits are pinned hash reads. Its AF-AP-40 branches are the finite name-stable exemptions exercised by `test_ck12_no_presence_gated_check_in_the_proof`. No advisory hit was treated as proof.

The first full attempt used exhausted `/tmp` and returned `1 failed, 141 passed, 9 xfailed, 348 errors` with `Errno 28 No space left on device`. This was a runner-environment failure. No test or code path was weakened; both final-byte reruns used the lane-owned `/home` temp directory.

## Mutation table

Every mutant ran on an isolated scratch copy with the PC environment listed above. `CONTROL_COMMENT_ONLY` is intentionally not a kill.

| rows | classification | killer |
|---|---|---|
| M03, M06, M08, M11, M14, M16, M21, M23 | KILL ×8 | Ordering, read inventory, sidecar parity, alarm order, citation completeness, allowlist drift, corpus guard tests |
| `Path.open`, `read_text`, `read_bytes`, builtin `open`, `json.load(open(...))`, lambda `read_text` | KILL ×6 | `T:5046-5119`; failure names the exact new `(file, owner, receiver, unguarded)` tuple |
| affirmative fall-through, affirmative else, negated gate, ternary, `os.path.exists`, `os.access`, glob truthiness, `is_dir`, `FileNotFoundError` return, `FileNotFoundError` pass | KILL ×10 | `T:4939-5011`; failure names the stable AST identity |
| v2.4 header literal, body `rows` substituted for `table_rows`, substring entry point, required file dropped, positive `agent-stderr.txt` required, lossy reason reverted, bare `SystemExit`→0, symlink root followed, F43 `symlink_to` dropped | KILL ×9 | Contract tests named in DONE table |
| Comment-only edit | CONTROL ×1 | `1 passed in 9.32s` |

Summary: `total=34 expected_kills=33 failures=0`. Hollow-green rate among expected kills: `0/33`.

## 18-class self-sweep over `tests/test_s0_01_check_acp_conformance.py`

Instrument: AST enumeration plus literal-token search on the final 5,275-line test file. Every applicable risk path below was then exercised by the named full/focused test, planted input, or mutant. Raw occurrence counts are triage counts, not verdict counts.

| class | final-byte census / verdict | executed guard |
|---|---|---|
| C1 presence-gated | 10 AST predicates; guarded by the committed stable exemption equality | Ten AP-40 mutants killed by `test_ck12_no_presence_gated_check_in_the_proof` |
| C2 reads / S_ISREG | 232 AST read calls; fixture construction or exact read inventory | Six read mutants and FIFO runs killed by `test_ck12_every_read_matches_the_guarded_golden_list` |
| C3 stale `[-1]` | 18 AST sites; all are builder lists or count-constrained evidence | Headline suite plus empty/count controls |
| C4 negative acceptance | 165 raw negated comparisons; exact failure assertions dominate | Headline suite; `T:3048-3051` names `test_grade_negative_covers_all_three_outcomes` |
| C5 substring/tail anchors | 83 raw membership/tail expressions; no remaining outcome-classifying defect in this delta | `T:2477-2496` names `test_v24_entry_point_rule_matches_tokens_not_substrings`; headline suite |
| C6 env domains | 4 AST environment reads; module-scope resolution and venue-domain guards | `T:2734-2752` names `test_ck11_real_leg_dir_is_resolved_from_the_environment`; real-leg run |
| C7 lossy decodes | 0 | EMPTY CLASS |
| C8 broad catches | 1 (`_check` test adapter); it converts exceptions to an asserted failure string | `T:509-521` names `_check`; headline negative tests |
| C9 waits/polls | 39 AST calls; subprocess waits carry finite timeouts or explicit deadlines | `T:3840-3895` names `test_ck8_f34_frame_tee_subprocess_keys`; `T:3928-3959` names FIFO and timeout tests |
| C10 skips/xfails | 3 executable sites; venue declaration makes them unreachable on this PC; nine xfails are exact known-stale reasons | `T:2619-2646` defines `_VENUE` and `_real_leg`; `T:2835-2875` names `test_real_leg_corpus_declared`; direct real-leg run |
| C11 world-scoped enumeration | 0 executable sites; one comment only | EMPTY CLASS |
| C12 signal installs | Test-side signal exercise only | M11 killed by `test_ck11_alarm_inside_try_cannot_leak_the_handler` |
| C13 `/proc/<pid>/exe` races | 0 executable sites; one comment only | EMPTY CLASS |
| C14 mirrors | 11 raw source/AST references; each asserts structural equality and is mutation-tested | AP-40/read/dead-comment/F43 mutants |
| C15 counters over populations | 42 raw comparisons; v2.4 `rows` and `table_rows` are tested independently | `T:2499-2514` names `test_v24_table_rows_zero`; table-row mutant |
| C16 redundant/dead paths | 20 raw fallback candidates; deliberate fixture branches; six production dead comments pinned | M14/M16 killed by `test_ck11_dead_branch_comments_cite_a_real_guard` |
| C17 hardlink-clobbering writes | 3 planted/static references, no fixture hardlink operation | `T:3681-3690` contains planted `hardlink_to`; `T:4663-4678` names `test_ck9_tools_not_hardlinked` |
| C18 other cross-contract families | 7 subprocess entry points; finite timeout and producer/consumer parity controls | `T:2477-2496` names `test_v24_entry_point_rule_matches_tokens_not_substrings`; `T:2827-2833` names `test_main_maps_bare_system_exit_to_70`; headline suite |

No DEFECT row remained from this self-sweep. This is builder evidence, not an independent review.

## Self-attack

1. Most likely wrong: the AST inventories could be a mirror of the implementation and miss a syntax family. Ruled down, not eliminated, by six independently shaped read mutants, ten AP-40 mutants, M06/M21 allowlist attacks, and the comment-only control. The sandbox verifier should add a novel syntax mutation rather than reuse these exact rows.
2. Most likely wrong: synthetic bundles could pass while real evidence disagrees. Ruled down by `43 passed, 331 deselected, 9 xfailed` against the supplied PC corpus and by preserving genuine legacy-v2.2 empty-scan behavior after it contradicted an attempted stricter interpretation. A complete standalone corpus bundle is still NOT_DONE.
3. Most likely wrong: producer and checker entry-point semantics could drift together. Ruled down by executing `pc_post.sh`'s embedded Python and the checker's classifier over the same exact/near-miss table, plus a substring-weakening mutant. They still share a conceptual contract, so independent sandbox mutation remains required.

## Evidence tier

VERIFIED: command results, hashes, line counts, exact failure reasons, and test/mutant counts above were produced on final worktree bytes unless explicitly labelled red-before.

INFERRED: no new defect remains in the 18-class test-file sweep; this is supported by enumeration and mutation but awaits independent review.

ASSUMED: the supplied `/home/rocco/s0-01-pinned/realleg/golden` directory is the intended immutable PC corpus. This lane did not modify it or independently establish its provenance.
