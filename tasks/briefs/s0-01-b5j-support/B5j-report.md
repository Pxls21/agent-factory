# B5j report — S0-01 frame tee, round 15

PIN: `246bec7ccc7d6cf40bb16ce3cae08045b0106719`

This is a build-lane PROPOSAL. It is not a gate verdict and remains subject to the sandbox-side adversarial-verifier lane.

## NOT DONE / limits

1. No sandbox-side independent verification was performed. This PC lane uses the same model for implementation and review, so it cannot self-accept.
2. The intentionally hanging iterator shape was not run through pytest. It was reproduced only in a standalone, PID-scoped watchdog probe, as the brief requires.
3. VB-F12 (real-leg corpus `tee_sha256` re-capture), VB-F13 (separate PC agent-file stat), and VB-F14 are outside this lane and were not changed.
4. Pytest was run with the PC lane's Python 3.11 environment only. No 3.12/3.13 or xdist run was attempted.
5. The full 51-mutant harness contained seven invalid constructions. I do not count their green results as product survivals or as successful tests. The exact discrepancy and corrected runs are below.

## Evidence tiers

VERIFIED:

- `75998e7` is an ancestor of the PIN (`git merge-base --is-ancestor` rc 0), and the two scoped files were last committed there before the inherited lane patch.
- Vendored `acp.rs` sha256 is `44e82861763694d2b82d02b15ee100ffd6c78874a2b2282865e6656c539c38f1`. Its `shutdown()` range is 422-444; its `kill_process_group()` range is 2323-2329. Group `killpg(..., SIGKILL)` / direct-child fallback precedes the five-second bounded `self.child.wait()`.
- Every result below came from execution on a `git archive 246bec7` copy with only the two scoped working files copied over it, except the explicitly standalone hang probe and read-only status/census commands.

INFERRED:

- No adjacent caller needs a source change beyond this scope. The implementation change is a helper extraction/reuse plus prose; the rest of the increment is deterministic test hardening.

ASSUMED:

- None.

## FILE IDENTITY — final bytes

| file | sha256 | lines | bytes |
|---|---|---:|---:|
| `proofs/S0-01/tools/frame_tee.py` | `990a2ad24475fde35291cd940e5f02d5e8dcf8f413cb16e4948f46407362cdb0` | 567 | 24528 |
| `tests/test_s0_01_frame_tee.py` | `bbdd7cdbee35593e36244ace3942fbd4f310a3ca8ceccf49f5fb2cd6982f594a` | 3950 | 194620 |

Scoped delta versus the PIN: tee +51/-26; test +266/-60. The final tee hash differs from the inherited draft because I corrected one nearby stale comment which said every reference site carried the full clause; the tests now require those sites to carry only `PINNED_SHUTDOWN_CLAUSE` references.

## DONE

| item | final implementation and proof |
|---|---|
| Both sentence halves derived | `test:3752` contains `kill_sig_m = re.search`; `test:3758` contains `wait_call_m = re.search`; `test:3767` contains `kill_sig in kill_half`; `test:3773` contains `wait_method in wait_half`; `test:3779` contains `PINNED_SHUTDOWN_CLAUSE == expected_clause`. |
| One sentence, structurally | `test:3869` performs `re.split`. At `test:3871`, `len(buzz_sentences) == 2`. At `test:3895-3898`, `clause_rx` and `masked_sources` restrict masking to the clause. At `test:3922`, `assert not proximity`. |
| Every tee-pipe mention pinned | `test:3147` builds `mentions`; `test:3184` contains `assert not bad`; `test:3188` requires `len(mentions) >= 50` so the walk cannot pass empty. |
| Zombie branch observed | `test:2879` requires `_kill_own_grandchild(framedir) == "gone"`. Sites 1 and 2 require `_kill_own_grandchild(framedir) == "live"` at `test:653` and `test:1287`; site 3 requires `== "gone"` at `test:2807` and remains the declared by-construction survivor. |
| Deterministic `/proc` race guard | Production helper `tee:81` contains `def _reread_interpreter`; `tee:97-98` contains `agent interpreter re-sample: exited before identity`; `test:3599` calls `_reread_interpreter(pid_max + 1)`. |
| Signal identity pinned | `test:3005` requires `getattr(sig_args[0], "attr", "") == "SIGTERM"`. |
| Race aggregate non-vacuous | `test:3554` initializes `outcomes = []`; `test:3567-3569` computes `lost = marker in proc.stderr` and appends it; `test:3586` requires `any(not lost for lost in outcomes)`. |
| FIFO domain tested | `test:893` runs `os.mkfifo`; `test:897-900` contains both `proc.returncode == 64` and `proc.stderr.decode().strip()`. |
| Nearby comment made true | At `tee:49-52`, the comment contains `module` and `docstring` on adjacent lines and then says other comments/docstrings refer to the constant without restating it. |

