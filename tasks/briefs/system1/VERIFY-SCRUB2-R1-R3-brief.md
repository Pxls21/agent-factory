# VERIFY-SCRUB2-R1-R3: attack the scrubber repair's round 3 before it lands (task #321)

Role: adversarial-verifier, the round-2 verifier resumed (sandbox, Opus 5.5). Do NOT spawn subagents. Report:
`tasks/briefs/system1/VERIFY-SCRUB2-R1-R3-report.md` (write it incrementally). If the harness refuses a report-file
write, return the WHOLE report as your final message and as your hand-back message (not a summary); never work around
the refusal.

Authored 2026-09-28 by the coordinator.

The change under test: the SCRUB2-R1 lane's working-tree files in the main tree `/home/user/agent-factory`
(uncommitted; sha256 prefixes in the premise): `scripts/transcript_export.py`, `tests/test_transcript_export.py`, and
the recorded dataset manifest's code hash. `scripts/session_export.py` and `tests/test_session_export.py` are unchanged
from round 2. Contract: `tasks/briefs/system1/SCRUB2-R1-R3-brief.md` (round 3), which keeps rounds 1 and 2 true. The
findings it repairs are yours: `tasks/briefs/system1/VERIFY-SCRUB2-R1-R2-report.md` (N1, N2, F-MUT, F-DOC). The
builder's report: `tasks/briefs/system1/SCRUB2-R1-R3-report.md`; read its DISCREPANCIES (R3-D1 to R3-D11) first. Its
claims are hypotheses.

Why it matters: this file scrubs every transcript the push syncs and every session export. A rule that hides LESS than
the PIN (SCRUB2's committed rules) leaks a secret into the repository at the next push; a super-linear rule stalls every
push on one long line (AF-AP-152).

## WHAT TO ATTACK (report every observation; no severity filter)

1. N1 and N2: your own red file (`tasks/briefs/system1/vscrub2r2/vscrub2r1r2_red.py`) on the final bytes, then new
   shapes of both classes beyond the builder's: Cookie head forms (case, `Set-Cookie`, spaces before the colon, escapes
   and quotes after it), pwd and credentials heads in every view (canonical JSON, pasted JSON, the decoded digest,
   `convert()`'s events).
2. V4 (no redaction the PIN makes may be lost in any view). The builder reports REAL 0 on generated text and on the
   corpus (its row A). Re-derive it with your own classifier. Judge R3-D1's 8 `OTHER|credentials` regions (the builder
   calls them K+NAME).
3. R3-D2: the new scheme-rule stop after an escaped quote (beyond your round-2 shape list). Does it hide less than the
   PIN anywhere? Does a plain head keep the PIN's whole token?
4. R3-D3: a Cookie head the PIN never read now searches its floor in its segment. Never less than the PIN; linear.
5. R3-D4: the stops show more names. For each newly shown name, the value after it is hidden or was shown by the PIN
   too; measure the residual (a value whose own tail spells a later head, such as `/pwd=`).
6. R3-D5: try to reproduce the one unexplained failure of `test_the_value_gate_reads_a_variable_and_a_raw_key_file` (four
   parallel pytest runs, as the builder's driver ran them).
7. B1, linear time: every rule changed in rounds 2 and 3, on your class of adversarial runs, each at several doublings
   up to at least 64,000 characters.
8. Everything earlier rounds made true stays true: F1, F15, F2, F7, F10, F12, B2, B3, D1, D2, D6 as ruled, the value
   gate, test isolation, the Laya lock (item counts), digest identity.
9. Mutation: reproduce at least six of the builder's y-group mutants as FAILED tests, and add a mutant for each round-3
   clause its set does not cover.

## GATE

Apply the blocking predicate of skill `contract-gate` and D-034 (a finding re-opens the build only if it is
CORE-BLOCKING; the rest become follow-ups). One recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY /
CONTRACT-INVALID, each blocking finding with its reproduction command.

## BOUNDARY

READ everything. WRITE only your report and scratch under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r3/`. Apply the lane's files only in a
scratch copy (a `git archive HEAD` of what the tests need, with the lane's files on top; never the shared tree). The
builder's instruments under `.../scratchpad/scrub2r3/` and yours under `.../scratchpad/vscrub2r2/` are yours to read and
run in your copy.

## STANDING RULES

- No git writes, no PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables. Anything that could reach one
  runs through the masking runner `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/masked.sh`.
  The exporter's default sources are never exercised. Test secrets are FAKE strings built at run time.
- Other lanes hold files in the main tree (`.lanes-live` lists them); touch none.
- The disk is shared: scratch under 200 MB, deleted as you go; a private `--basetemp` outside any work tree for every
  pytest run, passed as a pytest ARGUMENT (never through `PYTEST_ADDOPTS`, AF-AP-237); never run the whole
  `tests/test_vendored_manifest.py`.
- Test counts are pasted from `scripts/test_summary.sh` with their set ids. Stamps are substituted from `date -u`, never
  typed.
- Long commands in one foreground call, each under 10 minutes; kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Cite commits by subject or by an origin id; the coordinator's local ids change on the push.

## PREMISE — MEASURED at authoring (2026-09-28, main tree@0c11fd1)

Printed by `bash scripts/premise_block.sh` from the main tree at the PIN, origin 0c11fd1 (the pushed id). Expected to differ when you re-run it: nothing, unless HEAD moved (the first line checks the PIN is still an ancestor). The builder reports `320 passed` on the last line's set (`2 files set=e8f27bcb91e7`, run through `masked.sh absent` on a copy); that count was not re-run at authoring (the masking runner refuses the main tree, by design): re-measure it in your copy.

```
$ git merge-base --is-ancestor 0c11fd1 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git status --porcelain -- scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
 M docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
 M scripts/session_export.py
 M scripts/transcript_export.py
 M tests/test_session_export.py
 M tests/test_transcript_export.py
$ sha256sum scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json | cut -c1-16,65-
f6fe76b2b67d316a  scripts/transcript_export.py
0462fe2e9bdd14bc  scripts/session_export.py
39478c66e3ab96ed  tests/test_transcript_export.py
c1bb29a1ec924a71  tests/test_session_export.py
21658ac0d86de615  docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
$ sha256sum tasks/briefs/system1/SCRUB2-R1-R3-report.md tasks/briefs/system1/SCRUB2-R1-R3-brief.md tasks/briefs/system1/VERIFY-SCRUB2-R1-R2-report.md | cut -c1-16,65-
a999989ca57b20da  tasks/briefs/system1/SCRUB2-R1-R3-report.md
088b26ef39d2d904  tasks/briefs/system1/SCRUB2-R1-R3-brief.md
baff2425fb28cdff  tasks/briefs/system1/VERIFY-SCRUB2-R1-R2-report.md
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py tests/test_session_export.py | tail -1
2 files set=e8f27bcb91e7
```
