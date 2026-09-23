# VERIFY-AF-AP-127-R1 + REPIN-a-R2 — verify report (task #182, lane verify-182)

Brief: `tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-brief.md` (e4ce195). PIN c84f161. Components: (A) AF-AP-127-R1 =
9932f34 (the key rule of `scripts/transcript_export.py`); (B) REPIN-a-R2 = 9c991a2 (the R3(c) words at three sites).
Lane: sandbox, Opus 5.5, shared tree, no worktree. Started 2026-09-23T11:26:51Z (`date -u`).

STATUS: COMPLETE. Gate recommendations: (A) `MERGE-READY-WITH-FOLLOWUPS`; (B) `MERGE-READY-WITH-FOLLOWUPS`. No finding meets the
whole blocking predicate; no CONTRACT-DEFECT. Written incrementally, item by item.

## 1. PREMISE

**Verdict: MATCHES on every measured line. No CONTRACT-INVALID for A or B.** Re-measured 2026-09-23 11:27Z-11:29Z, tree HEAD e4ce195
(the brief's own commit on top of 5090671; neither touches a boundary file).
```
$ date -u; git rev-parse --short HEAD; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
Wed Sep 23 11:26:51 UTC 2026
e4ce195
c84f161
$ sha256[:16] lines (at c84f161 | in the tree), then git blob (at c84f161 | git hash-object of the tree file)
55989ae1c096bfc4   115 55989ae1c096bfc4   115 scripts/transcript_export.py                          31a3e3e9d7cf 31a3e3e9d7cf
e3ae36b40fded64b   151 e3ae36b40fded64b   151 tests/test_transcript_export.py                       8b92b7e5c717 8b92b7e5c717
3f7b5128b1dcd612    96 3f7b5128b1dcd612    96 harness-ports/tests/test_hermes_session_export.py     0d7893bf5d2e 0d7893bf5d2e
3e195a5821b2e945   104 3e195a5821b2e945   104 harness-ports/bin/hermes-session-export.py            04326ece5b7a 04326ece5b7a
6c0a3ff07156f9ad   173 6c0a3ff07156f9ad   173 upstream.lock.yaml                                    78f1495271fa 78f1495271fa
34295252a1aab29f   253 34295252a1aab29f   253 tests/test_upstream_lock_lane_runtime.py              e975710f3c72 e975710f3c72
b6cca36449c0b9cc   149 b6cca36449c0b9cc   149 tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md   7231e6c8b3b4 7231e6c8b3b4
160d2ce0b22b4cee   529 160d2ce0b22b4cee   529 harness-ports/bin/pc-lane.sh                          183f337eff91 183f337eff91
$ git diff --stat 9932f34^ 9932f34; git diff --stat 9c991a2^ 9c991a2
 harness-ports/tests/test_hermes_session_export.py |  5 ++++
 scripts/transcript_export.py                      |  9 +++++---
 tests/test_transcript_export.py                   | 28 +++++++++++++++++++++++
 3 files changed, 39 insertions(+), 3 deletions(-)
 tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md | 3 ++-
 tests/test_upstream_lock_lane_runtime.py            | 2 +-
 upstream.lock.yaml                                  | 2 +-
 3 files changed, 4 insertions(+), 3 deletions(-)
$ git diff --name-only c84f161 HEAD
scripts/gate_files.txt
scripts/no_laya_in_gates.py
tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-brief.md
tasks/briefs/laya/J1-0-R4-report.md
tests/test_no_laya_in_gates.py
$ (seams) scripts/transcript_export.py:29 `-----BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----.*?` ; tests/test_transcript_export.py:122 KEY_FAMILIES,
  :127 test_every_key_family_is_scrubbed_whole, :139 test_key_block_after_a_credential_keyword_is_scrubbed_whole ;
  harness-ports/tests/test_hermes_session_export.py:87 the F1 check `VERIFY-AF-AP-127 F1` ; harness-ports/bin/hermes-session-export.py:23 SCRUB_SRC ;
  upstream.lock.yaml:173 `verified:` ; tests/test_upstream_lock_lane_runtime.py:58 the (c) constant `110 PC lane directories` ; harness-ports/bin/pc-lane.sh:217-218 `PROMPT_FILE` ;
  tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md:8 "LATEST launch"                       (all at the brief's lines)
$ gates, once (the item-11 runs carry the set ids)
13 passed in 0.64s                                   (tests/test_transcript_export.py)
test_hermes_session_export: 15 checks passed  rc=0
16 passed in 0.18s                                   (tests/test_upstream_lock_lane_runtime.py)
$ ancestry
2d10a2c IS ancestor of 012d455b      9932f34 NOT ancestor of 012d455b      9932f34 IS ancestor of c84f161      9c991a2 IS ancestor of c84f161
2d10a2c 09-23 02:56 AF-AP-127 exporters: scrub the whole text, then cap; …      012d455 09-23 03:56 transcripts: scrubbed sandbox chat digests
$ git log 2d10a2c..c84f161 -- transcripts/pc  -> 221e68b 09-23 03:53 S0-02 B9 landed …
$ git log 9932f34..c84f161 -- transcripts ; git log c84f161..HEAD -- transcripts     -> (no output, both)
$ git ls-files transcripts | sed 's#/[^/]*$##' | sort | uniq -c
    104 transcripts/pc
     16 transcripts/sandbox
```
New fact from the pack (`/tmp/vr182/pack.md`, crg `callers_of scrub`): `scrub` has a THIRD consumer the brief does not name,
`harness-ports/bin/qwen_matrix.py:126` `_scrub_messages` (the Qwen matrix corpus builder, PC-side, not a committed path). It loads the
same file by path and fails closed with a named `MatrixError` (`harness-ports/bin/qwen_matrix.py:135-136`). Recorded as INFO (I-1).
No committed transcript was written after 9932f34: every committed file was exported under an earlier rule (item 3 measures it).

## 2. A — armor families through both real exporters

**Verdict: C3 HOLDS for every family in the frozen list, through both real exporters, in every shape that keeps a well-formed BEGIN
and END: 154 cells, 0 body lines on disk, a placeholder in each (SOLID).** Every leak in the matrix comes from a label or a shape
outside the frozen list: the `X9.42 DH PRIVATE KEY` label (a period in it; no tool here writes it), a doubled space inside
`PRIVATE KEY`/`KEY BLOCK`, a nested block (the KNOWN F2 class), and two adjacent formats whose armor names no PEM key.

**Labels, from primary sources in this sandbox** (2026-09-23 11:3xZ):
- `/usr/include/openssl/pem.h:32-56` (OpenSSL 3.0.13), private or secret: `ANY PRIVATE KEY` (:38), `RSA PRIVATE KEY` (:40), `DSA PRIVATE
  KEY` (:42), `ENCRYPTED PRIVATE KEY` (:46), `PRIVATE KEY` (:47), `EC PRIVATE KEY` (:54). Secret-bearing, no key word: `SSL SESSION
  PARAMETERS` (:50, carries the TLS master secret). Public or non-secret: the other 19 (item 3).
- `strings /lib/x86_64-linux-gnu/libcrypto.so.3` (a second source the brief did not name) adds `ED25519`, `ED448`, `X25519`, `X448`,
  `SM2` and `X9.42 DH` `PRIVATE KEY`, and their `PUBLIC KEY` twins. Throwaway keys show what the 3.0.13 CLI actually WRITES: `genpkey`
  writes `PRIVATE KEY` for all ten algorithms tried; `pkey -traditional` writes `RSA`/`DSA`/`EC PRIVATE KEY` (SM2 as `EC`) and refuses
  the rest (`DHX`: `PEM_write_bio_PrivateKey_traditional:unsupported public key type`). So the digit labels and `X9.42 DH PRIVATE KEY`
  are labels the library knows, not labels this CLI writes.
- `strings /usr/bin/gpg | grep -- 'PGP '` (GnuPG 2.4.4): `PGP PRIVATE KEY BLOCK`, `PGP SECRET KEY BLOCK` (secret); `PGP PUBLIC KEY
  BLOCK`, `PGP SIGNATURE`, `PGP MESSAGE`, `PGP SIGNED MESSAGE`, `PGP ARMORED FILE` (non-secret).
- OpenSSH: `ssh-keygen` is ABSENT (F15, KNOWN). New here: the venv's `cryptography` 50.0.1 writes a REAL `OPENSSH PRIVATE KEY` (a
  throwaway ed25519 and rsa-3072), with **64-column** lines. `ssh-keygen` writes 70 (the format; not probed): a FAKE 70-column row
  covers it. The SSH.com label `---- BEGIN SSH2 ENCRYPTED PRIVATE KEY ----` (four dashes and a space; `ssh-keygen -i` reads it) is
  taken from the format, not probed.

**Keys.** THROWAWAY keys made for this test only under `/tmp/vr182/keys` (openssl genpkey/pkey/rsa/pkcs8; gpg `--quick-gen-key` in a
temporary `GNUPGHOME=/tmp/vr182/g`, exported with `--armor`, one with `--comment`/`--emit-version`; `cryptography` for OpenSSH).
Relabels (the six libcrypto-only labels, `ANY PRIVATE KEY`, `PGP SECRET KEY BLOCK`) reuse a throwaway body under a new label. FAKE
random base64 for the 70-column OpenSSH, `SSL SESSION PARAMETERS` and the SSH.com rows. No body is printed anywhere.

