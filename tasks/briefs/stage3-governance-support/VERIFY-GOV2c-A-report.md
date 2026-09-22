# VERIFY-GOV2c-A adversarial verification report

PIN: `dab9803f78dfd6d7844b4e8d088ebdfb5541de92` (GOV2c paths byte-identical to `b1dba7b`).

Venue: owner's PC lane worktree; `/usr/bin/gpg` is `gpg (GnuPG) 2.4.7`; route is `agentfactory-verify-local`. D-028 assigns xhigh to verification, but this local vLLM route fixes effort server-side and does not permit per-lane selection.

## Item 1 — premise

REPRODUCED. `git diff --exit-code b1dba7b dab9803 -- RV TR RM PK` exited 0. The change history is `b1dba7b` then `756d516`; the GOV2c hunk set is RM `@@ -24`, `@@ -35`, `@@ -43`; RV `@@ -12`, `@@ -31`, `@@ -57`; TR `@@ -180`. At `2026-09-22T08:57:49Z`, SHA-256 prefixes were RV `010054c04f697c8c`, TR `ea9e0a466a4807d2`, RM `662fd187a827461b`, PK `5d8cf21468adb55e`.

REPRODUCED. With the PC venue exports and xdist, `tests/test_governance_review.py` collected 16 (`set=ce6a68f1998d`) and passed: `16 passed in 0.79s` at `2026-09-22T08:57:14Z`. The six-file set collected 49 but the current `pc_suite.sh set-id` reports `892ef4ebb5b8`, not the brief's stale `f3baa8cf79c7`; it passed: `49 passed in 0.94s` at `2026-09-22T08:57:15Z`.

Reviewed reachability: `load_packet` computes canonical bytes and their hash, invokes `verify_review`, and only then returns `reviewed=True` (`PK:136-156`). Ripwire maps `load_packet` plus 14 direct test callers of `verify_review`; GitNexus returned `risk: UNKNOWN`, target not found in the clone index, so no low-risk inference is made. The contract implementation enters `try` before snapshots (`RV:121-149`) and assigns `record = json.loads(record_bytes.decode("utf-8"))` while parsing those record bytes (`RV:168-179`).

DISCREPANCY: master premise calls the six-file set `f3baa8cf79c7`; this PC checkout measured the same six paths as `892ef4ebb5b8`, 49 collected and passed. The tests/count are reproduced; the set-id premise is stale.

## Item 2 — single snapshot (F1)

REPRODUCED through the real `verify_review` function and gpg 2.4.7, using 400 calls per hostile writer. At `2026-09-22T09:04:57Z`: `record-flip: accepts=0/400`, `signature-flip: accepts=0/400`, and `hardlink-swap: accepts=0/400`. Each refusal was `fubuki-packet-unreviewed` or `fubuki-review-signature-invalid`; no unsigned `reviewed:true` record became trusted. The harness preserved the production subprocess contract and killed only the temporary per-call gpg homes it created, by exact homedir.

REPRODUCED. A `reviews_dir` symlink to an attacker-controlled directory is followed: a valid owner-signed record is accepted, while an unsigned replacement is refused as `fubuki-review-signature-invalid`. This is not an F1 hole on the frozen contract: following an ancestor directory is equivalent to granting its writer store access, and the signature still binds the snapshot bytes. Final-component symlinks remain separately refused by `O_NOFOLLOW`; the read block begins `try` (`RV:121-125`) after `_read_no_symlink` is defined (`RV:51-67`).

## Item 3 — status-line acceptance (F2/F6)

REPRODUCED through real gpg 2.4.7 and `verify_review` at `2026-09-22T09:08:28Z`. Owner-over-different-bytes produced `BADSIG`, rc 1, and `fubuki-review-signature-invalid`. A raw newline in `--sig-notation` was rejected by gpg at signing (`rc=2`); a notation containing `[GNUPG:] GOODSIG injected` reached status output only as `NOTATION_DATA [GNUPG:]%20GOODSIG%20injected`, beside a real GOODSIG line for the valid signature. It did not create another status line.

