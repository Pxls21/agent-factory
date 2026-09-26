# VERIFY-SCRUB2-R1: attack the scrubber repair before it lands (task #321)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/VERIFY-SCRUB2-R1-report.md`
(write it incrementally). If the harness refuses a report-file write ("Subagents should return findings as text"), return the
rest of the report as the text of your final message; never work around the refusal.

PIN: the shared tree's HEAD, whose scrubber files equal origin eb48880's (unchanged since cdbc1b8). The change under test:
`tasks/briefs/system1/SCRUB2-R1.patch` (five diffs; the premise gives its sha256). Contract: `tasks/briefs/system1/SCRUB2-R1-brief.md`
(items 1-5, which keep `tasks/briefs/system1/SCRUB2-brief.md` items 1-8 true). Builder's report:
`tasks/briefs/system1/SCRUB2-R1-report.md`; read its D1 (a reversed conclusion) and D16 first. Its claims are hypotheses. The
findings it repairs: `tasks/briefs/system1/VERIFY-SCRUB2-report.md` sections 14 and 15; their reproduction scripts are in
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2/`.

## WHY

`scripts/transcript_export.py` scrubs every transcript the push syncs and every session export; a rule that hides LESS than
before leaks a secret into the repository at the next push, and a rule that runs in super-linear time stalls every push on one
long line (AF-AP-152). The builder's differential found its own first design losing redactions (1,042 of 5,000 texts) and
replaced it. Nobody has attacked the final design.

## WHAT TO ATTACK (report every observation; no severity filter)

1. **Lost redactions.** Any text where the new rules hide less than SCRUB2's (the PIN's) rules: new shapes beyond the builder's
   differential (JSON escapes of every kind before and inside a value, `\uXXXX` in the name, mixed case, whitespace and tab
   variants, nested quoting, a value split across an escaped newline, URL-encoded forms, YAML and shell here-docs). Each one
   through `export()` and `convert()`, as the contract says.
2. **F1, F15 and F2 as the contract words them**: every F1 context redacts; F15's shapes stop over-redacting; `Authorization:
   Negotiate <token>` redacts the token.
3. **F7 and the time class.** The lenient private-key rule and the Cookie rule in linear time: adversarial inputs (many BEGIN
   heads, long dash runs, alternations built to backtrack), each measured at several doublings. Check every other rule for the
   class too; the builder names three it left (P00, P04, `_ASSIGN_LINE`, its D7, task #333): confirm or correct its numbers.
4. **The cost** (contract item 3): each changed rule's ordinary-text cost; the builder's D14 names 10 newly hidden regions.
5. **Everything else stays true** (contract item 5): the measurement rows, the value gate, test isolation (no committed test
   opens a real source), and the Laya lock (the builder's pre-fit comparison).
6. **Mutation:** reproduce at least five of the builder's mutants as FAILED tests; check its three equivalent survivors (W6,
   W11, W28); add a mutant for each contract clause its set does not cover.

## GATE

Apply the blocking predicate of skill `contract-gate`. One recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS /
NOT-READY / CONTRACT-INVALID, each blocking finding with its reproduction command.

## BOUNDARY

READ everything. WRITE only your report and scratch under `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r1/`. Apply the patch only in a scratch copy: a
`git archive HEAD` of the directories the tests need (`scripts/`, `tests/`, `docs/research/findings/laya-ft-labels/`, plus
what their imports read), never a full worktree (the disk is tight) and never the shared tree.

## STANDING RULES

- No git writes, no PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables. Anything that could reach one
  runs through the masking runner `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/masked.sh`. The exporter's default sources are never exercised.
- Two other verifiers run beside you (VERIFY-I59-BCE and VERIFY-I59-LANDING, on another commit, under `/tmp/vbce-*` and
  `/tmp/vland-*`): never touch those.
- The disk is shared (about 1.3 GB free, three verifiers): scratch under 200 MB, deleted as you go; a short `--basetemp`;
  never run the whole `tests/test_vendored_manifest.py`.
- Test counts are pasted from `scripts/test_summary.sh`. Stamps are substituted from `date -u`, never typed.
- Long commands in one foreground call, each under 10 minutes; kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text of
  its own (under 200 characters; a note only for a 0).

## PREMISE — MEASURED at authoring (2026-09-26 10:5xZ, the sandbox tree, clean; HEAD's scrubber files = origin eb48880's)

```
$ git log --oneline cdbc1b8..HEAD -- scripts/transcript_export.py scripts/session_export.py scripts/known_values_check.py | wc -l
0
$ sha256sum tasks/briefs/system1/SCRUB2-R1.patch | cut -c1-16; grep -c "^diff --git" <it>
e72a85cca2a3382d
5
$ the patch applied to HEAD in a scratch copy: sha256 of the results (the coordinator, this session, before the patch was saved)
transcript_export.py 014439fb2694d273; session_export.py 0462fe2e9bdd14bc; test_transcript_export.py 00e7e9f80aedf16f; test_session_export.py c1bb29a1ec924a71; 2026-09-25-recorded/dataset-manifest.json 449811004a7abed8
$ bash scripts/test_summary.sh <the 12 files of the SCRUB2-R1 brief>   (with the patch applied in the tree, before it was held)
pytest-exit: 0
pytest-summary: 841 passed in 131.58s (0:02:11)
$ bash scripts/pc_suite.sh set-id -- <the same 12 files>
12 files set=27f27a25516b
$ df -Pm / | awk ...
1313 MB free
```
