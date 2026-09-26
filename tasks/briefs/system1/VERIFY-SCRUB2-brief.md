# VERIFY-SCRUB2: attack the scrubber hardening before it counts as verified (task #303; SCRUB2 = task #292)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/VERIFY-SCRUB2-report.md`
(write it incrementally). Target: the commit whose subject starts "SCRUB2 landed (task #292" (origin cdbc1b8, pushed with its local id
unchanged; the origin tip at authoring). Contract: `tasks/briefs/system1/SCRUB2-brief.md`
(items 1-8), the lane's report beside it, VERIFY-SCRUB1's report (its findings F1-F3, F8-F10, F12-F14, F17 are what SCRUB2 set out
to close), and AF-AP-224 in `docs/INCIDENT-LOG.md`.

Authorization, for the record: this is defensive work on the owner's own system. `scripts/transcript_export.py` scrubs the chat
digests that are committed and pushed. Every key and value you build is a fake made at run time (`secrets.token_hex`), and nothing
you print may contain a matched span.

## WHY

SCRUB2 changed the rules that decide what reaches origin, the value gate's reader, and three consumers that pinned the old rule
set (the coordinator applied those at landing). It landed on the coordinator's re-run of the lane's gates, with no independent
pass (orchestration 0f: GATED-PENDING-VERIFY). Grade against the contract and VERIFY-SCRUB1's findings, never the builder's cases.

## WHAT TO ATTACK (report everything; no severity filter)

1. **The anchors** (`_KEY_L`, `_KEY_R`, the opaque rule's `\b`-or-ASCII ends): your own hostile shapes in both directions,
   through `scrub`, `scrub_payload`, `scrub_strict`, `export()` and `session_export.convert()` end to end, and the other writers
   (`chat_find`, `hiccup_scan`, `jev`): keys before and after non-ASCII letters, digits, `_`, quotes, every JSON escape (and
   escaped backslashes before a letter), `\uXXXX`, ANSI colour codes; ordinary text that must stay (identifiers, prose, paths).
   Is every redaction the PIN made still made (no loss)?
2. **The five new shapes** (Cookie, Authorization after a scheme, `pwd`, `credentials`, the malformed PEM): false negatives
   (other spellings, spacing, quoting, JSON) and false positives on ordinary text; the lane measured its choices on this session's
   transcripts: re-check the numbers that decided them.
3. **Timing:** hostile inputs for every new or changed rule (many BEGIN lines with no END, long runs of names, spaces, quotes,
   escapes), through the real functions, with timings; say which grow faster than linearly.
4. **The value gate:** no default sources left anywhere (can any path reach the real sources without `main()`?); `_read_regular`
   on a FIFO, a directory, a symlink to either, a character device, a very large file, a file that changes under the read; the
   `<malformed line N>` numbering; an unknown kind; the refusal lines carry names and counts only. Use fixture sources only.
5. **Test isolation:** reproduce the lane's claim that no committed test opens a real source (an `openat` trace over the scrubber's
   test file and set A, inside VERIFY-SCRUB1's masking runner `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/masked.sh` with fakes, so a real source is never read
   even by accident); can a test still reach one by a subprocess or an import path?
6. **The consumer patches:** `session_export.PATTERN_NAMES` against the patterns in order (does any test catch a misaligned
   list, or would the next rule change turn the leak gate's exemptions off in silence?); the two test patches (the oracle's copy
   of the opaque rule; the gate total; the third glued key).
