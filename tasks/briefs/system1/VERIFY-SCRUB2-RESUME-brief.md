# VERIFY-SCRUB2, resumed from its saved point (task #303)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Owner: the chat of 2026-09-26 05:0xZ ("Yes relaunch
scrub 2 from saved point"; D-098). You continue a stopped lane's work:
- its full contract: `tasks/briefs/system1/VERIFY-SCRUB2-brief.md` (unchanged: WHAT TO ATTACK 1-8, RULES, the target at
  cdbc1b8);
- its report so far: `tasks/briefs/system1/VERIFY-SCRUB2-report.md` (sections 1-4 written, STATUS "IN PROGRESS");
- its scratch: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2/` (its scripts, its copies of
  the PIN and the target, its measurements).

## WHAT HAPPENED

The first verifier ran from 01:43Z to 03:33Z. At 03:33:29Z the owner interrupted the coordinator's turn, and the same
interrupt cut off the verifier's tool call: `measure_v2.py` sub parts 4 and 5 of 6 (part 4 finished; part 5 left an empty
file). The harness does not resume an agent the user stopped. You are a fresh agent: rely only on what the report and the
scratch hold.

## WHAT IS LEFT

1. **Finish section 4's corpus measurement.** Read `measure_v2.py` first, so you know what it measures. Re-run sub part 5 of
   6 (`python3 measure_v2.py sub 5 6 > m-sub-5.txt`, under 285 s per call, as before), then aggregate `m-sub-0` to `m-sub-5`,
   and write the result into section 4.
2. **Attack items 2, 3, 4, 6, 7 and 8** of the brief. Items 1 and 5 are written; add to them only if you find more.
3. **A finding from another lane to confirm or refute** (VERIFY-S1-RATE F6, 2026-09-26): `transcript_export.scrub` lets
   through, inside a note, a fake AWS key id (`AKIA` + 16 characters) and a fake three-segment JWT whose segments are each
   under 40 characters. Say whether SCRUB2's contract covered those shapes (then it is a finding against SCRUB2) or not (then
   it is a new gap: task #319).
4. **STATUS:** your gate recommendation, per the brief.

Report: continue in the same file. Under STATUS, add one line: the lane was stopped at 03:33:29Z and resumed by a fresh
agent at your `date -u`. Keep the first verifier's sections as they are; correct an error only with a dated note.

## STANDING RULES

The original brief's RULES hold in full. The other lanes now in this tree: SYNTH1 (`scripts/s1_synth.py`,
`tests/test_s1_synth.py`, `tasks/briefs/system1/SYNTH1-report.md`) and I59-A (`scripts/validate-ledger`,
`scripts/proof-runner`, `proofs/registry.yaml`, `tests/test_validate_ledger.py`, `tests/test_proof_runner.py`,
`tests/test_attested_inputs.py`, `tasks/briefs/i59/I59-A-report.md`): never touch their files. The disk has about 1.4 GB
free: keep new scratch under 100 MB. When a hook injection stamped `[S1 <id> <source>]` reaches you, write its score line as
a short text of its own (under 200 characters; a note only for a score of 0): a longer text is recorded as thinking and the
score is lost (VERIFY-S1-RATE F1).

## PREMISE — MEASURED at authoring (2026-09-26 05:0xZ, the sandbox tree)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-70
8d39d6a transcripts: scrubbed sandbox chat digests (2026-09-26)
$ git log --oneline cdbc1b8..HEAD -- scripts/transcript_export.py scripts/known_values_check.py tests/test_transcript_export.py tests/test_known_values_check.py scripts/session_export.py | wc -l
0
$ grep -n '^## ' tasks/briefs/system1/VERIFY-SCRUB2-report.md; sed -n '9,12p' <same>
9:## STATUS
13:## 1. PREMISE, re-measured (01:4xZ)
29:## 2. Fresh gates on the two changed test files (02:0xZ)
43:## 3. Attack item 5 first: no committed test opens a real source (02:0xZ)
67:## 4. Attack item 1: the anchors, hostile shapes both ways (02:0xZ)
## STATUS

IN PROGRESS.

$ for k in 0 1 2 3 4 5; do wc -l < <scratch>/vscrub2/m-sub-$k.txt; done   (head line of each)
m-sub-0: 32 lines | sub 0 6: 529140 texts, 151131101 characters, 176 s
m-sub-1: 25 lines | sub 1 6: 601584 texts, 163718955 characters, 184 s
m-sub-2: 30 lines | sub 2 6: 616480 texts, 162312339 characters, 184 s
m-sub-3: 23 lines | sub 3 6: 448499 texts, 128836810 characters, 148 s
m-sub-4: 23 lines | sub 4 6: 579048 texts, 162160013 characters, 186 s
m-sub-5: 0 lines | 
$ du -sh <scratch>/vscrub2; ls <scratch>/vscrub2 | grep -v '^m32-main' | tr '\n' ' '
26M
__pycache__ anchors.py e2e.py e2e_timing.py envlog exposure.py gate2.py laya_v.py lost.py m-main-0.txt m-main-1.txt m-main-2.txt m-main-3.txt m-main-4.txt m-main-5.txt m-sub-0.txt m-sub-1.txt m-sub-2.txt m-sub-3.txt m-sub-4.txt m-sub-5.txt measure_v2.py mt mutate2_lane.py mutate3.py pin shapes2.py t timing.py tr trace.sh 
```
