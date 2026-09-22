# PC lane — VERIFY-GOV2c (the independent, targeted adversarial verify of GOV2c: the governance review binding's TOCTOU closure, the GOODSIG/VALIDSIG status-line acceptance, the one-owner-key check)

PIN: 4cc3fe2

Role: adversarial-verifier. Route: the LOCAL verify route (`agentfactory-verify-local`; D-028 says xhigh for verify lanes — on the vLLM
route the effort is the server default and cannot be set per lane; say so in the report header). Venue: `tasks/briefs/pc/VENUE-MAP.md` —
read it first. Honey mode: full (line-bounded findings, evidence anchors, SOLID/UNSURE).

## WHAT YOU GRADE

GOV2c = commit `b1dba7b` (2026-09-17, "close VERIFY-GOV2b's two blockers in the review binding (TOCTOU + GOODSIG substring)"), the
coordinator's OWN repair of the two blockers a sandbox adversarial-verifier found in GOV2b. It was gated only by the coordinator's own
tests + 4 mutants — never independently verified (rule 0f). Its production surface is ONE function, `verify_review`, in
`src/agent_factory/governance/review.py` (`RV`), consumed by `load_packet` in `src/agent_factory/governance/packet.py`; its tests are
`tests/test_governance_review.py` (`TR`, the 6 GOV2c tests at TR:188-280 on top of the 10 GOV2b tests at TR:110-186); the owner
procedure is `docs/governance/reviews/README.md` (`RM`). The builder's own cases are NOT your cases: attack with NEW shapes through the
REAL function and the REAL gpg (2.4.7 on this host; the coordinator measured 2.4.4 in the sandbox).

The claims under test (RV:16-23, the GOV2c docstring): (F1) the record, its signature and the owner key are read ONCE with O_NOFOLLOW,
gpg verifies a COPY of exactly those bytes and the SAME record bytes are parsed — no second read to race; (F2/F6) a signature is accepted
only on a real `[GNUPG:] GOODSIG ` status LINE whose `VALIDSIG` fingerprint is in the one committed owner key's keyring — a `GOODSIG`
substring in a notation is not a status line; a revoked/expired key emits REVKEYSIG/EXPKEYSIG and no GOODSIG; (F5) "gpg runs by
absolute path with `--no-options` and a minimal env"; (F6) exactly one primary key in the owner file; (F7) every failure is a
`GovernanceError` with a stable reason; (F8) a symlink at the record/sig/owner-key path is refused.

