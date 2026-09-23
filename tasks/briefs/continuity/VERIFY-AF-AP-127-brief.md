# VERIFY-AF-AP-127 — the targeted verify of the transcript exporters' scrub-then-cap fix (task #155)

PIN: 1978e55 (origin head at authoring). The fix landed as 2d10a2c (task #138, the coordinator's own work in the main loop); every
boundary file below is byte-identical at 2d10a2c and the PIN except `tests/test_ap_screen.py`, which ea18960 changed for AF-AP-132
(line numbering) — measured below.
LANE: verify-af-ap-127 (sandbox; agent `adversarial-verifier` on the D-054 pin, in the SHARED tree, no worktree isolation). Honey
`full`: line-bounded findings, evidence anchors, SOLID/UNSURE. Do NOT spawn subagents.

WHY THIS LANE EXISTS: the fix is GATED-PENDING-VERIFY (rule 0f). Its only gates were the coordinator's own tests (red on the old
exporters: `2 failed, 3 passed` and one failed check; green after) and its own screen sweep. No independent reviewer has attacked it.
Both exporters write files that are COMMITTED to the repository: `scripts/transcript_export.py` writes `transcripts/sandbox/` at every
push (`scripts/push_clean.sh:117-118`), and `harness-ports/bin/hermes-session-export.py` writes each PC lane's transcript at harvest
(`harness-ports/bin/pc-lane.sh:514`). A secret that survives the scrubber reaches origin.

THE CLAIMS UNDER TEST (from the commit 2d10a2c and the ledger note "AF-AP-127 EXPORTERS FIXED"):
- C1. `scripts/transcript_export.py` scrubs each turn's WHOLE text, then caps it (`scrub(txt)[:cap]`, line 82).
- C2. `harness-ports/bin/hermes-session-export.py` `_body` scrubs the whole text, then caps, then indents heading-shaped lines (line 41),
  for both message bodies (`cap`) and tool bodies (`tool_body_cap`).
- C3. The scrubber's first rule redacts a private-key block from BEGIN through END, or to the end of the text when END is missing
  (`scripts/transcript_export.py:25-28`), so no later rule leaves pieces of it behind.
- C4. The screen row AF-AP-127 in `.claude/hooks/edit-snapshot.py:183-187` fires on a scrub/redact of an already-capped slice and never
  on `scrub(x)[:cap]` or a suffix slice; it finds no other instance in `scripts/ harness-ports/bin/ src/ proofs/`.
- C5. Exposure before the fix: "0 key blocks and 0 cut-short stubs in 48,701 committed turn bodies".
- C6. Only more redaction, never less: re-exporting the committed transcripts with the new order changes no byte except by redacting.

ITEMS (report every observation, no severity filter; the predicate and the gate recommendation come at the end):
1. PREMISE: re-measure the block below on the PIN (blob ids, the two gate runs with their set id, the 14 checks). A mismatch that is not
   explained by a commit you can name stops the lane CONTRACT-INVALID.
2. C1/C2 — the order, per write path. Enumerate EVERY value either exporter writes to disk (bodies, headings, the session header lines:
   model, cwd, token counts, tool names, timestamps) with its file:line. For each: is it scrubbed, is it capped, in which order, and can it
   carry a secret? Then attack each capped path with a secret that straddles the cap, for every pattern class in `SECRET_PATTERNS`
   (fake values only), through the REAL `export()` of each exporter (the sandbox one on a synthetic JSONL transcript; the PC one on a
   synthetic SQLite DB with the real `sessions`/`messages` columns the exporter reads — its own test builds one). Paste the written bytes
   around each cap.
