# P5a — S0-01 PC capture tools, round 1 (sandbox Opus 4.6 `code-implementer`)

PIN: `2823f05` (the commit carrying the brief). Origin moved to `4d2f313` while the lane ran; `git diff 2823f05..HEAD`
over my scope is EMPTY, so the PIN stayed a valid base and the gate was run at BOTH revisions. Clock: `date -u` =
`Tue Sep  8 00:52:02 UTC 2026`.

## FILE IDENTITY (sha256[:16] / lines, FINAL bytes)

`sha256sum | cut -c1-16` and `wc -l` on the working tree, with `git diff --numstat 2823f05`:

```
974b86f2445d239f  proofs/S0-01/pins.py                        235 lines    +79   -0   (ADD-only)
682cf587fa95e1d9  proofs/S0-01/tools/pc/pc_launch.py          351 lines   +116  -38
8db8caeaf5e56f28  proofs/S0-01/tools/pc/pc_post.sh            157 lines    +34  -12
8fd321169d9fe769  proofs/S0-01/tools/pc/pc_negative.py         46 lines    +29  -17
b06375eeaeced8b4  proofs/S0-01/tools/pc/run_leg.sh             68 lines      0    0   UNCHANGED
f4aa029239ff7d75  proofs/S0-01/tools/pc/collect_leg.sh         25 lines      0    0   UNCHANGED
aa250e3da7d42536  proofs/S0-01/tools/build_capture_record.py  180 lines    +17   -0
acc7d226357c3278  tests/test_s0_01_pc_post_scan.py            387 lines   +113  -47
468107ff49d1a1a2  tests/test_s0_01_pc_tools.py                606 lines    NEW
```

`proofs/S0-01/check_acp_conformance.py` and `tests/test_s0_01_check_acp_conformance.py` were NEVER opened for writing.
`git status --porcelain` over the scope after the whole mutation audit: exactly the 6 `M` + 1 `??` entries above.

## PREMISE — verified before any code

The brief's row #1 claim is TRUE, reproduced against the declared corpus (`bash scripts/realleg_sync.sh check` →
`realleg_sync: /root/s0-01-realleg/golden intact (142 files)`), scoring the checker's `_LEG_REQUIRED_FILES` +
`_LEG_OPTIONAL_DIRS` (`check_acp_conformance.py:1718-1726`, unchanged at HEAD) over every corpus positive leg:

```
run-1:     rejected=8 [backend-healthz-after.json, backend-healthz-before.json, hermes-config.sha256,
                       launch.exited, launch.ready, manifest-post.done, manifest-pre.done, teardown.txt]
           missing_required=2 [agent-stderr.txt, tee-status.json]
cancel:    rejected=8   (same names)          missing_required=2 (same)
shutdown:  rejected=7   (no teardown.txt)     missing_required=2 (same)
two-users: rejected=8   (same names)          missing_required=2 (same)
```

## DONE

**1. ONE list, in `pins.py` (ADD-only; nothing else in the file touched).**
`PINNED_LEG_FILES` at `proofs/S0-01/pins.py:184` — 35 names, `Counter{required: 26, optional: 4, excluded_on_collect: 3,
transient: 2}` — plus `PINNED_LEG_FILES_SINCE` (`pins.py:231`) and `PINNED_LEG_DIRS` (`pins.py:232`, 2 dirs). Every name
carries the producer that writes it, in a comment. Four statuses, because two of them are real and the brief already
names three: `required` / `optional` / `excluded_on_collect` (dropped by `collect_leg.sh --exclude`) / `transient`
(`manifest-pre.txt` and `manifest-post.txt`, which `gzip -9 -n -f` replaces in place). A consumer's allowlist is
`required | optional | PINNED_LEG_DIRS`.

