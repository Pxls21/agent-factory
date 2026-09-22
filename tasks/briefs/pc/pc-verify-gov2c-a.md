# PC lane — VERIFY-GOV2c-A (split 1 of 3 of `tasks/briefs/pc/pc-verify-gov2c.md`: master items 1, 2, 3, 4)

PIN: dab9803

Role: adversarial-verifier. Route: the LOCAL verify route (`agentfactory-verify-local`; D-028 says xhigh for verify lanes — on the vLLM
route the effort is the server default and cannot be set per lane; say so in the report header). Venue: `tasks/briefs/pc/VENUE-MAP.md` —
read it first. Honey mode: full (line-bounded findings, evidence anchors, SOLID/UNSURE).

## WHY A SPLIT (read this — it sets your working style)

The first VERIFY-GOV2c lane (Hermes session `20260922_072300_d1e998`, PIN 4cc3fe2) DIED at 07:09Z after 57 messages: its context grew
past the local model's late-system-message limit (~100k tokens → HTTP 400), OmniRoute fell back to a cloud model, and that model's safety
filter refused the brief (`transcripts/pc/pc-verify-gov2c.md--4cc3fe2.md`). Its tool-result bodies were NOT exported, so nothing it
reported counts as verified. The master brief is now run as THREE lanes; this one takes master items 1-4 only. Keep your context small:

- every terminal call's output is BOUNDED (`| tail -n 40` or `| head -c 3000`); a harness prints ONE line per case, never raw gpg output
  except the status lines a finding needs;
- draft the report after EACH item (write_file to the report path below), so a death loses one item, not the lane;
- do not read files whole when `sed -n` of a range answers the question; do not re-read the master brief after the first pass.

## THE MASTER BRIEF GOVERNS

Read `tasks/briefs/pc/pc-verify-gov2c.md` in your worktree ONCE: its WHAT YOU GRADE, COORDINATOR-MEASURED FACTS (a)-(d), DISPOSITION
and VENUE NOTES apply verbatim. Execute master ITEMS 1, 2, 3 and 4 EXACTLY as written there, with these overrides:

1. Item 1's premise commands run against THIS PIN (`dab9803`); the expected identities are in the block below.
2. Item 2's "expected 0 acceptances" sentences are QUESTIONS for you: paste the count you measure for each race; the pre-fix
   117-of-400 is VERIFY-GOV2b's number, not a promise about this code. The symlinked-`reviews_dir` sub-case is the one the dead lane never
   finished — give it its own paragraph.
3. Item 3 (vi): the dead lane's reading was that `line.split()` of a VALIDSIG status line yields `[0]='[GNUPG:]'`, `[1]='VALIDSIG'`,
   `[2]=<signing-key fpr>`, last = primary fpr. Confirm from a pasted line on THIS gpg; a miscount here would flip the whole F2/F6 grade.