## PREMISE — MEASURED at authoring (2026-09-22 06:1xZ, the sandbox clone at 4cc3fe2); re-measure as item 1
```
git log --format='%h %ad %s' --date=short -3 -- src/agent_factory/governance/review.py tests/test_governance_review.py docs/governance/reviews/README.md
  b1dba7b 2026-09-17 GOV2c: close VERIFY-GOV2b's two blockers in the review binding (TOCTOU + GOODSIG substring)
  756d516 2026-09-16 GOV2b: source the reviewed bit from a first-party owner-signed record (VERIFY-GOV1 F2; owner: go with b)
git log --oneline b1dba7b..4cc3fe2 -- <the same three paths>   → (empty: the three files are byte-identical since GOV2c)
git diff b1dba7b^ b1dba7b -- <the same three paths> | grep -E '^diff|^@@'
  RM: @@ -24,7 +24,7 @@  @@ -35,6 +35,9 @@  @@ -43,7 +46,14 @@
  RV: @@ -12,12 +12,22 @@  @@ -31,12 +41,50 @@  @@ -57,37 +105,72 @@
  TR: @@ -180,3 +180,100 @@
sha256 (first 16) at 4cc3fe2: RV 010054c04f697c8c · TR ea9e0a466a4807d2 · RM 662fd187a827461b
review.py seams: _is_governance_hash RV:47 · _read_no_symlink RV:51 (O_RDONLY|O_NOFOLLOW at :53, no O_NONBLOCK, no fstat) ·
  _keyring_shape RV:70 (pub: count + every fpr: field 9) · verify_review RV:88 (is_file pre-checks :107-110, shutil.which("gpg") :114,
  the three single reads :121-125, the 0700 temp home :128-129, env = GNUPGHOME + forwarded PATH + LC_ALL :136, --import :139-144,
  --status-fd 1 --verify :146-149, primary != 1 :154, the GOODSIG line + VALIDSIG[2] :159-164, json.loads of the SAME bytes :168,
  hash equality :174, reviewed is True :178)
GovernanceError reasons in RV (grep): fubuki-owner-key-ambiguous ×1, fubuki-owner-key-invalid ×1, fubuki-owner-key-missing ×1,
  fubuki-packet-unreviewed ×2, fubuki-review-gpg-unavailable ×2, fubuki-review-hash-invalid ×1, fubuki-review-record-invalid ×3,
  fubuki-review-signature-invalid ×1
sandbox gates (FUBUKI_OS_ROOT/FUBUKI_OTHER_ROOT exported; pyproject pythonpath = ["src"]):
  2026-09-22T06:16:09Z  python3 -m pytest -q tests/test_governance_review.py                    → 16 passed in 1.54s   (set ce6a68f1998d)
  2026-09-22T06:16:11Z  python3 -m pytest -q tests/test_governance_{bounds,packet,pin,pin_enforcement,projection,review}.py → 49 passed in 2.30s (set f3baa8cf79c7)
gpg: sandbox 2.4.4 (/usr/bin/gpg) · this PC 2.4.7 (/usr/bin/gpg)
```
The 2026-09-17 ledger quotes "the full governance suite (9 files) 65 passed" — a different set (AF-AP-73: a count carries its set);
the two sets above are this brief's.

## COORDINATOR-MEASURED FACTS FOR YOU (reproduce on this host; never trust them)
- (a) gpg 2.4.4 REFUSES an inline-signed or a clearsigned unrelated owner message offered as the `.asc` with the record as data:
  `gpg: not a detached signature`, rc 2, no GOODSIG (the control, a real detached signature: NEWSIG/GOODSIG/VALIDSIG, rc 0). RV:163
  refuses on `returncode != 0`. Reproduce on 2.4.7 — this is the boundary that would otherwise let ANY owner-signed inline text
  authorize ANY record.
- (b) ONE `verify_review` call leaves ONE `gpg-agent --homedir /tmp/tmpXXXX --use-standard-socket --daemon` running after its
  TemporaryDirectory is deleted (pgrep before/after around a single call; 25+ such orphans in the sandbox from earlier runs). RV has no
  `gpgconf --kill` and no `--no-autostart` (grep: none); the TEST fixture kills its own agents (TR:70) — production does not.
  `scripts/check-proof-status.py` (the other isolated-keyring gpg user) has none either — the sibling instance of the class.
- (c) `gpg = shutil.which("gpg")` (RV:114) and `PATH` forwarded into gpg's env (RV:136): the docstring's "absolute path" is the resolved
  path of whatever the caller's PATH names first.
- (d) `_read_no_symlink` opens with O_RDONLY|O_NOFOLLOW only (RV:53): no O_NONBLOCK, no fstat/S_ISREG; the `is_file()` pre-check at
  RV:107 is a separate stat.

## ITEMS (in order; every count PASTED with `date -u` beside it; every file:line by `sed -n` on the PIN; reproduced vs reviewed vs skipped stated per item)