3. C3 — the private-key class. Build FAKE key blocks (random base64 bodies of the real line length; never a key any tool generated for
   use; never paste a body into the report, only its header and footer lines and the verdict) for every armored private-key family the
   project's own tools can print: OpenSSH (`ssh-keygen`), PKCS#1/PKCS#8/SEC1 and the encrypted PKCS#8 form (`openssl`), and GnuPG's
   armored secret-key export (`gpg --export-secret-keys --armor`; the project's governance flow uses gpg). Questions to answer by running
   `scrub` on each: which families are redacted whole? Which leave any body line on disk? And for each family: CRLF line ends; an indented
   block (as inside YAML or a quoted reply); a block inside a JSON string with literal `\n` escapes (a tool result that printed JSON); a
   block whose BEGIN line was lost upstream (a head/tail truncation that keeps only the body tail and END); two blocks in one text; a
   block split across two turns. Paste a table: shape → bytes left on disk (redacted count, surviving body lines count).
4. Cost of the new order. The scrubber now runs on the WHOLE text, not the capped text. Time `scrub` on large inputs through the real
   function (10 MB of mixed text; many `-----BEGIN ` lines without END; long runs of base64 characters; long runs of uppercase after
   `-----BEGIN `). Paste the timings. A super-linear case that would stall the push-time export or the lane harvest is a finding.
5. C4 — the screen row. Through the hook's REAL `AP_SCREEN` entry (as `tests/test_edit_snapshot_ap_screen.py:459` reaches it), run
   new shapes, never the landing's four: `scrub(x[0:cap])`, `scrub(x[:cap], flags)`, `scrub(obj.get("t")[:cap])`, a two-step
   `t = x[:cap]` then `scrub(t)`, a helper that truncates (`scrub(truncate(x, n))`, `textwrap.shorten`), `redact(x[:])`, a shell
   pipeline that caps before it scrubs (`head -c N … | … scrub`). For each: fires or not, and whether it should. The screen is
   advisory (it informs, never blocks): a miss is a finding with its reproduction, not automatically a blocker.
6. C4's sweep, reproduced by an INDEPENDENT instrument: an AST walk over every first-party `.py` (scripts, harness-ports, src, proofs,
   .claude/hooks; tests listed separately) for a call to a redaction-verb function whose argument is a slice with an upper bound (any
   spelling), plus a shell sweep of `*.sh` for a cap (`head -c`, `cut -c`, `${v:0:N}`, `tail -c`) that feeds a scrub. Paste every hit
   and classify it. Then the wider question, reported as ADJACENT (outside this fix): any path that writes capped text into a COMMITTED
   file with no scrub at all.
7. C5 — reproduce the exposure count on the PIN: the number of committed turn bodies and the method for "cut-short stub" (a secret
   prefix at a body's cap boundary, cut below its pattern's minimum). If you cannot reproduce 48,701 or its method, say what you measured
   instead.
8. C6 — run the CURRENT `scrub` over every committed file under `transcripts/` (`git ls-files transcripts`) and paste the count of files
   where `scrub(text) != text`. Classify every difference: an unredacted secret-shaped string committed (a real exposure: report it by
   file:line and pattern class, NEVER paste the value), or scrub not being idempotent on its own output (say which pattern), or content
   exported before a scrubber change and not re-exported since.
9. Test strength. In scratch copies under `/tmp/vap127/` only: revert each exporter's order separately; drop the private-key rule; move
   it after the opaque rule; drop its `\Z` alternative; drop `re.S`; swap `_body`'s cap and indent order. For each mutant: does the
   suite red, and on which test? Each mutant compiles (`python3 -m py_compile`) and its suite collects (AF-AP-78); before you count a
   kill, run the killing test on the UNMUTATED tree and paste that it passes (AF-AP-138). A survivor is a finding.

BOUNDARY: CREATE `tasks/briefs/continuity/VERIFY-AF-AP-127-report.md` and write it incrementally. Nothing else in the repository.
Scratch, basetemps, synthetic transcripts and DBs, fake key blocks and mutants live under `/tmp/vap127/` and are removed when you are
done (the sandbox had 1.4 GB free at authoring; measured below). pytest: `-p no:cacheprovider --basetemp=/tmp/vap127/bt<n>`, removed
after each run. Other sandbox agents work in this tree on disjoint files (`proofs/S0-02/`, `proofs/S0-05/`, their tests,
`tasks/briefs/s0-02-support/`, `tasks/briefs/s0-05-support/`, `tasks/briefs/laya/`, `tasks/briefs/hermes-repin/`,
`upstream.lock.yaml`, `docs/HARNESS-PORTS.md`, `tests/test_upstream_lock_lane_runtime.py`): never touch, run or revert them. Never
run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push`. Never run either exporter with its default
output path (that rewrites committed transcripts): always pass `--out` under `/tmp/vap127/`. No outward-facing action; no PC or bridge
use. Secrets in fixtures are FAKE strings only.

AUTHORIZATION: this is defensive work on the owner's own repository: planting fake secrets and fake key blocks to prove the scrubber
removes them before a byte reaches a committed file.

CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
`scripts/lane_context.sh -q 'where is text capped before or after a secret scrub' -s scrub -s _body -s export -s turns -o /tmp/vap127/pack.md scripts/transcript_export.py harness-ports/bin/hermes-session-export.py .claude/hooks/edit-snapshot.py`.

PREDICATE: a finding blocks only if it is contract-mapped (C1-C6), reproduced through the real exporter or the real hook entry,
materially effective (a secret byte reaches a written file, or a claim C1-C6 is false as stated), with a concrete discriminator, and
in-boundary for the fix (the two exporters, the scrubber, the screen row). Everything else is a follow-up. Emit ONE GATE RECOMMENDATION
per component: (a) the sandbox exporter's order, (b) the PC exporter's order, (c) the private-key class, (d) the screen row — each
`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`. The coordinator owns the final gate.

Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/continuity/VERIFY-AF-AP-127-report.md --root .` (no `--map`
flags; cite full repo-relative paths); apply its `fix:` hints for at most three rounds, then paste and finish. The report ends with
DISCREPANCIES and NOT-done.

