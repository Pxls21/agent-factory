# VERIFY-JT1R1-JT2: the independent verify of the Jev client repair and the Jev bug locator (tasks #235, #227, #229; rule 0f)

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: the content of the files hashed below (re-measure the blobs first).
Report: `tasks/briefs/jev-laya/VERIFY-JT1R1-JT2-report.md` (write it incrementally from the start).

Two landings meet in `jev.rank`, so one verify covers both. JT1-R1 (commit "jev: JT1-R1 lands", GATED-PENDING-VERIFY) is the one
D-031 repair of the Jev client and the hiccup tracker; the coordinator re-ran its gate only. JT2 (commit "jev: JT2 lands", 6b171fb,
GATED-PENDING-VERIFY) was never verified; the JT1-R1 commit also carries the coordinator's alignment of JT2 to D-076 (b)
(`JEV_QUERY_CHARS` 1,200 to 1,000 and four test pins). Attack both against their full contracts with NEW shapes, never only the
lanes' cases. Report every meaningful observation with no severity filter, then apply the blocking predicate (contract-mapped,
reproduced through the real path, materially effective, a concrete discriminator, in-boundary) and give ONE gate recommendation
per component (JT1-R1, JT2): MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID.

## The contracts and the evidence

- JT1-R1: `tasks/briefs/jev-laya/JT1-brief.md` (D-1 to D-12, A1 to A8) as amended by D-076 (`docs/08_DECISION_LOG.md`), and
  `tasks/briefs/jev-laya/JT1-R1-brief.md`. Evidence: `tasks/briefs/jev-laya/JT1-R1-report.md`; the round before it:
  `tasks/briefs/jev-laya/VERIFY-JT1-report.md` (F-16, F-17, F-18, F-24 are the findings the repair answers).
- JT2: `tasks/briefs/jev-laya/JT2-brief.md` and D-077 (`docs/08_DECISION_LOG.md`: the locator's default order is `lexical`, Jev
  is opt-in). Evidence: `tasks/briefs/jev-laya/JT2-report.md`, `docs/research/findings/jev-locate-bench/`.

## The files

JT1-R1: `scripts/jev.py`, `scripts/jev_local.sh`, `scripts/hiccup_scan.py`, `scripts/hiccup_families.tsv`,
`tests/test_jev_client.py`, `tests/test_hiccup_scan.py`, `docs/HICCUPS.md` (generated). JT2: `scripts/jev_context.py`,
`scripts/jev_locate.py`, `scripts/jev_echo.py`, `tests/test_jev_context.py`, `tests/test_jev_locate_echo.py`,
`docs/research/findings/jev-locate-bench/`.

## Suspicions to test (not a limit)

- D-076 (a) and (d): can the normalization between the two scrubs build a secret shape the second scrub misses, or split one the
  first scrub caught? Every excerpt path, and the tool, model and agent-id cells: which paths reach the page without both scrubs?
  The lane's own leak cases (an ANSI code between a name and its value; a value under 8 characters) are scrubber limits it
  routed to follow-ups; say whether any other shape leaks, fake strings only.
- D-076 (b): the 1,000 and 2,500 cuts measured in characters against a 1,024-token window: does a real query plus a real chunk
  still cut the chunk off (dense text, code, non-Latin scripts)? Does the all-equal refusal fire on genuine ties (two irrelevant
  chunks that both score 0.0100), and is that the contract's intent? The CLI exit 3 line and the import API's None on every path.
- D-076 (c): the byte invariant (the `--jev` page minus its column equals the plain page) on inputs the lane did not sweep, and
  both pages under the 40,000-byte cap; what the plain page lost to the earlier trim (ADJ-5).
- JT2 against its whole contract, plus the alignment: the query sent is the question's tail and now survives rank's head cut
  whole; the pin test ties `JEV_QUERY_CHARS` to `jev.RANK_QUERY_CHARS`; one tied batch in a multi-batch ranking fails the whole
  ranking (all or nothing): does the pack fall back to the base order with the reason, and is that the contract? JT2's own
  all-equal check is now unreachable through rank for two or more chunks: dead code or a live guard?
- D-077: with no `--order`, the locator is lexical and never asks Jev; the Jev order only when asked.
- The adjacent findings the JT1-R1 lane reported (ADJ-1 to ADJ-5): reproduce or refute; do not fix.
- Whether any gate file imports or runs these files (`scripts/gate_files.txt`; `python3 scripts/no_laya_in_gates.py`).

## Evidence rules

Reproduce every claim you rely on; paste counts and outputs from commands you ran. Mutants on scratch copies ONLY (never edit,
stash, restore or check out a tracked file in this tree). Use a short `--basetemp` (for example `/tmp/vjt12/bt`; make the parent
first); the sandbox venv has no pytest-xdist, so never pass `-n`. The local Laya server for tools is 127.0.0.1:47411 (use it; never
stop it). Never call the bridge yourself: for the PC venue, test with an injected runner. Record which model served your turns if
you can see it.

## Standing rules

No outward actions (no commits, pushes, PRs, comments, GitHub writes, bridge calls, third-party APIs). Do not spawn subagents.
Other lanes: JT3-R1 edits `.claude/hooks/search-intercept.py`, `tests/test_search_intercept.py`, `tests/test_session_hooks.py`;
FT1 creates `scripts/laya_ft/` and `tests/test_laya_ft.py`; an OpenJev run writes `docs/research/findings/j2b-variants/openjev/`:
never touch those. Never create or remove `.jev/intercept-off`. Test secrets are FAKE strings (QZJ8... and X4Z9... style). Kill by
pid only. Check every file you write with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`.

## PREMISE — MEASURED at authoring (2026-09-24 16:1xZ, /home/user/agent-factory at local HEAD db5df20)

```
$ for f in <the twelve files>; do echo "$(git rev-parse --short=12 HEAD:$f) $f"; done
2d419d932bf6 scripts/jev.py
91ff34e0d914 scripts/jev_local.sh
8e9ca1210551 scripts/hiccup_scan.py
e70eb70948f4 scripts/hiccup_families.tsv
f562602c171e tests/test_jev_client.py
3cdfa67de2d6 tests/test_hiccup_scan.py
d8bd3df4b632 docs/HICCUPS.md
f25e3219e9bd scripts/jev_context.py
70720f113389 scripts/jev_locate.py
79ab68f0ce63 scripts/jev_echo.py
60af25fa3823 tests/test_jev_context.py
b5a110aafe74 tests/test_jev_locate_echo.py
$ grep -n -E "^RANK_QUERY_CHARS|^RANK_CHUNK_CHARS" scripts/jev.py; grep -n "^JEV_QUERY_CHARS" scripts/jev_context.py; grep -n "^DEFAULT_ORDER" scripts/jev_context.py
68:RANK_QUERY_CHARS = 1000     # the window budget (D-076 b): a rank's query, after the scrub
69:RANK_CHUNK_CHARS = 2500     # ... and each of its chunks
55:JEV_QUERY_CHARS = 1000      # = jev.RANK_QUERY_CHARS (D-076 (b)); the tail is kept here, so nothing is cut there
77:DEFAULT_ORDER = "lexical"
$ bash scripts/lane_gate.sh -r HEAD -f "<the 8 changed files>" -t "tests/test_jev_client.py tests/test_hiccup_scan.py tests/test_jev_context.py tests/test_jev_locate_echo.py" -n 2   (run on ec77d72 plus the working-tree files before the commit)
RESULT: rev=ec77d723111b files=8 deleted=0 runs=2 tests=8d2e46126186 identical=yes rc=0 summary="172 passed in 44.30s 172 passed in 43.35s"
```
