# T94 report — failed Hermes session never becomes a report (task #200) + relaunch never inherits a dead loop's FAILED (task #167)

LANE: t94 (PC continuation, code-implementer, private PIN copy). STATUS: PROPOSAL COMPLETE; independent adversarial verification NOT run.

## 1. Premise re-measure (contract item 1) — HOLDS

```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short origin/...; git rev-parse --short HEAD
2026-09-23T16:15Z
c6dcd61            (origin)
be848a1            (local HEAD; the brief says the four files are byte-identical at both — verified below)
$ origin-blob  worktree-blob  HEAD-blob  lines  file
183f337eff91 183f337eff91 183f337eff91 529 harness-ports/bin/pc-lane.sh
6d6024139163 6d6024139163 6d6024139163 609 scripts/pc_lane.sh
67ed1e0c3c56 67ed1e0c3c56 67ed1e0c3c56 641 harness-ports/tests/test_pc_lane.sh
948c19ac580c 948c19ac580c 948c19ac580c 452 harness-ports/tests/test_pc_lane_dispatcher.sh
$ grep anchors on R: 269 CAPACITY_RX · 270 QUOTA_RX · 304 SAFETY_RX · 305 PERSIST_RX · 450 --usage-file · 496 refusal grep ·
  503 DRAFT REPORT · 509 usage.json block                                  (all identical to the brief)
$ grep anchors on D: 384 probe · 386 *FAILED-UNRETRIED*) · 390 *FAILED*) · 413 *READY*) · 433 report ->   (identical)
$ grep -c 'pc-lane.sh\|pc_lane.sh' scripts/gate_files.txt
2
$ bash harness-ports/tests/test_pc_lane.sh | tail -1            (rc=0)
60 passed, 0 failed
$ bash harness-ports/tests/test_pc_lane_dispatcher.sh | tail -1 (rc=0)
pc_lane dispatcher: 39 passed, 0 failed
$ od -c <scratchpad>/evidence/report-pc-verify-t92-t90r3-pcj1.md--433d15e.md   (50 bytes, 15:33)
0000000   H   T   T   P       4   0   0   :       [   4   0   0   ]   :
0000020       N   o       u   s   e   r       q   u   e   r   y       f
0000040   o   u   n   d       i   n       m   e   s   s   a   g   e   s
0000060   .  \n
```
NOT re-measured (by rule): the premise's `scripts/pc.sh` usage.json read — this lane makes no bridge call.

## 2. Seams verified before code (build-loop step 1)

- R's post-loop order at the PIN: loop `done` at `R@feb26d7c:490` -> refusal grep at `R@feb26d7c:496` -> empty-report
  draft promotion at `R@feb26d7c:502-505` -> transcript export at `R@feb26d7c:509-519` -> final rc at
  `R@feb26d7c:521-529`. The safety family exits 70 inside the PIN loop at `R@feb26d7c:459-468`; capacity/persist retries continue
  inside it. Therefore the new post-loop rule cannot pre-empt those paths.
- Hermes writes usage.json through `--usage-file "$LANE_DIR/usage.json"` at R:464. T1's new fake Hermes reads that exact argv flag,
  so the tests bind to the runner's real seam, not to a path the test chooses.
- D's poll `probe=` at D:389 tests the current-dispatch FAILED condition first; D ships `brief.md` on every dispatch at D:249-252,
  FIRST and RESUME alike. D fetches `USAGE_B64` after its `report ->` line at D:443-447.
- The never-a-gate screen (`scripts/no_laya_in_gates.py`) parses R and D as shell text and allows exactly D's two `.` sources
  (`no_laya_in_gates.py:95-96`); this lane adds no source edge. R's verdict parser is inline `python3 -c` at R:510.
- Other readers of the lane markers: none. Literal sweep for `/FAILED|FAILED.stale|usage.json|report-draft.md|.lanes/` over
  scripts/, harness-ports/, .claude/hooks: only R, D, T1, T2 and pc-setup.sh (its own `.lanes/*.log` files). GitNexus impact:
  `pc-lane.sh` "not found", `pc_lane.sh` risk UNKNOWN (no callers resolved; exec edges are invisible to the index) — confirmed by text
  search: D:359 launches R; run-all.sh:27 runs T1 (and runs T2 and test_pc_lane_admission.sh, which does not touch the probe/fetch).
  PC continuation recheck: graft returned no indexed shell definitions or semantic hits; GitNexus's clone index was 832 commits stale,
  so `risk: UNKNOWN` remains unresolved rather than being treated as low risk. `scripts/why.sh` and the generated lane-context pack
  independently recovered the runner/dispatcher history and test entry points.