7. **The Laya lock:** reproduce the pre-fit comparison (the lane's `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/scrub2/laya2.py` or your own) and the manifest's
   code hash.
8. **Mutation** on the new code; a kill is a FAILED test, never an error (AF-AP-223).

## RULES

No git writes in this tree; no PC bridge; no outward-facing action; touch no tracked file (scratch only, under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2/`, at most 300 MB, deleted as you go; the disk is shared, 1.5G free at authoring). **Never read a real secret
source** (`.pc-bridge.env`, `/root/.codiv/api.env`, `/root/.config/session-export/pseudonym.key`, any `*.env`, `~/.config/qwen-*`,
the GH_TOKEN and GITHUB_TOKEN variables): the exporter's real run is the coordinator's. The transcripts hold secrets: read them in
process only and print ids and counts, never a record's text; print a matched span only as a masked shape. The tree also holds
S1-RATE's uncommitted, held files (`scripts/hook_context.py`, `.claude/hooks/system1-context.py`, `tests/test_session_hooks.py`,
`tests/test_system1_context.py`, `scripts/s1_scores.py`, `tests/test_s1_rate.py`): never edit or revert them. Test counts are pasted
from `scripts/test_summary.sh`; stamps from `date -u`. Long commands in one foreground call; kill by pid only. End with a GATE
RECOMMENDATION (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID) and the blocking predicate you applied.

## PREMISE — MEASURED at authoring (2026-09-26 01:4xZ, the sandbox tree)

```
$ git log -1 --format='%h %s' HEAD | cut -c1-110
cdbc1b8 SCRUB2 landed (task #292 closed, GATED-PENDING-VERIFY): provider keys anchored against non-ASCII glue 
$ git show --stat --format='' HEAD | tail -13
 .../2026-09-25-recorded/dataset-manifest.json      |   2 +-
 scripts/known_values_check.py                      |  52 ++-
 scripts/session_export.py                          |   7 +-
 scripts/transcript_export.py                       |  77 +++-
 tasks/briefs/system1/SCRUB2-report.md              | 402 ++++++++++++++++++
 tests/test_jev_locate_echo.py                      |   4 +-
 tests/test_known_values_check.py                   |  38 +-
 tests/test_session_export.py                       |   5 +-
 tests/test_transcript_export.py                    | 459 ++++++++++++++++++++-
 todo/BUILD-TASKLIST.md                             |   1 +
 wiki/topics/live-state.md                          |   6 +
 11 files changed, 995 insertions(+), 58 deletions(-)
$ grep -n -E '^_KEY_L|^_KEY_R|opaque-redacted|private-key-redacted|cookie\)|authorization\)|\(\?i:pwd\)|\(\?i:credentials\)' scripts/transcript_export.py | cut -c1-120
67:_KEY_L = r"(?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])|(?<=\\u[0-9A-Fa-f]{4}))"
68:_KEY_R = r"(?![A-Za-z0-9])"
77:     "<private-key-redacted>"),
83:     "<private-key-redacted>"),
95:    (re.compile(r"((?i:\b(?:set-)?cookie)[\"']?\s*:\s*[\"']?)(?=[^\r\n\"']*=[^\s;\"']{8})[^\r\n\"']+"), r"\1<redacted
98:    (re.compile(r"((?i:authorization)[\"']?\s*:\s*[\"']?(?i:token|basic|bearer|digest|negotiate|ntlm|apikey|api-key|k
103:    (re.compile(r"((?<![A-Za-z0-9])(?i:pwd)[\"']?\s*[:=]\s*[\"']?)(?![/~.$\\])(?=[^\s\"'&,;]{8})[^\s\"'&,;]+"),
105:    (re.compile(r"((?<![A-Za-z0-9])(?i:credentials)(?:[\"']\s*:|\s*=)\s*[\"']?)(?![/~.$\\])(?=[^\s\"'&,;]{8})"
125:    (re.compile(r"(?:\b|(?a:\b))[A-Za-z0-9_\-]{40,}(?:\b|(?a:\b))"), "<opaque-redacted>"),
148:    (re.compile(r"((?i:authorization)(?:\\*[\"'])?\s*:\s*(?:\\*[\"'])?(?i:basic)\s+)[A-Za-z0-9+/]{8,}=*"), r"\1<reda
160:    (re.compile(r"((?i:authorization)(?:\\*[\"'])?\s*[:=]\s*(?:\\*[\"'])?(?i:bearer)\s+"
179:OPAQUE_MARK = "<opaque-redacted>"      # the marker of scrub's coarse opaque-run rule
203:_KEY_RUN = re.compile(r"[A-Za-z0-9_\-+/=]{20,}")
$ grep -n -E '^def (known_values|export|main)|^def _read_regular|^class NotRegularFile|ENV_NAME = ' scripts/transcript_export.py scripts/known_values_check.py
scripts/transcript_export.py:286:def known_values(sources):
scripts/transcript_export.py:335:def export(transcript: str, out: str, cap: int, *, sources) -> list:
scripts/transcript_export.py:358:def main(argv=None) -> int:
scripts/known_values_check.py:35:ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
scripts/known_values_check.py:38:class NotRegularFile(OSError):
scripts/known_values_check.py:42:def _read_regular(path):
scripts/known_values_check.py:119:def main(argv=None):
$ python3 -c "import sys; sys.path.insert(0,'scripts'); import session_export as se; print(len(se.gate_patterns()), len(se.PATTERN_NAMES))"
23 23
$ (coordinator's landing gate, a clean git worktree of HEAD before the commit plus the eight files)
pytest-summary: 746 passed, 1 skipped in 114.40s (0:01:54)   set A, 15 files set=271f9e77620b
pytest-summary: 746 passed, 1 skipped in 113.28s (0:01:53)
pytest-summary: 74 passed in 319.69s (0:05:19)   tests/test_laya_ft.py tests/test_laya_systemone_server.py
the new exporter with the real sources into scratch: rc=0, 19 files, stderr empty (run by the coordinator)
```

A question for you, not a fact: the lane rejected `pwd` as a plain credential name because 16 Laya v2 items would change; does
the landed `pwd` rule (a non-path value only) change any of those items, and does the pre-fit check prove it?
