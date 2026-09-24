# JT1-R1 — the one focused repair of the Jev client and the hiccup tracker (task #235; D-076; D-031)

PIN: the content of the files hashed below (committed; re-measure the blobs first). CONTRACT: `tasks/briefs/jev-laya/JT1-brief.md`
(D-1 to D-12, A1 to A8) as amended by D-076 (`docs/08_DECISION_LOG.md`). EVIDENCE: `tasks/briefs/jev-laya/VERIFY-JT1-report.md`
(F-16, F-18, F-24, F-17 in detail, with the verifier's reproductions). LANE: jt1-r1 (sandbox; agent `code-implementer`, Opus 5.5,
in the SHARED tree, no worktree isolation). Do NOT spawn subagents. Report: `tasks/briefs/jev-laya/JT1-R1-report.md` (write it
incrementally from the start). This is the ONE repair D-031 allows for this contract revision: fix the set, not the instances.

## Boundary (MODIFY only these)

`scripts/jev.py`, `scripts/hiccup_scan.py`, `tests/test_jev_client.py`, `tests/test_hiccup_scan.py`, and `docs/HICCUPS.md` (only by
regenerating it with the scanner's own command, as JT1 did). READ anything else. Report adjacent defects; never fix them.

## The contract changes (D-076)

- **(a) D-11 order.** Every excerpt: scrub the raw text, normalize, scrub again, cut. Every path that puts text on the page
  (error first lines in both cluster tables, agent descriptions, and per (d) tool names, model names and agent ids) goes through it.
  The five F-16 shapes (named `password:`, `Authorization: Bearer`, `X-Agent-Token:`, `sk-` and `xox` values of 8-19 characters,
  fake strings only) must leave no letter of the value on the page.
- **(b) The rank window budget.** After the scrub, `rank` cuts the query to at most 1,000 characters and each chunk to at most
  2,500, and refuses as signal-free a rank whose answers are all equal (two or more chunks, equal to 4 decimals): the CLI exits 3
  with one line naming the reason, the import API returns None. Every other `jev.py` fail-open rule stays as it is.
- **(c) KC-J1b as bytes.** For every input, including pages over the 40,000-byte cap, the `--jev` page minus its column equals the
  plain page byte for byte, and both pages stay within the cap. How the trim achieves it is yours to choose; state the rule, and say
  what the plain page shows that it did not show before (for example fewer rows and a "not shown" line).
- **(d) F-17.** Tool, model and agent-id fields pass the same scrub.

## Evidence demands

1. Premise: re-measure the blobs and the test pair below; stop and report on any mismatch.
2. For each of (a) to (d): a new test that is RED on the PIN code for the reason the finding names and GREEN after, both runs pasted.
   (c) must cover at least one over-cap page built like the verifier's fixture (about 180 subagent transcripts, covered clusters,
   so the `--jev` run needs no model call) and a sweep of generated over-cap pages. (b) needs a live check against the local
   server on 127.0.0.1:47411 (never stop it): the verifier's long-query rank now either ranks with distinct scores or refuses.
3. The full pair `tests/test_jev_client.py tests/test_hiccup_scan.py` twice, pasted from `scripts/test_summary.sh`, with a short
   `--basetemp` (for example `/tmp/jt1r1/bt`; make the parent first; the sandbox venv has no pytest-xdist, never pass `-n`).
4. Mutants on scratch copies only: at least one per change, each red on a named test (revert the order; drop the query cut; drop the
   all-equal refusal; trim the two pages separately; skip the scrub on tool names).
5. `python3 scripts/no_laya_in_gates.py`, pyflakes on the four code files, and the separator check below on every file you write.
6. The report: files and lines changed, pasted counts, the mutant table, deviations with reasons, NOT-done.

## Standing rules

No outward actions (no pushes, PRs, comments, GitHub writes, bridge calls, third-party APIs). Do not commit. Test secrets are FAKE
strings (QZJ8... and X4Z9... style); never print a real one. Other lanes: JT2 edits `scripts/jev_context.py`, `scripts/jev_locate.py`,
`scripts/jev_echo.py`, `tests/test_jev_context.py`, `tests/test_jev_locate_echo.py` and `docs/research/findings/jev-locate-bench/`;
VERIFY-JT3 reads `.claude/hooks/search-intercept.py` and its tests; VERIFY-J1-1-R4 reads the `src/agent_factory/decisions/` files:
never touch those. Never create or remove `.jev/intercept-off`. Check every file you write with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`.

## PREMISE — MEASURED at authoring (2026-09-24 14:5xZ, /home/user/agent-factory at local HEAD ee44b41)

```
$ for f in scripts/jev.py scripts/jev_local.sh scripts/hiccup_scan.py scripts/hiccup_families.tsv tests/test_jev_client.py tests/test_hiccup_scan.py docs/HICCUPS.md; do echo "$(git rev-parse --short=12 HEAD:$f) $f"; done
e2d02c35ecc8 scripts/jev.py
91ff34e0d914 scripts/jev_local.sh
b1eb74892575 scripts/hiccup_scan.py
e70eb70948f4 scripts/hiccup_families.tsv
9491dbc0f81c tests/test_jev_client.py
e37a5a228cb0 tests/test_hiccup_scan.py
45d4f7ebf6fc docs/HICCUPS.md
$ bash scripts/test_summary.sh tests/test_jev_client.py tests/test_hiccup_scan.py --basetemp /tmp/jt1r1p/bt
pytest-exit: 0
pytest-summary: 77 passed in 22.08s
$ grep -n -E "^def (build_page|excerpt|_plain|normalize|_strip_jev_column)|^def (scrub|_scrub|rank|_build|cmd_rank)" scripts/hiccup_scan.py scripts/jev.py
scripts/hiccup_scan.py:77:def excerpt(text):
scripts/hiccup_scan.py:354:def _plain(text):
scripts/hiccup_scan.py:519:def build_page(sc, source, jev=None):
scripts/jev.py:141:def _build(cmd, args, max_chars):
scripts/jev.py:454:def rank(query, chunks, instructions=RANK_INSTRUCTIONS, **opts):
```
