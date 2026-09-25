# VERIFY-S0-04-LEAK: attack the S0-04 leak-screen fix and its re-mint before the owner signs (task #287)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/VERIFY-S0-04-LEAK-report.md`
(write it incrementally). Target: the commit whose subject starts "S0-04-LEAK landed (task #287" on the branch (the PIN
below; cite it by subject in anything you write). Contract: `tasks/briefs/system1/S0-04-LEAK-brief.md` (items 1-5), the
lane's own report beside it, and AF-AP-224 in `docs/INCIDENT-LOG.md`.

Authorization, for the record: this is defensive work on the owner's own system. The screens under test keep credentials
out of committed evidence; every key you build is a fake made at run time (`secrets.token_hex`), never a real value, and
nothing you print may contain a matched span that could be a real secret.

## WHY

S0-04 is a minted, owner-signed Stage 0 proof. The fix changed two leak screens (an attested input of the mint) and
re-minted the result; the owner re-signs the new result after this verify. A defect found after the signature costs the
owner another re-sign, so find it now. Grade against the contract, never the builder's own cases.

## WHAT TO ATTACK (report everything; no severity filter)

1. **The anchors.** Build your own hostile shapes: keys glued after `_`, `__`, `-`, `.`, `/`, `:`, a quote, a non-ASCII
   letter, a digit, a letter; keys at line start and end; inside JSON strings with escapes; `<PREFIX>_API_KEY=` and the
   other names of the key-assignment rule in upper, lower and mixed case, with spaces and quotes around `=`/`:`. Through the
   REAL checker on a bundle (copy a fixture bundle to scratch and plant the text), and through the real capture CLI's
   exception path: which leak, which pass, and is each outcome what the contract wants? Also the other direction: ordinary
   text the screens must not trip (header names, code identifiers, prose).
2. **The re-mint.** Reproduce it from a `git archive` of the PIN in scratch: `proof-runner` on the sandbox venue, the
   integrity check, `ledger-gen`; compare with the committed `result.json` and `proofs/ledger.json` field by field. Only the
   two tools' hashes and the volatile fields may differ from the previous result.
3. **The anchor state.** The committed tree is in state (b): no tag object, no local ref, a PENDING line. Prove the checker's
   behaviour on each neighbouring state in a scratch clone (tag present with and without the PENDING line; neither; a tag
   on a commit whose result differs) and that each gives the error or warning the governance README describes.
4. **The narrowed test.** `tests/test_proof_status.py`'s committed-anchor test now asserts no `WARNING S0-11` instead of no
   warning at all. Does any other guard still catch an UNDECLARED warning or an accepted proof with no anchor? Show it with
   a scratch mutation, or show the gap.
5. **Mutation.** Re-run the lane's mutants and add your own on the two changed rules; classify each by a FAILED test, never
   an error (AF-AP-223).
6. **Siblings.** Confirm or refute the lane's sibling findings (S0-01's `_STDERR_LEAK_RE`, the capture guard's missing
   key-assignment rule) with fake inputs through the real code.

## RULES

No git writes in this tree; no PC bridge; no outward-facing action; touch no tracked file (scratch only, under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vs004/`, deleted as you go; the disk is tight).
`tests/test_proof_status.py` needs a SHORT `--basetemp` (for example `/tmp/vs4/bt`, parent created first). Test counts are
pasted from `scripts/test_summary.sh`; stamps from `date -u`. End with a GATE RECOMMENDATION (MERGE-READY /
MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID) and the blocking predicate you applied.

## PREMISE — MEASURED at authoring (2026-09-25 21:1xZ, /home/user/agent-factory at the landing commit)

```
$ git log -1 --format='%h %s' HEAD | cut -c1-100   (the landing to verify; its pushed id follows the push)
<the landing commit> S0-04-LEAK landed (task #287, D-091 item 3; GATED-PENDING-VERIFY): S0-04 leak screen (sk-key
$ git show --stat HEAD | tail -12
 docs/INCIDENT-LOG.md                      |   2 +-
 docs/governance/tags/accepted-S0-04.tag   |  13 -
 proofs/S0-04/check_compression.py         |   7 +-
 proofs/S0-04/result.json                  |  16 +-
 proofs/S0-04/tools/pc/capture_leg.py      |   2 +-
 proofs/ledger.json                        |   2 +-
 tasks/briefs/system1/S0-04-LEAK-report.md | 535 ++++++++++++++++++++++++++++++
 tests/test_proof_status.py                |   2 +-
 tests/test_s0_04_compression.py           |  67 ++++
 todo/BUILD-TASKLIST.md                    |   2 +
 10 files changed, 621 insertions(+), 27 deletions(-)
$ python3 scripts/check-proof-status.py . ; echo rc
proof-status: WARNING S0-04: ACCEPTED with the anchor PENDING the owner's signed tag accepted/S0-04 (declared in the ledger) — not owner-verifiable yet
rc=0
$ python3 scripts/validate-ledger integrity --root . | tail -3
blocked_host numerator=0 denominator=1
conformance_checked_decision numerator=3 denominator=3
execution_proof numerator=9 denominator=9
$ mkdir -p /tmp/ps && bash scripts/test_summary.sh --basetemp=/tmp/ps/bt tests/test_s0_04_compression.py tests/test_proof_status.py
pytest-summary: 131 passed in 10.47s
$ git diff HEAD~1 HEAD -- proofs/S0-04/check_compression.py proofs/S0-04/tools/pc/capture_leg.py | grep -E '^[-+][^-+]'
-    ("sk-key", re.compile(r"\bsk-[A-Za-z0-9_-]{8,}")),
+    # Left anchor `(?<![A-Za-z0-9])`, not `\b`: `\b` needs a non-word character first, so a key glued
+    # after `_` (`x_sk-...`) and a name inside `OMNIROUTE_API_KEY=` passed (AF-AP-224). A letter or
+    # digit before still refuses (`task-...`, `nextPageToken`).
+    ("sk-key", re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{8,}")),
-        r"(?i)\b(?:api[_-]?key|apikey|secret|password|passwd|token)\b"
+        r"(?i)(?<![A-Za-z0-9])(?:api[_-]?key|apikey|secret|password|passwd|token)\b"
-LEAK_RE = re.compile(r"(?i)bearer\s+\S|\bsk-[A-Za-z0-9_-]{8,}")
+LEAK_RE = re.compile(r"(?i)bearer\s+\S|(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{8,}")
$ git diff HEAD~1 HEAD -- tests/test_proof_status.py | grep -E '^[-+][^-+]'
-        assert "WARNING" not in completed.stderr
+        assert "WARNING S0-11" not in completed.stderr    # the docstring's intent; another proof may be pending
```
