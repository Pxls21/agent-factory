# VERIFY-GOV2c-B report (master items 1, 5, 6, 8)

PIN: dab9803 (detached lane worktree)
Venue: PC lane `pc-verify-gov2c-b.md--dab9803`, GnuPG 2.4.7. Route `agentfactory-verify-local`: D-028 assigns xhigh to verifier lanes, but this vLLM route uses the dispatcher-set server default; no per-lane effort was set or claimed. Interpreter: `/home/rocco/venv-agent-factory/bin/python`. Scratch: `/tmp/vg2c-b/`.

## Item 1 — premise (REPRODUCED)

```
$ git log --format='%h %ad %s' --date=short -3 -- RV TR RM PK
b1dba7b 2026-09-17 GOV2c: close VERIFY-GOV2b's two blockers in the review binding (TOCTOU + GOODSIG substring)
756d516 2026-09-16 GOV2b: source the reviewed bit from a first-party owner-signed record (VERIFY-GOV1 F2; owner: go with b)
f5b5a1b 2026-09-16 GOV2a: enforce the pinned-source contract AT the production API (VERIFY-GOV1 F1)

$ git log --oneline b1dba7b..dab9803 -- RV TR RM PK
(empty)

$ git diff b1dba7b^ b1dba7b -- RV TR RM | grep -E '^diff|^@@'
RM: @@ -24,7 +24,7 @@  @@ -35,6 +35,9 @@  @@ -43,7 +46,14 @@
RV: @@ -12,12 +12,22 @@  @@ -31,12 +41,50 @@  @@ -57,37 +105,72 @@
TR: @@ -180,3 +180,100 @@

$ sha256sum <RV TR RM PK> | cut -c1-16
RV 010054c04f697c8c; TR ea9e0a466a4807d2; RM 662fd187a827461b; PK 5d8cf21468adb55e
```

All identities and hunk sets match the brief. At 2026-09-22T09:24:41Z, `tests/test_governance_review.py` (set `ce6a68f1998d`) passed `16 in 1.16s`; rc 0. At 2026-09-22T09:24:42Z, the six listed governance files passed `49 in 1.94s`; rc 0. Venue exports and `/tmp/vg2c-b/bt` were set for both. Independent re-run with the PC's declared `FUBUKI_OS_ROOT=/home/rocco/fubuki-pin/fubuki-os` and `FUBUKI_OTHER_ROOT=/home/rocco/fubuki-pin/fubuki-os-other`: `16 passed in 0.73s` at 2026-09-22T10:11:27Z and `49 passed in 0.96s` at 2026-09-22T10:11:35Z; both rc 0. An initial re-run omitted those two required declared inputs and produced the intended `FUBUKI_OS_ROOT is a declared GOV1 test input` failures (16 errors; then 11 passed/38 errors); no test claim relies on that invalid invocation.

**D1 — DISCREPANCY, SOLID.** The exact six-file list produces set id `892ef4ebb5b8` via the PIN's `scripts/pc_suite.sh` set-id formula, not the handed `f3baa8cf79c7`; stripping `tests/` gives `195a7b339dd7`. Count and file list match. This does not affect execution.

## Item 5 — F5 PATH resolution (REPRODUCED)

Static mechanism: `shutil.which("gpg")` at RV:114 resolves caller PATH; RV:136 forwards it; RV:137 executes that path. This contradicts F5's claim at RV:22-23 that PATH-shadowed gpg is not a trust channel.

```
$ command -v gpg; sha256sum /tmp/vg2c-b/fake-bin/gpg | cut -c1-16
/tmp/vg2c-b/fake-bin/gpg
9bc3d76ce8fa6c39

$ PATH=/tmp/vg2c-b/fake-bin:... PYTHONPATH=src python <real verify_review on unsigned record>
ACCEPTED unsigned record
rc=0 at 2026-09-22T09:28:54Z
```

The authorized scratch fake returns successful import/listing and shaped GOODSIG/VALIDSIG output. The real `verify_review` accepted an unsigned record. `load_packet` is the real consumer at PK:136; ripwire independently found it and the review tests as callers.

Re-verification at 2026-09-22T10:12:46Z used a freshly generated throwaway owner key, so the fixed-real-path control reaches signature validation rather than owner-key parsing:

```
FAKE_PATH ACCEPTED unsigned-valid-owner
REAL_PATH REFUSED fubuki-review-signature-invalid
F5_CONTROL_RC=0; LANE_OWNED_AGENTS_AFTER=0
```

**F1 — BLOCKER, SOLID.** Contract mapping: frozen F5 at RV:22-23 and master item 5. Canonical path: real `verify_review`. Material effect: unsigned review authorization is accepted. Discriminator: fake-first PATH accepts; a fixed real `/usr/bin/gpg` rejects the empty signature. Ownership: RV/TR/RM. Minimal fix: fixed trusted executable path(s), never `shutil.which` on caller PATH; add this regression through `verify_review` and preferably `load_packet`.

## Item 6 — special-file window (REPRODUCED)

RV:109 has a separate `Path.is_file()` pre-check; RV:53 opens only `O_RDONLY|O_NOFOLLOW`; the record bytes are
captured at RV:122 by `record_bytes = _read_no_symlink(record_path)`, without nonblocking mode or FD `fstat`.

