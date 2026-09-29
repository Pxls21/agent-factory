# VERIFY-SCRUB2-R1-R4: attack the scrubber repair's round 4 before it lands (task #321)

Role: adversarial-verifier, the round-3 verifier resumed (sandbox, Opus 5.5). Do NOT spawn subagents. Report:
`tasks/briefs/system1/VERIFY-SCRUB2-R1-R4-report.md` (write it incrementally). If the harness refuses a report-file
write, return the WHOLE report as your final message and as your hand-back message (not a summary); never work around
the refusal.

Authored 2026-09-29 by the coordinator.

The change under test: `tasks/briefs/system1/SCRUB2-R1-R4.patch` (rounds 3 and 4 together against PIN bef1e9e; 5 files:
`scripts/transcript_export.py`, `scripts/session_export.py`, `tests/test_transcript_export.py`,
`tests/test_session_export.py`, the recorded dataset manifest; sha256 in the premise). It is NOT applied in the main tree;
it applies at the brief's PIN (the premise checks it). Contract: `tasks/briefs/system1/SCRUB2-R1-R4-brief.md` (round 4,
the fourth round the owner authorized past D-031's budget, D-108 item 3), which keeps rounds 1 to 3 true. The findings it
repairs are yours: `tasks/briefs/system1/VERIFY-SCRUB2-R1-R3-report.md` (R3V-1 to R3V-11). The builder's report:
`tasks/briefs/system1/SCRUB2-R1-R4-report.md`; read its NOT-done list and DISC-1 to DISC-14 first. Its claims are
hypotheses.

Why it matters: this file scrubs every transcript the push syncs, every session export and, since task #373, every
string the scrubbing relay sends to codiv.ai (`scripts/jev_relay.py` runs `scrub_payload` and the value gate). A rule
that hides LESS than the PIN leaks a secret into the repository at the next push or out of the machine; a super-linear
rule stalls every push on one long line (AF-AP-152).

## WHAT TO ATTACK (report every observation; no severity filter)

