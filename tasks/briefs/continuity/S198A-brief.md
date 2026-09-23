# S198A — the transcript scrubber stops a value before the next secret name (AF-AP-157, task #198 increment A)

PIN: 9801fb5 (the origin head at dispatch; the boundary and its readers are byte-identical there and at the local head 172dbe2, blob ids in the premise block; re-measure them first).
LANE: s198a (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation). Honey `ultra` Lever-2: your report is DATA:
files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

WHY THIS LANE EXISTS (AF-AP-157). `scripts/transcript_export.py`'s `scrub` writes the chat digests that are committed and pushed to
origin (`transcripts/sandbox/`), and `harness-ports/bin/hermes-session-export.py` imports the same `scrub` by path for the PC lane
exports. Its credential-assignment rule takes a value of 8+ characters from `[^\s"'&,;]`, so a value can run over a following secret
NAME and its separator; the next rule never sees that name, and the name's value survives. Three of the five measured chained shapes
leak (premise block). Nothing in the committed transcripts is known to hold such a shape; this closes the class before one does.

BOUNDARY (exact): MODIFY `scripts/transcript_export.py` (S), `tests/test_transcript_export.py` (T); CREATE
`tasks/briefs/continuity/S198A-report.md` (write it incrementally from the start). READ-ONLY: `harness-ports/bin/hermes-session-export.py`
(P, it imports S by path; its tests are a gate), `harness-ports/tests/test_hermes_session_export.py`, `src/agent_factory/decisions/`
(the same class lives in `volatile.py`; increment B, not yours), everything else.

## The contract

1. **Premise first.** Re-measure the premise block. On a boundary mismatch, stop CONTRACT-INVALID and report what differs.
2. **The chained shapes close.** For the five premise shapes and your own chained shapes (both separators, quotes, spaces, a `token`
   head, upper and lower case, a head at the value's very end), no byte of any secret value survives `scrub`. A value that stops before
   a head is still redacted when it is a secret's value (decide how the rule's 8-character floor applies to a value cut short by a
   head, and state the reason); a name stays a name.
3. **No new exposure.** Every value byte the current `scrub` redacts stays redacted. Prove it with a differential between the PIN's S and
   yours over (a) every planted string in T, (b) a generator of your own with at least 100,000 inputs mixing names, separators, quotes
   and value alphabets, and (c) the raw session transcripts under `/root/.claude/projects/-home-user/*.jsonl`, run through
   `transcript_export.py` into scratch directories with each version. For (c), report ONLY counts and file:line locators of the lines
   that differ, never their text. If an old-scrubber output line holds a value the new one redacts, say so first in the report: the
   owner may need to rotate a credential.
4. **Order and cost.** The pattern order in `SECRET_PATTERNS` stays (the private-key block first, and the reason in its comment holds);
   state any change and why. Time adversarial inputs of 16k, 32k, 64k and 128k characters for every pattern you change, and paste the
   table with the per-doubling ratio; nothing may grow faster than linear.
5. **Tests (T).** The chained shapes as tests, each red at the PIN and green after (paste both runs); the negative controls (plain
   assignments, the existing planted classes, a name with no value, a short non-secret value) keep their PIN output. Pair any source-text
   pin with a behavioral control (AF-AP-80).
6. **Mutants (each on a scratch copy; never in the shared tree).** At least: m1 the PIN's value group back; m2 the head check covers `=`
   but not `:`; m3 the head check case-sensitive; m4 the quote before the separator dropped from the head; m5 the floor applied to a
   head-cut value (if your rule exempts it). Each must red a named test for the stated reason; paste the table.