- Primitives re-measured on the PC (Fedora 42, bash 5.2.37): `test A -ot B` resolves sub-second mtimes (two files 52 ms apart);
  a missing A is older than an existing B; an existing A is not older than a missing B; `date -u -r` printed
  `20260923T172927.946783327Z`. This confirms the predecessor's design premise on the execution host.

## 3. Design decisions (contract items 2-4)

- Item 2 (R): one new block between the loop's `done` and the refusal block; the refusal block's `if` becomes `elif`, so a
  runtime verdict of "failed" DECIDES and no text screen re-reads the promoted draft (without the `elif`, a draft or a failed output
  that contains `exhausted their quota` — QUOTA_RX is unanchored — would be turned into FAILED and report.md deleted).
  The promoted header's FIRST line starts `DRAFT REPORT — ` (so item 3's poller exemption recognizes it); the 200 bytes of the
  failed output go on ONE prefixed line with newlines shown as `\n` (a raw paste could put `API call failed …` or `No reply: …`
  at a line start, which D's probe greps anywhere in report.md and would misread as FAILED-UNRETRIED).
- Item 4 (AF-AP-140): BOTH, for two different windows.
  R at loop start (after the pidfile and traps, before any slow step): a FAILED left by a dead loop is renamed to
  `FAILED.stale-<its own mtime, UTC>` (a `.<pid>` suffix on a name collision, so an older stale marker is never overwritten).
  Why R: only the loop knows it is a new loop; without the rename the stale file would also shadow a relaunched loop that SUCCEEDS
  (D reads FAILED before READY), and a later FAILED from the new loop would overwrite the evidence.
  D in the probe: FAILED is terminal only when it is NOT OLDER than this dispatch's `brief.md` (both PC-clock mtimes, no skew).
  Why D too: between D's launch call and R's rename there is a window (setsid start, self-copy exec) in which D's first probe can
  read the stale file — a race R alone cannot close; the binding also covers a runner that predates the rename.
  Rejected: a pure reorder (liveness before FAILED). In the launch window there is no pidfile yet, so a reorder still reads the stale
  FAILED; moving the launch-window RUNNING rule above FAILED would also delay a live loop's fail-fast verdict.
- Test seam: `run_hermes_verdict` drives the real R script with a fake Hermes bound through its actual `--usage-file` argv;
  its fixture controls use neutral `FAKE_*` environment names, so R cannot reinterpret them as route settings. The first PC run
  exposed a predecessor test bug (fixture exported `FAKE_*` but read `HERMES_*`: 61 passed, 6 failed); fixing that test seam and
  making default JSON an explicit branch produced 67/67. T2 drives the real D private-copy/poll/harvest path through its fake bridge.

## 4. Contract tests (item 5)

| Item | Named executable assertion | Final result |
|---|---|---|
| (a) failed 400 + draft | `a failed Hermes session promotes its draft under the failed-session header and preserves the 400 output` | PASS |
| (b) failed 400, no draft | `a failed Hermes session with no draft is FAILED rc 70, with no report.md and its output preserved` | PASS |
| (c) finished-looking output | `NEGATIVE CONTROL: completed=false rejects output that looks like a finished MERGE-READY report` | PASS |
| (d) successful verdict | `positive control: failed=false, completed=true keeps report.md byte-identical` | PASS |
| (e) absent / malformed metadata | two named warning assertions | PASS / PASS |
| (f) pre-fix runner defense | `a pre-fix runner's failed usage verdict keeps last output under a non-report name and exits 70` | PASS |
| promoted-draft boundary | `a failed session's promoted DRAFT REPORT is harvestable as partial evidence` | PASS |
| (g) stale FAILED | R preserves/renames the marker; D's probe binds it to the shipped `brief.md` mtime and polls RUNNING | PASS / PASS |

RED BEFORE FIX (measured in this continuation): the first T1 run was `61 passed, 6 failed`, specifically all six new runtime-verdict
fixtures. That red indicted the new fixture seam, not production: helper exports and fake-Hermes reads used different names. After
that repair, the final focused suites were deterministic across two consecutive runs:

```
67 passed, 0 failed
67 passed, 0 failed
pc_lane dispatcher: 42 passed, 0 failed
pc_lane dispatcher: 42 passed, 0 failed
```

## 5. Mutation audit (item 6; scratch copies only)

Every mutant was syntax-checked, then run from its own full `git archive feb26d7` copy overlaid with final R/D/T1/T2. Production
bytes were never mutated. The exact killer and final summary follow.

| Mutant | Mutation | Named killer | Result |
|---|---|---|---|
| m1 | remove R's runtime-failed branch | failed-draft / no-draft / completed-false controls | KILLED: `64 passed, 3 failed` |
| m2 | R reads `failed` but ignores `completed` | `NEGATIVE CONTROL: completed=false rejects output that looks like a finished MERGE-READY report` | KILLED: `66 passed, 1 failed` |
| m3 | truncate instead of preserve failed output | failed-draft / no-draft / completed-false preservation controls | KILLED: `64 passed, 3 failed` |
| m4 | promote draft without exact `DRAFT REPORT` header | failed-draft header assertion | KILLED: `66 passed, 1 failed` |
| m5 | remove D's failed-usage defense | pre-fix-runner defense assertion | KILLED: `pc_lane dispatcher: 41 passed, 1 failed` |
| m6 | revert D's AF-AP-140 mtime binding | stale-FAILED RUNNING assertion | KILLED: `pc_lane dispatcher: 41 passed, 1 failed` |

The m2 control was sharpened during the audit to carry `failed:false, completed:false`; a fixture with both failure indicators set
could not independently kill removal of the completed check. This is the required anti-hollow-green branch control.

## 6. Gates and screens (item 7)

```
bash-n-final rc=0
67 passed, 0 failed
67 passed, 0 failed
pc_lane dispatcher: 42 passed, 0 failed
pc_lane dispatcher: 42 passed, 0 failed
```

`git diff --check` returned rc 0. AP screen classification over whole files:

- R: two pre-existing hits only. AF-AP-45 at R:122 is the existing `pids=` census in `stop_session`; AF-AP-118 at R:444 is the
  existing `fallback_providers` explanatory comment. Neither intersects this diff.
- D: 0 hits.
- T1 test screen: one pre-existing AF-AP-87 hit at T1:448, the established `kill -0` process-control assertion. It does not intersect
  this diff.
- T2 test screen: 0 hits.

Full harness gate on final bytes:

```
test_pc_lane.sh                    67 passed, 0 failed
test_pc_lane_dispatcher.sh         pc_lane dispatcher: 42 passed, 0 failed
test_qwen_matrix_sh.sh             qwen-matrix-sh: 18 passed, 1 failed
1 SUITE(S) FAILED
RUN_ALL_RC=1
```

The same `SECOND_SIGINT` failure reproduced unchanged on the PIN archive (`qwen-matrix-sh: 18 passed, 1 failed`; PIN full run also
had unrelated stale hook-spool failures, so `2 SUITE(S) FAILED`). A focused rerun on final bytes again produced exactly
`qwen-matrix-sh: 18 passed, 1 failed`, where expected rc 130 was rc 7 after missing `SECOND_SIGINT/result.json`. This is pre-existing
and outside the T94 boundary; it remains visible and unfixed.

`lane_gate.sh` was attempted once with the brief's two shell scripts as `-t`; that tool invokes pytest and rejected them with
`(no match in any of [<Dir tests>])`, RESULT rc 1. This is an instrument mismatch, not a product result. The brief's mandated shell
gates above were run directly twice, as specified by the PC continuation venue notes.

## 7. File identity and changed surfaces

Identity captured by the attempted static-copy gate at 2026-09-23T18:02:24Z (report was then extended, so its final identity follows
at close):

- R: sha256 `fd281439ea3b5aafa8fbf5cdd519383304ac1db2cff7d065b9e64a1d22d4efe3`, 581 lines.
- D: sha256 `ac4df5df7cd08f53138f79f72cdbb3084674e000272211cb72cd949e9b073d65`, 624 lines.
- T1: sha256 `bce3c4ff9bf83979a7b075ebf706324ee4809f6cc700f80d1de7ff54ccb88968`, 736 lines.
- T2: sha256 `53b9fd42b46598a5da92d3e1020524ace9b4363c924c0851c4f64c2327189384`, 484 lines.

Changed behavior is confined to R's stale-marker and runtime-verdict blocks, D's dispatch-bound marker probe and usage defense, and
the matching T1/T2 fixtures. No bridge, real lane, server, credential, or owner process was touched.

- Current implementation anchors: R renames a predecessor marker at `if [ -e "$LANE_DIR/FAILED" ]` (R:137), parses
  `usage_verdict=` at R:516, and branches on `[ "${usage_verdict%% *}" = failed ]` at R:528. The failed output is copied by
  `cp -f "$REPORT"` at R:530; the exact promoted `DRAFT REPORT` header is at R:533; the no-draft path writes FAILED at R:539-543.
- D's mtime-bound probe starts with `(! test -f ... -o ... -ot ...)` at D:389. Its defense parses `USAGE_VERDICT=` at D:444,
  excludes only the exact `DRAFT REPORT` first line at D:449, then moves bad output to `FAILED_OUTPUT=` at D:450-453.
- T1's fake reads the real `--usage-file` argument at T1:536-539; the independent `COMPLETED_FALSE_JSON=` fixture is T1:574;
  T1's runtime-failed draft, no-draft, negative, success, warning, and stale-marker assertions span T1:579-633.
- T2's failed-usage defense fixture begins at T2:387, its promoted-draft boundary at T2:399, and its stale-marker probe assertion
  at T2:408-414.

## 8. Evidence tiers, self-attack, discrepancies, NOT done

VERIFIED:

- R/D parse; T1/T2 each run twice with identical final counts; all six named mutants die for their intended reasons.
- The full harness failure is pre-existing for the same qwen-matrix `SECOND_SIGINT` assertion on the PIN and final bytes.
- PC mtime semantics, stale-marker preservation, exact promoted header, output retention, rc 70 failure paths, byte-identical success,
  warning count, and the dispatcher non-report filename are executable assertions.

INFERRED:

- Shell-script call edges remain only partly mapped because graft indexed no definitions and GitNexus's clone graph was stale and
  does not resolve R; this report does not turn that absence into a reachability claim.

ASSUMED: none for the changed runtime behavior.

SELF-ATTACK:

1. R could key on only one runtime flag. Ruled out by m2 and the `failed:false, completed:false` control.
2. A failed output could still become a semantic-looking report. Ruled out in R by the MERGE-READY control and in D by the pre-fix
   runner control; m1 and m5 independently remove those defenses and go red.
3. A relaunch could still lose or inherit its predecessor's marker in the launch window. R asserts the old content survives under a
   stale name; D's command assertion requires the dispatch brief mtime binding; m6 removes it and goes red. A separate verifier must
   still attack real shell race timing; this builder does not self-accept that concurrency claim.

DISCREPANCIES:

- Resume instruction named `report-draft.md`, but it did not exist. `report.attempt1.md` held only the 503 refusal. The substantive
  predecessor draft was this tracked report; it was used and independently re-run before reliance.
- Original brief baselines were 60 and 39; final counts are 67 and 42 because T94 adds seven R assertions and three D assertions.
- `lane_gate.sh` is pytest-only despite the PC continuation asking to gate these shell suites through it; direct brief-prescribed shell
  runs are the real test instrument.
- Full `run-all.sh` is red on a pre-existing qwen-matrix signal test. This proposal does not claim full-suite green.
- GitNexus `detect-changes` against the stale clone graph reported no changes for this detached private worktree; diff/status and the
  generated lane context are the usable local change instruments.
- Final report lint: `report_lint: 31 refs — OK 12, NEAR 3, MISS 7, UNCHECKABLE 9, UNRESOLVED 0 (worktree)`; the
  `--min-refs 12` floor passed. This was bounded to three rounds as required; surviving heuristic misses are reported, not chased.

NOT DONE:

- No live PC lane, bridge call, real Hermes request, server action, commit, push, or outward-facing action.
- No fix to the unrelated qwen-matrix failure.
- No independent adversarial-verifier run and no final gate verdict. This is a self-validated build proposal for the sandbox verifier.
