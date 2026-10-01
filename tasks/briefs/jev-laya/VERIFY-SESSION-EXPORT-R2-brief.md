# VERIFY-SESSION-EXPORT-R2 (task #439): issue #78's pre-export items

**PIN:** `cc488cec8b8f8a09919a7266de482e6c03f0c346`, origin's head after the push. The two landing commits are
`1effb39c` (issue #78's items) and `f69f54cb` (the known-values fix); the head commit adds chat digests only. The
shared tree's head moves with the coordinator's records, so every premise line below names the PIN itself.

## PREMISE — MEASURED at authoring (2026-10-01 16:0xZ, /home/user/agent-factory@cc488cec)

Re-measure each line as your first item; stop CONTRACT-INVALID on any difference.

```
$ git rev-parse cc488cec8b8f8a09919a7266de482e6c03f0c346^{commit}
cc488cec8b8f8a09919a7266de482e6c03f0c346
$ git log --format='%h %s' ee6ad873e6b765cac349a1b7ca074283da7e021c..cc488cec8b8f8a09919a7266de482e6c03f0c346
cc488cec transcripts: scrubbed sandbox chat digests (2026-10-01)
f69f54cb known-values check: a compressed target is read unpacked, one it cannot read whole is refused (AF-AP-255, task #439)
1effb39c session export: issue #78's pre-export items (task #439): R1-F-1, the canary marker, R1-F-2's tests, R1-F-7
$ git diff --stat ee6ad873e6b765cac349a1b7ca074283da7e021c cc488cec8b8f8a09919a7266de482e6c03f0c346 -- scripts/transcript_export.py scripts/session_export.py scripts/known_values_check.py tests/test_transcript_export.py tests/test_session_export.py tests/test_known_values_check.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
 .../2026-09-25-recorded/dataset-manifest.json      |  2 +-
 scripts/known_values_check.py                      | 73 +++++++++++++++--
 scripts/session_export.py                          | 55 +++++++++----
 scripts/transcript_export.py                       |  5 +-
 tests/test_known_values_check.py                   | 71 ++++++++++++++++
 tests/test_session_export.py                       | 95 ++++++++++++++++++++++
 tests/test_transcript_export.py                    | 16 ++++
 7 files changed, 294 insertions(+), 23 deletions(-)
$ for f in scripts/transcript_export.py scripts/session_export.py scripts/known_values_check.py tests/test_transcript_export.py tests/test_session_export.py tests/test_known_values_check.py; do printf '%s  %s\n' "$(git show cc488cec8b8f8a09919a7266de482e6c03f0c346:$f | sha256sum | cut -c1-64)" "$f"; done
5fedf0385ffedf1267f0ccaa4c88a4e214ac80002983a1d67827925afe83b48c  scripts/transcript_export.py
2613b8889aabfac98101f4e46bd3f6aeacbeac5e990176ae984c4b1165580a3f  scripts/session_export.py
37bc7b174adcd603e19e76babb6d608c08884087caad6a303694c5a3efd73ca6  scripts/known_values_check.py
1075f75afe6fb633e2e398b60e9d54a12686a17ad3f78e4fc65a935ba5a8ac33  tests/test_transcript_export.py
5758cf5322abe8f6dc4052af910d04f53c3098f041f78d09d22f1764e6d30b9f  tests/test_session_export.py
75c0884992d9774376ffef5a2a27262da305bf334a530882245eebdd7cdcf565  tests/test_known_values_check.py
$ git show cc488cec8b8f8a09919a7266de482e6c03f0c346:scripts/transcript_export.py | grep -n 'def _committed\|return s in keep or'
221:def _committed(s, keep):
226:    return s in keep or bool(m) and s[m.end():] in keep and not (m.end() > 12 and _keylike(s[:m.end() - 1]))
$ git show cc488cec8b8f8a09919a7266de482e6c03f0c346:scripts/session_export.py | grep -n 'def mark_canaries\|^CHAT_DIGESTS\|def repo_runs\|def export_source\|mark = a.mark_own_canaries\|--mark-own-canaries", action\|output_sha256'
184:def mark_canaries(text, counts):
712:CHAT_DIGESTS = b"transcripts/"
715:def repo_runs(repo, commit):
798:def export_source(root, src, offset, out_dir, expect_sha, key, archives, mark=False):
822:    return {"src": src, "offset": offset, "input_sha256": sha, "output": src + ".xz", "output_sha256": sha256_file(dest),
967:    mark = a.mark_own_canaries or prior.get("own_canaries") == "marked"       # AF-AP-213; a rerun keeps its mode
1085:    e.add_argument("--mark-own-canaries", action="store_true")
$ git show cc488cec8b8f8a09919a7266de482e6c03f0c346:scripts/known_values_check.py | grep -n '^UNPACK\|^REFUSE\|^LAYERS\|^class Unreadable\|^def _unpack\|^def _content\|except Unreadable'
47:UNPACK = ((b"\xfd7zXZ\x00", "xz", lzma.LZMADecompressor), (b"\x1f\x8b", "gzip", lambda: zlib.decompressobj(31)),
49:REFUSE = ((0, b"\x28\xb5\x2f\xfd", "zstd"), (0, b"PK\x03\x04", "zip"), (0, b"7z\xbc\xaf\x27\x1c", "7z"),
51:LAYERS = 8
58:class Unreadable(Exception):
139:def _unpack(make, data):
152:def _content(fp, data):
231:    except Unreadable as e:
$ git show cc488cec8b8f8a09919a7266de482e6c03f0c346:docs/INCIDENT-LOG.md | grep -c '^| AF-AP-255 |'
1
$ git diff --quiet cc488cec8b8f8a09919a7266de482e6c03f0c346 -- scripts/transcript_export.py scripts/session_export.py scripts/known_values_check.py tests/test_transcript_export.py tests/test_session_export.py tests/test_known_values_check.py && echo 'the shared tree holds the PIN bytes of the six files'
the shared tree holds the PIN bytes of the six files
$ python3 -m pytest --collect-only -q -p no:cacheprovider tests/test_transcript_export.py tests/test_session_export.py tests/test_known_values_check.py | tail -1 | sed -E 's/ in [0-9.]+s.*//'
287 tests collected
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py tests/test_session_export.py tests/test_known_values_check.py
3 files set=cb32e901cbed
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-session-export/h/ | wc -l
27
```

**You are the original verifier of the session exporter**, resumed: VERIFY-SESSION-EXPORT and its R1 re-verify
(2026-09-25, `tasks/briefs/jev-laya/VERIFY-SESSION-EXPORT-report.md`). Your R1 round recommended
MERGE-READY-WITH-FOLLOWUPS; the coordinator filed the follow-ups as issue #78. This round attacks the landing of
issue #78's four "before the next export" items, and the coordinator's fix of the known-values check (AF-AP-255).
Your scratch harness is still on disk
(`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-session-export/h/`); its worktree
copy and pin are stale, so point it at a fresh copy of the PIN below. Many things changed since your round (SCRUB2 on
2026-09-26 among them): re-read the code at the PIN, never your memory of it.

**Defensive authorization (CLAUDE.md, safeguard-flag routing):** this is defensive testing of the owner's own system.
The fake secrets, canaries and leak shapes you build are test fixtures for our own scrubber.

## The goal

Grade the landing against the contract below through the real CLI and the real code at the PIN, and return a GATE
RECOMMENDATION (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID). The coordinator owns the gate.
Report every observation with no severity filter, then apply the strict blocking predicate (contract-mapped, reproduced
through the real path, materially effective, a concrete discriminator, in the boundary). The real export ships to the
owner's PC only after your verdict.

## The contract the landing claims (the two landing commits' messages have the full reasoning)

1. **R1-F-1:** `_committed` in `scripts/transcript_export.py` keeps `NAME=<committed run>` only when the NAME is not
   token-like: a NAME of 12 or more characters with a letter and a digit makes the run uncommitted, so `scrub_strict`
   redacts it. It is your R1.8 candidate, verbatim.
2. **AF-AP-213:** `scripts/session_export.py export --mark-own-canaries` turns each whole test canary into
   `[canary:<name>]` after the scrub, on each event's JSON line, and counts it per source (`canaries_marked`) and in the
   totals; the manifest names the mode (`own_canaries`: `marked` or `counted`); an `--offsets` rerun takes the mode its
   manifest names. Off by default; the pseudonym key's printed forms are never marked; the gate still counts them and
   any canary the marking did not take whole.
3. **R1-F-2:** the lane tests now kill your 8 widening mutants (X1, X2a, X2b, X3, X4a, X4b, X4c, X6).
4. **R1-F-7, the coordinator's decision:** `repo_runs` leaves out every file under the top-level `transcripts/`
   (`CHAT_DIGESTS`); a nested `transcripts/` folder and a root `transcripts.md` stay in the set.
5. The DSV2 record's manifest (`docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json`) was
   regenerated by its tool; only the scrubber's hash moved.
6. **AF-AP-255, found by the coordinator:** `scripts/known_values_check.py` reads a compressed target unpacked: xz, gzip
   and bzip2, found by the first bytes, never the file's name; every stream in a file (the one-call `lzma` and `bz2`
   functions drop bytes after a stream, silently); up to eight layers. It refuses with exit 2 what it cannot read whole:
   zstd, zip, 7z, lz4, a tar archive, a stream cut short, bytes after a stream that are not a stream, nine layers. A line
   names the unpacked layers, and the total counts the bytes searched. The 2026-09-25 check of the real export read its
   `.xz` bytes and passed (`docs/INCIDENT-LOG.md`, AF-AP-255); the real export ships only after this check passes.