**Harness** `/tmp/vr182/h2.py`: each (family, shape) is one synthetic JSONL through the REAL CLI `scripts/transcript_export.py`
(`--transcript … --out /tmp/vr182/… --cap 1000000`), and one synthetic `state.db` (the test's `sessions`/`messages` columns) through
the REAL CLI `harness-ports/bin/hermes-session-export.py` (`--cap 1000000 --tool-body-cap 1000000`), the case text in BOTH an
assistant message body and a tool body. A body line is "left" when any 8-character window of it is in the written file.
```
$ python3 h2.py /tmp/vr182/w2 big      -> rows 307 md5 36a9d09c9f17a77147661477dd4e0103 caps big
$ python3 h2.py /tmp/vr182/w2b big     -> rows 307 md5 36a9d09c9f17a77147661477dd4e0103 caps big     (rerun: identical)
$ python3 h2.py /tmp/vr182/w2p prod    -> rows 307 md5 36a9d09c9f17a77147661477dd4e0103 caps prod    (default caps 4000 / 3000 + --tool-body-cap 3000)
cells where sandbox == PC message == PC tool body: 307/307
big : lines left sandbox/pc-msg/pc-tool = 1232 1232 1232
prod: lines left sandbox/pc-msg/pc-tool = 1232 1232 1232
frozen-list families x well-formed shapes: 154 cells; lines left: 0 ; placeholders 0 in: 0
```
The table (one exporter shown; the other two are identical in all 307 cells). Cell = body lines left/total . placeholders . the text
after the block kept (k) or lost (L) [. the prose between two blocks k/L]. Shapes: json\n = a service-account JSON string with literal
`\n`; repr\\n = a Python repr with `\\n`; hdrs = `Proc-Type:`/`DEK-Info:` (PEM) or `Version:`/`Comment:` (PGP); END=priv / END=pub =
the END line carries another private / a public label; 2B cut = a first block cut short, then a whole second block; 2B nest = a whole
block inside another; sp:type / sp:key / sp:block = one inner space doubled before PRIVATE / between PRIVATE and KEY / between KEY and
BLOCK.
```
family                         |   plain   |   crlf    |   yaml    |   quote   |  json\n   |  repr\\n  |   hdrs    | two+prose | END=priv  |  END=pub  |  2B cut   |  2B nest  |  sp:type  |  sp:key   | sp:block
RSA PRIVATE KEY (PKCS#1)       | 0/25.1.k  | 0/25.1.k  | 0/25.1.k  | 0/25.1.k  | 0/25.1.k  | 0/25.1.k  | 0/25.1.k  |0/50.2.k.k | 0/25.1.k  | 0/25.1.L  | 0/37.1.k  | 10/50.1.k | 0/25.1.k  | 20/25.0.k |     -
RSA PRIVATE KEY legacy-enc     | 0/25.1.k  | 0/25.1.k  | 0/25.1.k  | 0/25.1.k  | 0/25.1.k  | 0/25.1.k  | 0/25.1.k  |0/50.2.k.k | 0/25.1.k  | 0/25.1.L  | 0/37.1.k  | 11/50.1.k | 0/25.1.k  | 21/25.0.k |     -
DSA PRIVATE KEY                | 0/18.1.k  | 0/18.1.k  | 0/18.1.k  | 0/18.1.k  | 0/18.1.k  | 0/18.1.k  | 0/18.1.k  |0/36.2.k.k | 0/18.1.k  | 0/18.1.L  | 0/27.1.k  | 7/36.1.k  | 0/18.1.k  | 15/18.0.k |     -
EC PRIVATE KEY (SEC1)          |  0/3.1.k  |  0/3.1.k  |  0/3.1.k  |  0/3.1.k  |  0/3.1.k  |  0/3.1.k  |  0/3.1.k  | 0/6.2.k.k |  0/3.1.k  |  0/3.1.L  |  0/4.1.k  |  2/6.1.k  |  0/3.1.k  |  3/3.0.k  |     -
PRIVATE KEY (PKCS#8 RSA)       | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  |0/52.2.k.k | 0/26.1.k  | 0/26.1.L  | 0/39.1.k  | 13/52.1.k |     -     | 21/26.0.k |     -
PRIVATE KEY (PKCS#8 ED25519)   |  0/1.1.k  |  0/1.1.k  |  0/1.1.k  |  0/1.1.k  |  0/1.1.k  |  0/1.1.k  |  0/1.1.k  | 0/2.2.k.k |  0/1.1.k  |  0/1.1.L  |  0/2.1.k  |  0/2.1.k  |     -     |  1/1.0.k  |     -
ENCRYPTED PRIVATE KEY          | 0/28.1.k  | 0/28.1.k  | 0/28.1.k  | 0/28.1.k  | 0/28.1.k  | 0/28.1.k  | 0/28.1.k  |0/56.2.k.k | 0/28.1.k  | 0/28.1.L  | 0/42.1.k  | 11/56.1.k | 0/28.1.k  | 22/28.0.k |     -
ANY PRIVATE KEY                | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  |0/52.2.k.k | 0/26.1.k  | 0/26.1.L  | 0/39.1.k  | 13/52.1.k | 0/26.1.k  | 21/26.0.k |     -
ED25519 PRIVATE KEY            | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  |0/52.2.k.k | 0/26.1.k  | 0/26.1.L  | 0/39.1.k  | 13/52.1.k | 0/26.1.k  | 21/26.0.k |     -
ED448 PRIVATE KEY              | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  |0/52.2.k.k | 0/26.1.k  | 0/26.1.L  | 0/39.1.k  | 13/52.1.k | 0/26.1.k  | 21/26.0.k |     -
X25519 PRIVATE KEY             | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  |0/52.2.k.k | 0/26.1.k  | 0/26.1.L  | 0/39.1.k  | 13/52.1.k | 0/26.1.k  | 21/26.0.k |     -
X448 PRIVATE KEY               | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  |0/52.2.k.k | 0/26.1.k  | 0/26.1.L  | 0/39.1.k  | 13/52.1.k | 0/26.1.k  | 21/26.0.k |     -
SM2 PRIVATE KEY                | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  | 0/26.1.k  |0/52.2.k.k | 0/26.1.k  | 0/26.1.L  | 0/39.1.k  | 13/52.1.k | 0/26.1.k  | 21/26.0.k |     -
X9.42 DH PRIVATE KEY           | 21/26.0.k | 21/26.0.k | 21/26.0.k | 21/26.0.k | 21/26.0.k | 21/26.0.k | 21/26.0.k |40/52.0.k.k| 21/26.0.k | 21/26.0.k | 31/39.0.k | 42/52.0.k | 21/26.0.k | 21/26.0.k |     -
OPENSSH PRIVATE KEY ed25519    |  0/5.1.k  |  0/5.1.k  |  0/5.1.k  |  0/5.1.k  |  0/5.1.k  |  0/5.1.k  |  0/5.1.k  |0/10.2.k.k |  0/5.1.k  |  0/5.1.L  |  0/7.1.k  | 2/10.1.k  |  0/5.1.k  |  3/5.0.k  |     -
OPENSSH PRIVATE KEY rsa3072    | 0/39.1.k  | 0/39.1.k  | 0/39.1.k  | 0/39.1.k  | 0/39.1.k  | 0/39.1.k  | 0/39.1.k  |0/78.2.k.k | 0/39.1.k  | 0/39.1.L  | 0/58.1.k  | 16/78.1.k | 0/39.1.k  | 32/39.0.k |     -
OPENSSH PRIVATE KEY 70col      | 0/38.1.k  | 0/38.1.k  | 0/38.1.k  | 0/38.1.k  | 0/38.1.k  | 0/38.1.k  | 0/38.1.k  |0/76.2.k.k | 0/38.1.k  | 0/38.1.L  | 0/57.1.k  | 14/76.1.k | 0/38.1.k  | 30/38.0.k |     -
PGP PRIVATE KEY BLOCK ed25519  | 0/11.1.k  | 0/11.1.k  | 0/11.1.k  | 0/11.1.k  | 0/11.1.k  | 0/11.1.k  | 0/11.1.k  |0/22.2.k.k | 0/11.1.k  | 0/11.1.L  | 0/16.1.k  | 5/22.1.k  | 0/11.1.k  | 8/11.0.k  | 8/11.0.k
PGP PRIVATE KEY BLOCK rsa+hdrs | 0/40.1.k  | 0/40.1.k  | 0/40.1.k  | 0/40.1.k  | 0/40.1.k  | 0/40.1.k  | 0/40.1.k  |0/80.2.k.k | 0/40.1.k  | 0/40.1.L  | 0/60.1.k  | 16/80.1.k | 0/40.1.k  | 32/40.0.k | 32/40.0.k
PGP SECRET KEY BLOCK           | 0/11.1.k  | 0/11.1.k  | 0/11.1.k  | 0/11.1.k  | 0/11.1.k  | 0/11.1.k  | 0/11.1.k  |0/22.2.k.k | 0/11.1.k  | 0/11.1.L  | 0/16.1.k  | 5/22.1.k  | 0/11.1.k  | 8/11.0.k  | 8/11.0.k
SSL SESSION PARAMETERS         |  2/3.0.k  |  2/3.0.k  |  2/3.0.k  |  2/3.0.k  |  2/3.0.k  |  2/3.0.k  |  2/3.0.k  | 4/6.0.k.k |  2/3.0.k  |  2/3.0.k  |  3/4.0.k  |  5/6.0.k  |     -     |     -     |     -
SSH2 ENCRYPTED PRIVATE KEY     | 17/20.0.k | 17/20.0.k | 17/20.0.k | 17/20.0.k | 17/20.0.k | 17/20.0.k | 17/20.0.k |33/40.0.k.k| 17/20.0.k | 17/20.0.k | 23/30.0.k | 35/40.0.k | 17/20.0.k | 17/20.0.k |     -
```
Adjacent shapes, the real sandbox CLI (`/tmp/vr182/adj2.py`; the RSA PKCS#1 throwaway, FAKE ppk body):
```
lowercase label                               body lines left 20/25  placeholders 0  after kept
trailing spaces after dashes                  body lines left 0/25  placeholders 1  after kept
URL-encoded block (curl --data-urlencode)     body lines left 19/25  placeholders 0  after kept
HTML-escaped newlines (<br>)                  body lines left 0/25  placeholders 1  after kept
PuTTY .ppk v3 (FAKE, not armored)             body lines left 1/2  placeholders 0  after kept
```
Reading, per question of item 2:
- **Every frozen family, both exporters, message AND tool bodies:** redacted whole in plain, CRLF, indented (YAML, `> `), JSON `\n`,
  Python repr `\\n`, armor headers, two blocks (the prose between them survives: `k.k`), END with another private label, and a first
  block cut before a second one. **Closes F1 (GnuPG, both labels) on the real path.** The code also redacts plain PKCS#8 and every
  digit label. F8d's test gap is closed by the PKCS#8 test row (item 6, L2 killed); the digit labels stay untested (A-6).
- **END with a PUBLIC label** (`END=pub`): no leak; the rule runs to `\Z`, so the text after the block is lost (the F13 class, KNOWN).
- **Nested block** (`2B nest`): the outer block's tail after the inner END leaks (2-16 lines). That tail has no BEGIN: it is the KNOWN
  F2 class (a BEGIN-less fragment), not a new failure of the key rule.
- **A doubled inner space** before PRIVATE is absorbed (`[A-Z0-9 ]*`); inside `PRIVATE  KEY` or `KEY  BLOCK` it defeats the rule
  (1-32 lines leak). OpenSSL and GnuPG reject such a label, so no parser-valid block carries it. -> FOLLOW-UP A-2.
- **`X9.42 DH PRIVATE KEY`** (a period in the label) is never matched: 21 of 26 lines leak in every shape. It is a libcrypto label that
  OpenSSL 3.0.13 cannot write here. -> FOLLOW-UP A-1.
- **Adjacent formats** whose armor names no PEM private key: `SSL SESSION PARAMETERS` (2/3 lines), the SSH.com `---- BEGIN SSH2
  ENCRYPTED PRIVATE KEY ----` (17/20), a lowercase label (20/25), a URL-encoded block (19/25), PuTTY `.ppk` (1/2, not armored: the F3
  class). -> FOLLOW-UP A-3.

## 3. A — non-secret armor and the committed corpus

**Verdict: the widened rule touches NO non-secret label (0 of 33), and the current scrub changes 0 of the 120 committed transcripts.
No exposure, no F13 loss and no stale export in the corpus at the PIN (SOLID, two instruments).**

(a) Every public or non-secret label from item 2's enumeration, through the REAL `scrub` (`/tmp/vr182/h3.py`; `r0` = the key rule,
and `r8` = the 40-character opaque rule at `scripts/transcript_export.py:43`, which writes `opaque-redacted`). Real throwaway artifacts where this sandbox writes them
(`openssl req/pkey/rsa/ecparam/genpkey`, `gpg --export/--detach-sign/--clearsign/-e`), FAKE bodies otherwise:
```
label                      source               key-rule  scrub==text  rules fired (r0 = the key rule)
X509 CERTIFICATE           FAKE body            no        False        r8x5
CERTIFICATE                real (cert.pem)      no        False        r8x7
TRUSTED CERTIFICATE        FAKE body            no        False        r8x4
NEW CERTIFICATE REQUEST    FAKE body            no        False        r8x2
CERTIFICATE REQUEST        real (csr.pem)       no        False        r8x7
X509 CRL                   FAKE body            no        False        r8x1
PUBLIC KEY                 real (pub.pem)       no        False        r8x2
RSA PUBLIC KEY             real (rsapub.pem)    no        False        r8x2
DSA PUBLIC KEY             FAKE body            no        False        r8x2
PKCS7                      FAKE body            no        False        r8x5
PKCS #7 SIGNED DATA        FAKE body            no        False        r8x3
DH PARAMETERS              FAKE body            no        False        r8x3
X9.42 DH PARAMETERS        real (dhx.par)       no        False        r8x5
DSA PARAMETERS             real (dsaparam.pem)  no        False        r8x2
ECDSA PUBLIC KEY           FAKE body            no        False        r8x2
EC PARAMETERS              real (ecparam.pem)   no        True         -
PARAMETERS                 FAKE body            no        False        r8x1
CMS                        FAKE body            no        False        r8x1
EC PUBLIC KEY              FAKE body            no        False        r8x3
ED25519 PUBLIC KEY         FAKE body            no        False        r8x2
ED448 PUBLIC KEY           FAKE body            no        False        r8x3
X25519 PUBLIC KEY          FAKE body            no        False        r8x2
X448 PUBLIC KEY            FAKE body            no        False        r8x1
SM2 PUBLIC KEY             FAKE body            no        False        r8x4
SM2 PARAMETERS             FAKE body            no        False        r8x3
X9.42 DH PUBLIC KEY        FAKE body            no        False        r8x6
PGP PUBLIC KEY BLOCK       real (pgp_pub.asc)   no        False        r8x6
PGP SIGNATURE              real (m.sig)         no        True         -
PGP MESSAGE                real (m.enc)         no        True         -
PGP SIGNED MESSAGE         real (m.clear)       no        False        r8x1
PGP ARMORED FILE           FAKE body            no        False        r8x3
SSH2 PUBLIC KEY (RFC 4716) FAKE body            no        False        r8x4
OpenSSH one-line public key FAKE body            no        False        r8x1
```
The key rule hits none of them: the widening adds no over-redaction of public material. The changes shown are the pre-existing opaque
rule cutting 40+ runs out of public base64 (INFO I-3: `coarse, deliberately`, `scripts/transcript_export.py:42`, not this repair). The
only NEW redaction the widening can cause outside a real key is prose that writes a whole `-----BEGIN PGP PRIVATE KEY BLOCK-----` or a
`… SECRET KEY …-----` line with no END: the rest of that turn is lost (the F13 class, KNOWN).

(b) The corpus at the PIN:
```
$ python3 /tmp/vr182/h3.py c84f161        (the CURRENT scrub, `git show c84f161:<file>` for each `git ls-tree … transcripts` path)
files: 120
files where scrub(text) != text: 0
$ (independent scan, no scrub involved: armor lines of 4-5 dashes and any label; label words; PEM-body-shaped whole lines)
files: 120
armor lines (4-5 dashes, any label) in the committed corpus: 0
label mentions (any form): {'PGP PRIVATE KEY BLOCK': 0, 'PGP SECRET KEY BLOCK': 0, 'OPENSSH PRIVATE KEY': 0, 'RSA PRIVATE KEY': 0, '<private-key-redacted>': 0}
PEM-body-shaped lines (60-76 base64 chars, whole line): 0
```
Classification of the differences: there are none, so each class counts 0: committed unredacted keys 0; F13-class prose losses 0
(characters lost: 0); files that need a re-export for this rule 0. Every committed file was exported BEFORE 9932f34 (no commit after
it touches `transcripts/`, item 1), under the old rule, and none carries anything the new rule would change.

**Added at 12:06Z: the first committed export UNDER the new rule.** Origin moved during the lane (c84f161 -> 11195d9). 11195d9
(`transcripts: scrubbed sandbox chat digests (2026-09-23)`, 11:40Z, +424 lines in `transcripts/sandbox/chat-2026-09-23.md`) is
push_clean's push-time export, and 9932f34 is its ancestor (`git merge-base --is-ancestor`), so it ran under the widened rule
(from the tree or from the detached push worktree; both carry the rule). The same two instruments at 11195d9:
```
files: 120
files where scrub(text) != text: 0
files: 120 | armor lines: 0 | PEM-body-shaped lines: 0 | <private-key-redacted>: 0
```
No key reached it, and the widened rule redacted nothing in it. So no F13 prose loss occurred either: an F13 loss leaves a
placeholder, and there is none.

**Deployment (by code, SOLID):** the harvest runs `python3 "$AF_REPO/harness-ports/bin/hermes-session-export.py"`
(`harness-ports/bin/pc-lane.sh:514`, `AF_REPO` defaults to `$HOME/agent-factory` at `harness-ports/bin/pc-lane.sh:68`), and
`SCRUB_SRC` resolves next to THAT file (`harness-ports/bin/hermes-session-export.py:23`). Only `pc-lane.sh` itself runs from a private
copy (`harness-ports/bin/pc-lane.sh:58-61`, `PC_LANE_SELF_COPY`). So the clone's HEAD at HARVEST time sets the rule. Every harvest before the 11:2xZ
fast-forward used the old rule, and every harvest after it uses the new rule, including harvests of lanes launched before it. PC
transcripts harvested under the old rule and not yet committed (they travel home in lane trees) are NOT visible here (no bridge):
UNVERIFIED. The scrub is idempotent (0 of 120 files change on a re-scrub), so re-scrubbing an incoming transcript before the commit
would close that window. -> FOLLOW-UP A-4.

## 4. A — first position (F8a)

**Verdict: HOLDS. 13 new prefixes × 3 families (RSA PKCS#1, OpenSSH, GnuPG) = 39 cases: 0 body lines on disk through both real
exporters, and the text after the block is kept in all 39 (SOLID).** `/tmp/vr182/h4.py`: the real CLIs, the sandbox exporter at its
production cap, and the PC exporter on an assistant message AND a tool body (`--tool-body-cap 4000`). FAKE `sk-`/`ghp_`/opaque values.
```
prefix                                 family       sandbox(left/tot, shape on disk)      PC msg+tool(left/tot)  other planted value on disk
password=                              RSA PKCS#1    0/25  'password=<redacted>'                 0/25                  -  after=k
password=                              OPENSSH       0/5   'password=<redacted>'                 0/5                   -  after=k
password=                              PGP PRIVATE   0/12  'password=<redacted>'                 0/12                  -  after=k
token: "                               RSA PKCS#1    0/25  'token: "<redacted>"'                 0/25                  -  after=k
token: "                               OPENSSH       0/5   'token: "<redacted>"'                 0/5                   -  after=k
token: "                               PGP PRIVATE   0/12  'token: "<redacted>"'                 0/12                  -  after=k
Authorization:                         RSA PKCS#1    0/25  'Authorization: <redacted>'           0/25                  -  after=k
Authorization:                         OPENSSH       0/5   'Authorization: <redacted>'           0/5                   -  after=k
Authorization:                         PGP PRIVATE   0/12  'Authorization: <redacted>'           0/12                  -  after=k
Authorization: Bearer                  RSA PKCS#1    0/25  'Authorization: Bearer <private-key'  0/25                  -  after=k
Authorization: Bearer                  OPENSSH       0/5   'Authorization: Bearer <private-key'  0/5                   -  after=k
Authorization: Bearer                  PGP PRIVATE   0/12  'Authorization: Bearer <private-key'  0/12                  -  after=k
api_key:                               RSA PKCS#1    0/25  'api_key: <redacted>'                 0/25                  -  after=k
api_key:                               OPENSSH       0/5   'api_key: <redacted>'                 0/5                   -  after=k
api_key:                               PGP PRIVATE   0/12  'api_key: <redacted>'                 0/12                  -  after=k
"private_key": "  (real newlines)      RSA PKCS#1    0/25  '{"private_key": "<private-key-reda'  0/25                  -  after=k
"private_key": "  (real newlines)      OPENSSH       0/5   '{"private_key": "<private-key-reda'  0/5                   -  after=k
"private_key": "  (real newlines)      PGP PRIVATE   0/12  '{"private_key": "<private-key-reda'  0/12                  -  after=k
"private_key": "  (\n escapes)         RSA PKCS#1    0/25  '{"private_key": "<private-key-reda'  0/25                  -  after=k
"private_key": "  (\n escapes)         OPENSSH       0/5   '{"private_key": "<private-key-reda'  0/5                   -  after=k
"private_key": "  (\n escapes)         PGP PRIVATE   0/12  '{"private_key": "<private-key-reda'  0/12                  -  after=k
sk- string, same line, no space        RSA PKCS#1    0/25  'sk-<redacted><private-key-redacted'  0/25                  -  after=k
sk- string, same line, no space        OPENSSH       0/5   'sk-<redacted><private-key-redacted'  0/5                   -  after=k
sk- string, same line, no space        PGP PRIVATE   0/12  'sk-<redacted><private-key-redacted'  0/12                  -  after=k
sk- string, same line, a space         RSA PKCS#1    0/25  'sk-<redacted> <private-key-redacte'  0/25                  -  after=k
sk- string, same line, a space         OPENSSH       0/5   'sk-<redacted> <private-key-redacte'  0/5                   -  after=k
sk- string, same line, a space         PGP PRIVATE   0/12  'sk-<redacted> <private-key-redacte'  0/12                  -  after=k
ghp_ string, same line, no space       RSA PKCS#1    0/25  'gh<redacted><private-key-redacted>'  0/25                  -  after=k
ghp_ string, same line, no space       OPENSSH       0/5   'gh<redacted><private-key-redacted>'  0/5                   -  after=k
ghp_ string, same line, no space       PGP PRIVATE   0/12  'gh<redacted><private-key-redacted>'  0/12                  -  after=k
40+ opaque run, line before            RSA PKCS#1    0/25  '<opaque-redacted>'                   0/25                  -  after=k
40+ opaque run, line before            OPENSSH       0/5   '<opaque-redacted>'                   0/5                   -  after=k
40+ opaque run, line before            PGP PRIVATE   0/12  '<opaque-redacted>'                   0/12                  -  after=k
40+ opaque run, same line, no space    RSA PKCS#1    0/25  '<opaque-redacted><private-key-reda'  0/25                  -  after=k
40+ opaque run, same line, no space    OPENSSH       0/5   '<opaque-redacted><private-key-reda'  0/5                   -  after=k
40+ opaque run, same line, no space    PGP PRIVATE   0/12  '<opaque-redacted><private-key-reda'  0/12                  -  after=k
X-Agent-Token: (no space)              RSA PKCS#1    0/25  'X-Agent-Token:<redacted>'            0/25                  -  after=k
X-Agent-Token: (no space)              OPENSSH       0/5   'X-Agent-Token:<redacted>'            0/5                   -  after=k
X-Agent-Token: (no space)              PGP PRIVATE   0/12  'X-Agent-Token:<redacted>'            0/12                  -  after=k
```
**Can a later rule split a block the key rule already replaced?** No. `SECRET_PATTERNS` in order (`scripts/transcript_export.py:24-44`):
r0 key (:29-31) replaces the whole span with `<private-key-redacted>` before any other rule runs, so no body byte is left for a later
rule. The later rules can only touch the 22-character placeholder: r1, the credential rule (:33), takes it as an assigned VALUE and
renames it `<redacted>` (visible above after `password=`, `token: "`, `Authorization: `, `api_key: `, `X-Agent-Token:`); r2 Bearer
(:34), r3-r6 provider keys (:36-39), r7 bridge links (:41) and r8 opaque (:43) cannot match it (`<` and `>` bound its inner run of 20
word characters, under r8's 40). So the rename is the only interaction, and it moves no key byte. Rules run before r0 would split a
block: the `sk-` rule's class includes `-` and would eat `-----BEGIN` from `sk-…-----BEGIN` (the no-space rows). Those rows are safe
only because r0 is first. That order is what the landing's `tests/test_transcript_export.py:139` (`test_key_block_after_a_credential_keyword_is_scrubbed_whole`) pins with a `secret: ` prefix
(item 6 shows which mutants it kills). INFO I-4: after a keyword, the placeholder on disk reads `<redacted>`, so a reader cannot see
that a key was there. Harmless.

## 5. A — the PC exporter's binding to the rule

**Verdict: every broken scrubber FAILS CLOSED: rc 1, no output file, and the harvest prints its FAILED line and writes no transcript
(SOLID).** But the binding is by PATH, not by version: a stale or weakened `scrub` at that path exports with rc 0, silently. The 012d455b
window worked this way (FOLLOW-UP A-5).

`/tmp/vr182/h5.sh`: each case is a SCRATCH repo shape `/tmp/vr182/i5/<case>/` with the REAL `harness-ports/bin/hermes-session-export.py`
copied in and a scrubber variant at `scripts/transcript_export.py` (so `SCRUB_SRC`, `harness-ports/bin/hermes-session-export.py:23`,
resolves to the variant). A synthetic `state.db` holds one assistant message: a FAKE `AGENT_TOKEN=…` plus a throwaway GnuPG secret key.
Each case runs (1) the CLI directly and (2) the VERBATIM harvest block `harness-ports/bin/pc-lane.sh:509-519` (from `if [ "$HARNESS" = "hermes" ]`), `sed`-extracted, with
the lane's variables pointed at the scratch case. Metric: `leakcount.py`, i.e. body lines with any 8-character window on disk.
```
control                    rc=0   out-written=yes secret-lines(token:0 keylines:0/11 ph:1)  | harvest: pc-lane: transcript -> transcripts/pc/lane-x.md (in the lane transcript=yes (token:0 keylines:0/11 ph:1)
missing                    rc=1   out-written=no  secret-lines(-)  | harvest: pc-lane: session export FAILED (see lane.log) — report sti transcript=no (-)
      stderr: FileNotFoundError: [Errno 2] No such file or directory: '/tmp/vr182/i5/missing/scripts/transcript_export.py'
unreadable                 rc=0   out-written=yes secret-lines(token:0 keylines:0/11 ph:1)  | harvest: pc-lane: transcript -> transcripts/pc/lane-x.md (in the lane transcript=yes (token:0 keylines:0/11 ph:1)
unreadable2 (as nobody)    rc=1   out-written=no  secret-lines(-)  | harvest: pc-lane: session export FAILED (see lane.log) — report sti transcript=no (-)
      stderr: PermissionError: [Errno 13] Permission denied: '/tmp/vr182/i5/unreadable2/scripts/transcript_export.py'
raises                     rc=1   out-written=no  secret-lines(-)  | harvest: pc-lane: session export FAILED (see lane.log) — report sti transcript=no (-)
      stderr: RuntimeError: vr182 import-time failure
syntaxerr                  rc=1   out-written=no  secret-lines(-)  | harvest: pc-lane: session export FAILED (see lane.log) — report sti transcript=no (-)
      stderr: SyntaxError: '(' was never closed
empty                      rc=1   out-written=no  secret-lines(-)  | harvest: pc-lane: session export FAILED (see lane.log) — report sti transcript=no (-)
      stderr: AttributeError: module 'transcript_export' has no attribute 'scrub'
isdir                      rc=1   out-written=no  secret-lines(-)  | harvest: pc-lane: session export FAILED (see lane.log) — report sti transcript=no (-)
      stderr: IsADirectoryError: [Errno 21] Is a directory: '/tmp/vr182/i5/isdir/scripts/transcript_export.py'
scrub-raises               rc=1   out-written=no  secret-lines(-)  | harvest: pc-lane: session export FAILED (see lane.log) — report sti transcript=no (-)
      stderr: ValueError: vr182 scrub-time failure
scrub-none                 rc=1   out-written=no  secret-lines(-)  | harvest: pc-lane: session export FAILED (see lane.log) — report sti transcript=no (-)
      stderr: TypeError: 'NoneType' object is not callable
stale-rule                 rc=0   out-written=yes secret-lines(token:0 keylines:8/11 ph:0)  | harvest: pc-lane: transcript -> transcripts/pc/lane-x.md (in the lane transcript=yes (token:0 keylines:8/11 ph:0)
identity                   rc=0   out-written=yes secret-lines(token:3 keylines:11/11 ph:0)  | harvest: pc-lane: transcript -> transcripts/pc/lane-x.md (in the lane transcript=yes (token:3 keylines:11/11 ph:0)
```
- **Missing, unreadable (as `nobody`), raising on import, a syntax error, an empty file, a directory, `scrub` raising, `scrub` not
  callable:** all fail closed. `_scrub()` (`harness-ports/bin/hermes-session-export.py:26-30`) runs FIRST in `export()` (:47), before
  the DB is opened and before the one `write_text` (:83). So an exception writes nothing, the process exits 1, and the harvest's
  `|| echo "pc-lane: session export FAILED …"` branch (`harness-ports/bin/pc-lane.sh:517`) fires. The sandbox side fails closed too:
  `scripts/push_clean.sh:117-118` (`TRANSCRIPT_SYNC`) skips the commit when the export fails.
- **"unreadable" as root is not unreadable.** The sandbox runs as uid 0, which reads a mode-000 file, so that row behaves like the
  control. The real unreadable case is the `nobody` row (`setpriv --reuid=65534`).
- **`stale-rule`** (the rule at 9932f34^ at that path) exports GnuPG armor with 8 of 11 body lines and 0 placeholders, rc 0, through the
  verbatim harvest block: F1's leak, reproduced on the deployment path. **`identity`** (a `scrub` that returns its input) exports
  everything, rc 0. Nothing checks WHICH rule was loaded. The 9932f34 message's "so the PC exporter gets the same rule" is true only
  while the clone is current. Measured at authoring: the clone sat at 012d455b until 11:2xZ. -> FOLLOW-UP A-5: a load-time self-test in
  `_scrub()`, where the loaded `scrub` must redact a canary GnuPG block and a canary token, else exit non-zero. The same test belongs in
  `harness-ports/bin/qwen_matrix.py:126` `_scrub_messages`, the third consumer.

## 6. A — test strength (mutants)

**Verdict: the landing's five mutants reproduce EXACTLY as its message states. 7 of the 10 new mutants are killed. Three survive:
N2 (a security gap, but only on digit labels no tool here writes), N4 (EQUIVALENT: one trailing newline) and N7 (an over-redaction
gap). SOLID.** `/tmp/vr182/h6.py`: each mutant lives in its OWN scratch tree `/tmp/vr182/mut/<id>/` holding copies of
`scripts/transcript_export.py` (mutated), `tests/test_transcript_export.py`, `tests/conftest.py`, `pyproject.toml`,
`harness-ports/bin/hermes-session-export.py` and `harness-ports/tests/test_hermes_session_export.py`. The tests resolve `TOOL` and
`SCRUB_SRC` inside that tree. The harness asserts that the committed rule text appears exactly once and that its rebuilder reproduces
it byte for byte, so each mutant differs from the PIN only by its named change. Per mutant: `py_compile` rc; `pytest --co` count
(AF-AP-78); the pytest suite with `-rA`; `python3 harness-ports/tests/test_hermes_session_export.py`. The killer list comes from the
FAILED ids, and each killer is checked against the UNMUTATED run's PASSED ids (AF-AP-138).
```
U0 unmutated                                 py_compile rc=0 collected=13 | 13 passed in 0.58s | PC: test_hermes_session_export: 15 checks passed
  unmutated PASSED ids: 13
    test_every_key_family_is_scrubbed_whole[EC PRIVATE KEY] … [ENCRYPTED PRIVATE KEY] … [OPENSSH PRIVATE KEY] … [PGP PRIVATE KEY BLOCK]
    … [PGP SECRET KEY BLOCK] … [PRIVATE KEY] … [RSA PRIVATE KEY]; test_idempotent_and_deterministic;
    test_key_block_after_a_credential_keyword_is_scrubbed_whole; test_missing_transcript_exits_3;
    test_private_key_block_is_scrubbed_whole_or_to_the_end; test_secret_straddling_the_cap_never_reaches_disk;
    test_secrets_never_reach_disk_and_text_survives
L1 old rule                                  py_compile rc=0 collected=13 | 2 failed, 11 passed in 0.60s | PC: RED rc=1 at 91
    killed by: test_every_key_family_is_scrubbed_whole[PGP PRIVATE KEY BLOCK] (PASSED on U0)
    killed by: test_every_key_family_is_scrubbed_whole[PGP SECRET KEY BLOCK] (PASSED on U0)
L2 [A-Z0-9 ]+ (type word required)           py_compile rc=0 collected=13 | 1 failed, 12 passed in 0.58s | PC: test_hermes_session_export: 15 checks passed
    killed by: test_every_key_family_is_scrubbed_whole[PRIVATE KEY] (PASSED on U0)
L3 no SECRET                                 py_compile rc=0 collected=13 | 1 failed, 12 passed in 0.59s | PC: test_hermes_session_export: 15 checks passed
    killed by: test_every_key_family_is_scrubbed_whole[PGP SECRET KEY BLOCK] (PASSED on U0)
L4 END without BLOCK                         py_compile rc=0 collected=13 | 2 failed, 11 passed in 0.60s | PC: RED rc=1 at 91
    killed by: test_every_key_family_is_scrubbed_whole[PGP PRIVATE KEY BLOCK] (PASSED on U0)
    killed by: test_every_key_family_is_scrubbed_whole[PGP SECRET KEY BLOCK] (PASSED on U0)
L5 key rule moved last                       py_compile rc=0 collected=13 | 1 failed, 12 passed in 0.61s | PC: test_hermes_session_export: 15 checks passed
    killed by: test_key_block_after_a_credential_keyword_is_scrubbed_whole (PASSED on U0)
N1 greedy .*                                 py_compile rc=0 collected=13 | 9 failed, 4 passed in 0.61s | PC: RED rc=1 at 91
    killed by: all seven test_every_key_family_is_scrubbed_whole rows, test_key_block_after_a_credential_keyword_is_scrubbed_whole,
               test_private_key_block_is_scrubbed_whole_or_to_the_end (each PASSED on U0)
N2 [A-Z ]* (no digits)                       py_compile rc=0 collected=13 | 13 passed in 0.58s | PC: test_hermes_session_export: 15 checks passed
N3 (?: BLOCK)? dropped from BEGIN only       py_compile rc=0 collected=13 | 2 failed, 11 passed in 0.61s | PC: RED rc=1 at 91
    killed by: test_every_key_family_is_scrubbed_whole[PGP PRIVATE KEY BLOCK] (PASSED on U0)
    killed by: test_every_key_family_is_scrubbed_whole[PGP SECRET KEY BLOCK] (PASSED on U0)
N4 \Z -> $                                   py_compile rc=0 collected=13 | 13 passed in 0.60s | PC: test_hermes_session_export: 15 checks passed
N5 re.S dropped                              py_compile rc=0 collected=13 | 9 failed, 4 passed in 0.60s | PC: RED rc=1 at 91
    killed by: the same nine as N1 (each PASSED on U0)
N6 key rule moved SECOND                     py_compile rc=0 collected=13 | 1 failed, 12 passed in 0.61s | PC: test_hermes_session_export: 15 checks passed
    killed by: test_key_block_after_a_credential_keyword_is_scrubbed_whole (PASSED on U0)
N7 (?:PRIVATE|SECRET|PUBLIC) over-redaction  py_compile rc=0 collected=13 | 13 passed in 0.62s | PC: test_hermes_session_export: 15 checks passed
N8 placeholder text changed                  py_compile rc=0 collected=13 | 8 failed, 5 passed in 0.59s | PC: RED rc=1 at 91
    killed by: all seven test_every_key_family_is_scrubbed_whole rows, test_private_key_block_is_scrubbed_whole_or_to_the_end (each PASSED on U0)
N9 END drops SECRET only                     py_compile rc=0 collected=13 | 1 failed, 12 passed in 0.66s | PC: test_hermes_session_export: 15 checks passed
    killed by: test_every_key_family_is_scrubbed_whole[PGP SECRET KEY BLOCK] (PASSED on U0)
N10 no \Z alternative                        py_compile rc=0 collected=13 | 1 failed, 12 passed in 0.63s | PC: test_hermes_session_export: 15 checks passed
    killed by: test_private_key_block_is_scrubbed_whole_or_to_the_end (PASSED on U0)
```
(`/tmp/vr182/h6.out` holds the unabridged run: the N1/N5/N8 killer lines are listed there one per line. The first run cut the
parametrized ids at their inner spaces and merged the two PGP rows; the id regex was fixed and the whole table rerun. That run is
the one above.)

The landing's claims, checked row by row against the 9932f34 message: "the old rule: 2 failed (both PGP rows); the PC exporter check
red" = L1 ✓; "[A-Z0-9 ]+: 1 failed (the PKCS#8 row)" = L2 ✓; "no SECRET alternative: 1 failed (the PGP SECRET row)" = L3 ✓; "END without
BLOCK: 2 failed (both PGP rows); the PC check red" = L4 ✓; "the key rule moved last: 1 failed (the keyword test)" = L5 ✓.

The three survivors, measured on their mutated scratch modules:
```
N2 (no digits):
  ED25519 PRIVATE KEY    unmutated left 0/26   N2 left 21/26
  X25519 PRIVATE KEY     unmutated left 0/26   N2 left 21/26
  ED448 PRIVATE KEY      unmutated left 0/26   N2 left 21/26
  X448 PRIVATE KEY       unmutated left 0/26   N2 left 21/26
  SM2 PRIVATE KEY        unmutated left 0/26   N2 left 21/26
  RSA PRIVATE KEY        unmutated left 0/26   N2 left 0/26
N4 (\Z -> $): every text shape where the two could differ (no END; trailing newline or not; CRLF)
  no END, no trailing newline    equal=True  left U/N4 = 0/0  diff = ''
  no END, trailing \n            equal=False  left U/N4 = 0/0  diff = '\n'
  no END, trailing \n\n          equal=False  left U/N4 = 0/0  diff = '\n'
  no END, CRLF, trailing \r\n    equal=False  left U/N4 = 0/0  diff = '\n'
  END present                    equal=True  left U/N4 = 0/0  diff = ''
N7 (PUBLIC added): public blocks the mutant would eat
  PUBLIC KEY             unmutated key-rule placeholder: 0   N7: 1
  RSA PUBLIC KEY         unmutated key-rule placeholder: 0   N7: 1
  PGP PUBLIC KEY BLOCK   unmutated key-rule placeholder: 0   N7: 1
  CERTIFICATE            unmutated key-rule placeholder: 0   N7: 0
```
- **N2 — a SECURITY gap, on labels no tool here writes.** `KEY_FAMILIES` (`tests/test_transcript_export.py:122-123`) has no label with a
  digit, so dropping `0-9` from the class goes unnoticed, and 21 of 26 lines would leak for the five digit labels. OpenSSL 3.0.13
  writes none of those labels (item 2), so the gap is latent. -> FOLLOW-UP A-6: add one digit label (`ED25519 PRIVATE KEY`) to
  `KEY_FAMILIES`.
- **N4 — EQUIVALENT.** Without `re.M`, `$` differs from `\Z` only by one final newline. No key byte differs in any shape.
- **N7 — an OVER-REDACTION gap.** No test holds a public block, so a rule that also ate `PUBLIC KEY`, `RSA PUBLIC KEY` and `PGP PUBLIC
  KEY BLOCK` passes both suites. Not a security gap. -> FOLLOW-UP A-7: one negative control, a public block through the real CLI that
  must NOT get the key placeholder.

## 7. A — cost of the widened rule

**Verdict: LINEAR in every adversarial shape, for both rules. No finding (SOLID on the ratios; absolute times are indicative, since the
box was contended at load 1.9-3.5 on 4 CPUs).** `/tmp/vr182/h7.py`: the REAL `scrub` (current rule) against the same file at 9932f34^
(`git show 9932f34^:scripts/transcript_export.py`, loaded from `/tmp/vr182/te_old.py`). Each cell is the min of 3 runs. Linear scaling
means the 8 MB/1 MB ratio is about 8.
```
load: ['1.93', '3.51', '3.38'] cpus: 4
case                                                           rule  1MB(s)  2MB(s)  4MB(s)  8MB(s)   8MB/1MB
A mixed text (prose, code, base64, tokens, key blocks)         new    0.136   0.272   0.556   1.154     8.5x
A mixed text (prose, code, base64, tokens, key blocks)         old    0.153   0.288   0.600   1.213     7.9x
B1 BEGIN + 1000-char [A-Z0-9 ] run, no key label               new    0.164   0.327   0.690   1.318     8.1x
B1 BEGIN + 1000-char [A-Z0-9 ] run, no key label               old    0.154   0.306   0.606   1.263     8.2x
B2 BEGIN + run of 'PRIVATE KEX ' (a near miss at every word)   new    0.164   0.330   0.654   1.350     8.2x
B2 BEGIN + run of 'PRIVATE KEX ' (a near miss at every word)   old    0.157   0.312   0.633   1.244     7.9x
B3 ONE BEGIN line + one uppercase run to the end, no newline   new    0.157   0.314   0.633   1.294     8.2x
B3 ONE BEGIN line + one uppercase run to the end, no newline   old    0.153   0.304   0.629   1.235     8.1x
C1 one open block + many END lines with 1000-char runs         new    0.025   0.056   0.098   0.197     7.8x
C1 one open block + many END lines with 1000-char runs         old    0.019   0.039   0.080   0.158     8.2x
C2 one open block + END lines with 'PRIVATE KEX' runs          new    0.027   0.054   0.109   0.217     8.0x
C2 one open block + END lines with 'PRIVATE KEX' runs          old    0.150   0.303   0.596   1.272     8.5x
D1 100,000-scale valid BEGIN lines, no END (262,144 lines at 8 new    0.022   0.045   0.091   0.193     8.6x
D1 100,000-scale valid BEGIN lines, no END (262,144 lines at 8 old    0.023   0.044   0.093   0.193     8.6x
D2 non-key BEGIN lines, no END                                 new    0.154   0.302   0.604   1.243     8.1x
D2 non-key BEGIN lines, no END                                 old    0.152   0.290   0.576   1.178     7.7x
D3 GnuPG BEGIN lines, no END (new-rule only match)             new    0.022   0.044   0.090   0.174     8.0x
D3 GnuPG BEGIN lines, no END (new-rule only match)             old    0.147   0.298   0.595   1.169     7.9x

key rule alone (SECRET_PATTERNS[0].sub), 8 MB:
  A mixed text (prose, code, base64, tokens, key blocks)         new   0.027s  old   0.021s
  B1 BEGIN + 1000-char [A-Z0-9 ] run, no key label               new   0.075s  old   0.028s
  B2 BEGIN + run of 'PRIVATE KEX ' (a near miss at every word)   new   0.093s  old   0.036s
  B3 ONE BEGIN line + one uppercase run to the end, no newline   new   0.073s  old   0.028s
  C1 one open block + many END lines with 1000-char runs         new   0.204s  old   0.157s
  C2 one open block + END lines with 'PRIVATE KEX' runs          new   0.220s  old   0.004s
  D1 100,000-scale valid BEGIN lines, no END                     new   0.180s  old   0.186s
  D2 non-key BEGIN lines, no END                                 new   0.041s  old   0.025s
  D3 GnuPG BEGIN lines, no END (new-rule only match)             new   0.176s  old   0.031s

100,000 BEGIN lines exactly (D1/D3 shapes):
  RSA PRIVATE KEY          3,200,000 chars  new  0.070s  old  0.069s
  PGP PRIVATE KEY BLOCK    3,800,000 chars  new  0.077s  old  0.559s
  CERTIFICATE              2,800,000 chars  new  0.408s  old  0.398s
load: ['2.31', '3.18', '3.27']
```
Why it stays linear, from the pattern (`scripts/transcript_export.py:29-30`, `re.S`): a failing header costs one backtrack pass over its
`[A-Z0-9 ]*` run (B1-B3). Once a header matches, the `\Z` alternative always succeeds, so the engine never backtracks into the header.
`.*?` then pays O(1) per position, plus one pass over each `-----END ` run (C1, C2). Where the key rule alone costs up to 2.6x more
(B1-B3, 8 MB: 0.073-0.093 s against 0.028-0.036 s), the whole scrub does not notice. Where the new rule matches and the old one did not
(C2, D3), the whole scrub gets FASTER, because the later rules find nothing left. The worst whole-scrub cost was 1.35 s for 8 MB, and a
push-time export or a lane harvest scrubs one turn at a time. INFO I-5.

## 8. B — one string at three sites

**Verdict: HOLDS. Piece (c) of the parsed `verified:` value equals the test constant byte for byte, and the whole value equals the
constant. The Rule line says the same thing in its own words (latest launch, at or after, the same cutoff). The landing's negative
control reproduces exactly (`2 failed, 14 passed`), and every new mutant reds both value tests by name, at the first changed character
(SOLID).** `/tmp/vr182/h8.py`, with scratch trees `/tmp/vr182/b8/<case>/` (copies of the test, `upstream.lock.yaml`,
`docs/HARNESS-PORTS.md`, `tests/conftest.py`, `pyproject.toml`).
```
== the value, parsed (yaml.safe_load), split on '; ' at most twice ==
piece (c) of the lock        : '110 PC lane directories whose latest launch was at or after 2026-09-08 14:22:00Z (98 with a report; brief.md--0000000 never ran Hermes), tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md'
piece (c) of the test constant: '110 PC lane directories whose latest launch was at or after 2026-09-08 14:22:00Z (98 with a report; brief.md--0000000 never ran Hermes), tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md'
(c) lock == (c) constant, byte for byte: True | whole value == constant: True | (a) equal: True | (b) equal: True
naive split on '; ' gives 4 parts; the separator also occurs inside (c): True
line 173 carries (c) verbatim: True | line 173 starts with '    verified: "': True
the test constant's own source line (tests/test_upstream_lock_lane_runtime.py:58): '"110 PC lane directories whose latest launch was at or after'…

== the record's Rule line (record lines 8-10) vs piece (c) ==
  LATEST/latest launch     Rule line: True   piece (c): True
  at or after              Rule line: True   piece (c): True
  the cutoff               Rule line: True   piece (c): True
  brief.md--0000000 named  Rule line: False  piece (c): True
  110 / 98                 Rule line: False  piece (c): True

U0_unmutated: collected=16 | 16 passed in 0.21s
NC_old_lock_new_test: collected=16 | 2 failed, 14 passed in 0.17s
  red at T:170 — lane_runtime.hermes-agent-lane-runtime differs at verified: … [first difference at char 314: got …' 110 PC lanes first laun'… expected …' 110 PC lane directories'…]
  red at T:180 — verified mismatch: got "harness-ports/tests/run-all.sh on th… [first difference at char 314: got …' 110 PC lanes first laun'… expected …' 110 PC lane directories'…]
MB1_lock_c_one_char_case: collected=16 | 2 failed, 14 passed in 0.17s
  red at T:170 — lane_runtime.hermes-agent-lane-runtime differs at verified: … [first difference at char 340: got …'hose latest Launch was a'… expected …'hose latest launch was a'…]
  red at T:180 — verified mismatch: got "harness-ports/tests/run-all.sh on th… [first difference at char 340: got …'hose latest Launch was a'… expected …'hose latest launch was a'…]
MB1b_lock_c_one_char_digit: collected=16 | 2 failed, 14 passed in 0.17s
  red at T:170 — … [first difference at char 419: got …'f.md--0000001 never ran '… expected …'f.md--0000000 never ran '…]
  red at T:180 — … [first difference at char 419: got …'f.md--0000001 never ran '… expected …'f.md--0000000 never ran '…]
MB2_lock_pieces_b_c_reordered: collected=16 | 2 failed, 14 passed in 0.25s
  red at T:170 — … [first difference at char 181: got …'ts header); 110 PC lane '… expected …'ts header); identity pro'…]
  red at T:180 — … [first difference at char 181: got …'ts header); 110 PC lane '… expected …'ts header); identity pro'…]
MB3_constant_trailing_comma_space_dropped: collected=16 | 2 failed, 14 passed in 0.18s
  red at T:170 — … [first difference at char 438: got …' ran Hermes), tasks/brie'… expected …' ran Hermes)tasks/briefs'…]
  red at T:180 — … [first difference at char 438: got …' ran Hermes), tasks/brie'… expected …' ran Hermes)tasks/briefs'…]
MB4_constant_back_to_first_launched: collected=16 | 2 failed, 14 passed in 0.18s
  red at T:170 — … [first difference at char 314: got …' 110 PC lane directories'… expected …' 110 PC lanes first laun'…]
  red at T:180 — … [first difference at char 314: got …' 110 PC lane directories'… expected …' 110 PC lanes first laun'…]
```
(T = `tests/test_upstream_lock_lane_runtime.py`; T:170 is the assert of `test_lane_runtime_entry_values` (:166), T:180 that of
`test_lane_runtime_verified_value` (:177). NC = the lock at 9c991a2^ with the new test, the landing's control: "2 failed, 14 passed" ✓.)

Observations on the three sites:
- **The separator now occurs inside piece (c).** The constant joins three pieces with `"; "`
  (`tests/test_upstream_lock_lane_runtime.py:50`, `LANE_RUNTIME_VERIFIED`), and the amended (c) carries `"(98 with a report; brief.md--0000000 never ran
  Hermes)"`. A naive split therefore yields 4 parts, and the third would end inside an open parenthesis. No reader splits the value
  today (VERIFY-REPIN-a-R1 F8: nothing acts on `lane_runtime`), and the tests compare whole strings. INFO B-1: a `,` or `—` inside the
  parenthesis would keep the pieces recoverable.
- **The Rule line does not name 110/98 or the `0000000` directory**, but it states the counting rule, not the count. The count is on the
  record's **Result** line (record line 13 at the PIN): "110 lanes: 98 with a report, 4 with a FAILED marker, the rest live or stopped
  without a report". That line is NOT one of the three amended sites. It still counts `brief.md--0000000` among "110 lanes" and files it
  under "live or stopped", although that directory never started (F2's own point). -> FOLLOW-UP B-2 (outside 9c991a2's three strings).
- **The record's measuring script still names its variable `first`** (`first=$(stat -c %Y "$d/prompt.md" …)`, record lines 142-143), under a
  Rule line that now says LATEST. The script is the verbatim record of what ran on the PC, so renaming it would falsify the record. A
  one-line note beside it would stop a reader from re-deriving F1. INFO B-3.
- The amendment added one line to the record (148 -> 149 lines), so every table row moved down by one. VERIFY-REPIN-a-R1 and this
  brief cite pre-amendment numbers: the five relaunched lanes are record lines 22-26 at the PIN, not 21-25, and `brief.md--0000000` is
  line 64. INFO, see DISCREPANCIES.

## 9. B — are the words true for the method?

**Verdict: TRUE for the method, by the committed code (SOLID by code; the PC directories were not re-measured, per the brief).** The
`prompt.md` mtime is the time of the LATEST start of `harness-ports/bin/pc-lane.sh` that got past its pre-prompt guards. A refused
start does not move it, and a refused start launched nothing, so "latest launch" is the right name. One clause of the amended Rule
line overstates the mechanism ("truncates at every start"): FOLLOW-UP B-4, which does not change the count.

**Who writes `prompt.md`, and when** (P = `harness-ports/bin/pc-lane.sh`):
- The only code writer in the repo is P (`git grep -n 'prompt\.md' -- '*.sh' '*.py' '*.bash'`, vendored trees excluded: P:217, plus five
  read-only `grep -q` checks in `harness-ports/tests/test_pc_lane.sh`). Every use of `PROMPT_FILE` in P: `:218` truncates; `:222-245`
  append (the role file, the brief, five standing rules); `:319` and `:322` only READ it (`cat "$PROMPT_FILE"` into
  `> "$PROMPT_RUN"`, i.e. `prompt.attempt<N>.md`). No line of P removes or touches it (`rm -f` at `:111`, `:461`, `:497` hits
  `lane.pid`, the self-copy and `report.md` only).
- **So the mtime is the end of the prompt assembly in the latest start that reached :218.** Retries inside one start (the capacity
  loop, `:319-322`) write `prompt.attempt<N>.md` and leave the mtime alone. A retry is part of its start, not a new launch.

**Is a refused start a launch, and does it move the mtime?** It does not move it. These exits come BEFORE :218: no brief
(`:65`), no PIN (`:80-82`), a non-empty report (`:101-104`), a live pidfile (`:105-108`), `worktree add` failing or a tree at the
wrong commit (`:163-171`), a lane patch that does not apply (`:182-185`, FAILED + rc 70). None reaches Hermes (`:446`). So the record
cannot date a lane by a refused relaunch, which is correct for a "which lanes ran" count. The opposite edge: a start that passes :218
and then dies before `:446` DOES move the mtime with no Hermes run. The cases: a missing role file (`:221`), `cd "$TREE"` (`:251`), the
lane profile helper (`:438-440`). The record cannot tell these apart (no marker). They can only hide among the 12 no-report rows: a
report row's dated start is the one that wrote its report, because a non-empty report stops every later start at `:101`.
UNVERIFIED how many there are (no bridge).

**`brief.md`: its writer, and its mtime.** Only the dispatcher writes it: `scripts/pc_lane.sh:250-251` (`mkdir -p … && … base64 -d >
$REMOTE_BRIEF`), at every dispatch that passes the dispatcher's premise gate (`scripts/pc_lane.sh:211` `_premise_state`; the T90 gate runs before the
ship, AF-AP-79). It rewrites the file (`>`), so its mtime is the LATEST dispatch. The record reads it only when `prompt.md` is absent
(record lines 142-143, `stat … prompt.md || stat … brief.md`), that is, for a directory where no start reached :218. For such a
directory the latest dispatch IS its latest launch attempt. Consistent.

**`brief.md--0000000 never ran Hermes` — TRUE by code.** The name is the dispatcher's (`scripts/pc_lane.sh:150` `LANE_ID`: the basename's
trailing newline becomes the first `-` through `tr -c`, then `-<PIN>`). So a brief named `brief.md` pinned `0000000`. Hermes runs only
at P:446, after the prompt write at P:218. A row dated by `brief.md` has no `prompt.md`, so no start reached :218 and Hermes never ran.
With PIN `0000000`, P dies at `:163-171` unless some ref resolves from `0000000` (VERIFY-REPIN-a-R1's caveat, still standing).
**Origin (INFERRED, UNSURE):** `harness-ports/tests/test_pc_lane_dispatcher.sh` has used `$TMP/brief.md` with `PIN: 0000000` as its
dispatch fixture since 867e1f2 (09-14 17:11Z). That version exits on `LANE_PRINT_EFFORT=1` before any bridge call. 650b33b (09-15
18:03Z, lane QM0-b, a PC cloud lane dispatched about 15:2xZ and home by the ledger's "2026-09-15 17:5xZ landing sync",
`todo/BUILD-TASKLIST.md:658`, `landing sync`) added a bridge double "that keeps every command local". The row's time, 2026-09-15T17:09:44Z, falls inside
QM0-b's PC run. So an in-development version of that test, run on the PC, most likely shipped the fixture into the real lane root. No
committed record says so. The landed double answers `echo shipped` for the `mkdir` and executes nothing. Supporting fact, in this
sandbox today: 159 files `/tmp/pc-lane-provider-mix-brief.md--0000000-<pid>.sql`, left by that test's runs since 09-22 12:40Z
(`scripts/pc_lane.sh:538` `MIX_REMOTE` names them). They show that the fixture's lane id is exactly `brief.md--0000000`, the PC
directory's name, and that the double runs part of the dispatcher's PC-side work locally (INFO I-8).

**FOLLOW-UP B-4 (a Rule-line clause):** "the mtime of `prompt.md`, which `harness-ports/bin/pc-lane.sh:218` truncates at every start"
(record lines 8-9). Every start that is refused at `:65-185` does NOT truncate it. The true statement is "at every start that passes its
guards". The error runs toward understatement: a refused relaunch cannot add a lane to the count. So piece (c) and the count stand.

## 10. B — does piece (c) say what it proves?

**Grade: "latest launch" is ENOUGH for the claim the entry makes. Dropping the five-lane clause does not change what a reader concludes
about b3399c1, so it is NOT a hollow green (SOLID on the text; the reason follows).** A precision note in the RECORD is still worth
adding (FOLLOW-UP B-5).

What the entry claims (`upstream.lock.yaml:164-173`): the lane runtime is b3399c1 (0.21.1, Python 3.11.15, SQLite 3.53.1); its `role` is
the lane runtime and "NOT the S0-01 proof runtime"; its `reason` is "SQLite >= 3.51.3 for WAL on the shared profile state.db
(VERIFY-B5j); owner-run hermes update 2026-09-08". `verified:` then gives three pieces of evidence: (a) the adapters' suite, which by its
own header runs no Hermes binary; (b) the identity probe; (c) the usage count. So piece (c) is the ONLY evidence that lanes ran on the
pin, and it is a count of latest launches, not a claim about what produced each report.

The five (record lines 22-26 at the PIN: `pc-verify-b5j`, `pc-verify-n5i`, `pc-b2`, `pc-verify-m2`, `pc-verify-g2`, 14:25:47Z-14:31:16Z).
The incident log (`docs/INCIDENT-LOG.md:286`, the 2026-09-08 14:2xZ entry) records them "started 11:40Z-14:12Z on the 3.49.1 runtime",
stopped at 14:27Z, and "relaunched … on the repaired runtime (each resumes from its draft and tree under the RESUME note)":
- **Their latest launch DID run the repaired runtime**, so counting them under "latest launch at or after 14:22:00Z" is true. It is
  also evidence FOR the entry's `reason`: they are the lanes the 3.49.1 runtime put at risk, and they finished on the new one. The
  identity of that runtime as b3399c1 stays INFERRED, as VERIFY-REPIN-a-R1 6b noted: no lane records its sha, and the record's
  "Limits, stated" says so (record lines 15-17).
- **What the omission hides:** 5 of the 98 reports are MIXED-runtime products. Their drafts and trees began under 3.49.1. A reader who
  takes "98 with a report" as "98 reports written wholly by b3399c1" over-reads by at most 5. The word "latest" tells the reader that
  earlier launches may exist, and nothing in the entry claims report provenance. So the omission neither inflates b3399c1's identity
  nor its use, and it hides no GAP of the pin. The pin's real gaps are stated where they belong: "nothing reads `lane_runtime`"
  (`docs/HARNESS-PORTS.md` §12, R5) and "no lane records its sha" (the record's Limits).
- **But the record never states the mixed-runtime fact.** Piece (c) links it, yet rows 22-26 carry only dates. The fact lives in the
  incident log and in VERIFY-REPIN-a-R1's report. -> FOLLOW-UP B-5: one line in the record's "Limits, stated", naming the five and
  pointing to `docs/INCIDENT-LOG.md` (a record edit, outside 9c991a2's three strings).
- **A related implicature:** "(98 with a report; brief.md--0000000 never ran Hermes)" names ONE directory that never ran Hermes. A reader
  may infer that the other 109 did. Item 9 shows that a start which dies after P:218 and before P:446 counts with no Hermes run, and
  such rows can only be among the 11 other no-report rows. The record does not print which file dated each row (`prompt.md` or
  `brief.md`). UNVERIFIED. -> FOLLOW-UP B-6: a column for the dating file in the measuring script, so the "never ran" set is complete
  rather than a single named case.

## 11. GATES

**All green, twice each, with identical counts; `validate-ledger` matches authoring; the gates wrote nothing to the tree (SOLID).**
Counts are from `scripts/test_summary.sh` (system `python3`, pytest 9.1.1, `-p no:cacheprovider`), each with `--basetemp=/tmp/vr182/bt11/<run>`,
removed after each run.
```
Wed Sep 23 11:58:28 UTC 2026
== set ids ==   (bash scripts/pc_suite.sh set-id -- <files>, paths exactly as the brief lists them)
1 files set=73755bb9fbbf        tests/test_transcript_export.py
1 files set=0be097535262        harness-ports/tests/test_hermes_session_export.py
2 files set=3d348d3f5f4d        tests/test_upstream_lock_lane_runtime.py tests/test_s0_12_license_sbom.py
== G1 run 1: tests/test_transcript_export.py ==
pytest-exit: 0
pytest-summary: 13 passed in 0.55s
== G1 run 2: tests/test_transcript_export.py ==
pytest-exit: 0
pytest-summary: 13 passed in 0.54s
== G2 run 1: python3 harness-ports/tests/test_hermes_session_export.py ==
test_hermes_session_export: 15 checks passed
rc=0
== G2 run 2: python3 harness-ports/tests/test_hermes_session_export.py ==
test_hermes_session_export: 15 checks passed
rc=0
== G3 run 1: tests/test_upstream_lock_lane_runtime.py tests/test_s0_12_license_sbom.py ==
pytest-exit: 0
pytest-summary: 21 passed in 0.42s
== G3 run 2: tests/test_upstream_lock_lane_runtime.py tests/test_s0_12_license_sbom.py ==
pytest-exit: 0
pytest-summary: 21 passed in 0.41s
== G4: python3 scripts/validate-ledger integrity --root . ==
S0-01 PRESENT
S0-02 ABSENT
S0-03 PRESENT
S0-04 PRESENT
S0-05 ABSENT
S0-06 PRESENT
S0-07 PRESENT
S0-08 PRESENT
S0-09 PRESENT
S0-10 PRESENT
S0-11 PRESENT
S0-12 PRESENT
blocked_credential numerator=0 denominator=1
blocked_host numerator=0 denominator=1
conformance_checked_decision numerator=3 denominator=3
execution_proof numerator=7 denominator=9
rc=0
== tree status change during the gates (diff of `git status --porcelain` before/after) ==
(none)
Wed Sep 23 11:58:32 UTC 2026
```
G1 = the premise's 13 and the landing's "13 passed". G2 = 15 checks (the landing's "15 checks passed", was 14). G3's 21 = 16 (the
lane-runtime file, as in item 8's U0 run) + 5 (the S0-12 file; the landing's "5 passed"). G4: ten PRESENT, S0-02 and S0-05 ABSENT, as at
authoring. The item-6 and item-8 control runs (U0) are a third run of G1 and of the lane-runtime file, in scratch copies, with the same
counts.

## Claims of the two landing messages, row by row (reproduced here)

- 9932f34, F1 mechanism: the old rule wants `PRIVATE KEY-----` and misses GnuPG. Reproduced on REAL throwaway GnuPG blocks (`/tmp/vr182`,
  the real `scrub` at 9932f34^ vs the PIN): `PGP PRIVATE KEY BLOCK (ed25519)` old 8/11 lines left, placeholder x0 | new 0/11, x1;
  `(rsa3072 + headers)` old 32/40, x0 | new 0/40, x1; the same four numbers under the `PGP SECRET KEY BLOCK` label. The message's
  "9 of 15" came from its own FAKE body; the direction and the fix's effect agree.
- "BEGIN and END both match …; the rule stays FIRST …; the comment now says why": `scripts/transcript_export.py:25-31` ✓ (read).
- "the PC exporter gets the same rule" (SCRUB_SRC): ✓ at the path level, with A-5's version caveat (item 5).
- The tests (seven families incl. plain PKCS#8 and both PGP labels with the blank line and checksum; the keyword test; the PC check):
  `tests/test_transcript_export.py:122-145` (`KEY_FAMILIES`), `harness-ports/tests/test_hermes_session_export.py:87-91` (`<private-key-redacted>`) ✓.
- Gates: "13 passed" ✓ (item 11, twice); "15 checks passed" ✓; "pyflakes rc 0 on the three files" ✓
  (`/root/venv-agent-factory/bin/python -m pyflakes scripts/transcript_export.py tests/test_transcript_export.py harness-ports/tests/test_hermes_session_export.py` -> `rc=0`).
- The five mutants: L1-L5 ✓ exactly (item 6).
- 9c991a2: "the same words at all three sites" ✓ (item 8). "The count itself is unchanged … 110/98/4 … 'at or after'": recounted from
  the committed table (`awk` between the fences after the cutoff line): `rows=110 report=98 FAILED=4 before-cutoff=0 exactly-at-cutoff=0` ✓.
  Gates: "16 passed" ✓ (16 of G3's 21), "5 passed" ✓, `vendored_manifest --check` ✓ (`PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9
  vendored roots`, rc 0), validate-ledger ✓, the negative control "2 failed, 14 passed" ✓ (item 8). "truncates prompt.md at every
  start": over-broad (B-4). Tree unchanged across these runs (`git status --porcelain` before/after identical).

## FINDING INVENTORY

No severity filter. Predicate columns: C = contract-mapped (A: C3 and the 9932f34 claims; B: R3 with R3(c) as amended) · P = reproduced
through the real exporter, the real test or the real committed code · M = materially effective (a key or secret byte reaches a written
file, or a stated claim is false as stated) · D = a concrete discriminator · B = in-boundary (A: the key rule and its tests in the three
files of 9932f34; B: the three strings of 9c991a2). A finding blocks only with all five.

| # | class | finding (file:line) | evidence | C | P | M | D | B | reproduction | suggested fix |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | FOLLOW-UP | `X9.42 DH PRIVATE KEY` is never matched: the label has a period, and the class is `[A-Z0-9 ]` (`scripts/transcript_export.py:29-30`). 21 of 26 body lines leak in every shape, through both exporters. OpenSSL 3.0.13 cannot WRITE the label (`unsupported public key type`); it is a libcrypto string, missed by the prior verify's label list | SOLID (relabelled throwaway body) | C3 in general; not the frozen family list | yes | latent: no writer found | yes | yes | `python3 /tmp/vr182/h2.py` row `X9.42 DH PRIVATE KEY` | `[A-Z0-9 .]*` in BEGIN and END plus one test row |
| A-2 | FOLLOW-UP | A mangled label defeats the rule: a doubled space inside `PRIVATE KEY` / `KEY BLOCK` (1-32 lines), lowercase (20/25), 4 dashes, smart dashes, a zero-width char, a tab (20/25 each). 6 dashes still match. OpenSSL/GnuPG reject every one of these labels | SOLID | no: not a parser-valid block | yes | latent (a human-damaged paste) | yes | yes | item 2 `sp:key`/`sp:block`; the mangling probe | `\s+` between label words, a dash-tolerant fence, case-insensitive; with an over-redaction control |
| A-3 | FOLLOW-UP (adjacent) | Secret-bearing formats outside the PEM key labels: `SSL SESSION PARAMETERS` (pem.h:50, master secret; 2/3 lines), SSH.com `---- BEGIN SSH2 ENCRYPTED PRIVATE KEY ----` (17/20; the format, not probed), a URL-encoded PEM (19/25), PuTTY `.ppk` (1/2; not armored, the F3 class) | SOLID (FAKE / throwaway) | none | yes | outside any claim | yes | scrubber, not the key rule's claim | item 2 rows + `/tmp/vr182/adj2.py` | rules per format, or name the gaps in the docstring (`scripts/transcript_export.py:9-11`, `SECRET_PATTERNS`) |
| A-4 | FOLLOW-UP / UNVERIFIED | PC transcripts harvested under the old rule (the clone at 012d455b until 11:2xZ; the harvest reads the clone at harvest time, `harness-ports/bin/pc-lane.sh:514`) and not yet committed are invisible here. The committed corpus is clean (0 of 120 change; no armor line) | SOLID for the corpus; UNVERIFIED for the PC | none | corpus yes; PC no | unknown | — | no (deployment) | item 3 | re-scrub incoming `transcripts/pc/*.md` with the current `scrub` before the commit (idempotent), or a CI check `scrub(text) == text` over `transcripts/` |
| A-5 | FOLLOW-UP | The PC exporter binds to the rule by PATH, not version (`harness-ports/bin/hermes-session-export.py:23-30`). A stale rule (9932f34^) at `SCRUB_SRC` exports GnuPG armor with 8/11 lines and rc 0 through the verbatim harvest block; an identity `scrub` exports everything. Every BROKEN scrubber fails closed | SOLID | the 9932f34 message's "same rule" holds at the path level | yes (scratch copies + `harness-ports/bin/pc-lane.sh:509-519` verbatim) | yes, in a stale-clone window; no committed byte (A-4) | yes | NO: the fix is in `harness-ports/bin/hermes-session-export.py` and `harness-ports/bin/qwen_matrix.py`, outside 9932f34's three files | `bash /tmp/vr182/h5.sh` rows `stale-rule`, `identity` | a load-time canary: the loaded `scrub` must redact a canary GnuPG block and token, else exit non-zero |
| A-6 | FOLLOW-UP | Mutant N2 (`[A-Z ]*`, no digits) survives both suites: `KEY_FAMILIES` (`tests/test_transcript_export.py:122-123`) holds no digit label; ED25519/ED448/X25519/X448/SM2 blocks would leak 21/26 lines | SOLID | C3 (true in code, untested) | yes | no (current code correct; no writer of digit labels here) | yes | yes | `python3 /tmp/vr182/h6.py` row N2 | add `ED25519 PRIVATE KEY` to `KEY_FAMILIES` |
| A-7 | FOLLOW-UP | Mutant N7 (`PUBLIC` added) survives: no test holds a public block, so a rule that eats `PUBLIC KEY`/`RSA PUBLIC KEY`/`PGP PUBLIC KEY BLOCK` passes. Over-redaction, not a security gap | SOLID | none (C3 says nothing of public blocks) | yes | no | yes | yes | row N7 | one negative control: a public block through the real CLI keeps its text |
| A-8 | INFO | Mutant N4 (`\Z` -> `$`) is EQUIVALENT: without `re.M` the only difference is one trailing newline; no key byte differs | SOLID | — | yes | no | — | — | item 6 N4 probe | none |
| I-1 | INFO | A third consumer of `scrub`: `harness-ports/bin/qwen_matrix.py:126` `_scrub_messages` (the Qwen corpus, PC-side, not committed); it fails closed with a named `MatrixError` (`:135-136`) | SOLID (pack + read) | — | static | no | — | no | `/tmp/vr182/pack.md` | the A-5 canary there too |
| I-2 | INFO | F15 partly closed: `cryptography` 50.0.1 writes a REAL `OPENSSH PRIVATE KEY` (64 columns); `ssh-keygen`'s 70 columns stay unprobed (a FAKE row covers it). Both are redacted whole | SOLID (64) / UNSURE (70) | — | yes | no | — | — | item 2 | read the width from `ssh-keygen` on the PC |
| I-3 | INFO | The opaque rule (`scripts/transcript_export.py:43`, `<opaque-redacted>`) cuts 40+ runs out of public base64 (certificates, public keys): pre-existing, coarse by design, not the key rule | SOLID | — | yes | no | — | — | item 3(a) `r8` column | none |
| I-4 | INFO | After a credential keyword the key placeholder is renamed `<redacted>` by r1 (`:33`); a reader cannot see that a key was there. No byte leaks | SOLID | — | yes | no | — | — | item 4 | none |
| I-5 | INFO | Cost: linear in all nine shapes; the key rule alone is up to 2.6x slower on header runs, invisible in the whole scrub (max 1.35 s / 8 MB) | SOLID (ratios) | — | yes | no | — | — | item 7 | none |
| I-6 | INFO | The ledger names the repairs by their PRE-push ids: `todo/BUILD-TASKLIST.md:233` "AF-AP-127-R1 (#177) LANDED e44c914", "REPIN-a-R2 (#178) LANDED 1f41e13"; origin has 9932f34 and 9c991a2 (trees identical: 42bf52203161, b16cbffce732). The local ids resolve on no other clone | SOLID | — | — | no | — | no | `git branch -r --contains 1f41e13` (none) | cite the post-push ids |
| I-8 | INFO | `harness-ports/tests/test_pc_lane_dispatcher.sh` leaves `/tmp/pc-lane-provider-mix-brief.md--0000000-<pid>.sql` behind on every run: 159 files in this sandbox since 09-22 12:40Z, 4-6 per run. Its local bridge double executes the provider-mix write that `scripts/pc_lane.sh:538` (`MIX_REMOTE`) meant for the PC, and nothing removes it. Outside both boundaries | SOLID (`ls` + the line) | — | yes | disk only | — | no | `ls /tmp/pc-lane-provider-mix-brief.md--0000000-*.sql \| wc -l` -> 159 | remove the file in the double, or give the test its own `TMPDIR` |
| I-7 | INFO | Method: the sandbox runs as uid 0, which reads a mode-000 file; the real "unreadable" case needs a privilege drop (`setpriv --reuid=65534`) | SOLID | — | — | — | — | — | item 5 | none |
| B-1 | INFO | The separator `"; "` joining the three pieces (`tests/test_upstream_lock_lane_runtime.py:50`, `LANE_RUNTIME_VERIFIED`) now occurs INSIDE piece (c) ("(98 with a report; brief.md--0000000 …)"): a naive split gives 4 parts. Nothing splits the value today | SOLID | R3 (pieces in order) | yes | no | — | yes | item 8 | a `,` or `—` inside the parenthesis |
| B-2 | FOLLOW-UP | The record's Result line (`tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md:13`) still reads `110 lanes: 98 with a report` … `the rest live or stopped without a report`, although `brief.md--0000000` never started (F2's point). Not one of the three amended sites | SOLID | R3(c) (the record is its source) | yes | low: the number is right, one row's gloss is wrong | the row + P:163-171 | no (outside 9c991a2's three strings) | item 8 | "110 lane directories … the rest live, stopped, or never started (`brief.md--0000000`)" |
| B-3 | INFO | The record's script names its variable `first` (record lines 142-143) under a Rule that now says LATEST. The script is a verbatim record, so it keeps the name | SOLID | — | — | no | — | — | item 8 | a one-line note beside the script |
| B-4 | FOLLOW-UP | The Rule line's "which `harness-ports/bin/pc-lane.sh:218` (`: > "$PROMPT_FILE"`) truncates at every start" (record lines 8-9), and 9c991a2's message: starts refused at P:65-185 never reach :218. The count and piece (c) stand; the error runs toward conservatism | SOLID (code) | the record's method text, not the `verified:` value | yes | no effect on the count or on piece (c) | the P line list, item 9 | yes (one of the three strings) | item 9 | "at every start that passes its guards (P:65-185)" |
| B-5 | FOLLOW-UP | The record never states that 5 of the 98 reports (rows 22-26) are mixed-runtime products (first launched 11:40Z-14:12Z on 3.49.1, `docs/INCIDENT-LOG.md:286`, `hermes update`). Piece (c) is still true: graded NOT a hollow green (item 10) | SOLID | R3 ("says what it proves": met) | yes | low (5 of 98, no provenance claim) | the rows + the log line | no (a record edit) | item 10 | one line in the record's "Limits, stated" |
| B-6 | FOLLOW-UP / UNVERIFIED | The implicature that the other 109 directories ran Hermes: a start that dies between P:218 and P:446 counts with no Hermes run, possible only among the 11 other no-report rows; the record does not print which file dated each row | SOLID (code) / UNVERIFIED (PC) | none | code yes | unknown | — | no | item 9 | a dating-file column in the measuring script |

**KNOWN, seen again, not re-derived** (issue #41 for A, #42 for B): F2 (the nested block's tail, item 2 `2B nest`: a BEGIN-less fragment);
F13 (`END=pub` loses the text after the block; the widening adds the GnuPG and `SECRET KEY` labels to the prose-loss surface); F3 (the
`.ppk` row); F4/F5 (unscrubbed headers; the `usage.json` append at `harness-ports/bin/pc-lane.sh:516`, the only other writer into
`transcripts/`); F8c (the PC key check calls `_body`, not `export()`; item 2 covered `export()` through the CLI); F15 (see I-2).
VERIFY-REPIN-a-R1 F3 (drafts among the 98), F7 (the recorded script prints no counts), F12, F18 and F20 still stand as their report
states them.

**Verified TRUE, no finding:** C3 for every frozen family in every well-formed shape, through both exporters, message and tool bodies
(154 cells, 0 lines); the first position against 13 new prefixes (39 cases, 0 lines); fail-closed on every broken scrubber; 0 of 120
committed transcripts change; linear cost; L1-L5 exactly as claimed; for B, the three sites carry one meaning (lock == constant byte for
byte), the words are true for the method by code, `brief.md--0000000 never ran Hermes` is true by code, the recount is 110/98/4, and
every mutant of the words reds both value tests at the changed character.

## GATE RECOMMENDATIONS (one per component; the coordinator owns the gate)

- **(A) the key-armor class (AF-AP-127-R1, 9932f34) — `MERGE-READY-WITH-FOLLOWUPS`.** No finding meets all five conditions. C3 and
  every claim of 9932f34 reproduce through the real exporters: 0 body lines across 154 frozen-family cells; red-green on real
  throwaway GnuPG keys (old rule 8/11 and 32/40 lines, new 0); L1-L5 killed exactly as claimed; 7 of 10 new mutants killed; the first
  position holds against 13 new prefixes; every broken scrubber fails closed; 0 of 120 committed transcripts change; linear cost.
  Follow-ups: A-6 and A-7 (one test row and one negative control, in the repair's own files); A-1 and A-2 (class widenings of the
  rule, on labels no parser writes or accepts); A-3 (adjacent formats); A-4 and A-5 (deployment and binding, outside the three files).
- **(B) the R3(c) words (REPIN-a-R2, 9c991a2) — `MERGE-READY-WITH-FOLLOWUPS`.** No finding meets all five conditions. The lock's
  piece (c) equals the test constant byte for byte, and the Rule line carries the same meaning. The words are true for the method by
  the committed code (`prompt.md` = the latest start that passed its guards; a refused start launched nothing and moves nothing).
  `brief.md--0000000 never ran Hermes` is true by code. The recount is 110/98/4. The landing's negative control reproduces, and every
  new mutant reds both value tests by name. Dropping the five-lane clause does not flatter b3399c1 (item 10). Follow-ups: B-2, B-4,
  B-5, B-6.

These recommendations do NOT depend on anything left unreproduced: the PC-side facts (the `.lanes/` directories, the clone's HEAD,
uncommitted PC transcripts) were not re-measured (no bridge), and neither recommendation rests on them. A stands on the code, the real
exporters and the committed corpus; B stands on the committed code, the committed record and the tests.

## What was reproduced, what was reviewed statically, what was skipped

- REPRODUCED (this session, scratch under `/tmp/vr182/`): item 1's premise; items 2, 3, 4, 5, 6, 7 and 8 in full through the real
  exporters, the real `scrub`, the real tests and the verbatim harvest block; the red-green on real throwaway keys; the landing
  claims listed above; all item-11 gates, twice.
- STATIC (primary source read, not executed): the guard and write order in `harness-ports/bin/pc-lane.sh` and `scripts/pc_lane.sh`
  (item 9); the dispatcher-test history for the `0000000` origin; the incident-log and ledger records of the five relaunches; the
  `qwen_matrix.py` consumer.
- SKIPPED, with the reason: the PC (no bridge, by the brief); the other lanes' files (the brief's BOUNDARY); `/bug-echo` sweeps and any
  fix (a verifier reports); the full repo suite and a thermo-nuclear pass (outside this targeted verify); re-deriving the KNOWN rows.

## Report lint (three rounds of its `fix:` hints, then pasted)

```
$ python3 scripts/report_lint.py --min-refs 15 tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md --root .
report_lint: 56 refs — OK 52, NEAR 2, MISS 1, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
```
(The final run, after the 12:06Z addenda added two cited lines, both OK; the three fix rounds ended at 54 refs, OK 50.) Round 0 read OK 27, MISS 15, UNCHECKABLE 10. Round 1 added one backticked token per cited line and corrected one real error: the
constant's `"; ".join` is on line 50 of the test file, not 52, in two places. That brought it to OK 50, MISS 1. Rounds 2 and 3 tried two
more spellings for the last MISS. That MISS is item 3(a)'s citation of the opaque rule. The lint's own "cited line reads" shows the
cited line is that rule (`"<opaque-redacted>"`), so the citation is right: the lint's tokenizer takes the text BETWEEN the backtick
pairs on that line. The UNCHECKABLE is a verbatim paste in item 8, and it stays verbatim. The two NEAR are within one line.

## DISCREPANCIES

1. The brief's item 10 cites "record rows 21-25" for the five relaunched lanes. At the PIN they are rows 22-26, because 9c991a2 added
   one line to the record (148 -> 149 lines). The brief's premise paste labelled `sed -n 19,25p` shows the rows that sit at lines 21-27
   at the PIN. The content is identical.
2. The incident-log entry for 2026-09-08 14:2xZ is `docs/INCIDENT-LOG.md:286` at the PIN; VERIFY-REPIN-a-R1 cited it as :277-278 (the log
   has grown since).
3. The ledger names the two repairs by pre-push ids (`todo/BUILD-TASKLIST.md:233`: `LANDED e44c914`, `LANDED 1f41e13`); origin carries 9932f34 and
   9c991a2 with identical trees (I-6).
4. 9932f34's message says 9 of 15 body lines survived the old rule with its FAKE body; the real throwaway GnuPG blocks here leave 8/11 and
   32/40. Different bodies, same direction, same fix effect.
5. 9c991a2's message and the amended Rule line say `pc-lane.sh:218` truncates `prompt.md` "at every start"; a start refused at
   P:65-185 never reaches it (B-4).
6. The prior verify's libcrypto label list (`ANY|DSA|EC|ED25519|ED448|ENCRYPTED|RSA|SM2|X25519|X448 PRIVATE KEY`) omitted
   `X9.42 DH PRIVATE KEY`, which the same binary carries (A-1).
7. At the PIN no committed transcript had been written after 9932f34 (item 1), so the PIN corpus check tests the NEW rule against files
   the OLD rule wrote. During the lane, origin gained 11195d9, the first push-time export under the new rule. It was checked too:
   0 changes, 0 armor lines, 0 placeholders (item 3, the 12:06Z addendum).
8. The heads moved during the lane: local HEAD e4ce195 -> f6dde3f, origin c84f161 -> 11195d9 (at 12:06Z). No commit in either range
   touches a boundary file (`git log c84f161..origin/… -- <the eight files>` and `c84f161..HEAD` are both empty), and the working tree
   still equals c84f161 on all eight. My only repository write is this report.

## NOT-done

- No PC or bridge use (the brief). Not measured: the PC clone's HEAD; the `.lanes/` directories (which file dated each row; whether
  `brief.md--0000000` holds a `prompt.md`; its real origin); PC transcripts harvested under the old rule and not yet committed (A-4).
- `ssh-keygen` is absent: the 70-column OpenSSH width and the SSH.com label come from the format (FAKE rows). The real OpenSSH writer
  used here is `cryptography` 50.0.1 (64 columns). No encrypted OpenSSH key: `cryptography` needs `bcrypt`, which is absent.
- Not tested: binary or non-UTF-8 DB content; any `messages.role` beyond the test schema's. The live coordinator transcript was not
  read. The 11:40Z push-time export (11195d9) shows no F13 loss; later exports are not measured.
- No `/bug-echo` sweep, no fix of any finding, no full repo suite, no thermo-nuclear pass.
- Item 7 ran on a contended box (load 1.9-3.5 on 4 CPUs): the ratios carry the verdict; the absolute times are indicative.
- Scratch `/tmp/vr182/` (throwaway keys, the temporary `GNUPGHOME`, scratch trees, mutants, basetemps) is removed at the end of the lane;
  the removal is recorded in the final message, not here.
