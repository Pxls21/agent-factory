# VERIFY-AF-AP-127-R1 + REPIN-a-R2 — one targeted verify of two focused repairs (task #182)

PIN: c84f161 (origin head at authoring). Both repairs are on origin: AF-AP-127-R1 = 9932f34, REPIN-a-R2 = 9c991a2 (post-push
SHAs). The shared tree's HEAD is one local commit ahead (5090671, J1-0-R4), which touches no boundary file (measured below).
LANE: verify-182 (sandbox; agent `adversarial-verifier` on the D-054 pin, in the SHARED tree, no worktree isolation). Honey
`full`: line-bounded findings, evidence anchors, SOLID/UNSURE. Do NOT spawn subagents.

WHY THIS LANE EXISTS: both repairs are GATED-PENDING-VERIFY (rule 0f). Their only gates were the coordinator's own tests, its own
five mutants (A) and its own negative control (B). No independent reviewer has attacked either.
- A, AF-AP-127-R1 (task #177): the ONE focused repair (D-031) of VERIFY-AF-AP-127 F1. The scrubber's private-key rule now matches
  `[A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?` in BEGIN and END (`scripts/transcript_export.py:29-31`), so GnuPG armor is redacted
  whole. The PC exporter loads the same `scrub` from that file (`harness-ports/bin/hermes-session-export.py:23` `SCRUB_SRC`). Both
  exporters write COMMITTED files: `transcripts/sandbox/` at every push (`scripts/push_clean.sh:117-118`), and each PC lane's
  transcript at harvest (`harness-ports/bin/pc-lane.sh:514`). A key byte that survives reaches origin.
- B, REPIN-a-R2 (task #178): the coordinator's contract amendment of R3(c) after VERIFY-REPIN-a-R1 returned F1+F2 as a
  CONTRACT-DEFECT. The words changed, the count did not: "110 PC lane directories whose latest launch was at or after 2026-09-08
  14:22:00Z (98 with a report; brief.md--0000000 never ran Hermes)", at three sites (`upstream.lock.yaml:173`,
  `tests/test_upstream_lock_lane_runtime.py:58`, and the Rule line of `tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md:8`).

CONTRACT (frozen):
- A: VERIFY-AF-AP-127's grading in `tasks/briefs/continuity/VERIFY-AF-AP-127-report.md` (its finding inventory rows F1, F8a, F8d
  and its item 3 family list) + claim C3 of `tasks/briefs/continuity/VERIFY-AF-AP-127-brief.md` ("the scrubber's first rule redacts
  a private-key block from BEGIN through END, or to the end of the text when END is missing, so no later rule leaves pieces of it
  behind") + the repair's own claims in the message of 9932f34 (`git show -s 9932f34`).
- B: R3 of `tasks/briefs/hermes-repin/REPIN-a-R1-brief.md` ("the `verified:` value says what each piece proves") with R3(c) as
  amended by 9c991a2 (`git show -s 9c991a2`), graded against VERIFY-REPIN-a-R1 F1/F2 in
  `tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md`.
- KNOWN follow-ups, already filed (issue #41 for A, issue #42 for B): VERIFY-AF-AP-127 F2-F6, F8b, F8c, F9, F11-F15 and
  VERIFY-REPIN-a-R1 F3-F21, as their reports' inventory tables state them. Report anything you see, but mark a finding KNOWN when
  it is one of these, and do not re-derive them.

ITEMS (report every observation, no severity filter; the predicate and the gate recommendation come at the end):
1. PREMISE: re-measure the block below on the PIN and in the tree (blob ids, line counts, the two diffs, the seams, the gates with
   their set ids, the three B strings). A mismatch that no commit you can name explains stops the lane CONTRACT-INVALID for the
   component it touches; say which.
2. A — the armor families, through BOTH real exporters. Enumerate the armored labels from primary sources in this sandbox: OpenSSL's
   `PEM_STRING_*` in `/usr/include/openssl/pem.h`, the labels in the `gpg` binary (`strings /usr/bin/gpg | grep -- 'PGP '`), and the
   OpenSSH label (`ssh-keygen` is absent here, F15; take it from the format and say so). For every label that names private or
   secret key material, build blocks with FAKE random base64 bodies of the real line length, or with a THROWAWAY key generated for
   this test only under `/tmp/vr182/` (a temporary `GNUPGHOME`, `openssl genpkey` to a file there): never a key made for use, never
   a body pasted into the report (header, footer and verdict only), all removed at the end. Run each through the real `export()` of
   `scripts/transcript_export.py` (a synthetic JSONL transcript) and of `harness-ports/bin/hermes-session-export.py` (a synthetic
   SQLite DB with the real `sessions`/`messages` columns, as its test builds; message bodies AND tool bodies under
   `--tool-body-cap`). Shapes, per family: plain; CRLF; indented (YAML, a quoted reply); inside a JSON string with literal `\n`
   escapes (the service-account shape `"private_key": "-----BEGIN PRIVATE KEY-----\n…"`); a Python repr with `\\n`; armor headers
   (`Proc-Type:`/`DEK-Info:`, GnuPG `Comment:`); two blocks with prose between them (does the prose survive?); a BEGIN whose END
   carries a different label; a second BEGIN before the first END; a label with extra inner spaces. Paste a table: family × shape →
   body lines left on disk, placeholders written, the text after the block kept or lost.
3. A — what the widened rule touches that is NOT a secret. Every armored label from item 2's enumeration that names public or
   non-secret material (`PUBLIC KEY`, `CERTIFICATE`, `PGP PUBLIC KEY BLOCK`, `PGP SIGNATURE`, `PGP MESSAGE`, `PGP SIGNED MESSAGE`,
   parameters, CRLs, and any other the sources list): through the real `scrub`, untouched or redacted? Then the corpus: run the
   CURRENT `scrub` over every committed file under `transcripts/` (`git ls-files transcripts`) and paste the count of files where
   `scrub(text) != text`. Classify each difference: an unredacted key or secret committed (a real exposure: report it by file:line
   and class, NEVER paste the value), prose that names a BEGIN label with no END (the F13 class: count the characters lost), or a
   file exported before this rule and not re-exported since. Deployment fact for this item: the PC clone ran 012d455b, which lacks
   9932f34, until the coordinator fast-forwarded it to c84f161 at 11:2xZ (measured below); a PC transcript harvested before then was
   exported with the old key rule.
4. A — the rule's FIRST position (F8a's property). New prefixes before a BEGIN line, never the landing's `secret: `: `password=`,
   `token: "`, `Authorization: `, `"private_key": "`, an `sk-` or `ghp_` string on the same line, a 40-character opaque run on the
   line before. For each: does any body byte reach disk? Is there any later rule that can still split a block the key rule already
   replaced (read `SECRET_PATTERNS` in order, `scripts/transcript_export.py:24-44`)?
5. A — the PC exporter's binding to the rule. `harness-ports/bin/hermes-session-export.py` loads `scrub` from
   `scripts/transcript_export.py` by path (`SCRUB_SRC`, line 23). What does it do when that file is missing, unreadable, or raises
   on import: fail closed, or export unscrubbed text? Reproduce each in a scratch copy under `/tmp/vr182/`, never in the shared tree.
6. A — test strength. In scratch copies under `/tmp/vr182/` only: first re-run the landing's five mutants (the old rule; a required
   type word `[A-Z0-9 ]+`; no `SECRET`; END without `BLOCK`; the key rule moved last) and paste which test kills each. Then new
   ones, never the landing's: a greedy `.*`; `[A-Z ]*` (no digits: is any real family with a digit in its label tested?);
   `(?: BLOCK)?` dropped from BEGIN only; `\Z` replaced by `$`; `re.S` dropped; the key rule moved to SECOND position (after the
   credential rule, not last); `(?:PRIVATE|SECRET|PUBLIC)` (an over-redaction mutant: does anything notice?); the placeholder text
   changed. For each: py_compile rc 0 and the suite collects (AF-AP-78); before you count a kill, run the killing test on the
   UNMUTATED tree and paste that it passes (AF-AP-138). A survivor is a finding; say whether it is a security gap or an
   over-redaction gap.
