# VERIFY-GOV2c-C — independent verify of GOV2c (split 3 of 3: items 1, 7, 9, 10, 11, 12, 13)

PIN: dab9803 (worktree .lanes/pc-verify-gov2c-c.md--dab9803/tree, clean at launch)
Venue: PC host, gpg 2.4.7 (/usr/bin/gpg, libgcrypt 1.11.0-unknown), python /home/rocco/venv-agent-factory/bin/python (3.11.14).
Effort note (D-028): this lane runs on the local verify route `agentfactory-verify-local`; on the vLLM route the
reasoning effort is the server default and cannot be set per lane — the xhigh pin of D-028 is NOT applied here;
the coordinator's routing table does not reach this single-model host.

## Item 1 — PREMISE (re-measured at dab9803)

Commands + output (all in the lane worktree at dab9803):

```
git rev-parse HEAD → dab9803f78dfd6d7844b4e8d088ebdfb5541de92
git log --format='%h %ad %s' --date=short -3 -- src/agent_factory/governance/review.py tests/test_governance_review.py docs/governance/reviews/README.md
  b1dba7b 2026-09-17 GOV2c: close VERIFY-GOV2b's two blockers in the review binding (TOCTOU + GOODSIG substring)
  756d516 2026-09-16 GOV2b: source the reviewed bit from a first-party owner-signed record (VERIFY-GOV1 F2; owner: go with b)
git log --oneline b1dba7b..dab9803 -- src/agent_factory/governance/review.py tests/test_governance_review.py docs/governance/reviews/README.md src/agent_factory/governance/packet.py
  (empty: the four files are byte-identical since GOV2c = b1dba7b)
git diff b1dba7b^ b1dba7b -- <the three paths> | grep -E '^diff|^@@'
  RM: @@ -24,7 +24,7 @@  @@ -35,6 +35,9 @@  @@ -43,7 +46,14 @@
  RV: @@ -12,12 +12,22 @@  @@ -31,12 +41,50 @@  @@ -57,37 +105,72 @@
  TR: @@ -180,3 +180,100 @@
sha256 first-16 at dab9803: RV 010054c04f697c8c · TR ea9e0a466a4807d2 · RM 662fd187a827461b · PK 5d8cf21468adb55e
```

