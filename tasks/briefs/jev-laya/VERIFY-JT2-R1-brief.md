# VERIFY-JT2-R1: the independent verify of the Jev locator and bug-echo after their one repair (tasks #227, #229; rule 0f)

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: the content of the files hashed below (commit "jev: JT2-R1 lands").
Report: `tasks/briefs/jev-laya/VERIFY-JT2-R1-report.md` (write it incrementally from the start).

JT2-R1 is the ONE repair D-031 allows for JT2, after VERIFY-JT1R1-JT2 returned NOT-READY on F-20 (the coordinator's alignment made
JT2 send a raw 1,000-character tail, so bug-echo lost its label and head, and the locator lost its last words when the scrub
lengthened the text; AF-AP-193). The repair put one rule at the one call site: `jev_context.fit_scrubbed` scrubs with the scrub
`jev.rank` applies, then keeps the longest tail (locator) or head (each 488-character bug-echo side) that the scrub leaves unchanged.
Attack it against JT2's FULL contract (`tasks/briefs/jev-laya/JT2-brief.md`, D-077, and the client's D-076 (b) and D-080), the repair
brief (`tasks/briefs/jev-laya/JT2-R1-brief.md`) and the previous verify (`tasks/briefs/jev-laya/VERIFY-JT1R1-JT2-report.md`, section 9
and F-20, F-21, F-22, F-23), with NEW shapes, never only the lane's cases; the lane's report is `tasks/briefs/jev-laya/JT2-R1-report.md`.
Report every meaningful observation with no severity filter, then apply the blocking predicate (contract-mapped, reproduced through the
real path, materially effective, a concrete discriminator, in-boundary) and give ONE gate recommendation: MERGE-READY /
MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID.

## Suspicions to test (not a limit)

- The set: is `jev_context.jev_rank` really the only JT2 path to `jev.rank`, and do all three query builders (the locator's
  question, bug-echo's labelled query, the A3 bench input) pass through `fit_scrubbed`? Enumerate them yourself with two instruments.
- The rule: does what reaches the endpoint ALWAYS equal what JT2 passed (rank's scrub and cut remove nothing), for shapes the lane's
  sweep did not generate: multi-byte and combining characters at the cut, a `<redacted>` marker straddling the cut, named values that
  the scrub lengthens near both ends, secrets split across the label and a side, a side made only of redactable text, an empty side?
  Is the "longest" in "the longest tail or head" true, or can the settle loop give up more text than it must?
- The settle loop: its termination and cost on adversarial input (the lane measured a worst case of 951 rounds, 0.149 s): find a
  worse one, and say whether it can stall a pack.
- Leakage: can the cut end inside a secret the whole-text scrub would have redacted (ADJ-D closed a raw cut that sent a fake value
  unredacted); does any path send unscrubbed text when the scrubber is missing (the new "scrubber missing" reason)?
- F-23: does the new venue test really fail for any JT2 call that is not venue `local` (the verifier's J7 switch to `auto`)?
- Regressions: D-077 (the default order never asks Jev; its pack equals the lexical pack byte for byte), KC-J5 (Jev only reorders),
  the budget and determinism of the pack, the A3 benchmark's reproduction.
- F-22 (JT2's own all-equal check unreachable through the real rank) is a follow-up by the brief: note only whether it changed.

## Evidence rules

Reproduce every claim you rely on; paste counts and outputs from commands you ran. Mutants on scratch copies ONLY (never edit, stash,
restore or check out a tracked or lane file in this tree), one fresh copy per mutant with `PYTHONDONTWRITEBYTECODE=1` (AF-AP-192). The
local Laya server for tools is 127.0.0.1:47411 (use it; never stop it); log its calls to a scratch call log, never the shared
`.jev/calls.jsonl`. Use a short `--basetemp` (make the parent first); never pass `-n`. Another lane (VERIFY-FT1) runs CPU-heavy model
work on this box: prefer the loopback double for volume, and keep live calls few. Record which model served your turns if you can see it.

## Standing rules

No outward actions (no commits, pushes, PRs, comments, GitHub writes, bridge calls, third-party APIs). Do not spawn subagents. Never
create or remove `.jev/intercept-off`. Other lanes: VERIFY-JT3-R1 reads `.claude/hooks/search-intercept.py` and its tests; VERIFY-FT1
reads `scripts/laya_ft/`: never touch those. Test secrets are FAKE strings (QZJ8... and X4Z9... style). Kill by pid only (never pkill).
Check every file you write with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`.

## PREMISE — MEASURED at authoring (2026-09-24 17:4xZ, /home/user/agent-factory at local HEAD b97c84c)

```
$ for f in scripts/jev_context.py scripts/jev_locate.py scripts/jev_echo.py tests/test_jev_context.py tests/test_jev_locate_echo.py; do echo "$(git rev-parse --short=12 HEAD:$f) $f"; done
926080a0aede scripts/jev_context.py
70720f113389 scripts/jev_locate.py
a8acebaa5f59 scripts/jev_echo.py
78371dec3b10 tests/test_jev_context.py
f2c03454e6bb tests/test_jev_locate_echo.py
$ bash scripts/lane_gate.sh -r HEAD -f "scripts/jev_context.py scripts/jev_echo.py tests/test_jev_context.py tests/test_jev_locate_echo.py" -t "tests/test_jev_client.py tests/test_hiccup_scan.py tests/test_jev_context.py tests/test_jev_locate_echo.py" -n 2   (on 86337b7 plus the four files, before the commit)
RESULT: rev=86337b75c546 files=4 deleted=0 runs=2 tests=8d2e46126186 identical=yes rc=0 summary="180 passed in 50.58s 180 passed in 50.79s"
```
