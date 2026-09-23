NOT DONE: independent VERIFY-B9 and live capture follow this build lane. This lane does not self-accept or issue a gate verdict.

HEADER
- Role: code-implementer; PIN: `71463f3`; route: PC build lane. The local route is HYBRID in practice; this report claims no model identity.
- Authorization: defensive work on the owner's S0-02 runner/checker seam. The tests use scratch-only process and delivery doubles. No live relay, launcher, server, container, host secret file, commit, push, or outward action was used.
- Working tree touched: `proofs/S0-02/tools/pc/run_s0_02_legs.sh`, `tests/test_s0_02_buzz_authz.py`, and this report.

ITEM 1 -- PREMISE (verified)
- PIN identities re-measured from `git show 71463f3:<file>`:
  - R `proofs/S0-02/tools/pc/run_s0_02_legs.sh` sha256[:16]=`2f301973ee198a35`, lines=253, last-commit=`b3eba6ab`.
  - C `proofs/S0-02/check_buzz_authz.py` sha256[:16]=`6bc4729839495148`, lines=762, last-commit=`91e33f28`.
  - T2 `tests/test_s0_02_buzz_authz.py` sha256[:16]=`3f341399d0cb4f1d`, lines=2437, last-commit=`b3eba6ab`.
  - PP `proofs/S0-01/tools/pc/pc_post.sh` sha256[:16]=`92bf9609f54652d3`, lines=155, last-commit=`77f46a2d`.
- PIN anchors matched: `R@71463f3:34` `TURN_WAIT_S=${S0_02_TURN_WAIT_S:-100}`; `R@71463f3:35` `POLL_S=5`; `R@71463f3:182` `neg-replayed)`; `R@71463f3:187` `collect_leg "$out/first"`; `R@71463f3:198` `collect_leg "$out/second"`; `R@71463f3:243` `collect_masked "$out"`.
- DISCREPANCY: the brief's set id `a5de0beef100` did not reproduce in this checkout. `scripts/test_summary.sh` has no set-id producer; it prints only `pytest-exit` and `pytest-summary`.

ITEMS 2-3 -- RUNNER REPAIR (verified)
- `R:39` adds `S0_02_REPLAY_PREFIX_MISMATCH=8` as the named prefix-mismatch return code.
- `R:111` adds `snapshot_timeline()`: it writes `R:120` `head -c "$first_bytes" "$FD/timeline.jsonl" > "$out/first/timeline.jsonl"` after `R:119` computes the last-newline cut with `rfind`.
- `R:128` adds `delta_timeline()`: `R:130` proves the final live timeline extends the first snapshot with `cmp -n`; `R:131` emits `S0-02: neg-replayed final timeline does not extend the first snapshot (prefix mismatch)`; `R:135` writes the post-boundary delta with `tail -c +$((first_bytes + 1))`.
- `R:223` `neg-replayed)` now keeps one live process across both deliveries: `R:231` `first_bytes=$(snapshot_timeline "$out")`; second delivery/reuse/t0 remains at `R:238-R:240`; `R:252` `delta_timeline "$out" "$first_bytes"` writes the second sub-leg timeline.
- `R:305` `collect_masked "$out/first"` and `R:306` `collect_masked "$out/second"` copy the one post-exit masked log into both sub-legs. There is no replay-root `buzzacp.log` in the then branch.
- Consumer fixed point: `C:143` `_LEG_FILES_PLAIN` requires `buzzacp.log`; `C:569` checks the replay root has only `REPLAY_SUBLEGS`; `C:609` scans observables only when `sub == "second"`; `C:621` `if turns[1] != 0` refuses any second-delta turn.

