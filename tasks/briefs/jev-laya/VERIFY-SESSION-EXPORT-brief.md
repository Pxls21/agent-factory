# VERIFY-SESSION-EXPORT: attack the session export, its scrubber and its shipper (task #252; orchestration 0f; D-031)

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: db1de1c (the origin head that carries the harvest). Report:
`tasks/briefs/jev-laya/VERIFY-SESSION-EXPORT-report.md` (write it incrementally from the start). Do NOT spawn subagents. Report EVERY
meaningful observation with no severity filter, then apply the blocking predicate (contract-mapped; reproduced through the real
production path; materially effective; a concrete discriminator; in-boundary) and end with a GATE RECOMMENDATION: MERGE-READY,
MERGE-READY-WITH-FOLLOWUPS, NOT-READY or CONTRACT-INVALID. The coordinator owns the final gate. Authorization: this is defensive work
on the owner's own data pipeline; secret-shaped strings in your fixtures are FAKE canaries you invent.

## WHY

The export turns every session transcript into the training stream for the RWKV student and the Jev pipelines (D-086, D-087), and
it ships to the owner's PC. The scrubber is a security boundary: a secret that survives it is copied into a corpus that lives on,
and a scrub that is too wide destroys the data. The builder's own gate is not verification (orchestration 0f).

## CONTRACT (frozen)

`tasks/briefs/jev-laya/SESSION-EXPORT-brief.md` with AMENDMENT 1 (G1 to G6) and AMENDMENT 2 (every project folder, a converter that
resumes from a byte offset, pruner archives as events). The builder's report: `tasks/briefs/jev-laya/SESSION-EXPORT-report.md`
(its deviations, its self-attack and its NOT-done: judge each against the contract).

## ATTACK SURFACES (new shapes; never only the builder's own cases)

1. **Secrets that survive.** Build fixture transcripts (production record shapes, FAKE canaries) and run the real exporter on them:
   a short token (under 40 characters) echoed by a command that names no secret file; a secret split across two lines or two
   events; base64-, URL- and JSON-escaped secrets; a credential inside a URL (`https://user:pass@host`); a secret inside a tool
   INPUT, a thinking block, a hook output, a notification, a `file_change` diff and a pruner archive; a secret-bearing path named
   another way (`$HOME/.pc-bridge.env`, `~/.codiv/api.env`, a relative path, a quoted or globbed path, a symlink). Count survivors
   with a check independent of the builder's gate (your own fixture canaries by value).
2. **Scrubbing too much.** Measure what the payload pass removes from ordinary engineering text (commit ids, sha256 values, long
   test names, file paths): a scrub that eats the evidence a Jev needs is a data defect. The coordinator saw the plain `scrub` mark
   long commit and test names as opaque in reports: is the export's pass the same?
3. **Pseudonyms.** Stable across files and runs; keyed (a different key gives different pseudonyms); the key never in any output;
   no pseudonym for a value that a named secret rule already removed (the builder's G6 mutant).
4. **The resumable converter.** Split each fixture at every byte offset (or a dense sample): two parts from the returned offset give
   the same events as one pass; a line appended during a run is not half-read.
5. **Completeness.** Every record and attachment type in the real transcripts maps to an event or a counted drop (the builder
   surveyed 38 attachment types; check the counts add up against the input).
6. **The shipper** (`scripts/ship_to_pc.py`), against a fake bridge only: path traversal on the remote side, a chunk replayed from
   another file, a manifest sent early, a partial rerun after a crash between chunks, a remote file changed after a verified chunk.
7. **Regressions.** The chat export stays byte-identical on its fixtures; every other importer of `scrub` behaves as before.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Every finding with file:line, the command and its output, and the blocking predicate applied item by item.
3. A mutation table of NEW mutants (each red or surviving, with the test that catches it or the gap it shows).
4. The three test files at the PIN, twice, in a clean worktree: `bash scripts/test_summary.sh tests/test_transcript_export.py
   tests/test_session_export.py tests/test_ship_to_pc.py` (paste both summaries and the set id).
5. NOT-done.

## VENUE AND STANDING RULES

Work in a clean detached worktree at the PIN (`git -C /home/user/agent-factory worktree add --detach <scratch>/wt db1de1c`, the
only git write you make; remove it at the end). Scratch: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/
verify-session-export/` (the disk has about 2 GB free; stay under 500 MB). No network; no PC bridge; never run the shipper against
the real bridge; no outward-facing action. Never read a real secret file (`.pc-bridge.env`, `/root/.codiv/api.env`, the pseudonym
key, any `*.env`), never search the real transcripts for keys, tokens or passwords, and never print a secret: the coordinator ran the
known-values check (below). You may run the real exporter over the real transcripts into your scratch for counts only. FAKE strings
for every canary. Check your report with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` (0 expected).

## PREMISE — MEASURED at authoring (2026-09-25 06:2xZ, the sandbox)

```
$ git show db1de1c:<file> | sha256sum | cut -c1-16
395db6ddefe0e7fc  scripts/transcript_export.py
a402db33b776d1a7  tests/test_transcript_export.py
7bf26338e88c7bcc  scripts/session_export.py
05f83f7a0636c5dd  tests/test_session_export.py
39c88510acb21ee2  scripts/ship_to_pc.py
37cc6c042aea1771  tests/test_ship_to_pc.py
$ bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py   (the shared tree)
pytest-summary: 141 passed in 12.88s
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py
3 files set=6dde7977ceba
$ grep -n 'def scrub(\|def scrub_payload\|def scrub_strict' scripts/transcript_export.py
85:def scrub(text: str) -> str:
110:def scrub_payload(text: str, opaque=None) -> str:
140:def scrub_strict(text: str, opaque=None) -> str:
$ (the builder's run 1 summary line, from its report)
export 2026-09-25T05:47:40Z: 317 sources, 1178943962 bytes read, 38706220 bytes written, 329.3 s
$ (the coordinator's known-values check over the built export: real values read in process, counts only)
export files scanned: 317 | secrets checked: 4
  codiv:TYPESAFE_API_KEY  full=0 prefix16=0     pc-bridge.env:PC_BRIDGE_TOKEN  full=0 prefix16=0     pseudonym.key(hex)  full=0 prefix16=0
  codiv:TYPESAFE_BASE_URL full=23 prefix16=23   (a service base URL, not a secret)
```

Questions for you, not facts: does any secret shape survive the export that the 13 gate patterns cannot see? Does the payload pass
remove ordinary evidence (ids, hashes, test names) a Jev would need?