7. **Gates.** T and P's tests twice with identical counts and the set id (`bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py
   harness-ports/tests/test_hermes_session_export.py`); `python3 scripts/lint_delta.py`.

Standing rules: touch ONLY the boundary files; report adjacent defects, never fix them. Never run git add, commit, stash, checkout,
restore, reset or clean. Other lanes are live in the tree (B11 on `proofs/S0-02/check_buzz_authz.py`, `proofs/S0-02/spec.json`,
`tests/test_s0_02_buzz_authz.py`; verifiers writing `tasks/briefs/laya/VERIFY-J1-0-R5-report.md` and
`tasks/briefs/laya/VERIFY-J1-1-R2-report.md`): never touch their files. Take no outward-facing action. Fake secrets only in tests and
reports (`QZJ8…`, `X4Z9…` style). Paste every count and timestamp from command output. A deviation from any contract line is
STOP-and-report, never a self-accepted change.

## PREMISE — MEASURED at authoring (2026-09-23 15:10Z, /home/user/agent-factory@172dbe2)

```
$ for f in <boundary + readers>; do echo "$(git rev-parse HEAD:$f) $f"; done
a47e0e5861c90912df2e3eee31a77b5bf66e1e7b scripts/transcript_export.py
8d1723beb46ecde73fdddf6a6048df32ff5635b5 tests/test_transcript_export.py
04326ece5b7a6ac59b76e2fc2a3d7ec6ff5b7c70 harness-ports/bin/hermes-session-export.py
0d7893bf5d2ec1a16a013bb06ca1d7cc0baf65ec harness-ports/tests/test_hermes_session_export.py
$ grep -n "SECRET_PATTERNS = \|re.compile\|^def scrub" scripts/transcript_export.py | cut -c1-110
24:SECRET_PATTERNS = [
29:    (re.compile(r"-----BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----.*?"
33:    (re.compile(r"((?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Agent-Token|(?<![A-Za-z0-9])[A-Za-z0-9]*[_-]key|api[_-]?key|tok
35:    (re.compile(r"(Bearer\s+)[A-Za-z0-9._\-]{8,}"), r"\1<redacted>"),
37:    (re.compile(r"\bsk-[A-Za-z0-9_\-]{12,}\b"), "sk-<redacted>"),
38:    (re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"), "gh<redacted>"),
39:    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}\b"), "AIza<redacted>"),
40:    (re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}\b"), "xox-<redacted>"),
42:    (re.compile(r"https?://[a-z0-9\-]+\.trycloudflare\.com[^\s)\"']*", re.I), "https://<bridge-link-redacted>"),
44:    (re.compile(r"\b[A-Za-z0-9_\-]{40,}\b"), "<opaque-redacted>"),
48:def scrub(text: str) -> str:
$ grep -n "transcript_export\|spec_from_file_location" harness-ports/bin/hermes-session-export.py | cut -c1-110
8:scripts/transcript_export.py is applied (imported by path so the two never drift).
23:SCRUB_SRC = HERE.parents[2] / "scripts" / "transcript_export.py"
27:    spec = importlib.util.spec_from_file_location("transcript_export", SCRUB_SRC)
$ python -m pytest -q -p no:cacheprovider tests/test_transcript_export.py harness-ports/tests/test_hermes_session_export.py | tail -1 (twice)
23 passed in 0.99s
23 passed in 1.01s
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py harness-ports/tests/test_hermes_session_export.py
2 files set=4e81d5d61609
$ python -c '<transcript_export.scrub over the five chained shapes>'
LEAK 'passwd=aAPI_KEY : X4Z92Q0X1ZX02Z71' -> 'passwd=<redacted> : X4Z92Q0X1ZX02Z71'
LEAK "token='_API_KEY = 6Z4Z02ZX6Z4Z" -> "token='<redacted> = 6Z4Z02ZX6Z4Z"
LEAK "password='-db_password: 62669Q3JJ88ZX5466" -> "password='<redacted> 62669Q3JJ88ZX5466"
ok   'key: service-API_KEY: QZJ8QZJ8QZJ8' -> 'key: service-API_KEY: <redacted>'
ok   'mask-PASSWORD=QZJ8QZJ8QZJ8;token: WQ7XWQ7XWQ7XWQ7X' -> 'mask-PASSWORD=<redacted>;token: <redacted>'
```