```
$ timeout 10 python /tmp/vg2c-b/fifo_probe.py ...
rc=124 wall_ms=10004 at 2026-09-22T09:30:22Z
```

The probe replaces a normal record with a mode-0600 FIFO between the real pre-check and open, then invokes real `verify_review` without a writer. It hung. Re-run at 2026-09-22T10:08:45Z reproduced `FIFO rc=124 wall_ms=10003`.

**F2 — BLOCKER, SOLID.** Contract mapping: F1/F8 and explicit master item 6 no-hang requirement. Canonical path: real `verify_review` consumed by `load_packet`, defined at PK:136. Material effect: a reviews-dir writer can indefinitely block every review/load. Discriminator: timeout rc 124; a nonblocking FD regular-file check returns refusal. Ownership: RV/TR. Minimal fix: `O_NONBLOCK`, `fstat` the returned FD, require `stat.S_ISREG`, and map nonregular input to `fubuki-review-record-invalid`; add the forced FIFO race regression.

Other real-gpg, throwaway-key checks at 2026-09-22T09:32:02Z:

```
size-exact: ACCEPTED
size-plus-one: REFUSED fubuki-review-record-invalid
directory/socket/dev-null: REFUSED fubuki-packet-unreviewed
rc=0 wall_ms=129
```

**I1 — INFO, SOLID.** Size cap `_MAX_RECORD_BYTES` at RV:44 is inclusive. Directory/socket/device fail at `record_path.is_file()` RV:109, so their reason differs from an FD-level nonregular failure. No false approval.

## Item 8 — isolation and gpg-agent lifecycle (REPRODUCED)

At 2026-09-22T09:36:09Z, scratch-only hostile HOME `.gnupg/gpg.conf` and hostile `GNUPGHOME`, each with attacker-signed record, both refused `fubuki-review-signature-invalid`; `0→0` lane-owned agents; 13 ms. This supports RV:136-137's minimal environment and `--no-options`. The observed production temporary home mode was `0o700->0o700` (RV:129). Re-run at 2026-09-22T10:11:49Z matched: both hostile channels refused, normal/candidate runs were accepted, and every lane-owned census remained `0→0`.

Per override, only `gpg-agent --homedir /tmp/vg2c-b/...` processes were counted. All valid-signature one-call runs:

```
normal production: ACCEPTED; agents 0->0; 13 ms
scratch candidate `gpgconf --homedir <home> --kill all`: ACCEPTED; agents 0->0; 21 ms
scratch candidate `--no-autostart`: ACCEPTED; agents 0->0; 9 ms
```

Independent direct census at 2026-09-22T09:37:54Z: `VERIFY ACCEPTED WALL_MS 14`, then `AGENTS_AFTER_TEMP_DELETE 0`. All agents I created were killed by their scratch homedirs; final lane-owned census was empty.

**F3 — FOLLOW-UP, SOLID local measurement.** The brief's sandbox GnuPG 2.4.4 fact (one survivor/call, 28 total) did not reproduce on PC GnuPG 2.4.7. Re-run the per-temp-home census on 2.4.4 before accepting or declining cleanup. If reproduced, `gpgconf --homedir <home> --kill all` is the more deterministic candidate. This does not fail the PC-host contract.

## Finding inventory

1. F1 — **BLOCKER**, SOLID: PATH-shadowed fake gpg accepts unsigned record; full predicate met.
2. F2 — **BLOCKER**, SOLID: TOCTOU FIFO produces 10-second hang; full predicate met.
3. F3 — **FOLLOW-UP**, SOLID locally: gpg-agent discrepancy across GnuPG venues.
4. I1 — **INFO**, SOLID: inclusive 1 MiB boundary and pre-check reason taxonomy.
5. D1 — **INFO/DISCREPANCY**, SOLID: six-file set-id mismatch; count/list verified.
6. D2 — **INFO/DISCREPANCY**, SOLID: a direct re-run initially omitted the required FUBUKI root inputs and failed closed (`16 errors`; then `11 passed, 38 errors`). The corrected declared-input re-runs passed 16 and 49; this operator error did not produce a green claim.
7. L1 — **INFO**, SOLID: report-lint at 2026-09-22T10:12Z returned `14 refs — OK 13, NEAR 1, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (at dab9803)`; rc 0. The sole NEAR was report line 32 against review.py line 137, a claim token within one line of the cited range; no MISS-hint fix was applicable.

## Deliberately not done

Master items 2–4, 7, and 9–13 belong to other lanes. I did not run their status-shape, record-shape, integration, taxonomy, mutation, repeat-gate, or final report-lint tasks. No committed file, test, ledger, owner key, service, credential, commit, or push changed. The lane report itself is the only untracked worktree artifact.

## Follow-ups

1. Repair F1 with fixed gpg executable resolution plus fake-PATH regression.
2. Repair F2 with nonblocking FD regular-file verification plus forced FIFO-race regression.
3. Re-measure F3 on GnuPG 2.4.4.

Retro: F1/F2 are real defects; coordinator must run `/bug-echo` and record the applicable anti-pattern rows before close. No new reusable skill lesson.

GATE RECOMMENDATION (items 1, 5, 6, 8 only): NOT-READY — F1 and F2 satisfy every blocking-predicate condition. This is a recommendation; coordinator owns the gate decision.
