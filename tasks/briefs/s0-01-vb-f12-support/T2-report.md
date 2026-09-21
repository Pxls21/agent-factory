# T2 report — pin the committed S0-01 bundle's behaviour through the REAL proof-runner

PIN: 38ad46b · lane: pc-vb-f12-t2.md · role: code-implementer (local Qwen build route) · venue: PC (VENUE-MAP).
Report path: `tasks/briefs/s0-01-vb-f12-support/T2-report.md` (created this lane; the dir did not exist at the PIN).
Report aliases used by report_lint: `test`=tests/test_s0_01_spec_runner.py · `prun`=scripts/proof-runner ·
`spec`=proofs/S0-01/spec.json · `init`=proofs/S0-01/check_initialize.py · `conf`=proofs/S0-01/check_acp_conformance.py.

## FILE IDENTITY

- `tests/test_s0_01_spec_runner.py` (the ONLY file changed): 783 lines, sha256 `5ebae9911cd0c94e54953e110078a2462794b7ce779bbeb4b2f30cf4a4ec9f3b`.
  - diff vs PIN: 65 insertions, 3 deletions (the docstring preamble rewrite + two new tests).
  - docstring preamble: `test:1-17` (opens `test:1` with `S0-01` through the CANONICAL proof-runner).
  - must-update clause: `test:16` names the `AF-AP-107` round that must update these two tests when it lands.
  - kept V3 paragraph: `test:19-26` (`scripts/proof-runner` on `test:19`) — the per-line-substring paragraph is unchanged from the PIN.
  - item-2 test: `test:107` `test_committed_bundle_runner_reports_leg_exit_mismatch_not_a_result`; the stderr-equality assert is `test:126-127` (`leg-exit-mismatch: S0-01 positive expected 0 got 1` on `test:127`); the `r.stdout`-empty assert is `test:129`; the result.json-absent assert is `test:130` (`result.json`).
  - item-3 test: `test:133` `test_committed_negative_leg_cmd_reports_the_protocol_violation`; the two-line-equality assert is `test:149-151` (`protocol-violation: missing required initialize field` on `test:150`).
- `git status --porcelain` after finishing: ` M tests/test_s0_01_spec_runner.py` + `?? tasks/briefs/s0-01-vb-f12-support/` (this report). `proofs/`, `scripts/`, and every other test file are byte-identical to the PIN.
- `scripts/report_lint.py` in this tree is the dispatcher's CURRENT overlaid copy (not the PIN's) — a tool, not a deliverable; it is never listed in FILE IDENTITY.

## 1. Measured-vs-observed table (the four runner/negative lines)

Measured on a FRESH copy of the PIN (`cp -a <tree>/proofs` + `cp -a <tree>/scripts` into a scratch dir, cwd=that copy),
gate env `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz` exported,
venv `/home/rocco/venv-agent-factory/bin` first on PATH.

| # | command (as in the brief) | MEASURED (this session) | OBSERVED (brief's claim) | verdict |
|---|---|---|---|---|
| 1 | runner `--proof S0-01 --venue sandbox --root .` | rc=1 · stdout 0 bytes · stderr `[leg-exit-mismatch: S0-01 positive expected 0 got 1]` · result.json ABSENT · wall 3.86 s | rc 1 · empty stdout · that exact stderr · no result.json | MATCH (exact) |
| 2 | negative leg cmd, argv[1:] | rc=1 · line1 `[protocol-violation: missing required initialize field]` · line2 `[observed: error code=-32602 message=Invalid params]` · wall 0.09 s | rc 1 · those two exact lines | MATCH (exact) |

All four lines match the brief byte-for-byte. No discrepancy. The runner's mismatch string is built at `prun:189-190`
(`leg-exit-mismatch` on `prun:189`, `expected {expected_exit} got {run['exit_code']}` on `prun:190`); the exit-2 defer — the only
defer path — is the `raise Deferred` at `prun:182`, so a 1-exit leg is a mismatch, never a defer.

## 2. Why the committed bundle exits 1 (the premise, traced)

- Positive leg = the conformance checker's golden walk: `conf:1533` `check_golden` (the frozen `golden.jsonl` sha256
  compare). Its AF-AP-107 failure — the pinned hermes-acp emits `session_info_update` asynchronously (an OPEN owner
  decision, docs/INCIDENT-LOG.md 2026-09-21) — makes the positive leg exit 1, which the runner reports as the mismatch in §1.
- Negative leg = `spec:15` (`request` against `proofs/S0-01/evidence/golden/negative`); `init:97` `_check_request_directory`
  validates the capture, then prints the classification at `init:120` (`print(verdict)`, line 1) and the observed error at
  `init:121` (`print(observed)`, line 2), then `return 1`. The `spec:20` expected `failure_reason` is the exact text of line 1.

## 3. De-vacuous record (item 4) — red lines + green reruns, both pasted

Each expected string was changed by ONE character, the single test run, the failing assertion line pasted, the string
restored, then the full suite re-run green (§4). Red lines (verbatim, `--tb=short`):

