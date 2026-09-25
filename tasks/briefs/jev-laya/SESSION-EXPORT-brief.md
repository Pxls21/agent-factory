# SESSION-EXPORT: every session transcript as a scrubbed stream of calls and results, for the RWKV student (D-084, D-086)

Role: code-implementer (sandbox, Opus 5.5; the transcripts exist only in this sandbox). PIN: see the premise block. Report:
`tasks/briefs/jev-laya/SESSION-EXPORT-report.md` (write it incrementally from the start). Do NOT spawn subagents. Touch ONLY the
files in the boundary; report adjacent defects, never fix them.

## WHY

The owner (2026-09-25, D-086): "especially for rwkv training we need as much of the outputs as possible ... by the end of this all
the data should be usable since the rwkv version will be processing session data alongside layla". The RWKV student reads the
session as ONE stream: its state after a prefix carries what the prefix shows (the files read, the edits made, the earlier
outputs). Measured on the main session (premise block): 614 of 652 Edits touch a file read or written earlier in the stream, and a
re-run test command with no edit in between repeats its outcome 17 of 18 times. So the tool calls AND their results are the
training input, and the outcome the harness records at each call is its first label. `scripts/transcript_export.py` exports chat
text only; it drops tool calls and results by design. The session also touches secret files (premise counts), so this export is a
security boundary: the scrubber is tested on every payload shape BEFORE any export runs.

## GOAL

A deterministic exporter that turns every transcript under `/root/.claude/projects/-home-user/` into an ordered, scrubbed event
stream (one compressed file per transcript) plus a manifest, and a shipper that sends the export to the PC in verified chunks.
You build and test both. The coordinator runs the shipper: you never contact the bridge.

## BOUNDARY

- MODIFY `scripts/transcript_export.py` and `tests/test_transcript_export.py`: extend `scrub` (or add a stricter pass beside it)
  for tool payloads. Every existing test stays green unchanged, and the chat export's output on the existing test fixtures stays
  byte-identical.
- CREATE `scripts/session_export.py` and `tests/test_session_export.py`: the exporter.
- CREATE `scripts/ship_to_pc.py` and `tests/test_ship_to_pc.py`: the shipper, tested against a fake bridge in a temp tree
  (`tests/test_pc_sh.py` is the pattern: the real bridge must never be reachable from a test).
- OUTPUT (never committed): `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/session-export/`.
  The disk has about 2.7 GB free: stream everything, never hold a whole transcript in memory, and keep the output under 1 GB.
- READ: `docs/research/findings/laya-ft-data/SESSION-DECISIONS-2026-09-25.md` sections 1 and 2 (the record shapes and the
  harness fields that hold outcomes), `scripts/hiccup_scan.py` (a streaming reader of these transcripts), `scripts/chat_tail.py`,
  `scripts/pc_bridge_exec.py` (the bridge protocol), `tests/test_pc_sh.py`, `PC-BRIDGE.md` section "Protocol".

## PINNED DECISIONS (a conflict with the tree is a STOP-and-report)

