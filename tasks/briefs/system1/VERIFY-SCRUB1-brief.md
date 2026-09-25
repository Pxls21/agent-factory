# VERIFY-SCRUB1: attack the transcript scrubber's glued-key rules and its value gate (task #301; SCRUB1 = task #280)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/VERIFY-SCRUB1-report.md`
(write it incrementally). Target: the commit whose subject starts "SCRUB1 landed (task #280" (origin 49bf75e); PIN 2dbf1f4
(origin). Contract: `tasks/briefs/system1/SCRUB1-brief.md` (items 1-4), the lane's report beside it, and AF-AP-224 in
`docs/INCIDENT-LOG.md`.

Authorization, for the record: this is defensive work on the owner's own system. `scripts/transcript_export.py` scrubs the
chat digests that are committed and pushed; its screens keep credentials out of them. Every key and value you build is a
fake made at run time (`secrets.token_hex`), never a real one, and nothing you print may contain a matched span.

## WHY

SCRUB1 changed the rules that decide what reaches origin in `transcripts/sandbox/`, and added a gate that refuses to write
when a known secret value survives the rules. It landed on the coordinator's re-run of the lane's own gate, with no
independent pass (orchestration 0f: GATED-PENDING-VERIFY). A defect here puts a credential on origin. Grade against the
contract, never the builder's own cases.

## WHAT TO ATTACK (report everything; no severity filter)

1. **The four rules** (`sk-`, the `gh?_` family, `AIza`, `xox?-`). Build your own hostile shapes: keys glued after `_`,
   `__`, `-`, `.`, `/`, `:`, `=`, a quote, a backslash, a JSON escape (`\n`, `\t`, `\"`, `\u00XX` just before the key),
   a non-ASCII letter, a digit, a letter; keys at line start and end; inside URLs; the right side too (a key followed by
   `_`, a non-ASCII letter, a quote). Through the REAL functions (`scrub`, `scrub_payload`, `scrub_strict`) and through
   `export()` end to end on a fixture transcript whose records copy the SHAPE of real ones (fake content): which text does
   each writer scrub (the decoded string or the raw JSON), and does each outcome match the contract? The other direction:
   ordinary text the rules must not redact (the lane's words and your own: identifiers, prose, `task-notification`).
2. **The value gate**, only through fixture sources: `export(..., sources=<your tuple>)`, `known_values(<your tuple>)`,
   and `main()` only in process with `KNOWN_VALUE_SOURCES` replaced the way the committed tests replace it. A planted fake
   value refuses: exit 4 from `main()`, nothing written (no output directory, no partial or temporary file); the refusal
   lines carry names and counts only. Then: a value split across two days' files; the value in encoded forms (base64,
   URL-encoded, JSON-escaped, hex, another case): which pass the gate, and does the contract want them caught? A missing
   source is skipped with one line; an unreadable one refuses; `TYPESAFE_BASE_URL` is skipped by name in its own source
   only (the same value under another name counts); a URL's host counts; a value under the length floor. Is `export()` the
   only writer in this file?
3. **The byte-identity claims.** The lane says the 18 digests from this session's main transcript come out byte-identical
   under the new exporter and the one before it (49bf75e^), and that 0 of 6,196 stored Laya records change. Reproduce both:
   the two exporters over the same transcript into two scratch directories (the new one with `sources=()`, so no real
   source is ever read; the old one has no gate), compared by file set and sha256; every stored record re-scrubbed with the old and the new rules, the changed ones
   counted (the lane's 6,196 are the `state` fields of the stored records, 1,652 strings and 4,544 `{query, chunk}`
   dicts, its report section 6; `labels.jsonl` holds 5,301 lines: say how the two relate). The dataset rebuild is optional.
   Report the counts, and say how the committed `transcripts/sandbox/` files compare.
4. **Mutation.** Re-run the lane's harness (`<scratch>/scrub1/mutate.py`, adapted to a copy of the PIN in your scratch) and
   add your own mutants on the four rules and the gate; classify each by a FAILED test, never an error (AF-AP-223).
