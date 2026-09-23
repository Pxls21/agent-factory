# VERIFY-J1-1-R2 — the targeted independent verify of the decision ledger's sk/bearer yield repair (task #197)

PIN: fb016d0 (the origin commit of "J1-1-R2 landed (task #192; GATED-PENDING-VERIFY): …", local 9ad0e66). The boundary files are
byte-identical at the origin head 0dfd28e and at later heads until another J1-1 round lands (blob ids below; re-measure them first).
COMPONENT: `src/agent_factory/decisions/volatile.py` (V), `tests/test_decisions_canonical.py` (TC), `tests/test_decisions_ledger.py`
(TL). The builder's report `tasks/briefs/laya/J1-1-R2-report.md` is an INPUT TO ATTACK, not a truth.
LANE: verify-j1-1-r2 (sandbox; agent `adversarial-verifier`, in the SHARED tree, no worktree isolation). Honey `full`: line-bounded
findings, evidence anchors, SOLID/UNSURE. Do NOT spawn subagents.

WHY THIS LANE EXISTS: J1-1-R2 is GATED-PENDING-VERIFY (rule 0f). Its gates were the builder's own tests, mutants, fuzz and driver; the
coordinator re-ran the tests, the brief's appendix driver and the PIN's own tests, which is a second run of the same oracles. V is the
redaction layer of the decision ledger: a value that reaches `decision_state`'s output reaches `canonical()`, the row digest and the
append-only ledger line on disk.

CONTRACT (frozen): D-057 (`docs/08_DECISION_LOG.md`) and B1 to B5 of `tasks/briefs/laya/J1-1-R2-brief.md` ("The contract"), on top of
D-056 (AMENDMENT 1: bound after redact). KNOWN, do not re-derive; report as KNOWN if you meet them:
- AF-AP-157 (`docs/INCIDENT-LOG.md`): F-1, a widened value swallows a second secret name and frees its value, and D-3, a chained value
  keeps the PIN's output (the chain guard). Both are identical at the J1-1-R2 PIN d556c9b; task #198 repairs them. Their measured shapes
  are in the premise block.
- Issue #49 (V-2 to V-6, V-15, V-16, and #187's V-12 to V-14) and issue #47 stay open follow-ups.

## Items (report EVERY observation; no severity filter; rank downstream)

1. **Premise.** Re-measure the block below at the PIN (blob ids, the line map, both test runs with the set id, the driver, the PIN's
   own tests against V, the chained shapes). A mismatch in the boundary stops the lane CONTRACT-INVALID; say what differs.
2. **B1 beyond the builder's rows.** Build your OWN V-1 shapes (never the builder's or the appendix's): other secret-name spellings and
   cases the classes accept, both separators with and without quotes and spaces, the `bearer` and `sk-` prefixes glued to names at
   different offsets, names inside longer words, and every field of every closed schema that reaches `_redact_str`. For each: does any
   byte of the fake value reach `decision_state`'s output, `canonical()` of it, or the appended ledger line, and does `replay` accept
   the row? Include the bound's cut positions (D-056): a value cut by the bound must not leave a matchable fragment either.
3. **B2, an independent differential.** Write your own generator (not the builder's fuzz) and compare the PIN's V (d556c9b) with the new
   V over the same inputs: list every input where a byte the PIN redacted becomes visible. Separate value bytes from name bytes. The
   builder claims names and a following `=` are the ONLY newly visible bytes (its D-1): test that claim, and say whether any newly
   visible "name" byte can belong to a real secret (for example a key or token whose body contains a secret-name spelling followed by
   `=` or `:`).
4. **The chain guard.** Attack the guard's boundaries: a second head at the very end of the value, a head split by the bound, a head
   inside quotes, `token` heads with each separator, heads in mixed case. For each, is the output the PIN's byte for byte (the guard's
   promise), or better? Report any shape where the guard makes the output worse than the PIN.
5. **B4 identity.** The seven golden digests unchanged; `decision_state` idempotent on its own output for your shapes; no fixture string
   in the committed goldens or probes changes.
6. **B5 cost.** The new `_SK` and `_BEARER` evaluate `_YIELD` (nested lookaheads with lazy `\S*?` scans) at every run character. Build
   inputs meant to make that quadratic: many head positions each followed by a long head-free value, long runs of near-heads (`KE`,
   `PASSWOR`), long `token` runs. Time 16k, 32k, 64k and 128k characters (and 256k if the curve bends), and paste the table with the
   per-doubling ratio.
7. **The builder's evidence.** Re-run its 30-mutant table's killing tests on unmutated V (all pass) and at least ten of its mutants
   (each red for the stated reason). Add at least five mutants of your own (a dropped `(?i:…)`, `{8}` to `{7}`, one branch's chain
   guard removed, `_ENVVAL_HEAD` narrowed, the `(?<=_)` lookbehind dropped); say which test kills each or that none does.
8. **F-1 / D-3 input for task #198 (informational, never blocking).** On a scratch copy only, measure one candidate rule ("a value run
   never extends over a following `NAME[:=]` head") for V: which of the premise block's five chained shapes it closes, and whether it
   opens anything on your item 3 generator. An unrun proposal is a question, not a recommendation.
