# VERIFY-SCRUB2-R1-R2: attack the scrubber repair's round 2 before it lands (task #321)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/VERIFY-SCRUB2-R1-R2-report.md`
(write it incrementally). If the harness refuses a report-file write, return the WHOLE report as your final message and
as your hand-back message (not a summary); never work around the refusal.

Authored 2026-09-28 18:4xZ by the coordinator.

The change under test: the SCRUB2-R1 lane's working-tree files in the main tree `/home/user/agent-factory` (uncommitted;
sha256 prefixes in the premise): `scripts/transcript_export.py`, `tests/test_transcript_export.py`, and the recorded
dataset manifest's code hash. `scripts/session_export.py` and `tests/test_session_export.py` are unchanged from round 1.
Contracts: `tasks/briefs/system1/SCRUB2-R1-R2-brief.md` (round 2, items 1-7), which keeps
`tasks/briefs/system1/SCRUB2-R1-brief.md` (round 1) and `tasks/briefs/system1/SCRUB2-brief.md` true. The findings it
repairs: `tasks/briefs/system1/VERIFY-SCRUB2-R1-report.md` (B1 to B3, V4, V5, V21). The builder's report:
`tasks/briefs/system1/SCRUB2-R1-R2-report.md`; read its D1, D2, D6 and D7 first. Its claims are hypotheses.

Why it matters: `scripts/transcript_export.py` scrubs every transcript the push syncs and every session export. A rule
that hides LESS than before leaks a secret into the repository at the next push; a rule that runs in super-linear time
stalls every push on one long line (AF-AP-152).

The coordinator's ruling on the builder's D6 (2026-09-28): the 11 header names that now show (`credentials=`,
`Authorization:`, `credentials:`) are names, not values; V4 holds if each VALUE after them stays hidden by its own rule
or was shown by the PIN too. Your item 3 checks exactly that.

## WHAT TO ATTACK (report every observation; no severity filter)

1. B1: linear time. Every rule changed in either round, on backslash runs, dash runs, space runs, quote runs and runs
   built to make a lookahead or an alternation re-scan (the class), each at several doublings up to at least 64,000
   characters. The builder's D7: are the constants that grew 2 to 6.6 times still harmless on the real corpus?
2. B2 and B3: a Cookie value after an escaped `\n`, `\r` or `\t` in canonical JSON, pasted JSON and decoded text;
   Negotiate never takes the next line's word, in `scrub`, `scrub_payload`, the digest and `convert()`.
3. V4 and D6: any text where round 2 hides LESS than the PIN (SCRUB2's committed rules), in any view (canonical JSON,
   the decoded digest, `convert()`'s events). Beyond the builder's shapes and its `lost_shapes.py` and
   `rand_lost2.py`: literal escapes of every kind before and inside a value, mixed case, whitespace and tab variants,
   nested quoting, a value split across an escaped newline, URL-encoded forms, YAML and shell here-docs. For D6, show
   for each of the 11 regions that the value after the name is hidden or was shown by the PIN too.
4. D2: the scheme rule's fix (a new lost PIN redaction the builder found): does the fix hold, and does any sibling
   shape still read an escaped-quote head?
5. Item 7: everything round 1 made true stays true: F1, F15, F2, F7, F10, F12, the value gate, test isolation (no
   committed test opens a real source), the Laya lock (the pre-fit comparison, with item counts), item 6's measurement
   rows.
6. Mutation: reproduce at least six of the builder's mutants as FAILED tests (two of r2, M2', M22, one of r1, one of
   se); check its two equivalent survivors (W11, W28); add a mutant for each round-2 clause its set does not cover.

## GATE

Apply the blocking predicate of skill `contract-gate` and D-034 (a finding re-opens the build only if it is
CORE-BLOCKING; the rest become follow-ups). One recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY /
CONTRACT-INVALID, each blocking finding with its reproduction command.

## BOUNDARY

READ everything. WRITE only your report and scratch under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r2/`. Apply the lane's files only in a
scratch copy: a `git archive HEAD` of the directories the tests need (`scripts/`, `tests/`,
`docs/research/findings/laya-ft-labels/`, plus what their imports read) with the lane's files copied on top; never a full
worktree (the disk is tight) and never the shared tree. The previous verifier's probes in `.../scratchpad/vscrub2r1/probes/`
are yours to read and run in your copy.

## STANDING RULES

- No git writes, no PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables. Anything that could reach one
  runs through the masking runner `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/masked.sh`.
  The exporter's default sources are never exercised. Test secrets are FAKE strings built at run time.
- Other lanes hold files in the main tree (`.lanes-live` lists them); touch none.
- The disk is shared (see the premise): scratch under 200 MB, deleted as you go; a private `--basetemp` outside any work
  tree for every pytest run; never run the whole `tests/test_vendored_manifest.py`.
- Test counts are pasted from `scripts/test_summary.sh` with their set ids. Stamps are substituted from `date -u`, never
  typed.
- Long commands in one foreground call, each under 10 minutes; kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.

## PREMISE — MEASURED at authoring (2026-09-28 18:4xZ, the main tree; `bash scripts/premise_block.sh`)

```
$ git rev-parse --short HEAD
54877b9
$ git status --porcelain -- scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
 M docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
 M scripts/session_export.py
 M scripts/transcript_export.py
 M tests/test_session_export.py
 M tests/test_transcript_export.py
$ sha256sum scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json tasks/briefs/system1/SCRUB2-R1-R2-report.md | cut -c1-16,65-
e36f708b5515cd36  scripts/transcript_export.py
0462fe2e9bdd14bc  scripts/session_export.py
c917c5ccaf08074a  tests/test_transcript_export.py
c1bb29a1ec924a71  tests/test_session_export.py
8d5427fdac6ee5f8  docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
9f8458c240020749  tasks/briefs/system1/SCRUB2-R1-R2-report.md
$ git diff --stat -- scripts/transcript_export.py tests/test_transcript_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
 .../2026-09-25-recorded/dataset-manifest.json      |   2 +-
 scripts/transcript_export.py                       | 121 +++++-
 tests/test_transcript_export.py                    | 454 +++++++++++++++++++++
 3 files changed, 562 insertions(+), 15 deletions(-)
$ git log --oneline cdbc1b8..HEAD -- scripts/transcript_export.py scripts/session_export.py | wc -l
0
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r1/probes/ | head -12
after_v.py
bs_timing.py
census.py
cost_shapes.py
e2e_bs.py
e2e_neg.py
e2e_yaml.py
equiv.py
exposure_bs.py
laya_lock.py
lost_shapes.py
mutate_f12.py
$ ls -la /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/masked.sh
-rwxr-xr-x 1 root root 3175 Sep 25 22:17 /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/masked.sh
$ df -m / | tail -1
/dev/vda          258020 36639      1300  97% /
```

Coordinator note (19:1xZ): the `git rev-parse` line above read the local id before `push_clean.sh` rewrote the unpushed range (trailers only, the same tree); it shows the commit's id on origin, 54877b9, the D-105 commit (stale_ids).

The builder's floor, quoted from its report (your item 5 re-runs it): `12 files set=27f27a25516b`: `855 passed` twice.