- **D-1 The event schema (copy it; do not redesign).** One JSON object per line, in source order:
  `{"seq": int, "src": str, "line": int, "ts": str|null, "role": str, "kind": str, "tool": str|null, "call_id": str|null,
  "text": str, "truncated": {"kept_head": int, "kept_tail": int, "dropped": int}|null, "outcome": object|null}`.
  `seq` counts from 0 within one transcript; `src` is the transcript path relative to `/root/.claude/projects/-home-user/`;
  `line` is its JSONL line number. `role`: `owner`, `coordinator`, `agent`, `tool`, `hook` or `system` (define the mapping per
  transcript type: in the main session the human turns are the owner's; in a subagent transcript the first user turn is the
  coordinator's prompt; state your rule and test it on real record shapes). `kind`: `text`, `thinking`, `tool_call`,
  `tool_result`, `hook`, `notification` or `summary`. For a `tool_call`, `text` is the call's input as canonical JSON (scrubbed).
  `outcome`, on `tool_result` events only: the fields the harness wrote, never a regex over prose: `is_error`, the exit code from
  a leading `Exit code N` line, `timed_out_after_ms`, `denial_kind`; on stop-hook summaries: `hook_errors`. Leave out anything
  whose field you cannot name in a real record (AF-AP-42: never an invented shape).
- **D-2 Scrubbing.** Every `text` passes the extended scrubber. Beside it, a path denylist: a Read, Write or Edit whose path
  matches `\.pc-bridge\.env`, any `*.env` file, `qwen-builder/api-key`, `qwen-jev/omniroute\.key`, `\.codiv/api\.env` or a file
  under `\.hermes/profiles/` keeps its event, but its input and its result become `[payload dropped: secret path]`. A Bash command
  that names such a path keeps its scrubbed command, and its result goes through the strict pass. Thinking blocks: keep them only
  if they are present in plain text in the record, scrubbed like any text (state what the records hold).
- **D-3 Size.** Cap each event's `text` at 32,768 characters: keep the first 24,576 and the last 8,192 and record the rest in
  `truncated`. Report how many events hit the cap, per kind.
- **D-4 Determinism.** Fix every source's byte offset at the start (the live transcripts keep growing) and read each source only
  up to it; the manifest records the offset and the sha256 of the bytes read. The same offsets and code give byte-identical
  output: prove it with two runs.
- **D-5 Files.** One `.jsonl.xz` per source transcript (python `lzma`, preset 6; zstd is not installed), and
  `manifest.json`: the export id (its UTC start), the code's sha256, and per source the offset, the input sha256, the output
  sha256 and size, the event count per kind, the capped and dropped counts.
- **D-6 The leak gate.** After the export, decompress every output as a stream and scan it for the scrubber's own secret shapes
  and for the test canaries; it must find 0, and it prints counts per pattern only, never a match. A test builds a synthetic
  transcript with a FAKE secret in every payload shape (a Write of a `.env` file, a Bash result that prints an env line, a curl
  config with the token header, a bridge link, a `Bearer` header, a PEM block, a GitHub-token shape, a key file's content through
  Read) and asserts that none survives the export.
- **D-7 The shipper.** `ship_to_pc.py <export dir> <remote dir>` reads the bridge URL and token from `.pc-bridge.env` in process
  (never argv, never printed) and sends each file as base64 chunks of at most 96,000 characters per call: the bridge runs one
  shell command per call, and one argument is limited to 131,072 bytes. Up to 4 calls in flight; each chunk verified by sha256 on
  the PC; the file reassembled there and its sha256 checked against the manifest; a rerun resumes from the last verified chunk;
  the manifest ships last. Tests against a fake bridge: a dropped chunk resumes, a corrupted chunk is refused, the final sha256
  matches, and a wrong token is refused.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; STOP and report on a mismatch that matters to the design.
2. The scrubber: the new tests red first, then green; the existing tests unchanged; the chat export byte-identical on its fixtures.
3. The export over every transcript: events per kind, capped events per kind, dropped payloads, bytes read against bytes written,
   wall time. Two runs over the same offsets give identical output sha256s.
4. The leak gate: 0 matches (the counts per pattern pasted), and the canary test green.
5. The shipper tests.
6. Mutants on scratch copies, each red on a named test: one scrub rule removed (a canary survives); the denylist emptied; the cap
   off; the offset ignored (read to the end of the file).
7. Gates: `bash scripts/test_summary.sh` on the three test files, twice (paste both summaries), `scripts/pc_suite.sh set-id --`
   the same files; pyflakes on every file you write; `python3 scripts/no_laya_in_gates.py`; the separator check on every file you
   write (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`, 0 expected).

## STANDING RULES

No network; no PC bridge (the coordinator ships); no outward-facing action. Never print a secret; never search the records for
keys, tokens or passwords (the scrub runs in process, and the leak gate prints counts only). FAKE strings in every test. No git
writes of any kind in `/home/user/agent-factory` (the coordinator commits; another lane, DSV2, holds its own files in the same
tree). Long commands in ONE foreground call. A pytest `--basetemp` parent must exist first.

## PREMISE — MEASURED at authoring (2026-09-25 02:2xZ, the sandbox; origin at the push that carries this brief)

```
$ du -sh /root/.claude/projects/-home-user; find /root/.claude/projects/-home-user -name '*.jsonl' | awk -F/ '{print NF}' | sort | uniq -c
1.3G	/root/.claude/projects/-home-user
     38 10
      1 6
    257 8
$ (a streaming count over all 296 transcripts: tool calls whose input names a secret path; counts only)
pc-bridge.env          Read/Write/Edit     3  Bash  1699
dotenv                 Read/Write/Edit     5  Bash  1680
qwen-builder api-key   Read/Write/Edit     0  Bash    38
qwen-jev key           Read/Write/Edit     0  Bash     6
codiv api.env          Read/Write/Edit     1  Bash     8
hermes profile         Read/Write/Edit     0  Bash   323
$ (the coordinator's cause-in-prefix probe over the main session file, 704,448,851 bytes)
EDIT {'n': 652, 'prior': 614, 'err': 11, 'err_prior': 9}
TEST {'n': 824, 'prev': 40, 'same_noedit': 17, 'noedit': 18, 'same_edit': 15, 'edit': 22}
$ grep -n '^def \|^SECRET_PATTERNS' scripts/transcript_export.py
51:def _redact_run(m):
56:SECRET_PATTERNS = [
85:def scrub(text: str) -> str:
91:def turns(path):
116:def export(transcript: str, out: str, cap: int) -> list:
134:def main() -> int:
$ python3 -c "import zstandard"; which zstd xz gzip; df -h /root | tail -1
ModuleNotFoundError: No module named 'zstandard'
/usr/bin/xz
/usr/bin/gzip
/dev/vda        252G   35G  2.7G  93% /
```

Questions for you, not facts: which harness fields in these records hold an outcome beyond `is_error` (name each with a real
record's line); how many events and bytes the whole export holds after the cap; whether thinking blocks carry plain text.
