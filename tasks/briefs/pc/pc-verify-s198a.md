# VERIFY-S198A — the targeted independent adversarial verify of S198A: the transcript scrubber stops a credential value before the next secret name (AF-AP-157; task #203)

PIN: 750699a (the origin head: "transcripts: scrubbed sandbox chat digests"; S198A itself is 5415c2a, and S, T and P are byte-identical there
and at the PIN — premise below). Confirm with `git log --format='%h %s' -3 750699a`.
LANE: pc-verify-s198a
ROLE: adversarial-verifier. Route: the CLOUD verify route (`HERMES_MODEL=agentfactory-verify`, reasoning xhigh; OmniRoute's priority chain
starts at codex/gpt-5.6-terra-xhigh, a different model family from S198A's builder). Claim nothing about which model wrote which turn;
the harvest measures the provider mix. Venue: `tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey full: line-bounded findings,
evidence anchors, SOLID/UNSURE per observation.

The contract-gate predicate (D-031): a finding BLOCKS only if it is contract-mapped (the contract below), reproduced through the real
producer (`scrub` imported by path from `scripts/transcript_export.py`, and at least once through each real CLI: the sandbox exporter
`python3 scripts/transcript_export.py --transcript <jsonl> --out <dir>` and the PC session exporter `harness-ports/bin/hermes-session-export.py`
over a FAKE state.db built the way `harness-ports/tests/test_hermes_session_export.py` builds one), materially effective (a secret byte the
PIN hid is shown, or a chained secret survives, or a pattern grows faster than linear), with a concrete discriminator (the input, the
PIN's output and the new output, all with fake values), and inside the boundary (S and T below). Everything else is a follow-up. Emit ONE
GATE RECOMMENDATION: `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`; the coordinator owns the gate.

AUTHORIZATION: defensive review of the owner's own credential scrubber. Every secret-shaped value you write is a FAKE string (`QZJ8…`,
`X4Z9…` style). Never read any real transcript, session database, `~/.hermes/` file or credential on this host: the real-transcript
differential (c) was the builder's, in the sandbox, and is out of this lane.

WHY THIS LANE EXISTS: S198A (task #198 increment A, AF-AP-157) was built by a sandbox lane that the sandbox's weekly quota stopped after
its final gates. The coordinator proved the final blob AST-identical to the measured one, re-ran the gates and landed it. Rule 0f: a
re-run of the builder's own gates is not independent verification. Your job is NEW shapes, never the builder's cases.

COMPONENT: `scripts/transcript_export.py` (S: `_NAME`, `_WORD`, `_HEAD`, `_BEARER`, `_LINK`, `_VALUE`, `_CUT`, `_redact_run`,
`SECRET_PATTERNS`), `tests/test_transcript_export.py` (T). READ-ONLY readers: `harness-ports/bin/hermes-session-export.py` (P, imports
S by path), `harness-ports/tests/test_hermes_session_export.py`, `harness-ports/bin/qwen_matrix.py:126-137`.
CONTRACT (frozen): `tasks/briefs/continuity/S198A-brief.md` items 2-5, plus the COORDINATOR RULING in the S198A commit body (`git log
--format=%B -1 -- scripts/transcript_export.py`): the four extensions X1-X4 of the report's section 2.2 are ACCEPTED as contract
amendments; R-1 (a secret value that itself holds a shortest-form head shows that head's bytes) is a DECLARED RESIDUE. INPUTS TO ATTACK,
not truths: the report `tasks/briefs/continuity/S198A-report.md` (sections 2-9) and the commit body.
KNOWN, never blocking here: issue #53 (A1 `Basic` credentials; A2 a lower-case `bearer`; A3 xox eating a bridge-link host; A4 `:''` and
`:='` assignments; A5-A9), R-1 within its declared shape, the committed `transcripts/pc/` exposure question.

## Items (report EVERY observation; no severity filter; SOLID/UNSURE per observation)

1. PREMISE. Re-measure the block below in your worktree (blob ids, the gate count with its set id). A mismatch is CONTRACT-INVALID for
   the affected items; say which.
2. CHAINED SHAPES, NEW ONES (never T's `CHAINED`, `IN_RUN` or the report's section 3 lists). For each: the input, the PIN's output (S at
   9801fb5, from `git show 9801fb5:scripts/transcript_export.py` into your scratch), the new output, and whether any fake secret byte
   survives. At least: tabs and CRLF around the separator; `:=`, `==` and `=>`; a JSON-escaped quote (`\"`) before and after the
   separator; a head inside a URL query string (`?a=QZJ8…&api_key=X4Z9…`) with and without a bridge link; three or more heads in one run
   with mixed case; a head glued to the end of a base64 value (`…==_key=…`); names the report does not list but `_NAME` accepts (read
   `_NAME` and pick the rarest); non-ASCII letters next to a name (`ıAPI_KEY=`, `API_KEYé=`) and a non-breaking space as the separator's
   whitespace.
3. THE FOUR EXTENSIONS. For each of X1-X4, build at least three shapes aimed at its boundary and report whether it opens a new exposure
   against the PIN: X1 (a value stops before a Bearer match: vary the whitespace after `Bearer`, the token length around 8, `Bearer`
   glued to the value's start); X2 (the Bearer rule's own stop before a following Bearer match or link: chains of two and three);
   X3 (a bridge link taken whole past `&`, `,` and `;`: a link followed by a second credential in the same run, a link inside quotes
   and parentheses, a link with a head in its path); X4 (the shortest name reading: `*_key` and `*-key` with prefixes of 0, 1, 7 and 8
   characters, upper case).
