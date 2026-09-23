# PC continuation — lane T94 (tasks #200 + #167): a failed lane session never becomes a report; a relaunched lane never inherits a dead loop's FAILED

PIN: feb26d7 (the post-push origin head; the original brief's PIN c6dcd61 and this PIN carry byte-identical boundary files — premise below; gate with `-r feb26d7`)

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`, reasoning ultra: OmniRoute's priority chain of
codex and cloud models). The local route is at its KV ceiling with two verify lanes (AF-AP-146). Claim nothing about which model wrote
the code; the harvest measures the provider mix. Venue: `tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey ultra, Lever-2: the report
is DATA (files:lines, pasted counts, discrepancies, NOT-done). Keep your context small: `| tail -n 40` on long output, `sed -n` ranges
instead of whole-file reads.

AUTHORIZATION: defensive tooling on the owner's own lane runner and dispatcher. Every fixture runs in a `mktemp -d` tree with fake
harnesses and a fake bridge; no real lane, server, credential or bridge is touched.

## CONTINUATION (read second)

This lane CONTINUES sandbox lane T94. The sandbox model's weekly quota stopped it at about 16:4xZ on 2026-09-23, mid-increment. Its
last words: "Now implementing R, edit 1 of 2: the AF-AP-140 rename at loop start, placed after the pidfile and both traps so a refusal
cleans the pidfile." Its partial work is APPLIED on your worktree as the lane patch (`git status --porcelain` lists it):

- R (`harness-ports/bin/pc-lane.sh`): +53/-1 against the PIN. Two blocks exist: the AF-AP-140 rename of a stale `FAILED` at loop start
  (after the traps), and the runtime-verdict block after the attempt loop (usage.json read by an inline `python3 -c`; the failed output
  kept as `report.failed-output.md`; a draft promoted under a `DRAFT REPORT — the Hermes session FAILED …` header with the 200 bytes on
  ONE line; no draft → `FAILED` + rc 70; the refusal block's `if` became `elif`). NEITHER block has been tested or run.
- D (`scripts/pc_lane.sh`), T1 and T2: UNTOUCHED.
- The report `tasks/briefs/pc-t90-support/T94-report.md`: §1 premise (HOLDS, sandbox-measured), §2 seams, §3 design decisions.

Treat all of it as a predecessor's DRAFT, never as done: diff R against the PIN, re-verify each design decision in its §3 by your own
measurement (keep it, change it or reject it, and say why in the report), then finish the original brief's contract items 2-7 (item 3
D's defense, item 4's D half, item 5 the tests (a)-(g), item 6 the mutants m1-m6, item 7 the gates) and continue the SAME report
file: keep its sections, mark what you re-verified on this host, add the rest.

**The original brief governs:** `tasks/briefs/pc-t90-support/T94-brief.md`. READ IT WHOLE. Its boundary, contract, rejected alternative
and standing rules apply unchanged, with the venue mapping below.

## VENUE NOTES (this lane only)

- T1 and T2 build their fixtures in `mktemp -d` and set `PC_AF_REPO=/fake` (T1:30, T2:10 and T2:103-142 at the PIN). Run them from your
  tree only. Never run R or D against the real `/home/rocco/agent-factory/.lanes/`, never run `scripts/pc_lane.sh` with a real brief,
  never make a bridge call.
- You run inside a PRIVATE copy of the runner you are editing, so your edits reach no live lane. Two live lanes share this host
  (`pc-verify-k1-h.md--5276976`, `pc-verify-j1-0-r6.md--c6dcd61`); never touch their directories or processes.
- The predecessor measured `test A -ot B` sub-second resolution and `date -u -r` in the sandbox (bash 5.2.21) and INFERRED the PC. Measure
  both here (Fedora 42) and paste the result.
- Gates on this host: `bash harness-ports/tests/test_pc_lane.sh | tail -1` and `bash harness-ports/tests/test_pc_lane_dispatcher.sh |
  tail -1`, each twice with identical counts; `bash -n` on R and D; `bash harness-ports/tests/run-all.sh` once (paste its tail; a
  failure that also fails on the PIN's bytes in a `git archive feb26d7` copy is pre-existing: paste both runs). Each call under the 420 s
  terminal cap.
- Mutants: each on a copy under `../scratch/mut/<m>/` (`git archive feb26d7 | tar -x`, then your final R, D, T1, T2 copied over, then
  the one mutation). Never mutate your tree.

## PREMISE — MEASURED at authoring (2026-09-23 16:56Z, /home/user/agent-factory@feb26d7, the lane patch built from the dead lane's tree)
```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
2026-09-23T16:56Z
feb26d7
$ for f in <T94 boundary>; do echo "$(git rev-parse feb26d7:$f | cut -c1-12) $(git show feb26d7:$f | wc -l) $f"; done
183f337eff91 529 harness-ports/bin/pc-lane.sh
6d6024139163 609 scripts/pc_lane.sh
67ed1e0c3c56 641 harness-ports/tests/test_pc_lane.sh
948c19ac580c 452 harness-ports/tests/test_pc_lane_dispatcher.sh
$ git diff --stat c6dcd61 feb26d7 -- <T94 boundary> | wc -l   (0 = the original PIN c6dcd61 and feb26d7 carry identical boundary bytes)
0
$ git diff --numstat feb26d7 -- harness-ports/bin/pc-lane.sh   (the predecessor's partial edit, shipped in the lane patch)
53	1	harness-ports/bin/pc-lane.sh
$ grep -c . tasks/briefs/pc-t90-support/T94-report.md; grep -n "^## " tasks/briefs/pc-t90-support/T94-report.md
65
5:## 1. Premise re-measure (contract item 1) — HOLDS
34:## 2. Seams verified before code (build-loop step 1)
55:## 3. Design decisions (contract items 2-4)
$ sha256sum <lane patch> | cut -c1-12; grep "^diff --git" <lane patch>
7cebdb2519d7
diff --git a/harness-ports/bin/pc-lane.sh b/harness-ports/bin/pc-lane.sh
diff --git a/tasks/briefs/pc-t90-support/T94-report.md b/tasks/briefs/pc-t90-support/T94-report.md
```
