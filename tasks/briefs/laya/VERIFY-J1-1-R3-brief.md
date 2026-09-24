# VERIFY-J1-1-R3 — the independent verify of the third J1-1 redaction repair, and of the C4 amendment it forced (task #216 verifies task #202)

PIN: 942ad5e (the origin head at authoring; J1-1-R3 landed in fdac751 and no later commit touches V, TC or TL: the premise block
shows it; re-measure the boundary blobs first). COMPONENT: `src/agent_factory/decisions/volatile.py` (V), `tests/test_decisions_canonical.py` (TC), `tests/test_decisions_ledger.py`
(TL). The builder's report `tasks/briefs/laya/J1-1-R3-report.md` is an INPUT TO ATTACK, not a truth.
LANE: verify-j1-1-r3 (sandbox; agent `adversarial-verifier`, in the SHARED tree, no worktree isolation). Honey `full`: line-bounded
findings, evidence anchors, SOLID/UNSURE. Do NOT spawn subagents.

WHY THIS LANE EXISTS. J1-1-R3 is GATED-PENDING-VERIFY (rule 0f). V is the redaction layer of the decision ledger: a value that reaches
`decision_state`'s output reaches `canonical()`, the row digest and the append-only ledger line on disk. The builder met C1, C2, C3, C5
and C6, and C4 against d556c9b, and stopped on its D-1: C4 against fb016d0 cannot hold together with C1 on true chains. The coordinator
ruled D-067 (`docs/08_DECISION_LOG.md`) on the builder's measurements, which nobody independent has reproduced. This lane is that
reproduction. If C4a or C4b's attribution fails here, D-067 is void and the landing reverts.

CONTRACT (frozen): D-059 (AMENDMENT 3) as amended by D-067, and C1-C6 of `tasks/briefs/laya/J1-1-R3-brief.md` ("The contract") with C4
replaced by:
- C4a: no BODY byte that d556c9b redacts becomes visible.
- C4b: against fb016d0, a newly visible BODY byte is accepted only when a mechanical attribution assigns it to one of the contract's own
  fixes (R-1, R-2, R-4, R-3) or their combination, AND the byte is also visible at d556c9b.
KNOWN, do not re-derive; report as KNOWN if you meet them: AF-AP-157's chain family (task #198: in a chain the first value keeps the
PIN's output); the `NAME==v` residue behind sk or bearer (C2's declared residue); issue #49 and issue #47 rows.

## Items (report EVERY observation; no severity filter; rank downstream)

1. **Premise.** Re-measure the block below at the PIN. A mismatch in the boundary stops the lane CONTRACT-INVALID; say what differs.
2. **C4a, independently.** Write your OWN generator (never the builder's `diff3.py`, `tri3.py` or `attr3.py`, and never VERIFY-J1-1-R2's
   tools as they are). Compare d556c9b's V with the PIN's V over the same inputs through `decision_state` (and, for every hit, through
   `make_row` -> `append` -> the ledger line on disk -> `replay`). List every input where a byte d556c9b redacted becomes visible;
   separate BODY bytes from name, separator and padding bytes. Cover the special letters (U+0130, U+0131, U+017F and at least two other
   case-folding letters of your choice), both separators with and without quotes and spaces, `bearer` and `sk-` glued at several
   offsets, true chains (two and three values), and every field of every closed schema that reaches the redactor. Paste your input
   counts and the BODY count per family. The claim to break: zero.
3. **C4b, independently.** The same generator against fb016d0. For every newly visible BODY byte: is it visible at d556c9b as well
   (C4b's second condition)? Then build your OWN attribution (revert each of the four changes singly on a scratch copy, or any method
   that assigns an exposure to a change mechanically; say which) and report every exposure it cannot assign to R-1, R-2, R-4, R-3 or a
   combination of them. The builder claims its variant with all four changes reverted equals fb016d0 on all inputs: check that for
   your inputs (a mismatch means the attribution harness is broken, not the code).
4. **C1-C3 beyond the builder's rows.** Your own R-1, R-2, R-4 and R-3 shapes (never the builder's or VERIFY-J1-1-R2's case files):
   does any byte of the fake value reach `decision_state`'s output, `canonical()`, or the appended ledger line, and does `replay` accept
   the row? Then the three C3 mutants (V-M3, V-M11, V-M4) rebuilt on a scratch copy: each must be killed by a named test.
5. **The merge step.** `_BEARER_MERGE` and `_yield_pattern` are new. Attack them: a bearer run shorter than 16, a bearer at the very end
   of a value, a bearer inside quotes, `bearer` with mixed case and each special letter, a bearer glued to a second bearer, a merge
   whose tail holds a second head, the depth-2 limit the builder declares (`volatile.py:98-101`). For each: is the output the d556c9b
   output byte for byte, or better? Report every shape where it is worse.
6. **C5, cost and identity.** The seven golden digests unchanged; `decision_state` idempotent on its own output for your shapes; no
   fixture string in the committed goldens or probes changes. Time 16k, 32k, 64k, 128k and 256k characters on inputs built to make the
   new step super-linear (many glued bearers, long runs of near-heads, nested merges); paste the table with the per-doubling ratio.