4. R-1's BOUNDARY. Find the widest shape the residue shows. It is declared for "a shortest-form head inside a value" (at most the word,
   a quote, whitespace and the separator). A shape where MORE than those bytes show is a finding against the declaration.
5. THE FLOOR DECISION (report section 2.1). Attack the prose side: realistic English and code lines where a secret name is followed by a
   short ordinary word (the negative controls must keep their PIN output), and the secret side: a value cut short by a head is redacted
   at any length. Report any prose line the new rule changes and the PIN did not.
6. COST (contract item 4). Time your own adversarial inputs at 16k, 32k, 64k and 128k characters for `_redact_run` and the Bearer rule:
   many heads, many links, many `_key` fragments, long runs of name letters with no separator, alternating quotes. Paste the table with
   the per-doubling ratio. Growth faster than linear is a finding.
7. YOUR OWN DIFFERENTIAL. Write an independent planted-secret generator (at least 50,000 inputs; your own alphabet and templates, never
   the builder's harness): each input plants fake secrets as values of named assignments; count, for the PIN and for the new S, the
   planted secret bytes that appear in the output. A byte the PIN hides and the new S shows, outside a declared R-1 head, is a finding
   (paste the input). Paste the counts.
8. MUTANTS. Re-run the report's m1-m13 on the final bytes (each on a scratch copy under `../scratch/mut/`), and add at least four of
   your own aimed at X1-X4 (for example X3 without the `,` crossing). Each must red a named test for the stated reason; a survivor is a
   finding (name the missing test).
9. BOTH REAL CLIs. Plant three chained fake secrets in a fake JSONL transcript and in a fake state.db; run each exporter into a scratch
   directory; grep the written digests for every planted secret; paste the counts (expected 0) and the PIN's counts for the same inputs.
10. GATES. `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/bt tests/test_transcript_export.py
    harness-ports/tests/test_hermes_session_export.py` twice (set 4e81d5d61609), `python3 harness-ports/tests/test_hermes_session_export.py`,
    `python3 harness-ports/tests/test_qwen_matrix.py`; each under the 420 s cap.

Boundary: READ-ONLY on every repository file. CREATE only `tasks/briefs/continuity/VERIFY-S198A-report.md` in your tree (write it
incrementally from the start) and scratch files under `../scratch/`. Never fix anything. Take no outward-facing action.

## PREMISE — MEASURED at authoring (2026-09-23 17:17Z, /home/user/agent-factory@750699a)
```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf; git log --format="%h %s" -3 origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-90
2026-09-23T17:17Z
750699a
750699a transcripts: scrubbed sandbox chat digests (2026-09-23)
bdef01f Ledger plane 2026-09-23 17:0xZ: the sandbox weekly limit killed four sandbox lanes
5415c2a S198A (task #198 increment A; AF-AP-157): the transcript scrubber stops a credenti
$ git diff --stat 5415c2a 750699a -- scripts/transcript_export.py tests/test_transcript_export.py harness-ports | wc -l   (0 = S198A 5415c2a and the PIN carry identical S, T and P bytes)
0
$ for f in <S T P P-test qwen_matrix>; do echo "$(git rev-parse 750699a:$f | cut -c1-12) $(git show 750699a:$f | wc -l) $f"; done
37d94bd61556 153 scripts/transcript_export.py
12dbaae6d0da 351 tests/test_transcript_export.py
04326ece5b7a 104 harness-ports/bin/hermes-session-export.py
0d7893bf5d2e 96 harness-ports/tests/test_hermes_session_export.py
cd8763d0e3b3 581 harness-ports/bin/qwen_matrix.py
$ git rev-parse 9801fb5:scripts/transcript_export.py | cut -c1-12   (the PIN of S198A: the scrubber before the change)
a47e0e5861c9
$ python -m pytest -q -p no:cacheprovider --basetemp=/tmp/vs198p/bt tests/test_transcript_export.py harness-ports/tests/test_hermes_session_export.py | tail -1; bash scripts/pc_suite.sh set-id -- <the two files>
72 passed in 1.30s
2 files set=4e81d5d61609
$ grep -n "^_NAME\|^_WORD\|^_HEAD\|^_BEARER\|^_LINK\|^_VALUE\|^_CUT\|^def _redact_run\|^SECRET_PATTERNS" scripts/transcript_export.py
27:_NAME = (r"(?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Agent-Token|(?<![A-Za-z0-9])[A-Za-z0-9]*[_-]key|[_-]key|api[_-]?key"
32:_WORD = r"(?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Agent-Token|[_-]key|api[_-]?key|token|secret|password|passwd|Authorization)"
33:_HEAD = _WORD + r"[\"']?\s*[:=]"
35:_BEARER = r"(?-i:Bearer)\s+[A-Za-z0-9._\-]{8}"
36:_LINK = r"(?i:https?://[a-z0-9\-]+\.trycloudflare\.com)"
44:_VALUE = (r"(?:" + _WORD + r"[:=](?=" + _V + r")"
48:_CUT = re.compile(r"(" + _WORD + r"[:=])|(?:(?!" + _HEAD + r").)+", re.I | re.S)
51:def _redact_run(m):
56:SECRET_PATTERNS = [
```