ITEM 4 -- ADAPTED SOURCE PIN / MIRROR (verified)
- `T2:1724` `test_pc_runner_replay_window_and_nip98_guard_are_pinned` now pins `T2:1741` `cmp -n`, `T2:1742` `tail -c +$((first_bytes + 1))`, `T2:1745` `S0_02_REPLAY_PREFIX_MISMATCH=8`, and the dual masked-log copies at `T2:1746-T2:1747`.
- The pin also splits the replay branch at `T2:1753-T2:1763`, proving the replay then-branch writes `collect_masked "$out/first"` and `collect_masked "$out/second"`, while the else branch keeps `collect_masked "$out"` for every other leg.
- The runner-write mirror recognizes the new producer operations. `T2:1434-T2:1535` now admits the added snapshot/delta/masked-log/mkdir/cmp writes; `T2:1567-T2:1630` separates root writes from replay sub-leg writes before matching `_LEG_FILES_PLAIN`.
- DEVIATION (intent-preserving): `mkdir` was added to the writer whitelist because the new production helpers create sub-leg directories before writing files.

ITEM 5 -- PRODUCER->CONSUMER INTEGRATION (verified)
- `T2:2657` `test_replay_integration_runner_producer_into_real_checker` sources the entire runner and overrides only `launch_leg`, `deliver`, and `post_leg`. The real `stop_leg` path is checked by the `no pidfile` assertion at `T2:2667`; real `main`, `wait_turn_window`, `snapshot_timeline`, `delta_timeline`, and `collect_masked` run.
- Case A at `T2:2657` `test_replay_integration_runner_producer_into_real_checker`: runner-produced replay root has exactly `first` and `second`; each sub-leg has the six checker files; first has 1 prompt; second delta has 0 prompts; both sub-leg logs are the same post-exit masked log; real checker returns exactly:
  `PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; +1 revocation leg (assertion 2); removal evidence: coordinator-supplied receipt (unauthenticated; ordering and fields verified; not an end-to-end revocation proof)`
- Case B at `T2:2692` `test_replay_integration_empty_delta_second_timeline_passes`: an existing 0-byte `second/timeline.jsonl` is accepted by the real checker with the same PASS line. FINDING: C accepts the valid empty delta; no checker change is needed.
- Case C at `T2:2707` `test_replay_integration_pin_runner_reproduces_the_failure`: the same harness over `git show 71463f3:proofs/S0-02/tools/pc/run_s0_02_legs.sh` reproduces M-B exactly: `neg-replayed: expected exactly the sub-leg directories ['first', 'second'], got ['buzzacp.log', 'first', 'second']`. PIN + M-B-only repair reproduces M-A exactly: `neg-replayed/second: 1 ACP turn(s), expected 0 — the duplicate delivery produced a second turn`.

ITEM 6 -- PREFIX-PROOF AND BOUNDARY CONTROLS (verified)
- `T2:2799` `test_replay_prefix_proof_refuses_a_non_extension`: a changed byte inside the first region returns `rc=8`, emits the exact prefix-mismatch text, and writes no second timeline.
- `T2:2811` `test_replay_mid_line_snapshot_first_plus_delta_equals_final`: a mid-line live writer leaves the first snapshot cut at the last newline; the appended bytes become delta; concatenating first and delta equals the final live bytes.
- `T2:2822` `test_replay_empty_delta_writes_zero_byte_second`: final equals first; `second/timeline.jsonl` exists and is zero bytes.

