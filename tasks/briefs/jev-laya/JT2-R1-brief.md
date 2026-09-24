# JT2-R1 — the one focused repair of the Jev bug locator and Jev-assisted bug-echo (tasks #227, #229; D-031)

PIN: the content of the files hashed below (committed; re-measure the blobs first). CONTRACT: `tasks/briefs/jev-laya/JT2-brief.md` and
D-077 (`docs/08_DECISION_LOG.md`), with D-076 (b) and D-080 as the client's contract. EVIDENCE: `tasks/briefs/jev-laya/VERIFY-JT1R1-JT2-report.md`
(section 9 and the F-20, F-22, F-23 rows of section 11, with the verifier's reproductions). LANE: jt2-r1 (sandbox; agent `code-implementer`,
Opus 5.5, in the SHARED tree, no worktree isolation). Do NOT spawn subagents. Report: `tasks/briefs/jev-laya/JT2-R1-report.md` (write it
incrementally from the start). This is the ONE repair D-031 allows for JT2's contract revision: fix the set, not the instances.

## Boundary (MODIFY only these)

`scripts/jev_context.py`, `scripts/jev_locate.py`, `scripts/jev_echo.py`, `tests/test_jev_context.py`, `tests/test_jev_locate_echo.py`,
and your report. READ anything else (`scripts/jev.py` is the client: read it, never edit it). Report adjacent defects; never fix them.

## The set to fix

- **F-20, BLOCKER: a JT2 query must reach `jev.rank` whole.** The coordinator's alignment (commit "jev: JT1-R1 lands", e0d2bdc) made
  `jev_query` keep the question's raw last 1,000 characters for every consumer. Two members of the set break: (1) bug-echo's labelled
  query (`"the defect: %s; fixed as: %s"`, each side up to `SIDE_CHARS`, so up to 1,144 characters) loses its label and head; (2) the
  locator's tail loses its last words when the scrub lengthens it, because `jev.rank` scrubs BEFORE its head cut to 1,000 (AF-AP-193:
  a cut taken before a length-changing transform). The fix must hold for EVERY query JT2 builds (enumerate them with their call sites
  in the report): after the same scrub `jev.rank` applies, the text JT2 sends is at most `jev.RANK_QUERY_CHARS`, so rank's own cut is a
  no-op; the locator keeps the question's END, bug-echo keeps its label and both sides. How is yours to choose; state the rule.
- **F-23, carried because it is one line of test and guards the bridge:** a test that fails if any JT2 call to `jev.rank` uses a venue
  other than `local` (the verifier's J7 switch to `auto` passed all 78 tests; `auto` can walk to the PC bridge, F-10).
- **Not in this repair** (a verify-followup issue; do not fix): F-22 (JT2's own all-equal check is now unreachable through the real
  `rank`; leave it, say so) and the JT1-R1 findings.

## Evidence demands

1. Premise: re-measure the block below; stop and report on any mismatch.
2. For F-20: tests that are RED on the PIN code for the reason the finding names and GREEN after, both runs pasted: bug-echo's
   maximum-size query (both sides at the cap, the verifier's two A4 commits or equivalents) arrives at the endpoint whole, label
   first; a locator question whose last 1,000 characters hold named values that the scrub lengthens (FAKE strings) arrives with its
   last words; and one property sweep over generated queries: the sent query equals `scrub(built query)` cut by YOUR rule, and
   rank's cut never removes a character. Use the tests' existing loopback double (it records what is SENT).
3. The pair twice: `bash scripts/test_summary.sh tests/test_jev_context.py tests/test_jev_locate_echo.py --basetemp /tmp/jt2r1/bt`
   (make the parent first; the sandbox venv has no pytest-xdist, never pass `-n`), and the JT1 pair once
   (`tests/test_jev_client.py tests/test_hiccup_scan.py`) to show the client side is untouched.
4. The live check against the local Laya server on 127.0.0.1:47411 (never stop it): `scripts/jev_echo.py --order jev` on one of the
   verifier's A4 commits, with the sent query recorded (a scratch call log, never the shared `.jev/calls.jsonl`), label present.
5. Mutants on scratch copies only, each red on a named test: restore the tail cut for bug-echo; cut before the scrub; drop the venue
   pin.
6. `python3 scripts/no_laya_in_gates.py`, pyflakes on the five files, and the separator check below on every file you write.
7. The report: files and lines changed, the query-builder enumeration, pasted counts, the mutant table, deviations, NOT-done.

## Standing rules

No outward actions (no commits, pushes, PRs, comments, GitHub writes, bridge calls, third-party APIs). Other lanes: JT3-R1 edits
`.claude/hooks/search-intercept.py`, `tests/test_search_intercept.py` and `tests/test_session_hooks.py`; never touch those. Never create
or remove `.jev/intercept-off`. Test secrets are FAKE strings (QZJ8... and X4Z9... style). Kill by pid only. Check every file you write
with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`. Keep scratch small and delete large temporary outputs once their numbers are in your report.

## PREMISE — MEASURED at authoring (2026-09-24 17:1xZ, /home/user/agent-factory at local HEAD, after the FT1 commit)

```
$ for f in scripts/jev_context.py scripts/jev_locate.py scripts/jev_echo.py tests/test_jev_context.py tests/test_jev_locate_echo.py; do echo "$(git rev-parse --short=12 HEAD:$f) $f"; done
f25e3219e9bd scripts/jev_context.py
70720f113389 scripts/jev_locate.py
79ab68f0ce63 scripts/jev_echo.py
60af25fa3823 tests/test_jev_context.py
b5a110aafe74 tests/test_jev_locate_echo.py
$ grep -n -E "^(SIDE_CHARS|JEV_QUERY_CHARS)|def jev_query|the defect: |jev.rank\(jev_query" scripts/jev_echo.py scripts/jev_context.py
scripts/jev_echo.py:13:default (D-077). With `--order jev` (opt-in), Jev scores each against "the defect: <removed>; fixed as: <added>" with
scripts/jev_echo.py:37:SIDE_CHARS = 560
scripts/jev_echo.py:317:        query = "the defect: %s; fixed as: %s" % ("\n".join(removed)[:SIDE_CHARS], "\n".join(added)[:SIDE_CHARS])
scripts/jev_context.py:55:JEV_QUERY_CHARS = 1000      # = jev.RANK_QUERY_CHARS (D-076 (b)); the tail is kept here, so nothing is cut there
scripts/jev_context.py:755:def jev_query(text):
scripts/jev_context.py:784:            res = jev.rank(jev_query(query), items[b * JEV_BATCH:(b + 1) * JEV_BATCH],
$ sed -n 755,758p scripts/jev_context.py
def jev_query(text):
    """The question's last JEV_QUERY_CHARS characters (the model's window; see the module docstring)."""
    t = str(text).strip()
    return t[-JEV_QUERY_CHARS:]
$ grep -n '"venue"' scripts/jev_context.py
777:        opts["venue"] = "local"
```

The verifier's reproduction (its report, section 9): `de06db6 rc=0 built query chars=1013 sent chars=1000 starts with 'the defect: ':
False` and `40543ab: built 1144 sent 1000 | starts with the label: False`; the locator case `sent query ends with the question's last
words: False`.