Derivation is mechanical, not typed: the mapping was read off the producers and cross-checked against the corpus, and
four test directions keep it honest:
* `tests/test_s0_01_pc_tools.py:159-170` — `test_every_corpus_leg_entry_is_in_the_pinned_mapping`, the corpus ⊆ the mapping.
* `tests/test_s0_01_pc_tools.py:183-196` — every `required` name really present, under the corpus-version rule.
* `tests/test_s0_01_pc_tools.py:222-231` — `test_every_producer_write_lands_in_the_pinned_mapping`, producers ⊆ the mapping.
* `tests/test_s0_01_pc_tools.py:233-242` — `test_every_pinned_name_has_a_producer`, no orphan entry.

Rejected alternative: extending the checker's private set — that is how the two lists drifted.

**2. `capture.json` (#27/#28).** `build_capture_record.py:20` imports `pins`; `:63-69` fails on any missing `required`
FILE or `required` DIR, naming them, before the twelve default-on-absent gates run. Red-before/green-after, run:
`build_capture_record.py <empty-dir> run-1` was `rc 0` writing `{"capture": …, "files": {}, "version": 2}`; it is now
`rc 1` with `run-1: missing required leg files: argv.txt, backend-healthz-after.json, …, timeline.jsonl` (26 names).
`capture.json` itself is `optional` in the mapping (`pins.py:226`), so the checker admits it once it adopts the list.

**3. The scan header cannot lie (#5/#6; tests 4.2/15.2).** `pc_post.sh`:
* `is_pinned` at `:36-47` — pinned by ENTRY POINT: `argv[0] == PINNED_BUZZ_ACP_EXE_REALPATH`, or `argv[1] in
  (PINNED_TEE_PATH, PINNED_AGENT_REALPATH)`. No substring, anywhere.
* `keep` at `:87` is the body; `pinned_present` at `:95` is counted over that SAME list.
* header at `:93-96`: `# process-scan v2.4 … rows=<len(keep)> … table_rows=<len(rows)> utc=…` — two populations, two
  names, never asserted equal.
* `tests/test_s0_01_pc_post_scan.py:82-83` — `_parse` asserts `int(m.group(_ROWS)) == len(rows)` on EVERY caller, and
  fails with `header rows={m.group(_ROWS)} but the body carries {len(rows)} rows` (the sweep's one-line fix for 4.2/15.2).
* `tests/test_s0_01_pc_post_scan.py:344-378` — `test_pinned_present_is_exact_over_a_synthetic_table` keeps its shape and
  states in its docstring why both of its expectations changed.
* `tests/test_s0_01_pc_post_scan.py:271-301` — replaces the retired VERIFY-CK8 F14 test with the #6 decoy through real
  processes. `pinned_present` is now EXACT from inside one test even under 8 xdist workers, which v2.3 could only bound
  (`tests/test_s0_01_pc_post_scan.py:151`) — AF-AP-59's flakiness is designed out rather than tolerated.

**4. `pc_launch.py` fail-loud (#12, #25, #31, #32, #48, #52).** Six helpers extracted so each fix is reachable from a
test instead of buried in a 190-line `main()`; `main` calls them at `:247`, `:248`, `:304`, `:308`, `:310`, `:335`.
* `wait_for_manifest` `:80` — failure-aware: a non-empty `manifest-<phase>.log` with no `.done` is the failure
  signature, and its tail is surfaced (#32).
* `summary_tail` `:101` — `<empty summary>` instead of `IndexError` (#48).
* `wait_for_tee_identity` `:111` — named `SystemExit`, no `_note` default (#31).
* `buzz_identity` `:126` — `try/except OSError` → `pc_launch: buzz-acp exited during identity capture (rc=…)` (#12).
* `session_closure` `:139` — `ps -s <buzz pid>` (`:146`), fail-loud when the session is gone (`:154`) (#52).
* `redact_environ` `:167` — `len`/`sha256_12` on the RAW bytes (`:181`) (#25).
The stale comment my change falsified ("from the live process table") was fixed in the same edit (`:333`).

**5. `pc_negative.py` propagates the probe's exit code (#33).** Body wrapped in `main()` (`:19`) returning `rc` (`:42`),
`raise SystemExit(main())` (`:46`). Tested through the REAL wrapper and a REAL subprocess with a stub probe, rc ∈ {3,1,0}.

**6. `run_leg.sh` / `collect_leg.sh`.** Both already carry `set -euo pipefail`; NO CODE CHANGE was needed, so none was
made. The agreement is now tested: `tests/test_s0_01_pc_tools.py:526-536` declares each pattern's disposition and parses the
`--exclude=` literals out of the script, `tests/test_s0_01_pc_tools.py:538-559` checks each disposition against the
mapping mechanically, `tests/test_s0_01_pc_tools.py:561-568` checks the reverse direction, and
`tests/test_s0_01_pc_tools.py:583-604` packs a framedir carrying every mapping name with the real `tar` and the real
exclusion list and asserts the unpacked shape.

**7. Report discipline.** `scripts/report_lint.py` over this report, with a `--map` per scope file:
`report_lint: 39 refs — OK 29, NEAR 2, MISS 0, UNCHECKABLE 8, UNRESOLVED 0 (worktree)`. **MISS 0.** The heuristic rows:
both NEARs are the same reference, `scripts/realleg_sync.sh:30` (the claim token sits one line off the cited `pc-build`
case), and the 8 UNCHECKABLE rows are report lines whose reference carries no backticked claim token for the linter to
test — each is a pointer to a test or producer line named in full elsewhere in this report. `ap_screen.py` below.

## GATES (pasted verbatim)

Static-copy gate — `git archive <rev>` + exactly the lane's working-tree files, `scripts/test_summary.sh` twice, under
`--basetemp` in the session scratchpad:

```
RESULT: rev=2823f05dffa1 files=9 runs=2 identical=yes rc=0 summary="54 passed in 1.37s 54 passed in 1.27s"
RESULT: rev=4d2f31351645 files=7 runs=2 identical=yes rc=0 summary="55 passed in 1.50s 55 passed in 1.44s"
```

(The 54→55 delta is the `mentions` directory arm added to `test_build_capture_record_takes_its_required_list_from_pins`
after the whole-file AP screen; the second RESULT is the final code at current origin HEAD.)

Other gates:
* `pyflakes` over every Python file touched → rc 0, no output.
* `bash -n` → `OK proofs/S0-01/tools/pc/pc_post.sh`, `OK …/run_leg.sh`, `OK …/collect_leg.sh`.
* `python3 scripts/lint_delta.py --base 2823f05` → `12 .py changed, 0 NEW pyflakes hit(s), 0 removed`, rc 0.
* Every other `pins`-importing test file, at the PIN with only my `pins.py` on top
  (`tests/test_s0_01_negative_contract.py tests/test_s0_01_check_initialize.py tests/test_s0_01_acp_probe.py`) →
  `161 passed in 47.90s`. The `pins.py` addition is inert for its existing consumers.
* Process census: `ps -eww -o pid,ppid,etimes,stat,args` filtered on my own spawn signatures → no rows; 117 processes on
  the box, none mine. Every process this lane started was killed by pid.
* Mutants: applied to a scratch copy under the session scratchpad, restored BY COPY from the pristine archive after each
  run; `git status --porcelain` over the scope afterwards is exactly my 7 entries.

## MUTANT TABLE (16 applied, 16 killed; killer line pasted)

| # | mutant | file | verdict — killed by | killer line |
|---|---|---|---|---|
| 1 | LIST-DRIFT (drop `launch.ready` from the mapping) | pins.py | KILLED `test_every_corpus_leg_entry_is_in_the_pinned_mapping` | `AssertionError: corpus entries no consumer would admit: {'run-1': ['launch.ready'], 'cancel': ['launch.ready']…` |
| 2 | PRODUCER-UNLISTED (`pc_post.sh` writes `leak-report.json`) | pc_post.sh | KILLED `test_every_producer_write_lands_in_the_pinned_mapping` | `AssertionError: proofs/S0-01/tools/pc/pc_post.sh: writes names outside pins.PINNED_LEG_FILES: ['leak-report.json']` |
| 3 | MAPPING-ORPHAN (a mapping name no producer writes) | pins.py | KILLED `test_every_pinned_name_has_a_producer` | `AssertionError: pinned names no producer writes: ['never-written.json']` |
| 4 | TEE-WRITES-A-NEW-NAME (`tee-status.json` → `tee-heartbeat.json`) | frame_tee.py | KILLED `test_every_producer_write_lands_in_the_pinned_mapping` | `AssertionError: proofs/S0-01/tools/frame_tee.py: writes names outside pins.PINNED_LEG_FILES: ['tee-heartbeat.json']` |
| 5 | PINNED-OVER-TABLE (`pinned_present` over the full table again) | pc_post.sh | KILLED `test_pinned_present_is_exact_over_a_synthetic_table` | `AssertionError: # process-scan v2.4 mode=after rows=4 … owned_present=1` (the header tuple assertion) |
| 6 | SUBSTRING-PINNED (`any(p in cmd …)` restored) | pc_post.sh | KILLED `test_a_process_that_only_mentions_a_pinned_path_is_not_counted_as_pinned` | `AssertionError: assert 14222 not in {14220, 14222}` (the decoy is back in the body) |
| 7 | ROWS-LITERAL (`rows=4`) | pc_post.sh | KILLED `test_after_scan_persists_the_owned_closure_and_the_header` | `AssertionError: header rows=4 but the body carries 3 rows` |
| 8 | TABLE-ROWS-EQUALS-ROWS (`table_rows` counted over the body) | pc_post.sh | KILLED `test_after_scan_persists_the_owned_closure_and_the_header` | `AssertionError: assert 3 > 3` |
| 9 | CAPTURE-GREEN-ON-NOTHING (`if missing:` → `if False:`) | build_capture_record.py | KILLED `test_build_capture_record_fails_on_a_leg_with_no_timeline` | `AssertionError: (0, 'run-1: 0 raw files, 0 timeline entries…` |
| 10 | READLINK-UNGUARDED (drop the `try/except OSError`) | pc_launch.py | KILLED `test_pc_launch_names_a_buzz_exit_during_identity_capture` | `FileNotFoundError: [Errno 2] No such file or directory: '/proc/4242/exe'` |
| 11 | NOTE-DEFAULT (return the path instead of exiting) | pc_launch.py | KILLED `test_pc_launch_fails_when_the_tee_identity_never_appears` | `Failed: DID NOT RAISE SystemExit` |
| 12 | WAIT-SUCCESS-ONLY (drop the failure signature) | pc_launch.py | KILLED `test_pre_manifest_wait_breaks_on_a_manifest_error` | `AssertionError: assert 'pre manifest failed before its .done marker' in 'pc_launch: pre manifest did not finis…` |
| 13 | SUMMARY-INDEX (`lines[-1]` unguarded) | pc_launch.py | KILLED `test_pc_launch_survives_an_empty_pre_manifest_summary` | `IndexError: list index out of range` |
| 14 | WORLD-CLOSURE (`ps -eo` full table again) | pc_launch.py | KILLED `test_pc_launch_owned_closure_is_scoped_to_the_buzz_session` | `AssertionError: [14816, 14818, 14819]` (the detached grandchild adopted) |
| 15 | NEGATIVE-RC-DROPPED (`return 0`) | pc_negative.py | KILLED `test_pc_negative_propagates_the_probe_exit_code` | `assert 0 == 3` |
| 16 | FINGERPRINT-ON-REPLACED (hash the decoded string) | pc_launch.py | KILLED `test_env_redaction_fingerprints_the_raw_bytes` | `AssertionError: assert 7 == 8` (lossy length vs raw length) |

Mutant 14 is worth a note: on its first run it was killed only by the *dead-session* arm, because the original scoping
test could not tell `ps -s` from `ps -eo` (both return the same set for a plain parent→child tree). That was a hollow
green in MY test; `tests/test_s0_01_pc_tools.py:418-431` now spawns a DETACHED grandchild — ppid inside the closure,
session outside it — which is the only shape that discriminates, and the mutant is killed by the right test.

## ANTI-PATTERN SCREEN (`scripts/ap_screen.py`, whole files) — every hit classified BY RUNNING

`--tests tests/test_s0_01_pc_tools.py tests/test_s0_01_pc_post_scan.py` → `TEST_SCREEN over 2 path(s): 0 hits over 2 files`.

Production (`proofs/S0-01/tools/pc proofs/S0-01/tools/build_capture_record.py proofs/S0-01/pins.py`) →
`AP_SCREEN over 3 path(s): 21 hits over 4 files`:

| class | hits | classification |
|---|---|---|
| AF-AP-40 | 10 (build_capture_record.py `:71,95,100,106,113,118,133,139` +2) | **Was the defect (#27); now DOMINATED.** Every one of those `.exists()` / `.is_dir()` names is `required` in the mapping, so `:63-69` proves it present first. The screen surfaced a residual I had missed — the two required DIRS were not covered — and it is now fixed (`:65`) with the `mentions` arm added to the parametrised test. Run: dropping `timeline.jsonl` / `owned-pids.json` / `process-scan-teardown.txt` / `mentions` each gives `rc 1` naming exactly that entry. |
| AP-32 | 6 (pc_launch `:45,181`; build_capture_record `:23,24,28,45`) | **Reviewed-safe, consumer named.** `pc_launch:45` `sha256_file` feeds `hermes-config.sha256` and `buzz_acp_exe_sha256`, both compared against pins by the checker. `:181` is the #25 fix itself — the hashed form is now exactly the bytes `/proc/<pid>/environ` holds, pinned by `test_env_redaction_fingerprints_the_raw_bytes`. `build_capture_record`'s hashes feed `capture.json`, which the checker never trusts (its own docstring line 2). |
| AF-AP-45 | 2 (pc_launch `:143` comment, `:146` the `ps -s` call) | **Reviewed-safe, classified by RUNNING.** The closure is a MEMBERSHIP set, not a liveness claim; the STATE-column classification lives in the consumer. Probe: a parent that never reaps its child → `zombie pid 10544 state Z, in closure: True`, then the real `pc_post.sh scan after` over that `owned-pids.json` → `# process-scan v2.4 … owned=2 owned_present=1 pinned_present=0 owned_zombies=1 table_rows=97`, `BODY has the zombie: False`. A zombie is counted as a zombie and never as a survivor — the AF-AP-45 remedy, already implemented at `pc_post.sh:60-63` (`if parts[3].startswith("Z")` … `zombies.add`). |
| AF-AP-55 | 2 (pc_launch `:68` pre-existing `alive_pinned_buzz`, `:134` my `buzz_identity`) | **Not applicable — single-stage.** buzz-acp is a native binary launched directly as `PINNED_LAUNCH_ARGV[0]`, with no wrapper and no later `exec`; the read is ~12 s after launch. Evidence: the real corpus records `buzz_acp_exe_realpath = /home/rocco/s0-01-pinned/buzz/target/release/buzz-acp` and `buzz_acp_exe_sha256 = a5a17ffc…` = `pins.PINNED_BUZZ_ACP_SHA256`, which the checker compares — a wrapper stage would fail that pin. SWEEP-prod #11's AF-AP-55 defect is the two-stage AGENT in `frame_tee.py` (lane B5i), not this. |
| AF-AP-41 | 1 (build_capture_record `:108`) | **Pre-existing, untouched, non-load-bearing.** A regex over the startup line into `capture.json`; the checker pins the startup line itself token-by-token in `check_config_echo`. |

## DISCREPANCIES (things the brief or the sweep got wrong, with the evidence)

**D1 — the brief's pinned rule "for buzz-acp and the agent compare `/proc/<pid>/exe` realpath to the pinned realpaths"
cannot identify the agent, and I did not implement it.** Evidence, from the real corpus's own
`process-scan-after.txt` (run-1) and `runtime-identity.json`: the agent row is
`/home/rocco/s0-01-pinned/.venv-hermes/bin/python3 /home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp`, and the
identity file records `agent_interpreter_realpath = /usr/bin/python3.13`. `hermes-acp` is a SCRIPT, so its
`/proc/<pid>/exe` is the interpreter and never `PINNED_AGENT_REALPATH` — the exe rule would silently never match the
agent. I applied the brief's own mechanism for the structurally identical tee (`argv[1] ==` the pinned path) to the
agent as well, and dropped the `/proc/exe` read from the scan entirely, for three reasons: (i) it cannot fire for two
of the three pinned processes; (ii) the buzz-acp arm cannot fire in ANY sandbox test either, because the pinned path
cannot exist here and the predicate lives inside a `python3 - <<PY` heredoc that no test can monkeypatch — an
emitted-but-unreachable check is the hollow green the build loop forbids; (iii) exact token equality against an
absolute pinned path kills the substring defect completely (mutant #6) with no extra syscall. `/proc/<pid>/exe` is
still the identity oracle where it is verified and reachable: `pc_post.sh:120` reads it (`readlink /proc/$PID/exe`)
before signalling the buzz-acp pid, and `pc_launch.buzz_identity` records it into `runtime-identity.json` against a
pinned sha.

**D2 — `agent-stderr.txt` has NO positive-leg producer at all.** The brief describes it as one of "2 it REQUIRES"
that the corpus lacks, alongside `tee-status.json` — but the two are not the same problem. `tee-status.json` IS
written by `frame_tee.py`, so a v2.3+ capture has it and the corpus is simply older. `agent-stderr.txt` is written
ONLY by `proofs/S0-01/tools/acp_probe.py` (two `os.path.join(framedir, "agent-stderr.txt")` sites), into the NEGATIVE
leg; `grep -rn agent-stderr proofs/S0-01 --include=*.py --include=*.sh` (excluding `archive/`) finds no other writer.
Line numbers for that file are deliberately omitted: lane N5h holds it and they moved twice during this lane. So the checker's F20 rule
(`check_acp_conformance.py:1737`, `agent-stderr.txt` REQUIRED in every positive leg) is UNSATISFIABLE by the current
pipeline — no re-capture can produce it. It is therefore deliberately NOT in `PINNED_LEG_FILES`:
`pins.py:180-183` carries the comment beginning `NOT here, deliberately`;
`tests/test_s0_01_pc_tools.py:244-254` is `test_no_positive_leg_producer_writes_agent_stderr_txt`, which pins the
finding so a fix flips the test. The fix belongs to the tee (drain the agent's stderr to that name) or to the checker
(drop F20) — both outside P5a's scope.

**D3 — SWEEP-prod #1 lists `manifest-pre.txt.gz.sha256` among the producer names the F21 allowlist rejects "per leg",
but no corpus leg carries it, for a reason the sweep did not name.** `pc_manifest.sh:70` writes it (`sha256sum "$OUT.gz"` into `$OUT.gz.sha256`);
the `tar czf` at `collect_leg.sh:15` does NOT exclude it — proved empirically: a framedir containing
`manifest-pre.txt.gz.sha256` packed with the real exclusion list unpacks with that file present (GNU tar 1.35). It is
absent from the real-leg corpus because `scripts/realleg_sync.sh:30` (`pc-build`) strips
`--exclude='manifest-*.txt.gz.sha256'` explicitly. So the sidecars ARE in a collected leg and are NOT in the corpus:
the mapping calls them `optional` (`pins.py:213`) with that reason in the comment — admit, never require.

**D4 — the committed `proofs/S0-01/evidence/golden/` tree is v1-shaped and is not what any current producer writes.**
It carries `env-names.txt`, `mention-owner.json`, `mention-owner.err`, `capture.json` and no `timeline.jsonl`. Those
v1 names come from `proofs/S0-01/tools/archive/build_capture_record_v1.py`, not from the v2 pipeline, so they are not
in the mapping. SWEEP-prod #1 attributes them correctly to "the COMMITTED tree"; the note matters because a reader
could otherwise take them for producer output.

**D5 — a v2.3 property is deliberately RETIRED, not preserved.** VERIFY-CK8 F14's contract (a helper-shaped foreign
row dropped from the body while still counted in the header, surfacing as a loud `pinned_present … inconsistent with
body` Failure) cannot survive the #5 fix: once both counters come off one list they agree by construction. The drop is
now visible only as `table_rows > rows`. The old test is replaced by
`tests/test_s0_01_pc_post_scan.py:271-282`, whose docstring states the retirement in those words rather than letting it
be quietly lost.

**D6 — `#52`'s pinned fix narrows the owned set, and that costs something.** `ps -s <buzz pid>` cannot see a
descendant that calls `setsid()` for itself; the full-table walk could. The pinned tree does not do that —
`frame_tee.py:232` spawns the agent with a plain `Popen` (no `start_new_session`), which is why the real corpus's
three-row scan is one session — but the narrowing is real and is stated in the test's docstring, not hidden.

## NOT_DONE (first-class)

1. **NOT run on the PC — no bridge use in this lane, by the brief.** Every PC-only path is unit-tested against a
   monkeypatched primitive and has never executed end to end on the PC: `wait_for_manifest` (#32), `buzz_identity`
   (#12), `wait_for_tee_identity` (#31), `summary_tail` (#48) and the `pc_negative.py` wrapper against the REAL pinned
   agent (#33). `session_closure` (#52) and `redact_environ` (#25) DID run against real sandbox processes and real
   `/proc/<pid>/environ` bytes, but not against buzz-acp. The end-to-end proof is the coordinator's re-capture with the
   final tools.
2. **`tests/test_s0_01_audit_cp5_controls.py` goes RED — 2 of 3 — and I may not touch it.** Measured at current HEAD
   `4d2f313`: baseline `3 passed in 0.94s`; with my `pc_post.sh` on top, `2 failed, 1 passed in 1.05s`
   (`test_clean_shutdown_empty_after_scan_passes`, `test_shutdown_owned_survivor_is_named_whatever_its_command`). Both
   fail on the same cause — the checker's `_parse_scan_v23` rejects a v2.4 header:
   `process-scan-after.txt has no enumeration header`. **This is a sequencing dependency, not a defect in this lane;
   the change must land together with the checker's adoption below.**
3. **What the checker's next round must change (read at HEAD `4d2f313`, not at the PIN):**
   * `check_acp_conformance.py:154-155` — the header regex → `v2\.4` plus `table_rows=(\d+)` before `utc=`.
   * `:1234` and `:1338` — `rows=0` currently means "enumeration did not run". Under v2.4 `rows` is the BODY counter
     and a CLEAN teardown legitimately has `rows=0`; the enumeration check must read `table_rows` instead, or a
     successful shutdown fails.
   * `:1249-1253` — F17's `body_pinned` still counts by substring (`PINNED_TEE_PATH in cmd`). The producer no longer
     emits such rows, but the checker computes over the collected body: an OWNED row that merely mentions a pinned path
     would count in the checker and not in the header, i.e. a false Failure. It must adopt the entry-point rule.
   * `:1718-1726` — `_LEG_REQUIRED_FILES` / `_LEG_OPTIONAL_DIRS` → import `pins.PINNED_LEG_FILES` / `PINNED_LEG_DIRS`
     (allowlist = `required | optional | dirs`; required = `required`, minus `PINNED_LEG_FILES_SINCE` on an older corpus).
   * `:1737` — F20 `agent-stderr.txt`: unsatisfiable, see D2.
4. **Forward drift already visible:** lane B5i's uncommitted `frame_tee.py` declares `.runtime-identity.tmp`. Dot-prefixed
   names are deliberately outside the mapping — `pins.py:171-173` says they are `atomic-write scratch` and `never
   a leg ENTRY`, and one that survived a crash SHOULD be rejected as an unexpected entry — and the parser skips them,
   so B5i can land without
   touching this list. A NON-dot new name from any producer will fail `test_every_producer_write_lands_in_the_pinned_mapping`
   — by design.
5. **Not attempted:** the full `tests/` suite in one run (the checker set alone is ~17 min, over the Bash cap) and the
   PC `-n 8` gate. I ran, instead: my two files ×2 at two revisions, the whole `tests/test_s0_01_audit_cp5_controls.py`
   at both revisions, and every other `pins`-importing test file (`161 passed in 47.90s`).

## SELF-ATTACK — the three likeliest ways this is wrong

**A1 — "the producer parser is a mirror that agrees with itself, so direction (c) proves nothing."** The parser reads
the producers' bytes, not my mapping, and four mutants attack exactly this seam: PRODUCER-UNLISTED and
TEE-WRITES-A-NEW-NAME add a name to a real producer (both killed, naming the new name), MAPPING-ORPHAN adds a name to
the mapping only (killed), and `test_the_framedir_parser_fails_loud_on_an_unresolved_placeholder`
(`tests/test_s0_01_pc_tools.py:257-266`) proves the parser refuses a token it cannot resolve rather than dropping it;
the assertion it triggers is `unresolved placeholder in a framedir name`, at `tests/test_s0_01_pc_tools.py:144-145`.
That is the one way a parser like this fails silently. It is still bounded: it recognises the anchor forms the current producers
use (`os.path.join(FD|framedir, …)`, `d / "…"`, `f"{fd}/…"`, `"$FD/…"`, `OUT=$FD/…`), so a producer written in a NEW
idiom would be invisible. `test_every_producer_write_lands_in_the_pinned_mapping` therefore also asserts the parse
found something at all — `tests/test_s0_01_pc_tools.py:229` says `the parse is blind, not the file empty` — which
catches the whole-file blind case but not a single new idiom in a known file.

**A2 — "the mapping is graded against one corpus, and that corpus is v2.2, so `tee-status.json` was never actually
checked."** True and stated: `_corpus_version()` returns `v2.2` for `/root/s0-01-realleg/golden` because no leg carries
a versioned scan header (the corpus's first scan line is a body row) or a `tee-status.json`. So direction (b) grades 25
of the 26 required names. The gap is not hidden: `PINNED_LEG_FILES_SINCE` names the gated file,
`test_the_corpus_version_rule_actually_discriminates` (`tests/test_s0_01_pc_tools.py:197-203`) pins that the rule really
changes the required set, and
`tee-status.json` is still covered by direction (c) (`frame_tee.py` writes it) and by mutant 4. The first v2.4
re-capture promotes the corpus and closes it for real.

**A3 — "dropping the `/proc/<pid>/exe` check weakens the scan; argv can be spoofed."** It can — a process may set
`argv[0]` freely, and `ps` shows what it set. Three things bound that. First, the scan is an ENUMERATION over the
owner's own box, and the identity oracles that gate the proof are elsewhere and unspoofable: `pc_post.sh:120` reads
`readlink /proc/$PID/exe` before it signals anything, and `runtime-identity.json` carries the exe sha the checker compares to
`pins.PINNED_BUZZ_ACP_SHA256`. Second, membership in `owned-pids.json` comes from the process TREE
(`session_closure`), not from any argv. Third, the alternative was worse in a measurable way: the exe read cannot
identify the tee or the agent at all (D1), so a rule built on it would count 1 of the 3 real pinned processes while
looking rigorous. What I did NOT do is prove the exe read unnecessary on the PC — it has never run there under v2.4,
and item 1 of NOT_DONE says so.

Two smaller ones I checked and could not break. First, the header field ORDER change: `table_rows` sits before `utc=`,
so every existing `m.group(N)` in the test file keeps its meaning — the named constants `_ROWS, _TABLE_ROWS = 2, 9` at
`tests/test_s0_01_pc_post_scan.py:45` make that explicit, and the two counter-moving mutants (7, 8) prove it. Second,
`pins.py` growth breaking a consumer that enumerates the module: there is no such consumer
(`grep -n 'dir(pins)\|vars(pins)' tests/*.py` → none) and the other three `pins`-importing test files are `161 passed`.