7. A — cost of the widened rule. Time the real `scrub` against the rule at 9932f34^ on adversarial inputs: 10 MB of mixed text;
   many `-----BEGIN ` lines followed by long runs of `[A-Z0-9 ]` that never end in `PRIVATE KEY`; one open block followed by many
   `-----END ` lines with long uppercase runs; 100,000 BEGIN lines with no END. Paste the timings. A super-linear case that would
   stall the push-time export or a lane harvest is a finding.
8. B — the words are one string at three sites. Parse `upstream.lock.yaml` and show piece (c) of the `verified:` value equals the
   test constant byte for byte; show the record's Rule line says the same thing. Reproduce the landing's negative control in a
   scratch copy (the lock with the OLD words, the NEW test: the landing says `2 failed, 14 passed`). Then a one-character change to
   the lock's piece (c), a reordered piece, and the constant's trailing `, ` dropped: which test reds, by which message?
9. B — are the words TRUE for the method? The record dates each lane directory by `prompt.md`'s mtime, else `brief.md`'s.
   Measured at authoring: `harness-ports/bin/pc-lane.sh` is the only writer of `prompt.md` (`:217-218` truncates it at each start,
   `:222-245` append to it in that start), and a resumed attempt writes `prompt.attempt<N>.md` instead (`:319-322`). Is the mtime the
   LATEST start of `pc-lane.sh`? Is a start that is refused before `:218` (the report check at `:102-109`, the PIN refusal at
   `:165-171`) a launch, and does it move the mtime? Which code writes `brief.md` (`scripts/pc_lane.sh`), and is its mtime also a
   latest-launch time? Is `brief.md--0000000 never ran Hermes` true by code, and where did that directory come from? The PC
   directories are NOT re-measured (no bridge use): attack by consistency with the committed record and the committed code.