- item-2 (mutated `got 1` → `got 2`):
  `E   AssertionError: assert 'leg-exit-mis...ected 0 got 1' == 'leg-exit-mis...ected 0 got 2'`
  `E     - ted 0 got 2` / `E     + ted 0 got 1`
  → `FAILED …::test_committed_bundle_runner_reports_leg_exit_mismatch_not_a_result` · `1 failed in 3.77s`
  (assert at `test:126` — the stderr-equality assert, the mutated string's own line).
- item-3 (mutated `params` → `parama`):
  `E   AssertionError: assert ['protocol-vi...valid params'] == ['protocol-vi...valid parama']`
  `E     At index 1 diff: 'observed: error code=-32602 message=Invalid params' != 'observed: error code=-32602 message=Invalid parama'`
  → `FAILED …::test_committed_negative_leg_cmd_reports_the_protocol_violation` · `1 failed in 0.31s`
  (assert at `test:149` — the two-line-equality assert, the mutated string's own line).

Both mutants died at the EXPECTED assert for the exact expected reason (a character mismatch in the pinned string), not at
the rc or an upstream assert — so both tests pin the real stdout/stderr bytes, not just the exit code. Strings restored; both green.

## 4. Gate (every line pasted verbatim; each call < the 420 s cap)

Env: `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`;
venv first on PATH; `mkdir -p ../scratch/bt`.

- pytest RUN 1 (final bytes): `15 passed in 7.46s` · rc=0
- pytest RUN 2 (final bytes): `15 passed in 7.59s` · rc=0
  (the two summary lines agree: 15 passed — the brief's expected shape `15 passed in Ns`. 13 pre-existing + 2 new, nothing skipped/xfail.)
- `python -m pyflakes tests/test_s0_01_spec_runner.py` → rc=0 (no output = clean)
- `python3 scripts/ap_screen.py tests/test_s0_01_spec_runner.py` → last line: `--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---` · rc=0
- `sha256sum tests/test_s0_01_spec_runner.py` → `5ebae9911cd0c94e54953e110078a2462794b7ce779bbeb4b2f30cf4a4ec9f3b  tests/test_s0_01_spec_runner.py`

## 5. report_lint (run LAST, bounded rule — pasted)

- `prun:72` `_clean_env` reduces each leg's environment to `prun:18` `PASSTHROUGH_ENV` (`PATH`, `HOME`, `LANG`), and the
  venue is stamped only into `prun:216` `env_fingerprint` — so `--venue` is metadata and never reaches the legs.
  (This is the DISCREPANCIES mechanism note below, not a premise conflict: the brief's measured lines reproduced exactly,
  so the behaviour is venue-independent by construction.)
- Linter run (final round, after the alias fix + the `test:39` token fix):
  `python3 scripts/report_lint.py tasks/briefs/s0-01-vb-f12-support/T2-report.md --root <tree> --map test=tests/test_s0_01_spec_runner.py --map prun=scripts/proof-runner --map spec=proofs/S0-01/spec.json --map init=proofs/S0-01/check_initialize.py --map conf=proofs/S0-01/check_acp_conformance.py --min-refs 8`
  → summary line (pasted verbatim as plain text — the digits are not backticked, so the linter's ref-scanner does not
    re-match them against the summary and the line is self-consistent):
    report_lint: 37 refs — OK 29, NEAR 0, MISS 0, UNCHECKABLE 8, UNRESOLVED 0 (worktree)   rc=0
  (The 8 UNCHECKABLE are refs on statement-only lines — the ref is recorded but the line carries no claim token to check
   against; they are not defects. Round 1 was a mis-aliased invocation (see DISCREPANCIES); round 2 found one
   miss on the `_copy` ref (test line 39) which I fixed per the hint; this is the clean final run.)

## DISCREPANCIES

- **Alias collision in my round-1 linter run (my bug, not the tree's).** My first report draft used `runner` to mean the
  test file AND (in §1/§2) the proof-runner script. `--map runner=tests/test_s0_01_spec_runner.py` lets `runner` mean only
  one file, so `runner:182/189/190` resolved against the TEST file and produced spurious MISS rows (`cited line reads:
  'spec_schema = json.loads(...)'` = line 182 of the test file, not the runner). The tree is correct: I re-verified with
  absolute paths that `scripts/proof-runner` line 182 = `raise Deferred(` and 189-190 = the mismatch string. Fixed by giving
  the runner its own alias `prun` and re-running.
- **`--venue` is metadata only (mechanism note).** `prun:72` `_clean_env` + `prun:18` `PASSTHROUGH_ENV` = the legs only see
  PATH/HOME/LANG; the exported `S0_01_VENUE`/`S0_01_REAL_LEG_DIR` do not reach the leg processes. So the committed bundle
  fails identically on `--venue sandbox` and `--venue pc-bridge` — the `--venue sandbox` invocation in the brief is a
  reproduction detail, not a venue-dependent result. The pinned lines are unchanged by this.
- **Persistent-cwd trap (tool quirk, logged per the standing do-not).** The `terminal` tool persists the working
  directory between calls; an earlier `cd ../scratch` made a few grep/awk calls read the scratch copy rather than the
  tree. All line-number claims in this report were re-derived from the tree with ABSOLUTE paths after that. No
  measurement changed. (anti-pattern class: **stale-sink** — a stateful tool makes a later read hit the wrong copy of a
  file; guard: pin the root by absolute path, not a relative one, in any call that reads source for a cited line.)
- **report_lint final summary (pasted, plain text):** report_lint: 37 refs — OK 29, NEAR 0, MISS 0, UNCHECKABLE 8, UNRESOLVED 0 (worktree)   rc=0.
  (Quoted without backticks in both places so the linter does not re-match the summary's own digits as new refs —
  backticking them created a self-referential count loop.) Bounded-rule history: round 1 = my mis-aliased invocation
  (the `runner` collision described above — spurious MISS rows); round 2 = one miss on the `_copy` ref (test line 39) —
  fixed by the `fix:` hint (added the backticked `def _copy(tmp_path)` copied from the cited line, then removed the
  now-redundant second `test:39` ref whose only claim token was a section name); final round = the clean run above.
  No residual MISS; the FLOOR (≥8 OK) is met 29-fold.

## NOT-done (first-class)

- NOT minted: the runner over the committed bundle produces NO result.json (it reports the leg exit mismatch) — this IS
  the pinned behaviour, not a failure of this lane. The proof stays NOT minted until the AF-AP-107 golden decision lands
  and that round updates the two committed tests.
- NOT deferred: the committed bundle does NOT take the exit-2 deferral path (the positive leg exits 1, a real check
  failure, not capability-unavailable). The deferral path is only exercised on the controlled (stripped) copy by the
  three pre-existing deferral tests.
- No git write by this lane (no add/commit/push/stash) — the coordinator harvests the worktree. The one modified file is
  in the worktree; the report dir is untracked.
- `detect-changes` NOT run against the clone's GitNexus index: the lane tree is not in that index (the available-repos
  list omits this lane), and no SOURCE symbol changed (a test file only). A lane never commits, so the
  detect-changes-at-commit duty is the coordinator's at harvest.

## Self-attack (three most likely ways this change is wrong, and how each was ruled out)

1. **The pinned lines drift when the golden is re-captured.** → They are copied VERBATIM from a live run on THIS tree at
   the PIN (§1 table; §3 red lines prove the assert is the exact-line equality). When AF-AP-107 lands, the docstring
   (`test:16`) and both test docstrings (`test:112`, `test:138`) all say "must be updated when the AF-AP-107 golden
   decision lands" — that round owns the re-measure, not this one.
2. **`_copy` vs the stripped copy: I pinned the wrong tree shape.** → Items 2/3 use `root = _copy(tmp_path)` UNSTRIPPED
   (`test:39` `def _copy(tmp_path)`), exactly as the brief mandates (contrasted with the deferral tests' `_strip_v2_evidence` at `test:47`).
   Verified the unstripped copy retains `negative/timeline.jsonl` and all five leg dirs, so the negative leg runs the real
   classification (not the "not captured" defer) and the positive leg runs the real golden walk.
3. **The test is a mirror, not a gate (a tautology).** → Ruled out by the de-vacuous mutations (§3): a one-char change to
   each expected string made that test fail at its own assert for the exact reason, then green after restore. The tests
   invoke the REAL runner and REAL checker (not a re-implementation), so they gate the committed behaviour end-to-end.

## GATE RECOMMENDATION

MERGE-READY — exactly one file changed; all mechanical gates green (pytest×2 agree at 15, pyflakes rc 0, ap_screen 0 hits,
sha256 recorded, report_lint at its floor: 37 refs / 0 MISS, pasted as plain text above). The two new tests are
de-vacuous'd and pin the committed tree's real non-minting, non-deferring behaviour through the real proof-runner. This is a
PROPOSAL for the sandbox-side adversarial-verifier lane to grade — a build lane does not self-accept a gate verdict.

## RETRO (for the coordinator's /bug-echo + ANTI-PATTERN REGISTRY)

Two novel wrinkles worth a registry row (named with their class; the numbers are the coordinator's to assign):
1. **stale-sink** — a tool that persists working-directory state makes a later relative-path read hit the wrong copy of a
   file (I read the scratch copy's scripts/proof-runner instead of the tree's). Guard: absolute-path roots in any call that
   reads source for a cited line. (Report line: "Persistent-cwd trap" in DISCREPANCIES.)
2. **self-referential measure** — quoting a numeric tool output inside a document that a ref-scanner then scans makes the
   measure change the measured (backticking report_lint's summary turned its digits into new refs, so each re-run gave
   different counts). Guard: paste a linter's numeric summary as PLAIN text, never in a token-matched span.
No repo-code defect was found or fixed this lane — the one changed file is the test file, and its two new tests are the
deliverable; the "bugs" above are process/tooling, not source.
