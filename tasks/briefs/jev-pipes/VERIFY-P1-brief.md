# VERIFY-P1: attack the P1 replay's FAIL and the instrument that measured it (task #260; seed AC7; rule 0f; D-031)

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: e8c14bf (origin; the P1 harvest). Report:
`tasks/briefs/jev-pipes/VERIFY-P1-report.md` (write it incrementally from the start). Do NOT spawn subagents. Report EVERY
meaningful observation with no severity filter, then apply the blocking predicate (contract-mapped; reproduced through the real
production path; materially effective; a concrete discriminator; in-boundary) and end with a GATE RECOMMENDATION: MERGE-READY,
MERGE-READY-WITH-FOLLOWUPS, NOT-READY or CONTRACT-INVALID. The coordinator owns the final gate.

## WHY

P1 replayed the owner-recommended jev-pruner over this session's tool results with the local Laya scorer and pruned nothing
(FAIL). The seed's exit still needs an independent round (AC7), and the harness will grade the next scorer and the redesigned
pipeline: a harness that can only print FAIL, or that miscounts a PASS, would mislead every later decision (D-087). Two questions:
is the FAIL real and for the stated reasons, and would this instrument measure a working pruner correctly?

## CONTRACT (frozen)

`seeds/seed-jev-pipes-p1-v1.yaml` (the acceptance criteria and the exit conditions), `tasks/jev-pipes-p1-breakdown.md`, and
`tasks/briefs/jev-pipes/P1-brief.md`. The lane's report is `tasks/briefs/jev-pipes/P1-report.md` (its deviations, self-attack,
NOT-done and DISCREPANCIES: judge each against the contract); the findings report is
`docs/research/findings/jev-pipes/P1-replay-2026-09-25.md`.

## ATTACK SURFACES (new shapes; never only the lane's own cases)

1. **The FAIL's causes, each through the real code.** (a) The skip counts (document 2,351, few_chunks 524, budget_unfit 12,
   tool_error 10, binary 2): are they the vendored pruner's own decisions (`vendor/jev-pruner/src/`), or a harness rule that
   mirrors or overrides it? (b) The scorer never saw the chunk: rebuild a sample of the replay's per-chunk states exactly as
   `scripts/laya_systemone_server.py:139` sends them and as `laya.common.build_sequence` reads them (the typed-decisions
   checkpoint's own lengths; `scripts/laya_ft/build_dataset.py` `Fitter` is the existing instrument) and measure how many chunk
   tokens survive. (c) The fail-open trips (queue_depth 241, budget 13): the pruner's rule or the harness's?
2. **The instrument on a PASS path.** Construct a transcript fixture and a loopback fake scorer (a FAKE server you write; never
   the live one for this) that answers low only for chunks you planted as noise: does the replay prune them, count the saved
   tokens by the seed's formula, and PASS? Then plant a later tool input that uses a pruned chunk's distinctive tokens, and a
   re-run of the same command within 20 calls: are both counted as misses, and does the miss rate flip the verdict at the 5% bar?
   A compaction boundary: does the saving stop at the next compaction?
3. **The report's numbers.** Recompute the headline counts from the decision logs (`.jev/pipes/p1-decisions*.jsonl`, mode 0600,
   gitignored) and compare with both reports.
4. **Privacy.** No session text in any committed file of the lane (reports, fixtures, code); the decision logs hold pointers,
   counts and scores only.
5. **Regressions.** The `.gitignore` re-include of `vendor/jev-pruner/` (does anything else under `vendor/` become tracked?); the
   manifest tests' new counts; `scripts/vendored_manifest.py`'s new provenance parse on a hostile `VENDORED-FROM.md` line.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Every finding with file:line, the command and its output, and the blocking predicate applied item by item.
3. A mutation table of NEW mutants of the harness and its accounting (each red or surviving, with the test that catches it or the
   gap it shows): at least a miss that is not counted, a saving counted past a compaction, and a skip reason taken from the harness
   instead of the pruner.
4. `bash scripts/test_summary.sh tests/test_jev_pipes_replay.py` twice at the PIN in a clean worktree, with the set id.
5. NOT-done.

## VENUE AND STANDING RULES

Work in a clean detached worktree at the PIN (`git -C /home/user/agent-factory worktree add --detach <scratch>/wt e8c14bf`, the only
git write you make; remove it at the end). Scratch: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/
verify-p1/` (stay under 500 MB; about 2 GB are free). The live Laya server (127.0.0.1:47411, a live hook uses it): never restart
it; at most 20 requests to it in total, one at a time. No network beyond loopback; no PC bridge; no outward-facing action. Never
read a real secret file (`.pc-bridge.env`, `/root/.codiv/api.env`, any `*.env`, any key file). Session text you rebuild from the
transcripts stays in your scratch and never enters your report beyond short, non-secret identifiers. Check your report with
`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` (0 expected).

## PREMISE — MEASURED at authoring (2026-09-25 08:3xZ, the sandbox)

```
$ git show e8c14bf:<file> | sha256sum | cut -c1-16
f10df15241c34828  scripts/jev_pipes/replay_pruner.py
7789b1c8c983f9e6  scripts/jev_pipes/accounting.py
1e6f77216996d2f5  scripts/jev_pipes/transcript.py
54e1212d125e2654  scripts/jev_pipes/bridge.mjs
28b097e1ad7f67f6  tests/test_jev_pipes_replay.py
797329fdac2a446a  docs/research/findings/jev-pipes/P1-replay-2026-09-25.md
cba055a9dc33de21  scripts/laya_systemone_server.py
$ bash scripts/test_summary.sh tests/test_jev_pipes_replay.py        (the shared tree at the PIN's content)
pytest-summary: 34 passed in 13.40s
$ bash scripts/pc_suite.sh set-id -- tests/test_jev_pipes_replay.py
1 files set=17f6a5adc0c9
$ grep -n "dict(base, chunk=" scripts/laya_systemone_server.py
139:        one = State.agent.system_one(dict(base, chunk=chunks[qid]), {qid: q})
$ ls .jev/pipes/     (mode 0600 files, gitignored)
p1-decisions-plan-all.jsonl  p1-decisions-plan.jsonl  p1-decisions-sample.jsonl
$ (the typed-decisions checkpoint's lengths, read through build_dataset.Fitter by the coordinator at 08:2xZ)
max_len 1024 head_max_len 256
$ (the coordinator's echo measurement: the ap-hawk probe's per-chunk states, rebuilt the same way)
per-chunk states: 300 states cut: 0
```

Questions for you, not facts: the lane's full-set decision log: which file holds it (the listing shows plan, plan-all and sample
logs)? Does the replay mode that produced the verdict leave a log you can recompute from?