1. **PREMISE (first; stop on failure):** re-run the log/diff/sha commands above on your worktree and paste them; a different hunk set or
   identity → CONTRACT-INVALID, stop. Then the two pytest sets ONCE each with the venue exports (below) and `--basetemp /tmp/vg2c/bt`
   (`mkdir -p /tmp/vg2c` first — gpg's agent socket lives under the temp tree and a long path breaks it with `exit status 2`, a false
   red: AF-AP-73's cousin from `tests/test_proof_status.py`); paste the two summary lines beside the sandbox ones.
2. **The single-snapshot claim (F1):** rebuild the VERIFY-GOV2b race harness from its description — a writer that flips
   `<hash>.json` between the owner-signed record and an UNSIGNED `reviewed:true` record as fast as it can while `verify_review` runs in a
   loop of ≥ 400 calls; expected 0 acceptances of the unsigned record (the pre-fix code accepted 117 of 400). Then the SIG-path race
   (flip `<hash>.json.asc` between the record read RV:121 and the sig read RV:122 — still 0), a hardlink to a signed record swapped
   mid-call, and a `reviews_dir` that is ITSELF a symlink to an attacker directory (O_NOFOLLOW guards only the final component: say
   whether following it is a hole or merely equivalent to writing the store — the signature check still binds the bytes).
3. **The status-line acceptance (F2/F6), new shapes:** (i) the owner key over DIFFERENT bytes (BADSIG → rc 1 → refused; paste the status
   lines); (ii) a `--sig-notation` whose value is `[GNUPG:] GOODSIG …` text — measure gpg's percent-escaping in the NOTATION_DATA line
   (can a raw newline ever reach stdout?); (iii) an EXPIRED owner key (EXPKEYSIG) and an EXPIRED signature (`--default-sig-expire 1s`
   or `--faked-system-time`, EXPSIG); (iv) a signature by a SIGNING SUBKEY of the owner key — must PASS (`_keyring_shape` collects every
   `fpr:` line, VALIDSIG[2] is the subkey's fingerprint): a false RED here is a finding too; (v) the owner file holding the same key
   TWICE (does `--import` dedupe to primary == 1?), a key + its REVOCATION certificate (REVKEYSIG → refused, TR:209's cousin), an
   EMPTY owner file, a NON-ARMORED owner file (`--export` without `--armor` → does stdin import still work?); (vi) VALIDSIG's LAST
   field is the PRIMARY fingerprint and field 2 the signing key — confirm RV:162 reads field 2 and that the set at RV:84 contains both.
4. **The "not a detached signature" boundary (a):** reproduce (a) on 2.4.7 with a clearsigned AND an inline-signed owner message;
   then: a `.asc` holding TWO signatures (the owner's over other bytes + an attacker key's over the record) — what does gpg return
   and does RV refuse?; a binary (non-armored) detached signature (should PASS); the owner's REAL signed git tag (`git cat-file tag
   accepted/S0-01` → its PGP block is a detached signature over the tag payload) offered as the `.asc` over the record → BADSIG, refused
   (measure); a `.asc` that is a detached signature over the record made by the owner key but with a trailing SECOND armored block.
5. **F5's own claim vs (c):** put a fake `gpg` FIRST on PATH (a ~12-line script under your scratch: `--import` → rc 0; `--with-colons
   --list-keys` → one `pub:` line + one `fpr:` line with an arbitrary 40-hex fingerprint; `--verify` → `[GNUPG:] GOODSIG …` +
   `[GNUPG:] VALIDSIG <that fingerprint> …`, rc 0) and call `verify_review` on an UNSIGNED record. Expected by construction: ACCEPTED.
   Dispose it honestly: is a caller-controlled PATH inside the threat model the docstring states ("PATH-shadowed gpg is not a trust
   channel", RV:16-23 + the GOV2c ledger note)? The repo's rule (`os.environ` is NOT a config channel — resolve once, thread explicitly)
   says it is. Propose the minimal fix (an ordered absolute-path list `/usr/bin/gpg`, `/usr/bin/gpg2` with a refusal, or a
   `gpg_path` parameter threaded by `load_packet`'s caller) — a BLOCKER only if the predicate holds on the contract as written.
6. **The special-file window (d):** replace the record with a FIFO between the `is_file()` pre-check (RV:107) and the open (RV:53) —
   monkeypatch `Path.is_file` to return True for the FIFO, or race a `mv` — and call `verify_review` under `timeout 10`: does the
   governance gate HANG (no writer → the open blocks; no read timeout anywhere)? A hang = a DoS of every `load_packet` by a writer of the
   reviews dir (the F1 attacker). Minimal fix: `O_NONBLOCK` on the open + `os.fstat` S_ISREG → refuse with `fubuki-review-record-invalid`.
   Also: a directory, a socket and `/dev/null` at the record path (each refused by which line?), and a record of exactly
   `_MAX_RECORD_BYTES` vs one byte more (RV:60: the boundary — which side is accepted?).
7. **Record shapes through the REAL path (each signed by the owner key, so only the parser decides):** a UTF-8 BOM before the `{`;
   trailing bytes after the object; `"reviewed": 1` / `"true"` / `[true]`; a DUPLICATE `"reviewed"` key (json.loads keeps the last —
   `{"reviewed": false, …, "reviewed": true}` is accepted: say whether that matters when the owner signed both); `governance_hash`
   in UPPERCASE inside the record for a lowercase argument; an uppercase ARGUMENT (RV:103 refuses — paste); a hash argument with a `/`
   or `..` (refused at RV:103 before any path is built — paste); NaN/Infinity literals; nested objects; a 64-hex hash of another
   packet with a valid signature (TR:151 covers one shape — try the record naming BOTH hashes in two keys).
8. **The isolated keyring:** the temp home is 0700 (RV:129 — `TemporaryDirectory` already makes it 0700: a declared-equivalent mutant
   candidate); `--no-options` really ignores a hostile `~/.gnupg/gpg.conf` (write one with `trust-model always` + `keyring
   <attacker>` under a throwaway HOME, point HOME at it, verify an attacker-signed record → refused?); a hostile `GNUPGHOME` in the
   CALLER's environment is NOT forwarded (RV:136 builds env from scratch — confirm by setting it to an attacker keyring); then (b): count
   `gpg-agent` processes before/after ONE `verify_review` call on this host, and measure the two candidate fixes on a scratch copy —
   `gpgconf --homedir <home> --kill all` before the `with` block exits, or `--no-autostart` on every gpg call (does `--verify` of a
   public-key signature still work without an agent on 2.4.7?) — paste the call's wall time with and without.
9. **`load_packet` integration (packet.py):** the reviewed bit comes ONLY from `verify_review` (grep the package for every other
   reader of `reviewed` / `review`); the hash passed is the hash of the CANONICAL bytes (`compile_canonical`) — a packet whose on-disk
   form differs from its canonical form canonically-invisibly (whitespace/key order) shares the review record: is that the intended
   binding? state it; `_REPO_ROOT = parents[3]` (RV:37) — an installed copy of the package outside the repo resolves `DEFAULT_OWNER_KEY`
   to a missing file → `fubuki-owner-key-missing` (fail closed; note the deployment implication for the Hermes projection consumer).
10. **Error taxonomy (F7):** every reason above reached by a test (map reason → test name; an unreached reason is a finding); a hung gpg
    (`timeout=30`) → `SubprocessError` → `fubuki-review-gpg-unavailable` (simulate with the fake gpg sleeping 31 s); invalid UTF-8
    record bytes → `fubuki-review-record-invalid`; `record_path` containing a NUL byte → `ValueError` from `is_file()` — is it
    reachable through `_is_governance_hash`'s domain? (no: hex only — say so, one line).
11. **Mutants ≥ 12, each compile-checked (`python -m py_compile`) and collected before it counts (AF-AP-78), on a scratch copy of the
    PIN under your lane's scratch, restored byte-identical after (paste the sha):** M1 `startswith("[GNUPG:] GOODSIG ")` →
    `"GOODSIG" in verified.stdout`; M2 drop `signer not in owner_fingerprints`; M3 parse a SECOND read (`json.loads(record_path.read_bytes())`);
    M4 drop `os.O_NOFOLLOW`; M5 `primary != 1` → `primary < 1`; M6 `is not True` → `not record.get("reviewed")`; M7 hash equality →
    a prefix match on 8 hex; M8 `env = dict(os.environ)`; M9 `--status-fd 2`; M10 drop `verified.returncode != 0`; M11
    `_MAX_RECORD_BYTES = 1 << 40`; M12 `fingerprints.add(parts[9][:8])`; M13 drop the `sig_path.is_file()` conjunct; M14 drop
    `os.chmod(home, 0o700)` (declare equivalent or kill). Each: the NAMED test that goes red (`python -m pytest -q tests/test_governance_review.py`
    on the mutated copy, `-x`, the failing test's name pasted) or a FINDING with the killer you would write.
12. **Gates (the carve-out is unnecessary here — everything runs on this host):** `tests/test_governance_review.py` ×2 and the six-file
    governance set ×1, each under the 420 s cap, the FUBUKI exports set, the file list pasted beside every count (set ids ce6a68f1998d
    and f3baa8cf79c7).
13. **Report + lint:** `python3 scripts/report_lint.py <your report> --rev 4cc3fe2 --map RV=src/agent_factory/governance/review.py
    --map TR=tests/test_governance_review.py --map RM=docs/governance/reviews/README.md --map PK=src/agent_factory/governance/packet.py`
    (the CURRENT lint is overlaid into your tree by the dispatcher) — at most three fix rounds, then paste and finish (AF-AP-76).

## DISPOSITION (D-031 / D-034; skill `contract-gate`)
Discovery exhaustive, no severity filter. A finding BLOCKS only if it meets the whole predicate: contract-mapped (the F1/F2/F5/F6/F7/F8
claims above, the GOV2c ledger note, `docs/08_DECISION_LOG.md`) · canonically reproduced through the real `verify_review` + the real
gpg · materially effective · a concrete discriminator (a red test or a failing input, pasted) · in-boundary (RV/TR/RM/PK). Close with
ONE line `GATE RECOMMENDATION: MERGE-READY | MERGE-READY-WITH-FOLLOWUPS | NOT-READY | CONTRACT-INVALID` + the blocking set. Residue = a
numbered list (file:line, the failing input, the minimal fix, the red test) the coordinator files as `verify-followup` issues; you file
nothing, comment nowhere, commit nothing, push nothing. A blocker gets ONE focused repair keyed by RV's digest (D-031) — never a round.

## VENUE NOTES (this host)
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; never `pip install` into the shared venv; `python -m pytest -q …` directly (a
  PC-resident lane cannot run `scripts/pc_suite.sh`); Hermes's `terminal` tool caps ONE call at 420 s — the two sets run in seconds.
- Export `FUBUKI_OS_ROOT=/home/rocco/fubuki-pin/fubuki-os FUBUKI_OTHER_ROOT=/home/rocco/fubuki-pin/fubuki-os-other` for every pytest
  call (`tests/test_governance_review.py:34-39`: `pinned_fubuki` is autouse and FAILS without them — a declared input, AF-AP-81).
- Throwaway keys ONLY (`gpg --batch --pinentry-mode loopback --passphrase '' --quick-generate-key … ed25519 sign 0` in a 0700 scratch
  GNUPGHOME under `/tmp/vg2c/`); never touch `~/.gnupg`; kill the agents YOU start with `gpgconf --homedir <yours> --kill all` (by
  homedir, never by name); never `pkill`/`killall` by name — three other lanes (VERIFY-S4H, K1-d, VERIFY-B67) and the vLLM `qwen`
  container run on this host: never touch their trees, the container, OmniRoute, or any server.
- Read-only git in your worktree except your scratch copies; the report at `tasks/briefs/stage3-governance-support/VERIFY-GOV2c-report.md`
  in your worktree — draft after EACH item, return it whole as your final message (header: PIN, venue line with gpg version + the
  effort note, the item-1 pastes; then per-item reproduced/reviewed/skipped; findings; mutants; gates; the GATE RECOMMENDATION line).
- No foreground `sleep` in long waits — bounded polls; every namespace/agent/listener you create is yours to remove; paste `date -u`
  beside every count; a count is PASTED from the run, never typed.

**Authorization:** defensive testing of the owner's own governance code with throwaway keys on the owner's own host; the committed owner
key is read, never used to sign; nothing leaves this host.