## Static-copy gate

One foreground invocation after the final source edit:

```
== run 1/2: load 0.78 1.17 1.33
116 passed in 173.94s (0:02:53)   (pytest-exit: 0)
== run 2/2: load 1.62 1.45 1.41
116 passed in 174.39s (0:02:54)   (pytest-exit: 0)
RESULT: rev=246bec7ccc7d files=2 runs=2 identical=yes rc=0 summary="116 passed in 173.94s (0:02:53) 116 passed in 174.39s (0:02:54)"
lane_gate_wall=367.73 rc=0
```

The seven directly added or strengthened controls also ran together before the comment-only edit: `7 passed in 4.00s`. The final comment edit's sentence oracle then ran again: `1 passed, 115 deselected in 0.27s`.

## Standalone hang proof

The hang shape stayed outside pytest and was watchdoged.

- RED-before iterator shape against the PIN tee: after 3 s, the tee was still state S; main thread `wchan=hrtimer_nanosleep`, c2a thread `wchan=anon_pipe_read`, iterator reader alive, tee poll `None`. Closing only the probe's own stdin released it and the tee exited rc 0.
- The same raw iterator blocks on the final tee by design. The production tee drains to EOF; this increment closes the test-side admission path rather than inventing a production timeout.
- Bounded control: `_read_with_deadline` returned `None` at its 1.000 s deadline, tee stayed alive until client EOF, then exited rc 0 and its reader completed.

No name-matched signal or world process kill was used.

## Required B5j mutants — final bytes

All twelve contract mutants were reconstructed on fresh static copies after the final source edit:

```
MIRROR-3SITE                 KILLED  wait half does not name self.child.wait()
MIRROR-3SITE-ORDER           KILLED  kill half does not name derived SIGKILL / killpg
SEVENTH-SITE-PARAPHRASE      KILLED  module docstring has 3 buzz-acp sentences
SIXTH-SITE-TESTDOC           KILLED  kill token + derived bound in test-file window
SIXTH-SITE-TEECOMMENT        KILLED  kill token + derived bound in tee-file window
ZOMBIE-BRANCH-LIVE           KILLED  assert 'live' == 'gone'
PIPEREAD-ITERATION           KILLED  unbounded tee_proc.stdout Call
PIPEREAD-READLINES           KILLED  unbounded tee_proc.stdout Attribute
PIPEREAD-OSREAD              KILLED  unbounded tee_proc.stdout Attribute
PIPEREAD-ALIAS               KILLED  direct assignment and alias use both reported
RESAMPLE-NO-OSERROR-GUARD    KILLED  FileNotFoundError for /proc/4194305/exe
RESAMPLE-ALWAYS-FAILS         KILLED  all 20 trials lost the re-sample race
B5J-MUTANT-RESULT ran=12 killed=12 survived=0
```

The expected `GRANDCHILD-UNKILLED-S3` branch-assertion deletion survives by construction: `1 passed, 115 deselected in 30.80s`. Its fixture necessarily reaches the gone branch; sites 1 and 2 carry live-branch coverage.