## Questions the coordinator wants answered (attack them; add your own)

- Can the marking hide a value that is not a whole canary, or take part of a real secret with it? The landing argues
  that a canary in an event's JSON line is exactly a canary in one of the event's strings (no canary character is
  escaped by JSON or used as its separator). Try to break that argument.
- Can the marking change what the gate sees for a real secret glued to a canary (before or after it), compared with
  the same text unmarked? Is any secret shape the gate counted before the marking lost after it?
- Does the R1-F-7 filter remove anything the strict pass or the pseudonymizer still needed, and does it change how the
  standalone `gate` command reads an export made before this landing (it rebuilds the set from the manifest's repo and
  commit with today's code)?
- On the real transcripts, with a scratch key only: how many strict results change under R1-F-1 (your R1.6 counted 105
  NAME= keeps), and how many runs leave the committed set under R1-F-7? Counts only.
- Do your own new mutants of the marking and the filter survive the lane tests?
- The fixed checker: can a target hide text from it and still read as a pass (a format it neither unpacks nor refuses,
  a first-bytes test that misreads a format, a stream that unpacks in part)? Does it refuse any file our own tools
  write? Do your mutants of the unpacking survive `tests/test_known_values_check.py`?
- The export's gate reads each output through `lzma.open`, which also drops bytes after a stream (measured
  2026-10-01), and never compares an output with its manifest's `output_sha256`. Can stray bytes reach a shipped
  export, and would anything see them?

## Standing rules

- Real transcripts: counts and shapes only, never their text; a scratch key that your harness makes, never the real
  pseudonym key; never read or print a secret file or an environment secret.
- **Never print a canary or any 8-character window of one** (AF-AP-213 is that exact class: a printed canary lands in
  this session's transcript, which the next real export reads). Name canaries; never show values.
- No outward action (no PR, comment, push or publish); no subagents; no edit to the shared tree (scratch copies only:
  `git archive <PIN> | tar -x`, at most one mutant tree at a time, deleted after its run; the disk has about 4 GB free).
- Run each long gate in ONE foreground call (a backgrounded run never wakes you).
- Write your report incrementally to `tasks/briefs/jev-laya/VERIFY-SESSION-EXPORT-R2-report.md`. If the harness refuses
  a report-file write, return the rest of the report as the text of your final message; never work around the refusal.