10. B — does piece (c) say what it proves, and nothing it does not? VERIFY-REPIN-a-R1's own proposed wording also named the five
   lanes whose FIRST attempts ran on the old SQLite runtime and were relaunched at 14:2xZ (record rows 21-25: `pc-verify-b5j`,
   `pc-verify-n5i`, `pc-b2`, `pc-verify-m2`, `pc-verify-g2`, latest launch 14:25:47Z-14:31:16Z; task #51; the incident-log entry for
   2026-09-08 14:2xZ). The amendment dropped that clause. Read the whole `verified:` value and what the `hermes-agent-lane-runtime`
   entry claims. Does the omission change what a reader concludes about b3399c1 (a claim that flatters by omission is a hollow green
   in prose under the NO STUBS rule), or is "latest launch" enough for the claim the entry makes? Grade it either way, with the
   reason.
11. GATES, each command with its output and the set id (`bash scripts/pc_suite.sh set-id -- <files>`), run twice where it is a
   pytest set: `tests/test_transcript_export.py`; `python3 harness-ports/tests/test_hermes_session_export.py`;
   `tests/test_upstream_lock_lane_runtime.py tests/test_s0_12_license_sbom.py`; `python3 scripts/validate-ledger integrity --root .`
   (the ten PRESENT rows as at authoring, S0-02 and S0-05 ABSENT).

BOUNDARY: CREATE `tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md` and write it incrementally from the start.
Nothing else in the repository. Scratch, basetemps, synthetic transcripts and DBs, fake or throwaway keys and mutants live under
`/tmp/vr182/` and are removed when you are done (the sandbox had 1.4 GB free at authoring). pytest:
`-p no:cacheprovider --basetemp=/tmp/vr182/bt<n>` (create the parent first), removed after each run. Other sandbox agents work in
this tree on disjoint files: `proofs/S0-02/`, `proofs/S0-05/` (E3-R1 holds `proofs/S0-05/tools/pc/run_s0_05_units.sh`), their
tests (`tests/test_s0_05_egress.py`), `tasks/briefs/s0-02-support/`, `tasks/briefs/s0-05-support/`, `tasks/briefs/laya/`,
`scripts/no_laya_in_gates.py`, `tests/test_no_laya_in_gates.py`, `scripts/gate_files.txt`: never touch, run or revert them. Never
run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push`. Never run either exporter with its
default output path (that rewrites committed transcripts): always pass `--out` under `/tmp/vr182/`. No outward-facing action; no PC
or bridge use.

AUTHORIZATION: this is defensive work on the owner's own repository: planting fake secrets, fake key blocks and throwaway test keys
to prove the scrubber removes them before a byte reaches a committed file.

CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
`scripts/lane_context.sh -q 'which private-key armor does the scrubber redact and who loads it' -s scrub -s _scrub -s _body -s export -o /tmp/vr182/pack.md scripts/transcript_export.py harness-ports/bin/hermes-session-export.py tests/test_upstream_lock_lane_runtime.py`.

PREDICATE: a finding blocks only if it is contract-mapped (A: C3 and the 9932f34 claims; B: R3 with R3(c) as amended), reproduced
through the real exporter, the real test or the real committed code, materially effective (a key or secret byte reaches a written
file, or a stated claim is false as stated), with a concrete discriminator, and in-boundary for the repair (A: the key rule and its
tests in the three files of 9932f34; B: the three strings of 9c991a2). Everything else is a follow-up. Emit ONE GATE RECOMMENDATION
per component, (A) the key-armor class and (B) the R3(c) words, each `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` /
`CONTRACT-INVALID`. The coordinator owns the final gate.

Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md --root .`
(no `--map` flags; cite full repo-relative paths); apply its `fix:` hints for at most three rounds, then paste and finish. The report
ends with DISCREPANCIES and NOT-done.

