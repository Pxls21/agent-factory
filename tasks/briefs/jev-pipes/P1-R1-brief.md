# P1-R1: the one focused repair of the P1 replay instrument (task #267; D-031; VERIFY-P1 F-PERSIST and G-PASS)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/jev-pipes/P1-R1-report.md` (write it
incrementally from the start). This is the ONLY repair round the instrument gets (D-031; key: task #231, seed `seed_5aa221965993`
v1.0.0, production digest `replay_pruner.py` f10df15241c34828). PIN: e8c14bf (origin; the boundary files are unchanged since, measured).

## WHY

The P1 verdict (FAIL: nothing pruned) stands; the verifier reproduced it. But this harness will grade the next scorer and the
redesigned pipeline (the coordinator's ruling), and on a PASS path it overcounts: for a persisted Bash output it counts what the
pruner dropped from the persisted FILE, while the model saw only the stub (x2.4 on the verifier's fixture). Six of the verifier's ten
mutants of the accounting survive the lane's 34 tests, because no committed test drives a pruned row end to end.

## CONTRACT

`seeds/seed-jev-pipes-p1-v1.yaml` (the accounting in its acceptance criteria) and `tasks/briefs/jev-pipes/P1-brief.md`, unchanged.
The verifier's report `tasks/briefs/jev-pipes/VERIFY-P1-report.md` is the spec of the defect: section 4 (F-PERSIST and the PASS-path
oracle), section 8 (the mutation table M1-M10), section 9 (G-PASS, F-SCOPE, N-3).

## THE REPAIR

- **R-1 (F-PERSIST).** For a persisted result, the saving, the miss baseline and the keep-rate denominator count what the MODEL saw
  (the stub, `cand.chars`), never the file: `scripts/jev_pipes/replay_pruner.py:165` (`chars_saved`), and the same shape at the miss
  baseline and at the keep-rate denominator (the verifier names `:186` and `:220`; confirm each on the PIN's bytes and say if a site
  is not that shape). A non-persisted result is unchanged.
- **R-2 (G-PASS).** A committed end-to-end test with pruned rows, through the harness's one command and a LOOPBACK fake scorer that
  drops only planted noise chunks, with an oracle computed from the fixture's own event list (never from the harness): the verifier's
  variants v0, v1, v2, v1neg and persisted (section 4; its scratch probe `.../scratchpad/verify-p1/probe/pass_path.py` is the
  starting point, and `probe/mutate.py` its mutation driver). The suite must kill M1-M10 (section 8), each red on a named test.
- **R-3 (wording).** The findings report says "this session" where the verdict set is the main transcript only (F-SCOPE: the
  subagent transcripts hold 5,774 more Bash results of 2,000+ characters, not replayed), and the "partly visible" request (N-3):
  correct both sentences in `docs/research/findings/jev-pipes/P1-replay-2026-09-25.md`; no number changes (the verdict set had no
  pruned row, so F-PERSIST moves no committed figure: say so, measured).

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Red first: the new tests fail on the PIN's `replay_pruner.py` for the persisted variant and pass on yours (paste both).
3. The mutation table rerun: M1-M10 each red on a named test in the committed suite (paste the driver's summary line).
4. `bash scripts/test_summary.sh tests/test_jev_pipes_replay.py` twice, with the set id; pyflakes rc 0; the separator check 0 on every
   file you write.
5. The committed FAIL unchanged: re-run the harness's summary over the committed decision logs, or show from the logs that no
   verdict-set row was pruned, so the headline numbers do not move.
6. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `scripts/jev_pipes/replay_pruner.py`, `tests/test_jev_pipes_replay.py`, `tests/fixtures/jev_pipes/make_fixture.py` (only if the
fixture builder needs a persisted-result shape), `docs/research/findings/jev-pipes/P1-replay-2026-09-25.md` (the two sentences only).
CREATE: new fixture files under `tests/fixtures/jev_pipes/`, your report. READ everything else. Not `vendor/jev-pruner/`, not
`scripts/jev_pipes/bridge.mjs` or `accounting.py` unless a site of R-1 lies there (then STOP and report it first). Scratch:
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/p1-r1/`.

## STANDING RULES

No network beyond loopback test servers; the live Laya server (127.0.0.1:47411) is not used at all; no PC bridge; no git writes; no
outward-facing action. Never read a real secret file (`.pc-bridge.env`, `/root/.codiv/api.env`, any `*.env`, any key file). Fixtures are
synthetic; no session text enters a committed file. Another lane is live in this tree on other files: touch nothing outside your
boundary.

## PREMISE — MEASURED at authoring (2026-09-25 09:1xZ, the sandbox)

```
$ git show e8c14bf:<file> | sha256sum | cut -c1-16         (0 diff lines at the local head for scripts/jev_pipes/, the test, the fixtures)
f10df15241c34828  scripts/jev_pipes/replay_pruner.py
28b097e1ad7f67f6  tests/test_jev_pipes_replay.py
$ sed -n '165p' scripts/jev_pipes/replay_pruner.py
    chars_saved = result["charsBefore"] - result["charsAfter"] if pruned else 0
$ bash scripts/test_summary.sh tests/test_jev_pipes_replay.py
pytest-summary: 34 passed in 13.40s
$ bash scripts/pc_suite.sh set-id -- tests/test_jev_pipes_replay.py
1 files set=17f6a5adc0c9
$ (VERIFY-P1 section 4, the persisted variant)
persisted | PASS; 21; 0; 0.0; 49,955.4; 0; 49,955.4 | oracle 43,223.9 | toolu_pp_px chars_saved 3083 vs 1261
$ (VERIFY-P1 section 8)
Six of ten survive the lane's suite (M1, M2, M3, M5, M9, M10)
```