5. **Siblings.** Confirm or refute the registered follow-ups with fake inputs through the real code: #291 (push_clean hides a
   refused sync: read the code and reproduce in a scratch copy with a fake exporter; never run push_clean itself), #292 (the
   right side of the rules and the JSON-escape context), #293 (the other writers of scrubbed text have no value gate: list
   each writer and whether a fake known value planted in its input reaches its output).
6. Anything else in the same file (the private-key block, the credential assignment, Bearer, the bridge link, the opaque
   token rule): report what you find, with fake inputs.

## RULES

No git writes in this tree; no PC bridge; no outward-facing action; touch no tracked file (scratch only, under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/`, at most 300 MB, deleted as you go; the
disk is shared, 1.9G free at authoring). **Never read a real secret source:** not `.pc-bridge.env`, `/root/.codiv/api.env`,
`/root/.config/session-export/pseudonym.key`, any `*.env`, `~/.config/qwen-*`, nor the `GH_TOKEN` and `GITHUB_TOKEN`
variables; the exporter's default sources are never exercised, in process or by the CLI. The transcripts hold secrets: read
them in process only and print ids and counts, never a record's text. Print a matched span only as a masked shape (the
prefix, the length, the character classes). Test counts are pasted from `scripts/test_summary.sh`; stamps from `date -u`.
Long commands in one foreground call; kill by pid, never by name. End with a GATE RECOMMENDATION (MERGE-READY /
MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID) and the blocking predicate you applied.

## PREMISE — MEASURED at authoring (2026-09-25 22:0xZ, the sandbox clone at 2dbf1f4)

```
$ git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
2dbf1f4
$ git show --stat --format='%h %s' 49bf75e | cut -c1-120
49bf75e SCRUB1 landed (task #280, AF-AP-224; GATED-PENDING-VERIFY): the four provider-key rules of transcript_export tak

 docs/INCIDENT-LOG.md                               |   4 +-
 .../2026-09-25-recorded/dataset-manifest.json      |   2 +-
 scripts/transcript_export.py                       | 115 +++++++-
 tasks/briefs/system1/SCRUB1-report.md              | 323 +++++++++++++++++++++
 tests/test_transcript_export.py                    | 203 +++++++++++++
 todo/BUILD-TASKLIST.md                             |   1 +
 6 files changed, 632 insertions(+), 16 deletions(-)
$ git log --format=%h 49bf75e..origin/claude/soundbox-kit-migration-iz1jwf -- scripts/transcript_export.py scripts/known_values_check.py tests/test_transcript_export.py | wc -l
0
$ grep -n -E 'sk-\[A-Za|ghp\|gho|AIza\[|xox\[abprs|^KNOWN_VALUE_SOURCES|^def (export|known_values|value_hits|main)' scripts/transcript_export.py | cut -c1-110
84:    (re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_\-]{12,}\b"), "sk-<redacted>"),
85:    (re.compile(r"(?<![A-Za-z0-9])(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"), "gh<redacted>"),
86:    (re.compile(r"(?<![A-Za-z0-9])AIza[0-9A-Za-z_\-]{30,}\b"), "AIza<redacted>"),
87:    (re.compile(r"(?<![A-Za-z0-9])xox[abprs]-[A-Za-z0-9\-]{10,}\b"), "xox-<redacted>"),
237:KNOWN_VALUE_SOURCES = (
250:def known_values(sources=KNOWN_VALUE_SOURCES):
284:def value_hits(datas, values):
296:def export(transcript: str, out: str, cap: int, sources=KNOWN_VALUE_SOURCES) -> list:
319:def main() -> int:
$ ls transcripts/sandbox/ | wc -l; du -sh transcripts/sandbox | cut -f1
18
3.5M
$ wc -l < docs/research/findings/laya-ft-labels/2026-09-25-recorded/labels.jsonl
5301
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/scrub1/
m-digests.json
m-main.json
m-root2.json
m-sub.json
measure.py
mutate.py
probe_fixture.py
probe_other.py
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py 2>&1 | tail -1
1 files set=73755bb9fbbf
$ bash scripts/test_summary.sh tests/test_transcript_export.py   (run at authoring)
pytest-summary: 174 passed in 2.44s
```

A question for you, not a fact: the committed tests replace the value gate's sources; is there any path through
`main()` or `export()` that a test cannot reach without the real sources, and does that path matter?