## PREMISE — MEASURED at authoring (2026-09-23 11:16Z-11:25Z, sandbox @ c84f161, then the tree at 5090671)
```
$ date -u; git rev-parse --short HEAD
2026-09-23T11:16:52Z
c84f161
$ sha256[:16] lines  (at c84f161)
55989ae1c096bfc4   115 scripts/transcript_export.py
e3ae36b40fded64b   151 tests/test_transcript_export.py
3f7b5128b1dcd612    96 harness-ports/tests/test_hermes_session_export.py
3e195a5821b2e945   104 harness-ports/bin/hermes-session-export.py
6c0a3ff07156f9ad   173 upstream.lock.yaml
34295252a1aab29f   253 tests/test_upstream_lock_lane_runtime.py
b6cca36449c0b9cc   149 tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md
160d2ce0b22b4cee   529 harness-ports/bin/pc-lane.sh
$ git diff --stat 9932f34^ 9932f34; git diff --stat 9c991a2^ 9c991a2
 harness-ports/tests/test_hermes_session_export.py |  5 ++++
 scripts/transcript_export.py                      |  9 +++++---
 tests/test_transcript_export.py                   | 28 +++++++++++++++++++++++
 3 files changed, 39 insertions(+), 3 deletions(-)
 tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md | 3 ++-
 tests/test_upstream_lock_lane_runtime.py            | 2 +-
 upstream.lock.yaml                                  | 2 +-
 3 files changed, 4 insertions(+), 3 deletions(-)
$ grep -n (the seams)
scripts/transcript_export.py:29:    (re.compile(r"-----BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----.*?"
tests/test_transcript_export.py:122:KEY_FAMILIES = ("RSA PRIVATE KEY", "EC PRIVATE KEY", "OPENSSH PRIVATE KEY", "ENCRYPTED PRIVATE KEY",
tests/test_transcript_export.py:127:def test_every_key_family_is_scrubbed_whole(tmp_path, label):
tests/test_transcript_export.py:139:def test_key_block_after_a_credential_keyword_is_scrubbed_whole(tmp_path):
harness-ports/tests/test_hermes_session_export.py:87:    # VERIFY-AF-AP-127 F1: GnuPG armor (`… KEY BLOCK`) is scrubbed whole through this exporter too.
harness-ports/bin/hermes-session-export.py:23:SCRUB_SRC = HERE.parents[2] / "scripts" / "transcript_export.py"
upstream.lock.yaml:173:    verified: "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes
tests/test_upstream_lock_lane_runtime.py:58:    "110 PC lane directories whose latest launch was at or after 2026-09-08
harness-ports/bin/pc-lane.sh:217-218: PROMPT_FILE="$LANE_DIR/prompt.md" / : > "$PROMPT_FILE"
$ gates (at c84f161)
/root/venv-agent-factory/bin/python -m pytest tests/test_transcript_export.py -q  ->  13 passed in 0.66s
python3 harness-ports/tests/test_hermes_session_export.py  ->  test_hermes_session_export: 15 checks passed
/root/venv-agent-factory/bin/python -m pytest tests/test_upstream_lock_lane_runtime.py -q  ->  16 passed in 0.31s
$ date -u
2026-09-23T11:23:38Z
$ git diff --quiet c84f161 -- <the eight files above> (the working tree vs the PIN)
tree == c84f161 on the boundary
$ git log --format="%h %s" c84f161..HEAD | cut -c1-100
5090671 J1-0-R4 landed (task #172; GATED-PENDING-VERIFY): the never-a-gate screen scans to the end o
$ python3 (piece (c) of the lock's verified: value == the test constant?)
test constant (line 58 ): '110 PC lane directories whose latest launch was at or after 2026-09-08 14:22:00Z (98 with a report; brief.md--0000000 never ran Hermes), '
in lock line 173: True
$ grep -n "latest launch\|first launch\|LATEST launch" upstream.lock.yaml tests/test_upstream_lock_lane_runtime.py tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md | cut -c1-160
upstream.lock.yaml:173:    verified: "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: all suites pa
tests/test_upstream_lock_lane_runtime.py:58:    "110 PC lane directories whose latest launch was at or after 2026-09-08 14:22:00Z (98 with a report; brief.md--0
tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md:8:**Rule.** A lane counts when its directory's LATEST launch (the mtime of `prompt.md`, which `harness-ports
$ sed -n 217,218p;319,323p harness-ports/bin/pc-lane.sh | cut -c1-120
PROMPT_FILE="$LANE_DIR/prompt.md"
: > "$PROMPT_FILE"
PROMPT_RUN="$PROMPT_FILE"
if [ "$attempt" -gt 1 ] || [ -s "$LANE_REPORT_DRAFT" ]; then
  PROMPT_RUN="$LANE_DIR/prompt.attempt$attempt.md"
  { printf 'RESUME (attempt %s of this lane): a previous attempt of THIS lane ended on a route refusal or was stopped by
fi
$ grep -rn "prompt\.md" harness-ports/bin scripts/pc_lane.sh | grep -v "^harness-ports/bin/pc-lane.sh"
(no output)
$ sed -n 19,25p tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md
2026-09-08T14:22:32Z report - pc-verify-d5m.md--246bec7
2026-09-08T14:25:47Z report - pc-verify-b5j.md--01499e7
2026-09-08T14:27:09Z report - pc-verify-n5i.md--628da83
2026-09-08T14:28:43Z report - pc-b2.md--246bec7
2026-09-08T14:29:54Z report - pc-verify-m2.md--cb91edf
2026-09-08T14:31:16Z report - pc-verify-g2.md--887f021
2026-09-08T15:20:53Z report - pc-verify-ck13.md--77f46a2
$ grep -n "0000000" tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md
64:2026-09-15T17:09:44Z - - brief.md--0000000
$ PC clone (bridge, 11:2xZ): git rev-parse --abbrev-ref HEAD; git log -1 --format="%h %cd %s"
claude/soundbox-kit-migration-iz1jwf
012d455b 09-23 03:56 transcripts: scrubbed sandbox chat digests (2026-09-23)
$ (sandbox) git merge-base --is-ancestor 2d10a2c 012d455b; git merge-base --is-ancestor 9932f34 012d455b
2d10a2c IS ancestor of 012d455b
9932f34 NOT ancestor of 012d455b
$ PC clone: git status --porcelain (tracked); git fetch; git merge --ff-only c84f1611
tracked-dirty-lines: 0
c84f1611 09-23 11:15
HAS-9932f34
HAS-2d10a2c
$ git log --format='%h %cd %s' 2d10a2c..c84f161 -- transcripts/pc | cut -c1-120
221e68b 09-23 03:53 S0-02 B9 landed (GATED-PENDING-VERIFY): the replay leg's per-delivery delta model, the second delive
$ git ls-files transcripts | sed 's#/[^/]*$##' | sort | uniq -c
    104 transcripts/pc
     16 transcripts/sandbox
$ ls tests | grep -i 's0_12\|lane_runtime'; ls /usr/include/openssl/pem.h; which openssl gpg ssh-keygen
test_s0_12_license_sbom.py
test_upstream_lock_lane_runtime.py
/usr/include/openssl/pem.h
/usr/bin/openssl
/usr/bin/gpg
$ df -h /tmp | tail -1
/dev/vda        252G   36G  1.4G  97% /
```
Not measured at authoring, and so written as questions above: whether the landing's negative control reproduces, how many committed
transcripts change under the current scrub, and whether any new mutant survives.