## 51-run mutation discrepancy

The broad harness did execute all 51 rows: `ran=51 killed=43 survived=8 declared=1`. Seven nominal survivors were malformed or did not remove a claimed property:

1. `SITECOUNT-DUP` rewrote/reflowed the canonical sentence rather than adding an independent sentence. Correct insertion of a third exact sentence is killed: module docstring has three buzz-acp sentences.
2. `GRANDCHILD-UNKILLED-S1/S2` only deleted an assertion while still calling the helper; that mutation cannot make a passing run distinguish whether the deleted assertion was effective. Correct branch flips are killed at both sites (`'live' == 'gone'`).
3. `CENSUS-PKILL-DQ`, `CENSUS-PGREP-A`, and `CENSUS-WORLD` did not instantiate AF-AP-59's regex domain. Correct `pkill -f`, `pgrep -a -f`, and list-form `ps -ef` mutants all die: `CENSUS-MUTANT-RESULT ran=3 killed=3 survived=0`.
4. `R19-COLLECTOR` replaced one duplicated `is_file()` assertion with `assert True`; the next consumer assertion still enforces presence. Removing the consumer checks kills collection during import.

These invalid rows are excluded, not relabeled as successful mutation tests. The brief-required set is independently reconstructed and 12/12 killed above.

## 18-class self-sweep

Method: Python AST for statement/call shapes; regex/literal enumeration for textual APIs; execution of the focused mutations and the two full gates. Counts are for the final test file unless stated otherwise.

| class | count / method | result |
|---:|---|---|
| 1 presence gates | 154 AST `If` nodes | Relevant collectors are fail-loud; corrected collector-removal mutation dies. |
| 2 read receivers | 138 occurrences across `read_text`, `read_bytes`, `json.load`, `open`, `os.readlink` | Pipe reads are separately closed by the every-mention AST pin. |
| 3 stale tail reads | 1 literal `[-1]` | Existing guarded/static use; no new tail read. |
| 4 negative acceptance | 10 `assert ... not in` forms | Shutdown claim also has positive exact sentence/equality checks, so it is not held by negation alone. |
| 5 substring/tail anchors | 7 `startswith` / `endswith` calls | No new broad outcome classifier. |
| 6 env-domain fail-opens | 6 `os.environ.get` calls in tests | Agent empty/file/directory/FIFO/spawn domains are exact and loud. |
| 7 lossy decodes | 1 | Unchanged anchored diagnostic path; no new decision decode. |
| 8 broad catches | 0 broad AST handlers in tests | Empty class. |
| 9 waits/polls | 31 `while`; 48 `time.sleep` | Relevant reads are bounded; raw hang is proved standalone, not admitted to pytest. |
| 10 skips | 8 `pytest.skip` | `/dev/full` has a PC-venue declaration whose body at `test:932-934` contains both `_DEV_FULL` and `os.path.exists`; no new skip. |
| 11 world process sweeps | 1 registry-driven test | Corrected AF-AP-59 mutants 3/3 killed; own-pid `/proc` and `pgrep -P` paths remain allowed. |
| 12 signal installs | 7 textual mentions | Row 12.1 CLOSED by `test:3005` `assert sig_args and getattr(sig_args[0], "attr", "") == "SIGTERM"`; the SIGUSR1 mutant dies on this focused pin. |
| 13 `/proc/<pid>/exe` races | 1 test-side textual read plus 2 tee screen hits | Row is fail-loud and impossible-PID guard mutant dies deterministically. |
| 14 mirrors | 18 `PINNED_SHUTDOWN_CLAUSE` references | Rows 14.1/14.2 CLOSED: exact sentence + both-file proximity, and both halves bound to source-derived facts. |
| 15 cross-population counters | 0 `assert len(...) == len(...)` forms | Empty class for this delta; the 20-trial assertion is `any(won)`, not a tautological partition sum. |
| 16 redundant guards | examined focused gate guards | Nearby stale source comment corrected; no redundant new guard identified. |
| 17 hardlink-clobbering writes | 82 broad write-shaped AST calls, all existing test-fixture writes | No scoped production/test artifact write added by B5j. |
| 18 other families | 1 AST `os.kill`/`killpg`, 0 `assert True` | Kill is only in `_kill_own_grandchild`; pipe walker has documented process-alias/trusted-helper limits. |