REPRODUCED. An expired owner key yielded `EXPKEYSIG` plus `VALIDSIG`, rc 0, and production refused. An expired detached signature yielded `EXPSIG`, rc 1, and production refused. A revoked owner key yielded `REVKEYSIG`, rc 0, and production refused. Thus `verified.returncode != 0 OR not real GOODSIG` is required and correctly rejects all three shapes (`RV:159-165`).

REPRODUCED. A signing subkey passed. The pasted real `VALIDSIG` split confirmed field 2 was the signing subkey fingerprint `9C5DFD6F03A5441DE0107C19D1F18E4EDB4AE6E9`; the last field was its primary `FFB1B4DFC449E0873E4BDCBDFDF90A8B5F7643FF`. `_keyring_shape` collects both `fpr:` lines (`RV:70-85`), and `RV:162` reads field 2, so the path accepts an authorized signing subkey as required.

REPRODUCED. Two duplicate armor blocks deduplicated to one imported primary and passed. A key plus its post-sign revocation certificate was refused. An empty owner file was `fubuki-owner-key-invalid`; a binary (`--export`, non-armored) owner file passed. No F2/F6 violation reproduced.

## Item 4 — detached-signature boundary

REPRODUCED through real gpg 2.4.7 and `verify_review` at `2026-09-22T09:22:50Z`. A clearsigned unrelated owner message and an inline-signed unrelated owner message each produced the exact gpg stderr `gpg: not a detached signature`, rc 2, and production `fubuki-review-signature-invalid`. A combined `.asc` holding the owner signature over unrelated bytes plus an attacker signature over the record produced owner `BADSIG`, rc 1, and production refusal. A binary detached signature over the record passed.

REPRODUCED. `git cat-file -t accepted/S0-01` reported `tag`; its 507-byte tag object contains an armored PGP block. Offering that block over a review record produced owner `BADSIG`, rc 1, and production refusal: the tag signature remains bound to its tag payload, not arbitrary record bytes.

REPRODUCED. A valid owner detached signature followed by a second attacker armored block produced first `GOODSIG`/`VALIDSIG`, then `ERRSIG`/`NO_PUBKEY`, final rc 2; `verify_review` refused with `fubuki-review-signature-invalid`. That conservative result is correct under the real gpg consumer and rejects ambiguous appended blocks.

## Findings inventory

F1 — INFO (SOLID): the six-file test-set identity in the brief is stale. Contract mapping: none; this does not contradict GOV2c. Canonical path: the exact six files collected on this PIN. Material effect: none on code or test outcome. Reproduction: `pc_suite.sh set-id --` over those files returned `892ef4ebb5b8`; pytest collected 49 and passed. Suggested fix: correct the brief/ledger set id.

F2 — INFO (SOLID): `reviews_dir` itself may be a symlink. Contract mapping: none; F8 covers record, signature, and owner-key paths, not their common parent. Canonical path: real `verify_review` plus real gpg. Material effect: valid signed bytes accept and an unsigned replacement is refused. Reproduction: item 2's symlink control. Suggested fix: none; document only if the store-parent threat model later changes.

## Follow-ups

None from items 1–4.

## Not done

Items 5–13 belong to the other split lanes and were deliberately not executed here. This lane did not run the fake-PATH, special-file, record-shape, keyring/agent, integration, taxonomy, mutation, repeated-gate, or master-report-lint items.

## Hygiene and discrepancy

Scratch harnesses stayed under `/tmp/vg2c-a/`; each temporary owner home was killed with `gpgconf --homedir <home> --kill all` and each per-call temporary verifier home was killed by its exact homedir before deletion. No production files were edited; this report is the only worktree change. AP screen at `2026-09-22T09:12:52Z`: AP-51 on the required full PIN at line 3, classified RUN/benign identifier. `report_lint` at `2026-09-22T09:19:31Z`: `8 refs — OK 8, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (at dab9803)`.

DISCREPANCY: the master premise's six-file `f3baa8cf79c7` does not match this checkout's measured `892ef4ebb5b8`; 49 tests collected and passed, so the stale identity does not invalidate the executable premise.

RETRO: nothing to bake. The only discrepancy is an evidence-set identifier, classified above; no new implementation anti-pattern was found in items 1–4.

GATE RECOMMENDATION (items 1-4 only): MERGE-READY