9. **Gates.** TC and TL twice with identical counts and the set id (`bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py
   tests/test_decisions_ledger.py`); the PIN's own two test files against the new V in a scratch worktree (the premise block shows how).

Standing rules: write ONLY `tasks/briefs/laya/VERIFY-J1-1-R2-report.md` (incrementally, from the start) and scratch files under `/tmp`.
Every mutation runs on a scratch copy; never edit, stash, checkout, restore, reset or clean anything in the shared tree, and never run
git add or commit there. Other lanes are live in the tree (S198A on `scripts/transcript_export.py`, `tests/test_transcript_export.py`;
B12 on `proofs/S0-02/` and `tests/test_s0_02_buzz_authz.py`; a verifier writing `tasks/briefs/laya/VERIFY-J1-0-R5-report.md`): never
touch their files. Take no
outward-facing action. Paste every count and timestamp from command output. Fake secrets only (`QZJ8…`, `X4Z9…` style), never a real
key. End with a GATE RECOMMENDATION (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID) under the blocking
predicate (contract-mapped, reproduced through `decision_state` and the ledger append, materially effective, a concrete discriminator,
in-boundary); KNOWN rows never block this lane.

## PREMISE — MEASURED at authoring (2026-09-23 15:09Z, /home/user/agent-factory@9ad0e66)

```
$ git log --format="%h %s" -1 9ad0e66 | cut -c1-100
9ad0e66 J1-1-R2 landed (task #192; GATED-PENDING-VERIFY): the sk and bearer classes yield to a later
$ for f in <boundary>; do echo "$(git rev-parse 9ad0e66:$f) $f"; done
bf04415d72c1eb788e17d0b1e877bc8fdb23dbc5 src/agent_factory/decisions/volatile.py
440ac2426d8f559ca898f6e3664bc2807141987c tests/test_decisions_canonical.py
6648679bd40a1dc953287e9733a28a83c3c5573b tests/test_decisions_ledger.py
11df78562cf331a6fd2e5e302be9bb846e91e975 tasks/briefs/laya/J1-1-R2-report.md
$ git diff --stat d556c9b 9ad0e66 -- src/agent_factory/decisions/volatile.py tests/test_decisions_canonical.py tests/test_decisions_ledger.py
 src/agent_factory/decisions/volatile.py |  38 ++++-
 tests/test_decisions_canonical.py       | 214 +++++++++++++++++++++++++++-
 tests/test_decisions_ledger.py          |  78 ++++++++++
$ grep -n "^_SECRET_NAME\|^_ASSIGNMENT_HEAD\|^_ENVVAL_HEAD\|^_YIELD\|^_BEARER = \|^_SK = \|^def _redact_str\|^def decision_state" src/agent_factory/decisions/volatile.py
57:_SECRET_NAME = r"(?i:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)"
61:_ASSIGNMENT_HEAD = _SECRET_NAME + r"[\"']?\s?[:=]|(?i:(?:\b|(?<=_))token)[\"'\s]"
62:_ENVVAL_HEAD = r"(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)="
67:_YIELD = (
74:_BEARER = re.compile(
77:_SK = re.compile(r"sk-(?=[A-Za-z0-9_-]{8})(?:(?!" + _YIELD + r")[A-Za-z0-9_-])*")
354:def _redact_str(text: str) -> str:
387:def decision_state(question_id: str, state: dict, root: str | os.PathLike | None = None) -> dict:
$ for i in 1 2; do python -m pytest -q -p no:cacheprovider tests/test_decisions_canonical.py tests/test_decisions_ledger.py | tail -1; done
121 passed in 3.69s
121 passed in 3.75s
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
$ python <the J1-1-R2 brief's appendix driver>   (the brief's appendix holds the driver verbatim)
replayed rows: 14 shapes: 14 leaking: 0
$ git worktree add --detach /tmp/j11r2wt d556c9b; cp <new V> /tmp/j11r2wt/src/agent_factory/decisions/volatile.py
$ cd /tmp/j11r2wt && PYTHONPATH=/tmp/j11r2wt/src python -m pytest -q -p no:cacheprovider tests/test_decisions_canonical.py tests/test_decisions_ledger.py | tail -1
72 passed in 2.65s
$ python -c '<volatile._redact_str over the five KNOWN chained shapes>'
LEAK 'passwd=aAPI_KEY : X4Z92Q0X1ZX02Z71' -> 'passwd=<redacted:envval> : X4Z92Q0X1ZX02Z71'
LEAK "token='_API_KEY = 6Z4Z02ZX6Z4Z" -> "token='<redacted:envval> = 6Z4Z02ZX6Z4Z"
LEAK "password='-db_password: 62669Q3JJ88ZX5466" -> "password='<redacted:envval> 62669Q3JJ88ZX5466"
LEAK 'key: service-API_KEY: QZJ8QZJ8QZJ8' -> 'key: <redacted:envval> QZJ8QZJ8QZJ8'
LEAK 'mask-PASSWORD=QZJ8QZJ8QZJ8;token: WQ7XWQ7XWQ7XWQ7X' -> 'ma<redacted:sk>=QZJ8QZJ8QZJ8;token: <redacted:envval>'
```