## PREMISE — MEASURED at authoring (2026-09-23 09:25Z-09:31Z, sandbox @ 1978e55 + the local commits c69c07b and f77563f, neither touching this boundary)
```
$ date -u; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
Wed Sep 23 09:25:24 UTC 2026
1978e55
$ for f in <boundary>; do blob at 2d10a2c vs origin head; done
b2887443b443 b2887443b443 SAME scripts/transcript_export.py
04326ece5b7a 04326ece5b7a SAME harness-ports/bin/hermes-session-export.py
a6691647faa5 a6691647faa5 SAME .claude/hooks/edit-snapshot.py
cef778a1fd02 cef778a1fd02 SAME tests/test_transcript_export.py
40da66cc04bd 40da66cc04bd SAME harness-ports/tests/test_hermes_session_export.py
25eba0cc4912 25eba0cc4912 SAME tests/test_edit_snapshot_ap_screen.py
29f572185384 767ab95d7585 CHANGED tests/test_ap_screen.py
$ git log --format="%h %s" 2d10a2c..1978e55 -- <boundary> | cut -c1-120
ea18960 report_lint and ap_screen number lines on "\n" only (AF-AP-132): str.splitlines() read J1-2-R1's ledger.py two l
$ git diff --quiet 1978e55 -- <boundary> && echo tree == head on the boundary
tree == 1978e55 on the boundary
$ grep -n "scrub(\|redact(\|\[:cap\]\|:cap\]" scripts/transcript_export.py harness-ports/bin/hermes-session-export.py
scripts/transcript_export.py:44:def scrub(text: str) -> str:
scripts/transcript_export.py:82:        days.setdefault(day, []).append(f"## {role} @ {ts}\n\n{scrub(txt)[:cap]}\n")
harness-ports/bin/hermes-session-export.py:26:def _scrub():
harness-ports/bin/hermes-session-export.py:41:    return _HEADING_SHAPED.sub(r" \1", scrub(text)[:cap])
harness-ports/bin/hermes-session-export.py:47:    scrub = _scrub()
$ python3 -c "<the AF-AP-127 screen row over the first-party trees (py + sh)>"
  .claude/hooks/edit-snapshot.py:185: # exporters did `scrub(text[:cap])`; the J1-1 contract truncated inside normalize before redact.
  .claude/hooks/edit-snapshot.py:187: "a redaction/scrub applied to an already-capped slice (`scrub(x[:cap])`) — a secret straddling the cap falls b
screen AF-AP-127: 2 hit(s) over 175 tracked files (scripts harness-ports src proofs .claude/hooks .github; .py/.sh/extensionless)
$ git ls-files transcripts | wc -l; grep -rlE "BEGIN [A-Z0-9 ]*PRIVATE KEY" transcripts | wc -l; grep -roh "<private-key-redacted>" transcripts | wc -l
120
0
0
$ git log -1 --format="%h %ad %s" --date=format:"%m-%d %H:%M" -- transcripts
1978e55 09-23 09:13 transcripts: scrubbed sandbox chat digests (2026-09-23)
$ grep -n 'transcript_export\|hermes-session-export' scripts/*.sh harness-ports/bin/*.sh scripts/hooks/*
scripts/push_clean.sh:117:if [ "${TRANSCRIPT_SYNC:-1}" = "1" ] && [ -f scripts/transcript_export.py ]; then
scripts/push_clean.sh:118:  if python3 scripts/transcript_export.py --out transcripts/sandbox >/dev/null 2>&1 \
harness-ports/bin/pc-lane.sh:514:    python3 "$AF_REPO/harness-ports/bin/hermes-session-export.py" --db "$HDB" --session "$SID" \
$ for i in 1 2; do /root/venv-agent-factory/bin/python -m pytest tests/test_transcript_export.py tests/test_edit_snapshot_ap_screen.py tests/test_ap_screen.py -q -p no:cacheprovider --basetemp=/tmp/vap/bt$i | tail -1; done
108 passed in 0.44s
108 passed in 0.61s
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py tests/test_edit_snapshot_ap_screen.py tests/test_ap_screen.py
3 files set=7fa2348f21fe
$ python3 harness-ports/tests/test_hermes_session_export.py | tail -1
test_hermes_session_export: 14 checks passed
$ grep -n '^def test' tests/test_transcript_export.py
52:def test_secrets_never_reach_disk_and_text_survives(tmp_path):
69:def test_idempotent_and_deterministic(tmp_path):
90:def test_secret_straddling_the_cap_never_reaches_disk(tmp_path):
106:def test_private_key_block_is_scrubbed_whole_or_to_the_end(tmp_path):
120:def test_missing_transcript_exits_3(tmp_path):
$ df -h /tmp | tail -1
/dev/vda        252G   36G  1.4G  97% /
```
The landing's count was `107 passed` over the same three files; `tests/test_ap_screen.py` gained one test in ea18960, hence 108.