1. R3V-1, closed by the order: your red file (`tasks/briefs/system1/vscrub2r3/vscrub2r1r3_red.py`) on the patched bytes,
   then new shapes of the class (a rule for heads the PIN never read acting before a PIN-head rule) in `scrub()` and in
   `scrub_payload()`, in every view (canonical JSON, pasted JSON, the decoded digest, `convert()`'s events).
2. DISC-4, the cross-rule K-chain residual the builder holds with a strict xfail. Is it D1's class as ruled, or a new
   loss against the PIN? Measure its extent in every view (how many value characters the PIN hid show), and say whether
   it is core-blocking under D-034. If a stop or a reorder closes it without breaking item 2 of the contract, say which.
3. DISC-1, DISC-2 and DISC-3 (D6's start guard, `_LATER_PWD` and `_LATER_CRED` out of stage 1; the new
   `_credentials_or_same` branch): does any of them lose a value the PIN hid, in any view? Re-derive V4 (no redaction the
   PIN makes may be lost) with your own classifier on generated text and on the committed corpus.
4. DISC-5: B1 (linear time) fails for 2 of 97 census families in `scrub_payload`. Are the two PAYLOAD rules byte-identical
   to the PIN's, and is the growth the PIN's too (time both at doublings up to 64,000 characters)? A super-linear path the
   PIN already had is a follow-up; one this patch adds is not.
5. DISC-6 and DISC-7: two frozen items now equal the PIN rather than round 3 (D2's Negotiate-next column; R3-D2's plain-head
   promise in 3 texts). Does "equal to the PIN" meet the contract's words, and does any cell hide less than the PIN?
6. DISC-10 and DISC-11: the two-stage masking (a single-stage mutant can be masked by the other stage) and X13, called an
   equivalent mutant. Confirm with your own mutants, each run as a FAILED test.
7. Linear time for every rule changed in rounds 3 and 4, on your class of adversarial runs, each at several doublings up to
   at least 64,000 characters; and `scrub()`'s constant factor on the 21 committed digests (DISC-12).
8. Everything earlier rounds made true stays true: F1, F15, F2, F7, F10, F12, B2, B3, D1, D2, D6 as ruled, N1, the value
   gate, test isolation, the Laya lock (item counts), digest identity.
9. The relay, a consumer: `tests/test_jev_relay.py` on the patched bytes, and one relay round trip on loopback with a FAKE
   upstream you start yourself (never api.codiv.ai, never a real key: `--no-default-sources`, a fake value file).
10. Mutation: reproduce at least six of the builder's mutants as FAILED tests, and add a mutant for each round-4 clause its
    set does not cover (the stage order first: a new-head rule moved into stage 1).

## GATE

Apply the blocking predicate of skill `contract-gate` and D-034 (a finding re-opens the build only if it is
CORE-BLOCKING; the rest become follow-ups, which the owner routes to GitHub issues, D-108 item 2). One recommendation:
MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID, each blocking finding with its reproduction
command.

## BOUNDARY

READ everything. WRITE only your report and scratch under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r4/`. Apply the patch only in a scratch
copy (a detached worktree at the PIN with hooks off, or a `git archive` of what the tests need; never the shared tree);
remove every worktree you make before you report. The builder's instruments under `.../scratchpad/scrub2r4/` (if present)
and `.../scratchpad/scrub2r3/`, and yours under `.../scratchpad/vscrub2r2/` and `.../scratchpad/vscrub2r3/`, are yours to
read and run in your copy.

## STANDING RULES

- No git writes (a worktree add and remove, hooks off, is the one exception), no PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables. Anything that could reach one
  runs through the masking runner `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/masked.sh`.
  The exporter's and the relay's default sources are never exercised. Test secrets are FAKE strings built at run time.
- Another lane (VERIFY-LS-B10) and a VERIFY-H1a lane may run beside you; touch no file of theirs.
- The disk is shared: scratch under 200 MB, deleted as you go; a private `--basetemp` outside any work tree for every
  pytest run, passed as a pytest ARGUMENT (never through `PYTEST_ADDOPTS`, AF-AP-237); never run the whole
  `tests/test_vendored_manifest.py`.
- The sandbox VM rebooted twice today while tests ran (14:09:29Z, about 14:20:10Z; cause open, memory looked small): run
  `free -m` before a heavy command, keep each run's evidence on disk as you go, and say in the report which runs a reboot
  voided.
- Test counts are pasted from `scripts/test_summary.sh` with their set ids. Stamps are substituted from `date -u`, never
  typed.
- Long commands in one foreground call, each under 10 minutes; kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Cite commits by subject or by an origin id; the coordinator's local ids change on the push.

## PREMISE — MEASURED at authoring (2026-09-29, main tree@0ab1df7; PIN origin 0ab1df7)

Printed by `bash scripts/premise_block.sh` from the main tree at origin 0ab1df7, after the push. The PIN is origin 0ab1df7; the five files the patch changes are byte-identical from the builder's PIN bef1e9e to it (the numstat line), so the patch's base is the PIN's bytes. The last line is the set id for the counts you paste; no count was run at authoring: re-measure in your copy. Re-run every `$` line from `/home/user/agent-factory`; on any difference, stop and report CONTRACT-INVALID with the diff.

```
$ git merge-base --is-ancestor 0ab1df7 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git status --porcelain -- scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
$ git diff --numstat bef1e9e 0ab1df7 -- scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json | wc -l
0
$ sha256sum tasks/briefs/system1/SCRUB2-R1-R4.patch | cut -c1-64
f18f85c9b0abaf7b43c06ed4726671c781b9b44390268210e4de7d23aa4b8020
$ git apply --check tasks/briefs/system1/SCRUB2-R1-R4.patch && echo patch-applies-at-HEAD
patch-applies-at-HEAD
$ sha256sum scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json | cut -c1-16,65-
6ad316dccfca0147  scripts/transcript_export.py
68c712893ffed4e9  scripts/session_export.py
5b22cc0040767dc7  tests/test_transcript_export.py
101298e96f776997  tests/test_session_export.py
a2e6143c0543f640  docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
$ sha256sum tasks/briefs/system1/SCRUB2-R1-R4-report.md tasks/briefs/system1/SCRUB2-R1-R4-brief.md tasks/briefs/system1/VERIFY-SCRUB2-R1-R3-report.md | cut -c1-16,65-
2d065c4cf5ca328b  tasks/briefs/system1/SCRUB2-R1-R4-report.md
f604b295d41eff6b  tasks/briefs/system1/SCRUB2-R1-R4-brief.md
8c1acd7a7941d3d7  tasks/briefs/system1/VERIFY-SCRUB2-R1-R3-report.md
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py tests/test_session_export.py tests/test_jev_relay.py | tail -1
3 files set=fe0d5d434040
```