4. The report path is `tasks/briefs/stage3-governance-support/VERIFY-GOV2c-A-report.md` (not the master's); the master's item-13 lint
   command applies to it with `--rev dab9803`; at most three fix rounds, then paste and finish (AF-AP-76). Items 5-13 are OTHER lanes':
   do not start them; if a finding of yours bears on one, one line under FOLLOW-UPS.
5. Scratch under `/tmp/vg2c-a/` — small files only (throwaway keys, records, harness scripts; never a tree copy — AF-AP-112);
   pytest basetemp `/tmp/vg2c-a/bt` (short: gpg's agent socket path limit). Kill the agents YOU start by homedir
   (`gpgconf --homedir <yours> --kill all`), never by name; orphaned agents from OTHER lanes are not yours to touch.

## PREMISE — MEASURED (coordinator, 2026-09-22 08:48Z, the sandbox clone at dab9803; re-measure as item 1)

```
git log --oneline b1dba7b..dab9803 -- src/agent_factory/governance/review.py tests/test_governance_review.py docs/governance/reviews/README.md src/agent_factory/governance/packet.py
  (empty: the four files are byte-identical since GOV2c = b1dba7b)
sha256 (first 16) at dab9803: RV 010054c04f697c8c · TR ea9e0a466a4807d2 · RM 662fd187a827461b · PK 5d8cf21468adb55e
GovernanceError reasons in RV (grep -n -o 'fubuki-[a-z-]*'): :103 review-hash-invalid · :110 packet-unreviewed · :112 owner-key-missing ·
  :116 review-gpg-unavailable · :126 review-record-invalid · :144 owner-key-invalid · :151 review-gpg-unavailable · :155 owner-key-ambiguous ·
  :164 review-signature-invalid · :170 review-record-invalid · :172 review-record-invalid · :176 review-hash-mismatch
RV seams: _MAX_RECORD_BYTES = 1 << 20 (:44) · _is_governance_hash (:47) · _read_no_symlink O_RDONLY|O_NOFOLLOW (:51-53) · _keyring_shape (:70) ·
  verify_review (:88) · shutil.which("gpg") (:114) · chmod 0o700 (:129) · GOODSIG line (:160) · validsig[2] (:162) · json.loads (:168) ·
  reviewed is not True (:178)
sandbox gates (scripts/test_summary.sh exports FUBUKI_OS_ROOT/FUBUKI_OTHER_ROOT; PYTEST_ADDOPTS="--basetemp /tmp/vg2c/bt"):
  2026-09-22T08:48:06Z  tests/test_governance_review.py                                   → 16 passed in 1.46s  (set ce6a68f1998d)
  2026-09-22T08:48:08Z  tests/test_governance_{bounds,packet,pin,pin_enforcement,projection,review}.py → 49 passed in 1.94s (set f3baa8cf79c7)
gpg: sandbox 2.4.4 · this PC 2.4.7 (the dead lane's header)
```

## PRIOR CLAIMS from the dead lane (its own summaries; tool bodies unexported — count NOTHING as done; reproduce what your findings depend on)

- Item 1 on 4cc3fe2, gpg 2.4.7: `16 passed in 1.18s` / `49 passed in 1.96s`; log, hunks and the three sha256s matched the master.
- Item 2: three F1 races (record flip, sig flip, hardlink swap) reported `0/400 accepts` each; the symlinked-dir sub-case died on a stale
  agent socket (rc 2 at keygen) before any result.
- Item 3: (i) BADSIG → refused; (ii) gpg PERCENT-ESCAPES notation data (`NOTATION_DATA [GNUPG:]%20GOODSIG%20…`) — a raw newline never
  reaches stdout, and NOTATION_DATA is a distinct line the `startswith("[GNUPG:] GOODSIG ")` check ignores; (iii) EXPKEYSIG for an expired
  key and EXPSIG for an expired signature (the key must be generated AT the faked time — `--faked-system-time` on a fresh key made it
  "in the future", rc 2); (iv) a signing subkey → VALIDSIG field 2 = the subkey fpr, last field = the primary — RV:162 reads field 2;
  (v) the same key listed twice → `--import` dedupes to primary == 1 (accepted); a revocation cert generated BEFORE signing made the key
  unusable — sign first, then revoke (TR:209's order).
- Item (b): orphaned `gpg-agent` processes were observed after the harness runs (AF-AP-110's instance on this host).

## DELIVERABLE

`tasks/briefs/stage3-governance-support/VERIFY-GOV2c-A-report.md`, drafted after each item: header (PIN, venue line with the gpg version
and the effort note, the item-1 pastes); items 1-4 each reproduced / reviewed / skipped with pasted status lines and counts (`date -u`
beside every count); findings F1… with the blocking predicate applied; FOLLOW-UPS (one line each); NOT-done; ONE closing line
`GATE RECOMMENDATION (items 1-4 only): MERGE-READY | MERGE-READY-WITH-FOLLOWUPS | NOT-READY | CONTRACT-INVALID` — the coordinator joins
the three lanes' recommendations into the GOV2c gate. Commit nothing, push nothing, post nothing.

**Authorization:** defensive testing of the owner's own governance code with throwaway keys on the owner's own host; the committed owner
key is read, never used to sign; nothing leaves this host.