7. **The builder's evidence.** Re-run at least ten of its 58 mutants (each red for the stated reason) and add at least five of your own
   (the step's possessive replay made greedy; the depth-0 yield dropped from the step; `_BEARER_RUN` back to case-sensitive; FIX-B's
   lookahead removed; the step's `{16,}` floor changed); say which test kills each or that none does. Its D-3 (26 tests that cannot be
   red at the head): check that each named negative-control mutant really reds its test.
8. **Gates.** TC and TL twice with identical counts and the set id; `tests/test_decide_harvest.py` twice (the adjacent consumer; at
   this PIN it carries J1-3-R1's tests); pyflakes on V, TC and TL; `python3 scripts/no_laya_in_gates.py`.

Tools you may read (never run in place, never write): `/tmp/vj11r2/` (VERIFY-J1-1-R2's tools) and `/tmp/j113s/v/` (the builder's). They
exist in this container only; if they are gone, say so and work from the reports. Copy anything you run into `/tmp/vj113r3/`.

Standing rules: write ONLY `tasks/briefs/laya/VERIFY-J1-1-R3-report.md` (incrementally, from the start) and scratch files under
`/tmp/vj113r3/`. Every mutation runs on a scratch copy; never edit, stash, checkout, restore, reset or clean anything in the shared tree,
and never run git add or commit there. Another lane is live in the tree (task #215 on `.claude/hooks/edit-snapshot.py`,
`tests/test_edit_snapshot_ap_screen.py`, `tests/test_vendored_manifest.py`, three skills and their twins, the manifest files): never
touch its files. A command with a trailing `&` runs in the background in its own directory; never let one create files in the tree
root (VERIFY-K150 F-20). Take no outward-facing action, no PC or bridge use. Paste every count and timestamp from command output. Fake
secrets only (`QZJ8…`, `X4Z9…` style), never a real key. End with a GATE RECOMMENDATION (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS /
NOT-READY / CONTRACT-INVALID) under the blocking predicate (contract-mapped, reproduced through `decision_state` and the ledger append,
materially effective, a concrete discriminator, in-boundary); KNOWN rows never block this lane. A C4a hit or an unattributed C4b
exposure blocks. Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-1-R3-report.md` (at most three
fix rounds, then paste and finish).

## PREMISE — MEASURED at authoring (2026-09-24 05:1xZ, /home/user/agent-factory@942ad5e; generated by scripts/premise_block.sh)

```
$ git rev-parse --short '942ad5e^{commit}'
942ad5e
$ git merge-base --is-ancestor 942ad5e origin/claude/soundbox-kit-migration-iz1jwf && echo pin-is-on-origin
pin-is-on-origin
$ git log -1 --format='%h %s' 942ad5e -- src/agent_factory/decisions/volatile.py | cut -c1-90
fdac751 J1-1-R3 landed GATED-PENDING-VERIFY: the redaction regressions fixed; C4 amended (
$ git ls-tree 942ad5e -- src/agent_factory/decisions/volatile.py tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/test_decide_harvest.py | awk '{print substr($3,1,12), $4}'
2d5cf0072469 src/agent_factory/decisions/volatile.py
bb0187044a6a tests/test_decide_harvest.py
733fe70b705b tests/test_decisions_canonical.py
9900d9648fb8 tests/test_decisions_ledger.py
$ git ls-tree d556c9b -- src/agent_factory/decisions/volatile.py | awk '{print "d556c9b", substr($3,1,12), $4}'
d556c9b 20ebcd54f3ed src/agent_factory/decisions/volatile.py
$ git ls-tree fb016d0 -- src/agent_factory/decisions/volatile.py | awk '{print "fb016d0", substr($3,1,12), $4}'
fb016d0 bf04415d72c1 src/agent_factory/decisions/volatile.py
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*$//'
177 passed
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decide_harvest.py -q -p no:cacheprovider 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*$//'
67 passed
$ bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py
1 files set=87e28761f102
$ grep -n -E '^_BEARER_RUN|^_BEARER_MERGE|^def _yield_pattern|^_YIELD =|^_BEARER =|^_ENVVAL_HEAD|^_ASSIGNMENT_HEAD' src/agent_factory/decisions/volatile.py
68:_ASSIGNMENT_HEAD = _SECRET_NAME + r"[\"']?\s?[:=]|(?i:(?:\b|(?<=_))token)[\"'\s]"
69:_ENVVAL_HEAD = r"(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)="
70:_BEARER_RUN = r"(?i:[A-Za-z0-9._~+/-])"
73:def _yield_pattern(merge: str) -> str:
103:_BEARER_MERGE = (
107:_YIELD = _yield_pattern(_BEARER_MERGE)
108:_BEARER = re.compile(
$ grep -c '^| D-067 |' docs/08_DECISION_LOG.md
1
$ ls -d /tmp/vj11r2/tools /tmp/j113s/v/tools 2>&1
/tmp/j113s/v/tools
/tmp/vj11r2/tools
```
