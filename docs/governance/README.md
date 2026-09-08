# Governance — the owner-verifiable ACCEPTED anchor

Owner decision 2026-09-08 (task #30, option a; `docs/08_DECISION_LOG.md`): a proof the owner ACCEPTS is anchored by a
**GPG-signed annotated git tag** `accepted/<proof-id>` that only the owner can make. `scripts/check-proof-status.py`
(run by the test suite on the committed tree, and by the coordinator before every push that touches a status line)
verifies, for every `PROOF-STATUS: <id> = ACCEPTED` line in `todo/BUILD-TASKLIST.md`:

1. the tag `accepted/<id>` exists and is an annotated, signed tag (never a lightweight one);
2. its signature verifies against the owner's public key committed at `docs/governance/owner-signing-key.asc` — in an
   isolated keyring built from that one file at check time, never the host's keyring;
3. the tag's commit is in this branch's history;
4. that commit holds `proofs/<id>/result.json` **byte-identical** to the current one. An attested-input regeneration
   (AF-AP-56) makes a NEW artifact; a new artifact must be re-accepted with a new signed tag.

Until the owner signs, the ledger carries a VISIBLE declaration beside the status line —
`PROOF-ANCHOR: <id> = PENDING-OWNER-TAG (…)` — which the checker reports as a WARNING and never counts as verified. A tag
and a pending declaration together are a stale ledger and an error. The coordinator can write the declaration; it cannot
write the signature. `--no-anchors` skips the anchor check EXPLICITLY (the status-logic test fixtures use it; CI and the
coordinator never do).

## The owner's procedure (once per accepted proof; run on the PC in `~/agent-factory`, on the designated branch)

First time only — a signing key and its committed public half (skip the first line if `gpg --list-secret-keys` already
shows a key you want to use, and put its fingerprint in `FPR`):

```bash
gpg --quick-generate-key "Rocco <pixelcommerce588@gmail.com>" ed25519 sign 0
FPR=$(gpg --batch --with-colons --list-secret-keys | awk -F: '/^fpr:/{print $10; exit}')
git config --global user.signingkey "$FPR"
gpg --armor --export "$FPR" > docs/governance/owner-signing-key.asc
git add docs/governance/owner-signing-key.asc
git commit -m "governance: the owner's public signing key for accepted/<proof> tags"
git push origin HEAD
```

Per accepted proof — sign the tag on the commit that holds the result you accept (normally the branch head after the
coordinator's ledger push), push the tag, then tell the coordinator so the PENDING declaration is removed. Sign a commit that is
ALREADY on origin whenever you can (`git merge --ff-only origin/<branch>` first, then tag `HEAD`); if you tag a local commit of your
own, the coordinator's push preserves its object id (push_clean rewrites only commits that carry a model-identifier trailer —
AF-AP-69), so the tag stays valid:

```bash
git fetch origin && git merge --ff-only origin/claude/soundbox-kit-migration-iz1jwf
git -c gpg.format=openpgp tag -s accepted/S0-11 -m "ACCEPTED: S0-11 evaluation hardening — owner process decision 2026-09-04, on the current minted result" HEAD
git push origin accepted/S0-11
python3 scripts/check-proof-status.py .   # expect rc 0 and no WARNING once the declaration is removed
```

`gpg.format=openpgp` is forced because a git configured for SSH signing (common on machines that sign GitHub commits with
an SSH key) would otherwise refuse to make or verify an OpenPGP signature. The checker forces the same at verify time.

## When the PC cannot push (seen 2026-09-08)

The PC clone's stored GitHub credential was refused (`remote: Permission to … denied`, HTTP 403) on both `git push origin HEAD` and
the tag push, after the key commit and the signed tag had been made locally. The coordinator then brought both over the bridge as a
git bundle (`git bundle create … origin/<branch>..HEAD refs/tags/accepted/<id>` → base64 → the sandbox → `git fetch <bundle>`),
fast-forwarded the branch, re-ran the anchor check in the sandbox's isolated keyring, and pushed the branch through `push_clean.sh`
and the tag with `git push origin accepted/<id>`. The signature travels intact — a tag object is verified wherever it lands. Fixing the
PC credential is the owner's; until then this bundle path is the procedure.

The sandbox's git proxy refuses tag pushes (HTTP 403 — it permits the designated branch only), and CI clones without tags. So the
signed tag OBJECT is also committed as a file, `docs/governance/tags/accepted-<id>.tag` (`git cat-file tag accepted/<id>` bytes).
It is content-addressed: `git hash-object -w -t tag` on the file reproduces the exact object the owner signed, and the checker
imports and verifies it whenever the ref is absent (a clone without tags, CI with `fetch-depth: 0`). When both exist they must be
the same object. Anyone can restore the ref: `git update-ref refs/tags/accepted/<id> $(git hash-object -w -t tag docs/governance/tags/accepted-<id>.tag)`.