ITEM 7 -- MUTANTS (verified)
| id | mutation | killing test | result |
| --- | --- | --- | --- |
| m1 | second gets the cumulative timeline copy | `T2:2834` `test_replay_mutant_cumulative_second_is_rejected` | KILLED: exact `C:621` `if turns[1] != 0` second-turn failure text |
| m2 | remove the `cmp -n` prefix proof | `T2:2854` `test_replay_mutant_no_prefix_proof_still_writes_second` plus item 6a | KILLED: mutant writes second; real proof returns rc 8 |
| m3 | use `tail -c +$first_bytes` | `T2:2882` `test_replay_mutant_off_by_one_delta_breaks_concatenation` | KILLED: first+delta differs from final |
| m4 | root-only masked log (PIN behavior) | `T2:2906` `test_replay_mutant_root_only_masked_log_is_rejected` | KILLED: exact `C:569` `REPLAY_SUBLEGS` replay-root closure text |
| m5 | masked log into first only | `T2:2926` `test_replay_mutant_masked_log_first_only_fails_second_closure` | KILLED: exact `neg-replayed/second: missing ['buzzacp.log']` |
| m6 | snapshot includes the partial trailing line | `T2:2942` `test_replay_mutant_snapshot_not_cut_at_newline` | KILLED: first snapshot does not end LF |
| m7 | remove `wait_turn_window` before final read | `T2:2966` `test_replay_mutant_wait_removed_case_a_still_passes` | EQUIVALENT under this zero-latency fake + `S0_02_TURN_WAIT_S=0`; exact checker PASS. Production latency is why the window remains. |

GATES (verified unless stated)
- Syntax: `bash -n proofs/S0-02/tools/pc/run_s0_02_legs.sh` + `python3 -m py_compile tests/test_s0_02_buzz_authz.py proofs/S0-02/check_buzz_authz.py` -> `compile/bash-n: OK`.
- Full pytest run 1 with declared PC inputs: `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz python -m pytest -n 8 tests/test_s0_02_buzz_authz.py` -> `============================= 175 passed in 21.74s =============================` and `PYTEST_RC=0`.
- Full pytest run 2 with the same declared PC inputs: `============================= 175 passed in 21.33s =============================` and `PYTEST_RC=0`.
- Mechanical count source: `scripts/test_summary.sh -n 8 tests/test_s0_02_buzz_authz.py` with the same declared PC inputs -> `pytest-exit: 0`; `pytest-summary: 175 passed in 20.06s`.
- `git diff --check` -> rc 0, no output.
- `python3 scripts/ap_screen.py scratch/diff.patch` -> `--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---`.
- `python3 -m py_compile` -> OK; `pyflakes` / `lint_delta.py` not run to completion because pyflakes is absent from both `python` and `python3` (`No module named pyflakes`).
- `shellcheck` -> `shellcheck: not installed`.
- `scripts/lane_context.sh` pack written to `scratch/b9-pack-final.md` (306 lines). It reported AP screen 0 on R and refreshed graft context for T2.
- GitNexus `detect-changes` against the lane tree was unavailable: `Repository "/home/rocco/agent-factory/.lanes/pc-b9.md--71463f3/tree" not found`. This is reported as a tooling discrepancy, not hidden.

DISCREPANCIES / NOT DONE
- Independent VERIFY-B9 has not run. This build-lane output is a proposal until the sandbox adversarial verifier grades it.
- Live capture is not done by this lane. The coordinator owns that after VERIFY-B9.
- The brief's set id `a5de0beef100` did not reproduce; the local `scripts/test_summary.sh` prints no set id.
- `pyflakes` and `shellcheck` are absent in this lane environment; compile/bash syntax and full pytest passed.
- GitNexus lane-tree `detect-changes` failed because the lane path is not an indexed GitNexus repo.
- DEVIATION: after compaction I loaded `build-loop`, `contract-gate`, and `anti-hollow-green` despite the context-budget note; no repository state changed from that.

SELF-ATTACK
1. Wrong timeline shape: ruled out by no-space producer frames, real sourced runner bytes, exact first/second prompt counts, and real checker PASS.
2. Hollow closure green: ruled out by exact root/sub-leg file sets, both sub-leg log copies, no root log, plus m4/m5 exact failures.
3. Prefix/delta boundary error: ruled out by non-extension rc/text/no-write, mid-line byte concatenation, empty-delta zero bytes, and m2/m3/m6 mutants.

RETRO
- General lesson for anti-hollow-green/build-loop: a replay producer->consumer test must preserve the real live append shape and run the real consumer; source pins alone cannot prove boundary or closure behavior.
