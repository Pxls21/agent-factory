# SESSION-EXPORT-R1: the one focused repair of the session export (task #252; D-031; VERIFY-SESSION-EXPORT)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/jev-laya/SESSION-EXPORT-R1-report.md`
(write it incrementally from the start). This is the ONLY repair round the export gets (D-031). PIN: db1de1c (the harvest's origin
commit; the boundary files are unchanged since).

## WHY

The export is the training stream for the RWKV student and the Jev pipelines (D-086, D-087), and it leaves the sandbox for the
owner's PC. The verifier (`tasks/briefs/jev-laya/VERIFY-SESSION-EXPORT-report.md`) found a named credential in a DOUBLE-quoted value
survives once the exporter has written it as JSON (F-1, NOT-READY). The shipped copy was deleted from the PC. The scrubber also
destroys evidence a Jev needs: 40.7% of the values the opaque rule pseudonymizes are the repo's own test names (F-2), and the strict
pass redacts repo paths in results of calls that only source a secret file (F-3).

## CONTRACT

`tasks/briefs/jev-laya/SESSION-EXPORT-brief.md` with AMENDMENTS 1 and 2, plus AMENDMENT 3 below (the coordinator's ruling on the
verifier's two contract defects).

**AMENDMENT 3 (coordinator, 2026-09-25 07:3xZ).** A run that occurs verbatim in a file tracked by the repo at the export's commit is
not pseudonymized by the opaque rule and not redacted by the strict pass. Committed text is not a secret: the repo's hooks keep
secrets out of it, and a secret that did reach it is already exposed there. Build the set once per export from the tracked files'
contents at that commit (every run of the opaque rule's minimum length and shape). The named secret rules still run first and still
apply to such a run (a committed FAKE fixture token under a credential name is still redacted). Rejected: exempting identifier and
slug SHAPES (lowercase words joined by `_`, `-`, `/`, `.`): a UUID-shaped or word-shaped secret would pass.

## THE REPAIR (each item with its own FAKE-canary tests through the real CLI)

- **R-1 (F-1, the blocker).** Credentials behind a JSON-escaped quote are redacted: start from the verifier's candidate rule
  (`scratchpad/verify-session-export/fixrepo/scripts/transcript_export.py`, the `escaped-credential` rule and its gate name), and cover
  the verifier's 7 escaped shapes (its harness `scratchpad/verify-session-export/h/`). A 44-character value under a credential name is
  REDACTED, never pseudonymized (G6). The gate counts the new shape.
- **R-2 (F-4).** Drop the result of any call whose command names the pseudonym key path (as the D-2 denylist does), so a hex dump of
  the key cannot come out.
- **R-3 (the cheap part of F-5 to F-7).** Named rules for: a lowercase `bearer <token>`; `curl -u user:pass`; assignments to names that
  end in `PASS`, `PASSWD` or `PASSWORD`; a credential-only userinfo `scheme://token@host`; the tail of a URL password after a raw `@`
  (F-6). Path forms the denylist misses (F-7): `$HOME/`, `~/`, `./`, a doubled `//`, a relative path, a quoted path, a glob that matches
  a secret path. The rest of F-5 (short bare tokens in prose, URL-encoded values) stays a follow-up: say so.
- **R-4 (AMENDMENT 3).** The repo-verbatim exemption for the opaque rule and the strict pass.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Red first: each new canary test fails on the PIN's code and passes on yours (paste both).
3. The real export rebuilt twice (byte-identical), with its summary line; the leak gate 0 with the new rules; the verifier's harness
   re-run with 0 leaks for its escaped shapes and F-4's dump.
4. AMENDMENT 3's effect, counts only: the opaque rule's values by category before and after (the verifier's split: 109,328 values; test
   names 40.7%, kebab slugs 27.3%, path components 4.3%, hex ids 19.0%), and the strict pass's redactions of repo paths before and after.
5. Mutants: one per new rule, each red on a named test.
6. `bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py`, twice, with the
   set id; the chat export byte-identical on its fixtures; pyflakes rc 0; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` 0 on every file.
7. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `scripts/transcript_export.py`, `tests/test_transcript_export.py`, `scripts/session_export.py`, `tests/test_session_export.py`.
CREATE: your report. READ: everything else. Not `scripts/ship_to_pc.py` or its tests (F-8 is a follow-up). The export output goes to
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/session-export/` (replace the old run there; keep one
determinism rerun beside it and delete it at the end). The DSV2 record's manifest hashes `scripts/transcript_export.py`: the coordinator
regenerates it at harvest; do not touch it.

## STANDING RULES

No network; no PC bridge; never ship; no git writes; no outward-facing action. Never read a real secret file (`.pc-bridge.env`,
`/root/.codiv/api.env`, the pseudonym key, any `*.env`), never search the real transcripts for keys, tokens or passwords, never print a
secret; every canary is a FAKE string you invent. Counts over the real export are fine. A run of about 5.5 minutes: run it detached and
wait with `tail --pid`, or split it, under the 600 s tool cap.

## PREMISE — MEASURED at authoring (2026-09-25 07:3xZ, the sandbox)

```
$ git show db1de1c:<file> | sha256sum | cut -c1-16    (unchanged in the shared tree since)
395db6ddefe0e7fc  scripts/transcript_export.py
a402db33b776d1a7  tests/test_transcript_export.py
7bf26338e88c7bcc  scripts/session_export.py
05f83f7a0636c5dd  tests/test_session_export.py
$ bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py
pytest-summary: 141 passed in 12.88s
$ diff <(git show db1de1c:scripts/transcript_export.py) scratchpad/verify-session-export/fixrepo/scripts/transcript_export.py
101a102,105   (the candidate escaped-credential rule)
116c116       (its gate name added)
$ (the verifier's findings, its report sections 2, 5, 7 and 8)
F-1: 7 of 7 escaped shapes leak through the real CLI; 145 such values in the real export, 42 distinct
F-2: the opaque rule takes 109,328 values: test names 40.7%, kebab slugs 27.3%, path components 4.3%, hex ids 19.0%
F-3: 1,190 of 2,096 secret-path Bash calls only source .pc-bridge.env; their results get the strict pass
```