All four identities match the brief's premise block. gpg 2.4.7 confirmed on this host.
FUBUKI_OS_ROOT=/home/rocco/fubuki-pin/fubuki-os and FUBUKI_OTHER_ROOT=/home/rocco/fubuki-pin/fubuki-os-other both exist (verified).
pyproject.toml:15 `pythonpath = ["src"]` (the venv's pytest resolves the package from the worktree, no install needed).

Pytest sets (PC venue, `--basetemp /tmp/vg2c-c/bt`, FUBUKI exports set):

```
2026-09-22T09:49:04Z  tests/test_governance_review.py → 16 passed in 1.17s (rc 0)
2026-09-22T09:49:06Z  tests/test_governance_{bounds,packet,pin,pin_enforcement,projection,review}.py → 49 passed in 1.93s (rc 0)
set-id re-derivation: sha256("\n".join(sorted(files)) + "\n")[:12]
  one-file  → ce6a68f1998d  (== brief's set id)  ✓
  six-file  → f3baa8cf79c7  (== brief's set id)  ✓
```

Sandbox had 16 passed / 49 passed at 06:16Z and 08:48Z; the dead lane reported 16 / 49 at 4cc3fe2 — all agree with the
dab9803 re-run. Item 1 premise HOLDS. (Reproduced, not reviewed.)

## Item 7 — record shapes through real `verify_review` + real gpg 2.4.7

Reproduced with `/tmp/vg2c-c/item7_shapes.py`: a fresh throwaway `ed25519 sign` owner key signed EACH exact test record,
then the unmodified worktree's `agent_factory.governance.review.verify_review` read, verified, and parsed it. C0 was the
harness control and ACCEPTED, so subsequent outcomes exercise the parser after a real successful detached signature.

```
C0-valid-control                 ACCEPTED
C1-utf8-bom                      REFUSED fubuki-review-record-invalid
C2-trailing-byte                 REFUSED fubuki-review-record-invalid
C3-reviewed-int-1                REFUSED fubuki-packet-unreviewed
C4-reviewed-str-true             REFUSED fubuki-packet-unreviewed
C5-reviewed-list                 REFUSED fubuki-packet-unreviewed
C6-reviewed-float-1.0            REFUSED fubuki-packet-unreviewed
C7-dup-reviewed-last-true        ACCEPTED
C7b-dup-reviewed-last-false      REFUSED fubuki-packet-unreviewed
C8-record-uppercase-hash         REFUSED fubuki-review-hash-mismatch
C9-arg-uppercase-64hex           REFUSED fubuki-review-hash-invalid
C10-arg-dotdot-passwd            REFUSED fubuki-review-hash-invalid
C11-arg-slash                    REFUSED fubuki-review-hash-invalid
C12-arg-64chars-two-dots         REFUSED fubuki-review-hash-invalid
C13-arg-len-63                   REFUSED fubuki-review-hash-invalid
C14-arg-len-65                   REFUSED fubuki-review-hash-invalid
C15-arg-nul-byte                 REFUSED fubuki-review-hash-invalid
C16-arg-short                    REFUSED fubuki-review-hash-invalid
C17-arg-single-char              REFUSED fubuki-review-hash-invalid
C18-arg-empty                    REFUSED fubuki-review-hash-invalid
C19-hash-is-NaN                  REFUSED fubuki-review-hash-mismatch
C20-reviewed-is-Infinity         REFUSED fubuki-packet-unreviewed
C21-reviewed-nested-dict         REFUSED fubuki-packet-unreviewed
C22-two-keys-arg-first           ACCEPTED
C22b-two-keys-arg-second         REFUSED fubuki-review-hash-mismatch
2026-09-22T09:51Z harness exit 0; its own gpg homedir was killed by `gpgconf --homedir <scratch> --kill all` and deleted.
```

Exact reason strings from selected boundary cases: C1 `fubuki-review-record-invalid` (`Unexpected UTF-8 BOM`); C2
`fubuki-review-record-invalid` (`Extra data`); C8/C22b `fubuki-review-hash-mismatch`; C9-C18
`fubuki-review-hash-invalid` at `RV:102-103`, before a `record_path` is built; C3-C6/C7b/C20/C21
`fubuki-packet-unreviewed` at `RV:178-179`.

Duplicate `reviewed` keys: this does NOT falsify the current owner-trust claim. `json.loads` makes the last member
semantically authoritative, and the owner signed the complete ambiguous byte string; no store attacker can alter it.
It is an INFO hardening candidate for the owner-side review authoring procedure or a duplicate-key-rejecting JSON decoder,
not a contract-mapped blocker.

The record naming two hash-like keys passes only when the real `governance_hash` member equals the argument (C22), and
refuses if a differently named argument is passed (C22b). This matches `RV:174-176`: no alternate field authorizes a hash.
(Reproduced; no item-7 blocker.)

## Item 9 — `load_packet` integration

Code path: `PK:150-156` lint-checks, compiles with the pinned Fubuki canonicalizer, computes
`governance_hash(canonical)` at `PK:153-154`, calls the sole production consumer `verify_review` at `PK:155`,
and only then returns `Packet(canonical=canonical, hash=packet_hash, reviewed=True)` at `PK:156`. Literal production-package sweep found no other
reader of a review record or producer of `reviewed`; `projection.py` only refuses `packet.reviewed is false` at
`src/agent_factory/governance/projection.py:42-43`. A second exact caller sweep found the same sole runtime call.
Ripwire maps three test callers of `load_packet` (including `TR:167` and `TR:177`); GitNexus and code-review-graph
were unmapped because the clone's graph index is absent at this PIN (`Target 'load_packet' not found` / graph absent),
not treated as evidence of no caller.

Real integration probe (`/tmp/vg2c-c/item9_10.py`, fresh owner key, Fubuki pin verified before compile):

```
2026-09-22T10:13:22Z
I9-disk-different: True                         # only persona.package.json formatting/order changed
I9-canonical-equal: True
I9-hash-a: 18cb8a495ac14f030ce16bfda96107e25e489e874a65d971cc0bbe0dbe791dac
I9-hash-b: 18cb8a495ac14f030ce16bfda96107e25e489e874a65d971cc0bbe0dbe791dac
I9-load-packet-reformatted: ACCEPTED reviewed=True hash_matches=True
```

This is intended binding: review attests the canonical compiled packet, not incidental spelling/order of the source
manifest. It is explicit in `PK:110-122` and the existing canonicality discriminator is `tests/test_governance_packet.py:71-90`.
A substantive declared source-byte change rehashes and refuses old review records (`tests/test_governance_packet.py:93-102`).

Deployment implication, statically reviewed: `RV:37-41` derives the default owner key from a source-tree `parents[3]`
path. An installed package without the default owner key fails closed when `owner_key.is_file()` is false at `RV:111-112`, with
`fubuki-owner-key-missing`; the expected path is `docs/governance/owner-signing-key.asc`, so a Hermes projection deployment must package/configure the committed public key. This is
not a GOV2c behavioural defect because failure is closed, but it is a real release prerequisite. (Item 9 reproduced + reviewed.)

## Item 10 — error taxonomy (F7)

Every `GovernanceError` raise site in RV is reached by a current test or a real-path fresh control:

| RV site | reason | reaching discriminator |
|---|---|---|
| RV:103 | `fubuki-review-hash-invalid` | `TR:158-161` non-hex; item-7 C9-C18 hostile argument sweep |
| RV:110 | `fubuki-packet-unreviewed` | `TR:116-120` absent record; `TR:144-148` signed `reviewed:false` |
| RV:112 | `fubuki-owner-key-missing` | item-10 `I10-owner-key-missing` real path |
| RV:116 | `fubuki-review-gpg-unavailable` | `TR:260-266` missing executable |
| RV:126 | `fubuki-review-record-invalid` | `TR:269-279` O_NOFOLLOW symlink error |
| RV:144 | `fubuki-owner-key-invalid` | item-10 `I10-owner-key-invalid`, malformed armored input |
| RV:151 | `fubuki-review-gpg-unavailable` | item-10 `I10-fake-gpg-timeout-30s`, 31-second fake gpg → `subprocess.TimeoutExpired` |
| RV:155 | `fubuki-owner-key-ambiguous` | `TR:238-245` two owner keys |
| RV:164 | `fubuki-review-signature-invalid` | `TR:123-127` non-owner; `TR:137-141` tamper; `TR:209-235` revoked key |
| RV:170 | `fubuki-review-record-invalid` | item-7 C1/C2 and item-10 invalid UTF-8 after successful real signature |
| RV:172 | `fubuki-review-record-invalid` | `TR:248-257` owner-signed JSON list |
| RV:175-176 | `fubuki-review-hash-mismatch` | `TR:130-134`; item-7 C8/C22b |
| RV:179 | `fubuki-packet-unreviewed` | `TR:144-148`; item-7 strict-type sweep |

```
2026-09-22T10:13:22Z
I10-owner-key-missing: REFUSED reason='fubuki-owner-key-missing'
I10-owner-key-invalid: REFUSED reason='fubuki-owner-key-invalid'
I10-invalid-utf8: REFUSED reason='fubuki-review-record-invalid'
I10-fake-gpg-timeout-30s: REFUSED reason='fubuki-review-gpg-unavailable'
2026-09-22T10:13:52Z script exit 0; own gpg homedir and all scratch deleted
```

`record_path` containing NUL cannot reach `Path.is_file()` from this interface: `_is_governance_hash` at `RV:47-48`
rejects it at `RV:102-103`, confirmed item-7 C15. This is one execution-domain line, not a static assumption.
(Reproduced and mapped; no unreached taxonomy site remains.)

## Item 11 — mutation audit M1-M14

Isolation proof: all mutations were one-at-a-time in `/tmp/vg2c-c/rv/agent_factory/governance/review.py`; the worktree
was never edited. An initial run from the project root was VOID because pytest's `pythonpath = ["src"]` shadowed the
scratch package even though a standalone import named scratch. I discarded all those rows, switched pytest to an empty
`-c /tmp/vg2c-c/pytest-empty.ini` from the scratch cwd with the absolute test path, and re-ran every mutant. Final import:

```
IMPORT-PROOF rc=0 path='/tmp/vg2c-c/rv/agent_factory/governance/review.py'
```

Every final mutant compiled (`python -m py_compile` rc 0) and collected `16 tests` (collect rc 0) before execution.
Final mutation table, 2026-09-22T10:23:17Z–10:23:38Z:

| mutant | compiles / collected | final disposition | killed by existing test / required killer |
|---|---|---|---|
| M1 GOODSIG substring | yes / 16 | KILLED | `test_a_revoked_key_with_a_goodsig_notation_is_refused` (1 failed, 11 passed) |
| M2 drop owner fingerprint membership | yes / 16 | SURVIVED | killer `test_validsig_fingerprint_must_belong_to_owner`: sign with attacker, fake status `GOODSIG attacker` + `VALIDSIG attacker` while owner import/list remains real; assert `fubuki-review-signature-invalid` |
| M3 re-read record for parse | yes / 16 | KILLED | `test_toctou_a_flip_after_verify_does_not_grant_review` (1 failed, 10 passed) |
| M4 drop O_NOFOLLOW | yes / 16 | KILLED | `test_a_symlinked_record_is_refused` (1 failed, 15 passed) |
| M5 permit >1 primary owner key | yes / 16 | KILLED | `test_two_keys_in_the_owner_file_are_refused` (1 failed, 12 passed) |
| M6 truthiness instead of identity | yes / 16 | SURVIVED | killer `test_reviewed_integer_one_is_refused`: owner-sign `reviewed: 1`; assert `fubuki-packet-unreviewed` (item-7 C3 is the live discriminator) |
| M7 compare only 8-hex hash prefix | yes / 16 | SURVIVED | killer `test_hash_prefix_collision_is_refused`: owner-sign a distinct 64-hex hash sharing first 8 chars; assert `fubuki-review-hash-mismatch` |
| M8 inherit caller environment | yes / 16 | KILLED | `test_review_signed_by_non_owner_is_refused` became wrong reason under lane-owned hostile GNUPGHOME (1 failed, 2 passed) |
| M9 move status-fd to stderr | yes / 16 | KILLED | `test_valid_owner_signed_review_passes` (1 failed, 0 passed) |
| M10 ignore gpg nonzero rc | yes / 16 | SURVIVED | killer `test_nonzero_gpg_with_good_status_is_refused`: fake gpg returns owner GOODSIG/VALIDSIG with rc 1; assert `fubuki-review-signature-invalid` |
| M11 raise size ceiling to 1 TiB | yes / 16 | SURVIVED | killer `test_oversize_signed_record_is_refused`: owner-sign valid JSON over `_MAX_RECORD_BYTES`; assert `fubuki-review-record-invalid` through `verify_review` |
| M12 truncate stored fingerprints | yes / 16 | KILLED | `test_valid_owner_signed_review_passes` (1 failed, 0 passed) |
| M13 stop prechecking signature file | yes / 16 | SURVIVED | killer `test_missing_signature_keeps_unreviewed_reason`: valid record with absent `.asc`; assert exact `fubuki-packet-unreviewed` (mutant reaches `fubuki-review-record-invalid`) |
| M14 drop chmod 0700 | yes / 16 | EQUIVALENT-declared | live `TemporaryDirectory(dir=/tmp/vg2c-c)` mode was `0o700`; no output/state change on this host |

Totals: 7 killed (M1/M3/M4/M5/M8/M9/M12), 6 survived (M2/M6/M7/M10/M11/M13), 1 equivalent (M14).
The six surviving cases are test-coverage gaps, not demonstrated defects in unmodified RV. They therefore fail the
complete blocking predicate's canonical-production-defect/material-effect condition and are FOLLOW-UPs, not blockers.

Restoration and worktree identity:

```
RESTORE copy_sha256=010054c04f697c8c3dad4c7c9f3af71fc30f8fdccb76ce5eccca4013a4db654c
        source_sha256=010054c04f697c8c3dad4c7c9f3af71fc30f8fdccb76ce5eccca4013a4db654c equal=True
worktree RV first16 after audit: 010054c04f697c8c
```

## Item 12 — fresh gates on the unmodified worktree

FUBUKI_OS_ROOT=/home/rocco/fubuki-pin/fubuki-os and FUBUKI_OTHER_ROOT=/home/rocco/fubuki-pin/fubuki-os-other
were exported on every run; all used `--basetemp /tmp/vg2c-c/bt`. `${PIPESTATUS[0]}` was captured from every piped run.

```
2026-09-22T10:28:52Z  set ce6a68f1998d  tests/test_governance_review.py
  16 passed in 1.17s  PIPESTATUS=0
2026-09-22T10:28:53Z  set ce6a68f1998d  tests/test_governance_review.py
  16 passed in 1.15s  PIPESTATUS=0
2026-09-22T10:28:55Z  set f3baa8cf79c7
  tests/test_governance_bounds.py tests/test_governance_packet.py tests/test_governance_pin.py
  tests/test_governance_pin_enforcement.py tests/test_governance_projection.py tests/test_governance_review.py
  49 passed in 1.89s  PIPESTATUS=0
2026-09-22T10:28:57Z  worktree RV first16 = 010054c04f697c8c
```

The two ce6a68f1998d runs agree bitwise on count/outcome (16 passed, rc 0); the six-file set has the expected 49.

## Finding inventory

### F1 — INFO — duplicate JSON keys are last-member-wins

Evidence level: SOLID, reproduced through unmodified `verify_review` + real gpg 2.4.7. Contract mapping: none.
Canonical path: yes. Material effect: the owner-signed record with `"reviewed": false, "reviewed": true` accepts;
reversed order refuses. Reproduction: item-7 C7/C7b. Blocking predicate: fails contract mapping and does not let an
unsigned/store attacker change owner-signed bytes. Suggested fix: optional duplicate-key rejection in JSON decoding and
an owner-procedure test; not required for GOV2c readiness.

### F2 — FOLLOW-UP — six contract-relevant mutants survive the committed 16-test suite

Evidence level: SOLID, independently reproduced with scratch import proof, compile checks, collection checks, and fresh
execution. Contract mapping: F1/F2/F5/F6/F7/F8 test adequacy. Canonical path: mutation-only discriminator; the unmodified
production path is not defective. Material effect: the named mutants would weaken owner binding, strict booleans, exact
hash binding, gpg rc checks, record size, or missing-signature taxonomy, but none is present in the current RV.
Reproduction: item-11 table, M2/M6/M7/M10/M11/M13. Blocking predicate: fails canonical-production-defect/material-effect
for this increment; no static suspicion may cause NOT-READY. Suggested fix: add the six killer tests listed in item 11.

### F3 — FOLLOW-UP — source-tree-relative default owner key is a deployment prerequisite

Evidence level: SOLID static path + real `fubuki-owner-key-missing` control. Contract mapping: integration/deployment only,
not a GOV2c security-property failure. Canonical path: yes; missing key fails closed. Material effect: an installed Hermes
projection without the repo docs tree cannot load a reviewed packet. Reproduction: `RV:37-41`, item-10
`I10-owner-key-missing`. Blocking predicate: no false approval/evidence corruption; deployment packaging is outside this
repair boundary. Suggested fix: package the public key or thread an immutable configured key path at the projection entry.

## FOLLOW-UPS

1. Add committed killer tests for M2, M6, M7, M10, M11, and M13 exactly as specified in the mutation table.
2. Decide whether signed records with duplicate JSON members should be refused; if yes, use a duplicate-detecting decoder
   and add C7/C7b regressions.
3. Ensure the Hermes projection deployment ships `docs/governance/owner-signing-key.asc` or supplies an immutable explicit path.

## Deliberately skipped / NOT-done

- Master items 2-6 and 8 belong to the other two split lanes and were not started. This lane therefore does NOT claim to
  verify the race suite, status-line exotic forms, detached-signature boundary, PATH shadowing, FIFO/special-file window,
  hostile keyring, or gpg-agent orphan behaviour.
- No subagents, network calls, live model calls, bridge tools, production services, committed owner private key, commits,
  pushes, stashes, checkouts, resets, or outward actions.
- No production file changed. All keys were throwaway. Harnesses used homedir-scoped cleanup; a final pid-scoped census
  found one residual lane-owned `gpg-agent` from an earlier aborted C7 harness, terminated only PID 1746046, then found
  `OWNED-AFTER count=0`. No process outside `/tmp/vg2c-c/afgr-c7-*` or `afgr-c9-*` was signalled.
- `coverage.py` is not installed in the shared venv, so taxonomy mapping used explicit real-path controls plus exact
  source/test site mapping rather than branch instrumentation. No install was attempted.

## Hygiene / discrepancies

- Premise identities and set IDs reproduced exactly; no contract-invalidating premise conflict.
- The first item-11 execution was VOID: pytest's project `pythonpath = ["src"]` shadowed the scratch mutant despite a
  standalone scratch import proof. Those rows are discarded. The final audit used isolated pytest config and its own
  scratch-path import proof. This is an anti-hollow-green harness correction, not a product finding.
- Item-9 experiment 1 changed a declared source (`compile-request.json`) and correctly changed the canonical hash; it was
  discarded as the wrong shape. Experiment 2 changed only manifest JSON formatting/order and proved canonical equality.
- Code-intelligence discrepancy: the lane's GitNexus/code-review-graph indices were unavailable for these symbols; graft,
  ripwire, the lane-context pack, literal production sweeps, and direct source/test ranges supplied the map. No absence
  claim relies on GitNexus.
- AP screen: RV hits AP-32 at hash validation and AF-AP-110/AP-1 at the forwarded PATH environment; those are the known
  exact seams under master items 5/7, not new findings from this split. TR test screen: 0 hits.

## Blocking-predicate application

No finding in items 1, 7, 9-13 satisfies all five conditions. F1 has a real canonical-path effect but no contract breach
or attacker-controlled state transition. F2 has concrete mutation discriminators but no defect in the current production
implementation. F3 fails closed and its packaging fix is outside this focused GOV2c repair. The coordinator must combine
this bounded recommendation with split lanes A/B; it is not a final verdict.

## Item 13 — report + lint

Bounded lint completed in three rounds (initial + two fixes), using `--rev dab9803` and all four required maps.
Final pasted line:

```
report_lint: 44 refs — OK 36, NEAR 0, MISS 0, UNCHECKABLE 8, UNRESOLVED 0 (at dab9803)
PIPESTATUS=0
```

GATE RECOMMENDATION (items 1, 7, 9-13 only): MERGE-READY-WITH-FOLLOWUPS
