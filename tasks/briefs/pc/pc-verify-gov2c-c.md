# PC lane — VERIFY-GOV2c-C (split 3 of 3 of `tasks/briefs/pc/pc-verify-gov2c.md`: master items 1, 7, 9, 10, 11, 12, 13)

PIN: dab9803

Role: adversarial-verifier. Route: the LOCAL verify route (`agentfactory-verify-local`; D-028 says xhigh for verify lanes — on the vLLM
route the effort is the server default and cannot be set per lane; say so in the report header). Venue: `tasks/briefs/pc/VENUE-MAP.md` —
read it first. Honey mode: full (line-bounded findings, evidence anchors, SOLID/UNSURE).

## WHY A SPLIT (read this — it sets your working style)

The first VERIFY-GOV2c lane (Hermes session `20260922_072300_d1e998`, PIN 4cc3fe2) DIED at 07:09Z after 57 messages: its context grew
past the local model's late-system-message limit (~100k tokens → HTTP 400), OmniRoute fell back to a cloud model, and that model's safety
filter refused the brief (`transcripts/pc/pc-verify-gov2c.md--4cc3fe2.md`). Its tool-result bodies were NOT exported, so nothing it
reported counts as verified. The master brief is now run as THREE lanes; this one takes master items 1, 7, 9, 10, 11, 12 and 13 — the
record-shape, integration, taxonomy, mutation and gate items. Keep your context small:

- every terminal call's output is BOUNDED (`| tail -n 40` or `| head -c 3000`); a harness prints ONE line per case; a mutant run is
  `python -m pytest -q -x tests/test_governance_review.py 2>&1 | tail -n 5` — the failing test's NAME and the summary line, nothing more;
- draft the report after EACH item (write_file to the report path below), so a death loses one item, not the lane;
- do not read files whole when `sed -n` of a range answers the question; do not re-read the master brief after the first pass.

## THE MASTER BRIEF GOVERNS

Read `tasks/briefs/pc/pc-verify-gov2c.md` in your worktree ONCE: its WHAT YOU GRADE, COORDINATOR-MEASURED FACTS (a)-(d), DISPOSITION
and VENUE NOTES apply verbatim. Execute master ITEMS 1, 7, 9, 10, 11, 12 and 13 EXACTLY as written there, with these overrides:

1. Item 1's premise commands run against THIS PIN (`dab9803`); the expected identities are in the block below.
2. Item 7: every case is a QUESTION (accepted / refused with which reason) — paste the reason string for each; the master names no
   expected outcome except where RV's own line decides it (the RV:103 refusals). The duplicate-`reviewed`-key case gets the master's
   "say whether that matters when the owner signed both" answered in two sentences.
3. Item 11: the 14 mutants M1-M14 are applied ONE AT A TIME to a scratch copy of RV under `/tmp/vg2c-c/rv/` (copy `src/agent_factory`
   there, edit the copy, run pytest with `PYTHONPATH=/tmp/vg2c-c/rv` so the copy is imported — prove the copy is the one imported by
   pasting `python -c 'import agent_factory.governance.review as m; print(m.__file__)'` once); each mutant `py_compile`d and collected
   before it counts (AF-AP-78); the worktree's RV is never edited (paste its sha256 at the end, must equal 010054c04f697c8c).
   A mutant with NO red test is a FINDING with the killer test you would write (name + the assertion), never a silent row.
4. Item 12's gates run on the UNMODIFIED worktree with the FUBUKI exports and `--basetemp /tmp/vg2c-c/bt`; paste the set ids beside the
   counts (`ce6a68f1998d`, `f3baa8cf79c7`).