## AP screen, lint, and process census

```
TEST_SCREEN: 1 hit
AP-66 x1: `timer.daemon = True` is at line 1058 of the final test file.

AP_SCREEN: 13 hits
AP-24 4; AP-1 3; AF-AP-55 2; AP-51 2; AF-AP-58 1; AP-32 1

pyflakes_rc=0
PROCESS-CENSUS lane_infrastructure=2 spawned_test_offenders=0
```

The AP hits are expected existing surfaces tested by this file: bounded daemon drain, explicit environment contract, fail-loud `/proc` handling, relay identity prose, SIGTERM install, and hashing. No AF-AP-59 hit exists in the final test bytes.

Final report-reference lint, run after the last report edit:

```
report_lint: 28 refs — OK 28, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
report_lint_rc=0
```

## Red-green status

- GREEN was run on the final candidate twice in the complete static-copy gate.
- RED was run on every one of the 12 B5j-required mutants, each followed from the same final base and each killed for its intended reason.
- Corrected negative controls for the malformed broad-harness rows were also run.
- The inherited implementation's original red-before runs are documented by VERIFY-B5i. This lane did not rerun a full `75998e7` suite because its independent red evidence already exists and the brief requires final-byte mutant re-runs, which were performed.

## Discrepancies and deviations

1. The inherited 51-mutant runner was not trustworthy as an oracle; seven rows were malformed. I preserved its aggregate as data, explained each flaw, and ran corrected negatives rather than fabricating `51/51`.
2. The incremental-draft rule requested append-only writes. During attempt 2, one earlier command replaced a stale identity line with an explicit `SUPERSEDED` line before later sections were appended. No completed section was deleted; this is a procedural deviation.
3. The brief names `/root/venv-agent-factory/bin/python` and sandbox paths, while the venue map for this PC lane supplies `/home/rocco/venv-agent-factory/bin/python`, `S0_01_VENUE=pc`, and `/home/rocco/s0-01-pinned/realleg/golden`. The PC mapping was used.
4. The broad source comment above the constant contradicted the new five reference-site rule. I corrected only that nearby comment, then reran the full two-copy gate and all 12 required mutants.

## Self-attack

1. The sentence oracle could still be a three-site mirror. Ruled out for the named class by deriving `SIGKILL`, `killpg`, `child`, `wait`, order, and seconds from hash-pinned Rust before checking the human halves. MIRROR-3SITE and MIRROR-3SITE-ORDER both die for those derived facts.
2. The pipe walker could miss a spelling. The four verifier evasions all die, and the walk requires at least 50 mentions. Residual limits remain explicit in the test: a process alias (`p = tee_proc`) and a falsely trusted helper name are outside its reach; this proposal does not claim otherwise.
3. Green could come from absent evidence or an unexercised race. The impossible-PID test deterministically enters the OSError branch; the 20-trial test requires one successful late sample; FIFO is created and asserted executable; both final full gates collect and pass 116 tests. The final process census found zero lane-spawned leftovers.

## Scope and handoff

No stash, checkout, restore, reset, add, commit, push, bridge call, service restart, or outward action was performed. Repository modifications for this lane are limited to:

- `proofs/S0-01/tools/frame_tee.py`
- `tests/test_s0_01_frame_tee.py`
- `tasks/briefs/s0-01-b5j-support/B5j-report.md`

Other staged/modified paths belong to sibling lanes and were not changed here. This report is a proposal for the sandbox-side adversarial verifier, not acceptance.