5. The report path is `tasks/briefs/stage3-governance-support/VERIFY-GOV2c-C-report.md` (not the master's); item 13's lint command
   applies to it with `--rev dab9803`; at most three fix rounds, then paste and finish (AF-AP-76). Items 2-6 and 8 are OTHER lanes': do
   not start them; if a finding of yours bears on one, one line under FOLLOW-UPS.
6. Scratch under `/tmp/vg2c-c/` — small files only (throwaway keys, records, the `agent_factory` package copy for mutants; never a
   whole-tree copy — AF-AP-112); pytest basetemp `/tmp/vg2c-c/bt`. Kill the agents YOU start by homedir, never by name.

## PREMISE — MEASURED (coordinator, 2026-09-22 08:48Z, the sandbox clone at dab9803; re-measure as item 1)

```
git log --oneline b1dba7b..dab9803 -- src/agent_factory/governance/review.py tests/test_governance_review.py docs/governance/reviews/README.md src/agent_factory/governance/packet.py
  (empty: the four files are byte-identical since GOV2c = b1dba7b)
sha256 (first 16) at dab9803: RV 010054c04f697c8c · TR ea9e0a466a4807d2 · RM 662fd187a827461b · PK 5d8cf21468adb55e
GovernanceError reasons in RV (grep -n -o 'fubuki-[a-z-]*'): :103 review-hash-invalid · :110 packet-unreviewed · :112 owner-key-missing ·
  :116 review-gpg-unavailable · :126 review-record-invalid · :144 owner-key-invalid · :151 review-gpg-unavailable · :155 owner-key-ambiguous ·
  :164 review-signature-invalid · :170 review-record-invalid · :172 review-record-invalid · :176 review-hash-mismatch
  (12 raise sites, 9 distinct reasons — item 10 maps each SITE to the test that reaches it; a site no test reaches is a finding)
RV seams: _MAX_RECORD_BYTES = 1 << 20 (:44) · _is_governance_hash (:47) · _read_no_symlink O_RDONLY|O_NOFOLLOW (:51-53) · _keyring_shape (:70) ·
  verify_review (:88) · shutil.which("gpg") (:114) · chmod 0o700 (:129) · GOODSIG line (:160) · validsig[2] (:162) · json.loads (:168) ·
  reviewed is not True (:178)
sandbox gates (scripts/test_summary.sh exports FUBUKI_OS_ROOT/FUBUKI_OTHER_ROOT; PYTEST_ADDOPTS="--basetemp /tmp/vg2c/bt"):
  2026-09-22T08:48:06Z  tests/test_governance_review.py                                   → 16 passed in 1.46s  (set ce6a68f1998d)
  2026-09-22T08:48:08Z  tests/test_governance_{bounds,packet,pin,pin_enforcement,projection,review}.py → 49 passed in 1.94s (set f3baa8cf79c7)
gpg: sandbox 2.4.4 · this PC 2.4.7 (the dead lane's header)
```

## PRIOR CLAIMS from the dead lane (its own summaries; tool bodies unexported — count NOTHING as done; reproduce what your findings depend on)

- Item 1 on 4cc3fe2, gpg 2.4.7: `16 passed in 1.18s` / `49 passed in 1.96s`; identities matched the master.
- Items 7/10 (partial): hostile hash ARGUMENTS (uppercase, `../etc/passwd`, 63/65 chars, NUL, short, single-char) all refused at RV:103
  `fubuki-review-hash-invalid` before any path is built; a UTF-8 BOM and trailing bytes were REFUSED (`fubuki-review-record-invalid`);
  NaN/Infinity/float in `governance_hash` → hash-mismatch; NaN in `reviewed` → unreviewed; the lane's first arg tests were VOID
  (it passed `Path.mkdir()`'s None as a path — a harness bug it caught itself: check your own harness's negative control first).
- Items 9, 11, 12, 13 were never reached.

## DELIVERABLE

`tasks/briefs/stage3-governance-support/VERIFY-GOV2c-C-report.md`, drafted after each item: header (PIN, venue line with the gpg version
and the effort note, the item-1 pastes); items 1, 7, 9, 10, 11, 12, 13 each reproduced / reviewed / skipped with pasted lines and counts
(`date -u` beside every count); the MUTATION TABLE (M1-M14: compiles · collected · killed-by <test name> / SURVIVED / EQUIVALENT-declared);
findings F1… with the blocking predicate applied; FOLLOW-UPS (one line each); NOT-done; ONE closing line
`GATE RECOMMENDATION (items 1, 7, 9-13 only): MERGE-READY | MERGE-READY-WITH-FOLLOWUPS | NOT-READY | CONTRACT-INVALID` — the coordinator
joins the three lanes' recommendations into the GOV2c gate. Commit nothing, push nothing, post nothing.

**Authorization:** defensive testing of the owner's own governance code with throwaway keys on the owner's own host; the committed owner
key is read, never used to sign; nothing leaves this host.
